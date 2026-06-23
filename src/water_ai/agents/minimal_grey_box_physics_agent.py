from __future__ import annotations

from collections.abc import Sequence
import math

from water_ai.agents.base import BaseAgent
from water_ai.domain import AgentReport, QualityIssue, SensorReading, Severity
from water_ai.process_dynamics import generate_sensor_stream_from_process_state, initial_process_state


DEFAULT_SCENARIOS = [
    "clean_release",
    "oxidant_limitation",
    "reaction_time_insufficient",
    "catalyst_deactivation",
    "matrix_shock",
]


class MinimalGreyBoxPhysicsAgent(BaseAgent):
    """Audit a minimal grey-box physical prior before heavier process modeling."""

    name = "minimal_grey_box_physics_agent"

    def __init__(
        self,
        *,
        scenario_ids: list[str] | None = None,
        evidence_stage: str = "synthetic_physics_prior",
        field_calibration: dict[str, float] | None = None,
        base_rate_per_min: float = 0.045,
        nominal_retention_min: float = 36.0,
        matrix_inhibition_coeff: float = 1.35,
        catalyst_decay_coeff: float = 0.045,
        max_mean_residual: float = 0.18,
        max_mass_balance_residual: float = 0.16,
        max_byproduct_risk: float = 0.72,
        control_guardrail_backpropagation_metrics: dict[str, object] | None = None,
    ) -> None:
        self.scenario_ids = scenario_ids or DEFAULT_SCENARIOS
        self.evidence_stage = evidence_stage
        self.field_calibration = field_calibration or {}
        self.base_rate_per_min = base_rate_per_min
        self.nominal_retention_min = nominal_retention_min
        self.matrix_inhibition_coeff = matrix_inhibition_coeff
        self.catalyst_decay_coeff = catalyst_decay_coeff
        self.max_mean_residual = max_mean_residual
        self.max_mass_balance_residual = max_mass_balance_residual
        self.max_byproduct_risk = max_byproduct_risk
        self.control_guardrail_backpropagation_metrics = control_guardrail_backpropagation_metrics or {}

    def run(self, readings: Sequence[SensorReading]) -> AgentReport:
        del readings
        method_contract = self._method_contract()
        scenario_table = [self._evaluate_scenario(scenario_id) for scenario_id in self.scenario_ids]
        guardrail_patch = self._guardrail_failure_boundary_patch()
        readiness = self._readiness(scenario_table, guardrail_patch)
        issues = self._issues(scenario_table, readiness)
        recommendations = self._recommendations(scenario_table, readiness)
        summary = (
            f"最小灰箱物理审计：{readiness['grey_box_physics_status']}；"
            f"mean_residual={readiness['mean_grey_box_residual']:.3f}，"
            f"max_mass_balance_residual={readiness['max_mass_balance_residual']:.3f}。"
        )
        confidence = round(
            min(0.91, max(0.24, 0.42 + 0.40 * readiness["grey_box_physics_score"] - 0.035 * len(issues))),
            3,
        )
        return AgentReport(
            agent_name=self.name,
            confidence=confidence,
            summary=summary,
            issues=issues,
            recommendations=recommendations,
            metrics={
                "method_contract": method_contract,
                "scenario_physics_table": scenario_table,
                "guardrail_failure_boundary_patch": guardrail_patch,
                "control_guardrail_backpropagation_context": self._control_guardrail_backpropagation_context(guardrail_patch),
                "readiness": readiness,
                "calibration_contract": self._calibration_contract(),
                "agent50_writeback": self._agent50_writeback(readiness),
            },
        )

    def _evaluate_scenario(self, scenario_id: str) -> dict[str, object]:
        state = initial_process_state(scenario_id)
        synthetic_readings = generate_sensor_stream_from_process_state(state, n=int(self.nominal_retention_min), seed=17)
        observed_residual = float(synthetic_readings[-1].ground_truth_state["pollutant_residual_risk"])
        hydraulic_factor = self._clip(0.55 + 0.45 * state.hydraulic_efficiency, 0.25, 1.05)
        effective_retention = self.nominal_retention_min * hydraulic_factor
        rtd_short_circuit_risk = self._clip(1.0 - state.hydraulic_efficiency + 0.25 * max(0.0, state.matrix_interference - 0.55))
        matrix_inhibition = 1.0 / (1.0 + self.matrix_inhibition_coeff * state.matrix_interference)
        catalyst_term = self._clip(state.catalyst_activity * (0.55 + 0.45 * state.catalyst_lifetime_fraction), 0.05, 1.0)
        oxidant_term = self._clip(0.35 + 0.65 * state.oxidant_level, 0.05, 1.0)
        hydraulic_term = self._clip(0.30 + 0.70 * state.hydraulic_efficiency, 0.05, 1.0)
        k_effective = self.base_rate_per_min * catalyst_term * oxidant_term * hydraulic_term * matrix_inhibition
        predicted_removal = self._clip(1.0 - math.exp(-k_effective * effective_retention), 0.0, 0.96)
        bypass_fraction = self._clip(0.05 + 0.28 * rtd_short_circuit_risk + 0.12 * state.matrix_interference, 0.02, 0.42)
        converted_load = state.pollutant_load * (1.0 - bypass_fraction) * predicted_removal
        predicted_outlet_load = self._clip(
            state.pollutant_load * (bypass_fraction + (1.0 - bypass_fraction) * (1.0 - predicted_removal))
        )
        oxidant_consumption = converted_load * (0.32 + 0.18 * state.matrix_interference)
        oxidant_balance_residual = max(0.0, oxidant_consumption - state.oxidant_level)
        catalyst_decay_delta = self._clip(
            self.catalyst_decay_coeff
            * (0.35 + state.matrix_interference)
            * (0.55 + predicted_removal)
            * (1.10 if state.catalyst_regen_count else 1.0),
            0.004,
            0.12,
        )
        byproduct_risk = self._clip(
            0.18
            + 0.28 * state.matrix_interference
            + 0.18 * state.oxidant_level
            + 0.20 * max(0.0, predicted_removal - 0.55)
            + 0.12 * rtd_short_circuit_risk
        )
        mass_balance_residual = abs(state.pollutant_load - predicted_outlet_load - converted_load) / max(
            0.10, state.pollutant_load
        )
        grey_box_residual = abs(predicted_outlet_load - observed_residual)
        residual_sign = "under_predicts_residual" if predicted_outlet_load < observed_residual else "over_predicts_residual"
        failure_modes = self._failure_modes(
            grey_box_residual=grey_box_residual,
            mass_balance_residual=mass_balance_residual,
            byproduct_risk=byproduct_risk,
            rtd_short_circuit_risk=rtd_short_circuit_risk,
            catalyst_decay_delta=catalyst_decay_delta,
            catalyst_effective_activity=catalyst_term,
            matrix_inhibition=matrix_inhibition,
        )
        return {
            "scenario": scenario_id,
            "inlet_pollutant_load": round(state.pollutant_load, 3),
            "observed_synthetic_residual": round(observed_residual, 3),
            "effective_retention_min": round(effective_retention, 3),
            "rtd_short_circuit_risk": round(rtd_short_circuit_risk, 3),
            "pseudo_first_order_k_per_min": round(k_effective, 5),
            "matrix_inhibition_factor": round(matrix_inhibition, 3),
            "catalyst_effective_activity": round(catalyst_term, 3),
            "bypass_load_fraction": round(bypass_fraction, 3),
            "converted_load_proxy": round(converted_load, 3),
            "predicted_removal_fraction": round(predicted_removal, 3),
            "predicted_outlet_load": round(predicted_outlet_load, 3),
            "grey_box_residual": round(grey_box_residual, 3),
            "residual_sign": residual_sign,
            "mass_balance_residual": round(mass_balance_residual, 3),
            "oxidant_consumption_proxy": round(oxidant_consumption, 3),
            "oxidant_balance_residual": round(oxidant_balance_residual, 3),
            "catalyst_decay_delta": round(catalyst_decay_delta, 3),
            "byproduct_risk": round(byproduct_risk, 3),
            "failure_modes": failure_modes,
            "data_needs": [
                "inlet_target_pollutant",
                "outlet_target_pollutant",
                "hydraulic_residence_time_distribution",
                "oxidant_dose_and_residual",
                "catalyst_age_regen_history",
                "byproduct_lab_panel",
            ],
            "failure_boundary": "参数未由文献范围或 field calibration 校准前，只能作为 synthetic grey-box prior。",
        }

    def _readiness(
        self,
        scenario_table: list[dict[str, object]],
        guardrail_patch: list[dict[str, object]],
    ) -> dict[str, object]:
        count = max(1, len(scenario_table))
        residuals = [float(row["grey_box_residual"]) for row in scenario_table]
        mass_residuals = [float(row["mass_balance_residual"]) for row in scenario_table]
        byproduct_risks = [float(row["byproduct_risk"]) for row in scenario_table]
        violation_rows = [
            row
            for row in scenario_table
            if float(row["grey_box_residual"]) > self.max_mean_residual
            or float(row["mass_balance_residual"]) > self.max_mass_balance_residual
            or float(row["byproduct_risk"]) > self.max_byproduct_risk
            or bool(row["failure_modes"])
        ]
        mean_residual = sum(residuals) / count
        max_mass_balance = max(mass_residuals) if mass_residuals else 0.0
        max_byproduct = max(byproduct_risks) if byproduct_risks else 0.0
        field_ready = (
            self.evidence_stage == "field_physics_calibration"
            and float(self.field_calibration.get("field_physics_coverage", 0.0)) >= 0.85
            and float(self.field_calibration.get("max_field_residual", 1.0)) <= self.max_mean_residual
            and float(self.field_calibration.get("max_mass_balance_residual", 1.0)) <= self.max_mass_balance_residual
        )
        guardrail_patch_count = len(guardrail_patch)
        guardrail_consumed_count = sum(1 for row in guardrail_patch if row.get("target_agent") == self.name)
        guardrail_consumption_rate = round(guardrail_consumed_count / max(1, guardrail_patch_count), 3)
        score = round(
            0.34 * max(0.0, 1.0 - mean_residual / max(0.01, self.max_mean_residual))
            + 0.22 * max(0.0, 1.0 - max_mass_balance / max(0.01, self.max_mass_balance_residual))
            + 0.16 * max(0.0, 1.0 - max_byproduct / 1.0)
            + 0.12 * (1.0 - len(violation_rows) / count)
            + 0.10 * float(field_ready)
            + 0.06 * min(1.0, float(self.field_calibration.get("field_physics_coverage", 0.0))),
            3,
        )
        if field_ready and not violation_rows:
            status = "field_grey_box_physics_candidate_ready"
        elif mean_residual <= self.max_mean_residual and max_mass_balance <= self.max_mass_balance_residual:
            status = "synthetic_grey_box_physics_prior_ready_needs_field_calibration"
        else:
            status = "synthetic_grey_box_physics_prior_exposes_model_gap"
        return {
            "grey_box_physics_status": status,
            "grey_box_physics_score": score,
            "scenario_count": len(scenario_table),
            "mean_grey_box_residual": round(mean_residual, 3),
            "max_grey_box_residual": round(max(residuals) if residuals else 0.0, 3),
            "max_mass_balance_residual": round(max_mass_balance, 3),
            "max_byproduct_risk": round(max_byproduct, 3),
            "physics_violation_rate": round(len(violation_rows) / count, 3),
            "violation_scenarios": [str(row["scenario"]) for row in violation_rows],
            "guardrail_failure_boundary_count": sum(len(self._list(row.get("grey_box_boundary"))) for row in guardrail_patch),
            "guardrail_patch_consumed_count": guardrail_consumed_count,
            "guardrail_patch_count": guardrail_patch_count,
            "agent53_guardrail_boundary_consumption_rate": guardrail_consumption_rate,
            "synthetic_prior_ready": status.startswith("synthetic_"),
            "field_ready": field_ready,
            "can_update_soft_sensor_physics_prior": True,
            "can_update_guardrail_failure_boundaries": guardrail_consumption_rate >= 1.0 and guardrail_patch_count > 0,
            "can_update_agent50_priority": True,
            "can_write_to_actuator": field_ready and not violation_rows,
            "can_write_to_release_gate": False,
            "next_recommended_core_action": "P5_soft_sensor_node_modality_missingness",
        }

    def _issues(self, scenario_table: list[dict[str, object]], readiness: dict[str, object]) -> list[QualityIssue]:
        issues: list[QualityIssue] = []
        if not readiness["field_ready"]:
            issues.append(
                QualityIssue(
                    sensor="minimal_grey_box_physics",
                    issue_type="field_physics_calibration_required",
                    severity=Severity.WARNING,
                    message="当前灰箱物理层仍是 synthetic prior，需要 field RTD、进出水目标污染物、氧化剂余量和副产物标签校准。",
                    evidence=readiness,
                )
            )
        if readiness.get("can_update_guardrail_failure_boundaries", False):
            issues.append(
                QualityIssue(
                    sensor="minimal_grey_box_physics",
                    issue_type="guardrail_failure_boundaries_still_synthetic",
                    severity=Severity.INFO,
                    message="R4 guardrail 失败案例已反写为灰箱边界候选，但仍需 field replay 和物理校准才能成为现场机理结论。",
                    evidence={
                        "agent53_guardrail_boundary_consumption_rate": readiness.get(
                            "agent53_guardrail_boundary_consumption_rate"
                        ),
                        "guardrail_failure_boundary_count": readiness.get("guardrail_failure_boundary_count"),
                    },
                )
            )
        for row in scenario_table:
            if float(row["grey_box_residual"]) > self.max_mean_residual:
                issues.append(
                    QualityIssue(
                        sensor=str(row["scenario"]),
                        issue_type="grey_box_residual_high",
                        severity=Severity.WARNING,
                        message="拟一级灰箱预测与 synthetic 观测残差偏高，需要场景化校准或更换机理假设。",
                        evidence=row,
                    )
                )
            if float(row["mass_balance_residual"]) > self.max_mass_balance_residual:
                issues.append(
                    QualityIssue(
                        sensor=str(row["scenario"]),
                        issue_type="mass_balance_residual_high",
                        severity=Severity.WARNING,
                        message="质量守恒残差偏高，说明旁路/短流/副产物或未建模汇需要显式进入过程模型。",
                        evidence=row,
                    )
                )
            if "byproduct_risk_high" in row["failure_modes"]:
                issues.append(
                    QualityIssue(
                        sensor=str(row["scenario"]),
                        issue_type="byproduct_risk_requires_lab_panel",
                        severity=Severity.WARNING,
                        message="副产物风险偏高，不能只靠残留污染物代理判断放行。",
                        evidence=row,
                    )
                )
        return issues

    def _recommendations(self, scenario_table: list[dict[str, object]], readiness: dict[str, object]) -> list[str]:
        worst = max(scenario_table, key=lambda row: float(row["grey_box_residual"])) if scenario_table else {}
        recs = [
            "将停留时间分布、拟一级反应、基质抑制、催化剂衰减、副产物风险和质量/氧化剂残差写入软传感与控制的灰箱先验。",
            "把 field 数据采集从单纯传感流扩展为进出水目标污染物、RTD/池容、氧化剂投加和余量、催化剂再生历史、副产物 lab panel。",
            "Agent53 输出只能作为模型结构先验和残差审计，不能单独授权执行器或 release gate。",
        ]
        if worst:
            recs.append(
                f"优先校准 `{worst['scenario']}`：grey_box_residual={worst['grey_box_residual']}，failure_modes={worst['failure_modes']}。"
            )
        if readiness["field_ready"]:
            recs.append("field 物理校准通过后，可把该层作为软传感 physics prior 和 Agent49 reward residual 项。")
        if readiness.get("can_update_guardrail_failure_boundaries", False):
            recs.append(
                "R4b 已把控制 guardrail resolved cases 接入 Agent53：后续应把 catalyst proxy uncertainty 和 hydraulic latency/storage uncertainty 作为灰箱失败边界持续审计。"
            )
        return recs

    @staticmethod
    def _method_contract() -> dict[str, object]:
        return {
            "upgrade_id": "P4_minimal_grey_box_physics",
            "borrowed_from": [
                "WaterTAP-style unit model contracts and constraints",
                "QSDsan-style process/system simulation boundary",
                "Pseudo-first-order and Langmuir-Hinshelwood-inspired degradation kinetics",
                "Residence-time distribution and hydraulic retention concepts",
            ],
            "reality_mapping": "用最小参数层表达停留时间、反应速率、基质抑制、催化剂衰减、副产物风险和守恒残差。",
            "data_needs": [
                "inlet/outlet target pollutant labels",
                "hydraulic residence time distribution",
                "oxidant dose and residual measurements",
                "catalyst age/regeneration history",
                "byproduct lab panel",
                "batch-level flow and volume",
            ],
            "implementation_path": [
                "src/water_ai/agents/minimal_grey_box_physics_agent.py",
                "experiments/run_agent53_minimal_grey_box_physics.py",
                "deliverables/minimal_grey_box_physics.md",
                "outputs/minimal_grey_box_physics/grey_box_physics_metrics.json",
            ],
            "evaluation_metrics": [
                "grey_box_residual",
                "mass_balance_residual",
                "bypass_load_fraction",
                "oxidant_balance_residual",
                "byproduct_risk",
                "catalyst_decay_delta",
                "rtd_short_circuit_risk",
            ],
            "failure_boundary": "未经过 field calibration 前，只能作为 synthetic grey-box prior；不能证明现场机理或授权放行。",
        }

    @staticmethod
    def _calibration_contract() -> dict[str, object]:
        return {
            "minimum_field_tables": [
                "batch_inlet_outlet_lab",
                "hydraulic_rtd_or_tracer",
                "oxidant_dose_residual_log",
                "catalyst_age_regeneration_log",
                "byproduct_panel",
            ],
            "field_acceptance_gates": [
                "field_physics_coverage >= 0.85",
                "max_field_residual <= configured threshold",
                "max_mass_balance_residual <= configured threshold",
                "byproduct panel available for high oxidant/matrix scenarios",
            ],
        }

    @staticmethod
    def _agent50_writeback(readiness: dict[str, object]) -> dict[str, object]:
        return {
            "allowed_writeback": [
                "soft_sensor_physics_prior",
                "agent49_reward_residual_candidate",
                "guardrail_failure_boundary_candidate",
                "P4_completion_status_for_governance",
            ],
            "blocked_writeback": [
                "actuator_policy",
                "release_gate_policy",
                "field_mechanism_claim",
            ],
            "can_advance_governance_priority": bool(readiness["synthetic_prior_ready"]),
            "guardrail_boundary_consumption_rate": readiness.get("agent53_guardrail_boundary_consumption_rate", 0.0),
            "policy_effect": (
                "move_to_P5_soft_sensor_node_modality_missingness"
                if readiness["synthetic_prior_ready"]
                else "keep_P4_until_residuals_are_debugged"
            ),
        }

    def _guardrail_failure_boundary_patch(self) -> list[dict[str, object]]:
        patch = self.control_guardrail_backpropagation_metrics.get("grey_box_patch", [])
        if not isinstance(patch, list):
            return []
        return [
            {
                **item,
                "consumed_by_agent53": item.get("target_agent") == self.name,
                "patch_source": "R4_control_guardrail_failure_backpropagation",
                "field_boundary": item.get(
                    "field_boundary",
                    "synthetic guardrail backpropagation; field calibration required.",
                ),
            }
            for item in patch
            if isinstance(item, dict)
        ]

    def _control_guardrail_backpropagation_context(self, guardrail_patch: list[dict[str, object]]) -> dict[str, object]:
        readiness = self.control_guardrail_backpropagation_metrics.get("readiness", {})
        readiness = readiness if isinstance(readiness, dict) else {}
        coverage = self.control_guardrail_backpropagation_metrics.get("coverage_metrics", {})
        coverage = coverage if isinstance(coverage, dict) else {}
        consumed = sum(1 for item in guardrail_patch if item.get("consumed_by_agent53"))
        return {
            "guardrail_backpropagation_status": readiness.get("guardrail_backpropagation_status", "not_available"),
            "backpropagation_ready": bool(readiness.get("backpropagation_ready", False)),
            "resolved_case_count": int(coverage.get("resolved_case_count", 0)),
            "guardrail_patch_count": len(guardrail_patch),
            "agent53_guardrail_boundary_consumption_rate": round(consumed / max(1, len(guardrail_patch)), 3),
            "field_ready": bool(readiness.get("field_ready", False)),
            "can_write_to_actuator": False,
            "can_write_to_release_gate": False,
            "field_boundary": "R4b consumes synthetic guardrail boundaries as grey-box candidates only.",
        }

    def _failure_modes(
        self,
        *,
        grey_box_residual: float,
        mass_balance_residual: float,
        byproduct_risk: float,
        rtd_short_circuit_risk: float,
        catalyst_decay_delta: float,
        catalyst_effective_activity: float,
        matrix_inhibition: float,
    ) -> list[str]:
        modes: list[str] = []
        if grey_box_residual > self.max_mean_residual:
            modes.append("grey_box_residual_high")
        if mass_balance_residual > self.max_mass_balance_residual:
            modes.append("mass_balance_residual_high")
        if byproduct_risk > self.max_byproduct_risk:
            modes.append("byproduct_risk_high")
        if rtd_short_circuit_risk > 0.48:
            modes.append("rtd_short_circuit_risk_high")
        if catalyst_decay_delta > 0.055 or catalyst_effective_activity < 0.38:
            modes.append("catalyst_decay_risk_high")
        if matrix_inhibition < 0.48:
            modes.append("matrix_inhibition_strong")
        return modes

    @staticmethod
    def _clip(value: float, low: float = 0.0, high: float = 1.0) -> float:
        return max(low, min(high, value))

    @staticmethod
    def _list(value: object) -> list[str]:
        if isinstance(value, list):
            return [str(item) for item in value]
        if isinstance(value, tuple | set):
            return [str(item) for item in value]
        return []

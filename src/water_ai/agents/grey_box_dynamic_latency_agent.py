from __future__ import annotations

from collections.abc import Sequence

from water_ai.agents.base import BaseAgent
from water_ai.domain import AgentReport, QualityIssue, SensorReading, Severity


class GreyBoxDynamicLatencyAgent(BaseAgent):
    """Audit whether the loop structure buys enough time for delayed sensing and control."""

    name = "grey_box_dynamic_latency_agent"

    def __init__(
        self,
        *,
        scenario_profiles: list[dict[str, object]] | None = None,
        evidence_stage: str = "synthetic_replay",
        field_timestamp_coverage: float = 0.0,
        conformal_readiness: dict[str, object] | None = None,
        campaign_context: dict[str, object] | None = None,
    ) -> None:
        self.scenario_profiles = scenario_profiles or self._default_profiles()
        self.evidence_stage = evidence_stage
        self.field_timestamp_coverage = max(0.0, min(1.0, field_timestamp_coverage))
        self.conformal_readiness = conformal_readiness or {}
        self.campaign_context = campaign_context or {}

    def run(self, readings: Sequence[SensorReading]) -> AgentReport:
        del readings
        method_contract = self._method_contract()
        latency_budget = [self._evaluate_profile(profile) for profile in self.scenario_profiles]
        readiness = self._readiness(latency_budget)
        issues = self._issues(latency_budget, readiness)
        recommendations = self._recommendations(latency_budget, readiness)
        summary = (
            f"灰箱动态延迟审计：{readiness['latency_status']}；"
            f"延迟违约率 {readiness['latency_budget_violation_rate']:.3f}，"
            f"最小证据余量 {readiness['minimum_evidence_margin_min']:.1f} min。"
        )
        confidence = round(
            min(0.9, max(0.25, 0.44 + 0.32 * readiness["latency_readiness_score"] - 0.035 * len(issues))),
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
                "latency_budget": latency_budget,
                "readiness": readiness,
                "evidence_stage": self.evidence_stage,
                "field_timestamp_coverage": self.field_timestamp_coverage,
                "conformal_readiness": self.conformal_readiness,
                "campaign_context": self.campaign_context,
            },
        )

    def _evaluate_profile(self, profile: dict[str, object]) -> dict[str, object]:
        sampling_interval = self._number(profile, "sampling_interval_min")
        qc_window = self._number(profile, "qc_window_min")
        soft_sensor_compute = self._number(profile, "soft_sensor_compute_min")
        human_review = self._number(profile, "human_review_min")
        lab_turnaround = self._number(profile, "lab_turnaround_min")
        actuator_delay = self._number(profile, "actuator_delay_min")
        mixing_delay = self._number(profile, "mixing_delay_min")
        hold_buffer = self._number(profile, "hold_buffer_min")
        recycle_retention = self._number(profile, "recycle_retention_min")
        validation_overlap_credit = self._number(profile, "validation_overlap_credit_min")
        action_deadline = self._number(profile, "action_deadline_min")

        observation_latency = sampling_interval + qc_window + soft_sensor_compute
        control_action_latency = observation_latency + human_review + actuator_delay + mixing_delay
        release_evidence_latency = max(control_action_latency, observation_latency + lab_turnaround + human_review)
        loop_time_credit = hold_buffer + recycle_retention + validation_overlap_credit
        action_latency_margin = action_deadline - control_action_latency
        evidence_margin = loop_time_credit - release_evidence_latency
        latency_pressure = max(0.0, -min(action_latency_margin, evidence_margin))

        if action_latency_margin < 0:
            latency_status = "control_action_too_slow"
        elif evidence_margin < 0:
            latency_status = "needs_longer_buffer_or_fast_proxy"
        else:
            latency_status = "grey_box_latency_feasible"

        return {
            "scenario": str(profile.get("scenario", "unknown")),
            "risk_mode": str(profile.get("risk_mode", "unknown")),
            "borrowed_from": str(profile.get("borrowed_from", "parsa_2024_dynamic_control_review")),
            "reality_mapping": str(profile.get("reality_mapping", "sampling, validation, actuation, and loop buffer must be timed together")),
            "data_needs": list(profile.get("data_needs", self._default_data_needs())),
            "evaluation_metrics": list(profile.get("evaluation_metrics", self._default_metrics())),
            "failure_boundary": str(profile.get("failure_boundary", self._default_failure_boundary())),
            "sampling_interval_min": round(sampling_interval, 3),
            "qc_window_min": round(qc_window, 3),
            "soft_sensor_compute_min": round(soft_sensor_compute, 3),
            "human_review_min": round(human_review, 3),
            "lab_turnaround_min": round(lab_turnaround, 3),
            "actuator_delay_min": round(actuator_delay, 3),
            "mixing_delay_min": round(mixing_delay, 3),
            "hold_buffer_min": round(hold_buffer, 3),
            "recycle_retention_min": round(recycle_retention, 3),
            "validation_overlap_credit_min": round(validation_overlap_credit, 3),
            "action_deadline_min": round(action_deadline, 3),
            "observation_latency_min": round(observation_latency, 3),
            "control_action_latency_min": round(control_action_latency, 3),
            "release_evidence_latency_min": round(release_evidence_latency, 3),
            "loop_time_credit_min": round(loop_time_credit, 3),
            "action_latency_margin_min": round(action_latency_margin, 3),
            "evidence_margin_min": round(evidence_margin, 3),
            "latency_pressure_min": round(latency_pressure, 3),
            "latency_status": latency_status,
        }

    def _readiness(self, latency_budget: list[dict[str, object]]) -> dict[str, object]:
        count = max(1, len(latency_budget))
        violations = [
            item
            for item in latency_budget
            if item["latency_status"] != "grey_box_latency_feasible"
        ]
        action_violations = [
            item
            for item in latency_budget
            if float(item["action_latency_margin_min"]) < 0.0
        ]
        minimum_evidence_margin = min(float(item["evidence_margin_min"]) for item in latency_budget) if latency_budget else 0.0
        minimum_action_margin = min(float(item["action_latency_margin_min"]) for item in latency_budget) if latency_budget else 0.0
        violation_rate = round(len(violations) / count, 3)
        mean_pressure = round(sum(float(item["latency_pressure_min"]) for item in latency_budget) / count, 3)
        has_field_timestamps = self.evidence_stage == "field_timestamped" and self.field_timestamp_coverage >= 0.85
        conformal_ready = bool(self.conformal_readiness.get("can_write_to_release_gate", False))

        score = round(
            0.34 * (1.0 - violation_rate)
            + 0.16 * max(0.0, min(1.0, (minimum_evidence_margin + 90.0) / 180.0))
            + 0.16 * max(0.0, min(1.0, (minimum_action_margin + 90.0) / 180.0))
            + 0.14 * self.field_timestamp_coverage
            + 0.10 * float(has_field_timestamps)
            + 0.10 * float(conformal_ready),
            3,
        )

        if not has_field_timestamps:
            status = "synthetic_latency_budget_ready_needs_field_timestamps"
        elif action_violations or violation_rate > 0.25:
            status = "field_latency_constraints_need_control_redesign"
        else:
            status = "field_latency_budget_ready"

        return {
            "latency_status": status,
            "latency_readiness_score": score,
            "latency_budget_violation_rate": violation_rate,
            "violation_count": len(violations),
            "action_violation_count": len(action_violations),
            "minimum_evidence_margin_min": round(minimum_evidence_margin, 3),
            "minimum_action_margin_min": round(minimum_action_margin, 3),
            "mean_latency_pressure_min": mean_pressure,
            "field_timestamps_required": not has_field_timestamps,
            "field_replay_ready": has_field_timestamps and not violations and conformal_ready,
            "release_gate_can_use_latency_budget": has_field_timestamps and not violations and conformal_ready,
        }

    def _issues(self, latency_budget: list[dict[str, object]], readiness: dict[str, object]) -> list[QualityIssue]:
        issues: list[QualityIssue] = []
        if readiness["field_timestamps_required"]:
            issues.append(
                QualityIssue(
                    sensor="grey_box_dynamic_latency",
                    issue_type="field_timestamps_required_for_latency_budget",
                    severity=Severity.WARNING,
                    message="当前延迟预算仍基于 synthetic replay 和文献约束，需要现场采样、检测、执行器和回流时间戳验证。",
                    evidence=readiness,
                )
            )
        for item in latency_budget:
            if item["latency_status"] == "control_action_too_slow":
                issues.append(
                    QualityIssue(
                        sensor=str(item["scenario"]),
                        issue_type="control_action_latency_exceeds_deadline",
                        severity=Severity.CRITICAL,
                        message="控制动作在该场景下可能晚于工程可干预窗口，需要更快代理信号、自动执行器或保护性旁路。",
                        evidence=item,
                    )
                )
            elif item["latency_status"] == "needs_longer_buffer_or_fast_proxy":
                issues.append(
                    QualityIssue(
                        sensor=str(item["scenario"]),
                        issue_type="release_evidence_latency_exceeds_loop_credit",
                        severity=Severity.WARNING,
                        message="循环/暂存争取到的时间不足以等待慢证据，不能把仿真放行直接外推到现场。",
                        evidence=item,
                    )
                )
        if not self.conformal_readiness.get("can_write_to_release_gate", False):
            issues.append(
                QualityIssue(
                    sensor="grey_box_dynamic_latency",
                    issue_type="conformal_release_gate_not_field_ready",
                    severity=Severity.INFO,
                    message="软传感保形校准尚未通过 field holdout，延迟预算即使可行也不能单独授权放行。",
                    evidence=self.conformal_readiness,
                )
            )
        return issues

    def _recommendations(self, latency_budget: list[dict[str, object]], readiness: dict[str, object]) -> list[str]:
        recommendations = [
            "把采样时间、软传感计算时间、人工复核、执行器响应、混合时间、回流停留时间和离线检测 turnaround 写入 field schema。",
            "用真实 timestamped campaign replay 计算 latency_budget_violation_rate，不能只用 synthetic episode 的步数或成功率证明闭环可执行。",
        ]
        failed = [item for item in latency_budget if item["latency_status"] != "grey_box_latency_feasible"]
        if failed:
            scenarios = ", ".join(str(item["scenario"]) for item in failed)
            recommendations.append(
                f"优先重设 {scenarios} 的暂存/回流窗口、快检代理信号或自动执行器逻辑，直到 evidence_margin_min 和 action_latency_margin_min 同时为正。"
            )
        if readiness["release_gate_can_use_latency_budget"]:
            recommendations.append("field 时间戳、保形校准和延迟预算同时通过后，才可把该层写入 release gate。")
        else:
            recommendations.append("当前只允许把延迟预算作为模型真实性审计层，不允许作为现场自动放行依据。")
        return recommendations

    @staticmethod
    def _method_contract() -> dict[str, object]:
        return {
            "upgrade_id": "grey_box_dynamic_control_latency",
            "borrowed_from": ["parsa_2024_dynamic_control_review"],
            "reality_mapping": "把循环、暂存、低频采样、离线验证、人工复核和执行器响应共同建成时序约束。",
            "data_needs": GreyBoxDynamicLatencyAgent._default_data_needs(),
            "implementation_path": [
                "src/water_ai/agents/grey_box_dynamic_latency_agent.py",
                "experiments/run_agent40_grey_box_dynamic_latency.py",
                "deliverables/grey_box_dynamic_latency.md",
            ],
            "evaluation_metrics": GreyBoxDynamicLatencyAgent._default_metrics(),
            "failure_boundary": GreyBoxDynamicLatencyAgent._default_failure_boundary(),
        }

    @staticmethod
    def _default_data_needs() -> list[str]:
        return [
            "sampling_timestamp",
            "soft_sensor_prediction_timestamp",
            "offline_sample_timestamp",
            "offline_result_timestamp",
            "actuator_command_timestamp",
            "actuator_effect_timestamp",
            "recycle_start_end_timestamp",
            "hold_tank_release_timestamp",
            "batch_id",
        ]

    @staticmethod
    def _default_metrics() -> list[str]:
        return [
            "latency_budget_violation_rate",
            "minimum_evidence_margin_min",
            "minimum_action_margin_min",
            "field_replay_success_rate",
            "closed_loop_stability_under_delay",
        ]

    @staticmethod
    def _default_failure_boundary() -> str:
        return "synthetic replay 中的闭环稳定不等于 PLC/人工复核/检测排队/执行器滞后条件下可执行。"

    @staticmethod
    def _number(profile: dict[str, object], key: str) -> float:
        value = profile.get(key, 0.0)
        if isinstance(value, int | float):
            return float(value)
        return 0.0

    @staticmethod
    def _default_profiles() -> list[dict[str, object]]:
        common = {
            "borrowed_from": "parsa_2024_dynamic_control_review",
            "data_needs": GreyBoxDynamicLatencyAgent._default_data_needs(),
            "evaluation_metrics": GreyBoxDynamicLatencyAgent._default_metrics(),
            "failure_boundary": GreyBoxDynamicLatencyAgent._default_failure_boundary(),
            "soft_sensor_compute_min": 1.0,
            "actuator_delay_min": 5.0,
            "mixing_delay_min": 8.0,
        }
        return [
            {
                **common,
                "scenario": "sensor_faults",
                "risk_mode": "sensor_reliability",
                "reality_mapping": "低成本传感异常时需要质控窗口和旁路校准，不能即时信任放行信号。",
                "sampling_interval_min": 5.0,
                "qc_window_min": 12.0,
                "human_review_min": 10.0,
                "lab_turnaround_min": 45.0,
                "hold_buffer_min": 60.0,
                "recycle_retention_min": 24.0,
                "validation_overlap_credit_min": 15.0,
                "action_deadline_min": 110.0,
            },
            {
                **common,
                "scenario": "oxidant_limitation",
                "risk_mode": "fast_reagent_correction",
                "reality_mapping": "氧化剂不足可由在线 ORP/UV254 代理快速触发加药，但仍要考虑执行器和混合滞后。",
                "sampling_interval_min": 3.0,
                "qc_window_min": 6.0,
                "human_review_min": 4.0,
                "lab_turnaround_min": 0.0,
                "hold_buffer_min": 30.0,
                "recycle_retention_min": 36.0,
                "validation_overlap_credit_min": 0.0,
                "action_deadline_min": 70.0,
            },
            {
                **common,
                "scenario": "reaction_time_insufficient",
                "risk_mode": "retention_extension",
                "reality_mapping": "反应时间不足主要靠回流和延长停留时间处理，慢证据压力低于基质冲击场景。",
                "sampling_interval_min": 5.0,
                "qc_window_min": 8.0,
                "human_review_min": 5.0,
                "lab_turnaround_min": 30.0,
                "hold_buffer_min": 45.0,
                "recycle_retention_min": 48.0,
                "validation_overlap_credit_min": 10.0,
                "action_deadline_min": 160.0,
            },
            {
                **common,
                "scenario": "catalyst_deactivation",
                "risk_mode": "maintenance_decision",
                "reality_mapping": "催化剂失活需要生命周期验证和维护动作，回流窗口必须覆盖慢验证和停机决策。",
                "sampling_interval_min": 5.0,
                "qc_window_min": 10.0,
                "human_review_min": 15.0,
                "lab_turnaround_min": 90.0,
                "hold_buffer_min": 90.0,
                "recycle_retention_min": 72.0,
                "validation_overlap_credit_min": 30.0,
                "action_deadline_min": 240.0,
            },
            {
                **common,
                "scenario": "matrix_shock",
                "risk_mode": "pretreatment_or_switching",
                "reality_mapping": "基质冲击需要快代理信号先触发预处理/切换，离线确认往往赶不上早期控制窗口。",
                "sampling_interval_min": 3.0,
                "qc_window_min": 9.0,
                "human_review_min": 12.0,
                "lab_turnaround_min": 90.0,
                "hold_buffer_min": 45.0,
                "recycle_retention_min": 24.0,
                "validation_overlap_credit_min": 15.0,
                "action_deadline_min": 85.0,
            },
        ]

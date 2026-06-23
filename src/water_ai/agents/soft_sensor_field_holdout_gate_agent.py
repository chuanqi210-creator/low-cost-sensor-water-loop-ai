from __future__ import annotations

from collections.abc import Sequence

from water_ai.agents.base import BaseAgent
from water_ai.domain import AgentReport, QualityIssue, SensorReading, Severity
from water_ai.soft_sensor_model import TARGET_COLUMNS


class SoftSensorFieldHoldoutGateAgent(BaseAgent):
    """Gate soft-sensor release calibration on real field holdout evidence."""

    name = "soft_sensor_field_holdout_gate_agent"

    def __init__(
        self,
        *,
        uncertainty_metrics: dict[str, object] | None = None,
        conformal_metrics: dict[str, object] | None = None,
        min_uncertainty_records: int = 24,
        min_conformal_records: int = 36,
        min_evaluation_pairs: int | None = None,
        min_field_scenarios: int = 3,
        min_uncertainty_coverage: float = 0.82,
        min_conformal_coverage: float = 0.90,
        min_weak_target_coverage: float = 0.88,
        max_uncertainty_interval_width: float = 0.35,
        max_conformal_interval_width: float = 0.30,
        max_abstention_rate: float = 0.20,
        max_ood_rate: float = 0.12,
    ) -> None:
        self.uncertainty_metrics = uncertainty_metrics or {}
        self.conformal_metrics = conformal_metrics or {}
        self.min_uncertainty_records = min_uncertainty_records
        self.min_conformal_records = min_conformal_records
        self.min_evaluation_pairs = min_evaluation_pairs or len(TARGET_COLUMNS) * 8
        self.min_field_scenarios = min_field_scenarios
        self.min_uncertainty_coverage = min_uncertainty_coverage
        self.min_conformal_coverage = min_conformal_coverage
        self.min_weak_target_coverage = min_weak_target_coverage
        self.max_uncertainty_interval_width = max_uncertainty_interval_width
        self.max_conformal_interval_width = max_conformal_interval_width
        self.max_abstention_rate = max_abstention_rate
        self.max_ood_rate = max_ood_rate

    def run(self, readings: Sequence[SensorReading]) -> AgentReport:
        del readings
        evidence = self._evidence_stage()
        calibration = self._calibration_snapshot()
        gate_checks = self._gate_checks(evidence, calibration)
        readiness = self._readiness(gate_checks)
        release_policy = self._release_policy(readiness)
        issues = self._issues(gate_checks, readiness)
        recommendations = self._recommendations(readiness)
        summary = (
            f"软传感 field holdout 放行门控：{readiness['soft_sensor_field_holdout_gate_status']}；"
            f"可写 release gate {release_policy['can_write_to_release_gate']}，"
            f"自动放行 {release_policy['can_auto_release_treated_water']}。"
        )
        confidence = round(
            min(0.92, max(0.16, 0.30 + 0.48 * readiness["soft_sensor_field_holdout_gate_score"] - 0.03 * len(issues))),
            3,
        )

        return AgentReport(
            agent_name=self.name,
            confidence=confidence,
            summary=summary,
            issues=issues,
            recommendations=recommendations,
            metrics={
                "method_contract": self._method_contract(),
                "evidence": evidence,
                "calibration": calibration,
                "gate_checks": gate_checks,
                "readiness": readiness,
                "release_policy": release_policy,
            },
        )

    def _evidence_stage(self) -> dict[str, object]:
        uncertainty_stage = str(self.uncertainty_metrics.get("evidence_stage", "missing"))
        conformal_stage = str(self.conformal_metrics.get("evidence_stage", "missing"))
        uncertainty_readiness = self._dict(self.uncertainty_metrics.get("readiness"))
        conformal_readiness = self._dict(self.conformal_metrics.get("readiness"))
        return {
            "uncertainty_evidence_stage": uncertainty_stage,
            "conformal_evidence_stage": conformal_stage,
            "field_holdout_required": uncertainty_stage != "field_holdout" or conformal_stage != "field_holdout",
            "uncertainty_status": uncertainty_readiness.get("uncertainty_validation_status", "missing_uncertainty_status"),
            "conformal_status": conformal_readiness.get("conformal_status", "missing_conformal_status"),
            "upstream_conformal_can_write": bool(conformal_readiness.get("can_write_to_release_gate", False)),
        }

    def _calibration_snapshot(self) -> dict[str, object]:
        uncertainty = self._uncertainty_section()
        conformal = self._dict(self.conformal_metrics.get("conformal"))
        split = self._dict(self.conformal_metrics.get("split"))
        uncertainty_record_count = int(uncertainty.get("record_count", 0) or 0)
        conformal_record_count = int(split.get("record_count", 0) or 0)
        evaluation_pair_count = int(conformal.get("evaluation_pair_count", 0) or 0)
        uncertainty_ood_rate = self._rate(
            uncertainty.get("ood_alert_count", 0),
            uncertainty_record_count,
        )
        scenario_counts = self._dict(uncertainty.get("scenario_counts"))
        conformal_scenarios = self._dict(conformal.get("scenario_full_coverage"))
        scenario_names = set(scenario_counts) | set(conformal_scenarios)
        return {
            "uncertainty_record_count": uncertainty_record_count,
            "conformal_record_count": conformal_record_count,
            "evaluation_pair_count": evaluation_pair_count,
            "field_scenario_count": len(scenario_names),
            "uncertainty_overall_interval_coverage": float(uncertainty.get("overall_interval_coverage", 0.0) or 0.0),
            "conformal_overall_coverage": float(conformal.get("overall_conformal_coverage", 0.0) or 0.0),
            "uncertainty_mean_interval_width": float(uncertainty.get("mean_interval_width", 0.0) or 0.0),
            "conformal_mean_interval_width": float(conformal.get("mean_conformal_interval_width", 0.0) or 0.0),
            "release_abstention_rate": float(conformal.get("release_abstention_rate", 1.0) or 0.0),
            "conformal_ood_alert_rate": float(conformal.get("ood_alert_rate", 1.0) or 0.0),
            "uncertainty_ood_alert_rate": uncertainty_ood_rate,
            "uncertainty_coverage_by_target": self._dict(uncertainty.get("coverage_by_target")),
            "conformal_coverage_by_target": self._dict(conformal.get("coverage_by_target")),
            "scenario_counts": scenario_counts,
            "scenario_full_coverage": conformal_scenarios,
        }

    def _gate_checks(self, evidence: dict[str, object], calibration: dict[str, object]) -> list[dict[str, object]]:
        weak_targets = ("catalyst_activity", "matrix_interference")
        uncertainty_target_coverage = self._target_min(
            self._dict(calibration.get("uncertainty_coverage_by_target")),
            weak_targets,
        )
        conformal_target_coverage = self._target_min(
            self._dict(calibration.get("conformal_coverage_by_target")),
            weak_targets,
        )
        min_scenario_full_coverage = self._min_float(self._dict(calibration.get("scenario_full_coverage")).values(), default=0.0)
        checks = [
            self._check(
                "SFG0_field_holdout_origin",
                evidence["uncertainty_evidence_stage"] == "field_holdout"
                and evidence["conformal_evidence_stage"] == "field_holdout",
                "软传感不确定性与 conformal 校准都必须来自真实 field holdout。",
                evidence,
            ),
            self._check(
                "SFG1_record_volume",
                int(calibration["uncertainty_record_count"]) >= self.min_uncertainty_records
                and int(calibration["conformal_record_count"]) >= self.min_conformal_records
                and int(calibration["evaluation_pair_count"]) >= self.min_evaluation_pairs,
                "field holdout 记录数和评估 target-pair 数必须足以支撑 release gate。",
                {
                    "uncertainty_record_count": calibration["uncertainty_record_count"],
                    "conformal_record_count": calibration["conformal_record_count"],
                    "evaluation_pair_count": calibration["evaluation_pair_count"],
                    "min_uncertainty_records": self.min_uncertainty_records,
                    "min_conformal_records": self.min_conformal_records,
                    "min_evaluation_pairs": self.min_evaluation_pairs,
                },
            ),
            self._check(
                "SFG2_interval_coverage",
                float(calibration["uncertainty_overall_interval_coverage"]) >= self.min_uncertainty_coverage
                and float(calibration["conformal_overall_coverage"]) >= self.min_conformal_coverage,
                "预测区间和 conformal 区间覆盖率必须同时达标。",
                {
                    "uncertainty_overall_interval_coverage": calibration["uncertainty_overall_interval_coverage"],
                    "conformal_overall_coverage": calibration["conformal_overall_coverage"],
                    "min_uncertainty_coverage": self.min_uncertainty_coverage,
                    "min_conformal_coverage": self.min_conformal_coverage,
                },
            ),
            self._check(
                "SFG3_interval_width",
                float(calibration["uncertainty_mean_interval_width"]) <= self.max_uncertainty_interval_width
                and float(calibration["conformal_mean_interval_width"]) <= self.max_conformal_interval_width,
                "区间不能靠无限放宽来获得覆盖率。",
                {
                    "uncertainty_mean_interval_width": calibration["uncertainty_mean_interval_width"],
                    "conformal_mean_interval_width": calibration["conformal_mean_interval_width"],
                    "max_uncertainty_interval_width": self.max_uncertainty_interval_width,
                    "max_conformal_interval_width": self.max_conformal_interval_width,
                },
            ),
            self._check(
                "SFG4_abstention_and_ood",
                float(calibration["release_abstention_rate"]) <= self.max_abstention_rate
                and float(calibration["conformal_ood_alert_rate"]) <= self.max_ood_rate
                and float(calibration["uncertainty_ood_alert_rate"]) <= self.max_ood_rate,
                "abstention 和 OOD 不能过高，否则闭环控制会频繁进入人工/回退。",
                {
                    "release_abstention_rate": calibration["release_abstention_rate"],
                    "conformal_ood_alert_rate": calibration["conformal_ood_alert_rate"],
                    "uncertainty_ood_alert_rate": calibration["uncertainty_ood_alert_rate"],
                    "max_abstention_rate": self.max_abstention_rate,
                    "max_ood_rate": self.max_ood_rate,
                },
            ),
            self._check(
                "SFG5_weak_target_coverage",
                uncertainty_target_coverage >= self.min_weak_target_coverage
                and conformal_target_coverage >= self.min_weak_target_coverage,
                "催化剂活性和基质抑制是弱观测目标，不能只看总体覆盖率。",
                {
                    "weak_targets": list(weak_targets),
                    "uncertainty_min_weak_target_coverage": uncertainty_target_coverage,
                    "conformal_min_weak_target_coverage": conformal_target_coverage,
                    "min_weak_target_coverage": self.min_weak_target_coverage,
                },
            ),
            self._check(
                "SFG6_scenario_diversity",
                int(calibration["field_scenario_count"]) >= self.min_field_scenarios
                and min_scenario_full_coverage >= 0.75,
                "field holdout 必须覆盖多个真实工况，且不能只在单一轻松场景中过线。",
                {
                    "field_scenario_count": calibration["field_scenario_count"],
                    "min_field_scenarios": self.min_field_scenarios,
                    "min_scenario_full_coverage": min_scenario_full_coverage,
                    "required_min_scenario_full_coverage": 0.75,
                },
            ),
        ]
        return checks

    @staticmethod
    def _readiness(gate_checks: list[dict[str, object]]) -> dict[str, object]:
        passed = [check for check in gate_checks if check["passed"]]
        failed = [check for check in gate_checks if not check["passed"]]
        score = round(len(passed) / max(1, len(gate_checks)), 3)
        failed_ids = [str(check["check_id"]) for check in failed]
        if "SFG0_field_holdout_origin" in failed_ids:
            status = "soft_sensor_release_gate_blocked_non_field_holdout"
        elif failed:
            status = "soft_sensor_release_gate_blocked_calibration_gaps"
        else:
            status = "soft_sensor_field_holdout_release_candidate_ready"
        return {
            "soft_sensor_field_holdout_gate_status": status,
            "soft_sensor_field_holdout_gate_score": score,
            "passed_check_count": len(passed),
            "total_check_count": len(gate_checks),
            "failed_check_ids": failed_ids,
            "can_write_to_release_gate": not failed,
        }

    @staticmethod
    def _release_policy(readiness: dict[str, object]) -> dict[str, object]:
        can_write = bool(readiness["can_write_to_release_gate"])
        return {
            "target_agent": "SoftSensorAgent",
            "target_gate": "soft_sensor_release_gate",
            "write_scope": "field_holdout_calibrated_interval_threshold_candidate" if can_write else "no_release_gate_write",
            "can_write_to_release_gate": can_write,
            "can_auto_release_treated_water": False,
            "requires_human_review_before_application": True,
            "requires_offline_lab_confirmation_for_compliance": True,
            "forbidden_uses": [
                "direct_discharge_compliance_claim",
                "synthetic_holdout_as_field_evidence",
                "bypass_of_fault_diagnosis_or_cost_safety_agents",
            ],
        }

    @staticmethod
    def _issues(gate_checks: list[dict[str, object]], readiness: dict[str, object]) -> list[QualityIssue]:
        issues: list[QualityIssue] = []
        for check in gate_checks:
            if check["passed"]:
                continue
            severity = Severity.CRITICAL if check["check_id"] == "SFG0_field_holdout_origin" else Severity.WARNING
            issues.append(
                QualityIssue(
                    sensor="soft_sensor_field_holdout_gate",
                    issue_type=f"{check['check_id']}_failed",
                    severity=severity,
                    message=str(check["rationale"]),
                    evidence={"check": check, "readiness": readiness},
                )
            )
        if bool(readiness["can_write_to_release_gate"]) and readiness["soft_sensor_field_holdout_gate_status"] != "soft_sensor_field_holdout_release_candidate_ready":
            issues.append(
                QualityIssue(
                    sensor="soft_sensor_field_holdout_gate",
                    issue_type="release_gate_write_inconsistent_with_status",
                    severity=Severity.CRITICAL,
                    message="只有 field holdout 全部门控通过时才允许形成 release gate 校准候选。",
                    evidence=readiness,
                )
            )
        return issues

    @staticmethod
    def _recommendations(readiness: dict[str, object]) -> list[str]:
        status = str(readiness["soft_sensor_field_holdout_gate_status"])
        if status == "soft_sensor_field_holdout_release_candidate_ready":
            return [
                "可以形成软传感 release gate 校准候选，但只能作为阈值候选写入，不能直接授权出水达标或自动放行。",
                "应用前由人工复核 field holdout 批次、离线标签 QA、污染场景覆盖和控制回放结果。",
                "写入后继续监控 OOD、abstention、弱目标覆盖率，一旦漂移升高立刻回退到暂存/循环验证策略。",
            ]
        if status == "soft_sensor_release_gate_blocked_non_field_holdout":
            return [
                "当前只能保留 synthetic holdout 作为接口验证，不要写入 release gate。",
                "下一步采集真实 field holdout：传感时间序列、离线污染物标签、场景标签、软传感误差和 control outcome。",
                "重新运行 Agent36、Agent39，再由本 agent 决定是否形成 release gate 校准候选。",
            ]
        return [
            f"先修复未通过门控：{readiness['failed_check_ids']}。",
            "优先补弱目标标签、异常工况覆盖和场景分层校准，避免只靠总体 accuracy 掩盖工程风险。",
        ]

    @staticmethod
    def _method_contract() -> dict[str, object]:
        return {
            "upgrade_id": "soft_sensor_field_holdout_release_gate",
            "borrowed_from": [
                "split_conformal_prediction_interval_release_gating",
                "model_validation_and_uncertainty_calibration",
                "academic_research_agent_evidence_before_claims",
                "field_holdout_before_claim_verification",
            ],
            "reality_mapping": "把软传感器从 synthetic 可运行层推进到真实 field holdout 校准候选层，防止低成本传感闭环控制过度相信仿真区间。",
            "data_needs": [
                "field_holdout_sensor_timeseries",
                "offline_lab_residual_pollutant_labels",
                "target_abs_errors_by_hidden_state",
                "prediction_interval_coverage_by_target",
                "conformal_nonconformity_thresholds",
                "scenario_labels_for_matrix_shock_catalyst_deactivation_and_clean_release",
                "ood_and_abstention_records",
            ],
            "implementation_path": [
                "src/water_ai/agents/soft_sensor_field_holdout_gate_agent.py",
                "experiments/run_agent46_soft_sensor_field_holdout_gate.py",
                "outputs/soft_sensor_field_holdout_gate/field_holdout_gate_metrics.json",
            ],
            "evaluation_metrics": [
                "soft_sensor_field_holdout_gate_score",
                "SFG0_field_holdout_origin",
                "SFG2_interval_coverage",
                "SFG5_weak_target_coverage",
                "can_write_to_release_gate",
            ],
            "failure_boundary": "通过也只代表 soft sensor release gate calibration candidate ready，不能替代真实污染物达标检测、现场自动控制许可或长期材料寿命验证。",
        }

    def _uncertainty_section(self) -> dict[str, object]:
        return self._dict(self.uncertainty_metrics.get("uncertainty_metrics")) or self._dict(self.uncertainty_metrics.get("aggregate"))

    @staticmethod
    def _check(check_id: str, passed: bool, rationale: str, evidence: dict[str, object]) -> dict[str, object]:
        return {
            "check_id": check_id,
            "passed": bool(passed),
            "rationale": rationale,
            "evidence": evidence,
        }

    @staticmethod
    def _dict(value: object) -> dict[str, object]:
        return value if isinstance(value, dict) else {}

    @staticmethod
    def _rate(count: object, total: int) -> float:
        try:
            numerator = float(count or 0)
        except (TypeError, ValueError):
            numerator = 0.0
        return round(numerator / max(1, total), 3)

    @staticmethod
    def _target_min(coverage: dict[str, object], targets: tuple[str, ...]) -> float:
        values: list[float] = []
        for target in targets:
            value = coverage.get(target)
            if isinstance(value, int | float):
                values.append(float(value))
        return min(values) if len(values) == len(targets) else 0.0

    @staticmethod
    def _min_float(values: object, *, default: float) -> float:
        floats = [float(value) for value in values if isinstance(value, int | float)]
        return min(floats) if floats else default

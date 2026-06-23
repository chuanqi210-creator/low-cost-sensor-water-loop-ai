from __future__ import annotations

from collections.abc import Sequence
from math import ceil

from water_ai.agents.base import BaseAgent
from water_ai.domain import AgentReport, QualityIssue, SensorReading, Severity


class WeakTargetStratifiedConformalAgent(BaseAgent):
    """Audit weak hidden-state targets with target- and scenario-stratified conformal checks."""

    name = "weak_target_stratified_conformal_agent"

    def __init__(
        self,
        *,
        conformal_metrics: dict[str, object] | None = None,
        validation_records: list[dict[str, object]] | None = None,
        weak_targets: tuple[str, ...] = ("catalyst_activity", "matrix_interference"),
        min_weak_target_coverage: float = 0.88,
        max_candidate_width: float = 0.48,
        min_eval_records_per_target: int = 8,
        min_scenario_eval_records: int = 4,
        alpha: float | None = None,
    ) -> None:
        self.conformal_metrics = conformal_metrics or {}
        self.validation_records = validation_records or []
        self.weak_targets = weak_targets
        self.min_weak_target_coverage = min_weak_target_coverage
        self.max_candidate_width = max_candidate_width
        self.min_eval_records_per_target = min_eval_records_per_target
        self.min_scenario_eval_records = min_scenario_eval_records
        self.alpha = alpha

    def run(self, readings: Sequence[SensorReading]) -> AgentReport:
        del readings
        evidence = self._evidence()
        split = self._split()
        profiles = self._weak_target_profiles(split)
        gate_checks = self._gate_checks(evidence, split, profiles)
        readiness = self._readiness(evidence, gate_checks)
        handoff_policy = self._handoff_policy(readiness)
        issues = self._issues(gate_checks, readiness)
        recommendations = self._recommendations(readiness)
        weakest = min(profiles, key=lambda item: float(item["current_coverage"])) if profiles else {}
        summary = (
            f"弱目标分层保形校准：{readiness['weak_target_stratified_status']}；"
            f"最弱目标 {weakest.get('target', 'none')} coverage={weakest.get('current_coverage', 0)}。"
        )
        confidence = round(
            min(0.90, max(0.16, 0.30 + 0.45 * readiness["weak_target_stratified_score"] - 0.03 * len(issues))),
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
                "split": split,
                "weak_target_profiles": profiles,
                "gate_checks": gate_checks,
                "readiness": readiness,
                "handoff_policy": handoff_policy,
            },
        )

    def _evidence(self) -> dict[str, object]:
        conformal = self._dict(self.conformal_metrics.get("conformal"))
        readiness = self._dict(self.conformal_metrics.get("readiness"))
        evidence_stage = str(self.conformal_metrics.get("evidence_stage", "missing"))
        return {
            "evidence_stage": evidence_stage,
            "field_holdout_required": evidence_stage != "field_holdout",
            "upstream_conformal_status": readiness.get("conformal_status", "missing_conformal_status"),
            "upstream_can_write_to_release_gate": bool(readiness.get("can_write_to_release_gate", False)),
            "target_coverage_level": float(conformal.get("target_coverage_level", 1.0 - self._alpha()) or 1.0 - self._alpha()),
        }

    def _split(self) -> dict[str, object]:
        raw_split = self._dict(self.conformal_metrics.get("split"))
        record_count = len(self.validation_records)
        calibration_indices = raw_split.get("calibration_indices")
        evaluation_indices = raw_split.get("evaluation_indices")
        if not isinstance(calibration_indices, list) or not isinstance(evaluation_indices, list):
            calibration_count = max(1, min(record_count, int(round(record_count * 0.67))))
            if record_count > 1 and calibration_count == record_count:
                calibration_count = record_count - 1
            calibration_indices = list(range(calibration_count))
            evaluation_indices = list(range(calibration_count, record_count))
        return {
            "record_count": record_count,
            "calibration_indices": [int(index) for index in calibration_indices if isinstance(index, int) and index < record_count],
            "evaluation_indices": [int(index) for index in evaluation_indices if isinstance(index, int) and index < record_count],
            "calibration_count": len([index for index in calibration_indices if isinstance(index, int) and index < record_count]),
            "evaluation_count": len([index for index in evaluation_indices if isinstance(index, int) and index < record_count]),
        }

    def _weak_target_profiles(self, split: dict[str, object]) -> list[dict[str, object]]:
        conformal = self._dict(self.conformal_metrics.get("conformal"))
        coverage_by_target = self._dict(conformal.get("coverage_by_target"))
        width_by_target = self._dict(conformal.get("width_by_target"))
        base_thresholds = self._dict(conformal.get("target_nonconformity_thresholds"))
        misses_by_target = self._dict(conformal.get("misses_by_target"))
        profiles: list[dict[str, object]] = []
        for target in self.weak_targets:
            eval_errors = self._target_errors(split["evaluation_indices"], target)
            calibration_errors = self._target_errors(split["calibration_indices"], target)
            scenario_profile = self._scenario_profile(split["evaluation_indices"], target)
            current_coverage = float(coverage_by_target.get(target, self._coverage(eval_errors, float(base_thresholds.get(target, 0.0) or 0.0))) or 0.0)
            base_threshold = float(base_thresholds.get(target, self._quantile(calibration_errors)) or 0.0)
            candidate_threshold = self._candidate_threshold(base_threshold, eval_errors, current_coverage)
            candidate_width = round(2.0 * candidate_threshold, 4)
            scenario_min_coverage = self._min_scenario_coverage(scenario_profile)
            gap = round(max(0.0, self.min_weak_target_coverage - current_coverage), 3)
            profiles.append(
                {
                    "target": target,
                    "current_coverage": round(current_coverage, 3),
                    "coverage_gap": gap,
                    "base_threshold": round(base_threshold, 4),
                    "base_width": float(width_by_target.get(target, round(2.0 * base_threshold, 4)) or 0.0),
                    "miss_count": int(misses_by_target.get(target, 0) or 0),
                    "evaluation_error_count": len(eval_errors),
                    "max_evaluation_error": round(max(eval_errors), 4) if eval_errors else 0.0,
                    "candidate_threshold": round(candidate_threshold, 4),
                    "candidate_width": candidate_width,
                    "candidate_width_within_gate": candidate_width <= self.max_candidate_width,
                    "scenario_profile": scenario_profile,
                    "min_scenario_coverage": scenario_min_coverage,
                    "recommended_mode": self._recommended_mode(gap, scenario_min_coverage),
                    "candidate_use_boundary": "diagnostic_only_until_field_holdout" if self._evidence()["field_holdout_required"] else "field_candidate_for_agent46_review",
                }
            )
        return profiles

    def _gate_checks(
        self,
        evidence: dict[str, object],
        split: dict[str, object],
        profiles: list[dict[str, object]],
    ) -> list[dict[str, object]]:
        min_coverage = self._min_profile_value(profiles, "current_coverage", default=0.0)
        max_width = self._max_profile_value(profiles, "candidate_width", default=0.0)
        min_eval_count = min((int(profile["evaluation_error_count"]) for profile in profiles), default=0)
        min_scenario_coverage = self._min_profile_value(profiles, "min_scenario_coverage", default=0.0)
        checks = [
            self._check(
                "WTC0_field_holdout_origin",
                evidence["evidence_stage"] == "field_holdout",
                "弱目标分层阈值必须由真实 field holdout 确认后才可交给 release gate。",
                evidence,
            ),
            self._check(
                "WTC1_weak_target_eval_volume",
                int(split["evaluation_count"]) >= self.min_eval_records_per_target and min_eval_count >= self.min_eval_records_per_target,
                "每个弱目标都需要足够 evaluation errors 才能判断覆盖率。",
                {
                    "evaluation_count": split["evaluation_count"],
                    "min_target_eval_error_count": min_eval_count,
                    "required_min": self.min_eval_records_per_target,
                },
            ),
            self._check(
                "WTC2_weak_target_coverage",
                min_coverage >= self.min_weak_target_coverage,
                "弱目标 coverage 必须单独达标，不能被总体 coverage 掩盖。",
                {
                    "min_weak_target_coverage_observed": min_coverage,
                    "required_min": self.min_weak_target_coverage,
                },
            ),
            self._check(
                "WTC3_candidate_width_reasonable",
                max_width <= self.max_candidate_width,
                "候选阈值不能靠过宽区间换取表面 coverage。",
                {
                    "max_candidate_width": max_width,
                    "allowed_max": self.max_candidate_width,
                },
            ),
            self._check(
                "WTC4_scenario_stratification_support",
                min_scenario_coverage >= 0.75,
                "弱目标至少需要在关键场景上保持基本覆盖，失败场景必须分层校准。",
                {
                    "min_scenario_coverage": min_scenario_coverage,
                    "required_min": 0.75,
                    "min_scenario_eval_records": self.min_scenario_eval_records,
                },
            ),
            self._check(
                "WTC5_release_gate_boundary",
                evidence["upstream_can_write_to_release_gate"] is False,
                "该 agent 只能向 Agent46 提供弱目标校准候选，不能绕过 Agent46 写 release gate。",
                {
                    "upstream_can_write_to_release_gate": evidence["upstream_can_write_to_release_gate"],
                },
            ),
        ]
        return checks

    @staticmethod
    def _readiness(evidence: dict[str, object], gate_checks: list[dict[str, object]]) -> dict[str, object]:
        passed = [check for check in gate_checks if check["passed"]]
        failed = [check for check in gate_checks if not check["passed"]]
        failed_ids = [str(check["check_id"]) for check in failed]
        score = round(len(passed) / max(1, len(gate_checks)), 3)
        if evidence["field_holdout_required"]:
            status = "weak_target_stratified_synthetic_candidate_needs_field_holdout"
        elif failed:
            status = "field_weak_target_stratification_needs_recalibration"
        else:
            status = "field_weak_target_stratified_candidate_ready_for_agent46"
        return {
            "weak_target_stratified_status": status,
            "weak_target_stratified_score": score,
            "passed_check_count": len(passed),
            "total_check_count": len(gate_checks),
            "failed_check_ids": failed_ids,
            "can_pass_candidate_to_agent46": evidence["field_holdout_required"] is False and not failed,
            "can_write_to_release_gate": False,
        }

    @staticmethod
    def _handoff_policy(readiness: dict[str, object]) -> dict[str, object]:
        return {
            "target_agent": "SoftSensorFieldHoldoutGateAgent",
            "candidate_type": (
                "weak_target_stratified_threshold_candidate"
                if readiness["can_pass_candidate_to_agent46"]
                else "diagnostic_candidate_only"
            ),
            "can_pass_candidate_to_agent46": bool(readiness["can_pass_candidate_to_agent46"]),
            "can_write_to_release_gate": False,
            "can_auto_release_treated_water": False,
            "requires_field_holdout_replay": not bool(readiness["can_pass_candidate_to_agent46"]),
            "requires_human_review_before_application": True,
        }

    @staticmethod
    def _issues(gate_checks: list[dict[str, object]], readiness: dict[str, object]) -> list[QualityIssue]:
        issues: list[QualityIssue] = []
        for check in gate_checks:
            if check["passed"]:
                continue
            severity = Severity.CRITICAL if check["check_id"] == "WTC0_field_holdout_origin" else Severity.WARNING
            issues.append(
                QualityIssue(
                    sensor="weak_target_stratified_conformal",
                    issue_type=f"{check['check_id']}_failed",
                    severity=severity,
                    message=str(check["rationale"]),
                    evidence={"check": check, "readiness": readiness},
                )
            )
        return issues

    @staticmethod
    def _recommendations(readiness: dict[str, object]) -> list[str]:
        status = str(readiness["weak_target_stratified_status"])
        if status == "field_weak_target_stratified_candidate_ready_for_agent46":
            return [
                "将弱目标分层阈值候选交给 Agent46 复核，仍不得绕过 field holdout release gate。",
                "应用前保留 matrix_shock、catalyst_deactivation 和 clean_release 的分场景 coverage 记录。",
            ]
        if status == "weak_target_stratified_synthetic_candidate_needs_field_holdout":
            return [
                "保留当前弱目标分层阈值为 synthetic diagnostic candidate，不要写入 release gate。",
                "真实 field holdout 采样时必须提高 matrix_interference 和 catalyst_activity 的场景标签密度。",
                "在 Agent46 之前重跑本 agent，确认弱目标 coverage 和候选区间宽度均达标。",
            ]
        return [
            f"先修复弱目标分层门控：{readiness['failed_check_ids']}。",
            "优先按 matrix_shock、catalyst_deactivation、clean_release 分层重算 conformal thresholds。",
        ]

    @staticmethod
    def _method_contract() -> dict[str, object]:
        return {
            "upgrade_id": "weak_target_stratified_conformal_calibration",
            "borrowed_from": [
                "mondrian_or_group_conditional_conformal_prediction",
                "model_validation_and_uncertainty_targetwise_coverage",
                "academic_research_agent_evidence_before_claims",
                "field_holdout_before_release_gate",
            ],
            "reality_mapping": "把 catalyst_activity 和 matrix_interference 这类弱观测隐藏状态从总体 coverage 中拆出来，按目标和场景审查是否能进入软传感 release gate 候选。",
            "data_needs": [
                "field_holdout_target_abs_errors",
                "scenario_labels_for_matrix_shock_and_catalyst_deactivation",
                "per_target_prediction_intervals",
                "offline_lab_or_maintenance_labels_for_weak_targets",
                "ood_and_abstention_records",
            ],
            "implementation_path": [
                "src/water_ai/agents/weak_target_stratified_conformal_agent.py",
                "experiments/run_agent47_weak_target_stratified_conformal.py",
                "outputs/weak_target_stratified_conformal/weak_target_stratified_metrics.json",
            ],
            "evaluation_metrics": [
                "weak_target_stratified_score",
                "WTC2_weak_target_coverage",
                "WTC3_candidate_width_reasonable",
                "WTC4_scenario_stratification_support",
                "can_pass_candidate_to_agent46",
            ],
            "failure_boundary": "该 agent 只生成弱目标分层校准候选或诊断，不得直接写 release gate，不得替代真实污染物达标检测或 Agent46 field holdout 门控。",
        }

    def _target_errors(self, indices: object, target: str) -> list[float]:
        if not isinstance(indices, list):
            return []
        errors: list[float] = []
        for index in indices:
            if not isinstance(index, int) or index >= len(self.validation_records):
                continue
            target_errors = self._dict(self.validation_records[index].get("target_abs_errors"))
            value = target_errors.get(target)
            if isinstance(value, int | float):
                errors.append(float(value))
        return errors

    def _scenario_profile(self, indices: object, target: str) -> dict[str, dict[str, object]]:
        if not isinstance(indices, list):
            return {}
        base_threshold = float(self._dict(self._dict(self.conformal_metrics.get("conformal")).get("target_nonconformity_thresholds")).get(target, 0.0) or 0.0)
        profile: dict[str, dict[str, object]] = {}
        for index in indices:
            if not isinstance(index, int) or index >= len(self.validation_records):
                continue
            record = self.validation_records[index]
            scenario = str(record.get("scenario", "unknown"))
            target_errors = self._dict(record.get("target_abs_errors"))
            value = target_errors.get(target)
            if not isinstance(value, int | float):
                continue
            bucket = profile.setdefault(scenario, {"count": 0, "covered": 0, "max_error": 0.0})
            bucket["count"] = int(bucket["count"]) + 1
            bucket["covered"] = int(bucket["covered"]) + int(float(value) <= base_threshold)
            bucket["max_error"] = max(float(bucket["max_error"]), float(value))
        for bucket in profile.values():
            count = int(bucket["count"])
            bucket["coverage"] = round(int(bucket["covered"]) / max(1, count), 3)
            bucket["max_error"] = round(float(bucket["max_error"]), 4)
            bucket["has_min_eval_records"] = count >= self.min_scenario_eval_records
        return profile

    def _candidate_threshold(self, base_threshold: float, eval_errors: list[float], current_coverage: float) -> float:
        if not eval_errors or current_coverage >= self.min_weak_target_coverage:
            return base_threshold
        miss_envelope = max(eval_errors) * 1.05
        quantile_envelope = self._quantile(eval_errors)
        return max(base_threshold, miss_envelope, quantile_envelope)

    def _quantile(self, values: list[float]) -> float:
        if not values:
            return 0.0
        alpha = self._alpha()
        ordered = sorted(values)
        rank = ceil((len(ordered) + 1) * (1.0 - alpha))
        rank = max(1, min(len(ordered), rank))
        return ordered[rank - 1]

    def _alpha(self) -> float:
        if isinstance(self.alpha, int | float):
            return max(0.01, min(0.5, float(self.alpha)))
        value = self.conformal_metrics.get("alpha")
        return max(0.01, min(0.5, float(value))) if isinstance(value, int | float) else 0.10

    @staticmethod
    def _coverage(values: list[float], threshold: float) -> float:
        if not values:
            return 0.0
        return round(sum(1 for value in values if value <= threshold) / len(values), 3)

    @staticmethod
    def _min_scenario_coverage(profile: dict[str, dict[str, object]]) -> float:
        values = [float(bucket["coverage"]) for bucket in profile.values() if isinstance(bucket.get("coverage"), int | float)]
        return round(min(values), 3) if values else 0.0

    @staticmethod
    def _recommended_mode(gap: float, min_scenario_coverage: float) -> str:
        if gap > 0 and min_scenario_coverage < 0.88:
            return "target_and_scenario_stratified_conformal"
        if gap > 0:
            return "target_specific_conformal_margin"
        return "monitor_targetwise_coverage"

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
    def _min_profile_value(profiles: list[dict[str, object]], key: str, *, default: float) -> float:
        values = [float(profile[key]) for profile in profiles if isinstance(profile.get(key), int | float)]
        return round(min(values), 3) if values else default

    @staticmethod
    def _max_profile_value(profiles: list[dict[str, object]], key: str, *, default: float) -> float:
        values = [float(profile[key]) for profile in profiles if isinstance(profile.get(key), int | float)]
        return round(max(values), 3) if values else default

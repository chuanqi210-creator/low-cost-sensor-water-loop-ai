from __future__ import annotations

from collections.abc import Sequence
from math import ceil

from water_ai.agents.base import BaseAgent
from water_ai.domain import AgentReport, QualityIssue, SensorReading, Severity
from water_ai.soft_sensor_model import TARGET_COLUMNS


class SoftSensorConformalCalibrationAgent(BaseAgent):
    """Build a split-conformal calibration layer for soft-sensor intervals."""

    name = "soft_sensor_conformal_calibration_agent"

    def __init__(
        self,
        *,
        validation_records: list[dict[str, object]] | None = None,
        evidence_stage: str = "synthetic_holdout",
        alpha: float = 0.10,
        calibration_fraction: float = 0.67,
    ) -> None:
        self.validation_records = validation_records or []
        self.evidence_stage = evidence_stage
        self.alpha = max(0.01, min(0.5, alpha))
        self.calibration_fraction = max(0.4, min(0.8, calibration_fraction))

    def run(self, readings: Sequence[SensorReading]) -> AgentReport:
        del readings
        split = self._split_records()
        conformal = self._conformal_metrics(split)
        readiness = self._readiness(conformal)
        issues = self._issues(conformal, readiness)
        recommendations = self._recommendations(readiness)
        summary = (
            f"软传感保形校准：{readiness['conformal_status']}；"
            f"验证覆盖率 {conformal['overall_conformal_coverage']:.3f}，"
            f"平均区间宽度 {conformal['mean_conformal_interval_width']:.3f}。"
        )
        confidence = round(
            min(0.86, max(0.25, 0.42 + 0.36 * readiness["conformal_score"] - 0.04 * len(issues))),
            3,
        )

        return AgentReport(
            agent_name=self.name,
            confidence=confidence,
            summary=summary,
            issues=issues,
            recommendations=recommendations,
            metrics={
                "split": split,
                "conformal": conformal,
                "readiness": readiness,
                "evidence_stage": self.evidence_stage,
                "alpha": self.alpha,
                "validation_records": self.validation_records,
            },
        )

    def _split_records(self) -> dict[str, object]:
        records = list(self.validation_records)
        calibration_count = int(round(len(records) * self.calibration_fraction))
        calibration_count = max(1, min(len(records), calibration_count))
        if len(records) > 1 and calibration_count == len(records):
            calibration_count = len(records) - 1
        return {
            "record_count": len(records),
            "calibration_count": calibration_count,
            "evaluation_count": max(0, len(records) - calibration_count),
            "calibration_indices": list(range(calibration_count)),
            "evaluation_indices": list(range(calibration_count, len(records))),
        }

    def _conformal_metrics(self, split: dict[str, object]) -> dict[str, object]:
        records = self.validation_records
        calibration_indices = split["calibration_indices"] if isinstance(split["calibration_indices"], list) else []
        evaluation_indices = split["evaluation_indices"] if isinstance(split["evaluation_indices"], list) else []
        thresholds: dict[str, float] = {}
        coverage_by_target: dict[str, float] = {}
        width_by_target: dict[str, float] = {}
        misses_by_target: dict[str, int] = {}
        scenario_hits: dict[str, int] = {}
        scenario_counts: dict[str, int] = {}
        abstain_count = 0
        ood_alert_count = 0
        evaluated_pairs = 0
        covered_pairs = 0
        interval_widths: list[float] = []

        for target in TARGET_COLUMNS:
            residuals = [
                self._target_error(records[index], target)
                for index in calibration_indices
                if index < len(records) and self._target_error(records[index], target) is not None
            ]
            thresholds[target] = round(self._conformal_quantile([value for value in residuals if value is not None]), 4)

        for index in evaluation_indices:
            if index >= len(records):
                continue
            record = records[index]
            scenario = str(record.get("scenario", "unknown"))
            scenario_counts[scenario] = scenario_counts.get(scenario, 0) + 1
            if float(record.get("ood_risk", 0.0) or 0.0) > 0.12:
                ood_alert_count += 1
            record_hit_count = 0
            record_target_count = 0
            record_has_miss = False
            for target in TARGET_COLUMNS:
                error = self._target_error(record, target)
                if error is None:
                    continue
                evaluated_pairs += 1
                record_target_count += 1
                threshold = thresholds[target]
                width = 2.0 * threshold
                interval_widths.append(width)
                if error <= threshold:
                    covered_pairs += 1
                    record_hit_count += 1
                else:
                    misses_by_target[target] = misses_by_target.get(target, 0) + 1
                    record_has_miss = True
            if record_has_miss:
                abstain_count += 1
            if record_target_count:
                scenario_hits[scenario] = scenario_hits.get(scenario, 0) + int(record_hit_count == record_target_count)

        for target in TARGET_COLUMNS:
            target_eval_errors = [
                self._target_error(records[index], target)
                for index in evaluation_indices
                if index < len(records) and self._target_error(records[index], target) is not None
            ]
            threshold = thresholds[target]
            hits = sum(1 for error in target_eval_errors if error is not None and error <= threshold)
            coverage_by_target[target] = round(hits / max(1, len(target_eval_errors)), 3)
            width_by_target[target] = round(2.0 * threshold, 4)
            misses_by_target.setdefault(target, 0)

        scenario_full_coverage = {
            scenario: round(scenario_hits.get(scenario, 0) / max(1, count), 3)
            for scenario, count in scenario_counts.items()
        }
        overall_coverage = round(covered_pairs / max(1, evaluated_pairs), 3)
        mean_interval_width = round(sum(interval_widths) / max(1, len(interval_widths)), 4)
        target_coverage_error = round(abs(overall_coverage - (1.0 - self.alpha)), 3)
        return {
            "target_coverage_level": round(1.0 - self.alpha, 3),
            "target_nonconformity_thresholds": thresholds,
            "coverage_by_target": coverage_by_target,
            "width_by_target": width_by_target,
            "misses_by_target": misses_by_target,
            "scenario_full_coverage": scenario_full_coverage,
            "overall_conformal_coverage": overall_coverage,
            "mean_conformal_interval_width": mean_interval_width,
            "coverage_error": target_coverage_error,
            "evaluation_pair_count": evaluated_pairs,
            "release_abstention_rate": round(abstain_count / max(1, int(split["evaluation_count"])), 3),
            "ood_alert_rate": round(ood_alert_count / max(1, int(split["evaluation_count"])), 3),
        }

    def _readiness(self, conformal: dict[str, object]) -> dict[str, object]:
        coverage = float(conformal["overall_conformal_coverage"])
        coverage_error = float(conformal["coverage_error"])
        enough_records = len(self.validation_records) >= 36
        enough_evaluation = int(conformal["evaluation_pair_count"]) >= len(TARGET_COLUMNS) * 8
        interval_reasonable = float(conformal["mean_conformal_interval_width"]) <= 0.28
        score = round(
            0.34 * min(1.0, coverage / max(0.01, 1.0 - self.alpha))
            + 0.22 * max(0.0, 1.0 - coverage_error / 0.25)
            + 0.16 * float(enough_records)
            + 0.12 * float(enough_evaluation)
            + 0.08 * float(interval_reasonable)
            + 0.08 * float(self.evidence_stage == "field_holdout"),
            3,
        )
        if self.evidence_stage != "field_holdout":
            status = "synthetic_conformal_interface_ready_needs_field_holdout"
        elif coverage < 1.0 - self.alpha - 0.08:
            status = "field_conformal_intervals_need_recalibration"
        else:
            status = "field_conformal_calibration_ready"
        return {
            "conformal_status": status,
            "conformal_score": score,
            "field_holdout_required": self.evidence_stage != "field_holdout",
            "can_write_to_release_gate": self.evidence_stage == "field_holdout" and status == "field_conformal_calibration_ready",
        }

    def _issues(self, conformal: dict[str, object], readiness: dict[str, object]) -> list[QualityIssue]:
        issues: list[QualityIssue] = []
        if readiness["field_holdout_required"]:
            issues.append(
                QualityIssue(
                    sensor="soft_sensor_conformal_calibration",
                    issue_type="field_holdout_required_for_conformal_calibration",
                    severity=Severity.WARNING,
                    message="当前保形校准只在 synthetic split 上验证，不能写入现场 release gate。",
                    evidence=readiness,
                )
            )
        if float(conformal["overall_conformal_coverage"]) < 1.0 - self.alpha - 0.08:
            issues.append(
                QualityIssue(
                    sensor="soft_sensor_conformal_calibration",
                    issue_type="conformal_coverage_below_target",
                    severity=Severity.WARNING,
                    message="保形区间覆盖率低于目标，需要扩大校准集或按污染物/基质分层校准。",
                    evidence=conformal,
                )
            )
        if int(conformal["evaluation_pair_count"]) < len(TARGET_COLUMNS) * 8:
            issues.append(
                QualityIssue(
                    sensor="soft_sensor_conformal_calibration",
                    issue_type="evaluation_split_too_small",
                    severity=Severity.INFO,
                    message="保形评估样本偏少，下一步需要真实 field holdout 扩充评估集。",
                    evidence=conformal,
                )
            )
        return issues

    @staticmethod
    def _recommendations(readiness: dict[str, object]) -> list[str]:
        if readiness["field_holdout_required"]:
            return [
                "保留当前 split conformal 层作为 synthetic 接口验证，不要写入现场放行门。",
                "下一步用真实 field holdout 重新计算 nonconformity thresholds，并按污染物/基质分层评估 coverage。",
                "只有 field 覆盖率、区间宽度和 abstention rate 同时通过后，才允许把 conformal interval 写入 release gate。",
            ]
        return [
            "将 field 校准后的 conformal thresholds 写入软传感 release gate。",
            "继续监控分布漂移；一旦 OOD rate 升高，触发重新校准或人工复核。",
        ]

    def _conformal_quantile(self, residuals: list[float]) -> float:
        if not residuals:
            return 0.0
        ordered = sorted(residuals)
        rank = ceil((len(ordered) + 1) * (1.0 - self.alpha))
        rank = max(1, min(len(ordered), rank))
        return ordered[rank - 1]

    @staticmethod
    def _target_error(record: dict[str, object], target: str) -> float | None:
        errors = record.get("target_abs_errors", {})
        if not isinstance(errors, dict):
            return None
        value = errors.get(target)
        if isinstance(value, int | float):
            return float(value)
        return None

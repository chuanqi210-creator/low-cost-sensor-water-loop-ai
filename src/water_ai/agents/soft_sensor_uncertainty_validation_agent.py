from __future__ import annotations

from collections.abc import Sequence

from water_ai.agents.base import BaseAgent
from water_ai.domain import AgentReport, QualityIssue, SensorReading, Severity
from water_ai.soft_sensor_model import TARGET_COLUMNS


class SoftSensorUncertaintyValidationAgent(BaseAgent):
    """Validate soft-sensor uncertainty behavior on a labelled evaluation set."""

    name = "soft_sensor_uncertainty_validation_agent"

    def __init__(
        self,
        *,
        validation_records: list[dict[str, object]] | None = None,
        evidence_stage: str = "synthetic_holdout",
    ) -> None:
        self.validation_records = validation_records or []
        self.evidence_stage = evidence_stage

    def run(self, readings: Sequence[SensorReading]) -> AgentReport:
        del readings
        aggregate = self._aggregate()
        readiness = self._readiness(aggregate)
        issues = self._issues(aggregate, readiness)
        recommendations = self._recommendations(readiness)
        summary = (
            f"软传感不确定性验证：{readiness['uncertainty_validation_status']}；"
            f"区间覆盖率 {aggregate['overall_interval_coverage']:.3f}，"
            f"OOD 警报 {aggregate['ood_alert_count']} 次。"
        )
        confidence = round(min(0.86, max(0.25, 0.44 + 0.35 * readiness["uncertainty_validation_score"] - 0.04 * len(issues))), 3)

        return AgentReport(
            agent_name=self.name,
            confidence=confidence,
            summary=summary,
            issues=issues,
            recommendations=recommendations,
            metrics={
                "aggregate": aggregate,
                "readiness": readiness,
                "evidence_stage": self.evidence_stage,
                "validation_records": self.validation_records,
            },
        )

    def _aggregate(self) -> dict[str, object]:
        records = self.validation_records
        target_counts = {target: 0 for target in TARGET_COLUMNS}
        target_hits = {target: 0 for target in TARGET_COLUMNS}
        abs_errors: list[float] = []
        uncertainty_scores: list[float] = []
        record_error_pairs: list[tuple[float, float]] = []
        interval_widths: list[float] = []
        ood_alert_count = 0
        release_block_count = 0
        scenario_counts: dict[str, int] = {}

        for record in records:
            scenario = str(record.get("scenario", "unknown"))
            scenario_counts[scenario] = scenario_counts.get(scenario, 0) + 1
            uncertainty_score = float(record.get("uncertainty_score", 0.0) or 0.0)
            uncertainty_scores.append(uncertainty_score)
            if float(record.get("ood_risk", 0.0) or 0.0) > 0.12:
                ood_alert_count += 1
            if bool(record.get("release_blocked_by_uncertainty", False)):
                release_block_count += 1
            target_errors = record.get("target_abs_errors", {})
            target_coverage = record.get("target_interval_coverage", {})
            target_widths = record.get("target_interval_widths", {})
            if not isinstance(target_errors, dict) or not isinstance(target_coverage, dict):
                continue
            record_error_values = [float(value) for value in target_errors.values() if isinstance(value, int | float)]
            abs_errors.extend(record_error_values)
            if record_error_values:
                record_error_pairs.append((uncertainty_score, sum(record_error_values) / len(record_error_values)))
            if isinstance(target_widths, dict):
                interval_widths.extend(float(value) for value in target_widths.values() if isinstance(value, int | float))
            for target in TARGET_COLUMNS:
                if target in target_coverage:
                    target_counts[target] += 1
                    target_hits[target] += int(bool(target_coverage[target]))

        coverage_by_target = {
            target: round(target_hits[target] / max(1, target_counts[target]), 3)
            for target in TARGET_COLUMNS
        }
        overall_interval_coverage = round(sum(target_hits.values()) / max(1, sum(target_counts.values())), 3)
        mean_abs_error = round(sum(abs_errors) / max(1, len(abs_errors)), 4)
        mean_interval_width = round(sum(interval_widths) / max(1, len(interval_widths)), 4)
        median_uncertainty = sorted(uncertainty_scores)[len(uncertainty_scores) // 2] if uncertainty_scores else 0.0
        high_errors = [error for uncertainty, error in record_error_pairs if uncertainty >= median_uncertainty]
        low_errors = [error for uncertainty, error in record_error_pairs if uncertainty < median_uncertainty]
        high_error = round(sum(high_errors) / max(1, len(high_errors)), 4)
        low_error = round(sum(low_errors) / max(1, len(low_errors)), 4)
        return {
            "record_count": len(records),
            "scenario_counts": scenario_counts,
            "coverage_by_target": coverage_by_target,
            "overall_interval_coverage": overall_interval_coverage,
            "mean_abs_error": mean_abs_error,
            "mean_interval_width": mean_interval_width,
            "mean_uncertainty_score": round(sum(uncertainty_scores) / max(1, len(uncertainty_scores)), 4),
            "median_uncertainty_score": round(median_uncertainty, 4),
            "high_uncertainty_mean_abs_error": high_error,
            "low_uncertainty_mean_abs_error": low_error,
            "uncertainty_tracks_error": high_error >= low_error,
            "ood_alert_count": ood_alert_count,
            "release_block_count": release_block_count,
        }

    def _readiness(self, aggregate: dict[str, object]) -> dict[str, object]:
        coverage = float(aggregate["overall_interval_coverage"])
        enough_records = int(aggregate["record_count"]) >= 24
        uncertainty_tracks_error = bool(aggregate["uncertainty_tracks_error"])
        score = round(0.45 * min(1.0, coverage / 0.82) + 0.25 * float(enough_records) + 0.20 * float(uncertainty_tracks_error) + 0.10 * (self.evidence_stage == "field_holdout"), 3)
        if self.evidence_stage != "field_holdout":
            status = "synthetic_uncertainty_layer_ready_needs_field_holdout"
        elif coverage < 0.75:
            status = "field_uncertainty_intervals_need_recalibration"
        else:
            status = "field_uncertainty_validation_ready"
        return {
            "uncertainty_validation_status": status,
            "uncertainty_validation_score": score,
            "field_holdout_required": self.evidence_stage != "field_holdout",
        }

    @staticmethod
    def _issues(aggregate: dict[str, object], readiness: dict[str, object]) -> list[QualityIssue]:
        issues: list[QualityIssue] = []
        if readiness["field_holdout_required"]:
            issues.append(
                QualityIssue(
                    sensor="soft_sensor_uncertainty",
                    issue_type="field_holdout_required_for_uncertainty",
                    severity=Severity.WARNING,
                    message="当前不确定性验证只在 synthetic holdout 上成立，必须用真实 field holdout 校准后才能作为现场放行依据。",
                    evidence=readiness,
                )
            )
        if float(aggregate["overall_interval_coverage"]) < 0.75:
            issues.append(
                QualityIssue(
                    sensor="soft_sensor_uncertainty",
                    issue_type="prediction_interval_coverage_low",
                    severity=Severity.WARNING,
                    message="预测区间覆盖率偏低，需要重校准区间宽度或引入 conformal calibration。",
                    evidence=aggregate,
                )
            )
        if not bool(aggregate["uncertainty_tracks_error"]):
            issues.append(
                QualityIssue(
                    sensor="soft_sensor_uncertainty",
                    issue_type="uncertainty_error_alignment_weak",
                    severity=Severity.INFO,
                    message="高不确定性样本没有表现出更高误差，不确定性分数可能需要重新标定。",
                    evidence=aggregate,
                )
            )
        return issues

    @staticmethod
    def _recommendations(readiness: dict[str, object]) -> list[str]:
        if readiness["field_holdout_required"]:
            return [
                "保留当前不确定性层作为 synthetic 内部风险门，不要把它表述为现场校准完成。",
                "下一步用真实离线标签构建 field holdout，并做 prediction interval coverage 与 release probability calibration。",
                "若 field 覆盖率不足，优先使用 conformal calibration 或按污染物类别分层标定区间。",
            ]
        return [
            "可以将 field 校准后的不确定性门写入 release gate，并继续监测 OOD 样本。",
            "将高 OOD 批次回写到知识库和现场采样计划。",
        ]

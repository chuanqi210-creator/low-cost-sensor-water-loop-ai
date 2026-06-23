from __future__ import annotations

from collections.abc import Sequence
from copy import deepcopy
from math import ceil

from water_ai.agents.base import BaseAgent
from water_ai.agents.operations_scheduling_agent import OperationsSchedulingAgent
from water_ai.domain import AgentReport, QualityIssue, SensorReading, Severity


class PostReplanReplayAgent(BaseAgent):
    """Replay the next campaign envelope after a replanned control baseline is written back."""

    name = "post_replan_replay_agent"

    def __init__(
        self,
        *,
        pre_replan_records: list[dict[str, object]] | None = None,
        online_control_config: dict[str, object] | None = None,
        catalyst_spares_remaining: int = 0,
        oxidant_stock_units_remaining: float = 0.0,
        validation_staff_hours_capacity: float = 5.5,
        campaign_time_budget_min: int = 960,
        post_replan_records: list[dict[str, object]] | None = None,
    ) -> None:
        self.pre_replan_records = pre_replan_records or []
        self.online_control_config = online_control_config or {}
        self.catalyst_spares_remaining = catalyst_spares_remaining
        self.oxidant_stock_units_remaining = oxidant_stock_units_remaining
        self.validation_staff_hours_capacity = validation_staff_hours_capacity
        self.campaign_time_budget_min = campaign_time_budget_min
        self.post_replan_records = post_replan_records

    def run(self, readings: Sequence[SensorReading]) -> AgentReport:
        del readings
        before = self._operations_report(
            records=self.pre_replan_records,
            catalyst_spares_remaining=self.catalyst_spares_remaining,
            oxidant_stock_units_remaining=self.oxidant_stock_units_remaining,
            validation_staff_hours_capacity=self.validation_staff_hours_capacity,
            campaign_time_budget_min=self.campaign_time_budget_min,
        )
        projected = self._project_post_replan()
        after = self._operations_report(
            records=projected["records"],
            catalyst_spares_remaining=projected["catalyst_spares_remaining"],
            oxidant_stock_units_remaining=projected["oxidant_stock_units_remaining"],
            validation_staff_hours_capacity=projected["validation_staff_hours_capacity"],
            campaign_time_budget_min=projected["campaign_time_budget_min"],
        )
        comparison = self._comparison(before, after, projected)
        issues = self._issues(comparison)
        recommendations = self._recommendations(comparison)
        verdict = comparison["verdict"]
        summary = (
            f"重规划回放：{verdict}；验证占用 {comparison['before_validation_staff_usage']} -> "
            f"{comparison['after_validation_staff_usage']}，时间占用 {comparison['before_time_budget_usage']} -> "
            f"{comparison['after_time_budget_usage']}。"
        )
        confidence = round(min(0.95, max(0.18, 0.46 + 0.18 * comparison["impact_score"] - 0.05 * len(issues))), 3)

        return AgentReport(
            agent_name=self.name,
            confidence=confidence,
            summary=summary,
            issues=issues,
            recommendations=recommendations,
            metrics={
                "before": before,
                "after": after,
                "projection": projected["projection"],
                "comparison": comparison,
            },
        )

    def _project_post_replan(self) -> dict[str, object]:
        source_records = self.post_replan_records if self.post_replan_records is not None else self.pre_replan_records
        budget_items = self._budget_items()
        intake_fraction = self._protected_intake_fraction()
        admitted_count = max(1, min(len(source_records), ceil(len(source_records) * intake_fraction))) if source_records else 0
        records = deepcopy(source_records[:admitted_count])
        validation_multiplier = 0.78 if "外包低价值验证" in budget_items else 1.0
        if validation_multiplier != 1.0:
            for record in records:
                record["validation_minutes"] = round(float(record.get("validation_minutes", 0.0)) * validation_multiplier, 1)

        catalyst_spares_delta = 0
        if "催化剂备用供应商" in budget_items:
            catalyst_spares_delta += 1
        if "催化剂库存批复" in budget_items:
            catalyst_spares_delta += 2
        oxidant_stock_delta = 2.0 if "氧化剂库存批复" in budget_items else 0.0
        validation_hours_delta = 5.0 if "验证能力批复" in budget_items else 0.0

        return {
            "records": records,
            "catalyst_spares_remaining": self.catalyst_spares_remaining + catalyst_spares_delta,
            "oxidant_stock_units_remaining": round(self.oxidant_stock_units_remaining + oxidant_stock_delta, 3),
            "validation_staff_hours_capacity": self.validation_staff_hours_capacity + validation_hours_delta,
            "campaign_time_budget_min": self.campaign_time_budget_min,
            "projection": {
                "baseline_version": self.online_control_config.get("baseline_version", "unknown"),
                "intake_fraction": round(intake_fraction, 3),
                "admitted_batch_count": admitted_count,
                "source_batch_count": len(source_records),
                "validation_minutes_multiplier": validation_multiplier,
                "validation_hours_delta": validation_hours_delta,
                "catalyst_spares_delta": catalyst_spares_delta,
                "oxidant_stock_delta": oxidant_stock_delta,
                "budget_items_applied": budget_items,
                "selected_queue_policy": self.online_control_config.get("selected_queue_policy", {}),
                "selected_portfolio": self.online_control_config.get("selected_portfolio", {}),
            },
        }

    def _budget_items(self) -> list[str]:
        sequence = self.online_control_config.get("budget_sequence", [])
        if not isinstance(sequence, list):
            return []
        items: list[str] = []
        for entry in sequence:
            if isinstance(entry, dict) and entry.get("budget_item"):
                items.append(str(entry["budget_item"]))
        return items

    def _protected_intake_fraction(self) -> float:
        policy = self.online_control_config.get("load_control_policy", {})
        if not isinstance(policy, dict):
            return 1.0
        return max(0.1, min(1.0, float(policy.get("protected_intake_fraction", 1.0))))

    @staticmethod
    def _operations_report(
        *,
        records: list[dict[str, object]],
        catalyst_spares_remaining: int,
        oxidant_stock_units_remaining: float,
        validation_staff_hours_capacity: float,
        campaign_time_budget_min: int,
    ) -> dict[str, object]:
        report = OperationsSchedulingAgent(
            batch_records=records,
            catalyst_spares_remaining=catalyst_spares_remaining,
            oxidant_stock_units_remaining=oxidant_stock_units_remaining,
            validation_staff_hours_capacity=validation_staff_hours_capacity,
            campaign_time_budget_min=campaign_time_budget_min,
        ).run([])
        return {
            "campaign_metrics": report.metrics["campaign_metrics"],
            "bottlenecks": report.metrics["bottlenecks"],
            "schedule": report.metrics["schedule"],
        }

    def _comparison(
        self,
        before: dict[str, object],
        after: dict[str, object],
        projected: dict[str, object],
    ) -> dict[str, object]:
        before_metrics = before["campaign_metrics"]
        after_metrics = after["campaign_metrics"]
        before_ids = {str(item.get("bottleneck_id", "")) for item in before["bottlenecks"]}
        after_ids = {str(item.get("bottleneck_id", "")) for item in after["bottlenecks"]}
        validation_reduction = float(before_metrics["validation_staff_usage"]) - float(after_metrics["validation_staff_usage"])
        time_reduction = float(before_metrics["time_budget_usage"]) - float(after_metrics["time_budget_usage"])
        bottleneck_reduction = len(before_ids) - len(after_ids)
        throughput_fraction = float(projected["projection"]["admitted_batch_count"]) / max(float(projected["projection"]["source_batch_count"]), 1.0)
        impact_score = self._clip(
            0.30 * self._positive(validation_reduction)
            + 0.24 * self._positive(time_reduction)
            + 0.26 * min(max(bottleneck_reduction, 0) / max(len(before_ids), 1), 1.0)
            + 0.10 * float(after_metrics.get("success_rate", 0.0))
            + 0.10 * min(throughput_fraction / 0.45, 1.0)
        )
        if after_ids:
            verdict = "partial"
        elif throughput_fraction < 0.35:
            verdict = "partial_low_throughput"
        elif impact_score >= 0.45:
            verdict = "validated"
        else:
            verdict = "weak_effect"
        return {
            "verdict": verdict,
            "impact_score": round(impact_score, 3),
            "before_validation_staff_usage": before_metrics["validation_staff_usage"],
            "after_validation_staff_usage": after_metrics["validation_staff_usage"],
            "validation_staff_usage_reduction": round(validation_reduction, 3),
            "before_time_budget_usage": before_metrics["time_budget_usage"],
            "after_time_budget_usage": after_metrics["time_budget_usage"],
            "time_budget_usage_reduction": round(time_reduction, 3),
            "before_bottleneck_ids": sorted(before_ids),
            "after_bottleneck_ids": sorted(after_ids),
            "removed_bottleneck_ids": sorted(before_ids - after_ids),
            "remaining_bottleneck_ids": sorted(after_ids),
            "throughput_fraction": round(throughput_fraction, 3),
            "admitted_batch_count": projected["projection"]["admitted_batch_count"],
        }

    @staticmethod
    def _issues(comparison: dict[str, object]) -> list[QualityIssue]:
        issues: list[QualityIssue] = []
        if comparison["remaining_bottleneck_ids"]:
            issues.append(
                QualityIssue(
                    sensor="post_replan_replay",
                    issue_type="post_replan_bottlenecks_remaining",
                    severity=Severity.WARNING,
                    message="重规划回放后仍有瓶颈，下一轮 campaign 不能恢复满负荷。",
                    evidence={"remaining_bottleneck_ids": comparison["remaining_bottleneck_ids"]},
                )
            )
        if float(comparison["throughput_fraction"]) < 0.50:
            issues.append(
                QualityIssue(
                    sensor="post_replan_replay",
                    issue_type="throughput_tradeoff",
                    severity=Severity.INFO,
                    message="瓶颈改善依赖保护性限流，需要记录吞吐代价。",
                    evidence={"throughput_fraction": comparison["throughput_fraction"]},
                )
            )
        return issues

    @staticmethod
    def _recommendations(comparison: dict[str, object]) -> list[str]:
        recommendations = [
            f"回放结论为 {comparison['verdict']}，下一轮按 {comparison['throughput_fraction']} 吞吐比例执行并继续滚动遥测。",
        ]
        if comparison["remaining_bottleneck_ids"]:
            recommendations.append("仍有残余瓶颈，保持 replan_and_protect，并再次运行自动重规划链。")
        else:
            recommendations.append("瓶颈已清空，可在连续两个 campaign 稳定后按 0.15 梯度恢复进水。")
        recommendations.append("保留最终放行门、副产物和催化剂寿命慢证据，不因回放改善而取消安全验证。")
        return recommendations

    @staticmethod
    def _positive(value: float) -> float:
        return max(0.0, min(1.0, value))

    @staticmethod
    def _clip(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
        return max(lo, min(hi, value))

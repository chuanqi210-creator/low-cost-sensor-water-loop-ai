from __future__ import annotations

from collections.abc import Sequence
from copy import deepcopy
from math import ceil

from water_ai.agents.base import BaseAgent
from water_ai.agents.operations_scheduling_agent import OperationsSchedulingAgent
from water_ai.domain import AgentReport, QualityIssue, SensorReading, Severity


class RecoveryRampAgent(BaseAgent):
    """Test whether intake can recover after a validated post-replan replay."""

    name = "recovery_ramp_agent"

    def __init__(
        self,
        *,
        source_records: list[dict[str, object]] | None = None,
        online_control_config: dict[str, object] | None = None,
        catalyst_spares_remaining: int = 0,
        oxidant_stock_units_remaining: float = 0.0,
        validation_staff_hours_capacity: float = 5.5,
        campaign_time_budget_min: int = 960,
        start_fraction: float | None = None,
        ramp_step: float | None = None,
        target_stable_campaigns: int | None = None,
    ) -> None:
        self.source_records = source_records or []
        self.online_control_config = online_control_config or {}
        self.catalyst_spares_remaining = catalyst_spares_remaining
        self.oxidant_stock_units_remaining = oxidant_stock_units_remaining
        self.validation_staff_hours_capacity = validation_staff_hours_capacity
        self.campaign_time_budget_min = campaign_time_budget_min
        self.start_fraction = start_fraction if start_fraction is not None else self._protected_intake_fraction()
        rules = self.online_control_config.get("writeback_rules", {})
        if not isinstance(rules, dict):
            rules = {}
        self.ramp_step = ramp_step if ramp_step is not None else float(rules.get("ramp_step", 0.15))
        self.target_stable_campaigns = (
            target_stable_campaigns
            if target_stable_campaigns is not None
            else int(rules.get("stable_campaigns_required_for_ramp", 2))
        )

    def run(self, readings: Sequence[SensorReading]) -> AgentReport:
        del readings
        ramp_path = self._ramp_path()
        stable_count = sum(1 for item in ramp_path if item["stable"])
        final_safe = self._final_safe_state(ramp_path)
        target_met = stable_count >= self.target_stable_campaigns
        limiting_step = self._limiting_step(ramp_path)
        limiting_bottlenecks = list(limiting_step.get("bottleneck_ids", [])) if limiting_step else []
        verdict = self._verdict(target_met, stable_count, limiting_bottlenecks)
        issues = self._issues(target_met, limiting_step)
        recommendations = self._recommendations(verdict, final_safe, limiting_step)
        summary = (
            f"恢复爬坡：{verdict}；稳定轮次 {stable_count}/{self.target_stable_campaigns}，"
            f"安全进水上限 {final_safe['intake_fraction']}，实际吞吐 {final_safe['throughput_fraction']}。"
        )
        confidence = round(min(0.95, max(0.18, 0.44 + 0.12 * len(ramp_path) + 0.18 * float(target_met) - 0.05 * len(issues))), 3)

        return AgentReport(
            agent_name=self.name,
            confidence=confidence,
            summary=summary,
            issues=issues,
            recommendations=recommendations,
            metrics={
                "ramp_verdict": verdict,
                "target_met": target_met,
                "stable_campaigns_completed": stable_count,
                "target_stable_campaigns": self.target_stable_campaigns,
                "start_fraction": round(self.start_fraction, 3),
                "ramp_step": round(self.ramp_step, 3),
                "source_batch_count": len(self.source_records),
                "resource_projection": self._resource_projection(),
                "final_safe_intake_fraction": final_safe["intake_fraction"],
                "final_safe_throughput_fraction": final_safe["throughput_fraction"],
                "limiting_bottlenecks": limiting_bottlenecks,
                "limiting_attempted_fraction": limiting_step.get("attempted_intake_fraction") if limiting_step else None,
                "ramp_path": ramp_path,
            },
        )

    def _ramp_path(self) -> list[dict[str, object]]:
        path: list[dict[str, object]] = []
        current_fraction = self.start_fraction
        for step_index in range(1, self.target_stable_campaigns + 1):
            attempted_fraction = min(1.0, current_fraction + self.ramp_step)
            projection = self._project_fraction(attempted_fraction)
            bottleneck_ids = [str(item.get("bottleneck_id", "")) for item in projection["operations"]["bottlenecks"]]
            metrics = projection["operations"]["campaign_metrics"]
            stable = (
                not bottleneck_ids
                and float(metrics.get("success_rate", 0.0)) >= 0.95
                and float(metrics.get("validation_staff_usage", 1.0)) < 0.90
                and float(metrics.get("time_budget_usage", 1.0)) < 0.90
            )
            step = {
                "step_index": step_index,
                "attempted_intake_fraction": round(attempted_fraction, 3),
                "actual_throughput_fraction": projection["actual_throughput_fraction"],
                "admitted_batch_count": projection["admitted_batch_count"],
                "stable": stable,
                "bottleneck_ids": bottleneck_ids,
                "success_rate": metrics["success_rate"],
                "validation_staff_usage": metrics["validation_staff_usage"],
                "time_budget_usage": metrics["time_budget_usage"],
                "catalyst_spares_remaining": metrics["catalyst_spares_remaining"],
                "oxidant_stock_units_remaining": metrics["oxidant_stock_units_remaining"],
                "operating_mode": projection["operations"]["schedule"]["operating_mode"],
            }
            path.append(step)
            if not stable:
                break
            current_fraction = attempted_fraction
        return path

    def _project_fraction(self, intake_fraction: float) -> dict[str, object]:
        source_count = len(self.source_records)
        admitted_count = max(1, min(source_count, ceil(source_count * intake_fraction))) if source_count else 0
        records = deepcopy(self.source_records[:admitted_count])
        budget_items = self._budget_items()
        validation_multiplier = self._resource_projection()["validation_minutes_multiplier"]
        if validation_multiplier != 1.0:
            for record in records:
                record["validation_minutes"] = round(float(record.get("validation_minutes", 0.0)) * validation_multiplier, 1)
        operations = self._operations_report(records)
        return {
            "operations": operations,
            "admitted_batch_count": admitted_count,
            "actual_throughput_fraction": round(admitted_count / max(source_count, 1), 3),
        }

    def _operations_report(self, records: list[dict[str, object]]) -> dict[str, object]:
        resource_projection = self._resource_projection()
        report = OperationsSchedulingAgent(
            batch_records=records,
            catalyst_spares_remaining=int(resource_projection["catalyst_spares_projected"]),
            oxidant_stock_units_remaining=float(resource_projection["oxidant_stock_projected"]),
            validation_staff_hours_capacity=float(resource_projection["validation_staff_hours_projected"]),
            campaign_time_budget_min=self.campaign_time_budget_min,
        ).run([])
        return {
            "campaign_metrics": report.metrics["campaign_metrics"],
            "bottlenecks": report.metrics["bottlenecks"],
            "schedule": report.metrics["schedule"],
        }

    def _budget_items(self) -> list[str]:
        sequence = self.online_control_config.get("budget_sequence", [])
        if not isinstance(sequence, list):
            return []
        return [
            str(item["budget_item"])
            for item in sequence
            if isinstance(item, dict) and item.get("budget_item")
        ]

    def _resource_projection(self) -> dict[str, object]:
        budget_items = self._budget_items()
        catalyst_spares_delta = 0
        if "催化剂备用供应商" in budget_items:
            catalyst_spares_delta += 1
        if "催化剂库存批复" in budget_items:
            catalyst_spares_delta += 2
        oxidant_stock_delta = 2.0 if "氧化剂库存批复" in budget_items else 0.0
        validation_hours_delta = 5.0 if "验证能力批复" in budget_items else 0.0
        validation_multiplier = 0.78 if "外包低价值验证" in budget_items else 1.0
        return {
            "budget_items_applied": budget_items,
            "validation_minutes_multiplier": validation_multiplier,
            "validation_staff_hours_delta": validation_hours_delta,
            "validation_staff_hours_projected": round(self.validation_staff_hours_capacity + validation_hours_delta, 3),
            "catalyst_spares_delta": catalyst_spares_delta,
            "catalyst_spares_projected": self.catalyst_spares_remaining + catalyst_spares_delta,
            "oxidant_stock_delta": oxidant_stock_delta,
            "oxidant_stock_projected": round(self.oxidant_stock_units_remaining + oxidant_stock_delta, 3),
            "campaign_time_budget_min": self.campaign_time_budget_min,
        }

    def _protected_intake_fraction(self) -> float:
        policy = self.online_control_config.get("load_control_policy", {})
        if not isinstance(policy, dict):
            return 0.45
        return max(0.1, min(1.0, float(policy.get("protected_intake_fraction", 0.45))))

    def _final_safe_state(self, ramp_path: list[dict[str, object]]) -> dict[str, float]:
        safe_intake_fraction = round(self.start_fraction, 3)
        safe_throughput_fraction = round(self.start_fraction, 3)
        for item in ramp_path:
            if item["stable"]:
                safe_intake_fraction = float(item["attempted_intake_fraction"])
                safe_throughput_fraction = float(item["actual_throughput_fraction"])
            else:
                break
        return {
            "intake_fraction": round(safe_intake_fraction, 3),
            "throughput_fraction": round(safe_throughput_fraction, 3),
        }

    @staticmethod
    def _limiting_step(ramp_path: list[dict[str, object]]) -> dict[str, object] | None:
        for item in ramp_path:
            if not item["stable"]:
                return item
        return None

    @staticmethod
    def _verdict(target_met: bool, stable_count: int, limiting_bottlenecks: list[str]) -> str:
        if target_met:
            return "two_step_ramp_validated"
        if stable_count > 0 and limiting_bottlenecks:
            return "partial_ramp_hold"
        if limiting_bottlenecks:
            return "hold_protected_intake"
        return "insufficient_data"

    @staticmethod
    def _issues(target_met: bool, limiting_step: dict[str, object] | None) -> list[QualityIssue]:
        if target_met:
            return []
        limiting_bottlenecks = list(limiting_step.get("bottleneck_ids", [])) if limiting_step else []
        attempted_fraction = limiting_step.get("attempted_intake_fraction") if limiting_step else None
        return [
            QualityIssue(
                sensor="recovery_ramp",
                issue_type="ramp_limited_by_bottleneck",
                severity=Severity.WARNING,
                message="恢复进水爬坡会重新触发瓶颈，不能连续两轮按 0.15 梯度恢复。",
                evidence={
                    "attempted_intake_fraction": attempted_fraction,
                    "limiting_bottlenecks": limiting_bottlenecks,
                },
            )
        ]

    @staticmethod
    def _recommendations(
        verdict: str,
        final_safe: dict[str, float],
        limiting_step: dict[str, object] | None,
    ) -> list[str]:
        if verdict == "two_step_ramp_validated":
            return [
                f"连续两轮恢复验证通过，可把下一轮默认进水比例更新到 {final_safe['intake_fraction']}。",
                "继续保留最终放行门、副产物和催化剂寿命慢证据。",
            ]
        limiting_bottlenecks = list(limiting_step.get("bottleneck_ids", [])) if limiting_step else []
        attempted_fraction = limiting_step.get("attempted_intake_fraction") if limiting_step else "unknown"
        return [
            f"恢复进水上限暂定为 {final_safe['intake_fraction']}，实际吞吐 {final_safe['throughput_fraction']}；尝试 {attempted_fraction} 时会触发 {limiting_bottlenecks}。",
            "保持保护性进水并优先处理限制瓶颈，再重新运行恢复爬坡验证。",
        ]

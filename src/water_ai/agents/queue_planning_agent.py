from __future__ import annotations

from collections.abc import Sequence

from water_ai.agents.base import BaseAgent
from water_ai.domain import AgentReport, QualityIssue, SensorReading, Severity


class QueuePlanningAgent(BaseAgent):
    """Compare batch ordering policies before committing to a campaign queue."""

    name = "queue_planning_agent"

    def __init__(
        self,
        *,
        candidate_plans: list[dict[str, object]] | None = None,
    ) -> None:
        self.candidate_plans = candidate_plans or []

    def run(self, readings: Sequence[SensorReading]) -> AgentReport:
        ranked = [self._evaluate_plan(plan) for plan in self.candidate_plans]
        ranked.sort(key=lambda item: item["queue_score"], reverse=True)
        selected = ranked[0] if ranked else {}

        issues = [
            QualityIssue(
                sensor="queue",
                issue_type="queue_policy_risk",
                severity=Severity.WARNING,
                message="所有候选队列都存在明显运行瓶颈，需要增加资源或降低进水负荷。",
                evidence={"best_plan": selected},
            )
        ] if selected and float(selected["queue_score"]) < 0.45 else []
        recommendations = [self._sentence(item) for item in ranked[:3]]
        summary = (
            f"队列规划：推荐 {selected.get('policy_id', 'none')}，评分 {selected.get('queue_score', 0.0)}。"
            if selected
            else "队列规划：没有候选批次顺序可评价。"
        )
        confidence = round(min(0.95, max(0.15, 0.35 + 0.12 * len(ranked) + 0.30 * float(selected.get("success_rate", 0.0) if selected else 0.0))), 3)

        return AgentReport(
            agent_name=self.name,
            confidence=confidence,
            summary=summary,
            issues=issues,
            recommendations=recommendations or ["请提供至少一个候选批次顺序。"],
            metrics={
                "selected_policy": selected,
                "ranked_policies": ranked,
            },
        )

    def _evaluate_plan(self, plan: dict[str, object]) -> dict[str, object]:
        metrics = self._metrics(plan)
        bottlenecks = self._bottlenecks(plan)
        schedule = plan.get("schedule", {})
        operating_mode = str(schedule.get("operating_mode", "unknown")) if isinstance(schedule, dict) else "unknown"

        success_rate = float(metrics.get("success_rate", 0.0))
        validation_usage = float(metrics.get("validation_staff_usage", 1.0))
        time_usage = float(metrics.get("time_budget_usage", 1.0))
        catalyst_spares = float(metrics.get("catalyst_spares_remaining", 0.0))
        oxidant_stock = float(metrics.get("oxidant_stock_units_remaining", 0.0))
        bottleneck_penalty = self._bottleneck_penalty(bottlenecks)
        mode_penalty = {"normal_intake": 0.0, "staggered_intake": 0.08, "pause_or_limit_intake": 0.18}.get(operating_mode, 0.12)
        resource_reserve = self._clip(0.50 * min(catalyst_spares / 2.0, 1.0) + 0.50 * min(oxidant_stock / 1.2, 1.0))
        queue_score = self._clip(
            0.42 * success_rate
            + 0.20 * (1.0 - min(validation_usage, 1.4) / 1.4)
            + 0.18 * (1.0 - min(time_usage, 1.5) / 1.5)
            + 0.14 * resource_reserve
            - bottleneck_penalty
            - mode_penalty
        )
        return {
            "policy_id": str(plan.get("policy_id", "unknown")),
            "description": str(plan.get("description", "")),
            "scenarios": list(plan.get("scenarios", [])) if isinstance(plan.get("scenarios", []), list) else [],
            "queue_score": round(queue_score, 3),
            "success_rate": round(success_rate, 3),
            "validation_staff_usage": round(validation_usage, 3),
            "time_budget_usage": round(time_usage, 3),
            "catalyst_spares_remaining": int(catalyst_spares),
            "oxidant_stock_units_remaining": round(oxidant_stock, 3),
            "operating_mode": operating_mode,
            "bottleneck_ids": [str(item.get("bottleneck_id", "")) for item in bottlenecks],
            "next_batches": list(plan.get("scenarios", []))[:3] if isinstance(plan.get("scenarios", []), list) else [],
        }

    @staticmethod
    def _metrics(plan: dict[str, object]) -> dict[str, object]:
        metrics = plan.get("campaign_metrics", {})
        return metrics if isinstance(metrics, dict) else {}

    @staticmethod
    def _bottlenecks(plan: dict[str, object]) -> list[dict[str, object]]:
        bottlenecks = plan.get("bottlenecks", [])
        return [item for item in bottlenecks if isinstance(item, dict)] if isinstance(bottlenecks, list) else []

    @staticmethod
    def _bottleneck_penalty(bottlenecks: list[dict[str, object]]) -> float:
        penalty = 0.0
        for item in bottlenecks:
            severity = str(item.get("severity", "warning"))
            penalty += 0.10 if severity == "critical" else 0.05
        return penalty

    @staticmethod
    def _sentence(item: dict[str, object]) -> str:
        return (
            f"{item['policy_id']}：评分 {item['queue_score']}，模式 {item['operating_mode']}，"
            f"验证占用 {item['validation_staff_usage']}，时间占用 {item['time_budget_usage']}，"
            f"前 3 批 {item['next_batches']}。"
        )

    @staticmethod
    def _clip(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
        return max(lo, min(hi, value))

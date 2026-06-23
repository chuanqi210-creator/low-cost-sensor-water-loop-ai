from __future__ import annotations

from collections.abc import Sequence
from copy import deepcopy

from water_ai.agents.base import BaseAgent
from water_ai.agents.operations_scheduling_agent import OperationsSchedulingAgent
from water_ai.domain import AgentReport, QualityIssue, SensorReading, Severity


class ResourceExpansionAgent(BaseAgent):
    """Compare resource interventions when queue ordering cannot remove bottlenecks."""

    name = "resource_expansion_agent"

    def __init__(
        self,
        *,
        batch_records: list[dict[str, object]] | None = None,
        catalyst_spares_remaining: int = 0,
        oxidant_stock_units_remaining: float = 0.0,
        validation_staff_hours_capacity: float = 5.5,
        campaign_time_budget_min: int = 960,
        candidate_interventions: list[dict[str, object]] | None = None,
    ) -> None:
        self.batch_records = batch_records or []
        self.catalyst_spares_remaining = catalyst_spares_remaining
        self.oxidant_stock_units_remaining = oxidant_stock_units_remaining
        self.validation_staff_hours_capacity = validation_staff_hours_capacity
        self.campaign_time_budget_min = campaign_time_budget_min
        self.candidate_interventions = candidate_interventions or self._default_interventions()

    def run(self, readings: Sequence[SensorReading]) -> AgentReport:
        baseline = self._operations_report(
            batch_records=self.batch_records,
            catalyst_spares_remaining=self.catalyst_spares_remaining,
            oxidant_stock_units_remaining=self.oxidant_stock_units_remaining,
            validation_staff_hours_capacity=self.validation_staff_hours_capacity,
            campaign_time_budget_min=self.campaign_time_budget_min,
        )
        evaluated = [self._evaluate_intervention(intervention, baseline) for intervention in self.candidate_interventions]
        evaluated.sort(key=lambda item: item["intervention_score"], reverse=True)
        selected = evaluated[0] if evaluated else {}

        residual_bottlenecks = selected.get("residual_bottleneck_ids", []) if selected else []
        issues = [
            QualityIssue(
                sensor="resource",
                issue_type="residual_bottlenecks",
                severity=Severity.WARNING,
                message="最佳资源干预后仍存在运行瓶颈，需要组合措施或降低进水负荷。",
                evidence={"selected_intervention": selected},
            )
        ] if residual_bottlenecks else []
        recommendations = [self._sentence(item) for item in evaluated[:4]]
        summary = (
            f"资源扩容：推荐 {selected.get('intervention_id', 'none')}，评分 {selected.get('intervention_score', 0.0)}。"
            if selected
            else "资源扩容：没有候选干预可评价。"
        )
        confidence = round(min(0.95, max(0.15, 0.48 + 0.06 * len(evaluated) + 0.18 * float(selected.get("bottleneck_relief", 0.0) if selected else 0.0))), 3)

        return AgentReport(
            agent_name=self.name,
            confidence=confidence,
            summary=summary,
            issues=issues,
            recommendations=recommendations or ["请提供至少一个资源扩容候选方案。"],
            metrics={
                "baseline": baseline,
                "selected_intervention": selected,
                "ranked_interventions": evaluated,
            },
        )

    def _evaluate_intervention(
        self,
        intervention: dict[str, object],
        baseline: dict[str, object],
    ) -> dict[str, object]:
        adjusted_records = deepcopy(self.batch_records)
        catalyst_spares_remaining = self.catalyst_spares_remaining + int(intervention.get("catalyst_spares_delta", 0))
        oxidant_stock_units_remaining = self.oxidant_stock_units_remaining + float(intervention.get("oxidant_stock_delta", 0.0))
        validation_staff_hours_capacity = self.validation_staff_hours_capacity + float(intervention.get("validation_hours_delta", 0.0))
        campaign_time_budget_min = self.campaign_time_budget_min + int(intervention.get("campaign_time_delta_min", 0))
        validation_multiplier = float(intervention.get("validation_minutes_multiplier", 1.0))
        if validation_multiplier != 1.0:
            for record in adjusted_records:
                record["validation_minutes"] = round(float(record.get("validation_minutes", 0.0)) * validation_multiplier, 1)

        adjusted = self._operations_report(
            batch_records=adjusted_records,
            catalyst_spares_remaining=catalyst_spares_remaining,
            oxidant_stock_units_remaining=oxidant_stock_units_remaining,
            validation_staff_hours_capacity=validation_staff_hours_capacity,
            campaign_time_budget_min=campaign_time_budget_min,
        )
        baseline_penalty = self._bottleneck_penalty(baseline["bottlenecks"])
        adjusted_penalty = self._bottleneck_penalty(adjusted["bottlenecks"])
        bottleneck_relief = max(0.0, baseline_penalty - adjusted_penalty)
        intervention_cost = float(intervention.get("implementation_cost_index", 0.0))
        implementation_risk = float(intervention.get("implementation_risk", 0.0))
        metrics = adjusted["campaign_metrics"]
        validation_usage = float(metrics.get("validation_staff_usage", 1.0))
        time_usage = float(metrics.get("time_budget_usage", 1.0))
        spares = float(metrics.get("catalyst_spares_remaining", 0.0))
        oxidant = float(metrics.get("oxidant_stock_units_remaining", 0.0))
        reserve_score = self._clip(0.45 * min(spares / 2.0, 1.0) + 0.35 * min(oxidant / 1.2, 1.0) + 0.20 * (1.0 - min(validation_usage, 1.2) / 1.2))
        intervention_score = self._clip(
            0.42 * bottleneck_relief
            + 0.20 * reserve_score
            + 0.18 * (1.0 - min(time_usage, 1.4) / 1.4)
            + 0.12 * (1.0 - min(validation_usage, 1.4) / 1.4)
            - 0.18 * intervention_cost
            - 0.16 * implementation_risk
        )
        return {
            "intervention_id": str(intervention.get("intervention_id", "unknown")),
            "description": str(intervention.get("description", "")),
            "intervention_score": round(intervention_score, 3),
            "bottleneck_relief": round(bottleneck_relief, 3),
            "implementation_cost_index": round(intervention_cost, 3),
            "implementation_risk": round(implementation_risk, 3),
            "adjusted_operating_mode": adjusted["schedule"]["operating_mode"],
            "adjusted_validation_staff_usage": metrics["validation_staff_usage"],
            "adjusted_time_budget_usage": metrics["time_budget_usage"],
            "adjusted_catalyst_spares_remaining": metrics["catalyst_spares_remaining"],
            "adjusted_oxidant_stock_units_remaining": metrics["oxidant_stock_units_remaining"],
            "residual_bottleneck_ids": [item["bottleneck_id"] for item in adjusted["bottlenecks"]],
            "action_queue": adjusted["schedule"]["action_queue"],
        }

    @staticmethod
    def _operations_report(
        *,
        batch_records: list[dict[str, object]],
        catalyst_spares_remaining: int,
        oxidant_stock_units_remaining: float,
        validation_staff_hours_capacity: float,
        campaign_time_budget_min: int,
    ) -> dict[str, object]:
        report = OperationsSchedulingAgent(
            batch_records=batch_records,
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

    @staticmethod
    def _bottleneck_penalty(bottlenecks: list[dict[str, object]]) -> float:
        penalty = 0.0
        for item in bottlenecks:
            severity = str(item.get("severity", "warning"))
            penalty += 1.0 if severity == "critical" else 0.45
        return penalty

    @staticmethod
    def _sentence(item: dict[str, object]) -> str:
        return (
            f"{item['intervention_id']}：评分 {item['intervention_score']}，解除瓶颈 {item['bottleneck_relief']}，"
            f"验证占用 {item['adjusted_validation_staff_usage']}，时间占用 {item['adjusted_time_budget_usage']}，"
            f"剩余瓶颈 {item['residual_bottleneck_ids']}。"
        )

    @staticmethod
    def _default_interventions() -> list[dict[str, object]]:
        return [
            {
                "intervention_id": "add_validation_shift",
                "description": "增加一个旁路快检/离线验证班次。",
                "validation_hours_delta": 5.0,
                "implementation_cost_index": 0.42,
                "implementation_risk": 0.08,
            },
            {
                "intervention_id": "add_catalyst_spare",
                "description": "新增一个催化剂模块备件。",
                "catalyst_spares_delta": 1,
                "implementation_cost_index": 0.62,
                "implementation_risk": 0.06,
            },
            {
                "intervention_id": "replenish_oxidant_stock",
                "description": "补充氧化剂库存。",
                "oxidant_stock_delta": 1.5,
                "implementation_cost_index": 0.22,
                "implementation_risk": 0.04,
            },
            {
                "intervention_id": "compress_low_value_validation",
                "description": "压缩低价值验证项，把慢证据集中到放行门、副产物和催化剂风险。",
                "validation_minutes_multiplier": 0.72,
                "implementation_cost_index": 0.18,
                "implementation_risk": 0.16,
            },
            {
                "intervention_id": "extend_campaign_window",
                "description": "延长当日运行窗口。",
                "campaign_time_delta_min": 360,
                "implementation_cost_index": 0.32,
                "implementation_risk": 0.10,
            },
            {
                "intervention_id": "validation_shift_plus_spare",
                "description": "同时增加验证班次和催化剂备件。",
                "validation_hours_delta": 5.0,
                "catalyst_spares_delta": 1,
                "implementation_cost_index": 0.86,
                "implementation_risk": 0.10,
            },
            {
                "intervention_id": "full_resource_recovery",
                "description": "验证班次、催化剂备件、运行窗口和验证项压缩组合干预。",
                "validation_hours_delta": 5.0,
                "catalyst_spares_delta": 1,
                "campaign_time_delta_min": 360,
                "validation_minutes_multiplier": 0.78,
                "implementation_cost_index": 1.05,
                "implementation_risk": 0.18,
            },
        ]

    @staticmethod
    def _clip(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
        return max(lo, min(hi, value))

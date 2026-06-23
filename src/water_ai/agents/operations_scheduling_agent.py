from __future__ import annotations

from collections.abc import Sequence

from water_ai.agents.base import BaseAgent
from water_ai.domain import AgentReport, QualityIssue, SensorReading, Severity


class OperationsSchedulingAgent(BaseAgent):
    """Schedule intake, validation, consumables, and maintenance across batches."""

    name = "operations_scheduling_agent"

    def __init__(
        self,
        *,
        batch_records: list[dict[str, object]] | None = None,
        catalyst_spares_remaining: int = 1,
        oxidant_stock_units_remaining: float = 3.0,
        validation_staff_hours_capacity: float = 6.0,
        campaign_time_budget_min: int = 960,
    ) -> None:
        self.batch_records = batch_records or []
        self.catalyst_spares_remaining = catalyst_spares_remaining
        self.oxidant_stock_units_remaining = oxidant_stock_units_remaining
        self.validation_staff_hours_capacity = validation_staff_hours_capacity
        self.campaign_time_budget_min = campaign_time_budget_min

    def run(self, readings: Sequence[SensorReading]) -> AgentReport:
        metrics = self._campaign_metrics()
        bottlenecks = self._bottlenecks(metrics)
        schedule = self._schedule(metrics, bottlenecks)

        issues = [
            QualityIssue(
                sensor="operations",
                issue_type=item["bottleneck_id"],
                severity=Severity.CRITICAL if item["severity"] == "critical" else Severity.WARNING,
                message=item["message"],
                evidence=item,
            )
            for item in bottlenecks
        ]
        recommendations = [item["instruction"] for item in schedule["action_queue"]]
        summary = (
            f"运行调度：{schedule['operating_mode']}；成功率 {metrics['success_rate']}，"
            f"验证工时占用 {metrics['validation_staff_usage']}，催化剂备件 {self.catalyst_spares_remaining}。"
        )
        confidence = round(min(0.95, max(0.2, 0.50 + 0.35 * metrics["evidence_strength"] - 0.08 * len(bottlenecks))), 3)

        return AgentReport(
            agent_name=self.name,
            confidence=confidence,
            summary=summary,
            issues=issues,
            recommendations=recommendations or ["维持当前进水节奏，继续滚动更新 campaign 级运行指标。"],
            metrics={
                "campaign_metrics": metrics,
                "bottlenecks": bottlenecks,
                "schedule": schedule,
            },
        )

    def _campaign_metrics(self) -> dict[str, float | int]:
        records = self.batch_records
        batch_count = len(records)
        successes = sum(1 for record in records if bool(record.get("success", False)))
        total_elapsed = sum(float(record.get("elapsed_min", 0.0)) for record in records)
        total_cost = sum(float(record.get("cumulative_cost", 0.0)) for record in records)
        total_energy = sum(float(record.get("cumulative_energy", 0.0)) for record in records)
        validation_minutes = sum(float(record.get("validation_minutes", 0.0)) for record in records)
        regeneration_count = sum(int(record.get("regeneration_count", 0)) for record in records)
        replacement_count = sum(int(record.get("replacement_count", 0)) for record in records)
        oxidant_dose_count = sum(int(record.get("oxidant_dose_count", 0)) for record in records)
        last_lifetime = float(records[-1].get("catalyst_lifetime_fraction_end", 1.0)) if records else 1.0
        last_activity = float(records[-1].get("catalyst_activity_end", 1.0)) if records else 1.0
        validation_hours = validation_minutes / 60.0
        validation_staff_usage = validation_hours / max(self.validation_staff_hours_capacity, 1e-9)
        time_budget_usage = total_elapsed / max(float(self.campaign_time_budget_min), 1e-9)
        return {
            "batch_count": batch_count,
            "success_rate": round(successes / batch_count, 3) if batch_count else 0.0,
            "total_elapsed_min": round(total_elapsed, 1),
            "mean_elapsed_min": round(total_elapsed / batch_count, 1) if batch_count else 0.0,
            "total_cost": round(total_cost, 3),
            "total_energy": round(total_energy, 3),
            "validation_hours": round(validation_hours, 3),
            "validation_staff_usage": round(validation_staff_usage, 3),
            "time_budget_usage": round(time_budget_usage, 3),
            "regeneration_count": regeneration_count,
            "replacement_count": replacement_count,
            "oxidant_dose_count": oxidant_dose_count,
            "catalyst_lifetime_fraction_end": round(last_lifetime, 3),
            "catalyst_activity_end": round(last_activity, 3),
            "catalyst_spares_remaining": self.catalyst_spares_remaining,
            "oxidant_stock_units_remaining": round(self.oxidant_stock_units_remaining, 3),
            "evidence_strength": min(1.0, batch_count / 6.0),
        }

    def _bottlenecks(self, metrics: dict[str, float | int]) -> list[dict[str, object]]:
        bottlenecks: list[dict[str, object]] = []
        if float(metrics["success_rate"]) < 0.95:
            bottlenecks.append(
                {
                    "bottleneck_id": "release_reliability",
                    "severity": "critical",
                    "message": "多批次放行成功率不足，暂停扩大进水负荷。",
                    "value": metrics["success_rate"],
                    "threshold": 0.95,
                }
            )
        if float(metrics["validation_staff_usage"]) >= 0.90:
            bottlenecks.append(
                {
                    "bottleneck_id": "validation_capacity",
                    "severity": "critical" if float(metrics["validation_staff_usage"]) >= 1.10 else "warning",
                    "message": "旁路/离线验证工时接近或超过可用容量。",
                    "value": metrics["validation_staff_usage"],
                    "threshold": 0.90,
                }
            )
        if float(metrics["time_budget_usage"]) >= 0.90:
            bottlenecks.append(
                {
                    "bottleneck_id": "campaign_time_budget",
                    "severity": "warning",
                    "message": "循环、验证和维护占用的总时间接近运行窗口上限。",
                    "value": metrics["time_budget_usage"],
                    "threshold": 0.90,
                }
            )
        if int(metrics["catalyst_spares_remaining"]) <= 0:
            bottlenecks.append(
                {
                    "bottleneck_id": "catalyst_inventory",
                    "severity": "critical",
                    "message": "催化剂备件已耗尽，禁止依赖更换动作作为默认兜底。",
                    "value": metrics["catalyst_spares_remaining"],
                    "threshold": 1,
                }
            )
        elif int(metrics["catalyst_spares_remaining"]) == 1 and float(metrics["catalyst_lifetime_fraction_end"]) <= 0.45:
            bottlenecks.append(
                {
                    "bottleneck_id": "catalyst_inventory",
                    "severity": "warning",
                    "message": "催化剂寿命偏低且仅剩一个备件，应提前补库。",
                    "value": metrics["catalyst_spares_remaining"],
                    "threshold": 2,
                }
            )
        if float(metrics["oxidant_stock_units_remaining"]) <= 0.7:
            bottlenecks.append(
                {
                    "bottleneck_id": "oxidant_stock",
                    "severity": "warning",
                    "message": "氧化剂库存接近下限，后续补加药剂动作可能受限。",
                    "value": metrics["oxidant_stock_units_remaining"],
                    "threshold": 0.7,
                }
            )
        return bottlenecks

    def _schedule(
        self,
        metrics: dict[str, float | int],
        bottlenecks: list[dict[str, object]],
    ) -> dict[str, object]:
        bottleneck_ids = {str(item["bottleneck_id"]) for item in bottlenecks}
        action_queue: list[dict[str, object]] = []
        operating_mode = "normal_intake"

        if "release_reliability" in bottleneck_ids or "catalyst_inventory" in bottleneck_ids:
            operating_mode = "pause_or_limit_intake"
            action_queue.append(
                {
                    "action_id": "limit_intake",
                    "instruction": "限制新批次进水，优先消化待验证批次和维护风险。",
                    "priority": 1,
                }
            )
        elif "validation_capacity" in bottleneck_ids or "campaign_time_budget" in bottleneck_ids:
            operating_mode = "staggered_intake"
            action_queue.append(
                {
                    "action_id": "stagger_batches",
                    "instruction": "错峰安排进水和旁路验证，避免慢证据排队压垮闭环节奏。",
                    "priority": 1,
                }
            )

        if "validation_capacity" in bottleneck_ids:
            action_queue.append(
                {
                    "action_id": "reserve_validation_shift",
                    "instruction": "增加旁路快检班次或压缩低价值验证项，优先保障放行门和副产物验证。",
                    "priority": 2,
                }
            )
        if "catalyst_inventory" in bottleneck_ids:
            action_queue.append(
                {
                    "action_id": "reorder_catalyst_modules",
                    "instruction": "补充催化剂模块库存，并把寿命低于 0.45 的批次列入预防性维护。",
                    "priority": 2,
                }
            )
        if "oxidant_stock" in bottleneck_ids:
            action_queue.append(
                {
                    "action_id": "replenish_oxidant",
                    "instruction": "补充氧化剂库存，同时复核高加药场景的副产物验证计划。",
                    "priority": 3,
                }
            )
        if float(metrics["catalyst_lifetime_fraction_end"]) <= 0.38 and "catalyst_inventory" not in bottleneck_ids:
            action_queue.append(
                {
                    "action_id": "schedule_preventive_catalyst_service",
                    "instruction": "安排下一批前催化剂活性检查，必要时预防性再生，避免运行中触发更换。",
                    "priority": 3,
                }
            )

        action_queue.sort(key=lambda item: int(item["priority"]))
        return {
            "operating_mode": operating_mode,
            "action_queue": action_queue,
            "next_campaign_review_after_batches": max(1, min(3, int(metrics["batch_count"]) // 2 or 1)),
        }

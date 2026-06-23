from __future__ import annotations

from collections.abc import Sequence

from water_ai.agents.base import BaseAgent
from water_ai.agents.operations_scheduling_agent import OperationsSchedulingAgent
from water_ai.domain import AgentReport, QualityIssue, SensorReading, Severity


class CampaignTelemetryAgent(BaseAgent):
    """Convert real campaign operation records into online project-control updates."""

    name = "campaign_telemetry_agent"

    def __init__(
        self,
        *,
        batch_records: list[dict[str, object]] | None = None,
        update_cut_points: list[int] | None = None,
        initial_catalyst_spares: int = 1,
        initial_oxidant_stock_units: float = 2.2,
        validation_staff_hours_capacity: float = 5.5,
        campaign_time_budget_min: int = 960,
        budget_release_plan: dict[int, dict[str, object]] | None = None,
        planned_ready_campaign: int = 2,
    ) -> None:
        self.batch_records = batch_records or []
        self.update_cut_points = update_cut_points or self._default_cut_points(len(self.batch_records))
        self.initial_catalyst_spares = initial_catalyst_spares
        self.initial_oxidant_stock_units = initial_oxidant_stock_units
        self.validation_staff_hours_capacity = validation_staff_hours_capacity
        self.campaign_time_budget_min = campaign_time_budget_min
        self.budget_release_plan = budget_release_plan or {}
        self.planned_ready_campaign = planned_ready_campaign

    def run(self, readings: Sequence[SensorReading]) -> AgentReport:
        del readings
        updates = [self._build_update(index, cut_point) for index, cut_point in enumerate(self.update_cut_points)]
        latest = updates[-1] if updates else {}
        issues = self._issues(updates)
        recommendations = self._recommendations(latest)
        summary = (
            f"campaign 遥测桥接：生成 {len(updates)} 个滚动更新，最新 success_rate "
            f"{latest.get('success_rate', 0.0)}，验证占用 {latest.get('validation_staff_usage', 0.0)}。"
            if updates
            else "campaign 遥测桥接：没有批次记录可转换。"
        )
        confidence = round(min(0.95, max(0.15, 0.42 + 0.08 * len(updates) - 0.05 * len(issues))), 3)

        return AgentReport(
            agent_name=self.name,
            confidence=confidence,
            summary=summary,
            issues=issues,
            recommendations=recommendations,
            metrics={
                "rolling_campaign_updates": updates,
                "latest_update": latest,
                "update_cut_points": self.update_cut_points,
            },
        )

    def _build_update(self, campaign_id: int, cut_point: int) -> dict[str, object]:
        prefix = self.batch_records[:cut_point]
        catalyst_spares = self._catalyst_spares_remaining(prefix)
        oxidant_stock = self._oxidant_stock_remaining(prefix)
        operations = OperationsSchedulingAgent(
            batch_records=prefix,
            catalyst_spares_remaining=catalyst_spares,
            oxidant_stock_units_remaining=oxidant_stock,
            validation_staff_hours_capacity=self.validation_staff_hours_capacity,
            campaign_time_budget_min=self.campaign_time_budget_min,
        ).run([])
        metrics = operations.metrics["campaign_metrics"]
        bottlenecks = operations.metrics["bottlenecks"]
        budget = self._budget_release(campaign_id)
        acceptance_passed = self._acceptance_passed(metrics, bottlenecks)
        return {
            "campaign_id": campaign_id,
            "cut_point_batch_count": cut_point,
            "acceptance_passed": acceptance_passed,
            "success_rate": metrics["success_rate"],
            "validation_staff_usage": metrics["validation_staff_usage"],
            "time_budget_usage": metrics["time_budget_usage"],
            "catalyst_spares_remaining": metrics["catalyst_spares_remaining"],
            "oxidant_stock_units_remaining": metrics["oxidant_stock_units_remaining"],
            "intake_pressure_multiplier": self._intake_pressure(prefix, bottlenecks),
            "budget_release_fraction": budget["budget_release_fraction"],
            "budget_released_items": budget["budget_released_items"],
            "ready_campaign_slip": self._ready_campaign_slip(campaign_id, bottlenecks),
            "bottleneck_ids": [str(item.get("bottleneck_id", "")) for item in bottlenecks],
            "operating_mode": operations.metrics["schedule"]["operating_mode"],
            "source_scenarios": [str(record.get("scenario", "")) for record in prefix],
        }

    def _catalyst_spares_remaining(self, records: list[dict[str, object]]) -> int:
        replacements = sum(int(record.get("replacement_count", 0)) for record in records)
        return self.initial_catalyst_spares - replacements

    def _oxidant_stock_remaining(self, records: list[dict[str, object]]) -> float:
        oxidant_doses = sum(int(record.get("oxidant_dose_count", 0)) for record in records)
        return round(self.initial_oxidant_stock_units - 0.35 * oxidant_doses, 3)

    def _budget_release(self, campaign_id: int) -> dict[str, object]:
        payload = self.budget_release_plan.get(campaign_id, {})
        items = payload.get("budget_released_items", []) if isinstance(payload, dict) else []
        fraction = payload.get("budget_release_fraction", 1.0) if isinstance(payload, dict) else 1.0
        return {
            "budget_released_items": list(items) if isinstance(items, list) else [],
            "budget_release_fraction": round(float(fraction), 3),
        }

    @staticmethod
    def _acceptance_passed(metrics: dict[str, object], bottlenecks: list[dict[str, object]]) -> bool:
        critical_ids = {
            str(item.get("bottleneck_id", ""))
            for item in bottlenecks
            if str(item.get("severity", "")) == "critical"
        }
        if "release_reliability" in critical_ids:
            return False
        return float(metrics.get("success_rate", 0.0)) >= 0.95

    @staticmethod
    def _intake_pressure(records: list[dict[str, object]], bottlenecks: list[dict[str, object]]) -> float:
        if not records:
            return 1.0
        high_risk = sum(
            1
            for record in records
            if str(record.get("scenario", "")) in {"matrix_shock", "catalyst_deactivation", "oxidant_limitation"}
        )
        bottleneck_bonus = 0.05 * len(bottlenecks)
        return round(1.0 + 0.25 * high_risk / len(records) + bottleneck_bonus, 3)

    def _ready_campaign_slip(self, campaign_id: int, bottlenecks: list[dict[str, object]]) -> int:
        if campaign_id <= self.planned_ready_campaign:
            return 0
        critical_count = sum(1 for item in bottlenecks if str(item.get("severity", "")) == "critical")
        return critical_count

    @staticmethod
    def _issues(updates: list[dict[str, object]]) -> list[QualityIssue]:
        if not updates:
            return [
                QualityIssue(
                    sensor="campaign_telemetry",
                    issue_type="empty_campaign_records",
                    severity=Severity.WARNING,
                    message="没有批次记录，无法生成在线项目控制输入。",
                )
            ]
        latest = updates[-1]
        if not bool(latest.get("acceptance_passed", True)):
            return [
                QualityIssue(
                    sensor="campaign_telemetry",
                    issue_type="latest_acceptance_failed",
                    severity=Severity.WARNING,
                    message="最新 campaign 遥测未通过验收，应触发在线项目控制降负荷或重规划。",
                    evidence={"latest_update": latest},
                )
            ]
        return []

    @staticmethod
    def _recommendations(latest: dict[str, object]) -> list[str]:
        if not latest:
            return ["先运行多批次 campaign 仿真或导入现场批次记录。"]
        return [
            "将 rolling_campaign_updates 直接输入 OnlineProjectControlAgent，替代手工构造的项目状态。",
            f"最新滚动更新的主瓶颈为 {latest.get('bottleneck_ids', [])}，运行模式为 {latest.get('operating_mode', 'unknown')}。",
        ]

    @staticmethod
    def _default_cut_points(record_count: int) -> list[int]:
        if record_count <= 0:
            return []
        if record_count <= 3:
            return list(range(1, record_count + 1))
        points = sorted({max(1, record_count // 3), max(2, 2 * record_count // 3), record_count})
        return points

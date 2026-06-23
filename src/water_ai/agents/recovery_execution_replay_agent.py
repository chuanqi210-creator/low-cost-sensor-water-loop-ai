from __future__ import annotations

from collections.abc import Sequence
from copy import deepcopy
from math import ceil

from water_ai.agents.base import BaseAgent
from water_ai.agents.operations_scheduling_agent import OperationsSchedulingAgent
from water_ai.domain import AgentReport, QualityIssue, SensorReading, Severity


class RecoveryExecutionReplayAgent(BaseAgent):
    """Replay the written-back recovery strategy as the next executable campaign envelope."""

    name = "recovery_execution_replay_agent"

    def __init__(
        self,
        *,
        source_records: list[dict[str, object]] | None = None,
        recovery_baseline: dict[str, object] | None = None,
        catalyst_spares_remaining: int = 0,
        oxidant_stock_units_remaining: float = 0.0,
        validation_staff_hours_capacity: float = 5.5,
        campaign_time_budget_min: int = 960,
    ) -> None:
        self.source_records = source_records or []
        self.recovery_baseline = recovery_baseline or {}
        self.catalyst_spares_remaining = catalyst_spares_remaining
        self.oxidant_stock_units_remaining = oxidant_stock_units_remaining
        self.validation_staff_hours_capacity = validation_staff_hours_capacity
        self.campaign_time_budget_min = campaign_time_budget_min

    def run(self, readings: Sequence[SensorReading]) -> AgentReport:
        del readings
        no_overlap = self._projection(apply_recovery_policy=False)
        with_strategy = self._projection(apply_recovery_policy=True)
        comparison = self._comparison(no_overlap, with_strategy)
        issues = self._issues(comparison)
        recommendations = self._recommendations(comparison)
        summary = (
            f"恢复执行回放：{comparison['replay_verdict']}；时间占用 "
            f"{comparison['time_usage_without_strategy']} -> {comparison['time_usage_with_strategy']}，"
            f"建议下一轮进水 {comparison['recommended_next_intake_fraction']}。"
        )
        confidence = round(min(0.95, max(0.18, 0.48 + 0.18 * float(comparison["strategy_stable"]) - 0.05 * len(issues))), 3)

        return AgentReport(
            agent_name=self.name,
            confidence=confidence,
            summary=summary,
            issues=issues,
            recommendations=recommendations,
            metrics={
                "without_recovery_strategy": no_overlap,
                "with_recovery_strategy": with_strategy,
                "comparison": comparison,
            },
        )

    def _projection(self, *, apply_recovery_policy: bool) -> dict[str, object]:
        policy = self._recovery_policy()
        target_fraction = self._target_fraction(policy)
        records = self._select_records(target_fraction, str(policy.get("queue_policy", "source_order")))
        elapsed_reduction = 0.0
        if apply_recovery_policy and policy.get("selected_candidate_id") == "stagger_validation_overlap":
            records, elapsed_reduction = self._apply_validation_overlap(records, policy)
        records = self._apply_validation_multiplier(records)
        operations = self._operations_report(records)
        campaign_metrics = operations["campaign_metrics"]
        bottleneck_ids = [str(item.get("bottleneck_id", "")) for item in operations["bottlenecks"]]
        return {
            "apply_recovery_policy": apply_recovery_policy,
            "baseline_version": self.recovery_baseline.get("baseline_version", "unknown"),
            "selected_candidate_id": policy.get("selected_candidate_id", "none"),
            "target_intake_fraction": round(target_fraction, 3),
            "fallback_intake_fraction": round(float(policy.get("fallback_intake_fraction", target_fraction)), 3),
            "actual_throughput_fraction": round(len(records) / max(len(self.source_records), 1), 3),
            "admitted_batch_count": len(records),
            "elapsed_reduction_min": round(elapsed_reduction, 1),
            "campaign_metrics": campaign_metrics,
            "bottleneck_ids": bottleneck_ids,
            "schedule": operations["schedule"],
            "scenario_sequence": [str(record.get("scenario", "unknown")) for record in records],
        }

    def _select_records(self, intake_fraction: float, queue_policy: str) -> list[dict[str, object]]:
        source_count = len(self.source_records)
        admitted_count = max(1, min(source_count, ceil(source_count * intake_fraction))) if source_count else 0
        records = deepcopy(self.source_records)
        if queue_policy == "short_elapsed_first":
            records.sort(key=lambda record: float(record.get("elapsed_min", 0.0)))
        return records[:admitted_count]

    @staticmethod
    def _apply_validation_overlap(
        records: list[dict[str, object]],
        recovery_policy: dict[str, object],
    ) -> tuple[list[dict[str, object]], float]:
        adjusted = deepcopy(records)
        rule = recovery_policy.get("validation_overlap_rule", {})
        if not isinstance(rule, dict):
            rule = {}
        fraction = float(rule.get("overlap_fraction_of_validation_minutes", 0.35))
        max_per_batch = float(rule.get("max_overlap_min_per_batch", 30.0))
        total_reduction = 0.0
        for record in adjusted:
            validation_minutes = float(record.get("validation_minutes", 0.0))
            if validation_minutes <= 0:
                continue
            reduction = min(max_per_batch, max(0.0, fraction * validation_minutes))
            record["elapsed_min"] = round(max(0.0, float(record.get("elapsed_min", 0.0)) - reduction), 1)
            total_reduction += reduction
        return adjusted, total_reduction

    def _apply_validation_multiplier(self, records: list[dict[str, object]]) -> list[dict[str, object]]:
        adjusted = deepcopy(records)
        multiplier = self._validation_minutes_multiplier()
        if multiplier == 1.0:
            return adjusted
        for record in adjusted:
            record["validation_minutes"] = round(float(record.get("validation_minutes", 0.0)) * multiplier, 1)
        return adjusted

    def _operations_report(self, records: list[dict[str, object]]) -> dict[str, object]:
        resources = self._resource_projection()
        report = OperationsSchedulingAgent(
            batch_records=records,
            catalyst_spares_remaining=int(resources["catalyst_spares_projected"]),
            oxidant_stock_units_remaining=float(resources["oxidant_stock_projected"]),
            validation_staff_hours_capacity=float(resources["validation_staff_hours_projected"]),
            campaign_time_budget_min=self.campaign_time_budget_min,
        ).run([])
        return {
            "campaign_metrics": report.metrics["campaign_metrics"],
            "bottlenecks": report.metrics["bottlenecks"],
            "schedule": report.metrics["schedule"],
        }

    def _comparison(self, no_overlap: dict[str, object], with_strategy: dict[str, object]) -> dict[str, object]:
        no_metrics = no_overlap["campaign_metrics"]
        strategy_metrics = with_strategy["campaign_metrics"]
        strategy_bottlenecks = list(with_strategy["bottleneck_ids"])
        fallback_required = bool(strategy_bottlenecks) or float(strategy_metrics["time_budget_usage"]) >= 0.90 or float(strategy_metrics["validation_staff_usage"]) >= 0.90
        strategy_stable = not fallback_required and float(strategy_metrics["success_rate"]) >= 0.95
        expected_time = self._expected_time_usage()
        time_delta_from_expected = (
            round(float(strategy_metrics["time_budget_usage"]) - expected_time, 3)
            if expected_time is not None
            else None
        )
        if strategy_stable:
            verdict = "recovery_execution_validated"
        elif float(no_metrics["time_budget_usage"]) >= 0.90 and not strategy_bottlenecks:
            verdict = "recovery_needs_monitoring"
        else:
            verdict = "fallback_required"
        return {
            "replay_verdict": verdict,
            "strategy_stable": strategy_stable,
            "fallback_required": fallback_required,
            "target_intake_fraction": with_strategy["target_intake_fraction"],
            "fallback_intake_fraction": with_strategy["fallback_intake_fraction"],
            "recommended_next_intake_fraction": with_strategy["target_intake_fraction"] if strategy_stable else with_strategy["fallback_intake_fraction"],
            "time_usage_without_strategy": no_metrics["time_budget_usage"],
            "time_usage_with_strategy": strategy_metrics["time_budget_usage"],
            "time_usage_reduction": round(float(no_metrics["time_budget_usage"]) - float(strategy_metrics["time_budget_usage"]), 3),
            "validation_usage_without_strategy": no_metrics["validation_staff_usage"],
            "validation_usage_with_strategy": strategy_metrics["validation_staff_usage"],
            "strategy_bottleneck_ids": strategy_bottlenecks,
            "without_strategy_bottleneck_ids": no_overlap["bottleneck_ids"],
            "elapsed_reduction_min": with_strategy["elapsed_reduction_min"],
            "expected_time_budget_usage": expected_time,
            "time_usage_delta_from_expected": time_delta_from_expected,
            "actual_throughput_fraction": with_strategy["actual_throughput_fraction"],
            "admitted_batch_count": with_strategy["admitted_batch_count"],
        }

    def _recovery_policy(self) -> dict[str, object]:
        config = self.recovery_baseline.get("online_control_config", self.recovery_baseline)
        if not isinstance(config, dict):
            return {}
        policy = config.get("recovery_control_policy", {})
        return policy if isinstance(policy, dict) else {}

    def _target_fraction(self, policy: dict[str, object]) -> float:
        if policy.get("enabled"):
            return max(0.1, min(1.0, float(policy.get("target_intake_fraction", 1.0))))
        config = self.recovery_baseline.get("online_control_config", self.recovery_baseline)
        load_policy = config.get("load_control_policy", {}) if isinstance(config, dict) else {}
        if isinstance(load_policy, dict):
            return max(0.1, min(1.0, float(load_policy.get("protected_intake_fraction", 1.0))))
        return 1.0

    def _budget_items(self) -> list[str]:
        config = self.recovery_baseline.get("online_control_config", self.recovery_baseline)
        sequence = config.get("budget_sequence", []) if isinstance(config, dict) else []
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
        return {
            "validation_staff_hours_projected": round(self.validation_staff_hours_capacity + validation_hours_delta, 3),
            "catalyst_spares_projected": self.catalyst_spares_remaining + catalyst_spares_delta,
            "oxidant_stock_projected": round(self.oxidant_stock_units_remaining + oxidant_stock_delta, 3),
        }

    def _validation_minutes_multiplier(self) -> float:
        return 0.78 if "外包低价值验证" in self._budget_items() else 1.0

    def _expected_time_usage(self) -> float | None:
        policy = self._recovery_policy()
        value = policy.get("expected_time_budget_usage")
        return round(float(value), 3) if value is not None else None

    @staticmethod
    def _issues(comparison: dict[str, object]) -> list[QualityIssue]:
        if not comparison["fallback_required"]:
            return []
        return [
            QualityIssue(
                sensor="recovery_execution_replay",
                issue_type="recovery_fallback_triggered",
                severity=Severity.WARNING,
                message="恢复策略执行回放触发回退门槛，下一轮不能维持目标进水比例。",
                evidence={
                    "strategy_bottleneck_ids": comparison["strategy_bottleneck_ids"],
                    "time_usage_with_strategy": comparison["time_usage_with_strategy"],
                    "validation_usage_with_strategy": comparison["validation_usage_with_strategy"],
                    "fallback_intake_fraction": comparison["fallback_intake_fraction"],
                },
            )
        ]

    @staticmethod
    def _recommendations(comparison: dict[str, object]) -> list[str]:
        if comparison["strategy_stable"]:
            return [
                f"执行恢复策略后可维持目标进水 {comparison['target_intake_fraction']}，但 campaign 后继续运行遥测桥接、回放和爬坡复核。",
                "保留 fallback_intake_fraction，不把 0.75 视为永久满负荷基线。",
            ]
        return [
            f"恢复策略触发回退，下一轮进水降至 {comparison['fallback_intake_fraction']}。",
            "重新运行时间预算恢复方案选择，并检查验证错峰是否被真实执行。",
        ]

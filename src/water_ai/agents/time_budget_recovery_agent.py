from __future__ import annotations

from collections.abc import Sequence
from copy import deepcopy
from math import ceil

from water_ai.agents.base import BaseAgent
from water_ai.agents.operations_scheduling_agent import OperationsSchedulingAgent
from water_ai.domain import AgentReport, QualityIssue, SensorReading, Severity


class TimeBudgetRecoveryAgent(BaseAgent):
    """Compare concrete ways to remove the campaign-time bottleneck found during ramp-up."""

    name = "time_budget_recovery_agent"

    def __init__(
        self,
        *,
        source_records: list[dict[str, object]] | None = None,
        recovery_ramp_metrics: dict[str, object] | None = None,
        online_control_config: dict[str, object] | None = None,
        catalyst_spares_remaining: int = 0,
        oxidant_stock_units_remaining: float = 0.0,
        validation_staff_hours_capacity: float = 5.5,
        campaign_time_budget_min: int = 960,
        target_intake_fraction: float | None = None,
    ) -> None:
        self.source_records = source_records or []
        self.recovery_ramp_metrics = recovery_ramp_metrics or {}
        self.online_control_config = online_control_config or {}
        self.catalyst_spares_remaining = catalyst_spares_remaining
        self.oxidant_stock_units_remaining = oxidant_stock_units_remaining
        self.validation_staff_hours_capacity = validation_staff_hours_capacity
        self.campaign_time_budget_min = campaign_time_budget_min
        self.target_intake_fraction = target_intake_fraction if target_intake_fraction is not None else self._target_fraction()

    def run(self, readings: Sequence[SensorReading]) -> AgentReport:
        del readings
        candidates = self._candidate_results()
        selected = self._select_candidate(candidates)
        verdict = self._verdict(selected)
        issues = self._issues(selected)
        recommendations = self._recommendations(selected)
        summary = (
            f"时间预算恢复：{verdict}；推荐 {selected['candidate_id']}，"
            f"目标进水 {selected['target_intake_fraction']}，时间占用 {selected['time_budget_usage']}。"
        )
        confidence = round(min(0.95, max(0.2, 0.48 + 0.14 * float(selected["stable"]) - 0.05 * len(issues) + 0.04 * len(candidates))), 3)

        return AgentReport(
            agent_name=self.name,
            confidence=confidence,
            summary=summary,
            issues=issues,
            recommendations=recommendations,
            metrics={
                "strategy_verdict": verdict,
                "target_intake_fraction": round(self.target_intake_fraction, 3),
                "safe_intake_fraction": round(self._safe_fraction(), 3),
                "selected_candidate": selected,
                "candidate_results": candidates,
                "limiting_bottlenecks_from_ramp": self.recovery_ramp_metrics.get("limiting_bottlenecks", []),
            },
        )

    def _candidate_results(self) -> list[dict[str, object]]:
        return [
            self._evaluate_candidate(
                candidate_id="hold_safe_fraction",
                description="维持 Agent24 给出的安全恢复上限，不尝试更高负荷。",
                intake_fraction=self._safe_fraction(),
                queue_policy="source_order",
                cost_index=0.10,
                disruption_index=0.05,
            ),
            self._evaluate_candidate(
                candidate_id="extend_campaign_window_120min",
                description="将目标恢复比例保持在 0.75 左右，但额外释放 120 min campaign 时间窗口。",
                intake_fraction=self.target_intake_fraction,
                added_campaign_window_min=120,
                queue_policy="source_order",
                cost_index=0.55,
                disruption_index=0.18,
            ),
            self._evaluate_candidate(
                candidate_id="stagger_validation_overlap",
                description="保持原队列顺序，把旁路验证、暂存和回流观察部分并行错峰，压缩长验证批次的占用时间。",
                intake_fraction=self.target_intake_fraction,
                elapsed_overlap=True,
                queue_policy="source_order",
                cost_index=0.35,
                disruption_index=0.20,
            ),
            self._evaluate_candidate(
                candidate_id="time_smoothed_queue",
                description="在目标恢复比例下优先接纳短耗时批次，暂缓最长耗时批次，换取时间预算余量。",
                intake_fraction=self.target_intake_fraction,
                queue_policy="short_elapsed_first",
                cost_index=0.25,
                disruption_index=0.45,
            ),
            self._evaluate_candidate(
                candidate_id="hybrid_overlap_plus_60min",
                description="同时采用验证错峰和 60 min 时间窗口释放，作为恢复到目标比例的稳健方案。",
                intake_fraction=self.target_intake_fraction,
                added_campaign_window_min=60,
                elapsed_overlap=True,
                queue_policy="source_order",
                cost_index=0.65,
                disruption_index=0.30,
            ),
        ]

    def _evaluate_candidate(
        self,
        *,
        candidate_id: str,
        description: str,
        intake_fraction: float,
        added_campaign_window_min: int = 0,
        elapsed_overlap: bool = False,
        queue_policy: str,
        cost_index: float,
        disruption_index: float,
    ) -> dict[str, object]:
        records = self._select_records(intake_fraction, queue_policy)
        if elapsed_overlap:
            records, elapsed_reduction = self._apply_validation_overlap(records)
        else:
            elapsed_reduction = 0.0
        records = self._apply_validation_multiplier(records)
        operations = self._operations_report(
            records=records,
            campaign_time_budget_min=self.campaign_time_budget_min + added_campaign_window_min,
        )
        metrics = operations["campaign_metrics"]
        bottleneck_ids = [str(item.get("bottleneck_id", "")) for item in operations["bottlenecks"]]
        stable = (
            not bottleneck_ids
            and float(metrics.get("success_rate", 0.0)) >= 0.95
            and float(metrics.get("validation_staff_usage", 1.0)) < 0.90
            and float(metrics.get("time_budget_usage", 1.0)) < 0.90
        )
        throughput_fraction = round(len(records) / max(len(self.source_records), 1), 3)
        target_recovery = round(intake_fraction, 3) >= round(self.target_intake_fraction, 3)
        score = self._score_candidate(
            stable=stable,
            target_recovery=target_recovery,
            throughput_fraction=throughput_fraction,
            time_budget_usage=float(metrics["time_budget_usage"]),
            validation_staff_usage=float(metrics["validation_staff_usage"]),
            cost_index=cost_index,
            disruption_index=disruption_index,
        )
        return {
            "candidate_id": candidate_id,
            "description": description,
            "target_intake_fraction": round(intake_fraction, 3),
            "actual_throughput_fraction": throughput_fraction,
            "admitted_batch_count": len(records),
            "added_campaign_window_min": added_campaign_window_min,
            "elapsed_reduction_min": round(elapsed_reduction, 1),
            "queue_policy": queue_policy,
            "cost_index": round(cost_index, 3),
            "disruption_index": round(disruption_index, 3),
            "stable": stable,
            "target_recovery": target_recovery,
            "candidate_score": score,
            "bottleneck_ids": bottleneck_ids,
            "success_rate": metrics["success_rate"],
            "validation_staff_usage": metrics["validation_staff_usage"],
            "time_budget_usage": metrics["time_budget_usage"],
            "total_elapsed_min": metrics["total_elapsed_min"],
            "operating_mode": operations["schedule"]["operating_mode"],
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
    def _apply_validation_overlap(records: list[dict[str, object]]) -> tuple[list[dict[str, object]], float]:
        adjusted = deepcopy(records)
        total_reduction = 0.0
        for record in adjusted:
            validation_minutes = float(record.get("validation_minutes", 0.0))
            if validation_minutes <= 0:
                continue
            reduction = min(30.0, 0.35 * validation_minutes)
            elapsed = float(record.get("elapsed_min", 0.0))
            record["elapsed_min"] = round(max(0.0, elapsed - reduction), 1)
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

    def _operations_report(self, *, records: list[dict[str, object]], campaign_time_budget_min: int) -> dict[str, object]:
        resources = self._resource_projection()
        report = OperationsSchedulingAgent(
            batch_records=records,
            catalyst_spares_remaining=int(resources["catalyst_spares_projected"]),
            oxidant_stock_units_remaining=float(resources["oxidant_stock_projected"]),
            validation_staff_hours_capacity=float(resources["validation_staff_hours_projected"]),
            campaign_time_budget_min=campaign_time_budget_min,
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
        return {
            "validation_staff_hours_projected": round(self.validation_staff_hours_capacity + validation_hours_delta, 3),
            "catalyst_spares_projected": self.catalyst_spares_remaining + catalyst_spares_delta,
            "oxidant_stock_projected": round(self.oxidant_stock_units_remaining + oxidant_stock_delta, 3),
        }

    def _validation_minutes_multiplier(self) -> float:
        return 0.78 if "外包低价值验证" in self._budget_items() else 1.0

    def _target_fraction(self) -> float:
        limiting_fraction = self.recovery_ramp_metrics.get("limiting_attempted_fraction")
        if limiting_fraction is not None:
            return max(0.1, min(1.0, float(limiting_fraction)))
        safe = self._safe_fraction()
        step = float(self.recovery_ramp_metrics.get("ramp_step", 0.15))
        return max(0.1, min(1.0, safe + step))

    def _safe_fraction(self) -> float:
        return max(0.1, min(1.0, float(self.recovery_ramp_metrics.get("final_safe_intake_fraction", 0.45))))

    @staticmethod
    def _score_candidate(
        *,
        stable: bool,
        target_recovery: bool,
        throughput_fraction: float,
        time_budget_usage: float,
        validation_staff_usage: float,
        cost_index: float,
        disruption_index: float,
    ) -> float:
        time_headroom = max(0.0, 1.0 - min(time_budget_usage, 1.0))
        validation_headroom = max(0.0, 1.0 - min(validation_staff_usage, 1.0))
        score = (
            0.34 * float(stable)
            + 0.18 * float(target_recovery)
            + 0.16 * throughput_fraction
            + 0.12 * time_headroom
            + 0.08 * validation_headroom
            + 0.07 * (1.0 - min(cost_index, 1.0))
            + 0.05 * (1.0 - min(disruption_index, 1.0))
        )
        return round(score, 3)

    @staticmethod
    def _select_candidate(candidates: list[dict[str, object]]) -> dict[str, object]:
        stable_target = [item for item in candidates if item["stable"] and item["target_recovery"]]
        if stable_target:
            source_order_target = [item for item in stable_target if item["queue_policy"] == "source_order"]
            if source_order_target:
                return max(source_order_target, key=lambda item: float(item["candidate_score"]))
            return max(stable_target, key=lambda item: float(item["candidate_score"]))
        stable_any = [item for item in candidates if item["stable"]]
        if stable_any:
            return max(stable_any, key=lambda item: float(item["candidate_score"]))
        return max(candidates, key=lambda item: float(item["candidate_score"]))

    @staticmethod
    def _verdict(selected: dict[str, object]) -> str:
        if selected["stable"] and selected["target_recovery"]:
            return "target_recovery_feasible"
        if selected["stable"]:
            return "hold_safe_fraction"
        return "time_budget_unresolved"

    @staticmethod
    def _issues(selected: dict[str, object]) -> list[QualityIssue]:
        issues: list[QualityIssue] = []
        if not selected["stable"]:
            issues.append(
                QualityIssue(
                    sensor="time_budget_recovery",
                    issue_type="time_budget_unresolved",
                    severity=Severity.CRITICAL,
                    message="候选时间预算恢复方案仍无法解除瓶颈，应保持保护性进水并重新规划资源。",
                    evidence={"selected_candidate": selected["candidate_id"], "bottleneck_ids": selected["bottleneck_ids"]},
                )
            )
        elif not selected["target_recovery"]:
            issues.append(
                QualityIssue(
                    sensor="time_budget_recovery",
                    issue_type="target_recovery_not_feasible",
                    severity=Severity.WARNING,
                    message="当前只能维持安全恢复上限，尚不能恢复到目标进水比例。",
                    evidence={"selected_candidate": selected["candidate_id"], "actual_throughput_fraction": selected["actual_throughput_fraction"]},
                )
            )
        if float(selected["disruption_index"]) >= 0.40:
            issues.append(
                QualityIssue(
                    sensor="time_budget_recovery",
                    issue_type="queue_disruption_tradeoff",
                    severity=Severity.INFO,
                    message="推荐方案依赖明显改变队列顺序，需要防止高风险批次被长期后移。",
                    evidence={"selected_candidate": selected["candidate_id"], "scenario_sequence": selected["scenario_sequence"]},
                )
            )
        return issues

    @staticmethod
    def _recommendations(selected: dict[str, object]) -> list[str]:
        recommendations = [
            f"采用 `{selected['candidate_id']}` 作为下一轮时间预算恢复方案，目标进水比例 {selected['target_intake_fraction']}，预计时间占用 {selected['time_budget_usage']}。",
        ]
        if selected["stable"] and selected["target_recovery"]:
            recommendations.append("可把恢复到目标比例作为有条件动作，但必须保留 campaign 后遥测回放和瓶颈复核。")
        elif selected["stable"]:
            recommendations.append("保持安全恢复上限，不继续放量；优先释放时间窗口或压缩长验证批次。")
        else:
            recommendations.append("时间预算瓶颈仍未解除，维持保护性限流并重新运行资源扩容链。")
        if selected["queue_policy"] == "short_elapsed_first":
            recommendations.append("若采用短耗时优先队列，需要设置最长等待批次上限，避免高风险或催化剂压力批次被反复后移。")
        return recommendations

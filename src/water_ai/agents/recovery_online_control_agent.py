from __future__ import annotations

from collections.abc import Sequence
from copy import deepcopy

from water_ai.agents.base import BaseAgent
from water_ai.agents.online_project_control_agent import OnlineProjectControlAgent
from water_ai.domain import AgentReport, QualityIssue, SensorReading, Severity


class RecoveryOnlineControlAgent(BaseAgent):
    """Feed recovery execution replay into online project control with explicit fallback rules."""

    name = "recovery_online_control_agent"

    def __init__(
        self,
        *,
        recovery_execution_metrics: dict[str, object] | None = None,
        recovery_baseline: dict[str, object] | None = None,
    ) -> None:
        self.recovery_execution_metrics = recovery_execution_metrics or {}
        self.recovery_baseline = recovery_baseline or {}

    def run(self, readings: Sequence[SensorReading]) -> AgentReport:
        del readings
        update = self._recovery_campaign_update()
        online_report = self._online_project_control(update)
        adjusted = self._adjusted_control_state(online_report.metrics["current_control_state"])
        issues = self._issues(adjusted)
        recommendations = self._recommendations(adjusted)
        summary = (
            f"恢复在线控制：{adjusted['recovery_control_mode']}；下一轮进水 "
            f"{adjusted['next_intake_fraction']}，重规划 {adjusted['replan_required']}。"
        )
        confidence = round(min(0.95, max(0.18, 0.52 + 0.18 * float(not adjusted["replan_required"]) - 0.05 * len(issues))), 3)

        return AgentReport(
            agent_name=self.name,
            confidence=confidence,
            summary=summary,
            issues=issues,
            recommendations=recommendations,
            metrics={
                "recovery_campaign_update": update,
                "online_project_control": online_report.metrics,
                "adjusted_control_state": adjusted,
            },
        )

    def _recovery_campaign_update(self) -> dict[str, object]:
        comparison = self._comparison()
        with_strategy = self._with_strategy()
        metrics = with_strategy.get("campaign_metrics", {})
        bottleneck_ids = list(comparison.get("strategy_bottleneck_ids", with_strategy.get("bottleneck_ids", [])))
        strategy_stable = bool(comparison.get("strategy_stable", False))
        fallback_required = bool(comparison.get("fallback_required", not strategy_stable))
        return {
            "campaign_id": "recovery_execution_replay",
            "cut_point_batch_count": with_strategy.get("admitted_batch_count", comparison.get("admitted_batch_count", 0)),
            "acceptance_passed": strategy_stable and not fallback_required,
            "success_rate": metrics.get("success_rate", 0.0),
            "validation_staff_usage": metrics.get("validation_staff_usage", comparison.get("validation_usage_with_strategy", 1.0)),
            "time_budget_usage": metrics.get("time_budget_usage", comparison.get("time_usage_with_strategy", 1.0)),
            "catalyst_spares_remaining": metrics.get("catalyst_spares_remaining", 0),
            "oxidant_stock_units_remaining": metrics.get("oxidant_stock_units_remaining", 0.0),
            "intake_pressure_multiplier": self._intake_pressure(fallback_required),
            "budget_release_fraction": 1.0,
            "budget_released_items": self._budget_items(),
            "ready_campaign_slip": 0 if strategy_stable else 1,
            "bottleneck_ids": bottleneck_ids,
            "operating_mode": with_strategy.get("schedule", {}).get("operating_mode", "unknown") if isinstance(with_strategy.get("schedule", {}), dict) else "unknown",
            "source_scenarios": with_strategy.get("scenario_sequence", []),
            "recovery_policy_applied": bool(with_strategy.get("apply_recovery_policy", False)),
            "recovery_replay_verdict": comparison.get("replay_verdict", "unknown"),
            "fallback_required": fallback_required,
            "target_intake_fraction": comparison.get("target_intake_fraction", self._recovery_policy().get("target_intake_fraction")),
            "fallback_intake_fraction": comparison.get("fallback_intake_fraction", self._recovery_policy().get("fallback_intake_fraction")),
        }

    def _online_project_control(self, update: dict[str, object]) -> AgentReport:
        config = self._online_config()
        return OnlineProjectControlAgent(
            selected_portfolio=self._dict_section(config, "selected_portfolio"),
            budget_sequence=self._list_section(config, "budget_sequence"),
            load_control_policy=self._dict_section(config, "load_control_policy"),
            rolling_campaigns=[update],
        ).run([])

    def _adjusted_control_state(self, online_state: dict[str, object]) -> dict[str, object]:
        comparison = self._comparison()
        recovery_policy = self._recovery_policy()
        fallback_required = bool(comparison.get("fallback_required", False))
        strategy_stable = bool(comparison.get("strategy_stable", False))
        target_fraction = round(float(comparison.get("target_intake_fraction", recovery_policy.get("target_intake_fraction", 0.75))), 3)
        fallback_fraction = round(float(comparison.get("fallback_intake_fraction", recovery_policy.get("fallback_intake_fraction", target_fraction))), 3)
        adjusted = deepcopy(online_state)
        adjusted["base_online_state"] = deepcopy(online_state)
        adjusted["recovery_policy_id"] = recovery_policy.get("policy_id", "unknown")
        adjusted["recovery_replay_verdict"] = comparison.get("replay_verdict", "unknown")
        adjusted["target_intake_fraction"] = target_fraction
        adjusted["fallback_intake_fraction"] = fallback_fraction
        adjusted["fallback_required"] = fallback_required
        adjusted["strategy_stable"] = strategy_stable
        if fallback_required or not strategy_stable:
            adjusted["recovery_control_mode"] = "fallback_to_safe_fraction"
            adjusted["next_intake_fraction"] = fallback_fraction
            adjusted["replan_required"] = True
            reasons = list(adjusted.get("replan_reasons", []))
            reasons.append("恢复执行回放触发 fallback trigger")
            adjusted["replan_reasons"] = list(dict.fromkeys(str(item) for item in reasons))
        else:
            adjusted["recovery_control_mode"] = "maintain_conditional_recovery"
            adjusted["next_intake_fraction"] = target_fraction
            adjusted["replan_required"] = False
            adjusted["replan_reasons"] = []
        return adjusted

    def _comparison(self) -> dict[str, object]:
        comparison = self.recovery_execution_metrics.get("comparison", {})
        return comparison if isinstance(comparison, dict) else {}

    def _with_strategy(self) -> dict[str, object]:
        payload = self.recovery_execution_metrics.get("with_recovery_strategy", {})
        return payload if isinstance(payload, dict) else {}

    def _online_config(self) -> dict[str, object]:
        config = self.recovery_baseline.get("online_control_config", self.recovery_baseline)
        return config if isinstance(config, dict) else {}

    def _recovery_policy(self) -> dict[str, object]:
        policy = self._online_config().get("recovery_control_policy", {})
        return policy if isinstance(policy, dict) else {}

    def _budget_items(self) -> list[str]:
        items: list[str] = []
        for entry in self._list_section(self._online_config(), "budget_sequence"):
            if isinstance(entry, dict) and entry.get("budget_item"):
                items.append(str(entry["budget_item"]))
        return items

    @staticmethod
    def _dict_section(config: dict[str, object], key: str) -> dict[str, object]:
        section = config.get(key, {})
        return deepcopy(section) if isinstance(section, dict) else {}

    @staticmethod
    def _list_section(config: dict[str, object], key: str) -> list[object]:
        section = config.get(key, [])
        return deepcopy(section) if isinstance(section, list) else []

    @staticmethod
    def _intake_pressure(fallback_required: bool) -> float:
        return 1.12 if fallback_required else 1.0

    @staticmethod
    def _issues(adjusted: dict[str, object]) -> list[QualityIssue]:
        if not adjusted.get("replan_required"):
            return []
        return [
            QualityIssue(
                sensor="recovery_online_control",
                issue_type="recovery_online_replan_required",
                severity=Severity.WARNING,
                message="恢复执行结果触发回退或重规划，不能维持目标进水比例。",
                evidence={"adjusted_control_state": adjusted},
            )
        ]

    @staticmethod
    def _recommendations(adjusted: dict[str, object]) -> list[str]:
        if adjusted.get("replan_required"):
            return [
                f"下一轮进水回退到 {adjusted['next_intake_fraction']}，并重新运行时间预算恢复方案选择。",
                "保留恢复策略遥测，检查是执行偏差、验证错峰失败还是新瓶颈导致回退。",
            ]
        return [
            f"维持条件恢复进水 {adjusted['next_intake_fraction']}，但继续保留 fallback_intake_fraction {adjusted['fallback_intake_fraction']}。",
            "下一 campaign 后继续运行遥测桥接、恢复执行回放和在线控制复核。",
        ]

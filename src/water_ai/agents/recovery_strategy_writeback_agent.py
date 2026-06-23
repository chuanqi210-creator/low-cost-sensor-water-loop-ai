from __future__ import annotations

from collections.abc import Sequence
from copy import deepcopy

from water_ai.agents.base import BaseAgent
from water_ai.domain import AgentReport, QualityIssue, SensorReading, Severity


class RecoveryStrategyWritebackAgent(BaseAgent):
    """Write a feasible recovery strategy back into the online-control baseline."""

    name = "recovery_strategy_writeback_agent"

    def __init__(
        self,
        *,
        time_budget_recovery_metrics: dict[str, object] | None = None,
        previous_baseline: dict[str, object] | None = None,
        baseline_version: str = "baseline_v1_replan",
    ) -> None:
        self.time_budget_recovery_metrics = time_budget_recovery_metrics or {}
        self.previous_baseline = previous_baseline or {}
        self.baseline_version = baseline_version

    def run(self, readings: Sequence[SensorReading]) -> AgentReport:
        del readings
        writeback = self._writeback()
        issues = self._issues(writeback)
        recommendations = self._recommendations(writeback)
        decision = writeback["writeback_decision"]
        summary = (
            f"恢复策略写回：{decision['writeback_mode']}；下一轮目标进水 "
            f"{decision['next_intake_fraction']}，回退比例 {decision['fallback_intake_fraction']}。"
        )
        confidence = round(min(0.95, max(0.18, 0.50 + 0.20 * float(decision["target_recovery_enabled"]) - 0.05 * len(issues))), 3)

        return AgentReport(
            agent_name=self.name,
            confidence=confidence,
            summary=summary,
            issues=issues,
            recommendations=recommendations,
            metrics={
                "recovery_strategy_baseline": writeback,
            },
        )

    def _writeback(self) -> dict[str, object]:
        selected = self._selected_candidate()
        safe_fraction = float(self.time_budget_recovery_metrics.get("safe_intake_fraction", 0.45))
        target_fraction = float(self.time_budget_recovery_metrics.get("target_intake_fraction", safe_fraction))
        target_enabled = bool(selected.get("stable")) and bool(selected.get("target_recovery"))
        next_intake = target_fraction if target_enabled else safe_fraction
        fallback_fraction = safe_fraction
        config = deepcopy(self.previous_baseline)
        load_policy = self._dict_section(config, "load_control_policy")
        load_policy["protected_intake_fraction"] = round(next_intake, 3)
        load_policy["fallback_intake_fraction"] = round(fallback_fraction, 3)
        load_policy["normalization_rule"] = self._normalization_rule(target_enabled)
        load_policy["conditional_recovery_enabled"] = target_enabled
        load_policy["conditional_recovery_strategy"] = selected.get("candidate_id", "none")
        config["load_control_policy"] = load_policy

        recovery_policy = self._recovery_policy(selected, target_enabled, target_fraction, fallback_fraction)
        config["recovery_control_policy"] = recovery_policy
        config["writeback_rules"] = self._updated_writeback_rules(config, selected, target_enabled, fallback_fraction)
        config["guardrails"] = self._updated_guardrails(config, selected)
        config["selected_queue_policy"] = self._updated_queue_policy(config, selected)

        next_version = self._next_version()
        return {
            "update_required": True,
            "baseline_version": next_version,
            "previous_baseline_version": self.baseline_version,
            "online_control_config": config,
            "writeback_decision": {
                "writeback_mode": "conditional_target_recovery" if target_enabled else "hold_safe_recovery_fraction",
                "target_recovery_enabled": target_enabled,
                "selected_candidate_id": selected.get("candidate_id", "none"),
                "next_intake_fraction": round(next_intake, 3),
                "fallback_intake_fraction": round(fallback_fraction, 3),
                "expected_time_budget_usage": selected.get("time_budget_usage"),
                "expected_validation_staff_usage": selected.get("validation_staff_usage"),
                "expected_actual_throughput_fraction": selected.get("actual_throughput_fraction"),
            },
            "writeback_summary": self._summary(selected, target_enabled, next_intake, fallback_fraction),
        }

    def _selected_candidate(self) -> dict[str, object]:
        selected = self.time_budget_recovery_metrics.get("selected_candidate", {})
        return selected if isinstance(selected, dict) else {}

    @staticmethod
    def _dict_section(config: dict[str, object], key: str) -> dict[str, object]:
        section = config.get(key, {})
        return deepcopy(section) if isinstance(section, dict) else {}

    @staticmethod
    def _normalization_rule(target_enabled: bool) -> str:
        if target_enabled:
            return "在执行恢复控制策略且 campaign 后遥测未触发瓶颈时，允许按目标进水比例运行；若验收失败或时间预算超限，立即回退到 fallback_intake_fraction。"
        return "目标恢复比例暂不可行，保持安全恢复上限并继续滚动复核。"

    def _recovery_policy(
        self,
        selected: dict[str, object],
        target_enabled: bool,
        target_fraction: float,
        fallback_fraction: float,
    ) -> dict[str, object]:
        candidate_id = str(selected.get("candidate_id", "none"))
        policy = {
            "policy_id": "recovery_strategy_v1",
            "enabled": target_enabled,
            "selected_candidate_id": candidate_id,
            "target_intake_fraction": round(target_fraction if target_enabled else fallback_fraction, 3),
            "fallback_intake_fraction": round(fallback_fraction, 3),
            "expected_time_budget_usage": selected.get("time_budget_usage"),
            "expected_validation_staff_usage": selected.get("validation_staff_usage"),
            "expected_actual_throughput_fraction": selected.get("actual_throughput_fraction"),
            "admitted_batch_count": selected.get("admitted_batch_count"),
            "queue_policy": selected.get("queue_policy", "source_order"),
            "scenario_sequence": selected.get("scenario_sequence", []),
            "required_post_campaign_checks": [
                "CampaignTelemetryAgent",
                "PostReplanReplayAgent",
                "RecoveryRampAgent",
            ],
            "fallback_triggers": [
                "acceptance_passed is false",
                "time_budget_usage >= 0.90",
                "validation_staff_usage >= 0.90",
                "campaign_time_budget bottleneck returns",
                "new catalyst_inventory or oxidant_stock bottleneck appears",
            ],
        }
        if candidate_id == "stagger_validation_overlap":
            policy["execution_requirements"] = [
                "保持 selected_queue_policy 原队列顺序。",
                "将旁路验证、暂存等待和回流观察错峰并行。",
                "每个长验证批次最多折叠 30 min 总占用时间。",
                "不得取消放行门、副产物和催化剂寿命慢证据。",
            ]
            policy["validation_overlap_rule"] = {
                "overlap_fraction_of_validation_minutes": 0.35,
                "max_overlap_min_per_batch": 30,
                "projected_elapsed_reduction_min": selected.get("elapsed_reduction_min", 0.0),
            }
        else:
            policy["execution_requirements"] = [str(selected.get("description", "保持安全恢复策略并继续复核。"))]
        return policy

    def _updated_writeback_rules(
        self,
        config: dict[str, object],
        selected: dict[str, object],
        target_enabled: bool,
        fallback_fraction: float,
    ) -> dict[str, object]:
        rules = self._dict_section(config, "writeback_rules")
        rules.update(
            {
                "recovery_strategy_writeback": True,
                "target_recovery_enabled": target_enabled,
                "selected_recovery_candidate_id": selected.get("candidate_id", "none"),
                "fallback_intake_fraction": round(fallback_fraction, 3),
                "post_recovery_replay_required": True,
                "post_recovery_ramp_recheck_required": True,
                "replan_on_time_budget_usage_gte": 0.90,
                "replan_on_validation_staff_usage_gte": 0.90,
            }
        )
        return rules

    def _updated_guardrails(self, config: dict[str, object], selected: dict[str, object]) -> dict[str, object]:
        guardrails = self._dict_section(config, "guardrails")
        mandatory = guardrails.get("mandatory_replan_thresholds", [])
        if not isinstance(mandatory, list):
            mandatory = []
        for item in [
            "time_budget_usage >= 0.90 under recovery strategy",
            "validation_staff_usage >= 0.90 under recovery strategy",
            "campaign_time_budget bottleneck returns after staggered validation overlap",
        ]:
            if item not in mandatory:
                mandatory.append(item)
        guardrails["mandatory_replan_thresholds"] = mandatory
        guardrails["max_transition_intake_fraction"] = max(
            float(guardrails.get("max_transition_intake_fraction", 0.0) or 0.0),
            float(selected.get("target_intake_fraction", 0.0) or 0.0),
        )
        return guardrails

    def _updated_queue_policy(self, config: dict[str, object], selected: dict[str, object]) -> dict[str, object]:
        queue = self._dict_section(config, "selected_queue_policy")
        queue["runtime_recovery_override"] = {
            "queue_policy": selected.get("queue_policy", "source_order"),
            "preserve_replanned_order": selected.get("queue_policy", "source_order") == "source_order",
            "selected_recovery_candidate_id": selected.get("candidate_id", "none"),
            "scenario_sequence": selected.get("scenario_sequence", []),
        }
        return queue

    def _next_version(self) -> str:
        suffix = "_recovery"
        if self.baseline_version.endswith(suffix):
            return self.baseline_version
        return f"{self.baseline_version}{suffix}"

    @staticmethod
    def _summary(selected: dict[str, object], target_enabled: bool, next_intake: float, fallback_fraction: float) -> str:
        if target_enabled:
            return (
                f"写回恢复策略 {selected.get('candidate_id', 'none')}，下一轮目标进水 {round(next_intake, 3)}，"
                f"若遥测触发瓶颈则回退到 {round(fallback_fraction, 3)}。"
            )
        return (
            f"目标恢复方案不可行，写回安全恢复比例 {round(fallback_fraction, 3)}，"
            "继续保留恢复策略复核。"
        )

    @staticmethod
    def _issues(writeback: dict[str, object]) -> list[QualityIssue]:
        decision = writeback["writeback_decision"]
        issues: list[QualityIssue] = []
        if not bool(decision["target_recovery_enabled"]):
            issues.append(
                QualityIssue(
                    sensor="recovery_strategy_writeback",
                    issue_type="target_recovery_not_written",
                    severity=Severity.WARNING,
                    message="目标恢复方案尚不可写回，只能保持安全恢复上限。",
                    evidence={"writeback_decision": decision},
                )
            )
        if decision["selected_candidate_id"] == "time_smoothed_queue":
            issues.append(
                QualityIssue(
                    sensor="recovery_strategy_writeback",
                    issue_type="queue_reordering_requires_wait_limit",
                    severity=Severity.INFO,
                    message="恢复策略依赖重排队列，需要设置最长等待上限，避免高风险批次长期后移。",
                    evidence={"writeback_decision": decision},
                )
            )
        return issues

    @staticmethod
    def _recommendations(writeback: dict[str, object]) -> list[str]:
        decision = writeback["writeback_decision"]
        config = writeback["online_control_config"]
        recovery = config.get("recovery_control_policy", {})
        recommendations = [
            f"下一轮在线控制使用 {writeback['baseline_version']}。",
            f"按 {decision['selected_candidate_id']} 执行恢复策略，目标进水比例 {decision['next_intake_fraction']}，回退比例 {decision['fallback_intake_fraction']}。",
            "campaign 后必须重新运行遥测桥接、回放验证和恢复爬坡复核。",
        ]
        if isinstance(recovery, dict) and recovery.get("fallback_triggers"):
            recommendations.append("若触发任一 fallback trigger，立即回退到 fallback_intake_fraction 并重新执行时间预算恢复方案选择。")
        return recommendations

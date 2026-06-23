from __future__ import annotations

from collections.abc import Sequence

from water_ai.agents.base import BaseAgent
from water_ai.domain import AgentReport, QualityIssue, SensorReading, Severity


class ControlBaselineUpdateAgent(BaseAgent):
    """Write replanning outputs back into the next online-control baseline."""

    name = "control_baseline_update_agent"

    def __init__(
        self,
        *,
        replan_trace: dict[str, object] | None = None,
        replan_executed: bool = False,
        previous_baseline: dict[str, object] | None = None,
        baseline_version: str = "baseline_v1",
    ) -> None:
        self.replan_trace = replan_trace or {}
        self.replan_executed = replan_executed
        self.previous_baseline = previous_baseline or {}
        self.baseline_version = baseline_version

    def run(self, readings: Sequence[SensorReading]) -> AgentReport:
        del readings
        updated = self._updated_baseline()
        update_required = bool(updated["update_required"])
        issues = self._issues(updated)
        recommendations = self._recommendations(updated)
        summary = (
            f"控制基线更新：已写回 {updated['baseline_version']}，下一轮保护性进水比例 "
            f"{updated['online_control_config']['load_control_policy'].get('protected_intake_fraction', 0.0)}。"
            if update_required
            else "控制基线更新：未执行重规划，沿用上一版在线控制基线。"
        )
        confidence = round(min(0.95, max(0.18, 0.52 + 0.18 * float(update_required) - 0.05 * len(issues))), 3)

        return AgentReport(
            agent_name=self.name,
            confidence=confidence,
            summary=summary,
            issues=issues,
            recommendations=recommendations,
            metrics={
                "updated_baseline": updated,
            },
        )

    def _updated_baseline(self) -> dict[str, object]:
        if not self.replan_executed:
            return {
                "update_required": False,
                "baseline_version": self.baseline_version,
                "online_control_config": self.previous_baseline,
                "writeback_summary": "replan 未执行，保持上一版基线。",
            }

        queue = self._trace_section("queue_planning")
        portfolio = self._trace_section("adaptive_portfolio")
        implementation = self._trace_section("phased_implementation")
        stress = self._trace_section("implementation_stress_test")
        selected_portfolio = portfolio.get("selected_portfolio", {})
        load_control_policy = portfolio.get("load_control_policy", {})
        budget_sequence = portfolio.get("budget_sequence", [])
        selected_queue = queue.get("selected_policy", {})
        next_version = self._next_version()
        online_control_config = {
            "selected_queue_policy": selected_queue,
            "selected_portfolio": selected_portfolio,
            "budget_sequence": budget_sequence,
            "load_control_policy": load_control_policy,
            "readiness": implementation.get("readiness", {}),
            "guardrails": stress.get("guardrails", {}),
            "writeback_rules": {
                "stable_campaigns_required_for_ramp": 2,
                "ramp_step": 0.15,
                "replan_on_acceptance_failure": True,
                "replan_on_ready_campaign_slip_gt": 1,
            },
        }
        return {
            "update_required": True,
            "baseline_version": next_version,
            "online_control_config": online_control_config,
            "writeback_summary": (
                f"写回队列 {selected_queue.get('policy_id', 'none')}、项目包 "
                f"{selected_portfolio.get('package_id', 'none')}、预算项 {len(budget_sequence)} 个。"
            ),
        }

    def _trace_section(self, key: str) -> dict[str, object]:
        section = self.replan_trace.get(key, {})
        return section if isinstance(section, dict) else {}

    def _next_version(self) -> str:
        suffix = "_replan"
        if self.baseline_version.endswith(suffix):
            return self.baseline_version
        return f"{self.baseline_version}{suffix}"

    @staticmethod
    def _issues(updated: dict[str, object]) -> list[QualityIssue]:
        if not bool(updated.get("update_required", False)):
            return []
        config = updated.get("online_control_config", {})
        if not isinstance(config, dict):
            return [
                QualityIssue(
                    sensor="control_baseline",
                    issue_type="invalid_writeback_config",
                    severity=Severity.CRITICAL,
                    message="重规划已执行，但生成的在线控制基线不是结构化配置。",
                )
            ]
        missing: list[str] = []
        for key in ["selected_portfolio", "budget_sequence", "load_control_policy"]:
            if not config.get(key):
                missing.append(key)
        if missing:
            return [
                QualityIssue(
                    sensor="control_baseline",
                    issue_type="incomplete_writeback",
                    severity=Severity.WARNING,
                    message="重规划写回缺少关键配置项。",
                    evidence={"missing": missing, "updated_baseline": updated},
                )
            ]
        return []

    @staticmethod
    def _recommendations(updated: dict[str, object]) -> list[str]:
        if not bool(updated.get("update_required", False)):
            return ["沿用上一版在线控制基线；下一 campaign 后继续检查 replan_required。"]
        config = updated["online_control_config"]
        load_policy = config["load_control_policy"]
        portfolio = config["selected_portfolio"]
        queue = config.get("selected_queue_policy", {})
        return [
            f"下一轮 OnlineProjectControlAgent 使用 {updated['baseline_version']}。",
            f"默认项目包写回为 {portfolio.get('package_id', 'none')}，保护性进水比例 {load_policy.get('protected_intake_fraction', 0.0)}。",
            f"默认队列策略写回为 {queue.get('policy_id', 'none')}。",
            "每个 campaign 后继续用 CampaignTelemetryAgent 生成滚动更新，并用新基线判断是否再次重规划。",
        ]

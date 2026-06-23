from __future__ import annotations

from collections.abc import Sequence

from water_ai.agents.base import BaseAgent
from water_ai.domain import AgentReport, QualityIssue, SensorReading, Severity


class OnlineProjectControlAgent(BaseAgent):
    """Update project portfolio, budget order, and intake control after each campaign."""

    name = "online_project_control_agent"

    def __init__(
        self,
        *,
        selected_portfolio: dict[str, object] | None = None,
        budget_sequence: list[dict[str, object]] | None = None,
        load_control_policy: dict[str, object] | None = None,
        rolling_campaigns: list[dict[str, object]] | None = None,
        catalyst_safety_stock: int = 2,
        oxidant_safety_stock_units: float = 1.2,
        validation_usage_limit: float = 0.85,
        time_usage_limit: float = 0.90,
    ) -> None:
        self.selected_portfolio = selected_portfolio or {}
        self.budget_sequence = budget_sequence or []
        self.load_control_policy = load_control_policy or {}
        self.rolling_campaigns = rolling_campaigns or []
        self.catalyst_safety_stock = catalyst_safety_stock
        self.oxidant_safety_stock_units = oxidant_safety_stock_units
        self.validation_usage_limit = validation_usage_limit
        self.time_usage_limit = time_usage_limit

    def run(self, readings: Sequence[SensorReading]) -> AgentReport:
        del readings
        decisions = self._rolling_decisions()
        latest = decisions[-1] if decisions else {}
        issues = self._issues(latest)
        recommendations = self._recommendations(latest)
        summary = (
            f"在线项目控制：当前模式 {latest.get('project_mode', 'none')}，"
            f"下一轮进水比例 {latest.get('next_intake_fraction', 0.0)}，"
            f"下一预算项 {latest.get('next_budget_item', 'none')}。"
            if latest
            else "在线项目控制：没有 campaign 更新可滚动判断。"
        )
        confidence = round(min(0.95, max(0.18, 0.42 + 0.05 * len(decisions) + 0.20 * float(latest.get("control_confidence", 0.0) if latest else 0.0) - 0.06 * len(issues))), 3)

        return AgentReport(
            agent_name=self.name,
            confidence=confidence,
            summary=summary,
            issues=issues,
            recommendations=recommendations,
            metrics={
                "rolling_decisions": decisions,
                "current_control_state": latest,
                "selected_portfolio_id": self.selected_portfolio.get("package_id", "unknown"),
                "base_load_control_policy": self.load_control_policy,
            },
        )

    def _rolling_decisions(self) -> list[dict[str, object]]:
        decisions: list[dict[str, object]] = []
        last_intake = float(self.load_control_policy.get("protected_intake_fraction", 0.55))
        stable_streak = 0
        released_items: set[str] = set()

        for index, campaign in enumerate(self.rolling_campaigns):
            released_items.update(self._released_items(campaign))
            pressure = self._campaign_pressure(campaign)
            stable = bool(campaign.get("acceptance_passed", False)) and pressure["rolling_risk"] < 0.25
            stable_streak = stable_streak + 1 if stable else 0
            next_intake = self._next_intake_fraction(
                rolling_risk=pressure["rolling_risk"],
                stable_streak=stable_streak,
                last_intake=last_intake,
                acceptance_passed=bool(campaign.get("acceptance_passed", False)),
            )
            next_budget = self._next_budget_item(pressure["dominant_signals"], released_items)
            replan_required, replan_reasons = self._replan_state(pressure, campaign, stable_streak, next_intake)
            mode = self._project_mode(pressure["rolling_risk"], replan_required, stable_streak)
            decision = {
                "campaign_id": campaign.get("campaign_id", index),
                "project_mode": mode,
                "rolling_risk": pressure["rolling_risk"],
                "dominant_signals": pressure["dominant_signals"],
                "stable_streak": stable_streak,
                "next_intake_fraction": next_intake,
                "next_budget_item": next_budget,
                "released_budget_items": sorted(released_items),
                "replan_required": replan_required,
                "replan_reasons": replan_reasons,
                "control_confidence": self._control_confidence(pressure, stable_streak, replan_required),
            }
            decisions.append(decision)
            last_intake = next_intake
        return decisions

    def _campaign_pressure(self, campaign: dict[str, object]) -> dict[str, object]:
        validation_usage = float(campaign.get("validation_staff_usage", 0.0))
        time_usage = float(campaign.get("time_budget_usage", 0.0))
        catalyst_spares = int(campaign.get("catalyst_spares_remaining", self.catalyst_safety_stock))
        oxidant_stock = float(campaign.get("oxidant_stock_units_remaining", self.oxidant_safety_stock_units))
        success_rate = float(campaign.get("success_rate", 1.0))
        intake_pressure = float(campaign.get("intake_pressure_multiplier", 1.0))
        acceptance_passed = bool(campaign.get("acceptance_passed", True))
        budget_release_fraction = float(campaign.get("budget_release_fraction", 1.0))

        signals: list[str] = []
        risk = 0.0
        if validation_usage > self.validation_usage_limit:
            signals.append("validation_overload")
            risk += min(0.22, (validation_usage - self.validation_usage_limit) * 0.55 + 0.08)
        if time_usage > self.time_usage_limit:
            signals.append("time_budget_pressure")
            risk += min(0.18, (time_usage - self.time_usage_limit) * 0.45 + 0.06)
        if catalyst_spares < self.catalyst_safety_stock:
            signals.append("catalyst_inventory")
            risk += min(0.22, (self.catalyst_safety_stock - catalyst_spares) * 0.11)
        if oxidant_stock < self.oxidant_safety_stock_units:
            signals.append("oxidant_inventory")
            risk += min(0.12, (self.oxidant_safety_stock_units - oxidant_stock) * 0.08)
        if success_rate < 0.95 or not acceptance_passed:
            signals.append("acceptance_failure")
            risk += 0.28
        if intake_pressure > 1.05:
            signals.append("high_intake_pressure")
            risk += min(0.14, (intake_pressure - 1.0) * 0.22)
        if budget_release_fraction < 0.85:
            signals.append("budget_slow_release")
            risk += min(0.12, (0.85 - budget_release_fraction) * 0.35 + 0.04)
        return {
            "rolling_risk": round(self._clip(risk), 3),
            "dominant_signals": signals or ["stable"],
        }

    def _next_intake_fraction(
        self,
        *,
        rolling_risk: float,
        stable_streak: int,
        last_intake: float,
        acceptance_passed: bool,
    ) -> float:
        base = float(self.load_control_policy.get("protected_intake_fraction", 0.55))
        if not acceptance_passed or rolling_risk >= 0.55:
            return round(max(0.30, min(last_intake, base) - 0.10), 2)
        if rolling_risk >= 0.35:
            return round(min(base, 0.45), 2)
        if stable_streak >= 2:
            return round(min(1.0, max(last_intake, base) + 0.15), 2)
        if stable_streak == 1 and rolling_risk < 0.20:
            return round(min(0.75, max(last_intake, base) + 0.08), 2)
        return round(min(last_intake, base), 2)

    def _next_budget_item(self, signals: list[str], released_items: set[str]) -> str:
        priority = self._budget_priority(signals)
        ordered_items = [str(item.get("budget_item", "")) for item in self.budget_sequence if isinstance(item, dict)]
        for item in priority + ordered_items:
            if item and item not in released_items:
                return item
        return "本轮无需新增预算项，保持滚动复核"

    @staticmethod
    def _budget_priority(signals: list[str]) -> list[str]:
        priority: list[str] = []
        if "validation_overload" in signals or "high_intake_pressure" in signals or "acceptance_failure" in signals:
            priority.extend(["外包低价值验证", "验证能力批复"])
        if "catalyst_inventory" in signals:
            priority.extend(["催化剂备用供应商", "催化剂库存批复"])
        if "oxidant_inventory" in signals:
            priority.append("氧化剂库存批复")
        if "budget_slow_release" in signals:
            priority.extend(["验证能力批复", "催化剂库存批复", "氧化剂库存批复"])
        return priority

    @staticmethod
    def _released_items(campaign: dict[str, object]) -> set[str]:
        items = campaign.get("budget_released_items", [])
        return {str(item) for item in items} if isinstance(items, list) else set()

    @staticmethod
    def _replan_state(
        pressure: dict[str, object],
        campaign: dict[str, object],
        stable_streak: int,
        next_intake: float,
    ) -> tuple[bool, list[str]]:
        reasons: list[str] = []
        risk = float(pressure["rolling_risk"])
        signals = set(pressure["dominant_signals"])
        if risk >= 0.55:
            reasons.append("rolling_risk >= 0.55")
        if "acceptance_failure" in signals:
            reasons.append("验收或放行成功率未达标")
        if next_intake <= 0.35:
            reasons.append("保护性进水比例降至 0.35 以下")
        if int(campaign.get("ready_campaign_slip", 0)) > 1:
            reasons.append("ready campaign 推迟超过 1 个 campaign")
        if stable_streak == 0 and risk >= 0.35:
            reasons.append("压力升高且未形成稳定验收 streak")
        return bool(reasons), reasons

    @staticmethod
    def _project_mode(rolling_risk: float, replan_required: bool, stable_streak: int) -> str:
        if replan_required:
            return "replan_and_protect"
        if rolling_risk >= 0.35:
            return "protective_intake"
        if stable_streak >= 2:
            return "controlled_ramp_up"
        return "steady_monitoring"

    @staticmethod
    def _control_confidence(pressure: dict[str, object], stable_streak: int, replan_required: bool) -> float:
        confidence = 0.42 + 0.16 * min(stable_streak, 2) - 0.22 * float(pressure["rolling_risk"])
        if replan_required:
            confidence += 0.10
        return round(max(0.1, min(0.95, confidence)), 3)

    @staticmethod
    def _issues(latest: dict[str, object]) -> list[QualityIssue]:
        if not latest:
            return [
                QualityIssue(
                    sensor="online_project_control",
                    issue_type="missing_campaign_updates",
                    severity=Severity.WARNING,
                    message="未提供 campaign 级滚动更新，无法在线调整项目组合。",
                )
            ]
        if latest.get("replan_required"):
            return [
                QualityIssue(
                    sensor="online_project_control",
                    issue_type="online_replan_required",
                    severity=Severity.WARNING,
                    message="最新 campaign 触发在线重规划，需要重新计算队列、资源扩容或项目组合。",
                    evidence={"current_control_state": latest},
                )
            ]
        return []

    @staticmethod
    def _recommendations(latest: dict[str, object]) -> list[str]:
        if not latest:
            return ["补充至少一个 campaign 的验收、库存、预算和进水压力更新。"]
        recommendations = [
            f"下一 campaign 进水比例控制为 {latest['next_intake_fraction']}，项目模式为 {latest['project_mode']}。",
            f"下一预算项优先处理：{latest['next_budget_item']}。",
        ]
        if latest.get("replan_required"):
            recommendations.append("触发在线重规划：重新运行队列规划、资源扩容、压力测试和项目组合选择。")
        elif latest.get("project_mode") == "controlled_ramp_up":
            recommendations.append("已形成连续稳定验收，可按 0.15 梯度恢复进水，但继续保留最终放行门。")
        else:
            recommendations.append("保持 campaign 后滚动复核，避免阶段计划静态化。")
        return recommendations

    @staticmethod
    def _clip(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
        return max(lo, min(hi, value))

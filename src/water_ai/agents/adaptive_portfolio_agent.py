from __future__ import annotations

from collections.abc import Sequence

from water_ai.agents.base import BaseAgent
from water_ai.domain import AgentReport, QualityIssue, SensorReading, Severity


class AdaptivePortfolioAgent(BaseAgent):
    """Choose adaptive project packages from implementation stress-test results."""

    name = "adaptive_portfolio_agent"

    def __init__(
        self,
        *,
        ranked_stress_scenarios: list[dict[str, object]] | None = None,
        guardrails: dict[str, object] | None = None,
        selected_program: dict[str, object] | None = None,
        budget_limit_increment: float = 1.2,
        candidate_packages: list[dict[str, object]] | None = None,
    ) -> None:
        self.ranked_stress_scenarios = ranked_stress_scenarios or []
        self.guardrails = guardrails or {}
        self.selected_program = selected_program or {}
        self.budget_limit_increment = budget_limit_increment
        self.candidate_packages = candidate_packages or self._default_packages()

    def run(self, readings: Sequence[SensorReading]) -> AgentReport:
        del readings
        evaluated = [self._evaluate_package(package) for package in self.candidate_packages]
        evaluated.sort(key=lambda item: item["portfolio_score"], reverse=True)
        selected = evaluated[0] if evaluated else {}
        budget_sequence = self._budget_sequence(selected)
        load_policy = self._load_control_policy(selected)
        issues = self._issues(selected)
        recommendations = self._recommendations(selected, budget_sequence, load_policy)

        summary = (
            f"自适应项目组合：推荐 {selected.get('package_id', 'none')}，评分 {selected.get('portfolio_score', 0.0)}，"
            f"风险降低 {selected.get('expected_risk_reduction', 0.0)}。"
            if selected
            else "自适应项目组合：没有候选项目包可评价。"
        )
        confidence = round(min(0.95, max(0.16, 0.42 + 0.06 * len(evaluated) + 0.18 * float(selected.get("coverage_score", 0.0) if selected else 0.0) - 0.05 * len(issues))), 3)

        return AgentReport(
            agent_name=self.name,
            confidence=confidence,
            summary=summary,
            issues=issues,
            recommendations=recommendations,
            metrics={
                "selected_portfolio": selected,
                "ranked_portfolios": evaluated,
                "budget_sequence": budget_sequence,
                "load_control_policy": load_policy,
                "dominant_stress_signals": self._dominant_signals(),
            },
        )

    def _evaluate_package(self, package: dict[str, object]) -> dict[str, object]:
        signals = self._dominant_signals()
        baseline_risk = max([float(item.get("scenario_risk", 0.0)) for item in self.ranked_stress_scenarios] or [0.0])
        coverage = self._coverage_score(package, signals)
        risk_reduction = min(baseline_risk, baseline_risk * (0.35 + 0.55 * coverage))
        residual_risk = max(0.0, baseline_risk - risk_reduction)
        package_cost = float(package.get("incremental_budget_index", 0.0))
        budget_pressure = package_cost / max(self.budget_limit_increment, 1e-9)
        implementation_complexity = float(package.get("implementation_complexity", 0.0))
        speed = float(package.get("speed_score", 0.5))
        portfolio_score = self._clip(
            0.34 * coverage
            + 0.24 * (1.0 - min(residual_risk, 0.65) / 0.65)
            + 0.18 * speed
            + 0.14 * (1.0 - min(budget_pressure, 1.5) / 1.5)
            - 0.10 * implementation_complexity
        )
        return {
            "package_id": str(package.get("package_id", "unknown")),
            "description": str(package.get("description", "")),
            "portfolio_score": round(portfolio_score, 3),
            "coverage_score": round(coverage, 3),
            "expected_risk_reduction": round(risk_reduction, 3),
            "residual_risk": round(residual_risk, 3),
            "incremental_budget_index": round(package_cost, 3),
            "budget_pressure": round(budget_pressure, 3),
            "implementation_complexity": round(implementation_complexity, 3),
            "covered_signals": [signal for signal in signals if signal in set(package.get("covers", []))],
            "missing_signals": [signal for signal in signals if signal not in set(package.get("covers", []))],
            "budget_items": list(package.get("budget_items", [])) if isinstance(package.get("budget_items", []), list) else [],
            "load_controls": list(package.get("load_controls", [])) if isinstance(package.get("load_controls", []), list) else [],
            "fallback_actions": list(package.get("fallback_actions", [])) if isinstance(package.get("fallback_actions", []), list) else [],
        }

    def _dominant_signals(self) -> list[str]:
        signals: set[str] = set()
        for item in self.ranked_stress_scenarios:
            if float(item.get("catalyst_stockout_risk", 0.0)) >= 0.18:
                signals.add("catalyst_delay")
            if float(item.get("oxidant_stockout_risk", 0.0)) >= 0.18:
                signals.add("oxidant_delay")
            if float(item.get("validation_overload_risk", 0.0)) >= 0.24:
                signals.add("validation_ramp_delay")
            if float(item.get("budget_gap", 0.0)) >= 0.20:
                signals.add("budget_slow_release")
            if float(item.get("intake_pressure_multiplier", 1.0)) > 1.05:
                signals.add("high_intake_pressure")
            if "acceptance" in str(item.get("scenario_id", "")) and float(item.get("scenario_risk", 0.0)) > 0:
                signals.add("acceptance_failure")
        return sorted(signals) or ["on_schedule"]

    @staticmethod
    def _coverage_score(package: dict[str, object], signals: list[str]) -> float:
        covers = set(package.get("covers", [])) if isinstance(package.get("covers", []), list) else set()
        if not signals:
            return 0.0
        direct = sum(1 for signal in signals if signal in covers) / len(signals)
        broad_bonus = 0.12 if "all_transition_risks" in covers and any(signal != "on_schedule" for signal in signals) else 0.0
        return min(1.0, direct + broad_bonus)

    @staticmethod
    def _budget_sequence(selected: dict[str, object]) -> list[dict[str, object]]:
        items = selected.get("budget_items", [])
        if not isinstance(items, list):
            items = []
        return [
            {
                "order": index + 1,
                "budget_item": item,
                "release_rule": "先批复后进入下一项，失败则回退到保护性进水上限。",
            }
            for index, item in enumerate(items)
        ]

    def _load_control_policy(self, selected: dict[str, object]) -> dict[str, object]:
        base_guardrail = float(self.guardrails.get("max_transition_intake_fraction", 0.55))
        if "high_intake_pressure" in selected.get("covered_signals", []):
            protected = min(base_guardrail, 0.45)
        else:
            protected = base_guardrail
        return {
            "protected_intake_fraction": round(protected, 2),
            "normalization_rule": "仅当两个连续 campaign 通过阶段验收，才从保护性进水比例逐步恢复。",
            "load_controls": selected.get("load_controls", []),
        }

    @staticmethod
    def _issues(selected: dict[str, object]) -> list[QualityIssue]:
        if not selected:
            return [
                QualityIssue(
                    sensor="adaptive_portfolio",
                    issue_type="empty_portfolio_set",
                    severity=Severity.WARNING,
                    message="未提供可评价项目包。",
                )
            ]
        issues: list[QualityIssue] = []
        if float(selected.get("coverage_score", 0.0)) < 0.60:
            issues.append(
                QualityIssue(
                    sensor="adaptive_portfolio",
                    issue_type="weak_signal_coverage",
                    severity=Severity.WARNING,
                    message="推荐项目包未覆盖主要压力信号，备用路径可能不够稳健。",
                    evidence={"selected_portfolio": selected},
                )
            )
        if float(selected.get("budget_pressure", 0.0)) > 1.0:
            issues.append(
                QualityIssue(
                    sensor="adaptive_portfolio",
                    issue_type="portfolio_budget_pressure",
                    severity=Severity.WARNING,
                    message="推荐项目包超出本轮增量预算，需要拆分批复或降低进水负荷。",
                    evidence={"selected_portfolio": selected},
                )
            )
        return issues

    @staticmethod
    def _recommendations(
        selected: dict[str, object],
        budget_sequence: list[dict[str, object]],
        load_policy: dict[str, object],
    ) -> list[str]:
        recommendations = [
            f"采用 {selected.get('package_id', 'none')} 作为压力情景备用项目包，覆盖 {selected.get('covered_signals', [])}。",
            f"过渡期保护性进水比例设为 {load_policy.get('protected_intake_fraction', 0.0)}，未通过两个连续 campaign 验收前不恢复满负荷。",
        ]
        if budget_sequence:
            recommendations.append(
                "预算释放顺序：" + " -> ".join(str(item["budget_item"]) for item in budget_sequence)
            )
        recommendations.extend(selected.get("fallback_actions", [])[:3] if isinstance(selected.get("fallback_actions", []), list) else [])
        return recommendations

    @staticmethod
    def _default_packages() -> list[dict[str, object]]:
        return [
            {
                "package_id": "baseline_execution",
                "description": "按原分阶段计划执行，不增加备用资源。",
                "covers": ["on_schedule"],
                "incremental_budget_index": 0.05,
                "implementation_complexity": 0.04,
                "speed_score": 0.75,
                "budget_items": ["campaign滚动复核"],
                "load_controls": ["维持基准保护性进水比例"],
                "fallback_actions": ["只在触发阈值越界时重跑实施压力测试。"],
            },
            {
                "package_id": "validation_bridge_package",
                "description": "用外包低价值验证和内部关键验证优先级缓解验证爬坡失败。",
                "covers": ["validation_ramp_delay", "high_intake_pressure"],
                "incremental_budget_index": 0.38,
                "implementation_complexity": 0.18,
                "speed_score": 0.88,
                "budget_items": ["外包低价值背景验证", "内部关键验证班次加班池"],
                "load_controls": ["高验证压力批次错峰", "保护性进水上限 0.45"],
                "fallback_actions": ["内部班次只保留放行门、副产物和催化剂寿命证据。"],
            },
            {
                "package_id": "supplier_resilience_package",
                "description": "针对催化剂与氧化剂供应延迟建立双供应和应急调拨。",
                "covers": ["catalyst_delay", "oxidant_delay"],
                "incremental_budget_index": 0.72,
                "implementation_complexity": 0.26,
                "speed_score": 0.62,
                "budget_items": ["催化剂备用供应商", "催化剂应急调拨协议", "氧化剂安全库存"],
                "load_controls": ["连续催化剂压力批次禁止排队"],
                "fallback_actions": ["催化剂晚到时启动外部调拨或备用供应商询价。"],
            },
            {
                "package_id": "phased_budget_package",
                "description": "预算慢批时把建设拆成高瓶颈贡献的三张批复单。",
                "covers": ["budget_slow_release", "acceptance_failure"],
                "incremental_budget_index": 0.24,
                "implementation_complexity": 0.14,
                "speed_score": 0.82,
                "budget_items": ["验证能力批复", "催化剂库存批复", "氧化剂库存批复"],
                "load_controls": ["预算未批复项对应的高风险批次限流"],
                "fallback_actions": ["阶段验收失败时回退到上一阶段进水比例并重排队列。"],
            },
            {
                "package_id": "resilience_bridge_portfolio",
                "description": "组合备用供应、外包验证、预算分拆和保护性进水，覆盖复合压力情景。",
                "covers": [
                    "all_transition_risks",
                    "catalyst_delay",
                    "oxidant_delay",
                    "validation_ramp_delay",
                    "budget_slow_release",
                    "high_intake_pressure",
                    "acceptance_failure",
                ],
                "incremental_budget_index": 1.05,
                "implementation_complexity": 0.34,
                "speed_score": 0.74,
                "budget_items": ["外包低价值验证", "催化剂备用供应商", "验证能力批复", "催化剂库存批复", "氧化剂库存批复"],
                "load_controls": ["保护性进水上限 0.45", "拒绝新增高风险进水", "连续催化剂压力批次禁止排队"],
                "fallback_actions": [
                    "复合压力情景下同时启动备用供应、预算拆分和外包验证。",
                    "scenario_risk >= 0.35 时自动进入保护性进水。",
                    "阶段验收失败时回退并重跑队列规划和资源扩容评分。",
                ],
            },
        ]

    @staticmethod
    def _clip(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
        return max(lo, min(hi, value))

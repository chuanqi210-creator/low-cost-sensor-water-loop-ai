from __future__ import annotations

from collections.abc import Sequence
from statistics import mean

from water_ai.agents.base import BaseAgent
from water_ai.domain import AgentReport, QualityIssue, SensorReading, Severity


class ImplementationStressTestAgent(BaseAgent):
    """Stress-test a phased implementation plan under delays, budget gaps, and intake pressure."""

    name = "implementation_stress_test_agent"

    def __init__(
        self,
        *,
        selected_program: dict[str, object] | None = None,
        phase_plan: list[dict[str, object]] | None = None,
        intake_policy: dict[str, object] | None = None,
        inventory_policy: dict[str, object] | None = None,
        validation_staffing_plan: dict[str, object] | None = None,
        planning_horizon_campaigns: int = 4,
        stress_scenarios: list[dict[str, object]] | None = None,
    ) -> None:
        self.selected_program = selected_program or {}
        self.phase_plan = phase_plan or []
        self.intake_policy = intake_policy or {}
        self.inventory_policy = inventory_policy or {}
        self.validation_staffing_plan = validation_staffing_plan or {}
        self.planning_horizon_campaigns = planning_horizon_campaigns
        self.stress_scenarios = stress_scenarios or self._default_stress_scenarios()

    def run(self, readings: Sequence[SensorReading]) -> AgentReport:
        del readings
        evaluated = [self._evaluate_scenario(scenario) for scenario in self.stress_scenarios]
        evaluated.sort(key=lambda item: item["scenario_risk"], reverse=True)
        worst_case = evaluated[0] if evaluated else {}
        robustness_score = round(1.0 - mean(float(item["scenario_risk"]) for item in evaluated), 3) if evaluated else 0.0
        guardrails = self._guardrails(evaluated)
        trigger_table = self._trigger_table(evaluated)
        issues = self._issues(worst_case, robustness_score)
        recommendations = self._recommendations(worst_case, guardrails, trigger_table)

        summary = (
            f"实施压力测试：最坏情景 {worst_case.get('scenario_id', 'none')}，风险 {worst_case.get('scenario_risk', 0.0)}，"
            f"总体韧性 {robustness_score}。"
            if evaluated
            else "实施压力测试：没有压力情景可评价。"
        )
        confidence = round(min(0.95, max(0.18, 0.44 + 0.05 * len(evaluated) + 0.20 * robustness_score - 0.06 * len(issues))), 3)

        return AgentReport(
            agent_name=self.name,
            confidence=confidence,
            summary=summary,
            issues=issues,
            recommendations=recommendations,
            metrics={
                "robustness_score": robustness_score,
                "worst_case": worst_case,
                "ranked_stress_scenarios": evaluated,
                "guardrails": guardrails,
                "trigger_table": trigger_table,
            },
        )

    def _evaluate_scenario(self, scenario: dict[str, object]) -> dict[str, object]:
        base_ready = int(self.intake_policy.get("estimated_ready_campaign", self._base_ready_campaign()))
        catalyst_delay = int(scenario.get("catalyst_delay_campaigns", 0))
        oxidant_delay = int(scenario.get("oxidant_delay_campaigns", 0))
        validation_delay = int(scenario.get("validation_ramp_delay_campaigns", 0))
        budget_release = float(scenario.get("budget_release_fraction", 1.0))
        intake_pressure = float(scenario.get("intake_pressure_multiplier", 1.0))
        acceptance_failure = bool(scenario.get("acceptance_failure", False))

        adjusted_ready = base_ready + max(catalyst_delay, oxidant_delay, validation_delay)
        delay_pressure = min(max(0, adjusted_ready - base_ready) / max(self.planning_horizon_campaigns, 1), 1.0)
        budget_gap = max(0.0, 1.0 - budget_release)
        intake_overload = max(0.0, intake_pressure - 1.0)
        catalyst_stockout = self._stockout_risk(
            delay=catalyst_delay,
            safety_stock=float(self.inventory_policy.get("catalyst_safety_stock", 1.0)),
            reorder_point=float(self.inventory_policy.get("catalyst_reorder_point", 1.0)),
        )
        oxidant_stockout = self._stockout_risk(
            delay=oxidant_delay,
            safety_stock=float(self.inventory_policy.get("oxidant_safety_stock_units", 0.8)),
            reorder_point=float(self.inventory_policy.get("oxidant_reorder_point_campaigns", 1.0)),
        )
        validation_overload = self._validation_overload(validation_delay, intake_pressure)
        acceptance_penalty = 0.22 if acceptance_failure else 0.0
        interaction_penalty = 0.12 if delay_pressure > 0 and (budget_gap > 0 or intake_overload > 0) else 0.0
        scenario_risk = self._clip(
            0.24 * delay_pressure
            + 0.18 * budget_gap
            + 0.17 * intake_overload
            + 0.16 * catalyst_stockout
            + 0.10 * oxidant_stockout
            + 0.11 * validation_overload
            + acceptance_penalty
            + interaction_penalty
        )
        contingency_actions = self._contingency_actions(
            catalyst_delay=catalyst_delay,
            oxidant_delay=oxidant_delay,
            validation_delay=validation_delay,
            budget_gap=budget_gap,
            intake_overload=intake_overload,
            acceptance_failure=acceptance_failure,
        )
        protected_intake_fraction = self._protected_intake_fraction(scenario_risk, intake_pressure)

        return {
            "scenario_id": str(scenario.get("scenario_id", "unknown")),
            "description": str(scenario.get("description", "")),
            "scenario_risk": round(scenario_risk, 3),
            "base_ready_campaign": base_ready,
            "adjusted_ready_campaign": adjusted_ready,
            "delay_pressure": round(delay_pressure, 3),
            "budget_gap": round(budget_gap, 3),
            "catalyst_stockout_risk": round(catalyst_stockout, 3),
            "oxidant_stockout_risk": round(oxidant_stockout, 3),
            "validation_overload_risk": round(validation_overload, 3),
            "intake_pressure_multiplier": round(intake_pressure, 3),
            "protected_intake_fraction": round(protected_intake_fraction, 2),
            "contingency_actions": contingency_actions,
        }

    def _base_ready_campaign(self) -> int:
        if not self.phase_plan:
            return 0
        for phase in self.phase_plan:
            if str(phase.get("phase_id", "")) == "phase_3_integrated_ramp_up":
                return int(phase.get("campaign_start", 0))
        return int(self.phase_plan[-1].get("campaign_start", 0))

    @staticmethod
    def _stockout_risk(*, delay: int, safety_stock: float, reorder_point: float) -> float:
        if delay <= 0:
            return 0.0
        buffer = max(safety_stock, 0.0) / max(reorder_point, 1.0)
        return max(0.0, min(1.0, delay / max(reorder_point, 1.0) - 0.22 * buffer))

    def _validation_overload(self, validation_delay: int, intake_pressure: float) -> float:
        if validation_delay <= 0 and intake_pressure <= 1.0:
            return 0.0
        base_capacity = float(self.validation_staffing_plan.get("base_capacity_h_per_campaign", 1.0))
        target_capacity = float(self.validation_staffing_plan.get("target_capacity_h_per_campaign", base_capacity))
        ramp_gap = max(0.0, target_capacity - base_capacity) / max(target_capacity, 1e-9)
        return self._clip(0.42 * min(validation_delay, 2) / 2.0 + 0.38 * max(0.0, intake_pressure - 1.0) + 0.20 * ramp_gap)

    def _protected_intake_fraction(self, scenario_risk: float, intake_pressure: float) -> float:
        base = float(self.intake_policy.get("campaign_0_max_intake_fraction", 0.55))
        pre_ready = float(self.intake_policy.get("pre_ready_max_intake_fraction", 0.65))
        fraction = pre_ready if scenario_risk < 0.35 else base
        if intake_pressure > 1.0:
            fraction -= min(0.20, 0.10 * (intake_pressure - 1.0) * 2.0)
        if scenario_risk >= 0.55:
            fraction -= 0.10
        return self._clip(fraction, 0.30, 1.0)

    @staticmethod
    def _contingency_actions(
        *,
        catalyst_delay: int,
        oxidant_delay: int,
        validation_delay: int,
        budget_gap: float,
        intake_overload: float,
        acceptance_failure: bool,
    ) -> list[str]:
        actions: list[str] = []
        if catalyst_delay > 0:
            actions.append("延长催化剂压力批次错峰期，启动外部调拨或备用供应商询价。")
        if oxidant_delay > 0:
            actions.append("降低高加药策略默认权重，优先保留副产物验证和氧化剂余量快检。")
        if validation_delay > 0:
            actions.append("临时外包低价值背景验证，内部班次只保留放行门、副产物和催化剂寿命证据。")
        if budget_gap > 0:
            actions.append("把预算拆成验证能力、催化剂库存和氧化剂库存三张批复单，先批最高瓶颈解除项。")
        if intake_overload > 0:
            actions.append("拒绝新增高风险进水，直到待验证队列和催化剂库存恢复到安全线。")
        if acceptance_failure:
            actions.append("阶段验收失败时回退到上一阶段进水比例，并重跑队列规划和资源扩容评分。")
        return actions or ["按原分阶段计划执行，并保持每个 campaign 后滚动复核。"]

    @staticmethod
    def _guardrails(evaluated: list[dict[str, object]]) -> dict[str, object]:
        if not evaluated:
            return {}
        worst = evaluated[0]
        min_fraction = min(float(item["protected_intake_fraction"]) for item in evaluated)
        max_ready = max(int(item["adjusted_ready_campaign"]) for item in evaluated)
        return {
            "max_transition_intake_fraction": round(min_fraction, 2),
            "latest_safe_ready_campaign": max_ready,
            "mandatory_replan_thresholds": [
                "scenario_risk >= 0.55",
                "adjusted_ready_campaign slips by more than 1 campaign",
                "protected_intake_fraction <= 0.45",
                "阶段验收失败",
            ],
            "dominant_worst_case": worst["scenario_id"],
        }

    @staticmethod
    def _trigger_table(evaluated: list[dict[str, object]]) -> list[dict[str, object]]:
        triggers: list[dict[str, object]] = []
        for item in evaluated:
            if float(item["scenario_risk"]) >= 0.35:
                triggers.append(
                    {
                        "scenario_id": item["scenario_id"],
                        "trigger": "scenario_risk >= 0.35",
                        "response": item["contingency_actions"][:2],
                    }
                )
        return triggers

    @staticmethod
    def _issues(worst_case: dict[str, object], robustness_score: float) -> list[QualityIssue]:
        if not worst_case:
            return [
                QualityIssue(
                    sensor="implementation_stress",
                    issue_type="empty_stress_set",
                    severity=Severity.WARNING,
                    message="未提供实施压力情景，无法生成备用路径。",
                )
            ]
        issues: list[QualityIssue] = []
        if float(worst_case.get("scenario_risk", 0.0)) >= 0.55:
            issues.append(
                QualityIssue(
                    sensor="implementation_stress",
                    issue_type="severe_contingency_required",
                    severity=Severity.CRITICAL,
                    message="最坏情景风险过高，必须提前设置备用供应、预算分拆或限流阈值。",
                    evidence={"worst_case": worst_case},
                )
            )
        elif float(worst_case.get("scenario_risk", 0.0)) >= 0.35:
            issues.append(
                QualityIssue(
                    sensor="implementation_stress",
                    issue_type="contingency_required",
                    severity=Severity.WARNING,
                    message="实施计划在最坏情景下需要备用路径，不能只按基准排程执行。",
                    evidence={"worst_case": worst_case},
                )
            )
        if robustness_score < 0.62:
            issues.append(
                QualityIssue(
                    sensor="implementation_stress",
                    issue_type="low_implementation_robustness",
                    severity=Severity.WARNING,
                    message="分阶段实施总体韧性偏低，建议降低过渡期进水比例或增加备用资源。",
                    evidence={"robustness_score": robustness_score},
                )
            )
        return issues

    @staticmethod
    def _recommendations(
        worst_case: dict[str, object],
        guardrails: dict[str, object],
        trigger_table: list[dict[str, object]],
    ) -> list[str]:
        recommendations = [
            (
                f"按最坏情景 {worst_case.get('scenario_id', 'none')} 设置保护性进水上限 "
                f"{guardrails.get('max_transition_intake_fraction', 0.0)}，并保留重算队列的触发点。"
            )
        ]
        recommendations.extend(worst_case.get("contingency_actions", [])[:3] if isinstance(worst_case.get("contingency_actions", []), list) else [])
        if trigger_table:
            recommendations.append("把 scenario_risk >= 0.35 设为自动升级阈值，触发备用供应、预算拆分或限流。")
        recommendations.append("每个 campaign 后重新计算 ready campaign、库存安全线和验证队列，避免阶段计划静态化。")
        return recommendations

    @staticmethod
    def _default_stress_scenarios() -> list[dict[str, object]]:
        return [
            {
                "scenario_id": "on_schedule",
                "description": "资源、预算和验收均按计划推进。",
            },
            {
                "scenario_id": "catalyst_delay",
                "description": "催化剂备件比基准晚到一个 campaign。",
                "catalyst_delay_campaigns": 1,
            },
            {
                "scenario_id": "budget_slow_release",
                "description": "预算只释放 65%，必须分拆批复。",
                "budget_release_fraction": 0.65,
            },
            {
                "scenario_id": "validation_ramp_delay",
                "description": "验证班次爬坡延迟，慢证据队列更容易堆积。",
                "validation_ramp_delay_campaigns": 1,
            },
            {
                "scenario_id": "combined_delay_high_intake",
                "description": "催化剂晚到、验证爬坡延迟，同时进水压力升高。",
                "catalyst_delay_campaigns": 1,
                "validation_ramp_delay_campaigns": 1,
                "budget_release_fraction": 0.75,
                "intake_pressure_multiplier": 1.25,
            },
            {
                "scenario_id": "acceptance_failure",
                "description": "阶段验收失败，需要回退进水比例并重跑队列规划。",
                "acceptance_failure": True,
            },
        ]

    @staticmethod
    def _clip(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
        return max(lo, min(hi, value))

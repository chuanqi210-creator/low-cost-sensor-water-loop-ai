from __future__ import annotations

from collections.abc import Sequence

from water_ai.agents.adaptive_portfolio_agent import AdaptivePortfolioAgent
from water_ai.agents.base import BaseAgent
from water_ai.agents.implementation_stress_test_agent import ImplementationStressTestAgent
from water_ai.agents.long_term_economics_agent import LongTermEconomicsAgent
from water_ai.agents.phased_implementation_agent import PhasedImplementationAgent
from water_ai.agents.queue_planning_agent import QueuePlanningAgent
from water_ai.agents.resource_expansion_agent import ResourceExpansionAgent
from water_ai.domain import AgentReport, QualityIssue, SensorReading, Severity


class ReplanningOrchestratorAgent(BaseAgent):
    """Automatically rerun downstream planning when online control triggers replanning."""

    name = "replanning_orchestrator_agent"

    def __init__(
        self,
        *,
        current_control_state: dict[str, object] | None = None,
        batch_records: list[dict[str, object]] | None = None,
        queue_candidate_plans: list[dict[str, object]] | None = None,
        catalyst_spares_remaining: int = 0,
        oxidant_stock_units_remaining: float = 0.0,
        validation_staff_hours_capacity: float = 5.5,
        campaign_time_budget_min: int = 960,
        budget_limit_increment: float = 1.2,
    ) -> None:
        self.current_control_state = current_control_state or {}
        self.batch_records = batch_records or []
        self.queue_candidate_plans = queue_candidate_plans or []
        self.catalyst_spares_remaining = catalyst_spares_remaining
        self.oxidant_stock_units_remaining = oxidant_stock_units_remaining
        self.validation_staff_hours_capacity = validation_staff_hours_capacity
        self.campaign_time_budget_min = campaign_time_budget_min
        self.budget_limit_increment = budget_limit_increment

    def run(self, readings: Sequence[SensorReading]) -> AgentReport:
        del readings
        replan_required = bool(self.current_control_state.get("replan_required", False))
        if not replan_required:
            return self._no_replan_report()

        queue_report = self._queue_report()
        expansion_report = ResourceExpansionAgent(
            batch_records=self.batch_records,
            catalyst_spares_remaining=self.catalyst_spares_remaining,
            oxidant_stock_units_remaining=self.oxidant_stock_units_remaining,
            validation_staff_hours_capacity=self.validation_staff_hours_capacity,
            campaign_time_budget_min=self.campaign_time_budget_min,
        ).run([])
        economics_report = LongTermEconomicsAgent(
            batch_records=self.batch_records,
            resource_interventions=expansion_report.metrics["ranked_interventions"],
            catalyst_spares_remaining=self.catalyst_spares_remaining,
            oxidant_stock_units_remaining=self.oxidant_stock_units_remaining,
            validation_staff_hours_capacity=self.validation_staff_hours_capacity,
            campaign_time_budget_min=self.campaign_time_budget_min,
        ).run([])
        implementation_report = PhasedImplementationAgent(
            selected_program=economics_report.metrics["selected_program"],
            ranked_programs=economics_report.metrics["ranked_programs"],
            baseline=economics_report.metrics["baseline"],
            planning_assumptions=economics_report.metrics["planning_assumptions"],
            catalyst_spares_remaining=self.catalyst_spares_remaining,
            oxidant_stock_units_remaining=self.oxidant_stock_units_remaining,
            validation_staff_hours_capacity=self.validation_staff_hours_capacity,
            campaign_time_budget_min=self.campaign_time_budget_min,
        ).run([])
        stress_report = ImplementationStressTestAgent(
            selected_program=economics_report.metrics["selected_program"],
            phase_plan=implementation_report.metrics["phase_plan"],
            intake_policy=implementation_report.metrics["intake_policy"],
            inventory_policy=implementation_report.metrics["inventory_policy"],
            validation_staffing_plan=implementation_report.metrics["validation_staffing_plan"],
        ).run([])
        portfolio_report = AdaptivePortfolioAgent(
            ranked_stress_scenarios=stress_report.metrics["ranked_stress_scenarios"],
            guardrails=stress_report.metrics["guardrails"],
            selected_program=economics_report.metrics["selected_program"],
            budget_limit_increment=self.budget_limit_increment,
        ).run([])

        trace = {
            "trigger": self.current_control_state,
            "queue_planning": self._compact_queue(queue_report),
            "resource_expansion": {
                "summary": expansion_report.summary,
                "selected_intervention": expansion_report.metrics["selected_intervention"],
            },
            "long_term_economics": {
                "summary": economics_report.summary,
                "selected_program": economics_report.metrics["selected_program"],
            },
            "phased_implementation": {
                "summary": implementation_report.summary,
                "readiness": implementation_report.metrics["readiness"],
                "intake_policy": implementation_report.metrics["intake_policy"],
            },
            "implementation_stress_test": {
                "summary": stress_report.summary,
                "guardrails": stress_report.metrics["guardrails"],
                "worst_case": stress_report.metrics["worst_case"],
            },
            "adaptive_portfolio": {
                "summary": portfolio_report.summary,
                "selected_portfolio": portfolio_report.metrics["selected_portfolio"],
                "load_control_policy": portfolio_report.metrics["load_control_policy"],
                "budget_sequence": portfolio_report.metrics["budget_sequence"],
            },
        }
        recommendations = self._recommendations(trace)
        issues = self._issues(trace)
        summary = (
            "自动重规划：已重跑队列规划、资源扩容、长期经济性、分阶段实施、压力测试和项目组合；"
            f"新项目包 {trace['adaptive_portfolio']['selected_portfolio'].get('package_id', 'none')}。"
        )
        confidence = round(min(0.95, max(0.20, 0.58 + 0.04 * len(recommendations) - 0.05 * len(issues))), 3)

        return AgentReport(
            agent_name=self.name,
            confidence=confidence,
            summary=summary,
            issues=issues,
            recommendations=recommendations,
            metrics={
                "replan_executed": True,
                "replan_trace": trace,
            },
        )

    def _queue_report(self) -> AgentReport | None:
        if not self.queue_candidate_plans:
            return None
        return QueuePlanningAgent(candidate_plans=self.queue_candidate_plans).run([])

    @staticmethod
    def _compact_queue(report: AgentReport | None) -> dict[str, object]:
        if report is None:
            return {
                "summary": "未提供候选队列，本次自动重规划跳过队列排序。",
                "selected_policy": {},
            }
        return {
            "summary": report.summary,
            "selected_policy": report.metrics["selected_policy"],
        }

    def _no_replan_report(self) -> AgentReport:
        return AgentReport(
            agent_name=self.name,
            confidence=0.72,
            summary="自动重规划：当前在线控制状态未触发 replan，保持滚动监测。",
            issues=[],
            recommendations=["继续使用当前在线项目控制输出；每个 campaign 后重新检查 replan_required。"],
            metrics={
                "replan_executed": False,
                "replan_trace": {"trigger": self.current_control_state},
            },
        )

    @staticmethod
    def _recommendations(trace: dict[str, object]) -> list[str]:
        portfolio = trace["adaptive_portfolio"]["selected_portfolio"]
        load_policy = trace["adaptive_portfolio"]["load_control_policy"]
        budget_sequence = trace["adaptive_portfolio"]["budget_sequence"]
        recommendations = [
            f"采用重规划后的项目包 {portfolio.get('package_id', 'none')}。",
            f"重规划后保护性进水比例为 {load_policy.get('protected_intake_fraction', 0.0)}。",
        ]
        if budget_sequence:
            recommendations.append(
                "重规划预算顺序：" + " -> ".join(str(item["budget_item"]) for item in budget_sequence)
            )
        queue_policy = trace["queue_planning"]["selected_policy"]
        if queue_policy:
            recommendations.append(f"同步采用队列策略 {queue_policy.get('policy_id', 'unknown')}。")
        recommendations.append("把本轮 replan_trace 写回下一轮 OnlineProjectControlAgent 的基准策略。")
        return recommendations

    @staticmethod
    def _issues(trace: dict[str, object]) -> list[QualityIssue]:
        worst_case = trace["implementation_stress_test"]["worst_case"]
        if float(worst_case.get("scenario_risk", 0.0)) >= 0.55:
            return [
                QualityIssue(
                    sensor="replanning",
                    issue_type="severe_replan_residual_risk",
                    severity=Severity.WARNING,
                    message="自动重规划后最坏情景风险仍偏高，需要更强备用资源或进一步限流。",
                    evidence={"worst_case": worst_case},
                )
            ]
        return []

from __future__ import annotations

from collections.abc import Sequence

from water_ai.agents.base import BaseAgent
from water_ai.agents.resource_expansion_agent import ResourceExpansionAgent
from water_ai.domain import AgentReport, QualityIssue, SensorReading, Severity


class LongTermEconomicsAgent(BaseAgent):
    """Evaluate whether resource recovery programs are feasible over multiple campaigns."""

    name = "long_term_economics_agent"

    def __init__(
        self,
        *,
        batch_records: list[dict[str, object]] | None = None,
        resource_interventions: list[dict[str, object]] | None = None,
        catalyst_spares_remaining: int = 0,
        oxidant_stock_units_remaining: float = 0.0,
        validation_staff_hours_capacity: float = 5.5,
        campaign_time_budget_min: int = 960,
        planning_horizon_campaigns: int = 4,
        budget_index_limit: float = 4.2,
        catalyst_lead_time_campaigns: int = 2,
        oxidant_lead_time_campaigns: int = 1,
        validation_staff_ramp_campaigns: int = 1,
        candidate_programs: list[dict[str, object]] | None = None,
    ) -> None:
        self.batch_records = batch_records or []
        self.resource_interventions = resource_interventions or []
        self.catalyst_spares_remaining = catalyst_spares_remaining
        self.oxidant_stock_units_remaining = oxidant_stock_units_remaining
        self.validation_staff_hours_capacity = validation_staff_hours_capacity
        self.campaign_time_budget_min = campaign_time_budget_min
        self.planning_horizon_campaigns = planning_horizon_campaigns
        self.budget_index_limit = budget_index_limit
        self.catalyst_lead_time_campaigns = catalyst_lead_time_campaigns
        self.oxidant_lead_time_campaigns = oxidant_lead_time_campaigns
        self.validation_staff_ramp_campaigns = validation_staff_ramp_campaigns
        self.candidate_programs = candidate_programs or self._default_programs()

    def run(self, readings: Sequence[SensorReading]) -> AgentReport:
        del readings
        context = self._resource_context()
        baseline = context["baseline"]
        ranked_programs = [self._evaluate_program(program, baseline) for program in self.candidate_programs]
        ranked_programs.sort(key=lambda item: item["program_score"], reverse=True)
        selected = ranked_programs[0] if ranked_programs else {}

        issues = self._issues(selected)
        recommendations = [self._sentence(item) for item in ranked_programs[:3]]
        recommendations.extend(self._transition_recommendations(selected))
        summary = (
            f"长期经济性：推荐 {selected.get('program_id', 'none')}，评分 {selected.get('program_score', 0.0)}，"
            f"服务水平 {selected.get('service_level', 0.0)}，成本指数 {selected.get('multi_campaign_cost_index', 0.0)}。"
            if selected
            else "长期经济性：没有候选长期项目可评价。"
        )
        evidence_strength = float(baseline.get("campaign_metrics", {}).get("evidence_strength", 0.0)) if isinstance(baseline, dict) else 0.0
        confidence = round(
            min(0.95, max(0.15, 0.42 + 0.06 * len(ranked_programs) + 0.18 * evidence_strength - 0.06 * len(issues))),
            3,
        )

        return AgentReport(
            agent_name=self.name,
            confidence=confidence,
            summary=summary,
            issues=issues,
            recommendations=recommendations or ["请提供至少一个跨 campaign 的资源与预算项目候选方案。"],
            metrics={
                "baseline": baseline,
                "resource_interventions": context["ranked_interventions"],
                "selected_program": selected,
                "ranked_programs": ranked_programs,
                "planning_assumptions": {
                    "planning_horizon_campaigns": self.planning_horizon_campaigns,
                    "budget_index_limit": self.budget_index_limit,
                    "catalyst_lead_time_campaigns": self.catalyst_lead_time_campaigns,
                    "oxidant_lead_time_campaigns": self.oxidant_lead_time_campaigns,
                    "validation_staff_ramp_campaigns": self.validation_staff_ramp_campaigns,
                },
            },
        )

    def _resource_context(self) -> dict[str, object]:
        report = ResourceExpansionAgent(
            batch_records=self.batch_records,
            catalyst_spares_remaining=self.catalyst_spares_remaining,
            oxidant_stock_units_remaining=self.oxidant_stock_units_remaining,
            validation_staff_hours_capacity=self.validation_staff_hours_capacity,
            campaign_time_budget_min=self.campaign_time_budget_min,
        ).run([])
        ranked_interventions = self.resource_interventions or report.metrics["ranked_interventions"]
        return {
            "baseline": report.metrics["baseline"],
            "ranked_interventions": ranked_interventions,
        }

    def _evaluate_program(
        self,
        program: dict[str, object],
        baseline: dict[str, object],
    ) -> dict[str, object]:
        intervention = self._program_to_intervention(program)
        expansion = ResourceExpansionAgent(
            batch_records=self.batch_records,
            catalyst_spares_remaining=self.catalyst_spares_remaining,
            oxidant_stock_units_remaining=self.oxidant_stock_units_remaining,
            validation_staff_hours_capacity=self.validation_staff_hours_capacity,
            campaign_time_budget_min=self.campaign_time_budget_min,
            candidate_interventions=[intervention],
        ).run([])
        adjusted = expansion.metrics["selected_intervention"]
        baseline_metrics = baseline["campaign_metrics"]

        multi_campaign_cost = self._multi_campaign_cost(program)
        budget_pressure = multi_campaign_cost / max(self.budget_index_limit, 1e-9)
        lead_time_risk = self._lead_time_risk(program, baseline)
        compression_risk = self._compression_risk(program)
        residual_ids = list(adjusted.get("residual_bottleneck_ids", []))
        service_level = self._service_level(adjusted, residual_ids)
        resilience = self._resource_resilience(adjusted)
        residual_operational_risk = self._residual_operational_risk(
            residual_ids=residual_ids,
            lead_time_risk=lead_time_risk,
            budget_pressure=budget_pressure,
            implementation_risk=float(program.get("implementation_risk", 0.0)),
            compression_risk=compression_risk,
        )
        cost_score = 1.0 - min(budget_pressure, 1.6) / 1.6
        bottleneck_relief_score = min(float(adjusted.get("bottleneck_relief", 0.0)) / 2.5, 1.0)
        program_score = self._clip(
            0.36 * service_level
            + 0.19 * bottleneck_relief_score
            + 0.15 * resilience
            + 0.14 * (1.0 - lead_time_risk)
            + 0.12 * cost_score
            + 0.04 * min(float(baseline_metrics.get("success_rate", 0.0)), 1.0)
            - 0.10 * float(program.get("implementation_risk", 0.0))
            - 0.08 * compression_risk
        )

        return {
            "program_id": str(program.get("program_id", "unknown")),
            "description": str(program.get("description", "")),
            "program_score": round(program_score, 3),
            "service_level": round(service_level, 3),
            "resource_resilience": round(resilience, 3),
            "multi_campaign_cost_index": round(multi_campaign_cost, 3),
            "budget_pressure": round(budget_pressure, 3),
            "lead_time_risk": round(lead_time_risk, 3),
            "compression_risk": round(compression_risk, 3),
            "residual_operational_risk": round(residual_operational_risk, 3),
            "bottleneck_relief": adjusted.get("bottleneck_relief", 0.0),
            "adjusted_validation_staff_usage": adjusted.get("adjusted_validation_staff_usage", 0.0),
            "adjusted_time_budget_usage": adjusted.get("adjusted_time_budget_usage", 0.0),
            "adjusted_catalyst_spares_remaining": adjusted.get("adjusted_catalyst_spares_remaining", 0),
            "adjusted_oxidant_stock_units_remaining": adjusted.get("adjusted_oxidant_stock_units_remaining", 0.0),
            "residual_bottleneck_ids": residual_ids,
            "implementation_risk": round(float(program.get("implementation_risk", 0.0)), 3),
            "actions": {
                "validation_hours_delta": round(float(program.get("validation_hours_delta", 0.0)), 3),
                "catalyst_spares_delta": int(program.get("catalyst_spares_delta", 0)),
                "oxidant_stock_delta": round(float(program.get("oxidant_stock_delta", 0.0)), 3),
                "campaign_time_delta_min": int(program.get("campaign_time_delta_min", 0)),
                "validation_minutes_multiplier": round(float(program.get("validation_minutes_multiplier", 1.0)), 3),
            },
        }

    def _program_to_intervention(self, program: dict[str, object]) -> dict[str, object]:
        return {
            "intervention_id": str(program.get("program_id", "unknown")),
            "description": str(program.get("description", "")),
            "validation_hours_delta": float(program.get("validation_hours_delta", 0.0)),
            "catalyst_spares_delta": int(program.get("catalyst_spares_delta", 0)),
            "oxidant_stock_delta": float(program.get("oxidant_stock_delta", 0.0)),
            "campaign_time_delta_min": int(program.get("campaign_time_delta_min", 0)),
            "validation_minutes_multiplier": float(program.get("validation_minutes_multiplier", 1.0)),
            "implementation_cost_index": float(program.get("one_time_cost_index", program.get("implementation_cost_index", 0.0))),
            "implementation_risk": float(program.get("implementation_risk", 0.0)),
        }

    def _multi_campaign_cost(self, program: dict[str, object]) -> float:
        horizon = max(1, self.planning_horizon_campaigns)
        one_time = float(program.get("one_time_cost_index", program.get("implementation_cost_index", 0.0)))
        recurring = float(program.get("recurring_cost_index", 0.0)) * horizon
        catalyst_carrying = max(0, int(program.get("catalyst_spares_delta", 0))) * 0.07 * horizon
        oxidant_carrying = max(0.0, float(program.get("oxidant_stock_delta", 0.0))) * 0.035 * horizon
        window_cost = max(0, int(program.get("campaign_time_delta_min", 0))) / 360.0 * 0.16 * horizon
        governance_cost = max(0.0, 1.0 - float(program.get("validation_minutes_multiplier", 1.0))) * 0.28 * horizon
        return one_time + recurring + catalyst_carrying + oxidant_carrying + window_cost + governance_cost

    def _lead_time_risk(self, program: dict[str, object], baseline: dict[str, object]) -> float:
        bottleneck_ids = {
            str(item.get("bottleneck_id", ""))
            for item in baseline.get("bottlenecks", [])
            if isinstance(item, dict)
        }
        validation_needed = "validation_capacity" in bottleneck_ids
        catalyst_needed = "catalyst_inventory" in bottleneck_ids or self.catalyst_spares_remaining <= 0
        oxidant_needed = "oxidant_stock" in bottleneck_ids or self.oxidant_stock_units_remaining <= 0.7

        validation_delta = float(program.get("validation_hours_delta", 0.0))
        catalyst_delta = int(program.get("catalyst_spares_delta", 0))
        oxidant_delta = float(program.get("oxidant_stock_delta", 0.0))

        components = [
            self._lead_component(
                needed=validation_needed,
                added=validation_delta,
                lead_time=self.validation_staff_ramp_campaigns,
                bridge_inventory=0.0,
                missing_penalty=0.34,
                waiting_weight=0.17,
            ),
            self._lead_component(
                needed=catalyst_needed,
                added=float(catalyst_delta),
                lead_time=self.catalyst_lead_time_campaigns,
                bridge_inventory=float(self.catalyst_spares_remaining),
                missing_penalty=0.42,
                waiting_weight=0.20,
            ),
            self._lead_component(
                needed=oxidant_needed,
                added=oxidant_delta,
                lead_time=self.oxidant_lead_time_campaigns,
                bridge_inventory=self.oxidant_stock_units_remaining,
                missing_penalty=0.28,
                waiting_weight=0.14,
            ),
        ]
        return self._clip(sum(components))

    @staticmethod
    def _lead_component(
        *,
        needed: bool,
        added: float,
        lead_time: int,
        bridge_inventory: float,
        missing_penalty: float,
        waiting_weight: float,
    ) -> float:
        if not needed:
            return 0.03 if added > 0 and lead_time > 1 else 0.0
        if added <= 0:
            return missing_penalty
        bridge_discount = min(max(bridge_inventory, 0.0) * 0.08, 0.16)
        return max(0.03, min(0.36, waiting_weight * max(lead_time, 0) - bridge_discount))

    @staticmethod
    def _compression_risk(program: dict[str, object]) -> float:
        multiplier = float(program.get("validation_minutes_multiplier", 1.0))
        if multiplier >= 0.92:
            return 0.0
        return min(0.42, (0.92 - multiplier) * 1.4)

    def _service_level(self, adjusted: dict[str, object], residual_ids: list[object]) -> float:
        validation_usage = float(adjusted.get("adjusted_validation_staff_usage", 1.0))
        time_usage = float(adjusted.get("adjusted_time_budget_usage", 1.0))
        reserve = self._resource_resilience(adjusted)
        residual_penalty = min(0.72, 0.24 * len(residual_ids))
        return self._clip(
            0.36
            + 0.24 * (1.0 - min(validation_usage, 1.25) / 1.25)
            + 0.20 * (1.0 - min(time_usage, 1.35) / 1.35)
            + 0.20 * reserve
            - residual_penalty
        )

    @staticmethod
    def _resource_resilience(adjusted: dict[str, object]) -> float:
        validation_usage = float(adjusted.get("adjusted_validation_staff_usage", 1.0))
        catalyst_spares = float(adjusted.get("adjusted_catalyst_spares_remaining", 0.0))
        oxidant_stock = float(adjusted.get("adjusted_oxidant_stock_units_remaining", 0.0))
        validation_slack = max(0.0, 1.0 - min(validation_usage, 1.0))
        catalyst_buffer = min(catalyst_spares / 2.0, 1.0)
        oxidant_buffer = min(oxidant_stock / 1.5, 1.0)
        return max(0.0, min(1.0, 0.34 * validation_slack + 0.36 * catalyst_buffer + 0.30 * oxidant_buffer))

    def _residual_operational_risk(
        self,
        *,
        residual_ids: list[object],
        lead_time_risk: float,
        budget_pressure: float,
        implementation_risk: float,
        compression_risk: float,
    ) -> float:
        residual_penalty = min(1.0, len(residual_ids) * 0.32)
        budget_penalty = max(0.0, budget_pressure - 1.0)
        return self._clip(
            0.34 * lead_time_risk
            + 0.25 * residual_penalty
            + 0.18 * min(budget_penalty, 1.0)
            + 0.13 * implementation_risk
            + 0.10 * compression_risk
        )

    def _issues(self, selected: dict[str, object]) -> list[QualityIssue]:
        if not selected:
            return [
                QualityIssue(
                    sensor="long_term_economics",
                    issue_type="empty_program_set",
                    severity=Severity.CRITICAL,
                    message="长期经济性 Agent 未收到候选项目。",
                )
            ]
        issues: list[QualityIssue] = []
        if selected.get("residual_bottleneck_ids"):
            issues.append(
                QualityIssue(
                    sensor="long_term_economics",
                    issue_type="residual_long_term_bottleneck",
                    severity=Severity.WARNING,
                    message="最优长期项目后仍保留运行瓶颈，需降低进水负荷或增加外部资源。",
                    evidence={"selected_program": selected},
                )
            )
        if float(selected.get("lead_time_risk", 0.0)) >= 0.50:
            issues.append(
                QualityIssue(
                    sensor="long_term_economics",
                    issue_type="lead_time_gap",
                    severity=Severity.WARNING,
                    message="采购或人力爬坡提前期会形成过渡期空窗，不能把扩容视为立即可用。",
                    evidence={"selected_program": selected},
                )
            )
        if float(selected.get("budget_pressure", 0.0)) > 1.0:
            issues.append(
                QualityIssue(
                    sensor="long_term_economics",
                    issue_type="budget_pressure",
                    severity=Severity.WARNING,
                    message="多 campaign 项目成本超过当前预算指数，需要分阶段建设或压缩非关键验证项。",
                    evidence={"selected_program": selected},
                )
            )
        return issues

    @staticmethod
    def _sentence(item: dict[str, object]) -> str:
        return (
            f"{item['program_id']}：评分 {item['program_score']}，服务水平 {item['service_level']}，"
            f"成本指数 {item['multi_campaign_cost_index']}，提前期风险 {item['lead_time_risk']}，"
            f"残余瓶颈 {item['residual_bottleneck_ids']}。"
        )

    @staticmethod
    def _transition_recommendations(selected: dict[str, object]) -> list[str]:
        if not selected:
            return []
        recommendations: list[str] = []
        if float(selected.get("lead_time_risk", 0.0)) >= 0.35:
            recommendations.append("提前期过渡期内采用限流、错峰进水和验证优先级调度，不能等备件到场后才处理当前批次。")
        if float(selected.get("budget_pressure", 0.0)) > 0.90:
            recommendations.append("将长期项目拆成验证能力、催化剂库存、氧化剂库存三类预算包，按瓶颈解除贡献分阶段立项。")
        if float(selected.get("compression_risk", 0.0)) > 0.12:
            recommendations.append("压缩验证只能压低价值项目，副产物、催化剂衰减和最终放行门必须保留慢证据闭环。")
        return recommendations

    @staticmethod
    def _default_programs() -> list[dict[str, object]]:
        return [
            {
                "program_id": "minimum_response",
                "description": "只保留滚动监测和临时限流，不主动补齐资源。",
                "one_time_cost_index": 0.05,
                "recurring_cost_index": 0.04,
                "implementation_risk": 0.04,
            },
            {
                "program_id": "validation_capacity_program",
                "description": "优先补齐旁路快检与离线验证班次，缓解软传感器等待慢证据的问题。",
                "validation_hours_delta": 5.0,
                "one_time_cost_index": 0.24,
                "recurring_cost_index": 0.38,
                "implementation_risk": 0.10,
            },
            {
                "program_id": "inventory_buffer_program",
                "description": "优先建立催化剂模块和氧化剂库存缓冲，降低闭环动作被耗材卡住的概率。",
                "catalyst_spares_delta": 2,
                "oxidant_stock_delta": 1.6,
                "one_time_cost_index": 1.10,
                "recurring_cost_index": 0.18,
                "implementation_risk": 0.09,
            },
            {
                "program_id": "balanced_recovery_program",
                "description": "同时补验证班次、催化剂备件、氧化剂库存，并适度扩展运行窗口。",
                "validation_hours_delta": 5.0,
                "catalyst_spares_delta": 1,
                "oxidant_stock_delta": 1.2,
                "campaign_time_delta_min": 180,
                "one_time_cost_index": 1.02,
                "recurring_cost_index": 0.42,
                "implementation_risk": 0.14,
            },
            {
                "program_id": "full_recovery_program",
                "description": "按满负荷连续运行建设完整恢复能力，包括验证班次、备件、氧化剂、运行窗口和低价值验证压缩。",
                "validation_hours_delta": 5.0,
                "catalyst_spares_delta": 2,
                "oxidant_stock_delta": 2.0,
                "campaign_time_delta_min": 360,
                "validation_minutes_multiplier": 0.78,
                "one_time_cost_index": 1.55,
                "recurring_cost_index": 0.64,
                "implementation_risk": 0.22,
            },
        ]

    @staticmethod
    def _clip(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
        return max(lo, min(hi, value))

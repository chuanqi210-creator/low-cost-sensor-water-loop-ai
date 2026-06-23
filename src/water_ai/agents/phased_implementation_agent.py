from __future__ import annotations

from collections.abc import Sequence

from water_ai.agents.base import BaseAgent
from water_ai.agents.long_term_economics_agent import LongTermEconomicsAgent
from water_ai.domain import AgentReport, QualityIssue, SensorReading, Severity


class PhasedImplementationAgent(BaseAgent):
    """Turn a long-term recovery program into an executable staged implementation plan."""

    name = "phased_implementation_agent"

    def __init__(
        self,
        *,
        selected_program: dict[str, object] | None = None,
        ranked_programs: list[dict[str, object]] | None = None,
        baseline: dict[str, object] | None = None,
        planning_assumptions: dict[str, object] | None = None,
        batch_records: list[dict[str, object]] | None = None,
        catalyst_spares_remaining: int = 0,
        oxidant_stock_units_remaining: float = 0.0,
        validation_staff_hours_capacity: float = 5.5,
        campaign_time_budget_min: int = 960,
        planning_horizon_campaigns: int = 4,
        budget_index_limit: float = 4.2,
        catalyst_lead_time_campaigns: int = 2,
        oxidant_lead_time_campaigns: int = 1,
        validation_staff_ramp_campaigns: int = 1,
    ) -> None:
        self.selected_program = selected_program or {}
        self.ranked_programs = ranked_programs or []
        self.baseline = baseline or {}
        self.planning_assumptions = planning_assumptions or {}
        self.batch_records = batch_records or []
        self.catalyst_spares_remaining = catalyst_spares_remaining
        self.oxidant_stock_units_remaining = oxidant_stock_units_remaining
        self.validation_staff_hours_capacity = validation_staff_hours_capacity
        self.campaign_time_budget_min = campaign_time_budget_min
        self.planning_horizon_campaigns = planning_horizon_campaigns
        self.budget_index_limit = budget_index_limit
        self.catalyst_lead_time_campaigns = catalyst_lead_time_campaigns
        self.oxidant_lead_time_campaigns = oxidant_lead_time_campaigns
        self.validation_staff_ramp_campaigns = validation_staff_ramp_campaigns

    def run(self, readings: Sequence[SensorReading]) -> AgentReport:
        del readings
        context = self._implementation_context()
        selected = context["selected_program"]
        phases = self._phase_plan(selected, context["planning_assumptions"])
        inventory_policy = self._inventory_policy(selected, context["planning_assumptions"])
        validation_plan = self._validation_staffing_plan(selected, context["planning_assumptions"])
        intake_policy = self._intake_policy(selected, phases)
        readiness = self._readiness(selected, phases)
        schedule_risk = self._schedule_risk(selected, phases)
        execution_score = self._execution_score(selected, readiness, schedule_risk)
        milestones = self._milestones(phases)
        issues = self._issues(selected, execution_score, schedule_risk)
        recommendations = self._recommendations(selected, phases, intake_policy)

        summary = (
            f"分阶段实施：围绕 {selected.get('program_id', 'none')} 形成 {len(phases)} 个阶段，"
            f"预计第 {readiness['estimated_ready_campaign']} 个 campaign 进入完整能力验证，执行评分 {execution_score}。"
        )
        confidence = round(min(0.95, max(0.18, 0.46 + 0.08 * len(phases) + 0.16 * readiness["implementation_readiness"] - 0.06 * len(issues))), 3)

        return AgentReport(
            agent_name=self.name,
            confidence=confidence,
            summary=summary,
            issues=issues,
            recommendations=recommendations,
            metrics={
                "selected_program_id": selected.get("program_id", "none"),
                "execution_score": execution_score,
                "schedule_risk": schedule_risk,
                "readiness": readiness,
                "phase_plan": phases,
                "milestones": milestones,
                "inventory_policy": inventory_policy,
                "validation_staffing_plan": validation_plan,
                "intake_policy": intake_policy,
                "ranked_programs": context["ranked_programs"],
                "baseline": context["baseline"],
            },
        )

    def _implementation_context(self) -> dict[str, object]:
        if self.selected_program:
            assumptions = {
                "planning_horizon_campaigns": self.planning_horizon_campaigns,
                "budget_index_limit": self.budget_index_limit,
                "catalyst_lead_time_campaigns": self.catalyst_lead_time_campaigns,
                "oxidant_lead_time_campaigns": self.oxidant_lead_time_campaigns,
                "validation_staff_ramp_campaigns": self.validation_staff_ramp_campaigns,
                **self.planning_assumptions,
            }
            return {
                "selected_program": self.selected_program,
                "ranked_programs": self.ranked_programs,
                "baseline": self.baseline,
                "planning_assumptions": assumptions,
            }

        economics = LongTermEconomicsAgent(
            batch_records=self.batch_records,
            catalyst_spares_remaining=self.catalyst_spares_remaining,
            oxidant_stock_units_remaining=self.oxidant_stock_units_remaining,
            validation_staff_hours_capacity=self.validation_staff_hours_capacity,
            campaign_time_budget_min=self.campaign_time_budget_min,
            planning_horizon_campaigns=self.planning_horizon_campaigns,
            budget_index_limit=self.budget_index_limit,
            catalyst_lead_time_campaigns=self.catalyst_lead_time_campaigns,
            oxidant_lead_time_campaigns=self.oxidant_lead_time_campaigns,
            validation_staff_ramp_campaigns=self.validation_staff_ramp_campaigns,
        ).run([])
        return {
            "selected_program": economics.metrics["selected_program"],
            "ranked_programs": economics.metrics["ranked_programs"],
            "baseline": economics.metrics["baseline"],
            "planning_assumptions": economics.metrics["planning_assumptions"],
        }

    def _phase_plan(self, selected: dict[str, object], assumptions: dict[str, object]) -> list[dict[str, object]]:
        actions = self._actions(selected)
        if self._is_monitoring_only(actions):
            return [
                {
                    "phase_id": "phase_0_monitoring",
                    "campaign_start": 0,
                    "campaign_end": self.planning_horizon_campaigns,
                    "objective": "维持滚动监测和安全门，不启动额外资源建设。",
                    "actions": ["保持现有低成本传感、软传感估计和最终放行门。"],
                    "prerequisites": [],
                    "acceptance_criteria": ["连续 campaign 无验证、时间、库存瓶颈。"],
                    "risk_controls": ["若出现催化剂库存或验证工时 warning，自动升级到分阶段补库计划。"],
                    "expected_bottlenecks": [],
                    "readiness_gain": 0.12,
                }
            ]

        catalyst_lead = int(assumptions.get("catalyst_lead_time_campaigns", self.catalyst_lead_time_campaigns))
        oxidant_lead = int(assumptions.get("oxidant_lead_time_campaigns", self.oxidant_lead_time_campaigns))
        validation_ramp = int(assumptions.get("validation_staff_ramp_campaigns", self.validation_staff_ramp_campaigns))
        ready_campaign = max(
            catalyst_lead if int(actions["catalyst_spares_delta"]) > 0 else 0,
            oxidant_lead if float(actions["oxidant_stock_delta"]) > 0 else 0,
            validation_ramp if float(actions["validation_hours_delta"]) > 0 else 0,
            1,
        )

        phases: list[dict[str, object]] = [
            {
                "phase_id": "phase_0_transition_control",
                "campaign_start": 0,
                "campaign_end": 0,
                "objective": "在资源到位前防止低成本传感闭环被验证、备件或时间瓶颈压垮。",
                "actions": [
                    "限制新批次进水并保留回流/暂存缓冲。",
                    "把旁路验证优先级集中到放行门、副产物、催化剂寿命和高风险批次。",
                    "冻结非关键验证压缩，避免压掉安全门慢证据。",
                ],
                "prerequisites": ["确认当前瓶颈清单、库存台账和验证人员排班。"],
                "acceptance_criteria": ["待验证批次不过夜堆积。", "所有放行批次保留最终安全门证据。"],
                "risk_controls": ["若催化剂备件为 0，禁止把更换作为默认兜底动作。"],
                "expected_bottlenecks": self._residual_or_baseline_bottlenecks(selected),
                "readiness_gain": 0.16,
            }
        ]

        if float(actions["validation_hours_delta"]) > 0 or float(actions["oxidant_stock_delta"]) > 0:
            phases.append(
                {
                    "phase_id": "phase_1_validation_and_oxidant_ramp",
                    "campaign_start": 1,
                    "campaign_end": max(1, validation_ramp, oxidant_lead),
                    "objective": "先补最快见效的验证能力和氧化剂库存，缩短软传感等待慢证据的队列。",
                    "actions": [
                        f"验证工时容量增加 {actions['validation_hours_delta']} h/campaign。",
                        f"氧化剂库存补充 {actions['oxidant_stock_delta']} 单位。",
                        "建立验证优先级队列：放行门、副产物、催化剂寿命高于低价值背景项。",
                    ],
                    "prerequisites": ["快检/离线验证 SOP 与数据回写字段固定。", "氧化剂补库批号和副产物复核规则确认。"],
                    "acceptance_criteria": ["验证工时占用降到 0.85 以下。", "氧化剂库存高于安全库存线。"],
                    "risk_controls": ["新增班次未稳定前继续错峰进水。"],
                    "expected_bottlenecks": ["catalyst_inventory"] if int(actions["catalyst_spares_delta"]) > 0 and catalyst_lead > 1 else [],
                    "readiness_gain": 0.24,
                }
            )

        if int(actions["catalyst_spares_delta"]) > 0:
            phases.append(
                {
                    "phase_id": "phase_2_catalyst_procurement_lock",
                    "campaign_start": 1,
                    "campaign_end": max(1, catalyst_lead),
                    "objective": "把催化剂备件从临时补救转为安全库存，避免闭环控制被耗材提前期卡住。",
                    "actions": [
                        f"采购或调拨 {actions['catalyst_spares_delta']} 个催化剂模块备件。",
                        "设置催化剂寿命低于 0.45 的预防性维护清单。",
                        "到货前维持高风险批次限流，避免连续催化剂压力批次排队。",
                    ],
                    "prerequisites": ["确认催化剂兼容性、活化/验收程序和供应提前期。"],
                    "acceptance_criteria": ["催化剂备件库存不低于安全库存。", "更换后 commissioning 置信度满足放行前要求。"],
                    "risk_controls": ["若到货延迟，自动切换到较低进水比例并延长暂存窗口。"],
                    "expected_bottlenecks": ["catalyst_inventory"],
                    "readiness_gain": 0.26,
                }
            )

        phases.append(
            {
                "phase_id": "phase_3_integrated_ramp_up",
                "campaign_start": ready_campaign,
                "campaign_end": min(self.planning_horizon_campaigns, ready_campaign + 1),
                "objective": "在资源到位后进行完整能力试运行，验证循环、软传感、慢证据和闭环控制的联合稳定性。",
                "actions": [
                    "逐步恢复进水比例到 1.0。",
                    "复核 validation_staff_usage、time_budget_usage、库存余量和最终放行门。",
                    "仅压缩低价值验证项，保留副产物、催化剂衰减和最终放行慢证据。",
                ],
                "prerequisites": ["验证班次、氧化剂库存、催化剂备件和运行窗口均达到目标配置。"],
                "acceptance_criteria": ["连续两个 campaign 无 critical 瓶颈。", "放行成功率不低于 0.95。", "预算偏差不超过 10%。"],
                "risk_controls": ["若 time_budget_usage 仍超过 0.90，保留错峰进水并重新计算队列。"],
                "expected_bottlenecks": list(selected.get("residual_bottleneck_ids", [])) if isinstance(selected.get("residual_bottleneck_ids", []), list) else [],
                "readiness_gain": 0.34,
            }
        )
        return phases

    def _inventory_policy(self, selected: dict[str, object], assumptions: dict[str, object]) -> dict[str, object]:
        actions = self._actions(selected)
        catalyst_delta = max(0, int(actions["catalyst_spares_delta"]))
        oxidant_delta = max(0.0, float(actions["oxidant_stock_delta"]))
        catalyst_lead = int(assumptions.get("catalyst_lead_time_campaigns", self.catalyst_lead_time_campaigns))
        oxidant_lead = int(assumptions.get("oxidant_lead_time_campaigns", self.oxidant_lead_time_campaigns))
        return {
            "catalyst_safety_stock": max(1, catalyst_delta),
            "catalyst_reorder_point": max(1, catalyst_lead),
            "catalyst_order_quantity": max(1, catalyst_delta),
            "oxidant_safety_stock_units": round(max(0.8, 0.6 * oxidant_delta), 3),
            "oxidant_reorder_point_campaigns": max(1, oxidant_lead),
            "oxidant_order_quantity_units": round(max(1.0, oxidant_delta), 3),
            "stockout_action": "进入限流和错峰验证，禁止把更换或加药作为默认兜底。",
        }

    def _validation_staffing_plan(self, selected: dict[str, object], assumptions: dict[str, object]) -> dict[str, object]:
        actions = self._actions(selected)
        delta = float(actions["validation_hours_delta"])
        ramp = int(assumptions.get("validation_staff_ramp_campaigns", self.validation_staff_ramp_campaigns))
        return {
            "base_capacity_h_per_campaign": round(self.validation_staff_hours_capacity, 3),
            "target_capacity_h_per_campaign": round(self.validation_staff_hours_capacity + delta, 3),
            "ramp_campaigns": ramp if delta > 0 else 0,
            "priority_order": ["release_gate", "byproduct_risk", "catalyst_lifecycle", "matrix_shock", "low_value_background"],
            "qa_rule": "压缩验证只能压低价值背景项，不压最终放行门、副产物和催化剂寿命证据。",
        }

    def _intake_policy(self, selected: dict[str, object], phases: list[dict[str, object]]) -> dict[str, object]:
        ready_campaign = int(phases[-1]["campaign_start"]) if phases else 0
        lead_time_risk = float(selected.get("lead_time_risk", 0.0))
        budget_pressure = float(selected.get("budget_pressure", 0.0))
        transition_fraction = 0.5 if lead_time_risk >= 0.50 else 0.65
        if budget_pressure > 1.0:
            transition_fraction = min(transition_fraction, 0.55)
        return {
            "campaign_0_max_intake_fraction": round(transition_fraction, 2),
            "pre_ready_max_intake_fraction": round(min(0.75, transition_fraction + 0.15), 2),
            "post_ready_max_intake_fraction": 1.0,
            "estimated_ready_campaign": ready_campaign,
            "release_gate_mode": "strict_until_two_stable_campaigns",
            "queue_rule": "高风险批次错峰，不连续安排催化剂压力批次。",
        }

    def _readiness(self, selected: dict[str, object], phases: list[dict[str, object]]) -> dict[str, object]:
        ready_campaign = int(phases[-1]["campaign_start"]) if phases else 0
        readiness_gain = min(1.0, sum(float(phase.get("readiness_gain", 0.0)) for phase in phases))
        lead_time_penalty = 0.34 * float(selected.get("lead_time_risk", 0.0))
        budget_penalty = 0.22 * max(0.0, float(selected.get("budget_pressure", 0.0)) - 1.0)
        residual_penalty = 0.22 * float(selected.get("residual_operational_risk", 0.0))
        implementation_readiness = self._clip(readiness_gain - lead_time_penalty - budget_penalty - residual_penalty)
        return {
            "estimated_ready_campaign": ready_campaign,
            "readiness_gain": round(readiness_gain, 3),
            "implementation_readiness": round(implementation_readiness, 3),
        }

    def _schedule_risk(self, selected: dict[str, object], phases: list[dict[str, object]]) -> float:
        overlap_penalty = 0.04 * max(0, len(phases) - 3)
        return round(
            self._clip(
                0.42 * float(selected.get("lead_time_risk", 0.0))
                + 0.22 * max(0.0, float(selected.get("budget_pressure", 0.0)) - 1.0)
                + 0.22 * float(selected.get("residual_operational_risk", 0.0))
                + 0.10 * float(selected.get("compression_risk", 0.0))
                + overlap_penalty
            ),
            3,
        )

    def _execution_score(self, selected: dict[str, object], readiness: dict[str, object], schedule_risk: float) -> float:
        program_score = float(selected.get("program_score", 0.0))
        service_level = float(selected.get("service_level", 0.0))
        return round(
            self._clip(
                0.34 * program_score
                + 0.24 * service_level
                + 0.24 * float(readiness["implementation_readiness"])
                + 0.18 * (1.0 - schedule_risk)
            ),
            3,
        )

    @staticmethod
    def _milestones(phases: list[dict[str, object]]) -> list[dict[str, object]]:
        return [
            {
                "milestone_id": f"{phase['phase_id']}_acceptance",
                "due_campaign": phase["campaign_end"],
                "criteria": phase["acceptance_criteria"],
            }
            for phase in phases
        ]

    def _issues(self, selected: dict[str, object], execution_score: float, schedule_risk: float) -> list[QualityIssue]:
        issues: list[QualityIssue] = []
        if float(selected.get("lead_time_risk", 0.0)) >= 0.50:
            issues.append(
                QualityIssue(
                    sensor="implementation",
                    issue_type="transition_gap",
                    severity=Severity.WARNING,
                    message="资源到位前存在提前期空窗，必须通过限流、错峰和严格放行门过渡。",
                    evidence={"selected_program": selected},
                )
            )
        if float(selected.get("budget_pressure", 0.0)) > 1.0:
            issues.append(
                QualityIssue(
                    sensor="implementation",
                    issue_type="staged_budget_required",
                    severity=Severity.WARNING,
                    message="长期项目预算压力超过 1，需要拆成阶段性预算包和验收节点。",
                    evidence={"budget_pressure": selected.get("budget_pressure")},
                )
            )
        if selected.get("residual_bottleneck_ids"):
            issues.append(
                QualityIssue(
                    sensor="implementation",
                    issue_type="implementation_leaves_bottleneck",
                    severity=Severity.WARNING,
                    message="分阶段计划对应的长期项目仍有残余瓶颈，需保留限流或重新计算资源组合。",
                    evidence={"residual_bottleneck_ids": selected.get("residual_bottleneck_ids")},
                )
            )
        if execution_score < 0.45 or schedule_risk > 0.70:
            issues.append(
                QualityIssue(
                    sensor="implementation",
                    issue_type="weak_execution_plan",
                    severity=Severity.CRITICAL,
                    message="当前实施计划执行评分偏低，不宜直接恢复满负荷进水。",
                    evidence={"execution_score": execution_score, "schedule_risk": schedule_risk},
                )
            )
        return issues

    @staticmethod
    def _recommendations(
        selected: dict[str, object],
        phases: list[dict[str, object]],
        intake_policy: dict[str, object],
    ) -> list[str]:
        recommendations = [
            (
                f"按 {selected.get('program_id', 'none')} 分阶段实施：第 0 个 campaign 先限流到 "
                f"{int(float(intake_policy['campaign_0_max_intake_fraction']) * 100)}%，资源到位前继续错峰。"
            )
        ]
        recommendations.extend(
            f"{phase['phase_id']}：{phase['objective']}"
            for phase in phases[:3]
        )
        recommendations.append("每个阶段必须用验证工时占用、时间预算占用、库存余量和放行安全门作为验收指标。")
        return recommendations

    @staticmethod
    def _actions(selected: dict[str, object]) -> dict[str, object]:
        actions = selected.get("actions", {})
        if not isinstance(actions, dict):
            actions = {}
        return {
            "validation_hours_delta": float(actions.get("validation_hours_delta", 0.0)),
            "catalyst_spares_delta": int(actions.get("catalyst_spares_delta", 0)),
            "oxidant_stock_delta": float(actions.get("oxidant_stock_delta", 0.0)),
            "campaign_time_delta_min": int(actions.get("campaign_time_delta_min", 0)),
            "validation_minutes_multiplier": float(actions.get("validation_minutes_multiplier", 1.0)),
        }

    @staticmethod
    def _is_monitoring_only(actions: dict[str, object]) -> bool:
        return (
            float(actions["validation_hours_delta"]) <= 0
            and int(actions["catalyst_spares_delta"]) <= 0
            and float(actions["oxidant_stock_delta"]) <= 0
            and int(actions["campaign_time_delta_min"]) <= 0
            and float(actions["validation_minutes_multiplier"]) >= 0.999
        )

    @staticmethod
    def _residual_or_baseline_bottlenecks(selected: dict[str, object]) -> list[object]:
        residual = selected.get("residual_bottleneck_ids", [])
        return list(residual) if isinstance(residual, list) and residual else ["validation_capacity", "campaign_time_budget", "catalyst_inventory"]

    @staticmethod
    def _clip(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
        return max(lo, min(hi, value))

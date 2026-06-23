from __future__ import annotations

from collections.abc import Sequence

from water_ai.agents.base import BaseAgent
from water_ai.domain import AgentReport, QualityIssue, SensorReading, Severity


class MainChainReconnectionAgent(BaseAgent):
    """Audit whether core model patches are consumed by the live Agent1-9 chain."""

    name = "main_chain_reconnection_agent"

    def __init__(
        self,
        *,
        soft_sensor_report: AgentReport | None = None,
        mechanism_report: AgentReport | None = None,
        fault_report: AgentReport | None = None,
        control_report: AgentReport | None = None,
        cost_safety_report: AgentReport | None = None,
        arbitration_report: AgentReport | None = None,
        kg_reasoning_metrics: dict[str, object] | None = None,
        multi_facility_control_metrics: dict[str, object] | None = None,
        grey_box_physics_metrics: dict[str, object] | None = None,
        soft_sensor_matrix_metrics: dict[str, object] | None = None,
        engineering_constraints_metrics: dict[str, object] | None = None,
    ) -> None:
        self.soft_sensor_report = soft_sensor_report
        self.mechanism_report = mechanism_report
        self.fault_report = fault_report
        self.control_report = control_report
        self.cost_safety_report = cost_safety_report
        self.arbitration_report = arbitration_report
        self.kg_reasoning_metrics = kg_reasoning_metrics or {}
        self.multi_facility_control_metrics = multi_facility_control_metrics or {}
        self.grey_box_physics_metrics = grey_box_physics_metrics or {}
        self.soft_sensor_matrix_metrics = soft_sensor_matrix_metrics or {}
        self.engineering_constraints_metrics = engineering_constraints_metrics or {}

    def run(self, readings: Sequence[SensorReading]) -> AgentReport:
        del readings
        coupling_table = self._coupling_table()
        readiness = self._readiness(coupling_table)
        issues = self._issues(coupling_table, readiness)
        recommendations = self._recommendations(coupling_table, readiness)
        summary = (
            f"主链回接审计：{readiness['main_chain_reconnection_status']}；"
            f"prior_consumption_rate={readiness['main_chain_prior_consumption_rate']:.3f}。"
        )
        confidence = round(
            min(0.91, max(0.24, 0.38 + 0.42 * readiness["main_chain_reconnection_score"] - 0.035 * len(issues))),
            3,
        )
        return AgentReport(
            agent_name=self.name,
            confidence=confidence,
            summary=summary,
            issues=issues,
            recommendations=recommendations,
            metrics={
                "method_contract": self._method_contract(),
                "coupling_table": coupling_table,
                "readiness": readiness,
                "agent50_writeback": self._agent50_writeback(readiness),
            },
        )

    def _coupling_table(self) -> list[dict[str, object]]:
        soft_metrics = self._metrics(self.soft_sensor_report)
        mech_metrics = self._metrics(self.mechanism_report)
        fault_metrics = self._metrics(self.fault_report)
        control_metrics = self._metrics(self.control_report)
        cost_metrics = self._metrics(self.cost_safety_report)
        arb_metrics = self._metrics(self.arbitration_report)
        layout_context = soft_metrics.get("layout_context", {})
        layout_context = layout_context if isinstance(layout_context, dict) else {}
        grey_context = soft_metrics.get("grey_box_prior_context", {})
        grey_context = grey_context if isinstance(grey_context, dict) else {}
        kg_reasoning = mech_metrics.get("kg_reasoning", {})
        kg_reasoning = kg_reasoning if isinstance(kg_reasoning, dict) else {}
        evaluated_actions = cost_metrics.get("evaluated_actions", [])
        evaluated_actions = evaluated_actions if isinstance(evaluated_actions, list) else []
        engineering_used = arb_metrics.get("engineering_constraints_used", {})
        engineering_used = engineering_used if isinstance(engineering_used, dict) else {}
        final_plan = arb_metrics.get("final_plan", [])
        final_plan = final_plan if isinstance(final_plan, list) else []
        agent49_joint_actions = self.multi_facility_control_metrics.get("joint_action_matrix", [])
        agent49_joint_actions = agent49_joint_actions if isinstance(agent49_joint_actions, list) else []

        return [
            {
                "link_id": "L0_agent54_layout_to_agent2_soft_sensor",
                "source_agent": "Agent54/Agent48",
                "target_agent": "Agent2_SoftSensor",
                "consumed": layout_context.get("layout_status") not in {None, "no_layout_interface"},
                "evidence": {
                    "layout_status": layout_context.get("layout_status", "not_available"),
                    "node_specific_value_rate": layout_context.get("node_specific_value_rate", 0.0),
                },
                "writeback_boundary": "layout fallback can inform uncertainty; field node values required for deployment claims",
            },
            {
                "link_id": "L1_agent53_grey_box_to_agent2_soft_sensor",
                "source_agent": "Agent53",
                "target_agent": "Agent2_SoftSensor",
                "consumed": bool(grey_context.get("can_use_as_soft_sensor_prior", False)),
                "evidence": {
                    "grey_box_status": grey_context.get("grey_box_status", "not_available"),
                    "grey_box_residual_prior": grey_context.get("grey_box_residual_prior", 0.0),
                    "grey_box_byproduct_prior": grey_context.get("grey_box_byproduct_prior", 0.0),
                },
                "writeback_boundary": "synthetic grey-box prior can raise uncertainty and byproduct guard only; no release authorization",
            },
            {
                "link_id": "L2_agent56_kg_to_agent3_mechanism",
                "source_agent": "Agent56",
                "target_agent": "Agent3_Mechanism",
                "consumed": bool(kg_reasoning.get("evidence_paths")),
                "evidence": {
                    "evidence_path_count": len(kg_reasoning.get("evidence_paths", []))
                    if isinstance(kg_reasoning.get("evidence_paths", []), list)
                    else 0,
                },
                "writeback_boundary": "literature/synthetic KG evidence can explain hypotheses; field edges required for claims",
            },
            {
                "link_id": "L3_agent56_kg_to_agent5_control",
                "source_agent": "Agent56",
                "target_agent": "Agent5_ControlStrategy",
                "consumed": control_metrics.get("knowledge_reasoning_source") == "typed_kg_action_constraint_patch",
                "evidence": {
                    "knowledge_reasoning_source": control_metrics.get("knowledge_reasoning_source", "not_available"),
                    "knowledge_action_biases": control_metrics.get("knowledge_action_biases", {}),
                },
                "writeback_boundary": "KG action constraints can alter scores only; no actuator writeback",
            },
            {
                "link_id": "L4_agent55_engineering_to_agent9_cost_safety",
                "source_agent": "Agent55",
                "target_agent": "Agent9_CostSafety",
                "consumed": any(
                    isinstance(row, dict) and bool(row.get("engineering_constraint_patch"))
                    for row in evaluated_actions
                ),
                "evidence": {
                    "evaluated_action_count": len(evaluated_actions),
                    "patched_action_count": sum(
                        1
                        for row in evaluated_actions
                        if isinstance(row, dict) and bool(row.get("engineering_constraint_patch"))
                    ),
                },
                "writeback_boundary": "engineering patch affects objective scoring, not direct actuator execution",
            },
            {
                "link_id": "L5_agent55_engineering_to_agent10_arbitration",
                "source_agent": "Agent55",
                "target_agent": "Agent10_Arbitration",
                "consumed": bool(engineering_used.get("available", False)),
                "evidence": engineering_used,
                "writeback_boundary": "arbitration can block actions; field execution replay required before execution",
            },
            {
                "link_id": "L6_agent49_multi_facility_to_agent10_arbitration",
                "source_agent": "Agent49",
                "target_agent": "Agent10_Arbitration",
                "consumed": any(
                    isinstance(row, dict) and row.get("joint_action_id")
                    for row in evaluated_actions
                ),
                "evidence": {
                    "agent49_joint_action_count": len(agent49_joint_actions),
                    "cost_safety_joint_action_count": sum(
                        1 for row in evaluated_actions if isinstance(row, dict) and row.get("joint_action_id")
                    ),
                    "arbitration_final_plan_count": len(final_plan),
                    "final_plan_contains_joint_action": any(
                        isinstance(row, dict) and row.get("joint_action_id")
                        for row in final_plan
                    ),
                },
                "writeback_boundary": "Agent49 remains a collaborative policy candidate until replay and arbitration bridge are explicit",
            },
        ]

    @staticmethod
    def _readiness(coupling_table: list[dict[str, object]]) -> dict[str, object]:
        consumed_count = sum(1 for row in coupling_table if bool(row["consumed"]))
        rate = consumed_count / max(1, len(coupling_table))
        critical_links = {"L1_agent53_grey_box_to_agent2_soft_sensor", "L3_agent56_kg_to_agent5_control"}
        critical_ready = all(
            bool(row["consumed"])
            for row in coupling_table
            if str(row["link_id"]) in critical_links
        )
        score = round(0.58 * rate + 0.22 * float(critical_ready) + 0.20 * float(consumed_count >= 5), 3)
        if rate >= 0.84 and critical_ready:
            status = "synthetic_main_chain_reconnection_ready_needs_field_replay"
        else:
            status = "main_chain_reconnection_gaps_remain"
        return {
            "main_chain_reconnection_status": status,
            "main_chain_reconnection_score": score,
            "main_chain_prior_consumption_rate": round(rate, 3),
            "consumed_link_count": consumed_count,
            "total_link_count": len(coupling_table),
            "critical_links_ready": critical_ready,
            "can_update_agent50_priority": status.startswith("synthetic_"),
            "can_write_to_actuator": False,
            "can_write_to_release_gate": False,
            "next_recommended_core_action": "field_validation_queue_alignment_or_live_agent49_arbitration_bridge",
        }

    @staticmethod
    def _issues(coupling_table: list[dict[str, object]], readiness: dict[str, object]) -> list[QualityIssue]:
        issues: list[QualityIssue] = []
        for row in coupling_table:
            if not row["consumed"]:
                issues.append(
                    QualityIssue(
                        sensor="main_chain_reconnection",
                        issue_type=str(row["link_id"]),
                        severity=Severity.INFO,
                        message=f"{row['source_agent']} 尚未被 {row['target_agent']} 主链消费。",
                        evidence=row,
                    )
                )
        if readiness["can_write_to_actuator"] is False:
            issues.append(
                QualityIssue(
                    sensor="main_chain_reconnection",
                    issue_type="synthetic_reconnection_not_execution_ready",
                    severity=Severity.WARNING,
                    message="主链回接只证明 synthetic prior 已进入推理链，不能替代 field replay 或执行器许可。",
                    evidence=readiness,
                )
            )
        return issues

    @staticmethod
    def _recommendations(coupling_table: list[dict[str, object]], readiness: dict[str, object]) -> list[str]:
        recs = [
            "后续所有新增核心 agent 必须进入 coupling_table，证明是否被主闭环消费，而不是只生成独立报告。",
            "当前回接只允许改变软传感不确定性、机理证据、动作排序、成本安全评分和仲裁阻断。",
        ]
        open_links = [row for row in coupling_table if not row["consumed"]]
        if open_links:
            recs.append(f"优先补齐未消费链路：{', '.join(str(row['link_id']) for row in open_links)}。")
        if readiness["main_chain_prior_consumption_rate"] >= 0.84:
            recs.append("下一步应把 field_validation_queue 与真实数据接口逐项对齐，避免继续堆 synthetic prior。")
        return recs

    @staticmethod
    def _method_contract() -> dict[str, object]:
        return {
            "upgrade_id": "P8_cross_agent_core_reconnection",
            "borrowed_from": [
                "model integration audit",
                "agentic pipeline contract testing",
                "evidence-to-action traceability",
            ],
            "reality_mapping": "检查各核心模型成果是否真正进入低成本传感闭环主链，而不是停留在独立实验报告。",
            "data_needs": [
                "soft_sensor_layout_context",
                "soft_sensor_grey_box_prior_context",
                "mechanism_kg_reasoning",
                "control_knowledge_reasoning_source",
                "cost_safety_engineering_patch",
                "arbitration_engineering_constraints_used",
                "agent49_joint_action_matrix",
                "arbitration_joint_action_bridge",
            ],
            "implementation_path": [
                "src/water_ai/agents/soft_sensor_agent.py",
                "src/water_ai/agents/main_chain_reconnection_agent.py",
                "experiments/run_agent57_main_chain_reconnection.py",
            ],
            "evaluation_metrics": [
                "main_chain_prior_consumption_rate",
                "consumed_link_count",
                "critical_links_ready",
                "can_write_to_actuator",
            ],
            "failure_boundary": "主链回接只证明模型 prior 被消费；没有 field replay 时不能证明现场控制效果。",
        }

    @staticmethod
    def _agent50_writeback(readiness: dict[str, object]) -> dict[str, object]:
        return {
            "allowed_writeback": [
                "main_chain_reconnection_status",
                "core_prior_consumption_metrics",
                "P8_completion_status_for_governance",
            ],
            "blocked_writeback": [
                "actuator_policy",
                "release_gate_policy",
                "field_validation_claim",
            ],
            "can_advance_governance_priority": bool(readiness["can_update_agent50_priority"]),
            "policy_effect": (
                "move_to_field_validation_queue_alignment"
                if readiness["can_update_agent50_priority"]
                else "keep_P8_until_critical_prior_links_are_consumed"
            ),
        }

    @staticmethod
    def _metrics(report: AgentReport | None) -> dict[str, object]:
        if report is None:
            return {}
        return report.metrics

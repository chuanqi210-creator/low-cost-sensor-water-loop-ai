from __future__ import annotations

from collections.abc import Sequence

from water_ai.agents.base import BaseAgent
from water_ai.domain import AgentReport, QualityIssue, SensorReading, Severity
from water_ai.knowledge import build_knowledge_graph, reason_over_knowledge_graph


class KnowledgeGraphReasoningAgent(BaseAgent):
    """Couple the curated KG to mechanism evidence and control action constraints."""

    name = "knowledge_graph_reasoning_agent"

    def __init__(
        self,
        *,
        state_estimate: dict[str, float] | None = None,
        dq_issue_types: set[str] | None = None,
        soft_issue_types: set[str] | None = None,
        data_origin: str = "literature_informed_simulation_kg",
        min_score: float = 0.58,
    ) -> None:
        self.state_estimate = state_estimate or {}
        self.dq_issue_types = dq_issue_types or set()
        self.soft_issue_types = soft_issue_types or set()
        self.data_origin = data_origin
        self.min_score = min_score

    def run(self, readings: Sequence[SensorReading]) -> AgentReport:
        del readings
        graph = build_knowledge_graph()
        reasoning = reason_over_knowledge_graph(
            self.state_estimate,
            dq_issue_types=self.dq_issue_types,
            soft_issue_types=self.soft_issue_types,
            min_score=self.min_score,
        )
        retrospective = self._chain_retrospective(reasoning)
        readiness = self._readiness(reasoning, retrospective)
        issues = self._issues(reasoning, retrospective, readiness)
        recommendations = self._recommendations(retrospective, reasoning)
        summary = (
            f"可推理知识图谱：{readiness['kg_reasoning_status']}；"
            f"evidence_paths={readiness['evidence_path_count']}，"
            f"action_constraints={readiness['action_constraint_count']}。"
        )
        confidence = round(
            min(0.91, max(0.22, 0.38 + 0.42 * readiness["kg_reasoning_score"] - 0.035 * len(issues))),
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
                "kg_graph": graph,
                "kg_reasoning": reasoning,
                "agent_chain_retrospective": retrospective,
                "action_constraint_patch": reasoning["action_constraint_patch"],
                "mechanism_evidence_paths": reasoning["evidence_paths"],
                "field_validation_queue": reasoning["field_validation_queue"],
                "readiness": readiness,
                "agent50_writeback": self._agent50_writeback(readiness),
            },
        )

    def _readiness(self, reasoning: dict[str, object], retrospective: list[dict[str, object]]) -> dict[str, object]:
        reasoning_ready = reasoning.get("readiness", {})
        reasoning_ready = reasoning_ready if isinstance(reasoning_ready, dict) else {}
        evidence_traceability = float(reasoning_ready.get("evidence_traceability", 0.0))
        constraint_hit_rate = float(reasoning_ready.get("constraint_hit_rate", 0.0))
        field_ratio = float(reasoning_ready.get("field_supported_edge_ratio", 0.0))
        root_gap_resolved = any(
            item["gap_id"] == "G0_flat_knowledge_not_coupled_to_decisions"
            and item["after_agent56_status"] == "patched_by_typed_kg_reasoning"
            for item in retrospective
        )
        score = round(
            0.28 * evidence_traceability
            + 0.24 * constraint_hit_rate
            + 0.18 * float(root_gap_resolved)
            + 0.15 * min(1.0, len(reasoning.get("evidence_paths", [])) / 5.0)
            + 0.15 * field_ratio,
            3,
        )
        status = "kg_reasoning_patch_ready_needs_field_supported_edges" if root_gap_resolved else "kg_reasoning_patch_incomplete"
        if field_ratio > 0.0 and score >= 0.78:
            status = "field_supported_kg_reasoning_candidate_ready"
        return {
            "kg_reasoning_status": status,
            "kg_reasoning_score": score,
            "evidence_path_count": int(reasoning_ready.get("evidence_path_count", 0)),
            "action_constraint_count": int(reasoning_ready.get("action_constraint_count", 0)),
            "field_supported_edge_ratio": field_ratio,
            "evidence_traceability": evidence_traceability,
            "constraint_hit_rate": constraint_hit_rate,
            "claim_verification_pass_rate": float(reasoning_ready.get("claim_verification_pass_rate", 0.0)),
            "root_gap_resolved": root_gap_resolved,
            "can_update_mechanism_evidence": bool(reasoning_ready.get("can_update_mechanism_evidence", False)),
            "can_update_action_bias_prior": bool(reasoning_ready.get("can_update_action_bias_prior", False)),
            "can_write_to_actuator": False,
            "can_write_to_release_gate": False,
            "next_recommended_core_action": "reconnect_grey_box_and_layout_priors_to_live_soft_sensor_or_agent49",
        }

    @staticmethod
    def _chain_retrospective(reasoning: dict[str, object]) -> list[dict[str, object]]:
        evidence_paths = reasoning.get("evidence_paths", [])
        action_patch = reasoning.get("action_constraint_patch", [])
        field_queue = reasoning.get("field_validation_queue", [])
        unsupported = reasoning.get("unsupported_claims", [])
        return [
            {
                "rank": 1,
                "gap_id": "G0_flat_knowledge_not_coupled_to_decisions",
                "affected_agents": ["Agent3_Mechanism", "Agent4_FaultDiagnosis", "Agent5_ControlStrategy"],
                "global_view_problem": "知识库过去只是条目匹配和动作加分，缺少污染物-机制-规则-动作-验证需求的可追溯边。",
                "why_foundational": "它决定后续机理解释、故障排序和控制动作能否说明证据来源与失败边界。",
                "after_agent56_status": "patched_by_typed_kg_reasoning" if evidence_paths and action_patch else "still_open",
                "next_carryover": "把同一 KG patch 继续接入灰箱物理残差、稀疏布点和工程仲裁。",
            },
            {
                "rank": 2,
                "gap_id": "G1_parallel_core_agents_not_fully_reconnected",
                "affected_agents": ["Agent48", "Agent49", "Agent53", "Agent54", "Agent55"],
                "global_view_problem": "Agent48/49/53/54/55 已有核心能力，但部分结果仍通过实验报告并联存在，没有全部进入主闭环 Agent1-9。",
                "why_foundational": "会导致模型看起来功能多，但实时状态估计和控制仲裁没有完整消费这些 prior。",
                "after_agent56_status": "partially_open",
                "next_carryover": "优先把 KG evidence path 作为共同接口，再逐步把 grey_box_prior、layout_mask 和 engineering_patch 接入主链。",
            },
            {
                "rank": 3,
                "gap_id": "G2_field_validation_queue_not_action_specific",
                "affected_agents": ["Agent37", "Agent43", "Agent46", "Agent50"],
                "global_view_problem": "现场验证需求存在，但过去更像全局阻塞项，未按每条知识边和每个动作精确绑定。",
                "why_foundational": "真实工程中必须知道哪个动作因为缺哪类标签不能升级，而不是笼统说缺真实数据。",
                "after_agent56_status": "patched_as_field_validation_queue" if field_queue else "still_open",
                "next_carryover": "把 field_validation_queue 与 Agent30/42/44/45 的数据接口逐项对齐。",
            },
            {
                "rank": 4,
                "gap_id": "G3_claim_boundary_missing_for_source_poor_entries",
                "affected_agents": ["Agent37", "Agent38", "Agent50"],
                "global_view_problem": "部分早期知识条目有机理启发，但 source_basis 不够细，容易在后续文案或控制解释中显得证据过强。",
                "why_foundational": "科研价值取决于可审查证据链，source_basis 缺失会降低 claim verification。",
                "after_agent56_status": "exposed_by_unsupported_claims" if unsupported else "no_issue_detected",
                "next_carryover": "下一轮外部文献抽取优先补齐 source_basis、参数范围和适用边界。",
            },
        ]

    @staticmethod
    def _issues(
        reasoning: dict[str, object],
        retrospective: list[dict[str, object]],
        readiness: dict[str, object],
    ) -> list[QualityIssue]:
        issues: list[QualityIssue] = []
        if readiness["field_supported_edge_ratio"] == 0.0:
            issues.append(
                QualityIssue(
                    sensor="knowledge_graph_reasoning",
                    issue_type="no_field_supported_kg_edges",
                    severity=Severity.WARNING,
                    message="KG 已能约束机理和动作先验，但所有匹配边仍缺真实现场支持，不能写执行器或放行门。",
                    evidence=readiness,
                )
            )
        if reasoning.get("unsupported_claims"):
            issues.append(
                QualityIssue(
                    sensor="knowledge_graph_reasoning",
                    issue_type="source_or_field_claim_boundary_required",
                    severity=Severity.WARNING,
                    message="部分知识边缺 source_basis 或 field evidence，需要在后续文献抽取/现场验证中补齐。",
                    evidence={"unsupported_claims": reasoning["unsupported_claims"][:8]},
                )
            )
        for gap in retrospective:
            if gap["after_agent56_status"] in {"still_open", "partially_open"}:
                issues.append(
                    QualityIssue(
                        sensor="agent_chain_retrospective",
                        issue_type=str(gap["gap_id"]),
                        severity=Severity.INFO,
                        message=str(gap["global_view_problem"]),
                        evidence=gap,
                    )
                )
        return issues

    @staticmethod
    def _recommendations(retrospective: list[dict[str, object]], reasoning: dict[str, object]) -> list[str]:
        recs = [
            "把 KG 的 evidence_paths 写入 Agent3 机理假设，把 action_constraint_patch 写入 Agent5 控制动作先验。",
            "KG 只能改变 synthetic/literature 阶段的解释和排序；未有 field_supported_edge 前，不得写执行器或 release gate。",
        ]
        for item in retrospective[:3]:
            recs.append(f"{item['gap_id']}：{item['next_carryover']}")
        if reasoning.get("field_validation_queue"):
            recs.append("下一步按 field_validation_queue 对齐 Agent30/42/44/45 的现场数据接口。")
        return recs

    @staticmethod
    def _method_contract() -> dict[str, object]:
        return {
            "upgrade_id": "P6_reasonable_knowledge_graph_reasoning",
            "borrowed_from": [
                "scientific knowledge graph typed nodes and evidence edges",
                "W3C PROV-style provenance thinking",
                "claim verification gates from academic research agent workflows",
                "rule/action constraint propagation rather than unbounded prompt explanation",
            ],
            "reality_mapping": "把污染物、材料、机制、低成本信号、隐藏状态、控制动作和现场验证需求连接成可追溯图，使机理解释和动作排序能说明证据来源与禁止升级边界。",
            "data_needs": [
                "citation_key_and_source_basis_per_knowledge_edge",
                "raw_sensor_trace",
                "hidden_state_label_or_proxy",
                "action_taken",
                "post_action_lab_outcome",
                "field_validation_need_by_edge",
            ],
            "implementation_path": [
                "src/water_ai/knowledge.py",
                "src/water_ai/agents/knowledge_graph_reasoning_agent.py",
                "src/water_ai/agents/mechanism_agent.py",
                "src/water_ai/agents/fault_diagnosis_agent.py",
                "src/water_ai/agents/control_strategy_agent.py",
            ],
            "evaluation_metrics": [
                "field_supported_edge_ratio",
                "evidence_traceability",
                "constraint_hit_rate",
                "claim_verification_pass_rate",
                "action_constraint_count",
            ],
            "failure_boundary": "KG reasoning constrains explanations and action priors only; without field-supported edges it cannot prove treatment effect or authorize actuator/release-gate writeback.",
        }

    @staticmethod
    def _agent50_writeback(readiness: dict[str, object]) -> dict[str, object]:
        return {
            "allowed_writeback": [
                "mechanism_evidence_paths",
                "control_action_bias_prior",
                "field_validation_queue",
                "P6_completion_status_for_governance",
            ],
            "blocked_writeback": [
                "actuator_policy",
                "release_gate_policy",
                "field_mechanism_claim",
            ],
            "can_advance_governance_priority": bool(readiness["can_update_mechanism_evidence"])
            and bool(readiness["can_update_action_bias_prior"]),
            "policy_effect": (
                "move_to_cross_agent_reconnection"
                if readiness["can_update_mechanism_evidence"] and readiness["can_update_action_bias_prior"]
                else "keep_P6_until_evidence_paths_and_action_constraints_exist"
            ),
        }

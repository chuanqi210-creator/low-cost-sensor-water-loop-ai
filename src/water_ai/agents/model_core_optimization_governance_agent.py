from __future__ import annotations

from collections.abc import Sequence

from water_ai.agents.base import BaseAgent
from water_ai.domain import AgentReport, QualityIssue, SensorReading, Severity


REQUIRED_EVIDENCE_FIELDS = (
    "source",
    "method_family",
    "model_mapping",
    "data_needs",
    "implementation_path",
    "evaluation_metrics",
    "failure_boundary",
)

CORE_ABILITY_WEIGHTS = {
    "observability": 0.18,
    "controllability": 0.16,
    "explainability": 0.14,
    "verifiability": 0.18,
    "engineering_feasibility": 0.14,
    "evolvability": 0.10,
    "protectability": 0.10,
}

MODULE_TERMINATION_THRESHOLDS = {
    "input_contract_completeness": 0.95,
    "output_contract_completeness": 0.95,
    "state_variable_coverage": 0.90,
    "downstream_reconnection_rate": 0.80,
    "evidence_boundary_completeness": 1.00,
    "failure_boundary_completeness": 0.90,
    "no_write_boundary_clarity": 1.00,
}

MODULE_TERMINATION_PROOF_METADATA = {
    "input_contract_completeness": {
        "system_layer": "verification_governance_layer",
        "core_capability": "verifiability",
        "evidence_source": "module input contract metrics",
        "failure_boundary": "Do not close the module stage when upstream inputs are underspecified.",
    },
    "output_contract_completeness": {
        "system_layer": "verification_governance_layer",
        "core_capability": "verifiability",
        "evidence_source": "module output contract metrics",
        "failure_boundary": "Do not route downstream agents when outputs are underspecified.",
    },
    "state_variable_coverage": {
        "system_layer": "state_estimation_layer",
        "core_capability": "observability",
        "evidence_source": "hidden state coverage ledger",
        "failure_boundary": "Do not claim grey-box state coverage for hidden states missing contract rows.",
    },
    "downstream_reconnection_rate": {
        "system_layer": "diagnosis_decision_layer",
        "core_capability": "evolvability",
        "evidence_source": "main-chain reconnection metrics",
        "failure_boundary": "Do not add isolated agents that cannot reconnect to downstream gates.",
    },
    "evidence_boundary_completeness": {
        "system_layer": "mechanism_evidence_layer",
        "core_capability": "explainability",
        "evidence_source": "external evidence matrix completeness",
        "failure_boundary": "Do not treat synthetic, template, or literature-only support as field evidence.",
    },
    "failure_boundary_completeness": {
        "system_layer": "verification_governance_layer",
        "core_capability": "protectability",
        "evidence_source": "external evidence matrix failure boundaries",
        "failure_boundary": "Do not emit claims without explicit known-failure conditions.",
    },
    "no_write_boundary_clarity": {
        "system_layer": "closed_loop_execution_layer",
        "core_capability": "protectability",
        "evidence_source": "actuator and release no-write boundary policy",
        "failure_boundary": "Do not write actuator policy or release gate before field replay and human review.",
    },
}

EXPECTED_HIDDEN_STATES = (
    "pollutant_residual",
    "reaction_completion",
    "catalyst_activity",
    "matrix_interference",
    "hydraulic_delay",
    "release_or_byproduct_risk",
)


class ModelCoreOptimizationGovernanceAgent(BaseAgent):
    """Rank model-core work and interrupt low-value presentation drift."""

    name = "model_core_optimization_governance_agent"

    def __init__(
        self,
        *,
        manifest: dict[str, object] | None = None,
        agent48_metrics: dict[str, object] | None = None,
        agent49_metrics: dict[str, object] | None = None,
        catalyst_proxy_metrics: dict[str, object] | None = None,
        replay_evaluation_metrics: dict[str, object] | None = None,
        grey_box_physics_metrics: dict[str, object] | None = None,
        soft_sensor_matrix_metrics: dict[str, object] | None = None,
        engineering_constraints_metrics: dict[str, object] | None = None,
        knowledge_graph_reasoning_metrics: dict[str, object] | None = None,
        main_chain_reconnection_metrics: dict[str, object] | None = None,
        field_validation_queue_alignment_metrics: dict[str, object] | None = None,
        claim_specific_field_package_metrics: dict[str, object] | None = None,
        unified_field_evidence_gate_metrics: dict[str, object] | None = None,
        real_field_package_acceptance_metrics: dict[str, object] | None = None,
        r7_pipeline_metrics: dict[str, object] | None = None,
        field_path_endpoint_label_preflight: dict[str, object] | None = None,
        formal_search_execution_route_plan: dict[str, object] | None = None,
        formal_search_ai_nonlegal_review_brief: dict[str, object] | None = None,
        formal_search_nonlegal_review_operator_packet: dict[str, object] | None = None,
        external_activation_router: dict[str, object] | None = None,
        external_activation_operator_action_packet: dict[str, object] | None = None,
        field_activation_matrix_metrics: dict[str, object] | None = None,
        observation_contract_metrics: dict[str, object] | None = None,
        observation_response_bridge_metrics: dict[str, object] | None = None,
        catalyst_evidence_response_gate_metrics: dict[str, object] | None = None,
        catalyst_response_submission_kit_metrics: dict[str, object] | None = None,
        focused_catalyst_response_merge_metrics: dict[str, object] | None = None,
        catalyst_field_package_slice_metrics: dict[str, object] | None = None,
        catalyst_slice_r7_patch_candidate_metrics: dict[str, object] | None = None,
        control_replay_stress_metrics: dict[str, object] | None = None,
        backlog: list[dict[str, object]] | None = None,
        external_evidence_matrix: list[dict[str, object]] | None = None,
        current_work_item: dict[str, object] | None = None,
    ) -> None:
        self.manifest = manifest or {}
        self.agent48_metrics = agent48_metrics or {}
        self.agent49_metrics = agent49_metrics or {}
        self.catalyst_proxy_metrics = catalyst_proxy_metrics or {}
        self.replay_evaluation_metrics = replay_evaluation_metrics or {}
        self.grey_box_physics_metrics = grey_box_physics_metrics or {}
        self.soft_sensor_matrix_metrics = soft_sensor_matrix_metrics or {}
        self.engineering_constraints_metrics = engineering_constraints_metrics or {}
        self.knowledge_graph_reasoning_metrics = knowledge_graph_reasoning_metrics or {}
        self.main_chain_reconnection_metrics = main_chain_reconnection_metrics or {}
        self.field_validation_queue_alignment_metrics = field_validation_queue_alignment_metrics or {}
        self.claim_specific_field_package_metrics = claim_specific_field_package_metrics or {}
        self.unified_field_evidence_gate_metrics = unified_field_evidence_gate_metrics or {}
        self.real_field_package_acceptance_metrics = real_field_package_acceptance_metrics or {}
        self.r7_pipeline_metrics = r7_pipeline_metrics or {}
        self.field_path_endpoint_label_preflight = field_path_endpoint_label_preflight or {}
        self.formal_search_execution_route_plan = formal_search_execution_route_plan or {}
        self.formal_search_ai_nonlegal_review_brief = (
            formal_search_ai_nonlegal_review_brief or {}
        )
        self.formal_search_nonlegal_review_operator_packet = (
            formal_search_nonlegal_review_operator_packet or {}
        )
        self.external_activation_router = external_activation_router or {}
        self.external_activation_operator_action_packet = external_activation_operator_action_packet or {}
        self.field_activation_matrix_metrics = field_activation_matrix_metrics or {}
        self.observation_contract_metrics = observation_contract_metrics or {}
        self.observation_response_bridge_metrics = observation_response_bridge_metrics or {}
        self.catalyst_evidence_response_gate_metrics = catalyst_evidence_response_gate_metrics or {}
        self.catalyst_response_submission_kit_metrics = catalyst_response_submission_kit_metrics or {}
        self.focused_catalyst_response_merge_metrics = focused_catalyst_response_merge_metrics or {}
        self.catalyst_field_package_slice_metrics = catalyst_field_package_slice_metrics or {}
        self.catalyst_slice_r7_patch_candidate_metrics = catalyst_slice_r7_patch_candidate_metrics or {}
        self.control_replay_stress_metrics = control_replay_stress_metrics or {}
        self.backlog = backlog or self._default_backlog()
        self.external_evidence_matrix = external_evidence_matrix or []
        self.current_work_item = current_work_item or {
            "task_id": "current_model_core_governance",
            "title": "模型核心治理与下一步排序",
            "category": "model_core",
            "touches_model_metrics": True,
        }

    def run(self, readings: Sequence[SensorReading]) -> AgentReport:
        del readings
        priority_ranking = self._priority_ranking()
        low_priority_backlog = [item for item in priority_ranking if item["marginal_value_score"] < 0.45]
        external_blocker_backlog = [item for item in priority_ranking if bool(item.get("external_blocker", False))]
        evidence_matrix_status = self._evidence_matrix_status()
        blocked_reasons = self._blocked_reasons(evidence_matrix_status)
        governance_review_gate = self._governance_review_gate()
        stage_boundary_deferred_backlog = self._stage_boundary_deferred_backlog()
        external_activation_contract = self._external_activation_contract()
        recommended = self._recommended_next_core_action(priority_ranking)
        quantified_core_score_gate = self._quantified_core_score_gate(
            priority_ranking=priority_ranking,
            evidence_matrix_status=evidence_matrix_status,
            blocked_reasons=blocked_reasons,
            external_activation_contract=external_activation_contract,
        )
        self_interrupt_verdict = self._self_interrupt_verdict(
            stage_decision=str(quantified_core_score_gate["stage_decision"])
        )
        self_interrupt_reason = self._self_interrupt_reason(self_interrupt_verdict)
        quantified_core_score_gate["self_interrupt_verdict"] = self_interrupt_verdict
        quantified_core_score_gate["self_interrupt_reason"] = self_interrupt_reason
        quantified_core_score_gate["self_interrupt_mode"] = (
            "stage_gate_throttled_hard_gate_with_deferred_backlog"
        )
        issues = self._issues(evidence_matrix_status, self_interrupt_verdict)
        summary = (
            "模型核心治理："
            f"最高边际价值任务为 `{recommended['task_id']}`，"
            f"自我打断结论 `{self_interrupt_verdict}`，"
            f"量化阶段判定 `{quantified_core_score_gate['stage_decision']}`。"
        )
        confidence = round(
            min(
                0.93,
                max(
                    0.35,
                    0.55
                    + 0.18 * evidence_matrix_status["completeness_score"]
                    + 0.12 * bool(priority_ranking)
                    - 0.05 * len([issue for issue in issues if issue.severity == Severity.WARNING]),
                ),
            ),
            3,
        )

        return AgentReport(
            agent_name=self.name,
            confidence=confidence,
            summary=summary,
            issues=issues,
            recommendations=self._recommendations(recommended, self_interrupt_verdict, blocked_reasons),
            metrics={
                "governance_principles": self._governance_principles(),
                "priority_ranking": priority_ranking,
                "low_priority_backlog": low_priority_backlog,
                "external_blocker_backlog": external_blocker_backlog,
                "blocked_reasons": blocked_reasons,
                "external_activation_contract": external_activation_contract,
                "recommended_next_core_action": recommended,
                "self_interrupt_verdict": self_interrupt_verdict,
                "self_interrupt_reason": self_interrupt_reason,
                "self_interrupt_mode": "stage_gate_throttled_hard_gate_with_deferred_backlog",
                "governance_review_gate": governance_review_gate,
                "quantified_core_score_gate": quantified_core_score_gate,
                "governance_review_policy": "hard_risk_or_stage_boundary_only",
                "stage_boundary_deferred_backlog": stage_boundary_deferred_backlog,
                "stage_boundary_deferred_count": len(stage_boundary_deferred_backlog),
                "governance_scorecard": {
                    "scoring_fields": [
                        "model_core_relevance",
                        "downstream_chain_impact",
                        "scientific_value",
                        "engineering_feasibility",
                        "verification_readiness",
                        "avoid_presentation_bias",
                        "marginal_value_score",
                    ],
                    "weak_state_coverage": self._weak_state_coverage(),
                    "catalyst_activity_observability": self._catalyst_activity_observability(),
                    "catalyst_proxy_status": self._catalyst_proxy_status(),
                    "catalyst_proxy_after_patch": self._catalyst_proxy_after_patch(),
                    "agent49_coordination_status": self._agent49_readiness().get("coordination_status", "unknown"),
                    "replay_evaluation_status": self._replay_evaluation_status(),
                    "replay_joint_action_accuracy": self._replay_joint_action_accuracy(),
                    "grey_box_physics_status": self._grey_box_physics_status(),
                    "mean_grey_box_residual": self._mean_grey_box_residual(),
                    "soft_sensor_matrix_status": self._soft_sensor_matrix_status(),
                    "missingness_robustness_score": self._missingness_robustness_score(),
                    "engineering_constraints_status": self._engineering_constraints_status(),
                    "engineering_mean_execution_feasibility": self._engineering_mean_execution_feasibility(),
                    "kg_reasoning_status": self._kg_reasoning_status(),
                    "kg_evidence_traceability": self._kg_evidence_traceability(),
                    "kg_constraint_hit_rate": self._kg_constraint_hit_rate(),
                    "main_chain_reconnection_status": self._main_chain_reconnection_status(),
                    "main_chain_prior_consumption_rate": self._main_chain_prior_consumption_rate(),
                    "field_validation_alignment_status": self._field_validation_alignment_status(),
                    "field_need_to_table_coverage": self._field_need_to_table_coverage(),
                    "field_need_to_gate_coverage": self._field_need_to_gate_coverage(),
                    "claim_specific_package_status": self._claim_specific_package_status(),
                    "claim_specific_required_field_coverage": self._claim_specific_required_field_coverage(),
                    "source_basis_completion_rate": self._source_basis_completion_rate(),
                    "source_basis_detail_ready": self._source_basis_detail_ready(),
                    "external_field_blocker_active": self._external_field_blocker_active(),
                    "claim_basis_promotion_gate_status": self._claim_basis_promotion_gate_status(),
                    "claim_basis_promotion_ready_count": self._claim_basis_promotion_ready_count(),
                    "claim_basis_promotion_blocked_count": self._claim_basis_promotion_blocked_count(),
                    "claim_basis_promotion_can_emit_field_claim_upgrade": (
                        self._claim_basis_promotion_can_emit_field_claim_upgrade()
                    ),
                    "claim_basis_promotion_can_write_to_actuator": (
                        self._claim_basis_promotion_can_write_to_actuator()
                    ),
                    "claim_basis_promotion_can_write_to_release_gate": (
                        self._claim_basis_promotion_can_write_to_release_gate()
                    ),
                    "field_evidence_wait_status": self._field_evidence_wait_status(),
                    "external_activation_contract_status": external_activation_contract["contract_status"],
                    "external_activation_ready": external_activation_contract["activation_ready"],
                    "external_activation_ready_channel_count": (
                        external_activation_contract["ready_channel_count"]
                    ),
                    "external_activation_blocked_channel_count": (
                        external_activation_contract["blocked_channel_count"]
                    ),
                    "external_activation_next_operator_actions": (
                        external_activation_contract["next_operator_actions"]
                    ),
                    "external_activation_boundary_preserved": (
                        external_activation_contract["boundary_preserved"]
                    ),
                    "external_activation_router_status": self._external_activation_router_status(),
                    "external_activation_router_consumed": self._external_activation_router_consumed(),
                    "external_activation_router_path_supplied_count": (
                        self._external_activation_router_path_supplied_count()
                    ),
                    "external_activation_router_route_ready_count": (
                        self._external_activation_router_route_ready_count()
                    ),
                    "external_activation_router_model_chain_ready_route_count": (
                        self._external_activation_router_model_chain_ready_route_count()
                    ),
                    "external_activation_router_handoff_ready_route_count": (
                        self._external_activation_router_handoff_ready_route_count()
                    ),
                    "external_activation_router_blocked_route_count": (
                        self._external_activation_router_blocked_route_count()
                    ),
                    "external_activation_router_catalyst_patch_candidate_consumed": (
                        self._external_activation_router_catalyst_patch_candidate_consumed()
                    ),
                    "external_activation_router_catalyst_patch_candidate_status": (
                        self._external_activation_router_catalyst_patch_candidate_status()
                    ),
                    "external_activation_router_catalyst_patch_candidate_materialized": (
                        self._external_activation_router_catalyst_patch_candidate_materialized()
                    ),
                    "external_activation_router_catalyst_patch_candidate_preflight_status": (
                        self._external_activation_router_catalyst_patch_candidate_preflight_status()
                    ),
                    "external_activation_router_catalyst_patch_candidate_remaining_gap_count": (
                        self._external_activation_router_catalyst_patch_candidate_remaining_gap_count()
                    ),
                    "external_activation_router_catalyst_patch_candidate_can_submit_as_REAL_FIELD_REPLAY_PACKAGE_DIR": (
                        self._external_activation_router_catalyst_patch_candidate_can_submit_as_r7_dir()
                    ),
                    "external_activation_router_catalyst_patch_candidate_package_dir": (
                        self._external_activation_router_catalyst_patch_candidate_package_dir()
                    ),
                    "external_activation_router_field_activation_upstream_consumed": (
                        self._external_activation_router_field_activation_upstream_consumed()
                    ),
                    "external_activation_router_field_activation_upstream_status": (
                        self._external_activation_router_field_activation_upstream_status()
                    ),
                    "external_activation_router_field_activation_upstream_first_blocked_step": (
                        self._external_activation_router_field_activation_upstream_first_blocked_step()
                    ),
                    "external_activation_router_field_activation_upstream_highest_priority_blocker": (
                        self._external_activation_router_field_activation_upstream_highest_priority_blocker()
                    ),
                    "external_activation_router_field_activation_upstream_next_operator_action": (
                        self._external_activation_router_field_activation_upstream_next_operator_action()
                    ),
                    "external_activation_router_field_activation_upstream_can_submit_to_external_activation_router": (
                        self._external_activation_router_field_activation_upstream_can_submit_to_external_activation_router()
                    ),
                    "external_activation_router_field_activation_upstream_submission_packet_status": (
                        self._external_activation_router_field_activation_upstream_submission_packet_status()
                    ),
                    "external_activation_router_boundary_preserved": (
                        self._external_activation_router_boundary_preserved()
                    ),
                    "external_activation_router_no_write_boundary": (
                        self._external_activation_router_no_write_boundary()
                    ),
                    "external_activation_operator_action_packet_status": (
                        self._external_activation_operator_packet_status()
                    ),
                    "external_activation_operator_action_packet_target_hidden_state": (
                        self._external_activation_operator_packet_target_hidden_state()
                    ),
                    "external_activation_operator_action_packet_source_env_var": (
                        self._external_activation_operator_packet_source_env_var()
                    ),
                    "external_activation_operator_action_packet_expected_focused_response_row_count": (
                        self._external_activation_operator_packet_expected_focused_response_row_count()
                    ),
                    "external_activation_operator_action_packet_focused_candidate_availability_status": (
                        self._external_activation_operator_packet_focused_candidate_availability_status()
                    ),
                    "external_activation_operator_action_packet_focused_candidate_operator_packet_submit_ready": (
                        self._external_activation_operator_packet_focused_candidate_operator_packet_submit_ready()
                    ),
                    "external_activation_operator_action_packet_next_operator_action": (
                        self._external_activation_operator_packet_next_operator_action()
                    ),
                    "external_activation_operator_action_packet_boundary_pass": (
                        self._external_activation_operator_packet_boundary_pass()
                    ),
                    "external_activation_operator_action_packet_can_resume_model_chain": (
                        self._external_activation_operator_packet_can_resume_model_chain()
                    ),
                    "external_activation_operator_action_packet_can_write_to_actuator": (
                        self._external_activation_operator_packet_can_write_to_actuator()
                    ),
                    "external_activation_operator_action_packet_can_write_to_release_gate": (
                        self._external_activation_operator_packet_can_write_to_release_gate()
                    ),
                    "field_activation_matrix_status": self._field_activation_matrix_status(),
                    "field_activation_matrix_hidden_state_row_count": (
                        self._field_activation_matrix_hidden_state_row_count()
                    ),
                    "field_activation_matrix_can_resume_model_chain": (
                        self._field_activation_matrix_can_resume_model_chain()
                    ),
                    "field_activation_matrix_no_write_boundary_complete": (
                        self._field_activation_matrix_no_write_boundary_complete()
                    ),
                    "field_activation_response_source_preflight_status": (
                        self._field_activation_response_source_preflight_status()
                    ),
                    "field_activation_response_source_external_response_supplied": (
                        self._field_activation_response_source_external_response_supplied()
                    ),
                    "field_activation_response_source_can_run_response_preflight": (
                        self._field_activation_response_source_can_run_response_preflight()
                    ),
                    "field_activation_response_repair_work_order_status": (
                        self._field_activation_response_repair_work_order_status()
                    ),
                    "field_activation_response_repair_item_count": (
                        self._field_activation_response_repair_item_count()
                    ),
                    "field_activation_response_repair_highest_priority_repair_id": (
                        self._field_activation_response_repair_highest_priority_repair_id()
                    ),
                    "field_activation_response_preflight_status": (
                        self._field_activation_response_preflight_status()
                    ),
                    "field_activation_response_expected_row_count": (
                        self._field_activation_response_expected_row_count()
                    ),
                    "field_activation_response_template_marker_row_count": (
                        self._field_activation_response_template_marker_row_count()
                    ),
                    "field_activation_response_missing_value_payload_row_count": (
                        self._field_activation_response_missing_value_payload_row_count()
                    ),
                    "field_activation_response_template_value_payload_row_count": (
                        self._field_activation_response_template_value_payload_row_count()
                    ),
                    "field_activation_response_can_route_to_external_activation_router": (
                        self._field_activation_response_can_route_to_external_activation_router()
                    ),
                    "field_activation_response_completion_ledger_status": (
                        self._field_activation_response_completion_ledger_status()
                    ),
                    "field_activation_response_completion_ratio": (
                        self._field_activation_response_completion_ratio()
                    ),
                    "field_activation_response_completed_row_count": (
                        self._field_activation_response_completed_row_count()
                    ),
                    "field_activation_response_incomplete_row_count": (
                        self._field_activation_response_incomplete_row_count()
                    ),
                    "field_activation_response_next_hidden_state_focus": (
                        self._field_activation_response_next_hidden_state_focus()
                    ),
                    "field_activation_response_completion_next_operator_action": (
                        self._field_activation_response_completion_next_operator_action()
                    ),
                    "field_activation_response_focus_handoff_status": (
                        self._field_activation_response_focus_handoff_status()
                    ),
                    "field_activation_response_focus_handoff_target_hidden_state": (
                        self._field_activation_response_focus_handoff_target_hidden_state()
                    ),
                    "field_activation_response_focus_handoff_row_scan_reduction_ratio": (
                        self._field_activation_response_focus_handoff_row_scan_reduction_ratio()
                    ),
                    "field_activation_response_focus_handoff_next_operator_action": (
                        self._field_activation_response_focus_handoff_next_operator_action()
                    ),
                    "field_activation_response_focus_handoff_repair_work_order_status": (
                        self._field_activation_response_focus_handoff_repair_work_order_status()
                    ),
                    "field_activation_response_focus_handoff_repair_item_count": (
                        self._field_activation_response_focus_handoff_repair_item_count()
                    ),
                    "field_activation_response_focus_handoff_repair_next_operator_action": (
                        self._field_activation_response_focus_handoff_repair_next_operator_action()
                    ),
                    "field_activation_response_focus_handoff_source_env_var": (
                        self._field_activation_response_focus_handoff_source_env_var()
                    ),
                    "field_activation_response_focus_handoff_can_submit_to_external_activation_router": (
                        self._field_activation_response_focus_handoff_can_submit_to_external_activation_router()
                    ),
                    "field_activation_response_coherence_audit_status": (
                        self._field_activation_response_coherence_audit_status()
                    ),
                    "field_activation_response_coherence_hard_blocker_count": (
                        self._field_activation_response_coherence_hard_blocker_count()
                    ),
                    "field_activation_response_coherence_warning_count": (
                        self._field_activation_response_coherence_warning_count()
                    ),
                    "field_activation_response_coherence_highest_priority_blocker": (
                        self._field_activation_response_coherence_highest_priority_blocker()
                    ),
                    "field_activation_response_coherence_can_route_to_package_assembly": (
                        self._field_activation_response_coherence_can_route_to_package_assembly()
                    ),
                    "field_activation_package_assembly_status": (
                        self._field_activation_package_assembly_status()
                    ),
                    "field_activation_package_assembly_channel_plan_count": (
                        self._field_activation_package_assembly_channel_plan_count()
                    ),
                    "field_activation_package_assembly_candidate_channel_plan_count": (
                        self._field_activation_package_assembly_candidate_channel_plan_count()
                    ),
                    "field_activation_package_assembly_can_stage_external_package_candidates": (
                        self._field_activation_package_assembly_can_stage_external_package_candidates()
                    ),
                    "field_activation_package_staging_status": (
                        self._field_activation_package_staging_status()
                    ),
                    "field_activation_package_staging_selected_channel_manifest_count": (
                        self._field_activation_package_staging_selected_channel_manifest_count()
                    ),
                    "field_activation_package_staging_selected_row_blueprint_count": (
                        self._field_activation_package_staging_selected_row_blueprint_count()
                    ),
                    "field_activation_package_staging_selected_value_payload_mapping_count": (
                        self._field_activation_package_staging_selected_value_payload_mapping_count()
                    ),
                    "field_activation_package_staging_can_materialize_no_write_package_candidates": (
                        self._field_activation_package_staging_can_materialize_no_write_package_candidates()
                    ),
                    "field_activation_package_staging_next_operator_action": (
                        self._field_activation_package_staging_next_operator_action()
                    ),
                    "field_activation_materialized_package_preflight_status": (
                        self._field_activation_materialized_package_preflight_status()
                    ),
                    "field_activation_materialized_package_preflight_blocker_count": (
                        self._field_activation_materialized_package_preflight_blocker_count()
                    ),
                    "field_activation_materialized_package_blueprint_missing_row_count": (
                        self._field_activation_materialized_package_blueprint_missing_row_count()
                    ),
                    "field_activation_materialized_package_preflight_highest_priority_blocker": (
                        self._field_activation_materialized_package_preflight_highest_priority_blocker()
                    ),
                    "field_activation_materialized_package_preflight_can_route_to_external_activation_router": (
                        self._field_activation_materialized_package_preflight_can_route_to_external_activation_router()
                    ),
                    "field_activation_downstream_r7_preview_status": (
                        self._field_activation_downstream_r7_preview_status()
                    ),
                    "field_activation_downstream_r7_preview_executed": (
                        self._field_activation_downstream_r7_preview_executed()
                    ),
                    "field_activation_downstream_r7_preview_metric_evaluation_status": (
                        self._field_activation_downstream_r7_preview_metric_evaluation_status()
                    ),
                    "field_activation_downstream_r7_not_evaluated_metric_count": (
                        self._field_activation_downstream_r7_not_evaluated_metric_count()
                    ),
                    "field_activation_downstream_r7_agent44_import_status": (
                        self._field_activation_downstream_r7_agent44_import_status()
                    ),
                    "field_activation_downstream_r7_can_pass_to_timestamped_replay": (
                        self._field_activation_downstream_r7_can_pass_to_timestamped_replay()
                    ),
                    "field_activation_downstream_r7_highest_priority_blocker": (
                        self._field_activation_downstream_r7_highest_priority_blocker()
                    ),
                    "field_activation_downstream_r7_next_operator_action": (
                        self._field_activation_downstream_r7_next_operator_action()
                    ),
                    "field_activation_downstream_path_endpoint_preview_status": (
                        self._field_activation_downstream_path_endpoint_preview_status()
                    ),
                    "field_activation_downstream_path_endpoint_preview_executed": (
                        self._field_activation_downstream_path_endpoint_preview_executed()
                    ),
                    "field_activation_downstream_path_endpoint_preview_metric_evaluation_status": (
                        self._field_activation_downstream_path_endpoint_preview_metric_evaluation_status()
                    ),
                    "field_activation_downstream_path_endpoint_not_evaluated_metric_count": (
                        self._field_activation_downstream_path_endpoint_not_evaluated_metric_count()
                    ),
                    "field_activation_downstream_path_endpoint_preflight_status": (
                        self._field_activation_downstream_path_endpoint_preflight_status()
                    ),
                    "field_activation_downstream_path_endpoint_required_table_count": (
                        self._field_activation_downstream_path_endpoint_required_table_count()
                    ),
                    "field_activation_downstream_path_endpoint_contract_minimum_matched_batch_count": (
                        self._field_activation_downstream_path_endpoint_contract_minimum_matched_batch_count()
                    ),
                    "field_activation_downstream_path_endpoint_matched_batch_count": (
                        self._field_activation_downstream_path_endpoint_matched_batch_count()
                    ),
                    "field_activation_downstream_path_endpoint_required_matched_batch_deficit": (
                        self._field_activation_downstream_path_endpoint_required_matched_batch_deficit()
                    ),
                    "field_activation_downstream_path_endpoint_can_route_to_field_layout_holdout": (
                        self._field_activation_downstream_path_endpoint_can_route_to_field_layout_holdout()
                    ),
                    "field_activation_downstream_path_endpoint_highest_priority_blocker": (
                        self._field_activation_downstream_path_endpoint_highest_priority_blocker()
                    ),
                    "field_activation_downstream_path_endpoint_next_operator_action": (
                        self._field_activation_downstream_path_endpoint_next_operator_action()
                    ),
                    "field_activation_external_readiness_gate_status": (
                        self._field_activation_external_readiness_gate_status()
                    ),
                    "field_activation_external_readiness_first_blocked_step": (
                        self._field_activation_external_readiness_first_blocked_step()
                    ),
                    "field_activation_external_readiness_highest_priority_blocker": (
                        self._field_activation_external_readiness_highest_priority_blocker()
                    ),
                    "field_activation_external_readiness_next_operator_action": (
                        self._field_activation_external_readiness_next_operator_action()
                    ),
                    "field_activation_external_readiness_can_submit_to_external_activation_router": (
                        self._field_activation_external_readiness_can_submit_to_external_activation_router()
                    ),
                    "field_activation_response_submission_packet_status": (
                        self._field_activation_response_submission_packet_status()
                    ),
                    "field_activation_response_submission_packet_next_operator_action": (
                        self._field_activation_response_submission_packet_next_operator_action()
                    ),
                    "field_activation_response_submission_packet_highest_priority_blocker": (
                        self._field_activation_response_submission_packet_highest_priority_blocker()
                    ),
                    "field_activation_response_submission_packet_can_route_to_external_activation_router": (
                        self._field_activation_response_submission_packet_can_route_to_external_activation_router()
                    ),
                    "field_activation_schema_preflight_status": (
                        self._field_activation_schema_preflight_status()
                    ),
                    "field_activation_schema_can_validate_response_structure": (
                        self._field_activation_schema_can_validate_response_structure()
                    ),
                    "field_activation_schema_can_resume_model_chain": (
                        self._field_activation_schema_can_resume_model_chain()
                    ),
                    "external_activation_router_ready_channel_ids": (
                        self._external_activation_router_ready_channel_ids()
                    ),
                    "external_activation_router_model_chain_ready_channel_ids": (
                        self._external_activation_router_model_chain_ready_channel_ids()
                    ),
                    "external_activation_router_handoff_ready_channel_ids": (
                        self._external_activation_router_handoff_ready_channel_ids()
                    ),
                    "external_activation_router_blocked_channel_ids": (
                        self._external_activation_router_blocked_channel_ids()
                    ),
                    "external_activation_router_route_summary": (
                        self._external_activation_router_route_summary()
                    ),
                    "external_activation_router_highest_priority_blocker": (
                        self._external_activation_router_highest_priority_blocker()
                    ),
                    "external_activation_router_next_operator_action": (
                        self._external_activation_router_next_operator_action()
                    ),
                    "unified_field_evidence_gate_status": self._unified_field_evidence_status(),
                    "real_field_package_acceptance_status": self._real_field_package_acceptance_status(),
                    "r7_field_evidence_sufficiency_status": self._r7_field_evidence_sufficiency_status(),
                    "r7_field_evidence_sufficiency_score": self._r7_field_evidence_sufficiency_score(),
                    "r7_field_evidence_smoke_pass": self._r7_field_evidence_smoke_pass(),
                    "r7_can_route_to_human_review_candidate": self._r7_can_route_to_human_review_candidate(),
                    "r7_submission_readiness_status": self._r7_submission_readiness_status(),
                    "r7_submission_highest_priority_blocker": self._r7_submission_highest_priority_blocker(),
                    "r7_submission_next_operator_action": self._r7_submission_next_operator_action(),
                    "r7_submission_blocking_stage_count": self._r7_submission_blocking_stage_count(),
                    "r7_submission_repair_work_order_status": (
                        self._r7_submission_repair_work_order_status()
                    ),
                    "r7_submission_repair_item_count": self._r7_submission_repair_item_count(),
                    "r7_submission_repair_work_order_path": self._r7_submission_repair_work_order_path(),
                    "r7_submission_repair_response_preflight_status": (
                        self._r7_submission_repair_response_preflight_status()
                    ),
                    "r7_submission_repair_response_can_route_to_r7_preflight": (
                        self._r7_submission_repair_response_can_route_to_r7_preflight()
                    ),
                    "field_path_endpoint_label_preflight_status": self._field_path_endpoint_label_preflight_status(),
                    "field_path_endpoint_matched_batch_count": self._field_path_endpoint_matched_batch_count(),
                    "field_path_endpoint_required_matched_batch_deficit": (
                        self._field_path_endpoint_required_matched_batch_deficit()
                    ),
                    "field_path_endpoint_batch_alignment_gap_count": (
                        self._field_path_endpoint_batch_alignment_gap_count()
                    ),
                    "field_path_endpoint_alignment_patch_plan_status": (
                        self._field_path_endpoint_alignment_patch_plan_status()
                    ),
                    "field_path_endpoint_alignment_patch_plan_item_count": (
                        self._field_path_endpoint_alignment_patch_plan_item_count()
                    ),
                    "field_path_endpoint_label_package_ready": self._field_path_endpoint_label_package_ready(),
                    "field_path_endpoint_final_effluent_label_ready": (
                        self._field_path_endpoint_final_effluent_label_ready()
                    ),
                    "can_route_to_field_layout_holdout_with_path_labels": (
                        self._can_route_to_field_layout_holdout_with_path_labels()
                    ),
                    "release_gate_endpoint_label_blocked": self._release_gate_endpoint_label_blocked(),
                    "formal_search_execution_route_plan_status": (
                        self._formal_search_execution_route_plan_status()
                    ),
                    "formal_search_execution_complete_route_row_count": (
                        self._formal_search_execution_complete_route_row_count()
                    ),
                    "formal_search_execution_route_row_count": (
                        self._formal_search_execution_route_row_count()
                    ),
                    "formal_search_execution_mapped_seed_route_count": (
                        self._formal_search_execution_mapped_seed_route_count()
                    ),
                    "formal_search_execution_operator_first_action": (
                        self._formal_search_execution_operator_first_action()
                    ),
                    "formal_search_execution_boundary_preserved": (
                        self._formal_search_execution_boundary_preserved()
                    ),
                    "formal_search_ai_nonlegal_review_brief_status": (
                        self._formal_search_ai_nonlegal_review_brief_status()
                    ),
                    "formal_search_ai_nonlegal_review_brief_row_count": (
                        self._formal_search_ai_nonlegal_review_brief_row_count()
                    ),
                    "formal_search_ai_nonlegal_review_brief_missing_source_row_count": (
                        self._formal_search_ai_nonlegal_review_brief_missing_source_row_count()
                    ),
                    "formal_search_ai_nonlegal_review_brief_missing_claim_mapping_row_count": (
                        self._formal_search_ai_nonlegal_review_brief_missing_claim_mapping_row_count()
                    ),
                    "formal_search_ai_nonlegal_review_brief_can_help_human_review": (
                        self._formal_search_ai_nonlegal_review_brief_can_help_human_review()
                    ),
                    "formal_search_ai_nonlegal_review_brief_can_route_to_claim_scope_patch_draft": (
                        self._formal_search_ai_nonlegal_review_brief_can_route_to_claim_scope_patch_draft()
                    ),
                    "formal_search_ai_nonlegal_review_brief_boundary_preserved": (
                        self._formal_search_ai_nonlegal_review_brief_boundary_preserved()
                    ),
                    "formal_search_ai_nonlegal_review_brief_next_operator_action": (
                        self._formal_search_ai_nonlegal_review_brief_next_operator_action()
                    ),
                    "formal_search_nonlegal_review_operator_packet_status": (
                        self._formal_search_nonlegal_review_operator_packet_status()
                    ),
                    "formal_search_nonlegal_review_operator_packet_expected_review_packet_row_count": (
                        self._formal_search_nonlegal_review_operator_packet_expected_review_packet_row_count()
                    ),
                    "formal_search_nonlegal_review_operator_packet_high_priority_review_row_count": (
                        self._formal_search_nonlegal_review_operator_packet_high_priority_review_row_count()
                    ),
                    "formal_search_nonlegal_review_operator_packet_accepted_review_row_count": (
                        self._formal_search_nonlegal_review_operator_packet_accepted_review_row_count()
                    ),
                    "formal_search_nonlegal_review_operator_packet_source_env_var": (
                        self._formal_search_nonlegal_review_operator_packet_source_env_var()
                    ),
                    "formal_search_nonlegal_review_operator_packet_can_route_to_claim_scope_patch_draft": (
                        self._formal_search_nonlegal_review_operator_packet_can_route_to_claim_scope_patch_draft()
                    ),
                    "formal_search_nonlegal_review_operator_packet_boundary_preserved": (
                        self._formal_search_nonlegal_review_operator_packet_boundary_preserved()
                    ),
                    "formal_search_nonlegal_review_operator_packet_next_operator_action": (
                        self._formal_search_nonlegal_review_operator_packet_next_operator_action()
                    ),
                    "observation_contract_status": self._observation_contract_status(),
                    "observation_contract_weak_state_coverage": self._observation_contract_weak_state_coverage(),
                    "observation_response_bridge_status": self._observation_response_bridge_status(),
                    "observation_response_bridge_target_hidden_state": (
                        self._observation_response_bridge_target_hidden_state()
                    ),
                    "observation_response_bridge_response_row_count": (
                        self._observation_response_bridge_response_row_count()
                    ),
                    "observation_response_bridge_required_role_coverage_rate": (
                        self._observation_response_bridge_required_role_coverage_rate()
                    ),
                    "observation_response_bridge_can_route_to_agent51_field_proxy_holdout": (
                        self._observation_response_bridge_can_route_to_agent51_field_proxy_holdout()
                    ),
                    "observation_response_bridge_can_relax_agent49_catalyst_uncertainty_block": (
                        self._observation_response_bridge_can_relax_agent49_catalyst_uncertainty_block()
                    ),
                    "catalyst_evidence_response_gate_status": self._catalyst_evidence_response_gate_status(),
                    "catalyst_evidence_response_gate_target_response_row_count": (
                        self._catalyst_evidence_response_gate_target_response_row_count()
                    ),
                    "catalyst_evidence_response_gate_row_level_preflight_pass": (
                        self._catalyst_evidence_response_gate_row_level_preflight_pass()
                    ),
                    "catalyst_evidence_response_gate_matched_batch_count": (
                        self._catalyst_evidence_response_gate_matched_batch_count()
                    ),
                    "catalyst_evidence_response_gate_matched_batch_requirement_pass": (
                        self._catalyst_evidence_response_gate_matched_batch_requirement_pass()
                    ),
                    "catalyst_evidence_response_gate_can_route_to_focused_materialized_package_preflight": (
                        self._catalyst_evidence_response_gate_can_route_to_focused_materialized_package_preflight()
                    ),
                    "catalyst_evidence_response_gate_can_route_to_agent51_field_proxy_holdout": (
                        self._catalyst_evidence_response_gate_can_route_to_agent51_field_proxy_holdout()
                    ),
                    "catalyst_response_submission_kit_status": self._catalyst_response_submission_kit_status(),
                    "catalyst_response_submission_kit_target_response_row_count": (
                        self._catalyst_response_submission_kit_target_response_row_count()
                    ),
                    "catalyst_response_submission_kit_focused_template_path": (
                        self._catalyst_response_submission_kit_focused_template_path()
                    ),
                    "catalyst_response_submission_kit_can_route_to_agent51_field_proxy_holdout": (
                        self._catalyst_response_submission_kit_can_route_to_agent51_field_proxy_holdout()
                    ),
                    "focused_catalyst_response_merge_status": self._focused_catalyst_response_merge_status(),
                    "focused_catalyst_response_source_preflight_status": (
                        self._focused_catalyst_response_source_preflight_status()
                    ),
                    "focused_catalyst_response_source_can_run_merge_preflight": (
                        self._focused_catalyst_response_source_can_run_merge_preflight()
                    ),
                    "focused_catalyst_response_merge_row_preflight_pass": (
                        self._focused_catalyst_response_merge_row_preflight_pass()
                    ),
                    "focused_catalyst_response_repair_work_order_status": (
                        self._focused_catalyst_response_repair_work_order_status()
                    ),
                    "focused_catalyst_response_repair_item_count": (
                        self._focused_catalyst_response_repair_item_count()
                    ),
                    "focused_catalyst_response_repair_highest_priority_repair_id": (
                        self._focused_catalyst_response_repair_highest_priority_repair_id()
                    ),
                    "focused_catalyst_response_repair_next_operator_action": (
                        self._focused_catalyst_response_repair_next_operator_action()
                    ),
                    "focused_catalyst_response_merge_can_emit_candidate": (
                        self._focused_catalyst_response_merge_can_emit_candidate()
                    ),
                    "focused_catalyst_response_merge_can_submit_candidate_as_FIELD_ACTIVATION_RESPONSE_PATH": (
                        self._focused_catalyst_response_merge_can_submit_candidate_as_FIELD_ACTIVATION_RESPONSE_PATH()
                    ),
                    "focused_catalyst_response_merge_candidate_availability_status": (
                        self._focused_catalyst_response_merge_candidate_availability_status()
                    ),
                    "focused_catalyst_response_merge_candidate_preflight_submit_ready": (
                        self._focused_catalyst_response_merge_candidate_preflight_submit_ready()
                    ),
                    "focused_catalyst_response_merge_candidate_self_declared_submit_ready": (
                        self._focused_catalyst_response_merge_candidate_self_declared_submit_ready()
                    ),
                    "focused_catalyst_response_merge_candidate_submit_ready_semantics": (
                        self._focused_catalyst_response_merge_candidate_submit_ready_semantics()
                    ),
                    "focused_catalyst_response_merge_can_route_to_agent51_field_proxy_holdout": (
                        self._focused_catalyst_response_merge_can_route_to_agent51_field_proxy_holdout()
                    ),
                    "catalyst_field_package_slice_status": self._catalyst_field_package_slice_status(),
                    "catalyst_field_package_slice_preflight_pass": (
                        self._catalyst_field_package_slice_preflight_pass()
                    ),
                    "catalyst_field_package_slice_matched_batch_count": (
                        self._catalyst_field_package_slice_matched_batch_count()
                    ),
                    "catalyst_field_package_slice_template_dir": self._catalyst_field_package_slice_template_dir(),
                    "catalyst_field_package_slice_can_route_to_r7_field_package_patch_candidate": (
                        self._catalyst_field_package_slice_can_route_to_r7_field_package_patch_candidate()
                    ),
                    "catalyst_field_package_slice_can_route_to_agent51_field_proxy_holdout": (
                        self._catalyst_field_package_slice_can_route_to_agent51_field_proxy_holdout()
                    ),
                    "catalyst_slice_r7_patch_candidate_status": (
                        self._catalyst_slice_r7_patch_candidate_status()
                    ),
                    "catalyst_slice_r7_patch_candidate_materialized": (
                        self._catalyst_slice_r7_patch_candidate_materialized()
                    ),
                    "catalyst_slice_r7_patch_candidate_preflight_status": (
                        self._catalyst_slice_r7_patch_candidate_preflight_status()
                    ),
                    "catalyst_slice_r7_patch_candidate_remaining_gap_count": (
                        self._catalyst_slice_r7_patch_candidate_remaining_gap_count()
                    ),
                    "catalyst_slice_r7_patch_candidate_can_submit_as_REAL_FIELD_REPLAY_PACKAGE_DIR": (
                        self._catalyst_slice_r7_patch_candidate_can_submit_as_REAL_FIELD_REPLAY_PACKAGE_DIR()
                    ),
                    "control_replay_stress_status": self._control_replay_stress_status(),
                    "core_score": quantified_core_score_gate["core_score"],
                    "iteration_delta": quantified_core_score_gate["iteration_delta"],
                    "iteration_validity_status": quantified_core_score_gate["iteration_validity_status"],
                    "stage_decision": quantified_core_score_gate["stage_decision"],
                },
                "evidence_matrix_status": evidence_matrix_status,
            },
        )

    @staticmethod
    def _governance_principles() -> list[str]:
        return [
            "宏观架构原则：先搭系统骨架，再补局部细节；每项工作都必须映射到现场对象、观测、状态估计、机理证据、诊断决策、闭环执行或验证治理层。",
            "第一性原理：所有工作必须提升可观测、可控、可解释、可验证、可工程化或可演化中的至少一种核心能力。",
            "边际价值原则：优先处理能改变观测基础、状态估计、证据链、闭环控制可信度和工程落地路径的任务。",
            "证据分层原则：区分仿真成立、文献支持、开源方法启发和真实现场待验证。",
            "架构收敛原则：agent 不是越多越好；若新增模块不能改善接口、证据链、控制链或验证链，应优先合并、冻结或进入 backlog。",
            "低摩擦自我打断原则：自我打断不是模仿用户实时纠偏；只有硬风险或阶段边界才允许深度复盘，普通新想法只进入延迟 backlog，不重排当前小闭环。",
        ]

    @staticmethod
    def _default_backlog() -> list[dict[str, object]]:
        return [
            {
                "task_id": "P1_agent48_comparable_sparse_sensor_placement",
                "title": "Agent48 稀疏感知从启发式升级为可比较布点优化",
                "category": "sparse_sensing",
                "model_core_relevance": 0.98,
                "downstream_chain_impact": 0.96,
                "scientific_value": 0.90,
                "engineering_feasibility": 0.78,
                "verification_readiness": 0.76,
                "avoid_presentation_bias": 1.00,
                "next_experiment": "用候选传感器-节点矩阵比较 greedy、D-optimal、SSPOR/SSPOC 风格选择和成本约束 Pareto 前沿。",
                "metrics": ["state_observability", "reconstruction_gain", "weak_state_coverage", "total_cost_index"],
                "failure_boundary": "无真实拓扑、水力停留时间和维护可达性时只能作为 synthetic topology prior。",
            },
            {
                "task_id": "P2_catalyst_activity_weak_observability_proxy",
                "title": "catalyst_activity 弱观测增强",
                "category": "weak_target_observability",
                "model_core_relevance": 0.96,
                "downstream_chain_impact": 0.94,
                "scientific_value": 0.88,
                "engineering_feasibility": 0.74,
                "verification_readiness": 0.72,
                "avoid_presentation_bias": 1.00,
                "next_experiment": "构建 UV254/ORP/浊度/压降/停留时间的催化剂活性代理特征，并用分层 coverage 检查能否解除 Agent49 保护性阻断。",
                "metrics": ["catalyst_activity_observability", "weak_state_coverage", "policy_block_rate", "field_label_need"],
                "failure_boundary": "没有催化剂活性、再生、压降和离线标签时只能证明代理变量设计合理，不能证明催化剂真实衰减。",
            },
            {
                "task_id": "P3_agent49_replay_ready_offline_evaluation",
                "title": "Agent49 多设施协同控制升级到 replay-ready 离线评估",
                "category": "multi_facility_control",
                "model_core_relevance": 0.95,
                "downstream_chain_impact": 0.92,
                "scientific_value": 0.86,
                "engineering_feasibility": 0.75,
                "verification_readiness": 0.70,
                "avoid_presentation_bias": 1.00,
                "next_experiment": "定义多节点 state-action-reward replay schema，并离线评估 joint_action_accuracy、reward_regret、保护动作误触发成本。",
                "metrics": ["joint_action_accuracy", "reward_regret", "distilled_policy_accuracy", "field_replay_coverage"],
                "failure_boundary": "synthetic policy 不能替代现场策略；无 replay 时不能写入执行器或 release gate。",
            },
            {
                "task_id": "P4_minimal_grey_box_physics",
                "title": "灰箱物理机制最小增强",
                "category": "grey_box_physics",
                "model_core_relevance": 0.90,
                "downstream_chain_impact": 0.86,
                "scientific_value": 0.88,
                "engineering_feasibility": 0.70,
                "verification_readiness": 0.68,
                "avoid_presentation_bias": 1.00,
                "next_experiment": "加入停留时间、一级/准一级反应、基质抑制、催化剂衰减和副产物风险的最小参数层。",
                "metrics": ["mass_balance_residual", "residence_time_error", "grey_box_residual", "byproduct_risk_flag"],
                "failure_boundary": "参数未由现场或文献范围校准前只能作为先验约束，不可当作实证机理。",
            },
            {
                "task_id": "P5_soft_sensor_node_modality_missingness",
                "title": "软传感与 node-modality/missingness 矩阵耦合",
                "category": "soft_sensor_matrix",
                "model_core_relevance": 0.88,
                "downstream_chain_impact": 0.84,
                "scientific_value": 0.82,
                "engineering_feasibility": 0.76,
                "verification_readiness": 0.74,
                "avoid_presentation_bias": 1.00,
                "next_experiment": "把 Agent48 输出的节点-模态矩阵变成软传感输入契约，加入缺测掩码、低频采样和延迟特征。",
                "metrics": ["masked_mae", "interval_coverage", "missingness_robustness", "latency_aware_error"],
                "failure_boundary": "缺测机制若来自 synthetic dropout，不能外推为真实传感器污染、漂移或通信失败。",
            },
            {
                "task_id": "P6_reasonable_knowledge_graph_upgrade",
                "title": "知识库升级为可推理 KG",
                "category": "knowledge_graph",
                "model_core_relevance": 0.82,
                "downstream_chain_impact": 0.78,
                "scientific_value": 0.84,
                "engineering_feasibility": 0.72,
                "verification_readiness": 0.66,
                "avoid_presentation_bias": 0.96,
                "next_experiment": "把污染物、基质、材料、过程条件、可观测信号、隐藏状态和证据等级转成可追溯边。",
                "metrics": ["field_supported_edge_ratio", "evidence_traceability", "constraint_hit_rate", "claim_verification_pass_rate"],
                "failure_boundary": "KG 能约束假设和解释路径，但没有现场标签时不能证明控制效果。",
            },
            {
                "task_id": "P7_engineering_constraints_in_reward_and_arbitration",
                "title": "工程执行约束进入 reward 和仲裁",
                "category": "engineering_constraints",
                "model_core_relevance": 0.84,
                "downstream_chain_impact": 0.80,
                "scientific_value": 0.76,
                "engineering_feasibility": 0.82,
                "verification_readiness": 0.70,
                "avoid_presentation_bias": 1.00,
                "next_experiment": "把阀门切换频率、暂存容量、泵能耗、人工干预和失败回退成本写入 Agent49 reward。",
                "metrics": ["actuator_switch_count", "storage_violation_rate", "energy_cost_index", "human_review_rate"],
                "failure_boundary": "无 PLC/SCADA 点表和设备约束时只能做候选动作过滤，不能做现场执行计划。",
            },
            {
                "task_id": "L1_ppt_word_showcase_polish",
                "title": "PPT、Word、索引和展示材料美化",
                "category": "presentation",
                "model_core_relevance": 0.06,
                "downstream_chain_impact": 0.04,
                "scientific_value": 0.04,
                "engineering_feasibility": 0.45,
                "verification_readiness": 0.08,
                "avoid_presentation_bias": 0.02,
                "next_experiment": "不作为当前核心实验；仅在模型指标更新后同步表达层。",
                "metrics": ["none_for_model_core"],
                "failure_boundary": "不会提升观测、推理、控制或验证能力，必须进入低优先级 backlog。",
            },
            {
                "task_id": "P8_cross_agent_core_reconnection",
                "title": "把 KG/灰箱/布点/工程补丁接回主闭环链条",
                "category": "cross_agent_reconnection",
                "model_core_relevance": 0.70,
                "downstream_chain_impact": 0.72,
                "scientific_value": 0.76,
                "engineering_feasibility": 0.70,
                "verification_readiness": 0.62,
                "avoid_presentation_bias": 1.00,
                "next_experiment": "在 KG evidence path 成为共同接口后，逐步把 Agent53 physics prior、Agent54 layout mask、Agent55 engineering patch 接入主闭环 Agent1-9。",
                "metrics": [
                    "main_chain_prior_consumption_rate",
                    "kg_path_to_action_link_rate",
                    "grey_box_prior_used_by_soft_sensor",
                    "engineering_patch_used_by_arbitration",
                ],
                "failure_boundary": "这是模型链路联动改造，不能替代 field validation；只允许改变先验、解释和候选排序。",
            },
            {
                "task_id": "P9_field_validation_queue_alignment",
                "title": "把 KG field_validation_queue 对齐到真实数据接口与回放门控",
                "category": "field_validation_schema",
                "model_core_relevance": 0.72,
                "downstream_chain_impact": 0.76,
                "scientific_value": 0.82,
                "engineering_feasibility": 0.74,
                "verification_readiness": 0.68,
                "avoid_presentation_bias": 1.00,
                "next_experiment": "把 Agent56 的每条 field_validation_need 映射到 Agent30/42/44/45 的表、字段、gate 和 replay 验收指标。",
                "metrics": [
                    "field_need_to_table_coverage",
                    "field_need_to_gate_coverage",
                    "unmapped_validation_need_count",
                    "claim_upgrade_blocker_count",
                ],
                "failure_boundary": "这只是验证接口对齐；没有真实 field 包仍不能证明模型现场有效。",
            },
            {
                "task_id": "P10_claim_specific_field_package_and_source_basis",
                "title": "把对齐后的验证需求升级成 claim-specific 现场采集包和 source_basis 补全任务",
                "category": "field_package_source_basis",
                "model_core_relevance": 0.70,
                "downstream_chain_impact": 0.72,
                "scientific_value": 0.84,
                "engineering_feasibility": 0.70,
                "verification_readiness": 0.72,
                "avoid_presentation_bias": 1.00,
                "next_experiment": "按 Agent58 mapping_table 把 optional claim 字段提升为必采字段，生成最小 field package 验收矩阵，并列出 source_basis 待补文献/现场证据。",
                "metrics": [
                    "claim_specific_required_field_coverage",
                    "source_basis_completion_rate",
                    "minimal_field_package_pass_rate",
                    "field_claim_upgrade_blocker_count",
                ],
                "failure_boundary": "没有真实 field 数据时只能形成采集包和证据补全任务，不能升级为现场结论。",
            },
            {
                "task_id": "P11_source_basis_detail_or_real_field_package_import",
                "title": "补 source_basis 细节或导入真实 field package 进入证据链",
                "category": "field_evidence_completion",
                "model_core_relevance": 0.72,
                "downstream_chain_impact": 0.74,
                "scientific_value": 0.86,
                "engineering_feasibility": 0.68,
                "verification_readiness": 0.78,
                "avoid_presentation_bias": 1.00,
                "next_experiment": "若暂无真实数据，先补每个 source_basis 的具体文献/参数/适用边界；若已有真实包，则走 Agent44->42->43->45 证据链。",
                "metrics": [
                    "citation_detail_completion_rate",
                    "source_basis_parameter_boundary_coverage",
                    "field_replay_import_pass",
                    "evidence_chain_pass",
                ],
                "failure_boundary": "source_basis 细化是文献证据，不替代 field replay；真实包导入通过也不自动授权 release gate。",
            },
        ]

    def _priority_ranking(self) -> list[dict[str, object]]:
        ranked: list[dict[str, object]] = []
        for raw_item in self.backlog:
            item = dict(raw_item)
            if item.get("task_id") == "P1_agent48_comparable_sparse_sensor_placement" and self._agent48_comparable_baseline_ready():
                item["implementation_status"] = "synthetic_comparison_baseline_ready"
                item["elevation_reason"] = "Agent48 already reports comparable greedy/reconstruction/classification/topology strategies."
                item["model_core_relevance"] = 0.78
                item["downstream_chain_impact"] = 0.76
                item["scientific_value"] = 0.78
                item["engineering_feasibility"] = 0.74
                item["verification_readiness"] = 0.70
                item["next_experiment"] = (
                    "P1 的 synthetic 多策略比较基线已形成；除非补入真实 field topology，否则下一轮优先转向 catalyst_activity 弱观测代理。"
                )
            if item.get("task_id") == "P1_agent48_comparable_sparse_sensor_placement" and self._observation_contract_baseline_ready():
                item["implementation_status"] = "consumed_by_R2_observation_contract_ready_needs_field_topology"
                item["elevation_reason"] = (
                    "R2 observation contract has already consumed Agent48 sparse placement into a budget-aware "
                    f"contract; proxy_enhanced_weak_state_coverage={self._observation_contract_weak_state_coverage():.3f}. "
                    "Do not restart P1 unless real field topology or installability data are imported."
                )
                item["model_core_relevance"] = 0.62
                item["downstream_chain_impact"] = 0.62
                item["scientific_value"] = 0.70
                item["engineering_feasibility"] = 0.62
                item["verification_readiness"] = 0.54
                item["next_experiment"] = (
                    "P1 已被 R2 观测契约消费；内部不要重复做布点启发式，下一步只在真实 topology/installability 数据进入后刷新。"
                )
            if item.get("task_id") == "P2_catalyst_activity_weak_observability_proxy" and self._catalyst_proxy_baseline_ready():
                item["implementation_status"] = "synthetic_proxy_design_ready_needs_field_labels"
                item["elevation_reason"] = (
                    "Agent51 already provides a catalyst_activity proxy design baseline; "
                    f"after_patch_observability={self._catalyst_proxy_after_patch():.3f}. "
                    "Return to P2 only when field_proxy_holdout labels are available."
                )
                item["model_core_relevance"] = 0.78
                item["downstream_chain_impact"] = 0.78
                item["scientific_value"] = 0.82
                item["engineering_feasibility"] = 0.72
                item["verification_readiness"] = 0.64
                item["next_experiment"] = (
                    "Agent51 的 synthetic proxy baseline 已形成；P2 暂不继续堆 proxy，"
                    "除非补入 field_proxy_holdout，否则下一轮优先转向 Agent49 replay-ready 离线评估。"
                )
            if item.get("task_id") == "P2_catalyst_activity_weak_observability_proxy" and self._observation_contract_baseline_ready():
                item["implementation_status"] = "consumed_by_R2_observation_contract_ready_needs_proxy_holdout_labels"
                item["elevation_reason"] = (
                    "R2 has merged the Agent51 catalyst proxy patch into the shared observation contract; "
                    f"proxy_enhanced_weak_state_coverage={self._observation_contract_weak_state_coverage():.3f}. "
                    "More internal proxy design has low marginal value before field proxy holdout labels."
                )
                item["model_core_relevance"] = 0.64
                item["downstream_chain_impact"] = 0.64
                item["scientific_value"] = 0.74
                item["engineering_feasibility"] = 0.60
                item["verification_readiness"] = 0.52
                item["next_experiment"] = (
                    "P2 已被 R2 观测契约消费；下一步不是继续堆代理变量，而是等待 catalyst_activity/proxy holdout labels 或转向控制 replay。"
                )
            if (
                item.get("task_id") == "P2_catalyst_activity_weak_observability_proxy"
                and not self._catalyst_proxy_baseline_ready()
                and not self._observation_contract_baseline_ready()
                and self._catalyst_is_weak()
            ):
                item["elevation_reason"] = (
                    f"Agent48 weak_state_coverage={self._weak_state_coverage():.3f}, "
                    f"catalyst_activity_observability={self._catalyst_activity_observability():.3f}"
                )
                item["model_core_relevance"] = max(float(item["model_core_relevance"]), 0.99)
                item["downstream_chain_impact"] = max(float(item["downstream_chain_impact"]), 0.97)
                item["verification_readiness"] = max(float(item["verification_readiness"]), 0.78)
            if item.get("task_id") == "P3_agent49_replay_ready_offline_evaluation" and self._replay_evaluation_baseline_ready():
                item["implementation_status"] = "synthetic_replay_evaluation_ready_needs_field_replay"
                item["elevation_reason"] = (
                    "Agent52 already provides a replay-ready synthetic offline evaluation baseline; "
                    f"joint_action_accuracy={self._replay_joint_action_accuracy():.3f}. "
                    "Return to P3 only when field multi-node replay is available or when Agent49 reward priors are being patched."
                )
                item["model_core_relevance"] = 0.74
                item["downstream_chain_impact"] = 0.72
                item["scientific_value"] = 0.78
                item["engineering_feasibility"] = 0.70
                item["verification_readiness"] = 0.60
                item["next_experiment"] = (
                    "Agent52 的 synthetic replay-ready baseline 已形成；无真实多节点 field replay 时，"
                    "下一轮优先转向 P4 灰箱物理机制或 P5 软传感 node-modality/missingness 耦合。"
                )
            if item.get("task_id") == "P3_agent49_replay_ready_offline_evaluation" and self._control_replay_stress_baseline_ready():
                item["implementation_status"] = "consumed_by_R3_counterfactual_stress_ready_needs_field_replay"
                item["elevation_reason"] = (
                    "R3 counterfactual stress has already consumed Agent49/52 replay into guardrail stress cases; "
                    f"status={self._control_replay_stress_status()}. "
                    "Repeat P3 only after field state-action-reward replay is imported or when a new guardrail prior is added."
                )
                item["model_core_relevance"] = 0.64
                item["downstream_chain_impact"] = 0.64
                item["scientific_value"] = 0.76
                item["engineering_feasibility"] = 0.62
                item["verification_readiness"] = 0.56
                item["next_experiment"] = (
                    "P3 已被 R3 反事实压力测试消费；不要重复 synthetic replay，等待 field replay 或执行 R3b/R3c 之后的复核链。"
                )
            if item.get("task_id") == "P4_minimal_grey_box_physics" and self._grey_box_physics_baseline_ready():
                item["implementation_status"] = self._grey_box_physics_status()
                item["elevation_reason"] = (
                    "Agent53 already provides a minimal grey-box physics synthetic prior; "
                    f"mean_grey_box_residual={self._mean_grey_box_residual():.3f}. "
                    "Return to P4 only when field RTD/lab/catalyst/byproduct calibration data are available."
                )
                item["model_core_relevance"] = 0.78
                item["downstream_chain_impact"] = 0.76
                item["scientific_value"] = 0.82
                item["engineering_feasibility"] = 0.72
                item["verification_readiness"] = 0.64
                item["next_experiment"] = (
                    "Agent53 的 synthetic grey-box physics prior 已形成；无 field 物理校准时，"
                    "下一轮优先转向 P5 软传感 node-modality/missingness 耦合。"
                )
            if item.get("task_id") == "P5_soft_sensor_node_modality_missingness" and self._soft_sensor_matrix_baseline_ready():
                item["implementation_status"] = self._soft_sensor_matrix_status()
                item["elevation_reason"] = (
                    "Agent54 already provides a layout-aware soft sensor matrix synthetic contract; "
                    f"missingness_robustness_score={self._missingness_robustness_score():.3f}. "
                    "Return to P5 when field node-specific values and missingness replay are available."
                )
                item["model_core_relevance"] = 0.78
                item["downstream_chain_impact"] = 0.74
                item["scientific_value"] = 0.80
                item["engineering_feasibility"] = 0.72
                item["verification_readiness"] = 0.62
                item["next_experiment"] = (
                    "Agent54 的 synthetic layout-aware soft sensor contract 已形成；无 field missingness replay 时，"
                    "下一轮优先转向 P7 工程执行约束进入 reward 和仲裁。"
                )
            if item.get("task_id") == "P5_soft_sensor_node_modality_missingness" and self._observation_contract_baseline_ready():
                item["implementation_status"] = "consumed_by_R2_observation_contract_ready_needs_field_missingness"
                item["elevation_reason"] = (
                    "R2 already couples Agent54 layout/missingness terms with the selected node-modality contract; "
                    f"missingness_after_patch={self._observation_contract_missingness_after_patch():.3f}. "
                    "Further P5 changes need field node-specific missingness replay."
                )
                item["model_core_relevance"] = 0.62
                item["downstream_chain_impact"] = 0.60
                item["scientific_value"] = 0.72
                item["engineering_feasibility"] = 0.60
                item["verification_readiness"] = 0.52
                item["next_experiment"] = (
                    "P5 已被 R2 观测契约消费；不要重复补矩阵字段，除非导入 field missingness replay。"
                )
            if item.get("task_id") == "P7_engineering_constraints_in_reward_and_arbitration" and self._engineering_constraints_baseline_ready():
                item["implementation_status"] = self._engineering_constraints_status()
                item["elevation_reason"] = (
                    "Agent55 already provides an engineering execution constraint patch; "
                    f"mean_execution_feasibility={self._engineering_mean_execution_feasibility():.3f}. "
                    "Return to P7 only when PLC/SCADA points, SOP and field execution replay are available."
                )
                item["model_core_relevance"] = 0.74
                item["downstream_chain_impact"] = 0.72
                item["scientific_value"] = 0.72
                item["engineering_feasibility"] = 0.70
                item["verification_readiness"] = 0.60
                item["next_experiment"] = (
                    "Agent55 的 synthetic engineering reward/arbitration patch 已形成；"
                    "无现场执行 replay 时，下一轮优先转向 P6 可推理 KG 或等待工程执行日志。"
                )
            if item.get("task_id") == "P6_reasonable_knowledge_graph_upgrade" and self._kg_reasoning_baseline_ready():
                item["implementation_status"] = self._kg_reasoning_status()
                item["elevation_reason"] = (
                    "Agent56 already provides typed KG evidence paths and action constraint patches; "
                    f"evidence_traceability={self._kg_evidence_traceability():.3f}, "
                    f"constraint_hit_rate={self._kg_constraint_hit_rate():.3f}. "
                    "Return to P6 only when source_basis or field-supported KG edges are being expanded."
                )
                item["model_core_relevance"] = 0.74
                item["downstream_chain_impact"] = 0.72
                item["scientific_value"] = 0.78
                item["engineering_feasibility"] = 0.70
                item["verification_readiness"] = 0.60
                item["next_experiment"] = (
                    "Agent56 的 KG reasoning baseline 已形成；下一轮优先处理跨 agent 主链回接，"
                    "同时等待 field-supported KG edges。"
                )
            if item.get("task_id") == "P8_cross_agent_core_reconnection" and self._kg_reasoning_baseline_ready():
                item["elevation_reason"] = (
                    "The retrospective exposed that several high-value core agents remain partially parallel; "
                    "KG reasoning is now available as a shared evidence interface."
                )
                item["model_core_relevance"] = 0.86
                item["downstream_chain_impact"] = 0.88
                item["scientific_value"] = 0.82
                item["engineering_feasibility"] = 0.74
                item["verification_readiness"] = 0.66
                item["next_experiment"] = (
                    "优先把 Agent53 灰箱 prior 和 Agent54 layout/missingness 合同接入主软传感/控制链，"
                    "再检查 Agent49/55 是否被 Arbitration 主链完整消费。"
                )
            if item.get("task_id") == "P8_cross_agent_core_reconnection" and self._main_chain_reconnection_baseline_ready():
                item["implementation_status"] = self._main_chain_reconnection_status()
                item["elevation_reason"] = (
                    "Agent57 already reports main-chain prior consumption; "
                    f"main_chain_prior_consumption_rate={self._main_chain_prior_consumption_rate():.3f}. "
                    "Return to P8 only when a new core prior is not consumed by Agent1-10."
                )
                item["model_core_relevance"] = 0.74
                item["downstream_chain_impact"] = 0.72
                item["scientific_value"] = 0.76
                item["engineering_feasibility"] = 0.72
                item["verification_readiness"] = 0.60
                item["next_experiment"] = (
                    "Agent57 已完成 synthetic 主链回接审计；下一轮优先把 field_validation_queue 对齐到真实数据接口。"
                )
            if item.get("task_id") == "P9_field_validation_queue_alignment" and self._main_chain_reconnection_baseline_ready():
                item["elevation_reason"] = (
                    "After main-chain reconnection, the highest marginal value is mapping each validation need "
                    "to concrete field tables and replay gates."
                )
                item["model_core_relevance"] = 0.86
                item["downstream_chain_impact"] = 0.86
                item["scientific_value"] = 0.86
                item["engineering_feasibility"] = 0.76
                item["verification_readiness"] = 0.74
                item["next_experiment"] = (
                    "逐条读取 Agent56 field_validation_queue，映射到 Agent30/42/44/45 字段、gate、replay 验收和失败边界。"
                )
            if item.get("task_id") == "P9_field_validation_queue_alignment" and self._field_validation_alignment_baseline_ready():
                item["implementation_status"] = self._field_validation_alignment_status()
                item["elevation_reason"] = (
                    "Agent58 already maps the KG validation queue to field tables and gates; "
                    f"table_coverage={self._field_need_to_table_coverage():.3f}, "
                    f"gate_coverage={self._field_need_to_gate_coverage():.3f}. "
                    "Return to P9 only when new validation needs appear or an unmapped need is detected."
                )
                item["model_core_relevance"] = 0.70
                item["downstream_chain_impact"] = 0.70
                item["scientific_value"] = 0.78
                item["engineering_feasibility"] = 0.72
                item["verification_readiness"] = 0.62
                item["next_experiment"] = (
                    "P9 的接口对齐基线已形成；下一轮优先把 claim-specific 字段提升为最小现场采集包和 source_basis 补全任务。"
                )
            if item.get("task_id") == "P10_claim_specific_field_package_and_source_basis" and self._field_validation_alignment_baseline_ready():
                item["elevation_reason"] = (
                    "Agent58 exposed the next bottleneck: mapped validation needs still need claim-specific field package "
                    "requirements and source_basis completion before field claims can be upgraded."
                )
                item["model_core_relevance"] = 0.84
                item["downstream_chain_impact"] = 0.84
                item["scientific_value"] = 0.88
                item["engineering_feasibility"] = 0.74
                item["verification_readiness"] = 0.76
                item["next_experiment"] = (
                    "读取 Agent58 validation_mapping_table，把 detection_limit、result_time_min、sensor_status 等 claim 字段写入最小 field package 矩阵，"
                    "同时列出每条 KG supporting entry 需要补齐的 source_basis 和 field evidence。"
                )
            if item.get("task_id") == "P10_claim_specific_field_package_and_source_basis" and self._claim_specific_package_baseline_ready():
                item["implementation_status"] = self._claim_specific_package_status()
                item["elevation_reason"] = (
                    "Agent59 already produced the claim-specific field package matrix; "
                    f"required_field_coverage={self._claim_specific_required_field_coverage():.3f}, "
                    f"source_basis_completion_rate={self._source_basis_completion_rate():.3f}. "
                    "Return to P10 only when new validation mappings are added."
                )
                item["model_core_relevance"] = 0.72
                item["downstream_chain_impact"] = 0.72
                item["scientific_value"] = 0.80
                item["engineering_feasibility"] = 0.72
                item["verification_readiness"] = 0.64
                item["next_experiment"] = (
                    "P10 的采集包矩阵已形成；下一轮优先补 source_basis 细节或导入真实 field package。"
                )
            if item.get("task_id") == "P11_source_basis_detail_or_real_field_package_import" and self._claim_specific_package_baseline_ready():
                source_basis_complete = self._source_basis_detail_ready()
                if source_basis_complete:
                    if self._external_field_blocker_active():
                        item["implementation_status"] = "waiting_on_real_field_package_external_blocker"
                        item["external_blocker"] = True
                        item["blocked_by"] = "real_field_package_import_or_field_replay"
                        item["elevation_reason"] = (
                            "source_basis detail and claim-specific schema are complete; unified/R7 gates show the remaining "
                            "blocker is external real field package import, not an internal citation or schema task."
                        )
                        item["model_core_relevance"] = 0.54
                        item["downstream_chain_impact"] = 0.54
                        item["scientific_value"] = 0.72
                        item["engineering_feasibility"] = 0.48
                        item["verification_readiness"] = 0.48
                        item["next_experiment"] = (
                            "停止内部补 source_basis/citation；若用户提供 data_origin=field 的真实包，则运行 R7/Agent44->42->43->45。"
                            "若没有真实包，把 P11 放入 external blocker backlog，并转向 Agent60/R2/R3 指向的内部模型链路。"
                        )
                        item["failure_boundary"] = (
                            "这是外部 field package 等待态；不能用 synthetic/template 代替真实包，不能升级 field-supported claim，"
                            "不能写 actuator 或 release gate。"
                        )
                    else:
                        item["implementation_status"] = "source_basis_detail_ready_needs_real_field_package_import"
                        item["elevation_reason"] = (
                            "Agent59/unified gate report source_basis detail is complete; the remaining P11 blocker is real "
                            "field package import/replay, not more citation polishing."
                        )
                        item["model_core_relevance"] = 0.84
                        item["downstream_chain_impact"] = 0.84
                        item["scientific_value"] = 0.86
                        item["engineering_feasibility"] = 0.70
                        item["verification_readiness"] = 0.82
                        item["next_experiment"] = (
                            "source_basis detail 已闭合；不要继续补 citation。若有真实 field package，运行 Agent44->42->43->45 "
                            "和统一 evidence gate；若没有真实包，只能保持 field blocker，并把新工作转向不伪造 field evidence 的接口/验证增强。"
                        )
                        item["failure_boundary"] = (
                            "source_basis 细化已是文献证据完成态；没有真实 field package 时，不能升级 field-supported claim、"
                            "不能写 actuator 或 release gate。"
                        )
                else:
                    item["elevation_reason"] = (
                        "Agent59 shows schema coverage is ready but source basis and real field evidence still block claim upgrade."
                    )
                    item["model_core_relevance"] = 0.86
                    item["downstream_chain_impact"] = 0.84
                    item["scientific_value"] = 0.90
                    item["engineering_feasibility"] = 0.72
                    item["verification_readiness"] = 0.80
                    item["next_experiment"] = (
                        "先补 kb_sensor_limited_release_evidence 的具体 citation/参数/适用边界；"
                        "若用户提供真实现场包，则运行 Agent44->42->43->45 并回写 field-supported evidence。"
                    )
            item.update(self._score_item(item))
            ranked.append(item)
        ranked.sort(key=lambda entry: (-float(entry["marginal_value_score"]), str(entry["task_id"])))
        for rank, item in enumerate(ranked, start=1):
            item["rank"] = rank
        return ranked

    @staticmethod
    def _score_item(item: dict[str, object]) -> dict[str, float]:
        fields = {
            "model_core_relevance": float(item.get("model_core_relevance", 0.0)),
            "downstream_chain_impact": float(item.get("downstream_chain_impact", 0.0)),
            "scientific_value": float(item.get("scientific_value", 0.0)),
            "engineering_feasibility": float(item.get("engineering_feasibility", 0.0)),
            "verification_readiness": float(item.get("verification_readiness", 0.0)),
            "avoid_presentation_bias": float(item.get("avoid_presentation_bias", 0.0)),
        }
        score = (
            0.22 * fields["model_core_relevance"]
            + 0.18 * fields["downstream_chain_impact"]
            + 0.18 * fields["scientific_value"]
            + 0.15 * fields["engineering_feasibility"]
            + 0.15 * fields["verification_readiness"]
            + 0.12 * fields["avoid_presentation_bias"]
        )
        fields["marginal_value_score"] = round(score, 3)
        return fields

    def _quantified_core_score_gate(
        self,
        *,
        priority_ranking: list[dict[str, object]],
        evidence_matrix_status: dict[str, object],
        blocked_reasons: list[str],
        external_activation_contract: dict[str, object] | None = None,
    ) -> dict[str, object]:
        hidden_state_coverage_ledger = self._hidden_state_coverage_ledger()
        ability_scores = self._core_ability_scores(
            evidence_matrix_status,
            hidden_state_coverage_ledger=hidden_state_coverage_ledger,
        )
        core_score = round(
            sum(CORE_ABILITY_WEIGHTS[name] * ability_scores[name] for name in CORE_ABILITY_WEIGHTS),
            3,
        )
        previous_core_score = self._previous_core_score()
        iteration_delta = None if previous_core_score is None else round(core_score - previous_core_score, 3)
        explicit_hard_blocker_resolved = bool(self.current_work_item.get("resolved_p1_p2_blocker", False)) or bool(
            self.current_work_item.get("resolved_hard_blocker", False)
        )
        changed_contract_or_gate = self._changed_contract_or_gate()
        evidence_boundary_preserved = not bool(self.current_work_item.get("writes_synthetic_as_field_claim", False))
        targeted_tests_passed = self._targeted_tests_passed()
        module_gate = self._module_stage_termination_gate(
            evidence_matrix_status,
            hidden_state_coverage_ledger=hidden_state_coverage_ledger,
        )
        previous_module_stage_status = self._previous_module_stage_status()
        module_stage_blocker_resolved = (
            previous_module_stage_status == "module_stage_needs_more_core_work"
            and module_gate["module_stage_status"] == "module_stage_complete"
        )
        hard_blocker_resolved = explicit_hard_blocker_resolved or module_stage_blocker_resolved
        top_score = float(priority_ranking[0]["marginal_value_score"]) if priority_ranking else 0.0
        field_blocker_present = any("field" in reason.lower() or "现场" in reason for reason in blocked_reasons)
        external_field_wait_state = self._external_field_blocker_active() and not any(
            not self._field_waiting_or_consumed_task(item) and not self._is_presentation_or_polish(item)
            for item in priority_ranking
        )

        if not evidence_boundary_preserved:
            validity_status = "invalid_iteration_evidence_boundary_violation"
            stage_decision = "interrupt_and_refocus"
            continue_expansion_allowed = False
        elif external_field_wait_state:
            validity_status = "valid_stage_boundary_external_field_wait"
            stage_decision = "stop_expansion_wait_for_real_field_package_or_new_core_interface"
            continue_expansion_allowed = False
        elif iteration_delta is None:
            validity_status = "baseline_recorded_needs_next_delta"
            stage_decision = "continue_core_work_with_quantified_baseline"
            continue_expansion_allowed = True
        elif iteration_delta >= 0.10 or hard_blocker_resolved:
            validity_status = "valid_iteration"
            stage_decision = "continue_to_next_highest_value_core_action"
            continue_expansion_allowed = True
        elif iteration_delta < 0.05:
            validity_status = "low_marginal_gain_without_hard_blocker"
            stage_decision = "stop_expansion_enter_review_or_backlog"
            continue_expansion_allowed = False
        else:
            validity_status = "partial_iteration_needs_stage_review"
            stage_decision = "run_stage_review_before_expansion"
            continue_expansion_allowed = False

        if module_gate["module_stage_status"] == "module_stage_complete" and top_score < 0.65:
            stage_decision = "module_stage_complete_switch_or_wait_for_field_validation"
            continue_expansion_allowed = False
        effective_iteration_gate = self._effective_iteration_gate(
            iteration_delta=iteration_delta,
            validity_status=validity_status,
            stage_decision=stage_decision,
            hard_blocker_resolved=hard_blocker_resolved,
            changed_contract_or_gate=changed_contract_or_gate,
            evidence_boundary_preserved=evidence_boundary_preserved,
            targeted_tests_passed=targeted_tests_passed,
            external_field_wait_state=external_field_wait_state,
            continue_expansion_allowed=continue_expansion_allowed,
        )

        return {
            "gate_id": "R8u68_quantified_core_score_and_hidden_state_termination_gate",
            "core_score_formula": (
                "0.18*observability + 0.16*controllability + 0.14*explainability + "
                "0.18*verifiability + 0.14*engineering_feasibility + "
                "0.10*evolvability + 0.10*protectability"
            ),
            "ability_weights": CORE_ABILITY_WEIGHTS,
            "ability_scores": ability_scores,
            "core_score": core_score,
            "previous_core_score": previous_core_score,
            "iteration_delta": iteration_delta,
            "hard_blocker_resolved": hard_blocker_resolved,
            "explicit_hard_blocker_resolved": explicit_hard_blocker_resolved,
            "previous_module_stage_status": previous_module_stage_status,
            "module_stage_blocker_resolved": module_stage_blocker_resolved,
            "changed_contract_or_gate": changed_contract_or_gate,
            "evidence_boundary_preserved": evidence_boundary_preserved,
            "targeted_tests_passed": targeted_tests_passed,
            "field_blocker_present": field_blocker_present,
            "external_field_wait_state": external_field_wait_state,
            "top_marginal_value_score": round(top_score, 3),
            "single_iteration_thresholds": {
                "valid_delta_min": 0.10,
                "review_delta_min": 0.05,
                "hard_blocker_override": True,
                "requires_contract_or_gate_change": True,
                "requires_targeted_tests": True,
                "requires_evidence_boundary_preserved": True,
            },
            "effective_iteration_gate": effective_iteration_gate,
            "iteration_validity_status": validity_status,
            "continue_expansion_allowed": continue_expansion_allowed,
            "stage_decision": stage_decision,
            "next_allowed_actions": self._next_allowed_actions_for_stage(
                stage_decision=stage_decision,
                external_activation_contract=external_activation_contract,
            ),
            "external_resume_conditions": self._external_resume_conditions_for_stage(
                stage_decision=stage_decision,
                external_activation_contract=external_activation_contract,
            ),
            "hidden_state_coverage_ledger": hidden_state_coverage_ledger,
            "module_stage_termination_gate": module_gate,
            "next_gate_action": self._next_gate_action(
                validity_status=validity_status,
                stage_decision=stage_decision,
                field_blocker_present=field_blocker_present,
            ),
            "no_write_boundaries": {
                "can_write_to_actuator": False,
                "can_write_to_release_gate": False,
                "actuator_write_requires": [
                    "field state-action-reward replay",
                    "operator review",
                    "engineering execution constraint validation",
                    "protective candidate post-review gate",
                ],
                "release_gate_write_requires": [
                    "field endpoint labels",
                    "field holdout/replay pass",
                    "offline lab confirmation",
                    "human release review",
                ],
            },
        }

    @staticmethod
    def _effective_iteration_gate(
        *,
        iteration_delta: float | None,
        validity_status: str,
        stage_decision: str,
        hard_blocker_resolved: bool,
        changed_contract_or_gate: bool,
        evidence_boundary_preserved: bool,
        targeted_tests_passed: bool,
        external_field_wait_state: bool,
        continue_expansion_allowed: bool,
    ) -> dict[str, object]:
        score_delta_pass = iteration_delta is not None and iteration_delta >= 0.10
        low_gain_without_hard_blocker = (
            iteration_delta is not None
            and iteration_delta < 0.05
            and not hard_blocker_resolved
            and not external_field_wait_state
        )
        review_band_without_hard_blocker = (
            iteration_delta is not None
            and 0.05 <= iteration_delta < 0.10
            and not hard_blocker_resolved
            and not external_field_wait_state
        )
        stage_boundary_termination_pass = (
            external_field_wait_state
            and stage_decision == "stop_expansion_wait_for_real_field_package_or_new_core_interface"
        )
        if not evidence_boundary_preserved:
            validity_basis = "evidence_boundary_violation"
        elif stage_boundary_termination_pass:
            validity_basis = "stage_boundary_external_wait_not_score_gain"
        elif iteration_delta is None:
            validity_basis = "baseline_recorded_needs_next_delta"
        elif score_delta_pass:
            validity_basis = "score_delta_pass"
        elif hard_blocker_resolved:
            validity_basis = "hard_blocker_resolved"
        elif low_gain_without_hard_blocker:
            validity_basis = "low_gain_without_hard_blocker"
        elif review_band_without_hard_blocker:
            validity_basis = "review_band_without_hard_blocker"
        else:
            validity_basis = validity_status

        effective_iteration_pass = bool(
            evidence_boundary_preserved
            and (
                stage_boundary_termination_pass
                or (
                    changed_contract_or_gate
                    and targeted_tests_passed
                    and (score_delta_pass or hard_blocker_resolved)
                )
            )
        )
        return {
            "valid_delta_min": 0.10,
            "review_delta_min": 0.05,
            "score_delta_pass": score_delta_pass,
            "hard_blocker_resolution_pass": bool(hard_blocker_resolved),
            "stage_boundary_termination_pass": stage_boundary_termination_pass,
            "low_gain_without_hard_blocker": low_gain_without_hard_blocker,
            "review_band_without_hard_blocker": review_band_without_hard_blocker,
            "contract_or_gate_change_pass": bool(changed_contract_or_gate),
            "targeted_tests_passed": bool(targeted_tests_passed),
            "evidence_boundary_pass": bool(evidence_boundary_preserved),
            "micro_iteration_evidence_complete": bool(
                changed_contract_or_gate and targeted_tests_passed and evidence_boundary_preserved
            ),
            "effective_iteration_pass": effective_iteration_pass,
            "expansion_stop_required": not bool(continue_expansion_allowed),
            "validity_basis": validity_basis,
            "interpretation": (
                "Stage-boundary external wait is a valid termination condition, not a score-gain claim."
                if stage_boundary_termination_pass
                else "Use score delta or hard-blocker resolution to justify continued expansion."
            ),
        }

    def _next_allowed_actions_for_stage(
        self,
        *,
        stage_decision: str,
        external_activation_contract: dict[str, object] | None,
    ) -> list[dict[str, object]]:
        if stage_decision != "stop_expansion_wait_for_real_field_package_or_new_core_interface":
            return [
                {
                    "action_type": "continue_or_review_by_stage_gate",
                    "stage_decision": stage_decision,
                    "boundary": "Follow quantified core score gate before adding new model complexity.",
                }
            ]

        actions: list[dict[str, object]] = []
        router_rows = {
            str(row.get("channel_id", "unknown_channel")): row
            for row in self._external_activation_router_route_rows()
        }
        contract_channels = {
            str(channel.get("channel_id", "unknown_channel")): channel
            for channel in (external_activation_contract or {}).get("channels", [])
            if isinstance(channel, dict)
        }
        for action in (external_activation_contract or {}).get("next_operator_actions", []):
            if not isinstance(action, dict):
                continue
            channel_id = str(action.get("channel_id", ""))
            router_row = router_rows.get(channel_id, {})
            channel = contract_channels.get(channel_id, {})
            route_class = self._external_activation_action_route_class(channel_id)
            route_ready = bool(router_row.get("route_ready", False))
            can_resume_model_chain = bool(channel.get("can_resume_model_chain", False))
            handoff_only = route_class == "formal_search_handoff_only"
            catalyst_candidate = router_row.get("catalyst_slice_r7_patch_candidate", {})
            if not isinstance(catalyst_candidate, dict):
                catalyst_candidate = {}
            field_activation_upstream = router_row.get("field_activation_upstream_gate", {})
            if not isinstance(field_activation_upstream, dict):
                field_activation_upstream = {}
            current_model_chain_resume_ready = bool(
                route_ready and can_resume_model_chain and route_class == "model_chain_external_package"
            )
            current_handoff_ready = bool(route_ready and handoff_only)
            actions.append(
                {
                    "action_type": "submit_external_evidence_package",
                    "channel_id": channel_id,
                    "activation_route_class": route_class,
                    "model_chain_resume_candidate": route_class == "model_chain_external_package",
                    "handoff_only": handoff_only,
                    "can_resume_model_chain": can_resume_model_chain,
                    "requires_tested_interface": False,
                    "current_route_ready": route_ready,
                    "current_model_chain_resume_ready": current_model_chain_resume_ready,
                    "current_handoff_ready": current_handoff_ready,
                    "action_resume_state": self._external_activation_action_resume_state(
                        route_class=route_class,
                        route_ready=route_ready,
                        can_resume_model_chain=can_resume_model_chain,
                    ),
                    "package_pointer": action.get("package_pointer"),
                    "next_operator_action": action.get("next_operator_action"),
                    "router_status": self._external_activation_router_status(),
                    "router_route_status": router_row.get("route_status", "router_route_not_consumed"),
                    "router_blocked_reason": router_row.get("blocked_reason", ""),
                    "router_operator_action": router_row.get("operator_action", ""),
                    "router_preflight_status": (
                        self._external_activation_router_preflight_status(router_row)
                        if router_row
                        else "router_route_not_consumed"
                    ),
                    "router_catalyst_patch_candidate_status": str(
                        catalyst_candidate.get("patch_status", "")
                    ),
                    "router_catalyst_patch_candidate_can_submit_as_REAL_FIELD_REPLAY_PACKAGE_DIR": bool(
                        catalyst_candidate.get(
                            "can_submit_candidate_as_REAL_FIELD_REPLAY_PACKAGE_DIR",
                            False,
                        )
                    ),
                    "router_catalyst_patch_candidate_remaining_gap_count": self._safe_int(
                        catalyst_candidate.get("remaining_gap_count", 0)
                    ),
                    "router_catalyst_patch_candidate_package_dir": str(
                        catalyst_candidate.get("candidate_package_dir", "")
                    ),
                    "router_field_activation_upstream_status": str(
                        field_activation_upstream.get("status", "")
                    ),
                    "router_field_activation_upstream_first_blocked_step": str(
                        field_activation_upstream.get("first_blocked_step", "")
                    ),
                    "router_field_activation_upstream_highest_priority_blocker": str(
                        field_activation_upstream.get("highest_priority_blocker", "")
                    ),
                    "router_field_activation_upstream_next_operator_action": str(
                        field_activation_upstream.get("next_operator_action", "")
                    ),
                    "router_field_activation_upstream_can_submit_to_external_activation_router": bool(
                        field_activation_upstream.get(
                            "can_submit_to_external_activation_router",
                            False,
                        )
                    ),
                    **(
                        self._external_activation_operator_packet_core_gate_fields()
                        if channel_id == "R7_REAL_FIELD_PACKAGE"
                        else {}
                    ),
                    **(
                        self._formal_search_nonlegal_review_operator_packet_core_gate_fields()
                        if channel_id == "R8U79_FORMAL_SEARCH_RESULT_PACKAGE"
                        else {}
                    ),
                    "router_validation_command": ".venv/bin/python experiments/run_external_activation_router.py",
                    "boundary": self._external_activation_action_boundary(channel_id),
                }
            )

        field_activation_status = self._field_activation_matrix_status()
        field_activation_available = field_activation_status != "not_available"
        actions.append(
            {
                "action_type": "define_new_core_interface",
                "channel_id": "NEW_CORE_INTERFACE",
                "activation_route_class": "new_testable_core_interface",
                "model_chain_resume_candidate": False,
                "handoff_only": False,
                "can_resume_model_chain": False,
                "requires_tested_interface": True,
                "current_route_ready": False,
                "current_model_chain_resume_ready": False,
                "current_handoff_ready": False,
                "action_resume_state": (
                    "new_core_interface_defined_waiting_for_external_evidence"
                    if field_activation_available
                    else "new_interface_required_before_any_resume"
                ),
                "new_core_interface_id": self._field_activation_matrix_interface_id(),
                "new_core_interface_status": field_activation_status,
                "new_core_interface_hidden_state_row_count": (
                    self._field_activation_matrix_hidden_state_row_count()
                ),
                "new_core_interface_no_write_boundary_complete": (
                    self._field_activation_matrix_no_write_boundary_complete()
                ),
                "new_core_interface_response_source_preflight_status": (
                    self._field_activation_response_source_preflight_status()
                ),
                "new_core_interface_response_source_external_response_supplied": (
                    self._field_activation_response_source_external_response_supplied()
                ),
                "new_core_interface_response_source_can_run_response_preflight": (
                    self._field_activation_response_source_can_run_response_preflight()
                ),
                "new_core_interface_response_repair_work_order_status": (
                    self._field_activation_response_repair_work_order_status()
                ),
                "new_core_interface_response_repair_item_count": (
                    self._field_activation_response_repair_item_count()
                ),
                "new_core_interface_response_repair_highest_priority_repair_id": (
                    self._field_activation_response_repair_highest_priority_repair_id()
                ),
                "new_core_interface_response_preflight_status": (
                    self._field_activation_response_preflight_status()
                ),
                "new_core_interface_response_missing_value_payload_row_count": (
                    self._field_activation_response_missing_value_payload_row_count()
                ),
                "new_core_interface_response_template_value_payload_row_count": (
                    self._field_activation_response_template_value_payload_row_count()
                ),
                "new_core_interface_response_can_route": (
                    self._field_activation_response_can_route_to_external_activation_router()
                ),
                "new_core_interface_response_completion_ledger_status": (
                    self._field_activation_response_completion_ledger_status()
                ),
                "new_core_interface_response_completion_ratio": (
                    self._field_activation_response_completion_ratio()
                ),
                "new_core_interface_response_next_hidden_state_focus": (
                    self._field_activation_response_next_hidden_state_focus()
                ),
                "new_core_interface_response_completion_next_operator_action": (
                    self._field_activation_response_completion_next_operator_action()
                ),
                "new_core_interface_response_focus_handoff_status": (
                    self._field_activation_response_focus_handoff_status()
                ),
                "new_core_interface_response_focus_handoff_target_hidden_state": (
                    self._field_activation_response_focus_handoff_target_hidden_state()
                ),
                "new_core_interface_response_focus_handoff_row_scan_reduction_ratio": (
                    self._field_activation_response_focus_handoff_row_scan_reduction_ratio()
                ),
                "new_core_interface_response_focus_handoff_next_operator_action": (
                    self._field_activation_response_focus_handoff_next_operator_action()
                ),
                "new_core_interface_response_focus_handoff_repair_work_order_status": (
                    self._field_activation_response_focus_handoff_repair_work_order_status()
                ),
                "new_core_interface_response_focus_handoff_repair_item_count": (
                    self._field_activation_response_focus_handoff_repair_item_count()
                ),
                "new_core_interface_response_focus_handoff_repair_next_operator_action": (
                    self._field_activation_response_focus_handoff_repair_next_operator_action()
                ),
                "new_core_interface_external_activation_operator_action_packet_status": (
                    self._external_activation_operator_packet_status()
                ),
                "new_core_interface_external_activation_operator_action_packet_target_hidden_state": (
                    self._external_activation_operator_packet_target_hidden_state()
                ),
                "new_core_interface_external_activation_operator_action_packet_source_env_var": (
                    self._external_activation_operator_packet_source_env_var()
                ),
                "new_core_interface_external_activation_operator_action_packet_expected_focused_response_row_count": (
                    self._external_activation_operator_packet_expected_focused_response_row_count()
                ),
                "new_core_interface_external_activation_operator_action_packet_focused_candidate_availability_status": (
                    self._external_activation_operator_packet_focused_candidate_availability_status()
                ),
                "new_core_interface_external_activation_operator_action_packet_focused_candidate_operator_packet_submit_ready": (
                    self._external_activation_operator_packet_focused_candidate_operator_packet_submit_ready()
                ),
                "new_core_interface_external_activation_operator_action_packet_next_operator_action": (
                    self._external_activation_operator_packet_next_operator_action()
                ),
                "new_core_interface_external_activation_operator_action_packet_boundary_pass": (
                    self._external_activation_operator_packet_boundary_pass()
                ),
                "new_core_interface_external_activation_operator_action_packet_can_resume_model_chain": (
                    self._external_activation_operator_packet_can_resume_model_chain()
                ),
                "new_core_interface_external_activation_operator_action_packet_can_write_to_actuator": (
                    self._external_activation_operator_packet_can_write_to_actuator()
                ),
                "new_core_interface_external_activation_operator_action_packet_can_write_to_release_gate": (
                    self._external_activation_operator_packet_can_write_to_release_gate()
                ),
                "new_core_interface_response_coherence_audit_status": (
                    self._field_activation_response_coherence_audit_status()
                ),
                "new_core_interface_response_coherence_can_route": (
                    self._field_activation_response_coherence_can_route_to_package_assembly()
                ),
                "new_core_interface_package_assembly_status": (
                    self._field_activation_package_assembly_status()
                ),
                "new_core_interface_package_assembly_can_stage": (
                    self._field_activation_package_assembly_can_stage_external_package_candidates()
                ),
                "new_core_interface_package_staging_status": (
                    self._field_activation_package_staging_status()
                ),
                "new_core_interface_package_staging_selected_row_blueprint_count": (
                    self._field_activation_package_staging_selected_row_blueprint_count()
                ),
                "new_core_interface_package_staging_selected_value_payload_mapping_count": (
                    self._field_activation_package_staging_selected_value_payload_mapping_count()
                ),
                "new_core_interface_package_staging_can_materialize": (
                    self._field_activation_package_staging_can_materialize_no_write_package_candidates()
                ),
                "new_core_interface_package_staging_next_operator_action": (
                    self._field_activation_package_staging_next_operator_action()
                ),
                "new_core_interface_materialized_package_preflight_status": (
                    self._field_activation_materialized_package_preflight_status()
                ),
                "new_core_interface_materialized_package_blueprint_missing_row_count": (
                    self._field_activation_materialized_package_blueprint_missing_row_count()
                ),
                "new_core_interface_materialized_package_can_route": (
                    self._field_activation_materialized_package_preflight_can_route_to_external_activation_router()
                ),
                "new_core_interface_downstream_r7_preview_status": (
                    self._field_activation_downstream_r7_preview_status()
                ),
                "new_core_interface_downstream_r7_preview_executed": (
                    self._field_activation_downstream_r7_preview_executed()
                ),
                "new_core_interface_downstream_r7_preview_metric_evaluation_status": (
                    self._field_activation_downstream_r7_preview_metric_evaluation_status()
                ),
                "new_core_interface_downstream_r7_not_evaluated_metric_count": (
                    self._field_activation_downstream_r7_not_evaluated_metric_count()
                ),
                "new_core_interface_downstream_r7_can_pass_to_timestamped_replay": (
                    self._field_activation_downstream_r7_can_pass_to_timestamped_replay()
                ),
                "new_core_interface_downstream_r7_highest_priority_blocker": (
                    self._field_activation_downstream_r7_highest_priority_blocker()
                ),
                "new_core_interface_downstream_path_endpoint_preview_status": (
                    self._field_activation_downstream_path_endpoint_preview_status()
                ),
                "new_core_interface_downstream_path_endpoint_preview_executed": (
                    self._field_activation_downstream_path_endpoint_preview_executed()
                ),
                "new_core_interface_downstream_path_endpoint_preview_metric_evaluation_status": (
                    self._field_activation_downstream_path_endpoint_preview_metric_evaluation_status()
                ),
                "new_core_interface_downstream_path_endpoint_not_evaluated_metric_count": (
                    self._field_activation_downstream_path_endpoint_not_evaluated_metric_count()
                ),
                "new_core_interface_downstream_path_endpoint_can_route_to_field_layout_holdout": (
                    self._field_activation_downstream_path_endpoint_can_route_to_field_layout_holdout()
                ),
                "new_core_interface_downstream_path_endpoint_highest_priority_blocker": (
                    self._field_activation_downstream_path_endpoint_highest_priority_blocker()
                ),
                "new_core_interface_external_readiness_gate_status": (
                    self._field_activation_external_readiness_gate_status()
                ),
                "new_core_interface_external_readiness_next_operator_action": (
                    self._field_activation_external_readiness_next_operator_action()
                ),
                "new_core_interface_external_readiness_can_submit": (
                    self._field_activation_external_readiness_can_submit_to_external_activation_router()
                ),
                "new_core_interface_response_submission_packet_status": (
                    self._field_activation_response_submission_packet_status()
                ),
                "new_core_interface_response_submission_next_operator_action": (
                    self._field_activation_response_submission_packet_next_operator_action()
                ),
                "new_core_interface_response_submission_can_route": (
                    self._field_activation_response_submission_packet_can_route_to_external_activation_router()
                ),
                "new_core_interface_schema_preflight_status": (
                    self._field_activation_schema_preflight_status()
                ),
                "new_core_interface_schema_can_validate_response_structure": (
                    self._field_activation_schema_can_validate_response_structure()
                ),
                "new_core_interface_schema_can_resume_model_chain": (
                    self._field_activation_schema_can_resume_model_chain()
                ),
                "new_core_interface_schema_can_write_to_actuator": (
                    self._field_activation_schema_can_write_to_actuator()
                ),
                "new_core_interface_schema_can_write_to_release_gate": (
                    self._field_activation_schema_can_write_to_release_gate()
                ),
                "package_pointer": None,
                "next_operator_action": (
                    "Use field_activation_matrix to prepare state-level external evidence packages."
                    if field_activation_available
                    else (
                        "Provide a new testable interface, state variable, gate, field-data contract, "
                        "or engineering constraint that maps to the seven-layer system skeleton."
                    )
                ),
                "router_status": "not_applicable_for_new_core_interface",
                "router_route_status": "not_applicable_for_new_core_interface",
                "router_blocked_reason": "",
                "router_operator_action": (
                    "submit_external_packages_required_by_field_activation_matrix"
                    if field_activation_available
                    else "define_new_core_interface_with_tests"
                ),
                "router_preflight_status": (
                    "new_interface_defined_no_model_chain_resume_without_external_evidence"
                    if field_activation_available
                    else "new_interface_needs_tests_or_verification_gate"
                ),
                "router_validation_command": "not_applicable_for_new_core_interface",
                "boundary": (
                    "The new interface must preserve synthetic/template/literature/field boundaries "
                    "and must include tests or a verification gate."
                ),
            }
        )
        return actions

    @staticmethod
    def _external_activation_action_route_class(channel_id: str) -> str:
        if channel_id in {"R7_REAL_FIELD_PACKAGE", "R8U66_PATH_ENDPOINT_LABEL_PACKAGE"}:
            return "model_chain_external_package"
        if channel_id == "R8U79_FORMAL_SEARCH_RESULT_PACKAGE":
            return "formal_search_handoff_only"
        return "external_package_unknown_resume_class"

    @staticmethod
    def _external_activation_action_resume_state(
        *,
        route_class: str,
        route_ready: bool,
        can_resume_model_chain: bool,
    ) -> str:
        if route_class == "formal_search_handoff_only":
            return "handoff_ready_not_model_chain" if route_ready else "handoff_blocked_waiting_for_package"
        if route_class == "model_chain_external_package":
            if route_ready and can_resume_model_chain:
                return "model_chain_resume_ready_after_preflight"
            if route_ready and not can_resume_model_chain:
                return "router_ready_but_contract_still_blocks_model_chain"
            return "model_chain_blocked_waiting_for_package"
        if route_class == "external_package_unknown_resume_class":
            return "unknown_external_route_class_blocked"
        return "new_interface_required_before_any_resume"

    @staticmethod
    def _external_activation_action_boundary(channel_id: str) -> str:
        if channel_id == "R7_REAL_FIELD_PACKAGE":
            return (
                "This action may resume field import, timestamped replay and field evidence review only "
                "after Agent44/42/43/45 gates pass; it cannot write actuator policy, release gate, "
                "field-supported claims, patent/legal conclusions, or final deployment clearance by itself."
            )
        if channel_id == "R8U66_PATH_ENDPOINT_LABEL_PACKAGE":
            return (
                "This action may resume field layout holdout, path-stage validation and endpoint evidence "
                "review only after path/endpoint package preflight passes; it cannot write actuator policy, "
                "release gate, field-supported claims, patent/legal conclusions, or final release clearance by itself."
            )
        if channel_id == "R8U79_FORMAL_SEARCH_RESULT_PACKAGE":
            return (
                "This action is a formal-search handoff only: after Agent60 source/row preflight it may "
                "enter nonlegal comparison, formal counsel review handoff, or disclosure revision queues; "
                "it cannot resume field replay or control, write actuator policy, write release gate, emit "
                "patent/legal conclusions, or create field-supported claims."
            )
        return (
            "This external action has no known resume class; it cannot resume model-chain execution, write "
            "actuator policy, write release gate, emit patent/legal conclusions, or create field-supported "
            "claims until a tested channel-specific boundary is added."
        )

    def _external_resume_conditions_for_stage(
        self,
        *,
        stage_decision: str,
        external_activation_contract: dict[str, object] | None,
    ) -> dict[str, object]:
        if stage_decision != "stop_expansion_wait_for_real_field_package_or_new_core_interface":
            return {
                "resume_policy": "not_in_external_wait_state",
                "stage_decision": stage_decision,
            }

        contract = external_activation_contract or {}
        channels: list[dict[str, object]] = []
        for channel in contract.get("channels", []):
            if not isinstance(channel, dict):
                continue
            channels.append(
                {
                    "channel_id": channel.get("channel_id"),
                    "package_pointer": channel.get("package_pointer"),
                    "current_status": channel.get("current_status"),
                    "can_resume_model_chain": channel.get("can_resume_model_chain"),
                    "ready_for_external_submission": channel.get("ready_for_external_submission"),
                    "required_evidence": channel.get("required_evidence", []),
                    "reject_if": channel.get("reject_if", []),
                    "resumes_to": channel.get("resumes_to", []),
                }
            )
        return {
            "resume_policy": (
                "Resume internal model-chain execution only after at least one external channel passes "
                "its package/router/preflight gate, or after a genuinely new core interface is supplied."
            ),
            "contract_status": contract.get("contract_status", "missing_external_activation_contract"),
            "activation_ready": contract.get("activation_ready", False),
            "blocked_channel_count": contract.get("blocked_channel_count", len(channels)),
            "router_status": self._external_activation_router_status(),
            "router_consumed": self._external_activation_router_consumed(),
            "router_path_supplied_count": self._external_activation_router_path_supplied_count(),
            "router_route_ready_count": self._external_activation_router_route_ready_count(),
            "router_model_chain_ready_route_count": self._external_activation_router_model_chain_ready_route_count(),
            "router_handoff_ready_route_count": self._external_activation_router_handoff_ready_route_count(),
            "router_blocked_route_count": self._external_activation_router_blocked_route_count(),
            "router_catalyst_patch_candidate_consumed": (
                self._external_activation_router_catalyst_patch_candidate_consumed()
            ),
            "router_catalyst_patch_candidate_status": (
                self._external_activation_router_catalyst_patch_candidate_status()
            ),
            "router_catalyst_patch_candidate_can_submit_as_REAL_FIELD_REPLAY_PACKAGE_DIR": (
                self._external_activation_router_catalyst_patch_candidate_can_submit_as_r7_dir()
            ),
            "router_catalyst_patch_candidate_remaining_gap_count": (
                self._external_activation_router_catalyst_patch_candidate_remaining_gap_count()
            ),
            "router_catalyst_patch_candidate_package_dir": (
                self._external_activation_router_catalyst_patch_candidate_package_dir()
            ),
            "router_field_activation_upstream_consumed": (
                self._external_activation_router_field_activation_upstream_consumed()
            ),
            "router_field_activation_upstream_status": (
                self._external_activation_router_field_activation_upstream_status()
            ),
            "router_field_activation_upstream_first_blocked_step": (
                self._external_activation_router_field_activation_upstream_first_blocked_step()
            ),
            "router_field_activation_upstream_highest_priority_blocker": (
                self._external_activation_router_field_activation_upstream_highest_priority_blocker()
            ),
            "router_field_activation_upstream_next_operator_action": (
                self._external_activation_router_field_activation_upstream_next_operator_action()
            ),
            "router_field_activation_upstream_can_submit_to_external_activation_router": (
                self._external_activation_router_field_activation_upstream_can_submit_to_external_activation_router()
            ),
            "router_boundary_preserved": self._external_activation_router_boundary_preserved(),
            "router_ready_channel_ids": self._external_activation_router_ready_channel_ids(),
            "router_model_chain_ready_channel_ids": self._external_activation_router_model_chain_ready_channel_ids(),
            "router_handoff_ready_channel_ids": self._external_activation_router_handoff_ready_channel_ids(),
            "router_blocked_channel_ids": self._external_activation_router_blocked_channel_ids(),
            "router_highest_priority_blocker": self._external_activation_router_highest_priority_blocker(),
            "router_next_operator_action": self._external_activation_router_next_operator_action(),
            "router_validation_command": ".venv/bin/python experiments/run_external_activation_router.py",
            "router_route_summary": self._external_activation_router_route_summary(),
            "formal_search_nonlegal_review_operator_packet": (
                self._formal_search_nonlegal_review_operator_packet_core_gate_fields()
            ),
            "new_core_interface": {
                "interface_id": self._field_activation_matrix_interface_id(),
                "interface_status": self._field_activation_matrix_status(),
                "hidden_state_row_count": self._field_activation_matrix_hidden_state_row_count(),
                "can_resume_model_chain": self._field_activation_matrix_can_resume_model_chain(),
                "can_write_to_actuator": self._field_activation_matrix_can_write_to_actuator(),
                "can_write_to_release_gate": self._field_activation_matrix_can_write_to_release_gate(),
                "no_write_boundary_complete": self._field_activation_matrix_no_write_boundary_complete(),
                "response_source_preflight_status": self._field_activation_response_source_preflight_status(),
                "response_source_external_response_supplied": (
                    self._field_activation_response_source_external_response_supplied()
                ),
                "response_source_can_run_response_preflight": (
                    self._field_activation_response_source_can_run_response_preflight()
                ),
                "response_repair_work_order_status": self._field_activation_response_repair_work_order_status(),
                "response_repair_item_count": self._field_activation_response_repair_item_count(),
                "response_repair_highest_priority_repair_id": (
                    self._field_activation_response_repair_highest_priority_repair_id()
                ),
                "response_preflight_status": self._field_activation_response_preflight_status(),
                "response_expected_row_count": self._field_activation_response_expected_row_count(),
                "response_template_marker_row_count": (
                    self._field_activation_response_template_marker_row_count()
                ),
                "response_missing_value_payload_row_count": (
                    self._field_activation_response_missing_value_payload_row_count()
                ),
                "response_template_value_payload_row_count": (
                    self._field_activation_response_template_value_payload_row_count()
                ),
                "response_can_route_to_external_activation_router": (
                    self._field_activation_response_can_route_to_external_activation_router()
                ),
                "response_coherence_audit_status": self._field_activation_response_coherence_audit_status(),
                "response_coherence_hard_blocker_count": (
                    self._field_activation_response_coherence_hard_blocker_count()
                ),
                "response_coherence_warning_count": (
                    self._field_activation_response_coherence_warning_count()
                ),
                "response_coherence_highest_priority_blocker": (
                    self._field_activation_response_coherence_highest_priority_blocker()
                ),
                "response_coherence_can_route_to_package_assembly": (
                    self._field_activation_response_coherence_can_route_to_package_assembly()
                ),
                "package_assembly_status": self._field_activation_package_assembly_status(),
                "package_assembly_channel_plan_count": (
                    self._field_activation_package_assembly_channel_plan_count()
                ),
                "package_assembly_candidate_channel_plan_count": (
                    self._field_activation_package_assembly_candidate_channel_plan_count()
                ),
                "package_assembly_table_plan_count": (
                    self._field_activation_package_assembly_table_plan_count()
                ),
                "package_assembly_can_stage_external_package_candidates": (
                    self._field_activation_package_assembly_can_stage_external_package_candidates()
                ),
                "package_staging_status": self._field_activation_package_staging_status(),
                "package_staging_selected_channel_manifest_count": (
                    self._field_activation_package_staging_selected_channel_manifest_count()
                ),
                "package_staging_selected_row_blueprint_count": (
                    self._field_activation_package_staging_selected_row_blueprint_count()
                ),
                "package_staging_selected_value_payload_mapping_count": (
                    self._field_activation_package_staging_selected_value_payload_mapping_count()
                ),
                "package_staging_candidate_channel_requirement_count": (
                    self._field_activation_package_staging_candidate_channel_requirement_count()
                ),
                "package_staging_can_materialize_no_write_package_candidates": (
                    self._field_activation_package_staging_can_materialize_no_write_package_candidates()
                ),
                "package_staging_next_operator_action": self._field_activation_package_staging_next_operator_action(),
                "materialized_package_preflight_status": (
                    self._field_activation_materialized_package_preflight_status()
                ),
                "materialized_package_blocker_count": (
                    self._field_activation_materialized_package_preflight_blocker_count()
                ),
                "materialized_package_blueprint_missing_row_count": (
                    self._field_activation_materialized_package_blueprint_missing_row_count()
                ),
                "materialized_package_highest_priority_blocker": (
                    self._field_activation_materialized_package_preflight_highest_priority_blocker()
                ),
                "materialized_package_can_route_to_external_activation_router": (
                    self._field_activation_materialized_package_preflight_can_route_to_external_activation_router()
                ),
                "materialized_package_next_operator_action": (
                    self._field_activation_materialized_package_preflight_next_operator_action()
                ),
                "downstream_r7_preview_status": self._field_activation_downstream_r7_preview_status(),
                "downstream_r7_preview_executed": self._field_activation_downstream_r7_preview_executed(),
                "downstream_r7_preview_metric_evaluation_status": (
                    self._field_activation_downstream_r7_preview_metric_evaluation_status()
                ),
                "downstream_r7_not_evaluated_metric_count": (
                    self._field_activation_downstream_r7_not_evaluated_metric_count()
                ),
                "downstream_r7_agent44_import_status": (
                    self._field_activation_downstream_r7_agent44_import_status()
                ),
                "downstream_r7_can_pass_to_timestamped_replay": (
                    self._field_activation_downstream_r7_can_pass_to_timestamped_replay()
                ),
                "downstream_r7_highest_priority_blocker": (
                    self._field_activation_downstream_r7_highest_priority_blocker()
                ),
                "downstream_r7_next_operator_action": self._field_activation_downstream_r7_next_operator_action(),
                "downstream_path_endpoint_preview_status": (
                    self._field_activation_downstream_path_endpoint_preview_status()
                ),
                "downstream_path_endpoint_preview_executed": (
                    self._field_activation_downstream_path_endpoint_preview_executed()
                ),
                "downstream_path_endpoint_preview_metric_evaluation_status": (
                    self._field_activation_downstream_path_endpoint_preview_metric_evaluation_status()
                ),
                "downstream_path_endpoint_not_evaluated_metric_count": (
                    self._field_activation_downstream_path_endpoint_not_evaluated_metric_count()
                ),
                "downstream_path_endpoint_preflight_status": (
                    self._field_activation_downstream_path_endpoint_preflight_status()
                ),
                "downstream_path_endpoint_required_table_count": (
                    self._field_activation_downstream_path_endpoint_required_table_count()
                ),
                "downstream_path_endpoint_contract_minimum_matched_batch_count": (
                    self._field_activation_downstream_path_endpoint_contract_minimum_matched_batch_count()
                ),
                "downstream_path_endpoint_matched_batch_count": (
                    self._field_activation_downstream_path_endpoint_matched_batch_count()
                ),
                "downstream_path_endpoint_required_matched_batch_deficit": (
                    self._field_activation_downstream_path_endpoint_required_matched_batch_deficit()
                ),
                "downstream_path_endpoint_can_route_to_field_layout_holdout": (
                    self._field_activation_downstream_path_endpoint_can_route_to_field_layout_holdout()
                ),
                "downstream_path_endpoint_highest_priority_blocker": (
                    self._field_activation_downstream_path_endpoint_highest_priority_blocker()
                ),
                "downstream_path_endpoint_next_operator_action": (
                    self._field_activation_downstream_path_endpoint_next_operator_action()
                ),
                "external_readiness_gate_status": self._field_activation_external_readiness_gate_status(),
                "external_readiness_first_blocked_step": (
                    self._field_activation_external_readiness_first_blocked_step()
                ),
                "external_readiness_highest_priority_blocker": (
                    self._field_activation_external_readiness_highest_priority_blocker()
                ),
                "external_readiness_next_operator_action": (
                    self._field_activation_external_readiness_next_operator_action()
                ),
                "external_readiness_can_submit_to_external_activation_router": (
                    self._field_activation_external_readiness_can_submit_to_external_activation_router()
                ),
                "response_submission_packet_status": (
                    self._field_activation_response_submission_packet_status()
                ),
                "response_submission_highest_priority_blocker": (
                    self._field_activation_response_submission_packet_highest_priority_blocker()
                ),
                "response_submission_next_operator_action": (
                    self._field_activation_response_submission_packet_next_operator_action()
                ),
                "response_submission_can_route_to_external_activation_router": (
                    self._field_activation_response_submission_packet_can_route_to_external_activation_router()
                ),
                "response_completion_ledger_status": (
                    self._field_activation_response_completion_ledger_status()
                ),
                "response_completion_ratio": self._field_activation_response_completion_ratio(),
                "response_next_hidden_state_focus": (
                    self._field_activation_response_next_hidden_state_focus()
                ),
                "response_completion_next_operator_action": (
                    self._field_activation_response_completion_next_operator_action()
                ),
                "response_focus_handoff_status": (
                    self._field_activation_response_focus_handoff_status()
                ),
                "response_focus_handoff_target_hidden_state": (
                    self._field_activation_response_focus_handoff_target_hidden_state()
                ),
                "response_focus_handoff_row_scan_reduction_ratio": (
                    self._field_activation_response_focus_handoff_row_scan_reduction_ratio()
                ),
                "response_focus_handoff_next_operator_action": (
                    self._field_activation_response_focus_handoff_next_operator_action()
                ),
                "response_focus_handoff_repair_work_order_status": (
                    self._field_activation_response_focus_handoff_repair_work_order_status()
                ),
                "response_focus_handoff_repair_item_count": (
                    self._field_activation_response_focus_handoff_repair_item_count()
                ),
                "response_focus_handoff_repair_next_operator_action": (
                    self._field_activation_response_focus_handoff_repair_next_operator_action()
                ),
                "external_activation_operator_action_packet_status": (
                    self._external_activation_operator_packet_status()
                ),
                "external_activation_operator_action_packet_target_hidden_state": (
                    self._external_activation_operator_packet_target_hidden_state()
                ),
                "external_activation_operator_action_packet_source_env_var": (
                    self._external_activation_operator_packet_source_env_var()
                ),
                "external_activation_operator_action_packet_expected_focused_response_row_count": (
                    self._external_activation_operator_packet_expected_focused_response_row_count()
                ),
                "external_activation_operator_action_packet_focused_candidate_availability_status": (
                    self._external_activation_operator_packet_focused_candidate_availability_status()
                ),
                "external_activation_operator_action_packet_focused_candidate_operator_packet_submit_ready": (
                    self._external_activation_operator_packet_focused_candidate_operator_packet_submit_ready()
                ),
                "external_activation_operator_action_packet_next_operator_action": (
                    self._external_activation_operator_packet_next_operator_action()
                ),
                "external_activation_operator_action_packet_boundary_pass": (
                    self._external_activation_operator_packet_boundary_pass()
                ),
                "external_activation_operator_action_packet_can_resume_model_chain": (
                    self._external_activation_operator_packet_can_resume_model_chain()
                ),
                "external_activation_operator_action_packet_can_write_to_actuator": (
                    self._external_activation_operator_packet_can_write_to_actuator()
                ),
                "external_activation_operator_action_packet_can_write_to_release_gate": (
                    self._external_activation_operator_packet_can_write_to_release_gate()
                ),
                "schema_preflight_status": self._field_activation_schema_preflight_status(),
                "schema_can_validate_response_structure": (
                    self._field_activation_schema_can_validate_response_structure()
                ),
                "schema_can_resume_model_chain": self._field_activation_schema_can_resume_model_chain(),
                "schema_can_write_to_actuator": self._field_activation_schema_can_write_to_actuator(),
                "schema_can_write_to_release_gate": self._field_activation_schema_can_write_to_release_gate(),
                "next_gate": self._field_activation_matrix_next_gate(),
            },
            "channels": channels,
            "global_no_write_boundary": contract.get("global_no_write_boundary", ""),
        }

    def _core_ability_scores(
        self,
        evidence_matrix_status: dict[str, object],
        *,
        hidden_state_coverage_ledger: dict[str, object],
    ) -> dict[str, float]:
        field_ready_count = sum(
            1
            for ready in (
                self._catalyst_proxy_field_validated(),
                self._replay_evaluation_field_validated(),
                self._grey_box_physics_field_validated(),
                self._soft_sensor_matrix_field_validated(),
                self._engineering_constraints_field_validated(),
                self._kg_reasoning_field_validated(),
                self._field_validation_alignment_field_ready(),
                self._claim_specific_package_field_and_source_ready(),
            )
            if ready
        )
        field_readiness_bonus = min(0.18, 0.03 * field_ready_count)
        observability = self._bounded(
            0.35 * float(hidden_state_coverage_ledger["state_variable_contract_coverage"])
            + 0.25 * max(self._catalyst_activity_observability(), self._catalyst_proxy_after_patch())
            + 0.20 * float(hidden_state_coverage_ledger["design_or_patch_ready_coverage"])
            + 0.20 * min(1.0, self._field_need_to_table_coverage())
        )
        controllability = self._bounded(
            0.28 * self._replay_joint_action_accuracy()
            + 0.24 * self._engineering_mean_execution_feasibility()
            + 0.22 * min(1.0, self._field_need_to_gate_coverage())
            + 0.16 * min(1.0, self._main_chain_prior_consumption_rate())
            + 0.10 * (1.0 if self._agent49_readiness().get("can_write_to_actuator") is False else 0.3)
        )
        explainability = self._bounded(
            0.36 * self._kg_evidence_traceability()
            + 0.30 * self._kg_constraint_hit_rate()
            + 0.24 * min(1.0, self._main_chain_prior_consumption_rate())
            + 0.10 * evidence_matrix_status["completeness_score"]
        )
        verifiability = self._bounded(
            0.26 * evidence_matrix_status["completeness_score"]
            + 0.20 * min(1.0, self._field_need_to_table_coverage())
            + 0.20 * min(1.0, self._field_need_to_gate_coverage())
            + 0.16 * min(1.0, self._claim_specific_required_field_coverage())
            + 0.12 * min(1.0, self._source_basis_completion_rate())
            + field_readiness_bonus
        )
        engineering = self._bounded(
            0.34 * self._engineering_mean_execution_feasibility()
            + 0.22 * min(1.0, self._field_need_to_table_coverage())
            + 0.18 * min(1.0, self._claim_specific_required_field_coverage())
            + 0.16 * (1.0 if self._engineering_constraints_baseline_ready() else 0.0)
            + 0.10 * (1.0 if self._agent49_readiness().get("can_write_to_actuator") is False else 0.2)
        )
        evolvability = self._bounded(
            0.34 * min(1.0, self._main_chain_prior_consumption_rate())
            + 0.20 * (1.0 if self._main_chain_reconnection_baseline_ready() else 0.0)
            + 0.20 * (1.0 if self._claim_specific_package_baseline_ready() else 0.0)
            + 0.16 * (1.0 if self._soft_sensor_matrix_baseline_ready() else 0.0)
            + 0.10 * evidence_matrix_status["completeness_score"]
        )
        protectability = self._bounded(
            0.24 * min(1.0, self._claim_specific_required_field_coverage())
            + 0.22 * min(1.0, self._source_basis_completion_rate())
            + 0.18 * self._kg_evidence_traceability()
            + 0.12 * evidence_matrix_status["completeness_score"]
            + 0.12 * min(1.0, self._field_need_to_gate_coverage())
            + 0.08 * (1.0 if self._claim_specific_package_baseline_ready() else 0.0)
            + 0.04 * (1.0 if self._formal_search_execution_route_plan_ready() else 0.0)
            + 0.03 * (1.0 if self._formal_search_ai_nonlegal_review_brief_ready() else 0.0)
            + 0.02
            * (1.0 if self._formal_search_nonlegal_review_operator_packet_ready() else 0.0)
        )
        return {
            "observability": round(observability, 3),
            "controllability": round(controllability, 3),
            "explainability": round(explainability, 3),
            "verifiability": round(verifiability, 3),
            "engineering_feasibility": round(engineering, 3),
            "evolvability": round(evolvability, 3),
            "protectability": round(protectability, 3),
        }

    def _module_stage_termination_gate(
        self,
        evidence_matrix_status: dict[str, object],
        *,
        hidden_state_coverage_ledger: dict[str, object],
    ) -> dict[str, object]:
        metrics = {
            "input_contract_completeness": self._input_contract_completeness(),
            "output_contract_completeness": self._output_contract_completeness(),
            "state_variable_coverage": float(hidden_state_coverage_ledger["state_variable_contract_coverage"]),
            "downstream_reconnection_rate": self._downstream_reconnection_rate(),
            "evidence_boundary_completeness": min(1.0, float(evidence_matrix_status["completeness_score"])),
            "failure_boundary_completeness": self._failure_boundary_completeness(evidence_matrix_status),
            "no_write_boundary_clarity": self._no_write_boundary_clarity(),
        }
        blockers = [
            {
                "metric": name,
                "value": round(metrics[name], 3),
                "threshold": threshold,
            }
            for name, threshold in MODULE_TERMINATION_THRESHOLDS.items()
            if metrics[name] < threshold
        ]
        proof_rows = self._module_stage_termination_proof_rows(metrics)
        termination_pass_rate = round(
            sum(1 for row in proof_rows if row["passed"]) / len(proof_rows),
            3,
        )
        return {
            "module_stage_status": "module_stage_complete" if not blockers else "module_stage_needs_more_core_work",
            "thresholds": MODULE_TERMINATION_THRESHOLDS,
            "metrics": {name: round(value, 3) for name, value in metrics.items()},
            "termination_proof_status": (
                "module_stage_termination_proof_complete"
                if termination_pass_rate == 1.0
                else "module_stage_termination_proof_has_blockers"
            ),
            "termination_pass_rate": termination_pass_rate,
            "termination_proof_rows": proof_rows,
            "supporting_state_metrics": {
                "sparse_estimation_ready_coverage": hidden_state_coverage_ledger["sparse_estimation_ready_coverage"],
                "design_or_patch_ready_coverage": hidden_state_coverage_ledger["design_or_patch_ready_coverage"],
                "field_validated_state_coverage": hidden_state_coverage_ledger["field_validated_state_coverage"],
                "control_ready_state_coverage": hidden_state_coverage_ledger["control_ready_state_coverage"],
            },
            "blockers": blockers,
            "can_stop_current_module_expansion": not blockers,
            "termination_meaning": (
                "state_variable_coverage 表示关键隐藏状态已经进入可追踪合同；"
                "field_validated_state_coverage 和 control_ready_state_coverage 仍单独约束现场结论、执行器和 release gate。"
            ),
        }

    @staticmethod
    def _module_stage_termination_proof_rows(metrics: dict[str, float]) -> list[dict[str, object]]:
        rows: list[dict[str, object]] = []
        for metric, threshold in MODULE_TERMINATION_THRESHOLDS.items():
            value = round(metrics[metric], 3)
            metadata = MODULE_TERMINATION_PROOF_METADATA[metric]
            rows.append(
                {
                    "metric": metric,
                    "value": value,
                    "threshold": threshold,
                    "passed": value >= threshold,
                    "system_layer": metadata["system_layer"],
                    "core_capability": metadata["core_capability"],
                    "evidence_source": metadata["evidence_source"],
                    "failure_boundary": metadata["failure_boundary"],
                    "can_write_to_actuator": False,
                    "can_write_to_release_gate": False,
                    "field_claim_boundary": (
                        "This proof row can close architecture termination only; it cannot upgrade a "
                        "synthetic/template/literature claim into field evidence."
                    ),
                }
            )
        return rows

    def _next_gate_action(self, *, validity_status: str, stage_decision: str, field_blocker_present: bool) -> str:
        if validity_status == "invalid_iteration_evidence_boundary_violation":
            return "stop_and_restore_evidence_boundary_before_any_model_claim"
        if stage_decision == "stop_expansion_enter_review_or_backlog":
            return "freeze_current_micro_loop_and_move_new_ideas_to_stage_boundary_backlog"
        if stage_decision == "module_stage_complete_switch_or_wait_for_field_validation":
            return "switch_to_next_high_value_core_problem_or_wait_for_field_package"
        if field_blocker_present:
            return "continue_only_on_interfaces_or_packages_that_do_not_fabricate_field_evidence"
        return "continue_next_highest_value_core_action_with_targeted_tests"

    def _hidden_state_coverage_ledger(self) -> dict[str, object]:
        source_ledger = self.agent48_metrics.get("hidden_state_requirement_ledger", {})
        source_rows = source_ledger.get("state_rows", []) if isinstance(source_ledger, dict) else []
        rows_by_state = {
            str(row.get("hidden_state", "")): row
            for row in source_rows
            if isinstance(row, dict) and row.get("hidden_state")
        }
        state_rows: list[dict[str, object]] = []
        for state in EXPECTED_HIDDEN_STATES:
            source_row = rows_by_state.get(state, {})
            contract_covered = bool(source_row)
            sparse_ready = bool(source_row.get("ready_for_soft_sensor_estimation", False))
            proxy_design_ready = state == "catalyst_activity" and self._catalyst_proxy_baseline_ready()
            candidate_patch_ready = self._hidden_state_candidate_patch_ready(state, source_row)
            design_or_patch_ready = sparse_ready or proxy_design_ready or candidate_patch_ready
            field_validated = self._hidden_state_field_validated(state)
            control_ready = bool(source_row.get("ready_for_control_use", False)) and field_validated
            coverage_stage = self._hidden_state_coverage_stage(
                contract_covered=contract_covered,
                sparse_ready=sparse_ready,
                proxy_design_ready=proxy_design_ready,
                candidate_patch_ready=candidate_patch_ready,
                field_validated=field_validated,
                control_ready=control_ready,
            )
            state_rows.append(
                {
                    "hidden_state": state,
                    "contract_covered": contract_covered,
                    "sparse_estimation_ready": sparse_ready,
                    "proxy_design_ready": proxy_design_ready,
                    "candidate_patch_ready": candidate_patch_ready,
                    "design_or_patch_ready": design_or_patch_ready,
                    "field_validated": field_validated,
                    "control_ready": control_ready,
                    "coverage_stage": coverage_stage,
                    "min_primary_axis_score": round(float(source_row.get("min_primary_axis_score", 0.0)), 3)
                    if source_row
                    else 0.0,
                    "missing_required_zones": source_row.get("missing_required_zones", []) if source_row else [],
                    "missing_required_modalities": source_row.get("missing_required_modalities", []) if source_row else [],
                    "field_evidence_needed": source_row.get("field_evidence_needed", []) if source_row else [],
                    "candidate_patch_status": (
                        source_row.get("candidate_patch", {}).get("patch_status", "not_available")
                        if isinstance(source_row.get("candidate_patch", {}), dict)
                        else "not_available"
                    ),
                    "evidence_boundary": self._hidden_state_evidence_boundary(state, field_validated),
                }
            )
        total = len(EXPECTED_HIDDEN_STATES)
        contract_count = sum(1 for row in state_rows if row["contract_covered"])
        sparse_ready_count = sum(1 for row in state_rows if row["sparse_estimation_ready"])
        design_ready_count = sum(1 for row in state_rows if row["design_or_patch_ready"])
        field_validated_count = sum(1 for row in state_rows if row["field_validated"])
        control_ready_count = sum(1 for row in state_rows if row["control_ready"])
        return {
            "ledger_id": "R8u68_agent50_hidden_state_coverage_ledger",
            "source_agent": "Agent48_hidden_state_requirement_ledger_plus_Agent51_proxy_design",
            "source_ledger_status": str(source_ledger.get("ledger_status", "not_available"))
            if isinstance(source_ledger, dict)
            else "not_available",
            "expected_hidden_states": list(EXPECTED_HIDDEN_STATES),
            "hidden_state_count": total,
            "contract_covered_state_count": contract_count,
            "sparse_estimation_ready_state_count": sparse_ready_count,
            "design_or_patch_ready_state_count": design_ready_count,
            "field_validated_state_count": field_validated_count,
            "control_ready_state_count": control_ready_count,
            "state_variable_contract_coverage": round(contract_count / total, 3),
            "sparse_estimation_ready_coverage": round(sparse_ready_count / total, 3),
            "design_or_patch_ready_coverage": round(design_ready_count / total, 3),
            "field_validated_state_coverage": round(field_validated_count / total, 3),
            "control_ready_state_coverage": round(control_ready_count / total, 3),
            "state_rows": state_rows,
            "field_validation_blockers": [
                row["hidden_state"] for row in state_rows if not row["field_validated"]
            ],
            "control_readiness_blockers": [
                row["hidden_state"] for row in state_rows if not row["control_ready"]
            ],
            "termination_boundary": (
                "state_variable_contract_coverage may close the architecture contract gate, "
                "but field_validated_state_coverage and control_ready_state_coverage remain separate no-write gates."
            ),
        }

    @staticmethod
    def _hidden_state_candidate_patch_ready(state: str, source_row: dict[str, object]) -> bool:
        patch = source_row.get("candidate_patch", {}) if isinstance(source_row, dict) else {}
        if not isinstance(patch, dict):
            return False
        status = str(patch.get("patch_status", ""))
        if status in {"state_target_already_met", "candidate_pool_patch_available"}:
            return True
        if state == "catalyst_activity" and status == "candidate_pool_patch_incomplete":
            return True
        return False

    def _hidden_state_field_validated(self, state: str) -> bool:
        if state == "catalyst_activity":
            return self._catalyst_proxy_field_validated()
        if state in {"pollutant_residual", "reaction_completion", "release_or_byproduct_risk"}:
            return self._soft_sensor_matrix_field_validated() and self._field_validation_alignment_field_ready()
        if state == "hydraulic_delay":
            return self._replay_evaluation_field_validated() and self._soft_sensor_matrix_field_validated()
        if state == "matrix_interference":
            return self._soft_sensor_matrix_field_validated() and self._claim_specific_package_field_and_source_ready()
        return False

    @staticmethod
    def _hidden_state_coverage_stage(
        *,
        contract_covered: bool,
        sparse_ready: bool,
        proxy_design_ready: bool,
        candidate_patch_ready: bool,
        field_validated: bool,
        control_ready: bool,
    ) -> str:
        if control_ready:
            return "field_validated_control_ready"
        if field_validated:
            return "field_validated_estimation_ready"
        if sparse_ready:
            return "synthetic_sparse_estimation_ready"
        if proxy_design_ready:
            return "synthetic_proxy_design_ready_needs_field_labels"
        if candidate_patch_ready:
            return "candidate_patch_ready_needs_implementation_or_field_labels"
        if contract_covered:
            return "contract_only_needs_observation_patch"
        return "missing_state_contract"

    @staticmethod
    def _hidden_state_evidence_boundary(state: str, field_validated: bool) -> str:
        if field_validated:
            return f"{state} has field-validation support, but release/actuator write still requires downstream replay and operator gates."
        return (
            f"{state} is not field validated; synthetic sparse/proxy/candidate-patch coverage can guide design, "
            "but cannot support field claim, actuator write or release gate."
        )

    def _previous_core_score(self) -> float | None:
        candidates = (
            self.current_work_item.get("previous_core_score"),
            self.manifest.get("latest_agent50_core_score"),
            self.manifest.get("latest_core_score"),
        )
        for candidate in candidates:
            if candidate is None:
                continue
            try:
                return round(float(candidate), 3)
            except (TypeError, ValueError):
                continue
        return None

    def _previous_module_stage_status(self) -> str:
        if self.current_work_item.get("previous_module_stage_status"):
            return str(self.current_work_item["previous_module_stage_status"])
        return str(self.manifest.get("latest_agent50_module_stage_status", "not_recorded"))

    def _changed_contract_or_gate(self) -> bool:
        if bool(self.current_work_item.get("changed_contract_or_gate", False)):
            return True
        changed_keys = (
            "new_or_changed_interface",
            "new_or_changed_metric",
            "new_or_changed_gate",
            "new_or_changed_evidence_boundary",
            "new_or_changed_state_variable",
        )
        return any(bool(self.current_work_item.get(key, False)) for key in changed_keys)

    def _targeted_tests_passed(self) -> bool:
        if "targeted_tests_passed" in self.current_work_item:
            return bool(self.current_work_item.get("targeted_tests_passed", False))
        return True

    def _input_contract_completeness(self) -> float:
        values = [
            1.0 if self._agent48_comparable_baseline_ready() else 0.75,
            1.0 if self._soft_sensor_matrix_baseline_ready() else 0.65,
            min(1.0, self._field_need_to_table_coverage()),
            min(1.0, self._claim_specific_required_field_coverage()),
        ]
        return sum(values) / len(values)

    def _output_contract_completeness(self) -> float:
        values = [
            1.0 if self._replay_evaluation_baseline_ready() else 0.70,
            1.0 if self._grey_box_physics_baseline_ready() else 0.70,
            1.0 if self._engineering_constraints_baseline_ready() else 0.70,
            min(1.0, self._field_need_to_gate_coverage()),
        ]
        return sum(values) / len(values)

    def _state_variable_coverage(self) -> float:
        values = [
            self._weak_state_coverage(),
            max(self._catalyst_activity_observability(), self._catalyst_proxy_after_patch()),
            self._missingness_robustness_score(),
            min(1.0, self._main_chain_prior_consumption_rate()),
        ]
        return sum(values) / len(values)

    def _downstream_reconnection_rate(self) -> float:
        values = [
            min(1.0, self._main_chain_prior_consumption_rate()),
            min(1.0, self._field_need_to_gate_coverage()),
            1.0 if self._claim_specific_package_baseline_ready() else 0.0,
            1.0 if self._engineering_constraints_baseline_ready() else 0.0,
        ]
        return sum(values) / len(values)

    def _failure_boundary_completeness(self, evidence_matrix_status: dict[str, object]) -> float:
        boundary_score = float(evidence_matrix_status["completeness_score"])
        synthetic_boundaries = [
            self._catalyst_proxy_baseline_ready() and not self._catalyst_proxy_field_validated(),
            self._replay_evaluation_baseline_ready() and not self._replay_evaluation_field_validated(),
            self._grey_box_physics_baseline_ready() and not self._grey_box_physics_field_validated(),
            self._soft_sensor_matrix_baseline_ready() and not self._soft_sensor_matrix_field_validated(),
            self._engineering_constraints_baseline_ready() and not self._engineering_constraints_field_validated(),
            self._kg_reasoning_baseline_ready() and not self._kg_reasoning_field_validated(),
        ]
        return self._bounded(0.65 * boundary_score + 0.35 * min(1.0, sum(bool(item) for item in synthetic_boundaries) / 6))

    def _no_write_boundary_clarity(self) -> float:
        readiness = self._agent49_readiness()
        engineering = self._engineering_constraints_readiness()
        no_actuator = readiness.get("can_write_to_actuator") is False and engineering.get("can_write_to_actuator") is False
        no_release = readiness.get("can_write_to_release_gate") is False
        return 1.0 if no_actuator and no_release else 0.5

    @staticmethod
    def _bounded(value: float) -> float:
        return max(0.0, min(1.0, float(value)))

    def _evidence_matrix_status(self) -> dict[str, object]:
        records = self.external_evidence_matrix
        missing_by_record: list[dict[str, object]] = []
        for index, record in enumerate(records, start=1):
            missing = [field for field in REQUIRED_EVIDENCE_FIELDS if not record.get(field)]
            if missing:
                missing_by_record.append({"record_index": index, "source": record.get("source", "unknown"), "missing": missing})
        complete_count = len(records) - len(missing_by_record)
        return {
            "required_fields": list(REQUIRED_EVIDENCE_FIELDS),
            "record_count": len(records),
            "complete_record_count": complete_count,
            "incomplete_records": missing_by_record,
            "completeness_score": round(complete_count / max(1, len(records)), 3),
            "status": "evidence_matrix_complete" if records and not missing_by_record else "evidence_matrix_needs_patch",
        }

    def _blocked_reasons(self, evidence_matrix_status: dict[str, object]) -> list[str]:
        blocked: list[str] = []
        if self._catalyst_is_weak() and not self._catalyst_proxy_baseline_ready():
            blocked.append(
                "catalyst_activity weak observability blocks autonomous control: "
                f"weak_state_coverage={self._weak_state_coverage():.3f}, "
                f"catalyst_activity_observability={self._catalyst_activity_observability():.3f}"
            )
        if self._catalyst_proxy_baseline_ready() and not self._catalyst_proxy_field_validated():
            blocked.append(
                "Agent51 catalyst_activity proxy is only a synthetic design baseline; "
                "field_proxy_holdout labels are still required before relaxing Agent49 catalyst uncertainty blocks."
            )
        if self._replay_evaluation_baseline_ready() and not self._replay_evaluation_field_validated():
            blocked.append(
                "Agent52 multi-facility replay evaluation is only a synthetic baseline; "
                "field multi-node state-action-reward replay is still required before promoting Agent49."
            )
        if self._grey_box_physics_baseline_ready() and not self._grey_box_physics_field_validated():
            blocked.append(
                "Agent53 minimal grey-box physics is only a synthetic prior; "
                "field RTD, inlet/outlet pollutant, oxidant residual, catalyst history and byproduct labels are still required."
            )
        if self._soft_sensor_matrix_baseline_ready() and not self._soft_sensor_matrix_field_validated():
            blocked.append(
                "Agent54 soft sensor matrix coupling is only a synthetic layout contract; "
                "field node-specific values, layout holdout splits and missingness replay are still required."
            )
        if self._engineering_constraints_baseline_ready() and not self._engineering_constraints_field_validated():
            blocked.append(
                "Agent55 engineering execution constraints are only a synthetic reward/arbitration patch; "
                "PLC/SCADA point list, SOP and field execution replay are required before actuator writeback."
            )
        if self._kg_reasoning_baseline_ready() and not self._kg_reasoning_field_validated():
            blocked.append(
                "Agent56 knowledge graph reasoning is only a literature/synthetic reasoning patch; "
                "field-supported KG edges and source-basis completion are required before field mechanism claims."
            )
        if self._main_chain_reconnection_baseline_ready():
            blocked.append(
                "Agent57 main-chain reconnection is only a synthetic consumption audit; "
                "field replay and validation queue alignment are still required before field claims or actuator writeback."
            )
        if self._field_validation_alignment_baseline_ready() and not self._field_validation_alignment_field_ready():
            blocked.append(
                "Agent58 field validation queue alignment maps needs to tables/gates, but real field packages, "
                "claim-specific required fields and source_basis completion are still required before upgrading claims."
            )
        if self._claim_specific_package_baseline_ready() and not self._claim_specific_package_field_and_source_ready():
            if self._external_field_blocker_active():
                blocked.append(
                    "Agent59/unified evidence gate show source_basis detail and schema are ready; "
                    "P11 is now an external real-field-package blocker, so internal work should move to the next "
                    "non-field-fabricating model task until data_origin=field package is imported."
                )
            elif self._source_basis_detail_ready():
                blocked.append(
                    "Agent59 claim-specific field package matrix and source_basis detail are ready; "
                    "real Agent44->42->43->45 field evidence chain is still required before field claim upgrade."
                )
            else:
                blocked.append(
                    "Agent59 claim-specific field package matrix is ready, but citation-level source_basis detail and/or "
                    "real Agent44->42->43->45 field evidence chain are still required before field claim upgrade."
                )
        if self._soft_sensor_matrix_baseline_ready() and not self._field_path_endpoint_label_package_ready():
            blocked.append(
                "R8u66 field path/endpoint label package is not ready; field layout holdout, hydraulic path-stage "
                "validation and final-effluent release evidence still require node-specific path labels, endpoint "
                "labels, operation logs and offline lab rows."
            )
        if self._formal_search_execution_route_plan_ready():
            if "R8U79_FORMAL_SEARCH_RESULT_PACKAGE" in self._external_activation_router_handoff_ready_channel_ids():
                if self._formal_search_ai_nonlegal_review_brief_ready():
                    if self._formal_search_nonlegal_review_operator_packet_ready():
                        blocked.append(
                            "R8u136 formal search nonlegal review operator packet is ready and consolidates "
                            "the AI brief, response contract, source preflight and review readiness into a "
                            "single human-submission interface; "
                            f"{self._formal_search_nonlegal_review_operator_packet_source_env_var()} is still "
                            f"required with {self._formal_search_nonlegal_review_operator_packet_expected_review_packet_row_count()} "
                            "human nonlegal review rows before claim-scope patch drafting, and field replay/control "
                            "or claim text remain blocked."
                        )
                    else:
                        blocked.append(
                            "R8u134 formal search AI nonlegal review brief is ready and maps the preliminary "
                            "public-source hits to technical claim scaffolds for human triage; it is still only "
                            "an AI-assisted pre-review, so FORMAL_SEARCH_NONLEGAL_REVIEW_RESPONSE_PATH is required "
                            "before claim-scope patch drafting, and field replay/control or claim text remain blocked."
                        )
                else:
                    blocked.append(
                        "R8u79 formal search execution route plan is ready and FORMAL_SEARCH_RESULT_PACKAGE_PATH "
                        "has passed source/row preflight as a handoff-only route; it may enter human nonlegal "
                        "technical comparison, but it still cannot resume field replay/control or emit claim text."
                    )
            else:
                blocked.append(
                    "R8u79 formal search execution route plan is ready, but it is only an external/human search "
                    "execution handoff; a reviewer-filled FORMAL_SEARCH_RESULT_PACKAGE_PATH is still required before "
                    "nonlegal comparison review, formal counsel review or patent-grade claim refinement."
                )
        agent49_readiness = self._agent49_readiness()
        if str(agent49_readiness.get("coordination_status", "")).startswith("synthetic") and not self._replay_evaluation_baseline_ready():
            blocked.append("Agent49 is still synthetic_collaborative_policy_needs_field_replay; no actuator/release-gate write is allowed.")
        if evidence_matrix_status["status"] != "evidence_matrix_complete":
            blocked.append("external evidence matrix is incomplete; every method record must include source, mapping, data needs, metrics and failure boundary.")
        current = self.current_work_item
        if self._is_presentation_or_polish(current) and not bool(current.get("touches_model_metrics", False)):
            blocked.append("current work is presentation/polish-only and does not improve model metrics.")
        return blocked

    def _recommended_next_core_action(self, ranking: list[dict[str, object]]) -> dict[str, object]:
        if not ranking:
            return {
                "task_id": "no_ranked_task",
                "title": "无可执行核心任务",
                "next_experiment": "补 backlog 后重跑 Agent50。",
                "metrics": [],
                "failure_boundary": "缺任务输入。",
            }
        if self._external_field_blocker_active():
            actionable = [
                item
                for item in ranking
                if not self._field_waiting_or_consumed_task(item) and not self._is_presentation_or_polish(item)
            ]
            if not actionable:
                wait_status = self._field_evidence_wait_status()
                if self._field_activation_response_focus_handoff_ready():
                    return {
                        "task_id": "FIELD_ACTIVATION_RESPONSE_FOCUS_HANDOFF_NEXT_ACTION",
                        "title": "阶段边界：先按 focused catalyst_activity handoff 补最小外部响应",
                        "marginal_value_score": 0.0,
                        "implementation_status": "external_field_blocker_actionable_focused_handoff",
                        "external_blocker": True,
                        "blocked_by": self._field_activation_response_submission_packet_highest_priority_blocker(),
                        "first_blocked_step": self._field_activation_external_readiness_first_blocked_step(),
                        "next_operator_action": (
                            self._field_activation_response_focus_handoff_next_operator_action()
                        ),
                        "next_experiment": (
                            "当前 completion ledger 的下一隐藏状态是 catalyst_activity，且 focused handoff 已就绪。"
                            "先填写 6 行 focused_catalyst_response_template，设置 "
                            f"{self._field_activation_response_focus_handoff_source_env_var()}，运行 "
                            ".venv/bin/python experiments/run_focused_catalyst_response_merge.py；若 merge 预检通过，再把合并候选作为 "
                            "FIELD_ACTIVATION_RESPONSE_PATH 重跑 .venv/bin/python experiments/run_field_activation_matrix.py 和 "
                            ".venv/bin/python experiments/run_agent50_model_core_governance.py。该路径只减少外部采集/填报摩擦，"
                            "不生成 field 结论。"
                        ),
                        "metrics": [
                            "field_activation_response_focus_handoff_status",
                            "field_activation_response_focus_handoff_target_hidden_state",
                            "field_activation_response_focus_handoff_row_scan_reduction_ratio",
                            "field_activation_response_focus_handoff_next_operator_action",
                            "field_activation_response_focus_handoff_can_submit_to_external_activation_router",
                            "field_activation_response_submission_packet_status",
                            "field_activation_external_readiness_gate_status",
                        ],
                        "failure_boundary": (
                            "focused handoff 只把下一步缩小到 catalyst_activity 的 6 行外部响应；它不能替代完整 "
                            "field activation response、materialized package preflight、external activation router、"
                            "field replay/holdout、operator review、actuator gate 或 release gate。"
                        ),
                        "field_evidence_wait_status": wait_status,
                    }
                if self._field_activation_response_submission_packet_available():
                    return {
                        "task_id": "FIELD_ACTIVATION_RESPONSE_SUBMISSION_PACKET_NEXT_ACTION",
                        "title": "阶段边界：按 field activation response submission packet 提交外部响应",
                        "marginal_value_score": 0.0,
                        "implementation_status": "external_field_blocker_actionable_submission_packet",
                        "external_blocker": True,
                        "blocked_by": self._field_activation_response_submission_packet_highest_priority_blocker(),
                        "first_blocked_step": self._field_activation_external_readiness_first_blocked_step(),
                        "next_operator_action": (
                            self._field_activation_response_submission_packet_next_operator_action()
                        ),
                        "next_experiment": (
                            "当前内部 synthetic/template 扩张已到阶段边界。先按 R8u108 提交包执行："
                            f"{self._field_activation_response_submission_packet_next_operator_action()}。"
                            "该动作只提交并预检外部响应 JSON，不生成 field 结论；完成后重跑 "
                            "experiments/run_field_activation_matrix.py 和 "
                            "experiments/run_agent50_model_core_governance.py。"
                        ),
                        "metrics": [
                            "field_activation_response_submission_packet_status",
                            "field_activation_response_submission_packet_next_operator_action",
                            "field_activation_response_submission_packet_can_route_to_external_activation_router",
                            "field_activation_external_readiness_gate_status",
                            "field_package_import_pass",
                        ],
                        "failure_boundary": (
                            "该推荐只选择外部响应提交包的下一步；即使响应预检通过，也不能替代 "
                            "materialized package preflight、external activation router、field replay/holdout、"
                            "operator review、actuator gate 或 release gate。"
                        ),
                        "field_evidence_wait_status": wait_status,
                    }
                if self._field_activation_external_readiness_gate_available():
                    return {
                        "task_id": "FIELD_ACTIVATION_EXTERNAL_READINESS_NEXT_ACTION",
                        "title": "阶段边界：按 field activation external readiness gate 执行第一阻断动作",
                        "marginal_value_score": 0.0,
                        "implementation_status": "external_field_blocker_actionable_sequence_gate",
                        "external_blocker": True,
                        "blocked_by": self._field_activation_external_readiness_highest_priority_blocker(),
                        "first_blocked_step": self._field_activation_external_readiness_first_blocked_step(),
                        "next_operator_action": self._field_activation_external_readiness_next_operator_action(),
                        "next_experiment": (
                            "当前内部 synthetic/template 扩张已到阶段边界。先按 R8u106 顺序门执行："
                            f"{self._field_activation_external_readiness_next_operator_action()}。"
                            "该动作只推进外部证据接入，不生成 field 结论；完成后重跑 "
                            "experiments/run_field_activation_matrix.py、experiments/run_external_activation_router.py "
                            "和 experiments/run_agent50_model_core_governance.py。"
                        ),
                        "metrics": [
                            "field_activation_external_readiness_gate_status",
                            "field_activation_external_readiness_first_blocked_step",
                            "field_activation_external_readiness_can_submit_to_external_activation_router",
                            "field_package_import_pass",
                            "field_evidence_chain_ready",
                        ],
                        "failure_boundary": (
                            "该推荐只选择外部接入顺序门的下一步；即使顺序门通过，也只代表可以提交 router，"
                            "不能替代 R7/Agent44 field package preflight、Agent54 path/endpoint preflight、"
                            "field replay/holdout、operator review、actuator gate 或 release gate。"
                        ),
                        "field_evidence_wait_status": wait_status,
                    }
                return {
                    "task_id": "WAIT_real_field_package_or_new_core_interface",
                    "title": "阶段边界：等待真实 field package，或定义新的核心接口问题",
                    "marginal_value_score": 0.0,
                    "implementation_status": "external_field_blocker_wait_state",
                    "external_blocker": True,
                    "blocked_by": "real_field_package_import_or_new_core_interface_definition",
                    "next_experiment": (
                        "当前 source_basis/schema/R2/R3 synthetic 链条已形成，继续内部堆 P1-P11 边际价值低。"
                        "若有 data_origin=field 的真实包，执行 R7/Agent44->42->43->45；若没有，只有在定义新的核心接口、"
                        "新增真实工程约束或补入可验证数据需求时才开启下一轮内部迭代。"
                    ),
                    "metrics": [
                        "field_package_import_pass",
                        "field_evidence_chain_ready",
                        "source_basis_detail_ready",
                        "external_field_blocker_active",
                    ],
                    "failure_boundary": (
                        "等待态不是模型失败；它防止把 synthetic/template/literature 继续加工成 field 结论，"
                        "也防止用低边际内部补丁掩盖真实数据缺口。"
                    ),
                    "field_evidence_wait_status": wait_status,
                }
        top = dict(ranking[0])
        return {
            "task_id": top["task_id"],
            "title": top["title"],
            "marginal_value_score": top["marginal_value_score"],
            "implementation_status": top.get("implementation_status", ""),
            "external_blocker": bool(top.get("external_blocker", False)),
            "blocked_by": top.get("blocked_by", ""),
            "next_experiment": top.get("next_experiment", ""),
            "metrics": top.get("metrics", []),
            "failure_boundary": top.get("failure_boundary", ""),
        }

    def _field_waiting_or_consumed_task(self, item: dict[str, object]) -> bool:
        if bool(item.get("external_blocker", False)):
            return True
        text = " ".join(
            str(item.get(key, ""))
            for key in ("implementation_status", "next_experiment", "failure_boundary", "blocked_by")
        ).lower()
        waiting_tokens = (
            "consumed_by_",
            "waiting_on_real_field_package",
            "needs_real_field",
            "needs_real_data",
            "needs_field",
            "needs_plc_scada",
            "needs_proxy_holdout",
            "field replay",
            "field topology",
            "field labels",
            "field calibration",
            "field missingness",
            "field-supported",
            "真实 field",
            "真实包",
            "现场",
        )
        return any(token in text for token in waiting_tokens)

    def _governance_review_gate(self) -> dict[str, object]:
        current = self.current_work_item
        hard_risk = self._hard_interrupt_triggered(current)
        stage_boundary = self._at_stage_boundary(current)
        explicit_review = bool(current.get("force_governance_review", False))
        budget_remaining = self._review_budget_remaining(current)
        budget_allows_review = budget_remaining is None or budget_remaining > 0
        deep_review_allowed = hard_risk or explicit_review or (stage_boundary and budget_allows_review)
        if hard_risk:
            decision = "interrupt_and_refocus_now"
            reason = "hard-risk trigger bypasses throttle: presentation drift, evidence contradiction, or replay/guardrail boundary risk."
        elif explicit_review:
            decision = "run_stage_review"
            reason = "explicit governance review requested; use sparingly and only after a bounded work loop."
        elif stage_boundary and budget_allows_review:
            decision = "run_stage_review"
            reason = "current verifiable loop is closed; one concentrated reprioritization pass is allowed."
        elif stage_boundary and not budget_allows_review:
            decision = "defer_review_due_to_budget"
            reason = "stage boundary exists, but the governance review budget is exhausted; keep backlog and continue the selected core path."
        else:
            decision = "continue_current_micro_loop"
            reason = "no hard risk and no stage boundary; record new ideas without rerunning project-level governance."
        return {
            "review_policy": "hard_risk_or_stage_boundary_only",
            "deep_review_allowed": deep_review_allowed,
            "governance_rerun_recommended": deep_review_allowed,
            "decision": decision,
            "reason": reason,
            "hard_risk_detected": hard_risk,
            "stage_boundary": stage_boundary,
            "explicit_review_requested": explicit_review,
            "review_budget_remaining": budget_remaining,
        }

    def _self_interrupt_verdict(self, *, stage_decision: str | None = None) -> str:
        current = self.current_work_item
        if self._hard_interrupt_triggered(current):
            return "interrupt_and_refocus"
        if stage_decision == "stop_expansion_wait_for_real_field_package_or_new_core_interface":
            return "stage_boundary_wait_for_external_activation"
        return "continue_core_work"

    def _self_interrupt_reason(self, verdict: str) -> str:
        if verdict == "interrupt_and_refocus":
            return "当前工作触发硬中断：纯展示/整理漂移且无模型指标变化、硬性证据矛盾，或绕过 field replay/保护边界。"
        if verdict == "stage_boundary_wait_for_external_activation":
            return "当前不是硬中断，也不是继续内部扩张；量化阶段门已进入外部激活等待，只允许提交真实外部证据包或定义新的可测试核心接口。"
        return "当前未触发硬中断；若尚未到阶段边界，则继续完成当前可验证小闭环，普通新想法只进入延迟 backlog，避免频繁上下文切换。"

    def _stage_boundary_deferred_backlog(self) -> list[dict[str, object]]:
        current = self.current_work_item
        if self._hard_interrupt_triggered(current):
            return []
        if self._at_stage_boundary(current) or bool(current.get("force_governance_review", False)):
            return []
        if bool(current.get("touches_model_metrics", False)):
            return []
        return [
            {
                "task_id": current.get("task_id", "current_work_item"),
                "title": current.get("title", ""),
                "category": current.get("category", ""),
                "deferred_reason": (
                    "当前项未直接改变模型指标，但也未触发硬中断；只登记到阶段边界复盘，"
                    "不改变本轮 self_interrupt_verdict。"
                ),
            }
        ]

    def _hard_interrupt_triggered(self, item: dict[str, object]) -> bool:
        if bool(item.get("force_interrupt", False)) or bool(item.get("hard_evidence_contradiction", False)):
            return True
        if bool(item.get("bypasses_field_replay", False)) or bool(item.get("bypasses_guardrail", False)):
            return True
        if bool(item.get("writes_synthetic_as_field_claim", False)):
            return True
        return self._is_presentation_or_polish(item) and not bool(item.get("touches_model_metrics", False))

    @staticmethod
    def _at_stage_boundary(item: dict[str, object]) -> bool:
        return any(
            bool(item.get(key, False))
            for key in (
                "stage_boundary",
                "current_step_complete",
                "current_micro_loop_closed",
                "verification_passed",
                "iteration_boundary",
            )
        )

    @staticmethod
    def _review_budget_remaining(item: dict[str, object]) -> int | None:
        if "governance_review_budget_remaining" not in item:
            return None
        try:
            return int(item.get("governance_review_budget_remaining", 0))
        except (TypeError, ValueError):
            return 0

    @staticmethod
    def _is_presentation_or_polish(item: dict[str, object]) -> bool:
        text = " ".join(str(item.get(key, "")) for key in ("task_id", "title", "category", "description")).lower()
        presentation_tokens = (
            "ppt",
            "word",
            "deck",
            "slide",
            "presentation",
            "showcase",
            "polish",
            "展示",
            "汇报",
            "文档",
            "美化",
            "索引",
            "整理",
        )
        return any(token in text for token in presentation_tokens)

    def _issues(self, evidence_matrix_status: dict[str, object], verdict: str) -> list[QualityIssue]:
        issues: list[QualityIssue] = []
        if self._catalyst_is_weak() and not self._catalyst_proxy_baseline_ready():
            issues.append(
                QualityIssue(
                    sensor="agent48_sparse_sensing",
                    issue_type="catalyst_activity_weak_observability",
                    severity=Severity.WARNING,
                    message="catalyst_activity 是当前低成本传感链条最弱隐藏状态，必须优先补代理特征或现场标签。",
                    evidence={
                        "weak_state_coverage": self._weak_state_coverage(),
                        "catalyst_activity_observability": self._catalyst_activity_observability(),
                    },
                )
            )
        if self._catalyst_proxy_baseline_ready() and not self._catalyst_proxy_field_validated():
            issues.append(
                QualityIssue(
                    sensor="agent51_catalyst_activity_proxy",
                    issue_type="field_proxy_holdout_required",
                    severity=Severity.INFO,
                    message="Agent51 已形成 catalyst_activity synthetic proxy baseline，但仍不能解除 Agent49 保护规则。",
                    evidence={
                        "catalyst_proxy_status": self._catalyst_proxy_status(),
                        "proxy_observability_after_recommended_patch": self._catalyst_proxy_after_patch(),
                    },
                )
            )
        if self._replay_evaluation_baseline_ready() and not self._replay_evaluation_field_validated():
            issues.append(
                QualityIssue(
                    sensor="agent52_multi_facility_replay",
                    issue_type="field_multinode_replay_required",
                    severity=Severity.INFO,
                    message="Agent52 已形成 Agent49 replay-ready synthetic baseline，但仍不能提升为执行器候选。",
                    evidence={
                        "replay_evaluation_status": self._replay_evaluation_status(),
                        "joint_action_accuracy": self._replay_joint_action_accuracy(),
                    },
                )
            )
        if self._grey_box_physics_baseline_ready() and not self._grey_box_physics_field_validated():
            issues.append(
                QualityIssue(
                    sensor="agent53_minimal_grey_box_physics",
                    issue_type="field_physics_calibration_required",
                    severity=Severity.INFO,
                    message="Agent53 已形成最小灰箱物理 synthetic prior，但仍不能作为现场机理结论或放行依据。",
                    evidence={
                        "grey_box_physics_status": self._grey_box_physics_status(),
                        "mean_grey_box_residual": self._mean_grey_box_residual(),
                    },
                )
            )
        if self._soft_sensor_matrix_baseline_ready() and not self._soft_sensor_matrix_field_validated():
            issues.append(
                QualityIssue(
                    sensor="agent54_soft_sensor_matrix_coupling",
                    issue_type="field_missingness_replay_required",
                    severity=Severity.INFO,
                    message="Agent54 已形成软传感 node-modality/missingness synthetic contract，但仍不能作为现场缺测鲁棒性结论。",
                    evidence={
                        "soft_sensor_matrix_status": self._soft_sensor_matrix_status(),
                        "missingness_robustness_score": self._missingness_robustness_score(),
                    },
                )
            )
        if self._soft_sensor_matrix_baseline_ready() and not self._field_path_endpoint_label_package_ready():
            issues.append(
                QualityIssue(
                    sensor="r8u66_field_path_endpoint_label_package",
                    issue_type="field_path_endpoint_label_package_required",
                    severity=Severity.INFO,
                    message=(
                        "路径阶段标签和最终出水终点标签尚未形成可验收现场包；"
                        "因此 Agent54 的布局 holdout 不能升级为 field layout holdout，release gate 也不能用代理观测替代终点证据。"
                    ),
                    evidence={
                        "preflight_status": self._field_path_endpoint_label_preflight_status(),
                        "required_tables": self._field_path_endpoint_required_tables(),
                        "missing_tables": self._field_path_endpoint_missing_tables(),
                        "matched_batch_count": self._field_path_endpoint_matched_batch_count(),
                        "can_route_to_field_layout_holdout_with_path_labels": (
                            self._can_route_to_field_layout_holdout_with_path_labels()
                        ),
                        "release_gate_endpoint_label_blocked": self._release_gate_endpoint_label_blocked(),
                    },
                )
            )
        if self._engineering_constraints_baseline_ready() and not self._engineering_constraints_field_validated():
            issues.append(
                QualityIssue(
                    sensor="agent55_engineering_execution_constraints",
                    issue_type="field_execution_replay_required",
                    severity=Severity.INFO,
                    message="Agent55 已形成工程执行约束 reward/arbitration patch，但仍不能提升为现场执行器策略。",
                    evidence={
                        "engineering_constraints_status": self._engineering_constraints_status(),
                        "mean_execution_feasibility": self._engineering_mean_execution_feasibility(),
                    },
                )
            )
        if self._kg_reasoning_baseline_ready() and not self._kg_reasoning_field_validated():
            issues.append(
                QualityIssue(
                    sensor="agent56_knowledge_graph_reasoning",
                    issue_type="field_supported_kg_edges_required",
                    severity=Severity.INFO,
                    message="Agent56 已形成 typed KG evidence paths 和 action constraint patch，但仍不能升级为现场机理结论。",
                    evidence={
                        "kg_reasoning_status": self._kg_reasoning_status(),
                        "evidence_traceability": self._kg_evidence_traceability(),
                        "constraint_hit_rate": self._kg_constraint_hit_rate(),
                    },
                )
            )
        if self._main_chain_reconnection_baseline_ready():
            issues.append(
                QualityIssue(
                    sensor="agent57_main_chain_reconnection",
                    issue_type="field_validation_queue_alignment_required",
                    severity=Severity.INFO,
                    message="Agent57 已证明核心 prior 进入主链，但下一步仍要把 KG 验证需求逐项对齐到真实数据接口和 replay 门控。",
                    evidence={
                        "main_chain_reconnection_status": self._main_chain_reconnection_status(),
                        "main_chain_prior_consumption_rate": self._main_chain_prior_consumption_rate(),
                    },
                )
            )
        if self._field_validation_alignment_baseline_ready() and not self._field_validation_alignment_field_ready():
            issues.append(
                QualityIssue(
                    sensor="agent58_field_validation_queue_alignment",
                    issue_type="claim_specific_field_package_required",
                    severity=Severity.INFO,
                    message="Agent58 已把 KG 验证需求对齐到表、字段和 gate，但仍需最小现场采集包、必采字段升级和 source_basis 补全。",
                    evidence={
                        "field_validation_alignment_status": self._field_validation_alignment_status(),
                        "field_need_to_table_coverage": self._field_need_to_table_coverage(),
                        "field_need_to_gate_coverage": self._field_need_to_gate_coverage(),
                    },
                )
            )
        if self._claim_specific_package_baseline_ready() and not self._claim_specific_package_field_and_source_ready():
            if self._external_field_blocker_active():
                source_basis_message = (
                    "Agent59 与 unified evidence gate 表明 claim-specific schema、source_basis detail 已闭合；"
                    "当前 P11 只剩真实 field package 导入与 replay 证据链阻断，应进入 external blocker backlog，"
                    "内部迭代转向下一个不伪造 field evidence 的模型任务。"
                )
            elif self._source_basis_detail_ready():
                source_basis_message = (
                    "Agent59 已生成 claim-specific 必采字段矩阵，source_basis detail 已闭合；"
                    "当前只剩真实 field package 与 Agent44->42->43->45 证据链阻断 claim 升级。"
                )
            else:
                source_basis_message = (
                    "Agent59 已生成 claim-specific 必采字段矩阵，但 source_basis 仍需具体 citation/参数边界，"
                    "或等待真实 field package 证据链。"
                )
            issues.append(
                QualityIssue(
                    sensor="agent59_claim_specific_field_package",
                    issue_type="source_basis_detail_or_field_package_import_required",
                    severity=Severity.INFO,
                    message=source_basis_message,
                    evidence={
                        "claim_specific_package_status": self._claim_specific_package_status(),
                        "claim_specific_required_field_coverage": self._claim_specific_required_field_coverage(),
                        "source_basis_completion_rate": self._source_basis_completion_rate(),
                        "field_evidence_wait_status": self._field_evidence_wait_status(),
                    },
                )
            )
        if self._agent49_readiness().get("can_write_to_actuator") is False:
            issues.append(
                QualityIssue(
                    sensor="agent49_collaborative_control",
                    issue_type="field_replay_required_before_control_write",
                    severity=Severity.INFO,
                    message="Agent49 当前仍是 synthetic replay 草案，不能写入执行器或 release gate。",
                    evidence=self._agent49_readiness(),
                )
            )
        if evidence_matrix_status["status"] != "evidence_matrix_complete":
            issues.append(
                QualityIssue(
                    sensor="external_evidence_matrix",
                    issue_type="evidence_matrix_schema_incomplete",
                    severity=Severity.WARNING,
                    message="外部方法矩阵必须补齐来源、映射、数据需求、实现路径、指标和失败边界。",
                    evidence=evidence_matrix_status,
                )
            )
        if verdict == "interrupt_and_refocus":
            issues.append(
                QualityIssue(
                    sensor="self_interrupt",
                    issue_type="presentation_bias_detected",
                    severity=Severity.WARNING,
                    message="检测到展示/整理偏置，当前工作应中断并回到模型核心高价值任务。",
                    evidence={"current_work_item": self.current_work_item},
                )
            )
        elif verdict == "stage_boundary_wait_for_external_activation":
            issues.append(
                QualityIssue(
                    sensor="quantified_core_score_gate",
                    issue_type="stage_boundary_wait_for_external_activation",
                    severity=Severity.INFO,
                    message="量化阶段门已停止内部扩张，只允许外部证据包或新的可测试核心接口恢复主链。",
                    evidence={"current_work_item": self.current_work_item},
                )
            )
        return issues

    @staticmethod
    def _recommendations(recommended: dict[str, object], verdict: str, blocked_reasons: list[str]) -> list[str]:
        recs = []
        if verdict == "interrupt_and_refocus":
            recs.append("暂停展示或整理工作，先执行当前 priority_ranking 的最高边际价值模型任务。")
        elif verdict == "stage_boundary_wait_for_external_activation":
            recs.append(
                "停止继续堆叠内部 synthetic/template 产物；只能通过外部证据包或新的可测试核心接口恢复主链。"
            )
        recs.append(
            f"下一步优先执行 `{recommended['task_id']}`：{recommended.get('next_experiment', '')}"
        )
        if blocked_reasons:
            recs.append(f"先处理阻塞项：{'; '.join(blocked_reasons)}")
        recs.append("所有 synthetic 结果只能作为仿真基线，必须显式等待 field validation。")
        return recs

    def _agent48_coverage(self) -> dict[str, object]:
        coverage = self.agent48_metrics.get("coverage", {})
        return coverage if isinstance(coverage, dict) else {}

    def _agent49_readiness(self) -> dict[str, object]:
        readiness = self.agent49_metrics.get("readiness", {})
        return readiness if isinstance(readiness, dict) else {}

    def _catalyst_proxy_readiness(self) -> dict[str, object]:
        readiness = self.catalyst_proxy_metrics.get("readiness", {})
        return readiness if isinstance(readiness, dict) else {}

    def _catalyst_proxy_metric_block(self) -> dict[str, object]:
        metrics = self.catalyst_proxy_metrics.get("proxy_metrics", {})
        return metrics if isinstance(metrics, dict) else {}

    def _replay_readiness(self) -> dict[str, object]:
        readiness = self.replay_evaluation_metrics.get("readiness", {})
        return readiness if isinstance(readiness, dict) else {}

    def _replay_metric_block(self) -> dict[str, object]:
        metrics = self.replay_evaluation_metrics.get("offline_evaluation_metrics", {})
        return metrics if isinstance(metrics, dict) else {}

    def _grey_box_readiness(self) -> dict[str, object]:
        readiness = self.grey_box_physics_metrics.get("readiness", {})
        return readiness if isinstance(readiness, dict) else {}

    def _soft_sensor_matrix_readiness(self) -> dict[str, object]:
        readiness = self.soft_sensor_matrix_metrics.get("readiness", {})
        return readiness if isinstance(readiness, dict) else {}

    def _engineering_constraints_readiness(self) -> dict[str, object]:
        readiness = self.engineering_constraints_metrics.get("readiness", {})
        return readiness if isinstance(readiness, dict) else {}

    def _kg_reasoning_readiness(self) -> dict[str, object]:
        readiness = self.knowledge_graph_reasoning_metrics.get("readiness", {})
        return readiness if isinstance(readiness, dict) else {}

    def _main_chain_reconnection_readiness(self) -> dict[str, object]:
        readiness = self.main_chain_reconnection_metrics.get("readiness", {})
        return readiness if isinstance(readiness, dict) else {}

    def _field_validation_alignment_readiness(self) -> dict[str, object]:
        readiness = self.field_validation_queue_alignment_metrics.get("readiness", {})
        return readiness if isinstance(readiness, dict) else {}

    def _claim_specific_package_readiness(self) -> dict[str, object]:
        readiness = self.claim_specific_field_package_metrics.get("readiness", {})
        return readiness if isinstance(readiness, dict) else {}

    def _unified_field_evidence_readiness(self) -> dict[str, object]:
        readiness = self.unified_field_evidence_gate_metrics.get("readiness", {})
        return readiness if isinstance(readiness, dict) else {}

    def _claim_basis_promotion_gate(self) -> dict[str, object]:
        gate = self.unified_field_evidence_gate_metrics.get("claim_basis_promotion_gate", {})
        return gate if isinstance(gate, dict) else {}

    def _claim_basis_promotion_gate_status(self) -> str:
        return str(
            self._claim_basis_promotion_gate().get(
                "gate_status", "claim_basis_promotion_gate_not_available"
            )
        )

    def _claim_basis_promotion_ready_count(self) -> int:
        return int(self._claim_basis_promotion_gate().get("ready_promotion_count", 0) or 0)

    def _claim_basis_promotion_blocked_count(self) -> int:
        return int(self._claim_basis_promotion_gate().get("blocked_promotion_count", 0) or 0)

    def _claim_basis_promotion_can_emit_field_claim_upgrade(self) -> bool:
        return bool(self._claim_basis_promotion_gate().get("can_emit_field_claim_upgrade", False))

    def _claim_basis_promotion_can_write_to_actuator(self) -> bool:
        return bool(self._claim_basis_promotion_gate().get("can_write_to_actuator", False))

    def _claim_basis_promotion_can_write_to_release_gate(self) -> bool:
        return bool(self._claim_basis_promotion_gate().get("can_write_to_release_gate", False))

    def _real_field_package_acceptance_readiness(self) -> dict[str, object]:
        readiness = self.real_field_package_acceptance_metrics.get("readiness", {})
        return readiness if isinstance(readiness, dict) else {}

    def _r7_pipeline_readiness(self) -> dict[str, object]:
        readiness = self.r7_pipeline_metrics.get("pipeline_readiness", {})
        return readiness if isinstance(readiness, dict) else {}

    def _observation_contract_readiness(self) -> dict[str, object]:
        readiness = self.observation_contract_metrics.get("readiness", {})
        return readiness if isinstance(readiness, dict) else {}

    def _control_replay_stress_readiness(self) -> dict[str, object]:
        readiness = self.control_replay_stress_metrics.get("readiness", {})
        return readiness if isinstance(readiness, dict) else {}

    def _agent48_comparable_baseline_ready(self) -> bool:
        comparison = self.agent48_metrics.get("algorithm_comparison", [])
        if not isinstance(comparison, list):
            return False
        strategy_ids = {str(item.get("strategy_id", "")) for item in comparison if isinstance(item, dict)}
        required = {
            "greedy_marginal",
            "reconstruction_qr_proxy",
            "classification_sspoc_proxy",
            "topology_robust_cost_proxy",
        }
        selected_strategy = self.agent48_metrics.get("selected_strategy", {})
        return required.issubset(strategy_ids) and isinstance(selected_strategy, dict) and bool(selected_strategy.get("strategy_id"))

    def _weak_state_coverage(self) -> float:
        return float(self._agent48_coverage().get("weak_state_coverage", 0.0))

    def _catalyst_activity_observability(self) -> float:
        return float(self._agent48_coverage().get("catalyst_activity_observability", 0.0))

    def _catalyst_is_weak(self) -> bool:
        return self._weak_state_coverage() <= 0.35 or self._catalyst_activity_observability() < 0.55

    def _catalyst_proxy_status(self) -> str:
        return str(self._catalyst_proxy_readiness().get("catalyst_proxy_status", "not_available"))

    def _catalyst_proxy_after_patch(self) -> float:
        return float(self._catalyst_proxy_metric_block().get("proxy_observability_after_recommended_patch", 0.0))

    def _catalyst_proxy_baseline_ready(self) -> bool:
        readiness = self._catalyst_proxy_readiness()
        if not readiness:
            return False
        return (
            bool(readiness.get("proxy_ready", False))
            and self._catalyst_proxy_after_patch() >= 0.58
            and str(readiness.get("catalyst_proxy_status", "")).startswith(("synthetic_", "field_"))
        )

    def _catalyst_proxy_field_validated(self) -> bool:
        return bool(self._catalyst_proxy_readiness().get("field_validated", False))

    def _replay_evaluation_status(self) -> str:
        return str(self._replay_readiness().get("replay_evaluation_status", "not_available"))

    def _replay_joint_action_accuracy(self) -> float:
        return float(self._replay_metric_block().get("joint_action_accuracy", 0.0))

    def _replay_evaluation_baseline_ready(self) -> bool:
        readiness = self._replay_readiness()
        if not readiness:
            return False
        metrics = self._replay_metric_block()
        return (
            bool(readiness.get("synthetic_replay_ready", False))
            and int(metrics.get("replay_case_count", 0)) >= 5
            and str(readiness.get("replay_evaluation_status", "")).startswith(("synthetic_", "field_"))
        )

    def _replay_evaluation_field_validated(self) -> bool:
        return bool(self._replay_readiness().get("field_ready", False))

    def _grey_box_physics_status(self) -> str:
        return str(self._grey_box_readiness().get("grey_box_physics_status", "not_available"))

    def _mean_grey_box_residual(self) -> float:
        return float(self._grey_box_readiness().get("mean_grey_box_residual", 0.0))

    def _grey_box_physics_baseline_ready(self) -> bool:
        readiness = self._grey_box_readiness()
        if not readiness:
            return False
        return (
            bool(readiness.get("synthetic_prior_ready", False))
            and str(readiness.get("grey_box_physics_status", "")).startswith(("synthetic_", "field_"))
        )

    def _grey_box_physics_field_validated(self) -> bool:
        return bool(self._grey_box_readiness().get("field_ready", False))

    def _soft_sensor_matrix_status(self) -> str:
        return str(self._soft_sensor_matrix_readiness().get("soft_sensor_matrix_status", "not_available"))

    def _missingness_robustness_score(self) -> float:
        return float(self._soft_sensor_matrix_readiness().get("missingness_robustness_score", 0.0))

    def _soft_sensor_matrix_baseline_ready(self) -> bool:
        readiness = self._soft_sensor_matrix_readiness()
        if not readiness:
            return False
        return (
            bool(readiness.get("can_update_soft_sensor_training_schema", False))
            and str(readiness.get("soft_sensor_matrix_status", "")).startswith(("synthetic_", "field_"))
        )

    def _soft_sensor_matrix_field_validated(self) -> bool:
        return bool(self._soft_sensor_matrix_readiness().get("field_ready", False))

    def _engineering_constraints_status(self) -> str:
        return str(self._engineering_constraints_readiness().get("engineering_constraints_status", "not_available"))

    def _engineering_mean_execution_feasibility(self) -> float:
        return float(self._engineering_constraints_readiness().get("mean_execution_feasibility", 0.0))

    def _engineering_constraints_baseline_ready(self) -> bool:
        readiness = self._engineering_constraints_readiness()
        if not readiness:
            return False
        return (
            bool(readiness.get("can_update_agent49_reward_contract", False))
            and str(readiness.get("engineering_constraints_status", "")).startswith(("synthetic_", "field_"))
        )

    def _engineering_constraints_field_validated(self) -> bool:
        return bool(self._engineering_constraints_readiness().get("field_ready", False))

    def _kg_reasoning_status(self) -> str:
        return str(self._kg_reasoning_readiness().get("kg_reasoning_status", "not_available"))

    def _kg_evidence_traceability(self) -> float:
        return float(self._kg_reasoning_readiness().get("evidence_traceability", 0.0))

    def _kg_constraint_hit_rate(self) -> float:
        return float(self._kg_reasoning_readiness().get("constraint_hit_rate", 0.0))

    def _kg_reasoning_baseline_ready(self) -> bool:
        readiness = self._kg_reasoning_readiness()
        if not readiness:
            return False
        return (
            bool(readiness.get("can_update_mechanism_evidence", False))
            and bool(readiness.get("can_update_action_bias_prior", False))
            and str(readiness.get("kg_reasoning_status", "")).startswith(("kg_", "field_"))
        )

    def _kg_reasoning_field_validated(self) -> bool:
        return float(self._kg_reasoning_readiness().get("field_supported_edge_ratio", 0.0)) > 0.0

    def _main_chain_reconnection_status(self) -> str:
        return str(self._main_chain_reconnection_readiness().get("main_chain_reconnection_status", "not_available"))

    def _main_chain_prior_consumption_rate(self) -> float:
        return float(self._main_chain_reconnection_readiness().get("main_chain_prior_consumption_rate", 0.0))

    def _main_chain_reconnection_baseline_ready(self) -> bool:
        readiness = self._main_chain_reconnection_readiness()
        if not readiness:
            return False
        return (
            bool(readiness.get("can_update_agent50_priority", False))
            and self._main_chain_prior_consumption_rate() >= 0.84
            and str(readiness.get("main_chain_reconnection_status", "")).startswith("synthetic_")
        )

    def _field_validation_alignment_status(self) -> str:
        return str(self._field_validation_alignment_readiness().get("field_validation_alignment_status", "not_available"))

    def _field_need_to_table_coverage(self) -> float:
        return float(self._field_validation_alignment_readiness().get("field_need_to_table_coverage", 0.0))

    def _field_need_to_gate_coverage(self) -> float:
        return float(self._field_validation_alignment_readiness().get("field_need_to_gate_coverage", 0.0))

    def _field_validation_alignment_baseline_ready(self) -> bool:
        readiness = self._field_validation_alignment_readiness()
        if not readiness:
            return False
        return (
            bool(readiness.get("can_update_agent50_priority", False))
            and self._field_need_to_table_coverage() >= 0.95
            and self._field_need_to_gate_coverage() >= 0.95
            and str(readiness.get("field_validation_alignment_status", "")).startswith("field_validation_alignment_")
        )

    def _field_validation_alignment_field_ready(self) -> bool:
        status = self._field_validation_alignment_status()
        return status == "field_validation_alignment_field_chain_ready_for_human_review"

    def _claim_specific_package_status(self) -> str:
        return str(self._claim_specific_package_readiness().get("claim_specific_package_status", "not_available"))

    def _claim_specific_required_field_coverage(self) -> float:
        return float(self._claim_specific_package_readiness().get("claim_specific_required_field_coverage", 0.0))

    def _source_basis_completion_rate(self) -> float:
        return float(self._claim_specific_package_readiness().get("source_basis_completion_rate", 0.0))

    def _claim_specific_package_baseline_ready(self) -> bool:
        readiness = self._claim_specific_package_readiness()
        if not readiness:
            return False
        return (
            bool(readiness.get("can_update_agent50_priority", False))
            and self._claim_specific_required_field_coverage() >= 0.95
            and str(readiness.get("claim_specific_package_status", "")).startswith("claim_specific_package_")
        )

    def _claim_specific_package_field_and_source_ready(self) -> bool:
        return self._claim_specific_package_status() == "claim_specific_package_field_and_source_ready_for_human_review"

    def _unified_field_evidence_status(self) -> str:
        return str(self._unified_field_evidence_readiness().get("unified_field_evidence_gate_status", "not_available"))

    def _real_field_package_acceptance_status(self) -> str:
        return str(self._real_field_package_acceptance_readiness().get("real_field_package_acceptance_status", "not_available"))

    def _r7_field_evidence_sufficiency_status(self) -> str:
        return str(self._r7_pipeline_readiness().get("field_evidence_sufficiency_status", "not_available"))

    def _r7_field_evidence_sufficiency_score(self) -> float:
        return float(self._r7_pipeline_readiness().get("field_evidence_sufficiency_score", 0.0) or 0.0)

    def _r7_field_evidence_smoke_pass(self) -> bool:
        return bool(self._r7_pipeline_readiness().get("field_evidence_smoke_pass", False))

    def _r7_can_route_to_human_review_candidate(self) -> bool:
        return bool(self._r7_pipeline_readiness().get("can_route_to_human_review_candidate", False))

    def _r7_submission_readiness_status(self) -> str:
        return str(
            self._r7_pipeline_readiness().get(
                "field_package_submission_readiness_status",
                "not_available",
            )
        )

    def _r7_submission_highest_priority_blocker(self) -> str:
        return str(
            self._r7_pipeline_readiness().get(
                "field_package_submission_highest_priority_blocker",
                "not_available",
            )
        )

    def _r7_submission_next_operator_action(self) -> str:
        return str(
            self._r7_pipeline_readiness().get(
                "field_package_submission_next_operator_action",
                "not_available",
            )
        )

    def _r7_submission_blocking_stage_count(self) -> int:
        try:
            return int(
                self._r7_pipeline_readiness().get(
                    "field_package_submission_blocking_stage_count",
                    0,
                )
                or 0
            )
        except (TypeError, ValueError):
            return 0

    def _r7_submission_repair_work_order(self) -> dict[str, object]:
        submission = self.r7_pipeline_metrics.get("field_package_submission_readiness", {})
        if isinstance(submission, dict):
            work_order = submission.get("field_package_submission_repair_work_order", {})
            if isinstance(work_order, dict):
                return work_order
        return {}

    def _r7_submission_repair_work_order_status(self) -> str:
        readiness_status = self._r7_pipeline_readiness().get("field_package_submission_repair_work_order_status")
        if readiness_status:
            return str(readiness_status)
        return str(self._r7_submission_repair_work_order().get("work_order_status", "not_available"))

    def _r7_submission_repair_item_count(self) -> int:
        try:
            readiness_count = self._r7_pipeline_readiness().get("field_package_submission_repair_item_count")
            if readiness_count not in (None, ""):
                return int(readiness_count or 0)
            return int(self._r7_submission_repair_work_order().get("repair_item_count", 0) or 0)
        except (TypeError, ValueError):
            return 0

    def _r7_submission_repair_work_order_path(self) -> str:
        package = self.manifest.get("r7_real_field_replay_pipeline", {})
        if isinstance(package, dict) and package.get("submission_repair_work_order"):
            return str(package.get("submission_repair_work_order"))
        return "outputs/r7_real_field_replay_pipeline/field_package_submission_repair_work_order.json"

    def _r7_submission_repair_response_preflight_status(self) -> str:
        return str(
            self._r7_pipeline_readiness().get(
                "field_package_submission_repair_response_preflight_status",
                "not_available",
            )
        )

    def _r7_submission_repair_response_can_route_to_r7_preflight(self) -> bool:
        return bool(
            self._r7_pipeline_readiness().get(
                "field_package_submission_repair_response_can_route_to_r7_preflight",
                False,
            )
        )

    def _r7_submission_repair_response_template_path(self) -> str:
        package = self.manifest.get("r7_real_field_replay_pipeline", {})
        if isinstance(package, dict) and package.get("submission_repair_response_template"):
            return str(package.get("submission_repair_response_template"))
        return "outputs/r7_real_field_replay_pipeline/field_package_submission_repair_response_template.json"

    def _r7_submission_repair_response_preflight_path(self) -> str:
        package = self.manifest.get("r7_real_field_replay_pipeline", {})
        if isinstance(package, dict) and package.get("submission_repair_response_preflight"):
            return str(package.get("submission_repair_response_preflight"))
        return "outputs/r7_real_field_replay_pipeline/field_package_submission_repair_response_preflight.json"

    def _field_path_endpoint_label_preflight_status(self) -> str:
        return str(self.field_path_endpoint_label_preflight.get("preflight_status", "not_available"))

    def _field_path_endpoint_matched_batch_count(self) -> int:
        try:
            return int(self.field_path_endpoint_label_preflight.get("matched_batch_count", 0) or 0)
        except (TypeError, ValueError):
            return 0

    def _field_path_endpoint_required_matched_batch_deficit(self) -> int:
        try:
            return int(self.field_path_endpoint_label_preflight.get("required_matched_batch_deficit", 0) or 0)
        except (TypeError, ValueError):
            return 0

    def _field_path_endpoint_batch_alignment_gap_count(self) -> int:
        try:
            return int(self.field_path_endpoint_label_preflight.get("batch_alignment_gap_count", 0) or 0)
        except (TypeError, ValueError):
            return 0

    def _field_path_endpoint_alignment_patch_plan(self) -> dict[str, object]:
        plan = self.field_path_endpoint_label_preflight.get("alignment_patch_plan", {})
        return plan if isinstance(plan, dict) else {}

    def _field_path_endpoint_alignment_patch_plan_status(self) -> str:
        return str(self._field_path_endpoint_alignment_patch_plan().get("patch_plan_status", "not_available"))

    def _field_path_endpoint_alignment_patch_plan_item_count(self) -> int:
        try:
            return int(self._field_path_endpoint_alignment_patch_plan().get("item_count", 0) or 0)
        except (TypeError, ValueError):
            return 0

    def _field_path_endpoint_missing_tables(self) -> list[str]:
        missing = self.field_path_endpoint_label_preflight.get("missing_tables", [])
        if not isinstance(missing, list):
            return []
        return [str(table) for table in missing]

    def _field_path_endpoint_required_tables(self) -> list[str]:
        required = self.field_path_endpoint_label_preflight.get("required_tables", [])
        if not isinstance(required, list):
            return []
        return [str(table) for table in required]

    def _field_path_endpoint_label_package_ready(self) -> bool:
        return bool(self.field_path_endpoint_label_preflight.get("can_route_to_field_layout_holdout", False))

    def _field_path_endpoint_final_effluent_label_ready(self) -> bool:
        return self._field_path_endpoint_label_package_ready()

    def _can_route_to_field_layout_holdout_with_path_labels(self) -> bool:
        return (
            bool(self._r7_pipeline_readiness().get("can_route_to_field_holdout", False))
            and self._field_path_endpoint_label_package_ready()
        )

    def _release_gate_endpoint_label_blocked(self) -> bool:
        return not self._field_path_endpoint_final_effluent_label_ready()

    def _formal_search_execution_route_plan_status(self) -> str:
        return str(
            self.formal_search_execution_route_plan.get(
                "route_plan_status",
                "formal_search_execution_route_plan_not_available",
            )
        )

    def _formal_search_execution_route_plan_ready(self) -> bool:
        return (
            self._formal_search_execution_route_plan_status()
            == "formal_search_execution_route_plan_ready_waiting_for_external_search_execution"
            and self._formal_search_execution_boundary_preserved()
        )

    def _formal_search_execution_route_row_count(self) -> int:
        try:
            return int(self.formal_search_execution_route_plan.get("route_row_count", 0) or 0)
        except (TypeError, ValueError):
            return 0

    def _formal_search_execution_complete_route_row_count(self) -> int:
        try:
            return int(
                self.formal_search_execution_route_plan.get("complete_route_row_count", 0)
                or 0
            )
        except (TypeError, ValueError):
            return 0

    def _formal_search_execution_mapped_seed_route_count(self) -> int:
        try:
            return int(
                self.formal_search_execution_route_plan.get("mapped_seed_route_count", 0)
                or 0
            )
        except (TypeError, ValueError):
            return 0

    def _formal_search_execution_operator_first_action(self) -> str:
        return str(
            self.formal_search_execution_route_plan.get(
                "operator_first_action",
                "submit_formal_search_result_package_after_external_search",
            )
        )

    def _formal_search_execution_boundary_preserved(self) -> bool:
        return (
            self.formal_search_execution_route_plan.get("can_generate_prior_art_result") is False
            and self.formal_search_execution_route_plan.get("legal_opinion_allowed") is False
            and self.formal_search_execution_route_plan.get("can_emit_claim_text") is False
            and self.formal_search_execution_route_plan.get("field_claim_upgrade_allowed") is False
            and self.formal_search_execution_route_plan.get(
                "can_submit_synthetic_or_template_result_package"
            )
            is False
        )

    def _formal_search_ai_nonlegal_review_brief_metadata(self) -> dict[str, object]:
        metadata = self.formal_search_ai_nonlegal_review_brief.get("brief_metadata", {})
        return metadata if isinstance(metadata, dict) else {}

    def _formal_search_ai_nonlegal_review_brief_readiness(self) -> dict[str, object]:
        readiness = self.formal_search_ai_nonlegal_review_brief.get("review_readiness", {})
        return readiness if isinstance(readiness, dict) else {}

    def _formal_search_ai_nonlegal_review_brief_boundary(self) -> dict[str, object]:
        boundary = self.formal_search_ai_nonlegal_review_brief.get("boundary", {})
        return boundary if isinstance(boundary, dict) else {}

    def _formal_search_ai_nonlegal_review_brief_operator_next_action(self) -> dict[str, object]:
        action = self.formal_search_ai_nonlegal_review_brief.get("operator_next_action", {})
        return action if isinstance(action, dict) else {}

    def _formal_search_ai_nonlegal_review_brief_status(self) -> str:
        return str(
            self._formal_search_ai_nonlegal_review_brief_metadata().get(
                "brief_status",
                "formal_search_ai_nonlegal_review_brief_not_available",
            )
        )

    def _formal_search_ai_nonlegal_review_brief_ready(self) -> bool:
        return (
            self._formal_search_ai_nonlegal_review_brief_status()
            == "formal_search_ai_nonlegal_review_brief_ready_for_human_review"
            and self._formal_search_ai_nonlegal_review_brief_boundary_preserved()
        )

    def _formal_search_ai_nonlegal_review_brief_row_count(self) -> int:
        try:
            return int(
                self._formal_search_ai_nonlegal_review_brief_readiness().get(
                    "brief_row_count",
                    0,
                )
                or 0
            )
        except (TypeError, ValueError):
            return 0

    def _formal_search_ai_nonlegal_review_brief_missing_source_row_count(self) -> int:
        try:
            return int(
                self._formal_search_ai_nonlegal_review_brief_readiness().get(
                    "missing_source_row_count",
                    0,
                )
                or 0
            )
        except (TypeError, ValueError):
            return 0

    def _formal_search_ai_nonlegal_review_brief_missing_claim_mapping_row_count(self) -> int:
        try:
            return int(
                self._formal_search_ai_nonlegal_review_brief_readiness().get(
                    "missing_claim_mapping_row_count",
                    0,
                )
                or 0
            )
        except (TypeError, ValueError):
            return 0

    def _formal_search_ai_nonlegal_review_brief_can_help_human_review(self) -> bool:
        return bool(
            self._formal_search_ai_nonlegal_review_brief_readiness().get(
                "can_help_human_nonlegal_review",
                False,
            )
        )

    def _formal_search_ai_nonlegal_review_brief_can_route_to_claim_scope_patch_draft(
        self,
    ) -> bool:
        return bool(
            self._formal_search_ai_nonlegal_review_brief_readiness().get(
                "can_route_to_claim_scope_patch_draft",
                False,
            )
        )

    def _formal_search_ai_nonlegal_review_brief_boundary_preserved(self) -> bool:
        readiness = self._formal_search_ai_nonlegal_review_brief_readiness()
        boundary = self._formal_search_ai_nonlegal_review_brief_boundary()
        return (
            readiness.get("can_route_to_claim_scope_patch_draft") is False
            and readiness.get("can_generate_prior_art_result") is False
            and readiness.get("legal_opinion_allowed") is False
            and readiness.get("field_claim_upgrade_allowed") is False
            and boundary.get("can_emit_claim_text") is False
            and boundary.get("can_resume_model_chain") is False
            and boundary.get("can_write_to_actuator") is False
            and boundary.get("can_write_to_release_gate") is False
        )

    def _formal_search_ai_nonlegal_review_brief_next_operator_action(self) -> str:
        return str(
            self._formal_search_ai_nonlegal_review_brief_operator_next_action().get(
                "next_operator_action",
                "submit_human_nonlegal_review_response_via_FORMAL_SEARCH_NONLEGAL_REVIEW_RESPONSE_PATH",
            )
        )

    def _formal_search_nonlegal_review_operator_packet_metadata(self) -> dict[str, object]:
        metadata = self.formal_search_nonlegal_review_operator_packet.get(
            "operator_packet_metadata",
            {},
        )
        return metadata if isinstance(metadata, dict) else {}

    def _formal_search_nonlegal_review_operator_packet_action(self) -> dict[str, object]:
        action = self.formal_search_nonlegal_review_operator_packet.get(
            "operator_action",
            {},
        )
        return action if isinstance(action, dict) else {}

    def _formal_search_nonlegal_review_operator_packet_downstream(self) -> dict[str, object]:
        downstream = self.formal_search_nonlegal_review_operator_packet.get(
            "downstream_state",
            {},
        )
        return downstream if isinstance(downstream, dict) else {}

    def _formal_search_nonlegal_review_operator_packet_boundary(self) -> dict[str, object]:
        boundary = self.formal_search_nonlegal_review_operator_packet.get("boundary", {})
        return boundary if isinstance(boundary, dict) else {}

    def _formal_search_nonlegal_review_operator_packet_status(self) -> str:
        return str(
            self._formal_search_nonlegal_review_operator_packet_metadata().get(
                "packet_status",
                "formal_search_nonlegal_review_operator_packet_not_available",
            )
        )

    def _formal_search_nonlegal_review_operator_packet_ready(self) -> bool:
        return (
            self._formal_search_nonlegal_review_operator_packet_status()
            in {
                "formal_search_nonlegal_review_operator_packet_ready_waiting_for_human_response",
                "formal_search_nonlegal_review_operator_packet_human_response_ready_for_agent60_patch_gate",
            }
            and self._formal_search_nonlegal_review_operator_packet_boundary_preserved()
        )

    def _formal_search_nonlegal_review_operator_packet_expected_review_packet_row_count(
        self,
    ) -> int:
        return self._safe_int(
            self._formal_search_nonlegal_review_operator_packet_action().get(
                "expected_review_packet_row_count",
                0,
            )
        )

    def _formal_search_nonlegal_review_operator_packet_high_priority_review_row_count(
        self,
    ) -> int:
        return self._safe_int(
            self._formal_search_nonlegal_review_operator_packet_action().get(
                "high_priority_review_row_count",
                0,
            )
        )

    def _formal_search_nonlegal_review_operator_packet_accepted_review_row_count(
        self,
    ) -> int:
        return self._safe_int(
            self._formal_search_nonlegal_review_operator_packet_action().get(
                "accepted_review_row_count",
                0,
            )
        )

    def _formal_search_nonlegal_review_operator_packet_source_env_var(self) -> str:
        return str(
            self._formal_search_nonlegal_review_operator_packet_action().get(
                "source_env_var",
                "FORMAL_SEARCH_NONLEGAL_REVIEW_RESPONSE_PATH",
            )
        )

    def _formal_search_nonlegal_review_operator_packet_can_route_to_claim_scope_patch_draft(
        self,
    ) -> bool:
        return bool(
            self._formal_search_nonlegal_review_operator_packet_downstream().get(
                "can_route_to_claim_scope_patch_draft",
                False,
            )
        )

    def _formal_search_nonlegal_review_operator_packet_boundary_preserved(self) -> bool:
        boundary = self._formal_search_nonlegal_review_operator_packet_boundary()
        return (
            boundary.get("can_generate_prior_art_result") is False
            and boundary.get("legal_opinion_allowed") is False
            and boundary.get("field_claim_upgrade_allowed") is False
            and boundary.get("can_emit_claim_text") is False
            and boundary.get("can_resume_model_chain") is False
            and boundary.get("can_write_to_actuator") is False
            and boundary.get("can_write_to_release_gate") is False
            and boundary.get("can_route_to_claim_scope_patch_draft_without_human_response")
            is False
        )

    def _formal_search_nonlegal_review_operator_packet_next_operator_action(self) -> str:
        return str(
            self._formal_search_nonlegal_review_operator_packet_action().get(
                "next_operator_action",
                "complete_human_nonlegal_review_response_via_FORMAL_SEARCH_NONLEGAL_REVIEW_RESPONSE_PATH",
            )
        )

    def _formal_search_nonlegal_review_operator_packet_core_gate_fields(
        self,
    ) -> dict[str, object]:
        boundary = self._formal_search_nonlegal_review_operator_packet_boundary()
        return {
            "formal_nonlegal_review_operator_packet_status": (
                self._formal_search_nonlegal_review_operator_packet_status()
            ),
            "formal_nonlegal_review_operator_packet_ready": (
                self._formal_search_nonlegal_review_operator_packet_ready()
            ),
            "formal_nonlegal_review_operator_packet_expected_review_packet_row_count": (
                self._formal_search_nonlegal_review_operator_packet_expected_review_packet_row_count()
            ),
            "formal_nonlegal_review_operator_packet_high_priority_review_row_count": (
                self._formal_search_nonlegal_review_operator_packet_high_priority_review_row_count()
            ),
            "formal_nonlegal_review_operator_packet_accepted_review_row_count": (
                self._formal_search_nonlegal_review_operator_packet_accepted_review_row_count()
            ),
            "formal_nonlegal_review_operator_packet_source_env_var": (
                self._formal_search_nonlegal_review_operator_packet_source_env_var()
            ),
            "formal_nonlegal_review_operator_packet_next_operator_action": (
                self._formal_search_nonlegal_review_operator_packet_next_operator_action()
            ),
            "formal_nonlegal_review_operator_packet_can_route_to_claim_scope_patch_draft": (
                self._formal_search_nonlegal_review_operator_packet_can_route_to_claim_scope_patch_draft()
            ),
            "formal_nonlegal_review_operator_packet_boundary_preserved": (
                self._formal_search_nonlegal_review_operator_packet_boundary_preserved()
            ),
            "formal_nonlegal_review_operator_packet_can_generate_prior_art_result": bool(
                boundary.get("can_generate_prior_art_result", False)
            ),
            "formal_nonlegal_review_operator_packet_legal_opinion_allowed": bool(
                boundary.get("legal_opinion_allowed", False)
            ),
            "formal_nonlegal_review_operator_packet_field_claim_upgrade_allowed": bool(
                boundary.get("field_claim_upgrade_allowed", False)
            ),
            "formal_nonlegal_review_operator_packet_can_emit_claim_text": bool(
                boundary.get("can_emit_claim_text", False)
            ),
            "formal_nonlegal_review_operator_packet_can_resume_model_chain": bool(
                boundary.get("can_resume_model_chain", False)
            ),
            "formal_nonlegal_review_operator_packet_can_write_to_actuator": bool(
                boundary.get("can_write_to_actuator", False)
            ),
            "formal_nonlegal_review_operator_packet_can_write_to_release_gate": bool(
                boundary.get("can_write_to_release_gate", False)
            ),
        }

    def _source_basis_detail_ready(self) -> bool:
        unified = self._unified_field_evidence_readiness()
        return (
            self._source_basis_completion_rate() >= 0.95
            or float(unified.get("source_basis_completion_rate", 0.0)) >= 0.95
            or (
                float(unified.get("citation_detail_completion_rate", 0.0)) >= 0.95
                and float(unified.get("source_basis_parameter_boundary_coverage", 0.0)) >= 0.95
            )
        )

    def _field_evidence_chain_ready(self) -> bool:
        unified = self._unified_field_evidence_readiness()
        r7 = self._real_field_package_acceptance_readiness()
        return any(
            bool(flag)
            for flag in (
                self._claim_specific_package_field_and_source_ready(),
                unified.get("can_emit_field_claim_upgrade", False),
                unified.get("field_import_pass", False)
                and unified.get("field_replay_evidence_chain_pass", False)
                and unified.get("soft_sensor_field_holdout_gate_pass", False),
                r7.get("can_emit_field_supported_claim_candidate", False),
                r7.get("field_package_import_pass", False)
                and r7.get("field_replay_evidence_chain_pass", False)
                and r7.get("soft_sensor_field_holdout_gate_pass", False),
            )
        )

    def _field_import_ready(self) -> bool:
        unified = self._unified_field_evidence_readiness()
        r7 = self._real_field_package_acceptance_readiness()
        return (
            bool(unified.get("field_import_pass", False))
            or bool(r7.get("field_package_import_pass", False))
            or self._r7_field_evidence_smoke_pass()
        )

    def _external_field_blocker_active(self) -> bool:
        return (
            self._claim_specific_package_baseline_ready()
            and self._source_basis_detail_ready()
            and not self._field_evidence_chain_ready()
            and not self._field_import_ready()
        )

    def _external_activation_contract(self) -> dict[str, object]:
        """Machine-readable conditions for leaving the external-evidence wait state."""

        field_channel = {
            "channel_id": "R7_REAL_FIELD_PACKAGE",
            "channel_type": "field_validation",
            "current_status": self._r7_field_evidence_sufficiency_status(),
            "package_pointer": "REAL_FIELD_REPLAY_PACKAGE_DIR",
            "can_resume_model_chain": self._field_import_ready(),
            "ready_for_external_submission": True,
            "next_operator_action": self._r7_submission_next_operator_action(),
            "repair_work_order_status": self._r7_submission_repair_work_order_status(),
            "repair_item_count": self._r7_submission_repair_item_count(),
            "repair_work_order_path": self._r7_submission_repair_work_order_path(),
            "repair_response_preflight_status": self._r7_submission_repair_response_preflight_status(),
            "repair_response_can_route_to_r7_preflight": (
                self._r7_submission_repair_response_can_route_to_r7_preflight()
            ),
            "repair_response_template_path": self._r7_submission_repair_response_template_path(),
            "repair_response_preflight_path": self._r7_submission_repair_response_preflight_path(),
            "required_evidence": [
                "metadata.json with data_origin=field and no placeholder/template markers",
                "timestamped sensor_timeseries rows with batch_id, timestamp, node_id/sensor_id and sensor_status",
                "campaign_operation_log rows with action/effect timing and operator context",
                "offline_lab_results rows linked by batch_id and method/detection-limit metadata",
                "fast_proxy_event_log or equivalent proxy labels when pressure/conflict replay is evaluated",
            ],
            "resumes_to": [
                "Agent44 field import preflight",
                "Agent42 timestamped campaign replay",
                "Agent43 G6/P6 calibration gate",
                "Agent45 field replay evidence chain",
            ],
            "reject_if": [
                "header-only template package",
                "data_origin is synthetic/sample/template or missing",
                "batch_id/timestamp alignment is absent",
                "metadata contains TODO, placeholder or template markers",
            ],
            "no_write_boundary": (
                "Import/replay readiness can create field-review candidates only; actuator and release-gate writes "
                "remain blocked until holdout, operator review and release validation pass."
            ),
        }
        path_channel_ready = self._can_route_to_field_layout_holdout_with_path_labels()
        path_channel = {
            "channel_id": "R8U66_PATH_ENDPOINT_LABEL_PACKAGE",
            "channel_type": "field_layout_holdout",
            "current_status": self._field_path_endpoint_label_preflight_status(),
            "package_pointer": "FIELD_PATH_ENDPOINT_LABEL_PACKAGE_DIR",
            "can_resume_model_chain": path_channel_ready,
            "ready_for_external_submission": True,
            "next_operator_action": self.field_path_endpoint_label_preflight.get(
                "next_operator_action",
                "submit_field_path_endpoint_label_package_rows",
            ),
            "required_evidence": [
                "site_topology_or_bed_geometry",
                "node_modality_sensor_timeseries",
                "hydraulic_path_stage_labels",
                "final_effluent_endpoint_labels",
                "campaign_operation_log",
                "offline_lab_results",
                "at least 5 same-batch aligned path/endpoint/lab/operation rows",
            ],
            "resumes_to": [
                "Agent54 field layout holdout",
                "soft-sensor endpoint/path validation",
                "release-gate candidate review after field holdout and human review",
            ],
            "reject_if": [
                "any required table is missing or header-only",
                "matched_batch_count is below 5",
                "final_effluent_endpoint_labels are absent",
                "template markers or non-field provenance are present",
            ],
            "no_write_boundary": (
                "Path/endpoint readiness supports layout holdout only; it never directly authorizes release."
            ),
        }
        formal_handoff_ready = self._formal_search_execution_route_plan_ready()
        formal_channel = {
            "channel_id": "R8U79_FORMAL_SEARCH_RESULT_PACKAGE",
            "channel_type": "formal_search_review",
            "current_status": self._formal_search_execution_route_plan_status(),
            "linked_review_readiness_status": self._formal_search_linked_review_readiness_status(),
            "package_pointer": "FORMAL_SEARCH_RESULT_PACKAGE_PATH",
            "can_resume_model_chain": False,
            "ready_for_external_submission": formal_handoff_ready,
            "next_operator_action": self._formal_search_execution_operator_first_action(),
            "required_evidence": [
                "reviewer-filled formal_search_result_package with source manifest",
                "prior_art_hits rows produced by external/human search, not by project templates",
                "claim_element_comparisons rows with source links and reviewer notes",
                "source/table/row preflight pass before nonlegal comparison review",
            ],
            "resumes_to": [
                "R8u78 formal search result validation",
                "nonlegal comparison review packet",
                "formal counsel review handoff",
                "human disclosure revision queue",
            ],
            "reject_if": [
                "seed matrix is submitted as accepted prior art",
                "template package is submitted as search result",
                "synthetic/generated hit rows are present",
                "claim text, legal opinion or field-supported claim is emitted by the model",
            ],
            "no_write_boundary": (
                "Formal-search package readiness can route to human/nonlegal/formal review only; it does not "
                "create patentability, legal or field-validity conclusions."
            ),
        }
        channels = [field_channel, path_channel, formal_channel]
        ready_channels = [channel for channel in channels if bool(channel["can_resume_model_chain"])]
        handoff_channels = [channel for channel in channels if bool(channel["ready_for_external_submission"])]
        return {
            "contract_id": "R8u81_external_evidence_activation_contract",
            "architecture_layer": "verification_governance_layer",
            "enhanced_abilities": ["verifiability", "engineering_feasibility", "protectability"],
            "contract_status": (
                "external_evidence_activation_ready"
                if ready_channels
                else "waiting_for_external_evidence_packages"
            ),
            "activation_ready": bool(ready_channels),
            "ready_channel_count": len(ready_channels),
            "handoff_ready_channel_count": len(handoff_channels),
            "blocked_channel_count": len(channels) - len(ready_channels),
            "channels": channels,
            "next_operator_actions": [
                {
                    "channel_id": channel["channel_id"],
                    "package_pointer": channel["package_pointer"],
                    "next_operator_action": channel["next_operator_action"],
                }
                for channel in channels
                if not bool(channel["can_resume_model_chain"])
            ],
            "boundary_preserved": (
                not bool(self.current_work_item.get("writes_synthetic_as_field_claim", False))
                and self._formal_search_execution_boundary_preserved()
            ),
            "global_no_write_boundary": (
                "No channel may write actuator policy, release gate, patent/legal conclusion or field-supported "
                "claim until its downstream replay/holdout/human-review gates pass."
            ),
        }

    def _formal_search_linked_review_readiness_status(self) -> str:
        return str(
            self.formal_search_execution_route_plan.get(
                "linked_review_readiness_status",
                "formal_search_review_readiness_not_consumed_by_agent50",
            )
        )

    def _external_activation_router_status(self) -> str:
        return str(
            self.external_activation_router.get(
                "router_status",
                "external_activation_router_not_consumed_by_agent50",
            )
        )

    def _external_activation_router_consumed(self) -> bool:
        return self._external_activation_router_status() != "external_activation_router_not_consumed_by_agent50"

    def _external_activation_router_path_supplied_count(self) -> int:
        try:
            return int(self.external_activation_router.get("path_supplied_count", 0) or 0)
        except (TypeError, ValueError):
            return 0

    def _external_activation_router_route_ready_count(self) -> int:
        try:
            return int(self.external_activation_router.get("route_ready_count", 0) or 0)
        except (TypeError, ValueError):
            return 0

    def _external_activation_router_model_chain_ready_route_count(self) -> int:
        if "model_chain_ready_route_count" in self.external_activation_router:
            try:
                return int(self.external_activation_router.get("model_chain_ready_route_count", 0) or 0)
            except (TypeError, ValueError):
                return 0
        return len(self._external_activation_router_model_chain_ready_channel_ids())

    def _external_activation_router_handoff_ready_route_count(self) -> int:
        if "handoff_ready_route_count" in self.external_activation_router:
            try:
                return int(self.external_activation_router.get("handoff_ready_route_count", 0) or 0)
            except (TypeError, ValueError):
                return 0
        return len(self._external_activation_router_handoff_ready_channel_ids())

    def _external_activation_router_blocked_route_count(self) -> int:
        try:
            return int(self.external_activation_router.get("blocked_route_count", 0) or 0)
        except (TypeError, ValueError):
            return 0

    def _external_activation_router_boundary_preserved(self) -> bool:
        if not self._external_activation_router_consumed():
            return False
        return bool(self.external_activation_router.get("boundary_preserved", False))

    def _external_activation_router_no_write_boundary(self) -> str:
        return str(
            self.external_activation_router.get(
                "global_no_write_boundary",
                "Router not consumed; Agent50 cannot use router state as field/formal/legal evidence.",
            )
        )

    def _safe_int(self, value: object, default: int = 0) -> int:
        try:
            return int(value or default)
        except (TypeError, ValueError):
            return default

    def _external_activation_router_catalyst_patch_candidate_consumed(self) -> bool:
        return bool(
            self.external_activation_router.get(
                "catalyst_patch_candidate_consumed",
                False,
            )
        )

    def _external_activation_router_catalyst_patch_candidate_status(self) -> str:
        return str(
            self.external_activation_router.get(
                "catalyst_patch_candidate_status",
                "catalyst_patch_candidate_not_consumed_by_agent50",
            )
        )

    def _external_activation_router_catalyst_patch_candidate_materialized(self) -> bool:
        return bool(
            self.external_activation_router.get(
                "catalyst_patch_candidate_materialized",
                False,
            )
        )

    def _external_activation_router_catalyst_patch_candidate_preflight_status(self) -> str:
        return str(
            self.external_activation_router.get(
                "catalyst_patch_candidate_preflight_status",
                "not_consumed",
            )
        )

    def _external_activation_router_catalyst_patch_candidate_remaining_gap_count(self) -> int:
        return self._safe_int(
            self.external_activation_router.get(
                "catalyst_patch_candidate_remaining_gap_count",
                0,
            )
        )

    def _external_activation_router_catalyst_patch_candidate_can_submit_as_r7_dir(self) -> bool:
        return bool(
            self.external_activation_router.get(
                "catalyst_patch_candidate_can_submit_as_REAL_FIELD_REPLAY_PACKAGE_DIR",
                False,
            )
        )

    def _external_activation_router_catalyst_patch_candidate_package_dir(self) -> str:
        return str(
            self.external_activation_router.get(
                "catalyst_patch_candidate_package_dir",
                "",
            )
        )

    def _external_activation_router_field_activation_upstream_consumed(self) -> bool:
        return bool(
            self.external_activation_router.get(
                "field_activation_upstream_consumed",
                False,
            )
        )

    def _external_activation_router_field_activation_upstream_status(self) -> str:
        return str(
            self.external_activation_router.get(
                "field_activation_upstream_status",
                "field_activation_upstream_not_consumed_by_agent50",
            )
        )

    def _external_activation_router_field_activation_upstream_first_blocked_step(self) -> str:
        return str(
            self.external_activation_router.get(
                "field_activation_upstream_first_blocked_step",
                "",
            )
        )

    def _external_activation_router_field_activation_upstream_highest_priority_blocker(self) -> str:
        return str(
            self.external_activation_router.get(
                "field_activation_upstream_highest_priority_blocker",
                "",
            )
        )

    def _external_activation_router_field_activation_upstream_next_operator_action(self) -> str:
        return str(
            self.external_activation_router.get(
                "field_activation_upstream_next_operator_action",
                "",
            )
        )

    def _external_activation_router_field_activation_upstream_can_submit_to_external_activation_router(self) -> bool:
        return bool(
            self.external_activation_router.get(
                "field_activation_upstream_can_submit_to_external_activation_router",
                False,
            )
        )

    def _external_activation_router_field_activation_upstream_submission_packet_status(self) -> str:
        return str(
            self.external_activation_router.get(
                "field_activation_upstream_submission_packet_status",
                "field_activation_response_submission_packet_not_consumed_by_agent50",
            )
        )

    def _field_activation_matrix_readiness(self) -> dict[str, object]:
        readiness = self.field_activation_matrix_metrics.get("readiness", {})
        return readiness if isinstance(readiness, dict) else {}

    def _field_activation_matrix_interface_id(self) -> str:
        return str(
            self.field_activation_matrix_metrics.get(
                "interface_id",
                "FIELD_ACTIVATION_MATRIX_NOT_DEFINED",
            )
        )

    def _field_activation_matrix_status(self) -> str:
        return str(
            self._field_activation_matrix_readiness().get(
                "interface_status",
                "not_available",
            )
        )

    def _field_activation_matrix_hidden_state_row_count(self) -> int:
        try:
            return int(self._field_activation_matrix_readiness().get("hidden_state_row_count", 0) or 0)
        except (TypeError, ValueError):
            return 0

    def _field_activation_matrix_can_resume_model_chain(self) -> bool:
        return bool(self._field_activation_matrix_readiness().get("can_resume_model_chain", False))

    def _field_activation_matrix_can_write_to_actuator(self) -> bool:
        return bool(self._field_activation_matrix_readiness().get("can_write_to_actuator", False))

    def _field_activation_matrix_can_write_to_release_gate(self) -> bool:
        return bool(self._field_activation_matrix_readiness().get("can_write_to_release_gate", False))

    def _field_activation_matrix_no_write_boundary_complete(self) -> bool:
        try:
            return float(
                self._field_activation_matrix_readiness().get("no_write_boundary_completeness", 0.0)
                or 0.0
            ) >= 1.0
        except (TypeError, ValueError):
            return False

    def _field_activation_matrix_next_gate(self) -> str:
        return str(
            self._field_activation_matrix_readiness().get(
                "next_gate",
                "define_field_activation_matrix_before_external_collection",
            )
        )

    def _field_activation_response_source_preflight(self) -> dict[str, object]:
        preflight = self.field_activation_matrix_metrics.get("field_activation_response_source_preflight", {})
        return preflight if isinstance(preflight, dict) else {}

    def _field_activation_response_source_preflight_status(self) -> str:
        return str(
            self._field_activation_response_source_preflight().get(
                "source_preflight_status",
                "field_activation_response_source_preflight_not_available",
            )
        )

    def _field_activation_response_source_external_response_supplied(self) -> bool:
        return bool(
            self._field_activation_response_source_preflight().get(
                "external_response_supplied",
                False,
            )
        )

    def _field_activation_response_source_can_run_response_preflight(self) -> bool:
        return bool(
            self._field_activation_response_source_preflight().get(
                "can_run_response_preflight",
                False,
            )
        )

    def _field_activation_response_repair_work_order(self) -> dict[str, object]:
        work_order = self.field_activation_matrix_metrics.get("field_activation_response_repair_work_order", {})
        return work_order if isinstance(work_order, dict) else {}

    def _field_activation_response_repair_work_order_status(self) -> str:
        return str(
            self._field_activation_response_repair_work_order().get(
                "work_order_status",
                "field_activation_response_repair_work_order_not_available",
            )
        )

    def _field_activation_response_repair_item_count(self) -> int:
        try:
            return int(
                self._field_activation_response_repair_work_order().get(
                    "repair_item_count",
                    0,
                )
                or 0
            )
        except (TypeError, ValueError):
            return 0

    def _field_activation_response_repair_highest_priority_repair_id(self) -> str:
        return str(
            self._field_activation_response_repair_work_order().get(
                "highest_priority_repair_id",
                "",
            )
        )

    def _field_activation_response_preflight(self) -> dict[str, object]:
        preflight = self.field_activation_matrix_metrics.get("field_activation_response_preflight", {})
        return preflight if isinstance(preflight, dict) else {}

    def _field_activation_response_preflight_status(self) -> str:
        return str(
            self._field_activation_response_preflight().get(
                "preflight_status",
                "field_activation_response_preflight_not_available",
            )
        )

    def _field_activation_response_expected_row_count(self) -> int:
        try:
            return int(
                self._field_activation_response_preflight().get(
                    "expected_response_row_count",
                    0,
                )
                or 0
            )
        except (TypeError, ValueError):
            return 0

    def _field_activation_response_template_marker_row_count(self) -> int:
        try:
            return int(
                self._field_activation_response_preflight().get(
                    "template_marker_row_count",
                    0,
                )
                or 0
            )
        except (TypeError, ValueError):
            return 0

    def _field_activation_response_missing_value_payload_row_count(self) -> int:
        try:
            return int(
                self._field_activation_response_preflight().get(
                    "missing_value_payload_row_count",
                    0,
                )
                or 0
            )
        except (TypeError, ValueError):
            return 0

    def _field_activation_response_template_value_payload_row_count(self) -> int:
        try:
            return int(
                self._field_activation_response_preflight().get(
                    "template_value_payload_row_count",
                    0,
                )
                or 0
            )
        except (TypeError, ValueError):
            return 0

    def _field_activation_response_can_route_to_external_activation_router(self) -> bool:
        return bool(
            self._field_activation_response_preflight().get(
                "can_route_to_external_activation_router",
                False,
            )
        )

    def _field_activation_response_completion_ledger(self) -> dict[str, object]:
        ledger = self.field_activation_matrix_metrics.get(
            "field_activation_response_completion_ledger",
            {},
        )
        return ledger if isinstance(ledger, dict) else {}

    def _field_activation_response_completion_ledger_status(self) -> str:
        return str(
            self._field_activation_response_completion_ledger().get(
                "ledger_status",
                "field_activation_response_completion_ledger_not_available",
            )
        )

    def _field_activation_response_completion_ratio(self) -> float:
        try:
            return float(
                self._field_activation_response_completion_ledger().get("completion_ratio", 0.0)
                or 0.0
            )
        except (TypeError, ValueError):
            return 0.0

    def _field_activation_response_completed_row_count(self) -> int:
        try:
            return int(
                self._field_activation_response_completion_ledger().get(
                    "completed_response_row_count",
                    0,
                )
                or 0
            )
        except (TypeError, ValueError):
            return 0

    def _field_activation_response_incomplete_row_count(self) -> int:
        try:
            return int(
                self._field_activation_response_completion_ledger().get(
                    "incomplete_response_row_count",
                    0,
                )
                or 0
            )
        except (TypeError, ValueError):
            return 0

    def _field_activation_response_next_hidden_state_focus(self) -> str:
        return str(
            self._field_activation_response_completion_ledger().get(
                "next_hidden_state_focus",
                "",
            )
        )

    def _field_activation_response_completion_next_operator_action(self) -> str:
        return str(
            self._field_activation_response_completion_ledger().get(
                "next_operator_action",
                "inspect_field_activation_response_completion_ledger",
            )
        )

    def _field_activation_response_focus_handoff(self) -> dict[str, object]:
        handoff = self.field_activation_matrix_metrics.get("field_activation_response_focus_handoff", {})
        return handoff if isinstance(handoff, dict) else {}

    def _field_activation_response_focus_handoff_status(self) -> str:
        return str(
            self._field_activation_response_focus_handoff().get(
                "handoff_status",
                "field_activation_response_focus_handoff_not_available",
            )
        )

    def _field_activation_response_focus_handoff_ready(self) -> bool:
        return self._field_activation_response_focus_handoff_status() == (
            "field_activation_response_focus_handoff_ready_for_catalyst_activity"
        )

    def _field_activation_response_focus_handoff_target_hidden_state(self) -> str:
        return str(self._field_activation_response_focus_handoff().get("target_hidden_state", ""))

    def _field_activation_response_focus_handoff_row_scan_reduction_ratio(self) -> float:
        try:
            return float(
                self._field_activation_response_focus_handoff().get(
                    "row_scan_reduction_ratio",
                    0.0,
                )
                or 0.0
            )
        except (TypeError, ValueError):
            return 0.0

    def _field_activation_response_focus_handoff_next_operator_action(self) -> str:
        return str(
            self._field_activation_response_focus_handoff().get(
                "next_operator_action",
                "inspect_field_activation_response_focus_handoff",
            )
        )

    def _field_activation_response_focus_handoff_repair_work_order_status(self) -> str:
        return str(
            self._field_activation_response_focus_handoff().get(
                "focused_repair_work_order_status",
                "focused_catalyst_response_repair_work_order_not_available",
            )
        )

    def _field_activation_response_focus_handoff_repair_item_count(self) -> int:
        try:
            return int(
                self._field_activation_response_focus_handoff().get(
                    "focused_repair_item_count",
                    0,
                )
                or 0
            )
        except (TypeError, ValueError):
            return 0

    def _field_activation_response_focus_handoff_repair_next_operator_action(self) -> str:
        return str(self._field_activation_response_focus_handoff().get("focused_repair_next_operator_action", ""))

    def _field_activation_response_focus_handoff_source_env_var(self) -> str:
        return str(
            self._field_activation_response_focus_handoff().get(
                "focused_merge_source_env_var",
                "",
            )
        )

    def _field_activation_response_focus_handoff_can_submit_to_external_activation_router(self) -> bool:
        return bool(
            self._field_activation_response_focus_handoff().get(
                "can_submit_to_external_activation_router",
                False,
            )
        )

    def _field_activation_response_coherence_audit(self) -> dict[str, object]:
        audit = self.field_activation_matrix_metrics.get("field_activation_response_coherence_audit", {})
        return audit if isinstance(audit, dict) else {}

    def _field_activation_response_coherence_audit_status(self) -> str:
        return str(
            self._field_activation_response_coherence_audit().get(
                "audit_status",
                "field_activation_response_coherence_audit_not_available",
            )
        )

    def _field_activation_response_coherence_hard_blocker_count(self) -> int:
        try:
            return int(
                self._field_activation_response_coherence_audit().get("hard_blocker_count", 0)
                or 0
            )
        except (TypeError, ValueError):
            return 0

    def _field_activation_response_coherence_warning_count(self) -> int:
        try:
            return int(
                self._field_activation_response_coherence_audit().get("warning_count", 0)
                or 0
            )
        except (TypeError, ValueError):
            return 0

    def _field_activation_response_coherence_highest_priority_blocker(self) -> str:
        return str(
            self._field_activation_response_coherence_audit().get(
                "highest_priority_blocker",
                "",
            )
        )

    def _field_activation_response_coherence_can_route_to_package_assembly(self) -> bool:
        return bool(
            self._field_activation_response_coherence_audit().get(
                "can_route_to_package_assembly",
                False,
            )
        )

    def _field_activation_package_assembly_plan(self) -> dict[str, object]:
        plan = self.field_activation_matrix_metrics.get("field_activation_package_assembly_plan", {})
        return plan if isinstance(plan, dict) else {}

    def _field_activation_package_assembly_status(self) -> str:
        return str(
            self._field_activation_package_assembly_plan().get(
                "assembly_status",
                "field_activation_package_assembly_plan_not_available",
            )
        )

    def _field_activation_package_assembly_channel_plan_count(self) -> int:
        try:
            return int(
                self._field_activation_package_assembly_plan().get(
                    "channel_plan_count",
                    0,
                )
                or 0
            )
        except (TypeError, ValueError):
            return 0

    def _field_activation_package_assembly_candidate_channel_plan_count(self) -> int:
        try:
            return int(
                self._field_activation_package_assembly_plan().get(
                    "candidate_channel_plan_count",
                    0,
                )
                or 0
            )
        except (TypeError, ValueError):
            return 0

    def _field_activation_package_assembly_table_plan_count(self) -> int:
        try:
            return int(
                self._field_activation_package_assembly_plan().get(
                    "table_plan_count",
                    0,
                )
                or 0
            )
        except (TypeError, ValueError):
            return 0

    def _field_activation_package_assembly_can_stage_external_package_candidates(self) -> bool:
        return bool(
            self._field_activation_package_assembly_plan().get(
                "can_stage_external_package_candidates",
                False,
            )
        )

    def _field_activation_package_staging_manifest(self) -> dict[str, object]:
        manifest = self.field_activation_matrix_metrics.get("field_activation_package_staging_manifest", {})
        return manifest if isinstance(manifest, dict) else {}

    def _field_activation_package_staging_status(self) -> str:
        return str(
            self._field_activation_package_staging_manifest().get(
                "staging_status",
                "field_activation_package_staging_manifest_not_available",
            )
        )

    def _field_activation_package_staging_selected_channel_manifest_count(self) -> int:
        try:
            return int(
                self._field_activation_package_staging_manifest().get(
                    "selected_channel_manifest_count",
                    0,
                )
                or 0
            )
        except (TypeError, ValueError):
            return 0

    def _field_activation_package_staging_selected_row_blueprint_count(self) -> int:
        try:
            return int(
                self._field_activation_package_staging_manifest().get(
                    "selected_row_blueprint_count",
                    0,
                )
                or 0
            )
        except (TypeError, ValueError):
            return 0

    def _field_activation_package_staging_selected_value_payload_mapping_count(self) -> int:
        try:
            return int(
                self._field_activation_package_staging_manifest().get(
                    "selected_value_payload_mapping_count",
                    0,
                )
                or 0
            )
        except (TypeError, ValueError):
            return 0

    def _field_activation_package_staging_candidate_channel_requirement_count(self) -> int:
        try:
            return int(
                self._field_activation_package_staging_manifest().get(
                    "candidate_channel_requirement_count",
                    0,
                )
                or 0
            )
        except (TypeError, ValueError):
            return 0

    def _field_activation_package_staging_can_materialize_no_write_package_candidates(self) -> bool:
        return bool(
            self._field_activation_package_staging_manifest().get(
                "can_materialize_no_write_package_candidates",
                False,
            )
        )

    def _field_activation_package_staging_next_operator_action(self) -> str:
        return str(
            self._field_activation_package_staging_manifest().get(
                "next_operator_action",
                "complete_response_preflight_and_package_assembly_before_staging",
            )
        )

    def _field_activation_materialized_package_preflight(self) -> dict[str, object]:
        preflight = self.field_activation_matrix_metrics.get(
            "field_activation_materialized_package_preflight",
            {},
        )
        return preflight if isinstance(preflight, dict) else {}

    def _field_activation_materialized_package_preflight_status(self) -> str:
        return str(
            self._field_activation_materialized_package_preflight().get(
                "preflight_status",
                "field_activation_materialized_package_preflight_not_available",
            )
        )

    def _field_activation_materialized_package_preflight_blocker_count(self) -> int:
        try:
            return int(
                self._field_activation_materialized_package_preflight().get(
                    "blocker_count",
                    0,
                )
                or 0
            )
        except (TypeError, ValueError):
            return 0

    def _field_activation_materialized_package_blueprint_missing_row_count(self) -> int:
        try:
            return int(
                self._field_activation_materialized_package_preflight().get(
                    "blueprint_missing_row_count",
                    0,
                )
                or 0
            )
        except (TypeError, ValueError):
            return 0

    def _field_activation_materialized_package_preflight_highest_priority_blocker(self) -> str:
        return str(
            self._field_activation_materialized_package_preflight().get(
                "highest_priority_blocker",
                "",
            )
        )

    def _field_activation_materialized_package_preflight_can_route_to_external_activation_router(
        self,
    ) -> bool:
        return bool(
            self._field_activation_materialized_package_preflight().get(
                "can_route_to_external_activation_router",
                False,
            )
        )

    def _field_activation_materialized_package_preflight_next_operator_action(self) -> str:
        return str(
            self._field_activation_materialized_package_preflight().get(
                "next_operator_action",
                "complete_field_activation_staging_manifest_before_materializing_package",
            )
        )

    def _field_activation_downstream_r7_preview(self) -> dict[str, object]:
        preview = self.field_activation_matrix_metrics.get(
            "field_activation_downstream_r7_preview",
            {},
        )
        return preview if isinstance(preview, dict) else {}

    def _field_activation_downstream_r7_preview_status(self) -> str:
        return str(
            self._field_activation_downstream_r7_preview().get(
                "preview_status",
                "field_activation_downstream_r7_preview_not_available",
            )
        )

    def _field_activation_downstream_r7_preview_executed(self) -> bool:
        return bool(self._field_activation_downstream_r7_preview().get("preview_executed", False))

    def _field_activation_downstream_r7_preview_metric_evaluation_status(self) -> str:
        return str(
            self._field_activation_downstream_r7_preview().get(
                "preview_metric_evaluation_status",
                "downstream_preview_metrics_not_evaluated",
            )
        )

    def _field_activation_downstream_r7_not_evaluated_metric_count(self) -> int:
        names = self._field_activation_downstream_r7_preview().get("not_evaluated_metric_names", [])
        return len(names) if isinstance(names, list) else 0

    def _field_activation_downstream_r7_agent44_import_status(self) -> str:
        return str(
            self._field_activation_downstream_r7_preview().get(
                "r7_agent44_import_status",
                "agent44_import_not_run",
            )
        )

    def _field_activation_downstream_r7_can_pass_to_timestamped_replay(self) -> bool:
        return bool(
            self._field_activation_downstream_r7_preview().get(
                "downstream_r7_can_pass_to_timestamped_replay",
                False,
            )
        )

    def _field_activation_downstream_r7_highest_priority_blocker(self) -> str:
        return str(self._field_activation_downstream_r7_preview().get("highest_priority_blocker", ""))

    def _field_activation_downstream_r7_next_operator_action(self) -> str:
        return str(
            self._field_activation_downstream_r7_preview().get(
                "next_operator_action",
                "complete_materialized_package_preflight_before_r7_preview",
            )
        )

    def _field_activation_downstream_path_endpoint_preview(self) -> dict[str, object]:
        preview = self.field_activation_matrix_metrics.get(
            "field_activation_downstream_path_endpoint_preview",
            {},
        )
        return preview if isinstance(preview, dict) else {}

    def _field_activation_downstream_path_endpoint_preview_status(self) -> str:
        return str(
            self._field_activation_downstream_path_endpoint_preview().get(
                "preview_status",
                "field_activation_downstream_path_endpoint_preview_not_available",
            )
        )

    def _field_activation_downstream_path_endpoint_preview_executed(self) -> bool:
        return bool(self._field_activation_downstream_path_endpoint_preview().get("preview_executed", False))

    def _field_activation_downstream_path_endpoint_preview_metric_evaluation_status(self) -> str:
        return str(
            self._field_activation_downstream_path_endpoint_preview().get(
                "preview_metric_evaluation_status",
                "downstream_preview_metrics_not_evaluated",
            )
        )

    def _field_activation_downstream_path_endpoint_not_evaluated_metric_count(self) -> int:
        names = self._field_activation_downstream_path_endpoint_preview().get(
            "not_evaluated_metric_names",
            [],
        )
        return len(names) if isinstance(names, list) else 0

    def _field_activation_downstream_path_endpoint_preflight_status(self) -> str:
        return str(
            self._field_activation_downstream_path_endpoint_preview().get(
                "path_endpoint_preflight_status",
                "path_endpoint_preflight_not_run",
            )
        )

    def _field_activation_downstream_path_endpoint_required_table_count(self) -> int:
        try:
            return int(
                self._field_activation_downstream_path_endpoint_preview().get(
                    "path_endpoint_required_table_count",
                    0,
                )
                or 0
            )
        except (TypeError, ValueError):
            return 0

    def _field_activation_downstream_path_endpoint_contract_minimum_matched_batch_count(self) -> int:
        try:
            return int(
                self._field_activation_downstream_path_endpoint_preview().get(
                    "path_endpoint_contract_minimum_matched_batch_count",
                    0,
                )
                or 0
            )
        except (TypeError, ValueError):
            return 0

    def _field_activation_downstream_path_endpoint_matched_batch_count(self) -> int:
        try:
            return int(
                self._field_activation_downstream_path_endpoint_preview().get(
                    "path_endpoint_matched_batch_count",
                    0,
                )
                or 0
            )
        except (TypeError, ValueError):
            return 0

    def _field_activation_downstream_path_endpoint_required_matched_batch_deficit(self) -> int:
        try:
            return int(
                self._field_activation_downstream_path_endpoint_preview().get(
                    "path_endpoint_required_matched_batch_deficit",
                    0,
                )
                or 0
            )
        except (TypeError, ValueError):
            return 0

    def _field_activation_downstream_path_endpoint_can_route_to_field_layout_holdout(self) -> bool:
        return bool(
            self._field_activation_downstream_path_endpoint_preview().get(
                "downstream_path_endpoint_can_route_to_field_layout_holdout",
                False,
            )
        )

    def _field_activation_downstream_path_endpoint_highest_priority_blocker(self) -> str:
        return str(
            self._field_activation_downstream_path_endpoint_preview().get(
                "highest_priority_blocker",
                "",
            )
        )

    def _field_activation_downstream_path_endpoint_next_operator_action(self) -> str:
        return str(
            self._field_activation_downstream_path_endpoint_preview().get(
                "next_operator_action",
                "complete_materialized_package_preflight_before_path_endpoint_preview",
            )
        )

    def _field_activation_external_readiness_gate(self) -> dict[str, object]:
        gate = self.field_activation_matrix_metrics.get("field_activation_external_readiness_gate", {})
        return gate if isinstance(gate, dict) else {}

    def _field_activation_external_readiness_gate_available(self) -> bool:
        return self._field_activation_external_readiness_gate_status() != (
            "field_activation_external_readiness_gate_not_available"
        )

    def _field_activation_external_readiness_gate_status(self) -> str:
        return str(
            self._field_activation_external_readiness_gate().get(
                "gate_status",
                "field_activation_external_readiness_gate_not_available",
            )
        )

    def _field_activation_external_readiness_first_blocked_step(self) -> str:
        return str(self._field_activation_external_readiness_gate().get("first_blocked_step", ""))

    def _field_activation_external_readiness_highest_priority_blocker(self) -> str:
        return str(self._field_activation_external_readiness_gate().get("highest_priority_blocker", ""))

    def _field_activation_external_readiness_next_operator_action(self) -> str:
        return str(
            self._field_activation_external_readiness_gate().get(
                "next_operator_action",
                "inspect_field_activation_external_readiness_gate",
            )
        )

    def _field_activation_external_readiness_can_submit_to_external_activation_router(self) -> bool:
        return bool(
            self._field_activation_external_readiness_gate().get(
                "can_submit_to_external_activation_router",
                False,
            )
        )

    def _field_activation_response_submission_packet(self) -> dict[str, object]:
        packet = self.field_activation_matrix_metrics.get(
            "field_activation_response_submission_packet",
            {},
        )
        return packet if isinstance(packet, dict) else {}

    def _field_activation_response_submission_packet_available(self) -> bool:
        return self._field_activation_response_submission_packet_status() != (
            "field_activation_response_submission_packet_not_available"
        )

    def _field_activation_response_submission_packet_status(self) -> str:
        return str(
            self._field_activation_response_submission_packet().get(
                "packet_status",
                "field_activation_response_submission_packet_not_available",
            )
        )

    def _field_activation_response_submission_packet_next_operator_action(self) -> str:
        return str(
            self._field_activation_response_submission_packet().get(
                "next_operator_action",
                "inspect_field_activation_response_submission_packet",
            )
        )

    def _field_activation_response_submission_packet_highest_priority_blocker(self) -> str:
        return str(
            self._field_activation_response_submission_packet().get(
                "highest_priority_blocker",
                "",
            )
        )

    def _field_activation_response_submission_packet_can_route_to_external_activation_router(self) -> bool:
        return bool(
            self._field_activation_response_submission_packet().get(
                "can_route_to_external_activation_router",
                False,
            )
        )

    def _field_activation_schema_preflight(self) -> dict[str, object]:
        preflight = self.field_activation_matrix_metrics.get("field_activation_schema_preflight", {})
        return preflight if isinstance(preflight, dict) else {}

    def _field_activation_schema_preflight_status(self) -> str:
        return str(
            self._field_activation_schema_preflight().get(
                "schema_preflight_status",
                "field_activation_schema_preflight_not_available",
            )
        )

    def _field_activation_schema_can_validate_response_structure(self) -> bool:
        return bool(
            self._field_activation_schema_preflight().get(
                "can_validate_field_activation_response_structure",
                False,
            )
        )

    def _field_activation_schema_can_resume_model_chain(self) -> bool:
        return bool(
            self._field_activation_schema_preflight().get(
                "can_resume_model_chain",
                False,
            )
        )

    def _field_activation_schema_can_write_to_actuator(self) -> bool:
        return bool(
            self._field_activation_schema_preflight().get(
                "can_write_to_actuator",
                False,
            )
        )

    def _field_activation_schema_can_write_to_release_gate(self) -> bool:
        return bool(
            self._field_activation_schema_preflight().get(
                "can_write_to_release_gate",
                False,
            )
        )

    def _external_activation_router_route_rows(self) -> list[dict[str, object]]:
        rows = self.external_activation_router.get("route_rows", [])
        return [row for row in rows if isinstance(row, dict)] if isinstance(rows, list) else []

    def _external_activation_router_route_summary(self) -> list[dict[str, object]]:
        summaries: list[dict[str, object]] = []
        for row in self._external_activation_router_route_rows():
            summary: dict[str, object] = {
                "channel_id": str(row.get("channel_id", "unknown_channel")),
                "route_status": str(row.get("route_status", "unknown_route_status")),
                "path_supplied": bool(row.get("path_supplied", False)),
                "route_ready": bool(row.get("route_ready", False)),
                "can_resume_model_chain": bool(row.get("can_resume_model_chain", False)),
                "blocked_reason": str(row.get("blocked_reason", "")),
                "operator_action": str(row.get("operator_action", "")),
                "preflight_status": self._external_activation_router_preflight_status(row),
            }
            catalyst_candidate = row.get("catalyst_slice_r7_patch_candidate", {})
            if isinstance(catalyst_candidate, dict) and catalyst_candidate:
                summary.update(
                    {
                        "catalyst_patch_candidate_status": str(
                            catalyst_candidate.get("patch_status", "")
                        ),
                        "catalyst_patch_candidate_can_submit_as_REAL_FIELD_REPLAY_PACKAGE_DIR": bool(
                            catalyst_candidate.get(
                                "can_submit_candidate_as_REAL_FIELD_REPLAY_PACKAGE_DIR",
                                False,
                            )
                        ),
                        "catalyst_patch_candidate_remaining_gap_count": self._safe_int(
                            catalyst_candidate.get("remaining_gap_count", 0)
                        ),
                        "catalyst_patch_candidate_package_dir": str(
                            catalyst_candidate.get("candidate_package_dir", "")
                        ),
                    }
                )
            field_activation_upstream = row.get("field_activation_upstream_gate", {})
            if isinstance(field_activation_upstream, dict) and field_activation_upstream:
                summary.update(
                    {
                        "field_activation_upstream_status": str(
                            field_activation_upstream.get("status", "")
                        ),
                        "field_activation_upstream_first_blocked_step": str(
                            field_activation_upstream.get("first_blocked_step", "")
                        ),
                        "field_activation_upstream_highest_priority_blocker": str(
                            field_activation_upstream.get("highest_priority_blocker", "")
                        ),
                        "field_activation_upstream_next_operator_action": str(
                            field_activation_upstream.get("next_operator_action", "")
                        ),
                        "field_activation_upstream_can_submit_to_external_activation_router": bool(
                            field_activation_upstream.get(
                                "can_submit_to_external_activation_router",
                                False,
                            )
                        ),
                    }
                )
            summaries.append(summary)
        return summaries

    def _external_activation_router_ready_channel_ids(self) -> list[str]:
        ready_ids = self.external_activation_router.get("ready_channel_ids")
        if isinstance(ready_ids, list):
            return [str(channel_id) for channel_id in ready_ids]
        return [
            str(row.get("channel_id", "unknown_channel"))
            for row in self._external_activation_router_route_rows()
            if bool(row.get("route_ready", False))
        ]

    def _external_activation_router_model_chain_ready_channel_ids(self) -> list[str]:
        ready_ids = self.external_activation_router.get("model_chain_ready_channel_ids")
        if isinstance(ready_ids, list):
            return [str(channel_id) for channel_id in ready_ids]
        return [
            str(row.get("channel_id", "unknown_channel"))
            for row in self._external_activation_router_route_rows()
            if bool(row.get("route_ready", False)) and bool(row.get("can_resume_model_chain", False))
        ]

    def _external_activation_router_handoff_ready_channel_ids(self) -> list[str]:
        ready_ids = self.external_activation_router.get("handoff_ready_channel_ids")
        if isinstance(ready_ids, list):
            return [str(channel_id) for channel_id in ready_ids]
        return [
            str(row.get("channel_id", "unknown_channel"))
            for row in self._external_activation_router_route_rows()
            if bool(row.get("route_ready", False)) and not bool(row.get("can_resume_model_chain", False))
        ]

    def _external_activation_router_blocked_channel_ids(self) -> list[str]:
        blocked_ids = self.external_activation_router.get("blocked_channel_ids")
        if isinstance(blocked_ids, list):
            return [str(channel_id) for channel_id in blocked_ids]
        return [
            str(row.get("channel_id", "unknown_channel"))
            for row in self._external_activation_router_route_rows()
            if not bool(row.get("route_ready", False))
        ]

    def _external_activation_router_highest_priority_blocker(self) -> str:
        if not self._external_activation_router_consumed():
            return "external_activation_router_not_consumed_by_agent50"
        if "highest_priority_blocker" in self.external_activation_router:
            return str(self.external_activation_router.get("highest_priority_blocker", ""))
        route = self._external_activation_router_priority_route()
        if not route:
            return "external_activation_router_no_route_rows"
        if bool(route.get("route_ready", False)):
            return ""
        channel_id = str(route.get("channel_id", "unknown_channel"))
        blocked_reason = str(route.get("blocked_reason", "") or route.get("route_status", "unknown_route_status"))
        preflight_status = self._external_activation_router_preflight_status(route)
        if preflight_status != "-":
            return f"{channel_id}:{blocked_reason}:{preflight_status}"
        return f"{channel_id}:{blocked_reason}"

    def _external_activation_router_next_operator_action(self) -> str:
        if not self._external_activation_router_consumed():
            return "run_experiments/run_external_activation_router.py_before_agent50_consumption"
        if "next_operator_action" in self.external_activation_router:
            return str(self.external_activation_router.get("next_operator_action", ""))
        route = self._external_activation_router_priority_route()
        if not route:
            return "submit_or_set_one_external_activation_package_path"
        action = str(row_action) if (row_action := route.get("operator_action")) else ""
        if action:
            return action
        command = str(route.get("command_preview", ""))
        if bool(route.get("route_ready", False)) and command:
            return command
        return "inspect_external_activation_router_route_summary"

    def _external_activation_router_priority_route(self) -> dict[str, object]:
        rows = self._external_activation_router_route_rows()
        supplied_blocked = [
            row for row in rows if bool(row.get("path_supplied", False)) and not bool(row.get("route_ready", False))
        ]
        if supplied_blocked:
            return supplied_blocked[0]
        ready_rows = [row for row in rows if bool(row.get("route_ready", False))]
        if ready_rows:
            return ready_rows[0]
        blocked_rows = [row for row in rows if not bool(row.get("route_ready", False))]
        return blocked_rows[0] if blocked_rows else {}

    def _external_activation_router_preflight_status(self, route_row: dict[str, object]) -> str:
        field_preflight = route_row.get("field_package_preflight")
        if isinstance(field_preflight, dict):
            return str(field_preflight.get("status", "field_package_preflight_unknown"))
        path_preflight = route_row.get("path_endpoint_preflight")
        if isinstance(path_preflight, dict):
            return str(path_preflight.get("preflight_status", "path_endpoint_preflight_unknown"))
        formal_row_preflight = route_row.get("formal_search_result_package_row_preflight")
        if isinstance(formal_row_preflight, dict):
            return str(
                formal_row_preflight.get(
                    "formal_search_result_package_row_preflight_status",
                    "formal_search_result_package_row_preflight_unknown",
                )
            )
        formal_source_preflight = route_row.get("formal_search_result_package_source_preflight")
        if isinstance(formal_source_preflight, dict):
            return str(
                formal_source_preflight.get(
                    "formal_search_result_package_source_status",
                    "formal_search_result_package_source_unknown",
                )
            )
        field_activation_upstream = route_row.get("field_activation_upstream_gate")
        if isinstance(field_activation_upstream, dict):
            return str(
                field_activation_upstream.get(
                    "status",
                    "field_activation_upstream_status_unknown",
                )
            )
        return "-"

    def _external_activation_operator_packet_status(self) -> str:
        if not self.external_activation_operator_action_packet:
            return "external_activation_operator_action_packet_not_consumed_by_agent50"
        return str(
            self.external_activation_operator_action_packet.get(
                "packet_status",
                "external_activation_operator_action_packet_status_unknown",
            )
        )

    def _external_activation_operator_packet_target_hidden_state(self) -> str:
        return str(self.external_activation_operator_action_packet.get("target_hidden_state", ""))

    def _external_activation_operator_packet_source_env_var(self) -> str:
        return str(self.external_activation_operator_action_packet.get("source_env_var", ""))

    def _external_activation_operator_packet_expected_focused_response_row_count(self) -> int:
        return self._safe_int(
            self.external_activation_operator_action_packet.get(
                "expected_focused_response_row_count",
                0,
            )
        )

    def _external_activation_operator_packet_next_operator_action(self) -> str:
        if not self.external_activation_operator_action_packet:
            return "run_experiments/run_external_activation_operator_packet.py_before_agent50_consumption"
        return str(
            self.external_activation_operator_action_packet.get(
                "packet_next_operator_action",
                "",
            )
        )

    def _external_activation_operator_packet_focused_candidate_availability_status(self) -> str:
        return str(
            self.external_activation_operator_action_packet.get(
                "focused_candidate_availability_status",
                "focused_candidate_availability_not_available",
            )
        )

    def _external_activation_operator_packet_focused_candidate_operator_packet_submit_ready(self) -> bool:
        return bool(
            self.external_activation_operator_action_packet.get(
                "focused_candidate_operator_packet_submit_ready",
                False,
            )
        )

    def _external_activation_operator_packet_boundary_pass(self) -> bool:
        return bool(
            self.external_activation_operator_action_packet.get(
                "operator_packet_boundary_pass",
                False,
            )
        )

    def _external_activation_operator_packet_can_resume_model_chain(self) -> bool:
        return bool(self.external_activation_operator_action_packet.get("can_resume_model_chain", False))

    def _external_activation_operator_packet_can_write_to_actuator(self) -> bool:
        return bool(self.external_activation_operator_action_packet.get("can_write_to_actuator", False))

    def _external_activation_operator_packet_can_write_to_release_gate(self) -> bool:
        return bool(self.external_activation_operator_action_packet.get("can_write_to_release_gate", False))

    def _external_activation_operator_packet_core_gate_fields(self) -> dict[str, object]:
        return {
            "external_activation_operator_action_packet_status": (
                self._external_activation_operator_packet_status()
            ),
            "external_activation_operator_action_packet_target_hidden_state": (
                self._external_activation_operator_packet_target_hidden_state()
            ),
            "external_activation_operator_action_packet_source_env_var": (
                self._external_activation_operator_packet_source_env_var()
            ),
            "external_activation_operator_action_packet_expected_focused_response_row_count": (
                self._external_activation_operator_packet_expected_focused_response_row_count()
            ),
            "external_activation_operator_action_packet_focused_candidate_availability_status": (
                self._external_activation_operator_packet_focused_candidate_availability_status()
            ),
            "external_activation_operator_action_packet_focused_candidate_operator_packet_submit_ready": (
                self._external_activation_operator_packet_focused_candidate_operator_packet_submit_ready()
            ),
            "external_activation_operator_action_packet_next_operator_action": (
                self._external_activation_operator_packet_next_operator_action()
            ),
            "external_activation_operator_action_packet_boundary_pass": (
                self._external_activation_operator_packet_boundary_pass()
            ),
            "external_activation_operator_action_packet_can_resume_model_chain": (
                self._external_activation_operator_packet_can_resume_model_chain()
            ),
            "external_activation_operator_action_packet_can_write_to_actuator": (
                self._external_activation_operator_packet_can_write_to_actuator()
            ),
            "external_activation_operator_action_packet_can_write_to_release_gate": (
                self._external_activation_operator_packet_can_write_to_release_gate()
            ),
        }

    def _field_evidence_wait_status(self) -> dict[str, object]:
        unified = self._unified_field_evidence_readiness()
        r7 = self._real_field_package_acceptance_readiness()
        return {
            "external_field_blocker_active": self._external_field_blocker_active(),
            "source_basis_detail_ready": self._source_basis_detail_ready(),
            "field_import_ready": self._field_import_ready(),
            "field_evidence_chain_ready": self._field_evidence_chain_ready(),
            "unified_field_evidence_gate_status": self._unified_field_evidence_status(),
            "real_field_package_acceptance_status": self._real_field_package_acceptance_status(),
            "r7_field_evidence_sufficiency_status": self._r7_field_evidence_sufficiency_status(),
            "r7_field_evidence_sufficiency_score": self._r7_field_evidence_sufficiency_score(),
            "r7_field_evidence_smoke_pass": self._r7_field_evidence_smoke_pass(),
            "r7_can_route_to_agent42_smoke_replay": bool(
                self._r7_pipeline_readiness().get("can_route_to_agent42_smoke_replay", False)
            ),
            "r7_can_route_to_field_holdout": bool(
                self._r7_pipeline_readiness().get("can_route_to_field_holdout", False)
            ),
            "r7_can_route_to_human_review_candidate": self._r7_can_route_to_human_review_candidate(),
            "r7_submission_readiness_status": self._r7_submission_readiness_status(),
            "r7_submission_highest_priority_blocker": self._r7_submission_highest_priority_blocker(),
            "r7_submission_next_operator_action": self._r7_submission_next_operator_action(),
            "r7_submission_blocking_stage_count": self._r7_submission_blocking_stage_count(),
            "r7_submission_repair_work_order_status": self._r7_submission_repair_work_order_status(),
            "r7_submission_repair_item_count": self._r7_submission_repair_item_count(),
            "r7_submission_repair_work_order_path": self._r7_submission_repair_work_order_path(),
            "r7_submission_repair_response_preflight_status": (
                self._r7_submission_repair_response_preflight_status()
            ),
            "r7_submission_repair_response_can_route_to_r7_preflight": (
                self._r7_submission_repair_response_can_route_to_r7_preflight()
            ),
            "r7_submission_repair_response_template_path": (
                self._r7_submission_repair_response_template_path()
            ),
            "r7_submission_repair_response_preflight_path": (
                self._r7_submission_repair_response_preflight_path()
            ),
            "r7_field_supported_claim_upgrade_ready": bool(
                self._r7_pipeline_readiness().get("field_supported_claim_upgrade_ready", False)
            ),
            "field_path_endpoint_label_preflight_status": self._field_path_endpoint_label_preflight_status(),
            "field_path_endpoint_required_tables": self._field_path_endpoint_required_tables(),
            "field_path_endpoint_missing_tables": self._field_path_endpoint_missing_tables(),
            "field_path_endpoint_matched_batch_count": self._field_path_endpoint_matched_batch_count(),
            "field_path_endpoint_required_matched_batch_deficit": (
                self._field_path_endpoint_required_matched_batch_deficit()
            ),
            "field_path_endpoint_batch_alignment_gap_count": self._field_path_endpoint_batch_alignment_gap_count(),
            "field_path_endpoint_alignment_patch_plan_status": (
                self._field_path_endpoint_alignment_patch_plan_status()
            ),
            "field_path_endpoint_alignment_patch_plan_item_count": (
                self._field_path_endpoint_alignment_patch_plan_item_count()
            ),
            "field_path_endpoint_label_package_ready": self._field_path_endpoint_label_package_ready(),
            "field_path_endpoint_final_effluent_label_ready": self._field_path_endpoint_final_effluent_label_ready(),
            "can_route_to_field_layout_holdout_with_path_labels": (
                self._can_route_to_field_layout_holdout_with_path_labels()
            ),
            "release_gate_endpoint_label_blocked": self._release_gate_endpoint_label_blocked(),
            "unified_field_import_pass": bool(unified.get("field_import_pass", False)),
            "r7_field_package_import_pass": bool(r7.get("field_package_import_pass", False)),
            "field_activation_external_readiness_gate_status": (
                self._field_activation_external_readiness_gate_status()
            ),
            "field_activation_external_readiness_first_blocked_step": (
                self._field_activation_external_readiness_first_blocked_step()
            ),
            "field_activation_external_readiness_highest_priority_blocker": (
                self._field_activation_external_readiness_highest_priority_blocker()
            ),
            "field_activation_external_readiness_next_operator_action": (
                self._field_activation_external_readiness_next_operator_action()
            ),
            "field_activation_external_readiness_can_submit_to_external_activation_router": (
                self._field_activation_external_readiness_can_submit_to_external_activation_router()
            ),
            "field_activation_response_submission_packet_status": (
                self._field_activation_response_submission_packet_status()
            ),
            "field_activation_response_submission_packet_next_operator_action": (
                self._field_activation_response_submission_packet_next_operator_action()
            ),
            "field_activation_response_submission_packet_can_route_to_external_activation_router": (
                self._field_activation_response_submission_packet_can_route_to_external_activation_router()
            ),
            "field_activation_response_completion_ledger_status": (
                self._field_activation_response_completion_ledger_status()
            ),
            "field_activation_response_completion_ratio": (
                self._field_activation_response_completion_ratio()
            ),
            "field_activation_response_next_hidden_state_focus": (
                self._field_activation_response_next_hidden_state_focus()
            ),
            "field_activation_response_completion_next_operator_action": (
                self._field_activation_response_completion_next_operator_action()
            ),
            "field_activation_response_focus_handoff_status": (
                self._field_activation_response_focus_handoff_status()
            ),
            "field_activation_response_focus_handoff_target_hidden_state": (
                self._field_activation_response_focus_handoff_target_hidden_state()
            ),
            "field_activation_response_focus_handoff_row_scan_reduction_ratio": (
                self._field_activation_response_focus_handoff_row_scan_reduction_ratio()
            ),
            "field_activation_response_focus_handoff_next_operator_action": (
                self._field_activation_response_focus_handoff_next_operator_action()
            ),
            "field_activation_response_focus_handoff_repair_work_order_status": (
                self._field_activation_response_focus_handoff_repair_work_order_status()
            ),
            "field_activation_response_focus_handoff_repair_item_count": (
                self._field_activation_response_focus_handoff_repair_item_count()
            ),
            "field_activation_response_focus_handoff_repair_next_operator_action": (
                self._field_activation_response_focus_handoff_repair_next_operator_action()
            ),
            "external_activation_operator_action_packet_status": (
                self._external_activation_operator_packet_status()
            ),
            "external_activation_operator_action_packet_target_hidden_state": (
                self._external_activation_operator_packet_target_hidden_state()
            ),
            "external_activation_operator_action_packet_source_env_var": (
                self._external_activation_operator_packet_source_env_var()
            ),
            "external_activation_operator_action_packet_expected_focused_response_row_count": (
                self._external_activation_operator_packet_expected_focused_response_row_count()
            ),
            "external_activation_operator_action_packet_focused_candidate_availability_status": (
                self._external_activation_operator_packet_focused_candidate_availability_status()
            ),
            "external_activation_operator_action_packet_focused_candidate_operator_packet_submit_ready": (
                self._external_activation_operator_packet_focused_candidate_operator_packet_submit_ready()
            ),
            "external_activation_operator_action_packet_next_operator_action": (
                self._external_activation_operator_packet_next_operator_action()
            ),
            "external_activation_operator_action_packet_boundary_pass": (
                self._external_activation_operator_packet_boundary_pass()
            ),
            "observation_response_bridge_status": self._observation_response_bridge_status(),
            "observation_response_bridge_target_hidden_state": (
                self._observation_response_bridge_target_hidden_state()
            ),
            "observation_response_bridge_response_row_count": (
                self._observation_response_bridge_response_row_count()
            ),
            "observation_response_bridge_required_role_coverage_rate": (
                self._observation_response_bridge_required_role_coverage_rate()
            ),
            "observation_response_bridge_can_route_to_agent51_field_proxy_holdout": (
                self._observation_response_bridge_can_route_to_agent51_field_proxy_holdout()
            ),
            "observation_response_bridge_can_relax_agent49_catalyst_uncertainty_block": (
                self._observation_response_bridge_can_relax_agent49_catalyst_uncertainty_block()
            ),
            "catalyst_evidence_response_gate_status": self._catalyst_evidence_response_gate_status(),
            "catalyst_evidence_response_gate_row_level_preflight_pass": (
                self._catalyst_evidence_response_gate_row_level_preflight_pass()
            ),
            "catalyst_evidence_response_gate_matched_batch_count": (
                self._catalyst_evidence_response_gate_matched_batch_count()
            ),
            "catalyst_evidence_response_gate_can_route_to_focused_materialized_package_preflight": (
                self._catalyst_evidence_response_gate_can_route_to_focused_materialized_package_preflight()
            ),
            "catalyst_evidence_response_gate_can_route_to_agent51_field_proxy_holdout": (
                self._catalyst_evidence_response_gate_can_route_to_agent51_field_proxy_holdout()
            ),
            "catalyst_response_submission_kit_status": self._catalyst_response_submission_kit_status(),
            "catalyst_response_submission_kit_target_response_row_count": (
                self._catalyst_response_submission_kit_target_response_row_count()
            ),
            "catalyst_response_submission_kit_focused_template_path": (
                self._catalyst_response_submission_kit_focused_template_path()
            ),
            "catalyst_response_submission_kit_can_route_to_agent51_field_proxy_holdout": (
                self._catalyst_response_submission_kit_can_route_to_agent51_field_proxy_holdout()
            ),
            "focused_catalyst_response_merge_status": self._focused_catalyst_response_merge_status(),
            "focused_catalyst_response_source_preflight_status": (
                self._focused_catalyst_response_source_preflight_status()
            ),
            "focused_catalyst_response_source_can_run_merge_preflight": (
                self._focused_catalyst_response_source_can_run_merge_preflight()
            ),
            "focused_catalyst_response_merge_row_preflight_pass": (
                self._focused_catalyst_response_merge_row_preflight_pass()
            ),
            "focused_catalyst_response_repair_work_order_status": (
                self._focused_catalyst_response_repair_work_order_status()
            ),
            "focused_catalyst_response_repair_item_count": self._focused_catalyst_response_repair_item_count(),
            "focused_catalyst_response_repair_highest_priority_repair_id": (
                self._focused_catalyst_response_repair_highest_priority_repair_id()
            ),
            "focused_catalyst_response_repair_next_operator_action": (
                self._focused_catalyst_response_repair_next_operator_action()
            ),
            "focused_catalyst_response_merge_can_emit_candidate": (
                self._focused_catalyst_response_merge_can_emit_candidate()
            ),
            "focused_catalyst_response_merge_can_submit_candidate_as_FIELD_ACTIVATION_RESPONSE_PATH": (
                self._focused_catalyst_response_merge_can_submit_candidate_as_FIELD_ACTIVATION_RESPONSE_PATH()
            ),
            "focused_catalyst_response_merge_candidate_availability_status": (
                self._focused_catalyst_response_merge_candidate_availability_status()
            ),
            "focused_catalyst_response_merge_candidate_preflight_submit_ready": (
                self._focused_catalyst_response_merge_candidate_preflight_submit_ready()
            ),
            "focused_catalyst_response_merge_candidate_self_declared_submit_ready": (
                self._focused_catalyst_response_merge_candidate_self_declared_submit_ready()
            ),
            "focused_catalyst_response_merge_candidate_submit_ready_semantics": (
                self._focused_catalyst_response_merge_candidate_submit_ready_semantics()
            ),
            "focused_catalyst_response_merge_can_route_to_agent51_field_proxy_holdout": (
                self._focused_catalyst_response_merge_can_route_to_agent51_field_proxy_holdout()
            ),
            "catalyst_field_package_slice_status": self._catalyst_field_package_slice_status(),
            "catalyst_field_package_slice_preflight_pass": (
                self._catalyst_field_package_slice_preflight_pass()
            ),
            "catalyst_field_package_slice_matched_batch_count": (
                self._catalyst_field_package_slice_matched_batch_count()
            ),
            "catalyst_field_package_slice_template_dir": self._catalyst_field_package_slice_template_dir(),
            "catalyst_field_package_slice_can_route_to_r7_field_package_patch_candidate": (
                self._catalyst_field_package_slice_can_route_to_r7_field_package_patch_candidate()
            ),
            "catalyst_field_package_slice_can_route_to_agent51_field_proxy_holdout": (
                self._catalyst_field_package_slice_can_route_to_agent51_field_proxy_holdout()
            ),
            "catalyst_slice_r7_patch_candidate_status": self._catalyst_slice_r7_patch_candidate_status(),
            "catalyst_slice_r7_patch_candidate_materialized": (
                self._catalyst_slice_r7_patch_candidate_materialized()
            ),
            "catalyst_slice_r7_patch_candidate_preflight_status": (
                self._catalyst_slice_r7_patch_candidate_preflight_status()
            ),
            "catalyst_slice_r7_patch_candidate_remaining_gap_count": (
                self._catalyst_slice_r7_patch_candidate_remaining_gap_count()
            ),
            "catalyst_slice_r7_patch_candidate_can_submit_as_REAL_FIELD_REPLAY_PACKAGE_DIR": (
                self._catalyst_slice_r7_patch_candidate_can_submit_as_REAL_FIELD_REPLAY_PACKAGE_DIR()
            ),
            "next_internal_refactor_hint": self._next_internal_refactor_hint(),
        }

    def _next_internal_refactor_hint(self) -> dict[str, object]:
        for source in (
            self.unified_field_evidence_gate_metrics,
            self.observation_contract_metrics,
            self.control_replay_stress_metrics,
        ):
            action = source.get("next_refactor_action", {}) if isinstance(source, dict) else {}
            if isinstance(action, dict) and action.get("action_id"):
                return {
                    "action_id": action.get("action_id"),
                    "title": action.get("title", ""),
                    "reason": action.get("reason", ""),
                    "must_not_do": action.get("must_not_do", ""),
                }
        return {}

    def _observation_contract_status(self) -> str:
        return str(self._observation_contract_readiness().get("observation_contract_status", "not_available"))

    def _observation_contract_weak_state_coverage(self) -> float:
        return float(self._observation_contract_readiness().get("proxy_enhanced_weak_state_coverage", 0.0))

    def _observation_contract_missingness_after_patch(self) -> float:
        return float(self._observation_contract_readiness().get("missingness_robustness_after_patch", 0.0))

    def _observation_contract_baseline_ready(self) -> bool:
        readiness = self._observation_contract_readiness()
        if not readiness:
            return False
        return (
            bool(readiness.get("can_update_agent48_design_prior", False))
            and bool(readiness.get("can_update_agent54_observation_contract", False))
            and str(readiness.get("observation_contract_status", "")).startswith("synthetic_observation_contract_ready")
            and self._observation_contract_weak_state_coverage() >= 0.55
        )

    def _observation_response_bridge_status(self) -> str:
        return str(
            self.observation_response_bridge_metrics.get(
                "bridge_status",
                "observation_response_bridge_not_available",
            )
        )

    def _observation_response_bridge_target_hidden_state(self) -> str:
        return str(
            self.observation_response_bridge_metrics.get(
                "primary_target_hidden_state",
                "",
            )
        )

    def _observation_response_bridge_response_row_count(self) -> int:
        try:
            return int(self.observation_response_bridge_metrics.get("response_row_count", 0) or 0)
        except (TypeError, ValueError):
            return 0

    def _observation_response_bridge_required_role_coverage_rate(self) -> float:
        try:
            return float(
                self.observation_response_bridge_metrics.get(
                    "required_role_coverage_rate",
                    0.0,
                )
                or 0.0
            )
        except (TypeError, ValueError):
            return 0.0

    def _observation_response_bridge_can_route_to_agent51_field_proxy_holdout(self) -> bool:
        return bool(
            self.observation_response_bridge_metrics.get(
                "can_route_to_agent51_field_proxy_holdout",
                False,
            )
        )

    def _observation_response_bridge_can_relax_agent49_catalyst_uncertainty_block(self) -> bool:
        return bool(
            self.observation_response_bridge_metrics.get(
                "can_relax_agent49_catalyst_uncertainty_block",
                False,
            )
        )

    def _catalyst_evidence_response_gate_status(self) -> str:
        return str(
            self.catalyst_evidence_response_gate_metrics.get(
                "gate_status",
                "catalyst_evidence_response_gate_not_available",
            )
        )

    def _catalyst_evidence_response_gate_target_response_row_count(self) -> int:
        try:
            return int(self.catalyst_evidence_response_gate_metrics.get("target_response_row_count", 0) or 0)
        except (TypeError, ValueError):
            return 0

    def _catalyst_evidence_response_gate_row_level_preflight_pass(self) -> bool:
        return bool(self.catalyst_evidence_response_gate_metrics.get("row_level_preflight_pass", False))

    def _catalyst_evidence_response_gate_matched_batch_count(self) -> int:
        batch_alignment = self.catalyst_evidence_response_gate_metrics.get("batch_alignment", {})
        if not isinstance(batch_alignment, dict):
            return 0
        try:
            return int(batch_alignment.get("matched_batch_count", 0) or 0)
        except (TypeError, ValueError):
            return 0

    def _catalyst_evidence_response_gate_matched_batch_requirement_pass(self) -> bool:
        batch_alignment = self.catalyst_evidence_response_gate_metrics.get("batch_alignment", {})
        if not isinstance(batch_alignment, dict):
            return False
        return bool(batch_alignment.get("matched_batch_requirement_pass", False))

    def _catalyst_evidence_response_gate_can_route_to_focused_materialized_package_preflight(self) -> bool:
        return bool(
            self.catalyst_evidence_response_gate_metrics.get(
                "can_route_to_focused_materialized_package_preflight",
                False,
            )
        )

    def _catalyst_evidence_response_gate_can_route_to_agent51_field_proxy_holdout(self) -> bool:
        return bool(
            self.catalyst_evidence_response_gate_metrics.get(
                "can_route_to_agent51_field_proxy_holdout",
                False,
            )
        )

    def _catalyst_response_submission_kit_status(self) -> str:
        return str(
            self.catalyst_response_submission_kit_metrics.get(
                "kit_status",
                "catalyst_response_submission_kit_not_available",
            )
        )

    def _catalyst_response_submission_kit_target_response_row_count(self) -> int:
        try:
            return int(self.catalyst_response_submission_kit_metrics.get("target_response_row_count", 0) or 0)
        except (TypeError, ValueError):
            return 0

    def _catalyst_response_submission_kit_focused_template_path(self) -> str:
        return str(self.catalyst_response_submission_kit_metrics.get("focused_response_template_path", ""))

    def _catalyst_response_submission_kit_can_route_to_agent51_field_proxy_holdout(self) -> bool:
        return bool(
            self.catalyst_response_submission_kit_metrics.get(
                "can_route_to_agent51_field_proxy_holdout",
                False,
            )
        )

    def _focused_catalyst_response_merge_status(self) -> str:
        return str(
            self.focused_catalyst_response_merge_metrics.get(
                "preflight_status",
                "focused_catalyst_response_merge_not_available",
            )
        )

    def _focused_catalyst_response_source_preflight_status(self) -> str:
        return str(
            self.focused_catalyst_response_merge_metrics.get(
                "source_preflight_status",
                "focused_catalyst_response_source_preflight_not_available",
            )
        )

    def _focused_catalyst_response_source_can_run_merge_preflight(self) -> bool:
        return bool(
            self.focused_catalyst_response_merge_metrics.get(
                "source_can_run_merge_preflight",
                False,
            )
        )

    def _focused_catalyst_response_merge_row_preflight_pass(self) -> bool:
        return bool(self.focused_catalyst_response_merge_metrics.get("row_preflight_pass", False))

    def _focused_catalyst_response_repair_work_order(self) -> dict[str, object]:
        work_order = self.focused_catalyst_response_merge_metrics.get(
            "focused_catalyst_response_repair_work_order",
            {},
        )
        return work_order if isinstance(work_order, dict) else {}

    def _focused_catalyst_response_repair_work_order_status(self) -> str:
        return str(
            self._focused_catalyst_response_repair_work_order().get(
                "work_order_status",
                "focused_catalyst_response_repair_work_order_not_available",
            )
        )

    def _focused_catalyst_response_repair_item_count(self) -> int:
        try:
            return int(self._focused_catalyst_response_repair_work_order().get("repair_item_count", 0) or 0)
        except (TypeError, ValueError):
            return 0

    def _focused_catalyst_response_repair_highest_priority_repair_id(self) -> str:
        return str(self._focused_catalyst_response_repair_work_order().get("highest_priority_repair_id", ""))

    def _focused_catalyst_response_repair_next_operator_action(self) -> str:
        return str(self._focused_catalyst_response_repair_work_order().get("next_operator_action", ""))

    def _focused_catalyst_response_merge_can_emit_candidate(self) -> bool:
        return bool(
            self.focused_catalyst_response_merge_metrics.get(
                "can_emit_merged_full_response_candidate",
                False,
            )
        )

    def _focused_catalyst_response_merge_can_submit_candidate_as_FIELD_ACTIVATION_RESPONSE_PATH(self) -> bool:
        return bool(
            self.focused_catalyst_response_merge_metrics.get(
                "can_submit_candidate_as_FIELD_ACTIVATION_RESPONSE_PATH",
                False,
            )
        )

    def _focused_catalyst_response_merge_candidate_availability_status(self) -> str:
        return str(
            self.focused_catalyst_response_merge_metrics.get(
                "merged_full_response_candidate_availability_status",
                "candidate_availability_not_available",
            )
        )

    def _focused_catalyst_response_merge_candidate_self_declared_submit_ready(self) -> bool:
        return bool(
            self.focused_catalyst_response_merge_metrics.get(
                "merged_full_response_candidate_self_declared_submit_ready",
                False,
            )
        )

    def _focused_catalyst_response_merge_candidate_preflight_submit_ready(self) -> bool:
        return bool(
            self.focused_catalyst_response_merge_metrics.get(
                "merged_full_response_candidate_preflight_submit_ready",
                self.focused_catalyst_response_merge_metrics.get(
                    "can_submit_candidate_as_FIELD_ACTIVATION_RESPONSE_PATH",
                    False,
                ),
            )
        )

    def _focused_catalyst_response_merge_candidate_submit_ready_semantics(self) -> str:
        return str(
            self.focused_catalyst_response_merge_metrics.get(
                "merged_full_response_candidate_submit_ready_semantics",
                "focused_candidate_preflight_submit_ready_semantics_not_available",
            )
        )

    def _focused_catalyst_response_merge_can_route_to_agent51_field_proxy_holdout(self) -> bool:
        return bool(
            self.focused_catalyst_response_merge_metrics.get(
                "can_route_to_agent51_field_proxy_holdout",
                False,
            )
        )

    def _catalyst_field_package_slice_status(self) -> str:
        return str(
            self.catalyst_field_package_slice_metrics.get(
                "slice_status",
                "catalyst_field_package_slice_not_available",
            )
        )

    def _catalyst_field_package_slice_preflight_pass(self) -> bool:
        return bool(self.catalyst_field_package_slice_metrics.get("slice_preflight_pass", False))

    def _catalyst_field_package_slice_matched_batch_count(self) -> int:
        try:
            return int(self.catalyst_field_package_slice_metrics.get("matched_batch_count", 0) or 0)
        except (TypeError, ValueError):
            return 0

    def _catalyst_field_package_slice_template_dir(self) -> str:
        return str(self.catalyst_field_package_slice_metrics.get("focused_field_package_slice_template_dir", ""))

    def _catalyst_field_package_slice_can_route_to_r7_field_package_patch_candidate(self) -> bool:
        return bool(
            self.catalyst_field_package_slice_metrics.get(
                "can_route_to_r7_field_package_patch_candidate",
                False,
            )
        )

    def _catalyst_field_package_slice_can_route_to_agent51_field_proxy_holdout(self) -> bool:
        return bool(
            self.catalyst_field_package_slice_metrics.get(
                "can_route_to_agent51_field_proxy_holdout",
                False,
            )
        )

    def _catalyst_slice_r7_patch_candidate_status(self) -> str:
        return str(
            self.catalyst_slice_r7_patch_candidate_metrics.get(
                "patch_status",
                "catalyst_slice_r7_patch_candidate_not_available",
            )
        )

    def _catalyst_slice_r7_patch_candidate_materialized(self) -> bool:
        return bool(self.catalyst_slice_r7_patch_candidate_metrics.get("candidate_materialized", False))

    def _catalyst_slice_r7_patch_candidate_preflight_status(self) -> str:
        return str(self.catalyst_slice_r7_patch_candidate_metrics.get("candidate_preflight_status", "not_run"))

    def _catalyst_slice_r7_patch_candidate_remaining_gap_count(self) -> int:
        gap = self.catalyst_slice_r7_patch_candidate_metrics.get("full_package_gap_summary", {})
        if not isinstance(gap, dict):
            return 0
        try:
            return int(gap.get("remaining_gap_count", 0) or 0)
        except (TypeError, ValueError):
            return 0

    def _catalyst_slice_r7_patch_candidate_can_submit_as_REAL_FIELD_REPLAY_PACKAGE_DIR(self) -> bool:
        return bool(
            self.catalyst_slice_r7_patch_candidate_metrics.get(
                "can_submit_candidate_as_REAL_FIELD_REPLAY_PACKAGE_DIR",
                False,
            )
        )

    def _control_replay_stress_status(self) -> str:
        return str(self._control_replay_stress_readiness().get("control_replay_stress_status", "not_available"))

    def _control_replay_stress_baseline_ready(self) -> bool:
        readiness = self._control_replay_stress_readiness()
        if not readiness:
            return False
        return (
            bool(readiness.get("stress_ready", False))
            and bool(readiness.get("can_update_agent49_reward_prior", False))
            and str(readiness.get("control_replay_stress_status", "")).startswith("synthetic_counterfactual_stress_ready")
        )

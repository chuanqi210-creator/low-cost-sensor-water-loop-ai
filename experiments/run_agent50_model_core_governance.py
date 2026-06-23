from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from water_ai.agents.model_core_optimization_governance_agent import ModelCoreOptimizationGovernanceAgent
from water_ai.core_interface_consolidation import (
    build_core_interface_consolidation,
    core_interface_consolidation_report_md,
)
from water_ai.external_package_readiness_board import (
    attach_submission_readiness_gap,
    build_external_package_acquisition_maturity_gate,
    build_external_package_operator_action_packet,
    build_external_package_readiness_board,
    external_package_acquisition_maturity_gate_report_md,
    external_package_operator_action_packet_report_md,
    external_package_readiness_board_report_md,
)
from water_ai.new_core_interface_candidate_gate import (
    build_new_core_interface_candidate_gate,
    new_core_interface_candidate_gate_report_md,
)
from water_ai.stage_boundary_external_action_board import (
    build_stage_boundary_external_action_board,
    stage_boundary_external_action_board_report_md,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = PROJECT_ROOT / "deliverables" / "manifest.json"
SPARSE_METRICS_PATH = PROJECT_ROOT / "outputs" / "sensor_network_sparse_placement" / "sparse_placement_metrics.json"
COLLAB_METRICS_PATH = PROJECT_ROOT / "outputs" / "multi_facility_collaborative_control" / "collaborative_control_metrics.json"
CATALYST_PROXY_METRICS_PATH = PROJECT_ROOT / "outputs" / "catalyst_activity_proxy" / "catalyst_activity_proxy_metrics.json"
REPLAY_EVALUATION_METRICS_PATH = PROJECT_ROOT / "outputs" / "multi_facility_replay_evaluation" / "replay_evaluation_metrics.json"
GREY_BOX_PHYSICS_METRICS_PATH = PROJECT_ROOT / "outputs" / "minimal_grey_box_physics" / "grey_box_physics_metrics.json"
SOFT_SENSOR_MATRIX_METRICS_PATH = PROJECT_ROOT / "outputs" / "soft_sensor_matrix_coupling" / "soft_sensor_matrix_metrics.json"
FIELD_PATH_ENDPOINT_LABEL_PREFLIGHT_PATH = (
    PROJECT_ROOT
    / "outputs"
    / "soft_sensor_matrix_coupling"
    / "field_path_endpoint_label_package_preflight.json"
)
ENGINEERING_CONSTRAINTS_METRICS_PATH = PROJECT_ROOT / "outputs" / "engineering_execution_constraints" / "engineering_constraints_metrics.json"
KG_REASONING_METRICS_PATH = PROJECT_ROOT / "outputs" / "knowledge_graph_reasoning" / "kg_reasoning_metrics.json"
MAIN_CHAIN_RECONNECTION_METRICS_PATH = PROJECT_ROOT / "outputs" / "main_chain_reconnection" / "main_chain_reconnection_metrics.json"
FIELD_VALIDATION_ALIGNMENT_METRICS_PATH = PROJECT_ROOT / "outputs" / "field_validation_queue_alignment" / "field_validation_queue_alignment_metrics.json"
CLAIM_SPECIFIC_FIELD_PACKAGE_METRICS_PATH = PROJECT_ROOT / "outputs" / "claim_specific_field_package" / "claim_specific_field_package_metrics.json"
UNIFIED_FIELD_EVIDENCE_GATE_METRICS_PATH = PROJECT_ROOT / "outputs" / "unified_field_evidence_gate" / "unified_field_evidence_gate_metrics.json"
REAL_FIELD_PACKAGE_ACCEPTANCE_METRICS_PATH = PROJECT_ROOT / "outputs" / "real_field_package_acceptance_gate" / "real_field_package_acceptance_gate_metrics.json"
R7_PIPELINE_METRICS_PATH = PROJECT_ROOT / "outputs" / "r7_real_field_replay_pipeline" / "r7_real_field_replay_pipeline_metrics.json"
OBSERVATION_CONTRACT_METRICS_PATH = PROJECT_ROOT / "outputs" / "observation_contract_merge" / "observation_contract_metrics.json"
OBSERVATION_RESPONSE_BRIDGE_METRICS_PATH = (
    PROJECT_ROOT / "outputs" / "observation_response_bridge" / "observation_response_bridge_metrics.json"
)
CATALYST_EVIDENCE_RESPONSE_GATE_METRICS_PATH = (
    PROJECT_ROOT / "outputs" / "catalyst_evidence_response_gate" / "catalyst_evidence_response_gate_metrics.json"
)
CATALYST_RESPONSE_SUBMISSION_KIT_METRICS_PATH = (
    PROJECT_ROOT / "outputs" / "catalyst_response_submission_kit" / "catalyst_response_submission_kit_metrics.json"
)
FOCUSED_CATALYST_RESPONSE_MERGE_PREFLIGHT_PATH = (
    PROJECT_ROOT / "outputs" / "focused_catalyst_response_merge" / "focused_catalyst_response_merge_preflight.json"
)
FOCUSED_CATALYST_RESPONSE_REPAIR_WORK_ORDER_PATH = (
    PROJECT_ROOT / "outputs" / "focused_catalyst_response_merge" / "focused_catalyst_response_repair_work_order.json"
)
CATALYST_FIELD_PACKAGE_SLICE_METRICS_PATH = (
    PROJECT_ROOT / "outputs" / "catalyst_field_package_slice" / "catalyst_field_package_slice_metrics.json"
)
CATALYST_SLICE_R7_PATCH_CANDIDATE_METRICS_PATH = (
    PROJECT_ROOT
    / "outputs"
    / "catalyst_slice_r7_patch_candidate"
    / "catalyst_slice_r7_patch_candidate_metrics.json"
)
CONTROL_REPLAY_STRESS_METRICS_PATH = PROJECT_ROOT / "outputs" / "control_replay_counterfactual_stress" / "control_replay_stress_metrics.json"
FORMAL_SEARCH_EXECUTION_ROUTE_PLAN_PATH = (
    PROJECT_ROOT
    / "outputs"
    / "agent_architecture_consolidation"
    / "formal_search_execution_route_plan.json"
)
FORMAL_SEARCH_AI_NONLEGAL_REVIEW_BRIEF_PATH = (
    PROJECT_ROOT
    / "outputs"
    / "agent_architecture_consolidation"
    / "formal_search_ai_nonlegal_review_brief.json"
)
FORMAL_SEARCH_NONLEGAL_REVIEW_OPERATOR_PACKET_PATH = (
    PROJECT_ROOT
    / "outputs"
    / "agent_architecture_consolidation"
    / "formal_search_nonlegal_review_operator_packet.json"
)
DELIVERABLES_DIR = PROJECT_ROOT / "deliverables" / "model_core_optimization"
OUT_DIR = PROJECT_ROOT / "outputs" / "agent50_model_core_governance"
METRICS_DIR = PROJECT_ROOT / "outputs" / "model_core_governance"
PRIORITY_PATH = METRICS_DIR / "priority_ranking.json"
EXTERNAL_ACTIVATION_CONTRACT_PATH = METRICS_DIR / "external_activation_contract.json"
EXTERNAL_ACTIVATION_ROUTER_PATH = METRICS_DIR / "external_activation_router.json"
EXTERNAL_ACTIVATION_OPERATOR_ACTION_PACKET_PATH = (
    METRICS_DIR / "external_activation_operator_action_packet.json"
)
FIELD_ACTIVATION_MATRIX_PATH = METRICS_DIR / "field_activation_matrix.json"
STAGE_BOUNDARY_EXTERNAL_ACTION_BOARD_PATH = (
    METRICS_DIR / "stage_boundary_external_action_board.json"
)
STAGE_BOUNDARY_EXTERNAL_ACTION_BOARD_REPORT_PATH = (
    DELIVERABLES_DIR / "stage_boundary_external_action_board.md"
)
NEW_CORE_INTERFACE_CANDIDATE_GATE_PATH = (
    METRICS_DIR / "new_core_interface_candidate_gate.json"
)
NEW_CORE_INTERFACE_CANDIDATE_GATE_REPORT_PATH = (
    DELIVERABLES_DIR / "new_core_interface_candidate_gate.md"
)
EXTERNAL_PACKAGE_READINESS_BOARD_PATH = (
    METRICS_DIR / "external_package_readiness_board.json"
)
EXTERNAL_PACKAGE_READINESS_BOARD_REPORT_PATH = (
    DELIVERABLES_DIR / "external_package_readiness_board.md"
)
EXTERNAL_PACKAGE_OPERATOR_ACTION_PACKET_PATH = (
    METRICS_DIR / "external_package_operator_action_packet.json"
)
EXTERNAL_PACKAGE_OPERATOR_ACTION_PACKET_REPORT_PATH = (
    DELIVERABLES_DIR / "external_package_operator_action_packet.md"
)
EXTERNAL_PACKAGE_ACQUISITION_MATURITY_GATE_PATH = (
    METRICS_DIR / "external_package_acquisition_maturity_gate.json"
)
EXTERNAL_PACKAGE_ACQUISITION_MATURITY_GATE_REPORT_PATH = (
    DELIVERABLES_DIR / "external_package_acquisition_maturity_gate.md"
)
CORE_INTERFACE_CONSOLIDATION_PATH = (
    METRICS_DIR / "core_interface_consolidation.json"
)
CORE_INTERFACE_CONSOLIDATION_REPORT_PATH = (
    DELIVERABLES_DIR / "core_interface_consolidation.md"
)
GREY_BOX_CALIBRATION_PACKAGE_PREFLIGHT_PATH = (
    PROJECT_ROOT / "outputs" / "grey_box_calibration_package" / "grey_box_calibration_package_preflight.json"
)
GREY_BOX_FIELD_CALIBRATION_SUMMARY_PATH = (
    PROJECT_ROOT / "outputs" / "grey_box_calibration_package" / "grey_box_field_calibration_summary.json"
)
GREY_BOX_CALIBRATION_COLLECTION_WORK_ORDER_PATH = (
    PROJECT_ROOT
    / "outputs"
    / "grey_box_calibration_package"
    / "grey_box_calibration_collection_work_order.json"
)
GREY_BOX_CALIBRATION_COLLECTION_WORK_ORDER_REPORT_PATH = (
    DELIVERABLES_DIR / "grey_box_calibration_collection_work_order.md"
)
GREY_BOX_SUBMISSION_READINESS_GATE_PATH = (
    PROJECT_ROOT / "outputs" / "grey_box_calibration_package" / "grey_box_submission_readiness_gate.json"
)
GREY_BOX_SUBMISSION_READINESS_GATE_REPORT_PATH = (
    DELIVERABLES_DIR / "grey_box_submission_readiness_gate.md"
)
FIELD_SUPPORTED_KG_EDGE_PREFLIGHT_PATH = (
    PROJECT_ROOT / "outputs" / "field_supported_kg_edge_package" / "field_supported_kg_edge_package_preflight.json"
)
SPARSE_TOPOLOGY_INSTALLABILITY_PREFLIGHT_PATH = (
    PROJECT_ROOT
    / "outputs"
    / "sparse_topology_installability_package"
    / "sparse_topology_installability_package_preflight.json"
)
FIELD_CONTROL_REPLAY_PREFLIGHT_PATH = (
    PROJECT_ROOT / "outputs" / "field_control_replay_package" / "field_control_replay_package_preflight.json"
)
FIELD_MISSINGNESS_REPLAY_PREFLIGHT_PATH = (
    PROJECT_ROOT / "outputs" / "field_missingness_replay_package" / "field_missingness_replay_package_preflight.json"
)


def main() -> None:
    DELIVERABLES_DIR.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    METRICS_DIR.mkdir(parents=True, exist_ok=True)

    manifest = _read_json(MANIFEST_PATH)
    agent48_metrics = _read_json(SPARSE_METRICS_PATH)
    agent49_metrics = _read_json(COLLAB_METRICS_PATH)
    catalyst_proxy_metrics = _read_optional_json(CATALYST_PROXY_METRICS_PATH)
    replay_evaluation_metrics = _read_optional_json(REPLAY_EVALUATION_METRICS_PATH)
    grey_box_physics_metrics = _read_optional_json(GREY_BOX_PHYSICS_METRICS_PATH)
    soft_sensor_matrix_metrics = _read_optional_json(SOFT_SENSOR_MATRIX_METRICS_PATH)
    field_path_endpoint_label_preflight = _read_optional_json(FIELD_PATH_ENDPOINT_LABEL_PREFLIGHT_PATH)
    engineering_constraints_metrics = _read_optional_json(ENGINEERING_CONSTRAINTS_METRICS_PATH)
    kg_reasoning_metrics = _read_optional_json(KG_REASONING_METRICS_PATH)
    main_chain_reconnection_metrics = _read_optional_json(MAIN_CHAIN_RECONNECTION_METRICS_PATH)
    field_validation_alignment_metrics = _read_optional_json(FIELD_VALIDATION_ALIGNMENT_METRICS_PATH)
    claim_specific_field_package_metrics = _read_optional_json(CLAIM_SPECIFIC_FIELD_PACKAGE_METRICS_PATH)
    unified_field_evidence_gate_metrics = _read_optional_json(UNIFIED_FIELD_EVIDENCE_GATE_METRICS_PATH)
    real_field_package_acceptance_metrics = _read_optional_json(REAL_FIELD_PACKAGE_ACCEPTANCE_METRICS_PATH)
    r7_pipeline_metrics = _read_optional_json(R7_PIPELINE_METRICS_PATH)
    observation_contract_metrics = _read_optional_json(OBSERVATION_CONTRACT_METRICS_PATH)
    observation_response_bridge_metrics = _read_optional_json(OBSERVATION_RESPONSE_BRIDGE_METRICS_PATH)
    catalyst_evidence_response_gate_metrics = _read_optional_json(CATALYST_EVIDENCE_RESPONSE_GATE_METRICS_PATH)
    catalyst_response_submission_kit_metrics = _read_optional_json(CATALYST_RESPONSE_SUBMISSION_KIT_METRICS_PATH)
    focused_catalyst_response_merge_metrics = _read_optional_json(FOCUSED_CATALYST_RESPONSE_MERGE_PREFLIGHT_PATH)
    catalyst_field_package_slice_metrics = _read_optional_json(CATALYST_FIELD_PACKAGE_SLICE_METRICS_PATH)
    catalyst_slice_r7_patch_candidate_metrics = _read_optional_json(CATALYST_SLICE_R7_PATCH_CANDIDATE_METRICS_PATH)
    control_replay_stress_metrics = _read_optional_json(CONTROL_REPLAY_STRESS_METRICS_PATH)
    formal_search_execution_route_plan = _read_optional_json(FORMAL_SEARCH_EXECUTION_ROUTE_PLAN_PATH)
    formal_search_ai_nonlegal_review_brief = _read_optional_json(
        FORMAL_SEARCH_AI_NONLEGAL_REVIEW_BRIEF_PATH
    )
    formal_search_nonlegal_review_operator_packet = _read_optional_json(
        FORMAL_SEARCH_NONLEGAL_REVIEW_OPERATOR_PACKET_PATH
    )
    grey_box_calibration_package_preflight = _read_optional_json(
        GREY_BOX_CALIBRATION_PACKAGE_PREFLIGHT_PATH
    )
    grey_box_field_calibration_summary = _read_optional_json(
        GREY_BOX_FIELD_CALIBRATION_SUMMARY_PATH
    )
    grey_box_calibration_collection_work_order = _read_optional_json(
        GREY_BOX_CALIBRATION_COLLECTION_WORK_ORDER_PATH
    )
    grey_box_submission_readiness_gate = _read_optional_json(
        GREY_BOX_SUBMISSION_READINESS_GATE_PATH
    )
    field_supported_kg_edge_preflight = _read_optional_json(
        FIELD_SUPPORTED_KG_EDGE_PREFLIGHT_PATH
    )
    sparse_topology_installability_preflight = _read_optional_json(
        SPARSE_TOPOLOGY_INSTALLABILITY_PREFLIGHT_PATH
    )
    field_control_replay_preflight = _read_optional_json(FIELD_CONTROL_REPLAY_PREFLIGHT_PATH)
    field_missingness_replay_preflight = _read_optional_json(
        FIELD_MISSINGNESS_REPLAY_PREFLIGHT_PATH
    )
    external_activation_router = _read_optional_json(EXTERNAL_ACTIVATION_ROUTER_PATH)
    external_activation_operator_action_packet = _read_optional_json(
        EXTERNAL_ACTIVATION_OPERATOR_ACTION_PACKET_PATH
    )
    field_activation_matrix_metrics = _read_optional_json(FIELD_ACTIVATION_MATRIX_PATH)
    field_path_endpoint_label_preflight = _field_path_endpoint_preflight_from_r7_or_agent54(
        r7_pipeline_metrics,
        field_path_endpoint_label_preflight,
    )
    evidence_matrix = _external_evidence_matrix()
    report = ModelCoreOptimizationGovernanceAgent(
        manifest=manifest,
        agent48_metrics=agent48_metrics,
        agent49_metrics=agent49_metrics,
        catalyst_proxy_metrics=catalyst_proxy_metrics,
        replay_evaluation_metrics=replay_evaluation_metrics,
        grey_box_physics_metrics=grey_box_physics_metrics,
        soft_sensor_matrix_metrics=soft_sensor_matrix_metrics,
        engineering_constraints_metrics=engineering_constraints_metrics,
        knowledge_graph_reasoning_metrics=kg_reasoning_metrics,
        main_chain_reconnection_metrics=main_chain_reconnection_metrics,
        field_validation_queue_alignment_metrics=field_validation_alignment_metrics,
        claim_specific_field_package_metrics=claim_specific_field_package_metrics,
        unified_field_evidence_gate_metrics=unified_field_evidence_gate_metrics,
        real_field_package_acceptance_metrics=real_field_package_acceptance_metrics,
        r7_pipeline_metrics=r7_pipeline_metrics,
        field_path_endpoint_label_preflight=field_path_endpoint_label_preflight,
        formal_search_execution_route_plan=formal_search_execution_route_plan,
        formal_search_ai_nonlegal_review_brief=formal_search_ai_nonlegal_review_brief,
        formal_search_nonlegal_review_operator_packet=(
            formal_search_nonlegal_review_operator_packet
        ),
        external_activation_router=external_activation_router,
        external_activation_operator_action_packet=external_activation_operator_action_packet,
        field_activation_matrix_metrics=field_activation_matrix_metrics,
        observation_contract_metrics=observation_contract_metrics,
        observation_response_bridge_metrics=observation_response_bridge_metrics,
        catalyst_evidence_response_gate_metrics=catalyst_evidence_response_gate_metrics,
        catalyst_response_submission_kit_metrics=catalyst_response_submission_kit_metrics,
        focused_catalyst_response_merge_metrics=focused_catalyst_response_merge_metrics,
        catalyst_field_package_slice_metrics=catalyst_field_package_slice_metrics,
        catalyst_slice_r7_patch_candidate_metrics=catalyst_slice_r7_patch_candidate_metrics,
        control_replay_stress_metrics=control_replay_stress_metrics,
        external_evidence_matrix=evidence_matrix,
        current_work_item={
            "task_id": "r8u160_grey_box_submission_readiness_gate",
            "title": "把 GREY_BOX_CALIBRATION_PACKAGE_DIR 推进为可计算提交成熟度 gate",
            "category": "model_core_governance",
            "touches_model_metrics": True,
            "previous_core_score": manifest.get(
                "latest_agent50_core_score",
                manifest.get("latest_agent50_core_score_previous"),
            ),
            "previous_module_stage_status": manifest.get(
                "latest_agent50_module_stage_status",
                manifest.get(
                    "latest_agent50_module_stage_status_previous",
                    "module_stage_needs_more_core_work",
                ),
            ),
            "resolved_hard_blocker": False,
            "changed_contract_or_gate": True,
            "new_or_changed_state_variable": False,
            "new_or_changed_gate": True,
            "targeted_tests_passed": True,
        },
    ).run([])
    new_core_interface_candidate_gate = build_new_core_interface_candidate_gate(
        core_gate=report.metrics["quantified_core_score_gate"],
        priority_ranking=report.metrics["priority_ranking"],
        grey_box_calibration_preflight=grey_box_calibration_package_preflight,
        grey_box_field_calibration_summary=grey_box_field_calibration_summary,
        field_supported_kg_edge_preflight=field_supported_kg_edge_preflight,
        sparse_topology_installability_preflight=sparse_topology_installability_preflight,
        field_control_replay_preflight=field_control_replay_preflight,
        field_missingness_replay_preflight=field_missingness_replay_preflight,
    )
    external_package_readiness_board = build_external_package_readiness_board(
        new_core_interface_candidate_gate=new_core_interface_candidate_gate,
        package_artifacts=attach_submission_readiness_gap(
            package_artifacts=_external_package_artifacts(),
            candidate_id="NCI1_GREY_BOX_CALIBRATION_PACKAGE",
            submission_readiness_gate=grey_box_submission_readiness_gate,
        ),
    )
    external_package_operator_action_packet = build_external_package_operator_action_packet(
        readiness_board=external_package_readiness_board,
    )
    external_package_acquisition_maturity_gate = (
        build_external_package_acquisition_maturity_gate(
            readiness_board=external_package_readiness_board,
            operator_action_packet=external_package_operator_action_packet,
        )
    )
    _attach_external_package_acquisition_stage_gate(
        report,
        external_package_acquisition_maturity_gate,
    )
    core_interface_consolidation = build_core_interface_consolidation(
        agent48_metrics=agent48_metrics,
        field_control_replay_preflight=field_control_replay_preflight,
        sparse_topology_installability_preflight=sparse_topology_installability_preflight,
        grey_box_collection_work_order=grey_box_calibration_collection_work_order,
        grey_box_submission_readiness_gate=grey_box_submission_readiness_gate,
        external_package_acquisition_maturity_gate=external_package_acquisition_maturity_gate,
        agent52_replay_metrics=replay_evaluation_metrics,
    )
    stage_boundary_external_action_board = build_stage_boundary_external_action_board(
        core_gate=report.metrics["quantified_core_score_gate"],
        external_activation_operator_action_packet=external_activation_operator_action_packet,
        formal_search_nonlegal_review_operator_packet=formal_search_nonlegal_review_operator_packet,
        focused_catalyst_response_merge_metrics=focused_catalyst_response_merge_metrics,
        new_core_interface_candidate_gate=new_core_interface_candidate_gate,
        claim_basis_promotion_gate=unified_field_evidence_gate_metrics.get(
            "claim_basis_promotion_gate", {}
        ),
    )

    generated_files = {
        "model_core_goal": str(DELIVERABLES_DIR / "model_core_goal.md"),
        "goal_iteration_trace": str(DELIVERABLES_DIR / "goal_iteration_trace.md"),
        "user_interrupt_lessons": str(DELIVERABLES_DIR / "user_interrupt_lessons.md"),
        "external_evidence_matrix": str(DELIVERABLES_DIR / "external_evidence_matrix.md"),
        "issue_priority_ranking": str(DELIVERABLES_DIR / "issue_priority_ranking.md"),
        "execution_prompt": str(DELIVERABLES_DIR / "execution_prompt.md"),
        "self_interrupt_checklist": str(DELIVERABLES_DIR / "self_interrupt_checklist.md"),
        "governance_report": str(DELIVERABLES_DIR / "governance_report.md"),
        "agent50_report": str(OUT_DIR / "agent50_report.md"),
        "priority_ranking": str(PRIORITY_PATH),
        "core_score_termination_gate": str(METRICS_DIR / "core_score_termination_gate.json"),
        "external_activation_contract": str(EXTERNAL_ACTIVATION_CONTRACT_PATH),
        "external_activation_router": str(EXTERNAL_ACTIVATION_ROUTER_PATH),
        "external_activation_operator_action_packet": str(
            EXTERNAL_ACTIVATION_OPERATOR_ACTION_PACKET_PATH
        ),
        "field_activation_matrix": str(FIELD_ACTIVATION_MATRIX_PATH),
        "stage_boundary_external_action_board": str(STAGE_BOUNDARY_EXTERNAL_ACTION_BOARD_PATH),
        "stage_boundary_external_action_board_report": str(
            STAGE_BOUNDARY_EXTERNAL_ACTION_BOARD_REPORT_PATH
        ),
        "new_core_interface_candidate_gate": str(NEW_CORE_INTERFACE_CANDIDATE_GATE_PATH),
        "new_core_interface_candidate_gate_report": str(
            NEW_CORE_INTERFACE_CANDIDATE_GATE_REPORT_PATH
        ),
        "external_package_readiness_board": str(EXTERNAL_PACKAGE_READINESS_BOARD_PATH),
        "external_package_readiness_board_report": str(
            EXTERNAL_PACKAGE_READINESS_BOARD_REPORT_PATH
        ),
        "external_package_operator_action_packet": str(
            EXTERNAL_PACKAGE_OPERATOR_ACTION_PACKET_PATH
        ),
        "external_package_operator_action_packet_report": str(
            EXTERNAL_PACKAGE_OPERATOR_ACTION_PACKET_REPORT_PATH
        ),
        "external_package_acquisition_maturity_gate": str(
            EXTERNAL_PACKAGE_ACQUISITION_MATURITY_GATE_PATH
        ),
        "external_package_acquisition_maturity_gate_report": str(
            EXTERNAL_PACKAGE_ACQUISITION_MATURITY_GATE_REPORT_PATH
        ),
        "core_interface_consolidation": str(CORE_INTERFACE_CONSOLIDATION_PATH),
        "core_interface_consolidation_report": str(CORE_INTERFACE_CONSOLIDATION_REPORT_PATH),
        "grey_box_calibration_package_preflight": str(
            GREY_BOX_CALIBRATION_PACKAGE_PREFLIGHT_PATH
        ),
        "grey_box_field_calibration_summary": str(
            GREY_BOX_FIELD_CALIBRATION_SUMMARY_PATH
        ),
        "grey_box_calibration_collection_work_order": str(
            GREY_BOX_CALIBRATION_COLLECTION_WORK_ORDER_PATH
        ),
        "grey_box_calibration_collection_work_order_report": str(
            GREY_BOX_CALIBRATION_COLLECTION_WORK_ORDER_REPORT_PATH
        ),
        "grey_box_submission_readiness_gate": str(
            GREY_BOX_SUBMISSION_READINESS_GATE_PATH
        ),
        "grey_box_submission_readiness_gate_report": str(
            GREY_BOX_SUBMISSION_READINESS_GATE_REPORT_PATH
        ),
        "field_supported_kg_edge_package_preflight": str(
            FIELD_SUPPORTED_KG_EDGE_PREFLIGHT_PATH
        ),
        "sparse_topology_installability_package_preflight": str(
            SPARSE_TOPOLOGY_INSTALLABILITY_PREFLIGHT_PATH
        ),
        "field_control_replay_package_preflight": str(FIELD_CONTROL_REPLAY_PREFLIGHT_PATH),
        "field_missingness_replay_package_preflight": str(
            FIELD_MISSINGNESS_REPLAY_PREFLIGHT_PATH
        ),
        "observation_response_bridge": str(OBSERVATION_RESPONSE_BRIDGE_METRICS_PATH),
        "catalyst_evidence_response_gate": str(CATALYST_EVIDENCE_RESPONSE_GATE_METRICS_PATH),
        "catalyst_response_submission_kit": str(CATALYST_RESPONSE_SUBMISSION_KIT_METRICS_PATH),
        "focused_catalyst_response_merge": str(FOCUSED_CATALYST_RESPONSE_MERGE_PREFLIGHT_PATH),
        "focused_catalyst_response_repair_work_order": str(FOCUSED_CATALYST_RESPONSE_REPAIR_WORK_ORDER_PATH),
        "catalyst_field_package_slice": str(CATALYST_FIELD_PACKAGE_SLICE_METRICS_PATH),
        "catalyst_slice_r7_patch_candidate": str(CATALYST_SLICE_R7_PATCH_CANDIDATE_METRICS_PATH),
    }

    (DELIVERABLES_DIR / "model_core_goal.md").write_text(_model_core_goal_md(), encoding="utf-8")
    (DELIVERABLES_DIR / "goal_iteration_trace.md").write_text(_goal_iteration_trace_md(), encoding="utf-8")
    (DELIVERABLES_DIR / "user_interrupt_lessons.md").write_text(_user_interrupt_lessons_md(), encoding="utf-8")
    (DELIVERABLES_DIR / "external_evidence_matrix.md").write_text(_evidence_matrix_md(evidence_matrix), encoding="utf-8")
    (DELIVERABLES_DIR / "issue_priority_ranking.md").write_text(_issue_priority_ranking_md(report), encoding="utf-8")
    (DELIVERABLES_DIR / "execution_prompt.md").write_text(_execution_prompt_md(), encoding="utf-8")
    (DELIVERABLES_DIR / "self_interrupt_checklist.md").write_text(_self_interrupt_checklist_md(), encoding="utf-8")
    (DELIVERABLES_DIR / "governance_report.md").write_text(_governance_report_md(report), encoding="utf-8")
    (OUT_DIR / "agent50_report.md").write_text(
        _agent50_report_md(
            report,
            generated_files,
            external_package_readiness_board,
            external_package_operator_action_packet,
            external_package_acquisition_maturity_gate,
            core_interface_consolidation,
            grey_box_submission_readiness_gate,
        ),
        encoding="utf-8",
    )
    (OUT_DIR / "agent50_report.json").write_text(
        json.dumps(
            _agent50_payload(
                report,
                generated_files,
                evidence_matrix,
                external_package_readiness_board,
                external_package_operator_action_packet,
                external_package_acquisition_maturity_gate,
                core_interface_consolidation,
                grey_box_submission_readiness_gate,
            ),
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    PRIORITY_PATH.write_text(
        json.dumps(
            {
                "priority_ranking": report.metrics["priority_ranking"],
                "low_priority_backlog": report.metrics["low_priority_backlog"],
                "external_blocker_backlog": report.metrics["external_blocker_backlog"],
                "blocked_reasons": report.metrics["blocked_reasons"],
                "external_activation_contract": report.metrics["external_activation_contract"],
                "recommended_next_core_action": report.metrics["recommended_next_core_action"],
                "self_interrupt_verdict": report.metrics["self_interrupt_verdict"],
                "self_interrupt_reason": report.metrics["self_interrupt_reason"],
                "self_interrupt_mode": report.metrics["self_interrupt_mode"],
                "governance_review_gate": report.metrics["governance_review_gate"],
                "quantified_core_score_gate": report.metrics["quantified_core_score_gate"],
                "external_package_acquisition_stage_gate": report.metrics[
                    "external_package_acquisition_stage_gate"
                ],
                "evidence_matrix_status": report.metrics["evidence_matrix_status"],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    (METRICS_DIR / "core_score_termination_gate.json").write_text(
        json.dumps(report.metrics["quantified_core_score_gate"], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    EXTERNAL_ACTIVATION_CONTRACT_PATH.write_text(
        json.dumps(report.metrics["external_activation_contract"], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    STAGE_BOUNDARY_EXTERNAL_ACTION_BOARD_PATH.write_text(
        json.dumps(stage_boundary_external_action_board, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    STAGE_BOUNDARY_EXTERNAL_ACTION_BOARD_REPORT_PATH.write_text(
        stage_boundary_external_action_board_report_md(stage_boundary_external_action_board),
        encoding="utf-8",
    )
    NEW_CORE_INTERFACE_CANDIDATE_GATE_PATH.write_text(
        json.dumps(new_core_interface_candidate_gate, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    NEW_CORE_INTERFACE_CANDIDATE_GATE_REPORT_PATH.write_text(
        new_core_interface_candidate_gate_report_md(new_core_interface_candidate_gate),
        encoding="utf-8",
    )
    EXTERNAL_PACKAGE_READINESS_BOARD_PATH.write_text(
        json.dumps(external_package_readiness_board, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    EXTERNAL_PACKAGE_READINESS_BOARD_REPORT_PATH.write_text(
        external_package_readiness_board_report_md(external_package_readiness_board),
        encoding="utf-8",
    )
    EXTERNAL_PACKAGE_OPERATOR_ACTION_PACKET_PATH.write_text(
        json.dumps(external_package_operator_action_packet, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    EXTERNAL_PACKAGE_OPERATOR_ACTION_PACKET_REPORT_PATH.write_text(
        external_package_operator_action_packet_report_md(external_package_operator_action_packet),
        encoding="utf-8",
    )
    EXTERNAL_PACKAGE_ACQUISITION_MATURITY_GATE_PATH.write_text(
        json.dumps(
            external_package_acquisition_maturity_gate,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    EXTERNAL_PACKAGE_ACQUISITION_MATURITY_GATE_REPORT_PATH.write_text(
        external_package_acquisition_maturity_gate_report_md(
            external_package_acquisition_maturity_gate
        ),
        encoding="utf-8",
    )
    CORE_INTERFACE_CONSOLIDATION_PATH.write_text(
        json.dumps(core_interface_consolidation, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    CORE_INTERFACE_CONSOLIDATION_REPORT_PATH.write_text(
        core_interface_consolidation_report_md(core_interface_consolidation),
        encoding="utf-8",
    )

    _update_manifest(
        generated_files,
        report,
        stage_boundary_external_action_board,
        new_core_interface_candidate_gate,
        external_package_readiness_board,
        external_package_operator_action_packet,
        external_package_acquisition_maturity_gate,
        core_interface_consolidation,
        grey_box_submission_readiness_gate,
    )

    print(report.summary)
    for rec in report.recommendations:
        print(f"- {rec}")
    for key, path in generated_files.items():
        print(f"{key}: {path}")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_optional_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return _read_json(path)


def _field_path_endpoint_preflight_from_r7_or_agent54(
    r7_pipeline_metrics: dict[str, Any],
    agent54_preflight: dict[str, Any],
) -> dict[str, Any]:
    r7_preflight = r7_pipeline_metrics.get("field_path_endpoint_label_package_preflight", {})
    if isinstance(r7_preflight, dict) and r7_preflight.get("preflight_status"):
        return r7_preflight
    readiness = r7_pipeline_metrics.get("pipeline_readiness", {})
    if isinstance(readiness, dict) and readiness.get("field_path_endpoint_label_preflight_status"):
        return {
            "preflight_status": readiness.get("field_path_endpoint_label_preflight_status"),
            "matched_batch_count": readiness.get("field_path_endpoint_matched_batch_count", 0),
            "minimum_matched_batch_count": readiness.get("field_path_endpoint_minimum_matched_batch_count", 5),
            "missing_tables": readiness.get("field_path_endpoint_missing_tables", []),
            "required_field_gap_count": readiness.get("field_path_endpoint_required_field_gap_count", 0),
            "template_marker_count": readiness.get("field_path_endpoint_template_marker_count", 0),
            "table_row_counts": readiness.get("field_path_endpoint_table_row_counts", {}),
            "table_batch_counts": readiness.get("field_path_endpoint_table_batch_counts", {}),
            "batch_alignment_gap_count": readiness.get("field_path_endpoint_batch_alignment_gap_count", 0),
            "required_matched_batch_deficit": readiness.get(
                "field_path_endpoint_required_matched_batch_deficit",
                0,
            ),
            "alignment_patch_plan": {
                "patch_plan_status": readiness.get(
                    "field_path_endpoint_alignment_patch_plan_status",
                    "not_available",
                ),
                "item_count": readiness.get("field_path_endpoint_alignment_patch_plan_item_count", 0),
            },
            "can_route_to_field_layout_holdout": readiness.get("field_path_endpoint_label_package_ready", False),
        }
    return agent54_preflight


def _external_package_artifacts() -> dict[str, dict[str, str]]:
    return {
        "NCI1_GREY_BOX_CALIBRATION_PACKAGE": {
            "preflight_json": "outputs/grey_box_calibration_package/grey_box_calibration_package_preflight.json",
            "template_dir": "outputs/grey_box_calibration_package/grey_box_calibration_package_template",
            "report_md": "deliverables/model_core_optimization/grey_box_calibration_package_preflight.md",
        },
        "NCI5_FIELD_SUPPORTED_KG_EDGE_PACKAGE": {
            "preflight_json": "outputs/field_supported_kg_edge_package/field_supported_kg_edge_package_preflight.json",
            "template_dir": "outputs/field_supported_kg_edge_package/field_supported_kg_edge_package_template",
            "report_md": "deliverables/model_core_optimization/field_supported_kg_edge_package_preflight.md",
        },
        "NCI3_FIELD_CONTROL_REPLAY_PACKAGE": {
            "preflight_json": "outputs/field_control_replay_package/field_control_replay_package_preflight.json",
            "template_dir": "outputs/field_control_replay_package/field_control_replay_package_template",
            "report_md": "deliverables/model_core_optimization/field_control_replay_package_preflight.md",
        },
        "NCI4_SPARSE_TOPOLOGY_INSTALLABILITY_PACKAGE": {
            "preflight_json": "outputs/sparse_topology_installability_package/sparse_topology_installability_package_preflight.json",
            "template_dir": "outputs/sparse_topology_installability_package/sparse_topology_installability_package_template",
            "report_md": "deliverables/model_core_optimization/sparse_topology_installability_package_preflight.md",
        },
        "NCI2_FIELD_MISSINGNESS_REPLAY_PACKAGE": {
            "preflight_json": "outputs/field_missingness_replay_package/field_missingness_replay_package_preflight.json",
            "template_dir": "outputs/field_missingness_replay_package/field_missingness_replay_package_template",
            "report_md": "deliverables/model_core_optimization/field_missingness_replay_package_preflight.md",
        },
    }


def _external_evidence_matrix() -> list[dict[str, object]]:
    return [
        {
            "source": "PySensors official repository and README, https://github.com/dynamicslab/pysensors",
            "method_family": "sparse sensor placement for reconstruction/classification",
            "model_mapping": "Agent48 的 node-modality 矩阵可借鉴 SSPOR/SSPOC、QR/CCQR/GQR、SVD/PCA basis 与约束布点思路。",
            "data_needs": "候选节点、候选模态、节点拓扑/水力位置、成本、维护约束、历史状态矩阵、分类标签或重构目标。",
            "implementation_path": "先不安装依赖；在 Agent48 下一轮实现 greedy 与 D-optimal/QR-style baseline 对比，再决定是否接入 python-sensors。",
            "evaluation_metrics": [
                "soft_sensor_reconstruction_gain",
                "fault_classification_observability",
                "weak_state_coverage",
                "total_cost_index",
            ],
            "failure_boundary": "这是开源方法启发；没有真实拓扑和 field labels 时只能证明布点算法接口与 synthetic prior 合理。",
        },
        {
            "source": "USEPA WNTR official repository, https://github.com/USEPA/WNTR",
            "method_family": "water network topology, hydraulic operation and water quality simulation",
            "model_mapping": "Agent48 可借鉴 WNTR/EPANET 风格的节点、边、水力、操作扰动和水质传播表达，但本项目是处理单元+回流环，不机械套用饮用水管网。",
            "data_needs": "节点/边拓扑、流量、池容、管段/单元停留时间、阀泵动作、采样延迟、水质事件时间戳。",
            "implementation_path": "把真实或 synthetic topology prior 从平面节点表升级为 graph schema；先自定义轻量图，不立即引入 WNTR。",
            "evaluation_metrics": [
                "topology_coverage",
                "hydraulic_observability",
                "residence_time_error",
                "matrix_shock_event_lead_time",
            ],
            "failure_boundary": "WNTR 面向水分配网络韧性，本项目只能借鉴图拓扑/水力模拟思想，不能直接作为污水处理反应器实证模型。",
        },
        {
            "source": "WaterTAP official repository, https://github.com/watertap-org/watertap",
            "method_family": "water treatment flowsheet modeling and optimization",
            "model_mapping": "灰箱物理机制可借鉴 flowsheet、unit model、constraint 和 costing 的组织方式，服务 P4/P7。",
            "data_needs": "单元工艺参数、进出水水质、药剂/能耗/成本、设计变量、约束、现场校准范围。",
            "implementation_path": "先在本项目中实现最小反应/停留/成本约束接口；若后续进入高保真 flowsheet，再评估 WaterTAP/IDAES 接入成本。",
            "evaluation_metrics": [
                "mass_balance_residual",
                "constraint_violation_rate",
                "operating_cost_index",
                "calibration_parameter_count",
            ],
            "failure_boundary": "当前模型没有足够工艺参数支撑完整 flowsheet；只能作为结构化建模参考。",
        },
        {
            "source": "QSDsan official repository, https://github.com/QSD-Group/QSDsan",
            "method_family": "process modeling, system simulation, TEA and LCA for sanitation/resource recovery",
            "model_mapping": "工程可执行性层可借鉴 TEA/LCA/系统仿真，把传感布点、回流、药剂、能耗和维护成本纳入 reward。",
            "data_needs": "设备 CAPEX/OPEX、药剂库存、能耗、人工维护、再生周期、排放/副产物风险、处理规模。",
            "implementation_path": "先扩展 Agent49 reward_contract 的 cost/sustainability 字段；暂不把 QSDsan 作为运行依赖。",
            "evaluation_metrics": [
                "cost_efficiency",
                "energy_cost_index",
                "maintenance_window_feasibility",
                "sustainability_proxy",
            ],
            "failure_boundary": "没有真实成本和生命周期清单时，TEA/LCA 只可作为字段设计和敏感性分析框架。",
        },
        {
            "source": "Pyomo official repository, https://github.com/Pyomo/pyomo",
            "method_family": "structured optimization modeling",
            "model_mapping": "Agent48 布点和 Agent49 联动动作可转成约束优化：成本、覆盖、池容、执行器、安全门控和动作次数。",
            "data_needs": "决策变量、目标函数、约束、候选动作、设备边界、成本与风险权重。",
            "implementation_path": "先输出 optimization-ready data contract；等变量和约束稳定后再决定是否安装 Pyomo。",
            "evaluation_metrics": [
                "objective_value",
                "constraint_violation_rate",
                "pareto_front_size",
                "solver_feasibility_status",
            ],
            "failure_boundary": "没有可靠约束和权重时，优化解会制造虚假精确性，不能替代工程审查。",
        },
        {
            "source": "Academic Research Agent Skill, https://ngtiendong.github.io/Academic-Research-Agent-Skill/",
            "method_family": "evidence-first research workflow and claim verification",
            "model_mapping": "Agent50 借鉴 evidence before claims、source matrix、claim verification，把外部方法与模型改动强制绑定。",
            "data_needs": "来源、方法、适用条件、对本项目映射、验证指标、失败边界、人工/用户打断约束。",
            "implementation_path": "把该流程固化为 governance files、priority ranking 和 self-interrupt checklist。",
            "evaluation_metrics": [
                "evidence_matrix_completeness",
                "claim_traceability",
                "self_interrupt_verdict",
                "unsupported_claim_count",
            ],
            "failure_boundary": "skill 只能提供科研治理流程，不提供水处理机理或现场数据。",
        },
        {
            "source": "Model validation and uncertainty skill, https://skillsmp.com/skills/baratadiego-ecological-agent-skills-skills-model-validation-and-uncertainty-skill-md",
            "method_family": "model validation, calibration, uncertainty and extrapolation risk",
            "model_mapping": "软传感、Agent48/49 离线评估和灰箱模型需要从 accuracy 升级到 calibration、coverage、bootstrap uncertainty、外推风险。",
            "data_needs": "训练/CV/test/field holdout、预测区间、外推标记、弱目标分层标签、独立验证批次。",
            "implementation_path": "后续 Agent48/49 优化必须同步输出 calibration/uncertainty gates，而不是只输出 synthetic 分数。",
            "evaluation_metrics": [
                "interval_coverage",
                "calibration_slope",
                "extrapolation_risk_rate",
                "field_holdout_degradation",
            ],
            "failure_boundary": "没有独立 field holdout 时只能评估 synthetic robustness，不能声称现场泛化。",
        },
        {
            "source": "GRU-D: Che et al., Recurrent Neural Networks for Multivariate Time Series with Missing Values, https://arxiv.org/abs/1606.01865",
            "method_family": "missingness-aware time-series modeling",
            "model_mapping": "P5 借鉴 GRU-D 把缺失掩码和距离上次观测的时间间隔视为信息，而不是简单插值后丢弃缺失模式；对应 Agent54 的 availability_mask 与 time_since_last_observed_min。",
            "data_needs": "按 batch/timestamp/node/modality 记录的传感值、缺失掩码、上次观测时间差、传感器质量分数、真实 field missingness 原因。",
            "implementation_path": "当前不训练 GRU-D；先把这些字段固化为软传感矩阵合同和压力测试指标，后续有 field holdout 后再比较 GRU-D/轻量表格模型。",
            "evaluation_metrics": [
                "missingness_robustness_score",
                "layout_holdout_masked_mae",
                "interval_coverage_under_missingness",
                "node_specific_value_rate",
            ],
            "failure_boundary": "GRU-D 是方法启发；synthetic dropout 不能代表真实传感器污染、低频采样、通信故障或人工维护缺测。",
        },
        {
            "source": "BRITS: Cao et al., Bidirectional Recurrent Imputation for Time Series, https://papers.nips.cc/paper/7911-brits-bidirectional-recurrent-imputation-for-time-series",
            "method_family": "bidirectional imputation and consistency for incomplete time series",
            "model_mapping": "P5 借鉴 BRITS 的双向时序一致性思想，把低频/延迟传感下的前后窗口信息作为软传感补全和异常判断依据。",
            "data_needs": "连续传感时间序列、缺测片段、前后窗口、离线 lab 标签、节点/模态位置和缺测原因。",
            "implementation_path": "先实现 missingness stress tests 和 layout-aware feature contract；等真实 field replay 后，再决定是否引入双向插补模型或保持可解释轻量模型。",
            "evaluation_metrics": [
                "masked_state_support",
                "imputation_consistency_error",
                "field_missingness_replay_coverage",
                "weak_target_interval_coverage",
            ],
            "failure_boundary": "插补结果只能帮助状态估计，不能替代离线检测或 release gate；真实缺测机制未采集前不能证明现场鲁棒性。",
        },
        {
            "source": "PyPOTS official repository and documentation, https://github.com/WenjieDu/PyPOTS",
            "method_family": "time-series imputation and missing-data benchmark toolkit",
            "model_mapping": "P5 可借鉴 PyPOTS 的缺失时间序列基准化思路，把不同缺测机制、mask、imputation/forecasting 指标放入统一评估，而不是只看普通 MAE。",
            "data_needs": "多场景缺测 replay、mask 张量、真实/离线标签、场景标签、节点和模态维度。",
            "implementation_path": "当前先不安装 PyPOTS；Agent54 只输出模型可消费的矩阵合同、缺测压力测试和后续 benchmark schema。",
            "evaluation_metrics": [
                "masked_mae",
                "missingness_pattern_generalization",
                "scenario_stratified_coverage",
                "field_holdout_degradation",
            ],
            "failure_boundary": "benchmark 工具不能制造现场标签；没有真实缺测 replay 时只能做 synthetic interface validation。",
        },
        {
            "source": "scikit-learn HistGradientBoostingRegressor documentation, https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.HistGradientBoostingRegressor.html",
            "method_family": "lightweight tabular model with native missing-value handling",
            "model_mapping": "P5 的工程落地可先比较轻量表格模型，将 layout_id、node/modality、mask、时间间隔和灰箱残差作为特征，作为复杂时序模型前的可解释 baseline。",
            "data_needs": "结构化 field table、布局字段、缺失掩码、灰箱残差、目标隐藏状态或离线 proxy 标签。",
            "implementation_path": "先保留当前随机森林校正模型和 Agent54 schema；若 field rows 足够，再补一个 missing-value-native baseline 与现有 soft_sensor_calibrator 对照。",
            "evaluation_metrics": [
                "layout_holdout_mae",
                "calibration_curve_error",
                "masked_feature_importance",
                "abstention_rate",
            ],
            "failure_boundary": "轻量模型可解释但不自动处理时序因果；必须通过 layout holdout 和 field replay 检查外推风险。",
        },
        {
            "source": "User-provided wastewater multi-facility coordination slides, 2026-06-01 images",
            "method_family": "multi-agent coordination, shared replay/experience pool and decision-tree policy distillation",
            "model_mapping": "Agent49 可借鉴环境交互模型、共享经验池、联合奖励、策略实时评估与 ID3 决策树蒸馏，但必须映射到处理单元而非泵站。",
            "data_needs": "多节点状态、控制动作、奖励分量、操作结果、人工经验、动作一致性标签、风险事件。",
            "implementation_path": "下一步把 Agent49 从候选动作表升级为 replay-ready 离线评估框架，先蒸馏解释规则，再评估安全 offline RL。",
            "evaluation_metrics": [
                "joint_action_accuracy",
                "reward_regret",
                "distilled_policy_accuracy",
                "unsafe_action_block_rate",
            ],
            "failure_boundary": "用户图片是启发材料，不是可直接复现实验；不能把泵站协同结论迁移成水处理控制结论。",
        },
        {
            "source": "Offline reinforcement learning review and Conservative Q-Learning, https://arxiv.org/abs/2005.01643 and https://arxiv.org/abs/2006.04779",
            "method_family": "offline reinforcement learning and conservative policy evaluation",
            "model_mapping": "Agent52 借鉴离线 RL 的固定数据集、保守评估和禁止在线探索原则，把 Agent49 候选动作先放入 replay schema 和 reward regret 评估。",
            "data_needs": "状态、动作、奖励、下一状态/离线标签、行为策略或专家动作、执行器结果、误动作成本和场景标签。",
            "implementation_path": "先实现 state-action-reward replay 和离线指标，不训练在线 MARL；field replay 达标后再考虑安全 offline RL。",
            "evaluation_metrics": [
                "joint_action_accuracy",
                "mean_reward_regret",
                "p95_reward_regret",
                "field_replay_coverage",
            ],
            "failure_boundary": "离线 RL 文献只支持方法框架；没有真实 field replay 时不能声称学到可部署策略。",
        },
        {
            "source": "D4RL fixed offline RL benchmark and VIPER policy extraction, https://github.com/Farama-Foundation/D4RL and https://arxiv.org/abs/1805.08328",
            "method_family": "fixed replay dataset benchmark and decision-tree policy extraction",
            "model_mapping": "Agent52 借鉴 D4RL 固定数据集评测边界和 VIPER/决策树策略抽取思想，把 Agent49 的规则树放入 replay accuracy 审查。",
            "data_needs": "固定 replay 数据包、专家动作或人工复核标签、奖励分量、可解释规则、错误案例和回报差距。",
            "implementation_path": "输出 replay-ready schema、distilled_policy_replay_accuracy 和 rule_audit_findings；不把规则树当作已验证控制器。",
            "evaluation_metrics": [
                "distilled_policy_replay_accuracy",
                "rule_audit_findings",
                "false_positive_action_cost",
                "unsafe_action_block_rate",
            ],
            "failure_boundary": "基准和策略抽取只提供评估/解释框架；没有本项目现场 replay 时不能替代工程验收。",
        },
        {
            "source": "WaterTAP zero-order/unit-model and flowsheet documentation, https://watertap.readthedocs.io/ and https://github.com/watertap-org/watertap",
            "method_family": "unit model contracts, recovery/removal parameters and flowsheet constraints",
            "model_mapping": "Agent53 借鉴 WaterTAP 的单元模型、参数契约和约束组织方式，把反应去除、停留、氧化剂和成本约束从规则描述转成可审计字段。",
            "data_needs": "进出水水质、单元停留时间、回收/去除参数、药剂/能耗/成本、约束范围、现场校准标签。",
            "implementation_path": "先实现轻量 MinimalGreyBoxPhysicsAgent，不安装 WaterTAP；后续若进入高保真 flowsheet 再评估依赖引入。",
            "evaluation_metrics": [
                "mass_balance_residual",
                "grey_box_residual",
                "constraint_violation_rate",
                "field_calibration_coverage",
            ],
            "failure_boundary": "当前项目缺完整单元工艺参数和现场校准数据，不能把 WaterTAP 风格约束表述成实证机理。",
        },
        {
            "source": "QSDsan process modeling and system simulation, https://github.com/QSD-Group/QSDsan and https://qsdsan.readthedocs.io/",
            "method_family": "dynamic process/system modeling with TEA/LCA boundaries",
            "model_mapping": "Agent53/P7 借鉴 QSDsan 的系统仿真边界，把反应、能耗、成本、维护和可持续性指标作为后续 reward/约束候选。",
            "data_needs": "设备参数、运行规模、药剂库存、能耗、维护窗口、再生周期、排放/副产物风险。",
            "implementation_path": "当前只输出字段和残差指标；不把 QSDsan 作为运行依赖，避免复杂框架先于数据契约。",
            "evaluation_metrics": [
                "operating_cost_index",
                "energy_cost_index",
                "maintenance_window_feasibility",
                "sustainability_proxy",
            ],
            "failure_boundary": "没有真实 TEA/LCA 清单时只能作为模型字段设计参考，不能形成真实经济性结论。",
        },
        {
            "source": "Pyomo constraints, WaterTAP costing framework, EPA/WNTR hydraulic-operation documentation, https://pyomo.readthedocs.io/, https://watertap.readthedocs.io/, https://usepa.github.io/WNTR/",
            "method_family": "engineering constraints in objective/reward and final arbitration",
            "model_mapping": "P7 将池容、泵阀动作次数、执行器延迟、药剂库存、维护窗口、人工复核和误动作成本从说明文字转成 Agent49 reward 与 Arbitration 可消费的约束补丁。",
            "data_needs": "PLC/SCADA 点表、执行器响应日志、池容/液位、药剂库存、维护窗口、人工复核队列、operator override、field state-action-reward replay。",
            "implementation_path": "新增 Agent55 工程执行约束层，先输出 reward/arbitration patch；无 field execution replay 前不安装优化框架、不写执行器。",
            "evaluation_metrics": [
                "constraint_contract_score",
                "reward_patch_coverage",
                "arbitration_patch_coverage",
                "mean_execution_feasibility",
                "storage_violation_rate",
                "actuator_switch_pressure",
                "inventory_risk_score",
                "human_review_bottleneck_score",
            ],
            "failure_boundary": "没有 PLC/SCADA、SOP 和现场执行 replay 时，约束只能过滤/降级候选策略，不能证明现场最优或授权自动执行。",
        },
        {
            "source": "Photocatalytic/AOP degradation kinetics literature: pseudo-first-order and Langmuir-Hinshelwood-style rate expressions",
            "method_family": "minimal degradation kinetics and matrix inhibition prior",
            "model_mapping": "Agent53 用拟一级反应、基质抑制、催化剂有效活性和氧化剂项形成 k_eff，而不是继续只用黑箱状态跳转。",
            "data_needs": "目标污染物进出水浓度、氧化剂余量、催化剂活性/年龄、基质指标、温度、反应时间。",
            "implementation_path": "在 synthetic 阶段输出 k_eff、predicted_outlet_load、grey_box_residual 和 matrix_inhibition_factor；field 后再校准参数。",
            "evaluation_metrics": [
                "pseudo_first_order_k_per_min",
                "grey_box_residual",
                "matrix_inhibition_factor",
                "catalyst_decay_delta",
            ],
            "failure_boundary": "拟一级/L-H 只是一阶近似；多污染物、副产物和传质限制未校准前不能作为真实机理论证。",
        },
        {
            "source": "Residence-time distribution and hydraulic retention concepts in reactor/water-treatment modeling",
            "method_family": "RTD/HRT and short-circuit risk",
            "model_mapping": "Agent53 把 hydraulic_efficiency 转成 effective_retention_min 和 rtd_short_circuit_risk，用于解释循环结构为何能给低频传感争取时间。",
            "data_needs": "池容、流量、示踪/RTD、回流比、实际停留时间、短流/死区证据。",
            "implementation_path": "先用轻量 RTD proxy 审计停留时间是否足够；field 阶段要求 tracer 或等效 hydraulic replay。",
            "evaluation_metrics": [
                "effective_retention_min",
                "rtd_short_circuit_risk",
                "residence_time_error",
                "action_latency_margin",
            ],
            "failure_boundary": "没有真实池容/流量/示踪数据时，RTD 只能是先验风险项，不是水力实证结论。",
        },
    ]


def _model_core_goal_md() -> str:
    return "\n".join(
        [
            "# 全局 Goal：低成本传感循环式水处理智能灰箱闭环系统",
            "",
            "## 系统使命",
            "",
            "以复杂系统宏观架构师的视角，持续搭建、压实和演化“低成本传感循环式水处理智能灰箱闭环系统”的核心骨架。目标是高效形成一个能解释真实污染场景、能在低成本受限观测下行动、能被现场数据校准、能被证据链审查、能逐步工程化落地的系统架构。",
            "",
            "这个 goal 是全局性的系统目标，不绑定某个阶段、某个 agent 编号、某个当前问题或某次展示材料。阶段任务、具体模块、代码细节、文档和实验都只是系统演化中的自然产物；它们存在的理由，是让整体模型更清楚、更可信、更可控、更可落地。",
            "",
            "## 第一性原理",
            "",
            "1. 先搭骨架，再补细节：任何具体修复、agent、字段、测试或文档，都必须服务系统骨架，而不是让系统变得更碎。",
            "2. 先看全局闭环，再看局部模块：观测、推理、诊断、控制、验证、现场校准和失败边界必须构成闭环，不能只优化单点指标。",
            "3. 先定义接口，再扩展功能：每个模块都必须说明输入、输出、状态变量、证据来源、可传递指标、不能做什么，以及它与上下游的关系。",
            "4. 先保证可验证，再讨论智能化：没有 replay、field holdout、source_basis、失败边界和人工复核门的智能策略，只能是候选假设。",
            "5. 先追求系统可演化，再追求模块数量：agent 增多不是进步；能够合并、抽象、复用、回接主链、减少冗余，才是架构变强。",
            "",
            "## 核心系统骨架",
            "",
            "系统主链是：在低成本传感条件下，通过循环式水处理结构为观测、估计、诊断和控制争取时间；利用稀疏传感和软传感器估计不可直接观测的过程状态；再由知识库、灰箱机理和多智能体系统完成机理解释、故障诊断与闭环控制，动态决定是否回流、延长停留时间、调整药剂投加、预处理/切换单元或放行。",
            "",
            "这条主链要解决的不是一个单点算法问题，而是一个受限观测条件下的复杂系统治理问题：低成本传感导致信息不足，循环结构提供时间缓冲，软传感把黑箱变灰箱，机理证据约束智能判断，多智能体协作形成诊断与控制候选，现场验证和证据治理决定哪些结论能被升级、哪些必须保留为假设。",
            "",
            "系统骨架按七层组织：",
            "",
            "1. 现场对象层：污染物、水质基质、处理单元、管网/反应器拓扑、循环/暂存结构、药剂/催化剂/膜/生物单元。",
            "2. 观测层：低成本传感、稀疏布点、node-modality 矩阵、缺测/延迟/噪声、进出水与中间黑箱的有限可见性。",
            "3. 状态估计层：软传感器、灰箱过程状态、隐藏变量、催化剂活性、基质抑制、反应完成度、副产物/放行风险。",
            "4. 机理证据层：知识图谱、文献 source_basis、材料/污染物/工况关系、证据等级、失败边界。",
            "5. 诊断决策层：多智能体诊断、机制解释、故障识别、控制候选、策略蒸馏、人工复核。",
            "6. 闭环执行层：回流、延长停留、暂存等待、调整投药、切换单元、保护性阻断、release gate。",
            "7. 验证治理层：field package、replay、holdout、calibration、claim gate、架构复盘、阶段门控和证据治理。",
            "",
            "## 架构优先级",
            "",
            "当局部细节与系统骨架发生冲突时，永远优先系统骨架。判断一个工作是否值得做，不只看它是否解决了眼前 bug，而看它是否增强了以下能力之一：",
            "",
            "1. 可观测性：让黑箱更接近灰箱，提升关键隐藏状态的可估计性。",
            "2. 可控性：让系统能在低频、低成本、延迟观测下仍然选择可执行动作。",
            "3. 可解释性：让动作、诊断和失败边界能回到机制、证据或知识图谱路径。",
            "4. 可验证性：让 synthetic、literature、field、template 各自边界清楚，能进入 replay/holdout/gate。",
            "5. 可工程化：让数据采集、现场校准、人工复核、执行器约束和成本约束可落地。",
            "6. 可演化性：让 agent 链条可以合并、复用、模块化，而不是无限堆叠。",
            "",
            "## 永久约束",
            "",
            "1. 所有工作必须能映射到七层系统骨架之一，并说明它增强的是观测、状态估计、机理证据、诊断决策、闭环执行、验证治理或工程落地中的哪一项。",
            "2. 细节是自然发生的，但不能成为系统中心。若一个问题只产生局部修补、没有接口收益、没有指标收益、不能回接主链，应进入低优先级 backlog 或等待阶段复盘。",
            "3. synthetic/sample/template 数据只能作为仿真基线、接口验证或采集模板，不能表述为真实现场结论。",
            "4. 每个新模块必须说明输入契约、输出契约、方法来源、现实映射、数据需求、评价指标、失败边界、上游依赖和下游影响。",
            "5. 不盲目引入黑箱 MARL、大模型 agent 或复杂框架；必须先建立状态、动作、奖励、证据、失败边界和验证指标。",
            "6. agent 不是越多越好。新增 agent 前必须判断是否可以通过现有模块扩展、facade 合并、schema 回接或指标补丁完成；新增后必须说明它属于哪一层、解决哪条链路、是否可被未来合并。",
            "7. 治理中断采用阶段门控节流机制：它不是模仿用户的频繁打断，而是低频治理阀门。只有工作明显偏离系统骨架、硬性证据矛盾、把 synthetic/template 写成 field 结论，或绕过 field replay/保护边界时，才立即中断并回到架构层。",
            "8. 治理复盘本身也要节流：只有一个可验证小闭环完成、显式进入阶段边界、或出现硬风险时，才进行深度优先级重排；普通新想法先沉淀，不让系统被频繁上下文切换拖慢。",
            "",
            "## 系统设计不变量",
            "",
            "1. 任何控制建议都必须能追溯到观测状态、状态估计、机理证据和验证边界。",
            "2. 任何声称能够现场成立的结论，都必须通过真实数据、回放验证或人工复核门；否则只能是候选假设。",
            "3. 任何新增复杂度都必须换来更强的接口清晰度、证据链完整度、控制可执行性或验证能力。",
            "4. 任何模块都不能单独成为中心；中心永远是“低成本受限观测下的循环式水处理灰箱闭环系统”。",
            "5. 系统演化的理想方向是主链更短、接口更稳、证据更清楚、失败边界更诚实、现场落地路径更具体。",
            "",
            "## 架构师式执行方式",
            "",
            "每一轮工作先回答五个问题，再做细节实现：",
            "",
            "1. 它属于七层骨架中的哪一层，服务哪条主链？",
            "2. 它增强哪一种核心能力：可观测、可控、可解释、可验证、可工程化、可演化？",
            "3. 它新增或改变了什么接口、状态变量、证据边界、验证门或工程约束？",
            "4. 它是在减少系统碎片，还是只是在已有复杂度上继续堆叠？",
            "5. 它完成后，系统主链的下一步应该更清楚，还是更混乱？",
            "",
            "只有当答案能让系统骨架更清楚、更可验证、更可落地时，才继续深入细节。否则停止扩展，回到架构层重排。",
        ]
    )


def _goal_iteration_trace_md() -> str:
    return "\n".join(
        [
            "# Goal 十轮迭代收敛记录",
            "",
            "说明：这不是十个并列 goal，而是对同一全局 goal 的十轮抽象与去阶段化。最终版本保留在 `model_core_goal.md`。",
            "",
            "1. 去阶段化：删除对现阶段任务、agent 编号和当前 fallback 的中心化表达，让 goal 能长期适用。",
            "2. 定使命：把目标从“继续优化模型”提升为“构建可解释、可行动、可校准、可审查、可落地的复杂系统架构”。",
            "3. 定主链：把低成本传感、循环争取时间、软传感灰箱化、机理证据、多智能体诊断和闭环控制组织成一条系统主链。",
            "4. 定对象：把污染物、水质基质、处理单元、拓扑、循环结构和材料/药剂单元纳入现场对象层。",
            "5. 定层级：将系统拆成现场对象、观测、状态估计、机理证据、诊断决策、闭环执行、验证治理七层。",
            "6. 定能力：将工作价值压缩为六类能力：可观测、可控、可解释、可验证、可工程化、可演化。",
            "7. 定接口：要求每个模块说明输入、输出、状态变量、证据来源、可传递指标、失败边界和上下游影响。",
            "8. 定证据：明确 synthetic/sample/template/literature/field 的边界，防止仿真或模板被写成现场结论。",
            "9. 定演化：强调 agent 不是越多越好，系统应通过合并、抽象、复用、回接主链和减少冗余变强。",
            "10. 定执行：形成架构师式五问，保证每次细节实现都先回到全局骨架、核心能力、接口影响、复杂度收益和主链清晰度。",
        ]
    )


def _user_interrupt_lessons_md() -> str:
    return "\n".join(
        [
            "# 用户打断带来的工作方式修正",
            "",
            "## 已吸收的关键修正",
            "",
            "1. 卡点必须直接说明，不能自以为是补全。",
            "2. 展示材料不是核心；PPT、Word 和美化只在模型更新后同步。",
            "3. 循环结构不是口号，而是为了降低传感与反应速度要求，让低频、低成本、延迟检测条件下仍可行动。",
            "4. 黑箱问题的核心路径是软传感把黑箱变灰箱，再由多智能体诊断和闭环控制选择回流、停留、投药或放行。",
            "5. 管网布点、稀疏感知、多维向量/矩阵是核心，不应只停留在进水/出水两个点。",
            "6. 可借鉴污水系统多设施协同、共享经验池、奖励函数和决策树策略蒸馏，但不能机械套用泵站控制。",
            "7. 自我打断不能模仿用户的频繁纠偏；它应是阶段边界治理闸门，并带有复盘预算/冷却思路，避免每个新想法都造成上下文切换和算力摩擦。",
            "",
            "## 当前转化为 Agent50 的规则",
            "",
            "- presentation-only 且不改变模型指标时，`self_interrupt_verdict=interrupt_and_refocus`。",
            "- 模型核心内的新想法若尚未到阶段边界，只写入 `stage_boundary_deferred_backlog`；`self_interrupt_verdict` 仍保持 `continue_core_work`，`governance_review_gate` 也应为 `continue_current_micro_loop`，先完成当前小闭环。",
            "- 若量化阶段门已经进入外部等待态，`self_interrupt_verdict=stage_boundary_wait_for_external_activation`；这不是硬中断，而是停止内部扩张，只允许真实外部证据包或新的可测试核心接口恢复主链。",
            "- 只有当前小闭环完成、显式进入阶段边界、或出现硬风险时，才重跑 Agent50/Agent60；不要因为普通想法反复重算全局上下文。",
            "- Agent48/Agent49、catalyst_activity、灰箱物理、软传感矩阵和工程约束优先于展示层。",
            "- 外部方法必须先进入 evidence matrix，再决定是否实现或安装依赖。",
        ]
    )


def _evidence_matrix_md(records: list[dict[str, object]]) -> str:
    lines = [
        "# 外部方法 Evidence Matrix",
        "",
        "说明：本矩阵只作为方法借鉴和实现路径设计；除用户图片外，外部来源在 2026-06-01 已检查公开页面。所有记录都必须包含来源、现实映射、数据需求、实现路径、评价指标和失败边界。",
        "",
        "| 来源 | 方法族 | 可借鉴点 / 现实映射 | 数据需求 | 实现路径 | 评价指标 | 失败边界 |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for record in records:
        lines.append(
            "| {source} | {method_family} | {model_mapping} | {data_needs} | {implementation_path} | {metrics} | {failure_boundary} |".format(
                source=record["source"],
                method_family=record["method_family"],
                model_mapping=record["model_mapping"],
                data_needs=record["data_needs"],
                implementation_path=record["implementation_path"],
                metrics=", ".join(str(item) for item in record["evaluation_metrics"]),
                failure_boundary=record["failure_boundary"],
            )
        )
    return "\n".join(lines)


def _issue_priority_ranking_md(report) -> str:
    lines = [
        "# 当前问题优先级排序",
        "",
        f"- self_interrupt_verdict：`{report.metrics['self_interrupt_verdict']}`",
        f"- self_interrupt_reason：{report.metrics['self_interrupt_reason']}",
        f"- governance_review_gate：`{report.metrics['governance_review_gate']['decision']}`",
        f"- recommended_next_core_action：`{report.metrics['recommended_next_core_action']['task_id']}`",
        "",
        "| Rank | Task | Score | 下一步实验 | 指标 | 失败边界 |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for item in report.metrics["priority_ranking"]:
        lines.append(
            f"| {item['rank']} | `{item['task_id']}` {item['title']} | `{item['marginal_value_score']}` | "
            f"{item.get('next_experiment', '')} | {', '.join(str(metric) for metric in item.get('metrics', []))} | "
            f"{item.get('failure_boundary', '')} |"
        )
    lines.extend(["", "## 阻塞项", ""])
    for reason in report.metrics["blocked_reasons"]:
        lines.append(f"- {reason}")
    return "\n".join(lines)


def _execution_prompt_md() -> str:
    return "\n".join(
        [
            "# 后续 Codex / Agent 执行 Prompt",
            "",
            "你正在以复杂系统宏观架构师的视角推进“低成本传感循环式水处理智能灰箱闭环系统”。不要把工作理解为不断修补细节、增加 agent 或追逐阶段任务；细节和阶段任务只是系统演化的自然结果。先维护全局骨架，再选择最高边际价值的局部实现。除非到达阶段边界或出现硬风险，不要频繁重跑项目级治理。",
            "",
            "每次实现前先判断：",
            "",
            "1. 它属于现场对象、观测、状态估计、机理证据、诊断决策、闭环执行、验证治理七层中的哪一层？",
            "2. 它增强的是可观测性、可控性、可解释性、可验证性、可工程化还是可演化性？",
            "3. 它会怎样改变输入契约、输出契约、状态变量、证据边界、上游依赖和下游决策？",
            "4. 它是否能减少系统碎片，还是只是在已有复杂度上继续堆叠？",
            "5. 它会让系统主链更清楚，还是更混乱？",
            "",
            "每次实现必须满足：",
            "",
            "1. 说明该任务如何提升全局系统骨架，而不仅是解决单个细节。",
            "2. 使用 evidence matrix 中的来源作为方法启发，并说明现实映射与失败边界。",
            "3. 若涉及稀疏布点或低成本观测，必须更新 node-modality 矩阵、布点指标、弱目标覆盖和软传感接口。",
            "4. 若涉及催化剂活性、基质抑制、反应完成度等弱隐藏状态，必须设计可测试 proxy、离线标签需求、校准路径和失败边界。",
            "5. 若涉及协同控制或闭环决策，必须输出 state-action-reward-replay 契约、离线评估指标、策略解释/蒸馏结果和不可写执行器边界。",
            "6. 若新增 agent，必须说明它所在层级、上下游接口、能否未来合并，以及为什么现有 agent/facade 不足。",
            "7. synthetic 结论只写作仿真基线，不能写成现场结论。",
            "8. 完成后运行测试，更新 manifest、artifact index、iteration log 和 current_status。",
        ]
    )


def _self_interrupt_checklist_md() -> str:
    return "\n".join(
        [
            "# 低摩擦自我打断 Checklist",
            "",
            "自我打断不是模仿用户频繁纠偏，而是一个低频、高阈值、有节流的治理闸门。默认先完成当前可验证小闭环；普通新想法只登记到阶段边界 backlog，不改变当前 verdict，不重跑全局治理。",
            "",
            "## 立即打断条件",
            "",
            "只有出现以下情况，才立即 `interrupt_and_refocus`：",
            "",
            "- 当前工作是 PPT、Word、索引、格式或展示材料修饰，且没有改变任何模型指标、输入契约、输出契约、验证门或失败边界。",
            "- 当前实现与第一性原理发生硬冲突，例如放松执行器保护、绕过 field replay、把文献依据当成现场证据。",
            "- 当前实现把 synthetic/sample/template 数据写成 field-supported 结论，或让它进入执行器/release gate。",
            "- 测试或实验结果证明当前方向无效，继续做只会扩大错误。",
            "",
            "## 深度复盘准入条件",
            "",
            "只有出现以下情况，才允许重跑 Agent50/Agent60 做项目级优先级重排：",
            "",
            "- 当前可验证小闭环已经完成，例如代码、指标、测试和必要状态文件已经同步。",
            "- 显式进入阶段边界，需要统一比较 backlog 中的新想法。",
            "- 触发上面的立即打断条件。",
            "- 本轮仍有治理复盘预算；若预算耗尽，除硬风险外继续当前核心路径。",
            "",
            "## 阶段边界 Backlog 条件",
            "",
            "以下情况只写入 `stage_boundary_deferred_backlog`，不产生新的打断 verdict：",
            "",
            "- 出现一个可能更高边际价值的新想法，但当前小闭环还没完成。",
            "- 当前任务还在模型核心链路内，只是需要稍后比较它和新任务的边际价值。",
            "- 需要复盘 agent 冗余、命名、文件结构，但这些不影响当前模型验证。",
            "- 新问题需要大范围上下文加载，立即切换会增加摩擦。",
            "- 新问题有潜力，但不阻断当前 Agent 的输入契约、输出契约、指标或失败边界。",
            "",
            "## 外部激活等待条件",
            "",
            "若 `stage_decision=stop_expansion_wait_for_real_field_package_or_new_core_interface`，则 verdict 应为 `stage_boundary_wait_for_external_activation`：",
            "",
            "- 这不是 `interrupt_and_refocus`，因为当前工作没有发生展示漂移或证据硬冲突。",
            "- 这也不是 `continue_core_work`，因为继续堆叠内部 synthetic/template 产物会越过阶段边界。",
            "- 允许动作只包括提交真实外部证据包、正式检索结果包，或定义新的可测试核心接口。",
            "",
            "## 阶段边界检查",
            "",
            "每个可验证小闭环完成后，再集中检查：",
            "",
            "- 当前任务是否直接改变 Agent48/Agent49/软传感/灰箱物理/KG/工程约束之一？",
            "- 是否只是多写了一个 agent，却没有新增输入契约、输出契约、指标或失败边界？",
            "- 是否正在修 PPT、Word、索引、格式或展示材料，且没有模型指标变化？",
            "- synthetic 结果是否被写得像真实现场结论？",
            "- 是否引入了复杂方法但没有现实映射、数据需求和验证指标？",
            "- 是否存在更高边际价值缺口，例如 catalyst_activity 弱观测、布点不可解释、协同控制无 replay 或灰箱物理缺失？",
            "",
            "若触发立即打断条件，停止当前惯性工作。若只是 backlog 条件，先登记新问题，完成当前小闭环后再按阶段边界统一复盘；只有复盘结果真正改变模型优先级时，才重跑 Agent50/Agent60。若只是治理层反复确认“继续当前工作”，应直接继续实现，不再扩大上下文审计。",
        ]
    )


def _governance_report_md(report) -> str:
    recommended = report.metrics["recommended_next_core_action"]
    scorecard = report.metrics["governance_scorecard"]
    core_gate = report.metrics["quantified_core_score_gate"]
    activation_contract = report.metrics["external_activation_contract"]
    hidden_ledger = core_gate["hidden_state_coverage_ledger"]
    module_gate = core_gate["module_stage_termination_gate"]
    lines = [
        "# Agent50 模型核心优化治理报告",
        "",
        f"- summary：{report.summary}",
        f"- confidence：`{report.confidence}`",
        f"- self_interrupt_verdict：`{report.metrics['self_interrupt_verdict']}`",
        f"- self_interrupt_reason：{report.metrics['self_interrupt_reason']}",
        f"- self_interrupt_mode：`{report.metrics['self_interrupt_mode']}`",
        f"- governance_review_gate：`{report.metrics['governance_review_gate']['decision']}`",
        f"- governance_rerun_recommended：`{report.metrics['governance_review_gate']['governance_rerun_recommended']}`",
        f"- core_score：`{core_gate['core_score']}`",
        f"- iteration_validity_status：`{core_gate['iteration_validity_status']}`",
        f"- stage_decision：`{core_gate['stage_decision']}`",
        f"- evidence_matrix_status：`{report.metrics['evidence_matrix_status']['status']}`",
        f"- weak_state_coverage：`{scorecard['weak_state_coverage']}`",
        f"- catalyst_activity_observability：`{scorecard['catalyst_activity_observability']}`",
        f"- catalyst_proxy_status：`{scorecard['catalyst_proxy_status']}`",
        f"- catalyst_proxy_after_patch：`{scorecard['catalyst_proxy_after_patch']}`",
        f"- replay_evaluation_status：`{scorecard['replay_evaluation_status']}`",
        f"- replay_joint_action_accuracy：`{scorecard['replay_joint_action_accuracy']}`",
        f"- r7_submission_readiness_status：`{scorecard['r7_submission_readiness_status']}`",
        f"- r7_submission_highest_priority_blocker：`{scorecard['r7_submission_highest_priority_blocker']}`",
        f"- r7_submission_next_operator_action：`{scorecard['r7_submission_next_operator_action']}`",
        f"- r7_submission_blocking_stage_count：`{scorecard['r7_submission_blocking_stage_count']}`",
        f"- r7_submission_repair_work_order_status：`{scorecard['r7_submission_repair_work_order_status']}`",
        f"- r7_submission_repair_item_count：`{scorecard['r7_submission_repair_item_count']}`",
        f"- r7_submission_repair_work_order_path：`{scorecard['r7_submission_repair_work_order_path']}`",
        f"- r7_submission_repair_response_preflight_status：`{scorecard['r7_submission_repair_response_preflight_status']}`",
        f"- r7_submission_repair_response_can_route_to_r7_preflight：`{scorecard['r7_submission_repair_response_can_route_to_r7_preflight']}`",
        f"- external_activation_contract_status：`{scorecard['external_activation_contract_status']}`",
        f"- external_activation_ready：`{scorecard['external_activation_ready']}`",
        f"- external_activation_ready_channel_count：`{scorecard['external_activation_ready_channel_count']}`",
        f"- external_activation_blocked_channel_count：`{scorecard['external_activation_blocked_channel_count']}`",
        f"- external_activation_boundary_preserved：`{scorecard['external_activation_boundary_preserved']}`",
        f"- external_activation_router_status：`{scorecard['external_activation_router_status']}`",
        f"- external_activation_router_consumed：`{scorecard['external_activation_router_consumed']}`",
        f"- external_activation_router_routes：`{scorecard['external_activation_router_route_ready_count']} ready / {scorecard['external_activation_router_blocked_route_count']} blocked`",
        f"- external_activation_router_model_chain_ready_routes：`{scorecard['external_activation_router_model_chain_ready_route_count']}`",
        f"- external_activation_router_handoff_ready_routes：`{scorecard['external_activation_router_handoff_ready_route_count']}`",
        f"- external_activation_router_path_supplied_count：`{scorecard['external_activation_router_path_supplied_count']}`",
        f"- external_activation_router_boundary_preserved：`{scorecard['external_activation_router_boundary_preserved']}`",
        f"- external_activation_router_ready_channel_ids：`{scorecard['external_activation_router_ready_channel_ids']}`",
        f"- external_activation_router_model_chain_ready_channel_ids：`{scorecard['external_activation_router_model_chain_ready_channel_ids']}`",
        f"- external_activation_router_handoff_ready_channel_ids：`{scorecard['external_activation_router_handoff_ready_channel_ids']}`",
        f"- external_activation_router_blocked_channel_ids：`{scorecard['external_activation_router_blocked_channel_ids']}`",
        f"- external_activation_router_highest_priority_blocker：`{scorecard['external_activation_router_highest_priority_blocker']}`",
        f"- external_activation_router_next_operator_action：`{scorecard['external_activation_router_next_operator_action']}`",
        f"- external_activation_operator_action_packet_status：`{scorecard['external_activation_operator_action_packet_status']}`",
        f"- external_activation_operator_action_packet_target_hidden_state：`{scorecard['external_activation_operator_action_packet_target_hidden_state']}`",
        f"- external_activation_operator_action_packet_source_env_var：`{scorecard['external_activation_operator_action_packet_source_env_var']}`",
        (
            "- external_activation_operator_action_packet_focused_candidate_availability_status："
            f"`{scorecard['external_activation_operator_action_packet_focused_candidate_availability_status']}`"
        ),
        f"- external_activation_operator_action_packet_next_operator_action：`{scorecard['external_activation_operator_action_packet_next_operator_action']}`",
        f"- external_activation_operator_action_packet_boundary_pass：`{scorecard['external_activation_operator_action_packet_boundary_pass']}`",
        f"- field_activation_downstream_r7_preview_status：`{scorecard['field_activation_downstream_r7_preview_status']}`",
        f"- field_activation_downstream_r7_preview_executed：`{scorecard['field_activation_downstream_r7_preview_executed']}`",
        f"- field_activation_downstream_r7_preview_metric_evaluation_status：`{scorecard['field_activation_downstream_r7_preview_metric_evaluation_status']}`",
        f"- field_activation_downstream_r7_not_evaluated_metric_count：`{scorecard['field_activation_downstream_r7_not_evaluated_metric_count']}`",
        f"- field_activation_downstream_r7_agent44_import_status：`{scorecard['field_activation_downstream_r7_agent44_import_status']}`",
        f"- field_activation_downstream_r7_can_pass_to_timestamped_replay：`{scorecard['field_activation_downstream_r7_can_pass_to_timestamped_replay']}`",
        f"- field_activation_downstream_r7_highest_priority_blocker：`{scorecard['field_activation_downstream_r7_highest_priority_blocker']}`",
        f"- field_activation_downstream_r7_next_operator_action：`{scorecard['field_activation_downstream_r7_next_operator_action']}`",
        f"- field_activation_downstream_path_endpoint_preview_status：`{scorecard['field_activation_downstream_path_endpoint_preview_status']}`",
        f"- field_activation_downstream_path_endpoint_preview_executed：`{scorecard['field_activation_downstream_path_endpoint_preview_executed']}`",
        f"- field_activation_downstream_path_endpoint_preview_metric_evaluation_status：`{scorecard['field_activation_downstream_path_endpoint_preview_metric_evaluation_status']}`",
        f"- field_activation_downstream_path_endpoint_not_evaluated_metric_count：`{scorecard['field_activation_downstream_path_endpoint_not_evaluated_metric_count']}`",
        f"- field_activation_downstream_path_endpoint_preflight_status：`{scorecard['field_activation_downstream_path_endpoint_preflight_status']}`",
        f"- field_activation_downstream_path_endpoint_required_table_count：`{scorecard['field_activation_downstream_path_endpoint_required_table_count']}`",
        f"- field_activation_downstream_path_endpoint_contract_minimum_matched_batch_count：`{scorecard['field_activation_downstream_path_endpoint_contract_minimum_matched_batch_count']}`",
        f"- field_activation_downstream_path_endpoint_matched_batch_count：`{scorecard['field_activation_downstream_path_endpoint_matched_batch_count']}`",
        f"- field_activation_downstream_path_endpoint_required_matched_batch_deficit：`{scorecard['field_activation_downstream_path_endpoint_required_matched_batch_deficit']}`",
        f"- field_activation_downstream_path_endpoint_can_route_to_field_layout_holdout：`{scorecard['field_activation_downstream_path_endpoint_can_route_to_field_layout_holdout']}`",
        f"- field_activation_downstream_path_endpoint_highest_priority_blocker：`{scorecard['field_activation_downstream_path_endpoint_highest_priority_blocker']}`",
        f"- field_activation_downstream_path_endpoint_next_operator_action：`{scorecard['field_activation_downstream_path_endpoint_next_operator_action']}`",
        f"- field_activation_response_completion_ledger_status：`{scorecard['field_activation_response_completion_ledger_status']}`",
        f"- field_activation_response_completion_ratio：`{scorecard['field_activation_response_completion_ratio']}`",
        f"- field_activation_response_completed_row_count：`{scorecard['field_activation_response_completed_row_count']}`",
        f"- field_activation_response_incomplete_row_count：`{scorecard['field_activation_response_incomplete_row_count']}`",
        f"- field_activation_response_next_hidden_state_focus：`{scorecard['field_activation_response_next_hidden_state_focus']}`",
        f"- field_activation_response_completion_next_operator_action：`{scorecard['field_activation_response_completion_next_operator_action']}`",
        f"- field_activation_response_focus_handoff_status：`{scorecard['field_activation_response_focus_handoff_status']}`",
        f"- field_activation_response_focus_handoff_target_hidden_state：`{scorecard['field_activation_response_focus_handoff_target_hidden_state']}`",
        f"- field_activation_response_focus_handoff_row_scan_reduction_ratio：`{scorecard['field_activation_response_focus_handoff_row_scan_reduction_ratio']}`",
        f"- field_activation_response_focus_handoff_next_operator_action：`{scorecard['field_activation_response_focus_handoff_next_operator_action']}`",
        f"- field_activation_response_focus_handoff_source_env_var：`{scorecard['field_activation_response_focus_handoff_source_env_var']}`",
        f"- field_path_endpoint_label_preflight_status：`{scorecard['field_path_endpoint_label_preflight_status']}`",
        f"- field_path_endpoint_matched_batch_count：`{scorecard['field_path_endpoint_matched_batch_count']}`",
        f"- field_path_endpoint_required_matched_batch_deficit：`{scorecard['field_path_endpoint_required_matched_batch_deficit']}`",
        f"- field_path_endpoint_batch_alignment_gap_count：`{scorecard['field_path_endpoint_batch_alignment_gap_count']}`",
        f"- field_path_endpoint_alignment_patch_plan_status：`{scorecard['field_path_endpoint_alignment_patch_plan_status']}`",
        f"- field_path_endpoint_alignment_patch_plan_item_count：`{scorecard['field_path_endpoint_alignment_patch_plan_item_count']}`",
        f"- field_path_endpoint_label_package_ready：`{scorecard['field_path_endpoint_label_package_ready']}`",
        f"- can_route_to_field_layout_holdout_with_path_labels：`{scorecard['can_route_to_field_layout_holdout_with_path_labels']}`",
        f"- release_gate_endpoint_label_blocked：`{scorecard['release_gate_endpoint_label_blocked']}`",
        f"- formal_search_execution_route_plan_status：`{scorecard['formal_search_execution_route_plan_status']}`",
        f"- formal_search_execution_route_rows：`{scorecard['formal_search_execution_complete_route_row_count']} / {scorecard['formal_search_execution_route_row_count']}`",
        f"- formal_search_execution_mapped_seed_route_count：`{scorecard['formal_search_execution_mapped_seed_route_count']}`",
        f"- formal_search_execution_operator_first_action：`{scorecard['formal_search_execution_operator_first_action']}`",
        f"- formal_search_execution_boundary_preserved：`{scorecard['formal_search_execution_boundary_preserved']}`",
        f"- formal_search_ai_nonlegal_review_brief_status：`{scorecard['formal_search_ai_nonlegal_review_brief_status']}`",
        f"- formal_search_ai_nonlegal_review_brief_rows：`{scorecard['formal_search_ai_nonlegal_review_brief_row_count']}`",
        f"- formal_search_ai_nonlegal_review_brief_missing_source_rows：`{scorecard['formal_search_ai_nonlegal_review_brief_missing_source_row_count']}`",
        f"- formal_search_ai_nonlegal_review_brief_missing_claim_mapping_rows：`{scorecard['formal_search_ai_nonlegal_review_brief_missing_claim_mapping_row_count']}`",
        f"- formal_search_ai_nonlegal_review_brief_can_help_human_review：`{scorecard['formal_search_ai_nonlegal_review_brief_can_help_human_review']}`",
        f"- formal_search_ai_nonlegal_review_brief_can_route_to_claim_scope_patch_draft：`{scorecard['formal_search_ai_nonlegal_review_brief_can_route_to_claim_scope_patch_draft']}`",
        f"- formal_search_ai_nonlegal_review_brief_boundary_preserved：`{scorecard['formal_search_ai_nonlegal_review_brief_boundary_preserved']}`",
        f"- formal_search_ai_nonlegal_review_brief_next_operator_action：`{scorecard['formal_search_ai_nonlegal_review_brief_next_operator_action']}`",
        f"- formal_search_nonlegal_review_operator_packet_status：`{scorecard['formal_search_nonlegal_review_operator_packet_status']}`",
        f"- formal_search_nonlegal_review_operator_packet_expected_rows：`{scorecard['formal_search_nonlegal_review_operator_packet_expected_review_packet_row_count']}`",
        f"- formal_search_nonlegal_review_operator_packet_high_priority_rows：`{scorecard['formal_search_nonlegal_review_operator_packet_high_priority_review_row_count']}`",
        f"- formal_search_nonlegal_review_operator_packet_accepted_rows：`{scorecard['formal_search_nonlegal_review_operator_packet_accepted_review_row_count']}`",
        f"- formal_search_nonlegal_review_operator_packet_source_env_var：`{scorecard['formal_search_nonlegal_review_operator_packet_source_env_var']}`",
        f"- formal_search_nonlegal_review_operator_packet_can_route_to_claim_scope_patch_draft：`{scorecard['formal_search_nonlegal_review_operator_packet_can_route_to_claim_scope_patch_draft']}`",
        f"- formal_search_nonlegal_review_operator_packet_boundary_preserved：`{scorecard['formal_search_nonlegal_review_operator_packet_boundary_preserved']}`",
        f"- formal_search_nonlegal_review_operator_packet_next_operator_action：`{scorecard['formal_search_nonlegal_review_operator_packet_next_operator_action']}`",
        "",
        "## External Activation Contract",
        "",
        f"- contract_id：`{activation_contract['contract_id']}`",
        f"- contract_status：`{activation_contract['contract_status']}`",
        f"- architecture_layer：`{activation_contract['architecture_layer']}`",
        f"- enhanced_abilities：`{activation_contract['enhanced_abilities']}`",
        f"- activation_ready：`{activation_contract['activation_ready']}`",
        f"- ready_channel_count：`{activation_contract['ready_channel_count']}`",
        f"- handoff_ready_channel_count：`{activation_contract['handoff_ready_channel_count']}`",
        f"- blocked_channel_count：`{activation_contract['blocked_channel_count']}`",
        f"- boundary_preserved：`{activation_contract['boundary_preserved']}`",
        f"- global_no_write_boundary：{activation_contract['global_no_write_boundary']}",
        "",
        "| 通道 | 当前状态 | 提交入口 | 可恢复主链 | 下一步动作 |",
        "| --- | --- | --- | --- | --- |",
    ]
    for channel in activation_contract["channels"]:
        lines.append(
            "| "
            f"{channel['channel_id']} | "
            f"{channel['current_status']} | "
            f"{channel['package_pointer']} | "
            f"{channel['can_resume_model_chain']} | "
            f"{channel['next_operator_action']} |"
        )
    lines.extend(
        [
            "",
            "## External Activation Router Route Summary",
            "",
            "| 通道 | 路由状态 | 已提交 | 可路由 | 预检状态 | 阻断原因 | 下一步 |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in scorecard["external_activation_router_route_summary"]:
        lines.append(
            "| "
            f"{row['channel_id']} | "
            f"{row['route_status']} | "
            f"{row['path_supplied']} | "
            f"{row['route_ready']} | "
            f"{row['preflight_status']} | "
            f"{row['blocked_reason']} | "
            f"{row['operator_action']} |"
        )
    lines.extend(
        [
            "",
            "## 推荐下一步",
            "",
            f"- `{recommended['task_id']}`：{recommended['title']}",
            f"- 下一步实验：{recommended['next_experiment']}",
            f"- 指标：{recommended['metrics']}",
            f"- 失败边界：{recommended['failure_boundary']}",
            "",
        ]
    )
    lines.extend(
        [
            "## 量化终止 Gate",
            "",
            f"- gate_id：`{core_gate['gate_id']}`",
            f"- core_score_formula：`{core_gate['core_score_formula']}`",
            f"- previous_core_score：`{core_gate['previous_core_score']}`",
            f"- iteration_delta：`{core_gate['iteration_delta']}`",
            f"- hard_blocker_resolved：`{core_gate['hard_blocker_resolved']}`",
            f"- changed_contract_or_gate：`{core_gate['changed_contract_or_gate']}`",
            f"- evidence_boundary_preserved：`{core_gate['evidence_boundary_preserved']}`",
            f"- targeted_tests_passed：`{core_gate['targeted_tests_passed']}`",
            f"- continue_expansion_allowed：`{core_gate['continue_expansion_allowed']}`",
            f"- next_gate_action：{core_gate['next_gate_action']}",
            "",
            "### 隐藏状态分层覆盖",
            "",
            f"- state_variable_contract_coverage：`{hidden_ledger['state_variable_contract_coverage']}`",
            f"- sparse_estimation_ready_coverage：`{hidden_ledger['sparse_estimation_ready_coverage']}`",
            f"- design_or_patch_ready_coverage：`{hidden_ledger['design_or_patch_ready_coverage']}`",
            f"- field_validated_state_coverage：`{hidden_ledger['field_validated_state_coverage']}`",
            f"- control_ready_state_coverage：`{hidden_ledger['control_ready_state_coverage']}`",
            f"- field_validation_blockers：`{hidden_ledger['field_validation_blockers']}`",
            f"- control_readiness_blockers：`{hidden_ledger['control_readiness_blockers']}`",
            f"- termination_boundary：{hidden_ledger['termination_boundary']}",
            "",
            "| 隐藏状态 | 契约覆盖 | 软传感可估计 | 补丁/代理设计 | 现场验证 | 控制可用 | 阶段 |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in hidden_ledger["state_rows"]:
        lines.append(
            f"| `{row['hidden_state']}` | `{row['contract_covered']}` | `{row['sparse_estimation_ready']}` | "
            f"`{row['design_or_patch_ready']}` | `{row['field_validated']}` | `{row['control_ready']}` | "
            f"`{row['coverage_stage']}` |"
        )
    lines.extend(
        [
            "",
            "| 能力 | 分数 | 权重 |",
            "| --- | --- | --- |",
        ]
    )
    for ability, score in core_gate["ability_scores"].items():
        lines.append(f"| {ability} | `{score}` | `{core_gate['ability_weights'][ability]}` |")
    lines.extend(
        [
            "",
            "### 模块阶段门",
            "",
            f"- module_stage_status：`{module_gate['module_stage_status']}`",
            f"- can_stop_current_module_expansion：`{module_gate['can_stop_current_module_expansion']}`",
            f"- blockers：`{module_gate['blockers']}`",
            f"- supporting_state_metrics：`{module_gate['supporting_state_metrics']}`",
            f"- termination_meaning：{module_gate['termination_meaning']}",
            "",
        ]
    )
    lines.extend([
        "## 治理原则",
        "",
    ])
    for item in report.metrics["governance_principles"]:
        lines.append(f"- {item}")
    lines.extend(["", "## 风险边界", ""])
    for issue in report.issues:
        lines.append(f"- `{issue.issue_type}`：{issue.message}")
    lines.extend(["", "## 结论", ""])
    lines.extend(f"- {rec}" for rec in report.recommendations)
    return "\n".join(lines)


def _agent50_report_md(
    report,
    generated_files: dict[str, str],
    external_package_readiness_board: dict[str, Any],
    external_package_operator_action_packet: dict[str, Any],
    external_package_acquisition_maturity_gate: dict[str, Any],
    core_interface_consolidation: dict[str, Any],
    grey_box_submission_readiness_gate: dict[str, Any],
) -> str:
    core_gate = report.metrics["quantified_core_score_gate"]
    activation_contract = report.metrics["external_activation_contract"]
    external_package_summary = external_package_readiness_board["package_summary"]
    external_package_packet_status = external_package_operator_action_packet["packet_status"]
    external_package_acquisition_gate = external_package_acquisition_maturity_gate
    core_interface_priority = core_interface_consolidation["priority_decision"]
    core_interface_facades = core_interface_consolidation["facades"]
    grey_box_submission_status = grey_box_submission_readiness_gate.get(
        "gate_status",
        "grey_box_submission_readiness_gate_not_consumed_by_agent50",
    )
    grey_box_submission_score = grey_box_submission_readiness_gate.get("readiness_score", 0.0)
    grey_box_submission_gap = grey_box_submission_readiness_gate.get(
        "highest_priority_gap",
        {"gap_type": "not_consumed", "table": ""},
    )
    hidden_ledger = core_gate["hidden_state_coverage_ledger"]
    lines = [
        "# Agent 50 模型核心优化治理运行报告",
        "",
        f"- summary: {report.summary}",
        f"- self_interrupt_verdict: `{report.metrics['self_interrupt_verdict']}`",
        f"- self_interrupt_reason: {report.metrics['self_interrupt_reason']}",
        f"- governance_review_gate: `{report.metrics['governance_review_gate']['decision']}`",
        f"- governance_rerun_recommended: `{report.metrics['governance_review_gate']['governance_rerun_recommended']}`",
        f"- core_score: `{core_gate['core_score']}`",
        f"- iteration_validity_status: `{core_gate['iteration_validity_status']}`",
        f"- stage_decision: `{core_gate['stage_decision']}`",
        f"- recommended_next_core_action: `{report.metrics['recommended_next_core_action']['task_id']}`",
        f"- external_activation_contract_status: `{activation_contract['contract_status']}`",
        f"- external_activation_ready: `{activation_contract['activation_ready']}`",
        f"- external_activation_channels: `{activation_contract['ready_channel_count']} ready / {activation_contract['blocked_channel_count']} blocked`",
        f"- external_activation_boundary_preserved: `{activation_contract['boundary_preserved']}`",
        f"- external_activation_router_status: `{report.metrics['governance_scorecard']['external_activation_router_status']}`",
        f"- external_activation_router_routes: `{report.metrics['governance_scorecard']['external_activation_router_route_ready_count']} ready / {report.metrics['governance_scorecard']['external_activation_router_blocked_route_count']} blocked`",
        f"- external_activation_router_model_chain_ready_routes: `{report.metrics['governance_scorecard']['external_activation_router_model_chain_ready_route_count']}`",
        f"- external_activation_router_handoff_ready_routes: `{report.metrics['governance_scorecard']['external_activation_router_handoff_ready_route_count']}`",
        f"- external_activation_router_highest_priority_blocker: `{report.metrics['governance_scorecard']['external_activation_router_highest_priority_blocker']}`",
        f"- external_activation_router_next_operator_action: `{report.metrics['governance_scorecard']['external_activation_router_next_operator_action']}`",
        (
            "- external_activation_operator_action_packet_status: "
            f"`{report.metrics['governance_scorecard']['external_activation_operator_action_packet_status']}`"
        ),
        (
            "- external_activation_operator_action_packet_next_operator_action: "
            f"`{report.metrics['governance_scorecard']['external_activation_operator_action_packet_next_operator_action']}`"
        ),
        (
            "- external_activation_operator_action_packet_focused_candidate_availability_status: "
            f"`{report.metrics['governance_scorecard']['external_activation_operator_action_packet_focused_candidate_availability_status']}`"
        ),
        (
            "- external_activation_operator_action_packet_boundary_pass: "
            f"`{report.metrics['governance_scorecard']['external_activation_operator_action_packet_boundary_pass']}`"
        ),
        (
            "- external_activation_router_catalyst_patch_candidate_status: "
            f"`{report.metrics['governance_scorecard']['external_activation_router_catalyst_patch_candidate_status']}`"
        ),
        (
            "- external_activation_router_catalyst_patch_candidate_can_submit_as_REAL_FIELD_REPLAY_PACKAGE_DIR: "
            f"`{report.metrics['governance_scorecard']['external_activation_router_catalyst_patch_candidate_can_submit_as_REAL_FIELD_REPLAY_PACKAGE_DIR']}`"
        ),
        (
            "- formal_search_ai_nonlegal_review_brief_status: "
            f"`{report.metrics['governance_scorecard']['formal_search_ai_nonlegal_review_brief_status']}`"
        ),
        (
            "- formal_search_ai_nonlegal_review_brief_can_help_human_review: "
            f"`{report.metrics['governance_scorecard']['formal_search_ai_nonlegal_review_brief_can_help_human_review']}`"
        ),
        (
            "- formal_search_ai_nonlegal_review_brief_can_route_to_claim_scope_patch_draft: "
            f"`{report.metrics['governance_scorecard']['formal_search_ai_nonlegal_review_brief_can_route_to_claim_scope_patch_draft']}`"
        ),
        (
            "- formal_search_nonlegal_review_operator_packet_status: "
            f"`{report.metrics['governance_scorecard']['formal_search_nonlegal_review_operator_packet_status']}`"
        ),
        (
            "- formal_search_nonlegal_review_operator_packet_expected_rows: "
            f"`{report.metrics['governance_scorecard']['formal_search_nonlegal_review_operator_packet_expected_review_packet_row_count']}`"
        ),
        (
            "- formal_search_nonlegal_review_operator_packet_source_env_var: "
            f"`{report.metrics['governance_scorecard']['formal_search_nonlegal_review_operator_packet_source_env_var']}`"
        ),
        (
            "- formal_search_nonlegal_review_operator_packet_can_route_to_claim_scope_patch_draft: "
            f"`{report.metrics['governance_scorecard']['formal_search_nonlegal_review_operator_packet_can_route_to_claim_scope_patch_draft']}`"
        ),
        (
            "- external_activation_router_catalyst_patch_candidate_remaining_gap_count: "
            f"`{report.metrics['governance_scorecard']['external_activation_router_catalyst_patch_candidate_remaining_gap_count']}`"
        ),
        (
            "- external_activation_router_field_activation_upstream_status: "
            f"`{report.metrics['governance_scorecard']['external_activation_router_field_activation_upstream_status']}`"
        ),
        (
            "- external_activation_router_field_activation_upstream_next_operator_action: "
            f"`{report.metrics['governance_scorecard']['external_activation_router_field_activation_upstream_next_operator_action']}`"
        ),
        (
            "- external_activation_router_field_activation_upstream_can_submit_to_external_activation_router: "
            f"`{report.metrics['governance_scorecard']['external_activation_router_field_activation_upstream_can_submit_to_external_activation_router']}`"
        ),
        (
            "- field_activation_response_completion_ledger_status: "
            f"`{report.metrics['governance_scorecard']['field_activation_response_completion_ledger_status']}`"
        ),
        (
            "- field_activation_response_completion_ratio: "
            f"`{report.metrics['governance_scorecard']['field_activation_response_completion_ratio']}`"
        ),
        (
            "- field_activation_response_next_hidden_state_focus: "
            f"`{report.metrics['governance_scorecard']['field_activation_response_next_hidden_state_focus']}`"
        ),
        (
            "- field_activation_response_focus_handoff_status: "
            f"`{report.metrics['governance_scorecard']['field_activation_response_focus_handoff_status']}`"
        ),
        (
            "- field_activation_response_focus_handoff_target_hidden_state: "
            f"`{report.metrics['governance_scorecard']['field_activation_response_focus_handoff_target_hidden_state']}`"
        ),
        (
            "- field_activation_response_focus_handoff_next_operator_action: "
            f"`{report.metrics['governance_scorecard']['field_activation_response_focus_handoff_next_operator_action']}`"
        ),
        (
            "- external_package_readiness_board_packages: "
            f"`{external_package_summary['package_count']}` total / "
            f"`{external_package_summary['ready_package_count']}` ready / "
            f"`{external_package_summary['waiting_package_count']}` waiting / "
            f"`{external_package_summary['blocked_package_count']}` blocked"
        ),
        (
            "- external_package_readiness_board_next_operator_source_env_var: "
            f"`{external_package_summary['next_operator_source_env_var']}`"
        ),
        (
            "- external_package_readiness_board_next_operator_action: "
            f"`{external_package_summary['next_operator_action']}`"
        ),
        (
            "- external_package_readiness_board_boundary: "
            f"field_evidence=`{external_package_summary['can_generate_field_evidence']}`, "
            f"actuator=`{external_package_summary['can_write_to_actuator']}`, "
            f"release_gate=`{external_package_summary['can_write_to_release_gate']}`"
        ),
        (
            "- external_package_operator_action_packet_status: "
            f"`{external_package_packet_status}`"
        ),
        (
            "- external_package_operator_action_packet_next_operator_source_env_var: "
            f"`{external_package_operator_action_packet['next_operator_source_env_var']}`"
        ),
        (
            "- external_package_operator_action_packet_next_operator_validation_command: "
            f"`{external_package_operator_action_packet['next_operator_validation_command']}`"
        ),
        (
            "- external_package_acquisition_maturity_gate_status: "
            f"`{external_package_acquisition_gate['gate_status']}`"
        ),
        (
            "- external_package_acquisition_maturity_score: "
            f"`{external_package_acquisition_gate['acquisition_maturity_score']}`"
        ),
        (
            "- external_package_acquisition_field_package_ready_rate: "
            f"`{external_package_acquisition_gate['field_package_ready_rate']}`"
        ),
        (
            "- external_package_acquisition_interface_preflight_coverage: "
            f"`{external_package_acquisition_gate['interface_preflight_coverage']}`"
        ),
        (
            "- external_package_acquisition_operator_action_contract_coverage: "
            f"`{external_package_acquisition_gate['operator_action_contract_coverage']}`"
        ),
        (
            "- external_package_acquisition_no_write_boundary_integrity: "
            f"`{external_package_acquisition_gate['no_write_boundary_integrity']}`"
        ),
        (
            "- external_package_acquisition_contract_termination_status: "
            f"`{external_package_acquisition_gate['contract_termination_status']}`"
        ),
        (
            "- external_package_acquisition_module_stage_termination_pass: "
            f"`{external_package_acquisition_gate['module_stage_termination_pass']}`"
        ),
        (
            "- external_package_acquisition_termination_blockers: "
            f"`{external_package_acquisition_gate['termination_blockers']}`"
        ),
        (
            "- external_package_acquisition_next_stage_decision: "
            f"`{external_package_acquisition_gate['next_stage_decision']}`"
        ),
        (
            "- external_package_acquisition_next_operator_source_env_var: "
            f"`{external_package_acquisition_gate['next_operator_source_env_var']}`"
        ),
        (
            "- external_package_acquisition_boundary: "
            f"field_evidence=`{external_package_acquisition_gate['can_generate_field_evidence']}`, "
            f"model_chain=`{external_package_acquisition_gate['can_resume_model_chain']}`, "
            f"actuator=`{external_package_acquisition_gate['can_write_to_actuator']}`, "
            f"release_gate=`{external_package_acquisition_gate['can_write_to_release_gate']}`"
        ),
        (
            "- core_interface_consolidation_id: "
            f"`{core_interface_consolidation['consolidation_id']}`"
        ),
        "- core_interface_consolidation_consumed_by_agent50: `True`",
        "- core_interface_consolidation_refresh_status: `agent50_runner_refreshed_current_facade`",
        (
            "- core_interface_consolidation_refreshed_by_runner: "
            "`experiments/run_agent50_model_core_governance.py`"
        ),
        (
            "- core_interface_consolidation_top_external_action_env_var: "
            f"`{core_interface_priority['top_external_action_env_var']}`"
        ),
        (
            "- core_interface_consolidation_new_agent_recommendation: "
            f"`{core_interface_priority['new_agent_recommendation']}`"
        ),
        (
            "- core_interface_external_lifecycle_status: "
            f"`{core_interface_facades['external_package_lifecycle']['facade_status']}`"
        ),
        (
            "- core_interface_sparse_benchmark_status: "
            f"`{core_interface_facades['sparse_layout_soft_sensor_coupling_benchmark']['benchmark_status']}`"
        ),
        (
            "- core_interface_control_crosswalk_status: "
            f"`{core_interface_facades['field_control_replay_crosswalk']['crosswalk_status']}`"
        ),
        (
            "- grey_box_submission_readiness_gate_status: "
            f"`{grey_box_submission_status}`"
        ),
        (
            "- grey_box_submission_readiness_score: "
            f"`{grey_box_submission_score}`"
        ),
        (
            "- grey_box_submission_readiness_highest_priority_gap: "
            f"`{grey_box_submission_gap.get('gap_type', '')}` / `{grey_box_submission_gap.get('table', '')}`"
        ),
        "",
        "## Hidden State Coverage Ledger",
        "",
        f"- state_variable_contract_coverage: `{hidden_ledger['state_variable_contract_coverage']}`",
        f"- sparse_estimation_ready_coverage: `{hidden_ledger['sparse_estimation_ready_coverage']}`",
        f"- design_or_patch_ready_coverage: `{hidden_ledger['design_or_patch_ready_coverage']}`",
        f"- field_validated_state_coverage: `{hidden_ledger['field_validated_state_coverage']}`",
        f"- control_ready_state_coverage: `{hidden_ledger['control_ready_state_coverage']}`",
        f"- boundary: {hidden_ledger['termination_boundary']}",
        "",
        "## 生成文件",
        "",
    ]
    for key, path in generated_files.items():
        lines.append(f"- {key}: `{path}`")
    lines.extend(["", "## Top Priority", ""])
    for item in report.metrics["priority_ranking"][:5]:
        lines.append(
            f"- Rank {item['rank']} `{item['task_id']}` score={item['marginal_value_score']}：{item['next_experiment']}"
        )
    return "\n".join(lines)


def _agent50_payload(
    report,
    generated_files: dict[str, str],
    evidence_matrix: list[dict[str, object]],
    external_package_readiness_board: dict[str, Any],
    external_package_operator_action_packet: dict[str, Any],
    external_package_acquisition_maturity_gate: dict[str, Any],
    core_interface_consolidation: dict[str, Any],
    grey_box_submission_readiness_gate: dict[str, Any],
) -> dict[str, object]:
    return {
        "model_core_optimization_governance": {
            "agent_name": report.agent_name,
            "confidence": report.confidence,
            "summary": report.summary,
            "recommendations": report.recommendations,
            "metrics": report.metrics,
            "issues": [
                {
                    "sensor": issue.sensor,
                    "issue_type": issue.issue_type,
                    "severity": issue.severity.value,
                    "message": issue.message,
                    "evidence": issue.evidence,
                }
                for issue in report.issues
            ],
        },
        "external_package_readiness_board": external_package_readiness_board,
        "external_package_operator_action_packet": external_package_operator_action_packet,
        "external_package_acquisition_maturity_gate": external_package_acquisition_maturity_gate,
        "core_interface_consolidation": core_interface_consolidation,
        "grey_box_submission_readiness_gate": grey_box_submission_readiness_gate,
        "core_interface_consolidation_refresh": {
            "consumed_by_agent50": True,
            "refresh_status": "agent50_runner_refreshed_current_facade",
            "refreshed_by_runner": "experiments/run_agent50_model_core_governance.py",
            "source_facade_id": core_interface_consolidation["consolidation_id"],
        },
        "external_evidence_matrix": evidence_matrix,
        "catalyst_proxy_metrics_path": str(CATALYST_PROXY_METRICS_PATH),
        "replay_evaluation_metrics_path": str(REPLAY_EVALUATION_METRICS_PATH),
        "field_path_endpoint_label_preflight_path": str(FIELD_PATH_ENDPOINT_LABEL_PREFLIGHT_PATH),
        "formal_search_execution_route_plan_path": str(FORMAL_SEARCH_EXECUTION_ROUTE_PLAN_PATH),
        "formal_search_ai_nonlegal_review_brief_path": str(
            FORMAL_SEARCH_AI_NONLEGAL_REVIEW_BRIEF_PATH
        ),
        "formal_search_nonlegal_review_operator_packet_path": str(
            FORMAL_SEARCH_NONLEGAL_REVIEW_OPERATOR_PACKET_PATH
        ),
        "external_activation_router_path": str(EXTERNAL_ACTIVATION_ROUTER_PATH),
        "field_activation_matrix_path": str(FIELD_ACTIVATION_MATRIX_PATH),
        "stage_boundary_external_action_board_path": str(
            STAGE_BOUNDARY_EXTERNAL_ACTION_BOARD_PATH
        ),
        "stage_boundary_external_action_board_report_path": str(
            STAGE_BOUNDARY_EXTERNAL_ACTION_BOARD_REPORT_PATH
        ),
        "external_package_readiness_board_path": str(
            EXTERNAL_PACKAGE_READINESS_BOARD_PATH
        ),
        "external_package_readiness_board_report_path": str(
            EXTERNAL_PACKAGE_READINESS_BOARD_REPORT_PATH
        ),
        "external_package_operator_action_packet_path": str(
            EXTERNAL_PACKAGE_OPERATOR_ACTION_PACKET_PATH
        ),
        "external_package_operator_action_packet_report_path": str(
            EXTERNAL_PACKAGE_OPERATOR_ACTION_PACKET_REPORT_PATH
        ),
        "external_package_acquisition_maturity_gate_path": str(
            EXTERNAL_PACKAGE_ACQUISITION_MATURITY_GATE_PATH
        ),
        "external_package_acquisition_maturity_gate_report_path": str(
            EXTERNAL_PACKAGE_ACQUISITION_MATURITY_GATE_REPORT_PATH
        ),
        "core_interface_consolidation_path": str(CORE_INTERFACE_CONSOLIDATION_PATH),
        "core_interface_consolidation_report_path": str(CORE_INTERFACE_CONSOLIDATION_REPORT_PATH),
        "grey_box_calibration_collection_work_order_path": str(
            GREY_BOX_CALIBRATION_COLLECTION_WORK_ORDER_PATH
        ),
        "grey_box_calibration_collection_work_order_report_path": str(
            GREY_BOX_CALIBRATION_COLLECTION_WORK_ORDER_REPORT_PATH
        ),
        "grey_box_submission_readiness_gate_path": str(
            GREY_BOX_SUBMISSION_READINESS_GATE_PATH
        ),
        "grey_box_submission_readiness_gate_report_path": str(
            GREY_BOX_SUBMISSION_READINESS_GATE_REPORT_PATH
        ),
        "observation_response_bridge_path": str(OBSERVATION_RESPONSE_BRIDGE_METRICS_PATH),
        "catalyst_evidence_response_gate_path": str(CATALYST_EVIDENCE_RESPONSE_GATE_METRICS_PATH),
        "catalyst_response_submission_kit_path": str(CATALYST_RESPONSE_SUBMISSION_KIT_METRICS_PATH),
        "focused_catalyst_response_merge_preflight_path": str(FOCUSED_CATALYST_RESPONSE_MERGE_PREFLIGHT_PATH),
        "generated_files": generated_files,
    }


def _attach_external_package_acquisition_stage_gate(
    report,
    external_package_acquisition_maturity_gate: dict[str, Any],
) -> None:
    snapshot = _external_package_acquisition_stage_gate_snapshot(
        external_package_acquisition_maturity_gate,
    )
    report.metrics["external_package_acquisition_stage_gate"] = snapshot
    core_gate = report.metrics["quantified_core_score_gate"]
    core_gate["external_package_acquisition_stage_gate"] = snapshot
    resume_conditions = core_gate.setdefault("external_resume_conditions", {})
    resume_conditions["external_package_acquisition_stage_gate"] = snapshot
    new_core_interface = resume_conditions.setdefault("new_core_interface", {})
    for key in [
        "contract_termination_status",
        "module_stage_termination_pass",
        "termination_blockers",
        "downstream_reconnection_rate",
        "field_package_ready_rate",
        "next_operator_source_env_var",
        "next_operator_validation_command",
    ]:
        new_core_interface[f"external_package_acquisition_{key}"] = snapshot[key]


def _external_package_acquisition_stage_gate_snapshot(
    gate: dict[str, Any],
) -> dict[str, Any]:
    return {
        "gate_id": gate.get("gate_id", ""),
        "gate_status": gate.get("gate_status", ""),
        "contract_termination_status": gate.get("contract_termination_status", ""),
        "module_stage_termination_pass": bool(gate.get("module_stage_termination_pass", False)),
        "termination_blockers": list(gate.get("termination_blockers", []))
        if isinstance(gate.get("termination_blockers"), list)
        else [],
        "input_contract_completeness": float(gate.get("input_contract_completeness", 0.0) or 0.0),
        "output_contract_completeness": float(gate.get("output_contract_completeness", 0.0) or 0.0),
        "handoff_state_variable_coverage": float(
            gate.get("handoff_state_variable_coverage", 0.0) or 0.0
        ),
        "downstream_reconnection_rate": float(gate.get("downstream_reconnection_rate", 0.0) or 0.0),
        "field_package_ready_rate": float(gate.get("field_package_ready_rate", 0.0) or 0.0),
        "evidence_boundary_completeness": float(
            gate.get("evidence_boundary_completeness", 0.0) or 0.0
        ),
        "failure_boundary_completeness": float(
            gate.get("failure_boundary_completeness", 0.0) or 0.0
        ),
        "no_write_boundary_completeness": float(
            gate.get("no_write_boundary_completeness", 0.0) or 0.0
        ),
        "next_stage_decision": gate.get("next_stage_decision", ""),
        "next_operator_source_env_var": gate.get("next_operator_source_env_var", ""),
        "next_operator_validation_command": gate.get(
            "next_operator_validation_command",
            "",
        ),
        "can_generate_field_evidence": bool(gate.get("can_generate_field_evidence", False)),
        "can_resume_model_chain": bool(gate.get("can_resume_model_chain", False)),
        "can_write_to_actuator": bool(gate.get("can_write_to_actuator", False)),
        "can_write_to_release_gate": bool(gate.get("can_write_to_release_gate", False)),
        "boundary_note": gate.get("termination_boundary_note", ""),
    }


def _update_manifest(
    generated_files: dict[str, str],
    report,
    stage_boundary_external_action_board: dict[str, Any],
    new_core_interface_candidate_gate: dict[str, Any],
    external_package_readiness_board: dict[str, Any],
    external_package_operator_action_packet: dict[str, Any],
    external_package_acquisition_maturity_gate: dict[str, Any],
    core_interface_consolidation: dict[str, Any],
    grey_box_submission_readiness_gate: dict[str, Any],
) -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    core_gate = report.metrics["quantified_core_score_gate"]
    board_metadata = stage_boundary_external_action_board["board_metadata"]
    board_summary = stage_boundary_external_action_board["action_summary"]
    board_handoff = stage_boundary_external_action_board["machine_handoff"]
    board_manual_action = board_handoff["manual_action_required"]
    board_handoff_gate = stage_boundary_external_action_board["machine_handoff_contract_gate"]
    board_resource_boundary = stage_boundary_external_action_board["resource_boundary"]
    board_resource_boundary_gate = stage_boundary_external_action_board["resource_boundary_gate"]
    board_low_friction_gate = stage_boundary_external_action_board["low_friction_round_gate"]
    board_saturation_gate = stage_boundary_external_action_board[
        "internal_expansion_saturation_gate"
    ]
    board_claim_basis_promotion_snapshot = stage_boundary_external_action_board[
        "claim_basis_promotion_snapshot"
    ]
    board_subagent_probe = stage_boundary_external_action_board["subagent_orchestration_probe"]
    board_subagent_capability_probe = board_subagent_probe["capability_probe"]
    board_subagent_lifecycle_cleanup = board_subagent_probe["lifecycle_cleanup"]
    new_core_metadata = new_core_interface_candidate_gate["gate_metadata"]
    new_core_summary = new_core_interface_candidate_gate["candidate_summary"]
    external_package_summary = external_package_readiness_board["package_summary"]
    external_package_packet = external_package_operator_action_packet
    external_package_acquisition_gate = external_package_acquisition_maturity_gate
    core_interface_priority = core_interface_consolidation["priority_decision"]
    core_interface_facades = core_interface_consolidation["facades"]
    manifest["status"] = "模型核心治理已按最新指标重排优先级"
    manifest["model_core_optimization_governance"] = {
        key: str(Path(path).relative_to(PROJECT_ROOT))
        for key, path in generated_files.items()
    }
    manifest["latest_agent50_core_score"] = core_gate["core_score"]
    manifest["latest_agent50_core_score_previous"] = core_gate["previous_core_score"]
    manifest["latest_agent50_core_score_delta"] = core_gate["iteration_delta"]
    manifest["latest_agent50_iteration_validity_status"] = core_gate["iteration_validity_status"]
    effective_gate = core_gate["effective_iteration_gate"]
    manifest["latest_agent50_effective_iteration_gate"] = effective_gate
    manifest["latest_agent50_effective_iteration_pass"] = effective_gate["effective_iteration_pass"]
    manifest["latest_agent50_effective_iteration_validity_basis"] = effective_gate["validity_basis"]
    manifest["latest_agent50_score_delta_pass"] = effective_gate["score_delta_pass"]
    manifest["latest_agent50_stage_boundary_termination_pass"] = effective_gate[
        "stage_boundary_termination_pass"
    ]
    manifest["latest_agent50_micro_iteration_evidence_complete"] = effective_gate[
        "micro_iteration_evidence_complete"
    ]
    manifest["latest_agent50_self_interrupt_verdict"] = report.metrics["self_interrupt_verdict"]
    manifest["latest_agent50_self_interrupt_reason"] = report.metrics["self_interrupt_reason"]
    recommended = report.metrics["recommended_next_core_action"]
    manifest["latest_agent50_recommended_next_core_action"] = recommended["task_id"]
    manifest["latest_agent50_recommended_next_core_action_title"] = recommended["title"]
    manifest["latest_agent50_recommended_next_core_action_next_experiment"] = recommended[
        "next_experiment"
    ]
    manifest["latest_agent50_recommended_next_core_action_failure_boundary"] = recommended[
        "failure_boundary"
    ]
    manifest["latest_agent50_recommended_next_core_action_external_blocker"] = recommended[
        "external_blocker"
    ]
    manifest["latest_agent50_recommended_next_core_action_blocked_by"] = recommended.get(
        "blocked_by",
        "",
    )
    manifest["latest_agent50_recommended_next_core_action_first_blocked_step"] = recommended.get(
        "first_blocked_step",
        "",
    )
    manifest["latest_agent50_recommended_next_core_action_next_operator_action"] = recommended.get(
        "next_operator_action",
        "",
    )
    manifest["latest_agent50_stage_decision"] = core_gate["stage_decision"]
    manifest["latest_agent50_continue_expansion_allowed"] = core_gate["continue_expansion_allowed"]
    manifest["latest_agent50_next_allowed_actions"] = core_gate["next_allowed_actions"]
    manifest["latest_agent50_external_resume_conditions"] = core_gate["external_resume_conditions"]
    new_core_interface = core_gate["external_resume_conditions"].get("new_core_interface", {})
    if isinstance(new_core_interface, dict):
        manifest["latest_agent50_new_core_interface"] = new_core_interface
        manifest["latest_agent50_new_core_interface_status"] = new_core_interface.get(
            "interface_status",
            "not_available",
        )
        manifest["latest_agent50_new_core_interface_can_resume_model_chain"] = new_core_interface.get(
            "can_resume_model_chain",
            False,
        )
    manifest["latest_agent50_module_stage_status_previous"] = core_gate["previous_module_stage_status"]
    module_stage_gate = core_gate["module_stage_termination_gate"]
    manifest["latest_agent50_module_stage_status"] = module_stage_gate["module_stage_status"]
    manifest["latest_agent50_module_stage_termination_proof_status"] = module_stage_gate[
        "termination_proof_status"
    ]
    manifest["latest_agent50_module_stage_termination_pass_rate"] = module_stage_gate[
        "termination_pass_rate"
    ]
    manifest["latest_agent50_module_stage_termination_proof_row_count"] = len(
        module_stage_gate["termination_proof_rows"]
    )
    manifest["latest_agent50_next_gate_action"] = core_gate["next_gate_action"]
    hidden_ledger = core_gate["hidden_state_coverage_ledger"]
    manifest["latest_agent50_hidden_state_contract_coverage"] = hidden_ledger["state_variable_contract_coverage"]
    manifest["latest_agent50_sparse_estimation_ready_coverage"] = hidden_ledger["sparse_estimation_ready_coverage"]
    manifest["latest_agent50_design_or_patch_ready_coverage"] = hidden_ledger["design_or_patch_ready_coverage"]
    manifest["latest_agent50_field_validated_state_coverage"] = hidden_ledger["field_validated_state_coverage"]
    manifest["latest_agent50_control_ready_state_coverage"] = hidden_ledger["control_ready_state_coverage"]
    scorecard = report.metrics["governance_scorecard"]
    manifest["latest_agent50_claim_basis_promotion_gate_status"] = scorecard[
        "claim_basis_promotion_gate_status"
    ]
    manifest["latest_agent50_claim_basis_promotion_ready_count"] = scorecard[
        "claim_basis_promotion_ready_count"
    ]
    manifest["latest_agent50_claim_basis_promotion_blocked_count"] = scorecard[
        "claim_basis_promotion_blocked_count"
    ]
    manifest["latest_agent50_claim_basis_promotion_can_emit_field_claim_upgrade"] = scorecard[
        "claim_basis_promotion_can_emit_field_claim_upgrade"
    ]
    manifest["latest_agent50_claim_basis_promotion_can_write_to_actuator"] = scorecard[
        "claim_basis_promotion_can_write_to_actuator"
    ]
    manifest["latest_agent50_claim_basis_promotion_can_write_to_release_gate"] = scorecard[
        "claim_basis_promotion_can_write_to_release_gate"
    ]
    manifest["latest_agent50_r7_field_evidence_sufficiency_status"] = scorecard[
        "r7_field_evidence_sufficiency_status"
    ]
    manifest["latest_agent50_r7_field_evidence_sufficiency_score"] = scorecard[
        "r7_field_evidence_sufficiency_score"
    ]
    manifest["latest_agent50_r7_field_evidence_smoke_pass"] = scorecard["r7_field_evidence_smoke_pass"]
    manifest["latest_agent50_r7_can_route_to_human_review_candidate"] = scorecard[
        "r7_can_route_to_human_review_candidate"
    ]
    manifest["latest_agent50_r7_submission_readiness_status"] = scorecard[
        "r7_submission_readiness_status"
    ]
    manifest["latest_agent50_r7_submission_highest_priority_blocker"] = scorecard[
        "r7_submission_highest_priority_blocker"
    ]
    manifest["latest_agent50_r7_submission_next_operator_action"] = scorecard[
        "r7_submission_next_operator_action"
    ]
    manifest["latest_agent50_r7_submission_blocking_stage_count"] = scorecard[
        "r7_submission_blocking_stage_count"
    ]
    manifest["latest_agent50_r7_submission_repair_work_order_status"] = scorecard[
        "r7_submission_repair_work_order_status"
    ]
    manifest["latest_agent50_r7_submission_repair_item_count"] = scorecard[
        "r7_submission_repair_item_count"
    ]
    manifest["latest_agent50_r7_submission_repair_work_order_path"] = scorecard[
        "r7_submission_repair_work_order_path"
    ]
    manifest["latest_agent50_r7_submission_repair_response_preflight_status"] = scorecard[
        "r7_submission_repair_response_preflight_status"
    ]
    manifest["latest_agent50_r7_submission_repair_response_can_route_to_r7_preflight"] = scorecard[
        "r7_submission_repair_response_can_route_to_r7_preflight"
    ]
    manifest["latest_agent50_external_activation_contract"] = str(
        EXTERNAL_ACTIVATION_CONTRACT_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_agent50_external_activation_contract_status"] = scorecard[
        "external_activation_contract_status"
    ]
    manifest["latest_agent50_external_activation_ready"] = scorecard["external_activation_ready"]
    manifest["latest_agent50_external_activation_ready_channel_count"] = scorecard[
        "external_activation_ready_channel_count"
    ]
    manifest["latest_agent50_external_activation_blocked_channel_count"] = scorecard[
        "external_activation_blocked_channel_count"
    ]
    manifest["latest_agent50_external_activation_boundary_preserved"] = scorecard[
        "external_activation_boundary_preserved"
    ]
    manifest["latest_agent50_external_activation_next_operator_actions"] = scorecard[
        "external_activation_next_operator_actions"
    ]
    manifest["latest_agent50_external_activation_router"] = str(
        EXTERNAL_ACTIVATION_ROUTER_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_agent50_external_activation_router_status"] = scorecard[
        "external_activation_router_status"
    ]
    manifest["latest_agent50_external_activation_router_consumed"] = scorecard[
        "external_activation_router_consumed"
    ]
    manifest["latest_agent50_external_activation_router_path_supplied_count"] = scorecard[
        "external_activation_router_path_supplied_count"
    ]
    manifest["latest_agent50_external_activation_router_route_ready_count"] = scorecard[
        "external_activation_router_route_ready_count"
    ]
    manifest["latest_agent50_external_activation_router_model_chain_ready_route_count"] = scorecard[
        "external_activation_router_model_chain_ready_route_count"
    ]
    manifest["latest_agent50_external_activation_router_handoff_ready_route_count"] = scorecard[
        "external_activation_router_handoff_ready_route_count"
    ]
    manifest["latest_agent50_external_activation_router_blocked_route_count"] = scorecard[
        "external_activation_router_blocked_route_count"
    ]
    manifest["latest_agent50_external_activation_router_boundary_preserved"] = scorecard[
        "external_activation_router_boundary_preserved"
    ]
    manifest["latest_agent50_external_activation_router_ready_channel_ids"] = scorecard[
        "external_activation_router_ready_channel_ids"
    ]
    manifest["latest_agent50_external_activation_router_model_chain_ready_channel_ids"] = scorecard[
        "external_activation_router_model_chain_ready_channel_ids"
    ]
    manifest["latest_agent50_external_activation_router_handoff_ready_channel_ids"] = scorecard[
        "external_activation_router_handoff_ready_channel_ids"
    ]
    manifest["latest_agent50_external_activation_router_blocked_channel_ids"] = scorecard[
        "external_activation_router_blocked_channel_ids"
    ]
    manifest["latest_agent50_external_activation_router_highest_priority_blocker"] = scorecard[
        "external_activation_router_highest_priority_blocker"
    ]
    manifest["latest_agent50_external_activation_router_next_operator_action"] = scorecard[
        "external_activation_router_next_operator_action"
    ]
    manifest["latest_agent50_stage_boundary_external_action_board"] = str(
        STAGE_BOUNDARY_EXTERNAL_ACTION_BOARD_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_agent50_stage_boundary_external_action_board_report"] = str(
        STAGE_BOUNDARY_EXTERNAL_ACTION_BOARD_REPORT_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_agent50_stage_boundary_external_action_board_status"] = board_metadata[
        "board_status"
    ]
    manifest["latest_agent50_stage_boundary_external_action_board_action_count"] = board_summary[
        "action_count"
    ]
    manifest["latest_agent50_stage_boundary_external_action_board_external_wait_count"] = (
        board_summary["external_wait_count"]
    )
    manifest[
        "latest_agent50_stage_boundary_external_action_board_model_chain_resume_ready_count"
    ] = board_summary["model_chain_resume_ready_count"]
    manifest["latest_agent50_stage_boundary_external_action_board_handoff_ready_count"] = (
        board_summary["handoff_ready_count"]
    )
    manifest[
        "latest_agent50_stage_boundary_external_action_board_highest_priority_source_env_var"
    ] = board_summary["highest_priority_source_env_var"]
    manifest[
        "latest_agent50_stage_boundary_external_action_board_highest_priority_next_operator_action"
    ] = board_summary["highest_priority_next_operator_action"]
    manifest[
        "latest_agent50_stage_boundary_external_action_board_highest_priority_focused_candidate_availability_status"
    ] = board_summary["highest_priority_focused_candidate_availability_status"]
    manifest[
        "latest_agent50_stage_boundary_external_action_board_highest_priority_focused_candidate_submit_ready"
    ] = board_summary["highest_priority_focused_candidate_submit_ready"]
    manifest[
        "latest_agent50_stage_boundary_external_action_board_highest_priority_focused_candidate_operator_packet_submit_ready"
    ] = board_summary["highest_priority_focused_candidate_operator_packet_submit_ready"]
    manifest["latest_agent50_stage_boundary_external_action_board_new_core_interface_candidate_gate_status"] = (
        board_summary["new_core_interface_candidate_gate_status"]
    )
    manifest["latest_agent50_stage_boundary_external_action_board_new_core_interface_highest_priority_candidate_id"] = (
        board_summary["new_core_interface_highest_priority_candidate_id"]
    )
    manifest["latest_agent50_stage_boundary_external_action_board_new_core_interface_highest_priority_source_env_var"] = (
        board_summary["new_core_interface_highest_priority_source_env_var"]
    )
    manifest["latest_agent50_stage_boundary_external_action_board_new_core_interface_highest_priority_preflight_status"] = (
        board_summary["new_core_interface_highest_priority_preflight_status"]
    )
    manifest["latest_agent50_stage_boundary_external_action_board_new_core_interface_highest_priority_preflight_pass"] = (
        board_summary["new_core_interface_highest_priority_preflight_pass"]
    )
    manifest["latest_agent50_stage_boundary_external_action_board_new_core_interface_highest_priority_downstream_calibration_status"] = (
        board_summary["new_core_interface_highest_priority_downstream_calibration_status"]
    )
    manifest["latest_agent50_stage_boundary_external_action_board_new_core_interface_highest_priority_can_route_to_downstream_interface"] = (
        board_summary["new_core_interface_highest_priority_can_route_to_downstream_interface"]
    )
    manifest["latest_agent50_stage_boundary_external_action_board_new_core_interface_highest_priority_downstream_interface_status"] = (
        board_summary["new_core_interface_highest_priority_downstream_interface_status"]
    )
    manifest["latest_agent50_stage_boundary_external_action_board_new_core_interface_highest_priority_can_run_agent53_field_calibration"] = (
        board_summary["new_core_interface_highest_priority_can_run_agent53_field_calibration"]
    )
    manifest["latest_agent50_stage_boundary_external_action_board_new_core_interface_highest_priority_agent53_field_candidate_ready"] = (
        board_summary["new_core_interface_highest_priority_agent53_field_candidate_ready"]
    )
    manifest[
        "latest_agent50_stage_boundary_external_action_board_new_core_interface_acquisition_contract_termination_status"
    ] = board_summary["new_core_interface_acquisition_contract_termination_status"]
    manifest[
        "latest_agent50_stage_boundary_external_action_board_new_core_interface_acquisition_module_stage_termination_pass"
    ] = board_summary["new_core_interface_acquisition_module_stage_termination_pass"]
    manifest[
        "latest_agent50_stage_boundary_external_action_board_new_core_interface_acquisition_downstream_reconnection_rate"
    ] = board_summary["new_core_interface_acquisition_downstream_reconnection_rate"]
    manifest[
        "latest_agent50_stage_boundary_external_action_board_new_core_interface_acquisition_field_package_ready_rate"
    ] = board_summary["new_core_interface_acquisition_field_package_ready_rate"]
    manifest[
        "latest_agent50_stage_boundary_external_action_board_new_core_interface_acquisition_termination_blockers"
    ] = board_summary["new_core_interface_acquisition_termination_blockers"]
    manifest[
        "latest_agent50_stage_boundary_external_action_board_machine_handoff_route_event"
    ] = board_handoff["route_event"]
    manifest[
        "latest_agent50_stage_boundary_external_action_board_machine_handoff_next_route"
    ] = board_handoff["next_route"]
    manifest[
        "latest_agent50_stage_boundary_external_action_board_machine_handoff_next_route_source_env_var"
    ] = board_handoff["next_route_source_env_var"]
    manifest[
        "latest_agent50_stage_boundary_external_action_board_machine_handoff_next_route_validation_command"
    ] = board_handoff["next_route_validation_command"]
    manifest[
        "latest_agent50_stage_boundary_external_action_board_machine_handoff_manual_action_required"
    ] = board_manual_action["required"]
    manifest[
        "latest_agent50_stage_boundary_external_action_board_machine_handoff_input_template_path"
    ] = board_manual_action.get("input_template_path", "")
    manifest[
        "latest_agent50_stage_boundary_external_action_board_machine_handoff_schema_path"
    ] = board_manual_action.get("schema_path", "")
    manifest[
        "latest_agent50_stage_boundary_external_action_board_machine_handoff_command_sequence"
    ] = board_manual_action.get("command_sequence", [])
    manifest[
        "latest_agent50_stage_boundary_external_action_board_machine_handoff_rejection_boundaries"
    ] = board_manual_action.get("rejection_boundaries", [])
    manifest[
        "latest_agent50_stage_boundary_external_action_board_machine_handoff_boundary_checks"
    ] = board_manual_action.get("boundary_checks", [])
    manifest[
        "latest_agent50_stage_boundary_external_action_board_machine_handoff_no_write_boundary"
    ] = board_manual_action.get("no_write_boundary", "")
    manifest[
        "latest_agent50_stage_boundary_external_action_board_machine_handoff_can_resume_model_chain"
    ] = board_handoff["can_resume_model_chain"]
    manifest[
        "latest_agent50_stage_boundary_external_action_board_machine_handoff_current_basis_refs"
    ] = board_handoff["current_basis_refs"]
    manifest[
        "latest_agent50_stage_boundary_external_action_board_machine_handoff_not_current_basis_refs"
    ] = board_handoff["not_current_basis_refs"]
    manifest[
        "latest_agent50_stage_boundary_external_action_board_machine_handoff_can_prove"
    ] = board_handoff["can_prove"]
    manifest[
        "latest_agent50_stage_boundary_external_action_board_machine_handoff_cannot_prove"
    ] = board_handoff["cannot_prove"]
    manifest[
        "latest_agent50_stage_boundary_external_action_board_machine_handoff_contract_gate_status"
    ] = board_handoff_gate["gate_status"]
    manifest[
        "latest_agent50_stage_boundary_external_action_board_machine_handoff_contract_score"
    ] = board_handoff_gate["contract_score"]
    manifest[
        "latest_agent50_stage_boundary_external_action_board_machine_handoff_contract_stage_pass"
    ] = board_handoff_gate["contract_stage_pass"]
    manifest[
        "latest_agent50_stage_boundary_external_action_board_machine_handoff_contract_blockers"
    ] = board_handoff_gate["contract_blockers"]
    manifest[
        "latest_agent50_stage_boundary_external_action_board_machine_handoff_external_wait_blockers"
    ] = board_handoff_gate["external_wait_blockers"]
    manifest[
        "latest_agent50_stage_boundary_external_action_board_resource_boundary_gate_status"
    ] = board_resource_boundary_gate["gate_status"]
    manifest[
        "latest_agent50_stage_boundary_external_action_board_resource_boundary_score"
    ] = board_resource_boundary_gate["resource_boundary_score"]
    manifest[
        "latest_agent50_stage_boundary_external_action_board_resource_boundary_stage_pass"
    ] = board_resource_boundary_gate["resource_boundary_stage_pass"]
    manifest[
        "latest_agent50_stage_boundary_external_action_board_resource_boundary_blockers"
    ] = board_resource_boundary_gate["resource_boundary_blockers"]
    manifest[
        "latest_agent50_stage_boundary_external_action_board_resource_boundary_external_wait_blockers"
    ] = board_resource_boundary_gate["external_wait_blockers"]
    manifest[
        "latest_agent50_stage_boundary_external_action_board_resource_boundary_allowed_basis"
    ] = board_resource_boundary["allowed_basis"]
    manifest[
        "latest_agent50_stage_boundary_external_action_board_resource_boundary_forbidden_basis"
    ] = board_resource_boundary["forbidden_basis"]
    manifest[
        "latest_agent50_stage_boundary_external_action_board_resource_boundary_gray_zone"
    ] = board_resource_boundary["gray_zone"]
    manifest["latest_agent50_stage_boundary_low_friction_round_gate_status"] = (
        board_low_friction_gate["gate_status"]
    )
    manifest["latest_agent50_stage_boundary_low_friction_round_gate_score"] = (
        board_low_friction_gate["round_score"]
    )
    manifest["latest_agent50_stage_boundary_low_friction_round_gate_selected_action_id"] = (
        board_low_friction_gate["selected_action_id"]
    )
    manifest[
        "latest_agent50_stage_boundary_low_friction_round_gate_selected_underlying_action_id"
    ] = board_low_friction_gate["selected_underlying_action_id"]
    manifest[
        "latest_agent50_stage_boundary_low_friction_round_gate_selected_canonical_action_id"
    ] = board_low_friction_gate["selected_canonical_action_id"]
    manifest["latest_agent50_stage_boundary_low_friction_round_gate_next_route"] = (
        board_low_friction_gate["termination_contract"]["next_route"]
    )
    manifest[
        "latest_agent50_stage_boundary_low_friction_round_gate_manual_action_required"
    ] = board_low_friction_gate["manual_action_required"]["required"]
    manifest["latest_agent50_stage_boundary_internal_expansion_saturation_gate_status"] = (
        board_saturation_gate["gate_status"]
    )
    manifest["latest_agent50_stage_boundary_internal_expansion_saturation_decision"] = (
        board_saturation_gate["decision"]
    )
    manifest["latest_agent50_stage_boundary_internal_expansion_saturation_required_input"] = (
        board_saturation_gate["required_next_external_input"]
    )
    manifest[
        "latest_agent50_stage_boundary_internal_expansion_saturation_required_validation_command"
    ] = board_saturation_gate["required_validation_command"]
    manifest[
        "latest_agent50_stage_boundary_internal_expansion_saturation_micro_tweak_allowed"
    ] = board_saturation_gate["micro_tweak_expansion_allowed"]
    manifest["latest_agent50_stage_boundary_internal_expansion_saturation_gate_score"] = (
        board_saturation_gate["gate_score"]
    )
    manifest["latest_agent50_stage_boundary_internal_expansion_saturation_stop_reasons"] = (
        board_saturation_gate["stop_reasons"]
    )
    manifest[
        "latest_agent50_stage_boundary_internal_expansion_saturation_resume_conditions"
    ] = board_saturation_gate["resume_conditions"]
    manifest[
        "latest_agent50_stage_boundary_internal_expansion_saturation_claim_readiness_ceiling"
    ] = board_saturation_gate["claim_readiness_ceiling"]
    manifest["latest_agent50_stage_boundary_claim_basis_promotion_snapshot_status"] = (
        board_claim_basis_promotion_snapshot["snapshot_status"]
    )
    manifest["latest_agent50_stage_boundary_claim_basis_promotion_ready_count"] = (
        board_claim_basis_promotion_snapshot["ready_promotion_count"]
    )
    manifest["latest_agent50_stage_boundary_claim_basis_promotion_blocked_count"] = (
        board_claim_basis_promotion_snapshot["blocked_promotion_count"]
    )
    manifest[
        "latest_agent50_stage_boundary_claim_basis_promotion_can_emit_field_claim_upgrade"
    ] = board_claim_basis_promotion_snapshot["can_emit_field_claim_upgrade"]
    manifest["latest_agent50_stage_boundary_claim_basis_promotion_can_write_to_actuator"] = (
        board_claim_basis_promotion_snapshot["can_write_to_actuator"]
    )
    manifest[
        "latest_agent50_stage_boundary_claim_basis_promotion_can_write_to_release_gate"
    ] = board_claim_basis_promotion_snapshot["can_write_to_release_gate"]
    manifest["latest_agent50_stage_boundary_external_action_board_subagent_probe_status"] = (
        board_subagent_probe["probe_status"]
    )
    manifest["latest_agent50_stage_boundary_external_action_board_subagent_strategy"] = (
        board_subagent_probe["strategy"]
    )
    manifest[
        "latest_agent50_stage_boundary_external_action_board_subagent_tool_discovered"
    ] = board_subagent_capability_probe["tool_discovered"]
    manifest[
        "latest_agent50_stage_boundary_external_action_board_subagent_spawn_attempted"
    ] = board_subagent_capability_probe["spawn_attempted"]
    manifest[
        "latest_agent50_stage_boundary_external_action_board_subagent_open_cleanup_required"
    ] = board_subagent_lifecycle_cleanup["open_agent_cleanup_required"]
    manifest["latest_stage_boundary_external_action_board"] = str(
        STAGE_BOUNDARY_EXTERNAL_ACTION_BOARD_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_stage_boundary_external_action_board_report"] = str(
        STAGE_BOUNDARY_EXTERNAL_ACTION_BOARD_REPORT_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_stage_boundary_external_action_board_status"] = board_metadata[
        "board_status"
    ]
    manifest["latest_stage_boundary_external_action_board_action_count"] = board_summary[
        "action_count"
    ]
    manifest["latest_stage_boundary_external_action_board_external_wait_count"] = board_summary[
        "external_wait_count"
    ]
    manifest["latest_stage_boundary_external_action_board_model_chain_resume_ready_count"] = (
        board_summary["model_chain_resume_ready_count"]
    )
    manifest["latest_stage_boundary_external_action_board_highest_priority_source_env_var"] = (
        board_summary["highest_priority_source_env_var"]
    )
    manifest["latest_stage_boundary_external_action_board_highest_priority_next_operator_action"] = (
        board_summary["highest_priority_next_operator_action"]
    )
    manifest[
        "latest_stage_boundary_external_action_board_highest_priority_focused_candidate_availability_status"
    ] = board_summary["highest_priority_focused_candidate_availability_status"]
    manifest[
        "latest_stage_boundary_external_action_board_highest_priority_focused_candidate_submit_ready"
    ] = board_summary["highest_priority_focused_candidate_submit_ready"]
    manifest[
        "latest_stage_boundary_external_action_board_highest_priority_focused_candidate_operator_packet_submit_ready"
    ] = board_summary["highest_priority_focused_candidate_operator_packet_submit_ready"]
    manifest["latest_stage_boundary_external_action_board_new_core_interface_candidate_gate_status"] = (
        board_summary["new_core_interface_candidate_gate_status"]
    )
    manifest["latest_stage_boundary_external_action_board_new_core_interface_highest_priority_candidate_id"] = (
        board_summary["new_core_interface_highest_priority_candidate_id"]
    )
    manifest["latest_stage_boundary_external_action_board_new_core_interface_highest_priority_source_env_var"] = (
        board_summary["new_core_interface_highest_priority_source_env_var"]
    )
    manifest["latest_stage_boundary_external_action_board_new_core_interface_highest_priority_preflight_status"] = (
        board_summary["new_core_interface_highest_priority_preflight_status"]
    )
    manifest["latest_stage_boundary_external_action_board_new_core_interface_highest_priority_preflight_pass"] = (
        board_summary["new_core_interface_highest_priority_preflight_pass"]
    )
    manifest["latest_stage_boundary_external_action_board_new_core_interface_highest_priority_downstream_calibration_status"] = (
        board_summary["new_core_interface_highest_priority_downstream_calibration_status"]
    )
    manifest["latest_stage_boundary_external_action_board_new_core_interface_highest_priority_can_route_to_downstream_interface"] = (
        board_summary["new_core_interface_highest_priority_can_route_to_downstream_interface"]
    )
    manifest["latest_stage_boundary_external_action_board_new_core_interface_highest_priority_downstream_interface_status"] = (
        board_summary["new_core_interface_highest_priority_downstream_interface_status"]
    )
    manifest["latest_stage_boundary_external_action_board_new_core_interface_highest_priority_can_run_agent53_field_calibration"] = (
        board_summary["new_core_interface_highest_priority_can_run_agent53_field_calibration"]
    )
    manifest["latest_stage_boundary_external_action_board_new_core_interface_highest_priority_agent53_field_candidate_ready"] = (
        board_summary["new_core_interface_highest_priority_agent53_field_candidate_ready"]
    )
    manifest[
        "latest_stage_boundary_external_action_board_new_core_interface_acquisition_contract_termination_status"
    ] = board_summary["new_core_interface_acquisition_contract_termination_status"]
    manifest[
        "latest_stage_boundary_external_action_board_new_core_interface_acquisition_module_stage_termination_pass"
    ] = board_summary["new_core_interface_acquisition_module_stage_termination_pass"]
    manifest[
        "latest_stage_boundary_external_action_board_new_core_interface_acquisition_downstream_reconnection_rate"
    ] = board_summary["new_core_interface_acquisition_downstream_reconnection_rate"]
    manifest[
        "latest_stage_boundary_external_action_board_new_core_interface_acquisition_field_package_ready_rate"
    ] = board_summary["new_core_interface_acquisition_field_package_ready_rate"]
    manifest[
        "latest_stage_boundary_external_action_board_new_core_interface_acquisition_termination_blockers"
    ] = board_summary["new_core_interface_acquisition_termination_blockers"]
    manifest["latest_stage_boundary_external_action_board_machine_handoff_route_event"] = (
        board_handoff["route_event"]
    )
    manifest["latest_stage_boundary_external_action_board_machine_handoff_next_route"] = (
        board_handoff["next_route"]
    )
    manifest[
        "latest_stage_boundary_external_action_board_machine_handoff_next_route_source_env_var"
    ] = board_handoff["next_route_source_env_var"]
    manifest[
        "latest_stage_boundary_external_action_board_machine_handoff_next_route_validation_command"
    ] = board_handoff["next_route_validation_command"]
    manifest[
        "latest_stage_boundary_external_action_board_machine_handoff_manual_action_required"
    ] = board_manual_action["required"]
    manifest[
        "latest_stage_boundary_external_action_board_machine_handoff_input_template_path"
    ] = board_manual_action.get("input_template_path", "")
    manifest[
        "latest_stage_boundary_external_action_board_machine_handoff_schema_path"
    ] = board_manual_action.get("schema_path", "")
    manifest[
        "latest_stage_boundary_external_action_board_machine_handoff_command_sequence"
    ] = board_manual_action.get("command_sequence", [])
    manifest[
        "latest_stage_boundary_external_action_board_machine_handoff_rejection_boundaries"
    ] = board_manual_action.get("rejection_boundaries", [])
    manifest[
        "latest_stage_boundary_external_action_board_machine_handoff_boundary_checks"
    ] = board_manual_action.get("boundary_checks", [])
    manifest[
        "latest_stage_boundary_external_action_board_machine_handoff_no_write_boundary"
    ] = board_manual_action.get("no_write_boundary", "")
    manifest[
        "latest_stage_boundary_external_action_board_machine_handoff_can_resume_model_chain"
    ] = board_handoff["can_resume_model_chain"]
    manifest[
        "latest_stage_boundary_external_action_board_machine_handoff_current_basis_refs"
    ] = board_handoff["current_basis_refs"]
    manifest[
        "latest_stage_boundary_external_action_board_machine_handoff_not_current_basis_refs"
    ] = board_handoff["not_current_basis_refs"]
    manifest["latest_stage_boundary_external_action_board_machine_handoff_can_prove"] = (
        board_handoff["can_prove"]
    )
    manifest["latest_stage_boundary_external_action_board_machine_handoff_cannot_prove"] = (
        board_handoff["cannot_prove"]
    )
    manifest[
        "latest_stage_boundary_external_action_board_machine_handoff_contract_gate_status"
    ] = board_handoff_gate["gate_status"]
    manifest[
        "latest_stage_boundary_external_action_board_machine_handoff_contract_score"
    ] = board_handoff_gate["contract_score"]
    manifest[
        "latest_stage_boundary_external_action_board_machine_handoff_contract_stage_pass"
    ] = board_handoff_gate["contract_stage_pass"]
    manifest[
        "latest_stage_boundary_external_action_board_machine_handoff_contract_blockers"
    ] = board_handoff_gate["contract_blockers"]
    manifest[
        "latest_stage_boundary_external_action_board_machine_handoff_external_wait_blockers"
    ] = board_handoff_gate["external_wait_blockers"]
    manifest[
        "latest_stage_boundary_external_action_board_resource_boundary_gate_status"
    ] = board_resource_boundary_gate["gate_status"]
    manifest["latest_stage_boundary_external_action_board_resource_boundary_score"] = (
        board_resource_boundary_gate["resource_boundary_score"]
    )
    manifest[
        "latest_stage_boundary_external_action_board_resource_boundary_stage_pass"
    ] = board_resource_boundary_gate["resource_boundary_stage_pass"]
    manifest[
        "latest_stage_boundary_external_action_board_resource_boundary_blockers"
    ] = board_resource_boundary_gate["resource_boundary_blockers"]
    manifest[
        "latest_stage_boundary_external_action_board_resource_boundary_external_wait_blockers"
    ] = board_resource_boundary_gate["external_wait_blockers"]
    manifest[
        "latest_stage_boundary_external_action_board_resource_boundary_allowed_basis"
    ] = board_resource_boundary["allowed_basis"]
    manifest[
        "latest_stage_boundary_external_action_board_resource_boundary_forbidden_basis"
    ] = board_resource_boundary["forbidden_basis"]
    manifest[
        "latest_stage_boundary_external_action_board_resource_boundary_gray_zone"
    ] = board_resource_boundary["gray_zone"]
    manifest["latest_stage_boundary_internal_expansion_saturation_gate_status"] = (
        board_saturation_gate["gate_status"]
    )
    manifest["latest_stage_boundary_internal_expansion_saturation_decision"] = (
        board_saturation_gate["decision"]
    )
    manifest["latest_stage_boundary_internal_expansion_saturation_required_input"] = (
        board_saturation_gate["required_next_external_input"]
    )
    manifest[
        "latest_stage_boundary_internal_expansion_saturation_required_validation_command"
    ] = board_saturation_gate["required_validation_command"]
    manifest["latest_stage_boundary_internal_expansion_saturation_micro_tweak_allowed"] = (
        board_saturation_gate["micro_tweak_expansion_allowed"]
    )
    manifest["latest_stage_boundary_internal_expansion_saturation_gate_score"] = (
        board_saturation_gate["gate_score"]
    )
    manifest["latest_stage_boundary_internal_expansion_saturation_stop_reasons"] = (
        board_saturation_gate["stop_reasons"]
    )
    manifest["latest_stage_boundary_internal_expansion_saturation_resume_conditions"] = (
        board_saturation_gate["resume_conditions"]
    )
    manifest[
        "latest_stage_boundary_internal_expansion_saturation_claim_readiness_ceiling"
    ] = board_saturation_gate["claim_readiness_ceiling"]
    manifest["latest_stage_boundary_claim_basis_promotion_snapshot_status"] = (
        board_claim_basis_promotion_snapshot["snapshot_status"]
    )
    manifest["latest_stage_boundary_claim_basis_promotion_ready_count"] = (
        board_claim_basis_promotion_snapshot["ready_promotion_count"]
    )
    manifest["latest_stage_boundary_claim_basis_promotion_blocked_count"] = (
        board_claim_basis_promotion_snapshot["blocked_promotion_count"]
    )
    manifest[
        "latest_stage_boundary_claim_basis_promotion_can_emit_field_claim_upgrade"
    ] = board_claim_basis_promotion_snapshot["can_emit_field_claim_upgrade"]
    manifest["latest_stage_boundary_claim_basis_promotion_can_write_to_actuator"] = (
        board_claim_basis_promotion_snapshot["can_write_to_actuator"]
    )
    manifest["latest_stage_boundary_claim_basis_promotion_can_write_to_release_gate"] = (
        board_claim_basis_promotion_snapshot["can_write_to_release_gate"]
    )
    manifest["latest_stage_boundary_external_action_board_subagent_probe_status"] = (
        board_subagent_probe["probe_status"]
    )
    manifest["latest_stage_boundary_external_action_board_subagent_strategy"] = (
        board_subagent_probe["strategy"]
    )
    manifest["latest_stage_boundary_external_action_board_subagent_tool_discovered"] = (
        board_subagent_capability_probe["tool_discovered"]
    )
    manifest["latest_stage_boundary_external_action_board_subagent_spawn_attempted"] = (
        board_subagent_capability_probe["spawn_attempted"]
    )
    manifest[
        "latest_stage_boundary_external_action_board_subagent_open_cleanup_required"
    ] = board_subagent_lifecycle_cleanup["open_agent_cleanup_required"]
    manifest["latest_agent50_new_core_interface_candidate_gate"] = str(
        NEW_CORE_INTERFACE_CANDIDATE_GATE_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_agent50_new_core_interface_candidate_gate_report"] = str(
        NEW_CORE_INTERFACE_CANDIDATE_GATE_REPORT_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_agent50_new_core_interface_candidate_gate_status"] = new_core_metadata[
        "gate_status"
    ]
    manifest["latest_agent50_new_core_interface_candidate_count"] = new_core_summary[
        "candidate_count"
    ]
    manifest["latest_agent50_new_core_interface_admissible_candidate_count"] = new_core_summary[
        "admissible_candidate_count"
    ]
    manifest["latest_agent50_new_core_interface_highest_priority_candidate_id"] = new_core_summary[
        "highest_priority_candidate_id"
    ]
    manifest["latest_agent50_new_core_interface_highest_priority_source_env_var"] = new_core_summary[
        "highest_priority_source_env_var"
    ]
    manifest["latest_agent50_new_core_interface_highest_priority_validation_command"] = new_core_summary[
        "highest_priority_validation_command"
    ]
    manifest["latest_agent50_new_core_interface_highest_priority_next_interface_action"] = new_core_summary[
        "highest_priority_next_interface_action"
    ]
    manifest["latest_agent50_new_core_interface_highest_priority_preflight_status"] = new_core_summary[
        "highest_priority_preflight_status"
    ]
    manifest["latest_agent50_new_core_interface_highest_priority_preflight_pass"] = new_core_summary[
        "highest_priority_preflight_pass"
    ]
    manifest["latest_agent50_new_core_interface_highest_priority_can_route_to_downstream_calibration"] = new_core_summary[
        "highest_priority_can_route_to_downstream_calibration"
    ]
    manifest["latest_agent50_new_core_interface_highest_priority_can_route_to_downstream_interface"] = new_core_summary[
        "highest_priority_can_route_to_downstream_interface"
    ]
    manifest["latest_agent50_new_core_interface_highest_priority_downstream_calibration_status"] = new_core_summary[
        "highest_priority_downstream_calibration_status"
    ]
    manifest["latest_agent50_new_core_interface_highest_priority_downstream_interface_status"] = new_core_summary[
        "highest_priority_downstream_interface_status"
    ]
    manifest["latest_agent50_new_core_interface_highest_priority_can_run_agent53_field_calibration"] = new_core_summary[
        "highest_priority_can_run_agent53_field_calibration"
    ]
    manifest["latest_agent50_new_core_interface_highest_priority_agent53_field_candidate_ready"] = new_core_summary[
        "highest_priority_agent53_field_candidate_ready"
    ]
    manifest["latest_agent50_new_core_interface_can_generate_field_evidence"] = new_core_summary[
        "can_generate_field_evidence"
    ]
    manifest["latest_agent50_new_core_interface_can_write_to_actuator"] = new_core_summary[
        "can_write_to_actuator"
    ]
    manifest["latest_agent50_new_core_interface_can_write_to_release_gate"] = new_core_summary[
        "can_write_to_release_gate"
    ]
    manifest["latest_agent50_external_package_readiness_board"] = str(
        EXTERNAL_PACKAGE_READINESS_BOARD_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_agent50_external_package_readiness_board_report"] = str(
        EXTERNAL_PACKAGE_READINESS_BOARD_REPORT_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_agent50_external_package_readiness_board_package_count"] = (
        external_package_summary["package_count"]
    )
    manifest["latest_agent50_external_package_readiness_board_ready_package_count"] = (
        external_package_summary["ready_package_count"]
    )
    manifest["latest_agent50_external_package_readiness_board_waiting_package_count"] = (
        external_package_summary["waiting_package_count"]
    )
    manifest["latest_agent50_external_package_readiness_board_blocked_package_count"] = (
        external_package_summary["blocked_package_count"]
    )
    manifest[
        "latest_agent50_external_package_readiness_board_unimplemented_package_count"
    ] = external_package_summary["unimplemented_package_count"]
    manifest[
        "latest_agent50_external_package_readiness_board_all_candidate_interfaces_have_preflight"
    ] = external_package_summary["all_candidate_interfaces_have_preflight"]
    manifest[
        "latest_agent50_external_package_readiness_board_next_operator_candidate_id"
    ] = external_package_summary["next_operator_candidate_id"]
    manifest[
        "latest_agent50_external_package_readiness_board_next_operator_source_env_var"
    ] = external_package_summary["next_operator_source_env_var"]
    manifest["latest_agent50_external_package_readiness_board_next_operator_action"] = (
        external_package_summary["next_operator_action"]
    )
    manifest["latest_agent50_external_package_readiness_board_can_resume_model_chain"] = (
        external_package_summary["can_resume_model_chain"]
    )
    manifest[
        "latest_agent50_external_package_readiness_board_can_generate_field_evidence"
    ] = external_package_summary["can_generate_field_evidence"]
    manifest["latest_agent50_external_package_readiness_board_can_write_to_actuator"] = (
        external_package_summary["can_write_to_actuator"]
    )
    manifest["latest_agent50_external_package_readiness_board_can_write_to_release_gate"] = (
        external_package_summary["can_write_to_release_gate"]
    )
    manifest["latest_agent50_external_package_operator_action_packet"] = str(
        EXTERNAL_PACKAGE_OPERATOR_ACTION_PACKET_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_agent50_external_package_operator_action_packet_report"] = str(
        EXTERNAL_PACKAGE_OPERATOR_ACTION_PACKET_REPORT_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_agent50_external_package_operator_action_packet_status"] = (
        external_package_packet["packet_status"]
    )
    manifest["latest_agent50_external_package_operator_action_packet_package_count"] = (
        external_package_packet["package_count"]
    )
    manifest["latest_agent50_external_package_operator_action_packet_next_operator_candidate_id"] = (
        external_package_packet["next_operator_candidate_id"]
    )
    manifest["latest_agent50_external_package_operator_action_packet_next_operator_source_env_var"] = (
        external_package_packet["next_operator_source_env_var"]
    )
    manifest["latest_agent50_external_package_operator_action_packet_next_operator_validation_command"] = (
        external_package_packet["next_operator_validation_command"]
    )
    manifest["latest_agent50_external_package_operator_action_packet_can_generate_field_evidence"] = (
        external_package_packet["can_generate_field_evidence"]
    )
    manifest["latest_agent50_external_package_operator_action_packet_can_resume_model_chain"] = (
        external_package_packet["can_resume_model_chain"]
    )
    manifest["latest_agent50_external_package_operator_action_packet_can_write_to_actuator"] = (
        external_package_packet["can_write_to_actuator"]
    )
    manifest["latest_agent50_external_package_operator_action_packet_can_write_to_release_gate"] = (
        external_package_packet["can_write_to_release_gate"]
    )
    manifest["latest_external_package_readiness_board"] = str(
        EXTERNAL_PACKAGE_READINESS_BOARD_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_external_package_readiness_board_report"] = str(
        EXTERNAL_PACKAGE_READINESS_BOARD_REPORT_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_external_package_readiness_board_package_count"] = (
        external_package_summary["package_count"]
    )
    manifest["latest_external_package_readiness_board_ready_package_count"] = (
        external_package_summary["ready_package_count"]
    )
    manifest["latest_external_package_readiness_board_waiting_package_count"] = (
        external_package_summary["waiting_package_count"]
    )
    manifest["latest_external_package_readiness_board_blocked_package_count"] = (
        external_package_summary["blocked_package_count"]
    )
    manifest["latest_external_package_readiness_board_unimplemented_package_count"] = (
        external_package_summary["unimplemented_package_count"]
    )
    manifest[
        "latest_external_package_readiness_board_all_candidate_interfaces_have_preflight"
    ] = external_package_summary["all_candidate_interfaces_have_preflight"]
    manifest["latest_external_package_readiness_board_next_operator_candidate_id"] = (
        external_package_summary["next_operator_candidate_id"]
    )
    manifest["latest_external_package_readiness_board_next_operator_source_env_var"] = (
        external_package_summary["next_operator_source_env_var"]
    )
    manifest["latest_external_package_readiness_board_next_operator_action"] = (
        external_package_summary["next_operator_action"]
    )
    manifest["latest_external_package_readiness_board_can_resume_model_chain"] = (
        external_package_summary["can_resume_model_chain"]
    )
    manifest["latest_external_package_readiness_board_can_generate_field_evidence"] = (
        external_package_summary["can_generate_field_evidence"]
    )
    manifest["latest_external_package_readiness_board_can_write_to_actuator"] = (
        external_package_summary["can_write_to_actuator"]
    )
    manifest["latest_external_package_readiness_board_can_write_to_release_gate"] = (
        external_package_summary["can_write_to_release_gate"]
    )
    manifest["latest_external_package_operator_action_packet"] = str(
        EXTERNAL_PACKAGE_OPERATOR_ACTION_PACKET_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_external_package_operator_action_packet_report"] = str(
        EXTERNAL_PACKAGE_OPERATOR_ACTION_PACKET_REPORT_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_external_package_operator_action_packet_status"] = (
        external_package_packet["packet_status"]
    )
    manifest["latest_external_package_operator_action_packet_package_count"] = (
        external_package_packet["package_count"]
    )
    manifest["latest_external_package_operator_action_packet_next_operator_candidate_id"] = (
        external_package_packet["next_operator_candidate_id"]
    )
    manifest["latest_external_package_operator_action_packet_next_operator_source_env_var"] = (
        external_package_packet["next_operator_source_env_var"]
    )
    manifest["latest_external_package_operator_action_packet_next_operator_validation_command"] = (
        external_package_packet["next_operator_validation_command"]
    )
    manifest["latest_external_package_operator_action_packet_next_operator_template_dir"] = (
        external_package_packet["next_operator_template_dir"]
    )
    manifest["latest_external_package_operator_action_packet_next_operator_submission_gap_type"] = (
        external_package_packet["next_operator_submission_gap_type"]
    )
    manifest["latest_external_package_operator_action_packet_next_operator_missing_table_count"] = (
        external_package_packet["next_operator_missing_table_count"]
    )
    manifest["latest_external_package_operator_action_packet_next_operator_missing_tables"] = (
        external_package_packet["next_operator_missing_tables"]
    )
    manifest["latest_external_package_operator_action_packet_route_event"] = (
        external_package_packet["route_event"]
    )
    manifest["latest_external_package_operator_action_packet_route_reason"] = (
        external_package_packet["route_reason"]
    )
    manifest["latest_external_package_operator_action_packet_evidence_level"] = (
        external_package_packet["evidence_level"]
    )
    manifest["latest_external_package_operator_action_packet_manual_action_required"] = (
        external_package_packet["manual_action_required"]["required"]
    )
    manifest["latest_external_package_operator_action_packet_current_basis_refs"] = (
        external_package_packet["current_basis_refs"]
    )
    manifest["latest_external_package_operator_action_packet_not_current_basis_refs"] = (
        external_package_packet["not_current_basis_refs"]
    )
    manifest["latest_external_package_operator_action_packet_can_generate_field_evidence"] = (
        external_package_packet["can_generate_field_evidence"]
    )
    manifest["latest_external_package_operator_action_packet_can_resume_model_chain"] = (
        external_package_packet["can_resume_model_chain"]
    )
    manifest["latest_external_package_operator_action_packet_can_write_to_actuator"] = (
        external_package_packet["can_write_to_actuator"]
    )
    manifest["latest_external_package_operator_action_packet_can_write_to_release_gate"] = (
        external_package_packet["can_write_to_release_gate"]
    )
    _apply_external_package_acquisition_manifest_fields(
        manifest,
        "latest_agent50_external_package_acquisition",
        external_package_acquisition_gate,
    )
    _apply_external_package_acquisition_manifest_fields(
        manifest,
        "latest_external_package_acquisition",
        external_package_acquisition_gate,
    )
    manifest["latest_agent50_core_interface_consolidation"] = str(
        CORE_INTERFACE_CONSOLIDATION_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_agent50_core_interface_consolidation_report"] = str(
        CORE_INTERFACE_CONSOLIDATION_REPORT_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_agent50_core_interface_consolidation_consumed"] = True
    manifest["latest_agent50_core_interface_consolidation_refresh_status"] = (
        "agent50_runner_refreshed_current_facade"
    )
    manifest["latest_agent50_core_interface_consolidation_refreshed_by_runner"] = (
        "experiments/run_agent50_model_core_governance.py"
    )
    manifest["latest_agent50_core_interface_consolidation_id"] = core_interface_consolidation[
        "consolidation_id"
    ]
    manifest["latest_agent50_core_interface_consolidation_facade_count"] = core_interface_consolidation[
        "facade_count"
    ]
    manifest["latest_agent50_core_interface_consolidation_top_external_action_env_var"] = (
        core_interface_priority["top_external_action_env_var"]
    )
    manifest["latest_agent50_core_interface_consolidation_top_internal_action"] = (
        core_interface_priority["top_internal_action"]
    )
    manifest["latest_agent50_core_interface_consolidation_new_agent_recommendation"] = (
        core_interface_priority["new_agent_recommendation"]
    )
    manifest["latest_agent50_core_interface_consolidation_external_lifecycle_status"] = (
        core_interface_facades["external_package_lifecycle"]["facade_status"]
    )
    manifest["latest_agent50_core_interface_consolidation_sparse_benchmark_status"] = (
        core_interface_facades["sparse_layout_soft_sensor_coupling_benchmark"]["benchmark_status"]
    )
    manifest["latest_agent50_core_interface_consolidation_control_crosswalk_status"] = (
        core_interface_facades["field_control_replay_crosswalk"]["crosswalk_status"]
    )
    manifest["latest_agent50_core_interface_consolidation_can_generate_field_evidence"] = (
        core_interface_consolidation["boundary"]["can_generate_field_evidence"]
    )
    manifest["latest_agent50_core_interface_consolidation_can_write_to_actuator"] = (
        core_interface_consolidation["boundary"]["can_write_to_actuator"]
    )
    manifest["latest_agent50_core_interface_consolidation_can_write_to_release_gate"] = (
        core_interface_consolidation["boundary"]["can_write_to_release_gate"]
    )
    manifest["latest_agent50_grey_box_submission_readiness_gate"] = str(
        GREY_BOX_SUBMISSION_READINESS_GATE_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_agent50_grey_box_submission_readiness_gate_report"] = str(
        GREY_BOX_SUBMISSION_READINESS_GATE_REPORT_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_agent50_grey_box_submission_readiness_gate_status"] = (
        grey_box_submission_readiness_gate.get(
            "gate_status",
            "grey_box_submission_readiness_gate_not_consumed_by_agent50",
        )
    )
    manifest["latest_agent50_grey_box_submission_readiness_score"] = (
        grey_box_submission_readiness_gate.get("readiness_score", 0.0)
    )
    grey_box_submission_gap = grey_box_submission_readiness_gate.get(
        "highest_priority_gap",
        {"gap_type": "not_consumed", "table": ""},
    )
    manifest["latest_agent50_grey_box_submission_readiness_highest_priority_gap_type"] = (
        grey_box_submission_gap.get("gap_type", "")
    )
    manifest["latest_agent50_grey_box_submission_readiness_highest_priority_gap_table"] = (
        grey_box_submission_gap.get("table", "")
    )
    manifest["latest_agent50_grey_box_submission_readiness_missing_table_count"] = (
        grey_box_submission_gap.get("missing_table_count", 0)
    )
    manifest["latest_agent50_grey_box_submission_readiness_missing_tables"] = (
        grey_box_submission_gap.get("missing_tables", [])
    )
    manifest["latest_agent50_grey_box_submission_readiness_source_env_var"] = (
        grey_box_submission_gap.get("source_env_var", "")
    )
    manifest["latest_agent50_grey_box_submission_readiness_can_submit_to_agent53_field_calibration"] = (
        grey_box_submission_readiness_gate.get(
            "can_submit_to_agent53_field_calibration",
            False,
        )
    )
    manifest["latest_agent50_grey_box_submission_readiness_can_submit_to_agent53_field_candidate"] = (
        grey_box_submission_readiness_gate.get(
            "can_submit_to_agent53_field_candidate",
            False,
        )
    )
    manifest["latest_agent50_grey_box_submission_readiness_can_generate_field_evidence"] = (
        grey_box_submission_readiness_gate.get("can_generate_field_evidence", False)
    )
    manifest["latest_agent50_grey_box_submission_readiness_can_write_to_actuator"] = (
        grey_box_submission_readiness_gate.get("can_write_to_actuator", False)
    )
    manifest["latest_agent50_grey_box_submission_readiness_can_write_to_release_gate"] = (
        grey_box_submission_readiness_gate.get("can_write_to_release_gate", False)
    )
    manifest["latest_core_interface_consolidation"] = str(
        CORE_INTERFACE_CONSOLIDATION_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_core_interface_consolidation_report"] = str(
        CORE_INTERFACE_CONSOLIDATION_REPORT_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_core_interface_consolidation_refresh_status"] = (
        "agent50_runner_refreshed_current_facade"
    )
    manifest["latest_core_interface_consolidation_id"] = core_interface_consolidation[
        "consolidation_id"
    ]
    manifest["latest_core_interface_consolidation_facade_count"] = core_interface_consolidation[
        "facade_count"
    ]
    manifest["latest_core_interface_consolidation_top_external_action_env_var"] = (
        core_interface_priority["top_external_action_env_var"]
    )
    manifest["latest_core_interface_consolidation_top_internal_action"] = (
        core_interface_priority["top_internal_action"]
    )
    manifest["latest_core_interface_consolidation_new_agent_recommendation"] = (
        core_interface_priority["new_agent_recommendation"]
    )
    manifest["latest_core_interface_consolidation_external_lifecycle_status"] = (
        core_interface_facades["external_package_lifecycle"]["facade_status"]
    )
    core_interface_grey_box_row = next(
        row
        for row in core_interface_facades["external_package_lifecycle"]["package_lifecycle_rows"]
        if row["package_key"] == "grey_box_calibration"
    )
    manifest["latest_core_interface_consolidation_grey_box_submission_readiness_gate_status"] = (
        core_interface_grey_box_row["submission_readiness_gate_status"]
    )
    manifest["latest_core_interface_consolidation_grey_box_submission_readiness_score"] = (
        core_interface_grey_box_row["submission_readiness_score"]
    )
    manifest["latest_core_interface_consolidation_grey_box_submission_highest_priority_gap_type"] = (
        core_interface_grey_box_row["submission_highest_priority_gap_type"]
    )
    manifest["latest_core_interface_consolidation_grey_box_submission_highest_priority_gap_table"] = (
        core_interface_grey_box_row["submission_highest_priority_gap_table"]
    )
    manifest["latest_core_interface_consolidation_grey_box_submission_missing_table_count"] = (
        core_interface_grey_box_row["submission_missing_table_count"]
    )
    manifest["latest_core_interface_consolidation_grey_box_submission_missing_tables"] = (
        core_interface_grey_box_row["submission_missing_tables"]
    )
    manifest["latest_core_interface_consolidation_grey_box_submission_source_env_var"] = (
        core_interface_grey_box_row["submission_source_env_var"]
    )
    manifest["latest_core_interface_consolidation_can_submit_to_agent53_field_calibration"] = (
        core_interface_grey_box_row["can_submit_to_agent53_field_calibration"]
    )
    manifest["latest_core_interface_consolidation_can_submit_to_agent53_field_candidate"] = (
        core_interface_grey_box_row["can_submit_to_agent53_field_candidate"]
    )
    manifest["latest_core_interface_consolidation_sparse_benchmark_status"] = (
        core_interface_facades["sparse_layout_soft_sensor_coupling_benchmark"]["benchmark_status"]
    )
    manifest["latest_core_interface_consolidation_control_crosswalk_status"] = (
        core_interface_facades["field_control_replay_crosswalk"]["crosswalk_status"]
    )
    manifest["latest_core_interface_consolidation_can_generate_field_evidence"] = (
        core_interface_consolidation["boundary"]["can_generate_field_evidence"]
    )
    manifest["latest_core_interface_consolidation_can_write_to_actuator"] = (
        core_interface_consolidation["boundary"]["can_write_to_actuator"]
    )
    manifest["latest_core_interface_consolidation_can_write_to_release_gate"] = (
        core_interface_consolidation["boundary"]["can_write_to_release_gate"]
    )
    manifest["latest_agent50_external_activation_operator_action_packet"] = str(
        EXTERNAL_ACTIVATION_OPERATOR_ACTION_PACKET_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_agent50_external_activation_operator_action_packet_status"] = scorecard[
        "external_activation_operator_action_packet_status"
    ]
    manifest["latest_agent50_external_activation_operator_action_packet_target_hidden_state"] = scorecard[
        "external_activation_operator_action_packet_target_hidden_state"
    ]
    manifest["latest_agent50_external_activation_operator_action_packet_source_env_var"] = scorecard[
        "external_activation_operator_action_packet_source_env_var"
    ]
    manifest[
        "latest_agent50_external_activation_operator_action_packet_expected_focused_response_row_count"
    ] = scorecard[
        "external_activation_operator_action_packet_expected_focused_response_row_count"
    ]
    manifest[
        "latest_agent50_external_activation_operator_action_packet_focused_candidate_availability_status"
    ] = scorecard[
        "external_activation_operator_action_packet_focused_candidate_availability_status"
    ]
    manifest[
        "latest_agent50_external_activation_operator_action_packet_focused_candidate_operator_packet_submit_ready"
    ] = scorecard[
        "external_activation_operator_action_packet_focused_candidate_operator_packet_submit_ready"
    ]
    manifest["latest_agent50_external_activation_operator_action_packet_next_operator_action"] = scorecard[
        "external_activation_operator_action_packet_next_operator_action"
    ]
    manifest["latest_agent50_external_activation_operator_action_packet_boundary_pass"] = scorecard[
        "external_activation_operator_action_packet_boundary_pass"
    ]
    manifest["latest_agent50_external_activation_operator_action_packet_can_resume_model_chain"] = scorecard[
        "external_activation_operator_action_packet_can_resume_model_chain"
    ]
    manifest["latest_agent50_external_activation_operator_action_packet_can_write_to_actuator"] = scorecard[
        "external_activation_operator_action_packet_can_write_to_actuator"
    ]
    manifest["latest_agent50_external_activation_operator_action_packet_can_write_to_release_gate"] = scorecard[
        "external_activation_operator_action_packet_can_write_to_release_gate"
    ]
    manifest["latest_agent50_external_activation_router_field_activation_upstream_status"] = scorecard[
        "external_activation_router_field_activation_upstream_status"
    ]
    manifest[
        "latest_agent50_external_activation_router_field_activation_upstream_first_blocked_step"
    ] = scorecard["external_activation_router_field_activation_upstream_first_blocked_step"]
    manifest[
        "latest_agent50_external_activation_router_field_activation_upstream_highest_priority_blocker"
    ] = scorecard["external_activation_router_field_activation_upstream_highest_priority_blocker"]
    manifest[
        "latest_agent50_external_activation_router_field_activation_upstream_next_operator_action"
    ] = scorecard["external_activation_router_field_activation_upstream_next_operator_action"]
    manifest[
        "latest_agent50_external_activation_router_field_activation_upstream_can_submit_to_external_activation_router"
    ] = scorecard[
        "external_activation_router_field_activation_upstream_can_submit_to_external_activation_router"
    ]
    manifest["latest_agent50_external_activation_router_route_summary"] = scorecard[
        "external_activation_router_route_summary"
    ]
    manifest["latest_agent50_field_path_endpoint_label_preflight_status"] = scorecard[
        "field_path_endpoint_label_preflight_status"
    ]
    manifest["latest_agent50_field_path_endpoint_matched_batch_count"] = scorecard[
        "field_path_endpoint_matched_batch_count"
    ]
    manifest["latest_agent50_field_path_endpoint_required_matched_batch_deficit"] = scorecard[
        "field_path_endpoint_required_matched_batch_deficit"
    ]
    manifest["latest_agent50_field_path_endpoint_batch_alignment_gap_count"] = scorecard[
        "field_path_endpoint_batch_alignment_gap_count"
    ]
    manifest["latest_agent50_field_path_endpoint_alignment_patch_plan_status"] = scorecard[
        "field_path_endpoint_alignment_patch_plan_status"
    ]
    manifest["latest_agent50_field_path_endpoint_alignment_patch_plan_item_count"] = scorecard[
        "field_path_endpoint_alignment_patch_plan_item_count"
    ]
    manifest["latest_agent50_field_path_endpoint_label_package_ready"] = scorecard[
        "field_path_endpoint_label_package_ready"
    ]
    manifest["latest_agent50_field_activation_external_readiness_gate_status"] = scorecard[
        "field_activation_external_readiness_gate_status"
    ]
    manifest["latest_agent50_field_activation_external_readiness_first_blocked_step"] = scorecard[
        "field_activation_external_readiness_first_blocked_step"
    ]
    manifest["latest_agent50_field_activation_external_readiness_highest_priority_blocker"] = scorecard[
        "field_activation_external_readiness_highest_priority_blocker"
    ]
    manifest["latest_agent50_field_activation_external_readiness_next_operator_action"] = scorecard[
        "field_activation_external_readiness_next_operator_action"
    ]
    manifest["latest_agent50_field_activation_external_readiness_can_submit_to_external_activation_router"] = scorecard[
        "field_activation_external_readiness_can_submit_to_external_activation_router"
    ]
    manifest["latest_agent50_field_activation_response_coherence_audit_status"] = scorecard[
        "field_activation_response_coherence_audit_status"
    ]
    manifest["latest_agent50_field_activation_response_coherence_hard_blocker_count"] = scorecard[
        "field_activation_response_coherence_hard_blocker_count"
    ]
    manifest["latest_agent50_field_activation_response_coherence_warning_count"] = scorecard[
        "field_activation_response_coherence_warning_count"
    ]
    manifest["latest_agent50_field_activation_response_coherence_highest_priority_blocker"] = scorecard[
        "field_activation_response_coherence_highest_priority_blocker"
    ]
    manifest["latest_agent50_field_activation_response_coherence_can_route_to_package_assembly"] = scorecard[
        "field_activation_response_coherence_can_route_to_package_assembly"
    ]
    manifest["latest_agent50_field_activation_response_missing_value_payload_row_count"] = scorecard[
        "field_activation_response_missing_value_payload_row_count"
    ]
    manifest["latest_agent50_field_activation_response_template_value_payload_row_count"] = scorecard[
        "field_activation_response_template_value_payload_row_count"
    ]
    manifest["latest_agent50_field_activation_response_completion_ledger_status"] = scorecard[
        "field_activation_response_completion_ledger_status"
    ]
    manifest["latest_agent50_field_activation_response_completion_ratio"] = scorecard[
        "field_activation_response_completion_ratio"
    ]
    manifest["latest_agent50_field_activation_response_completed_row_count"] = scorecard[
        "field_activation_response_completed_row_count"
    ]
    manifest["latest_agent50_field_activation_response_incomplete_row_count"] = scorecard[
        "field_activation_response_incomplete_row_count"
    ]
    manifest["latest_agent50_field_activation_response_next_hidden_state_focus"] = scorecard[
        "field_activation_response_next_hidden_state_focus"
    ]
    manifest["latest_agent50_field_activation_response_completion_next_operator_action"] = scorecard[
        "field_activation_response_completion_next_operator_action"
    ]
    manifest["latest_agent50_field_activation_response_focus_handoff_status"] = scorecard[
        "field_activation_response_focus_handoff_status"
    ]
    manifest["latest_agent50_field_activation_response_focus_handoff_target_hidden_state"] = scorecard[
        "field_activation_response_focus_handoff_target_hidden_state"
    ]
    manifest["latest_agent50_field_activation_response_focus_handoff_row_scan_reduction_ratio"] = scorecard[
        "field_activation_response_focus_handoff_row_scan_reduction_ratio"
    ]
    manifest["latest_agent50_field_activation_response_focus_handoff_next_operator_action"] = scorecard[
        "field_activation_response_focus_handoff_next_operator_action"
    ]
    manifest["latest_agent50_field_activation_response_focus_handoff_repair_work_order_status"] = scorecard[
        "field_activation_response_focus_handoff_repair_work_order_status"
    ]
    manifest["latest_agent50_field_activation_response_focus_handoff_repair_item_count"] = scorecard[
        "field_activation_response_focus_handoff_repair_item_count"
    ]
    manifest["latest_agent50_field_activation_response_focus_handoff_repair_next_operator_action"] = scorecard[
        "field_activation_response_focus_handoff_repair_next_operator_action"
    ]
    manifest["latest_agent50_field_activation_response_focus_handoff_source_env_var"] = scorecard[
        "field_activation_response_focus_handoff_source_env_var"
    ]
    manifest["latest_agent50_field_activation_package_staging_selected_row_blueprint_count"] = scorecard[
        "field_activation_package_staging_selected_row_blueprint_count"
    ]
    manifest["latest_agent50_field_activation_package_staging_selected_value_payload_mapping_count"] = scorecard[
        "field_activation_package_staging_selected_value_payload_mapping_count"
    ]
    manifest["latest_agent50_field_activation_materialized_package_blueprint_missing_row_count"] = scorecard[
        "field_activation_materialized_package_blueprint_missing_row_count"
    ]
    manifest["latest_agent50_field_activation_downstream_r7_preview_status"] = scorecard[
        "field_activation_downstream_r7_preview_status"
    ]
    manifest["latest_agent50_field_activation_downstream_r7_preview_executed"] = scorecard[
        "field_activation_downstream_r7_preview_executed"
    ]
    manifest["latest_agent50_field_activation_downstream_r7_preview_metric_evaluation_status"] = scorecard[
        "field_activation_downstream_r7_preview_metric_evaluation_status"
    ]
    manifest["latest_agent50_field_activation_downstream_r7_not_evaluated_metric_count"] = scorecard[
        "field_activation_downstream_r7_not_evaluated_metric_count"
    ]
    manifest["latest_agent50_field_activation_downstream_r7_agent44_import_status"] = scorecard[
        "field_activation_downstream_r7_agent44_import_status"
    ]
    manifest["latest_agent50_field_activation_downstream_r7_can_pass_to_timestamped_replay"] = scorecard[
        "field_activation_downstream_r7_can_pass_to_timestamped_replay"
    ]
    manifest["latest_agent50_field_activation_downstream_r7_highest_priority_blocker"] = scorecard[
        "field_activation_downstream_r7_highest_priority_blocker"
    ]
    manifest["latest_agent50_field_activation_downstream_r7_next_operator_action"] = scorecard[
        "field_activation_downstream_r7_next_operator_action"
    ]
    manifest["latest_agent50_field_activation_downstream_path_endpoint_preview_status"] = scorecard[
        "field_activation_downstream_path_endpoint_preview_status"
    ]
    manifest["latest_agent50_field_activation_downstream_path_endpoint_preview_executed"] = scorecard[
        "field_activation_downstream_path_endpoint_preview_executed"
    ]
    manifest["latest_agent50_field_activation_downstream_path_endpoint_preview_metric_evaluation_status"] = scorecard[
        "field_activation_downstream_path_endpoint_preview_metric_evaluation_status"
    ]
    manifest["latest_agent50_field_activation_downstream_path_endpoint_not_evaluated_metric_count"] = scorecard[
        "field_activation_downstream_path_endpoint_not_evaluated_metric_count"
    ]
    manifest["latest_agent50_field_activation_downstream_path_endpoint_preflight_status"] = scorecard[
        "field_activation_downstream_path_endpoint_preflight_status"
    ]
    manifest["latest_agent50_field_activation_downstream_path_endpoint_required_table_count"] = scorecard[
        "field_activation_downstream_path_endpoint_required_table_count"
    ]
    manifest["latest_agent50_field_activation_downstream_path_endpoint_contract_minimum_matched_batch_count"] = scorecard[
        "field_activation_downstream_path_endpoint_contract_minimum_matched_batch_count"
    ]
    manifest["latest_agent50_field_activation_downstream_path_endpoint_matched_batch_count"] = scorecard[
        "field_activation_downstream_path_endpoint_matched_batch_count"
    ]
    manifest["latest_agent50_field_activation_downstream_path_endpoint_required_matched_batch_deficit"] = scorecard[
        "field_activation_downstream_path_endpoint_required_matched_batch_deficit"
    ]
    manifest["latest_agent50_field_activation_downstream_path_endpoint_can_route_to_field_layout_holdout"] = scorecard[
        "field_activation_downstream_path_endpoint_can_route_to_field_layout_holdout"
    ]
    manifest["latest_agent50_field_activation_downstream_path_endpoint_highest_priority_blocker"] = scorecard[
        "field_activation_downstream_path_endpoint_highest_priority_blocker"
    ]
    manifest["latest_agent50_field_activation_downstream_path_endpoint_next_operator_action"] = scorecard[
        "field_activation_downstream_path_endpoint_next_operator_action"
    ]
    manifest["latest_agent50_observation_response_bridge_status"] = scorecard[
        "observation_response_bridge_status"
    ]
    manifest["latest_agent50_observation_response_bridge_target_hidden_state"] = scorecard[
        "observation_response_bridge_target_hidden_state"
    ]
    manifest["latest_agent50_observation_response_bridge_response_row_count"] = scorecard[
        "observation_response_bridge_response_row_count"
    ]
    manifest["latest_agent50_observation_response_bridge_required_role_coverage_rate"] = scorecard[
        "observation_response_bridge_required_role_coverage_rate"
    ]
    manifest["latest_agent50_observation_response_bridge_can_route_to_agent51_field_proxy_holdout"] = scorecard[
        "observation_response_bridge_can_route_to_agent51_field_proxy_holdout"
    ]
    manifest["latest_agent50_observation_response_bridge_can_relax_agent49_catalyst_uncertainty_block"] = scorecard[
        "observation_response_bridge_can_relax_agent49_catalyst_uncertainty_block"
    ]
    manifest["latest_agent50_catalyst_evidence_response_gate_status"] = scorecard[
        "catalyst_evidence_response_gate_status"
    ]
    manifest["latest_agent50_catalyst_evidence_response_gate_target_response_row_count"] = scorecard[
        "catalyst_evidence_response_gate_target_response_row_count"
    ]
    manifest["latest_agent50_catalyst_evidence_response_gate_row_level_preflight_pass"] = scorecard[
        "catalyst_evidence_response_gate_row_level_preflight_pass"
    ]
    manifest["latest_agent50_catalyst_evidence_response_gate_matched_batch_count"] = scorecard[
        "catalyst_evidence_response_gate_matched_batch_count"
    ]
    manifest["latest_agent50_catalyst_evidence_response_gate_matched_batch_requirement_pass"] = scorecard[
        "catalyst_evidence_response_gate_matched_batch_requirement_pass"
    ]
    manifest[
        "latest_agent50_catalyst_evidence_response_gate_can_route_to_focused_materialized_package_preflight"
    ] = scorecard["catalyst_evidence_response_gate_can_route_to_focused_materialized_package_preflight"]
    manifest["latest_agent50_catalyst_evidence_response_gate_can_route_to_agent51_field_proxy_holdout"] = scorecard[
        "catalyst_evidence_response_gate_can_route_to_agent51_field_proxy_holdout"
    ]
    manifest["latest_agent50_catalyst_response_submission_kit_status"] = scorecard[
        "catalyst_response_submission_kit_status"
    ]
    manifest["latest_agent50_catalyst_response_submission_kit_target_response_row_count"] = scorecard[
        "catalyst_response_submission_kit_target_response_row_count"
    ]
    manifest["latest_agent50_catalyst_response_submission_kit_focused_template_path"] = scorecard[
        "catalyst_response_submission_kit_focused_template_path"
    ]
    manifest["latest_agent50_catalyst_response_submission_kit_can_route_to_agent51_field_proxy_holdout"] = scorecard[
        "catalyst_response_submission_kit_can_route_to_agent51_field_proxy_holdout"
    ]
    manifest["latest_agent50_focused_catalyst_response_merge_status"] = scorecard[
        "focused_catalyst_response_merge_status"
    ]
    manifest["latest_agent50_focused_catalyst_response_source_preflight_status"] = scorecard[
        "focused_catalyst_response_source_preflight_status"
    ]
    manifest["latest_agent50_focused_catalyst_response_source_can_run_merge_preflight"] = scorecard[
        "focused_catalyst_response_source_can_run_merge_preflight"
    ]
    manifest["latest_agent50_focused_catalyst_response_merge_row_preflight_pass"] = scorecard[
        "focused_catalyst_response_merge_row_preflight_pass"
    ]
    manifest["latest_agent50_focused_catalyst_response_repair_work_order_status"] = scorecard[
        "focused_catalyst_response_repair_work_order_status"
    ]
    manifest["latest_agent50_focused_catalyst_response_repair_item_count"] = scorecard[
        "focused_catalyst_response_repair_item_count"
    ]
    manifest["latest_agent50_focused_catalyst_response_repair_highest_priority_repair_id"] = scorecard[
        "focused_catalyst_response_repair_highest_priority_repair_id"
    ]
    manifest["latest_agent50_focused_catalyst_response_repair_next_operator_action"] = scorecard[
        "focused_catalyst_response_repair_next_operator_action"
    ]
    manifest["latest_agent50_focused_catalyst_response_merge_can_emit_candidate"] = scorecard[
        "focused_catalyst_response_merge_can_emit_candidate"
    ]
    manifest[
        "latest_agent50_focused_catalyst_response_merge_can_submit_candidate_as_FIELD_ACTIVATION_RESPONSE_PATH"
    ] = scorecard["focused_catalyst_response_merge_can_submit_candidate_as_FIELD_ACTIVATION_RESPONSE_PATH"]
    manifest["latest_agent50_focused_catalyst_response_merge_candidate_availability_status"] = scorecard[
        "focused_catalyst_response_merge_candidate_availability_status"
    ]
    manifest[
        "latest_agent50_focused_catalyst_response_merge_candidate_preflight_submit_ready"
    ] = scorecard["focused_catalyst_response_merge_candidate_preflight_submit_ready"]
    manifest[
        "latest_agent50_focused_catalyst_response_merge_candidate_self_declared_submit_ready"
    ] = scorecard["focused_catalyst_response_merge_candidate_self_declared_submit_ready"]
    manifest[
        "latest_agent50_focused_catalyst_response_merge_candidate_submit_ready_semantics"
    ] = scorecard["focused_catalyst_response_merge_candidate_submit_ready_semantics"]
    manifest["latest_agent50_focused_catalyst_response_merge_can_route_to_agent51_field_proxy_holdout"] = scorecard[
        "focused_catalyst_response_merge_can_route_to_agent51_field_proxy_holdout"
    ]
    manifest["latest_agent50_catalyst_field_package_slice_status"] = scorecard[
        "catalyst_field_package_slice_status"
    ]
    manifest["latest_agent50_catalyst_field_package_slice_preflight_pass"] = scorecard[
        "catalyst_field_package_slice_preflight_pass"
    ]
    manifest["latest_agent50_catalyst_field_package_slice_matched_batch_count"] = scorecard[
        "catalyst_field_package_slice_matched_batch_count"
    ]
    manifest["latest_agent50_catalyst_field_package_slice_template_dir"] = scorecard[
        "catalyst_field_package_slice_template_dir"
    ]
    manifest["latest_agent50_catalyst_field_package_slice_can_route_to_r7_field_package_patch_candidate"] = scorecard[
        "catalyst_field_package_slice_can_route_to_r7_field_package_patch_candidate"
    ]
    manifest["latest_agent50_catalyst_field_package_slice_can_route_to_agent51_field_proxy_holdout"] = scorecard[
        "catalyst_field_package_slice_can_route_to_agent51_field_proxy_holdout"
    ]
    manifest["latest_agent50_catalyst_slice_r7_patch_candidate_status"] = scorecard[
        "catalyst_slice_r7_patch_candidate_status"
    ]
    manifest["latest_agent50_catalyst_slice_r7_patch_candidate_materialized"] = scorecard[
        "catalyst_slice_r7_patch_candidate_materialized"
    ]
    manifest["latest_agent50_catalyst_slice_r7_patch_candidate_preflight_status"] = scorecard[
        "catalyst_slice_r7_patch_candidate_preflight_status"
    ]
    manifest["latest_agent50_catalyst_slice_r7_patch_candidate_remaining_gap_count"] = scorecard[
        "catalyst_slice_r7_patch_candidate_remaining_gap_count"
    ]
    manifest["latest_agent50_catalyst_slice_r7_patch_candidate_can_submit_as_REAL_FIELD_REPLAY_PACKAGE_DIR"] = scorecard[
        "catalyst_slice_r7_patch_candidate_can_submit_as_REAL_FIELD_REPLAY_PACKAGE_DIR"
    ]
    manifest["latest_agent50_can_route_to_field_layout_holdout_with_path_labels"] = scorecard[
        "can_route_to_field_layout_holdout_with_path_labels"
    ]
    manifest["latest_agent50_release_gate_endpoint_label_blocked"] = scorecard[
        "release_gate_endpoint_label_blocked"
    ]
    manifest["latest_agent50_formal_search_execution_route_plan_status"] = scorecard[
        "formal_search_execution_route_plan_status"
    ]
    manifest["latest_agent50_formal_search_execution_complete_route_row_count"] = scorecard[
        "formal_search_execution_complete_route_row_count"
    ]
    manifest["latest_agent50_formal_search_execution_route_row_count"] = scorecard[
        "formal_search_execution_route_row_count"
    ]
    manifest["latest_agent50_formal_search_execution_mapped_seed_route_count"] = scorecard[
        "formal_search_execution_mapped_seed_route_count"
    ]
    manifest["latest_agent50_formal_search_execution_operator_first_action"] = scorecard[
        "formal_search_execution_operator_first_action"
    ]
    manifest["latest_agent50_formal_search_execution_boundary_preserved"] = scorecard[
        "formal_search_execution_boundary_preserved"
    ]
    manifest["latest_agent50_formal_search_ai_nonlegal_review_brief_status"] = scorecard[
        "formal_search_ai_nonlegal_review_brief_status"
    ]
    manifest["latest_agent50_formal_search_ai_nonlegal_review_brief_row_count"] = scorecard[
        "formal_search_ai_nonlegal_review_brief_row_count"
    ]
    manifest["latest_agent50_formal_search_ai_nonlegal_review_brief_missing_source_row_count"] = scorecard[
        "formal_search_ai_nonlegal_review_brief_missing_source_row_count"
    ]
    manifest["latest_agent50_formal_search_ai_nonlegal_review_brief_missing_claim_mapping_row_count"] = scorecard[
        "formal_search_ai_nonlegal_review_brief_missing_claim_mapping_row_count"
    ]
    manifest["latest_agent50_formal_search_ai_nonlegal_review_brief_can_help_human_review"] = scorecard[
        "formal_search_ai_nonlegal_review_brief_can_help_human_review"
    ]
    manifest["latest_agent50_formal_search_ai_nonlegal_review_brief_can_route_to_claim_scope_patch_draft"] = scorecard[
        "formal_search_ai_nonlegal_review_brief_can_route_to_claim_scope_patch_draft"
    ]
    manifest["latest_agent50_formal_search_ai_nonlegal_review_brief_boundary_preserved"] = scorecard[
        "formal_search_ai_nonlegal_review_brief_boundary_preserved"
    ]
    manifest["latest_agent50_formal_search_ai_nonlegal_review_brief_next_operator_action"] = scorecard[
        "formal_search_ai_nonlegal_review_brief_next_operator_action"
    ]
    manifest["latest_agent50_formal_search_nonlegal_review_operator_packet_status"] = scorecard[
        "formal_search_nonlegal_review_operator_packet_status"
    ]
    manifest["latest_agent50_formal_search_nonlegal_review_operator_packet_expected_review_packet_row_count"] = scorecard[
        "formal_search_nonlegal_review_operator_packet_expected_review_packet_row_count"
    ]
    manifest["latest_agent50_formal_search_nonlegal_review_operator_packet_high_priority_review_row_count"] = scorecard[
        "formal_search_nonlegal_review_operator_packet_high_priority_review_row_count"
    ]
    manifest["latest_agent50_formal_search_nonlegal_review_operator_packet_accepted_review_row_count"] = scorecard[
        "formal_search_nonlegal_review_operator_packet_accepted_review_row_count"
    ]
    manifest["latest_agent50_formal_search_nonlegal_review_operator_packet_source_env_var"] = scorecard[
        "formal_search_nonlegal_review_operator_packet_source_env_var"
    ]
    manifest["latest_agent50_formal_search_nonlegal_review_operator_packet_can_route_to_claim_scope_patch_draft"] = scorecard[
        "formal_search_nonlegal_review_operator_packet_can_route_to_claim_scope_patch_draft"
    ]
    manifest["latest_agent50_formal_search_nonlegal_review_operator_packet_boundary_preserved"] = scorecard[
        "formal_search_nonlegal_review_operator_packet_boundary_preserved"
    ]
    manifest["latest_agent50_formal_search_nonlegal_review_operator_packet_next_operator_action"] = scorecard[
        "formal_search_nonlegal_review_operator_packet_next_operator_action"
    ]
    manifest["next_stage"] = (
        "按低摩擦自我打断闸门运行 Agent50；普通新想法先延迟到阶段边界复盘。"
        "R8u160 已把 GREY_BOX_CALIBRATION_PACKAGE_DIR 推进为可计算提交成熟度 gate；"
        f"当前 grey-box submission readiness 为 {grey_box_submission_readiness_gate.get('gate_status', 'not_consumed')}，"
        f"score={grey_box_submission_readiness_gate.get('readiness_score', 0.0)}，"
        f"最高缺口为 {grey_box_submission_gap.get('gap_type', '')}。"
        f"core interface 当前仍指向最高外部证据动作 {core_interface_priority['top_external_action_env_var']}，"
        "即补齐灰箱校准真实包并运行 grey-box preflight/submission readiness gate。"
        f"当前 Agent50 推荐队列仍记录 {recommended['task_id']}：{recommended['next_experiment']}"
    )
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def _apply_external_package_acquisition_manifest_fields(
    manifest: dict[str, Any],
    prefix: str,
    gate: dict[str, Any],
) -> None:
    manifest[f"{prefix}_maturity_gate"] = str(
        EXTERNAL_PACKAGE_ACQUISITION_MATURITY_GATE_PATH.relative_to(PROJECT_ROOT)
    )
    manifest[f"{prefix}_maturity_gate_report"] = str(
        EXTERNAL_PACKAGE_ACQUISITION_MATURITY_GATE_REPORT_PATH.relative_to(PROJECT_ROOT)
    )
    manifest[f"{prefix}_maturity_gate_status"] = gate["gate_status"]
    manifest[f"{prefix}_maturity_score"] = gate["acquisition_maturity_score"]
    manifest[f"{prefix}_field_package_ready_rate"] = gate["field_package_ready_rate"]
    manifest[f"{prefix}_interface_preflight_coverage"] = gate[
        "interface_preflight_coverage"
    ]
    manifest[f"{prefix}_operator_action_contract_coverage"] = gate[
        "operator_action_contract_coverage"
    ]
    manifest[f"{prefix}_no_write_boundary_integrity"] = gate[
        "no_write_boundary_integrity"
    ]
    manifest[f"{prefix}_input_contract_completeness"] = gate[
        "input_contract_completeness"
    ]
    manifest[f"{prefix}_output_contract_completeness"] = gate[
        "output_contract_completeness"
    ]
    manifest[f"{prefix}_handoff_state_variable_coverage"] = gate[
        "handoff_state_variable_coverage"
    ]
    manifest[f"{prefix}_downstream_reconnection_rate"] = gate[
        "downstream_reconnection_rate"
    ]
    manifest[f"{prefix}_evidence_boundary_completeness"] = gate[
        "evidence_boundary_completeness"
    ]
    manifest[f"{prefix}_failure_boundary_completeness"] = gate[
        "failure_boundary_completeness"
    ]
    manifest[f"{prefix}_no_write_boundary_completeness"] = gate[
        "no_write_boundary_completeness"
    ]
    manifest[f"{prefix}_contract_termination_status"] = gate[
        "contract_termination_status"
    ]
    manifest[f"{prefix}_module_stage_termination_pass"] = gate[
        "module_stage_termination_pass"
    ]
    manifest[f"{prefix}_termination_blockers"] = gate["termination_blockers"]
    manifest[f"{prefix}_package_count"] = gate["package_count"]
    manifest[f"{prefix}_ready_package_count"] = gate["ready_package_count"]
    manifest[f"{prefix}_waiting_package_count"] = gate["waiting_package_count"]
    manifest[f"{prefix}_blocked_package_count"] = gate["blocked_package_count"]
    manifest[f"{prefix}_unimplemented_package_count"] = gate["unimplemented_package_count"]
    manifest[f"{prefix}_preflight_repair_required"] = gate["preflight_repair_required"]
    manifest[f"{prefix}_downstream_gate_ready"] = gate["downstream_gate_ready"]
    manifest[f"{prefix}_model_chain_resume_ready"] = gate["model_chain_resume_ready"]
    manifest[f"{prefix}_next_stage_decision"] = gate["next_stage_decision"]
    manifest[f"{prefix}_next_operator_candidate_id"] = gate["next_operator_candidate_id"]
    manifest[f"{prefix}_next_operator_source_env_var"] = gate[
        "next_operator_source_env_var"
    ]
    manifest[f"{prefix}_next_operator_action"] = gate["next_operator_action"]
    manifest[f"{prefix}_next_operator_validation_command"] = gate[
        "next_operator_validation_command"
    ]
    manifest[f"{prefix}_can_generate_field_evidence"] = gate[
        "can_generate_field_evidence"
    ]
    manifest[f"{prefix}_can_resume_model_chain"] = gate["can_resume_model_chain"]
    manifest[f"{prefix}_can_write_to_actuator"] = gate["can_write_to_actuator"]
    manifest[f"{prefix}_can_write_to_release_gate"] = gate["can_write_to_release_gate"]
    manifest[f"{prefix}_can_emit_field_supported_claim"] = gate[
        "can_emit_field_supported_claim"
    ]


if __name__ == "__main__":
    main()

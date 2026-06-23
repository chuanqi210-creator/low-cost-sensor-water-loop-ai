from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from water_ai.stage_boundary_external_action_board import (
    build_stage_boundary_external_action_board,
    stage_boundary_external_action_board_report_md,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = PROJECT_ROOT / "deliverables" / "manifest.json"
CORE_GATE_PATH = (
    PROJECT_ROOT / "outputs" / "model_core_governance" / "core_score_termination_gate.json"
)
EXTERNAL_OPERATOR_PACKET_PATH = (
    PROJECT_ROOT
    / "outputs"
    / "model_core_governance"
    / "external_activation_operator_action_packet.json"
)
FORMAL_OPERATOR_PACKET_PATH = (
    PROJECT_ROOT
    / "outputs"
    / "agent_architecture_consolidation"
    / "formal_search_nonlegal_review_operator_packet.json"
)
FOCUSED_CATALYST_RESPONSE_MERGE_PREFLIGHT_PATH = (
    PROJECT_ROOT
    / "outputs"
    / "focused_catalyst_response_merge"
    / "focused_catalyst_response_merge_preflight.json"
)
NEW_CORE_INTERFACE_CANDIDATE_GATE_PATH = (
    PROJECT_ROOT
    / "outputs"
    / "model_core_governance"
    / "new_core_interface_candidate_gate.json"
)
UNIFIED_FIELD_EVIDENCE_GATE_METRICS_PATH = (
    PROJECT_ROOT
    / "outputs"
    / "unified_field_evidence_gate"
    / "unified_field_evidence_gate_metrics.json"
)
OUT_PATH = (
    PROJECT_ROOT
    / "outputs"
    / "model_core_governance"
    / "stage_boundary_external_action_board.json"
)
REPORT_PATH = (
    PROJECT_ROOT
    / "deliverables"
    / "model_core_optimization"
    / "stage_boundary_external_action_board.md"
)


def main() -> None:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    board = build_stage_boundary_external_action_board(
        core_gate=_read_json(CORE_GATE_PATH),
        external_activation_operator_action_packet=_read_json(EXTERNAL_OPERATOR_PACKET_PATH),
        formal_search_nonlegal_review_operator_packet=_read_json(FORMAL_OPERATOR_PACKET_PATH),
        focused_catalyst_response_merge_metrics=_read_json(
            FOCUSED_CATALYST_RESPONSE_MERGE_PREFLIGHT_PATH
        ),
        new_core_interface_candidate_gate=_read_json(NEW_CORE_INTERFACE_CANDIDATE_GATE_PATH),
        claim_basis_promotion_gate=_read_json(UNIFIED_FIELD_EVIDENCE_GATE_METRICS_PATH).get(
            "claim_basis_promotion_gate", {}
        ),
    )
    OUT_PATH.write_text(json.dumps(board, ensure_ascii=False, indent=2), encoding="utf-8")
    REPORT_PATH.write_text(stage_boundary_external_action_board_report_md(board), encoding="utf-8")
    _update_manifest(board)

    metadata = board["board_metadata"]
    summary = board["action_summary"]
    handoff = board["machine_handoff"]
    manual_action = handoff["manual_action_required"]
    handoff_gate = board["machine_handoff_contract_gate"]
    resource_boundary = board["resource_boundary"]
    resource_boundary_gate = board["resource_boundary_gate"]
    low_friction_gate = board["low_friction_round_gate"]
    saturation_gate = board["internal_expansion_saturation_gate"]
    claim_basis_promotion_snapshot = board["claim_basis_promotion_snapshot"]
    subagent_probe = board["subagent_orchestration_probe"]
    subagent_capability_probe = subagent_probe["capability_probe"]
    subagent_lifecycle_cleanup = subagent_probe["lifecycle_cleanup"]
    print(f"Stage boundary external action board: {metadata['board_status']}")
    print(f"- action_count: {summary['action_count']}")
    print(f"- external_wait_count: {summary['external_wait_count']}")
    print(f"- model_chain_resume_ready_count: {summary['model_chain_resume_ready_count']}")
    print(f"- highest_priority_source_env_var: {summary['highest_priority_source_env_var']}")
    print(f"board: {OUT_PATH}")
    print(f"report: {REPORT_PATH}")


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _update_manifest(board: dict[str, Any]) -> None:
    manifest = _read_json(MANIFEST_PATH)
    metadata = board["board_metadata"]
    summary = board["action_summary"]
    handoff = board["machine_handoff"]
    manual_action = handoff["manual_action_required"]
    handoff_gate = board["machine_handoff_contract_gate"]
    resource_boundary = board["resource_boundary"]
    resource_boundary_gate = board["resource_boundary_gate"]
    low_friction_gate = board["low_friction_round_gate"]
    saturation_gate = board["internal_expansion_saturation_gate"]
    claim_basis_promotion_snapshot = board["claim_basis_promotion_snapshot"]
    subagent_probe = board["subagent_orchestration_probe"]
    subagent_capability_probe = subagent_probe["capability_probe"]
    subagent_lifecycle_cleanup = subagent_probe["lifecycle_cleanup"]
    manifest["latest_stage_boundary_external_action_board"] = str(
        OUT_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_stage_boundary_external_action_board_report"] = str(
        REPORT_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_stage_boundary_external_action_board_status"] = metadata[
        "board_status"
    ]
    manifest["latest_stage_boundary_external_action_board_action_count"] = summary[
        "action_count"
    ]
    manifest["latest_stage_boundary_external_action_board_external_wait_count"] = summary[
        "external_wait_count"
    ]
    manifest["latest_stage_boundary_external_action_board_model_chain_resume_ready_count"] = (
        summary["model_chain_resume_ready_count"]
    )
    manifest["latest_stage_boundary_external_action_board_highest_priority_source_env_var"] = (
        summary["highest_priority_source_env_var"]
    )
    manifest["latest_stage_boundary_external_action_board_highest_priority_next_operator_action"] = (
        summary["highest_priority_next_operator_action"]
    )
    manifest["latest_stage_boundary_external_action_board_highest_priority_focused_candidate_availability_status"] = (
        summary["highest_priority_focused_candidate_availability_status"]
    )
    manifest["latest_stage_boundary_external_action_board_highest_priority_focused_candidate_submit_ready"] = (
        summary["highest_priority_focused_candidate_submit_ready"]
    )
    manifest[
        "latest_stage_boundary_external_action_board_highest_priority_focused_candidate_operator_packet_submit_ready"
    ] = summary["highest_priority_focused_candidate_operator_packet_submit_ready"]
    manifest["latest_stage_boundary_external_action_board_new_core_interface_candidate_gate_status"] = (
        summary["new_core_interface_candidate_gate_status"]
    )
    manifest["latest_stage_boundary_external_action_board_new_core_interface_highest_priority_candidate_id"] = (
        summary["new_core_interface_highest_priority_candidate_id"]
    )
    manifest["latest_stage_boundary_external_action_board_new_core_interface_highest_priority_source_env_var"] = (
        summary["new_core_interface_highest_priority_source_env_var"]
    )
    manifest["latest_stage_boundary_external_action_board_new_core_interface_highest_priority_preflight_status"] = (
        summary["new_core_interface_highest_priority_preflight_status"]
    )
    manifest["latest_stage_boundary_external_action_board_new_core_interface_highest_priority_preflight_pass"] = (
        summary["new_core_interface_highest_priority_preflight_pass"]
    )
    manifest[
        "latest_stage_boundary_external_action_board_new_core_interface_acquisition_contract_termination_status"
    ] = summary["new_core_interface_acquisition_contract_termination_status"]
    manifest[
        "latest_stage_boundary_external_action_board_new_core_interface_acquisition_module_stage_termination_pass"
    ] = summary["new_core_interface_acquisition_module_stage_termination_pass"]
    manifest[
        "latest_stage_boundary_external_action_board_new_core_interface_acquisition_downstream_reconnection_rate"
    ] = summary["new_core_interface_acquisition_downstream_reconnection_rate"]
    manifest[
        "latest_stage_boundary_external_action_board_new_core_interface_acquisition_field_package_ready_rate"
    ] = summary["new_core_interface_acquisition_field_package_ready_rate"]
    manifest[
        "latest_stage_boundary_external_action_board_new_core_interface_acquisition_termination_blockers"
    ] = summary["new_core_interface_acquisition_termination_blockers"]
    manifest["latest_stage_boundary_external_action_board_machine_handoff_route_event"] = (
        handoff["route_event"]
    )
    manifest["latest_stage_boundary_external_action_board_machine_handoff_next_route"] = (
        handoff["next_route"]
    )
    manifest[
        "latest_stage_boundary_external_action_board_machine_handoff_next_route_source_env_var"
    ] = handoff["next_route_source_env_var"]
    manifest[
        "latest_stage_boundary_external_action_board_machine_handoff_next_route_validation_command"
    ] = handoff["next_route_validation_command"]
    manifest[
        "latest_stage_boundary_external_action_board_machine_handoff_manual_action_required"
    ] = manual_action["required"]
    manifest[
        "latest_stage_boundary_external_action_board_machine_handoff_input_template_path"
    ] = manual_action.get("input_template_path", "")
    manifest[
        "latest_stage_boundary_external_action_board_machine_handoff_schema_path"
    ] = manual_action.get("schema_path", "")
    manifest[
        "latest_stage_boundary_external_action_board_machine_handoff_command_sequence"
    ] = manual_action.get("command_sequence", [])
    manifest[
        "latest_stage_boundary_external_action_board_machine_handoff_rejection_boundaries"
    ] = manual_action.get("rejection_boundaries", [])
    manifest[
        "latest_stage_boundary_external_action_board_machine_handoff_boundary_checks"
    ] = manual_action.get("boundary_checks", [])
    manifest[
        "latest_stage_boundary_external_action_board_machine_handoff_no_write_boundary"
    ] = manual_action.get("no_write_boundary", "")
    manifest[
        "latest_stage_boundary_external_action_board_machine_handoff_can_resume_model_chain"
    ] = handoff["can_resume_model_chain"]
    manifest[
        "latest_stage_boundary_external_action_board_machine_handoff_current_basis_refs"
    ] = handoff["current_basis_refs"]
    manifest[
        "latest_stage_boundary_external_action_board_machine_handoff_not_current_basis_refs"
    ] = handoff["not_current_basis_refs"]
    manifest["latest_stage_boundary_external_action_board_machine_handoff_can_prove"] = (
        handoff["can_prove"]
    )
    manifest["latest_stage_boundary_external_action_board_machine_handoff_cannot_prove"] = (
        handoff["cannot_prove"]
    )
    manifest[
        "latest_stage_boundary_external_action_board_machine_handoff_contract_gate_status"
    ] = handoff_gate["gate_status"]
    manifest[
        "latest_stage_boundary_external_action_board_machine_handoff_contract_score"
    ] = handoff_gate["contract_score"]
    manifest[
        "latest_stage_boundary_external_action_board_machine_handoff_contract_stage_pass"
    ] = handoff_gate["contract_stage_pass"]
    manifest[
        "latest_stage_boundary_external_action_board_machine_handoff_contract_blockers"
    ] = handoff_gate["contract_blockers"]
    manifest[
        "latest_stage_boundary_external_action_board_machine_handoff_external_wait_blockers"
    ] = handoff_gate["external_wait_blockers"]
    manifest[
        "latest_stage_boundary_external_action_board_resource_boundary_gate_status"
    ] = resource_boundary_gate["gate_status"]
    manifest["latest_stage_boundary_external_action_board_resource_boundary_score"] = (
        resource_boundary_gate["resource_boundary_score"]
    )
    manifest[
        "latest_stage_boundary_external_action_board_resource_boundary_stage_pass"
    ] = resource_boundary_gate["resource_boundary_stage_pass"]
    manifest[
        "latest_stage_boundary_external_action_board_resource_boundary_blockers"
    ] = resource_boundary_gate["resource_boundary_blockers"]
    manifest[
        "latest_stage_boundary_external_action_board_resource_boundary_external_wait_blockers"
    ] = resource_boundary_gate["external_wait_blockers"]
    manifest[
        "latest_stage_boundary_external_action_board_resource_boundary_allowed_basis"
    ] = resource_boundary["allowed_basis"]
    manifest[
        "latest_stage_boundary_external_action_board_resource_boundary_forbidden_basis"
    ] = resource_boundary["forbidden_basis"]
    manifest[
        "latest_stage_boundary_external_action_board_resource_boundary_gray_zone"
    ] = resource_boundary["gray_zone"]
    manifest["latest_stage_boundary_low_friction_round_gate_status"] = low_friction_gate[
        "gate_status"
    ]
    manifest["latest_stage_boundary_low_friction_round_gate_score"] = low_friction_gate[
        "round_score"
    ]
    manifest["latest_stage_boundary_low_friction_round_gate_selected_action_id"] = (
        low_friction_gate["selected_action_id"]
    )
    manifest["latest_stage_boundary_low_friction_round_gate_selected_underlying_action_id"] = (
        low_friction_gate["selected_underlying_action_id"]
    )
    manifest["latest_stage_boundary_low_friction_round_gate_selected_canonical_action_id"] = (
        low_friction_gate["selected_canonical_action_id"]
    )
    manifest["latest_stage_boundary_low_friction_round_gate_next_route"] = (
        low_friction_gate["termination_contract"]["next_route"]
    )
    manifest["latest_stage_boundary_low_friction_round_gate_manual_action_required"] = (
        low_friction_gate["manual_action_required"]["required"]
    )
    manifest["latest_stage_boundary_internal_expansion_saturation_gate_status"] = (
        saturation_gate["gate_status"]
    )
    manifest["latest_stage_boundary_internal_expansion_saturation_decision"] = (
        saturation_gate["decision"]
    )
    manifest["latest_stage_boundary_internal_expansion_saturation_required_input"] = (
        saturation_gate["required_next_external_input"]
    )
    manifest[
        "latest_stage_boundary_internal_expansion_saturation_required_validation_command"
    ] = saturation_gate["required_validation_command"]
    manifest["latest_stage_boundary_internal_expansion_saturation_micro_tweak_allowed"] = (
        saturation_gate["micro_tweak_expansion_allowed"]
    )
    manifest["latest_stage_boundary_internal_expansion_saturation_gate_score"] = (
        saturation_gate["gate_score"]
    )
    manifest["latest_stage_boundary_internal_expansion_saturation_stop_reasons"] = (
        saturation_gate["stop_reasons"]
    )
    manifest["latest_stage_boundary_internal_expansion_saturation_resume_conditions"] = (
        saturation_gate["resume_conditions"]
    )
    manifest[
        "latest_stage_boundary_internal_expansion_saturation_claim_readiness_ceiling"
    ] = saturation_gate["claim_readiness_ceiling"]
    manifest["latest_stage_boundary_claim_basis_promotion_snapshot_status"] = (
        claim_basis_promotion_snapshot["snapshot_status"]
    )
    manifest["latest_stage_boundary_claim_basis_promotion_ready_count"] = (
        claim_basis_promotion_snapshot["ready_promotion_count"]
    )
    manifest["latest_stage_boundary_claim_basis_promotion_blocked_count"] = (
        claim_basis_promotion_snapshot["blocked_promotion_count"]
    )
    manifest[
        "latest_stage_boundary_claim_basis_promotion_can_emit_field_claim_upgrade"
    ] = claim_basis_promotion_snapshot["can_emit_field_claim_upgrade"]
    manifest["latest_stage_boundary_claim_basis_promotion_can_write_to_actuator"] = (
        claim_basis_promotion_snapshot["can_write_to_actuator"]
    )
    manifest["latest_stage_boundary_claim_basis_promotion_can_write_to_release_gate"] = (
        claim_basis_promotion_snapshot["can_write_to_release_gate"]
    )
    manifest["latest_stage_boundary_external_action_board_subagent_probe_status"] = (
        subagent_probe["probe_status"]
    )
    manifest["latest_stage_boundary_external_action_board_subagent_strategy"] = (
        subagent_probe["strategy"]
    )
    manifest["latest_stage_boundary_external_action_board_subagent_tool_discovered"] = (
        subagent_capability_probe["tool_discovered"]
    )
    manifest["latest_stage_boundary_external_action_board_subagent_spawn_attempted"] = (
        subagent_capability_probe["spawn_attempted"]
    )
    manifest[
        "latest_stage_boundary_external_action_board_subagent_open_cleanup_required"
    ] = subagent_lifecycle_cleanup["open_agent_cleanup_required"]
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()

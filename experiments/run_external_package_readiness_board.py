from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from water_ai.external_package_readiness_board import (
    attach_submission_readiness_gap,
    build_external_package_acquisition_maturity_gate,
    build_external_package_operator_action_packet,
    build_external_package_readiness_board,
    external_package_acquisition_maturity_gate_report_md,
    external_package_operator_action_packet_report_md,
    external_package_readiness_board_report_md,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = PROJECT_ROOT / "deliverables" / "manifest.json"
METRICS_DIR = PROJECT_ROOT / "outputs" / "model_core_governance"
DELIVERABLES_DIR = PROJECT_ROOT / "deliverables" / "model_core_optimization"
NEW_CORE_INTERFACE_CANDIDATE_GATE_PATH = (
    METRICS_DIR / "new_core_interface_candidate_gate.json"
)
GREY_BOX_SUBMISSION_READINESS_GATE_PATH = (
    PROJECT_ROOT / "outputs" / "grey_box_calibration_package" / "grey_box_submission_readiness_gate.json"
)
OUT_PATH = METRICS_DIR / "external_package_readiness_board.json"
REPORT_PATH = DELIVERABLES_DIR / "external_package_readiness_board.md"
OPERATOR_PACKET_PATH = METRICS_DIR / "external_package_operator_action_packet.json"
OPERATOR_PACKET_REPORT_PATH = (
    DELIVERABLES_DIR / "external_package_operator_action_packet.md"
)
ACQUISITION_MATURITY_GATE_PATH = (
    METRICS_DIR / "external_package_acquisition_maturity_gate.json"
)
ACQUISITION_MATURITY_GATE_REPORT_PATH = (
    DELIVERABLES_DIR / "external_package_acquisition_maturity_gate.md"
)


def main() -> None:
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    DELIVERABLES_DIR.mkdir(parents=True, exist_ok=True)
    package_artifacts = attach_submission_readiness_gap(
        package_artifacts=_package_artifacts(),
        candidate_id="NCI1_GREY_BOX_CALIBRATION_PACKAGE",
        submission_readiness_gate=_read_json(GREY_BOX_SUBMISSION_READINESS_GATE_PATH),
    )
    board = build_external_package_readiness_board(
        new_core_interface_candidate_gate=_read_json(NEW_CORE_INTERFACE_CANDIDATE_GATE_PATH),
        package_artifacts=package_artifacts,
    )
    packet = build_external_package_operator_action_packet(readiness_board=board)
    acquisition_gate = build_external_package_acquisition_maturity_gate(
        readiness_board=board,
        operator_action_packet=packet,
    )
    OUT_PATH.write_text(json.dumps(board, ensure_ascii=False, indent=2), encoding="utf-8")
    REPORT_PATH.write_text(external_package_readiness_board_report_md(board), encoding="utf-8")
    OPERATOR_PACKET_PATH.write_text(
        json.dumps(packet, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    OPERATOR_PACKET_REPORT_PATH.write_text(
        external_package_operator_action_packet_report_md(packet),
        encoding="utf-8",
    )
    ACQUISITION_MATURITY_GATE_PATH.write_text(
        json.dumps(acquisition_gate, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    ACQUISITION_MATURITY_GATE_REPORT_PATH.write_text(
        external_package_acquisition_maturity_gate_report_md(acquisition_gate),
        encoding="utf-8",
    )
    _update_manifest(board, packet, acquisition_gate)

    summary = board["package_summary"]
    print("External package readiness board:", summary["package_count"])
    print(f"- ready_package_count: {summary['ready_package_count']}")
    print(f"- waiting_package_count: {summary['waiting_package_count']}")
    print(f"- blocked_package_count: {summary['blocked_package_count']}")
    print(f"- next_operator_source_env_var: {summary['next_operator_source_env_var']}")
    print(f"- operator_packet_status: {packet['packet_status']}")
    print(f"- operator_packet_next_env_var: {packet['next_operator_source_env_var']}")
    print(f"- acquisition_gate_status: {acquisition_gate['gate_status']}")
    print(f"- acquisition_maturity_score: {acquisition_gate['acquisition_maturity_score']}")
    print(f"- field_package_ready_rate: {acquisition_gate['field_package_ready_rate']}")
    print(f"- next_stage_decision: {acquisition_gate['next_stage_decision']}")
    print(f"board: {OUT_PATH}")
    print(f"report: {REPORT_PATH}")
    print(f"operator_packet: {OPERATOR_PACKET_PATH}")
    print(f"operator_packet_report: {OPERATOR_PACKET_REPORT_PATH}")
    print(f"acquisition_maturity_gate: {ACQUISITION_MATURITY_GATE_PATH}")
    print(f"acquisition_maturity_gate_report: {ACQUISITION_MATURITY_GATE_REPORT_PATH}")


def _package_artifacts() -> dict[str, dict[str, Any]]:
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


def _update_manifest(
    board: dict[str, Any],
    packet: dict[str, Any],
    acquisition_gate: dict[str, Any],
) -> None:
    manifest = _read_json(MANIFEST_PATH)
    summary = board["package_summary"]
    manifest["latest_external_package_readiness_board"] = str(
        OUT_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_external_package_readiness_board_report"] = str(
        REPORT_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_external_package_readiness_board_package_count"] = summary[
        "package_count"
    ]
    manifest["latest_external_package_readiness_board_ready_package_count"] = summary[
        "ready_package_count"
    ]
    manifest["latest_external_package_readiness_board_waiting_package_count"] = summary[
        "waiting_package_count"
    ]
    manifest["latest_external_package_readiness_board_blocked_package_count"] = summary[
        "blocked_package_count"
    ]
    manifest["latest_external_package_readiness_board_unimplemented_package_count"] = (
        summary["unimplemented_package_count"]
    )
    manifest["latest_external_package_readiness_board_all_candidate_interfaces_have_preflight"] = (
        summary["all_candidate_interfaces_have_preflight"]
    )
    manifest["latest_external_package_readiness_board_next_operator_source_env_var"] = (
        summary["next_operator_source_env_var"]
    )
    manifest["latest_external_package_readiness_board_next_operator_action"] = summary[
        "next_operator_action"
    ]
    manifest["latest_external_package_readiness_board_can_generate_field_evidence"] = summary[
        "can_generate_field_evidence"
    ]
    manifest["latest_external_package_readiness_board_can_write_to_actuator"] = summary[
        "can_write_to_actuator"
    ]
    manifest["latest_external_package_readiness_board_can_write_to_release_gate"] = summary[
        "can_write_to_release_gate"
    ]
    manifest["latest_external_package_operator_action_packet"] = str(
        OPERATOR_PACKET_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_external_package_operator_action_packet_report"] = str(
        OPERATOR_PACKET_REPORT_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_external_package_operator_action_packet_status"] = packet[
        "packet_status"
    ]
    manifest["latest_external_package_operator_action_packet_package_count"] = packet[
        "package_count"
    ]
    manifest["latest_external_package_operator_action_packet_next_operator_candidate_id"] = (
        packet["next_operator_candidate_id"]
    )
    manifest["latest_external_package_operator_action_packet_next_operator_source_env_var"] = (
        packet["next_operator_source_env_var"]
    )
    manifest["latest_external_package_operator_action_packet_next_operator_validation_command"] = (
        packet["next_operator_validation_command"]
    )
    manifest["latest_external_package_operator_action_packet_next_operator_template_dir"] = (
        packet["next_operator_template_dir"]
    )
    manifest["latest_external_package_operator_action_packet_next_operator_submission_gap_type"] = (
        packet["next_operator_submission_gap_type"]
    )
    manifest["latest_external_package_operator_action_packet_next_operator_missing_table_count"] = (
        packet["next_operator_missing_table_count"]
    )
    manifest["latest_external_package_operator_action_packet_next_operator_missing_tables"] = (
        packet["next_operator_missing_tables"]
    )
    manifest["latest_external_package_operator_action_packet_route_event"] = packet[
        "route_event"
    ]
    manifest["latest_external_package_operator_action_packet_route_reason"] = packet[
        "route_reason"
    ]
    manifest["latest_external_package_operator_action_packet_evidence_level"] = packet[
        "evidence_level"
    ]
    manifest["latest_external_package_operator_action_packet_manual_action_required"] = (
        packet["manual_action_required"]["required"]
    )
    manifest["latest_external_package_operator_action_packet_current_basis_refs"] = (
        packet["current_basis_refs"]
    )
    manifest["latest_external_package_operator_action_packet_not_current_basis_refs"] = (
        packet["not_current_basis_refs"]
    )
    manifest["latest_external_package_operator_action_packet_can_generate_field_evidence"] = (
        packet["can_generate_field_evidence"]
    )
    manifest["latest_external_package_operator_action_packet_can_write_to_actuator"] = packet[
        "can_write_to_actuator"
    ]
    manifest["latest_external_package_operator_action_packet_can_write_to_release_gate"] = (
        packet["can_write_to_release_gate"]
    )
    manifest["latest_external_package_acquisition_maturity_gate"] = str(
        ACQUISITION_MATURITY_GATE_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_external_package_acquisition_maturity_gate_report"] = str(
        ACQUISITION_MATURITY_GATE_REPORT_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_external_package_acquisition_maturity_gate_status"] = (
        acquisition_gate["gate_status"]
    )
    manifest["latest_external_package_acquisition_maturity_score"] = (
        acquisition_gate["acquisition_maturity_score"]
    )
    manifest["latest_external_package_acquisition_field_package_ready_rate"] = (
        acquisition_gate["field_package_ready_rate"]
    )
    manifest["latest_external_package_acquisition_interface_preflight_coverage"] = (
        acquisition_gate["interface_preflight_coverage"]
    )
    manifest["latest_external_package_acquisition_operator_action_contract_coverage"] = (
        acquisition_gate["operator_action_contract_coverage"]
    )
    manifest["latest_external_package_acquisition_no_write_boundary_integrity"] = (
        acquisition_gate["no_write_boundary_integrity"]
    )
    manifest["latest_external_package_acquisition_input_contract_completeness"] = (
        acquisition_gate["input_contract_completeness"]
    )
    manifest["latest_external_package_acquisition_output_contract_completeness"] = (
        acquisition_gate["output_contract_completeness"]
    )
    manifest["latest_external_package_acquisition_handoff_state_variable_coverage"] = (
        acquisition_gate["handoff_state_variable_coverage"]
    )
    manifest["latest_external_package_acquisition_downstream_reconnection_rate"] = (
        acquisition_gate["downstream_reconnection_rate"]
    )
    manifest["latest_external_package_acquisition_evidence_boundary_completeness"] = (
        acquisition_gate["evidence_boundary_completeness"]
    )
    manifest["latest_external_package_acquisition_failure_boundary_completeness"] = (
        acquisition_gate["failure_boundary_completeness"]
    )
    manifest["latest_external_package_acquisition_no_write_boundary_completeness"] = (
        acquisition_gate["no_write_boundary_completeness"]
    )
    manifest["latest_external_package_acquisition_contract_termination_status"] = (
        acquisition_gate["contract_termination_status"]
    )
    manifest["latest_external_package_acquisition_module_stage_termination_pass"] = (
        acquisition_gate["module_stage_termination_pass"]
    )
    manifest["latest_external_package_acquisition_termination_blockers"] = (
        acquisition_gate["termination_blockers"]
    )
    manifest["latest_external_package_acquisition_package_count"] = (
        acquisition_gate["package_count"]
    )
    manifest["latest_external_package_acquisition_ready_package_count"] = (
        acquisition_gate["ready_package_count"]
    )
    manifest["latest_external_package_acquisition_waiting_package_count"] = (
        acquisition_gate["waiting_package_count"]
    )
    manifest["latest_external_package_acquisition_blocked_package_count"] = (
        acquisition_gate["blocked_package_count"]
    )
    manifest["latest_external_package_acquisition_unimplemented_package_count"] = (
        acquisition_gate["unimplemented_package_count"]
    )
    manifest["latest_external_package_acquisition_preflight_repair_required"] = (
        acquisition_gate["preflight_repair_required"]
    )
    manifest["latest_external_package_acquisition_downstream_gate_ready"] = (
        acquisition_gate["downstream_gate_ready"]
    )
    manifest["latest_external_package_acquisition_model_chain_resume_ready"] = (
        acquisition_gate["model_chain_resume_ready"]
    )
    manifest["latest_external_package_acquisition_next_stage_decision"] = (
        acquisition_gate["next_stage_decision"]
    )
    manifest["latest_external_package_acquisition_next_operator_candidate_id"] = (
        acquisition_gate["next_operator_candidate_id"]
    )
    manifest["latest_external_package_acquisition_next_operator_source_env_var"] = (
        acquisition_gate["next_operator_source_env_var"]
    )
    manifest["latest_external_package_acquisition_next_operator_action"] = (
        acquisition_gate["next_operator_action"]
    )
    manifest["latest_external_package_acquisition_next_operator_validation_command"] = (
        acquisition_gate["next_operator_validation_command"]
    )
    manifest["latest_external_package_acquisition_can_generate_field_evidence"] = (
        acquisition_gate["can_generate_field_evidence"]
    )
    manifest["latest_external_package_acquisition_can_resume_model_chain"] = (
        acquisition_gate["can_resume_model_chain"]
    )
    manifest["latest_external_package_acquisition_can_write_to_actuator"] = (
        acquisition_gate["can_write_to_actuator"]
    )
    manifest["latest_external_package_acquisition_can_write_to_release_gate"] = (
        acquisition_gate["can_write_to_release_gate"]
    )
    manifest["latest_external_package_acquisition_can_emit_field_supported_claim"] = (
        acquisition_gate["can_emit_field_supported_claim"]
    )
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()

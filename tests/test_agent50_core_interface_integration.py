import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RUNNER = PROJECT_ROOT / "experiments" / "run_agent50_model_core_governance.py"
CORE_INTERFACE_RUNNER = PROJECT_ROOT / "experiments" / "run_core_interface_consolidation.py"
AGENT50_PAYLOAD = PROJECT_ROOT / "outputs" / "agent50_model_core_governance" / "agent50_report.json"
CORE_INTERFACE_ARTIFACT = PROJECT_ROOT / "outputs" / "model_core_governance" / "core_interface_consolidation.json"
CORE_SCORE_GATE = PROJECT_ROOT / "outputs" / "model_core_governance" / "core_score_termination_gate.json"
PRIORITY_RANKING = PROJECT_ROOT / "outputs" / "model_core_governance" / "priority_ranking.json"
STAGE_BOUNDARY_BOARD = (
    PROJECT_ROOT / "outputs" / "model_core_governance" / "stage_boundary_external_action_board.json"
)
GOVERNANCE_RECOVERY_INTEGRITY_AUDIT = (
    PROJECT_ROOT / "outputs" / "model_core_governance" / "governance_recovery_integrity_audit.json"
)
FORMAL_SEARCH_NONLEGAL_REVIEW_RESPONSE_PREFLIGHT = (
    PROJECT_ROOT
    / "outputs"
    / "agent_architecture_consolidation"
    / "formal_search_nonlegal_review_response_source_preflight.json"
)
UNIFIED_FIELD_EVIDENCE_GATE_METRICS = (
    PROJECT_ROOT / "outputs" / "unified_field_evidence_gate" / "unified_field_evidence_gate_metrics.json"
)
GREY_BOX_SUBMISSION_GATE = (
    PROJECT_ROOT / "outputs" / "grey_box_calibration_package" / "grey_box_submission_readiness_gate.json"
)
MANIFEST = PROJECT_ROOT / "deliverables" / "manifest.json"


def test_agent50_runner_refreshes_core_interface_consolidation_outputs() -> None:
    source = RUNNER.read_text(encoding="utf-8")

    assert "build_core_interface_consolidation(" in source
    assert "CORE_INTERFACE_CONSOLIDATION_PATH.write_text(" in source
    assert "CORE_INTERFACE_CONSOLIDATION_REPORT_PATH.write_text(" in source
    assert '"core_interface_consolidation": str(CORE_INTERFACE_CONSOLIDATION_PATH)' in source
    assert (
        '"core_interface_consolidation_report": str(CORE_INTERFACE_CONSOLIDATION_REPORT_PATH)'
        in source
    )
    assert '"core_interface_consolidation": core_interface_consolidation' in source
    assert '"core_interface_consolidation_refresh": {' in source
    assert '"consumed_by_agent50": True' in source
    assert '"refresh_status": "agent50_runner_refreshed_current_facade"' in source
    assert "manifest[\"latest_agent50_core_interface_consolidation\"]" in source
    assert "manifest[\"latest_agent50_core_interface_consolidation_consumed\"]" in source
    assert "manifest[\"latest_agent50_core_interface_consolidation_refresh_status\"]" in source
    assert "manifest[\"latest_core_interface_consolidation\"]" in source


def test_agent50_report_exposes_core_interface_status_fields() -> None:
    source = RUNNER.read_text(encoding="utf-8")

    assert "core_interface_consolidation_id" in source
    assert "core_interface_consolidation_consumed_by_agent50" in source
    assert "core_interface_consolidation_refresh_status" in source
    assert "core_interface_consolidation_top_external_action_env_var" in source
    assert "core_interface_consolidation_new_agent_recommendation" in source
    assert "core_interface_external_lifecycle_status" in source
    assert "core_interface_sparse_benchmark_status" in source
    assert "core_interface_control_crosswalk_status" in source


def test_agent50_runner_consumes_grey_box_submission_readiness_gate() -> None:
    source = RUNNER.read_text(encoding="utf-8")

    assert "GREY_BOX_SUBMISSION_READINESS_GATE_PATH" in source
    assert "GREY_BOX_SUBMISSION_READINESS_GATE_REPORT_PATH" in source
    assert "grey_box_submission_readiness_gate = _read_optional_json" in source
    assert "grey_box_submission_readiness_gate=grey_box_submission_readiness_gate" in source
    assert '"grey_box_submission_readiness_gate": str(' in source
    assert '"grey_box_submission_readiness_gate": grey_box_submission_readiness_gate' in source
    assert "grey_box_submission_readiness_gate_status" in source
    assert "latest_agent50_grey_box_submission_readiness_gate_status" in source


def test_core_interface_runner_consumes_grey_box_submission_readiness_gate() -> None:
    source = CORE_INTERFACE_RUNNER.read_text(encoding="utf-8")

    assert "GREY_BOX_SUBMISSION_READINESS_GATE_PATH" in source
    assert "grey_box_submission_readiness_gate=_read_optional_json" in source
    assert "latest_core_interface_consolidation_grey_box_submission_readiness_gate_status" in source
    assert "latest_core_interface_consolidation_can_submit_to_agent53_field_calibration" in source


def test_core_interface_artifact_projects_grey_box_submission_readiness_gate() -> None:
    gate = _read_json(GREY_BOX_SUBMISSION_GATE)
    core_interface = _read_json(CORE_INTERFACE_ARTIFACT)
    grey_box_row = _grey_box_lifecycle_row(core_interface)

    assert grey_box_row["submission_readiness_gate_id"] == gate["gate_id"]
    assert grey_box_row["submission_readiness_gate_status"] == gate["gate_status"]
    assert grey_box_row["submission_readiness_score"] == gate["readiness_score"]
    assert (
        grey_box_row["submission_highest_priority_gap_type"]
        == gate["highest_priority_gap"]["gap_type"]
    )
    assert grey_box_row["submission_highest_priority_gap_table"] == gate["highest_priority_gap"]["table"]
    assert (
        grey_box_row["can_submit_to_agent53_field_calibration"]
        == gate["can_submit_to_agent53_field_calibration"]
    )
    assert (
        grey_box_row["can_submit_to_agent53_field_candidate"]
        == gate["can_submit_to_agent53_field_candidate"]
    )
    assert grey_box_row["submission_gate_can_generate_field_evidence"] is False
    assert grey_box_row["submission_gate_can_write_to_actuator"] is False
    assert grey_box_row["submission_gate_can_write_to_release_gate"] is False


def test_agent50_payload_embeds_gate_and_core_interface_projection() -> None:
    payload = _read_json(AGENT50_PAYLOAD)
    gate = payload["grey_box_submission_readiness_gate"]
    grey_box_row = _grey_box_lifecycle_row(payload["core_interface_consolidation"])

    assert gate["gate_id"] == "R8u160_grey_box_submission_readiness_gate"
    assert grey_box_row["submission_readiness_gate_status"] == gate["gate_status"]
    assert grey_box_row["submission_readiness_score"] == gate["readiness_score"]
    assert (
        grey_box_row["submission_highest_priority_gap_type"]
        == gate["highest_priority_gap"]["gap_type"]
    )
    assert grey_box_row["can_submit_to_agent53_field_calibration"] is False
    assert grey_box_row["can_submit_to_agent53_field_candidate"] is False
    assert gate["can_generate_field_evidence"] is False
    assert gate["can_write_to_actuator"] is False
    assert gate["can_write_to_release_gate"] is False


def test_manifest_exposes_core_interface_grey_box_submission_readiness_summary() -> None:
    gate = _read_json(GREY_BOX_SUBMISSION_GATE)
    manifest = _read_json(MANIFEST)

    assert (
        manifest["latest_core_interface_consolidation_grey_box_submission_readiness_gate_status"]
        == gate["gate_status"]
    )
    assert (
        manifest["latest_core_interface_consolidation_grey_box_submission_readiness_score"]
        == gate["readiness_score"]
    )
    assert (
        manifest["latest_core_interface_consolidation_grey_box_submission_highest_priority_gap_type"]
        == gate["highest_priority_gap"]["gap_type"]
    )
    assert (
        manifest["latest_grey_box_submission_readiness_missing_table_count"]
        == gate["highest_priority_gap"]["missing_table_count"]
    )
    assert (
        manifest["latest_grey_box_submission_readiness_missing_tables"]
        == gate["highest_priority_gap"]["missing_tables"]
    )
    assert (
        manifest["latest_grey_box_submission_readiness_source_env_var"]
        == gate["highest_priority_gap"]["source_env_var"]
    )
    assert (
        manifest["latest_agent50_grey_box_submission_readiness_missing_table_count"]
        == gate["highest_priority_gap"]["missing_table_count"]
    )
    assert (
        manifest["latest_agent50_grey_box_submission_readiness_missing_tables"]
        == gate["highest_priority_gap"]["missing_tables"]
    )
    assert (
        manifest["latest_agent50_grey_box_submission_readiness_source_env_var"]
        == gate["highest_priority_gap"]["source_env_var"]
    )
    assert (
        manifest[
            "latest_external_package_operator_action_packet_next_operator_submission_gap_type"
        ]
        == gate["highest_priority_gap"]["gap_type"]
    )
    assert (
        manifest[
            "latest_external_package_operator_action_packet_next_operator_missing_table_count"
        ]
        == gate["highest_priority_gap"]["missing_table_count"]
    )
    assert (
        manifest["latest_external_package_operator_action_packet_next_operator_missing_tables"]
        == gate["highest_priority_gap"]["missing_tables"]
    )
    assert (
        manifest["latest_external_package_operator_action_packet_next_operator_template_dir"]
        == "outputs/grey_box_calibration_package/grey_box_calibration_package_template"
    )
    assert (
        manifest["latest_external_package_operator_action_packet_route_event"]
        == "external_activation_wait"
    )
    assert (
        manifest["latest_external_package_operator_action_packet_route_reason"]
        == "waiting_for_real_external_package_before_downstream_replay_holdout_calibration"
    )
    assert (
        manifest["latest_external_package_operator_action_packet_evidence_level"]
        == "operator_handoff_only_not_field_evidence"
    )
    assert (
        manifest["latest_external_package_operator_action_packet_manual_action_required"]
        is True
    )
    assert "readiness_board.package_rows" in manifest[
        "latest_external_package_operator_action_packet_current_basis_refs"
    ]
    assert "template_rows" in manifest[
        "latest_external_package_operator_action_packet_not_current_basis_refs"
    ]
    assert (
        manifest["latest_external_package_acquisition_contract_termination_status"]
        == "external_package_contracts_complete_but_waiting_for_field_packages"
    )
    assert (
        manifest["latest_external_package_acquisition_module_stage_termination_pass"]
        is False
    )
    assert (
        manifest["latest_external_package_acquisition_input_contract_completeness"]
        == 1.0
    )
    assert (
        manifest["latest_external_package_acquisition_output_contract_completeness"]
        == 1.0
    )
    assert (
        manifest["latest_external_package_acquisition_handoff_state_variable_coverage"]
        == 1.0
    )
    assert (
        manifest["latest_external_package_acquisition_downstream_reconnection_rate"]
        == 0.0
    )
    assert (
        manifest["latest_external_package_acquisition_evidence_boundary_completeness"]
        == 1.0
    )
    assert (
        manifest["latest_external_package_acquisition_failure_boundary_completeness"]
        == 1.0
    )
    assert (
        manifest["latest_external_package_acquisition_no_write_boundary_completeness"]
        == 1.0
    )
    assert manifest["latest_external_package_acquisition_termination_blockers"] == [
        "downstream_reconnection_rate_below_0.80",
        "field_package_ready_rate_below_1.00",
    ]
    assert (
        manifest[
            "latest_agent50_external_package_acquisition_contract_termination_status"
        ]
        == manifest["latest_external_package_acquisition_contract_termination_status"]
    )
    assert (
        manifest["latest_core_interface_consolidation_grey_box_submission_missing_table_count"]
        == gate["highest_priority_gap"]["missing_table_count"]
    )
    assert (
        manifest["latest_core_interface_consolidation_grey_box_submission_missing_tables"]
        == gate["highest_priority_gap"]["missing_tables"]
    )
    assert (
        manifest["latest_core_interface_consolidation_grey_box_submission_source_env_var"]
        == gate["highest_priority_gap"]["source_env_var"]
    )
    assert (
        manifest["latest_core_interface_consolidation_can_submit_to_agent53_field_calibration"]
        == gate["can_submit_to_agent53_field_calibration"]
    )
    assert (
        manifest["latest_core_interface_consolidation_can_submit_to_agent53_field_candidate"]
        == gate["can_submit_to_agent53_field_candidate"]
    )


def test_core_gate_exposes_external_package_acquisition_termination_snapshot() -> None:
    core_gate = _read_json(CORE_SCORE_GATE)
    priority = _read_json(PRIORITY_RANKING)

    snapshot = core_gate["external_package_acquisition_stage_gate"]
    resume_snapshot = core_gate["external_resume_conditions"][
        "external_package_acquisition_stage_gate"
    ]
    new_core = core_gate["external_resume_conditions"]["new_core_interface"]

    assert snapshot["contract_termination_status"] == (
        "external_package_contracts_complete_but_waiting_for_field_packages"
    )
    assert snapshot["module_stage_termination_pass"] is False
    assert snapshot["downstream_reconnection_rate"] == 0.0
    assert snapshot["field_package_ready_rate"] == 0.0
    assert snapshot["termination_blockers"] == [
        "downstream_reconnection_rate_below_0.80",
        "field_package_ready_rate_below_1.00",
    ]
    assert resume_snapshot == snapshot
    assert (
        new_core["external_package_acquisition_contract_termination_status"]
        == snapshot["contract_termination_status"]
    )
    assert (
        new_core["external_package_acquisition_module_stage_termination_pass"]
        is False
    )
    assert (
        priority["external_package_acquisition_stage_gate"]["termination_blockers"]
        == snapshot["termination_blockers"]
    )


def test_core_gate_and_manifest_expose_module_stage_termination_proof() -> None:
    core_gate = _read_json(CORE_SCORE_GATE)
    manifest = _read_json(MANIFEST)
    module_gate = core_gate["module_stage_termination_gate"]
    proof_rows = module_gate["termination_proof_rows"]

    assert module_gate["termination_proof_status"] == "module_stage_termination_proof_complete"
    assert module_gate["termination_pass_rate"] == 1.0
    assert len(proof_rows) == 7
    assert all(row["system_layer"] for row in proof_rows)
    assert all(row["core_capability"] for row in proof_rows)
    assert all(row["failure_boundary"] for row in proof_rows)
    no_write_row = next(row for row in proof_rows if row["metric"] == "no_write_boundary_clarity")
    assert no_write_row["can_write_to_actuator"] is False
    assert no_write_row["can_write_to_release_gate"] is False
    assert (
        manifest["latest_agent50_module_stage_termination_proof_status"]
        == module_gate["termination_proof_status"]
    )
    assert (
        manifest["latest_agent50_module_stage_termination_pass_rate"]
        == module_gate["termination_pass_rate"]
    )
    assert manifest["latest_agent50_module_stage_termination_proof_row_count"] == 7


def test_manifest_exposes_stage_boundary_acquisition_termination_snapshot() -> None:
    manifest = _read_json(MANIFEST)
    board = _read_json(STAGE_BOUNDARY_BOARD)
    summary = board["action_summary"]

    assert (
        manifest[
            "latest_stage_boundary_external_action_board_new_core_interface_acquisition_contract_termination_status"
        ]
        == summary["new_core_interface_acquisition_contract_termination_status"]
    )
    assert (
        manifest[
            "latest_stage_boundary_external_action_board_new_core_interface_acquisition_module_stage_termination_pass"
        ]
        is False
    )
    assert (
        manifest[
            "latest_agent50_stage_boundary_external_action_board_new_core_interface_acquisition_contract_termination_status"
        ]
        == summary["new_core_interface_acquisition_contract_termination_status"]
    )
    assert manifest[
        "latest_agent50_stage_boundary_external_action_board_new_core_interface_acquisition_termination_blockers"
    ] == [
        "downstream_reconnection_rate_below_0.80",
        "field_package_ready_rate_below_1.00",
    ]


def test_manifest_exposes_stage_boundary_machine_handoff_summary() -> None:
    manifest = _read_json(MANIFEST)
    board = _read_json(STAGE_BOUNDARY_BOARD)
    handoff = board["machine_handoff"]

    assert (
        manifest["latest_stage_boundary_external_action_board_machine_handoff_route_event"]
        == handoff["route_event"]
    )
    assert (
        manifest["latest_stage_boundary_external_action_board_machine_handoff_next_route"]
        == handoff["next_route"]
    )
    assert (
        manifest[
            "latest_stage_boundary_external_action_board_machine_handoff_next_route_source_env_var"
        ]
        == "FOCUSED_CATALYST_RESPONSE_PATH"
    )
    assert (
        manifest[
            "latest_stage_boundary_external_action_board_machine_handoff_next_route_validation_command"
        ]
        == handoff["next_route_validation_command"]
    )
    assert (
        manifest[
            "latest_stage_boundary_external_action_board_machine_handoff_manual_action_required"
        ]
        is True
    )
    assert (
        manifest[
            "latest_stage_boundary_external_action_board_machine_handoff_input_template_path"
        ]
        == handoff["manual_action_required"]["input_template_path"]
    )
    assert (
        manifest[
            "latest_stage_boundary_external_action_board_machine_handoff_schema_path"
        ]
        == handoff["manual_action_required"]["schema_path"]
    )
    assert (
        manifest[
            "latest_stage_boundary_external_action_board_machine_handoff_command_sequence"
        ]
        == handoff["manual_action_required"]["command_sequence"]
    )
    assert (
        manifest[
            "latest_stage_boundary_external_action_board_machine_handoff_rejection_boundaries"
        ]
        == handoff["manual_action_required"]["rejection_boundaries"]
    )
    assert (
        manifest[
            "latest_stage_boundary_external_action_board_machine_handoff_boundary_checks"
        ]
        == handoff["manual_action_required"]["boundary_checks"]
    )
    assert (
        manifest[
            "latest_stage_boundary_external_action_board_machine_handoff_no_write_boundary"
        ]
        == handoff["manual_action_required"]["no_write_boundary"]
    )
    assert (
        manifest[
            "latest_agent50_stage_boundary_external_action_board_machine_handoff_route_event"
        ]
        == "external_activation_wait"
    )
    assert (
        manifest[
            "latest_agent50_stage_boundary_external_action_board_machine_handoff_next_route_validation_command"
        ]
        == handoff["next_route_validation_command"]
    )
    assert (
        manifest[
            "latest_agent50_stage_boundary_external_action_board_machine_handoff_input_template_path"
        ]
        == handoff["manual_action_required"]["input_template_path"]
    )
    assert (
        manifest[
            "latest_agent50_stage_boundary_external_action_board_machine_handoff_command_sequence"
        ]
        == handoff["manual_action_required"]["command_sequence"]
    )
    assert (
        manifest[
            "latest_agent50_stage_boundary_external_action_board_machine_handoff_rejection_boundaries"
        ]
        == handoff["manual_action_required"]["rejection_boundaries"]
    )
    assert (
        manifest[
            "latest_agent50_stage_boundary_external_action_board_machine_handoff_no_write_boundary"
        ]
        == handoff["manual_action_required"]["no_write_boundary"]
    )


def test_manifest_exposes_low_friction_round_gate_summary() -> None:
    manifest = _read_json(MANIFEST)
    board = _read_json(STAGE_BOUNDARY_BOARD)
    gate = board["low_friction_round_gate"]

    assert manifest["latest_stage_boundary_low_friction_round_gate_status"] == gate[
        "gate_status"
    ]
    assert manifest["latest_stage_boundary_low_friction_round_gate_score"] == gate[
        "round_score"
    ]
    assert manifest["latest_stage_boundary_low_friction_round_gate_selected_action_id"] == gate[
        "selected_action_id"
    ]
    assert (
        manifest["latest_stage_boundary_low_friction_round_gate_selected_canonical_action_id"]
        == gate["selected_canonical_action_id"]
    )
    assert (
        manifest["latest_stage_boundary_low_friction_round_gate_selected_underlying_action_id"]
        == gate["selected_underlying_action_id"]
    )
    assert manifest["latest_stage_boundary_low_friction_round_gate_next_route"] == gate[
        "termination_contract"
    ]["next_route"]
    assert manifest["latest_stage_boundary_low_friction_round_gate_manual_action_required"] == (
        gate["manual_action_required"]["required"]
    )
    assert manifest["latest_agent50_stage_boundary_low_friction_round_gate_status"] == gate[
        "gate_status"
    ]
    assert manifest["latest_agent50_stage_boundary_low_friction_round_gate_score"] == gate[
        "round_score"
    ]
    assert (
        manifest["latest_agent50_stage_boundary_low_friction_round_gate_selected_canonical_action_id"]
        == "FIELD_ACTIVATION_RESPONSE_FOCUS_HANDOFF_NEXT_ACTION"
    )


def test_manifest_exposes_internal_expansion_saturation_gate_summary() -> None:
    manifest = _read_json(MANIFEST)
    board = _read_json(STAGE_BOUNDARY_BOARD)
    gate = board["internal_expansion_saturation_gate"]

    assert manifest["latest_stage_boundary_internal_expansion_saturation_gate_status"] == (
        gate["gate_status"]
    )
    assert manifest["latest_stage_boundary_internal_expansion_saturation_decision"] == (
        "stop_internal_micro_expansion_wait_for_real_external_input"
    )
    assert (
        manifest["latest_stage_boundary_internal_expansion_saturation_required_input"]
        == "FOCUSED_CATALYST_RESPONSE_PATH"
    )
    assert (
        manifest["latest_stage_boundary_internal_expansion_saturation_micro_tweak_allowed"]
        is False
    )
    assert manifest["latest_stage_boundary_internal_expansion_saturation_stop_reasons"] == (
        gate["stop_reasons"]
    )
    assert manifest["latest_stage_boundary_internal_expansion_saturation_resume_conditions"] == (
        gate["resume_conditions"]
    )
    assert (
        manifest["latest_stage_boundary_internal_expansion_saturation_claim_readiness_ceiling"]
        == "governance_contract_only_until_real_field_validation"
    )
    assert (
        manifest["latest_agent50_stage_boundary_internal_expansion_saturation_gate_status"]
        == gate["gate_status"]
    )
    assert (
        manifest["latest_agent50_stage_boundary_internal_expansion_saturation_required_input"]
        == "FOCUSED_CATALYST_RESPONSE_PATH"
    )
    assert (
        manifest["latest_agent50_stage_boundary_internal_expansion_saturation_micro_tweak_allowed"]
        is False
    )


def test_manifest_exposes_stage_boundary_claim_basis_promotion_snapshot() -> None:
    manifest = _read_json(MANIFEST)
    board = _read_json(STAGE_BOUNDARY_BOARD)
    snapshot = board["claim_basis_promotion_snapshot"]

    assert (
        manifest["latest_stage_boundary_claim_basis_promotion_snapshot_status"]
        == snapshot["snapshot_status"]
    )
    assert (
        manifest["latest_stage_boundary_claim_basis_promotion_ready_count"]
        == snapshot["ready_promotion_count"]
    )
    assert (
        manifest["latest_stage_boundary_claim_basis_promotion_blocked_count"]
        == snapshot["blocked_promotion_count"]
    )
    assert (
        manifest["latest_stage_boundary_claim_basis_promotion_can_emit_field_claim_upgrade"]
        == snapshot["can_emit_field_claim_upgrade"]
    )
    assert manifest["latest_stage_boundary_claim_basis_promotion_can_write_to_actuator"] is False
    assert manifest["latest_stage_boundary_claim_basis_promotion_can_write_to_release_gate"] is False
    assert (
        manifest["latest_agent50_stage_boundary_claim_basis_promotion_snapshot_status"]
        == snapshot["snapshot_status"]
    )
    assert (
        manifest["latest_agent50_stage_boundary_claim_basis_promotion_ready_count"]
        == snapshot["ready_promotion_count"]
    )
    assert (
        manifest["latest_agent50_stage_boundary_claim_basis_promotion_blocked_count"]
        == snapshot["blocked_promotion_count"]
    )


def test_manifest_exposes_minimum_recovery_traceability_gate_summary() -> None:
    manifest = _read_json(MANIFEST)
    audit = _read_json(GOVERNANCE_RECOVERY_INTEGRITY_AUDIT)
    gate = audit["minimum_traceability_gate"]

    assert manifest["latest_governance_recovery_traceability_gate_status"] == gate[
        "gate_status"
    ]
    assert manifest["latest_governance_recovery_traceability_score"] == gate[
        "traceability_score"
    ]
    assert manifest["latest_governance_recovery_traceability_missing_link_count"] == gate[
        "missing_link_count"
    ]
    assert manifest["latest_governance_recovery_decision_log_status"] == gate[
        "decision_log_status"
    ]
    assert manifest["latest_agent50_governance_recovery_traceability_gate_status"] == gate[
        "gate_status"
    ]
    assert manifest["latest_agent50_governance_recovery_traceability_score"] == gate[
        "traceability_score"
    ]


def test_manifest_exposes_stage_boundary_machine_handoff_tail() -> None:
    manifest = _read_json(MANIFEST)
    board = _read_json(STAGE_BOUNDARY_BOARD)
    handoff = board["machine_handoff"]

    assert (
        manifest[
            "latest_agent50_stage_boundary_external_action_board_machine_handoff_can_resume_model_chain"
        ]
        is False
    )
    assert "template_rows" in manifest[
        "latest_stage_boundary_external_action_board_machine_handoff_not_current_basis_refs"
    ]
    assert "field treatment performance" in manifest[
        "latest_agent50_stage_boundary_external_action_board_machine_handoff_cannot_prove"
    ]


def test_manifest_exposes_stage_boundary_machine_handoff_contract_gate() -> None:
    manifest = _read_json(MANIFEST)
    board = _read_json(STAGE_BOUNDARY_BOARD)
    gate = board["machine_handoff_contract_gate"]

    assert (
        manifest["latest_stage_boundary_external_action_board_machine_handoff_contract_gate_status"]
        == gate["gate_status"]
    )
    assert (
        manifest["latest_stage_boundary_external_action_board_machine_handoff_contract_score"]
        == 1.0
    )
    assert (
        manifest["latest_stage_boundary_external_action_board_machine_handoff_contract_stage_pass"]
        is True
    )
    assert (
        manifest["latest_agent50_stage_boundary_external_action_board_machine_handoff_contract_gate_status"]
        == "machine_handoff_contract_complete_waiting_for_external_input"
    )
    assert (
        manifest[
            "latest_agent50_stage_boundary_external_action_board_machine_handoff_external_wait_blockers"
        ]
        == ["real_external_input_required"]
    )


def test_manifest_exposes_stage_boundary_resource_boundary_gate() -> None:
    manifest = _read_json(MANIFEST)
    board = _read_json(STAGE_BOUNDARY_BOARD)
    boundary = board["resource_boundary"]
    gate = board["resource_boundary_gate"]

    assert (
        manifest["latest_stage_boundary_external_action_board_resource_boundary_gate_status"]
        == gate["gate_status"]
    )
    assert (
        manifest["latest_stage_boundary_external_action_board_resource_boundary_score"]
        == 1.0
    )
    assert (
        manifest["latest_stage_boundary_external_action_board_resource_boundary_stage_pass"]
        is True
    )
    assert (
        manifest[
            "latest_stage_boundary_external_action_board_resource_boundary_forbidden_basis"
        ]
        == boundary["forbidden_basis"]
    )
    assert (
        manifest[
            "latest_agent50_stage_boundary_external_action_board_resource_boundary_gate_status"
        ]
        == "resource_boundary_complete_waiting_for_real_external_input"
    )
    assert (
        manifest[
            "latest_agent50_stage_boundary_external_action_board_resource_boundary_external_wait_blockers"
        ]
        == ["real_external_input_required"]
    )


def test_manifest_exposes_stage_boundary_subagent_orchestration_probe() -> None:
    manifest = _read_json(MANIFEST)
    board = _read_json(STAGE_BOUNDARY_BOARD)
    probe = board["subagent_orchestration_probe"]

    assert (
        manifest["latest_stage_boundary_external_action_board_subagent_probe_status"]
        == probe["probe_status"]
    )
    assert (
        manifest["latest_stage_boundary_external_action_board_subagent_strategy"]
        == "not_needed"
    )
    assert (
        manifest["latest_stage_boundary_external_action_board_subagent_tool_discovered"]
        is False
    )
    assert (
        manifest["latest_stage_boundary_external_action_board_subagent_spawn_attempted"]
        is False
    )
    assert (
        manifest["latest_stage_boundary_external_action_board_subagent_open_cleanup_required"]
        is False
    )
    assert (
        manifest["latest_agent50_stage_boundary_external_action_board_subagent_probe_status"]
        == probe["probe_status"]
    )
    assert (
        manifest["latest_agent50_stage_boundary_external_action_board_subagent_strategy"]
        == "not_needed"
    )


def test_manifest_exposes_governance_recovery_integrity_audit() -> None:
    manifest = _read_json(MANIFEST)
    audit = _read_json(GOVERNANCE_RECOVERY_INTEGRITY_AUDIT)

    assert (
        manifest["latest_governance_recovery_integrity_audit"]
        == "outputs/model_core_governance/governance_recovery_integrity_audit.json"
    )
    assert (
        manifest["latest_governance_recovery_integrity_audit_status"]
        == audit["audit_metadata"]["audit_status"]
    )
    assert manifest["latest_governance_recovery_integrity_score"] == 1.0
    assert manifest["latest_governance_recovery_integrity_stage_pass"] is True
    assert manifest["latest_governance_recovery_integrity_blockers"] == []
    assert manifest["latest_governance_recovery_integrity_safe_next_route"] == (
        "submit_real_external_input_then_rerun_stage_preflight_and_agent50"
    )
    assert (
        manifest["latest_agent50_governance_recovery_integrity_audit_status"]
        == "recovery_integrity_pass_waiting_for_real_external_input"
    )
    numeric_trace = audit["numeric_calculation_trace"]
    assert (
        manifest["latest_governance_recovery_integrity_numeric_trace_status"]
        == numeric_trace["trace_status"]
    )
    assert manifest["latest_governance_recovery_integrity_numeric_trace_pass"] is True
    assert manifest["latest_governance_recovery_integrity_numeric_trace_score_delta"] == 0.0
    assert (
        manifest["latest_agent50_governance_recovery_integrity_numeric_trace_status"]
        == "numeric_trace_pass_recovery_integrity_score_recomputed"
    )
    protocol_adaptation = audit["protocol_adaptation"]
    assert (
        manifest["latest_governance_recovery_integrity_protocol_adaptation_status"]
        == protocol_adaptation["adaptation_status"]
    )
    assert (
        manifest["latest_governance_recovery_integrity_protocol_anti_bloat_gate_status"]
        == "pass_selective_adoption_not_full_protocol_copy"
    )
    assert manifest["latest_governance_recovery_integrity_protocol_selected_rule_count"] == 6
    assert manifest["latest_governance_recovery_integrity_protocol_deferred_rule_count"] == 4


def test_manifest_exposes_nonlegal_review_ai_draft_boundary_gate() -> None:
    manifest = _read_json(MANIFEST)
    preflight = _read_json(FORMAL_SEARCH_NONLEGAL_REVIEW_RESPONSE_PREFLIGHT)

    assert (
        manifest[
            "latest_agent60_formal_search_nonlegal_review_response_ai_draft_boundary_gap_count"
        ]
        == preflight["ai_draft_boundary_gap_count"]
    )
    assert (
        manifest[
            "latest_agent60_formal_search_nonlegal_review_response_ai_draft_boundary_gaps"
        ]
        == preflight["ai_draft_boundary_gaps"]
    )


def test_manifest_exposes_claim_basis_promotion_gate_summary() -> None:
    manifest = _read_json(MANIFEST)
    unified_gate = _read_json(UNIFIED_FIELD_EVIDENCE_GATE_METRICS)
    promotion_gate = unified_gate["claim_basis_promotion_gate"]

    assert manifest["latest_claim_basis_promotion_gate_status"] == promotion_gate["gate_status"]
    assert (
        manifest["latest_claim_basis_promotion_gate_ready_promotion_count"]
        == promotion_gate["ready_promotion_count"]
    )
    assert (
        manifest["latest_claim_basis_promotion_gate_blocked_promotion_count"]
        == promotion_gate["blocked_promotion_count"]
    )
    assert (
        manifest["latest_claim_basis_promotion_gate_can_emit_field_claim_upgrade"]
        == promotion_gate["can_emit_field_claim_upgrade"]
    )
    assert manifest["latest_claim_basis_promotion_gate_can_write_to_actuator"] is False
    assert manifest["latest_claim_basis_promotion_gate_can_write_to_release_gate"] is False


def test_manifest_exposes_agent50_claim_basis_promotion_gate_summary() -> None:
    manifest = _read_json(MANIFEST)
    agent50 = _read_json(AGENT50_PAYLOAD)
    scorecard = agent50["model_core_optimization_governance"]["metrics"]["governance_scorecard"]

    assert (
        manifest["latest_agent50_claim_basis_promotion_gate_status"]
        == scorecard["claim_basis_promotion_gate_status"]
    )
    assert (
        manifest["latest_agent50_claim_basis_promotion_ready_count"]
        == scorecard["claim_basis_promotion_ready_count"]
    )
    assert (
        manifest["latest_agent50_claim_basis_promotion_blocked_count"]
        == scorecard["claim_basis_promotion_blocked_count"]
    )
    assert (
        manifest["latest_agent50_claim_basis_promotion_can_emit_field_claim_upgrade"]
        == scorecard["claim_basis_promotion_can_emit_field_claim_upgrade"]
    )
    assert manifest["latest_agent50_claim_basis_promotion_can_write_to_actuator"] is False
    assert manifest["latest_agent50_claim_basis_promotion_can_write_to_release_gate"] is False


def _read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _grey_box_lifecycle_row(core_interface: dict[str, object]) -> dict[str, object]:
    facades = core_interface["facades"]
    assert isinstance(facades, dict)
    lifecycle = facades["external_package_lifecycle"]
    assert isinstance(lifecycle, dict)
    rows = lifecycle["package_lifecycle_rows"]
    assert isinstance(rows, list)
    return next(row for row in rows if isinstance(row, dict) and row["package_key"] == "grey_box_calibration")

from water_ai.stage_boundary_external_action_board import (
    build_stage_boundary_external_action_board,
    stage_boundary_external_action_board_report_md,
)


def test_stage_boundary_action_board_orders_external_inputs_without_internal_expansion() -> None:
    board = build_stage_boundary_external_action_board(
        core_gate=_core_gate(),
        external_activation_operator_action_packet=_external_operator_packet(),
        formal_search_nonlegal_review_operator_packet=_formal_operator_packet(),
        focused_catalyst_response_merge_metrics=_focused_merge_metrics(),
    )

    metadata = board["board_metadata"]
    stage = board["stage_boundary"]
    summary = board["action_summary"]
    rows = {row["channel_id"]: row for row in board["action_rows"]}
    boundary = board["boundary"]

    assert metadata["board_id"] == "R8u139_stage_boundary_external_action_board"
    assert metadata["board_status"] == (
        "stage_boundary_external_action_board_waiting_for_external_inputs"
    )
    assert stage["internal_expansion_allowed"] is False
    assert stage["core_score"] == 0.96
    assert stage["iteration_delta"] == 0.0
    assert summary["action_count"] == 4
    assert summary["external_wait_count"] == 3
    assert summary["model_chain_resume_ready_count"] == 0
    assert summary["handoff_ready_count"] == 1
    assert summary["highest_priority_action_id"] == "R8u139_R7_REAL_FIELD_PACKAGE"
    assert summary["highest_priority_source_env_var"] == "FOCUSED_CATALYST_RESPONSE_PATH"
    assert summary["highest_priority_focused_candidate_availability_status"] == (
        "candidate_not_submittable_waiting_for_FOCUSED_CATALYST_RESPONSE_PATH"
    )
    assert summary["highest_priority_focused_candidate_submit_ready"] is False
    assert (
        summary["highest_priority_focused_candidate_operator_packet_submit_ready"]
        is False
    )

    assert rows["R7_REAL_FIELD_PACKAGE"]["priority_order"] == 1
    assert rows["R7_REAL_FIELD_PACKAGE"]["source_env_var"] == "FOCUSED_CATALYST_RESPONSE_PATH"
    assert rows["R7_REAL_FIELD_PACKAGE"]["expected_input_row_count"] == 6
    assert rows["R7_REAL_FIELD_PACKAGE"]["target_hidden_state"] == "catalyst_activity"
    assert rows["R7_REAL_FIELD_PACKAGE"]["linked_operator_packet_status"] == (
        "operator_packet_waiting_for_focused_catalyst_response"
    )
    assert rows["R7_REAL_FIELD_PACKAGE"]["current_model_chain_resume_ready"] is False
    assert rows["R7_REAL_FIELD_PACKAGE"]["focused_merge_preflight_status"] == (
        "focused_catalyst_response_merge_waiting_for_FOCUSED_CATALYST_RESPONSE_PATH"
    )
    assert rows["R7_REAL_FIELD_PACKAGE"]["focused_candidate_availability_status"] == (
        "candidate_not_submittable_waiting_for_FOCUSED_CATALYST_RESPONSE_PATH"
    )
    assert rows["R7_REAL_FIELD_PACKAGE"]["focused_candidate_self_declared_submit_ready"] is False
    assert rows["R7_REAL_FIELD_PACKAGE"]["focused_candidate_operator_packet_submit_ready"] is False
    assert rows["R7_REAL_FIELD_PACKAGE"]["focused_candidate_submit_ready"] is False
    assert rows["R7_REAL_FIELD_PACKAGE"]["focused_candidate_external_response_supplied"] is False
    assert (
        rows["R7_REAL_FIELD_PACKAGE"][
            "focused_candidate_can_submit_as_FIELD_ACTIVATION_RESPONSE_PATH"
        ]
        is False
    )
    assert rows["R7_REAL_FIELD_PACKAGE"]["can_write_to_actuator"] is False
    assert rows["R7_REAL_FIELD_PACKAGE"]["can_write_to_release_gate"] is False
    assert board["operator_runbook"][0]["focused_candidate_availability_status"] == (
        "candidate_not_submittable_waiting_for_FOCUSED_CATALYST_RESPONSE_PATH"
    )
    assert board["operator_runbook"][0]["focused_candidate_operator_packet_submit_ready"] is False
    assert board["operator_runbook"][0]["focused_candidate_submit_ready"] is False

    assert rows["R8U79_FORMAL_SEARCH_RESULT_PACKAGE"]["priority_order"] == 3
    assert rows["R8U79_FORMAL_SEARCH_RESULT_PACKAGE"]["handoff_only"] is True
    assert rows["R8U79_FORMAL_SEARCH_RESULT_PACKAGE"]["current_handoff_ready"] is True
    assert (
        rows["R8U79_FORMAL_SEARCH_RESULT_PACKAGE"]["current_model_chain_resume_ready"]
        is False
    )
    assert rows["R8U79_FORMAL_SEARCH_RESULT_PACKAGE"]["source_env_var"] == (
        "FORMAL_SEARCH_NONLEGAL_REVIEW_RESPONSE_PATH"
    )
    assert rows["R8U79_FORMAL_SEARCH_RESULT_PACKAGE"]["expected_input_row_count"] == 7
    assert rows["R8U79_FORMAL_SEARCH_RESULT_PACKAGE"]["can_route_to_claim_scope_patch_draft"] is False
    assert rows["R8U79_FORMAL_SEARCH_RESULT_PACKAGE"]["can_emit_claim_text"] is False

    assert rows["NEW_CORE_INTERFACE"]["requires_tested_interface"] is True
    assert rows["NEW_CORE_INTERFACE"]["requires_external_input"] is False
    assert boundary["can_generate_field_evidence"] is False
    assert boundary["can_resume_model_chain_without_external_gate"] is False
    assert boundary["legal_opinion_allowed"] is False
    assert boundary["can_emit_claim_text"] is False
    assert boundary["can_write_to_actuator"] is False
    assert boundary["can_write_to_release_gate"] is False


def test_stage_boundary_action_board_marks_resume_candidate_only_after_core_gate_ready() -> None:
    core_gate = _core_gate()
    for row in core_gate["next_allowed_actions"]:
        if row["channel_id"] == "R7_REAL_FIELD_PACKAGE":
            row["current_model_chain_resume_ready"] = True
            row["current_route_ready"] = True
            row["can_resume_model_chain"] = True

    board = build_stage_boundary_external_action_board(
        core_gate=core_gate,
        external_activation_operator_action_packet=_external_operator_packet(),
        formal_search_nonlegal_review_operator_packet=_formal_operator_packet(),
    )

    assert board["board_metadata"]["board_status"] == (
        "stage_boundary_external_action_board_has_model_chain_resume_candidate"
    )
    assert board["action_summary"]["model_chain_resume_ready_count"] == 1
    assert board["boundary"]["can_write_to_actuator"] is False
    assert board["boundary"]["can_write_to_release_gate"] is False


def test_stage_boundary_action_board_blocks_self_declared_candidate_without_operator_packet_ready() -> None:
    metrics = _focused_merge_metrics()
    metrics["merged_full_response_candidate_self_declared_submit_ready"] = True
    metrics["merged_full_response_candidate_external_response_supplied"] = True
    metrics["can_submit_candidate_as_FIELD_ACTIVATION_RESPONSE_PATH"] = False
    metrics["row_preflight_pass"] = False
    operator_packet = _external_operator_packet()
    operator_packet["focused_candidate_operator_packet_submit_ready"] = False

    board = build_stage_boundary_external_action_board(
        core_gate=_core_gate(),
        external_activation_operator_action_packet=operator_packet,
        formal_search_nonlegal_review_operator_packet=_formal_operator_packet(),
        focused_catalyst_response_merge_metrics=metrics,
    )

    summary = board["action_summary"]
    row = {
        item["channel_id"]: item for item in board["action_rows"]
    }["R7_REAL_FIELD_PACKAGE"]

    assert row["focused_candidate_self_declared_submit_ready"] is True
    assert row["focused_candidate_operator_packet_submit_ready"] is False
    assert row["focused_candidate_submit_ready"] is False
    assert summary["highest_priority_focused_candidate_submit_ready"] is False
    assert (
        summary["highest_priority_focused_candidate_operator_packet_submit_ready"]
        is False
    )


def test_stage_boundary_action_board_allows_submit_ready_only_after_packet_and_preflight_pass() -> None:
    metrics = _focused_merge_metrics()
    metrics["merged_full_response_candidate_self_declared_submit_ready"] = True
    metrics["merged_full_response_candidate_external_response_supplied"] = True
    metrics["can_submit_candidate_as_FIELD_ACTIVATION_RESPONSE_PATH"] = True
    metrics["row_preflight_pass"] = True
    operator_packet = _external_operator_packet()
    operator_packet["focused_candidate_operator_packet_submit_ready"] = True

    board = build_stage_boundary_external_action_board(
        core_gate=_core_gate(),
        external_activation_operator_action_packet=operator_packet,
        formal_search_nonlegal_review_operator_packet=_formal_operator_packet(),
        focused_catalyst_response_merge_metrics=metrics,
    )

    row = {
        item["channel_id"]: item for item in board["action_rows"]
    }["R7_REAL_FIELD_PACKAGE"]

    assert row["focused_candidate_operator_packet_submit_ready"] is True
    assert row["focused_candidate_submit_ready"] is True
    assert board["action_summary"]["highest_priority_focused_candidate_submit_ready"] is True


def test_stage_boundary_action_board_report_surfaces_priority_and_no_write_boundary() -> None:
    board = build_stage_boundary_external_action_board(
        core_gate=_core_gate(),
        external_activation_operator_action_packet=_external_operator_packet(),
        formal_search_nonlegal_review_operator_packet=_formal_operator_packet(),
        focused_catalyst_response_merge_metrics=_focused_merge_metrics(),
    )

    report_md = stage_boundary_external_action_board_report_md(board)

    assert "FOCUSED_CATALYST_RESPONSE_PATH" in report_md
    assert "candidate_not_submittable_waiting_for_FOCUSED_CATALYST_RESPONSE_PATH" in report_md
    assert "highest_priority_focused_candidate_operator_packet_submit_ready: `False`" in report_md
    assert "highest_priority_focused_candidate_submit_ready: `False`" in report_md
    assert "FORMAL_SEARCH_NONLEGAL_REVIEW_RESPONSE_PATH" in report_md
    assert "can_write_to_actuator: `False`" in report_md
    assert "can_write_to_release_gate: `False`" in report_md
    assert "model_chain_resume_ready_count: `0`" in report_md


def test_stage_boundary_action_board_surfaces_ranked_new_core_interface_candidate() -> None:
    board = build_stage_boundary_external_action_board(
        core_gate=_core_gate(),
        external_activation_operator_action_packet=_external_operator_packet(),
        formal_search_nonlegal_review_operator_packet=_formal_operator_packet(),
        focused_catalyst_response_merge_metrics=_focused_merge_metrics(),
        new_core_interface_candidate_gate=_new_core_interface_candidate_gate(),
    )

    summary = board["action_summary"]
    rows = {row["channel_id"]: row for row in board["action_rows"]}
    new_core_row = rows["NEW_CORE_INTERFACE"]
    report_md = stage_boundary_external_action_board_report_md(board)

    assert summary["new_core_interface_candidate_gate_status"] == (
        "new_core_interface_candidate_gate_ready_with_ranked_contracts"
    )
    assert summary["new_core_interface_highest_priority_candidate_id"] == (
        "NCI1_GREY_BOX_CALIBRATION_PACKAGE"
    )
    assert summary["new_core_interface_highest_priority_source_env_var"] == (
        "GREY_BOX_CALIBRATION_PACKAGE_DIR"
    )
    assert summary["new_core_interface_highest_priority_preflight_status"] == (
        "grey_box_calibration_package_waiting_for_GREY_BOX_CALIBRATION_PACKAGE_DIR"
    )
    assert summary["new_core_interface_highest_priority_preflight_pass"] is False
    assert summary["new_core_interface_highest_priority_downstream_calibration_status"] == (
        "grey_box_field_calibration_waiting_for_preflight_ready"
    )
    assert summary["new_core_interface_highest_priority_can_route_to_downstream_interface"] is False
    assert summary["new_core_interface_highest_priority_downstream_interface_status"] == (
        "grey_box_field_calibration_waiting_for_preflight_ready"
    )
    assert summary["new_core_interface_highest_priority_can_run_agent53_field_calibration"] is False
    assert summary["new_core_interface_highest_priority_agent53_field_candidate_ready"] is False
    assert new_core_row["source_env_var"] == "GREY_BOX_CALIBRATION_PACKAGE_DIR"
    assert new_core_row["validation_command"] == (
        ".venv/bin/python experiments/run_grey_box_calibration_package_preflight.py"
    )
    assert new_core_row["requires_tested_interface"] is True
    assert new_core_row["requires_external_input"] is False
    assert new_core_row["new_core_interface_highest_priority_preflight_status"] == (
        "grey_box_calibration_package_waiting_for_GREY_BOX_CALIBRATION_PACKAGE_DIR"
    )
    assert new_core_row["new_core_interface_highest_priority_preflight_pass"] is False
    assert new_core_row["new_core_interface_highest_priority_downstream_calibration_status"] == (
        "grey_box_field_calibration_waiting_for_preflight_ready"
    )
    assert new_core_row["new_core_interface_highest_priority_can_route_to_downstream_interface"] is False
    assert new_core_row["new_core_interface_highest_priority_downstream_interface_status"] == (
        "grey_box_field_calibration_waiting_for_preflight_ready"
    )
    assert new_core_row["new_core_interface_highest_priority_can_run_agent53_field_calibration"] is False
    assert new_core_row["new_core_interface_highest_priority_agent53_field_candidate_ready"] is False
    assert new_core_row["new_core_interface_can_generate_field_evidence"] is False
    assert new_core_row["new_core_interface_can_write_to_actuator"] is False
    assert new_core_row["new_core_interface_can_write_to_release_gate"] is False
    assert board["operator_runbook"][-1]["new_core_interface_highest_priority_candidate_id"] == (
        "NCI1_GREY_BOX_CALIBRATION_PACKAGE"
    )
    assert "## New Core Interface Candidate" in report_md
    assert "NCI1_GREY_BOX_CALIBRATION_PACKAGE" in report_md
    assert "GREY_BOX_CALIBRATION_PACKAGE_DIR" in report_md
    assert "grey_box_calibration_package_waiting_for_GREY_BOX_CALIBRATION_PACKAGE_DIR" in report_md


def test_stage_boundary_action_board_surfaces_new_core_acquisition_termination_snapshot() -> None:
    board = build_stage_boundary_external_action_board(
        core_gate=_core_gate(),
        external_activation_operator_action_packet=_external_operator_packet(),
        formal_search_nonlegal_review_operator_packet=_formal_operator_packet(),
        focused_catalyst_response_merge_metrics=_focused_merge_metrics(),
        new_core_interface_candidate_gate=_new_core_interface_candidate_gate(),
    )

    summary = board["action_summary"]
    rows = {row["channel_id"]: row for row in board["action_rows"]}
    runbook = {step["channel_id"]: step for step in board["operator_runbook"]}
    new_core_row = rows["NEW_CORE_INTERFACE"]
    report_md = stage_boundary_external_action_board_report_md(board)

    assert summary["new_core_interface_acquisition_contract_termination_status"] == (
        "external_package_contracts_complete_but_waiting_for_field_packages"
    )
    assert summary["new_core_interface_acquisition_module_stage_termination_pass"] is False
    assert summary["new_core_interface_acquisition_downstream_reconnection_rate"] == 0.0
    assert summary["new_core_interface_acquisition_field_package_ready_rate"] == 0.0
    assert summary["new_core_interface_acquisition_termination_blockers"] == [
        "downstream_reconnection_rate_below_0.80",
        "field_package_ready_rate_below_1.00",
    ]
    assert new_core_row["new_core_interface_acquisition_contract_termination_status"] == (
        "external_package_contracts_complete_but_waiting_for_field_packages"
    )
    assert new_core_row["new_core_interface_acquisition_module_stage_termination_pass"] is False
    assert new_core_row["new_core_interface_acquisition_termination_blockers"] == [
        "downstream_reconnection_rate_below_0.80",
        "field_package_ready_rate_below_1.00",
    ]
    assert runbook["NEW_CORE_INTERFACE"][
        "new_core_interface_acquisition_contract_termination_status"
    ] == "external_package_contracts_complete_but_waiting_for_field_packages"
    assert "new_core_interface_acquisition_contract_termination_status" in report_md
    assert "downstream_reconnection_rate_below_0.80" in report_md


def test_stage_boundary_action_board_exposes_machine_handoff_for_low_friction_resume() -> None:
    board = build_stage_boundary_external_action_board(
        core_gate=_core_gate(),
        external_activation_operator_action_packet=_external_operator_packet(),
        formal_search_nonlegal_review_operator_packet=_formal_operator_packet(),
        focused_catalyst_response_merge_metrics=_focused_merge_metrics(),
        new_core_interface_candidate_gate=_new_core_interface_candidate_gate(),
    )

    handoff = board["machine_handoff"]
    report_md = stage_boundary_external_action_board_report_md(board)

    assert handoff["handoff_id"] == "R8u169_stage_boundary_external_action_machine_handoff"
    assert handoff["current_stage"] == "stage_boundary_external_activation"
    assert handoff["route_event"] == "external_activation_wait"
    assert handoff["next_route"] == (
        "submit_real_external_input_then_rerun_stage_preflight_and_agent50"
    )
    assert handoff["next_route_source_env_var"] == "FOCUSED_CATALYST_RESPONSE_PATH"
    assert handoff["next_route_validation_command"] == (
        ".venv/bin/python experiments/run_focused_catalyst_response_merge.py"
    )
    assert handoff["manual_action_required"]["required"] is True
    assert handoff["manual_action_required"]["source_env_var"] == (
        "FOCUSED_CATALYST_RESPONSE_PATH"
    )
    assert handoff["manual_action_required"]["action"] == (
        "fill_outputs/catalyst_response_submission_kit/"
        "focused_catalyst_response_template.json_with_real_field_values_then_set_"
        "FOCUSED_CATALYST_RESPONSE_PATH"
    )
    assert handoff["manual_action_required"]["input_template_path"] == (
        "outputs/catalyst_response_submission_kit/focused_catalyst_response_template.json"
    )
    assert handoff["manual_action_required"]["schema_path"] == (
        "outputs/catalyst_response_submission_kit/focused_catalyst_response_schema.json"
    )
    assert handoff["manual_action_required"]["command_sequence"] == [
        "fill outputs/catalyst_response_submission_kit/focused_catalyst_response_template.json with real field values",
        "export FOCUSED_CATALYST_RESPONSE_PATH=/absolute/path/to/filled_focused_response.json",
        ".venv/bin/python experiments/run_focused_catalyst_response_merge.py",
    ]
    assert handoff["manual_action_required"]["rejection_boundaries"] == [
        "Reject template/sample/synthetic rows as field evidence.",
        "Reject rows with TODO/template markers in required evidence payloads.",
    ]
    assert handoff["manual_action_required"]["boundary_checks"] == [
        {"check_id": "template_rows_are_not_field_evidence", "pass": True}
    ]
    assert "cannot generate field evidence" in handoff["manual_action_required"]["no_write_boundary"]
    assert handoff["current_basis_refs"] == [
        "core_gate.stage_decision",
        "core_gate.next_allowed_actions",
        "external_activation_operator_action_packet",
        "focused_catalyst_response_merge_metrics",
        "formal_search_nonlegal_review_operator_packet",
        "new_core_interface_candidate_gate",
        "core_gate.external_package_acquisition_stage_gate",
    ]
    assert "synthetic_rows" in handoff["not_current_basis_refs"]
    assert "template_rows" in handoff["not_current_basis_refs"]
    assert "field treatment performance" in handoff["cannot_prove"]
    assert "which external action is currently highest priority" in handoff["can_prove"]
    assert handoff["no_write_boundary_preserved"] is True
    assert handoff["can_generate_field_evidence"] is False
    assert handoff["can_resume_model_chain"] is False
    assert handoff["can_write_to_actuator"] is False
    assert handoff["can_write_to_release_gate"] is False
    assert "## Machine Handoff" in report_md
    assert "route_event: `external_activation_wait`" in report_md
    assert "not_current_basis_refs" in report_md


def test_stage_boundary_action_board_scores_machine_handoff_contract_completeness() -> None:
    board = build_stage_boundary_external_action_board(
        core_gate=_core_gate(),
        external_activation_operator_action_packet=_external_operator_packet(),
        formal_search_nonlegal_review_operator_packet=_formal_operator_packet(),
        focused_catalyst_response_merge_metrics=_focused_merge_metrics(),
        new_core_interface_candidate_gate=_new_core_interface_candidate_gate(),
    )

    gate = board["machine_handoff_contract_gate"]
    report_md = stage_boundary_external_action_board_report_md(board)

    assert gate["gate_id"] == "R8u170_stage_boundary_machine_handoff_contract_gate"
    assert gate["gate_status"] == (
        "machine_handoff_contract_complete_waiting_for_external_input"
    )
    assert gate["contract_stage_pass"] is True
    assert gate["contract_score"] == 1.0
    assert gate["thresholds"] == {
        "route_contract_completeness": 1.0,
        "manual_action_contract_completeness": 1.0,
        "basis_boundary_completeness": 1.0,
        "proof_boundary_completeness": 1.0,
        "no_write_boundary_completeness": 1.0,
        "recovery_linkage_completeness": 1.0,
    }
    assert gate["route_contract_completeness"] == 1.0
    assert gate["manual_action_contract_completeness"] == 1.0
    assert gate["basis_boundary_completeness"] == 1.0
    assert gate["proof_boundary_completeness"] == 1.0
    assert gate["no_write_boundary_completeness"] == 1.0
    assert gate["recovery_linkage_completeness"] == 1.0
    assert gate["contract_blockers"] == []
    assert gate["external_wait_blockers"] == ["real_external_input_required"]
    assert gate["can_generate_field_evidence"] is False
    assert gate["can_resume_model_chain"] is False
    assert gate["can_write_to_actuator"] is False
    assert gate["can_write_to_release_gate"] is False
    assert "machine_handoff_contract_gate_status" in report_md
    assert "machine_handoff_contract_score: `1.0`" in report_md


def test_stage_boundary_action_board_scores_low_friction_round_gate() -> None:
    board = build_stage_boundary_external_action_board(
        core_gate=_core_gate(),
        external_activation_operator_action_packet=_external_operator_packet(),
        formal_search_nonlegal_review_operator_packet=_formal_operator_packet(),
        focused_catalyst_response_merge_metrics=_focused_merge_metrics(),
        new_core_interface_candidate_gate=_new_core_interface_candidate_gate(),
    )

    gate = board["low_friction_round_gate"]
    summary = board["action_summary"]
    report_md = stage_boundary_external_action_board_report_md(board)

    assert gate["gate_id"] == "R8u177_low_friction_round_gate"
    assert gate["gate_status"] == "low_friction_single_action_waiting_for_external_input"
    assert gate["evidence_level"] == "governance_contract_not_field_evidence"
    assert gate["round_score"] == 1.0
    assert gate["selected_action_count"] == 1
    assert gate["selected_action_id"] == summary["highest_priority_action_id"]
    assert gate["selected_canonical_action_id"] == "FIELD_ACTIVATION_RESPONSE_FOCUS_HANDOFF_NEXT_ACTION"
    assert gate["selected_underlying_action_id"] == "R8u139_R7_REAL_FIELD_PACKAGE"
    assert gate["selected_source_env_var"] == "FOCUSED_CATALYST_RESPONSE_PATH"
    assert gate["user_burden_shifted"] is False
    assert gate["machine_writeback_required"] is True
    assert gate["manual_action_required"]["required"] is True
    assert gate["manual_action_required"]["source_env_var"] == "FOCUSED_CATALYST_RESPONSE_PATH"
    assert gate["manual_action_required"]["input_template_path"] == (
        "outputs/catalyst_response_submission_kit/focused_catalyst_response_template.json"
    )
    assert gate["manual_action_required"]["command_sequence"] == [
        "fill outputs/catalyst_response_submission_kit/focused_catalyst_response_template.json with real field values",
        "export FOCUSED_CATALYST_RESPONSE_PATH=/absolute/path/to/filled_focused_response.json",
        ".venv/bin/python experiments/run_focused_catalyst_response_merge.py",
    ]
    assert gate["manual_action_required"]["rejection_boundaries"] == [
        "Reject template/sample/synthetic rows as field evidence.",
        "Reject rows with TODO/template markers in required evidence payloads.",
    ]
    assert gate["manual_action_required"]["boundary_checks"] == [
        {"check_id": "template_rows_are_not_field_evidence", "pass": True}
    ]
    assert "cannot generate field evidence" in gate["manual_action_required"]["no_write_boundary"]
    assert gate["manual_action_required"]["validation_command"] == (
        ".venv/bin/python experiments/run_focused_catalyst_response_merge.py"
    )
    assert gate["manual_action_required"]["resume_evidence"]
    assert gate["termination_contract"]["continue_expansion_allowed"] is False
    assert gate["termination_contract"]["route_event"] == "external_activation_wait"
    assert gate["termination_contract"]["next_route"] == (
        "submit_real_external_input_then_rerun_stage_preflight_and_agent50"
    )
    assert gate["can_generate_field_evidence"] is False
    assert gate["can_write_to_actuator"] is False
    assert gate["can_write_to_release_gate"] is False
    assert gate["field_claim_upgrade_allowed"] is False
    assert "## Low Friction Round Gate" in report_md
    assert "low_friction_round_gate_status" in report_md


def test_stage_boundary_action_board_exposes_claim_basis_promotion_snapshot() -> None:
    board = build_stage_boundary_external_action_board(
        core_gate=_core_gate(),
        external_activation_operator_action_packet=_external_operator_packet(),
        formal_search_nonlegal_review_operator_packet=_formal_operator_packet(),
        focused_catalyst_response_merge_metrics=_focused_merge_metrics(),
        new_core_interface_candidate_gate=_new_core_interface_candidate_gate(),
        claim_basis_promotion_gate=_claim_basis_promotion_gate(),
    )

    snapshot = board["claim_basis_promotion_snapshot"]
    report_md = stage_boundary_external_action_board_report_md(board)

    assert snapshot["snapshot_status"] == "claim_basis_promotion_blocked_until_field_validation"
    assert snapshot["promotion_decision_count"] == 5
    assert snapshot["ready_promotion_count"] == 0
    assert snapshot["blocked_promotion_count"] == 5
    assert snapshot["can_emit_field_claim_upgrade"] is False
    assert snapshot["can_write_to_actuator"] is False
    assert snapshot["can_write_to_release_gate"] is False
    assert snapshot["stage_boundary_effect"] == (
        "keep_external_wait_until_real_field_validation_and_human_review"
    )
    assert "## Claim Basis Promotion Snapshot" in report_md
    assert "claim_basis_promotion_snapshot_status" in report_md


def test_stage_boundary_action_board_exposes_resource_boundary_gate() -> None:
    board = build_stage_boundary_external_action_board(
        core_gate=_core_gate(),
        external_activation_operator_action_packet=_external_operator_packet(),
        formal_search_nonlegal_review_operator_packet=_formal_operator_packet(),
        focused_catalyst_response_merge_metrics=_focused_merge_metrics(),
        new_core_interface_candidate_gate=_new_core_interface_candidate_gate(),
    )

    boundary = board["resource_boundary"]
    gate = board["resource_boundary_gate"]
    report_md = stage_boundary_external_action_board_report_md(board)

    assert boundary["boundary_id"] == "R8u171_stage_boundary_resource_boundary"
    assert "verified_stage_boundary_gates" in boundary["allowed_basis"]
    assert "template_rows_as_field_evidence" in boundary["forbidden_basis"]
    assert "literature_only_rows_as_field_evidence" in boundary["forbidden_basis"]
    assert "protocol_as_governance_pattern_not_domain_evidence" in boundary[
        "official_supplementary_basis"
    ]
    assert "external_package_supplied_but_not_preflighted" in boundary["gray_zone"]
    assert boundary["external_model_or_tool_policy"]["can_use_for_governance"] is True
    assert boundary["external_model_or_tool_policy"]["can_emit_legal_or_patent_conclusion"] is False
    assert boundary["manual_annotation_or_human_labeling_policy"]["manual_action_required"] is True
    assert boundary["no_write_policy"]["can_write_to_actuator"] is False
    assert boundary["no_write_policy"]["can_write_to_release_gate"] is False

    assert gate["gate_id"] == "R8u171_stage_boundary_resource_boundary_gate"
    assert gate["gate_status"] == (
        "resource_boundary_complete_waiting_for_real_external_input"
    )
    assert gate["resource_boundary_score"] == 1.0
    assert gate["resource_boundary_stage_pass"] is True
    assert gate["thresholds"] == {
        "allowed_basis_completeness": 1.0,
        "forbidden_basis_completeness": 1.0,
        "supplementary_basis_completeness": 1.0,
        "gray_zone_completeness": 1.0,
        "tool_policy_completeness": 1.0,
        "manual_annotation_policy_completeness": 1.0,
        "no_write_policy_completeness": 1.0,
    }
    assert gate["resource_boundary_blockers"] == []
    assert gate["external_wait_blockers"] == ["real_external_input_required"]
    assert gate["can_generate_field_evidence"] is False
    assert gate["can_write_to_actuator"] is False
    assert gate["can_write_to_release_gate"] is False
    assert "## Resource Boundary" in report_md
    assert "resource_boundary_gate_status" in report_md
    assert "resource_boundary_score: `1.0`" in report_md


def test_stage_boundary_action_board_exposes_subagent_orchestration_probe() -> None:
    board = build_stage_boundary_external_action_board(
        core_gate=_core_gate(),
        external_activation_operator_action_packet=_external_operator_packet(),
        formal_search_nonlegal_review_operator_packet=_formal_operator_packet(),
        focused_catalyst_response_merge_metrics=_focused_merge_metrics(),
        new_core_interface_candidate_gate=_new_core_interface_candidate_gate(),
    )

    probe = board["subagent_orchestration_probe"]
    report_md = stage_boundary_external_action_board_report_md(board)

    assert probe["probe_id"] == "R8u175_stage_boundary_subagent_orchestration_probe"
    assert probe["probe_status"] == "subagent_orchestration_not_needed_for_external_wait"
    assert probe["capability"] == "not_needed"
    assert probe["strategy"] == "not_needed"
    assert probe["no_spawn_reason"] == (
        "current_stage_is_external_activation_wait_and_no_parallel_internal_task_is_required"
    )
    assert probe["capability_probe"]["tool_discovered"] is False
    assert probe["capability_probe"]["spawn_attempted"] is False
    assert probe["capability_probe"]["wait_status"] == "not_started"
    assert probe["capability_probe"]["integration_decision"] == "not_needed"
    assert probe["lifecycle_cleanup"]["close_attempted"] is False
    assert probe["lifecycle_cleanup"]["close_status"] == "not_needed"
    assert probe["lifecycle_cleanup"]["open_agent_cleanup_required"] is False
    assert probe["roles"] == []
    assert probe["manual_proxy_needed"] is False
    assert probe["can_delegate_goal_completion"] is False
    assert probe["can_generate_field_evidence"] is False
    assert "## Subagent Orchestration Probe" in report_md
    assert "subagent_orchestration_probe_status" in report_md


def test_stage_boundary_action_board_exposes_protocol_adapted_internal_expansion_saturation_gate() -> None:
    board = build_stage_boundary_external_action_board(
        core_gate=_core_gate(),
        external_activation_operator_action_packet=_external_operator_packet(),
        formal_search_nonlegal_review_operator_packet=_formal_operator_packet(),
        focused_catalyst_response_merge_metrics=_focused_merge_metrics(),
        new_core_interface_candidate_gate=_new_core_interface_candidate_gate(),
        claim_basis_promotion_gate=_claim_basis_promotion_gate(),
    )

    gate = board["internal_expansion_saturation_gate"]
    report_md = stage_boundary_external_action_board_report_md(board)

    assert gate["gate_id"] == "R8u186_stage_boundary_internal_expansion_saturation_gate"
    assert gate["gate_status"] == "internal_expansion_saturated_waiting_for_external_input"
    assert gate["source_protocol"] == (
        "complex_project_startup_governance_protocol_v3_core_selected_rules"
    )
    assert "anti_protocol_bloat_gate" in gate["adopted_protocol_principles"]
    assert "continuous_cycle_no_idle_expansion" in gate["adopted_protocol_principles"]
    assert gate["model_core_boundary_layer"] == "verification_governance"
    assert gate["decision"] == "stop_internal_micro_expansion_wait_for_real_external_input"
    assert gate["internal_expansion_allowed"] is False
    assert gate["micro_tweak_expansion_allowed"] is False
    assert gate["current_external_blocker"] == "FOCUSED_CATALYST_RESPONSE_PATH"
    assert gate["required_next_external_input"] == "FOCUSED_CATALYST_RESPONSE_PATH"
    assert gate["required_validation_command"] == (
        ".venv/bin/python experiments/run_focused_catalyst_response_merge.py"
    )
    assert gate["iteration_delta"] == 0.0
    assert gate["delta_threshold"] == 0.05
    assert gate["gate_score"] == 1.0
    assert gate["claim_readiness_ceiling"] == (
        "governance_contract_only_until_real_field_validation"
    )
    assert gate["stop_reasons"] == [
        "core_score_iteration_delta_below_0.05",
        "stage_decision_waits_for_external_activation",
        "low_friction_gate_has_single_action",
        "focused_candidate_not_submittable_without_real_external_input",
        "machine_handoff_contract_complete",
        "resource_boundary_complete",
        "claim_basis_promotion_blocked_until_field_validation",
    ]
    assert gate["resume_conditions"] == [
        "FOCUSED_CATALYST_RESPONSE_PATH_supplied_and_focused_merge_preflight_passed",
        "hard_boundary_contradiction_detected",
        "new_P1_or_P2_model_interface_blocker_identified",
    ]
    assert gate["allowed_internal_work"] == [
        "consume_real_external_input",
        "repair_hard_boundary_contradiction",
        "refresh_artifacts_after_external_input",
        "run_verification_without_expanding_model_logic",
    ]
    assert gate["disallowed_internal_work"] == [
        "add_more_operator_convenience_fields_without_new_boundary_gap",
        "create_additional_synthetic_template_outputs_as_progress",
        "spawn_subagents_for_external_wait_without_parallel_internal_domain",
        "promote_claims_or_control_without_field_package",
    ]
    assert gate["can_generate_field_evidence"] is False
    assert gate["can_write_to_actuator"] is False
    assert gate["can_write_to_release_gate"] is False
    assert "## Internal Expansion Saturation Gate" in report_md
    assert "internal_expansion_saturated_waiting_for_external_input" in report_md


def _core_gate() -> dict[str, object]:
    return {
        "core_score": 0.96,
        "previous_core_score": 0.96,
        "iteration_delta": 0.0,
        "iteration_validity_status": "valid_stage_boundary_external_field_wait",
        "stage_decision": "stop_expansion_wait_for_real_field_package_or_new_core_interface",
        "self_interrupt_verdict": "stage_boundary_wait_for_external_activation",
        "continue_expansion_allowed": False,
        "next_gate_action": "continue_only_on_interfaces_or_packages_that_do_not_fabricate_field_evidence",
        "external_package_acquisition_stage_gate": {
            "contract_termination_status": (
                "external_package_contracts_complete_but_waiting_for_field_packages"
            ),
            "module_stage_termination_pass": False,
            "termination_blockers": [
                "downstream_reconnection_rate_below_0.80",
                "field_package_ready_rate_below_1.00",
            ],
            "downstream_reconnection_rate": 0.0,
            "field_package_ready_rate": 0.0,
            "next_stage_decision": "collect_external_field_packages_before_downstream_gates",
            "next_operator_source_env_var": "GREY_BOX_CALIBRATION_PACKAGE_DIR",
            "next_operator_validation_command": (
                ".venv/bin/python experiments/run_grey_box_calibration_package_preflight.py"
            ),
        },
        "next_allowed_actions": [
            {
                "channel_id": "R7_REAL_FIELD_PACKAGE",
                "activation_route_class": "model_chain_external_package",
                "model_chain_resume_candidate": True,
                "handoff_only": False,
                "requires_tested_interface": False,
                "current_route_ready": False,
                "current_handoff_ready": False,
                "current_model_chain_resume_ready": False,
                "can_resume_model_chain": False,
                "package_pointer": "REAL_FIELD_REPLAY_PACKAGE_DIR",
                "next_operator_action": "repair_metadata_headers_and_real_rows_before_agent42",
                "router_validation_command": ".venv/bin/python experiments/run_external_activation_router.py",
                "boundary": "cannot write actuator policy or release gate",
            },
            {
                "channel_id": "R8U66_PATH_ENDPOINT_LABEL_PACKAGE",
                "activation_route_class": "model_chain_external_package",
                "model_chain_resume_candidate": True,
                "handoff_only": False,
                "requires_tested_interface": False,
                "current_route_ready": False,
                "current_handoff_ready": False,
                "current_model_chain_resume_ready": False,
                "can_resume_model_chain": False,
                "package_pointer": "FIELD_PATH_ENDPOINT_LABEL_PACKAGE_DIR",
                "next_operator_action": "fix_field_path_endpoint_label_package_preflight_blockers",
                "boundary": "cannot write actuator policy or release gate",
            },
            {
                "channel_id": "R8U79_FORMAL_SEARCH_RESULT_PACKAGE",
                "activation_route_class": "formal_search_handoff_only",
                "model_chain_resume_candidate": False,
                "handoff_only": True,
                "requires_tested_interface": False,
                "current_route_ready": True,
                "current_handoff_ready": True,
                "current_model_chain_resume_ready": False,
                "can_resume_model_chain": False,
                "package_pointer": "FORMAL_SEARCH_RESULT_PACKAGE_PATH",
                "next_operator_action": "complete_human_nonlegal_comparison_review_response",
                "formal_nonlegal_review_operator_packet_status": (
                    "formal_search_nonlegal_review_operator_packet_ready_waiting_for_human_response"
                ),
                "formal_nonlegal_review_operator_packet_expected_review_packet_row_count": 7,
                "formal_nonlegal_review_operator_packet_source_env_var": (
                    "FORMAL_SEARCH_NONLEGAL_REVIEW_RESPONSE_PATH"
                ),
                "formal_nonlegal_review_operator_packet_can_route_to_claim_scope_patch_draft": False,
                "formal_nonlegal_review_operator_packet_can_emit_claim_text": False,
                "boundary": "formal-search handoff only; cannot resume field replay or control",
            },
            {
                "channel_id": "NEW_CORE_INTERFACE",
                "activation_route_class": "new_testable_core_interface",
                "model_chain_resume_candidate": False,
                "handoff_only": False,
                "requires_tested_interface": True,
                "current_route_ready": False,
                "current_handoff_ready": False,
                "current_model_chain_resume_ready": False,
                "can_resume_model_chain": False,
                "next_operator_action": "Use field_activation_matrix to prepare state-level external evidence packages.",
                "boundary": "must preserve evidence boundaries",
            },
        ],
    }


def _external_operator_packet() -> dict[str, object]:
    return {
        "packet_status": "operator_packet_waiting_for_focused_catalyst_response",
        "source_env_var": "FOCUSED_CATALYST_RESPONSE_PATH",
        "target_hidden_state": "catalyst_activity",
        "expected_focused_response_row_count": 6,
        "focused_template_path": (
            "outputs/catalyst_response_submission_kit/focused_catalyst_response_template.json"
        ),
        "focused_schema_path": (
            "outputs/catalyst_response_submission_kit/focused_catalyst_response_schema.json"
        ),
        "current_commands": [
            "fill outputs/catalyst_response_submission_kit/focused_catalyst_response_template.json with real field values",
            "export FOCUSED_CATALYST_RESPONSE_PATH=/absolute/path/to/filled_focused_response.json",
            ".venv/bin/python experiments/run_focused_catalyst_response_merge.py",
        ],
        "rejection_boundaries": [
            "Reject template/sample/synthetic rows as field evidence.",
            "Reject rows with TODO/template markers in required evidence payloads.",
        ],
        "boundary_checks": [
            {"check_id": "template_rows_are_not_field_evidence", "pass": True},
        ],
        "no_write_boundary": (
            "This packet only tells an operator how to fill and validate the focused catalyst "
            "response. It cannot generate field evidence."
        ),
        "packet_next_operator_action": (
            "fill_outputs/catalyst_response_submission_kit/"
            "focused_catalyst_response_template.json_with_real_field_values_then_set_"
            "FOCUSED_CATALYST_RESPONSE_PATH"
        ),
        "focused_merge_runner": "experiments/run_focused_catalyst_response_merge.py",
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
    }


def _formal_operator_packet() -> dict[str, object]:
    return {
        "operator_packet_metadata": {
            "packet_status": (
                "formal_search_nonlegal_review_operator_packet_ready_waiting_for_human_response"
            )
        },
        "operator_action": {
            "source_env_var": "FORMAL_SEARCH_NONLEGAL_REVIEW_RESPONSE_PATH",
            "expected_review_packet_row_count": 7,
        },
        "downstream_state": {
            "can_route_to_claim_scope_patch_draft": False,
        },
        "boundary": {
            "can_emit_claim_text": False,
            "can_write_to_actuator": False,
            "can_write_to_release_gate": False,
        },
    }


def _focused_merge_metrics() -> dict[str, object]:
    return {
        "preflight_status": "focused_catalyst_response_merge_waiting_for_FOCUSED_CATALYST_RESPONSE_PATH",
        "row_preflight_pass": False,
        "can_submit_candidate_as_FIELD_ACTIVATION_RESPONSE_PATH": False,
        "merged_full_response_candidate_availability_status": (
            "candidate_not_submittable_waiting_for_FOCUSED_CATALYST_RESPONSE_PATH"
        ),
        "merged_full_response_candidate_self_declared_submit_ready": False,
        "merged_full_response_candidate_external_response_supplied": False,
        "merged_full_response_candidate_use_boundary": (
            "If false, this file is a diagnostic artifact and must not be routed as field evidence."
        ),
        "batch_alignment": {
            "matched_batch_count": 0,
            "minimum_matched_batch_count": 3,
            "matched_batch_requirement_pass": False,
        },
    }


def _new_core_interface_candidate_gate() -> dict[str, object]:
    return {
        "gate_metadata": {
            "gate_status": "new_core_interface_candidate_gate_ready_with_ranked_contracts",
        },
        "candidate_summary": {
            "candidate_count": 1,
            "admissible_candidate_count": 1,
            "highest_priority_candidate_id": "NCI1_GREY_BOX_CALIBRATION_PACKAGE",
            "highest_priority_source_env_var": "GREY_BOX_CALIBRATION_PACKAGE_DIR",
            "highest_priority_system_layer": "state_estimation_and_grey_box_physics",
            "highest_priority_core_ability": "verifiability_and_explainability",
            "highest_priority_validation_command": (
                ".venv/bin/python experiments/run_grey_box_calibration_package_preflight.py"
            ),
            "highest_priority_preflight_status": (
                "grey_box_calibration_package_waiting_for_GREY_BOX_CALIBRATION_PACKAGE_DIR"
            ),
            "highest_priority_preflight_pass": False,
            "highest_priority_can_route_to_downstream_calibration": False,
            "highest_priority_downstream_calibration_status": (
                "grey_box_field_calibration_waiting_for_preflight_ready"
            ),
            "highest_priority_can_route_to_downstream_interface": False,
            "highest_priority_downstream_interface_status": (
                "grey_box_field_calibration_waiting_for_preflight_ready"
            ),
            "highest_priority_can_run_agent53_field_calibration": False,
            "highest_priority_agent53_field_candidate_ready": False,
            "highest_priority_next_interface_action": (
                "define_GREY_BOX_CALIBRATION_PACKAGE_DIR_preflight_before_adding_more_grey_box_logic"
            ),
            "can_generate_field_evidence": False,
            "can_resume_model_chain": False,
            "can_write_to_actuator": False,
            "can_write_to_release_gate": False,
        },
        "candidate_rows": [
            {
                "candidate_id": "NCI1_GREY_BOX_CALIBRATION_PACKAGE",
                "minimum_row_count": 3,
                "input_contract": ["influent_effluent_lab_pairs"],
                "output_contract": ["mass_balance_residual_summary"],
                "failure_boundary": "cannot create field evidence",
            }
        ],
    }


def _claim_basis_promotion_gate() -> dict[str, object]:
    return {
        "gate_status": "claim_basis_promotion_blocked_until_field_validation",
        "promotion_decision_count": 5,
        "ready_promotion_count": 0,
        "blocked_promotion_count": 5,
        "can_emit_field_claim_upgrade": False,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
        "failure_boundary": (
            "field-supported claim candidates require real field package, replay, holdout and human review"
        ),
    }

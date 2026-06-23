from water_ai import external_package_readiness_board as board_module
from water_ai.external_package_readiness_board import (
    BOARD_ID,
    attach_submission_readiness_gap,
    build_external_package_readiness_board,
    external_package_readiness_board_report_md,
)


def test_external_package_readiness_board_aggregates_all_new_core_packages() -> None:
    board = build_external_package_readiness_board(
        new_core_interface_candidate_gate=_candidate_gate(),
        package_artifacts=_artifacts(),
    )

    metadata = board["board_metadata"]
    summary = board["package_summary"]
    rows = {row["candidate_id"]: row for row in board["package_rows"]}

    assert metadata["board_id"] == BOARD_ID
    assert summary["package_count"] == 5
    assert summary["waiting_package_count"] == 5
    assert summary["ready_package_count"] == 0
    assert summary["blocked_package_count"] == 0
    assert summary["unimplemented_package_count"] == 0
    assert summary["all_candidate_interfaces_have_preflight"] is True
    assert summary["next_operator_candidate_id"] == "NCI1_GREY_BOX_CALIBRATION_PACKAGE"
    assert summary["next_operator_source_env_var"] == "GREY_BOX_CALIBRATION_PACKAGE_DIR"
    assert summary["can_generate_field_evidence"] is False
    assert summary["can_write_to_actuator"] is False
    assert summary["can_write_to_release_gate"] is False
    assert rows["NCI1_GREY_BOX_CALIBRATION_PACKAGE"]["template_dir"] == (
        "outputs/grey_box_calibration_package/grey_box_calibration_package_template"
    )
    assert rows["NCI3_FIELD_CONTROL_REPLAY_PACKAGE"]["matched_unit_summary"] == "none"
    assert rows["NCI2_FIELD_MISSINGNESS_REPLAY_PACKAGE"]["can_write_to_release_gate"] is False


def test_external_package_readiness_board_counts_ready_and_blocked_packages() -> None:
    gate = _candidate_gate()
    gate["candidate_rows"][0]["candidate_preflight_pass"] = True
    gate["candidate_rows"][0]["candidate_preflight_status"] = (
        "grey_box_calibration_package_ready_for_agent53_field_calibration"
    )
    gate["candidate_rows"][0]["candidate_matched_batch_count"] = 3
    gate["candidate_rows"][1]["candidate_preflight_status"] = (
        "field_supported_kg_edge_package_blocked_at_schema"
    )

    board = build_external_package_readiness_board(
        new_core_interface_candidate_gate=gate,
        package_artifacts=_artifacts(),
    )

    summary = board["package_summary"]
    rows = {row["candidate_id"]: row for row in board["package_rows"]}

    assert summary["ready_package_count"] == 1
    assert summary["blocked_package_count"] == 1
    assert summary["waiting_package_count"] == 3
    assert summary["next_operator_candidate_id"] == "NCI5_FIELD_SUPPORTED_KG_EDGE_PACKAGE"
    assert summary["next_operator_source_env_var"] == "FIELD_SUPPORTED_KG_EDGE_PACKAGE_DIR"
    assert rows["NCI1_GREY_BOX_CALIBRATION_PACKAGE"]["matched_unit_summary"] == "batch:3"
    assert rows["NCI5_FIELD_SUPPORTED_KG_EDGE_PACKAGE"]["package_preflight_status"] == (
        "field_supported_kg_edge_package_blocked_at_schema"
    )


def test_external_package_readiness_board_report_surfaces_no_write_boundary() -> None:
    board = build_external_package_readiness_board(
        new_core_interface_candidate_gate=_candidate_gate(),
        package_artifacts=_artifacts(),
    )

    report = external_package_readiness_board_report_md(board)

    assert "External Package Readiness Board" in report
    assert "NCI4_SPARSE_TOPOLOGY_INSTALLABILITY_PACKAGE" in report
    assert "FIELD_MISSINGNESS_REPLAY_PACKAGE_DIR" in report
    assert "can_write_to_actuator: `False`" in report
    assert "does not validate field performance" in report


def test_external_package_operator_action_packet_prioritizes_all_waiting_packages() -> None:
    board = build_external_package_readiness_board(
        new_core_interface_candidate_gate=_candidate_gate(),
        package_artifacts=_artifacts(),
    )

    packet = board_module.build_external_package_operator_action_packet(readiness_board=board)

    assert packet["packet_id"] == "R8u155_external_package_operator_action_packet"
    assert packet["packet_status"] == "external_package_operator_packet_waiting_for_field_packages"
    assert packet["source_board_id"] == BOARD_ID
    assert packet["package_count"] == 5
    assert packet["ready_package_count"] == 0
    assert packet["waiting_package_count"] == 5
    assert packet["blocked_package_count"] == 0
    assert packet["next_operator_candidate_id"] == "NCI1_GREY_BOX_CALIBRATION_PACKAGE"
    assert packet["next_operator_source_env_var"] == "GREY_BOX_CALIBRATION_PACKAGE_DIR"
    assert packet["next_operator_validation_command"] == "run_NCI1_GREY_BOX_CALIBRATION_PACKAGE"
    assert packet["operator_actions"][0]["candidate_id"] == "NCI1_GREY_BOX_CALIBRATION_PACKAGE"
    assert packet["operator_actions"][0]["action_status"] == "collect_external_package"
    assert packet["operator_actions"][0]["template_dir"] == (
        "outputs/grey_box_calibration_package/grey_box_calibration_package_template"
    )
    assert packet["operator_actions"][0]["minimum_row_count"] == 3
    assert packet["operator_actions"][0]["run_after_submission"] == [
        "run_NCI1_GREY_BOX_CALIBRATION_PACKAGE"
    ]
    assert packet["operator_actions"][4]["candidate_id"] == "NCI2_FIELD_MISSINGNESS_REPLAY_PACKAGE"
    assert packet["can_generate_field_evidence"] is False
    assert packet["can_resume_model_chain"] is False
    assert packet["can_write_to_actuator"] is False
    assert packet["can_write_to_release_gate"] is False
    assert "Reject template rows" in packet["rejection_rules"][0]


def test_external_package_operator_action_packet_surfaces_grey_box_missing_tables() -> None:
    artifacts = _artifacts()
    artifacts["NCI1_GREY_BOX_CALIBRATION_PACKAGE"].update(
        {
            "submission_gap_type": "missing_external_package",
            "missing_table_count": 5,
            "missing_tables": [
                "batch_inlet_outlet_lab",
                "hydraulic_rtd_or_tracer",
                "oxidant_dose_residual_log",
                "catalyst_age_regeneration_log",
                "byproduct_panel",
            ],
            "submission_source_env_var": "GREY_BOX_CALIBRATION_PACKAGE_DIR",
        }
    )
    board = build_external_package_readiness_board(
        new_core_interface_candidate_gate=_candidate_gate(),
        package_artifacts=artifacts,
    )

    packet = board_module.build_external_package_operator_action_packet(readiness_board=board)

    rows = {row["candidate_id"]: row for row in board["package_rows"]}
    actions = {action["candidate_id"]: action for action in packet["operator_actions"]}
    grey_box_row = rows["NCI1_GREY_BOX_CALIBRATION_PACKAGE"]
    grey_box_action = actions["NCI1_GREY_BOX_CALIBRATION_PACKAGE"]
    assert grey_box_row["submission_gap_type"] == "missing_external_package"
    assert grey_box_row["missing_table_count"] == 5
    assert grey_box_row["missing_tables"] == [
        "batch_inlet_outlet_lab",
        "hydraulic_rtd_or_tracer",
        "oxidant_dose_residual_log",
        "catalyst_age_regeneration_log",
        "byproduct_panel",
    ]
    assert grey_box_action["submission_gap_type"] == "missing_external_package"
    assert grey_box_action["missing_table_count"] == 5
    assert grey_box_action["missing_tables"] == grey_box_row["missing_tables"]
    assert grey_box_action["submission_source_env_var"] == "GREY_BOX_CALIBRATION_PACKAGE_DIR"
    assert grey_box_action["validation_command"] == grey_box_row["validation_command"]
    assert packet["next_operator_submission_gap_type"] == "missing_external_package"
    assert packet["next_operator_missing_table_count"] == 5
    assert packet["next_operator_missing_tables"] == grey_box_row["missing_tables"]
    assert packet["next_operator_template_dir"] == grey_box_row["template_dir"]


def test_external_package_operator_action_packet_exposes_machine_handoff_semantics() -> None:
    artifacts = _artifacts()
    artifacts["NCI1_GREY_BOX_CALIBRATION_PACKAGE"].update(
        {
            "submission_gap_type": "missing_external_package",
            "missing_table_count": 5,
            "missing_tables": [
                "batch_inlet_outlet_lab",
                "hydraulic_rtd_or_tracer",
                "oxidant_dose_residual_log",
                "catalyst_age_regeneration_log",
                "byproduct_panel",
            ],
            "submission_source_env_var": "GREY_BOX_CALIBRATION_PACKAGE_DIR",
        }
    )
    board = build_external_package_readiness_board(
        new_core_interface_candidate_gate=_candidate_gate(),
        package_artifacts=artifacts,
    )

    packet = board_module.build_external_package_operator_action_packet(readiness_board=board)

    assert packet["route_event"] == "external_activation_wait"
    assert packet["route_reason"] == (
        "waiting_for_real_external_package_before_downstream_replay_holdout_calibration"
    )
    assert packet["evidence_level"] == "operator_handoff_only_not_field_evidence"
    assert packet["manual_action_required"]["required"] is True
    assert packet["manual_action_required"]["source_env_var"] == "GREY_BOX_CALIBRATION_PACKAGE_DIR"
    assert packet["manual_action_required"]["template_dir"] == (
        "outputs/grey_box_calibration_package/grey_box_calibration_package_template"
    )
    assert packet["manual_action_required"]["missing_tables"] == [
        "batch_inlet_outlet_lab",
        "hydraulic_rtd_or_tracer",
        "oxidant_dose_residual_log",
        "catalyst_age_regeneration_log",
        "byproduct_panel",
    ]
    assert "readiness_board.package_rows" in packet["current_basis_refs"]
    assert "template_rows" in packet["not_current_basis_refs"]
    assert "next external package to collect" in packet["can_prove"]
    assert "field treatment performance" in packet["cannot_prove"]
    assert "actuator or release-gate readiness" in packet["cannot_prove"]


def test_attach_submission_readiness_gap_copies_missing_table_contract() -> None:
    artifacts = _artifacts()

    enriched = attach_submission_readiness_gap(
        package_artifacts=artifacts,
        candidate_id="NCI1_GREY_BOX_CALIBRATION_PACKAGE",
        submission_readiness_gate={
            "highest_priority_gap": {
                "gap_type": "missing_external_package",
                "missing_table_count": 5,
                "missing_tables": [
                    "batch_inlet_outlet_lab",
                    "hydraulic_rtd_or_tracer",
                    "oxidant_dose_residual_log",
                    "catalyst_age_regeneration_log",
                    "byproduct_panel",
                ],
                "source_env_var": "GREY_BOX_CALIBRATION_PACKAGE_DIR",
            }
        },
    )

    assert "missing_table_count" not in artifacts["NCI1_GREY_BOX_CALIBRATION_PACKAGE"]
    assert enriched["NCI1_GREY_BOX_CALIBRATION_PACKAGE"]["submission_gap_type"] == (
        "missing_external_package"
    )
    assert enriched["NCI1_GREY_BOX_CALIBRATION_PACKAGE"]["missing_table_count"] == 5
    assert enriched["NCI1_GREY_BOX_CALIBRATION_PACKAGE"]["missing_tables"] == [
        "batch_inlet_outlet_lab",
        "hydraulic_rtd_or_tracer",
        "oxidant_dose_residual_log",
        "catalyst_age_regeneration_log",
        "byproduct_panel",
    ]
    assert enriched["NCI1_GREY_BOX_CALIBRATION_PACKAGE"]["submission_source_env_var"] == (
        "GREY_BOX_CALIBRATION_PACKAGE_DIR"
    )


def test_external_package_operator_action_packet_blocks_schema_repairs_before_collection() -> None:
    gate = _candidate_gate()
    gate["candidate_rows"][1]["candidate_preflight_status"] = (
        "field_supported_kg_edge_package_blocked_at_schema"
    )
    board = build_external_package_readiness_board(
        new_core_interface_candidate_gate=gate,
        package_artifacts=_artifacts(),
    )

    packet = board_module.build_external_package_operator_action_packet(readiness_board=board)

    assert packet["packet_status"] == "external_package_operator_packet_blocked_by_preflight_repair"
    assert packet["blocked_package_count"] == 1
    assert packet["next_operator_candidate_id"] == "NCI5_FIELD_SUPPORTED_KG_EDGE_PACKAGE"
    assert packet["next_operator_source_env_var"] == "FIELD_SUPPORTED_KG_EDGE_PACKAGE_DIR"
    assert packet["operator_actions"][1]["action_status"] == "repair_preflight_blocker"
    assert packet["operator_actions"][1]["priority_reason"] == "blocked_preflight_before_collection"


def test_external_package_operator_action_packet_report_surfaces_collection_commands() -> None:
    board = build_external_package_readiness_board(
        new_core_interface_candidate_gate=_candidate_gate(),
        package_artifacts=_artifacts(),
    )
    packet = board_module.build_external_package_operator_action_packet(readiness_board=board)

    report = board_module.external_package_operator_action_packet_report_md(packet)

    assert "External Package Operator Action Packet" in report
    assert "GREY_BOX_CALIBRATION_PACKAGE_DIR" in report
    assert "run_NCI1_GREY_BOX_CALIBRATION_PACKAGE" in report
    assert "does not generate field evidence" in report


def test_external_package_acquisition_maturity_gate_scores_waiting_queue() -> None:
    board = build_external_package_readiness_board(
        new_core_interface_candidate_gate=_candidate_gate(),
        package_artifacts=_artifacts(),
    )
    packet = board_module.build_external_package_operator_action_packet(readiness_board=board)

    gate = board_module.build_external_package_acquisition_maturity_gate(
        readiness_board=board,
        operator_action_packet=packet,
    )

    assert gate["gate_id"] == "R8u156_external_package_acquisition_maturity_gate"
    assert gate["gate_status"] == (
        "external_package_acquisition_interfaces_ready_waiting_for_field_packages"
    )
    assert gate["source_packet_id"] == "R8u155_external_package_operator_action_packet"
    assert gate["package_count"] == 5
    assert gate["field_package_ready_rate"] == 0.0
    assert gate["operator_action_contract_coverage"] == 1.0
    assert gate["interface_preflight_coverage"] == 1.0
    assert gate["no_write_boundary_integrity"] == 1.0
    assert gate["acquisition_maturity_score"] == 0.85
    assert gate["model_chain_resume_ready"] is False
    assert gate["next_stage_decision"] == "collect_external_field_packages_before_downstream_gates"
    assert gate["next_operator_source_env_var"] == "GREY_BOX_CALIBRATION_PACKAGE_DIR"
    assert gate["can_generate_field_evidence"] is False
    assert gate["can_write_to_actuator"] is False
    assert gate["can_write_to_release_gate"] is False


def test_external_package_acquisition_maturity_gate_exposes_goal_termination_metrics() -> None:
    board = build_external_package_readiness_board(
        new_core_interface_candidate_gate=_candidate_gate(),
        package_artifacts=_artifacts(),
    )
    packet = board_module.build_external_package_operator_action_packet(readiness_board=board)

    gate = board_module.build_external_package_acquisition_maturity_gate(
        readiness_board=board,
        operator_action_packet=packet,
    )

    assert gate["termination_thresholds"] == {
        "input_contract_completeness": 0.95,
        "output_contract_completeness": 0.95,
        "handoff_state_variable_coverage": 0.9,
        "downstream_reconnection_rate": 0.8,
        "evidence_boundary_completeness": 1.0,
        "failure_boundary_completeness": 0.9,
        "no_write_boundary_completeness": 1.0,
    }
    assert gate["input_contract_completeness"] == 1.0
    assert gate["output_contract_completeness"] == 1.0
    assert gate["handoff_state_variable_coverage"] == 1.0
    assert gate["downstream_reconnection_rate"] == 0.0
    assert gate["evidence_boundary_completeness"] == 1.0
    assert gate["failure_boundary_completeness"] == 1.0
    assert gate["no_write_boundary_completeness"] == 1.0
    assert gate["contract_termination_status"] == (
        "external_package_contracts_complete_but_waiting_for_field_packages"
    )
    assert gate["module_stage_termination_pass"] is False
    assert gate["termination_blockers"] == [
        "downstream_reconnection_rate_below_0.80",
        "field_package_ready_rate_below_1.00",
    ]
    assert gate["termination_boundary_note"] == (
        "handoff_state_variable_coverage only scores operator/package lifecycle state "
        "fields; it is not field hidden-state validation."
    )


def test_external_package_acquisition_maturity_gate_prioritizes_preflight_repairs() -> None:
    gate_input = _candidate_gate()
    gate_input["candidate_rows"][1]["candidate_preflight_status"] = (
        "field_supported_kg_edge_package_blocked_at_schema"
    )
    board = build_external_package_readiness_board(
        new_core_interface_candidate_gate=gate_input,
        package_artifacts=_artifacts(),
    )
    packet = board_module.build_external_package_operator_action_packet(readiness_board=board)

    gate = board_module.build_external_package_acquisition_maturity_gate(
        readiness_board=board,
        operator_action_packet=packet,
    )

    assert gate["gate_status"] == "external_package_acquisition_blocked_by_preflight_repair"
    assert gate["preflight_repair_required"] is True
    assert gate["blocked_package_count"] == 1
    assert gate["next_operator_candidate_id"] == "NCI5_FIELD_SUPPORTED_KG_EDGE_PACKAGE"
    assert gate["next_stage_decision"] == "repair_external_package_preflight_before_collection"
    assert gate["acquisition_maturity_score"] < 0.85


def test_external_package_acquisition_maturity_gate_report_explains_no_field_claim() -> None:
    board = build_external_package_readiness_board(
        new_core_interface_candidate_gate=_candidate_gate(),
        package_artifacts=_artifacts(),
    )
    packet = board_module.build_external_package_operator_action_packet(readiness_board=board)
    gate = board_module.build_external_package_acquisition_maturity_gate(
        readiness_board=board,
        operator_action_packet=packet,
    )

    report = board_module.external_package_acquisition_maturity_gate_report_md(gate)

    assert "External Package Acquisition Maturity Gate" in report
    assert "acquisition_maturity_score" in report
    assert "field_package_ready_rate: `0.0`" in report
    assert "cannot resume the model chain" in report


def _candidate_gate() -> dict[str, object]:
    rows = [
        _row(1, "NCI1_GREY_BOX_CALIBRATION_PACKAGE", "P4_minimal_grey_box_physics", "GREY_BOX_CALIBRATION_PACKAGE_DIR", "grey_box_calibration_package_waiting_for_GREY_BOX_CALIBRATION_PACKAGE_DIR"),
        _row(2, "NCI5_FIELD_SUPPORTED_KG_EDGE_PACKAGE", "P6_reasonable_knowledge_graph_upgrade", "FIELD_SUPPORTED_KG_EDGE_PACKAGE_DIR", "field_supported_kg_edge_package_waiting_for_FIELD_SUPPORTED_KG_EDGE_PACKAGE_DIR"),
        _row(3, "NCI3_FIELD_CONTROL_REPLAY_PACKAGE", "P3_agent49_replay_ready_offline_evaluation", "FIELD_CONTROL_REPLAY_PACKAGE_DIR", "field_control_replay_package_waiting_for_FIELD_CONTROL_REPLAY_PACKAGE_DIR"),
        _row(4, "NCI4_SPARSE_TOPOLOGY_INSTALLABILITY_PACKAGE", "P1_agent48_comparable_sparse_sensor_placement", "SPARSE_TOPOLOGY_INSTALLABILITY_PACKAGE_DIR", "sparse_topology_installability_package_waiting_for_SPARSE_TOPOLOGY_INSTALLABILITY_PACKAGE_DIR"),
        _row(5, "NCI2_FIELD_MISSINGNESS_REPLAY_PACKAGE", "P5_soft_sensor_node_modality_missingness", "FIELD_MISSINGNESS_REPLAY_PACKAGE_DIR", "field_missingness_replay_package_waiting_for_FIELD_MISSINGNESS_REPLAY_PACKAGE_DIR"),
    ]
    return {
        "gate_metadata": {
            "gate_id": "R8u147_new_core_interface_candidate_gate",
            "gate_status": "new_core_interface_candidate_gate_ready_with_ranked_contracts",
        },
        "candidate_summary": {"candidate_count": 5},
        "candidate_rows": rows,
    }


def _row(
    priority: int,
    candidate_id: str,
    task_id: str,
    env_var: str,
    status: str,
) -> dict[str, object]:
    return {
        "priority_order": priority,
        "candidate_id": candidate_id,
        "task_id": task_id,
        "title": task_id,
        "source_env_var": env_var,
        "system_layer": "test_layer",
        "core_ability": "verifiability",
        "candidate_preflight_status": status,
        "candidate_preflight_pass": False,
        "interface_candidate_status": "admissible_contract_candidate_waiting_for_interface_preflight",
        "can_route_to_downstream_interface": False,
        "downstream_interface_status": status,
        "validation_command": f"run_{candidate_id}",
        "next_interface_action": f"fill_{env_var}",
        "candidate_matched_batch_count": 0,
        "candidate_matched_edge_count": 0,
        "candidate_matched_node_count": 0,
        "candidate_matched_transition_count": 0,
        "candidate_matched_sample_count": 0,
        "minimum_row_count": 3,
        "input_contract": ["field_rows"],
        "output_contract": ["preflight_metrics"],
        "failure_boundary": "no field claim without downstream validation",
    }


def _artifacts() -> dict[str, dict[str, str]]:
    return {
        "NCI1_GREY_BOX_CALIBRATION_PACKAGE": {
            "template_dir": "outputs/grey_box_calibration_package/grey_box_calibration_package_template"
        },
        "NCI5_FIELD_SUPPORTED_KG_EDGE_PACKAGE": {
            "template_dir": "outputs/field_supported_kg_edge_package/field_supported_kg_edge_package_template"
        },
        "NCI3_FIELD_CONTROL_REPLAY_PACKAGE": {
            "template_dir": "outputs/field_control_replay_package/field_control_replay_package_template"
        },
        "NCI4_SPARSE_TOPOLOGY_INSTALLABILITY_PACKAGE": {
            "template_dir": "outputs/sparse_topology_installability_package/sparse_topology_installability_package_template"
        },
        "NCI2_FIELD_MISSINGNESS_REPLAY_PACKAGE": {
            "template_dir": "outputs/field_missingness_replay_package/field_missingness_replay_package_template"
        },
    }

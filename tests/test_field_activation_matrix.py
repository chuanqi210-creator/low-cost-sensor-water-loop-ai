import csv
import json
from pathlib import Path

from water_ai.field_activation_matrix import (
    audit_field_activation_response_coherence,
    build_field_activation_package_assembly_plan,
    build_field_activation_package_staging_manifest,
    build_field_activation_external_readiness_gate,
    build_field_activation_matrix,
    build_field_activation_response_completion_ledger,
    build_field_activation_response_focus_handoff,
    build_field_activation_response_repair_work_order,
    build_field_activation_response_submission_packet,
    build_field_activation_response_template,
    build_field_activation_schema_contract,
    preflight_field_activation_response,
    preflight_field_activation_response_source,
    preflight_field_activation_materialized_package,
    preflight_field_activation_schema_contract,
    preview_field_activation_downstream_path_endpoint_preflight,
    preview_field_activation_downstream_r7_preflight,
)


def test_field_activation_matrix_maps_all_hidden_states_to_external_evidence() -> None:
    matrix = build_field_activation_matrix(_core_gate())
    readiness = matrix["readiness"]

    assert matrix["interface_type"] == "new_testable_core_interface"
    assert readiness["interface_status"] == "field_activation_matrix_ready_for_state_level_external_collection"
    assert readiness["hidden_state_row_count"] == 6
    assert readiness["hidden_state_row_coverage"] == 1.0
    assert readiness["activation_ready_state_count"] == 0
    assert readiness["can_resume_model_chain"] is False
    assert readiness["can_write_to_actuator"] is False
    assert readiness["can_write_to_release_gate"] is False

    for row in matrix["state_activation_rows"]:
        assert row["required_channels"]
        assert row["required_field_evidence"]
        assert row["evidence_boundary"]
        assert "cannot write actuator policy" in row["no_write_boundary"]
        assert row["activation_status"] == "state_blocked_waiting_for_external_evidence"


def test_field_activation_matrix_keeps_catalyst_activity_as_state_level_blocker() -> None:
    matrix = build_field_activation_matrix(_core_gate())
    rows = {row["hidden_state"]: row for row in matrix["state_activation_rows"]}
    catalyst = rows["catalyst_activity"]

    assert catalyst["sparse_estimation_ready"] is False
    assert catalyst["required_channels"] == [
        "R7_REAL_FIELD_PACKAGE",
        "R8U66_PATH_ENDPOINT_LABEL_PACKAGE",
    ]
    assert "node_modality_sensor_timeseries.N3_catalyst_bed:pressure_drop_kPa" in catalyst[
        "required_field_evidence"
    ]
    assert "offline_lab_results.catalyst_activity" in catalyst["required_field_evidence"]
    assert "campaign_operation_log.regeneration_event" in catalyst["required_field_evidence"]
    assert "Agent51 catalyst proxy field holdout" in catalyst["resumes_to"]
    assert catalyst["next_operator_focus"]["action_id"] == (
        "collect_field_activation_evidence_for_catalyst_activity"
    )


def test_field_activation_matrix_allows_state_route_without_direct_writeback() -> None:
    core_gate = _core_gate()
    first_row = core_gate["hidden_state_coverage_ledger"]["state_rows"][0]
    first_row["field_validated"] = True
    core_gate["external_resume_conditions"]["router_route_summary"][0]["route_ready"] = True
    core_gate["external_resume_conditions"]["router_route_summary"][0]["can_resume_model_chain"] = True
    core_gate["external_resume_conditions"]["router_model_chain_ready_channel_ids"] = [
        "R7_REAL_FIELD_PACKAGE"
    ]

    matrix = build_field_activation_matrix(core_gate)
    pollutant = matrix["state_activation_rows"][0]

    assert pollutant["activation_status"] == "state_field_validated_model_chain_resume_ready"
    assert matrix["readiness"]["activation_ready_state_count"] == 1
    assert matrix["readiness"]["can_resume_model_chain"] is True
    assert matrix["readiness"]["can_write_to_actuator"] is False
    assert matrix["readiness"]["can_write_to_release_gate"] is False
    assert "actuator_policy" in matrix["writeback_policy"]["blocked_writeback"]
    assert "release_gate" in matrix["writeback_policy"]["blocked_writeback"]


def test_field_activation_response_template_is_blocked_until_real_field_rows_are_filled() -> None:
    matrix = build_field_activation_matrix(_core_gate())
    template = build_field_activation_response_template(matrix)
    preflight = preflight_field_activation_response(template, matrix)
    assembly = build_field_activation_package_assembly_plan(
        template,
        matrix,
        preflight,
        _external_activation_contract(),
    )

    assert template["package_type"] == "field_activation_evidence_response"
    assert template["required_response_row_count"] == len(template["evidence_rows"])
    assert preflight["preflight_status"] == (
        "field_activation_response_blocked_before_external_package_preflight"
    )
    assert preflight["expected_response_row_count"] == len(template["evidence_rows"])
    assert preflight["provided_response_row_count"] == len(template["evidence_rows"])
    assert preflight["template_marker_row_count"] == len(template["evidence_rows"])
    assert preflight["non_field_row_count"] == len(template["evidence_rows"])
    assert preflight["missing_value_payload_row_count"] == 0
    assert preflight["template_value_payload_row_count"] == len(template["evidence_rows"])
    assert preflight["can_route_to_external_activation_router"] is False
    assert preflight["can_resume_model_chain"] is False
    assert preflight["can_write_to_actuator"] is False
    assert preflight["can_write_to_release_gate"] is False
    assert assembly["assembly_status"] == (
        "field_activation_package_assembly_plan_blocked_by_response_preflight"
    )
    assert assembly["channel_plan_count"] == 1
    assert assembly["candidate_channel_plan_count"] == 2
    candidate_channels = {plan["channel_id"] for plan in assembly["candidate_channel_plans"]}
    assert "R7_REAL_FIELD_PACKAGE" in candidate_channels
    assert "R8U66_PATH_ENDPOINT_LABEL_PACKAGE" in candidate_channels
    assert assembly["can_stage_external_package_candidates"] is False
    assert assembly["can_resume_model_chain"] is False


def test_field_activation_response_completion_ledger_marks_default_template_as_zero_complete() -> None:
    matrix = build_field_activation_matrix(_core_gate())
    template = build_field_activation_response_template(matrix)
    source_preflight = preflight_field_activation_response_source(
        source_path="",
        load_status="field_activation_response_source_not_supplied",
        response=template,
        default_response_template=template,
        matrix=matrix,
    )
    response_preflight = preflight_field_activation_response(template, matrix)

    ledger = build_field_activation_response_completion_ledger(
        template,
        matrix,
        source_preflight,
        response_preflight,
    )

    assert ledger["ledger_status"] == (
        "field_activation_response_completion_waiting_for_external_response"
    )
    assert ledger["expected_response_row_count"] == len(template["evidence_rows"])
    assert ledger["completed_response_row_count"] == 0
    assert ledger["incomplete_response_row_count"] == len(template["evidence_rows"])
    assert ledger["completion_ratio"] == 0.0
    assert ledger["next_hidden_state_focus"] == "catalyst_activity"
    assert ledger["issue_scope_counts"]["template_marker"] == len(template["evidence_rows"])
    assert ledger["can_route_to_package_assembly"] is False
    assert ledger["can_write_to_actuator"] is False
    assert ledger["can_write_to_release_gate"] is False


def test_field_activation_response_focus_handoff_routes_default_template_to_catalyst_kit() -> None:
    matrix = build_field_activation_matrix(_core_gate())
    template = build_field_activation_response_template(matrix)
    source_preflight = preflight_field_activation_response_source(
        source_path="",
        load_status="field_activation_response_source_not_supplied",
        response=template,
        default_response_template=template,
        matrix=matrix,
    )
    response_preflight = preflight_field_activation_response(template, matrix)
    ledger = build_field_activation_response_completion_ledger(
        template,
        matrix,
        source_preflight,
        response_preflight,
    )

    handoff = build_field_activation_response_focus_handoff(
        ledger,
        _focused_catalyst_kit_metrics(),
        _focused_catalyst_merge_preflight(),
    )

    assert handoff["handoff_status"] == "field_activation_response_focus_handoff_ready_for_catalyst_activity"
    assert handoff["target_hidden_state"] == "catalyst_activity"
    assert handoff["focused_response_row_count"] == 6
    assert handoff["full_response_expected_row_count"] == len(template["evidence_rows"])
    assert handoff["row_scan_reduction_count"] == len(template["evidence_rows"]) - 6
    assert handoff["row_scan_reduction_ratio"] > 0.8
    assert handoff["focused_merge_source_env_var"] == "FOCUSED_CATALYST_RESPONSE_PATH"
    assert handoff["focused_repair_work_order_status"] == (
        "focused_catalyst_response_repair_work_order_waiting_for_external_response"
    )
    assert handoff["focused_repair_item_count"] == 1
    assert "FOCUSED_CATALYST_RESPONSE_PATH" in handoff["next_operator_action"]
    assert handoff["can_submit_to_external_activation_router"] is False
    assert handoff["can_write_to_actuator"] is False
    assert handoff["can_write_to_release_gate"] is False


def test_field_activation_response_completion_ledger_tracks_partial_catalyst_completion() -> None:
    matrix = build_field_activation_matrix(_core_gate())
    template = build_field_activation_response_template(matrix)
    response = build_field_activation_response_template(matrix)
    for index, row in enumerate(response["evidence_rows"], start=1):
        if row["hidden_state"] != "catalyst_activity":
            continue
        row["data_origin"] = "field"
        row["batch_id"] = "B_CATALYST"
        row["timestamp"] = "2026-06-21T08:00:00+08:00"
        row["node_id"] = "N3_catalyst_bed"
        row["sensor_id"] = "S_catalyst_proxy"
        row["evidence_value_reference"] = f"{row['table_name']}.{row['field_name']}"
        row["evidence_value"] = f"catalyst_field_value_{index}"
        row["offline_method_id"] = "LCMS_METHOD_01"
        row["detection_limit"] = "method_recorded"
        row["chain_of_custody_id"] = "COC_001"
        row["operator_id"] = "operator_001"
        row["no_write_boundary_confirmed"] = "true"
        row["review_notes"] = "real catalyst field package row prepared for downstream preflight"
    source_preflight = preflight_field_activation_response_source(
        source_path="/tmp/field_activation_response.json",
        load_status="field_activation_response_source_loaded",
        response=response,
        default_response_template=template,
        matrix=matrix,
    )
    response_preflight = preflight_field_activation_response(response, matrix)

    ledger = build_field_activation_response_completion_ledger(
        response,
        matrix,
        source_preflight,
        response_preflight,
    )
    state_rows = {row["hidden_state"]: row for row in ledger["hidden_state_completion_rows"]}

    assert ledger["ledger_status"] == "field_activation_response_completion_partially_completed"
    assert ledger["completed_response_row_count"] == state_rows["catalyst_activity"]["expected_row_count"]
    assert state_rows["catalyst_activity"]["completion_status"] == "group_complete"
    assert state_rows["pollutant_residual"]["completion_status"] == "group_not_started"
    assert ledger["next_hidden_state_focus"] == "pollutant_residual"
    assert ledger["can_route_to_package_assembly"] is False
    assert ledger["can_resume_model_chain"] is False


def test_field_activation_response_focus_handoff_uses_repair_action_when_focused_source_is_blocked() -> None:
    matrix = build_field_activation_matrix(_core_gate())
    template = build_field_activation_response_template(matrix)
    source_preflight = preflight_field_activation_response_source(
        source_path="",
        load_status="field_activation_response_source_not_supplied",
        response=template,
        default_response_template=template,
        matrix=matrix,
    )
    response_preflight = preflight_field_activation_response(template, matrix)
    ledger = build_field_activation_response_completion_ledger(
        template,
        matrix,
        source_preflight,
        response_preflight,
    )

    handoff = build_field_activation_response_focus_handoff(
        ledger,
        _focused_catalyst_kit_metrics(),
        _focused_catalyst_merge_preflight_source_blocked(),
    )

    assert handoff["handoff_status"] == "field_activation_response_focus_handoff_ready_for_catalyst_activity"
    assert handoff["focused_repair_work_order_status"] == (
        "focused_catalyst_response_repair_work_order_blocked_at_source_preflight"
    )
    assert handoff["focused_repair_item_count"] == 1
    assert handoff["next_operator_action"] == "repair_FOCUSED_CATALYST_RESPONSE_PATH_file_path"


def test_field_activation_response_focus_handoff_waits_for_full_rows_after_catalyst_complete() -> None:
    matrix = build_field_activation_matrix(_core_gate())
    template = build_field_activation_response_template(matrix)
    response = build_field_activation_response_template(matrix)
    for index, row in enumerate(response["evidence_rows"], start=1):
        if row["hidden_state"] != "catalyst_activity":
            continue
        row["data_origin"] = "field"
        row["batch_id"] = "B_CATALYST"
        row["timestamp"] = "2026-06-21T08:00:00+08:00"
        row["node_id"] = "N3_catalyst_bed"
        row["sensor_id"] = "S_catalyst_proxy"
        row["evidence_value_reference"] = f"{row['table_name']}.{row['field_name']}"
        row["evidence_value"] = f"catalyst_field_value_{index}"
        row["offline_method_id"] = "LCMS_METHOD_01"
        row["detection_limit"] = "method_recorded"
        row["chain_of_custody_id"] = "COC_001"
        row["operator_id"] = "operator_001"
        row["no_write_boundary_confirmed"] = "true"
        row["review_notes"] = "real catalyst field package row prepared for downstream preflight"
    source_preflight = preflight_field_activation_response_source(
        source_path="/tmp/field_activation_response.json",
        load_status="field_activation_response_source_loaded",
        response=response,
        default_response_template=template,
        matrix=matrix,
    )
    response_preflight = preflight_field_activation_response(response, matrix)
    ledger = build_field_activation_response_completion_ledger(
        response,
        matrix,
        source_preflight,
        response_preflight,
    )

    handoff = build_field_activation_response_focus_handoff(
        ledger,
        _focused_catalyst_kit_metrics(),
        _focused_catalyst_merge_preflight(),
    )

    assert ledger["next_hidden_state_focus"] == "pollutant_residual"
    assert handoff["handoff_status"] == "field_activation_response_focus_handoff_waiting_for_full_response_focus"
    assert handoff["focused_hidden_state_supported"] is False
    assert handoff["next_operator_action"] == "continue_full_field_activation_response_rows_for_pollutant_residual"
    assert handoff["row_scan_reduction_ratio"] == 0.0


def test_field_activation_response_completion_ledger_ready_after_filled_response() -> None:
    matrix = build_field_activation_matrix(_core_gate())
    template = build_field_activation_response_template(matrix)
    response = build_field_activation_response_template(matrix)
    _fill_field_activation_response(response)
    source_preflight = preflight_field_activation_response_source(
        source_path="/tmp/field_activation_response.json",
        load_status="field_activation_response_source_loaded",
        response=response,
        default_response_template=template,
        matrix=matrix,
    )
    response_preflight = preflight_field_activation_response(response, matrix)

    ledger = build_field_activation_response_completion_ledger(
        response,
        matrix,
        source_preflight,
        response_preflight,
    )

    assert ledger["ledger_status"] == (
        "field_activation_response_completion_ready_for_package_assembly"
    )
    assert ledger["completed_response_row_count"] == ledger["expected_response_row_count"]
    assert ledger["incomplete_response_row_count"] == 0
    assert ledger["completion_ratio"] == 1.0
    assert ledger["issue_scope_counts"] == {}
    assert ledger["next_hidden_state_focus"] == ""
    assert ledger["can_route_to_package_assembly"] is True
    assert ledger["can_write_to_actuator"] is False
    assert ledger["can_write_to_release_gate"] is False


def test_field_activation_response_focus_handoff_exits_after_filled_response() -> None:
    matrix = build_field_activation_matrix(_core_gate())
    template = build_field_activation_response_template(matrix)
    response = build_field_activation_response_template(matrix)
    _fill_field_activation_response(response)
    source_preflight = preflight_field_activation_response_source(
        source_path="/tmp/field_activation_response.json",
        load_status="field_activation_response_source_loaded",
        response=response,
        default_response_template=template,
        matrix=matrix,
    )
    response_preflight = preflight_field_activation_response(response, matrix)
    ledger = build_field_activation_response_completion_ledger(
        response,
        matrix,
        source_preflight,
        response_preflight,
    )

    handoff = build_field_activation_response_focus_handoff(
        ledger,
        _focused_catalyst_kit_metrics(),
        _focused_catalyst_merge_preflight(),
    )

    assert handoff["handoff_status"] == "field_activation_response_focus_handoff_not_needed_response_complete"
    assert handoff["target_hidden_state"] == ""
    assert handoff["next_operator_action"] == (
        "continue_to_no_write_package_assembly_staging_and_materialized_preflight"
    )
    assert handoff["can_resume_model_chain"] is False
    assert handoff["can_write_to_actuator"] is False
    assert handoff["can_write_to_release_gate"] is False


def test_field_activation_package_staging_manifest_blocks_template_rows() -> None:
    matrix = build_field_activation_matrix(_core_gate())
    template = build_field_activation_response_template(matrix)
    source_preflight = preflight_field_activation_response_source(
        source_path="",
        load_status="field_activation_response_source_not_supplied",
        response=template,
        default_response_template=template,
        matrix=matrix,
    )
    preflight = preflight_field_activation_response(template, matrix)
    assembly = build_field_activation_package_assembly_plan(
        template,
        matrix,
        preflight,
        _external_activation_contract(),
    )

    staging = build_field_activation_package_staging_manifest(
        template,
        assembly,
        preflight,
        source_preflight,
    )

    assert staging["staging_status"] == (
        "field_activation_package_staging_manifest_blocked_by_response_preflight"
    )
    assert staging["selected_channel_manifest_count"] == 1
    assert staging["candidate_channel_requirement_count"] == 2
    assert staging["selected_channel_ids"] == ["R7_REAL_FIELD_PACKAGE"]
    assert staging["candidate_channel_ids"] == [
        "R7_REAL_FIELD_PACKAGE",
        "R8U66_PATH_ENDPOINT_LABEL_PACKAGE",
    ]
    assert staging["can_materialize_no_write_package_candidates"] is False
    assert staging["can_route_to_external_activation_router"] is False
    assert staging["can_resume_model_chain"] is False
    assert staging["can_write_to_actuator"] is False
    assert staging["can_write_to_release_gate"] is False
    assert staging["next_operator_action"] == (
        "complete_response_preflight_and_package_assembly_before_staging"
    )


def test_field_activation_schema_preflight_accepts_template_structure_without_field_claims() -> None:
    matrix = build_field_activation_matrix(_core_gate())
    template = build_field_activation_response_template(matrix)
    response_preflight = preflight_field_activation_response(template, matrix)
    assembly = build_field_activation_package_assembly_plan(
        template,
        matrix,
        response_preflight,
        _external_activation_contract(),
    )
    schema_contract = build_field_activation_schema_contract(matrix, template, assembly)
    schema_preflight = preflight_field_activation_schema_contract(
        schema_contract,
        template,
        assembly,
    )

    assert schema_contract["schema_contract_status"] == "field_activation_schema_contract_ready"
    assert schema_preflight["schema_preflight_status"] == "field_activation_schema_preflight_passed"
    assert schema_preflight["response_top_level_missing_count"] == 0
    assert schema_preflight["evidence_row_missing_field_count"] == 0
    assert schema_preflight["assembly_top_level_missing_count"] == 0
    assert schema_preflight["assembly_channel_missing_field_count"] == 0
    assert schema_preflight["assembly_table_missing_field_count"] == 0
    assert schema_preflight["no_write_violation_count"] == 0
    assert schema_preflight["can_validate_field_activation_response_structure"] is True
    assert schema_preflight["can_resume_model_chain"] is False
    assert schema_preflight["can_write_to_actuator"] is False
    assert schema_preflight["can_write_to_release_gate"] is False
    assert response_preflight["can_route_to_external_activation_router"] is False


def test_field_activation_schema_preflight_blocks_missing_required_response_field() -> None:
    matrix = build_field_activation_matrix(_core_gate())
    template = build_field_activation_response_template(matrix)
    response_preflight = preflight_field_activation_response(template, matrix)
    assembly = build_field_activation_package_assembly_plan(
        template,
        matrix,
        response_preflight,
        _external_activation_contract(),
    )
    schema_contract = build_field_activation_schema_contract(matrix, template, assembly)
    template["evidence_rows"][0].pop("batch_id")

    schema_preflight = preflight_field_activation_schema_contract(
        schema_contract,
        template,
        assembly,
    )

    assert schema_preflight["schema_preflight_status"] == "field_activation_schema_preflight_blocked"
    assert schema_preflight["evidence_row_missing_field_count"] == 1
    assert schema_preflight["can_validate_field_activation_response_structure"] is False
    assert schema_preflight["can_resume_model_chain"] is False
    assert schema_preflight["can_write_to_actuator"] is False
    assert schema_preflight["can_write_to_release_gate"] is False


def test_field_activation_response_source_preflight_defaults_to_template_without_field_claims() -> None:
    matrix = build_field_activation_matrix(_core_gate())
    template = build_field_activation_response_template(matrix)
    source_preflight = preflight_field_activation_response_source(
        source_path="",
        load_status="field_activation_response_source_not_supplied",
        response=template,
        default_response_template=template,
        matrix=matrix,
    )

    assert source_preflight["source_preflight_status"] == (
        "field_activation_response_source_using_default_template"
    )
    assert source_preflight["external_response_supplied"] is False
    assert source_preflight["using_default_template"] is True
    assert source_preflight["can_run_response_preflight"] is True
    assert source_preflight["can_route_to_external_activation_router"] is False
    assert source_preflight["can_resume_model_chain"] is False
    assert source_preflight["can_write_to_actuator"] is False
    assert source_preflight["can_write_to_release_gate"] is False


def test_field_activation_response_source_preflight_accepts_external_json_shape() -> None:
    matrix = build_field_activation_matrix(_core_gate())
    template = build_field_activation_response_template(matrix)
    response = build_field_activation_response_template(matrix)
    for index, row in enumerate(response["evidence_rows"], start=1):
        row["data_origin"] = "field"
        row["batch_id"] = f"B{index:03d}"
        row["timestamp"] = "2026-06-21T08:00:00+08:00"
        row["node_id"] = "N3_catalyst_bed" if row["hidden_state"] == "catalyst_activity" else "N_out"
        row["sensor_id"] = "S_uv254_or_lab"
        row["evidence_value_reference"] = f"{row['table_name']}.{row['field_name']}"
        row["evidence_value"] = f"field_value_{index}"
        row["offline_method_id"] = "LCMS_METHOD_01"
        row["detection_limit"] = "method_recorded"
        row["chain_of_custody_id"] = "COC_001"
        row["operator_id"] = "operator_001"
        row["no_write_boundary_confirmed"] = "true"
        row["review_notes"] = "real field package row prepared for downstream preflight"

    source_preflight = preflight_field_activation_response_source(
        source_path="/tmp/field_activation_response.json",
        load_status="field_activation_response_source_loaded",
        response=response,
        default_response_template=template,
        matrix=matrix,
    )
    response_preflight = preflight_field_activation_response(response, matrix)

    assert source_preflight["source_preflight_status"] == (
        "field_activation_response_source_loaded_external_json"
    )
    assert source_preflight["external_response_supplied"] is True
    assert source_preflight["using_default_template"] is False
    assert source_preflight["source_interface_match"] is True
    assert source_preflight["selected_response_row_count"] == len(template["evidence_rows"])
    assert source_preflight["can_run_response_preflight"] is True
    assert source_preflight["can_resume_model_chain"] is False
    assert response_preflight["preflight_status"] == (
        "field_activation_response_ready_for_external_package_preflight"
    )


def test_field_activation_response_preflight_blocks_reference_only_rows_without_value_payload() -> None:
    matrix = build_field_activation_matrix(_core_gate())
    response = build_field_activation_response_template(matrix)
    _fill_field_activation_response(response)
    for row in response["evidence_rows"]:
        row.pop("evidence_value")

    preflight = preflight_field_activation_response(response, matrix)

    assert preflight["preflight_status"] == (
        "field_activation_response_blocked_before_external_package_preflight"
    )
    assert preflight["missing_value_payload_row_count"] == len(response["evidence_rows"])
    assert preflight["template_value_payload_row_count"] == 0
    assert preflight["can_route_to_external_activation_router"] is False
    assert set(preflight["blocked_row_ids"]).issubset(
        {row["response_row_id"] for row in response["evidence_rows"]}
    )
    assert len(preflight["blocked_row_ids"]) == 30


def test_field_activation_response_repair_work_order_prioritizes_missing_external_response() -> None:
    matrix = build_field_activation_matrix(_core_gate())
    template = build_field_activation_response_template(matrix)
    source_preflight = preflight_field_activation_response_source(
        source_path="",
        load_status="field_activation_response_source_not_supplied",
        response=template,
        default_response_template=template,
        matrix=matrix,
    )
    response_preflight = preflight_field_activation_response(template, matrix)
    assembly = build_field_activation_package_assembly_plan(
        template,
        matrix,
        response_preflight,
        _external_activation_contract(),
    )
    schema_contract = build_field_activation_schema_contract(matrix, template, assembly)
    schema_preflight = preflight_field_activation_schema_contract(
        schema_contract,
        template,
        assembly,
    )

    work_order = build_field_activation_response_repair_work_order(
        source_preflight,
        response_preflight,
        schema_preflight,
        assembly,
    )

    assert work_order["work_order_status"] == (
        "field_activation_response_repair_work_order_waiting_for_external_response"
    )
    assert work_order["repair_item_count"] >= 5
    assert work_order["highest_priority_repair_id"] == "R8U102_SUBMIT_FIELD_ACTIVATION_RESPONSE"
    assert work_order["can_route_to_response_preflight"] is True
    assert work_order["can_route_to_package_assembly"] is False
    assert work_order["can_stage_external_package_candidates"] is False
    assert work_order["can_resume_model_chain"] is False
    assert work_order["can_write_to_actuator"] is False
    assert work_order["can_write_to_release_gate"] is False
    repair_ids = {item["repair_id"] for item in work_order["repair_items"]}
    assert "R8U102_REPLACE_TEMPLATE_MARKERS" in repair_ids
    assert "R8U102_SET_DATA_ORIGIN_FIELD" in repair_ids
    assert "R8U102_REPLACE_VALUE_PAYLOAD_TEMPLATE" in repair_ids
    assert "R8U102_COMPLETE_RESPONSE_PREFLIGHT_BEFORE_ASSEMBLY" in repair_ids


def test_field_activation_response_preflight_accepts_filled_field_rows_without_writeback() -> None:
    matrix = build_field_activation_matrix(_core_gate())
    response = build_field_activation_response_template(matrix)
    for index, row in enumerate(response["evidence_rows"], start=1):
        row["data_origin"] = "field"
        row["batch_id"] = f"B{index:03d}"
        row["timestamp"] = "2026-06-21T08:00:00+08:00"
        row["node_id"] = "N3_catalyst_bed" if row["hidden_state"] == "catalyst_activity" else "N_out"
        row["sensor_id"] = "S_uv254_or_lab"
        row["evidence_value_reference"] = f"{row['table_name']}.{row['field_name']}"
        row["evidence_value"] = f"field_value_{index}"
        row["offline_method_id"] = "LCMS_METHOD_01"
        row["detection_limit"] = "method_recorded"
        row["chain_of_custody_id"] = "COC_001"
        row["operator_id"] = "operator_001"
        row["no_write_boundary_confirmed"] = "true"
        row["review_notes"] = "real field package row prepared for downstream preflight"

    preflight = preflight_field_activation_response(response, matrix)
    assembly = build_field_activation_package_assembly_plan(
        response,
        matrix,
        preflight,
        _external_activation_contract(),
    )

    assert preflight["preflight_status"] == (
        "field_activation_response_ready_for_external_package_preflight"
    )
    assert preflight["missing_response_row_count"] == 0
    assert preflight["template_marker_row_count"] == 0
    assert preflight["non_field_row_count"] == 0
    assert preflight["missing_value_payload_row_count"] == 0
    assert preflight["template_value_payload_row_count"] == 0
    assert preflight["no_write_unconfirmed_row_count"] == 0
    assert preflight["can_route_to_external_activation_router"] is True
    assert preflight["can_resume_model_chain"] is False
    assert preflight["can_write_to_actuator"] is False
    assert preflight["can_write_to_release_gate"] is False
    assert assembly["assembly_status"] == (
        "field_activation_package_assembly_plan_ready_for_no_write_package_staging"
    )
    assert assembly["can_stage_external_package_candidates"] is True
    assert assembly["can_route_to_external_activation_router"] is True
    assert assembly["candidate_channel_plan_count"] == 2
    assert assembly["can_resume_model_chain"] is False
    assert assembly["can_write_to_actuator"] is False
    assert assembly["can_write_to_release_gate"] is False
    channel = assembly["channel_plans"][0]
    assert channel["channel_id"] == "R7_REAL_FIELD_PACKAGE"
    table_names = {table["table_name"] for table in channel["table_assemblies"]}
    assert "offline_lab_results" in table_names
    assert "campaign_operation_log" in table_names
    assert "node_modality_sensor_timeseries" in table_names


def test_field_activation_response_coherence_audit_waits_for_response_preflight() -> None:
    matrix = build_field_activation_matrix(_core_gate())
    template = build_field_activation_response_template(matrix)
    response_preflight = preflight_field_activation_response(template, matrix)

    audit = audit_field_activation_response_coherence(template, matrix, response_preflight)

    assert audit["audit_status"] == (
        "field_activation_response_coherence_audit_waiting_for_response_preflight"
    )
    assert audit["response_ready_for_audit"] is False
    assert audit["audit_execution_status"] == (
        "coherence_checks_deferred_until_response_preflight_ready"
    )
    assert audit["hard_blocker_count"] == 0
    assert audit["warning_count"] == 0
    assert audit["highest_priority_blocker"] == ""
    assert audit["blockers"] == []
    assert audit["warnings"] == []
    assert audit["can_route_to_package_assembly"] is False
    assert audit["can_resume_model_chain"] is False
    assert audit["can_write_to_actuator"] is False
    assert audit["can_write_to_release_gate"] is False


def test_field_activation_response_coherence_audit_blocks_fragmented_hidden_state_batches() -> None:
    matrix = build_field_activation_matrix(_core_gate())
    response = build_field_activation_response_template(matrix)
    _fill_field_activation_response(response)
    for index, row in enumerate(response["evidence_rows"], start=1):
        if row["hidden_state"] == "catalyst_activity":
            row["batch_id"] = f"B_FRAGMENTED_{index:03d}"
    response_preflight = preflight_field_activation_response(response, matrix)

    audit = audit_field_activation_response_coherence(response, matrix, response_preflight)
    assembly = build_field_activation_package_assembly_plan(
        response,
        matrix,
        response_preflight,
        _external_activation_contract(),
        audit,
    )

    assert response_preflight["can_route_to_external_activation_router"] is True
    assert audit["audit_status"] == (
        "field_activation_response_coherence_audit_blocked_before_package_assembly"
    )
    assert audit["highest_priority_blocker"] == "R8U117_HIDDEN_STATE_BATCH_ALIGNMENT_FRAGMENTED"
    assert audit["can_route_to_package_assembly"] is False
    assert assembly["assembly_status"] == (
        "field_activation_package_assembly_plan_blocked_by_response_coherence_audit"
    )
    assert assembly["can_stage_external_package_candidates"] is False


def test_field_activation_response_coherence_audit_allows_coherent_response_into_readiness_gate() -> None:
    chain = _ready_field_activation_chain()
    audit = audit_field_activation_response_coherence(
        chain["response"],
        chain["matrix"],
        chain["response_preflight"],
    )
    assembly = build_field_activation_package_assembly_plan(
        chain["response"],
        chain["matrix"],
        chain["response_preflight"],
        _external_activation_contract(),
        audit,
    )
    staging = build_field_activation_package_staging_manifest(
        chain["response"],
        assembly,
        chain["response_preflight"],
        chain["source_preflight"],
    )
    materialized_preflight = preflight_field_activation_materialized_package(
        staging,
        package_dir_path="",
    )
    work_order = build_field_activation_response_repair_work_order(
        chain["source_preflight"],
        chain["response_preflight"],
        chain["schema_preflight"],
        assembly,
        audit,
    )
    gate = build_field_activation_external_readiness_gate(
        chain["source_preflight"],
        work_order,
        chain["response_preflight"],
        assembly,
        staging,
        materialized_preflight,
        chain["schema_preflight"],
        audit,
    )

    assert audit["audit_status"] == "field_activation_response_coherence_audit_passed_for_package_assembly"
    assert audit["hard_blocker_count"] == 0
    assert audit["can_route_to_package_assembly"] is True
    assert assembly["assembly_status"] == (
        "field_activation_package_assembly_plan_ready_for_no_write_package_staging"
    )
    assert work_order["work_order_status"] == (
        "field_activation_response_repair_work_order_ready_no_repairs_required"
    )
    assert gate["first_blocked_step"] == "materialized_package_preflight"
    assert gate["highest_priority_blocker"] == "R8U105_SET_MATERIALIZED_PACKAGE_DIR"


def test_field_activation_package_staging_manifest_guides_operator_after_filled_response() -> None:
    matrix = build_field_activation_matrix(_core_gate())
    template = build_field_activation_response_template(matrix)
    response = build_field_activation_response_template(matrix)
    for index, row in enumerate(response["evidence_rows"], start=1):
        row["data_origin"] = "field"
        row["batch_id"] = f"B{index:03d}"
        row["timestamp"] = "2026-06-21T08:00:00+08:00"
        row["node_id"] = "N3_catalyst_bed" if row["hidden_state"] == "catalyst_activity" else "N_out"
        row["sensor_id"] = "S_uv254_or_lab"
        row["evidence_value_reference"] = f"{row['table_name']}.{row['field_name']}"
        row["evidence_value"] = f"field_value_{index}"
        row["offline_method_id"] = "LCMS_METHOD_01"
        row["detection_limit"] = "method_recorded"
        row["chain_of_custody_id"] = "COC_001"
        row["operator_id"] = "operator_001"
        row["no_write_boundary_confirmed"] = "true"
        row["review_notes"] = "real field package row prepared for downstream preflight"

    source_preflight = preflight_field_activation_response_source(
        source_path="/tmp/field_activation_response.json",
        load_status="field_activation_response_source_loaded",
        response=response,
        default_response_template=template,
        matrix=matrix,
    )
    preflight = preflight_field_activation_response(response, matrix)
    assembly = build_field_activation_package_assembly_plan(
        response,
        matrix,
        preflight,
        _external_activation_contract(),
    )
    staging = build_field_activation_package_staging_manifest(
        response,
        assembly,
        preflight,
        source_preflight,
    )

    assert staging["staging_status"] == (
        "field_activation_package_staging_manifest_ready_for_operator_package_materialization"
    )
    assert staging["external_response_supplied"] is True
    assert staging["selected_channel_manifest_count"] == 1
    assert staging["selected_table_manifest_count"] >= 3
    assert staging["selected_row_blueprint_count"] == len(response["evidence_rows"])
    assert staging["selected_value_payload_mapping_count"] == len(response["evidence_rows"])
    assert staging["candidate_channel_requirement_count"] == 2
    assert staging["selected_channel_ids"] == ["R7_REAL_FIELD_PACKAGE"]
    assert staging["package_pointers_to_set"] == ["REAL_FIELD_REPLAY_PACKAGE_DIR"]
    assert staging["can_materialize_no_write_package_candidates"] is True
    assert staging["can_route_to_external_activation_router"] is True
    assert staging["can_resume_model_chain"] is False
    assert staging["can_write_to_actuator"] is False
    assert staging["can_write_to_release_gate"] is False
    channel = staging["selected_channel_manifests"][0]
    assert channel["package_pointer"] == "REAL_FIELD_REPLAY_PACKAGE_DIR"
    assert channel["can_materialize_from_selected_response"] is True
    assert "run_external_activation_router.py" in channel["validation_command_preview"]
    tables = {table["table_name"]: table for table in channel["table_manifests"]}
    assert "offline_lab_results" in tables
    assert "campaign_operation_log" in tables
    assert "node_modality_sensor_timeseries" in tables
    assert "batch_id" in tables["offline_lab_results"]["required_columns"]
    assert "chain_of_custody_id" in tables["offline_lab_results"]["required_columns"]
    assert tables["offline_lab_results"]["row_blueprint_count"] > 0
    assert tables["offline_lab_results"]["value_payload_mapping_count"] > 0
    first_lab_blueprint = tables["offline_lab_results"]["row_blueprints"][0]
    assert first_lab_blueprint["output_row"]["data_origin"] == "field"
    assert first_lab_blueprint["value_payload_columns"]
    candidate_channels = {channel["channel_id"] for channel in staging["candidate_channel_requirements"]}
    assert "R8U66_PATH_ENDPOINT_LABEL_PACKAGE" in candidate_channels


def test_field_activation_materialized_package_preflight_blocks_until_staging_ready() -> None:
    matrix = build_field_activation_matrix(_core_gate())
    template = build_field_activation_response_template(matrix)
    source_preflight = preflight_field_activation_response_source(
        source_path="",
        load_status="field_activation_response_source_not_supplied",
        response=template,
        default_response_template=template,
        matrix=matrix,
    )
    response_preflight = preflight_field_activation_response(template, matrix)
    assembly = build_field_activation_package_assembly_plan(
        template,
        matrix,
        response_preflight,
        _external_activation_contract(),
    )
    staging = build_field_activation_package_staging_manifest(
        template,
        assembly,
        response_preflight,
        source_preflight,
    )

    materialized_preflight = preflight_field_activation_materialized_package(
        staging,
        package_dir_path="",
    )

    assert materialized_preflight["preflight_status"] == (
        "field_activation_materialized_package_preflight_blocked_by_staging_manifest"
    )
    assert materialized_preflight["highest_priority_blocker"] == "R8U105_STAGING_MANIFEST_NOT_READY"
    assert materialized_preflight["can_route_to_external_activation_router"] is False
    assert materialized_preflight["can_resume_model_chain"] is False
    assert materialized_preflight["can_write_to_actuator"] is False
    assert materialized_preflight["can_write_to_release_gate"] is False


def test_field_activation_materialized_package_preflight_waits_for_package_dir_after_ready_staging() -> None:
    staging = _ready_field_activation_staging()

    materialized_preflight = preflight_field_activation_materialized_package(
        staging,
        package_dir_path="",
    )

    assert materialized_preflight["preflight_status"] == (
        "field_activation_materialized_package_preflight_waiting_for_package_dir"
    )
    assert materialized_preflight["package_pointer"] == "REAL_FIELD_REPLAY_PACKAGE_DIR"
    assert materialized_preflight["highest_priority_blocker"] == "R8U105_SET_MATERIALIZED_PACKAGE_DIR"
    assert materialized_preflight["next_operator_action"] == "set_REAL_FIELD_REPLAY_PACKAGE_DIR"
    assert materialized_preflight["can_route_to_external_activation_router"] is False
    assert materialized_preflight["can_resume_model_chain"] is False
    assert materialized_preflight["can_write_to_actuator"] is False
    assert materialized_preflight["can_write_to_release_gate"] is False


def test_field_activation_materialized_package_preflight_accepts_materialized_package_dir(
    tmp_path: Path,
) -> None:
    staging = _ready_field_activation_staging()
    package_dir = tmp_path / "field_package"
    _write_materialized_package_from_staging(package_dir, staging)

    materialized_preflight = preflight_field_activation_materialized_package(
        staging,
        package_dir_path=str(package_dir),
    )

    assert materialized_preflight["preflight_status"] == (
        "field_activation_materialized_package_preflight_ready_for_external_activation_router"
    )
    assert materialized_preflight["expected_table_count"] == materialized_preflight["checked_table_count"]
    assert materialized_preflight["present_table_count"] == materialized_preflight["expected_table_count"]
    assert materialized_preflight["missing_table_count"] == 0
    assert materialized_preflight["header_gap_count"] == 0
    assert materialized_preflight["template_marker_row_count"] == 0
    assert materialized_preflight["non_field_row_count"] == 0
    assert materialized_preflight["blueprint_expected_row_count"] > 0
    assert materialized_preflight["blueprint_matched_row_count"] == materialized_preflight[
        "blueprint_expected_row_count"
    ]
    assert materialized_preflight["blueprint_missing_row_count"] == 0
    assert materialized_preflight["metadata_blocker_count"] == 0
    assert materialized_preflight["blocker_count"] == 0
    assert materialized_preflight["highest_priority_blocker"] == ""
    assert materialized_preflight["can_route_to_external_activation_router"] is True
    assert materialized_preflight["can_resume_model_chain"] is False
    assert materialized_preflight["can_write_to_actuator"] is False
    assert materialized_preflight["can_write_to_release_gate"] is False
    assert "REAL_FIELD_REPLAY_PACKAGE_DIR=" in materialized_preflight["router_validation_command"]
    assert "run_external_activation_router.py" in materialized_preflight["router_validation_command"]


def test_field_activation_materialized_package_preflight_blocks_blueprint_mismatch(
    tmp_path: Path,
) -> None:
    staging = _ready_field_activation_staging()
    package_dir = tmp_path / "field_package"
    _write_materialized_package_from_staging(package_dir, staging)
    channel = staging["selected_channel_manifests"][0]
    table = next(table for table in channel["table_manifests"] if table["row_blueprints"])
    path = package_dir / table["output_file"]
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = [dict(row) for row in reader]
        columns = list(reader.fieldnames or [])
    first_value_column = table["row_blueprints"][0]["value_payload_columns"][0]
    rows[0][first_value_column] = "wrong_field_value"
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)

    materialized_preflight = preflight_field_activation_materialized_package(
        staging,
        package_dir_path=str(package_dir),
    )

    assert materialized_preflight["preflight_status"] == (
        "field_activation_materialized_package_preflight_blocked_by_package_gaps"
    )
    assert materialized_preflight["blueprint_missing_row_count"] >= 1
    assert any(
        blocker["blocker_id"] == "R8U105_TABLE_BLUEPRINT_ROWS_MISSING"
        for blocker in materialized_preflight["blockers"]
    )
    assert materialized_preflight["can_route_to_external_activation_router"] is False


def test_field_activation_materialized_package_preflight_blocks_missing_metadata(
    tmp_path: Path,
) -> None:
    staging = _ready_field_activation_staging()
    package_dir = tmp_path / "field_package"
    _write_materialized_package_from_staging(package_dir, staging, include_metadata=False)

    materialized_preflight = preflight_field_activation_materialized_package(
        staging,
        package_dir_path=str(package_dir),
    )

    assert materialized_preflight["preflight_status"] == (
        "field_activation_materialized_package_preflight_blocked_by_package_gaps"
    )
    assert materialized_preflight["highest_priority_blocker"] == "R8U105_METADATA_JSON_MISSING"
    assert materialized_preflight["metadata_blocker_count"] == 1
    assert materialized_preflight["can_route_to_external_activation_router"] is False
    assert materialized_preflight["can_resume_model_chain"] is False


def test_field_activation_downstream_r7_preview_waits_for_materialized_preflight() -> None:
    chain = _ready_field_activation_chain()

    preview = preview_field_activation_downstream_r7_preflight(
        chain["staging"],
        chain["materialized_preflight"],
        package_dir_path="",
    )

    assert preview["preview_status"] == (
        "field_activation_downstream_r7_preview_blocked_by_materialized_package_preflight"
    )
    assert preview["preview_executed"] is False
    assert preview["preview_metric_evaluation_status"] == (
        "deferred_until_materialized_package_preflight_ready"
    )
    assert "r7_agent44_import_status" in preview["not_evaluated_metric_names"]
    assert preview["highest_priority_blocker"] == "R8U105_SET_MATERIALIZED_PACKAGE_DIR"
    assert preview["r7_preflight_status"] == "r7_preflight_not_run"
    assert preview["downstream_r7_can_pass_to_timestamped_replay"] is False
    assert preview["can_resume_model_chain"] is False
    assert preview["can_write_to_actuator"] is False
    assert preview["can_write_to_release_gate"] is False


def test_field_activation_downstream_r7_preview_exposes_agent44_gap_after_materialized_preflight(
    tmp_path: Path,
) -> None:
    staging = _ready_field_activation_staging()
    package_dir = tmp_path / "field_package"
    _write_materialized_package_from_staging(package_dir, staging)
    materialized_preflight = preflight_field_activation_materialized_package(
        staging,
        package_dir_path=str(package_dir),
    )

    preview = preview_field_activation_downstream_r7_preflight(
        staging,
        materialized_preflight,
        package_dir_path=str(package_dir),
    )

    assert materialized_preflight["can_route_to_external_activation_router"] is True
    assert preview["preview_status"] == "field_activation_downstream_r7_preview_blocked_by_r7_preflight"
    assert preview["preview_executed"] is True
    assert preview["preview_metric_evaluation_status"] == "r7_preflight_metrics_evaluated"
    assert preview["not_evaluated_metric_names"] == []
    assert preview["r7_preflight_status"] != "r7_preflight_not_run"
    assert preview["downstream_r7_can_pass_to_timestamped_replay"] is False
    assert preview["downstream_r7_would_resume_model_chain_in_router"] is False
    assert preview["highest_priority_blocker"].startswith("R8U121_R7_")
    assert preview["r7_preflight"]["can_pass_to_timestamped_replay"] is False
    assert preview["r7_next_actions"]
    assert preview["can_submit_to_external_activation_router"] is True
    assert preview["can_resume_model_chain"] is False
    assert preview["can_write_to_actuator"] is False
    assert preview["can_write_to_release_gate"] is False
    assert "read-only" in preview["no_write_boundary"]


def test_field_activation_downstream_path_endpoint_preview_waits_for_materialized_preflight() -> None:
    chain = _ready_field_activation_chain()

    preview = preview_field_activation_downstream_path_endpoint_preflight(
        chain["staging"],
        chain["materialized_preflight"],
        package_dir_path="",
    )

    assert preview["preview_status"] == (
        "field_activation_downstream_path_endpoint_preview_blocked_by_materialized_package_preflight"
    )
    assert preview["preview_executed"] is False
    assert preview["preview_metric_evaluation_status"] == (
        "deferred_until_materialized_package_preflight_ready"
    )
    assert "path_endpoint_required_matched_batch_deficit" in preview["not_evaluated_metric_names"]
    assert preview["path_endpoint_required_table_count"] == 6
    assert preview["path_endpoint_contract_minimum_matched_batch_count"] == 5
    assert preview["highest_priority_blocker"] == "R8U105_SET_MATERIALIZED_PACKAGE_DIR"
    assert preview["path_endpoint_preflight_status"] == "path_endpoint_preflight_not_run"
    assert preview["downstream_path_endpoint_can_route_to_field_layout_holdout"] is False
    assert preview["can_resume_model_chain"] is False
    assert preview["can_write_to_actuator"] is False
    assert preview["can_write_to_release_gate"] is False


def test_field_activation_downstream_path_endpoint_preview_exposes_layout_gap_after_materialized_preflight(
    tmp_path: Path,
) -> None:
    staging = _ready_field_activation_staging()
    package_dir = tmp_path / "field_package"
    _write_materialized_package_from_staging(package_dir, staging)
    materialized_preflight = preflight_field_activation_materialized_package(
        staging,
        package_dir_path=str(package_dir),
    )

    preview = preview_field_activation_downstream_path_endpoint_preflight(
        staging,
        materialized_preflight,
        package_dir_path=str(package_dir),
    )

    assert materialized_preflight["can_route_to_external_activation_router"] is True
    assert preview["preview_status"] == (
        "field_activation_downstream_path_endpoint_preview_blocked_by_path_endpoint_preflight"
    )
    assert preview["preview_executed"] is True
    assert preview["preview_metric_evaluation_status"] == "path_endpoint_preflight_metrics_evaluated"
    assert preview["not_evaluated_metric_names"] == []
    assert preview["path_endpoint_required_table_count"] == 6
    assert preview["path_endpoint_contract_minimum_matched_batch_count"] == 5
    assert preview["path_endpoint_preflight_status"] == "field_path_endpoint_label_package_blocked_by_preflight"
    assert preview["downstream_path_endpoint_can_route_to_field_layout_holdout"] is False
    assert preview["downstream_path_endpoint_would_resume_model_chain_in_router"] is False
    assert preview["highest_priority_blocker"].startswith("R8U122_PATH_ENDPOINT_")
    assert preview["path_endpoint_preflight"]["can_route_to_field_layout_holdout"] is False
    assert preview["can_submit_to_external_activation_router"] is True
    assert preview["can_resume_model_chain"] is False
    assert preview["can_write_to_actuator"] is False
    assert preview["can_write_to_release_gate"] is False
    assert "read-only" in preview["no_write_boundary"]


def test_field_activation_external_readiness_gate_sequences_response_before_package_dir() -> None:
    chain = _default_field_activation_chain()

    gate = build_field_activation_external_readiness_gate(
        chain["source_preflight"],
        chain["repair_work_order"],
        chain["response_preflight"],
        chain["assembly"],
        chain["staging"],
        chain["materialized_preflight"],
        chain["schema_preflight"],
    )

    assert gate["gate_status"] == "field_activation_external_readiness_waiting_for_external_response"
    assert gate["first_blocked_step"] == "response_source"
    assert gate["highest_priority_blocker"] == "R8U106_SUBMIT_FIELD_ACTIVATION_RESPONSE"
    assert gate["next_operator_action"] == "set_FIELD_ACTIVATION_RESPONSE_PATH_to_filled_external_response_json"
    assert gate["can_submit_to_external_activation_router"] is False
    assert gate["can_resume_model_chain"] is False
    assert gate["can_write_to_actuator"] is False
    assert gate["can_write_to_release_gate"] is False
    steps = {step["step_id"]: step for step in gate["sequence_steps"]}
    assert steps["response_source"]["ready"] is False
    assert steps["materialized_package_preflight"]["ready"] is False


def test_field_activation_external_readiness_gate_waits_for_materialized_package_dir_after_staging() -> None:
    chain = _ready_field_activation_chain()

    gate = build_field_activation_external_readiness_gate(
        chain["source_preflight"],
        chain["repair_work_order"],
        chain["response_preflight"],
        chain["assembly"],
        chain["staging"],
        chain["materialized_preflight"],
        chain["schema_preflight"],
    )

    assert gate["gate_status"] == (
        "field_activation_external_readiness_blocked_at_materialized_package_preflight"
    )
    assert gate["first_blocked_step"] == "materialized_package_preflight"
    assert gate["highest_priority_blocker"] == "R8U105_SET_MATERIALIZED_PACKAGE_DIR"
    assert gate["next_operator_action"] == "set_REAL_FIELD_REPLAY_PACKAGE_DIR"
    assert gate["ready_step_count"] == 6
    assert gate["blocked_step_count"] == 1
    assert gate["can_submit_to_external_activation_router"] is False
    assert gate["can_resume_model_chain"] is False


def test_field_activation_external_readiness_gate_allows_router_after_materialized_preflight(
    tmp_path: Path,
) -> None:
    chain = _ready_field_activation_chain()
    package_dir = tmp_path / "field_package"
    _write_materialized_package_from_staging(package_dir, chain["staging"])
    materialized_preflight = preflight_field_activation_materialized_package(
        chain["staging"],
        package_dir_path=str(package_dir),
    )

    gate = build_field_activation_external_readiness_gate(
        chain["source_preflight"],
        chain["repair_work_order"],
        chain["response_preflight"],
        chain["assembly"],
        chain["staging"],
        materialized_preflight,
        chain["schema_preflight"],
    )

    assert gate["gate_status"] == "field_activation_external_readiness_ready_for_external_activation_router"
    assert gate["first_blocked_step"] == ""
    assert gate["highest_priority_blocker"] == ""
    assert gate["next_operator_action"] == "run_external_activation_router_with_materialized_package_pointer"
    assert gate["ready_step_count"] == gate["total_step_count"]
    assert gate["blocked_step_count"] == 0
    assert gate["can_submit_to_external_activation_router"] is True
    assert gate["can_resume_model_chain"] is False
    assert gate["can_write_to_actuator"] is False
    assert gate["can_write_to_release_gate"] is False


def test_field_activation_response_submission_packet_guides_default_external_response() -> None:
    chain = _default_field_activation_chain()
    gate = build_field_activation_external_readiness_gate(
        chain["source_preflight"],
        chain["repair_work_order"],
        chain["response_preflight"],
        chain["assembly"],
        chain["staging"],
        chain["materialized_preflight"],
        chain["schema_preflight"],
    )

    packet = build_field_activation_response_submission_packet(
        chain["template"],
        chain["source_preflight"],
        chain["repair_work_order"],
        chain["response_preflight"],
        gate,
        response_template_path="outputs/model_core_governance/field_activation_response_template.json",
    )

    assert packet["packet_status"] == (
        "field_activation_response_submission_packet_waiting_for_external_response"
    )
    assert packet["source_env_var"] == "FIELD_ACTIVATION_RESPONSE_PATH"
    assert packet["required_response_row_count"] == 33
    assert packet["highest_priority_blocker"] == "R8U106_SUBMIT_FIELD_ACTIVATION_RESPONSE"
    assert packet["next_operator_action"] == "fill_response_template_and_set_FIELD_ACTIVATION_RESPONSE_PATH"
    assert packet["can_submit_to_response_preflight"] is True
    assert packet["can_route_to_external_activation_router"] is False
    assert packet["can_resume_model_chain"] is False
    assert packet["can_write_to_actuator"] is False
    assert packet["can_write_to_release_gate"] is False
    assert "FIELD_ACTIVATION_RESPONSE_PATH=/path/to/filled_response.json" in packet[
        "validation_commands"
    ][0]
    assert "does not generate field evidence" in packet["no_write_boundary"]


def test_field_activation_response_submission_packet_tracks_ready_response_before_package_dir() -> None:
    chain = _ready_field_activation_chain()
    gate = build_field_activation_external_readiness_gate(
        chain["source_preflight"],
        chain["repair_work_order"],
        chain["response_preflight"],
        chain["assembly"],
        chain["staging"],
        chain["materialized_preflight"],
        chain["schema_preflight"],
    )

    packet = build_field_activation_response_submission_packet(
        chain["template"],
        chain["source_preflight"],
        chain["repair_work_order"],
        chain["response_preflight"],
        gate,
        response_template_path="outputs/model_core_governance/field_activation_response_template.json",
    )

    assert packet["packet_status"] == (
        "field_activation_response_submission_packet_response_ready_for_package_assembly"
    )
    assert packet["repair_item_count"] == 0
    assert packet["highest_priority_repair_id"] == ""
    assert packet["top_repair_items"] == []
    assert packet["next_operator_action"] == (
        "stage_no_write_external_package_candidates_then_run_materialized_package_preflight"
    )
    assert packet["can_submit_to_response_preflight"] is True
    assert packet["can_route_to_external_activation_router"] is True
    assert packet["can_resume_model_chain"] is False
    assert packet["can_write_to_actuator"] is False
    assert packet["can_write_to_release_gate"] is False


def test_field_activation_response_repair_work_order_ready_after_filled_response() -> None:
    matrix = build_field_activation_matrix(_core_gate())
    template = build_field_activation_response_template(matrix)
    response = build_field_activation_response_template(matrix)
    for index, row in enumerate(response["evidence_rows"], start=1):
        row["data_origin"] = "field"
        row["batch_id"] = f"B{index:03d}"
        row["timestamp"] = "2026-06-21T08:00:00+08:00"
        row["node_id"] = "N3_catalyst_bed" if row["hidden_state"] == "catalyst_activity" else "N_out"
        row["sensor_id"] = "S_uv254_or_lab"
        row["evidence_value_reference"] = f"{row['table_name']}.{row['field_name']}"
        row["evidence_value"] = f"field_value_{index}"
        row["offline_method_id"] = "LCMS_METHOD_01"
        row["detection_limit"] = "method_recorded"
        row["chain_of_custody_id"] = "COC_001"
        row["operator_id"] = "operator_001"
        row["no_write_boundary_confirmed"] = "true"
        row["review_notes"] = "real field package row prepared for downstream preflight"

    source_preflight = preflight_field_activation_response_source(
        source_path="/tmp/field_activation_response.json",
        load_status="field_activation_response_source_loaded",
        response=response,
        default_response_template=template,
        matrix=matrix,
    )
    response_preflight = preflight_field_activation_response(response, matrix)
    assembly = build_field_activation_package_assembly_plan(
        response,
        matrix,
        response_preflight,
        _external_activation_contract(),
    )
    schema_contract = build_field_activation_schema_contract(matrix, template, assembly)
    schema_preflight = preflight_field_activation_schema_contract(
        schema_contract,
        response,
        assembly,
    )

    work_order = build_field_activation_response_repair_work_order(
        source_preflight,
        response_preflight,
        schema_preflight,
        assembly,
    )

    assert work_order["work_order_status"] == (
        "field_activation_response_repair_work_order_ready_no_repairs_required"
    )
    assert work_order["repair_item_count"] == 0
    assert work_order["highest_priority_repair_id"] == ""
    assert work_order["can_route_to_package_assembly"] is True
    assert work_order["can_stage_external_package_candidates"] is True
    assert work_order["can_resume_model_chain"] is False
    assert work_order["can_write_to_actuator"] is False
    assert work_order["can_write_to_release_gate"] is False


def _default_field_activation_chain() -> dict[str, object]:
    matrix = build_field_activation_matrix(_core_gate())
    template = build_field_activation_response_template(matrix)
    source_preflight = preflight_field_activation_response_source(
        source_path="",
        load_status="field_activation_response_source_not_supplied",
        response=template,
        default_response_template=template,
        matrix=matrix,
    )
    response_preflight = preflight_field_activation_response(template, matrix)
    assembly = build_field_activation_package_assembly_plan(
        template,
        matrix,
        response_preflight,
        _external_activation_contract(),
    )
    staging = build_field_activation_package_staging_manifest(
        template,
        assembly,
        response_preflight,
        source_preflight,
    )
    materialized_preflight = preflight_field_activation_materialized_package(
        staging,
        package_dir_path="",
    )
    schema_contract = build_field_activation_schema_contract(matrix, template, assembly)
    schema_preflight = preflight_field_activation_schema_contract(
        schema_contract,
        template,
        assembly,
    )
    repair_work_order = build_field_activation_response_repair_work_order(
        source_preflight,
        response_preflight,
        schema_preflight,
        assembly,
    )
    return {
        "matrix": matrix,
        "template": template,
        "response": template,
        "source_preflight": source_preflight,
        "response_preflight": response_preflight,
        "assembly": assembly,
        "staging": staging,
        "materialized_preflight": materialized_preflight,
        "schema_preflight": schema_preflight,
        "repair_work_order": repair_work_order,
    }


def _ready_field_activation_chain() -> dict[str, object]:
    matrix = build_field_activation_matrix(_core_gate())
    template = build_field_activation_response_template(matrix)
    response = build_field_activation_response_template(matrix)
    _fill_field_activation_response(response)
    source_preflight = preflight_field_activation_response_source(
        source_path="/tmp/field_activation_response.json",
        load_status="field_activation_response_source_loaded",
        response=response,
        default_response_template=template,
        matrix=matrix,
    )
    response_preflight = preflight_field_activation_response(response, matrix)
    assembly = build_field_activation_package_assembly_plan(
        response,
        matrix,
        response_preflight,
        _external_activation_contract(),
    )
    staging = build_field_activation_package_staging_manifest(
        response,
        assembly,
        response_preflight,
        source_preflight,
    )
    materialized_preflight = preflight_field_activation_materialized_package(
        staging,
        package_dir_path="",
    )
    schema_contract = build_field_activation_schema_contract(matrix, template, assembly)
    schema_preflight = preflight_field_activation_schema_contract(
        schema_contract,
        response,
        assembly,
    )
    repair_work_order = build_field_activation_response_repair_work_order(
        source_preflight,
        response_preflight,
        schema_preflight,
        assembly,
    )
    return {
        "matrix": matrix,
        "template": template,
        "response": response,
        "source_preflight": source_preflight,
        "response_preflight": response_preflight,
        "assembly": assembly,
        "staging": staging,
        "materialized_preflight": materialized_preflight,
        "schema_preflight": schema_preflight,
        "repair_work_order": repair_work_order,
    }


def _ready_field_activation_staging() -> dict[str, object]:
    return _ready_field_activation_chain()["staging"]


def _fill_field_activation_response(response: dict[str, object]) -> None:
    for index, row in enumerate(response["evidence_rows"], start=1):
        row["data_origin"] = "field"
        row["batch_id"] = f"B_{str(row['hidden_state']).upper()}"
        row["timestamp"] = "2026-06-21T08:00:00+08:00"
        row["node_id"] = "N3_catalyst_bed" if row["hidden_state"] == "catalyst_activity" else "N_out"
        row["sensor_id"] = "S_uv254_or_lab"
        row["evidence_value_reference"] = f"{row['table_name']}.{row['field_name']}"
        row["evidence_value"] = f"field_value_{index}"
        row["offline_method_id"] = "LCMS_METHOD_01"
        row["detection_limit"] = "method_recorded"
        row["chain_of_custody_id"] = "COC_001"
        row["operator_id"] = "operator_001"
        row["no_write_boundary_confirmed"] = "true"
        row["review_notes"] = "real field package row prepared for downstream preflight"


def _write_materialized_package_from_staging(
    package_dir: Path,
    staging: dict[str, object],
    *,
    include_metadata: bool = True,
) -> None:
    package_dir.mkdir(parents=True, exist_ok=False)
    if include_metadata:
        metadata = {
            "data_origin": "field",
            "site_id": "site_alpha",
            "campaign_id": "campaign_001",
            "sampling_start": "2026-06-21T08:00:00+08:00",
            "sampling_end": "2026-06-21T12:00:00+08:00",
            "operator_id": "operator_001",
            "instrument_snapshot_id": "sensor_bank_001",
            "chain_of_custody_id": "COC_001",
        }
        (package_dir / "metadata.json").write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    channel = staging["selected_channel_manifests"][0]
    for table in channel["table_manifests"]:
        path = package_dir / table["output_file"]
        columns = list(table["required_columns"])
        blueprint_rows = [
            dict(blueprint["output_row"])
            for blueprint in table.get("row_blueprints", [])
            if isinstance(blueprint, dict) and isinstance(blueprint.get("output_row"), dict)
        ]
        rows = blueprint_rows or [{column: _field_value_for_column(column) for column in columns}]
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=columns)
            writer.writeheader()
            for row in rows:
                writer.writerow({column: row.get(column, "") for column in columns})


def _field_value_for_column(column: str) -> str:
    return {
        "batch_id": "B001",
        "data_origin": "field",
        "chain_of_custody_id": "COC_001",
        "operator_id": "operator_001",
        "timestamp": "2026-06-21T08:00:00+08:00",
        "node_id": "N3_catalyst_bed",
        "sensor_id": "S_uv254_or_lab",
        "offline_method_id": "LCMS_METHOD_01",
        "detection_limit": "method_recorded",
    }.get(column, "field_value_1")


def _core_gate() -> dict[str, object]:
    return {
        "gate_id": "R8u68_quantified_core_score_and_hidden_state_termination_gate",
        "hidden_state_coverage_ledger": {
            "state_rows": [
                _state("pollutant_residual", sparse_ready=True),
                _state("reaction_completion", sparse_ready=True),
                _state(
                    "catalyst_activity",
                    sparse_ready=False,
                    field_evidence_needed=[
                        "node_modality_sensor_timeseries.N3_catalyst_bed_outlet:UV254_abs",
                        "node_modality_sensor_timeseries.N3_catalyst_bed_outlet:ORP_mV",
                        "node_modality_sensor_timeseries.N3_catalyst_bed:pressure_drop_kPa",
                        "offline_lab_results.catalyst_activity",
                        "campaign_operation_log.regeneration_event",
                    ],
                ),
                _state("matrix_interference", sparse_ready=False),
                _state("hydraulic_delay", sparse_ready=True),
                _state("release_or_byproduct_risk", sparse_ready=True),
            ]
        },
        "external_resume_conditions": {
            "router_model_chain_ready_channel_ids": [],
            "router_route_summary": [
                {
                    "channel_id": "R7_REAL_FIELD_PACKAGE",
                    "package_pointer": "REAL_FIELD_REPLAY_PACKAGE_DIR",
                    "route_status": "activation_route_waiting_for_env_var",
                    "route_ready": False,
                    "can_resume_model_chain": False,
                    "blocked_reason": "REAL_FIELD_REPLAY_PACKAGE_DIR:not_set",
                },
                {
                    "channel_id": "R8U66_PATH_ENDPOINT_LABEL_PACKAGE",
                    "package_pointer": "FIELD_PATH_ENDPOINT_LABEL_PACKAGE_DIR",
                    "route_status": "activation_route_waiting_for_env_var",
                    "route_ready": False,
                    "can_resume_model_chain": False,
                    "blocked_reason": "FIELD_PATH_ENDPOINT_LABEL_PACKAGE_DIR:not_set",
                },
            ],
            "channels": [
                {
                    "channel_id": "R7_REAL_FIELD_PACKAGE",
                    "package_pointer": "REAL_FIELD_REPLAY_PACKAGE_DIR",
                    "current_status": "field_evidence_sufficiency_blocked_before_import",
                    "can_resume_model_chain": False,
                    "resumes_to": ["Agent44 field import preflight"],
                },
                {
                    "channel_id": "R8U66_PATH_ENDPOINT_LABEL_PACKAGE",
                    "package_pointer": "FIELD_PATH_ENDPOINT_LABEL_PACKAGE_DIR",
                    "current_status": "field_path_endpoint_label_package_blocked_by_preflight",
                    "can_resume_model_chain": False,
                    "resumes_to": ["Agent54 field layout holdout"],
                },
            ],
        },
    }


def _state(
    hidden_state: str,
    *,
    sparse_ready: bool,
    field_evidence_needed: list[str] | None = None,
) -> dict[str, object]:
    return {
        "hidden_state": hidden_state,
        "contract_covered": True,
        "sparse_estimation_ready": sparse_ready,
        "field_validated": False,
        "control_ready": False,
        "coverage_stage": "synthetic_sparse_estimation_ready" if sparse_ready else "synthetic_proxy_design_ready_needs_field_labels",
        "field_evidence_needed": field_evidence_needed or [f"offline_lab_results.{hidden_state}"],
        "evidence_boundary": (
            f"{hidden_state} is not field validated; synthetic sparse/proxy coverage can guide design, "
            "but cannot support field claim, actuator write or release gate."
        ),
    }


def _external_activation_contract() -> dict[str, object]:
    return {
        "channels": [
            {
                "channel_id": "R7_REAL_FIELD_PACKAGE",
                "package_pointer": "REAL_FIELD_REPLAY_PACKAGE_DIR",
                "required_evidence": [
                    "metadata.json with data_origin=field",
                    "timestamped sensor_timeseries rows",
                    "campaign_operation_log rows",
                    "offline_lab_results rows",
                ],
                "reject_if": ["template markers or non-field provenance are present"],
                "resumes_to": ["Agent44 field import preflight"],
            },
            {
                "channel_id": "R8U66_PATH_ENDPOINT_LABEL_PACKAGE",
                "package_pointer": "FIELD_PATH_ENDPOINT_LABEL_PACKAGE_DIR",
                "required_evidence": [
                    "site_topology_or_bed_geometry",
                    "node_modality_sensor_timeseries",
                    "hydraulic_path_stage_labels",
                ],
                "reject_if": ["matched_batch_count is below 5"],
                "resumes_to": ["Agent54 field layout holdout"],
            },
        ]
    }


def _focused_catalyst_kit_metrics() -> dict[str, object]:
    return {
        "kit_id": "R8u111_catalyst_response_submission_kit",
        "kit_status": "catalyst_response_submission_kit_ready_for_operator_fill",
        "target_hidden_state": "catalyst_activity",
        "target_response_row_count": 6,
        "focused_response_template_path": (
            "outputs/catalyst_response_submission_kit/focused_catalyst_response_template.json"
        ),
        "focused_response_schema_path": (
            "outputs/catalyst_response_submission_kit/focused_catalyst_response_schema.json"
        ),
        "full_response_merge_plan_path": (
            "outputs/catalyst_response_submission_kit/focused_to_full_response_merge_plan.json"
        ),
    }


def _focused_catalyst_merge_preflight() -> dict[str, object]:
    return {
        "preflight_id": "R8u112_focused_catalyst_response_merge_preflight",
        "preflight_status": "focused_catalyst_response_merge_waiting_for_FOCUSED_CATALYST_RESPONSE_PATH",
        "source_env_var": "FOCUSED_CATALYST_RESPONSE_PATH",
        "expected_focused_response_row_count": 6,
        "next_operator_action": "fill_focused_catalyst_response_template_and_set_FOCUSED_CATALYST_RESPONSE_PATH",
        "focused_catalyst_response_repair_work_order": {
            "work_order_status": "focused_catalyst_response_repair_work_order_waiting_for_external_response",
            "repair_item_count": 1,
            "highest_priority_repair_id": "FOCUSED_SOURCE_SUBMIT_RESPONSE",
            "next_operator_action": (
                "fill_outputs/catalyst_response_submission_kit/focused_catalyst_response_template.json_"
                "with_real_field_values_then_set_FOCUSED_CATALYST_RESPONSE_PATH"
            ),
        },
    }


def _focused_catalyst_merge_preflight_source_blocked() -> dict[str, object]:
    preflight = _focused_catalyst_merge_preflight()
    preflight["preflight_status"] = "focused_catalyst_response_merge_blocked_at_source_preflight"
    preflight["source_can_run_merge_preflight"] = False
    preflight["next_operator_action"] = "repair_FOCUSED_CATALYST_RESPONSE_PATH_file_or_json_shape"
    preflight["focused_catalyst_response_repair_work_order"] = {
        "work_order_status": "focused_catalyst_response_repair_work_order_blocked_at_source_preflight",
        "repair_item_count": 1,
        "highest_priority_repair_id": "FOCUSED_SOURCE_REPAIR_LOAD",
        "next_operator_action": "repair_FOCUSED_CATALYST_RESPONSE_PATH_file_path",
    }
    return preflight

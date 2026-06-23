from __future__ import annotations

from copy import deepcopy

from water_ai.focused_catalyst_response_merge import (
    build_focused_catalyst_response_merge_preflight,
    build_focused_catalyst_response_repair_work_order,
    preflight_focused_catalyst_response_source,
)
from experiments.run_focused_catalyst_response_merge import _deliverable_md


def test_focused_merge_waits_for_external_focused_response_path() -> None:
    source_preflight = preflight_focused_catalyst_response_source(
        source_path="",
        load_status="focused_catalyst_response_source_not_supplied",
        response=_focused_template(),
        default_response_template=_focused_template(),
    )
    result = build_focused_catalyst_response_merge_preflight(
        focused_response=_focused_template(),
        focused_schema=_schema(),
        full_response_template=_full_template(),
        merge_plan=_merge_plan(),
        external_response_supplied=False,
        source_preflight=source_preflight,
    )

    assert source_preflight["source_preflight_status"] == "focused_catalyst_response_source_using_default_template"
    assert source_preflight["can_run_merge_preflight"] is True
    assert result["preflight_status"] == "focused_catalyst_response_merge_waiting_for_FOCUSED_CATALYST_RESPONSE_PATH"
    assert result["source_preflight_status"] == "focused_catalyst_response_source_using_default_template"
    assert result["source_can_run_merge_preflight"] is True
    assert result["row_preflight_pass"] is False
    assert result["can_emit_merged_full_response_candidate"] is False
    assert result["can_submit_candidate_as_FIELD_ACTIVATION_RESPONSE_PATH"] is False
    assert result["can_route_to_agent51_field_proxy_holdout"] is False
    assert result["can_write_to_actuator"] is False
    assert result["can_write_to_release_gate"] is False
    assert result["merged_full_response_candidate_availability_status"] == (
        "candidate_not_submittable_waiting_for_FOCUSED_CATALYST_RESPONSE_PATH"
    )
    assert result["merged_full_response_candidate_self_declared_submit_ready"] is False
    assert result["merged_full_response_candidate_preflight_submit_ready"] is False
    assert result["merged_full_response_candidate_external_response_supplied"] is False
    assert "not field validation" in result["merged_full_response_candidate_submit_ready_semantics"]
    candidate = result["merged_full_response_candidate"]
    assert candidate["candidate_availability_status"] == (
        "candidate_not_submittable_waiting_for_FOCUSED_CATALYST_RESPONSE_PATH"
    )
    assert candidate["can_submit_candidate_as_FIELD_ACTIVATION_RESPONSE_PATH"] is False
    assert candidate["candidate_preflight_submit_ready"] is False
    assert candidate["candidate_self_declared_submit_ready"] is False
    assert "not field validation" in candidate["candidate_submit_ready_semantics"]
    assert candidate["external_focused_response_supplied"] is False
    assert candidate["focused_replacement_row_count"] == 0
    assert candidate["focused_row_preflight_pass"] is False
    assert "must not be routed as field evidence" in candidate["candidate_use_boundary"]

    work_order = build_focused_catalyst_response_repair_work_order(
        source_preflight=source_preflight,
        merge_preflight=result,
    )

    assert work_order["work_order_status"] == (
        "focused_catalyst_response_repair_work_order_waiting_for_external_response"
    )
    assert work_order["repair_item_count"] == 1
    assert work_order["highest_priority_repair_id"] == "FOCUSED_SOURCE_SUBMIT_RESPONSE"
    assert work_order["can_submit_candidate_as_FIELD_ACTIVATION_RESPONSE_PATH"] is False


def test_focused_merge_blocks_when_source_path_is_missing() -> None:
    source_preflight = preflight_focused_catalyst_response_source(
        source_path="/tmp/missing-focused-catalyst-response.json",
        load_status="focused_catalyst_response_source_file_missing",
        response={},
        default_response_template=_focused_template(),
    )
    result = build_focused_catalyst_response_merge_preflight(
        focused_response=_focused_template(),
        focused_schema=_schema(),
        full_response_template=_full_template(),
        merge_plan=_merge_plan(),
        source_path="/tmp/missing-focused-catalyst-response.json",
        external_response_supplied=False,
        source_preflight=source_preflight,
    )

    assert source_preflight["source_preflight_status"] == "focused_catalyst_response_source_file_missing"
    assert source_preflight["can_run_merge_preflight"] is False
    assert source_preflight["next_operator_action"] == "repair_FOCUSED_CATALYST_RESPONSE_PATH_file_path"
    assert result["preflight_status"] == "focused_catalyst_response_merge_blocked_at_source_preflight"
    assert result["source_preflight_status"] == "focused_catalyst_response_source_file_missing"
    assert result["source_can_run_merge_preflight"] is False
    assert result["next_operator_action"] == "repair_FOCUSED_CATALYST_RESPONSE_PATH_file_or_json_shape"
    assert result["can_emit_merged_full_response_candidate"] is False
    assert result["can_submit_candidate_as_FIELD_ACTIVATION_RESPONSE_PATH"] is False
    assert result["can_write_to_actuator"] is False
    assert result["can_write_to_release_gate"] is False

    work_order = build_focused_catalyst_response_repair_work_order(
        source_preflight=source_preflight,
        merge_preflight=result,
    )

    assert work_order["work_order_status"] == "focused_catalyst_response_repair_work_order_blocked_at_source_preflight"
    assert work_order["repair_item_count"] == 1
    assert work_order["highest_priority_repair_id"] == "FOCUSED_SOURCE_REPAIR_LOAD"
    assert work_order["next_operator_action"] == "repair_FOCUSED_CATALYST_RESPONSE_PATH_file_path"


def test_focused_merge_emits_full_response_candidate_without_claiming_full_preflight_pass() -> None:
    source_preflight = preflight_focused_catalyst_response_source(
        source_path="/tmp/focused.json",
        load_status="focused_catalyst_response_source_loaded",
        response=_filled_focused_response(["B001", "B002", "B003"]),
        default_response_template=_focused_template(),
    )
    result = build_focused_catalyst_response_merge_preflight(
        focused_response=_filled_focused_response(["B001", "B002", "B003"]),
        focused_schema=_schema(),
        full_response_template=_full_template(),
        merge_plan=_merge_plan(),
        source_path="/tmp/focused.json",
        external_response_supplied=True,
        source_preflight=source_preflight,
    )

    candidate = result["merged_full_response_candidate"]
    rows_by_id = {row["response_row_id"]: row for row in candidate["evidence_rows"]}

    assert result["preflight_status"] == "focused_catalyst_response_merge_ready_for_FIELD_ACTIVATION_RESPONSE_PATH_candidate"
    assert result["source_preflight_status"] == "focused_catalyst_response_source_loaded"
    assert result["source_can_run_merge_preflight"] is True
    assert result["row_preflight_pass"] is True
    assert result["batch_alignment"]["matched_batch_count"] == 3
    assert result["can_emit_merged_full_response_candidate"] is True
    assert result["can_submit_candidate_as_FIELD_ACTIVATION_RESPONSE_PATH"] is True
    assert result["merged_full_response_candidate_availability_status"] == (
        "candidate_ready_for_FIELD_ACTIVATION_RESPONSE_PATH_preflight_only"
    )
    assert result["merged_full_response_candidate_self_declared_submit_ready"] is True
    assert result["merged_full_response_candidate_preflight_submit_ready"] is True
    assert result["merged_full_response_candidate_external_response_supplied"] is True
    assert "actuator readiness" in result["merged_full_response_candidate_submit_ready_semantics"]
    assert result["can_route_to_full_external_activation_router"] is False
    assert result["can_route_to_agent51_field_proxy_holdout"] is False
    assert candidate["package_type"] == "field_activation_evidence_response"
    assert candidate["focused_replacement_row_count"] == 6
    assert candidate["candidate_availability_status"] == (
        "candidate_ready_for_FIELD_ACTIVATION_RESPONSE_PATH_preflight_only"
    )
    assert candidate["can_submit_candidate_as_FIELD_ACTIVATION_RESPONSE_PATH"] is True
    assert candidate["candidate_preflight_submit_ready"] is True
    assert candidate["candidate_self_declared_submit_ready"] is True
    assert candidate["external_focused_response_supplied"] is True
    assert candidate["source_preflight_status"] == "focused_catalyst_response_source_loaded"
    assert candidate["focused_row_preflight_pass"] is True
    assert candidate["focused_matched_batch_count"] == 3
    assert candidate["focused_minimum_matched_batch_count"] == 3
    assert len(candidate["evidence_rows"]) == 33
    assert rows_by_id["catalyst_activity_04"]["data_origin"] == "field"
    assert rows_by_id["other_state_01"]["data_origin"] == "TODO_field"
    assert "remaining rows may still contain TODO" in result["full_response_boundary"]

    work_order = build_focused_catalyst_response_repair_work_order(
        source_preflight=source_preflight,
        merge_preflight=result,
    )

    assert work_order["work_order_status"] == (
        "focused_catalyst_response_repair_work_order_ready_for_FIELD_ACTIVATION_RESPONSE_PATH_candidate"
    )
    assert work_order["repair_item_count"] == 0
    assert work_order["can_submit_candidate_as_FIELD_ACTIVATION_RESPONSE_PATH"] is True
    assert work_order["can_write_to_actuator"] is False


def test_focused_merge_deliverable_uses_preflight_submit_ready_not_ambiguous_self_declared_label() -> None:
    source_preflight = preflight_focused_catalyst_response_source(
        source_path="/tmp/focused.json",
        load_status="focused_catalyst_response_source_loaded",
        response=_filled_focused_response(["B001", "B002", "B003"]),
        default_response_template=_focused_template(),
    )
    result = build_focused_catalyst_response_merge_preflight(
        focused_response=_filled_focused_response(["B001", "B002", "B003"]),
        focused_schema=_schema(),
        full_response_template=_full_template(),
        merge_plan=_merge_plan(),
        source_path="/tmp/focused.json",
        external_response_supplied=True,
        source_preflight=source_preflight,
    )
    result["focused_catalyst_response_repair_work_order"] = (
        build_focused_catalyst_response_repair_work_order(
            source_preflight=source_preflight,
            merge_preflight=result,
        )
    )
    candidate = result["merged_full_response_candidate"]

    report_md = _deliverable_md(result, candidate)

    assert "candidate_preflight_submit_ready: `True`" in report_md
    assert "candidate_self_declared_submit_ready_legacy_alias: `True`" in report_md
    assert "candidate_submit_ready_semantics:" in report_md
    assert "not field validation" in report_md


def test_focused_merge_blocks_when_shared_batch_requirement_is_not_met() -> None:
    focused = _filled_focused_response(["B001", "B002"])

    result = build_focused_catalyst_response_merge_preflight(
        focused_response=focused,
        focused_schema=_schema(),
        full_response_template=_full_template(),
        merge_plan=_merge_plan(),
        external_response_supplied=True,
    )

    assert result["preflight_status"] == "focused_catalyst_response_merge_blocked_at_batch_alignment"
    assert result["row_preflight_pass"] is False
    assert result["batch_alignment"]["matched_batch_count"] == 2
    assert result["can_emit_merged_full_response_candidate"] is False

    work_order = build_focused_catalyst_response_repair_work_order(
        source_preflight=preflight_focused_catalyst_response_source(
            source_path="/tmp/focused.json",
            load_status="focused_catalyst_response_source_loaded",
            response=focused,
            default_response_template=_focused_template(),
        ),
        merge_preflight=result,
    )

    assert work_order["work_order_status"] == "focused_catalyst_response_repair_work_order_blocked_at_batch_alignment"
    assert work_order["matched_batch_deficit"] == 1
    assert work_order["highest_priority_repair_id"] == "FOCUSED_BATCH_ALIGNMENT"
    assert work_order["next_operator_action"] == (
        "add_at_least_three_shared_real_field_batch_ids_to_all_six_focused_rows"
    )


def _schema() -> dict[str, object]:
    return {
        "required_top_level_fields": [
            "template_id",
            "package_type",
            "source_interface_id",
            "target_hidden_state",
            "required_response_row_count",
            "minimum_matched_batch_count",
            "evidence_rows",
            "no_write_boundary",
        ],
        "required_row_fields": [
            "response_row_id",
            "hidden_state",
            "required_evidence",
            "evidence_channel",
            "table_name",
            "field_name",
            "data_origin",
            "batch_id",
            "matched_batch_ids",
            "timestamp",
            "node_id",
            "sensor_id",
            "evidence_value_reference",
            "offline_method_id",
            "detection_limit",
            "chain_of_custody_id",
            "operator_id",
            "no_write_boundary_confirmed",
            "review_notes",
        ],
        "row_count_must_equal": 6,
    }


def _merge_plan() -> dict[str, object]:
    return {
        "focused_response_row_ids": _row_ids(),
        "remaining_full_response_row_count": 27,
    }


def _focused_template() -> dict[str, object]:
    response = _filled_focused_response(["TODO_batch_id_1", "TODO_batch_id_2", "TODO_batch_id_3"])
    for row in response["evidence_rows"]:
        row["data_origin"] = "TODO_field"
        row["batch_id"] = "TODO_batch_id_1,TODO_batch_id_2,TODO_batch_id_3"
        row["matched_batch_ids"] = ["TODO_batch_id_1", "TODO_batch_id_2", "TODO_batch_id_3"]
        row["evidence_value_reference"] = "TODO_table_column_or_file_reference"
        row["no_write_boundary_confirmed"] = "TODO_true"
    return response


def _filled_focused_response(batch_ids: list[str]) -> dict[str, object]:
    rows = []
    for row_id, evidence, role, rank in _target_rows():
        table_name, field_name = evidence.split(".", 1)
        rows.append(
            {
                "response_row_id": row_id,
                "hidden_state": "catalyst_activity",
                "required_evidence": evidence,
                "evidence_channel": "R7_REAL_FIELD_PACKAGE",
                "table_name": table_name,
                "field_name": field_name,
                "data_origin": "field",
                "batch_id": ",".join(batch_ids),
                "matched_batch_ids": batch_ids,
                "timestamp": "2026-06-01T08:00:00Z",
                "node_id": "N3_catalyst_bed",
                "sensor_id": "field_instrument_ref",
                "evidence_value_reference": f"{evidence}@field_package",
                "offline_method_id": "field_method_ref",
                "detection_limit": "field_detection_limit_ref",
                "chain_of_custody_id": "COC-001",
                "operator_id": "operator-001",
                "no_write_boundary_confirmed": True,
                "review_notes": "field provenance reference supplied",
                "observation_role": role,
                "priority": "P1" if rank == 1 else "P2",
                "priority_rank": rank,
            }
        )
    return {
        "template_id": "filled_focused_catalyst_response",
        "package_type": "focused_catalyst_activity_response",
        "source_interface_id": "R8u97_field_activation_matrix_interface",
        "target_hidden_state": "catalyst_activity",
        "required_response_row_count": 6,
        "minimum_matched_batch_count": 3,
        "evidence_rows": rows,
        "no_write_boundary": "No actuator or release gate write is authorized.",
    }


def _full_template() -> dict[str, object]:
    focused = _filled_focused_response(["TODO_batch_id_1", "TODO_batch_id_2", "TODO_batch_id_3"])
    catalyst_rows = deepcopy(focused["evidence_rows"])
    for row in catalyst_rows:
        row["data_origin"] = "TODO_field"
        row["batch_id"] = "TODO_batch_id"
        row["matched_batch_ids"] = ["TODO_batch_id"]
        row["evidence_value_reference"] = "TODO_table_column_or_file_reference"
        row["no_write_boundary_confirmed"] = "TODO_true"
    other_rows = [
        {
            "response_row_id": f"other_state_{index:02d}",
            "hidden_state": "other_state",
            "required_evidence": f"other_table.other_field_{index}",
            "data_origin": "TODO_field",
        }
        for index in range(27)
    ]
    return {
        "template_id": "R8u98_field_activation_evidence_response_template",
        "package_type": "field_activation_evidence_response",
        "source_interface_id": "R8u97_field_activation_matrix_interface",
        "required_response_row_count": 33,
        "evidence_rows": catalyst_rows + other_rows,
    }


def _row_ids() -> list[str]:
    return [row[0] for row in _target_rows()]


def _target_rows() -> list[tuple[str, str, str, int]]:
    return [
        ("catalyst_activity_03", "node_modality_sensor_timeseries.N3_catalyst_bed:pressure_drop_kPa", "pressure_headloss_proxy", 1),
        ("catalyst_activity_04", "offline_lab_results.catalyst_activity", "catalyst_activity_label", 1),
        ("catalyst_activity_05", "campaign_operation_log.regeneration_event", "regeneration_event", 1),
        ("catalyst_activity_06", "site_topology_or_bed_geometry.nominal_HRT_min", "hydraulic_normalizer", 1),
        ("catalyst_activity_01", "node_modality_sensor_timeseries.N3_catalyst_bed_outlet:UV254_abs", "bed_outlet_uv254_proxy", 2),
        ("catalyst_activity_02", "node_modality_sensor_timeseries.N3_catalyst_bed_outlet:ORP_mV", "bed_outlet_orp_proxy", 2),
    ]

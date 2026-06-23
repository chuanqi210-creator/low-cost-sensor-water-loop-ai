from __future__ import annotations

from copy import deepcopy

from water_ai.catalyst_evidence_response_gate import build_catalyst_evidence_response_gate


def test_catalyst_gate_waits_for_external_field_activation_response() -> None:
    response = _response_template()

    result = build_catalyst_evidence_response_gate(
        observation_response_bridge=_bridge(),
        response=response,
        response_source_preflight={"external_response_supplied": False},
        response_preflight={"preflight_status": "field_activation_response_blocked_before_external_package_preflight"},
        response_submission_packet={"next_operator_action": "fill_response_template_and_set_FIELD_ACTIVATION_RESPONSE_PATH"},
    )

    assert result["gate_status"] == "catalyst_evidence_response_gate_waiting_for_FIELD_ACTIVATION_RESPONSE_PATH"
    assert result["target_response_row_count"] == 6
    assert result["row_level_preflight_pass"] is False
    assert result["can_route_to_focused_materialized_package_preflight"] is False
    assert result["can_route_to_agent51_field_proxy_holdout"] is False
    assert result["can_relax_agent49_catalyst_uncertainty_block"] is False
    assert result["can_write_to_actuator"] is False
    assert result["can_write_to_release_gate"] is False


def test_catalyst_gate_accepts_filled_priority_rows_but_does_not_relax_agent49() -> None:
    response = _filled_response(matched_batch_ids=["B001", "B002", "B003"])

    result = build_catalyst_evidence_response_gate(
        observation_response_bridge=_bridge(),
        response=response,
        response_source_preflight={"external_response_supplied": True},
        response_preflight={"preflight_status": "field_activation_response_blocked_before_external_package_preflight"},
        response_submission_packet={"packet_status": "field_activation_response_submission_packet_waiting_for_external_response"},
    )

    assert result["gate_status"] == "catalyst_evidence_response_gate_ready_for_focused_package_preflight"
    assert result["provided_target_response_row_count"] == 6
    assert result["blocked_target_response_row_count"] == 0
    assert result["row_level_preflight_pass"] is True
    assert result["batch_alignment"]["matched_batch_count"] == 3
    assert result["batch_alignment"]["matched_batch_requirement_pass"] is True
    assert result["can_route_to_focused_materialized_package_preflight"] is True
    assert result["can_route_to_agent51_field_proxy_holdout"] is False
    assert result["can_relax_agent49_catalyst_uncertainty_block"] is False
    assert "does not run Agent51 holdout" in result["field_boundary"]


def test_catalyst_gate_blocks_missing_priority_row() -> None:
    response = _filled_response(matched_batch_ids=["B001", "B002", "B003"])
    response["evidence_rows"] = [
        row for row in response["evidence_rows"] if row["response_row_id"] != "catalyst_activity_04"
    ]

    result = build_catalyst_evidence_response_gate(
        observation_response_bridge=_bridge(),
        response=response,
        response_source_preflight={"external_response_supplied": True},
        response_preflight={"preflight_status": "field_activation_response_blocked_before_external_package_preflight"},
        response_submission_packet={},
    )

    assert result["gate_status"] == "catalyst_evidence_response_gate_blocked_at_priority_rows"
    assert result["missing_target_response_row_count"] == 1
    assert result["can_route_to_focused_materialized_package_preflight"] is False
    missing = [row for row in result["target_row_results"] if row["row_status"] == "missing_response_row"]
    assert missing[0]["response_row_id"] == "catalyst_activity_04"


def _bridge() -> dict[str, object]:
    rows = [
        ("catalyst_activity_03", "node_modality_sensor_timeseries.N3_catalyst_bed:pressure_drop_kPa", "pressure_headloss_proxy", 1),
        ("catalyst_activity_04", "offline_lab_results.catalyst_activity", "catalyst_activity_label", 1),
        ("catalyst_activity_05", "campaign_operation_log.regeneration_event", "regeneration_event", 1),
        ("catalyst_activity_06", "site_topology_or_bed_geometry.nominal_HRT_min", "hydraulic_normalizer", 1),
        ("catalyst_activity_01", "node_modality_sensor_timeseries.N3_catalyst_bed_outlet:UV254_abs", "bed_outlet_uv254_proxy", 2),
        ("catalyst_activity_02", "node_modality_sensor_timeseries.N3_catalyst_bed_outlet:ORP_mV", "bed_outlet_orp_proxy", 2),
    ]
    return {
        "bridge_id": "R8u109_observation_response_bridge",
        "bridge_status": "observation_response_bridge_ready_for_priority_field_response_fill",
        "r2_fv4_requirement": {"minimum_matched_batch_count": 3},
        "priority_response_rows": [
            {
                "response_row_id": row_id,
                "hidden_state": "catalyst_activity",
                "required_evidence": evidence,
                "observation_role": role,
                "priority_rank": rank,
            }
            for row_id, evidence, role, rank in rows
        ],
    }


def _response_template() -> dict[str, object]:
    response = _filled_response(matched_batch_ids=["TODO_batch_id"])
    for row in response["evidence_rows"]:
        row["data_origin"] = "TODO_field"
        row["batch_id"] = "TODO_batch_id"
        row["matched_batch_ids"] = ["TODO_batch_id"]
        row["evidence_value_reference"] = "TODO_table_column_or_file_reference"
        row["no_write_boundary_confirmed"] = "TODO_true"
    return response


def _filled_response(*, matched_batch_ids: list[str]) -> dict[str, object]:
    bridge = _bridge()
    rows = []
    for target in bridge["priority_response_rows"]:
        row = deepcopy(target)
        row.update(
            {
                "data_origin": "field",
                "batch_id": ",".join(matched_batch_ids),
                "matched_batch_ids": matched_batch_ids,
                "timestamp": "2026-06-01T08:00:00Z",
                "node_id": "N3_catalyst_bed",
                "sensor_id": "field_instrument_ref",
                "evidence_value_reference": f"{row['required_evidence']}@field_package",
                "offline_method_id": "field_method_ref",
                "detection_limit": "field_method_detection_limit_ref",
                "chain_of_custody_id": "COC-001",
                "operator_id": "operator-001",
                "no_write_boundary_confirmed": True,
                "review_notes": "field provenance reference supplied",
            }
        )
        rows.append(row)
    return {
        "template_id": "external_response",
        "package_type": "field_activation_evidence_response",
        "source_interface_id": "R8u97_field_activation_matrix_interface",
        "required_response_row_count": len(rows),
        "evidence_rows": rows,
    }

from water_ai.catalyst_response_submission_kit import build_catalyst_response_submission_kit


def test_catalyst_submission_kit_builds_six_row_operator_template() -> None:
    kit = build_catalyst_response_submission_kit(
        observation_response_bridge=_bridge(),
        full_response_template=_full_response_template(),
        catalyst_evidence_response_gate=_focused_gate(),
    )

    template = kit["focused_response_template"]
    schema = kit["focused_response_schema"]
    merge_plan = kit["full_response_merge_plan"]

    assert kit["kit_status"] == "catalyst_response_submission_kit_ready_for_operator_fill"
    assert kit["target_hidden_state"] == "catalyst_activity"
    assert kit["target_response_row_count"] == 6
    assert template["package_type"] == "focused_catalyst_activity_response"
    assert template["required_response_row_count"] == 6
    assert template["minimum_matched_batch_count"] == 3
    assert schema["row_count_must_equal"] == 6
    assert len(template["evidence_rows"]) == 6
    assert [row["response_row_id"] for row in template["evidence_rows"][:4]] == [
        "catalyst_activity_03",
        "catalyst_activity_04",
        "catalyst_activity_05",
        "catalyst_activity_06",
    ]
    assert all(row["data_origin"] == "TODO_field" for row in template["evidence_rows"])
    assert all(row["matched_batch_ids"] == ["TODO_batch_id_1", "TODO_batch_id_2", "TODO_batch_id_3"] for row in template["evidence_rows"])
    assert merge_plan["merge_strategy"] == "replace_rows_by_response_row_id"
    assert merge_plan["focused_replacement_row_count"] == 6
    assert merge_plan["remaining_full_response_row_count"] == 27
    assert kit["can_replace_full_field_activation_response"] is False
    assert kit["can_route_to_agent51_field_proxy_holdout"] is False
    assert kit["can_relax_agent49_catalyst_uncertainty_block"] is False
    assert kit["can_write_to_actuator"] is False
    assert kit["can_write_to_release_gate"] is False


def test_catalyst_submission_kit_blocks_when_full_template_lacks_target_rows() -> None:
    full_template = _full_response_template()
    full_template["evidence_rows"] = [
        row for row in full_template["evidence_rows"] if row["response_row_id"] != "catalyst_activity_04"
    ]

    kit = build_catalyst_response_submission_kit(
        observation_response_bridge=_bridge(),
        full_response_template=full_template,
        catalyst_evidence_response_gate=_focused_gate(),
    )

    assert kit["kit_status"] == "catalyst_response_submission_kit_blocked_by_missing_full_template_rows"
    assert kit["missing_full_template_row_ids"] == ["catalyst_activity_04"]
    assert kit["can_route_to_catalyst_evidence_response_gate"] is False


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
        "r2_fv4_requirement": {"minimum_matched_batch_count": 3},
        "priority_response_rows": [
            {
                "response_row_id": row_id,
                "hidden_state": "catalyst_activity",
                "required_evidence": evidence,
                "evidence_channel": "R7_REAL_FIELD_PACKAGE",
                "table_name": evidence.split(".", 1)[0],
                "field_name": evidence.split(".", 1)[1],
                "observation_role": role,
                "priority": "P1" if rank == 1 else "P2",
                "priority_rank": rank,
            }
            for row_id, evidence, role, rank in rows
        ],
    }


def _full_response_template() -> dict[str, object]:
    bridge_rows = _bridge()["priority_response_rows"]
    catalyst_rows = [
        {
            "response_row_id": row["response_row_id"],
            "hidden_state": row["hidden_state"],
            "required_evidence": row["required_evidence"],
            "evidence_channel": row["evidence_channel"],
            "table_name": row["table_name"],
            "field_name": row["field_name"],
            "data_origin": "TODO_field",
            "batch_id": "TODO_batch_id",
            "timestamp": "TODO_timestamp_or_not_applicable",
            "node_id": "TODO_node_id_or_not_applicable",
            "sensor_id": "TODO_sensor_id_or_not_applicable",
            "evidence_value_reference": "TODO_table_column_or_file_reference",
            "offline_method_id": "TODO_method_id_or_not_applicable",
            "detection_limit": "TODO_detection_limit_or_not_applicable",
            "chain_of_custody_id": "TODO_chain_of_custody_id",
            "operator_id": "TODO_operator_id",
            "no_write_boundary_confirmed": "TODO_true",
            "review_notes": "TODO_explain_real_field_source_and_alignment",
        }
        for row in bridge_rows
    ]
    filler_rows = [
        {
            "response_row_id": f"other_state_{index:02d}",
            "hidden_state": "other_state",
            "required_evidence": f"other_table.other_field_{index}",
        }
        for index in range(27)
    ]
    return {
        "template_id": "R8u98_field_activation_evidence_response_template",
        "package_type": "field_activation_evidence_response",
        "source_interface_id": "R8u97_field_activation_matrix_interface",
        "required_response_row_count": 33,
        "evidence_rows": catalyst_rows + filler_rows,
    }


def _focused_gate() -> dict[str, object]:
    return {
        "gate_id": "R8u110_catalyst_evidence_response_gate",
        "gate_status": "catalyst_evidence_response_gate_waiting_for_FIELD_ACTIVATION_RESPONSE_PATH",
    }

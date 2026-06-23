from water_ai.observation_response_bridge import build_observation_response_bridge


def test_observation_response_bridge_prioritizes_catalyst_response_rows() -> None:
    bridge = build_observation_response_bridge(
        observation_contract_metrics=_observation_contract_metrics(),
        response_template=_response_template(),
        response_submission_packet=_submission_packet(),
        catalyst_holdout_summary=_catalyst_holdout_summary(),
        soft_sensor_matrix_metrics=_soft_sensor_matrix_metrics(),
    )

    assert bridge["bridge_status"] == "observation_response_bridge_ready_for_priority_field_response_fill"
    assert bridge["primary_target_hidden_state"] == "catalyst_activity"
    assert bridge["response_row_count"] == 6
    assert bridge["mapped_response_row_count"] == 6
    assert bridge["required_role_coverage_rate"] == 1.0
    assert bridge["missing_required_roles"] == []
    assert bridge["r2_fv4_requirement"]["minimum_matched_batch_count"] == 3
    assert bridge["can_route_to_agent51_field_proxy_holdout"] is False
    assert bridge["can_relax_agent49_catalyst_uncertainty_block"] is False
    assert bridge["can_write_to_actuator"] is False
    assert bridge["can_write_to_release_gate"] is False
    row_ids = {row["response_row_id"] for row in bridge["priority_response_rows"]}
    assert row_ids == {
        "catalyst_activity_01",
        "catalyst_activity_02",
        "catalyst_activity_03",
        "catalyst_activity_04",
        "catalyst_activity_05",
        "catalyst_activity_06",
    }
    roles = {row["observation_role"] for row in bridge["priority_response_rows"]}
    assert "pressure_headloss_proxy" in roles
    assert "catalyst_activity_label" in roles
    assert "regeneration_event" in roles
    assert "hydraulic_normalizer" in roles
    assert "does not validate catalyst activity" in bridge["no_write_boundary"]


def test_observation_response_bridge_routes_only_after_agent51_holdout_ready() -> None:
    summary = _catalyst_holdout_summary()
    summary["ready_for_agent51_validation"] = True
    summary["field_validation_pass"] = True
    summary["scoreable_batch_count"] = 3
    summary["missing_required_signals"] = []
    summary["can_relax_agent49_catalyst_uncertainty_block"] = True
    packet = _submission_packet()
    packet["packet_status"] = "field_activation_response_submission_packet_response_ready_for_package_assembly"

    bridge = build_observation_response_bridge(
        observation_contract_metrics=_observation_contract_metrics(),
        response_template=_response_template(),
        response_submission_packet=packet,
        catalyst_holdout_summary=summary,
        soft_sensor_matrix_metrics=_soft_sensor_matrix_metrics(),
    )

    assert bridge["bridge_status"] == "observation_response_bridge_ready_for_agent51_field_proxy_holdout"
    assert bridge["can_route_to_agent51_field_proxy_holdout"] is True
    assert bridge["can_relax_agent49_catalyst_uncertainty_block"] is True
    assert bridge["can_resume_model_chain"] is False
    assert bridge["can_write_to_actuator"] is False
    assert bridge["can_write_to_release_gate"] is False


def test_observation_response_bridge_blocks_when_target_rows_are_missing() -> None:
    template = _response_template()
    template["evidence_rows"] = [
        row for row in template["evidence_rows"] if row["hidden_state"] != "catalyst_activity"
    ]

    bridge = build_observation_response_bridge(
        observation_contract_metrics=_observation_contract_metrics(),
        response_template=template,
        response_submission_packet=_submission_packet(),
        catalyst_holdout_summary=_catalyst_holdout_summary(),
        soft_sensor_matrix_metrics=_soft_sensor_matrix_metrics(),
    )

    assert bridge["bridge_status"] == "observation_response_bridge_blocked_by_missing_target_response_rows"
    assert bridge["response_row_count"] == 0
    assert bridge["required_role_coverage_rate"] == 0.0
    assert "pressure_headloss_proxy" in bridge["missing_required_roles"]
    assert bridge["can_route_to_agent51_field_proxy_holdout"] is False


def _observation_contract_metrics() -> dict[str, object]:
    return {
        "readiness": {
            "observation_contract_status": "synthetic_observation_contract_ready_needs_field_topology_proxy_labels_and_missingness",
            "agent48_hidden_state_hard_unresolved": ["catalyst_activity"],
        },
        "field_validation_requirements": [
            {
                "requirement_id": "R2_FV4_agent48_hidden_state_requirement_patch",
                "needed_for": "resolving Agent48 hard unresolved hidden-state sensing needs",
                "required_tables": [
                    "node_modality_sensor_timeseries",
                    "offline_lab_results",
                    "campaign_operation_log",
                    "site_topology_or_bed_geometry",
                ],
                "hard_unresolved_hidden_states": ["catalyst_activity"],
                "minimum_matched_batch_count": 3,
                "required_signals_or_fields": [
                    "pressure_drop_kPa_or_headloss_proxy",
                    "catalyst_activity_label",
                    "regeneration_event",
                    "nominal_HRT_min",
                ],
                "pressure_headloss_candidate_ids": [
                    "N3_catalyst_bed:pressure_drop_kPa",
                    "N3_catalyst_bed:headloss_kPa_per_m",
                    "N3_catalyst_bed:flow_normalized_pressure_residual",
                ],
            }
        ],
    }


def _response_template() -> dict[str, object]:
    return {
        "template_id": "R8u98_field_activation_evidence_response_template",
        "evidence_rows": [
            _row("catalyst_activity_01", "node_modality_sensor_timeseries", "N3_catalyst_bed_outlet:UV254_abs"),
            _row("catalyst_activity_02", "node_modality_sensor_timeseries", "N3_catalyst_bed_outlet:ORP_mV"),
            _row("catalyst_activity_03", "node_modality_sensor_timeseries", "N3_catalyst_bed:pressure_drop_kPa"),
            _row("catalyst_activity_04", "offline_lab_results", "catalyst_activity"),
            _row("catalyst_activity_05", "campaign_operation_log", "regeneration_event"),
            _row("catalyst_activity_06", "site_topology_or_bed_geometry", "nominal_HRT_min"),
            {
                "response_row_id": "hydraulic_delay_01",
                "hidden_state": "hydraulic_delay",
                "required_evidence": "campaign_operation_log.hold_time_min",
                "evidence_channel": "R7_REAL_FIELD_PACKAGE",
                "table_name": "campaign_operation_log",
                "field_name": "hold_time_min",
            },
        ],
    }


def _row(response_row_id: str, table_name: str, field_name: str) -> dict[str, object]:
    return {
        "response_row_id": response_row_id,
        "hidden_state": "catalyst_activity",
        "required_evidence": f"{table_name}.{field_name}",
        "evidence_channel": "R7_REAL_FIELD_PACKAGE",
        "table_name": table_name,
        "field_name": field_name,
    }


def _submission_packet() -> dict[str, object]:
    return {
        "packet_id": "R8u108_field_activation_response_submission_packet",
        "packet_status": "field_activation_response_submission_packet_waiting_for_external_response",
        "next_operator_action": "fill_response_template_and_set_FIELD_ACTIVATION_RESPONSE_PATH",
    }


def _catalyst_holdout_summary() -> dict[str, object]:
    return {
        "field_proxy_holdout_summary_status": "field_proxy_holdout_coverage_gaps",
        "ready_for_agent51_validation": False,
        "field_validation_pass": False,
        "scoreable_batch_count": 0,
        "minimum_batch_count": 3,
        "required_node_signals": [
            "N3_catalyst_bed:pressure_drop_kPa",
            "N3_catalyst_bed_outlet:ORP_mV",
            "N3_catalyst_bed_outlet:UV254_abs",
        ],
        "missing_required_signals": [
            "N3_catalyst_bed_outlet:UV254_abs",
            "N3_catalyst_bed_outlet:ORP_mV",
            "N3_catalyst_bed:pressure_drop_kPa",
        ],
        "can_relax_agent49_catalyst_uncertainty_block": False,
    }


def _soft_sensor_matrix_metrics() -> dict[str, object]:
    return {
        "readiness": {
            "soft_sensor_matrix_status": "synthetic_layout_aware_soft_sensor_contract_ready_needs_field_missingness",
            "pressure_headloss_candidate_pool_status": "pressure_headloss_candidate_pool_ready_needs_field_topology_and_labels",
            "pressure_headloss_schema_ready": False,
            "can_use_pressure_headloss_for_field_claim": False,
        },
        "feature_contract": {
            "pressure_headloss_candidate_contract": {
                "candidate_ids": [
                    "N3_catalyst_bed:pressure_drop_kPa",
                    "N3_catalyst_bed:headloss_kPa_per_m",
                    "N3_catalyst_bed:flow_normalized_pressure_residual",
                ]
            }
        },
    }

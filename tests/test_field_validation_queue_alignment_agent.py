from water_ai.agents.field_validation_queue_alignment_agent import FieldValidationQueueAlignmentAgent


def test_field_validation_queue_alignment_maps_agent56_needs_to_tables_and_gates() -> None:
    report = FieldValidationQueueAlignmentAgent(
        field_validation_queue=_agent56_field_queue(),
        field_data_metrics=_field_data_metrics(),
        timestamped_replay_metrics=_timestamped_replay_metrics(),
        field_replay_import_metrics=_field_replay_import_metrics(),
        evidence_chain_metrics=_evidence_chain_metrics(),
    ).run([])

    readiness = report.metrics["readiness"]
    mapping = {row["field_validation_need"]: row for row in report.metrics["validation_mapping_table"]}

    assert readiness["field_validation_alignment_status"] == "field_validation_alignment_ready_needs_real_field_package"
    assert readiness["field_need_to_table_coverage"] == 1.0
    assert readiness["field_need_to_gate_coverage"] == 1.0
    assert readiness["can_write_to_actuator"] is False
    assert readiness["can_write_to_release_gate"] is False
    assert mapping["真实传感漂移记录"]["agent30_tables"] == ["sensor_timeseries"]
    assert mapping["离线放行标签"]["agent30_tables"] == ["offline_lab_results"]
    assert "detection_limit" in mapping["低浓度目标物检测限"]["optional_fields_promoted_for_claim"]["offline_lab_results"]
    assert any(issue.issue_type == "field_package_required_before_claim_upgrade" for issue in report.issues)


def test_field_validation_queue_alignment_flags_unmapped_needs() -> None:
    report = FieldValidationQueueAlignmentAgent(
        field_validation_queue=[
            {
                "field_validation_need": "未知现场证据类型",
                "supporting_entries": ["kb_unknown"],
                "required_before": "field_claim",
            }
        ]
    ).run([])

    readiness = report.metrics["readiness"]

    assert readiness["field_validation_alignment_status"] == "field_validation_alignment_incomplete"
    assert readiness["unmapped_validation_need_count"] == 1
    assert readiness["can_update_agent50_priority"] is False
    assert any(issue.issue_type == "field_validation_need_unmapped" for issue in report.issues)


def test_field_validation_queue_alignment_empty_queue_cannot_advance() -> None:
    report = FieldValidationQueueAlignmentAgent(field_validation_queue=[]).run([])

    readiness = report.metrics["readiness"]

    assert readiness["field_validation_alignment_status"] == "field_validation_alignment_empty_queue"
    assert readiness["can_update_agent50_priority"] is False
    assert any(issue.issue_type == "field_validation_queue_empty" for issue in report.issues)


def test_field_validation_queue_alignment_consumes_r4_field_requirement_patch() -> None:
    report = FieldValidationQueueAlignmentAgent(
        field_validation_queue=_agent56_field_queue(),
        field_data_metrics=_field_data_metrics(),
        timestamped_replay_metrics=_timestamped_replay_metrics(),
        field_replay_import_metrics=_field_replay_import_metrics(),
        evidence_chain_metrics=_evidence_chain_metrics(),
        control_guardrail_backpropagation_metrics=_guardrail_backpropagation_metrics(),
    ).run([])

    readiness = report.metrics["readiness"]
    coverage = report.metrics["coverage"]
    guardrail_rows = [
        row for row in report.metrics["validation_mapping_table"] if row.get("guardrail_patch_consumed")
    ]

    assert len(guardrail_rows) == 2
    assert readiness["field_requirement_patch_consumption_rate"] == 1.0
    assert readiness["guardrail_requirement_patch_count"] == 2
    assert coverage["guardrail_required_field_count"] == 12
    assert coverage["guardrail_missing_schema_field_count"] == 0
    assert coverage["guardrail_missing_schema_fields"] == []
    assert readiness["can_write_to_actuator"] is False
    assert readiness["can_write_to_release_gate"] is False
    assert not any(issue.issue_type == "guardrail_field_schema_extension_required" for issue in report.issues)


def _agent56_field_queue() -> list[dict[str, object]]:
    return [
        {
            "field_validation_need": "真实传感漂移记录",
            "supporting_entries": ["kb_sensor_limited_release_evidence"],
            "required_before": "actuator_or_release_gate_claim",
        },
        {
            "field_validation_need": "离线放行标签",
            "supporting_entries": ["kb_sensor_limited_release_evidence"],
            "required_before": "actuator_or_release_gate_claim",
        },
        {
            "field_validation_need": "低浓度目标物检测限",
            "supporting_entries": ["kb_sensor_limited_release_evidence"],
            "required_before": "actuator_or_release_gate_claim",
        },
    ]


def _field_data_metrics() -> dict[str, object]:
    return {
        "readiness": {
            "interface_status": "template_ready_not_field_validated",
            "data_origin": "synthetic",
        }
    }


def _timestamped_replay_metrics() -> dict[str, object]:
    return {
        "readiness": {
            "timestamped_replay_status": "synthetic_timestamp_schema_ready_needs_field_replay",
            "field_replay_required": True,
            "can_calibrate_fast_proxy": False,
        }
    }


def _field_replay_import_metrics() -> dict[str, object]:
    return {
        "readiness": {
            "field_replay_import_status": "field_replay_import_blocked_non_field_origin",
            "can_pass_to_timestamped_replay": False,
        }
    }


def _evidence_chain_metrics() -> dict[str, object]:
    return {
        "readiness": {
            "field_replay_evidence_chain_status": "field_replay_evidence_chain_blocked_at_import",
            "can_emit_protective_writeback_candidate": False,
            "can_write_to_release_gate": False,
        }
    }


def _guardrail_backpropagation_metrics() -> dict[str, object]:
    return {
        "readiness": {
            "backpropagation_ready": True,
            "field_ready": False,
        },
        "field_requirement_patch": [
            {
                "scenario": "catalyst_uncertain_low_proxy",
                "required_fields": [
                    "proxy_holdout_label",
                    "pressure_drop_kPa",
                    "regeneration_event",
                    "operator_override",
                    "N3_catalyst_bed_outlet:UV254_abs",
                    "N3_catalyst_bed_outlet:turbidity_NTU",
                ],
                "claim_boundary": (
                    "synthetic guardrail resolved false-positive catalyst protection; "
                    "field proxy labels are required before catalyst-control claim upgrade."
                ),
            },
            {
                "scenario": "hydraulic_delay_violation",
                "required_fields": [
                    "tank_storage_margin",
                    "actuator_latency_p90",
                    "pump_valve_result",
                    "flow_Lmin",
                    "hold_time_min",
                    "recycle_ratio",
                ],
                "claim_boundary": (
                    "synthetic guardrail resolved high-regret recycle action; "
                    "field hydraulic replay is required before recycle-control claim upgrade."
                ),
            },
        ],
    }

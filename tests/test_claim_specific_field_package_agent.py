from water_ai.agents.claim_specific_field_package_agent import ClaimSpecificFieldPackageAgent
from water_ai.agents.field_validation_queue_alignment_agent import FieldValidationQueueAlignmentAgent


def test_claim_specific_field_package_promotes_optional_fields_to_claim_required() -> None:
    report = ClaimSpecificFieldPackageAgent(
        validation_mapping_table=_validation_mapping_table(),
        kg_reasoning_metrics=_kg_reasoning_metrics(),
        field_package_status=_field_package_status(),
    ).run([])

    readiness = report.metrics["readiness"]
    matrix = {row["field_validation_need"]: row for row in report.metrics["minimal_field_package_matrix"]}

    assert readiness["claim_specific_package_status"] == "claim_specific_package_ready_needs_real_data_and_source_basis_detail"
    assert readiness["claim_specific_required_field_coverage"] == 1.0
    assert readiness["minimal_field_package_field_pass_rate"] == 0.0
    assert readiness["source_basis_completion_rate"] == 0.45
    assert "detection_limit" in matrix["低浓度目标物检测限"]["claim_specific_required_fields"]["offline_lab_results"]
    assert "source_basis_needs_citation_or_parameter_detail" in matrix["离线放行标签"]["claim_upgrade_blocked_by"]
    assert readiness["can_write_to_actuator"] is False
    assert readiness["can_write_to_release_gate"] is False


def test_claim_specific_field_package_requires_mapping_table() -> None:
    report = ClaimSpecificFieldPackageAgent(validation_mapping_table=[]).run([])

    readiness = report.metrics["readiness"]

    assert readiness["claim_specific_package_status"] == "claim_specific_package_missing_mapping_table"
    assert readiness["can_update_agent50_priority"] is False
    assert any(issue.issue_type == "validation_mapping_table_required" for issue in report.issues)


def test_claim_specific_field_package_consumes_source_basis_detail_library() -> None:
    kg_metrics = _kg_reasoning_metrics()
    kg_metrics["source_basis_detail_library"] = _source_basis_detail_library()
    report = ClaimSpecificFieldPackageAgent(
        validation_mapping_table=_validation_mapping_table(),
        kg_reasoning_metrics=kg_metrics,
        field_package_status=_field_package_status(),
    ).run([])

    readiness = report.metrics["readiness"]
    source_task = report.metrics["source_basis_completion_tasks"][0]

    assert readiness["source_basis_completion_rate"] == 1.0
    assert source_task["citation_detail_complete"] is True
    assert any("doi:10." in item for item in source_task["current_source_basis"])


def test_claim_specific_field_package_retains_r4_guardrail_required_fields() -> None:
    alignment = FieldValidationQueueAlignmentAgent(
        control_guardrail_backpropagation_metrics=_guardrail_backpropagation_metrics()
    ).run([])
    field_package_status = {
        **alignment.metrics["field_package_status"],
        "guardrail_requirement_patch_count": alignment.metrics["coverage"]["guardrail_requirement_patch_count"],
    }
    report = ClaimSpecificFieldPackageAgent(
        validation_mapping_table=alignment.metrics["validation_mapping_table"],
        kg_reasoning_metrics=_kg_reasoning_metrics(),
        field_package_status=field_package_status,
    ).run([])

    readiness = report.metrics["readiness"]
    matrix = {row["guardrail_source_scenario"]: row for row in report.metrics["minimal_field_package_matrix"]}
    source_tasks = {
        task["entry_id"]: task for task in report.metrics["source_basis_completion_tasks"]
    }

    assert readiness["field_requirement_patch_consumption_rate"] == 1.0
    assert readiness["guardrail_package_row_count"] == 2
    assert readiness["unmet_guardrail_field_count"] == 0
    assert readiness["source_basis_completion_rate"] == 1.0
    assert readiness["can_write_to_actuator"] is False
    assert readiness["can_write_to_release_gate"] is False
    assert source_tasks["R4_control_guardrail_failure_backpropagation"]["source_basis_present"] is True
    assert source_tasks["R4_control_guardrail_failure_backpropagation"]["citation_detail_complete"] is True
    assert "_guardrail_requirement_patch" in matrix["catalyst_uncertain_low_proxy"]["claim_specific_required_fields"]
    assert matrix["catalyst_uncertain_low_proxy"]["guardrail_missing_schema_fields"] == []
    assert matrix["hydraulic_delay_violation"]["guardrail_missing_schema_fields"] == []
    assert not any(
        issue.issue_type == "guardrail_claim_package_schema_extension_required" for issue in report.issues
    )


def _validation_mapping_table() -> list[dict[str, object]]:
    return [
        {
            "need_id": "FVQ02",
            "field_validation_need": "离线放行标签",
            "need_type": "offline_release_label_for_soft_sensor_and_claim_gate",
            "supporting_entries": ["kb_sensor_limited_release_evidence"],
            "required_table_fields": {
                "offline_lab_results": [
                    "batch_id",
                    "sample_time_min",
                    "analyte",
                    "value",
                    "unit",
                    "method",
                    "qa_flag",
                ]
            },
            "optional_fields_promoted_for_claim": {
                "offline_lab_results": ["result_time_min", "detection_limit", "sample_source"]
            },
            "agent30_tables": ["offline_lab_results"],
            "agent42_replay_tables": ["offline_lab_results"],
            "agent44_metadata_fields": ["data_origin", "site_id", "campaign_id", "chain_of_custody_id"],
            "agent43_gate_ids": ["G6_1_field_origin", "G6_2_timestamp_schema_ready"],
            "validation_metrics": ["field_holdout_label_count", "soft_sensor_interval_coverage"],
        },
        {
            "need_id": "FVQ03",
            "field_validation_need": "低浓度目标物检测限",
            "need_type": "low_concentration_detection_limit_for_target_pollutants",
            "supporting_entries": ["kb_sensor_limited_release_evidence"],
            "required_table_fields": {
                "offline_lab_results": [
                    "batch_id",
                    "sample_time_min",
                    "analyte",
                    "value",
                    "unit",
                    "method",
                    "qa_flag",
                ]
            },
            "optional_fields_promoted_for_claim": {
                "offline_lab_results": ["detection_limit", "result_time_min", "sample_source", "replicate_id"]
            },
            "agent30_tables": ["offline_lab_results"],
            "agent42_replay_tables": ["offline_lab_results"],
            "agent44_metadata_fields": ["data_origin", "site_id", "campaign_id", "chain_of_custody_id"],
            "agent43_gate_ids": ["G6_1_field_origin", "G6_2_timestamp_schema_ready"],
            "validation_metrics": ["detection_limit_coverage", "qa_pass_rate"],
        },
    ]


def _kg_reasoning_metrics() -> dict[str, object]:
    return {
        "kg_reasoning": {
            "matched_entries": [
                {
                    "entry_id": "kb_sensor_limited_release_evidence",
                    "source_basis": ["low_cost_proxy_sensing", "soft_sensor_release_gate"],
                }
            ]
        }
    }


def _field_package_status() -> dict[str, object]:
    return {
        "field_replay_import_ready": False,
        "field_replay_evidence_chain_ready": False,
        "release_gate_boundary_preserved": True,
    }


def _source_basis_detail_library() -> dict[str, object]:
    return {
        "low_cost_proxy_sensing": {
            "evidence_stage": "literature_supported_method_not_field_validated",
            "citation_records": [
                {
                    "citation_key": "Schneider_2020_EST_onsite_soft_sensors",
                    "title": "Benchmarking Soft Sensors for Remote Monitoring of On-Site Wastewater Treatment Plants",
                    "doi": "10.1021/acs.est.9b07760",
                }
            ],
            "parameter_or_method_boundaries": ["field drift labels are required"],
            "failure_boundary": "not field-supported without real field holdout",
        },
        "soft_sensor_release_gate": {
            "evidence_stage": "literature_supported_validation_method_not_field_validated",
            "citation_records": [
                {
                    "citation_key": "Haimi_2013_EnvModSoft_WWTP_soft_sensors",
                    "title": "Data-derived soft-sensors for biological wastewater treatment plants: An overview",
                    "doi": "10.1016/j.envsoft.2013.05.009",
                }
            ],
            "parameter_or_method_boundaries": ["field holdout is required"],
            "failure_boundary": "not field-supported without real release labels",
        },
    }


def _guardrail_backpropagation_metrics() -> dict[str, object]:
    return {
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
        ]
    }

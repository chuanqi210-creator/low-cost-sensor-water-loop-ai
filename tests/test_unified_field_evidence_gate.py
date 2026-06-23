from copy import deepcopy

from water_ai.field_evidence_gate import UnifiedFieldEvidenceGate


def test_unified_gate_consumes_existing_gate_sources_and_builds_claim_records() -> None:
    result = _gate().build()

    assert result["readiness"]["unified_evidence_record_count"] == 2
    assert result["gate_consolidation"]["consumed_gate_source_count"] == 6
    assert result["gate_consolidation"]["gate_source_consolidation_coverage"] == 1.0
    assert result["gate_consolidation"]["duplicate_gate_cluster_resolved_as_interface"] is True


def test_unified_gate_preserves_synthetic_and_release_boundaries() -> None:
    result = _gate().build()

    assert result["readiness"]["synthetic_boundary_preserved"] is True
    assert result["readiness"]["can_emit_field_claim_upgrade"] is False
    assert result["readiness"]["can_write_to_release_gate"] is False
    assert result["readiness"]["can_write_to_actuator"] is False
    assert "release_gate_policy" in result["writeback_policy"]["blocked_writeback"]
    assert "actuator_policy" in result["writeback_policy"]["blocked_writeback"]


def test_unified_gate_completes_literature_traceability_without_field_upgrade() -> None:
    result = _gate().build()

    assert result["readiness"]["source_basis_completion_rate"] == 0.45
    assert result["readiness"]["citation_detail_completion_rate"] == 1.0
    assert result["readiness"]["source_basis_parameter_boundary_coverage"] == 1.0
    assert result["readiness"]["effective_literature_traceability"] == 1.0
    assert result["source_basis_detail_status"]["field_supported_edge_ratio"] == 0.0
    assert result["next_refactor_action"]["action_id"] == "R2_agent48_51_54_observation_contract_merge"
    assert result["source_basis_detail_tasks"][0]["routed_to_unified_gate"] is True
    assert "source_basis_literature_detail_complete_not_field_supported" in result["unified_evidence_records"][0]["claim_upgrade_blocked_by"]
    assert "source_basis_needs_citation_or_parameter_detail" not in result["unified_evidence_records"][0]["claim_upgrade_blocked_by"]


def test_unified_gate_source_basis_detail_library_has_required_scientific_boundaries() -> None:
    result = _gate().build()
    library = result["source_basis_detail_library"]

    assert set(library) == {"low_cost_proxy_sensing", "soft_sensor_release_gate"}
    for detail in library.values():
        assert detail["citation_records"]
        assert detail["reality_mapping"]
        assert detail["applicable_conditions"]
        assert detail["parameter_or_method_boundaries"]
        assert detail["required_field_validation"]
        assert detail["failure_boundary"]
        assert all(record["source_url"] and record["citation_key"] for record in detail["citation_records"])


def test_unified_gate_accepts_expanded_source_basis_strings_from_agent59() -> None:
    gate = _gate()
    claim_metrics = deepcopy(gate.claim_specific_package_metrics)
    claim_metrics["minimal_field_package_matrix"][0]["source_basis_status"]["source_basis"] = [
        "source_basis_id:low_cost_proxy_sensing; evidence_stage:literature_supported_method_not_field_validated",
        "citation:Schneider_2020_EST_onsite_soft_sensors; doi:10.1021/acs.est.9b07760",
    ]
    claim_metrics["minimal_field_package_matrix"][1]["source_basis_status"]["source_basis"] = [
        "source_basis_id:soft_sensor_release_gate; evidence_stage:literature_supported_validation_method_not_field_validated",
        "citation:Haimi_2013_EnvModSoft_WWTP_soft_sensors; doi:10.1016/j.envsoft.2013.05.009",
    ]

    result = UnifiedFieldEvidenceGate(
        field_validation_alignment_metrics=gate.field_validation_alignment_metrics,
        claim_specific_package_metrics=claim_metrics,
        field_replay_import_metrics=gate.field_replay_import_metrics,
        field_replay_gate_metrics=gate.field_replay_gate_metrics,
        field_replay_evidence_chain_metrics=gate.field_replay_evidence_chain_metrics,
        soft_sensor_field_holdout_gate_metrics=gate.soft_sensor_field_holdout_gate_metrics,
    ).build()

    status = result["source_basis_detail_status"]

    assert status["source_basis_ids"] == ["low_cost_proxy_sensing", "soft_sensor_release_gate"]
    assert status["citation_detail_completion_rate"] == 1.0
    assert status["parameter_boundary_coverage"] == 1.0


def test_unified_gate_keeps_field_import_and_replay_blockers_explicit() -> None:
    result = _gate().build()
    record = result["unified_evidence_records"][0]

    assert record["field_import_status"]["data_origin"] == "synthetic"
    assert record["field_import_status"]["import_ready"] is False
    assert "field_origin_not_verified" in record["claim_upgrade_blocked_by"]
    assert "field_replay_import_not_passed" in record["claim_upgrade_blocked_by"]
    assert "failed_replay_gate:G6_1_field_origin" in record["claim_upgrade_blocked_by"]
    assert record["evidence_stage"] == "synthetic_baseline_field_validation_required"


def test_unified_gate_exposes_claim_basis_promotion_gate_for_blocked_records() -> None:
    result = _gate().build()
    promotion_gate = result["claim_basis_promotion_gate"]

    assert promotion_gate["gate_status"] == "claim_basis_promotion_blocked_until_field_validation"
    assert promotion_gate["promotion_decision_count"] == 2
    assert promotion_gate["blocked_promotion_count"] == 2
    assert promotion_gate["ready_promotion_count"] == 0
    assert promotion_gate["can_emit_field_claim_upgrade"] is False
    assert promotion_gate["can_write_to_actuator"] is False
    assert promotion_gate["can_write_to_release_gate"] is False

    first_row = promotion_gate["promotion_rows"][0]
    assert first_row["need_id"] == "FVQ01"
    assert first_row["promotion_status"] == "blocked"
    assert first_row["allowed_promotion_level"] == "no_field_claim_upgrade"
    assert first_row["current_basis"]["source_basis_traceability"] == "literature_detail_complete"
    assert first_row["current_basis"]["field_import"] == "not_passed"
    assert "synthetic_rows_as_field_evidence" in first_row["not_current_basis"]
    assert "field_origin_not_verified" in first_row["blocked_by"]
    assert first_row["next_required_gate"] == "import_real_field_package_then_replay_holdout_and_human_review"


def test_unified_gate_allows_only_field_supported_candidate_after_real_field_chain_passes() -> None:
    gate = _field_ready_gate()
    result = gate.build()
    promotion_gate = result["claim_basis_promotion_gate"]

    assert result["readiness"]["can_emit_field_claim_upgrade"] is True
    assert promotion_gate["gate_status"] == "claim_basis_promotion_ready_for_field_supported_candidate_review"
    assert promotion_gate["promotion_decision_count"] == 2
    assert promotion_gate["ready_promotion_count"] == 2
    assert promotion_gate["blocked_promotion_count"] == 0
    assert promotion_gate["can_emit_field_claim_upgrade"] is True
    assert promotion_gate["can_write_to_actuator"] is False
    assert promotion_gate["can_write_to_release_gate"] is False

    first_row = promotion_gate["promotion_rows"][0]
    assert first_row["promotion_status"] == "field_supported_candidate_ready_for_human_review"
    assert first_row["allowed_promotion_level"] == "field_supported_claim_candidate_not_release_or_actuator"
    assert first_row["requires_human_review"] is True
    assert first_row["current_basis"]["field_import"] == "passed"
    assert first_row["current_basis"]["replay_evidence_chain"] == "passed"
    assert first_row["current_basis"]["soft_sensor_holdout"] == "passed"
    assert "actuator_policy" in first_row["not_current_basis"]
    assert "release_gate_policy" in first_row["not_current_basis"]


def _gate() -> UnifiedFieldEvidenceGate:
    return UnifiedFieldEvidenceGate(
        field_validation_alignment_metrics={
            "validation_mapping_table": [
                {
                    "need_id": "FVQ01",
                    "field_validation_need": "真实传感漂移记录",
                    "need_type": "sensor_drift_and_low_cost_signal_validity",
                    "supporting_entries": ["kb_sensor_limited_release_evidence"],
                    "required_table_fields": {"sensor_timeseries": ["batch_id", "timestamp_min"]},
                    "agent44_metadata_fields": ["data_origin", "site_id"],
                    "agent43_gate_ids": ["G6_1_field_origin", "G6_2_timestamp_schema_ready"],
                    "validation_metrics": ["sensor_drift_rate"],
                },
                {
                    "need_id": "FVQ02",
                    "field_validation_need": "离线放行标签",
                    "need_type": "offline_release_label_for_soft_sensor_and_claim_gate",
                    "supporting_entries": ["kb_sensor_limited_release_evidence"],
                    "required_table_fields": {"offline_lab_results": ["batch_id", "value"]},
                    "agent44_metadata_fields": ["data_origin", "site_id"],
                    "agent43_gate_ids": ["G6_1_field_origin", "G6_3_batch_linkage_complete"],
                    "validation_metrics": ["field_holdout_label_count"],
                },
            ]
        },
        claim_specific_package_metrics={
            "minimal_field_package_matrix": [
                {
                    "need_id": "FVQ01",
                    "supporting_entries": ["kb_sensor_limited_release_evidence"],
                    "claim_specific_required_fields": {"sensor_timeseries": ["batch_id", "timestamp_min"]},
                    "metadata_required_fields": ["data_origin", "site_id"],
                    "replay_gate_ids": ["G6_1_field_origin"],
                    "validation_metrics": ["sensor_drift_rate"],
                    "acceptance_artifacts": ["metadata.json", "sensor_timeseries.csv"],
                    "source_basis_status": {
                        "source_basis": ["low_cost_proxy_sensing"],
                        "source_basis_present": True,
                        "citation_detail_complete": False,
                    },
                    "claim_upgrade_blocked_by": [
                        "real_field_package_not_imported",
                        "source_basis_needs_citation_or_parameter_detail",
                    ],
                },
                {
                    "need_id": "FVQ02",
                    "supporting_entries": ["kb_sensor_limited_release_evidence"],
                    "claim_specific_required_fields": {"offline_lab_results": ["batch_id", "value"]},
                    "metadata_required_fields": ["data_origin", "site_id"],
                    "replay_gate_ids": ["G6_1_field_origin"],
                    "validation_metrics": ["field_holdout_label_count"],
                    "acceptance_artifacts": ["metadata.json", "offline_lab_results.csv"],
                    "source_basis_status": {
                        "source_basis": ["soft_sensor_release_gate"],
                        "source_basis_present": True,
                        "citation_detail_complete": False,
                    },
                    "claim_upgrade_blocked_by": ["real_field_package_not_imported"],
                },
            ],
            "source_basis_completion_tasks": [
                {
                    "entry_id": "kb_sensor_limited_release_evidence",
                    "current_source_basis": ["low_cost_proxy_sensing"],
                    "blocks_claim_upgrade": True,
                }
            ],
            "readiness": {"source_basis_completion_rate": 0.45},
        },
        field_replay_import_metrics={
            "metadata_audit": {"data_origin": "synthetic", "origin_ready": False},
            "readiness": {
                "field_replay_import_status": "field_replay_import_blocked_non_field_origin",
                "can_pass_to_timestamped_replay": False,
                "accepted_table_count": 4,
                "total_table_count": 4,
            },
        },
        field_replay_gate_metrics={
            "readiness": {
                "field_replay_gate_status": "synthetic_replay_gate_blocked",
                "accepted_gate_count": 7,
                "total_gate_count": 8,
                "failed_gate_ids": ["G6_1_field_origin"],
                "can_write_to_protective_control": False,
                "can_write_to_release_gate": False,
            }
        },
        field_replay_evidence_chain_metrics={
            "readiness": {
                "field_replay_evidence_chain_status": "field_replay_evidence_chain_blocked_at_import",
                "import_ready": False,
                "timestamped_replay_ready": False,
                "g6_ready": False,
                "can_emit_protective_writeback_candidate": False,
                "can_write_to_release_gate": False,
            }
        },
        soft_sensor_field_holdout_gate_metrics={
            "readiness": {
                "soft_sensor_field_holdout_gate_status": "soft_sensor_release_gate_blocked_non_field_holdout",
                "passed_check_count": 5,
                "total_check_count": 7,
                "failed_check_ids": ["SFG0_field_holdout_origin"],
                "can_write_to_release_gate": False,
            }
        },
    )


def _field_ready_gate() -> UnifiedFieldEvidenceGate:
    gate = _gate()
    claim_metrics = deepcopy(gate.claim_specific_package_metrics)
    for row in claim_metrics["minimal_field_package_matrix"]:
        row["claim_upgrade_blocked_by"] = []
        row["source_basis_status"]["citation_detail_complete"] = True

    return UnifiedFieldEvidenceGate(
        field_validation_alignment_metrics=gate.field_validation_alignment_metrics,
        claim_specific_package_metrics=claim_metrics,
        field_replay_import_metrics={
            "metadata_audit": {"data_origin": "field", "origin_ready": True},
            "readiness": {
                "field_replay_import_status": "field_replay_import_ready",
                "can_pass_to_timestamped_replay": True,
                "accepted_table_count": 4,
                "total_table_count": 4,
            },
        },
        field_replay_gate_metrics={
            "readiness": {
                "field_replay_gate_status": "field_replay_gate_passed",
                "accepted_gate_count": 8,
                "total_gate_count": 8,
                "failed_gate_ids": [],
                "can_write_to_protective_control": True,
                "can_write_to_release_gate": False,
            }
        },
        field_replay_evidence_chain_metrics={
            "readiness": {
                "field_replay_evidence_chain_status": "field_replay_evidence_chain_passed",
                "import_ready": True,
                "timestamped_replay_ready": True,
                "g6_ready": True,
                "can_emit_protective_writeback_candidate": True,
                "can_write_to_release_gate": False,
            }
        },
        soft_sensor_field_holdout_gate_metrics={
            "readiness": {
                "soft_sensor_field_holdout_gate_status": "soft_sensor_field_holdout_gate_passed",
                "passed_check_count": 7,
                "total_check_count": 7,
                "failed_check_ids": [],
                "can_write_to_release_gate": True,
            }
        },
    )

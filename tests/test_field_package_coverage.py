import csv
import json
from pathlib import Path

from water_ai.agents.field_replay_import_agent import write_field_replay_package_template
from water_ai.field_package_coverage import assess_field_package_coverage


def test_field_package_coverage_blocks_before_import_for_template(tmp_path: Path) -> None:
    package_dir = tmp_path / "template"
    write_field_replay_package_template(package_dir)

    result = assess_field_package_coverage(package_dir, claim_specific_package_metrics=_claim_metrics())

    readiness = result["readiness"]
    patch_plan = result["patch_plan"]
    assert readiness["field_package_coverage_status"] == "field_package_coverage_blocked_before_import"
    assert patch_plan["patch_plan_status"] == "patch_plan_blocked_at_import_preflight"
    assert patch_plan["next_blocking_stage"] == "R7a_import_preflight"
    assert any(item["item_id"] == "R7A_METADATA_PLACEHOLDERS" for item in patch_plan["items"])
    assert any(item["action"] == "add_real_timestamped_rows" for item in patch_plan["items"])
    assert readiness["field_evidence_sufficiency_status"] == "field_evidence_sufficiency_blocked_before_import"
    assert readiness["can_route_to_agent42_smoke_replay"] is False
    assert readiness["can_route_to_field_holdout"] is False
    assert readiness["can_route_to_human_review_candidate"] is False
    assert readiness["no_write_boundary_pass"] is True
    assert readiness["can_write_to_actuator"] is False
    assert readiness["can_write_to_release_gate"] is False


def test_field_package_coverage_reports_claim_specific_missing_fields(tmp_path: Path) -> None:
    package_dir = tmp_path / "minimal_replay_package"
    _write_package(package_dir, include_claim_fields=False, include_weak_targets=True)

    result = assess_field_package_coverage(package_dir, claim_specific_package_metrics=_claim_metrics())

    readiness = result["readiness"]
    patch_plan = result["patch_plan"]
    assert readiness["field_package_coverage_status"] == "field_package_claim_specific_coverage_gaps"
    assert readiness["claim_specific_coverage_rate"] == 0.0
    assert result["claim_coverage_audit"][0]["claim_upgrade_blocked_by"] == ["claim_required_headers_missing"]
    assert patch_plan["patch_plan_status"] == "patch_plan_requires_claim_specific_fields"
    table_item = next(item for item in patch_plan["items"] if item["item_id"].startswith("R7G_TABLE"))
    assert table_item["target_table"] == "offline_lab_results"
    assert "detection_limit" in table_item["fields_to_add"]


def test_field_package_coverage_passes_claim_and_soft_holdout_fields(tmp_path: Path) -> None:
    package_dir = tmp_path / "full_package"
    _write_package(package_dir, include_claim_fields=True, include_weak_targets=True)

    result = assess_field_package_coverage(package_dir, claim_specific_package_metrics=_claim_metrics())

    readiness = result["readiness"]
    patch_plan = result["patch_plan"]
    assert readiness["field_package_coverage_status"] == "field_package_coverage_ready_for_replay_and_holdout"
    assert readiness["minimum_replay_contract_status"] == "minimum_replay_contract_ready_for_agent42_smoke_test"
    assert readiness["minimum_common_batch_count"] == 3
    assert readiness["minimum_valid_matched_batch_count"] == 3
    assert readiness["minimum_valid_operation_action_count"] == 3
    assert readiness["minimum_invalid_operation_action_count"] == 0
    assert readiness["minimum_valid_lab_result_count"] == 6
    assert readiness["minimum_invalid_lab_result_count"] == 0
    assert readiness["minimum_valid_proxy_label_count"] == 3
    assert readiness["minimum_invalid_proxy_label_count"] == 0
    assert readiness["minimum_pressure_headloss_event_count"] == 3
    assert readiness["minimum_valid_pressure_headloss_event_count"] == 3
    assert readiness["minimum_invalid_pressure_headloss_event_count"] == 0
    assert readiness["minimum_valid_pressure_headloss_batch_count"] == 3
    assert readiness["claim_specific_coverage_rate"] == 1.0
    assert readiness["soft_holdout_coverage_pass"] is True
    assert readiness["field_evidence_sufficiency_status"] == (
        "field_evidence_sufficiency_smoke_ready_needs_calibration_event_volume"
    )
    assert readiness["field_evidence_smoke_pass"] is True
    assert readiness["field_evidence_calibration_volume_pass"] is False
    assert readiness["can_route_to_agent42_smoke_replay"] is True
    assert readiness["can_route_to_field_holdout"] is True
    assert readiness["can_route_to_human_review_candidate"] is False
    assert readiness["field_supported_claim_upgrade_ready"] is False
    assert readiness["control_candidate_ready"] is False
    assert readiness["release_gate_candidate_ready"] is False
    assert readiness["no_write_boundary_pass"] is True
    assert patch_plan["patch_plan_status"] == "patch_plan_ready_for_replay_and_holdout"
    assert patch_plan["item_count"] == 0


def test_field_package_coverage_sufficiency_gate_routes_review_candidate_without_writeback(
    tmp_path: Path,
) -> None:
    package_dir = tmp_path / "calibration_volume_package"
    _write_package(
        package_dir,
        include_claim_fields=True,
        include_weak_targets=True,
        include_catalyst_proxy_holdout=True,
        batch_count=12,
    )

    result = assess_field_package_coverage(
        package_dir,
        claim_specific_package_metrics=_claim_metrics(),
        catalyst_proxy_metrics=_catalyst_proxy_metrics(),
    )

    readiness = result["readiness"]
    sufficiency = result["field_evidence_sufficiency_gate"]

    assert readiness["field_package_coverage_status"] == "field_package_coverage_ready_for_replay_and_holdout"
    assert readiness["field_evidence_sufficiency_status"] == (
        "field_evidence_sufficiency_ready_for_replay_holdout_and_human_review_queue"
    )
    assert readiness["field_evidence_smoke_pass"] is True
    assert readiness["field_evidence_calibration_volume_pass"] is True
    assert readiness["field_evidence_sufficiency_score"] == 1.0
    assert readiness["can_route_to_agent42_smoke_replay"] is True
    assert readiness["can_route_to_field_holdout"] is True
    assert readiness["can_route_to_human_review_candidate"] is True
    assert readiness["field_supported_claim_upgrade_ready"] is False
    assert readiness["control_candidate_ready"] is False
    assert readiness["release_gate_candidate_ready"] is False
    assert readiness["can_write_to_actuator"] is False
    assert readiness["can_write_to_release_gate"] is False
    assert sufficiency["blocking_reasons"] == []
    assert sufficiency["no_write_boundary"]["can_write_to_actuator"] is False
    assert sufficiency["no_write_boundary"]["can_write_to_release_gate"] is False


def test_field_package_coverage_requires_minimum_replay_contract_when_batches_are_too_sparse(tmp_path: Path) -> None:
    package_dir = tmp_path / "one_batch_package"
    _write_package(package_dir, include_claim_fields=True, include_weak_targets=True, batch_count=1)

    result = assess_field_package_coverage(package_dir, claim_specific_package_metrics=_claim_metrics())

    readiness = result["readiness"]
    patch_plan = result["patch_plan"]
    assert readiness["field_package_coverage_status"] == "field_package_coverage_ready_for_replay_and_holdout"
    assert readiness["minimum_replay_contract_status"] == "minimum_replay_contract_batch_linkage_gaps"
    assert patch_plan["patch_plan_status"] == "patch_plan_requires_minimum_replay_contract"
    assert patch_plan["next_blocking_stage"] == "R7i_minimum_replay_contract_patch"
    assert patch_plan["items"][0]["item_id"] == "R7I_MATCHED_BATCH_GROUPS"


def test_field_package_coverage_requires_time_order_patch_before_replay(tmp_path: Path) -> None:
    package_dir = tmp_path / "invalid_time_order_package"
    _write_package(package_dir, include_claim_fields=True, include_weak_targets=True, invalid_time_order=True)

    result = assess_field_package_coverage(package_dir, claim_specific_package_metrics=_claim_metrics())

    readiness = result["readiness"]
    contract = result["minimum_replay_contract_audit"]
    patch_plan = result["patch_plan"]
    assert readiness["field_package_coverage_status"] == "field_package_coverage_ready_for_replay_and_holdout"
    assert readiness["minimum_replay_contract_status"] == "minimum_replay_contract_time_order_gaps"
    assert readiness["minimum_time_order_violation_count"] == 4
    assert contract["time_order_violation_count"] == 4
    assert patch_plan["patch_plan_status"] == "patch_plan_requires_minimum_replay_contract"
    assert patch_plan["items"][0]["item_id"] == "R7I_TIME_ORDER"


def test_field_package_coverage_requires_operation_action_quality_before_replay(tmp_path: Path) -> None:
    package_dir = tmp_path / "invalid_operation_quality_package"
    _write_package(package_dir, include_claim_fields=True, include_weak_targets=True, invalid_operation_quality=True)

    result = assess_field_package_coverage(package_dir, claim_specific_package_metrics=_claim_metrics())

    readiness = result["readiness"]
    contract = result["minimum_replay_contract_audit"]
    patch_plan = result["patch_plan"]
    assert readiness["field_package_coverage_status"] == "field_package_coverage_ready_for_replay_and_holdout"
    assert readiness["minimum_replay_contract_status"] == "minimum_replay_contract_operation_action_quality_gaps"
    assert readiness["minimum_valid_operation_action_count"] == 0
    assert readiness["minimum_invalid_operation_action_count"] == 3
    assert contract["operation_action_quality"]["invalid_operation_action_rows"][0]["batch_id"] == "B001"
    assert patch_plan["patch_plan_status"] == "patch_plan_requires_minimum_replay_contract"
    action_item = next(item for item in patch_plan["items"] if item["item_id"] == "R7I_OPERATION_ACTION_QUALITY")
    assert action_item["current_valid_operation_action_count"] == 0


def test_field_package_coverage_requires_lab_result_quality_before_replay(tmp_path: Path) -> None:
    package_dir = tmp_path / "invalid_lab_quality_package"
    _write_package(package_dir, include_claim_fields=True, include_weak_targets=True, invalid_lab_quality=True)

    result = assess_field_package_coverage(package_dir, claim_specific_package_metrics=_claim_metrics())

    readiness = result["readiness"]
    contract = result["minimum_replay_contract_audit"]
    patch_plan = result["patch_plan"]
    assert readiness["field_package_coverage_status"] == "field_package_coverage_ready_for_replay_and_holdout"
    assert readiness["minimum_replay_contract_status"] == "minimum_replay_contract_lab_result_quality_gaps"
    assert readiness["minimum_valid_lab_result_count"] == 0
    assert readiness["minimum_invalid_lab_result_count"] == 6
    assert contract["lab_result_quality"]["invalid_lab_result_rows"][0]["batch_id"] == "B001"
    assert patch_plan["patch_plan_status"] == "patch_plan_requires_minimum_replay_contract"
    lab_item = next(item for item in patch_plan["items"] if item["item_id"] == "R7I_LAB_RESULT_QUALITY")
    assert lab_item["current_valid_lab_result_count"] == 0


def test_field_package_coverage_requires_valid_lab_and_proxy_on_same_batches(tmp_path: Path) -> None:
    package_dir = tmp_path / "misaligned_valid_batch_package"
    _write_package(
        package_dir,
        include_claim_fields=True,
        include_weak_targets=True,
        batch_count=4,
        misaligned_valid_batches=True,
    )

    result = assess_field_package_coverage(package_dir, claim_specific_package_metrics=_claim_metrics())

    readiness = result["readiness"]
    contract = result["minimum_replay_contract_audit"]
    patch_plan = result["patch_plan"]
    assert readiness["field_package_coverage_status"] == "field_package_coverage_ready_for_replay_and_holdout"
    assert readiness["minimum_common_batch_count"] == 4
    assert readiness["minimum_valid_lab_result_count"] == 6
    assert readiness["minimum_valid_proxy_label_count"] == 3
    assert readiness["minimum_valid_matched_batch_count"] == 2
    assert readiness["minimum_replay_contract_status"] == "minimum_replay_contract_valid_matched_batch_gaps"
    assert contract["valid_matched_batch_ids_sample"] == ["B002", "B003"]
    matched_item = next(item for item in patch_plan["items"] if item["item_id"] == "R7I_VALID_MATCHED_BATCH_GROUPS")
    assert matched_item["current_valid_matched_batch_count"] == 2


def test_field_package_coverage_requires_proxy_label_quality_before_replay(tmp_path: Path) -> None:
    package_dir = tmp_path / "invalid_proxy_label_package"
    _write_package(package_dir, include_claim_fields=True, include_weak_targets=True, invalid_proxy_label=True)

    result = assess_field_package_coverage(package_dir, claim_specific_package_metrics=_claim_metrics())

    readiness = result["readiness"]
    contract = result["minimum_replay_contract_audit"]
    patch_plan = result["patch_plan"]
    assert readiness["field_package_coverage_status"] == "field_package_coverage_ready_for_replay_and_holdout"
    assert readiness["minimum_replay_contract_status"] == "minimum_replay_contract_proxy_label_quality_gaps"
    assert readiness["minimum_valid_proxy_label_count"] == 2
    assert readiness["minimum_invalid_proxy_label_count"] == 1
    assert contract["proxy_label_quality"]["invalid_proxy_label_rows"][0]["batch_id"] == "B001"
    assert patch_plan["patch_plan_status"] == "patch_plan_requires_minimum_replay_contract"
    quality_item = next(item for item in patch_plan["items"] if item["item_id"] == "R7I_PROXY_LABEL_QUALITY")
    assert quality_item["current_valid_proxy_label_count"] == 2


def test_field_package_coverage_requires_pressure_headloss_quality_before_replay(tmp_path: Path) -> None:
    package_dir = tmp_path / "invalid_pressure_headloss_package"
    _write_package(
        package_dir,
        include_claim_fields=True,
        include_weak_targets=True,
        invalid_pressure_headloss_quality=True,
    )

    result = assess_field_package_coverage(package_dir, claim_specific_package_metrics=_claim_metrics())

    readiness = result["readiness"]
    contract = result["minimum_replay_contract_audit"]
    patch_plan = result["patch_plan"]
    assert readiness["field_package_coverage_status"] == "field_package_coverage_ready_for_replay_and_holdout"
    assert readiness["minimum_replay_contract_status"] == "minimum_replay_contract_pressure_headloss_quality_gaps"
    assert readiness["minimum_valid_pressure_headloss_event_count"] == 2
    assert readiness["minimum_invalid_pressure_headloss_event_count"] == 1
    assert contract["pressure_headloss_quality"]["invalid_pressure_headloss_event_rows"][0]["batch_id"] == "B001"
    assert patch_plan["patch_plan_status"] == "patch_plan_requires_minimum_replay_contract"
    quality_item = next(item for item in patch_plan["items"] if item["item_id"] == "R7I_PRESSURE_HEADLOSS_QUALITY")
    assert quality_item["current_valid_pressure_headloss_event_count"] == 2


def test_field_package_coverage_surfaces_agent44_pressure_headloss_type_errors(tmp_path: Path) -> None:
    package_dir = tmp_path / "agent44_pressure_type_error_package"
    _write_package(
        package_dir,
        include_claim_fields=True,
        include_weak_targets=True,
        invalid_pressure_headloss_type=True,
    )

    result = assess_field_package_coverage(package_dir, claim_specific_package_metrics=_claim_metrics())

    readiness = result["readiness"]
    patch_plan = result["patch_plan"]
    assert readiness["field_package_coverage_status"] == "field_package_coverage_blocked_before_import"
    assert readiness["preflight_status"] == "field_package_preflight_agent44_blocked"
    assert patch_plan["patch_plan_status"] == "patch_plan_blocked_at_import_preflight"
    type_item = next(
        item for item in patch_plan["items"] if item["item_id"] == "R7A_AGENT44_TYPE_ERRORS_pressure_headloss_event_log"
    )
    assert type_item["target_table"] == "pressure_headloss_event_log"
    assert type_item["type_errors"][0]["field"] == "pressure_drop_kPa"


def test_field_package_coverage_flags_missing_weak_target_labels(tmp_path: Path) -> None:
    package_dir = tmp_path / "missing_weak_targets"
    _write_package(package_dir, include_claim_fields=True, include_weak_targets=False)

    result = assess_field_package_coverage(package_dir, claim_specific_package_metrics=_claim_metrics())

    readiness = result["readiness"]
    soft = result["soft_holdout_coverage_audit"]
    patch_plan = result["patch_plan"]
    assert readiness["field_package_coverage_status"] == "field_package_soft_holdout_coverage_gaps"
    assert "catalyst_activity" in soft["missing_weak_target_analytes"]
    assert "matrix_interference" in soft["missing_weak_target_analytes"]
    assert patch_plan["patch_plan_status"] == "patch_plan_requires_soft_holdout_weak_targets"
    weak_item = next(item for item in patch_plan["items"] if item["item_id"] == "R7H_WEAK_TARGET_ANALYTES")
    assert weak_item["required_analytes"] == ["catalyst_activity", "matrix_interference"]


def test_field_package_coverage_requires_agent51_catalyst_proxy_holdout(tmp_path: Path) -> None:
    package_dir = tmp_path / "missing_agent51_holdout"
    _write_package(package_dir, include_claim_fields=True, include_weak_targets=True)

    result = assess_field_package_coverage(
        package_dir,
        claim_specific_package_metrics=_claim_metrics(),
        catalyst_proxy_metrics=_catalyst_proxy_metrics(),
    )

    readiness = result["readiness"]
    audit = result["field_proxy_holdout_audit"]
    patch_plan = result["patch_plan"]
    assert readiness["field_package_coverage_status"] == "field_package_field_proxy_holdout_gaps"
    assert readiness["field_proxy_holdout_required"] is True
    assert readiness["field_proxy_holdout_coverage_pass"] is False
    assert audit["status"] == "field_proxy_holdout_coverage_gaps"
    assert "N3_catalyst_bed_outlet:UV254_abs" in audit["sensor_signal_audit"]["missing_patch_signals"]
    assert audit["sensor_signal_audit"]["source_table"] == "node_modality_sensor_timeseries"
    assert "node_modality_sensor_timeseries" in audit["missing_required_tables"]
    assert "site_topology_or_bed_geometry" in audit["missing_required_tables"]
    assert patch_plan["patch_plan_status"] == "patch_plan_requires_catalyst_proxy_field_holdout"
    item_ids = {item["item_id"] for item in patch_plan["items"]}
    assert "R7J_CATALYST_PROXY_SENSOR_SIGNALS" in item_ids
    assert "R7J_CATALYST_PROXY_HYDRAULIC_GEOMETRY" in item_ids
    assert "R7J_CATALYST_PROXY_LAB_LABELS" in item_ids
    assert "R7J_CATALYST_PROXY_REGENERATION_EVENTS" in item_ids
    assert "R7J_CATALYST_PROXY_MATCHED_BATCHES" in item_ids


def test_field_package_coverage_passes_agent51_catalyst_proxy_holdout(tmp_path: Path) -> None:
    package_dir = tmp_path / "agent51_holdout_ready"
    _write_package(
        package_dir,
        include_claim_fields=True,
        include_weak_targets=True,
        include_catalyst_proxy_holdout=True,
    )

    result = assess_field_package_coverage(
        package_dir,
        claim_specific_package_metrics=_claim_metrics(),
        catalyst_proxy_metrics=_catalyst_proxy_metrics(),
    )

    readiness = result["readiness"]
    audit = result["field_proxy_holdout_audit"]
    patch_plan = result["patch_plan"]
    assert readiness["field_package_coverage_status"] == "field_package_coverage_ready_for_replay_and_holdout"
    assert readiness["field_proxy_holdout_status"] == "field_proxy_holdout_ready_for_agent51_validation"
    assert readiness["field_proxy_holdout_coverage_pass"] is True
    assert readiness["field_proxy_holdout_matched_batch_count"] == 3
    assert audit["sensor_signal_audit"]["source_table"] == "node_modality_sensor_timeseries"
    assert audit["sensor_signal_audit"]["valid_all_signal_batch_count"] == 3
    assert audit["geometry_audit"]["geometry_coverage_pass"] is True
    assert patch_plan["patch_plan_status"] == "patch_plan_ready_for_replay_and_holdout"
    assert patch_plan["item_count"] == 0


def test_field_package_coverage_accepts_pressure_headloss_events_as_agent51_pressure_source(tmp_path: Path) -> None:
    package_dir = tmp_path / "agent51_holdout_pressure_event_source"
    _write_package(
        package_dir,
        include_claim_fields=True,
        include_weak_targets=True,
        include_catalyst_proxy_holdout=True,
        include_catalyst_proxy_node_pressure=False,
    )

    result = assess_field_package_coverage(
        package_dir,
        claim_specific_package_metrics=_claim_metrics(),
        catalyst_proxy_metrics=_catalyst_proxy_metrics(),
    )

    readiness = result["readiness"]
    audit = result["field_proxy_holdout_audit"]
    pressure_signal = audit["sensor_signal_audit"]["signal_audits"]["N3_catalyst_bed:pressure_drop_kPa"]
    patch_plan = result["patch_plan"]
    assert readiness["field_package_coverage_status"] == "field_package_coverage_ready_for_replay_and_holdout"
    assert readiness["field_proxy_holdout_status"] == "field_proxy_holdout_ready_for_agent51_validation"
    assert "N3_catalyst_bed:pressure_drop_kPa" not in audit["sensor_signal_audit"]["missing_patch_signals"]
    assert pressure_signal["node_modality_valid_batch_count"] == 0
    assert pressure_signal["pressure_headloss_event_valid_batch_count"] == 3
    assert pressure_signal["valid_batch_count"] == 3
    assert pressure_signal["accepted_evidence_sources"] == ["pressure_headloss_event_log"]
    assert audit["matched_proxy_holdout_batch_count"] == 3
    assert patch_plan["patch_plan_status"] == "patch_plan_ready_for_replay_and_holdout"


def test_field_package_coverage_turns_pressure_source_conflicts_into_field_patch_requirements(
    tmp_path: Path,
) -> None:
    package_dir = tmp_path / "agent51_holdout_pressure_source_conflict"
    _write_package(
        package_dir,
        include_claim_fields=True,
        include_weak_targets=True,
        include_catalyst_proxy_holdout=True,
        conflicting_pressure_sources=True,
    )

    result = assess_field_package_coverage(
        package_dir,
        claim_specific_package_metrics=_claim_metrics(),
        catalyst_proxy_metrics=_catalyst_proxy_metrics(),
    )

    readiness = result["readiness"]
    audit = result["field_proxy_holdout_audit"]
    sensor_audit = audit["sensor_signal_audit"]
    patch_plan = result["patch_plan"]
    conflict_item = next(
        item for item in patch_plan["items"] if item["item_id"] == "R8M_PRESSURE_SOURCE_CONFLICT_FIELD_PATCH"
    )

    assert readiness["field_package_coverage_status"] == "field_package_field_proxy_holdout_gaps"
    assert readiness["pressure_source_conflict_count"] == 1
    assert readiness["pressure_source_conflict_requires_operator_review"] is True
    assert readiness["field_package_pressure_conflict_resolution_status"] == (
        "pressure_source_conflicts_require_field_patch"
    )
    assert readiness["field_package_pressure_conflict_resolution_ready"] is False
    assert audit["conflict_requires_operator_review"] is True
    assert sensor_audit["pressure_source_conflict_count"] == 1
    assert sensor_audit["pressure_source_conflicts"][0]["batch_id"] == "B001"
    assert patch_plan["patch_plan_status"] == "patch_plan_requires_pressure_source_conflict_resolution"
    assert patch_plan["next_blocking_stage"] == "R8m_pressure_source_conflict_field_patch_requirements"
    assert conflict_item["operator_review_required"] is True
    assert conflict_item["target_tables"] == [
        "node_modality_sensor_timeseries",
        "pressure_headloss_event_log",
        "campaign_operation_log",
    ]
    assert "authoritative_pressure_source" in conflict_item["fields_to_add_or_fill"]["campaign_operation_log"]


def test_field_package_coverage_allows_resolved_pressure_source_conflict_for_agent51_holdout(
    tmp_path: Path,
) -> None:
    package_dir = tmp_path / "agent51_holdout_pressure_source_conflict_resolved"
    _write_package(
        package_dir,
        include_claim_fields=True,
        include_weak_targets=True,
        include_catalyst_proxy_holdout=True,
        conflicting_pressure_sources=True,
        resolved_pressure_source_conflict=True,
    )

    result = assess_field_package_coverage(
        package_dir,
        claim_specific_package_metrics=_claim_metrics(),
        catalyst_proxy_metrics=_catalyst_proxy_metrics(),
    )

    readiness = result["readiness"]
    audit = result["field_proxy_holdout_audit"]
    sensor_audit = audit["sensor_signal_audit"]
    pressure_signal = sensor_audit["signal_audits"]["N3_catalyst_bed:pressure_drop_kPa"]
    patch_plan = result["patch_plan"]

    assert readiness["field_package_coverage_status"] == "field_package_coverage_ready_for_replay_and_holdout"
    assert readiness["pressure_source_conflict_count"] == 1
    assert readiness["resolved_pressure_source_conflict_count"] == 1
    assert readiness["unresolved_pressure_source_conflict_count"] == 0
    assert readiness["pressure_source_resolution_record_count"] == 1
    assert readiness["pressure_source_conflict_requires_operator_review"] is False
    assert readiness["field_package_pressure_conflict_resolution_status"] == (
        "pressure_source_conflicts_resolved_by_operator_review"
    )
    assert readiness["field_package_pressure_conflict_resolution_ready"] is True
    assert audit["conflict_requires_operator_review"] is False
    assert sensor_audit["resolved_pressure_source_conflict_count"] == 1
    assert sensor_audit["unresolved_pressure_source_conflict_count"] == 0
    assert pressure_signal["valid_batch_count"] == 3
    assert patch_plan["patch_plan_status"] == "patch_plan_ready_for_replay_and_holdout"
    assert not any(item["item_id"] == "R8M_PRESSURE_SOURCE_CONFLICT_FIELD_PATCH" for item in patch_plan["items"])


def _write_package(
    package_dir: Path,
    *,
    include_claim_fields: bool,
    include_weak_targets: bool,
    batch_count: int = 3,
    invalid_time_order: bool = False,
    invalid_operation_quality: bool = False,
    invalid_lab_quality: bool = False,
    invalid_proxy_label: bool = False,
    invalid_pressure_headloss_quality: bool = False,
    invalid_pressure_headloss_type: bool = False,
    conflicting_pressure_sources: bool = False,
    resolved_pressure_source_conflict: bool = False,
    misaligned_valid_batches: bool = False,
    include_catalyst_proxy_holdout: bool = False,
    include_catalyst_proxy_node_pressure: bool = True,
) -> None:
    package_dir.mkdir()
    (package_dir / "metadata.json").write_text(json.dumps(_metadata(), ensure_ascii=False), encoding="utf-8")
    tables = _tables(
        include_claim_fields=include_claim_fields,
        include_weak_targets=include_weak_targets,
        batch_count=batch_count,
        invalid_time_order=invalid_time_order,
        invalid_operation_quality=invalid_operation_quality,
        invalid_lab_quality=invalid_lab_quality,
        invalid_proxy_label=invalid_proxy_label,
        invalid_pressure_headloss_quality=invalid_pressure_headloss_quality,
        invalid_pressure_headloss_type=invalid_pressure_headloss_type,
        conflicting_pressure_sources=conflicting_pressure_sources,
        resolved_pressure_source_conflict=resolved_pressure_source_conflict,
        misaligned_valid_batches=misaligned_valid_batches,
        include_catalyst_proxy_holdout=include_catalyst_proxy_holdout,
        include_catalyst_proxy_node_pressure=include_catalyst_proxy_node_pressure,
    )
    for table, rows in tables.items():
        with (package_dir / f"{table}.csv").open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)


def _metadata() -> dict[str, object]:
    return {
        "data_origin": "field",
        "site_id": "field_site_A",
        "campaign_id": "C001",
        "sampling_start": "2026-06-01T08:00:00+08:00",
        "sampling_end": "2026-06-01T12:00:00+08:00",
        "operator_id": "operator_01",
        "instrument_snapshot_id": "sensor_snapshot_v1",
        "chain_of_custody_id": "custody_001",
    }


def _tables(
    *,
    include_claim_fields: bool,
    include_weak_targets: bool,
    batch_count: int,
    invalid_time_order: bool,
    invalid_operation_quality: bool,
    invalid_lab_quality: bool,
    invalid_proxy_label: bool,
    invalid_pressure_headloss_quality: bool,
    invalid_pressure_headloss_type: bool,
    conflicting_pressure_sources: bool,
    resolved_pressure_source_conflict: bool,
    misaligned_valid_batches: bool,
    include_catalyst_proxy_holdout: bool,
    include_catalyst_proxy_node_pressure: bool,
) -> dict[str, list[dict[str, object]]]:
    rows = {
        "sensor_timeseries": [],
        "offline_lab_results": [],
        "campaign_operation_log": [],
        "fast_proxy_event_log": [],
        "pressure_headloss_event_log": [],
    }
    if include_catalyst_proxy_holdout:
        rows["node_modality_sensor_timeseries"] = []
        rows["site_topology_or_bed_geometry"] = [
            {
                "node_id": "N3_catalyst_bed",
                "bed_volume": "8.4",
                "nominal_HRT_min": "34",
                "flow_Lmin": "1.2",
            }
        ]
    for index in range(1, batch_count + 1):
        batch_id = f"B{index:03d}"
        base_sensor = {
                "batch_id": batch_id,
                "timestamp_min": "0",
                "EC_uScm": "3000",
                "turbidity_NTU": "40",
                "UV254_abs": "0.86",
                "pH": "7.8",
                "ORP_mV": "510",
                "flow_Lmin": "1.2",
                "pressure_drop_kPa": "6.4",
                "headloss_kPa_per_m": "0.31",
                "bed_inlet_pressure_kPa": "118.0",
                "bed_outlet_pressure_kPa": "111.6",
        }
        rows["sensor_timeseries"].append(base_sensor)
        if include_catalyst_proxy_holdout:
            node_signal_rows = [
                ("N3_catalyst_bed_outlet", "UV254_abs", "0.42"),
                ("N3_catalyst_bed_outlet", "ORP_mV", "470"),
            ]
            if include_catalyst_proxy_node_pressure:
                node_signal_rows.append(("N3_catalyst_bed", "pressure_drop_kPa", "6.5"))
            for node_id, modality, value in node_signal_rows:
                rows["node_modality_sensor_timeseries"].append(
                    {
                        "batch_id": batch_id,
                        "timestamp_min": "0",
                        "node_id": node_id,
                        "zone": "catalyst_bed",
                        "modality": modality,
                        "value": value,
                        "sensor_status": "calibrated",
                        "instrument_id": "r7j_low_cost_bank",
                        "acquisition_time_min": "0",
                        "ingest_time_min": "1",
                    }
                )
        lab = {
            "batch_id": batch_id,
            "sample_time_min": "15",
            "result_time_min": "10" if invalid_time_order and index == 1 else "95",
            "analyte": "matrix_interference" if include_weak_targets else "matrix_shock_label",
            "value": "1.0",
            "qa_flag": "fail" if invalid_lab_quality or (misaligned_valid_batches and index == 1) else "pass",
        }
        if include_claim_fields:
            lab.update({"detection_limit": "0.01", "method": "LCMS", "unit": "mg/L"})
        lab["pressure_headloss_proxy_label"] = "true"
        if include_catalyst_proxy_holdout:
            lab["lab_label_time_min"] = "95"
        rows["offline_lab_results"].append(lab)
        if include_weak_targets:
            catalyst_row = dict(lab)
            catalyst_row["analyte"] = "catalyst_activity"
            rows["offline_lab_results"].append(catalyst_row)
        operation = {
            "campaign_id": "C001",
            "batch_id": batch_id,
            "action_id": "hold_for_validation",
            "command_time_min": "10",
            "effect_time_min": "50" if invalid_time_order and index == 1 else "16",
            "start_min": "20",
            "end_min": "42",
            "release_policy": "block_release_until_lab_and_field_conformal_calibration",
            "bed_id": "N3_catalyst_bed",
            "pressure_headloss_review_required": "true",
        }
        if resolved_pressure_source_conflict and index == 1:
            operation.update(
                {
                    "pressure_source_resolution": "resolved",
                    "authoritative_pressure_source": "pressure_headloss_event_log",
                    "reviewer_id": "operator_01",
                    "review_time": "2026-06-01T09:05:00+08:00",
                    "calibration_action_id": "CAL_PRESSURE_001",
                    "calibration_note": "Bench gauge matched pressure_headloss_event_log for B001.",
                }
            )
        if include_catalyst_proxy_holdout:
            operation["regeneration_event"] = "true" if index == 1 else "false"
        if invalid_operation_quality:
            operation.update(
                {
                    "recycle_ratio": "1.2",
                    "tank_storage_margin": "-0.1",
                    "actuator_latency_p90": "-2",
                    "pump_valve_result": "failed",
                    "hold_time_min": "-5",
                }
            )
        rows["campaign_operation_log"].append(operation)
        rows["fast_proxy_event_log"].append(
            {
                "campaign_id": "C001",
                "batch_id": batch_id,
                "event_time_min": "10",
                "proxy_score": "0.88",
                "specificity_guard_score": "0.83",
                "protective_triggered": "true",
                "triggered_action_id": "hold_for_validation",
                "field_label_matrix_shock": "true",
                "lab_label_time_min": "5" if invalid_time_order and index == 1 else "95",
                "false_positive_cost_index": "-0.1" if (invalid_proxy_label and index == 1) or (misaligned_valid_batches and index == batch_count) else "0.0",
            }
        )
        rows["pressure_headloss_event_log"].append(
            {
                "campaign_id": "C001",
                "batch_id": batch_id,
                "event_time_min": "18",
                "bed_id": "N3_catalyst_bed",
                "pressure_drop_kPa": (
                    "not_numeric"
                    if invalid_pressure_headloss_type and index == 1
                    else "-1.0"
                    if invalid_pressure_headloss_quality and index == 1
                    else "14.0"
                    if conflicting_pressure_sources and index == 1
                    else "6.4"
                ),
                "headloss_kPa_per_m": "0.31",
                "flow_Lmin": "0" if invalid_pressure_headloss_quality and index == 1 else "1.2",
                "matched_lab_sample_time_min": "15",
                "regeneration_event": "false",
                "hydraulic_anomaly_label": "true" if index == 1 else "false",
                "flow_normalized_pressure_residual": "0.18",
                "expected_clean_bed_pressure_drop_kPa": "5.3",
                "operator_review_required": "true" if index == 1 else "false",
            }
        )
    return rows


def _claim_metrics() -> dict[str, object]:
    return {
        "minimal_field_package_matrix": [
            {
                "need_id": "FVQ_test",
                "field_validation_need": "offline release label",
                "need_type": "soft_sensor_holdout",
                "claim_specific_required_fields": {
                    "offline_lab_results": [
                        "batch_id",
                        "sample_time_min",
                        "result_time_min",
                        "analyte",
                        "value",
                        "qa_flag",
                        "detection_limit",
                        "method",
                        "unit",
                    ]
                },
                "metadata_required_fields": ["data_origin", "site_id", "campaign_id", "chain_of_custody_id"],
            }
        ]
    }


def _catalyst_proxy_metrics() -> dict[str, object]:
    return {
        "weak_axis_repair_plan": {
            "repair_status": "agent48_catalyst_axis_requires_proxy_patch_and_field_label",
            "field_repair_evidence_requirements": [
                {
                    "required_table": "sensor_timeseries",
                    "required_fields": ["timestamp_min", "batch_id", "node_id", "modality", "value", "sensor_status"],
                    "requirement_id": "CAX_1_low_cost_sensor",
                    "patch_class": "low_cost_sensor",
                    "supports_patch_signals": [
                        "N3_catalyst_bed_outlet:UV254_abs",
                        "N3_catalyst_bed_outlet:ORP_mV",
                        "N3_catalyst_bed:pressure_drop_kPa",
                    ],
                    "evidence_stage_required": "field_proxy_holdout",
                },
                {
                    "required_table": "site_topology_or_bed_geometry",
                    "required_fields": ["node_id", "bed_volume", "nominal_HRT_min", "flow_Lmin"],
                    "requirement_id": "CAX_2_hydraulic_or_geometry_field",
                    "patch_class": "hydraulic_or_geometry_field",
                    "supports_patch_signals": ["reactor_bed_volume_or_HRT"],
                    "evidence_stage_required": "field_proxy_holdout",
                },
                {
                    "required_table": "campaign_operation_log",
                    "required_fields": ["batch_id", "regeneration_event", "command_time_min", "effect_time_min"],
                    "requirement_id": "CAX_3_operation_log_field",
                    "patch_class": "operation_log_field",
                    "supports_patch_signals": ["campaign_operation_log.regeneration_event"],
                    "evidence_stage_required": "field_proxy_holdout",
                },
                {
                    "required_table": "offline_lab_results",
                    "required_fields": ["batch_id", "analyte", "value", "qa_flag", "lab_label_time_min"],
                    "requirement_id": "CAX_4_offline_lab_label",
                    "patch_class": "offline_lab_label",
                    "supports_patch_signals": ["pre_post_regeneration_lab_label"],
                    "evidence_stage_required": "field_proxy_holdout",
                },
            ],
        }
    }

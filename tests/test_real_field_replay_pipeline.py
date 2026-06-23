import csv
import json
from pathlib import Path

from water_ai.agents.field_replay_import_agent import write_field_replay_package_template
from water_ai.real_field_replay_pipeline import build_real_field_replay_pipeline


def test_real_field_replay_pipeline_blocks_template_before_import(tmp_path: Path) -> None:
    package_dir = tmp_path / "template_package"
    write_field_replay_package_template(package_dir)

    result = build_real_field_replay_pipeline(package_dir, minimum_proxy_events=3)

    readiness = result["pipeline_readiness"]
    submission = result["field_package_submission_readiness"]
    repair_work_order = submission["field_package_submission_repair_work_order"]
    repair_response_template = result["field_package_submission_repair_response_template"]
    repair_response_preflight = result["field_package_submission_repair_response_preflight"]
    patch_plan = result["field_package_coverage"]["patch_plan"]
    assert result["preflight"]["status"] == "field_package_template_ready_needs_real_values_and_rows"
    assert submission["submission_readiness_status"] == "field_package_submission_blocked_at_import_preflight"
    assert submission["highest_priority_blocker"] == "R7A_IMPORT_PREFLIGHT"
    assert submission["blocking_stage_count"] >= 4
    assert submission["can_submit_to_agent42_smoke_replay"] is False
    assert submission["can_route_to_path_endpoint_layout_holdout"] is False
    assert submission["can_write_to_actuator"] is False
    assert submission["can_write_to_release_gate"] is False
    assert repair_work_order["work_order_status"] == (
        "field_package_submission_repair_work_order_blocked_at_import_preflight"
    )
    assert repair_work_order["highest_priority_blocker"] == "R7A_IMPORT_PREFLIGHT"
    assert repair_work_order["repair_item_count"] >= patch_plan["item_count"]
    assert repair_work_order["routing_contract"]["can_write_to_actuator"] is False
    assert repair_work_order["routing_contract"]["can_write_to_release_gate"] is False
    assert repair_work_order["submission_requirements"]["reject_header_only_template"] is True
    assert repair_work_order["submission_requirements"]["reject_synthetic_or_sample_rows_as_field_evidence"] is True
    work_item_ids = {item["work_item_id"] for item in repair_work_order["repair_items"]}
    assert "R7A_METADATA_PLACEHOLDERS" in work_item_ids
    assert "R7A_REAL_ROWS_sensor_timeseries" in work_item_ids
    assert "R8U76_MINIMUM_MATCHED_BATCH_DEFICIT" in work_item_ids
    assert readiness["field_package_submission_readiness_status"] == (
        "field_package_submission_blocked_at_import_preflight"
    )
    assert readiness["field_package_submission_highest_priority_blocker"] == "R7A_IMPORT_PREFLIGHT"
    assert readiness["field_package_submission_next_operator_action"] == (
        "repair_metadata_headers_and_real_rows_before_agent42"
    )
    assert readiness["field_package_submission_repair_work_order_status"] == (
        "field_package_submission_repair_work_order_blocked_at_import_preflight"
    )
    assert readiness["field_package_submission_repair_item_count"] == repair_work_order["repair_item_count"]
    assert repair_response_template["required_work_item_count"] == repair_work_order["repair_item_count"]
    assert len(repair_response_template["repair_response_rows"]) == repair_work_order["repair_item_count"]
    assert repair_response_preflight["preflight_status"] == (
        "repair_response_preflight_blocked_at_template_markers"
    )
    assert repair_response_preflight["template_marker_count"] == repair_work_order["repair_item_count"]
    assert repair_response_preflight["can_route_to_r7_preflight"] is False
    assert readiness["field_package_submission_repair_response_preflight_status"] == (
        "repair_response_preflight_blocked_at_template_markers"
    )
    assert readiness["field_package_submission_repair_response_can_route_to_r7_preflight"] is False
    assert readiness["field_replay_import_status"] == "field_replay_import_metadata_blocked"
    assert readiness["r7_status"] == "real_field_package_acceptance_blocked_at_import"
    assert patch_plan["patch_plan_status"] == "patch_plan_blocked_at_import_preflight"
    assert patch_plan["item_count"] >= 2
    assert readiness["minimum_valid_matched_batch_count"] == 0
    assert readiness["minimum_valid_operation_action_count"] == 0
    assert readiness["minimum_valid_lab_result_count"] == 0
    assert readiness["minimum_valid_proxy_label_count"] == 0
    assert readiness["field_path_endpoint_label_preflight_status"] == "field_path_endpoint_label_package_blocked_by_preflight"
    assert readiness["field_path_endpoint_label_package_ready"] is False
    assert readiness["field_path_endpoint_required_matched_batch_deficit"] == 5
    assert readiness["field_path_endpoint_alignment_patch_plan_status"] == (
        "field_path_endpoint_alignment_blocked_by_preflight"
    )
    assert readiness["field_path_endpoint_alignment_patch_plan_item_count"] >= 6
    assert readiness["can_route_to_field_layout_holdout_with_path_labels"] is False
    assert readiness["release_gate_endpoint_label_blocked"] is True
    assert readiness["can_write_to_actuator"] is False
    assert readiness["can_write_to_release_gate"] is False


def test_real_field_replay_pipeline_accepts_complete_repair_response_only_for_rerun_route(tmp_path: Path) -> None:
    package_dir = tmp_path / "template_package"
    write_field_replay_package_template(package_dir)
    initial = build_real_field_replay_pipeline(package_dir, minimum_proxy_events=3)
    response = _submitted_repair_response_from_template(
        initial["field_package_submission_repair_response_template"]
    )

    result = build_real_field_replay_pipeline(
        package_dir,
        field_package_submission_repair_response=response,
        minimum_proxy_events=3,
    )

    readiness = result["pipeline_readiness"]
    preflight = result["field_package_submission_repair_response_preflight"]
    assert preflight["preflight_status"] == "repair_response_preflight_ready_for_r7_preflight"
    assert preflight["submitted_item_count"] == preflight["required_work_item_count"]
    assert preflight["template_marker_count"] == 0
    assert preflight["can_route_to_r7_preflight"] is True
    assert preflight["next_operator_action"] == "rerun_r7_field_package_preflight_with_repaired_package"
    assert readiness["field_package_submission_repair_response_can_route_to_r7_preflight"] is True
    assert readiness["field_package_submission_readiness_status"] == (
        "field_package_submission_blocked_at_import_preflight"
    )
    assert readiness["can_write_to_actuator"] is False
    assert readiness["can_write_to_release_gate"] is False


def test_real_field_replay_pipeline_reports_path_endpoint_batch_alignment_deficit(tmp_path: Path) -> None:
    package_dir = tmp_path / "partial_path_endpoint_package"
    _write_complete_package_with_path_endpoint_labels(package_dir)
    for table in [
        "sensor_timeseries",
        "offline_lab_results",
        "campaign_operation_log",
        "fast_proxy_event_log",
        "pressure_headloss_event_log",
        "node_modality_sensor_timeseries",
        "hydraulic_path_stage_labels",
        "final_effluent_endpoint_labels",
    ]:
        _truncate_csv_rows(package_dir / f"{table}.csv", 2)

    result = build_real_field_replay_pipeline(
        package_dir,
        matrix_fast_proxy_metrics={"readiness": {"can_write_to_release_gate": False}},
        claim_specific_package_metrics=_claim_metrics(field_pass=1.0),
        multi_facility_replay_evaluation_metrics=_control_metrics(ready=True),
        unified_field_evidence_gate_metrics=_unified_gate_metrics(field_pass=False),
        minimum_proxy_events=3,
    )

    readiness = result["pipeline_readiness"]
    submission = result["field_package_submission_readiness"]
    preflight = result["field_path_endpoint_label_package_preflight"]
    patch_plan = preflight["alignment_patch_plan"]
    repair_work_order = submission["field_package_submission_repair_work_order"]

    assert preflight["preflight_status"] == "field_path_endpoint_label_package_blocked_by_preflight"
    assert readiness["field_path_endpoint_matched_batch_count"] == 2
    assert readiness["field_path_endpoint_required_matched_batch_deficit"] == 3
    assert readiness["field_path_endpoint_batch_alignment_gap_count"] == 0
    assert readiness["field_path_endpoint_table_batch_counts"]["final_effluent_endpoint_labels"] == 2
    assert readiness["field_path_endpoint_alignment_patch_plan_status"] == (
        "field_path_endpoint_alignment_blocked_by_preflight"
    )
    assert patch_plan["required_matched_batch_deficit"] == 3
    assert any(item["item_id"] == "R8U76_MINIMUM_MATCHED_BATCH_DEFICIT" for item in patch_plan["items"])
    assert readiness["field_path_endpoint_label_package_ready"] is False
    assert readiness["can_route_to_field_layout_holdout_with_path_labels"] is False
    assert readiness["can_write_to_actuator"] is False
    assert readiness["can_write_to_release_gate"] is False
    assert repair_work_order["work_order_status"] in {
        "field_package_submission_repair_work_order_requires_minimum_replay_contract",
        "field_package_submission_repair_work_order_requires_path_endpoint_alignment",
    }
    assert repair_work_order["submission_requirements"]["required_path_endpoint_matched_batch_deficit"] == 3
    assert any(
        item["work_item_id"] == "R8U76_MINIMUM_MATCHED_BATCH_DEFICIT"
        and item["required_matched_batch_deficit"] == 3
        for item in repair_work_order["repair_items"]
    )


def test_real_field_replay_pipeline_dynamically_accepts_path_endpoint_labels(tmp_path: Path) -> None:
    package_dir = tmp_path / "complete_path_endpoint_package"
    _write_complete_package_with_path_endpoint_labels(package_dir)

    result = build_real_field_replay_pipeline(
        package_dir,
        matrix_fast_proxy_metrics={"readiness": {"can_write_to_release_gate": False}},
        claim_specific_package_metrics=_claim_metrics(field_pass=1.0),
        multi_facility_replay_evaluation_metrics=_control_metrics(ready=True),
        unified_field_evidence_gate_metrics=_unified_gate_metrics(field_pass=False),
        minimum_proxy_events=3,
    )

    readiness = result["pipeline_readiness"]
    submission = result["field_package_submission_readiness"]
    preflight = result["field_path_endpoint_label_package_preflight"]
    repair_work_order = submission["field_package_submission_repair_work_order"]

    assert preflight["preflight_status"] == "field_path_endpoint_label_package_ready_for_field_layout_holdout"
    assert readiness["field_path_endpoint_label_preflight_status"] == (
        "field_path_endpoint_label_package_ready_for_field_layout_holdout"
    )
    assert readiness["field_path_endpoint_matched_batch_count"] == 5
    assert readiness["field_path_endpoint_required_matched_batch_deficit"] == 0
    assert readiness["field_path_endpoint_batch_alignment_gap_count"] == 0
    assert readiness["field_path_endpoint_alignment_patch_plan_status"] == "field_path_endpoint_alignment_ready"
    assert readiness["field_path_endpoint_alignment_patch_plan_item_count"] == 0
    assert readiness["field_path_endpoint_label_package_ready"] is True
    assert submission["submission_readiness_status"] == "field_package_submission_import_ready_needs_replay_evidence"
    assert submission["highest_priority_blocker"] == "R7_FIELD_EVIDENCE_SUFFICIENCY"
    assert submission["can_submit_to_agent42_smoke_replay"] is False
    assert submission["path_endpoint_required_matched_batch_deficit"] == 0
    assert submission["can_write_to_actuator"] is False
    assert submission["can_write_to_release_gate"] is False
    assert repair_work_order["work_order_status"] == (
        "field_package_submission_repair_work_order_requires_field_evidence_sufficiency"
    )
    assert repair_work_order["routing_contract"]["can_route_to_path_endpoint_layout_holdout"] is False
    assert repair_work_order["submission_requirements"]["required_path_endpoint_matched_batch_deficit"] == 0
    assert readiness["field_package_submission_readiness_status"] == (
        "field_package_submission_import_ready_needs_replay_evidence"
    )
    assert readiness["field_path_endpoint_final_effluent_label_ready"] is True
    assert readiness["can_route_to_field_layout_holdout_with_path_labels"] is False
    assert readiness["release_gate_endpoint_label_blocked"] is False
    assert readiness["field_evidence_smoke_pass"] is False
    assert readiness["field_evidence_sufficiency_status"] == "field_evidence_sufficiency_blocked_claim_specific_rows"
    assert readiness["can_write_to_actuator"] is False
    assert readiness["can_write_to_release_gate"] is False


def test_real_field_replay_pipeline_routes_complete_package_to_soft_holdout_block(tmp_path: Path) -> None:
    package_dir = tmp_path / "complete_field_package"
    _write_complete_package(package_dir)

    result = build_real_field_replay_pipeline(
        package_dir,
        matrix_fast_proxy_metrics={"readiness": {"can_write_to_release_gate": False}},
        claim_specific_package_metrics=_claim_metrics(field_pass=1.0),
        multi_facility_replay_evaluation_metrics=_control_metrics(ready=True),
        unified_field_evidence_gate_metrics=_unified_gate_metrics(field_pass=False),
        minimum_proxy_events=3,
    )

    readiness = result["pipeline_readiness"]
    r7 = result["r7_acceptance"]["readiness"]
    assert result["preflight"]["status"] == "field_package_preflight_ready_for_agent42"
    assert readiness["field_replay_import_status"] == "field_replay_import_ready_for_timestamped_replay"
    assert readiness["field_replay_evidence_chain_status"] == "field_replay_protective_writeback_candidate_ready"
    assert readiness["minimum_valid_matched_batch_count"] == 3
    assert readiness["minimum_valid_operation_action_count"] == 3
    assert readiness["minimum_invalid_operation_action_count"] == 0
    assert readiness["minimum_valid_lab_result_count"] == 3
    assert readiness["minimum_invalid_lab_result_count"] == 0
    assert readiness["minimum_valid_proxy_label_count"] == 3
    assert readiness["minimum_invalid_proxy_label_count"] == 0
    assert readiness["minimum_pressure_headloss_event_count"] == 3
    assert readiness["minimum_valid_pressure_headloss_event_count"] == 3
    assert readiness["minimum_invalid_pressure_headloss_event_count"] == 0
    assert readiness["minimum_valid_pressure_headloss_batch_count"] == 3
    assert readiness["can_emit_protective_control_candidate"] is True
    assert readiness["can_write_to_actuator"] is False
    assert readiness["can_write_to_release_gate"] is False
    assert r7["real_field_package_acceptance_status"] == "real_field_package_acceptance_blocked_at_soft_sensor_holdout"


def test_real_field_replay_pipeline_surfaces_agent51_catalyst_proxy_holdout_gap(tmp_path: Path) -> None:
    package_dir = tmp_path / "agent51_holdout_gap_package"
    _write_agent51_holdout_gap_package(package_dir)

    result = build_real_field_replay_pipeline(
        package_dir,
        matrix_fast_proxy_metrics={"readiness": {"can_write_to_release_gate": False}},
        claim_specific_package_metrics=_coverage_claim_metrics(),
        catalyst_proxy_metrics=_catalyst_proxy_metrics(),
        unified_field_evidence_gate_metrics=_unified_gate_metrics(field_pass=False),
        minimum_proxy_events=3,
    )

    readiness = result["pipeline_readiness"]
    patch_plan = result["field_package_coverage"]["patch_plan"]
    assert readiness["field_replay_import_status"] == "field_replay_import_ready_for_timestamped_replay"
    assert readiness["field_package_coverage_status"] == "field_package_field_proxy_holdout_gaps"
    assert readiness["soft_holdout_coverage_pass"] is True
    assert readiness["field_proxy_holdout_required"] is True
    assert readiness["field_proxy_holdout_coverage_pass"] is False
    assert readiness["field_proxy_holdout_matched_batch_count"] == 0
    assert readiness["agent51_field_proxy_summary_status"] == "field_proxy_holdout_coverage_gaps"
    assert readiness["agent51_field_proxy_scoreable_batch_count"] == 0
    assert readiness["agent51_field_proxy_validation_pass"] is False
    assert patch_plan["patch_plan_status"] == "patch_plan_requires_catalyst_proxy_field_holdout"
    assert any(item["item_id"] == "R7J_CATALYST_PROXY_SENSOR_SIGNALS" for item in patch_plan["items"])


def _write_complete_package(package_dir: Path) -> None:
    package_dir.mkdir()
    (package_dir / "metadata.json").write_text(json.dumps(_metadata(), ensure_ascii=False), encoding="utf-8")
    for table, rows in _raw_package_as_strings().items():
        with (package_dir / f"{table}.csv").open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)


def _write_agent51_holdout_gap_package(package_dir: Path) -> None:
    package_dir.mkdir()
    (package_dir / "metadata.json").write_text(json.dumps(_metadata(), ensure_ascii=False), encoding="utf-8")
    tables = {
        "sensor_timeseries": [
            _sensor("B001", "0"),
            _sensor("B002", "0"),
            _sensor("B003", "0"),
        ],
        "offline_lab_results": [
            _lab_weak_target("B001", "matrix_interference"),
            _lab_weak_target("B001", "catalyst_activity"),
            _lab_weak_target("B002", "matrix_interference"),
            _lab_weak_target("B002", "catalyst_activity"),
            _lab_weak_target("B003", "matrix_interference"),
            _lab_weak_target("B003", "catalyst_activity"),
        ],
        "campaign_operation_log": [
            _operation("B001", "hold_for_validation", "10", "16", "20", "42"),
            _operation("B002", "hold_for_validation", "12", "18", "22", "44"),
            _operation("B003", "hold_for_validation", "12", "15", "15", "90"),
        ],
        "fast_proxy_event_log": [
            _proxy_event("B001", "10", "95", "true", "true", "0.0"),
            _proxy_event("B002", "12", "90", "true", "true", "0.0"),
            _proxy_event("B003", "12", "100", "false", "false", "0.0"),
        ],
        "pressure_headloss_event_log": [
            _pressure_event("B001", "18", "15", "true"),
            _pressure_event("B002", "20", "15", "false"),
            _pressure_event("B003", "22", "15", "false"),
        ],
    }
    for table, rows in tables.items():
        with (package_dir / f"{table}.csv").open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)


def _write_complete_package_with_path_endpoint_labels(package_dir: Path) -> None:
    package_dir.mkdir()
    (package_dir / "metadata.json").write_text(json.dumps(_metadata(), ensure_ascii=False), encoding="utf-8")
    batches = [f"B{idx:03d}" for idx in range(1, 6)]
    tables = {
        "sensor_timeseries": [_sensor(batch_id, "0") for batch_id in batches],
        "offline_lab_results": [
            {
                **_lab(batch_id, "15", "95"),
                "sample_source": "final_effluent",
                "method": "LCMS",
                "unit": "mg/L",
            }
            for batch_id in batches
        ],
        "campaign_operation_log": [
            {
                **_operation(batch_id, "switch_or_pretreat", "10", "16", "20", "42"),
                "operator_override": "false",
            }
            for batch_id in batches
        ],
        "fast_proxy_event_log": [
            _proxy_event(batch_id, "10", "95", "true", "true", "0.0")
            for batch_id in batches
        ],
        "pressure_headloss_event_log": [
            _pressure_event(batch_id, "18", "15", "true")
            for batch_id in batches
        ],
        "site_topology_or_bed_geometry": [
            {
                "site_id": "field_site_A",
                "node_id": "N5_effluent",
                "zone": "effluent",
                "upstream_node_id": "N4_loop",
                "downstream_node_id": "OUT",
                "path_stage_id": "S5_release_boundary",
                "hydraulic_path_role": "final_effluent_endpoint",
                "nominal_flow_Lmin": "1.20",
                "nominal_HRT_min": "20",
                "recycle_ratio": "0.35",
                "release_boundary_flag": "true",
                "recirculation_loop_flag": "false",
            }
        ],
        "node_modality_sensor_timeseries": [
            {
                "batch_id": batch_id,
                "timestamp_min": "12",
                "layout_id": "field_layout_v1",
                "node_id": "N5_effluent",
                "zone": "effluent",
                "modality": "UV254_abs",
                "sensor_value": "0.18",
                "availability_mask": "1",
                "time_since_last_observed_min": "0",
                "data_origin": "field",
            }
            for batch_id in batches
        ],
        "hydraulic_path_stage_labels": [
            {
                "batch_id": batch_id,
                "layout_id": "field_layout_v1",
                "node_id": "N5_effluent",
                "zone": "effluent",
                "path_stage_id": "S5_release_boundary",
                "hydraulic_path_role": "final_effluent_endpoint",
                "stage_coverage_label": "1",
                "direct_path_stage_coverage_label": "1",
                "proxy_path_stage_coverage_label": "0",
                "label_source": "operator_topology_review",
                "reviewer_id": "reviewer_a",
                "review_time_min": "30",
            }
            for batch_id in batches
        ],
        "final_effluent_endpoint_labels": [
            {
                "batch_id": batch_id,
                "endpoint_node_id": "N5_effluent",
                "sample_time_min": "24",
                "final_effluent_direct_observed": "1",
                "release_gate_label": "hold",
                "release_risk_label": "0.2",
                "analyte": "target_pollutant",
                "value": "0.08",
                "unit": "mg/L",
                "qa_flag": "pass",
                "reviewer_id": "reviewer_a",
            }
            for batch_id in batches
        ],
    }
    for table, rows in tables.items():
        with (package_dir / f"{table}.csv").open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)


def _truncate_csv_rows(csv_path: Path, keep_count: int) -> None:
    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)[:keep_count]
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _submitted_repair_response_from_template(template: dict[str, object]) -> dict[str, object]:
    rows = []
    for index, row in enumerate(template["repair_response_rows"], start=1):
        rows.append(
            {
                **row,
                "operator_status": "submitted_for_r7_preflight",
                "evidence_artifact": f"field_package_repair_artifact_{index}.csv",
                "evidence_type": "field_metadata_or_csv_rows",
                "data_origin_assertion": "field",
                "batch_id_count": "5",
                "reviewer_id": "operator_01",
                "review_time": "2026-06-21T10:00:00+08:00",
                "no_write_boundary_confirmed": "true",
                "operator_notes": "repaired package rows are ready for R7 preflight",
                "template_only": False,
            }
        )
    return {
        "linked_work_order_id": template["linked_work_order_id"],
        "repair_response_rows": rows,
    }


def _metadata() -> dict[str, object]:
    return {
        "data_origin": "field",
        "site_id": "field_site_A",
        "campaign_id": "C001",
        "sampling_start": "2026-06-01T08:00:00+08:00",
        "sampling_end": "2026-06-01T12:00:00+08:00",
        "operator_id": "operator_01",
        "instrument_snapshot_id": "low_cost_sensor_bank_v2",
        "chain_of_custody_id": "custody_C001_signed",
    }


def _raw_package_as_strings() -> dict[str, list[dict[str, object]]]:
    return {
        "sensor_timeseries": [
            _sensor("B001", "0"),
            _sensor("B002", "0"),
            _sensor("B003", "0"),
        ],
        "offline_lab_results": [
            _lab("B001", "15", "95"),
            _lab("B002", "15", "90"),
            _lab("B003", "15", "100"),
        ],
        "campaign_operation_log": [
            _operation("B001", "switch_or_pretreat", "10", "16", "20", "42"),
            _operation("B002", "switch_or_pretreat", "12", "18", "22", "44"),
            _operation("B003", "hold_for_validation", "12", "15", "15", "90"),
        ],
        "fast_proxy_event_log": [
            _proxy_event("B001", "10", "95", "true", "true", "0.0"),
            _proxy_event("B002", "12", "90", "true", "true", "0.0"),
            _proxy_event("B003", "12", "100", "false", "false", "0.0"),
        ],
        "pressure_headloss_event_log": [
            _pressure_event("B001", "18", "15", "true"),
            _pressure_event("B002", "20", "15", "false"),
            _pressure_event("B003", "22", "15", "false"),
        ],
    }


def _sensor(batch_id: str, timestamp: str) -> dict[str, object]:
    return {
        "batch_id": batch_id,
        "timestamp_min": timestamp,
        "EC_uScm": "3000.0",
        "turbidity_NTU": "40.0",
        "UV254_abs": "0.86",
        "pH": "7.8",
        "ORP_mV": "510.0",
        "flow_Lmin": "1.20",
        "pressure_drop_kPa": "6.4",
        "headloss_kPa_per_m": "0.31",
        "bed_inlet_pressure_kPa": "118.0",
        "bed_outlet_pressure_kPa": "111.6",
    }


def _lab(batch_id: str, sample_time: str, result_time: str) -> dict[str, object]:
    return {
        "batch_id": batch_id,
        "sample_time_min": sample_time,
        "result_time_min": result_time,
        "analyte": "matrix_shock_label",
        "value": "1.0",
        "qa_flag": "pass",
        "proxy_holdout_label": "true",
        "pressure_headloss_proxy_label": "true",
    }


def _lab_weak_target(batch_id: str, analyte: str) -> dict[str, object]:
    return {
        "batch_id": batch_id,
        "sample_time_min": "15",
        "result_time_min": "95",
        "analyte": analyte,
        "value": "1.0",
        "qa_flag": "pass",
        "proxy_holdout_label": "true",
        "detection_limit": "0.01",
        "method": "LCMS",
        "unit": "mg/L",
    }


def _operation(batch_id: str, action_id: str, command: str, effect: str, start: str, end: str) -> dict[str, object]:
    return {
        "campaign_id": "C001",
        "batch_id": batch_id,
        "action_id": action_id,
        "command_time_min": command,
        "effect_time_min": effect,
        "start_min": start,
        "end_min": end,
        "release_policy": "block_release_until_lab_and_field_conformal_calibration",
        "recycle_ratio": "0.35",
        "tank_storage_margin": "0.42",
        "actuator_latency_p90": "8.0",
        "pump_valve_result": "ok",
        "hold_time_min": "45",
        "regeneration_event": "false",
        "bed_id": "N3_catalyst_bed",
        "pressure_headloss_review_required": "true",
    }


def _proxy_event(batch_id: str, event_time: str, label_time: str, triggered: str, label: str, cost: str) -> dict[str, object]:
    return {
        "campaign_id": "C001",
        "batch_id": batch_id,
        "event_time_min": event_time,
        "proxy_score": "0.88",
        "specificity_guard_score": "0.83",
        "protective_triggered": triggered,
        "triggered_action_id": "switch_or_pretreat" if triggered == "true" else "none",
        "field_label_matrix_shock": label,
        "lab_label_time_min": label_time,
        "false_positive_cost_index": cost,
    }


def _pressure_event(batch_id: str, event_time: str, lab_sample_time: str, anomaly: str) -> dict[str, object]:
    return {
        "campaign_id": "C001",
        "batch_id": batch_id,
        "event_time_min": event_time,
        "bed_id": "N3_catalyst_bed",
        "pressure_drop_kPa": "6.4",
        "headloss_kPa_per_m": "0.31",
        "flow_Lmin": "1.20",
        "matched_lab_sample_time_min": lab_sample_time,
        "regeneration_event": "false",
        "hydraulic_anomaly_label": anomaly,
        "flow_normalized_pressure_residual": "0.18",
        "expected_clean_bed_pressure_drop_kPa": "5.3",
        "operator_review_required": "true" if anomaly == "true" else "false",
    }


def _claim_metrics(*, field_pass: float) -> dict[str, object]:
    return {
        "readiness": {
            "claim_specific_package_status": "claim_specific_package_ready",
            "source_basis_completion_rate": 1.0,
            "minimal_field_package_schema_pass_rate": 1.0,
            "minimal_field_package_field_pass_rate": field_pass,
        }
    }


def _coverage_claim_metrics() -> dict[str, object]:
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


def _unified_gate_metrics(*, field_pass: bool) -> dict[str, object]:
    return {
        "readiness": {
            "unified_field_evidence_gate_status": "unified_gate_ready",
            "can_emit_field_claim_upgrade": field_pass,
        }
    }


def _control_metrics(*, ready: bool) -> dict[str, object]:
    return {
        "readiness": {
            "replay_evaluation_status": (
                "field_replay_evaluation_candidate_ready"
                if ready
                else "synthetic_replay_evaluation_ready_needs_field_replay"
            ),
            "field_ready": ready,
            "catalyst_proxy_field_validation_pass": ready,
            "catalyst_guardrail_mode": (
                "agent51_field_validated_human_reviewed_relaxation_candidate"
                if ready
                else "agent51_holdout_coverage_gaps_keep_catalyst_guardrail"
            ),
            "can_write_to_actuator": ready,
        },
        "offline_evaluation_metrics": {
            "field_replay_coverage": 0.90 if ready else 0.0,
            "joint_action_accuracy": 0.93 if ready else 0.667,
            "mean_reward_regret": 0.05 if ready else 0.055,
            "catalyst_proxy_summary_status": (
                "field_proxy_holdout_validation_passed"
                if ready
                else "field_proxy_holdout_coverage_gaps"
            ),
            "catalyst_proxy_scoreable_batch_count": 4 if ready else 0,
            "catalyst_proxy_field_validation_pass": ready,
        },
    }

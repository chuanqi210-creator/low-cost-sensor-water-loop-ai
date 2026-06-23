import csv
import json
from pathlib import Path

from water_ai.agents.field_replay_calibration_gate_agent import FieldReplayCalibrationGateAgent
from water_ai.agents.field_replay_import_agent import (
    FieldReplayImportAgent,
    field_replay_package_template_spec,
    load_field_replay_package,
    preflight_field_replay_package,
    write_field_replay_package_template,
)
from water_ai.agents.timestamped_campaign_replay_agent import TimestampedCampaignReplayAgent


def test_field_replay_import_blocks_synthetic_origin_but_normalizes_rows() -> None:
    report = FieldReplayImportAgent(
        metadata=_metadata("synthetic"),
        raw_tables=_raw_package_as_strings(),
    ).run([])

    readiness = report.metrics["readiness"]
    normalized = report.metrics["normalized_datasets"]

    assert readiness["field_replay_import_status"] == "field_replay_import_blocked_non_field_origin"
    assert readiness["can_pass_to_timestamped_replay"] is False
    assert readiness["can_pass_to_g6"] is False
    assert readiness["can_write_to_protective_control"] is False
    assert isinstance(normalized["sensor_timeseries"][0]["timestamp_min"], float)
    assert isinstance(normalized["sensor_timeseries"][0]["flow_Lmin"], float)
    assert normalized["offline_lab_results"][0]["proxy_holdout_label"] is True
    assert isinstance(normalized["campaign_operation_log"][0]["recycle_ratio"], float)
    assert isinstance(normalized["campaign_operation_log"][0]["tank_storage_margin"], float)
    assert isinstance(normalized["campaign_operation_log"][0]["actuator_latency_p90"], float)
    assert isinstance(normalized["campaign_operation_log"][0]["hold_time_min"], float)
    assert normalized["campaign_operation_log"][0]["regeneration_event"] is False
    assert normalized["campaign_operation_log"][0]["pressure_headloss_review_required"] is True
    assert normalized["fast_proxy_event_log"][0]["protective_triggered"] is True
    assert isinstance(normalized["pressure_headloss_event_log"][0]["pressure_drop_kPa"], float)
    assert normalized["pressure_headloss_event_log"][0]["hydraulic_anomaly_label"] is True
    assert any(issue.issue_type == "non_field_origin_blocked" for issue in report.issues)


def test_field_replay_import_ready_package_can_flow_to_agent42_and_agent43() -> None:
    import_report = FieldReplayImportAgent(
        metadata=_metadata("field"),
        raw_tables=_raw_package_as_strings(),
    ).run([])

    import_readiness = import_report.metrics["readiness"]
    assert import_readiness["field_replay_import_status"] == "field_replay_import_ready_for_timestamped_replay"
    assert import_readiness["can_pass_to_timestamped_replay"] is True
    assert import_readiness["can_write_to_protective_control"] is False

    replay_report = TimestampedCampaignReplayAgent(
        datasets=import_report.metrics["normalized_datasets"],
        data_origin=import_readiness["accepted_data_origin"],
        minimum_proxy_events=3,
    ).run([])
    gate_report = FieldReplayCalibrationGateAgent(
        timestamped_replay_report=replay_report,
        matrix_fast_proxy_metrics=_matrix_fast_proxy_metrics(),
        minimum_proxy_events=3,
    ).run([])

    assert replay_report.metrics["readiness"]["timestamped_replay_status"] == "field_timestamped_replay_ready_for_fast_proxy_calibration"
    assert gate_report.metrics["readiness"]["field_replay_gate_status"] == "field_fast_proxy_protective_control_gate_ready"
    assert gate_report.metrics["writeback_policy"]["can_write_to_protective_control"] is True
    assert gate_report.metrics["writeback_policy"]["can_write_to_release_gate"] is False


def test_field_replay_import_rejects_missing_metadata() -> None:
    report = FieldReplayImportAgent(raw_tables=_raw_package_as_strings()).run([])

    readiness = report.metrics["readiness"]

    assert readiness["field_replay_import_status"] == "field_replay_import_missing_metadata"
    assert readiness["can_pass_to_timestamped_replay"] is False
    assert any(issue.issue_type == "metadata_missing" for issue in report.issues)


def test_field_replay_import_rejects_missing_required_table() -> None:
    raw_tables = _raw_package_as_strings()
    raw_tables.pop("fast_proxy_event_log")

    report = FieldReplayImportAgent(
        metadata=_metadata("field"),
        raw_tables=raw_tables,
    ).run([])

    readiness = report.metrics["readiness"]
    audit = report.metrics["table_import_audit"]

    assert readiness["field_replay_import_status"] == "field_replay_import_schema_blocked"
    assert audit["fast_proxy_event_log"]["status"] == "missing_table"
    assert readiness["can_pass_to_timestamped_replay"] is False


def test_field_replay_import_catches_numeric_and_boolean_type_errors() -> None:
    raw_tables = _raw_package_as_strings()
    raw_tables["sensor_timeseries"][0]["pH"] = "not-a-number"
    raw_tables["campaign_operation_log"][0]["tank_storage_margin"] = "full-enough"
    raw_tables["campaign_operation_log"][0]["regeneration_event"] = "unknown"
    raw_tables["offline_lab_results"][0]["proxy_holdout_label"] = "not-sure"
    raw_tables["fast_proxy_event_log"][0]["protective_triggered"] = "maybe"
    raw_tables["pressure_headloss_event_log"][0]["pressure_drop_kPa"] = "high"
    raw_tables["pressure_headloss_event_log"][0]["hydraulic_anomaly_label"] = "maybe"

    report = FieldReplayImportAgent(
        metadata=_metadata("field"),
        raw_tables=raw_tables,
    ).run([])

    audit = report.metrics["table_import_audit"]

    assert report.metrics["readiness"]["field_replay_import_status"] == "field_replay_import_schema_blocked"
    assert audit["sensor_timeseries"]["status"] == "type_coercion_failed"
    assert audit["offline_lab_results"]["status"] == "type_coercion_failed"
    assert audit["campaign_operation_log"]["status"] == "type_coercion_failed"
    assert audit["fast_proxy_event_log"]["status"] == "type_coercion_failed"
    assert audit["pressure_headloss_event_log"]["status"] == "type_coercion_failed"
    assert any(error["field"] == "pH" for error in audit["sensor_timeseries"]["type_errors"])
    assert any(error["field"] == "proxy_holdout_label" for error in audit["offline_lab_results"]["type_errors"])
    assert any(error["field"] == "tank_storage_margin" for error in audit["campaign_operation_log"]["type_errors"])
    assert any(error["field"] == "regeneration_event" for error in audit["campaign_operation_log"]["type_errors"])
    assert any(error["field"] == "protective_triggered" for error in audit["fast_proxy_event_log"]["type_errors"])
    assert any(error["field"] == "pressure_drop_kPa" for error in audit["pressure_headloss_event_log"]["type_errors"])
    assert any(error["field"] == "hydraulic_anomaly_label" for error in audit["pressure_headloss_event_log"]["type_errors"])


def test_field_replay_import_blocks_pressure_headloss_event_without_lab_anchor() -> None:
    raw_tables = _raw_package_as_strings()
    raw_tables["pressure_headloss_event_log"].append(_pressure_event("B999", "18", "15", "true"))

    report = FieldReplayImportAgent(
        metadata=_metadata("field"),
        raw_tables=raw_tables,
    ).run([])

    linkage = report.metrics["linkage_audit"]

    assert report.metrics["readiness"]["field_replay_import_status"] == "field_replay_import_linkage_blocked"
    assert "B999" in linkage["pressure_headloss_without_lab_batches"]
    assert any(issue.issue_type == "linkage_blocked" for issue in report.issues)


def test_load_field_replay_package_reads_csv_and_metadata(tmp_path: Path) -> None:
    package_dir = tmp_path / "field_package"
    package_dir.mkdir()
    (package_dir / "metadata.json").write_text(json.dumps(_metadata("field"), ensure_ascii=False), encoding="utf-8")
    for table, rows in _raw_package_as_strings().items():
        with (package_dir / f"{table}.csv").open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)

    metadata, raw_tables = load_field_replay_package(package_dir)
    report = FieldReplayImportAgent(metadata=metadata, raw_tables=raw_tables).run([])

    assert metadata["data_origin"] == "field"
    assert set(raw_tables) == {
        "sensor_timeseries",
        "offline_lab_results",
        "campaign_operation_log",
        "pressure_headloss_event_log",
        "fast_proxy_event_log",
    }
    assert report.metrics["readiness"]["field_replay_import_status"] == "field_replay_import_ready_for_timestamped_replay"


def test_field_replay_template_preflight_blocks_placeholders_and_header_only_rows(tmp_path: Path) -> None:
    package_dir = tmp_path / "r7_field_template"

    result = write_field_replay_package_template(package_dir)
    metadata, raw_tables = load_field_replay_package(package_dir)
    report = FieldReplayImportAgent(metadata=metadata, raw_tables=raw_tables).run([])
    preflight = preflight_field_replay_package(package_dir)

    assert result["template_dir"] == str(package_dir)
    assert "node_modality_sensor_timeseries.csv" in result["optional_supplement_files"]
    assert "site_topology_or_bed_geometry.csv" in result["optional_supplement_files"]
    assert (package_dir / "node_modality_sensor_timeseries.csv").exists()
    assert (package_dir / "site_topology_or_bed_geometry.csv").exists()
    assert metadata["data_origin"] == "field"
    assert set(raw_tables) == {
        "sensor_timeseries",
        "offline_lab_results",
        "campaign_operation_log",
        "pressure_headloss_event_log",
        "fast_proxy_event_log",
        "node_modality_sensor_timeseries",
        "site_topology_or_bed_geometry",
        "hydraulic_path_stage_labels",
        "final_effluent_endpoint_labels",
    }
    assert report.metrics["readiness"]["field_replay_import_status"] == "field_replay_import_metadata_blocked"
    assert preflight["status"] == "field_package_template_ready_needs_real_values_and_rows"
    assert preflight["files_ready"] is True
    assert preflight["real_rows_ready"] is False
    assert preflight["r7j_supplement_audit"]["node_modality_sensor_timeseries"]["status"] == "supplement_header_ready"
    assert preflight["r7j_supplement_audit"]["site_topology_or_bed_geometry"]["status"] == "supplement_header_ready"
    assert "site_id" in preflight["placeholder_metadata_fields"]
    assert preflight["can_pass_to_timestamped_replay"] is False


def test_field_replay_preflight_ready_for_agent42_on_complete_package(tmp_path: Path) -> None:
    package_dir = tmp_path / "complete_field_package"
    package_dir.mkdir()
    (package_dir / "metadata.json").write_text(json.dumps(_metadata("field"), ensure_ascii=False), encoding="utf-8")
    for table, rows in _raw_package_as_strings().items():
        with (package_dir / f"{table}.csv").open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)

    preflight = preflight_field_replay_package(package_dir)

    assert preflight["status"] == "field_package_preflight_ready_for_agent42"
    assert preflight["files_ready"] is True
    assert preflight["real_rows_ready"] is True
    assert preflight["placeholder_metadata_fields"] == []
    assert preflight["agent44_import_status"] == "field_replay_import_ready_for_timestamped_replay"
    assert preflight["can_pass_to_timestamped_replay"] is True


def test_field_replay_template_spec_contains_r7_guardrail_fields() -> None:
    spec = field_replay_package_template_spec()

    assert "flow_Lmin" in spec["csv_headers"]["sensor_timeseries"]
    assert "sensor_status" in spec["csv_headers"]["sensor_timeseries"]
    assert "node_id" not in spec["csv_headers"]["sensor_timeseries"]
    assert spec["csv_headers"]["node_modality_sensor_timeseries"][:10] == [
        "batch_id",
        "timestamp_min",
        "node_id",
        "zone",
        "modality",
        "value",
        "sensor_status",
        "instrument_id",
        "acquisition_time_min",
        "ingest_time_min",
    ]
    assert "layout_id" in spec["csv_headers"]["node_modality_sensor_timeseries"]
    assert "availability_mask" in spec["csv_headers"]["node_modality_sensor_timeseries"]
    assert "time_since_last_observed_min" in spec["csv_headers"]["node_modality_sensor_timeseries"]
    assert "data_origin" in spec["csv_headers"]["node_modality_sensor_timeseries"]
    assert "sensor_value" in spec["csv_headers"]["node_modality_sensor_timeseries"]
    assert "proxy_holdout_label" in spec["csv_headers"]["offline_lab_results"]
    assert "pressure_headloss_proxy_label" in spec["csv_headers"]["offline_lab_results"]
    assert "lab_label_time_min" in spec["csv_headers"]["offline_lab_results"]
    assert "tank_storage_margin" in spec["csv_headers"]["campaign_operation_log"]
    assert "actuator_latency_p90" in spec["csv_headers"]["campaign_operation_log"]
    assert "hold_time_min" in spec["csv_headers"]["campaign_operation_log"]
    assert "regeneration_event" in spec["csv_headers"]["campaign_operation_log"]
    assert "pressure_headloss_event_log" in spec["csv_headers"]
    assert "matched_lab_sample_time_min" in spec["csv_headers"]["pressure_headloss_event_log"]
    assert "operator_review_required" in spec["csv_headers"]["pressure_headloss_event_log"]
    assert spec["csv_headers"]["site_topology_or_bed_geometry"][:4] == [
        "node_id",
        "bed_volume",
        "nominal_HRT_min",
        "flow_Lmin",
    ]
    assert "site_id" in spec["csv_headers"]["site_topology_or_bed_geometry"]
    assert "path_stage_id" in spec["csv_headers"]["site_topology_or_bed_geometry"]
    assert "hydraulic_path_role" in spec["csv_headers"]["site_topology_or_bed_geometry"]
    assert "release_boundary_flag" in spec["csv_headers"]["site_topology_or_bed_geometry"]
    assert "hydraulic_path_stage_labels" in spec["csv_headers"]
    assert "final_effluent_endpoint_labels" in spec["csv_headers"]
    assert "node_modality_sensor_timeseries.csv" in spec["optional_supplement_files"]
    assert "site_topology_or_bed_geometry.csv" in spec["optional_supplement_files"]
    assert "hydraulic_path_stage_labels.csv" in spec["optional_supplement_files"]
    assert "final_effluent_endpoint_labels.csv" in spec["optional_supplement_files"]
    assert spec["r7j_catalyst_proxy_holdout_template"]["minimum_matched_batch_count"] == 3


def _metadata(origin: str) -> dict[str, object]:
    return {
        "data_origin": origin,
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
        "pressure_headloss_event_log": [
            _pressure_event("B001", "18", "15", "true"),
            _pressure_event("B002", "20", "15", "true"),
            _pressure_event("B003", "30", "15", "false"),
        ],
        "fast_proxy_event_log": [
            _proxy_event("B001", "10", "95", "true", "true", "0.0"),
            _proxy_event("B002", "12", "90", "true", "true", "0.0"),
            _proxy_event("B003", "12", "100", "false", "false", "0.0"),
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
        "pressure_drop_kPa": "4.20",
        "headloss_kPa_per_m": "5.25",
        "bed_inlet_pressure_kPa": "104.10",
        "bed_outlet_pressure_kPa": "99.90",
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
        "bed_id": "BED_A",
        "pressure_headloss_review_required": "true",
    }


def _pressure_event(batch_id: str, event_time: str, matched_sample: str, anomaly: str) -> dict[str, object]:
    return {
        "campaign_id": "C001",
        "batch_id": batch_id,
        "event_time_min": event_time,
        "bed_id": "BED_A",
        "pressure_drop_kPa": "6.80" if anomaly == "true" else "4.10",
        "headloss_kPa_per_m": "8.50" if anomaly == "true" else "5.10",
        "flow_Lmin": "1.20",
        "matched_lab_sample_time_min": matched_sample,
        "regeneration_event": "false",
        "hydraulic_anomaly_label": anomaly,
        "flow_normalized_pressure_residual": "0.42" if anomaly == "true" else "0.08",
        "expected_clean_bed_pressure_drop_kPa": "3.20",
        "operator_review_required": anomaly,
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


def _matrix_fast_proxy_metrics() -> dict[str, object]:
    return {
        "readiness": {
            "can_write_to_release_gate": False,
        }
    }

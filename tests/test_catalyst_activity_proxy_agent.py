import csv
import json
from pathlib import Path

from water_ai.agents.catalyst_activity_proxy_agent import CatalystActivityProxyAgent
from water_ai.agents.sensor_network_sparse_placement_agent import SensorNetworkSparsePlacementAgent
from water_ai.catalyst_proxy_field_holdout import build_catalyst_proxy_field_holdout_summary


def test_catalyst_activity_proxy_agent_builds_proxy_catalog_and_feature_table() -> None:
    report = CatalystActivityProxyAgent(sparse_placement_metrics=_sparse_metrics()).run([])

    catalog = report.metrics["proxy_catalog"]
    table = report.metrics["proxy_feature_table"]
    method = report.metrics["method_contract"]

    assert len(catalog) >= 5
    assert table
    assert "input_contract" in method
    assert "failure_boundary" in method
    assert any(item["proxy_id"] == "bed_uv254_removal_delta" for item in catalog)
    assert all("catalyst_activity_proxy_score" in row for row in table)


def test_catalyst_activity_proxy_agent_identifies_missing_patch_signals_from_agent48() -> None:
    report = CatalystActivityProxyAgent(sparse_placement_metrics=_sparse_metrics()).run([])

    metrics = report.metrics["proxy_metrics"]
    repair = report.metrics["weak_axis_repair_plan"]
    patches = metrics["recommended_sensor_patches"]

    assert "N3_catalyst_bed_outlet:UV254_abs" in patches
    assert "N3_catalyst_bed_outlet:ORP_mV" in patches
    assert "N3_catalyst_bed:pressure_drop_kPa" in patches
    assert metrics["proxy_observability_after_recommended_patch"] > metrics["current_proxy_observability"]
    assert metrics["weak_state_coverage_after_proxy_design"] >= 0.55
    assert repair["repair_status"] == "agent48_catalyst_axis_requires_proxy_patch_and_field_label"
    assert repair["current_axis_coverage"] == 0.3
    assert repair["target_axis_coverage"] == 0.55
    assert repair["recoverable_by_current_candidate_pool"] is False
    assert repair["proxy_projected_axis_coverage"] >= 0.55
    assert repair["prioritized_proxy_patches"][0]["patch_signal"] == "N3_catalyst_bed_outlet:UV254_abs"
    assert any(req["required_table"] == "offline_lab_results" for req in repair["field_repair_evidence_requirements"])


def test_catalyst_activity_proxy_agent_keeps_agent49_block_for_synthetic_proxy_design() -> None:
    report = CatalystActivityProxyAgent(sparse_placement_metrics=_sparse_metrics()).run([])

    readiness = report.metrics["readiness"]
    interface = report.metrics["agent49_interface"]
    repair = report.metrics["weak_axis_repair_plan"]

    assert readiness["catalyst_proxy_status"] == "synthetic_catalyst_proxy_design_ready_needs_field_labels"
    assert readiness["can_relax_agent49_catalyst_uncertainty_block"] is False
    assert interface["policy_effect"] == "keep_R3_catalyst_uncertainty_block"
    assert interface["state_patch"]["weak_axis_repair_status"] == repair["repair_status"]
    assert interface["state_patch"]["prioritized_proxy_patches"]
    assert any(issue.issue_type == "field_catalyst_labels_required" for issue in report.issues)
    assert any(
        issue.issue_type == "agent48_catalyst_axis_not_recoverable_by_current_candidate_pool"
        for issue in report.issues
    )


def test_catalyst_activity_proxy_agent_can_become_field_candidate_with_holdout_validation() -> None:
    report = CatalystActivityProxyAgent(
        sparse_placement_metrics=_sparse_metrics(),
        data_origin="field_proxy_holdout",
        field_validation={
            "field_label_coverage": 0.82,
            "proxy_label_correlation": 0.76,
            "holdout_mae": 0.11,
        },
    ).run([])

    readiness = report.metrics["readiness"]
    interface = report.metrics["agent49_interface"]

    assert readiness["catalyst_proxy_status"] == "field_catalyst_proxy_candidate_ready"
    assert readiness["can_relax_agent49_catalyst_uncertainty_block"] is True
    assert interface["can_relax_catalyst_uncertainty_block"] is True
    assert readiness["can_write_to_release_gate"] is False


def test_catalyst_proxy_field_holdout_summary_extracts_scoreable_rows(tmp_path: Path) -> None:
    package_dir = tmp_path / "agent51_field_holdout_ready"
    _write_catalyst_holdout_package(package_dir)

    summary = build_catalyst_proxy_field_holdout_summary(package_dir)
    report = CatalystActivityProxyAgent(
        sparse_placement_metrics=_sparse_metrics(),
        field_proxy_holdout_summary=summary,
    ).run([])

    readiness = report.metrics["readiness"]
    interface = report.metrics["agent49_interface"]

    assert summary["field_proxy_holdout_summary_status"] == "field_proxy_holdout_validation_passed"
    assert summary["matched_batch_count"] == 3
    assert summary["scoreable_batch_count"] == 3
    assert summary["field_validation_metrics"]["proxy_label_correlation"] >= 0.68
    assert summary["field_validation_metrics"]["holdout_mae"] <= 0.16
    assert readiness["data_origin"] == "field_proxy_holdout"
    assert readiness["field_validated"] is True
    assert readiness["pressure_evidence_source_contract"] == [
        "node_modality_sensor_timeseries",
        "pressure_headloss_event_log",
    ]
    assert interface["can_relax_catalyst_uncertainty_block"] is True
    assert readiness["can_write_to_actuator"] is False
    assert readiness["can_write_to_release_gate"] is False


def test_catalyst_proxy_field_holdout_summary_uses_pressure_headloss_event_log_as_pressure_source(tmp_path: Path) -> None:
    package_dir = tmp_path / "agent51_pressure_event_source"
    _write_catalyst_holdout_package(
        package_dir,
        include_node_pressure_signal=False,
        include_pressure_headloss_events=True,
    )

    summary = build_catalyst_proxy_field_holdout_summary(package_dir)

    assert summary["field_proxy_holdout_summary_status"] == "field_proxy_holdout_validation_passed"
    assert summary["scoreable_batch_count"] == 3
    assert summary["pressure_headloss_event_source_batch_count"] == 3
    assert summary["pressure_evidence_source_batch_counts"]["pressure_headloss_event_log"] == 3
    assert "pressure_headloss_event_log" in summary["accepted_pressure_evidence_sources"]
    assert "N3_catalyst_bed:pressure_drop_kPa" not in summary["missing_required_signals"]
    assert all(row["pressure_drop_source"] == "pressure_headloss_event_log" for row in summary["feature_rows"])


def test_catalyst_proxy_field_holdout_summary_blocks_conflicting_pressure_sources(tmp_path: Path) -> None:
    package_dir = tmp_path / "agent51_pressure_source_conflict"
    _write_catalyst_holdout_package(
        package_dir,
        include_node_pressure_signal=True,
        include_pressure_headloss_events=True,
        pressure_headloss_event_values={"B001": "1.0", "B002": "12.0", "B003": "8.0"},
    )

    summary = build_catalyst_proxy_field_holdout_summary(package_dir)

    assert summary["field_proxy_holdout_summary_status"] == "field_proxy_holdout_coverage_gaps"
    assert summary["scoreable_batch_count"] == 2
    assert summary["pressure_source_conflict_count"] == 1
    assert summary["conflict_requires_operator_review"] is True
    conflict = summary["pressure_source_conflicts"][0]
    assert conflict["batch_id"] == "B002"
    assert conflict["action"] == "operator_review_required_before_agent51_scoring"
    assert summary["pressure_evidence_source_batch_counts"]["source_conflict_requires_operator_review"] == 1
    assert "source_conflict_requires_operator_review" not in summary["accepted_pressure_evidence_sources"]


def test_catalyst_proxy_field_holdout_summary_restores_resolved_pressure_source_conflict(
    tmp_path: Path,
) -> None:
    package_dir = tmp_path / "agent51_pressure_source_conflict_resolved"
    _write_catalyst_holdout_package(
        package_dir,
        include_node_pressure_signal=True,
        include_pressure_headloss_events=True,
        pressure_headloss_event_values={"B001": "1.0", "B002": "12.0", "B003": "8.0"},
        pressure_source_resolution_by_batch={"B002": "pressure_headloss_event_log"},
    )

    summary = build_catalyst_proxy_field_holdout_summary(package_dir)

    assert summary["field_proxy_holdout_summary_status"] == "field_proxy_holdout_validation_passed"
    assert summary["scoreable_batch_count"] == 3
    assert summary["pressure_source_conflict_count"] == 1
    assert summary["resolved_pressure_source_conflict_count"] == 1
    assert summary["unresolved_pressure_source_conflict_count"] == 0
    assert summary["pressure_source_resolution_record_count"] == 1
    assert summary["conflict_requires_operator_review"] is False
    assert summary["pressure_source_resolutions"][0]["batch_id"] == "B002"
    assert summary["pressure_source_resolutions"][0]["authoritative_pressure_source"] == "pressure_headloss_event_log"
    assert summary["pressure_evidence_source_batch_counts"]["source_conflict_requires_operator_review"] == 0
    resolved_row = next(row for row in summary["feature_rows"] if row["batch_id"] == "B002")
    assert resolved_row["pressure_drop_source"] == "pressure_headloss_event_log"
    assert resolved_row["score_status"] == "scoreable"


def test_catalyst_proxy_field_holdout_summary_blocks_when_node_signals_are_missing(tmp_path: Path) -> None:
    package_dir = tmp_path / "agent51_field_holdout_gap"
    _write_catalyst_holdout_package(package_dir, include_node_signals=False)

    summary = build_catalyst_proxy_field_holdout_summary(package_dir)
    report = CatalystActivityProxyAgent(
        sparse_placement_metrics=_sparse_metrics(),
        field_proxy_holdout_summary=summary,
    ).run([])

    readiness = report.metrics["readiness"]

    assert summary["field_proxy_holdout_summary_status"] == "field_proxy_holdout_coverage_gaps"
    assert summary["ready_for_agent51_validation"] is False
    assert "N3_catalyst_bed_outlet:UV254_abs" in summary["missing_required_signals"]
    assert readiness["field_labels_required"] is True
    assert readiness["can_relax_agent49_catalyst_uncertainty_block"] is False
    assert any(issue.issue_type == "field_proxy_holdout_summary_not_ready" for issue in report.issues)


def _sparse_metrics() -> dict[str, object]:
    report = SensorNetworkSparsePlacementAgent(max_sensors=6, budget_limit=5.8).run([])
    return {
        "selected_sensor_plan": report.metrics["selected_sensor_plan"],
        "coverage": dict(report.metrics["coverage"]),
        "readiness": dict(report.metrics["readiness"]),
        "selected_strategy": dict(report.metrics["selected_strategy"]),
        "placement_diagnostics": dict(report.metrics["placement_diagnostics"]),
    }


def _write_catalyst_holdout_package(
    package_dir: Path,
    *,
    include_node_signals: bool = True,
    include_node_pressure_signal: bool = True,
    include_pressure_headloss_events: bool = False,
    pressure_headloss_event_values: dict[str, str] | None = None,
    pressure_source_resolution_by_batch: dict[str, str] | None = None,
) -> None:
    package_dir.mkdir()
    (package_dir / "metadata.json").write_text(
        json.dumps(
            {
                "data_origin": "field",
                "site_id": "field_site_A",
                "campaign_id": "C001",
                "sampling_start": "2026-06-01T08:00:00+08:00",
                "sampling_end": "2026-06-01T12:00:00+08:00",
                "operator_id": "operator_01",
                "instrument_snapshot_id": "sensor_snapshot_v1",
                "chain_of_custody_id": "custody_001",
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    rows_by_table = {
        "sensor_timeseries": [
            _sensor_context("B001", "1.00", "700"),
            _sensor_context("B002", "1.00", "700"),
            _sensor_context("B003", "1.00", "700"),
        ],
        "offline_lab_results": [
            _catalyst_label("B001", "0.80"),
            _catalyst_label("B002", "0.47"),
            _catalyst_label("B003", "0.23"),
        ],
        "campaign_operation_log": [
            _operation("B001", "true"),
            _operation("B002", "false"),
            _operation("B003", "false"),
        ],
        "site_topology_or_bed_geometry": [
            {
                "node_id": "N3_catalyst_bed",
                "bed_volume": "8.4",
                "nominal_HRT_min": "20",
                "flow_Lmin": "1.2",
            }
        ],
    }
    if include_node_signals:
        rows_by_table["node_modality_sensor_timeseries"] = [
            *_node_signal_rows("B001", "0.30", "580", "1.0", include_pressure=include_node_pressure_signal),
            *_node_signal_rows("B002", "0.60", "640", "4.0", include_pressure=include_node_pressure_signal),
            *_node_signal_rows("B003", "0.80", "675", "8.0", include_pressure=include_node_pressure_signal),
        ]
    if include_pressure_headloss_events:
        event_values = pressure_headloss_event_values or {"B001": "1.0", "B002": "4.0", "B003": "8.0"}
        resolution_by_batch = pressure_source_resolution_by_batch or {}
        rows_by_table["pressure_headloss_event_log"] = [
            _pressure_headloss_event("B001", event_values["B001"], "true", resolution_by_batch.get("B001")),
            _pressure_headloss_event("B002", event_values["B002"], "false", resolution_by_batch.get("B002")),
            _pressure_headloss_event("B003", event_values["B003"], "false", resolution_by_batch.get("B003")),
        ]
    for table, rows in rows_by_table.items():
        with (package_dir / f"{table}.csv").open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)


def _sensor_context(batch_id: str, uv254: str, orp: str) -> dict[str, object]:
    return {
        "batch_id": batch_id,
        "timestamp_min": "0",
        "EC_uScm": "3000",
        "turbidity_NTU": "40",
        "UV254_abs": uv254,
        "pH": "7.8",
        "ORP_mV": orp,
        "flow_Lmin": "1.2",
    }


def _node_signal_rows(
    batch_id: str,
    uv254_out: str,
    orp_out: str,
    pressure_drop: str,
    *,
    include_pressure: bool = True,
) -> list[dict[str, object]]:
    rows = [
        _node_signal(batch_id, "N3_catalyst_bed_outlet", "UV254_abs", uv254_out),
        _node_signal(batch_id, "N3_catalyst_bed_outlet", "ORP_mV", orp_out),
    ]
    if include_pressure:
        rows.append(_node_signal(batch_id, "N3_catalyst_bed", "pressure_drop_kPa", pressure_drop))
    return rows


def _node_signal(batch_id: str, node_id: str, modality: str, value: str) -> dict[str, object]:
    return {
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


def _catalyst_label(batch_id: str, value: str) -> dict[str, object]:
    return {
        "batch_id": batch_id,
        "sample_time_min": "15",
        "result_time_min": "95",
        "analyte": "catalyst_activity",
        "value": value,
        "qa_flag": "pass",
        "lab_label_time_min": "95",
    }


def _operation(batch_id: str, regeneration_event: str) -> dict[str, object]:
    return {
        "campaign_id": "C001",
        "batch_id": batch_id,
        "action_id": "hold_for_validation",
        "command_time_min": "10",
        "effect_time_min": "16",
        "start_min": "20",
        "end_min": "42",
        "release_policy": "block_release_until_lab_and_field_conformal_calibration",
        "regeneration_event": regeneration_event,
    }


def _pressure_headloss_event(
    batch_id: str,
    pressure_drop: str,
    anomaly: str,
    authoritative_source: str | None = None,
) -> dict[str, object]:
    row = {
        "campaign_id": "C001",
        "batch_id": batch_id,
        "event_time_min": "18",
        "bed_id": "N3_catalyst_bed",
        "pressure_drop_kPa": pressure_drop,
        "headloss_kPa_per_m": "0.31",
        "flow_Lmin": "1.2",
        "matched_lab_sample_time_min": "15",
        "regeneration_event": "false",
        "hydraulic_anomaly_label": anomaly,
        "flow_normalized_pressure_residual": "0.18",
        "expected_clean_bed_pressure_drop_kPa": "5.3",
        "operator_review_required": "true" if anomaly == "true" else "false",
        "pressure_source_resolution": "",
        "authoritative_pressure_source": "",
        "reviewer_id": "",
        "review_time": "",
        "calibration_action_id": "",
        "calibration_note": "",
    }
    if authoritative_source:
        row.update(
            {
                "pressure_source_resolution": "resolved",
                "authoritative_pressure_source": authoritative_source,
                "reviewer_id": "operator_01",
                "review_time": "2026-06-01T09:10:00+08:00",
                "calibration_action_id": "CAL_PRESSURE_002",
                "calibration_note": f"Operator selected {authoritative_source} for {batch_id}.",
            }
        )
    return row

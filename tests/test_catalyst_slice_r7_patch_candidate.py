from __future__ import annotations

import csv
from pathlib import Path

from water_ai.catalyst_field_package_slice import TABLE_COLUMNS
from water_ai.catalyst_slice_r7_patch_candidate import build_catalyst_slice_r7_patch_candidate


def test_catalyst_slice_r7_patch_waits_for_valid_slice(tmp_path: Path) -> None:
    result = build_catalyst_slice_r7_patch_candidate(
        candidate_dir=tmp_path / "candidate",
        external_slice_supplied=False,
    )

    assert result["patch_status"] == "catalyst_slice_r7_patch_waiting_for_valid_catalyst_slice"
    assert result["slice_preflight_pass"] is False
    assert result["candidate_materialized"] is False
    assert result["candidate_preflight_status"] == "not_run"
    assert result["can_run_r7_import_preflight_on_candidate"] is False
    assert result["can_submit_candidate_as_REAL_FIELD_REPLAY_PACKAGE_DIR"] is False
    assert result["can_route_to_agent51_field_proxy_holdout"] is False
    assert result["can_write_to_actuator"] is False
    assert result["can_write_to_release_gate"] is False


def test_valid_catalyst_slice_materializes_full_r7_patch_candidate_but_preserves_full_package_gaps(
    tmp_path: Path,
) -> None:
    slice_dir = tmp_path / "valid_slice"
    candidate_dir = tmp_path / "candidate"
    _write_valid_slice(slice_dir, ["B001", "B002", "B003"])

    result = build_catalyst_slice_r7_patch_candidate(
        slice_dir=slice_dir,
        candidate_dir=candidate_dir,
        external_slice_supplied=True,
    )

    gap = result["full_package_gap_summary"]
    overlay = result["overlay_audit"]

    assert result["patch_status"] == "catalyst_slice_r7_patch_candidate_materialized_but_full_package_blocked"
    assert result["slice_preflight_pass"] is True
    assert result["slice_matched_batch_count"] == 3
    assert result["candidate_materialized"] is True
    assert overlay["overlay_pass"] is True
    assert overlay["patched_table_count"] == 4
    assert (candidate_dir / "metadata.json").exists()
    assert (candidate_dir / "node_modality_sensor_timeseries.csv").exists()
    assert result["candidate_preflight_status"] == "field_package_template_ready_needs_real_values_and_rows"
    assert "sensor_timeseries" in gap["header_only_required_tables"]
    assert "fast_proxy_event_log" in gap["header_only_required_tables"]
    assert "pressure_headloss_event_log" in gap["header_only_required_tables"]
    assert "site_id" in gap["placeholder_metadata_fields"]
    assert gap["remaining_gap_count"] > 0
    assert result["can_run_r7_import_preflight_on_candidate"] is True
    assert result["can_submit_candidate_as_REAL_FIELD_REPLAY_PACKAGE_DIR"] is False
    assert result["can_route_to_agent51_field_proxy_holdout"] is False
    assert "cannot replace metadata" in result["field_boundary"]


def test_catalyst_slice_r7_patch_blocks_missing_explicit_base_package(tmp_path: Path) -> None:
    slice_dir = tmp_path / "valid_slice"
    _write_valid_slice(slice_dir, ["B001", "B002", "B003"])

    result = build_catalyst_slice_r7_patch_candidate(
        slice_dir=slice_dir,
        candidate_dir=tmp_path / "candidate",
        base_package_dir=tmp_path / "missing_base",
        external_slice_supplied=True,
        base_package_supplied=True,
    )

    assert result["slice_preflight_pass"] is True
    assert result["patch_status"] == "catalyst_slice_r7_patch_blocked_by_missing_base_package"
    assert result["candidate_materialized"] is False
    assert result["can_submit_candidate_as_REAL_FIELD_REPLAY_PACKAGE_DIR"] is False


def _write_valid_slice(path: Path, batch_ids: list[str]) -> None:
    _write_table(
        path / "node_modality_sensor_timeseries.csv",
        TABLE_COLUMNS["node_modality_sensor_timeseries"],
        [
            _sensor_row(batch_id, node_id, modality, index)
            for index, batch_id in enumerate(batch_ids, start=1)
            for node_id, modality in [
                ("N3_catalyst_bed", "pressure_drop_kPa"),
                ("N3_catalyst_bed_outlet", "UV254_abs"),
                ("N3_catalyst_bed_outlet", "ORP_mV"),
            ]
        ],
    )
    _write_table(
        path / "offline_lab_results.csv",
        TABLE_COLUMNS["offline_lab_results"],
        [_lab_row(batch_id, index) for index, batch_id in enumerate(batch_ids, start=1)],
    )
    _write_table(
        path / "campaign_operation_log.csv",
        TABLE_COLUMNS["campaign_operation_log"],
        [_operation_row(batch_id, index) for index, batch_id in enumerate(batch_ids, start=1)],
    )
    _write_table(
        path / "site_topology_or_bed_geometry.csv",
        TABLE_COLUMNS["site_topology_or_bed_geometry"],
        [_geometry_row()],
    )


def _write_table(path: Path, columns: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in columns})


def _sensor_row(batch_id: str, node_id: str, modality: str, index: int) -> dict[str, str]:
    return {
        "batch_id": batch_id,
        "timestamp_min": str(index * 10),
        "node_id": node_id,
        "zone": "catalyst_bed_zone",
        "modality": modality,
        "value": str(1.5 + index),
        "sensor_status": "ok",
        "instrument_id": f"INS-{modality}",
        "acquisition_time_min": str(index * 10),
        "ingest_time_min": str(index * 10 + 1),
        "layout_id": "field_layout_v1",
        "availability_mask": "1",
        "time_since_last_observed_min": "0",
        "data_origin": "field",
        "sensor_value": str(1.5 + index),
    }


def _lab_row(batch_id: str, index: int) -> dict[str, str]:
    return {
        "batch_id": batch_id,
        "sample_time_min": str(index * 10 + 2),
        "result_time_min": str(index * 10 + 30),
        "analyte": "catalyst_activity",
        "value": str(0.7 + index * 0.01),
        "qa_flag": "pass",
        "proxy_holdout_label": "valid",
        "catalyst_activity_label": "valid",
        "pressure_headloss_proxy_label": "valid",
        "lab_label_time_min": str(index * 10 + 30),
        "detection_limit": "0.01",
        "method": "field_method_ref",
        "unit": "relative_activity",
        "sample_source": "N3_catalyst_bed",
    }


def _operation_row(batch_id: str, index: int) -> dict[str, str]:
    return {
        "campaign_id": "CAMP-001",
        "batch_id": batch_id,
        "action_id": f"ACT-{index:03d}",
        "command_time_min": str(index * 10 + 40),
        "effect_time_min": str(index * 10 + 45),
        "start_min": str(index * 10),
        "end_min": str(index * 10 + 60),
        "release_policy": "hold",
        "recycle_ratio": "0.2",
        "tank_storage_margin": "0.6",
        "actuator_latency_p90": "5",
        "pump_valve_result": "confirmed",
        "hold_time_min": "30",
        "regeneration_event": "true" if index == 1 else "false",
        "bed_id": "N3_catalyst_bed",
        "pressure_headloss_review_required": "false",
        "operator_override": "false",
    }


def _geometry_row() -> dict[str, str]:
    return {
        "node_id": "N3_catalyst_bed",
        "bed_volume": "100",
        "nominal_HRT_min": "30",
        "flow_Lmin": "3.3",
        "site_id": "SITE-001",
        "zone": "catalyst_bed_zone",
        "upstream_node_id": "N2_pre_treatment_outlet",
        "downstream_node_id": "N3_catalyst_bed_outlet",
        "path_stage_id": "catalyst_stage",
        "hydraulic_path_role": "reaction_contact_zone",
        "nominal_flow_Lmin": "3.3",
        "recycle_ratio": "0.2",
        "release_boundary_flag": "false",
        "recirculation_loop_flag": "true",
    }

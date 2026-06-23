from __future__ import annotations

import csv
from pathlib import Path

from water_ai.catalyst_field_package_slice import (
    TABLE_COLUMNS,
    build_catalyst_field_package_slice_preflight,
    build_catalyst_field_package_slice_template,
)


def test_catalyst_field_package_slice_template_builds_four_r7_aligned_tables() -> None:
    template = build_catalyst_field_package_slice_template()

    assert template["slice_id"] == "R8u113_catalyst_field_package_slice"
    assert template["target_hidden_state"] == "catalyst_activity"
    assert template["required_table_count"] == 4
    assert template["minimum_matched_batch_count"] == 3
    assert template["table_row_counts"] == {
        "node_modality_sensor_timeseries": 9,
        "offline_lab_results": 3,
        "campaign_operation_log": 3,
        "site_topology_or_bed_geometry": 1,
    }
    sensor_rows = template["tables"]["node_modality_sensor_timeseries"]["rows"]
    assert {f"{row['node_id']}:{row['modality']}" for row in sensor_rows} == {
        "N3_catalyst_bed:pressure_drop_kPa",
        "N3_catalyst_bed_outlet:UV254_abs",
        "N3_catalyst_bed_outlet:ORP_mV",
    }
    assert all(row["data_origin"] == "TODO_field" for row in sensor_rows)
    assert "cannot authorize actuator writes" in template["no_write_boundary"]


def test_catalyst_field_package_slice_preflight_waits_without_external_slice() -> None:
    result = build_catalyst_field_package_slice_preflight(external_slice_supplied=False)

    assert result["slice_status"] == "catalyst_field_package_slice_waiting_for_CATALYST_FIELD_PACKAGE_SLICE_DIR"
    assert result["slice_preflight_pass"] is False
    assert result["matched_batch_count"] == 0
    assert result["can_route_to_r7_field_package_patch_candidate"] is False
    assert result["can_route_to_agent51_field_proxy_holdout"] is False
    assert result["can_relax_agent49_catalyst_uncertainty_block"] is False
    assert result["can_write_to_actuator"] is False
    assert result["can_write_to_release_gate"] is False


def test_valid_catalyst_field_package_slice_becomes_r7_patch_candidate_without_claiming_holdout(
    tmp_path: Path,
) -> None:
    _write_valid_slice(tmp_path, ["B001", "B002", "B003"])

    result = build_catalyst_field_package_slice_preflight(
        source_dir=tmp_path,
        external_slice_supplied=True,
    )

    assert result["slice_status"] == "catalyst_field_package_slice_ready_for_r7_package_patch_candidate"
    assert result["slice_preflight_pass"] is True
    assert result["matched_batch_count"] == 3
    assert result["matched_batch_ids"] == ["B001", "B002", "B003"]
    assert result["sensor_audit"]["sensor_coverage_pass"] is True
    assert result["lab_audit"]["catalyst_activity_label_pass"] is True
    assert result["operation_audit"]["regeneration_event_pass"] is True
    assert result["geometry_audit"]["geometry_coverage_pass"] is True
    assert result["can_route_to_r7_field_package_patch_candidate"] is True
    assert result["can_route_to_agent51_field_proxy_holdout"] is False
    assert result["can_relax_agent49_catalyst_uncertainty_block"] is False
    assert "cannot replace the complete field package" in result["field_boundary"]


def test_catalyst_field_package_slice_blocks_when_batch_alignment_is_incomplete(tmp_path: Path) -> None:
    _write_valid_slice(tmp_path, ["B001", "B002", "B003"])
    _write_table(
        tmp_path / "offline_lab_results.csv",
        TABLE_COLUMNS["offline_lab_results"],
        [_lab_row("B001", 1), _lab_row("B002", 2), _lab_row("B004", 4)],
    )

    result = build_catalyst_field_package_slice_preflight(
        source_dir=tmp_path,
        external_slice_supplied=True,
    )

    assert result["slice_status"] == "catalyst_field_package_slice_blocked_at_batch_alignment"
    assert result["slice_preflight_pass"] is False
    assert result["matched_batch_count"] == 2
    assert "shared_sensor_lab_operation_batch_alignment_failed" in result["blocking_reasons"]
    assert result["can_route_to_r7_field_package_patch_candidate"] is False


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

import csv
from pathlib import Path

from water_ai.field_missingness_replay_package import (
    AVAILABILITY_TABLE,
    LABEL_TABLE,
    QUALITY_TABLE,
    SOURCE_ENV_VAR,
    TABLE_COLUMNS,
    TIME_SINCE_TABLE,
    TIMESERIES_TABLE,
    build_field_missingness_replay_package_preflight,
    write_field_missingness_replay_package_template,
)


def test_field_missingness_replay_package_waits_for_external_dir() -> None:
    preflight = build_field_missingness_replay_package_preflight()

    assert preflight["source_env_var"] == SOURCE_ENV_VAR
    assert preflight["package_status"] == (
        "field_missingness_replay_package_waiting_for_FIELD_MISSINGNESS_REPLAY_PACKAGE_DIR"
    )
    assert preflight["package_preflight_pass"] is False
    assert preflight["can_route_to_agent54_field_missingness_replay"] is False
    assert preflight["can_route_to_soft_sensor_missingness_holdout"] is False
    assert preflight["can_generate_field_evidence"] is False
    assert preflight["can_write_to_actuator"] is False
    assert preflight["can_write_to_release_gate"] is False
    assert "missing_external_package_dir" in preflight["blocking_reasons"]


def test_field_missingness_replay_package_blocks_template_rows(tmp_path: Path) -> None:
    write_field_missingness_replay_package_template(tmp_path)

    preflight = build_field_missingness_replay_package_preflight(
        source_dir=tmp_path,
        external_package_supplied=True,
    )

    assert preflight["package_preflight_pass"] is False
    assert preflight["package_status"] == "field_missingness_replay_package_blocked_at_field_origin"
    assert "template_markers_present" in preflight["blocking_reasons"]
    assert "non_field_rows_present" in preflight["blocking_reasons"]
    assert preflight["matched_sample_count"] == 0


def test_field_missingness_replay_package_accepts_minimum_field_samples(
    tmp_path: Path,
) -> None:
    _write_valid_package(tmp_path)

    preflight = build_field_missingness_replay_package_preflight(
        source_dir=tmp_path,
        external_package_supplied=True,
    )

    assert preflight["package_status"] == (
        "field_missingness_replay_package_ready_for_agent54_missingness_holdout"
    )
    assert preflight["package_preflight_pass"] is True
    assert preflight["matched_sample_count"] == 3
    assert preflight["field_missingness_replay_coverage_candidate"] == 1.0
    assert preflight["unavailable_sample_count"] == 1
    assert preflight["hidden_state_count"] == 3
    assert preflight["mean_sensor_quality_score"] == 0.8
    assert preflight["timeseries_audit"]["valid_row_count"] == 3
    assert preflight["availability_audit"]["valid_row_count"] == 3
    assert preflight["time_since_audit"]["valid_row_count"] == 3
    assert preflight["quality_audit"]["valid_row_count"] == 3
    assert preflight["label_audit"]["valid_row_count"] == 3
    assert preflight["can_route_to_agent54_field_missingness_replay"] is True
    assert preflight["can_route_to_soft_sensor_missingness_holdout"] is True
    assert preflight["can_generate_field_evidence"] is False
    assert preflight["can_write_to_actuator"] is False
    assert preflight["can_write_to_release_gate"] is False
    assert "does not prove field soft-sensor accuracy" in preflight["field_boundary"]


def test_field_missingness_replay_package_blocks_missing_label_table(
    tmp_path: Path,
) -> None:
    _write_valid_package(tmp_path)
    (tmp_path / f"{LABEL_TABLE}.csv").unlink()

    preflight = build_field_missingness_replay_package_preflight(
        source_dir=tmp_path,
        external_package_supplied=True,
    )

    assert preflight["package_preflight_pass"] is False
    assert preflight["package_status"] == "field_missingness_replay_package_blocked_at_schema"
    assert "missing_required_tables" in preflight["blocking_reasons"]
    assert "matched_sample_deficit" in preflight["blocking_reasons"]


def test_field_missingness_replay_package_blocks_all_available_samples(
    tmp_path: Path,
) -> None:
    _write_valid_package(tmp_path, all_available=True)

    preflight = build_field_missingness_replay_package_preflight(
        source_dir=tmp_path,
        external_package_supplied=True,
    )

    assert preflight["package_preflight_pass"] is False
    assert preflight["package_status"] == (
        "field_missingness_replay_package_blocked_at_missingness_events"
    )
    assert "missingness_event_deficit" in preflight["blocking_reasons"]
    assert preflight["matched_sample_count"] == 3
    assert preflight["unavailable_sample_count"] == 0


def _write_valid_package(root: Path, *, all_available: bool = False) -> None:
    sample_ids = ["S001", "S002", "S003"]
    hidden_states = ["matrix_inhibition", "catalyst_activity", "residual_pollutant"]
    _write_csv(
        root / f"{TIMESERIES_TABLE}.csv",
        TABLE_COLUMNS[TIMESERIES_TABLE],
        [
            {
                "sample_id": sample_id,
                "batch_id": f"B{index:03d}",
                "node_id": f"N{index}",
                "modality": ["pH", "UV254", "ORP"][index - 1],
                "timestamp_min": str(index * 10),
                "value": str(7.0 + index * 0.1),
                "qa_flag": "pass",
                "data_origin": "field",
            }
            for index, sample_id in enumerate(sample_ids, start=1)
        ],
    )
    _write_csv(
        root / f"{AVAILABILITY_TABLE}.csv",
        TABLE_COLUMNS[AVAILABILITY_TABLE],
        [
            {
                "sample_id": sample_id,
                "node_id": f"N{index}",
                "modality": ["pH", "UV254", "ORP"][index - 1],
                "is_available": "true" if all_available or index != 2 else "false",
                "missingness_reason": "none" if all_available or index != 2 else "sensor_fouling",
                "mask_source": "sensor_log",
                "qa_flag": "pass",
                "data_origin": "field",
            }
            for index, sample_id in enumerate(sample_ids, start=1)
        ],
    )
    _write_csv(
        root / f"{TIME_SINCE_TABLE}.csv",
        TABLE_COLUMNS[TIME_SINCE_TABLE],
        [
            {
                "sample_id": sample_id,
                "node_id": f"N{index}",
                "modality": ["pH", "UV254", "ORP"][index - 1],
                "time_since_last_observed_min": str(index * 5),
                "sampling_interval_min": "15",
                "expected_next_observed_min": str(index * 10 + 15),
                "qa_flag": "pass",
                "data_origin": "field",
            }
            for index, sample_id in enumerate(sample_ids, start=1)
        ],
    )
    _write_csv(
        root / f"{QUALITY_TABLE}.csv",
        TABLE_COLUMNS[QUALITY_TABLE],
        [
            {
                "sample_id": sample_id,
                "sensor_id": f"sensor_{index}",
                "node_id": f"N{index}",
                "modality": ["pH", "UV254", "ORP"][index - 1],
                "quality_score": str([0.9, 0.7, 0.8][index - 1]),
                "drift_flag": "false",
                "fouling_flag": "true" if index == 2 else "false",
                "calibration_status": "current" if index != 2 else "due",
                "qa_flag": "pass",
                "data_origin": "field",
            }
            for index, sample_id in enumerate(sample_ids, start=1)
        ],
    )
    _write_csv(
        root / f"{LABEL_TABLE}.csv",
        TABLE_COLUMNS[LABEL_TABLE],
        [
            {
                "sample_id": sample_id,
                "batch_id": f"B{index:03d}",
                "hidden_state": hidden_states[index - 1],
                "label_value": str(index * 0.25),
                "label_source": "offline_lab",
                "label_time_min": str(index * 10 + 60),
                "layout_holdout_split": "missingness_holdout",
                "qa_flag": "pass",
                "data_origin": "field",
            }
            for index, sample_id in enumerate(sample_ids, start=1)
        ],
    )


def _write_csv(path: Path, columns: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)

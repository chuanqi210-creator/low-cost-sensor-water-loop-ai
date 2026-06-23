from __future__ import annotations

import csv
import math
from pathlib import Path
from typing import Any


PACKAGE_ID = "R8u153_field_missingness_replay_package_preflight"
SOURCE_ENV_VAR = "FIELD_MISSINGNESS_REPLAY_PACKAGE_DIR"
MINIMUM_MATCHED_SAMPLE_COUNT = 3

TIMESERIES_TABLE = "node_modality_time_series"
AVAILABILITY_TABLE = "availability_mask"
TIME_SINCE_TABLE = "time_since_last_observed_min"
QUALITY_TABLE = "sensor_quality_status"
LABEL_TABLE = "offline_hidden_state_labels"

REQUIRED_TABLES = (
    TIMESERIES_TABLE,
    AVAILABILITY_TABLE,
    TIME_SINCE_TABLE,
    QUALITY_TABLE,
    LABEL_TABLE,
)

TABLE_COLUMNS = {
    TIMESERIES_TABLE: [
        "sample_id",
        "batch_id",
        "node_id",
        "modality",
        "timestamp_min",
        "value",
        "qa_flag",
        "data_origin",
    ],
    AVAILABILITY_TABLE: [
        "sample_id",
        "node_id",
        "modality",
        "is_available",
        "missingness_reason",
        "mask_source",
        "qa_flag",
        "data_origin",
    ],
    TIME_SINCE_TABLE: [
        "sample_id",
        "node_id",
        "modality",
        "time_since_last_observed_min",
        "sampling_interval_min",
        "expected_next_observed_min",
        "qa_flag",
        "data_origin",
    ],
    QUALITY_TABLE: [
        "sample_id",
        "sensor_id",
        "node_id",
        "modality",
        "quality_score",
        "drift_flag",
        "fouling_flag",
        "calibration_status",
        "qa_flag",
        "data_origin",
    ],
    LABEL_TABLE: [
        "sample_id",
        "batch_id",
        "hidden_state",
        "label_value",
        "label_source",
        "label_time_min",
        "layout_holdout_split",
        "qa_flag",
        "data_origin",
    ],
}

ACCEPTED_QA_FLAGS = {"pass", "passed", "valid", "ok", "qc_pass", "qualified", "合格"}
ACCEPTED_SPLITS = {"train", "calibration", "validation", "test", "holdout", "field_holdout", "missingness_holdout"}


def build_field_missingness_replay_package_template(
    sample_ids: list[str] | None = None,
) -> dict[str, Any]:
    ids = sample_ids or ["TODO_sample_id_1", "TODO_sample_id_2", "TODO_sample_id_3"]
    tables = {
        TIMESERIES_TABLE: {
            "columns": TABLE_COLUMNS[TIMESERIES_TABLE],
            "rows": [_timeseries_template_row(sample_id, index) for index, sample_id in enumerate(ids, start=1)],
        },
        AVAILABILITY_TABLE: {
            "columns": TABLE_COLUMNS[AVAILABILITY_TABLE],
            "rows": [_availability_template_row(sample_id) for sample_id in ids],
        },
        TIME_SINCE_TABLE: {
            "columns": TABLE_COLUMNS[TIME_SINCE_TABLE],
            "rows": [_time_since_template_row(sample_id) for sample_id in ids],
        },
        QUALITY_TABLE: {
            "columns": TABLE_COLUMNS[QUALITY_TABLE],
            "rows": [_quality_template_row(sample_id) for sample_id in ids],
        },
        LABEL_TABLE: {
            "columns": TABLE_COLUMNS[LABEL_TABLE],
            "rows": [_label_template_row(sample_id, index) for index, sample_id in enumerate(ids, start=1)],
        },
    }
    return {
        "package_id": PACKAGE_ID,
        "package_type": "field_missingness_replay_package_template",
        "source_env_var": SOURCE_ENV_VAR,
        "required_table_count": len(REQUIRED_TABLES),
        "required_tables": list(REQUIRED_TABLES),
        "minimum_matched_sample_count": MINIMUM_MATCHED_SAMPLE_COUNT,
        "tables": tables,
        "table_row_counts": {name: len(table["rows"]) for name, table in tables.items()},
        "operator_instructions": [
            "Fill TODO values with real field missingness replay rows.",
            "Use at least three shared sample_id values across all five tables.",
            "Use data_origin=field for every row.",
            "Include at least one unavailable/missing sample; all-available rows cannot test missingness robustness.",
            "Passing this preflight only routes data to soft-sensor missingness replay; it never creates field performance claims by itself.",
        ],
        "no_write_boundary": _no_write_boundary(),
    }


def write_field_missingness_replay_package_template(target_dir: str | Path) -> dict[str, Any]:
    target = Path(target_dir)
    target.mkdir(parents=True, exist_ok=True)
    template = build_field_missingness_replay_package_template()
    for table_name, table in template["tables"].items():
        _write_csv(target / f"{table_name}.csv", table["columns"], table["rows"])
    return template


def build_field_missingness_replay_package_preflight(
    *,
    source_dir: str | Path | None = None,
    external_package_supplied: bool = False,
) -> dict[str, Any]:
    source = Path(source_dir) if source_dir not in (None, "") else None
    if not external_package_supplied or source is None:
        return _preflight_payload(
            source_path="" if source is None else str(source),
            external_package_supplied=False,
            package_status="field_missingness_replay_package_waiting_for_FIELD_MISSINGNESS_REPLAY_PACKAGE_DIR",
            table_audits={},
            timeseries_audit=_empty_signal_audit("node_modality_time_series"),
            availability_audit=_empty_signal_audit("availability_mask"),
            time_since_audit=_empty_signal_audit("time_since_last_observed"),
            quality_audit=_empty_signal_audit("sensor_quality_status"),
            label_audit=_empty_signal_audit("offline_hidden_state_label"),
            matched_sample_ids=[],
            blocking_reasons=["missing_external_package_dir"],
        )
    if not source.exists() or not source.is_dir():
        return _preflight_payload(
            source_path=str(source),
            external_package_supplied=True,
            package_status="field_missingness_replay_package_blocked_at_missing_source_dir",
            table_audits={},
            timeseries_audit=_empty_signal_audit("node_modality_time_series"),
            availability_audit=_empty_signal_audit("availability_mask"),
            time_since_audit=_empty_signal_audit("time_since_last_observed"),
            quality_audit=_empty_signal_audit("sensor_quality_status"),
            label_audit=_empty_signal_audit("offline_hidden_state_label"),
            matched_sample_ids=[],
            blocking_reasons=["source_dir_missing_or_not_directory"],
        )

    tables, table_audits = _read_tables(source)
    missing_tables = [name for name in REQUIRED_TABLES if not table_audits[name]["file_exists"]]
    header_gaps = [
        {"table": name, "missing_columns": audit["missing_columns"]}
        for name, audit in table_audits.items()
        if audit["missing_columns"]
    ]
    template_marker_count = sum(int(audit["template_marker_count"]) for audit in table_audits.values())
    non_field_row_count = sum(int(audit["non_field_row_count"]) for audit in table_audits.values())

    timeseries_audit = _timeseries_audit(tables.get(TIMESERIES_TABLE, []))
    availability_audit = _availability_audit(tables.get(AVAILABILITY_TABLE, []))
    time_since_audit = _time_since_audit(tables.get(TIME_SINCE_TABLE, []))
    quality_audit = _quality_audit(tables.get(QUALITY_TABLE, []))
    label_audit = _label_audit(tables.get(LABEL_TABLE, []))
    matched_sample_ids = sorted(
        set(timeseries_audit["valid_sample_ids"])
        & set(availability_audit["valid_sample_ids"])
        & set(time_since_audit["valid_sample_ids"])
        & set(quality_audit["valid_sample_ids"])
        & set(label_audit["valid_sample_ids"])
    )
    blocking_reasons = _blocking_reasons(
        missing_tables=missing_tables,
        header_gaps=header_gaps,
        template_marker_count=template_marker_count,
        non_field_row_count=non_field_row_count,
        timeseries_audit=timeseries_audit,
        availability_audit=availability_audit,
        time_since_audit=time_since_audit,
        quality_audit=quality_audit,
        label_audit=label_audit,
        matched_sample_ids=matched_sample_ids,
    )
    return _preflight_payload(
        source_path=str(source),
        external_package_supplied=True,
        package_status=_package_status(blocking_reasons),
        table_audits=table_audits,
        timeseries_audit=timeseries_audit,
        availability_audit=availability_audit,
        time_since_audit=time_since_audit,
        quality_audit=quality_audit,
        label_audit=label_audit,
        matched_sample_ids=matched_sample_ids,
        blocking_reasons=blocking_reasons,
    )


def _preflight_payload(
    *,
    source_path: str,
    external_package_supplied: bool,
    package_status: str,
    table_audits: dict[str, dict[str, Any]],
    timeseries_audit: dict[str, Any],
    availability_audit: dict[str, Any],
    time_since_audit: dict[str, Any],
    quality_audit: dict[str, Any],
    label_audit: dict[str, Any],
    matched_sample_ids: list[str],
    blocking_reasons: list[str],
) -> dict[str, Any]:
    preflight_pass = external_package_supplied and not blocking_reasons
    coverage = round(min(1.0, len(matched_sample_ids) / MINIMUM_MATCHED_SAMPLE_COUNT), 3)
    return {
        "package_id": PACKAGE_ID,
        "package_type": "field_missingness_replay_package_preflight",
        "source_env_var": SOURCE_ENV_VAR,
        "source_path": source_path,
        "external_package_supplied": external_package_supplied,
        "package_status": package_status,
        "package_preflight_pass": preflight_pass,
        "required_table_count": len(REQUIRED_TABLES),
        "required_tables": list(REQUIRED_TABLES),
        "minimum_matched_sample_count": MINIMUM_MATCHED_SAMPLE_COUNT,
        "matched_sample_count": len(matched_sample_ids),
        "matched_sample_ids": matched_sample_ids,
        "field_missingness_replay_coverage_candidate": coverage,
        "unavailable_sample_count": int(availability_audit.get("unavailable_sample_count", 0) or 0),
        "mean_sensor_quality_score": quality_audit.get("mean_quality_score"),
        "hidden_state_count": int(label_audit.get("hidden_state_count", 0) or 0),
        "table_audits": table_audits,
        "timeseries_audit": timeseries_audit,
        "availability_audit": availability_audit,
        "time_since_audit": time_since_audit,
        "quality_audit": quality_audit,
        "label_audit": label_audit,
        "blocking_reasons": blocking_reasons,
        "can_route_to_agent54_field_missingness_replay": preflight_pass,
        "can_route_to_soft_sensor_missingness_holdout": preflight_pass,
        "can_generate_field_evidence": False,
        "can_resume_model_chain": False,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
        "next_operator_action": _next_operator_action(package_status),
        "field_boundary": (
            "This preflight only checks whether an external field missingness replay package is "
            "ready for soft-sensor missingness holdout work. Passing this gate does not prove "
            "field soft-sensor accuracy, authorize release decisions, or relax actuator guardrails."
        ),
        "no_write_boundary": _no_write_boundary(),
    }


def _read_tables(source: Path) -> tuple[dict[str, list[dict[str, str]]], dict[str, dict[str, Any]]]:
    tables: dict[str, list[dict[str, str]]] = {}
    audits: dict[str, dict[str, Any]] = {}
    for table_name in REQUIRED_TABLES:
        path = source / f"{table_name}.csv"
        required_columns = TABLE_COLUMNS[table_name]
        if not path.exists():
            audits[table_name] = {
                "file_exists": False,
                "row_count": 0,
                "missing_columns": required_columns,
                "template_marker_count": 0,
                "non_field_row_count": 0,
            }
            tables[table_name] = []
            continue
        rows, headers = _read_csv(path)
        audits[table_name] = {
            "file_exists": True,
            "row_count": len(rows),
            "missing_columns": [column for column in required_columns if column not in headers],
            "template_marker_count": sum(_row_has_template_marker(row) for row in rows),
            "non_field_row_count": sum(
                1 for row in rows if _normalize(row.get("data_origin")) != "field"
            ),
        }
        tables[table_name] = rows
    return tables, audits


def _timeseries_audit(rows: list[dict[str, str]]) -> dict[str, Any]:
    valid_ids = []
    nodes = set()
    modalities = set()
    for row in rows:
        if not _row_common_valid(row):
            continue
        sample_id = str(row.get("sample_id", "")).strip()
        timestamp = _float(row.get("timestamp_min"))
        value = _float(row.get("value"))
        if timestamp is None or value is None or timestamp < 0:
            continue
        if any(not str(row.get(column, "")).strip() for column in ["batch_id", "node_id", "modality"]):
            continue
        valid_ids.append(sample_id)
        nodes.add(str(row.get("node_id", "")).strip())
        modalities.add(str(row.get("modality", "")).strip())
    return {
        "signal_family": "node_modality_time_series",
        "row_count": len(rows),
        "valid_row_count": len(valid_ids),
        "valid_sample_ids": sorted(set(valid_ids)),
        "node_count": len(nodes),
        "modality_count": len(modalities),
        "modalities": sorted(modalities),
    }


def _availability_audit(rows: list[dict[str, str]]) -> dict[str, Any]:
    valid_ids = []
    unavailable_ids = []
    reasons = set()
    for row in rows:
        if not _row_common_valid(row):
            continue
        sample_id = str(row.get("sample_id", "")).strip()
        available = _bool(row.get("is_available"))
        if available is None:
            continue
        if any(
            not str(row.get(column, "")).strip()
            for column in ["node_id", "modality", "missingness_reason", "mask_source"]
        ):
            continue
        valid_ids.append(sample_id)
        reason = str(row.get("missingness_reason", "")).strip()
        reasons.add(reason)
        if not available:
            unavailable_ids.append(sample_id)
    return {
        "signal_family": "availability_mask",
        "row_count": len(rows),
        "valid_row_count": len(valid_ids),
        "valid_sample_ids": sorted(set(valid_ids)),
        "unavailable_sample_ids": sorted(set(unavailable_ids)),
        "unavailable_sample_count": len(set(unavailable_ids)),
        "missingness_reasons": sorted(reasons),
    }


def _time_since_audit(rows: list[dict[str, str]]) -> dict[str, Any]:
    valid_ids = []
    times = []
    intervals = []
    for row in rows:
        if not _row_common_valid(row):
            continue
        sample_id = str(row.get("sample_id", "")).strip()
        time_since = _float(row.get("time_since_last_observed_min"))
        interval = _float(row.get("sampling_interval_min"))
        next_observed = _float(row.get("expected_next_observed_min"))
        if (
            time_since is None
            or interval is None
            or next_observed is None
            or time_since < 0
            or interval <= 0
            or next_observed < 0
        ):
            continue
        if any(not str(row.get(column, "")).strip() for column in ["node_id", "modality"]):
            continue
        valid_ids.append(sample_id)
        times.append(time_since)
        intervals.append(interval)
    return {
        "signal_family": "time_since_last_observed",
        "row_count": len(rows),
        "valid_row_count": len(valid_ids),
        "valid_sample_ids": sorted(set(valid_ids)),
        "mean_time_since_last_observed_min": round(sum(times) / len(times), 3) if times else None,
        "mean_sampling_interval_min": round(sum(intervals) / len(intervals), 3) if intervals else None,
    }


def _quality_audit(rows: list[dict[str, str]]) -> dict[str, Any]:
    valid_ids = []
    quality_scores = []
    drift_count = 0
    fouling_count = 0
    calibration_statuses = set()
    for row in rows:
        if not _row_common_valid(row):
            continue
        sample_id = str(row.get("sample_id", "")).strip()
        quality = _float(row.get("quality_score"))
        drift = _bool(row.get("drift_flag"))
        fouling = _bool(row.get("fouling_flag"))
        calibration_status = str(row.get("calibration_status", "")).strip()
        if quality is None or not 0 <= quality <= 1 or drift is None or fouling is None:
            continue
        if any(
            not str(row.get(column, "")).strip()
            for column in ["sensor_id", "node_id", "modality", "calibration_status"]
        ):
            continue
        valid_ids.append(sample_id)
        quality_scores.append(quality)
        calibration_statuses.add(calibration_status)
        if drift:
            drift_count += 1
        if fouling:
            fouling_count += 1
    return {
        "signal_family": "sensor_quality_status",
        "row_count": len(rows),
        "valid_row_count": len(valid_ids),
        "valid_sample_ids": sorted(set(valid_ids)),
        "mean_quality_score": round(sum(quality_scores) / len(quality_scores), 3) if quality_scores else None,
        "drift_flag_count": drift_count,
        "fouling_flag_count": fouling_count,
        "calibration_statuses": sorted(calibration_statuses),
    }


def _label_audit(rows: list[dict[str, str]]) -> dict[str, Any]:
    valid_ids = []
    hidden_states = set()
    splits = set()
    for row in rows:
        if not _row_common_valid(row):
            continue
        sample_id = str(row.get("sample_id", "")).strip()
        label_value = _float(row.get("label_value"))
        label_time = _float(row.get("label_time_min"))
        split = _normalize(row.get("layout_holdout_split"))
        if (
            label_value is None
            or label_time is None
            or label_time < 0
            or split not in ACCEPTED_SPLITS
        ):
            continue
        if any(
            not str(row.get(column, "")).strip()
            for column in ["batch_id", "hidden_state", "label_source"]
        ):
            continue
        valid_ids.append(sample_id)
        hidden_states.add(str(row.get("hidden_state", "")).strip())
        splits.add(split)
    return {
        "signal_family": "offline_hidden_state_label",
        "row_count": len(rows),
        "valid_row_count": len(valid_ids),
        "valid_sample_ids": sorted(set(valid_ids)),
        "hidden_state_count": len(hidden_states),
        "hidden_states": sorted(hidden_states),
        "layout_holdout_splits": sorted(splits),
    }


def _blocking_reasons(
    *,
    missing_tables: list[str],
    header_gaps: list[dict[str, Any]],
    template_marker_count: int,
    non_field_row_count: int,
    timeseries_audit: dict[str, Any],
    availability_audit: dict[str, Any],
    time_since_audit: dict[str, Any],
    quality_audit: dict[str, Any],
    label_audit: dict[str, Any],
    matched_sample_ids: list[str],
) -> list[str]:
    reasons: list[str] = []
    if missing_tables:
        reasons.append("missing_required_tables")
    if header_gaps:
        reasons.append("missing_required_columns")
    if template_marker_count > 0:
        reasons.append("template_markers_present")
    if non_field_row_count > 0:
        reasons.append("non_field_rows_present")
    signal_requirements = [
        ("insufficient_node_modality_timeseries_rows", timeseries_audit),
        ("insufficient_availability_mask_rows", availability_audit),
        ("insufficient_time_since_observed_rows", time_since_audit),
        ("insufficient_sensor_quality_rows", quality_audit),
        ("insufficient_offline_hidden_state_label_rows", label_audit),
    ]
    for reason, audit in signal_requirements:
        if int(audit.get("valid_row_count", 0) or 0) < MINIMUM_MATCHED_SAMPLE_COUNT:
            reasons.append(reason)
    if int(availability_audit.get("unavailable_sample_count", 0) or 0) < 1:
        reasons.append("missingness_event_deficit")
    if len(matched_sample_ids) < MINIMUM_MATCHED_SAMPLE_COUNT:
        reasons.append("matched_sample_deficit")
    return reasons


def _package_status(blocking_reasons: list[str]) -> str:
    if not blocking_reasons:
        return "field_missingness_replay_package_ready_for_agent54_missingness_holdout"
    if "missing_required_tables" in blocking_reasons or "missing_required_columns" in blocking_reasons:
        return "field_missingness_replay_package_blocked_at_schema"
    if "template_markers_present" in blocking_reasons or "non_field_rows_present" in blocking_reasons:
        return "field_missingness_replay_package_blocked_at_field_origin"
    if "missingness_event_deficit" in blocking_reasons:
        return "field_missingness_replay_package_blocked_at_missingness_events"
    if "matched_sample_deficit" in blocking_reasons:
        return "field_missingness_replay_package_blocked_at_sample_alignment"
    return "field_missingness_replay_package_blocked_at_content_preflight"


def _next_operator_action(package_status: str) -> str:
    if package_status == "field_missingness_replay_package_ready_for_agent54_missingness_holdout":
        return "route_FIELD_MISSINGNESS_REPLAY_PACKAGE_DIR_to_Agent54_field_missingness_holdout_consumer"
    if package_status == "field_missingness_replay_package_blocked_at_missing_source_dir":
        return "repair_FIELD_MISSINGNESS_REPLAY_PACKAGE_DIR_path"
    if package_status == "field_missingness_replay_package_blocked_at_schema":
        return "repair_FIELD_MISSINGNESS_REPLAY_PACKAGE_csv_headers_and_required_tables"
    if package_status == "field_missingness_replay_package_blocked_at_field_origin":
        return "replace_template_or_non_field_missingness_rows_with_real_field_rows"
    if package_status == "field_missingness_replay_package_blocked_at_missingness_events":
        return "add_at_least_one_real_unavailable_or_missing_sensor_sample"
    if package_status == "field_missingness_replay_package_blocked_at_sample_alignment":
        return "add_at_least_three_shared_sample_ids_across_all_missingness_replay_tables"
    return "fill_field_missingness_replay_package_template_and_set_FIELD_MISSINGNESS_REPLAY_PACKAGE_DIR"


def _empty_signal_audit(signal_family: str) -> dict[str, Any]:
    return {
        "signal_family": signal_family,
        "row_count": 0,
        "valid_row_count": 0,
        "valid_sample_ids": [],
    }


def _row_common_valid(row: dict[str, str]) -> bool:
    sample_id = str(row.get("sample_id", "")).strip()
    if not sample_id or "TODO" in sample_id:
        return False
    return _normalize(row.get("qa_flag")) in ACCEPTED_QA_FLAGS and _normalize(
        row.get("data_origin")
    ) == "field"


def _read_csv(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = [dict(row) for row in reader]
        return rows, list(reader.fieldnames or [])


def _write_csv(path: Path, columns: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def _row_has_template_marker(row: dict[str, str]) -> bool:
    return any(_has_template_marker(value) for value in row.values())


def _has_template_marker(value: object) -> bool:
    text = str(value or "").strip().lower()
    return not text or "todo" in text or "template" in text or "placeholder" in text


def _float(value: object) -> float | None:
    try:
        parsed = float(str(value).strip())
    except (TypeError, ValueError):
        return None
    if not math.isfinite(parsed):
        return None
    return parsed


def _bool(value: object) -> bool | None:
    text = _normalize(value)
    if text in {"true", "1", "yes", "y", "available", "observed", "是"}:
        return True
    if text in {"false", "0", "no", "n", "unavailable", "missing", "lost", "否"}:
        return False
    return None


def _normalize(value: object) -> str:
    return str(value or "").strip().lower()


def _no_write_boundary() -> str:
    return (
        "This package is only a field missingness replay preflight input. It cannot write "
        "soft-sensor field performance claims, actuator policy, release-gate policy or "
        "deployment clearance."
    )


def _timeseries_template_row(sample_id: str, index: int) -> dict[str, str]:
    return {
        "sample_id": sample_id,
        "batch_id": f"TODO_batch_{index}",
        "node_id": "TODO_node_id",
        "modality": "TODO_pH_ORP_UV254_turbidity_conductivity_flow_temperature",
        "timestamp_min": "TODO_numeric",
        "value": "TODO_numeric",
        "qa_flag": "TODO_pass",
        "data_origin": "TODO_field",
    }


def _availability_template_row(sample_id: str) -> dict[str, str]:
    return {
        "sample_id": sample_id,
        "node_id": "TODO_node_id",
        "modality": "TODO_modality",
        "is_available": "TODO_true_or_false",
        "missingness_reason": "TODO_low_frequency_sampling_fouling_communication_or_none",
        "mask_source": "TODO_sensor_log_or_operator_log",
        "qa_flag": "TODO_pass",
        "data_origin": "TODO_field",
    }


def _time_since_template_row(sample_id: str) -> dict[str, str]:
    return {
        "sample_id": sample_id,
        "node_id": "TODO_node_id",
        "modality": "TODO_modality",
        "time_since_last_observed_min": "TODO_numeric",
        "sampling_interval_min": "TODO_numeric",
        "expected_next_observed_min": "TODO_numeric",
        "qa_flag": "TODO_pass",
        "data_origin": "TODO_field",
    }


def _quality_template_row(sample_id: str) -> dict[str, str]:
    return {
        "sample_id": sample_id,
        "sensor_id": "TODO_sensor_id",
        "node_id": "TODO_node_id",
        "modality": "TODO_modality",
        "quality_score": "TODO_0_to_1",
        "drift_flag": "TODO_true_or_false",
        "fouling_flag": "TODO_true_or_false",
        "calibration_status": "TODO_current_due_overdue_or_failed",
        "qa_flag": "TODO_pass",
        "data_origin": "TODO_field",
    }


def _label_template_row(sample_id: str, index: int) -> dict[str, str]:
    return {
        "sample_id": sample_id,
        "batch_id": f"TODO_batch_{index}",
        "hidden_state": "TODO_residual_pollutant_or_catalyst_activity_or_matrix_inhibition",
        "label_value": "TODO_numeric",
        "label_source": "TODO_offline_lab_or_operator_review",
        "label_time_min": "TODO_numeric",
        "layout_holdout_split": "TODO_missingness_holdout",
        "qa_flag": "TODO_pass",
        "data_origin": "TODO_field",
    }

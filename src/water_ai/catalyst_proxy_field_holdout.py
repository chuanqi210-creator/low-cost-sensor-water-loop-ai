from __future__ import annotations

import csv
from math import log
from pathlib import Path
from typing import Any

from water_ai.agents.field_replay_import_agent import FieldReplayImportAgent


REQUIRED_NODE_SIGNALS = {
    "N3_catalyst_bed_outlet:UV254_abs": ("N3_catalyst_bed_outlet", "UV254_abs"),
    "N3_catalyst_bed_outlet:ORP_mV": ("N3_catalyst_bed_outlet", "ORP_mV"),
    "N3_catalyst_bed:pressure_drop_kPa": ("N3_catalyst_bed", "pressure_drop_kPa"),
}
FIELD_PROXY_HOLDOUT_MINIMUM_BATCHES = 3
MIN_FIELD_CORRELATION = 0.68
MAX_FIELD_MAE = 0.16
EXPECTED_CATALYST_RATE_PER_MIN = 0.05
PRESSURE_DROP_REFERENCE_KPA = 12.0
PRESSURE_SOURCE_CONFLICT_ABS_TOLERANCE_KPA = 1.0
PRESSURE_SOURCE_CONFLICT_REL_TOLERANCE = 0.25
PRESSURE_SOURCE_RESOLUTION_FIELDS = [
    "pressure_source_resolution",
    "authoritative_pressure_source",
    "reviewer_id",
    "review_time",
    "calibration_action_id",
    "calibration_note",
]
PRESSURE_SOURCE_RESOLUTION_TOKENS = {
    "accepted",
    "calibrated",
    "confirmed",
    "operator_reviewed",
    "resolved",
    "reviewed",
    "source_selected",
}
PRESSURE_SOURCE_ALIASES = {
    "node": "node_modality_sensor_timeseries",
    "node_modality": "node_modality_sensor_timeseries",
    "node_modality_sensor": "node_modality_sensor_timeseries",
    "node_modality_sensor_timeseries": "node_modality_sensor_timeseries",
    "pressure_event": "pressure_headloss_event_log",
    "pressure_headloss": "pressure_headloss_event_log",
    "pressure_headloss_event": "pressure_headloss_event_log",
    "pressure_headloss_event_log": "pressure_headloss_event_log",
}
ACCEPTED_SENSOR_STATUS = {"ok", "pass", "passed", "valid", "calibrated", "normal", "qualified", "合格", "正常"}
ACCEPTED_LAB_QA_FLAGS = {"pass", "passed", "valid", "ok", "qc_pass", "qualified", "合格"}


def build_catalyst_proxy_field_holdout_summary(
    package_dir: str | Path,
    *,
    minimum_batches: int = FIELD_PROXY_HOLDOUT_MINIMUM_BATCHES,
    min_field_correlation: float = MIN_FIELD_CORRELATION,
    max_field_mae: float = MAX_FIELD_MAE,
) -> dict[str, Any]:
    """Extract Agent51 catalyst proxy holdout rows from a field replay package.

    The summary is deliberately conservative: a ready summary means the package can
    score Agent51 proxy rows against catalyst_activity labels. It does not by itself
    authorize actuator or release-gate writeback.
    """

    root = Path(package_dir)
    rows_by_table = {table: _read_csv(root / f"{table}.csv") for table in _required_tables()}
    rows_by_table["pressure_headloss_event_log"] = _read_csv(root / "pressure_headloss_event_log.csv")
    missing_tables = [
        table
        for table, rows in rows_by_table.items()
        if table not in {"sensor_timeseries", "pressure_headloss_event_log"} and not (root / f"{table}.csv").exists()
    ]
    primary_context = _primary_sensor_context(rows_by_table["sensor_timeseries"])
    signal_values, signal_invalid_rows = _node_signal_values(rows_by_table["node_modality_sensor_timeseries"])
    pressure_signal_values, pressure_invalid_rows = _pressure_headloss_signal_values(
        rows_by_table["pressure_headloss_event_log"]
    )
    pressure_resolution_audit = _pressure_source_resolution_records(rows_by_table)
    pressure_source_by_batch, pressure_source_conflicts, unresolved_pressure_source_conflicts, pressure_source_resolutions = _merge_pressure_headloss_event_signal(
        signal_values,
        pressure_signal_values,
        pressure_resolution_audit["valid_resolution_by_batch"],
    )
    lab_labels, lab_invalid_rows = _catalyst_activity_labels(rows_by_table["offline_lab_results"])
    operations, operation_invalid_rows = _operation_events(rows_by_table["campaign_operation_log"])
    geometry, geometry_invalid_rows = _bed_geometry(rows_by_table["site_topology_or_bed_geometry"])

    signal_batch_sets = [
        set(signal_values.get(signal, {}))
        for signal in REQUIRED_NODE_SIGNALS
    ]
    all_signal_batches = set.intersection(*signal_batch_sets) if signal_batch_sets else set()
    matched_batches = sorted(all_signal_batches & set(lab_labels) & set(operations))
    feature_rows = [
        _build_feature_row(
            batch_id,
            primary_context=primary_context.get(batch_id, {}),
            signal_values=signal_values,
            lab_labels=lab_labels,
            operations=operations,
            geometry=geometry,
            pressure_source_by_batch=pressure_source_by_batch,
        )
        for batch_id in matched_batches
    ]
    scoreable_rows = [row for row in feature_rows if row["score_status"] == "scoreable"]
    proxy_scores = [float(row["catalyst_activity_proxy_score"]) for row in scoreable_rows]
    labels = [float(row["catalyst_activity_label"]) for row in scoreable_rows]
    errors = [abs(score - label) for score, label in zip(proxy_scores, labels, strict=True)]
    correlation = _correlation(proxy_scores, labels)
    holdout_mae = round(sum(errors) / max(1, len(errors)), 3) if errors else 1.0
    field_label_coverage = round(len(scoreable_rows) / max(1, len(matched_batches)), 3)
    ready_for_validation = len(scoreable_rows) >= minimum_batches
    validation_pass = (
        ready_for_validation
        and field_label_coverage >= 0.75
        and correlation >= min_field_correlation
        and holdout_mae <= max_field_mae
    )
    status = _summary_status(
        missing_tables=missing_tables,
        matched_batch_count=len(matched_batches),
        scoreable_batch_count=len(scoreable_rows),
        validation_pass=validation_pass,
        minimum_batches=minimum_batches,
    )
    missing_signals = [
        signal
        for signal in REQUIRED_NODE_SIGNALS
        if len(signal_values.get(signal, {})) < minimum_batches
    ]
    return {
        "package_dir": str(root),
        "summary_id": "Agent51_catalyst_proxy_field_holdout_summary",
        "field_proxy_holdout_summary_status": status,
        "source_basis": "field_package_extractor",
        "evidence_stage": "field_proxy_holdout_candidate",
        "minimum_batch_count": minimum_batches,
        "missing_required_tables": missing_tables,
        "missing_required_signals": missing_signals,
        "matched_batch_count": len(matched_batches),
        "matched_batch_ids_sample": matched_batches[:8],
        "scoreable_batch_count": len(scoreable_rows),
        "ready_for_agent51_validation": ready_for_validation,
        "field_validation_pass": validation_pass,
        "field_validation_metrics": {
            "field_label_coverage": field_label_coverage,
            "proxy_label_correlation": correlation,
            "holdout_mae": holdout_mae,
            "scoreable_batch_count": len(scoreable_rows),
            "matched_batch_count": len(matched_batches),
        },
        "required_node_signals": sorted(REQUIRED_NODE_SIGNALS),
        "signal_batch_counts": {
            signal: len(signal_values.get(signal, {}))
            for signal in sorted(REQUIRED_NODE_SIGNALS)
        },
        "accepted_pressure_evidence_sources": _accepted_pressure_evidence_sources(
            signal_values,
            pressure_source_by_batch,
        ),
        "pressure_headloss_event_source_batch_count": sum(
            1 for source in pressure_source_by_batch.values() if source == "pressure_headloss_event_log"
        ),
        "pressure_evidence_source_batch_counts": {
            "node_modality_sensor_timeseries": sum(
                1 for source in pressure_source_by_batch.values() if source == "node_modality_sensor_timeseries"
            ),
            "pressure_headloss_event_log": sum(
                1 for source in pressure_source_by_batch.values() if source == "pressure_headloss_event_log"
            ),
            "source_conflict_requires_operator_review": sum(
                1 for source in pressure_source_by_batch.values() if source == "source_conflict_requires_operator_review"
            ),
        },
        "pressure_source_priority_policy": (
            "Use node_modality_sensor_timeseries pressure_drop_kPa when available, fill missing pressure from "
            "pressure_headloss_event_log, and block scoreability when both sources conflict beyond tolerance."
        ),
        "pressure_source_conflict_count": len(pressure_source_conflicts),
        "pressure_source_conflicts": pressure_source_conflicts[:12],
        "resolved_pressure_source_conflict_count": len(pressure_source_resolutions),
        "unresolved_pressure_source_conflict_count": len(unresolved_pressure_source_conflicts),
        "unresolved_pressure_source_conflicts": unresolved_pressure_source_conflicts[:12],
        "pressure_source_resolutions": pressure_source_resolutions[:12],
        "pressure_source_resolution_record_count": pressure_resolution_audit["valid_resolution_count"],
        "pressure_source_resolution_invalid_rows": pressure_resolution_audit["invalid_resolution_rows"],
        "pressure_source_conflict_abs_tolerance_kPa": PRESSURE_SOURCE_CONFLICT_ABS_TOLERANCE_KPA,
        "pressure_source_conflict_rel_tolerance": PRESSURE_SOURCE_CONFLICT_REL_TOLERANCE,
        "conflict_requires_operator_review": bool(unresolved_pressure_source_conflicts),
        "lab_label_batch_count": len(lab_labels),
        "operation_event_batch_count": len(operations),
        "bed_geometry_available": bool(geometry),
        "feature_rows": feature_rows,
        "invalid_rows": {
            "node_modality_sensor_timeseries": signal_invalid_rows[:12],
            "pressure_headloss_event_log": pressure_invalid_rows[:12],
            "pressure_source_resolution": pressure_resolution_audit["invalid_resolution_rows"],
            "offline_lab_results": lab_invalid_rows[:12],
            "campaign_operation_log": operation_invalid_rows[:12],
            "site_topology_or_bed_geometry": geometry_invalid_rows[:12],
        },
        "boundary": (
            "This summary only turns an R7j-ready package into Agent51 validation rows. "
            "It does not prove field-supported control, write actuators or write release gates."
        ),
        "can_relax_agent49_catalyst_uncertainty_block": validation_pass,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
    }


def _required_tables() -> list[str]:
    return [
        "sensor_timeseries",
        "node_modality_sensor_timeseries",
        "offline_lab_results",
        "campaign_operation_log",
        "site_topology_or_bed_geometry",
    ]


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def _primary_sensor_context(rows: list[dict[str, str]]) -> dict[str, dict[str, float]]:
    context: dict[str, dict[str, float]] = {}
    for row in rows:
        batch_id = str(row.get("batch_id", "")).strip()
        if _is_missing(batch_id) or batch_id in context:
            continue
        parsed: dict[str, float] = {}
        for field in ("UV254_abs", "ORP_mV", "flow_Lmin", "turbidity_NTU", "timestamp_min"):
            value = _optional_number(row.get(field))
            if value is not None:
                parsed[field] = value
        if parsed:
            context[batch_id] = parsed
    return context


def _node_signal_values(
    rows: list[dict[str, str]],
) -> tuple[dict[str, dict[str, float]], list[dict[str, Any]]]:
    values: dict[str, dict[str, list[float]]] = {signal: {} for signal in REQUIRED_NODE_SIGNALS}
    invalid_rows: list[dict[str, Any]] = []
    for index, row in enumerate(rows):
        node_id = str(row.get("node_id", "")).strip()
        modality = str(row.get("modality", "")).strip()
        signal = f"{node_id}:{modality}"
        if signal not in REQUIRED_NODE_SIGNALS:
            continue
        errors: list[dict[str, Any]] = []
        batch_id = str(row.get("batch_id", "")).strip()
        if _is_missing(batch_id):
            errors.append({"field": "batch_id", "error": "missing_batch_id", "value": row.get("batch_id")})
        _, time_error = FieldReplayImportAgent._parse_number(row.get("timestamp_min"))
        if time_error:
            errors.append({"field": "timestamp_min", "error": time_error, "value": row.get("timestamp_min")})
        value, value_error = FieldReplayImportAgent._parse_number(row.get("value"))
        if value_error:
            errors.append({"field": "value", "error": value_error, "value": row.get("value")})
        sensor_status = str(row.get("sensor_status", "")).strip().lower()
        if _is_missing(sensor_status):
            errors.append({"field": "sensor_status", "error": "missing_sensor_status", "value": row.get("sensor_status")})
        elif sensor_status not in ACCEPTED_SENSOR_STATUS:
            errors.append({"field": "sensor_status", "error": "sensor_status_not_accepted", "value": row.get("sensor_status")})
        if errors:
            invalid_rows.append({"row_index": index, "signal": signal, "batch_id": batch_id, "errors": errors})
            continue
        values[signal].setdefault(batch_id, []).append(value)
    averaged = {
        signal: {batch_id: round(sum(items) / len(items), 6) for batch_id, items in batch_values.items()}
        for signal, batch_values in values.items()
    }
    return averaged, invalid_rows


def _pressure_headloss_signal_values(
    rows: list[dict[str, str]],
) -> tuple[dict[str, dict[str, float]], list[dict[str, Any]]]:
    signal = "N3_catalyst_bed:pressure_drop_kPa"
    values: dict[str, list[float]] = {}
    invalid_rows: list[dict[str, Any]] = []
    for index, row in enumerate(rows):
        bed_id = str(row.get("bed_id", "")).strip()
        if bed_id != "N3_catalyst_bed":
            continue
        errors: list[dict[str, Any]] = []
        batch_id = str(row.get("batch_id", "")).strip()
        if _is_missing(batch_id):
            errors.append({"field": "batch_id", "error": "missing_batch_id", "value": row.get("batch_id")})
        pressure_drop, pressure_error = FieldReplayImportAgent._parse_number(row.get("pressure_drop_kPa"))
        if pressure_error:
            errors.append({"field": "pressure_drop_kPa", "error": pressure_error, "value": row.get("pressure_drop_kPa")})
        elif pressure_drop < 0:
            errors.append(
                {"field": "pressure_drop_kPa", "error": "negative_pressure_drop", "value": row.get("pressure_drop_kPa")}
            )
        flow, flow_error = FieldReplayImportAgent._parse_number(row.get("flow_Lmin"))
        if flow_error:
            errors.append({"field": "flow_Lmin", "error": flow_error, "value": row.get("flow_Lmin")})
        elif flow <= 0:
            errors.append({"field": "flow_Lmin", "error": "non_positive_flow", "value": row.get("flow_Lmin")})
        _, label_time_error = FieldReplayImportAgent._parse_number(row.get("matched_lab_sample_time_min"))
        if label_time_error:
            errors.append(
                {
                    "field": "matched_lab_sample_time_min",
                    "error": label_time_error,
                    "value": row.get("matched_lab_sample_time_min"),
                }
            )
        _, anomaly_error = FieldReplayImportAgent._parse_bool(row.get("hydraulic_anomaly_label"))
        if anomaly_error:
            errors.append(
                {
                    "field": "hydraulic_anomaly_label",
                    "error": anomaly_error,
                    "value": row.get("hydraulic_anomaly_label"),
                }
            )
        if errors:
            invalid_rows.append({"row_index": index, "signal": signal, "batch_id": batch_id, "errors": errors})
            continue
        values.setdefault(batch_id, []).append(pressure_drop)
    return {signal: {batch_id: round(sum(items) / len(items), 6) for batch_id, items in values.items()}}, invalid_rows


def _merge_pressure_headloss_event_signal(
    signal_values: dict[str, dict[str, float]],
    pressure_signal_values: dict[str, dict[str, float]],
    pressure_resolution_by_batch: dict[str, Any],
) -> tuple[dict[str, str], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    signal = "N3_catalyst_bed:pressure_drop_kPa"
    signal_values.setdefault(signal, {})
    pressure_source_by_batch = {
        batch_id: "node_modality_sensor_timeseries"
        for batch_id in signal_values.get(signal, {})
    }
    conflicts: list[dict[str, Any]] = []
    unresolved_conflicts: list[dict[str, Any]] = []
    resolutions: list[dict[str, Any]] = []
    for batch_id, value in pressure_signal_values.get(signal, {}).items():
        if batch_id in signal_values[signal]:
            node_value = signal_values[signal][batch_id]
            difference = abs(node_value - value)
            tolerance = max(
                PRESSURE_SOURCE_CONFLICT_ABS_TOLERANCE_KPA,
                PRESSURE_SOURCE_CONFLICT_REL_TOLERANCE * max(abs(node_value), abs(value), 1e-6),
            )
            if difference > tolerance:
                conflict = {
                    "batch_id": batch_id,
                    "node_modality_pressure_drop_kPa": round(node_value, 6),
                    "pressure_headloss_event_pressure_drop_kPa": round(value, 6),
                    "absolute_difference_kPa": round(difference, 6),
                    "conflict_tolerance_kPa": round(tolerance, 6),
                    "action": "operator_review_required_before_agent51_scoring",
                }
                resolution = _dict(pressure_resolution_by_batch.get(batch_id))
                if resolution:
                    authoritative_source = str(resolution.get("authoritative_pressure_source"))
                    if authoritative_source == "pressure_headloss_event_log":
                        signal_values[signal][batch_id] = value
                    else:
                        signal_values[signal][batch_id] = node_value
                    pressure_source_by_batch[batch_id] = authoritative_source
                    resolved = {
                        **conflict,
                        "authoritative_pressure_source": authoritative_source,
                        "pressure_source_resolution": resolution.get("pressure_source_resolution"),
                        "reviewer_id": resolution.get("reviewer_id"),
                        "review_time": resolution.get("review_time"),
                        "calibration_action_id": resolution.get("calibration_action_id"),
                        "calibration_note": resolution.get("calibration_note"),
                        "resolution_source_table": resolution.get("source_table"),
                        "action": "operator_review_resolved_before_agent51_scoring",
                    }
                    conflicts.append(resolved)
                    resolutions.append(resolved)
                    continue
                conflicts.append(conflict)
                unresolved_conflicts.append(conflict)
                signal_values[signal].pop(batch_id, None)
                pressure_source_by_batch[batch_id] = "source_conflict_requires_operator_review"
            continue
        signal_values[signal][batch_id] = value
        pressure_source_by_batch[batch_id] = "pressure_headloss_event_log"
    return pressure_source_by_batch, conflicts, unresolved_conflicts, resolutions


def _pressure_source_resolution_records(rows_by_table: dict[str, list[dict[str, str]]]) -> dict[str, Any]:
    records: dict[str, dict[str, Any]] = {}
    invalid_rows: list[dict[str, Any]] = []
    for table in ("pressure_headloss_event_log", "campaign_operation_log"):
        for index, row in enumerate(rows_by_table.get(table, [])):
            if not any(not _is_missing(row.get(field)) for field in PRESSURE_SOURCE_RESOLUTION_FIELDS):
                continue
            parsed, errors = _parse_pressure_source_resolution_row(row, table, index)
            if errors:
                invalid_rows.append(
                    {
                        "source_table": table,
                        "row_index": index,
                        "batch_id": row.get("batch_id"),
                        "errors": errors,
                    }
                )
                continue
            records.setdefault(str(parsed["batch_id"]), parsed)
    return {
        "required_fields": PRESSURE_SOURCE_RESOLUTION_FIELDS,
        "accepted_resolution_tokens": sorted(PRESSURE_SOURCE_RESOLUTION_TOKENS),
        "accepted_authoritative_sources": sorted({"node_modality_sensor_timeseries", "pressure_headloss_event_log"}),
        "valid_resolution_count": len(records),
        "valid_resolution_batch_ids": sorted(records),
        "valid_resolution_by_batch": records,
        "invalid_resolution_count": len(invalid_rows),
        "invalid_resolution_rows": invalid_rows[:12],
    }


def _parse_pressure_source_resolution_row(
    row: dict[str, str],
    table: str,
    index: int,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    errors: list[dict[str, Any]] = []
    batch_id = row.get("batch_id")
    if _is_missing(batch_id):
        errors.append({"field": "batch_id", "error": "missing_batch_id", "value": batch_id})
    resolution_token = str(row.get("pressure_source_resolution", "")).strip().lower()
    if _is_missing(resolution_token):
        errors.append(
            {
                "field": "pressure_source_resolution",
                "error": "missing_pressure_source_resolution",
                "value": row.get("pressure_source_resolution"),
            }
        )
    elif resolution_token not in PRESSURE_SOURCE_RESOLUTION_TOKENS:
        errors.append(
            {
                "field": "pressure_source_resolution",
                "error": "unsupported_pressure_source_resolution",
                "value": row.get("pressure_source_resolution"),
                "accepted": sorted(PRESSURE_SOURCE_RESOLUTION_TOKENS),
            }
        )
    authoritative_source = _normalize_pressure_source(row.get("authoritative_pressure_source"))
    if authoritative_source is None:
        errors.append(
            {
                "field": "authoritative_pressure_source",
                "error": "unsupported_authoritative_pressure_source",
                "value": row.get("authoritative_pressure_source"),
                "accepted": sorted({"node_modality_sensor_timeseries", "pressure_headloss_event_log"}),
            }
        )
    for field in ("reviewer_id", "review_time", "calibration_action_id", "calibration_note"):
        if _is_missing(row.get(field)):
            errors.append({"field": field, "error": f"missing_{field}", "value": row.get(field)})
    if errors:
        return {}, errors
    return {
        "batch_id": str(batch_id),
        "pressure_source_resolution": resolution_token,
        "authoritative_pressure_source": authoritative_source,
        "reviewer_id": str(row.get("reviewer_id")),
        "review_time": str(row.get("review_time")),
        "calibration_action_id": str(row.get("calibration_action_id")),
        "calibration_note": str(row.get("calibration_note")),
        "source_table": table,
        "row_index": index,
    }, []


def _normalize_pressure_source(value: Any) -> str | None:
    if _is_missing(value):
        return None
    return PRESSURE_SOURCE_ALIASES.get(str(value).strip().lower())


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _accepted_pressure_evidence_sources(
    signal_values: dict[str, dict[str, float]],
    pressure_source_by_batch: dict[str, str],
) -> list[str]:
    sources = {
        source
        for source in pressure_source_by_batch.values()
        if source != "source_conflict_requires_operator_review"
    }
    if signal_values.get("N3_catalyst_bed:pressure_drop_kPa") and not sources:
        sources.add("node_modality_sensor_timeseries")
    return sorted(sources)


def _catalyst_activity_labels(
    rows: list[dict[str, str]],
) -> tuple[dict[str, float], list[dict[str, Any]]]:
    labels: dict[str, list[float]] = {}
    invalid_rows: list[dict[str, Any]] = []
    for index, row in enumerate(rows):
        if str(row.get("analyte", "")).strip() != "catalyst_activity":
            continue
        errors: list[dict[str, Any]] = []
        batch_id = str(row.get("batch_id", "")).strip()
        if _is_missing(batch_id):
            errors.append({"field": "batch_id", "error": "missing_batch_id", "value": row.get("batch_id")})
        value, value_error = FieldReplayImportAgent._parse_number(row.get("value"))
        if value_error:
            errors.append({"field": "value", "error": value_error, "value": row.get("value")})
        _, time_error = FieldReplayImportAgent._parse_number(row.get("lab_label_time_min"))
        if time_error:
            errors.append({"field": "lab_label_time_min", "error": time_error, "value": row.get("lab_label_time_min")})
        qa_flag = str(row.get("qa_flag", "")).strip().lower()
        if _is_missing(qa_flag):
            errors.append({"field": "qa_flag", "error": "missing_qa_flag", "value": row.get("qa_flag")})
        elif qa_flag not in ACCEPTED_LAB_QA_FLAGS:
            errors.append({"field": "qa_flag", "error": "qa_flag_not_pass", "value": row.get("qa_flag")})
        if errors:
            invalid_rows.append({"row_index": index, "batch_id": batch_id, "errors": errors})
            continue
        labels.setdefault(batch_id, []).append(_normalize_activity_label(value))
    averaged = {batch_id: round(sum(items) / len(items), 6) for batch_id, items in labels.items()}
    return averaged, invalid_rows


def _operation_events(
    rows: list[dict[str, str]],
) -> tuple[dict[str, dict[str, Any]], list[dict[str, Any]]]:
    operations: dict[str, dict[str, Any]] = {}
    invalid_rows: list[dict[str, Any]] = []
    for index, row in enumerate(rows):
        errors: list[dict[str, Any]] = []
        batch_id = str(row.get("batch_id", "")).strip()
        if _is_missing(batch_id):
            errors.append({"field": "batch_id", "error": "missing_batch_id", "value": row.get("batch_id")})
        regeneration_event, bool_error = FieldReplayImportAgent._parse_bool(row.get("regeneration_event"))
        if bool_error:
            errors.append({"field": "regeneration_event", "error": bool_error, "value": row.get("regeneration_event")})
        command_time, command_error = FieldReplayImportAgent._parse_number(row.get("command_time_min"))
        if command_error:
            errors.append({"field": "command_time_min", "error": command_error, "value": row.get("command_time_min")})
        effect_time, effect_error = FieldReplayImportAgent._parse_number(row.get("effect_time_min"))
        if effect_error:
            errors.append({"field": "effect_time_min", "error": effect_error, "value": row.get("effect_time_min")})
        if errors:
            invalid_rows.append({"row_index": index, "batch_id": batch_id, "errors": errors})
            continue
        operations.setdefault(
            batch_id,
            {
                "regeneration_event": regeneration_event,
                "command_time_min": command_time,
                "effect_time_min": effect_time,
            },
        )
    return operations, invalid_rows


def _bed_geometry(rows: list[dict[str, str]]) -> tuple[dict[str, float], list[dict[str, Any]]]:
    valid_rows: list[dict[str, float]] = []
    invalid_rows: list[dict[str, Any]] = []
    for index, row in enumerate(rows):
        errors: list[dict[str, Any]] = []
        node_id = str(row.get("node_id", "")).strip()
        if _is_missing(node_id):
            errors.append({"field": "node_id", "error": "missing_node_id", "value": row.get("node_id")})
        parsed: dict[str, float] = {}
        for field in ("bed_volume", "nominal_HRT_min", "flow_Lmin"):
            value, value_error = FieldReplayImportAgent._parse_number(row.get(field))
            if value_error:
                errors.append({"field": field, "error": value_error, "value": row.get(field)})
            elif value <= 0:
                errors.append({"field": field, "error": "non_positive_geometry_value", "value": row.get(field)})
            else:
                parsed[field] = value
        if errors:
            invalid_rows.append({"row_index": index, "node_id": node_id, "errors": errors})
            continue
        parsed["node_priority"] = 0.0 if node_id == "N3_catalyst_bed" else 1.0
        valid_rows.append(parsed)
    if not valid_rows:
        return {}, invalid_rows
    selected = sorted(valid_rows, key=lambda item: item["node_priority"])[0]
    selected.pop("node_priority", None)
    return selected, invalid_rows


def _build_feature_row(
    batch_id: str,
    *,
    primary_context: dict[str, float],
    signal_values: dict[str, dict[str, float]],
    lab_labels: dict[str, float],
    operations: dict[str, dict[str, Any]],
    geometry: dict[str, float],
    pressure_source_by_batch: dict[str, str],
) -> dict[str, Any]:
    uv_in = primary_context.get("UV254_abs")
    uv_out = signal_values["N3_catalyst_bed_outlet:UV254_abs"].get(batch_id)
    orp_in = primary_context.get("ORP_mV")
    orp_out = signal_values["N3_catalyst_bed_outlet:ORP_mV"].get(batch_id)
    pressure_drop = signal_values["N3_catalyst_bed:pressure_drop_kPa"].get(batch_id)
    hrt = geometry.get("nominal_HRT_min")
    label = lab_labels.get(batch_id)
    missing_inputs = [
        name
        for name, value in {
            "sensor_timeseries.UV254_abs": uv_in,
            "N3_catalyst_bed_outlet.UV254_abs": uv_out,
            "sensor_timeseries.ORP_mV": orp_in,
            "N3_catalyst_bed_outlet.ORP_mV": orp_out,
            "N3_catalyst_bed.pressure_drop_kPa": pressure_drop,
            "site_topology_or_bed_geometry.nominal_HRT_min": hrt,
            "offline_lab_results.catalyst_activity": label,
        }.items()
        if value is None
    ]
    row: dict[str, Any] = {
        "batch_id": batch_id,
        "score_status": "scoreable" if not missing_inputs else "not_scoreable_missing_inputs",
        "missing_score_inputs": missing_inputs,
        "catalyst_activity_label": round(float(label), 3) if label is not None else None,
        "regeneration_event": bool(operations.get(batch_id, {}).get("regeneration_event", False)),
        "command_to_effect_delay_min": _operation_delay(operations.get(batch_id, {})),
        "pressure_drop_source": pressure_source_by_batch.get(batch_id),
    }
    if missing_inputs:
        return row
    uv_removal = _clip((uv_in - uv_out) / max(uv_in, 1e-6))
    orp_decay = _clip((orp_in - orp_out) / 180.0)
    pressure_drop_norm = _clip(pressure_drop / PRESSURE_DROP_REFERENCE_KPA)
    rate_score = _clip((-log(max(1e-6, uv_out / max(uv_in, 1e-6))) / max(1.0, hrt)) / EXPECTED_CATALYST_RATE_PER_MIN)
    proxy_score = _clip(
        0.38 * uv_removal
        + 0.18 * orp_decay
        + 0.24 * rate_score
        + 0.20 * (1.0 - pressure_drop_norm)
    )
    row.update(
        {
            "uv254_removal_ratio": round(uv_removal, 3),
            "orp_decay_score": round(orp_decay, 3),
            "pressure_drop_norm": round(pressure_drop_norm, 3),
            "residence_time_normalized_rate_score": round(rate_score, 3),
            "catalyst_activity_proxy_score": round(proxy_score, 3),
            "absolute_proxy_error": round(abs(proxy_score - float(label)), 3),
        }
    )
    return row


def _operation_delay(operation: dict[str, Any]) -> float | None:
    command = operation.get("command_time_min")
    effect = operation.get("effect_time_min")
    if command is None or effect is None:
        return None
    return round(max(0.0, float(effect) - float(command)), 3)


def _summary_status(
    *,
    missing_tables: list[str],
    matched_batch_count: int,
    scoreable_batch_count: int,
    validation_pass: bool,
    minimum_batches: int,
) -> str:
    if missing_tables or matched_batch_count < minimum_batches:
        return "field_proxy_holdout_coverage_gaps"
    if scoreable_batch_count < minimum_batches:
        return "field_proxy_holdout_ready_needs_primary_context"
    if validation_pass:
        return "field_proxy_holdout_validation_passed"
    return "field_proxy_holdout_validation_needs_recalibration"


def _normalize_activity_label(value: float) -> float:
    if value > 1.0 and value <= 100.0:
        return round(value / 100.0, 6)
    return _clip(value)


def _optional_number(value: Any) -> float | None:
    if _is_missing(value):
        return None
    parsed, error = FieldReplayImportAgent._parse_number(value)
    if error:
        return None
    return parsed


def _is_missing(value: Any) -> bool:
    return FieldReplayImportAgent._is_missing_value(value)


def _clip(value: float) -> float:
    return max(0.0, min(1.0, value))


def _correlation(xs: list[float], ys: list[float]) -> float:
    if len(xs) < 2 or len(xs) != len(ys):
        return 0.0
    mean_x = sum(xs) / len(xs)
    mean_y = sum(ys) / len(ys)
    num = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys, strict=True))
    den_x = sum((x - mean_x) ** 2 for x in xs) ** 0.5
    den_y = sum((y - mean_y) ** 2 for y in ys) ** 0.5
    return round(num / max(1e-9, den_x * den_y), 3)

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from water_ai.agents.field_replay_import_agent import FieldReplayImportAgent, preflight_field_replay_package


SOFT_HOLDOUT_FIELD_REQUIREMENTS = {
    "sensor_timeseries": [
        "batch_id",
        "timestamp_min",
        "EC_uScm",
        "turbidity_NTU",
        "UV254_abs",
        "pH",
        "ORP_mV",
        "flow_Lmin",
    ],
    "offline_lab_results": [
        "batch_id",
        "sample_time_min",
        "result_time_min",
        "analyte",
        "value",
        "qa_flag",
    ],
}

WEAK_TARGET_ANALYTES = {"catalyst_activity", "matrix_interference"}
PRESSURE_HEADLOSS_TABLE = "pressure_headloss_event_log"
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
REPLAY_TABLES = [
    "sensor_timeseries",
    "offline_lab_results",
    "campaign_operation_log",
    "fast_proxy_event_log",
    PRESSURE_HEADLOSS_TABLE,
]
MINIMUM_SMOKE_TEST_MATCHED_BATCHES = 3
RECOMMENDED_CALIBRATION_PROXY_EVENTS = 12
FIELD_PROXY_HOLDOUT_MINIMUM_MATCHED_BATCHES = 3
FIELD_PROXY_SENSOR_TABLE = "node_modality_sensor_timeseries"
FIELD_PROXY_LEGACY_SENSOR_TABLE = "sensor_timeseries"
FIELD_PROXY_GEOMETRY_TABLE = "site_topology_or_bed_geometry"
FIELD_PROXY_REQUIRED_ANALYTE = "catalyst_activity"
FIELD_PROXY_PRESSURE_SIGNAL = "N3_catalyst_bed:pressure_drop_kPa"
PRESSURE_SOURCE_ALIASES = {
    "node": FIELD_PROXY_SENSOR_TABLE,
    "node_modality": FIELD_PROXY_SENSOR_TABLE,
    "node_modality_sensor": FIELD_PROXY_SENSOR_TABLE,
    FIELD_PROXY_SENSOR_TABLE: FIELD_PROXY_SENSOR_TABLE,
    "pressure_event": PRESSURE_HEADLOSS_TABLE,
    "pressure_headloss": PRESSURE_HEADLOSS_TABLE,
    "pressure_headloss_event": PRESSURE_HEADLOSS_TABLE,
    PRESSURE_HEADLOSS_TABLE: PRESSURE_HEADLOSS_TABLE,
}
ACCEPTED_SENSOR_STATUS = {"ok", "pass", "passed", "valid", "calibrated", "normal", "qualified", "合格", "正常"}
PROXY_LABEL_QUALITY_FIELDS = [
    "protective_triggered",
    "field_label_matrix_shock",
    "false_positive_cost_index",
    "event_time_min",
    "lab_label_time_min",
]
LAB_RESULT_QUALITY_FIELDS = [
    "sample_time_min",
    "result_time_min",
    "analyte",
    "value",
    "qa_flag",
]
ACCEPTED_LAB_QA_FLAGS = {"pass", "passed", "valid", "ok", "qc_pass", "qualified", "合格"}
OPERATION_ACTION_QUALITY_FIELDS = [
    "action_id",
    "command_time_min",
    "effect_time_min",
    "start_min",
    "end_min",
    "release_policy",
]
PRESSURE_HEADLOSS_QUALITY_FIELDS = [
    "batch_id",
    "event_time_min",
    "bed_id",
    "pressure_drop_kPa",
    "headloss_kPa_per_m",
    "flow_Lmin",
    "matched_lab_sample_time_min",
    "regeneration_event",
    "hydraulic_anomaly_label",
]
ACCEPTED_PUMP_VALVE_RESULTS = {"ok", "pass", "passed", "success", "normal", "executed", "confirmed", "合格", "正常"}
INVALID_OPERATION_ACTION_TOKENS = {"none", "unknown", "noop", "no_action", "missing"}


def assess_field_package_coverage(
    package_dir: str | Path,
    *,
    claim_specific_package_metrics: dict[str, Any] | None = None,
    soft_sensor_field_holdout_gate_metrics: dict[str, Any] | None = None,
    catalyst_proxy_metrics: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Compare a package directory against R7 claim and soft-holdout evidence needs."""

    root = Path(package_dir)
    metadata = _load_metadata(root)
    table_profiles = _table_profiles(root)
    claim_rows = _claim_rows(claim_specific_package_metrics or {})
    claim_audit = [_audit_claim_row(row, metadata, table_profiles) for row in claim_rows]
    soft_holdout_audit = _soft_holdout_audit(table_profiles, soft_sensor_field_holdout_gate_metrics or {})
    field_proxy_holdout_audit = _field_proxy_holdout_audit(table_profiles, catalyst_proxy_metrics or {})
    minimum_replay_contract = _minimum_replay_contract_audit(table_profiles)
    preflight = preflight_field_replay_package(root)
    readiness = _coverage_readiness(
        claim_audit,
        soft_holdout_audit,
        field_proxy_holdout_audit,
        minimum_replay_contract,
        preflight,
    )
    field_evidence_sufficiency_gate = _dict(readiness.get("field_evidence_sufficiency_gate"))
    return {
        "package_dir": str(root),
        "metadata_fields": sorted(metadata),
        "table_profiles": table_profiles,
        "claim_coverage_audit": claim_audit,
        "soft_holdout_coverage_audit": soft_holdout_audit,
        "field_proxy_holdout_audit": field_proxy_holdout_audit,
        "minimum_replay_contract_audit": minimum_replay_contract,
        "field_evidence_sufficiency_gate": field_evidence_sufficiency_gate,
        "readiness": readiness,
        "next_actions": _next_actions(readiness, claim_audit, soft_holdout_audit, field_proxy_holdout_audit),
        "patch_plan": _patch_plan(
            readiness,
            preflight,
            claim_audit,
            soft_holdout_audit,
            field_proxy_holdout_audit,
            minimum_replay_contract,
        ),
    }


def _load_metadata(root: Path) -> dict[str, Any]:
    path = root / "metadata.json"
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _table_profiles(root: Path) -> dict[str, dict[str, Any]]:
    profiles: dict[str, dict[str, Any]] = {}
    for csv_path in sorted(root.glob("*.csv")):
        with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            headers = list(reader.fieldnames or [])
            rows = [dict(row) for row in reader]
        profiles[csv_path.stem] = {
            "path": str(csv_path),
            "headers": headers,
            "row_count": len(rows),
            "non_empty_fields": sorted(
                {
                    field
                    for field in headers
                    if any(not FieldReplayImportAgent._is_missing_value(row.get(field)) for row in rows)
                }
            ),
            "sample_values_by_field": _sample_values_by_field(rows, headers),
            "unique_values_by_field": _unique_values_by_field(
                rows,
                [field for field in ("batch_id", "campaign_id", "analyte", "action_id") if field in headers],
            ),
            "time_order_violations": _time_order_violations(csv_path.stem, rows),
            "operation_action_quality": _operation_action_quality(rows) if csv_path.stem == "campaign_operation_log" else {},
            "lab_result_quality": _lab_result_quality(rows) if csv_path.stem == "offline_lab_results" else {},
            "proxy_label_quality": _proxy_label_quality(rows) if csv_path.stem == "fast_proxy_event_log" else {},
            "pressure_headloss_quality": _pressure_headloss_quality(rows)
            if csv_path.stem == PRESSURE_HEADLOSS_TABLE
            else {},
        }
    return profiles


def _sample_values_by_field(rows: list[dict[str, Any]], headers: list[str]) -> dict[str, list[str]]:
    values: dict[str, list[str]] = {}
    for field in headers:
        seen: list[str] = []
        for row in rows:
            value = row.get(field)
            if FieldReplayImportAgent._is_missing_value(value):
                continue
            token = str(value)
            if token not in seen:
                seen.append(token)
            if len(seen) >= 5:
                break
        values[field] = seen
    return values


def _unique_values_by_field(rows: list[dict[str, Any]], fields: list[str]) -> dict[str, list[str]]:
    values: dict[str, set[str]] = {field: set() for field in fields}
    for row in rows:
        for field in fields:
            value = row.get(field)
            if FieldReplayImportAgent._is_missing_value(value):
                continue
            values[field].add(str(value))
    return {field: sorted(tokens) for field, tokens in values.items()}


def _time_order_violations(table: str, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    violations: list[dict[str, Any]] = []
    for index, row in enumerate(rows):
        if table == "offline_lab_results":
            sample = _optional_number(row.get("sample_time_min"))
            result = _optional_number(row.get("result_time_min"))
            if sample is not None and result is not None and result < sample:
                violations.append(
                    {
                        "row_index": index,
                        "rule": "sample_time_min <= result_time_min",
                        "sample_time_min": sample,
                        "result_time_min": result,
                    }
                )
        elif table == "campaign_operation_log":
            command = _optional_number(row.get("command_time_min"))
            effect = _optional_number(row.get("effect_time_min"))
            start = _optional_number(row.get("start_min"))
            end = _optional_number(row.get("end_min"))
            if None not in {command, effect, start, end} and not (
                command <= effect <= end and start <= end
            ):
                violations.append(
                    {
                        "row_index": index,
                        "rule": "command_time_min <= effect_time_min <= end_min and start_min <= end_min",
                        "command_time_min": command,
                        "effect_time_min": effect,
                        "start_min": start,
                        "end_min": end,
                    }
                )
        elif table == "fast_proxy_event_log":
            event_time = _optional_number(row.get("event_time_min"))
            label_time = _optional_number(row.get("lab_label_time_min"))
            if event_time is not None and label_time is not None and label_time < event_time:
                violations.append(
                    {
                        "row_index": index,
                        "rule": "event_time_min <= lab_label_time_min",
                        "event_time_min": event_time,
                        "lab_label_time_min": label_time,
                    }
                )
    return violations


def _proxy_label_quality(rows: list[dict[str, Any]]) -> dict[str, Any]:
    invalid_rows: list[dict[str, Any]] = []
    class_counts = {
        "protective_triggered_true": 0,
        "protective_triggered_false": 0,
        "field_label_matrix_shock_true": 0,
        "field_label_matrix_shock_false": 0,
    }
    for index, row in enumerate(rows):
        row_errors: list[dict[str, Any]] = []
        batch_id = row.get("batch_id")
        if FieldReplayImportAgent._is_missing_value(batch_id):
            row_errors.append({"field": "batch_id", "error": "missing_batch_id", "value": batch_id})
        protective, protective_error = FieldReplayImportAgent._parse_bool(row.get("protective_triggered"))
        if protective_error:
            row_errors.append({"field": "protective_triggered", "error": protective_error, "value": row.get("protective_triggered")})
        field_label, field_label_error = FieldReplayImportAgent._parse_bool(row.get("field_label_matrix_shock"))
        if field_label_error:
            row_errors.append(
                {"field": "field_label_matrix_shock", "error": field_label_error, "value": row.get("field_label_matrix_shock")}
            )
        false_positive_cost, cost_error = FieldReplayImportAgent._parse_number(row.get("false_positive_cost_index"))
        if cost_error:
            row_errors.append(
                {
                    "field": "false_positive_cost_index",
                    "error": cost_error,
                    "value": row.get("false_positive_cost_index"),
                }
            )
        elif false_positive_cost < 0:
            row_errors.append(
                {
                    "field": "false_positive_cost_index",
                    "error": "negative_false_positive_cost_index",
                    "value": row.get("false_positive_cost_index"),
                }
            )
        for field in ("event_time_min", "lab_label_time_min"):
            _, time_error = FieldReplayImportAgent._parse_number(row.get(field))
            if time_error:
                row_errors.append({"field": field, "error": time_error, "value": row.get(field)})
        if row_errors:
            invalid_rows.append(
                {
                    "row_index": index,
                    "batch_id": row.get("batch_id"),
                    "errors": row_errors,
                }
            )
            continue
        class_counts["protective_triggered_true" if protective else "protective_triggered_false"] += 1
        class_counts["field_label_matrix_shock_true" if field_label else "field_label_matrix_shock_false"] += 1
    valid_count = len(rows) - len(invalid_rows)
    invalid_indexes = {int(row["row_index"]) for row in invalid_rows}
    valid_batch_ids = sorted(
        {
            str(row.get("batch_id"))
            for index, row in enumerate(rows)
            if index not in invalid_indexes and not FieldReplayImportAgent._is_missing_value(row.get("batch_id"))
        }
    )
    return {
        "required_fields": PROXY_LABEL_QUALITY_FIELDS,
        "row_count": len(rows),
        "valid_proxy_label_count": valid_count,
        "valid_proxy_label_batch_count": len(valid_batch_ids),
        "valid_proxy_label_batch_ids": valid_batch_ids,
        "invalid_proxy_label_count": len(invalid_rows),
        "invalid_proxy_label_rows": invalid_rows[:12],
        "proxy_label_class_counts": class_counts,
        "quality_pass": valid_count >= MINIMUM_SMOKE_TEST_MATCHED_BATCHES,
        "quality_note": (
            "Valid fast-proxy labels require parseable protective_triggered, field_label_matrix_shock, "
            "false_positive_cost_index, event_time_min and lab_label_time_min. Timestamp order is audited separately."
        ),
    }


def _lab_result_quality(rows: list[dict[str, Any]]) -> dict[str, Any]:
    invalid_rows: list[dict[str, Any]] = []
    analyte_valid_counts: dict[str, int] = {}
    qa_flag_counts: dict[str, int] = {}
    for index, row in enumerate(rows):
        row_errors: list[dict[str, Any]] = []
        batch_id = row.get("batch_id")
        if FieldReplayImportAgent._is_missing_value(batch_id):
            row_errors.append({"field": "batch_id", "error": "missing_batch_id", "value": batch_id})
        analyte = row.get("analyte")
        if FieldReplayImportAgent._is_missing_value(analyte):
            row_errors.append({"field": "analyte", "error": "missing_analyte", "value": analyte})
        value, value_error = FieldReplayImportAgent._parse_number(row.get("value"))
        if value_error:
            row_errors.append({"field": "value", "error": value_error, "value": row.get("value")})
        elif value < 0:
            row_errors.append({"field": "value", "error": "negative_lab_value", "value": row.get("value")})
        for field in ("sample_time_min", "result_time_min"):
            _, time_error = FieldReplayImportAgent._parse_number(row.get(field))
            if time_error:
                row_errors.append({"field": field, "error": time_error, "value": row.get(field)})
        qa_token = str(row.get("qa_flag", "")).strip().lower()
        if FieldReplayImportAgent._is_missing_value(row.get("qa_flag")):
            row_errors.append({"field": "qa_flag", "error": "missing_qa_flag", "value": row.get("qa_flag")})
        elif qa_token not in ACCEPTED_LAB_QA_FLAGS:
            row_errors.append({"field": "qa_flag", "error": "qa_flag_not_pass", "value": row.get("qa_flag")})
        qa_flag_counts[qa_token or "missing"] = qa_flag_counts.get(qa_token or "missing", 0) + 1
        if row_errors:
            invalid_rows.append({"row_index": index, "batch_id": row.get("batch_id"), "errors": row_errors})
            continue
        analyte_key = str(analyte)
        analyte_valid_counts[analyte_key] = analyte_valid_counts.get(analyte_key, 0) + 1
    valid_count = len(rows) - len(invalid_rows)
    invalid_indexes = {int(row["row_index"]) for row in invalid_rows}
    valid_batch_ids = sorted(
        {
            str(row.get("batch_id"))
            for index, row in enumerate(rows)
            if index not in invalid_indexes and not FieldReplayImportAgent._is_missing_value(row.get("batch_id"))
        }
    )
    return {
        "required_fields": LAB_RESULT_QUALITY_FIELDS,
        "accepted_qa_flags": sorted(ACCEPTED_LAB_QA_FLAGS),
        "row_count": len(rows),
        "valid_lab_result_count": valid_count,
        "valid_lab_result_batch_count": len(valid_batch_ids),
        "valid_lab_result_batch_ids": valid_batch_ids,
        "invalid_lab_result_count": len(invalid_rows),
        "invalid_lab_result_rows": invalid_rows[:12],
        "analyte_valid_counts": dict(sorted(analyte_valid_counts.items())),
        "qa_flag_counts": dict(sorted(qa_flag_counts.items())),
        "quality_pass": valid_count >= MINIMUM_SMOKE_TEST_MATCHED_BATCHES,
        "quality_note": (
            "Valid offline lab results require parseable sample/result times, non-negative numeric value, "
            "non-empty analyte and a passing QA flag. Claim-specific method/unit/detection_limit are audited separately."
        ),
    }


def _operation_action_quality(rows: list[dict[str, Any]]) -> dict[str, Any]:
    invalid_rows: list[dict[str, Any]] = []
    action_counts: dict[str, int] = {}
    pump_valve_counts: dict[str, int] = {}
    for index, row in enumerate(rows):
        row_errors: list[dict[str, Any]] = []
        batch_id = row.get("batch_id")
        if FieldReplayImportAgent._is_missing_value(batch_id):
            row_errors.append({"field": "batch_id", "error": "missing_batch_id", "value": batch_id})
        action_token = str(row.get("action_id", "")).strip()
        if FieldReplayImportAgent._is_missing_value(action_token):
            row_errors.append({"field": "action_id", "error": "missing_action_id", "value": row.get("action_id")})
        elif action_token.lower() in INVALID_OPERATION_ACTION_TOKENS:
            row_errors.append({"field": "action_id", "error": "non_executable_action_id", "value": row.get("action_id")})
        for field in ("command_time_min", "effect_time_min", "start_min", "end_min"):
            _, time_error = FieldReplayImportAgent._parse_number(row.get(field))
            if time_error:
                row_errors.append({"field": field, "error": time_error, "value": row.get(field)})
        release_policy = row.get("release_policy")
        if FieldReplayImportAgent._is_missing_value(release_policy):
            row_errors.append({"field": "release_policy", "error": "missing_release_policy", "value": release_policy})
        _validate_optional_number(row, "recycle_ratio", row_errors, minimum=0.0, maximum=1.0)
        _validate_optional_number(row, "tank_storage_margin", row_errors, minimum=0.0)
        _validate_optional_number(row, "actuator_latency_p90", row_errors, minimum=0.0)
        _validate_optional_number(row, "hold_time_min", row_errors, minimum=0.0)
        pump_valve_result = row.get("pump_valve_result")
        if not FieldReplayImportAgent._is_missing_value(pump_valve_result):
            pump_token = str(pump_valve_result).strip().lower()
            pump_valve_counts[pump_token] = pump_valve_counts.get(pump_token, 0) + 1
            if pump_token not in ACCEPTED_PUMP_VALVE_RESULTS:
                row_errors.append(
                    {"field": "pump_valve_result", "error": "pump_valve_result_not_successful", "value": pump_valve_result}
                )
        if "regeneration_event" in row and not FieldReplayImportAgent._is_missing_value(row.get("regeneration_event")):
            _, bool_error = FieldReplayImportAgent._parse_bool(row.get("regeneration_event"))
            if bool_error:
                row_errors.append({"field": "regeneration_event", "error": bool_error, "value": row.get("regeneration_event")})
        if row_errors:
            invalid_rows.append({"row_index": index, "batch_id": batch_id, "errors": row_errors})
            continue
        action_counts[action_token] = action_counts.get(action_token, 0) + 1
    valid_count = len(rows) - len(invalid_rows)
    invalid_indexes = {int(row["row_index"]) for row in invalid_rows}
    valid_batch_ids = sorted(
        {
            str(row.get("batch_id"))
            for index, row in enumerate(rows)
            if index not in invalid_indexes and not FieldReplayImportAgent._is_missing_value(row.get("batch_id"))
        }
    )
    return {
        "required_fields": OPERATION_ACTION_QUALITY_FIELDS,
        "accepted_pump_valve_results": sorted(ACCEPTED_PUMP_VALVE_RESULTS),
        "row_count": len(rows),
        "valid_operation_action_count": valid_count,
        "valid_operation_action_batch_count": len(valid_batch_ids),
        "valid_operation_action_batch_ids": valid_batch_ids,
        "invalid_operation_action_count": len(invalid_rows),
        "invalid_operation_action_rows": invalid_rows[:12],
        "action_counts": dict(sorted(action_counts.items())),
        "pump_valve_result_counts": dict(sorted(pump_valve_counts.items())),
        "quality_pass": valid_count >= MINIMUM_SMOKE_TEST_MATCHED_BATCHES,
        "quality_note": (
            "Valid operation rows require executable action_id, parseable command/effect/start/end times and "
            "release_policy. Optional engineering fields are range-checked when provided."
        ),
    }


def _pressure_headloss_quality(rows: list[dict[str, Any]]) -> dict[str, Any]:
    invalid_rows: list[dict[str, Any]] = []
    anomaly_counts = {
        "hydraulic_anomaly_label_true": 0,
        "hydraulic_anomaly_label_false": 0,
        "regeneration_event_true": 0,
        "regeneration_event_false": 0,
    }
    for index, row in enumerate(rows):
        row_errors: list[dict[str, Any]] = []
        batch_id = row.get("batch_id")
        if FieldReplayImportAgent._is_missing_value(batch_id):
            row_errors.append({"field": "batch_id", "error": "missing_batch_id", "value": batch_id})
        bed_id = row.get("bed_id")
        if FieldReplayImportAgent._is_missing_value(bed_id):
            row_errors.append({"field": "bed_id", "error": "missing_bed_id", "value": bed_id})
        for field in ("event_time_min", "matched_lab_sample_time_min"):
            value, error = FieldReplayImportAgent._parse_number(row.get(field))
            if error:
                row_errors.append({"field": field, "error": error, "value": row.get(field)})
            elif value < 0:
                row_errors.append({"field": field, "error": "negative_timestamp", "value": row.get(field)})
        for field in ("pressure_drop_kPa", "headloss_kPa_per_m"):
            value, error = FieldReplayImportAgent._parse_number(row.get(field))
            if error:
                row_errors.append({"field": field, "error": error, "value": row.get(field)})
            elif value < 0:
                row_errors.append({"field": field, "error": "negative_pressure_headloss_value", "value": row.get(field)})
        flow, flow_error = FieldReplayImportAgent._parse_number(row.get("flow_Lmin"))
        if flow_error:
            row_errors.append({"field": "flow_Lmin", "error": flow_error, "value": row.get("flow_Lmin")})
        elif flow <= 0:
            row_errors.append({"field": "flow_Lmin", "error": "non_positive_flow", "value": row.get("flow_Lmin")})
        hydraulic_label, hydraulic_error = FieldReplayImportAgent._parse_bool(row.get("hydraulic_anomaly_label"))
        if hydraulic_error:
            row_errors.append(
                {"field": "hydraulic_anomaly_label", "error": hydraulic_error, "value": row.get("hydraulic_anomaly_label")}
            )
        regeneration_event, regeneration_error = FieldReplayImportAgent._parse_bool(row.get("regeneration_event"))
        if regeneration_error:
            row_errors.append(
                {"field": "regeneration_event", "error": regeneration_error, "value": row.get("regeneration_event")}
            )
        if "operator_review_required" in row and not FieldReplayImportAgent._is_missing_value(
            row.get("operator_review_required")
        ):
            _, operator_review_error = FieldReplayImportAgent._parse_bool(row.get("operator_review_required"))
            if operator_review_error:
                row_errors.append(
                    {
                        "field": "operator_review_required",
                        "error": operator_review_error,
                        "value": row.get("operator_review_required"),
                    }
                )
        _validate_optional_number(row, "flow_normalized_pressure_residual", row_errors)
        _validate_optional_number(row, "expected_clean_bed_pressure_drop_kPa", row_errors, minimum=0.0)
        if row_errors:
            invalid_rows.append({"row_index": index, "batch_id": batch_id, "errors": row_errors})
            continue
        anomaly_counts["hydraulic_anomaly_label_true" if hydraulic_label else "hydraulic_anomaly_label_false"] += 1
        anomaly_counts["regeneration_event_true" if regeneration_event else "regeneration_event_false"] += 1
    valid_count = len(rows) - len(invalid_rows)
    invalid_indexes = {int(row["row_index"]) for row in invalid_rows}
    valid_batch_ids = sorted(
        {
            str(row.get("batch_id"))
            for index, row in enumerate(rows)
            if index not in invalid_indexes and not FieldReplayImportAgent._is_missing_value(row.get("batch_id"))
        }
    )
    return {
        "required_fields": PRESSURE_HEADLOSS_QUALITY_FIELDS,
        "row_count": len(rows),
        "valid_pressure_headloss_event_count": valid_count,
        "valid_pressure_headloss_batch_count": len(valid_batch_ids),
        "valid_pressure_headloss_batch_ids": valid_batch_ids,
        "invalid_pressure_headloss_event_count": len(invalid_rows),
        "invalid_pressure_headloss_event_rows": invalid_rows[:12],
        "pressure_headloss_class_counts": anomaly_counts,
        "quality_pass": valid_count >= MINIMUM_SMOKE_TEST_MATCHED_BATCHES
        and len(valid_batch_ids) >= MINIMUM_SMOKE_TEST_MATCHED_BATCHES,
        "quality_note": (
            "Valid pressure/headloss events require same-batch bed_id, parseable non-negative pressure/headloss "
            "signals, positive flow, parseable matched lab sample time and hydraulic/regeneration labels."
        ),
    }


def _validate_optional_number(
    row: dict[str, Any],
    field: str,
    errors: list[dict[str, Any]],
    *,
    minimum: float | None = None,
    maximum: float | None = None,
) -> None:
    if field not in row or FieldReplayImportAgent._is_missing_value(row.get(field)):
        return
    parsed, message = FieldReplayImportAgent._parse_number(row.get(field))
    if message:
        errors.append({"field": field, "error": message, "value": row.get(field)})
        return
    if minimum is not None and parsed < minimum:
        errors.append({"field": field, "error": "below_minimum", "value": row.get(field), "minimum": minimum})
    if maximum is not None and parsed > maximum:
        errors.append({"field": field, "error": "above_maximum", "value": row.get(field), "maximum": maximum})


def _optional_number(value: Any) -> float | None:
    if FieldReplayImportAgent._is_missing_value(value):
        return None
    parsed, message = FieldReplayImportAgent._parse_number(value)
    if message:
        return None
    return parsed


def _claim_rows(metrics: dict[str, Any]) -> list[dict[str, Any]]:
    rows = metrics.get("minimal_field_package_matrix", [])
    return rows if isinstance(rows, list) else []


def _audit_claim_row(
    row: dict[str, Any],
    metadata: dict[str, Any],
    table_profiles: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    required_metadata = [str(field) for field in _list(row.get("metadata_required_fields"))]
    metadata_missing = [
        field
        for field in required_metadata
        if FieldReplayImportAgent._is_missing_value(metadata.get(field))
    ]
    required_fields_by_table = _dict(row.get("claim_specific_required_fields"))
    table_audits: dict[str, dict[str, Any]] = {}
    logical_guardrail_fields: list[str] = []
    for table, fields in sorted(required_fields_by_table.items()):
        required_fields = [str(field) for field in _list(fields)]
        if str(table).startswith("_"):
            logical_guardrail_fields.extend(required_fields)
            continue
        profile = table_profiles.get(str(table), {})
        headers = set(_list(profile.get("headers")))
        non_empty = set(_list(profile.get("non_empty_fields")))
        row_count = int(profile.get("row_count", 0) or 0)
        table_audits[str(table)] = {
            "required_fields": required_fields,
            "row_count": row_count,
            "missing_headers": [field for field in required_fields if field not in headers],
            "empty_required_fields": [field for field in required_fields if field in headers and field not in non_empty],
            "row_presence_pass": row_count > 0,
        }
    all_headers = {field for profile in table_profiles.values() for field in _list(profile.get("headers"))}
    missing_logical_guardrail_fields = [field for field in logical_guardrail_fields if field not in all_headers]
    missing_header_count = sum(len(audit["missing_headers"]) for audit in table_audits.values())
    empty_field_count = sum(len(audit["empty_required_fields"]) for audit in table_audits.values())
    missing_row_tables = [table for table, audit in table_audits.items() if not audit["row_presence_pass"]]
    coverage_pass = not metadata_missing and not missing_header_count and not empty_field_count and not missing_row_tables and not missing_logical_guardrail_fields
    return {
        "need_id": row.get("need_id"),
        "field_validation_need": row.get("field_validation_need"),
        "need_type": row.get("need_type"),
        "metadata_missing": metadata_missing,
        "table_audits": table_audits,
        "logical_guardrail_fields": sorted(set(logical_guardrail_fields)),
        "missing_logical_guardrail_fields": missing_logical_guardrail_fields,
        "missing_row_tables": missing_row_tables,
        "coverage_pass": coverage_pass,
        "claim_upgrade_blocked_by": [] if coverage_pass else _claim_blockers(
            metadata_missing,
            missing_header_count,
            empty_field_count,
            missing_row_tables,
            missing_logical_guardrail_fields,
        ),
    }


def _soft_holdout_audit(
    table_profiles: dict[str, dict[str, Any]],
    soft_sensor_field_holdout_gate_metrics: dict[str, Any],
) -> dict[str, Any]:
    table_audits = {}
    for table, required_fields in SOFT_HOLDOUT_FIELD_REQUIREMENTS.items():
        profile = table_profiles.get(table, {})
        headers = set(_list(profile.get("headers")))
        non_empty = set(_list(profile.get("non_empty_fields")))
        table_audits[table] = {
            "required_fields": required_fields,
            "row_count": int(profile.get("row_count", 0) or 0),
            "missing_headers": [field for field in required_fields if field not in headers],
            "empty_required_fields": [field for field in required_fields if field in headers and field not in non_empty],
        }
    offline_profile = table_profiles.get("offline_lab_results", {})
    analytes = set(_list(_dict(offline_profile.get("unique_values_by_field")).get("analyte")))
    missing_weak_target_analytes = sorted(WEAK_TARGET_ANALYTES - analytes)
    gate_readiness = _dict(soft_sensor_field_holdout_gate_metrics.get("readiness"))
    required_from_gate = list(gate_readiness.get("failed_check_ids", [])) if isinstance(gate_readiness.get("failed_check_ids"), list) else []
    coverage_pass = (
        all(not audit["missing_headers"] and not audit["empty_required_fields"] and audit["row_count"] > 0 for audit in table_audits.values())
        and not missing_weak_target_analytes
    )
    return {
        "table_audits": table_audits,
        "observed_offline_analytes": sorted(analytes),
        "required_weak_target_analytes": sorted(WEAK_TARGET_ANALYTES),
        "missing_weak_target_analytes": missing_weak_target_analytes,
        "upstream_failed_check_ids": required_from_gate,
        "coverage_pass": coverage_pass,
    }


def _field_proxy_holdout_audit(
    table_profiles: dict[str, dict[str, Any]],
    catalyst_proxy_metrics: dict[str, Any],
) -> dict[str, Any]:
    repair_plan = _dict(catalyst_proxy_metrics.get("weak_axis_repair_plan"))
    repair_status = str(repair_plan.get("repair_status", "not_requested"))
    evidence_requirements = [
        _dict(item)
        for item in _list(repair_plan.get("field_repair_evidence_requirements"))
        if str(_dict(item).get("evidence_stage_required", "")) == "field_proxy_holdout"
    ]
    holdout_required = bool(evidence_requirements)
    if not holdout_required:
        return {
            "audit_id": "R7j_agent51_catalyst_proxy_holdout_contract",
            "repair_status": repair_status,
            "holdout_required": False,
            "coverage_pass": True,
            "status": "field_proxy_holdout_not_requested",
            "minimum_matched_batch_count": FIELD_PROXY_HOLDOUT_MINIMUM_MATCHED_BATCHES,
            "matched_proxy_holdout_batch_count": 0,
            "matched_proxy_holdout_batch_ids_sample": [],
            "field_boundary": (
                "No Agent51 weak-axis repair plan was supplied, so R7j does not change the generic replay package gate."
            ),
        }

    table_audits = _field_proxy_requirement_table_audits(table_profiles, evidence_requirements)
    required_sensor_signals = _field_proxy_required_sensor_signals(evidence_requirements)
    sensor_audit = _field_proxy_sensor_signal_audit(table_profiles, required_sensor_signals)
    lab_audit = _field_proxy_lab_label_audit(table_profiles)
    operation_audit = _field_proxy_operation_audit(table_profiles)
    geometry_audit = _field_proxy_geometry_audit(table_profiles)
    matched_batches = (
        set(sensor_audit["valid_all_signal_batch_ids"])
        & set(lab_audit["valid_catalyst_activity_batch_ids"])
        & set(operation_audit["valid_regeneration_event_batch_ids"])
    )
    matched_batch_count = len(matched_batches)
    missing_required_tables = [
        table for table, audit in table_audits.items() if not bool(audit.get("table_present", False))
    ]
    missing_required_fields_by_table = {
        table: audit["missing_headers"]
        for table, audit in table_audits.items()
        if audit.get("missing_headers")
    }
    empty_required_fields_by_table = {
        table: audit["empty_required_fields"]
        for table, audit in table_audits.items()
        if audit.get("empty_required_fields")
    }
    coverage_pass = (
        not missing_required_tables
        and not missing_required_fields_by_table
        and not empty_required_fields_by_table
        and not sensor_audit["missing_patch_signals"]
        and not bool(sensor_audit.get("conflict_requires_operator_review", False))
        and lab_audit["catalyst_activity_label_pass"]
        and operation_audit["regeneration_event_pass"]
        and geometry_audit["geometry_coverage_pass"]
        and matched_batch_count >= FIELD_PROXY_HOLDOUT_MINIMUM_MATCHED_BATCHES
    )
    status = (
        "field_proxy_holdout_ready_for_agent51_validation"
        if coverage_pass
        else "field_proxy_holdout_coverage_gaps"
    )
    return {
        "audit_id": "R7j_agent51_catalyst_proxy_holdout_contract",
        "repair_status": repair_status,
        "holdout_required": True,
        "coverage_pass": coverage_pass,
        "status": status,
        "minimum_matched_batch_count": FIELD_PROXY_HOLDOUT_MINIMUM_MATCHED_BATCHES,
        "required_patch_signals": required_sensor_signals,
        "table_audits": table_audits,
        "missing_required_tables": missing_required_tables,
        "missing_required_fields_by_table": missing_required_fields_by_table,
        "empty_required_fields_by_table": empty_required_fields_by_table,
        "pressure_source_conflict_count": sensor_audit.get("pressure_source_conflict_count", 0),
        "resolved_pressure_source_conflict_count": sensor_audit.get("resolved_pressure_source_conflict_count", 0),
        "unresolved_pressure_source_conflict_count": sensor_audit.get("unresolved_pressure_source_conflict_count", 0),
        "pressure_source_resolution_record_count": sensor_audit.get("pressure_source_resolution_record_count", 0),
        "pressure_source_conflict_batch_ids_sample": sensor_audit.get("pressure_source_conflict_batch_ids_sample", []),
        "unresolved_pressure_source_conflict_batch_ids_sample": sensor_audit.get(
            "unresolved_pressure_source_conflict_batch_ids_sample",
            [],
        ),
        "pressure_source_conflicts": sensor_audit.get("pressure_source_conflicts", []),
        "unresolved_pressure_source_conflicts": sensor_audit.get("unresolved_pressure_source_conflicts", []),
        "pressure_source_resolutions": sensor_audit.get("pressure_source_resolutions", []),
        "conflict_requires_operator_review": bool(sensor_audit.get("conflict_requires_operator_review", False)),
        "sensor_signal_audit": sensor_audit,
        "lab_label_audit": lab_audit,
        "operation_event_audit": operation_audit,
        "geometry_audit": geometry_audit,
        "matched_proxy_holdout_batch_count": matched_batch_count,
        "matched_proxy_holdout_batch_ids_sample": sorted(matched_batches)[:8],
        "matched_batch_requirement": (
            "At least three batch_id values must have all Agent51 catalyst proxy sensor signals, "
            "QA-passed catalyst_activity lab labels and parseable regeneration_event operation rows."
        ),
        "field_boundary": (
            "R7j only validates that the field package can support Agent51 catalyst proxy holdout. "
            "It does not make the catalyst proxy field-supported or relax Agent49 catalyst uncertainty by itself."
        ),
    }


def _field_proxy_requirement_table_audits(
    table_profiles: dict[str, dict[str, Any]],
    evidence_requirements: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    audits: dict[str, dict[str, Any]] = {}
    for requirement in evidence_requirements:
        table = str(requirement.get("required_table", ""))
        if not table:
            continue
        required_fields = [str(field) for field in _list(requirement.get("required_fields"))]
        if str(requirement.get("patch_class", "")) == "low_cost_sensor" and table == FIELD_PROXY_LEGACY_SENSOR_TABLE:
            table = _field_proxy_sensor_evidence_table(table_profiles, required_fields)
        profile = table_profiles.get(table, {})
        headers = set(_list(profile.get("headers")))
        non_empty = set(_list(profile.get("non_empty_fields")))
        audits[table] = {
            "requirement_id": requirement.get("requirement_id"),
            "patch_class": requirement.get("patch_class"),
            "accepted_alternative_tables": [FIELD_PROXY_SENSOR_TABLE, FIELD_PROXY_LEGACY_SENSOR_TABLE]
            if str(requirement.get("patch_class", "")) == "low_cost_sensor"
            else [],
            "minimum_evidence": requirement.get("minimum_evidence"),
            "supports_patch_signals": [str(item) for item in _list(requirement.get("supports_patch_signals"))],
            "required_fields": required_fields,
            "table_present": table in table_profiles,
            "row_count": int(profile.get("row_count", 0) or 0),
            "missing_headers": [field for field in required_fields if field not in headers],
            "empty_required_fields": [field for field in required_fields if field in headers and field not in non_empty],
        }
    return audits


def _field_proxy_sensor_evidence_table(table_profiles: dict[str, dict[str, Any]], required_fields: list[str]) -> str:
    supplement = _dict(table_profiles.get(FIELD_PROXY_SENSOR_TABLE))
    if supplement:
        return FIELD_PROXY_SENSOR_TABLE
    legacy = _dict(table_profiles.get(FIELD_PROXY_LEGACY_SENSOR_TABLE))
    legacy_headers = set(_list(legacy.get("headers")))
    if legacy and all(field in legacy_headers for field in required_fields):
        return FIELD_PROXY_LEGACY_SENSOR_TABLE
    return FIELD_PROXY_SENSOR_TABLE


def _field_proxy_required_sensor_signals(evidence_requirements: list[dict[str, Any]]) -> list[str]:
    signals: list[str] = []
    for requirement in evidence_requirements:
        if str(requirement.get("patch_class", "")) != "low_cost_sensor":
            continue
        for signal in _list(requirement.get("supports_patch_signals")):
            token = str(signal)
            if ":" in token and token not in signals:
                signals.append(token)
    return signals


def _field_proxy_sensor_signal_audit(
    table_profiles: dict[str, dict[str, Any]],
    required_signals: list[str],
) -> dict[str, Any]:
    source_table = _field_proxy_sensor_evidence_table(
        table_profiles,
        ["batch_id", "timestamp_min", "node_id", "modality", "value", "sensor_status"],
    )
    profile = _dict(table_profiles.get(source_table, {}))
    rows = _csv_rows(profile)
    pressure_event_values = _pressure_headloss_event_pressure_values(table_profiles)
    pressure_event_batch_ids = sorted(pressure_event_values)
    pressure_resolution_audit = _pressure_source_resolution_records(table_profiles)
    pressure_resolution_by_batch = _dict(pressure_resolution_audit.get("valid_resolution_by_batch"))
    signal_audits: dict[str, dict[str, Any]] = {}
    signal_batch_sets: list[set[str]] = []
    pressure_source_conflicts: list[dict[str, Any]] = []
    unresolved_pressure_source_conflicts: list[dict[str, Any]] = []
    pressure_source_resolutions: list[dict[str, Any]] = []
    for signal in required_signals:
        node_id, modality = signal.split(":", 1)
        valid_rows: list[dict[str, Any]] = []
        invalid_rows: list[dict[str, Any]] = []
        for index, row in enumerate(rows):
            if str(row.get("node_id", "")).strip() != node_id or str(row.get("modality", "")).strip() != modality:
                continue
            errors: list[dict[str, Any]] = []
            batch_id = row.get("batch_id")
            if FieldReplayImportAgent._is_missing_value(batch_id):
                errors.append({"field": "batch_id", "error": "missing_batch_id", "value": batch_id})
            _, time_error = FieldReplayImportAgent._parse_number(row.get("timestamp_min"))
            if time_error:
                errors.append({"field": "timestamp_min", "error": time_error, "value": row.get("timestamp_min")})
            value, value_error = FieldReplayImportAgent._parse_number(row.get("value"))
            if value_error:
                errors.append({"field": "value", "error": value_error, "value": row.get("value")})
            sensor_status = str(row.get("sensor_status", "")).strip().lower()
            if FieldReplayImportAgent._is_missing_value(row.get("sensor_status")):
                errors.append({"field": "sensor_status", "error": "missing_sensor_status", "value": row.get("sensor_status")})
            elif sensor_status not in ACCEPTED_SENSOR_STATUS:
                errors.append({"field": "sensor_status", "error": "sensor_status_not_accepted", "value": row.get("sensor_status")})
            if errors:
                invalid_rows.append({"row_index": index, "batch_id": batch_id, "errors": errors})
                continue
            valid_rows.append({"batch_id": str(batch_id), "timestamp_min": row.get("timestamp_min"), "value": value})
        node_batch_values = _average_values_by_batch(valid_rows)
        node_batch_ids = sorted(node_batch_values)
        accepted_evidence_sources = ["node_modality_sensor_timeseries"] if node_batch_ids else []
        pressure_event_batch_ids_for_signal: list[str] = []
        pressure_source_conflict_audit: dict[str, Any] = {
            "pressure_source_conflict_count": 0,
            "pressure_source_conflict_batch_ids": [],
            "unresolved_pressure_source_conflict_count": 0,
            "unresolved_pressure_source_conflict_batch_ids": [],
            "resolved_pressure_source_conflict_count": 0,
            "pressure_source_conflicts": [],
            "unresolved_pressure_source_conflicts": [],
            "pressure_source_resolutions": [],
            "conflict_requires_operator_review": False,
        }
        if signal == FIELD_PROXY_PRESSURE_SIGNAL and pressure_event_batch_ids:
            pressure_source_conflict_audit = _pressure_source_conflict_audit(
                node_batch_values,
                pressure_event_values,
                pressure_resolution_by_batch,
            )
            pressure_source_conflicts = _list(pressure_source_conflict_audit.get("pressure_source_conflicts"))
            unresolved_pressure_source_conflicts = _list(
                pressure_source_conflict_audit.get("unresolved_pressure_source_conflicts")
            )
            pressure_source_resolutions = _list(pressure_source_conflict_audit.get("pressure_source_resolutions"))
            raw_conflict_batch_ids = set(_list(pressure_source_conflict_audit.get("pressure_source_conflict_batch_ids")))
            unresolved_batch_ids = set(
                _list(pressure_source_conflict_audit.get("unresolved_pressure_source_conflict_batch_ids"))
            )
            resolved_by_source = {
                str(item.get("batch_id")): str(item.get("authoritative_pressure_source"))
                for item in pressure_source_resolutions
            }
            node_batch_ids = sorted(
                (set(node_batch_ids) - raw_conflict_batch_ids)
                | {batch_id for batch_id, source in resolved_by_source.items() if source == FIELD_PROXY_SENSOR_TABLE}
            )
            pressure_event_batch_ids_for_signal = sorted(
                (set(pressure_event_batch_ids) - raw_conflict_batch_ids)
                | {batch_id for batch_id, source in resolved_by_source.items() if source == PRESSURE_HEADLOSS_TABLE}
            )
            pressure_event_batch_ids_for_signal = sorted(set(pressure_event_batch_ids_for_signal) - unresolved_batch_ids)
            accepted_evidence_sources = []
            if node_batch_ids:
                accepted_evidence_sources.append("node_modality_sensor_timeseries")
            if pressure_event_batch_ids_for_signal:
                accepted_evidence_sources.append(PRESSURE_HEADLOSS_TABLE)
            batch_ids = sorted(set(node_batch_ids) | set(pressure_event_batch_ids_for_signal))
        else:
            batch_ids = node_batch_ids
        signal_batch_sets.append(set(batch_ids))
        signal_audits[signal] = {
            "node_id": node_id,
            "modality": modality,
            "valid_row_count": len(valid_rows),
            "node_modality_valid_batch_count": len(node_batch_ids),
            "node_modality_valid_batch_ids_sample": node_batch_ids[:8],
            "pressure_headloss_event_valid_batch_count": len(pressure_event_batch_ids)
            if signal == FIELD_PROXY_PRESSURE_SIGNAL
            else 0,
            "pressure_headloss_event_valid_batch_ids_sample": pressure_event_batch_ids_for_signal[:8]
            if signal == FIELD_PROXY_PRESSURE_SIGNAL
            else [],
            "accepted_evidence_sources": accepted_evidence_sources,
            "pressure_source_conflict_audit": pressure_source_conflict_audit
            if signal == FIELD_PROXY_PRESSURE_SIGNAL
            else {},
            "valid_batch_count": len(batch_ids),
            "valid_batch_ids_sample": batch_ids[:8],
            "invalid_row_count": len(invalid_rows),
            "invalid_rows": invalid_rows[:8],
            "coverage_pass": len(batch_ids) >= FIELD_PROXY_HOLDOUT_MINIMUM_MATCHED_BATCHES,
        }
    all_signal_batches = set.intersection(*signal_batch_sets) if signal_batch_sets else set()
    missing_patch_signals = [
        signal for signal, audit in signal_audits.items() if not bool(audit.get("coverage_pass", False))
    ]
    return {
        "source_table": source_table,
        "fallback_table": FIELD_PROXY_LEGACY_SENSOR_TABLE if source_table == FIELD_PROXY_SENSOR_TABLE else FIELD_PROXY_SENSOR_TABLE,
        "required_sensor_table_format": "node_modality_sensor_timeseries_supplement",
        "accepted_sensor_status": sorted(ACCEPTED_SENSOR_STATUS),
        "required_patch_signals": required_signals,
        "accepted_pressure_evidence_sources": signal_audits.get(FIELD_PROXY_PRESSURE_SIGNAL, {}).get(
            "accepted_evidence_sources",
            [],
        ),
        "pressure_headloss_event_valid_batch_count": len(pressure_event_batch_ids),
        "pressure_source_resolution_record_count": len(pressure_resolution_by_batch),
        "pressure_source_resolution_required_fields": PRESSURE_SOURCE_RESOLUTION_FIELDS,
        "pressure_source_resolution_invalid_rows": pressure_resolution_audit.get("invalid_resolution_rows", []),
        "pressure_source_conflict_count": len(pressure_source_conflicts),
        "pressure_source_conflict_batch_ids_sample": [
            str(item)
            for item in _list(
                signal_audits.get(FIELD_PROXY_PRESSURE_SIGNAL, {})
                .get("pressure_source_conflict_audit", {})
                .get("pressure_source_conflict_batch_ids")
            )
        ][:8],
        "unresolved_pressure_source_conflict_count": len(unresolved_pressure_source_conflicts),
        "unresolved_pressure_source_conflict_batch_ids_sample": [
            str(item.get("batch_id"))
            for item in unresolved_pressure_source_conflicts
            if not FieldReplayImportAgent._is_missing_value(item.get("batch_id"))
        ][:8],
        "resolved_pressure_source_conflict_count": len(pressure_source_resolutions),
        "pressure_source_conflicts": pressure_source_conflicts[:12],
        "unresolved_pressure_source_conflicts": unresolved_pressure_source_conflicts[:12],
        "pressure_source_resolutions": pressure_source_resolutions[:12],
        "pressure_source_conflict_abs_tolerance_kPa": PRESSURE_SOURCE_CONFLICT_ABS_TOLERANCE_KPA,
        "pressure_source_conflict_rel_tolerance": PRESSURE_SOURCE_CONFLICT_REL_TOLERANCE,
        "pressure_source_resolution_fields": PRESSURE_SOURCE_RESOLUTION_FIELDS,
        "conflict_requires_operator_review": bool(unresolved_pressure_source_conflicts),
        "signal_audits": signal_audits,
        "missing_patch_signals": missing_patch_signals,
        "valid_all_signal_batch_count": len(all_signal_batches),
        "valid_all_signal_batch_ids": sorted(all_signal_batches),
        "valid_all_signal_batch_ids_sample": sorted(all_signal_batches)[:8],
    }


def _average_values_by_batch(rows: list[dict[str, Any]]) -> dict[str, float]:
    values: dict[str, list[float]] = {}
    for row in rows:
        batch_id = str(row.get("batch_id", "")).strip()
        value = row.get("value")
        if FieldReplayImportAgent._is_missing_value(batch_id) or value is None:
            continue
        values.setdefault(batch_id, []).append(float(value))
    return {
        batch_id: round(sum(batch_values) / len(batch_values), 6)
        for batch_id, batch_values in values.items()
        if batch_values
    }


def _pressure_headloss_event_pressure_values(table_profiles: dict[str, dict[str, Any]]) -> dict[str, float]:
    rows = _csv_rows(_dict(table_profiles.get(PRESSURE_HEADLOSS_TABLE, {})))
    values: dict[str, list[float]] = {}
    for row in rows:
        if str(row.get("bed_id", "")).strip() != "N3_catalyst_bed":
            continue
        batch_id = row.get("batch_id")
        if FieldReplayImportAgent._is_missing_value(batch_id):
            continue
        pressure_drop, pressure_error = FieldReplayImportAgent._parse_number(row.get("pressure_drop_kPa"))
        flow, flow_error = FieldReplayImportAgent._parse_number(row.get("flow_Lmin"))
        if pressure_error or flow_error or pressure_drop < 0 or flow <= 0:
            continue
        values.setdefault(str(batch_id), []).append(pressure_drop)
    return {
        batch_id: round(sum(batch_values) / len(batch_values), 6)
        for batch_id, batch_values in values.items()
        if batch_values
    }


def _pressure_source_conflict_audit(
    node_pressure_values: dict[str, float],
    pressure_event_values: dict[str, float],
    pressure_resolution_by_batch: dict[str, Any],
) -> dict[str, Any]:
    conflicts: list[dict[str, Any]] = []
    unresolved_conflicts: list[dict[str, Any]] = []
    resolutions: list[dict[str, Any]] = []
    for batch_id in sorted(set(node_pressure_values) & set(pressure_event_values)):
        node_value = float(node_pressure_values[batch_id])
        event_value = float(pressure_event_values[batch_id])
        difference = abs(node_value - event_value)
        tolerance = max(
            PRESSURE_SOURCE_CONFLICT_ABS_TOLERANCE_KPA,
            PRESSURE_SOURCE_CONFLICT_REL_TOLERANCE * max(abs(node_value), abs(event_value), 1e-6),
        )
        if difference <= tolerance:
            continue
        conflict = {
            "batch_id": batch_id,
            "node_modality_pressure_drop_kPa": round(node_value, 6),
            "pressure_headloss_event_pressure_drop_kPa": round(event_value, 6),
            "absolute_difference_kPa": round(difference, 6),
            "conflict_tolerance_kPa": round(tolerance, 6),
            "source_tables": [FIELD_PROXY_SENSOR_TABLE, PRESSURE_HEADLOSS_TABLE],
            "required_action": "operator_review_and_pressure_source_calibration_patch_before_agent51_scoring",
        }
        resolution = _dict(pressure_resolution_by_batch.get(batch_id))
        if resolution:
            resolved = {
                **conflict,
                "authoritative_pressure_source": resolution.get("authoritative_pressure_source"),
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
    return {
        "pressure_source_conflict_count": len(conflicts),
        "pressure_source_conflict_batch_ids": [str(item["batch_id"]) for item in conflicts],
        "resolved_pressure_source_conflict_count": len(resolutions),
        "unresolved_pressure_source_conflict_count": len(unresolved_conflicts),
        "unresolved_pressure_source_conflict_batch_ids": [
            str(item["batch_id"]) for item in unresolved_conflicts
        ],
        "pressure_source_conflicts": conflicts,
        "pressure_source_resolutions": resolutions,
        "unresolved_pressure_source_conflicts": unresolved_conflicts,
        "conflict_requires_operator_review": bool(unresolved_conflicts),
    }


def _pressure_source_resolution_records(table_profiles: dict[str, dict[str, Any]]) -> dict[str, Any]:
    records: dict[str, dict[str, Any]] = {}
    invalid_rows: list[dict[str, Any]] = []
    for table in (PRESSURE_HEADLOSS_TABLE, "campaign_operation_log"):
        for index, row in enumerate(_csv_rows(_dict(table_profiles.get(table, {})))):
            if not any(not FieldReplayImportAgent._is_missing_value(row.get(field)) for field in PRESSURE_SOURCE_RESOLUTION_FIELDS):
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
            batch_id = str(parsed["batch_id"])
            records.setdefault(batch_id, parsed)
    return {
        "required_fields": PRESSURE_SOURCE_RESOLUTION_FIELDS,
        "accepted_resolution_tokens": sorted(PRESSURE_SOURCE_RESOLUTION_TOKENS),
        "accepted_authoritative_sources": sorted({FIELD_PROXY_SENSOR_TABLE, PRESSURE_HEADLOSS_TABLE}),
        "valid_resolution_count": len(records),
        "valid_resolution_batch_ids": sorted(records),
        "valid_resolution_by_batch": records,
        "invalid_resolution_count": len(invalid_rows),
        "invalid_resolution_rows": invalid_rows[:12],
    }


def _parse_pressure_source_resolution_row(
    row: dict[str, Any],
    table: str,
    index: int,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    errors: list[dict[str, Any]] = []
    batch_id = row.get("batch_id")
    if FieldReplayImportAgent._is_missing_value(batch_id):
        errors.append({"field": "batch_id", "error": "missing_batch_id", "value": batch_id})
    resolution_token = str(row.get("pressure_source_resolution", "")).strip().lower()
    if FieldReplayImportAgent._is_missing_value(resolution_token):
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
                "accepted": sorted({FIELD_PROXY_SENSOR_TABLE, PRESSURE_HEADLOSS_TABLE}),
            }
        )
    for field in ("reviewer_id", "review_time", "calibration_action_id", "calibration_note"):
        if FieldReplayImportAgent._is_missing_value(row.get(field)):
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
    if FieldReplayImportAgent._is_missing_value(value):
        return None
    return PRESSURE_SOURCE_ALIASES.get(str(value).strip().lower())


def _field_proxy_lab_label_audit(table_profiles: dict[str, dict[str, Any]]) -> dict[str, Any]:
    profile = _dict(table_profiles.get("offline_lab_results", {}))
    rows = _csv_rows(profile)
    valid_batch_ids: set[str] = set()
    invalid_rows: list[dict[str, Any]] = []
    for index, row in enumerate(rows):
        if str(row.get("analyte", "")).strip() != FIELD_PROXY_REQUIRED_ANALYTE:
            continue
        errors: list[dict[str, Any]] = []
        batch_id = row.get("batch_id")
        if FieldReplayImportAgent._is_missing_value(batch_id):
            errors.append({"field": "batch_id", "error": "missing_batch_id", "value": batch_id})
        value, value_error = FieldReplayImportAgent._parse_number(row.get("value"))
        if value_error:
            errors.append({"field": "value", "error": value_error, "value": row.get("value")})
        elif value < 0:
            errors.append({"field": "value", "error": "negative_lab_value", "value": row.get("value")})
        _, label_time_error = FieldReplayImportAgent._parse_number(row.get("lab_label_time_min"))
        if label_time_error:
            errors.append({"field": "lab_label_time_min", "error": label_time_error, "value": row.get("lab_label_time_min")})
        qa_token = str(row.get("qa_flag", "")).strip().lower()
        if FieldReplayImportAgent._is_missing_value(row.get("qa_flag")):
            errors.append({"field": "qa_flag", "error": "missing_qa_flag", "value": row.get("qa_flag")})
        elif qa_token not in ACCEPTED_LAB_QA_FLAGS:
            errors.append({"field": "qa_flag", "error": "qa_flag_not_pass", "value": row.get("qa_flag")})
        if errors:
            invalid_rows.append({"row_index": index, "batch_id": batch_id, "errors": errors})
            continue
        valid_batch_ids.add(str(batch_id))
    return {
        "required_analyte": FIELD_PROXY_REQUIRED_ANALYTE,
        "valid_catalyst_activity_label_count": len(valid_batch_ids),
        "valid_catalyst_activity_batch_ids": sorted(valid_batch_ids),
        "valid_catalyst_activity_batch_ids_sample": sorted(valid_batch_ids)[:8],
        "invalid_catalyst_activity_label_rows": invalid_rows[:8],
        "catalyst_activity_label_pass": len(valid_batch_ids) >= FIELD_PROXY_HOLDOUT_MINIMUM_MATCHED_BATCHES,
    }


def _field_proxy_operation_audit(table_profiles: dict[str, dict[str, Any]]) -> dict[str, Any]:
    profile = _dict(table_profiles.get("campaign_operation_log", {}))
    rows = _csv_rows(profile)
    valid_batch_ids: set[str] = set()
    invalid_rows: list[dict[str, Any]] = []
    for index, row in enumerate(rows):
        errors: list[dict[str, Any]] = []
        batch_id = row.get("batch_id")
        if FieldReplayImportAgent._is_missing_value(batch_id):
            errors.append({"field": "batch_id", "error": "missing_batch_id", "value": batch_id})
        _, bool_error = FieldReplayImportAgent._parse_bool(row.get("regeneration_event"))
        if bool_error:
            errors.append({"field": "regeneration_event", "error": bool_error, "value": row.get("regeneration_event")})
        for field in ("command_time_min", "effect_time_min"):
            _, time_error = FieldReplayImportAgent._parse_number(row.get(field))
            if time_error:
                errors.append({"field": field, "error": time_error, "value": row.get(field)})
        if errors:
            invalid_rows.append({"row_index": index, "batch_id": batch_id, "errors": errors})
            continue
        valid_batch_ids.add(str(batch_id))
    return {
        "valid_regeneration_event_count": len(valid_batch_ids),
        "valid_regeneration_event_batch_ids": sorted(valid_batch_ids),
        "valid_regeneration_event_batch_ids_sample": sorted(valid_batch_ids)[:8],
        "invalid_regeneration_event_rows": invalid_rows[:8],
        "regeneration_event_pass": len(valid_batch_ids) >= FIELD_PROXY_HOLDOUT_MINIMUM_MATCHED_BATCHES,
    }


def _field_proxy_geometry_audit(table_profiles: dict[str, dict[str, Any]]) -> dict[str, Any]:
    profile = _dict(table_profiles.get(FIELD_PROXY_GEOMETRY_TABLE, {}))
    rows = _csv_rows(profile)
    valid_rows: list[dict[str, Any]] = []
    invalid_rows: list[dict[str, Any]] = []
    for index, row in enumerate(rows):
        errors: list[dict[str, Any]] = []
        if FieldReplayImportAgent._is_missing_value(row.get("node_id")):
            errors.append({"field": "node_id", "error": "missing_node_id", "value": row.get("node_id")})
        for field in ("bed_volume", "nominal_HRT_min", "flow_Lmin"):
            value, value_error = FieldReplayImportAgent._parse_number(row.get(field))
            if value_error:
                errors.append({"field": field, "error": value_error, "value": row.get(field)})
            elif value <= 0:
                errors.append({"field": field, "error": "non_positive_geometry_value", "value": row.get(field)})
        if errors:
            invalid_rows.append({"row_index": index, "node_id": row.get("node_id"), "errors": errors})
            continue
        valid_rows.append({"node_id": str(row.get("node_id"))})
    return {
        "target_table": FIELD_PROXY_GEOMETRY_TABLE,
        "valid_geometry_row_count": len(valid_rows),
        "valid_geometry_node_ids": sorted({row["node_id"] for row in valid_rows}),
        "invalid_geometry_rows": invalid_rows[:8],
        "geometry_coverage_pass": len(valid_rows) > 0,
    }


def _csv_rows(profile: dict[str, Any]) -> list[dict[str, Any]]:
    path = profile.get("path")
    if path in {None, ""}:
        return []
    csv_path = Path(str(path))
    if not csv_path.exists():
        return []
    with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return [dict(row) for row in reader]


def _minimum_replay_contract_audit(table_profiles: dict[str, dict[str, Any]]) -> dict[str, Any]:
    batch_sets = {
        table: set(_list(_dict(table_profiles.get(table, {})).get("unique_values_by_field", {}).get("batch_id")))
        for table in REPLAY_TABLES
    }
    table_row_counts = {
        table: int(_dict(table_profiles.get(table, {})).get("row_count", 0) or 0)
        for table in REPLAY_TABLES
    }
    if all(batch_sets.values()):
        common_batches = set.intersection(*batch_sets.values())
    else:
        common_batches = set()
    missing_row_tables = [table for table, count in table_row_counts.items() if count <= 0]
    time_order_violations = {
        table: _list(_dict(table_profiles.get(table, {})).get("time_order_violations"))
        for table in REPLAY_TABLES
    }
    time_order_violation_count = sum(len(items) for items in time_order_violations.values())
    common_batch_count = len(common_batches)
    operation_action_quality = _dict(_dict(table_profiles.get("campaign_operation_log", {})).get("operation_action_quality"))
    valid_operation_action_count = int(operation_action_quality.get("valid_operation_action_count", 0) or 0)
    invalid_operation_action_count = int(operation_action_quality.get("invalid_operation_action_count", 0) or 0)
    valid_operation_batches = set(_list(operation_action_quality.get("valid_operation_action_batch_ids")))
    lab_result_quality = _dict(_dict(table_profiles.get("offline_lab_results", {})).get("lab_result_quality"))
    valid_lab_result_count = int(lab_result_quality.get("valid_lab_result_count", 0) or 0)
    invalid_lab_result_count = int(lab_result_quality.get("invalid_lab_result_count", 0) or 0)
    valid_lab_batches = set(_list(lab_result_quality.get("valid_lab_result_batch_ids")))
    proxy_event_count = table_row_counts.get("fast_proxy_event_log", 0)
    proxy_label_quality = _dict(_dict(table_profiles.get("fast_proxy_event_log", {})).get("proxy_label_quality"))
    valid_proxy_label_count = int(proxy_label_quality.get("valid_proxy_label_count", 0) or 0)
    invalid_proxy_label_count = int(proxy_label_quality.get("invalid_proxy_label_count", 0) or 0)
    valid_proxy_batches = set(_list(proxy_label_quality.get("valid_proxy_label_batch_ids")))
    pressure_event_count = table_row_counts.get(PRESSURE_HEADLOSS_TABLE, 0)
    pressure_headloss_quality = _dict(
        _dict(table_profiles.get(PRESSURE_HEADLOSS_TABLE, {})).get("pressure_headloss_quality")
    )
    valid_pressure_headloss_event_count = int(
        pressure_headloss_quality.get("valid_pressure_headloss_event_count", 0) or 0
    )
    invalid_pressure_headloss_event_count = int(
        pressure_headloss_quality.get("invalid_pressure_headloss_event_count", 0) or 0
    )
    valid_pressure_batches = set(_list(pressure_headloss_quality.get("valid_pressure_headloss_batch_ids")))
    valid_pressure_batch_count = len(valid_pressure_batches)
    valid_matched_batches = (
        common_batches
        & valid_operation_batches
        & valid_lab_batches
        & valid_proxy_batches
        & valid_pressure_batches
    )
    valid_matched_batch_count = len(valid_matched_batches)
    if missing_row_tables:
        status = "minimum_replay_contract_blocked_missing_rows"
    elif time_order_violation_count:
        status = "minimum_replay_contract_time_order_gaps"
    elif common_batch_count < MINIMUM_SMOKE_TEST_MATCHED_BATCHES:
        status = "minimum_replay_contract_batch_linkage_gaps"
    elif valid_operation_action_count < MINIMUM_SMOKE_TEST_MATCHED_BATCHES:
        status = "minimum_replay_contract_operation_action_quality_gaps"
    elif valid_lab_result_count < MINIMUM_SMOKE_TEST_MATCHED_BATCHES:
        status = "minimum_replay_contract_lab_result_quality_gaps"
    elif proxy_event_count < MINIMUM_SMOKE_TEST_MATCHED_BATCHES:
        status = "minimum_replay_contract_proxy_event_gaps"
    elif valid_proxy_label_count < MINIMUM_SMOKE_TEST_MATCHED_BATCHES:
        status = "minimum_replay_contract_proxy_label_quality_gaps"
    elif pressure_event_count < MINIMUM_SMOKE_TEST_MATCHED_BATCHES:
        status = "minimum_replay_contract_pressure_headloss_event_gaps"
    elif valid_pressure_headloss_event_count < MINIMUM_SMOKE_TEST_MATCHED_BATCHES:
        status = "minimum_replay_contract_pressure_headloss_quality_gaps"
    elif valid_pressure_batch_count < MINIMUM_SMOKE_TEST_MATCHED_BATCHES:
        status = "minimum_replay_contract_pressure_headloss_quality_gaps"
    elif valid_matched_batch_count < MINIMUM_SMOKE_TEST_MATCHED_BATCHES:
        status = "minimum_replay_contract_valid_matched_batch_gaps"
    else:
        status = "minimum_replay_contract_ready_for_agent42_smoke_test"
    return {
        "contract_id": "R7_minimum_timestamped_replay_package_contract",
        "minimum_smoke_test_matched_batch_count": MINIMUM_SMOKE_TEST_MATCHED_BATCHES,
        "recommended_calibration_proxy_event_count": RECOMMENDED_CALIBRATION_PROXY_EVENTS,
        "required_tables": REPLAY_TABLES,
        "table_row_counts": table_row_counts,
        "table_batch_counts": {table: len(values) for table, values in batch_sets.items()},
        "common_batch_count": common_batch_count,
        "common_batch_ids_sample": sorted(common_batches)[:8],
        "valid_matched_batch_count": valid_matched_batch_count,
        "valid_matched_batch_ids_sample": sorted(valid_matched_batches)[:8],
        "valid_operation_action_count": valid_operation_action_count,
        "invalid_operation_action_count": invalid_operation_action_count,
        "operation_action_quality": operation_action_quality,
        "valid_lab_result_count": valid_lab_result_count,
        "invalid_lab_result_count": invalid_lab_result_count,
        "lab_result_quality": lab_result_quality,
        "proxy_event_count": proxy_event_count,
        "valid_proxy_label_count": valid_proxy_label_count,
        "invalid_proxy_label_count": invalid_proxy_label_count,
        "proxy_label_quality": proxy_label_quality,
        "pressure_headloss_event_count": pressure_event_count,
        "valid_pressure_headloss_event_count": valid_pressure_headloss_event_count,
        "invalid_pressure_headloss_event_count": invalid_pressure_headloss_event_count,
        "valid_pressure_headloss_batch_count": valid_pressure_batch_count,
        "pressure_headloss_quality": pressure_headloss_quality,
        "missing_row_tables": missing_row_tables,
        "time_order_violation_count": time_order_violation_count,
        "time_order_violations": time_order_violations,
        "status": status,
        "contract_pass": status == "minimum_replay_contract_ready_for_agent42_smoke_test",
        "batch_linkage_requirement": (
            "At least three batch_id values should appear across sensor_timeseries, offline_lab_results, "
            "campaign_operation_log, fast_proxy_event_log and pressure_headloss_event_log for an Agent42 smoke replay."
        ),
        "valid_matched_batch_requirement": (
            "At least three common batch_id values should also have QA-passed offline lab results and valid "
            "operation actions, field-labeled fast-proxy events and valid pressure/headloss events on the same batch_id."
        ),
        "time_order_constraints": [
            "offline_lab_results: sample_time_min <= result_time_min",
            "campaign_operation_log: command_time_min <= effect_time_min <= end_min and start_min <= end_min",
            "fast_proxy_event_log: event_time_min <= lab_label_time_min",
        ],
        "calibration_note": (
            "Three matched batches are a smoke-test floor; field calibration should target at least "
            f"{RECOMMENDED_CALIBRATION_PROXY_EVENTS} proxy events before protective control tuning."
        ),
    }


def _coverage_readiness(
    claim_audit: list[dict[str, Any]],
    soft_holdout_audit: dict[str, Any],
    field_proxy_holdout_audit: dict[str, Any],
    minimum_replay_contract: dict[str, Any],
    preflight: dict[str, Any],
) -> dict[str, Any]:
    total_claims = len(claim_audit)
    passed_claims = sum(1 for row in claim_audit if row["coverage_pass"])
    claim_rate = round(passed_claims / max(1, total_claims), 3)
    soft_pass = bool(soft_holdout_audit["coverage_pass"])
    field_proxy_pass = bool(field_proxy_holdout_audit["coverage_pass"])
    pressure_conflict_count = int(field_proxy_holdout_audit.get("pressure_source_conflict_count", 0) or 0)
    unresolved_pressure_conflict_count = int(
        field_proxy_holdout_audit.get("unresolved_pressure_source_conflict_count", 0) or 0
    )
    resolved_pressure_conflict_count = int(
        field_proxy_holdout_audit.get("resolved_pressure_source_conflict_count", 0) or 0
    )
    pressure_resolution_record_count = int(
        field_proxy_holdout_audit.get("pressure_source_resolution_record_count", 0) or 0
    )
    pressure_conflict_requires_review = bool(
        field_proxy_holdout_audit.get("conflict_requires_operator_review", False)
    )
    preflight_status = str(preflight.get("status", "unknown"))
    if preflight_status != "field_package_preflight_ready_for_agent42":
        status = "field_package_coverage_blocked_before_import"
    elif claim_rate < 0.95:
        status = "field_package_claim_specific_coverage_gaps"
    elif not soft_pass:
        status = "field_package_soft_holdout_coverage_gaps"
    elif not field_proxy_pass:
        status = "field_package_field_proxy_holdout_gaps"
    else:
        status = "field_package_coverage_ready_for_replay_and_holdout"
    base_readiness = {
        "field_package_coverage_status": status,
        "claim_need_count": total_claims,
        "claim_need_pass_count": passed_claims,
        "claim_specific_coverage_rate": claim_rate,
        "soft_holdout_coverage_pass": soft_pass,
        "field_proxy_holdout_status": field_proxy_holdout_audit.get("status", "unknown"),
        "field_proxy_holdout_required": bool(field_proxy_holdout_audit.get("holdout_required", False)),
        "field_proxy_holdout_coverage_pass": field_proxy_pass,
        "field_proxy_holdout_matched_batch_count": field_proxy_holdout_audit.get("matched_proxy_holdout_batch_count", 0),
        "field_proxy_holdout_minimum_matched_batch_count": field_proxy_holdout_audit.get(
            "minimum_matched_batch_count",
            FIELD_PROXY_HOLDOUT_MINIMUM_MATCHED_BATCHES,
        ),
        "pressure_source_conflict_count": pressure_conflict_count,
        "resolved_pressure_source_conflict_count": resolved_pressure_conflict_count,
        "unresolved_pressure_source_conflict_count": unresolved_pressure_conflict_count,
        "pressure_source_resolution_record_count": pressure_resolution_record_count,
        "pressure_source_conflict_requires_operator_review": pressure_conflict_requires_review,
        "pressure_source_conflict_batch_ids_sample": field_proxy_holdout_audit.get(
            "pressure_source_conflict_batch_ids_sample",
            [],
        ),
        "unresolved_pressure_source_conflict_batch_ids_sample": field_proxy_holdout_audit.get(
            "unresolved_pressure_source_conflict_batch_ids_sample",
            [],
        ),
        "field_package_pressure_conflict_resolution_status": (
            "pressure_source_conflicts_require_field_patch"
            if pressure_conflict_requires_review
            else "pressure_source_conflicts_resolved_by_operator_review"
            if pressure_conflict_count and resolved_pressure_conflict_count == pressure_conflict_count
            else "pressure_source_conflict_resolution_clear"
        ),
        "field_package_pressure_conflict_resolution_ready": not pressure_conflict_requires_review,
        "preflight_status": preflight_status,
        "minimum_replay_contract_status": minimum_replay_contract["status"],
        "minimum_replay_contract_pass": bool(minimum_replay_contract["contract_pass"]),
        "minimum_common_batch_count": minimum_replay_contract["common_batch_count"],
        "minimum_valid_matched_batch_count": minimum_replay_contract["valid_matched_batch_count"],
        "minimum_valid_operation_action_count": minimum_replay_contract["valid_operation_action_count"],
        "minimum_invalid_operation_action_count": minimum_replay_contract["invalid_operation_action_count"],
        "minimum_valid_lab_result_count": minimum_replay_contract["valid_lab_result_count"],
        "minimum_invalid_lab_result_count": minimum_replay_contract["invalid_lab_result_count"],
        "minimum_proxy_event_count": minimum_replay_contract["proxy_event_count"],
        "minimum_valid_proxy_label_count": minimum_replay_contract["valid_proxy_label_count"],
        "minimum_invalid_proxy_label_count": minimum_replay_contract["invalid_proxy_label_count"],
        "minimum_pressure_headloss_event_count": minimum_replay_contract["pressure_headloss_event_count"],
        "minimum_valid_pressure_headloss_event_count": minimum_replay_contract[
            "valid_pressure_headloss_event_count"
        ],
        "minimum_invalid_pressure_headloss_event_count": minimum_replay_contract[
            "invalid_pressure_headloss_event_count"
        ],
        "minimum_valid_pressure_headloss_batch_count": minimum_replay_contract[
            "valid_pressure_headloss_batch_count"
        ],
        "minimum_time_order_violation_count": minimum_replay_contract["time_order_violation_count"],
        "can_support_claim_specific_review": claim_rate >= 0.95,
        "can_support_soft_sensor_holdout": soft_pass,
        "can_support_agent51_field_proxy_holdout": field_proxy_pass,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
    }
    sufficiency_gate = _field_evidence_sufficiency_gate(base_readiness, minimum_replay_contract)
    return {
        **base_readiness,
        "field_evidence_sufficiency_gate": sufficiency_gate,
        "field_evidence_sufficiency_status": sufficiency_gate["field_evidence_sufficiency_status"],
        "field_evidence_sufficiency_score": sufficiency_gate["field_evidence_sufficiency_score"],
        "field_evidence_smoke_pass": sufficiency_gate["field_evidence_smoke_pass"],
        "field_evidence_calibration_volume_pass": sufficiency_gate["field_evidence_calibration_volume_pass"],
        "can_route_to_agent42_smoke_replay": sufficiency_gate["can_route_to_agent42_smoke_replay"],
        "can_route_to_field_holdout": sufficiency_gate["can_route_to_field_holdout"],
        "can_route_to_human_review_candidate": sufficiency_gate["can_route_to_human_review_candidate"],
        "field_supported_claim_upgrade_ready": sufficiency_gate["field_supported_claim_upgrade_ready"],
        "control_candidate_ready": sufficiency_gate["control_candidate_ready"],
        "release_gate_candidate_ready": sufficiency_gate["release_gate_candidate_ready"],
        "no_write_boundary_pass": sufficiency_gate["no_write_boundary_pass"],
    }


def _field_evidence_sufficiency_gate(
    readiness: dict[str, Any],
    minimum_replay_contract: dict[str, Any],
) -> dict[str, Any]:
    """Assess whether a field package is merely importable, replay-smoke-ready, or review-ready."""

    checks = [
        _sufficiency_check(
            "field_origin_import",
            "Field provenance/import preflight is ready.",
            str(readiness.get("preflight_status", "")) == "field_package_preflight_ready_for_agent42",
            0.20,
            "field package import/preflight is not ready",
        ),
        _sufficiency_check(
            "claim_specific_rows",
            "Claim-specific required rows and fields are sufficiently covered.",
            float(readiness.get("claim_specific_coverage_rate", 0.0) or 0.0) >= 0.95,
            0.12,
            "claim-specific field rows or required fields are missing",
        ),
        _sufficiency_check(
            "soft_sensor_holdout_labels",
            "Soft-sensor holdout labels and weak targets are present.",
            bool(readiness.get("soft_holdout_coverage_pass", False)),
            0.12,
            "soft-sensor holdout labels or weak-target analytes are missing",
        ),
        _sufficiency_check(
            "catalyst_proxy_holdout",
            "Catalyst proxy holdout contract is satisfied when requested.",
            bool(readiness.get("field_proxy_holdout_coverage_pass", False)),
            0.14,
            "catalyst proxy holdout evidence is missing or blocked",
        ),
        _sufficiency_check(
            "minimum_replay_contract",
            "Minimum same-batch timestamped replay contract is satisfied.",
            bool(readiness.get("minimum_replay_contract_pass", False)),
            0.16,
            "minimum replay contract is not satisfied",
        ),
        _sufficiency_check(
            "temporal_alignment",
            "Sensor/lab/operation/proxy timing has no detected ordering violation.",
            int(readiness.get("minimum_time_order_violation_count", 0) or 0) == 0,
            0.08,
            "time-order violations remain in replay tables",
        ),
        _sufficiency_check(
            "pressure_conflict_resolution",
            "Pressure/headloss source conflicts are absent or operator-resolved.",
            bool(readiness.get("field_package_pressure_conflict_resolution_ready", False)),
            0.08,
            "pressure source conflict requires operator review",
        ),
        _sufficiency_check(
            "no_write_boundary",
            "Coverage gate cannot write actuator or release-gate policy.",
            not bool(readiness.get("can_write_to_actuator", False))
            and not bool(readiness.get("can_write_to_release_gate", False)),
            0.10,
            "no-write boundary is not explicit",
        ),
    ]
    score = round(sum(float(check["weight"]) for check in checks if bool(check["passed"])), 3)
    smoke_pass = all(
        bool(check["passed"])
        for check in checks
        if check["check_id"] not in {"no_write_boundary"}
    ) and bool(_check_by_id(checks, "no_write_boundary")["passed"])
    calibration_volume_pass = (
        int(minimum_replay_contract.get("proxy_event_count", 0) or 0) >= RECOMMENDED_CALIBRATION_PROXY_EVENTS
        and int(minimum_replay_contract.get("valid_proxy_label_count", 0) or 0) >= RECOMMENDED_CALIBRATION_PROXY_EVENTS
        and int(minimum_replay_contract.get("valid_matched_batch_count", 0) or 0) >= RECOMMENDED_CALIBRATION_PROXY_EVENTS
    )
    blocking_reasons = [str(check["blocking_reason"]) for check in checks if not bool(check["passed"])]
    if not smoke_pass:
        status = _sufficiency_blocked_status(readiness, minimum_replay_contract)
    elif not calibration_volume_pass:
        status = "field_evidence_sufficiency_smoke_ready_needs_calibration_event_volume"
    else:
        status = "field_evidence_sufficiency_ready_for_replay_holdout_and_human_review_queue"
    if smoke_pass and not calibration_volume_pass:
        blocking_reasons.append(
            f"field calibration volume below recommended {RECOMMENDED_CALIBRATION_PROXY_EVENTS} same-batch proxy events"
        )
    return {
        "gate_id": "R7_field_evidence_sufficiency_gate",
        "field_evidence_sufficiency_status": status,
        "field_evidence_sufficiency_score": score,
        "field_evidence_smoke_pass": smoke_pass,
        "field_evidence_calibration_volume_pass": calibration_volume_pass,
        "minimum_smoke_matched_batch_count": MINIMUM_SMOKE_TEST_MATCHED_BATCHES,
        "recommended_calibration_proxy_event_count": RECOMMENDED_CALIBRATION_PROXY_EVENTS,
        "current_valid_matched_batch_count": int(minimum_replay_contract.get("valid_matched_batch_count", 0) or 0),
        "current_valid_proxy_label_count": int(minimum_replay_contract.get("valid_proxy_label_count", 0) or 0),
        "current_proxy_event_count": int(minimum_replay_contract.get("proxy_event_count", 0) or 0),
        "checks": checks,
        "blocking_reasons": blocking_reasons,
        "can_route_to_agent42_smoke_replay": smoke_pass,
        "can_route_to_field_holdout": smoke_pass,
        "can_route_to_human_review_candidate": smoke_pass and calibration_volume_pass,
        "field_supported_claim_upgrade_ready": False,
        "control_candidate_ready": False,
        "release_gate_candidate_ready": False,
        "no_write_boundary_pass": bool(_check_by_id(checks, "no_write_boundary")["passed"]),
        "no_write_boundary": {
            "can_write_to_actuator": False,
            "can_write_to_release_gate": False,
            "can_write_field_supported_claim": False,
            "why": (
                "This gate only proves data sufficiency for replay, holdout, and human-review queueing. "
                "Field-supported claims, actuator candidates, and release-gate candidates require downstream R7 gates."
            ),
        },
        "field_boundary": (
            "A sufficient field package is not a deployed-control result. It only permits downstream replay, "
            "field holdout, unified evidence review, and human review."
        ),
    }


def _sufficiency_check(
    check_id: str,
    requirement: str,
    passed: bool,
    weight: float,
    blocking_reason: str,
) -> dict[str, Any]:
    return {
        "check_id": check_id,
        "requirement": requirement,
        "passed": bool(passed),
        "weight": weight,
        "blocking_reason": "" if passed else blocking_reason,
    }


def _check_by_id(checks: list[dict[str, Any]], check_id: str) -> dict[str, Any]:
    for check in checks:
        if check["check_id"] == check_id:
            return check
    return {"passed": False}


def _sufficiency_blocked_status(
    readiness: dict[str, Any],
    minimum_replay_contract: dict[str, Any],
) -> str:
    preflight_status = str(readiness.get("preflight_status", ""))
    if preflight_status != "field_package_preflight_ready_for_agent42":
        return "field_evidence_sufficiency_blocked_before_import"
    if float(readiness.get("claim_specific_coverage_rate", 0.0) or 0.0) < 0.95:
        return "field_evidence_sufficiency_blocked_claim_specific_rows"
    if not bool(readiness.get("soft_holdout_coverage_pass", False)):
        return "field_evidence_sufficiency_blocked_soft_sensor_holdout"
    if not bool(readiness.get("field_proxy_holdout_coverage_pass", False)):
        return "field_evidence_sufficiency_blocked_catalyst_proxy_holdout"
    if str(minimum_replay_contract.get("status", "")) != "minimum_replay_contract_ready_for_agent42_smoke_test":
        return "field_evidence_sufficiency_blocked_minimum_replay_contract"
    if int(readiness.get("minimum_time_order_violation_count", 0) or 0):
        return "field_evidence_sufficiency_blocked_temporal_alignment"
    if not bool(readiness.get("field_package_pressure_conflict_resolution_ready", False)):
        return "field_evidence_sufficiency_blocked_pressure_source_resolution"
    return "field_evidence_sufficiency_blocked_unknown"


def _next_actions(
    readiness: dict[str, Any],
    claim_audit: list[dict[str, Any]],
    soft_holdout_audit: dict[str, Any],
    field_proxy_holdout_audit: dict[str, Any],
) -> list[str]:
    status = str(readiness["field_package_coverage_status"])
    if status == "field_package_coverage_blocked_before_import":
        return ["Fix preflight/import blockers before interpreting claim or soft-holdout coverage."]
    actions: list[str] = []
    failed_claims = [row for row in claim_audit if not row["coverage_pass"]]
    if failed_claims:
        first = failed_claims[0]
        actions.append(
            f"Patch claim need {first.get('need_id')}: {', '.join(first['claim_upgrade_blocked_by'])}."
        )
    if soft_holdout_audit["missing_weak_target_analytes"]:
        actions.append(
            "Add offline_lab_results analytes for weak targets: "
            + ", ".join(soft_holdout_audit["missing_weak_target_analytes"])
            + "."
        )
    if bool(field_proxy_holdout_audit.get("holdout_required", False)) and not bool(
        field_proxy_holdout_audit.get("coverage_pass", False)
    ):
        if bool(field_proxy_holdout_audit.get("conflict_requires_operator_review", False)):
            actions.append(
                "Resolve pressure source conflicts between node_modality_sensor_timeseries and "
                "pressure_headloss_event_log before Agent51 scoring or Agent49/52 guardrail relaxation."
            )
        missing_signals = _list(_dict(field_proxy_holdout_audit.get("sensor_signal_audit")).get("missing_patch_signals"))
        if missing_signals:
            actions.append(
                "Add same-batch node/modality sensor rows for Agent51 catalyst proxy signals: "
                + ", ".join(str(item) for item in missing_signals)
                + "."
            )
        if _dict(field_proxy_holdout_audit.get("missing_required_fields_by_table")):
            actions.append("Patch R7j catalyst proxy holdout fields before relaxing catalyst uncertainty.")
    if not actions:
        actions.append("Coverage is ready; proceed to replay, soft holdout calibration and human review gates.")
    actions.append("Coverage readiness is not deployment permission; actuator and release-gate writeback remain forbidden.")
    return actions


def _patch_plan(
    readiness: dict[str, Any],
    preflight: dict[str, Any],
    claim_audit: list[dict[str, Any]],
    soft_holdout_audit: dict[str, Any],
    field_proxy_holdout_audit: dict[str, Any],
    minimum_replay_contract: dict[str, Any],
) -> dict[str, Any]:
    status = str(readiness["field_package_coverage_status"])
    pressure_conflict_requires_review = bool(
        _dict(field_proxy_holdout_audit.get("sensor_signal_audit")).get(
            "conflict_requires_operator_review",
            False,
        )
    )
    if status == "field_package_coverage_blocked_before_import":
        next_stage = "R7a_import_preflight"
        items = _preflight_patch_items(preflight)
    elif status == "field_package_claim_specific_coverage_gaps":
        next_stage = "R7g_claim_specific_field_package_patch"
        items = _claim_patch_items(claim_audit)
    elif status == "field_package_soft_holdout_coverage_gaps":
        next_stage = "R7h_soft_holdout_weak_target_patch"
        items = _soft_holdout_patch_items(soft_holdout_audit) + _minimum_replay_patch_items(minimum_replay_contract)
    elif status == "field_package_field_proxy_holdout_gaps":
        next_stage = (
            "R8m_pressure_source_conflict_field_patch_requirements"
            if pressure_conflict_requires_review
            else "R7j_catalyst_proxy_field_holdout_patch"
        )
        items = _field_proxy_holdout_patch_items(field_proxy_holdout_audit) + _minimum_replay_patch_items(
            minimum_replay_contract
        )
    elif not minimum_replay_contract["contract_pass"]:
        next_stage = "R7i_minimum_replay_contract_patch"
        items = _minimum_replay_patch_items(minimum_replay_contract)
    else:
        next_stage = "R7b_replay_and_holdout_gate_execution"
        items = []
    plan_status = _patch_plan_status(status, bool(minimum_replay_contract["contract_pass"]))
    if pressure_conflict_requires_review:
        plan_status = "patch_plan_requires_pressure_source_conflict_resolution"
    return {
        "patch_plan_status": plan_status,
        "next_blocking_stage": next_stage,
        "item_count": len(items),
        "items": items,
        "operator_checklist": _operator_checklist(plan_status, items),
        "can_execute_without_real_field_values": False,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
        "field_boundary": (
            "Patch plan items only describe missing evidence needed for replay and claim review. "
            "They do not authorize field-supported claims, actuator writeback or release-gate writeback."
        ),
    }


def _patch_plan_status(coverage_status: str, minimum_replay_contract_pass: bool) -> str:
    mapping = {
        "field_package_coverage_blocked_before_import": "patch_plan_blocked_at_import_preflight",
        "field_package_claim_specific_coverage_gaps": "patch_plan_requires_claim_specific_fields",
        "field_package_soft_holdout_coverage_gaps": "patch_plan_requires_soft_holdout_weak_targets",
        "field_package_field_proxy_holdout_gaps": "patch_plan_requires_catalyst_proxy_field_holdout",
        "field_package_coverage_ready_for_replay_and_holdout": "patch_plan_ready_for_replay_and_holdout",
    }
    if coverage_status == "field_package_coverage_ready_for_replay_and_holdout" and not minimum_replay_contract_pass:
        return "patch_plan_requires_minimum_replay_contract"
    return mapping.get(coverage_status, "patch_plan_unknown")


def _preflight_patch_items(preflight: dict[str, Any]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    placeholder_fields = [str(field) for field in _list(preflight.get("placeholder_metadata_fields"))]
    if placeholder_fields:
        items.append(
            {
                "item_id": "R7A_METADATA_PLACEHOLDERS",
                "stage": "preflight",
                "target_file": "metadata.json",
                "action": "replace_placeholder_metadata_with_real_provenance",
                "fields_to_fill": placeholder_fields,
                "minimum_evidence": "真实 site/campaign/time/operator/instrument/custody provenance。",
                "why_required": "placeholder metadata cannot establish field origin or chain of custody.",
            }
        )
    file_audit = _dict(preflight.get("file_audit"))
    csv_files = _dict(file_audit.get("csv_files"))
    for table, audit in sorted(csv_files.items()):
        audit = _dict(audit)
        if not audit.get("exists", False):
            items.append(
                {
                    "item_id": f"R7A_MISSING_FILE_{table}",
                    "stage": "preflight",
                    "target_file": f"{table}.csv",
                    "action": "create_required_csv_file",
                    "required_headers": _list(audit.get("expected_headers")),
                    "why_required": "required package table is absent.",
                }
            )
            continue
        missing_headers = [str(field) for field in _list(audit.get("missing_required_headers"))]
        if missing_headers:
            items.append(
                {
                    "item_id": f"R7A_MISSING_HEADERS_{table}",
                    "stage": "preflight",
                    "target_table": str(table),
                    "action": "add_required_headers",
                    "fields_to_add": missing_headers,
                    "why_required": "Agent44 cannot type-check or normalize this table without required headers.",
                }
            )
    row_counts = _dict(preflight.get("row_counts"))
    for table, count in sorted(row_counts.items()):
        if int(count or 0) <= 0:
            items.append(
                {
                    "item_id": f"R7A_REAL_ROWS_{table}",
                    "stage": "preflight",
                    "target_table": str(table),
                    "action": "add_real_timestamped_rows",
                    "minimum_rows": 1,
                    "recommended_rows": "At least 3 matched batches for replay smoke tests; more for holdout calibration.",
                    "why_required": "header-only CSVs cannot enter timestamped replay or field evidence gates.",
                }
            )
    if preflight.get("status") == "field_package_preflight_agent44_blocked":
        agent44_required_field_blockers = _dict(preflight.get("agent44_required_field_blockers"))
        for table, fields in sorted(agent44_required_field_blockers.items()):
            items.append(
                {
                    "item_id": f"R7A_AGENT44_REQUIRED_FIELDS_{table}",
                    "stage": "preflight",
                    "target_table": str(table),
                    "action": "fill_agent44_required_fields",
                    "fields_to_fill": [str(field) for field in _list(fields)],
                    "why_required": "Agent44 cannot normalize or replay this table while required values are missing.",
                }
            )
        agent44_type_error_tables = _dict(preflight.get("agent44_type_error_tables"))
        for table, type_errors in sorted(agent44_type_error_tables.items()):
            items.append(
                {
                    "item_id": f"R7A_AGENT44_TYPE_ERRORS_{table}",
                    "stage": "preflight",
                    "target_table": str(table),
                    "action": "repair_agent44_type_coercion_errors",
                    "type_errors": _list(type_errors),
                    "why_required": (
                        "Agent44 must parse numeric and boolean fields before timestamped replay can trust delays, "
                        "labels or pressure/headloss signals."
                    ),
                }
            )
        linkage_blockers = _dict(preflight.get("agent44_linkage_blockers"))
        if linkage_blockers:
            items.append(
                {
                    "item_id": "R7A_AGENT44_BATCH_LINKAGE",
                    "stage": "preflight",
                    "target_tables": REPLAY_TABLES,
                    "action": "align_agent44_batch_linkage",
                    "linkage_blockers": linkage_blockers,
                    "why_required": (
                        "Agent44 cannot pass to replay unless sensor, lab, operation, fast-proxy and "
                        "pressure/headloss rows share batch anchors."
                    ),
                }
            )
    return items


def _claim_patch_items(claim_audit: list[dict[str, Any]]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for row in claim_audit:
        if bool(row.get("coverage_pass", False)):
            continue
        need_id = str(row.get("need_id", "unknown_need"))
        if row.get("metadata_missing"):
            items.append(
                {
                    "item_id": f"R7G_METADATA_{need_id}",
                    "stage": "claim_specific_package",
                    "need_id": need_id,
                    "action": "fill_claim_required_metadata",
                    "fields_to_fill": [str(field) for field in _list(row.get("metadata_missing"))],
                    "why_required": "claim-specific review needs provenance fields to bind rows to a real campaign.",
                }
            )
        for table, audit in sorted(_dict(row.get("table_audits")).items()):
            audit = _dict(audit)
            missing_headers = [str(field) for field in _list(audit.get("missing_headers"))]
            empty_fields = [str(field) for field in _list(audit.get("empty_required_fields"))]
            if missing_headers or empty_fields or not bool(audit.get("row_presence_pass", False)):
                items.append(
                    {
                        "item_id": f"R7G_TABLE_{need_id}_{table}",
                        "stage": "claim_specific_package",
                        "need_id": need_id,
                        "target_table": str(table),
                        "action": "patch_claim_required_table_fields",
                        "fields_to_add": missing_headers,
                        "fields_to_fill": empty_fields,
                        "minimum_rows": 1 if not bool(audit.get("row_presence_pass", False)) else 0,
                        "why_required": "claim cannot be upgraded without non-empty evidence rows for its required fields.",
                    }
                )
        logical = [str(field) for field in _list(row.get("missing_logical_guardrail_fields"))]
        if logical:
            items.append(
                {
                    "item_id": f"R7G_LOGICAL_GUARDRAIL_{need_id}",
                    "stage": "claim_specific_package",
                    "need_id": need_id,
                    "action": "map_logical_guardrail_fields_to_package_tables",
                    "fields_to_map": logical,
                    "why_required": "guardrail fields generated upstream must be visible in at least one real package table.",
                }
            )
    return items


def _soft_holdout_patch_items(soft_holdout_audit: dict[str, Any]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for table, audit in sorted(_dict(soft_holdout_audit.get("table_audits")).items()):
        audit = _dict(audit)
        missing_headers = [str(field) for field in _list(audit.get("missing_headers"))]
        empty_fields = [str(field) for field in _list(audit.get("empty_required_fields"))]
        row_count = int(audit.get("row_count", 0) or 0)
        if missing_headers or empty_fields or row_count <= 0:
            items.append(
                {
                    "item_id": f"R7H_SOFT_HOLDOUT_TABLE_{table}",
                    "stage": "soft_sensor_field_holdout",
                    "target_table": str(table),
                    "action": "patch_soft_holdout_required_fields",
                    "fields_to_add": missing_headers,
                    "fields_to_fill": empty_fields,
                    "minimum_rows": 1 if row_count <= 0 else 0,
                    "why_required": "soft-sensor field holdout needs matched low-cost sensor and lab rows.",
                }
            )
    missing_analytes = [str(item) for item in _list(soft_holdout_audit.get("missing_weak_target_analytes"))]
    if missing_analytes:
        items.append(
            {
                "item_id": "R7H_WEAK_TARGET_ANALYTES",
                "stage": "soft_sensor_field_holdout",
                "target_table": "offline_lab_results",
                "action": "add_weak_target_holdout_analytes",
                "required_analytes": missing_analytes,
                "why_required": "overall soft-sensor coverage cannot substitute catalyst_activity and matrix_interference holdout labels.",
            }
        )
    return items


def _field_proxy_holdout_patch_items(field_proxy_holdout_audit: dict[str, Any]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    missing_required_tables = [str(item) for item in _list(field_proxy_holdout_audit.get("missing_required_tables"))]
    if missing_required_tables:
        items.append(
            {
                "item_id": "R7J_CATALYST_PROXY_REQUIRED_TABLES",
                "stage": "catalyst_proxy_field_holdout",
                "target_tables": missing_required_tables,
                "action": "create_agent51_field_proxy_holdout_tables",
                "why_required": "Agent51 catalyst weak-axis repair needs real field holdout evidence beyond generic replay rows.",
            }
        )
    for table, fields in sorted(_dict(field_proxy_holdout_audit.get("missing_required_fields_by_table")).items()):
        items.append(
            {
                "item_id": f"R7J_CATALYST_PROXY_FIELDS_{table}",
                "stage": "catalyst_proxy_field_holdout",
                "target_table": str(table),
                "action": "add_agent51_field_proxy_holdout_fields",
                "fields_to_add": [str(field) for field in _list(fields)],
                "why_required": "The current package cannot bind Agent51 proxy signals to node, modality, value, timing or QA status.",
            }
        )
    for table, fields in sorted(_dict(field_proxy_holdout_audit.get("empty_required_fields_by_table")).items()):
        items.append(
            {
                "item_id": f"R7J_CATALYST_PROXY_VALUES_{table}",
                "stage": "catalyst_proxy_field_holdout",
                "target_table": str(table),
                "action": "fill_agent51_field_proxy_holdout_values",
                "fields_to_fill": [str(field) for field in _list(fields)],
                "minimum_rows": FIELD_PROXY_HOLDOUT_MINIMUM_MATCHED_BATCHES,
                "why_required": "Header-only or empty fields cannot validate catalyst proxy holdout.",
            }
        )
    sensor_audit = _dict(field_proxy_holdout_audit.get("sensor_signal_audit"))
    missing_signals = [str(item) for item in _list(sensor_audit.get("missing_patch_signals"))]
    pressure_source_conflicts = [
        _dict(item)
        for item in _list(
            sensor_audit.get(
                "unresolved_pressure_source_conflicts",
                sensor_audit.get("pressure_source_conflicts"),
            )
        )
    ]
    if pressure_source_conflicts:
        items.append(
            {
                "item_id": "R8M_PRESSURE_SOURCE_CONFLICT_FIELD_PATCH",
                "stage": "pressure_source_conflict_field_patch",
                "target_tables": [FIELD_PROXY_SENSOR_TABLE, PRESSURE_HEADLOSS_TABLE, "campaign_operation_log"],
                "action": "resolve_pressure_source_conflicts_before_agent51_scoring",
                "operator_review_required": True,
                "pressure_source_conflict_count": len(pressure_source_conflicts),
                "pressure_source_conflict_batch_ids": [
                    str(item.get("batch_id"))
                    for item in pressure_source_conflicts
                    if not FieldReplayImportAgent._is_missing_value(item.get("batch_id"))
                ],
                "pressure_source_conflicts": pressure_source_conflicts[:12],
                "pressure_source_conflict_abs_tolerance_kPa": PRESSURE_SOURCE_CONFLICT_ABS_TOLERANCE_KPA,
                "pressure_source_conflict_rel_tolerance": PRESSURE_SOURCE_CONFLICT_REL_TOLERANCE,
                "fields_to_review": {
                    FIELD_PROXY_SENSOR_TABLE: [
                        "batch_id",
                        "timestamp_min",
                        "node_id",
                        "modality",
                        "value",
                        "sensor_status",
                        "instrument_id",
                    ],
                    PRESSURE_HEADLOSS_TABLE: [
                        "batch_id",
                        "event_time_min",
                        "bed_id",
                        "pressure_drop_kPa",
                        "flow_Lmin",
                        "operator_review_required",
                    ],
                },
                "fields_to_add_or_fill": {
                    "campaign_operation_log": PRESSURE_SOURCE_RESOLUTION_FIELDS,
                    PRESSURE_HEADLOSS_TABLE: ["operator_review_required", *PRESSURE_SOURCE_RESOLUTION_FIELDS],
                },
                "minimum_evidence": (
                    "For each conflicting batch, provide operator review, calibration action id, authoritative "
                    "pressure source and note whether node pressure or pressure_headloss_event_log should be trusted."
                ),
                "why_required": (
                    "Conflicting pressure sources cannot support Agent51 catalyst proxy scoring, Agent49 guardrail "
                    "relaxation or Agent52 replay promotion until field calibration resolves the source boundary."
                ),
            }
        )
    if missing_signals:
        items.append(
            {
                "item_id": "R7J_CATALYST_PROXY_SENSOR_SIGNALS",
                "stage": "catalyst_proxy_field_holdout",
                "target_table": sensor_audit.get("source_table", FIELD_PROXY_SENSOR_TABLE),
                "action": "add_same_batch_node_modality_sensor_rows",
                "required_patch_signals": missing_signals,
                "required_format": sensor_audit.get("required_sensor_table_format", "node_modality_long_table"),
                "minimum_matched_batch_count": FIELD_PROXY_HOLDOUT_MINIMUM_MATCHED_BATCHES,
                "why_required": "Generic UV254/ORP columns do not prove the missing signal was observed at the catalyst bed node.",
            }
        )
    lab_audit = _dict(field_proxy_holdout_audit.get("lab_label_audit"))
    if not bool(lab_audit.get("catalyst_activity_label_pass", False)):
        items.append(
            {
                "item_id": "R7J_CATALYST_PROXY_LAB_LABELS",
                "stage": "catalyst_proxy_field_holdout",
                "target_table": "offline_lab_results",
                "action": "add_qa_passed_catalyst_activity_holdout_labels",
                "required_analyte": FIELD_PROXY_REQUIRED_ANALYTE,
                "required_fields": ["batch_id", "analyte", "value", "qa_flag", "lab_label_time_min"],
                "minimum_valid_label_count": FIELD_PROXY_HOLDOUT_MINIMUM_MATCHED_BATCHES,
                "current_valid_label_count": lab_audit.get("valid_catalyst_activity_label_count", 0),
                "why_required": "Agent51 proxy design cannot become a field holdout without QA-passed catalyst_activity labels.",
            }
        )
    operation_audit = _dict(field_proxy_holdout_audit.get("operation_event_audit"))
    if not bool(operation_audit.get("regeneration_event_pass", False)):
        items.append(
            {
                "item_id": "R7J_CATALYST_PROXY_REGENERATION_EVENTS",
                "stage": "catalyst_proxy_field_holdout",
                "target_table": "campaign_operation_log",
                "action": "add_parseable_regeneration_events",
                "required_fields": ["batch_id", "regeneration_event", "command_time_min", "effect_time_min"],
                "minimum_valid_event_count": FIELD_PROXY_HOLDOUT_MINIMUM_MATCHED_BATCHES,
                "current_valid_event_count": operation_audit.get("valid_regeneration_event_count", 0),
                "why_required": "Regeneration response separates reversible catalyst activity loss from fouling or matrix effects.",
            }
        )
    geometry_audit = _dict(field_proxy_holdout_audit.get("geometry_audit"))
    if not bool(geometry_audit.get("geometry_coverage_pass", False)):
        items.append(
            {
                "item_id": "R7J_CATALYST_PROXY_HYDRAULIC_GEOMETRY",
                "stage": "catalyst_proxy_field_holdout",
                "target_table": FIELD_PROXY_GEOMETRY_TABLE,
                "action": "add_bed_geometry_or_hrt_records",
                "required_fields": ["node_id", "bed_volume", "nominal_HRT_min", "flow_Lmin"],
                "why_required": "Catalyst activity proxy needs HRT or bed volume to turn removal deltas into grey-box rate residuals.",
            }
        )
    matched_count = int(field_proxy_holdout_audit.get("matched_proxy_holdout_batch_count", 0) or 0)
    if matched_count < FIELD_PROXY_HOLDOUT_MINIMUM_MATCHED_BATCHES:
        items.append(
            {
                "item_id": "R7J_CATALYST_PROXY_MATCHED_BATCHES",
                "stage": "catalyst_proxy_field_holdout",
                "target_tables": [
                    FIELD_PROXY_SENSOR_TABLE,
                    "offline_lab_results",
                    "campaign_operation_log",
                    FIELD_PROXY_GEOMETRY_TABLE,
                ],
                "action": "align_agent51_proxy_evidence_on_same_batch_ids",
                "minimum_matched_batch_count": FIELD_PROXY_HOLDOUT_MINIMUM_MATCHED_BATCHES,
                "current_matched_batch_count": matched_count,
                "why_required": "Agent51 cannot validate a proxy if sensor, lab and operation evidence do not overlap on the same batches.",
            }
        )
    return items


def _minimum_replay_patch_items(minimum_replay_contract: dict[str, Any]) -> list[dict[str, Any]]:
    status = str(minimum_replay_contract["status"])
    if status in {"minimum_replay_contract_ready_for_agent42_smoke_test", "minimum_replay_contract_blocked_missing_rows"}:
        return []
    items: list[dict[str, Any]] = []
    if status == "minimum_replay_contract_time_order_gaps":
        items.append(
            {
                "item_id": "R7I_TIME_ORDER",
                "stage": "minimum_timestamped_replay_contract",
                "target_tables": [
                    table
                    for table, violations in _dict(minimum_replay_contract.get("time_order_violations")).items()
                    if violations
                ],
                "action": "fix_timestamp_order_before_replay",
                "time_order_violations": minimum_replay_contract["time_order_violations"],
                "why_required": "Agent42 replay rejects impossible time order because it corrupts lab delay, actuator latency and proxy lead-time estimates.",
            }
        )
    if status == "minimum_replay_contract_batch_linkage_gaps":
        items.append(
            {
                "item_id": "R7I_MATCHED_BATCH_GROUPS",
                "stage": "minimum_timestamped_replay_contract",
                "target_tables": REPLAY_TABLES,
                "action": "add_matched_batch_rows_across_all_replay_tables",
                "minimum_common_batch_count": MINIMUM_SMOKE_TEST_MATCHED_BATCHES,
                "current_common_batch_count": minimum_replay_contract["common_batch_count"],
                "why_required": (
                    "Agent42 replay needs matched batch_id groups across sensor, lab, operation, fast-proxy "
                    "and pressure/headloss event tables."
                ),
            }
        )
    if int(minimum_replay_contract.get("valid_operation_action_count", 0) or 0) < MINIMUM_SMOKE_TEST_MATCHED_BATCHES:
        items.append(
            {
                "item_id": "R7I_OPERATION_ACTION_QUALITY",
                "stage": "minimum_timestamped_replay_contract",
                "target_table": "campaign_operation_log",
                "action": "repair_operation_action_quality",
                "required_fields": OPERATION_ACTION_QUALITY_FIELDS,
                "accepted_pump_valve_results": sorted(ACCEPTED_PUMP_VALVE_RESULTS),
                "minimum_valid_operation_action_count": MINIMUM_SMOKE_TEST_MATCHED_BATCHES,
                "current_valid_operation_action_count": minimum_replay_contract.get("valid_operation_action_count", 0),
                "invalid_operation_action_rows": _dict(minimum_replay_contract.get("operation_action_quality")).get(
                    "invalid_operation_action_rows",
                    [],
                ),
                "why_required": "Control replay needs executable operation rows, not just operation timestamps.",
            }
        )
    if int(minimum_replay_contract.get("valid_lab_result_count", 0) or 0) < MINIMUM_SMOKE_TEST_MATCHED_BATCHES:
        items.append(
            {
                "item_id": "R7I_LAB_RESULT_QUALITY",
                "stage": "minimum_timestamped_replay_contract",
                "target_table": "offline_lab_results",
                "action": "repair_offline_lab_result_quality",
                "required_fields": LAB_RESULT_QUALITY_FIELDS,
                "accepted_qa_flags": sorted(ACCEPTED_LAB_QA_FLAGS),
                "minimum_valid_lab_result_count": MINIMUM_SMOKE_TEST_MATCHED_BATCHES,
                "current_valid_lab_result_count": minimum_replay_contract.get("valid_lab_result_count", 0),
                "invalid_lab_result_rows": _dict(minimum_replay_contract.get("lab_result_quality")).get(
                    "invalid_lab_result_rows",
                    [],
                ),
                "why_required": "Soft-sensor holdout and claim review need QA-passed offline labels, not just lab rows.",
            }
        )
    if int(minimum_replay_contract["proxy_event_count"]) < MINIMUM_SMOKE_TEST_MATCHED_BATCHES:
        items.append(
            {
                "item_id": "R7I_PROXY_EVENT_COUNT",
                "stage": "minimum_timestamped_replay_contract",
                "target_table": "fast_proxy_event_log",
                "action": "add_field_labeled_proxy_events",
                "minimum_proxy_events_for_smoke_test": MINIMUM_SMOKE_TEST_MATCHED_BATCHES,
                "recommended_proxy_events_for_calibration": RECOMMENDED_CALIBRATION_PROXY_EVENTS,
                "current_proxy_event_count": minimum_replay_contract["proxy_event_count"],
                "why_required": "Fast-proxy precision/recall and lead-time checks need enough labeled proxy events.",
            }
        )
    if int(minimum_replay_contract.get("valid_proxy_label_count", 0) or 0) < MINIMUM_SMOKE_TEST_MATCHED_BATCHES:
        items.append(
            {
                "item_id": "R7I_PROXY_LABEL_QUALITY",
                "stage": "minimum_timestamped_replay_contract",
                "target_table": "fast_proxy_event_log",
                "action": "repair_fast_proxy_label_fields",
                "required_fields": PROXY_LABEL_QUALITY_FIELDS,
                "minimum_valid_proxy_label_count": MINIMUM_SMOKE_TEST_MATCHED_BATCHES,
                "current_valid_proxy_label_count": minimum_replay_contract.get("valid_proxy_label_count", 0),
                "invalid_proxy_label_rows": _dict(minimum_replay_contract.get("proxy_label_quality")).get(
                    "invalid_proxy_label_rows",
                    [],
                ),
                "why_required": "Fast-proxy calibration needs valid labels, not just proxy-event rows.",
            }
        )
    if int(minimum_replay_contract.get("pressure_headloss_event_count", 0) or 0) < MINIMUM_SMOKE_TEST_MATCHED_BATCHES:
        items.append(
            {
                "item_id": "R7I_PRESSURE_HEADLOSS_EVENT_COUNT",
                "stage": "minimum_timestamped_replay_contract",
                "target_table": PRESSURE_HEADLOSS_TABLE,
                "action": "add_pressure_headloss_events",
                "minimum_pressure_headloss_events_for_smoke_test": MINIMUM_SMOKE_TEST_MATCHED_BATCHES,
                "current_pressure_headloss_event_count": minimum_replay_contract.get(
                    "pressure_headloss_event_count",
                    0,
                ),
                "why_required": (
                    "Pressure/headloss replay needs enough same-campaign hydraulic proxy events to test catalyst-bed "
                    "fouling, blockage and guardrail boundaries."
                ),
            }
        )
    if (
        int(minimum_replay_contract.get("valid_pressure_headloss_event_count", 0) or 0)
        < MINIMUM_SMOKE_TEST_MATCHED_BATCHES
        or int(minimum_replay_contract.get("valid_pressure_headloss_batch_count", 0) or 0)
        < MINIMUM_SMOKE_TEST_MATCHED_BATCHES
    ):
        items.append(
            {
                "item_id": "R7I_PRESSURE_HEADLOSS_QUALITY",
                "stage": "minimum_timestamped_replay_contract",
                "target_table": PRESSURE_HEADLOSS_TABLE,
                "action": "repair_pressure_headloss_event_quality",
                "required_fields": PRESSURE_HEADLOSS_QUALITY_FIELDS,
                "minimum_valid_pressure_headloss_event_count": MINIMUM_SMOKE_TEST_MATCHED_BATCHES,
                "current_valid_pressure_headloss_event_count": minimum_replay_contract.get(
                    "valid_pressure_headloss_event_count",
                    0,
                ),
                "current_valid_pressure_headloss_batch_count": minimum_replay_contract.get(
                    "valid_pressure_headloss_batch_count",
                    0,
                ),
                "invalid_pressure_headloss_event_rows": _dict(
                    minimum_replay_contract.get("pressure_headloss_quality")
                ).get(
                    "invalid_pressure_headloss_event_rows",
                    [],
                ),
                "why_required": (
                    "The hydraulic proxy cannot enter grey-box replay unless pressure/headloss rows are tied to "
                    "a bed, a matched lab sample time, positive flow and parseable anomaly/regeneration labels."
                ),
            }
        )
    if int(minimum_replay_contract.get("valid_matched_batch_count", 0) or 0) < MINIMUM_SMOKE_TEST_MATCHED_BATCHES:
        items.append(
            {
                "item_id": "R7I_VALID_MATCHED_BATCH_GROUPS",
                "stage": "minimum_timestamped_replay_contract",
                "target_tables": REPLAY_TABLES,
                "action": "align_valid_lab_proxy_and_pressure_headloss_on_same_batch_ids",
                "minimum_valid_matched_batch_count": MINIMUM_SMOKE_TEST_MATCHED_BATCHES,
                "current_valid_matched_batch_count": minimum_replay_contract.get("valid_matched_batch_count", 0),
                "valid_matched_batch_ids_sample": minimum_replay_contract.get("valid_matched_batch_ids_sample", []),
                "why_required": (
                    "Replay needs valid lab labels, fast-proxy labels and pressure/headloss proxy events on the "
                    "same matched batch_id groups."
                ),
            }
        )
    return items


def _operator_checklist(status: str, items: list[dict[str, Any]]) -> list[str]:
    if not items:
        return ["Coverage patch plan is clear; proceed to replay, soft holdout calibration and human review gates."]
    checklist = [
        f"{item['item_id']}: {item['action']}"
        for item in items[:8]
    ]
    if len(items) > 8:
        checklist.append(f"... plus {len(items) - 8} additional patch items.")
    if status == "patch_plan_blocked_at_import_preflight":
        checklist.append("After patching, rerun Agent44 preflight before interpreting claim or holdout coverage.")
    elif status == "patch_plan_requires_claim_specific_fields":
        checklist.append("After patching, rerun R7 pipeline and Agent59 claim-specific package checks.")
    elif status == "patch_plan_requires_soft_holdout_weak_targets":
        checklist.append("After patching, rerun Agent36/39/47/46 soft-sensor holdout gates before R7 claim upgrade.")
    elif status == "patch_plan_requires_minimum_replay_contract":
        checklist.append("After patching, rerun Agent44 then Agent42/43/45 to verify matched batch replay.")
    elif status == "patch_plan_requires_catalyst_proxy_field_holdout":
        checklist.append(
            "After patching, rerun Agent51/R2/R7j and keep Agent49 catalyst uncertainty protection until field_proxy_holdout passes."
        )
    elif status == "patch_plan_requires_pressure_source_conflict_resolution":
        checklist.append(
            "After resolving pressure source conflicts, rerun R7 pipeline, Agent51 holdout and Agent49/52 replay before any guardrail relaxation."
        )
    return checklist


def _claim_blockers(
    metadata_missing: list[str],
    missing_header_count: int,
    empty_field_count: int,
    missing_row_tables: list[str],
    missing_logical_guardrail_fields: list[str],
) -> list[str]:
    blockers = []
    if metadata_missing:
        blockers.append("metadata_required_fields_missing")
    if missing_header_count:
        blockers.append("claim_required_headers_missing")
    if empty_field_count:
        blockers.append("claim_required_fields_empty")
    if missing_row_tables:
        blockers.append("claim_required_tables_have_no_rows")
    if missing_logical_guardrail_fields:
        blockers.append("logical_guardrail_fields_not_present_in_any_table")
    return blockers


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []

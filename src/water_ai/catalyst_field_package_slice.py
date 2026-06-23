from __future__ import annotations

import csv
from pathlib import Path
from typing import Any


SLICE_ID = "R8u113_catalyst_field_package_slice"
TARGET_HIDDEN_STATE = "catalyst_activity"
SOURCE_ENV_VAR = "CATALYST_FIELD_PACKAGE_SLICE_DIR"
MINIMUM_MATCHED_BATCH_COUNT = 3

NODE_MODALITY_SENSOR_TABLE = "node_modality_sensor_timeseries"
OFFLINE_LAB_TABLE = "offline_lab_results"
CAMPAIGN_OPERATION_TABLE = "campaign_operation_log"
GEOMETRY_TABLE = "site_topology_or_bed_geometry"

REQUIRED_TABLES = (
    NODE_MODALITY_SENSOR_TABLE,
    OFFLINE_LAB_TABLE,
    CAMPAIGN_OPERATION_TABLE,
    GEOMETRY_TABLE,
)

REQUIRED_SENSOR_SIGNALS = (
    ("N3_catalyst_bed", "pressure_drop_kPa", "pressure_headloss_proxy"),
    ("N3_catalyst_bed_outlet", "UV254_abs", "bed_outlet_uv254_proxy"),
    ("N3_catalyst_bed_outlet", "ORP_mV", "bed_outlet_orp_proxy"),
)

TABLE_COLUMNS = {
    NODE_MODALITY_SENSOR_TABLE: [
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
        "layout_id",
        "availability_mask",
        "time_since_last_observed_min",
        "data_origin",
        "sensor_value",
    ],
    OFFLINE_LAB_TABLE: [
        "batch_id",
        "sample_time_min",
        "result_time_min",
        "analyte",
        "value",
        "qa_flag",
        "proxy_holdout_label",
        "catalyst_activity_label",
        "pressure_headloss_proxy_label",
        "lab_label_time_min",
        "detection_limit",
        "method",
        "unit",
        "sample_source",
    ],
    CAMPAIGN_OPERATION_TABLE: [
        "campaign_id",
        "batch_id",
        "action_id",
        "command_time_min",
        "effect_time_min",
        "start_min",
        "end_min",
        "release_policy",
        "recycle_ratio",
        "tank_storage_margin",
        "actuator_latency_p90",
        "pump_valve_result",
        "hold_time_min",
        "regeneration_event",
        "bed_id",
        "pressure_headloss_review_required",
        "operator_override",
    ],
    GEOMETRY_TABLE: [
        "node_id",
        "bed_volume",
        "nominal_HRT_min",
        "flow_Lmin",
        "site_id",
        "zone",
        "upstream_node_id",
        "downstream_node_id",
        "path_stage_id",
        "hydraulic_path_role",
        "nominal_flow_Lmin",
        "recycle_ratio",
        "release_boundary_flag",
        "recirculation_loop_flag",
    ],
}

ACCEPTED_SENSOR_STATUS = {"ok", "pass", "passed", "valid", "calibrated", "normal", "qualified", "合格", "正常"}
ACCEPTED_LAB_QA_FLAGS = {"pass", "passed", "valid", "ok", "qc_pass", "qualified", "合格"}


def build_catalyst_field_package_slice_template(
    batch_ids: list[str] | None = None,
) -> dict[str, Any]:
    """Build the smallest four-table field package slice needed for catalyst_activity holdout."""

    ids = batch_ids or ["TODO_batch_id_1", "TODO_batch_id_2", "TODO_batch_id_3"]
    tables = {
        NODE_MODALITY_SENSOR_TABLE: {
            "columns": TABLE_COLUMNS[NODE_MODALITY_SENSOR_TABLE],
            "rows": _sensor_template_rows(ids),
        },
        OFFLINE_LAB_TABLE: {
            "columns": TABLE_COLUMNS[OFFLINE_LAB_TABLE],
            "rows": _lab_template_rows(ids),
        },
        CAMPAIGN_OPERATION_TABLE: {
            "columns": TABLE_COLUMNS[CAMPAIGN_OPERATION_TABLE],
            "rows": _operation_template_rows(ids),
        },
        GEOMETRY_TABLE: {
            "columns": TABLE_COLUMNS[GEOMETRY_TABLE],
            "rows": [_geometry_template_row()],
        },
    }
    return {
        "slice_id": SLICE_ID,
        "slice_type": "focused_catalyst_activity_field_package_slice_template",
        "target_hidden_state": TARGET_HIDDEN_STATE,
        "required_table_count": len(REQUIRED_TABLES),
        "required_tables": list(REQUIRED_TABLES),
        "minimum_matched_batch_count": MINIMUM_MATCHED_BATCH_COUNT,
        "required_sensor_signals": [
            {"node_id": node_id, "modality": modality, "observation_role": role}
            for node_id, modality, role in REQUIRED_SENSOR_SIGNALS
        ],
        "tables": tables,
        "table_row_counts": {name: len(table["rows"]) for name, table in tables.items()},
        "operator_instructions": [
            "Fill all TODO values with real field records before preflight.",
            "Use at least three shared batch_id values across sensor, offline lab and campaign operation rows.",
            "Keep sensor rows data_origin=field and accepted sensor_status.",
            "Keep offline_lab_results analyte=catalyst_activity and QA-passed lab labels.",
            "Keep campaign_operation_log regeneration_event parseable and action times numeric.",
            "Provide positive bed_volume, nominal_HRT_min and flow_Lmin for the catalyst bed geometry row.",
        ],
        "no_write_boundary": _no_write_boundary(),
    }


def build_catalyst_field_package_slice_preflight(
    *,
    source_dir: str | Path | None = None,
    external_slice_supplied: bool = False,
) -> dict[str, Any]:
    """Preflight a focused four-table catalyst field package slice without claiming full field validation."""

    source = Path(source_dir) if source_dir not in (None, "") else None
    if not external_slice_supplied or source is None:
        return _preflight_payload(
            source_path="" if source is None else str(source),
            external_slice_supplied=False,
            slice_status="catalyst_field_package_slice_waiting_for_CATALYST_FIELD_PACKAGE_SLICE_DIR",
            table_audits={},
            sensor_audit=_empty_sensor_audit(),
            lab_audit=_empty_lab_audit(),
            operation_audit=_empty_operation_audit(),
            geometry_audit=_empty_geometry_audit(),
            matched_batch_ids=[],
            blocking_reasons=["missing_external_slice_dir"],
        )
    if not source.exists() or not source.is_dir():
        return _preflight_payload(
            source_path=str(source),
            external_slice_supplied=True,
            slice_status="catalyst_field_package_slice_blocked_at_missing_source_dir",
            table_audits={},
            sensor_audit=_empty_sensor_audit(),
            lab_audit=_empty_lab_audit(),
            operation_audit=_empty_operation_audit(),
            geometry_audit=_empty_geometry_audit(),
            matched_batch_ids=[],
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

    sensor_audit = _sensor_audit(tables.get(NODE_MODALITY_SENSOR_TABLE, []))
    lab_audit = _lab_audit(tables.get(OFFLINE_LAB_TABLE, []))
    operation_audit = _operation_audit(tables.get(CAMPAIGN_OPERATION_TABLE, []))
    geometry_audit = _geometry_audit(tables.get(GEOMETRY_TABLE, []))
    matched_batch_ids = sorted(
        set(sensor_audit["all_signal_shared_batch_ids"])
        & set(lab_audit["valid_catalyst_activity_batch_ids"])
        & set(operation_audit["valid_regeneration_event_batch_ids"])
    )
    blocking_reasons = _blocking_reasons(
        missing_tables=missing_tables,
        header_gaps=header_gaps,
        template_marker_count=template_marker_count,
        sensor_audit=sensor_audit,
        lab_audit=lab_audit,
        operation_audit=operation_audit,
        geometry_audit=geometry_audit,
        matched_batch_ids=matched_batch_ids,
    )
    return _preflight_payload(
        source_path=str(source),
        external_slice_supplied=True,
        slice_status=_slice_status(blocking_reasons),
        table_audits=table_audits,
        sensor_audit=sensor_audit,
        lab_audit=lab_audit,
        operation_audit=operation_audit,
        geometry_audit=geometry_audit,
        matched_batch_ids=matched_batch_ids,
        blocking_reasons=blocking_reasons,
    )


def _preflight_payload(
    *,
    source_path: str,
    external_slice_supplied: bool,
    slice_status: str,
    table_audits: dict[str, dict[str, Any]],
    sensor_audit: dict[str, Any],
    lab_audit: dict[str, Any],
    operation_audit: dict[str, Any],
    geometry_audit: dict[str, Any],
    matched_batch_ids: list[str],
    blocking_reasons: list[str],
) -> dict[str, Any]:
    slice_preflight_pass = not blocking_reasons and external_slice_supplied
    return {
        "slice_id": SLICE_ID,
        "slice_type": "focused_catalyst_activity_field_package_slice_preflight",
        "target_hidden_state": TARGET_HIDDEN_STATE,
        "source_env_var": SOURCE_ENV_VAR,
        "source_path": source_path,
        "external_slice_supplied": external_slice_supplied,
        "slice_status": slice_status,
        "slice_preflight_pass": slice_preflight_pass,
        "required_table_count": len(REQUIRED_TABLES),
        "required_tables": list(REQUIRED_TABLES),
        "generated_table_count": len(REQUIRED_TABLES),
        "minimum_matched_batch_count": MINIMUM_MATCHED_BATCH_COUNT,
        "matched_batch_count": len(matched_batch_ids),
        "matched_batch_ids": matched_batch_ids,
        "matched_batch_requirement_pass": len(matched_batch_ids) >= MINIMUM_MATCHED_BATCH_COUNT,
        "table_audits": table_audits,
        "sensor_audit": sensor_audit,
        "lab_audit": lab_audit,
        "operation_audit": operation_audit,
        "geometry_audit": geometry_audit,
        "blocking_reason_count": len(blocking_reasons),
        "blocking_reasons": blocking_reasons,
        "can_route_to_r7_field_package_patch_candidate": slice_preflight_pass,
        "can_route_to_agent51_field_proxy_holdout": False,
        "can_relax_agent49_catalyst_uncertainty_block": False,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
        "next_operator_action": _next_operator_action(slice_status),
        "field_boundary": (
            "This focused slice can only prepare the catalyst_activity rows for a full R7 field package import. "
            "It cannot replace the complete field package, Agent51 field proxy holdout, or field-supported claims."
        ),
        "no_write_boundary": _no_write_boundary(),
    }


def _read_tables(source: Path) -> tuple[dict[str, list[dict[str, str]]], dict[str, dict[str, Any]]]:
    tables: dict[str, list[dict[str, str]]] = {}
    audits: dict[str, dict[str, Any]] = {}
    for table_name in REQUIRED_TABLES:
        path = source / f"{table_name}.csv"
        rows: list[dict[str, str]] = []
        fieldnames: list[str] = []
        if path.exists():
            with path.open(newline="", encoding="utf-8-sig") as handle:
                reader = csv.DictReader(handle)
                fieldnames = list(reader.fieldnames or [])
                rows = [{key: (value or "") for key, value in row.items()} for row in reader]
        tables[table_name] = rows
        missing_columns = [column for column in TABLE_COLUMNS[table_name] if column not in fieldnames]
        audits[table_name] = {
            "path": str(path),
            "file_exists": path.exists(),
            "row_count": len(rows),
            "expected_columns": TABLE_COLUMNS[table_name],
            "observed_columns": fieldnames,
            "missing_columns": missing_columns,
            "schema_pass": path.exists() and not missing_columns,
            "template_marker_count": _template_marker_count(rows),
        }
    return tables, audits


def _sensor_audit(rows: list[dict[str, str]]) -> dict[str, Any]:
    signal_results: dict[str, dict[str, Any]] = {}
    signal_batch_sets: list[set[str]] = []
    for node_id, modality, role in REQUIRED_SENSOR_SIGNALS:
        signal = f"{node_id}:{modality}"
        valid_batch_ids: set[str] = set()
        invalid_rows: list[dict[str, Any]] = []
        for index, row in enumerate(rows):
            if row.get("node_id", "").strip() != node_id or row.get("modality", "").strip() != modality:
                continue
            errors = _sensor_row_errors(row)
            if errors:
                invalid_rows.append({"row_index": index, "batch_id": row.get("batch_id", ""), "errors": errors})
            else:
                valid_batch_ids.add(row["batch_id"].strip())
        batch_ids = sorted(valid_batch_ids)
        signal_batch_sets.append(valid_batch_ids)
        signal_results[signal] = {
            "node_id": node_id,
            "modality": modality,
            "observation_role": role,
            "valid_batch_count": len(batch_ids),
            "valid_batch_ids": batch_ids,
            "invalid_row_count": len(invalid_rows),
            "invalid_rows": invalid_rows[:8],
            "coverage_pass": len(batch_ids) >= MINIMUM_MATCHED_BATCH_COUNT,
        }
    shared_batch_ids = sorted(set.intersection(*signal_batch_sets)) if signal_batch_sets else []
    return {
        "required_sensor_signals": list(signal_results),
        "signal_results": signal_results,
        "all_signal_shared_batch_count": len(shared_batch_ids),
        "all_signal_shared_batch_ids": shared_batch_ids,
        "sensor_coverage_pass": (
            all(result["coverage_pass"] for result in signal_results.values())
            and len(shared_batch_ids) >= MINIMUM_MATCHED_BATCH_COUNT
        ),
    }


def _lab_audit(rows: list[dict[str, str]]) -> dict[str, Any]:
    valid_batch_ids: set[str] = set()
    invalid_rows: list[dict[str, Any]] = []
    for index, row in enumerate(rows):
        if row.get("analyte", "").strip() != TARGET_HIDDEN_STATE:
            continue
        errors = _lab_row_errors(row)
        if errors:
            invalid_rows.append({"row_index": index, "batch_id": row.get("batch_id", ""), "errors": errors})
        else:
            valid_batch_ids.add(row["batch_id"].strip())
    batch_ids = sorted(valid_batch_ids)
    return {
        "required_analyte": TARGET_HIDDEN_STATE,
        "valid_catalyst_activity_label_count": len(batch_ids),
        "valid_catalyst_activity_batch_ids": batch_ids,
        "invalid_catalyst_activity_label_rows": invalid_rows[:8],
        "catalyst_activity_label_pass": len(batch_ids) >= MINIMUM_MATCHED_BATCH_COUNT,
    }


def _operation_audit(rows: list[dict[str, str]]) -> dict[str, Any]:
    valid_batch_ids: set[str] = set()
    invalid_rows: list[dict[str, Any]] = []
    for index, row in enumerate(rows):
        errors = _operation_row_errors(row)
        if errors:
            invalid_rows.append({"row_index": index, "batch_id": row.get("batch_id", ""), "errors": errors})
        else:
            valid_batch_ids.add(row["batch_id"].strip())
    batch_ids = sorted(valid_batch_ids)
    return {
        "valid_regeneration_event_count": len(batch_ids),
        "valid_regeneration_event_batch_ids": batch_ids,
        "invalid_regeneration_event_rows": invalid_rows[:8],
        "regeneration_event_pass": len(batch_ids) >= MINIMUM_MATCHED_BATCH_COUNT,
    }


def _geometry_audit(rows: list[dict[str, str]]) -> dict[str, Any]:
    valid_node_ids: set[str] = set()
    invalid_rows: list[dict[str, Any]] = []
    for index, row in enumerate(rows):
        errors = _geometry_row_errors(row)
        if errors:
            invalid_rows.append({"row_index": index, "node_id": row.get("node_id", ""), "errors": errors})
        else:
            valid_node_ids.add(row["node_id"].strip())
    return {
        "target_table": GEOMETRY_TABLE,
        "valid_geometry_row_count": len(valid_node_ids),
        "valid_geometry_node_ids": sorted(valid_node_ids),
        "invalid_geometry_rows": invalid_rows[:8],
        "geometry_coverage_pass": bool(valid_node_ids),
    }


def _blocking_reasons(
    *,
    missing_tables: list[str],
    header_gaps: list[dict[str, Any]],
    template_marker_count: int,
    sensor_audit: dict[str, Any],
    lab_audit: dict[str, Any],
    operation_audit: dict[str, Any],
    geometry_audit: dict[str, Any],
    matched_batch_ids: list[str],
) -> list[str]:
    reasons: list[str] = []
    if missing_tables:
        reasons.append("missing_required_tables")
    if header_gaps:
        reasons.append("table_schema_missing_required_columns")
    if template_marker_count:
        reasons.append("template_markers_still_present")
    if not sensor_audit["sensor_coverage_pass"]:
        reasons.append("sensor_signal_coverage_or_shared_batch_alignment_failed")
    if not lab_audit["catalyst_activity_label_pass"]:
        reasons.append("catalyst_activity_lab_label_coverage_failed")
    if not operation_audit["regeneration_event_pass"]:
        reasons.append("regeneration_event_operation_coverage_failed")
    if not geometry_audit["geometry_coverage_pass"]:
        reasons.append("bed_geometry_coverage_failed")
    if len(matched_batch_ids) < MINIMUM_MATCHED_BATCH_COUNT:
        reasons.append("shared_sensor_lab_operation_batch_alignment_failed")
    return reasons


def _slice_status(blocking_reasons: list[str]) -> str:
    if not blocking_reasons:
        return "catalyst_field_package_slice_ready_for_r7_package_patch_candidate"
    if "missing_required_tables" in blocking_reasons:
        return "catalyst_field_package_slice_blocked_at_missing_tables"
    if "table_schema_missing_required_columns" in blocking_reasons:
        return "catalyst_field_package_slice_blocked_at_table_schema"
    if "template_markers_still_present" in blocking_reasons:
        return "catalyst_field_package_slice_blocked_at_template_markers"
    if "shared_sensor_lab_operation_batch_alignment_failed" in blocking_reasons:
        return "catalyst_field_package_slice_blocked_at_batch_alignment"
    return "catalyst_field_package_slice_blocked_at_field_preflight"


def _next_operator_action(status: str) -> str:
    return {
        "catalyst_field_package_slice_waiting_for_CATALYST_FIELD_PACKAGE_SLICE_DIR": (
            "fill_focused_field_package_slice_template_and_set_CATALYST_FIELD_PACKAGE_SLICE_DIR"
        ),
        "catalyst_field_package_slice_blocked_at_missing_source_dir": "provide_existing_slice_directory",
        "catalyst_field_package_slice_blocked_at_missing_tables": "add_all_four_required_csv_tables",
        "catalyst_field_package_slice_blocked_at_table_schema": "repair_csv_headers_to_match_r7_template",
        "catalyst_field_package_slice_blocked_at_template_markers": "replace_all_TODO_values_with_real_field_records",
        "catalyst_field_package_slice_blocked_at_batch_alignment": (
            "align_at_least_three_real_batch_ids_across_sensor_lab_and_operation_tables"
        ),
        "catalyst_field_package_slice_blocked_at_field_preflight": "repair_invalid_field_values",
        "catalyst_field_package_slice_ready_for_r7_package_patch_candidate": (
            "merge_slice_into_full_real_field_package_then_run_r7_import_preflight"
        ),
    }.get(status, "inspect_catalyst_field_package_slice_preflight")


def _sensor_row_errors(row: dict[str, str]) -> list[str]:
    errors: list[str] = []
    if _missing(row.get("batch_id")):
        errors.append("missing_batch_id")
    if _number_error(row.get("timestamp_min")):
        errors.append("timestamp_min_not_numeric")
    if _number_error(row.get("value")):
        errors.append("value_not_numeric")
    if row.get("sensor_status", "").strip().lower() not in ACCEPTED_SENSOR_STATUS:
        errors.append("sensor_status_not_accepted")
    if row.get("data_origin", "").strip().lower() != "field":
        errors.append("data_origin_not_field")
    return errors


def _lab_row_errors(row: dict[str, str]) -> list[str]:
    errors: list[str] = []
    if _missing(row.get("batch_id")):
        errors.append("missing_batch_id")
    value, error = _parse_number(row.get("value"))
    if error:
        errors.append("value_not_numeric")
    elif value is not None and value < 0:
        errors.append("negative_lab_value")
    if _number_error(row.get("lab_label_time_min")):
        errors.append("lab_label_time_min_not_numeric")
    if row.get("qa_flag", "").strip().lower() not in ACCEPTED_LAB_QA_FLAGS:
        errors.append("qa_flag_not_accepted")
    return errors


def _operation_row_errors(row: dict[str, str]) -> list[str]:
    errors: list[str] = []
    if _missing(row.get("batch_id")):
        errors.append("missing_batch_id")
    if _bool_error(row.get("regeneration_event")):
        errors.append("regeneration_event_not_boolean")
    for field in ("command_time_min", "effect_time_min"):
        if _number_error(row.get(field)):
            errors.append(f"{field}_not_numeric")
    return errors


def _geometry_row_errors(row: dict[str, str]) -> list[str]:
    errors: list[str] = []
    if _missing(row.get("node_id")):
        errors.append("missing_node_id")
    for field in ("bed_volume", "nominal_HRT_min", "flow_Lmin"):
        value, error = _parse_number(row.get(field))
        if error:
            errors.append(f"{field}_not_numeric")
        elif value is not None and value <= 0:
            errors.append(f"{field}_not_positive")
    return errors


def _sensor_template_rows(batch_ids: list[str]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for batch_index, batch_id in enumerate(batch_ids, start=1):
        for node_id, modality, role in REQUIRED_SENSOR_SIGNALS:
            rows.append(
                {
                    "batch_id": batch_id,
                    "timestamp_min": f"TODO_timestamp_min_{batch_index}",
                    "node_id": node_id,
                    "zone": "catalyst_bed_zone",
                    "modality": modality,
                    "value": f"TODO_{modality}_value_{batch_index}",
                    "sensor_status": "TODO_ok",
                    "instrument_id": f"TODO_instrument_{role}",
                    "acquisition_time_min": f"TODO_acquisition_time_min_{batch_index}",
                    "ingest_time_min": f"TODO_ingest_time_min_{batch_index}",
                    "layout_id": "R8u113_focused_catalyst_layout",
                    "availability_mask": "TODO_1",
                    "time_since_last_observed_min": "TODO_time_since_last_observed_min",
                    "data_origin": "TODO_field",
                    "sensor_value": f"TODO_{modality}_value_{batch_index}",
                }
            )
    return rows


def _lab_template_rows(batch_ids: list[str]) -> list[dict[str, str]]:
    return [
        {
            "batch_id": batch_id,
            "sample_time_min": f"TODO_sample_time_min_{index}",
            "result_time_min": f"TODO_result_time_min_{index}",
            "analyte": TARGET_HIDDEN_STATE,
            "value": f"TODO_catalyst_activity_value_{index}",
            "qa_flag": "TODO_pass",
            "proxy_holdout_label": "TODO_proxy_holdout_label",
            "catalyst_activity_label": "TODO_catalyst_activity_label",
            "pressure_headloss_proxy_label": "TODO_pressure_headloss_proxy_label",
            "lab_label_time_min": f"TODO_lab_label_time_min_{index}",
            "detection_limit": "TODO_detection_limit",
            "method": "TODO_lab_method",
            "unit": "TODO_activity_unit",
            "sample_source": "N3_catalyst_bed_or_outlet",
        }
        for index, batch_id in enumerate(batch_ids, start=1)
    ]


def _operation_template_rows(batch_ids: list[str]) -> list[dict[str, str]]:
    return [
        {
            "campaign_id": "TODO_campaign_id",
            "batch_id": batch_id,
            "action_id": f"TODO_action_id_{index}",
            "command_time_min": f"TODO_command_time_min_{index}",
            "effect_time_min": f"TODO_effect_time_min_{index}",
            "start_min": f"TODO_start_min_{index}",
            "end_min": f"TODO_end_min_{index}",
            "release_policy": "TODO_no_release_policy_change",
            "recycle_ratio": "TODO_recycle_ratio",
            "tank_storage_margin": "TODO_tank_storage_margin",
            "actuator_latency_p90": "TODO_actuator_latency_p90",
            "pump_valve_result": "TODO_pump_valve_result",
            "hold_time_min": "TODO_hold_time_min",
            "regeneration_event": "TODO_true_or_false",
            "bed_id": "N3_catalyst_bed",
            "pressure_headloss_review_required": "TODO_true_or_false",
            "operator_override": "TODO_operator_override",
        }
        for index, batch_id in enumerate(batch_ids, start=1)
    ]


def _geometry_template_row() -> dict[str, str]:
    return {
        "node_id": "N3_catalyst_bed",
        "bed_volume": "TODO_bed_volume",
        "nominal_HRT_min": "TODO_nominal_HRT_min",
        "flow_Lmin": "TODO_flow_Lmin",
        "site_id": "TODO_site_id",
        "zone": "catalyst_bed_zone",
        "upstream_node_id": "N2_pre_treatment_outlet",
        "downstream_node_id": "N3_catalyst_bed_outlet",
        "path_stage_id": "catalyst_stage",
        "hydraulic_path_role": "reaction_contact_zone",
        "nominal_flow_Lmin": "TODO_nominal_flow_Lmin",
        "recycle_ratio": "TODO_recycle_ratio",
        "release_boundary_flag": "false",
        "recirculation_loop_flag": "true",
    }


def _empty_sensor_audit() -> dict[str, Any]:
    return {
        "required_sensor_signals": [f"{node_id}:{modality}" for node_id, modality, _ in REQUIRED_SENSOR_SIGNALS],
        "signal_results": {},
        "all_signal_shared_batch_count": 0,
        "all_signal_shared_batch_ids": [],
        "sensor_coverage_pass": False,
    }


def _empty_lab_audit() -> dict[str, Any]:
    return {
        "required_analyte": TARGET_HIDDEN_STATE,
        "valid_catalyst_activity_label_count": 0,
        "valid_catalyst_activity_batch_ids": [],
        "invalid_catalyst_activity_label_rows": [],
        "catalyst_activity_label_pass": False,
    }


def _empty_operation_audit() -> dict[str, Any]:
    return {
        "valid_regeneration_event_count": 0,
        "valid_regeneration_event_batch_ids": [],
        "invalid_regeneration_event_rows": [],
        "regeneration_event_pass": False,
    }


def _empty_geometry_audit() -> dict[str, Any]:
    return {
        "target_table": GEOMETRY_TABLE,
        "valid_geometry_row_count": 0,
        "valid_geometry_node_ids": [],
        "invalid_geometry_rows": [],
        "geometry_coverage_pass": False,
    }


def _template_marker_count(rows: list[dict[str, str]]) -> int:
    return sum(1 for row in rows for value in row.values() if _has_template_marker(value))


def _has_template_marker(value: Any) -> bool:
    token = str(value or "").strip().upper()
    return token.startswith("TODO") or "TODO_" in token or token in {"TBD", "PLACEHOLDER"}


def _missing(value: Any) -> bool:
    return value is None or str(value).strip() == "" or _has_template_marker(value)


def _number_error(value: Any) -> bool:
    return _parse_number(value)[1] is not None


def _parse_number(value: Any) -> tuple[float | None, str | None]:
    if _missing(value):
        return None, "missing"
    try:
        return float(str(value).strip()), None
    except ValueError:
        return None, "not_numeric"


def _bool_error(value: Any) -> bool:
    if _missing(value):
        return True
    return str(value).strip().lower() not in {"true", "false", "1", "0", "yes", "no", "y", "n", "是", "否"}


def _no_write_boundary() -> str:
    return (
        "This focused field package slice cannot authorize actuator writes, release-gate writes, "
        "Agent51 field proxy holdout pass, Agent49 guardrail relaxation, or field-supported claims."
    )

from __future__ import annotations

import csv
import math
from pathlib import Path
from typing import Any


PACKAGE_ID = "R8u151_sparse_topology_installability_package_preflight"
SOURCE_ENV_VAR = "SPARSE_TOPOLOGY_INSTALLABILITY_PACKAGE_DIR"
MINIMUM_MATCHED_NODE_COUNT = 3

TOPOLOGY_TABLE = "site_topology_graph"
COST_TABLE = "candidate_node_modality_costs"
CONSTRAINT_TABLE = "installability_maintenance_constraints"
HYDRAULIC_DELAY_TABLE = "node_hydraulic_delay"
LABEL_TABLE = "labeled_state_matrix"

REQUIRED_TABLES = (
    TOPOLOGY_TABLE,
    COST_TABLE,
    CONSTRAINT_TABLE,
    HYDRAULIC_DELAY_TABLE,
    LABEL_TABLE,
)

TABLE_COLUMNS = {
    TOPOLOGY_TABLE: [
        "node_id",
        "node_type",
        "upstream_node_id",
        "downstream_node_id",
        "unit_id",
        "path_stage",
        "edge_length_m",
        "nominal_flow_Lmin",
        "qa_flag",
        "data_origin",
    ],
    COST_TABLE: [
        "node_id",
        "modality",
        "sensor_type",
        "capex_usd",
        "opex_usd_month",
        "maintenance_interval_day",
        "installable_flag",
        "power_available",
        "communication_available",
        "qa_flag",
        "data_origin",
    ],
    CONSTRAINT_TABLE: [
        "node_id",
        "constraint_id",
        "access_level",
        "safety_class",
        "maintenance_window_min",
        "downtime_cost_index",
        "operator_review_required",
        "blocked_reason",
        "qa_flag",
        "data_origin",
    ],
    HYDRAULIC_DELAY_TABLE: [
        "node_id",
        "upstream_reference",
        "delay_min",
        "mixing_volume_L",
        "short_circuit_risk",
        "hydraulic_confidence",
        "qa_flag",
        "data_origin",
    ],
    LABEL_TABLE: [
        "node_id",
        "batch_id",
        "timestamp_min",
        "hidden_state",
        "label_value",
        "label_source",
        "layout_holdout_split",
        "qa_flag",
        "data_origin",
    ],
}

ACCEPTED_QA_FLAGS = {"pass", "passed", "valid", "ok", "qc_pass", "qualified", "合格"}
ACCEPTED_SPLITS = {"train", "calibration", "validation", "test", "holdout", "field_holdout", "layout_holdout"}


def build_sparse_topology_installability_package_template(
    node_ids: list[str] | None = None,
) -> dict[str, Any]:
    ids = node_ids or ["TODO_node_id_1", "TODO_node_id_2", "TODO_node_id_3"]
    tables = {
        TOPOLOGY_TABLE: {
            "columns": TABLE_COLUMNS[TOPOLOGY_TABLE],
            "rows": [_topology_template_row(node_id, index) for index, node_id in enumerate(ids)],
        },
        COST_TABLE: {
            "columns": TABLE_COLUMNS[COST_TABLE],
            "rows": [_cost_template_row(node_id) for node_id in ids],
        },
        CONSTRAINT_TABLE: {
            "columns": TABLE_COLUMNS[CONSTRAINT_TABLE],
            "rows": [_constraint_template_row(node_id) for node_id in ids],
        },
        HYDRAULIC_DELAY_TABLE: {
            "columns": TABLE_COLUMNS[HYDRAULIC_DELAY_TABLE],
            "rows": [_hydraulic_delay_template_row(node_id) for node_id in ids],
        },
        LABEL_TABLE: {
            "columns": TABLE_COLUMNS[LABEL_TABLE],
            "rows": [_label_template_row(node_id, index) for index, node_id in enumerate(ids, start=1)],
        },
    }
    return {
        "package_id": PACKAGE_ID,
        "package_type": "sparse_topology_installability_package_template",
        "source_env_var": SOURCE_ENV_VAR,
        "required_table_count": len(REQUIRED_TABLES),
        "required_tables": list(REQUIRED_TABLES),
        "minimum_matched_node_count": MINIMUM_MATCHED_NODE_COUNT,
        "tables": tables,
        "table_row_counts": {name: len(table["rows"]) for name, table in tables.items()},
        "operator_instructions": [
            "Fill TODO values with real site topology, installability, hydraulic delay and labeled-state rows.",
            "Use at least three shared node_id values across all five tables.",
            "Use data_origin=field for every row; design sketches or synthetic topology should not pass this preflight.",
            "Use SOURCE/SINK style markers rather than blank upstream/downstream nodes for boundary nodes.",
            "Keep actuator and release decisions closed; this package only routes data into Agent48 layout-holdout work.",
        ],
        "no_write_boundary": _no_write_boundary(),
    }


def write_sparse_topology_installability_package_template(target_dir: str | Path) -> dict[str, Any]:
    target = Path(target_dir)
    target.mkdir(parents=True, exist_ok=True)
    template = build_sparse_topology_installability_package_template()
    for table_name, table in template["tables"].items():
        _write_csv(target / f"{table_name}.csv", table["columns"], table["rows"])
    return template


def build_sparse_topology_installability_package_preflight(
    *,
    source_dir: str | Path | None = None,
    external_package_supplied: bool = False,
) -> dict[str, Any]:
    source = Path(source_dir) if source_dir not in (None, "") else None
    if not external_package_supplied or source is None:
        return _preflight_payload(
            source_path="" if source is None else str(source),
            external_package_supplied=False,
            package_status="sparse_topology_installability_package_waiting_for_SPARSE_TOPOLOGY_INSTALLABILITY_PACKAGE_DIR",
            table_audits={},
            topology_audit=_empty_signal_audit("site_topology"),
            cost_audit=_empty_signal_audit("node_modality_cost"),
            constraint_audit=_empty_signal_audit("installability_constraint"),
            hydraulic_delay_audit=_empty_signal_audit("hydraulic_delay"),
            label_audit=_empty_signal_audit("labeled_state_matrix"),
            matched_node_ids=[],
            blocking_reasons=["missing_external_package_dir"],
        )
    if not source.exists() or not source.is_dir():
        return _preflight_payload(
            source_path=str(source),
            external_package_supplied=True,
            package_status="sparse_topology_installability_package_blocked_at_missing_source_dir",
            table_audits={},
            topology_audit=_empty_signal_audit("site_topology"),
            cost_audit=_empty_signal_audit("node_modality_cost"),
            constraint_audit=_empty_signal_audit("installability_constraint"),
            hydraulic_delay_audit=_empty_signal_audit("hydraulic_delay"),
            label_audit=_empty_signal_audit("labeled_state_matrix"),
            matched_node_ids=[],
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

    topology_audit = _topology_audit(tables.get(TOPOLOGY_TABLE, []))
    cost_audit = _cost_audit(tables.get(COST_TABLE, []))
    constraint_audit = _constraint_audit(tables.get(CONSTRAINT_TABLE, []))
    hydraulic_delay_audit = _hydraulic_delay_audit(tables.get(HYDRAULIC_DELAY_TABLE, []))
    label_audit = _label_audit(tables.get(LABEL_TABLE, []))
    matched_node_ids = sorted(
        set(topology_audit["valid_node_ids"])
        & set(cost_audit["installable_valid_node_ids"])
        & set(constraint_audit["valid_node_ids"])
        & set(hydraulic_delay_audit["valid_node_ids"])
        & set(label_audit["valid_node_ids"])
    )
    blocking_reasons = _blocking_reasons(
        missing_tables=missing_tables,
        header_gaps=header_gaps,
        template_marker_count=template_marker_count,
        non_field_row_count=non_field_row_count,
        topology_audit=topology_audit,
        cost_audit=cost_audit,
        constraint_audit=constraint_audit,
        hydraulic_delay_audit=hydraulic_delay_audit,
        label_audit=label_audit,
        matched_node_ids=matched_node_ids,
    )
    return _preflight_payload(
        source_path=str(source),
        external_package_supplied=True,
        package_status=_package_status(blocking_reasons),
        table_audits=table_audits,
        topology_audit=topology_audit,
        cost_audit=cost_audit,
        constraint_audit=constraint_audit,
        hydraulic_delay_audit=hydraulic_delay_audit,
        label_audit=label_audit,
        matched_node_ids=matched_node_ids,
        blocking_reasons=blocking_reasons,
    )


def _preflight_payload(
    *,
    source_path: str,
    external_package_supplied: bool,
    package_status: str,
    table_audits: dict[str, dict[str, Any]],
    topology_audit: dict[str, Any],
    cost_audit: dict[str, Any],
    constraint_audit: dict[str, Any],
    hydraulic_delay_audit: dict[str, Any],
    label_audit: dict[str, Any],
    matched_node_ids: list[str],
    blocking_reasons: list[str],
) -> dict[str, Any]:
    preflight_pass = external_package_supplied and not blocking_reasons
    coverage = round(min(1.0, len(matched_node_ids) / MINIMUM_MATCHED_NODE_COUNT), 3)
    return {
        "package_id": PACKAGE_ID,
        "package_type": "sparse_topology_installability_package_preflight",
        "source_env_var": SOURCE_ENV_VAR,
        "source_path": source_path,
        "external_package_supplied": external_package_supplied,
        "package_status": package_status,
        "package_preflight_pass": preflight_pass,
        "required_table_count": len(REQUIRED_TABLES),
        "required_tables": list(REQUIRED_TABLES),
        "minimum_matched_node_count": MINIMUM_MATCHED_NODE_COUNT,
        "matched_node_count": len(matched_node_ids),
        "matched_node_ids": matched_node_ids,
        "sparse_topology_coverage_candidate": coverage,
        "installable_candidate_node_count": int(cost_audit.get("installable_candidate_node_count", 0) or 0),
        "path_stage_count": int(topology_audit.get("path_stage_count", 0) or 0),
        "hidden_state_count": int(label_audit.get("hidden_state_count", 0) or 0),
        "table_audits": table_audits,
        "topology_audit": topology_audit,
        "cost_audit": cost_audit,
        "constraint_audit": constraint_audit,
        "hydraulic_delay_audit": hydraulic_delay_audit,
        "label_audit": label_audit,
        "blocking_reasons": blocking_reasons,
        "can_route_to_agent48_sparse_layout_holdout": preflight_pass,
        "can_generate_field_evidence": False,
        "can_resume_model_chain": False,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
        "can_authorize_field_deployment": False,
        "next_operator_action": _next_operator_action(package_status),
        "field_boundary": (
            "This preflight only checks whether an external topology/installability package is "
            "ready for Agent48 sparse layout-holdout work. Passing this gate does not prove a "
            "deployable sensor layout, field soft-sensor performance, actuator readiness or "
            "release-gate readiness."
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


def _topology_audit(rows: list[dict[str, str]]) -> dict[str, Any]:
    valid_ids = []
    path_stages = set()
    node_types = set()
    for row in rows:
        if not _row_common_valid(row):
            continue
        node_id = str(row.get("node_id", "")).strip()
        required_text = [
            "node_type",
            "upstream_node_id",
            "downstream_node_id",
            "unit_id",
            "path_stage",
        ]
        if any(not str(row.get(column, "")).strip() for column in required_text):
            continue
        edge_length = _float(row.get("edge_length_m"))
        nominal_flow = _float(row.get("nominal_flow_Lmin"))
        if edge_length is None or nominal_flow is None or edge_length < 0 or nominal_flow <= 0:
            continue
        valid_ids.append(node_id)
        path_stages.add(str(row.get("path_stage", "")).strip())
        node_types.add(str(row.get("node_type", "")).strip())
    return {
        "signal_family": "site_topology",
        "row_count": len(rows),
        "valid_row_count": len(valid_ids),
        "valid_node_ids": sorted(set(valid_ids)),
        "path_stage_count": len(path_stages),
        "path_stages": sorted(path_stages),
        "node_types": sorted(node_types),
    }


def _cost_audit(rows: list[dict[str, str]]) -> dict[str, Any]:
    valid_ids = []
    installable_ids = []
    modality_pairs = set()
    sensor_types = set()
    capex_values = []
    for row in rows:
        if not _row_common_valid(row):
            continue
        node_id = str(row.get("node_id", "")).strip()
        modality = str(row.get("modality", "")).strip()
        sensor_type = str(row.get("sensor_type", "")).strip()
        capex = _float(row.get("capex_usd"))
        opex = _float(row.get("opex_usd_month"))
        interval = _float(row.get("maintenance_interval_day"))
        installable = _bool(row.get("installable_flag"))
        power = _bool(row.get("power_available"))
        communication = _bool(row.get("communication_available"))
        if (
            not modality
            or not sensor_type
            or capex is None
            or opex is None
            or interval is None
            or capex < 0
            or opex < 0
            or interval <= 0
            or installable is None
            or power is None
            or communication is None
        ):
            continue
        valid_ids.append(node_id)
        modality_pairs.add(f"{node_id}:{modality}")
        sensor_types.add(sensor_type)
        capex_values.append(capex)
        if installable and power and communication:
            installable_ids.append(node_id)
    return {
        "signal_family": "node_modality_cost",
        "row_count": len(rows),
        "valid_row_count": len(valid_ids),
        "valid_node_ids": sorted(set(valid_ids)),
        "installable_valid_node_ids": sorted(set(installable_ids)),
        "installable_candidate_node_count": len(set(installable_ids)),
        "node_modality_pair_count": len(modality_pairs),
        "sensor_types": sorted(sensor_types),
        "mean_capex_usd": round(sum(capex_values) / len(capex_values), 3) if capex_values else None,
    }


def _constraint_audit(rows: list[dict[str, str]]) -> dict[str, Any]:
    valid_ids = []
    review_required_count = 0
    access_levels = set()
    safety_classes = set()
    for row in rows:
        if not _row_common_valid(row):
            continue
        node_id = str(row.get("node_id", "")).strip()
        if any(
            not str(row.get(column, "")).strip()
            for column in ["constraint_id", "access_level", "safety_class"]
        ):
            continue
        maintenance_window = _float(row.get("maintenance_window_min"))
        downtime_cost = _float(row.get("downtime_cost_index"))
        review_required = _bool(row.get("operator_review_required"))
        if (
            maintenance_window is None
            or downtime_cost is None
            or review_required is None
            or maintenance_window < 0
            or downtime_cost < 0
        ):
            continue
        valid_ids.append(node_id)
        if review_required:
            review_required_count += 1
        access_levels.add(str(row.get("access_level", "")).strip())
        safety_classes.add(str(row.get("safety_class", "")).strip())
    return {
        "signal_family": "installability_constraint",
        "row_count": len(rows),
        "valid_row_count": len(valid_ids),
        "valid_node_ids": sorted(set(valid_ids)),
        "operator_review_required_row_count": review_required_count,
        "access_levels": sorted(access_levels),
        "safety_classes": sorted(safety_classes),
    }


def _hydraulic_delay_audit(rows: list[dict[str, str]]) -> dict[str, Any]:
    valid_ids = []
    delays = []
    confidences = []
    for row in rows:
        if not _row_common_valid(row):
            continue
        node_id = str(row.get("node_id", "")).strip()
        upstream_reference = str(row.get("upstream_reference", "")).strip()
        delay = _float(row.get("delay_min"))
        mixing_volume = _float(row.get("mixing_volume_L"))
        short_circuit_risk = _float(row.get("short_circuit_risk"))
        confidence = _float(row.get("hydraulic_confidence"))
        if (
            not upstream_reference
            or delay is None
            or mixing_volume is None
            or short_circuit_risk is None
            or confidence is None
            or delay < 0
            or mixing_volume <= 0
            or not 0 <= short_circuit_risk <= 1
            or not 0 <= confidence <= 1
        ):
            continue
        valid_ids.append(node_id)
        delays.append(delay)
        confidences.append(confidence)
    return {
        "signal_family": "hydraulic_delay",
        "row_count": len(rows),
        "valid_row_count": len(valid_ids),
        "valid_node_ids": sorted(set(valid_ids)),
        "mean_delay_min": round(sum(delays) / len(delays), 3) if delays else None,
        "mean_hydraulic_confidence": round(sum(confidences) / len(confidences), 3) if confidences else None,
    }


def _label_audit(rows: list[dict[str, str]]) -> dict[str, Any]:
    valid_ids = []
    hidden_states = set()
    splits = set()
    batch_ids = set()
    for row in rows:
        if not _row_common_valid(row):
            continue
        node_id = str(row.get("node_id", "")).strip()
        batch_id = str(row.get("batch_id", "")).strip()
        hidden_state = str(row.get("hidden_state", "")).strip()
        label_source = str(row.get("label_source", "")).strip()
        split = _normalize(row.get("layout_holdout_split"))
        timestamp = _float(row.get("timestamp_min"))
        label_value = _float(row.get("label_value"))
        if (
            not batch_id
            or not hidden_state
            or not label_source
            or split not in ACCEPTED_SPLITS
            or timestamp is None
            or label_value is None
            or timestamp < 0
        ):
            continue
        valid_ids.append(node_id)
        hidden_states.add(hidden_state)
        splits.add(split)
        batch_ids.add(batch_id)
    return {
        "signal_family": "labeled_state_matrix",
        "row_count": len(rows),
        "valid_row_count": len(valid_ids),
        "valid_node_ids": sorted(set(valid_ids)),
        "hidden_state_count": len(hidden_states),
        "hidden_states": sorted(hidden_states),
        "layout_holdout_splits": sorted(splits),
        "batch_count": len(batch_ids),
    }


def _blocking_reasons(
    *,
    missing_tables: list[str],
    header_gaps: list[dict[str, Any]],
    template_marker_count: int,
    non_field_row_count: int,
    topology_audit: dict[str, Any],
    cost_audit: dict[str, Any],
    constraint_audit: dict[str, Any],
    hydraulic_delay_audit: dict[str, Any],
    label_audit: dict[str, Any],
    matched_node_ids: list[str],
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
        ("insufficient_site_topology_nodes", topology_audit),
        ("insufficient_node_modality_cost_rows", cost_audit),
        ("insufficient_installability_constraint_rows", constraint_audit),
        ("insufficient_hydraulic_delay_rows", hydraulic_delay_audit),
        ("insufficient_labeled_state_rows", label_audit),
    ]
    for reason, audit in signal_requirements:
        if int(audit.get("valid_row_count", 0) or 0) < MINIMUM_MATCHED_NODE_COUNT:
            reasons.append(reason)
    if int(cost_audit.get("installable_candidate_node_count", 0) or 0) < MINIMUM_MATCHED_NODE_COUNT:
        reasons.append("installable_node_deficit")
    if len(matched_node_ids) < MINIMUM_MATCHED_NODE_COUNT:
        reasons.append("matched_node_deficit")
    return reasons


def _package_status(blocking_reasons: list[str]) -> str:
    if not blocking_reasons:
        return "sparse_topology_installability_package_ready_for_agent48_layout_holdout"
    if "missing_required_tables" in blocking_reasons or "missing_required_columns" in blocking_reasons:
        return "sparse_topology_installability_package_blocked_at_schema"
    if "template_markers_present" in blocking_reasons or "non_field_rows_present" in blocking_reasons:
        return "sparse_topology_installability_package_blocked_at_field_origin"
    if "installable_node_deficit" in blocking_reasons:
        return "sparse_topology_installability_package_blocked_at_installability"
    if "matched_node_deficit" in blocking_reasons:
        return "sparse_topology_installability_package_blocked_at_node_alignment"
    return "sparse_topology_installability_package_blocked_at_content_preflight"


def _next_operator_action(package_status: str) -> str:
    if package_status == "sparse_topology_installability_package_ready_for_agent48_layout_holdout":
        return "route_SPARSE_TOPOLOGY_INSTALLABILITY_PACKAGE_DIR_to_Agent48_sparse_layout_holdout_consumer"
    if package_status == "sparse_topology_installability_package_blocked_at_missing_source_dir":
        return "repair_SPARSE_TOPOLOGY_INSTALLABILITY_PACKAGE_DIR_path"
    if package_status == "sparse_topology_installability_package_blocked_at_schema":
        return "repair_SPARSE_TOPOLOGY_INSTALLABILITY_PACKAGE_csv_headers_and_required_tables"
    if package_status == "sparse_topology_installability_package_blocked_at_field_origin":
        return "replace_template_or_non_field_topology_rows_with_real_field_site_rows"
    if package_status == "sparse_topology_installability_package_blocked_at_installability":
        return "add_at_least_three_installable_powered_connected_candidate_sensor_nodes"
    if package_status == "sparse_topology_installability_package_blocked_at_node_alignment":
        return "add_at_least_three_shared_node_ids_across_topology_cost_constraints_delay_and_label_tables"
    return "fill_sparse_topology_installability_package_template_and_set_SPARSE_TOPOLOGY_INSTALLABILITY_PACKAGE_DIR"


def _empty_signal_audit(signal_family: str) -> dict[str, Any]:
    return {
        "signal_family": signal_family,
        "row_count": 0,
        "valid_row_count": 0,
        "valid_node_ids": [],
    }


def _row_common_valid(row: dict[str, str]) -> bool:
    node_id = str(row.get("node_id", "")).strip()
    if not node_id or "TODO" in node_id:
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
    if text in {"true", "1", "yes", "y", "available", "installable", "required", "是"}:
        return True
    if text in {"false", "0", "no", "n", "unavailable", "blocked", "否"}:
        return False
    return None


def _normalize(value: object) -> str:
    return str(value or "").strip().lower()


def _no_write_boundary() -> str:
    return (
        "This package is only a sparse topology and installability preflight input. It cannot "
        "write actuator policy, release-gate policy, deployable sensor layout approval, field "
        "soft-sensor claims or deployment clearance."
    )


def _topology_template_row(node_id: str, index: int) -> dict[str, str]:
    return {
        "node_id": node_id,
        "node_type": "TODO_reactor_or_pipe_or_tank_or_release_boundary",
        "upstream_node_id": "TODO_SOURCE_or_upstream_node_id",
        "downstream_node_id": "TODO_downstream_node_id_or_SINK",
        "unit_id": f"TODO_unit_{index + 1}",
        "path_stage": "TODO_inlet_buffer_reactor_catalyst_bed_recirculation_release",
        "edge_length_m": "TODO_numeric",
        "nominal_flow_Lmin": "TODO_numeric",
        "qa_flag": "TODO_pass",
        "data_origin": "TODO_field",
    }


def _cost_template_row(node_id: str) -> dict[str, str]:
    return {
        "node_id": node_id,
        "modality": "TODO_pH_ORP_UV254_turbidity_conductivity_flow_temperature_pressure",
        "sensor_type": "TODO_sensor_type",
        "capex_usd": "TODO_numeric",
        "opex_usd_month": "TODO_numeric",
        "maintenance_interval_day": "TODO_numeric",
        "installable_flag": "TODO_true_or_false",
        "power_available": "TODO_true_or_false",
        "communication_available": "TODO_true_or_false",
        "qa_flag": "TODO_pass",
        "data_origin": "TODO_field",
    }


def _constraint_template_row(node_id: str) -> dict[str, str]:
    return {
        "node_id": node_id,
        "constraint_id": "TODO_constraint_id",
        "access_level": "TODO_easy_medium_hard",
        "safety_class": "TODO_safety_class",
        "maintenance_window_min": "TODO_numeric",
        "downtime_cost_index": "TODO_numeric",
        "operator_review_required": "TODO_true_or_false",
        "blocked_reason": "TODO_none_or_reason",
        "qa_flag": "TODO_pass",
        "data_origin": "TODO_field",
    }


def _hydraulic_delay_template_row(node_id: str) -> dict[str, str]:
    return {
        "node_id": node_id,
        "upstream_reference": "TODO_upstream_reference_node_or_unit",
        "delay_min": "TODO_numeric",
        "mixing_volume_L": "TODO_numeric",
        "short_circuit_risk": "TODO_0_to_1",
        "hydraulic_confidence": "TODO_0_to_1",
        "qa_flag": "TODO_pass",
        "data_origin": "TODO_field",
    }


def _label_template_row(node_id: str, index: int) -> dict[str, str]:
    return {
        "node_id": node_id,
        "batch_id": f"TODO_batch_{index}",
        "timestamp_min": "TODO_numeric",
        "hidden_state": "TODO_residual_pollutant_or_catalyst_activity_or_matrix_inhibition",
        "label_value": "TODO_numeric",
        "label_source": "TODO_lab_or_operator_review_or_field_holdout",
        "layout_holdout_split": "TODO_train_or_field_holdout",
        "qa_flag": "TODO_pass",
        "data_origin": "TODO_field",
    }

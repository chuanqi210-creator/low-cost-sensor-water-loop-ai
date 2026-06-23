from __future__ import annotations

import csv
import math
from pathlib import Path
from typing import Any


PACKAGE_ID = "R8u150_field_supported_kg_edge_package_preflight"
SOURCE_ENV_VAR = "FIELD_SUPPORTED_KG_EDGE_PACKAGE_DIR"
MINIMUM_MATCHED_EDGE_COUNT = 3

EDGE_TABLE = "pollutant_material_condition_edges"
SOURCE_BASIS_TABLE = "source_basis_rows"
FIELD_SUPPORT_TABLE = "field_supported_edge_rows"
FAILURE_BOUNDARY_TABLE = "failure_boundary_annotations"
CLAIM_ACTION_TABLE = "claim_action_constraint_links"

REQUIRED_TABLES = (
    EDGE_TABLE,
    SOURCE_BASIS_TABLE,
    FIELD_SUPPORT_TABLE,
    FAILURE_BOUNDARY_TABLE,
    CLAIM_ACTION_TABLE,
)

TABLE_COLUMNS = {
    EDGE_TABLE: [
        "edge_id",
        "pollutant",
        "material_or_unit",
        "condition_axis",
        "relation",
        "hidden_state",
        "action_constraint_id",
        "evidence_stage",
        "qa_flag",
        "data_origin",
    ],
    SOURCE_BASIS_TABLE: [
        "edge_id",
        "source_basis_id",
        "source_type",
        "source_reference",
        "source_detail",
        "qa_flag",
        "data_origin",
    ],
    FIELD_SUPPORT_TABLE: [
        "edge_id",
        "batch_id",
        "node_id",
        "observed_metric",
        "observed_value",
        "expected_direction",
        "support_direction",
        "field_support_score",
        "qa_flag",
        "data_origin",
    ],
    FAILURE_BOUNDARY_TABLE: [
        "edge_id",
        "boundary_type",
        "boundary_statement",
        "cannot_claim_without",
        "qa_flag",
        "data_origin",
    ],
    CLAIM_ACTION_TABLE: [
        "edge_id",
        "claim_or_action_id",
        "constraint_type",
        "allowed_use",
        "blocked_use",
        "human_review_required",
        "qa_flag",
        "data_origin",
    ],
}

ACCEPTED_QA_FLAGS = {"pass", "passed", "valid", "ok", "qc_pass", "qualified", "合格"}
FIELD_SUPPORTED_STAGES = {"field_supported", "field_validated", "field_replay_supported"}
FIELD_SOURCE_TYPES = {"field_lab", "field_sensor", "operation_log", "field_replay", "human_review"}


def build_field_supported_kg_edge_package_template(
    edge_ids: list[str] | None = None,
) -> dict[str, Any]:
    ids = edge_ids or ["TODO_edge_id_1", "TODO_edge_id_2", "TODO_edge_id_3"]
    tables = {
        EDGE_TABLE: {
            "columns": TABLE_COLUMNS[EDGE_TABLE],
            "rows": [_edge_template_row(edge_id) for edge_id in ids],
        },
        SOURCE_BASIS_TABLE: {
            "columns": TABLE_COLUMNS[SOURCE_BASIS_TABLE],
            "rows": [_source_basis_template_row(edge_id) for edge_id in ids],
        },
        FIELD_SUPPORT_TABLE: {
            "columns": TABLE_COLUMNS[FIELD_SUPPORT_TABLE],
            "rows": [_field_support_template_row(edge_id) for edge_id in ids],
        },
        FAILURE_BOUNDARY_TABLE: {
            "columns": TABLE_COLUMNS[FAILURE_BOUNDARY_TABLE],
            "rows": [_failure_boundary_template_row(edge_id) for edge_id in ids],
        },
        CLAIM_ACTION_TABLE: {
            "columns": TABLE_COLUMNS[CLAIM_ACTION_TABLE],
            "rows": [_claim_action_template_row(edge_id) for edge_id in ids],
        },
    }
    return {
        "package_id": PACKAGE_ID,
        "package_type": "field_supported_kg_edge_package_template",
        "source_env_var": SOURCE_ENV_VAR,
        "required_table_count": len(REQUIRED_TABLES),
        "required_tables": list(REQUIRED_TABLES),
        "minimum_matched_edge_count": MINIMUM_MATCHED_EDGE_COUNT,
        "tables": tables,
        "table_row_counts": {name: len(table["rows"]) for name, table in tables.items()},
        "operator_instructions": [
            "Fill TODO values with real field-supported KG edge records.",
            "Use at least three shared edge_id values across all five tables.",
            "Use data_origin=field for every row.",
            "Use evidence_stage=field_supported or stronger for every KG edge row.",
            "Attach a concrete source_basis, field support row, failure boundary and claim/action constraint to every edge.",
        ],
        "no_write_boundary": _no_write_boundary(),
    }


def write_field_supported_kg_edge_package_template(target_dir: str | Path) -> dict[str, Any]:
    target = Path(target_dir)
    target.mkdir(parents=True, exist_ok=True)
    template = build_field_supported_kg_edge_package_template()
    for table_name, table in template["tables"].items():
        _write_csv(target / f"{table_name}.csv", table["columns"], table["rows"])
    return template


def build_field_supported_kg_edge_package_preflight(
    *,
    source_dir: str | Path | None = None,
    external_package_supplied: bool = False,
) -> dict[str, Any]:
    source = Path(source_dir) if source_dir not in (None, "") else None
    if not external_package_supplied or source is None:
        return _preflight_payload(
            source_path="" if source is None else str(source),
            external_package_supplied=False,
            package_status="field_supported_kg_edge_package_waiting_for_FIELD_SUPPORTED_KG_EDGE_PACKAGE_DIR",
            table_audits={},
            edge_audit=_empty_signal_audit("kg_edge"),
            source_basis_audit=_empty_signal_audit("source_basis"),
            field_support_audit=_empty_signal_audit("field_support"),
            failure_boundary_audit=_empty_signal_audit("failure_boundary"),
            claim_action_audit=_empty_signal_audit("claim_action_constraint"),
            matched_edge_ids=[],
            blocking_reasons=["missing_external_package_dir"],
        )
    if not source.exists() or not source.is_dir():
        return _preflight_payload(
            source_path=str(source),
            external_package_supplied=True,
            package_status="field_supported_kg_edge_package_blocked_at_missing_source_dir",
            table_audits={},
            edge_audit=_empty_signal_audit("kg_edge"),
            source_basis_audit=_empty_signal_audit("source_basis"),
            field_support_audit=_empty_signal_audit("field_support"),
            failure_boundary_audit=_empty_signal_audit("failure_boundary"),
            claim_action_audit=_empty_signal_audit("claim_action_constraint"),
            matched_edge_ids=[],
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

    edge_audit = _edge_audit(tables.get(EDGE_TABLE, []))
    source_basis_audit = _source_basis_audit(tables.get(SOURCE_BASIS_TABLE, []))
    field_support_audit = _field_support_audit(tables.get(FIELD_SUPPORT_TABLE, []))
    failure_boundary_audit = _failure_boundary_audit(tables.get(FAILURE_BOUNDARY_TABLE, []))
    claim_action_audit = _claim_action_audit(tables.get(CLAIM_ACTION_TABLE, []))
    matched_edge_ids = sorted(
        set(edge_audit["valid_edge_ids"])
        & set(source_basis_audit["valid_edge_ids"])
        & set(field_support_audit["valid_edge_ids"])
        & set(failure_boundary_audit["valid_edge_ids"])
        & set(claim_action_audit["valid_edge_ids"])
    )
    blocking_reasons = _blocking_reasons(
        missing_tables=missing_tables,
        header_gaps=header_gaps,
        template_marker_count=template_marker_count,
        non_field_row_count=non_field_row_count,
        edge_audit=edge_audit,
        source_basis_audit=source_basis_audit,
        field_support_audit=field_support_audit,
        failure_boundary_audit=failure_boundary_audit,
        claim_action_audit=claim_action_audit,
        matched_edge_ids=matched_edge_ids,
    )
    return _preflight_payload(
        source_path=str(source),
        external_package_supplied=True,
        package_status=_package_status(blocking_reasons),
        table_audits=table_audits,
        edge_audit=edge_audit,
        source_basis_audit=source_basis_audit,
        field_support_audit=field_support_audit,
        failure_boundary_audit=failure_boundary_audit,
        claim_action_audit=claim_action_audit,
        matched_edge_ids=matched_edge_ids,
        blocking_reasons=blocking_reasons,
    )


def _preflight_payload(
    *,
    source_path: str,
    external_package_supplied: bool,
    package_status: str,
    table_audits: dict[str, dict[str, Any]],
    edge_audit: dict[str, Any],
    source_basis_audit: dict[str, Any],
    field_support_audit: dict[str, Any],
    failure_boundary_audit: dict[str, Any],
    claim_action_audit: dict[str, Any],
    matched_edge_ids: list[str],
    blocking_reasons: list[str],
) -> dict[str, Any]:
    preflight_pass = external_package_supplied and not blocking_reasons
    coverage = round(min(1.0, len(matched_edge_ids) / MINIMUM_MATCHED_EDGE_COUNT), 3)
    return {
        "package_id": PACKAGE_ID,
        "package_type": "field_supported_kg_edge_package_preflight",
        "source_env_var": SOURCE_ENV_VAR,
        "source_path": source_path,
        "external_package_supplied": external_package_supplied,
        "package_status": package_status,
        "package_preflight_pass": preflight_pass,
        "required_table_count": len(REQUIRED_TABLES),
        "required_tables": list(REQUIRED_TABLES),
        "minimum_matched_edge_count": MINIMUM_MATCHED_EDGE_COUNT,
        "matched_edge_count": len(matched_edge_ids),
        "matched_edge_ids": matched_edge_ids,
        "field_supported_edge_coverage_candidate": coverage,
        "table_audits": table_audits,
        "edge_audit": edge_audit,
        "source_basis_audit": source_basis_audit,
        "field_support_audit": field_support_audit,
        "failure_boundary_audit": failure_boundary_audit,
        "claim_action_audit": claim_action_audit,
        "blocking_reasons": blocking_reasons,
        "can_route_to_kg_reasoning_field_edge_update": preflight_pass,
        "can_upgrade_site_specific_claims": False,
        "can_generate_field_evidence": False,
        "can_resume_model_chain": False,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
        "next_operator_action": _next_operator_action(package_status),
        "field_boundary": (
            "This preflight only checks whether an external KG edge package is structurally "
            "ready for downstream KG reasoning. Passing this gate does not prove a site-specific "
            "mechanism claim, authorize control actions, or upgrade release decisions."
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


def _edge_audit(rows: list[dict[str, str]]) -> dict[str, Any]:
    valid_ids = []
    relations = set()
    for row in rows:
        if not _row_common_valid(row):
            continue
        edge_id = str(row.get("edge_id", "")).strip()
        if _normalize(row.get("evidence_stage")) not in FIELD_SUPPORTED_STAGES:
            continue
        required_text = [
            "pollutant",
            "material_or_unit",
            "condition_axis",
            "relation",
            "hidden_state",
            "action_constraint_id",
        ]
        if any(not str(row.get(column, "")).strip() for column in required_text):
            continue
        valid_ids.append(edge_id)
        relations.add(str(row.get("relation", "")).strip())
    return {
        "signal_family": "kg_edge",
        "row_count": len(rows),
        "valid_row_count": len(valid_ids),
        "valid_edge_ids": sorted(set(valid_ids)),
        "relation_count": len(relations),
        "relations": sorted(relations),
    }


def _source_basis_audit(rows: list[dict[str, str]]) -> dict[str, Any]:
    valid_ids = []
    source_types = set()
    for row in rows:
        if not _row_common_valid(row):
            continue
        source_type = _normalize(row.get("source_type"))
        if source_type not in FIELD_SOURCE_TYPES:
            continue
        if any(
            not str(row.get(column, "")).strip()
            for column in ["source_basis_id", "source_reference", "source_detail"]
        ):
            continue
        valid_ids.append(str(row.get("edge_id", "")).strip())
        source_types.add(source_type)
    return {
        "signal_family": "source_basis",
        "row_count": len(rows),
        "valid_row_count": len(valid_ids),
        "valid_edge_ids": sorted(set(valid_ids)),
        "source_types": sorted(source_types),
    }


def _field_support_audit(rows: list[dict[str, str]]) -> dict[str, Any]:
    valid_ids = []
    scores = []
    for row in rows:
        if not _row_common_valid(row):
            continue
        observed_value = _float(row.get("observed_value"))
        support_score = _float(row.get("field_support_score"))
        if observed_value is None or support_score is None or not 0 <= support_score <= 1:
            continue
        if any(
            not str(row.get(column, "")).strip()
            for column in ["batch_id", "node_id", "observed_metric", "expected_direction", "support_direction"]
        ):
            continue
        valid_ids.append(str(row.get("edge_id", "")).strip())
        scores.append(float(support_score))
    return {
        "signal_family": "field_support",
        "row_count": len(rows),
        "valid_row_count": len(valid_ids),
        "valid_edge_ids": sorted(set(valid_ids)),
        "mean_field_support_score": round(sum(scores) / len(scores), 3) if scores else None,
        "min_field_support_score": round(min(scores), 3) if scores else None,
    }


def _failure_boundary_audit(rows: list[dict[str, str]]) -> dict[str, Any]:
    valid_ids = []
    boundary_types = set()
    for row in rows:
        if not _row_common_valid(row):
            continue
        if any(
            not str(row.get(column, "")).strip()
            for column in ["boundary_type", "boundary_statement", "cannot_claim_without"]
        ):
            continue
        valid_ids.append(str(row.get("edge_id", "")).strip())
        boundary_types.add(str(row.get("boundary_type", "")).strip())
    return {
        "signal_family": "failure_boundary",
        "row_count": len(rows),
        "valid_row_count": len(valid_ids),
        "valid_edge_ids": sorted(set(valid_ids)),
        "boundary_types": sorted(boundary_types),
    }


def _claim_action_audit(rows: list[dict[str, str]]) -> dict[str, Any]:
    valid_ids = []
    human_review_count = 0
    for row in rows:
        if not _row_common_valid(row):
            continue
        if any(
            not str(row.get(column, "")).strip()
            for column in ["claim_or_action_id", "constraint_type", "allowed_use", "blocked_use"]
        ):
            continue
        review_required = _normalize(row.get("human_review_required")) in {"true", "1", "yes", "y", "required"}
        if not review_required:
            continue
        valid_ids.append(str(row.get("edge_id", "")).strip())
        human_review_count += 1
    return {
        "signal_family": "claim_action_constraint",
        "row_count": len(rows),
        "valid_row_count": len(valid_ids),
        "valid_edge_ids": sorted(set(valid_ids)),
        "human_review_required_row_count": human_review_count,
    }


def _blocking_reasons(
    *,
    missing_tables: list[str],
    header_gaps: list[dict[str, Any]],
    template_marker_count: int,
    non_field_row_count: int,
    edge_audit: dict[str, Any],
    source_basis_audit: dict[str, Any],
    field_support_audit: dict[str, Any],
    failure_boundary_audit: dict[str, Any],
    claim_action_audit: dict[str, Any],
    matched_edge_ids: list[str],
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
        ("insufficient_kg_edges", edge_audit),
        ("insufficient_source_basis_rows", source_basis_audit),
        ("insufficient_field_support_rows", field_support_audit),
        ("insufficient_failure_boundary_rows", failure_boundary_audit),
        ("insufficient_claim_action_constraint_rows", claim_action_audit),
    ]
    for reason, audit in signal_requirements:
        if int(audit.get("valid_row_count", 0) or 0) < MINIMUM_MATCHED_EDGE_COUNT:
            reasons.append(reason)
    if len(matched_edge_ids) < MINIMUM_MATCHED_EDGE_COUNT:
        reasons.append("matched_edge_deficit")
    return reasons


def _package_status(blocking_reasons: list[str]) -> str:
    if not blocking_reasons:
        return "field_supported_kg_edge_package_ready_for_kg_reasoning"
    if "missing_required_tables" in blocking_reasons or "missing_required_columns" in blocking_reasons:
        return "field_supported_kg_edge_package_blocked_at_schema"
    if "template_markers_present" in blocking_reasons or "non_field_rows_present" in blocking_reasons:
        return "field_supported_kg_edge_package_blocked_at_field_origin"
    if "matched_edge_deficit" in blocking_reasons:
        return "field_supported_kg_edge_package_blocked_at_edge_alignment"
    return "field_supported_kg_edge_package_blocked_at_content_preflight"


def _next_operator_action(package_status: str) -> str:
    if package_status == "field_supported_kg_edge_package_ready_for_kg_reasoning":
        return "route_FIELD_SUPPORTED_KG_EDGE_PACKAGE_DIR_to_KG_reasoning_field_edge_preflight_consumer"
    if package_status == "field_supported_kg_edge_package_blocked_at_missing_source_dir":
        return "repair_FIELD_SUPPORTED_KG_EDGE_PACKAGE_DIR_path"
    if package_status == "field_supported_kg_edge_package_blocked_at_schema":
        return "repair_FIELD_SUPPORTED_KG_EDGE_PACKAGE_csv_headers_and_required_tables"
    if package_status == "field_supported_kg_edge_package_blocked_at_field_origin":
        return "replace_template_or_non_field_KG_edge_rows_with_real_field_supported_rows"
    if package_status == "field_supported_kg_edge_package_blocked_at_edge_alignment":
        return "add_at_least_three_shared_edge_ids_across_all_field_supported_KG_edge_tables"
    return "fill_field_supported_kg_edge_package_template_and_set_FIELD_SUPPORTED_KG_EDGE_PACKAGE_DIR"


def _empty_signal_audit(signal_family: str) -> dict[str, Any]:
    return {
        "signal_family": signal_family,
        "row_count": 0,
        "valid_row_count": 0,
        "valid_edge_ids": [],
    }


def _row_common_valid(row: dict[str, str]) -> bool:
    edge_id = str(row.get("edge_id", "")).strip()
    if not edge_id or "TODO" in edge_id:
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


def _normalize(value: object) -> str:
    return str(value or "").strip().lower()


def _no_write_boundary() -> str:
    return (
        "This package is only a field-supported KG edge preflight input. It cannot write "
        "actuator policy, release-gate policy, field-supported mechanism claims, claim text "
        "or deployment clearance."
    )


def _edge_template_row(edge_id: str) -> dict[str, str]:
    return {
        "edge_id": edge_id,
        "pollutant": "TODO_pollutant",
        "material_or_unit": "TODO_material_or_unit",
        "condition_axis": "TODO_condition_axis",
        "relation": "TODO_relation",
        "hidden_state": "TODO_hidden_state",
        "action_constraint_id": "TODO_action_constraint_id",
        "evidence_stage": "TODO_field_supported",
        "qa_flag": "TODO_pass",
        "data_origin": "TODO_field",
    }


def _source_basis_template_row(edge_id: str) -> dict[str, str]:
    return {
        "edge_id": edge_id,
        "source_basis_id": "TODO_source_basis_id",
        "source_type": "TODO_field_lab_or_operation_log",
        "source_reference": "TODO_source_reference",
        "source_detail": "TODO_source_detail",
        "qa_flag": "TODO_pass",
        "data_origin": "TODO_field",
    }


def _field_support_template_row(edge_id: str) -> dict[str, str]:
    return {
        "edge_id": edge_id,
        "batch_id": "TODO_batch_id",
        "node_id": "TODO_node_id",
        "observed_metric": "TODO_metric",
        "observed_value": "TODO_value",
        "expected_direction": "TODO_increase_or_decrease",
        "support_direction": "TODO_supported_or_contradicted",
        "field_support_score": "TODO_0_to_1",
        "qa_flag": "TODO_pass",
        "data_origin": "TODO_field",
    }


def _failure_boundary_template_row(edge_id: str) -> dict[str, str]:
    return {
        "edge_id": edge_id,
        "boundary_type": "TODO_boundary_type",
        "boundary_statement": "TODO_boundary_statement",
        "cannot_claim_without": "TODO_required_evidence_before_claim",
        "qa_flag": "TODO_pass",
        "data_origin": "TODO_field",
    }


def _claim_action_template_row(edge_id: str) -> dict[str, str]:
    return {
        "edge_id": edge_id,
        "claim_or_action_id": "TODO_claim_or_action_id",
        "constraint_type": "TODO_constraint_type",
        "allowed_use": "TODO_allowed_use",
        "blocked_use": "TODO_blocked_use",
        "human_review_required": "TODO_true",
        "qa_flag": "TODO_pass",
        "data_origin": "TODO_field",
    }

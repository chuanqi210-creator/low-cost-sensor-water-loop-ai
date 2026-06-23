from __future__ import annotations

import csv
import math
from pathlib import Path
from typing import Any


PACKAGE_ID = "R8u148_grey_box_calibration_package_preflight"
FIELD_CALIBRATION_SUMMARY_ID = "R8u149_grey_box_field_calibration_summary"
COLLECTION_WORK_ORDER_ID = "R8u157_grey_box_calibration_collection_work_order"
SUBMISSION_READINESS_GATE_ID = "R8u160_grey_box_submission_readiness_gate"
SOURCE_ENV_VAR = "GREY_BOX_CALIBRATION_PACKAGE_DIR"
MINIMUM_MATCHED_BATCH_COUNT = 3
AGENT53_MAX_FIELD_RESIDUAL = 0.18
AGENT53_MAX_MASS_BALANCE_RESIDUAL = 0.16

BATCH_LAB_TABLE = "batch_inlet_outlet_lab"
HYDRAULIC_TABLE = "hydraulic_rtd_or_tracer"
OXIDANT_TABLE = "oxidant_dose_residual_log"
CATALYST_TABLE = "catalyst_age_regeneration_log"
BYPRODUCT_TABLE = "byproduct_panel"

REQUIRED_TABLES = (
    BATCH_LAB_TABLE,
    HYDRAULIC_TABLE,
    OXIDANT_TABLE,
    CATALYST_TABLE,
    BYPRODUCT_TABLE,
)

TABLE_COLUMNS = {
    BATCH_LAB_TABLE: [
        "batch_id",
        "sample_time_min",
        "target_pollutant",
        "inlet_concentration",
        "outlet_concentration",
        "pollutant_unit",
        "matrix_indicator",
        "matrix_indicator_unit",
        "lab_method",
        "qa_flag",
        "data_origin",
    ],
    HYDRAULIC_TABLE: [
        "batch_id",
        "measurement_time_min",
        "unit_id",
        "effective_HRT_min",
        "nominal_HRT_min",
        "rtd_t10_min",
        "rtd_t90_min",
        "tracer_recovery_fraction",
        "flow_Lmin",
        "volume_L",
        "qa_flag",
        "data_origin",
    ],
    OXIDANT_TABLE: [
        "batch_id",
        "timestamp_min",
        "oxidant_name",
        "dose_mg_L",
        "residual_mg_L",
        "energy_kWh_m3",
        "qa_flag",
        "data_origin",
    ],
    CATALYST_TABLE: [
        "batch_id",
        "timestamp_min",
        "catalyst_id",
        "catalyst_age_h",
        "catalyst_activity_label",
        "regeneration_event",
        "regeneration_count",
        "qa_flag",
        "data_origin",
    ],
    BYPRODUCT_TABLE: [
        "batch_id",
        "sample_time_min",
        "analyte",
        "value",
        "unit",
        "detection_limit",
        "method",
        "qa_flag",
        "data_origin",
    ],
}

ACCEPTED_QA_FLAGS = {"pass", "passed", "valid", "ok", "qc_pass", "qualified", "合格"}


def build_grey_box_calibration_package_template(
    batch_ids: list[str] | None = None,
) -> dict[str, Any]:
    """Build the minimum external package template for Agent53 field calibration."""

    ids = batch_ids or ["TODO_batch_id_1", "TODO_batch_id_2", "TODO_batch_id_3"]
    tables = {
        BATCH_LAB_TABLE: {
            "columns": TABLE_COLUMNS[BATCH_LAB_TABLE],
            "rows": [_lab_template_row(batch_id) for batch_id in ids],
        },
        HYDRAULIC_TABLE: {
            "columns": TABLE_COLUMNS[HYDRAULIC_TABLE],
            "rows": [_hydraulic_template_row(batch_id) for batch_id in ids],
        },
        OXIDANT_TABLE: {
            "columns": TABLE_COLUMNS[OXIDANT_TABLE],
            "rows": [_oxidant_template_row(batch_id) for batch_id in ids],
        },
        CATALYST_TABLE: {
            "columns": TABLE_COLUMNS[CATALYST_TABLE],
            "rows": [_catalyst_template_row(batch_id) for batch_id in ids],
        },
        BYPRODUCT_TABLE: {
            "columns": TABLE_COLUMNS[BYPRODUCT_TABLE],
            "rows": [_byproduct_template_row(batch_id) for batch_id in ids],
        },
    }
    return {
        "package_id": PACKAGE_ID,
        "package_type": "grey_box_calibration_package_template",
        "source_env_var": SOURCE_ENV_VAR,
        "required_table_count": len(REQUIRED_TABLES),
        "required_tables": list(REQUIRED_TABLES),
        "minimum_matched_batch_count": MINIMUM_MATCHED_BATCH_COUNT,
        "tables": tables,
        "table_row_counts": {name: len(table["rows"]) for name, table in tables.items()},
        "operator_instructions": [
            "Fill all TODO values with real field records before preflight.",
            "Use at least three shared batch_id values across all five tables.",
            "Keep data_origin=field for every row.",
            "Use QA-passed lab, hydraulic, oxidant, catalyst and byproduct rows.",
            "Provide positive inlet concentration, HRT/RTD, flow/volume and nonnegative dose/residual/byproduct values.",
        ],
        "no_write_boundary": _no_write_boundary(),
    }


def write_grey_box_calibration_package_template(target_dir: str | Path) -> dict[str, Any]:
    """Write the grey-box calibration package CSV template."""

    target = Path(target_dir)
    target.mkdir(parents=True, exist_ok=True)
    template = build_grey_box_calibration_package_template()
    for table_name, table in template["tables"].items():
        _write_csv(target / f"{table_name}.csv", table["columns"], table["rows"])
    return template


def build_grey_box_calibration_package_preflight(
    *,
    source_dir: str | Path | None = None,
    external_package_supplied: bool = False,
) -> dict[str, Any]:
    """Preflight a grey-box calibration package without upgrading it to field evidence."""

    source = Path(source_dir) if source_dir not in (None, "") else None
    if not external_package_supplied or source is None:
        return _preflight_payload(
            source_path="" if source is None else str(source),
            external_package_supplied=False,
            package_status="grey_box_calibration_package_waiting_for_GREY_BOX_CALIBRATION_PACKAGE_DIR",
            table_audits={},
            lab_audit=_empty_signal_audit("lab_pair"),
            hydraulic_audit=_empty_signal_audit("hydraulic_rtd"),
            oxidant_audit=_empty_signal_audit("oxidant_dose_residual"),
            catalyst_audit=_empty_signal_audit("catalyst_history"),
            byproduct_audit=_empty_signal_audit("byproduct_panel"),
            matched_batch_ids=[],
            blocking_reasons=["missing_external_package_dir"],
        )
    if not source.exists() or not source.is_dir():
        return _preflight_payload(
            source_path=str(source),
            external_package_supplied=True,
            package_status="grey_box_calibration_package_blocked_at_missing_source_dir",
            table_audits={},
            lab_audit=_empty_signal_audit("lab_pair"),
            hydraulic_audit=_empty_signal_audit("hydraulic_rtd"),
            oxidant_audit=_empty_signal_audit("oxidant_dose_residual"),
            catalyst_audit=_empty_signal_audit("catalyst_history"),
            byproduct_audit=_empty_signal_audit("byproduct_panel"),
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
    non_field_row_count = sum(int(audit["non_field_row_count"]) for audit in table_audits.values())

    lab_audit = _lab_pair_audit(tables.get(BATCH_LAB_TABLE, []))
    hydraulic_audit = _hydraulic_audit(tables.get(HYDRAULIC_TABLE, []))
    oxidant_audit = _oxidant_audit(tables.get(OXIDANT_TABLE, []))
    catalyst_audit = _catalyst_audit(tables.get(CATALYST_TABLE, []))
    byproduct_audit = _byproduct_audit(tables.get(BYPRODUCT_TABLE, []))
    matched_batch_ids = sorted(
        set(lab_audit["valid_batch_ids"])
        & set(hydraulic_audit["valid_batch_ids"])
        & set(oxidant_audit["valid_batch_ids"])
        & set(catalyst_audit["valid_batch_ids"])
        & set(byproduct_audit["valid_batch_ids"])
    )
    blocking_reasons = _blocking_reasons(
        missing_tables=missing_tables,
        header_gaps=header_gaps,
        template_marker_count=template_marker_count,
        non_field_row_count=non_field_row_count,
        lab_audit=lab_audit,
        hydraulic_audit=hydraulic_audit,
        oxidant_audit=oxidant_audit,
        catalyst_audit=catalyst_audit,
        byproduct_audit=byproduct_audit,
        matched_batch_ids=matched_batch_ids,
    )
    return _preflight_payload(
        source_path=str(source),
        external_package_supplied=True,
        package_status=_package_status(blocking_reasons),
        table_audits=table_audits,
        lab_audit=lab_audit,
        hydraulic_audit=hydraulic_audit,
        oxidant_audit=oxidant_audit,
        catalyst_audit=catalyst_audit,
        byproduct_audit=byproduct_audit,
        matched_batch_ids=matched_batch_ids,
        blocking_reasons=blocking_reasons,
    )


def build_grey_box_field_calibration_summary(
    *,
    source_dir: str | Path | None = None,
    external_package_supplied: bool = False,
    preflight: dict[str, Any] | None = None,
    max_field_residual: float = AGENT53_MAX_FIELD_RESIDUAL,
    max_mass_balance_residual: float = AGENT53_MAX_MASS_BALANCE_RESIDUAL,
) -> dict[str, Any]:
    """Build an Agent53-compatible field-calibration summary from a preflighted package."""

    package_preflight = preflight or build_grey_box_calibration_package_preflight(
        source_dir=source_dir,
        external_package_supplied=external_package_supplied,
    )
    if not package_preflight.get("package_preflight_pass", False):
        return _field_calibration_summary_payload(
            source_path=str(package_preflight.get("source_path", "")),
            package_preflight_status=str(
                package_preflight.get("package_status", "grey_box_calibration_package_preflight_missing")
            ),
            package_preflight_pass=False,
            matched_batch_ids=[],
            batch_calibration_rows=[],
            max_field_residual=max_field_residual,
            max_mass_balance_residual=max_mass_balance_residual,
            summary_status="grey_box_field_calibration_waiting_for_preflight_ready",
            blocking_reasons=list(package_preflight.get("blocking_reasons", [])),
        )

    source_path = str(source_dir or package_preflight.get("source_path", ""))
    source = Path(source_path) if source_path else None
    if source is None or not source.exists() or not source.is_dir():
        return _field_calibration_summary_payload(
            source_path=source_path,
            package_preflight_status=str(package_preflight.get("package_status", "")),
            package_preflight_pass=True,
            matched_batch_ids=[],
            batch_calibration_rows=[],
            max_field_residual=max_field_residual,
            max_mass_balance_residual=max_mass_balance_residual,
            summary_status="grey_box_field_calibration_blocked_at_source_reload",
            blocking_reasons=["source_dir_missing_when_building_field_calibration_summary"],
        )

    tables, _ = _read_tables(source)
    lab_rows = _first_valid_row_by_batch(tables.get(BATCH_LAB_TABLE, []))
    hydraulic_rows = _first_valid_row_by_batch(tables.get(HYDRAULIC_TABLE, []))
    byproduct_sums = _byproduct_sum_by_batch(tables.get(BYPRODUCT_TABLE, []))
    matched_batch_ids = [
        str(batch_id)
        for batch_id in package_preflight.get("matched_batch_ids", [])
        if str(batch_id) in lab_rows and str(batch_id) in hydraulic_rows
    ]
    batch_calibration_rows = [
        _batch_field_calibration_row(
            batch_id=batch_id,
            lab_row=lab_rows[batch_id],
            hydraulic_row=hydraulic_rows[batch_id],
            byproduct_value=byproduct_sums.get(batch_id, 0.0),
        )
        for batch_id in matched_batch_ids
    ]
    usable_rows = [row for row in batch_calibration_rows if row["usable_for_agent53_field_calibration"]]
    if len(usable_rows) < MINIMUM_MATCHED_BATCH_COUNT:
        return _field_calibration_summary_payload(
            source_path=source_path,
            package_preflight_status=str(package_preflight.get("package_status", "")),
            package_preflight_pass=True,
            matched_batch_ids=matched_batch_ids,
            batch_calibration_rows=batch_calibration_rows,
            max_field_residual=max_field_residual,
            max_mass_balance_residual=max_mass_balance_residual,
            summary_status="grey_box_field_calibration_blocked_at_computable_batch_summary",
            blocking_reasons=["insufficient_computable_field_calibration_rows"],
        )

    return _field_calibration_summary_payload(
        source_path=source_path,
        package_preflight_status=str(package_preflight.get("package_status", "")),
        package_preflight_pass=True,
        matched_batch_ids=matched_batch_ids,
        batch_calibration_rows=usable_rows,
        max_field_residual=max_field_residual,
        max_mass_balance_residual=max_mass_balance_residual,
        summary_status="",
        blocking_reasons=[],
    )


def build_grey_box_calibration_collection_work_order(
    *,
    preflight: dict[str, Any],
    field_calibration_summary: dict[str, Any],
    template_dir: str,
    validation_command: str,
) -> dict[str, Any]:
    """Build an operator-facing work order for the next grey-box field package."""

    table_audits = preflight.get("table_audits", {})
    work_items = [
        _collection_table_work_item(
            table_name=table_name,
            template_dir=template_dir,
            table_audit=table_audits.get(table_name, {}),
            signal_audit=_signal_audit_for_table(table_name, preflight),
            external_package_supplied=bool(preflight.get("external_package_supplied", False)),
        )
        for table_name in REQUIRED_TABLES
    ]
    work_order_status = _collection_work_order_status(
        preflight=preflight,
        field_calibration_summary=field_calibration_summary,
    )
    next_operator_action = _collection_next_operator_action(
        work_order_status=work_order_status,
        preflight=preflight,
        field_calibration_summary=field_calibration_summary,
    )
    return {
        "work_order_id": COLLECTION_WORK_ORDER_ID,
        "work_order_type": "grey_box_calibration_external_field_package_collection_work_order",
        "architecture_layer": "verification_governance_to_state_estimation",
        "enhanced_abilities": ["verifiability", "engineering_feasibility", "explainability"],
        "source_package_id": preflight.get("package_id", PACKAGE_ID),
        "source_summary_id": field_calibration_summary.get(
            "summary_id",
            FIELD_CALIBRATION_SUMMARY_ID,
        ),
        "work_order_status": work_order_status,
        "source_env_var": SOURCE_ENV_VAR,
        "source_path": str(preflight.get("source_path", "")),
        "template_dir": template_dir,
        "validation_command": validation_command,
        "run_after_submission": [validation_command] if validation_command else [],
        "package_status": str(preflight.get("package_status", "")),
        "summary_status": str(field_calibration_summary.get("summary_status", "")),
        "minimum_matched_batch_count": MINIMUM_MATCHED_BATCH_COUNT,
        "matched_batch_count": int(preflight.get("matched_batch_count", 0) or 0),
        "matched_batch_ids": list(preflight.get("matched_batch_ids", [])),
        "required_table_count": len(REQUIRED_TABLES),
        "table_work_item_count": len(work_items),
        "table_work_items": work_items,
        "acceptance_criteria": [
            "All five required CSV tables exist with the required headers.",
            "Every submitted row uses data_origin=field and an accepted qa_flag.",
            "Template markers and TODO values are removed before preflight.",
            "At least three shared batch_id values pass lab, hydraulic, oxidant, catalyst and byproduct audits.",
            "Passing this work order only routes the package to Agent53 field calibration; it does not prove the mechanism.",
        ],
        "blocking_reasons": list(preflight.get("blocking_reasons", [])),
        "repair_required": not bool(preflight.get("package_preflight_pass", False)),
        "field_package_ready_for_agent53": bool(
            field_calibration_summary.get("can_run_agent53_field_calibration", False)
        ),
        "agent53_field_candidate_ready": bool(
            field_calibration_summary.get("agent53_field_candidate_ready", False)
        ),
        "next_operator_action": next_operator_action,
        "can_generate_field_evidence": False,
        "can_resume_model_chain": False,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
        "can_emit_field_supported_claim": False,
        "boundary_statement": (
            "This work order only guides external field package collection for grey-box "
            "calibration. It cannot resume the model chain, cannot generate field evidence, "
            "cannot prove mechanism validity and cannot authorize actuator or release-gate writes."
        ),
    }


def grey_box_calibration_collection_work_order_report_md(
    work_order: dict[str, Any],
) -> str:
    lines = [
        "# Grey-Box Calibration Collection Work Order",
        "",
        "## Role",
        "",
        (
            "This work order turns the next external package action into a table-level "
            "collection checklist for `GREY_BOX_CALIBRATION_PACKAGE_DIR`."
        ),
        "",
        "## Work Order State",
        "",
        f"- work_order_id: `{work_order['work_order_id']}`",
        f"- work_order_status: `{work_order['work_order_status']}`",
        f"- source_env_var: `{work_order['source_env_var']}`",
        f"- source_path: `{work_order['source_path']}`",
        f"- template_dir: `{work_order['template_dir']}`",
        f"- validation_command: `{work_order['validation_command']}`",
        f"- minimum_matched_batch_count: `{work_order['minimum_matched_batch_count']}`",
        f"- matched_batch_count: `{work_order['matched_batch_count']}`",
        f"- field_package_ready_for_agent53: `{work_order['field_package_ready_for_agent53']}`",
        f"- agent53_field_candidate_ready: `{work_order['agent53_field_candidate_ready']}`",
        f"- next_operator_action: `{work_order['next_operator_action']}`",
        f"- can_generate_field_evidence: `{work_order['can_generate_field_evidence']}`",
        f"- can_resume_model_chain: `{work_order['can_resume_model_chain']}`",
        f"- can_write_to_actuator: `{work_order['can_write_to_actuator']}`",
        f"- can_write_to_release_gate: `{work_order['can_write_to_release_gate']}`",
        "",
        "## Table Work Items",
        "",
        (
            "| table | status | template csv | required columns | valid rows | "
            "template markers | non-field rows |"
        ),
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for item in work_order["table_work_items"]:
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` |".format(
                item["table_name"],
                item["current_status"],
                item["template_csv"],
                ", ".join(item["required_columns"]),
                item["valid_row_count"],
                item["template_marker_count"],
                item["non_field_row_count"],
            )
        )
    lines.extend(["", "## Acceptance Criteria", ""])
    for criterion in work_order["acceptance_criteria"]:
        lines.append(f"- {criterion}")
    lines.extend(["", "## Boundary", "", work_order["boundary_statement"], ""])
    return "\n".join(lines)


def build_grey_box_submission_readiness_gate(
    *,
    preflight: dict[str, Any],
    field_calibration_summary: dict[str, Any],
    collection_work_order: dict[str, Any],
) -> dict[str, Any]:
    """Score whether the external package can be submitted downstream without field overclaiming."""

    component_scores = _submission_component_scores(
        preflight=preflight,
        field_calibration_summary=field_calibration_summary,
        collection_work_order=collection_work_order,
    )
    readiness_score = _weighted_submission_readiness_score(component_scores)
    highest_priority_gap = _highest_priority_submission_gap(
        preflight=preflight,
        collection_work_order=collection_work_order,
    )
    gate_status = _submission_gate_status(
        preflight=preflight,
        field_calibration_summary=field_calibration_summary,
    )
    return {
        "gate_id": SUBMISSION_READINESS_GATE_ID,
        "gate_type": "grey_box_external_package_submission_readiness_gate",
        "architecture_layer": "verification_governance_to_state_estimation",
        "enhanced_abilities": [
            "verifiability",
            "engineering_feasibility",
            "explainability",
        ],
        "source_env_var": SOURCE_ENV_VAR,
        "source_path": str(preflight.get("source_path", "")),
        "package_status": str(preflight.get("package_status", "")),
        "summary_status": str(field_calibration_summary.get("summary_status", "")),
        "work_order_status": str(collection_work_order.get("work_order_status", "")),
        "gate_status": gate_status,
        "readiness_score": readiness_score,
        "component_scores": component_scores,
        "minimum_matched_batch_count": MINIMUM_MATCHED_BATCH_COUNT,
        "matched_batch_count": int(preflight.get("matched_batch_count", 0) or 0),
        "computable_batch_count": int(
            field_calibration_summary.get("computable_batch_count", 0) or 0
        ),
        "highest_priority_gap": highest_priority_gap,
        "blocking_reasons": list(preflight.get("blocking_reasons", [])),
        "can_submit_to_agent53_field_calibration": bool(
            field_calibration_summary.get("can_run_agent53_field_calibration", False)
        ),
        "can_submit_to_agent53_field_candidate": bool(
            field_calibration_summary.get("agent53_field_candidate_ready", False)
        ),
        "can_generate_field_evidence": False,
        "can_resume_model_chain": False,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
        "can_emit_field_supported_claim": False,
        "next_operator_action": _submission_next_operator_action(
            gate_status=gate_status,
            preflight=preflight,
            field_calibration_summary=field_calibration_summary,
            highest_priority_gap=highest_priority_gap,
        ),
        "failure_boundary": (
            "This gate scores package submission readiness only. It can route a package "
            "to Agent53 field calibration when inputs are complete, but it cannot generate "
            "field evidence, prove mechanism validity, authorize actuator writes, authorize "
            "release-gate writes or emit field-supported claims."
        ),
        "no_write_boundary": _no_write_boundary(),
    }


def grey_box_submission_readiness_gate_report_md(gate: dict[str, Any]) -> str:
    lines = [
        "# Grey-Box Submission Readiness Gate",
        "",
        "## Role",
        "",
        (
            "This gate converts the grey-box calibration package preflight, field "
            "calibration summary and collection work order into one submission-readiness "
            "score for `GREY_BOX_CALIBRATION_PACKAGE_DIR`."
        ),
        "",
        "## State",
        "",
        f"- gate_id: `{gate['gate_id']}`",
        f"- gate_status: `{gate['gate_status']}`",
        f"- readiness_score: `{gate['readiness_score']}`",
        f"- source_env_var: `{gate['source_env_var']}`",
        f"- matched_batch_count: `{gate['matched_batch_count']}`",
        f"- computable_batch_count: `{gate['computable_batch_count']}`",
        f"- can_submit_to_agent53_field_calibration: `{gate['can_submit_to_agent53_field_calibration']}`",
        f"- can_submit_to_agent53_field_candidate: `{gate['can_submit_to_agent53_field_candidate']}`",
        f"- next_operator_action: `{gate['next_operator_action']}`",
        "",
        "## Component Scores",
        "",
        "| component | score |",
        "| --- | --- |",
    ]
    for key, value in gate["component_scores"].items():
        lines.append(f"| `{key}` | `{value}` |")
    lines.extend(
        [
            "",
            "## Highest Priority Gap",
            "",
            f"- gap_type: `{gate['highest_priority_gap']['gap_type']}`",
            f"- table: `{gate['highest_priority_gap']['table']}`",
            f"- missing_table_count: `{gate['highest_priority_gap'].get('missing_table_count', 0)}`",
            "- missing_tables: `{}`".format(
                gate["highest_priority_gap"].get("missing_tables", [])
            ),
            f"- next_action: `{gate['highest_priority_gap']['next_action']}`",
            "",
            "## Boundary",
            "",
            gate["failure_boundary"],
            "",
            gate["no_write_boundary"],
            "",
        ]
    )
    return "\n".join(lines)


def _submission_component_scores(
    *,
    preflight: dict[str, Any],
    field_calibration_summary: dict[str, Any],
    collection_work_order: dict[str, Any],
) -> dict[str, float]:
    table_items = list(collection_work_order.get("table_work_items", []))
    table_count = max(1, len(REQUIRED_TABLES))
    existing_tables = sum(
        1
        for item in table_items
        if item.get("current_status") != "repair_missing_table_or_columns"
        and int(item.get("row_count", 0) or 0) > 0
    )
    schema_ready_tables = sum(
        1
        for item in table_items
        if not item.get("missing_columns")
        and item.get("current_status") != "repair_missing_table_or_columns"
    )
    clean_origin_tables = sum(
        1
        for item in table_items
        if int(item.get("template_marker_count", 0) or 0) == 0
        and int(item.get("non_field_row_count", 0) or 0) == 0
        and int(item.get("valid_row_count", 0) or 0) >= MINIMUM_MATCHED_BATCH_COUNT
    )
    signal_coverage = _mean(
        [
            min(
                1.0,
                int(item.get("valid_row_count", 0) or 0) / MINIMUM_MATCHED_BATCH_COUNT,
            )
            for item in table_items
        ]
    )
    return {
        "source_package_present": float(bool(preflight.get("external_package_supplied", False))),
        "schema_completeness": round(schema_ready_tables / table_count, 3),
        "field_origin_integrity": round(clean_origin_tables / table_count, 3),
        "matched_batch_coverage": round(
            min(1.0, int(preflight.get("matched_batch_count", 0) or 0) / MINIMUM_MATCHED_BATCH_COUNT),
            3,
        ),
        "signal_validity_coverage": signal_coverage,
        "agent53_summary_readiness": float(
            bool(field_calibration_summary.get("can_run_agent53_field_calibration", False))
        ),
        "residual_threshold_readiness": _residual_threshold_readiness(field_calibration_summary),
        "no_write_boundary_integrity": float(
            not preflight.get("can_write_to_actuator", True)
            and not preflight.get("can_write_to_release_gate", True)
            and not field_calibration_summary.get("can_write_to_actuator", True)
            and not field_calibration_summary.get("can_write_to_release_gate", True)
            and not collection_work_order.get("can_write_to_actuator", True)
            and not collection_work_order.get("can_write_to_release_gate", True)
        ),
        "submitted_table_presence": round(existing_tables / table_count, 3),
    }


def _weighted_submission_readiness_score(component_scores: dict[str, float]) -> float:
    weights = {
        "source_package_present": 0.117,
        "schema_completeness": 0.12,
        "field_origin_integrity": 0.14,
        "matched_batch_coverage": 0.14,
        "signal_validity_coverage": 0.12,
        "agent53_summary_readiness": 0.12,
        "residual_threshold_readiness": 0.10,
        "no_write_boundary_integrity": 0.143,
    }
    return round(sum(component_scores[key] * weight for key, weight in weights.items()), 3)


def _residual_threshold_readiness(field_calibration_summary: dict[str, Any]) -> float:
    if bool(field_calibration_summary.get("agent53_field_candidate_ready", False)):
        return 1.0
    if bool(field_calibration_summary.get("can_run_agent53_field_calibration", False)):
        return 0.5
    return 0.0


def _highest_priority_submission_gap(
    *,
    preflight: dict[str, Any],
    collection_work_order: dict[str, Any],
) -> dict[str, Any]:
    if not bool(preflight.get("external_package_supplied", False)):
        return {
            "gap_type": "missing_external_package",
            "table": "all_required_tables",
            "missing_table_count": len(REQUIRED_TABLES),
            "missing_tables": list(REQUIRED_TABLES),
            "source_env_var": SOURCE_ENV_VAR,
            "next_action": str(preflight.get("next_operator_action", "")),
        }
    for item in collection_work_order.get("table_work_items", []):
        if item.get("current_status") == "repair_missing_table_or_columns":
            return {
                "gap_type": "repair_missing_table_or_columns",
                "table": item["table_name"],
                "next_action": f"repair_schema_for_{item['table_name']}",
            }
    for item in collection_work_order.get("table_work_items", []):
        if int(item.get("template_marker_count", 0) or 0) or int(
            item.get("non_field_row_count", 0) or 0
        ):
            return {
                "gap_type": "replace_template_or_non_field_rows",
                "table": item["table_name"],
                "next_action": f"replace_template_rows_with_real_field_rows_for_{item['table_name']}",
            }
    for item in collection_work_order.get("table_work_items", []):
        if int(item.get("valid_row_count", 0) or 0) < MINIMUM_MATCHED_BATCH_COUNT:
            return {
                "gap_type": "add_valid_qa_passed_field_rows",
                "table": item["table_name"],
                "next_action": f"add_qa_passed_field_rows_for_{item['table_name']}",
            }
    if not bool(preflight.get("package_preflight_pass", False)):
        return {
            "gap_type": "matched_batch_alignment_or_signal_audit",
            "table": "",
            "next_action": str(preflight.get("next_operator_action", "")),
        }
    return {
        "gap_type": "none",
        "table": "",
        "next_action": "run_agent53_field_calibration_with_no_write_boundaries",
    }


def _submission_gate_status(
    *,
    preflight: dict[str, Any],
    field_calibration_summary: dict[str, Any],
) -> str:
    if bool(field_calibration_summary.get("agent53_field_candidate_ready", False)):
        return "grey_box_submission_readiness_ready_for_agent53_field_candidate"
    if bool(field_calibration_summary.get("can_run_agent53_field_calibration", False)):
        return "grey_box_submission_readiness_ready_for_agent53_calibration_with_residual_review"
    if not bool(preflight.get("external_package_supplied", False)):
        return "grey_box_submission_readiness_waiting_for_external_package"
    return "grey_box_submission_readiness_blocked_by_package_preflight"


def _submission_next_operator_action(
    *,
    gate_status: str,
    preflight: dict[str, Any],
    field_calibration_summary: dict[str, Any],
    highest_priority_gap: dict[str, Any],
) -> str:
    if gate_status in {
        "grey_box_submission_readiness_ready_for_agent53_field_candidate",
        "grey_box_submission_readiness_ready_for_agent53_calibration_with_residual_review",
    }:
        return str(field_calibration_summary.get("next_operator_action", ""))
    if highest_priority_gap["gap_type"] != "none":
        return str(highest_priority_gap["next_action"])
    return str(preflight.get("next_operator_action", ""))


def _collection_table_work_item(
    *,
    table_name: str,
    template_dir: str,
    table_audit: dict[str, Any],
    signal_audit: dict[str, Any],
    external_package_supplied: bool,
) -> dict[str, Any]:
    template_csv = str(Path(template_dir) / f"{table_name}.csv") if template_dir else f"{table_name}.csv"
    template_marker_count = int(table_audit.get("template_marker_count", 0) or 0)
    non_field_row_count = int(table_audit.get("non_field_row_count", 0) or 0)
    missing_columns = list(table_audit.get("missing_columns", TABLE_COLUMNS[table_name]))
    valid_row_count = int(signal_audit.get("valid_row_count", 0) or 0)
    return {
        "table_name": table_name,
        "template_csv": template_csv,
        "join_key": "batch_id",
        "minimum_rows": MINIMUM_MATCHED_BATCH_COUNT,
        "required_data_origin": "field",
        "accepted_qa_flags": sorted(ACCEPTED_QA_FLAGS),
        "required_columns": TABLE_COLUMNS[table_name],
        "row_count": int(table_audit.get("row_count", 0) or 0),
        "valid_row_count": valid_row_count,
        "valid_batch_ids": list(signal_audit.get("valid_batch_ids", [])),
        "missing_columns": missing_columns,
        "template_marker_count": template_marker_count,
        "non_field_row_count": non_field_row_count,
        "current_status": _collection_table_status(
            external_package_supplied=external_package_supplied,
            file_exists=bool(table_audit.get("file_exists", False)),
            missing_columns=missing_columns,
            template_marker_count=template_marker_count,
            non_field_row_count=non_field_row_count,
            valid_row_count=valid_row_count,
        ),
    }


def _collection_table_status(
    *,
    external_package_supplied: bool,
    file_exists: bool,
    missing_columns: list[str],
    template_marker_count: int,
    non_field_row_count: int,
    valid_row_count: int,
) -> str:
    if not external_package_supplied:
        return "needs_real_field_rows"
    if not file_exists or missing_columns:
        return "repair_missing_table_or_columns"
    if template_marker_count or non_field_row_count:
        return "replace_template_rows_with_field_rows"
    if valid_row_count < MINIMUM_MATCHED_BATCH_COUNT:
        return "add_valid_qa_passed_field_rows"
    return "table_ready_for_calibration_preflight"


def _signal_audit_for_table(table_name: str, preflight: dict[str, Any]) -> dict[str, Any]:
    audit_key_by_table = {
        BATCH_LAB_TABLE: "lab_pair_audit",
        HYDRAULIC_TABLE: "hydraulic_audit",
        OXIDANT_TABLE: "oxidant_audit",
        CATALYST_TABLE: "catalyst_audit",
        BYPRODUCT_TABLE: "byproduct_audit",
    }
    return preflight.get(audit_key_by_table[table_name], _empty_signal_audit(table_name))


def _collection_work_order_status(
    *,
    preflight: dict[str, Any],
    field_calibration_summary: dict[str, Any],
) -> str:
    if bool(field_calibration_summary.get("can_run_agent53_field_calibration", False)):
        return "grey_box_calibration_collection_work_order_ready_for_agent53_field_calibration"
    if not bool(preflight.get("external_package_supplied", False)):
        return "grey_box_calibration_collection_work_order_waiting_for_external_package"
    return "grey_box_calibration_collection_work_order_blocked_by_preflight_repair"


def _collection_next_operator_action(
    *,
    work_order_status: str,
    preflight: dict[str, Any],
    field_calibration_summary: dict[str, Any],
) -> str:
    if work_order_status == (
        "grey_box_calibration_collection_work_order_ready_for_agent53_field_calibration"
    ):
        return str(field_calibration_summary.get("next_operator_action", ""))
    return str(preflight.get("next_operator_action", ""))


def _preflight_payload(
    *,
    source_path: str,
    external_package_supplied: bool,
    package_status: str,
    table_audits: dict[str, dict[str, Any]],
    lab_audit: dict[str, Any],
    hydraulic_audit: dict[str, Any],
    oxidant_audit: dict[str, Any],
    catalyst_audit: dict[str, Any],
    byproduct_audit: dict[str, Any],
    matched_batch_ids: list[str],
    blocking_reasons: list[str],
) -> dict[str, Any]:
    preflight_pass = external_package_supplied and not blocking_reasons
    coverage = round(min(1.0, len(matched_batch_ids) / MINIMUM_MATCHED_BATCH_COUNT), 3)
    return {
        "package_id": PACKAGE_ID,
        "package_type": "grey_box_calibration_package_preflight",
        "source_env_var": SOURCE_ENV_VAR,
        "source_path": source_path,
        "external_package_supplied": external_package_supplied,
        "package_status": package_status,
        "package_preflight_pass": preflight_pass,
        "required_table_count": len(REQUIRED_TABLES),
        "required_tables": list(REQUIRED_TABLES),
        "minimum_matched_batch_count": MINIMUM_MATCHED_BATCH_COUNT,
        "matched_batch_count": len(matched_batch_ids),
        "matched_batch_ids": matched_batch_ids,
        "field_physics_coverage_candidate": coverage,
        "table_audits": table_audits,
        "lab_pair_audit": lab_audit,
        "hydraulic_audit": hydraulic_audit,
        "oxidant_audit": oxidant_audit,
        "catalyst_audit": catalyst_audit,
        "byproduct_audit": byproduct_audit,
        "blocking_reasons": blocking_reasons,
        "can_route_to_agent53_field_calibration": preflight_pass,
        "can_generate_field_evidence": False,
        "can_resume_model_chain": False,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
        "next_operator_action": _next_operator_action(package_status),
        "field_boundary": (
            "This preflight only checks whether a grey-box calibration package is structurally "
            "ready for Agent53 field calibration. Passing this gate does not prove mechanism "
            "validity, field-supported claims, actuator readiness or release readiness."
        ),
        "no_write_boundary": _no_write_boundary(),
    }


def _field_calibration_summary_payload(
    *,
    source_path: str,
    package_preflight_status: str,
    package_preflight_pass: bool,
    matched_batch_ids: list[str],
    batch_calibration_rows: list[dict[str, Any]],
    max_field_residual: float,
    max_mass_balance_residual: float,
    summary_status: str,
    blocking_reasons: list[str],
) -> dict[str, Any]:
    computable_rows = [
        row
        for row in batch_calibration_rows
        if row.get("usable_for_agent53_field_calibration") and "field_residual_proxy" in row
    ]
    coverage = round(min(1.0, len(computable_rows) / MINIMUM_MATCHED_BATCH_COUNT), 3)
    residuals = [float(row["field_residual_proxy"]) for row in computable_rows]
    mass_residuals = [float(row["mass_balance_residual_proxy"]) for row in computable_rows]
    k_values = [float(row["observed_k_per_min"]) for row in computable_rows]
    removal_values = [float(row["observed_removal_fraction"]) for row in computable_rows]
    byproduct_fractions = [float(row["byproduct_load_fraction_proxy"]) for row in computable_rows]
    max_observed_field_residual = round(max(residuals) if residuals else 1.0, 3)
    max_observed_mass_residual = round(max(mass_residuals) if mass_residuals else 1.0, 3)
    can_run_agent53 = package_preflight_pass and coverage >= 1.0 and not blocking_reasons
    agent53_field_candidate_ready = (
        can_run_agent53
        and max_observed_field_residual <= max_field_residual
        and max_observed_mass_residual <= max_mass_balance_residual
    )
    if not summary_status:
        summary_status = (
            "grey_box_field_calibration_summary_ready_for_agent53_field_candidate"
            if agent53_field_candidate_ready
            else "grey_box_field_calibration_summary_ready_with_residual_blockers"
        )
    field_calibration_for_agent53 = {
        "field_physics_coverage": coverage,
        "max_field_residual": max_observed_field_residual,
        "max_mass_balance_residual": max_observed_mass_residual,
        "mean_observed_k_per_min": _mean(k_values),
        "mean_observed_removal_fraction": _mean(removal_values),
        "max_byproduct_load_fraction_proxy": round(
            max(byproduct_fractions) if byproduct_fractions else 1.0,
            3,
        ),
    }
    return {
        "summary_id": FIELD_CALIBRATION_SUMMARY_ID,
        "summary_type": "grey_box_field_calibration_summary_for_agent53",
        "summary_status": summary_status,
        "source_env_var": SOURCE_ENV_VAR,
        "source_path": source_path,
        "package_preflight_status": package_preflight_status,
        "package_preflight_pass": package_preflight_pass,
        "matched_batch_count": len(matched_batch_ids),
        "computable_batch_count": len(computable_rows),
        "matched_batch_ids": matched_batch_ids,
        "agent53_thresholds": {
            "max_field_residual": max_field_residual,
            "max_mass_balance_residual": max_mass_balance_residual,
            "minimum_field_physics_coverage": 0.85,
        },
        "field_calibration_for_agent53": field_calibration_for_agent53,
        "batch_calibration_rows": batch_calibration_rows,
        "blocking_reasons": blocking_reasons,
        "can_run_agent53_field_calibration": can_run_agent53,
        "agent53_field_candidate_ready": agent53_field_candidate_ready,
        "can_generate_field_evidence": False,
        "can_resume_model_chain": False,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
        "next_operator_action": _field_calibration_next_action(
            summary_status=summary_status,
            can_run_agent53=can_run_agent53,
            agent53_field_candidate_ready=agent53_field_candidate_ready,
        ),
        "field_boundary": (
            "This summary converts a structurally accepted external field package into "
            "Agent53-compatible calibration inputs. It can support a downstream field "
            "calibration run, but it does not by itself prove a mechanism, authorize "
            "control actions or upgrade release decisions."
        ),
        "no_write_boundary": _no_write_boundary(),
    }


def _batch_field_calibration_row(
    *,
    batch_id: str,
    lab_row: dict[str, str],
    hydraulic_row: dict[str, str],
    byproduct_value: float,
) -> dict[str, Any]:
    inlet = _float(lab_row.get("inlet_concentration"))
    outlet = _float(lab_row.get("outlet_concentration"))
    hrt = _float(hydraulic_row.get("effective_HRT_min"))
    if inlet is None or outlet is None or hrt is None or inlet <= 0 or outlet < 0 or hrt <= 0:
        return {
            "batch_id": batch_id,
            "usable_for_agent53_field_calibration": False,
            "blocking_reason": "missing_or_invalid_inlet_outlet_or_effective_HRT",
        }
    remaining_fraction = max(0.0, outlet / inlet)
    observed_removal = max(-1.0, min(1.0, (inlet - outlet) / inlet))
    observed_k = 0.0
    if 0 <= outlet < inlet:
        observed_k = -math.log(max(outlet / inlet, 1e-6)) / hrt
    converted_load_proxy = max(0.0, inlet - outlet)
    mass_balance_residual = abs(inlet - outlet - converted_load_proxy - byproduct_value) / max(inlet, 1e-6)
    return {
        "batch_id": batch_id,
        "target_pollutant": str(lab_row.get("target_pollutant", "")),
        "inlet_concentration": round(inlet, 6),
        "outlet_concentration": round(outlet, 6),
        "effective_HRT_min": round(hrt, 6),
        "field_residual_proxy": round(remaining_fraction, 3),
        "observed_removal_fraction": round(observed_removal, 3),
        "observed_k_per_min": round(observed_k, 5),
        "converted_load_proxy": round(converted_load_proxy, 6),
        "byproduct_load_proxy": round(byproduct_value, 6),
        "byproduct_load_fraction_proxy": round(byproduct_value / max(inlet, 1e-6), 3),
        "mass_balance_residual_proxy": round(min(1.0, mass_balance_residual), 3),
        "usable_for_agent53_field_calibration": True,
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


def _lab_pair_audit(rows: list[dict[str, str]]) -> dict[str, Any]:
    valid_ids = []
    removal_fractions = []
    for row in rows:
        if not _row_common_valid(row):
            continue
        inlet = _float(row.get("inlet_concentration"))
        outlet = _float(row.get("outlet_concentration"))
        if inlet is None or outlet is None or inlet <= 0 or outlet < 0:
            continue
        valid_ids.append(str(row.get("batch_id", "")))
        removal_fractions.append(max(-1.0, min(1.0, (inlet - outlet) / inlet)))
    return {
        "signal_family": "lab_pair",
        "row_count": len(rows),
        "valid_row_count": len(valid_ids),
        "valid_batch_ids": sorted(set(valid_ids)),
        "mean_observed_removal_fraction": (
            round(sum(removal_fractions) / len(removal_fractions), 3)
            if removal_fractions
            else None
        ),
    }


def _hydraulic_audit(rows: list[dict[str, str]]) -> dict[str, Any]:
    valid_ids = []
    hrt_values = []
    for row in rows:
        if not _row_common_valid(row):
            continue
        effective_hrt = _float(row.get("effective_HRT_min"))
        nominal_hrt = _float(row.get("nominal_HRT_min"))
        flow = _float(row.get("flow_Lmin"))
        volume = _float(row.get("volume_L"))
        if any(value is None for value in [effective_hrt, nominal_hrt, flow, volume]):
            continue
        if min(effective_hrt or 0, nominal_hrt or 0, flow or 0, volume or 0) <= 0:
            continue
        valid_ids.append(str(row.get("batch_id", "")))
        hrt_values.append(float(effective_hrt))
    return {
        "signal_family": "hydraulic_rtd",
        "row_count": len(rows),
        "valid_row_count": len(valid_ids),
        "valid_batch_ids": sorted(set(valid_ids)),
        "mean_effective_HRT_min": (
            round(sum(hrt_values) / len(hrt_values), 3) if hrt_values else None
        ),
    }


def _oxidant_audit(rows: list[dict[str, str]]) -> dict[str, Any]:
    valid_ids = []
    for row in rows:
        if not _row_common_valid(row):
            continue
        dose = _float(row.get("dose_mg_L"))
        residual = _float(row.get("residual_mg_L"))
        energy = _float(row.get("energy_kWh_m3"))
        if any(value is None for value in [dose, residual, energy]):
            continue
        if min(dose or 0, residual or 0, energy or 0) < 0:
            continue
        valid_ids.append(str(row.get("batch_id", "")))
    return {
        "signal_family": "oxidant_dose_residual",
        "row_count": len(rows),
        "valid_row_count": len(valid_ids),
        "valid_batch_ids": sorted(set(valid_ids)),
    }


def _catalyst_audit(rows: list[dict[str, str]]) -> dict[str, Any]:
    valid_ids = []
    regen_count = 0
    for row in rows:
        if not _row_common_valid(row):
            continue
        age = _float(row.get("catalyst_age_h"))
        activity = _float(row.get("catalyst_activity_label"))
        regeneration_count = _float(row.get("regeneration_count"))
        if any(value is None for value in [age, activity, regeneration_count]):
            continue
        if age < 0 or not 0 <= activity <= 1 or regeneration_count < 0:
            continue
        valid_ids.append(str(row.get("batch_id", "")))
        if _normalize(row.get("regeneration_event")) not in {"", "none", "no", "false", "0"}:
            regen_count += 1
    return {
        "signal_family": "catalyst_history",
        "row_count": len(rows),
        "valid_row_count": len(valid_ids),
        "valid_batch_ids": sorted(set(valid_ids)),
        "regeneration_event_row_count": regen_count,
    }


def _byproduct_audit(rows: list[dict[str, str]]) -> dict[str, Any]:
    valid_ids = []
    analytes = set()
    for row in rows:
        if not _row_common_valid(row):
            continue
        value = _float(row.get("value"))
        detection_limit = _float(row.get("detection_limit"))
        if value is None or detection_limit is None or value < 0 or detection_limit < 0:
            continue
        if not str(row.get("analyte", "")).strip() or not str(row.get("method", "")).strip():
            continue
        valid_ids.append(str(row.get("batch_id", "")))
        analytes.add(str(row.get("analyte", "")).strip())
    return {
        "signal_family": "byproduct_panel",
        "row_count": len(rows),
        "valid_row_count": len(valid_ids),
        "valid_batch_ids": sorted(set(valid_ids)),
        "analyte_count": len(analytes),
        "analytes": sorted(analytes),
    }


def _blocking_reasons(
    *,
    missing_tables: list[str],
    header_gaps: list[dict[str, Any]],
    template_marker_count: int,
    non_field_row_count: int,
    lab_audit: dict[str, Any],
    hydraulic_audit: dict[str, Any],
    oxidant_audit: dict[str, Any],
    catalyst_audit: dict[str, Any],
    byproduct_audit: dict[str, Any],
    matched_batch_ids: list[str],
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
        ("insufficient_lab_pairs", lab_audit),
        ("insufficient_hydraulic_rtd_rows", hydraulic_audit),
        ("insufficient_oxidant_rows", oxidant_audit),
        ("insufficient_catalyst_history_rows", catalyst_audit),
        ("insufficient_byproduct_panel_rows", byproduct_audit),
    ]
    for reason, audit in signal_requirements:
        if int(audit.get("valid_row_count", 0) or 0) < MINIMUM_MATCHED_BATCH_COUNT:
            reasons.append(reason)
    if len(matched_batch_ids) < MINIMUM_MATCHED_BATCH_COUNT:
        reasons.append("matched_batch_deficit")
    return reasons


def _package_status(blocking_reasons: list[str]) -> str:
    if not blocking_reasons:
        return "grey_box_calibration_package_ready_for_agent53_field_calibration"
    if "missing_required_tables" in blocking_reasons or "missing_required_columns" in blocking_reasons:
        return "grey_box_calibration_package_blocked_at_schema"
    if "template_markers_present" in blocking_reasons or "non_field_rows_present" in blocking_reasons:
        return "grey_box_calibration_package_blocked_at_field_origin"
    if "matched_batch_deficit" in blocking_reasons:
        return "grey_box_calibration_package_blocked_at_batch_alignment"
    return "grey_box_calibration_package_blocked_at_content_preflight"


def _next_operator_action(package_status: str) -> str:
    if package_status == "grey_box_calibration_package_ready_for_agent53_field_calibration":
        return "route_GREY_BOX_CALIBRATION_PACKAGE_DIR_to_Agent53_field_calibration_preflight_consumer"
    if package_status == "grey_box_calibration_package_blocked_at_missing_source_dir":
        return "repair_GREY_BOX_CALIBRATION_PACKAGE_DIR_path"
    if package_status == "grey_box_calibration_package_blocked_at_schema":
        return "repair_grey_box_calibration_package_csv_headers_and_required_tables"
    if package_status == "grey_box_calibration_package_blocked_at_field_origin":
        return "replace_template_or_non_field_rows_with_real_field_rows"
    if package_status == "grey_box_calibration_package_blocked_at_batch_alignment":
        return "add_at_least_three_shared_batch_ids_across_all_grey_box_calibration_tables"
    return "fill_grey_box_calibration_package_template_and_set_GREY_BOX_CALIBRATION_PACKAGE_DIR"


def _empty_signal_audit(signal_family: str) -> dict[str, Any]:
    return {
        "signal_family": signal_family,
        "row_count": 0,
        "valid_row_count": 0,
        "valid_batch_ids": [],
    }


def _row_common_valid(row: dict[str, str]) -> bool:
    batch_id = str(row.get("batch_id", "")).strip()
    if not batch_id or "TODO" in batch_id:
        return False
    return _normalize(row.get("qa_flag")) in ACCEPTED_QA_FLAGS and _normalize(
        row.get("data_origin")
    ) == "field"


def _first_valid_row_by_batch(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    indexed: dict[str, dict[str, str]] = {}
    for row in rows:
        if not _row_common_valid(row):
            continue
        batch_id = str(row.get("batch_id", "")).strip()
        if batch_id and batch_id not in indexed:
            indexed[batch_id] = row
    return indexed


def _byproduct_sum_by_batch(rows: list[dict[str, str]]) -> dict[str, float]:
    sums: dict[str, float] = {}
    for row in rows:
        if not _row_common_valid(row):
            continue
        value = _float(row.get("value"))
        if value is None or value < 0:
            continue
        batch_id = str(row.get("batch_id", "")).strip()
        if batch_id:
            sums[batch_id] = sums.get(batch_id, 0.0) + value
    return sums


def _field_calibration_next_action(
    *,
    summary_status: str,
    can_run_agent53: bool,
    agent53_field_candidate_ready: bool,
) -> str:
    if agent53_field_candidate_ready:
        return "run_Agent53_with_evidence_stage_field_physics_calibration_and_keep_release_gate_closed"
    if can_run_agent53:
        return "run_Agent53_field_calibration_to_quantify_residual_blockers_before_any_control_relaxation"
    if summary_status == "grey_box_field_calibration_blocked_at_source_reload":
        return "repair_GREY_BOX_CALIBRATION_PACKAGE_DIR_path_before_building_field_calibration_summary"
    if summary_status == "grey_box_field_calibration_blocked_at_computable_batch_summary":
        return "repair_inlet_outlet_HRT_values_until_three_batches_are_computable"
    return "complete_grey_box_calibration_package_preflight_before_building_field_calibration_summary"


def _mean(values: list[float]) -> float:
    if not values:
        return 0.0
    return round(sum(values) / len(values), 5)


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
        "This package is only a grey-box calibration preflight input. It cannot write actuator "
        "policy, release-gate policy, field-supported mechanism claims or deployment clearance."
    )


def _lab_template_row(batch_id: str) -> dict[str, str]:
    return {
        "batch_id": batch_id,
        "sample_time_min": "TODO_sample_time_min",
        "target_pollutant": "TODO_target_pollutant",
        "inlet_concentration": "TODO_inlet_concentration",
        "outlet_concentration": "TODO_outlet_concentration",
        "pollutant_unit": "TODO_unit",
        "matrix_indicator": "TODO_COD_or_NOM_or_salinity",
        "matrix_indicator_unit": "TODO_unit",
        "lab_method": "TODO_method",
        "qa_flag": "TODO_pass",
        "data_origin": "TODO_field",
    }


def _hydraulic_template_row(batch_id: str) -> dict[str, str]:
    return {
        "batch_id": batch_id,
        "measurement_time_min": "TODO_measurement_time_min",
        "unit_id": "TODO_reactor_or_loop_id",
        "effective_HRT_min": "TODO_effective_HRT_min",
        "nominal_HRT_min": "TODO_nominal_HRT_min",
        "rtd_t10_min": "TODO_rtd_t10_min",
        "rtd_t90_min": "TODO_rtd_t90_min",
        "tracer_recovery_fraction": "TODO_tracer_recovery_fraction",
        "flow_Lmin": "TODO_flow_Lmin",
        "volume_L": "TODO_volume_L",
        "qa_flag": "TODO_pass",
        "data_origin": "TODO_field",
    }


def _oxidant_template_row(batch_id: str) -> dict[str, str]:
    return {
        "batch_id": batch_id,
        "timestamp_min": "TODO_timestamp_min",
        "oxidant_name": "TODO_oxidant_name",
        "dose_mg_L": "TODO_dose_mg_L",
        "residual_mg_L": "TODO_residual_mg_L",
        "energy_kWh_m3": "TODO_energy_kWh_m3",
        "qa_flag": "TODO_pass",
        "data_origin": "TODO_field",
    }


def _catalyst_template_row(batch_id: str) -> dict[str, str]:
    return {
        "batch_id": batch_id,
        "timestamp_min": "TODO_timestamp_min",
        "catalyst_id": "TODO_catalyst_id",
        "catalyst_age_h": "TODO_catalyst_age_h",
        "catalyst_activity_label": "TODO_0_to_1",
        "regeneration_event": "TODO_none_or_regenerated",
        "regeneration_count": "TODO_regeneration_count",
        "qa_flag": "TODO_pass",
        "data_origin": "TODO_field",
    }


def _byproduct_template_row(batch_id: str) -> dict[str, str]:
    return {
        "batch_id": batch_id,
        "sample_time_min": "TODO_sample_time_min",
        "analyte": "TODO_byproduct_analyte",
        "value": "TODO_value",
        "unit": "TODO_unit",
        "detection_limit": "TODO_detection_limit",
        "method": "TODO_method",
        "qa_flag": "TODO_pass",
        "data_origin": "TODO_field",
    }

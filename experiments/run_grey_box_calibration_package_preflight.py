from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from water_ai.grey_box_calibration_package import (
    SOURCE_ENV_VAR,
    build_grey_box_calibration_collection_work_order,
    build_grey_box_calibration_package_preflight,
    build_grey_box_field_calibration_summary,
    build_grey_box_submission_readiness_gate,
    grey_box_calibration_collection_work_order_report_md,
    grey_box_submission_readiness_gate_report_md,
    write_grey_box_calibration_package_template,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = PROJECT_ROOT / "deliverables" / "manifest.json"
OUT_DIR = PROJECT_ROOT / "outputs" / "grey_box_calibration_package"
DELIVERABLES_DIR = PROJECT_ROOT / "deliverables" / "model_core_optimization"
TEMPLATE_DIR = OUT_DIR / "grey_box_calibration_package_template"
PREFLIGHT_PATH = OUT_DIR / "grey_box_calibration_package_preflight.json"
FIELD_CALIBRATION_SUMMARY_PATH = OUT_DIR / "grey_box_field_calibration_summary.json"
COLLECTION_WORK_ORDER_PATH = OUT_DIR / "grey_box_calibration_collection_work_order.json"
SUBMISSION_READINESS_GATE_PATH = OUT_DIR / "grey_box_submission_readiness_gate.json"
REPORT_PATH = DELIVERABLES_DIR / "grey_box_calibration_package_preflight.md"
COLLECTION_WORK_ORDER_REPORT_PATH = (
    DELIVERABLES_DIR / "grey_box_calibration_collection_work_order.md"
)
SUBMISSION_READINESS_GATE_REPORT_PATH = (
    DELIVERABLES_DIR / "grey_box_submission_readiness_gate.md"
)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DELIVERABLES_DIR.mkdir(parents=True, exist_ok=True)
    template = write_grey_box_calibration_package_template(TEMPLATE_DIR)
    source_path = os.environ.get(SOURCE_ENV_VAR, "")
    preflight = build_grey_box_calibration_package_preflight(
        source_dir=source_path,
        external_package_supplied=bool(source_path),
    )
    field_calibration_summary = build_grey_box_field_calibration_summary(
        source_dir=source_path,
        external_package_supplied=bool(source_path),
        preflight=preflight,
    )
    collection_work_order = build_grey_box_calibration_collection_work_order(
        preflight=preflight,
        field_calibration_summary=field_calibration_summary,
        template_dir=str(TEMPLATE_DIR.relative_to(PROJECT_ROOT)),
        validation_command=".venv/bin/python experiments/run_grey_box_calibration_package_preflight.py",
    )
    submission_readiness_gate = build_grey_box_submission_readiness_gate(
        preflight=preflight,
        field_calibration_summary=field_calibration_summary,
        collection_work_order=collection_work_order,
    )
    PREFLIGHT_PATH.write_text(json.dumps(preflight, ensure_ascii=False, indent=2), encoding="utf-8")
    FIELD_CALIBRATION_SUMMARY_PATH.write_text(
        json.dumps(field_calibration_summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    COLLECTION_WORK_ORDER_PATH.write_text(
        json.dumps(collection_work_order, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    SUBMISSION_READINESS_GATE_PATH.write_text(
        json.dumps(submission_readiness_gate, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    REPORT_PATH.write_text(_report_md(preflight, field_calibration_summary, template), encoding="utf-8")
    COLLECTION_WORK_ORDER_REPORT_PATH.write_text(
        grey_box_calibration_collection_work_order_report_md(collection_work_order),
        encoding="utf-8",
    )
    SUBMISSION_READINESS_GATE_REPORT_PATH.write_text(
        grey_box_submission_readiness_gate_report_md(submission_readiness_gate),
        encoding="utf-8",
    )
    _update_manifest(
        preflight,
        field_calibration_summary,
        collection_work_order,
        submission_readiness_gate,
    )

    print(f"Grey-box calibration package preflight: {preflight['package_status']}")
    print(f"- package_preflight_pass: {preflight['package_preflight_pass']}")
    print(f"- matched_batch_count: {preflight['matched_batch_count']}")
    print(f"- field_calibration_summary_status: {field_calibration_summary['summary_status']}")
    print(f"- can_run_agent53_field_calibration: {field_calibration_summary['can_run_agent53_field_calibration']}")
    print(f"- collection_work_order_status: {collection_work_order['work_order_status']}")
    print(f"- submission_readiness_gate_status: {submission_readiness_gate['gate_status']}")
    print(f"- submission_readiness_score: {submission_readiness_gate['readiness_score']}")
    print(f"- next_operator_action: {preflight['next_operator_action']}")
    print(f"preflight: {PREFLIGHT_PATH}")
    print(f"field_calibration_summary: {FIELD_CALIBRATION_SUMMARY_PATH}")
    print(f"collection_work_order: {COLLECTION_WORK_ORDER_PATH}")
    print(f"submission_readiness_gate: {SUBMISSION_READINESS_GATE_PATH}")
    print(f"report: {REPORT_PATH}")
    print(f"collection_work_order_report: {COLLECTION_WORK_ORDER_REPORT_PATH}")
    print(f"submission_readiness_gate_report: {SUBMISSION_READINESS_GATE_REPORT_PATH}")


def _report_md(
    preflight: dict[str, Any],
    field_calibration_summary: dict[str, Any],
    template: dict[str, Any],
) -> str:
    lines = [
        "# Grey-Box Calibration Package Preflight",
        "",
        "## Role",
        "",
        (
            "This preflight checks whether an external `GREY_BOX_CALIBRATION_PACKAGE_DIR` "
            "can be routed to Agent53 field calibration. It is not a field-validation result."
        ),
        "",
        "## Status",
        "",
        f"- package_status: `{preflight['package_status']}`",
        f"- source_env_var: `{preflight['source_env_var']}`",
        f"- source_path: `{preflight['source_path']}`",
        f"- package_preflight_pass: `{preflight['package_preflight_pass']}`",
        f"- matched_batch_count: `{preflight['matched_batch_count']}`",
        f"- minimum_matched_batch_count: `{preflight['minimum_matched_batch_count']}`",
        f"- field_physics_coverage_candidate: `{preflight['field_physics_coverage_candidate']}`",
        f"- can_route_to_agent53_field_calibration: `{preflight['can_route_to_agent53_field_calibration']}`",
        f"- can_generate_field_evidence: `{preflight['can_generate_field_evidence']}`",
        f"- can_write_to_actuator: `{preflight['can_write_to_actuator']}`",
        f"- can_write_to_release_gate: `{preflight['can_write_to_release_gate']}`",
        f"- next_operator_action: `{preflight['next_operator_action']}`",
        "",
        "## Agent53 Field Calibration Summary",
        "",
        f"- summary_status: `{field_calibration_summary['summary_status']}`",
        f"- computable_batch_count: `{field_calibration_summary['computable_batch_count']}`",
        (
            "- can_run_agent53_field_calibration: "
            f"`{field_calibration_summary['can_run_agent53_field_calibration']}`"
        ),
        f"- agent53_field_candidate_ready: `{field_calibration_summary['agent53_field_candidate_ready']}`",
        (
            "- field_calibration_for_agent53: "
            f"`{field_calibration_summary['field_calibration_for_agent53']}`"
        ),
        f"- summary_next_operator_action: `{field_calibration_summary['next_operator_action']}`",
        "",
        "## Required Tables",
        "",
        "| table | rows | missing columns | template markers | non-field rows |",
        "| --- | --- | --- | --- | --- |",
    ]
    audits = preflight["table_audits"]
    for table in preflight["required_tables"]:
        audit = audits.get(table, {})
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` |".format(
                table,
                audit.get("row_count", 0),
                audit.get("missing_columns", []),
                audit.get("template_marker_count", 0),
                audit.get("non_field_row_count", 0),
            )
        )
    lines.extend(
        [
            "",
            "## Signal Audits",
            "",
            "| signal | valid rows | valid batch ids |",
            "| --- | --- | --- |",
        ]
    )
    for key in [
        "lab_pair_audit",
        "hydraulic_audit",
        "oxidant_audit",
        "catalyst_audit",
        "byproduct_audit",
    ]:
        audit = preflight[key]
        lines.append(
            f"| `{audit['signal_family']}` | `{audit['valid_row_count']}` | `{audit['valid_batch_ids']}` |"
        )
    lines.extend(["", "## Blocking Reasons", ""])
    if preflight["blocking_reasons"]:
        for reason in preflight["blocking_reasons"]:
            lines.append(f"- `{reason}`")
    else:
        lines.append("- None.")
    lines.extend(
        [
            "",
            "## Template Location",
            "",
            f"- template_dir: `{TEMPLATE_DIR.relative_to(PROJECT_ROOT)}`",
            f"- required_table_count: `{template['required_table_count']}`",
            "",
            "## Boundary",
            "",
            preflight["field_boundary"],
            "",
            preflight["no_write_boundary"],
            "",
        ]
    )
    return "\n".join(lines)


def _update_manifest(
    preflight: dict[str, Any],
    field_calibration_summary: dict[str, Any],
    collection_work_order: dict[str, Any],
    submission_readiness_gate: dict[str, Any],
) -> None:
    manifest = _read_json(MANIFEST_PATH)
    manifest["latest_grey_box_calibration_package_preflight"] = str(
        PREFLIGHT_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_grey_box_calibration_package_preflight_report"] = str(
        REPORT_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_grey_box_field_calibration_summary"] = str(
        FIELD_CALIBRATION_SUMMARY_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_grey_box_calibration_collection_work_order"] = str(
        COLLECTION_WORK_ORDER_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_grey_box_calibration_collection_work_order_report"] = str(
        COLLECTION_WORK_ORDER_REPORT_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_grey_box_submission_readiness_gate"] = str(
        SUBMISSION_READINESS_GATE_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_grey_box_submission_readiness_gate_report"] = str(
        SUBMISSION_READINESS_GATE_REPORT_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_grey_box_calibration_package_template_dir"] = str(
        TEMPLATE_DIR.relative_to(PROJECT_ROOT)
    )
    manifest["latest_grey_box_calibration_package_status"] = preflight["package_status"]
    manifest["latest_grey_box_calibration_package_preflight_pass"] = preflight[
        "package_preflight_pass"
    ]
    manifest["latest_grey_box_calibration_package_matched_batch_count"] = preflight[
        "matched_batch_count"
    ]
    manifest["latest_grey_box_calibration_package_can_route_to_agent53_field_calibration"] = (
        preflight["can_route_to_agent53_field_calibration"]
    )
    manifest["latest_grey_box_calibration_package_can_generate_field_evidence"] = preflight[
        "can_generate_field_evidence"
    ]
    manifest["latest_grey_box_calibration_package_can_write_to_actuator"] = preflight[
        "can_write_to_actuator"
    ]
    manifest["latest_grey_box_calibration_package_can_write_to_release_gate"] = preflight[
        "can_write_to_release_gate"
    ]
    manifest["latest_grey_box_calibration_package_next_operator_action"] = preflight[
        "next_operator_action"
    ]
    manifest["latest_grey_box_field_calibration_status"] = field_calibration_summary[
        "summary_status"
    ]
    manifest["latest_grey_box_field_calibration_can_run_agent53_field_calibration"] = (
        field_calibration_summary["can_run_agent53_field_calibration"]
    )
    manifest["latest_grey_box_field_calibration_agent53_field_candidate_ready"] = (
        field_calibration_summary["agent53_field_candidate_ready"]
    )
    manifest["latest_grey_box_field_calibration_can_generate_field_evidence"] = (
        field_calibration_summary["can_generate_field_evidence"]
    )
    manifest["latest_grey_box_field_calibration_can_write_to_actuator"] = (
        field_calibration_summary["can_write_to_actuator"]
    )
    manifest["latest_grey_box_field_calibration_can_write_to_release_gate"] = (
        field_calibration_summary["can_write_to_release_gate"]
    )
    manifest["latest_grey_box_calibration_collection_work_order_status"] = (
        collection_work_order["work_order_status"]
    )
    manifest["latest_grey_box_calibration_collection_work_order_table_count"] = (
        collection_work_order["table_work_item_count"]
    )
    manifest["latest_grey_box_calibration_collection_work_order_field_package_ready_for_agent53"] = (
        collection_work_order["field_package_ready_for_agent53"]
    )
    manifest["latest_grey_box_calibration_collection_work_order_agent53_field_candidate_ready"] = (
        collection_work_order["agent53_field_candidate_ready"]
    )
    manifest["latest_grey_box_calibration_collection_work_order_next_operator_action"] = (
        collection_work_order["next_operator_action"]
    )
    manifest["latest_grey_box_calibration_collection_work_order_can_generate_field_evidence"] = (
        collection_work_order["can_generate_field_evidence"]
    )
    manifest["latest_grey_box_calibration_collection_work_order_can_resume_model_chain"] = (
        collection_work_order["can_resume_model_chain"]
    )
    manifest["latest_grey_box_calibration_collection_work_order_can_write_to_actuator"] = (
        collection_work_order["can_write_to_actuator"]
    )
    manifest["latest_grey_box_calibration_collection_work_order_can_write_to_release_gate"] = (
        collection_work_order["can_write_to_release_gate"]
    )
    manifest["latest_grey_box_submission_readiness_gate_status"] = submission_readiness_gate[
        "gate_status"
    ]
    manifest["latest_grey_box_submission_readiness_score"] = submission_readiness_gate[
        "readiness_score"
    ]
    manifest["latest_grey_box_submission_readiness_highest_priority_gap_type"] = (
        submission_readiness_gate["highest_priority_gap"]["gap_type"]
    )
    manifest["latest_grey_box_submission_readiness_highest_priority_gap_table"] = (
        submission_readiness_gate["highest_priority_gap"]["table"]
    )
    manifest["latest_grey_box_submission_readiness_missing_table_count"] = (
        submission_readiness_gate["highest_priority_gap"].get("missing_table_count", 0)
    )
    manifest["latest_grey_box_submission_readiness_missing_tables"] = (
        submission_readiness_gate["highest_priority_gap"].get("missing_tables", [])
    )
    manifest["latest_grey_box_submission_readiness_source_env_var"] = (
        submission_readiness_gate["highest_priority_gap"].get("source_env_var", "")
    )
    manifest["latest_grey_box_submission_readiness_can_submit_to_agent53_field_calibration"] = (
        submission_readiness_gate["can_submit_to_agent53_field_calibration"]
    )
    manifest["latest_grey_box_submission_readiness_can_submit_to_agent53_field_candidate"] = (
        submission_readiness_gate["can_submit_to_agent53_field_candidate"]
    )
    manifest["latest_grey_box_submission_readiness_can_generate_field_evidence"] = (
        submission_readiness_gate["can_generate_field_evidence"]
    )
    manifest["latest_grey_box_submission_readiness_can_write_to_actuator"] = (
        submission_readiness_gate["can_write_to_actuator"]
    )
    manifest["latest_grey_box_submission_readiness_can_write_to_release_gate"] = (
        submission_readiness_gate["can_write_to_release_gate"]
    )
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()

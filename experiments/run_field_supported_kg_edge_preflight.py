from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from water_ai.field_supported_kg_edge_package import (
    SOURCE_ENV_VAR,
    build_field_supported_kg_edge_package_preflight,
    write_field_supported_kg_edge_package_template,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = PROJECT_ROOT / "deliverables" / "manifest.json"
OUT_DIR = PROJECT_ROOT / "outputs" / "field_supported_kg_edge_package"
DELIVERABLES_DIR = PROJECT_ROOT / "deliverables" / "model_core_optimization"
TEMPLATE_DIR = OUT_DIR / "field_supported_kg_edge_package_template"
PREFLIGHT_PATH = OUT_DIR / "field_supported_kg_edge_package_preflight.json"
REPORT_PATH = DELIVERABLES_DIR / "field_supported_kg_edge_package_preflight.md"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DELIVERABLES_DIR.mkdir(parents=True, exist_ok=True)
    template = write_field_supported_kg_edge_package_template(TEMPLATE_DIR)
    source_path = os.environ.get(SOURCE_ENV_VAR, "")
    preflight = build_field_supported_kg_edge_package_preflight(
        source_dir=source_path,
        external_package_supplied=bool(source_path),
    )
    PREFLIGHT_PATH.write_text(json.dumps(preflight, ensure_ascii=False, indent=2), encoding="utf-8")
    REPORT_PATH.write_text(_report_md(preflight, template), encoding="utf-8")
    _update_manifest(preflight)

    print(f"Field-supported KG edge package preflight: {preflight['package_status']}")
    print(f"- package_preflight_pass: {preflight['package_preflight_pass']}")
    print(f"- matched_edge_count: {preflight['matched_edge_count']}")
    print(f"- next_operator_action: {preflight['next_operator_action']}")
    print(f"preflight: {PREFLIGHT_PATH}")
    print(f"report: {REPORT_PATH}")


def _report_md(preflight: dict[str, Any], template: dict[str, Any]) -> str:
    lines = [
        "# Field-Supported KG Edge Package Preflight",
        "",
        "## Role",
        "",
        (
            "This preflight checks whether an external `FIELD_SUPPORTED_KG_EDGE_PACKAGE_DIR` "
            "can be routed to KG reasoning as field-supported edge input. It is not a "
            "site-specific mechanism proof or claim upgrade."
        ),
        "",
        "## Status",
        "",
        f"- package_status: `{preflight['package_status']}`",
        f"- source_env_var: `{preflight['source_env_var']}`",
        f"- source_path: `{preflight['source_path']}`",
        f"- package_preflight_pass: `{preflight['package_preflight_pass']}`",
        f"- matched_edge_count: `{preflight['matched_edge_count']}`",
        f"- minimum_matched_edge_count: `{preflight['minimum_matched_edge_count']}`",
        f"- field_supported_edge_coverage_candidate: `{preflight['field_supported_edge_coverage_candidate']}`",
        (
            "- can_route_to_kg_reasoning_field_edge_update: "
            f"`{preflight['can_route_to_kg_reasoning_field_edge_update']}`"
        ),
        f"- can_upgrade_site_specific_claims: `{preflight['can_upgrade_site_specific_claims']}`",
        f"- can_generate_field_evidence: `{preflight['can_generate_field_evidence']}`",
        f"- can_write_to_actuator: `{preflight['can_write_to_actuator']}`",
        f"- can_write_to_release_gate: `{preflight['can_write_to_release_gate']}`",
        f"- next_operator_action: `{preflight['next_operator_action']}`",
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
    lines.extend(["", "## Signal Audits", "", "| signal | valid rows | valid edge ids |", "| --- | --- | --- |"])
    for key in [
        "edge_audit",
        "source_basis_audit",
        "field_support_audit",
        "failure_boundary_audit",
        "claim_action_audit",
    ]:
        audit = preflight[key]
        lines.append(
            f"| `{audit['signal_family']}` | `{audit['valid_row_count']}` | `{audit['valid_edge_ids']}` |"
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


def _update_manifest(preflight: dict[str, Any]) -> None:
    manifest = _read_json(MANIFEST_PATH)
    manifest["latest_field_supported_kg_edge_package_preflight"] = str(
        PREFLIGHT_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_field_supported_kg_edge_package_preflight_report"] = str(
        REPORT_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_field_supported_kg_edge_package_template_dir"] = str(
        TEMPLATE_DIR.relative_to(PROJECT_ROOT)
    )
    manifest["latest_field_supported_kg_edge_package_status"] = preflight["package_status"]
    manifest["latest_field_supported_kg_edge_package_preflight_pass"] = preflight[
        "package_preflight_pass"
    ]
    manifest["latest_field_supported_kg_edge_package_matched_edge_count"] = preflight[
        "matched_edge_count"
    ]
    manifest["latest_field_supported_kg_edge_package_can_route_to_kg_reasoning_field_edge_update"] = (
        preflight["can_route_to_kg_reasoning_field_edge_update"]
    )
    manifest["latest_field_supported_kg_edge_package_can_upgrade_site_specific_claims"] = (
        preflight["can_upgrade_site_specific_claims"]
    )
    manifest["latest_field_supported_kg_edge_package_can_generate_field_evidence"] = preflight[
        "can_generate_field_evidence"
    ]
    manifest["latest_field_supported_kg_edge_package_can_write_to_actuator"] = preflight[
        "can_write_to_actuator"
    ]
    manifest["latest_field_supported_kg_edge_package_can_write_to_release_gate"] = preflight[
        "can_write_to_release_gate"
    ]
    manifest["latest_field_supported_kg_edge_package_next_operator_action"] = preflight[
        "next_operator_action"
    ]
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()

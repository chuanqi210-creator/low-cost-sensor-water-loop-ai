from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from water_ai.field_missingness_replay_package import (
    SOURCE_ENV_VAR,
    build_field_missingness_replay_package_preflight,
    write_field_missingness_replay_package_template,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = PROJECT_ROOT / "deliverables" / "manifest.json"
OUT_DIR = PROJECT_ROOT / "outputs" / "field_missingness_replay_package"
DELIVERABLES_DIR = PROJECT_ROOT / "deliverables" / "model_core_optimization"
TEMPLATE_DIR = OUT_DIR / "field_missingness_replay_package_template"
PREFLIGHT_PATH = OUT_DIR / "field_missingness_replay_package_preflight.json"
REPORT_PATH = DELIVERABLES_DIR / "field_missingness_replay_package_preflight.md"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DELIVERABLES_DIR.mkdir(parents=True, exist_ok=True)
    template = write_field_missingness_replay_package_template(TEMPLATE_DIR)
    source_path = os.environ.get(SOURCE_ENV_VAR, "")
    preflight = build_field_missingness_replay_package_preflight(
        source_dir=source_path,
        external_package_supplied=bool(source_path),
    )
    PREFLIGHT_PATH.write_text(json.dumps(preflight, ensure_ascii=False, indent=2), encoding="utf-8")
    REPORT_PATH.write_text(_report_md(preflight, template), encoding="utf-8")
    _update_manifest(preflight)

    print(f"Field missingness replay package preflight: {preflight['package_status']}")
    print(f"- package_preflight_pass: {preflight['package_preflight_pass']}")
    print(f"- matched_sample_count: {preflight['matched_sample_count']}")
    print(f"- unavailable_sample_count: {preflight['unavailable_sample_count']}")
    print(f"- next_operator_action: {preflight['next_operator_action']}")
    print(f"preflight: {PREFLIGHT_PATH}")
    print(f"report: {REPORT_PATH}")


def _report_md(preflight: dict[str, Any], template: dict[str, Any]) -> str:
    lines = [
        "# Field Missingness Replay Package Preflight",
        "",
        "## Role",
        "",
        (
            "This preflight checks whether an external `FIELD_MISSINGNESS_REPLAY_PACKAGE_DIR` "
            "can be routed to Agent54 as field missingness replay input for soft-sensor "
            "holdout work. It is not a field soft-sensor performance result."
        ),
        "",
        "## Status",
        "",
        f"- package_status: `{preflight['package_status']}`",
        f"- source_env_var: `{preflight['source_env_var']}`",
        f"- source_path: `{preflight['source_path']}`",
        f"- package_preflight_pass: `{preflight['package_preflight_pass']}`",
        f"- matched_sample_count: `{preflight['matched_sample_count']}`",
        f"- minimum_matched_sample_count: `{preflight['minimum_matched_sample_count']}`",
        f"- field_missingness_replay_coverage_candidate: `{preflight['field_missingness_replay_coverage_candidate']}`",
        f"- unavailable_sample_count: `{preflight['unavailable_sample_count']}`",
        f"- mean_sensor_quality_score: `{preflight['mean_sensor_quality_score']}`",
        f"- hidden_state_count: `{preflight['hidden_state_count']}`",
        (
            "- can_route_to_agent54_field_missingness_replay: "
            f"`{preflight['can_route_to_agent54_field_missingness_replay']}`"
        ),
        (
            "- can_route_to_soft_sensor_missingness_holdout: "
            f"`{preflight['can_route_to_soft_sensor_missingness_holdout']}`"
        ),
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
    lines.extend(["", "## Signal Audits", "", "| signal | valid rows | valid sample ids |", "| --- | --- | --- |"])
    for key in [
        "timeseries_audit",
        "availability_audit",
        "time_since_audit",
        "quality_audit",
        "label_audit",
    ]:
        audit = preflight[key]
        lines.append(
            f"| `{audit['signal_family']}` | `{audit['valid_row_count']}` | `{audit['valid_sample_ids']}` |"
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
    manifest["latest_field_missingness_replay_package_preflight"] = str(
        PREFLIGHT_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_field_missingness_replay_package_preflight_report"] = str(
        REPORT_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_field_missingness_replay_package_template_dir"] = str(
        TEMPLATE_DIR.relative_to(PROJECT_ROOT)
    )
    manifest["latest_field_missingness_replay_package_status"] = preflight["package_status"]
    manifest["latest_field_missingness_replay_package_preflight_pass"] = preflight[
        "package_preflight_pass"
    ]
    manifest["latest_field_missingness_replay_package_matched_sample_count"] = preflight[
        "matched_sample_count"
    ]
    manifest["latest_field_missingness_replay_package_unavailable_sample_count"] = preflight[
        "unavailable_sample_count"
    ]
    manifest["latest_field_missingness_replay_package_can_route_to_agent54_field_missingness_replay"] = (
        preflight["can_route_to_agent54_field_missingness_replay"]
    )
    manifest["latest_field_missingness_replay_package_can_route_to_soft_sensor_missingness_holdout"] = (
        preflight["can_route_to_soft_sensor_missingness_holdout"]
    )
    manifest["latest_field_missingness_replay_package_can_generate_field_evidence"] = preflight[
        "can_generate_field_evidence"
    ]
    manifest["latest_field_missingness_replay_package_can_write_to_actuator"] = preflight[
        "can_write_to_actuator"
    ]
    manifest["latest_field_missingness_replay_package_can_write_to_release_gate"] = preflight[
        "can_write_to_release_gate"
    ]
    manifest["latest_field_missingness_replay_package_next_operator_action"] = preflight[
        "next_operator_action"
    ]
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()

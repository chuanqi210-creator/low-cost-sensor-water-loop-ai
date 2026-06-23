from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from water_ai.catalyst_evidence_response_gate import build_catalyst_evidence_response_gate


PROJECT_ROOT = Path(__file__).resolve().parents[1]
FIELD_ACTIVATION_RESPONSE_ENV = "FIELD_ACTIVATION_RESPONSE_PATH"
OBSERVATION_RESPONSE_BRIDGE_PATH = (
    PROJECT_ROOT / "outputs" / "observation_response_bridge" / "observation_response_bridge_metrics.json"
)
RESPONSE_TEMPLATE_PATH = (
    PROJECT_ROOT / "outputs" / "model_core_governance" / "field_activation_response_template.json"
)
RESPONSE_SOURCE_PREFLIGHT_PATH = (
    PROJECT_ROOT / "outputs" / "model_core_governance" / "field_activation_response_source_preflight.json"
)
RESPONSE_PREFLIGHT_PATH = (
    PROJECT_ROOT / "outputs" / "model_core_governance" / "field_activation_response_preflight.json"
)
RESPONSE_SUBMISSION_PACKET_PATH = (
    PROJECT_ROOT / "outputs" / "model_core_governance" / "field_activation_response_submission_packet.json"
)
OUT_DIR = PROJECT_ROOT / "outputs" / "catalyst_evidence_response_gate"
METRICS_PATH = OUT_DIR / "catalyst_evidence_response_gate_metrics.json"
DELIVERABLE_PATH = PROJECT_ROOT / "deliverables" / "model_core_optimization" / "catalyst_evidence_response_gate.md"
MANIFEST_PATH = PROJECT_ROOT / "deliverables" / "manifest.json"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DELIVERABLE_PATH.parent.mkdir(parents=True, exist_ok=True)

    response = _selected_response()
    result = build_catalyst_evidence_response_gate(
        observation_response_bridge=_read_json(OBSERVATION_RESPONSE_BRIDGE_PATH),
        response=response,
        response_source_preflight=_read_json(RESPONSE_SOURCE_PREFLIGHT_PATH),
        response_preflight=_read_json(RESPONSE_PREFLIGHT_PATH),
        response_submission_packet=_read_json(RESPONSE_SUBMISSION_PACKET_PATH),
    )
    METRICS_PATH.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    DELIVERABLE_PATH.write_text(_deliverable_md(result), encoding="utf-8")
    _update_manifest(result)

    print(f"Catalyst evidence response gate: {result['gate_status']}")
    print(f"- target rows: {result['target_response_row_count']}")
    print(f"- row-level pass: {result['row_level_preflight_pass']}")
    print(f"- matched batches: {result['batch_alignment']['matched_batch_count']}")
    print(f"- next: {result['next_operator_action']}")
    print(f"metrics: {METRICS_PATH}")
    print(f"deliverable: {DELIVERABLE_PATH}")


def _selected_response() -> dict[str, Any]:
    response_path = os.environ.get(FIELD_ACTIVATION_RESPONSE_ENV, "").strip()
    if response_path and Path(response_path).exists():
        return _read_json(Path(response_path))
    return _read_json(RESPONSE_TEMPLATE_PATH)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _deliverable_md(result: dict[str, Any]) -> str:
    lines = [
        "# R8u110 Catalyst Evidence Response Gate",
        "",
        "## 定位",
        "",
        (
            "该门控只检查 R8u109 定位出的 catalyst_activity 六条优先 response rows，"
            "用于判断它们是否具备进入 focused package preflight 的最低条件。"
        ),
        "",
        "## Readiness",
        "",
        f"- gate_status: `{result['gate_status']}`",
        f"- target_hidden_state: `{result['target_hidden_state']}`",
        f"- response_source_external_response_supplied: `{result['response_source_external_response_supplied']}`",
        f"- target_response_row_count: `{result['target_response_row_count']}`",
        f"- provided_target_response_row_count: `{result['provided_target_response_row_count']}`",
        f"- missing_target_response_row_count: `{result['missing_target_response_row_count']}`",
        f"- blocked_target_response_row_count: `{result['blocked_target_response_row_count']}`",
        f"- row_level_preflight_pass: `{result['row_level_preflight_pass']}`",
        f"- matched_batch_count: `{result['batch_alignment']['matched_batch_count']}`",
        f"- matched_batch_requirement_pass: `{result['batch_alignment']['matched_batch_requirement_pass']}`",
        f"- can_route_to_focused_materialized_package_preflight: `{result['can_route_to_focused_materialized_package_preflight']}`",
        f"- can_route_to_agent51_field_proxy_holdout: `{result['can_route_to_agent51_field_proxy_holdout']}`",
        f"- can_relax_agent49_catalyst_uncertainty_block: `{result['can_relax_agent49_catalyst_uncertainty_block']}`",
        f"- next_operator_action: `{result['next_operator_action']}`",
        "",
        "## Target Rows",
        "",
        "| row | role | status | issues | batch ids |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in result["target_row_results"]:
        lines.append(
            f"| `{row['response_row_id']}` | `{row['observation_role']}` | "
            f"`{row['row_status']}` | `{row['blocking_issues']}` | `{row['batch_ids']}` |"
        )
    lines.extend(
        [
            "",
            "## Batch Boundary",
            "",
            result["batch_alignment"]["batch_boundary"],
            "",
            "## Field Boundary",
            "",
            result["field_boundary"],
            "",
            "## No-Write Boundary",
            "",
            result["no_write_boundary"],
            "",
        ]
    )
    return "\n".join(lines)


def _update_manifest(result: dict[str, Any]) -> None:
    manifest = _read_json(MANIFEST_PATH)
    manifest["latest_catalyst_evidence_response_gate"] = str(METRICS_PATH.relative_to(PROJECT_ROOT))
    manifest["latest_catalyst_evidence_response_gate_doc"] = str(DELIVERABLE_PATH.relative_to(PROJECT_ROOT))
    manifest["latest_catalyst_evidence_response_gate_status"] = result["gate_status"]
    manifest["latest_catalyst_evidence_response_gate_target_hidden_state"] = result["target_hidden_state"]
    manifest["latest_catalyst_evidence_response_gate_target_response_row_count"] = result[
        "target_response_row_count"
    ]
    manifest["latest_catalyst_evidence_response_gate_row_level_preflight_pass"] = result[
        "row_level_preflight_pass"
    ]
    manifest["latest_catalyst_evidence_response_gate_matched_batch_count"] = result["batch_alignment"][
        "matched_batch_count"
    ]
    manifest["latest_catalyst_evidence_response_gate_matched_batch_requirement_pass"] = result[
        "batch_alignment"
    ]["matched_batch_requirement_pass"]
    manifest["latest_catalyst_evidence_response_gate_can_route_to_focused_materialized_package_preflight"] = result[
        "can_route_to_focused_materialized_package_preflight"
    ]
    manifest["latest_catalyst_evidence_response_gate_can_route_to_agent51_field_proxy_holdout"] = result[
        "can_route_to_agent51_field_proxy_holdout"
    ]
    manifest["latest_catalyst_evidence_response_gate_can_relax_agent49_catalyst_uncertainty_block"] = result[
        "can_relax_agent49_catalyst_uncertainty_block"
    ]
    manifest["latest_catalyst_evidence_response_gate_next_operator_action"] = result["next_operator_action"]
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from water_ai.catalyst_response_submission_kit import build_catalyst_response_submission_kit


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OBSERVATION_RESPONSE_BRIDGE_PATH = (
    PROJECT_ROOT / "outputs" / "observation_response_bridge" / "observation_response_bridge_metrics.json"
)
FULL_RESPONSE_TEMPLATE_PATH = (
    PROJECT_ROOT / "outputs" / "model_core_governance" / "field_activation_response_template.json"
)
CATALYST_GATE_PATH = (
    PROJECT_ROOT / "outputs" / "catalyst_evidence_response_gate" / "catalyst_evidence_response_gate_metrics.json"
)
OUT_DIR = PROJECT_ROOT / "outputs" / "catalyst_response_submission_kit"
METRICS_PATH = OUT_DIR / "catalyst_response_submission_kit_metrics.json"
FOCUSED_TEMPLATE_PATH = OUT_DIR / "focused_catalyst_response_template.json"
FOCUSED_SCHEMA_PATH = OUT_DIR / "focused_catalyst_response_schema.json"
MERGE_PLAN_PATH = OUT_DIR / "focused_to_full_response_merge_plan.json"
DELIVERABLE_PATH = PROJECT_ROOT / "deliverables" / "model_core_optimization" / "catalyst_response_submission_kit.md"
MANIFEST_PATH = PROJECT_ROOT / "deliverables" / "manifest.json"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DELIVERABLE_PATH.parent.mkdir(parents=True, exist_ok=True)

    result = build_catalyst_response_submission_kit(
        observation_response_bridge=_read_json(OBSERVATION_RESPONSE_BRIDGE_PATH),
        full_response_template=_read_json(FULL_RESPONSE_TEMPLATE_PATH),
        catalyst_evidence_response_gate=_read_json(CATALYST_GATE_PATH),
    )
    METRICS_PATH.write_text(json.dumps(_metrics_result(result), ensure_ascii=False, indent=2), encoding="utf-8")
    FOCUSED_TEMPLATE_PATH.write_text(
        json.dumps(result["focused_response_template"], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    FOCUSED_SCHEMA_PATH.write_text(
        json.dumps(result["focused_response_schema"], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    MERGE_PLAN_PATH.write_text(
        json.dumps(result["full_response_merge_plan"], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    DELIVERABLE_PATH.write_text(_deliverable_md(result), encoding="utf-8")
    _update_manifest(result)

    print(f"Catalyst response submission kit: {result['kit_status']}")
    print(f"- target rows: {result['target_response_row_count']}")
    print(f"- template: {FOCUSED_TEMPLATE_PATH}")
    print(f"- schema: {FOCUSED_SCHEMA_PATH}")
    print(f"- merge plan: {MERGE_PLAN_PATH}")
    print(f"- next: {result['next_operator_action']}")


def _metrics_result(result: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in result.items()
        if key not in {"focused_response_template", "focused_response_schema", "full_response_merge_plan"}
    } | {
        "focused_response_template_path": str(FOCUSED_TEMPLATE_PATH.relative_to(PROJECT_ROOT)),
        "focused_response_schema_path": str(FOCUSED_SCHEMA_PATH.relative_to(PROJECT_ROOT)),
        "full_response_merge_plan_path": str(MERGE_PLAN_PATH.relative_to(PROJECT_ROOT)),
    }


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _deliverable_md(result: dict[str, Any]) -> str:
    template = result["focused_response_template"]
    merge_plan = result["full_response_merge_plan"]
    lines = [
        "# R8u111 Catalyst Response Submission Kit",
        "",
        "## 定位",
        "",
        (
            "该提交小包把 full field activation response 的 33 行收缩为 catalyst_activity 的 6 行，"
            "降低外部人员填写 `FIELD_ACTIVATION_RESPONSE_PATH` 前的扫描摩擦。"
        ),
        "",
        "## Readiness",
        "",
        f"- kit_status: `{result['kit_status']}`",
        f"- target_hidden_state: `{result['target_hidden_state']}`",
        f"- target_response_row_count: `{result['target_response_row_count']}`",
        f"- minimum_matched_batch_count: `{result['minimum_matched_batch_count']}`",
        f"- focused_response_template_path: `{FOCUSED_TEMPLATE_PATH.relative_to(PROJECT_ROOT)}`",
        f"- focused_response_schema_path: `{FOCUSED_SCHEMA_PATH.relative_to(PROJECT_ROOT)}`",
        f"- merge_plan_path: `{MERGE_PLAN_PATH.relative_to(PROJECT_ROOT)}`",
        f"- can_route_to_agent51_field_proxy_holdout: `{result['can_route_to_agent51_field_proxy_holdout']}`",
        f"- can_relax_agent49_catalyst_uncertainty_block: `{result['can_relax_agent49_catalyst_uncertainty_block']}`",
        "",
        "## Focused Rows",
        "",
        "| row | role | required evidence | priority |",
        "| --- | --- | --- | --- |",
    ]
    for row in template["evidence_rows"]:
        lines.append(
            f"| `{row['response_row_id']}` | `{row['observation_role']}` | "
            f"`{row['required_evidence']}` | `{row['priority']}` |"
        )
    lines.extend(
        [
            "",
            "## Merge Plan",
            "",
            f"- merge_strategy: `{merge_plan['merge_strategy']}`",
            f"- target_full_template_row_count: `{merge_plan['target_full_template_row_count']}`",
            f"- focused_replacement_row_count: `{merge_plan['focused_replacement_row_count']}`",
            f"- remaining_full_response_row_count: `{merge_plan['remaining_full_response_row_count']}`",
            "",
            "## Boundary",
            "",
            result["field_boundary"],
            "",
            result["no_write_boundary"],
            "",
        ]
    )
    return "\n".join(lines)


def _update_manifest(result: dict[str, Any]) -> None:
    manifest = _read_json(MANIFEST_PATH)
    manifest["latest_catalyst_response_submission_kit"] = str(METRICS_PATH.relative_to(PROJECT_ROOT))
    manifest["latest_catalyst_response_submission_kit_doc"] = str(DELIVERABLE_PATH.relative_to(PROJECT_ROOT))
    manifest["latest_catalyst_response_submission_kit_focused_template"] = str(
        FOCUSED_TEMPLATE_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_catalyst_response_submission_kit_schema"] = str(FOCUSED_SCHEMA_PATH.relative_to(PROJECT_ROOT))
    manifest["latest_catalyst_response_submission_kit_merge_plan"] = str(MERGE_PLAN_PATH.relative_to(PROJECT_ROOT))
    manifest["latest_catalyst_response_submission_kit_status"] = result["kit_status"]
    manifest["latest_catalyst_response_submission_kit_target_response_row_count"] = result[
        "target_response_row_count"
    ]
    manifest["latest_catalyst_response_submission_kit_minimum_matched_batch_count"] = result[
        "minimum_matched_batch_count"
    ]
    manifest["latest_catalyst_response_submission_kit_can_route_to_agent51_field_proxy_holdout"] = result[
        "can_route_to_agent51_field_proxy_holdout"
    ]
    manifest["latest_catalyst_response_submission_kit_can_relax_agent49_catalyst_uncertainty_block"] = result[
        "can_relax_agent49_catalyst_uncertainty_block"
    ]
    manifest["latest_catalyst_response_submission_kit_next_operator_action"] = result["next_operator_action"]
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()

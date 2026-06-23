from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from water_ai.focused_catalyst_response_merge import (
    build_focused_catalyst_response_merge_preflight,
    build_focused_catalyst_response_repair_work_order,
    preflight_focused_catalyst_response_source,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
FOCUSED_RESPONSE_ENV = "FOCUSED_CATALYST_RESPONSE_PATH"
FOCUSED_TEMPLATE_PATH = (
    PROJECT_ROOT / "outputs" / "catalyst_response_submission_kit" / "focused_catalyst_response_template.json"
)
FOCUSED_SCHEMA_PATH = (
    PROJECT_ROOT / "outputs" / "catalyst_response_submission_kit" / "focused_catalyst_response_schema.json"
)
FULL_RESPONSE_TEMPLATE_PATH = (
    PROJECT_ROOT / "outputs" / "model_core_governance" / "field_activation_response_template.json"
)
MERGE_PLAN_PATH = (
    PROJECT_ROOT / "outputs" / "catalyst_response_submission_kit" / "focused_to_full_response_merge_plan.json"
)
OUT_DIR = PROJECT_ROOT / "outputs" / "focused_catalyst_response_merge"
SOURCE_PREFLIGHT_PATH = OUT_DIR / "focused_catalyst_response_source_preflight.json"
PREFLIGHT_PATH = OUT_DIR / "focused_catalyst_response_merge_preflight.json"
REPAIR_WORK_ORDER_PATH = OUT_DIR / "focused_catalyst_response_repair_work_order.json"
MERGED_CANDIDATE_PATH = OUT_DIR / "merged_full_field_activation_response_candidate.json"
DELIVERABLE_PATH = PROJECT_ROOT / "deliverables" / "model_core_optimization" / "focused_catalyst_response_merge.md"
MANIFEST_PATH = PROJECT_ROOT / "deliverables" / "manifest.json"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DELIVERABLE_PATH.parent.mkdir(parents=True, exist_ok=True)

    focused_template = _read_json(FOCUSED_TEMPLATE_PATH)
    focused_response, source_preflight = _load_focused_response(focused_template)
    result = build_focused_catalyst_response_merge_preflight(
        focused_response=focused_response,
        focused_schema=_read_json(FOCUSED_SCHEMA_PATH),
        full_response_template=_read_json(FULL_RESPONSE_TEMPLATE_PATH),
        merge_plan=_read_json(MERGE_PLAN_PATH),
        source_path=str(source_preflight["source_path"]),
        external_response_supplied=bool(source_preflight["external_response_supplied"]),
        source_preflight=source_preflight,
    )
    repair_work_order = build_focused_catalyst_response_repair_work_order(
        source_preflight=source_preflight,
        merge_preflight=result,
    )
    result["focused_catalyst_response_repair_work_order"] = repair_work_order

    candidate = result.pop("merged_full_response_candidate")
    SOURCE_PREFLIGHT_PATH.write_text(json.dumps(source_preflight, ensure_ascii=False, indent=2), encoding="utf-8")
    PREFLIGHT_PATH.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    REPAIR_WORK_ORDER_PATH.write_text(
        json.dumps(repair_work_order, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    MERGED_CANDIDATE_PATH.write_text(json.dumps(candidate, ensure_ascii=False, indent=2), encoding="utf-8")
    DELIVERABLE_PATH.write_text(_deliverable_md(result, candidate), encoding="utf-8")
    _update_manifest(result, candidate)

    print(f"Focused catalyst response merge: {result['preflight_status']}")
    print(f"- source: {source_preflight['source_preflight_status']}")
    print(f"- row pass: {result['row_preflight_pass']}")
    print(f"- matched batches: {result['batch_alignment']['matched_batch_count']}")
    print(f"- repair work order: {repair_work_order['work_order_status']}")
    print(f"- candidate: {MERGED_CANDIDATE_PATH}")
    print(f"- next: {result['next_operator_action']}")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_focused_response(default_template: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    source_path = os.environ.get(FOCUSED_RESPONSE_ENV, "").strip()
    if not source_path:
        source_preflight = preflight_focused_catalyst_response_source(
            source_path="",
            load_status="focused_catalyst_response_source_not_supplied",
            response=default_template,
            default_response_template=default_template,
        )
        return default_template, source_preflight

    path = Path(source_path).expanduser()
    if not path.is_absolute():
        path = (PROJECT_ROOT / path).resolve()
    if not path.exists():
        response: dict[str, Any] = {}
        load_status = "focused_catalyst_response_source_file_missing"
    else:
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            response = {}
            load_status = "focused_catalyst_response_source_invalid_json"
        else:
            if isinstance(loaded, dict):
                response = loaded
                load_status = "focused_catalyst_response_source_loaded"
            else:
                response = {}
                load_status = "focused_catalyst_response_source_root_not_object"

    source_preflight = preflight_focused_catalyst_response_source(
        source_path=str(path),
        load_status=load_status,
        response=response,
        default_response_template=default_template,
    )
    return (response if source_preflight["can_run_merge_preflight"] else default_template), source_preflight


def _deliverable_md(result: dict[str, Any], candidate: dict[str, Any]) -> str:
    lines = [
        "# R8u112 Focused Catalyst Response Merge Preflight",
        "",
        "## 定位",
        "",
        (
            "该预检把外部填写后的 focused catalyst response 合并回 full field activation response candidate。"
            "它只验证和替换 `catalyst_activity` 六行，不替代 full response preflight 或 field validation。"
        ),
        "",
        "## Readiness",
        "",
        f"- source_preflight_status: `{result['source_preflight_status']}`",
        f"- source_can_run_merge_preflight: `{result['source_can_run_merge_preflight']}`",
        f"- preflight_status: `{result['preflight_status']}`",
        f"- source_env_var: `{result['source_env_var']}`",
        f"- external_response_supplied: `{result['external_response_supplied']}`",
        f"- row_preflight_pass: `{result['row_preflight_pass']}`",
        f"- matched_batch_count: `{result['batch_alignment']['matched_batch_count']}`",
        f"- matched_batch_requirement_pass: `{result['batch_alignment']['matched_batch_requirement_pass']}`",
        f"- repair_work_order_status: `{result['focused_catalyst_response_repair_work_order']['work_order_status']}`",
        f"- repair_item_count: `{result['focused_catalyst_response_repair_work_order']['repair_item_count']}`",
        f"- highest_priority_repair_id: `{result['focused_catalyst_response_repair_work_order']['highest_priority_repair_id']}`",
        f"- repair_next_operator_action: `{result['focused_catalyst_response_repair_work_order']['next_operator_action']}`",
        f"- can_emit_merged_full_response_candidate: `{result['can_emit_merged_full_response_candidate']}`",
        f"- can_submit_candidate_as_FIELD_ACTIVATION_RESPONSE_PATH: `{result['can_submit_candidate_as_FIELD_ACTIVATION_RESPONSE_PATH']}`",
        f"- candidate_availability_status: `{candidate['candidate_availability_status']}`",
        f"- candidate_preflight_submit_ready: `{candidate['candidate_preflight_submit_ready']}`",
        f"- candidate_self_declared_submit_ready_legacy_alias: `{candidate['candidate_self_declared_submit_ready']}`",
        f"- candidate_submit_ready_semantics: {candidate['candidate_submit_ready_semantics']}",
        f"- can_route_to_agent51_field_proxy_holdout: `{result['can_route_to_agent51_field_proxy_holdout']}`",
        f"- focused_catalyst_response_repair_work_order_path: `{REPAIR_WORK_ORDER_PATH.relative_to(PROJECT_ROOT)}`",
        f"- merged_full_response_candidate_path: `{MERGED_CANDIDATE_PATH.relative_to(PROJECT_ROOT)}`",
        "",
        "## Focused Rows",
        "",
        "| row | status | issues | batch ids |",
        "| --- | --- | --- | --- |",
    ]
    for row in result["row_results"]:
        lines.append(
            f"| `{row['response_row_id']}` | `{row['row_status']}` | "
            f"`{row['blocking_issues']}` | `{row['batch_ids']}` |"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            candidate["candidate_use_boundary"],
            "",
            result["full_response_boundary"],
            "",
            result["no_write_boundary"],
            "",
        ]
    )
    return "\n".join(lines)


def _update_manifest(result: dict[str, Any], candidate: dict[str, Any]) -> None:
    manifest = _read_json(MANIFEST_PATH)
    manifest["latest_focused_catalyst_response_source_preflight"] = str(
        SOURCE_PREFLIGHT_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_focused_catalyst_response_source_preflight_status"] = result[
        "source_preflight_status"
    ]
    manifest["latest_focused_catalyst_response_source_can_run_merge_preflight"] = result[
        "source_can_run_merge_preflight"
    ]
    manifest["latest_focused_catalyst_response_merge_preflight"] = str(PREFLIGHT_PATH.relative_to(PROJECT_ROOT))
    manifest["latest_focused_catalyst_response_repair_work_order"] = str(
        REPAIR_WORK_ORDER_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_focused_catalyst_response_repair_work_order_status"] = result[
        "focused_catalyst_response_repair_work_order"
    ]["work_order_status"]
    manifest["latest_focused_catalyst_response_repair_item_count"] = result[
        "focused_catalyst_response_repair_work_order"
    ]["repair_item_count"]
    manifest["latest_focused_catalyst_response_repair_highest_priority_repair_id"] = result[
        "focused_catalyst_response_repair_work_order"
    ]["highest_priority_repair_id"]
    manifest["latest_focused_catalyst_response_repair_next_operator_action"] = result[
        "focused_catalyst_response_repair_work_order"
    ]["next_operator_action"]
    manifest["latest_focused_catalyst_response_merge_doc"] = str(DELIVERABLE_PATH.relative_to(PROJECT_ROOT))
    manifest["latest_focused_catalyst_response_merge_candidate"] = str(
        MERGED_CANDIDATE_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_focused_catalyst_response_merge_candidate_availability_status"] = candidate[
        "candidate_availability_status"
    ]
    manifest["latest_focused_catalyst_response_merge_candidate_self_declared_submit_ready"] = candidate[
        "candidate_self_declared_submit_ready"
    ]
    manifest["latest_focused_catalyst_response_merge_candidate_preflight_submit_ready"] = candidate[
        "candidate_preflight_submit_ready"
    ]
    manifest["latest_focused_catalyst_response_merge_candidate_submit_ready_semantics"] = candidate[
        "candidate_submit_ready_semantics"
    ]
    manifest["latest_focused_catalyst_response_merge_candidate_external_response_supplied"] = candidate[
        "external_focused_response_supplied"
    ]
    manifest["latest_focused_catalyst_response_merge_candidate_focused_replacement_row_count"] = candidate[
        "focused_replacement_row_count"
    ]
    manifest["latest_focused_catalyst_response_merge_candidate_focused_matched_batch_count"] = candidate[
        "focused_matched_batch_count"
    ]
    manifest["latest_focused_catalyst_response_merge_status"] = result["preflight_status"]
    manifest["latest_focused_catalyst_response_merge_row_preflight_pass"] = result["row_preflight_pass"]
    manifest["latest_focused_catalyst_response_merge_matched_batch_count"] = result["batch_alignment"][
        "matched_batch_count"
    ]
    manifest["latest_focused_catalyst_response_merge_can_emit_candidate"] = result[
        "can_emit_merged_full_response_candidate"
    ]
    manifest["latest_focused_catalyst_response_merge_can_submit_candidate_as_FIELD_ACTIVATION_RESPONSE_PATH"] = result[
        "can_submit_candidate_as_FIELD_ACTIVATION_RESPONSE_PATH"
    ]
    manifest["latest_focused_catalyst_response_merge_can_route_to_agent51_field_proxy_holdout"] = result[
        "can_route_to_agent51_field_proxy_holdout"
    ]
    manifest["latest_focused_catalyst_response_merge_next_operator_action"] = result["next_operator_action"]
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()

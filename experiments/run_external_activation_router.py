from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from water_ai.external_activation_router import build_external_activation_router


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = PROJECT_ROOT / "deliverables" / "manifest.json"
CONTRACT_PATH = PROJECT_ROOT / "outputs" / "model_core_governance" / "external_activation_contract.json"
CANDIDATE_METRICS_PATH = (
    PROJECT_ROOT
    / "outputs"
    / "catalyst_slice_r7_patch_candidate"
    / "catalyst_slice_r7_patch_candidate_metrics.json"
)
FIELD_ACTIVATION_EXTERNAL_READINESS_GATE_PATH = (
    PROJECT_ROOT / "outputs" / "model_core_governance" / "field_activation_external_readiness_gate.json"
)
FIELD_ACTIVATION_RESPONSE_SUBMISSION_PACKET_PATH = (
    PROJECT_ROOT / "outputs" / "model_core_governance" / "field_activation_response_submission_packet.json"
)
FIELD_ACTIVATION_RESPONSE_FOCUS_HANDOFF_PATH = (
    PROJECT_ROOT / "outputs" / "model_core_governance" / "field_activation_response_focus_handoff.json"
)
OUT_PATH = PROJECT_ROOT / "outputs" / "model_core_governance" / "external_activation_router.json"
REPORT_PATH = PROJECT_ROOT / "deliverables" / "model_core_optimization" / "external_activation_router.md"


def main() -> None:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    contract = _read_json(CONTRACT_PATH)
    router = build_external_activation_router(
        contract,
        env={
            "REAL_FIELD_REPLAY_PACKAGE_DIR": os.environ.get("REAL_FIELD_REPLAY_PACKAGE_DIR", ""),
            "FIELD_PATH_ENDPOINT_LABEL_PACKAGE_DIR": os.environ.get(
                "FIELD_PATH_ENDPOINT_LABEL_PACKAGE_DIR",
                "",
            ),
            "FORMAL_SEARCH_RESULT_PACKAGE_PATH": os.environ.get("FORMAL_SEARCH_RESULT_PACKAGE_PATH", ""),
        },
        project_root=PROJECT_ROOT,
        catalyst_slice_r7_patch_candidate_metrics=_read_json(CANDIDATE_METRICS_PATH),
        field_activation_external_readiness_gate=_read_json(
            FIELD_ACTIVATION_EXTERNAL_READINESS_GATE_PATH
        ),
        field_activation_response_submission_packet=_read_json(
            FIELD_ACTIVATION_RESPONSE_SUBMISSION_PACKET_PATH
        ),
        field_activation_response_focus_handoff=_read_json(
            FIELD_ACTIVATION_RESPONSE_FOCUS_HANDOFF_PATH
        ),
    )
    OUT_PATH.write_text(json.dumps(router, ensure_ascii=False, indent=2), encoding="utf-8")
    REPORT_PATH.write_text(_report_md(router), encoding="utf-8")
    _update_manifest(router)
    print(f"External activation router: {router['router_status']}")
    print(f"- route_ready_count: {router['route_ready_count']}")
    print(f"- model_chain_ready_route_count: {router['model_chain_ready_route_count']}")
    print(f"- handoff_ready_route_count: {router['handoff_ready_route_count']}")
    print(f"- path_supplied_count: {router['path_supplied_count']}")
    print(f"- blocked_route_count: {router['blocked_route_count']}")
    print(f"- catalyst_patch_candidate_status: {router['catalyst_patch_candidate_status']}")
    print(
        "- catalyst_patch_candidate_can_submit_as_REAL_FIELD_REPLAY_PACKAGE_DIR: "
        f"{router['catalyst_patch_candidate_can_submit_as_REAL_FIELD_REPLAY_PACKAGE_DIR']}"
    )
    print(f"- field_activation_upstream_status: {router['field_activation_upstream_status']}")
    print(
        "- field_activation_upstream_focus_handoff_status: "
        f"{router['field_activation_upstream_focus_handoff_status']}"
    )
    print(
        "- field_activation_upstream_can_submit_to_external_activation_router: "
        f"{router['field_activation_upstream_can_submit_to_external_activation_router']}"
    )
    print(f"- highest_priority_blocker: {router['highest_priority_blocker']}")
    print(f"- next_operator_action: {router['next_operator_action']}")
    print(f"router: {OUT_PATH}")
    print(f"report: {REPORT_PATH}")


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _report_md(router: dict[str, Any]) -> str:
    lines = [
        "# External Activation Router",
        "",
        f"- router_id：`{router['router_id']}`",
        f"- source_contract_id：`{router['source_contract_id']}`",
        f"- router_status：`{router['router_status']}`",
        f"- path_supplied_count：`{router['path_supplied_count']}`",
        f"- route_ready_count：`{router['route_ready_count']}`",
        f"- model_chain_ready_route_count：`{router['model_chain_ready_route_count']}`",
        f"- handoff_ready_route_count：`{router['handoff_ready_route_count']}`",
        f"- blocked_route_count：`{router['blocked_route_count']}`",
        f"- catalyst_patch_candidate_status：`{router['catalyst_patch_candidate_status']}`",
        f"- catalyst_patch_candidate_materialized：`{router['catalyst_patch_candidate_materialized']}`",
        f"- catalyst_patch_candidate_preflight_status：`{router['catalyst_patch_candidate_preflight_status']}`",
        f"- catalyst_patch_candidate_remaining_gap_count：`{router['catalyst_patch_candidate_remaining_gap_count']}`",
        (
            "- catalyst_patch_candidate_can_submit_as_REAL_FIELD_REPLAY_PACKAGE_DIR："
            f"`{router['catalyst_patch_candidate_can_submit_as_REAL_FIELD_REPLAY_PACKAGE_DIR']}`"
        ),
        f"- catalyst_patch_candidate_package_dir：`{router['catalyst_patch_candidate_package_dir']}`",
        f"- field_activation_upstream_status：`{router['field_activation_upstream_status']}`",
        (
            "- field_activation_upstream_can_submit_to_external_activation_router："
            f"`{router['field_activation_upstream_can_submit_to_external_activation_router']}`"
        ),
        f"- field_activation_upstream_first_blocked_step：`{router['field_activation_upstream_first_blocked_step']}`",
        f"- field_activation_upstream_highest_priority_blocker：`{router['field_activation_upstream_highest_priority_blocker']}`",
        f"- field_activation_upstream_next_operator_action：`{router['field_activation_upstream_next_operator_action']}`",
        f"- field_activation_upstream_submission_packet_status：`{router['field_activation_upstream_submission_packet_status']}`",
        f"- field_activation_upstream_focus_handoff_status：`{router['field_activation_upstream_focus_handoff_status']}`",
        (
            "- field_activation_upstream_focus_handoff_target_hidden_state："
            f"`{router['field_activation_upstream_focus_handoff_target_hidden_state']}`"
        ),
        (
            "- field_activation_upstream_focus_handoff_source_env_var："
            f"`{router['field_activation_upstream_focus_handoff_source_env_var']}`"
        ),
        (
            "- field_activation_upstream_focus_handoff_repair_work_order_status："
            f"`{router['field_activation_upstream_focus_handoff_repair_work_order_status']}`"
        ),
        (
            "- field_activation_upstream_focus_handoff_repair_item_count："
            f"`{router['field_activation_upstream_focus_handoff_repair_item_count']}`"
        ),
        (
            "- field_activation_upstream_focus_handoff_repair_next_operator_action："
            f"`{router['field_activation_upstream_focus_handoff_repair_next_operator_action']}`"
        ),
        f"- priority_route_channel_id：`{router['priority_route_channel_id']}`",
        f"- priority_route_status：`{router['priority_route_status']}`",
        f"- priority_route_preflight_status：`{router['priority_route_preflight_status']}`",
        f"- highest_priority_blocker：`{router['highest_priority_blocker']}`",
        f"- next_operator_action：`{router['next_operator_action']}`",
        f"- router_validation_command：`{router['router_validation_command']}`",
        f"- ready_channel_ids：`{router['ready_channel_ids']}`",
        f"- model_chain_ready_channel_ids：`{router['model_chain_ready_channel_ids']}`",
        f"- handoff_ready_channel_ids：`{router['handoff_ready_channel_ids']}`",
        f"- blocked_channel_ids：`{router['blocked_channel_ids']}`",
        f"- boundary_preserved：`{router['boundary_preserved']}`",
        f"- global_no_write_boundary：{router['global_no_write_boundary']}",
        "",
        "| 通道 | 状态 | 路径变量 | 已提交 | 可路由 | 预检 | 阻断原因 | 下一步 |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in router["route_rows"]:
        lines.append(
            "| "
            f"{row['channel_id']} | "
            f"{row['route_status']} | "
            f"{row['package_pointer']} | "
            f"{row['path_supplied']} | "
            f"{row['route_ready']} | "
            f"{_route_preflight_status(row)} | "
            f"{row.get('blocked_reason', '')} | "
            f"{row.get('operator_action', '')} |"
        )
    lines.extend(["", "## Ready Commands", ""])
    if router["next_commands"]:
        lines.extend(f"- `{command}`" for command in router["next_commands"])
    else:
        lines.append("- No route is ready; set one of the package path environment variables first.")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- The router does not execute external search or field replay by itself.",
            "- The router does not create field evidence from a path existing on disk.",
            "- Actuator/release/legal/claim outputs remain blocked until downstream gates pass.",
        ]
    )
    return "\n".join(lines)


def _route_preflight_status(row: dict[str, Any]) -> str:
    field_preflight = row.get("field_package_preflight")
    if isinstance(field_preflight, dict):
        return str(field_preflight.get("status", "field_package_preflight_unknown"))
    path_preflight = row.get("path_endpoint_preflight")
    if isinstance(path_preflight, dict):
        return str(path_preflight.get("preflight_status", "path_endpoint_preflight_unknown"))
    return "-"


def _update_manifest(router: dict[str, Any]) -> None:
    manifest = _read_json(MANIFEST_PATH)
    manifest["latest_external_activation_router"] = str(OUT_PATH.relative_to(PROJECT_ROOT))
    manifest["latest_external_activation_router_report"] = str(REPORT_PATH.relative_to(PROJECT_ROOT))
    manifest["latest_external_activation_router_status"] = router["router_status"]
    manifest["latest_external_activation_router_path_supplied_count"] = router["path_supplied_count"]
    manifest["latest_external_activation_router_route_ready_count"] = router["route_ready_count"]
    manifest["latest_external_activation_router_model_chain_ready_route_count"] = router[
        "model_chain_ready_route_count"
    ]
    manifest["latest_external_activation_router_handoff_ready_route_count"] = router[
        "handoff_ready_route_count"
    ]
    manifest["latest_external_activation_router_blocked_route_count"] = router["blocked_route_count"]
    manifest["latest_external_activation_router_catalyst_patch_candidate_consumed"] = router[
        "catalyst_patch_candidate_consumed"
    ]
    manifest["latest_external_activation_router_catalyst_patch_candidate_status"] = router[
        "catalyst_patch_candidate_status"
    ]
    manifest["latest_external_activation_router_catalyst_patch_candidate_materialized"] = router[
        "catalyst_patch_candidate_materialized"
    ]
    manifest["latest_external_activation_router_catalyst_patch_candidate_preflight_status"] = router[
        "catalyst_patch_candidate_preflight_status"
    ]
    manifest["latest_external_activation_router_catalyst_patch_candidate_remaining_gap_count"] = router[
        "catalyst_patch_candidate_remaining_gap_count"
    ]
    manifest[
        "latest_external_activation_router_catalyst_patch_candidate_can_submit_as_REAL_FIELD_REPLAY_PACKAGE_DIR"
    ] = router["catalyst_patch_candidate_can_submit_as_REAL_FIELD_REPLAY_PACKAGE_DIR"]
    manifest["latest_external_activation_router_catalyst_patch_candidate_package_dir"] = router[
        "catalyst_patch_candidate_package_dir"
    ]
    manifest["latest_external_activation_router_field_activation_upstream_consumed"] = router[
        "field_activation_upstream_consumed"
    ]
    manifest["latest_external_activation_router_field_activation_upstream_status"] = router[
        "field_activation_upstream_status"
    ]
    manifest[
        "latest_external_activation_router_field_activation_upstream_can_submit_to_external_activation_router"
    ] = router["field_activation_upstream_can_submit_to_external_activation_router"]
    manifest["latest_external_activation_router_field_activation_upstream_first_blocked_step"] = router[
        "field_activation_upstream_first_blocked_step"
    ]
    manifest[
        "latest_external_activation_router_field_activation_upstream_highest_priority_blocker"
    ] = router["field_activation_upstream_highest_priority_blocker"]
    manifest["latest_external_activation_router_field_activation_upstream_next_operator_action"] = router[
        "field_activation_upstream_next_operator_action"
    ]
    manifest[
        "latest_external_activation_router_field_activation_upstream_submission_packet_status"
    ] = router["field_activation_upstream_submission_packet_status"]
    manifest[
        "latest_external_activation_router_field_activation_upstream_focus_handoff_status"
    ] = router["field_activation_upstream_focus_handoff_status"]
    manifest[
        "latest_external_activation_router_field_activation_upstream_focus_handoff_target_hidden_state"
    ] = router["field_activation_upstream_focus_handoff_target_hidden_state"]
    manifest[
        "latest_external_activation_router_field_activation_upstream_focus_handoff_source_env_var"
    ] = router["field_activation_upstream_focus_handoff_source_env_var"]
    manifest[
        "latest_external_activation_router_field_activation_upstream_focus_handoff_repair_work_order_status"
    ] = router["field_activation_upstream_focus_handoff_repair_work_order_status"]
    manifest[
        "latest_external_activation_router_field_activation_upstream_focus_handoff_repair_item_count"
    ] = router["field_activation_upstream_focus_handoff_repair_item_count"]
    manifest[
        "latest_external_activation_router_field_activation_upstream_focus_handoff_repair_next_operator_action"
    ] = router["field_activation_upstream_focus_handoff_repair_next_operator_action"]
    manifest["latest_external_activation_router_ready_channel_ids"] = router["ready_channel_ids"]
    manifest["latest_external_activation_router_model_chain_ready_channel_ids"] = router[
        "model_chain_ready_channel_ids"
    ]
    manifest["latest_external_activation_router_handoff_ready_channel_ids"] = router[
        "handoff_ready_channel_ids"
    ]
    manifest["latest_external_activation_router_blocked_channel_ids"] = router["blocked_channel_ids"]
    manifest["latest_external_activation_router_priority_route_channel_id"] = router[
        "priority_route_channel_id"
    ]
    manifest["latest_external_activation_router_priority_route_status"] = router[
        "priority_route_status"
    ]
    manifest["latest_external_activation_router_priority_route_preflight_status"] = router[
        "priority_route_preflight_status"
    ]
    manifest["latest_external_activation_router_highest_priority_blocker"] = router[
        "highest_priority_blocker"
    ]
    manifest["latest_external_activation_router_next_operator_action"] = router[
        "next_operator_action"
    ]
    manifest["latest_external_activation_router_validation_command"] = router[
        "router_validation_command"
    ]
    manifest["latest_external_activation_router_boundary_preserved"] = router["boundary_preserved"]
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()

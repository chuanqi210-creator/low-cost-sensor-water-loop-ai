from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from water_ai.external_activation_operator_packet import (
    build_external_activation_operator_action_packet,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = PROJECT_ROOT / "deliverables" / "manifest.json"
CORE_GATE_PATH = PROJECT_ROOT / "outputs" / "model_core_governance" / "core_score_termination_gate.json"
EXTERNAL_ACTIVATION_ROUTER_PATH = (
    PROJECT_ROOT / "outputs" / "model_core_governance" / "external_activation_router.json"
)
CATALYST_RESPONSE_SUBMISSION_KIT_PATH = (
    PROJECT_ROOT
    / "outputs"
    / "catalyst_response_submission_kit"
    / "catalyst_response_submission_kit_metrics.json"
)
FOCUSED_CATALYST_RESPONSE_MERGE_PATH = (
    PROJECT_ROOT
    / "outputs"
    / "focused_catalyst_response_merge"
    / "focused_catalyst_response_merge_preflight.json"
)
FOCUSED_CATALYST_RESPONSE_TEMPLATE_PATH = (
    PROJECT_ROOT
    / "outputs"
    / "catalyst_response_submission_kit"
    / "focused_catalyst_response_template.json"
)
OUT_PATH = (
    PROJECT_ROOT
    / "outputs"
    / "model_core_governance"
    / "external_activation_operator_action_packet.json"
)
REPORT_PATH = (
    PROJECT_ROOT
    / "deliverables"
    / "model_core_optimization"
    / "external_activation_operator_action_packet.md"
)


def main() -> None:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    packet = build_external_activation_operator_action_packet(
        core_gate=_read_json(CORE_GATE_PATH),
        external_activation_router=_read_json(EXTERNAL_ACTIVATION_ROUTER_PATH),
        catalyst_response_submission_kit=_read_json(CATALYST_RESPONSE_SUBMISSION_KIT_PATH),
        focused_catalyst_response_merge=_read_json(FOCUSED_CATALYST_RESPONSE_MERGE_PATH),
        focused_catalyst_response_template=_read_json(FOCUSED_CATALYST_RESPONSE_TEMPLATE_PATH),
    )
    OUT_PATH.write_text(json.dumps(packet, ensure_ascii=False, indent=2), encoding="utf-8")
    REPORT_PATH.write_text(_report_md(packet), encoding="utf-8")
    _update_manifest(packet)

    print(f"External activation operator packet: {packet['packet_status']}")
    print(f"- target_hidden_state: {packet['target_hidden_state']}")
    print(f"- source_env_var: {packet['source_env_var']}")
    print(f"- expected_focused_response_row_count: {packet['expected_focused_response_row_count']}")
    print(f"- packet_next_operator_action: {packet['packet_next_operator_action']}")
    print(f"- next_operator_action: {packet['next_operator_action']}")
    print(f"- operator_packet_boundary_pass: {packet['operator_packet_boundary_pass']}")
    print(f"packet: {OUT_PATH}")
    print(f"report: {REPORT_PATH}")


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _report_md(packet: dict[str, Any]) -> str:
    lines = [
        "# External Activation Operator Action Packet",
        "",
        "## 定位",
        "",
        (
            "该包把当前最高优先外部动作压成一个可执行清单：填写 focused catalyst response、"
            "设置 `FOCUSED_CATALYST_RESPONSE_PATH`、运行 focused merge，再在预检通过后回填 "
            "`FIELD_ACTIVATION_RESPONSE_PATH`。它只是操作交接，不生成现场证据。"
        ),
        "",
        "## Current Action",
        "",
        f"- packet_id: `{packet['packet_id']}`",
        f"- packet_status: `{packet['packet_status']}`",
        f"- target_hidden_state: `{packet['target_hidden_state']}`",
        f"- source_env_var: `{packet['source_env_var']}`",
        f"- target_full_response_env_var: `{packet['target_full_response_env_var']}`",
        f"- focused_template_path: `{packet['focused_template_path']}`",
        f"- focused_schema_path: `{packet['focused_schema_path']}`",
        f"- focused_merge_plan_path: `{packet['focused_merge_plan_path']}`",
        f"- expected_focused_response_row_count: `{packet['expected_focused_response_row_count']}`",
        f"- template_evidence_row_count: `{packet['template_evidence_row_count']}`",
        f"- minimum_matched_batch_count: `{packet['minimum_matched_batch_count']}`",
        f"- focused_merge_preflight_status: `{packet['focused_merge_preflight_status']}`",
        f"- focused_candidate_availability_status: `{packet['focused_candidate_availability_status']}`",
        f"- focused_candidate_self_declared_submit_ready: `{packet['focused_candidate_self_declared_submit_ready']}`",
        f"- focused_candidate_operator_packet_submit_ready: `{packet['focused_candidate_operator_packet_submit_ready']}`",
        f"- focused_repair_work_order_status: `{packet['focused_repair_work_order_status']}`",
        f"- focused_repair_next_operator_action: `{packet['focused_repair_next_operator_action']}`",
        f"- packet_next_operator_action: `{packet['packet_next_operator_action']}`",
        f"- next_operator_action: `{packet['next_operator_action']}`",
        f"- operator_packet_boundary_pass: `{packet['operator_packet_boundary_pass']}`",
        "",
        "## Commands",
        "",
    ]
    for command in packet["current_commands"]:
        lines.append(f"- `{command}`")
    lines.extend(
        [
            "",
            "## Operator Steps",
            "",
            "| order | step | action | condition |",
            "| --- | --- | --- | --- |",
        ]
    )
    for step in packet["operator_steps"]:
        lines.append(
            "| {order} | `{step_id}` | `{action}` | {condition} |".format(
                order=step["order"],
                step_id=step["step_id"],
                action=step["action"],
                condition=step.get("condition", ""),
            )
        )
    lines.extend(
        [
            "",
            "## Boundary Checks",
            "",
            "| check | pass | detail |",
            "| --- | --- | --- |",
        ]
    )
    for check in packet["boundary_checks"]:
        lines.append(f"| `{check['check_id']}` | `{check['pass']}` | {check['detail']} |")
    lines.extend(
        [
            "",
            "## No-Write Boundary",
            "",
            packet["focused_candidate_use_boundary"],
            "",
            packet["no_write_boundary"],
            "",
            "## Rejection Boundaries",
            "",
        ]
    )
    for boundary in packet["rejection_boundaries"]:
        lines.append(f"- {boundary}")
    lines.append("")
    return "\n".join(lines)


def _update_manifest(packet: dict[str, Any]) -> None:
    manifest = _read_json(MANIFEST_PATH)
    manifest["latest_external_activation_operator_action_packet"] = str(
        OUT_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_external_activation_operator_action_packet_status"] = packet[
        "packet_status"
    ]
    manifest["latest_external_activation_operator_action_packet_target_hidden_state"] = (
        packet["target_hidden_state"]
    )
    manifest["latest_external_activation_operator_action_packet_source_env_var"] = packet[
        "source_env_var"
    ]
    manifest["latest_external_activation_operator_action_packet_next_operator_action"] = (
        packet["next_operator_action"]
    )
    manifest["latest_external_activation_operator_action_packet_focused_candidate_availability_status"] = (
        packet["focused_candidate_availability_status"]
    )
    manifest["latest_external_activation_operator_action_packet_focused_candidate_self_declared_submit_ready"] = (
        packet["focused_candidate_self_declared_submit_ready"]
    )
    manifest["latest_external_activation_operator_action_packet_focused_candidate_operator_packet_submit_ready"] = (
        packet["focused_candidate_operator_packet_submit_ready"]
    )
    manifest["latest_external_activation_operator_action_packet_boundary_pass"] = packet[
        "operator_packet_boundary_pass"
    ]
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()

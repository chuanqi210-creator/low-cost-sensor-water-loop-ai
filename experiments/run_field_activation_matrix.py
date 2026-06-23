from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from water_ai.field_activation_matrix import (
    audit_field_activation_response_coherence,
    build_field_activation_package_assembly_plan,
    build_field_activation_package_staging_manifest,
    build_field_activation_external_readiness_gate,
    build_field_activation_matrix,
    build_field_activation_response_completion_ledger,
    build_field_activation_response_focus_handoff,
    build_field_activation_response_repair_work_order,
    build_field_activation_response_submission_packet,
    build_field_activation_response_template,
    build_field_activation_schema_contract,
    preflight_field_activation_materialized_package,
    preflight_field_activation_response,
    preflight_field_activation_response_source,
    preflight_field_activation_schema_contract,
    preview_field_activation_downstream_path_endpoint_preflight,
    preview_field_activation_downstream_r7_preflight,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CORE_GATE_PATH = PROJECT_ROOT / "outputs" / "model_core_governance" / "core_score_termination_gate.json"
OUT_PATH = PROJECT_ROOT / "outputs" / "model_core_governance" / "field_activation_matrix.json"
RESPONSE_TEMPLATE_PATH = (
    PROJECT_ROOT / "outputs" / "model_core_governance" / "field_activation_response_template.json"
)
RESPONSE_PREFLIGHT_PATH = (
    PROJECT_ROOT / "outputs" / "model_core_governance" / "field_activation_response_preflight.json"
)
RESPONSE_COHERENCE_AUDIT_PATH = (
    PROJECT_ROOT / "outputs" / "model_core_governance" / "field_activation_response_coherence_audit.json"
)
RESPONSE_SOURCE_PREFLIGHT_PATH = (
    PROJECT_ROOT / "outputs" / "model_core_governance" / "field_activation_response_source_preflight.json"
)
RESPONSE_REPAIR_WORK_ORDER_PATH = (
    PROJECT_ROOT / "outputs" / "model_core_governance" / "field_activation_response_repair_work_order.json"
)
RESPONSE_COMPLETION_LEDGER_PATH = (
    PROJECT_ROOT / "outputs" / "model_core_governance" / "field_activation_response_completion_ledger.json"
)
RESPONSE_FOCUS_HANDOFF_PATH = (
    PROJECT_ROOT / "outputs" / "model_core_governance" / "field_activation_response_focus_handoff.json"
)
CATALYST_RESPONSE_SUBMISSION_KIT_METRICS_PATH = (
    PROJECT_ROOT / "outputs" / "catalyst_response_submission_kit" / "catalyst_response_submission_kit_metrics.json"
)
FOCUSED_CATALYST_RESPONSE_MERGE_PREFLIGHT_PATH = (
    PROJECT_ROOT
    / "outputs"
    / "focused_catalyst_response_merge"
    / "focused_catalyst_response_merge_preflight.json"
)
PACKAGE_ASSEMBLY_PLAN_PATH = (
    PROJECT_ROOT / "outputs" / "model_core_governance" / "field_activation_package_assembly_plan.json"
)
PACKAGE_STAGING_MANIFEST_PATH = (
    PROJECT_ROOT / "outputs" / "model_core_governance" / "field_activation_package_staging_manifest.json"
)
MATERIALIZED_PACKAGE_PREFLIGHT_PATH = (
    PROJECT_ROOT / "outputs" / "model_core_governance" / "field_activation_materialized_package_preflight.json"
)
DOWNSTREAM_R7_PREVIEW_PATH = (
    PROJECT_ROOT / "outputs" / "model_core_governance" / "field_activation_downstream_r7_preview.json"
)
DOWNSTREAM_PATH_ENDPOINT_PREVIEW_PATH = (
    PROJECT_ROOT
    / "outputs"
    / "model_core_governance"
    / "field_activation_downstream_path_endpoint_preview.json"
)
EXTERNAL_READINESS_GATE_PATH = (
    PROJECT_ROOT / "outputs" / "model_core_governance" / "field_activation_external_readiness_gate.json"
)
RESPONSE_SUBMISSION_PACKET_PATH = (
    PROJECT_ROOT / "outputs" / "model_core_governance" / "field_activation_response_submission_packet.json"
)
SCHEMA_CONTRACT_PATH = (
    PROJECT_ROOT / "outputs" / "model_core_governance" / "field_activation_schema_contract.json"
)
SCHEMA_PREFLIGHT_PATH = (
    PROJECT_ROOT / "outputs" / "model_core_governance" / "field_activation_schema_preflight.json"
)
EXTERNAL_ACTIVATION_CONTRACT_PATH = (
    PROJECT_ROOT / "outputs" / "model_core_governance" / "external_activation_contract.json"
)
DOC_PATH = PROJECT_ROOT / "deliverables" / "model_core_optimization" / "field_activation_matrix.md"
MANIFEST_PATH = PROJECT_ROOT / "deliverables" / "manifest.json"
FIELD_ACTIVATION_RESPONSE_PATH_ENV = "FIELD_ACTIVATION_RESPONSE_PATH"


def main() -> None:
    core_gate = json.loads(CORE_GATE_PATH.read_text(encoding="utf-8"))
    external_activation_contract = _read_optional_json(EXTERNAL_ACTIVATION_CONTRACT_PATH)
    matrix = build_field_activation_matrix(core_gate)
    response_template = build_field_activation_response_template(matrix)
    selected_response, response_source_preflight = _load_selected_response(response_template, matrix)
    response_preflight = preflight_field_activation_response(selected_response, matrix)
    response_completion_ledger = build_field_activation_response_completion_ledger(
        selected_response,
        matrix,
        response_source_preflight,
        response_preflight,
    )
    response_focus_handoff = build_field_activation_response_focus_handoff(
        response_completion_ledger,
        _read_optional_json(CATALYST_RESPONSE_SUBMISSION_KIT_METRICS_PATH),
        _read_optional_json(FOCUSED_CATALYST_RESPONSE_MERGE_PREFLIGHT_PATH),
    )
    response_coherence_audit = audit_field_activation_response_coherence(
        selected_response,
        matrix,
        response_preflight,
    )
    package_assembly_plan = build_field_activation_package_assembly_plan(
        selected_response,
        matrix,
        response_preflight,
        external_activation_contract,
        response_coherence_audit,
    )
    package_staging_manifest = build_field_activation_package_staging_manifest(
        selected_response,
        package_assembly_plan,
        response_preflight,
        response_source_preflight,
    )
    materialized_package_dir = _selected_materialized_package_dir(package_staging_manifest)
    materialized_package_preflight = preflight_field_activation_materialized_package(
        package_staging_manifest,
        package_dir_path=materialized_package_dir,
    )
    downstream_r7_preview = preview_field_activation_downstream_r7_preflight(
        package_staging_manifest,
        materialized_package_preflight,
        package_dir_path=materialized_package_dir,
    )
    downstream_path_endpoint_preview = preview_field_activation_downstream_path_endpoint_preflight(
        package_staging_manifest,
        materialized_package_preflight,
        package_dir_path=materialized_package_dir,
    )
    schema_contract = build_field_activation_schema_contract(
        matrix,
        response_template,
        package_assembly_plan,
    )
    schema_preflight = preflight_field_activation_schema_contract(
        schema_contract,
        selected_response,
        package_assembly_plan,
    )
    response_repair_work_order = build_field_activation_response_repair_work_order(
        response_source_preflight,
        response_preflight,
        schema_preflight,
        package_assembly_plan,
        response_coherence_audit,
    )
    external_readiness_gate = build_field_activation_external_readiness_gate(
        response_source_preflight,
        response_repair_work_order,
        response_preflight,
        package_assembly_plan,
        package_staging_manifest,
        materialized_package_preflight,
        schema_preflight,
        response_coherence_audit,
    )
    response_submission_packet = build_field_activation_response_submission_packet(
        response_template,
        response_source_preflight,
        response_repair_work_order,
        response_preflight,
        external_readiness_gate,
        response_template_path=str(RESPONSE_TEMPLATE_PATH.relative_to(PROJECT_ROOT)),
        response_coherence_audit=response_coherence_audit,
    )
    matrix["field_activation_response_template_path"] = str(RESPONSE_TEMPLATE_PATH.relative_to(PROJECT_ROOT))
    matrix["field_activation_response_source_preflight_path"] = str(
        RESPONSE_SOURCE_PREFLIGHT_PATH.relative_to(PROJECT_ROOT)
    )
    matrix["field_activation_response_repair_work_order_path"] = str(
        RESPONSE_REPAIR_WORK_ORDER_PATH.relative_to(PROJECT_ROOT)
    )
    matrix["field_activation_response_preflight_path"] = str(RESPONSE_PREFLIGHT_PATH.relative_to(PROJECT_ROOT))
    matrix["field_activation_response_completion_ledger_path"] = str(
        RESPONSE_COMPLETION_LEDGER_PATH.relative_to(PROJECT_ROOT)
    )
    matrix["field_activation_response_focus_handoff_path"] = str(
        RESPONSE_FOCUS_HANDOFF_PATH.relative_to(PROJECT_ROOT)
    )
    matrix["field_activation_response_coherence_audit_path"] = str(
        RESPONSE_COHERENCE_AUDIT_PATH.relative_to(PROJECT_ROOT)
    )
    matrix["field_activation_package_assembly_plan_path"] = str(
        PACKAGE_ASSEMBLY_PLAN_PATH.relative_to(PROJECT_ROOT)
    )
    matrix["field_activation_package_staging_manifest_path"] = str(
        PACKAGE_STAGING_MANIFEST_PATH.relative_to(PROJECT_ROOT)
    )
    matrix["field_activation_materialized_package_preflight_path"] = str(
        MATERIALIZED_PACKAGE_PREFLIGHT_PATH.relative_to(PROJECT_ROOT)
    )
    matrix["field_activation_downstream_r7_preview_path"] = str(
        DOWNSTREAM_R7_PREVIEW_PATH.relative_to(PROJECT_ROOT)
    )
    matrix["field_activation_downstream_path_endpoint_preview_path"] = str(
        DOWNSTREAM_PATH_ENDPOINT_PREVIEW_PATH.relative_to(PROJECT_ROOT)
    )
    matrix["field_activation_external_readiness_gate_path"] = str(
        EXTERNAL_READINESS_GATE_PATH.relative_to(PROJECT_ROOT)
    )
    matrix["field_activation_response_submission_packet_path"] = str(
        RESPONSE_SUBMISSION_PACKET_PATH.relative_to(PROJECT_ROOT)
    )
    matrix["field_activation_schema_contract_path"] = str(SCHEMA_CONTRACT_PATH.relative_to(PROJECT_ROOT))
    matrix["field_activation_schema_preflight_path"] = str(SCHEMA_PREFLIGHT_PATH.relative_to(PROJECT_ROOT))
    matrix["field_activation_response_source_preflight"] = response_source_preflight
    matrix["field_activation_response_repair_work_order"] = response_repair_work_order
    matrix["field_activation_response_preflight"] = response_preflight
    matrix["field_activation_response_completion_ledger"] = response_completion_ledger
    matrix["field_activation_response_focus_handoff"] = response_focus_handoff
    matrix["field_activation_response_coherence_audit"] = response_coherence_audit
    matrix["field_activation_package_assembly_plan"] = package_assembly_plan
    matrix["field_activation_package_staging_manifest"] = package_staging_manifest
    matrix["field_activation_materialized_package_preflight"] = materialized_package_preflight
    matrix["field_activation_downstream_r7_preview"] = downstream_r7_preview
    matrix["field_activation_downstream_path_endpoint_preview"] = downstream_path_endpoint_preview
    matrix["field_activation_external_readiness_gate"] = external_readiness_gate
    matrix["field_activation_response_submission_packet"] = response_submission_packet
    matrix["field_activation_schema_contract"] = schema_contract
    matrix["field_activation_schema_preflight"] = schema_preflight
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    DOC_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(matrix, ensure_ascii=False, indent=2), encoding="utf-8")
    RESPONSE_TEMPLATE_PATH.write_text(
        json.dumps(response_template, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    RESPONSE_SOURCE_PREFLIGHT_PATH.write_text(
        json.dumps(response_source_preflight, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    RESPONSE_REPAIR_WORK_ORDER_PATH.write_text(
        json.dumps(response_repair_work_order, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    RESPONSE_PREFLIGHT_PATH.write_text(
        json.dumps(response_preflight, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    RESPONSE_COMPLETION_LEDGER_PATH.write_text(
        json.dumps(response_completion_ledger, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    RESPONSE_FOCUS_HANDOFF_PATH.write_text(
        json.dumps(response_focus_handoff, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    RESPONSE_COHERENCE_AUDIT_PATH.write_text(
        json.dumps(response_coherence_audit, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    PACKAGE_ASSEMBLY_PLAN_PATH.write_text(
        json.dumps(package_assembly_plan, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    PACKAGE_STAGING_MANIFEST_PATH.write_text(
        json.dumps(package_staging_manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    MATERIALIZED_PACKAGE_PREFLIGHT_PATH.write_text(
        json.dumps(materialized_package_preflight, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    DOWNSTREAM_R7_PREVIEW_PATH.write_text(
        json.dumps(downstream_r7_preview, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    DOWNSTREAM_PATH_ENDPOINT_PREVIEW_PATH.write_text(
        json.dumps(downstream_path_endpoint_preview, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    EXTERNAL_READINESS_GATE_PATH.write_text(
        json.dumps(external_readiness_gate, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    RESPONSE_SUBMISSION_PACKET_PATH.write_text(
        json.dumps(response_submission_packet, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    SCHEMA_CONTRACT_PATH.write_text(
        json.dumps(schema_contract, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    SCHEMA_PREFLIGHT_PATH.write_text(
        json.dumps(schema_preflight, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    DOC_PATH.write_text(_matrix_md(matrix), encoding="utf-8")
    _update_manifest(matrix)
    print(matrix["readiness"]["interface_status"])
    print(response_source_preflight["source_preflight_status"])
    print(response_repair_work_order["work_order_status"])
    print(response_preflight["preflight_status"])
    print(response_completion_ledger["ledger_status"])
    print(response_focus_handoff["handoff_status"])
    print(response_coherence_audit["audit_status"])
    print(package_assembly_plan["assembly_status"])
    print(package_staging_manifest["staging_status"])
    print(materialized_package_preflight["preflight_status"])
    print(downstream_r7_preview["preview_status"])
    print(downstream_path_endpoint_preview["preview_status"])
    print(external_readiness_gate["gate_status"])
    print(response_submission_packet["packet_status"])
    print(schema_preflight["schema_preflight_status"])
    print(f"field_activation_matrix: {OUT_PATH}")
    print(f"field_activation_matrix_doc: {DOC_PATH}")
    print(f"field_activation_response_template: {RESPONSE_TEMPLATE_PATH}")
    print(f"field_activation_response_source_preflight: {RESPONSE_SOURCE_PREFLIGHT_PATH}")
    print(f"field_activation_response_repair_work_order: {RESPONSE_REPAIR_WORK_ORDER_PATH}")
    print(f"field_activation_response_preflight: {RESPONSE_PREFLIGHT_PATH}")
    print(f"field_activation_response_completion_ledger: {RESPONSE_COMPLETION_LEDGER_PATH}")
    print(f"field_activation_response_focus_handoff: {RESPONSE_FOCUS_HANDOFF_PATH}")
    print(f"field_activation_response_coherence_audit: {RESPONSE_COHERENCE_AUDIT_PATH}")
    print(f"field_activation_package_assembly_plan: {PACKAGE_ASSEMBLY_PLAN_PATH}")
    print(f"field_activation_package_staging_manifest: {PACKAGE_STAGING_MANIFEST_PATH}")
    print(f"field_activation_materialized_package_preflight: {MATERIALIZED_PACKAGE_PREFLIGHT_PATH}")
    print(f"field_activation_downstream_r7_preview: {DOWNSTREAM_R7_PREVIEW_PATH}")
    print(f"field_activation_downstream_path_endpoint_preview: {DOWNSTREAM_PATH_ENDPOINT_PREVIEW_PATH}")
    print(f"field_activation_external_readiness_gate: {EXTERNAL_READINESS_GATE_PATH}")
    print(f"field_activation_response_submission_packet: {RESPONSE_SUBMISSION_PACKET_PATH}")
    print(f"field_activation_schema_contract: {SCHEMA_CONTRACT_PATH}")
    print(f"field_activation_schema_preflight: {SCHEMA_PREFLIGHT_PATH}")


def _matrix_md(matrix: dict[str, Any]) -> str:
    readiness = matrix["readiness"]
    lines = [
        "# Field Activation Matrix",
        "",
        "## 定位",
        "",
        (
            "该接口把 Agent50 的隐藏状态 ledger 与外部证据通道连接起来，"
            "用于回答：每个不可直接观测状态需要补哪些真实字段，补完后能恢复哪段 replay/holdout/review 链路。"
        ),
        "",
        "## Readiness",
        "",
        f"- interface_status: `{readiness['interface_status']}`",
        f"- hidden_state_row_count: `{readiness['hidden_state_row_count']}`",
        f"- hidden_state_row_coverage: `{readiness['hidden_state_row_coverage']}`",
        f"- activation_ready_state_count: `{readiness['activation_ready_state_count']}`",
        f"- field_validated_state_count: `{readiness['field_validated_state_count']}`",
        f"- control_ready_state_count: `{readiness['control_ready_state_count']}`",
        f"- can_resume_model_chain: `{readiness['can_resume_model_chain']}`",
        f"- can_write_to_actuator: `{readiness['can_write_to_actuator']}`",
        f"- can_write_to_release_gate: `{readiness['can_write_to_release_gate']}`",
        f"- response_source_preflight_status: `{matrix['field_activation_response_source_preflight']['source_preflight_status']}`",
        f"- external_response_supplied: `{matrix['field_activation_response_source_preflight']['external_response_supplied']}`",
        f"- response_repair_work_order_status: `{matrix['field_activation_response_repair_work_order']['work_order_status']}`",
        f"- response_repair_item_count: `{matrix['field_activation_response_repair_work_order']['repair_item_count']}`",
        f"- response_preflight_status: `{matrix['field_activation_response_preflight']['preflight_status']}`",
        f"- response_template_marker_row_count: `{matrix['field_activation_response_preflight']['template_marker_row_count']}`",
        (
            "- response_missing_value_payload_row_count: "
            f"`{matrix['field_activation_response_preflight']['missing_value_payload_row_count']}`"
        ),
        (
            "- response_template_value_payload_row_count: "
            f"`{matrix['field_activation_response_preflight']['template_value_payload_row_count']}`"
        ),
        (
            "- response_completion_ledger_status: "
            f"`{matrix['field_activation_response_completion_ledger']['ledger_status']}`"
        ),
        (
            "- response_completion_ratio: "
            f"`{matrix['field_activation_response_completion_ledger']['completion_ratio']}`"
        ),
        (
            "- response_completed_row_count: "
            f"`{matrix['field_activation_response_completion_ledger']['completed_response_row_count']}`"
        ),
        (
            "- response_next_hidden_state_focus: "
            f"`{matrix['field_activation_response_completion_ledger']['next_hidden_state_focus']}`"
        ),
        (
            "- response_completion_next_operator_action: "
            f"`{matrix['field_activation_response_completion_ledger']['next_operator_action']}`"
        ),
        (
            "- response_focus_handoff_status: "
            f"`{matrix['field_activation_response_focus_handoff']['handoff_status']}`"
        ),
        (
            "- response_focus_handoff_target_hidden_state: "
            f"`{matrix['field_activation_response_focus_handoff']['target_hidden_state']}`"
        ),
        (
            "- response_focus_handoff_row_scan_reduction_ratio: "
            f"`{matrix['field_activation_response_focus_handoff']['row_scan_reduction_ratio']}`"
        ),
        (
            "- response_focus_handoff_next_operator_action: "
            f"`{matrix['field_activation_response_focus_handoff']['next_operator_action']}`"
        ),
        (
            "- response_focus_handoff_repair_work_order_status: "
            f"`{matrix['field_activation_response_focus_handoff']['focused_repair_work_order_status']}`"
        ),
        (
            "- response_focus_handoff_repair_item_count: "
            f"`{matrix['field_activation_response_focus_handoff']['focused_repair_item_count']}`"
        ),
        f"- response_coherence_audit_status: `{matrix['field_activation_response_coherence_audit']['audit_status']}`",
        (
            "- response_coherence_hard_blocker_count: "
            f"`{matrix['field_activation_response_coherence_audit']['hard_blocker_count']}`"
        ),
        (
            "- response_coherence_warning_count: "
            f"`{matrix['field_activation_response_coherence_audit']['warning_count']}`"
        ),
        f"- package_assembly_status: `{matrix['field_activation_package_assembly_plan']['assembly_status']}`",
        f"- package_staging_status: `{matrix['field_activation_package_staging_manifest']['staging_status']}`",
        (
            "- package_staging_selected_channel_count: "
            f"`{matrix['field_activation_package_staging_manifest']['selected_channel_manifest_count']}`"
        ),
        (
            "- package_staging_selected_row_blueprint_count: "
            f"`{matrix['field_activation_package_staging_manifest']['selected_row_blueprint_count']}`"
        ),
        (
            "- package_staging_selected_value_payload_mapping_count: "
            f"`{matrix['field_activation_package_staging_manifest']['selected_value_payload_mapping_count']}`"
        ),
        (
            "- materialized_package_preflight_status: "
            f"`{matrix['field_activation_materialized_package_preflight']['preflight_status']}`"
        ),
        (
            "- materialized_package_blocker_count: "
            f"`{matrix['field_activation_materialized_package_preflight']['blocker_count']}`"
        ),
        (
            "- materialized_package_blueprint_missing_row_count: "
            f"`{matrix['field_activation_materialized_package_preflight']['blueprint_missing_row_count']}`"
        ),
        (
            "- materialized_package_next_operator_action: "
            f"`{matrix['field_activation_materialized_package_preflight']['next_operator_action']}`"
        ),
        (
            "- downstream_r7_preview_status: "
            f"`{matrix['field_activation_downstream_r7_preview']['preview_status']}`"
        ),
        (
            "- downstream_r7_preview_executed: "
            f"`{matrix['field_activation_downstream_r7_preview']['preview_executed']}`"
        ),
        (
            "- downstream_r7_preview_metric_evaluation_status: "
            f"`{matrix['field_activation_downstream_r7_preview']['preview_metric_evaluation_status']}`"
        ),
        (
            "- downstream_r7_can_pass_to_timestamped_replay: "
            f"`{matrix['field_activation_downstream_r7_preview']['downstream_r7_can_pass_to_timestamped_replay']}`"
        ),
        (
            "- downstream_r7_highest_priority_blocker: "
            f"`{matrix['field_activation_downstream_r7_preview']['highest_priority_blocker']}`"
        ),
        (
            "- downstream_r7_next_operator_action: "
            f"`{matrix['field_activation_downstream_r7_preview']['next_operator_action']}`"
        ),
        (
            "- downstream_path_endpoint_preview_status: "
            f"`{matrix['field_activation_downstream_path_endpoint_preview']['preview_status']}`"
        ),
        (
            "- downstream_path_endpoint_preview_executed: "
            f"`{matrix['field_activation_downstream_path_endpoint_preview']['preview_executed']}`"
        ),
        (
            "- downstream_path_endpoint_preview_metric_evaluation_status: "
            f"`{matrix['field_activation_downstream_path_endpoint_preview']['preview_metric_evaluation_status']}`"
        ),
        (
            "- downstream_path_endpoint_required_table_count: "
            f"`{matrix['field_activation_downstream_path_endpoint_preview']['path_endpoint_required_table_count']}`"
        ),
        (
            "- downstream_path_endpoint_contract_minimum_matched_batch_count: "
            f"`{matrix['field_activation_downstream_path_endpoint_preview']['path_endpoint_contract_minimum_matched_batch_count']}`"
        ),
        (
            "- downstream_path_endpoint_can_route_to_field_layout_holdout: "
            f"`{matrix['field_activation_downstream_path_endpoint_preview']['downstream_path_endpoint_can_route_to_field_layout_holdout']}`"
        ),
        (
            "- downstream_path_endpoint_highest_priority_blocker: "
            f"`{matrix['field_activation_downstream_path_endpoint_preview']['highest_priority_blocker']}`"
        ),
        (
            "- downstream_path_endpoint_next_operator_action: "
            f"`{matrix['field_activation_downstream_path_endpoint_preview']['next_operator_action']}`"
        ),
        (
            "- external_readiness_gate_status: "
            f"`{matrix['field_activation_external_readiness_gate']['gate_status']}`"
        ),
        (
            "- external_readiness_first_blocked_step: "
            f"`{matrix['field_activation_external_readiness_gate']['first_blocked_step']}`"
        ),
        (
            "- external_readiness_next_operator_action: "
            f"`{matrix['field_activation_external_readiness_gate']['next_operator_action']}`"
        ),
        (
            "- response_submission_packet_status: "
            f"`{matrix['field_activation_response_submission_packet']['packet_status']}`"
        ),
        (
            "- response_submission_next_operator_action: "
            f"`{matrix['field_activation_response_submission_packet']['next_operator_action']}`"
        ),
        f"- schema_preflight_status: `{matrix['field_activation_schema_preflight']['schema_preflight_status']}`",
        (
            "- schema_can_validate_response_structure: "
            f"`{matrix['field_activation_schema_preflight']['can_validate_field_activation_response_structure']}`"
        ),
        "",
        "## Method Contract",
        "",
        f"- technical_problem: {matrix['method_contract']['technical_problem']}",
        f"- technical_means: {matrix['method_contract']['technical_means']}",
        f"- technical_effect: {matrix['method_contract']['technical_effect']}",
        f"- evidence_boundary: {matrix['method_contract']['evidence_boundary']}",
        "",
        "## State Rows",
        "",
        "| hidden_state | activation_status | required_channels | first evidence fields | resumes_to |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in matrix["state_activation_rows"]:
        fields = ", ".join(row["required_field_evidence"][:4])
        channels = ", ".join(row["required_channels"])
        resumes = ", ".join(row["resumes_to"][:3])
        lines.append(
            f"| `{row['hidden_state']}` | `{row['activation_status']}` | {channels} | {fields} | {resumes} |"
        )
    lines.extend(
        [
            "",
            "## No-Write Boundary",
            "",
            matrix["writeback_policy"]["boundary"],
            "",
            "## Response Package",
            "",
        f"- template: `{matrix['field_activation_response_template_path']}`",
        f"- source preflight: `{matrix['field_activation_response_source_preflight_path']}`",
        f"- repair work order: `{matrix['field_activation_response_repair_work_order_path']}`",
        f"- preflight: `{matrix['field_activation_response_preflight_path']}`",
        f"- completion ledger: `{matrix['field_activation_response_completion_ledger_path']}`",
        f"- focus handoff: `{matrix['field_activation_response_focus_handoff_path']}`",
        f"- coherence audit: `{matrix['field_activation_response_coherence_audit_path']}`",
        f"- package assembly plan: `{matrix['field_activation_package_assembly_plan_path']}`",
        f"- package staging manifest: `{matrix['field_activation_package_staging_manifest_path']}`",
        f"- materialized package preflight: `{matrix['field_activation_materialized_package_preflight_path']}`",
        f"- downstream R7 preview: `{matrix['field_activation_downstream_r7_preview_path']}`",
        f"- downstream path/endpoint preview: `{matrix['field_activation_downstream_path_endpoint_preview_path']}`",
        f"- external readiness gate: `{matrix['field_activation_external_readiness_gate_path']}`",
        f"- response submission packet: `{matrix['field_activation_response_submission_packet_path']}`",
        f"- schema contract: `{matrix['field_activation_schema_contract_path']}`",
        f"- schema preflight: `{matrix['field_activation_schema_preflight_path']}`",
        (
            "- 当前 template 预检默认被阻断，这是正确状态：现场人员必须把 TODO 行替换为真实 field "
            "batch/timestamp/node/sensor/lab/operation 证据后才能进入外部包预检。"
        ),
        (
            "- schema preflight 只证明字段结构和 no-write flags 合格；它允许模板标记存在，"
            "但不能证明现场证据成立。"
        ),
        (
            "- coherence audit 会在包组装前检查 batch/node/sensor/chain-of-custody/lab method 是否能形成"
            "可回放证据组；它只做一致性和工程可拼接性审计，不把响应包升级为现场结论。"
        ),
        (
            f"- 如果已有填写后的响应包，设置 `{FIELD_ACTIVATION_RESPONSE_PATH_ENV}=/path/to/response.json` "
            "后重跑该脚本；source preflight 只检查文件可读和根结构，证据成立仍以 response preflight 为准。"
        ),
        (
            "- 如果已经按 staging manifest 整理出现场包目录，设置对应 package pointer 环境变量"
            "（例如 `REAL_FIELD_REPLAY_PACKAGE_DIR=/path/to/package_dir`）后重跑该脚本；"
            "materialized package preflight 会检查 metadata.json、CSV 表、必需字段、模板标记和 field provenance。"
        ),
        (
            "- downstream R7 preview 会用同一个 materialized package 只读调用 Agent44 field replay package "
            "preflight，提前暴露缺表、类型、必需字段或 batch linkage 问题；它不会恢复模型链，也不会写入控制或放行。"
        ),
        (
            "- downstream path/endpoint preview 会用同一个 materialized package 只读调用 Agent54 "
            "field path/endpoint label preflight，提前暴露路径阶段、最终出水终点标签、共同 batch 和 "
            "release gate 端点证据缺口；它不会恢复模型链，也不会写入控制或放行。"
        ),
        ]
    )
    return "\n".join(lines)


def _update_manifest(matrix: dict[str, Any]) -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    readiness = matrix["readiness"]
    manifest["latest_field_activation_matrix"] = str(OUT_PATH.relative_to(PROJECT_ROOT))
    manifest["latest_field_activation_matrix_doc"] = str(DOC_PATH.relative_to(PROJECT_ROOT))
    manifest["latest_field_activation_matrix_status"] = readiness["interface_status"]
    manifest["latest_field_activation_matrix_hidden_state_row_count"] = readiness[
        "hidden_state_row_count"
    ]
    manifest["latest_field_activation_matrix_can_resume_model_chain"] = readiness[
        "can_resume_model_chain"
    ]
    manifest["latest_field_activation_matrix_can_write_to_actuator"] = readiness[
        "can_write_to_actuator"
    ]
    manifest["latest_field_activation_matrix_can_write_to_release_gate"] = readiness[
        "can_write_to_release_gate"
    ]
    manifest["latest_field_activation_matrix_required_channel_ids"] = readiness[
        "required_channel_ids"
    ]
    manifest["latest_field_activation_matrix_next_operator_actions"] = matrix[
        "next_operator_actions"
    ]
    source_preflight = matrix["field_activation_response_source_preflight"]
    manifest["latest_field_activation_response_source_preflight"] = str(
        RESPONSE_SOURCE_PREFLIGHT_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_field_activation_response_source_preflight_status"] = source_preflight[
        "source_preflight_status"
    ]
    manifest["latest_field_activation_response_source_external_response_supplied"] = source_preflight[
        "external_response_supplied"
    ]
    manifest["latest_field_activation_response_source_can_run_response_preflight"] = source_preflight[
        "can_run_response_preflight"
    ]
    manifest["latest_field_activation_response_source_env_var"] = FIELD_ACTIVATION_RESPONSE_PATH_ENV
    repair_work_order = matrix["field_activation_response_repair_work_order"]
    manifest["latest_field_activation_response_repair_work_order"] = str(
        RESPONSE_REPAIR_WORK_ORDER_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_field_activation_response_repair_work_order_status"] = repair_work_order[
        "work_order_status"
    ]
    manifest["latest_field_activation_response_repair_item_count"] = repair_work_order[
        "repair_item_count"
    ]
    manifest["latest_field_activation_response_repair_highest_priority_repair_id"] = repair_work_order[
        "highest_priority_repair_id"
    ]
    manifest["latest_field_activation_response_repair_next_operator_action"] = repair_work_order[
        "next_operator_action"
    ]
    preflight = matrix["field_activation_response_preflight"]
    manifest["latest_field_activation_response_template"] = str(
        RESPONSE_TEMPLATE_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_field_activation_response_preflight"] = str(
        RESPONSE_PREFLIGHT_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_field_activation_response_preflight_status"] = preflight[
        "preflight_status"
    ]
    manifest["latest_field_activation_response_expected_row_count"] = preflight[
        "expected_response_row_count"
    ]
    manifest["latest_field_activation_response_template_marker_row_count"] = preflight[
        "template_marker_row_count"
    ]
    manifest["latest_field_activation_response_can_route_to_external_activation_router"] = preflight[
        "can_route_to_external_activation_router"
    ]
    completion_ledger = matrix["field_activation_response_completion_ledger"]
    manifest["latest_field_activation_response_completion_ledger"] = str(
        RESPONSE_COMPLETION_LEDGER_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_field_activation_response_completion_ledger_status"] = completion_ledger[
        "ledger_status"
    ]
    manifest["latest_field_activation_response_completion_ratio"] = completion_ledger[
        "completion_ratio"
    ]
    manifest["latest_field_activation_response_completed_row_count"] = completion_ledger[
        "completed_response_row_count"
    ]
    manifest["latest_field_activation_response_incomplete_row_count"] = completion_ledger[
        "incomplete_response_row_count"
    ]
    manifest["latest_field_activation_response_next_hidden_state_focus"] = completion_ledger[
        "next_hidden_state_focus"
    ]
    manifest["latest_field_activation_response_completion_next_operator_action"] = completion_ledger[
        "next_operator_action"
    ]
    focus_handoff = matrix["field_activation_response_focus_handoff"]
    manifest["latest_field_activation_response_focus_handoff"] = str(
        RESPONSE_FOCUS_HANDOFF_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_field_activation_response_focus_handoff_status"] = focus_handoff[
        "handoff_status"
    ]
    manifest["latest_field_activation_response_focus_handoff_target_hidden_state"] = focus_handoff[
        "target_hidden_state"
    ]
    manifest["latest_field_activation_response_focus_handoff_row_scan_reduction_ratio"] = focus_handoff[
        "row_scan_reduction_ratio"
    ]
    manifest["latest_field_activation_response_focus_handoff_next_operator_action"] = focus_handoff[
        "next_operator_action"
    ]
    manifest["latest_field_activation_response_focus_handoff_repair_work_order_status"] = focus_handoff[
        "focused_repair_work_order_status"
    ]
    manifest["latest_field_activation_response_focus_handoff_repair_item_count"] = focus_handoff[
        "focused_repair_item_count"
    ]
    manifest["latest_field_activation_response_focus_handoff_repair_next_operator_action"] = focus_handoff[
        "focused_repair_next_operator_action"
    ]
    manifest["latest_field_activation_response_focus_handoff_source_env_var"] = focus_handoff[
        "focused_merge_source_env_var"
    ]
    manifest["latest_field_activation_response_focus_handoff_can_submit_to_external_activation_router"] = (
        focus_handoff["can_submit_to_external_activation_router"]
    )
    coherence = matrix["field_activation_response_coherence_audit"]
    manifest["latest_field_activation_response_coherence_audit"] = str(
        RESPONSE_COHERENCE_AUDIT_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_field_activation_response_coherence_audit_status"] = coherence[
        "audit_status"
    ]
    manifest["latest_field_activation_response_coherence_hard_blocker_count"] = coherence[
        "hard_blocker_count"
    ]
    manifest["latest_field_activation_response_coherence_warning_count"] = coherence[
        "warning_count"
    ]
    manifest["latest_field_activation_response_coherence_highest_priority_blocker"] = coherence[
        "highest_priority_blocker"
    ]
    manifest["latest_field_activation_response_coherence_next_operator_action"] = coherence[
        "next_operator_action"
    ]
    manifest["latest_field_activation_response_coherence_can_route_to_package_assembly"] = coherence[
        "can_route_to_package_assembly"
    ]
    assembly = matrix["field_activation_package_assembly_plan"]
    manifest["latest_field_activation_package_assembly_plan"] = str(
        PACKAGE_ASSEMBLY_PLAN_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_field_activation_package_assembly_status"] = assembly[
        "assembly_status"
    ]
    manifest["latest_field_activation_package_assembly_channel_plan_count"] = assembly[
        "channel_plan_count"
    ]
    manifest["latest_field_activation_package_assembly_table_plan_count"] = assembly[
        "table_plan_count"
    ]
    manifest["latest_field_activation_package_assembly_candidate_channel_plan_count"] = assembly[
        "candidate_channel_plan_count"
    ]
    manifest["latest_field_activation_package_assembly_candidate_table_plan_count"] = assembly[
        "candidate_table_plan_count"
    ]
    manifest["latest_field_activation_package_assembly_can_stage_external_package_candidates"] = assembly[
        "can_stage_external_package_candidates"
    ]
    staging = matrix["field_activation_package_staging_manifest"]
    manifest["latest_field_activation_package_staging_manifest"] = str(
        PACKAGE_STAGING_MANIFEST_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_field_activation_package_staging_status"] = staging[
        "staging_status"
    ]
    manifest["latest_field_activation_package_staging_selected_channel_manifest_count"] = staging[
        "selected_channel_manifest_count"
    ]
    manifest["latest_field_activation_package_staging_candidate_channel_requirement_count"] = staging[
        "candidate_channel_requirement_count"
    ]
    manifest["latest_field_activation_package_staging_can_materialize_no_write_package_candidates"] = staging[
        "can_materialize_no_write_package_candidates"
    ]
    manifest["latest_field_activation_package_staging_next_operator_action"] = staging[
        "next_operator_action"
    ]
    manifest["latest_field_activation_package_staging_package_pointers_to_set"] = staging[
        "package_pointers_to_set"
    ]
    materialized_preflight = matrix["field_activation_materialized_package_preflight"]
    manifest["latest_field_activation_materialized_package_preflight"] = str(
        MATERIALIZED_PACKAGE_PREFLIGHT_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_field_activation_materialized_package_preflight_status"] = materialized_preflight[
        "preflight_status"
    ]
    manifest["latest_field_activation_materialized_package_preflight_package_pointer"] = (
        materialized_preflight["package_pointer"]
    )
    manifest["latest_field_activation_materialized_package_preflight_blocker_count"] = materialized_preflight[
        "blocker_count"
    ]
    manifest["latest_field_activation_materialized_package_preflight_highest_priority_blocker"] = (
        materialized_preflight["highest_priority_blocker"]
    )
    manifest["latest_field_activation_materialized_package_preflight_next_operator_action"] = (
        materialized_preflight["next_operator_action"]
    )
    manifest["latest_field_activation_materialized_package_preflight_can_route_to_external_activation_router"] = (
        materialized_preflight["can_route_to_external_activation_router"]
    )
    manifest["latest_field_activation_materialized_package_preflight_can_resume_model_chain"] = materialized_preflight[
        "can_resume_model_chain"
    ]
    manifest["latest_field_activation_materialized_package_preflight_can_write_to_actuator"] = materialized_preflight[
        "can_write_to_actuator"
    ]
    manifest["latest_field_activation_materialized_package_preflight_can_write_to_release_gate"] = materialized_preflight[
        "can_write_to_release_gate"
    ]
    downstream_r7_preview = matrix["field_activation_downstream_r7_preview"]
    manifest["latest_field_activation_downstream_r7_preview"] = str(
        DOWNSTREAM_R7_PREVIEW_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_field_activation_downstream_r7_preview_status"] = downstream_r7_preview[
        "preview_status"
    ]
    manifest["latest_field_activation_downstream_r7_preview_executed"] = downstream_r7_preview[
        "preview_executed"
    ]
    manifest["latest_field_activation_downstream_r7_preview_metric_evaluation_status"] = downstream_r7_preview[
        "preview_metric_evaluation_status"
    ]
    manifest["latest_field_activation_downstream_r7_not_evaluated_metric_count"] = len(
        downstream_r7_preview["not_evaluated_metric_names"]
    )
    manifest["latest_field_activation_downstream_r7_preflight_status"] = downstream_r7_preview[
        "r7_preflight_status"
    ]
    manifest["latest_field_activation_downstream_r7_agent44_import_status"] = downstream_r7_preview[
        "r7_agent44_import_status"
    ]
    manifest["latest_field_activation_downstream_r7_can_pass_to_timestamped_replay"] = downstream_r7_preview[
        "downstream_r7_can_pass_to_timestamped_replay"
    ]
    manifest["latest_field_activation_downstream_r7_highest_priority_blocker"] = downstream_r7_preview[
        "highest_priority_blocker"
    ]
    manifest["latest_field_activation_downstream_r7_next_operator_action"] = downstream_r7_preview[
        "next_operator_action"
    ]
    manifest["latest_field_activation_downstream_r7_can_resume_model_chain"] = downstream_r7_preview[
        "can_resume_model_chain"
    ]
    manifest["latest_field_activation_downstream_r7_can_write_to_actuator"] = downstream_r7_preview[
        "can_write_to_actuator"
    ]
    manifest["latest_field_activation_downstream_r7_can_write_to_release_gate"] = downstream_r7_preview[
        "can_write_to_release_gate"
    ]
    downstream_path_endpoint_preview = matrix["field_activation_downstream_path_endpoint_preview"]
    manifest["latest_field_activation_downstream_path_endpoint_preview"] = str(
        DOWNSTREAM_PATH_ENDPOINT_PREVIEW_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_field_activation_downstream_path_endpoint_preview_status"] = (
        downstream_path_endpoint_preview["preview_status"]
    )
    manifest["latest_field_activation_downstream_path_endpoint_preview_executed"] = (
        downstream_path_endpoint_preview["preview_executed"]
    )
    manifest["latest_field_activation_downstream_path_endpoint_preview_metric_evaluation_status"] = (
        downstream_path_endpoint_preview["preview_metric_evaluation_status"]
    )
    manifest["latest_field_activation_downstream_path_endpoint_not_evaluated_metric_count"] = len(
        downstream_path_endpoint_preview["not_evaluated_metric_names"]
    )
    manifest["latest_field_activation_downstream_path_endpoint_required_table_count"] = (
        downstream_path_endpoint_preview["path_endpoint_required_table_count"]
    )
    manifest["latest_field_activation_downstream_path_endpoint_contract_minimum_matched_batch_count"] = (
        downstream_path_endpoint_preview["path_endpoint_contract_minimum_matched_batch_count"]
    )
    manifest["latest_field_activation_downstream_path_endpoint_preflight_status"] = (
        downstream_path_endpoint_preview["path_endpoint_preflight_status"]
    )
    manifest["latest_field_activation_downstream_path_endpoint_matched_batch_count"] = (
        downstream_path_endpoint_preview["path_endpoint_matched_batch_count"]
    )
    manifest["latest_field_activation_downstream_path_endpoint_required_matched_batch_deficit"] = (
        downstream_path_endpoint_preview["path_endpoint_required_matched_batch_deficit"]
    )
    manifest["latest_field_activation_downstream_path_endpoint_can_route_to_field_layout_holdout"] = (
        downstream_path_endpoint_preview["downstream_path_endpoint_can_route_to_field_layout_holdout"]
    )
    manifest["latest_field_activation_downstream_path_endpoint_highest_priority_blocker"] = (
        downstream_path_endpoint_preview["highest_priority_blocker"]
    )
    manifest["latest_field_activation_downstream_path_endpoint_next_operator_action"] = (
        downstream_path_endpoint_preview["next_operator_action"]
    )
    manifest["latest_field_activation_downstream_path_endpoint_can_resume_model_chain"] = (
        downstream_path_endpoint_preview["can_resume_model_chain"]
    )
    manifest["latest_field_activation_downstream_path_endpoint_can_write_to_actuator"] = (
        downstream_path_endpoint_preview["can_write_to_actuator"]
    )
    manifest["latest_field_activation_downstream_path_endpoint_can_write_to_release_gate"] = (
        downstream_path_endpoint_preview["can_write_to_release_gate"]
    )
    external_readiness_gate = matrix["field_activation_external_readiness_gate"]
    manifest["latest_field_activation_external_readiness_gate"] = str(
        EXTERNAL_READINESS_GATE_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_field_activation_external_readiness_gate_status"] = external_readiness_gate[
        "gate_status"
    ]
    manifest["latest_field_activation_external_readiness_first_blocked_step"] = external_readiness_gate[
        "first_blocked_step"
    ]
    manifest["latest_field_activation_external_readiness_highest_priority_blocker"] = external_readiness_gate[
        "highest_priority_blocker"
    ]
    manifest["latest_field_activation_external_readiness_next_operator_action"] = external_readiness_gate[
        "next_operator_action"
    ]
    manifest["latest_field_activation_external_readiness_ready_step_count"] = external_readiness_gate[
        "ready_step_count"
    ]
    manifest["latest_field_activation_external_readiness_blocked_step_count"] = external_readiness_gate[
        "blocked_step_count"
    ]
    manifest["latest_field_activation_external_readiness_can_submit_to_external_activation_router"] = (
        external_readiness_gate["can_submit_to_external_activation_router"]
    )
    manifest["latest_field_activation_external_readiness_can_resume_model_chain"] = external_readiness_gate[
        "can_resume_model_chain"
    ]
    manifest["latest_field_activation_external_readiness_can_write_to_actuator"] = external_readiness_gate[
        "can_write_to_actuator"
    ]
    manifest["latest_field_activation_external_readiness_can_write_to_release_gate"] = external_readiness_gate[
        "can_write_to_release_gate"
    ]
    submission_packet = matrix["field_activation_response_submission_packet"]
    manifest["latest_field_activation_response_submission_packet"] = str(
        RESPONSE_SUBMISSION_PACKET_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_field_activation_response_submission_packet_status"] = submission_packet[
        "packet_status"
    ]
    manifest["latest_field_activation_response_submission_packet_next_operator_action"] = submission_packet[
        "next_operator_action"
    ]
    manifest["latest_field_activation_response_submission_packet_highest_priority_blocker"] = (
        submission_packet["highest_priority_blocker"]
    )
    manifest["latest_field_activation_response_submission_packet_source_env_var"] = submission_packet[
        "source_env_var"
    ]
    manifest["latest_field_activation_response_submission_packet_can_submit_to_response_preflight"] = (
        submission_packet["can_submit_to_response_preflight"]
    )
    manifest["latest_field_activation_response_submission_packet_can_route_to_external_activation_router"] = (
        submission_packet["can_route_to_external_activation_router"]
    )
    manifest["latest_field_activation_response_submission_packet_can_resume_model_chain"] = submission_packet[
        "can_resume_model_chain"
    ]
    manifest["latest_field_activation_response_submission_packet_can_write_to_actuator"] = submission_packet[
        "can_write_to_actuator"
    ]
    manifest["latest_field_activation_response_submission_packet_can_write_to_release_gate"] = submission_packet[
        "can_write_to_release_gate"
    ]
    schema = matrix["field_activation_schema_preflight"]
    manifest["latest_field_activation_schema_contract"] = str(
        SCHEMA_CONTRACT_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_field_activation_schema_preflight"] = str(
        SCHEMA_PREFLIGHT_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_field_activation_schema_preflight_status"] = schema[
        "schema_preflight_status"
    ]
    manifest["latest_field_activation_schema_can_validate_response_structure"] = schema[
        "can_validate_field_activation_response_structure"
    ]
    manifest["latest_field_activation_schema_can_resume_model_chain"] = schema[
        "can_resume_model_chain"
    ]
    manifest["latest_field_activation_schema_can_write_to_actuator"] = schema[
        "can_write_to_actuator"
    ]
    manifest["latest_field_activation_schema_can_write_to_release_gate"] = schema[
        "can_write_to_release_gate"
    ]
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def _load_selected_response(
    response_template: dict[str, Any],
    matrix: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    source_path = os.environ.get(FIELD_ACTIVATION_RESPONSE_PATH_ENV, "").strip()
    if not source_path:
        source_preflight = preflight_field_activation_response_source(
            source_path="",
            load_status="field_activation_response_source_not_supplied",
            response=response_template,
            default_response_template=response_template,
            matrix=matrix,
        )
        return response_template, source_preflight

    path = Path(source_path).expanduser()
    if not path.is_absolute():
        path = (PROJECT_ROOT / path).resolve()
    if not path.exists():
        response: dict[str, Any] = {}
        load_status = "field_activation_response_source_file_missing"
    else:
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            response = {}
            load_status = "field_activation_response_source_invalid_json"
        else:
            if isinstance(loaded, dict):
                response = loaded
                load_status = "field_activation_response_source_loaded"
            else:
                response = {}
                load_status = "field_activation_response_source_root_not_object"

    source_preflight = preflight_field_activation_response_source(
        source_path=str(path),
        load_status=load_status,
        response=response,
        default_response_template=response_template,
        matrix=matrix,
    )
    return response, source_preflight


def _selected_materialized_package_dir(staging_manifest: dict[str, Any]) -> str:
    pointers = staging_manifest.get("package_pointers_to_set", [])
    if isinstance(pointers, list):
        for pointer in pointers:
            value = os.environ.get(str(pointer), "").strip()
            if value:
                return value
    return os.environ.get("FIELD_ACTIVATION_MATERIALIZED_PACKAGE_DIR", "").strip()


def _read_optional_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()

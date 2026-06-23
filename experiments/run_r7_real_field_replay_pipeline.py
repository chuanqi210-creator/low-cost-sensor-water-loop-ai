from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from water_ai.agents.field_replay_import_agent import write_field_replay_package_template
from water_ai.real_field_replay_pipeline import build_real_field_replay_pipeline


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = PROJECT_ROOT / "deliverables" / "manifest.json"
MATRIX_FAST_PROXY_METRICS = PROJECT_ROOT / "outputs" / "matrix_shock_fast_proxy" / "fast_proxy_metrics.json"
SOFT_SENSOR_FIELD_HOLDOUT_METRICS = (
    PROJECT_ROOT / "outputs" / "soft_sensor_field_holdout_gate" / "field_holdout_gate_metrics.json"
)
CLAIM_PACKAGE_METRICS = PROJECT_ROOT / "outputs" / "claim_specific_field_package" / "claim_specific_field_package_metrics.json"
CATALYST_PROXY_METRICS = PROJECT_ROOT / "outputs" / "catalyst_activity_proxy" / "catalyst_activity_proxy_metrics.json"
MULTI_FACILITY_REPLAY_EVALUATION_METRICS = (
    PROJECT_ROOT / "outputs" / "multi_facility_replay_evaluation" / "replay_evaluation_metrics.json"
)
UNIFIED_FIELD_EVIDENCE_GATE_METRICS = (
    PROJECT_ROOT / "outputs" / "unified_field_evidence_gate" / "unified_field_evidence_gate_metrics.json"
)
OUT_DIR = PROJECT_ROOT / "outputs" / "r7_real_field_replay_pipeline"
DELIVERABLE_PATH = PROJECT_ROOT / "deliverables" / "model_core_optimization" / "r7_real_field_replay_pipeline.md"
TEMPLATE_DIR = PROJECT_ROOT / "outputs" / "field_replay_import" / "real_field_package_template"
PIPELINE_METRICS = OUT_DIR / "r7_real_field_replay_pipeline_metrics.json"
PIPELINE_REPORT = OUT_DIR / "r7_real_field_replay_pipeline_report.md"
SUBMISSION_REPAIR_WORK_ORDER = OUT_DIR / "field_package_submission_repair_work_order.json"
SUBMISSION_REPAIR_RESPONSE_TEMPLATE = OUT_DIR / "field_package_submission_repair_response_template.json"
SUBMISSION_REPAIR_RESPONSE_PREFLIGHT = OUT_DIR / "field_package_submission_repair_response_preflight.json"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DELIVERABLE_PATH.parent.mkdir(parents=True, exist_ok=True)
    package_dir, source_type = _resolve_package_dir()
    result = build_real_field_replay_pipeline(
        package_dir,
        matrix_fast_proxy_metrics=_read_json(MATRIX_FAST_PROXY_METRICS),
        soft_sensor_field_holdout_gate_metrics=_read_json(SOFT_SENSOR_FIELD_HOLDOUT_METRICS),
        claim_specific_package_metrics=_read_json(CLAIM_PACKAGE_METRICS),
        catalyst_proxy_metrics=_read_json(CATALYST_PROXY_METRICS),
        multi_facility_replay_evaluation_metrics=_read_json(MULTI_FACILITY_REPLAY_EVALUATION_METRICS),
        unified_field_evidence_gate_metrics=_read_json(UNIFIED_FIELD_EVIDENCE_GATE_METRICS),
        field_package_submission_repair_response=_resolve_repair_response(),
    )
    result["source_package_type"] = source_type
    PIPELINE_METRICS.write_text(json.dumps(_strip_normalized(result), ensure_ascii=False, indent=2), encoding="utf-8")
    repair_work_order = result["field_package_submission_readiness"]["field_package_submission_repair_work_order"]
    SUBMISSION_REPAIR_WORK_ORDER.write_text(
        json.dumps(repair_work_order, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    SUBMISSION_REPAIR_RESPONSE_TEMPLATE.write_text(
        json.dumps(result["field_package_submission_repair_response_template"], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    SUBMISSION_REPAIR_RESPONSE_PREFLIGHT.write_text(
        json.dumps(result["field_package_submission_repair_response_preflight"], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    PIPELINE_REPORT.write_text(_report_md(result), encoding="utf-8")
    DELIVERABLE_PATH.write_text(_deliverable_md(result), encoding="utf-8")
    _update_manifest(result)

    readiness = result["pipeline_readiness"]
    print(f"R7 real field replay pipeline: {readiness['r7_status']}")
    print(f"- source_package_type: {source_type}")
    print(f"- import: {readiness['field_replay_import_status']}")
    print(f"- chain: {readiness['field_replay_evidence_chain_status']}")
    print(f"- submission_repair_work_order: {readiness['field_package_submission_repair_work_order_status']}")
    print(
        "- submission_repair_response_preflight: "
        f"{readiness['field_package_submission_repair_response_preflight_status']}"
    )
    print(f"- next: {readiness['r7_next_action']}")
    print(f"report: {PIPELINE_REPORT}")
    print(f"metrics: {PIPELINE_METRICS}")
    print(f"repair_work_order: {SUBMISSION_REPAIR_WORK_ORDER}")
    print(f"repair_response_template: {SUBMISSION_REPAIR_RESPONSE_TEMPLATE}")
    print(f"repair_response_preflight: {SUBMISSION_REPAIR_RESPONSE_PREFLIGHT}")


def _resolve_package_dir() -> tuple[Path, str]:
    env_path = os.environ.get("REAL_FIELD_REPLAY_PACKAGE_DIR", "").strip()
    if env_path:
        package_dir = Path(env_path).expanduser().resolve()
        if not package_dir.exists():
            raise FileNotFoundError(f"REAL_FIELD_REPLAY_PACKAGE_DIR does not exist: {package_dir}")
        if not package_dir.is_dir():
            raise NotADirectoryError(f"REAL_FIELD_REPLAY_PACKAGE_DIR is not a directory: {package_dir}")
        return package_dir, "user_provided_field_package"
    write_field_replay_package_template(TEMPLATE_DIR)
    return TEMPLATE_DIR, "header_only_template_preflight"


def _resolve_repair_response() -> dict[str, Any] | None:
    env_path = os.environ.get("FIELD_PACKAGE_SUBMISSION_REPAIR_RESPONSE_PATH", "").strip()
    if not env_path:
        return None
    path = Path(env_path).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(f"FIELD_PACKAGE_SUBMISSION_REPAIR_RESPONSE_PATH does not exist: {path}")
    if not path.is_file():
        raise IsADirectoryError(f"FIELD_PACKAGE_SUBMISSION_REPAIR_RESPONSE_PATH is not a file: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError("FIELD_PACKAGE_SUBMISSION_REPAIR_RESPONSE_PATH must point to a JSON object")
    return payload


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _report_md(result: dict[str, Any]) -> str:
    readiness = result["pipeline_readiness"]
    preflight = result["preflight"]
    coverage = result["field_package_coverage"]
    coverage_readiness = coverage["readiness"]
    patch_plan = coverage.get("patch_plan", {})
    repair_work_order = result["field_package_submission_readiness"]["field_package_submission_repair_work_order"]
    repair_response_preflight = result["field_package_submission_repair_response_preflight"]
    r7 = result["r7_acceptance"]["readiness"]
    lines = [
        "# R7 Real Field Replay Pipeline 报告",
        "",
        f"- source_package_type：`{result['source_package_type']}`",
        f"- package_dir：`{result['package_dir']}`",
        f"- submission_readiness_status：`{readiness['field_package_submission_readiness_status']}`",
        f"- submission_highest_priority_blocker：`{readiness['field_package_submission_highest_priority_blocker']}`",
        f"- submission_next_operator_action：`{readiness['field_package_submission_next_operator_action']}`",
        f"- submission_blocking_stage_count：`{readiness['field_package_submission_blocking_stage_count']}`",
        f"- submission_can_submit_to_agent42_smoke_replay：`{readiness['field_package_submission_can_submit_to_agent42_smoke_replay']}`",
        f"- submission_can_route_to_path_endpoint_layout_holdout：`{readiness['field_package_submission_can_route_to_path_endpoint_layout_holdout']}`",
        f"- submission_no_write_boundary_pass：`{readiness['field_package_submission_no_write_boundary_pass']}`",
        f"- submission_repair_work_order_status：`{readiness['field_package_submission_repair_work_order_status']}`",
        f"- submission_repair_item_count：`{readiness['field_package_submission_repair_item_count']}`",
        f"- submission_repair_work_order_path：`{SUBMISSION_REPAIR_WORK_ORDER.relative_to(PROJECT_ROOT)}`",
        f"- submission_repair_response_preflight_status：`{readiness['field_package_submission_repair_response_preflight_status']}`",
        f"- submission_repair_response_missing_item_count：`{readiness['field_package_submission_repair_response_missing_item_count']}`",
        f"- submission_repair_response_template_marker_count：`{readiness['field_package_submission_repair_response_template_marker_count']}`",
        f"- submission_repair_response_can_route_to_r7_preflight：`{readiness['field_package_submission_repair_response_can_route_to_r7_preflight']}`",
        f"- submission_repair_response_template_path：`{SUBMISSION_REPAIR_RESPONSE_TEMPLATE.relative_to(PROJECT_ROOT)}`",
        f"- submission_repair_response_preflight_path：`{SUBMISSION_REPAIR_RESPONSE_PREFLIGHT.relative_to(PROJECT_ROOT)}`",
        f"- preflight_status：`{preflight['status']}`",
        f"- field_replay_import_status：`{readiness['field_replay_import_status']}`",
        f"- field_replay_evidence_chain_status：`{readiness['field_replay_evidence_chain_status']}`",
        f"- field_package_coverage_status：`{coverage_readiness['field_package_coverage_status']}`",
        f"- claim_specific_coverage_rate：`{coverage_readiness['claim_specific_coverage_rate']}`",
        f"- soft_holdout_coverage_pass：`{coverage_readiness['soft_holdout_coverage_pass']}`",
        f"- field_proxy_holdout_status：`{readiness['field_proxy_holdout_status']}`",
        f"- field_proxy_holdout_required：`{readiness['field_proxy_holdout_required']}`",
        f"- field_proxy_holdout_coverage_pass：`{readiness['field_proxy_holdout_coverage_pass']}`",
        f"- field_proxy_holdout_matched_batch_count：`{readiness['field_proxy_holdout_matched_batch_count']}`",
        f"- pressure_source_conflict_count：`{readiness['pressure_source_conflict_count']}`",
        f"- resolved_pressure_source_conflict_count：`{readiness['resolved_pressure_source_conflict_count']}`",
        f"- unresolved_pressure_source_conflict_count：`{readiness['unresolved_pressure_source_conflict_count']}`",
        f"- pressure_source_resolution_record_count：`{readiness['pressure_source_resolution_record_count']}`",
        f"- pressure_source_conflict_requires_operator_review：`{readiness['pressure_source_conflict_requires_operator_review']}`",
        f"- field_package_pressure_conflict_resolution_status：`{readiness['field_package_pressure_conflict_resolution_status']}`",
        f"- field_package_pressure_conflict_resolution_ready：`{readiness['field_package_pressure_conflict_resolution_ready']}`",
        f"- agent51_field_proxy_summary_status：`{readiness['agent51_field_proxy_summary_status']}`",
        f"- agent51_field_proxy_scoreable_batch_count：`{readiness['agent51_field_proxy_scoreable_batch_count']}`",
        f"- agent51_field_proxy_validation_pass：`{readiness['agent51_field_proxy_validation_pass']}`",
        f"- agent51_field_proxy_holdout_mae：`{readiness['agent51_field_proxy_holdout_mae']}`",
        f"- agent51_field_proxy_label_correlation：`{readiness['agent51_field_proxy_label_correlation']}`",
        f"- multi_facility_control_promotion_pass：`{readiness['multi_facility_control_promotion_pass']}`",
        f"- catalyst_proxy_field_validation_pass：`{readiness['catalyst_proxy_field_validation_pass']}`",
        f"- minimum_replay_contract_status：`{readiness['minimum_replay_contract_status']}`",
        f"- field_evidence_sufficiency_status：`{readiness['field_evidence_sufficiency_status']}`",
        f"- field_evidence_sufficiency_score：`{readiness['field_evidence_sufficiency_score']}`",
        f"- field_evidence_smoke_pass：`{readiness['field_evidence_smoke_pass']}`",
        f"- field_evidence_calibration_volume_pass：`{readiness['field_evidence_calibration_volume_pass']}`",
        f"- can_route_to_agent42_smoke_replay：`{readiness['can_route_to_agent42_smoke_replay']}`",
        f"- can_route_to_field_holdout：`{readiness['can_route_to_field_holdout']}`",
        f"- field_path_endpoint_label_preflight_status：`{readiness['field_path_endpoint_label_preflight_status']}`",
        f"- field_path_endpoint_matched_batch_count：`{readiness['field_path_endpoint_matched_batch_count']}`",
        f"- field_path_endpoint_minimum_matched_batch_count：`{readiness['field_path_endpoint_minimum_matched_batch_count']}`",
        f"- field_path_endpoint_missing_tables：`{readiness['field_path_endpoint_missing_tables']}`",
        f"- field_path_endpoint_required_field_gap_count：`{readiness['field_path_endpoint_required_field_gap_count']}`",
        f"- field_path_endpoint_template_marker_count：`{readiness['field_path_endpoint_template_marker_count']}`",
        f"- field_path_endpoint_table_row_counts：`{readiness['field_path_endpoint_table_row_counts']}`",
        f"- field_path_endpoint_table_batch_counts：`{readiness['field_path_endpoint_table_batch_counts']}`",
        f"- field_path_endpoint_batch_alignment_gap_count：`{readiness['field_path_endpoint_batch_alignment_gap_count']}`",
        f"- field_path_endpoint_required_matched_batch_deficit：`{readiness['field_path_endpoint_required_matched_batch_deficit']}`",
        f"- field_path_endpoint_alignment_patch_plan_status：`{readiness['field_path_endpoint_alignment_patch_plan_status']}`",
        f"- field_path_endpoint_alignment_patch_plan_item_count：`{readiness['field_path_endpoint_alignment_patch_plan_item_count']}`",
        f"- field_path_endpoint_label_package_ready：`{readiness['field_path_endpoint_label_package_ready']}`",
        f"- field_path_endpoint_final_effluent_label_ready：`{readiness['field_path_endpoint_final_effluent_label_ready']}`",
        f"- can_route_to_field_layout_holdout_with_path_labels：`{readiness['can_route_to_field_layout_holdout_with_path_labels']}`",
        f"- release_gate_endpoint_label_blocked：`{readiness['release_gate_endpoint_label_blocked']}`",
        f"- can_route_to_human_review_candidate：`{readiness['can_route_to_human_review_candidate']}`",
        f"- field_supported_claim_upgrade_ready：`{readiness['field_supported_claim_upgrade_ready']}`",
        f"- minimum_common_batch_count：`{readiness['minimum_common_batch_count']}`",
        f"- minimum_valid_matched_batch_count：`{readiness['minimum_valid_matched_batch_count']}`",
        f"- minimum_valid_operation_action_count：`{readiness['minimum_valid_operation_action_count']}`",
        f"- minimum_invalid_operation_action_count：`{readiness['minimum_invalid_operation_action_count']}`",
        f"- minimum_valid_lab_result_count：`{readiness['minimum_valid_lab_result_count']}`",
        f"- minimum_invalid_lab_result_count：`{readiness['minimum_invalid_lab_result_count']}`",
        f"- minimum_proxy_event_count：`{readiness['minimum_proxy_event_count']}`",
        f"- minimum_valid_proxy_label_count：`{readiness['minimum_valid_proxy_label_count']}`",
        f"- minimum_invalid_proxy_label_count：`{readiness['minimum_invalid_proxy_label_count']}`",
        f"- minimum_pressure_headloss_event_count：`{readiness['minimum_pressure_headloss_event_count']}`",
        f"- minimum_valid_pressure_headloss_event_count：`{readiness['minimum_valid_pressure_headloss_event_count']}`",
        f"- minimum_invalid_pressure_headloss_event_count：`{readiness['minimum_invalid_pressure_headloss_event_count']}`",
        f"- minimum_valid_pressure_headloss_batch_count：`{readiness['minimum_valid_pressure_headloss_batch_count']}`",
        f"- minimum_time_order_violation_count：`{readiness['minimum_time_order_violation_count']}`",
        f"- patch_plan_status：`{patch_plan.get('patch_plan_status', 'unknown')}`",
        f"- patch_plan_item_count：`{patch_plan.get('item_count', 0)}`",
        f"- r7_status：`{readiness['r7_status']}`",
        f"- r7_score：`{readiness['r7_score']}`",
        f"- next_action：`{readiness['r7_next_action']}`",
        f"- can_emit_protective_control_candidate：`{readiness['can_emit_protective_control_candidate']}`",
        f"- can_write_to_actuator：`{readiness['can_write_to_actuator']}`",
        f"- can_write_to_release_gate：`{readiness['can_write_to_release_gate']}`",
        "",
        "## Preflight Next Actions",
        "",
    ]
    for action in preflight.get("next_actions", []):
        lines.append(f"- {action}")
    lines.extend(
        [
            "",
            "## Coverage Next Actions",
            "",
        ]
    )
    for action in coverage.get("next_actions", []):
        lines.append(f"- {action}")
    lines.extend(
        [
            "",
            "## Coverage Patch Plan",
            "",
        ]
    )
    for item in patch_plan.get("items", []):
        lines.append(
            f"- `{item.get('item_id')}`：{item.get('action')}；target="
            f"{item.get('target_file') or item.get('target_table') or item.get('need_id') or '-'}"
        )
    if not patch_plan.get("items"):
        lines.append("- No coverage patch item before replay/holdout gates.")
    lines.extend(
        [
            "",
            "## Submission Repair Work Order",
            "",
            f"- status：`{repair_work_order['work_order_status']}`",
            f"- highest_priority_blocker：`{repair_work_order['highest_priority_blocker']}`",
            f"- next_operator_action：`{repair_work_order['next_operator_action']}`",
            f"- repair_item_count：`{repair_work_order['repair_item_count']}`",
        ]
    )
    for item in repair_work_order.get("repair_items", [])[:10]:
        lines.append(
            f"- `{item.get('work_item_id')}`：{item.get('action')}；"
            f"target=`{item.get('target')}`；stage=`{item.get('source_stage_id')}`"
        )
    if repair_work_order.get("repair_item_count", 0) > 10:
        lines.append(f"- ... plus {repair_work_order['repair_item_count'] - 10} additional repair items.")
    lines.extend(
        [
            "",
            "## Submission Repair Response Preflight",
            "",
            f"- status：`{repair_response_preflight['preflight_status']}`",
            f"- required_work_item_count：`{repair_response_preflight['required_work_item_count']}`",
            f"- response_row_count：`{repair_response_preflight['response_row_count']}`",
            f"- submitted_item_count：`{repair_response_preflight['submitted_item_count']}`",
            f"- blocked_item_count：`{repair_response_preflight['blocked_item_count']}`",
            f"- template_marker_count：`{repair_response_preflight['template_marker_count']}`",
            f"- can_route_to_r7_preflight：`{repair_response_preflight['can_route_to_r7_preflight']}`",
            f"- next_operator_action：`{repair_response_preflight['next_operator_action']}`",
        ]
    )
    lines.extend(
        [
            "",
            "## R7 Failed Stages",
            "",
        ]
    )
    for stage_id in r7.get("failed_stage_ids", []):
        lines.append(f"- `{stage_id}`")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- This pipeline does not write actuator policy.",
            "- This pipeline does not write automatic release-gate policy.",
            "- Header-only templates and synthetic packages remain field-validation-required.",
        ]
    )
    return "\n".join(lines)


def _deliverable_md(result: dict[str, Any]) -> str:
    readiness = result["pipeline_readiness"]
    patch_plan = result["field_package_coverage"].get("patch_plan", {})
    repair_work_order = result["field_package_submission_readiness"]["field_package_submission_repair_work_order"]
    repair_response_preflight = result["field_package_submission_repair_response_preflight"]
    lines = [
        "# R7 真实 Field Replay 端到端管线",
        "",
        "该管线把一个 package directory 直接送入 Agent44 preflight/import、Agent45 内部 Agent42/43 replay/G6，"
        "再进入 R7 acceptance gate。它用于定位真实现场包卡在哪一段，不会自动写执行器或 release gate。",
        "",
        f"- 当前 source_package_type：`{result['source_package_type']}`",
        f"- 当前 package_dir：`{result['package_dir']}`",
        f"- Submission readiness：`{readiness['field_package_submission_readiness_status']}`，highest_blocker=`{readiness['field_package_submission_highest_priority_blocker']}`，next_action=`{readiness['field_package_submission_next_operator_action']}`，blocking_stage_count=`{readiness['field_package_submission_blocking_stage_count']}`，agent42_smoke_submission=`{readiness['field_package_submission_can_submit_to_agent42_smoke_replay']}`，path_endpoint_layout_holdout=`{readiness['field_package_submission_can_route_to_path_endpoint_layout_holdout']}`，no_write=`{readiness['field_package_submission_no_write_boundary_pass']}`",
        f"- Submission repair work order：`{readiness['field_package_submission_repair_work_order_status']}`，repair_item_count=`{readiness['field_package_submission_repair_item_count']}`，path=`{SUBMISSION_REPAIR_WORK_ORDER.relative_to(PROJECT_ROOT)}`",
        f"- Submission repair response preflight：`{readiness['field_package_submission_repair_response_preflight_status']}`，missing_items=`{readiness['field_package_submission_repair_response_missing_item_count']}`，template_markers=`{readiness['field_package_submission_repair_response_template_marker_count']}`，route_to_r7_preflight=`{readiness['field_package_submission_repair_response_can_route_to_r7_preflight']}`",
        f"- R7 状态：`{readiness['r7_status']}`",
        f"- Coverage 状态：`{readiness['field_package_coverage_status']}`",
        f"- Agent51 catalyst proxy holdout：`{readiness['field_proxy_holdout_status']}`，required=`{readiness['field_proxy_holdout_required']}`，pass=`{readiness['field_proxy_holdout_coverage_pass']}`，matched_batch_count=`{readiness['field_proxy_holdout_matched_batch_count']}`",
        f"- 压力源冲突补丁：conflict_count=`{readiness['pressure_source_conflict_count']}`，resolved=`{readiness['resolved_pressure_source_conflict_count']}`，unresolved=`{readiness['unresolved_pressure_source_conflict_count']}`，resolution_records=`{readiness['pressure_source_resolution_record_count']}`，operator_review=`{readiness['pressure_source_conflict_requires_operator_review']}`，resolution_status=`{readiness['field_package_pressure_conflict_resolution_status']}`，resolution_ready=`{readiness['field_package_pressure_conflict_resolution_ready']}`",
        f"- Agent51 holdout summary：`{readiness['agent51_field_proxy_summary_status']}`，scoreable_batch_count=`{readiness['agent51_field_proxy_scoreable_batch_count']}`，validation_pass=`{readiness['agent51_field_proxy_validation_pass']}`，holdout_mae=`{readiness['agent51_field_proxy_holdout_mae']}`，label_correlation=`{readiness['agent51_field_proxy_label_correlation']}`",
        f"- 多设施控制晋级：control_promotion_pass=`{readiness['multi_facility_control_promotion_pass']}`，catalyst_proxy_field_validation_pass=`{readiness['catalyst_proxy_field_validation_pass']}`",
        f"- 最小 replay 契约：`{readiness['minimum_replay_contract_status']}`，common_batch_count=`{readiness['minimum_common_batch_count']}`，valid_matched_batch_count=`{readiness['minimum_valid_matched_batch_count']}`，valid_operation_actions=`{readiness['minimum_valid_operation_action_count']}`，valid_lab_results=`{readiness['minimum_valid_lab_result_count']}`，valid_proxy_labels=`{readiness['minimum_valid_proxy_label_count']}`，valid_pressure_headloss_events=`{readiness['minimum_valid_pressure_headloss_event_count']}`，valid_pressure_headloss_batches=`{readiness['minimum_valid_pressure_headloss_batch_count']}`，time_order_violations=`{readiness['minimum_time_order_violation_count']}`",
        f"- Field evidence sufficiency：`{readiness['field_evidence_sufficiency_status']}`，score=`{readiness['field_evidence_sufficiency_score']}`，smoke_pass=`{readiness['field_evidence_smoke_pass']}`，calibration_volume_pass=`{readiness['field_evidence_calibration_volume_pass']}`，agent42_smoke=`{readiness['can_route_to_agent42_smoke_replay']}`，field_holdout=`{readiness['can_route_to_field_holdout']}`，human_review_candidate=`{readiness['can_route_to_human_review_candidate']}`，field_claim_upgrade_ready=`{readiness['field_supported_claim_upgrade_ready']}`",
        f"- Field path/endpoint labels：`{readiness['field_path_endpoint_label_preflight_status']}`，matched_batch_count=`{readiness['field_path_endpoint_matched_batch_count']}`，minimum=`{readiness['field_path_endpoint_minimum_matched_batch_count']}`，required_deficit=`{readiness['field_path_endpoint_required_matched_batch_deficit']}`，batch_alignment_gap_count=`{readiness['field_path_endpoint_batch_alignment_gap_count']}`，alignment_patch_plan=`{readiness['field_path_endpoint_alignment_patch_plan_status']}`，alignment_patch_items=`{readiness['field_path_endpoint_alignment_patch_plan_item_count']}`，ready=`{readiness['field_path_endpoint_label_package_ready']}`，layout_holdout_with_path_labels=`{readiness['can_route_to_field_layout_holdout_with_path_labels']}`，release_endpoint_blocked=`{readiness['release_gate_endpoint_label_blocked']}`",
        f"- Patch plan：`{patch_plan.get('patch_plan_status', 'unknown')}`，item_count=`{patch_plan.get('item_count', 0)}`",
        f"- 下一步：`{readiness['r7_next_action']}`",
        "",
        "## 使用方式",
        "",
        "```bash",
        "REAL_FIELD_REPLAY_PACKAGE_DIR=/path/to/field_package .venv/bin/python experiments/run_r7_real_field_replay_pipeline.py",
        "```",
        "",
        "如果不设置 `REAL_FIELD_REPLAY_PACKAGE_DIR`，脚本只会使用 header-only template 做 preflight 演练，不产生 field evidence。",
        "",
        "## 输出文件",
        "",
        f"- pipeline report：`{PIPELINE_REPORT.relative_to(PROJECT_ROOT)}`",
        f"- pipeline metrics：`{PIPELINE_METRICS.relative_to(PROJECT_ROOT)}`",
        f"- submission repair work order：`{SUBMISSION_REPAIR_WORK_ORDER.relative_to(PROJECT_ROOT)}`",
        f"- submission repair response template：`{SUBMISSION_REPAIR_RESPONSE_TEMPLATE.relative_to(PROJECT_ROOT)}`",
        f"- submission repair response preflight：`{SUBMISSION_REPAIR_RESPONSE_PREFLIGHT.relative_to(PROJECT_ROOT)}`",
        "",
        "## 当前补包计划",
        "",
    ]
    for item in patch_plan.get("items", []):
        lines.append(
            f"- `{item.get('item_id')}`：{item.get('action')}；"
            f"target=`{item.get('target_file') or item.get('target_table') or item.get('need_id') or '-'}`"
        )
    if not patch_plan.get("items"):
        lines.append("- 当前 coverage 层没有补包项，可进入 replay、soft holdout 和人工复核门控。")
    lines.extend(
        [
            "",
            "## 当前 Submission Repair Work Order",
            "",
            f"- status：`{repair_work_order['work_order_status']}`",
            f"- highest_blocker：`{repair_work_order['highest_priority_blocker']}`",
            f"- next_operator_action：`{repair_work_order['next_operator_action']}`",
        ]
    )
    for item in repair_work_order.get("repair_items", [])[:10]:
        lines.append(
            f"- `{item.get('work_item_id')}`：{item.get('action')}；"
            f"target=`{item.get('target')}`；stage=`{item.get('source_stage_id')}`"
        )
    if repair_work_order.get("repair_item_count", 0) > 10:
        lines.append(f"- ... plus {repair_work_order['repair_item_count'] - 10} additional repair items.")
    lines.extend(
        [
            "",
            "## 当前 Submission Repair Response Preflight",
            "",
            f"- status：`{repair_response_preflight['preflight_status']}`",
            f"- submitted_item_count：`{repair_response_preflight['submitted_item_count']}`",
            f"- blocked_item_count：`{repair_response_preflight['blocked_item_count']}`",
            f"- template_marker_count：`{repair_response_preflight['template_marker_count']}`",
            f"- can_route_to_r7_preflight：`{repair_response_preflight['can_route_to_r7_preflight']}`",
            f"- next_operator_action：`{repair_response_preflight['next_operator_action']}`",
        ]
    )
    lines.extend(
        [
            "",
            "## 边界",
            "",
            "- 只有真实 `data_origin=field`、真实 provenance 和真实 timestamped rows 才能进入 field replay。",
            "- 即使 Agent44/45/R7 局部通过，也必须继续通过 soft holdout、claim-specific rows、unified evidence gate 和人工复核。",
            "- 该管线永远不自动写入执行器策略或自动放行门。",
        ]
    )
    return "\n".join(lines)


def _update_manifest(result: dict[str, Any]) -> None:
    manifest = _read_json(MANIFEST_PATH)
    readiness = result["pipeline_readiness"]
    manifest["status"] = (
        "R7 real field replay pipeline 已生成，并已接入 R7j Agent51 catalyst proxy field holdout 审计"
    )
    manifest["r7_real_field_replay_pipeline"] = {
        "r7_real_field_replay_pipeline": str(DELIVERABLE_PATH.relative_to(PROJECT_ROOT)),
        "pipeline_report": str(PIPELINE_REPORT.relative_to(PROJECT_ROOT)),
        "pipeline_metrics": str(PIPELINE_METRICS.relative_to(PROJECT_ROOT)),
        "submission_repair_work_order": str(SUBMISSION_REPAIR_WORK_ORDER.relative_to(PROJECT_ROOT)),
        "submission_repair_response_template": str(
            SUBMISSION_REPAIR_RESPONSE_TEMPLATE.relative_to(PROJECT_ROOT)
        ),
        "submission_repair_response_preflight": str(
            SUBMISSION_REPAIR_RESPONSE_PREFLIGHT.relative_to(PROJECT_ROOT)
        ),
    }
    manifest["latest_r7_pipeline_status"] = readiness["r7_status"]
    manifest["latest_r7_pipeline_submission_readiness_status"] = readiness[
        "field_package_submission_readiness_status"
    ]
    manifest["latest_r7_pipeline_submission_highest_priority_blocker"] = readiness[
        "field_package_submission_highest_priority_blocker"
    ]
    manifest["latest_r7_pipeline_submission_next_operator_action"] = readiness[
        "field_package_submission_next_operator_action"
    ]
    manifest["latest_r7_pipeline_submission_blocking_stage_count"] = readiness[
        "field_package_submission_blocking_stage_count"
    ]
    manifest["latest_r7_pipeline_submission_can_submit_to_agent42_smoke_replay"] = readiness[
        "field_package_submission_can_submit_to_agent42_smoke_replay"
    ]
    manifest["latest_r7_pipeline_submission_can_route_to_path_endpoint_layout_holdout"] = readiness[
        "field_package_submission_can_route_to_path_endpoint_layout_holdout"
    ]
    manifest["latest_r7_pipeline_submission_no_write_boundary_pass"] = readiness[
        "field_package_submission_no_write_boundary_pass"
    ]
    manifest["latest_r7_pipeline_submission_repair_work_order_status"] = readiness[
        "field_package_submission_repair_work_order_status"
    ]
    manifest["latest_r7_pipeline_submission_repair_item_count"] = readiness[
        "field_package_submission_repair_item_count"
    ]
    manifest["latest_r7_pipeline_submission_repair_response_preflight_status"] = readiness[
        "field_package_submission_repair_response_preflight_status"
    ]
    manifest["latest_r7_pipeline_submission_repair_response_missing_item_count"] = readiness[
        "field_package_submission_repair_response_missing_item_count"
    ]
    manifest["latest_r7_pipeline_submission_repair_response_template_marker_count"] = readiness[
        "field_package_submission_repair_response_template_marker_count"
    ]
    manifest["latest_r7_pipeline_submission_repair_response_can_route_to_r7_preflight"] = readiness[
        "field_package_submission_repair_response_can_route_to_r7_preflight"
    ]
    manifest["latest_r7_pipeline_coverage_status"] = readiness["field_package_coverage_status"]
    manifest["latest_r7_pipeline_field_proxy_holdout_status"] = readiness["field_proxy_holdout_status"]
    manifest["latest_r7_pipeline_field_proxy_holdout_pass"] = readiness["field_proxy_holdout_coverage_pass"]
    manifest["latest_r7_pipeline_field_proxy_holdout_matched_batch_count"] = readiness[
        "field_proxy_holdout_matched_batch_count"
    ]
    manifest["latest_r7_pipeline_pressure_source_conflict_count"] = readiness["pressure_source_conflict_count"]
    manifest["latest_r7_pipeline_resolved_pressure_source_conflict_count"] = readiness[
        "resolved_pressure_source_conflict_count"
    ]
    manifest["latest_r7_pipeline_unresolved_pressure_source_conflict_count"] = readiness[
        "unresolved_pressure_source_conflict_count"
    ]
    manifest["latest_r7_pipeline_pressure_source_resolution_record_count"] = readiness[
        "pressure_source_resolution_record_count"
    ]
    manifest["latest_r7_pipeline_pressure_source_conflict_requires_operator_review"] = readiness[
        "pressure_source_conflict_requires_operator_review"
    ]
    manifest["latest_r7_pipeline_pressure_conflict_resolution_status"] = readiness[
        "field_package_pressure_conflict_resolution_status"
    ]
    manifest["latest_r7_pipeline_pressure_conflict_resolution_ready"] = readiness[
        "field_package_pressure_conflict_resolution_ready"
    ]
    manifest["latest_r7_pipeline_agent51_field_proxy_summary_status"] = readiness[
        "agent51_field_proxy_summary_status"
    ]
    manifest["latest_r7_pipeline_agent51_field_proxy_scoreable_batch_count"] = readiness[
        "agent51_field_proxy_scoreable_batch_count"
    ]
    manifest["latest_r7_pipeline_agent51_field_proxy_validation_pass"] = readiness[
        "agent51_field_proxy_validation_pass"
    ]
    manifest["latest_r7_pipeline_multi_facility_control_promotion_pass"] = readiness[
        "multi_facility_control_promotion_pass"
    ]
    manifest["latest_r7_pipeline_catalyst_proxy_field_validation_pass"] = readiness[
        "catalyst_proxy_field_validation_pass"
    ]
    manifest["latest_r7_pipeline_minimum_replay_contract_status"] = readiness["minimum_replay_contract_status"]
    manifest["latest_r7_pipeline_field_evidence_sufficiency_status"] = readiness[
        "field_evidence_sufficiency_status"
    ]
    manifest["latest_r7_pipeline_field_evidence_sufficiency_score"] = readiness[
        "field_evidence_sufficiency_score"
    ]
    manifest["latest_r7_pipeline_field_evidence_smoke_pass"] = readiness["field_evidence_smoke_pass"]
    manifest["latest_r7_pipeline_field_evidence_calibration_volume_pass"] = readiness[
        "field_evidence_calibration_volume_pass"
    ]
    manifest["latest_r7_pipeline_can_route_to_human_review_candidate"] = readiness[
        "can_route_to_human_review_candidate"
    ]
    manifest["latest_r7_pipeline_field_path_endpoint_label_preflight_status"] = readiness[
        "field_path_endpoint_label_preflight_status"
    ]
    manifest["latest_r7_pipeline_field_path_endpoint_matched_batch_count"] = readiness[
        "field_path_endpoint_matched_batch_count"
    ]
    manifest["latest_r7_pipeline_field_path_endpoint_required_matched_batch_deficit"] = readiness[
        "field_path_endpoint_required_matched_batch_deficit"
    ]
    manifest["latest_r7_pipeline_field_path_endpoint_batch_alignment_gap_count"] = readiness[
        "field_path_endpoint_batch_alignment_gap_count"
    ]
    manifest["latest_r7_pipeline_field_path_endpoint_alignment_patch_plan_status"] = readiness[
        "field_path_endpoint_alignment_patch_plan_status"
    ]
    manifest["latest_r7_pipeline_field_path_endpoint_alignment_patch_plan_item_count"] = readiness[
        "field_path_endpoint_alignment_patch_plan_item_count"
    ]
    manifest["latest_r7_pipeline_field_path_endpoint_label_package_ready"] = readiness[
        "field_path_endpoint_label_package_ready"
    ]
    manifest["latest_r7_pipeline_can_route_to_field_layout_holdout_with_path_labels"] = readiness[
        "can_route_to_field_layout_holdout_with_path_labels"
    ]
    manifest["latest_r7_pipeline_release_gate_endpoint_label_blocked"] = readiness[
        "release_gate_endpoint_label_blocked"
    ]
    manifest["latest_r7_pipeline_field_supported_claim_upgrade_ready"] = readiness[
        "field_supported_claim_upgrade_ready"
    ]
    manifest["latest_r7_pipeline_minimum_common_batch_count"] = readiness["minimum_common_batch_count"]
    manifest["latest_r7_pipeline_minimum_valid_matched_batch_count"] = readiness["minimum_valid_matched_batch_count"]
    manifest["latest_r7_pipeline_minimum_valid_operation_action_count"] = readiness[
        "minimum_valid_operation_action_count"
    ]
    manifest["latest_r7_pipeline_minimum_invalid_operation_action_count"] = readiness[
        "minimum_invalid_operation_action_count"
    ]
    manifest["latest_r7_pipeline_minimum_valid_lab_result_count"] = readiness["minimum_valid_lab_result_count"]
    manifest["latest_r7_pipeline_minimum_invalid_lab_result_count"] = readiness["minimum_invalid_lab_result_count"]
    manifest["latest_r7_pipeline_minimum_valid_proxy_label_count"] = readiness["minimum_valid_proxy_label_count"]
    manifest["latest_r7_pipeline_minimum_invalid_proxy_label_count"] = readiness["minimum_invalid_proxy_label_count"]
    manifest["latest_r7_pipeline_minimum_pressure_headloss_event_count"] = readiness[
        "minimum_pressure_headloss_event_count"
    ]
    manifest["latest_r7_pipeline_minimum_valid_pressure_headloss_event_count"] = readiness[
        "minimum_valid_pressure_headloss_event_count"
    ]
    manifest["latest_r7_pipeline_minimum_invalid_pressure_headloss_event_count"] = readiness[
        "minimum_invalid_pressure_headloss_event_count"
    ]
    manifest["latest_r7_pipeline_minimum_valid_pressure_headloss_batch_count"] = readiness[
        "minimum_valid_pressure_headloss_batch_count"
    ]
    manifest["latest_r7_pipeline_minimum_time_order_violation_count"] = readiness[
        "minimum_time_order_violation_count"
    ]
    manifest["latest_r7_pipeline_next_action"] = readiness["r7_next_action"]
    manifest["next_stage"] = (
        f"按 R7 pipeline，下一步执行 {readiness['r7_next_action']}。"
        "若有真实包，使用 REAL_FIELD_REPLAY_PACKAGE_DIR 运行端到端 replay 管线；"
        "真实包通过 R7a 后继续由 R7j 检查 N3 床出口 UV254/ORP、催化剂床压降、床体积/HRT、"
        "再生事件和 QA 通过的 catalyst_activity 标签；R8m 进一步检查 node pressure 与 pressure_headloss_event_log "
        "是否发生同批次来源冲突，并把冲突转成 operator review 与校准补包项；field evidence sufficiency gate "
        "会区分 smoke replay ready 与 human-review candidate ready；模板或 synthetic 包仍不得作为 field evidence。"
    )
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def _strip_normalized(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: _strip_normalized(item)
            for key, item in value.items()
            if key != "normalized_datasets"
        }
    if isinstance(value, list):
        return [_strip_normalized(item) for item in value]
    return value


if __name__ == "__main__":
    main()

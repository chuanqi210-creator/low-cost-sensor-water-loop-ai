from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from water_ai.agents.field_replay_import_agent import preflight_field_replay_package
from water_ai.agents.soft_sensor_matrix_coupling_agent import (
    build_field_path_endpoint_label_package_contract,
    preflight_field_path_endpoint_label_package,
)


EXPECTED_HIDDEN_STATES = (
    "pollutant_residual",
    "reaction_completion",
    "catalyst_activity",
    "matrix_interference",
    "hydraulic_delay",
    "release_or_byproduct_risk",
)

RESPONSE_TEMPLATE_REQUIRED_FIELDS = (
    "template_id",
    "package_type",
    "source_interface_id",
    "required_response_row_count",
    "evidence_rows",
    "no_write_boundary",
)

RESPONSE_ROW_REQUIRED_FIELDS = (
    "response_row_id",
    "hidden_state",
    "required_evidence",
    "evidence_channel",
    "table_name",
    "field_name",
    "data_origin",
    "batch_id",
    "evidence_value_reference",
    "evidence_value",
    "chain_of_custody_id",
    "operator_id",
    "no_write_boundary_confirmed",
)

PACKAGE_ASSEMBLY_REQUIRED_FIELDS = (
    "plan_id",
    "response_preflight_status",
    "assembly_status",
    "channel_plans",
    "candidate_channel_plans",
    "no_write_boundary",
)

PACKAGE_CHANNEL_PLAN_REQUIRED_FIELDS = (
    "channel_id",
    "package_pointer",
    "assembly_status",
    "table_assemblies",
    "can_resume_model_chain",
    "can_write_to_actuator",
    "can_write_to_release_gate",
)

PACKAGE_TABLE_ASSEMBLY_REQUIRED_FIELDS = (
    "table_name",
    "field_names",
    "hidden_states",
    "response_row_ids",
    "required_output_columns",
    "row_alignment_keys",
)

R7_METADATA_REQUIRED_FIELDS = (
    "data_origin",
    "site_id",
    "campaign_id",
    "sampling_start",
    "sampling_end",
    "operator_id",
    "instrument_snapshot_id",
    "chain_of_custody_id",
)


STATE_ACTIVATION_LIBRARY: dict[str, dict[str, Any]] = {
    "pollutant_residual": {
        "required_channels": ["R7_REAL_FIELD_PACKAGE", "R8U66_PATH_ENDPOINT_LABEL_PACKAGE"],
        "required_field_evidence": [
            "offline_lab_results.pollutant_residual",
            "sensor_timeseries.final_effluent:UV254_abs",
            "sensor_timeseries.final_effluent:ORP_mV",
            "final_effluent_endpoint_labels.release_label",
            "field_holdout_release_labels.batch_id",
        ],
        "resumes_to": [
            "Agent44 field import preflight",
            "Agent46 soft-sensor field holdout gate",
            "human release review candidate",
        ],
        "technical_problem": "低成本传感器不能直接高频测出残留污染物，需要用离线标签校准软传感估计。",
        "technical_means": "把出水端低成本 proxy、离线实验标签和 endpoint label 对齐到同一 batch_id。",
        "technical_effect": "让残留污染物从 synthetic proxy 推断升级为可回放、可 holdout 的现场候选证据。",
    },
    "reaction_completion": {
        "required_channels": ["R7_REAL_FIELD_PACKAGE", "R8U66_PATH_ENDPOINT_LABEL_PACKAGE"],
        "required_field_evidence": [
            "offline_lab_results.reaction_completion_proxy",
            "campaign_operation_log.hold_time_min",
            "campaign_operation_log.effect_time_min",
            "campaign_operation_log.recycle_ratio",
            "site_topology_or_bed_geometry.nominal_HRT_min",
        ],
        "resumes_to": [
            "Agent42 timestamped campaign replay",
            "Agent53 grey-box residence-time check",
            "Agent49 recycle/hold-time control review",
        ],
        "technical_problem": "循环处理争取了时间，但没有现场停留时间和反应完成标签时不能判断是否该回流或放行。",
        "technical_means": "把操作日志、HRT/接触时间和离线反应完成 proxy 绑定到同一时段。",
        "technical_effect": "把回流、延长停留和暂存等待从经验动作变成可回放的控制候选。",
    },
    "catalyst_activity": {
        "required_channels": ["R7_REAL_FIELD_PACKAGE", "R8U66_PATH_ENDPOINT_LABEL_PACKAGE"],
        "required_field_evidence": [
            "node_modality_sensor_timeseries.N3_catalyst_bed_outlet:UV254_abs",
            "node_modality_sensor_timeseries.N3_catalyst_bed_outlet:ORP_mV",
            "node_modality_sensor_timeseries.N3_catalyst_bed:pressure_drop_kPa",
            "offline_lab_results.catalyst_activity",
            "campaign_operation_log.regeneration_event",
            "site_topology_or_bed_geometry.nominal_HRT_min",
        ],
        "resumes_to": [
            "Agent51 catalyst proxy field holdout",
            "Agent52 control replay promotion gate",
            "Agent49 catalyst regeneration/replacement candidate review",
        ],
        "technical_problem": "催化剂活性是当前弱观测状态，缺少床层压降、再生事件和离线活性标签会阻断控制升级。",
        "technical_means": "把催化床前后 proxy、床层压降、再生日志和离线活性标签作为同一状态激活包。",
        "technical_effect": "让催化剂衰减、再生和更换从解释性假设变成可验证的保护性控制候选。",
    },
    "matrix_interference": {
        "required_channels": ["R7_REAL_FIELD_PACKAGE"],
        "required_field_evidence": [
            "field_labeled_fast_proxy_event_log.matrix_shock",
            "offline_lab_results.matrix_interference",
            "sensor_timeseries.influent:conductivity_uScm",
            "sensor_timeseries.influent:turbidity_NTU",
            "sensor_timeseries.influent:ORP_mV",
        ],
        "resumes_to": [
            "Agent41 matrix shock fast proxy",
            "Agent45 field replay evidence chain",
            "Agent49 conservative control arbitration",
        ],
        "technical_problem": "水质基质冲击会让软传感和催化效率外推失真，单纯进出水传感难以及时解释。",
        "technical_means": "把进水 EC/浊度/ORP proxy、人工或离线 matrix shock 标签与 replay 事件对齐。",
        "technical_effect": "让系统能识别何时应保守回流、暂存验证或切换处理单元，而不是盲目放行。",
    },
    "hydraulic_delay": {
        "required_channels": ["R7_REAL_FIELD_PACKAGE", "R8U66_PATH_ENDPOINT_LABEL_PACKAGE"],
        "required_field_evidence": [
            "campaign_operation_log.effect_time_min",
            "campaign_operation_log.hold_time_min",
            "campaign_operation_log.recycle_ratio",
            "site_topology_or_bed_geometry.flow_Lmin",
            "hydraulic_path_stage_labels.stage_id",
        ],
        "resumes_to": [
            "Agent42 timestamped campaign replay",
            "Agent54 field layout holdout",
            "Agent49 multi-facility delay-aware control review",
        ],
        "technical_problem": "循环结构降低了传感响应速度要求，但必须知道延迟和路径，否则控制动作无法归因。",
        "technical_means": "把路径阶段标签、流量、停留时间、回流比和动作生效时间写成水力延迟证据。",
        "technical_effect": "让低频观测下的回流、延长停留和跨单元切换具备可回放的时间轴。",
    },
    "release_or_byproduct_risk": {
        "required_channels": ["R7_REAL_FIELD_PACKAGE", "R8U66_PATH_ENDPOINT_LABEL_PACKAGE"],
        "required_field_evidence": [
            "offline_lab_results.byproduct_or_release_risk",
            "final_effluent_endpoint_labels.release_label",
            "human_reviewed_release_gate_labels.batch_id",
            "campaign_operation_log.operator_review_decision",
        ],
        "resumes_to": [
            "Agent46 soft-sensor field holdout gate",
            "Agent58 field validation queue alignment",
            "human release gate review",
        ],
        "technical_problem": "副产物或放行风险不能由低成本 proxy 直接证明，必须有人工复核和离线确认。",
        "technical_means": "把终端放行标签、副产物离线检测和人工复核决策接入同一 release gate 证据链。",
        "technical_effect": "让系统能生成放行候选或保护性阻断候选，但不绕过人工和离线验证。",
    },
}


def build_field_activation_matrix(
    core_gate: dict[str, Any],
    *,
    interface_id: str = "R8u97_field_activation_matrix_interface",
) -> dict[str, Any]:
    """Map hidden states to external evidence channels and model-chain resume gates."""

    hidden_ledger = _dict(core_gate.get("hidden_state_coverage_ledger"))
    external_conditions = _dict(core_gate.get("external_resume_conditions"))
    state_rows = _state_rows(hidden_ledger)
    route_rows = _route_rows(external_conditions)
    channels = _channels(external_conditions)
    rows = [
        _activation_row(state_row, route_rows=route_rows, channels=channels)
        for state_row in state_rows
    ]
    readiness = _readiness(rows, external_conditions)
    return {
        "interface_id": interface_id,
        "interface_type": "new_testable_core_interface",
        "source_core_gate_id": core_gate.get("gate_id", "unknown_core_gate"),
        "system_layer_mapping": [
            "观测层",
            "状态估计层",
            "机理证据层",
            "诊断决策层",
            "闭环执行层",
            "验证治理层",
        ],
        "core_capability_mapping": [
            "可观测性",
            "可控性",
            "可解释性",
            "可验证性",
            "可工程化",
            "可保护性",
        ],
        "method_contract": _method_contract(),
        "state_activation_rows": rows,
        "readiness": readiness,
        "next_operator_actions": _next_operator_actions(rows),
        "writeback_policy": _writeback_policy(readiness),
    }


def build_field_activation_response_template(matrix: dict[str, Any]) -> dict[str, Any]:
    """Build an operator-fillable response package template for state-level evidence."""

    rows: list[dict[str, Any]] = []
    for state_row in _matrix_state_rows(matrix):
        hidden_state = str(state_row.get("hidden_state", "unknown_hidden_state"))
        required_channels = [str(channel) for channel in state_row.get("required_channels", [])]
        default_channel = required_channels[0] if required_channels else "TODO_channel"
        for index, evidence_field in enumerate(state_row.get("required_field_evidence", []), start=1):
            table_name, field_name = _split_evidence_field(str(evidence_field))
            rows.append(
                {
                    "response_row_id": f"{hidden_state}_{index:02d}",
                    "hidden_state": hidden_state,
                    "required_evidence": str(evidence_field),
                    "evidence_channel": default_channel,
                    "table_name": table_name,
                    "field_name": field_name,
                    "data_origin": "TODO_field",
                    "batch_id": "TODO_batch_id",
                    "timestamp": "TODO_timestamp_or_not_applicable",
                    "node_id": "TODO_node_id_or_not_applicable",
                    "sensor_id": "TODO_sensor_id_or_not_applicable",
                    "evidence_value_reference": "TODO_table_column_or_file_reference",
                    "evidence_value": "TODO_actual_field_value_or_json_payload",
                    "offline_method_id": "TODO_method_id_or_not_applicable",
                    "detection_limit": "TODO_detection_limit_or_not_applicable",
                    "chain_of_custody_id": "TODO_chain_of_custody_id",
                    "operator_id": "TODO_operator_id",
                    "no_write_boundary_confirmed": "TODO_true",
                    "review_notes": "TODO_explain_real_field_source_and_alignment",
                }
            )
    return {
        "template_id": "R8u98_field_activation_evidence_response_template",
        "package_type": "field_activation_evidence_response",
        "source_interface_id": matrix.get("interface_id", "unknown_field_activation_matrix"),
        "required_response_row_count": len(rows),
        "evidence_rows": rows,
        "operator_instructions": [
            "Fill every evidence row with real field provenance; do not leave TODO/template markers.",
            "Fill evidence_value with the actual machine-readable value or JSON payload; evidence_value_reference is provenance only.",
            "Use data_origin=field only for rows backed by real field data.",
            "Keep batch_id/timestamp/node_id/sensor_id alignment when the evidence comes from time-series or lab tables.",
            "Confirm no_write_boundary_confirmed=true for every row; this response cannot authorize actuator or release-gate writes.",
        ],
        "no_write_boundary": (
            "The response template only prepares state-level external evidence for preflight/replay/review. "
            "It cannot write actuator policy, release gate, legal conclusions or field-supported claims."
        ),
    }


def preflight_field_activation_response(
    response: dict[str, Any],
    matrix: dict[str, Any],
) -> dict[str, Any]:
    """Validate a filled field-activation response without treating it as field proof."""

    expected = _expected_response_index(matrix)
    rows = response.get("evidence_rows", [])
    evidence_rows = [row for row in rows if isinstance(row, dict)] if isinstance(rows, list) else []
    provided = {
        (
            str(row.get("hidden_state", "")),
            str(row.get("required_evidence", "")),
        ): row
        for row in evidence_rows
    }
    missing = [
        {"hidden_state": state, "required_evidence": evidence}
        for state, evidence in expected
        if (state, evidence) not in provided
    ]
    extra = [
        {"hidden_state": state, "required_evidence": evidence}
        for state, evidence in provided
        if (state, evidence) not in expected
    ]
    template_rows = [
        row for row in evidence_rows if _row_has_template_marker(row)
    ]
    non_field_rows = [
        row
        for row in evidence_rows
        if str(row.get("data_origin", "")).strip().lower() != "field"
    ]
    unsupported_channel_rows = [
        row
        for row in evidence_rows
        if str(row.get("evidence_channel", "")) not in _allowed_channels_for_state(
            matrix,
            str(row.get("hidden_state", "")),
        )
    ]
    missing_alignment_rows = [
        row
        for row in evidence_rows
        if not str(row.get("batch_id", "")).strip()
        or _has_template_marker(str(row.get("batch_id", "")))
        or not str(row.get("evidence_value_reference", "")).strip()
        or _has_template_marker(str(row.get("evidence_value_reference", "")))
    ]
    missing_value_payload_rows = [
        row for row in evidence_rows if _response_value_payload_missing(row)
    ]
    template_value_payload_rows = [
        row
        for row in evidence_rows
        if not _response_value_payload_missing(row)
        and _response_value_payload_has_template_marker(row)
    ]
    no_write_unconfirmed_rows = [
        row for row in evidence_rows if not _truthy(row.get("no_write_boundary_confirmed"))
    ]
    source_mismatch = (
        str(response.get("source_interface_id", "")) != str(matrix.get("interface_id", ""))
    )
    package_type_ok = str(response.get("package_type", "")) == "field_activation_evidence_response"
    ready = bool(
        package_type_ok
        and not source_mismatch
        and not missing
        and not extra
        and not template_rows
        and not non_field_rows
        and not unsupported_channel_rows
        and not missing_alignment_rows
        and not missing_value_payload_rows
        and not template_value_payload_rows
        and not no_write_unconfirmed_rows
    )
    return {
        "preflight_id": "R8u98_field_activation_evidence_response_preflight",
        "package_type_ok": package_type_ok,
        "source_interface_id": response.get("source_interface_id", ""),
        "source_interface_match": not source_mismatch,
        "preflight_status": (
            "field_activation_response_ready_for_external_package_preflight"
            if ready
            else "field_activation_response_blocked_before_external_package_preflight"
        ),
        "expected_response_row_count": len(expected),
        "provided_response_row_count": len(evidence_rows),
        "missing_response_row_count": len(missing),
        "extra_response_row_count": len(extra),
        "template_marker_row_count": len(template_rows),
        "non_field_row_count": len(non_field_rows),
        "unsupported_channel_row_count": len(unsupported_channel_rows),
        "missing_alignment_row_count": len(missing_alignment_rows),
        "missing_value_payload_row_count": len(missing_value_payload_rows),
        "template_value_payload_row_count": len(template_value_payload_rows),
        "no_write_unconfirmed_row_count": len(no_write_unconfirmed_rows),
        "can_route_to_external_activation_router": ready,
        "can_resume_model_chain": False,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
        "missing_response_rows": missing[:20],
        "extra_response_rows": extra[:20],
        "blocked_row_ids": _blocked_row_ids(
            template_rows
            + non_field_rows
            + unsupported_channel_rows
            + missing_alignment_rows
            + missing_value_payload_rows
            + template_value_payload_rows
            + no_write_unconfirmed_rows
        ),
        "next_operator_action": (
            "submit_response_to_external_activation_router_or_field_package_preflight"
            if ready
            else "fill_all_rows_with_real_field_values_and_confirm_no_write_boundary"
        ),
        "no_write_boundary": (
            "Passing this preflight only means state-level evidence rows are filled and ready for downstream "
            "package/router preflight. It does not authorize actuator policy, release gate, legal conclusions "
            "or field-supported claims."
        ),
    }


def build_field_activation_response_completion_ledger(
    response: dict[str, Any],
    matrix: dict[str, Any],
    response_source_preflight: dict[str, Any],
    response_preflight: dict[str, Any],
) -> dict[str, Any]:
    """Summarize how far the operator-filled response is from machine-ready evidence."""

    expected_rows = _expected_response_entries(matrix)
    evidence_rows = _list_of_dicts(response.get("evidence_rows"))
    provided = {
        (
            str(row.get("hidden_state", "")),
            str(row.get("required_evidence", "")),
        ): row
        for row in evidence_rows
    }
    row_ledgers = [
        _response_completion_row(entry, provided.get((entry["hidden_state"], entry["required_evidence"])), matrix)
        for entry in expected_rows
    ]
    state_rows = _response_completion_state_rows(row_ledgers)
    table_rows = _response_completion_table_rows(row_ledgers)
    issue_counts = _response_completion_issue_counts(row_ledgers)
    completed_count = sum(1 for row in row_ledgers if row["completion_status"] == "row_complete")
    expected_count = len(expected_rows)
    incomplete_count = expected_count - completed_count
    next_focus = _response_completion_next_hidden_state_focus(state_rows)
    status = _response_completion_ledger_status(
        completed_count=completed_count,
        expected_count=expected_count,
        response_source_preflight=response_source_preflight,
        response_preflight=response_preflight,
    )
    return {
        "ledger_id": "R8u124_field_activation_response_completion_ledger",
        "ledger_type": "field_activation_response_completion_ledger",
        "ledger_status": status,
        "source_preflight_status": response_source_preflight.get("source_preflight_status", "unknown"),
        "external_response_supplied": bool(
            response_source_preflight.get("external_response_supplied", False)
        ),
        "response_preflight_status": response_preflight.get("preflight_status", "unknown"),
        "expected_response_row_count": expected_count,
        "provided_response_row_count": len(evidence_rows),
        "completed_response_row_count": completed_count,
        "incomplete_response_row_count": incomplete_count,
        "completion_ratio": _ratio(completed_count, expected_count),
        "issue_scope_counts": issue_counts,
        "hidden_state_completion_rows": state_rows,
        "table_completion_rows": table_rows,
        "next_hidden_state_focus": next_focus.get("hidden_state", ""),
        "next_hidden_state_focus_status": next_focus.get("completion_status", ""),
        "next_operator_action": _response_completion_next_operator_action(status, next_focus),
        "can_route_to_response_preflight": bool(
            response_source_preflight.get("can_run_response_preflight", False)
        ),
        "can_route_to_package_assembly": bool(
            response_preflight.get("can_route_to_external_activation_router", False)
        ),
        "can_resume_model_chain": False,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
        "no_write_boundary": (
            "This ledger only measures response completion and machine-readiness gaps. It does not create "
            "field evidence, run replay/holdout, resume the model chain, write actuator policy, write a "
            "release gate, or upgrade any claim to field-supported."
        ),
    }


def build_field_activation_response_focus_handoff(
    response_completion_ledger: dict[str, Any],
    catalyst_response_submission_kit: dict[str, Any] | None = None,
    focused_catalyst_response_merge_preflight: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Route the next incomplete hidden-state focus to a smaller response package when possible."""

    kit = catalyst_response_submission_kit or {}
    merge_preflight = focused_catalyst_response_merge_preflight or {}
    focused_repair_work_order = merge_preflight.get("focused_catalyst_response_repair_work_order", {})
    if not isinstance(focused_repair_work_order, dict):
        focused_repair_work_order = {}
    ledger_status = str(response_completion_ledger.get("ledger_status", "unknown"))
    next_focus = str(response_completion_ledger.get("next_hidden_state_focus", ""))
    expected_row_count = _safe_int(response_completion_ledger.get("expected_response_row_count", 0))
    kit_row_count = _safe_int(kit.get("target_response_row_count", 0))
    kit_ready = str(kit.get("kit_status", "")) == "catalyst_response_submission_kit_ready_for_operator_fill"
    if not next_focus:
        handoff_status = "field_activation_response_focus_handoff_not_needed_response_complete"
    elif next_focus != "catalyst_activity":
        handoff_status = "field_activation_response_focus_handoff_waiting_for_full_response_focus"
    elif not kit_ready:
        handoff_status = "field_activation_response_focus_handoff_blocked_by_catalyst_kit"
    else:
        handoff_status = "field_activation_response_focus_handoff_ready_for_catalyst_activity"

    return {
        "handoff_id": "R8u125_field_activation_response_focus_handoff",
        "handoff_type": "field_activation_response_focus_handoff",
        "handoff_status": handoff_status,
        "source_completion_ledger_id": response_completion_ledger.get("ledger_id", "unknown_ledger"),
        "source_completion_ledger_status": ledger_status,
        "target_hidden_state": next_focus,
        "focused_hidden_state_supported": next_focus == "catalyst_activity",
        "focused_response_kit_id": kit.get("kit_id", "catalyst_response_submission_kit_not_available"),
        "focused_response_kit_status": kit.get(
            "kit_status",
            "catalyst_response_submission_kit_not_available",
        ),
        "focused_response_template_path": kit.get("focused_response_template_path", ""),
        "focused_response_schema_path": kit.get("focused_response_schema_path", ""),
        "focused_to_full_response_merge_plan_path": kit.get("full_response_merge_plan_path", ""),
        "focused_response_row_count": kit_row_count,
        "full_response_expected_row_count": expected_row_count,
        "row_scan_reduction_count": max(0, expected_row_count - kit_row_count)
        if next_focus == "catalyst_activity"
        else 0,
        "row_scan_reduction_ratio": _ratio(max(0, expected_row_count - kit_row_count), expected_row_count)
        if next_focus == "catalyst_activity"
        else 0.0,
        "focused_merge_preflight_id": merge_preflight.get(
            "preflight_id",
            "focused_catalyst_response_merge_preflight_not_available",
        ),
        "focused_merge_preflight_status": merge_preflight.get(
            "preflight_status",
            "focused_catalyst_response_merge_preflight_not_available",
        ),
        "focused_merge_source_env_var": merge_preflight.get(
            "source_env_var",
            "FOCUSED_CATALYST_RESPONSE_PATH",
        ),
        "full_response_env_var": "FIELD_ACTIVATION_RESPONSE_PATH",
        "focused_merge_next_operator_action": merge_preflight.get(
            "next_operator_action",
            "run_focused_catalyst_response_merge_preflight",
        ),
        "focused_repair_work_order_status": focused_repair_work_order.get(
            "work_order_status",
            "focused_catalyst_response_repair_work_order_not_available",
        ),
        "focused_repair_item_count": _safe_int(focused_repair_work_order.get("repair_item_count", 0)),
        "focused_repair_highest_priority_repair_id": focused_repair_work_order.get(
            "highest_priority_repair_id",
            "",
        ),
        "focused_repair_next_operator_action": focused_repair_work_order.get("next_operator_action", ""),
        "next_operator_action": _field_activation_response_focus_handoff_next_action(
            handoff_status,
            next_focus,
            str(
                focused_repair_work_order.get(
                    "work_order_status",
                    "focused_catalyst_response_repair_work_order_not_available",
                )
            ),
            str(focused_repair_work_order.get("next_operator_action", "")),
        ),
        "full_response_still_required": next_focus == "catalyst_activity",
        "can_replace_full_field_activation_response": False,
        "can_submit_to_external_activation_router": False,
        "can_resume_model_chain": False,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
        "field_boundary": (
            "This handoff narrows the next operator action from the full field activation response to the "
            "focused catalyst_activity rows when catalyst_activity is the next incomplete hidden state. The "
            "focused response still has to pass merge/full-response/package preflight before any field chain "
            "can resume."
        ),
        "no_write_boundary": (
            "The handoff is an operator-routing artifact only. It cannot create field evidence, authorize "
            "control actions, release water, relax Agent49 catalyst guardrails or upgrade synthetic results "
            "to field-supported claims."
        ),
    }


def audit_field_activation_response_coherence(
    response: dict[str, Any],
    matrix: dict[str, Any],
    response_preflight: dict[str, Any],
) -> dict[str, Any]:
    """Check whether a filled response is coherent enough for package assembly.

    The audit is stricter than row-level preflight but still no-write: it checks
    whether rows can form replayable field evidence groups; it does not assert
    that the field measurements are scientifically true.
    """

    rows = _list_of_dicts(response.get("evidence_rows"))
    response_ready = bool(response_preflight.get("can_route_to_external_activation_router", False))
    blockers: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    hidden_state_audits = [
        _coherence_hidden_state_audit(
            str(state_row.get("hidden_state", "unknown_hidden_state")),
            rows,
            blockers=blockers,
            warnings=warnings,
        )
        for state_row in _matrix_state_rows(matrix)
    ]
    row_scope_audits = [
        _coherence_row_scope_audit(row, blockers=blockers, warnings=warnings)
        for row in rows
    ]
    if not response_ready:
        blockers = []
        warnings = []
        status = "field_activation_response_coherence_audit_waiting_for_response_preflight"
    elif blockers:
        status = "field_activation_response_coherence_audit_blocked_before_package_assembly"
    else:
        status = "field_activation_response_coherence_audit_passed_for_package_assembly"
    can_route = bool(response_ready and not blockers)
    return {
        "audit_id": "R8u117_field_activation_response_coherence_audit",
        "audit_type": "field_activation_response_batch_node_custody_coherence_audit",
        "audit_status": status,
        "response_preflight_status": response_preflight.get("preflight_status", "unknown"),
        "response_ready_for_audit": response_ready,
        "audit_execution_status": (
            "coherence_checks_deferred_until_response_preflight_ready"
            if not response_ready
            else "coherence_checks_executed"
        ),
        "evidence_row_count": len(rows),
        "hidden_state_audit_count": len(hidden_state_audits),
        "row_scope_audit_count": len(row_scope_audits),
        "hard_blocker_count": len(blockers),
        "warning_count": len(warnings),
        "highest_priority_blocker": str(blockers[0]["blocker_id"]) if blockers else "",
        "hidden_state_alignment_audits": hidden_state_audits,
        "row_scope_audits": row_scope_audits,
        "blockers": blockers[:50],
        "warnings": warnings[:50],
        "can_route_to_package_assembly": can_route,
        "can_route_to_external_activation_router": can_route,
        "can_resume_model_chain": False,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
        "next_operator_action": _coherence_next_operator_action(status, blockers),
        "no_write_boundary": (
            "This coherence audit checks whether a filled field-activation response can be assembled into "
            "replayable package candidates with batch/node/sensor/custody/method alignment. It does not prove "
            "field truth, does not run replay/holdout, and cannot write actuator policy, release gate, "
            "legal conclusions or field-supported claims."
        ),
    }


def preflight_field_activation_response_source(
    *,
    source_path: str,
    load_status: str,
    response: dict[str, Any],
    default_response_template: dict[str, Any],
    matrix: dict[str, Any],
) -> dict[str, Any]:
    """Preflight the selected response source before evidence-row validation."""

    external_response_supplied = bool(source_path.strip())
    using_default_template = not external_response_supplied
    root_object_ok = isinstance(response, dict)
    selected_response_id = str(
        response.get(
            "template_id",
            response.get("response_id", "unknown_field_activation_response"),
        )
    )
    template_row_count = len(_list_of_dicts(default_response_template.get("evidence_rows")))
    selected_row_count = len(_list_of_dicts(response.get("evidence_rows"))) if root_object_ok else 0
    source_interface_match = (
        str(response.get("source_interface_id", "")) == str(matrix.get("interface_id", ""))
        if root_object_ok
        else False
    )
    if using_default_template:
        status = "field_activation_response_source_using_default_template"
    elif load_status != "field_activation_response_source_loaded":
        status = "field_activation_response_source_blocked_at_file_load"
    elif not root_object_ok:
        status = "field_activation_response_source_blocked_at_root_shape"
    else:
        status = "field_activation_response_source_loaded_external_json"
    can_run_response_preflight = bool(
        root_object_ok
        and status
        in {
            "field_activation_response_source_using_default_template",
            "field_activation_response_source_loaded_external_json",
        }
    )
    return {
        "source_preflight_id": "R8u101_field_activation_response_source_preflight",
        "source_preflight_status": status,
        "source_path": source_path,
        "source_env_var": "FIELD_ACTIVATION_RESPONSE_PATH",
        "load_status": load_status,
        "external_response_supplied": external_response_supplied,
        "using_default_template": using_default_template,
        "root_object_ok": root_object_ok,
        "selected_response_id": selected_response_id,
        "source_interface_match": source_interface_match,
        "template_response_row_count": template_row_count,
        "selected_response_row_count": selected_row_count,
        "can_run_response_preflight": can_run_response_preflight,
        "can_route_to_external_activation_router": False,
        "can_resume_model_chain": False,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
        "next_operator_action": (
            "set_FIELD_ACTIVATION_RESPONSE_PATH_to_filled_external_response_json"
            if using_default_template
            else (
                "repair_FIELD_ACTIVATION_RESPONSE_PATH_json_before_response_preflight"
                if not can_run_response_preflight
                else "run_field_activation_response_preflight_on_loaded_external_response"
            )
        ),
        "no_write_boundary": (
            "The response source preflight only selects and shape-checks the response JSON. It does not prove "
            "field evidence, does not run replay/holdout, and cannot write actuator policy, release gate, "
            "legal conclusions or field-supported claims."
        ),
    }


def build_field_activation_package_assembly_plan(
    response: dict[str, Any],
    matrix: dict[str, Any],
    response_preflight: dict[str, Any],
    external_activation_contract: dict[str, Any] | None = None,
    response_coherence_audit: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Group state-level evidence rows into channel/table package assembly targets."""

    contract_channels = _contract_channel_map(external_activation_contract or {})
    coherence = response_coherence_audit or {}
    response_ready = bool(
        response_preflight.get("can_route_to_external_activation_router", False)
        and coherence.get("can_route_to_package_assembly", True)
    )
    rows = response.get("evidence_rows", [])
    evidence_rows = [row for row in rows if isinstance(row, dict)] if isinstance(rows, list) else []
    grouped: dict[str, dict[str, list[dict[str, Any]]]] = {}
    for row in evidence_rows:
        channel_id = str(row.get("evidence_channel", "unknown_channel"))
        table_name = str(row.get("table_name", "unknown_table"))
        grouped.setdefault(channel_id, {}).setdefault(table_name, []).append(row)

    channel_plans = [
        _assembly_channel_plan(
            channel_id,
            table_groups,
            contract_channels=contract_channels,
            response_preflight=response_preflight,
            response_ready=response_ready,
        )
        for channel_id, table_groups in sorted(grouped.items())
    ]
    candidate_channel_plans = _candidate_channel_plans_from_matrix(
        matrix,
        contract_channels=contract_channels,
        response_preflight=response_preflight,
        response_ready=response_ready,
    )
    return {
        "plan_id": "R8u99_field_activation_package_assembly_plan",
        "source_interface_id": matrix.get("interface_id", "unknown_field_activation_matrix"),
        "source_response_template_id": response.get("template_id", "unknown_response_template"),
        "response_preflight_status": response_preflight.get("preflight_status", "unknown"),
        "response_coherence_audit_status": coherence.get(
            "audit_status",
            "field_activation_response_coherence_audit_not_supplied",
        ),
        "response_coherence_hard_blocker_count": int(coherence.get("hard_blocker_count", 0) or 0),
        "assembly_status": (
            "field_activation_package_assembly_plan_ready_for_no_write_package_staging"
            if response_ready
            else _package_assembly_blocked_status(response_preflight, coherence)
        ),
        "channel_plan_count": len(channel_plans),
        "table_plan_count": sum(len(channel["table_assemblies"]) for channel in channel_plans),
        "candidate_channel_plan_count": len(candidate_channel_plans),
        "candidate_table_plan_count": sum(
            len(channel["table_assemblies"]) for channel in candidate_channel_plans
        ),
        "evidence_row_count": len(evidence_rows),
        "channel_plans": channel_plans,
        "candidate_channel_plans": candidate_channel_plans,
        "can_stage_external_package_candidates": response_ready,
        "can_route_to_external_activation_router": response_ready,
        "can_resume_model_chain": False,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
        "operator_sequence": _assembly_operator_sequence(response_ready),
        "no_write_boundary": (
            "The assembly plan only groups filled state-level evidence into package tables. It never creates "
            "field evidence by itself, never runs replay/holdout, and never writes actuator policy, release gate, "
            "legal conclusions or field-supported claims."
        ),
    }


def build_field_activation_package_staging_manifest(
    response: dict[str, Any],
    package_assembly_plan: dict[str, Any],
    response_preflight: dict[str, Any],
    response_source_preflight: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Prepare a no-write operator manifest for materializing external package candidates."""

    source_preflight = response_source_preflight or {}
    response_ready = bool(response_preflight.get("can_route_to_external_activation_router", False))
    assembly_ready = bool(package_assembly_plan.get("can_stage_external_package_candidates", False))
    selected_channel_plans = _list_of_dicts(package_assembly_plan.get("channel_plans"))
    candidate_channel_plans = _list_of_dicts(package_assembly_plan.get("candidate_channel_plans"))
    selected_channel_manifests = [
        _staging_channel_manifest(
            plan,
            can_materialize=response_ready and assembly_ready,
            plan_basis="selected_filled_response_channel",
        )
        for plan in selected_channel_plans
    ]
    candidate_channel_requirements = [
        _staging_channel_manifest(
            plan,
            can_materialize=False,
            plan_basis=str(plan.get("plan_basis", "matrix_required_channel_requirement")),
        )
        for plan in candidate_channel_plans
    ]
    can_materialize = bool(response_ready and assembly_ready and selected_channel_manifests)
    return {
        "manifest_id": "R8u104_field_activation_package_staging_manifest",
        "manifest_type": "field_activation_no_write_package_staging_manifest",
        "source_response_id": response.get(
            "template_id",
            response.get("response_id", "unknown_field_activation_response"),
        ),
        "response_source_preflight_status": source_preflight.get(
            "source_preflight_status",
            "field_activation_response_source_preflight_not_supplied",
        ),
        "external_response_supplied": bool(source_preflight.get("external_response_supplied", False)),
        "response_preflight_status": response_preflight.get("preflight_status", "unknown_response_preflight"),
        "package_assembly_status": package_assembly_plan.get("assembly_status", "unknown_assembly_status"),
        "staging_status": _package_staging_status(
            response_ready=response_ready,
            assembly_ready=assembly_ready,
            selected_channel_count=len(selected_channel_manifests),
        ),
        "selected_channel_manifest_count": len(selected_channel_manifests),
        "selected_table_manifest_count": sum(
            len(channel["table_manifests"]) for channel in selected_channel_manifests
        ),
        "selected_row_blueprint_count": sum(
            int(table.get("row_blueprint_count", 0) or 0)
            for channel in selected_channel_manifests
            for table in _list_of_dicts(channel.get("table_manifests"))
        ),
        "selected_value_payload_mapping_count": sum(
            int(table.get("value_payload_mapping_count", 0) or 0)
            for channel in selected_channel_manifests
            for table in _list_of_dicts(channel.get("table_manifests"))
        ),
        "candidate_channel_requirement_count": len(candidate_channel_requirements),
        "candidate_table_requirement_count": sum(
            len(channel["table_manifests"]) for channel in candidate_channel_requirements
        ),
        "selected_channel_ids": [str(channel["channel_id"]) for channel in selected_channel_manifests],
        "candidate_channel_ids": [str(channel["channel_id"]) for channel in candidate_channel_requirements],
        "package_pointers_to_set": [
            str(channel["package_pointer"])
            for channel in selected_channel_manifests
            if channel.get("package_pointer")
        ],
        "can_materialize_no_write_package_candidates": can_materialize,
        "can_route_to_external_activation_router": can_materialize,
        "can_resume_model_chain": False,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
        "selected_channel_manifests": selected_channel_manifests,
        "candidate_channel_requirements": candidate_channel_requirements,
        "router_validation_command": ".venv/bin/python experiments/run_external_activation_router.py",
        "next_operator_action": _package_staging_next_operator_action(can_materialize, selected_channel_manifests),
        "no_write_boundary": (
            "This staging manifest only tells an operator how to materialize filled field-activation response rows "
            "into external package directories for downstream preflight. It does not create field evidence, does not "
            "run replay/holdout, and cannot write actuator policy, release gate, legal conclusions or field-supported "
            "claims."
        ),
    }


def preflight_field_activation_materialized_package(
    staging_manifest: dict[str, Any],
    *,
    package_dir_path: str,
) -> dict[str, Any]:
    """Validate an operator-materialized package directory against the staging manifest."""

    selected_channels = _list_of_dicts(staging_manifest.get("selected_channel_manifests"))
    primary_channel = selected_channels[0] if selected_channels else {}
    package_pointer = str(
        primary_channel.get(
            "package_pointer",
            (staging_manifest.get("package_pointers_to_set") or ["FIELD_ACTIVATION_MATERIALIZED_PACKAGE_DIR"])[0]
            if isinstance(staging_manifest.get("package_pointers_to_set"), list)
            and staging_manifest.get("package_pointers_to_set")
            else "FIELD_ACTIVATION_MATERIALIZED_PACKAGE_DIR",
        )
    )
    staging_ready = bool(staging_manifest.get("can_materialize_no_write_package_candidates", False))
    if not staging_ready:
        return _materialized_package_preflight_result(
            package_pointer=package_pointer,
            package_dir_path=package_dir_path,
            status="field_activation_materialized_package_preflight_blocked_by_staging_manifest",
            selected_channels=selected_channels,
            blockers=[
                {
                    "blocker_id": "R8U105_STAGING_MANIFEST_NOT_READY",
                    "reason": str(staging_manifest.get("staging_status", "unknown_staging_status")),
                }
            ],
            next_operator_action="complete_field_activation_staging_manifest_before_materializing_package",
        )
    if not package_dir_path.strip():
        return _materialized_package_preflight_result(
            package_pointer=package_pointer,
            package_dir_path=package_dir_path,
            status="field_activation_materialized_package_preflight_waiting_for_package_dir",
            selected_channels=selected_channels,
            blockers=[
                {
                    "blocker_id": "R8U105_SET_MATERIALIZED_PACKAGE_DIR",
                    "reason": f"{package_pointer}:not_set",
                }
            ],
            next_operator_action=f"set_{package_pointer}",
        )
    package_dir = Path(package_dir_path).expanduser()
    blockers: list[dict[str, Any]] = []
    metadata_audit: dict[str, Any] = {}
    table_audits: list[dict[str, Any]] = []
    if not package_dir.exists():
        blockers.append({"blocker_id": "R8U105_PACKAGE_DIR_MISSING", "reason": f"{package_dir}:missing"})
    elif not package_dir.is_dir():
        blockers.append({"blocker_id": "R8U105_PACKAGE_PATH_NOT_DIRECTORY", "reason": f"{package_dir}:not_directory"})
    else:
        metadata_audit = _materialized_metadata_audit(package_dir)
        if metadata_audit["metadata_blocker_count"]:
            blockers.extend(metadata_audit["metadata_blockers"])
        for channel in selected_channels:
            for table_manifest in _list_of_dicts(channel.get("table_manifests")):
                audit = _materialized_table_audit(package_dir, table_manifest)
                table_audits.append(audit)
                blockers.extend(audit["table_blockers"])
    status = (
        "field_activation_materialized_package_preflight_ready_for_external_activation_router"
        if not blockers and selected_channels
        else "field_activation_materialized_package_preflight_blocked_by_package_gaps"
    )
    return _materialized_package_preflight_result(
        package_pointer=package_pointer,
        package_dir_path=package_dir_path,
        status=status,
        selected_channels=selected_channels,
        blockers=blockers,
        metadata_audit=metadata_audit,
        table_audits=table_audits,
        next_operator_action=(
            f"set_{package_pointer}_and_run_external_activation_router"
            if status == "field_activation_materialized_package_preflight_ready_for_external_activation_router"
            else _materialized_next_operator_action(blockers)
        ),
    )


def preview_field_activation_downstream_r7_preflight(
    staging_manifest: dict[str, Any],
    materialized_package_preflight: dict[str, Any],
    *,
    package_dir_path: str | None = None,
) -> dict[str, Any]:
    """Preview the downstream R7/Agent44 field replay gate without resuming the model chain."""

    del staging_manifest
    selected_channel_ids = [
        str(channel_id)
        for channel_id in materialized_package_preflight.get("selected_channel_ids", [])
        if str(channel_id)
    ]
    package_pointer = str(
        materialized_package_preflight.get("package_pointer", "REAL_FIELD_REPLAY_PACKAGE_DIR")
    )
    selected_path = (
        str(package_dir_path)
        if package_dir_path is not None
        else str(materialized_package_preflight.get("package_dir_path", ""))
    )
    upstream_ready = bool(
        materialized_package_preflight.get("can_route_to_external_activation_router", False)
    )
    if not upstream_ready:
        blocker = str(
            materialized_package_preflight.get(
                "highest_priority_blocker",
                "R8U121_MATERIALIZED_PACKAGE_PREFLIGHT_NOT_READY",
            )
        ) or "R8U121_MATERIALIZED_PACKAGE_PREFLIGHT_NOT_READY"
        return _downstream_r7_preview_result(
            package_pointer=package_pointer,
            package_dir_path=selected_path,
            selected_channel_ids=selected_channel_ids,
            status="field_activation_downstream_r7_preview_blocked_by_materialized_package_preflight",
            preview_executed=False,
            r7_preflight={},
            highest_priority_blocker=blocker,
            next_operator_action=str(
                materialized_package_preflight.get(
                    "next_operator_action",
                    "complete_materialized_package_preflight_before_r7_preview",
                )
            ),
            upstream_materialized_package_status=str(
                materialized_package_preflight.get("preflight_status", "unknown_materialized_preflight")
            ),
        )
    if package_pointer != "REAL_FIELD_REPLAY_PACKAGE_DIR" and "R7_REAL_FIELD_PACKAGE" not in selected_channel_ids:
        return _downstream_r7_preview_result(
            package_pointer=package_pointer,
            package_dir_path=selected_path,
            selected_channel_ids=selected_channel_ids,
            status="field_activation_downstream_r7_preview_not_applicable_non_r7_channel",
            preview_executed=False,
            r7_preflight={},
            highest_priority_blocker="R8U121_NON_R7_CHANNEL",
            next_operator_action="run_channel_specific_downstream_preflight_before_model_chain_resume",
            upstream_materialized_package_status=str(
                materialized_package_preflight.get("preflight_status", "unknown_materialized_preflight")
            ),
        )
    if not selected_path.strip():
        return _downstream_r7_preview_result(
            package_pointer=package_pointer,
            package_dir_path=selected_path,
            selected_channel_ids=selected_channel_ids,
            status="field_activation_downstream_r7_preview_waiting_for_package_dir",
            preview_executed=False,
            r7_preflight={},
            highest_priority_blocker="R8U121_SET_R7_PACKAGE_DIR",
            next_operator_action=f"set_{package_pointer}_before_r7_preview",
            upstream_materialized_package_status=str(
                materialized_package_preflight.get("preflight_status", "unknown_materialized_preflight")
            ),
        )
    try:
        r7_preflight = preflight_field_replay_package(Path(selected_path).expanduser())
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return _downstream_r7_preview_result(
            package_pointer=package_pointer,
            package_dir_path=selected_path,
            selected_channel_ids=selected_channel_ids,
            status="field_activation_downstream_r7_preview_preflight_error",
            preview_executed=True,
            r7_preflight={
                "status": "field_activation_downstream_r7_preview_error",
                "error_type": type(exc).__name__,
                "error_message": str(exc),
            },
            highest_priority_blocker="R8U121_R7_PREFLIGHT_ERROR",
            next_operator_action="repair_materialized_package_until_r7_preflight_can_run",
            upstream_materialized_package_status=str(
                materialized_package_preflight.get("preflight_status", "unknown_materialized_preflight")
            ),
        )
    r7_ready = bool(r7_preflight.get("can_pass_to_timestamped_replay", False))
    return _downstream_r7_preview_result(
        package_pointer=package_pointer,
        package_dir_path=selected_path,
        selected_channel_ids=selected_channel_ids,
        status=(
            "field_activation_downstream_r7_preview_ready_for_agent42_replay_review"
            if r7_ready
            else "field_activation_downstream_r7_preview_blocked_by_r7_preflight"
        ),
        preview_executed=True,
        r7_preflight=r7_preflight,
        highest_priority_blocker="" if r7_ready else _downstream_r7_highest_blocker(r7_preflight),
        next_operator_action=(
            "run_external_activation_router_then_r7_pipeline_under_no_write_review"
            if r7_ready
            else _downstream_r7_next_operator_action(r7_preflight)
        ),
        upstream_materialized_package_status=str(
            materialized_package_preflight.get("preflight_status", "unknown_materialized_preflight")
        ),
    )


def preview_field_activation_downstream_path_endpoint_preflight(
    staging_manifest: dict[str, Any],
    materialized_package_preflight: dict[str, Any],
    *,
    package_dir_path: str | None = None,
) -> dict[str, Any]:
    """Preview the downstream R8u66/Agent54 path-endpoint label gate without writes."""

    selected_channel_ids = [
        str(channel_id)
        for channel_id in materialized_package_preflight.get("selected_channel_ids", [])
        if str(channel_id)
    ]
    package_pointer = str(
        materialized_package_preflight.get("package_pointer", "FIELD_PATH_ENDPOINT_LABEL_PACKAGE_DIR")
    )
    selected_path = (
        str(package_dir_path)
        if package_dir_path is not None
        else str(materialized_package_preflight.get("package_dir_path", ""))
    )
    upstream_status = str(
        materialized_package_preflight.get("preflight_status", "unknown_materialized_preflight")
    )
    upstream_ready = bool(
        materialized_package_preflight.get("can_route_to_external_activation_router", False)
    )
    path_contract = build_field_path_endpoint_label_package_contract()
    if not upstream_ready:
        blocker = str(
            materialized_package_preflight.get(
                "highest_priority_blocker",
                "R8U122_MATERIALIZED_PACKAGE_PREFLIGHT_NOT_READY",
            )
        ) or "R8U122_MATERIALIZED_PACKAGE_PREFLIGHT_NOT_READY"
        return _downstream_path_endpoint_preview_result(
            package_pointer=package_pointer,
            package_dir_path=selected_path,
            selected_channel_ids=selected_channel_ids,
            status=(
                "field_activation_downstream_path_endpoint_preview_blocked_by_materialized_package_preflight"
            ),
            preview_executed=False,
            path_endpoint_preflight={},
            highest_priority_blocker=blocker,
            next_operator_action=str(
                materialized_package_preflight.get(
                    "next_operator_action",
                    "complete_materialized_package_preflight_before_path_endpoint_preview",
                )
            ),
            upstream_materialized_package_status=upstream_status,
        )
    if not _staging_has_path_endpoint_preview_scope(staging_manifest, selected_channel_ids):
        return _downstream_path_endpoint_preview_result(
            package_pointer=package_pointer,
            package_dir_path=selected_path,
            selected_channel_ids=selected_channel_ids,
            status="field_activation_downstream_path_endpoint_preview_not_applicable_no_path_scope",
            preview_executed=False,
            path_endpoint_preflight={},
            highest_priority_blocker="R8U122_NO_PATH_ENDPOINT_SCOPE",
            next_operator_action="skip_path_endpoint_preview_or_stage_path_endpoint_label_package",
            upstream_materialized_package_status=upstream_status,
        )
    if not selected_path.strip():
        return _downstream_path_endpoint_preview_result(
            package_pointer=package_pointer,
            package_dir_path=selected_path,
            selected_channel_ids=selected_channel_ids,
            status="field_activation_downstream_path_endpoint_preview_waiting_for_package_dir",
            preview_executed=False,
            path_endpoint_preflight={},
            highest_priority_blocker="R8U122_SET_PATH_ENDPOINT_PACKAGE_DIR",
            next_operator_action=f"set_{package_pointer}_before_path_endpoint_preview",
            upstream_materialized_package_status=upstream_status,
        )
    try:
        csv_package = _read_path_endpoint_csv_package(Path(selected_path).expanduser(), path_contract)
        path_endpoint_preflight = preflight_field_path_endpoint_label_package(
            csv_package,
            contract=path_contract,
        )
    except (OSError, csv.Error, ValueError) as exc:
        return _downstream_path_endpoint_preview_result(
            package_pointer=package_pointer,
            package_dir_path=selected_path,
            selected_channel_ids=selected_channel_ids,
            status="field_activation_downstream_path_endpoint_preview_preflight_error",
            preview_executed=True,
            path_endpoint_preflight={
                "preflight_status": "field_activation_downstream_path_endpoint_preview_error",
                "error_type": type(exc).__name__,
                "error_message": str(exc),
            },
            highest_priority_blocker="R8U122_PATH_ENDPOINT_PREFLIGHT_ERROR",
            next_operator_action="repair_materialized_package_until_path_endpoint_preflight_can_run",
            upstream_materialized_package_status=upstream_status,
        )
    ready = bool(path_endpoint_preflight.get("can_route_to_field_layout_holdout", False))
    return _downstream_path_endpoint_preview_result(
        package_pointer=package_pointer,
        package_dir_path=selected_path,
        selected_channel_ids=selected_channel_ids,
        status=(
            "field_activation_downstream_path_endpoint_preview_ready_for_layout_holdout_review"
            if ready
            else "field_activation_downstream_path_endpoint_preview_blocked_by_path_endpoint_preflight"
        ),
        preview_executed=True,
        path_endpoint_preflight=path_endpoint_preflight,
        highest_priority_blocker="" if ready else _downstream_path_endpoint_highest_blocker(
            path_endpoint_preflight
        ),
        next_operator_action=(
            "route_to_field_layout_holdout_review_under_no_write_boundary"
            if ready
            else str(
                path_endpoint_preflight.get(
                    "next_operator_action",
                    "fix_field_path_endpoint_label_package_preflight_blockers",
                )
            )
        ),
        upstream_materialized_package_status=upstream_status,
    )


def build_field_activation_external_readiness_gate(
    response_source_preflight: dict[str, Any],
    response_repair_work_order: dict[str, Any],
    response_preflight: dict[str, Any],
    package_assembly_plan: dict[str, Any],
    package_staging_manifest: dict[str, Any],
    materialized_package_preflight: dict[str, Any],
    schema_preflight: dict[str, Any],
    response_coherence_audit: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Sequence response, staging and materialized-package checks into one operator gate."""

    steps = [
        _external_readiness_step(
            "response_source",
            status=str(response_source_preflight.get("source_preflight_status", "unknown_source_preflight")),
            ready=bool(
                response_source_preflight.get("external_response_supplied", False)
                and response_source_preflight.get("can_run_response_preflight", False)
            ),
            blocker_id=(
                "R8U106_SUBMIT_FIELD_ACTIVATION_RESPONSE"
                if bool(response_source_preflight.get("using_default_template", False))
                else "R8U106_REPAIR_FIELD_ACTIVATION_RESPONSE_SOURCE"
            ),
            next_operator_action=str(
                response_source_preflight.get(
                    "next_operator_action",
                    "set_FIELD_ACTIVATION_RESPONSE_PATH_to_filled_external_response_json",
                )
            ),
            evidence={
                "source_env_var": response_source_preflight.get("source_env_var", "FIELD_ACTIVATION_RESPONSE_PATH"),
                "external_response_supplied": response_source_preflight.get("external_response_supplied", False),
                "using_default_template": response_source_preflight.get("using_default_template", False),
            },
        ),
        _external_readiness_step(
            "schema_preflight",
            status=str(schema_preflight.get("schema_preflight_status", "unknown_schema_preflight")),
            ready=bool(schema_preflight.get("can_validate_field_activation_response_structure", False)),
            blocker_id="R8U106_REPAIR_FIELD_ACTIVATION_SCHEMA",
            next_operator_action="repair_response_or_assembly_schema_fields",
            evidence={
                "response_top_level_missing_count": schema_preflight.get("response_top_level_missing_count", 0),
                "evidence_row_missing_field_count": schema_preflight.get("evidence_row_missing_field_count", 0),
                "no_write_violation_count": schema_preflight.get("no_write_violation_count", 0),
            },
        ),
        _external_readiness_step(
            "response_preflight",
            status=str(response_preflight.get("preflight_status", "unknown_response_preflight")),
            ready=bool(response_preflight.get("can_route_to_external_activation_router", False)),
            blocker_id="R8U106_REPAIR_FIELD_ACTIVATION_RESPONSE_ROWS",
            next_operator_action=str(
                response_repair_work_order.get(
                    "next_operator_action",
                    "repair_field_provenance_alignment_channels_and_no_write_confirmations",
                )
            ),
            evidence={
                "expected_response_row_count": response_preflight.get("expected_response_row_count", 0),
                "template_marker_row_count": response_preflight.get("template_marker_row_count", 0),
                "non_field_row_count": response_preflight.get("non_field_row_count", 0),
            },
        ),
    ]
    if response_coherence_audit is not None:
        steps.append(
            _external_readiness_step(
                "response_coherence_audit",
                status=str(response_coherence_audit.get("audit_status", "unknown_response_coherence_audit")),
                ready=bool(response_coherence_audit.get("can_route_to_package_assembly", False)),
                blocker_id=str(
                    response_coherence_audit.get(
                        "highest_priority_blocker",
                        "R8U106_REPAIR_FIELD_ACTIVATION_RESPONSE_COHERENCE",
                    )
                )
                or "R8U106_REPAIR_FIELD_ACTIVATION_RESPONSE_COHERENCE",
                next_operator_action=str(
                    response_coherence_audit.get(
                        "next_operator_action",
                        "repair_field_activation_response_coherence_before_package_assembly",
                    )
                ),
                evidence={
                    "hard_blocker_count": response_coherence_audit.get("hard_blocker_count", 0),
                    "warning_count": response_coherence_audit.get("warning_count", 0),
                    "highest_priority_blocker": response_coherence_audit.get("highest_priority_blocker", ""),
                },
            )
        )
    steps.extend(
        [
            _external_readiness_step(
                "repair_work_order",
                status=str(response_repair_work_order.get("work_order_status", "unknown_repair_work_order")),
                ready=_safe_int(response_repair_work_order.get("repair_item_count")) == 0,
                blocker_id=str(
                    response_repair_work_order.get(
                        "highest_priority_repair_id",
                        "R8U106_COMPLETE_RESPONSE_REPAIR_WORK_ORDER",
                    )
                )
                or "R8U106_COMPLETE_RESPONSE_REPAIR_WORK_ORDER",
                next_operator_action=str(
                    response_repair_work_order.get(
                        "next_operator_action",
                        "inspect_repair_items_before_any_downstream_action",
                    )
                ),
                evidence={
                    "repair_item_count": response_repair_work_order.get("repair_item_count", 0),
                    "highest_priority_repair_id": response_repair_work_order.get("highest_priority_repair_id", ""),
                },
            ),
            _external_readiness_step(
            "package_assembly",
            status=str(package_assembly_plan.get("assembly_status", "unknown_package_assembly")),
            ready=bool(package_assembly_plan.get("can_stage_external_package_candidates", False)),
            blocker_id="R8U106_COMPLETE_PACKAGE_ASSEMBLY",
            next_operator_action="regenerate_package_assembly_plan_after_response_preflight_ready",
            evidence={
                "channel_plan_count": package_assembly_plan.get("channel_plan_count", 0),
                "candidate_channel_plan_count": package_assembly_plan.get("candidate_channel_plan_count", 0),
            },
            ),
            _external_readiness_step(
            "package_staging",
            status=str(package_staging_manifest.get("staging_status", "unknown_package_staging")),
            ready=bool(package_staging_manifest.get("can_materialize_no_write_package_candidates", False)),
            blocker_id="R8U106_COMPLETE_PACKAGE_STAGING",
            next_operator_action=str(
                package_staging_manifest.get(
                    "next_operator_action",
                    "complete_response_preflight_and_package_assembly_before_staging",
                )
            ),
            evidence={
                "selected_channel_manifest_count": package_staging_manifest.get(
                    "selected_channel_manifest_count",
                    0,
                ),
                "candidate_channel_requirement_count": package_staging_manifest.get(
                    "candidate_channel_requirement_count",
                    0,
                ),
                "package_pointers_to_set": package_staging_manifest.get("package_pointers_to_set", []),
            },
            ),
            _external_readiness_step(
            "materialized_package_preflight",
            status=str(
                materialized_package_preflight.get(
                    "preflight_status",
                    "unknown_materialized_package_preflight",
                )
            ),
            ready=bool(materialized_package_preflight.get("can_route_to_external_activation_router", False)),
            blocker_id=str(
                materialized_package_preflight.get(
                    "highest_priority_blocker",
                    "R8U106_COMPLETE_MATERIALIZED_PACKAGE_PREFLIGHT",
                )
            )
            or "R8U106_COMPLETE_MATERIALIZED_PACKAGE_PREFLIGHT",
            next_operator_action=str(
                materialized_package_preflight.get(
                    "next_operator_action",
                    "complete_field_activation_staging_manifest_before_materializing_package",
                )
            ),
            evidence={
                "package_pointer": materialized_package_preflight.get("package_pointer", ""),
                "blocker_count": materialized_package_preflight.get("blocker_count", 0),
                "highest_priority_blocker": materialized_package_preflight.get("highest_priority_blocker", ""),
            },
            ),
        ]
    )
    blocked_step = next((step for step in steps if not step["ready"]), None)
    ready = blocked_step is None
    return {
        "gate_id": "R8u106_field_activation_external_readiness_gate",
        "gate_type": "field_activation_external_handoff_sequence_gate",
        "gate_status": (
            "field_activation_external_readiness_ready_for_external_activation_router"
            if ready
            else _external_readiness_blocked_status(str(blocked_step["step_id"]))
        ),
        "ready_step_count": sum(1 for step in steps if step["ready"]),
        "blocked_step_count": sum(1 for step in steps if not step["ready"]),
        "total_step_count": len(steps),
        "first_blocked_step": "" if ready else str(blocked_step["step_id"]),
        "highest_priority_blocker": "" if ready else str(blocked_step["blocker_id"]),
        "next_operator_action": (
            "run_external_activation_router_with_materialized_package_pointer"
            if ready
            else str(blocked_step["next_operator_action"])
        ),
        "can_submit_to_external_activation_router": ready,
        "can_resume_model_chain": False,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
        "sequence_steps": steps,
        "operator_sequence": [
            "Submit a filled FIELD_ACTIVATION_RESPONSE_PATH before materializing any package directory.",
            "Pass schema, response preflight and repair work order before package assembly/staging.",
            "Materialize the selected package directory from the staging manifest.",
            "Set the selected package pointer, such as REAL_FIELD_REPLAY_PACKAGE_DIR, only after the directory preflight passes.",
            "Run experiments/run_external_activation_router.py, then downstream R7/Agent44 or path/endpoint preflights.",
        ],
        "no_write_boundary": (
            "This readiness gate only orders existing field-activation preflights. It does not create field "
            "evidence, does not run replay/holdout, does not resume the model chain, and cannot write actuator "
            "policy, release gate, legal conclusions or field-supported claims."
        ),
    }


def build_field_activation_response_submission_packet(
    response_template: dict[str, Any],
    response_source_preflight: dict[str, Any],
    response_repair_work_order: dict[str, Any],
    response_preflight: dict[str, Any],
    external_readiness_gate: dict[str, Any],
    *,
    response_template_path: str,
    response_coherence_audit: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Package the operator-facing response-submission contract without creating evidence."""

    status = _response_submission_packet_status(
        response_source_preflight=response_source_preflight,
        response_preflight=response_preflight,
        external_readiness_gate=external_readiness_gate,
    )
    source_env_var = str(response_source_preflight.get("source_env_var", "FIELD_ACTIVATION_RESPONSE_PATH"))
    next_action = _response_submission_next_operator_action(
        status=status,
        response_source_preflight=response_source_preflight,
        response_repair_work_order=response_repair_work_order,
        external_readiness_gate=external_readiness_gate,
    )
    can_route = bool(response_preflight.get("can_route_to_external_activation_router", False))
    top_repair_items = _response_submission_top_repair_items(response_repair_work_order)
    return {
        "packet_id": "R8u108_field_activation_response_submission_packet",
        "packet_type": "field_activation_response_submission_packet",
        "packet_status": status,
        "source_env_var": source_env_var,
        "response_template_path": response_template_path,
        "required_response_row_count": int(response_template.get("required_response_row_count", 0) or 0),
        "source_preflight_status": response_source_preflight.get("source_preflight_status", "unknown"),
        "response_preflight_status": response_preflight.get("preflight_status", "unknown"),
        "response_coherence_audit_status": (response_coherence_audit or {}).get(
            "audit_status",
            "field_activation_response_coherence_audit_not_supplied",
        ),
        "response_coherence_hard_blocker_count": int(
            (response_coherence_audit or {}).get("hard_blocker_count", 0) or 0
        ),
        "response_coherence_warning_count": int(
            (response_coherence_audit or {}).get("warning_count", 0) or 0
        ),
        "repair_work_order_status": response_repair_work_order.get("work_order_status", "unknown"),
        "external_readiness_gate_status": external_readiness_gate.get("gate_status", "unknown"),
        "first_blocked_step": external_readiness_gate.get("first_blocked_step", ""),
        "highest_priority_blocker": (
            external_readiness_gate.get("highest_priority_blocker")
            or response_repair_work_order.get("highest_priority_repair_id")
            or ""
        ),
        "repair_item_count": int(response_repair_work_order.get("repair_item_count", 0) or 0),
        "highest_priority_repair_id": response_repair_work_order.get("highest_priority_repair_id", ""),
        "top_repair_items": top_repair_items,
        "required_top_level_fields": list(RESPONSE_TEMPLATE_REQUIRED_FIELDS),
        "required_evidence_row_fields": list(RESPONSE_ROW_REQUIRED_FIELDS),
        "operator_submission_steps": [
            f"Open {response_template_path} and copy it to an external response JSON before editing.",
            "Replace every TODO/template marker with real field provenance, batch, timestamp, node, sensor, lab and operation evidence.",
            f"Set {source_env_var}=/path/to/filled_response.json.",
            f"Run {source_env_var}=/path/to/filled_response.json .venv/bin/python experiments/run_field_activation_matrix.py.",
            "Inspect field_activation_response_source_preflight, field_activation_response_preflight and field_activation_response_repair_work_order.",
            "Only after response, repair, assembly, staging and materialized package preflights pass, run the external activation router.",
        ],
        "validation_commands": [
            f"{source_env_var}=/path/to/filled_response.json .venv/bin/python experiments/run_field_activation_matrix.py",
            ".venv/bin/python experiments/run_agent50_model_core_governance.py",
            ".venv/bin/python experiments/run_external_activation_router.py",
        ],
        "next_operator_action": next_action,
        "can_submit_to_response_preflight": bool(
            response_source_preflight.get("can_run_response_preflight", False)
        ),
        "can_route_to_external_activation_router": can_route,
        "can_resume_model_chain": False,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
        "no_write_boundary": (
            "This submission packet only tells an operator how to submit and validate a filled field-activation "
            "response JSON. It does not generate field evidence, does not run replay/holdout, does not materialize "
            "a package directory, and cannot write actuator policy, release gate, legal conclusions or "
            "field-supported claims."
        ),
    }


def build_field_activation_schema_contract(
    matrix: dict[str, Any],
    response_template: dict[str, Any],
    assembly_plan: dict[str, Any],
) -> dict[str, Any]:
    """Describe the machine-checkable structure required before field package staging."""

    return {
        "schema_contract_id": "R8u100_field_activation_schema_contract",
        "schema_contract_status": "field_activation_schema_contract_ready",
        "source_interface_id": matrix.get("interface_id", "unknown_field_activation_matrix"),
        "source_response_template_id": response_template.get("template_id", "unknown_response_template"),
        "source_assembly_plan_id": assembly_plan.get("plan_id", "unknown_assembly_plan"),
        "schema_scope": [
            "field_activation_response_template_structure",
            "field_activation_package_assembly_plan_structure",
            "no_write_boundary_structure",
        ],
        "response_template_schema": {
            "required_top_level_fields": list(RESPONSE_TEMPLATE_REQUIRED_FIELDS),
            "required_evidence_row_fields": list(RESPONSE_ROW_REQUIRED_FIELDS),
            "allowed_package_type": "field_activation_evidence_response",
            "expected_response_row_count": response_template.get("required_response_row_count", 0),
            "template_markers_allowed_for_schema_preflight": True,
            "template_markers_allowed_for_field_evidence_preflight": False,
        },
        "package_assembly_schema": {
            "required_top_level_fields": list(PACKAGE_ASSEMBLY_REQUIRED_FIELDS),
            "required_channel_plan_fields": list(PACKAGE_CHANNEL_PLAN_REQUIRED_FIELDS),
            "required_table_assembly_fields": list(PACKAGE_TABLE_ASSEMBLY_REQUIRED_FIELDS),
            "allowed_assembly_statuses": [
                "field_activation_package_assembly_plan_blocked_by_response_preflight",
                "field_activation_package_assembly_plan_blocked_by_response_coherence_audit",
                "field_activation_package_assembly_plan_ready_for_no_write_package_staging",
            ],
            "candidate_channel_plans_required": True,
        },
        "no_write_policy": {
            "assembly_plan_boolean_fields_required_false": [
                "can_resume_model_chain",
                "can_write_to_actuator",
                "can_write_to_release_gate",
            ],
            "channel_plan_boolean_fields_required_false": [
                "can_resume_model_chain",
                "can_write_to_actuator",
                "can_write_to_release_gate",
            ],
            "response_row_confirmation_field": "no_write_boundary_confirmed",
            "response_row_confirmation_value_is_not_required_for_schema_preflight": True,
        },
        "capability_boundary": {
            "can_validate_field_activation_response_structure": True,
            "can_resume_model_chain": False,
            "can_write_to_actuator": False,
            "can_write_to_release_gate": False,
        },
        "no_write_boundary": (
            "This schema contract validates structure only. It permits template markers at schema-preflight time, "
            "but it cannot convert template/sample rows into field evidence and cannot write actuator policy, "
            "release gate, legal conclusions or field-supported claims."
        ),
    }


def preflight_field_activation_schema_contract(
    schema_contract: dict[str, Any],
    response_template: dict[str, Any],
    assembly_plan: dict[str, Any],
) -> dict[str, Any]:
    """Check whether response and assembly artifacts satisfy the lightweight schema contract."""

    response_schema = _dict(schema_contract.get("response_template_schema"))
    assembly_schema = _dict(schema_contract.get("package_assembly_schema"))
    response_required = _string_list(
        response_schema.get("required_top_level_fields"),
        default=RESPONSE_TEMPLATE_REQUIRED_FIELDS,
    )
    row_required = _string_list(
        response_schema.get("required_evidence_row_fields"),
        default=RESPONSE_ROW_REQUIRED_FIELDS,
    )
    assembly_required = _string_list(
        assembly_schema.get("required_top_level_fields"),
        default=PACKAGE_ASSEMBLY_REQUIRED_FIELDS,
    )
    channel_required = _string_list(
        assembly_schema.get("required_channel_plan_fields"),
        default=PACKAGE_CHANNEL_PLAN_REQUIRED_FIELDS,
    )
    table_required = _string_list(
        assembly_schema.get("required_table_assembly_fields"),
        default=PACKAGE_TABLE_ASSEMBLY_REQUIRED_FIELDS,
    )

    response_top_missing = _missing_fields(response_template, response_required)
    evidence_rows = _list_of_dicts(response_template.get("evidence_rows"))
    evidence_row_missing = _missing_by_index(evidence_rows, row_required, id_field="response_row_id")
    expected_count = _safe_int(response_schema.get("expected_response_row_count"))
    response_count_ok = len(evidence_rows) == expected_count
    package_type_ok = (
        str(response_template.get("package_type", ""))
        == str(response_schema.get("allowed_package_type", "field_activation_evidence_response"))
    )

    assembly_top_missing = _missing_fields(assembly_plan, assembly_required)
    channel_plans = _list_of_dicts(assembly_plan.get("channel_plans"))
    candidate_channel_plans = _list_of_dicts(assembly_plan.get("candidate_channel_plans"))
    all_channel_plans = channel_plans + candidate_channel_plans
    channel_missing = _missing_by_index(all_channel_plans, channel_required, id_field="channel_id")
    table_rows = [
        table
        for channel in all_channel_plans
        for table in _list_of_dicts(channel.get("table_assemblies"))
    ]
    table_missing = _missing_by_index(table_rows, table_required, id_field="table_name")
    allowed_statuses = set(
        _string_list(
            assembly_schema.get("allowed_assembly_statuses"),
            default=(
                "field_activation_package_assembly_plan_blocked_by_response_preflight",
                "field_activation_package_assembly_plan_blocked_by_response_coherence_audit",
                "field_activation_package_assembly_plan_ready_for_no_write_package_staging",
            ),
        )
    )
    assembly_status_ok = str(assembly_plan.get("assembly_status", "")) in allowed_statuses
    candidate_channel_plans_ok = bool(candidate_channel_plans) or not bool(
        assembly_schema.get("candidate_channel_plans_required", True)
    )
    no_write_violations = _no_write_schema_violations(assembly_plan, all_channel_plans)
    passed = bool(
        schema_contract.get("schema_contract_status") == "field_activation_schema_contract_ready"
        and package_type_ok
        and response_count_ok
        and assembly_status_ok
        and candidate_channel_plans_ok
        and not response_top_missing
        and not evidence_row_missing
        and not assembly_top_missing
        and not channel_missing
        and not table_missing
        and not no_write_violations
    )
    return {
        "schema_preflight_id": "R8u100_field_activation_schema_preflight",
        "schema_contract_id": schema_contract.get("schema_contract_id", ""),
        "schema_preflight_status": (
            "field_activation_schema_preflight_passed"
            if passed
            else "field_activation_schema_preflight_blocked"
        ),
        "package_type_ok": package_type_ok,
        "response_row_count_ok": response_count_ok,
        "expected_response_row_count": expected_count,
        "provided_response_row_count": len(evidence_rows),
        "response_top_level_missing_count": len(response_top_missing),
        "evidence_row_missing_field_count": sum(len(row["missing_fields"]) for row in evidence_row_missing),
        "assembly_top_level_missing_count": len(assembly_top_missing),
        "assembly_channel_missing_field_count": sum(len(row["missing_fields"]) for row in channel_missing),
        "assembly_table_missing_field_count": sum(len(row["missing_fields"]) for row in table_missing),
        "assembly_status_ok": assembly_status_ok,
        "candidate_channel_plans_ok": candidate_channel_plans_ok,
        "no_write_violation_count": len(no_write_violations),
        "can_validate_field_activation_response_structure": passed,
        "can_resume_model_chain": False,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
        "response_top_level_missing_fields": response_top_missing,
        "evidence_row_missing_fields": evidence_row_missing[:20],
        "assembly_top_level_missing_fields": assembly_top_missing,
        "assembly_channel_missing_fields": channel_missing[:20],
        "assembly_table_missing_fields": table_missing[:20],
        "no_write_violations": no_write_violations[:20],
        "next_operator_action": (
            "schema_structure_ready_fill_real_field_values_then_run_field_activation_response_preflight"
            if passed
            else "repair_field_activation_schema_structure_before_field_package_staging"
        ),
        "no_write_boundary": (
            "Passing this schema preflight only proves that the response template and package assembly plan "
            "have the required fields and no-write boundary flags. It does not prove field evidence and cannot "
            "authorize model-chain resume, actuator writes or release-gate writes."
        ),
    }


def build_field_activation_response_repair_work_order(
    response_source_preflight: dict[str, Any],
    response_preflight: dict[str, Any],
    schema_preflight: dict[str, Any],
    package_assembly_plan: dict[str, Any],
    response_coherence_audit: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Convert field-activation response blockers into an operator repair work order."""

    repair_items: list[dict[str, Any]] = []
    _extend_source_repair_items(repair_items, response_source_preflight)
    _extend_schema_repair_items(repair_items, schema_preflight)
    _extend_response_repair_items(repair_items, response_preflight)
    if response_coherence_audit is not None:
        _extend_coherence_repair_items(repair_items, response_coherence_audit)
    _extend_assembly_repair_items(repair_items, package_assembly_plan)
    repair_items = sorted(repair_items, key=lambda item: (int(item["priority"]), str(item["repair_id"])))
    status = _response_repair_work_order_status(
        repair_items=repair_items,
        response_source_preflight=response_source_preflight,
        response_preflight=response_preflight,
        schema_preflight=schema_preflight,
        package_assembly_plan=package_assembly_plan,
        response_coherence_audit=response_coherence_audit,
    )
    return {
        "work_order_id": "R8u102_field_activation_response_repair_work_order",
        "work_order_status": status,
        "source_preflight_status": response_source_preflight.get("source_preflight_status", "unknown"),
        "response_preflight_status": response_preflight.get("preflight_status", "unknown"),
        "response_coherence_audit_status": (response_coherence_audit or {}).get(
            "audit_status",
            "field_activation_response_coherence_audit_not_supplied",
        ),
        "schema_preflight_status": schema_preflight.get("schema_preflight_status", "unknown"),
        "package_assembly_status": package_assembly_plan.get("assembly_status", "unknown"),
        "repair_item_count": len(repair_items),
        "highest_priority_repair_id": repair_items[0]["repair_id"] if repair_items else "",
        "can_route_to_response_preflight": bool(
            response_source_preflight.get("can_run_response_preflight", False)
        ),
        "can_route_to_package_assembly": bool(
            response_preflight.get("can_route_to_external_activation_router", False)
        ),
        "can_stage_external_package_candidates": bool(
            package_assembly_plan.get("can_stage_external_package_candidates", False)
        ),
        "can_resume_model_chain": False,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
        "repair_items": repair_items,
        "next_operator_action": _response_repair_next_operator_action(status),
        "no_write_boundary": (
            "This repair work order only tells an operator how to fix the field-activation response package. "
            "It cannot create field evidence, run replay/holdout, resume the model chain, or write actuator "
            "policy, release gate, legal conclusions or field-supported claims."
        ),
    }


def _extend_source_repair_items(
    repair_items: list[dict[str, Any]],
    source_preflight: dict[str, Any],
) -> None:
    status = str(source_preflight.get("source_preflight_status", "unknown"))
    if status == "field_activation_response_source_using_default_template":
        repair_items.append(
            _repair_item(
                "R8U102_SUBMIT_FIELD_ACTIVATION_RESPONSE",
                priority=5,
                scope="response_source",
                issue="No external field activation response was supplied; default template is still being preflighted.",
                required_action=(
                    "Fill outputs/model_core_governance/field_activation_response_template.json with real "
                    "field provenance, save it as an external response JSON, then set FIELD_ACTIVATION_RESPONSE_PATH."
                ),
                evidence={"source_env_var": source_preflight.get("source_env_var", "FIELD_ACTIVATION_RESPONSE_PATH")},
            )
        )
    elif not bool(source_preflight.get("can_run_response_preflight", False)):
        repair_items.append(
            _repair_item(
                "R8U102_REPAIR_RESPONSE_SOURCE_FILE",
                priority=5,
                scope="response_source",
                issue="The supplied FIELD_ACTIVATION_RESPONSE_PATH cannot enter response preflight.",
                required_action=(
                    "Repair the external JSON path, encoding, root object shape, or selected response structure, "
                    "then rerun experiments/run_field_activation_matrix.py."
                ),
                evidence={
                    "source_path": source_preflight.get("source_path", ""),
                    "load_status": source_preflight.get("load_status", ""),
                    "root_object_ok": source_preflight.get("root_object_ok", False),
                },
            )
        )


def _extend_schema_repair_items(
    repair_items: list[dict[str, Any]],
    schema_preflight: dict[str, Any],
) -> None:
    if str(schema_preflight.get("schema_preflight_status", "")) == "field_activation_schema_preflight_passed":
        return
    if schema_preflight.get("response_top_level_missing_fields"):
        repair_items.append(
            _repair_item(
                "R8U102_REPAIR_RESPONSE_TOP_LEVEL_SCHEMA",
                priority=20,
                scope="response_schema",
                issue="The response JSON is missing required top-level fields.",
                required_action="Add the missing top-level fields before evidence-row preflight.",
                evidence={"missing_fields": schema_preflight.get("response_top_level_missing_fields", [])},
            )
        )
    if _safe_int(schema_preflight.get("evidence_row_missing_field_count")) > 0:
        repair_items.append(
            _repair_item(
                "R8U102_REPAIR_RESPONSE_ROW_SCHEMA",
                priority=20,
                scope="response_schema",
                issue="One or more evidence rows are missing required fields.",
                required_action="Fill all required evidence-row fields before field evidence preflight.",
                evidence={"missing_rows": schema_preflight.get("evidence_row_missing_fields", [])},
            )
        )
    if _safe_int(schema_preflight.get("assembly_top_level_missing_count")) > 0:
        repair_items.append(
            _repair_item(
                "R8U102_REPAIR_ASSEMBLY_TOP_LEVEL_SCHEMA",
                priority=30,
                scope="assembly_schema",
                issue="The package assembly plan is missing top-level fields.",
                required_action="Regenerate the field activation assembly plan after repairing the response JSON.",
                evidence={"missing_fields": schema_preflight.get("assembly_top_level_missing_fields", [])},
            )
        )
    if _safe_int(schema_preflight.get("assembly_channel_missing_field_count")) > 0:
        repair_items.append(
            _repair_item(
                "R8U102_REPAIR_ASSEMBLY_CHANNEL_SCHEMA",
                priority=30,
                scope="assembly_schema",
                issue="One or more assembly channel plans are missing required fields.",
                required_action="Regenerate or repair channel-level assembly plans before package staging.",
                evidence={"missing_channels": schema_preflight.get("assembly_channel_missing_fields", [])},
            )
        )
    if _safe_int(schema_preflight.get("assembly_table_missing_field_count")) > 0:
        repair_items.append(
            _repair_item(
                "R8U102_REPAIR_ASSEMBLY_TABLE_SCHEMA",
                priority=30,
                scope="assembly_schema",
                issue="One or more assembly table plans are missing required fields.",
                required_action="Regenerate or repair table-level assembly plans before package staging.",
                evidence={"missing_tables": schema_preflight.get("assembly_table_missing_fields", [])},
            )
        )
    if _safe_int(schema_preflight.get("no_write_violation_count")) > 0:
        repair_items.append(
            _repair_item(
                "R8U102_REPAIR_NO_WRITE_SCHEMA_VIOLATION",
                priority=5,
                scope="protective_boundary",
                issue="A schema artifact violates no-write boundary flags.",
                required_action=(
                    "Set can_resume_model_chain, can_write_to_actuator, and can_write_to_release_gate to false "
                    "until downstream replay/holdout/human-review gates pass."
                ),
                evidence={"violations": schema_preflight.get("no_write_violations", [])},
            )
        )


def _extend_response_repair_items(
    repair_items: list[dict[str, Any]],
    response_preflight: dict[str, Any],
) -> None:
    if bool(response_preflight.get("can_route_to_external_activation_router", False)):
        return
    checks = [
        (
            "R8U102_FILL_MISSING_RESPONSE_ROWS",
            "missing_response_row_count",
            20,
            "response_rows",
            "Required hidden-state/evidence rows are missing.",
            "Add the missing response rows listed by hidden_state and required_evidence.",
            "missing_response_rows",
        ),
        (
            "R8U102_REMOVE_EXTRA_RESPONSE_ROWS",
            "extra_response_row_count",
            35,
            "response_rows",
            "The response contains extra hidden-state/evidence rows not required by the matrix.",
            "Remove or remap extra rows so the response aligns with the field activation matrix.",
            "extra_response_rows",
        ),
        (
            "R8U102_REPLACE_TEMPLATE_MARKERS",
            "template_marker_row_count",
            15,
            "field_provenance",
            "Response rows still contain TODO/template/sample markers.",
            "Replace every template marker with real field provenance, values, methods or alignment references.",
            "blocked_row_ids",
        ),
        (
            "R8U102_SET_DATA_ORIGIN_FIELD",
            "non_field_row_count",
            15,
            "field_provenance",
            "Some response rows are not marked with data_origin=field.",
            "Set data_origin=field only for rows backed by real field records; otherwise keep the response blocked.",
            "blocked_row_ids",
        ),
        (
            "R8U102_REPAIR_UNSUPPORTED_CHANNELS",
            "unsupported_channel_row_count",
            25,
            "channel_mapping",
            "Some rows use evidence channels not allowed for the hidden state.",
            "Select one of the hidden state's required channels before package assembly.",
            "blocked_row_ids",
        ),
        (
            "R8U102_FILL_ALIGNMENT_KEYS",
            "missing_alignment_row_count",
            15,
            "batch_alignment",
            "Rows are missing batch/evidence-value alignment or still use template alignment markers.",
            "Fill batch_id and evidence_value_reference with real, traceable field/lab/table references.",
            "blocked_row_ids",
        ),
        (
            "R8U102_FILL_VALUE_PAYLOAD",
            "missing_value_payload_row_count",
            12,
            "field_value_payload",
            "Rows are missing the actual machine-readable field value payload.",
            "Fill evidence_value with the actual measured value, label, event flag or JSON payload; keep evidence_value_reference for provenance.",
            "blocked_row_ids",
        ),
        (
            "R8U102_REPLACE_VALUE_PAYLOAD_TEMPLATE",
            "template_value_payload_row_count",
            12,
            "field_value_payload",
            "Rows still use template markers in the field value payload.",
            "Replace evidence_value template markers with actual operator-supplied field values before package assembly.",
            "blocked_row_ids",
        ),
        (
            "R8U102_CONFIRM_NO_WRITE_BOUNDARY",
            "no_write_unconfirmed_row_count",
            10,
            "protective_boundary",
            "Rows have not confirmed the no-write boundary.",
            "Set no_write_boundary_confirmed=true only after confirming the response cannot authorize actuator or release-gate writes.",
            "blocked_row_ids",
        ),
    ]
    for repair_id, count_key, priority, scope, issue, action, evidence_key in checks:
        count = _safe_int(response_preflight.get(count_key))
        if count <= 0:
            continue
        repair_items.append(
            _repair_item(
                repair_id,
                priority=priority,
                scope=scope,
                issue=issue,
                required_action=action,
                evidence={
                    "count": count,
                    evidence_key: response_preflight.get(evidence_key, []),
                },
            )
        )


def _extend_coherence_repair_items(
    repair_items: list[dict[str, Any]],
    response_coherence_audit: dict[str, Any],
) -> None:
    if bool(response_coherence_audit.get("can_route_to_package_assembly", False)):
        return
    if str(response_coherence_audit.get("audit_status", "")) == (
        "field_activation_response_coherence_audit_waiting_for_response_preflight"
    ):
        return
    blockers = _list_of_dicts(response_coherence_audit.get("blockers"))
    for blocker in blockers[:10]:
        repair_items.append(
            _repair_item(
                str(blocker.get("blocker_id", "R8U117_REPAIR_RESPONSE_COHERENCE")),
                priority=int(blocker.get("priority", 18) or 18),
                scope=str(blocker.get("scope", "response_coherence")),
                issue=str(blocker.get("issue", "Field activation response coherence is blocked.")),
                required_action=str(
                    blocker.get(
                        "required_action",
                        "Repair batch/node/sensor/custody/method alignment before package assembly.",
                    )
                ),
                evidence=dict(blocker.get("evidence", {})) if isinstance(blocker.get("evidence"), dict) else {},
            )
        )


def _extend_assembly_repair_items(
    repair_items: list[dict[str, Any]],
    assembly_plan: dict[str, Any],
) -> None:
    if bool(assembly_plan.get("can_stage_external_package_candidates", False)):
        return
    repair_items.append(
        _repair_item(
            "R8U102_COMPLETE_RESPONSE_PREFLIGHT_BEFORE_ASSEMBLY",
            priority=40,
            scope="package_assembly",
            issue="Package assembly is blocked because the response preflight is not ready.",
            required_action=(
                "Repair the response source/schema/evidence rows first; then regenerate the assembly plan and "
                "stage channel package candidates under the required package pointers."
            ),
            evidence={
                "assembly_status": assembly_plan.get("assembly_status", ""),
                "candidate_channel_plan_count": assembly_plan.get("candidate_channel_plan_count", 0),
                "candidate_table_plan_count": assembly_plan.get("candidate_table_plan_count", 0),
            },
        )
    )


def _response_repair_work_order_status(
    *,
    repair_items: list[dict[str, Any]],
    response_source_preflight: dict[str, Any],
    response_preflight: dict[str, Any],
    schema_preflight: dict[str, Any],
    package_assembly_plan: dict[str, Any],
    response_coherence_audit: dict[str, Any] | None = None,
) -> str:
    if not repair_items:
        return "field_activation_response_repair_work_order_ready_no_repairs_required"
    source_status = str(response_source_preflight.get("source_preflight_status", ""))
    if source_status == "field_activation_response_source_using_default_template":
        return "field_activation_response_repair_work_order_waiting_for_external_response"
    if not bool(response_source_preflight.get("can_run_response_preflight", False)):
        return "field_activation_response_repair_work_order_blocked_at_source_preflight"
    if str(schema_preflight.get("schema_preflight_status", "")) != "field_activation_schema_preflight_passed":
        return "field_activation_response_repair_work_order_blocked_at_schema_preflight"
    if not bool(response_preflight.get("can_route_to_external_activation_router", False)):
        return "field_activation_response_repair_work_order_blocked_at_response_preflight"
    if response_coherence_audit is not None and not bool(
        response_coherence_audit.get("can_route_to_package_assembly", False)
    ):
        return "field_activation_response_repair_work_order_blocked_at_response_coherence_audit"
    if not bool(package_assembly_plan.get("can_stage_external_package_candidates", False)):
        return "field_activation_response_repair_work_order_blocked_at_package_assembly"
    return "field_activation_response_repair_work_order_blocked_by_unknown_repair_items"


def _response_repair_next_operator_action(status: str) -> str:
    return {
        "field_activation_response_repair_work_order_ready_no_repairs_required": (
            "stage_no_write_external_package_candidates_then_run_downstream_package_preflights"
        ),
        "field_activation_response_repair_work_order_waiting_for_external_response": (
            "fill_response_template_and_set_FIELD_ACTIVATION_RESPONSE_PATH"
        ),
        "field_activation_response_repair_work_order_blocked_at_source_preflight": (
            "repair_FIELD_ACTIVATION_RESPONSE_PATH_file_or_json_shape"
        ),
        "field_activation_response_repair_work_order_blocked_at_schema_preflight": (
            "repair_response_or_assembly_schema_fields"
        ),
        "field_activation_response_repair_work_order_blocked_at_response_preflight": (
            "repair_field_provenance_alignment_channels_and_no_write_confirmations"
        ),
        "field_activation_response_repair_work_order_blocked_at_response_coherence_audit": (
            "repair_batch_node_sensor_custody_or_method_coherence_before_package_assembly"
        ),
        "field_activation_response_repair_work_order_blocked_at_package_assembly": (
            "regenerate_package_assembly_plan_after_response_preflight_ready"
        ),
    }.get(status, "inspect_repair_items_before_any_downstream_action")


def _repair_item(
    repair_id: str,
    *,
    priority: int,
    scope: str,
    issue: str,
    required_action: str,
    evidence: dict[str, Any],
) -> dict[str, Any]:
    return {
        "repair_id": repair_id,
        "priority": priority,
        "scope": scope,
        "issue": issue,
        "required_action": required_action,
        "evidence": evidence,
        "can_resume_model_chain_after_repair": False,
        "can_write_to_actuator_after_repair": False,
        "can_write_to_release_gate_after_repair": False,
    }


def _method_contract() -> dict[str, Any]:
    return {
        "technical_problem": (
            "当前系统知道需要真实 field package，但缺少按隐藏状态拆解的采集-回放-控制恢复接口。"
        ),
        "technical_means": (
            "把每个隐藏状态映射到外部证据通道、必需字段、可恢复 gate、证据边界和 no-write 边界。"
        ),
        "technical_effect": (
            "让现场采集从通道级提交变成状态级补证，减少 scan 摩擦，并防止把 proxy/template 误写成 field 结论。"
        ),
        "evidence_boundary": (
            "该接口只定义激活矩阵和补证路径；没有真实 field rows、holdout、replay 和人工复核时，"
            "不能生成 field-supported claim、actuator policy 或 release gate。"
        ),
    }


def _activation_row(
    state_row: dict[str, Any],
    *,
    route_rows: dict[str, dict[str, Any]],
    channels: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    state = str(state_row.get("hidden_state", "unknown_hidden_state"))
    spec = STATE_ACTIVATION_LIBRARY.get(state, {})
    required_channels = list(spec.get("required_channels", []))
    required_evidence = _dedupe(
        list(state_row.get("field_evidence_needed", []))
        + list(spec.get("required_field_evidence", []))
    )
    channel_status = [
        _channel_status(channel_id, route_rows=route_rows, channels=channels)
        for channel_id in required_channels
    ]
    field_validated = bool(state_row.get("field_validated", False))
    control_ready = bool(state_row.get("control_ready", False))
    route_ready = any(row["route_ready"] for row in channel_status)
    model_chain_ready = any(row["can_resume_model_chain"] for row in channel_status)
    return {
        "hidden_state": state,
        "coverage_stage": state_row.get("coverage_stage", "unknown"),
        "contract_covered": bool(state_row.get("contract_covered", False)),
        "sparse_estimation_ready": bool(state_row.get("sparse_estimation_ready", False)),
        "field_validated": field_validated,
        "control_ready": control_ready,
        "required_channels": required_channels,
        "required_field_evidence": required_evidence,
        "channel_status": channel_status,
        "resumes_to": list(spec.get("resumes_to", [])),
        "activation_status": _activation_status(
            field_validated=field_validated,
            control_ready=control_ready,
            route_ready=route_ready,
            model_chain_ready=model_chain_ready,
        ),
        "next_operator_focus": _next_operator_focus(state, required_channels, required_evidence),
        "technical_problem": spec.get("technical_problem", ""),
        "technical_means": spec.get("technical_means", ""),
        "technical_effect": spec.get("technical_effect", ""),
        "evidence_boundary": state_row.get(
            "evidence_boundary",
            f"{state} is not field validated; do not write field claims, actuator policy or release gate.",
        ),
        "no_write_boundary": (
            "This state row can prepare collection, replay and review candidates only; it cannot write "
            "actuator policy, release gate, patent/legal conclusion or field-supported claim."
        ),
    }


def _channel_status(
    channel_id: str,
    *,
    route_rows: dict[str, dict[str, Any]],
    channels: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    route = route_rows.get(channel_id, {})
    channel = channels.get(channel_id, {})
    return {
        "channel_id": channel_id,
        "package_pointer": channel.get("package_pointer", route.get("package_pointer", "")),
        "route_status": route.get("route_status", "activation_route_not_supplied"),
        "route_ready": bool(route.get("route_ready", False)),
        "can_resume_model_chain": bool(
            route.get("can_resume_model_chain", channel.get("can_resume_model_chain", False))
        ),
        "blocked_reason": route.get("blocked_reason", ""),
        "current_status": channel.get("current_status", ""),
        "resumes_to": channel.get("resumes_to", route.get("resumes_to", [])),
    }


def _activation_status(
    *,
    field_validated: bool,
    control_ready: bool,
    route_ready: bool,
    model_chain_ready: bool,
) -> str:
    if control_ready:
        return "state_control_ready_after_field_validation"
    if field_validated and model_chain_ready:
        return "state_field_validated_model_chain_resume_ready"
    if route_ready:
        return "state_has_ready_external_route_needs_replay_holdout_or_review"
    return "state_blocked_waiting_for_external_evidence"


def _next_operator_focus(
    state: str,
    required_channels: list[str],
    required_evidence: list[str],
) -> dict[str, Any]:
    return {
        "action_id": f"collect_field_activation_evidence_for_{state}",
        "submit_channels": required_channels,
        "first_required_evidence": required_evidence[:3],
        "operator_instruction": (
            "Collect real field rows for the listed evidence fields and keep batch_id/timestamp/node_id alignment; "
            "do not fill template markers or synthetic rows."
        ),
    }


def _readiness(
    rows: list[dict[str, Any]],
    external_conditions: dict[str, Any],
) -> dict[str, Any]:
    row_count = len(rows)
    activation_ready_rows = [
        row
        for row in rows
        if row["activation_status"] in {
            "state_control_ready_after_field_validation",
            "state_field_validated_model_chain_resume_ready",
        }
    ]
    evidence_boundary_complete = all(bool(row.get("evidence_boundary")) for row in rows)
    no_write_boundary_complete = all(bool(row.get("no_write_boundary")) for row in rows)
    required_channel_ids = sorted(
        {channel_id for row in rows for channel_id in row.get("required_channels", [])}
    )
    model_chain_ready_channel_ids = list(
        external_conditions.get("router_model_chain_ready_channel_ids", [])
    )
    return {
        "interface_status": (
            "field_activation_matrix_ready_for_state_level_external_collection"
            if row_count == len(EXPECTED_HIDDEN_STATES)
            and evidence_boundary_complete
            and no_write_boundary_complete
            else "field_activation_matrix_incomplete"
        ),
        "hidden_state_row_count": row_count,
        "expected_hidden_state_count": len(EXPECTED_HIDDEN_STATES),
        "hidden_state_row_coverage": round(row_count / len(EXPECTED_HIDDEN_STATES), 3),
        "activation_ready_state_count": len(activation_ready_rows),
        "field_validated_state_count": sum(1 for row in rows if row["field_validated"]),
        "control_ready_state_count": sum(1 for row in rows if row["control_ready"]),
        "required_channel_ids": required_channel_ids,
        "model_chain_ready_channel_ids": model_chain_ready_channel_ids,
        "can_resume_model_chain": bool(activation_ready_rows and model_chain_ready_channel_ids),
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
        "evidence_boundary_completeness": 1.0 if evidence_boundary_complete else 0.0,
        "no_write_boundary_completeness": 1.0 if no_write_boundary_complete else 0.0,
        "next_gate": "submit_external_evidence_packages_or_run_router_preflight",
    }


def _next_operator_actions(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [dict(row["next_operator_focus"]) for row in rows]


def _writeback_policy(readiness: dict[str, Any]) -> dict[str, Any]:
    return {
        "can_resume_model_chain": bool(readiness["can_resume_model_chain"]),
        "allowed_writeback": [
            "state_level_collection_plan",
            "external_package_preflight_candidate",
            "human_review_queue_candidate_after_field_replay",
        ],
        "blocked_writeback": [
            "actuator_policy",
            "release_gate",
            "patent_or_legal_conclusion",
            "field_supported_claim",
        ],
        "boundary": (
            "Even when a state-level route is ready, the matrix only routes evidence into replay/holdout/review. "
            "It never authorizes direct actuator, release-gate, legal or field-claim writes."
        ),
    }


def _state_rows(hidden_ledger: dict[str, Any]) -> list[dict[str, Any]]:
    rows = hidden_ledger.get("state_rows", [])
    if isinstance(rows, list) and rows:
        return [row for row in rows if isinstance(row, dict)]
    return [{"hidden_state": state, "field_validated": False, "control_ready": False} for state in EXPECTED_HIDDEN_STATES]


def _matrix_state_rows(matrix: dict[str, Any]) -> list[dict[str, Any]]:
    rows = matrix.get("state_activation_rows", [])
    return [row for row in rows if isinstance(row, dict)] if isinstance(rows, list) else []


def _expected_response_index(matrix: dict[str, Any]) -> set[tuple[str, str]]:
    return {
        (str(row.get("hidden_state", "")), str(evidence))
        for row in _matrix_state_rows(matrix)
        for evidence in row.get("required_field_evidence", [])
    }


def _expected_response_entries(matrix: dict[str, Any]) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    for state_row in _matrix_state_rows(matrix):
        hidden_state = str(state_row.get("hidden_state", "unknown_hidden_state"))
        for evidence in state_row.get("required_field_evidence", []):
            required_evidence = str(evidence)
            table_name, field_name = _split_evidence_field(required_evidence)
            entries.append(
                {
                    "hidden_state": hidden_state,
                    "required_evidence": required_evidence,
                    "table_name": table_name,
                    "field_name": field_name,
                }
            )
    return entries


def _response_completion_row(
    expected: dict[str, str],
    row: dict[str, Any] | None,
    matrix: dict[str, Any],
) -> dict[str, Any]:
    hidden_state = expected["hidden_state"]
    required_evidence = expected["required_evidence"]
    issue_scopes: list[str] = []
    missing_fields: list[str] = []
    response_row_id = f"{hidden_state}:{required_evidence}"
    evidence_channel = ""
    if row is None:
        issue_scopes.append("missing_response_row")
    else:
        response_row_id = str(row.get("response_row_id", response_row_id))
        evidence_channel = str(row.get("evidence_channel", ""))
        missing_fields = _missing_fields(row, list(RESPONSE_ROW_REQUIRED_FIELDS))
        if missing_fields:
            issue_scopes.append("missing_required_fields")
        if _row_has_template_marker(row):
            issue_scopes.append("template_marker")
        if str(row.get("data_origin", "")).strip().lower() != "field":
            issue_scopes.append("non_field_origin")
        if evidence_channel not in _allowed_channels_for_state(matrix, hidden_state):
            issue_scopes.append("unsupported_channel")
        if (
            not str(row.get("batch_id", "")).strip()
            or _has_template_marker(str(row.get("batch_id", "")))
            or not str(row.get("evidence_value_reference", "")).strip()
            or _has_template_marker(str(row.get("evidence_value_reference", "")))
        ):
            issue_scopes.append("missing_alignment")
        if _response_value_payload_missing(row):
            issue_scopes.append("missing_value_payload")
        elif _response_value_payload_has_template_marker(row):
            issue_scopes.append("template_value_payload")
        if not _truthy(row.get("no_write_boundary_confirmed")):
            issue_scopes.append("no_write_unconfirmed")
    issue_scopes = _dedupe(issue_scopes)
    complete = row is not None and not issue_scopes
    return {
        "response_row_id": response_row_id,
        "hidden_state": hidden_state,
        "required_evidence": required_evidence,
        "table_name": expected["table_name"],
        "field_name": expected["field_name"],
        "evidence_channel": evidence_channel,
        "row_supplied": row is not None,
        "completion_status": "row_complete" if complete else "row_incomplete",
        "issue_scopes": issue_scopes,
        "missing_required_fields": missing_fields,
        "next_operator_action": _response_completion_row_next_action(issue_scopes),
    }


def _response_completion_state_rows(row_ledgers: list[dict[str, Any]]) -> list[dict[str, Any]]:
    state_order = _dedupe([row["hidden_state"] for row in row_ledgers])
    state_rows: list[dict[str, Any]] = []
    for hidden_state in state_order:
        rows = [row for row in row_ledgers if row["hidden_state"] == hidden_state]
        completed = [row for row in rows if row["completion_status"] == "row_complete"]
        incomplete = [row for row in rows if row["completion_status"] != "row_complete"]
        supplied = [row for row in rows if row["row_supplied"]]
        issue_counts = _response_completion_issue_counts(rows)
        status = _response_completion_group_status(len(completed), len(rows))
        state_rows.append(
            {
                "hidden_state": hidden_state,
                "completion_status": status,
                "expected_row_count": len(rows),
                "provided_row_count": len(supplied),
                "completed_row_count": len(completed),
                "incomplete_row_count": len(incomplete),
                "completion_ratio": _ratio(len(completed), len(rows)),
                "table_names": sorted({str(row["table_name"]) for row in rows}),
                "top_issue_scopes": list(issue_counts.keys())[:6],
                "issue_scope_counts": issue_counts,
                "incomplete_response_row_ids": [
                    str(row["response_row_id"]) for row in incomplete[:12]
                ],
                "next_operator_action": _response_completion_group_next_action(status, issue_counts),
            }
        )
    return state_rows


def _response_completion_table_rows(row_ledgers: list[dict[str, Any]]) -> list[dict[str, Any]]:
    table_order = _dedupe([row["table_name"] for row in row_ledgers])
    table_rows: list[dict[str, Any]] = []
    for table_name in table_order:
        rows = [row for row in row_ledgers if row["table_name"] == table_name]
        completed = [row for row in rows if row["completion_status"] == "row_complete"]
        incomplete = [row for row in rows if row["completion_status"] != "row_complete"]
        table_rows.append(
            {
                "table_name": table_name,
                "completion_status": _response_completion_group_status(len(completed), len(rows)),
                "expected_row_count": len(rows),
                "completed_row_count": len(completed),
                "incomplete_row_count": len(incomplete),
                "completion_ratio": _ratio(len(completed), len(rows)),
                "hidden_states": sorted({str(row["hidden_state"]) for row in rows}),
                "top_issue_scopes": list(_response_completion_issue_counts(rows).keys())[:6],
            }
        )
    return table_rows


def _response_completion_issue_counts(row_ledgers: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in row_ledgers:
        for scope in row.get("issue_scopes", []):
            scope_text = str(scope)
            counts[scope_text] = counts.get(scope_text, 0) + 1
    return dict(sorted(counts.items(), key=lambda item: (-item[1], item[0])))


def _response_completion_group_status(completed_count: int, expected_count: int) -> str:
    if expected_count == 0:
        return "group_not_required"
    if completed_count == 0:
        return "group_not_started"
    if completed_count == expected_count:
        return "group_complete"
    return "group_partially_complete"


def _response_completion_next_hidden_state_focus(
    state_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    incomplete = [row for row in state_rows if row["completion_status"] != "group_complete"]
    if not incomplete:
        return {}
    for row in incomplete:
        if row["hidden_state"] == "catalyst_activity":
            return row
    return incomplete[0]


def _response_completion_ledger_status(
    *,
    completed_count: int,
    expected_count: int,
    response_source_preflight: dict[str, Any],
    response_preflight: dict[str, Any],
) -> str:
    source_status = str(response_source_preflight.get("source_preflight_status", ""))
    if source_status == "field_activation_response_source_using_default_template":
        return "field_activation_response_completion_waiting_for_external_response"
    if not bool(response_source_preflight.get("can_run_response_preflight", False)):
        return "field_activation_response_completion_blocked_at_source_preflight"
    if bool(response_preflight.get("can_route_to_external_activation_router", False)):
        return "field_activation_response_completion_ready_for_package_assembly"
    if completed_count == 0:
        return "field_activation_response_completion_no_rows_completed"
    if completed_count < expected_count:
        return "field_activation_response_completion_partially_completed"
    return "field_activation_response_completion_blocked_by_response_preflight"


def _response_completion_next_operator_action(status: str, next_focus: dict[str, Any]) -> str:
    if status == "field_activation_response_completion_waiting_for_external_response":
        return "copy_template_fill_real_field_values_and_set_FIELD_ACTIVATION_RESPONSE_PATH"
    if status == "field_activation_response_completion_blocked_at_source_preflight":
        return "repair_FIELD_ACTIVATION_RESPONSE_PATH_file_or_json_shape"
    if status == "field_activation_response_completion_ready_for_package_assembly":
        return "continue_to_no_write_package_assembly_staging_and_materialized_preflight"
    focus = str(next_focus.get("hidden_state", "field_activation_response"))
    focus_action = str(next_focus.get("next_operator_action", "repair_incomplete_response_rows"))
    return f"{focus}:{focus_action}"


def _field_activation_response_focus_handoff_next_action(
    handoff_status: str,
    next_focus: str,
    focused_repair_status: str = "",
    focused_repair_action: str = "",
) -> str:
    if handoff_status == "field_activation_response_focus_handoff_ready_for_catalyst_activity":
        if (
            focused_repair_action
            and focused_repair_status
            not in {
                "",
                "focused_catalyst_response_repair_work_order_not_available",
                "focused_catalyst_response_repair_work_order_waiting_for_external_response",
            }
        ):
            return focused_repair_action
        return (
            "fill_focused_catalyst_response_template_then_set_FOCUSED_CATALYST_RESPONSE_PATH_"
            "and_merge_to_FIELD_ACTIVATION_RESPONSE_PATH"
        )
    if handoff_status == "field_activation_response_focus_handoff_not_needed_response_complete":
        return "continue_to_no_write_package_assembly_staging_and_materialized_preflight"
    if handoff_status == "field_activation_response_focus_handoff_blocked_by_catalyst_kit":
        return "rerun_catalyst_response_submission_kit_before_focused_handoff"
    focus = next_focus or "field_activation_response"
    return f"continue_full_field_activation_response_rows_for_{focus}"


def _response_completion_row_next_action(issue_scopes: list[str]) -> str:
    if not issue_scopes:
        return "row_ready_continue"
    action_by_scope = {
        "missing_response_row": "add_missing_response_row",
        "missing_required_fields": "fill_required_response_row_fields",
        "template_marker": "replace_template_markers_with_real_field_values",
        "non_field_origin": "set_data_origin_field_only_for_real_records",
        "unsupported_channel": "select_allowed_evidence_channel_for_hidden_state",
        "missing_alignment": "fill_batch_id_and_evidence_value_reference",
        "missing_value_payload": "fill_machine_readable_evidence_value",
        "template_value_payload": "replace_evidence_value_template_payload",
        "no_write_unconfirmed": "confirm_no_write_boundary",
    }
    return action_by_scope.get(issue_scopes[0], "repair_response_row_completion_gap")


def _response_completion_group_next_action(status: str, issue_counts: dict[str, int]) -> str:
    if status == "group_complete":
        return "group_ready_continue"
    if not issue_counts:
        return "inspect_incomplete_group_rows"
    return _response_completion_row_next_action([next(iter(issue_counts))])


def _coherence_hidden_state_audit(
    hidden_state: str,
    rows: list[dict[str, Any]],
    *,
    blockers: list[dict[str, Any]],
    warnings: list[dict[str, Any]],
) -> dict[str, Any]:
    state_rows = [row for row in rows if str(row.get("hidden_state", "")) == hidden_state]
    batch_ids = _non_template_values(row.get("batch_id", "") for row in state_rows)
    chain_ids = _non_template_values(row.get("chain_of_custody_id", "") for row in state_rows)
    table_names = sorted({str(row.get("table_name", "")) for row in state_rows if row.get("table_name")})
    batch_alignment_status = _batch_alignment_status(batch_ids, len(state_rows))
    if batch_alignment_status == "hidden_state_batch_alignment_fragmented":
        blockers.append(
            _coherence_blocker(
                "R8U117_HIDDEN_STATE_BATCH_ALIGNMENT_FRAGMENTED",
                priority=12,
                scope="batch_alignment",
                issue=(
                    f"{hidden_state} evidence rows use fragmented batch_id values, so the state cannot be "
                    "assembled into one replayable evidence group."
                ),
                required_action=(
                    "Use a shared batch_id/campaign alignment key for evidence rows that support the same "
                    "hidden state, or split the response into separate coherent field packages."
                ),
                evidence={
                    "hidden_state": hidden_state,
                    "batch_ids": batch_ids[:10],
                    "response_row_ids": _row_ids(state_rows)[:10],
                },
            )
        )
    if len(chain_ids) > 1:
        warnings.append(
            _coherence_warning(
                "R8U117_CHAIN_OF_CUSTODY_FRAGMENTED",
                scope="custody_alignment",
                issue=(
                    f"{hidden_state} evidence rows use multiple chain_of_custody_id values; this may be valid, "
                    "but downstream reviewers need an explicit merge note."
                ),
                evidence={"hidden_state": hidden_state, "chain_of_custody_ids": chain_ids[:10]},
            )
        )
    return {
        "hidden_state": hidden_state,
        "response_row_count": len(state_rows),
        "table_count": len(table_names),
        "table_names": table_names,
        "distinct_batch_count": len(batch_ids),
        "batch_ids": batch_ids[:10],
        "distinct_chain_of_custody_count": len(chain_ids),
        "batch_alignment_status": batch_alignment_status,
        "can_assemble_state_evidence_group": batch_alignment_status
        in {
            "hidden_state_single_batch_alignment",
            "hidden_state_no_rows_yet",
        },
    }


def _coherence_row_scope_audit(
    row: dict[str, Any],
    *,
    blockers: list[dict[str, Any]],
    warnings: list[dict[str, Any]],
) -> dict[str, Any]:
    table_name = str(row.get("table_name", ""))
    response_row_id = str(row.get("response_row_id", "unknown_response_row"))
    missing: list[str] = []
    if _table_requires_time_node_sensor(table_name):
        for field in ("timestamp", "node_id", "sensor_id"):
            if _missing_or_template(row.get(field, "")):
                missing.append(field)
    if table_name == "offline_lab_results":
        for field in ("offline_method_id", "detection_limit"):
            if _missing_or_template(row.get(field, "")):
                missing.append(field)
    if missing:
        blockers.append(
            _coherence_blocker(
                "R8U117_RESPONSE_ROW_SCOPE_FIELDS_MISSING",
                priority=14,
                scope="row_scope_alignment",
                issue=(
                    f"{response_row_id} lacks fields required to assemble its table-level evidence scope."
                ),
                required_action=(
                    "Fill timestamp/node_id/sensor_id for sensor or operation rows, and offline_method_id/"
                    "detection_limit for offline_lab_results rows before package assembly."
                ),
                evidence={"response_row_id": response_row_id, "table_name": table_name, "missing_fields": missing},
            )
        )
    expected_node = _expected_node_from_required_evidence(row)
    supplied_node = str(row.get("node_id", "")).strip()
    node_alignment_status = "node_not_applicable"
    if expected_node:
        node_alignment_status = (
            "node_matches_required_evidence"
            if supplied_node == expected_node
            else "node_needs_review_against_required_evidence"
        )
        if supplied_node and supplied_node != expected_node:
            warnings.append(
                _coherence_warning(
                    "R8U117_NODE_ID_DIFFERS_FROM_REQUIRED_EVIDENCE",
                    scope="node_alignment_review",
                    issue=(
                        f"{response_row_id} node_id differs from the node embedded in required_evidence."
                    ),
                    evidence={
                        "response_row_id": response_row_id,
                        "required_evidence_node": expected_node,
                        "supplied_node_id": supplied_node,
                    },
                )
            )
    return {
        "response_row_id": response_row_id,
        "hidden_state": str(row.get("hidden_state", "")),
        "table_name": table_name,
        "required_evidence": str(row.get("required_evidence", "")),
        "missing_scope_fields": missing,
        "node_alignment_status": node_alignment_status,
        "can_assemble_row_scope": not missing,
    }


def _coherence_blocker(
    blocker_id: str,
    *,
    priority: int,
    scope: str,
    issue: str,
    required_action: str,
    evidence: dict[str, Any],
) -> dict[str, Any]:
    return {
        "blocker_id": blocker_id,
        "priority": priority,
        "scope": scope,
        "issue": issue,
        "required_action": required_action,
        "evidence": evidence,
    }


def _coherence_warning(
    warning_id: str,
    *,
    scope: str,
    issue: str,
    evidence: dict[str, Any],
) -> dict[str, Any]:
    return {
        "warning_id": warning_id,
        "scope": scope,
        "issue": issue,
        "evidence": evidence,
    }


def _coherence_next_operator_action(status: str, blockers: list[dict[str, Any]]) -> str:
    if status == "field_activation_response_coherence_audit_waiting_for_response_preflight":
        return "complete_response_preflight_before_coherence_audit"
    if not blockers:
        return "continue_to_no_write_package_assembly_and_staging"
    blocker = str(blockers[0].get("blocker_id", "R8U117_REPAIR_RESPONSE_COHERENCE"))
    return {
        "R8U117_HIDDEN_STATE_BATCH_ALIGNMENT_FRAGMENTED": (
            "repair_hidden_state_batch_alignment_before_package_assembly"
        ),
        "R8U117_RESPONSE_ROW_SCOPE_FIELDS_MISSING": (
            "fill_missing_timestamp_node_sensor_or_lab_method_fields"
        ),
    }.get(blocker, "repair_field_activation_response_coherence_before_package_assembly")


def _batch_alignment_status(batch_ids: list[str], row_count: int) -> str:
    if row_count <= 0:
        return "hidden_state_no_rows_yet"
    if not batch_ids:
        return "hidden_state_batch_alignment_missing"
    if len(batch_ids) == 1:
        return "hidden_state_single_batch_alignment"
    return "hidden_state_batch_alignment_fragmented"


def _table_requires_time_node_sensor(table_name: str) -> bool:
    return table_name not in {"offline_lab_results", "context_or_manual_review"}


def _expected_node_from_required_evidence(row: dict[str, Any]) -> str:
    field_name = str(row.get("field_name", ""))
    if ":" not in field_name:
        return ""
    return field_name.split(":", 1)[0].strip()


def _missing_or_template(value: Any) -> bool:
    text = str(value).strip()
    return not text or _has_template_marker(text)


def _non_template_values(values: Any) -> list[str]:
    return sorted({str(value).strip() for value in values if not _missing_or_template(value)})


def _row_ids(rows: list[dict[str, Any]]) -> list[str]:
    return [str(row.get("response_row_id", "unknown_response_row")) for row in rows]


def _allowed_channels_for_state(matrix: dict[str, Any], hidden_state: str) -> set[str]:
    for row in _matrix_state_rows(matrix):
        if str(row.get("hidden_state", "")) == hidden_state:
            return {str(channel) for channel in row.get("required_channels", [])}
    return set()


def _split_evidence_field(evidence_field: str) -> tuple[str, str]:
    if "." not in evidence_field:
        return "context_or_manual_review", evidence_field
    table_name, field_name = evidence_field.split(".", 1)
    return table_name, field_name


def _contract_channel_map(contract: dict[str, Any]) -> dict[str, dict[str, Any]]:
    channels = contract.get("channels", [])
    if not isinstance(channels, list):
        return {}
    return {
        str(channel.get("channel_id", "unknown_channel")): channel
        for channel in channels
        if isinstance(channel, dict)
    }


def _assembly_channel_plan(
    channel_id: str,
    table_groups: dict[str, list[dict[str, Any]]],
    *,
    contract_channels: dict[str, dict[str, Any]],
    response_preflight: dict[str, Any],
    response_ready: bool | None = None,
) -> dict[str, Any]:
    contract = contract_channels.get(channel_id, {})
    ready = (
        bool(response_preflight.get("can_route_to_external_activation_router", False))
        if response_ready is None
        else bool(response_ready)
    )
    return {
        "channel_id": channel_id,
        "package_pointer": contract.get("package_pointer", _default_package_pointer(channel_id)),
        "assembly_status": (
            "channel_package_assembly_ready_for_no_write_staging"
            if ready
            else "channel_package_assembly_blocked_by_response_preflight"
        ),
        "required_contract_evidence": contract.get("required_evidence", []),
        "reject_if": contract.get("reject_if", []),
        "resumes_to": contract.get("resumes_to", []),
        "table_assemblies": [
            _table_assembly(table_name, rows)
            for table_name, rows in sorted(table_groups.items())
        ],
        "can_resume_model_chain": False,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
        "next_operator_action": (
            f"stage_{channel_id}_package_candidate_then_run_external_activation_router"
            if ready
            else "complete_field_activation_response_preflight_before_package_staging"
        ),
    }


def _candidate_channel_plans_from_matrix(
    matrix: dict[str, Any],
    *,
    contract_channels: dict[str, dict[str, Any]],
    response_preflight: dict[str, Any],
    response_ready: bool | None = None,
) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, list[dict[str, Any]]]] = {}
    for state_row in _matrix_state_rows(matrix):
        hidden_state = str(state_row.get("hidden_state", "unknown_hidden_state"))
        for channel_id in state_row.get("required_channels", []):
            channel = str(channel_id)
            for index, evidence_field in enumerate(state_row.get("required_field_evidence", []), start=1):
                table_name, field_name = _split_evidence_field(str(evidence_field))
                grouped.setdefault(channel, {}).setdefault(table_name, []).append(
                    {
                        "response_row_id": f"candidate_{hidden_state}_{index:02d}",
                        "hidden_state": hidden_state,
                        "table_name": table_name,
                        "field_name": field_name,
                    }
                )
    return [
        {
            **_assembly_channel_plan(
                channel_id,
                table_groups,
                contract_channels=contract_channels,
                response_preflight=response_preflight,
                response_ready=response_ready,
            ),
            "plan_basis": "matrix_required_channels_not_filled_response_choice",
        }
        for channel_id, table_groups in sorted(grouped.items())
    ]


def _package_assembly_blocked_status(
    response_preflight: dict[str, Any],
    response_coherence_audit: dict[str, Any],
) -> str:
    if not bool(response_preflight.get("can_route_to_external_activation_router", False)):
        return "field_activation_package_assembly_plan_blocked_by_response_preflight"
    if response_coherence_audit and not bool(
        response_coherence_audit.get("can_route_to_package_assembly", False)
    ):
        return "field_activation_package_assembly_plan_blocked_by_response_coherence_audit"
    return "field_activation_package_assembly_plan_blocked_by_response_preflight"


def _table_assembly(table_name: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    field_names = sorted({str(row.get("field_name", "")) for row in rows if row.get("field_name")})
    hidden_states = sorted({str(row.get("hidden_state", "")) for row in rows if row.get("hidden_state")})
    response_row_ids = [str(row.get("response_row_id", "unknown_response_row")) for row in rows]
    return {
        "table_name": table_name,
        "field_names": field_names,
        "hidden_states": hidden_states,
        "response_row_ids": response_row_ids,
        "source_response_rows": _table_assembly_source_rows(rows),
        "source_response_row_count": len(rows),
        "required_output_columns": _required_output_columns(table_name, field_names),
        "row_alignment_keys": [
            "batch_id",
            "timestamp",
            "node_id",
            "sensor_id",
            "chain_of_custody_id",
        ],
    }


def _required_output_columns(table_name: str, field_names: list[str]) -> list[str]:
    base = ["batch_id", "data_origin", "chain_of_custody_id", "operator_id"]
    if table_name not in {"offline_lab_results", "context_or_manual_review"}:
        base.extend(["timestamp", "node_id", "sensor_id"])
    if table_name == "offline_lab_results":
        base.extend(["offline_method_id", "detection_limit"])
    return _dedupe(base + field_names)


def _table_assembly_source_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    preserved_fields = (
        "response_row_id",
        "hidden_state",
        "required_evidence",
        "table_name",
        "field_name",
        "data_origin",
        "batch_id",
        "timestamp",
        "node_id",
        "sensor_id",
        "offline_method_id",
        "detection_limit",
        "evidence_value_reference",
        "evidence_value",
        "chain_of_custody_id",
        "operator_id",
    )
    return [
        {field: row.get(field, "") for field in preserved_fields if field in row}
        for row in rows
    ]


def _default_package_pointer(channel_id: str) -> str:
    return {
        "R7_REAL_FIELD_PACKAGE": "REAL_FIELD_REPLAY_PACKAGE_DIR",
        "R8U66_PATH_ENDPOINT_LABEL_PACKAGE": "FIELD_PATH_ENDPOINT_LABEL_PACKAGE_DIR",
        "R8U79_FORMAL_SEARCH_RESULT_PACKAGE": "FORMAL_SEARCH_RESULT_PACKAGE_PATH",
    }.get(channel_id, "UNKNOWN_EXTERNAL_PACKAGE_POINTER")


def _assembly_operator_sequence(response_ready: bool) -> list[str]:
    if not response_ready:
        return [
            "Fill field_activation_response_template.json with real field values.",
            "Run field_activation_response_preflight until it is ready.",
            "Only then assemble channel package candidates and run external activation router preflight.",
        ]
    return [
        "Group filled response rows by evidence_channel and table_name.",
        "Stage channel package candidates under the required package pointers.",
        "Run .venv/bin/python experiments/run_external_activation_router.py.",
        "Do not write actuator policy or release gate until downstream replay/holdout/human-review gates pass.",
    ]


def _package_staging_status(
    *,
    response_ready: bool,
    assembly_ready: bool,
    selected_channel_count: int,
) -> str:
    if not response_ready:
        return "field_activation_package_staging_manifest_blocked_by_response_preflight"
    if not assembly_ready:
        return "field_activation_package_staging_manifest_blocked_by_assembly_plan"
    if selected_channel_count <= 0:
        return "field_activation_package_staging_manifest_blocked_no_selected_channel_plan"
    return "field_activation_package_staging_manifest_ready_for_operator_package_materialization"


def _package_staging_next_operator_action(
    can_materialize: bool,
    selected_channel_manifests: list[dict[str, Any]],
) -> str:
    if not can_materialize:
        return "complete_response_preflight_and_package_assembly_before_staging"
    pointers = [
        str(channel.get("package_pointer", ""))
        for channel in selected_channel_manifests
        if channel.get("package_pointer")
    ]
    if not pointers:
        return "materialize_selected_channel_package_then_run_external_activation_router"
    return f"materialize_selected_channel_package_then_set_{pointers[0]}"


def _staging_channel_manifest(
    channel_plan: dict[str, Any],
    *,
    can_materialize: bool,
    plan_basis: str,
) -> dict[str, Any]:
    channel_id = str(channel_plan.get("channel_id", "unknown_channel"))
    package_pointer = str(channel_plan.get("package_pointer", _default_package_pointer(channel_id)))
    table_manifests = [
        _staging_table_manifest(table, can_materialize=can_materialize)
        for table in _list_of_dicts(channel_plan.get("table_assemblies"))
    ]
    return {
        "channel_id": channel_id,
        "package_pointer": package_pointer,
        "plan_basis": plan_basis,
        "package_directory_placeholder": f"TODO_CREATE_NO_WRITE_PACKAGE_DIR_FOR_{channel_id}",
        "can_materialize_from_selected_response": can_materialize,
        "source_response_row_count": sum(
            int(table.get("source_response_row_count", 0) or 0) for table in table_manifests
        ),
        "table_manifest_count": len(table_manifests),
        "table_manifests": table_manifests,
        "validation_command_preview": (
            f"{package_pointer}=<package_dir> .venv/bin/python experiments/run_external_activation_router.py"
            if package_pointer
            else ".venv/bin/python experiments/run_external_activation_router.py"
        ),
        "operator_action": (
            f"create_no_write_package_directory_for_{channel_id}_then_set_{package_pointer}"
            if can_materialize
            else f"use_{channel_id}_as_requirement_reference_until_rows_are_selected_for_this_channel"
        ),
        "can_resume_model_chain": False,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
    }


def _staging_table_manifest(table_assembly: dict[str, Any], *, can_materialize: bool) -> dict[str, Any]:
    table_name = str(table_assembly.get("table_name", "unknown_table"))
    required_columns = _string_list(table_assembly.get("required_output_columns"), default=())
    field_names = _string_list(table_assembly.get("field_names"), default=())
    source_rows = _list_of_dicts(table_assembly.get("source_response_rows"))
    value_payload_mappings = (
        _staging_value_payload_mappings(source_rows)
        if can_materialize
        else []
    )
    row_blueprints = (
        _staging_table_row_blueprints(
            table_name=table_name,
            source_rows=source_rows,
            required_columns=required_columns,
            field_names=field_names,
        )
        if can_materialize
        else []
    )
    return {
        "table_name": table_name,
        "output_file": f"{table_name}.csv",
        "required_columns": required_columns,
        "row_alignment_keys": _string_list(table_assembly.get("row_alignment_keys"), default=()),
        "field_names": field_names,
        "hidden_states": _string_list(table_assembly.get("hidden_states"), default=()),
        "source_response_row_ids": _string_list(table_assembly.get("response_row_ids"), default=()),
        "source_response_row_count": int(table_assembly.get("source_response_row_count", 0) or 0),
        "value_payload_mapping_status": (
            "value_payload_rows_ready_for_operator_materialization"
            if can_materialize
            else "value_payload_mapping_deferred_until_response_ready"
        ),
        "value_payload_mapping_count": len(value_payload_mappings),
        "value_payload_mappings": value_payload_mappings,
        "row_blueprint_count": len(row_blueprints),
        "row_blueprints": row_blueprints,
        "no_write_boundary": (
            "These row blueprints only map operator-supplied response values into package CSV columns for "
            "preflight. They do not create or prove field evidence and cannot write actuator policy or release gate."
        ),
    }


def _staging_value_payload_mappings(source_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "response_row_id": str(row.get("response_row_id", "unknown_response_row")),
            "hidden_state": str(row.get("hidden_state", "unknown_hidden_state")),
            "required_evidence": str(row.get("required_evidence", "")),
            "target_table": str(row.get("table_name", "unknown_table")),
            "target_column": str(row.get("field_name", "unknown_field")),
            "evidence_value": row.get("evidence_value", ""),
            "evidence_value_reference": str(row.get("evidence_value_reference", "")),
            "batch_id": str(row.get("batch_id", "")),
        }
        for row in source_rows
    ]


def _staging_table_row_blueprints(
    *,
    table_name: str,
    source_rows: list[dict[str, Any]],
    required_columns: list[str],
    field_names: list[str],
) -> list[dict[str, Any]]:
    field_name_set = set(field_names)
    identity_columns = [column for column in required_columns if column not in field_name_set]
    grouped: dict[tuple[str, ...], dict[str, Any]] = {}
    for row in source_rows:
        key = tuple(str(row.get(column, "")) for column in identity_columns)
        if key not in grouped:
            output_row = {column: str(row.get(column, "")) for column in identity_columns}
            output_row.update({field_name: "" for field_name in field_names})
            grouped[key] = {
                "table_name": table_name,
                "output_row": output_row,
                "source_response_row_ids": [],
                "value_payload_columns": [],
            }
        field_name = str(row.get("field_name", ""))
        if field_name:
            grouped[key]["output_row"][field_name] = _payload_to_csv_cell(row.get("evidence_value", ""))
            grouped[key]["value_payload_columns"].append(field_name)
        grouped[key]["source_response_row_ids"].append(
            str(row.get("response_row_id", "unknown_response_row"))
        )
    return [
        {
            "row_blueprint_id": f"{table_name}_blueprint_{index:03d}",
            "table_name": table_name,
            "output_row": blueprint["output_row"],
            "source_response_row_ids": blueprint["source_response_row_ids"],
            "value_payload_columns": sorted(set(blueprint["value_payload_columns"])),
            "no_write_boundary": (
                "Blueprint row only maps supplied response payloads to CSV cells for downstream preflight; "
                "it is not field evidence."
            ),
        }
        for index, blueprint in enumerate(grouped.values(), start=1)
    ]


def _payload_to_csv_cell(value: object) -> str:
    if isinstance(value, (dict, list, tuple, set)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    return str(value)


def _materialized_package_preflight_result(
    *,
    package_pointer: str,
    package_dir_path: str,
    status: str,
    selected_channels: list[dict[str, Any]],
    blockers: list[dict[str, Any]],
    next_operator_action: str,
    metadata_audit: dict[str, Any] | None = None,
    table_audits: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    table_audits = table_audits or []
    metadata_audit = metadata_audit or {}
    ready = status == "field_activation_materialized_package_preflight_ready_for_external_activation_router"
    return {
        "preflight_id": "R8u105_field_activation_materialized_package_preflight",
        "package_pointer": package_pointer,
        "package_dir_path": package_dir_path,
        "preflight_status": status,
        "selected_channel_ids": [str(channel.get("channel_id", "unknown_channel")) for channel in selected_channels],
        "selected_channel_count": len(selected_channels),
        "expected_table_count": sum(
            len(_list_of_dicts(channel.get("table_manifests"))) for channel in selected_channels
        ),
        "checked_table_count": len(table_audits),
        "present_table_count": sum(1 for audit in table_audits if audit.get("file_exists")),
        "missing_table_count": sum(1 for audit in table_audits if not audit.get("file_exists")),
        "header_gap_count": sum(int(audit.get("missing_column_count", 0) or 0) for audit in table_audits),
        "empty_table_count": sum(1 for audit in table_audits if audit.get("file_exists") and int(audit.get("row_count", 0) or 0) == 0),
        "template_marker_row_count": sum(int(audit.get("template_marker_row_count", 0) or 0) for audit in table_audits),
        "non_field_row_count": sum(int(audit.get("non_field_row_count", 0) or 0) for audit in table_audits),
        "blueprint_expected_row_count": sum(
            int(audit.get("blueprint_expected_row_count", 0) or 0) for audit in table_audits
        ),
        "blueprint_matched_row_count": sum(
            int(audit.get("blueprint_matched_row_count", 0) or 0) for audit in table_audits
        ),
        "blueprint_missing_row_count": sum(
            int(audit.get("blueprint_missing_row_count", 0) or 0) for audit in table_audits
        ),
        "metadata_blocker_count": int(metadata_audit.get("metadata_blocker_count", 0) or 0),
        "blocker_count": len(blockers),
        "highest_priority_blocker": str(blockers[0]["blocker_id"]) if blockers else "",
        "blockers": blockers[:50],
        "metadata_audit": metadata_audit,
        "table_audits": table_audits,
        "can_route_to_external_activation_router": ready,
        "can_resume_model_chain": False,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
        "router_validation_command": (
            f"{package_pointer}={package_dir_path} .venv/bin/python experiments/run_external_activation_router.py"
            if ready
            else ".venv/bin/python experiments/run_external_activation_router.py"
        ),
        "next_operator_action": next_operator_action,
        "no_write_boundary": (
            "This preflight only checks whether an operator-materialized package directory matches the field "
            "activation staging manifest. It does not run replay/holdout, does not create field evidence, and "
            "cannot write actuator policy, release gate, legal conclusions or field-supported claims."
        ),
    }


def _downstream_r7_preview_result(
    *,
    package_pointer: str,
    package_dir_path: str,
    selected_channel_ids: list[str],
    status: str,
    preview_executed: bool,
    r7_preflight: dict[str, Any],
    highest_priority_blocker: str,
    next_operator_action: str,
    upstream_materialized_package_status: str,
) -> dict[str, Any]:
    r7_ready = bool(r7_preflight.get("can_pass_to_timestamped_replay", False))
    r7_next_actions = r7_preflight.get("next_actions", [])
    metric_evaluation_status = _downstream_preview_metric_evaluation_status(
        status=status,
        preview_executed=preview_executed,
        executed_status="r7_preflight_metrics_evaluated",
    )
    return {
        "preview_id": "R8u121_field_activation_downstream_r7_preflight_preview",
        "preview_type": "no_write_r7_agent44_import_gate_preview",
        "preview_status": status,
        "upstream_materialized_package_status": upstream_materialized_package_status,
        "package_pointer": package_pointer,
        "package_dir_path": package_dir_path,
        "selected_channel_ids": selected_channel_ids,
        "preview_executed": preview_executed,
        "preview_metric_evaluation_status": metric_evaluation_status,
        "not_evaluated_metric_names": [] if preview_executed else [
            "r7_preflight_status",
            "r7_agent44_import_status",
            "r7_files_ready",
            "r7_real_rows_ready",
            "r7_placeholder_metadata_field_count",
            "r7_agent44_type_error_count",
            "r7_agent44_blocking_table_count",
            "r7_agent44_required_field_blocker_table_count",
            "r7_agent44_linkage_blocker_count",
            "downstream_r7_can_pass_to_timestamped_replay",
        ],
        "r7_preflight_status": str(r7_preflight.get("status", "r7_preflight_not_run")),
        "r7_agent44_import_status": str(
            r7_preflight.get("agent44_import_status", "agent44_import_not_run")
        ),
        "r7_agent44_import_score": r7_preflight.get("agent44_import_score", 0),
        "r7_files_ready": bool(r7_preflight.get("files_ready", False)),
        "r7_real_rows_ready": bool(r7_preflight.get("real_rows_ready", False)),
        "r7_placeholder_metadata_field_count": len(
            _string_list(r7_preflight.get("placeholder_metadata_fields"), default=())
        ),
        "r7_agent44_type_error_count": int(r7_preflight.get("agent44_type_error_count", 0) or 0),
        "r7_agent44_blocking_table_count": len(_dict(r7_preflight.get("agent44_blocking_table_statuses"))),
        "r7_agent44_required_field_blocker_table_count": len(
            _dict(r7_preflight.get("agent44_required_field_blockers"))
        ),
        "r7_agent44_linkage_blocker_count": len(_dict(r7_preflight.get("agent44_linkage_blockers"))),
        "downstream_r7_can_pass_to_timestamped_replay": r7_ready,
        "downstream_r7_would_resume_model_chain_in_router": r7_ready,
        "highest_priority_blocker": highest_priority_blocker,
        "next_operator_action": next_operator_action,
        "r7_next_actions": r7_next_actions if isinstance(r7_next_actions, list) else [],
        "r7_preflight": r7_preflight,
        "can_submit_to_external_activation_router": status not in {
            "field_activation_downstream_r7_preview_blocked_by_materialized_package_preflight",
            "field_activation_downstream_r7_preview_waiting_for_package_dir",
            "field_activation_downstream_r7_preview_not_applicable_non_r7_channel",
        },
        "can_resume_model_chain": False,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
        "no_write_boundary": (
            "This preview runs the downstream R7/Agent44 field replay package preflight as a read-only check. "
            "Even if R7 would pass, this artifact cannot resume the model chain, run replay/holdout, write actuator "
            "policy, write a release gate or label any conclusion field-supported."
        ),
    }


def _downstream_r7_highest_blocker(r7_preflight: dict[str, Any]) -> str:
    status = str(r7_preflight.get("status", ""))
    if status == "field_package_preflight_missing_files_or_headers":
        return "R8U121_R7_MISSING_FILES_OR_HEADERS"
    if r7_preflight.get("placeholder_metadata_fields"):
        return "R8U121_R7_PLACEHOLDER_METADATA"
    if not bool(r7_preflight.get("real_rows_ready", False)):
        return "R8U121_R7_MISSING_REAL_ROWS"
    if _dict(r7_preflight.get("agent44_required_field_blockers")):
        return "R8U121_R7_AGENT44_REQUIRED_FIELDS_BLOCKED"
    if int(r7_preflight.get("agent44_type_error_count", 0) or 0) > 0:
        return "R8U121_R7_AGENT44_TYPE_COERCION_BLOCKED"
    if _dict(r7_preflight.get("agent44_linkage_blockers")):
        return "R8U121_R7_AGENT44_BATCH_LINKAGE_BLOCKED"
    if str(r7_preflight.get("agent44_import_status", "")) != (
        "field_replay_import_ready_for_timestamped_replay"
    ):
        return "R8U121_R7_AGENT44_IMPORT_BLOCKED"
    return "R8U121_R7_PREFLIGHT_NOT_READY"


def _downstream_preview_metric_evaluation_status(
    *,
    status: str,
    preview_executed: bool,
    executed_status: str,
) -> str:
    if preview_executed:
        return executed_status
    if "blocked_by_materialized_package_preflight" in status:
        return "deferred_until_materialized_package_preflight_ready"
    if "waiting_for_package_dir" in status:
        return "deferred_until_package_dir_supplied"
    if "not_applicable" in status:
        return "not_applicable_for_selected_channel_scope"
    return "downstream_preview_metrics_not_evaluated"


def _downstream_r7_next_operator_action(r7_preflight: dict[str, Any]) -> str:
    next_actions = r7_preflight.get("next_actions", [])
    if isinstance(next_actions, list) and next_actions:
        return str(next_actions[0])
    return "repair_r7_field_package_until_agent44_preflight_passes"


def _downstream_path_endpoint_preview_result(
    *,
    package_pointer: str,
    package_dir_path: str,
    selected_channel_ids: list[str],
    status: str,
    preview_executed: bool,
    path_endpoint_preflight: dict[str, Any],
    highest_priority_blocker: str,
    next_operator_action: str,
    upstream_materialized_package_status: str,
) -> dict[str, Any]:
    ready = bool(path_endpoint_preflight.get("can_route_to_field_layout_holdout", False))
    alignment_patch_plan = _dict(path_endpoint_preflight.get("alignment_patch_plan"))
    path_contract = build_field_path_endpoint_label_package_contract()
    required_tables = _string_list(path_contract.get("required_tables"), default=())
    metric_evaluation_status = _downstream_preview_metric_evaluation_status(
        status=status,
        preview_executed=preview_executed,
        executed_status="path_endpoint_preflight_metrics_evaluated",
    )
    return {
        "preview_id": "R8u122_field_activation_downstream_path_endpoint_preflight_preview",
        "preview_type": "no_write_r8u66_agent54_path_endpoint_label_gate_preview",
        "preview_status": status,
        "upstream_materialized_package_status": upstream_materialized_package_status,
        "package_pointer": package_pointer,
        "package_dir_path": package_dir_path,
        "selected_channel_ids": selected_channel_ids,
        "preview_executed": preview_executed,
        "preview_metric_evaluation_status": metric_evaluation_status,
        "not_evaluated_metric_names": [] if preview_executed else [
            "path_endpoint_preflight_status",
            "path_endpoint_matched_batch_count",
            "path_endpoint_required_matched_batch_deficit",
            "path_endpoint_batch_alignment_gap_count",
            "path_endpoint_template_marker_count",
            "path_endpoint_required_field_gap_count",
            "path_endpoint_missing_table_count",
            "path_endpoint_empty_table_count",
            "path_endpoint_alignment_patch_plan_status",
            "path_endpoint_alignment_patch_plan_item_count",
            "downstream_path_endpoint_can_route_to_field_layout_holdout",
        ],
        "path_endpoint_required_table_count": len(required_tables),
        "path_endpoint_required_tables": required_tables,
        "path_endpoint_contract_minimum_matched_batch_count": int(
            path_contract.get("minimum_matched_batch_count", 5) or 5
        ),
        "path_endpoint_preflight_status": str(
            path_endpoint_preflight.get("preflight_status", "path_endpoint_preflight_not_run")
        ),
        "path_endpoint_matched_batch_count": int(
            path_endpoint_preflight.get("matched_batch_count", 0) or 0
        ),
        "path_endpoint_minimum_matched_batch_count": int(
            path_endpoint_preflight.get("minimum_matched_batch_count", 0) or 0
        ),
        "path_endpoint_required_matched_batch_deficit": int(
            path_endpoint_preflight.get("required_matched_batch_deficit", 0) or 0
        ),
        "path_endpoint_batch_alignment_gap_count": int(
            path_endpoint_preflight.get("batch_alignment_gap_count", 0) or 0
        ),
        "path_endpoint_template_marker_count": int(
            path_endpoint_preflight.get("template_marker_count", 0) or 0
        ),
        "path_endpoint_required_field_gap_count": int(
            path_endpoint_preflight.get("required_field_gap_count", 0) or 0
        ),
        "path_endpoint_missing_table_count": len(_string_list(path_endpoint_preflight.get("missing_tables"), default=())),
        "path_endpoint_empty_table_count": len(_string_list(path_endpoint_preflight.get("empty_tables"), default=())),
        "path_endpoint_alignment_patch_plan_status": str(
            alignment_patch_plan.get("patch_plan_status", "path_endpoint_alignment_patch_plan_not_run")
        ),
        "path_endpoint_alignment_patch_plan_item_count": len(
            _list_of_dicts(alignment_patch_plan.get("patch_items"))
        ),
        "downstream_path_endpoint_can_route_to_field_layout_holdout": ready,
        "downstream_path_endpoint_would_resume_model_chain_in_router": ready,
        "highest_priority_blocker": highest_priority_blocker,
        "next_operator_action": next_operator_action,
        "path_endpoint_preflight": path_endpoint_preflight,
        "can_submit_to_external_activation_router": status not in {
            "field_activation_downstream_path_endpoint_preview_blocked_by_materialized_package_preflight",
            "field_activation_downstream_path_endpoint_preview_waiting_for_package_dir",
            "field_activation_downstream_path_endpoint_preview_not_applicable_no_path_scope",
        },
        "can_resume_model_chain": False,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
        "no_write_boundary": (
            "This preview runs the downstream R8u66/Agent54 path-endpoint label preflight as a read-only check. "
            "Even if path labels would route to layout holdout, this artifact cannot resume the model chain, "
            "run holdout/replay, write actuator policy, write a release gate or label any conclusion "
            "field-supported."
        ),
    }


def _downstream_path_endpoint_highest_blocker(preflight: dict[str, Any]) -> str:
    if _string_list(preflight.get("missing_tables"), default=()):
        return "R8U122_PATH_ENDPOINT_MISSING_TABLES"
    if _string_list(preflight.get("empty_tables"), default=()):
        return "R8U122_PATH_ENDPOINT_EMPTY_TABLES"
    if _string_list(preflight.get("invalid_table_shapes"), default=()):
        return "R8U122_PATH_ENDPOINT_INVALID_TABLE_SHAPES"
    if int(preflight.get("template_marker_count", 0) or 0) > 0:
        return "R8U122_PATH_ENDPOINT_TEMPLATE_MARKERS"
    if int(preflight.get("required_field_gap_count", 0) or 0) > 0:
        return "R8U122_PATH_ENDPOINT_REQUIRED_FIELDS_BLOCKED"
    if int(preflight.get("required_matched_batch_deficit", 0) or 0) > 0:
        return "R8U122_PATH_ENDPOINT_MATCHED_BATCH_DEFICIT"
    if int(preflight.get("batch_alignment_gap_count", 0) or 0) > 0:
        return "R8U122_PATH_ENDPOINT_BATCH_ALIGNMENT_GAP"
    if str(preflight.get("preflight_status", "")) != (
        "field_path_endpoint_label_package_ready_for_field_layout_holdout"
    ):
        return "R8U122_PATH_ENDPOINT_PREFLIGHT_BLOCKED"
    return "R8U122_PATH_ENDPOINT_NOT_READY"


def _staging_has_path_endpoint_preview_scope(
    staging_manifest: dict[str, Any],
    selected_channel_ids: list[str],
) -> bool:
    if "R8U66_PATH_ENDPOINT_LABEL_PACKAGE" in selected_channel_ids:
        return True
    contract_tables = set(
        _string_list(
            build_field_path_endpoint_label_package_contract().get("required_tables"),
            default=(),
        )
    )
    selected_channels = _list_of_dicts(staging_manifest.get("selected_channel_manifests"))
    for channel in selected_channels:
        for table in _list_of_dicts(channel.get("table_manifests")):
            if str(table.get("table_name", "")) in contract_tables:
                return True
    return False


def _read_path_endpoint_csv_package(
    package_dir: Path,
    contract: dict[str, object],
) -> dict[str, object]:
    required_tables = _string_list(contract.get("required_tables"), default=())
    package: dict[str, object] = {}
    for table in required_tables:
        path = package_dir / f"{table}.csv"
        if not path.exists():
            continue
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            package[table] = [dict(row) for row in reader]
    return package


def _materialized_metadata_audit(package_dir: Path) -> dict[str, Any]:
    metadata_path = package_dir / "metadata.json"
    blockers: list[dict[str, Any]] = []
    if not metadata_path.exists():
        blockers.append({"blocker_id": "R8U105_METADATA_JSON_MISSING", "reason": "metadata.json:missing"})
        return {
            "metadata_path": str(metadata_path),
            "metadata_loaded": False,
            "missing_metadata_fields": list(R7_METADATA_REQUIRED_FIELDS),
            "metadata_template_field_count": 0,
            "metadata_blocker_count": len(blockers),
            "metadata_blockers": blockers,
        }
    try:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        blockers.append(
            {
                "blocker_id": "R8U105_METADATA_JSON_INVALID",
                "reason": f"metadata.json:{type(exc).__name__}",
            }
        )
        return {
            "metadata_path": str(metadata_path),
            "metadata_loaded": False,
            "missing_metadata_fields": list(R7_METADATA_REQUIRED_FIELDS),
            "metadata_template_field_count": 0,
            "metadata_blocker_count": len(blockers),
            "metadata_blockers": blockers,
        }
    metadata = metadata if isinstance(metadata, dict) else {}
    missing = [field for field in R7_METADATA_REQUIRED_FIELDS if not str(metadata.get(field, "")).strip()]
    template_fields = [
        field
        for field in R7_METADATA_REQUIRED_FIELDS
        if _has_template_marker(str(metadata.get(field, "")))
    ]
    if missing:
        blockers.append(
            {
                "blocker_id": "R8U105_METADATA_REQUIRED_FIELDS_MISSING",
                "reason": ",".join(missing),
            }
        )
    if template_fields:
        blockers.append(
            {
                "blocker_id": "R8U105_METADATA_TEMPLATE_MARKERS",
                "reason": ",".join(template_fields),
            }
        )
    if str(metadata.get("data_origin", "")).strip().lower() != "field":
        blockers.append(
            {
                "blocker_id": "R8U105_METADATA_NON_FIELD_ORIGIN",
                "reason": str(metadata.get("data_origin", "missing")),
            }
        )
    return {
        "metadata_path": str(metadata_path),
        "metadata_loaded": bool(metadata),
        "missing_metadata_fields": missing,
        "metadata_template_fields": template_fields,
        "metadata_template_field_count": len(template_fields),
        "metadata_data_origin": str(metadata.get("data_origin", "")),
        "metadata_blocker_count": len(blockers),
        "metadata_blockers": blockers,
    }


def _materialized_table_audit(package_dir: Path, table_manifest: dict[str, Any]) -> dict[str, Any]:
    output_file = str(table_manifest.get("output_file", "unknown.csv"))
    table_name = str(table_manifest.get("table_name", output_file.replace(".csv", "")))
    path = package_dir / output_file
    required_columns = _string_list(table_manifest.get("required_columns"), default=())
    blockers: list[dict[str, Any]] = []
    if not path.exists():
        blockers.append({"blocker_id": "R8U105_TABLE_FILE_MISSING", "table_name": table_name, "reason": output_file})
        return {
            "table_name": table_name,
            "output_file": output_file,
            "file_exists": False,
            "row_count": 0,
            "missing_columns": required_columns,
            "missing_column_count": len(required_columns),
            "template_marker_row_count": 0,
            "non_field_row_count": 0,
            "table_blockers": blockers,
        }
    rows, headers = _read_csv_rows(path)
    missing_columns = [column for column in required_columns if column not in headers]
    if missing_columns:
        blockers.append(
            {
                "blocker_id": "R8U105_TABLE_HEADER_GAP",
                "table_name": table_name,
                "reason": ",".join(missing_columns),
            }
        )
    if not rows:
        blockers.append({"blocker_id": "R8U105_TABLE_EMPTY", "table_name": table_name, "reason": output_file})
    template_rows = [
        row for row in rows if _materialized_row_has_template_marker(row, table_manifest)
    ]
    non_field_rows = [
        row for row in rows if str(row.get("data_origin", "")).strip().lower() != "field"
    ]
    blueprint_audit = _materialized_table_blueprint_audit(rows, table_manifest)
    if template_rows:
        blockers.append(
            {
                "blocker_id": "R8U105_TABLE_TEMPLATE_MARKERS",
                "table_name": table_name,
                "reason": f"{len(template_rows)} rows",
            }
        )
    if non_field_rows:
        blockers.append(
            {
                "blocker_id": "R8U105_TABLE_NON_FIELD_ORIGIN",
                "table_name": table_name,
                "reason": f"{len(non_field_rows)} rows",
            }
        )
    if int(blueprint_audit.get("blueprint_missing_row_count", 0) or 0) > 0:
        blockers.append(
            {
                "blocker_id": "R8U105_TABLE_BLUEPRINT_ROWS_MISSING",
                "table_name": table_name,
                "reason": f"{blueprint_audit['blueprint_missing_row_count']} blueprint rows",
            }
        )
    return {
        "table_name": table_name,
        "output_file": output_file,
        "file_exists": True,
        "row_count": len(rows),
        "header_count": len(headers),
        "missing_columns": missing_columns,
        "missing_column_count": len(missing_columns),
        "template_marker_row_count": len(template_rows),
        "non_field_row_count": len(non_field_rows),
        "blueprint_expected_row_count": blueprint_audit["blueprint_expected_row_count"],
        "blueprint_matched_row_count": blueprint_audit["blueprint_matched_row_count"],
        "blueprint_missing_row_count": blueprint_audit["blueprint_missing_row_count"],
        "missing_blueprint_rows": blueprint_audit["missing_blueprint_rows"],
        "table_blockers": blockers,
    }


def _materialized_table_blueprint_audit(
    rows: list[dict[str, Any]],
    table_manifest: dict[str, Any],
) -> dict[str, Any]:
    blueprints = _list_of_dicts(table_manifest.get("row_blueprints"))
    missing: list[dict[str, Any]] = []
    matched_count = 0
    for blueprint in blueprints:
        expected = _dict(blueprint.get("output_row"))
        compare_columns = [
            column
            for column, value in expected.items()
            if str(value).strip()
        ]
        if any(_csv_row_matches_blueprint(row, expected, compare_columns) for row in rows):
            matched_count += 1
            continue
        missing.append(
            {
                "row_blueprint_id": str(blueprint.get("row_blueprint_id", "unknown_blueprint")),
                "source_response_row_ids": _string_list(
                    blueprint.get("source_response_row_ids"),
                    default=(),
                ),
                "required_non_empty_columns": compare_columns,
            }
        )
    return {
        "blueprint_expected_row_count": len(blueprints),
        "blueprint_matched_row_count": matched_count,
        "blueprint_missing_row_count": len(missing),
        "missing_blueprint_rows": missing[:20],
    }


def _materialized_row_has_template_marker(
    row: dict[str, Any],
    table_manifest: dict[str, Any],
) -> bool:
    required_columns = _string_list(table_manifest.get("required_columns"), default=())
    field_names = set(_string_list(table_manifest.get("field_names"), default=()))
    identity_columns = [column for column in required_columns if column not in field_names]
    for column in identity_columns:
        value = str(row.get(column, ""))
        if _has_template_marker(value):
            return True
    for column in field_names:
        value = str(row.get(column, "")).strip()
        if value and _has_template_marker(value):
            return True
    return False


def _csv_row_matches_blueprint(
    row: dict[str, Any],
    expected: dict[str, Any],
    compare_columns: list[str],
) -> bool:
    return all(str(row.get(column, "")) == str(expected.get(column, "")) for column in compare_columns)


def _read_csv_rows(path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        headers = [str(header) for header in (reader.fieldnames or [])]
        return [dict(row) for row in reader], headers


def _materialized_next_operator_action(blockers: list[dict[str, Any]]) -> str:
    if not blockers:
        return "set_package_pointer_and_run_external_activation_router"
    blocker = str(blockers[0].get("blocker_id", "R8U105_UNKNOWN_BLOCKER"))
    return {
        "R8U105_STAGING_MANIFEST_NOT_READY": "complete_field_activation_staging_manifest_before_materializing_package",
        "R8U105_SET_MATERIALIZED_PACKAGE_DIR": "set_materialized_package_directory_path",
        "R8U105_PACKAGE_DIR_MISSING": "create_or_correct_materialized_package_directory",
        "R8U105_PACKAGE_PATH_NOT_DIRECTORY": "submit_materialized_package_directory_not_file",
        "R8U105_METADATA_JSON_MISSING": "add_metadata_json_with_field_origin_and_required_ids",
        "R8U105_METADATA_JSON_INVALID": "repair_metadata_json",
        "R8U105_METADATA_REQUIRED_FIELDS_MISSING": "fill_required_metadata_fields",
        "R8U105_METADATA_TEMPLATE_MARKERS": "replace_metadata_template_markers",
        "R8U105_METADATA_NON_FIELD_ORIGIN": "set_metadata_data_origin_field_only_for_real_field_package",
        "R8U105_TABLE_FILE_MISSING": "create_missing_csv_tables_from_staging_manifest",
        "R8U105_TABLE_HEADER_GAP": "add_required_csv_columns_from_staging_manifest",
        "R8U105_TABLE_EMPTY": "add_real_field_rows_to_csv_tables",
        "R8U105_TABLE_TEMPLATE_MARKERS": "replace_csv_template_markers_with_real_field_values",
        "R8U105_TABLE_NON_FIELD_ORIGIN": "set_csv_data_origin_field_only_for_real_field_rows",
        "R8U105_TABLE_BLUEPRINT_ROWS_MISSING": "materialize_csv_rows_from_field_activation_row_blueprints",
    }.get(blocker, "repair_materialized_package_blockers")


def _external_readiness_step(
    step_id: str,
    *,
    status: str,
    ready: bool,
    blocker_id: str,
    next_operator_action: str,
    evidence: dict[str, Any],
) -> dict[str, Any]:
    return {
        "step_id": step_id,
        "status": status,
        "ready": ready,
        "blocker_id": "" if ready else blocker_id,
        "next_operator_action": "step_ready_continue" if ready else next_operator_action,
        "evidence": evidence,
    }


def _external_readiness_blocked_status(step_id: str) -> str:
    return {
        "response_source": "field_activation_external_readiness_waiting_for_external_response",
        "schema_preflight": "field_activation_external_readiness_blocked_at_schema_preflight",
        "response_preflight": "field_activation_external_readiness_blocked_at_response_preflight",
        "repair_work_order": "field_activation_external_readiness_blocked_at_repair_work_order",
        "package_assembly": "field_activation_external_readiness_blocked_at_package_assembly",
        "package_staging": "field_activation_external_readiness_blocked_at_package_staging",
        "materialized_package_preflight": (
            "field_activation_external_readiness_blocked_at_materialized_package_preflight"
        ),
    }.get(step_id, "field_activation_external_readiness_blocked_at_unknown_step")


def _response_submission_packet_status(
    *,
    response_source_preflight: dict[str, Any],
    response_preflight: dict[str, Any],
    external_readiness_gate: dict[str, Any],
) -> str:
    if bool(response_preflight.get("can_route_to_external_activation_router", False)):
        return "field_activation_response_submission_packet_response_ready_for_package_assembly"
    source_status = str(response_source_preflight.get("source_preflight_status", ""))
    if source_status == "field_activation_response_source_using_default_template":
        return "field_activation_response_submission_packet_waiting_for_external_response"
    if not bool(response_source_preflight.get("can_run_response_preflight", False)):
        return "field_activation_response_submission_packet_blocked_at_source_preflight"
    if str(external_readiness_gate.get("first_blocked_step", "")) == "response_preflight":
        return "field_activation_response_submission_packet_blocked_at_response_preflight"
    return "field_activation_response_submission_packet_blocked_before_router_submission"


def _response_submission_next_operator_action(
    *,
    status: str,
    response_source_preflight: dict[str, Any],
    response_repair_work_order: dict[str, Any],
    external_readiness_gate: dict[str, Any],
) -> str:
    if status == "field_activation_response_submission_packet_waiting_for_external_response":
        return "fill_response_template_and_set_FIELD_ACTIVATION_RESPONSE_PATH"
    if status == "field_activation_response_submission_packet_blocked_at_source_preflight":
        return str(
            response_source_preflight.get(
                "next_operator_action",
                "repair_FIELD_ACTIVATION_RESPONSE_PATH_file_or_json_shape",
            )
        )
    if status == "field_activation_response_submission_packet_response_ready_for_package_assembly":
        return "stage_no_write_external_package_candidates_then_run_materialized_package_preflight"
    return str(
        response_repair_work_order.get(
            "next_operator_action",
            external_readiness_gate.get(
                "next_operator_action",
                "inspect_field_activation_response_submission_packet",
            ),
        )
    )


def _response_submission_top_repair_items(
    response_repair_work_order: dict[str, Any],
) -> list[dict[str, Any]]:
    rows = _list_of_dicts(response_repair_work_order.get("repair_items"))
    return [
        {
            "repair_id": row.get("repair_id", ""),
            "priority": row.get("priority", ""),
            "scope": row.get("scope", ""),
            "required_action": row.get("required_action", ""),
        }
        for row in rows[:5]
    ]


def _route_rows(external_conditions: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows = external_conditions.get("router_route_summary", [])
    if not isinstance(rows, list):
        return {}
    return {
        str(row.get("channel_id", "unknown_channel")): row
        for row in rows
        if isinstance(row, dict)
    }


def _channels(external_conditions: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows = external_conditions.get("channels", [])
    if not isinstance(rows, list):
        return {}
    return {
        str(row.get("channel_id", "unknown_channel")): row
        for row in rows
        if isinstance(row, dict)
    }


def _dict(value: object) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list_of_dicts(value: object) -> list[dict[str, Any]]:
    return [row for row in value if isinstance(row, dict)] if isinstance(value, list) else []


def _string_list(value: object, *, default: tuple[str, ...]) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value]
    if isinstance(value, tuple):
        return [str(item) for item in value]
    return list(default)


def _safe_int(value: object) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def _ratio(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return round(numerator / denominator, 3)


def _missing_fields(row: dict[str, Any], required_fields: list[str]) -> list[str]:
    return [field for field in required_fields if field not in row]


def _missing_by_index(
    rows: list[dict[str, Any]],
    required_fields: list[str],
    *,
    id_field: str,
) -> list[dict[str, Any]]:
    missing_rows = []
    for index, row in enumerate(rows):
        missing = _missing_fields(row, required_fields)
        if missing:
            missing_rows.append(
                {
                    "row_index": index,
                    "row_id": str(row.get(id_field, f"row_{index}")),
                    "missing_fields": missing,
                }
            )
    return missing_rows


def _no_write_schema_violations(
    assembly_plan: dict[str, Any],
    channel_plans: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    violations: list[dict[str, Any]] = []
    for field in ("can_resume_model_chain", "can_write_to_actuator", "can_write_to_release_gate"):
        if bool(assembly_plan.get(field, False)):
            violations.append({"scope": "assembly_plan", "field": field, "value": assembly_plan.get(field)})
    for channel in channel_plans:
        for field in ("can_resume_model_chain", "can_write_to_actuator", "can_write_to_release_gate"):
            if bool(channel.get(field, False)):
                violations.append(
                    {
                        "scope": "channel_plan",
                        "channel_id": str(channel.get("channel_id", "unknown_channel")),
                        "field": field,
                        "value": channel.get(field),
                    }
                )
    return violations


def _dedupe(values: list[Any]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        text = str(value)
        if text and text not in seen:
            seen.add(text)
            result.append(text)
    return result


def _response_value_payload_missing(row: dict[str, Any]) -> bool:
    if "evidence_value" not in row:
        return True
    value = row.get("evidence_value")
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    if isinstance(value, (list, tuple, set, dict)):
        return len(value) == 0
    return False


def _response_value_payload_has_template_marker(row: dict[str, Any]) -> bool:
    return _row_has_template_marker({"evidence_value": row.get("evidence_value")})


def _row_has_template_marker(row: dict[str, Any]) -> bool:
    return any(_has_template_marker(str(value)) for value in row.values())


def _has_template_marker(value: str) -> bool:
    lowered = value.strip().lower()
    return (
        not lowered
        or "todo" in lowered
        or "template" in lowered
        or "placeholder" in lowered
        or lowered in {"sample", "synthetic", "nan", "none", "null"}
    )


def _truthy(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes", "y", "confirmed"}


def _blocked_row_ids(rows: list[dict[str, Any]]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for row in rows:
        row_id = str(row.get("response_row_id", "unknown_response_row"))
        if row_id not in seen:
            seen.add(row_id)
            result.append(row_id)
    return result[:30]

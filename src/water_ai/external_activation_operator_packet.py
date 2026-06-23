from __future__ import annotations

from pathlib import Path
from typing import Any


PACKET_ID = "R8u130_external_activation_operator_action_packet"


def build_external_activation_operator_action_packet(
    *,
    core_gate: dict[str, Any],
    external_activation_router: dict[str, Any],
    catalyst_response_submission_kit: dict[str, Any],
    focused_catalyst_response_merge: dict[str, Any],
    focused_catalyst_response_template: dict[str, Any],
) -> dict[str, Any]:
    """Build a single operator-facing packet for the current external activation step."""

    template_rows = _list_of_dicts(focused_catalyst_response_template.get("evidence_rows"))
    repair_work_order = _dict_like(
        focused_catalyst_response_merge.get("focused_catalyst_response_repair_work_order")
    )
    expected_rows = _first_int(
        catalyst_response_submission_kit.get("target_response_row_count"),
        focused_catalyst_response_template.get("required_response_row_count"),
        focused_catalyst_response_merge.get("expected_focused_response_row_count"),
        default=len(template_rows),
    )
    minimum_batch_count = _first_int(
        catalyst_response_submission_kit.get("minimum_matched_batch_count"),
        focused_catalyst_response_template.get("minimum_matched_batch_count"),
        default=3,
    )
    template_path = str(
        catalyst_response_submission_kit.get(
            "focused_response_template_path",
            "outputs/catalyst_response_submission_kit/focused_catalyst_response_template.json",
        )
    )
    schema_path = str(
        catalyst_response_submission_kit.get(
            "focused_response_schema_path",
            "outputs/catalyst_response_submission_kit/focused_catalyst_response_schema.json",
        )
    )
    merge_plan_path = str(
        catalyst_response_submission_kit.get(
            "full_response_merge_plan_path",
            "outputs/catalyst_response_submission_kit/focused_to_full_response_merge_plan.json",
        )
    )
    merge_status = str(focused_catalyst_response_merge.get("preflight_status", "not_available"))
    source_status = str(
        focused_catalyst_response_merge.get("source_preflight_status", "not_available")
    )
    repair_status = str(repair_work_order.get("work_order_status", "not_available"))
    repair_next_action = str(repair_work_order.get("next_operator_action", ""))
    handoff_action = _router_or_core_handoff_action(core_gate, external_activation_router)
    can_submit_candidate = bool(
        focused_catalyst_response_merge.get(
            "can_submit_candidate_as_FIELD_ACTIVATION_RESPONSE_PATH",
            False,
        )
    )
    candidate_self_declared_submit_ready = bool(
        focused_catalyst_response_merge.get(
            "merged_full_response_candidate_self_declared_submit_ready",
            can_submit_candidate,
        )
    )
    candidate_submit_ready = can_submit_candidate and candidate_self_declared_submit_ready
    candidate_availability_status = str(
        focused_catalyst_response_merge.get(
            "merged_full_response_candidate_availability_status",
            (
                "candidate_ready_for_FIELD_ACTIVATION_RESPONSE_PATH_preflight_only"
                if candidate_submit_ready
                else "candidate_availability_not_available"
            ),
        )
    )
    candidate_external_response_supplied = bool(
        focused_catalyst_response_merge.get(
            "merged_full_response_candidate_external_response_supplied",
            False,
        )
    )
    candidate_use_boundary = str(
        focused_catalyst_response_merge.get(
            "merged_full_response_candidate_use_boundary",
            "",
        )
    )
    packet_status = _packet_status(
        can_submit_candidate=candidate_submit_ready,
        repair_status=repair_status,
        merge_status=merge_status,
        source_status=source_status,
    )
    focused_template_ready = len(template_rows) == expected_rows and expected_rows > 0
    next_operator_action = _packet_next_operator_action(
        can_submit_candidate=candidate_submit_ready,
        repair_next_action=repair_next_action,
        handoff_action=handoff_action,
    )
    current_commands = _current_commands(
        packet_status=packet_status,
        template_path=template_path,
    )
    boundary_checks = _boundary_checks(
        template_rows=template_rows,
        minimum_batch_count=minimum_batch_count,
    )
    boundary_pass = all(bool(check["pass"]) for check in boundary_checks)
    return {
        "packet_id": PACKET_ID,
        "packet_type": "external_activation_operator_next_action_packet",
        "architecture_layer": "verification_governance_to_external_execution_handoff",
        "enhanced_abilities": ["verifiability", "engineering_feasibility", "evolvability"],
        "source_stage_decision": str(core_gate.get("stage_decision", "")),
        "source_self_interrupt_verdict": str(core_gate.get("self_interrupt_verdict", "")),
        "source_router_status": str(external_activation_router.get("router_status", "")),
        "source_router_highest_priority_blocker": str(
            external_activation_router.get("highest_priority_blocker", "")
        ),
        "packet_status": packet_status,
        "target_hidden_state": str(
            focused_catalyst_response_template.get(
                "target_hidden_state",
                focused_catalyst_response_merge.get("target_hidden_state", "catalyst_activity"),
            )
        ),
        "source_env_var": str(
            focused_catalyst_response_merge.get("source_env_var", "FOCUSED_CATALYST_RESPONSE_PATH")
        ),
        "target_full_response_env_var": "FIELD_ACTIVATION_RESPONSE_PATH",
        "focused_template_path": template_path,
        "focused_schema_path": schema_path,
        "focused_merge_plan_path": merge_plan_path,
        "focused_merge_runner": "experiments/run_focused_catalyst_response_merge.py",
        "field_activation_runner": "experiments/run_field_activation_matrix.py",
        "agent50_runner": "experiments/run_agent50_model_core_governance.py",
        "merged_full_response_candidate_path": (
            "outputs/focused_catalyst_response_merge/"
            "merged_full_field_activation_response_candidate.json"
        ),
        "expected_focused_response_row_count": expected_rows,
        "template_evidence_row_count": len(template_rows),
        "focused_template_ready": focused_template_ready,
        "minimum_matched_batch_count": minimum_batch_count,
        "required_row_fields": _string_list(
            catalyst_response_submission_kit.get("required_row_fields")
        ),
        "operator_instructions": _string_list(
            focused_catalyst_response_template.get("operator_instructions")
        ),
        "source_preflight_status": source_status,
        "focused_merge_preflight_status": merge_status,
        "focused_merge_row_preflight_pass": bool(
            focused_catalyst_response_merge.get("row_preflight_pass", False)
        ),
        "focused_merge_can_submit_candidate_as_FIELD_ACTIVATION_RESPONSE_PATH": (
            can_submit_candidate
        ),
        "focused_candidate_availability_status": candidate_availability_status,
        "focused_candidate_self_declared_submit_ready": candidate_self_declared_submit_ready,
        "focused_candidate_external_response_supplied": candidate_external_response_supplied,
        "focused_candidate_operator_packet_submit_ready": candidate_submit_ready,
        "focused_candidate_use_boundary": candidate_use_boundary,
        "focused_repair_work_order_status": repair_status,
        "focused_repair_item_count": _first_int(repair_work_order.get("repair_item_count"), default=0),
        "focused_repair_highest_priority_repair_id": str(
            repair_work_order.get("highest_priority_repair_id", "")
        ),
        "focused_repair_next_operator_action": repair_next_action,
        "handoff_next_operator_action": handoff_action,
        "packet_next_operator_action": next_operator_action,
        "next_operator_action": next_operator_action,
        "operator_steps": _operator_steps(template_path=template_path),
        "current_commands": current_commands,
        "boundary_checks": boundary_checks,
        "operator_packet_boundary_pass": boundary_pass,
        "can_generate_field_evidence": False,
        "can_resume_model_chain": False,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
        "can_emit_field_supported_claim": False,
        "no_write_boundary": (
            "This packet only tells an operator how to fill and validate the focused catalyst "
            "response. It cannot generate field evidence, resume the model chain, write actuator "
            "policy, write a release gate, relax Agent49 catalyst guardrails, pass Agent51 holdout "
            "or emit a field-supported claim."
        ),
        "rejection_boundaries": [
            "Reject template/sample/synthetic rows as field evidence.",
            "Reject rows with TODO/template markers in required evidence payloads.",
            "Reject responses that do not use at least the minimum shared real batch_id count.",
            "Reject responses whose no_write_boundary_confirmed is not true on every row.",
            "Reject any shortcut that skips focused merge, full response preflight, materialized package preflight, replay/holdout or operator review.",
        ],
    }


def _packet_status(
    *,
    can_submit_candidate: bool,
    repair_status: str,
    merge_status: str,
    source_status: str,
) -> str:
    if can_submit_candidate:
        return "operator_packet_ready_to_set_FIELD_ACTIVATION_RESPONSE_PATH"
    if repair_status in {
        "focused_catalyst_response_repair_work_order_blocked_at_source_preflight",
        "focused_catalyst_response_repair_work_order_blocked_at_row_preflight",
        "focused_catalyst_response_repair_work_order_blocked_at_batch_alignment",
    }:
        return "operator_packet_blocked_by_focused_repair_work_order"
    if source_status == "focused_catalyst_response_source_using_default_template":
        return "operator_packet_waiting_for_focused_catalyst_response"
    if merge_status == "focused_catalyst_response_merge_waiting_for_FOCUSED_CATALYST_RESPONSE_PATH":
        return "operator_packet_waiting_for_focused_catalyst_response"
    return "operator_packet_waiting_for_external_activation"


def _packet_next_operator_action(
    *,
    can_submit_candidate: bool,
    repair_next_action: str,
    handoff_action: str,
) -> str:
    if can_submit_candidate:
        return "set_FIELD_ACTIVATION_RESPONSE_PATH_to_merged_full_response_candidate"
    if repair_next_action:
        return repair_next_action
    return handoff_action or "inspect_external_activation_router"


def _operator_steps(*, template_path: str) -> list[dict[str, Any]]:
    return [
        {
            "step_id": "OP1_FILL_FOCUSED_TEMPLATE",
            "order": 1,
            "action": "fill_focused_catalyst_response_template_with_real_field_values",
            "input_path": template_path,
            "output_expectation": "a reviewer-filled JSON file with six catalyst_activity evidence rows",
            "must_not_use": "synthetic/sample/template/TODO values",
        },
        {
            "step_id": "OP2_SET_FOCUSED_ENV",
            "order": 2,
            "action": "set_FOCUSED_CATALYST_RESPONSE_PATH",
            "command_template": "export FOCUSED_CATALYST_RESPONSE_PATH=/absolute/path/to/filled_focused_response.json",
            "output_expectation": "focused source preflight can load the operator-supplied JSON",
        },
        {
            "step_id": "OP3_RUN_FOCUSED_MERGE",
            "order": 3,
            "action": "run_focused_merge_preflight",
            "command": ".venv/bin/python experiments/run_focused_catalyst_response_merge.py",
            "expected_ready_status": (
                "focused_catalyst_response_merge_ready_for_FIELD_ACTIVATION_RESPONSE_PATH_candidate"
            ),
        },
        {
            "step_id": "OP4_SET_FULL_RESPONSE_CANDIDATE",
            "order": 4,
            "action": "set_FIELD_ACTIVATION_RESPONSE_PATH_if_focused_merge_ready",
            "command_template": (
                "export FIELD_ACTIVATION_RESPONSE_PATH="
                "outputs/focused_catalyst_response_merge/merged_full_field_activation_response_candidate.json"
            ),
            "condition": "only after OP3 ready status passes",
        },
        {
            "step_id": "OP5_RERUN_MAIN_GATES",
            "order": 5,
            "action": "rerun_field_activation_and_agent50",
            "commands": [
                ".venv/bin/python experiments/run_field_activation_matrix.py",
                ".venv/bin/python experiments/run_agent50_model_core_governance.py",
            ],
            "condition": "only after FIELD_ACTIVATION_RESPONSE_PATH points to the merged candidate",
        },
    ]


def _current_commands(*, packet_status: str, template_path: str) -> list[str]:
    if packet_status == "operator_packet_ready_to_set_FIELD_ACTIVATION_RESPONSE_PATH":
        return [
            "export FIELD_ACTIVATION_RESPONSE_PATH=outputs/focused_catalyst_response_merge/merged_full_field_activation_response_candidate.json",
            ".venv/bin/python experiments/run_field_activation_matrix.py",
            ".venv/bin/python experiments/run_agent50_model_core_governance.py",
        ]
    return [
        f"fill {template_path} with real field values",
        "export FOCUSED_CATALYST_RESPONSE_PATH=/absolute/path/to/filled_focused_response.json",
        ".venv/bin/python experiments/run_focused_catalyst_response_merge.py",
    ]


def _boundary_checks(
    *,
    template_rows: list[dict[str, Any]],
    minimum_batch_count: int,
) -> list[dict[str, Any]]:
    return [
        {
            "check_id": "template_has_rows",
            "pass": bool(template_rows),
            "detail": f"template row count = {len(template_rows)}",
        },
        {
            "check_id": "minimum_batch_count_declared",
            "pass": minimum_batch_count > 0,
            "detail": f"minimum shared batch count = {minimum_batch_count}",
        },
        {
            "check_id": "no_write_confirmation_fields_present",
            "pass": all("no_write_boundary_confirmed" in row for row in template_rows),
            "detail": "each template row must expose no_write_boundary_confirmed",
        },
        {
            "check_id": "template_rows_are_not_field_evidence",
            "pass": True,
            "detail": "template TODO rows are collection instructions only, not field evidence",
        },
    ]


def _router_or_core_handoff_action(
    core_gate: dict[str, Any],
    external_activation_router: dict[str, Any],
) -> str:
    router_action = str(external_activation_router.get("next_operator_action", ""))
    if router_action:
        return router_action
    resume_conditions = _dict_like(core_gate.get("external_resume_conditions"))
    return str(resume_conditions.get("router_next_operator_action", ""))


def _dict_like(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list_of_dicts(value: Any) -> list[dict[str, Any]]:
    return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []


def _string_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value]
    if isinstance(value, str) and value:
        return [value]
    return []


def _first_int(*values: Any, default: int = 0) -> int:
    for value in values:
        try:
            if value is not None and value != "":
                return int(value)
        except (TypeError, ValueError):
            continue
    return default


def path_exists(path: str | Path, *, project_root: str | Path) -> bool:
    """Small public helper used by runners/tests without binding packet logic to the filesystem."""

    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = Path(project_root) / candidate
    return candidate.exists()

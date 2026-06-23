from __future__ import annotations

from typing import Any


TARGET_HIDDEN_STATE = "catalyst_activity"
GATE_ID = "R8u110_catalyst_evidence_response_gate"


def build_catalyst_evidence_response_gate(
    *,
    observation_response_bridge: dict[str, Any],
    response: dict[str, Any],
    response_source_preflight: dict[str, Any],
    response_preflight: dict[str, Any],
    response_submission_packet: dict[str, Any],
) -> dict[str, Any]:
    """Preflight the catalyst-focused response rows without treating them as field proof."""

    target_rows = _target_rows(observation_response_bridge)
    response_rows = _response_rows_by_id(response)
    row_results = [_row_result(target, response_rows.get(str(target["response_row_id"]))) for target in target_rows]
    missing = [row for row in row_results if row["row_status"] == "missing_response_row"]
    blocked = [row for row in row_results if row["blocking_issue_count"] > 0]
    row_level_ready = bool(row_results) and not missing and not blocked
    batch_alignment = _batch_alignment(row_results, observation_response_bridge)
    source_external = bool(response_source_preflight.get("external_response_supplied", False))
    full_response_ready = (
        str(response_preflight.get("preflight_status", ""))
        == "field_activation_response_ready_for_external_package_preflight"
    )
    status = _gate_status(
        source_external=source_external,
        row_level_ready=row_level_ready,
        batch_alignment_pass=bool(batch_alignment["matched_batch_requirement_pass"]),
    )
    return {
        "gate_id": GATE_ID,
        "gate_type": "focused_catalyst_activity_response_gate",
        "gate_status": status,
        "target_hidden_state": TARGET_HIDDEN_STATE,
        "source_bridge_id": observation_response_bridge.get("bridge_id", "unknown_bridge"),
        "source_bridge_status": observation_response_bridge.get("bridge_status", "unknown"),
        "response_submission_packet_status": response_submission_packet.get("packet_status", "unknown"),
        "response_source_preflight_status": response_source_preflight.get("source_preflight_status", "unknown"),
        "response_source_external_response_supplied": source_external,
        "full_response_preflight_status": response_preflight.get("preflight_status", "unknown"),
        "full_response_ready_for_external_package_preflight": full_response_ready,
        "target_response_row_count": len(target_rows),
        "provided_target_response_row_count": sum(1 for row in row_results if row["row_status"] != "missing_response_row"),
        "missing_target_response_row_count": len(missing),
        "blocked_target_response_row_count": len(blocked),
        "row_level_preflight_pass": row_level_ready,
        "target_row_results": row_results,
        "batch_alignment": batch_alignment,
        "can_route_to_focused_materialized_package_preflight": bool(
            row_level_ready and batch_alignment["matched_batch_requirement_pass"]
        ),
        "can_route_to_full_external_activation_router": bool(full_response_ready),
        "can_route_to_agent51_field_proxy_holdout": False,
        "can_relax_agent49_catalyst_uncertainty_block": False,
        "can_resume_model_chain": False,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
        "next_operator_action": _next_operator_action(
            status=status,
            packet_action=str(response_submission_packet.get("next_operator_action", "")),
        ),
        "field_boundary": (
            "This focused gate checks only whether the six catalyst_activity response rows are complete enough "
            "to be materialized into a real package candidate. It does not inspect package CSV values, does not "
            "run Agent51 holdout scoring, does not validate catalyst activity, and does not relax Agent49."
        ),
        "no_write_boundary": (
            "Even when the focused response rows pass, the result cannot write actuator policy or release gate. "
            "A real materialized field package, Agent51 holdout, replay gates and operator review remain required."
        ),
    }


def _gate_status(
    *,
    source_external: bool,
    row_level_ready: bool,
    batch_alignment_pass: bool,
) -> str:
    if not source_external:
        return "catalyst_evidence_response_gate_waiting_for_FIELD_ACTIVATION_RESPONSE_PATH"
    if not row_level_ready:
        return "catalyst_evidence_response_gate_blocked_at_priority_rows"
    if not batch_alignment_pass:
        return "catalyst_evidence_response_gate_priority_rows_ready_needs_matched_batches"
    return "catalyst_evidence_response_gate_ready_for_focused_package_preflight"


def _next_operator_action(*, status: str, packet_action: str) -> str:
    if status == "catalyst_evidence_response_gate_waiting_for_FIELD_ACTIVATION_RESPONSE_PATH":
        return packet_action or "fill_response_template_and_set_FIELD_ACTIVATION_RESPONSE_PATH"
    if status == "catalyst_evidence_response_gate_blocked_at_priority_rows":
        return "repair_catalyst_activity_priority_response_rows"
    if status == "catalyst_evidence_response_gate_priority_rows_ready_needs_matched_batches":
        return "add_at_least_three_shared_field_batch_ids_to_all_catalyst_priority_rows"
    return "materialize_focused_catalyst_package_and_run_agent51_field_proxy_holdout_preflight"


def _target_rows(bridge: dict[str, Any]) -> list[dict[str, Any]]:
    rows = [
        row
        for row in _list_of_dicts(bridge.get("priority_response_rows"))
        if str(row.get("hidden_state", "")) == TARGET_HIDDEN_STATE
    ]
    return sorted(rows, key=lambda row: (int(row.get("priority_rank", 9) or 9), str(row.get("response_row_id", ""))))


def _response_rows_by_id(response: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows = {}
    for row in _list_of_dicts(response.get("evidence_rows")):
        row_id = str(row.get("response_row_id", ""))
        if row_id:
            rows[row_id] = row
    return rows


def _row_result(target: dict[str, Any], row: dict[str, Any] | None) -> dict[str, Any]:
    row_id = str(target.get("response_row_id", ""))
    role = str(target.get("observation_role", "unknown_role"))
    if row is None:
        return {
            "response_row_id": row_id,
            "observation_role": role,
            "required_evidence": target.get("required_evidence", ""),
            "row_status": "missing_response_row",
            "blocking_issue_count": 1,
            "blocking_issues": ["missing_response_row"],
            "batch_ids": [],
        }

    issues: list[str] = []
    if str(row.get("hidden_state", "")) != TARGET_HIDDEN_STATE:
        issues.append("hidden_state_mismatch")
    if str(row.get("required_evidence", "")) != str(target.get("required_evidence", "")):
        issues.append("required_evidence_mismatch")
    if str(row.get("data_origin", "")).strip().lower() != "field":
        issues.append("data_origin_not_field")
    if _row_has_template_marker(row):
        issues.append("template_marker_present")
    if not _truthy(row.get("no_write_boundary_confirmed")):
        issues.append("no_write_boundary_not_confirmed")
    if not str(row.get("evidence_value_reference", "")).strip():
        issues.append("missing_evidence_value_reference")
    if not _batch_ids(row):
        issues.append("missing_batch_ids")
    return {
        "response_row_id": row_id,
        "observation_role": role,
        "required_evidence": target.get("required_evidence", ""),
        "row_status": "focused_row_ready" if not issues else "focused_row_blocked",
        "blocking_issue_count": len(issues),
        "blocking_issues": issues,
        "batch_ids": _batch_ids(row),
        "evidence_value_reference": row.get("evidence_value_reference", ""),
        "data_origin": row.get("data_origin", ""),
    }


def _batch_alignment(
    row_results: list[dict[str, Any]],
    bridge: dict[str, Any],
) -> dict[str, Any]:
    minimum = _minimum_matched_batch_count(bridge)
    role_to_batches = {
        str(row["observation_role"]): set(str(batch_id) for batch_id in _list(row.get("batch_ids")))
        for row in row_results
    }
    nonempty_sets = [batches for batches in role_to_batches.values() if batches]
    shared = set.intersection(*nonempty_sets) if len(nonempty_sets) == len(role_to_batches) and nonempty_sets else set()
    return {
        "minimum_matched_batch_count": minimum,
        "role_to_batch_ids": {role: sorted(batch_ids) for role, batch_ids in role_to_batches.items()},
        "matched_batch_count": len(shared),
        "matched_batch_ids_sample": sorted(shared)[:8],
        "matched_batch_requirement_pass": len(shared) >= minimum,
        "batch_boundary": (
            "Focused response rows must share at least three real field batch_id values before they can become a "
            "candidate package for Agent51 field proxy holdout. Response-level batch IDs still do not prove field "
            "values; package CSV preflight and holdout scoring remain required."
        ),
    }


def _minimum_matched_batch_count(bridge: dict[str, Any]) -> int:
    requirement = _dict(bridge.get("r2_fv4_requirement"))
    try:
        return int(requirement.get("minimum_matched_batch_count", 3) or 3)
    except (TypeError, ValueError):
        return 3


def _batch_ids(row: dict[str, Any]) -> list[str]:
    candidates = row.get("matched_batch_ids")
    if candidates is None:
        candidates = row.get("batch_ids")
    if candidates is None:
        candidates = row.get("batch_id")
    return [
        value
        for item in _list(candidates)
        for value in _split_batch_value(str(item))
        if value and not _has_template_marker(value)
    ]


def _split_batch_value(value: str) -> list[str]:
    normalized = value.replace(";", ",").replace("|", ",")
    return [part.strip() for part in normalized.split(",") if part.strip()]


def _row_has_template_marker(row: dict[str, Any]) -> bool:
    return any(_has_template_marker(value) for value in row.values() if isinstance(value, (str, int, float, bool)))


def _has_template_marker(value: object) -> bool:
    text = str(value).strip().lower()
    return not text or "todo" in text or "template" in text or text in {"nan", "none", "null"}


def _truthy(value: object) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def _dict(value: object) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: object) -> list[Any]:
    if isinstance(value, list):
        return value
    if value is None:
        return []
    return [value]


def _list_of_dicts(value: object) -> list[dict[str, Any]]:
    return [item for item in _list(value) if isinstance(item, dict)]

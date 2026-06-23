from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


BOARD_ID = "R8u154_external_package_readiness_board"
OPERATOR_PACKET_ID = "R8u155_external_package_operator_action_packet"
ACQUISITION_MATURITY_GATE_ID = "R8u156_external_package_acquisition_maturity_gate"
ACQUISITION_TERMINATION_THRESHOLDS = {
    "input_contract_completeness": 0.95,
    "output_contract_completeness": 0.95,
    "handoff_state_variable_coverage": 0.90,
    "downstream_reconnection_rate": 0.80,
    "evidence_boundary_completeness": 1.00,
    "failure_boundary_completeness": 0.90,
    "no_write_boundary_completeness": 1.00,
}


def attach_submission_readiness_gap(
    *,
    package_artifacts: dict[str, dict[str, Any]],
    candidate_id: str,
    submission_readiness_gate: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    """Attach a package-specific submission gap without mutating artifact defaults."""

    enriched = {key: dict(value) for key, value in package_artifacts.items()}
    if candidate_id not in enriched:
        return enriched
    gap = _dict(submission_readiness_gate.get("highest_priority_gap"))
    missing_tables = _list_of_strings(gap.get("missing_tables", []))
    if not gap and not missing_tables:
        return enriched
    enriched[candidate_id].update(
        {
            "submission_gap_type": str(gap.get("gap_type", "")),
            "submission_highest_priority_gap_table": str(gap.get("table", "")),
            "missing_table_count": _safe_int(
                gap.get("missing_table_count", len(missing_tables))
            )
            or len(missing_tables),
            "missing_tables": missing_tables,
            "submission_source_env_var": str(gap.get("source_env_var", "")),
        }
    )
    return enriched


def build_external_package_readiness_board(
    *,
    new_core_interface_candidate_gate: dict[str, Any],
    package_artifacts: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Aggregate all new-core external packages into one field-submission board."""

    artifacts = package_artifacts or {}
    candidate_rows = _candidate_rows(new_core_interface_candidate_gate)
    package_rows = [
        _package_row(row, artifacts.get(str(row.get("candidate_id", "")), {}))
        for row in candidate_rows
    ]
    ready_rows = [row for row in package_rows if row["package_preflight_pass"]]
    waiting_rows = [
        row
        for row in package_rows
        if not row["package_preflight_pass"]
        and "waiting_for_" in row["package_preflight_status"]
    ]
    blocked_rows = [
        row
        for row in package_rows
        if not row["package_preflight_pass"]
        and "waiting_for_" not in row["package_preflight_status"]
    ]
    unimplemented_rows = [
        row
        for row in package_rows
        if row["package_preflight_status"] == "interface_preflight_not_implemented_yet"
    ]
    highest = package_rows[0] if package_rows else {}
    first_waiting = waiting_rows[0] if waiting_rows else {}
    first_blocked = blocked_rows[0] if blocked_rows else {}
    next_row = first_blocked or first_waiting or highest
    return {
        "board_metadata": {
            "board_id": BOARD_ID,
            "board_role": "new_core_external_package_readiness_queue",
            "created_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            "source_gate_id": _dict(new_core_interface_candidate_gate.get("gate_metadata")).get(
                "gate_id",
                "",
            ),
            "source_gate_status": _dict(new_core_interface_candidate_gate.get("gate_metadata")).get(
                "gate_status",
                "",
            ),
        },
        "package_summary": {
            "package_count": len(package_rows),
            "ready_package_count": len(ready_rows),
            "waiting_package_count": len(waiting_rows),
            "blocked_package_count": len(blocked_rows),
            "unimplemented_package_count": len(unimplemented_rows),
            "all_candidate_interfaces_have_preflight": len(unimplemented_rows) == 0
            and len(package_rows) > 0,
            "highest_priority_candidate_id": str(highest.get("candidate_id", "")),
            "highest_priority_source_env_var": str(highest.get("source_env_var", "")),
            "highest_priority_package_preflight_status": str(
                highest.get("package_preflight_status", "")
            ),
            "next_operator_candidate_id": str(next_row.get("candidate_id", "")),
            "next_operator_source_env_var": str(next_row.get("source_env_var", "")),
            "next_operator_action": str(next_row.get("next_operator_action", "")),
            "can_resume_model_chain": False,
            "can_generate_field_evidence": False,
            "can_write_to_actuator": False,
            "can_write_to_release_gate": False,
        },
        "package_rows": package_rows,
        "collection_groups": _collection_groups(package_rows),
        "selection_rules": {
            "purpose": "collect real external packages before reopening model-chain claims",
            "ready_requires": [
                "external package directory supplied through its source env var",
                "required CSV tables and columns present",
                "rows use data_origin=field and pass QA",
                "minimum aligned ids across package tables",
                "package-specific safety or evidence boundary checks",
            ],
            "do_not_use_when": [
                "template rows remain",
                "source rows are synthetic/literature-only",
                "downstream replay, holdout, calibration or claim gates have not run",
            ],
        },
        "boundary": {
            "readiness_board_only": True,
            "can_generate_field_evidence": False,
            "can_resume_model_chain": False,
            "can_write_to_actuator": False,
            "can_write_to_release_gate": False,
            "boundary_statement": (
                "This board aggregates external package readiness. It does not validate field "
                "performance, does not run downstream replay/holdout/calibration, and does not "
                "authorize actuator or release-gate actions."
            ),
        },
    }


def external_package_readiness_board_report_md(board: dict[str, Any]) -> str:
    metadata = board["board_metadata"]
    summary = board["package_summary"]
    lines = [
        "# External Package Readiness Board",
        "",
        "## Role",
        "",
        (
            "This board aggregates the new-core external package interfaces into one "
            "field-submission queue. It is a readiness and routing artifact, not a field "
            "validation result."
        ),
        "",
        "## Board State",
        "",
        f"- board_id: `{metadata['board_id']}`",
        f"- source_gate_status: `{metadata['source_gate_status']}`",
        f"- package_count: `{summary['package_count']}`",
        f"- ready_package_count: `{summary['ready_package_count']}`",
        f"- waiting_package_count: `{summary['waiting_package_count']}`",
        f"- blocked_package_count: `{summary['blocked_package_count']}`",
        f"- unimplemented_package_count: `{summary['unimplemented_package_count']}`",
        (
            "- all_candidate_interfaces_have_preflight: "
            f"`{summary['all_candidate_interfaces_have_preflight']}`"
        ),
        f"- next_operator_candidate_id: `{summary['next_operator_candidate_id']}`",
        f"- next_operator_source_env_var: `{summary['next_operator_source_env_var']}`",
        f"- next_operator_action: `{summary['next_operator_action']}`",
        f"- can_generate_field_evidence: `{summary['can_generate_field_evidence']}`",
        f"- can_write_to_actuator: `{summary['can_write_to_actuator']}`",
        f"- can_write_to_release_gate: `{summary['can_write_to_release_gate']}`",
        "",
        "## Package Rows",
        "",
        (
            "| order | candidate | task | env var | status | pass | matched | template | "
            "missing tables | validation command | next action |"
        ),
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in board["package_rows"]:
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` |".format(
                row["priority_order"],
                row["candidate_id"],
                row["task_id"],
                row["source_env_var"],
                row["package_preflight_status"],
                row["package_preflight_pass"],
                row["matched_unit_summary"],
                row["template_dir"],
                row.get("missing_table_count", ""),
                row["validation_command"],
                row["next_operator_action"],
            )
        )
    lines.extend(["", "## Collection Groups", ""])
    for group in board["collection_groups"]:
        lines.append(
            "- `{}`: candidates={}, source_env_vars={}, readiness=`{}`".format(
                group["group_id"],
                group["candidate_ids"],
                group["source_env_vars"],
                group["readiness_status"],
            )
        )
    lines.extend(["", "## Boundary", "", board["boundary"]["boundary_statement"], ""])
    return "\n".join(lines)


def build_external_package_operator_action_packet(
    *, readiness_board: dict[str, Any]
) -> dict[str, Any]:
    """Turn the readiness board into an operator-facing field-package queue."""

    summary = _dict(readiness_board.get("package_summary"))
    rows = _package_rows(readiness_board)
    actions = [_operator_action(row) for row in rows]
    blocked_actions = [
        action for action in actions if action["action_status"] == "repair_preflight_blocker"
    ]
    waiting_actions = [
        action for action in actions if action["action_status"] == "collect_external_package"
    ]
    ready_actions = [
        action for action in actions if action["action_status"] == "ready_for_downstream_consumer"
    ]
    next_action = (blocked_actions or waiting_actions or ready_actions or [{}])[0]
    blocked_count = _safe_int(summary.get("blocked_package_count", len(blocked_actions)))
    waiting_count = _safe_int(summary.get("waiting_package_count", len(waiting_actions)))
    ready_count = _safe_int(summary.get("ready_package_count", len(ready_actions)))
    packet_status = _operator_packet_status(
        blocked_count=blocked_count,
        waiting_count=waiting_count,
        ready_count=ready_count,
        action_count=len(actions),
    )
    route_event = _operator_packet_route_event(packet_status)
    return {
        "packet_id": OPERATOR_PACKET_ID,
        "packet_type": "external_package_field_submission_operator_action_packet",
        "architecture_layer": "verification_governance_to_external_field_package_collection",
        "enhanced_abilities": ["verifiability", "engineering_feasibility", "evolvability"],
        "source_board_id": _dict(readiness_board.get("board_metadata")).get("board_id", ""),
        "source_board_status": _dict(readiness_board.get("board_metadata")).get(
            "source_gate_status",
            "",
        ),
        "packet_status": packet_status,
        "package_count": _safe_int(summary.get("package_count", len(actions))),
        "ready_package_count": ready_count,
        "waiting_package_count": waiting_count,
        "blocked_package_count": blocked_count,
        "unimplemented_package_count": _safe_int(summary.get("unimplemented_package_count", 0)),
        "all_candidate_interfaces_have_preflight": bool(
            summary.get("all_candidate_interfaces_have_preflight", False)
        ),
        "route_event": route_event,
        "route_reason": _operator_packet_route_reason(route_event),
        "evidence_level": _operator_packet_evidence_level(route_event),
        "next_operator_candidate_id": str(next_action.get("candidate_id", "")),
        "next_operator_source_env_var": str(next_action.get("source_env_var", "")),
        "next_operator_action": str(next_action.get("next_operator_action", "")),
        "next_operator_validation_command": str(next_action.get("validation_command", "")),
        "next_operator_template_dir": str(next_action.get("template_dir", "")),
        "next_operator_submission_gap_type": str(
            next_action.get("submission_gap_type", "")
        ),
        "next_operator_missing_table_count": _safe_int(
            next_action.get("missing_table_count", 0)
        ),
        "next_operator_missing_tables": _list_of_strings(
            next_action.get("missing_tables", [])
        ),
        "operator_actions": actions,
        "operator_action_sequence": [action["candidate_id"] for action in actions],
        "current_commands": _operator_commands(actions),
        "current_basis_refs": _operator_current_basis_refs(readiness_board),
        "not_current_basis_refs": [
            "template_rows",
            "synthetic_rows",
            "sample_rows",
            "literature_only_rows",
            "downstream_replay_holdout_calibration_not_run",
        ],
        "manual_action_required": _operator_manual_action_required(
            route_event=route_event,
            next_action=next_action,
        ),
        "can_prove": [
            "next external package to collect",
            "source env var and template directory for the next package",
            "package-specific validation command to run after submission",
            "no-write boundary before downstream validation",
        ],
        "cannot_prove": [
            "field treatment performance",
            "field-supported mechanism validity",
            "model-chain resume readiness",
            "actuator or release-gate readiness",
        ],
        "rejection_rules": [
            "Reject template rows, sample rows, literature-only rows and synthetic rows as field packages.",
            "Reject package directories that do not pass the package-specific preflight command.",
            "Reject ready-looking packages before downstream replay, holdout, calibration or claim gates run.",
            "Reject any shortcut that writes actuator policy or release gates from a readiness packet.",
        ],
        "handoff_boundary": (
            "This packet only queues external package collection and validation commands. It does "
            "not generate field evidence, does not run downstream replay/holdout/calibration, "
            "does not resume the model chain and does not authorize actuator or release-gate writes."
        ),
        "can_generate_field_evidence": False,
        "can_resume_model_chain": False,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
        "can_emit_field_supported_claim": False,
    }


def external_package_operator_action_packet_report_md(packet: dict[str, Any]) -> str:
    lines = [
        "# External Package Operator Action Packet",
        "",
        "## Role",
        "",
        (
            "This packet turns the external package readiness board into an ordered field-package "
            "collection queue. It does not generate field evidence."
        ),
        "",
        "## Packet State",
        "",
        f"- packet_id: `{packet['packet_id']}`",
        f"- packet_status: `{packet['packet_status']}`",
        f"- route_event: `{packet['route_event']}`",
        f"- route_reason: `{packet['route_reason']}`",
        f"- evidence_level: `{packet['evidence_level']}`",
        f"- package_count: `{packet['package_count']}`",
        f"- ready_package_count: `{packet['ready_package_count']}`",
        f"- waiting_package_count: `{packet['waiting_package_count']}`",
        f"- blocked_package_count: `{packet['blocked_package_count']}`",
        f"- next_operator_candidate_id: `{packet['next_operator_candidate_id']}`",
        f"- next_operator_source_env_var: `{packet['next_operator_source_env_var']}`",
        f"- next_operator_validation_command: `{packet['next_operator_validation_command']}`",
        f"- next_operator_template_dir: `{packet['next_operator_template_dir']}`",
        (
            "- next_operator_missing_table_count: "
            f"`{packet['next_operator_missing_table_count']}`"
        ),
        (
            "- next_operator_missing_tables: "
            f"`{packet['next_operator_missing_tables']}`"
        ),
        f"- manual_action_required: `{packet['manual_action_required']['required']}`",
        f"- can_generate_field_evidence: `{packet['can_generate_field_evidence']}`",
        f"- can_write_to_actuator: `{packet['can_write_to_actuator']}`",
        f"- can_write_to_release_gate: `{packet['can_write_to_release_gate']}`",
        "",
        "## Operator Actions",
        "",
        (
            "| order | candidate | env var | action status | template | validation command | "
            "missing tables | next action |"
        ),
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for action in packet["operator_actions"]:
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` |".format(
                action["priority_order"],
                action["candidate_id"],
                action["source_env_var"],
                action["action_status"],
                action["template_dir"],
                action["validation_command"],
                action.get("missing_table_count", ""),
                action["next_operator_action"],
            )
        )
    lines.extend(["", "## Commands", ""])
    for command in packet["current_commands"]:
        lines.append(f"- `{command}`")
    lines.extend(["", "## Rejection Rules", ""])
    for rule in packet["rejection_rules"]:
        lines.append(f"- {rule}")
    lines.extend(["", "## Boundary", "", packet["handoff_boundary"], ""])
    return "\n".join(lines)


def build_external_package_acquisition_maturity_gate(
    *, readiness_board: dict[str, Any], operator_action_packet: dict[str, Any]
) -> dict[str, Any]:
    """Score whether external package collection is interface-ready or field-ready."""

    summary = _dict(readiness_board.get("package_summary"))
    package_count = _safe_int(summary.get("package_count", 0))
    ready_count = _safe_int(summary.get("ready_package_count", 0))
    waiting_count = _safe_int(summary.get("waiting_package_count", 0))
    blocked_count = _safe_int(summary.get("blocked_package_count", 0))
    unimplemented_count = _safe_int(summary.get("unimplemented_package_count", 0))
    operator_actions = _list_of_dicts(operator_action_packet.get("operator_actions"))
    field_package_ready_rate = _safe_ratio(ready_count, package_count)
    interface_preflight_coverage = (
        1.0 if package_count and unimplemented_count == 0 else _safe_ratio(package_count - unimplemented_count, package_count)
    )
    operator_action_contract_coverage = _operator_action_contract_coverage(operator_actions)
    no_write_boundary_integrity = _no_write_boundary_integrity(
        operator_action_packet,
        operator_actions,
    )
    input_contract_completeness = _operator_action_list_field_coverage(
        operator_actions,
        "input_contract",
    )
    output_contract_completeness = _operator_action_list_field_coverage(
        operator_actions,
        "output_contract",
    )
    handoff_state_variable_coverage = _handoff_state_variable_coverage(
        operator_action_packet,
        operator_actions,
    )
    downstream_reconnection_rate = field_package_ready_rate
    evidence_boundary_completeness = _operator_packet_evidence_boundary_completeness(
        operator_action_packet,
    )
    failure_boundary_completeness = _operator_action_scalar_field_coverage(
        operator_actions,
        "failure_boundary",
    )
    no_write_boundary_completeness = no_write_boundary_integrity
    termination_blockers = _acquisition_termination_blockers(
        input_contract_completeness=input_contract_completeness,
        output_contract_completeness=output_contract_completeness,
        handoff_state_variable_coverage=handoff_state_variable_coverage,
        downstream_reconnection_rate=downstream_reconnection_rate,
        evidence_boundary_completeness=evidence_boundary_completeness,
        failure_boundary_completeness=failure_boundary_completeness,
        no_write_boundary_completeness=no_write_boundary_completeness,
        field_package_ready_rate=field_package_ready_rate,
    )
    module_stage_termination_pass = not termination_blockers
    score = (
        0.35 * interface_preflight_coverage
        + 0.25 * operator_action_contract_coverage
        + 0.25 * no_write_boundary_integrity
        + 0.15 * field_package_ready_rate
    )
    if blocked_count:
        score -= min(0.15, 0.05 * blocked_count)
    score = round(max(0.0, min(1.0, score)), 3)
    preflight_repair_required = blocked_count > 0
    gate_status = _acquisition_gate_status(
        blocked_count=blocked_count,
        waiting_count=waiting_count,
        ready_count=ready_count,
        package_count=package_count,
    )
    next_stage_decision = _acquisition_next_stage_decision(
        blocked_count=blocked_count,
        waiting_count=waiting_count,
        ready_count=ready_count,
        package_count=package_count,
    )
    return {
        "gate_id": ACQUISITION_MATURITY_GATE_ID,
        "gate_type": "external_package_acquisition_maturity_gate",
        "source_board_id": _dict(readiness_board.get("board_metadata")).get("board_id", ""),
        "source_packet_id": str(operator_action_packet.get("packet_id", "")),
        "gate_status": gate_status,
        "package_count": package_count,
        "ready_package_count": ready_count,
        "waiting_package_count": waiting_count,
        "blocked_package_count": blocked_count,
        "unimplemented_package_count": unimplemented_count,
        "field_package_ready_rate": field_package_ready_rate,
        "interface_preflight_coverage": interface_preflight_coverage,
        "operator_action_contract_coverage": operator_action_contract_coverage,
        "no_write_boundary_integrity": no_write_boundary_integrity,
        "termination_thresholds": dict(ACQUISITION_TERMINATION_THRESHOLDS),
        "input_contract_completeness": input_contract_completeness,
        "output_contract_completeness": output_contract_completeness,
        "handoff_state_variable_coverage": handoff_state_variable_coverage,
        "downstream_reconnection_rate": downstream_reconnection_rate,
        "evidence_boundary_completeness": evidence_boundary_completeness,
        "failure_boundary_completeness": failure_boundary_completeness,
        "no_write_boundary_completeness": no_write_boundary_completeness,
        "contract_termination_status": _acquisition_contract_termination_status(
            blocked_count=blocked_count,
            waiting_count=waiting_count,
            ready_count=ready_count,
            package_count=package_count,
            module_stage_termination_pass=module_stage_termination_pass,
        ),
        "module_stage_termination_pass": module_stage_termination_pass,
        "termination_blockers": termination_blockers,
        "termination_boundary_note": (
            "handoff_state_variable_coverage only scores operator/package lifecycle state "
            "fields; it is not field hidden-state validation."
        ),
        "acquisition_maturity_score": score,
        "score_formula": (
            "0.35*interface_preflight_coverage + "
            "0.25*operator_action_contract_coverage + "
            "0.25*no_write_boundary_integrity + 0.15*field_package_ready_rate "
            "- preflight_repair_penalty"
        ),
        "preflight_repair_required": preflight_repair_required,
        "model_chain_resume_ready": False,
        "field_evidence_generation_ready": False,
        "downstream_gate_ready": ready_count == package_count and package_count > 0,
        "next_stage_decision": next_stage_decision,
        "next_operator_candidate_id": str(
            operator_action_packet.get("next_operator_candidate_id", "")
        ),
        "next_operator_source_env_var": str(
            operator_action_packet.get("next_operator_source_env_var", "")
        ),
        "next_operator_action": str(operator_action_packet.get("next_operator_action", "")),
        "next_operator_validation_command": str(
            operator_action_packet.get("next_operator_validation_command", "")
        ),
        "can_generate_field_evidence": False,
        "can_resume_model_chain": False,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
        "can_emit_field_supported_claim": False,
        "boundary_statement": (
            "This gate scores collection-interface maturity only. It cannot resume the model "
            "chain, cannot generate field evidence, cannot run downstream replay/holdout/"
            "calibration and cannot authorize actuator or release-gate writes."
        ),
    }


def external_package_acquisition_maturity_gate_report_md(gate: dict[str, Any]) -> str:
    lines = [
        "# External Package Acquisition Maturity Gate",
        "",
        "## Gate State",
        "",
        f"- gate_id: `{gate['gate_id']}`",
        f"- gate_status: `{gate['gate_status']}`",
        f"- acquisition_maturity_score: `{gate['acquisition_maturity_score']}`",
        f"- field_package_ready_rate: `{gate['field_package_ready_rate']}`",
        f"- interface_preflight_coverage: `{gate['interface_preflight_coverage']}`",
        f"- operator_action_contract_coverage: `{gate['operator_action_contract_coverage']}`",
        f"- no_write_boundary_integrity: `{gate['no_write_boundary_integrity']}`",
        f"- input_contract_completeness: `{gate['input_contract_completeness']}`",
        f"- output_contract_completeness: `{gate['output_contract_completeness']}`",
        f"- handoff_state_variable_coverage: `{gate['handoff_state_variable_coverage']}`",
        f"- downstream_reconnection_rate: `{gate['downstream_reconnection_rate']}`",
        f"- evidence_boundary_completeness: `{gate['evidence_boundary_completeness']}`",
        f"- failure_boundary_completeness: `{gate['failure_boundary_completeness']}`",
        f"- no_write_boundary_completeness: `{gate['no_write_boundary_completeness']}`",
        f"- contract_termination_status: `{gate['contract_termination_status']}`",
        f"- module_stage_termination_pass: `{gate['module_stage_termination_pass']}`",
        f"- termination_blockers: `{gate['termination_blockers']}`",
        f"- next_stage_decision: `{gate['next_stage_decision']}`",
        f"- next_operator_source_env_var: `{gate['next_operator_source_env_var']}`",
        f"- next_operator_validation_command: `{gate['next_operator_validation_command']}`",
        f"- model_chain_resume_ready: `{gate['model_chain_resume_ready']}`",
        f"- can_generate_field_evidence: `{gate['can_generate_field_evidence']}`",
        f"- can_write_to_actuator: `{gate['can_write_to_actuator']}`",
        f"- can_write_to_release_gate: `{gate['can_write_to_release_gate']}`",
        "",
        "## Boundary",
        "",
        gate["boundary_statement"],
        "",
    ]
    return "\n".join(lines)


def _candidate_rows(candidate_gate: dict[str, Any]) -> list[dict[str, Any]]:
    rows = candidate_gate.get("candidate_rows", [])
    return [row for row in rows if isinstance(row, dict)] if isinstance(rows, list) else []


def _package_rows(board: dict[str, Any]) -> list[dict[str, Any]]:
    rows = board.get("package_rows", [])
    return [row for row in rows if isinstance(row, dict)] if isinstance(rows, list) else []


def _operator_action(row: dict[str, Any]) -> dict[str, Any]:
    if bool(row.get("package_preflight_pass", False)):
        action_status = "ready_for_downstream_consumer"
        priority_reason = "preflight_ready_waiting_for_downstream_consumer"
    elif "waiting_for_" in str(row.get("package_preflight_status", "")):
        action_status = "collect_external_package"
        priority_reason = "waiting_for_external_package"
    else:
        action_status = "repair_preflight_blocker"
        priority_reason = "blocked_preflight_before_collection"
    validation_command = str(row.get("validation_command", ""))
    action = {
        "priority_order": _safe_int(row.get("priority_order", 0)),
        "candidate_id": str(row.get("candidate_id", "")),
        "task_id": str(row.get("task_id", "")),
        "title": str(row.get("title", "")),
        "source_env_var": str(row.get("source_env_var", "")),
        "system_layer": str(row.get("system_layer", "")),
        "core_ability": str(row.get("core_ability", "")),
        "action_status": action_status,
        "priority_reason": priority_reason,
        "package_preflight_status": str(row.get("package_preflight_status", "")),
        "package_preflight_pass": bool(row.get("package_preflight_pass", False)),
        "template_dir": str(row.get("template_dir", "")),
        "preflight_json": str(row.get("preflight_json", "")),
        "report_md": str(row.get("report_md", "")),
        "validation_command": validation_command,
        "run_after_submission": [validation_command] if validation_command else [],
        "next_operator_action": str(row.get("next_operator_action", "")),
        "minimum_row_count": _safe_int(row.get("minimum_row_count", 0)),
        "matched_unit_summary": str(row.get("matched_unit_summary", "none")),
        "input_contract": list(row.get("input_contract", []))
        if isinstance(row.get("input_contract", []), list)
        else [],
        "output_contract": list(row.get("output_contract", []))
        if isinstance(row.get("output_contract", []), list)
        else [],
        "failure_boundary": str(row.get("failure_boundary", "")),
        "can_generate_field_evidence": False,
        "can_resume_model_chain": False,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
    }
    _copy_submission_gap_fields(action, row)
    return action


def _operator_packet_status(
    *, blocked_count: int, waiting_count: int, ready_count: int, action_count: int
) -> str:
    if blocked_count:
        return "external_package_operator_packet_blocked_by_preflight_repair"
    if waiting_count:
        return "external_package_operator_packet_waiting_for_field_packages"
    if ready_count and ready_count == action_count:
        return "external_package_operator_packet_ready_for_downstream_consumers"
    return "external_package_operator_packet_no_external_package_actions"


def _operator_packet_route_event(packet_status: str) -> str:
    if packet_status == "external_package_operator_packet_blocked_by_preflight_repair":
        return "route_back"
    if packet_status == "external_package_operator_packet_waiting_for_field_packages":
        return "external_activation_wait"
    if packet_status == "external_package_operator_packet_ready_for_downstream_consumers":
        return "execute_preflight"
    return "blocked"


def _operator_packet_route_reason(route_event: str) -> str:
    if route_event == "route_back":
        return "repair_external_package_preflight_before_collection_or_downstream_use"
    if route_event == "external_activation_wait":
        return "waiting_for_real_external_package_before_downstream_replay_holdout_calibration"
    if route_event == "execute_preflight":
        return "external_packages_ready_for_downstream_replay_holdout_calibration_gates"
    return "no_external_package_action_available"


def _operator_packet_evidence_level(route_event: str) -> str:
    if route_event == "execute_preflight":
        return "field_package_preflight_ready_but_not_field_evidence"
    if route_event == "route_back":
        return "operator_repair_handoff_only_not_field_evidence"
    return "operator_handoff_only_not_field_evidence"


def _operator_current_basis_refs(readiness_board: dict[str, Any]) -> list[str]:
    board_id = _dict(readiness_board.get("board_metadata")).get("board_id", "")
    refs = [
        "readiness_board.package_rows",
        "readiness_board.package_summary",
        "readiness_board.boundary",
        "operator_actions.validation_command",
    ]
    if board_id:
        refs.insert(0, f"source_board_id:{board_id}")
    return refs


def _operator_manual_action_required(
    *, route_event: str, next_action: dict[str, Any]
) -> dict[str, Any]:
    required = route_event in {"external_activation_wait", "route_back"}
    action = (
        "fill_external_package_template_with_real_field_rows_then_export_env_var"
        if route_event == "external_activation_wait"
        else "repair_external_package_preflight_blocker"
        if route_event == "route_back"
        else "run_downstream_replay_holdout_calibration_gates"
    )
    return {
        "required": required,
        "actor": "field_operator_or_user" if required else "pipeline_runner",
        "action": action,
        "source_env_var": str(next_action.get("source_env_var", "")),
        "template_dir": str(next_action.get("template_dir", "")),
        "validation_command": str(next_action.get("validation_command", "")),
        "missing_table_count": _safe_int(next_action.get("missing_table_count", 0)),
        "missing_tables": _list_of_strings(next_action.get("missing_tables", [])),
        "resume_evidence": (
            "package preflight JSON showing pass=true, or blocker fields showing the next repair"
        ),
    }


def _operator_commands(actions: list[dict[str, Any]]) -> list[str]:
    commands = []
    for action in actions:
        if action["action_status"] == "collect_external_package":
            commands.append(f"fill {action['template_dir']} with real field rows")
            commands.append(
                f"export {action['source_env_var']}=/absolute/path/to/{action['candidate_id']}"
            )
        elif action["action_status"] == "repair_preflight_blocker":
            commands.append(f"repair {action['source_env_var']} package until preflight passes")
        for command in action["run_after_submission"]:
            commands.append(command)
    return commands


def _operator_action_contract_coverage(actions: list[dict[str, Any]]) -> float:
    if not actions:
        return 0.0
    required = [
        "candidate_id",
        "source_env_var",
        "template_dir",
        "validation_command",
        "next_operator_action",
        "input_contract",
        "output_contract",
        "failure_boundary",
    ]
    complete = 0
    for action in actions:
        if all(bool(action.get(field)) for field in required):
            complete += 1
    return _safe_ratio(complete, len(actions))


def _operator_action_list_field_coverage(
    actions: list[dict[str, Any]],
    field_name: str,
) -> float:
    if not actions:
        return 0.0
    complete = sum(
        1
        for action in actions
        if isinstance(action.get(field_name), list) and bool(action.get(field_name))
    )
    return _safe_ratio(complete, len(actions))


def _operator_action_scalar_field_coverage(
    actions: list[dict[str, Any]],
    field_name: str,
) -> float:
    if not actions:
        return 0.0
    complete = sum(1 for action in actions if _present(action.get(field_name)))
    return _safe_ratio(complete, len(actions))


def _handoff_state_variable_coverage(
    packet: dict[str, Any],
    actions: list[dict[str, Any]],
) -> float:
    packet_required = [
        "packet_status",
        "route_event",
        "route_reason",
        "evidence_level",
        "manual_action_required",
        "next_operator_candidate_id",
        "next_operator_action",
        "next_operator_validation_command",
    ]
    action_required = [
        "action_status",
        "priority_reason",
        "package_preflight_status",
        "package_preflight_pass",
        "source_env_var",
        "template_dir",
        "validation_command",
        "next_operator_action",
    ]
    checks = [_present(packet.get(field)) for field in packet_required]
    for action in actions:
        checks.extend(_present(action.get(field)) for field in action_required)
    if not checks:
        return 0.0
    return round(sum(1 for item in checks if item) / len(checks), 3)


def _operator_packet_evidence_boundary_completeness(packet: dict[str, Any]) -> float:
    required = [
        "route_event",
        "route_reason",
        "evidence_level",
        "current_basis_refs",
        "not_current_basis_refs",
        "manual_action_required",
        "can_prove",
        "cannot_prove",
        "handoff_boundary",
    ]
    complete = sum(1 for field in required if _present(packet.get(field)))
    return _safe_ratio(complete, len(required))


def _no_write_boundary_integrity(
    packet: dict[str, Any],
    actions: list[dict[str, Any]],
) -> float:
    top_level_ok = all(
        packet.get(field) is False
        for field in [
            "can_generate_field_evidence",
            "can_resume_model_chain",
            "can_write_to_actuator",
            "can_write_to_release_gate",
        ]
    )
    action_ok = all(
        action.get("can_generate_field_evidence") is False
        and action.get("can_resume_model_chain") is False
        and action.get("can_write_to_actuator") is False
        and action.get("can_write_to_release_gate") is False
        for action in actions
    )
    return 1.0 if top_level_ok and action_ok else 0.0


def _acquisition_termination_blockers(
    *,
    input_contract_completeness: float,
    output_contract_completeness: float,
    handoff_state_variable_coverage: float,
    downstream_reconnection_rate: float,
    evidence_boundary_completeness: float,
    failure_boundary_completeness: float,
    no_write_boundary_completeness: float,
    field_package_ready_rate: float,
) -> list[str]:
    metrics = {
        "input_contract_completeness": input_contract_completeness,
        "output_contract_completeness": output_contract_completeness,
        "handoff_state_variable_coverage": handoff_state_variable_coverage,
        "downstream_reconnection_rate": downstream_reconnection_rate,
        "evidence_boundary_completeness": evidence_boundary_completeness,
        "failure_boundary_completeness": failure_boundary_completeness,
        "no_write_boundary_completeness": no_write_boundary_completeness,
    }
    blockers = [
        f"{name}_below_{threshold:.2f}"
        for name, threshold in ACQUISITION_TERMINATION_THRESHOLDS.items()
        if metrics[name] < threshold
    ]
    if field_package_ready_rate < 1.0:
        blockers.append("field_package_ready_rate_below_1.00")
    return blockers


def _acquisition_contract_termination_status(
    *,
    blocked_count: int,
    waiting_count: int,
    ready_count: int,
    package_count: int,
    module_stage_termination_pass: bool,
) -> str:
    if module_stage_termination_pass:
        return "external_package_contracts_complete_ready_for_downstream_gates"
    if blocked_count:
        return "external_package_contracts_blocked_by_preflight_repair"
    if waiting_count:
        return "external_package_contracts_complete_but_waiting_for_field_packages"
    if ready_count != package_count:
        return "external_package_contracts_incomplete"
    return "external_package_contracts_waiting_for_downstream_confirmation"


def _acquisition_gate_status(
    *, blocked_count: int, waiting_count: int, ready_count: int, package_count: int
) -> str:
    if blocked_count:
        return "external_package_acquisition_blocked_by_preflight_repair"
    if waiting_count:
        return "external_package_acquisition_interfaces_ready_waiting_for_field_packages"
    if ready_count and ready_count == package_count:
        return "external_package_acquisition_ready_for_downstream_gates"
    return "external_package_acquisition_not_available"


def _acquisition_next_stage_decision(
    *, blocked_count: int, waiting_count: int, ready_count: int, package_count: int
) -> str:
    if blocked_count:
        return "repair_external_package_preflight_before_collection"
    if waiting_count:
        return "collect_external_field_packages_before_downstream_gates"
    if ready_count and ready_count == package_count:
        return "run_downstream_replay_holdout_calibration_gates"
    return "define_or_repair_external_package_interfaces"


def _package_row(row: dict[str, Any], artifacts: dict[str, Any]) -> dict[str, Any]:
    matched_counts = {
        "batch": _safe_int(row.get("candidate_matched_batch_count", 0)),
        "edge": _safe_int(row.get("candidate_matched_edge_count", 0)),
        "node": _safe_int(row.get("candidate_matched_node_count", 0)),
        "transition": _safe_int(row.get("candidate_matched_transition_count", 0)),
        "sample": _safe_int(row.get("candidate_matched_sample_count", 0)),
    }
    matched_summary = ", ".join(
        f"{name}:{count}" for name, count in matched_counts.items() if count
    ) or "none"
    package_row = {
        "priority_order": _safe_int(row.get("priority_order", 0)),
        "candidate_id": str(row.get("candidate_id", "")),
        "task_id": str(row.get("task_id", "")),
        "title": str(row.get("title", "")),
        "source_env_var": str(row.get("source_env_var", "")),
        "system_layer": str(row.get("system_layer", "")),
        "core_ability": str(row.get("core_ability", "")),
        "package_preflight_status": str(row.get("candidate_preflight_status", "")),
        "package_preflight_pass": bool(row.get("candidate_preflight_pass", False)),
        "interface_candidate_status": str(row.get("interface_candidate_status", "")),
        "can_route_to_downstream_interface": bool(
            row.get("can_route_to_downstream_interface", False)
        ),
        "downstream_interface_status": str(row.get("downstream_interface_status", "")),
        "validation_command": str(row.get("validation_command", "")),
        "next_operator_action": str(row.get("next_interface_action", "")),
        "matched_counts": matched_counts,
        "matched_unit_summary": matched_summary,
        "minimum_row_count": _safe_int(row.get("minimum_row_count", 0)),
        "input_contract": list(row.get("input_contract", []))
        if isinstance(row.get("input_contract", []), list)
        else [],
        "output_contract": list(row.get("output_contract", []))
        if isinstance(row.get("output_contract", []), list)
        else [],
        "failure_boundary": str(row.get("failure_boundary", "")),
        "preflight_json": artifacts.get("preflight_json", ""),
        "template_dir": artifacts.get("template_dir", ""),
        "report_md": artifacts.get("report_md", ""),
        "can_generate_field_evidence": False,
        "can_resume_model_chain": False,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
    }
    _copy_submission_gap_fields(package_row, artifacts)
    return package_row


def _copy_submission_gap_fields(target: dict[str, Any], source: dict[str, Any]) -> None:
    if source.get("submission_gap_type"):
        target["submission_gap_type"] = str(source.get("submission_gap_type", ""))
    if source.get("submission_highest_priority_gap_table"):
        target["submission_highest_priority_gap_table"] = str(
            source.get("submission_highest_priority_gap_table", "")
        )
    missing_tables = _list_of_strings(source.get("missing_tables", []))
    if missing_tables or source.get("missing_table_count") not in (None, ""):
        target["missing_table_count"] = (
            _safe_int(source.get("missing_table_count", len(missing_tables)))
            or len(missing_tables)
        )
        target["missing_tables"] = missing_tables
    if source.get("submission_source_env_var"):
        target["submission_source_env_var"] = str(source.get("submission_source_env_var", ""))


def _collection_groups(package_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    group_specs = [
        (
            "state_estimation_and_grey_box",
            {"NCI1_GREY_BOX_CALIBRATION_PACKAGE"},
            "calibrate grey-box priors before claiming process mechanism validity",
        ),
        (
            "mechanism_evidence_kg",
            {"NCI5_FIELD_SUPPORTED_KG_EDGE_PACKAGE"},
            "connect pollutant-material-condition edges to field-supported source basis",
        ),
        (
            "control_replay_execution",
            {"NCI3_FIELD_CONTROL_REPLAY_PACKAGE"},
            "evaluate multi-facility control candidates offline before any actuator promotion",
        ),
        (
            "sparse_observation_layout",
            {"NCI4_SPARSE_TOPOLOGY_INSTALLABILITY_PACKAGE"},
            "ground sparse sensing layout in real topology, installability and labels",
        ),
        (
            "soft_sensor_missingness",
            {"NCI2_FIELD_MISSINGNESS_REPLAY_PACKAGE"},
            "test soft-sensor robustness under real missingness and sensor-quality events",
        ),
    ]
    groups = []
    by_id = {row["candidate_id"]: row for row in package_rows}
    for group_id, candidate_ids, purpose in group_specs:
        rows = [by_id[candidate_id] for candidate_id in candidate_ids if candidate_id in by_id]
        ready = sum(1 for row in rows if row["package_preflight_pass"])
        waiting = sum(
            1
            for row in rows
            if not row["package_preflight_pass"] and "waiting_for_" in row["package_preflight_status"]
        )
        blocked = len(rows) - ready - waiting
        if ready and ready == len(rows):
            readiness = "ready_for_downstream_consumer"
        elif blocked:
            readiness = "blocked_by_preflight_repair"
        elif waiting:
            readiness = "waiting_for_external_package"
        else:
            readiness = "not_available"
        groups.append(
            {
                "group_id": group_id,
                "purpose": purpose,
                "candidate_ids": [row["candidate_id"] for row in rows],
                "source_env_vars": [row["source_env_var"] for row in rows],
                "ready_count": ready,
                "waiting_count": waiting,
                "blocked_count": blocked,
                "readiness_status": readiness,
                "next_operator_actions": [row["next_operator_action"] for row in rows],
            }
        )
    return groups


def _dict(value: object) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list_of_dicts(value: object) -> list[dict[str, Any]]:
    return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []


def _list_of_strings(value: object) -> list[str]:
    return [str(item) for item in value if item not in (None, "")] if isinstance(value, list) else []


def _safe_ratio(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return round(numerator / denominator, 3)


def _safe_int(value: object) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def _present(value: object) -> bool:
    if isinstance(value, bool):
        return True
    if isinstance(value, (list, dict)):
        return bool(value)
    return value not in (None, "")

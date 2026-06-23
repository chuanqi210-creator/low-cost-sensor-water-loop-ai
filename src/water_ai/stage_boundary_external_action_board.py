from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


BOARD_ID = "R8u139_stage_boundary_external_action_board"


def build_stage_boundary_external_action_board(
    *,
    core_gate: dict[str, Any],
    external_activation_operator_action_packet: dict[str, Any],
    formal_search_nonlegal_review_operator_packet: dict[str, Any],
    focused_catalyst_response_merge_metrics: dict[str, Any] | None = None,
    new_core_interface_candidate_gate: dict[str, Any] | None = None,
    claim_basis_promotion_gate: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build the stage-boundary external action board from already-verified gates."""

    action_rows = _action_rows(
        core_gate=core_gate,
        external_activation_operator_action_packet=external_activation_operator_action_packet,
        formal_search_nonlegal_review_operator_packet=formal_search_nonlegal_review_operator_packet,
        focused_catalyst_response_merge_metrics=focused_catalyst_response_merge_metrics or {},
        new_core_interface_candidate_gate=new_core_interface_candidate_gate or {},
        external_package_acquisition_stage_gate=_dict(
            core_gate.get("external_package_acquisition_stage_gate")
        ),
    )
    new_core_summary = _dict((new_core_interface_candidate_gate or {}).get("candidate_summary"))
    new_core_metadata = _dict((new_core_interface_candidate_gate or {}).get("gate_metadata"))
    model_chain_ready_count = sum(
        1 for row in action_rows if row["current_model_chain_resume_ready"] is True
    )
    handoff_ready_count = sum(1 for row in action_rows if row["current_handoff_ready"] is True)
    external_wait_count = sum(1 for row in action_rows if row["requires_external_input"] is True)
    status = _board_status(
        core_gate=core_gate,
        model_chain_ready_count=model_chain_ready_count,
        external_wait_count=external_wait_count,
    )
    machine_handoff = _machine_handoff(
        core_gate=core_gate,
        action_rows=action_rows,
        board_status=status,
    )
    stage_boundary = {
        "internal_expansion_allowed": bool(core_gate.get("continue_expansion_allowed", False)),
        "core_score": core_gate.get("core_score"),
        "previous_core_score": core_gate.get("previous_core_score"),
        "iteration_delta": core_gate.get("iteration_delta"),
        "iteration_validity_status": core_gate.get("iteration_validity_status", ""),
        "stage_decision": core_gate.get("stage_decision", ""),
        "next_gate_action": core_gate.get("next_gate_action", ""),
    }
    machine_handoff_contract_gate = _machine_handoff_contract_gate(machine_handoff)
    resource_boundary = _resource_boundary(machine_handoff)
    resource_boundary_gate = _resource_boundary_gate(resource_boundary, machine_handoff)
    subagent_orchestration_probe = _subagent_orchestration_probe(machine_handoff)
    claim_basis_promotion_snapshot = _claim_basis_promotion_snapshot(
        claim_basis_promotion_gate or {}
    )
    low_friction_round_gate = _low_friction_round_gate(
        stage_boundary=stage_boundary,
        action_rows=action_rows,
        machine_handoff=machine_handoff,
        machine_handoff_contract_gate=machine_handoff_contract_gate,
        resource_boundary_gate=resource_boundary_gate,
    )
    internal_expansion_saturation_gate = _internal_expansion_saturation_gate(
        stage_boundary=stage_boundary,
        action_rows=action_rows,
        machine_handoff=machine_handoff,
        machine_handoff_contract_gate=machine_handoff_contract_gate,
        resource_boundary_gate=resource_boundary_gate,
        low_friction_round_gate=low_friction_round_gate,
        claim_basis_promotion_snapshot=claim_basis_promotion_snapshot,
    )
    return {
        "board_metadata": {
            "board_id": BOARD_ID,
            "board_status": status,
            "board_role": "stage_boundary_external_action_queue",
            "created_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            "source_core_gate_stage_decision": str(core_gate.get("stage_decision", "")),
            "source_core_gate_self_interrupt_verdict": str(
                core_gate.get("self_interrupt_verdict", "")
            ),
        },
        "stage_boundary": stage_boundary,
        "action_summary": {
            "action_count": len(action_rows),
            "external_wait_count": external_wait_count,
            "model_chain_resume_ready_count": model_chain_ready_count,
            "handoff_ready_count": handoff_ready_count,
            "highest_priority_action_id": action_rows[0]["action_id"] if action_rows else "",
            "highest_priority_source_env_var": action_rows[0]["source_env_var"] if action_rows else "",
            "highest_priority_next_operator_action": (
                action_rows[0]["next_operator_action"] if action_rows else ""
            ),
            "highest_priority_focused_candidate_availability_status": (
                action_rows[0].get("focused_candidate_availability_status", "")
                if action_rows
                else ""
            ),
            "highest_priority_focused_candidate_submit_ready": (
                action_rows[0].get("focused_candidate_submit_ready", False)
                if action_rows
                else False
            ),
            "highest_priority_focused_candidate_operator_packet_submit_ready": (
                action_rows[0].get("focused_candidate_operator_packet_submit_ready", False)
                if action_rows
                else False
            ),
            "new_core_interface_candidate_gate_status": str(
                new_core_metadata.get("gate_status", "")
            ),
            "new_core_interface_highest_priority_candidate_id": str(
                new_core_summary.get("highest_priority_candidate_id", "")
            ),
            "new_core_interface_highest_priority_source_env_var": str(
                new_core_summary.get("highest_priority_source_env_var", "")
            ),
            "new_core_interface_highest_priority_preflight_status": str(
                new_core_summary.get("highest_priority_preflight_status", "")
            ),
            "new_core_interface_highest_priority_preflight_pass": bool(
                new_core_summary.get("highest_priority_preflight_pass", False)
            ),
            "new_core_interface_highest_priority_downstream_calibration_status": str(
                new_core_summary.get("highest_priority_downstream_calibration_status", "")
            ),
            "new_core_interface_highest_priority_can_route_to_downstream_interface": bool(
                new_core_summary.get("highest_priority_can_route_to_downstream_interface", False)
            ),
            "new_core_interface_highest_priority_downstream_interface_status": str(
                new_core_summary.get("highest_priority_downstream_interface_status", "")
            ),
            "new_core_interface_highest_priority_can_run_agent53_field_calibration": bool(
                new_core_summary.get("highest_priority_can_run_agent53_field_calibration", False)
            ),
            "new_core_interface_highest_priority_agent53_field_candidate_ready": bool(
                new_core_summary.get("highest_priority_agent53_field_candidate_ready", False)
            ),
            **_new_core_acquisition_summary(action_rows),
        },
        "action_rows": action_rows,
        "operator_runbook": _operator_runbook(action_rows),
        "machine_handoff": machine_handoff,
        "machine_handoff_contract_gate": machine_handoff_contract_gate,
        "resource_boundary": resource_boundary,
        "resource_boundary_gate": resource_boundary_gate,
        "low_friction_round_gate": low_friction_round_gate,
        "internal_expansion_saturation_gate": internal_expansion_saturation_gate,
        "subagent_orchestration_probe": subagent_orchestration_probe,
        "claim_basis_promotion_snapshot": claim_basis_promotion_snapshot,
        "boundary": {
            "can_generate_field_evidence": False,
            "can_resume_model_chain_without_external_gate": False,
            "can_generate_prior_art_result": False,
            "legal_opinion_allowed": False,
            "field_claim_upgrade_allowed": False,
            "can_emit_claim_text": False,
            "can_write_to_actuator": False,
            "can_write_to_release_gate": False,
            "boundary_statement": (
                "This board only orders already-defined external actions at a stage boundary. "
                "It does not create evidence, legal conclusions, claim text, field validation, "
                "actuator commands or release authorization."
            ),
        },
    }


def stage_boundary_external_action_board_report_md(board: dict[str, Any]) -> str:
    """Render the operator board as a compact human-readable stage-boundary report."""

    metadata = board["board_metadata"]
    stage = board["stage_boundary"]
    summary = board["action_summary"]
    handoff = _dict(board.get("machine_handoff"))
    handoff_gate = _dict(board.get("machine_handoff_contract_gate"))
    resource_boundary = _dict(board.get("resource_boundary"))
    resource_boundary_gate = _dict(board.get("resource_boundary_gate"))
    low_friction_gate = _dict(board.get("low_friction_round_gate"))
    saturation_gate = _dict(board.get("internal_expansion_saturation_gate"))
    claim_basis_promotion_snapshot = _dict(board.get("claim_basis_promotion_snapshot"))
    subagent_probe = _dict(board.get("subagent_orchestration_probe"))
    capability_probe = _dict(subagent_probe.get("capability_probe"))
    lifecycle_cleanup = _dict(subagent_probe.get("lifecycle_cleanup"))
    lines = [
        "# Stage Boundary External Action Board",
        "",
        "## Position",
        "",
        (
            "This board is the stage-boundary operator queue. It does not add internal "
            "model complexity; it orders the external inputs that can move the system after "
            "Agent50 has stopped synthetic/template expansion."
        ),
        "",
        "## Board State",
        "",
        f"- board_id: `{metadata['board_id']}`",
        f"- board_status: `{metadata['board_status']}`",
        f"- stage_decision: `{stage['stage_decision']}`",
        f"- internal_expansion_allowed: `{stage['internal_expansion_allowed']}`",
        f"- core_score: `{stage['core_score']}`",
        f"- previous_core_score: `{stage['previous_core_score']}`",
        f"- iteration_delta: `{stage['iteration_delta']}`",
        f"- action_count: `{summary['action_count']}`",
        f"- external_wait_count: `{summary['external_wait_count']}`",
        f"- model_chain_resume_ready_count: `{summary['model_chain_resume_ready_count']}`",
        f"- handoff_ready_count: `{summary['handoff_ready_count']}`",
        f"- highest_priority_source_env_var: `{summary['highest_priority_source_env_var']}`",
        (
            "- highest_priority_focused_candidate_availability_status: "
            f"`{summary['highest_priority_focused_candidate_availability_status']}`"
        ),
        (
            "- highest_priority_focused_candidate_operator_packet_submit_ready: "
            f"`{summary['highest_priority_focused_candidate_operator_packet_submit_ready']}`"
        ),
        (
            "- highest_priority_focused_candidate_submit_ready: "
            f"`{summary['highest_priority_focused_candidate_submit_ready']}`"
        ),
        (
            "- new_core_interface_candidate_gate_status: "
            f"`{summary.get('new_core_interface_candidate_gate_status', '')}`"
        ),
        (
            "- new_core_interface_highest_priority_candidate_id: "
            f"`{summary.get('new_core_interface_highest_priority_candidate_id', '')}`"
        ),
        (
            "- new_core_interface_highest_priority_source_env_var: "
            f"`{summary.get('new_core_interface_highest_priority_source_env_var', '')}`"
        ),
        (
            "- new_core_interface_highest_priority_preflight_status: "
            f"`{summary.get('new_core_interface_highest_priority_preflight_status', '')}`"
        ),
        (
            "- new_core_interface_highest_priority_preflight_pass: "
            f"`{summary.get('new_core_interface_highest_priority_preflight_pass', False)}`"
        ),
        (
            "- new_core_interface_highest_priority_downstream_calibration_status: "
            f"`{summary.get('new_core_interface_highest_priority_downstream_calibration_status', '')}`"
        ),
        (
            "- new_core_interface_highest_priority_can_route_to_downstream_interface: "
            f"`{summary.get('new_core_interface_highest_priority_can_route_to_downstream_interface', False)}`"
        ),
        (
            "- new_core_interface_highest_priority_downstream_interface_status: "
            f"`{summary.get('new_core_interface_highest_priority_downstream_interface_status', '')}`"
        ),
        (
            "- new_core_interface_highest_priority_can_run_agent53_field_calibration: "
            f"`{summary.get('new_core_interface_highest_priority_can_run_agent53_field_calibration', False)}`"
        ),
        (
            "- new_core_interface_highest_priority_agent53_field_candidate_ready: "
            f"`{summary.get('new_core_interface_highest_priority_agent53_field_candidate_ready', False)}`"
        ),
        (
            "- new_core_interface_acquisition_contract_termination_status: "
            f"`{summary.get('new_core_interface_acquisition_contract_termination_status', '')}`"
        ),
        (
            "- new_core_interface_acquisition_module_stage_termination_pass: "
            f"`{summary.get('new_core_interface_acquisition_module_stage_termination_pass', False)}`"
        ),
        (
            "- new_core_interface_acquisition_termination_blockers: "
            f"`{summary.get('new_core_interface_acquisition_termination_blockers', [])}`"
        ),
        "",
        "## Machine Handoff",
        "",
        f"- handoff_id: `{handoff.get('handoff_id', '')}`",
        f"- current_stage: `{handoff.get('current_stage', '')}`",
        f"- route_event: `{handoff.get('route_event', '')}`",
        f"- route_reason: `{handoff.get('route_reason', '')}`",
        f"- next_route: `{handoff.get('next_route', '')}`",
        f"- next_route_source_env_var: `{handoff.get('next_route_source_env_var', '')}`",
        f"- next_route_validation_command: `{handoff.get('next_route_validation_command', '')}`",
        f"- current_basis_refs: `{handoff.get('current_basis_refs', [])}`",
        f"- not_current_basis_refs: `{handoff.get('not_current_basis_refs', [])}`",
        f"- manual_action_required: `{handoff.get('manual_action_required', {})}`",
        f"- can_prove: `{handoff.get('can_prove', [])}`",
        f"- cannot_prove: `{handoff.get('cannot_prove', [])}`",
        f"- no_write_boundary_preserved: `{handoff.get('no_write_boundary_preserved', False)}`",
        f"- machine_handoff_contract_gate_status: `{handoff_gate.get('gate_status', '')}`",
        f"- machine_handoff_contract_score: `{handoff_gate.get('contract_score', 0.0)}`",
        f"- machine_handoff_contract_stage_pass: `{handoff_gate.get('contract_stage_pass', False)}`",
        f"- machine_handoff_contract_blockers: `{handoff_gate.get('contract_blockers', [])}`",
        f"- machine_handoff_external_wait_blockers: `{handoff_gate.get('external_wait_blockers', [])}`",
        "",
        "## Resource Boundary",
        "",
        f"- boundary_id: `{resource_boundary.get('boundary_id', '')}`",
        f"- allowed_basis: `{resource_boundary.get('allowed_basis', [])}`",
        f"- forbidden_basis: `{resource_boundary.get('forbidden_basis', [])}`",
        (
            "- official_supplementary_basis: "
            f"`{resource_boundary.get('official_supplementary_basis', [])}`"
        ),
        f"- gray_zone: `{resource_boundary.get('gray_zone', [])}`",
        f"- boundary_reason: `{resource_boundary.get('boundary_reason', '')}`",
        (
            "- resource_boundary_gate_status: "
            f"`{resource_boundary_gate.get('gate_status', '')}`"
        ),
        (
            "- resource_boundary_score: "
            f"`{resource_boundary_gate.get('resource_boundary_score', 0.0)}`"
        ),
        (
            "- resource_boundary_stage_pass: "
            f"`{resource_boundary_gate.get('resource_boundary_stage_pass', False)}`"
        ),
        (
            "- resource_boundary_blockers: "
            f"`{resource_boundary_gate.get('resource_boundary_blockers', [])}`"
        ),
        (
            "- resource_boundary_external_wait_blockers: "
            f"`{resource_boundary_gate.get('external_wait_blockers', [])}`"
        ),
        "",
        "## Low Friction Round Gate",
        "",
        (
            "- low_friction_round_gate_status: "
            f"`{low_friction_gate.get('gate_status', '')}`"
        ),
        f"- round_score: `{low_friction_gate.get('round_score', 0.0)}`",
        (
            "- selected_action_id: "
            f"`{low_friction_gate.get('selected_action_id', '')}`"
        ),
        (
            "- selected_canonical_action_id: "
            f"`{low_friction_gate.get('selected_canonical_action_id', '')}`"
        ),
        (
            "- selected_underlying_action_id: "
            f"`{low_friction_gate.get('selected_underlying_action_id', '')}`"
        ),
        (
            "- selected_source_env_var: "
            f"`{low_friction_gate.get('selected_source_env_var', '')}`"
        ),
        (
            "- user_burden_shifted: "
            f"`{low_friction_gate.get('user_burden_shifted', False)}`"
        ),
        (
            "- machine_writeback_required: "
            f"`{low_friction_gate.get('machine_writeback_required', False)}`"
        ),
        (
            "- low_friction_blockers: "
            f"`{low_friction_gate.get('blockers', [])}`"
        ),
        (
            "- evidence_level: "
            f"`{low_friction_gate.get('evidence_level', '')}`"
        ),
        "",
        "## Internal Expansion Saturation Gate",
        "",
        (
            "- internal_expansion_saturation_gate_status: "
            f"`{saturation_gate.get('gate_status', '')}`"
        ),
        f"- decision: `{saturation_gate.get('decision', '')}`",
        (
            "- required_next_external_input: "
            f"`{saturation_gate.get('required_next_external_input', '')}`"
        ),
        (
            "- required_validation_command: "
            f"`{saturation_gate.get('required_validation_command', '')}`"
        ),
        (
            "- micro_tweak_expansion_allowed: "
            f"`{saturation_gate.get('micro_tweak_expansion_allowed', False)}`"
        ),
        f"- stop_reasons: `{saturation_gate.get('stop_reasons', [])}`",
        f"- resume_conditions: `{saturation_gate.get('resume_conditions', [])}`",
        f"- allowed_internal_work: `{saturation_gate.get('allowed_internal_work', [])}`",
        f"- disallowed_internal_work: `{saturation_gate.get('disallowed_internal_work', [])}`",
        (
            "- claim_readiness_ceiling: "
            f"`{saturation_gate.get('claim_readiness_ceiling', '')}`"
        ),
        "",
        "## Claim Basis Promotion Snapshot",
        "",
        (
            "- claim_basis_promotion_snapshot_status: "
            f"`{claim_basis_promotion_snapshot.get('snapshot_status', '')}`"
        ),
        (
            "- promotion_decision_count: "
            f"`{claim_basis_promotion_snapshot.get('promotion_decision_count', 0)}`"
        ),
        (
            "- ready_promotion_count: "
            f"`{claim_basis_promotion_snapshot.get('ready_promotion_count', 0)}`"
        ),
        (
            "- blocked_promotion_count: "
            f"`{claim_basis_promotion_snapshot.get('blocked_promotion_count', 0)}`"
        ),
        (
            "- can_emit_field_claim_upgrade: "
            f"`{claim_basis_promotion_snapshot.get('can_emit_field_claim_upgrade', False)}`"
        ),
        (
            "- stage_boundary_effect: "
            f"`{claim_basis_promotion_snapshot.get('stage_boundary_effect', '')}`"
        ),
        "",
        "## Subagent Orchestration Probe",
        "",
        (
            "- subagent_orchestration_probe_status: "
            f"`{subagent_probe.get('probe_status', '')}`"
        ),
        f"- capability: `{subagent_probe.get('capability', '')}`",
        f"- strategy: `{subagent_probe.get('strategy', '')}`",
        f"- no_spawn_reason: `{subagent_probe.get('no_spawn_reason', '')}`",
        f"- tool_discovered: `{capability_probe.get('tool_discovered', False)}`",
        f"- spawn_attempted: `{capability_probe.get('spawn_attempted', False)}`",
        f"- wait_status: `{capability_probe.get('wait_status', '')}`",
        f"- integration_decision: `{capability_probe.get('integration_decision', '')}`",
        f"- close_attempted: `{lifecycle_cleanup.get('close_attempted', False)}`",
        f"- close_status: `{lifecycle_cleanup.get('close_status', '')}`",
        (
            "- open_agent_cleanup_required: "
            f"`{lifecycle_cleanup.get('open_agent_cleanup_required', False)}`"
        ),
        f"- roles: `{subagent_probe.get('roles', [])}`",
        f"- manual_proxy_needed: `{subagent_probe.get('manual_proxy_needed', False)}`",
        (
            "- can_delegate_goal_completion: "
            f"`{subagent_probe.get('can_delegate_goal_completion', False)}`"
        ),
        (
            "- can_generate_field_evidence: "
            f"`{subagent_probe.get('can_generate_field_evidence', False)}`"
        ),
        "",
        "## Action Rows",
        "",
        (
            "| priority | channel | class | env var | rows | candidate status | "
            "operator packet ready | submit ready | handoff ready | model resume ready | next action |"
        ),
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in board["action_rows"]:
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` |".format(
                row["priority_order"],
                row["channel_id"],
                row["activation_route_class"],
                row["source_env_var"],
                row["expected_input_row_count"],
                row.get("focused_candidate_availability_status", ""),
                row.get("focused_candidate_operator_packet_submit_ready", ""),
                row.get("focused_candidate_submit_ready", ""),
                row["current_handoff_ready"],
                row["current_model_chain_resume_ready"],
                row["next_operator_action"],
            )
        )
    for row in board["action_rows"]:
        if row["channel_id"] != "NEW_CORE_INTERFACE":
            continue
        candidate_id = row.get("new_core_interface_highest_priority_candidate_id", "")
        if not candidate_id:
            break
        lines.extend(
            [
                "",
                "## New Core Interface Candidate",
                "",
                f"- candidate_id: `{candidate_id}`",
                (
                    "- source_env_var: "
                    f"`{row.get('new_core_interface_highest_priority_source_env_var', '')}`"
                ),
                    (
                        "- validation_command: "
                        f"`{row.get('new_core_interface_highest_priority_validation_command', '')}`"
                    ),
                    (
                        "- preflight_status: "
                        f"`{row.get('new_core_interface_highest_priority_preflight_status', '')}`"
                    ),
                    (
                        "- preflight_pass: "
                        f"`{row.get('new_core_interface_highest_priority_preflight_pass', False)}`"
                    ),
                    (
                        "- downstream_calibration_status: "
                        f"`{row.get('new_core_interface_highest_priority_downstream_calibration_status', '')}`"
                    ),
                    (
                        "- can_route_to_downstream_interface: "
                        f"`{row.get('new_core_interface_highest_priority_can_route_to_downstream_interface', False)}`"
                    ),
                    (
                        "- downstream_interface_status: "
                        f"`{row.get('new_core_interface_highest_priority_downstream_interface_status', '')}`"
                    ),
                    (
                        "- can_run_agent53_field_calibration: "
                        f"`{row.get('new_core_interface_highest_priority_can_run_agent53_field_calibration', False)}`"
                    ),
                    (
                        "- agent53_field_candidate_ready: "
                        f"`{row.get('new_core_interface_highest_priority_agent53_field_candidate_ready', False)}`"
                    ),
                    (
                        "- next_interface_action: "
                        f"`{row.get('new_core_interface_highest_priority_next_interface_action', '')}`"
                ),
                (
                    "- acquisition_contract_termination_status: "
                    f"`{row.get('new_core_interface_acquisition_contract_termination_status', '')}`"
                ),
                (
                    "- acquisition_module_stage_termination_pass: "
                    f"`{row.get('new_core_interface_acquisition_module_stage_termination_pass', False)}`"
                ),
                (
                    "- acquisition_termination_blockers: "
                    f"`{row.get('new_core_interface_acquisition_termination_blockers', [])}`"
                ),
                (
                    "- failure_boundary: "
                    f"{row.get('new_core_interface_highest_priority_failure_boundary', '')}"
                ),
            ]
        )
        break
    lines.extend(
        [
            "",
            "## Operator Runbook",
            "",
            "| order | channel | source env var | validation command |",
            "| --- | --- | --- | --- |",
        ]
    )
    for step in board["operator_runbook"]:
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` |".format(
                step["order"],
                step["channel_id"],
                step["source_env_var"],
                step["validation_command"],
            )
        )
    lines.extend(["", "## Boundary", ""])
    boundary = board["boundary"]
    for key in [
        "can_generate_field_evidence",
        "can_resume_model_chain_without_external_gate",
        "can_generate_prior_art_result",
        "legal_opinion_allowed",
        "field_claim_upgrade_allowed",
        "can_emit_claim_text",
        "can_write_to_actuator",
        "can_write_to_release_gate",
    ]:
        lines.append(f"- {key}: `{boundary[key]}`")
    lines.extend(["", boundary["boundary_statement"], ""])
    return "\n".join(lines)


def _action_rows(
    *,
    core_gate: dict[str, Any],
    external_activation_operator_action_packet: dict[str, Any],
    formal_search_nonlegal_review_operator_packet: dict[str, Any],
    focused_catalyst_response_merge_metrics: dict[str, Any],
    new_core_interface_candidate_gate: dict[str, Any],
    external_package_acquisition_stage_gate: dict[str, Any],
) -> list[dict[str, Any]]:
    raw_rows = [
        row
        for row in core_gate.get("next_allowed_actions", [])
        if isinstance(row, dict)
    ]
    rows = [
        _action_row(
            row,
            external_activation_operator_action_packet=external_activation_operator_action_packet,
            formal_search_nonlegal_review_operator_packet=formal_search_nonlegal_review_operator_packet,
            focused_catalyst_response_merge_metrics=focused_catalyst_response_merge_metrics,
            new_core_interface_candidate_gate=new_core_interface_candidate_gate,
            external_package_acquisition_stage_gate=external_package_acquisition_stage_gate,
        )
        for row in raw_rows
    ]
    return sorted(rows, key=lambda row: (row["priority_order"], row["action_id"]))


def _action_row(
    action: dict[str, Any],
    *,
    external_activation_operator_action_packet: dict[str, Any],
    formal_search_nonlegal_review_operator_packet: dict[str, Any],
    focused_catalyst_response_merge_metrics: dict[str, Any],
    new_core_interface_candidate_gate: dict[str, Any],
    external_package_acquisition_stage_gate: dict[str, Any],
) -> dict[str, Any]:
    channel_id = str(action.get("channel_id", "unknown_channel"))
    priority_order = _priority_order(channel_id)
    source_env_var = str(action.get("package_pointer") or "")
    expected_input_row_count = 0
    linked_packet_status = ""
    target_hidden_state = ""
    validation_command = str(action.get("router_validation_command") or "")
    input_template_path = ""
    schema_path = ""
    merge_plan_path = ""
    command_sequence: list[str] = []
    rejection_boundaries: list[str] = []
    boundary_checks: list[dict[str, Any]] = []
    action_no_write_boundary = ""
    focused_candidate_context: dict[str, Any] = {}
    new_core_context: dict[str, Any] = {}
    if channel_id == "R7_REAL_FIELD_PACKAGE":
        source_env_var = str(
            external_activation_operator_action_packet.get(
                "source_env_var",
                source_env_var,
            )
        )
        expected_input_row_count = _safe_int(
            external_activation_operator_action_packet.get(
                "expected_focused_response_row_count",
                0,
            )
        )
        linked_packet_status = str(
            external_activation_operator_action_packet.get("packet_status", "")
        )
        target_hidden_state = str(
            external_activation_operator_action_packet.get("target_hidden_state", "")
        )
        validation_command = _python_experiment_command(
            str(
                external_activation_operator_action_packet.get(
                    "focused_merge_runner",
                    "experiments/run_focused_catalyst_response_merge.py",
                )
            )
        )
        input_template_path = str(
            external_activation_operator_action_packet.get("focused_template_path", "")
        )
        schema_path = str(
            external_activation_operator_action_packet.get("focused_schema_path", "")
        )
        merge_plan_path = str(
            external_activation_operator_action_packet.get("focused_merge_plan_path", "")
        )
        command_sequence = _string_list(
            external_activation_operator_action_packet.get("current_commands")
        )
        rejection_boundaries = _string_list(
            external_activation_operator_action_packet.get("rejection_boundaries")
        )
        boundary_checks = _list_of_dicts(
            external_activation_operator_action_packet.get("boundary_checks")
        )
        action_no_write_boundary = str(
            external_activation_operator_action_packet.get("no_write_boundary", "")
        )
        focused_candidate_context = _focused_candidate_context(
            focused_catalyst_response_merge_metrics,
            external_activation_operator_action_packet,
        )
    elif channel_id == "R8U79_FORMAL_SEARCH_RESULT_PACKAGE":
        source_env_var = str(
            action.get(
                "formal_nonlegal_review_operator_packet_source_env_var",
                _dict(formal_search_nonlegal_review_operator_packet.get("operator_action")).get(
                    "source_env_var",
                    "FORMAL_SEARCH_NONLEGAL_REVIEW_RESPONSE_PATH",
                ),
            )
        )
        expected_input_row_count = _safe_int(
            action.get(
                "formal_nonlegal_review_operator_packet_expected_review_packet_row_count",
                _dict(formal_search_nonlegal_review_operator_packet.get("operator_action")).get(
                    "expected_review_packet_row_count",
                    0,
                ),
            )
        )
        linked_packet_status = str(
            action.get(
                "formal_nonlegal_review_operator_packet_status",
                _dict(formal_search_nonlegal_review_operator_packet.get("operator_packet_metadata")).get(
                    "packet_status",
                    "",
                ),
            )
        )
        validation_command = "experiments/run_agent60_agent_architecture_consolidation.py"
    elif channel_id == "R8U66_PATH_ENDPOINT_LABEL_PACKAGE":
        source_env_var = "FIELD_PATH_ENDPOINT_LABEL_PACKAGE_DIR"
    elif channel_id == "NEW_CORE_INTERFACE":
        new_core_context = _new_core_interface_context(new_core_interface_candidate_gate)
        new_core_context.update(
            _new_core_acquisition_context(external_package_acquisition_stage_gate)
        )
        source_env_var = (
            str(new_core_context.get("new_core_interface_highest_priority_source_env_var", ""))
            or "FIELD_ACTIVATION_RESPONSE_PATH_or_new_testable_interface"
        )
        validation_command = (
            str(new_core_context.get("new_core_interface_highest_priority_validation_command", ""))
            or validation_command
        )
    next_operator_action = _next_operator_action(
        action=action,
        channel_id=channel_id,
        external_activation_operator_action_packet=external_activation_operator_action_packet,
    )
    row = {
        "action_id": f"R8u139_{channel_id}",
        "channel_id": channel_id,
        "priority_order": priority_order,
        "activation_route_class": str(action.get("activation_route_class", "")),
        "model_chain_resume_candidate": bool(action.get("model_chain_resume_candidate", False)),
        "handoff_only": bool(action.get("handoff_only", False)),
        "requires_tested_interface": bool(action.get("requires_tested_interface", False)),
        "requires_external_input": channel_id != "NEW_CORE_INTERFACE",
        "current_route_ready": bool(action.get("current_route_ready", False)),
        "current_handoff_ready": bool(action.get("current_handoff_ready", False)),
        "current_model_chain_resume_ready": bool(
            action.get("current_model_chain_resume_ready", False)
        ),
        "source_env_var": source_env_var,
        "expected_input_row_count": expected_input_row_count,
        "target_hidden_state": target_hidden_state,
        "linked_operator_packet_status": linked_packet_status,
        "next_operator_action": next_operator_action,
        "validation_command": validation_command,
        "input_template_path": input_template_path,
        "schema_path": schema_path,
        "merge_plan_path": merge_plan_path,
        "command_sequence": command_sequence,
        "rejection_boundaries": rejection_boundaries,
        "boundary_checks": boundary_checks,
        "action_no_write_boundary": action_no_write_boundary,
        "can_resume_model_chain": bool(action.get("can_resume_model_chain", False)),
        "can_route_to_claim_scope_patch_draft": bool(
            action.get("formal_nonlegal_review_operator_packet_can_route_to_claim_scope_patch_draft",
                       False)
        ),
        "can_emit_claim_text": bool(
            action.get("formal_nonlegal_review_operator_packet_can_emit_claim_text", False)
        ),
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
        "boundary": str(action.get("boundary", "")),
    }
    if channel_id == "R7_REAL_FIELD_PACKAGE":
        row.update(focused_candidate_context)
    if channel_id == "NEW_CORE_INTERFACE":
        row.update(new_core_context)
    return row


def _next_operator_action(
    *,
    action: dict[str, Any],
    channel_id: str,
    external_activation_operator_action_packet: dict[str, Any],
) -> str:
    if channel_id == "R7_REAL_FIELD_PACKAGE":
        packet_action = str(
            external_activation_operator_action_packet.get("packet_next_operator_action", "")
        )
        if packet_action:
            return packet_action
    return str(action.get("next_operator_action") or action.get("router_operator_action") or "")


def _focused_candidate_context(
    metrics: dict[str, Any],
    external_activation_operator_action_packet: dict[str, Any],
) -> dict[str, Any]:
    batch_alignment = _dict(metrics.get("batch_alignment"))
    self_declared_submit_ready = bool(
        metrics.get(
            "merged_full_response_candidate_self_declared_submit_ready",
            False,
        )
    )
    external_response_supplied = bool(
        metrics.get(
            "merged_full_response_candidate_external_response_supplied",
            False,
        )
    )
    can_submit_as_field_activation_response = bool(
        metrics.get(
            "can_submit_candidate_as_FIELD_ACTIVATION_RESPONSE_PATH",
            False,
        )
    )
    row_preflight_pass = bool(metrics.get("row_preflight_pass", False))
    packet_ready_value = external_activation_operator_action_packet.get(
        "focused_candidate_operator_packet_submit_ready"
    )
    if packet_ready_value is None:
        operator_packet_submit_ready = (
            self_declared_submit_ready
            and external_response_supplied
            and can_submit_as_field_activation_response
            and row_preflight_pass
        )
    else:
        operator_packet_submit_ready = bool(packet_ready_value)
    canonical_submit_ready = (
        operator_packet_submit_ready
        and can_submit_as_field_activation_response
        and row_preflight_pass
    )
    return {
        "focused_merge_preflight_status": str(
            metrics.get(
                "preflight_status",
                "focused_catalyst_response_merge_not_available",
            )
        ),
        "focused_candidate_availability_status": str(
            metrics.get(
                "merged_full_response_candidate_availability_status",
                "candidate_availability_not_available",
            )
        ),
        "focused_candidate_self_declared_submit_ready": self_declared_submit_ready,
        "focused_candidate_external_response_supplied": external_response_supplied,
        "focused_candidate_can_submit_as_FIELD_ACTIVATION_RESPONSE_PATH": (
            can_submit_as_field_activation_response
        ),
        "focused_candidate_operator_packet_submit_ready": operator_packet_submit_ready,
        "focused_candidate_submit_ready": canonical_submit_ready,
        "focused_merge_row_preflight_pass": row_preflight_pass,
        "focused_merge_matched_batch_count": _safe_int(
            batch_alignment.get("matched_batch_count", 0)
        ),
        "focused_merge_minimum_matched_batch_count": _safe_int(
            batch_alignment.get("minimum_matched_batch_count", 0)
        ),
        "focused_candidate_use_boundary": str(
            metrics.get("merged_full_response_candidate_use_boundary", "")
        ),
    }


def _operator_runbook(action_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    runbook: list[dict[str, Any]] = []
    for row in action_rows:
        runbook.append(
            {
                "step_id": f"RUN_{row['priority_order']}_{row['channel_id']}",
                "order": row["priority_order"],
                "channel_id": row["channel_id"],
                "source_env_var": row["source_env_var"],
                "expected_input_row_count": row["expected_input_row_count"],
                "focused_candidate_availability_status": row.get(
                    "focused_candidate_availability_status",
                    "",
                ),
                "focused_candidate_self_declared_submit_ready": row.get(
                    "focused_candidate_self_declared_submit_ready",
                    False,
                ),
                "focused_candidate_operator_packet_submit_ready": row.get(
                    "focused_candidate_operator_packet_submit_ready",
                    False,
                ),
                "focused_candidate_submit_ready": row.get(
                    "focused_candidate_submit_ready",
                    False,
                ),
                "next_operator_action": row["next_operator_action"],
                "validation_command": row["validation_command"],
                "input_template_path": row.get("input_template_path", ""),
                "schema_path": row.get("schema_path", ""),
                "command_sequence": list(row.get("command_sequence", []))
                if isinstance(row.get("command_sequence", []), list)
                else [],
                "rejection_boundaries": list(row.get("rejection_boundaries", []))
                if isinstance(row.get("rejection_boundaries", []), list)
                else [],
                "boundary_checks": list(row.get("boundary_checks", []))
                if isinstance(row.get("boundary_checks", []), list)
                else [],
                "action_no_write_boundary": row.get("action_no_write_boundary", ""),
                "new_core_interface_highest_priority_candidate_id": row.get(
                    "new_core_interface_highest_priority_candidate_id",
                    "",
                ),
                "new_core_interface_highest_priority_source_env_var": row.get(
                    "new_core_interface_highest_priority_source_env_var",
                    "",
                ),
                "new_core_interface_highest_priority_downstream_calibration_status": row.get(
                    "new_core_interface_highest_priority_downstream_calibration_status",
                    "",
                ),
                "new_core_interface_highest_priority_can_route_to_downstream_interface": row.get(
                    "new_core_interface_highest_priority_can_route_to_downstream_interface",
                    False,
                ),
                "new_core_interface_highest_priority_downstream_interface_status": row.get(
                    "new_core_interface_highest_priority_downstream_interface_status",
                    "",
                ),
                "new_core_interface_highest_priority_can_run_agent53_field_calibration": row.get(
                    "new_core_interface_highest_priority_can_run_agent53_field_calibration",
                    False,
                ),
                "new_core_interface_highest_priority_agent53_field_candidate_ready": row.get(
                    "new_core_interface_highest_priority_agent53_field_candidate_ready",
                    False,
                ),
                "new_core_interface_acquisition_contract_termination_status": row.get(
                    "new_core_interface_acquisition_contract_termination_status",
                    "",
                ),
                "new_core_interface_acquisition_module_stage_termination_pass": row.get(
                    "new_core_interface_acquisition_module_stage_termination_pass",
                    False,
                ),
                "new_core_interface_acquisition_downstream_reconnection_rate": row.get(
                    "new_core_interface_acquisition_downstream_reconnection_rate",
                    0.0,
                ),
                "new_core_interface_acquisition_field_package_ready_rate": row.get(
                    "new_core_interface_acquisition_field_package_ready_rate",
                    0.0,
                ),
                "new_core_interface_acquisition_termination_blockers": row.get(
                    "new_core_interface_acquisition_termination_blockers",
                    [],
                ),
                "new_core_interface_acquisition_next_stage_decision": row.get(
                    "new_core_interface_acquisition_next_stage_decision",
                    "",
                ),
                "new_core_interface_acquisition_next_operator_source_env_var": row.get(
                    "new_core_interface_acquisition_next_operator_source_env_var",
                    "",
                ),
                "must_not": [
                    "do_not_use_synthetic_template_rows_as_field_evidence",
                    "do_not_skip_preflight_replay_holdout_or_operator_review",
                    "do_not_write_actuator_or_release_gate_from_this_board",
                ],
            }
        )
    return runbook


def _machine_handoff(
    *,
    core_gate: dict[str, Any],
    action_rows: list[dict[str, Any]],
    board_status: str,
) -> dict[str, Any]:
    highest = action_rows[0] if action_rows else {}
    route_event = _machine_route_event(action_rows)
    manual_required = route_event == "external_activation_wait"
    can_resume_model_chain = any(
        row.get("current_model_chain_resume_ready") is True for row in action_rows
    )
    return {
        "handoff_id": "R8u169_stage_boundary_external_action_machine_handoff",
        "current_stage": "stage_boundary_external_activation",
        "stage_status": board_status,
        "route_event": route_event,
        "route_reason": _machine_route_reason(core_gate, route_event),
        "next_route": _machine_next_route(route_event),
        "next_route_source_env_var": str(highest.get("source_env_var", "")),
        "next_route_validation_command": str(highest.get("validation_command", "")),
        "manual_action_required": {
            "required": manual_required,
            "actor": "field_operator_or_user" if manual_required else "",
            "source_env_var": str(highest.get("source_env_var", "")) if manual_required else "",
            "action": str(highest.get("next_operator_action", "")) if manual_required else "",
            "validation_command": (
                str(highest.get("validation_command", "")) if manual_required else ""
            ),
            "input_template_path": (
                str(highest.get("input_template_path", "")) if manual_required else ""
            ),
            "schema_path": str(highest.get("schema_path", "")) if manual_required else "",
            "merge_plan_path": (
                str(highest.get("merge_plan_path", "")) if manual_required else ""
            ),
            "command_sequence": (
                list(highest.get("command_sequence", []))
                if manual_required and isinstance(highest.get("command_sequence", []), list)
                else []
            ),
            "rejection_boundaries": (
                list(highest.get("rejection_boundaries", []))
                if manual_required and isinstance(highest.get("rejection_boundaries", []), list)
                else []
            ),
            "boundary_checks": (
                list(highest.get("boundary_checks", []))
                if manual_required and isinstance(highest.get("boundary_checks", []), list)
                else []
            ),
            "no_write_boundary": (
                str(highest.get("action_no_write_boundary", "")) if manual_required else ""
            ),
            "resume_evidence": (
                "preflight JSON showing pass=true, or blocker fields showing the next repair"
                if manual_required
                else ""
            ),
        },
        "current_basis_refs": [
            "core_gate.stage_decision",
            "core_gate.next_allowed_actions",
            "external_activation_operator_action_packet",
            "focused_catalyst_response_merge_metrics",
            "formal_search_nonlegal_review_operator_packet",
            "new_core_interface_candidate_gate",
            "core_gate.external_package_acquisition_stage_gate",
        ],
        "not_current_basis_refs": [
            "synthetic_rows",
            "template_rows",
            "sample_rows",
            "literature_only_rows",
            "formal_search_handoff_as_field_evidence",
            "downstream_replay_holdout_calibration_not_run",
            "merged_candidate_when_submit_ready_false",
        ],
        "can_prove": [
            "which external action is currently highest priority",
            "which source env var and validation command to use next",
            "why internal expansion remains stopped at the stage boundary",
            "which no-write boundaries are preserved before downstream gates",
        ],
        "cannot_prove": [
            "field treatment performance",
            "field-supported mechanism validity",
            "model-chain resume readiness",
            "actuator or release-gate readiness",
            "legal or patentability conclusions",
        ],
        "can_generate_field_evidence": False,
        "can_resume_model_chain": can_resume_model_chain,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
        "no_write_boundary_preserved": True,
    }


def _machine_handoff_contract_gate(handoff: dict[str, Any]) -> dict[str, Any]:
    thresholds = {
        "route_contract_completeness": 1.0,
        "manual_action_contract_completeness": 1.0,
        "basis_boundary_completeness": 1.0,
        "proof_boundary_completeness": 1.0,
        "no_write_boundary_completeness": 1.0,
        "recovery_linkage_completeness": 1.0,
    }
    manual_action = _dict(handoff.get("manual_action_required"))
    scores = {
        "route_contract_completeness": _presence_score(
            handoff,
            [
                "current_stage",
                "stage_status",
                "route_event",
                "route_reason",
                "next_route",
                "next_route_source_env_var",
                "next_route_validation_command",
            ],
        ),
        "manual_action_contract_completeness": _manual_action_contract_completeness(
            manual_action
        ),
        "basis_boundary_completeness": _list_boundary_score(
            handoff,
            "current_basis_refs",
            "not_current_basis_refs",
        ),
        "proof_boundary_completeness": _list_boundary_score(
            handoff,
            "can_prove",
            "cannot_prove",
        ),
        "no_write_boundary_completeness": _no_write_boundary_score(handoff),
        "recovery_linkage_completeness": _presence_score(
            handoff,
            ["next_route", "next_route_source_env_var", "next_route_validation_command"],
        ),
    }
    contract_blockers = [
        f"{metric}_below_{threshold:.2f}"
        for metric, threshold in thresholds.items()
        if scores[metric] < threshold
    ]
    contract_stage_pass = not contract_blockers
    external_wait_blockers = (
        ["real_external_input_required"]
        if handoff.get("route_event") == "external_activation_wait"
        else []
    )
    contract_score = round(sum(scores.values()) / len(scores), 3)
    return {
        "gate_id": "R8u170_stage_boundary_machine_handoff_contract_gate",
        "gate_status": _machine_handoff_contract_gate_status(
            contract_stage_pass=contract_stage_pass,
            route_event=str(handoff.get("route_event", "")),
        ),
        "thresholds": thresholds,
        **scores,
        "contract_score": contract_score,
        "contract_stage_pass": contract_stage_pass,
        "contract_blockers": contract_blockers,
        "external_wait_blockers": external_wait_blockers,
        "can_generate_field_evidence": False,
        "can_resume_model_chain": bool(handoff.get("can_resume_model_chain", False)),
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
        "boundary_note": (
            "This gate scores whether the stage-boundary machine handoff is complete "
            "enough for low-friction recovery. It does not score field evidence, "
            "model-chain resume readiness, actuator readiness or release readiness."
        ),
    }


def _machine_handoff_contract_gate_status(
    *,
    contract_stage_pass: bool,
    route_event: str,
) -> str:
    if contract_stage_pass and route_event == "external_activation_wait":
        return "machine_handoff_contract_complete_waiting_for_external_input"
    if contract_stage_pass and route_event == "model_chain_resume_candidate_ready":
        return "machine_handoff_contract_complete_ready_for_downstream_review"
    if contract_stage_pass:
        return "machine_handoff_contract_complete_needs_stage_review"
    return "machine_handoff_contract_incomplete"


def _resource_boundary(handoff: dict[str, Any]) -> dict[str, Any]:
    manual_action = _dict(handoff.get("manual_action_required"))
    return {
        "boundary_id": "R8u171_stage_boundary_resource_boundary",
        "allowed_basis": [
            "verified_stage_boundary_gates",
            "machine_handoff_contract_gate",
            "operator_packets_after_schema_preflight",
            "real_external_packages_after_preflight_pass",
            "human_nonlegal_review_after_response_preflight",
        ],
        "forbidden_basis": [
            "template_rows_as_field_evidence",
            "synthetic_rows_as_field_evidence",
            "sample_rows_as_field_evidence",
            "literature_only_rows_as_field_evidence",
            "self_declared_candidate_without_preflight",
            "formal_search_handoff_as_legal_or_patent_opinion",
            "actuator_or_release_write_before_downstream_gates",
        ],
        "official_supplementary_basis": [
            "protocol_as_governance_pattern_not_domain_evidence",
            "template_directories_as_schema_guides_only",
            "literature_and_open_source_methods_as_method_priors_only",
        ],
        "gray_zone": [
            "external_package_supplied_but_not_preflighted",
            "human_review_response_supplied_but_not_schema_checked",
            "candidate_interface_ranked_but_not_downstream_reconnected",
        ],
        "boundary_reason": (
            "Preserve evidence provenance while waiting for real external field inputs; "
            "separate governance inspiration, schema templates and method priors from field evidence."
        ),
        "distribution_warning": (
            "Any external package may differ by site, matrix, sensor cadence, operator action "
            "and batch alignment until replay/holdout/calibration gates pass."
        ),
        "approved_access_or_permission": {
            "required_source_env_var": str(manual_action.get("source_env_var", "")),
            "validation_command": str(manual_action.get("validation_command", "")),
            "resume_evidence": str(manual_action.get("resume_evidence", "")),
        },
        "external_model_or_tool_policy": {
            "can_use_for_governance": True,
            "can_use_for_code_search": True,
            "can_use_for_method_prior": True,
            "can_emit_legal_or_patent_conclusion": False,
            "can_replace_field_validation": False,
            "policy_note": (
                "External tools and skills may organize evidence or suggest methods, but cannot "
                "upgrade synthetic/template/literature artifacts into field-supported claims."
            ),
        },
        "manual_annotation_or_human_labeling_policy": {
            "manual_action_required": bool(manual_action.get("required", False)),
            "accepted_after_preflight": True,
            "cannot_substitute_field_labels": True,
            "required_evidence_after_action": str(manual_action.get("resume_evidence", "")),
        },
        "no_write_policy": {
            "can_generate_field_evidence": False,
            "can_resume_model_chain": bool(handoff.get("can_resume_model_chain", False)),
            "can_write_to_actuator": False,
            "can_write_to_release_gate": False,
            "field_claim_upgrade_allowed": False,
        },
    }


def _subagent_orchestration_probe(handoff: dict[str, Any]) -> dict[str, Any]:
    return {
        "probe_id": "R8u175_stage_boundary_subagent_orchestration_probe",
        "probe_status": "subagent_orchestration_not_needed_for_external_wait",
        "capability": "not_needed",
        "strategy": "not_needed",
        "no_spawn_reason": (
            "current_stage_is_external_activation_wait_and_no_parallel_internal_task_is_required"
        ),
        "capability_probe": {
            "environment_listed": False,
            "tool_discovered": False,
            "discovery_method": "not_invoked_for_external_wait",
            "callable_tool": "",
            "spawn_attempted": False,
            "agent_ids": [],
            "wait_status": "not_started",
            "integration_decision": "not_needed",
            "integration_reason": (
                "external activation wait has no independent internal subagent task"
            ),
            "route_event": str(handoff.get("route_event", "")),
        },
        "lifecycle_cleanup": {
            "close_attempted": False,
            "closed_agent_ids": [],
            "close_status": "not_needed",
            "previous_status_summary": "",
            "repeated_close_result": "",
            "cleanup_decision": "no_subagents_opened_by_this_recovery_artifact",
            "open_agent_cleanup_required": False,
        },
        "roles": [],
        "manual_proxy_needed": False,
        "can_delegate_goal_completion": False,
        "can_generate_field_evidence": False,
    }


def _resource_boundary_gate(
    boundary: dict[str, Any],
    handoff: dict[str, Any],
) -> dict[str, Any]:
    thresholds = {
        "allowed_basis_completeness": 1.0,
        "forbidden_basis_completeness": 1.0,
        "supplementary_basis_completeness": 1.0,
        "gray_zone_completeness": 1.0,
        "tool_policy_completeness": 1.0,
        "manual_annotation_policy_completeness": 1.0,
        "no_write_policy_completeness": 1.0,
    }
    tool_policy = _dict(boundary.get("external_model_or_tool_policy"))
    manual_policy = _dict(boundary.get("manual_annotation_or_human_labeling_policy"))
    no_write_policy = _dict(boundary.get("no_write_policy"))
    scores = {
        "allowed_basis_completeness": _non_empty_list_score(boundary, "allowed_basis"),
        "forbidden_basis_completeness": _non_empty_list_score(boundary, "forbidden_basis"),
        "supplementary_basis_completeness": _non_empty_list_score(
            boundary,
            "official_supplementary_basis",
        ),
        "gray_zone_completeness": _non_empty_list_score(boundary, "gray_zone"),
        "tool_policy_completeness": _presence_score(
            tool_policy,
            [
                "can_use_for_governance",
                "can_use_for_code_search",
                "can_use_for_method_prior",
                "can_emit_legal_or_patent_conclusion",
                "can_replace_field_validation",
                "policy_note",
            ],
        ),
        "manual_annotation_policy_completeness": _presence_score(
            manual_policy,
            [
                "manual_action_required",
                "accepted_after_preflight",
                "cannot_substitute_field_labels",
                "required_evidence_after_action",
            ],
        ),
        "no_write_policy_completeness": _no_write_policy_score(no_write_policy),
    }
    blockers = [
        f"{metric}_below_{threshold:.2f}"
        for metric, threshold in thresholds.items()
        if scores[metric] < threshold
    ]
    stage_pass = not blockers
    external_wait_blockers = (
        ["real_external_input_required"]
        if handoff.get("route_event") == "external_activation_wait"
        else []
    )
    score = round(sum(scores.values()) / len(scores), 3)
    return {
        "gate_id": "R8u171_stage_boundary_resource_boundary_gate",
        "gate_status": _resource_boundary_gate_status(
            stage_pass=stage_pass,
            route_event=str(handoff.get("route_event", "")),
        ),
        "thresholds": thresholds,
        **scores,
        "resource_boundary_score": score,
        "resource_boundary_stage_pass": stage_pass,
        "resource_boundary_blockers": blockers,
        "external_wait_blockers": external_wait_blockers,
        "can_generate_field_evidence": False,
        "can_resume_model_chain": bool(no_write_policy.get("can_resume_model_chain", False)),
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
        "boundary_note": (
            "This gate scores whether allowed, forbidden, supplementary and gray-zone "
            "resources are explicit enough to prevent evidence leakage. It does not score "
            "field validation or downstream control readiness."
        ),
    }


def _claim_basis_promotion_snapshot(
    claim_basis_promotion_gate: dict[str, Any],
) -> dict[str, Any]:
    gate_status = str(
        claim_basis_promotion_gate.get(
            "gate_status", "claim_basis_promotion_gate_not_available"
        )
    )
    ready_count = int(claim_basis_promotion_gate.get("ready_promotion_count", 0) or 0)
    blocked_count = int(claim_basis_promotion_gate.get("blocked_promotion_count", 0) or 0)
    can_emit_field_claim_upgrade = bool(
        claim_basis_promotion_gate.get("can_emit_field_claim_upgrade", False)
    )
    return {
        "snapshot_id": "R8u179_stage_boundary_claim_basis_promotion_snapshot",
        "snapshot_status": gate_status,
        "evidence_level": "stage_boundary_snapshot_not_field_evidence",
        "promotion_decision_count": int(
            claim_basis_promotion_gate.get("promotion_decision_count", 0) or 0
        ),
        "ready_promotion_count": ready_count,
        "blocked_promotion_count": blocked_count,
        "can_emit_field_claim_upgrade": can_emit_field_claim_upgrade,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
        "stage_boundary_effect": (
            "field_supported_claim_candidate_ready_needs_human_review_and_separate_write_gates"
            if can_emit_field_claim_upgrade and blocked_count == 0 and ready_count > 0
            else "keep_external_wait_until_real_field_validation_and_human_review"
        ),
        "failure_boundary": str(
            claim_basis_promotion_gate.get(
                "failure_boundary",
                "Claim basis promotion status cannot create field evidence, actuator readiness or release readiness.",
            )
        ),
    }


def _resource_boundary_gate_status(
    *,
    stage_pass: bool,
    route_event: str,
) -> str:
    if stage_pass and route_event == "external_activation_wait":
        return "resource_boundary_complete_waiting_for_real_external_input"
    if stage_pass and route_event == "model_chain_resume_candidate_ready":
        return "resource_boundary_complete_ready_for_downstream_review"
    if stage_pass:
        return "resource_boundary_complete_needs_stage_review"
    return "resource_boundary_incomplete"


def _internal_expansion_saturation_gate(
    *,
    stage_boundary: dict[str, Any],
    action_rows: list[dict[str, Any]],
    machine_handoff: dict[str, Any],
    machine_handoff_contract_gate: dict[str, Any],
    resource_boundary_gate: dict[str, Any],
    low_friction_round_gate: dict[str, Any],
    claim_basis_promotion_snapshot: dict[str, Any],
) -> dict[str, Any]:
    highest = action_rows[0] if action_rows else {}
    route_event = str(machine_handoff.get("route_event", ""))
    stage_decision = str(stage_boundary.get("stage_decision", ""))
    iteration_delta = _safe_float(stage_boundary.get("iteration_delta"))
    delta_threshold = 0.05
    focused_candidate_submit_ready = bool(
        highest.get("focused_candidate_submit_ready", False)
    )
    stop_reasons: list[str] = []
    if abs(iteration_delta) < delta_threshold:
        stop_reasons.append("core_score_iteration_delta_below_0.05")
    if "wait" in stage_decision or route_event == "external_activation_wait":
        stop_reasons.append("stage_decision_waits_for_external_activation")
    if (
        low_friction_round_gate.get("selected_action_count") == 1
        and str(low_friction_round_gate.get("gate_status", ""))
        != "low_friction_round_gate_incomplete"
    ):
        stop_reasons.append("low_friction_gate_has_single_action")
    if (
        highest.get("source_env_var") == "FOCUSED_CATALYST_RESPONSE_PATH"
        and focused_candidate_submit_ready is False
    ):
        stop_reasons.append("focused_candidate_not_submittable_without_real_external_input")
    if machine_handoff_contract_gate.get("contract_stage_pass") is True:
        stop_reasons.append("machine_handoff_contract_complete")
    if resource_boundary_gate.get("resource_boundary_stage_pass") is True:
        stop_reasons.append("resource_boundary_complete")
    if (
        claim_basis_promotion_snapshot.get("snapshot_status")
        == "claim_basis_promotion_blocked_until_field_validation"
    ):
        stop_reasons.append("claim_basis_promotion_blocked_until_field_validation")

    required_next_external_input = str(machine_handoff.get("next_route_source_env_var", ""))
    required_validation_command = str(
        machine_handoff.get("next_route_validation_command", "")
    )
    internal_expansion_allowed = bool(
        stage_boundary.get("internal_expansion_allowed", False)
    )
    micro_tweak_expansion_allowed = not (
        route_event == "external_activation_wait"
        and internal_expansion_allowed is False
        and len(stop_reasons) >= 5
    )
    gate_score = 1.0 if micro_tweak_expansion_allowed is False else 0.0
    return {
        "gate_id": "R8u186_stage_boundary_internal_expansion_saturation_gate",
        "gate_status": _internal_expansion_saturation_gate_status(
            micro_tweak_expansion_allowed=micro_tweak_expansion_allowed,
            route_event=route_event,
        ),
        "source_protocol": (
            "complex_project_startup_governance_protocol_v3_core_selected_rules"
        ),
        "adopted_protocol_principles": [
            "anti_protocol_bloat_gate",
            "continuous_cycle_no_idle_expansion",
            "claim_readiness_ladder",
            "stage_handoff_route_back",
            "micro_task_execution_check",
        ],
        "model_core_boundary_layer": "verification_governance",
        "decision": (
            "stop_internal_micro_expansion_wait_for_real_external_input"
            if micro_tweak_expansion_allowed is False
            else "allow_internal_repair_or_downstream_review"
        ),
        "internal_expansion_allowed": internal_expansion_allowed,
        "micro_tweak_expansion_allowed": micro_tweak_expansion_allowed,
        "current_external_blocker": required_next_external_input,
        "required_next_external_input": required_next_external_input,
        "required_validation_command": required_validation_command,
        "iteration_delta": iteration_delta,
        "delta_threshold": delta_threshold,
        "gate_score": gate_score,
        "stop_reasons": stop_reasons,
        "resume_conditions": [
            "FOCUSED_CATALYST_RESPONSE_PATH_supplied_and_focused_merge_preflight_passed",
            "hard_boundary_contradiction_detected",
            "new_P1_or_P2_model_interface_blocker_identified",
        ],
        "allowed_internal_work": [
            "consume_real_external_input",
            "repair_hard_boundary_contradiction",
            "refresh_artifacts_after_external_input",
            "run_verification_without_expanding_model_logic",
        ],
        "disallowed_internal_work": [
            "add_more_operator_convenience_fields_without_new_boundary_gap",
            "create_additional_synthetic_template_outputs_as_progress",
            "spawn_subagents_for_external_wait_without_parallel_internal_domain",
            "promote_claims_or_control_without_field_package",
        ],
        "claim_readiness_ceiling": (
            "governance_contract_only_until_real_field_validation"
        ),
        "can_generate_field_evidence": False,
        "can_resume_model_chain": bool(machine_handoff.get("can_resume_model_chain", False)),
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
        "boundary_note": (
            "This protocol-adapted gate stops low-value internal expansion when the "
            "stage boundary is already recoverable and the remaining blocker is real "
            "external field input. It does not create evidence, claims, actuator "
            "commands or release authorization."
        ),
    }


def _internal_expansion_saturation_gate_status(
    *,
    micro_tweak_expansion_allowed: bool,
    route_event: str,
) -> str:
    if micro_tweak_expansion_allowed is False and route_event == "external_activation_wait":
        return "internal_expansion_saturated_waiting_for_external_input"
    if micro_tweak_expansion_allowed is False:
        return "internal_expansion_saturated_needs_stage_review"
    return "internal_expansion_repair_or_review_allowed"


def _low_friction_round_gate(
    *,
    stage_boundary: dict[str, Any],
    action_rows: list[dict[str, Any]],
    machine_handoff: dict[str, Any],
    machine_handoff_contract_gate: dict[str, Any],
    resource_boundary_gate: dict[str, Any],
) -> dict[str, Any]:
    highest = action_rows[0] if action_rows else {}
    manual_action = _dict(machine_handoff.get("manual_action_required"))
    selected_action_count = 1 if highest else 0
    user_burden_shifted = _manual_action_contract_completeness(manual_action) < 1.0
    machine_writeback_required = True
    termination_contract = {
        "continue_expansion_allowed": bool(stage_boundary.get("internal_expansion_allowed", False)),
        "stage_decision": str(stage_boundary.get("stage_decision", "")),
        "route_event": str(machine_handoff.get("route_event", "")),
        "next_route": str(machine_handoff.get("next_route", "")),
        "handoff_contract_stage_pass": bool(
            machine_handoff_contract_gate.get("contract_stage_pass", False)
        ),
        "resource_boundary_stage_pass": bool(
            resource_boundary_gate.get("resource_boundary_stage_pass", False)
        ),
    }
    scores = {
        "single_selected_action_score": 1.0
        if selected_action_count == 1 and _has_value(highest.get("action_id"))
        else 0.0,
        "manual_action_specificity_score": 1.0 if not user_burden_shifted else 0.0,
        "machine_writeback_score": 1.0
        if machine_writeback_required
        and _has_value(machine_handoff.get("next_route"))
        and _has_value(machine_handoff.get("next_route_validation_command"))
        else 0.0,
        "termination_contract_score": 1.0
        if termination_contract["continue_expansion_allowed"] is False
        and _has_value(termination_contract["route_event"])
        and _has_value(termination_contract["next_route"])
        else 0.0,
        "no_write_boundary_score": _no_write_boundary_score(machine_handoff),
    }
    blockers = [
        f"{metric}_below_1.00"
        for metric, score in scores.items()
        if score < 1.0
    ]
    round_score = round(sum(scores.values()) / len(scores), 3)
    route_event = str(machine_handoff.get("route_event", ""))
    return {
        "gate_id": "R8u177_low_friction_round_gate",
        "gate_status": _low_friction_round_gate_status(
            blockers=blockers,
            route_event=route_event,
        ),
        "evidence_level": "governance_contract_not_field_evidence",
        "thresholds": {key: 1.0 for key in scores},
        **scores,
        "round_score": round_score,
        "selected_action_count": selected_action_count,
        "selected_action_id": str(highest.get("action_id", "")),
        "selected_underlying_action_id": str(highest.get("action_id", "")),
        "selected_canonical_action_id": _canonical_low_friction_action_id(highest),
        "selected_source_env_var": str(highest.get("source_env_var", "")),
        "selected_next_operator_action": str(highest.get("next_operator_action", "")),
        "manual_action_required": manual_action,
        "user_burden_shifted": user_burden_shifted,
        "machine_writeback_required": machine_writeback_required,
        "termination_contract": termination_contract,
        "blockers": blockers,
        "can_generate_field_evidence": False,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
        "field_claim_upgrade_allowed": False,
        "boundary_note": (
            "This gate only verifies that one highest-leverage next action is recoverable "
            "with a concrete manual-action contract and machine writeback. It is not field "
            "evidence, control readiness or release authorization."
        ),
    }


def _low_friction_round_gate_status(*, blockers: list[str], route_event: str) -> str:
    if blockers:
        return "low_friction_round_gate_incomplete"
    if route_event == "external_activation_wait":
        return "low_friction_single_action_waiting_for_external_input"
    if route_event == "model_chain_resume_candidate_ready":
        return "low_friction_single_action_ready_for_downstream_review"
    return "low_friction_single_action_needs_stage_review"


def _non_empty_list_score(source: dict[str, Any], key: str) -> float:
    value = source.get(key, [])
    return 1.0 if isinstance(value, list) and len(value) > 0 else 0.0


def _no_write_policy_score(policy: dict[str, Any]) -> float:
    if (
        policy.get("can_generate_field_evidence") is False
        and policy.get("can_write_to_actuator") is False
        and policy.get("can_write_to_release_gate") is False
        and policy.get("field_claim_upgrade_allowed") is False
    ):
        return 1.0
    return 0.0


def _presence_score(source: dict[str, Any], fields: list[str]) -> float:
    if not fields:
        return 1.0
    present = sum(1 for field in fields if _has_value(source.get(field)))
    return round(present / len(fields), 3)


def _manual_action_contract_completeness(manual_action: dict[str, Any]) -> float:
    if manual_action.get("required") is not True:
        return 1.0
    return _presence_score(
        manual_action,
        ["actor", "source_env_var", "action", "validation_command", "resume_evidence"],
    )


def _list_boundary_score(source: dict[str, Any], positive_key: str, negative_key: str) -> float:
    positive = source.get(positive_key, [])
    negative = source.get(negative_key, [])
    positive_ready = isinstance(positive, list) and len(positive) > 0
    negative_ready = isinstance(negative, list) and len(negative) > 0
    return 1.0 if positive_ready and negative_ready else 0.0


def _no_write_boundary_score(handoff: dict[str, Any]) -> float:
    if (
        handoff.get("can_generate_field_evidence") is False
        and handoff.get("can_write_to_actuator") is False
        and handoff.get("can_write_to_release_gate") is False
        and handoff.get("no_write_boundary_preserved") is True
    ):
        return 1.0
    return 0.0


def _has_value(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, dict, tuple, set)):
        return len(value) > 0
    return True


def _machine_route_event(action_rows: list[dict[str, Any]]) -> str:
    if any(row.get("current_model_chain_resume_ready") is True for row in action_rows):
        return "model_chain_resume_candidate_ready"
    if any(row.get("requires_external_input") is True for row in action_rows):
        return "external_activation_wait"
    return "stage_boundary_review_needed"


def _machine_route_reason(core_gate: dict[str, Any], route_event: str) -> str:
    if route_event == "external_activation_wait":
        return "waiting_for_real_external_input_before_downstream_replay_holdout_calibration"
    if route_event == "model_chain_resume_candidate_ready":
        return "at_least_one_route_passed_external_gate_but_no_write_boundaries_still_apply"
    return str(core_gate.get("stage_decision", "stage_boundary_needs_review"))


def _machine_next_route(route_event: str) -> str:
    if route_event == "external_activation_wait":
        return "submit_real_external_input_then_rerun_stage_preflight_and_agent50"
    if route_event == "model_chain_resume_candidate_ready":
        return "rerun_downstream_replay_holdout_and_human_review_before_any_write"
    return "review_core_gate_before_expanding_internal_model"


def _new_core_interface_context(candidate_gate: dict[str, Any]) -> dict[str, Any]:
    metadata = _dict(candidate_gate.get("gate_metadata"))
    summary = _dict(candidate_gate.get("candidate_summary"))
    rows = candidate_gate.get("candidate_rows", [])
    candidate_rows = rows if isinstance(rows, list) else []
    highest_id = str(summary.get("highest_priority_candidate_id", ""))
    highest_row = next(
        (
            row
            for row in candidate_rows
            if isinstance(row, dict) and str(row.get("candidate_id", "")) == highest_id
        ),
        {},
    )
    return {
        "new_core_interface_candidate_gate_status": str(
            metadata.get("gate_status", "new_core_interface_candidate_gate_not_available")
        ),
        "new_core_interface_candidate_count": _safe_int(summary.get("candidate_count", 0)),
        "new_core_interface_admissible_candidate_count": _safe_int(
            summary.get("admissible_candidate_count", 0)
        ),
        "new_core_interface_highest_priority_candidate_id": highest_id,
        "new_core_interface_highest_priority_source_env_var": str(
            summary.get("highest_priority_source_env_var", "")
        ),
        "new_core_interface_highest_priority_system_layer": str(
            summary.get("highest_priority_system_layer", "")
        ),
        "new_core_interface_highest_priority_core_ability": str(
            summary.get("highest_priority_core_ability", "")
        ),
        "new_core_interface_highest_priority_validation_command": str(
            summary.get("highest_priority_validation_command", "")
        ),
        "new_core_interface_highest_priority_preflight_status": str(
            summary.get("highest_priority_preflight_status", "")
        ),
        "new_core_interface_highest_priority_preflight_pass": bool(
            summary.get("highest_priority_preflight_pass", False)
        ),
        "new_core_interface_highest_priority_can_route_to_downstream_calibration": bool(
            summary.get("highest_priority_can_route_to_downstream_calibration", False)
        ),
        "new_core_interface_highest_priority_downstream_calibration_status": str(
            summary.get("highest_priority_downstream_calibration_status", "")
        ),
        "new_core_interface_highest_priority_can_route_to_downstream_interface": bool(
            summary.get("highest_priority_can_route_to_downstream_interface", False)
        ),
        "new_core_interface_highest_priority_downstream_interface_status": str(
            summary.get("highest_priority_downstream_interface_status", "")
        ),
        "new_core_interface_highest_priority_can_run_agent53_field_calibration": bool(
            summary.get("highest_priority_can_run_agent53_field_calibration", False)
        ),
        "new_core_interface_highest_priority_agent53_field_candidate_ready": bool(
            summary.get("highest_priority_agent53_field_candidate_ready", False)
        ),
        "new_core_interface_highest_priority_next_interface_action": str(
            summary.get("highest_priority_next_interface_action", "")
        ),
        "new_core_interface_highest_priority_minimum_row_count": _safe_int(
            highest_row.get("minimum_row_count", 0)
        ),
        "new_core_interface_highest_priority_input_contract": list(
            highest_row.get("input_contract", [])
        )
        if isinstance(highest_row.get("input_contract", []), list)
        else [],
        "new_core_interface_highest_priority_output_contract": list(
            highest_row.get("output_contract", [])
        )
        if isinstance(highest_row.get("output_contract", []), list)
        else [],
        "new_core_interface_highest_priority_failure_boundary": str(
            highest_row.get("failure_boundary", "")
        ),
        "new_core_interface_can_generate_field_evidence": bool(
            summary.get("can_generate_field_evidence", False)
        ),
        "new_core_interface_can_resume_model_chain": bool(
            summary.get("can_resume_model_chain", False)
        ),
        "new_core_interface_can_write_to_actuator": bool(
            summary.get("can_write_to_actuator", False)
        ),
        "new_core_interface_can_write_to_release_gate": bool(
            summary.get("can_write_to_release_gate", False)
        ),
    }


def _new_core_acquisition_context(stage_gate: dict[str, Any]) -> dict[str, Any]:
    blockers = stage_gate.get("termination_blockers", [])
    return {
        "new_core_interface_acquisition_contract_termination_status": str(
            stage_gate.get("contract_termination_status", "")
        ),
        "new_core_interface_acquisition_module_stage_termination_pass": bool(
            stage_gate.get("module_stage_termination_pass", False)
        ),
        "new_core_interface_acquisition_downstream_reconnection_rate": _safe_float(
            stage_gate.get("downstream_reconnection_rate", 0.0)
        ),
        "new_core_interface_acquisition_field_package_ready_rate": _safe_float(
            stage_gate.get("field_package_ready_rate", 0.0)
        ),
        "new_core_interface_acquisition_termination_blockers": (
            list(blockers) if isinstance(blockers, list) else []
        ),
        "new_core_interface_acquisition_next_stage_decision": str(
            stage_gate.get("next_stage_decision", "")
        ),
        "new_core_interface_acquisition_next_operator_source_env_var": str(
            stage_gate.get("next_operator_source_env_var", "")
        ),
        "new_core_interface_acquisition_next_operator_validation_command": str(
            stage_gate.get("next_operator_validation_command", "")
        ),
    }


def _new_core_acquisition_summary(
    action_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    new_core_row = next(
        (row for row in action_rows if row.get("channel_id") == "NEW_CORE_INTERFACE"),
        {},
    )
    return {
        "new_core_interface_acquisition_contract_termination_status": str(
            new_core_row.get(
                "new_core_interface_acquisition_contract_termination_status",
                "",
            )
        ),
        "new_core_interface_acquisition_module_stage_termination_pass": bool(
            new_core_row.get(
                "new_core_interface_acquisition_module_stage_termination_pass",
                False,
            )
        ),
        "new_core_interface_acquisition_downstream_reconnection_rate": _safe_float(
            new_core_row.get(
                "new_core_interface_acquisition_downstream_reconnection_rate",
                0.0,
            )
        ),
        "new_core_interface_acquisition_field_package_ready_rate": _safe_float(
            new_core_row.get(
                "new_core_interface_acquisition_field_package_ready_rate",
                0.0,
            )
        ),
        "new_core_interface_acquisition_termination_blockers": (
            list(new_core_row.get("new_core_interface_acquisition_termination_blockers", []))
            if isinstance(
                new_core_row.get("new_core_interface_acquisition_termination_blockers", []),
                list,
            )
            else []
        ),
    }


def _board_status(
    *,
    core_gate: dict[str, Any],
    model_chain_ready_count: int,
    external_wait_count: int,
) -> str:
    if model_chain_ready_count > 0:
        return "stage_boundary_external_action_board_has_model_chain_resume_candidate"
    if (
        core_gate.get("stage_decision")
        == "stop_expansion_wait_for_real_field_package_or_new_core_interface"
        and external_wait_count > 0
    ):
        return "stage_boundary_external_action_board_waiting_for_external_inputs"
    return "stage_boundary_external_action_board_needs_core_gate_review"


def _priority_order(channel_id: str) -> int:
    order = {
        "R7_REAL_FIELD_PACKAGE": 1,
        "R8U66_PATH_ENDPOINT_LABEL_PACKAGE": 2,
        "R8U79_FORMAL_SEARCH_RESULT_PACKAGE": 3,
        "NEW_CORE_INTERFACE": 4,
    }
    return order.get(channel_id, 99)


def _canonical_low_friction_action_id(action_row: dict[str, Any]) -> str:
    if (
        action_row.get("channel_id") == "R7_REAL_FIELD_PACKAGE"
        and action_row.get("source_env_var") == "FOCUSED_CATALYST_RESPONSE_PATH"
    ):
        return "FIELD_ACTIVATION_RESPONSE_FOCUS_HANDOFF_NEXT_ACTION"
    return str(action_row.get("action_id", ""))


def _python_experiment_command(path: str) -> str:
    cleaned = path.strip()
    if not cleaned:
        return ""
    if cleaned.startswith(".venv/bin/python "):
        return cleaned
    if cleaned.startswith("experiments/") and cleaned.endswith(".py"):
        return f".venv/bin/python {cleaned}"
    return cleaned


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value]


def _list_of_dicts(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_int(value: Any) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def _safe_float(value: Any) -> float:
    try:
        return float(value or 0.0)
    except (TypeError, ValueError):
        return 0.0

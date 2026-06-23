from pathlib import Path

from water_ai.governance_recovery_integrity_audit import (
    build_governance_recovery_integrity_audit,
    governance_recovery_integrity_audit_report_md,
)


def test_governance_recovery_integrity_audit_scores_stage_boundary_recovery_chain(
    tmp_path: Path,
) -> None:
    (tmp_path / "experiments").mkdir()
    (tmp_path / "outputs" / "model_core_governance").mkdir(parents=True)
    (tmp_path / "deliverables" / "model_core_optimization").mkdir(parents=True)
    validation_command = tmp_path / "experiments" / "run_focused_catalyst_response_merge.py"
    validation_command.write_text("# runner\n", encoding="utf-8")
    board_path = (
        tmp_path
        / "outputs"
        / "model_core_governance"
        / "stage_boundary_external_action_board.json"
    )
    report_path = (
        tmp_path
        / "deliverables"
        / "model_core_optimization"
        / "stage_boundary_external_action_board.md"
    )
    board_path.write_text("{}", encoding="utf-8")
    report_path.write_text("# board\n", encoding="utf-8")

    handoff = _handoff()
    boundary = _resource_boundary()
    audit = build_governance_recovery_integrity_audit(
        project_root=tmp_path,
        manifest={
            "latest_stage_boundary_external_action_board": str(
                board_path.relative_to(tmp_path)
            ),
            "latest_stage_boundary_external_action_board_report": str(
                report_path.relative_to(tmp_path)
            ),
            "latest_stage_boundary_external_action_board_machine_handoff_route_event": (
                handoff["route_event"]
            ),
            "latest_stage_boundary_external_action_board_machine_handoff_next_route": (
                handoff["next_route"]
            ),
            "latest_stage_boundary_external_action_board_machine_handoff_next_route_source_env_var": (
                handoff["next_route_source_env_var"]
            ),
            "latest_stage_boundary_external_action_board_machine_handoff_next_route_validation_command": (
                handoff["next_route_validation_command"]
            ),
            "latest_stage_boundary_external_action_board_machine_handoff_manual_action_required": True,
            "latest_stage_boundary_external_action_board_machine_handoff_current_basis_refs": (
                handoff["current_basis_refs"]
            ),
            "latest_stage_boundary_external_action_board_machine_handoff_not_current_basis_refs": (
                handoff["not_current_basis_refs"]
            ),
            "latest_stage_boundary_external_action_board_resource_boundary_forbidden_basis": (
                boundary["forbidden_basis"]
            ),
        },
        stage_boundary_external_action_board={
            "machine_handoff": handoff,
            "machine_handoff_contract_gate": {
                "contract_stage_pass": True,
                "contract_score": 1.0,
            },
            "resource_boundary": boundary,
            "resource_boundary_gate": {
                "resource_boundary_stage_pass": True,
                "resource_boundary_score": 1.0,
            },
            "subagent_orchestration_probe": _subagent_probe(),
            "boundary": {
                "can_generate_field_evidence": False,
                "can_write_to_actuator": False,
                "can_write_to_release_gate": False,
            },
        },
        core_score_termination_gate={
            "stage_decision": "stop_expansion_wait_for_real_field_package_or_new_core_interface",
        },
    )
    report_md = governance_recovery_integrity_audit_report_md(audit)

    assert audit["audit_metadata"]["audit_id"] == (
        "R8u172_governance_recovery_integrity_audit"
    )
    assert audit["audit_metadata"]["audit_status"] == (
        "recovery_integrity_pass_waiting_for_real_external_input"
    )
    assert audit["recovery_integrity_score"] == 1.0
    assert audit["recovery_integrity_stage_pass"] is True
    assert audit["blockers"] == []
    assert audit["stale_or_mismatch_fields"] == []
    assert audit["safe_next_route"] == (
        "submit_real_external_input_then_rerun_stage_preflight_and_agent50"
    )
    assert audit["checks"]["manifest_stage_board_route_alignment"] == 1.0
    assert audit["checks"]["validation_command_exists"] == 1.0
    assert audit["checks"]["manifest_pointer_freshness"] == 1.0
    assert audit["checks"]["manual_action_contract_integrity"] == 1.0
    assert audit["checks"]["basis_boundary_integrity"] == 1.0
    assert audit["checks"]["resource_boundary_integrity"] == 1.0
    assert audit["checks"]["subagent_orchestration_integrity"] == 1.0
    assert audit["checks"]["no_write_boundary_integrity"] == 1.0
    trace_gate = audit["minimum_traceability_gate"]
    assert trace_gate["gate_id"] == "R8u177_minimum_recovery_traceability_gate"
    assert trace_gate["gate_status"] == "minimum_recovery_traceability_pass"
    assert trace_gate["decision_log_status"] == "decision_log_minimum_recovery_route_recorded"
    assert trace_gate["traceability_status"] == "traceability_minimum_recovery_route_recorded"
    assert trace_gate["traceability_score"] == 1.0
    assert trace_gate["missing_link_count"] == 0
    assert trace_gate["blockers"] == []
    assert trace_gate["scope_boundary"] == (
        "recovery_route_trace_only_not_full_project_traceability_matrix"
    )
    assert trace_gate["can_replace_full_traceability_matrix"] is False
    assert len(trace_gate["trace_rows"]) == 4
    assert {row["trace_id"] for row in trace_gate["trace_rows"]} == {
        "basis_to_stage_route",
        "resource_boundary_to_no_write",
        "manual_action_to_resume_evidence",
        "protocol_adaptation_to_anti_bloat",
    }
    numeric_trace = audit["numeric_calculation_trace"]
    assert numeric_trace["trace_id"] == (
        "R8u173_recovery_integrity_numeric_calculation_trace"
    )
    assert numeric_trace["trace_status"] == (
        "numeric_trace_pass_recovery_integrity_score_recomputed"
    )
    assert numeric_trace["score_formula"] == "mean(check_scores)"
    assert numeric_trace["component_count"] == 8
    assert numeric_trace["component_scores"] == audit["checks"]
    assert numeric_trace["computed_score"] == audit["recovery_integrity_score"]
    assert numeric_trace["reported_score"] == 1.0
    assert numeric_trace["score_delta"] == 0.0
    assert numeric_trace["trace_pass"] is True
    assert numeric_trace["field_claim_upgrade_allowed"] is False
    protocol_adaptation = audit["protocol_adaptation"]
    assert protocol_adaptation["adaptation_id"] == (
        "R8u173_complex_project_protocol_to_engineering_model_adapter"
    )
    assert protocol_adaptation["source_protocol"] == (
        "复杂项目启动前置治理协议_v3_核心版.md"
    )
    assert protocol_adaptation["anti_protocol_bloat_gate"]["gate_status"] == (
        "pass_selective_adoption_not_full_protocol_copy"
    )
    assert protocol_adaptation["anti_protocol_bloat_gate"]["selected_rule_count"] == 6
    assert protocol_adaptation["anti_protocol_bloat_gate"]["deferred_rule_count"] == 4
    selected_rule_ids = {
        rule["rule_id"] for rule in protocol_adaptation["selected_rules"]
    }
    assert {
        "current_basis_contract",
        "resource_boundary_contract",
        "numeric_calculation_trace",
        "dynamic_stage_handoff",
        "micro_task_execution_check",
        "subagent_orchestration_probe",
    } <= selected_rule_ids
    assert protocol_adaptation["engineering_model_effect"] == {
        "system_layer": "verification_governance",
        "core_abilities": ["verifiability", "engineering_feasibility", "evolvability"],
        "model_change_type": "recovery_gate_contract_upgrade",
    }
    assert audit["change_inventory"][0]["path"] == str(board_path.relative_to(tmp_path))
    assert audit["boundary"]["can_generate_field_evidence"] is False
    assert audit["boundary"]["can_write_to_actuator"] is False
    assert audit["boundary"]["can_write_to_release_gate"] is False
    assert "recovery_integrity_score: `1.0`" in report_md
    assert "numeric_calculation_trace_status" in report_md
    assert "protocol_adaptation_status" in report_md
    assert "minimum_traceability_gate_status" in report_md
    assert "safe_next_route" in report_md


def test_governance_recovery_integrity_audit_fails_on_extended_route_alignment_drift(
    tmp_path: Path,
) -> None:
    (tmp_path / "experiments").mkdir()
    (tmp_path / "outputs" / "model_core_governance").mkdir(parents=True)
    (tmp_path / "deliverables" / "model_core_optimization").mkdir(parents=True)
    validation_command = tmp_path / "experiments" / "run_focused_catalyst_response_merge.py"
    validation_command.write_text("# runner\n", encoding="utf-8")
    board_path = (
        tmp_path
        / "outputs"
        / "model_core_governance"
        / "stage_boundary_external_action_board.json"
    )
    report_path = (
        tmp_path
        / "deliverables"
        / "model_core_optimization"
        / "stage_boundary_external_action_board.md"
    )
    board_path.write_text("{}", encoding="utf-8")
    report_path.write_text("# board\n", encoding="utf-8")

    handoff = _handoff()
    boundary = _resource_boundary()
    audit = build_governance_recovery_integrity_audit(
        project_root=tmp_path,
        manifest={
            "latest_stage_boundary_external_action_board": str(
                board_path.relative_to(tmp_path)
            ),
            "latest_stage_boundary_external_action_board_report": str(
                report_path.relative_to(tmp_path)
            ),
            "latest_stage_boundary_external_action_board_machine_handoff_route_event": (
                "continue_current_micro_loop"
            ),
            "latest_stage_boundary_external_action_board_machine_handoff_next_route": (
                handoff["next_route"]
            ),
            "latest_stage_boundary_external_action_board_machine_handoff_next_route_source_env_var": (
                handoff["next_route_source_env_var"]
            ),
            "latest_stage_boundary_external_action_board_machine_handoff_next_route_validation_command": (
                "experiments/old_stale_route.py"
            ),
            "latest_stage_boundary_external_action_board_machine_handoff_manual_action_required": True,
            "latest_stage_boundary_external_action_board_machine_handoff_current_basis_refs": [
                "stale.current_basis"
            ],
            "latest_stage_boundary_external_action_board_machine_handoff_not_current_basis_refs": (
                handoff["not_current_basis_refs"]
            ),
            "latest_stage_boundary_external_action_board_resource_boundary_forbidden_basis": (
                boundary["forbidden_basis"]
            ),
        },
        stage_boundary_external_action_board={
            "machine_handoff": handoff,
            "machine_handoff_contract_gate": {
                "contract_stage_pass": True,
                "contract_score": 1.0,
            },
            "resource_boundary": boundary,
            "resource_boundary_gate": {
                "resource_boundary_stage_pass": True,
                "resource_boundary_score": 1.0,
            },
            "subagent_orchestration_probe": _subagent_probe(),
            "boundary": {
                "can_generate_field_evidence": False,
                "can_write_to_actuator": False,
                "can_write_to_release_gate": False,
            },
        },
        core_score_termination_gate={
            "stage_decision": "stop_expansion_wait_for_real_field_package_or_new_core_interface",
        },
    )

    assert audit["checks"]["manifest_stage_board_route_alignment"] == 0.0
    assert "manifest_stage_board_route_alignment_below_1.00" in audit["blockers"]
    assert audit["recovery_integrity_stage_pass"] is False
    assert audit["safe_next_route"] == (
        "repair_recovery_integrity_blockers_before_next_route"
    )
    assert (
        "latest_stage_boundary_external_action_board_machine_handoff_route_event"
        in audit["stale_or_mismatch_fields"]
    )
    assert (
        "latest_stage_boundary_external_action_board_machine_handoff_next_route_validation_command"
        in audit["stale_or_mismatch_fields"]
    )
    assert (
        "latest_stage_boundary_external_action_board_machine_handoff_current_basis_refs"
        in audit["stale_or_mismatch_fields"]
    )


def test_governance_recovery_integrity_audit_fails_on_invalid_subagent_probe(
    tmp_path: Path,
) -> None:
    (tmp_path / "experiments").mkdir()
    (tmp_path / "outputs" / "model_core_governance").mkdir(parents=True)
    (tmp_path / "deliverables" / "model_core_optimization").mkdir(parents=True)
    validation_command = tmp_path / "experiments" / "run_focused_catalyst_response_merge.py"
    validation_command.write_text("# runner\n", encoding="utf-8")
    board_path = (
        tmp_path
        / "outputs"
        / "model_core_governance"
        / "stage_boundary_external_action_board.json"
    )
    report_path = (
        tmp_path
        / "deliverables"
        / "model_core_optimization"
        / "stage_boundary_external_action_board.md"
    )
    board_path.write_text("{}", encoding="utf-8")
    report_path.write_text("# board\n", encoding="utf-8")

    handoff = _handoff()
    boundary = _resource_boundary()
    invalid_probe = _subagent_probe()
    invalid_probe["capability"] = "available"
    invalid_probe["strategy"] = "parallel_domains"
    invalid_probe["capability_probe"]["tool_discovered"] = False
    invalid_probe["capability_probe"]["spawn_attempted"] = False
    invalid_probe["roles"] = []
    audit = build_governance_recovery_integrity_audit(
        project_root=tmp_path,
        manifest={
            "latest_stage_boundary_external_action_board": str(
                board_path.relative_to(tmp_path)
            ),
            "latest_stage_boundary_external_action_board_report": str(
                report_path.relative_to(tmp_path)
            ),
            "latest_stage_boundary_external_action_board_machine_handoff_route_event": (
                handoff["route_event"]
            ),
            "latest_stage_boundary_external_action_board_machine_handoff_next_route": (
                handoff["next_route"]
            ),
            "latest_stage_boundary_external_action_board_machine_handoff_next_route_source_env_var": (
                handoff["next_route_source_env_var"]
            ),
            "latest_stage_boundary_external_action_board_machine_handoff_next_route_validation_command": (
                handoff["next_route_validation_command"]
            ),
            "latest_stage_boundary_external_action_board_machine_handoff_manual_action_required": True,
            "latest_stage_boundary_external_action_board_machine_handoff_current_basis_refs": (
                handoff["current_basis_refs"]
            ),
            "latest_stage_boundary_external_action_board_machine_handoff_not_current_basis_refs": (
                handoff["not_current_basis_refs"]
            ),
            "latest_stage_boundary_external_action_board_resource_boundary_forbidden_basis": (
                boundary["forbidden_basis"]
            ),
        },
        stage_boundary_external_action_board={
            "machine_handoff": handoff,
            "machine_handoff_contract_gate": {
                "contract_stage_pass": True,
                "contract_score": 1.0,
            },
            "resource_boundary": boundary,
            "resource_boundary_gate": {
                "resource_boundary_stage_pass": True,
                "resource_boundary_score": 1.0,
            },
            "subagent_orchestration_probe": invalid_probe,
            "boundary": {
                "can_generate_field_evidence": False,
                "can_write_to_actuator": False,
                "can_write_to_release_gate": False,
            },
        },
        core_score_termination_gate={
            "stage_decision": "stop_expansion_wait_for_real_field_package_or_new_core_interface",
        },
    )

    assert audit["checks"]["subagent_orchestration_integrity"] == 0.0
    assert "subagent_orchestration_integrity_below_1.00" in audit["blockers"]
    assert "subagent_available_without_tool_or_spawn_evidence" in audit[
        "stale_or_mismatch_fields"
    ]
    assert "subagent_parallel_strategy_without_roles" in audit[
        "stale_or_mismatch_fields"
    ]
    assert audit["recovery_integrity_stage_pass"] is False


def test_governance_recovery_integrity_audit_flags_missing_minimum_traceability_link(
    tmp_path: Path,
) -> None:
    (tmp_path / "experiments").mkdir()
    (tmp_path / "outputs" / "model_core_governance").mkdir(parents=True)
    (tmp_path / "deliverables" / "model_core_optimization").mkdir(parents=True)
    validation_command = tmp_path / "experiments" / "run_focused_catalyst_response_merge.py"
    validation_command.write_text("# runner\n", encoding="utf-8")
    board_path = (
        tmp_path
        / "outputs"
        / "model_core_governance"
        / "stage_boundary_external_action_board.json"
    )
    report_path = (
        tmp_path
        / "deliverables"
        / "model_core_optimization"
        / "stage_boundary_external_action_board.md"
    )
    board_path.write_text("{}", encoding="utf-8")
    report_path.write_text("# board\n", encoding="utf-8")

    handoff = _handoff()
    handoff["manual_action_required"] = {
        "required": True,
        "actor": "field_operator_or_user",
        "source_env_var": "FOCUSED_CATALYST_RESPONSE_PATH",
        "action": "fill_focused_catalyst_response_template",
        "validation_command": "experiments/run_focused_catalyst_response_merge.py",
        "resume_evidence": "",
    }
    boundary = _resource_boundary()
    audit = build_governance_recovery_integrity_audit(
        project_root=tmp_path,
        manifest={
            "latest_stage_boundary_external_action_board": str(
                board_path.relative_to(tmp_path)
            ),
            "latest_stage_boundary_external_action_board_report": str(
                report_path.relative_to(tmp_path)
            ),
            "latest_stage_boundary_external_action_board_machine_handoff_route_event": (
                handoff["route_event"]
            ),
            "latest_stage_boundary_external_action_board_machine_handoff_next_route": (
                handoff["next_route"]
            ),
            "latest_stage_boundary_external_action_board_machine_handoff_next_route_source_env_var": (
                handoff["next_route_source_env_var"]
            ),
            "latest_stage_boundary_external_action_board_machine_handoff_next_route_validation_command": (
                handoff["next_route_validation_command"]
            ),
            "latest_stage_boundary_external_action_board_machine_handoff_manual_action_required": True,
            "latest_stage_boundary_external_action_board_machine_handoff_current_basis_refs": (
                handoff["current_basis_refs"]
            ),
            "latest_stage_boundary_external_action_board_machine_handoff_not_current_basis_refs": (
                handoff["not_current_basis_refs"]
            ),
            "latest_stage_boundary_external_action_board_resource_boundary_forbidden_basis": (
                boundary["forbidden_basis"]
            ),
        },
        stage_boundary_external_action_board={
            "machine_handoff": handoff,
            "machine_handoff_contract_gate": {
                "contract_stage_pass": False,
                "contract_score": 0.833,
            },
            "resource_boundary": boundary,
            "resource_boundary_gate": {
                "resource_boundary_stage_pass": True,
                "resource_boundary_score": 1.0,
            },
            "subagent_orchestration_probe": _subagent_probe(),
            "boundary": {
                "can_generate_field_evidence": False,
                "can_write_to_actuator": False,
                "can_write_to_release_gate": False,
            },
        },
        core_score_termination_gate={
            "stage_decision": "stop_expansion_wait_for_real_field_package_or_new_core_interface",
        },
    )

    trace_gate = audit["minimum_traceability_gate"]
    assert trace_gate["gate_status"] == "minimum_recovery_traceability_incomplete"
    assert trace_gate["traceability_score"] < 1.0
    assert trace_gate["missing_link_count"] == 1
    assert "manual_action_to_resume_evidence_missing_link" in trace_gate["blockers"]
    manual_row = [
        row
        for row in trace_gate["trace_rows"]
        if row["trace_id"] == "manual_action_to_resume_evidence"
    ][0]
    assert manual_row["link_status"] == "missing_link"
    assert "resume_evidence" in manual_row["missing_fields"]


def _handoff() -> dict[str, object]:
    return {
        "route_event": "external_activation_wait",
        "next_route": "submit_real_external_input_then_rerun_stage_preflight_and_agent50",
        "next_route_source_env_var": "FOCUSED_CATALYST_RESPONSE_PATH",
        "next_route_validation_command": "experiments/run_focused_catalyst_response_merge.py",
        "manual_action_required": {
            "required": True,
            "actor": "field_operator_or_user",
            "source_env_var": "FOCUSED_CATALYST_RESPONSE_PATH",
            "action": "fill_focused_catalyst_response_template",
            "validation_command": "experiments/run_focused_catalyst_response_merge.py",
            "resume_evidence": "preflight JSON showing pass=true",
        },
        "current_basis_refs": ["core_gate.stage_decision"],
        "not_current_basis_refs": [
            "synthetic_rows",
            "template_rows",
            "literature_only_rows",
        ],
        "can_generate_field_evidence": False,
        "can_resume_model_chain": False,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
        "no_write_boundary_preserved": True,
    }


def _subagent_probe() -> dict[str, object]:
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


def _resource_boundary() -> dict[str, object]:
    return {
        "allowed_basis": ["verified_stage_boundary_gates"],
        "forbidden_basis": [
            "template_rows_as_field_evidence",
            "synthetic_rows_as_field_evidence",
            "literature_only_rows_as_field_evidence",
        ],
        "official_supplementary_basis": ["template_directories_as_schema_guides_only"],
        "gray_zone": ["external_package_supplied_but_not_preflighted"],
        "external_model_or_tool_policy": {
            "can_emit_legal_or_patent_conclusion": False,
            "can_replace_field_validation": False,
        },
        "manual_annotation_or_human_labeling_policy": {
            "manual_action_required": True,
            "accepted_after_preflight": True,
        },
        "no_write_policy": {
            "can_generate_field_evidence": False,
            "can_write_to_actuator": False,
            "can_write_to_release_gate": False,
            "field_claim_upgrade_allowed": False,
        },
    }

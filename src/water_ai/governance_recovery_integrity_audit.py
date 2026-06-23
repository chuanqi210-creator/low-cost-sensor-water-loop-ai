from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any


AUDIT_ID = "R8u172_governance_recovery_integrity_audit"


def build_governance_recovery_integrity_audit(
    *,
    project_root: Path,
    manifest: dict[str, Any],
    stage_boundary_external_action_board: dict[str, Any],
    core_score_termination_gate: dict[str, Any],
) -> dict[str, Any]:
    """Check whether the top recovery artifacts are mutually consistent."""

    handoff = _dict(stage_boundary_external_action_board.get("machine_handoff"))
    resource_boundary = _dict(stage_boundary_external_action_board.get("resource_boundary"))
    board_boundary = _dict(stage_boundary_external_action_board.get("boundary"))
    subagent_orchestration_probe = _dict(
        stage_boundary_external_action_board.get("subagent_orchestration_probe")
    )
    protocol_adaptation = _protocol_adaptation()
    checks, issues = _run_checks(
        project_root=project_root,
        manifest=manifest,
        handoff=handoff,
        resource_boundary=resource_boundary,
        board_boundary=board_boundary,
        subagent_orchestration_probe=subagent_orchestration_probe,
        stage_boundary_external_action_board=stage_boundary_external_action_board,
    )
    blockers = [
        f"{name}_below_1.00"
        for name, score in checks.items()
        if score < 1.0
    ]
    score = round(sum(checks.values()) / len(checks), 3) if checks else 0.0
    thresholds = {name: 1.0 for name in checks}
    numeric_calculation_trace = _numeric_calculation_trace(
        checks=checks,
        reported_score=score,
        thresholds=thresholds,
    )
    minimum_traceability_gate = _minimum_traceability_gate(
        handoff=handoff,
        resource_boundary=resource_boundary,
        board_boundary=board_boundary,
        core_score_termination_gate=core_score_termination_gate,
        protocol_adaptation=protocol_adaptation,
    )
    if numeric_calculation_trace["trace_pass"] is not True:
        blockers.append("numeric_calculation_trace_failed")
    blockers.extend(minimum_traceability_gate["blockers"])
    stage_pass = not blockers
    safe_next_route = (
        str(handoff.get("next_route", ""))
        if stage_pass
        else "repair_recovery_integrity_blockers_before_next_route"
    )
    route_event = str(handoff.get("route_event", ""))
    return {
        "audit_metadata": {
            "audit_id": AUDIT_ID,
            "audit_status": _audit_status(stage_pass=stage_pass, route_event=route_event),
            "audit_role": "cross_artifact_recovery_integrity_audit",
            "created_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace(
                "+00:00",
                "Z",
            ),
            "source_stage_decision": str(core_score_termination_gate.get("stage_decision", "")),
        },
        "thresholds": thresholds,
        "checks": checks,
        "numeric_calculation_trace": numeric_calculation_trace,
        "protocol_adaptation": protocol_adaptation,
        "minimum_traceability_gate": minimum_traceability_gate,
        "recovery_integrity_score": score,
        "recovery_integrity_stage_pass": stage_pass,
        "blockers": blockers,
        "stale_or_mismatch_fields": issues,
        "safe_next_route": safe_next_route,
        "route_event": route_event,
        "change_inventory": _change_inventory(project_root, manifest, handoff),
        "boundary": {
            "can_generate_field_evidence": False,
            "can_resume_model_chain": bool(handoff.get("can_resume_model_chain", False)),
            "can_write_to_actuator": False,
            "can_write_to_release_gate": False,
            "field_claim_upgrade_allowed": False,
            "boundary_note": (
                "This audit checks recovery-chain consistency only. It does not create "
                "field evidence, field validation, actuator readiness, release readiness, "
                "legal opinions or patentability conclusions."
            ),
        },
    }


def governance_recovery_integrity_audit_report_md(audit: dict[str, Any]) -> str:
    metadata = audit["audit_metadata"]
    lines = [
        "# Governance Recovery Integrity Audit",
        "",
        "## Position",
        "",
        (
            "This audit checks whether manifest, stage boundary board, validation command, "
            "basis boundaries and no-write boundaries agree before the next recovery route."
        ),
        "",
        "## Audit State",
        "",
        f"- audit_id: `{metadata['audit_id']}`",
        f"- audit_status: `{metadata['audit_status']}`",
        f"- recovery_integrity_score: `{audit['recovery_integrity_score']}`",
        f"- recovery_integrity_stage_pass: `{audit['recovery_integrity_stage_pass']}`",
        f"- safe_next_route: `{audit['safe_next_route']}`",
        f"- blockers: `{audit['blockers']}`",
        f"- stale_or_mismatch_fields: `{audit['stale_or_mismatch_fields']}`",
        "",
        "## Checks",
        "",
    ]
    for name, score in audit["checks"].items():
        lines.append(f"- {name}: `{score}`")
    numeric_trace = audit["numeric_calculation_trace"]
    lines.extend(
        [
            "",
            "## Numeric Calculation Trace",
            "",
            f"- numeric_calculation_trace_status: `{numeric_trace['trace_status']}`",
            f"- numeric_calculation_trace_formula: `{numeric_trace['score_formula']}`",
            f"- numeric_calculation_trace_component_count: `{numeric_trace['component_count']}`",
            f"- numeric_calculation_trace_reported_score: `{numeric_trace['reported_score']}`",
            f"- numeric_calculation_trace_computed_score: `{numeric_trace['computed_score']}`",
            f"- numeric_calculation_trace_score_delta: `{numeric_trace['score_delta']}`",
            f"- field_claim_upgrade_allowed: `{numeric_trace['field_claim_upgrade_allowed']}`",
        ]
    )
    protocol_adaptation = audit["protocol_adaptation"]
    anti_bloat_gate = protocol_adaptation["anti_protocol_bloat_gate"]
    lines.extend(
        [
            "",
            "## Protocol Adaptation",
            "",
            f"- protocol_adaptation_status: `{protocol_adaptation['adaptation_status']}`",
            f"- source_protocol: `{protocol_adaptation['source_protocol']}`",
            f"- anti_protocol_bloat_gate_status: `{anti_bloat_gate['gate_status']}`",
            f"- selected_rule_count: `{anti_bloat_gate['selected_rule_count']}`",
            f"- deferred_rule_count: `{anti_bloat_gate['deferred_rule_count']}`",
            f"- engineering_model_effect: `{protocol_adaptation['engineering_model_effect']}`",
            "",
            "| rule_id | model mapping | gate or metric | failure boundary |",
            "| --- | --- | --- | --- |",
        ]
    )
    for rule in protocol_adaptation["selected_rules"]:
        lines.append(
            "| "
            f"`{rule['rule_id']}` | "
            f"{rule['project_mapping']} | "
            f"`{rule['implemented_as']}` | "
            f"{rule['failure_boundary']} |"
        )
    trace_gate = audit["minimum_traceability_gate"]
    lines.extend(
        [
            "",
            "## Minimum Traceability Gate",
            "",
            f"- minimum_traceability_gate_status: `{trace_gate['gate_status']}`",
            f"- decision_log_status: `{trace_gate['decision_log_status']}`",
            f"- traceability_status: `{trace_gate['traceability_status']}`",
            f"- traceability_score: `{trace_gate['traceability_score']}`",
            f"- missing_link_count: `{trace_gate['missing_link_count']}`",
            f"- blockers: `{trace_gate['blockers']}`",
            f"- scope_boundary: `{trace_gate['scope_boundary']}`",
            "",
            "| trace_id | link_status | missing_fields |",
            "| --- | --- | --- |",
        ]
    )
    for row in trace_gate["trace_rows"]:
        lines.append(
            "| "
            f"`{row['trace_id']}` | "
            f"`{row['link_status']}` | "
            f"`{row['missing_fields']}` |"
        )
    lines.extend(
        [
            "",
            "## Change Inventory",
            "",
            "| path | role | status |",
            "| --- | --- | --- |",
        ]
    )
    for item in audit["change_inventory"]:
        lines.append(f"| `{item['path']}` | `{item['role']}` | `{item['status']}` |")
    boundary = audit["boundary"]
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            f"- can_generate_field_evidence: `{boundary['can_generate_field_evidence']}`",
            f"- can_resume_model_chain: `{boundary['can_resume_model_chain']}`",
            f"- can_write_to_actuator: `{boundary['can_write_to_actuator']}`",
            f"- can_write_to_release_gate: `{boundary['can_write_to_release_gate']}`",
            f"- field_claim_upgrade_allowed: `{boundary['field_claim_upgrade_allowed']}`",
            "",
            boundary["boundary_note"],
            "",
        ]
    )
    return "\n".join(lines)


def _run_checks(
    *,
    project_root: Path,
    manifest: dict[str, Any],
    handoff: dict[str, Any],
    resource_boundary: dict[str, Any],
    board_boundary: dict[str, Any],
    subagent_orchestration_probe: dict[str, Any],
    stage_boundary_external_action_board: dict[str, Any],
) -> tuple[dict[str, float], list[str]]:
    checks: dict[str, float] = {}
    issues: list[str] = []
    checks["manifest_stage_board_route_alignment"], route_issues = _route_alignment(
        manifest,
        handoff,
        resource_boundary,
    )
    issues.extend(route_issues)
    checks["validation_command_exists"], command_issues = _validation_command_exists(
        project_root,
        str(handoff.get("next_route_validation_command", "")),
    )
    issues.extend(command_issues)
    checks["manifest_pointer_freshness"], pointer_issues = _manifest_pointer_freshness(
        project_root,
        manifest,
    )
    issues.extend(pointer_issues)
    checks["manual_action_contract_integrity"], manual_issues = _manual_action_integrity(
        _dict(handoff.get("manual_action_required"))
    )
    issues.extend(manual_issues)
    checks["basis_boundary_integrity"], basis_issues = _basis_boundary_integrity(handoff)
    issues.extend(basis_issues)
    checks["resource_boundary_integrity"], resource_issues = _resource_boundary_integrity(
        resource_boundary,
        stage_boundary_external_action_board,
    )
    issues.extend(resource_issues)
    (
        checks["subagent_orchestration_integrity"],
        subagent_issues,
    ) = _subagent_orchestration_integrity(subagent_orchestration_probe)
    issues.extend(subagent_issues)
    checks["no_write_boundary_integrity"], no_write_issues = _no_write_integrity(
        handoff,
        resource_boundary,
        board_boundary,
    )
    issues.extend(no_write_issues)
    return checks, issues


def _numeric_calculation_trace(
    *,
    checks: dict[str, float],
    reported_score: float,
    thresholds: dict[str, float],
) -> dict[str, Any]:
    component_scores = {name: float(score) for name, score in checks.items()}
    computed_score = (
        round(sum(component_scores.values()) / len(component_scores), 3)
        if component_scores
        else 0.0
    )
    score_delta = round(abs(computed_score - float(reported_score)), 6)
    trace_pass = score_delta == 0.0
    return {
        "trace_id": "R8u173_recovery_integrity_numeric_calculation_trace",
        "trace_status": (
            "numeric_trace_pass_recovery_integrity_score_recomputed"
            if trace_pass
            else "numeric_trace_failed_score_mismatch"
        ),
        "score_formula": "mean(check_scores)",
        "source_fields": list(component_scores),
        "component_scores": component_scores,
        "component_count": len(component_scores),
        "thresholds": thresholds,
        "reported_score": reported_score,
        "computed_score": computed_score,
        "score_delta": score_delta,
        "trace_pass": trace_pass,
        "unit": "dimensionless_score_0_to_1",
        "boundary_level": "governance_recovery_integrity_not_field_validation",
        "evidence_level": "governance_audit_not_field_evidence",
        "can_generate_field_evidence": False,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
        "field_claim_upgrade_allowed": False,
    }


def _protocol_adaptation() -> dict[str, Any]:
    selected_rules = [
        {
            "rule_id": "current_basis_contract",
            "protocol_concept": "current_basis 与 not_current_basis 分离",
            "project_mapping": "区分 stage gate、真实外部输入、synthetic/template/literature 边界",
            "system_layer": "verification_governance",
            "core_ability": "verifiability",
            "implemented_as": "basis_boundary_integrity",
            "failure_boundary": "若 current_basis 为空或 synthetic/template/literature 未显式排除，则不能继续恢复主链。",
        },
        {
            "rule_id": "resource_boundary_contract",
            "protocol_concept": "allowed_basis/forbidden_basis/gray_zone 资源边界",
            "project_mapping": "阻断 template、synthetic、literature-only 进入 field evidence 或 release gate",
            "system_layer": "verification_governance",
            "core_ability": "protectability",
            "implemented_as": "resource_boundary_integrity + no_write_boundary_integrity",
            "failure_boundary": "资源边界缺失时只能修复治理链，不能升级现场结论。",
        },
        {
            "rule_id": "numeric_calculation_trace",
            "protocol_concept": "数字结论必须可复算、带单位和外推边界",
            "project_mapping": "恢复完整性分数由七个检查项均值复算",
            "system_layer": "verification_governance",
            "core_ability": "verifiability",
            "implemented_as": "numeric_calculation_trace",
            "failure_boundary": "分数无法复算时即使检查项看似通过，也不能作为下一路由依据。",
        },
        {
            "rule_id": "dynamic_stage_handoff",
            "protocol_concept": "机器看版必须留下 route_event、next_route、route_reason",
            "project_mapping": "恢复链从最新 stage boundary board 读取安全下一路由",
            "system_layer": "verification_governance",
            "core_ability": "evolvability",
            "implemented_as": "safe_next_route + route_event",
            "failure_boundary": "路由不一致时进入 repair_recovery_integrity_blockers_before_next_route。",
        },
        {
            "rule_id": "micro_task_execution_check",
            "protocol_concept": "声称完成的治理修复必须落到可运行小任务",
            "project_mapping": "下一路由必须有存在的 validation command 和 change inventory",
            "system_layer": "verification_governance",
            "core_ability": "engineering_feasibility",
            "implemented_as": "validation_command_exists + change_inventory",
            "failure_boundary": "没有可运行验证命令时，不能只靠文字 handoff 继续。",
        },
        {
            "rule_id": "subagent_orchestration_probe",
            "protocol_concept": "子代理可用性要区分 environment_listed/tool_discovered/spawn_attempted",
            "project_mapping": "只把子代理作为只读审计或明确边界 worker，不让其替代主链判断",
            "system_layer": "verification_governance",
            "core_ability": "evolvability",
            "implemented_as": "subagent_orchestration_integrity",
            "failure_boundary": "若无 tool_discovered 或 spawn_attempted 证据，只能写 inline_fallback。",
        },
    ]
    deferred_rules = [
        {
            "rule_id": "live_project_pool_scan",
            "defer_reason": "当前项目是既有工程模型优化，不是新项目池发散。",
        },
        {
            "rule_id": "full_traceability_matrix",
            "defer_reason": "后续进入论文/专利/field package 成熟阶段再扩展，避免当前恢复链膨胀。",
        },
        {
            "rule_id": "rendered_artifact_freshness",
            "defer_reason": "本轮不更新 Word/PPT/PDF，不应把展示物 QA 放在模型主链之前。",
        },
        {
            "rule_id": "real_project_pressure_test_gate",
            "defer_reason": "当前最高价值是压实本项目恢复链，外部压力测试进入阶段边界 backlog。",
        },
    ]
    return {
        "adaptation_id": "R8u173_complex_project_protocol_to_engineering_model_adapter",
        "source_protocol": "复杂项目启动前置治理协议_v3_核心版.md",
        "adaptation_status": "selected_protocol_rules_integrated_into_recovery_gate",
        "selected_rules": selected_rules,
        "deferred_rules": deferred_rules,
        "anti_protocol_bloat_gate": {
            "gate_status": "pass_selective_adoption_not_full_protocol_copy",
            "selected_rule_count": len(selected_rules),
            "deferred_rule_count": len(deferred_rules),
            "adoption_rule": (
                "Only protocol rules that improve recovery, evidence boundaries, "
                "numeric traceability or low-friction continuation enter this audit."
            ),
        },
        "engineering_model_effect": {
            "system_layer": "verification_governance",
            "core_abilities": ["verifiability", "engineering_feasibility", "evolvability"],
            "model_change_type": "recovery_gate_contract_upgrade",
        },
    }


def _minimum_traceability_gate(
    *,
    handoff: dict[str, Any],
    resource_boundary: dict[str, Any],
    board_boundary: dict[str, Any],
    core_score_termination_gate: dict[str, Any],
    protocol_adaptation: dict[str, Any],
) -> dict[str, Any]:
    manual_action = _dict(handoff.get("manual_action_required"))
    no_write_policy = _dict(resource_boundary.get("no_write_policy"))
    anti_bloat_gate = _dict(protocol_adaptation.get("anti_protocol_bloat_gate"))
    trace_rows = [
        _trace_row(
            trace_id="basis_to_stage_route",
            source_fields={
                "current_basis_refs": handoff.get("current_basis_refs"),
                "stage_decision": core_score_termination_gate.get("stage_decision"),
                "route_event": handoff.get("route_event"),
                "next_route": handoff.get("next_route"),
            },
        ),
        _trace_row(
            trace_id="resource_boundary_to_no_write",
            source_fields={
                "forbidden_basis": resource_boundary.get("forbidden_basis"),
                "resource_no_write_policy": no_write_policy,
                "board_can_generate_field_evidence": board_boundary.get(
                    "can_generate_field_evidence"
                ),
                "board_can_write_to_actuator": board_boundary.get("can_write_to_actuator"),
                "board_can_write_to_release_gate": board_boundary.get(
                    "can_write_to_release_gate"
                ),
            },
            false_fields=[
                "board_can_generate_field_evidence",
                "board_can_write_to_actuator",
                "board_can_write_to_release_gate",
            ],
        ),
        _trace_row(
            trace_id="manual_action_to_resume_evidence",
            source_fields={
                "required": manual_action.get("required"),
                "source_env_var": manual_action.get("source_env_var"),
                "action": manual_action.get("action"),
                "validation_command": manual_action.get("validation_command"),
                "resume_evidence": manual_action.get("resume_evidence"),
            },
        ),
        _trace_row(
            trace_id="protocol_adaptation_to_anti_bloat",
            source_fields={
                "adaptation_status": protocol_adaptation.get("adaptation_status"),
                "selected_rules": protocol_adaptation.get("selected_rules"),
                "deferred_rules": protocol_adaptation.get("deferred_rules"),
                "anti_protocol_bloat_gate_status": anti_bloat_gate.get("gate_status"),
            },
        ),
    ]
    missing_rows = [row for row in trace_rows if row["link_status"] != "linked"]
    score = round((len(trace_rows) - len(missing_rows)) / len(trace_rows), 3)
    blockers = [
        f"{row['trace_id']}_missing_link"
        for row in missing_rows
    ]
    return {
        "gate_id": "R8u177_minimum_recovery_traceability_gate",
        "gate_status": (
            "minimum_recovery_traceability_pass"
            if not missing_rows
            else "minimum_recovery_traceability_incomplete"
        ),
        "decision_log_status": (
            "decision_log_minimum_recovery_route_recorded"
            if not missing_rows
            else "decision_log_minimum_recovery_route_incomplete"
        ),
        "traceability_status": (
            "traceability_minimum_recovery_route_recorded"
            if not missing_rows
            else "traceability_minimum_recovery_route_incomplete"
        ),
        "traceability_score": score,
        "trace_rows": trace_rows,
        "missing_link_count": len(missing_rows),
        "blockers": blockers,
        "scope_boundary": "recovery_route_trace_only_not_full_project_traceability_matrix",
        "can_replace_full_traceability_matrix": False,
        "evidence_level": "governance_recovery_trace_not_field_evidence",
        "can_generate_field_evidence": False,
        "can_resume_model_chain": False,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
        "field_claim_upgrade_allowed": False,
    }


def _trace_row(
    *,
    trace_id: str,
    source_fields: dict[str, Any],
    false_fields: list[str] | None = None,
) -> dict[str, Any]:
    false_field_set = set(false_fields or [])
    missing_fields = [
        field
        for field, value in source_fields.items()
        if (value is not False if field in false_field_set else not _has_value(value))
    ]
    return {
        "trace_id": trace_id,
        "source_fields": source_fields,
        "link_status": "linked" if not missing_fields else "missing_link",
        "missing_fields": missing_fields,
    }


def _route_alignment(
    manifest: dict[str, Any],
    handoff: dict[str, Any],
    resource_boundary: dict[str, Any],
) -> tuple[float, list[str]]:
    expected = {
        "latest_stage_boundary_external_action_board_machine_handoff_route_event": handoff.get(
            "route_event"
        ),
        "latest_stage_boundary_external_action_board_machine_handoff_next_route": handoff.get(
            "next_route"
        ),
        "latest_stage_boundary_external_action_board_machine_handoff_next_route_source_env_var": handoff.get(
            "next_route_source_env_var"
        ),
        "latest_stage_boundary_external_action_board_machine_handoff_next_route_validation_command": handoff.get(
            "next_route_validation_command"
        ),
        "latest_stage_boundary_external_action_board_machine_handoff_manual_action_required": _dict(
            handoff.get("manual_action_required")
        ).get("required"),
        "latest_stage_boundary_external_action_board_machine_handoff_current_basis_refs": handoff.get(
            "current_basis_refs"
        ),
        "latest_stage_boundary_external_action_board_machine_handoff_not_current_basis_refs": handoff.get(
            "not_current_basis_refs"
        ),
        "latest_stage_boundary_external_action_board_resource_boundary_forbidden_basis": (
            resource_boundary.get("forbidden_basis")
        ),
    }
    issues = [
        key
        for key, value in expected.items()
        if manifest.get(key) != value
    ]
    return (1.0 if not issues else 0.0), issues


def _validation_command_exists(project_root: Path, command: str) -> tuple[float, list[str]]:
    command_path = _extract_existing_command_path(project_root, command)
    if command_path is None:
        return 0.0, [f"missing_validation_command:{command}"]
    return 1.0, []


def _manifest_pointer_freshness(
    project_root: Path,
    manifest: dict[str, Any],
) -> tuple[float, list[str]]:
    pointer_keys = [
        "latest_stage_boundary_external_action_board",
        "latest_stage_boundary_external_action_board_report",
    ]
    missing = [
        key
        for key in pointer_keys
        if not _path_exists(project_root, str(manifest.get(key, "")))
    ]
    return (1.0 if not missing else 0.0), missing


def _manual_action_integrity(manual_action: dict[str, Any]) -> tuple[float, list[str]]:
    if manual_action.get("required") is not True:
        return 1.0, []
    required = ["actor", "source_env_var", "action", "validation_command", "resume_evidence"]
    missing = [field for field in required if not _has_value(manual_action.get(field))]
    return (1.0 if not missing else 0.0), [f"manual_action_missing:{field}" for field in missing]


def _basis_boundary_integrity(handoff: dict[str, Any]) -> tuple[float, list[str]]:
    current_basis = handoff.get("current_basis_refs", [])
    not_current_basis = handoff.get("not_current_basis_refs", [])
    required_rejections = ["synthetic", "template", "literature"]
    issues: list[str] = []
    if not isinstance(current_basis, list) or not current_basis:
        issues.append("current_basis_refs_empty")
    if not isinstance(not_current_basis, list) or not not_current_basis:
        issues.append("not_current_basis_refs_empty")
    for required in required_rejections:
        if not any(required in str(item) for item in not_current_basis):
            issues.append(f"not_current_basis_missing:{required}")
    return (1.0 if not issues else 0.0), issues


def _resource_boundary_integrity(
    resource_boundary: dict[str, Any],
    stage_boundary_external_action_board: dict[str, Any],
) -> tuple[float, list[str]]:
    forbidden = resource_boundary.get("forbidden_basis", [])
    required_forbidden = [
        "template_rows_as_field_evidence",
        "synthetic_rows_as_field_evidence",
        "literature_only_rows_as_field_evidence",
    ]
    issues = [
        f"forbidden_basis_missing:{item}"
        for item in required_forbidden
        if item not in forbidden
    ]
    resource_gate = _dict(stage_boundary_external_action_board.get("resource_boundary_gate"))
    if resource_gate.get("resource_boundary_stage_pass") is not True:
        issues.append("resource_boundary_gate_not_passed")
    return (1.0 if not issues else 0.0), issues


def _no_write_integrity(
    handoff: dict[str, Any],
    resource_boundary: dict[str, Any],
    board_boundary: dict[str, Any],
) -> tuple[float, list[str]]:
    no_write_policy = _dict(resource_boundary.get("no_write_policy"))
    expected_false = [
        ("handoff.can_generate_field_evidence", handoff.get("can_generate_field_evidence")),
        ("handoff.can_write_to_actuator", handoff.get("can_write_to_actuator")),
        ("handoff.can_write_to_release_gate", handoff.get("can_write_to_release_gate")),
        ("resource.can_generate_field_evidence", no_write_policy.get("can_generate_field_evidence")),
        ("resource.can_write_to_actuator", no_write_policy.get("can_write_to_actuator")),
        ("resource.can_write_to_release_gate", no_write_policy.get("can_write_to_release_gate")),
        ("board.can_generate_field_evidence", board_boundary.get("can_generate_field_evidence")),
        ("board.can_write_to_actuator", board_boundary.get("can_write_to_actuator")),
        ("board.can_write_to_release_gate", board_boundary.get("can_write_to_release_gate")),
    ]
    issues = [name for name, value in expected_false if value is not False]
    if handoff.get("no_write_boundary_preserved") is not True:
        issues.append("handoff.no_write_boundary_preserved")
    return (1.0 if not issues else 0.0), issues


def _subagent_orchestration_integrity(probe: dict[str, Any]) -> tuple[float, list[str]]:
    if not probe:
        return 0.0, ["subagent_orchestration_probe_missing"]

    issues: list[str] = []
    capability_probe = _dict(probe.get("capability_probe"))
    lifecycle_cleanup = _dict(probe.get("lifecycle_cleanup"))
    capability = str(probe.get("capability", ""))
    strategy = str(probe.get("strategy", ""))
    roles = probe.get("roles", [])
    allowed_capabilities = {"not_needed", "available", "unavailable"}
    allowed_strategies = {
        "not_needed",
        "read_only_audit",
        "parallel_domains",
        "sequential_worker",
        "reviewer",
        "inline_fallback",
        "user_proxy_required",
        "audit_timeout_non_blocking",
    }

    for field in ["probe_id", "probe_status", "capability", "strategy"]:
        if not _has_value(probe.get(field)):
            issues.append(f"subagent_probe_missing:{field}")
    if capability not in allowed_capabilities:
        issues.append(f"subagent_invalid_capability:{capability}")
    if strategy not in allowed_strategies:
        issues.append(f"subagent_invalid_strategy:{strategy}")

    tool_discovered = capability_probe.get("tool_discovered") is True
    spawn_attempted = capability_probe.get("spawn_attempted") is True
    if capability == "not_needed":
        if strategy != "not_needed":
            issues.append("subagent_not_needed_strategy_mismatch")
        if not _has_value(probe.get("no_spawn_reason")):
            issues.append("subagent_no_spawn_reason_missing")
        if spawn_attempted:
            issues.append("subagent_spawn_attempted_when_not_needed")
        if lifecycle_cleanup.get("open_agent_cleanup_required") is not False:
            issues.append("subagent_cleanup_required_when_not_needed")
    if capability == "available" and not (tool_discovered or spawn_attempted):
        issues.append("subagent_available_without_tool_or_spawn_evidence")

    strategies_requiring_roles = {
        "read_only_audit",
        "parallel_domains",
        "sequential_worker",
        "reviewer",
    }
    if strategy in strategies_requiring_roles and not _has_value(roles):
        if strategy == "parallel_domains":
            issues.append("subagent_parallel_strategy_without_roles")
        else:
            issues.append(f"subagent_{strategy}_strategy_without_roles")

    if spawn_attempted:
        wait_status = str(capability_probe.get("wait_status", ""))
        finished_statuses = {"returned", "timed_out", "blocked", "failed"}
        if wait_status in finished_statuses and not _has_value(lifecycle_cleanup):
            issues.append("subagent_lifecycle_cleanup_missing_after_spawn")
    if probe.get("can_delegate_goal_completion") is not False:
        issues.append("subagent_goal_delegation_boundary_not_false")
    if probe.get("can_generate_field_evidence") is not False:
        issues.append("subagent_field_evidence_boundary_not_false")

    return (1.0 if not issues else 0.0), issues


def _change_inventory(
    project_root: Path,
    manifest: dict[str, Any],
    handoff: dict[str, Any],
) -> list[dict[str, str]]:
    items = [
        (
            str(manifest.get("latest_stage_boundary_external_action_board", "")),
            "stage_boundary_board",
        ),
        (
            str(manifest.get("latest_stage_boundary_external_action_board_report", "")),
            "stage_boundary_report",
        ),
        (str(handoff.get("next_route_validation_command", "")), "validation_command"),
        ("deliverables/manifest.json", "manifest"),
    ]
    return [
        {
            "path": path,
            "role": role,
            "status": "exists" if _path_exists(project_root, path) else "missing",
        }
        for path, role in items
    ]


def _audit_status(*, stage_pass: bool, route_event: str) -> str:
    if stage_pass and route_event == "external_activation_wait":
        return "recovery_integrity_pass_waiting_for_real_external_input"
    if stage_pass and route_event == "model_chain_resume_candidate_ready":
        return "recovery_integrity_pass_ready_for_downstream_review"
    if stage_pass:
        return "recovery_integrity_pass_needs_stage_review"
    return "recovery_integrity_failed_repair_before_next_route"


def _extract_existing_command_path(project_root: Path, command: str) -> Path | None:
    for token in command.split():
        cleaned = token.strip().strip("'\"")
        if not cleaned or cleaned.startswith("-"):
            continue
        candidate = project_root / cleaned
        if candidate.exists() and candidate.is_file():
            return candidate
    return None


def _path_exists(project_root: Path, path: str) -> bool:
    if not path:
        return False
    candidate = project_root / path
    return candidate.exists()


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _has_value(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, dict, tuple, set)):
        return len(value) > 0
    return True

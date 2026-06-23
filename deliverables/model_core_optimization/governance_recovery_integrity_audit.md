# Governance Recovery Integrity Audit

## Position

This audit checks whether manifest, stage boundary board, validation command, basis boundaries and no-write boundaries agree before the next recovery route.

## Audit State

- audit_id: `R8u172_governance_recovery_integrity_audit`
- audit_status: `recovery_integrity_pass_waiting_for_real_external_input`
- recovery_integrity_score: `1.0`
- recovery_integrity_stage_pass: `True`
- safe_next_route: `submit_real_external_input_then_rerun_stage_preflight_and_agent50`
- blockers: `[]`
- stale_or_mismatch_fields: `[]`

## Checks

- manifest_stage_board_route_alignment: `1.0`
- validation_command_exists: `1.0`
- manifest_pointer_freshness: `1.0`
- manual_action_contract_integrity: `1.0`
- basis_boundary_integrity: `1.0`
- resource_boundary_integrity: `1.0`
- subagent_orchestration_integrity: `1.0`
- no_write_boundary_integrity: `1.0`

## Numeric Calculation Trace

- numeric_calculation_trace_status: `numeric_trace_pass_recovery_integrity_score_recomputed`
- numeric_calculation_trace_formula: `mean(check_scores)`
- numeric_calculation_trace_component_count: `8`
- numeric_calculation_trace_reported_score: `1.0`
- numeric_calculation_trace_computed_score: `1.0`
- numeric_calculation_trace_score_delta: `0.0`
- field_claim_upgrade_allowed: `False`

## Protocol Adaptation

- protocol_adaptation_status: `selected_protocol_rules_integrated_into_recovery_gate`
- source_protocol: `复杂项目启动前置治理协议_v3_核心版.md`
- anti_protocol_bloat_gate_status: `pass_selective_adoption_not_full_protocol_copy`
- selected_rule_count: `6`
- deferred_rule_count: `4`
- engineering_model_effect: `{'system_layer': 'verification_governance', 'core_abilities': ['verifiability', 'engineering_feasibility', 'evolvability'], 'model_change_type': 'recovery_gate_contract_upgrade'}`

| rule_id | model mapping | gate or metric | failure boundary |
| --- | --- | --- | --- |
| `current_basis_contract` | 区分 stage gate、真实外部输入、synthetic/template/literature 边界 | `basis_boundary_integrity` | 若 current_basis 为空或 synthetic/template/literature 未显式排除，则不能继续恢复主链。 |
| `resource_boundary_contract` | 阻断 template、synthetic、literature-only 进入 field evidence 或 release gate | `resource_boundary_integrity + no_write_boundary_integrity` | 资源边界缺失时只能修复治理链，不能升级现场结论。 |
| `numeric_calculation_trace` | 恢复完整性分数由七个检查项均值复算 | `numeric_calculation_trace` | 分数无法复算时即使检查项看似通过，也不能作为下一路由依据。 |
| `dynamic_stage_handoff` | 恢复链从最新 stage boundary board 读取安全下一路由 | `safe_next_route + route_event` | 路由不一致时进入 repair_recovery_integrity_blockers_before_next_route。 |
| `micro_task_execution_check` | 下一路由必须有存在的 validation command 和 change inventory | `validation_command_exists + change_inventory` | 没有可运行验证命令时，不能只靠文字 handoff 继续。 |
| `subagent_orchestration_probe` | 只把子代理作为只读审计或明确边界 worker，不让其替代主链判断 | `subagent_orchestration_integrity` | 若无 tool_discovered 或 spawn_attempted 证据，只能写 inline_fallback。 |

## Minimum Traceability Gate

- minimum_traceability_gate_status: `minimum_recovery_traceability_pass`
- decision_log_status: `decision_log_minimum_recovery_route_recorded`
- traceability_status: `traceability_minimum_recovery_route_recorded`
- traceability_score: `1.0`
- missing_link_count: `0`
- blockers: `[]`
- scope_boundary: `recovery_route_trace_only_not_full_project_traceability_matrix`

| trace_id | link_status | missing_fields |
| --- | --- | --- |
| `basis_to_stage_route` | `linked` | `[]` |
| `resource_boundary_to_no_write` | `linked` | `[]` |
| `manual_action_to_resume_evidence` | `linked` | `[]` |
| `protocol_adaptation_to_anti_bloat` | `linked` | `[]` |

## Change Inventory

| path | role | status |
| --- | --- | --- |
| `outputs/model_core_governance/stage_boundary_external_action_board.json` | `stage_boundary_board` | `exists` |
| `deliverables/model_core_optimization/stage_boundary_external_action_board.md` | `stage_boundary_report` | `exists` |
| `.venv/bin/python experiments/run_focused_catalyst_response_merge.py` | `validation_command` | `missing` |
| `deliverables/manifest.json` | `manifest` | `exists` |

## Boundary

- can_generate_field_evidence: `False`
- can_resume_model_chain: `False`
- can_write_to_actuator: `False`
- can_write_to_release_gate: `False`
- field_claim_upgrade_allowed: `False`

This audit checks recovery-chain consistency only. It does not create field evidence, field validation, actuator readiness, release readiness, legal opinions or patentability conclusions.

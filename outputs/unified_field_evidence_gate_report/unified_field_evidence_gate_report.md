# 统一 Field Evidence Gate 报告

- 状态：`unified_gate_ready_blocking_field_claim_upgrade`
- 统一证据记录数：5
- gate 来源合并覆盖率：1.0
- source_basis_completion_rate（Agent59 原始任务完成率）：1.0
- citation_detail_completion_rate（统一 gate 补充后的文献细节率）：1.0
- source_basis_parameter_boundary_coverage：1.0
- effective_literature_traceability：1.0
- field_supported_edge_ratio：0.0
- claim_basis_promotion_gate_status：claim_basis_promotion_blocked_until_field_validation
- promotion_decision_count：5
- ready_promotion_count：0
- blocked_promotion_count：5
- field_import_pass：False
- field_replay_evidence_chain_pass：False
- soft_sensor_field_holdout_gate_pass：False
- can_emit_field_claim_upgrade：False
- can_write_to_release_gate：False

## 下一步

- `R2_agent48_51_54_observation_contract_merge`：合并稀疏布点、催化剂代理与软传感观测矩阵合同
- 原因：field evidence gate 已统一且 source_basis 细节已补齐；下一步回到观测基础链路提升 Agent48/51/54 联动。
- 禁止事项：不能仅增加传感器数量，必须保留成本、拓扑和 field label 边界。

## 统一记录

### FVQ01 真实传感漂移记录

- evidence_stage：`synthetic_baseline_field_validation_required`
- supporting_entries：kb_sensor_limited_release_evidence
- replay_gate_ids：G6_1_field_origin, G6_2_timestamp_schema_ready, G6_3_batch_linkage_complete
- source_basis_present：True
- citation_detail_complete：True
- detail_library_complete：True
- blockers：failed_replay_gate:G6_1_field_origin, failed_soft_sensor_gate:SFG0_field_holdout_origin, failed_soft_sensor_gate:SFG5_weak_target_coverage, field_origin_not_verified, field_replay_evidence_chain_not_passed, field_replay_import_not_passed, real_field_package_not_imported

### FVQ02 离线放行标签

- evidence_stage：`synthetic_baseline_field_validation_required`
- supporting_entries：kb_sensor_limited_release_evidence
- replay_gate_ids：G6_1_field_origin, G6_2_timestamp_schema_ready, G6_3_batch_linkage_complete
- source_basis_present：True
- citation_detail_complete：True
- detail_library_complete：True
- blockers：failed_replay_gate:G6_1_field_origin, failed_soft_sensor_gate:SFG0_field_holdout_origin, failed_soft_sensor_gate:SFG5_weak_target_coverage, field_origin_not_verified, field_replay_evidence_chain_not_passed, field_replay_import_not_passed, real_field_package_not_imported

### FVQ03 低浓度目标物检测限

- evidence_stage：`synthetic_baseline_field_validation_required`
- supporting_entries：kb_sensor_limited_release_evidence
- replay_gate_ids：G6_1_field_origin, G6_2_timestamp_schema_ready, G6_3_batch_linkage_complete
- source_basis_present：True
- citation_detail_complete：True
- detail_library_complete：True
- blockers：failed_replay_gate:G6_1_field_origin, failed_soft_sensor_gate:SFG0_field_holdout_origin, failed_soft_sensor_gate:SFG5_weak_target_coverage, field_origin_not_verified, field_replay_evidence_chain_not_passed, field_replay_import_not_passed, real_field_package_not_imported

### R4F04 R4 guardrail 催化剂代理不确定现场验证

- evidence_stage：`synthetic_baseline_field_validation_required`
- supporting_entries：R4_control_guardrail_failure_backpropagation
- replay_gate_ids：G6_1_field_origin, G6_2_timestamp_schema_ready, G6_3_batch_linkage_complete, G6_7_false_positive_cost
- source_basis_present：True
- citation_detail_complete：True
- detail_library_complete：False
- blockers：failed_replay_gate:G6_1_field_origin, failed_soft_sensor_gate:SFG0_field_holdout_origin, failed_soft_sensor_gate:SFG5_weak_target_coverage, field_origin_not_verified, field_replay_evidence_chain_not_passed, field_replay_import_not_passed, real_field_package_not_imported

### R4F05 R4 guardrail 水力延迟与池容执行验证

- evidence_stage：`synthetic_baseline_field_validation_required`
- supporting_entries：R4_control_guardrail_failure_backpropagation
- replay_gate_ids：G6_1_field_origin, G6_2_timestamp_schema_ready, G6_3_batch_linkage_complete, G6_6_latency_action_margin
- source_basis_present：True
- citation_detail_complete：True
- detail_library_complete：False
- blockers：failed_replay_gate:G6_1_field_origin, failed_soft_sensor_gate:SFG0_field_holdout_origin, failed_soft_sensor_gate:SFG5_weak_target_coverage, field_origin_not_verified, field_replay_evidence_chain_not_passed, field_replay_import_not_passed, real_field_package_not_imported

## Claim Basis Promotion Gate

- gate_status：`claim_basis_promotion_blocked_until_field_validation`
- evidence_level：`claim_basis_promotion_gate_not_field_evidence`
- can_emit_field_claim_upgrade：False
- can_write_to_actuator：False
- can_write_to_release_gate：False

### FVQ01 promotion

- status：`blocked`
- allowed_promotion_level：`no_field_claim_upgrade`
- current_basis：{'evidence_stage': 'synthetic_baseline_field_validation_required', 'source_basis_traceability': 'literature_detail_complete', 'field_import': 'not_passed', 'replay_evidence_chain': 'not_passed', 'soft_sensor_holdout': 'not_passed', 'supporting_entries': ['kb_sensor_limited_release_evidence'], 'replay_gate_ids': ['G6_1_field_origin', 'G6_2_timestamp_schema_ready', 'G6_3_batch_linkage_complete']}
- not_current_basis：synthetic_rows_as_field_evidence, template_rows_as_field_evidence, literature_only_rows_as_field_evidence, formal_search_handoff_as_field_evidence, actuator_policy, release_gate_policy, patent_or_legal_conclusion
- blocked_by：failed_replay_gate:G6_1_field_origin, failed_soft_sensor_gate:SFG0_field_holdout_origin, failed_soft_sensor_gate:SFG5_weak_target_coverage, field_origin_not_verified, field_replay_evidence_chain_not_passed, field_replay_import_not_passed, real_field_package_not_imported
- next_required_gate：`import_real_field_package_then_replay_holdout_and_human_review`

### FVQ02 promotion

- status：`blocked`
- allowed_promotion_level：`no_field_claim_upgrade`
- current_basis：{'evidence_stage': 'synthetic_baseline_field_validation_required', 'source_basis_traceability': 'literature_detail_complete', 'field_import': 'not_passed', 'replay_evidence_chain': 'not_passed', 'soft_sensor_holdout': 'not_passed', 'supporting_entries': ['kb_sensor_limited_release_evidence'], 'replay_gate_ids': ['G6_1_field_origin', 'G6_2_timestamp_schema_ready', 'G6_3_batch_linkage_complete']}
- not_current_basis：synthetic_rows_as_field_evidence, template_rows_as_field_evidence, literature_only_rows_as_field_evidence, formal_search_handoff_as_field_evidence, actuator_policy, release_gate_policy, patent_or_legal_conclusion
- blocked_by：failed_replay_gate:G6_1_field_origin, failed_soft_sensor_gate:SFG0_field_holdout_origin, failed_soft_sensor_gate:SFG5_weak_target_coverage, field_origin_not_verified, field_replay_evidence_chain_not_passed, field_replay_import_not_passed, real_field_package_not_imported
- next_required_gate：`import_real_field_package_then_replay_holdout_and_human_review`

### FVQ03 promotion

- status：`blocked`
- allowed_promotion_level：`no_field_claim_upgrade`
- current_basis：{'evidence_stage': 'synthetic_baseline_field_validation_required', 'source_basis_traceability': 'literature_detail_complete', 'field_import': 'not_passed', 'replay_evidence_chain': 'not_passed', 'soft_sensor_holdout': 'not_passed', 'supporting_entries': ['kb_sensor_limited_release_evidence'], 'replay_gate_ids': ['G6_1_field_origin', 'G6_2_timestamp_schema_ready', 'G6_3_batch_linkage_complete']}
- not_current_basis：synthetic_rows_as_field_evidence, template_rows_as_field_evidence, literature_only_rows_as_field_evidence, formal_search_handoff_as_field_evidence, actuator_policy, release_gate_policy, patent_or_legal_conclusion
- blocked_by：failed_replay_gate:G6_1_field_origin, failed_soft_sensor_gate:SFG0_field_holdout_origin, failed_soft_sensor_gate:SFG5_weak_target_coverage, field_origin_not_verified, field_replay_evidence_chain_not_passed, field_replay_import_not_passed, real_field_package_not_imported
- next_required_gate：`import_real_field_package_then_replay_holdout_and_human_review`

### R4F04 promotion

- status：`blocked`
- allowed_promotion_level：`no_field_claim_upgrade`
- current_basis：{'evidence_stage': 'synthetic_baseline_field_validation_required', 'source_basis_traceability': 'literature_detail_complete', 'field_import': 'not_passed', 'replay_evidence_chain': 'not_passed', 'soft_sensor_holdout': 'not_passed', 'supporting_entries': ['R4_control_guardrail_failure_backpropagation'], 'replay_gate_ids': ['G6_1_field_origin', 'G6_2_timestamp_schema_ready', 'G6_3_batch_linkage_complete', 'G6_7_false_positive_cost']}
- not_current_basis：synthetic_rows_as_field_evidence, template_rows_as_field_evidence, literature_only_rows_as_field_evidence, formal_search_handoff_as_field_evidence, actuator_policy, release_gate_policy, patent_or_legal_conclusion
- blocked_by：failed_replay_gate:G6_1_field_origin, failed_soft_sensor_gate:SFG0_field_holdout_origin, failed_soft_sensor_gate:SFG5_weak_target_coverage, field_origin_not_verified, field_replay_evidence_chain_not_passed, field_replay_import_not_passed, real_field_package_not_imported
- next_required_gate：`import_real_field_package_then_replay_holdout_and_human_review`

### R4F05 promotion

- status：`blocked`
- allowed_promotion_level：`no_field_claim_upgrade`
- current_basis：{'evidence_stage': 'synthetic_baseline_field_validation_required', 'source_basis_traceability': 'literature_detail_complete', 'field_import': 'not_passed', 'replay_evidence_chain': 'not_passed', 'soft_sensor_holdout': 'not_passed', 'supporting_entries': ['R4_control_guardrail_failure_backpropagation'], 'replay_gate_ids': ['G6_1_field_origin', 'G6_2_timestamp_schema_ready', 'G6_3_batch_linkage_complete', 'G6_6_latency_action_margin']}
- not_current_basis：synthetic_rows_as_field_evidence, template_rows_as_field_evidence, literature_only_rows_as_field_evidence, formal_search_handoff_as_field_evidence, actuator_policy, release_gate_policy, patent_or_legal_conclusion
- blocked_by：failed_replay_gate:G6_1_field_origin, failed_soft_sensor_gate:SFG0_field_holdout_origin, failed_soft_sensor_gate:SFG5_weak_target_coverage, field_origin_not_verified, field_replay_evidence_chain_not_passed, field_replay_import_not_passed, real_field_package_not_imported
- next_required_gate：`import_real_field_package_then_replay_holdout_and_human_review`

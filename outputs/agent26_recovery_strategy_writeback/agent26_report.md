# Agent 26 恢复策略写回报告

- source_report: `outputs/agent25_time_budget_recovery/agent25_report.json`
- baseline_report: `outputs/agent22_control_baseline_update/agent22_report.json`
- summary: 恢复策略写回：conditional_target_recovery；下一轮目标进水 0.75，回退比例 0.6。
- baseline_version: `baseline_v1_replan_recovery`
- previous_baseline_version: `baseline_v1_replan`
- writeback_mode: `conditional_target_recovery`
- selected_candidate_id: `stagger_validation_overlap`
- next_intake_fraction: `0.75`
- fallback_intake_fraction: `0.6`
- expected_time_budget_usage: `0.884`
- expected_validation_staff_usage: `0.394`

## 恢复控制策略

- enabled: `True`
- target_intake_fraction: `0.75`
- fallback_intake_fraction: `0.6`
- queue_policy: `source_order`
- scenario_sequence: `['matrix_shock', 'catalyst_deactivation', 'matrix_shock', 'catalyst_deactivation', 'oxidant_limitation', 'oxidant_limitation']`
- required_post_campaign_checks: `['CampaignTelemetryAgent', 'PostReplanReplayAgent', 'RecoveryRampAgent']`
- fallback_triggers: `['acceptance_passed is false', 'time_budget_usage >= 0.90', 'validation_staff_usage >= 0.90', 'campaign_time_budget bottleneck returns', 'new catalyst_inventory or oxidant_stock bottleneck appears']`
- execution_requirements: `['保持 selected_queue_policy 原队列顺序。', '将旁路验证、暂存等待和回流观察错峰并行。', '每个长验证批次最多折叠 30 min 总占用时间。', '不得取消放行门、副产物和催化剂寿命慢证据。']`
- validation_overlap_rule: `{'overlap_fraction_of_validation_minutes': 0.35, 'max_overlap_min_per_batch': 30, 'projected_elapsed_reduction_min': 90.2}`

## 写回规则

- load_control_policy: `{'protected_intake_fraction': 0.75, 'normalization_rule': '在执行恢复控制策略且 campaign 后遥测未触发瓶颈时，允许按目标进水比例运行；若验收失败或时间预算超限，立即回退到 fallback_intake_fraction。', 'load_controls': ['保护性进水上限 0.45', '拒绝新增高风险进水', '连续催化剂压力批次禁止排队'], 'fallback_intake_fraction': 0.6, 'conditional_recovery_enabled': True, 'conditional_recovery_strategy': 'stagger_validation_overlap'}`
- writeback_rules: `{'stable_campaigns_required_for_ramp': 2, 'ramp_step': 0.15, 'replan_on_acceptance_failure': True, 'replan_on_ready_campaign_slip_gt': 1, 'recovery_strategy_writeback': True, 'target_recovery_enabled': True, 'selected_recovery_candidate_id': 'stagger_validation_overlap', 'fallback_intake_fraction': 0.6, 'post_recovery_replay_required': True, 'post_recovery_ramp_recheck_required': True, 'replan_on_time_budget_usage_gte': 0.9, 'replan_on_validation_staff_usage_gte': 0.9}`
- guardrails: `{'max_transition_intake_fraction': 0.75, 'latest_safe_ready_campaign': 3, 'mandatory_replan_thresholds': ['scenario_risk >= 0.55', 'adjusted_ready_campaign slips by more than 1 campaign', 'protected_intake_fraction <= 0.45', '阶段验收失败', 'time_budget_usage >= 0.90 under recovery strategy', 'validation_staff_usage >= 0.90 under recovery strategy', 'campaign_time_budget bottleneck returns after staggered validation overlap'], 'dominant_worst_case': 'combined_delay_high_intake'}`
- runtime_recovery_override: `{'queue_policy': 'source_order', 'preserve_replanned_order': True, 'selected_recovery_candidate_id': 'stagger_validation_overlap', 'scenario_sequence': ['matrix_shock', 'catalyst_deactivation', 'matrix_shock', 'catalyst_deactivation', 'oxidant_limitation', 'oxidant_limitation']}`

## 建议

- 下一轮在线控制使用 baseline_v1_replan_recovery。
- 按 stagger_validation_overlap 执行恢复策略，目标进水比例 0.75，回退比例 0.6。
- campaign 后必须重新运行遥测桥接、回放验证和恢复爬坡复核。
- 若触发任一 fallback trigger，立即回退到 fallback_intake_fraction 并重新执行时间预算恢复方案选择。
# 多设施协同控制 Replay-Ready 离线评估

- replay_evaluation_status：`synthetic_replay_evaluation_ready_needs_field_replay`
- replay_case_count：`6`
- joint_action_accuracy：`0.667`
- mean_reward_regret：`0.055`
- protective_false_positive_rate：`0.167`
- guardrail_aware_joint_action_accuracy：`1.0`
- guardrail_aware_mean_reward_regret：`0.0`
- guardrail_aware_false_positive_action_cost：`0.0`
- field_replay_coverage：`0.0`
- catalyst_proxy_summary_status：`field_proxy_holdout_coverage_gaps`
- catalyst_proxy_scoreable_batch_count：`0`
- catalyst_proxy_field_validation_pass：`False`
- pressure_headloss_boundary_consumed：`True`
- pressure_headloss_candidate_count：`3`
- pressure_headloss_blocked_guardrail_case_count：`2`
- pressure_headloss_can_relax_control_guardrail：`False`
- control_policy_baseline_comparison_status：`synthetic_control_policy_baseline_comparison_ready_needs_field_replay`
- control_policy_baseline_strategy_count：`6`
- agent52_replay_export_status：`agent52_replay_export_ready_synthetic_only`
- agent52_replay_export_row_count：`6`
- can_write_to_actuator：`False`

## Replay Schema

| 字段 | 说明 |
| --- | --- |
| `batch_id` | state-action-reward replay 必需字段 |
| `timestamp_min` | state-action-reward replay 必需字段 |
| `scenario` | state-action-reward replay 必需字段 |
| `facility_state_vector` | state-action-reward replay 必需字段 |
| `available_node_modalities` | state-action-reward replay 必需字段 |
| `missingness_mask` | state-action-reward replay 必需字段 |
| `policy_action_id` | state-action-reward replay 必需字段 |
| `expert_action_id` | state-action-reward replay 必需字段 |
| `reward_by_action` | state-action-reward replay 必需字段 |
| `observed_reward` | state-action-reward replay 必需字段 |
| `next_state_summary` | state-action-reward replay 必需字段 |
| `lab_label` | state-action-reward replay 必需字段 |
| `operator_override` | state-action-reward replay 必需字段 |
| `catalyst_proxy_summary_status` | state-action-reward replay 必需字段 |
| `catalyst_proxy_validation_pass` | state-action-reward replay 必需字段 |
| `catalyst_proxy_scoreable_batch_count` | state-action-reward replay 必需字段 |
| `pressure_headloss_candidate_pool_status` | state-action-reward replay 必需字段 |
| `pressure_headloss_candidate_ids` | state-action-reward replay 必需字段 |
| `pressure_headloss_control_boundary` | state-action-reward replay 必需字段 |
| `pressure_source_conflict_count` | state-action-reward replay 必需字段 |
| `resolved_pressure_source_conflict_count` | state-action-reward replay 必需字段 |
| `unresolved_pressure_source_conflict_count` | state-action-reward replay 必需字段 |
| `pressure_source_resolution_record_count` | state-action-reward replay 必需字段 |
| `pressure_source_conflict_requires_operator_review` | state-action-reward replay 必需字段 |
| `data_origin` | state-action-reward replay 必需字段 |

## Synthetic Replay Cases

| Case | Scenario | Baseline Policy | R3b Policy | Expert | Baseline Regret | R3b Regret | False Positive Cost |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `R0` | matrix_shock_visible | `J0_matrix_shock_equalize_and_recycle` | `J0_matrix_shock_equalize_and_recycle` | `J0_matrix_shock_equalize_and_recycle` | `0.0` | `0.0` | `0.0` |
| `R1` | reaction_completion_lag | `J1_reaction_completion_recovery` | `J1_reaction_completion_recovery` | `J1_reaction_completion_recovery` | `0.0` | `0.0` | `0.0` |
| `R2` | catalyst_uncertain_low_proxy | `J2_catalyst_protection_before_regeneration` | `J4_safe_low_cost_standby` | `J4_safe_low_cost_standby` | `0.177` | `0.0` | `0.18` |
| `R3` | polishing_release_risk | `J3_polishing_and_release_gate` | `J3_polishing_and_release_gate` | `J3_polishing_and_release_gate` | `0.0` | `0.0` | `0.0` |
| `R4` | clean_but_low_field_evidence | `J4_safe_low_cost_standby` | `J4_safe_low_cost_standby` | `J4_safe_low_cost_standby` | `0.0` | `0.0` | `0.0` |
| `R5` | hydraulic_delay_violation | `J0_matrix_shock_equalize_and_recycle` | `J3_polishing_and_release_gate` | `J3_polishing_and_release_gate` | `0.153` | `0.0` | `0.0` |

## Agent49 Writeback Boundary

- allowed_writeback：`['reward_prior', 'replay_schema', 'offline_metric_contract']`
- blocked_writeback：`['actuator_policy', 'release_gate_policy', 'online_MARL_training']`
- policy_effect：`keep_agent49_synthetic_policy_block`

## Control Policy Baseline Comparison

| Strategy | Accuracy | Mean Regret | P95 Regret | False Positive Cost | Release Mismatch | Unsafe Rate |
| --- | --- | --- | --- | --- | --- | --- |
| `agent49_policy` | `0.667` | `0.055` | `0.177` | `0.166` | `0.0` | `0.167` |
| `guardrail_aware_policy` | `1.0` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` |
| `safe_standby_rule` | `0.333` | `0.121` | `0.245` | `0.182` | `0.0` | `0.0` |
| `release_first_rule` | `0.333` | `0.001` | `0.006` | `0.0` | `0.667` | `0.0` |
| `deterministic_random_action_baseline` | `0.5` | `0.096` | `0.265` | `0.193` | `0.0` | `0.0` |
| `expert_upper_bound` | `1.0` | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` |

### Baseline Delta Summary

- guardrail_vs_agent49_accuracy_gain：`0.333`
- guardrail_vs_agent49_mean_regret_delta：`0.055`
- guardrail_vs_agent49_false_positive_cost_delta：`0.166`
- guardrail_vs_release_first_mismatch_delta：`0.667`
- guardrail_vs_safe_standby_mean_reward_delta：`0.121`
- guardrail_vs_random_regret_delta：`0.096`

### Baseline Boundary

- `cannot prove deployed control performance from synthetic replay`
- `cannot prove patentability or inventiveness`
- `cannot write actuator policy`
- `cannot write release gate policy`
- `cannot replace operator review or field holdout`

## Agent52 Replay Export Work Package

- work_package_id：`R8U25_AGENT52_REPLAY_EXPORT_WORK_PACKAGE`
- export_status：`agent52_replay_export_ready_synthetic_only`
- all_rows_field_origin：`False`
- can_route_to_r8p_candidate_rows：`False`
- can_create_field_evidence_by_export_only：`False`
- expected_output_files：`['agent52_replay_export_manifest.json', 'agent52_replay_table.csv', 'agent52_replay_table.rows.json']`
- failure_boundary：Agent52 replay export supplies replay-origin action/conflict evidence only. Synthetic rows cannot become field evidence, and even field replay rows must pass R8p/R8v/operator/release gates before execution.

## Agent51 Catalyst Proxy Context

- summary_status：`field_proxy_holdout_coverage_gaps`
- ready_for_agent51_validation：`False`
- field_validation_pass：`False`
- scoreable_batch_count：`0`
- guardrail_mode：`agent51_holdout_coverage_gaps_keep_catalyst_guardrail`

## Pressure/Headloss Replay Boundary

- pool_status：`pressure_headloss_candidate_pool_ready_needs_field_topology_and_labels`
- candidate_ids：`['N3_catalyst_bed:pressure_drop_kPa', 'N3_catalyst_bed:headloss_kPa_per_m', 'N3_catalyst_bed:flow_normalized_pressure_residual']`
- consumed_by_agent52：`True`
- field_validation_required：`True`
- control_boundary：pressure/headloss may shape hydraulic and catalyst-state explanation priors, but cannot relax recycle/catalyst guardrails or promote actuator use without field topology, matched lab labels and missingness replay.

## 结论

- 把 Agent49 的候选协同动作接入 state-action-reward replay schema，而不是直接训练在线 MARL。
- 先用 replay 计算 joint_action_accuracy、reward_regret、误保护成本和策略蒸馏准确度，再决定是否进入人工复核的执行器候选。
- 将 highest_regret_cases 写回 Agent49 reward_prior，优先修正高 regret 场景的动作排序。
- 下一步必须准备真实多节点 sensor/lab/operation/action replay；synthetic replay 只能证明 schema 和指标可运行。
- 优先复核保护性误触发案例：[{'batch_id': 'R2', 'scenario': 'catalyst_uncertain_low_proxy', 'policy_action_id': 'J2_catalyst_protection_before_regeneration', 'false_positive_action_cost': 0.18}]。
- R3c 已形成 guardrail-aware replay 对照：保留 baseline 指标，同时用 R3b policy 检查 regret 与误保护成本是否下降。
- Agent51 catalyst proxy field holdout 未过线时，Agent52 只能更新 replay/reward prior，不能让 Agent49 放松催化剂不确定性保护。
- R8d 已把 pressure/headloss 控制边界纳入 Agent52 replay；下一步需要用压降/水头损失时序、床层几何和 matched lab labels 验证该边界，否则仍不能解除回流或催化剂 guardrail。
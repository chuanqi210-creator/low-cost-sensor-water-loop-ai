# R2 观测契约合并报告

- 状态：`synthetic_observation_contract_ready_needs_field_topology_proxy_labels_and_missingness`
- 推荐 contract：`budget_rebalanced_proxy_contract`
- weak_state_coverage：0.3 -> 0.58
- catalyst_observability_gain：0.28
- weak_axis_repair_status：`agent48_catalyst_axis_requires_proxy_patch_and_field_label`
- weak_axis_repair_score：0.983
- agent48_hidden_state_ledger_status：`hidden_state_requirement_ledger_ready_with_gaps`
- agent48_hidden_state_ready_count：4/6
- agent48_hidden_state_minimum_patch_status：`minimum_cost_patch_requires_new_modality_or_field_label`
- agent48_hidden_state_hard_unresolved：['catalyst_activity']
- agent48_pressure_headloss_candidate_pool_status：`pressure_headloss_candidate_pool_ready_needs_field_topology_and_labels`
- agent48_pressure_headloss_candidate_count：3
- estimated_missingness_robustness_after_patch：0.727
- recommended_cost_index：5.272
- budget_pass：True
- can_write_to_release_gate：False

## 推荐合同

- contract_id：`greedy_marginal:6x10::budget_rebalanced_proxy_contract`
- added_patch_pairs：['N3_catalyst_bed_outlet:ORP_mV', 'N3_catalyst_bed_outlet:UV254_abs']
- removed_base_pairs：['N5_polishing_inlet:turbidity_NTU']
- field_repair_evidence_requirement_count：4
- contract_pairs：['N0_influent:EC_uScm', 'N1_equalization_tank:flow_Lmin', 'N2_reactor_mid:ORP_mV', 'N3_catalyst_bed_outlet:ORP_mV', 'N3_catalyst_bed_outlet:UV254_abs', 'N3_catalyst_bed_outlet:turbidity_NTU', 'N4_recirculation_loop:UV254_abs']

## 下一步

- `R3_agent49_replay_counterfactual_stress`：对 Agent49/52 做协同控制 replay 反事实压力测试
- 原因：观测契约已把 weak_state_coverage 推过 0.55 的设计门槛；下一步应检验控制策略在反事实 replay 下是否稳健。
- 禁止事项：不能训练黑箱 MARL 或写执行器；先做离线 replay、reward regret 和保护性误触发压力测试。

# R2 Agent48/51/54 观测契约合并

## 核心判断

R2 把稀疏布点、catalyst_activity 代理观测和软传感 node-modality/missingness 合同合成一个 observation contract。这一步的关键不是增加传感器数量，而是在预算约束下让弱隐藏状态可观测，并让软传感矩阵直接消费同一份观测合同。

- 状态：`synthetic_observation_contract_ready_needs_field_topology_proxy_labels_and_missingness`
- base weak_state_coverage：0.3
- proxy_enhanced_weak_state_coverage：0.58
- catalyst_observability_gain：0.28
- weak_axis_repair_status：`agent48_catalyst_axis_requires_proxy_patch_and_field_label`
- weak_axis_repair_score：0.983
- field_repair_evidence_requirement_count：4
- agent48_hidden_state_ledger_status：`hidden_state_requirement_ledger_ready_with_gaps`
- agent48_hidden_state_ready_count：4/6
- agent48_hidden_state_minimum_patch_status：`minimum_cost_patch_requires_new_modality_or_field_label`
- agent48_hidden_state_hard_unresolved：['catalyst_activity']
- agent48_pressure_headloss_candidate_pool_status：`pressure_headloss_candidate_pool_ready_needs_field_topology_and_labels`
- agent48_pressure_headloss_candidate_ids：['N3_catalyst_bed:pressure_drop_kPa', 'N3_catalyst_bed:headloss_kPa_per_m', 'N3_catalyst_bed:flow_normalized_pressure_residual']
- recommended_contract_id：`budget_rebalanced_proxy_contract`
- recommended_cost_index：5.272
- budget_pass：True
- layout_alignment_pass：True
- field_topology_ready：False
- field_proxy_labels_ready：False
- field_missingness_ready：False

## Base Layout

- layout_id：`greedy_marginal:6x10`
- base_total_cost_index：4.176
- budget_limit：5.8
- selected_pairs：['N4_recirculation_loop:UV254_abs', 'N3_catalyst_bed_outlet:turbidity_NTU', 'N2_reactor_mid:ORP_mV', 'N0_influent:EC_uScm', 'N1_equalization_tank:flow_Lmin', 'N5_polishing_inlet:turbidity_NTU']
- hidden_state_requirement_ledger_status：`hidden_state_requirement_ledger_ready_with_gaps`
- hidden_state_hard_unresolved：['catalyst_activity']
- pressure_headloss_candidate_pool_status：`pressure_headloss_candidate_pool_ready_needs_field_topology_and_labels`
- pressure_headloss_candidate_ids：['N3_catalyst_bed:pressure_drop_kPa', 'N3_catalyst_bed:headloss_kPa_per_m', 'N3_catalyst_bed:flow_normalized_pressure_residual']

## Agent48 Hidden State Requirement Rows

| Hidden State | Min Primary Score | Ready Count Basis | Hard Boundary |
| --- | ---: | --- | --- |
| `pollutant_residual` | 0.814 | soft=True, control=False | ['field_topology_and_labels_required', 'missing_required_zone:effluent'] |
| `reaction_completion` | 0.712 | soft=True, control=False | ['field_topology_and_labels_required', 'missing_required_modality:pH'] |
| `catalyst_activity` | 0.3 | soft=False, control=False | ['candidate_pool_cannot_reach_primary_axis_target', 'field_topology_and_labels_required', 'missing_required_modality:pressure_drop_kPa', 'pressure_drop_or_headloss_proxy_not_in_selected_layout'] |
| `matrix_interference` | 0.587 | soft=False, control=False | ['field_topology_and_labels_required'] |
| `hydraulic_delay` | 0.76 | soft=True, control=False | ['field_topology_and_labels_required', 'missing_required_modality:pressure_drop_kPa', 'pressure_drop_or_headloss_proxy_not_in_selected_layout'] |
| `release_or_byproduct_risk` | 0.712 | soft=True, control=False | ['field_topology_and_labels_required', 'missing_required_modality:pH', 'missing_required_zone:effluent'] |

## Contract Candidates

| Candidate | Weak state | Cost | Budget | Added | Removed | Score |
| --- | ---: | ---: | --- | --- | --- | ---: |
| `base_agent48_layout` | 0.3 | 4.176 | True | [] | [] | 0.735 |
| `full_proxy_patch_contract` | 0.72 | 6.824 | False | ['N3_catalyst_bed:pressure_drop_kPa', 'N3_catalyst_bed_outlet:ORP_mV', 'N3_catalyst_bed_outlet:UV254_abs'] | [] | 0.82 |
| `budget_rebalanced_proxy_contract` | 0.58 | 5.272 | True | ['N3_catalyst_bed_outlet:ORP_mV', 'N3_catalyst_bed_outlet:UV254_abs'] | ['N5_polishing_inlet:turbidity_NTU'] | 0.96 |

## Weak Axis Repair Records

| Patch | Repair Priority | Patch Type | Why Needed |
| --- | ---: | --- | --- |
| `N3_catalyst_bed_outlet:UV254_abs` | 0.66 | `add_modality_to_existing_node` | 床出口 UV254 与回流/床入口 UV254 组成差分，支撑活性和停留时间归一化速率残差。 |
| `N3_catalyst_bed_outlet:ORP_mV` | 0.36 | `add_modality_to_existing_node` | 床出口 ORP 与反应核心 ORP 组成氧化剂利用/衰减代理。 |
| `N3_catalyst_bed:pressure_drop_kPa` | 0.35 | `add_node_modality` | 压降用于区分催化剂活性衰减与床层堵塞/污堵。 |

## Recommended Observation Contract

- rationale：优先加入床出口 UV254/ORP 两个高价值代理补点，并替换最低边际、非核心节点的原始传感点，使 catalyst_activity 过 0.55 的同时维持预算约束。
- added_patch_pairs：['N3_catalyst_bed_outlet:ORP_mV', 'N3_catalyst_bed_outlet:UV254_abs']
- removed_base_pairs：['N5_polishing_inlet:turbidity_NTU']
- estimated_missingness_robustness_after_patch：0.727

## Soft Sensor Schema Patch

- missing_layout_terms：['layout_id', 'node_id', 'zone', 'modality', 'availability_mask', 'time_since_last_observed_min', 'grey_box_residual_prior']
- patch_target：SoftSensor training and inference feature schema

## Field Validation Requirements

- `R2_FV1_field_topology_and_installability`：final field sensor placement，tables=['site_topology', 'sensor_install_costs', 'maintenance_access']
- `R2_FV2_proxy_holdout_labels`：relaxing catalyst uncertainty block，tables=['offline_catalyst_activity_labels', 'pressure_drop_log', 'regeneration_event_log']
- `R2_FV3_node_specific_missingness_replay`：soft sensor layout holdout performance，tables=['sensor_timeseries', 'missingness_event_log', 'layout_holdout_split']
- `R2_FV4_agent48_hidden_state_requirement_patch`：resolving Agent48 hard unresolved hidden-state sensing needs，tables=['node_modality_sensor_timeseries', 'offline_lab_results', 'campaign_operation_log', 'site_topology_or_bed_geometry']

## 下一步

- `R3_agent49_replay_counterfactual_stress`：对 Agent49/52 做协同控制 replay 反事实压力测试
- 原因：观测契约已把 weak_state_coverage 推过 0.55 的设计门槛；下一步应检验控制策略在反事实 replay 下是否稳健。
- 禁止事项：不能训练黑箱 MARL 或写执行器；先做离线 replay、reward regret 和保护性误触发压力测试。

## 边界

- R2 只写 design prior 和 observation contract，不写执行器、不写 release gate。
- budget-rebalanced contract 仍需要 field topology、proxy labels 和真实 missingness replay。
- full proxy patch 是上限方案，但当前估算超预算，不能直接当成现场布点方案。

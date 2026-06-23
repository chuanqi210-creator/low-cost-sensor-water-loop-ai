# 管网布点与稀疏感知设计

- sparse_placement_status：`sparse_sensor_layout_ready_needs_field_topology`
- sparse_placement_score：`0.68`
- selected_strategy：`greedy_marginal`
- selected_strategy_score：`0.726`
- baseline_comparison_status：`sparse_baseline_comparison_ready_needs_field_topology_and_labels`
- best_vs_random_delta：`0.062`
- best_vs_cost_only_delta：`0.258`
- selected_sensor_count：`6`
- total_cost_index：`4.176`
- weak_state_coverage：`0.3`
- reconstruction_stability_score：`0.401`
- condition_number_proxy：`61.726`
- weak_axis_gap_count：`2`
- hidden_state_ledger_status：`hidden_state_requirement_ledger_ready_with_gaps`
- ready_hidden_state_count：`4/6`
- minimum_cost_patch_status：`minimum_cost_patch_requires_new_modality_or_field_label`
- pressure_headloss_candidate_pool_status：`pressure_headloss_candidate_pool_ready_needs_field_topology_and_labels`
- pressure_headloss_candidate_count：`3`
- hydraulic_path_contract_status：`hydraulic_path_contract_ready_needs_field_topology_and_release_endpoint`
- hydraulic_path_covered_stage_count：`6/6`
- recirculation_loop_observed：`True`
- final_release_gate_needs_effluent_label：`True`
- matrix_shape：`[6, 10]`

## Strategy Comparison

| Rank | Strategy | Comparable | Reconstruction | Classification | Robustness | Topology | Cost |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `1` | `greedy_marginal` | `0.726` | `0.682` | `0.628` | `0.672` | `0.768` | `1.0` |
| `2` | `classification_sspoc_proxy` | `0.694` | `0.668` | `0.698` | `0.721` | `0.429` | `1.0` |
| `3` | `reconstruction_qr_proxy` | `0.692` | `0.682` | `0.671` | `0.723` | `0.429` | `1.0` |
| `4` | `deterministic_random_baseline` | `0.664` | `0.579` | `0.652` | `0.664` | `0.536` | `1.0` |
| `5` | `topology_robust_cost_proxy` | `0.622` | `0.313` | `0.625` | `0.67` | `0.768` | `1.0` |
| `6` | `cost_only_baseline` | `0.468` | `0.251` | `0.347` | `0.481` | `0.536` | `1.0` |

## Baseline Comparison Contract

- comparison_status：`sparse_baseline_comparison_ready_needs_field_topology_and_labels`
- required_baseline_strategy_ids：`['deterministic_random_baseline', 'cost_only_baseline', 'reconstruction_qr_proxy', 'classification_sspoc_proxy', 'topology_robust_cost_proxy']`
- missing_baseline_strategy_ids：`[]`
- claim_scope_use：use these baselines to distinguish node-modality hidden-state placement from generic sparse placement, cost-only rules and random ablations
- cannot_do：['cannot prove patentability', 'cannot prove field deployment performance', 'cannot replace field topology, node-specific time series or offline hidden-state labels']

## Selected Sparse Plan

| Order | Candidate | Zone | Cost | Main Contribution |
| --- | --- | --- | --- | --- |
| `1` | `N4_recirculation_loop:UV254_abs` | `loop` | `1.012` | ['soft_sensor_reconstruction_gain', 'cost_efficiency', 'pollutant_residual_observability'] |
| `2` | `N3_catalyst_bed_outlet:turbidity_NTU` | `catalyst_bed` | `0.826` | ['cost_efficiency', 'control_latency_gain', 'fault_classification_observability'] |
| `3` | `N2_reactor_mid:ORP_mV` | `reaction_core` | `0.756` | ['cost_efficiency', 'oxidant_observability', 'reaction_completion_observability'] |
| `4` | `N0_influent:EC_uScm` | `influent` | `0.434` | ['cost_efficiency', 'matrix_interference_observability', 'control_latency_gain'] |
| `5` | `N1_equalization_tank:flow_Lmin` | `buffer` | `0.476` | ['cost_efficiency', 'control_latency_gain', 'hydraulic_observability'] |
| `6` | `N5_polishing_inlet:turbidity_NTU` | `polishing` | `0.672` | ['cost_efficiency', 'control_latency_gain', 'matrix_interference_observability'] |

## Observation Coverage

| Axis | Coverage |
| --- | --- |
| `pollutant_residual_observability` | `0.814` |
| `reaction_completion_observability` | `0.712` |
| `oxidant_observability` | `0.775` |
| `catalyst_activity_observability` | `0.3` |
| `matrix_interference_observability` | `0.851` |
| `hydraulic_observability` | `0.76` |
| `fault_classification_observability` | `0.587` |
| `control_latency_gain` | `0.837` |
| `soft_sensor_reconstruction_gain` | `0.827` |
| `cost_efficiency` | `1.0` |
| `weak_state_coverage` | `0.3` |
| `total_cost_index` | `4.176` |
| `node_diversity_count` | `6.0` |
| `modality_diversity_count` | `5.0` |

## Placement Diagnostics

- diagnostic_status：`placement_diagnostics_need_axis_patch_or_field_benchmark`
- selected_matrix_rank：`6`
- axis_span_rank_ratio：`0.667`
- layout_redundancy_score：`0.825`
- single_point_dependency_count：`4`

| Axis | Current | Target | Best Available Candidate | Recoverable |
| --- | --- | --- | --- | --- |
| `catalyst_activity_observability` | `0.3` | `0.55` | `N3_catalyst_bed_outlet:UV254_abs` | `False` |
| `fault_classification_observability` | `0.587` | `0.6` | `N4_recirculation_loop:EC_uScm` | `True` |

## Hidden State Requirement Ledger

| Hidden State | Min Primary Score | Ready For Soft Sensor | Ready For Control | Patch Status | Unresolved |
| --- | --- | --- | --- | --- | --- |
| `pollutant_residual` | `0.814` | `True` | `False` | `state_target_already_met` | ['field_topology_and_labels_required', 'missing_required_zone:effluent'] |
| `reaction_completion` | `0.712` | `True` | `False` | `state_target_already_met` | ['field_topology_and_labels_required', 'missing_required_modality:pH'] |
| `catalyst_activity` | `0.3` | `False` | `False` | `candidate_pool_patch_incomplete` | ['candidate_pool_cannot_reach_primary_axis_target', 'field_topology_and_labels_required', 'missing_required_modality:pressure_drop_kPa', 'pressure_drop_or_headloss_proxy_not_in_selected_layout'] |
| `matrix_interference` | `0.587` | `False` | `False` | `candidate_pool_patch_available` | ['field_topology_and_labels_required'] |
| `hydraulic_delay` | `0.76` | `True` | `False` | `state_target_already_met` | ['field_topology_and_labels_required', 'missing_required_modality:pressure_drop_kPa', 'pressure_drop_or_headloss_proxy_not_in_selected_layout'] |
| `release_or_byproduct_risk` | `0.712` | `True` | `False` | `state_target_already_met` | ['field_topology_and_labels_required', 'missing_required_modality:pH', 'missing_required_zone:effluent'] |

## Minimum Cost Requirement Patch

- patch_status：`minimum_cost_patch_requires_new_modality_or_field_label`
- recommended_candidate_ids：`['N3_catalyst_bed_outlet:ORP_mV', 'N4_recirculation_loop:ORP_mV', 'N0_influent:temp_C', 'N4_recirculation_loop:EC_uScm']`
- hard_unresolved_hidden_states：`['catalyst_activity']`
- estimated_added_cost_upper_bound：`2.348`
- pressure_headloss_candidate_ids：`['N3_catalyst_bed:pressure_drop_kPa', 'N3_catalyst_bed:headloss_kPa_per_m', 'N3_catalyst_bed:flow_normalized_pressure_residual']`

## Pressure/Headloss Candidate Pool

| Candidate | Type | Target States | Cost | Required Table | Boundary |
| --- | --- | --- | ---: | --- | --- |
| `N3_catalyst_bed:pressure_drop_kPa` | `direct_low_cost_differential_pressure_sensor` | ['catalyst_activity', 'hydraulic_delay'] | `0.68` | `node_modality_sensor_timeseries` | supplemental pressure/headloss candidate only; not part of selected installed layout until field topology and installability are reviewed |
| `N3_catalyst_bed:headloss_kPa_per_m` | `derived_headloss_proxy_from_pressure_and_bed_geometry` | ['catalyst_activity', 'hydraulic_delay'] | `0.18` | `site_topology_or_bed_geometry` | supplemental pressure/headloss candidate only; not part of selected installed layout until field topology and installability are reviewed |
| `N3_catalyst_bed:flow_normalized_pressure_residual` | `grey_box_residual_proxy` | ['catalyst_activity', 'hydraulic_delay'] | `0.0` | `node_modality_sensor_timeseries + site_topology_or_bed_geometry` | supplemental pressure/headloss candidate only; not part of selected installed layout until field topology and installability are reviewed |

## Hydraulic Path Coverage Contract

- contract_status：`hydraulic_path_contract_ready_needs_field_topology_and_release_endpoint`
- can_support_soft_sensor_path_prior：`True`
- can_support_control_replay_design_prior：`True`
- can_finalize_field_deployment：`False`
- unresolved_requirements：['field_topology_and_hydraulic_path_labels_required', 'final_effluent_release_endpoint_not_directly_observed', 'pressure_drop_or_headloss_proxy_not_installed_in_selected_layout']

| Stage | Role | Covered | Direct | Proxy | Sensors | Missing Zones | Missing Modalities |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `S0_influent_matrix` 进水/基质冲击入口 | pre_treat_or_hold_before_reactor | `True` | `True` | `False` | ['N0_influent:EC_uScm'] | [] | ['turbidity_NTU', 'UV254_abs'] |
| `S1_equalization_buffer` 均质/暂存缓冲段 | hold_or_extend_retention_time | `True` | `True` | `False` | ['N1_equalization_tank:flow_Lmin'] | [] | [] |
| `S2_reaction_core` 反应核心段 | dose_adjust_or_recycle_candidate | `True` | `True` | `False` | ['N2_reactor_mid:ORP_mV'] | [] | ['pH'] |
| `S3_catalyst_bed` 催化剂/材料床段 | catalyst_guardrail_or_regeneration_candidate | `True` | `True` | `False` | ['N3_catalyst_bed_outlet:turbidity_NTU'] | [] | ['pressure_drop_kPa'] |
| `S4_recirculation_loop` 回流/循环段 | recycle_or_extend_loop_decision | `True` | `True` | `False` | ['N4_recirculation_loop:UV254_abs'] | [] | [] |
| `S5_release_boundary` 末端精处理/放行边界 | release_gate_or_hold_for_validation | `True` | `False` | `True` | ['N5_polishing_inlet:turbidity_NTU'] | ['effluent'] | ['UV254_abs', 'ORP_mV', 'pH'] |

## 结论

- 把当前传感设计从“传感器种类敏感性”升级为“节点-模态稀疏观测矩阵”，并把 node_id/zone/missingness mask 写入 field holdout。
- 优先在基质冲击、催化剂床、回流环和末端出水之间形成互补布点，而不是只在进出水各放一个点。
- 当前最高边际价值布点候选为 N4_recirculation_loop:UV254_abs，主要贡献 ['soft_sensor_reconstruction_gain', 'cost_efficiency', 'pollutant_residual_observability']。
- 下一轮布点优化应优先补 catalyst_activity_observability，当前覆盖 0.3，候选池最佳为 N3_catalyst_bed_outlet:UV254_abs。
- 隐藏状态需求账本显示 ['catalyst_activity'] 不是靠现有候选池简单加点能解决；需要把 pressure_drop/headloss、节点级 catalyst proxy 标签或床体/HRT 字段纳入现场包。
- 下一步需要真实管网/反应单元拓扑、水力停留时间、维护可达性和仪表成本，替换 synthetic topology prior。
- 水力路径合同显示当前布点只把 polishing 作为末端代理观察；若要支撑放行门，必须补 effluent 端点标签、离线 byproduct/release risk 标签和人工复核结果。
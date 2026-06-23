# Agent 48 管网布点与稀疏感知报告

- summary: 稀疏传感布点：sparse_sensor_layout_ready_needs_field_topology；选择 6 个 node-modality，策略 greedy_marginal，弱状态覆盖 0.300。
- sparse_placement_status: `sparse_sensor_layout_ready_needs_field_topology`
- selected_strategy: `greedy_marginal`
- selected_strategy_score: `0.726`
- baseline_comparison_status: `sparse_baseline_comparison_ready_needs_field_topology_and_labels`
- best_vs_random_delta: `0.062`
- best_vs_cost_only_delta: `0.258`
- weak_state_coverage: `0.3`
- reconstruction_stability_score: `0.401`
- weak_axis_gap_count: `2`
- hidden_state_ledger_status: `hidden_state_requirement_ledger_ready_with_gaps`
- ready_hidden_state_count: `4/6`
- minimum_cost_patch_status: `minimum_cost_patch_requires_new_modality_or_field_label`
- hard_unresolved_hidden_states: `['catalyst_activity']`
- pressure_headloss_candidate_pool_status: `pressure_headloss_candidate_pool_ready_needs_field_topology_and_labels`
- pressure_headloss_candidate_count: `3`
- hydraulic_path_contract_status: `hydraulic_path_contract_ready_needs_field_topology_and_release_endpoint`
- hydraulic_path_covered_stage_count: `6/6`
- recirculation_loop_observed: `True`
- final_release_gate_needs_effluent_label: `True`
- total_cost_index: `4.176`

## 生成文件

- sensor_network_sparse_placement: `deliverables/sensor_network_sparse_placement.md`
- agent48_report: `outputs/agent48_sensor_network_sparse_placement/agent48_report.md`
- sparse_placement_metrics: `outputs/sensor_network_sparse_placement/sparse_placement_metrics.json`

## 风险边界

- `field_topology_required_for_deployment`：当前布点基于 synthetic topology prior，需要真实管网/处理单元拓扑和水力停留时间校准后才能部署。
- `weak_state_observability_low`：稀疏布点对 catalyst_activity 或 matrix_interference 的观测覆盖不足。
- `placement_matrix_diagnostics_need_axis_patch_or_field_benchmark`：当前稀疏观测矩阵存在弱轴缺口、条件数偏高或单点依赖，需要补充候选轴或用真实 field topology benchmark 校准。
- `hidden_state_requirement_requires_new_modality_or_field_label`：现有候选传感器池无法用剩余预算满足部分隐藏状态需求，需要新增模态、节点级 field label 或床体/HRT 证据。
- `hydraulic_path_release_endpoint_needs_effluent_label`：当前稀疏布点覆盖了末端精处理代理段，但没有直接覆盖最终 effluent 放行端点，不能支撑 release gate。
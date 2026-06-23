# Agent 54 软传感矩阵耦合报告

- summary: 软传感矩阵耦合：synthetic_layout_aware_soft_sensor_contract_ready_needs_field_missingness；layout_contract_score=1.000，missingness_robustness=0.684。
- soft_sensor_matrix_status: `synthetic_layout_aware_soft_sensor_contract_ready_needs_field_missingness`
- missingness_robustness_score: `0.684`
- pressure_headloss_candidate_pool_status: `pressure_headloss_candidate_pool_ready_needs_field_topology_and_labels`
- pressure_headloss_candidate_count: `3`
- hydraulic_path_contract_status: `hydraulic_path_contract_ready_needs_field_topology_and_release_endpoint`
- hydraulic_path_covered_stage_count: `6/6`
- hydraulic_path_feature_variation_status: `synthetic_path_feature_variation_ready_for_layout_holdout`
- layout_holdout_status: `synthetic_layout_holdout_ready_needs_field_path_labels`
- layout_holdout_mean_mae: `0.01524`
- field_path_endpoint_label_package_status: `no_field_path_endpoint_label_package_supplied`
- field_path_endpoint_label_matched_batch_count: `0`
- hydraulic_path_final_release_gate_needs_effluent_label: `True`
- can_write_to_release_gate: `False`

## 生成文件

- soft_sensor_matrix_coupling: `/Users/chuchenqidawang/Documents/低成本传感循环式水处理智能闭环项目/deliverables/soft_sensor_matrix_coupling.md`
- agent54_report: `/Users/chuchenqidawang/Documents/低成本传感循环式水处理智能闭环项目/outputs/agent54_soft_sensor_matrix_coupling/agent54_report.md`
- soft_sensor_matrix_metrics: `/Users/chuchenqidawang/Documents/低成本传感循环式水处理智能闭环项目/outputs/soft_sensor_matrix_coupling/soft_sensor_matrix_metrics.json`
- field_path_endpoint_label_package_contract: `/Users/chuchenqidawang/Documents/低成本传感循环式水处理智能闭环项目/outputs/soft_sensor_matrix_coupling/field_path_endpoint_label_package_contract.json`
- field_path_endpoint_label_package_preflight: `/Users/chuchenqidawang/Documents/低成本传感循环式水处理智能闭环项目/outputs/soft_sensor_matrix_coupling/field_path_endpoint_label_package_preflight.json`
- field_path_endpoint_label_package_template: `/Users/chuchenqidawang/Documents/低成本传感循环式水处理智能闭环项目/outputs/soft_sensor_matrix_coupling/field_path_endpoint_label_package_template.json`

## 风险边界

- `soft_sensor_layout_features_missing`：当前软传感训练特征仍不是 layout-aware，缺 node/zone/modality/mask/layout_id 等字段。
- `node_specific_values_missing`：推理链已接入 layout_id 和 mask，但当前读数仍使用全局 modality fallback，缺节点级真实值。
- `field_missingness_replay_required`：P5 当前只能形成 synthetic layout contract，需要真实缺测、污染、延迟和维护事件 replay 才能校准。
- `pressure_headloss_candidate_schema_not_trained`：Agent54 已读取 pressure/headloss 候选池，但当前软传感训练 schema 尚未包含这些候选特征；只能作为下一轮候选通道。
- `hydraulic_path_release_endpoint_blocks_release_use`：当前软传感路径先验仍缺最终 effluent 放行端点标签，不能把 polishing 代理观察用于 release gate。
- `field_path_endpoint_label_package_required_for_field_holdout`：已有 synthetic layout holdout，但缺真实 path_stage/endpoint/node-specific field rows，不能升级为 field layout holdout。
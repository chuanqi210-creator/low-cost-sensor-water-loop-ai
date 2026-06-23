# 软传感 Node-Modality/Missingness 矩阵耦合

- soft_sensor_matrix_status：`synthetic_layout_aware_soft_sensor_contract_ready_needs_field_missingness`
- layout_id：`greedy_marginal:6x10`
- layout_contract_score：`1.0`
- missingness_robustness_score：`0.684`
- live_layout_context_status：`global_modality_fallback_used_for_layout`
- pressure_headloss_candidate_pool_status：`pressure_headloss_candidate_pool_ready_needs_field_topology_and_labels`
- pressure_headloss_candidate_count：`3`
- hydraulic_path_contract_status：`hydraulic_path_contract_ready_needs_field_topology_and_release_endpoint`
- hydraulic_path_covered_stage_count：`6/6`
- hydraulic_path_feature_variation_status：`synthetic_path_feature_variation_ready_for_layout_holdout`
- layout_holdout_status：`synthetic_layout_holdout_ready_needs_field_path_labels`
- layout_holdout_mean_mae：`0.01524`
- hydraulic_path_final_release_gate_needs_effluent_label：`True`
- can_write_to_release_gate：`False`

## Feature Tensor Contract

- tensor_axes：`['time', 'node', 'modality', 'feature_channel']`
- feature_channels：`['sensor_value', 'availability_mask', 'time_since_last_observed_min', 'data_quality_score', 'observation_axis_weight', 'hydraulic_path_stage_prior', 'grey_box_residual_prior']`
- mask_shape：`[6, 5]`
- selected_nodes：`['N0_influent', 'N1_equalization_tank', 'N2_reactor_mid', 'N3_catalyst_bed_outlet', 'N4_recirculation_loop', 'N5_polishing_inlet']`
- selected_modalities：`['EC_uScm', 'ORP_mV', 'UV254_abs', 'flow_Lmin', 'turbidity_NTU']`

## Hydraulic Path Feature Contract

- source：`Agent48.hydraulic_path_coverage_contract`
- contract_status：`hydraulic_path_contract_ready_needs_field_topology_and_release_endpoint`
- feature_terms：`['hydraulic_path_coverage_rate', 'direct_hydraulic_path_coverage_rate', 'proxy_hydraulic_path_coverage_rate', 'recirculation_loop_observed_flag', 'low_frequency_time_buffer_observed_flag', 'release_boundary_proxy_flag', 'final_effluent_direct_observed_flag', 'release_endpoint_label_missing_flag']`
- field_schema_terms：`['path_stage_id', 'hydraulic_path_role', 'stage_coverage_mask', 'direct_path_stage_coverage_mask', 'proxy_path_stage_coverage_mask', 'release_boundary_flag', 'recirculation_loop_flag', 'low_frequency_time_buffer_flag']`
- covered_stage_count：`6/6`
- recirculation_loop_observed：`True`
- final_release_gate_needs_effluent_label：`True`
- can_use_for_release_gate：`False`

## Layout Holdout Boundary

- hydraulic_path_feature_variation_ready：`True`
- layout_holdout_ready：`True`
- layout_holdout_train_layout_count：`5`
- layout_holdout_heldout_layout_count：`2`
- layout_holdout_field_boundary：synthetic layout holdout checks path-feature schema generalization only; it cannot prove field performance without path labels, node-specific values and endpoint lab labels

## Field Path/Endpoint Label Package Gate

- package_contract_id：`R8u66_field_path_endpoint_label_package_contract`
- minimum_matched_batch_count：`5`
- required_tables：`['site_topology_or_bed_geometry', 'node_modality_sensor_timeseries', 'hydraulic_path_stage_labels', 'final_effluent_endpoint_labels', 'campaign_operation_log', 'offline_lab_results']`
- preflight_status：`no_field_path_endpoint_label_package_supplied`
- matched_batch_count：`0`
- can_route_to_field_layout_holdout：`False`
- next_operator_action：`submit_field_path_endpoint_label_package_rows`
- field_boundary：contract only; no real path/endpoint package rows have been supplied

## Missingness Stress Tests

| Scenario | Critical target | Missing fraction | Support | Fallback |
| --- | --- | --- | --- | --- |
| `full_layout_available` | `all_states` | `0.0` | `0.824` | direct_node_modality_values |
| `catalyst_bed_uv254_orp_missing` | `catalyst_activity` | `0.067` | `0.472` | pressure_drop_regeneration_response_and_grey_box_rate_residual |
| `recycle_loop_flow_delay` | `hydraulic_confidence` | `0.1` | `0.697` | time_since_last_observed_and_loop_hold_time_prior |
| `matrix_shock_ec_turbidity_sparse` | `matrix_interference` | `0.1` | `0.745` | uv254_ph_orp_proxy_and_fast_proxy_event_log |

## Training Schema Gap

- current_model_layout_aware：`False`
- missing_layout_terms：`['layout_id', 'node_id', 'zone', 'modality', 'availability_mask', 'time_since_last_observed_min', 'grey_box_residual_prior']`
- missing_pressure_headloss_terms：`['pressure_drop_kPa', 'headloss_kPa_per_m', 'flow_normalized_pressure_residual']`
- missing_hydraulic_path_terms：`[]`

## Pressure/Headloss Candidate Contract

- source：`R2.observation_contract.base_layout`
- candidate_ids：`['N3_catalyst_bed:pressure_drop_kPa', 'N3_catalyst_bed:headloss_kPa_per_m', 'N3_catalyst_bed:flow_normalized_pressure_residual']`
- field_required_tables：`['node_modality_sensor_timeseries', 'offline_lab_results', 'campaign_operation_log', 'site_topology_or_bed_geometry']`
- can_use_as_installed_sensor：`False`

## 结论与边界

- 把 Agent48 的 layout_id、node_id、zone、modality、availability_mask 和 time_since_last_observed_min 写入软传感训练/推理 schema。
- 训练阶段按 layout_id 做 holdout，防止模型只记住某个 synthetic 布点而不能泛化到现场布点变化。
- 将 Agent53 的 grey_box_residual_prior 作为可选 feature channel，但 field 物理校准前只能作为先验，不得写 release gate。
- 下一轮应把工程执行约束写入 Agent49 reward 和最终仲裁，尤其是泵阀动作次数、池容、药剂库存和人工复核时间。
- 把 pressure_drop/headloss/flow-normalized residual 作为催化剂活性和水力状态的候选软传感通道，但必须等待现场床层几何、压降记录和 lab label 匹配后才能形成性能 claim。
- 软传感训练特征已接入数值化水力路径字段，并已形成 synthetic layout holdout；下一步应提交真实 path_stage/endpoint labels、node-specific field values 和 final effluent 端点标签包，通过 R8u66 preflight 后再进入 field layout holdout。
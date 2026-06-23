# 催化剂活性代理观测设计

- catalyst_proxy_status：`synthetic_catalyst_proxy_design_ready_needs_field_labels`
- catalyst_proxy_score：`0.5`
- current_proxy_observability：`0.331`
- proxy_observability_after_recommended_patch：`0.72`
- weak_state_coverage_after_proxy_design：`0.72`
- weak_axis_repair_status：`agent48_catalyst_axis_requires_proxy_patch_and_field_label`
- repair_score：`0.983`
- can_relax_agent49_catalyst_uncertainty_block：`False`
- field_proxy_holdout_summary_status：`field_proxy_holdout_coverage_gaps`
- field_proxy_holdout_scoreable_batch_count：`0`

## Proxy Catalog

| Proxy | Current Support | Missing Signals | Recommended Patch | Formula |
| --- | --- | --- | --- | --- |
| `bed_uv254_removal_delta` 催化剂床前后 UV254 去除率 | `0.5` | ['N3_catalyst_bed_outlet:UV254_abs'] | ['N3_catalyst_bed_outlet:UV254_abs'] | `(UV254_in - UV254_out) / max(UV254_in, eps)` |
| `orp_decay_across_bed` 催化剂床前后 ORP 衰减/利用 | `0.5` | ['N3_catalyst_bed_outlet:ORP_mV'] | ['N3_catalyst_bed_outlet:ORP_mV'] | `clip((ORP_in - ORP_out) / 180, 0, 1)` |
| `turbidity_pressure_fouling` 浊度/压降污染堵塞代理 | `0.5` | ['N3_catalyst_bed:pressure_drop_kPa'] | ['N3_catalyst_bed:pressure_drop_kPa'] | `0.55 * turbidity_delta_norm + 0.45 * pressure_drop_norm` |
| `regeneration_response_gain` 再生前后响应增益 | `0.0` | ['operation_log:regeneration_event', 'pre_post_regeneration:uv254_or_rate_gain'] | ['campaign_operation_log.regeneration_event', 'pre_post_regeneration_lab_label'] | `post_regen_removal_or_rate - pre_regen_removal_or_rate` |
| `residence_time_normalized_rate_residual` 停留时间归一化反应速率残差 | `0.75` | ['N3_catalyst_bed_outlet:UV254_abs'] | ['N3_catalyst_bed_outlet:UV254_abs', 'reactor_bed_volume_or_HRT'] | `-ln(UV254_out / UV254_in) / HRT compared with expected oxidant-adjusted rate` |

## Synthetic Proxy Cases

| Case | Scenario | Proxy Score | Label | Error |
| --- | --- | --- | --- | --- |
| `C0_healthy_active` | healthy_active_catalyst | `0.687` | `0.78` | `0.093` |
| `C1_reversible_fouling` | fouled_but_regenerable | `0.357` | `0.46` | `0.103` |
| `C2_exhausted_low_response` | exhausted_or_irreversible_deactivation | `0.268` | `0.28` | `0.012` |
| `C3_matrix_suppressed` | matrix_interference_masks_activity | `0.365` | `0.52` | `0.155` |

## Agent48 Weak Axis Repair Plan

- target_axis：`catalyst_activity_observability`
- current_axis_coverage：`0.3`
- target_axis_coverage：`0.55`
- agent48_best_available_candidate：`N3_catalyst_bed_outlet:UV254_abs`
- recoverable_by_current_candidate_pool：`False`
- proxy_projected_axis_coverage：`0.72`

| Patch | Class | Priority | Supports | Why |
| --- | --- | ---: | --- | --- |
| `N3_catalyst_bed_outlet:UV254_abs` | `low_cost_sensor` | `0.66` | ['bed_uv254_removal_delta', 'residence_time_normalized_rate_residual'] | 床出口 UV254 与回流/床入口 UV254 组成差分，支撑活性和停留时间归一化速率残差。 |
| `N3_catalyst_bed_outlet:ORP_mV` | `low_cost_sensor` | `0.36` | ['orp_decay_across_bed'] | 床出口 ORP 与反应核心 ORP 组成氧化剂利用/衰减代理。 |
| `N3_catalyst_bed:pressure_drop_kPa` | `low_cost_sensor` | `0.35` | ['turbidity_pressure_fouling'] | 压降用于区分催化剂活性衰减与床层堵塞/污堵。 |
| `reactor_bed_volume_or_HRT` | `hydraulic_or_geometry_field` | `0.28` | ['residence_time_normalized_rate_residual'] | 床体积或停留时间用于把去除率转化为灰箱速率残差。 |
| `campaign_operation_log.regeneration_event` | `operation_log_field` | `0.25` | ['regeneration_response_gain'] | 再生事件用于判断活性下降是否可逆。 |
| `pre_post_regeneration_lab_label` | `offline_lab_label` | `0.23` | ['regeneration_response_gain'] | 离线标签用于把 synthetic proxy 升级为 field_proxy_holdout。 |

## Field Repair Evidence Requirements

- `CAX_1_low_cost_sensor`：table=`node_modality_sensor_timeseries`，fields=['timestamp_min', 'batch_id', 'node_id', 'modality', 'value', 'sensor_status']，minimum=same-batch inlet/outlet signal pairs with calibration status
- `CAX_2_hydraulic_or_geometry_field`：table=`site_topology_or_bed_geometry`，fields=['node_id', 'bed_volume', 'nominal_HRT_min', 'flow_Lmin']，minimum=bed geometry and flow records to normalize reaction rate residuals
- `CAX_3_operation_log_field`：table=`campaign_operation_log`，fields=['batch_id', 'regeneration_event', 'command_time_min', 'effect_time_min']，minimum=time-aligned regeneration events before/after proxy response
- `CAX_4_offline_lab_label`：table=`offline_lab_results`，fields=['batch_id', 'analyte', 'value', 'qa_flag', 'lab_label_time_min']，minimum=QA-passed catalyst activity or regeneration response labels

## Field Proxy Holdout Summary

- status：`field_proxy_holdout_coverage_gaps`
- matched_batch_count：`0`
- scoreable_batch_count：`0`
- field_validation_metrics：`{'field_label_coverage': 0.0, 'proxy_label_correlation': 0.0, 'holdout_mae': 1.0, 'scoreable_batch_count': 0, 'matched_batch_count': 0}`
- boundary：This summary only turns an R7j-ready package into Agent51 validation rows. It does not prove field-supported control, write actuators or write release gates.

## Agent49 Interface

- policy_effect：`keep_R3_catalyst_uncertainty_block`
- boundary：synthetic proxy design cannot relax Agent49 actuator or release gate blocks

## 结论

- 把 catalyst_activity 从单点弱状态改成床前后差分、反应速率残差、污堵/压降和再生响应共同支持的代理观测。
- 将 proxy_observability_after_recommended_patch 写回 Agent48/Agent49 作为设计先验，但 synthetic 阶段不能解除执行器保护规则。
- 优先补充这些信号或字段：['N3_catalyst_bed:pressure_drop_kPa', 'N3_catalyst_bed_outlet:ORP_mV', 'N3_catalyst_bed_outlet:UV254_abs']。
- Agent48 已证明 catalyst_activity 不是当前候选池可自然补足的弱轴；下一步应按 weak_axis_repair_plan 优先补床出口 UV254/ORP、压降、再生事件和离线活性标签。
- 下一步需要 field_proxy_holdout：至少包含催化剂活性离线标签、压降、再生事件和床前后 UV254/ORP。
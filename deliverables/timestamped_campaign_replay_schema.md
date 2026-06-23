# Timestamped Campaign Replay Schema

- timestamped_replay_status：`synthetic_timestamp_schema_ready_needs_field_replay`
- timestamped_replay_score：`0.94`
- data_origin：`synthetic`
- timestamp_coverage：`1.0`
- proxy_precision：`1.0`
- proxy_recall：`1.0`
- pressure_headloss_event_count：`12`
- pressure_headloss_matched_batch_count：`12`
- can_calibrate_fast_proxy：`False`

## 生成文件

- timestamped_campaign_replay_schema: `/Users/chuchenqidawang/Documents/低成本传感循环式水处理智能闭环项目/deliverables/timestamped_campaign_replay_schema.md`
- agent42_report: `/Users/chuchenqidawang/Documents/低成本传感循环式水处理智能闭环项目/outputs/agent42_timestamped_campaign_replay/agent42_report.md`
- timestamped_replay_schema_json: `/Users/chuchenqidawang/Documents/低成本传感循环式水处理智能闭环项目/outputs/timestamped_campaign_replay/timestamped_replay_schema.json`
- timestamped_replay_templates: `/Users/chuchenqidawang/Documents/低成本传感循环式水处理智能闭环项目/outputs/timestamped_campaign_replay/templates`
- synthetic_timestamped_replay_package: `/Users/chuchenqidawang/Documents/低成本传感循环式水处理智能闭环项目/outputs/timestamped_campaign_replay/synthetic_timestamped_replay`

## 表结构

### sensor_timeseries

- 描述：低成本传感原始时间序列，支撑快代理触发时间。
- 必需字段：batch_id, timestamp_min, EC_uScm, turbidity_NTU, UV254_abs, pH, ORP_mV
- 可选字段：flow_Lmin, pressure_drop_kPa, headloss_kPa_per_m, bed_inlet_pressure_kPa, bed_outlet_pressure_kPa
- 时间字段：timestamp_min

### offline_lab_results

- 描述：离线标签与结果返回时间，用于计算检测 turnaround 和快代理标签。
- 必需字段：batch_id, sample_time_min, result_time_min, analyte, value, qa_flag
- 可选字段：proxy_holdout_label, catalyst_activity_label, pressure_headloss_proxy_label
- 时间字段：sample_time_min, result_time_min

### campaign_operation_log

- 描述：控制动作命令、执行和生效时间，用于计算执行器/预处理延迟。
- 必需字段：campaign_id, batch_id, action_id, command_time_min, effect_time_min, start_min, end_min, release_policy
- 可选字段：recycle_ratio, tank_storage_margin, actuator_latency_p90, pump_valve_result, hold_time_min, regeneration_event, bed_id, pressure_headloss_review_required
- 时间字段：command_time_min, effect_time_min, start_min, end_min

### pressure_headloss_event_log

- 描述：压降/水头损失候选代理事件，用于 replay 催化剂床堵塞、水力异常和 guardrail 阻断边界。
- 必需字段：campaign_id, batch_id, event_time_min, bed_id, pressure_drop_kPa, headloss_kPa_per_m, flow_Lmin, matched_lab_sample_time_min, regeneration_event, hydraulic_anomaly_label
- 可选字段：flow_normalized_pressure_residual, expected_clean_bed_pressure_drop_kPa, operator_review_required
- 时间字段：event_time_min, matched_lab_sample_time_min

### fast_proxy_event_log

- 描述：基质冲击快代理事件与现场标签，用于 precision/recall、提前量和误触发成本校准。
- 必需字段：campaign_id, batch_id, event_time_min, proxy_score, specificity_guard_score, protective_triggered, triggered_action_id, field_label_matrix_shock, lab_label_time_min, false_positive_cost_index
- 时间字段：event_time_min, lab_label_time_min

## 结论

- 把 sensor、lab、operation 和 fast_proxy_event_log 放到同一 batch 时间轴，优先保证 result_time_min 与 effect_time_min。
- 用 field-labeled fast_proxy_event_log 计算 precision、recall、提前量和误触发成本，再决定是否写入保护性控制。
- pressure_headloss_event_log 必须回连同 batch 的传感、离线标签和床层信息，才能从候选水力代理进入 guardrail replay。
- 当前 synthetic timestamped package 只能作为模板联调，不得作为 Agent41 现场有效性证据。
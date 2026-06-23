# 真实数据接口与校准准备规范

## 目的

Agent30 的作用是把当前仿真研究平台推进到真实数据校准阶段：先规定现场数据包必须包含哪些表、哪些字段、怎样用 batch_id 回连，再判断当前数据包能否进入软传感器、时间预算、催化剂寿命和经济性校准。

## 当前状态

- 数据来源：`synthetic`。
- 接口状态：`template_ready_not_field_validated`。
- 校准就绪度：`1.0`。
- 生成 schema：`outputs/agent30_field_data_interface/field_data_schema.json`。
- 生成采集模板：`outputs/agent30_field_data_interface/field_data_templates`。
- 合成样例数据包：`outputs/agent30_field_data_interface/synthetic_field_data_package`。

## 数据表契约

### sensor_timeseries

- 说明：低成本在线传感器原始时间序列。
- 必需字段：batch_id, timestamp_min, cycle_id, pH, ORP_mV, EC_uScm, turbidity_NTU, temp_C, flow_Lmin, UV254_abs
- 可选字段：sensor_status, operator_note, instrument_id, acquisition_time_min, ingest_time_min, pressure_drop_kPa, headloss_kPa_per_m, bed_inlet_pressure_kPa, bed_outlet_pressure_kPa, flow_normalized_pressure_residual
- 主键：batch_id, timestamp_min
- 校准对象：DataQualityAgent, SoftSensorAgent, sensor_noise_multiplier

### offline_lab_results

- 说明：旁路快检/离线检测标签，用于校准软传感器和放行门。
- 必需字段：batch_id, sample_time_min, analyte, value, unit, method, qa_flag
- 可选字段：result_time_min, turnaround_min, detection_limit, lab_id, replicate_id, sample_source, proxy_holdout_label
- 主键：batch_id, sample_time_min, analyte
- 校准对象：SoftSensorAgent, ValidationPlanningAgent, release_gate

### catalyst_lifecycle

- 说明：催化剂寿命、再生和更换记录。
- 必需字段：catalyst_id, batch_id, cycle_count, regen_count, activity_assay, pressure_drop_kPa, lifetime_fraction
- 可选字段：surface_pollution_index, replacement_flag, regen_method, regeneration_event, headloss_kPa_per_m, bed_geometry_id, catalyst_bed_depth_m
- 主键：catalyst_id, batch_id
- 校准对象：CatalystLifecycleAgent, RecoveryStrategyWritebackAgent

### campaign_operation_log

- 说明：批次运行、动作执行和闭环控制日志。
- 必需字段：campaign_id, batch_id, action_id, start_min, end_min, intake_fraction, success
- 可选字段：command_time_min, effect_time_min, recycle_start_min, recycle_end_min, pretreatment_effect_time_min, fast_proxy_score, release_policy, recycle_ratio, dose_factor, validation_minutes, operator_override, tank_storage_margin, actuator_latency_p90, pump_valve_result, hold_time_min, regeneration_event, bed_id, pressure_headloss_review_required
- 主键：campaign_id, batch_id, action_id, start_min
- 校准对象：CampaignTelemetryAgent, RecoveryRampAgent, RecoveryOnlineControlAgent

### site_topology_or_bed_geometry

- 说明：处理单元拓扑、催化剂床几何和水力先验，用于把压降/水头损失候选信号从黑箱代理转成可校准灰箱边界。
- 必需字段：site_id, node_id, zone, upstream_node_id, downstream_node_id, bed_id, bed_depth_m, bed_area_m2, nominal_flow_Lmin, nominal_HRT_min
- 可选字段：pressure_sensor_location, install_access_score, bed_media, hydraulic_position, expected_clean_bed_pressure_drop_kPa
- 主键：site_id, node_id, bed_id
- 校准对象：SensorNetworkSparsePlacementAgent, SoftSensorMatrixCouplingAgent, MultiFacilityReplayEvaluationAgent, RealFieldReplayPipeline

### cost_deployment

- 说明：传感器、试剂、催化剂、人工和部署接口的经济性参数。
- 必需字段：item_id, category, unit_cost_cny, quantity, lead_time_days
- 可选字段：vendor, maintenance_hours_per_month, interface_point
- 主键：item_id
- 校准对象：SensitivityAnalysisAgent, ResourceExpansionAgent, LongTermEconomicsAgent

## 下一步

- 当前接口模板可运行，下一步用真实现场数据替换 synthetic/sample 行。
- P1-P5 校准任务在字段契约上均已具备模板入口；真实采集时应优先保证 batch_id 可回连。
- 先采集同一批次的在线传感时间序列、离线检测标签和 campaign 操作日志，再补催化剂寿命与经济性记录。

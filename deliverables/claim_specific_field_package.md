# Claim-Specific 现场采集包

- claim_specific_package_status：`claim_specific_package_ready_needs_real_data_and_source_basis_detail`
- claim_specific_required_field_coverage：`1.0`
- minimal_field_package_schema_pass_rate：`1.0`
- minimal_field_package_field_pass_rate：`0.0`
- source_basis_completion_rate：`1.0`
- field_requirement_patch_consumption_rate：`1.0`
- unmet_guardrail_field_count：`0`
- field_claim_upgrade_blocker_count：`5`
- can_write_to_actuator：`False`
- can_write_to_release_gate：`False`

## Minimal Field Package Matrix

| Need | Required Fields | Metadata | Gates | Blockers |
| --- | --- | --- | --- | --- |
| `真实传感漂移记录` | `{'sensor_timeseries': ['EC_uScm', 'ORP_mV', 'UV254_abs', 'acquisition_time_min', 'batch_id', 'cycle_id', 'flow_Lmin', 'ingest_time_min', 'instrument_id', 'pH', 'sensor_status', 'temp_C', 'timestamp_min', 'turbidity_NTU']}` | `['data_origin', 'site_id', 'instrument_snapshot_id', 'chain_of_custody_id']` | `['G6_1_field_origin', 'G6_2_timestamp_schema_ready', 'G6_3_batch_linkage_complete']` | `['real_field_package_not_imported']` |
| `离线放行标签` | `{'offline_lab_results': ['analyte', 'batch_id', 'detection_limit', 'method', 'qa_flag', 'result_time_min', 'sample_source', 'sample_time_min', 'unit', 'value']}` | `['data_origin', 'site_id', 'campaign_id', 'chain_of_custody_id']` | `['G6_1_field_origin', 'G6_2_timestamp_schema_ready', 'G6_3_batch_linkage_complete']` | `['real_field_package_not_imported']` |
| `低浓度目标物检测限` | `{'offline_lab_results': ['analyte', 'batch_id', 'detection_limit', 'method', 'qa_flag', 'replicate_id', 'result_time_min', 'sample_source', 'sample_time_min', 'unit', 'value']}` | `['data_origin', 'site_id', 'campaign_id', 'chain_of_custody_id']` | `['G6_1_field_origin', 'G6_2_timestamp_schema_ready', 'G6_3_batch_linkage_complete']` | `['real_field_package_not_imported']` |
| `R4 guardrail 催化剂代理不确定现场验证` | `{'campaign_operation_log': ['action_id', 'batch_id', 'campaign_id', 'end_min', 'intake_fraction', 'operator_override', 'start_min', 'success'], 'catalyst_lifecycle': ['activity_assay', 'batch_id', 'catalyst_id', 'cycle_count', 'lifetime_fraction', 'pressure_drop_kPa', 'regen_count', 'regen_method', 'replacement_flag', 'surface_pollution_index'], 'offline_lab_results': ['analyte', 'batch_id', 'method', 'qa_flag', 'sample_time_min', 'unit', 'value'], 'sensor_timeseries': ['EC_uScm', 'ORP_mV', 'UV254_abs', 'batch_id', 'cycle_id', 'flow_Lmin', 'pH', 'temp_C', 'timestamp_min', 'turbidity_NTU'], '_guardrail_requirement_patch': ['N3_catalyst_bed_outlet:UV254_abs', 'N3_catalyst_bed_outlet:turbidity_NTU', 'operator_override', 'pressure_drop_kPa', 'proxy_holdout_label', 'regeneration_event']}` | `['data_origin', 'site_id', 'campaign_id', 'operator_id', 'chain_of_custody_id']` | `['G6_1_field_origin', 'G6_2_timestamp_schema_ready', 'G6_3_batch_linkage_complete', 'G6_7_false_positive_cost']` | `['real_field_package_not_imported']` |
| `R4 guardrail 水力延迟与池容执行验证` | `{'campaign_operation_log': ['action_id', 'batch_id', 'campaign_id', 'command_time_min', 'effect_time_min', 'end_min', 'intake_fraction', 'operator_override', 'recycle_ratio', 'start_min', 'success', 'validation_minutes'], 'sensor_timeseries': ['EC_uScm', 'ORP_mV', 'UV254_abs', 'batch_id', 'cycle_id', 'flow_Lmin', 'pH', 'temp_C', 'timestamp_min', 'turbidity_NTU'], '_guardrail_requirement_patch': ['actuator_latency_p90', 'flow_Lmin', 'hold_time_min', 'pump_valve_result', 'recycle_ratio', 'tank_storage_margin']}` | `['data_origin', 'site_id', 'campaign_id', 'operator_id', 'chain_of_custody_id']` | `['G6_1_field_origin', 'G6_2_timestamp_schema_ready', 'G6_3_batch_linkage_complete', 'G6_6_latency_action_margin']` | `['real_field_package_not_imported']` |

## Source Basis Completion Tasks

- `kb_sensor_limited_release_evidence`：current=['source_basis_id:low_cost_proxy_sensing; evidence_stage:literature_supported_method_not_field_validated', 'citation:Schneider_2020_EST_onsite_soft_sensors; doi:10.1021/acs.est.9b07760; title:Benchmarking Soft Sensors for Remote Monitoring of On-Site Wastewater Treatment Plants', 'citation:Song_2021_WaterResearch_AOP_surrogates; doi:10.1016/j.watres.2020.116733; title:Surrogates for on-line monitoring of the attenuation of trace organic contaminants during advanced oxidation processes for water reuse', 'parameter_boundary:必须记录 sensor_status、instrument_id、acquisition_time_min、ingest_time_min; 必须估计 sensor_drift_rate、timestamp_coverage、sensor_status_coverage; UV254/荧光 proxy 不能跨污染物类别、水质基质或工艺阶段无校准迁移', 'failure_boundary:低成本 proxy sensing 可增强观测和排序，但不能单独证明污染物达标；没有 field-labeled drift 和离线检测标签时不能写 release gate。', 'source_basis_id:soft_sensor_release_gate; evidence_stage:literature_supported_validation_method_not_field_validated', 'citation:Haimi_2013_EnvModSoft_WWTP_soft_sensors; doi:10.1016/j.envsoft.2013.05.009; title:Data-derived soft-sensors for biological wastewater treatment plants: An overview', 'citation:Dürrenmatt_2021_WaterResearch_Ecoli_soft_sensor; doi:10.1016/j.watres.2021.116806; title:Soft sensor predictor of E. coli concentration based on conventional monitoring parameters for wastewater disinfection control', 'citation:Angelopoulos_Bates_2023_conformal_prediction; doi:10.1561/2200000101; title:Conformal Prediction: A Gentle Introduction', 'parameter_boundary:必须报告 interval_coverage、conformal_coverage、interval_width、abstention_rate; 必须按 catalyst_activity、matrix_interference 等弱目标分层检查 coverage; 若 SFG0 field origin 或弱目标 coverage 未通过，不能写 release gate', 'failure_boundary:软传感 release gate 只能在真实 field holdout 和离线标签通过后成为校准候选；synthetic conformal coverage 不能证明现场自动放行安全。']；required_patch=['具体文献/报告 citation key', '适用水质/污染物边界', '参数范围或检测方法', '对应 field_validation_need 的证据等级']
- `R4_control_guardrail_failure_backpropagation`：current=['internal_artifact: outputs/control_guardrail_backpropagation/control_guardrail_backpropagation_metrics.json; generated=2026-06-02; evidence_stage=synthetic_replay_backpropagation', 'parameter_boundary: catalyst proxy labels, pressure_drop_kPa, regeneration_event, tank_storage_margin, actuator_latency_p90, pump_valve_result, hold_time_min and recycle_ratio must be field validated before control claims', 'failure_boundary: not field-supported; no actuator or release-gate writeback without real field replay']；required_patch=['具体文献/报告 citation key', '适用水质/污染物边界', '参数范围或检测方法', '对应 field_validation_need 的证据等级']

## 结论边界

- `claim_upgrade_blocked`：该验证需求的采集包已定义，但 claim 仍不能升级为现场结论。
- `claim_upgrade_blocked`：该验证需求的采集包已定义，但 claim 仍不能升级为现场结论。
- `claim_upgrade_blocked`：该验证需求的采集包已定义，但 claim 仍不能升级为现场结论。
- `claim_upgrade_blocked`：该验证需求的采集包已定义，但 claim 仍不能升级为现场结论。
- `claim_upgrade_blocked`：该验证需求的采集包已定义，但 claim 仍不能升级为现场结论。
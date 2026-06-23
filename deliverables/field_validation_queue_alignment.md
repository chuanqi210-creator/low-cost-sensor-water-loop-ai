# 现场验证队列对齐

- field_validation_alignment_status：`field_validation_alignment_ready_needs_real_field_package`
- field_need_to_table_coverage：`1.0`
- field_need_to_gate_coverage：`1.0`
- schema_extension_required_count：`5`
- field_requirement_patch_consumption_rate：`1.0`
- guardrail_missing_schema_field_count：`0`
- claim_upgrade_blocker_count：`5`
- can_write_to_actuator：`False`
- can_write_to_release_gate：`False`

## Field Package Status

- field_data_interface_status：`template_ready_not_field_validated`
- field_data_origin：`synthetic`
- timestamped_replay_status：`synthetic_timestamp_schema_ready_needs_field_replay`
- field_replay_import_status：`field_replay_import_blocked_non_field_origin`
- field_replay_import_ready：`False`
- field_replay_evidence_chain_status：`field_replay_evidence_chain_blocked_at_import`
- field_replay_evidence_chain_ready：`False`
- release_gate_boundary_preserved：`True`
- guardrail_requirement_patch_count：`2`

## Validation Mapping Table

| Need | Type | Agent30 Tables | Agent42 Tables | Agent43 Gates | Claim Fields | Boundary |
| --- | --- | --- | --- | --- | --- | --- |
| `真实传感漂移记录` | `sensor_drift_and_low_cost_signal_validity` | `sensor_timeseries` | `sensor_timeseries` | `G6_1_field_origin, G6_2_timestamp_schema_ready, G6_3_batch_linkage_complete` | `{'sensor_timeseries': ['sensor_status', 'instrument_id', 'acquisition_time_min', 'ingest_time_min']}` | 真实漂移记录只能校准 sensor_confidence 和软传感不确定性；不能单独授权 release gate。 |
| `离线放行标签` | `offline_release_label_for_soft_sensor_and_claim_gate` | `offline_lab_results` | `offline_lab_results` | `G6_1_field_origin, G6_2_timestamp_schema_ready, G6_3_batch_linkage_complete` | `{'offline_lab_results': ['result_time_min', 'detection_limit', 'sample_source']}` | 离线放行标签只能支持软传感校准和人工审核；release gate 仍需独立 conformal/field holdout 门控。 |
| `低浓度目标物检测限` | `low_concentration_detection_limit_for_target_pollutants` | `offline_lab_results` | `offline_lab_results` | `G6_1_field_origin, G6_2_timestamp_schema_ready, G6_3_batch_linkage_complete` | `{'offline_lab_results': ['detection_limit', 'result_time_min', 'sample_source', 'replicate_id']}` | 检测限缺失时不能把低浓度残留或达标放行升级为现场结论；只能作为待验证 claim。 |
| `R4 guardrail 催化剂代理不确定现场验证` | `guardrail_catalyst_proxy_uncertainty_validation` | `catalyst_lifecycle, offline_lab_results, sensor_timeseries, campaign_operation_log` | `sensor_timeseries, offline_lab_results, campaign_operation_log` | `G6_1_field_origin, G6_2_timestamp_schema_ready, G6_3_batch_linkage_complete, G6_7_false_positive_cost` | `{'campaign_operation_log': ['operator_override'], 'catalyst_lifecycle': ['surface_pollution_index', 'replacement_flag', 'regen_method']}` | synthetic guardrail resolved false-positive catalyst protection; field proxy labels are required before catalyst-control claim upgrade. |
| `R4 guardrail 水力延迟与池容执行验证` | `guardrail_hydraulic_latency_storage_validation` | `campaign_operation_log, sensor_timeseries` | `campaign_operation_log, sensor_timeseries, fast_proxy_event_log` | `G6_1_field_origin, G6_2_timestamp_schema_ready, G6_3_batch_linkage_complete, G6_6_latency_action_margin` | `{'campaign_operation_log': ['command_time_min', 'effect_time_min', 'recycle_ratio', 'validation_minutes', 'operator_override']}` | synthetic guardrail resolved high-regret recycle action; field hydraulic replay is required before recycle-control claim upgrade. |

## 结论边界

- `claim_specific_optional_fields_promoted`：该 claim 需要把当前 optional 字段提升为本验证任务的必采字段。
- `claim_specific_optional_fields_promoted`：该 claim 需要把当前 optional 字段提升为本验证任务的必采字段。
- `claim_specific_optional_fields_promoted`：该 claim 需要把当前 optional 字段提升为本验证任务的必采字段。
- `claim_specific_optional_fields_promoted`：该 claim 需要把当前 optional 字段提升为本验证任务的必采字段。
- `claim_specific_optional_fields_promoted`：该 claim 需要把当前 optional 字段提升为本验证任务的必采字段。
- `field_package_required_before_claim_upgrade`：验证需求已映射到接口，但没有真实 field 包和证据链前仍不能升级为现场结论。
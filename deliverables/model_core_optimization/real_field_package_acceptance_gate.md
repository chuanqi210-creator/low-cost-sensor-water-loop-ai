# R7 真实 Field Package 导入与 Replay/Holdout 验收门

## 核心判断

R7 的作用是把真实现场数据包从“有文件”变成“可进入 replay、holdout 和 claim 审查的证据”。它不是 field-supported 结论本身，也不允许自动写执行器或 release gate。

- 状态：`real_field_package_acceptance_blocked_at_import`
- 通过阶段：0/8
- 阻断原因：field_package_not_imported_or_data_origin_not_field, timestamped_replay_not_field_ready, g6_p6_replay_gate_not_passed, field_replay_evidence_chain_not_passed, multi_facility_control_or_catalyst_proxy_holdout_not_passed, soft_sensor_field_holdout_gate_not_passed, claim_specific_real_field_rows_not_passed, unified_field_evidence_gate_not_passed
- 多设施控制晋级：`False`，catalyst_proxy_field_validation_pass=`False`
- 下一步：`R7a_import_real_field_package_with_metadata_and_csv`

## 最小真实数据包

- metadata required fields：data_origin, site_id, campaign_id, sampling_start, sampling_end, operator_id, instrument_snapshot_id, chain_of_custody_id
- metadata required values：{'data_origin': 'field'}
- csv tables：sensor_timeseries.csv, offline_lab_results.csv, campaign_operation_log.csv, fast_proxy_event_log.csv, catalyst_lifecycle.csv, cost_deployment.csv
- guardrail required fields：proxy_holdout_label, regeneration_event, tank_storage_margin, actuator_latency_p90, pump_valve_result, hold_time_min, recycle_ratio

## 验收链

- Agent44 field origin/import gate
- Agent42 timestamped replay
- Agent43 G6/P6 replay gate
- Agent45 field replay evidence chain
- Agent52 multi-facility replay promotion gate with Agent51 catalyst proxy holdout
- Agent46 soft-sensor field holdout gate
- human review before any release-gate calibration writeback

## Acceptance Matrix

| Stage | 作用 | 当前状态 | 通过 | 下一阻断 |
| --- | --- | --- | --- | --- |
| `R7S1_field_package_import` | 真实 field package 导入与 provenance | `field_replay_import_blocked_non_field_origin` | `False` | `field_package_not_imported_or_data_origin_not_field` |
| `R7S2_timestamped_replay` | sensor/lab/operation/proxy 同轴 replay | `synthetic_timestamp_schema_ready_needs_field_replay` | `False` | `timestamped_replay_not_field_ready` |
| `R7S3_g6_p6_replay_gate` | G6/P6 replay gate 与保护性控制候选 | `synthetic_replay_gate_blocked` | `False` | `g6_p6_replay_gate_not_passed` |
| `R7S4_field_replay_evidence_chain` | Agent44 -> Agent42 -> Agent43 -> Agent45 证据链 | `field_replay_evidence_chain_blocked_at_import` | `False` | `field_replay_evidence_chain_not_passed` |
| `R7S4b_multi_facility_control_promotion` | Agent49/52 多设施控制晋级与催化剂代理验证门 | `synthetic_replay_evaluation_ready_needs_field_replay` | `False` | `multi_facility_control_or_catalyst_proxy_holdout_not_passed` |
| `R7S5_soft_sensor_field_holdout` | 软传感 field holdout release calibration gate | `soft_sensor_release_gate_blocked_non_field_holdout` | `False` | `soft_sensor_field_holdout_gate_not_passed` |
| `R7S6_claim_specific_field_package` | claim-specific 字段、source_basis 与真实 field rows | `claim_specific_package_ready_needs_real_data_and_source_basis_detail` | `False` | `claim_specific_real_field_rows_not_passed` |
| `R7S7_unified_field_evidence_gate` | 统一 evidence gate 的 field-supported 升级判断 | `unified_gate_ready_blocking_field_claim_upgrade` | `False` | `unified_field_evidence_gate_not_passed` |

## 写回边界

- allowed_writeback：R7_acceptance_status_for_governance, field_package_blocker_table
- blocked_writeback：actuator_policy, automatic_release_gate_policy, field_control_effectiveness_claim_without_human_review, synthetic_template_as_field_evidence
- 当前没有真实 field package 通过前，所有结果仍是 field-validation-required。
- 即使未来 R7 自动门全过，也只能进入人工复核，不能自动放行。
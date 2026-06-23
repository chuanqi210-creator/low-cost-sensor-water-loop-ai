# R7 Real Field Package Acceptance Gate 报告

- 状态：`real_field_package_acceptance_blocked_at_import`
- 分数：`0.0`
- 通过阶段：`0/8`
- can_emit_protective_control_candidate：`False`
- multi_facility_control_promotion_pass：`False`
- catalyst_proxy_field_validation_pass：`False`
- can_emit_release_gate_calibration_candidate：`False`
- can_emit_field_supported_claim_candidate：`False`
- can_write_to_release_gate：`False`

## Blocking Reasons

- `field_package_not_imported_or_data_origin_not_field`
- `timestamped_replay_not_field_ready`
- `g6_p6_replay_gate_not_passed`
- `field_replay_evidence_chain_not_passed`
- `multi_facility_control_or_catalyst_proxy_holdout_not_passed`
- `soft_sensor_field_holdout_gate_not_passed`
- `claim_specific_real_field_rows_not_passed`
- `unified_field_evidence_gate_not_passed`

## Acceptance Matrix

| Stage | Status | Passed | Blocker |
| --- | --- | --- | --- |
| `R7S1_field_package_import` 真实 field package 导入与 provenance | `field_replay_import_blocked_non_field_origin` | `False` | `field_package_not_imported_or_data_origin_not_field` |
| `R7S2_timestamped_replay` sensor/lab/operation/proxy 同轴 replay | `synthetic_timestamp_schema_ready_needs_field_replay` | `False` | `timestamped_replay_not_field_ready` |
| `R7S3_g6_p6_replay_gate` G6/P6 replay gate 与保护性控制候选 | `synthetic_replay_gate_blocked` | `False` | `g6_p6_replay_gate_not_passed` |
| `R7S4_field_replay_evidence_chain` Agent44 -> Agent42 -> Agent43 -> Agent45 证据链 | `field_replay_evidence_chain_blocked_at_import` | `False` | `field_replay_evidence_chain_not_passed` |
| `R7S4b_multi_facility_control_promotion` Agent49/52 多设施控制晋级与催化剂代理验证门 | `synthetic_replay_evaluation_ready_needs_field_replay` | `False` | `multi_facility_control_or_catalyst_proxy_holdout_not_passed` |
| `R7S5_soft_sensor_field_holdout` 软传感 field holdout release calibration gate | `soft_sensor_release_gate_blocked_non_field_holdout` | `False` | `soft_sensor_field_holdout_gate_not_passed` |
| `R7S6_claim_specific_field_package` claim-specific 字段、source_basis 与真实 field rows | `claim_specific_package_ready_needs_real_data_and_source_basis_detail` | `False` | `claim_specific_real_field_rows_not_passed` |
| `R7S7_unified_field_evidence_gate` 统一 evidence gate 的 field-supported 升级判断 | `unified_gate_ready_blocking_field_claim_upgrade` | `False` | `unified_field_evidence_gate_not_passed` |

## Next

- `R7a_import_real_field_package_with_metadata_and_csv`：导入 data_origin=field 的真实 metadata 与 CSV 包
- reason：field_package_not_imported_or_data_origin_not_field; timestamped_replay_not_field_ready; g6_p6_replay_gate_not_passed; field_replay_evidence_chain_not_passed; multi_facility_control_or_catalyst_proxy_holdout_not_passed; soft_sensor_field_holdout_gate_not_passed; claim_specific_real_field_rows_not_passed; unified_field_evidence_gate_not_passed
- must_not_do：不能把 synthetic/sample 包当成真实现场 replay；不能绕过人工复核写执行器或 release gate。

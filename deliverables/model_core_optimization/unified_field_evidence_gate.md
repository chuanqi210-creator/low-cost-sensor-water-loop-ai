# 统一 Field Evidence Gate

## 核心判断

这一步不是新增业务 agent，而是把分散在 Agent43/44/45/46/58/59 的 field evidence、claim package、source_basis、replay/holdout gate 合成一个统一证据门控接口。它的价值是减少重复阻断、统一 claim 升级边界，并让后续模块只消费一个证据接口。

- 状态：`unified_gate_ready_blocking_field_claim_upgrade`
- 统一证据记录数：5
- 消费 gate 来源数：6/6
- source_basis_completion_rate（Agent59 原始任务完成率）：1.0
- citation_detail_completion_rate（统一 gate 补充后的文献细节率）：1.0
- source_basis_parameter_boundary_coverage：1.0
- effective_literature_traceability：1.0
- field_supported_edge_ratio：0.0
- claim_basis_promotion_gate_status：claim_basis_promotion_blocked_until_field_validation
- ready_promotion_count：0
- blocked_promotion_count：5
- synthetic 边界保留：True

## 已合并的证据来源

- Agent43_FieldReplayCalibrationGate
- Agent44_FieldReplayImport
- Agent45_FieldReplayEvidenceChain
- Agent46_SoftSensorFieldHoldoutGate
- Agent58_FieldValidationQueueAlignment
- Agent59_ClaimSpecificFieldPackage

## 统一阻断类型

- failed_replay_gate
- failed_soft_sensor_gate
- field_origin_not_verified
- field_replay_evidence_chain_not_passed
- field_replay_import_not_passed
- real_field_package_not_imported

## 证据记录

| Need | Stage | Raw source detail flag | Detail library complete | Field import | Evidence chain | Soft gate |
| --- | --- | --- | --- | --- | --- | --- |
| FVQ01 | synthetic_baseline_field_validation_required | True | True | False | False | False |
| FVQ02 | synthetic_baseline_field_validation_required | True | True | False | False | False |
| FVQ03 | synthetic_baseline_field_validation_required | True | True | False | False | False |
| R4F04 | synthetic_baseline_field_validation_required | True | False | False | False | False |
| R4F05 | synthetic_baseline_field_validation_required | True | False | False | False | False |

## Claim Basis Promotion Gate

该 gate 把每条统一证据记录转成主张升级决策行，明确哪些依据是当前可用依据，哪些依据绝不能被误写为 field evidence、release gate、actuator policy 或法律/专利结论。

- gate_status：`claim_basis_promotion_blocked_until_field_validation`
- promotion_decision_count：5
- ready_promotion_count：0
- blocked_promotion_count：5
- can_emit_field_claim_upgrade：False
- can_write_to_actuator：False
- can_write_to_release_gate：False

| Need | Promotion status | Allowed level | Next required gate | Blockers |
| --- | --- | --- | --- | --- |
| FVQ01 | blocked | no_field_claim_upgrade | import_real_field_package_then_replay_holdout_and_human_review | failed_replay_gate:G6_1_field_origin; failed_soft_sensor_gate:SFG0_field_holdout_origin; failed_soft_sensor_gate:SFG5_weak_target_coverage; field_origin_not_verified; field_replay_evidence_chain_not_passed; field_replay_import_not_passed; real_field_package_not_imported |
| FVQ02 | blocked | no_field_claim_upgrade | import_real_field_package_then_replay_holdout_and_human_review | failed_replay_gate:G6_1_field_origin; failed_soft_sensor_gate:SFG0_field_holdout_origin; failed_soft_sensor_gate:SFG5_weak_target_coverage; field_origin_not_verified; field_replay_evidence_chain_not_passed; field_replay_import_not_passed; real_field_package_not_imported |
| FVQ03 | blocked | no_field_claim_upgrade | import_real_field_package_then_replay_holdout_and_human_review | failed_replay_gate:G6_1_field_origin; failed_soft_sensor_gate:SFG0_field_holdout_origin; failed_soft_sensor_gate:SFG5_weak_target_coverage; field_origin_not_verified; field_replay_evidence_chain_not_passed; field_replay_import_not_passed; real_field_package_not_imported |
| R4F04 | blocked | no_field_claim_upgrade | import_real_field_package_then_replay_holdout_and_human_review | failed_replay_gate:G6_1_field_origin; failed_soft_sensor_gate:SFG0_field_holdout_origin; failed_soft_sensor_gate:SFG5_weak_target_coverage; field_origin_not_verified; field_replay_evidence_chain_not_passed; field_replay_import_not_passed; real_field_package_not_imported |
| R4F05 | blocked | no_field_claim_upgrade | import_real_field_package_then_replay_holdout_and_human_review | failed_replay_gate:G6_1_field_origin; failed_soft_sensor_gate:SFG0_field_holdout_origin; failed_soft_sensor_gate:SFG5_weak_target_coverage; field_origin_not_verified; field_replay_evidence_chain_not_passed; field_replay_import_not_passed; real_field_package_not_imported |

## Source Basis Detail Library

这一步把原先的 source_basis 方法标签补成可追溯的文献、适用条件、参数边界和失败边界。它只提升 literature-supported traceability，不产生 field-supported claim。

### low_cost_proxy_sensing

- evidence_stage：`literature_supported_method_not_field_validated`
- citation_count：2
- parameter_or_method_boundaries：必须记录 sensor_status、instrument_id、acquisition_time_min、ingest_time_min; 必须估计 sensor_drift_rate、timestamp_coverage、sensor_status_coverage; UV254/荧光 proxy 不能跨污染物类别、水质基质或工艺阶段无校准迁移
- required_field_validation：真实传感漂移记录; 离线放行标签; 低浓度目标物检测限
- failure_boundary：低成本 proxy sensing 可增强观测和排序，但不能单独证明污染物达标；没有 field-labeled drift 和离线检测标签时不能写 release gate。

### soft_sensor_release_gate

- evidence_stage：`literature_supported_validation_method_not_field_validated`
- citation_count：3
- parameter_or_method_boundaries：必须报告 interval_coverage、conformal_coverage、interval_width、abstention_rate; 必须按 catalyst_activity、matrix_interference 等弱目标分层检查 coverage; 若 SFG0 field origin 或弱目标 coverage 未通过，不能写 release gate
- required_field_validation：离线放行标签; 低浓度目标物检测限; field holdout sensor/lab paired records
- failure_boundary：软传感 release gate 只能在真实 field holdout 和离线标签通过后成为校准候选；synthetic conformal coverage 不能证明现场自动放行安全。


## 下一步

- `R2_agent48_51_54_observation_contract_merge`：合并稀疏布点、催化剂代理与软传感观测矩阵合同
- 原因：field evidence gate 已统一且 source_basis 细节已补齐；下一步回到观测基础链路提升 Agent48/51/54 联动。
- 禁止事项：不能仅增加传感器数量，必须保留成本、拓扑和 field label 边界。

## 边界

- 统一 gate 只合并接口和阻断口径，不产生 field-supported 结论。
- source_basis citation detail 只能增强 literature-supported traceability，不能替代真实 field package。
- 当前不写执行器、不写 release gate、不删除历史 Agent43/44/45/46/58/59。

# Field Activation Matrix

## 定位

该接口把 Agent50 的隐藏状态 ledger 与外部证据通道连接起来，用于回答：每个不可直接观测状态需要补哪些真实字段，补完后能恢复哪段 replay/holdout/review 链路。

## Readiness

- interface_status: `field_activation_matrix_ready_for_state_level_external_collection`
- hidden_state_row_count: `6`
- hidden_state_row_coverage: `1.0`
- activation_ready_state_count: `0`
- field_validated_state_count: `0`
- control_ready_state_count: `0`
- can_resume_model_chain: `False`
- can_write_to_actuator: `False`
- can_write_to_release_gate: `False`
- response_source_preflight_status: `field_activation_response_source_using_default_template`
- external_response_supplied: `False`
- response_repair_work_order_status: `field_activation_response_repair_work_order_waiting_for_external_response`
- response_repair_item_count: `7`
- response_preflight_status: `field_activation_response_blocked_before_external_package_preflight`
- response_template_marker_row_count: `33`
- response_missing_value_payload_row_count: `0`
- response_template_value_payload_row_count: `33`
- response_completion_ledger_status: `field_activation_response_completion_waiting_for_external_response`
- response_completion_ratio: `0.0`
- response_completed_row_count: `0`
- response_next_hidden_state_focus: `catalyst_activity`
- response_completion_next_operator_action: `copy_template_fill_real_field_values_and_set_FIELD_ACTIVATION_RESPONSE_PATH`
- response_focus_handoff_status: `field_activation_response_focus_handoff_ready_for_catalyst_activity`
- response_focus_handoff_target_hidden_state: `catalyst_activity`
- response_focus_handoff_row_scan_reduction_ratio: `0.818`
- response_focus_handoff_next_operator_action: `fill_focused_catalyst_response_template_then_set_FOCUSED_CATALYST_RESPONSE_PATH_and_merge_to_FIELD_ACTIVATION_RESPONSE_PATH`
- response_focus_handoff_repair_work_order_status: `focused_catalyst_response_repair_work_order_waiting_for_external_response`
- response_focus_handoff_repair_item_count: `1`
- response_coherence_audit_status: `field_activation_response_coherence_audit_waiting_for_response_preflight`
- response_coherence_hard_blocker_count: `0`
- response_coherence_warning_count: `0`
- package_assembly_status: `field_activation_package_assembly_plan_blocked_by_response_preflight`
- package_staging_status: `field_activation_package_staging_manifest_blocked_by_response_preflight`
- package_staging_selected_channel_count: `1`
- package_staging_selected_row_blueprint_count: `0`
- package_staging_selected_value_payload_mapping_count: `0`
- materialized_package_preflight_status: `field_activation_materialized_package_preflight_blocked_by_staging_manifest`
- materialized_package_blocker_count: `1`
- materialized_package_blueprint_missing_row_count: `0`
- materialized_package_next_operator_action: `complete_field_activation_staging_manifest_before_materializing_package`
- downstream_r7_preview_status: `field_activation_downstream_r7_preview_blocked_by_materialized_package_preflight`
- downstream_r7_preview_executed: `False`
- downstream_r7_preview_metric_evaluation_status: `deferred_until_materialized_package_preflight_ready`
- downstream_r7_can_pass_to_timestamped_replay: `False`
- downstream_r7_highest_priority_blocker: `R8U105_STAGING_MANIFEST_NOT_READY`
- downstream_r7_next_operator_action: `complete_field_activation_staging_manifest_before_materializing_package`
- downstream_path_endpoint_preview_status: `field_activation_downstream_path_endpoint_preview_blocked_by_materialized_package_preflight`
- downstream_path_endpoint_preview_executed: `False`
- downstream_path_endpoint_preview_metric_evaluation_status: `deferred_until_materialized_package_preflight_ready`
- downstream_path_endpoint_required_table_count: `6`
- downstream_path_endpoint_contract_minimum_matched_batch_count: `5`
- downstream_path_endpoint_can_route_to_field_layout_holdout: `False`
- downstream_path_endpoint_highest_priority_blocker: `R8U105_STAGING_MANIFEST_NOT_READY`
- downstream_path_endpoint_next_operator_action: `complete_field_activation_staging_manifest_before_materializing_package`
- external_readiness_gate_status: `field_activation_external_readiness_waiting_for_external_response`
- external_readiness_first_blocked_step: `response_source`
- external_readiness_next_operator_action: `set_FIELD_ACTIVATION_RESPONSE_PATH_to_filled_external_response_json`
- response_submission_packet_status: `field_activation_response_submission_packet_waiting_for_external_response`
- response_submission_next_operator_action: `fill_response_template_and_set_FIELD_ACTIVATION_RESPONSE_PATH`
- schema_preflight_status: `field_activation_schema_preflight_passed`
- schema_can_validate_response_structure: `True`

## Method Contract

- technical_problem: 当前系统知道需要真实 field package，但缺少按隐藏状态拆解的采集-回放-控制恢复接口。
- technical_means: 把每个隐藏状态映射到外部证据通道、必需字段、可恢复 gate、证据边界和 no-write 边界。
- technical_effect: 让现场采集从通道级提交变成状态级补证，减少 scan 摩擦，并防止把 proxy/template 误写成 field 结论。
- evidence_boundary: 该接口只定义激活矩阵和补证路径；没有真实 field rows、holdout、replay 和人工复核时，不能生成 field-supported claim、actuator policy 或 release gate。

## State Rows

| hidden_state | activation_status | required_channels | first evidence fields | resumes_to |
| --- | --- | --- | --- | --- |
| `pollutant_residual` | `state_blocked_waiting_for_external_evidence` | R7_REAL_FIELD_PACKAGE, R8U66_PATH_ENDPOINT_LABEL_PACKAGE | offline_lab_results.pollutant_residual, field_holdout_release_labels, sensor_timeseries.final_effluent:UV254_abs, sensor_timeseries.final_effluent:ORP_mV | Agent44 field import preflight, Agent46 soft-sensor field holdout gate, human release review candidate |
| `reaction_completion` | `state_blocked_waiting_for_external_evidence` | R7_REAL_FIELD_PACKAGE, R8U66_PATH_ENDPOINT_LABEL_PACKAGE | offline_lab_results.reaction_completion_proxy, known_HRT_or_contact_time, campaign_operation_log.hold_time_min, campaign_operation_log.effect_time_min | Agent42 timestamped campaign replay, Agent53 grey-box residence-time check, Agent49 recycle/hold-time control review |
| `catalyst_activity` | `state_blocked_waiting_for_external_evidence` | R7_REAL_FIELD_PACKAGE, R8U66_PATH_ENDPOINT_LABEL_PACKAGE | node_modality_sensor_timeseries.N3_catalyst_bed_outlet:UV254_abs, node_modality_sensor_timeseries.N3_catalyst_bed_outlet:ORP_mV, node_modality_sensor_timeseries.N3_catalyst_bed:pressure_drop_kPa, offline_lab_results.catalyst_activity | Agent51 catalyst proxy field holdout, Agent52 control replay promotion gate, Agent49 catalyst regeneration/replacement candidate review |
| `matrix_interference` | `state_blocked_waiting_for_external_evidence` | R7_REAL_FIELD_PACKAGE | field_labeled_fast_proxy_event_log.matrix_shock, offline_lab_results.matrix_interference, sensor_timeseries.influent:conductivity_uScm, sensor_timeseries.influent:turbidity_NTU | Agent41 matrix shock fast proxy, Agent45 field replay evidence chain, Agent49 conservative control arbitration |
| `hydraulic_delay` | `state_blocked_waiting_for_external_evidence` | R7_REAL_FIELD_PACKAGE, R8U66_PATH_ENDPOINT_LABEL_PACKAGE | campaign_operation_log.effect_time_min, campaign_operation_log.hold_time_min, campaign_operation_log.recycle_ratio, site_topology_or_bed_geometry.flow_Lmin | Agent42 timestamped campaign replay, Agent54 field layout holdout, Agent49 multi-facility delay-aware control review |
| `release_or_byproduct_risk` | `state_blocked_waiting_for_external_evidence` | R7_REAL_FIELD_PACKAGE, R8U66_PATH_ENDPOINT_LABEL_PACKAGE | offline_lab_results.byproduct_or_release_risk, human_reviewed_release_gate_labels, final_effluent_endpoint_labels.release_label, human_reviewed_release_gate_labels.batch_id | Agent46 soft-sensor field holdout gate, Agent58 field validation queue alignment, human release gate review |

## No-Write Boundary

Even when a state-level route is ready, the matrix only routes evidence into replay/holdout/review. It never authorizes direct actuator, release-gate, legal or field-claim writes.

## Response Package

- template: `outputs/model_core_governance/field_activation_response_template.json`
- source preflight: `outputs/model_core_governance/field_activation_response_source_preflight.json`
- repair work order: `outputs/model_core_governance/field_activation_response_repair_work_order.json`
- preflight: `outputs/model_core_governance/field_activation_response_preflight.json`
- completion ledger: `outputs/model_core_governance/field_activation_response_completion_ledger.json`
- focus handoff: `outputs/model_core_governance/field_activation_response_focus_handoff.json`
- coherence audit: `outputs/model_core_governance/field_activation_response_coherence_audit.json`
- package assembly plan: `outputs/model_core_governance/field_activation_package_assembly_plan.json`
- package staging manifest: `outputs/model_core_governance/field_activation_package_staging_manifest.json`
- materialized package preflight: `outputs/model_core_governance/field_activation_materialized_package_preflight.json`
- downstream R7 preview: `outputs/model_core_governance/field_activation_downstream_r7_preview.json`
- downstream path/endpoint preview: `outputs/model_core_governance/field_activation_downstream_path_endpoint_preview.json`
- external readiness gate: `outputs/model_core_governance/field_activation_external_readiness_gate.json`
- response submission packet: `outputs/model_core_governance/field_activation_response_submission_packet.json`
- schema contract: `outputs/model_core_governance/field_activation_schema_contract.json`
- schema preflight: `outputs/model_core_governance/field_activation_schema_preflight.json`
- 当前 template 预检默认被阻断，这是正确状态：现场人员必须把 TODO 行替换为真实 field batch/timestamp/node/sensor/lab/operation 证据后才能进入外部包预检。
- schema preflight 只证明字段结构和 no-write flags 合格；它允许模板标记存在，但不能证明现场证据成立。
- coherence audit 会在包组装前检查 batch/node/sensor/chain-of-custody/lab method 是否能形成可回放证据组；它只做一致性和工程可拼接性审计，不把响应包升级为现场结论。
- 如果已有填写后的响应包，设置 `FIELD_ACTIVATION_RESPONSE_PATH=/path/to/response.json` 后重跑该脚本；source preflight 只检查文件可读和根结构，证据成立仍以 response preflight 为准。
- 如果已经按 staging manifest 整理出现场包目录，设置对应 package pointer 环境变量（例如 `REAL_FIELD_REPLAY_PACKAGE_DIR=/path/to/package_dir`）后重跑该脚本；materialized package preflight 会检查 metadata.json、CSV 表、必需字段、模板标记和 field provenance。
- downstream R7 preview 会用同一个 materialized package 只读调用 Agent44 field replay package preflight，提前暴露缺表、类型、必需字段或 batch linkage 问题；它不会恢复模型链，也不会写入控制或放行。
- downstream path/endpoint preview 会用同一个 materialized package 只读调用 Agent54 field path/endpoint label preflight，提前暴露路径阶段、最终出水终点标签、共同 batch 和 release gate 端点证据缺口；它不会恢复模型链，也不会写入控制或放行。
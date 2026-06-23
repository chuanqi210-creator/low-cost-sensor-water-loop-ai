# R7 真实 Field Replay 端到端管线

该管线把一个 package directory 直接送入 Agent44 preflight/import、Agent45 内部 Agent42/43 replay/G6，再进入 R7 acceptance gate。它用于定位真实现场包卡在哪一段，不会自动写执行器或 release gate。

- 当前 source_package_type：`header_only_template_preflight`
- 当前 package_dir：`outputs/field_replay_import/real_field_package_template`
- Submission readiness：`field_package_submission_blocked_at_import_preflight`，highest_blocker=`R7A_IMPORT_PREFLIGHT`，next_action=`repair_metadata_headers_and_real_rows_before_agent42`，blocking_stage_count=`5`，agent42_smoke_submission=`False`，path_endpoint_layout_holdout=`False`，no_write=`True`
- Submission repair work order：`field_package_submission_repair_work_order_blocked_at_import_preflight`，repair_item_count=`13`，path=`outputs/r7_real_field_replay_pipeline/field_package_submission_repair_work_order.json`
- Submission repair response preflight：`repair_response_preflight_blocked_at_template_markers`，missing_items=`0`，template_markers=`13`，route_to_r7_preflight=`False`
- R7 状态：`real_field_package_acceptance_blocked_at_import`
- Coverage 状态：`field_package_coverage_blocked_before_import`
- Agent51 catalyst proxy holdout：`field_proxy_holdout_coverage_gaps`，required=`True`，pass=`False`，matched_batch_count=`0`
- 压力源冲突补丁：conflict_count=`0`，resolved=`0`，unresolved=`0`，resolution_records=`0`，operator_review=`False`，resolution_status=`pressure_source_conflict_resolution_clear`，resolution_ready=`True`
- Agent51 holdout summary：`field_proxy_holdout_coverage_gaps`，scoreable_batch_count=`0`，validation_pass=`False`，holdout_mae=`1.0`，label_correlation=`0.0`
- 多设施控制晋级：control_promotion_pass=`False`，catalyst_proxy_field_validation_pass=`False`
- 最小 replay 契约：`minimum_replay_contract_blocked_missing_rows`，common_batch_count=`0`，valid_matched_batch_count=`0`，valid_operation_actions=`0`，valid_lab_results=`0`，valid_proxy_labels=`0`，valid_pressure_headloss_events=`0`，valid_pressure_headloss_batches=`0`，time_order_violations=`0`
- Field evidence sufficiency：`field_evidence_sufficiency_blocked_before_import`，score=`0.26`，smoke_pass=`False`，calibration_volume_pass=`False`，agent42_smoke=`False`，field_holdout=`False`，human_review_candidate=`False`，field_claim_upgrade_ready=`False`
- Field path/endpoint labels：`field_path_endpoint_label_package_blocked_by_preflight`，matched_batch_count=`0`，minimum=`5`，required_deficit=`5`，batch_alignment_gap_count=`0`，alignment_patch_plan=`field_path_endpoint_alignment_blocked_by_preflight`，alignment_patch_items=`7`，ready=`False`，layout_holdout_with_path_labels=`False`，release_endpoint_blocked=`True`
- Patch plan：`patch_plan_blocked_at_import_preflight`，item_count=`6`
- 下一步：`R7a_import_real_field_package_with_metadata_and_csv`

## 使用方式

```bash
REAL_FIELD_REPLAY_PACKAGE_DIR=/path/to/field_package .venv/bin/python experiments/run_r7_real_field_replay_pipeline.py
```

如果不设置 `REAL_FIELD_REPLAY_PACKAGE_DIR`，脚本只会使用 header-only template 做 preflight 演练，不产生 field evidence。

## 输出文件

- pipeline report：`outputs/r7_real_field_replay_pipeline/r7_real_field_replay_pipeline_report.md`
- pipeline metrics：`outputs/r7_real_field_replay_pipeline/r7_real_field_replay_pipeline_metrics.json`
- submission repair work order：`outputs/r7_real_field_replay_pipeline/field_package_submission_repair_work_order.json`
- submission repair response template：`outputs/r7_real_field_replay_pipeline/field_package_submission_repair_response_template.json`
- submission repair response preflight：`outputs/r7_real_field_replay_pipeline/field_package_submission_repair_response_preflight.json`

## 当前补包计划

- `R7A_METADATA_PLACEHOLDERS`：replace_placeholder_metadata_with_real_provenance；target=`metadata.json`
- `R7A_REAL_ROWS_campaign_operation_log`：add_real_timestamped_rows；target=`campaign_operation_log`
- `R7A_REAL_ROWS_fast_proxy_event_log`：add_real_timestamped_rows；target=`fast_proxy_event_log`
- `R7A_REAL_ROWS_offline_lab_results`：add_real_timestamped_rows；target=`offline_lab_results`
- `R7A_REAL_ROWS_pressure_headloss_event_log`：add_real_timestamped_rows；target=`pressure_headloss_event_log`
- `R7A_REAL_ROWS_sensor_timeseries`：add_real_timestamped_rows；target=`sensor_timeseries`

## 当前 Submission Repair Work Order

- status：`field_package_submission_repair_work_order_blocked_at_import_preflight`
- highest_blocker：`R7A_IMPORT_PREFLIGHT`
- next_operator_action：`repair_metadata_headers_and_real_rows_before_agent42`
- `R7A_METADATA_PLACEHOLDERS`：replace_placeholder_metadata_with_real_provenance；target=`metadata.json`；stage=`R7I_MINIMUM_REPLAY_CONTRACT`
- `R7A_REAL_ROWS_campaign_operation_log`：add_real_timestamped_rows；target=`campaign_operation_log`；stage=`R7I_MINIMUM_REPLAY_CONTRACT`
- `R7A_REAL_ROWS_fast_proxy_event_log`：add_real_timestamped_rows；target=`fast_proxy_event_log`；stage=`R7I_MINIMUM_REPLAY_CONTRACT`
- `R7A_REAL_ROWS_offline_lab_results`：add_real_timestamped_rows；target=`offline_lab_results`；stage=`R7I_MINIMUM_REPLAY_CONTRACT`
- `R7A_REAL_ROWS_pressure_headloss_event_log`：add_real_timestamped_rows；target=`pressure_headloss_event_log`；stage=`R7I_MINIMUM_REPLAY_CONTRACT`
- `R7A_REAL_ROWS_sensor_timeseries`：add_real_timestamped_rows；target=`sensor_timeseries`；stage=`R7I_MINIMUM_REPLAY_CONTRACT`
- `R8U76_SITE_TOPOLOGY_OR_BED_GEOMETRY_ROWS_REQUIRED`：add_real_field_rows；target=`site_topology_or_bed_geometry`；stage=`R8U66_PATH_ENDPOINT_ALIGNMENT`
- `R8U76_NODE_MODALITY_SENSOR_TIMESERIES_ROWS_REQUIRED`：add_real_field_rows；target=`node_modality_sensor_timeseries`；stage=`R8U66_PATH_ENDPOINT_ALIGNMENT`
- `R8U76_HYDRAULIC_PATH_STAGE_LABELS_ROWS_REQUIRED`：add_real_field_rows；target=`hydraulic_path_stage_labels`；stage=`R8U66_PATH_ENDPOINT_ALIGNMENT`
- `R8U76_FINAL_EFFLUENT_ENDPOINT_LABELS_ROWS_REQUIRED`：add_real_field_rows；target=`final_effluent_endpoint_labels`；stage=`R8U66_PATH_ENDPOINT_ALIGNMENT`
- ... plus 3 additional repair items.

## 当前 Submission Repair Response Preflight

- status：`repair_response_preflight_blocked_at_template_markers`
- submitted_item_count：`0`
- blocked_item_count：`0`
- template_marker_count：`13`
- can_route_to_r7_preflight：`False`
- next_operator_action：`replace_todo_template_markers_before_submission`

## 边界

- 只有真实 `data_origin=field`、真实 provenance 和真实 timestamped rows 才能进入 field replay。
- 即使 Agent44/45/R7 局部通过，也必须继续通过 soft holdout、claim-specific rows、unified evidence gate 和人工复核。
- 该管线永远不自动写入执行器策略或自动放行门。
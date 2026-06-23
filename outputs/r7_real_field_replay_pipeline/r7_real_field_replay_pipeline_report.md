# R7 Real Field Replay Pipeline 报告

- source_package_type：`header_only_template_preflight`
- package_dir：`/Users/chuchenqidawang/Documents/低成本传感循环式水处理智能闭环项目/outputs/field_replay_import/real_field_package_template`
- submission_readiness_status：`field_package_submission_blocked_at_import_preflight`
- submission_highest_priority_blocker：`R7A_IMPORT_PREFLIGHT`
- submission_next_operator_action：`repair_metadata_headers_and_real_rows_before_agent42`
- submission_blocking_stage_count：`5`
- submission_can_submit_to_agent42_smoke_replay：`False`
- submission_can_route_to_path_endpoint_layout_holdout：`False`
- submission_no_write_boundary_pass：`True`
- submission_repair_work_order_status：`field_package_submission_repair_work_order_blocked_at_import_preflight`
- submission_repair_item_count：`13`
- submission_repair_work_order_path：`outputs/r7_real_field_replay_pipeline/field_package_submission_repair_work_order.json`
- submission_repair_response_preflight_status：`repair_response_preflight_blocked_at_template_markers`
- submission_repair_response_missing_item_count：`0`
- submission_repair_response_template_marker_count：`13`
- submission_repair_response_can_route_to_r7_preflight：`False`
- submission_repair_response_template_path：`outputs/r7_real_field_replay_pipeline/field_package_submission_repair_response_template.json`
- submission_repair_response_preflight_path：`outputs/r7_real_field_replay_pipeline/field_package_submission_repair_response_preflight.json`
- preflight_status：`field_package_template_ready_needs_real_values_and_rows`
- field_replay_import_status：`field_replay_import_metadata_blocked`
- field_replay_evidence_chain_status：`field_replay_evidence_chain_blocked_at_import`
- field_package_coverage_status：`field_package_coverage_blocked_before_import`
- claim_specific_coverage_rate：`0.0`
- soft_holdout_coverage_pass：`False`
- field_proxy_holdout_status：`field_proxy_holdout_coverage_gaps`
- field_proxy_holdout_required：`True`
- field_proxy_holdout_coverage_pass：`False`
- field_proxy_holdout_matched_batch_count：`0`
- pressure_source_conflict_count：`0`
- resolved_pressure_source_conflict_count：`0`
- unresolved_pressure_source_conflict_count：`0`
- pressure_source_resolution_record_count：`0`
- pressure_source_conflict_requires_operator_review：`False`
- field_package_pressure_conflict_resolution_status：`pressure_source_conflict_resolution_clear`
- field_package_pressure_conflict_resolution_ready：`True`
- agent51_field_proxy_summary_status：`field_proxy_holdout_coverage_gaps`
- agent51_field_proxy_scoreable_batch_count：`0`
- agent51_field_proxy_validation_pass：`False`
- agent51_field_proxy_holdout_mae：`1.0`
- agent51_field_proxy_label_correlation：`0.0`
- multi_facility_control_promotion_pass：`False`
- catalyst_proxy_field_validation_pass：`False`
- minimum_replay_contract_status：`minimum_replay_contract_blocked_missing_rows`
- field_evidence_sufficiency_status：`field_evidence_sufficiency_blocked_before_import`
- field_evidence_sufficiency_score：`0.26`
- field_evidence_smoke_pass：`False`
- field_evidence_calibration_volume_pass：`False`
- can_route_to_agent42_smoke_replay：`False`
- can_route_to_field_holdout：`False`
- field_path_endpoint_label_preflight_status：`field_path_endpoint_label_package_blocked_by_preflight`
- field_path_endpoint_matched_batch_count：`0`
- field_path_endpoint_minimum_matched_batch_count：`5`
- field_path_endpoint_missing_tables：`[]`
- field_path_endpoint_required_field_gap_count：`0`
- field_path_endpoint_template_marker_count：`0`
- field_path_endpoint_table_row_counts：`{'site_topology_or_bed_geometry': 0, 'node_modality_sensor_timeseries': 0, 'hydraulic_path_stage_labels': 0, 'final_effluent_endpoint_labels': 0, 'campaign_operation_log': 0, 'offline_lab_results': 0}`
- field_path_endpoint_table_batch_counts：`{'site_topology_or_bed_geometry': 0, 'node_modality_sensor_timeseries': 0, 'hydraulic_path_stage_labels': 0, 'final_effluent_endpoint_labels': 0, 'campaign_operation_log': 0, 'offline_lab_results': 0}`
- field_path_endpoint_batch_alignment_gap_count：`0`
- field_path_endpoint_required_matched_batch_deficit：`5`
- field_path_endpoint_alignment_patch_plan_status：`field_path_endpoint_alignment_blocked_by_preflight`
- field_path_endpoint_alignment_patch_plan_item_count：`7`
- field_path_endpoint_label_package_ready：`False`
- field_path_endpoint_final_effluent_label_ready：`False`
- can_route_to_field_layout_holdout_with_path_labels：`False`
- release_gate_endpoint_label_blocked：`True`
- can_route_to_human_review_candidate：`False`
- field_supported_claim_upgrade_ready：`False`
- minimum_common_batch_count：`0`
- minimum_valid_matched_batch_count：`0`
- minimum_valid_operation_action_count：`0`
- minimum_invalid_operation_action_count：`0`
- minimum_valid_lab_result_count：`0`
- minimum_invalid_lab_result_count：`0`
- minimum_proxy_event_count：`0`
- minimum_valid_proxy_label_count：`0`
- minimum_invalid_proxy_label_count：`0`
- minimum_pressure_headloss_event_count：`0`
- minimum_valid_pressure_headloss_event_count：`0`
- minimum_invalid_pressure_headloss_event_count：`0`
- minimum_valid_pressure_headloss_batch_count：`0`
- minimum_time_order_violation_count：`0`
- patch_plan_status：`patch_plan_blocked_at_import_preflight`
- patch_plan_item_count：`6`
- r7_status：`real_field_package_acceptance_blocked_at_import`
- r7_score：`0.0`
- next_action：`R7a_import_real_field_package_with_metadata_and_csv`
- can_emit_protective_control_candidate：`False`
- can_write_to_actuator：`False`
- can_write_to_release_gate：`False`

## Preflight Next Actions

- Replace placeholder metadata fields: site_id, campaign_id, sampling_start, sampling_end, operator_id, instrument_snapshot_id, chain_of_custody_id.
- Add real timestamped field rows to every CSV; header-only templates cannot enter field replay.
- Fill Agent44 required fields in: campaign_operation_log, fast_proxy_event_log, offline_lab_results, pressure_headloss_event_log, sensor_timeseries.
- Do not label this package field-supported until Agent44/42/43/45/46/59/R7 gates pass.

## Coverage Next Actions

- Fix preflight/import blockers before interpreting claim or soft-holdout coverage.

## Coverage Patch Plan

- `R7A_METADATA_PLACEHOLDERS`：replace_placeholder_metadata_with_real_provenance；target=metadata.json
- `R7A_REAL_ROWS_campaign_operation_log`：add_real_timestamped_rows；target=campaign_operation_log
- `R7A_REAL_ROWS_fast_proxy_event_log`：add_real_timestamped_rows；target=fast_proxy_event_log
- `R7A_REAL_ROWS_offline_lab_results`：add_real_timestamped_rows；target=offline_lab_results
- `R7A_REAL_ROWS_pressure_headloss_event_log`：add_real_timestamped_rows；target=pressure_headloss_event_log
- `R7A_REAL_ROWS_sensor_timeseries`：add_real_timestamped_rows；target=sensor_timeseries

## Submission Repair Work Order

- status：`field_package_submission_repair_work_order_blocked_at_import_preflight`
- highest_priority_blocker：`R7A_IMPORT_PREFLIGHT`
- next_operator_action：`repair_metadata_headers_and_real_rows_before_agent42`
- repair_item_count：`13`
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

## Submission Repair Response Preflight

- status：`repair_response_preflight_blocked_at_template_markers`
- required_work_item_count：`13`
- response_row_count：`13`
- submitted_item_count：`0`
- blocked_item_count：`0`
- template_marker_count：`13`
- can_route_to_r7_preflight：`False`
- next_operator_action：`replace_todo_template_markers_before_submission`

## R7 Failed Stages

- `R7S1_field_package_import`
- `R7S2_timestamped_replay`
- `R7S3_g6_p6_replay_gate`
- `R7S4_field_replay_evidence_chain`
- `R7S4b_multi_facility_control_promotion`
- `R7S5_soft_sensor_field_holdout`
- `R7S6_claim_specific_field_package`
- `R7S7_unified_field_evidence_gate`

## Boundary

- This pipeline does not write actuator policy.
- This pipeline does not write automatic release-gate policy.
- Header-only templates and synthetic packages remain field-validation-required.
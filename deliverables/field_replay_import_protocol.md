# Field Replay Import Protocol

- source_package_type：`synthetic_interface_package`
- source_package_dir：`outputs/field_replay_import/synthetic_replay_import_package`
- preflight_status：`field_package_preflight_blocked_non_field_origin`
- field_replay_import_status：`field_replay_import_blocked_non_field_origin`
- field_replay_import_score：`0.6`
- accepted_tables：`5/5`
- data_origin：`synthetic`
- linkage_status：`linkage_ready`
- can_pass_to_timestamped_replay：`False`
- can_pass_to_g6：`False`
- can_write_to_protective_control：`False`
- real_field_template_optional_supplements：`['node_modality_sensor_timeseries.csv', 'site_topology_or_bed_geometry.csv', 'hydraulic_path_stage_labels.csv', 'final_effluent_endpoint_labels.csv']`
- real_field_template_preflight_status：`field_package_template_ready_needs_real_values_and_rows`

## 方法契约

- upgrade_id：`field_replay_import_gate_before_timestamped_replay`
- borrowed_from：`['academic_research_agent_evidence_before_claims', 'systematic_literature_review_data_extraction_gates', 'model_validation_and_uncertainty_provenance_checks', 'timestamped_campaign_replay_for_fast_proxy_validation']`
- 现实映射：把真实现场 replay 包从“几张 CSV”提升为可追溯、可类型验收、可 batch 回连的数据入口，防止 synthetic/sample 数据误入现场校准。
- 数据需求：metadata.json, sensor_timeseries.csv, offline_lab_results.csv, campaign_operation_log.csv, fast_proxy_event_log.csv, pressure_headloss_event_log.csv, node_modality_sensor_timeseries.csv for Agent51 catalyst proxy holdout, site_topology_or_bed_geometry.csv for Agent51 catalyst proxy holdout, pressure/headloss batch labels and bed_id linkage, site_id, campaign_id, instrument_snapshot_id, chain_of_custody_id
- 评价指标：field_replay_import_score, accepted_table_count, type_coercion_error_count, metadata_origin_ready, batch_linkage_status
- 失败边界：导入通过只代表现场 replay 包可进入 Agent42；不能替代 Agent42 replay 指标、Agent43 G6/P6 或真实污染物达标验证。

## 表导入验收

| Table | 行数 | 状态 | 缺失字段 | 类型错误数 |
| --- | --- | --- | --- | --- |
| `sensor_timeseries` | `60` | `import_ready` | `[]` | `0` |
| `offline_lab_results` | `12` | `import_ready` | `[]` | `0` |
| `campaign_operation_log` | `12` | `import_ready` | `[]` | `0` |
| `pressure_headloss_event_log` | `12` | `import_ready` | `[]` | `0` |
| `fast_proxy_event_log` | `12` | `import_ready` | `[]` | `0` |

## Preflight 下一步

- Use this package only for interface testing; create a separate package with data_origin=field and real provenance before replay.
- Do not label this package field-supported until Agent44/42/43/45/46/59/R7 gates pass.

## R7j Catalyst Proxy Holdout Supplement

| Supplement Table | 状态 | 行数 | 缺失字段 |
| --- | --- | --- | --- |
| `node_modality_sensor_timeseries` | `supplement_missing_optional_file` | `0` | `['batch_id', 'timestamp_min', 'node_id', 'zone', 'modality', 'value', 'sensor_status', 'instrument_id', 'acquisition_time_min', 'ingest_time_min', 'layout_id', 'availability_mask', 'time_since_last_observed_min', 'data_origin', 'sensor_value']` |
| `site_topology_or_bed_geometry` | `supplement_missing_optional_file` | `0` | `['node_id', 'bed_volume', 'nominal_HRT_min', 'flow_Lmin', 'site_id', 'zone', 'upstream_node_id', 'downstream_node_id', 'path_stage_id', 'hydraulic_path_role', 'nominal_flow_Lmin', 'recycle_ratio', 'release_boundary_flag', 'recirculation_loop_flag']` |
| `hydraulic_path_stage_labels` | `supplement_missing_optional_file` | `0` | `['batch_id', 'layout_id', 'node_id', 'zone', 'path_stage_id', 'hydraulic_path_role', 'stage_coverage_label', 'direct_path_stage_coverage_label', 'proxy_path_stage_coverage_label', 'label_source', 'reviewer_id', 'review_time_min']` |
| `final_effluent_endpoint_labels` | `supplement_missing_optional_file` | `0` | `['batch_id', 'endpoint_node_id', 'sample_time_min', 'final_effluent_direct_observed', 'release_gate_label', 'release_risk_label', 'analyte', 'value', 'unit', 'qa_flag', 'reviewer_id']` |

- R7j supplement 对 Agent44 导入是 optional；当 R7 coverage 消费 Agent51 weak_axis_repair_plan 时，它会成为 catalyst proxy field holdout 的证据要求。

## Real Field Template R7j Supplement

| Supplement Table | 状态 | 行数 | 缺失字段 |
| --- | --- | --- | --- |
| `node_modality_sensor_timeseries` | `supplement_header_ready` | `0` | `[]` |
| `site_topology_or_bed_geometry` | `supplement_header_ready` | `0` | `[]` |
| `hydraulic_path_stage_labels` | `supplement_header_ready` | `0` | `[]` |
| `final_effluent_endpoint_labels` | `supplement_header_ready` | `0` | `[]` |

## 生成文件

- field_replay_import_protocol: `deliverables/field_replay_import_protocol.md`
- agent44_report: `outputs/agent44_field_replay_import/agent44_report.md`
- import_acceptance_metrics: `outputs/field_replay_import/import_acceptance_metrics.json`
- preflight_metrics: `outputs/field_replay_import/real_field_package_preflight_metrics.json`
- template_preflight_metrics: `outputs/field_replay_import/real_field_package_template_preflight_metrics.json`
- import_schema: `outputs/field_replay_import/import_schema.json`
- real_field_package_template: `outputs/field_replay_import/real_field_package_template`
- input_replay_package: `outputs/field_replay_import/synthetic_replay_import_package`

## 结论

- 不要把当前 replay 包传给 G6/P6；先补齐 metadata provenance、CSV 必需字段、类型转换和 batch 关联。
- synthetic/sample 包只能用于接口联调，不得作为现场快代理 precision/recall 证据。
- 真实导入包至少应包含 data_origin=field、site_id、campaign_id、operator_id、instrument_snapshot_id 和 chain_of_custody_id。
- 若使用 pressure/headloss 作为水力代理，必须提供 pressure_headloss_event_log.csv，并确保每个 pressure batch 有同 batch 离线标签锚点。
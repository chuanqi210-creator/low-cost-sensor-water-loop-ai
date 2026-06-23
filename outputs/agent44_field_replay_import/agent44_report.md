# Agent 44 Field Replay Import 报告

- summary: 现场 replay 导入门：field_replay_import_blocked_non_field_origin；表验收 5/5，可进入 timestamped replay False。
- source_package_type: `synthetic_interface_package`
- source_package_dir: `/Users/chuchenqidawang/Documents/低成本传感循环式水处理智能闭环项目/outputs/field_replay_import/synthetic_replay_import_package`
- preflight_status: `field_package_preflight_blocked_non_field_origin`
- field_replay_import_status: `field_replay_import_blocked_non_field_origin`
- can_pass_to_timestamped_replay: `False`
- can_pass_to_g6: `False`
- optional_supplement_files: `['node_modality_sensor_timeseries.csv', 'site_topology_or_bed_geometry.csv']`
- r7j_supplement_audit: `{'node_modality_sensor_timeseries': {'exists': False, 'status': 'supplement_missing_optional_file', 'expected_headers': ['batch_id', 'timestamp_min', 'node_id', 'zone', 'modality', 'value', 'sensor_status', 'instrument_id', 'acquisition_time_min', 'ingest_time_min'], 'actual_headers': [], 'missing_headers': ['batch_id', 'timestamp_min', 'node_id', 'zone', 'modality', 'value', 'sensor_status', 'instrument_id', 'acquisition_time_min', 'ingest_time_min'], 'row_count': 0, 'field_boundary': 'Optional for Agent44 import, but required by R7j when Agent51 catalyst proxy holdout is evaluated.'}, 'site_topology_or_bed_geometry': {'exists': False, 'status': 'supplement_missing_optional_file', 'expected_headers': ['node_id', 'bed_volume', 'nominal_HRT_min', 'flow_Lmin'], 'actual_headers': [], 'missing_headers': ['node_id', 'bed_volume', 'nominal_HRT_min', 'flow_Lmin'], 'row_count': 0, 'field_boundary': 'Optional for Agent44 import, but required by R7j when Agent51 catalyst proxy holdout is evaluated.'}}`
- template_preflight_status: `field_package_template_ready_needs_real_values_and_rows`
- template_r7j_supplement_audit: `{'node_modality_sensor_timeseries': {'exists': True, 'status': 'supplement_header_ready', 'expected_headers': ['batch_id', 'timestamp_min', 'node_id', 'zone', 'modality', 'value', 'sensor_status', 'instrument_id', 'acquisition_time_min', 'ingest_time_min'], 'actual_headers': ['batch_id', 'timestamp_min', 'node_id', 'zone', 'modality', 'value', 'sensor_status', 'instrument_id', 'acquisition_time_min', 'ingest_time_min'], 'missing_headers': [], 'row_count': 0, 'field_boundary': 'Optional for Agent44 import, but required by R7j when Agent51 catalyst proxy holdout is evaluated.'}, 'site_topology_or_bed_geometry': {'exists': True, 'status': 'supplement_header_ready', 'expected_headers': ['node_id', 'bed_volume', 'nominal_HRT_min', 'flow_Lmin'], 'actual_headers': ['node_id', 'bed_volume', 'nominal_HRT_min', 'flow_Lmin'], 'missing_headers': [], 'row_count': 0, 'field_boundary': 'Optional for Agent44 import, but required by R7j when Agent51 catalyst proxy holdout is evaluated.'}}`

## 生成文件

- field_replay_import_protocol: `/Users/chuchenqidawang/Documents/低成本传感循环式水处理智能闭环项目/deliverables/field_replay_import_protocol.md`
- agent44_report: `/Users/chuchenqidawang/Documents/低成本传感循环式水处理智能闭环项目/outputs/agent44_field_replay_import/agent44_report.md`
- import_acceptance_metrics: `/Users/chuchenqidawang/Documents/低成本传感循环式水处理智能闭环项目/outputs/field_replay_import/import_acceptance_metrics.json`
- preflight_metrics: `/Users/chuchenqidawang/Documents/低成本传感循环式水处理智能闭环项目/outputs/field_replay_import/real_field_package_preflight_metrics.json`
- template_preflight_metrics: `/Users/chuchenqidawang/Documents/低成本传感循环式水处理智能闭环项目/outputs/field_replay_import/real_field_package_template_preflight_metrics.json`
- import_schema: `/Users/chuchenqidawang/Documents/低成本传感循环式水处理智能闭环项目/outputs/field_replay_import/import_schema.json`
- real_field_package_template: `/Users/chuchenqidawang/Documents/低成本传感循环式水处理智能闭环项目/outputs/field_replay_import/real_field_package_template`
- input_replay_package: `/Users/chuchenqidawang/Documents/低成本传感循环式水处理智能闭环项目/outputs/field_replay_import/synthetic_replay_import_package`

## 风险边界

- `non_field_origin_blocked`：现场 replay 包 metadata 未达到 provenance 和 field origin 要求。
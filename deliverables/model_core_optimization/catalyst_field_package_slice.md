# R8u113 Catalyst Field Package Slice

## 定位

该切片把 catalyst_activity 的现场补数范围压缩为四张 CSV 表：`node_modality_sensor_timeseries`、`offline_lab_results`、`campaign_operation_log`、`site_topology_or_bed_geometry`。它服务 R7/Agent51 的真实 field package 补齐，但不替代完整 field package import。

## Readiness

- slice_status: `catalyst_field_package_slice_waiting_for_CATALYST_FIELD_PACKAGE_SLICE_DIR`
- source_env_var: `CATALYST_FIELD_PACKAGE_SLICE_DIR`
- external_slice_supplied: `False`
- slice_preflight_pass: `False`
- matched_batch_count: `0`
- matched_batch_requirement_pass: `False`
- template_dir: `outputs/catalyst_field_package_slice/focused_field_package_slice_template`
- can_route_to_r7_field_package_patch_candidate: `False`
- can_route_to_agent51_field_proxy_holdout: `False`
- can_relax_agent49_catalyst_uncertainty_block: `False`

## Required Tables

| table | planned rows | purpose |
| --- | ---: | --- |
| `node_modality_sensor_timeseries` | 9 | UV254、ORP、pressure_drop 三个低成本/过程代理信号 |
| `offline_lab_results` | 3 | QA-passed catalyst_activity 离线标签 |
| `campaign_operation_log` | 3 | 再生事件和动作时延对齐 |
| `site_topology_or_bed_geometry` | 1 | 床层体积、HRT、流量等几何归一化信息 |

## Blocking Reasons

- `missing_external_slice_dir`

## Boundary

This focused slice can only prepare the catalyst_activity rows for a full R7 field package import. It cannot replace the complete field package, Agent51 field proxy holdout, or field-supported claims.

This focused field package slice cannot authorize actuator writes, release-gate writes, Agent51 field proxy holdout pass, Agent49 guardrail relaxation, or field-supported claims.

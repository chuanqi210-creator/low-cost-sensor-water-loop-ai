# R8u111 Catalyst Response Submission Kit

## 定位

该提交小包把 full field activation response 的 33 行收缩为 catalyst_activity 的 6 行，降低外部人员填写 `FIELD_ACTIVATION_RESPONSE_PATH` 前的扫描摩擦。

## Readiness

- kit_status: `catalyst_response_submission_kit_ready_for_operator_fill`
- target_hidden_state: `catalyst_activity`
- target_response_row_count: `6`
- minimum_matched_batch_count: `3`
- focused_response_template_path: `outputs/catalyst_response_submission_kit/focused_catalyst_response_template.json`
- focused_response_schema_path: `outputs/catalyst_response_submission_kit/focused_catalyst_response_schema.json`
- merge_plan_path: `outputs/catalyst_response_submission_kit/focused_to_full_response_merge_plan.json`
- can_route_to_agent51_field_proxy_holdout: `False`
- can_relax_agent49_catalyst_uncertainty_block: `False`

## Focused Rows

| row | role | required evidence | priority |
| --- | --- | --- | --- |
| `catalyst_activity_03` | `pressure_headloss_proxy` | `node_modality_sensor_timeseries.N3_catalyst_bed:pressure_drop_kPa` | `P1` |
| `catalyst_activity_04` | `catalyst_activity_label` | `offline_lab_results.catalyst_activity` | `P1` |
| `catalyst_activity_05` | `regeneration_event` | `campaign_operation_log.regeneration_event` | `P1` |
| `catalyst_activity_06` | `hydraulic_normalizer` | `site_topology_or_bed_geometry.nominal_HRT_min` | `P1` |
| `catalyst_activity_01` | `bed_outlet_uv254_proxy` | `node_modality_sensor_timeseries.N3_catalyst_bed_outlet:UV254_abs` | `P2` |
| `catalyst_activity_02` | `bed_outlet_orp_proxy` | `node_modality_sensor_timeseries.N3_catalyst_bed_outlet:ORP_mV` | `P2` |

## Merge Plan

- merge_strategy: `replace_rows_by_response_row_id`
- target_full_template_row_count: `33`
- focused_replacement_row_count: `6`
- remaining_full_response_row_count: `27`

## Boundary

The focused template reduces operator scanning from the full 33-row response to six catalyst_activity rows. Filled rows must still be merged into a valid full field activation response or inspected by R8u110; no field claim is created by the template itself.

This focused submission kit cannot authorize actuator writes, release-gate writes, field-supported claims, Agent51 holdout pass, or Agent49 catalyst guardrail relaxation.

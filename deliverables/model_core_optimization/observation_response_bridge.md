# R8u109 Observation Response Bridge

## 定位

该桥把 R2/Agent48/51/54 的观测弱轴需求映射到 R8u108 field activation response template 中的优先响应行，避免现场补证时在完整模板里重新扫描 catalyst_activity 证据。

## Readiness

- bridge_status: `observation_response_bridge_ready_for_priority_field_response_fill`
- target_hidden_states: `['catalyst_activity']`
- response_row_count: `6`
- required_role_coverage_rate: `1.0`
- missing_required_roles: `[]`
- response_submission_packet_status: `field_activation_response_submission_packet_waiting_for_external_response`
- response_submission_next_operator_action: `fill_response_template_and_set_FIELD_ACTIVATION_RESPONSE_PATH`
- can_route_to_agent51_field_proxy_holdout: `False`
- can_relax_agent49_catalyst_uncertainty_block: `False`
- can_write_to_actuator: `False`
- can_write_to_release_gate: `False`

## Priority Response Rows

| row | role | priority | table | field |
| --- | --- | --- | --- | --- |
| `catalyst_activity_03` | `pressure_headloss_proxy` | `P1` | `node_modality_sensor_timeseries` | `N3_catalyst_bed:pressure_drop_kPa` |
| `catalyst_activity_04` | `catalyst_activity_label` | `P1` | `offline_lab_results` | `catalyst_activity` |
| `catalyst_activity_05` | `regeneration_event` | `P1` | `campaign_operation_log` | `regeneration_event` |
| `catalyst_activity_06` | `hydraulic_normalizer` | `P1` | `site_topology_or_bed_geometry` | `nominal_HRT_min` |
| `catalyst_activity_01` | `bed_outlet_uv254_proxy` | `P2` | `node_modality_sensor_timeseries` | `N3_catalyst_bed_outlet:UV254_abs` |
| `catalyst_activity_02` | `bed_outlet_orp_proxy` | `P2` | `node_modality_sensor_timeseries` | `N3_catalyst_bed_outlet:ORP_mV` |

## Batch Alignment

The response rows identify which field evidence must be submitted first, but batch alignment is proved only when at least 3 real field batch_id values are matched across node_modality_sensor_timeseries, offline_lab_results, campaign_operation_log and site_topology_or_bed_geometry. A filled response JSON alone is not field validation.

## No-Write Boundary

This bridge only prioritizes existing observation-contract evidence rows inside the field activation response template. It does not create field evidence, does not validate catalyst activity, does not relax Agent49 guardrails, and cannot write actuator policy or release gate.

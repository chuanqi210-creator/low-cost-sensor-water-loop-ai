# R4 控制 Guardrail 失败案例反写：灰箱机制与现场字段

- status：`synthetic_guardrail_backpropagation_ready_needs_field_replay_and_grey_box_calibration`
- resolved_case_count：`2`
- resolved_case_to_mechanism_coverage：`1.0`
- resolved_case_to_field_requirement_coverage：`1.0`
- grey_box_failure_boundary_count：`6`
- field_replay_required_field_count：`12`
- field_replay_coverage：`0.0`
- can_write_to_actuator：`False`

## Resolved Case Backpropagation

| Case | Scenario | Mechanism Family | Guardrail Action | Field Fields | Claim Boundary |
| --- | --- | --- | --- | --- | --- |
| `R2` | catalyst_uncertain_low_proxy | `catalyst_activity_proxy_uncertainty` | `J4_safe_low_cost_standby` | proxy_holdout_label, pressure_drop_kPa, regeneration_event, operator_override, N3_catalyst_bed_outlet:UV254_abs, N3_catalyst_bed_outlet:turbidity_NTU | synthetic guardrail resolved false-positive catalyst protection; field proxy labels are required before catalyst-control claim upgrade. |
| `R5` | hydraulic_delay_violation | `hydraulic_latency_and_storage_uncertainty` | `J3_polishing_and_release_gate` | tank_storage_margin, actuator_latency_p90, pump_valve_result, flow_Lmin, hold_time_min, recycle_ratio | synthetic guardrail resolved high-regret recycle action; field hydraulic replay is required before recycle-control claim upgrade. |

## Grey-Box Patch

### catalyst_uncertain_low_proxy

- mechanism_family：`catalyst_activity_proxy_uncertainty`
- control_implication：keep J4_safe_low_cost_standby or human-reviewed catalyst protection until field proxy labels close the uncertainty.
- field_boundary：synthetic guardrail resolved false-positive catalyst protection; field proxy labels are required before catalyst-control claim upgrade.
- grey_box_boundary：
  - catalyst activity cannot be treated as observed without proxy holdout label
  - protective/regeneration actions require pressure-drop or lifecycle evidence
  - matrix inhibition and catalyst deactivation must remain separable hypotheses

### hydraulic_delay_violation

- mechanism_family：`hydraulic_latency_and_storage_uncertainty`
- control_implication：prefer J3_polishing_and_release_gate over recycle escalation until hydraulic execution evidence exists.
- field_boundary：synthetic guardrail resolved high-regret recycle action; field hydraulic replay is required before recycle-control claim upgrade.
- grey_box_boundary：
  - recycle escalation is unsafe when residence-time delay and storage margin are unobserved
  - latency budget must include actuator response, pump-valve result and tank capacity
  - loop retention benefit must be checked against polishing/release-gate alternative

## Field Requirement Patch

- `catalyst_uncertain_low_proxy`：proxy_holdout_label, pressure_drop_kPa, regeneration_event, operator_override, N3_catalyst_bed_outlet:UV254_abs, N3_catalyst_bed_outlet:turbidity_NTU
- `hydraulic_delay_violation`：tank_storage_margin, actuator_latency_p90, pump_valve_result, flow_Lmin, hold_time_min, recycle_ratio

## 边界

- 本结果只把 synthetic guardrail replay 失败案例反写为机制边界和采集字段。
- field_replay_coverage 仍为 0 时，不能宣称现场控制有效、灰箱参数已校准或可写执行器。
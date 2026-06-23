# Field Control Replay Package Preflight

## Role

This preflight checks whether an external `FIELD_CONTROL_REPLAY_PACKAGE_DIR` can be routed to Agent49/Agent52 as field state-action replay input. It is an offline evaluation gate, not a live-control authorization.

## Status

- package_status: `field_control_replay_package_waiting_for_FIELD_CONTROL_REPLAY_PACKAGE_DIR`
- source_env_var: `FIELD_CONTROL_REPLAY_PACKAGE_DIR`
- source_path: ``
- package_preflight_pass: `False`
- matched_transition_count: `0`
- minimum_matched_transition_count: `3`
- field_control_replay_coverage_candidate: `0.0`
- reward_component_count: `0`
- mean_actuator_latency_min: `None`
- unsafe_or_override_transition_count: `0`
- can_route_to_agent49_field_control_replay: `False`
- can_route_to_agent52_policy_replay_evaluation: `False`
- can_authorize_policy_promotion: `False`
- can_generate_field_evidence: `False`
- can_write_to_actuator: `False`
- can_write_to_release_gate: `False`
- next_operator_action: `fill_field_control_replay_package_template_and_set_FIELD_CONTROL_REPLAY_PACKAGE_DIR`

## Required Tables

| table | rows | missing columns | template markers | non-field rows |
| --- | --- | --- | --- | --- |
| `state_action_next_state_rows` | `0` | `[]` | `0` | `0` |
| `reward_component_rows` | `0` | `[]` | `0` | `0` |
| `operator_or_expert_action_labels` | `0` | `[]` | `0` | `0` |
| `actuator_latency_and_result_rows` | `0` | `[]` | `0` | `0` |
| `unsafe_action_or_override_events` | `0` | `[]` | `0` | `0` |

## Signal Audits

| signal | valid rows | valid transition ids |
| --- | --- | --- |
| `state_action_transition` | `0` | `[]` |
| `reward_component` | `0` | `[]` |
| `operator_expert_action_label` | `0` | `[]` |
| `actuator_latency_result` | `0` | `[]` |
| `unsafe_override_event` | `0` | `[]` |

## Blocking Reasons

- `missing_external_package_dir`

## Template Location

- template_dir: `outputs/field_control_replay_package/field_control_replay_package_template`
- required_table_count: `5`

## Boundary

This preflight only checks whether an external field control replay package is ready for Agent49/Agent52 offline evaluation. Passing this gate does not prove policy superiority, authorize live actuator writes, relax safety guardrails or open release-gate decisions.

This package is only a field control replay preflight input. It cannot write actuator policy, release-gate policy, live control approval, policy-promotion claims or deployment clearance.

# Field Missingness Replay Package Preflight

## Role

This preflight checks whether an external `FIELD_MISSINGNESS_REPLAY_PACKAGE_DIR` can be routed to Agent54 as field missingness replay input for soft-sensor holdout work. It is not a field soft-sensor performance result.

## Status

- package_status: `field_missingness_replay_package_waiting_for_FIELD_MISSINGNESS_REPLAY_PACKAGE_DIR`
- source_env_var: `FIELD_MISSINGNESS_REPLAY_PACKAGE_DIR`
- source_path: ``
- package_preflight_pass: `False`
- matched_sample_count: `0`
- minimum_matched_sample_count: `3`
- field_missingness_replay_coverage_candidate: `0.0`
- unavailable_sample_count: `0`
- mean_sensor_quality_score: `None`
- hidden_state_count: `0`
- can_route_to_agent54_field_missingness_replay: `False`
- can_route_to_soft_sensor_missingness_holdout: `False`
- can_generate_field_evidence: `False`
- can_write_to_actuator: `False`
- can_write_to_release_gate: `False`
- next_operator_action: `fill_field_missingness_replay_package_template_and_set_FIELD_MISSINGNESS_REPLAY_PACKAGE_DIR`

## Required Tables

| table | rows | missing columns | template markers | non-field rows |
| --- | --- | --- | --- | --- |
| `node_modality_time_series` | `0` | `[]` | `0` | `0` |
| `availability_mask` | `0` | `[]` | `0` | `0` |
| `time_since_last_observed_min` | `0` | `[]` | `0` | `0` |
| `sensor_quality_status` | `0` | `[]` | `0` | `0` |
| `offline_hidden_state_labels` | `0` | `[]` | `0` | `0` |

## Signal Audits

| signal | valid rows | valid sample ids |
| --- | --- | --- |
| `node_modality_time_series` | `0` | `[]` |
| `availability_mask` | `0` | `[]` |
| `time_since_last_observed` | `0` | `[]` |
| `sensor_quality_status` | `0` | `[]` |
| `offline_hidden_state_label` | `0` | `[]` |

## Blocking Reasons

- `missing_external_package_dir`

## Template Location

- template_dir: `outputs/field_missingness_replay_package/field_missingness_replay_package_template`
- required_table_count: `5`

## Boundary

This preflight only checks whether an external field missingness replay package is ready for soft-sensor missingness holdout work. Passing this gate does not prove field soft-sensor accuracy, authorize release decisions, or relax actuator guardrails.

This package is only a field missingness replay preflight input. It cannot write soft-sensor field performance claims, actuator policy, release-gate policy or deployment clearance.

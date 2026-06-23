# Grey-Box Calibration Package Preflight

## Role

This preflight checks whether an external `GREY_BOX_CALIBRATION_PACKAGE_DIR` can be routed to Agent53 field calibration. It is not a field-validation result.

## Status

- package_status: `grey_box_calibration_package_waiting_for_GREY_BOX_CALIBRATION_PACKAGE_DIR`
- source_env_var: `GREY_BOX_CALIBRATION_PACKAGE_DIR`
- source_path: ``
- package_preflight_pass: `False`
- matched_batch_count: `0`
- minimum_matched_batch_count: `3`
- field_physics_coverage_candidate: `0.0`
- can_route_to_agent53_field_calibration: `False`
- can_generate_field_evidence: `False`
- can_write_to_actuator: `False`
- can_write_to_release_gate: `False`
- next_operator_action: `fill_grey_box_calibration_package_template_and_set_GREY_BOX_CALIBRATION_PACKAGE_DIR`

## Agent53 Field Calibration Summary

- summary_status: `grey_box_field_calibration_waiting_for_preflight_ready`
- computable_batch_count: `0`
- can_run_agent53_field_calibration: `False`
- agent53_field_candidate_ready: `False`
- field_calibration_for_agent53: `{'field_physics_coverage': 0.0, 'max_field_residual': 1.0, 'max_mass_balance_residual': 1.0, 'mean_observed_k_per_min': 0.0, 'mean_observed_removal_fraction': 0.0, 'max_byproduct_load_fraction_proxy': 1.0}`
- summary_next_operator_action: `complete_grey_box_calibration_package_preflight_before_building_field_calibration_summary`

## Required Tables

| table | rows | missing columns | template markers | non-field rows |
| --- | --- | --- | --- | --- |
| `batch_inlet_outlet_lab` | `0` | `[]` | `0` | `0` |
| `hydraulic_rtd_or_tracer` | `0` | `[]` | `0` | `0` |
| `oxidant_dose_residual_log` | `0` | `[]` | `0` | `0` |
| `catalyst_age_regeneration_log` | `0` | `[]` | `0` | `0` |
| `byproduct_panel` | `0` | `[]` | `0` | `0` |

## Signal Audits

| signal | valid rows | valid batch ids |
| --- | --- | --- |
| `lab_pair` | `0` | `[]` |
| `hydraulic_rtd` | `0` | `[]` |
| `oxidant_dose_residual` | `0` | `[]` |
| `catalyst_history` | `0` | `[]` |
| `byproduct_panel` | `0` | `[]` |

## Blocking Reasons

- `missing_external_package_dir`

## Template Location

- template_dir: `outputs/grey_box_calibration_package/grey_box_calibration_package_template`
- required_table_count: `5`

## Boundary

This preflight only checks whether a grey-box calibration package is structurally ready for Agent53 field calibration. Passing this gate does not prove mechanism validity, field-supported claims, actuator readiness or release readiness.

This package is only a grey-box calibration preflight input. It cannot write actuator policy, release-gate policy, field-supported mechanism claims or deployment clearance.

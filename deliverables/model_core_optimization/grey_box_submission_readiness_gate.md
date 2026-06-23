# Grey-Box Submission Readiness Gate

## Role

This gate converts the grey-box calibration package preflight, field calibration summary and collection work order into one submission-readiness score for `GREY_BOX_CALIBRATION_PACKAGE_DIR`.

## State

- gate_id: `R8u160_grey_box_submission_readiness_gate`
- gate_status: `grey_box_submission_readiness_waiting_for_external_package`
- readiness_score: `0.143`
- source_env_var: `GREY_BOX_CALIBRATION_PACKAGE_DIR`
- matched_batch_count: `0`
- computable_batch_count: `0`
- can_submit_to_agent53_field_calibration: `False`
- can_submit_to_agent53_field_candidate: `False`
- next_operator_action: `fill_grey_box_calibration_package_template_and_set_GREY_BOX_CALIBRATION_PACKAGE_DIR`

## Component Scores

| component | score |
| --- | --- |
| `source_package_present` | `0.0` |
| `schema_completeness` | `0.0` |
| `field_origin_integrity` | `0.0` |
| `matched_batch_coverage` | `0.0` |
| `signal_validity_coverage` | `0.0` |
| `agent53_summary_readiness` | `0.0` |
| `residual_threshold_readiness` | `0.0` |
| `no_write_boundary_integrity` | `1.0` |
| `submitted_table_presence` | `0.0` |

## Highest Priority Gap

- gap_type: `missing_external_package`
- table: `all_required_tables`
- missing_table_count: `5`
- missing_tables: `['batch_inlet_outlet_lab', 'hydraulic_rtd_or_tracer', 'oxidant_dose_residual_log', 'catalyst_age_regeneration_log', 'byproduct_panel']`
- next_action: `fill_grey_box_calibration_package_template_and_set_GREY_BOX_CALIBRATION_PACKAGE_DIR`

## Boundary

This gate scores package submission readiness only. It can route a package to Agent53 field calibration when inputs are complete, but it cannot generate field evidence, prove mechanism validity, authorize actuator writes, authorize release-gate writes or emit field-supported claims.

This package is only a grey-box calibration preflight input. It cannot write actuator policy, release-gate policy, field-supported mechanism claims or deployment clearance.

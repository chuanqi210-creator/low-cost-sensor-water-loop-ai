# Grey-Box Calibration Collection Work Order

## Role

This work order turns the next external package action into a table-level collection checklist for `GREY_BOX_CALIBRATION_PACKAGE_DIR`.

## Work Order State

- work_order_id: `R8u157_grey_box_calibration_collection_work_order`
- work_order_status: `grey_box_calibration_collection_work_order_waiting_for_external_package`
- source_env_var: `GREY_BOX_CALIBRATION_PACKAGE_DIR`
- source_path: ``
- template_dir: `outputs/grey_box_calibration_package/grey_box_calibration_package_template`
- validation_command: `.venv/bin/python experiments/run_grey_box_calibration_package_preflight.py`
- minimum_matched_batch_count: `3`
- matched_batch_count: `0`
- field_package_ready_for_agent53: `False`
- agent53_field_candidate_ready: `False`
- next_operator_action: `fill_grey_box_calibration_package_template_and_set_GREY_BOX_CALIBRATION_PACKAGE_DIR`
- can_generate_field_evidence: `False`
- can_resume_model_chain: `False`
- can_write_to_actuator: `False`
- can_write_to_release_gate: `False`

## Table Work Items

| table | status | template csv | required columns | valid rows | template markers | non-field rows |
| --- | --- | --- | --- | --- | --- | --- |
| `batch_inlet_outlet_lab` | `needs_real_field_rows` | `outputs/grey_box_calibration_package/grey_box_calibration_package_template/batch_inlet_outlet_lab.csv` | `batch_id, sample_time_min, target_pollutant, inlet_concentration, outlet_concentration, pollutant_unit, matrix_indicator, matrix_indicator_unit, lab_method, qa_flag, data_origin` | `0` | `0` | `0` |
| `hydraulic_rtd_or_tracer` | `needs_real_field_rows` | `outputs/grey_box_calibration_package/grey_box_calibration_package_template/hydraulic_rtd_or_tracer.csv` | `batch_id, measurement_time_min, unit_id, effective_HRT_min, nominal_HRT_min, rtd_t10_min, rtd_t90_min, tracer_recovery_fraction, flow_Lmin, volume_L, qa_flag, data_origin` | `0` | `0` | `0` |
| `oxidant_dose_residual_log` | `needs_real_field_rows` | `outputs/grey_box_calibration_package/grey_box_calibration_package_template/oxidant_dose_residual_log.csv` | `batch_id, timestamp_min, oxidant_name, dose_mg_L, residual_mg_L, energy_kWh_m3, qa_flag, data_origin` | `0` | `0` | `0` |
| `catalyst_age_regeneration_log` | `needs_real_field_rows` | `outputs/grey_box_calibration_package/grey_box_calibration_package_template/catalyst_age_regeneration_log.csv` | `batch_id, timestamp_min, catalyst_id, catalyst_age_h, catalyst_activity_label, regeneration_event, regeneration_count, qa_flag, data_origin` | `0` | `0` | `0` |
| `byproduct_panel` | `needs_real_field_rows` | `outputs/grey_box_calibration_package/grey_box_calibration_package_template/byproduct_panel.csv` | `batch_id, sample_time_min, analyte, value, unit, detection_limit, method, qa_flag, data_origin` | `0` | `0` | `0` |

## Acceptance Criteria

- All five required CSV tables exist with the required headers.
- Every submitted row uses data_origin=field and an accepted qa_flag.
- Template markers and TODO values are removed before preflight.
- At least three shared batch_id values pass lab, hydraulic, oxidant, catalyst and byproduct audits.
- Passing this work order only routes the package to Agent53 field calibration; it does not prove the mechanism.

## Boundary

This work order only guides external field package collection for grey-box calibration. It cannot resume the model chain, cannot generate field evidence, cannot prove mechanism validity and cannot authorize actuator or release-gate writes.

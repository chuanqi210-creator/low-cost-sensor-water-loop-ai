# External Package Acquisition Maturity Gate

## Gate State

- gate_id: `R8u156_external_package_acquisition_maturity_gate`
- gate_status: `external_package_acquisition_interfaces_ready_waiting_for_field_packages`
- acquisition_maturity_score: `0.85`
- field_package_ready_rate: `0.0`
- interface_preflight_coverage: `1.0`
- operator_action_contract_coverage: `1.0`
- no_write_boundary_integrity: `1.0`
- input_contract_completeness: `1.0`
- output_contract_completeness: `1.0`
- handoff_state_variable_coverage: `1.0`
- downstream_reconnection_rate: `0.0`
- evidence_boundary_completeness: `1.0`
- failure_boundary_completeness: `1.0`
- no_write_boundary_completeness: `1.0`
- contract_termination_status: `external_package_contracts_complete_but_waiting_for_field_packages`
- module_stage_termination_pass: `False`
- termination_blockers: `['downstream_reconnection_rate_below_0.80', 'field_package_ready_rate_below_1.00']`
- next_stage_decision: `collect_external_field_packages_before_downstream_gates`
- next_operator_source_env_var: `GREY_BOX_CALIBRATION_PACKAGE_DIR`
- next_operator_validation_command: `.venv/bin/python experiments/run_grey_box_calibration_package_preflight.py`
- model_chain_resume_ready: `False`
- can_generate_field_evidence: `False`
- can_write_to_actuator: `False`
- can_write_to_release_gate: `False`

## Boundary

This gate scores collection-interface maturity only. It cannot resume the model chain, cannot generate field evidence, cannot run downstream replay/holdout/calibration and cannot authorize actuator or release-gate writes.

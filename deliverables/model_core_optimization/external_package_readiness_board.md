# External Package Readiness Board

## Role

This board aggregates the new-core external package interfaces into one field-submission queue. It is a readiness and routing artifact, not a field validation result.

## Board State

- board_id: `R8u154_external_package_readiness_board`
- source_gate_status: `new_core_interface_candidate_gate_ready_with_ranked_contracts`
- package_count: `5`
- ready_package_count: `0`
- waiting_package_count: `5`
- blocked_package_count: `0`
- unimplemented_package_count: `0`
- all_candidate_interfaces_have_preflight: `True`
- next_operator_candidate_id: `NCI1_GREY_BOX_CALIBRATION_PACKAGE`
- next_operator_source_env_var: `GREY_BOX_CALIBRATION_PACKAGE_DIR`
- next_operator_action: `complete_grey_box_calibration_package_preflight_before_building_field_calibration_summary`
- can_generate_field_evidence: `False`
- can_write_to_actuator: `False`
- can_write_to_release_gate: `False`

## Package Rows

| order | candidate | task | env var | status | pass | matched | template | missing tables | validation command | next action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `1` | `NCI1_GREY_BOX_CALIBRATION_PACKAGE` | `P4_minimal_grey_box_physics` | `GREY_BOX_CALIBRATION_PACKAGE_DIR` | `grey_box_calibration_package_waiting_for_GREY_BOX_CALIBRATION_PACKAGE_DIR` | `False` | `none` | `outputs/grey_box_calibration_package/grey_box_calibration_package_template` | `5` | `.venv/bin/python experiments/run_grey_box_calibration_package_preflight.py` | `complete_grey_box_calibration_package_preflight_before_building_field_calibration_summary` |
| `4` | `NCI5_FIELD_SUPPORTED_KG_EDGE_PACKAGE` | `P6_reasonable_knowledge_graph_upgrade` | `FIELD_SUPPORTED_KG_EDGE_PACKAGE_DIR` | `field_supported_kg_edge_package_waiting_for_FIELD_SUPPORTED_KG_EDGE_PACKAGE_DIR` | `False` | `none` | `outputs/field_supported_kg_edge_package/field_supported_kg_edge_package_template` | `` | `.venv/bin/python experiments/run_field_supported_kg_edge_preflight.py` | `fill_field_supported_kg_edge_package_template_and_set_FIELD_SUPPORTED_KG_EDGE_PACKAGE_DIR` |
| `7` | `NCI3_FIELD_CONTROL_REPLAY_PACKAGE` | `P3_agent49_replay_ready_offline_evaluation` | `FIELD_CONTROL_REPLAY_PACKAGE_DIR` | `field_control_replay_package_waiting_for_FIELD_CONTROL_REPLAY_PACKAGE_DIR` | `False` | `none` | `outputs/field_control_replay_package/field_control_replay_package_template` | `` | `.venv/bin/python experiments/run_field_control_replay_preflight.py` | `fill_field_control_replay_package_template_and_set_FIELD_CONTROL_REPLAY_PACKAGE_DIR` |
| `9` | `NCI4_SPARSE_TOPOLOGY_INSTALLABILITY_PACKAGE` | `P1_agent48_comparable_sparse_sensor_placement` | `SPARSE_TOPOLOGY_INSTALLABILITY_PACKAGE_DIR` | `sparse_topology_installability_package_waiting_for_SPARSE_TOPOLOGY_INSTALLABILITY_PACKAGE_DIR` | `False` | `none` | `outputs/sparse_topology_installability_package/sparse_topology_installability_package_template` | `` | `.venv/bin/python experiments/run_sparse_topology_installability_preflight.py` | `fill_sparse_topology_installability_package_template_and_set_SPARSE_TOPOLOGY_INSTALLABILITY_PACKAGE_DIR` |
| `10` | `NCI2_FIELD_MISSINGNESS_REPLAY_PACKAGE` | `P5_soft_sensor_node_modality_missingness` | `FIELD_MISSINGNESS_REPLAY_PACKAGE_DIR` | `field_missingness_replay_package_waiting_for_FIELD_MISSINGNESS_REPLAY_PACKAGE_DIR` | `False` | `none` | `outputs/field_missingness_replay_package/field_missingness_replay_package_template` | `` | `.venv/bin/python experiments/run_field_missingness_replay_preflight.py` | `fill_field_missingness_replay_package_template_and_set_FIELD_MISSINGNESS_REPLAY_PACKAGE_DIR` |

## Collection Groups

- `state_estimation_and_grey_box`: candidates=['NCI1_GREY_BOX_CALIBRATION_PACKAGE'], source_env_vars=['GREY_BOX_CALIBRATION_PACKAGE_DIR'], readiness=`waiting_for_external_package`
- `mechanism_evidence_kg`: candidates=['NCI5_FIELD_SUPPORTED_KG_EDGE_PACKAGE'], source_env_vars=['FIELD_SUPPORTED_KG_EDGE_PACKAGE_DIR'], readiness=`waiting_for_external_package`
- `control_replay_execution`: candidates=['NCI3_FIELD_CONTROL_REPLAY_PACKAGE'], source_env_vars=['FIELD_CONTROL_REPLAY_PACKAGE_DIR'], readiness=`waiting_for_external_package`
- `sparse_observation_layout`: candidates=['NCI4_SPARSE_TOPOLOGY_INSTALLABILITY_PACKAGE'], source_env_vars=['SPARSE_TOPOLOGY_INSTALLABILITY_PACKAGE_DIR'], readiness=`waiting_for_external_package`
- `soft_sensor_missingness`: candidates=['NCI2_FIELD_MISSINGNESS_REPLAY_PACKAGE'], source_env_vars=['FIELD_MISSINGNESS_REPLAY_PACKAGE_DIR'], readiness=`waiting_for_external_package`

## Boundary

This board aggregates external package readiness. It does not validate field performance, does not run downstream replay/holdout/calibration, and does not authorize actuator or release-gate actions.

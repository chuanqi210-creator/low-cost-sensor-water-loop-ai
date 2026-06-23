# New Core Interface Candidate Gate

## Role

This gate turns the generic `NEW_CORE_INTERFACE` stage-boundary option into a ranked list of concrete, testable interface contracts. It is a routing and architecture gate, not a field-validation result.

## Gate State

- gate_id: `R8u147_new_core_interface_candidate_gate`
- gate_status: `new_core_interface_candidate_gate_ready_with_ranked_contracts`
- stage_decision: `stop_expansion_wait_for_real_field_package_or_new_core_interface`
- candidate_count: `5`
- admissible_candidate_count: `5`
- highest_priority_candidate_id: `NCI1_GREY_BOX_CALIBRATION_PACKAGE`
- highest_priority_source_env_var: `GREY_BOX_CALIBRATION_PACKAGE_DIR`
- highest_priority_validation_command: `.venv/bin/python experiments/run_grey_box_calibration_package_preflight.py`
- highest_priority_preflight_status: `grey_box_calibration_package_waiting_for_GREY_BOX_CALIBRATION_PACKAGE_DIR`
- highest_priority_preflight_pass: `False`
- highest_priority_can_route_to_downstream_calibration: `False`
- highest_priority_can_route_to_downstream_interface: `False`
- highest_priority_downstream_calibration_status: `grey_box_field_calibration_waiting_for_preflight_ready`
- highest_priority_downstream_interface_status: `grey_box_field_calibration_waiting_for_preflight_ready`
- highest_priority_can_run_agent53_field_calibration: `False`
- highest_priority_agent53_field_candidate_ready: `False`
- can_generate_field_evidence: `False`
- can_write_to_actuator: `False`
- can_write_to_release_gate: `False`

## Candidate Rows

| order | candidate | task | status | preflight | env var | layer | ability | minimum rows | next interface action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `1` | `NCI1_GREY_BOX_CALIBRATION_PACKAGE` | `P4_minimal_grey_box_physics` | `admissible_contract_candidate_waiting_for_interface_preflight` | `grey_box_calibration_package_waiting_for_GREY_BOX_CALIBRATION_PACKAGE_DIR` | `GREY_BOX_CALIBRATION_PACKAGE_DIR` | `state_estimation_and_grey_box_physics` | `verifiability_and_explainability` | `3` | `complete_grey_box_calibration_package_preflight_before_building_field_calibration_summary` |
| `4` | `NCI5_FIELD_SUPPORTED_KG_EDGE_PACKAGE` | `P6_reasonable_knowledge_graph_upgrade` | `admissible_contract_candidate_waiting_for_interface_preflight` | `field_supported_kg_edge_package_waiting_for_FIELD_SUPPORTED_KG_EDGE_PACKAGE_DIR` | `FIELD_SUPPORTED_KG_EDGE_PACKAGE_DIR` | `mechanism_evidence_and_knowledge_graph` | `explainability_and_verifiability` | `3` | `fill_field_supported_kg_edge_package_template_and_set_FIELD_SUPPORTED_KG_EDGE_PACKAGE_DIR` |
| `7` | `NCI3_FIELD_CONTROL_REPLAY_PACKAGE` | `P3_agent49_replay_ready_offline_evaluation` | `admissible_contract_candidate_waiting_for_interface_preflight` | `field_control_replay_package_waiting_for_FIELD_CONTROL_REPLAY_PACKAGE_DIR` | `FIELD_CONTROL_REPLAY_PACKAGE_DIR` | `diagnosis_decision_and_closed_loop_execution` | `controllability_and_engineering_feasibility` | `3` | `fill_field_control_replay_package_template_and_set_FIELD_CONTROL_REPLAY_PACKAGE_DIR` |
| `9` | `NCI4_SPARSE_TOPOLOGY_INSTALLABILITY_PACKAGE` | `P1_agent48_comparable_sparse_sensor_placement` | `admissible_contract_candidate_waiting_for_interface_preflight` | `sparse_topology_installability_package_waiting_for_SPARSE_TOPOLOGY_INSTALLABILITY_PACKAGE_DIR` | `SPARSE_TOPOLOGY_INSTALLABILITY_PACKAGE_DIR` | `observation_sparse_sensing_and_topology` | `observability_and_engineering_feasibility` | `3` | `fill_sparse_topology_installability_package_template_and_set_SPARSE_TOPOLOGY_INSTALLABILITY_PACKAGE_DIR` |
| `10` | `NCI2_FIELD_MISSINGNESS_REPLAY_PACKAGE` | `P5_soft_sensor_node_modality_missingness` | `admissible_contract_candidate_waiting_for_interface_preflight` | `field_missingness_replay_package_waiting_for_FIELD_MISSINGNESS_REPLAY_PACKAGE_DIR` | `FIELD_MISSINGNESS_REPLAY_PACKAGE_DIR` | `observation_and_soft_sensor_state_estimation` | `observability_and_verifiability` | `3` | `fill_field_missingness_replay_package_template_and_set_FIELD_MISSINGNESS_REPLAY_PACKAGE_DIR` |

## Boundary

This gate ranks possible new core interfaces. It does not implement the interface, does not validate field data and does not authorize any control or release action.

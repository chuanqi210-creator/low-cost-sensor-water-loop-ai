# External Package Operator Action Packet

## Role

This packet turns the external package readiness board into an ordered field-package collection queue. It does not generate field evidence.

## Packet State

- packet_id: `R8u155_external_package_operator_action_packet`
- packet_status: `external_package_operator_packet_waiting_for_field_packages`
- route_event: `external_activation_wait`
- route_reason: `waiting_for_real_external_package_before_downstream_replay_holdout_calibration`
- evidence_level: `operator_handoff_only_not_field_evidence`
- package_count: `5`
- ready_package_count: `0`
- waiting_package_count: `5`
- blocked_package_count: `0`
- next_operator_candidate_id: `NCI1_GREY_BOX_CALIBRATION_PACKAGE`
- next_operator_source_env_var: `GREY_BOX_CALIBRATION_PACKAGE_DIR`
- next_operator_validation_command: `.venv/bin/python experiments/run_grey_box_calibration_package_preflight.py`
- next_operator_template_dir: `outputs/grey_box_calibration_package/grey_box_calibration_package_template`
- next_operator_missing_table_count: `5`
- next_operator_missing_tables: `['batch_inlet_outlet_lab', 'hydraulic_rtd_or_tracer', 'oxidant_dose_residual_log', 'catalyst_age_regeneration_log', 'byproduct_panel']`
- manual_action_required: `True`
- can_generate_field_evidence: `False`
- can_write_to_actuator: `False`
- can_write_to_release_gate: `False`

## Operator Actions

| order | candidate | env var | action status | template | validation command | missing tables | next action |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `1` | `NCI1_GREY_BOX_CALIBRATION_PACKAGE` | `GREY_BOX_CALIBRATION_PACKAGE_DIR` | `collect_external_package` | `outputs/grey_box_calibration_package/grey_box_calibration_package_template` | `.venv/bin/python experiments/run_grey_box_calibration_package_preflight.py` | `5` | `complete_grey_box_calibration_package_preflight_before_building_field_calibration_summary` |
| `4` | `NCI5_FIELD_SUPPORTED_KG_EDGE_PACKAGE` | `FIELD_SUPPORTED_KG_EDGE_PACKAGE_DIR` | `collect_external_package` | `outputs/field_supported_kg_edge_package/field_supported_kg_edge_package_template` | `.venv/bin/python experiments/run_field_supported_kg_edge_preflight.py` | `` | `fill_field_supported_kg_edge_package_template_and_set_FIELD_SUPPORTED_KG_EDGE_PACKAGE_DIR` |
| `7` | `NCI3_FIELD_CONTROL_REPLAY_PACKAGE` | `FIELD_CONTROL_REPLAY_PACKAGE_DIR` | `collect_external_package` | `outputs/field_control_replay_package/field_control_replay_package_template` | `.venv/bin/python experiments/run_field_control_replay_preflight.py` | `` | `fill_field_control_replay_package_template_and_set_FIELD_CONTROL_REPLAY_PACKAGE_DIR` |
| `9` | `NCI4_SPARSE_TOPOLOGY_INSTALLABILITY_PACKAGE` | `SPARSE_TOPOLOGY_INSTALLABILITY_PACKAGE_DIR` | `collect_external_package` | `outputs/sparse_topology_installability_package/sparse_topology_installability_package_template` | `.venv/bin/python experiments/run_sparse_topology_installability_preflight.py` | `` | `fill_sparse_topology_installability_package_template_and_set_SPARSE_TOPOLOGY_INSTALLABILITY_PACKAGE_DIR` |
| `10` | `NCI2_FIELD_MISSINGNESS_REPLAY_PACKAGE` | `FIELD_MISSINGNESS_REPLAY_PACKAGE_DIR` | `collect_external_package` | `outputs/field_missingness_replay_package/field_missingness_replay_package_template` | `.venv/bin/python experiments/run_field_missingness_replay_preflight.py` | `` | `fill_field_missingness_replay_package_template_and_set_FIELD_MISSINGNESS_REPLAY_PACKAGE_DIR` |

## Commands

- `fill outputs/grey_box_calibration_package/grey_box_calibration_package_template with real field rows`
- `export GREY_BOX_CALIBRATION_PACKAGE_DIR=/absolute/path/to/NCI1_GREY_BOX_CALIBRATION_PACKAGE`
- `.venv/bin/python experiments/run_grey_box_calibration_package_preflight.py`
- `fill outputs/field_supported_kg_edge_package/field_supported_kg_edge_package_template with real field rows`
- `export FIELD_SUPPORTED_KG_EDGE_PACKAGE_DIR=/absolute/path/to/NCI5_FIELD_SUPPORTED_KG_EDGE_PACKAGE`
- `.venv/bin/python experiments/run_field_supported_kg_edge_preflight.py`
- `fill outputs/field_control_replay_package/field_control_replay_package_template with real field rows`
- `export FIELD_CONTROL_REPLAY_PACKAGE_DIR=/absolute/path/to/NCI3_FIELD_CONTROL_REPLAY_PACKAGE`
- `.venv/bin/python experiments/run_field_control_replay_preflight.py`
- `fill outputs/sparse_topology_installability_package/sparse_topology_installability_package_template with real field rows`
- `export SPARSE_TOPOLOGY_INSTALLABILITY_PACKAGE_DIR=/absolute/path/to/NCI4_SPARSE_TOPOLOGY_INSTALLABILITY_PACKAGE`
- `.venv/bin/python experiments/run_sparse_topology_installability_preflight.py`
- `fill outputs/field_missingness_replay_package/field_missingness_replay_package_template with real field rows`
- `export FIELD_MISSINGNESS_REPLAY_PACKAGE_DIR=/absolute/path/to/NCI2_FIELD_MISSINGNESS_REPLAY_PACKAGE`
- `.venv/bin/python experiments/run_field_missingness_replay_preflight.py`

## Rejection Rules

- Reject template rows, sample rows, literature-only rows and synthetic rows as field packages.
- Reject package directories that do not pass the package-specific preflight command.
- Reject ready-looking packages before downstream replay, holdout, calibration or claim gates run.
- Reject any shortcut that writes actuator policy or release gates from a readiness packet.

## Boundary

This packet only queues external package collection and validation commands. It does not generate field evidence, does not run downstream replay/holdout/calibration, does not resume the model chain and does not authorize actuator or release-gate writes.

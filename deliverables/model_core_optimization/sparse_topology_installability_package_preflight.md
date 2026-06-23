# Sparse Topology Installability Package Preflight

## Role

This preflight checks whether an external `SPARSE_TOPOLOGY_INSTALLABILITY_PACKAGE_DIR` can be routed to Agent48 as field topology/installability input for sparse layout-holdout work. It is not a deployable sensor-layout approval.

## Status

- package_status: `sparse_topology_installability_package_waiting_for_SPARSE_TOPOLOGY_INSTALLABILITY_PACKAGE_DIR`
- source_env_var: `SPARSE_TOPOLOGY_INSTALLABILITY_PACKAGE_DIR`
- source_path: ``
- package_preflight_pass: `False`
- matched_node_count: `0`
- minimum_matched_node_count: `3`
- sparse_topology_coverage_candidate: `0.0`
- installable_candidate_node_count: `0`
- path_stage_count: `0`
- hidden_state_count: `0`
- can_route_to_agent48_sparse_layout_holdout: `False`
- can_authorize_field_deployment: `False`
- can_generate_field_evidence: `False`
- can_write_to_actuator: `False`
- can_write_to_release_gate: `False`
- next_operator_action: `fill_sparse_topology_installability_package_template_and_set_SPARSE_TOPOLOGY_INSTALLABILITY_PACKAGE_DIR`

## Required Tables

| table | rows | missing columns | template markers | non-field rows |
| --- | --- | --- | --- | --- |
| `site_topology_graph` | `0` | `[]` | `0` | `0` |
| `candidate_node_modality_costs` | `0` | `[]` | `0` | `0` |
| `installability_maintenance_constraints` | `0` | `[]` | `0` | `0` |
| `node_hydraulic_delay` | `0` | `[]` | `0` | `0` |
| `labeled_state_matrix` | `0` | `[]` | `0` | `0` |

## Signal Audits

| signal | valid rows | valid node ids |
| --- | --- | --- |
| `site_topology` | `0` | `[]` |
| `node_modality_cost` | `0` | `[]` |
| `installability_constraint` | `0` | `[]` |
| `hydraulic_delay` | `0` | `[]` |
| `labeled_state_matrix` | `0` | `[]` |

## Blocking Reasons

- `missing_external_package_dir`

## Template Location

- template_dir: `outputs/sparse_topology_installability_package/sparse_topology_installability_package_template`
- required_table_count: `5`

## Boundary

This preflight only checks whether an external topology/installability package is ready for Agent48 sparse layout-holdout work. Passing this gate does not prove a deployable sensor layout, field soft-sensor performance, actuator readiness or release-gate readiness.

This package is only a sparse topology and installability preflight input. It cannot write actuator policy, release-gate policy, deployable sensor layout approval, field soft-sensor claims or deployment clearance.

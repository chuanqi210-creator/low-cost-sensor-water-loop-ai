# Field-Supported KG Edge Package Preflight

## Role

This preflight checks whether an external `FIELD_SUPPORTED_KG_EDGE_PACKAGE_DIR` can be routed to KG reasoning as field-supported edge input. It is not a site-specific mechanism proof or claim upgrade.

## Status

- package_status: `field_supported_kg_edge_package_waiting_for_FIELD_SUPPORTED_KG_EDGE_PACKAGE_DIR`
- source_env_var: `FIELD_SUPPORTED_KG_EDGE_PACKAGE_DIR`
- source_path: ``
- package_preflight_pass: `False`
- matched_edge_count: `0`
- minimum_matched_edge_count: `3`
- field_supported_edge_coverage_candidate: `0.0`
- can_route_to_kg_reasoning_field_edge_update: `False`
- can_upgrade_site_specific_claims: `False`
- can_generate_field_evidence: `False`
- can_write_to_actuator: `False`
- can_write_to_release_gate: `False`
- next_operator_action: `fill_field_supported_kg_edge_package_template_and_set_FIELD_SUPPORTED_KG_EDGE_PACKAGE_DIR`

## Required Tables

| table | rows | missing columns | template markers | non-field rows |
| --- | --- | --- | --- | --- |
| `pollutant_material_condition_edges` | `0` | `[]` | `0` | `0` |
| `source_basis_rows` | `0` | `[]` | `0` | `0` |
| `field_supported_edge_rows` | `0` | `[]` | `0` | `0` |
| `failure_boundary_annotations` | `0` | `[]` | `0` | `0` |
| `claim_action_constraint_links` | `0` | `[]` | `0` | `0` |

## Signal Audits

| signal | valid rows | valid edge ids |
| --- | --- | --- |
| `kg_edge` | `0` | `[]` |
| `source_basis` | `0` | `[]` |
| `field_support` | `0` | `[]` |
| `failure_boundary` | `0` | `[]` |
| `claim_action_constraint` | `0` | `[]` |

## Blocking Reasons

- `missing_external_package_dir`

## Template Location

- template_dir: `outputs/field_supported_kg_edge_package/field_supported_kg_edge_package_template`
- required_table_count: `5`

## Boundary

This preflight only checks whether an external KG edge package is structurally ready for downstream KG reasoning. Passing this gate does not prove a site-specific mechanism claim, authorize control actions, or upgrade release decisions.

This package is only a field-supported KG edge preflight input. It cannot write actuator policy, release-gate policy, field-supported mechanism claims, claim text or deployment clearance.

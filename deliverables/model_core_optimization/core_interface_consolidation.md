# Core Interface Consolidation Facade

## Role

This R8u158 artifact compresses the current core model work into three machine-readable facades: external package lifecycle, sparse-layout soft-sensor coupling, and field-control replay schema crosswalk. It is not a field validation result and cannot generate field evidence.

## Status

- consolidation_id: `R8u158_core_interface_consolidation_facade`
- facade_count: `3`
- top_external_action_env_var: `GREY_BOX_CALIBRATION_PACKAGE_DIR`
- top_external_action: `complete_grey_box_calibration_package_preflight_before_building_field_calibration_summary`
- top_internal_action: `maintain_core_interface_facades_and_refresh_only_when field packages, Agent48 layout metrics or Agent52 replay schema change`
- new_agent_recommendation: `do_not_add_linear_agent`

## Facades

- external_package_lifecycle: `external_package_lifecycle_waiting_for_field_packages`
- sparse_layout_soft_sensor_coupling_benchmark: `synthetic_layout_coupling_benchmark_ready_needs_field_topology_missingness_labels`
- field_control_replay_crosswalk: `field_control_replay_crosswalk_ready_waiting_for_FIELD_CONTROL_REPLAY_PACKAGE_DIR`

## External Package Lifecycle

| package | env var | status | matched | submission readiness | downstream | next action |
| --- | --- | --- | --- | --- | --- | --- |
| `grey_box_calibration` | `GREY_BOX_CALIBRATION_PACKAGE_DIR` | `grey_box_calibration_collection_work_order_waiting_for_external_package` | `0/3` | `grey_box_submission_readiness_waiting_for_external_package / 0.143; missing_tables=5` | `Agent53_minimal_grey_box_physics` | `fill_grey_box_calibration_package_template_and_set_GREY_BOX_CALIBRATION_PACKAGE_DIR` |
| `field_control_replay` | `FIELD_CONTROL_REPLAY_PACKAGE_DIR` | `field_control_replay_package_waiting_for_FIELD_CONTROL_REPLAY_PACKAGE_DIR` | `0/3` | `not_applicable / n/a` | `Agent49_52_offline_control_replay` | `fill_field_control_replay_package_template_and_set_FIELD_CONTROL_REPLAY_PACKAGE_DIR` |
| `sparse_topology_installability` | `SPARSE_TOPOLOGY_INSTALLABILITY_PACKAGE_DIR` | `sparse_topology_installability_package_waiting_for_SPARSE_TOPOLOGY_INSTALLABILITY_PACKAGE_DIR` | `0/3` | `not_applicable / n/a` | `Agent48_54_layout_holdout` | `fill_sparse_topology_installability_package_template_and_set_SPARSE_TOPOLOGY_INSTALLABILITY_PACKAGE_DIR` |

## Sparse Layout Coupling Benchmark

| rank | strategy | score | catalyst support | missingness robustness | pressure/headloss penalty |
| --- | --- | --- | --- | --- | --- |
| `1` | `reconstruction_qr_proxy` | `0.549` | `0.366` | `0.747` | `0.12` |
| `2` | `classification_sspoc_proxy` | `0.545` | `0.404` | `0.768` | `0.12` |
| `3` | `greedy_marginal` | `0.533` | `0.3` | `0.698` | `0.12` |
| `4` | `deterministic_random_baseline` | `0.505` | `0.327` | `0.696` | `0.12` |
| `5` | `topology_robust_cost_proxy` | `0.447` | `0.199` | `0.7` | `0.12` |
| `6` | `cost_only_baseline` | `0.375` | `0.214` | `0.633` | `0.12` |

## Field Control Replay Crosswalk

| source table | target fields | required for |
| --- | --- | --- |
| `state_action_next_state_rows` | `['transition_id', 'batch_id', 'facility_id', 'state_vector_ref', 'action_id', 'next_state_vector_ref', 'observed_outcome']` | `state-action-next-state replay row` |
| `reward_component_rows` | `['reward_components', 'component_value', 'component_weight', 'objective_direction']` | `reward calculation and regret audit` |
| `operator_or_expert_action_labels` | `['expert_action_id', 'expert_action_label', 'action_match_required']` | `joint action accuracy and policy distillation audit` |
| `actuator_latency_and_result_rows` | `['actuator_id', 'commanded_action_id', 'latency_min', 'execution_result']` | `execution feasibility and latency guardrail` |
| `unsafe_action_or_override_events` | `['unsafe_action_flag', 'override_flag', 'override_reason', 'human_review_required']` | `operator review and no-write safety boundary` |

## Cannot Claim

- cannot authorize actuator writes
- cannot authorize release gate writes
- cannot claim catalyst deactivation is validated
- cannot claim field policy superiority
- cannot claim field soft-sensor accuracy
- cannot claim field-optimal sensor placement
- cannot claim online MARL readiness
- cannot relax Agent49 catalyst guardrail
- cannot write actuator policy
- cannot write release gate

## Boundary

This facade cannot generate field evidence, cannot resume the model chain, cannot write actuator policy and cannot write a release gate.

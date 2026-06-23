# 主闭环链条回接审计

- main_chain_reconnection_status：`synthetic_main_chain_reconnection_ready_needs_field_replay`
- main_chain_prior_consumption_rate：`1.0`
- consumed_link_count：`7` / `7`
- critical_links_ready：`True`
- can_write_to_actuator：`False`
- can_write_to_release_gate：`False`

## Coupling Table

| Link | Source -> Target | Consumed | Evidence | Boundary |
| --- | --- | --- | --- | --- |
| `L0_agent54_layout_to_agent2_soft_sensor` | `Agent54/Agent48 -> Agent2_SoftSensor` | `True` | `{'layout_status': 'global_modality_fallback_used_for_layout', 'node_specific_value_rate': 0.0}` | layout fallback can inform uncertainty; field node values required for deployment claims |
| `L1_agent53_grey_box_to_agent2_soft_sensor` | `Agent53 -> Agent2_SoftSensor` | `True` | `{'grey_box_status': 'synthetic_grey_box_physics_prior_ready_needs_field_calibration', 'grey_box_residual_prior': 0.206, 'grey_box_byproduct_prior': 0.597}` | synthetic grey-box prior can raise uncertainty and byproduct guard only; no release authorization |
| `L2_agent56_kg_to_agent3_mechanism` | `Agent56 -> Agent3_Mechanism` | `True` | `{'evidence_path_count': 1}` | literature/synthetic KG evidence can explain hypotheses; field edges required for claims |
| `L3_agent56_kg_to_agent5_control` | `Agent56 -> Agent5_ControlStrategy` | `True` | `{'knowledge_reasoning_source': 'typed_kg_action_constraint_patch', 'knowledge_action_biases': {'hold_for_validation': 0.108, 'recirculate': 0.094, 'release': -0.121}}` | KG action constraints can alter scores only; no actuator writeback |
| `L4_agent55_engineering_to_agent9_cost_safety` | `Agent55 -> Agent9_CostSafety` | `True` | `{'evaluated_action_count': 12, 'patched_action_count': 7}` | engineering patch affects objective scoring, not direct actuator execution |
| `L5_agent55_engineering_to_agent10_arbitration` | `Agent55 -> Agent10_Arbitration` | `True` | `{'available': True, 'blocked_action_ids': ['regenerate_catalyst', 'replace_catalyst'], 'readiness': {'engineering_constraints_status': 'synthetic_engineering_constraints_reward_patch_ready_needs_plc_scada_and_field_replay', 'engineering_constraints_score': 0.815, 'constraint_contract_score': 1.0, 'reward_patch_coverage': 1.0, 'arbitration_patch_coverage': 1.0, 'mean_execution_feasibility': 0.98, 'hard_blocked_joint_action_count': 1, 'storage_violation_rate': 0.2, 'actuator_switch_pressure': 0.125, 'inventory_risk_score': 0.0, 'human_review_bottleneck_score': 0.0, 'field_ready': False, 'can_update_agent49_reward_contract': True, 'can_patch_final_arbitration': True, 'can_write_to_actuator': False, 'can_write_to_release_gate': False, 'next_recommended_core_action': 'P6_reasonable_knowledge_graph_upgrade'}}` | arbitration can block actions; field execution replay required before execution |
| `L6_agent49_multi_facility_to_agent10_arbitration` | `Agent49 -> Agent10_Arbitration` | `True` | `{'agent49_joint_action_count': 5, 'cost_safety_joint_action_count': 3, 'arbitration_final_plan_count': 2, 'final_plan_contains_joint_action': False}` | Agent49 remains a collaborative policy candidate until replay and arbitration bridge are explicit |

## 结论边界

- `synthetic_reconnection_not_execution_ready`：主链回接只证明 synthetic prior 已进入推理链，不能替代 field replay 或执行器许可。
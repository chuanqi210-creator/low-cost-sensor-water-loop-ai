# R3 控制 Replay 反事实压力测试报告

- 状态：`synthetic_counterfactual_stress_ready_needs_field_replay`
- stress_case_count：6
- baseline_joint_action_accuracy：0.667
- observation_contract_accuracy：0.833
- guardrail_candidate_accuracy：1.0
- p95_reward_regret_delta_guardrail：0.177
- protective_false_positive_cost_delta_guardrail：0.18
- can_write_to_actuator：False

## Stress Cases

| Case | Scenario | Baseline | Observation | Guardrail | Resolution |
| --- | --- | --- | --- | --- | --- |
| `R0` | matrix_shock_visible | `J0_matrix_shock_equalize_and_recycle` | `J0_matrix_shock_equalize_and_recycle` | `J0_matrix_shock_equalize_and_recycle` | baseline_already_matches_expert |
| `R1` | reaction_completion_lag | `J1_reaction_completion_recovery` | `J1_reaction_completion_recovery` | `J1_reaction_completion_recovery` | baseline_already_matches_expert |
| `R2` | catalyst_uncertain_low_proxy | `J2_catalyst_protection_before_regeneration` | `J4_safe_low_cost_standby` | `J4_safe_low_cost_standby` | resolved_by_R3_guardrail_candidate |
| `R3` | polishing_release_risk | `J3_polishing_and_release_gate` | `J3_polishing_and_release_gate` | `J3_polishing_and_release_gate` | baseline_already_matches_expert |
| `R4` | clean_but_low_field_evidence | `J4_safe_low_cost_standby` | `J4_safe_low_cost_standby` | `J4_safe_low_cost_standby` | baseline_already_matches_expert |
| `R5` | hydraulic_delay_violation | `J0_matrix_shock_equalize_and_recycle` | `J0_matrix_shock_equalize_and_recycle` | `J3_polishing_and_release_gate` | resolved_by_R3_guardrail_candidate |

## 下一步

- `R3b_agent49_reward_prior_patch_from_counterfactual_stress`：把 R3 反事实压力结果写成 Agent49 reward prior guardrails
- 原因：R3 stress 已暴露并修复 synthetic 高 regret/误保护场景；下一步应把规则补丁接入 Agent49 reward prior，但仍不写执行器。
- 禁止事项：不能把 synthetic stress improvement 当作现场控制有效性。

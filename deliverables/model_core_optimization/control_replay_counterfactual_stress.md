# R3 Agent49/52 控制 Replay 反事实压力测试

## 核心判断

R3 把 Agent52 的 replay-ready baseline 升级为反事实压力测试。它比较三层策略：原始 Agent49/52 baseline、接入 R2 观测契约后的 observation-aware policy、以及 R3 reward guardrail candidate。目标不是训练在线 MARL，而是先找出高 regret、误保护和工程不可执行场景。

- 状态：`synthetic_counterfactual_stress_ready_needs_field_replay`
- baseline accuracy：0.667
- observation contract accuracy：0.833
- guardrail candidate accuracy：1.0
- p95 regret delta：0.177
- false positive cost delta：0.18
- unsafe_action_block_correction_rate：1.0
- field_replay_coverage：0.0
- can_update_agent49_reward_prior：True
- can_write_to_actuator：False
- can_write_to_release_gate：False

## Counterfactual Stress Table

| Case | Scenario | Expert | Baseline | Observation Contract | Guardrail Candidate | Regret baseline -> guardrail | Boundary |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `R0` | matrix_shock_visible | `J0_matrix_shock_equalize_and_recycle` | `J0_matrix_shock_equalize_and_recycle` | `J0_matrix_shock_equalize_and_recycle` | `J0_matrix_shock_equalize_and_recycle` | 0.0 -> 0.0 | synthetic replay case; field replay required before policy promotion |
| `R1` | reaction_completion_lag | `J1_reaction_completion_recovery` | `J1_reaction_completion_recovery` | `J1_reaction_completion_recovery` | `J1_reaction_completion_recovery` | 0.0 -> 0.0 | synthetic replay case; field replay required before policy promotion |
| `R2` | catalyst_uncertain_low_proxy | `J4_safe_low_cost_standby` | `J2_catalyst_protection_before_regeneration` | `J4_safe_low_cost_standby` | `J4_safe_low_cost_standby` | 0.177 -> 0.0 | needs field proxy labels before relaxing catalyst uncertainty block |
| `R3` | polishing_release_risk | `J3_polishing_and_release_gate` | `J3_polishing_and_release_gate` | `J3_polishing_and_release_gate` | `J3_polishing_and_release_gate` | 0.0 -> 0.0 | needs lab label and release gate evidence before any release action |
| `R4` | clean_but_low_field_evidence | `J4_safe_low_cost_standby` | `J4_safe_low_cost_standby` | `J4_safe_low_cost_standby` | `J4_safe_low_cost_standby` | 0.0 -> 0.0 | synthetic replay case; field replay required before policy promotion |
| `R5` | hydraulic_delay_violation | `J3_polishing_and_release_gate` | `J0_matrix_shock_equalize_and_recycle` | `J0_matrix_shock_equalize_and_recycle` | `J3_polishing_and_release_gate` | 0.153 -> 0.0 | needs tank storage, actuator latency and operation replay before recycle promotion |

## Reward Prior Patch Candidate

- patch_id：`R3_counterfactual_guardrail_reward_prior`
- target_agent：`multi_facility_collaborative_control_agent`
- metric_delta：{'accuracy_gain_guardrail': 0.333, 'p95_reward_regret_delta_guardrail': 0.177, 'protective_false_positive_cost_delta_guardrail': 0.18}

- `R3G1_catalyst_uncertain_requires_standby_or_human_review`：IF catalyst proxy is not field validated and catalyst action would be protective/regeneration THEN prefer J4_safe_low_cost_standby or human-reviewed catalyst protection；reduce protective false-positive cost from baseline replay cases
- `R3G2_hydraulic_delay_unknown_blocks_recycle`：IF tank storage margin or actuator latency evidence is missing THEN prefer J3_polishing_and_release_gate over recycle escalation；reduce high-regret unsafe recycle actions under delayed evidence

## Field Replay Requirements

- `R3_FV1_state_action_reward_replay`：control stress validation，fields=['facility_state_vector', 'policy_action_id', 'operator_or_expert_action_id', 'reward_by_action', 'next_state_summary']
- `R3_FV2_hydraulic_execution_replay`：recycle and hold action safety，fields=['tank_storage_margin', 'actuator_latency_p90', 'pump_valve_result']
- `R3_FV3_catalyst_action_replay`：catalyst protection false-positive cost，fields=['proxy_holdout_label', 'pressure_drop_kPa', 'regeneration_event', 'operator_override']

## 下一步

- `R3b_agent49_reward_prior_patch_from_counterfactual_stress`：把 R3 反事实压力结果写成 Agent49 reward prior guardrails
- 原因：R3 stress 已暴露并修复 synthetic 高 regret/误保护场景；下一步应把规则补丁接入 Agent49 reward prior，但仍不写执行器。
- 禁止事项：不能把 synthetic stress improvement 当作现场控制有效性。

## 边界

- R3 只能写 reward prior 和 stress suite 候选，不能写执行器。
- guardrail 在 synthetic stress 上改善指标，不等于现场控制有效性。
- field replay coverage 仍为 0 前，不训练 offline RL，不做 release gate。

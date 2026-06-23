# 工程执行约束进入 Reward 与仲裁

- engineering_constraints_status：`synthetic_engineering_constraints_reward_patch_ready_needs_plc_scada_and_field_replay`
- mean_execution_feasibility：`0.98`
- reward_patch_coverage：`1.0`
- arbitration_patch_coverage：`1.0`
- can_write_to_actuator：`False`

## Joint Action Constraint Evaluation

| Joint Action | Feasibility | Penalty | Hard Block | Reasons |
| --- | --- | --- | --- | --- |
| `J4_safe_low_cost_standby` | `0.975` | `0.022` | `False` | `[]` |
| `J3_polishing_and_release_gate` | `1.0` | `0.0` | `False` | `[]` |
| `J0_matrix_shock_equalize_and_recycle` | `1.0` | `0.0` | `False` | `[]` |
| `J2_catalyst_protection_before_regeneration` | `0.923` | `0.068` | `True` | `['maintenance_window_pressure']` |
| `J1_reaction_completion_recovery` | `1.0` | `0.0` | `False` | `[]` |

## Patched Agent49 Top Actions

| Rank | Joint Action | Score | Engineering Penalty | Feasibility |
| --- | --- | --- | --- | --- |
| `1` | `J4_safe_low_cost_standby` | `0.535` | `0.022` | `0.975` |
| `2` | `J3_polishing_and_release_gate` | `0.504` | `0.0` | `1.0` |
| `3` | `J0_matrix_shock_equalize_and_recycle` | `0.503` | `0.0` | `1.0` |
| `4` | `J1_reaction_completion_recovery` | `0.482` | `0.0` | `1.0` |
| `5` | `J2_catalyst_protection_before_regeneration` | `0.3` | `0.068` | `0.923` |

## 结论与边界

- 把池容、泵阀动作次数、执行器延迟、药剂库存、维护窗口、人工复核和误动作成本写入 Agent49 reward，而不是只写在说明里。
- 最终仲裁阶段要消费同一份 action_constraint_patch；触发硬约束的动作只能进入人工复核或保护性候选，不能自动执行。
- 采集 PLC/SCADA 点表、执行器响应日志、人工复核排队和药剂库存日志后，才能把该层从 synthetic patch 升级为现场执行候选。
- 优先复核 `J2_catalyst_protection_before_regeneration`：penalty=0.068，hard_reasons=['maintenance_window_pressure']。
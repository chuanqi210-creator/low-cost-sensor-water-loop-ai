# Agent49 工程约束补丁后协同控制摘要

- summary: 多设施协同控制：synthetic_collaborative_policy_needs_field_replay；设施 agent 5 个，候选联动动作 5 个，策略蒸馏准确度 0.787。
- engineering_constraints_status: `synthetic_engineering_constraints_reward_patch_ready_needs_plc_scada_and_field_replay`

| Rank | Joint Action | Score | Penalty | Feasibility |
| --- | --- | --- | --- | --- |
| `1` | `J4_safe_low_cost_standby` | `0.535` | `0.022` | `0.975` |
| `2` | `J3_polishing_and_release_gate` | `0.504` | `0.0` | `1.0` |
| `3` | `J0_matrix_shock_equalize_and_recycle` | `0.503` | `0.0` | `1.0` |
| `4` | `J1_reaction_completion_recovery` | `0.482` | `0.0` | `1.0` |
| `5` | `J2_catalyst_protection_before_regeneration` | `0.3` | `0.068` | `0.923` |
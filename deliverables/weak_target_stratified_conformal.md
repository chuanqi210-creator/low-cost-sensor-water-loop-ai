# 弱目标分层保形校准

- weak_target_stratified_status：`weak_target_stratified_synthetic_candidate_needs_field_holdout`
- weak_target_stratified_score：`0.667`
- evidence_stage：`synthetic_holdout`
- can_pass_candidate_to_agent46：`False`
- can_write_to_release_gate：`False`

## Weak Target Profiles

| Target | Coverage | Gap | Base Width | Candidate Width | Mode |
| --- | --- | --- | --- | --- | --- |
| `catalyst_activity` | `1.0` | `0.0` | `0.415` | `0.415` | `monitor_targetwise_coverage` |
| `matrix_interference` | `0.875` | `0.005` | `0.172` | `0.1932` | `target_and_scenario_stratified_conformal` |

## Gate Checks

| Check | Pass | Rationale |
| --- | --- | --- |
| `WTC0_field_holdout_origin` | `False` | 弱目标分层阈值必须由真实 field holdout 确认后才可交给 release gate。 |
| `WTC1_weak_target_eval_volume` | `True` | 每个弱目标都需要足够 evaluation errors 才能判断覆盖率。 |
| `WTC2_weak_target_coverage` | `False` | 弱目标 coverage 必须单独达标，不能被总体 coverage 掩盖。 |
| `WTC3_candidate_width_reasonable` | `True` | 候选阈值不能靠过宽区间换取表面 coverage。 |
| `WTC4_scenario_stratification_support` | `True` | 弱目标至少需要在关键场景上保持基本覆盖，失败场景必须分层校准。 |
| `WTC5_release_gate_boundary` | `True` | 该 agent 只能向 Agent46 提供弱目标校准候选，不能绕过 Agent46 写 release gate。 |

## 结论

- 保留当前弱目标分层阈值为 synthetic diagnostic candidate，不要写入 release gate。
- 真实 field holdout 采样时必须提高 matrix_interference 和 catalyst_activity 的场景标签密度。
- 在 Agent46 之前重跑本 agent，确认弱目标 coverage 和候选区间宽度均达标。
# Agent 10 催化剂生命周期模拟报告

## remaining_life_regeneration

- lifecycle summary: 催化剂生命周期建议：优先再生催化剂，评分 0.779。
- lifecycle state: `{'catalyst_activity': 0.282, 'catalyst_lifetime_fraction': 0.66, 'catalyst_regen_count': 1.0, 'catalyst_age_cycles': 7.0, 'regeneration_potential': 0.454, 'replacement_urgency': 0.58, 'evidence_strength': 0.867}`
- maintenance decision: `{'action_id': 'regenerate_catalyst', 'action_name': '优先再生催化剂', 'score': 0.779, 'rationale': '活性不足但仍有可恢复寿命，适合先再生再回流验证。'}`
- validation plan: `{'plan_name': 'catalyst_lifecycle_validation', 'urgency': 0.644, 'hold_min': 45, 'validation_delay_min': 28, 'targets': ['catalyst_activity_assay', 'pressure_drop_check', 'residual_oxidant_quick_test', 'surface_fouling_inspection'], 'release_gate': 'use validation evidence to update offline_residual_proxy before release'}`
- final actions: `['regenerate_catalyst', 'recirculate']`
- blocked: `['release', 'dose_oxidant']`

## exhausted_life_replacement

- lifecycle summary: 催化剂生命周期建议：更换催化剂模块，评分 0.794。
- lifecycle state: `{'catalyst_activity': 0.28, 'catalyst_lifetime_fraction': 0.24, 'catalyst_regen_count': 3.0, 'catalyst_age_cycles': 12.0, 'regeneration_potential': 0.18, 'replacement_urgency': 0.86, 'evidence_strength': 1.0}`
- maintenance decision: `{'action_id': 'replace_catalyst', 'action_name': '更换催化剂模块', 'score': 0.794, 'rationale': '再生边际收益下降，继续再生可能增加停机和材料损耗。'}`
- validation plan: `{'plan_name': 'catalyst_lifecycle_validation', 'urgency': 0.631, 'hold_min': 45, 'validation_delay_min': 28, 'targets': ['catalyst_activity_assay', 'pressure_drop_check', 'surface_fouling_inspection'], 'release_gate': 'use validation evidence to update offline_residual_proxy before release'}`
- final actions: `['replace_catalyst', 'recirculate']`
- blocked: `['release', 'dose_oxidant', 'regenerate_catalyst']`

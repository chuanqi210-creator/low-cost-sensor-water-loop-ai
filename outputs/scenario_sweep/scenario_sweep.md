# 多场景闭环决策扫查

## clean_release

- summary: 最终仲裁：执行 达标放行 等 1 个动作；未通过安全门 []。
- state: `{'pollutant_residual_risk': 0.12, 'reaction_completion': 0.871, 'oxidant_remaining': 0.814, 'catalyst_activity': 0.654, 'matrix_interference': 0.225, 'byproduct_risk': 0.464, 'offline_validation_confidence': 0.0, 'offline_residual_proxy': 0.0, 'offline_validation_age_min': 999.0, 'hydraulic_confidence': 1.0, 'sensor_confidence': 1.0, 'compliance_probability': 1.0, 'recycle_gain': 0.059, 'release_readiness': 0.838, 'cycle_id': 5, 'catalyst_age_cycles': 1, 'catalyst_regen_count': 0, 'catalyst_lifetime_fraction': 0.96, 'catalyst_regeneration_potential': 0.717, 'catalyst_replacement_urgency': 0.124}`
- top fault: `{'fault_id': 'matrix_interference', 'fault_name': '基质干扰或新扰动进入系统', 'score': 0.274, 'risk_level': 'medium', 'evidence': {'matrix_interference': 0.225, 'drift_suspected': False, 'knowledge_support': []}, 'next_check': '检测盐度、COD/TOC、浊度来源；判断是否需要预处理或切换单元。'}`
- catalyst lifecycle: `{'action_id': 'monitor_catalyst', 'action_name': '维持监测', 'score': 0.733, 'rationale': '寿命风险尚可接受，暂不触发维护动作。'}`
- validation plan: `{'plan_name': 'routine_soft_sensor_audit', 'urgency': 0.18, 'hold_min': 18, 'validation_delay_min': 8, 'targets': ['periodic_grab_sample_COD_or_TOC'], 'release_gate': 'use validation evidence to update offline_residual_proxy before release'}`
- strategy profile: `cost_first`
- final actions: `['release']`
- blocked: `['dose_oxidant', 'recirculate', 'replace_catalyst']`

## sensor_faults

- summary: 最终仲裁：执行 核查泵阀与回流管路 等 4 个动作；未通过安全门 ['release_readiness_gate', 'hydraulic_confidence_gate']。
- state: `{'pollutant_residual_risk': 0.339, 'reaction_completion': 0.373, 'oxidant_remaining': 0.802, 'catalyst_activity': 0.491, 'matrix_interference': 0.361, 'byproduct_risk': 0.369, 'offline_validation_confidence': 0.0, 'offline_residual_proxy': 0.0, 'offline_validation_age_min': 999.0, 'hydraulic_confidence': 0.272, 'sensor_confidence': 0.888, 'compliance_probability': 0.794, 'recycle_gain': 0.204, 'release_readiness': 0.794, 'cycle_id': 1, 'catalyst_age_cycles': 2, 'catalyst_regen_count': 0, 'catalyst_lifetime_fraction': 0.9, 'catalyst_regeneration_potential': 0.709, 'catalyst_replacement_urgency': 0.296}`
- top fault: `{'fault_id': 'hydraulic_retention_anomaly', 'fault_name': '水力停留时间或回流执行异常', 'score': 0.836, 'risk_level': 'medium', 'evidence': {'sustained_shift': False, 'low_flow_absolute': True, 'hydraulic_confidence': 0.272, 'mechanism_ids': ['hydraulic_anomaly', 'loop_buffer_needed', 'sensor_uncertainty'], 'recycle_gain': 0.204}, 'next_check': '核查泵、阀、回流管路和实际流量；必要时重新计算 HRT。'}`
- catalyst lifecycle: `{'action_id': 'monitor_catalyst', 'action_name': '维持监测', 'score': 0.627, 'rationale': '寿命风险尚可接受，暂不触发维护动作。'}`
- validation plan: `{'plan_name': 'sensor_reliability_cross_check', 'urgency': 0.487, 'hold_min': 28, 'validation_delay_min': 12, 'targets': ['grab_sample_COD_or_TOC', 'sensor_calibration_check', 'target_pollutant_proxy'], 'release_gate': 'use validation evidence to update offline_residual_proxy before release'}`
- strategy profile: `safety_first`
- final actions: `['inspect_hydraulics', 'calibrate_sensors', 'hold_for_validation', 'recirculate']`
- blocked: `['release', 'dose_oxidant', 'replace_catalyst']`

## oxidant_limitation

- summary: 最终仲裁：执行 补加氧化剂 等 2 个动作；未通过安全门 ['release_readiness_gate', 'residual_risk_gate']。
- state: `{'pollutant_residual_risk': 0.586, 'reaction_completion': 0.261, 'oxidant_remaining': 0.151, 'catalyst_activity': 0.504, 'matrix_interference': 0.331, 'byproduct_risk': 0.125, 'offline_validation_confidence': 0.0, 'offline_residual_proxy': 0.0, 'offline_validation_age_min': 999.0, 'hydraulic_confidence': 1.0, 'sensor_confidence': 1.0, 'compliance_probability': 0.661, 'recycle_gain': 0.534, 'release_readiness': 0.653, 'cycle_id': 1, 'catalyst_age_cycles': 3, 'catalyst_regen_count': 0, 'catalyst_lifetime_fraction': 0.88, 'catalyst_regeneration_potential': 0.69, 'catalyst_replacement_urgency': 0.314}`
- top fault: `{'fault_id': 'cycle_window_insufficient', 'fault_name': '循环缓冲或验证窗口不足', 'score': 0.9, 'risk_level': 'medium', 'evidence': {'pollutant_residual_risk': 0.586, 'oxidant_remaining': 0.151, 'release_readiness': 0.653, 'recycle_gain': 0.534, 'mechanism_ids': ['oxidant_limitation', 'loop_buffer_needed'], 'knowledge_support': [{'entry_id': 'kb_oxidant_limited_refractory_organics', 'match_score': 0.82, 'pollutant_class': '高负荷还原性或难降解有机污染物', 'material_family': '氧化剂驱动体系'}, {'entry_id': 'kb_loop_buffer_for_slow_sensing', 'match_score': 0.82, 'pollutant_class': '目标污染物需慢检测或低成本代理检测的废水', 'material_family': '循环式反应器/旁路快检系统'}]}, 'next_check': '安排下一回流/停留窗口，并同步进行软传感复估与旁路快检，而不是立即放行。'}`
- catalyst lifecycle: `{'action_id': 'monitor_catalyst', 'action_name': '维持监测', 'score': 0.614, 'rationale': '寿命风险尚可接受，暂不触发维护动作。'}`
- validation plan: `{'plan_name': 'routine_soft_sensor_audit', 'urgency': 0.442, 'hold_min': 18, 'validation_delay_min': 8, 'targets': ['residual_oxidant_quick_test'], 'release_gate': 'use validation evidence to update offline_residual_proxy before release'}`
- strategy profile: `emergency_response`
- final actions: `['dose_oxidant', 'recirculate']`
- blocked: `['release', 'replace_catalyst']`

## reaction_time_insufficient

- summary: 最终仲裁：执行 继续回流处理 等 1 个动作；未通过安全门 ['release_readiness_gate', 'residual_risk_gate']。
- state: `{'pollutant_residual_risk': 0.414, 'reaction_completion': 0.484, 'oxidant_remaining': 0.752, 'catalyst_activity': 0.504, 'matrix_interference': 0.319, 'byproduct_risk': 0.318, 'offline_validation_confidence': 0.0, 'offline_residual_proxy': 0.0, 'offline_validation_age_min': 999.0, 'hydraulic_confidence': 0.733, 'sensor_confidence': 1.0, 'compliance_probability': 0.782, 'recycle_gain': 0.285, 'release_readiness': 0.782, 'cycle_id': 1, 'catalyst_age_cycles': 3, 'catalyst_regen_count': 0, 'catalyst_lifetime_fraction': 0.86, 'catalyst_regeneration_potential': 0.669, 'catalyst_replacement_urgency': 0.295}`
- top fault: `{'fault_id': 'cycle_window_insufficient', 'fault_name': '循环缓冲或验证窗口不足', 'score': 0.779, 'risk_level': 'medium', 'evidence': {'pollutant_residual_risk': 0.414, 'oxidant_remaining': 0.752, 'release_readiness': 0.782, 'recycle_gain': 0.285, 'mechanism_ids': ['loop_buffer_needed'], 'knowledge_support': [{'entry_id': 'kb_loop_buffer_for_slow_sensing', 'match_score': 0.82, 'pollutant_class': '目标污染物需慢检测或低成本代理检测的废水', 'material_family': '循环式反应器/旁路快检系统'}, {'entry_id': 'kb_catalyst_site_fouling', 'match_score': 0.613, 'pollutant_class': '含络合物、天然有机质或颗粒物的复杂废水', 'material_family': '负载型催化剂/类芬顿/光催化材料'}]}, 'next_check': '安排下一回流/停留窗口，并同步进行软传感复估与旁路快检，而不是立即放行。'}`
- catalyst lifecycle: `{'action_id': 'monitor_catalyst', 'action_name': '维持监测', 'score': 0.616, 'rationale': '寿命风险尚可接受，暂不触发维护动作。'}`
- validation plan: `{'plan_name': 'routine_soft_sensor_audit', 'urgency': 0.211, 'hold_min': 18, 'validation_delay_min': 8, 'targets': ['periodic_grab_sample_COD_or_TOC'], 'release_gate': 'use validation evidence to update offline_residual_proxy before release'}`
- strategy profile: `balanced`
- final actions: `['recirculate']`
- blocked: `['release', 'dose_oxidant', 'replace_catalyst']`

## catalyst_deactivation

- summary: 最终仲裁：执行 再生或更换催化剂 等 2 个动作；未通过安全门 ['release_readiness_gate', 'residual_risk_gate']。
- state: `{'pollutant_residual_risk': 0.478, 'reaction_completion': 0.417, 'oxidant_remaining': 0.726, 'catalyst_activity': 0.282, 'matrix_interference': 0.306, 'byproduct_risk': 0.28, 'offline_validation_confidence': 0.0, 'offline_residual_proxy': 0.0, 'offline_validation_age_min': 999.0, 'hydraulic_confidence': 0.991, 'sensor_confidence': 1.0, 'compliance_probability': 0.739, 'recycle_gain': 0.362, 'release_readiness': 0.739, 'cycle_id': 1, 'catalyst_age_cycles': 7, 'catalyst_regen_count': 1, 'catalyst_lifetime_fraction': 0.66, 'catalyst_regeneration_potential': 0.454, 'catalyst_replacement_urgency': 0.58}`
- top fault: `{'fault_id': 'cycle_window_insufficient', 'fault_name': '循环缓冲或验证窗口不足', 'score': 0.821, 'risk_level': 'medium', 'evidence': {'pollutant_residual_risk': 0.478, 'oxidant_remaining': 0.726, 'release_readiness': 0.739, 'recycle_gain': 0.362, 'mechanism_ids': ['loop_buffer_needed', 'catalyst_deactivation'], 'knowledge_support': [{'entry_id': 'kb_catalyst_site_fouling', 'match_score': 0.82, 'pollutant_class': '含络合物、天然有机质或颗粒物的复杂废水', 'material_family': '负载型催化剂/类芬顿/光催化材料'}, {'entry_id': 'kb_loop_buffer_for_slow_sensing', 'match_score': 0.82, 'pollutant_class': '目标污染物需慢检测或低成本代理检测的废水', 'material_family': '循环式反应器/旁路快检系统'}]}, 'next_check': '安排下一回流/停留窗口，并同步进行软传感复估与旁路快检，而不是立即放行。'}`
- catalyst lifecycle: `{'action_id': 'regenerate_catalyst', 'action_name': '优先再生催化剂', 'score': 0.779, 'rationale': '活性不足但仍有可恢复寿命，适合先再生再回流验证。'}`
- validation plan: `{'plan_name': 'catalyst_lifecycle_validation', 'urgency': 0.644, 'hold_min': 45, 'validation_delay_min': 28, 'targets': ['catalyst_activity_assay', 'pressure_drop_check', 'residual_oxidant_quick_test', 'surface_fouling_inspection'], 'release_gate': 'use validation evidence to update offline_residual_proxy before release'}`
- strategy profile: `safety_first`
- final actions: `['regenerate_catalyst', 'recirculate']`
- blocked: `['release', 'dose_oxidant']`

## matrix_shock

- summary: 最终仲裁：执行 预处理或切换处理单元 等 3 个动作；未通过安全门 ['release_readiness_gate', 'residual_risk_gate']。
- state: `{'pollutant_residual_risk': 0.549, 'reaction_completion': 0.402, 'oxidant_remaining': 0.641, 'catalyst_activity': 0.5, 'matrix_interference': 0.88, 'byproduct_risk': 0.373, 'offline_validation_confidence': 0.0, 'offline_residual_proxy': 0.0, 'offline_validation_age_min': 999.0, 'hydraulic_confidence': 0.963, 'sensor_confidence': 1.0, 'compliance_probability': 0.58, 'recycle_gain': 0.405, 'release_readiness': 0.58, 'cycle_id': 1, 'catalyst_age_cycles': 4, 'catalyst_regen_count': 0, 'catalyst_lifetime_fraction': 0.82, 'catalyst_regeneration_potential': 0.597, 'catalyst_replacement_urgency': 0.356}`
- top fault: `{'fault_id': 'reaction_time_insufficient', 'fault_name': '反应时间不足', 'score': 0.887, 'risk_level': 'medium', 'evidence': {'pollutant_residual_risk': 0.549, 'oxidant_remaining': 0.641, 'catalyst_activity': 0.5, 'recycle_gain': 0.405, 'knowledge_support': [{'entry_id': 'kb_matrix_aop_inhibition', 'match_score': 0.82, 'pollutant_class': '高盐/高 COD 难降解有机废水', 'material_family': '高级氧化或催化氧化材料'}]}, 'next_check': '优先延长停留或增加回流窗口，而不是立即加药。'}`
- catalyst lifecycle: `{'action_id': 'monitor_catalyst', 'action_name': '维持监测', 'score': 0.572, 'rationale': '寿命风险尚可接受，暂不触发维护动作。'}`
- validation plan: `{'plan_name': 'matrix_shock_characterization', 'urgency': 0.671, 'hold_min': 35, 'validation_delay_min': 18, 'targets': ['COD_or_TOC', 'residual_oxidant_quick_test', 'salinity_or_EC_reference', 'turbidity_reference'], 'release_gate': 'use validation evidence to update offline_residual_proxy before release'}`
- strategy profile: `safety_first`
- final actions: `['switch_or_pretreat', 'hold_for_validation', 'recirculate']`
- blocked: `['release', 'dose_oxidant', 'replace_catalyst']`

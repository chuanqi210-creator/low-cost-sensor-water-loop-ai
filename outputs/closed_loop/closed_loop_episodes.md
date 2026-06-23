# 多轮闭环执行仿真

## sensor_faults

### Step 0 / sensor_faults

- summary: 最终仲裁：执行 核查泵阀与回流管路 等 4 个动作；未通过安全门 ['release_readiness_gate', 'hydraulic_confidence_gate']。
- strategy profile: `safety_first`
- state: `{'pollutant_residual_risk': 0.339, 'reaction_completion': 0.373, 'oxidant_remaining': 0.802, 'catalyst_activity': 0.491, 'matrix_interference': 0.361, 'byproduct_risk': 0.369, 'offline_validation_confidence': 0.0, 'offline_residual_proxy': 0.0, 'offline_validation_age_min': 999.0, 'hydraulic_confidence': 0.272, 'sensor_confidence': 0.888, 'compliance_probability': 0.794, 'recycle_gain': 0.204, 'release_readiness': 0.794, 'cycle_id': 1.0, 'catalyst_age_cycles': 2.0, 'catalyst_regen_count': 0.0, 'catalyst_lifetime_fraction': 0.9, 'catalyst_regeneration_potential': 0.709, 'catalyst_replacement_urgency': 0.296}`
- final actions: `['inspect_hydraulics', 'calibrate_sensors', 'hold_for_validation', 'recirculate']`
- blocked: `['release', 'dose_oxidant', 'replace_catalyst']`
- next scenario: `clean_release`

### Step 1 / clean_release

- summary: 最终仲裁：执行 达标放行 等 1 个动作；未通过安全门 []。
- strategy profile: `cost_first`
- state: `{'pollutant_residual_risk': 0.254, 'reaction_completion': 0.555, 'oxidant_remaining': 0.778, 'catalyst_activity': 0.299, 'matrix_interference': 0.312, 'byproduct_risk': 0.363, 'offline_validation_confidence': 0.238, 'offline_residual_proxy': 0.251, 'offline_validation_age_min': 46.5, 'hydraulic_confidence': 0.966, 'sensor_confidence': 1.0, 'compliance_probability': 0.888, 'recycle_gain': 0.216, 'release_readiness': 0.86, 'cycle_id': 2.0, 'catalyst_age_cycles': 3.0, 'catalyst_regen_count': 0.0, 'catalyst_lifetime_fraction': 0.88, 'catalyst_regeneration_potential': 0.696, 'catalyst_replacement_urgency': 0.31}`
- final actions: `['release']`
- blocked: `['dose_oxidant', 'replace_catalyst']`
- next scenario: `None`

## oxidant_limitation

### Step 0 / oxidant_limitation

- summary: 最终仲裁：执行 补加氧化剂 等 2 个动作；未通过安全门 ['release_readiness_gate', 'residual_risk_gate']。
- strategy profile: `emergency_response`
- state: `{'pollutant_residual_risk': 0.586, 'reaction_completion': 0.261, 'oxidant_remaining': 0.151, 'catalyst_activity': 0.504, 'matrix_interference': 0.331, 'byproduct_risk': 0.125, 'offline_validation_confidence': 0.0, 'offline_residual_proxy': 0.0, 'offline_validation_age_min': 999.0, 'hydraulic_confidence': 1.0, 'sensor_confidence': 1.0, 'compliance_probability': 0.661, 'recycle_gain': 0.534, 'release_readiness': 0.653, 'cycle_id': 1.0, 'catalyst_age_cycles': 3.0, 'catalyst_regen_count': 0.0, 'catalyst_lifetime_fraction': 0.88, 'catalyst_regeneration_potential': 0.69, 'catalyst_replacement_urgency': 0.314}`
- final actions: `['dose_oxidant', 'recirculate']`
- blocked: `['release', 'replace_catalyst']`
- next scenario: `reaction_time_insufficient`

### Step 1 / reaction_time_insufficient

- summary: 最终仲裁：执行 再生或更换催化剂 等 3 个动作；未通过安全门 ['release_readiness_gate', 'residual_risk_gate']。
- strategy profile: `safety_first`
- state: `{'pollutant_residual_risk': 0.361, 'reaction_completion': 0.505, 'oxidant_remaining': 0.627, 'catalyst_activity': 0.324, 'matrix_interference': 0.287, 'byproduct_risk': 0.198, 'offline_validation_confidence': 0.0, 'offline_residual_proxy': 0.0, 'offline_validation_age_min': 999.0, 'hydraulic_confidence': 1.0, 'sensor_confidence': 1.0, 'compliance_probability': 0.835, 'recycle_gain': 0.3, 'release_readiness': 0.805, 'cycle_id': 2.0, 'catalyst_age_cycles': 4.0, 'catalyst_regen_count': 0.0, 'catalyst_lifetime_fraction': 0.86, 'catalyst_regeneration_potential': 0.673, 'catalyst_replacement_urgency': 0.306}`
- final actions: `['regenerate_catalyst', 'hold_for_validation', 'recirculate']`
- blocked: `['release', 'dose_oxidant', 'replace_catalyst']`
- next scenario: `clean_release`

### Step 2 / clean_release

- summary: 最终仲裁：执行 达标放行 等 1 个动作；未通过安全门 []。
- strategy profile: `balanced`
- state: `{'pollutant_residual_risk': 0.316, 'reaction_completion': 0.565, 'oxidant_remaining': 0.64, 'catalyst_activity': 0.411, 'matrix_interference': 0.266, 'byproduct_risk': 0.225, 'offline_validation_confidence': 0.225, 'offline_residual_proxy': 0.485, 'offline_validation_age_min': 49.5, 'hydraulic_confidence': 1.0, 'sensor_confidence': 1.0, 'compliance_probability': 0.873, 'recycle_gain': 0.256, 'release_readiness': 0.834, 'cycle_id': 3.0, 'catalyst_age_cycles': 6.0, 'catalyst_regen_count': 1.0, 'catalyst_lifetime_fraction': 0.768, 'catalyst_regeneration_potential': 0.537, 'catalyst_replacement_urgency': 0.519}`
- final actions: `['release']`
- blocked: `['dose_oxidant', 'replace_catalyst']`
- next scenario: `None`

## reaction_time_insufficient

### Step 0 / reaction_time_insufficient

- summary: 最终仲裁：执行 继续回流处理 等 1 个动作；未通过安全门 ['release_readiness_gate', 'residual_risk_gate']。
- strategy profile: `balanced`
- state: `{'pollutant_residual_risk': 0.414, 'reaction_completion': 0.484, 'oxidant_remaining': 0.752, 'catalyst_activity': 0.504, 'matrix_interference': 0.319, 'byproduct_risk': 0.318, 'offline_validation_confidence': 0.0, 'offline_residual_proxy': 0.0, 'offline_validation_age_min': 999.0, 'hydraulic_confidence': 0.733, 'sensor_confidence': 1.0, 'compliance_probability': 0.782, 'recycle_gain': 0.285, 'release_readiness': 0.782, 'cycle_id': 1.0, 'catalyst_age_cycles': 3.0, 'catalyst_regen_count': 0.0, 'catalyst_lifetime_fraction': 0.86, 'catalyst_regeneration_potential': 0.669, 'catalyst_replacement_urgency': 0.295}`
- final actions: `['recirculate']`
- blocked: `['release', 'dose_oxidant', 'replace_catalyst']`
- next scenario: `reaction_time_insufficient`

### Step 1 / reaction_time_insufficient

- summary: 最终仲裁：执行 继续回流处理 等 1 个动作；未通过安全门 ['residual_risk_gate']。
- strategy profile: `balanced`
- state: `{'pollutant_residual_risk': 0.362, 'reaction_completion': 0.505, 'oxidant_remaining': 0.754, 'catalyst_activity': 0.503, 'matrix_interference': 0.291, 'byproduct_risk': 0.326, 'offline_validation_confidence': 0.0, 'offline_residual_proxy': 0.0, 'offline_validation_age_min': 999.0, 'hydraulic_confidence': 0.736, 'sensor_confidence': 1.0, 'compliance_probability': 0.822, 'recycle_gain': 0.248, 'release_readiness': 0.822, 'cycle_id': 2.0, 'catalyst_age_cycles': 4.0, 'catalyst_regen_count': 0.0, 'catalyst_lifetime_fraction': 0.84, 'catalyst_regeneration_potential': 0.66, 'catalyst_replacement_urgency': 0.321}`
- final actions: `['recirculate']`
- blocked: `['release', 'dose_oxidant', 'replace_catalyst']`
- next scenario: `reaction_time_insufficient`

### Step 2 / reaction_time_insufficient

- summary: 最终仲裁：执行 达标放行 等 1 个动作；未通过安全门 []。
- strategy profile: `balanced`
- state: `{'pollutant_residual_risk': 0.34, 'reaction_completion': 0.496, 'oxidant_remaining': 0.762, 'catalyst_activity': 0.491, 'matrix_interference': 0.271, 'byproduct_risk': 0.34, 'offline_validation_confidence': 0.0, 'offline_residual_proxy': 0.0, 'offline_validation_age_min': 999.0, 'hydraulic_confidence': 0.723, 'sensor_confidence': 1.0, 'compliance_probability': 0.836, 'recycle_gain': 0.229, 'release_readiness': 0.836, 'cycle_id': 3.0, 'catalyst_age_cycles': 5.0, 'catalyst_regen_count': 0.0, 'catalyst_lifetime_fraction': 0.821, 'catalyst_regeneration_potential': 0.653, 'catalyst_replacement_urgency': 0.353}`
- final actions: `['release']`
- blocked: `['dose_oxidant', 'replace_catalyst']`
- next scenario: `None`

## catalyst_deactivation

### Step 0 / catalyst_deactivation

- summary: 最终仲裁：执行 再生或更换催化剂 等 2 个动作；未通过安全门 ['release_readiness_gate', 'residual_risk_gate']。
- strategy profile: `safety_first`
- state: `{'pollutant_residual_risk': 0.478, 'reaction_completion': 0.417, 'oxidant_remaining': 0.726, 'catalyst_activity': 0.282, 'matrix_interference': 0.306, 'byproduct_risk': 0.28, 'offline_validation_confidence': 0.0, 'offline_residual_proxy': 0.0, 'offline_validation_age_min': 999.0, 'hydraulic_confidence': 0.991, 'sensor_confidence': 1.0, 'compliance_probability': 0.739, 'recycle_gain': 0.362, 'release_readiness': 0.739, 'cycle_id': 1.0, 'catalyst_age_cycles': 7.0, 'catalyst_regen_count': 1.0, 'catalyst_lifetime_fraction': 0.66, 'catalyst_regeneration_potential': 0.454, 'catalyst_replacement_urgency': 0.58}`
- final actions: `['regenerate_catalyst', 'recirculate']`
- blocked: `['release', 'dose_oxidant']`
- next scenario: `reaction_time_insufficient`

### Step 1 / reaction_time_insufficient

- summary: 最终仲裁：执行 更换催化剂模块 等 3 个动作；未通过安全门 ['release_readiness_gate', 'residual_risk_gate']。
- strategy profile: `safety_first`
- state: `{'pollutant_residual_risk': 0.368, 'reaction_completion': 0.493, 'oxidant_remaining': 0.722, 'catalyst_activity': 0.282, 'matrix_interference': 0.279, 'byproduct_risk': 0.291, 'offline_validation_confidence': 0.0, 'offline_residual_proxy': 0.0, 'offline_validation_age_min': 999.0, 'hydraulic_confidence': 0.994, 'sensor_confidence': 1.0, 'compliance_probability': 0.822, 'recycle_gain': 0.29, 'release_readiness': 0.812, 'cycle_id': 2.0, 'catalyst_age_cycles': 9.0, 'catalyst_regen_count': 2.0, 'catalyst_lifetime_fraction': 0.554, 'catalyst_regeneration_potential': 0.301, 'catalyst_replacement_urgency': 0.777}`
- final actions: `['replace_catalyst', 'hold_for_validation', 'recirculate']`
- blocked: `['release', 'dose_oxidant']`
- next scenario: `clean_release`

### Step 2 / clean_release

- summary: 最终仲裁：执行 达标放行 等 1 个动作；未通过安全门 []。
- strategy profile: `balanced`
- state: `{'pollutant_residual_risk': 0.288, 'reaction_completion': 0.607, 'oxidant_remaining': 0.74, 'catalyst_activity': 0.538, 'matrix_interference': 0.249, 'byproduct_risk': 0.328, 'offline_validation_confidence': 0.249, 'offline_residual_proxy': 0.443, 'offline_validation_age_min': 49.5, 'hydraulic_confidence': 0.982, 'sensor_confidence': 1.0, 'compliance_probability': 0.889, 'recycle_gain': 0.217, 'release_readiness': 0.859, 'cycle_id': 3.0, 'catalyst_age_cycles': 1.0, 'catalyst_regen_count': 0.0, 'catalyst_lifetime_fraction': 0.981, 'catalyst_regeneration_potential': 0.766, 'catalyst_replacement_urgency': 0.227}`
- final actions: `['release']`
- blocked: `['dose_oxidant', 'replace_catalyst']`
- next scenario: `None`

## matrix_shock

### Step 0 / matrix_shock

- summary: 最终仲裁：执行 预处理或切换处理单元 等 3 个动作；未通过安全门 ['release_readiness_gate', 'residual_risk_gate']。
- strategy profile: `safety_first`
- state: `{'pollutant_residual_risk': 0.549, 'reaction_completion': 0.402, 'oxidant_remaining': 0.641, 'catalyst_activity': 0.5, 'matrix_interference': 0.88, 'byproduct_risk': 0.373, 'offline_validation_confidence': 0.0, 'offline_residual_proxy': 0.0, 'offline_validation_age_min': 999.0, 'hydraulic_confidence': 0.963, 'sensor_confidence': 1.0, 'compliance_probability': 0.58, 'recycle_gain': 0.405, 'release_readiness': 0.58, 'cycle_id': 1.0, 'catalyst_age_cycles': 4.0, 'catalyst_regen_count': 0.0, 'catalyst_lifetime_fraction': 0.82, 'catalyst_regeneration_potential': 0.597, 'catalyst_replacement_urgency': 0.356}`
- final actions: `['switch_or_pretreat', 'hold_for_validation', 'recirculate']`
- blocked: `['release', 'dose_oxidant', 'replace_catalyst']`
- next scenario: `clean_release`

### Step 1 / clean_release

- summary: 最终仲裁：执行 达标放行 等 1 个动作；未通过安全门 []。
- strategy profile: `safety_first`
- state: `{'pollutant_residual_risk': 0.303, 'reaction_completion': 0.527, 'oxidant_remaining': 0.717, 'catalyst_activity': 0.31, 'matrix_interference': 0.298, 'byproduct_risk': 0.295, 'offline_validation_confidence': 0.171, 'offline_residual_proxy': 0.418, 'offline_validation_age_min': 58.5, 'hydraulic_confidence': 1.0, 'sensor_confidence': 1.0, 'compliance_probability': 0.863, 'recycle_gain': 0.257, 'release_readiness': 0.833, 'cycle_id': 2.0, 'catalyst_age_cycles': 5.0, 'catalyst_regen_count': 0.0, 'catalyst_lifetime_fraction': 0.799, 'catalyst_regeneration_potential': 0.635, 'catalyst_replacement_urgency': 0.355}`
- final actions: `['release']`
- blocked: `['dose_oxidant', 'replace_catalyst']`
- next scenario: `None`

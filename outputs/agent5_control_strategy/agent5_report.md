# Agent 5 控制策略模拟报告

- Agent: `control_strategy_agent`
- 策略可信度: `0.89`
- 摘要: 首要控制动作：暂存并旁路验证，评分 0.976。

## 动作排序

### 暂存并旁路验证（score=0.976）

- 参数: `{'hold_min': 18, 'validation_delay_min': 9, 'validation': 'COD/TOC、目标污染物、余氧化剂或副产物快检'}`
- 需要人工复核: `False`
- 依据: `{'release_readiness': 0.755, 'compliance_probability': 0.943, 'byproduct_risk': 0.459, 'fault_ids': ['hydraulic_retention_anomaly', 'matrix_interference', 'release_evidence_insufficient', 'sensor_data_unreliable'], 'knowledge_action_bias': 0.22}`

### 校准或降权异常传感器（score=0.914）

- 参数: `{'channels': 'use Agent 1 low-score channels', 'apply_to_soft_sensor': True}`
- 需要人工复核: `True`
- 依据: `{'fault_ids': ['hydraulic_retention_anomaly', 'matrix_interference', 'release_evidence_insufficient', 'sensor_data_unreliable'], 'knowledge_action_bias': 0.194}`

### 核查泵阀与回流管路（score=0.78）

- 参数: `{'check_items': ['pump', 'valve', 'recycle_line', 'actual_flow'], 'pause_release': True}`
- 需要人工复核: `True`
- 依据: `{'fault_ids': ['hydraulic_retention_anomaly', 'matrix_interference', 'release_evidence_insufficient', 'sensor_data_unreliable']}`

### 预处理或切换处理单元（score=0.31）

- 参数: `{'candidate_units': ['coagulation', 'adsorption', 'membrane', 'deep_oxidation']}`
- 需要人工复核: `True`
- 依据: `{'matrix_interference': 0.414, 'fault_ids': ['hydraulic_retention_anomaly', 'matrix_interference', 'release_evidence_insufficient', 'sensor_data_unreliable']}`

### 继续回流处理（score=0.219）

- 参数: `{'recycle_ratio': 0.32, 'extra_retention_min': 14}`
- 需要人工复核: `False`
- 依据: `{'recycle_gain': 0.066, 'pollutant_residual_risk': 0.156, 'cycle_id': 5, 'fault_ids': ['hydraulic_retention_anomaly', 'matrix_interference', 'release_evidence_insufficient', 'sensor_data_unreliable'], 'knowledge_action_bias': 0.082}`

### 再生或更换催化剂（score=0.002）

- 参数: `{'regen_intensity': 0.34, 'downtime_min': 40, 'confirm_with': '催化剂活性、表面污染或压降快检'}`
- 需要人工复核: `True`
- 依据: `{'catalyst_activity': 0.761, 'reaction_completion': 0.822, 'pollutant_residual_risk': 0.156, 'oxidant_remaining': 0.775, 'fault_ids': ['hydraulic_retention_anomaly', 'matrix_interference', 'release_evidence_insufficient', 'sensor_data_unreliable']}`

### 补加氧化剂（score=0.0）

- 参数: `{'dose_factor': 0.1, 'confirm_with': '余氧化剂快检'}`
- 需要人工复核: `False`
- 依据: `{'oxidant_remaining': 0.775, 'byproduct_risk': 0.459, 'dose_factor': 0.1, 'fault_ids': ['hydraulic_retention_anomaly', 'matrix_interference', 'release_evidence_insufficient', 'sensor_data_unreliable']}`

### 达标放行（score=0.0）

- 参数: `{'release_gate': 'release_readiness >= 0.82 and residual <= 0.35 and hydraulic_confidence >= 0.7 and byproduct_risk <= 0.65'}`
- 需要人工复核: `False`
- 依据: `{'release_readiness': 0.755, 'compliance_probability': 0.943, 'pollutant_residual_risk': 0.156, 'hydraulic_confidence': 0.997, 'byproduct_risk': 0.459, 'knowledge_action_bias': -0.22}`

## 可执行计划

- 暂存并旁路验证：参数 {'hold_min': 18, 'validation_delay_min': 9, 'validation': 'COD/TOC、目标污染物、余氧化剂或副产物快检'}；依据 {'release_readiness': 0.755, 'compliance_probability': 0.943, 'byproduct_risk': 0.459, 'fault_ids': ['hydraulic_retention_anomaly', 'matrix_interference', 'release_evidence_insufficient', 'sensor_data_unreliable'], 'knowledge_action_bias': 0.22}。
- 校准或降权异常传感器：参数 {'channels': 'use Agent 1 low-score channels', 'apply_to_soft_sensor': True}；依据 {'fault_ids': ['hydraulic_retention_anomaly', 'matrix_interference', 'release_evidence_insufficient', 'sensor_data_unreliable'], 'knowledge_action_bias': 0.194}。
- 核查泵阀与回流管路：参数 {'check_items': ['pump', 'valve', 'recycle_line', 'actual_flow'], 'pause_release': True}；依据 {'fault_ids': ['hydraulic_retention_anomaly', 'matrix_interference', 'release_evidence_insufficient', 'sensor_data_unreliable']}。

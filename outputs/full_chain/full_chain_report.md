# 多智能体闭环全链条模拟报告

## data_quality

- Agent: `data_quality_agent`
- confidence: `0.794`
- summary: 发现 0 个严重问题、8 个警告；传感可信度评分 0.79。

- 检查数据采集链路；缺失窗口内禁止直接放行高风险水样。
- 触发旁路复测或离线快检，避免异常尖峰直接驱动加药/回流决策。
- 对卡死传感器进行清洗、校准或更换；下游软传感器降低该通道权重。
- 将疑似漂移通道标记为低可信，并增加最近一次离线真值校准。
- 持续偏移通道需要结合设备状态解释；控制器应暂停使用该通道做精细投加判断。

## soft_sensor

- Agent: `soft_sensor_agent`
- confidence: `0.755`
- summary: 估计污染物残留风险 0.16，达标概率 0.94，副产物风险 0.46，离线验证置信度 0.00，回流边际收益 0.07。

- 水质估计达标概率较高，但释放准备度不足，应先进入机理诊断或旁路校准。

## mechanism

- Agent: `mechanism_agent`
- confidence: `0.76`
- summary: 首要机理假设：水质可能已处理完成但证据不足，评分 0.816。

- 保持暂存，进行旁路快检；若校准通过再放行。
- 进入旁路快检或离线校准，禁止直接自动放行。
- 核查泵阀、管路堵塞和实际回流比，再更新停留时间估计。

## fault_diagnosis

- Agent: `fault_diagnosis_agent`
- confidence: `0.727`
- summary: 首要故障模式：达标证据不足导致放行受阻，评分 0.793。

- 维持暂存并进行快速离线验证；验证通过后再进入放行候选。
- 核查泵、阀、回流管路和实际流量；必要时重新计算 HRT。
- 先做传感器校准/旁路快检；在校准前禁止自动放行。
- 检测盐度、COD/TOC、浊度来源；判断是否需要预处理或切换单元。

## catalyst_lifecycle

- Agent: `catalyst_lifecycle_agent`
- confidence: `0.72`
- summary: 催化剂生命周期建议：维持监测，评分 0.627。

- 维持监测：评分 0.627；依据：寿命风险尚可接受，暂不触发维护动作。

## validation_planning

- Agent: `validation_planning_agent`
- confidence: `0.835`
- summary: 验证规划：matrix_shock_characterization，紧迫度 0.958。

- matrix_shock_characterization：暂存 35 min，等待验证 18 min，验证目标 ['COD_or_TOC', 'UV254_reference', 'grab_sample_COD_or_TOC', 'salinity_or_EC_reference', 'sensor_calibration_check', 'target_pollutant', 'target_pollutant_proxy', 'turbidity_reference']。

## control_strategy

- Agent: `control_strategy_agent`
- confidence: `0.898`
- summary: 首要控制动作：暂存并旁路验证，评分 1.0。

- 暂存并旁路验证：参数 {'hold_min': 35, 'validation_delay_min': 18, 'validation': ['COD_or_TOC', 'UV254_reference', 'grab_sample_COD_or_TOC', 'salinity_or_EC_reference', 'sensor_calibration_check', 'target_pollutant', 'target_pollutant_proxy', 'turbidity_reference'], 'validation_plan': 'matrix_shock_characterization'}；依据 {'release_readiness': 0.755, 'compliance_probability': 0.943, 'byproduct_risk': 0.459, 'validation_urgency': 0.958, 'fault_ids': ['hydraulic_retention_anomaly', 'matrix_interference', 'release_evidence_insufficient', 'sensor_data_unreliable'], 'knowledge_action_bias': 0.22}。
- 校准或降权异常传感器：参数 {'channels': 'use Agent 1 low-score channels', 'apply_to_soft_sensor': True}；依据 {'fault_ids': ['hydraulic_retention_anomaly', 'matrix_interference', 'release_evidence_insufficient', 'sensor_data_unreliable'], 'knowledge_action_bias': 0.194}。
- 核查泵阀与回流管路：参数 {'check_items': ['pump', 'valve', 'recycle_line', 'actual_flow'], 'pause_release': True}；依据 {'fault_ids': ['hydraulic_retention_anomaly', 'matrix_interference', 'release_evidence_insufficient', 'sensor_data_unreliable']}。

## strategy_profile

- Agent: `strategy_profile_agent`
- confidence: `0.58`
- summary: 策略目标模板：safety_first。

- 采用 safety_first 策略目标模板；依据：存在放行、传感、水力或副产物安全压力。

## cost_safety

- Agent: `cost_safety_agent`
- confidence: `0.564`
- summary: 成本安全最优动作：暂存并旁路验证，策略目标评分 0.649，净收益评分 0.729。

- 暂存并旁路验证：策略目标评分 0.649，净收益评分 0.729；安全收益 0.8284，成本 0.25，时间 0.4024，风险 0.04519999999999999。
- 校准或降权异常传感器：策略目标评分 0.576，净收益评分 0.591；安全收益 0.7226800000000001，成本 0.22，时间 0.32448000000000005，风险 0.014039999999999997。
- 核查泵阀与回流管路：策略目标评分 0.468，净收益评分 0.501；安全收益 0.72，成本 0.18，时间 0.35，风险 0.08。

## arbitration

- Agent: `arbitration_agent`
- confidence: `0.564`
- summary: 最终仲裁：执行 暂存并旁路验证 等 3 个动作；未通过安全门 ['release_readiness_gate']。

- 执行：暂存并旁路验证；策略目标 0.649，净收益 0.729；参数 {'hold_min': 35, 'validation_delay_min': 18, 'validation': ['COD_or_TOC', 'UV254_reference', 'grab_sample_COD_or_TOC', 'salinity_or_EC_reference', 'sensor_calibration_check', 'target_pollutant', 'target_pollutant_proxy', 'turbidity_reference'], 'validation_plan': 'matrix_shock_characterization'}。
- 执行：校准或降权异常传感器；策略目标 0.576，净收益 0.591；参数 {'channels': 'use Agent 1 low-score channels', 'apply_to_soft_sensor': True}。
- 执行：核查泵阀与回流管路；策略目标 0.468，净收益 0.501；参数 {'check_items': ['pump', 'valve', 'recycle_line', 'actual_flow'], 'pause_release': True}。
- 禁止动作：release, dose_oxidant, recirculate, regenerate_catalyst, replace_catalyst。

# Agent 1 数据质控模拟报告

- Agent: `data_quality_agent`
- 传感可信度: `0.794`
- 摘要: 发现 0 个严重问题、8 个警告；传感可信度评分 0.79。

## 指标

- readings: 72
- sensor_count: 7
- missing_count: 1
- issue_count: 8
- critical_count: 0
- warning_count: 8
- confidence: 0.794
- sensor_scores: {'pH': 0.72, 'ORP_mV': 0.82, 'EC_uScm': 0.65, 'turbidity_NTU': 0.68, 'temp_C': 1.0, 'flow_Lmin': 0.44, 'UV254_abs': 1.0}

## 建议

- 检查数据采集链路；缺失窗口内禁止直接放行高风险水样。
- 触发旁路复测或离线快检，避免异常尖峰直接驱动加药/回流决策。
- 对卡死传感器进行清洗、校准或更换；下游软传感器降低该通道权重。
- 将疑似漂移通道标记为低可信，并增加最近一次离线真值校准。
- 持续偏移通道需要结合设备状态解释；控制器应暂停使用该通道做精细投加判断。
- 核查泵阀状态；低流量可能改变实际停留时间和回流收益。

## 传感通道可信权重

- pH: 0.72
- ORP_mV: 0.82
- EC_uScm: 0.65
- turbidity_NTU: 0.68
- temp_C: 1.0
- flow_Lmin: 0.44
- UV254_abs: 1.0

## 前 12 个问题

- [warning] ORP_mV / missing: ORP_mV 在 10 min 缺失。
- [warning] pH / spike: pH 在 21 min 出现突变，变化率 3.68/min。
- [warning] pH / spike: pH 在 22 min 出现突变，变化率 3.72/min。
- [warning] flow_Lmin / spike: flow_Lmin 在 58 min 出现突变，变化率 0.974/min。
- [warning] flow_Lmin / spike: flow_Lmin 在 64 min 出现突变，变化率 0.901/min。
- [warning] EC_uScm / flatline: EC_uScm 在 32-37 min 近似卡死。
- [warning] turbidity_NTU / drift_suspected: 浊度后段中位数明显高于前段，疑似传感漂移或新扰动进入系统。
- [warning] flow_Lmin / sustained_shift: flow_Lmin 在 56-61 min 持续低于基线，疑似泵阀异常或管路堵塞。

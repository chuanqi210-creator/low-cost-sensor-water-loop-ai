# Agent 2 软传感器模拟报告

- Agent: `soft_sensor_agent`
- 估计可信度: `0.755`
- 摘要: 估计污染物残留风险 0.16，达标概率 0.94，副产物风险 0.46，回流边际收益 0.07。

## 隐藏状态估计

- pollutant_residual_risk: 0.156
- reaction_completion: 0.822
- oxidant_remaining: 0.775
- catalyst_activity: 0.761
- matrix_interference: 0.414
- byproduct_risk: 0.459
- hydraulic_confidence: 0.997
- sensor_confidence: 0.755
- compliance_probability: 0.943
- recycle_gain: 0.066
- release_readiness: 0.755
- cycle_id: 5

## 合成真值校验

- pollutant_residual_risk_abs_error: 0.0728
- reaction_completion_abs_error: 0.0073
- oxidant_remaining_abs_error: 0.0206
- catalyst_activity_abs_error: 0.0885
- matrix_interference_abs_error: 0.068

## 建议

- 水质估计达标概率较高，但释放准备度不足，应先进入机理诊断或旁路校准。

## 状态问题

- [warning] low_sensor_confidence: 软测量输入可信度偏低，状态估计需要旁路检测或离线真值校准。
- [warning] release_blocked_by_uncertainty: 水质估计可能达标，但受传感可信度或回流收益约束，不建议自动放行。

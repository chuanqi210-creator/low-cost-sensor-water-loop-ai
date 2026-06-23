# Agent 3 机理解释模拟报告

- Agent: `mechanism_agent`
- 解释可信度: `0.76`
- 摘要: 首要机理假设：水质可能已处理完成但证据不足，评分 0.816。

## 机理假设排序

### 水质可能已处理完成但证据不足（score=0.816）

- 解释: 软测量显示达标概率较高，但传感可信度不足或存在漂移，不能把模型估计直接等同于安全放行。
- 行动提示: 保持暂存，进行旁路快检；若校准通过再放行。
- 证据: `{'compliance_probability': 0.943, 'release_readiness': 0.755, 'soft_issue_types': ['low_sensor_confidence', 'release_blocked_by_uncertainty'], 'knowledge_support': [{'entry_id': 'kb_sensor_limited_release_evidence', 'match_score': 0.97, 'pollutant_class': '低浓度目标污染物或慢检测指标', 'material_family': '低成本传感 + 软传感系统', 'mechanism_tags': ['sensor_uncertainty', 'release_evidence_gap']}]}`

### 传感不确定性主导（score=0.763）

- 解释: 低成本传感通道出现缺失、突变、卡死或漂移时，软测量虽然可以估计状态，但放行决策应受传感可信度约束。
- 行动提示: 进入旁路快检或离线校准，禁止直接自动放行。
- 证据: `{'sensor_confidence': 0.755, 'dq_issue_types': ['drift_suspected', 'flatline', 'missing', 'spike', 'sustained_shift'], 'knowledge_support': [{'entry_id': 'kb_sensor_limited_release_evidence', 'match_score': 0.97, 'pollutant_class': '低浓度目标污染物或慢检测指标', 'material_family': '低成本传感 + 软传感系统', 'mechanism_tags': ['sensor_uncertainty', 'release_evidence_gap']}]}`

### 水力停留时间异常（score=0.7）

- 解释: 流量持续偏低、短窗口平均流量不足或水力置信度低，会改变实际停留时间和回流收益，使模型对反应进程的判断出现偏差。
- 行动提示: 核查泵阀、管路堵塞和实际回流比，再更新停留时间估计。
- 证据: `{'dq_issue_types': ['drift_suspected', 'flatline', 'missing', 'spike', 'sustained_shift'], 'hydraulic_confidence': 0.997, 'recycle_gain': 0.066}`

### 基质干扰增强（score=0.628）

- 解释: 电导率、浊度或 pH 偏离提示高盐、高 COD、颗粒物或缓冲体系可能消耗氧化剂并抑制高级氧化反应。
- 行动提示: 评估预处理、提高氧化剂投加、调 pH 或切换到更适合高基质负荷的单元。
- 证据: `{'matrix_interference': 0.414, 'dq_issue_types': ['drift_suspected', 'flatline', 'missing', 'spike', 'sustained_shift']}`

## 知识库命中

### kb_sensor_limited_release_evidence（score=0.97）

- 污染物场景: 低浓度目标污染物或慢检测指标
- 材料/工艺族: 低成本传感 + 软传感系统
- 机制标签: `['sensor_uncertainty', 'release_evidence_gap']`
- 支持规则: `['sensor_uncertainty', 'likely_treated_but_not_releasable']`
- 解释: 低成本代理信号出现缺失、漂移或置信度不足时，软传感结果不能直接等同于放行证据。
- 行动提示: 进入校准、降权或旁路检测流程；模型估计只能作为排序依据，不能替代放行门槛。

### kb_loop_buffer_for_slow_sensing（score=0.587）

- 污染物场景: 目标污染物需慢检测或低成本代理检测的废水
- 材料/工艺族: 循环式反应器/旁路快检系统
- 机制标签: `['loop_buffer_needed', 'soft_sensor_delay', 'grey_box_inference']`
- 支持规则: `['loop_buffer_needed']`
- 解释: 当软传感认为继续循环仍有收益，而放行证据不足时，循环结构可以为慢检测、模型复估和旁路验证争取时间。
- 行动提示: 不要强行实时控制；设置暂存/回流窗口，让慢证据进入下一轮状态估计。

## 建议

- 保持暂存，进行旁路快检；若校准通过再放行。
- 进入旁路快检或离线校准，禁止直接自动放行。
- 核查泵阀、管路堵塞和实际回流比，再更新停留时间估计。

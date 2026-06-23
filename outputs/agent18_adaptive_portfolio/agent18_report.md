# Agent 18 自适应项目组合模拟报告

- stress_summary: 实施压力测试：最坏情景 combined_delay_high_intake，风险 0.356，总体韧性 0.86。
- portfolio_summary: 自适应项目组合：推荐 resilience_bridge_portfolio，评分 0.724，风险降低 0.32。
- selected_portfolio: `resilience_bridge_portfolio`
- dominant_stress_signals: `['acceptance_failure', 'budget_slow_release', 'catalyst_delay', 'high_intake_pressure', 'validation_ramp_delay']`
- load_control_policy: `{'protected_intake_fraction': 0.45, 'normalization_rule': '仅当两个连续 campaign 通过阶段验收，才从保护性进水比例逐步恢复。', 'load_controls': ['保护性进水上限 0.45', '拒绝新增高风险进水', '连续催化剂压力批次禁止排队']}`

## 项目包排序

### resilience_bridge_portfolio

- portfolio_score: `0.724`
- coverage_score: `1.0`
- expected_risk_reduction: `0.32`
- residual_risk: `0.036`
- budget_pressure: `0.875`
- covered_signals: `['acceptance_failure', 'budget_slow_release', 'catalyst_delay', 'high_intake_pressure', 'validation_ramp_delay']`
- missing_signals: `[]`
- budget_items: `['外包低价值验证', '催化剂备用供应商', '验证能力批复', '催化剂库存批复', '氧化剂库存批复']`

### phased_budget_package

- portfolio_score: `0.574`
- coverage_score: `0.4`
- expected_risk_reduction: `0.203`
- residual_risk: `0.153`
- budget_pressure: `0.2`
- covered_signals: `['acceptance_failure', 'budget_slow_release']`
- missing_signals: `['catalyst_delay', 'high_intake_pressure', 'validation_ramp_delay']`
- budget_items: `['验证能力批复', '催化剂库存批复', '氧化剂库存批复']`

### validation_bridge_package

- portfolio_score: `0.57`
- coverage_score: `0.4`
- expected_risk_reduction: `0.203`
- residual_risk: `0.153`
- budget_pressure: `0.317`
- covered_signals: `['high_intake_pressure', 'validation_ramp_delay']`
- missing_signals: `['acceptance_failure', 'budget_slow_release', 'catalyst_delay']`
- budget_items: `['外包低价值背景验证', '内部关键验证班次加班池']`

### baseline_execution

- portfolio_score: `0.422`
- coverage_score: `0.0`
- expected_risk_reduction: `0.125`
- residual_risk: `0.231`
- budget_pressure: `0.042`
- covered_signals: `[]`
- missing_signals: `['acceptance_failure', 'budget_slow_release', 'catalyst_delay', 'high_intake_pressure', 'validation_ramp_delay']`
- budget_items: `['campaign滚动复核']`

### supplier_resilience_package

- portfolio_score: `0.407`
- coverage_score: `0.2`
- expected_risk_reduction: `0.164`
- residual_risk: `0.192`
- budget_pressure: `0.6`
- covered_signals: `['catalyst_delay']`
- missing_signals: `['acceptance_failure', 'budget_slow_release', 'high_intake_pressure', 'validation_ramp_delay']`
- budget_items: `['催化剂备用供应商', '催化剂应急调拨协议', '氧化剂安全库存']`

## 预算释放顺序

- 1. 外包低价值验证：先批复后进入下一项，失败则回退到保护性进水上限。
- 2. 催化剂备用供应商：先批复后进入下一项，失败则回退到保护性进水上限。
- 3. 验证能力批复：先批复后进入下一项，失败则回退到保护性进水上限。
- 4. 催化剂库存批复：先批复后进入下一项，失败则回退到保护性进水上限。
- 5. 氧化剂库存批复：先批复后进入下一项，失败则回退到保护性进水上限。

## 建议

- 采用 resilience_bridge_portfolio 作为压力情景备用项目包，覆盖 ['acceptance_failure', 'budget_slow_release', 'catalyst_delay', 'high_intake_pressure', 'validation_ramp_delay']。
- 过渡期保护性进水比例设为 0.45，未通过两个连续 campaign 验收前不恢复满负荷。
- 预算释放顺序：外包低价值验证 -> 催化剂备用供应商 -> 验证能力批复 -> 催化剂库存批复 -> 氧化剂库存批复
- 复合压力情景下同时启动备用供应、预算拆分和外包验证。
- scenario_risk >= 0.35 时自动进入保护性进水。
- 阶段验收失败时回退并重跑队列规划和资源扩容评分。
# Agent 19 在线滚动项目控制模拟报告

- portfolio_summary: 自适应项目组合：推荐 resilience_bridge_portfolio，评分 0.724，风险降低 0.32。
- control_summary: 在线项目控制：当前模式 controlled_ramp_up，下一轮进水比例 0.68，下一预算项 本轮无需新增预算项，保持滚动复核。
- current_project_mode: `controlled_ramp_up`
- next_intake_fraction: `0.68`
- next_budget_item: `本轮无需新增预算项，保持滚动复核`

## 滚动决策

### campaign 0

- mode: `replan_and_protect`
- rolling_risk: `0.368`
- dominant_signals: `['validation_overload', 'time_budget_pressure', 'catalyst_inventory', 'high_intake_pressure', 'budget_slow_release']`
- stable_streak: `0`
- next_intake_fraction: `0.45`
- next_budget_item: `验证能力批复`
- replan_required: `True`
- replan_reasons: `['压力升高且未形成稳定验收 streak']`

### campaign 1

- mode: `steady_monitoring`
- rolling_risk: `0.0`
- dominant_signals: `['stable']`
- stable_streak: `1`
- next_intake_fraction: `0.53`
- next_budget_item: `催化剂库存批复`
- replan_required: `False`
- replan_reasons: `[]`

### campaign 2

- mode: `controlled_ramp_up`
- rolling_risk: `0.0`
- dominant_signals: `['stable']`
- stable_streak: `2`
- next_intake_fraction: `0.68`
- next_budget_item: `本轮无需新增预算项，保持滚动复核`
- replan_required: `False`
- replan_reasons: `[]`

## 建议

- 下一 campaign 进水比例控制为 0.68，项目模式为 controlled_ramp_up。
- 下一预算项优先处理：本轮无需新增预算项，保持滚动复核。
- 已形成连续稳定验收，可按 0.15 梯度恢复进水，但继续保留最终放行门。
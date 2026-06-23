# Agent 20 Campaign 遥测桥接模拟报告

- telemetry_summary: campaign 遥测桥接：生成 3 个滚动更新，最新 success_rate 1.0，验证占用 1.406。
- control_summary: 在线项目控制：当前模式 replan_and_protect，下一轮进水比例 0.35，下一预算项 本轮无需新增预算项，保持滚动复核。
- current_project_mode: `replan_and_protect`
- next_intake_fraction: `0.35`
- next_budget_item: `本轮无需新增预算项，保持滚动复核`

## 遥测滚动更新

### update 0

- cut_point_batch_count: `2`
- acceptance_passed: `True`
- success_rate: `1.0`
- validation_staff_usage: `0.161`
- time_budget_usage: `0.223`
- catalyst_spares_remaining: `1`
- oxidant_stock_units_remaining: `2.2`
- intake_pressure_multiplier: `1.25`
- bottleneck_ids: `[]`

### update 1

- cut_point_batch_count: `5`
- acceptance_passed: `True`
- success_rate: `1.0`
- validation_staff_usage: `0.824`
- time_budget_usage: `0.799`
- catalyst_spares_remaining: `0`
- oxidant_stock_units_remaining: `1.85`
- intake_pressure_multiplier: `1.3`
- bottleneck_ids: `['catalyst_inventory']`

### update 2

- cut_point_batch_count: `8`
- acceptance_passed: `True`
- success_rate: `1.0`
- validation_staff_usage: `1.406`
- time_budget_usage: `1.188`
- catalyst_spares_remaining: `0`
- oxidant_stock_units_remaining: `1.5`
- intake_pressure_multiplier: `1.337`
- bottleneck_ids: `['validation_capacity', 'campaign_time_budget', 'catalyst_inventory']`

## 在线控制结果

### campaign update 0

- mode: `steady_monitoring`
- rolling_risk: `0.285`
- dominant_signals: `['catalyst_inventory', 'high_intake_pressure', 'budget_slow_release']`
- next_intake_fraction: `0.45`
- next_budget_item: `验证能力批复`
- replan_required: `False`

### campaign update 1

- mode: `steady_monitoring`
- rolling_risk: `0.337`
- dominant_signals: `['catalyst_inventory', 'high_intake_pressure', 'budget_slow_release']`
- next_intake_fraction: `0.45`
- next_budget_item: `催化剂库存批复`
- replan_required: `False`

### campaign update 2

- mode: `replan_and_protect`
- rolling_risk: `0.694`
- dominant_signals: `['validation_overload', 'time_budget_pressure', 'catalyst_inventory', 'high_intake_pressure']`
- next_intake_fraction: `0.35`
- next_budget_item: `本轮无需新增预算项，保持滚动复核`
- replan_required: `True`

## 建议

- 下一 campaign 进水比例控制为 0.35，项目模式为 replan_and_protect。
- 下一预算项优先处理：本轮无需新增预算项，保持滚动复核。
- 触发在线重规划：重新运行队列规划、资源扩容、压力测试和项目组合选择。
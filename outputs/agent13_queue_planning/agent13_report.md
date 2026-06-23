# Agent 13 批次队列规划模拟报告

- summary: 队列规划：推荐 high_risk_first，评分 0.097。

## 策略排序

### high_risk_first

- score: `0.097`
- operating_mode: `pause_or_limit_intake`
- validation_staff_usage: `1.406`
- time_budget_usage: `1.188`
- catalyst_spares_remaining: `0`
- bottlenecks: `['validation_capacity', 'campaign_time_budget', 'catalyst_inventory']`
- next_batches: `['matrix_shock', 'catalyst_deactivation', 'matrix_shock']`

### arrival_order

- score: `0.06`
- operating_mode: `pause_or_limit_intake`
- validation_staff_usage: `2.17`
- time_budget_usage: `1.646`
- catalyst_spares_remaining: `0`
- bottlenecks: `['validation_capacity', 'campaign_time_budget', 'catalyst_inventory']`
- next_batches: `['sensor_faults', 'oxidant_limitation', 'reaction_time_insufficient']`

### validation_smoothed

- score: `0.025`
- operating_mode: `pause_or_limit_intake`
- validation_staff_usage: `1.727`
- time_budget_usage: `1.602`
- catalyst_spares_remaining: `-1`
- bottlenecks: `['validation_capacity', 'campaign_time_budget', 'catalyst_inventory']`
- next_batches: `['reaction_time_insufficient', 'sensor_faults', 'oxidant_limitation']`

### catalyst_preserving

- score: `0.025`
- operating_mode: `pause_or_limit_intake`
- validation_staff_usage: `1.667`
- time_budget_usage: `1.579`
- catalyst_spares_remaining: `-1`
- bottlenecks: `['validation_capacity', 'campaign_time_budget', 'catalyst_inventory']`
- next_batches: `['sensor_faults', 'reaction_time_insufficient', 'oxidant_limitation']`

## 建议

- high_risk_first：评分 0.097，模式 pause_or_limit_intake，验证占用 1.406，时间占用 1.188，前 3 批 ['matrix_shock', 'catalyst_deactivation', 'matrix_shock']。
- arrival_order：评分 0.06，模式 pause_or_limit_intake，验证占用 2.17，时间占用 1.646，前 3 批 ['sensor_faults', 'oxidant_limitation', 'reaction_time_insufficient']。
- validation_smoothed：评分 0.025，模式 pause_or_limit_intake，验证占用 1.727，时间占用 1.602，前 3 批 ['reaction_time_insufficient', 'sensor_faults', 'oxidant_limitation']。
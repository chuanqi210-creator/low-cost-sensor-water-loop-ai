# Agent 14 资源扩容对比模拟报告

- summary: 资源扩容：推荐 full_resource_recovery，评分 1.0。
- baseline: `{'batch_count': 8, 'success_rate': 1.0, 'total_elapsed_min': 1140.0, 'mean_elapsed_min': 142.5, 'total_cost': 6.744, 'total_energy': 3.733, 'validation_hours': 7.733, 'validation_staff_usage': 1.406, 'time_budget_usage': 1.188, 'regeneration_count': 3, 'replacement_count': 1, 'oxidant_dose_count': 2, 'catalyst_lifetime_fraction_end': 0.807, 'catalyst_activity_end': 0.836, 'catalyst_spares_remaining': 0, 'oxidant_stock_units_remaining': 1.5, 'evidence_strength': 1.0}`

## 干预方案排序

### full_resource_recovery

- score: `1.0`
- bottleneck_relief: `2.45`
- cost_index: `1.05`
- validation_staff_usage: `0.574`
- time_budget_usage: `0.864`
- catalyst_spares_remaining: `1`
- residual_bottlenecks: `[]`

### validation_shift_plus_spare

- score: `0.884`
- bottleneck_relief: `2.0`
- cost_index: `0.86`
- validation_staff_usage: `0.737`
- time_budget_usage: `1.188`
- catalyst_spares_remaining: `1`
- residual_bottlenecks: `['campaign_time_budget']`

### add_validation_shift

- score: `0.501`
- bottleneck_relief: `1.0`
- cost_index: `0.42`
- validation_staff_usage: `0.737`
- time_budget_usage: `1.188`
- catalyst_spares_remaining: `0`
- residual_bottlenecks: `['campaign_time_budget', 'catalyst_inventory']`

### add_catalyst_spare

- score: `0.441`
- bottleneck_relief: `1.0`
- cost_index: `0.62`
- validation_staff_usage: `1.406`
- time_budget_usage: `1.188`
- catalyst_spares_remaining: `1`
- residual_bottlenecks: `['validation_capacity', 'campaign_time_budget']`

### compress_low_value_validation

- score: `0.31`
- bottleneck_relief: `0.55`
- cost_index: `0.18`
- validation_staff_usage: `1.013`
- time_budget_usage: `1.188`
- catalyst_spares_remaining: `0`
- residual_bottlenecks: `['validation_capacity', 'campaign_time_budget', 'catalyst_inventory']`

### extend_campaign_window

- score: `0.254`
- bottleneck_relief: `0.45`
- cost_index: `0.32`
- validation_staff_usage: `1.406`
- time_budget_usage: `0.864`
- catalyst_spares_remaining: `0`
- residual_bottlenecks: `['validation_capacity', 'catalyst_inventory']`

### replenish_oxidant_stock

- score: `0.051`
- bottleneck_relief: `0.0`
- cost_index: `0.22`
- validation_staff_usage: `1.406`
- time_budget_usage: `1.188`
- catalyst_spares_remaining: `0`
- residual_bottlenecks: `['validation_capacity', 'campaign_time_budget', 'catalyst_inventory']`

## 建议

- full_resource_recovery：评分 1.0，解除瓶颈 2.45，验证占用 0.574，时间占用 0.864，剩余瓶颈 []。
- validation_shift_plus_spare：评分 0.884，解除瓶颈 2.0，验证占用 0.737，时间占用 1.188，剩余瓶颈 ['campaign_time_budget']。
- add_validation_shift：评分 0.501，解除瓶颈 1.0，验证占用 0.737，时间占用 1.188，剩余瓶颈 ['campaign_time_budget', 'catalyst_inventory']。
- add_catalyst_spare：评分 0.441，解除瓶颈 1.0，验证占用 1.406，时间占用 1.188，剩余瓶颈 ['validation_capacity', 'campaign_time_budget']。
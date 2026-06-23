# Agent 24 恢复放量爬坡验证报告

- source_report: `outputs/agent22_control_baseline_update/agent22_report.json`
- summary: 恢复爬坡：partial_ramp_hold；稳定轮次 1/2，安全进水上限 0.6，实际吞吐 0.625。
- verdict: `partial_ramp_hold`
- start_fraction: `0.45`
- ramp_step: `0.15`
- stable_campaigns_completed: `1/2`
- final_safe_intake_fraction: `0.6`
- final_safe_throughput_fraction: `0.625`
- limiting_attempted_fraction: `0.75`
- limiting_bottlenecks: `['campaign_time_budget']`

## 资源投影

- budget_items_applied: `['外包低价值验证', '催化剂备用供应商', '验证能力批复', '催化剂库存批复', '氧化剂库存批复']`
- validation_minutes_multiplier: `0.78`
- validation_staff_hours_delta: `5.0`
- validation_staff_hours_projected: `10.5`
- catalyst_spares_delta: `3`
- catalyst_spares_projected: `3`
- oxidant_stock_delta: `2.0`
- oxidant_stock_projected: `3.5`
- campaign_time_budget_min: `960`

## 爬坡路径

| step | attempted_intake | actual_throughput | admitted_batches | stable | bottlenecks | validation_usage | time_usage | mode |
| --- | ---: | ---: | ---: | --- | --- | ---: | ---: | --- |
| 1 | 0.6 | 0.625 | 5 | True | `[]` | 0.337 | 0.799 | normal_intake |
| 2 | 0.75 | 0.75 | 6 | False | `['campaign_time_budget']` | 0.394 | 0.978 | staggered_intake |

## 建议

- 恢复进水上限暂定为 0.6，实际吞吐 0.625；尝试 0.75 时会触发 ['campaign_time_budget']。
- 保持保护性进水并优先处理限制瓶颈，再重新运行恢复爬坡验证。
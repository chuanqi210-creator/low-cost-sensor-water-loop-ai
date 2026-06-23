# Agent 23 重规划后回放验证报告

- source_report: `outputs/agent22_control_baseline_update/agent22_report.json`
- summary: 重规划回放：validated；验证占用 1.406 -> 0.337，时间占用 1.188 -> 0.755。
- verdict: `validated`
- impact_score: `0.864`

## 对比结果

- validation_staff_usage: `1.406 -> 0.337`
- time_budget_usage: `1.188 -> 0.755`
- removed_bottlenecks: `['campaign_time_budget', 'catalyst_inventory', 'validation_capacity']`
- remaining_bottlenecks: `[]`
- throughput_fraction: `0.5`
- admitted_batch_count: `4`

## 回放投影

- baseline_version: `baseline_v1_replan`
- intake_fraction: `0.45`
- validation_minutes_multiplier: `0.78`
- validation_hours_delta: `5.0`
- catalyst_spares_delta: `3`
- oxidant_stock_delta: `2.0`
- budget_items_applied: `['外包低价值验证', '催化剂备用供应商', '验证能力批复', '催化剂库存批复', '氧化剂库存批复']`

## 建议

- 回放结论为 validated，下一轮按 0.5 吞吐比例执行并继续滚动遥测。
- 瓶颈已清空，可在连续两个 campaign 稳定后按 0.15 梯度恢复进水。
- 保留最终放行门、副产物和催化剂寿命慢证据，不因回放改善而取消安全验证。
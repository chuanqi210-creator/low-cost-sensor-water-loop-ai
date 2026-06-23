# Agent 27 恢复策略执行回放报告

- source_report: `/Users/chuchenqidawang/Documents/py学习/低成本传感循环式水处理智能闭环项目/outputs/agent26_recovery_strategy_writeback/agent26_report.json`
- campaign_report: `/Users/chuchenqidawang/Documents/py学习/低成本传感循环式水处理智能闭环项目/outputs/agent24_recovery_ramp/agent24_report.json`
- summary: 恢复执行回放：recovery_execution_validated；时间占用 0.978 -> 0.884，建议下一轮进水 0.75。
- replay_verdict: `recovery_execution_validated`
- target_intake_fraction: `0.75`
- recommended_next_intake_fraction: `0.75`
- fallback_required: `False`
- time_usage_without_strategy: `0.978`
- time_usage_with_strategy: `0.884`
- time_usage_reduction: `0.094`
- expected_time_budget_usage: `0.884`
- time_usage_delta_from_expected: `0.0`
- validation_usage_with_strategy: `0.394`
- elapsed_reduction_min: `90.2`

## 无错峰 vs 写回策略

- without_strategy_bottlenecks: `['campaign_time_budget']`
- with_strategy_bottlenecks: `[]`
- without_strategy_mode: `staggered_intake`
- with_strategy_mode: `normal_intake`
- scenario_sequence: `['matrix_shock', 'catalyst_deactivation', 'matrix_shock', 'catalyst_deactivation', 'oxidant_limitation', 'oxidant_limitation']`

## 建议

- 执行恢复策略后可维持目标进水 0.75，但 campaign 后继续运行遥测桥接、回放和爬坡复核。
- 保留 fallback_intake_fraction，不把 0.75 视为永久满负荷基线。
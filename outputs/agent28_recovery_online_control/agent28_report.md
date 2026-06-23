# Agent 28 恢复在线控制接入报告

- source_report: `outputs/agent27_recovery_execution_replay/agent27_report.json`
- baseline_report: `outputs/agent26_recovery_strategy_writeback/agent26_report.json`
- summary: 恢复在线控制：maintain_conditional_recovery；下一轮进水 0.75，重规划 False。
- recovery_control_mode: `maintain_conditional_recovery`
- next_intake_fraction: `0.75`
- fallback_intake_fraction: `0.6`
- replan_required: `False`
- recovery_replay_verdict: `recovery_execution_validated`

## 恢复 campaign 更新

- acceptance_passed: `True`
- validation_staff_usage: `0.394`
- time_budget_usage: `0.884`
- bottleneck_ids: `[]`
- recovery_policy_applied: `True`
- source_scenarios: `['matrix_shock', 'catalyst_deactivation', 'matrix_shock', 'catalyst_deactivation', 'oxidant_limitation', 'oxidant_limitation']`

## OnlineProjectControl 原始判断

- base_project_mode: `steady_monitoring`
- base_next_intake_fraction: `0.75`
- base_replan_required: `False`
- base_dominant_signals: `['stable']`

## 建议

- 维持条件恢复进水 0.75，但继续保留 fallback_intake_fraction 0.6。
- 下一 campaign 后继续运行遥测桥接、恢复执行回放和在线控制复核。
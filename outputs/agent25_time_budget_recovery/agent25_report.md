# Agent 25 时间预算恢复方案报告

- source_report: `/Users/chuchenqidawang/Documents/py学习/低成本传感循环式水处理智能闭环项目/outputs/agent24_recovery_ramp/agent24_report.json`
- baseline_report: `/Users/chuchenqidawang/Documents/py学习/低成本传感循环式水处理智能闭环项目/outputs/agent22_control_baseline_update/agent22_report.json`
- summary: 时间预算恢复：target_recovery_feasible；推荐 stagger_validation_overlap，目标进水 0.75，时间占用 0.884。
- verdict: `target_recovery_feasible`
- target_intake_fraction: `0.75`
- safe_intake_fraction: `0.6`
- selected_candidate: `stagger_validation_overlap`
- selected_time_budget_usage: `0.884`
- selected_actual_throughput_fraction: `0.75`

## 候选方案对比

| candidate | stable | target_recovery | throughput | time_usage | validation_usage | added_window | elapsed_reduction | bottlenecks | score |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| hold_safe_fraction | True | False | 0.625 | 0.799 | 0.337 | 0 | 0.0 | `[]` | 0.628 |
| extend_campaign_window_120min | True | True | 0.75 | 0.869 | 0.394 | 120 | 0.0 | `[]` | 0.777 |
| stagger_validation_overlap | True | True | 0.75 | 0.884 | 0.394 | 0 | 90.2 | `[]` | 0.788 |
| time_smoothed_queue | True | True | 0.75 | 0.628 | 0.337 | 0 | 0.0 | `[]` | 0.818 |
| hybrid_overlap_plus_60min | True | True | 0.75 | 0.832 | 0.394 | 60 | 90.2 | `[]` | 0.768 |

## 推荐方案批次顺序

- queue_policy: `source_order`
- scenario_sequence: `['matrix_shock', 'catalyst_deactivation', 'matrix_shock', 'catalyst_deactivation', 'oxidant_limitation', 'oxidant_limitation']`

## 建议

- 采用 `stagger_validation_overlap` 作为下一轮时间预算恢复方案，目标进水比例 0.75，预计时间占用 0.884。
- 可把恢复到目标比例作为有条件动作，但必须保留 campaign 后遥测回放和瓶颈复核。
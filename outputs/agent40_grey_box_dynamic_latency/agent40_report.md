# Agent 40 灰箱动态延迟审计报告

- summary: 灰箱动态延迟审计：synthetic_latency_budget_ready_needs_field_timestamps；延迟违约率 0.200，最小证据余量 -31.0 min。
- latency_status: `synthetic_latency_budget_ready_needs_field_timestamps`
- latency_budget_violation_rate: `0.2`
- release_gate_can_use_latency_budget: `False`

## 生成文件

- grey_box_dynamic_latency: `deliverables/grey_box_dynamic_latency.md`
- agent40_report: `outputs/agent40_grey_box_dynamic_latency/agent40_report.md`
- latency_budget_metrics: `outputs/grey_box_dynamic_latency/latency_budget_metrics.json`

## 风险边界

- `field_timestamps_required_for_latency_budget`：当前延迟预算仍基于 synthetic replay 和文献约束，需要现场采样、检测、执行器和回流时间戳验证。
- `release_evidence_latency_exceeds_loop_credit`：循环/暂存争取到的时间不足以等待慢证据，不能把仿真放行直接外推到现场。
- `conformal_release_gate_not_field_ready`：软传感保形校准尚未通过 field holdout，延迟预算即使可行也不能单独授权放行。
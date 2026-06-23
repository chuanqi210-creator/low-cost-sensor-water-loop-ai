# Agent 51 催化剂活性代理观测报告

- summary: 催化剂活性代理观测：synthetic_catalyst_proxy_design_ready_needs_field_labels；当前代理观测 0.331，补点后 0.720。
- catalyst_proxy_status: `synthetic_catalyst_proxy_design_ready_needs_field_labels`
- proxy_observability_after_recommended_patch: `0.72`
- weak_state_coverage_after_proxy_design: `0.72`
- weak_axis_repair_status: `agent48_catalyst_axis_requires_proxy_patch_and_field_label`
- repair_score: `0.983`
- field_proxy_holdout_summary_status: `field_proxy_holdout_coverage_gaps`
- field_proxy_holdout_scoreable_batch_count: `0`

## 生成文件

- catalyst_activity_proxy: `deliverables/catalyst_activity_proxy.md`
- agent51_report: `outputs/agent51_catalyst_activity_proxy/agent51_report.md`
- catalyst_activity_proxy_metrics: `outputs/catalyst_activity_proxy/catalyst_activity_proxy_metrics.json`
- field_proxy_holdout_summary: `outputs/catalyst_activity_proxy/field_proxy_holdout_summary.json`

## 风险边界

- `proxy_required_signals_missing`：催化剂活性代理仍缺少床前后差分、压降或再生事件相关信号。
- `field_catalyst_labels_required`：当前代理只是在 synthetic proxy cases 上可计算，必须用真实催化剂活性/再生/压降标签验证。
- `field_proxy_holdout_summary_not_ready`：已提供 field proxy holdout 摘要，但批次、信号、标签或主表上下文不足，暂不能作为 Agent51 field validation 输入。
- `catalyst_proxy_cannot_relax_agent49_block`：未通过 field proxy holdout 前，Agent49 的催化剂不确定性保护规则仍必须保留。
- `agent48_catalyst_axis_not_recoverable_by_current_candidate_pool`：Agent48 诊断显示 catalyst_activity 弱轴无法由当前低成本候选池自然补足，必须通过代理补点和 field labels 修复。
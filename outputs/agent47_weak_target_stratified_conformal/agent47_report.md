# Agent 47 弱目标分层保形校准报告

- summary: 弱目标分层保形校准：weak_target_stratified_synthetic_candidate_needs_field_holdout；最弱目标 matrix_interference coverage=0.875。
- weak_target_stratified_status: `weak_target_stratified_synthetic_candidate_needs_field_holdout`
- failed_check_ids: `['WTC0_field_holdout_origin', 'WTC2_weak_target_coverage']`

## 生成文件

- weak_target_stratified_conformal: `/Users/chuchenqidawang/Documents/低成本传感循环式水处理智能闭环项目/deliverables/weak_target_stratified_conformal.md`
- agent47_report: `/Users/chuchenqidawang/Documents/低成本传感循环式水处理智能闭环项目/outputs/agent47_weak_target_stratified_conformal/agent47_report.md`
- weak_target_stratified_metrics: `/Users/chuchenqidawang/Documents/低成本传感循环式水处理智能闭环项目/outputs/weak_target_stratified_conformal/weak_target_stratified_metrics.json`

## 风险边界

- `WTC0_field_holdout_origin_failed`：弱目标分层阈值必须由真实 field holdout 确认后才可交给 release gate。
- `WTC2_weak_target_coverage_failed`：弱目标 coverage 必须单独达标，不能被总体 coverage 掩盖。
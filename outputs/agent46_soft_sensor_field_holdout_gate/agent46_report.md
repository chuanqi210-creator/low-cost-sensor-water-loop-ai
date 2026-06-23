# Agent 46 软传感 Field Holdout 放行门控报告

- summary: 软传感 field holdout 放行门控：soft_sensor_release_gate_blocked_non_field_holdout；可写 release gate False，自动放行 False。
- gate_status: `soft_sensor_release_gate_blocked_non_field_holdout`
- can_write_to_release_gate: `False`
- failed_check_ids: `['SFG0_field_holdout_origin', 'SFG5_weak_target_coverage']`

## 生成文件

- soft_sensor_field_holdout_gate: `/Users/chuchenqidawang/Documents/低成本传感循环式水处理智能闭环项目/deliverables/soft_sensor_field_holdout_gate.md`
- agent46_report: `/Users/chuchenqidawang/Documents/低成本传感循环式水处理智能闭环项目/outputs/agent46_soft_sensor_field_holdout_gate/agent46_report.md`
- field_holdout_gate_metrics: `/Users/chuchenqidawang/Documents/低成本传感循环式水处理智能闭环项目/outputs/soft_sensor_field_holdout_gate/field_holdout_gate_metrics.json`

## 风险边界

- `SFG0_field_holdout_origin_failed`：软传感不确定性与 conformal 校准都必须来自真实 field holdout。
- `SFG5_weak_target_coverage_failed`：催化剂活性和基质抑制是弱观测目标，不能只看总体覆盖率。
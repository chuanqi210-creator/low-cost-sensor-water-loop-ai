# Agent 34 实证校准入口门控报告

- summary: 实证校准门控：calibration_protocol_ready_waiting_for_field_data；数据门 5/6 通过。
- calibration_gate_status: `calibration_protocol_ready_waiting_for_field_data`
- gate_score: `0.833`
- accepted_gates: `5/6`

## 生成文件

- calibration_protocol: `/Users/chuchenqidawang/Documents/低成本传感循环式水处理智能闭环项目/deliverables/field_calibration_protocol.md`
- acceptance_gates: `/Users/chuchenqidawang/Documents/低成本传感循环式水处理智能闭环项目/deliverables/field_data_acceptance_gates.md`
- calibration_runbook: `/Users/chuchenqidawang/Documents/低成本传感循环式水处理智能闭环项目/deliverables/field_calibration_runbook.md`
- agent34_report: `/Users/chuchenqidawang/Documents/低成本传感循环式水处理智能闭环项目/outputs/agent34_field_calibration_gate/agent34_report.md`

## 建议

- 先按 G0-G2 采集最小现场数据包：传感时间序列、离线标签和 campaign 操作日志。
- 不要用 synthetic/sample 行重训软传感器；它们只用于接口演示和脚本联调。
- 现场数据通过验收门后，再按 P1-P5 顺序写回模型参数并重跑全链条回归。

## 风险边界

- `field_data_required_before_calibration`：当前只能生成校准门控和采集验收计划；必须导入真实 field 数据后才能执行参数校准。
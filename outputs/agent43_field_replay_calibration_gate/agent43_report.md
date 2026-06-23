# Agent 43 Field Replay Calibration Gate 报告

- summary: 现场回放校准门：synthetic_replay_gate_blocked；G6 7/8，保护性写回 False。
- field_replay_gate_status: `synthetic_replay_gate_blocked`
- accepted_gates: `7/8`
- can_write_to_protective_control: `False`
- can_write_to_release_gate: `False`

## 生成文件

- field_replay_calibration_gate: `/Users/chuchenqidawang/Documents/低成本传感循环式水处理智能闭环项目/deliverables/field_replay_calibration_gate.md`
- agent43_report: `/Users/chuchenqidawang/Documents/低成本传感循环式水处理智能闭环项目/outputs/agent43_field_replay_calibration_gate/agent43_report.md`
- g6_p6_gate_metrics: `/Users/chuchenqidawang/Documents/低成本传感循环式水处理智能闭环项目/outputs/field_replay_calibration_gate/g6_p6_gate_metrics.json`

## 风险边界

- `G6_1_field_origin`：data_origin 必须为 field，synthetic/sample 不得写入快代理控制。
# 灰箱动态延迟审计

- latency_status：`synthetic_latency_budget_ready_needs_field_timestamps`
- latency_readiness_score：`0.443`
- evidence_stage：`synthetic_replay`
- field_timestamp_coverage：`0.0`
- latency_budget_violation_rate：`0.2`
- minimum_evidence_margin_min：`-31.0`
- minimum_action_margin_min：`43.0`
- release_gate_can_use_latency_budget：`False`

## 方法契约

- upgrade_id：`grey_box_dynamic_control_latency`
- borrowed_from：`['parsa_2024_dynamic_control_review']`
- 现实映射：把循环、暂存、低频采样、离线验证、人工复核和执行器响应共同建成时序约束。
- 数据需求：sampling_timestamp, soft_sensor_prediction_timestamp, offline_sample_timestamp, offline_result_timestamp, actuator_command_timestamp, actuator_effect_timestamp, recycle_start_end_timestamp, hold_tank_release_timestamp, batch_id
- 评价指标：latency_budget_violation_rate, minimum_evidence_margin_min, minimum_action_margin_min, field_replay_success_rate, closed_loop_stability_under_delay
- 失败边界：synthetic replay 中的闭环稳定不等于 PLC/人工复核/检测排队/执行器滞后条件下可执行。

## 场景延迟预算

| 场景 | 状态 | 行动余量 min | 证据余量 min | 循环时间信用 min | 慢证据延迟 min | 失败边界 |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| `sensor_faults` | `grey_box_latency_feasible` | 69.0 | 26.0 | 99.0 | 73.0 | synthetic replay 中的闭环稳定不等于 PLC/人工复核/检测排队/执行器滞后条件下可执行。 |
| `oxidant_limitation` | `grey_box_latency_feasible` | 43.0 | 39.0 | 66.0 | 27.0 | synthetic replay 中的闭环稳定不等于 PLC/人工复核/检测排队/执行器滞后条件下可执行。 |
| `reaction_time_insufficient` | `grey_box_latency_feasible` | 128.0 | 54.0 | 103.0 | 49.0 | synthetic replay 中的闭环稳定不等于 PLC/人工复核/检测排队/执行器滞后条件下可执行。 |
| `catalyst_deactivation` | `grey_box_latency_feasible` | 196.0 | 71.0 | 192.0 | 121.0 | synthetic replay 中的闭环稳定不等于 PLC/人工复核/检测排队/执行器滞后条件下可执行。 |
| `matrix_shock` | `needs_longer_buffer_or_fast_proxy` | 47.0 | -31.0 | 84.0 | 115.0 | synthetic replay 中的闭环稳定不等于 PLC/人工复核/检测排队/执行器滞后条件下可执行。 |

## 结论

- 把采样时间、软传感计算时间、人工复核、执行器响应、混合时间、回流停留时间和离线检测 turnaround 写入 field schema。
- 用真实 timestamped campaign replay 计算 latency_budget_violation_rate，不能只用 synthetic episode 的步数或成功率证明闭环可执行。
- 优先重设 matrix_shock 的暂存/回流窗口、快检代理信号或自动执行器逻辑，直到 evidence_margin_min 和 action_latency_margin_min 同时为正。
- 当前只允许把延迟预算作为模型真实性审计层，不允许作为现场自动放行依据。
# 现场实证校准协议

- 当前门控状态：`calibration_protocol_ready_waiting_for_field_data`
- 数据来源：`synthetic`
- 当前接口状态：`template_ready_not_field_validated`
- 回归基线：`213 passed`

## 校准顺序

### P0_field_snapshot 冻结现场原始数据快照

- 动作：先建立 raw/imported/accepted 三层数据目录，记录采样设备、人员和导入版本。
- 上游任务是否就绪：`True`
- 当前阻塞项：[]

### P1_sensor_noise_drift 标定传感噪声与漂移

- 动作：更新 DataQualityAgent 阈值、sensor_confidence 和采样噪声模型。
- 上游任务是否就绪：`True`
- 当前阻塞项：[]

### P2_soft_sensor_retraining 重训软传感器

- 动作：用离线标签校准污染物残留、反应完成度、副产物风险和达标概率。
- 上游任务是否就绪：`True`
- 当前阻塞项：[]

### P3_catalyst_lifecycle 校准催化剂寿命

- 动作：更新再生/更换门槛、寿命衰减和压降风险。
- 上游任务是否就绪：`True`
- 当前阻塞项：[]

### P4_loop_time_budget 校准循环时间预算

- 动作：更新暂存/回流/验证错峰收益和 0.75/0.60 恢复边界。
- 上游任务是否就绪：`True`
- 当前阻塞项：[]

### P5_cost_deployment 校准成本与部署接口

- 动作：更新传感器经济性、资源扩容成本和 PLC/SCADA 接口约束。
- 上游任务是否就绪：`True`
- 当前阻塞项：[]

### P6_timestamped_fast_proxy_replay 校准时间戳回放与快代理

- 动作：先按 Agent44 协议导入带 metadata.json 的 sensor、lab、operation 和 fast_proxy_event_log CSV 包，通过 provenance、field origin、字段、类型转换和 batch 回连验收后，再按 Agent42 schema 重算 matrix_shock 快代理 precision/recall、提前量和误触发成本，最后由 Agent45 汇总 Agent44 -> Agent42 -> Agent43 完整证据链；软传感 release gate 需另行按 Agent36 -> Agent39 -> Agent47 -> Agent46 使用真实 field holdout 校准。
- 上游任务是否就绪：`True`
- 当前阻塞项：[`field_labeled_timestamped_replay_missing`]

## 参数写回对象

- `DataQualityAgent`：sensor_ranges、rate_limits、flatline_eps、sensor_confidence thresholds
- `SoftSensorAgent`：soft_sensor_calibrator、label windows、uncertainty calibration
- `ValidationPlanningAgent`：offline validation delay、release gate、qa_flag weighting
- `CatalystLifecycleAgent`：regen threshold、replacement urgency、lifetime decay curve
- `MatrixShockFastProxyAgent`：proxy thresholds、specificity guard、protective trigger boundary
- `TimestampedCampaignReplayAgent`：timestamp coverage、precision/recall、lead-time and false-positive cost gates
- `RecoveryOnlineControlAgent`：next_intake_fraction、fallback triggers、campaign review gates
- `LongTermEconomicsAgent`：unit costs、lead times、staff capacity、deployment interface points

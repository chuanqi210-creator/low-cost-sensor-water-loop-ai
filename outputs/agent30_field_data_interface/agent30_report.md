# Agent 30 真实数据接口与校准准备报告

- summary: 真实数据接口：template_ready_not_field_validated；字段完整度 1.000，校准就绪度 1.000。
- data_origin: `synthetic`
- interface_status: `template_ready_not_field_validated`
- calibration_readiness_score: `1.0`
- field_coverage: `1.0`
- linkage_score: `1.0`

## 生成文件

- schema: `/Users/chuchenqidawang/Documents/低成本传感循环式水处理智能闭环项目/outputs/agent30_field_data_interface/field_data_schema.json`
- templates: `/Users/chuchenqidawang/Documents/低成本传感循环式水处理智能闭环项目/outputs/agent30_field_data_interface/field_data_templates`
- synthetic_package: `/Users/chuchenqidawang/Documents/低成本传感循环式水处理智能闭环项目/outputs/agent30_field_data_interface/synthetic_field_data_package`
- doc: `/Users/chuchenqidawang/Documents/低成本传感循环式水处理智能闭环项目/docs/field_data_interface_spec.md`

## 数据表状态

| 表 | 记录数 | 状态 | 表评分 | 缺失字段 |
| --- | ---: | --- | ---: | --- |
| sensor_timeseries | 288 | `import_ready` | 1.0 | [] |
| offline_lab_results | 24 | `import_ready` | 1.0 | [] |
| catalyst_lifecycle | 8 | `import_ready` | 1.0 | [] |
| campaign_operation_log | 35 | `import_ready` | 1.0 | [] |
| site_topology_or_bed_geometry | 1 | `import_ready` | 1.0 | [] |
| cost_deployment | 4 | `import_ready` | 1.0 | [] |

## 校准任务

| 任务 | 就绪 | 得分 | 阻塞项 | 模型更新 |
| --- | --- | ---: | --- | --- |
| P1_sensor_noise_drift | `True` | 1.0 | [] | 校准 DataQualityAgent 阈值、采样噪声模型和 sensor_confidence。 |
| P2_soft_sensor_retraining | `True` | 1.0 | [] | 重训 soft sensor calibrator，并估计不可观测状态的不确定性。 |
| P3_catalyst_lifecycle | `True` | 1.0 | [] | 校准再生/更换门槛、寿命衰减和副产物安全门。 |
| P4_loop_time_budget | `True` | 1.0 | [] | 校准 Agent24-28 的时间预算、错峰收益、恢复爬坡和 fallback triggers。 |
| P5_cost_deployment | `True` | 1.0 | [] | 校准传感器经济性、资源扩容成本、预算释放顺序和 PLC/SCADA 接口。 |
| P6_pressure_headloss_replay_contract | `True` | 1.0 | [] | 校准 pressure/headloss 是否能作为 catalyst_activity 与 hydraulic anomaly 的候选代理，并保持执行器阻断边界。 |

## 建议

- 当前接口模板可运行，下一步用真实现场数据替换 synthetic/sample 行。
- P1-P5 校准任务在字段契约上均已具备模板入口；真实采集时应优先保证 batch_id 可回连。
- 先采集同一批次的在线传感时间序列、离线检测标签和 campaign 操作日志，再补催化剂寿命与经济性记录。

## 风险边界

- `synthetic_template_not_field_validated`：当前数据包可用于接口演示，但不是现场实测数据，不能作为实证校准结论。
# 现场数据验收门

| Gate | 状态 | 验收规则 | 最小现场包 | 阻塞项 |
| --- | --- | --- | --- | --- |
| `G0_data_origin` 真实数据来源确认 | 未通过 | data_origin 必须为 field，且保留原始数据快照、导入版本号和采样说明。 | 至少 3 个真实 batch 的在线传感、离线标签、操作日志和 fast proxy event log。 | ['data_origin:synthetic'] |
| `G1_sensor_stream_quality` 传感时间序列验收 | 通过 | 每个 batch 至少覆盖完整循环窗口；主键 batch_id+timestamp_min 无重复；传感器状态可追溯。 | 每个 batch >= 24 条记录，建议包含清洗前后和一次低流量扰动。 | [] |
| `G2_lab_label_alignment` 离线检测标签对齐 | 通过 | 离线标签必须能回连同一 batch 的传感窗口，并含 qa_flag、method 和单位。 | 每个关键 batch 至少 2 个标签时点，覆盖处理前/后或回流前/后。 | [] |
| `G3_catalyst_lifecycle_alignment` 催化剂寿命与副产物风险对齐 | 通过 | 催化剂活性、压降、再生次数和寿命比例必须能回连 batch_id 与离线标签。 | 至少覆盖新鲜、再生后和活性下降三个状态点。 | [] |
| `G4_loop_time_budget_alignment` 循环时间预算与回退门槛验收 | 通过 | 动作开始/结束、验证耗时、回流/暂存参数和成功标记必须完整。 | 至少 1 个完整 campaign，含一次回流或暂存动作。 | [] |
| `G5_cost_deployment_alignment` 成本和部署接口验收 | 通过 | 传感器、试剂、催化剂、人工与接口成本必须可追溯到部署项和 lead time。 | 至少包含传感器、离线检测、催化剂、氧化剂和 PLC/SCADA 接口条目。 | [] |
| `G6_timestamped_fast_proxy_replay` 时间戳回放与快代理标签验收 | 未通过 | sensor、lab、operation 和 fast_proxy_event_log 必须能按 batch_id 对齐，且包含 result_time_min、effect_time_min、field_label_matrix_shock 和 false_positive_cost_index。 | 至少 3 个真实 batch，覆盖 matrix_shock 阳性和阴性事件。 | ['field_labeled_timestamped_replay_missing'] |

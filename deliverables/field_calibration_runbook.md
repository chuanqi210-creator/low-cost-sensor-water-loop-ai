# 现场校准运行手册

## R1_collect 采集最小现场数据包

- 操作：先围绕同一批次采集 sensor_timeseries、offline_lab_results、campaign_operation_log 和 fast_proxy_event_log，再补 catalyst_lifecycle 与 cost_deployment。
- 退出条件：G0-G2 通过，且 batch_id 可回连。

## R2_accept 运行验收门

- 操作：逐表检查必需字段、主键重复、记录量、qa_flag、时间窗口和跨表 batch_id。
- 退出条件：基础门控当前通过 5/6；加入 Agent44 导入门、Agent42/43 的 G6 时间戳回放门、Agent45 证据链、Agent47 弱目标分层保形校准和 Agent46 软传感 field holdout 门控后，需同时通过 G0、Agent44、G6 和 Agent45 才能形成快代理保护性写回候选，且通过 Agent36、Agent39、Agent47 和 Agent46 才能形成软传感 release gate 校准候选。

## R3_calibrate 按 P1-P6 写回模型

- 操作：先写回数据质控和软传感，再写回催化剂、时间预算、快代理保护性触发和成本部署参数。
- 退出条件：校准后重新运行 closed_loop、scenario_sweep、robustness 和 recovery online control。

## R4_audit 形成现场校准审计包

- 操作：保留原始数据、清洗脚本、参数 diff、回归结果和边界说明。
- 退出条件：回归结果不低于当前基线：213 passed。

## 建议

- 先按 G0-G2 采集最小现场数据包：传感时间序列、离线标签、campaign 操作日志和 fast proxy event log。
- 不要用 synthetic/sample 行重训软传感器；它们只用于接口演示和脚本联调。
- 现场数据通过验收门后，再按 P1-P6 顺序写回模型参数并重跑全链条回归。

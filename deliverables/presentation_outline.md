# 汇报 / PPT 提纲

## S1 研究缘起：低成本传感下的黑箱困境

- 核心信息：高端仪器昂贵且反应/检测存在延迟，工程上常出现进水、出水可测而中间过程不可观测的问题。
- 可用证据：聊天中提出的“软传感器把黑箱变灰箱”, 低成本传感与循环争取时间的研究定位

## S2 总体思路：循环结构 + 软传感 + 多智能体

- 核心信息：系统不追求一次处理完，而是用回流、暂存、慢证据和闭环控制让行动可行。
- 可用证据：project_overview_28_agent.md, agent_system_spec.md

## S3 系统架构：执行链 + 综合接口整理展示层

- 核心信息：当前成果包包含 54 个 agent：执行链覆盖数据质控、软传感、机理诊断、控制仲裁、重规划和恢复控制，支持层覆盖综合、接口、整理、展示素材、正式展示、校准门控、模型真实性审计、软传感不确定性验证、知识图谱策展、文献证据抽取、软传感保形校准、灰箱动态延迟审计、基质冲击快代理控制、时间戳回放接口、现场回放校准门控、现场 replay 导入门、现场 replay 证据链、软传感 field holdout 放行门控、弱目标分层保形校准、管网布点与稀疏感知、多设施协同控制、模型核心优化治理、催化剂活性代理观测、多设施 replay 离线评估、最小灰箱物理机制、软传感矩阵耦合。
- 可用证据：total_agent_chain_count=54, docs/agent_system_spec.md

## S4 关键证据：从瓶颈发现到自动重规划

- 核心信息：多批次运行暴露验证工时、时间窗口和催化剂库存瓶颈，系统能转入资源扩容、分阶段实施和写回回放。
- 可用证据：outputs/agent23_post_replan_replay/agent23_report.md

## S5 工程恢复：0.75 条件恢复与 0.60 回退线

- 核心信息：0.75 不是永久满负荷结论，而是在验证错峰和 campaign 后复核条件下维持的恢复状态。
- 可用证据：outputs/agent27_recovery_execution_replay/agent27_report.md, outputs/agent28_recovery_online_control/agent28_report.md

## S6 真实数据接口：从仿真平台进入实证校准

- 核心信息：已定义五张现场数据表和 CSV 模板，用 batch_id 连接传感、离线检测、催化剂和操作日志。
- 可用证据：docs/field_data_interface_spec.md, outputs/agent30_field_data_interface/field_data_templates/

## S7 边界说明：可作为研究平台，不是现场自治结论

- 核心信息：当前结果适合项目书、原型展示和实证前仿真基线；真实漂移、寿命、副产物和部署接口仍需校准。
- 可用证据：field_data_origin=synthetic, project_maturity=research_platform_ready_for_field_calibration

## S8 下一步实证校准

- 核心信息：先接入真实传感时间序列、离线标签和 campaign 日志，再校准软传感器、时间预算和 fallback triggers。
- 可用证据：deliverables/README.md, outputs/agent30_field_data_interface/agent30_report.md

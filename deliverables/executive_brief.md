# 执行摘要

- 本项目已经从研究想法整理为可运行的低成本传感循环式水处理多智能体研究平台。
- 当前链条包含 54 个 agent：28 个执行 agent 加 26 个综合、接口、整理、展示素材、正式展示、校准门控、模型真实性审计、软传感不确定性验证、知识图谱策展、文献证据抽取、软传感保形校准、灰箱动态延迟审计、基质冲击快代理控制、时间戳回放接口、现场回放校准门控、现场 replay 导入门、现场 replay 证据链、软传感 field holdout 放行门控、弱目标分层保形校准、管网布点与稀疏感知、多设施协同控制、模型核心优化治理、催化剂活性代理观测、多设施 replay 离线评估、最小灰箱物理机制、软传感矩阵耦合 agent。
- 核心机制是用循环、暂存和慢证据窗口降低传感与反应速度要求，再用软传感器和多智能体诊断把黑箱过程变成可解释、可回退的灰箱。
- 最新恢复控制为 maintain_conditional_recovery：下一轮进水 0.75，失败回退 0.6。
- 真实数据接口状态为 template_ready_not_field_validated，当前模板可运行，但必须用现场数据替换 synthetic/sample 行。

## 汇报口径

- 用 executive_brief.md 作为项目书摘要开头，用 presentation_outline.md 作为汇报/PPT 结构。
- 用 key_metrics_table.md 统一口径，避免汇报时把 0.75 条件恢复误说成永久满负荷结论。
- 下一阶段以 field_data_interface_spec.md、timestamped_campaign_replay_schema.md 和 CSV 模板为入口接入真实现场数据。
# 用户打断带来的工作方式修正

## 已吸收的关键修正

1. 卡点必须直接说明，不能自以为是补全。
2. 展示材料不是核心；PPT、Word 和美化只在模型更新后同步。
3. 循环结构不是口号，而是为了降低传感与反应速度要求，让低频、低成本、延迟检测条件下仍可行动。
4. 黑箱问题的核心路径是软传感把黑箱变灰箱，再由多智能体诊断和闭环控制选择回流、停留、投药或放行。
5. 管网布点、稀疏感知、多维向量/矩阵是核心，不应只停留在进水/出水两个点。
6. 可借鉴污水系统多设施协同、共享经验池、奖励函数和决策树策略蒸馏，但不能机械套用泵站控制。
7. 自我打断不能模仿用户的频繁纠偏；它应是阶段边界治理闸门，并带有复盘预算/冷却思路，避免每个新想法都造成上下文切换和算力摩擦。

## 当前转化为 Agent50 的规则

- presentation-only 且不改变模型指标时，`self_interrupt_verdict=interrupt_and_refocus`。
- 模型核心内的新想法若尚未到阶段边界，只写入 `stage_boundary_deferred_backlog`；`self_interrupt_verdict` 仍保持 `continue_core_work`，`governance_review_gate` 也应为 `continue_current_micro_loop`，先完成当前小闭环。
- 若量化阶段门已经进入外部等待态，`self_interrupt_verdict=stage_boundary_wait_for_external_activation`；这不是硬中断，而是停止内部扩张，只允许真实外部证据包或新的可测试核心接口恢复主链。
- 只有当前小闭环完成、显式进入阶段边界、或出现硬风险时，才重跑 Agent50/Agent60；不要因为普通想法反复重算全局上下文。
- Agent48/Agent49、catalyst_activity、灰箱物理、软传感矩阵和工程约束优先于展示层。
- 外部方法必须先进入 evidence matrix，再决定是否实现或安装依赖。
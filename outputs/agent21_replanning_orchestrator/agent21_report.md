# Agent 21 自动重规划编排模拟报告

- control_summary: 在线项目控制：当前模式 replan_and_protect，下一轮进水比例 0.35，下一预算项 本轮无需新增预算项，保持滚动复核。
- replan_summary: 自动重规划：已重跑队列规划、资源扩容、长期经济性、分阶段实施、压力测试和项目组合；新项目包 resilience_bridge_portfolio。
- replan_executed: `True`

## 重规划链路

- queue_planning: 队列规划：推荐 high_risk_first，评分 0.097。
- resource_expansion: 资源扩容：推荐 full_resource_recovery，评分 1.0。
- long_term_economics: 长期经济性：推荐 full_recovery_program，评分 0.651，服务水平 0.723，成本指数 5.836。
- phased_implementation: 分阶段实施：围绕 full_recovery_program 形成 4 个阶段，预计第 2 个 campaign 进入完整能力验证，执行评分 0.657。
- implementation_stress_test: 实施压力测试：最坏情景 combined_delay_high_intake，风险 0.356，总体韧性 0.86。
- adaptive_portfolio: 自适应项目组合：推荐 resilience_bridge_portfolio，评分 0.724，风险降低 0.32。

## 关键输出

- selected_queue_policy: `high_risk_first`
- selected_intervention: `full_resource_recovery`
- selected_program: `full_recovery_program`
- selected_portfolio: `resilience_bridge_portfolio`
- load_control_policy: `{'protected_intake_fraction': 0.45, 'normalization_rule': '仅当两个连续 campaign 通过阶段验收，才从保护性进水比例逐步恢复。', 'load_controls': ['保护性进水上限 0.45', '拒绝新增高风险进水', '连续催化剂压力批次禁止排队']}`

## 建议

- 采用重规划后的项目包 resilience_bridge_portfolio。
- 重规划后保护性进水比例为 0.45。
- 重规划预算顺序：外包低价值验证 -> 催化剂备用供应商 -> 验证能力批复 -> 催化剂库存批复 -> 氧化剂库存批复
- 同步采用队列策略 high_risk_first。
- 把本轮 replan_trace 写回下一轮 OnlineProjectControlAgent 的基准策略。
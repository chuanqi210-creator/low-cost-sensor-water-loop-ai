# Agent 17 实施压力测试模拟报告

- implementation_summary: 分阶段实施：围绕 full_recovery_program 形成 4 个阶段，预计第 2 个 campaign 进入完整能力验证，执行评分 0.657。
- stress_summary: 实施压力测试：最坏情景 combined_delay_high_intake，风险 0.356，总体韧性 0.86。
- robustness_score: `0.86`
- guardrails: `{'max_transition_intake_fraction': 0.45, 'latest_safe_ready_campaign': 3, 'mandatory_replan_thresholds': ['scenario_risk >= 0.55', 'adjusted_ready_campaign slips by more than 1 campaign', 'protected_intake_fraction <= 0.45', '阶段验收失败'], 'dominant_worst_case': 'combined_delay_high_intake'}`

## 压力情景排序

### combined_delay_high_intake

- scenario_risk: `0.356`
- adjusted_ready_campaign: `3`
- protected_intake_fraction: `0.45`
- catalyst_stockout_risk: `0.28`
- validation_overload_risk: `0.4`
- contingency_actions:
  - 延长催化剂压力批次错峰期，启动外部调拨或备用供应商询价。
  - 临时外包低价值背景验证，内部班次只保留放行门、副产物和催化剂寿命证据。
  - 把预算拆成验证能力、催化剂库存和氧化剂库存三张批复单，先批最高瓶颈解除项。
  - 拒绝新增高风险进水，直到待验证队列和催化剂库存恢复到安全线。

### acceptance_failure

- scenario_risk: `0.22`
- adjusted_ready_campaign: `2`
- protected_intake_fraction: `0.65`
- catalyst_stockout_risk: `0.0`
- validation_overload_risk: `0.0`
- contingency_actions:
  - 阶段验收失败时回退到上一阶段进水比例，并重跑队列规划和资源扩容评分。

### catalyst_delay

- scenario_risk: `0.105`
- adjusted_ready_campaign: `3`
- protected_intake_fraction: `0.65`
- catalyst_stockout_risk: `0.28`
- validation_overload_risk: `0.0`
- contingency_actions:
  - 延长催化剂压力批次错峰期，启动外部调拨或备用供应商询价。

### validation_ramp_delay

- scenario_risk: `0.094`
- adjusted_ready_campaign: `3`
- protected_intake_fraction: `0.65`
- catalyst_stockout_risk: `0.0`
- validation_overload_risk: `0.305`
- contingency_actions:
  - 临时外包低价值背景验证，内部班次只保留放行门、副产物和催化剂寿命证据。

### budget_slow_release

- scenario_risk: `0.063`
- adjusted_ready_campaign: `2`
- protected_intake_fraction: `0.65`
- catalyst_stockout_risk: `0.0`
- validation_overload_risk: `0.0`
- contingency_actions:
  - 把预算拆成验证能力、催化剂库存和氧化剂库存三张批复单，先批最高瓶颈解除项。

### on_schedule

- scenario_risk: `0.0`
- adjusted_ready_campaign: `2`
- protected_intake_fraction: `0.65`
- catalyst_stockout_risk: `0.0`
- validation_overload_risk: `0.0`
- contingency_actions:
  - 按原分阶段计划执行，并保持每个 campaign 后滚动复核。

## 触发阈值

- `combined_delay_high_intake`: scenario_risk >= 0.35 -> ['延长催化剂压力批次错峰期，启动外部调拨或备用供应商询价。', '临时外包低价值背景验证，内部班次只保留放行门、副产物和催化剂寿命证据。']

## 建议

- 按最坏情景 combined_delay_high_intake 设置保护性进水上限 0.45，并保留重算队列的触发点。
- 延长催化剂压力批次错峰期，启动外部调拨或备用供应商询价。
- 临时外包低价值背景验证，内部班次只保留放行门、副产物和催化剂寿命证据。
- 把预算拆成验证能力、催化剂库存和氧化剂库存三张批复单，先批最高瓶颈解除项。
- 把 scenario_risk >= 0.35 设为自动升级阈值，触发备用供应、预算拆分或限流。
- 每个 campaign 后重新计算 ready campaign、库存安全线和验证队列，避免阶段计划静态化。
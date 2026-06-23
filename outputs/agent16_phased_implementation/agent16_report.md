# Agent 16 分阶段实施模拟报告

- long_term_summary: 长期经济性：推荐 full_recovery_program，评分 0.651，服务水平 0.723，成本指数 5.836。
- implementation_summary: 分阶段实施：围绕 full_recovery_program 形成 4 个阶段，预计第 2 个 campaign 进入完整能力验证，执行评分 0.657。
- execution_score: `0.657`
- schedule_risk: `0.434`
- readiness: `{'estimated_ready_campaign': 2, 'readiness_gain': 1.0, 'implementation_readiness': 0.668}`

## 阶段计划

### phase_0_transition_control

- campaign_window: `0 -> 0`
- objective: 在资源到位前防止低成本传感闭环被验证、备件或时间瓶颈压垮。
- expected_bottlenecks: `['validation_capacity', 'campaign_time_budget', 'catalyst_inventory']`
- readiness_gain: `0.16`
- actions:
  - 限制新批次进水并保留回流/暂存缓冲。
  - 把旁路验证优先级集中到放行门、副产物、催化剂寿命和高风险批次。
  - 冻结非关键验证压缩，避免压掉安全门慢证据。
- acceptance_criteria:
  - 待验证批次不过夜堆积。
  - 所有放行批次保留最终安全门证据。

### phase_1_validation_and_oxidant_ramp

- campaign_window: `1 -> 1`
- objective: 先补最快见效的验证能力和氧化剂库存，缩短软传感等待慢证据的队列。
- expected_bottlenecks: `['catalyst_inventory']`
- readiness_gain: `0.24`
- actions:
  - 验证工时容量增加 5.0 h/campaign。
  - 氧化剂库存补充 2.0 单位。
  - 建立验证优先级队列：放行门、副产物、催化剂寿命高于低价值背景项。
- acceptance_criteria:
  - 验证工时占用降到 0.85 以下。
  - 氧化剂库存高于安全库存线。

### phase_2_catalyst_procurement_lock

- campaign_window: `1 -> 2`
- objective: 把催化剂备件从临时补救转为安全库存，避免闭环控制被耗材提前期卡住。
- expected_bottlenecks: `['catalyst_inventory']`
- readiness_gain: `0.26`
- actions:
  - 采购或调拨 2 个催化剂模块备件。
  - 设置催化剂寿命低于 0.45 的预防性维护清单。
  - 到货前维持高风险批次限流，避免连续催化剂压力批次排队。
- acceptance_criteria:
  - 催化剂备件库存不低于安全库存。
  - 更换后 commissioning 置信度满足放行前要求。

### phase_3_integrated_ramp_up

- campaign_window: `2 -> 3`
- objective: 在资源到位后进行完整能力试运行，验证循环、软传感、慢证据和闭环控制的联合稳定性。
- expected_bottlenecks: `[]`
- readiness_gain: `0.34`
- actions:
  - 逐步恢复进水比例到 1.0。
  - 复核 validation_staff_usage、time_budget_usage、库存余量和最终放行门。
  - 仅压缩低价值验证项，保留副产物、催化剂衰减和最终放行慢证据。
- acceptance_criteria:
  - 连续两个 campaign 无 critical 瓶颈。
  - 放行成功率不低于 0.95。
  - 预算偏差不超过 10%。

## 库存与班次策略

- inventory_policy: `{'catalyst_safety_stock': 2, 'catalyst_reorder_point': 2, 'catalyst_order_quantity': 2, 'oxidant_safety_stock_units': 1.2, 'oxidant_reorder_point_campaigns': 1, 'oxidant_order_quantity_units': 2.0, 'stockout_action': '进入限流和错峰验证，禁止把更换或加药作为默认兜底。'}`
- validation_staffing_plan: `{'base_capacity_h_per_campaign': 5.5, 'target_capacity_h_per_campaign': 10.5, 'ramp_campaigns': 1, 'priority_order': ['release_gate', 'byproduct_risk', 'catalyst_lifecycle', 'matrix_shock', 'low_value_background'], 'qa_rule': '压缩验证只能压低价值背景项，不压最终放行门、副产物和催化剂寿命证据。'}`
- intake_policy: `{'campaign_0_max_intake_fraction': 0.5, 'pre_ready_max_intake_fraction': 0.65, 'post_ready_max_intake_fraction': 1.0, 'estimated_ready_campaign': 2, 'release_gate_mode': 'strict_until_two_stable_campaigns', 'queue_rule': '高风险批次错峰，不连续安排催化剂压力批次。'}`

## 建议

- 按 full_recovery_program 分阶段实施：第 0 个 campaign 先限流到 50%，资源到位前继续错峰。
- phase_0_transition_control：在资源到位前防止低成本传感闭环被验证、备件或时间瓶颈压垮。
- phase_1_validation_and_oxidant_ramp：先补最快见效的验证能力和氧化剂库存，缩短软传感等待慢证据的队列。
- phase_2_catalyst_procurement_lock：把催化剂备件从临时补救转为安全库存，避免闭环控制被耗材提前期卡住。
- 每个阶段必须用验证工时占用、时间预算占用、库存余量和放行安全门作为验收指标。
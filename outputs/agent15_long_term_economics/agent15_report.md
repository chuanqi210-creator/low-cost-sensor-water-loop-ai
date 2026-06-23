# Agent 15 长期经济性与提前期模拟报告

- resource_expansion_summary: 资源扩容：推荐 full_resource_recovery，评分 1.0。
- long_term_summary: 长期经济性：推荐 full_recovery_program，评分 0.651，服务水平 0.723，成本指数 5.836。
- selected_program: `full_recovery_program`
- planning_assumptions: `{'planning_horizon_campaigns': 4, 'budget_index_limit': 4.2, 'catalyst_lead_time_campaigns': 2, 'oxidant_lead_time_campaigns': 1, 'validation_staff_ramp_campaigns': 1}`

## 长期项目排序

### full_recovery_program

- program_score: `0.651`
- service_level: `0.723`
- resource_resilience: `0.805`
- multi_campaign_cost_index: `5.836`
- budget_pressure: `1.39`
- lead_time_risk: `0.53`
- residual_operational_risk: `0.299`
- residual_bottlenecks: `[]`
- actions: `{'validation_hours_delta': 5.0, 'catalyst_spares_delta': 2, 'oxidant_stock_delta': 2.0, 'campaign_time_delta_min': 360, 'validation_minutes_multiplier': 0.78}`

### balanced_recovery_program

- program_score: `0.526`
- service_level: `0.384`
- resource_resilience: `0.569`
- multi_campaign_cost_index: `3.468`
- budget_pressure: `0.826`
- lead_time_risk: `0.53`
- residual_operational_risk: `0.278`
- residual_bottlenecks: `['campaign_time_budget']`
- actions: `{'validation_hours_delta': 5.0, 'catalyst_spares_delta': 1, 'oxidant_stock_delta': 1.2, 'campaign_time_delta_min': 180, 'validation_minutes_multiplier': 1.0}`

### validation_capacity_program

- program_score: `0.339`
- service_level: `0.08`
- resource_resilience: `0.389`
- multi_campaign_cost_index: `1.76`
- budget_pressure: `0.419`
- lead_time_risk: `0.59`
- residual_operational_risk: `0.374`
- residual_bottlenecks: `['campaign_time_budget', 'catalyst_inventory']`
- actions: `{'validation_hours_delta': 5.0, 'catalyst_spares_delta': 0, 'oxidant_stock_delta': 0.0, 'campaign_time_delta_min': 0, 'validation_minutes_multiplier': 1.0}`

### inventory_buffer_program

- program_score: `0.334`
- service_level: `0.036`
- resource_resilience: `0.66`
- multi_campaign_cost_index: `2.604`
- budget_pressure: `0.62`
- lead_time_risk: `0.7`
- residual_operational_risk: `0.41`
- residual_bottlenecks: `['validation_capacity', 'campaign_time_budget']`
- actions: `{'validation_hours_delta': 0.0, 'catalyst_spares_delta': 2, 'oxidant_stock_delta': 1.6, 'campaign_time_delta_min': 0, 'validation_minutes_multiplier': 1.0}`

### minimum_response

- program_score: `0.231`
- service_level: `0.0`
- resource_resilience: `0.3`
- multi_campaign_cost_index: `0.21`
- budget_pressure: `0.05`
- lead_time_risk: `0.76`
- residual_operational_risk: `0.504`
- residual_bottlenecks: `['validation_capacity', 'campaign_time_budget', 'catalyst_inventory']`
- actions: `{'validation_hours_delta': 0.0, 'catalyst_spares_delta': 0, 'oxidant_stock_delta': 0.0, 'campaign_time_delta_min': 0, 'validation_minutes_multiplier': 1.0}`

## 建议

- full_recovery_program：评分 0.651，服务水平 0.723，成本指数 5.836，提前期风险 0.53，残余瓶颈 []。
- balanced_recovery_program：评分 0.526，服务水平 0.384，成本指数 3.468，提前期风险 0.53，残余瓶颈 ['campaign_time_budget']。
- validation_capacity_program：评分 0.339，服务水平 0.08，成本指数 1.76，提前期风险 0.59，残余瓶颈 ['campaign_time_budget', 'catalyst_inventory']。
- 提前期过渡期内采用限流、错峰进水和验证优先级调度，不能等备件到场后才处理当前批次。
- 将长期项目拆成验证能力、催化剂库存、氧化剂库存三类预算包，按瓶颈解除贡献分阶段立项。
- 压缩验证只能压低价值项目，副产物、催化剂衰减和最终放行门必须保留慢证据闭环。
# Agent 22 控制基线写回模拟报告

- source_report: `/Users/chuchenqidawang/Documents/py学习/低成本传感循环式水处理智能闭环项目/outputs/agent21_replanning_orchestrator/agent21_report.json`
- summary: 控制基线更新：已写回 baseline_v1_replan，下一轮保护性进水比例 0.45。
- update_required: `True`
- baseline_version: `baseline_v1_replan`
- writeback_summary: 写回队列 high_risk_first、项目包 resilience_bridge_portfolio、预算项 5 个。

## 写回配置

- selected_queue_policy: `{'policy_id': 'high_risk_first', 'description': 'high_risk_first', 'scenarios': ['matrix_shock', 'catalyst_deactivation', 'matrix_shock', 'catalyst_deactivation', 'oxidant_limitation', 'oxidant_limitation', 'sensor_faults', 'reaction_time_insufficient'], 'queue_score': 0.097, 'success_rate': 1.0, 'validation_staff_usage': 1.406, 'time_budget_usage': 1.188, 'catalyst_spares_remaining': 0, 'oxidant_stock_units_remaining': 1.5, 'operating_mode': 'pause_or_limit_intake', 'bottleneck_ids': ['validation_capacity', 'campaign_time_budget', 'catalyst_inventory'], 'next_batches': ['matrix_shock', 'catalyst_deactivation', 'matrix_shock']}`
- selected_portfolio: `{'package_id': 'resilience_bridge_portfolio', 'description': '组合备用供应、外包验证、预算分拆和保护性进水，覆盖复合压力情景。', 'portfolio_score': 0.724, 'coverage_score': 1.0, 'expected_risk_reduction': 0.32, 'residual_risk': 0.036, 'incremental_budget_index': 1.05, 'budget_pressure': 0.875, 'implementation_complexity': 0.34, 'covered_signals': ['acceptance_failure', 'budget_slow_release', 'catalyst_delay', 'high_intake_pressure', 'validation_ramp_delay'], 'missing_signals': [], 'budget_items': ['外包低价值验证', '催化剂备用供应商', '验证能力批复', '催化剂库存批复', '氧化剂库存批复'], 'load_controls': ['保护性进水上限 0.45', '拒绝新增高风险进水', '连续催化剂压力批次禁止排队'], 'fallback_actions': ['复合压力情景下同时启动备用供应、预算拆分和外包验证。', 'scenario_risk >= 0.35 时自动进入保护性进水。', '阶段验收失败时回退并重跑队列规划和资源扩容评分。']}`
- load_control_policy: `{'protected_intake_fraction': 0.45, 'normalization_rule': '仅当两个连续 campaign 通过阶段验收，才从保护性进水比例逐步恢复。', 'load_controls': ['保护性进水上限 0.45', '拒绝新增高风险进水', '连续催化剂压力批次禁止排队']}`
- budget_sequence: `[{'order': 1, 'budget_item': '外包低价值验证', 'release_rule': '先批复后进入下一项，失败则回退到保护性进水上限。'}, {'order': 2, 'budget_item': '催化剂备用供应商', 'release_rule': '先批复后进入下一项，失败则回退到保护性进水上限。'}, {'order': 3, 'budget_item': '验证能力批复', 'release_rule': '先批复后进入下一项，失败则回退到保护性进水上限。'}, {'order': 4, 'budget_item': '催化剂库存批复', 'release_rule': '先批复后进入下一项，失败则回退到保护性进水上限。'}, {'order': 5, 'budget_item': '氧化剂库存批复', 'release_rule': '先批复后进入下一项，失败则回退到保护性进水上限。'}]`
- guardrails: `{'max_transition_intake_fraction': 0.45, 'latest_safe_ready_campaign': 3, 'mandatory_replan_thresholds': ['scenario_risk >= 0.55', 'adjusted_ready_campaign slips by more than 1 campaign', 'protected_intake_fraction <= 0.45', '阶段验收失败'], 'dominant_worst_case': 'combined_delay_high_intake'}`
- writeback_rules: `{'stable_campaigns_required_for_ramp': 2, 'ramp_step': 0.15, 'replan_on_acceptance_failure': True, 'replan_on_ready_campaign_slip_gt': 1}`

## 建议

- 下一轮 OnlineProjectControlAgent 使用 baseline_v1_replan。
- 默认项目包写回为 resilience_bridge_portfolio，保护性进水比例 0.45。
- 默认队列策略写回为 high_risk_first。
- 每个 campaign 后继续用 CampaignTelemetryAgent 生成滚动更新，并用新基线判断是否再次重规划。
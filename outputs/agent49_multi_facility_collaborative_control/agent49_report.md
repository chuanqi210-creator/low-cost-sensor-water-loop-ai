# Agent 49 多设施协同控制报告

- summary: 多设施协同控制：synthetic_collaborative_policy_needs_field_replay；设施 agent 5 个，候选联动动作 5 个，策略蒸馏准确度 0.790。
- coordination_status: `synthetic_collaborative_policy_needs_field_replay`
- can_write_to_actuator: `False`
- control_replay_guardrails_integrated: `True`
- R3b patch: `R3_counterfactual_guardrail_reward_prior`
- catalyst_proxy_summary_status: `field_proxy_holdout_coverage_gaps`
- catalyst_guardrail_mode: `agent51_holdout_coverage_gaps_keep_catalyst_guardrail`
- pressure_headloss_candidate_pool_status: `pressure_headloss_candidate_pool_ready_needs_field_topology_and_labels`
- pressure_headloss_candidate_count: `3`
- pressure_headloss_can_relax_control_guardrail: `False`
- distilled_policy_accuracy_proxy: `0.79`

## 生成文件

- multi_facility_collaborative_control: `/Users/chuchenqidawang/Documents/低成本传感循环式水处理智能闭环项目/deliverables/multi_facility_collaborative_control.md`
- agent49_report: `/Users/chuchenqidawang/Documents/低成本传感循环式水处理智能闭环项目/outputs/agent49_multi_facility_collaborative_control/agent49_report.md`
- collaborative_control_metrics: `/Users/chuchenqidawang/Documents/低成本传感循环式水处理智能闭环项目/outputs/multi_facility_collaborative_control/collaborative_control_metrics.json`

## 风险边界

- `field_coordination_replay_required`：当前多设施协同策略只是在稀疏观测矩阵上的候选策略，需要真实多节点状态-动作-结果 replay 验证。
- `catalyst_axis_repair_prior_not_field_validated`：催化剂活性观测已通过 Agent51/R2 形成修复先验，但缺 field proxy labels，协同控制仍不能解除催化剂保护规则。
- `pressure_headloss_candidate_not_field_validated_for_control`：Agent49 已读取 pressure/headloss 候选合同，但它只能作为水力/催化剂状态解释先验，不能解除回流或催化剂动作保护边界。
- `agent51_catalyst_proxy_not_ready_for_control_relaxation`：Agent49 已读取 Agent51 field holdout summary，但催化剂代理尚未通过现场验证，因此控制侧继续保留 R3G1 保护边界。
- `policy_distillation_accuracy_not_field_ready`：决策树蒸馏规则尚未达到现场控制所需准确度，只能作为解释草案。
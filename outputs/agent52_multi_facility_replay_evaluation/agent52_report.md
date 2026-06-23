# Agent 52 多设施 Replay 离线评估报告

- summary: 多设施 replay 离线评估：synthetic_replay_evaluation_ready_needs_field_replay；synthetic joint_action_accuracy=0.667，mean_reward_regret=0.055。
- replay_evaluation_status: `synthetic_replay_evaluation_ready_needs_field_replay`
- joint_action_accuracy: `0.667`
- mean_reward_regret: `0.055`
- guardrail_aware_joint_action_accuracy: `1.0`
- guardrail_aware_mean_reward_regret: `0.0`
- catalyst_proxy_summary_status: `field_proxy_holdout_coverage_gaps`
- catalyst_guardrail_mode: `agent51_holdout_coverage_gaps_keep_catalyst_guardrail`
- pressure_headloss_boundary_consumed: `True`
- pressure_headloss_candidate_count: `3`
- pressure_headloss_field_validation_required: `True`
- control_policy_baseline_comparison_status: `synthetic_control_policy_baseline_comparison_ready_needs_field_replay`
- control_policy_baseline_strategy_count: `6`
- agent52_replay_export_status: `agent52_replay_export_ready_synthetic_only`
- agent52_replay_export_row_count: `6`
- can_write_to_actuator: `False`

## 生成文件

- multi_facility_replay_evaluation: `deliverables/multi_facility_replay_evaluation.md`
- agent52_report: `outputs/agent52_multi_facility_replay_evaluation/agent52_report.md`
- replay_evaluation_metrics: `outputs/multi_facility_replay_evaluation/replay_evaluation_metrics.json`
- agent52_replay_export_manifest: `outputs/multi_facility_replay_evaluation/agent52_replay_export/agent52_replay_export_manifest.json`
- agent52_replay_table_csv: `outputs/multi_facility_replay_evaluation/agent52_replay_export/agent52_replay_table.csv`
- agent52_replay_table_rows_json: `outputs/multi_facility_replay_evaluation/agent52_replay_export/agent52_replay_table.rows.json`

## 风险边界

- `field_replay_required_before_agent49_promotion`：Agent49 replay 评估当前只在 synthetic cases 上可运行，必须导入真实多节点 state-action-reward replay 后才能提升为执行器候选。
- `joint_action_accuracy_below_execution_threshold`：离线 joint_action_accuracy 未达到现场执行候选门槛，说明协同动作仍需重放数据校准。
- `distilled_policy_replay_accuracy_not_ready`：决策树蒸馏还只是解释代理，未通过 replay accuracy 前不能替代控制策略。
- `protective_false_positive_cost_visible`：synthetic replay 已暴露保护性动作误触发成本，需要进入 Agent49 reward 和人工复核字段。
- `guardrail_aware_replay_still_synthetic`：R3b guardrail-aware replay 已改善 synthetic 指标，但 field_replay_coverage 仍为 0，不能升级为现场控制有效性。
- `catalyst_proxy_field_validation_blocks_agent49_promotion`：Agent52 replay 已读取 Agent51 catalyst proxy 状态；在 field holdout 未通过前，Agent49 不能把催化剂保护/再生升级为执行器候选。
- `pressure_headloss_guardrail_boundary_requires_field_replay`：Agent52 已消费 Agent49 pressure/headloss 控制边界，但现场拓扑、床层几何和匹配 lab label 未过线前，它只能用于 replay 阻断解释。
# 多设施协同控制与策略蒸馏设计

- coordination_status：`synthetic_collaborative_policy_needs_field_replay`
- coordination_readiness_score：`0.36`
- can_write_to_actuator：`False`
- control_replay_guardrails_integrated：`True`
- reward_prior_guardrail_available：`True`
- catalyst_proxy_summary_status：`field_proxy_holdout_coverage_gaps`
- catalyst_proxy_scoreable_batch_count：`0`
- catalyst_guardrail_mode：`agent51_holdout_coverage_gaps_keep_catalyst_guardrail`
- pressure_headloss_candidate_pool_status：`pressure_headloss_candidate_pool_ready_needs_field_topology_and_labels`
- pressure_headloss_candidate_count：`3`
- pressure_headloss_can_relax_control_guardrail：`False`
- distilled_policy_accuracy_proxy：`0.79`
- top_ranked_action：`J4_safe_low_cost_standby`

## Facility Agents

| Agent | Role | Observed Nodes | Candidate Actions |
| --- | --- | --- | --- |
| `F0_equalization_buffer_agent` | 均质/暂存/进水扰动削峰 | ['N0_influent', 'N1_equalization_tank'] | ['hold_and_homogenize', 'divert_to_buffer', 'reduce_intake_fraction'] |
| `F1_reaction_core_agent` | 反应核心与药剂/氧化剂调节 | ['N2_reactor_mid'] | ['extend_reaction_retention', 'adjust_oxidant_dose', 'pulse_mixing'] |
| `F2_catalyst_bed_agent` | 催化剂床保护、再生与切换 | ['N3_catalyst_bed_outlet'] | ['protect_catalyst_bed', 'schedule_regeneration', 'switch_parallel_bed'] |
| `F3_recirculation_loop_agent` | 回流、延长停留时间和低频观测缓冲 | ['N4_recirculation_loop'] | ['increase_recycle_ratio', 'extend_loop_retention', 'hold_for_slow_evidence'] |
| `F4_polishing_release_agent` | 末端精处理、暂存验证与放行阻断 | [] | ['route_to_polishing', 'block_release_until_lab', 'conditional_release_after_gate'] |

## Joint Actions

| Rank | Joint Action | Score | R3b Penalty | R3b Bonus | Intent |
| --- | --- | --- | ---: | ---: | --- |
| `1` | `J4_safe_low_cost_standby` | `0.616` | `0.0` | `0.045` | 观测不足或策略不确定时选择低成本暂存与放行阻断。 |
| `2` | `J3_polishing_and_release_gate` | `0.582` | `0.0` | `0.04` | 末端风险不清时进入精处理与慢证据门控，不允许仅凭 synthetic 软传感放行。 |
| `3` | `J1_reaction_completion_recovery` | `0.52` | `0.0` | `0.0` | 反应不足时同步调药和延长停留时间，而不是只提高单一药剂。 |
| `4` | `J0_matrix_shock_equalize_and_recycle` | `0.401` | `0.14` | `0.0` | 基质冲击先削峰再回流，避免反应核心被瞬时负荷推入不可解释区。 |
| `5` | `J2_catalyst_protection_before_regeneration` | `0.185` | `0.16` | `0.0` | 催化剂状态不清时先保护负荷，再决定再生、切换或更换。 |

## R3b Control Replay Guardrails

- patch_id：`R3_counterfactual_guardrail_reward_prior`
- guardrail_candidate_accuracy：`1.0`
- field_replay_coverage：`0.0`
- catalyst_proxy_summary_status：`field_proxy_holdout_coverage_gaps`
- catalyst_proxy_scoreable_batch_count：`0`
- catalyst_guardrail_mode：`agent51_holdout_coverage_gaps_keep_catalyst_guardrail`
- pressure_headloss_candidate_ids：`['N3_catalyst_bed:pressure_drop_kPa', 'N3_catalyst_bed:headloss_kPa_per_m', 'N3_catalyst_bed:flow_normalized_pressure_residual']`
- pressure_headloss_control_boundary：pressure/headloss may shape hydraulic and catalyst-state explanation priors, but cannot relax recycle/catalyst guardrails or promote actuator use without field topology, matched lab labels and missingness replay.
- 边界：R3b reward prior guardrails can change synthetic reward ranking and explanation rules only; field replay is required before actuator or release-gate promotion.

## Decision Tree Distillation

- `R1_matrix_shock_protective_loop`：IF matrix_interference_observability >= 0.70 and control_latency_gain >= 0.70 THEN `J0_matrix_shock_equalize_and_recycle`；发现基质冲击时优先均质暂存和回流削峰。
- `R2_reaction_completion_recovery`：IF reaction_completion_observability >= 0.65 and oxidant_observability >= 0.65 THEN `J1_reaction_completion_recovery`；反应不足且氧化剂状态可观测时联动调药和延长停留。
- `R3_catalyst_uncertainty_block`：IF catalyst_activity_observability < 0.55 THEN `J2_catalyst_protection_before_regeneration with human_review`；催化剂状态不可观测时先保护负荷，不自动再生或切换。
- `R4_release_gate_block`：IF field_replay_evidence < 0.85 or soft_sensor field holdout not passed THEN `J3_polishing_and_release_gate`；放行必须等待现场证据门，不能由 synthetic 策略直接决定。
- `R3G1_catalyst_uncertain_requires_standby_or_human_review`：IF catalyst proxy labels are not field validated and catalyst action would protect/regenerate THEN `prefer J4_safe_low_cost_standby or require human-reviewed catalyst protection`；R3 反事实压力测试发现催化剂低代理证据会触发保护性误动作，先暂存和阻断放行。
- `R3G2_hydraulic_delay_unknown_blocks_recycle`：IF tank storage margin or actuator latency evidence is missing and recycle escalation is proposed THEN `prefer J3_polishing_and_release_gate`；水力延迟和执行证据不足时，不把回流升级当成默认安全动作。
- `R8C_pressure_headloss_candidate_boundary`：IF pressure/headloss candidate exists but field topology, matched lab labels or missingness replay are incomplete THEN `use as explanation prior only; do not relax hydraulic delay or catalyst guardrails`；压降/水头损失可帮助解释床层堵塞、催化剂衰减和水力异常，但现场证据前不能推动回流升级、再生或执行器动作。

## 结论

- 把单处理链闭环升级为“多设施 agent 协同”：均质池、反应核心、催化剂床、回流环和末端精处理分别提出局部动作，再由联合奖励函数仲裁。
- 把 Agent48 的 node-modality 稀疏观测矩阵作为协同控制的状态入口，缺节点或缺模态时用 missingness mask 显式进入策略。
- 用决策树蒸馏把多 agent 策略转成现场可审查规则，所有规则都必须保留人工复核和禁止自动放行边界。
- 下一步应采集真实多节点 sensor/lab/operation/action replay，形成共享经验池，再验证 joint_action_accuracy、reward_regret 和误动作成本。
- Agent49 可消费 Agent51/R2 的催化剂弱轴修复先验更新状态向量，但 field proxy labels 前必须保留催化剂不确定性保护。
- Agent49 已消费 pressure/headloss 候选合同；下一步需要用 site topology、bed geometry、压降时序、lab label 和操作日志做 field replay，否则只能作为解释先验和 guardrail 边界。
- 决策树代理当前只能解释策略，不能替代协同控制器；需要 field replay 上准确度达到 0.90 后再进入执行器候选。
- R3b 已把反事实压力测试中的 R3G1/R3G2 接入 Agent49 reward prior；下一步需要 Agent52 用 guardrail-aware replay 复核 regret 和误保护成本。
- Agent49 已接入 Agent51 field holdout summary；若 scoreable batch 不足或 MAE/相关性未过线，J2 催化剂保护/再生仍要转入暂存或人工复核。
- P7 后续必须把工程执行约束补丁持续接入 reward，包括池容、泵阀延迟、药剂库存、维护窗口和人工复核排队。
# 当前问题优先级排序

- self_interrupt_verdict：`stage_boundary_wait_for_external_activation`
- self_interrupt_reason：当前不是硬中断，也不是继续内部扩张；量化阶段门已进入外部激活等待，只允许提交真实外部证据包或定义新的可测试核心接口。
- governance_review_gate：`continue_current_micro_loop`
- recommended_next_core_action：`FIELD_ACTIVATION_RESPONSE_FOCUS_HANDOFF_NEXT_ACTION`

| Rank | Task | Score | 下一步实验 | 指标 | 失败边界 |
| --- | --- | --- | --- | --- | --- |
| 1 | `P4_minimal_grey_box_physics` 灰箱物理机制最小增强 | `0.78` | Agent53 的 synthetic grey-box physics prior 已形成；无 field 物理校准时，下一轮优先转向 P5 软传感 node-modality/missingness 耦合。 | mass_balance_residual, residence_time_error, grey_box_residual, byproduct_risk_flag | 参数未由现场或文献范围校准前只能作为先验约束，不可当作实证机理。 |
| 2 | `P10_claim_specific_field_package_and_source_basis` 把对齐后的验证需求升级成 claim-specific 现场采集包和 source_basis 补全任务 | `0.756` | P10 的采集包矩阵已形成；下一轮优先补 source_basis 细节或导入真实 field package。 | claim_specific_required_field_coverage, source_basis_completion_rate, minimal_field_package_pass_rate, field_claim_upgrade_blocker_count | 没有真实 field 数据时只能形成采集包和证据补全任务，不能升级为现场结论。 |
| 3 | `P8_cross_agent_core_reconnection` 把 KG/灰箱/布点/工程补丁接回主闭环链条 | `0.747` | Agent57 已完成 synthetic 主链回接审计；下一轮优先把 field_validation_queue 对齐到真实数据接口。 | main_chain_prior_consumption_rate, kg_path_to_action_link_rate, grey_box_prior_used_by_soft_sensor, engineering_patch_used_by_arbitration | 这是模型链路联动改造，不能替代 field validation；只允许改变先验、解释和候选排序。 |
| 4 | `P6_reasonable_knowledge_graph_upgrade` 知识库升级为可推理 KG | `0.743` | Agent56 的 KG reasoning baseline 已形成；下一轮优先处理跨 agent 主链回接，同时等待 field-supported KG edges。 | field_supported_edge_ratio, evidence_traceability, constraint_hit_rate, claim_verification_pass_rate | KG 能约束假设和解释路径，但没有现场标签时不能证明控制效果。 |
| 5 | `P9_field_validation_queue_alignment` 把 KG field_validation_queue 对齐到真实数据接口与回放门控 | `0.741` | P9 的接口对齐基线已形成；下一轮优先把 claim-specific 字段提升为最小现场采集包和 source_basis 补全任务。 | field_need_to_table_coverage, field_need_to_gate_coverage, unmapped_validation_need_count, claim_upgrade_blocker_count | 这只是验证接口对齐；没有真实 field 包仍不能证明模型现场有效。 |
| 6 | `P7_engineering_constraints_in_reward_and_arbitration` 工程执行约束进入 reward 和仲裁 | `0.737` | Agent55 的 synthetic engineering reward/arbitration patch 已形成；无现场执行 replay 时，下一轮优先转向 P6 可推理 KG 或等待工程执行日志。 | actuator_switch_count, storage_violation_rate, energy_cost_index, human_review_rate | 无 PLC/SCADA 点表和设备约束时只能做候选动作过滤，不能做现场执行计划。 |
| 7 | `P3_agent49_replay_ready_offline_evaluation` Agent49 多设施协同控制升级到 replay-ready 离线评估 | `0.69` | P3 已被 R3 反事实压力测试消费；不要重复 synthetic replay，等待 field replay 或执行 R3b/R3c 之后的复核链。 | joint_action_accuracy, reward_regret, distilled_policy_accuracy, field_replay_coverage | synthetic policy 不能替代现场策略；无 replay 时不能写入执行器或 release gate。 |
| 8 | `P2_catalyst_activity_weak_observability_proxy` catalyst_activity 弱观测增强 | `0.677` | P2 已被 R2 观测契约消费；下一步不是继续堆代理变量，而是等待 catalyst_activity/proxy holdout labels 或转向控制 replay。 | catalyst_activity_observability, weak_state_coverage, policy_block_rate, field_label_need | 没有催化剂活性、再生、压降和离线标签时只能证明代理变量设计合理，不能证明催化剂真实衰减。 |
| 9 | `P1_agent48_comparable_sparse_sensor_placement` Agent48 稀疏感知从启发式升级为可比较布点优化 | `0.668` | P1 已被 R2 观测契约消费；内部不要重复做布点启发式，下一步只在真实 topology/installability 数据进入后刷新。 | state_observability, reconstruction_gain, weak_state_coverage, total_cost_index | 无真实拓扑、水力停留时间和维护可达性时只能作为 synthetic topology prior。 |
| 10 | `P5_soft_sensor_node_modality_missingness` 软传感与 node-modality/missingness 矩阵耦合 | `0.662` | P5 已被 R2 观测契约消费；不要重复补矩阵字段，除非导入 field missingness replay。 | masked_mae, interval_coverage, missingness_robustness, latency_aware_error | 缺测机制若来自 synthetic dropout，不能外推为真实传感器污染、漂移或通信失败。 |
| 11 | `P11_source_basis_detail_or_real_field_package_import` 补 source_basis 细节或导入真实 field package 进入证据链 | `0.61` | 停止内部补 source_basis/citation；若用户提供 data_origin=field 的真实包，则运行 R7/Agent44->42->43->45。若没有真实包，把 P11 放入 external blocker backlog，并转向 Agent60/R2/R3 指向的内部模型链路。 | citation_detail_completion_rate, source_basis_parameter_boundary_coverage, field_replay_import_pass, evidence_chain_pass | 这是外部 field package 等待态；不能用 synthetic/template 代替真实包，不能升级 field-supported claim，不能写 actuator 或 release gate。 |
| 12 | `L1_ppt_word_showcase_polish` PPT、Word、索引和展示材料美化 | `0.11` | 不作为当前核心实验；仅在模型指标更新后同步表达层。 | none_for_model_core | 不会提升观测、推理、控制或验证能力，必须进入低优先级 backlog。 |

## 阻塞项

- Agent51 catalyst_activity proxy is only a synthetic design baseline; field_proxy_holdout labels are still required before relaxing Agent49 catalyst uncertainty blocks.
- Agent52 multi-facility replay evaluation is only a synthetic baseline; field multi-node state-action-reward replay is still required before promoting Agent49.
- Agent53 minimal grey-box physics is only a synthetic prior; field RTD, inlet/outlet pollutant, oxidant residual, catalyst history and byproduct labels are still required.
- Agent54 soft sensor matrix coupling is only a synthetic layout contract; field node-specific values, layout holdout splits and missingness replay are still required.
- Agent55 engineering execution constraints are only a synthetic reward/arbitration patch; PLC/SCADA point list, SOP and field execution replay are required before actuator writeback.
- Agent56 knowledge graph reasoning is only a literature/synthetic reasoning patch; field-supported KG edges and source-basis completion are required before field mechanism claims.
- Agent57 main-chain reconnection is only a synthetic consumption audit; field replay and validation queue alignment are still required before field claims or actuator writeback.
- Agent58 field validation queue alignment maps needs to tables/gates, but real field packages, claim-specific required fields and source_basis completion are still required before upgrading claims.
- Agent59/unified evidence gate show source_basis detail and schema are ready; P11 is now an external real-field-package blocker, so internal work should move to the next non-field-fabricating model task until data_origin=field package is imported.
- R8u66 field path/endpoint label package is not ready; field layout holdout, hydraulic path-stage validation and final-effluent release evidence still require node-specific path labels, endpoint labels, operation logs and offline lab rows.
- R8u79 formal search execution route plan is ready, but it is only an external/human search execution handoff; a reviewer-filled FORMAL_SEARCH_RESULT_PACKAGE_PATH is still required before nonlegal comparison review, formal counsel review or patent-grade claim refinement.
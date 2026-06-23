# 模型架构复盘与减冗治理

## 核心判断

当前系统已经不适合继续按 agent 编号线性理解。更高价值的做法是把 60 个历史 agent 压缩到少数核心模块，并检查每个模块是否真正提升观测、推理、控制、验证或工程可执行性。
Agent60 只作为本轮复盘治理工具存在，不计入原有模型能力链。

- 已映射 Agent：60/60
- 模块数：9
- 七层系统骨架覆盖率：1.0
- 六类系统能力覆盖率：1.0
- 模块接口契约覆盖率：1.0
- 核心锚点覆盖率：1.0
- 冗余/合并簇数：5
- 展示层冻结数：3

## 全局七层系统骨架映射

| 层级 | 模块 | 能力 | 状态 |
| --- | --- | --- | --- |
| L1_field_object_layer 现场对象层 | M1_sparse_observation_layout, M5_kg_claim_evidence, M7_project_operations_support | controllability, engineering_feasibility, explainability, observability, verifiability | covered |
| L2_observation_layer 观测层 | M1_sparse_observation_layout, M2_soft_sensor_state_estimation, M6_field_evidence_chain | engineering_feasibility, observability, verifiability | covered |
| L3_state_estimation_layer 状态估计层 | M1_sparse_observation_layout, M2_soft_sensor_state_estimation, M3_grey_box_mechanism | engineering_feasibility, explainability, observability, verifiability | covered |
| L4_mechanism_evidence_layer 机理证据层 | M3_grey_box_mechanism, M5_kg_claim_evidence | explainability, verifiability | covered |
| L5_diagnostic_decision_layer 诊断决策层 | M3_grey_box_mechanism, M4_collaborative_control, M6_field_evidence_chain | controllability, engineering_feasibility, explainability, verifiability | covered |
| L6_closed_loop_execution_layer 闭环执行层 | M4_collaborative_control, M7_project_operations_support | controllability, engineering_feasibility, explainability, verifiability | covered |
| L7_validation_governance_layer 验证治理层 | M2_soft_sensor_state_estimation, M4_collaborative_control, M5_kg_claim_evidence, M6_field_evidence_chain, M7_project_operations_support, M8_model_governance | controllability, engineering_feasibility, evolvability, explainability, observability, verifiability | covered |

## 模块接口契约矩阵

这一部分对应全局 goal 中“先定义接口，再扩展功能”的原则。它检查每个模块是否具备输入、输出、状态变量、证据来源、可传递指标、不能做什么、上下游依赖和现场验证需求，而不是只保留一个抽象名称。

| 模块 | 关键状态变量 | 可传递指标 | 上游依赖 | 下游消费者 | 不能做 |
| --- | --- | --- | --- | --- | --- |
| M1_sparse_observation_layout 低成本稀疏感知与布点 | observable_nodes, modalities, weak_state_coverage, cost_index, topology_prior | weak_state_coverage, soft_sensor_reconstruction_gain, total_cost_index, single_point_dependency | field_object_definition, sensor_cost_catalog, site_topology_or_bed_geometry | M2_soft_sensor_state_estimation, M4_collaborative_control, M6_field_evidence_chain | 不能仅靠加点位宣称现场可观测；无真实拓扑/标签时不能作为部署结论。 |
| M2_soft_sensor_state_estimation 软传感、缺测矩阵与不确定性 | pollutant_residual, reaction_completion, matrix_interference, catalyst_activity, uncertainty_interval | masked_mae, interval_coverage, missingness_robustness_score, field_holdout_gate_pass | M1_sparse_observation_layout, M3_grey_box_mechanism, offline_lab_results | M3_grey_box_mechanism, M4_collaborative_control, M6_field_evidence_chain | 不能把 synthetic dropout 或模板 holdout 写成现场缺测鲁棒性结论。 |
| M3_grey_box_mechanism 灰箱物理、机理解释与故障诊断 | k_eff, mass_balance_residual, hydraulic_delay, catalyst_decay, byproduct_risk | grey_box_residual, mass_balance_residual, mechanism_hypothesis_count, fault_mode_coverage | M2_soft_sensor_state_estimation, M5_kg_claim_evidence, field RTD and lab panels | M4_collaborative_control, M5_kg_claim_evidence, M6_field_evidence_chain | 不能把未校准灰箱参数当成现场机理结论或放行依据。 |
| M4_collaborative_control 循环式处理、多设施协同控制与仲裁 | facility_state, joint_action, reward_components, guardrail_context, operator_review_required | joint_action_accuracy, reward_regret, distilled_policy_accuracy, false_positive_cost | M2_soft_sensor_state_estimation, M3_grey_box_mechanism, M6_field_evidence_chain | M6_field_evidence_chain, M7_project_operations_support | 无真实多节点 replay 和人工复核门时不能写执行器或 release gate。 |
| M5_kg_claim_evidence 知识图谱、文献证据与 Claim 审查 | evidence_edge, claim_status, source_basis_detail, constraint_hit, field_supported_edge | evidence_traceability, constraint_hit_rate, source_basis_completion_rate, field_supported_edge_ratio | field object taxonomy, literature evidence matrix, M3_grey_box_mechanism | M3_grey_box_mechanism, M4_collaborative_control, M6_field_evidence_chain | 不能把文献依据或 KG 推理当成现场支持结论。 |
| M6_field_evidence_chain 现场数据接口、Replay 与证据门控 | field_import_pass, evidence_chain_pass, claim_gate_status, replay_contract_status, field_supported_claim | field_replay_import_pass, field_need_to_gate_coverage, evidence_chain_pass, can_write_to_release_gate | M1_sparse_observation_layout, M2_soft_sensor_state_estimation, M4_collaborative_control, M5_kg_claim_evidence | M4_collaborative_control, M8_model_governance | 不能把 header-only/template package 或 synthetic replay 当成 field evidence。 |
| M7_project_operations_support 项目运行、资源调度与实施管理 | campaign_queue, resource_capacity, replan_trigger, recovery_load_fraction, deployment_budget | campaign_success_rate, resource_bottleneck_count, replan_trigger, recovery_load_fraction | M4_collaborative_control, M6_field_evidence_chain, site operations records | M8_model_governance, implementation planning | 不能压过模型核心链路，也不能替代状态估计、控制 replay 或 field claim gate。 |
| M8_model_governance 模型治理、主链回接与减冗复盘 | system_spine_status, interface_contract_coverage, consolidation_score, self_interrupt_verdict, fallback_action | main_chain_prior_consumption_rate, mapped_agent_count, redundancy_cluster_count, system_spine_coverage | all core modules, global goal, test/regression outputs | all module owners, future refactor work | 治理层不能替代模型能力、现场验证或执行器授权。 |
| M9_presentation_delivery 展示、文档与汇报材料 | deliverable_status, artifact_index_status | artifact_availability | M8_model_governance, validated model outputs | human presentation only | 不能改变模型结论，不能制造 field-supported claim，不能作为核心优化中心。 |

## 专利级技术特征 Ledger

这部分不是把项目转成专利文本，而是用专利交底的严谨度反向检查模型：每个核心特征必须说清技术问题、技术手段、状态变量、控制动作、验证指标、技术效果、现有技术区别和失败边界。

- 状态：`technical_feature_ledger_ready_as_disclosure_scaffold_not_field_claim`
- 技术特征覆盖率：1.0
- 机器可读 ledger：`outputs/agent_architecture_consolidation/patent_technical_feature_ledger.json`
- 现场 claim 升级边界：该 ledger 只证明技术方案骨架更清楚；任何现场成立 claim 仍必须通过 R7/R8p/R8v、field holdout、operator review 和 release gate。

| 特征 | 模块 | 技术手段 | 技术效果 | 现有技术区别 | Claim 骨架角色 |
| --- | --- | --- | --- | --- | --- |
| PTF1_node_modality_sparse_sensing | M1_sparse_observation_layout | 构建 node-modality 稀疏感知矩阵，把节点、传感模态、安装成本、缺测风险和隐藏状态覆盖统一评分。 | 用有限传感预算提升关键隐藏状态可估计性，并把不能观测的轴显式转入补证据队列。 | 区别于只按经验选点或只建黑箱预测模型，本特征把布点、隐藏状态覆盖和后续软传感/控制接口绑定。 | 主权利要求中的稀疏感知输入构建步骤；可作为 node-modality 布点从属特征。 |
| PTF2_soft_sensor_grey_state_estimation | M2_soft_sensor_state_estimation | 以稀疏传感矩阵、缺测 mask、时间延迟、灰箱先验和离线标签训练软传感器，并输出不确定性和 abstention 标志。 | 把不可直接观测的黑箱状态转成可审查的灰箱估计，同时防止低置信估计直接驱动放行。 | 区别于只输出点预测的 ML 软测量，本特征把缺测、低频、灰箱先验、不确定性和 release gate 绑定。 | 主权利要求中的隐藏状态估计步骤；可作为软传感/不确定性从属特征。 |
| PTF3_grey_box_mechanism_boundary | M3_grey_box_mechanism | 引入反应动力学、质量守恒、水力延迟、催化剂衰减、基质抑制和副产物风险等灰箱边界。 | 让控制动作能够回到反应、水力和催化剂机制，而不是只依赖黑箱分数。 | 区别于纯机器学习过程模拟，本特征把机制残差、故障边界和控制动作候选联动。 | 主权利要求中的灰箱机理约束步骤；可作为催化剂活性/水力延迟从属特征。 |
| PTF4_cyclic_low_frequency_control | M4_collaborative_control | 利用循环、暂存、延长停留和多设施协同控制，为软传感、诊断和人工复核争取时间窗口。 | 通过循环窗口降低对高速昂贵传感器的依赖，并把控制动作变成可回退、可解释的工程动作。 | 区别于实时高频全量传感控制，本特征把低频感知约束与循环式处理结构协同设计。 | 主权利要求中的闭环控制步骤；可作为低频传感-循环窗口协同控制从属特征。 |
| PTF5_mechanism_kg_evidence_constraint | M5_kg_claim_evidence | 构建 typed KG 和 source_basis，把污染物、材料、过程条件、低成本信号、隐藏状态、动作和风险连接为证据路径。 | 让多智能体诊断和控制动作具有证据路径，减少无依据扩展。 | 区别于只堆论文摘要，本特征把 KG 证据转成可传递控制约束和现场验证字段。 | 从属权利要求中的机理证据约束与 claim gate 特征。 |
| PTF6_field_replay_release_gate | M6_field_evidence_chain | 建立 field package、timestamped replay、holdout、operator review、calibration 和 release gate 的分级证据链。 | 把证据等级从 synthetic/template/literature/field/operator-reviewed/release-gated 明确分层，降低误放行风险。 | 区别于只报告模型精度，本特征把现场证据升级路径和保护性写回边界作为系统组成。 | 主权利要求中的验证治理与保护性控制写回步骤；也可形成现场 replay 分案。 |
| PTF7_engineering_execution_constraints | M7_project_operations_support | 把资源、成本、执行延迟、恢复爬坡和 SOP 约束作为控制 reward、仲裁和实施计划的硬边界。 | 提高控制候选的工程可执行性，避免算法策略与现场执行条件脱节。 | 区别于只优化水质目标，本特征把现场执行约束纳入控制候选生成与仲裁。 | 从属权利要求中的工程执行约束和实施支持特征。 |
| PTF8_stage_gated_model_governance | M8_model_governance | 采用七层系统骨架、接口契约、冗余簇、fallback 和阶段门控，审查每个新增能力是否回接主链。 | 让系统演化更短、更稳、更可审查，减少无效 agent 扩张。 | 区别于单次 agent 编排，本特征把证据边界、接口契约和阶段门控作为长期演化机制。 | 可作为系统治理或计算机实现方法的支撑特征，不单独替代水处理核心。 |

## 技术方案 Claim Skeleton Scaffold

这部分把技术特征组合成“主方法/系统 + 从属或分案方向”的技术骨架。它不是法律权利要求文本，也不是授权判断；作用是检查系统主链是否已经能被清楚拆成可实施、可验证、可对比的技术方案。

- 状态：`technical_claim_skeleton_ready_as_scaffold_not_legal_claim_not_field_claim`
- Claim scaffold 覆盖率：1.0
- 机器可读 scaffold：`outputs/agent_architecture_consolidation/technical_claim_skeleton_scaffold.json`
- 现场 claim 升级边界：该 scaffold 只把技术方案组合成方法/系统/从属方向骨架；任何现场成立 claim 或执行器写回仍必须通过 R7/R8p/R8v、field holdout、operator review 和 release gate。

| Scaffold | 类型 | 映射特征 | 技术效果 | 现有技术区别 |
| --- | --- | --- | --- | --- |
| TCS1_independent_method_low_cost_sparse_cyclic_greybox_control | independent_method_scaffold | PTF1_node_modality_sparse_sensing, PTF2_soft_sensor_grey_state_estimation, PTF3_grey_box_mechanism_boundary, PTF4_cyclic_low_frequency_control, PTF5_mechanism_kg_evidence_constraint, PTF6_field_replay_release_gate | 在不依赖高成本高频全量传感的情况下，让黑箱过程具备可估计、可解释、可回放验证和可保护执行的闭环能力。 | 区别于单纯软测量、单点控制或经验回流，本方案把稀疏观测、循环争取时间、灰箱估计、机理证据和证据门控组合为一条不可绕过的控制链。 |
| TCS2_independent_system_architecture | independent_system_scaffold | PTF1_node_modality_sparse_sensing, PTF2_soft_sensor_grey_state_estimation, PTF3_grey_box_mechanism_boundary, PTF4_cyclic_low_frequency_control, PTF5_mechanism_kg_evidence_constraint, PTF6_field_replay_release_gate, PTF7_engineering_execution_constraints, PTF8_stage_gated_model_governance | 让系统结构、接口、状态变量、控制动作和证据门形成可审查架构，减少 agent 堆叠和证据边界漂移。 | 区别于一次性多智能体流程，本系统把模型能力、证据门和工程执行约束组织为长期演化的七层闭环架构。 |
| TCS3_dependent_catalyst_activity_regeneration_control | dependent_or_divisional_scaffold | PTF1_node_modality_sparse_sensing, PTF2_soft_sensor_grey_state_estimation, PTF3_grey_box_mechanism_boundary, PTF4_cyclic_low_frequency_control, PTF6_field_replay_release_gate | 在低成本条件下提升催化剂活性可观测性，并避免未验证代理信号直接解除保护。 | 区别于只按运行周期更换催化剂，本方向把代理观测、软传感和证据门控联动到再生/更换控制。 |
| TCS4_dependent_node_modality_sparse_hidden_state_estimation | dependent_or_divisional_scaffold | PTF1_node_modality_sparse_sensing, PTF2_soft_sensor_grey_state_estimation | 让传感布点直接服务隐藏状态估计，而不是只优化传感器数量或单点精度。 | 区别于普通稀疏传感器布设，本方向把布点矩阵与软传感隐藏状态和证据门绑定。 |
| TCS5_dependent_field_replay_protective_writeback | dependent_or_divisional_scaffold | PTF4_cyclic_low_frequency_control, PTF6_field_replay_release_gate, PTF8_stage_gated_model_governance | 减少把 synthetic/template 误当现场证据造成的误放行和误执行。 | 区别于只离线评估控制精度，本方向把现场 replay 证据链作为执行器写回前置条件。 |
| TCS6_dependent_low_frequency_cycle_window_control | dependent_or_divisional_scaffold | PTF2_soft_sensor_grey_state_estimation, PTF4_cyclic_low_frequency_control, PTF7_engineering_execution_constraints | 用循环结构换取观测和诊断时间，降低对高速昂贵传感器的依赖。 | 区别于高频实时控制，本方向把慢传感约束和循环处理结构作为同一控制问题处理。 |
| TCS7_dependent_greybox_multi_agent_safety_arbitration | dependent_or_divisional_scaffold | PTF3_grey_box_mechanism_boundary, PTF4_cyclic_low_frequency_control, PTF5_mechanism_kg_evidence_constraint, PTF7_engineering_execution_constraints, PTF8_stage_gated_model_governance | 让多智能体输出受机理证据和工程安全边界约束，降低冲突动作和过度自动化风险。 | 区别于黑箱 MARL 或简单投票，本方向要求每个动作可追溯到状态、机理证据、工程约束和验证门。 |

## 技术实施例与验证矩阵

这部分把 claim skeleton 落成实施例、所需数据包、验证门和验收指标。它仍然只是实施例 scaffold；没有真实 field package、replay、holdout 和 operator review 时，不能生成现场结论。

- 状态：`technical_embodiment_matrix_ready_not_field_evidence`
- 实施例覆盖率：1.0
- 机器可读矩阵：`outputs/agent_architecture_consolidation/technical_embodiment_validation_matrix.json`
- 证据边界：该矩阵只定义实施例与验证门；没有真实 field package、replay、holdout 和 operator review 时，不能生成 field evidence、不能写执行器、不能写 release gate。

| 实施例 | 场景 | 技术效果待测量项 | 当前证据状态 |
| --- | --- | --- | --- |
| TE1_end_to_end_low_cost_cyclic_greybox_control | 某污染批次进入均质池、反应核心、催化剂床、回流环和末端精处理单元，现场只允许少量低成本传感和离线验证。 | 验证低成本稀疏传感与循环窗口是否能在不误放行的前提下提升隐藏状态可估计性和控制可执行性。 | scaffold_only_waiting_for_field_package |
| TE2_pressure_resolution_route_package_validation | node_modality_sensor_timeseries 与 pressure_headloss_event_log 对同一 batch 的压降证据冲突，需要 operator review 和 route work package 后才能进入 R8p/R8v。 | 验证压力源冲突不会被静默平均或越过人工复核，并能被转化为可修补、可装配、可回放的现场行包路径。 | blocked_waiting_for_R7_TO_R8P_WORK_PACKAGE_DIR |
| TE3_catalyst_activity_proxy_regeneration | 催化剂床活性不可直接低成本测量，需要通过 UV254、ORP、压降、再生事件和离线标签形成代理证据。 | 验证低成本代理能否提高催化剂活性可观测性，并避免未验证代理解除保护。 | design_prior_and_schema_ready_waiting_for_field_proxy_holdout |
| TE4_node_modality_sparse_hidden_state_layout | 在预算受限的处理单元和管网节点上选择传感器组合，使 pollutant_residual、reaction_completion、catalyst_activity 等隐藏状态具备最低可估计性。 | 验证传感布点是否真正提升隐藏状态可估计性，而不是只增加传感器数量。 | synthetic_design_prior_waiting_for_field_topology_and_labels |
| TE5_low_frequency_cycle_window_control | 低成本传感和离线检测慢于反应/放行决策，需要用回流、暂存和延长停留时间换取验证窗口。 | 验证循环结构是否能降低对高频昂贵传感器的依赖，并降低误放行风险。 | synthetic_latency_replay_waiting_for_timestamped_field_campaign |
| TE6_greybox_multi_agent_safety_arbitration | 多个 agent 对同一污染批次提出回流、投药、切换、催化剂保护或放行候选，需要以机理证据、工程约束和证据等级仲裁。 | 验证多智能体输出是否能被灰箱机理和工程安全边界约束，而不是靠黑箱投票或 MARL 直接执行。 | synthetic_counterfactual_replay_waiting_for_field_state_action_reward_replay |

## 技术效果度量矩阵

这部分把实施例中的“效果”继续压成可度量合同：相对什么基线、看哪些指标、需要什么阈值、通过哪个 gate、失败时如何保持阻断。它的作用是让后续 field package 到来后能直接验收，而不是提前宣称现场成立。

- 状态：`technical_effect_measurement_matrix_ready_not_field_evidence`
- 技术效果覆盖率：1.0
- 机器可读矩阵：`outputs/agent_architecture_consolidation/technical_effect_measurement_matrix.json`
- 证据边界：该矩阵只把技术效果转成基线、指标、阈值和验证门；没有真实 field package、replay、holdout、operator review 和 release gate 时，不能把任何效果写成现场成立结论。

| 技术效果 | 关联实施例 | 基线对照 | 核心指标 | 当前证据状态 |
| --- | --- | --- | --- | --- |
| TEM1_observability_gain_under_sparse_sensing | TE4_node_modality_sparse_hidden_state_layout | 进水一个、出水一个的低成本规则布点，或不考虑节点-模态矩阵的 cost-only 贪心布点。 | weak_state_coverage, selected_matrix_rank, condition_number_proxy, single_point_dependency, missingness_robustness_score | synthetic_design_prior_waiting_for_field_topology_and_labels |
| TEM2_blackbox_to_greybox_state_estimation | TE1_end_to_end_low_cost_cyclic_greybox_control, TE4_node_modality_sparse_hidden_state_layout | 仅用出水阈值、单点经验规则或不带灰箱先验的纯黑箱回归模型。 | masked_mae, interval_coverage, field_holdout_gate_pass, grey_box_residual, abstention_or_ood_rate | interface_and_synthetic_holdout_ready_waiting_for_field_holdout |
| TEM3_low_frequency_cycle_window_reduces_fast_sensor_need | TE5_low_frequency_cycle_window_control | 一次通过式处理或假设传感/检测即时返回的闭环控制。 | latency_violation_rate, hold_time_min, storage_margin, false_positive_cost, release_block_correctness | synthetic_latency_replay_waiting_for_timestamped_field_campaign |
| TEM4_catalyst_proxy_guardrail_effect | TE3_catalyst_activity_proxy_regeneration | 只按运行时长、处理批次数或人工经验判断催化剂再生/更换。 | scoreable_batch_count, proxy_label_correlation, holdout_mae, pressure_source_conflict_count, catalyst_guardrail_mode | design_prior_and_schema_ready_waiting_for_field_proxy_holdout |
| TEM5_field_replay_protective_writeback_reduces_false_release | TE1_end_to_end_low_cost_cyclic_greybox_control, TE2_pressure_resolution_route_package_validation, TE5_low_frequency_cycle_window_control | 直接使用 synthetic replay、静默平均冲突压力源或跳过人工复核的自动放行流程。 | evidence_chain_pass, pressure_source_conflict_requires_operator_review, can_write_to_release_gate, release_block_correctness, field_scenario_coverage | blocked_waiting_for_R7_TO_R8P_WORK_PACKAGE_DIR |
| TEM6_greybox_multi_agent_arbitration_reduces_conflict_actions | TE6_greybox_multi_agent_safety_arbitration | 简单多数投票、单 agent 规则或未受机理证据约束的黑箱 MARL 策略。 | joint_action_accuracy, reward_regret, constraint_hit_rate, false_positive_cost, operator_review_required | synthetic_counterfactual_replay_waiting_for_field_state_action_reward_replay |
| TEM7_engineering_execution_constraint_feasibility | TE1_end_to_end_low_cost_cyclic_greybox_control, TE5_low_frequency_cycle_window_control, TE6_greybox_multi_agent_safety_arbitration | 不考虑执行器延迟、资源库存、人工复核窗口和安全 SOP 的纯算法动作排序。 | execution_constraint_violation_count, actuator_latency_violation_count, storage_or_reagent_bottleneck_count, operator_review_sla_violation_count, blocked_action_count | engineering_constraint_contract_ready_waiting_for_actuator_feedback |

## 现有技术区别与保护性风险矩阵

这部分把潜在 claim、技术特征和技术效果映射到已有方法族，检查项目的区别点是否足够具体。它不是正式专利检索，也不是法律意见；作用是提前暴露“只是普通 AI/软传感/多智能体”的风险，并给出从属回退方向。

- 状态：`prior_art_distinction_matrix_ready_as_hypothesis_not_search_or_legal_opinion`
- 区别矩阵覆盖率：1.0
- 机器可读矩阵：`outputs/agent_architecture_consolidation/prior_art_distinction_matrix.json`
- 证据边界：该矩阵只把已有技术家族与本项目候选区别点映射成检索/交底假设；没有正式 prior-art search、法律审查和 field validation 时，不能声称新颖性、创造性或授权可能性。

| 区别项 | 已知方法族 | 区别组合 | 风险等级 | 正式检索需求 |
| --- | --- | --- | --- | --- |
| PAD1_soft_sensor_ml_vs_cyclic_greybox_release_gated_control | wastewater soft sensors, data-driven process monitoring and sensor-limited control | 低成本 node-modality 稀疏观测 + 软传感不确定性 + 灰箱边界 + 回流/暂存争取时间 + field replay/release gate 的组合。 | medium | formal patent/prior-art search, field holdout, timestamped replay, release gate audit |
| PAD2_sparse_sensor_placement_vs_node_modality_hidden_state_layout | sparse sensor placement for reconstruction or classification | 把传感位置扩展为 node-modality 矩阵，并把覆盖目标从一般重构转成 pollutant_residual、reaction_completion、catalyst_activity 等隐藏状态及下游控制可用性。 | medium_high | field topology, node-specific time series, offline weak-state labels, missingness replay |
| PAD3_marl_pump_coordination_vs_greybox_multi_agent_safety_arbitration | multi-agent reinforcement learning, pump-station coordination and policy distillation | 本项目把多 agent 输出限制在灰箱机理、KG 证据、工程执行约束、operator review 和 field replay 之内，不允许黑箱策略直接写执行器。 | medium | field state-action-reward replay, operator review labels, engineering constraint replay |
| PAD4_flowsheet_optimization_vs_low_cost_observation_gated_greybox_control | water treatment flowsheet modeling, unit-model optimization, TEA/LCA and process constraints | 本项目不是先假设完整高保真参数，而是在低成本观测不足时用软传感和循环窗口形成可校准灰箱，再由 replay/field gate 限制控制动作。 | medium | field calibration, RTD/HRT evidence, actuator feedback, timestamped replay |
| PAD5_scientific_kg_vs_action_constraint_and_claim_gate | scientific knowledge graphs, literature evidence matrices and research-agent claim verification | 本项目把 KG/source_basis 作为控制候选约束、claim gate 和 field validation queue，而不是只做文献摘要或解释文本。 | medium_high | citation-level source_basis audit, field-supported KG edges, release gate audit |
| PAD6_ai_catalyst_discovery_vs_operational_catalyst_activity_guardrail | AI-for-science catalyst/material discovery and catalyst process monitoring | 本项目把催化剂活性作为运行过程中的隐藏状态，用低成本代理、压力冲突解除、field proxy holdout 和循环控制决定保护、再生或更换候选。 | medium | Agent51 field proxy holdout, pressure source resolution, offline catalyst activity labels |
| PAD7_replay_validation_vs_pressure_resolution_protective_release_gate | offline replay validation, data provenance gates and operational safety review | 本项目把压力源冲突、TODO/template/provenance gate、同批次六表、时间窗、场景语义和下游路由组合成 release 前的保护性证据门。 | medium | R7_TO_R8P_WORK_PACKAGE_DIR, R8p acceptance, R8v routing, operator review, release gate audit |

## 正式检索工作包与 Claim 收窄路线

这部分把区别假设继续转成可执行检索任务：去哪里搜、搜什么、收集什么证据、发现相似现有技术后如何收窄 claim。它不是检索结果，也不允许给出新颖性或创造性判断。

- 状态：`formal_search_work_packages_ready_not_search_results`
- 工作包覆盖率：1.0
- 机器可读矩阵：`outputs/agent_architecture_consolidation/formal_search_work_packages.json`
- 证据边界：该矩阵只生成正式检索工作包和 claim fallback 路线；它不是检索结果、不是法律意见、不证明新颖性/创造性，也不产生 field-supported claim。

| 工作包 | 关联区别项 | 搜索目标 | 回退路线 |
| --- | --- | --- | --- |
| FSWP1_cyclic_greybox_soft_sensor_release_gate_search | PAD1_soft_sensor_ml_vs_cyclic_greybox_release_gated_control | 检索低成本/稀疏传感软测量、循环/暂存水处理和 release gate 是否已被组合为灰箱闭环控制。 | 收窄到低频传感-循环窗口协同控制、field replay release gate 或 node-modality hidden-state coverage 子组合。 |
| FSWP2_node_modality_sparse_hidden_state_search | PAD2_sparse_sensor_placement_vs_node_modality_hidden_state_layout | 检索稀疏传感布点是否已被限定到水处理 node-modality 矩阵、隐藏状态覆盖和后续软传感/控制 gate。 | 收窄到 catalyst_activity 弱轴补点、pressure/headloss proxy、regeneration_event 和 field missingness replay。 |
| FSWP3_greybox_multi_agent_safety_arbitration_search | PAD3_marl_pump_coordination_vs_greybox_multi_agent_safety_arbitration | 检索多智能体水处理/泵站协同、离线 RL、策略蒸馏与安全仲裁是否已结合灰箱机理和 field replay 写回边界。 | 收窄到 pressure conflict、catalyst guardrail、KG action constraint 或 release gate 下的安全仲裁。 |
| FSWP4_low_cost_observation_gated_flowsheet_search | PAD4_flowsheet_optimization_vs_low_cost_observation_gated_greybox_control | 检索水处理 flowsheet/优化/成本约束是否已处理低成本观测不足、循环等待和证据门控控制的组合。 | 收窄到低频传感-循环窗口协同控制、执行约束仲裁或 RTD/HRT 证据窗口。 |
| FSWP5_scientific_kg_action_constraint_claim_gate_search | PAD5_scientific_kg_vs_action_constraint_and_claim_gate | 检索 Scientific KG、文献证据矩阵和 claim verification 是否已作为水处理控制动作约束和 release/claim gate。 | 收窄到 KG action constraint patch、claim-specific field package、unsupported action blocking 或 source_basis-to-field queue。 |
| FSWP6_operational_catalyst_activity_guardrail_search | PAD6_ai_catalyst_discovery_vs_operational_catalyst_activity_guardrail | 检索 AI 催化剂发现、催化剂活性监测和水处理再生/更换控制是否已结合低成本代理与 field proxy holdout gate。 | 收窄到 UV254/ORP/pressure_drop/regeneration_event 代理组合、pressure source resolution 或 Agent51 field proxy holdout。 |
| FSWP7_pressure_resolution_protective_release_gate_search | PAD7_replay_validation_vs_pressure_resolution_protective_release_gate | 检索 replay/provenance/operator review 是否已形成针对水处理压力源冲突解除的保护性 release gate 装配链。 | 收窄到 pressure-source conflict resolution、R7-to-R8p work package assembly、release-block correctness 或 operator-review-before-clearance。 |

## 正式检索结果接收 Schema

这部分规定正式检索结果回来后必须如何提交：每条命中要有来源、检索式、命中的 claim 元素、缺失元素、风险信号和 reviewer 状态；claim element comparison 必须逐项标记项目元素与现有技术披露的关系。

- 状态：`formal_search_result_intake_schema_ready_waiting_for_external_results`
- Intake 覆盖率：1.0
- 机器可读 schema：`outputs/agent_architecture_consolidation/formal_search_result_intake_schema.json`
- 证据边界：该 schema 只定义正式检索结果的接收、字段和阻断规则；没有外部检索结果与人工复核时，不能生成 prior-art hit 结论、法律意见或 field-supported claim。

| Intake | 工作包 | 接收状态 | 当前命中数 |
| --- | --- | --- | ---: |
| FSRI1_FSWP1_cyclic_greybox_soft_sensor_release_gate_search | FSWP1_cyclic_greybox_soft_sensor_release_gate_search | formal_search_result_intake_schema_ready_waiting_for_search_results | 0 |
| FSRI2_FSWP2_node_modality_sparse_hidden_state_search | FSWP2_node_modality_sparse_hidden_state_search | formal_search_result_intake_schema_ready_waiting_for_search_results | 0 |
| FSRI3_FSWP3_greybox_multi_agent_safety_arbitration_search | FSWP3_greybox_multi_agent_safety_arbitration_search | formal_search_result_intake_schema_ready_waiting_for_search_results | 0 |
| FSRI4_FSWP4_low_cost_observation_gated_flowsheet_search | FSWP4_low_cost_observation_gated_flowsheet_search | formal_search_result_intake_schema_ready_waiting_for_search_results | 0 |
| FSRI5_FSWP5_scientific_kg_action_constraint_claim_gate_search | FSWP5_scientific_kg_action_constraint_claim_gate_search | formal_search_result_intake_schema_ready_waiting_for_search_results | 0 |
| FSRI6_FSWP6_operational_catalyst_activity_guardrail_search | FSWP6_operational_catalyst_activity_guardrail_search | formal_search_result_intake_schema_ready_waiting_for_search_results | 0 |
| FSRI7_FSWP7_pressure_resolution_protective_release_gate_search | FSWP7_pressure_resolution_protective_release_gate_search | formal_search_result_intake_schema_ready_waiting_for_search_results | 0 |

## 正式检索结果验证门

这部分把接收 schema 进一步转成运行时 gate：检查结果包是否能读、字段是否完整、来源库和检索式是否可追溯、claim element comparison 是否覆盖项目元素、reviewer 字段是否越界。它仍然不是法律意见，也不会在没有外部/人工检索结果时生成 prior-art 结论。

- 状态：`formal_search_result_validation_gate_ready_waiting_for_external_result_package`
- Gate 覆盖率：1.0
- 机器可读 gate：`outputs/agent_architecture_consolidation/formal_search_result_validation_gate.json`
- 证据边界：该 validation gate 只是正式检索结果包进入模型前的结构、来源、比对和 reviewer 边界门；当前没有外部结果包，因此不能生成 prior-art comparison、法律意见或 field-supported claim。

| Gate | Intake | 工作包 | 状态 | 当前 validated hit |
| --- | --- | --- | --- | ---: |
| FSRG1_FSWP1_cyclic_greybox_soft_sensor_release_gate_search | FSRI1_FSWP1_cyclic_greybox_soft_sensor_release_gate_search | FSWP1_cyclic_greybox_soft_sensor_release_gate_search | formal_search_result_validation_gate_ready_waiting_for_result_package | 0 |
| FSRG2_FSWP2_node_modality_sparse_hidden_state_search | FSRI2_FSWP2_node_modality_sparse_hidden_state_search | FSWP2_node_modality_sparse_hidden_state_search | formal_search_result_validation_gate_ready_waiting_for_result_package | 0 |
| FSRG3_FSWP3_greybox_multi_agent_safety_arbitration_search | FSRI3_FSWP3_greybox_multi_agent_safety_arbitration_search | FSWP3_greybox_multi_agent_safety_arbitration_search | formal_search_result_validation_gate_ready_waiting_for_result_package | 0 |
| FSRG4_FSWP4_low_cost_observation_gated_flowsheet_search | FSRI4_FSWP4_low_cost_observation_gated_flowsheet_search | FSWP4_low_cost_observation_gated_flowsheet_search | formal_search_result_validation_gate_ready_waiting_for_result_package | 0 |
| FSRG5_FSWP5_scientific_kg_action_constraint_claim_gate_search | FSRI5_FSWP5_scientific_kg_action_constraint_claim_gate_search | FSWP5_scientific_kg_action_constraint_claim_gate_search | formal_search_result_validation_gate_ready_waiting_for_result_package | 0 |
| FSRG6_FSWP6_operational_catalyst_activity_guardrail_search | FSRI6_FSWP6_operational_catalyst_activity_guardrail_search | FSWP6_operational_catalyst_activity_guardrail_search | formal_search_result_validation_gate_ready_waiting_for_result_package | 0 |
| FSRG7_FSWP7_pressure_resolution_protective_release_gate_search | FSRI7_FSWP7_pressure_resolution_protective_release_gate_search | FSWP7_pressure_resolution_protective_release_gate_search | formal_search_result_validation_gate_ready_waiting_for_result_package | 0 |

## 正式检索结果包模板与 Source Preflight

这部分把 validation gate 前移成可提交的结果包合同，并提供可填报 submission skeleton。外部/人工检索结果需要按 package metadata、work package results、prior-art hit table、claim element comparison 和 fallback recommendation 的结构提交；source preflight 会先检查路径、JSON 根结构、工作包覆盖、必需表形状和 TODO/template markers。

- 模板状态：`formal_search_result_package_templates_ready_waiting_for_submission`
- Submission skeleton：`formal_search_result_package_submission_template_ready`
- Source preflight：`formal_search_result_package_preflight_waiting_for_submission_path`
- Row preflight：`formal_search_result_package_row_preflight_blocked_at_source_preflight`
- Validation execution：`formal_search_result_validation_execution_blocked_at_row_preflight`
- Execution validated/rejected hit：0 / 0
- 可进入人工非法律比较审查：False
- 非法律比较审查包：`formal_search_nonlegal_review_packet_blocked_at_validation_execution`
- 审查包行数：0
- 非法律审查回填模板：`formal_search_nonlegal_review_response_template_blocked_at_review_packet`
- 非法律审查回填 preflight：`formal_search_nonlegal_review_response_preflight_blocked_at_template`
- 回填 accepted/rejected row：0 / 0
- Claim scope patch draft：`formal_search_claim_scope_patch_draft_blocked_at_nonlegal_review_response`
- Draft patch row：0
- 可进入正式专利代理人审查：False
- 可直接生成权利要求文本：False
- Formal counsel review template：`formal_counsel_review_response_template_blocked_at_claim_scope_patch_draft`
- Formal counsel review preflight：`formal_counsel_review_response_preflight_blocked_at_template`
- 可进入技术交底修订队列：False
- Disclosure revision queue：`formal_disclosure_revision_queue_blocked_at_formal_counsel_review_response`
- Disclosure revision item：0
- 可交给人工交底编辑：False
- 可自动应用修订：False
- Disclosure revision impact plan：`formal_disclosure_revision_impact_plan_blocked_at_revision_queue`
- Revision impact item：0
- 可交给人工工件修订：False
- 可自动改写核心工件：False
- Formal search review readiness：`formal_search_review_blocked_at_result_package_source_preflight`
- 最高优先阻塞：`FSR_SOURCE_PREFLIGHT`
- 下一步人工动作：`submit_formal_search_result_package`
- 边界违规数：0
- Formal search execution route plan：`formal_search_execution_route_plan_ready_waiting_for_external_search_execution`
- 检索路线数：7 / 7
- 首个执行动作：`execute_external_or_human_search_and_submit_FORMAL_SEARCH_RESULT_PACKAGE_PATH`
- 机器可读模板：`outputs/agent_architecture_consolidation/formal_search_result_package_template.json`
- 可填报 skeleton：`outputs/agent_architecture_consolidation/formal_search_result_package_submission_template.json`
- 机器可读 preflight：`outputs/agent_architecture_consolidation/formal_search_result_package_source_preflight.json`
- 行级 preflight：`outputs/agent_architecture_consolidation/formal_search_result_package_row_preflight.json`
- Validation execution：`outputs/agent_architecture_consolidation/formal_search_result_validation_execution.json`
- 非法律比较审查包：`outputs/agent_architecture_consolidation/formal_search_nonlegal_comparison_review_packet.json`
- 非法律审查回填模板：`outputs/agent_architecture_consolidation/formal_search_nonlegal_review_response_template.json`
- 非法律审查回填 preflight：`outputs/agent_architecture_consolidation/formal_search_nonlegal_review_response_source_preflight.json`
- Claim scope patch draft：`outputs/agent_architecture_consolidation/formal_search_claim_scope_patch_draft.json`
- Formal counsel review template：`outputs/agent_architecture_consolidation/formal_counsel_review_response_template.json`
- Formal counsel review preflight：`outputs/agent_architecture_consolidation/formal_counsel_review_response_source_preflight.json`
- Disclosure revision queue：`outputs/agent_architecture_consolidation/formal_disclosure_revision_queue.json`
- Disclosure revision impact plan：`outputs/agent_architecture_consolidation/formal_disclosure_revision_impact_plan.json`
- Formal search review readiness：`outputs/agent_architecture_consolidation/formal_search_review_readiness.json`
- Formal search execution route plan：`outputs/agent_architecture_consolidation/formal_search_execution_route_plan.json`
- 证据边界：该 preflight 只检查正式检索结果包的 source/path/root shape；即使通过，也只允许进入 formal_search_result_validation_gate，不能直接生成法律意见、prior-art 结论或 field-supported claim。

| Template | 工作包 | 必需表 | 状态 |
| --- | --- | --- | --- |
| FSRPT1_FSWP1_cyclic_greybox_soft_sensor_release_gate_search | FSWP1_cyclic_greybox_soft_sensor_release_gate_search | prior_art_hit_table, claim_element_comparison_chart, fallback_claim_scope_recommendation | formal_search_result_package_template_ready_waiting_for_submission |
| FSRPT2_FSWP2_node_modality_sparse_hidden_state_search | FSWP2_node_modality_sparse_hidden_state_search | prior_art_hit_table, claim_element_comparison_chart, fallback_claim_scope_recommendation | formal_search_result_package_template_ready_waiting_for_submission |
| FSRPT3_FSWP3_greybox_multi_agent_safety_arbitration_search | FSWP3_greybox_multi_agent_safety_arbitration_search | prior_art_hit_table, claim_element_comparison_chart, fallback_claim_scope_recommendation | formal_search_result_package_template_ready_waiting_for_submission |
| FSRPT4_FSWP4_low_cost_observation_gated_flowsheet_search | FSWP4_low_cost_observation_gated_flowsheet_search | prior_art_hit_table, claim_element_comparison_chart, fallback_claim_scope_recommendation | formal_search_result_package_template_ready_waiting_for_submission |
| FSRPT5_FSWP5_scientific_kg_action_constraint_claim_gate_search | FSWP5_scientific_kg_action_constraint_claim_gate_search | prior_art_hit_table, claim_element_comparison_chart, fallback_claim_scope_recommendation | formal_search_result_package_template_ready_waiting_for_submission |
| FSRPT6_FSWP6_operational_catalyst_activity_guardrail_search | FSWP6_operational_catalyst_activity_guardrail_search | prior_art_hit_table, claim_element_comparison_chart, fallback_claim_scope_recommendation | formal_search_result_package_template_ready_waiting_for_submission |
| FSRPT7_FSWP7_pressure_resolution_protective_release_gate_search | FSWP7_pressure_resolution_protective_release_gate_search | prior_art_hit_table, claim_element_comparison_chart, fallback_claim_scope_recommendation | formal_search_result_package_template_ready_waiting_for_submission |

## 模块化视角

### M1_sparse_observation_layout 低成本稀疏感知与布点

- 类型：core_model
- 作用：决定系统能看到什么、在哪些节点看、用哪些低成本信号看。
- 核心问题：低成本传感是否足以支撑软传感、故障分类和低频闭环控制？
- Agent 数：4
- 核心锚点：sensor_network_sparse_placement_agent, catalyst_activity_proxy_agent
- 策略：keep_as_core_module_with_explicit_io_contract
- 失败边界：无真实拓扑、水力停留时间、安装成本和 field labels 时，只能形成 synthetic topology prior。

### M2_soft_sensor_state_estimation 软传感、缺测矩阵与不确定性

- 类型：core_model
- 作用：把低成本传感、缺测 mask 和灰箱先验转成隐藏状态估计与放行不确定性。
- 核心问题：黑箱过程能否被软传感和灰箱先验转成可审查的灰箱状态？
- Agent 数：6
- 核心锚点：soft_sensor_matrix_coupling_agent
- 策略：merge_subagents_into_module_interface
- 失败边界：synthetic holdout 和 dropout 不能替代真实 field holdout 与真实缺测 replay。

### M3_grey_box_mechanism 灰箱物理、机理解释与故障诊断

- 类型：core_model
- 作用：把软传感状态转成反应、基质、催化剂、水力和副产物风险的机理解释。
- 核心问题：模型是否只是拟合分数，还是能解释为什么该回流、暂存、补药或保护催化剂？
- Agent 数：7
- 核心锚点：minimal_grey_box_physics_agent
- 策略：merge_subagents_into_module_interface
- 失败边界：灰箱参数未由现场 RTD、进出水污染物、催化剂历史和副产物标签校准前，只能作为先验。

### M4_collaborative_control 循环式处理、多设施协同控制与仲裁

- 类型：core_model
- 作用：把循环、暂存、反应、催化剂床、回流和末端精处理组织成可解释的联合动作。
- 核心问题：系统是否能在低频/延迟传感下选择可执行、可回退、可解释的联动动作？
- Agent 数：8
- 核心锚点：multi_facility_collaborative_control_agent, multi_facility_replay_evaluation_agent, engineering_execution_constraint_agent
- 策略：merge_subagents_into_module_interface
- 失败边界：无真实多节点 state-action-reward replay 时，不能写执行器或 release gate。

### M5_kg_claim_evidence 知识图谱、文献证据与 Claim 审查

- 类型：core_model
- 作用：把污染物、材料、过程、低成本信号、隐藏状态、动作和风险连成可追溯证据路径。
- 核心问题：模型每个强 claim 是否有文献、参数边界、适用条件和 field 验证需求？
- Agent 数：5
- 核心锚点：knowledge_graph_reasoning_agent, claim_specific_field_package_agent
- 策略：merge_gate_and_claim_evidence_contracts
- 失败边界：文献和 KG 只能支撑假设、先验和约束，不能替代现场证据。

### M6_field_evidence_chain 现场数据接口、Replay 与证据门控

- 类型：core_model
- 作用：把真实 sensor/lab/operation/replay 数据转成可升级或阻断 claim 的验收链。
- 核心问题：哪些数据表、字段、metadata、gate 和 replay 结果足以把仿真 claim 升级为现场待验证结论？
- Agent 数：7
- 核心锚点：timestamped_campaign_replay_agent, field_replay_import_agent, field_replay_evidence_chain_agent
- 策略：merge_gate_and_claim_evidence_contracts
- 失败边界：接口通过和 synthetic package 只证明流程能跑；data_origin=field 前不能升级现场结论。

### M7_project_operations_support 项目运行、资源调度与实施管理

- 类型：support
- 作用：把批次、队列、资源、预算、库存和恢复爬坡转成项目实施支持层。
- 核心问题：如果模型要落地，运行组织、资源和恢复策略是否可执行？
- Agent 数：18
- 核心锚点：-
- 策略：compress_to_project_operations_support_facade
- 失败边界：该层支持工程实施，不应压过 Agent48/49/51/52/54/55/56/59 的模型核心优化。

### M8_model_governance 模型治理、主链回接与减冗复盘

- 类型：governance
- 作用：检查新增能力是否被主链消费、是否偏离模型核心、是否需要合并或冻结。
- 核心问题：系统是在提高模型能力，还是在继续堆文件、堆 agent 和堆展示？
- Agent 数：2
- 核心锚点：-
- 策略：keep_as_core_module_with_explicit_io_contract
- 失败边界：治理层只能排序、阻断和提出重构路线，本身不替代模型能力或现场验证。

### M9_presentation_delivery 展示、文档与汇报材料

- 类型：frozen_presentation
- 作用：表达和交付模型结果，不改变模型本身。
- 核心问题：是否只是在美化表达而没有提升观测、推理、控制、验证或工程可行性？
- Agent 数：3
- 核心锚点：-
- 策略：freeze_low_priority_until_model_metrics_change
- 失败边界：默认冻结为低优先级，只有模型核心指标更新后才同步。

## 核心链路消费关系

| 来源 | 消费者 | 接口 | 状态 | 边界 |
| --- | --- | --- | --- | --- |
| sensor_network_sparse_placement_agent | soft_sensor_matrix_coupling_agent, catalyst_activity_proxy_agent, multi_facility_collaborative_control_agent | node_modality observation matrix, selected sensors, missingness contract | consumed_synthetic_prior | needs field topology and node-specific timeseries |
| catalyst_activity_proxy_agent | multi_facility_replay_evaluation_agent, multi_facility_collaborative_control_agent | catalyst proxy features, recommended sensor patches, weak-state block boundary | design_prior_only | needs field_proxy_holdout labels before relaxing catalyst blocks |
| minimal_grey_box_physics_agent | soft_sensor_matrix_coupling_agent, main_chain_reconnection_agent | grey-box residual prior, mass-balance and byproduct risk flags | consumed_synthetic_prior | needs field RTD/lab/catalyst/byproduct calibration |
| soft_sensor_matrix_coupling_agent | multi_facility_collaborative_control_agent, soft_sensor_agent | layout_id, node, modality, availability mask, time-since-last-observed | contract_ready_not_field_validated | needs field missingness replay and node-specific values |
| multi_facility_collaborative_control_agent | multi_facility_replay_evaluation_agent, engineering_execution_constraint_agent | facility state/action matrix, joint actions, reward components, distilled rules | replay_ready_synthetic | needs multi-node state-action-reward replay |
| engineering_execution_constraint_agent | multi_facility_collaborative_control_agent, cost_safety_agent, arbitration_agent | reward patch, action constraint patch, arbitration hard blocks | consumed_synthetic_patch | needs PLC/SCADA points, SOP and execution replay |
| knowledge_graph_reasoning_agent | mechanism_agent, control_strategy_agent, field_validation_queue_alignment_agent | evidence paths, action constraints, field_validation_queue | traceable_literature_synthetic_patch | needs field-supported KG edges and source_basis detail |
| claim_specific_field_package_agent | model_core_optimization_governance_agent, future_source_basis_detail_work | claim-specific field package, source_basis completion tasks | schema_ready_source_basis_incomplete | needs citation details or real field package |

## 当前最高边际价值重构

- 动作：`R7a_import_real_field_package_with_metadata_and_csv`
- 标题：导入 data_origin=field 的真实 metadata 与 CSV 包
- 触发指标：R7_status=real_field_package_acceptance_blocked_at_import; passed_stage_count=0/8; field_package_coverage_status=field_package_coverage_blocked_before_import; claim_specific_coverage_rate=0.000; soft_holdout_coverage_pass=False; minimum_replay_contract_status=minimum_replay_contract_blocked_missing_rows; minimum_common_batch_count=0; minimum_valid_matched_batch_count=0; minimum_valid_operation_action_count=0; minimum_invalid_operation_action_count=0; minimum_valid_lab_result_count=0; minimum_invalid_lab_result_count=0; minimum_valid_proxy_label_count=0; minimum_invalid_proxy_label_count=0; minimum_time_order_violation_count=0; pressure_source_conflict_count=0; resolved_pressure_source_conflict_count=0; unresolved_pressure_source_conflict_count=0; pressure_source_resolution_record_count=0; pressure_source_conflict_requires_operator_review=False; pressure_conflict_resolution_status=pressure_source_conflict_resolution_clear; patch_plan_status=patch_plan_blocked_at_import_preflight; patch_plan_item_count=6; source_basis_completion_rate=1.000; minimal_field_package_field_pass_rate=0.000
- 原因：R4b/R5/R6 已完成 patch consumption、schema 覆盖和 source_basis detail；R7 pipeline 现在不仅能看导入是否通过，还能判断真实包是否足以支撑 claim-specific review 和 soft sensor holdout。
- 路径：先修复真实包 preflight/import：替换 placeholder metadata，补齐真实时间戳行和 data_origin=field，通过 Agent44 后再解释 claim/soft-holdout coverage。
- 禁止事项：没有真实 field package 时不能伪造 field-supported 结论，也不能把 synthetic template 当作现场 replay。

## 无真实包时的离线核心 Fallback

- 动作：`R8p_fix_field_rows_source_preflight`
- 标题：按 R8p patch plan 修复 pressure resolution 真实行包
- 原因：R8p 已把 source/schema/template/provenance、同批次六表 bundle、temporal-window、scenario-semantic 和场景验收失败转成可执行补包计划；Agent60 现在应直接消费该计划，R7-to-R8p completion plan 进一步把补齐路径拆成 R7 source package、operator supplement 和 Agent52 replay export 三类证据工单；R8u-24 route contracts 已把三类证据工单拆成生产者、输入输出、验收门和失败边界；R8u-25 route work packages 已把每条证据路线进一步拆成提交文件、字段、验收检查和证据边界；R8u-26 work package templates/preflight 已把提交目录、模板占位和候选包缺口前移到机器检查；R8u-27 work package patch plan 已把预检阻塞转成逐项可执行修补动作；R8u-28 assembly gate 已把四类 work package 到 R8p candidate rows 的装配顺序和验证边界固化；R8u-47 submission readiness review 已把 source、schema/provenance、bundle、temporal、semantic、routing 与 R7 work package assembly 汇总成 R8v 入口门；R8u-48 source package route guide 已把 direct JSON、direct CSV directory 和 R7-to-R8p work package 三条提交路线并列成可执行入口；R8u-49 source package route preflight 已把三条提交路线进一步判定为 ready/waiting/blocked，并保留 replay/holdout 边界；R8u-50 downstream route handoff 已把 R8v 目标、执行顺序、期望 gate metrics 和禁止写入边界固化成交接契约；R8u-51 downstream target gate preflight 已把四个 R8v 下游目标的运行命令、输入合同、输出指标和阻断边界固化为 target-level preflight board；R8u-52 downstream target gate result intake 已把 Agent51/49/52/R7 返回结果的目标覆盖、指标字段、source artifact、人工复核边界和禁止写入边界固化为 result-package preflight；R8u-53 downstream target gate result arbitration 已把四个目标 gate 的 pass/fail/blocked/review 状态合并为只可进入人工复核的安全仲裁门；优先处理最高阻断项，而不是继续停留在泛化的“采集真实行”。
- 边界：不能把 patch plan 当作 field evidence；补包计划只指导现场采集，所有真实行仍必须通过 R8p acceptance、R8v 路由复核和后续 Agent51/49/52/R7 gate，不能写 actuator 或 release gate。

- R7-to-R8p completion plan：r7_to_r8p_completion_plan_waiting_for_r7_package
- completion item 数：6
- completion item 分类：{'r7_source_package': 1, 'operator_supplement': 4, 'agent52_replay_export': 1}
- completion 字段缺口分类：{'r7_source_package': 0, 'operator_supplement': 10, 'agent52_replay_export': 11}
- completion route contracts：completion_route_contracts_ready_waiting_for_r7_package
- open route 数：4
- open routes：['r7_source_package', 'operator_supplement', 'agent52_replay_export', 'r8p_validation_gates']
- completion route work packages：route_work_packages_ready_waiting_for_r7_package
- open work package 数：4
- open work packages：['R8U25_R7_SOURCE_PACKAGE_WORK_PACKAGE', 'R8U25_OPERATOR_SUPPLEMENT_WORK_PACKAGE', 'R8U25_AGENT52_REPLAY_EXPORT_WORK_PACKAGE', 'R8U25_R8P_VALIDATION_GATES_WORK_PACKAGE']
- completion route work package preflight：route_work_package_preflight_waiting_for_submission_dir
- submitted work package 数：0
- passed work package 数：0
- blocked work package 数：4
- completion route work package patch plan：route_work_package_patch_plan_waiting_for_submission_dir
- patch item 数：1
- highest patch：R8U27_SET_R7_TO_R8P_WORK_PACKAGE_DIR
- completion route work package assembly gate：route_work_package_assembly_gate_blocked_waiting_for_submission_dir
- assembly step 数：6
- blocked assembly step 数：6
- submission readiness review：submission_readiness_review_blocked_at_source_package
- submission readiness next action：R8p_fix_field_rows_source_preflight
- submission readiness can route to R8v：False
- source package route guide：source_package_submission_route_guide_ready_for_source_package_submission
- source package recommended route：direct_r8p_json_or_csv_source_package
- source package next action：R8p_submit_direct_json_or_csv_source_package
- source package route preflight：source_package_route_preflight_waiting_for_source_package_submission
- source package recommended route preflight：recommended_route_preflight_waiting_for_direct_source_package

## 复盘后的工作原则

- 后续不再默认新增 agent；优先合并接口、回接主链、压缩重复 gate。
- 展示层 agent 默认冻结，只有模型指标更新后同步。
- 项目运维 agent 作为支持层，不参与当前核心优先级竞争。
- Agent48/51/54、Agent49/52/55、Agent56/59 是当前最需要保持联动的三条核心轴。
- 所有 field-related 输出必须继续区分 schema ready、synthetic replay ready、field validation required。

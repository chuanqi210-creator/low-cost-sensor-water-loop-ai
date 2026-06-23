# Agent60 架构复盘与减冗治理报告

说明：Agent60 是本轮复盘治理工具，不计入被复盘的模型能力链；下列统计审计的是当前模型本体。

- 状态：`module_consolidation_ready_with_complete_interface_contracts`
- Agent 数：60
- 已映射 Agent：60/60
- 模块数：9
- 七层系统骨架覆盖率：1.0
- 六类系统能力覆盖率：1.0
- 骨架状态：`global_system_spine_mapped_with_frozen_expression_layer`
- 模块接口契约覆盖率：1.0
- 接口契约状态：`all_module_interface_contracts_complete`
- 核心模型模块数：6
- 冗余/合并簇数：5
- 展示层冻结 Agent 数：3
- 架构整理分数：1.0
- 自我打断结论：`continue_core_architecture_consolidation`

## 下一步最高边际价值动作

### 1. R7a_import_real_field_package_with_metadata_and_csv

- 标题：导入 data_origin=field 的真实 metadata 与 CSV 包
- 边际价值分：0.842
- 触发指标：R7_status=real_field_package_acceptance_blocked_at_import; passed_stage_count=0/8; field_package_coverage_status=field_package_coverage_blocked_before_import; claim_specific_coverage_rate=0.000; soft_holdout_coverage_pass=False; minimum_replay_contract_status=minimum_replay_contract_blocked_missing_rows; minimum_common_batch_count=0; minimum_valid_matched_batch_count=0; minimum_valid_operation_action_count=0; minimum_invalid_operation_action_count=0; minimum_valid_lab_result_count=0; minimum_invalid_lab_result_count=0; minimum_valid_proxy_label_count=0; minimum_invalid_proxy_label_count=0; minimum_time_order_violation_count=0; pressure_source_conflict_count=0; resolved_pressure_source_conflict_count=0; unresolved_pressure_source_conflict_count=0; pressure_source_resolution_record_count=0; pressure_source_conflict_requires_operator_review=False; pressure_conflict_resolution_status=pressure_source_conflict_resolution_clear; patch_plan_status=patch_plan_blocked_at_import_preflight; patch_plan_item_count=6; source_basis_completion_rate=1.000; minimal_field_package_field_pass_rate=0.000
- 为什么现在做：R4b/R5/R6 已完成 patch consumption、schema 覆盖和 source_basis detail；R7 pipeline 现在不仅能看导入是否通过，还能判断真实包是否足以支撑 claim-specific review 和 soft sensor holdout。
- 实现路径：先修复真实包 preflight/import：替换 placeholder metadata，补齐真实时间戳行和 data_origin=field，通过 Agent44 后再解释 claim/soft-holdout coverage。
- 不能做：没有真实 field package 时不能伪造 field-supported 结论，也不能把 synthetic template 当作现场 replay。

### 2. R2_observation_contract_baseline_completed

- 标题：Agent48/51/54 观测契约 baseline 已形成
- 边际价值分：0.7
- 触发指标：proxy_enhanced_weak_state_coverage=0.580; budget_pass=True
- 为什么现在做：R2 已把稀疏布点、催化剂代理观测和软传感矩阵合同合并为预算内 observation contract；下一步应进入控制 replay 压力测试。
- 实现路径：维护 observation contract 输出，不继续在观测层堆补丁；转向 Agent49/52 replay counterfactual stress。
- 不能做：不能把 synthetic observation contract 当作 field deployment 或 release gate。

### 3. R5_guardrail_schema_extension_baseline_completed

- 标题：R5 guardrail field/replay schema baseline 已覆盖
- 边际价值分：0.697
- 触发指标：unmet_guardrail_field_count=0; field_requirement_patch_consumption_rate=1.000
- 为什么现在做：R5 已把 R4b guardrail 必采字段纳入 Agent30/42 schema，继续扩字段的边际价值下降。
- 实现路径：保留 schema 扩展；下一步补 R4 guardrail source_basis detail 并准备真实 field package 导入验收。
- 不能做：不能把 schema ready 当成 field-supported evidence 或控制有效性。

### 4. R1_unified_gate_baseline_completed

- 标题：统一 field evidence gate baseline 已形成
- 边际价值分：0.676
- 触发指标：source_basis_completion_rate=1.000; citation_detail_completion_rate=1.000
- 为什么现在做：统一 gate 已形成且 source_basis 细节不再是主阻断，后续应回到观测/控制核心链路。
- 实现路径：维持接口，不继续堆 field gate；转向 Agent48/51/54 或 Agent49/52。
- 不能做：不能把维护接口变成文档整理工作。

### 5. R4_freeze_presentation_and_compress_project_ops

- 标题：冻结展示层并压缩项目运维链
- 边际价值分：0.6
- 触发指标：redundancy_cluster_count=5
- 为什么现在做：展示层和项目运维链 agent 数量较多，容易把工作带离模型核心。
- 实现路径：保留输出，但通过 module facade 压缩对主链的暴露面。
- 不能做：不能把压缩整理变成 PPT/Word 美化工作。

## 无真实包时的离线核心 Fallback

- 动作：`R8p_fix_field_rows_source_preflight`
- 标题：按 R8p patch plan 修复 pressure resolution 真实行包
- 触发指标：field_rows_patch_plan_status=field_rows_patch_plan_blocked_at_source_preflight; patch_item_count=12; highest_priority_patch_id=R8P_SOURCE_MISSING_FIELD_ROWS_FILE; operator_handoff_status=field_rows_operator_handoff_ready_needs_source_package; schema_status=field_rows_package_schema_ready; schema_validation_status=schema_validation_blocked_at_source_preflight; collection_checklist_status=field_rows_collection_checklist_ready_needs_source_package; batch_bundle_preflight_status=batch_bundle_preflight_blocked_at_source_preflight; temporal_window_preflight_status=temporal_window_preflight_blocked_at_source_preflight; scenario_semantic_preflight_status=scenario_semantic_preflight_blocked_at_source_preflight; downstream_routing_preflight_status=downstream_routing_preflight_blocked_at_source_preflight; provenance_gate_status=all_required_tables_require_field_origin; all_tables_require_data_origin=True; r7_completion_plan_status=r7_to_r8p_completion_plan_waiting_for_r7_package; r7_completion_item_count=6; r7_completion_item_classes=agent52_replay_export:1,operator_supplement:4,r7_source_package:1; r7_completion_field_gaps=agent52_replay_export:11,operator_supplement:10,r7_source_package:0; r7_route_contract_status=completion_route_contracts_ready_waiting_for_r7_package; r7_open_route_count=4; r7_open_route_ids=r7_source_package,operator_supplement,agent52_replay_export,r8p_validation_gates; r7_work_package_status=route_work_packages_ready_waiting_for_r7_package; r7_open_work_package_count=4; r7_open_work_package_ids=R8U25_R7_SOURCE_PACKAGE_WORK_PACKAGE,R8U25_OPERATOR_SUPPLEMENT_WORK_PACKAGE,R8U25_AGENT52_REPLAY_EXPORT_WORK_PACKAGE,R8U25_R8P_VALIDATION_GATES_WORK_PACKAGE; r7_work_package_template_status=route_work_package_templates_ready_not_evidence; r7_work_package_preflight_status=route_work_package_preflight_waiting_for_submission_dir; r7_submitted_work_package_count=0; r7_passed_work_package_count=0; r7_blocked_work_package_count=4; r7_work_package_patch_plan_status=route_work_package_patch_plan_waiting_for_submission_dir; r7_work_package_patch_item_count=1; r7_work_package_highest_priority_patch_id=R8U27_SET_R7_TO_R8P_WORK_PACKAGE_DIR; r7_work_package_assembly_gate_status=route_work_package_assembly_gate_blocked_waiting_for_submission_dir; r7_work_package_assembly_step_count=6; r7_work_package_ready_assembly_step_count=0; r7_work_package_blocked_assembly_step_count=6; submission_readiness_review_status=submission_readiness_review_blocked_at_source_package; submission_readiness_next_operator_action=R8p_fix_field_rows_source_preflight; submission_readiness_can_route_to_r8v=False; source_package_route_guide_status=source_package_submission_route_guide_ready_for_source_package_submission; source_package_recommended_route_id=direct_r8p_json_or_csv_source_package; source_package_next_operator_action=R8p_submit_direct_json_or_csv_source_package; source_package_route_option_count=3; source_package_route_preflight_status=source_package_route_preflight_waiting_for_source_package_submission; source_package_recommended_route_preflight_status=recommended_route_preflight_waiting_for_direct_source_package; source_package_route_preflight_next_operator_action=R8p_submit_direct_json_or_csv_source_package; source_package_ready_route_count=0; source_package_waiting_route_count=3; source_package_blocked_route_count=0; downstream_route_handoff_status=downstream_route_handoff_blocked_by_upstream_r8p_preflight; downstream_ready_handoff_target_count=0; downstream_blocked_handoff_target_count=4; downstream_route_handoff_next_operator_action=R8p_fix_field_rows_source_preflight; downstream_target_gate_preflight_status=downstream_target_gate_preflight_blocked_by_downstream_route_handoff; downstream_ready_target_gate_count=0; downstream_blocked_target_gate_count=4; downstream_target_gate_preflight_next_operator_action=R8p_fix_field_rows_source_preflight; downstream_target_gate_result_preflight_status=downstream_target_gate_result_preflight_blocked_by_target_gate_preflight; downstream_target_gate_result_submitted_count=0; downstream_target_gate_result_accepted_count=0; downstream_target_gate_result_rejected_count=0; downstream_target_gate_result_next_operator_action=R8p_fix_field_rows_source_preflight; downstream_target_gate_result_arbitration_status=downstream_target_gate_result_arbitration_blocked_by_result_preflight; downstream_target_gate_result_arbitration_next_operator_action=R8p_fix_field_rows_source_preflight; downstream_target_gate_result_can_route_to_operator_review=False; downstream_target_gate_result_can_emit_protective_control_candidate=False; downstream_target_gate_operator_review_preflight_status=downstream_target_gate_operator_review_preflight_blocked_by_arbitration; downstream_target_gate_operator_review_approved_count=0; downstream_target_gate_operator_review_rejected_count=0; downstream_target_gate_operator_review_hold_count=0; downstream_target_gate_operator_review_next_operator_action=R8p_fix_field_rows_source_preflight; downstream_target_gate_operator_review_can_route_to_post_review_gate=False; downstream_target_gate_operator_review_can_emit_protective_control_candidate=False; downstream_target_gate_post_review_gate_status=downstream_target_gate_post_review_gate_blocked_by_operator_review_preflight; downstream_target_gate_post_review_next_operator_action=R8p_fix_field_rows_source_preflight; downstream_target_gate_post_review_can_route_to_protective_candidate=False; downstream_target_gate_post_review_can_emit_protective_control_candidate=False; downstream_target_gate_protective_candidate_evaluation_status=protective_candidate_evaluation_blocked_by_post_review_gate; downstream_target_gate_protective_candidate_next_operator_action=R8p_fix_field_rows_source_preflight; downstream_target_gate_protective_candidate_can_emit=False; downstream_target_gate_protective_candidate_can_route_to_final_execution_review=False
- 原因：R8p 已把 source/schema/template/provenance、同批次六表 bundle、temporal-window、scenario-semantic 和场景验收失败转成可执行补包计划；Agent60 现在应直接消费该计划，R7-to-R8p completion plan 进一步把补齐路径拆成 R7 source package、operator supplement 和 Agent52 replay export 三类证据工单；R8u-24 route contracts 已把三类证据工单拆成生产者、输入输出、验收门和失败边界；R8u-25 route work packages 已把每条证据路线进一步拆成提交文件、字段、验收检查和证据边界；R8u-26 work package templates/preflight 已把提交目录、模板占位和候选包缺口前移到机器检查；R8u-27 work package patch plan 已把预检阻塞转成逐项可执行修补动作；R8u-28 assembly gate 已把四类 work package 到 R8p candidate rows 的装配顺序和验证边界固化；R8u-47 submission readiness review 已把 source、schema/provenance、bundle、temporal、semantic、routing 与 R7 work package assembly 汇总成 R8v 入口门；R8u-48 source package route guide 已把 direct JSON、direct CSV directory 和 R7-to-R8p work package 三条提交路线并列成可执行入口；R8u-49 source package route preflight 已把三条提交路线进一步判定为 ready/waiting/blocked，并保留 replay/holdout 边界；R8u-50 downstream route handoff 已把 R8v 目标、执行顺序、期望 gate metrics 和禁止写入边界固化成交接契约；R8u-51 downstream target gate preflight 已把四个 R8v 下游目标的运行命令、输入合同、输出指标和阻断边界固化为 target-level preflight board；R8u-52 downstream target gate result intake 已把 Agent51/49/52/R7 返回结果的目标覆盖、指标字段、source artifact、人工复核边界和禁止写入边界固化为 result-package preflight；R8u-53 downstream target gate result arbitration 已把四个目标 gate 的 pass/fail/blocked/review 状态合并为只可进入人工复核的安全仲裁门；优先处理最高阻断项，而不是继续停留在泛化的“采集真实行”。
- 禁止事项：不能把 patch plan 当作 field evidence；补包计划只指导现场采集，所有真实行仍必须通过 R8p acceptance、R8v 路由复核和后续 Agent51/49/52/R7 gate，不能写 actuator 或 release gate。

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
- source package ready/waiting/blocked routes：0/3/0
- completion plan 路径：outputs/pressure_resolution_replay_scenario_pack/pressure_resolution_replay_rows_r7_completion_plan.json

## 全局七层系统骨架

| 层级 | 覆盖状态 | 模块 | 能力 | 核心问题 |
| --- | --- | --- | --- | --- |
| L1_field_object_layer 现场对象层 | covered | M1_sparse_observation_layout, M5_kg_claim_evidence, M7_project_operations_support | controllability, engineering_feasibility, explainability, observability, verifiability | 污染物、水质基质、处理单元、拓扑和材料/药剂对象是否被明确建模？ |
| L2_observation_layer 观测层 | covered | M1_sparse_observation_layout, M2_soft_sensor_state_estimation, M6_field_evidence_chain | engineering_feasibility, observability, verifiability | 低成本传感、稀疏布点、缺测、延迟和节点-模态矩阵是否能支撑隐藏状态估计？ |
| L3_state_estimation_layer 状态估计层 | covered | M1_sparse_observation_layout, M2_soft_sensor_state_estimation, M3_grey_box_mechanism | engineering_feasibility, explainability, observability, verifiability | 软传感、灰箱状态和弱隐藏变量是否有可验证的估计契约？ |
| L4_mechanism_evidence_layer 机理证据层 | covered | M3_grey_box_mechanism, M5_kg_claim_evidence | explainability, verifiability | 机理解释、知识图谱、文献依据和失败边界是否可追溯？ |
| L5_diagnostic_decision_layer 诊断决策层 | covered | M3_grey_box_mechanism, M4_collaborative_control, M6_field_evidence_chain | controllability, engineering_feasibility, explainability, verifiability | 诊断、故障识别、控制候选、策略解释和人工复核是否形成闭环？ |
| L6_closed_loop_execution_layer 闭环执行层 | covered | M4_collaborative_control, M7_project_operations_support | controllability, engineering_feasibility, explainability, verifiability | 回流、暂存、延长停留、投药、切换单元和保护性阻断是否可执行？ |
| L7_validation_governance_layer 验证治理层 | covered | M2_soft_sensor_state_estimation, M4_collaborative_control, M5_kg_claim_evidence, M6_field_evidence_chain, M7_project_operations_support, M8_model_governance | controllability, engineering_feasibility, evolvability, explainability, observability, verifiability | field package、replay、holdout、calibration、claim gate 和阶段治理是否能审查结论？ |

## 模块接口契约矩阵

| 模块 | 输入/输出契约 | 状态变量 | 可传递指标 | 不能做 | 现场验证需求 |
| --- | --- | --- | --- | --- | --- |
| M1_sparse_observation_layout 低成本稀疏感知与布点 | 输入：污染场景、处理单元/管网拓扑候选、低成本传感候选、安装/维护成本、节点-模态可用性。<br>输出：node-modality 观测矩阵、候选布点方案、弱隐藏状态覆盖、成本约束和软传感输入先验。 | observable_nodes, modalities, weak_state_coverage, cost_index, topology_prior | weak_state_coverage, soft_sensor_reconstruction_gain, total_cost_index, single_point_dependency | 不能仅靠加点位宣称现场可观测；无真实拓扑/标签时不能作为部署结论。 | 真实拓扑、水力停留时间、安装可达性、节点级时间序列和弱状态离线标签。 |
| M2_soft_sensor_state_estimation 软传感、缺测矩阵与不确定性 | 输入：node-modality 观测矩阵、缺测 mask、低频/延迟特征、灰箱先验、离线标签和 field holdout split。<br>输出：隐藏状态估计、预测区间、缺测鲁棒性、OOD/abstention 标志和 release 前不确定性边界。 | pollutant_residual, reaction_completion, matrix_interference, catalyst_activity, uncertainty_interval | masked_mae, interval_coverage, missingness_robustness_score, field_holdout_gate_pass | 不能把 synthetic dropout 或模板 holdout 写成现场缺测鲁棒性结论。 | 真实 field holdout、节点级缺测原因、低频采样延迟和目标污染物/弱状态标签。 |
| M3_grey_box_mechanism 灰箱物理、机理解释与故障诊断 | 输入：软传感状态、反应/传质先验、RTD/停留时间、催化剂历史、基质信息和副产物风险标签。<br>输出：灰箱残差、机理假设、故障模式、反应/水力/催化剂边界和可解释控制约束。 | k_eff, mass_balance_residual, hydraulic_delay, catalyst_decay, byproduct_risk | grey_box_residual, mass_balance_residual, mechanism_hypothesis_count, fault_mode_coverage | 不能把未校准灰箱参数当成现场机理结论或放行依据。 | 现场 RTD、池容/流量、进出水污染物、氧化剂余量、催化剂再生历史和副产物面板。 |
| M4_collaborative_control 循环式处理、多设施协同控制与仲裁 | 输入：状态估计、灰箱边界、工程约束、候选动作、reward prior、多节点 replay schema 和人工复核规则。<br>输出：联合动作候选、保护性阻断、回流/暂存/投药/切换建议、策略解释和不可写执行器边界。 | facility_state, joint_action, reward_components, guardrail_context, operator_review_required | joint_action_accuracy, reward_regret, distilled_policy_accuracy, false_positive_cost | 无真实多节点 replay 和人工复核门时不能写执行器或 release gate。 | 真实多节点 sensor/lab/operation/action/reward replay、PLC/SCADA 点表、SOP 和执行反馈。 |
| M5_kg_claim_evidence 知识图谱、文献证据与 Claim 审查 | 输入：污染物、材料、工况、过程机制、低成本信号、文献 source_basis 和 field validation needs。<br>输出：typed KG edge、evidence path、claim constraint、source_basis detail 和 field validation queue。 | evidence_edge, claim_status, source_basis_detail, constraint_hit, field_supported_edge | evidence_traceability, constraint_hit_rate, source_basis_completion_rate, field_supported_edge_ratio | 不能把文献依据或 KG 推理当成现场支持结论。 | 可追溯 citation、参数/适用边界、claim-specific 现场字段和 field-supported KG edges。 |
| M6_field_evidence_chain 现场数据接口、Replay 与证据门控 | 输入：metadata、sensor/lab/operation/proxy/replay CSV、field origin、timestamp alignment、holdout 和 calibration records。<br>输出：import gate、timestamped replay、evidence chain、claim gate、field package patch plan 和升级/阻断结论。 | field_import_pass, evidence_chain_pass, claim_gate_status, replay_contract_status, field_supported_claim | field_replay_import_pass, field_need_to_gate_coverage, evidence_chain_pass, can_write_to_release_gate | 不能把 header-only/template package 或 synthetic replay 当成 field evidence。 | data_origin=field 的完整 metadata/CSV、共同 batch、时间顺序、QA 通过标签和人工复核记录。 |
| M7_project_operations_support 项目运行、资源调度与实施管理 | 输入：批次、队列、资源、库存、预算、执行时间、恢复爬坡和现场作业约束。<br>输出：项目运行计划、资源瓶颈、重规划触发、恢复策略和工程实施支持信号。 | campaign_queue, resource_capacity, replan_trigger, recovery_load_fraction, deployment_budget | campaign_success_rate, resource_bottleneck_count, replan_trigger, recovery_load_fraction | 不能压过模型核心链路，也不能替代状态估计、控制 replay 或 field claim gate。 | 真实运行排班、资源成本、执行时间、故障恢复和人工操作记录。 |
| M8_model_governance 模型治理、主链回接与减冗复盘 | 输入：全局 goal、模块指标、agent audit、evidence matrix、backlog、stage gate 和 regression results。<br>输出：优先级排序、骨架覆盖、接口缺口、冗余合并建议、冻结策略和下一步核心动作。 | system_spine_status, interface_contract_coverage, consolidation_score, self_interrupt_verdict, fallback_action | main_chain_prior_consumption_rate, mapped_agent_count, redundancy_cluster_count, system_spine_coverage | 治理层不能替代模型能力、现场验证或执行器授权。 | 不直接产生 field evidence；只检查 field evidence 的路径、门控和边界。 |
| M9_presentation_delivery 展示、文档与汇报材料 | 输入：已验证或明确标注边界的模型结果、图表、报告摘要和用户汇报需求。<br>输出：文档、PPT、索引和展示材料。 | deliverable_status, artifact_index_status | artifact_availability | 不能改变模型结论，不能制造 field-supported claim，不能作为核心优化中心。 | 无；仅表达层。需要同步模型边界而不是产生现场证据。 |

## 专利级技术特征 Ledger

说明：该 ledger 是技术交底成熟度检查，不是法律意见，也不是 field-supported 结论。

- 状态：`technical_feature_ledger_ready_as_disclosure_scaffold_not_field_claim`
- 技术特征数：8/8
- 覆盖率：1.0
- 抽象口号风险特征：[]
- 允许现场 claim 升级：False
- 机器可读 ledger：`outputs/agent_architecture_consolidation/patent_technical_feature_ledger.json`

| 特征 | 对应模块 | 技术问题 | 技术手段 | 控制动作 | 验证指标 | 边界 |
| --- | --- | --- | --- | --- | --- | --- |
| PTF1_node_modality_sparse_sensing | M1_sparse_observation_layout | 低成本现场只能布设少量 pH/ORP/电导/浊度/UV254/流量等传感器，中间反应过程仍接近黑箱。 | 构建 node-modality 稀疏感知矩阵，把节点、传感模态、安装成本、缺测风险和隐藏状态覆盖统一评分。 | 选择布点组合, 标记弱观测轴, 触发催化剂活性代理补点, 保留未验证保护边界 | weak_state_coverage, matrix_rank, condition_number_proxy, single_point_dependency | 当前可作为 synthetic/design-prior 与接口验证；真实部署仍需 field topology、安装可达性和节点标签。 |
| PTF2_soft_sensor_grey_state_estimation | M2_soft_sensor_state_estimation | 低频、延迟和缺测传感无法直接测得残留污染物、反应完成度、催化剂活性和副产物风险。 | 以稀疏传感矩阵、缺测 mask、时间延迟、灰箱先验和离线标签训练软传感器，并输出不确定性和 abstention 标志。 | 估计隐藏状态, 输出不确定性, 触发暂存等待, 阻断 release gate, 要求人工复核 | masked_mae, interval_coverage, missingness_robustness_score, field_holdout_gate_pass | synthetic dropout 或模板 holdout 只能证明接口可运行，不能替代真实 field holdout。 |
| PTF3_grey_box_mechanism_boundary | M3_grey_box_mechanism | 单纯预测无法解释为何需要回流、延长停留、补药、再生催化剂或阻断放行。 | 引入反应动力学、质量守恒、水力延迟、催化剂衰减、基质抑制和副产物风险等灰箱边界。 | 解释故障模式, 约束投药/回流动作, 触发催化剂再生或更换候选, 生成保护性阻断 | grey_box_residual, mass_balance_residual, fault_mode_coverage, resolved_case_to_mechanism_coverage | 未由现场 RTD、污染物面板和催化剂历史校准前，灰箱参数只能作为先验。 |
| PTF4_cyclic_low_frequency_control | M4_collaborative_control | 低成本传感速度慢、采样少，传统一次通过式处理难以及时判断是否达标。 | 利用循环、暂存、延长停留和多设施协同控制，为软传感、诊断和人工复核争取时间窗口。 | 回流, 延长停留时间, 暂存等待, 调整投药, 切换处理单元, 催化剂再生/更换, 放行或阻断 | joint_action_accuracy, reward_regret, false_positive_cost, release_block_correctness | synthetic replay 只能证明控制候选逻辑，不能写真实执行器或 release gate。 |
| PTF5_mechanism_kg_evidence_constraint | M5_kg_claim_evidence | 材料、污染物、工况和低成本信号之间的证据分散，容易让模型生成不可追溯 claim。 | 构建 typed KG 和 source_basis，把污染物、材料、过程条件、低成本信号、隐藏状态、动作和风险连接为证据路径。 | 约束控制候选, 触发必采字段, 阻断无证据 claim, 标记文献支持与现场支持边界 | evidence_traceability, constraint_hit_rate, source_basis_completion_rate, field_supported_edge_ratio | literature-supported 和 KG-inferred 不能等同于 field-supported。 |
| PTF6_field_replay_release_gate | M6_field_evidence_chain | 仿真、模板和真实现场数据混杂时，系统可能错误地把可运行流程当成现场有效。 | 建立 field package、timestamped replay、holdout、operator review、calibration 和 release gate 的分级证据链。 | 导入真实包, 运行 replay, 执行 holdout, 要求 calibration, 阻断 claim upgrade, 允许或拒绝 release gate | field_replay_import_pass, evidence_chain_pass, claim_gate_status, can_write_to_release_gate | header-only、template、sample 或 synthetic replay 均不能替代 data_origin=field。 |
| PTF7_engineering_execution_constraints | M7_project_operations_support | 即使模型给出动作，现场仍受泵阀、药剂、库存、人工、延迟和恢复爬坡限制。 | 把资源、成本、执行延迟、恢复爬坡和 SOP 约束作为控制 reward、仲裁和实施计划的硬边界。 | 限制不可执行动作, 触发重规划, 调整恢复爬坡, 约束投药/回流执行时序 | resource_bottleneck_count, replan_trigger, recovery_load_fraction, execution_constraint_violation_count | 项目运维支持不替代状态估计、field replay 或 release gate。 |
| PTF8_stage_gated_model_governance | M8_model_governance | agent 数量增长会造成重复 gate、上下游割裂和模型主链不清。 | 采用七层系统骨架、接口契约、冗余簇、fallback 和阶段门控，审查每个新增能力是否回接主链。 | 冻结展示层, 合并重复 gate, 重排高边际价值任务, 阻断越界 field claim, 维持低频自我打断 | system_spine_coverage, interface_contract_coverage, redundancy_cluster_count, self_interrupt_verdict | 治理输出不产生 field evidence，只审查证据路径与模型边界。 |

## 技术方案 Claim Skeleton Scaffold

说明：该 scaffold 只把技术特征组合成方法/系统/从属方向骨架，不是法律权利要求文本，也不是授权判断。

- 状态：`technical_claim_skeleton_ready_as_scaffold_not_legal_claim_not_field_claim`
- Claim scaffold 数：7/7
- 覆盖率：1.0
- 独立方向：['TCS1_independent_method_low_cost_sparse_cyclic_greybox_control', 'TCS2_independent_system_architecture']
- 从属/分案方向：['TCS3_dependent_catalyst_activity_regeneration_control', 'TCS4_dependent_node_modality_sparse_hidden_state_estimation', 'TCS5_dependent_field_replay_protective_writeback', 'TCS6_dependent_low_frequency_cycle_window_control', 'TCS7_dependent_greybox_multi_agent_safety_arbitration']
- 缺失技术特征覆盖：[]
- 允许现场 claim 升级：False
- 机器可读 scaffold：`outputs/agent_architecture_consolidation/technical_claim_skeleton_scaffold.json`

| Scaffold | 类型 | 映射特征 | 组合手段 | 验证门 | 边界 |
| --- | --- | --- | --- | --- | --- |
| TCS1_independent_method_low_cost_sparse_cyclic_greybox_control | independent_method_scaffold | PTF1_node_modality_sparse_sensing, PTF2_soft_sensor_grey_state_estimation, PTF3_grey_box_mechanism_boundary, PTF4_cyclic_low_frequency_control, PTF5_mechanism_kg_evidence_constraint, PTF6_field_replay_release_gate | 将 node-modality 稀疏观测、软传感灰箱估计、机理/KG 证据约束、循环式控制动作和 field replay/release gate 串成主链。 | R7 field package, R8p row acceptance gates, R8v routing, field holdout, operator review, release gate | 该主链 scaffold 不能替代真实 field replay；未通过验证门前只能作为技术方案候选。 |
| TCS2_independent_system_architecture | independent_system_scaffold | PTF1_node_modality_sparse_sensing, PTF2_soft_sensor_grey_state_estimation, PTF3_grey_box_mechanism_boundary, PTF4_cyclic_low_frequency_control, PTF5_mechanism_kg_evidence_constraint, PTF6_field_replay_release_gate, PTF7_engineering_execution_constraints, PTF8_stage_gated_model_governance | 把七层系统骨架落实为对象层、观测层、估计层、机理证据层、诊断决策层、闭环执行层和验证治理层的组件组合。 | system_spine_coverage, interface_contract_coverage, replay regression, field evidence chain, operator review | 系统 scaffold 只说明结构完整性，不能证明任一现场控制结论成立。 |
| TCS3_dependent_catalyst_activity_regeneration_control | dependent_or_divisional_scaffold | PTF1_node_modality_sparse_sensing, PTF2_soft_sensor_grey_state_estimation, PTF3_grey_box_mechanism_boundary, PTF4_cyclic_low_frequency_control, PTF6_field_replay_release_gate | 以 UV254/ORP/压降/再生事件/离线活性标签形成代理观测，并将软传感不确定性和灰箱催化剂衰减边界接入再生/更换动作。 | Agent51 field proxy holdout, pressure_source_resolution, R8p/R8v, operator review | 代理相关性和 synthetic holdout 不能替代真实 field proxy holdout。 |
| TCS4_dependent_node_modality_sparse_hidden_state_estimation | dependent_or_divisional_scaffold | PTF1_node_modality_sparse_sensing, PTF2_soft_sensor_grey_state_estimation | 将节点、模态、成本、缺测、拓扑和隐藏状态需求合并为矩阵，并把布点结果作为软传感输入契约。 | field topology, node-specific time series, field missingness replay, offline labels | 无真实拓扑和标签时只能作为 design prior。 |
| TCS5_dependent_field_replay_protective_writeback | dependent_or_divisional_scaffold | PTF4_cyclic_low_frequency_control, PTF6_field_replay_release_gate, PTF8_stage_gated_model_governance | 将 field package、timestamped replay、holdout、operator review、claim gate 和 release gate 组成保护性写回链。 | R7, R8p, R8v, field holdout, operator review, release gate | 模板、样例、header-only 和 synthetic replay 都不能触发 field-supported 写回。 |
| TCS6_dependent_low_frequency_cycle_window_control | dependent_or_divisional_scaffold | PTF2_soft_sensor_grey_state_estimation, PTF4_cyclic_low_frequency_control, PTF7_engineering_execution_constraints | 把低频采样间隔、软传感不确定性、暂存容量、回流路径和执行延迟共同纳入动作选择。 | timestamped replay, latency budget replay, operator review, actuator feedback | 延迟预算和 synthetic replay 不能替代真实 timestamped campaign replay。 |
| TCS7_dependent_greybox_multi_agent_safety_arbitration | dependent_or_divisional_scaffold | PTF3_grey_box_mechanism_boundary, PTF4_cyclic_low_frequency_control, PTF5_mechanism_kg_evidence_constraint, PTF7_engineering_execution_constraints, PTF8_stage_gated_model_governance | 将灰箱残差、KG 证据、工程约束、reward prior 和人工复核门合成仲裁规则。 | counterfactual replay, field state-action-reward replay, operator review, governance stage gate | 多智能体仲裁逻辑通过前仍是候选策略，不能越过 field replay 写执行器。 |

## 技术实施例与验证矩阵

说明：该矩阵把方法/系统/从属方向落成可验收实施例，但仍不生成 field evidence。

- 状态：`technical_embodiment_matrix_ready_not_field_evidence`
- 实施例数：6/6
- 覆盖率：1.0
- 缺失 claim 覆盖：[]
- 缺失 feature 覆盖：[]
- 允许现场 claim 升级：False
- 机器可读矩阵：`outputs/agent_architecture_consolidation/technical_embodiment_validation_matrix.json`

| 实施例 | 链接 Claim | 数据包/工件 | 验证门 | 验收指标 | 边界 |
| --- | --- | --- | --- | --- | --- |
| TE1_end_to_end_low_cost_cyclic_greybox_control | TCS1_independent_method_low_cost_sparse_cyclic_greybox_control, TCS2_independent_system_architecture | R7 field package, R8p accepted pressure-resolution rows, R8v routing outputs, field holdout split, operator review log | R7 field package, R8p, R8v, field holdout, operator review, release gate | field_import_pass, field_scenario_coverage, joint_action_accuracy, evidence_chain_pass, can_write_to_release_gate | 任一 field/replay/holdout/release gate 阻断时，不得生成 field-supported claim 或执行器写回。 |
| TE2_pressure_resolution_route_package_validation | TCS5_dependent_field_replay_protective_writeback, TCS6_dependent_low_frequency_cycle_window_control | pressure_resolution_replay_rows_r7_completion_route_work_package_preflight.json, pressure_resolution_replay_rows_r7_completion_route_work_package_patch_plan.json, pressure_resolution_replay_rows_r7_completion_route_work_package_assembly_gate.json, pressure_source_resolution | work package preflight, R8u-27 patch plan, R8u-28 assembly gate, R8p, R8v, operator review | submitted_work_package_count, passed_work_package_count, blocked_assembly_step_count, field_scenario_coverage, pressure_source_conflict_requires_operator_review | 未设置或未通过 R7_TO_R8P_WORK_PACKAGE_DIR 时，只能保留 candidate workflow，不能生成 field evidence。 |
| TE3_catalyst_activity_proxy_regeneration | TCS3_dependent_catalyst_activity_regeneration_control | node_modality_sensor_timeseries, pressure_headloss_event_log, offline_lab_results, campaign_operation_log, Agent51 field proxy holdout summary | Agent51 field proxy holdout, pressure_source_resolution, R8p/R8v, operator review | scoreable_batch_count, proxy_label_correlation, holdout_mae, pressure_source_conflict_count, catalyst_guardrail_mode | field proxy holdout 未通过或压力冲突未解除时，不能触发自动再生/更换执行器。 |
| TE4_node_modality_sparse_hidden_state_layout | TCS4_dependent_node_modality_sparse_hidden_state_estimation | sparse_placement_metrics.json, observation_contract_metrics.json, soft_sensor_matrix_metrics.json, field topology package | field topology, field missingness replay, offline labels, soft sensor holdout | weak_state_coverage, selected_matrix_rank, condition_number_proxy, missingness_robustness_score | 无真实拓扑和标签时不能声称现场最优布点或现场可观测性达标。 |
| TE5_low_frequency_cycle_window_control | TCS6_dependent_low_frequency_cycle_window_control | timestamped_campaign_replay, grey_box_dynamic_latency metrics, campaign_operation_log, fast_proxy_event_log | timestamped replay, latency budget replay, operator review, actuator feedback | latency_violation_rate, hold_time_min, storage_margin, false_positive_cost, release_block_correctness | 暂存容量或执行延迟不足时，不能选择依赖循环窗口的控制动作。 |
| TE6_greybox_multi_agent_safety_arbitration | TCS7_dependent_greybox_multi_agent_safety_arbitration | control_replay_stress_metrics.json, multi_facility_replay_evaluation metrics, knowledge_graph_reasoning outputs, engineering_execution_constraint metrics, field state-action-reward replay | counterfactual replay, field state-action-reward replay, operator review, governance stage gate | joint_action_accuracy, reward_regret, constraint_hit_rate, false_positive_cost, operator_review_required | 机制冲突、证据缺口或执行约束不满足时必须保持阻断。 |

## 技术效果度量矩阵

说明：该矩阵把实施例中的技术效果转成基线、指标、阈值和验证门；它仍然不是 field-supported 结论。

- 状态：`technical_effect_measurement_matrix_ready_not_field_evidence`
- 技术效果数：7/7
- 覆盖率：1.0
- 缺失实施例覆盖：[]
- 允许现场 claim 升级：False
- 可写执行器：False
- 可写 release gate：False
- 机器可读矩阵：`outputs/agent_architecture_consolidation/technical_effect_measurement_matrix.json`

| 技术效果 | 关联实施例 | 基线 | 指标 | 阈值/规则 | 验证门 | 边界 |
| --- | --- | --- | --- | --- | --- | --- |
| TEM1_observability_gain_under_sparse_sensing | TE4_node_modality_sparse_hidden_state_layout | 进水一个、出水一个的低成本规则布点，或不考虑节点-模态矩阵的 cost-only 贪心布点。 | weak_state_coverage, selected_matrix_rank, condition_number_proxy, single_point_dependency, missingness_robustness_score | weak_state_coverage must improve over baseline without exceeding cost cap<br>selected_matrix_rank must not decrease relative to baseline layout<br>field topology and offline weak-state labels must confirm the same hidden-state coverage direction | field topology package + missingness replay + soft sensor holdout | 没有真实拓扑、节点级时间序列和弱状态标签时，只能说明候选布点逻辑，不能声称现场最优布点。 |
| TEM2_blackbox_to_greybox_state_estimation | TE1_end_to_end_low_cost_cyclic_greybox_control, TE4_node_modality_sparse_hidden_state_layout | 仅用出水阈值、单点经验规则或不带灰箱先验的纯黑箱回归模型。 | masked_mae, interval_coverage, field_holdout_gate_pass, grey_box_residual, abstention_or_ood_rate | masked_mae must improve on the field holdout split before claim upgrade<br>prediction intervals must satisfy the configured coverage gate<br>OOD or high-uncertainty batches must abstain instead of releasing control | field holdout + uncertainty calibration + operator review | field holdout 未通过或不确定性未校准时，软传感结果只能作为候选估计，不能解除保护或放行。 |
| TEM3_low_frequency_cycle_window_reduces_fast_sensor_need | TE5_low_frequency_cycle_window_control | 一次通过式处理或假设传感/检测即时返回的闭环控制。 | latency_violation_rate, hold_time_min, storage_margin, false_positive_cost, release_block_correctness | timestamped field replay must show cycle window covers sensor/lab/operator latency<br>latency_violation_rate must remain below the configured gate before release candidate generation<br>false_positive_cost and release_block_correctness must be reported together | timestamped field replay + latency budget gate + actuator feedback | 暂存容量、回流通道或执行器延迟不足时，不能选择依赖循环窗口的控制动作。 |
| TEM4_catalyst_proxy_guardrail_effect | TE3_catalyst_activity_proxy_regeneration | 只按运行时长、处理批次数或人工经验判断催化剂再生/更换。 | scoreable_batch_count, proxy_label_correlation, holdout_mae, pressure_source_conflict_count, catalyst_guardrail_mode | Agent51 field proxy holdout must pass before regeneration/replacement candidate generation<br>holdout_mae and proxy_label_correlation must be reported on field-linked batches<br>pressure source conflict must be resolved or sent to operator review before catalyst action | Agent51 field proxy holdout + pressure_source_resolution + R8p/R8v | 代理 holdout 未通过或压力冲突未解除时，不能触发自动再生或更换执行器。 |
| TEM5_field_replay_protective_writeback_reduces_false_release | TE1_end_to_end_low_cost_cyclic_greybox_control, TE2_pressure_resolution_route_package_validation, TE5_low_frequency_cycle_window_control | 直接使用 synthetic replay、静默平均冲突压力源或跳过人工复核的自动放行流程。 | evidence_chain_pass, pressure_source_conflict_requires_operator_review, can_write_to_release_gate, release_block_correctness, field_scenario_coverage | R7/R8p/R8v gates must pass before any release-gated claim<br>pressure_source_conflict_requires_operator_review must remain true until conflict resolution is accepted<br>can_write_to_release_gate must remain false in scaffold/template/synthetic states | R7/R8p/R8v + pressure conflict operator review + release gate | 真实行包、冲突解除或 operator review 任一缺失时，只能阻断或生成补件任务，不能放行。 |
| TEM6_greybox_multi_agent_arbitration_reduces_conflict_actions | TE6_greybox_multi_agent_safety_arbitration | 简单多数投票、单 agent 规则或未受机理证据约束的黑箱 MARL 策略。 | joint_action_accuracy, reward_regret, constraint_hit_rate, false_positive_cost, operator_review_required | field state-action-reward replay must pass before writeback<br>constraint_hit_rate must be reported with false_positive_cost<br>conflict actions must route to operator review or protective block | field state-action-reward replay + KG source_basis + governance stage gate | 机制冲突、证据缺口或执行约束不满足时，仲裁器必须保持阻断，不能写执行器。 |
| TEM7_engineering_execution_constraint_feasibility | TE1_end_to_end_low_cost_cyclic_greybox_control, TE5_low_frequency_cycle_window_control, TE6_greybox_multi_agent_safety_arbitration | 不考虑执行器延迟、资源库存、人工复核窗口和安全 SOP 的纯算法动作排序。 | execution_constraint_violation_count, actuator_latency_violation_count, storage_or_reagent_bottleneck_count, operator_review_sla_violation_count, blocked_action_count | no automatic action may bypass actuator/SOP feasibility checks<br>constraint violations must convert to protective block or operator review<br>field replay must include actuator feedback before engineering claim upgrade | engineering constraint replay + actuator feedback + operator review SLA | 执行器、库存、暂存或人工复核约束不满足时，候选动作必须降级为阻断/等待/补件。 |

## 现有技术区别与保护性风险矩阵

说明：该矩阵是 prior-art distinction hypothesis，不是正式检索、法律意见或授权判断。

- 状态：`prior_art_distinction_matrix_ready_as_hypothesis_not_search_or_legal_opinion`
- 区别项：7/7
- 覆盖率：1.0
- 缺失 claim 覆盖：[]
- 缺失 feature 覆盖：[]
- 缺失 effect 覆盖：[]
- 需要正式检索：True
- 允许新颖性/创造性结论：False
- 机器可读矩阵：`outputs/agent_architecture_consolidation/prior_art_distinction_matrix.json`

| 区别项 | 已知方法族 | 区别组合 | 风险 | 从属回退路线 | 边界 |
| --- | --- | --- | --- | --- | --- |
| PAD1_soft_sensor_ml_vs_cyclic_greybox_release_gated_control | wastewater soft sensors, data-driven process monitoring and sensor-limited control | 低成本 node-modality 稀疏观测 + 软传感不确定性 + 灰箱边界 + 回流/暂存争取时间 + field replay/release gate 的组合。 | medium；soft sensors, cyclic reactors and release gates may each be known; protectability depends on whether the constrained combination and evidence-gated action path is sufficiently specific. | 将独立方向收窄到低成本低频观测下的循环窗口、field replay release gate 或 node-modality hidden-state coverage 子组合。 | 未完成正式检索和现场 gate 前，只能作为区别假设，不能写成新颖性/创造性结论。 |
| PAD2_sparse_sensor_placement_vs_node_modality_hidden_state_layout | sparse sensor placement for reconstruction or classification | 把传感位置扩展为 node-modality 矩阵，并把覆盖目标从一般重构转成 pollutant_residual、reaction_completion、catalyst_activity 等隐藏状态及下游控制可用性。 | medium_high；通用稀疏布点方法较成熟；保护点应落在水处理隐藏状态、node-modality 合同和后续 release/holdout gate 的耦合。 | 收窄到 catalyst_activity 弱轴补点、pressure/headloss proxy 与 field missingness replay 的从属方向。 | 无真实拓扑和标签时不能宣称现场布点优于已有稀疏传感方案。 |
| PAD3_marl_pump_coordination_vs_greybox_multi_agent_safety_arbitration | multi-agent reinforcement learning, pump-station coordination and policy distillation | 本项目把多 agent 输出限制在灰箱机理、KG 证据、工程执行约束、operator review 和 field replay 之内，不允许黑箱策略直接写执行器。 | medium；多智能体和策略蒸馏均已有公开方法；保护点应避免泛化到 MARL，本项目应限定为灰箱证据门控的水处理控制仲裁链。 | 收窄到 pressure conflict、catalyst guardrail 或 release gate 下的安全仲裁从属方案。 | 无现场 replay 时不能证明多 agent 仲裁比已有协同控制更优或可部署。 |
| PAD4_flowsheet_optimization_vs_low_cost_observation_gated_greybox_control | water treatment flowsheet modeling, unit-model optimization, TEA/LCA and process constraints | 本项目不是先假设完整高保真参数，而是在低成本观测不足时用软传感和循环窗口形成可校准灰箱，再由 replay/field gate 限制控制动作。 | medium；流程模拟和约束优化已有成熟工具；本项目应突出低成本稀疏观测条件下的循环窗口与证据门控控制链。 | 收窄到低频传感-循环窗口协同控制或工程执行约束仲裁。 | 没有完整工艺参数和现场校准时，不能把灰箱约束写成真实机理论证。 |
| PAD5_scientific_kg_vs_action_constraint_and_claim_gate | scientific knowledge graphs, literature evidence matrices and research-agent claim verification | 本项目把 KG/source_basis 作为控制候选约束、claim gate 和 field validation queue，而不是只做文献摘要或解释文本。 | medium_high；KG 和 claim verification 已是通用科研 AI 方法；保护点应落在水处理控制动作、field validation queue 和 release gate 的耦合。 | 收窄到 KG action constraint patch、claim-specific field package 或 unsupported action 阻断。 | 文献证据只能支撑先验与约束，不能替代现场数据或 claim 成立。 |
| PAD6_ai_catalyst_discovery_vs_operational_catalyst_activity_guardrail | AI-for-science catalyst/material discovery and catalyst process monitoring | 本项目把催化剂活性作为运行过程中的隐藏状态，用低成本代理、压力冲突解除、field proxy holdout 和循环控制决定保护、再生或更换候选。 | medium；催化剂监测和 AI 材料发现均可能已有；保护点应限定在低成本代理、压力冲突解除和再生/更换控制 gate。 | 收窄到 UV254/ORP/pressure_drop/regeneration_event 的代理观测组合和 holdout 保护边界。 | field proxy holdout 未通过前不能触发自动再生/更换，也不能主张现场催化剂控制效果。 |
| PAD7_replay_validation_vs_pressure_resolution_protective_release_gate | offline replay validation, data provenance gates and operational safety review | 本项目把压力源冲突、TODO/template/provenance gate、同批次六表、时间窗、场景语义和下游路由组合成 release 前的保护性证据门。 | medium；单独 replay/provenance gate 风险较高；保护点应集中在水处理压力源冲突解除到 release gate 的装配链。 | 收窄到 pressure-source conflict resolution、R7-to-R8p work package assembly 或 release-block correctness。 | 未通过真实行包、operator review 和 release gate 前，所有 protective writeback 只能是候选或阻断。 |

## 正式检索工作包与 Claim 收窄路线

说明：该矩阵只生成检索任务和 fallback 路线，不是检索结果、法律意见或授权判断。

- 状态：`formal_search_work_packages_ready_not_search_results`
- 工作包：7/7
- 覆盖率：1.0
- 缺失 PAD 覆盖：[]
- 正式检索已完成：False
- 允许法律意见：False
- 机器可读矩阵：`outputs/agent_architecture_consolidation/formal_search_work_packages.json`

| 工作包 | 关联区别项 | 检索目标 | 检索库 | 检索式数 | Claim fallback | 决策规则 |
| --- | --- | --- | --- | ---: | --- | --- |
| FSWP1_cyclic_greybox_soft_sensor_release_gate_search | PAD1_soft_sensor_ml_vs_cyclic_greybox_release_gated_control | 检索低成本/稀疏传感软测量、循环/暂存水处理和 release gate 是否已被组合为灰箱闭环控制。 | CNIPA, Google Patents, Espacenet, WIPO Patentscope, Google Scholar | 8 | 收窄到低频传感-循环窗口协同控制、field replay release gate 或 node-modality hidden-state coverage 子组合。 | 只有检索未发现完整组合，且 field gate 后续可验证时，才保留主方法/系统宽口径；否则转向从属 fallback。 |
| FSWP2_node_modality_sparse_hidden_state_search | PAD2_sparse_sensor_placement_vs_node_modality_hidden_state_layout | 检索稀疏传感布点是否已被限定到水处理 node-modality 矩阵、隐藏状态覆盖和后续软传感/控制 gate。 | Google Patents, Espacenet, CNIPA, IEEE Xplore, Google Scholar, GitHub | 8 | 收窄到 catalyst_activity 弱轴补点、pressure/headloss proxy、regeneration_event 和 field missingness replay。 | 如果 prior art 已公开通用稀疏布点，主张必须落到隐藏状态覆盖、催化剂弱轴和下游 gate 的具体接口。 |
| FSWP3_greybox_multi_agent_safety_arbitration_search | PAD3_marl_pump_coordination_vs_greybox_multi_agent_safety_arbitration | 检索多智能体水处理/泵站协同、离线 RL、策略蒸馏与安全仲裁是否已结合灰箱机理和 field replay 写回边界。 | CNIPA, Google Patents, Espacenet, IEEE Xplore, ACM Digital Library, Google Scholar | 8 | 收窄到 pressure conflict、catalyst guardrail、KG action constraint 或 release gate 下的安全仲裁。 | 已有 MARL/泵站协同不能直接覆盖本项目，除非同时具备灰箱证据门、工程约束和水处理放行 gate。 |
| FSWP4_low_cost_observation_gated_flowsheet_search | PAD4_flowsheet_optimization_vs_low_cost_observation_gated_greybox_control | 检索水处理 flowsheet/优化/成本约束是否已处理低成本观测不足、循环等待和证据门控控制的组合。 | Google Patents, CNIPA, Espacenet, Google Scholar, WaterTAP/QSDsan/Pyomo documentation | 8 | 收窄到低频传感-循环窗口协同控制、执行约束仲裁或 RTD/HRT 证据窗口。 | 如果现有优化模型已覆盖工艺约束，区别点必须保留在低成本观测门控和循环等待窗口。 |
| FSWP5_scientific_kg_action_constraint_claim_gate_search | PAD5_scientific_kg_vs_action_constraint_and_claim_gate | 检索 Scientific KG、文献证据矩阵和 claim verification 是否已作为水处理控制动作约束和 release/claim gate。 | Google Scholar, Google Patents, CNIPA, WIPO Patentscope, Semantic Scholar | 8 | 收窄到 KG action constraint patch、claim-specific field package、unsupported action blocking 或 source_basis-to-field queue。 | KG 本身不保护；只有 KG 边被控制约束、claim gate 和 field validation queue 消费时才保留为技术特征。 |
| FSWP6_operational_catalyst_activity_guardrail_search | PAD6_ai_catalyst_discovery_vs_operational_catalyst_activity_guardrail | 检索 AI 催化剂发现、催化剂活性监测和水处理再生/更换控制是否已结合低成本代理与 field proxy holdout gate。 | Google Scholar, Google Patents, CNIPA, Espacenet, WIPO Patentscope | 8 | 收窄到 UV254/ORP/pressure_drop/regeneration_event 代理组合、pressure source resolution 或 Agent51 field proxy holdout。 | 若已有运行态催化剂活性代理，保护点必须进一步限定到低成本代理组合、冲突解除和再生/更换保护边界。 |
| FSWP7_pressure_resolution_protective_release_gate_search | PAD7_replay_validation_vs_pressure_resolution_protective_release_gate | 检索 replay/provenance/operator review 是否已形成针对水处理压力源冲突解除的保护性 release gate 装配链。 | CNIPA, Google Patents, Espacenet, WIPO Patentscope, Google Scholar | 8 | 收窄到 pressure-source conflict resolution、R7-to-R8p work package assembly、release-block correctness 或 operator-review-before-clearance。 | 已有 replay/provenance 技术不能覆盖本项目，除非也覆盖压力源冲突解除、行包装配和保护性 release gate。 |

## 正式检索结果接收 Schema

说明：该 schema 只定义检索结果如何提交、比对和阻断；不是 prior-art 结果或法律意见。

- 状态：`formal_search_result_intake_schema_ready_waiting_for_external_results`
- Intake schema：7/7
- 覆盖率：1.0
- 缺失 work package 覆盖：[]
- 已提供检索结果：False
- accepted hit 数：0
- 可生成 prior-art 结论：False
- 机器可读 schema：`outputs/agent_architecture_consolidation/formal_search_result_intake_schema.json`

| Intake | 工作包 | 输入工件 | Hit 字段数 | Comparison 字段数 | 阻断条件 |
| --- | --- | --- | ---: | ---: | --- |
| FSRI1_FSWP1_cyclic_greybox_soft_sensor_release_gate_search | FSWP1_cyclic_greybox_soft_sensor_release_gate_search | FSWP1_cyclic_greybox_soft_sensor_release_gate_search_prior_art_hit_table.csv_or_json, FSWP1_cyclic_greybox_soft_sensor_release_gate_search_claim_element_comparison_chart.csv_or_json, FSWP1_cyclic_greybox_soft_sensor_release_gate_search_fallback_claim_scope_recommendation.md_or_json | 18 | 12 | missing publication_or_patent_id or url_or_reference<br>unknown source_database<br>empty matched_claim_elements<br>empty missing_project_elements when overlap_level is full_or_near_full<br>legal opinion text in reviewer fields<br>attempt to set field_claim_upgrade_allowed=true before field validation gates |
| FSRI2_FSWP2_node_modality_sparse_hidden_state_search | FSWP2_node_modality_sparse_hidden_state_search | FSWP2_node_modality_sparse_hidden_state_search_prior_art_hit_table.csv_or_json, FSWP2_node_modality_sparse_hidden_state_search_claim_element_comparison_chart.csv_or_json, FSWP2_node_modality_sparse_hidden_state_search_fallback_claim_scope_recommendation.md_or_json | 18 | 12 | missing publication_or_patent_id or url_or_reference<br>unknown source_database<br>empty matched_claim_elements<br>empty missing_project_elements when overlap_level is full_or_near_full<br>legal opinion text in reviewer fields<br>attempt to set field_claim_upgrade_allowed=true before field validation gates |
| FSRI3_FSWP3_greybox_multi_agent_safety_arbitration_search | FSWP3_greybox_multi_agent_safety_arbitration_search | FSWP3_greybox_multi_agent_safety_arbitration_search_prior_art_hit_table.csv_or_json, FSWP3_greybox_multi_agent_safety_arbitration_search_claim_element_comparison_chart.csv_or_json, FSWP3_greybox_multi_agent_safety_arbitration_search_fallback_claim_scope_recommendation.md_or_json | 18 | 12 | missing publication_or_patent_id or url_or_reference<br>unknown source_database<br>empty matched_claim_elements<br>empty missing_project_elements when overlap_level is full_or_near_full<br>legal opinion text in reviewer fields<br>attempt to set field_claim_upgrade_allowed=true before field validation gates |
| FSRI4_FSWP4_low_cost_observation_gated_flowsheet_search | FSWP4_low_cost_observation_gated_flowsheet_search | FSWP4_low_cost_observation_gated_flowsheet_search_prior_art_hit_table.csv_or_json, FSWP4_low_cost_observation_gated_flowsheet_search_claim_element_comparison_chart.csv_or_json, FSWP4_low_cost_observation_gated_flowsheet_search_fallback_claim_scope_recommendation.md_or_json | 18 | 12 | missing publication_or_patent_id or url_or_reference<br>unknown source_database<br>empty matched_claim_elements<br>empty missing_project_elements when overlap_level is full_or_near_full<br>legal opinion text in reviewer fields<br>attempt to set field_claim_upgrade_allowed=true before field validation gates |
| FSRI5_FSWP5_scientific_kg_action_constraint_claim_gate_search | FSWP5_scientific_kg_action_constraint_claim_gate_search | FSWP5_scientific_kg_action_constraint_claim_gate_search_prior_art_hit_table.csv_or_json, FSWP5_scientific_kg_action_constraint_claim_gate_search_claim_element_comparison_chart.csv_or_json, FSWP5_scientific_kg_action_constraint_claim_gate_search_fallback_claim_scope_recommendation.md_or_json | 18 | 12 | missing publication_or_patent_id or url_or_reference<br>unknown source_database<br>empty matched_claim_elements<br>empty missing_project_elements when overlap_level is full_or_near_full<br>legal opinion text in reviewer fields<br>attempt to set field_claim_upgrade_allowed=true before field validation gates |
| FSRI6_FSWP6_operational_catalyst_activity_guardrail_search | FSWP6_operational_catalyst_activity_guardrail_search | FSWP6_operational_catalyst_activity_guardrail_search_prior_art_hit_table.csv_or_json, FSWP6_operational_catalyst_activity_guardrail_search_claim_element_comparison_chart.csv_or_json, FSWP6_operational_catalyst_activity_guardrail_search_fallback_claim_scope_recommendation.md_or_json | 18 | 12 | missing publication_or_patent_id or url_or_reference<br>unknown source_database<br>empty matched_claim_elements<br>empty missing_project_elements when overlap_level is full_or_near_full<br>legal opinion text in reviewer fields<br>attempt to set field_claim_upgrade_allowed=true before field validation gates |
| FSRI7_FSWP7_pressure_resolution_protective_release_gate_search | FSWP7_pressure_resolution_protective_release_gate_search | FSWP7_pressure_resolution_protective_release_gate_search_prior_art_hit_table.csv_or_json, FSWP7_pressure_resolution_protective_release_gate_search_claim_element_comparison_chart.csv_or_json, FSWP7_pressure_resolution_protective_release_gate_search_fallback_claim_scope_recommendation.md_or_json | 18 | 12 | missing publication_or_patent_id or url_or_reference<br>unknown source_database<br>empty matched_claim_elements<br>empty missing_project_elements when overlap_level is full_or_near_full<br>legal opinion text in reviewer fields<br>attempt to set field_claim_upgrade_allowed=true before field validation gates |

## 正式检索结果验证门

说明：该 gate 验证外部/人工检索结果包的字段、来源、查询 provenance、claim element comparison 和 reviewer 边界；当前没有结果包，因此不会生成 prior-art 结论。

- 状态：`formal_search_result_validation_gate_ready_waiting_for_external_result_package`
- Validation gate：7/7
- 覆盖率：1.0
- 缺失 intake 覆盖：[]
- 已提供结果包：False
- validated hit 数：0
- rejected hit 数：0
- 可生成 prior-art 结论：False
- 机器可读 gate：`outputs/agent_architecture_consolidation/formal_search_result_validation_gate.json`

| Gate | Intake | 工作包 | 来源库 | 查询来源数 | 运行时验证步骤 | Patch outputs |
| --- | --- | --- | --- | ---: | --- | --- |
| FSRG1_FSWP1_cyclic_greybox_soft_sensor_release_gate_search | FSRI1_FSWP1_cyclic_greybox_soft_sensor_release_gate_search | FSWP1_cyclic_greybox_soft_sensor_release_gate_search | CNIPA, Google Patents, Espacenet, WIPO Patentscope, Google Scholar | 9 | load prior_art_hit_table and claim_element_comparison_chart from the linked intake artifacts<br>reject package if required table fields or comparison fields are missing<br>reject hit rows whose linked_work_package_id is not the current work package<br>reject source_database values outside the linked formal search work package search_databases<br>reject matched_query values that are neither generated queries nor reviewer-approved expansions<br>require every accepted hit to state disclosed capabilities and missing project elements<br>require claim element comparisons to cover at least one mapped claim, feature or effect element<br>reject reviewer text that asserts legal conclusion, authorization likelihood or field-supported claim<br>route accepted overlap to claim_scope_decision_options without producing legal opinion | FSWP1_cyclic_greybox_soft_sensor_release_gate_search_missing_required_fields_patch<br>FSWP1_cyclic_greybox_soft_sensor_release_gate_search_source_database_or_query_provenance_patch<br>FSWP1_cyclic_greybox_soft_sensor_release_gate_search_claim_element_comparison_gap_patch<br>FSWP1_cyclic_greybox_soft_sensor_release_gate_search_reviewer_boundary_patch<br>FSWP1_cyclic_greybox_soft_sensor_release_gate_search_claim_scope_fallback_patch |
| FSRG2_FSWP2_node_modality_sparse_hidden_state_search | FSRI2_FSWP2_node_modality_sparse_hidden_state_search | FSWP2_node_modality_sparse_hidden_state_search | Google Patents, Espacenet, CNIPA, IEEE Xplore, Google Scholar, GitHub | 9 | load prior_art_hit_table and claim_element_comparison_chart from the linked intake artifacts<br>reject package if required table fields or comparison fields are missing<br>reject hit rows whose linked_work_package_id is not the current work package<br>reject source_database values outside the linked formal search work package search_databases<br>reject matched_query values that are neither generated queries nor reviewer-approved expansions<br>require every accepted hit to state disclosed capabilities and missing project elements<br>require claim element comparisons to cover at least one mapped claim, feature or effect element<br>reject reviewer text that asserts legal conclusion, authorization likelihood or field-supported claim<br>route accepted overlap to claim_scope_decision_options without producing legal opinion | FSWP2_node_modality_sparse_hidden_state_search_missing_required_fields_patch<br>FSWP2_node_modality_sparse_hidden_state_search_source_database_or_query_provenance_patch<br>FSWP2_node_modality_sparse_hidden_state_search_claim_element_comparison_gap_patch<br>FSWP2_node_modality_sparse_hidden_state_search_reviewer_boundary_patch<br>FSWP2_node_modality_sparse_hidden_state_search_claim_scope_fallback_patch |
| FSRG3_FSWP3_greybox_multi_agent_safety_arbitration_search | FSRI3_FSWP3_greybox_multi_agent_safety_arbitration_search | FSWP3_greybox_multi_agent_safety_arbitration_search | CNIPA, Google Patents, Espacenet, IEEE Xplore, ACM Digital Library, Google Scholar | 9 | load prior_art_hit_table and claim_element_comparison_chart from the linked intake artifacts<br>reject package if required table fields or comparison fields are missing<br>reject hit rows whose linked_work_package_id is not the current work package<br>reject source_database values outside the linked formal search work package search_databases<br>reject matched_query values that are neither generated queries nor reviewer-approved expansions<br>require every accepted hit to state disclosed capabilities and missing project elements<br>require claim element comparisons to cover at least one mapped claim, feature or effect element<br>reject reviewer text that asserts legal conclusion, authorization likelihood or field-supported claim<br>route accepted overlap to claim_scope_decision_options without producing legal opinion | FSWP3_greybox_multi_agent_safety_arbitration_search_missing_required_fields_patch<br>FSWP3_greybox_multi_agent_safety_arbitration_search_source_database_or_query_provenance_patch<br>FSWP3_greybox_multi_agent_safety_arbitration_search_claim_element_comparison_gap_patch<br>FSWP3_greybox_multi_agent_safety_arbitration_search_reviewer_boundary_patch<br>FSWP3_greybox_multi_agent_safety_arbitration_search_claim_scope_fallback_patch |
| FSRG4_FSWP4_low_cost_observation_gated_flowsheet_search | FSRI4_FSWP4_low_cost_observation_gated_flowsheet_search | FSWP4_low_cost_observation_gated_flowsheet_search | Google Patents, CNIPA, Espacenet, Google Scholar, WaterTAP/QSDsan/Pyomo documentation | 9 | load prior_art_hit_table and claim_element_comparison_chart from the linked intake artifacts<br>reject package if required table fields or comparison fields are missing<br>reject hit rows whose linked_work_package_id is not the current work package<br>reject source_database values outside the linked formal search work package search_databases<br>reject matched_query values that are neither generated queries nor reviewer-approved expansions<br>require every accepted hit to state disclosed capabilities and missing project elements<br>require claim element comparisons to cover at least one mapped claim, feature or effect element<br>reject reviewer text that asserts legal conclusion, authorization likelihood or field-supported claim<br>route accepted overlap to claim_scope_decision_options without producing legal opinion | FSWP4_low_cost_observation_gated_flowsheet_search_missing_required_fields_patch<br>FSWP4_low_cost_observation_gated_flowsheet_search_source_database_or_query_provenance_patch<br>FSWP4_low_cost_observation_gated_flowsheet_search_claim_element_comparison_gap_patch<br>FSWP4_low_cost_observation_gated_flowsheet_search_reviewer_boundary_patch<br>FSWP4_low_cost_observation_gated_flowsheet_search_claim_scope_fallback_patch |
| FSRG5_FSWP5_scientific_kg_action_constraint_claim_gate_search | FSRI5_FSWP5_scientific_kg_action_constraint_claim_gate_search | FSWP5_scientific_kg_action_constraint_claim_gate_search | Google Scholar, Google Patents, CNIPA, WIPO Patentscope, Semantic Scholar | 9 | load prior_art_hit_table and claim_element_comparison_chart from the linked intake artifacts<br>reject package if required table fields or comparison fields are missing<br>reject hit rows whose linked_work_package_id is not the current work package<br>reject source_database values outside the linked formal search work package search_databases<br>reject matched_query values that are neither generated queries nor reviewer-approved expansions<br>require every accepted hit to state disclosed capabilities and missing project elements<br>require claim element comparisons to cover at least one mapped claim, feature or effect element<br>reject reviewer text that asserts legal conclusion, authorization likelihood or field-supported claim<br>route accepted overlap to claim_scope_decision_options without producing legal opinion | FSWP5_scientific_kg_action_constraint_claim_gate_search_missing_required_fields_patch<br>FSWP5_scientific_kg_action_constraint_claim_gate_search_source_database_or_query_provenance_patch<br>FSWP5_scientific_kg_action_constraint_claim_gate_search_claim_element_comparison_gap_patch<br>FSWP5_scientific_kg_action_constraint_claim_gate_search_reviewer_boundary_patch<br>FSWP5_scientific_kg_action_constraint_claim_gate_search_claim_scope_fallback_patch |
| FSRG6_FSWP6_operational_catalyst_activity_guardrail_search | FSRI6_FSWP6_operational_catalyst_activity_guardrail_search | FSWP6_operational_catalyst_activity_guardrail_search | Google Scholar, Google Patents, CNIPA, Espacenet, WIPO Patentscope | 9 | load prior_art_hit_table and claim_element_comparison_chart from the linked intake artifacts<br>reject package if required table fields or comparison fields are missing<br>reject hit rows whose linked_work_package_id is not the current work package<br>reject source_database values outside the linked formal search work package search_databases<br>reject matched_query values that are neither generated queries nor reviewer-approved expansions<br>require every accepted hit to state disclosed capabilities and missing project elements<br>require claim element comparisons to cover at least one mapped claim, feature or effect element<br>reject reviewer text that asserts legal conclusion, authorization likelihood or field-supported claim<br>route accepted overlap to claim_scope_decision_options without producing legal opinion | FSWP6_operational_catalyst_activity_guardrail_search_missing_required_fields_patch<br>FSWP6_operational_catalyst_activity_guardrail_search_source_database_or_query_provenance_patch<br>FSWP6_operational_catalyst_activity_guardrail_search_claim_element_comparison_gap_patch<br>FSWP6_operational_catalyst_activity_guardrail_search_reviewer_boundary_patch<br>FSWP6_operational_catalyst_activity_guardrail_search_claim_scope_fallback_patch |
| FSRG7_FSWP7_pressure_resolution_protective_release_gate_search | FSRI7_FSWP7_pressure_resolution_protective_release_gate_search | FSWP7_pressure_resolution_protective_release_gate_search | CNIPA, Google Patents, Espacenet, WIPO Patentscope, Google Scholar | 9 | load prior_art_hit_table and claim_element_comparison_chart from the linked intake artifacts<br>reject package if required table fields or comparison fields are missing<br>reject hit rows whose linked_work_package_id is not the current work package<br>reject source_database values outside the linked formal search work package search_databases<br>reject matched_query values that are neither generated queries nor reviewer-approved expansions<br>require every accepted hit to state disclosed capabilities and missing project elements<br>require claim element comparisons to cover at least one mapped claim, feature or effect element<br>reject reviewer text that asserts legal conclusion, authorization likelihood or field-supported claim<br>route accepted overlap to claim_scope_decision_options without producing legal opinion | FSWP7_pressure_resolution_protective_release_gate_search_missing_required_fields_patch<br>FSWP7_pressure_resolution_protective_release_gate_search_source_database_or_query_provenance_patch<br>FSWP7_pressure_resolution_protective_release_gate_search_claim_element_comparison_gap_patch<br>FSWP7_pressure_resolution_protective_release_gate_search_reviewer_boundary_patch<br>FSWP7_pressure_resolution_protective_release_gate_search_claim_scope_fallback_patch |

## 正式检索结果包模板与 Source Preflight

说明：该层把 validation gate 前移为可提交的 JSON 包合同，并生成可填报 submission skeleton；source preflight 会检查 source/path/root shape 和 TODO/template markers。没有真实结果包时仍保持等待，不生成 prior-art 结论。

- 模板状态：`formal_search_result_package_templates_ready_waiting_for_submission`
- 模板覆盖率：1.0
- Submission skeleton：`formal_search_result_package_submission_template_ready`
- Source preflight：`formal_search_result_package_preflight_waiting_for_submission_path`
- Row preflight：`formal_search_result_package_row_preflight_blocked_at_source_preflight`
- 结果包路径：`FORMAL_SEARCH_RESULT_PACKAGE_PATH`
- Template marker gaps：0
- Row gaps：0
- Comparison coverage gaps：0
- Reviewer boundary gaps：0
- 可进入 validation gate：False
- 行级可进入 validation gate：False
- Validation execution：`formal_search_result_validation_execution_blocked_at_row_preflight`
- Execution validated hit 数：0
- Execution rejected hit 数：0
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
- 可生成 prior-art 结论：False
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

| Template | Gate | 工作包 | 必需表 | 来源库 |
| --- | --- | --- | --- | --- |
| FSRPT1_FSWP1_cyclic_greybox_soft_sensor_release_gate_search | FSRG1_FSWP1_cyclic_greybox_soft_sensor_release_gate_search | FSWP1_cyclic_greybox_soft_sensor_release_gate_search | prior_art_hit_table, claim_element_comparison_chart, fallback_claim_scope_recommendation | CNIPA, Google Patents, Espacenet, WIPO Patentscope, Google Scholar |
| FSRPT2_FSWP2_node_modality_sparse_hidden_state_search | FSRG2_FSWP2_node_modality_sparse_hidden_state_search | FSWP2_node_modality_sparse_hidden_state_search | prior_art_hit_table, claim_element_comparison_chart, fallback_claim_scope_recommendation | Google Patents, Espacenet, CNIPA, IEEE Xplore, Google Scholar, GitHub |
| FSRPT3_FSWP3_greybox_multi_agent_safety_arbitration_search | FSRG3_FSWP3_greybox_multi_agent_safety_arbitration_search | FSWP3_greybox_multi_agent_safety_arbitration_search | prior_art_hit_table, claim_element_comparison_chart, fallback_claim_scope_recommendation | CNIPA, Google Patents, Espacenet, IEEE Xplore, ACM Digital Library, Google Scholar |
| FSRPT4_FSWP4_low_cost_observation_gated_flowsheet_search | FSRG4_FSWP4_low_cost_observation_gated_flowsheet_search | FSWP4_low_cost_observation_gated_flowsheet_search | prior_art_hit_table, claim_element_comparison_chart, fallback_claim_scope_recommendation | Google Patents, CNIPA, Espacenet, Google Scholar, WaterTAP/QSDsan/Pyomo documentation |
| FSRPT5_FSWP5_scientific_kg_action_constraint_claim_gate_search | FSRG5_FSWP5_scientific_kg_action_constraint_claim_gate_search | FSWP5_scientific_kg_action_constraint_claim_gate_search | prior_art_hit_table, claim_element_comparison_chart, fallback_claim_scope_recommendation | Google Scholar, Google Patents, CNIPA, WIPO Patentscope, Semantic Scholar |
| FSRPT6_FSWP6_operational_catalyst_activity_guardrail_search | FSRG6_FSWP6_operational_catalyst_activity_guardrail_search | FSWP6_operational_catalyst_activity_guardrail_search | prior_art_hit_table, claim_element_comparison_chart, fallback_claim_scope_recommendation | Google Scholar, Google Patents, CNIPA, Espacenet, WIPO Patentscope |
| FSRPT7_FSWP7_pressure_resolution_protective_release_gate_search | FSRG7_FSWP7_pressure_resolution_protective_release_gate_search | FSWP7_pressure_resolution_protective_release_gate_search | prior_art_hit_table, claim_element_comparison_chart, fallback_claim_scope_recommendation | CNIPA, Google Patents, Espacenet, WIPO Patentscope, Google Scholar |

## 模块板块

| 模块 | 类型 | Agent 数 | 核心锚点 | 处理策略 |
| --- | --- | ---: | --- | --- |
| M1_sparse_observation_layout 低成本稀疏感知与布点 | core_model | 4 | sensor_network_sparse_placement_agent, catalyst_activity_proxy_agent | keep_as_core_module_with_explicit_io_contract |
| M2_soft_sensor_state_estimation 软传感、缺测矩阵与不确定性 | core_model | 6 | soft_sensor_matrix_coupling_agent | merge_subagents_into_module_interface |
| M3_grey_box_mechanism 灰箱物理、机理解释与故障诊断 | core_model | 7 | minimal_grey_box_physics_agent | merge_subagents_into_module_interface |
| M4_collaborative_control 循环式处理、多设施协同控制与仲裁 | core_model | 8 | multi_facility_collaborative_control_agent, multi_facility_replay_evaluation_agent, engineering_execution_constraint_agent | merge_subagents_into_module_interface |
| M5_kg_claim_evidence 知识图谱、文献证据与 Claim 审查 | core_model | 5 | knowledge_graph_reasoning_agent, claim_specific_field_package_agent | merge_gate_and_claim_evidence_contracts |
| M6_field_evidence_chain 现场数据接口、Replay 与证据门控 | core_model | 7 | timestamped_campaign_replay_agent, field_replay_import_agent, field_replay_evidence_chain_agent | merge_gate_and_claim_evidence_contracts |
| M7_project_operations_support 项目运行、资源调度与实施管理 | support | 18 | - | compress_to_project_operations_support_facade |
| M8_model_governance 模型治理、主链回接与减冗复盘 | governance | 2 | - | keep_as_core_module_with_explicit_io_contract |
| M9_presentation_delivery 展示、文档与汇报材料 | frozen_presentation | 3 | - | freeze_low_priority_until_model_metrics_change |

## 冗余与合并簇

### C1_soft_sensor_validation_cluster

- 类型：merge
- 优先级：high
- Agent：soft_sensor_conformal_calibration_agent, soft_sensor_uncertainty_validation_agent, weak_target_stratified_conformal_agent
- 合并原因：不确定性、保形、弱目标和 field holdout 都在服务同一个 release calibration boundary。
- 合并目标：M2_soft_sensor_state_estimation + M6_field_evidence_chain shared gate contract
- 保留指标：interval_coverage, weak_target_coverage, abstention_rate, field_holdout_gate_pass

### C2_field_evidence_claim_gate_cluster

- 类型：merge
- 优先级：highest
- Agent：claim_specific_field_package_agent, field_calibration_gate_agent, field_replay_calibration_gate_agent, field_validation_queue_alignment_agent, soft_sensor_field_holdout_gate_agent
- 合并原因：field calibration、replay gate、claim package 和 source_basis 阻断都在回答同一件事：哪条 claim 能否升级。
- 合并目标：UnifiedFieldEvidenceGate interface
- 保留指标：field_need_to_gate_coverage, source_basis_completion_rate, evidence_chain_pass, can_write_to_release_gate

### C3_project_operations_cluster

- 类型：compress
- 优先级：medium
- Agent：adaptive_portfolio_agent, campaign_telemetry_agent, control_baseline_update_agent, implementation_stress_test_agent, long_term_economics_agent, online_project_control_agent, operations_scheduling_agent, phased_implementation_agent, post_replan_replay_agent, project_synthesis_agent, queue_planning_agent, recovery_execution_replay_agent, recovery_online_control_agent, recovery_ramp_agent, recovery_strategy_writeback_agent, replanning_orchestrator_agent, resource_expansion_agent, time_budget_recovery_agent
- 合并原因：队列、资源、预算、压力测试、在线重规划和恢复爬坡属于同一实施支持层，不应继续占据核心模型链路。
- 合并目标：ProjectOperationsSupport facade
- 保留指标：campaign_success_rate, resource_bottleneck_count, replan_trigger, recovery_load_fraction

### C4_presentation_freeze_cluster

- 类型：freeze
- 优先级：low
- Agent：deliverable_organization_agent, presentation_asset_agent, presentation_deck_agent
- 合并原因：展示、PPT、Word 和索引不改变模型能力，只有模型指标更新后才同步。
- 合并目标：FrozenPresentationBacklog
- 保留指标：none_for_model_core

### C5_kg_literature_reasoning_cluster

- 类型：merge
- 优先级：high
- Agent：knowledge_graph_curation_agent, literature_evidence_agent
- 合并原因：KG schema、文献证据和 reasoning patch 应共享同一证据记录格式，避免 source_basis 继续只是方法标签。
- 合并目标：M5_kg_claim_evidence source-backed evidence store
- 保留指标：evidence_traceability, constraint_hit_rate, source_basis_completion_rate, field_supported_edge_ratio

## 边界

- 本轮是模型架构复盘与减冗治理，不产生 field-supported 结论。
- 不删除历史代码；先通过模块 facade、统一接口和指标契约压缩复杂度。
- synthetic/sample 仍只能作为仿真基线和接口验证，不能写执行器或 release gate。

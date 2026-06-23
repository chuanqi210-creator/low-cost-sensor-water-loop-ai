from __future__ import annotations

import json
from collections import Counter, defaultdict
from collections.abc import Sequence
from pathlib import Path

from water_ai.agents.base import BaseAgent
from water_ai.domain import AgentReport, QualityIssue, SensorReading, Severity


REQUIRED_ARCHITECTURE_EVIDENCE_FIELDS = (
    "source",
    "method_family",
    "model_mapping",
    "data_needs",
    "implementation_path",
    "evaluation_metrics",
    "failure_boundary",
)

SYSTEM_LAYER_BLUEPRINTS: tuple[dict[str, object], ...] = (
    {
        "layer_id": "L1_field_object_layer",
        "title": "现场对象层",
        "core_question": "污染物、水质基质、处理单元、拓扑和材料/药剂对象是否被明确建模？",
    },
    {
        "layer_id": "L2_observation_layer",
        "title": "观测层",
        "core_question": "低成本传感、稀疏布点、缺测、延迟和节点-模态矩阵是否能支撑隐藏状态估计？",
    },
    {
        "layer_id": "L3_state_estimation_layer",
        "title": "状态估计层",
        "core_question": "软传感、灰箱状态和弱隐藏变量是否有可验证的估计契约？",
    },
    {
        "layer_id": "L4_mechanism_evidence_layer",
        "title": "机理证据层",
        "core_question": "机理解释、知识图谱、文献依据和失败边界是否可追溯？",
    },
    {
        "layer_id": "L5_diagnostic_decision_layer",
        "title": "诊断决策层",
        "core_question": "诊断、故障识别、控制候选、策略解释和人工复核是否形成闭环？",
    },
    {
        "layer_id": "L6_closed_loop_execution_layer",
        "title": "闭环执行层",
        "core_question": "回流、暂存、延长停留、投药、切换单元和保护性阻断是否可执行？",
    },
    {
        "layer_id": "L7_validation_governance_layer",
        "title": "验证治理层",
        "core_question": "field package、replay、holdout、calibration、claim gate 和阶段治理是否能审查结论？",
    },
)


REQUIRED_SYSTEM_ABILITIES = (
    "observability",
    "controllability",
    "explainability",
    "verifiability",
    "engineering_feasibility",
    "evolvability",
)


MODULE_SYSTEM_SPINE_MAP: dict[str, dict[str, object]] = {
    "M1_sparse_observation_layout": {
        "primary_layer": "L2_observation_layer",
        "secondary_layers": ["L1_field_object_layer", "L3_state_estimation_layer"],
        "core_abilities": ["observability", "engineering_feasibility"],
        "spine_role": "把现场对象转成低成本可观测 node-modality 矩阵，是黑箱变灰箱的观测入口。",
    },
    "M2_soft_sensor_state_estimation": {
        "primary_layer": "L3_state_estimation_layer",
        "secondary_layers": ["L2_observation_layer", "L7_validation_governance_layer"],
        "core_abilities": ["observability", "verifiability"],
        "spine_role": "把稀疏观测、缺测和灰箱先验转成可审查的隐藏状态估计。",
    },
    "M3_grey_box_mechanism": {
        "primary_layer": "L4_mechanism_evidence_layer",
        "secondary_layers": ["L3_state_estimation_layer", "L5_diagnostic_decision_layer"],
        "core_abilities": ["explainability", "verifiability"],
        "spine_role": "把软传感状态连接到反应、基质、催化剂、水力和副产物风险解释。",
    },
    "M4_collaborative_control": {
        "primary_layer": "L5_diagnostic_decision_layer",
        "secondary_layers": ["L6_closed_loop_execution_layer", "L7_validation_governance_layer"],
        "core_abilities": ["controllability", "explainability", "verifiability"],
        "spine_role": "把诊断状态转成可回放、可解释、可阻断的联动动作候选。",
    },
    "M5_kg_claim_evidence": {
        "primary_layer": "L4_mechanism_evidence_layer",
        "secondary_layers": ["L1_field_object_layer", "L7_validation_governance_layer"],
        "core_abilities": ["explainability", "verifiability"],
        "spine_role": "把污染物、材料、工况、动作和风险连接成可追溯证据路径。",
    },
    "M6_field_evidence_chain": {
        "primary_layer": "L7_validation_governance_layer",
        "secondary_layers": ["L2_observation_layer", "L5_diagnostic_decision_layer"],
        "core_abilities": ["verifiability", "engineering_feasibility"],
        "spine_role": "把真实数据接口、replay、holdout 和 claim gate 转成现场证据升级链。",
    },
    "M7_project_operations_support": {
        "primary_layer": "L6_closed_loop_execution_layer",
        "secondary_layers": ["L1_field_object_layer", "L7_validation_governance_layer"],
        "core_abilities": ["engineering_feasibility", "controllability"],
        "spine_role": "把队列、资源、预算、恢复爬坡和执行组织压缩成工程实施支持层。",
    },
    "M8_model_governance": {
        "primary_layer": "L7_validation_governance_layer",
        "secondary_layers": [],
        "core_abilities": ["evolvability", "verifiability"],
        "spine_role": "检查新增能力是否回接主链、是否需要合并、冻结或重排。",
    },
    "M9_presentation_delivery": {
        "primary_layer": "OUTSIDE_MODEL_SPINE",
        "secondary_layers": [],
        "core_abilities": [],
        "spine_role": "表达层，不增强系统骨架；冻结为低优先级，仅在模型指标变化后同步。",
    },
}

REQUIRED_MODULE_INTERFACE_FIELDS = (
    "input_contract",
    "output_contract",
    "state_variables",
    "evidence_sources",
    "transferable_metrics",
    "cannot_do",
    "upstream_dependencies",
    "downstream_consumers",
    "field_validation_need",
)

REQUIRED_PATENT_TECHNICAL_FEATURE_FIELDS = (
    "feature_id",
    "module_id",
    "mapped_layers",
    "core_abilities",
    "technical_problem",
    "technical_means",
    "system_structure",
    "state_variables",
    "control_actions",
    "implementation_example",
    "verification_metrics",
    "technical_effect",
    "prior_art_distinction",
    "claim_skeleton_role",
    "evidence_boundary",
    "field_validation_gate",
    "failure_boundary",
    "protectability_note",
)

REQUIRED_TECHNICAL_CLAIM_SCAFFOLD_FIELDS = (
    "claim_id",
    "claim_type",
    "claim_title",
    "mapped_feature_ids",
    "required_layers",
    "technical_problem",
    "technical_combination",
    "method_steps",
    "system_components",
    "state_variables",
    "control_actions",
    "verification_gates",
    "technical_effect",
    "prior_art_distinction",
    "evidence_boundary",
    "failure_boundary",
    "legal_status",
)

REQUIRED_TECHNICAL_EMBODIMENT_FIELDS = (
    "embodiment_id",
    "embodiment_title",
    "linked_claim_ids",
    "linked_feature_ids",
    "scenario",
    "source_package_requirements",
    "required_tables_or_artifacts",
    "step_sequence",
    "validation_gates",
    "acceptance_metrics",
    "technical_effect_to_measure",
    "current_evidence_status",
    "failure_boundary",
    "field_claim_upgrade_allowed",
)

REQUIRED_TECHNICAL_EFFECT_MEASUREMENT_FIELDS = (
    "effect_id",
    "linked_embodiment_ids",
    "linked_claim_ids",
    "linked_feature_ids",
    "effect_statement",
    "baseline_comparator",
    "measurement_metrics",
    "acceptance_thresholds",
    "required_evidence_tiers",
    "current_evidence_status",
    "validation_gate",
    "failure_boundary",
    "field_claim_upgrade_allowed",
    "can_write_to_actuator",
    "can_write_to_release_gate",
)

REQUIRED_PRIOR_ART_DISTINCTION_FIELDS = (
    "distinction_id",
    "mapped_claim_ids",
    "mapped_feature_ids",
    "mapped_effect_ids",
    "prior_art_family",
    "representative_sources",
    "known_prior_capability",
    "distinguishing_combination",
    "why_not_generic_ai_or_control",
    "technical_problem_addressed",
    "required_embodiments",
    "measurable_effects",
    "evidence_status",
    "novelty_risk_level",
    "combination_risk",
    "dependent_fallback_path",
    "verification_needed",
    "legal_status",
    "formal_search_required",
    "field_claim_upgrade_allowed",
    "failure_boundary",
)

REQUIRED_FORMAL_SEARCH_WORK_PACKAGE_FIELDS = (
    "work_package_id",
    "linked_distinction_ids",
    "mapped_claim_ids",
    "mapped_feature_ids",
    "mapped_effect_ids",
    "search_objective",
    "search_databases",
    "english_search_queries",
    "chinese_search_queries",
    "classification_hints",
    "evidence_to_collect",
    "negative_evidence_checks",
    "claim_fallback_if_prior_art_found",
    "field_validation_gate_to_preserve",
    "decision_rule",
    "expected_output_artifacts",
    "formal_search_required",
    "formal_search_completed",
    "legal_opinion_allowed",
    "field_claim_upgrade_allowed",
    "failure_boundary",
)

PRIOR_ART_HIT_TABLE_FIELDS = (
    "hit_id",
    "linked_work_package_id",
    "source_database",
    "publication_or_patent_id",
    "title",
    "assignee_or_authors",
    "publication_date",
    "url_or_reference",
    "matched_query",
    "matched_claim_elements",
    "disclosed_capabilities",
    "missing_project_elements",
    "overlap_level",
    "novelty_risk_signal",
    "combination_risk_signal",
    "reviewer_id",
    "review_status",
    "legal_status",
)

CLAIM_ELEMENT_COMPARISON_FIELDS = (
    "comparison_id",
    "linked_hit_id",
    "linked_work_package_id",
    "claim_or_feature_element",
    "project_element_text",
    "prior_art_disclosure_text",
    "match_level",
    "missing_or_distinguishing_detail",
    "fallback_claim_scope_impact",
    "field_validation_gate_to_preserve",
    "reviewer_decision",
    "legal_status",
)

REQUIRED_FORMAL_SEARCH_RESULT_INTAKE_FIELDS = (
    "intake_id",
    "linked_work_package_id",
    "linked_distinction_ids",
    "mapped_claim_ids",
    "mapped_feature_ids",
    "mapped_effect_ids",
    "required_hit_table_fields",
    "required_claim_element_comparison_fields",
    "required_reviewer_fields",
    "input_artifacts",
    "acceptance_checks",
    "blocking_conditions",
    "minimum_evidence_to_accept_hit",
    "claim_scope_decision_options",
    "field_validation_gate_to_preserve",
    "formal_search_result_supplied",
    "accepted_hit_count",
    "can_generate_prior_art_result",
    "legal_opinion_allowed",
    "field_claim_upgrade_allowed",
    "failure_boundary",
)

REQUIRED_FORMAL_SEARCH_RESULT_VALIDATION_GATE_FIELDS = (
    "validation_gate_id",
    "linked_intake_id",
    "linked_work_package_id",
    "linked_distinction_ids",
    "mapped_claim_ids",
    "mapped_feature_ids",
    "mapped_effect_ids",
    "accepted_input_artifacts",
    "allowed_source_databases",
    "allowed_query_sources",
    "hit_table_required_fields",
    "comparison_chart_required_fields",
    "runtime_validation_steps",
    "blocking_conditions",
    "patch_plan_outputs",
    "prior_art_result_generation_rule",
    "formal_search_result_package_supplied",
    "validated_hit_count",
    "rejected_hit_count",
    "can_generate_prior_art_result",
    "legal_opinion_allowed",
    "field_claim_upgrade_allowed",
    "failure_boundary",
    "validation_gate_status",
)

REQUIRED_FORMAL_SEARCH_RESULT_PACKAGE_TEMPLATE_FIELDS = (
    "package_template_id",
    "linked_validation_gate_id",
    "linked_intake_id",
    "linked_work_package_id",
    "mapped_claim_ids",
    "mapped_feature_ids",
    "mapped_effect_ids",
    "package_root_key",
    "package_manifest_required_fields",
    "required_result_tables",
    "prior_art_hit_table_template_fields",
    "claim_element_comparison_template_fields",
    "fallback_recommendation_fields",
    "allowed_source_databases",
    "allowed_query_sources",
    "row_level_rejection_rules",
    "validation_command",
    "package_template_status",
    "formal_search_result_package_supplied",
    "can_route_to_validation_gate",
    "can_generate_prior_art_result",
    "legal_opinion_allowed",
    "field_claim_upgrade_allowed",
    "failure_boundary",
)

FORBIDDEN_PRIOR_ART_REVIEW_TERMS = (
    "legal opinion",
    "novelty conclusion",
    "inventiveness conclusion",
    "patentable",
    "grant likely",
    "authorization likelihood",
    "field-supported claim",
    "法律意见",
    "新颖性结论",
    "创造性结论",
    "可授权",
    "授权可能",
    "现场成立",
)

REQUIRED_FORMAL_SEARCH_RESULT_SUBMISSION_TEMPLATE_FIELDS = (
    "submission_template_status",
    "expected_env_var",
    "recommended_output_path",
    "package_metadata",
    "work_package_results",
    "expected_work_package_ids",
    "required_result_tables",
    "template_marker_policy",
    "can_route_to_validation_gate",
    "can_generate_prior_art_result",
    "legal_opinion_allowed",
    "field_claim_upgrade_allowed",
    "failure_boundary",
)

NONLEGAL_REVIEW_RESPONSE_FIELDS = (
    "review_packet_row_id",
    "linked_work_package_id",
    "hit_id",
    "reviewer_id",
    "review_time",
    "nonlegal_overlap_assessment",
    "distinguishing_technical_detail",
    "fallback_scope_recommendation",
    "preserved_field_validation_gate",
    "evidence_boundary_acknowledgement",
    "reviewer_signature_or_trace_id",
    "legal_status",
)

FORMAL_COUNSEL_REVIEW_RESPONSE_FIELDS = (
    "claim_scope_patch_id",
    "review_packet_row_id",
    "linked_work_package_id",
    "hit_id",
    "formal_reviewer_id",
    "review_time",
    "scope_review_disposition",
    "approved_technical_revision_summary",
    "required_disclosure_revision",
    "preserved_field_validation_gate",
    "required_followup_search_or_evidence",
    "boundary_acknowledgement",
    "formal_review_trace_id",
    "legal_status",
)

FORBIDDEN_FORMAL_COUNSEL_ROUTING_TERMS = (
    "novelty conclusion",
    "inventiveness conclusion",
    "legal conclusion",
    "patentable",
    "grant likely",
    "authorization likelihood",
    "field-supported claim",
    "新颖性结论",
    "创造性结论",
    "法律结论",
    "可授权",
    "授权可能",
    "现场成立",
)


MODULE_INTERFACE_CONTRACTS: dict[str, dict[str, object]] = {
    "M1_sparse_observation_layout": {
        "input_contract": "污染场景、处理单元/管网拓扑候选、低成本传感候选、安装/维护成本、节点-模态可用性。",
        "output_contract": "node-modality 观测矩阵、候选布点方案、弱隐藏状态覆盖、成本约束和软传感输入先验。",
        "state_variables": ["observable_nodes", "modalities", "weak_state_coverage", "cost_index", "topology_prior"],
        "evidence_sources": ["candidate sensor table", "synthetic topology prior", "future field topology", "node-specific field labels"],
        "transferable_metrics": ["weak_state_coverage", "soft_sensor_reconstruction_gain", "total_cost_index", "single_point_dependency"],
        "cannot_do": "不能仅靠加点位宣称现场可观测；无真实拓扑/标签时不能作为部署结论。",
        "upstream_dependencies": ["field_object_definition", "sensor_cost_catalog", "site_topology_or_bed_geometry"],
        "downstream_consumers": ["M2_soft_sensor_state_estimation", "M4_collaborative_control", "M6_field_evidence_chain"],
        "field_validation_need": "真实拓扑、水力停留时间、安装可达性、节点级时间序列和弱状态离线标签。",
    },
    "M2_soft_sensor_state_estimation": {
        "input_contract": "node-modality 观测矩阵、缺测 mask、低频/延迟特征、灰箱先验、离线标签和 field holdout split。",
        "output_contract": "隐藏状态估计、预测区间、缺测鲁棒性、OOD/abstention 标志和 release 前不确定性边界。",
        "state_variables": ["pollutant_residual", "reaction_completion", "matrix_interference", "catalyst_activity", "uncertainty_interval"],
        "evidence_sources": ["synthetic holdout", "offline lab labels", "field holdout", "missingness replay"],
        "transferable_metrics": ["masked_mae", "interval_coverage", "missingness_robustness_score", "field_holdout_gate_pass"],
        "cannot_do": "不能把 synthetic dropout 或模板 holdout 写成现场缺测鲁棒性结论。",
        "upstream_dependencies": ["M1_sparse_observation_layout", "M3_grey_box_mechanism", "offline_lab_results"],
        "downstream_consumers": ["M3_grey_box_mechanism", "M4_collaborative_control", "M6_field_evidence_chain"],
        "field_validation_need": "真实 field holdout、节点级缺测原因、低频采样延迟和目标污染物/弱状态标签。",
    },
    "M3_grey_box_mechanism": {
        "input_contract": "软传感状态、反应/传质先验、RTD/停留时间、催化剂历史、基质信息和副产物风险标签。",
        "output_contract": "灰箱残差、机理假设、故障模式、反应/水力/催化剂边界和可解释控制约束。",
        "state_variables": ["k_eff", "mass_balance_residual", "hydraulic_delay", "catalyst_decay", "byproduct_risk"],
        "evidence_sources": ["literature priors", "synthetic mechanism stress", "future field RTD", "offline pollutant/byproduct panels"],
        "transferable_metrics": ["grey_box_residual", "mass_balance_residual", "mechanism_hypothesis_count", "fault_mode_coverage"],
        "cannot_do": "不能把未校准灰箱参数当成现场机理结论或放行依据。",
        "upstream_dependencies": ["M2_soft_sensor_state_estimation", "M5_kg_claim_evidence", "field RTD and lab panels"],
        "downstream_consumers": ["M4_collaborative_control", "M5_kg_claim_evidence", "M6_field_evidence_chain"],
        "field_validation_need": "现场 RTD、池容/流量、进出水污染物、氧化剂余量、催化剂再生历史和副产物面板。",
    },
    "M4_collaborative_control": {
        "input_contract": "状态估计、灰箱边界、工程约束、候选动作、reward prior、多节点 replay schema 和人工复核规则。",
        "output_contract": "联合动作候选、保护性阻断、回流/暂存/投药/切换建议、策略解释和不可写执行器边界。",
        "state_variables": ["facility_state", "joint_action", "reward_components", "guardrail_context", "operator_review_required"],
        "evidence_sources": ["synthetic replay", "counterfactual stress", "future field state-action-reward replay", "operator review log"],
        "transferable_metrics": ["joint_action_accuracy", "reward_regret", "distilled_policy_accuracy", "false_positive_cost"],
        "cannot_do": "无真实多节点 replay 和人工复核门时不能写执行器或 release gate。",
        "upstream_dependencies": ["M2_soft_sensor_state_estimation", "M3_grey_box_mechanism", "M6_field_evidence_chain"],
        "downstream_consumers": ["M6_field_evidence_chain", "M7_project_operations_support"],
        "field_validation_need": "真实多节点 sensor/lab/operation/action/reward replay、PLC/SCADA 点表、SOP 和执行反馈。",
    },
    "M5_kg_claim_evidence": {
        "input_contract": "污染物、材料、工况、过程机制、低成本信号、文献 source_basis 和 field validation needs。",
        "output_contract": "typed KG edge、evidence path、claim constraint、source_basis detail 和 field validation queue。",
        "state_variables": ["evidence_edge", "claim_status", "source_basis_detail", "constraint_hit", "field_supported_edge"],
        "evidence_sources": ["literature records", "source_basis library", "KG reasoning patch", "future field-supported edges"],
        "transferable_metrics": ["evidence_traceability", "constraint_hit_rate", "source_basis_completion_rate", "field_supported_edge_ratio"],
        "cannot_do": "不能把文献依据或 KG 推理当成现场支持结论。",
        "upstream_dependencies": ["field object taxonomy", "literature evidence matrix", "M3_grey_box_mechanism"],
        "downstream_consumers": ["M3_grey_box_mechanism", "M4_collaborative_control", "M6_field_evidence_chain"],
        "field_validation_need": "可追溯 citation、参数/适用边界、claim-specific 现场字段和 field-supported KG edges。",
    },
    "M6_field_evidence_chain": {
        "input_contract": "metadata、sensor/lab/operation/proxy/replay CSV、field origin、timestamp alignment、holdout 和 calibration records。",
        "output_contract": "import gate、timestamped replay、evidence chain、claim gate、field package patch plan 和升级/阻断结论。",
        "state_variables": ["field_import_pass", "evidence_chain_pass", "claim_gate_status", "replay_contract_status", "field_supported_claim"],
        "evidence_sources": ["real field package", "timestamped replay", "field holdout", "operator calibration", "source_basis detail"],
        "transferable_metrics": ["field_replay_import_pass", "field_need_to_gate_coverage", "evidence_chain_pass", "can_write_to_release_gate"],
        "cannot_do": "不能把 header-only/template package 或 synthetic replay 当成 field evidence。",
        "upstream_dependencies": ["M1_sparse_observation_layout", "M2_soft_sensor_state_estimation", "M4_collaborative_control", "M5_kg_claim_evidence"],
        "downstream_consumers": ["M4_collaborative_control", "M8_model_governance"],
        "field_validation_need": "data_origin=field 的完整 metadata/CSV、共同 batch、时间顺序、QA 通过标签和人工复核记录。",
    },
    "M7_project_operations_support": {
        "input_contract": "批次、队列、资源、库存、预算、执行时间、恢复爬坡和现场作业约束。",
        "output_contract": "项目运行计划、资源瓶颈、重规划触发、恢复策略和工程实施支持信号。",
        "state_variables": ["campaign_queue", "resource_capacity", "replan_trigger", "recovery_load_fraction", "deployment_budget"],
        "evidence_sources": ["operations log", "resource plan", "cost catalog", "future execution replay"],
        "transferable_metrics": ["campaign_success_rate", "resource_bottleneck_count", "replan_trigger", "recovery_load_fraction"],
        "cannot_do": "不能压过模型核心链路，也不能替代状态估计、控制 replay 或 field claim gate。",
        "upstream_dependencies": ["M4_collaborative_control", "M6_field_evidence_chain", "site operations records"],
        "downstream_consumers": ["M8_model_governance", "implementation planning"],
        "field_validation_need": "真实运行排班、资源成本、执行时间、故障恢复和人工操作记录。",
    },
    "M8_model_governance": {
        "input_contract": "全局 goal、模块指标、agent audit、evidence matrix、backlog、stage gate 和 regression results。",
        "output_contract": "优先级排序、骨架覆盖、接口缺口、冗余合并建议、冻结策略和下一步核心动作。",
        "state_variables": ["system_spine_status", "interface_contract_coverage", "consolidation_score", "self_interrupt_verdict", "fallback_action"],
        "evidence_sources": ["module reports", "manifest", "test results", "artifact index", "external architecture evidence"],
        "transferable_metrics": ["main_chain_prior_consumption_rate", "mapped_agent_count", "redundancy_cluster_count", "system_spine_coverage"],
        "cannot_do": "治理层不能替代模型能力、现场验证或执行器授权。",
        "upstream_dependencies": ["all core modules", "global goal", "test/regression outputs"],
        "downstream_consumers": ["all module owners", "future refactor work"],
        "field_validation_need": "不直接产生 field evidence；只检查 field evidence 的路径、门控和边界。",
    },
    "M9_presentation_delivery": {
        "input_contract": "已验证或明确标注边界的模型结果、图表、报告摘要和用户汇报需求。",
        "output_contract": "文档、PPT、索引和展示材料。",
        "state_variables": ["deliverable_status", "artifact_index_status"],
        "evidence_sources": ["generated artifacts", "render checks"],
        "transferable_metrics": ["artifact_availability"],
        "cannot_do": "不能改变模型结论，不能制造 field-supported claim，不能作为核心优化中心。",
        "upstream_dependencies": ["M8_model_governance", "validated model outputs"],
        "downstream_consumers": ["human presentation only"],
        "field_validation_need": "无；仅表达层。需要同步模型边界而不是产生现场证据。",
    },
}

PATENT_TECHNICAL_FEATURE_BLUEPRINTS: tuple[dict[str, object], ...] = (
    {
        "feature_id": "PTF1_node_modality_sparse_sensing",
        "module_id": "M1_sparse_observation_layout",
        "technical_problem": "低成本现场只能布设少量 pH/ORP/电导/浊度/UV254/流量等传感器，中间反应过程仍接近黑箱。",
        "technical_means": "构建 node-modality 稀疏感知矩阵，把节点、传感模态、安装成本、缺测风险和隐藏状态覆盖统一评分。",
        "system_structure": "污染场景与处理拓扑输入后，输出候选布点、弱状态覆盖、单点依赖和软传感输入先验。",
        "control_actions": ["选择布点组合", "标记弱观测轴", "触发催化剂活性代理补点", "保留未验证保护边界"],
        "implementation_example": "在催化剂床进出口和末端单元布设 UV254/ORP/压降代理，形成 N3 catalyst bed 的低成本观测合同。",
        "verification_metrics": ["weak_state_coverage", "matrix_rank", "condition_number_proxy", "single_point_dependency"],
        "technical_effect": "用有限传感预算提升关键隐藏状态可估计性，并把不能观测的轴显式转入补证据队列。",
        "prior_art_distinction": "区别于只按经验选点或只建黑箱预测模型，本特征把布点、隐藏状态覆盖和后续软传感/控制接口绑定。",
        "claim_skeleton_role": "主权利要求中的稀疏感知输入构建步骤；可作为 node-modality 布点从属特征。",
        "evidence_boundary": "当前可作为 synthetic/design-prior 与接口验证；真实部署仍需 field topology、安装可达性和节点标签。",
        "field_validation_gate": "R7/R8p field package 中的 node_modality_sensor_timeseries、site_topology_or_bed_geometry 和离线标签。",
        "failure_boundary": "无真实拓扑和弱状态标签时不能声称现场最优布点或现场可观测性达标。",
        "protectability_note": "保护重点不是“使用传感器”，而是受成本约束的 node-modality 矩阵、弱状态覆盖和下游软传感接口组合。",
    },
    {
        "feature_id": "PTF2_soft_sensor_grey_state_estimation",
        "module_id": "M2_soft_sensor_state_estimation",
        "technical_problem": "低频、延迟和缺测传感无法直接测得残留污染物、反应完成度、催化剂活性和副产物风险。",
        "technical_means": "以稀疏传感矩阵、缺测 mask、时间延迟、灰箱先验和离线标签训练软传感器，并输出不确定性和 abstention 标志。",
        "system_structure": "观测层输出进入状态估计层，生成隐藏状态、预测区间、缺测鲁棒性和放行前风险边界。",
        "control_actions": ["估计隐藏状态", "输出不确定性", "触发暂存等待", "阻断 release gate", "要求人工复核"],
        "implementation_example": "当 UV254/ORP/压降代理不足以确认催化剂活性时，软传感器输出高不确定性并维持催化剂保护规则。",
        "verification_metrics": ["masked_mae", "interval_coverage", "missingness_robustness_score", "field_holdout_gate_pass"],
        "technical_effect": "把不可直接观测的黑箱状态转成可审查的灰箱估计，同时防止低置信估计直接驱动放行。",
        "prior_art_distinction": "区别于只输出点预测的 ML 软测量，本特征把缺测、低频、灰箱先验、不确定性和 release gate 绑定。",
        "claim_skeleton_role": "主权利要求中的隐藏状态估计步骤；可作为软传感/不确定性从属特征。",
        "evidence_boundary": "synthetic dropout 或模板 holdout 只能证明接口可运行，不能替代真实 field holdout。",
        "field_validation_gate": "field holdout、离线实验标签、真实缺测 replay 和 operator-reviewed release decision。",
        "failure_boundary": "预测区间未校准或 OOD 标志触发时，不能放松保护性阻断。",
        "protectability_note": "保护重点是低成本稀疏观测到隐藏过程状态的灰箱估计链，而不是泛称软传感算法。",
    },
    {
        "feature_id": "PTF3_grey_box_mechanism_boundary",
        "module_id": "M3_grey_box_mechanism",
        "technical_problem": "单纯预测无法解释为何需要回流、延长停留、补药、再生催化剂或阻断放行。",
        "technical_means": "引入反应动力学、质量守恒、水力延迟、催化剂衰减、基质抑制和副产物风险等灰箱边界。",
        "system_structure": "状态估计输出与机理证据层耦合，形成故障模式、机理假设和控制约束补丁。",
        "control_actions": ["解释故障模式", "约束投药/回流动作", "触发催化剂再生或更换候选", "生成保护性阻断"],
        "implementation_example": "当压降冲突和催化剂代理标签不一致时，系统要求 operator review 并保持水力/催化剂保护边界。",
        "verification_metrics": ["grey_box_residual", "mass_balance_residual", "fault_mode_coverage", "resolved_case_to_mechanism_coverage"],
        "technical_effect": "让控制动作能够回到反应、水力和催化剂机制，而不是只依赖黑箱分数。",
        "prior_art_distinction": "区别于纯机器学习过程模拟，本特征把机制残差、故障边界和控制动作候选联动。",
        "claim_skeleton_role": "主权利要求中的灰箱机理约束步骤；可作为催化剂活性/水力延迟从属特征。",
        "evidence_boundary": "未由现场 RTD、污染物面板和催化剂历史校准前，灰箱参数只能作为先验。",
        "field_validation_gate": "field RTD、进出水污染物、副产物面板、催化剂再生记录和 pressure_source_resolution。",
        "failure_boundary": "机理证据冲突未解决时不能升级控制策略或解除保护。",
        "protectability_note": "保护重点是灰箱机理边界对诊断和闭环动作的约束关系，而不是泛称机理解释。",
    },
    {
        "feature_id": "PTF4_cyclic_low_frequency_control",
        "module_id": "M4_collaborative_control",
        "technical_problem": "低成本传感速度慢、采样少，传统一次通过式处理难以及时判断是否达标。",
        "technical_means": "利用循环、暂存、延长停留和多设施协同控制，为软传感、诊断和人工复核争取时间窗口。",
        "system_structure": "诊断决策层生成联合动作候选，闭环执行层执行回流、暂存、投药、切换单元和 release gate 阻断。",
        "control_actions": ["回流", "延长停留时间", "暂存等待", "调整投药", "切换处理单元", "催化剂再生/更换", "放行或阻断"],
        "implementation_example": "当低频代理显示 matrix shock 且软传感不确定性高时，系统选择暂存等待和再测，而不是立即放行。",
        "verification_metrics": ["joint_action_accuracy", "reward_regret", "false_positive_cost", "release_block_correctness"],
        "technical_effect": "通过循环窗口降低对高速昂贵传感器的依赖，并把控制动作变成可回退、可解释的工程动作。",
        "prior_art_distinction": "区别于实时高频全量传感控制，本特征把低频感知约束与循环式处理结构协同设计。",
        "claim_skeleton_role": "主权利要求中的闭环控制步骤；可作为低频传感-循环窗口协同控制从属特征。",
        "evidence_boundary": "synthetic replay 只能证明控制候选逻辑，不能写真实执行器或 release gate。",
        "field_validation_gate": "多节点 state-action-reward replay、operator review、actuator latency、R8v routing 和 field holdout。",
        "failure_boundary": "无真实 replay 和人工复核时，联合动作只能是候选，不能作为自动执行策略。",
        "protectability_note": "保护重点是低频观测、循环缓冲和动作仲裁的组合技术路线。",
    },
    {
        "feature_id": "PTF5_mechanism_kg_evidence_constraint",
        "module_id": "M5_kg_claim_evidence",
        "technical_problem": "材料、污染物、工况和低成本信号之间的证据分散，容易让模型生成不可追溯 claim。",
        "technical_means": "构建 typed KG 和 source_basis，把污染物、材料、过程条件、低成本信号、隐藏状态、动作和风险连接为证据路径。",
        "system_structure": "机理证据层向状态估计和控制层输出 action constraint patch、field validation queue 和 claim evidence boundary。",
        "control_actions": ["约束控制候选", "触发必采字段", "阻断无证据 claim", "标记文献支持与现场支持边界"],
        "implementation_example": "PFAS/抗生素/染料等污染场景进入知识图谱后，系统只允许在 source_basis 覆盖的工况范围内生成处理建议。",
        "verification_metrics": ["evidence_traceability", "constraint_hit_rate", "source_basis_completion_rate", "field_supported_edge_ratio"],
        "technical_effect": "让多智能体诊断和控制动作具有证据路径，减少无依据扩展。",
        "prior_art_distinction": "区别于只堆论文摘要，本特征把 KG 证据转成可传递控制约束和现场验证字段。",
        "claim_skeleton_role": "从属权利要求中的机理证据约束与 claim gate 特征。",
        "evidence_boundary": "literature-supported 和 KG-inferred 不能等同于 field-supported。",
        "field_validation_gate": "source_basis detail、claim-specific field package、field-supported KG edge 和 evidence chain pass。",
        "failure_boundary": "source_basis 不完整或参数超出文献边界时，不能升级为强 claim。",
        "protectability_note": "保护重点是证据图谱到控制约束/验证字段的转化，不是泛称知识图谱。",
    },
    {
        "feature_id": "PTF6_field_replay_release_gate",
        "module_id": "M6_field_evidence_chain",
        "technical_problem": "仿真、模板和真实现场数据混杂时，系统可能错误地把可运行流程当成现场有效。",
        "technical_means": "建立 field package、timestamped replay、holdout、operator review、calibration 和 release gate 的分级证据链。",
        "system_structure": "验证治理层接收 metadata/CSV、共同 batch、时间顺序、行级 provenance 和 replay 输出，决定 claim 升级或阻断。",
        "control_actions": ["导入真实包", "运行 replay", "执行 holdout", "要求 calibration", "阻断 claim upgrade", "允许或拒绝 release gate"],
        "implementation_example": "R7-to-R8p work package 通过 preflight 后，仍必须经 R8p schema/provenance/template/bundle/temporal/semantic gates 和 R8v routing。",
        "verification_metrics": ["field_replay_import_pass", "evidence_chain_pass", "claim_gate_status", "can_write_to_release_gate"],
        "technical_effect": "把证据等级从 synthetic/template/literature/field/operator-reviewed/release-gated 明确分层，降低误放行风险。",
        "prior_art_distinction": "区别于只报告模型精度，本特征把现场证据升级路径和保护性写回边界作为系统组成。",
        "claim_skeleton_role": "主权利要求中的验证治理与保护性控制写回步骤；也可形成现场 replay 分案。",
        "evidence_boundary": "header-only、template、sample 或 synthetic replay 均不能替代 data_origin=field。",
        "field_validation_gate": "R7 import、R8p/R8v gates、field holdout、Agent51/49/52/R7 evidence chain 和人工复核。",
        "failure_boundary": "任一必需 gate 阻断时，不能写 actuator、release gate 或 field-supported claim。",
        "protectability_note": "保护重点是现场 replay 证据门控与保护性写回之间的硬连接。",
    },
    {
        "feature_id": "PTF7_engineering_execution_constraints",
        "module_id": "M7_project_operations_support",
        "technical_problem": "即使模型给出动作，现场仍受泵阀、药剂、库存、人工、延迟和恢复爬坡限制。",
        "technical_means": "把资源、成本、执行延迟、恢复爬坡和 SOP 约束作为控制 reward、仲裁和实施计划的硬边界。",
        "system_structure": "闭环执行层与项目运行支持层共享执行约束，向控制策略输出不可行动作、成本惩罚和重规划触发。",
        "control_actions": ["限制不可执行动作", "触发重规划", "调整恢复爬坡", "约束投药/回流执行时序"],
        "implementation_example": "当泵阀响应超过允许延迟或暂存容量不足时，系统不允许选择需要快速切换的策略。",
        "verification_metrics": ["resource_bottleneck_count", "replan_trigger", "recovery_load_fraction", "execution_constraint_violation_count"],
        "technical_effect": "提高控制候选的工程可执行性，避免算法策略与现场执行条件脱节。",
        "prior_art_distinction": "区别于只优化水质目标，本特征把现场执行约束纳入控制候选生成与仲裁。",
        "claim_skeleton_role": "从属权利要求中的工程执行约束和实施支持特征。",
        "evidence_boundary": "项目运维支持不替代状态估计、field replay 或 release gate。",
        "field_validation_gate": "PLC/SCADA 点表、SOP、操作日志、库存/药剂记录和执行反馈 replay。",
        "failure_boundary": "无现场执行反馈时，工程约束只能作为候选边界。",
        "protectability_note": "保护重点是执行约束进入控制仲裁链，而不是普通项目管理。",
    },
    {
        "feature_id": "PTF8_stage_gated_model_governance",
        "module_id": "M8_model_governance",
        "technical_problem": "agent 数量增长会造成重复 gate、上下游割裂和模型主链不清。",
        "technical_means": "采用七层系统骨架、接口契约、冗余簇、fallback 和阶段门控，审查每个新增能力是否回接主链。",
        "system_structure": "模型治理层读取各模块指标、manifest、测试和 evidence matrix，输出优先级、冻结/合并建议和下一步核心动作。",
        "control_actions": ["冻结展示层", "合并重复 gate", "重排高边际价值任务", "阻断越界 field claim", "维持低频自我打断"],
        "implementation_example": "当无真实 field package 时，治理层保持 R7a 为最高证据动作，同时允许 R8p work package preflight/assembly gate 离线推进。",
        "verification_metrics": ["system_spine_coverage", "interface_contract_coverage", "redundancy_cluster_count", "self_interrupt_verdict"],
        "technical_effect": "让系统演化更短、更稳、更可审查，减少无效 agent 扩张。",
        "prior_art_distinction": "区别于单次 agent 编排，本特征把证据边界、接口契约和阶段门控作为长期演化机制。",
        "claim_skeleton_role": "可作为系统治理或计算机实现方法的支撑特征，不单独替代水处理核心。",
        "evidence_boundary": "治理输出不产生 field evidence，只审查证据路径与模型边界。",
        "field_validation_gate": "所有 field claim 仍必须回到 R7/R8p/R8v、holdout、operator review 和 release gate。",
        "failure_boundary": "治理层不能替代模型能力、现场数据或执行器授权。",
        "protectability_note": "保护重点是阶段门控治理如何约束水处理灰箱闭环系统，而不是泛称项目管理。",
    },
)

TECHNICAL_CLAIM_SCAFFOLD_BLUEPRINTS: tuple[dict[str, object], ...] = (
    {
        "claim_id": "TCS1_independent_method_low_cost_sparse_cyclic_greybox_control",
        "claim_type": "independent_method_scaffold",
        "claim_title": "面向低成本稀疏传感条件的循环式水处理灰箱闭环控制方法",
        "mapped_feature_ids": [
            "PTF1_node_modality_sparse_sensing",
            "PTF2_soft_sensor_grey_state_estimation",
            "PTF3_grey_box_mechanism_boundary",
            "PTF4_cyclic_low_frequency_control",
            "PTF5_mechanism_kg_evidence_constraint",
            "PTF6_field_replay_release_gate",
        ],
        "required_layers": [
            "L1_field_object_layer",
            "L2_observation_layer",
            "L3_state_estimation_layer",
            "L4_mechanism_evidence_layer",
            "L5_diagnostic_decision_layer",
            "L6_closed_loop_execution_layer",
            "L7_validation_governance_layer",
        ],
        "technical_problem": "低成本、低频、稀疏和延迟传感下，传统水处理系统难以同时判断隐藏状态、解释机理并安全执行闭环动作。",
        "technical_combination": "将 node-modality 稀疏观测、软传感灰箱估计、机理/KG 证据约束、循环式控制动作和 field replay/release gate 串成主链。",
        "method_steps": [
            "获取污染物、水质基质、处理单元、管网/反应器拓扑和循环/暂存结构。",
            "构建低成本 node-modality 稀疏感知矩阵并识别弱观测隐藏状态。",
            "利用软传感器和灰箱先验估计污染物残留、反应完成度、催化剂活性、基质抑制和放行风险。",
            "基于机理证据和知识图谱生成诊断解释、控制候选和失败边界。",
            "在循环式结构中动态选择回流、延长停留、暂存等待、调整投药、切换单元、催化剂再生/更换或保护性阻断。",
            "通过 field package、timestamped replay、holdout、operator review 和 release gate 决定 claim 或动作能否升级。",
        ],
        "system_components": [
            "现场对象建模模块",
            "低成本稀疏传感模块",
            "软传感灰箱状态估计模块",
            "机理证据/KG 约束模块",
            "多智能体诊断与控制仲裁模块",
            "循环执行与保护性 release gate 模块",
            "field replay 与证据治理模块",
        ],
        "state_variables": [
            "node_modality_matrix",
            "pollutant_residual",
            "reaction_completion",
            "catalyst_activity",
            "matrix_interference",
            "byproduct_or_release_risk",
            "operator_review_required",
            "field_claim_status",
        ],
        "control_actions": ["回流", "延长停留时间", "暂存等待", "调整投药", "切换单元", "催化剂再生/更换", "保护性阻断", "放行"],
        "verification_gates": ["R7 field package", "R8p row acceptance gates", "R8v routing", "field holdout", "operator review", "release gate"],
        "technical_effect": "在不依赖高成本高频全量传感的情况下，让黑箱过程具备可估计、可解释、可回放验证和可保护执行的闭环能力。",
        "prior_art_distinction": "区别于单纯软测量、单点控制或经验回流，本方案把稀疏观测、循环争取时间、灰箱估计、机理证据和证据门控组合为一条不可绕过的控制链。",
        "evidence_boundary": "该主链 scaffold 不能替代真实 field replay；未通过验证门前只能作为技术方案候选。",
        "failure_boundary": "任一必需证据门阻断时，不能写 actuator、release gate 或 field-supported claim。",
        "legal_status": "technical_claim_scaffold_not_legal_advice",
    },
    {
        "claim_id": "TCS2_independent_system_architecture",
        "claim_type": "independent_system_scaffold",
        "claim_title": "低成本传感循环式水处理智能灰箱闭环系统",
        "mapped_feature_ids": [
            "PTF1_node_modality_sparse_sensing",
            "PTF2_soft_sensor_grey_state_estimation",
            "PTF3_grey_box_mechanism_boundary",
            "PTF4_cyclic_low_frequency_control",
            "PTF5_mechanism_kg_evidence_constraint",
            "PTF6_field_replay_release_gate",
            "PTF7_engineering_execution_constraints",
            "PTF8_stage_gated_model_governance",
        ],
        "required_layers": [
            "L1_field_object_layer",
            "L2_observation_layer",
            "L3_state_estimation_layer",
            "L4_mechanism_evidence_layer",
            "L5_diagnostic_decision_layer",
            "L6_closed_loop_execution_layer",
            "L7_validation_governance_layer",
        ],
        "technical_problem": "已有系统往往将传感、估计、控制、验证和工程约束分离，难以在低成本受限观测下形成可实施闭环。",
        "technical_combination": "把七层系统骨架落实为对象层、观测层、估计层、机理证据层、诊断决策层、闭环执行层和验证治理层的组件组合。",
        "method_steps": [
            "由现场对象层定义污染物、水质、处理单元和循环拓扑。",
            "由观测层形成低成本传感和缺测/延迟矩阵。",
            "由状态估计层输出隐藏过程状态与不确定性。",
            "由机理证据层输出证据路径和控制约束。",
            "由诊断决策层生成候选动作和人工复核信号。",
            "由闭环执行层执行可回退动作并维持保护性阻断。",
            "由验证治理层审查 field claim 和 release gate。",
        ],
        "system_components": [
            "field object registry",
            "node-modality sparse sensing matrix",
            "soft sensor estimator",
            "grey-box mechanism boundary engine",
            "KG evidence constraint engine",
            "multi-agent diagnostic arbitration engine",
            "cyclic execution controller",
            "field replay and claim gate",
            "stage-gated governance facade",
        ],
        "state_variables": [
            "system_spine_status",
            "interface_contract_coverage",
            "facility_state",
            "joint_action",
            "guardrail_context",
            "evidence_chain_pass",
            "release_gate_status",
        ],
        "control_actions": ["模块合并", "证据阻断", "动作仲裁", "执行约束注入", "保护性写回", "阶段门控"],
        "verification_gates": ["system_spine_coverage", "interface_contract_coverage", "replay regression", "field evidence chain", "operator review"],
        "technical_effect": "让系统结构、接口、状态变量、控制动作和证据门形成可审查架构，减少 agent 堆叠和证据边界漂移。",
        "prior_art_distinction": "区别于一次性多智能体流程，本系统把模型能力、证据门和工程执行约束组织为长期演化的七层闭环架构。",
        "evidence_boundary": "系统 scaffold 只说明结构完整性，不能证明任一现场控制结论成立。",
        "failure_boundary": "治理层不能替代现场数据、模型验证或执行器授权。",
        "legal_status": "technical_claim_scaffold_not_legal_advice",
    },
    {
        "claim_id": "TCS3_dependent_catalyst_activity_regeneration_control",
        "claim_type": "dependent_or_divisional_scaffold",
        "claim_title": "催化剂活性代理观测与再生/更换闭环控制",
        "mapped_feature_ids": [
            "PTF1_node_modality_sparse_sensing",
            "PTF2_soft_sensor_grey_state_estimation",
            "PTF3_grey_box_mechanism_boundary",
            "PTF4_cyclic_low_frequency_control",
            "PTF6_field_replay_release_gate",
        ],
        "required_layers": ["L2_observation_layer", "L3_state_estimation_layer", "L4_mechanism_evidence_layer", "L6_closed_loop_execution_layer", "L7_validation_governance_layer"],
        "technical_problem": "催化剂活性通常难以用低成本传感器直接测得，导致再生、更换和保护策略缺少证据边界。",
        "technical_combination": "以 UV254/ORP/压降/再生事件/离线活性标签形成代理观测，并将软传感不确定性和灰箱催化剂衰减边界接入再生/更换动作。",
        "method_steps": [
            "采集催化剂床前后低成本代理信号和压降事件。",
            "匹配离线 catalyst_activity 标签、再生事件和床体/HRT 信息。",
            "估计催化剂活性及置信边界。",
            "在不确定或冲突时保持保护性阻断并请求 operator review。",
            "在 gate 通过后生成再生或更换候选。",
        ],
        "system_components": ["catalyst bed proxy sensing", "catalyst activity soft sensor", "pressure conflict resolution", "regeneration/replacement action gate"],
        "state_variables": ["catalyst_activity", "pressure_drop_kPa", "regeneration_event", "catalyst_decay", "operator_review_required"],
        "control_actions": ["催化剂再生", "催化剂更换", "保持保护", "暂存等待", "人工复核"],
        "verification_gates": ["Agent51 field proxy holdout", "pressure_source_resolution", "R8p/R8v", "operator review"],
        "technical_effect": "在低成本条件下提升催化剂活性可观测性，并避免未验证代理信号直接解除保护。",
        "prior_art_distinction": "区别于只按运行周期更换催化剂，本方向把代理观测、软传感和证据门控联动到再生/更换控制。",
        "evidence_boundary": "代理相关性和 synthetic holdout 不能替代真实 field proxy holdout。",
        "failure_boundary": "压降冲突、标签缺失或 holdout 未通过时不能解除催化剂保护规则。",
        "legal_status": "technical_claim_scaffold_not_legal_advice",
    },
    {
        "claim_id": "TCS4_dependent_node_modality_sparse_hidden_state_estimation",
        "claim_type": "dependent_or_divisional_scaffold",
        "claim_title": "node-modality 稀疏布点与隐藏状态估计",
        "mapped_feature_ids": ["PTF1_node_modality_sparse_sensing", "PTF2_soft_sensor_grey_state_estimation"],
        "required_layers": ["L1_field_object_layer", "L2_observation_layer", "L3_state_estimation_layer", "L7_validation_governance_layer"],
        "technical_problem": "有限预算下的传感布点若不面向隐藏状态，会造成关键状态不可估计。",
        "technical_combination": "将节点、模态、成本、缺测、拓扑和隐藏状态需求合并为矩阵，并把布点结果作为软传感输入契约。",
        "method_steps": [
            "定义节点、处理区和可用传感模态。",
            "计算隐藏状态覆盖、矩阵稳定性和单点依赖。",
            "选择低成本布点并标记弱观测轴。",
            "把布局、缺测 mask 和时间延迟传给软传感器。",
        ],
        "system_components": ["sensor candidate catalog", "node-modality matrix", "hidden-state requirement ledger", "soft sensor feature contract"],
        "state_variables": ["weak_state_coverage", "selected_matrix_rank", "availability_mask", "time_since_last_observed"],
        "control_actions": ["补点", "保持 abstention", "触发离线标签采集", "阻断低置信放行"],
        "verification_gates": ["field topology", "node-specific time series", "field missingness replay", "offline labels"],
        "technical_effect": "让传感布点直接服务隐藏状态估计，而不是只优化传感器数量或单点精度。",
        "prior_art_distinction": "区别于普通稀疏传感器布设，本方向把布点矩阵与软传感隐藏状态和证据门绑定。",
        "evidence_boundary": "无真实拓扑和标签时只能作为 design prior。",
        "failure_boundary": "弱状态覆盖不足时不能声称黑箱已变灰箱。",
        "legal_status": "technical_claim_scaffold_not_legal_advice",
    },
    {
        "claim_id": "TCS5_dependent_field_replay_protective_writeback",
        "claim_type": "dependent_or_divisional_scaffold",
        "claim_title": "现场 replay 证据门控与保护性控制写回",
        "mapped_feature_ids": [
            "PTF4_cyclic_low_frequency_control",
            "PTF6_field_replay_release_gate",
            "PTF8_stage_gated_model_governance",
        ],
        "required_layers": ["L5_diagnostic_decision_layer", "L6_closed_loop_execution_layer", "L7_validation_governance_layer"],
        "technical_problem": "控制策略即使在仿真中表现良好，也可能因现场证据不足或模板数据误用而误写执行器。",
        "technical_combination": "将 field package、timestamped replay、holdout、operator review、claim gate 和 release gate 组成保护性写回链。",
        "method_steps": [
            "导入 data_origin=field 的 metadata/CSV 包。",
            "执行 timestamped replay 和行级 provenance/template/bundle/temporal/semantic gates。",
            "运行 field holdout 与 operator review。",
            "根据 gate 结果允许保护性控制候选或继续阻断。",
        ],
        "system_components": ["field package importer", "timestamped replay engine", "evidence chain gate", "release/protective writeback gate"],
        "state_variables": ["field_import_pass", "evidence_chain_pass", "claim_gate_status", "can_write_to_release_gate"],
        "control_actions": ["保护性写回", "拒绝放行", "要求校准", "维持人工复核"],
        "verification_gates": ["R7", "R8p", "R8v", "field holdout", "operator review", "release gate"],
        "technical_effect": "减少把 synthetic/template 误当现场证据造成的误放行和误执行。",
        "prior_art_distinction": "区别于只离线评估控制精度，本方向把现场 replay 证据链作为执行器写回前置条件。",
        "evidence_boundary": "模板、样例、header-only 和 synthetic replay 都不能触发 field-supported 写回。",
        "failure_boundary": "任一 gate 阻断时只能保留候选或保护性阻断。",
        "legal_status": "technical_claim_scaffold_not_legal_advice",
    },
    {
        "claim_id": "TCS6_dependent_low_frequency_cycle_window_control",
        "claim_type": "dependent_or_divisional_scaffold",
        "claim_title": "低频传感-循环窗口协同控制",
        "mapped_feature_ids": ["PTF2_soft_sensor_grey_state_estimation", "PTF4_cyclic_low_frequency_control", "PTF7_engineering_execution_constraints"],
        "required_layers": ["L2_observation_layer", "L3_state_estimation_layer", "L6_closed_loop_execution_layer", "L7_validation_governance_layer"],
        "technical_problem": "低成本传感和离线检测反应慢，若没有循环/暂存窗口，控制动作可能来不及验证。",
        "technical_combination": "把低频采样间隔、软传感不确定性、暂存容量、回流路径和执行延迟共同纳入动作选择。",
        "method_steps": [
            "计算采样/检测/软传感/人工复核/执行器延迟。",
            "判断循环或暂存结构是否能覆盖验证窗口。",
            "在时间不足时选择回流、暂存、延长停留或阻断放行。",
            "在工程约束允许时恢复下一处理单元。",
        ],
        "system_components": ["low-frequency sensing schedule", "cycle/holding window", "latency budget", "execution constraint gate"],
        "state_variables": ["sampling_interval", "hold_time_min", "hydraulic_delay", "actuator_latency", "storage_margin"],
        "control_actions": ["延长停留", "回流", "暂存等待", "放行阻断", "切换单元"],
        "verification_gates": ["timestamped replay", "latency budget replay", "operator review", "actuator feedback"],
        "technical_effect": "用循环结构换取观测和诊断时间，降低对高速昂贵传感器的依赖。",
        "prior_art_distinction": "区别于高频实时控制，本方向把慢传感约束和循环处理结构作为同一控制问题处理。",
        "evidence_boundary": "延迟预算和 synthetic replay 不能替代真实 timestamped campaign replay。",
        "failure_boundary": "暂存容量或执行延迟不满足时，不能选择依赖该窗口的控制动作。",
        "legal_status": "technical_claim_scaffold_not_legal_advice",
    },
    {
        "claim_id": "TCS7_dependent_greybox_multi_agent_safety_arbitration",
        "claim_type": "dependent_or_divisional_scaffold",
        "claim_title": "灰箱机理先验约束下的多智能体诊断与安全仲裁",
        "mapped_feature_ids": [
            "PTF3_grey_box_mechanism_boundary",
            "PTF4_cyclic_low_frequency_control",
            "PTF5_mechanism_kg_evidence_constraint",
            "PTF7_engineering_execution_constraints",
            "PTF8_stage_gated_model_governance",
        ],
        "required_layers": ["L4_mechanism_evidence_layer", "L5_diagnostic_decision_layer", "L6_closed_loop_execution_layer", "L7_validation_governance_layer"],
        "technical_problem": "多个 agent 各自给出控制建议时，如果缺少机理和安全仲裁，可能产生冲突动作或越界执行。",
        "technical_combination": "将灰箱残差、KG 证据、工程约束、reward prior 和人工复核门合成仲裁规则。",
        "method_steps": [
            "收集状态估计、机理残差、KG 证据和工程约束。",
            "生成多个控制候选及其失败边界。",
            "依据安全收益、误放行风险、执行可行性和证据等级排序。",
            "对证据不足或冲突动作触发保护性阻断和 operator review。",
        ],
        "system_components": ["mechanism boundary engine", "KG constraint patch", "multi-agent candidate generator", "safety arbitration gate", "stage governance"],
        "state_variables": ["grey_box_residual", "constraint_hit", "joint_action", "reward_components", "operator_review_required"],
        "control_actions": ["动作排序", "冲突阻断", "人工复核", "保护性控制", "策略蒸馏"],
        "verification_gates": ["counterfactual replay", "field state-action-reward replay", "operator review", "governance stage gate"],
        "technical_effect": "让多智能体输出受机理证据和工程安全边界约束，降低冲突动作和过度自动化风险。",
        "prior_art_distinction": "区别于黑箱 MARL 或简单投票，本方向要求每个动作可追溯到状态、机理证据、工程约束和验证门。",
        "evidence_boundary": "多智能体仲裁逻辑通过前仍是候选策略，不能越过 field replay 写执行器。",
        "failure_boundary": "机制冲突、证据缺口或执行约束不满足时必须保持阻断。",
        "legal_status": "technical_claim_scaffold_not_legal_advice",
    },
)

TECHNICAL_EMBODIMENT_BLUEPRINTS: tuple[dict[str, object], ...] = (
    {
        "embodiment_id": "TE1_end_to_end_low_cost_cyclic_greybox_control",
        "embodiment_title": "端到端低成本稀疏传感循环式灰箱闭环控制实施例",
        "linked_claim_ids": [
            "TCS1_independent_method_low_cost_sparse_cyclic_greybox_control",
            "TCS2_independent_system_architecture",
        ],
        "linked_feature_ids": [
            "PTF1_node_modality_sparse_sensing",
            "PTF2_soft_sensor_grey_state_estimation",
            "PTF3_grey_box_mechanism_boundary",
            "PTF4_cyclic_low_frequency_control",
            "PTF5_mechanism_kg_evidence_constraint",
            "PTF6_field_replay_release_gate",
        ],
        "scenario": "某污染批次进入均质池、反应核心、催化剂床、回流环和末端精处理单元，现场只允许少量低成本传感和离线验证。",
        "source_package_requirements": [
            "field metadata with data_origin=field",
            "node_modality_sensor_timeseries",
            "offline_lab_results",
            "campaign_operation_log",
            "fast_proxy_event_log",
            "agent52_replay_table",
        ],
        "required_tables_or_artifacts": [
            "R7 field package",
            "R8p accepted pressure-resolution rows",
            "R8v routing outputs",
            "field holdout split",
            "operator review log",
        ],
        "step_sequence": [
            "构建现场对象和循环拓扑。",
            "形成低成本 node-modality 观测矩阵。",
            "估计隐藏过程状态和不确定性。",
            "由灰箱/KG 证据生成控制候选和失败边界。",
            "执行回流、暂存、投药、切换或保护性阻断候选。",
            "通过 field replay、holdout、operator review 和 release gate 审查。",
        ],
        "validation_gates": ["R7 field package", "R8p", "R8v", "field holdout", "operator review", "release gate"],
        "acceptance_metrics": ["field_import_pass", "field_scenario_coverage", "joint_action_accuracy", "evidence_chain_pass", "can_write_to_release_gate"],
        "technical_effect_to_measure": "验证低成本稀疏传感与循环窗口是否能在不误放行的前提下提升隐藏状态可估计性和控制可执行性。",
        "current_evidence_status": "scaffold_only_waiting_for_field_package",
        "failure_boundary": "任一 field/replay/holdout/release gate 阻断时，不得生成 field-supported claim 或执行器写回。",
        "field_claim_upgrade_allowed": False,
    },
    {
        "embodiment_id": "TE2_pressure_resolution_route_package_validation",
        "embodiment_title": "压力源冲突解除与 R7-to-R8p route work package 验收实施例",
        "linked_claim_ids": [
            "TCS5_dependent_field_replay_protective_writeback",
            "TCS6_dependent_low_frequency_cycle_window_control",
        ],
        "linked_feature_ids": [
            "PTF4_cyclic_low_frequency_control",
            "PTF6_field_replay_release_gate",
            "PTF8_stage_gated_model_governance",
        ],
        "scenario": "node_modality_sensor_timeseries 与 pressure_headloss_event_log 对同一 batch 的压降证据冲突，需要 operator review 和 route work package 后才能进入 R8p/R8v。",
        "source_package_requirements": [
            "R7_TO_R8P_WORK_PACKAGE_DIR",
            "R7 source package work package",
            "operator supplement work package",
            "Agent52 replay export work package",
            "R8p validation gate work package",
        ],
        "required_tables_or_artifacts": [
            "pressure_resolution_replay_rows_r7_completion_route_work_package_preflight.json",
            "pressure_resolution_replay_rows_r7_completion_route_work_package_patch_plan.json",
            "pressure_resolution_replay_rows_r7_completion_route_work_package_assembly_gate.json",
            "pressure_source_resolution",
        ],
        "step_sequence": [
            "提交 R7_TO_R8P_WORK_PACKAGE_DIR。",
            "运行 work package preflight 并按 patch plan 修补缺口。",
            "验证四类 work package 均通过候选提交检查。",
            "按 assembly gate 装配 R8p candidate rows package。",
            "重跑 R8p/R8v validation gates 和 pressure conflict replay。",
        ],
        "validation_gates": ["work package preflight", "R8u-27 patch plan", "R8u-28 assembly gate", "R8p", "R8v", "operator review"],
        "acceptance_metrics": [
            "submitted_work_package_count",
            "passed_work_package_count",
            "blocked_assembly_step_count",
            "field_scenario_coverage",
            "pressure_source_conflict_requires_operator_review",
        ],
        "technical_effect_to_measure": "验证压力源冲突不会被静默平均或越过人工复核，并能被转化为可修补、可装配、可回放的现场行包路径。",
        "current_evidence_status": "blocked_waiting_for_R7_TO_R8P_WORK_PACKAGE_DIR",
        "failure_boundary": "未设置或未通过 R7_TO_R8P_WORK_PACKAGE_DIR 时，只能保留 candidate workflow，不能生成 field evidence。",
        "field_claim_upgrade_allowed": False,
    },
    {
        "embodiment_id": "TE3_catalyst_activity_proxy_regeneration",
        "embodiment_title": "催化剂活性代理观测与再生/更换闭环实施例",
        "linked_claim_ids": ["TCS3_dependent_catalyst_activity_regeneration_control"],
        "linked_feature_ids": [
            "PTF1_node_modality_sparse_sensing",
            "PTF2_soft_sensor_grey_state_estimation",
            "PTF3_grey_box_mechanism_boundary",
            "PTF4_cyclic_low_frequency_control",
            "PTF6_field_replay_release_gate",
        ],
        "scenario": "催化剂床活性不可直接低成本测量，需要通过 UV254、ORP、压降、再生事件和离线标签形成代理证据。",
        "source_package_requirements": [
            "N3 catalyst bed inlet/outlet UV254 and ORP",
            "pressure_drop_kPa or pressure_headloss_event_log",
            "regeneration_event",
            "offline catalyst_activity labels",
            "bed geometry and HRT",
        ],
        "required_tables_or_artifacts": [
            "node_modality_sensor_timeseries",
            "pressure_headloss_event_log",
            "offline_lab_results",
            "campaign_operation_log",
            "Agent51 field proxy holdout summary",
        ],
        "step_sequence": [
            "对齐催化剂床代理信号与离线标签。",
            "计算 catalyst_activity 软传感估计与不确定性。",
            "检查 pressure source conflict 和 operator review 状态。",
            "在 holdout 通过前保持催化剂保护。",
            "gate 通过后再生成催化剂再生或更换候选。",
        ],
        "validation_gates": ["Agent51 field proxy holdout", "pressure_source_resolution", "R8p/R8v", "operator review"],
        "acceptance_metrics": ["scoreable_batch_count", "proxy_label_correlation", "holdout_mae", "pressure_source_conflict_count", "catalyst_guardrail_mode"],
        "technical_effect_to_measure": "验证低成本代理能否提高催化剂活性可观测性，并避免未验证代理解除保护。",
        "current_evidence_status": "design_prior_and_schema_ready_waiting_for_field_proxy_holdout",
        "failure_boundary": "field proxy holdout 未通过或压力冲突未解除时，不能触发自动再生/更换执行器。",
        "field_claim_upgrade_allowed": False,
    },
    {
        "embodiment_id": "TE4_node_modality_sparse_hidden_state_layout",
        "embodiment_title": "node-modality 稀疏布点与隐藏状态估计实施例",
        "linked_claim_ids": ["TCS4_dependent_node_modality_sparse_hidden_state_estimation"],
        "linked_feature_ids": [
            "PTF1_node_modality_sparse_sensing",
            "PTF2_soft_sensor_grey_state_estimation",
        ],
        "scenario": "在预算受限的处理单元和管网节点上选择传感器组合，使 pollutant_residual、reaction_completion、catalyst_activity 等隐藏状态具备最低可估计性。",
        "source_package_requirements": [
            "site topology",
            "sensor candidate catalog",
            "installation and maintenance cost catalog",
            "node-specific time series",
            "offline weak-state labels",
        ],
        "required_tables_or_artifacts": [
            "sparse_placement_metrics.json",
            "observation_contract_metrics.json",
            "soft_sensor_matrix_metrics.json",
            "field topology package",
        ],
        "step_sequence": [
            "建立节点、模态和成本矩阵。",
            "计算 rank、弱状态覆盖和单点依赖。",
            "选择候选布点并标记硬缺口。",
            "把 layout_id、availability mask 和 time-since-last-observed 传入软传感器。",
            "通过 field topology 和 missingness replay 复核。",
        ],
        "validation_gates": ["field topology", "field missingness replay", "offline labels", "soft sensor holdout"],
        "acceptance_metrics": ["weak_state_coverage", "selected_matrix_rank", "condition_number_proxy", "missingness_robustness_score"],
        "technical_effect_to_measure": "验证传感布点是否真正提升隐藏状态可估计性，而不是只增加传感器数量。",
        "current_evidence_status": "synthetic_design_prior_waiting_for_field_topology_and_labels",
        "failure_boundary": "无真实拓扑和标签时不能声称现场最优布点或现场可观测性达标。",
        "field_claim_upgrade_allowed": False,
    },
    {
        "embodiment_id": "TE5_low_frequency_cycle_window_control",
        "embodiment_title": "低频传感-循环窗口协同控制实施例",
        "linked_claim_ids": ["TCS6_dependent_low_frequency_cycle_window_control"],
        "linked_feature_ids": [
            "PTF2_soft_sensor_grey_state_estimation",
            "PTF4_cyclic_low_frequency_control",
            "PTF7_engineering_execution_constraints",
        ],
        "scenario": "低成本传感和离线检测慢于反应/放行决策，需要用回流、暂存和延长停留时间换取验证窗口。",
        "source_package_requirements": [
            "timestamped sensor readings",
            "lab result timestamps",
            "operation action timestamps",
            "tank storage margin",
            "actuator latency and pump/valve feedback",
        ],
        "required_tables_or_artifacts": [
            "timestamped_campaign_replay",
            "grey_box_dynamic_latency metrics",
            "campaign_operation_log",
            "fast_proxy_event_log",
        ],
        "step_sequence": [
            "计算采样、检测、软传感、人工复核和执行器延迟。",
            "判断暂存/循环窗口能否覆盖慢证据返回。",
            "若窗口不足，选择回流、暂存或阻断放行。",
            "若窗口足够且 gate 通过，允许进入下一处理单元候选。",
        ],
        "validation_gates": ["timestamped replay", "latency budget replay", "operator review", "actuator feedback"],
        "acceptance_metrics": ["latency_violation_rate", "hold_time_min", "storage_margin", "false_positive_cost", "release_block_correctness"],
        "technical_effect_to_measure": "验证循环结构是否能降低对高频昂贵传感器的依赖，并降低误放行风险。",
        "current_evidence_status": "synthetic_latency_replay_waiting_for_timestamped_field_campaign",
        "failure_boundary": "暂存容量或执行延迟不足时，不能选择依赖循环窗口的控制动作。",
        "field_claim_upgrade_allowed": False,
    },
    {
        "embodiment_id": "TE6_greybox_multi_agent_safety_arbitration",
        "embodiment_title": "灰箱机理约束下的多智能体诊断与安全仲裁实施例",
        "linked_claim_ids": ["TCS7_dependent_greybox_multi_agent_safety_arbitration"],
        "linked_feature_ids": [
            "PTF3_grey_box_mechanism_boundary",
            "PTF4_cyclic_low_frequency_control",
            "PTF5_mechanism_kg_evidence_constraint",
            "PTF7_engineering_execution_constraints",
            "PTF8_stage_gated_model_governance",
        ],
        "scenario": "多个 agent 对同一污染批次提出回流、投药、切换、催化剂保护或放行候选，需要以机理证据、工程约束和证据等级仲裁。",
        "source_package_requirements": [
            "soft sensor state estimates",
            "grey-box residuals",
            "KG evidence paths",
            "engineering constraint patches",
            "state-action-reward replay",
            "operator review log",
        ],
        "required_tables_or_artifacts": [
            "control_replay_stress_metrics.json",
            "multi_facility_replay_evaluation metrics",
            "knowledge_graph_reasoning outputs",
            "engineering_execution_constraint metrics",
            "field state-action-reward replay",
        ],
        "step_sequence": [
            "收集状态估计、机理残差、KG 约束和工程约束。",
            "生成多个控制候选及失败边界。",
            "按安全收益、误放行风险、执行可行性和证据等级排序。",
            "对冲突或证据不足动作触发 operator review 和保护性阻断。",
        ],
        "validation_gates": ["counterfactual replay", "field state-action-reward replay", "operator review", "governance stage gate"],
        "acceptance_metrics": ["joint_action_accuracy", "reward_regret", "constraint_hit_rate", "false_positive_cost", "operator_review_required"],
        "technical_effect_to_measure": "验证多智能体输出是否能被灰箱机理和工程安全边界约束，而不是靠黑箱投票或 MARL 直接执行。",
        "current_evidence_status": "synthetic_counterfactual_replay_waiting_for_field_state_action_reward_replay",
        "failure_boundary": "机制冲突、证据缺口或执行约束不满足时必须保持阻断。",
        "field_claim_upgrade_allowed": False,
    },
)

TECHNICAL_EFFECT_MEASUREMENT_BLUEPRINTS: tuple[dict[str, object], ...] = (
    {
        "effect_id": "TEM1_observability_gain_under_sparse_sensing",
        "linked_embodiment_ids": ["TE4_node_modality_sparse_hidden_state_layout"],
        "linked_claim_ids": ["TCS4_dependent_node_modality_sparse_hidden_state_estimation"],
        "linked_feature_ids": [
            "PTF1_node_modality_sparse_sensing",
            "PTF2_soft_sensor_grey_state_estimation",
        ],
        "effect_statement": "证明 node-modality 稀疏布点相对无结构布点或单纯进出水传感，能提高关键隐藏状态的可估计性。",
        "baseline_comparator": "进水一个、出水一个的低成本规则布点，或不考虑节点-模态矩阵的 cost-only 贪心布点。",
        "measurement_metrics": [
            "weak_state_coverage",
            "selected_matrix_rank",
            "condition_number_proxy",
            "single_point_dependency",
            "missingness_robustness_score",
        ],
        "acceptance_thresholds": [
            "weak_state_coverage must improve over baseline without exceeding cost cap",
            "selected_matrix_rank must not decrease relative to baseline layout",
            "field topology and offline weak-state labels must confirm the same hidden-state coverage direction",
        ],
        "required_evidence_tiers": ["synthetic_baseline", "field_topology", "offline_labels", "field_missingness_replay"],
        "current_evidence_status": "synthetic_design_prior_waiting_for_field_topology_and_labels",
        "validation_gate": "field topology package + missingness replay + soft sensor holdout",
        "failure_boundary": "没有真实拓扑、节点级时间序列和弱状态标签时，只能说明候选布点逻辑，不能声称现场最优布点。",
        "field_claim_upgrade_allowed": False,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
    },
    {
        "effect_id": "TEM2_blackbox_to_greybox_state_estimation",
        "linked_embodiment_ids": [
            "TE1_end_to_end_low_cost_cyclic_greybox_control",
            "TE4_node_modality_sparse_hidden_state_layout",
        ],
        "linked_claim_ids": [
            "TCS1_independent_method_low_cost_sparse_cyclic_greybox_control",
            "TCS2_independent_system_architecture",
            "TCS4_dependent_node_modality_sparse_hidden_state_estimation",
        ],
        "linked_feature_ids": [
            "PTF1_node_modality_sparse_sensing",
            "PTF2_soft_sensor_grey_state_estimation",
            "PTF3_grey_box_mechanism_boundary",
        ],
        "effect_statement": "证明低成本观测、缺测 mask、灰箱先验和离线标签结合后，能把中间不可见过程从黑箱推进到可审查灰箱。",
        "baseline_comparator": "仅用出水阈值、单点经验规则或不带灰箱先验的纯黑箱回归模型。",
        "measurement_metrics": [
            "masked_mae",
            "interval_coverage",
            "field_holdout_gate_pass",
            "grey_box_residual",
            "abstention_or_ood_rate",
        ],
        "acceptance_thresholds": [
            "masked_mae must improve on the field holdout split before claim upgrade",
            "prediction intervals must satisfy the configured coverage gate",
            "OOD or high-uncertainty batches must abstain instead of releasing control",
        ],
        "required_evidence_tiers": ["synthetic_holdout", "literature_prior", "field_holdout", "operator_review"],
        "current_evidence_status": "interface_and_synthetic_holdout_ready_waiting_for_field_holdout",
        "validation_gate": "field holdout + uncertainty calibration + operator review",
        "failure_boundary": "field holdout 未通过或不确定性未校准时，软传感结果只能作为候选估计，不能解除保护或放行。",
        "field_claim_upgrade_allowed": False,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
    },
    {
        "effect_id": "TEM3_low_frequency_cycle_window_reduces_fast_sensor_need",
        "linked_embodiment_ids": ["TE5_low_frequency_cycle_window_control"],
        "linked_claim_ids": ["TCS6_dependent_low_frequency_cycle_window_control"],
        "linked_feature_ids": [
            "PTF2_soft_sensor_grey_state_estimation",
            "PTF4_cyclic_low_frequency_control",
            "PTF7_engineering_execution_constraints",
        ],
        "effect_statement": "证明循环、暂存和延长停留时间能为低频传感、离线检测和人工复核争取时间，从而降低对昂贵高频传感器的依赖。",
        "baseline_comparator": "一次通过式处理或假设传感/检测即时返回的闭环控制。",
        "measurement_metrics": [
            "latency_violation_rate",
            "hold_time_min",
            "storage_margin",
            "false_positive_cost",
            "release_block_correctness",
        ],
        "acceptance_thresholds": [
            "timestamped field replay must show cycle window covers sensor/lab/operator latency",
            "latency_violation_rate must remain below the configured gate before release candidate generation",
            "false_positive_cost and release_block_correctness must be reported together",
        ],
        "required_evidence_tiers": ["synthetic_latency_replay", "timestamped_field_campaign", "actuator_feedback", "operator_review"],
        "current_evidence_status": "synthetic_latency_replay_waiting_for_timestamped_field_campaign",
        "validation_gate": "timestamped field replay + latency budget gate + actuator feedback",
        "failure_boundary": "暂存容量、回流通道或执行器延迟不足时，不能选择依赖循环窗口的控制动作。",
        "field_claim_upgrade_allowed": False,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
    },
    {
        "effect_id": "TEM4_catalyst_proxy_guardrail_effect",
        "linked_embodiment_ids": ["TE3_catalyst_activity_proxy_regeneration"],
        "linked_claim_ids": ["TCS3_dependent_catalyst_activity_regeneration_control"],
        "linked_feature_ids": [
            "PTF1_node_modality_sparse_sensing",
            "PTF2_soft_sensor_grey_state_estimation",
            "PTF3_grey_box_mechanism_boundary",
            "PTF4_cyclic_low_frequency_control",
            "PTF6_field_replay_release_gate",
        ],
        "effect_statement": "证明 UV254、ORP、压降、再生事件和离线标签形成的代理观测能提高催化剂活性可观测性，并保持未验证代理下的保护边界。",
        "baseline_comparator": "只按运行时长、处理批次数或人工经验判断催化剂再生/更换。",
        "measurement_metrics": [
            "scoreable_batch_count",
            "proxy_label_correlation",
            "holdout_mae",
            "pressure_source_conflict_count",
            "catalyst_guardrail_mode",
        ],
        "acceptance_thresholds": [
            "Agent51 field proxy holdout must pass before regeneration/replacement candidate generation",
            "holdout_mae and proxy_label_correlation must be reported on field-linked batches",
            "pressure source conflict must be resolved or sent to operator review before catalyst action",
        ],
        "required_evidence_tiers": ["design_prior", "field_proxy_holdout", "pressure_source_resolution", "operator_review"],
        "current_evidence_status": "design_prior_and_schema_ready_waiting_for_field_proxy_holdout",
        "validation_gate": "Agent51 field proxy holdout + pressure_source_resolution + R8p/R8v",
        "failure_boundary": "代理 holdout 未通过或压力冲突未解除时，不能触发自动再生或更换执行器。",
        "field_claim_upgrade_allowed": False,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
    },
    {
        "effect_id": "TEM5_field_replay_protective_writeback_reduces_false_release",
        "linked_embodiment_ids": [
            "TE1_end_to_end_low_cost_cyclic_greybox_control",
            "TE2_pressure_resolution_route_package_validation",
            "TE5_low_frequency_cycle_window_control",
        ],
        "linked_claim_ids": [
            "TCS1_independent_method_low_cost_sparse_cyclic_greybox_control",
            "TCS5_dependent_field_replay_protective_writeback",
            "TCS6_dependent_low_frequency_cycle_window_control",
        ],
        "linked_feature_ids": [
            "PTF4_cyclic_low_frequency_control",
            "PTF6_field_replay_release_gate",
            "PTF8_stage_gated_model_governance",
        ],
        "effect_statement": "证明 replay、压力源冲突解除、operator review 和 release gate 能阻止证据不足批次被静默放行。",
        "baseline_comparator": "直接使用 synthetic replay、静默平均冲突压力源或跳过人工复核的自动放行流程。",
        "measurement_metrics": [
            "evidence_chain_pass",
            "pressure_source_conflict_requires_operator_review",
            "can_write_to_release_gate",
            "release_block_correctness",
            "field_scenario_coverage",
        ],
        "acceptance_thresholds": [
            "R7/R8p/R8v gates must pass before any release-gated claim",
            "pressure_source_conflict_requires_operator_review must remain true until conflict resolution is accepted",
            "can_write_to_release_gate must remain false in scaffold/template/synthetic states",
        ],
        "required_evidence_tiers": ["R7_field_package", "R8p_acceptance", "R8v_routing", "operator_review", "release_gate"],
        "current_evidence_status": "blocked_waiting_for_R7_TO_R8P_WORK_PACKAGE_DIR",
        "validation_gate": "R7/R8p/R8v + pressure conflict operator review + release gate",
        "failure_boundary": "真实行包、冲突解除或 operator review 任一缺失时，只能阻断或生成补件任务，不能放行。",
        "field_claim_upgrade_allowed": False,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
    },
    {
        "effect_id": "TEM6_greybox_multi_agent_arbitration_reduces_conflict_actions",
        "linked_embodiment_ids": ["TE6_greybox_multi_agent_safety_arbitration"],
        "linked_claim_ids": ["TCS7_dependent_greybox_multi_agent_safety_arbitration"],
        "linked_feature_ids": [
            "PTF3_grey_box_mechanism_boundary",
            "PTF4_cyclic_low_frequency_control",
            "PTF5_mechanism_kg_evidence_constraint",
            "PTF7_engineering_execution_constraints",
            "PTF8_stage_gated_model_governance",
        ],
        "effect_statement": "证明多智能体候选动作经过灰箱机理、KG 证据和工程约束仲裁后，能减少冲突动作和过度自动化风险。",
        "baseline_comparator": "简单多数投票、单 agent 规则或未受机理证据约束的黑箱 MARL 策略。",
        "measurement_metrics": [
            "joint_action_accuracy",
            "reward_regret",
            "constraint_hit_rate",
            "false_positive_cost",
            "operator_review_required",
        ],
        "acceptance_thresholds": [
            "field state-action-reward replay must pass before writeback",
            "constraint_hit_rate must be reported with false_positive_cost",
            "conflict actions must route to operator review or protective block",
        ],
        "required_evidence_tiers": ["counterfactual_replay", "field_state_action_reward_replay", "KG_source_basis", "operator_review"],
        "current_evidence_status": "synthetic_counterfactual_replay_waiting_for_field_state_action_reward_replay",
        "validation_gate": "field state-action-reward replay + KG source_basis + governance stage gate",
        "failure_boundary": "机制冲突、证据缺口或执行约束不满足时，仲裁器必须保持阻断，不能写执行器。",
        "field_claim_upgrade_allowed": False,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
    },
    {
        "effect_id": "TEM7_engineering_execution_constraint_feasibility",
        "linked_embodiment_ids": [
            "TE1_end_to_end_low_cost_cyclic_greybox_control",
            "TE5_low_frequency_cycle_window_control",
            "TE6_greybox_multi_agent_safety_arbitration",
        ],
        "linked_claim_ids": [
            "TCS2_independent_system_architecture",
            "TCS6_dependent_low_frequency_cycle_window_control",
            "TCS7_dependent_greybox_multi_agent_safety_arbitration",
        ],
        "linked_feature_ids": [
            "PTF4_cyclic_low_frequency_control",
            "PTF7_engineering_execution_constraints",
            "PTF8_stage_gated_model_governance",
        ],
        "effect_statement": "证明候选控制动作不仅算法上可选，而且满足泵阀、暂存容量、药剂库存、人工复核和现场 SOP 的执行约束。",
        "baseline_comparator": "不考虑执行器延迟、资源库存、人工复核窗口和安全 SOP 的纯算法动作排序。",
        "measurement_metrics": [
            "execution_constraint_violation_count",
            "actuator_latency_violation_count",
            "storage_or_reagent_bottleneck_count",
            "operator_review_sla_violation_count",
            "blocked_action_count",
        ],
        "acceptance_thresholds": [
            "no automatic action may bypass actuator/SOP feasibility checks",
            "constraint violations must convert to protective block or operator review",
            "field replay must include actuator feedback before engineering claim upgrade",
        ],
        "required_evidence_tiers": ["engineering_constraint_patch", "actuator_feedback", "operator_review", "field_replay"],
        "current_evidence_status": "engineering_constraint_contract_ready_waiting_for_actuator_feedback",
        "validation_gate": "engineering constraint replay + actuator feedback + operator review SLA",
        "failure_boundary": "执行器、库存、暂存或人工复核约束不满足时，候选动作必须降级为阻断/等待/补件。",
        "field_claim_upgrade_allowed": False,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
    },
)

PRIOR_ART_DISTINCTION_BLUEPRINTS: tuple[dict[str, object], ...] = (
    {
        "distinction_id": "PAD1_soft_sensor_ml_vs_cyclic_greybox_release_gated_control",
        "mapped_claim_ids": [
            "TCS1_independent_method_low_cost_sparse_cyclic_greybox_control",
            "TCS2_independent_system_architecture",
        ],
        "mapped_feature_ids": [
            "PTF1_node_modality_sparse_sensing",
            "PTF2_soft_sensor_grey_state_estimation",
            "PTF3_grey_box_mechanism_boundary",
            "PTF4_cyclic_low_frequency_control",
            "PTF6_field_replay_release_gate",
        ],
        "mapped_effect_ids": [
            "TEM1_observability_gain_under_sparse_sensing",
            "TEM2_blackbox_to_greybox_state_estimation",
            "TEM3_low_frequency_cycle_window_reduces_fast_sensor_need",
            "TEM5_field_replay_protective_writeback_reduces_false_release",
        ],
        "prior_art_family": "wastewater soft sensors, data-driven process monitoring and sensor-limited control",
        "representative_sources": [
            "Model validation and uncertainty skill",
            "GRU-D / BRITS / PyPOTS missing-data modeling references",
            "scikit-learn missing-value-native baseline documentation",
        ],
        "known_prior_capability": "已有软传感和缺测时间序列方法可估计水质或过程状态，但通常不把循环结构、低频等待窗口、release gate 和现场 replay 绑定为一个保护性闭环。",
        "distinguishing_combination": "低成本 node-modality 稀疏观测 + 软传感不确定性 + 灰箱边界 + 回流/暂存争取时间 + field replay/release gate 的组合。",
        "why_not_generic_ai_or_control": "区别点不是使用机器学习，而是让低频/缺测观测先进入灰箱状态和证据门，再决定能否回流、暂存、投药、切换或放行。",
        "technical_problem_addressed": "低成本观测不足和检测延迟导致中间过程黑箱、控制动作缺少可验证依据。",
        "required_embodiments": [
            "TE1_end_to_end_low_cost_cyclic_greybox_control",
            "TE4_node_modality_sparse_hidden_state_layout",
            "TE5_low_frequency_cycle_window_control",
        ],
        "measurable_effects": [
            "hidden-state observability gain",
            "field holdout calibrated grey-state estimation",
            "latency violation reduction before release decisions",
        ],
        "evidence_status": "distinction_hypothesis_needs_formal_prior_art_search_and_field_validation",
        "novelty_risk_level": "medium",
        "combination_risk": "soft sensors, cyclic reactors and release gates may each be known; protectability depends on whether the constrained combination and evidence-gated action path is sufficiently specific.",
        "dependent_fallback_path": "将独立方向收窄到低成本低频观测下的循环窗口、field replay release gate 或 node-modality hidden-state coverage 子组合。",
        "verification_needed": [
            "formal patent/prior-art search",
            "field holdout",
            "timestamped replay",
            "release gate audit",
        ],
        "legal_status": "prior_art_distinction_hypothesis_not_legal_opinion",
        "formal_search_required": True,
        "field_claim_upgrade_allowed": False,
        "failure_boundary": "未完成正式检索和现场 gate 前，只能作为区别假设，不能写成新颖性/创造性结论。",
    },
    {
        "distinction_id": "PAD2_sparse_sensor_placement_vs_node_modality_hidden_state_layout",
        "mapped_claim_ids": ["TCS4_dependent_node_modality_sparse_hidden_state_estimation"],
        "mapped_feature_ids": [
            "PTF1_node_modality_sparse_sensing",
            "PTF2_soft_sensor_grey_state_estimation",
        ],
        "mapped_effect_ids": ["TEM1_observability_gain_under_sparse_sensing"],
        "prior_art_family": "sparse sensor placement for reconstruction or classification",
        "representative_sources": [
            "PySensors official repository",
            "SSPOR/SSPOC, QR/CCQR/GQR and SVD/PCA basis selection methods",
        ],
        "known_prior_capability": "已有稀疏传感布点方法可服务重构或分类，也可结合成本约束选择传感位置。",
        "distinguishing_combination": "把传感位置扩展为 node-modality 矩阵，并把覆盖目标从一般重构转成 pollutant_residual、reaction_completion、catalyst_activity 等隐藏状态及下游控制可用性。",
        "why_not_generic_ai_or_control": "区别点不是稀疏布点算法本身，而是布点合同向软传感、催化剂代理、循环控制和 field missingness replay 传递约束。",
        "technical_problem_addressed": "预算受限时传感器数量少，传统进出水布点无法保证关键隐藏状态可估计。",
        "required_embodiments": ["TE4_node_modality_sparse_hidden_state_layout"],
        "measurable_effects": [
            "weak_state_coverage gain",
            "selected_matrix_rank preservation",
            "single-point dependency reduction",
        ],
        "evidence_status": "method_mapping_ready_waiting_for_field_topology_and_labels",
        "novelty_risk_level": "medium_high",
        "combination_risk": "通用稀疏布点方法较成熟；保护点应落在水处理隐藏状态、node-modality 合同和后续 release/holdout gate 的耦合。",
        "dependent_fallback_path": "收窄到 catalyst_activity 弱轴补点、pressure/headloss proxy 与 field missingness replay 的从属方向。",
        "verification_needed": ["field topology", "node-specific time series", "offline weak-state labels", "missingness replay"],
        "legal_status": "prior_art_distinction_hypothesis_not_legal_opinion",
        "formal_search_required": True,
        "field_claim_upgrade_allowed": False,
        "failure_boundary": "无真实拓扑和标签时不能宣称现场布点优于已有稀疏传感方案。",
    },
    {
        "distinction_id": "PAD3_marl_pump_coordination_vs_greybox_multi_agent_safety_arbitration",
        "mapped_claim_ids": ["TCS7_dependent_greybox_multi_agent_safety_arbitration"],
        "mapped_feature_ids": [
            "PTF3_grey_box_mechanism_boundary",
            "PTF4_cyclic_low_frequency_control",
            "PTF5_mechanism_kg_evidence_constraint",
            "PTF7_engineering_execution_constraints",
            "PTF8_stage_gated_model_governance",
        ],
        "mapped_effect_ids": [
            "TEM6_greybox_multi_agent_arbitration_reduces_conflict_actions",
            "TEM7_engineering_execution_constraint_feasibility",
        ],
        "prior_art_family": "multi-agent reinforcement learning, pump-station coordination and policy distillation",
        "representative_sources": [
            "User-provided wastewater multi-facility coordination slides",
            "Offline RL / Conservative Q-Learning",
            "D4RL and VIPER policy extraction references",
        ],
        "known_prior_capability": "已有多智能体协同控制、共享经验池、联合奖励和策略蒸馏思路，泵站调度中也常见基于水位/流量的联动控制。",
        "distinguishing_combination": "本项目把多 agent 输出限制在灰箱机理、KG 证据、工程执行约束、operator review 和 field replay 之内，不允许黑箱策略直接写执行器。",
        "why_not_generic_ai_or_control": "区别点不是多个 agent 或强化学习，而是候选动作必须回到状态估计、机理证据、工程约束和验证门，冲突动作默认保护性阻断。",
        "technical_problem_addressed": "多设施协同动作容易因证据不足、动作冲突或执行约束缺失而造成误投药、误放行或过度自动化。",
        "required_embodiments": ["TE6_greybox_multi_agent_safety_arbitration"],
        "measurable_effects": [
            "joint_action_accuracy under replay",
            "constraint_hit_rate with false_positive_cost",
            "operator_review_required for conflicts",
        ],
        "evidence_status": "synthetic_counterfactual_replay_waiting_for_field_state_action_reward_replay",
        "novelty_risk_level": "medium",
        "combination_risk": "多智能体和策略蒸馏均已有公开方法；保护点应避免泛化到 MARL，本项目应限定为灰箱证据门控的水处理控制仲裁链。",
        "dependent_fallback_path": "收窄到 pressure conflict、catalyst guardrail 或 release gate 下的安全仲裁从属方案。",
        "verification_needed": ["field state-action-reward replay", "operator review labels", "engineering constraint replay"],
        "legal_status": "prior_art_distinction_hypothesis_not_legal_opinion",
        "formal_search_required": True,
        "field_claim_upgrade_allowed": False,
        "failure_boundary": "无现场 replay 时不能证明多 agent 仲裁比已有协同控制更优或可部署。",
    },
    {
        "distinction_id": "PAD4_flowsheet_optimization_vs_low_cost_observation_gated_greybox_control",
        "mapped_claim_ids": [
            "TCS1_independent_method_low_cost_sparse_cyclic_greybox_control",
            "TCS2_independent_system_architecture",
        ],
        "mapped_feature_ids": [
            "PTF2_soft_sensor_grey_state_estimation",
            "PTF3_grey_box_mechanism_boundary",
            "PTF4_cyclic_low_frequency_control",
            "PTF7_engineering_execution_constraints",
        ],
        "mapped_effect_ids": [
            "TEM2_blackbox_to_greybox_state_estimation",
            "TEM3_low_frequency_cycle_window_reduces_fast_sensor_need",
            "TEM7_engineering_execution_constraint_feasibility",
        ],
        "prior_art_family": "water treatment flowsheet modeling, unit-model optimization, TEA/LCA and process constraints",
        "representative_sources": [
            "WaterTAP official repository and documentation",
            "QSDsan process/system simulation",
            "Pyomo constraints and WaterTAP costing references",
        ],
        "known_prior_capability": "已有水处理 flowsheet、单元模型、成本、约束优化和系统仿真框架。",
        "distinguishing_combination": "本项目不是先假设完整高保真参数，而是在低成本观测不足时用软传感和循环窗口形成可校准灰箱，再由 replay/field gate 限制控制动作。",
        "why_not_generic_ai_or_control": "区别点不是优化求解器，而是将不完整观测、低频证据到达、循环等待和保护性放行门写成控制前置条件。",
        "technical_problem_addressed": "真实现场往往缺少完整 flowsheet 参数和高频传感，纯优化模型容易产生虚假精确控制。",
        "required_embodiments": [
            "TE1_end_to_end_low_cost_cyclic_greybox_control",
            "TE5_low_frequency_cycle_window_control",
        ],
        "measurable_effects": [
            "grey_box_residual under field holdout",
            "latency budget coverage",
            "execution constraint violation count",
        ],
        "evidence_status": "greybox_interface_ready_waiting_for_field_calibration_and_actuator_feedback",
        "novelty_risk_level": "medium",
        "combination_risk": "流程模拟和约束优化已有成熟工具；本项目应突出低成本稀疏观测条件下的循环窗口与证据门控控制链。",
        "dependent_fallback_path": "收窄到低频传感-循环窗口协同控制或工程执行约束仲裁。",
        "verification_needed": ["field calibration", "RTD/HRT evidence", "actuator feedback", "timestamped replay"],
        "legal_status": "prior_art_distinction_hypothesis_not_legal_opinion",
        "formal_search_required": True,
        "field_claim_upgrade_allowed": False,
        "failure_boundary": "没有完整工艺参数和现场校准时，不能把灰箱约束写成真实机理论证。",
    },
    {
        "distinction_id": "PAD5_scientific_kg_vs_action_constraint_and_claim_gate",
        "mapped_claim_ids": [
            "TCS1_independent_method_low_cost_sparse_cyclic_greybox_control",
            "TCS7_dependent_greybox_multi_agent_safety_arbitration",
        ],
        "mapped_feature_ids": [
            "PTF5_mechanism_kg_evidence_constraint",
            "PTF6_field_replay_release_gate",
            "PTF8_stage_gated_model_governance",
        ],
        "mapped_effect_ids": [
            "TEM5_field_replay_protective_writeback_reduces_false_release",
            "TEM6_greybox_multi_agent_arbitration_reduces_conflict_actions",
        ],
        "prior_art_family": "scientific knowledge graphs, literature evidence matrices and research-agent claim verification",
        "representative_sources": [
            "SciKG survey seed in literature evidence matrix",
            "Academic Research Agent Skill",
            "Agent37/38 KG and literature evidence records",
        ],
        "known_prior_capability": "已有科学知识图谱和文献抽取流程可组织证据、节点、关系和 claim boundary。",
        "distinguishing_combination": "本项目把 KG/source_basis 作为控制候选约束、claim gate 和 field validation queue，而不是只做文献摘要或解释文本。",
        "why_not_generic_ai_or_control": "区别点不是知识图谱，而是 KG 边必须影响动作约束、失败边界、现场字段需求和 release/claim gate。",
        "technical_problem_addressed": "多 agent 容易产生缺证据的解释和控制建议，需要可追溯证据路径约束动作和 claim 升级。",
        "required_embodiments": [
            "TE1_end_to_end_low_cost_cyclic_greybox_control",
            "TE6_greybox_multi_agent_safety_arbitration",
        ],
        "measurable_effects": [
            "evidence_chain_pass",
            "constraint_hit_rate",
            "operator_review_required for unsupported actions",
        ],
        "evidence_status": "source_basis_detail_ready_not_field_supported",
        "novelty_risk_level": "medium_high",
        "combination_risk": "KG 和 claim verification 已是通用科研 AI 方法；保护点应落在水处理控制动作、field validation queue 和 release gate 的耦合。",
        "dependent_fallback_path": "收窄到 KG action constraint patch、claim-specific field package 或 unsupported action 阻断。",
        "verification_needed": ["citation-level source_basis audit", "field-supported KG edges", "release gate audit"],
        "legal_status": "prior_art_distinction_hypothesis_not_legal_opinion",
        "formal_search_required": True,
        "field_claim_upgrade_allowed": False,
        "failure_boundary": "文献证据只能支撑先验与约束，不能替代现场数据或 claim 成立。",
    },
    {
        "distinction_id": "PAD6_ai_catalyst_discovery_vs_operational_catalyst_activity_guardrail",
        "mapped_claim_ids": ["TCS3_dependent_catalyst_activity_regeneration_control"],
        "mapped_feature_ids": [
            "PTF1_node_modality_sparse_sensing",
            "PTF2_soft_sensor_grey_state_estimation",
            "PTF3_grey_box_mechanism_boundary",
            "PTF4_cyclic_low_frequency_control",
            "PTF6_field_replay_release_gate",
        ],
        "mapped_effect_ids": ["TEM4_catalyst_proxy_guardrail_effect"],
        "prior_art_family": "AI-for-science catalyst/material discovery and catalyst process monitoring",
        "representative_sources": [
            "Multi-agent AI catalyst discovery reference from user-provided PDF",
            "AOP/photocatalytic degradation kinetics seed records",
            "Agent51 catalyst proxy holdout metrics",
        ],
        "known_prior_capability": "已有 AI 催化剂发现、材料筛选和降解动力学建模可以辅助材料设计或反应机理分析。",
        "distinguishing_combination": "本项目把催化剂活性作为运行过程中的隐藏状态，用低成本代理、压力冲突解除、field proxy holdout 和循环控制决定保护、再生或更换候选。",
        "why_not_generic_ai_or_control": "区别点不是用 AI 发现新催化剂，而是把不可直接低成本测量的催化剂活性纳入受证据门控的现场闭环控制。",
        "technical_problem_addressed": "现场催化剂活性衰减难以直接低成本观测，误判会导致过度再生、更换或误放行。",
        "required_embodiments": ["TE3_catalyst_activity_proxy_regeneration"],
        "measurable_effects": [
            "proxy_label_correlation",
            "holdout_mae",
            "catalyst_guardrail_mode",
        ],
        "evidence_status": "design_prior_and_schema_ready_waiting_for_field_proxy_holdout",
        "novelty_risk_level": "medium",
        "combination_risk": "催化剂监测和 AI 材料发现均可能已有；保护点应限定在低成本代理、压力冲突解除和再生/更换控制 gate。",
        "dependent_fallback_path": "收窄到 UV254/ORP/pressure_drop/regeneration_event 的代理观测组合和 holdout 保护边界。",
        "verification_needed": ["Agent51 field proxy holdout", "pressure source resolution", "offline catalyst activity labels"],
        "legal_status": "prior_art_distinction_hypothesis_not_legal_opinion",
        "formal_search_required": True,
        "field_claim_upgrade_allowed": False,
        "failure_boundary": "field proxy holdout 未通过前不能触发自动再生/更换，也不能主张现场催化剂控制效果。",
    },
    {
        "distinction_id": "PAD7_replay_validation_vs_pressure_resolution_protective_release_gate",
        "mapped_claim_ids": [
            "TCS5_dependent_field_replay_protective_writeback",
            "TCS6_dependent_low_frequency_cycle_window_control",
        ],
        "mapped_feature_ids": [
            "PTF4_cyclic_low_frequency_control",
            "PTF6_field_replay_release_gate",
            "PTF8_stage_gated_model_governance",
        ],
        "mapped_effect_ids": ["TEM5_field_replay_protective_writeback_reduces_false_release"],
        "prior_art_family": "offline replay validation, data provenance gates and operational safety review",
        "representative_sources": [
            "R7/R8p/R8v pressure-resolution scenario pack outputs",
            "field replay evidence chain",
            "operator review and release gate contracts",
        ],
        "known_prior_capability": "已有 replay、数据溯源和人工审核可用于模型验证或运行审查。",
        "distinguishing_combination": "本项目把压力源冲突、TODO/template/provenance gate、同批次六表、时间窗、场景语义和下游路由组合成 release 前的保护性证据门。",
        "why_not_generic_ai_or_control": "区别点不是做 replay，而是 replay 失败或压力源冲突未解除时自动转为补包/人工复核/保护性阻断，不能静默平均或放行。",
        "technical_problem_addressed": "现场证据源冲突和模板数据混入会导致错误解除保护或误放行。",
        "required_embodiments": [
            "TE2_pressure_resolution_route_package_validation",
            "TE5_low_frequency_cycle_window_control",
        ],
        "measurable_effects": [
            "pressure_source_conflict_requires_operator_review",
            "evidence_chain_pass",
            "release_block_correctness",
        ],
        "evidence_status": "route_work_package_gate_ready_waiting_for_submission_dir",
        "novelty_risk_level": "medium",
        "combination_risk": "单独 replay/provenance gate 风险较高；保护点应集中在水处理压力源冲突解除到 release gate 的装配链。",
        "dependent_fallback_path": "收窄到 pressure-source conflict resolution、R7-to-R8p work package assembly 或 release-block correctness。",
        "verification_needed": ["R7_TO_R8P_WORK_PACKAGE_DIR", "R8p acceptance", "R8v routing", "operator review", "release gate audit"],
        "legal_status": "prior_art_distinction_hypothesis_not_legal_opinion",
        "formal_search_required": True,
        "field_claim_upgrade_allowed": False,
        "failure_boundary": "未通过真实行包、operator review 和 release gate 前，所有 protective writeback 只能是候选或阻断。",
    },
)

FORMAL_SEARCH_WORK_PACKAGE_BLUEPRINTS: tuple[dict[str, object], ...] = (
    {
        "work_package_id": "FSWP1_cyclic_greybox_soft_sensor_release_gate_search",
        "linked_distinction_ids": ["PAD1_soft_sensor_ml_vs_cyclic_greybox_release_gated_control"],
        "search_objective": "检索低成本/稀疏传感软测量、循环/暂存水处理和 release gate 是否已被组合为灰箱闭环控制。",
        "search_databases": ["CNIPA", "Google Patents", "Espacenet", "WIPO Patentscope", "Google Scholar"],
        "english_search_queries": [
            "\"wastewater\" \"soft sensor\" \"recycle\" \"release gate\"",
            "\"low cost sensor\" \"grey-box\" \"wastewater\" \"closed-loop control\"",
            "\"soft sensing\" \"hydraulic retention\" \"recycle\" \"effluent release\"",
            "\"sensor-limited\" \"water treatment\" \"hold tank\" \"control\"",
        ],
        "chinese_search_queries": [
            "污水处理 软传感 回流 放行 门控",
            "低成本传感 灰箱 水处理 闭环控制",
            "低频传感 暂存 回流 水处理 控制",
            "软测量 出水放行 证据门控",
        ],
        "classification_hints": ["G05B", "G06N", "C02F", "G01N"],
        "evidence_to_collect": [
            "是否同时包含低成本稀疏传感、软传感不确定性、循环/暂存窗口和放行门控",
            "是否存在 field replay 或 operator review 作为放行前置条件",
            "控制动作是否包含回流、延长停留、投药、切换或暂存等待",
        ],
        "negative_evidence_checks": [
            "若 prior art 已覆盖完整组合，主独立方向需要收窄",
            "若只覆盖软传感或只覆盖循环控制，记录缺失的证据门控/低频窗口差异",
        ],
        "claim_fallback_if_prior_art_found": "收窄到低频传感-循环窗口协同控制、field replay release gate 或 node-modality hidden-state coverage 子组合。",
        "field_validation_gate_to_preserve": "field holdout + timestamped replay + operator review + release gate",
        "decision_rule": "只有检索未发现完整组合，且 field gate 后续可验证时，才保留主方法/系统宽口径；否则转向从属 fallback。",
        "expected_output_artifacts": [
            "prior_art_hit_table",
            "claim_element_comparison_chart",
            "fallback_claim_scope_recommendation",
        ],
        "formal_search_required": True,
        "formal_search_completed": False,
        "legal_opinion_allowed": False,
        "field_claim_upgrade_allowed": False,
        "failure_boundary": "未完成正式检索和 field gate 前，不得把该组合写成新颖性或创造性结论。",
    },
    {
        "work_package_id": "FSWP2_node_modality_sparse_hidden_state_search",
        "linked_distinction_ids": ["PAD2_sparse_sensor_placement_vs_node_modality_hidden_state_layout"],
        "search_objective": "检索稀疏传感布点是否已被限定到水处理 node-modality 矩阵、隐藏状态覆盖和后续软传感/控制 gate。",
        "search_databases": ["Google Patents", "Espacenet", "CNIPA", "IEEE Xplore", "Google Scholar", "GitHub"],
        "english_search_queries": [
            "\"sparse sensor placement\" \"wastewater\" \"hidden state\"",
            "\"node modality\" \"sensor placement\" \"water treatment\"",
            "\"SSPOR\" OR \"SSPOC\" \"water quality\" \"sensor placement\"",
            "\"catalyst activity\" \"sensor placement\" \"soft sensor\"",
        ],
        "chinese_search_queries": [
            "稀疏传感 布点 污水处理 隐藏状态",
            "节点 模态 传感器布设 水处理",
            "催化剂活性 软传感 布点",
            "低成本传感 布点 水质 状态估计",
        ],
        "classification_hints": ["G01N", "G05B", "G06F", "C02F"],
        "evidence_to_collect": [
            "是否存在 node-modality 而非单纯节点布点",
            "是否把隐藏状态覆盖作为布点目标",
            "是否把布点输出传递给软传感、缺测 replay 或 release gate",
        ],
        "negative_evidence_checks": [
            "若已有文献覆盖 node-modality hidden-state layout，保留 catalyst_activity/pressure proxy 从属收窄",
            "若只覆盖通用稀疏布点，记录水处理隐藏状态和 field gate 差异",
        ],
        "claim_fallback_if_prior_art_found": "收窄到 catalyst_activity 弱轴补点、pressure/headloss proxy、regeneration_event 和 field missingness replay。",
        "field_validation_gate_to_preserve": "field topology + node-specific time series + offline weak-state labels + missingness replay",
        "decision_rule": "如果 prior art 已公开通用稀疏布点，主张必须落到隐藏状态覆盖、催化剂弱轴和下游 gate 的具体接口。",
        "expected_output_artifacts": [
            "sensor_placement_prior_art_hits",
            "node_modality_claim_element_chart",
            "catalyst_axis_fallback_scope",
        ],
        "formal_search_required": True,
        "formal_search_completed": False,
        "legal_opinion_allowed": False,
        "field_claim_upgrade_allowed": False,
        "failure_boundary": "无真实拓扑/标签且未完成检索时，不能宣称布点方案优于已有稀疏传感方法。",
    },
    {
        "work_package_id": "FSWP3_greybox_multi_agent_safety_arbitration_search",
        "linked_distinction_ids": ["PAD3_marl_pump_coordination_vs_greybox_multi_agent_safety_arbitration"],
        "search_objective": "检索多智能体水处理/泵站协同、离线 RL、策略蒸馏与安全仲裁是否已结合灰箱机理和 field replay 写回边界。",
        "search_databases": ["CNIPA", "Google Patents", "Espacenet", "IEEE Xplore", "ACM Digital Library", "Google Scholar"],
        "english_search_queries": [
            "\"multi-agent\" \"wastewater\" \"grey-box\" \"safety arbitration\"",
            "\"multi-agent reinforcement learning\" \"pump station\" \"policy distillation\"",
            "\"offline reinforcement learning\" \"water treatment\" \"operator review\"",
            "\"grey-box\" \"multi-agent\" \"control\" \"release gate\"",
        ],
        "chinese_search_queries": [
            "多智能体 污水处理 灰箱 安全仲裁",
            "多智能体强化学习 泵站 协同控制 策略蒸馏",
            "离线强化学习 水处理 人工复核",
            "灰箱 多智能体 控制 放行门控",
        ],
        "classification_hints": ["G05B", "G06N", "C02F", "E03F"],
        "evidence_to_collect": [
            "是否存在多设施协同控制和共享经验池",
            "是否包含灰箱机理/KG 证据约束",
            "是否禁止未通过 field replay 的动作写执行器",
        ],
        "negative_evidence_checks": [
            "若已有多智能体泵站协同，比较其是否面向泵站液位/流量而非反应器/催化剂/放行 gate",
            "若已有安全仲裁，检查是否包含 source_basis、operator review 和 release gate",
        ],
        "claim_fallback_if_prior_art_found": "收窄到 pressure conflict、catalyst guardrail、KG action constraint 或 release gate 下的安全仲裁。",
        "field_validation_gate_to_preserve": "field state-action-reward replay + KG source_basis + operator review + engineering constraint replay",
        "decision_rule": "已有 MARL/泵站协同不能直接覆盖本项目，除非同时具备灰箱证据门、工程约束和水处理放行 gate。",
        "expected_output_artifacts": [
            "multi_agent_control_prior_art_table",
            "greybox_arbitration_element_chart",
            "safety_arbitration_fallback_plan",
        ],
        "formal_search_required": True,
        "formal_search_completed": False,
        "legal_opinion_allowed": False,
        "field_claim_upgrade_allowed": False,
        "failure_boundary": "无 field replay 时不能证明多 agent 仲裁优于已有控制，也不能写执行器。",
    },
    {
        "work_package_id": "FSWP4_low_cost_observation_gated_flowsheet_search",
        "linked_distinction_ids": ["PAD4_flowsheet_optimization_vs_low_cost_observation_gated_greybox_control"],
        "search_objective": "检索水处理 flowsheet/优化/成本约束是否已处理低成本观测不足、循环等待和证据门控控制的组合。",
        "search_databases": ["Google Patents", "CNIPA", "Espacenet", "Google Scholar", "WaterTAP/QSDsan/Pyomo documentation"],
        "english_search_queries": [
            "\"water treatment\" \"flowsheet\" \"low-cost sensors\" \"control\"",
            "\"grey-box\" \"water treatment\" \"optimization\" \"sensor limited\"",
            "\"hydraulic retention\" \"soft sensor\" \"process optimization\"",
            "\"unit model\" \"release gate\" \"water treatment\"",
        ],
        "chinese_search_queries": [
            "水处理 流程模拟 低成本传感 控制",
            "灰箱 水处理 优化 传感受限",
            "水力停留时间 软传感 工艺优化",
            "单元模型 放行门控 水处理",
        ],
        "classification_hints": ["C02F", "G05B", "G06Q", "G06N"],
        "evidence_to_collect": [
            "是否存在完整 flowsheet 参数和约束优化",
            "是否把低成本观测不足作为控制门控前提",
            "是否以循环/暂存弥补低频证据延迟",
        ],
        "negative_evidence_checks": [
            "若已有 flowsheet 优化，检查其是否需要高保真参数而非低成本灰箱状态",
            "若已有低成本控制，检查其是否包含 release/replay/operator gate",
        ],
        "claim_fallback_if_prior_art_found": "收窄到低频传感-循环窗口协同控制、执行约束仲裁或 RTD/HRT 证据窗口。",
        "field_validation_gate_to_preserve": "field calibration + RTD/HRT evidence + actuator feedback + timestamped replay",
        "decision_rule": "如果现有优化模型已覆盖工艺约束，区别点必须保留在低成本观测门控和循环等待窗口。",
        "expected_output_artifacts": [
            "flowsheet_prior_art_table",
            "observation_gated_control_claim_chart",
            "greybox_calibration_gap_list",
        ],
        "formal_search_required": True,
        "formal_search_completed": False,
        "legal_opinion_allowed": False,
        "field_claim_upgrade_allowed": False,
        "failure_boundary": "不能把 WaterTAP/QSDsan/Pyomo 风格建模本身写成创新点；必须落到本项目受限观测控制链。",
    },
    {
        "work_package_id": "FSWP5_scientific_kg_action_constraint_claim_gate_search",
        "linked_distinction_ids": ["PAD5_scientific_kg_vs_action_constraint_and_claim_gate"],
        "search_objective": "检索 Scientific KG、文献证据矩阵和 claim verification 是否已作为水处理控制动作约束和 release/claim gate。",
        "search_databases": ["Google Scholar", "Google Patents", "CNIPA", "WIPO Patentscope", "Semantic Scholar"],
        "english_search_queries": [
            "\"scientific knowledge graph\" \"water treatment\" \"control constraint\"",
            "\"knowledge graph\" \"wastewater\" \"claim verification\"",
            "\"literature evidence\" \"release gate\" \"water treatment\"",
            "\"knowledge graph\" \"multi-agent\" \"action constraint\"",
        ],
        "chinese_search_queries": [
            "科学知识图谱 水处理 控制约束",
            "知识图谱 污水处理 证据链",
            "文献证据 放行门控 水处理",
            "知识图谱 多智能体 动作约束",
        ],
        "classification_hints": ["G06F", "G06N", "G05B", "C02F"],
        "evidence_to_collect": [
            "KG 是否只用于解释/检索，还是实际约束控制动作",
            "是否包含 source_basis 到 field validation queue 的映射",
            "是否包含 unsupported action 阻断或 claim gate",
        ],
        "negative_evidence_checks": [
            "若已有 KG 控制约束，检查是否面向水处理 release gate 和 field rows",
            "若只已有文献摘要/KG，记录其未触及控制写回边界",
        ],
        "claim_fallback_if_prior_art_found": "收窄到 KG action constraint patch、claim-specific field package、unsupported action blocking 或 source_basis-to-field queue。",
        "field_validation_gate_to_preserve": "citation-level source_basis audit + field-supported KG edges + release gate audit",
        "decision_rule": "KG 本身不保护；只有 KG 边被控制约束、claim gate 和 field validation queue 消费时才保留为技术特征。",
        "expected_output_artifacts": [
            "kg_prior_art_hit_table",
            "source_basis_to_action_constraint_chart",
            "unsupported_claim_blocking_fallback",
        ],
        "formal_search_required": True,
        "formal_search_completed": False,
        "legal_opinion_allowed": False,
        "field_claim_upgrade_allowed": False,
        "failure_boundary": "文献证据不能替代现场证据，KG 解释不能替代控制验证。",
    },
    {
        "work_package_id": "FSWP6_operational_catalyst_activity_guardrail_search",
        "linked_distinction_ids": ["PAD6_ai_catalyst_discovery_vs_operational_catalyst_activity_guardrail"],
        "search_objective": "检索 AI 催化剂发现、催化剂活性监测和水处理再生/更换控制是否已结合低成本代理与 field proxy holdout gate。",
        "search_databases": ["Google Scholar", "Google Patents", "CNIPA", "Espacenet", "WIPO Patentscope"],
        "english_search_queries": [
            "\"catalyst activity\" \"soft sensor\" \"water treatment\"",
            "\"photocatalyst\" \"regeneration\" \"ORP\" \"UV254\"",
            "\"AI\" \"catalyst discovery\" \"wastewater\" \"closed-loop control\"",
            "\"pressure drop\" \"catalyst bed\" \"activity\" \"water purification\"",
        ],
        "chinese_search_queries": [
            "催化剂活性 软传感 水处理",
            "光催化剂 再生 ORP UV254",
            "AI 催化剂发现 污水处理 闭环控制",
            "压降 催化剂床 活性 水净化",
        ],
        "classification_hints": ["C02F", "B01J", "G01N", "G05B", "G06N"],
        "evidence_to_collect": [
            "是否已有 UV254/ORP/pressure_drop/regeneration_event 代理组合",
            "是否使用 field proxy holdout 才允许再生/更换候选",
            "是否区分材料发现和运行态活性保护控制",
        ],
        "negative_evidence_checks": [
            "若已有催化剂活性代理，检查其是否包含压力源冲突解除和 release gate",
            "若已有 AI 催化剂发现，记录其是否仅服务材料筛选而非运行控制",
        ],
        "claim_fallback_if_prior_art_found": "收窄到 UV254/ORP/pressure_drop/regeneration_event 代理组合、pressure source resolution 或 Agent51 field proxy holdout。",
        "field_validation_gate_to_preserve": "Agent51 field proxy holdout + pressure source resolution + offline catalyst_activity labels",
        "decision_rule": "若已有运行态催化剂活性代理，保护点必须进一步限定到低成本代理组合、冲突解除和再生/更换保护边界。",
        "expected_output_artifacts": [
            "catalyst_activity_prior_art_table",
            "proxy_signal_element_chart",
            "catalyst_guardrail_fallback_scope",
        ],
        "formal_search_required": True,
        "formal_search_completed": False,
        "legal_opinion_allowed": False,
        "field_claim_upgrade_allowed": False,
        "failure_boundary": "field proxy holdout 未通过前不能触发自动再生/更换，也不能主张运行态控制效果。",
    },
    {
        "work_package_id": "FSWP7_pressure_resolution_protective_release_gate_search",
        "linked_distinction_ids": ["PAD7_replay_validation_vs_pressure_resolution_protective_release_gate"],
        "search_objective": "检索 replay/provenance/operator review 是否已形成针对水处理压力源冲突解除的保护性 release gate 装配链。",
        "search_databases": ["CNIPA", "Google Patents", "Espacenet", "WIPO Patentscope", "Google Scholar"],
        "english_search_queries": [
            "\"pressure source conflict\" \"water treatment\" \"operator review\"",
            "\"field replay\" \"release gate\" \"wastewater\"",
            "\"data provenance\" \"water treatment\" \"protective control\"",
            "\"pressure drop\" \"replay\" \"catalyst bed\" \"release\"",
        ],
        "chinese_search_queries": [
            "压力源 冲突 水处理 人工复核",
            "现场回放 放行门控 污水处理",
            "数据溯源 水处理 保护性控制",
            "压降 回放 催化剂床 放行",
        ],
        "classification_hints": ["G05B", "G01N", "C02F", "G06F"],
        "evidence_to_collect": [
            "是否已有压力源冲突识别和 authoritative source 记录",
            "是否要求 TODO/template/provenance gate",
            "是否要求同批次多表、时间窗、场景语义和下游路由",
        ],
        "negative_evidence_checks": [
            "若已有 replay validation，检查是否有 pressure-source conflict 与 release blocking",
            "若已有 provenance gate，检查是否能自动转补包/人工复核/保护性阻断",
        ],
        "claim_fallback_if_prior_art_found": "收窄到 pressure-source conflict resolution、R7-to-R8p work package assembly、release-block correctness 或 operator-review-before-clearance。",
        "field_validation_gate_to_preserve": "R7_TO_R8P_WORK_PACKAGE_DIR + R8p acceptance + R8v routing + operator review + release gate audit",
        "decision_rule": "已有 replay/provenance 技术不能覆盖本项目，除非也覆盖压力源冲突解除、行包装配和保护性 release gate。",
        "expected_output_artifacts": [
            "pressure_resolution_prior_art_table",
            "release_gate_element_chart",
            "operator_review_fallback_scope",
        ],
        "formal_search_required": True,
        "formal_search_completed": False,
        "legal_opinion_allowed": False,
        "field_claim_upgrade_allowed": False,
        "failure_boundary": "未通过真实行包、operator review 和 release gate 前，所有 protective writeback 只能是候选或阻断。",
    },
)


MODULE_BLUEPRINTS: tuple[dict[str, object], ...] = (
    {
        "module_id": "M1_sparse_observation_layout",
        "title": "低成本稀疏感知与布点",
        "model_role": "决定系统能看到什么、在哪些节点看、用哪些低成本信号看。",
        "core_question": "低成本传感是否足以支撑软传感、故障分类和低频闭环控制？",
        "module_type": "core_model",
        "primary_metrics": [
            "weak_state_coverage",
            "soft_sensor_reconstruction_gain",
            "topology_coverage_score",
            "total_cost_index",
        ],
        "failure_boundary": "无真实拓扑、水力停留时间、安装成本和 field labels 时，只能形成 synthetic topology prior。",
    },
    {
        "module_id": "M2_soft_sensor_state_estimation",
        "title": "软传感、缺测矩阵与不确定性",
        "model_role": "把低成本传感、缺测 mask 和灰箱先验转成隐藏状态估计与放行不确定性。",
        "core_question": "黑箱过程能否被软传感和灰箱先验转成可审查的灰箱状态？",
        "module_type": "core_model",
        "primary_metrics": [
            "masked_mae",
            "interval_coverage",
            "missingness_robustness_score",
            "field_holdout_gate_pass",
        ],
        "failure_boundary": "synthetic holdout 和 dropout 不能替代真实 field holdout 与真实缺测 replay。",
    },
    {
        "module_id": "M3_grey_box_mechanism",
        "title": "灰箱物理、机理解释与故障诊断",
        "model_role": "把软传感状态转成反应、基质、催化剂、水力和副产物风险的机理解释。",
        "core_question": "模型是否只是拟合分数，还是能解释为什么该回流、暂存、补药或保护催化剂？",
        "module_type": "core_model",
        "primary_metrics": [
            "grey_box_residual",
            "mass_balance_residual",
            "mechanism_hypothesis_count",
            "fault_mode_coverage",
        ],
        "failure_boundary": "灰箱参数未由现场 RTD、进出水污染物、催化剂历史和副产物标签校准前，只能作为先验。",
    },
    {
        "module_id": "M4_collaborative_control",
        "title": "循环式处理、多设施协同控制与仲裁",
        "model_role": "把循环、暂存、反应、催化剂床、回流和末端精处理组织成可解释的联合动作。",
        "core_question": "系统是否能在低频/延迟传感下选择可执行、可回退、可解释的联动动作？",
        "module_type": "core_model",
        "primary_metrics": [
            "joint_action_accuracy",
            "reward_regret",
            "distilled_policy_accuracy",
            "release_block_correctness",
        ],
        "failure_boundary": "无真实多节点 state-action-reward replay 时，不能写执行器或 release gate。",
    },
    {
        "module_id": "M5_kg_claim_evidence",
        "title": "知识图谱、文献证据与 Claim 审查",
        "model_role": "把污染物、材料、过程、低成本信号、隐藏状态、动作和风险连成可追溯证据路径。",
        "core_question": "模型每个强 claim 是否有文献、参数边界、适用条件和 field 验证需求？",
        "module_type": "core_model",
        "primary_metrics": [
            "evidence_traceability",
            "constraint_hit_rate",
            "source_basis_completion_rate",
            "field_supported_edge_ratio",
        ],
        "failure_boundary": "文献和 KG 只能支撑假设、先验和约束，不能替代现场证据。",
    },
    {
        "module_id": "M6_field_evidence_chain",
        "title": "现场数据接口、Replay 与证据门控",
        "model_role": "把真实 sensor/lab/operation/replay 数据转成可升级或阻断 claim 的验收链。",
        "core_question": "哪些数据表、字段、metadata、gate 和 replay 结果足以把仿真 claim 升级为现场待验证结论？",
        "module_type": "core_model",
        "primary_metrics": [
            "field_replay_import_pass",
            "field_need_to_gate_coverage",
            "evidence_chain_pass",
            "can_write_to_release_gate",
        ],
        "failure_boundary": "接口通过和 synthetic package 只证明流程能跑；data_origin=field 前不能升级现场结论。",
    },
    {
        "module_id": "M7_project_operations_support",
        "title": "项目运行、资源调度与实施管理",
        "model_role": "把批次、队列、资源、预算、库存和恢复爬坡转成项目实施支持层。",
        "core_question": "如果模型要落地，运行组织、资源和恢复策略是否可执行？",
        "module_type": "support",
        "primary_metrics": [
            "campaign_success_rate",
            "resource_bottleneck_count",
            "replan_trigger",
            "recovery_load_fraction",
        ],
        "failure_boundary": "该层支持工程实施，不应压过 Agent48/49/51/52/54/55/56/59 的模型核心优化。",
    },
    {
        "module_id": "M8_model_governance",
        "title": "模型治理、主链回接与减冗复盘",
        "model_role": "检查新增能力是否被主链消费、是否偏离模型核心、是否需要合并或冻结。",
        "core_question": "系统是在提高模型能力，还是在继续堆文件、堆 agent 和堆展示？",
        "module_type": "governance",
        "primary_metrics": [
            "main_chain_prior_consumption_rate",
            "mapped_agent_count",
            "redundancy_cluster_count",
            "self_interrupt_verdict",
        ],
        "failure_boundary": "治理层只能排序、阻断和提出重构路线，本身不替代模型能力或现场验证。",
    },
    {
        "module_id": "M9_presentation_delivery",
        "title": "展示、文档与汇报材料",
        "model_role": "表达和交付模型结果，不改变模型本身。",
        "core_question": "是否只是在美化表达而没有提升观测、推理、控制、验证或工程可行性？",
        "module_type": "frozen_presentation",
        "primary_metrics": ["none_for_model_core"],
        "failure_boundary": "默认冻结为低优先级，只有模型核心指标更新后才同步。",
    },
)


AGENT_MODULE_MAP: dict[str, tuple[str, str]] = {
    "data_quality_agent": ("M1_sparse_observation_layout", "keep_core_support"),
    "sensitivity_analysis_agent": ("M1_sparse_observation_layout", "keep_core_support"),
    "sensor_network_sparse_placement_agent": ("M1_sparse_observation_layout", "keep_core_anchor"),
    "catalyst_activity_proxy_agent": ("M1_sparse_observation_layout", "keep_core_anchor"),
    "soft_sensor_agent": ("M2_soft_sensor_state_estimation", "keep_core_anchor"),
    "soft_sensor_uncertainty_validation_agent": ("M2_soft_sensor_state_estimation", "merge_into_soft_sensor_validation"),
    "soft_sensor_conformal_calibration_agent": ("M2_soft_sensor_state_estimation", "merge_into_soft_sensor_validation"),
    "soft_sensor_field_holdout_gate_agent": ("M2_soft_sensor_state_estimation", "merge_with_field_evidence_gate"),
    "weak_target_stratified_conformal_agent": ("M2_soft_sensor_state_estimation", "merge_into_soft_sensor_validation"),
    "soft_sensor_matrix_coupling_agent": ("M2_soft_sensor_state_estimation", "keep_core_anchor"),
    "mechanism_agent": ("M3_grey_box_mechanism", "keep_core_anchor"),
    "fault_diagnosis_agent": ("M3_grey_box_mechanism", "keep_core_anchor"),
    "catalyst_lifecycle_agent": ("M3_grey_box_mechanism", "keep_core_support"),
    "minimal_grey_box_physics_agent": ("M3_grey_box_mechanism", "keep_core_anchor"),
    "grey_box_dynamic_latency_agent": ("M3_grey_box_mechanism", "keep_core_support"),
    "matrix_shock_fast_proxy_agent": ("M3_grey_box_mechanism", "keep_core_support"),
    "model_realism_audit_agent": ("M3_grey_box_mechanism", "merge_into_model_governance"),
    "strategy_profile_agent": ("M4_collaborative_control", "merge_into_control_policy"),
    "validation_planning_agent": ("M4_collaborative_control", "keep_core_support"),
    "control_strategy_agent": ("M4_collaborative_control", "keep_core_anchor"),
    "cost_safety_agent": ("M4_collaborative_control", "keep_core_anchor"),
    "arbitration_agent": ("M4_collaborative_control", "keep_core_anchor"),
    "multi_facility_collaborative_control_agent": ("M4_collaborative_control", "keep_core_anchor"),
    "multi_facility_replay_evaluation_agent": ("M4_collaborative_control", "keep_core_anchor"),
    "engineering_execution_constraint_agent": ("M4_collaborative_control", "keep_core_anchor"),
    "knowledge_graph_curation_agent": ("M5_kg_claim_evidence", "merge_into_kg_evidence"),
    "literature_evidence_agent": ("M5_kg_claim_evidence", "merge_into_kg_evidence"),
    "knowledge_graph_reasoning_agent": ("M5_kg_claim_evidence", "keep_core_anchor"),
    "field_validation_queue_alignment_agent": ("M5_kg_claim_evidence", "merge_with_field_evidence_gate"),
    "claim_specific_field_package_agent": ("M5_kg_claim_evidence", "merge_with_field_evidence_gate"),
    "field_data_interface_agent": ("M6_field_evidence_chain", "keep_core_support"),
    "field_calibration_gate_agent": ("M6_field_evidence_chain", "merge_into_field_evidence_gate"),
    "timestamped_campaign_replay_agent": ("M6_field_evidence_chain", "keep_core_anchor"),
    "field_replay_import_agent": ("M6_field_evidence_chain", "keep_core_anchor"),
    "field_replay_calibration_gate_agent": ("M6_field_evidence_chain", "merge_into_field_evidence_gate"),
    "field_replay_evidence_chain_agent": ("M6_field_evidence_chain", "keep_core_anchor"),
    "pressure_resolution_replay_scenario_pack_agent": ("M6_field_evidence_chain", "keep_core_support"),
    "campaign_telemetry_agent": ("M7_project_operations_support", "compress_into_project_ops"),
    "operations_scheduling_agent": ("M7_project_operations_support", "compress_into_project_ops"),
    "queue_planning_agent": ("M7_project_operations_support", "compress_into_project_ops"),
    "resource_expansion_agent": ("M7_project_operations_support", "compress_into_project_ops"),
    "long_term_economics_agent": ("M7_project_operations_support", "compress_into_project_ops"),
    "phased_implementation_agent": ("M7_project_operations_support", "compress_into_project_ops"),
    "implementation_stress_test_agent": ("M7_project_operations_support", "compress_into_project_ops"),
    "adaptive_portfolio_agent": ("M7_project_operations_support", "compress_into_project_ops"),
    "online_project_control_agent": ("M7_project_operations_support", "compress_into_project_ops"),
    "replanning_orchestrator_agent": ("M7_project_operations_support", "compress_into_project_ops"),
    "control_baseline_update_agent": ("M7_project_operations_support", "compress_into_project_ops"),
    "post_replan_replay_agent": ("M7_project_operations_support", "compress_into_project_ops"),
    "recovery_ramp_agent": ("M7_project_operations_support", "compress_into_project_ops"),
    "time_budget_recovery_agent": ("M7_project_operations_support", "compress_into_project_ops"),
    "recovery_strategy_writeback_agent": ("M7_project_operations_support", "compress_into_project_ops"),
    "recovery_execution_replay_agent": ("M7_project_operations_support", "compress_into_project_ops"),
    "recovery_online_control_agent": ("M7_project_operations_support", "compress_into_project_ops"),
    "project_synthesis_agent": ("M7_project_operations_support", "compress_into_project_ops"),
    "model_core_optimization_governance_agent": ("M8_model_governance", "keep_governance"),
    "main_chain_reconnection_agent": ("M8_model_governance", "keep_governance"),
    "agent_architecture_consolidation_agent": ("M8_model_governance", "keep_governance"),
    "deliverable_organization_agent": ("M9_presentation_delivery", "freeze_low_priority"),
    "presentation_asset_agent": ("M9_presentation_delivery", "freeze_low_priority"),
    "presentation_deck_agent": ("M9_presentation_delivery", "freeze_low_priority"),
}


CORE_ANCHOR_AGENTS = {
    "sensor_network_sparse_placement_agent",
    "multi_facility_collaborative_control_agent",
    "catalyst_activity_proxy_agent",
    "multi_facility_replay_evaluation_agent",
    "minimal_grey_box_physics_agent",
    "soft_sensor_matrix_coupling_agent",
    "engineering_execution_constraint_agent",
    "knowledge_graph_reasoning_agent",
    "claim_specific_field_package_agent",
    "timestamped_campaign_replay_agent",
    "field_replay_import_agent",
    "field_replay_evidence_chain_agent",
}


class AgentArchitectureConsolidationAgent(BaseAgent):
    """Map many historical agents into fewer model modules and expose refactor priority."""

    name = "agent_architecture_consolidation_agent"

    def __init__(
        self,
        *,
        agent_names: Sequence[str] | None = None,
        experiment_names: Sequence[str] | None = None,
        agent_run_numbers: dict[str, int] | None = None,
        priority_ranking: dict[str, object] | None = None,
        core_metrics: dict[str, object] | None = None,
        external_architecture_evidence: Sequence[dict[str, object]] | None = None,
        nonlegal_prior_art_seed_matrix: dict[str, object] | None = None,
        formal_search_result_package_path: str | None = None,
        formal_search_nonlegal_review_response_path: str | None = None,
        formal_counsel_review_response_path: str | None = None,
    ) -> None:
        self.agent_names = sorted(set(agent_names or AGENT_MODULE_MAP.keys()))
        self.experiment_names = sorted(set(experiment_names or ()))
        self.agent_run_numbers = agent_run_numbers or {}
        self.priority_ranking = priority_ranking or {}
        self.core_metrics = core_metrics or {}
        self.external_architecture_evidence = list(external_architecture_evidence or self._default_external_evidence())
        self.nonlegal_prior_art_seed_matrix = nonlegal_prior_art_seed_matrix or {}
        self.formal_search_result_package_path = formal_search_result_package_path
        self.formal_search_nonlegal_review_response_path = (
            formal_search_nonlegal_review_response_path
        )
        self.formal_counsel_review_response_path = formal_counsel_review_response_path

    def run(self, readings: Sequence[SensorReading]) -> AgentReport:
        del readings
        evidence_status = self._external_evidence_status()
        audit_table = self._agent_audit_table()
        module_board = self._module_board(audit_table)
        system_spine_map = self._system_spine_map(module_board)
        system_layer_board = self._system_layer_board(system_spine_map)
        system_spine_coverage = self._system_spine_coverage(system_layer_board, system_spine_map)
        module_interface_contracts = self._module_interface_contracts(module_board)
        interface_contract_coverage = self._interface_contract_coverage(module_interface_contracts)
        redundancy_clusters = self._redundancy_clusters(audit_table)
        consumption_map = self._core_consumption_map()
        next_actions = self._ranked_refactor_actions(redundancy_clusters)
        offline_core_fallback = self._offline_core_fallback_action(next_actions)
        patent_technical_feature_ledger = self._patent_technical_feature_ledger(
            module_board=module_board,
            system_spine_map=system_spine_map,
            module_interface_contracts=module_interface_contracts,
        )
        patent_technical_feature_coverage = self._patent_technical_feature_coverage(
            patent_technical_feature_ledger
        )
        technical_claim_skeleton_scaffold = self._technical_claim_skeleton_scaffold(
            patent_technical_feature_ledger
        )
        technical_claim_skeleton_coverage = self._technical_claim_skeleton_coverage(
            technical_claim_skeleton_scaffold
        )
        technical_embodiment_validation_matrix = self._technical_embodiment_validation_matrix(
            patent_technical_feature_ledger=patent_technical_feature_ledger,
            technical_claim_skeleton_scaffold=technical_claim_skeleton_scaffold,
        )
        technical_embodiment_validation_coverage = self._technical_embodiment_validation_coverage(
            technical_embodiment_validation_matrix
        )
        technical_effect_measurement_matrix = self._technical_effect_measurement_matrix(
            technical_embodiment_validation_matrix
        )
        technical_effect_measurement_coverage = self._technical_effect_measurement_coverage(
            technical_effect_measurement_matrix=technical_effect_measurement_matrix,
            technical_embodiment_validation_matrix=technical_embodiment_validation_matrix,
        )
        prior_art_distinction_matrix = self._prior_art_distinction_matrix(
            technical_claim_skeleton_scaffold=technical_claim_skeleton_scaffold,
            patent_technical_feature_ledger=patent_technical_feature_ledger,
            technical_effect_measurement_matrix=technical_effect_measurement_matrix,
        )
        prior_art_distinction_coverage = self._prior_art_distinction_coverage(
            prior_art_distinction_matrix=prior_art_distinction_matrix,
            technical_claim_skeleton_scaffold=technical_claim_skeleton_scaffold,
            patent_technical_feature_ledger=patent_technical_feature_ledger,
            technical_effect_measurement_matrix=technical_effect_measurement_matrix,
        )
        formal_search_work_package_matrix = self._formal_search_work_package_matrix(
            prior_art_distinction_matrix
        )
        formal_search_work_package_coverage = self._formal_search_work_package_coverage(
            formal_search_work_package_matrix=formal_search_work_package_matrix,
            prior_art_distinction_matrix=prior_art_distinction_matrix,
        )
        formal_search_result_intake_schema = self._formal_search_result_intake_schema(
            formal_search_work_package_matrix
        )
        formal_search_result_intake_coverage = self._formal_search_result_intake_coverage(
            formal_search_result_intake_schema=formal_search_result_intake_schema,
            formal_search_work_package_matrix=formal_search_work_package_matrix,
        )
        formal_search_result_validation_gate = self._formal_search_result_validation_gate(
            formal_search_result_intake_schema=formal_search_result_intake_schema,
            formal_search_work_package_matrix=formal_search_work_package_matrix,
        )
        formal_search_result_validation_gate_coverage = self._formal_search_result_validation_gate_coverage(
            formal_search_result_validation_gate=formal_search_result_validation_gate,
            formal_search_result_intake_schema=formal_search_result_intake_schema,
        )
        formal_search_result_package_template = self._formal_search_result_package_template(
            formal_search_result_validation_gate
        )
        formal_search_result_package_template_coverage = self._formal_search_result_package_template_coverage(
            formal_search_result_package_template=formal_search_result_package_template,
            formal_search_result_validation_gate=formal_search_result_validation_gate,
        )
        formal_search_result_package_submission_template = (
            self._formal_search_result_package_submission_template(
                formal_search_result_package_template
            )
        )
        formal_search_result_package_source_preflight = self._formal_search_result_package_source_preflight(
            formal_search_result_package_template
        )
        formal_search_result_package_row_preflight = self._formal_search_result_package_row_preflight(
            formal_search_result_package_template=formal_search_result_package_template,
            source_preflight=formal_search_result_package_source_preflight,
        )
        formal_search_result_validation_execution = self._formal_search_result_validation_execution(
            formal_search_result_validation_gate=formal_search_result_validation_gate,
            formal_search_result_package_template=formal_search_result_package_template,
            source_preflight=formal_search_result_package_source_preflight,
            row_preflight=formal_search_result_package_row_preflight,
        )
        formal_search_nonlegal_comparison_review_packet = (
            self._formal_search_nonlegal_comparison_review_packet(
                validation_execution=formal_search_result_validation_execution,
            )
        )
        formal_search_nonlegal_review_response_template = (
            self._formal_search_nonlegal_review_response_template(
                review_packet=formal_search_nonlegal_comparison_review_packet,
            )
        )
        formal_search_nonlegal_review_response_source_preflight = (
            self._formal_search_nonlegal_review_response_source_preflight(
                review_packet=formal_search_nonlegal_comparison_review_packet,
                response_template=formal_search_nonlegal_review_response_template,
            )
        )
        formal_search_claim_scope_patch_draft = self._formal_search_claim_scope_patch_draft(
            response_preflight=formal_search_nonlegal_review_response_source_preflight,
        )
        formal_counsel_review_response_template = (
            self._formal_counsel_review_response_template(
                claim_scope_patch_draft=formal_search_claim_scope_patch_draft,
            )
        )
        formal_counsel_review_response_source_preflight = (
            self._formal_counsel_review_response_source_preflight(
                response_template=formal_counsel_review_response_template,
            )
        )
        formal_disclosure_revision_queue = self._formal_disclosure_revision_queue(
            formal_counsel_preflight=formal_counsel_review_response_source_preflight,
        )
        formal_disclosure_revision_impact_plan = self._formal_disclosure_revision_impact_plan(
            disclosure_revision_queue=formal_disclosure_revision_queue,
        )
        formal_search_review_readiness = self._formal_search_review_readiness(
            source_preflight=formal_search_result_package_source_preflight,
            row_preflight=formal_search_result_package_row_preflight,
            validation_execution=formal_search_result_validation_execution,
            nonlegal_review_packet=formal_search_nonlegal_comparison_review_packet,
            nonlegal_response_preflight=formal_search_nonlegal_review_response_source_preflight,
            claim_scope_patch_draft=formal_search_claim_scope_patch_draft,
            formal_counsel_preflight=formal_counsel_review_response_source_preflight,
            disclosure_revision_queue=formal_disclosure_revision_queue,
            disclosure_revision_impact_plan=formal_disclosure_revision_impact_plan,
        )
        formal_search_execution_route_plan = self._formal_search_execution_route_plan(
            formal_search_work_package_matrix=formal_search_work_package_matrix,
            formal_search_result_package_template=formal_search_result_package_template,
            formal_search_result_package_submission_template=(
                formal_search_result_package_submission_template
            ),
            formal_search_review_readiness=formal_search_review_readiness,
            nonlegal_prior_art_seed_matrix=self.nonlegal_prior_art_seed_matrix,
        )
        unmapped_agents = [row for row in audit_table if row["module_id"] == "UNMAPPED"]
        presentation_agents = [row for row in audit_table if row["module_id"] == "M9_presentation_delivery"]
        core_anchor_coverage = self._core_anchor_coverage(audit_table)
        consolidation_score = self._consolidation_score(
            audit_table=audit_table,
            module_board=module_board,
            redundancy_clusters=redundancy_clusters,
            evidence_status=evidence_status,
            core_anchor_coverage=core_anchor_coverage,
            system_spine_coverage=system_spine_coverage,
            interface_contract_coverage=interface_contract_coverage,
        )
        self_interrupt_verdict = self._self_interrupt_verdict(audit_table, next_actions)
        issues = self._issues(
            unmapped_agents=unmapped_agents,
            presentation_agents=presentation_agents,
            evidence_status=evidence_status,
            core_anchor_coverage=core_anchor_coverage,
            system_spine_coverage=system_spine_coverage,
            interface_contract_coverage=interface_contract_coverage,
        )
        summary = (
            "架构复盘治理："
            f"已将 {len(audit_table)} 个 agent 映射到 {len(module_board)} 个模块，"
            f"七层骨架覆盖 {system_spine_coverage['layer_coverage_rate']:.3f}，"
            f"识别 {len(redundancy_clusters)} 个合并/冻结簇，"
            f"下一步为 `{next_actions[0]['action_id']}`。"
        )
        confidence = round(
            min(0.94, max(0.35, 0.45 + 0.36 * consolidation_score + 0.12 * evidence_status["completeness_score"])),
            3,
        )
        return AgentReport(
            agent_name=self.name,
            confidence=confidence,
            summary=summary,
            issues=issues,
            recommendations=self._recommendations(next_actions, self_interrupt_verdict, offline_core_fallback),
            metrics={
                "architecture_status": "module_consolidation_ready_with_complete_interface_contracts",
                "agent_count": len(audit_table),
                "mapped_agent_count": len(audit_table) - len(unmapped_agents),
                "unmapped_agent_count": len(unmapped_agents),
                "module_count": len(module_board),
                "system_spine_coverage": system_spine_coverage,
                "system_layer_board": system_layer_board,
                "system_spine_map": system_spine_map,
                "module_interface_contracts": module_interface_contracts,
                "interface_contract_coverage": interface_contract_coverage,
                "core_model_module_count": len(
                    [module for module in module_board if module["module_type"] == "core_model"]
                ),
                "presentation_freeze_agent_count": len(presentation_agents),
                "core_anchor_coverage": core_anchor_coverage,
                "redundancy_cluster_count": len(redundancy_clusters),
                "consolidation_candidate_count": len(
                    [
                        row
                        for row in audit_table
                        if str(row["retention_decision"]).startswith(("merge", "compress", "freeze"))
                    ]
                ),
                "consolidation_readiness_score": consolidation_score,
                "self_interrupt_verdict": self_interrupt_verdict,
                "module_board": module_board,
                "agent_audit_table": audit_table,
                "redundancy_clusters": redundancy_clusters,
                "core_consumption_map": consumption_map,
                "patent_technical_feature_ledger": patent_technical_feature_ledger,
                "patent_technical_feature_coverage": patent_technical_feature_coverage,
                "technical_claim_skeleton_scaffold": technical_claim_skeleton_scaffold,
                "technical_claim_skeleton_coverage": technical_claim_skeleton_coverage,
                "technical_embodiment_validation_matrix": technical_embodiment_validation_matrix,
                "technical_embodiment_validation_coverage": technical_embodiment_validation_coverage,
                "technical_effect_measurement_matrix": technical_effect_measurement_matrix,
                "technical_effect_measurement_coverage": technical_effect_measurement_coverage,
                "prior_art_distinction_matrix": prior_art_distinction_matrix,
                "prior_art_distinction_coverage": prior_art_distinction_coverage,
                "formal_search_work_package_matrix": formal_search_work_package_matrix,
                "formal_search_work_package_coverage": formal_search_work_package_coverage,
                "formal_search_result_intake_schema": formal_search_result_intake_schema,
                "formal_search_result_intake_coverage": formal_search_result_intake_coverage,
                "formal_search_result_validation_gate": formal_search_result_validation_gate,
                "formal_search_result_validation_gate_coverage": formal_search_result_validation_gate_coverage,
                "formal_search_result_package_template": formal_search_result_package_template,
                "formal_search_result_package_template_coverage": formal_search_result_package_template_coverage,
                "formal_search_result_package_submission_template": (
                    formal_search_result_package_submission_template
                ),
                "formal_search_result_package_source_preflight": formal_search_result_package_source_preflight,
                "formal_search_result_package_row_preflight": formal_search_result_package_row_preflight,
                "formal_search_result_validation_execution": formal_search_result_validation_execution,
                "formal_search_nonlegal_comparison_review_packet": (
                    formal_search_nonlegal_comparison_review_packet
                ),
                "formal_search_nonlegal_review_response_template": (
                    formal_search_nonlegal_review_response_template
                ),
                "formal_search_nonlegal_review_response_source_preflight": (
                    formal_search_nonlegal_review_response_source_preflight
                ),
                "formal_search_claim_scope_patch_draft": formal_search_claim_scope_patch_draft,
                "formal_counsel_review_response_template": formal_counsel_review_response_template,
                "formal_counsel_review_response_source_preflight": (
                    formal_counsel_review_response_source_preflight
                ),
                "formal_disclosure_revision_queue": formal_disclosure_revision_queue,
                "formal_disclosure_revision_impact_plan": formal_disclosure_revision_impact_plan,
                "formal_search_review_readiness": formal_search_review_readiness,
                "formal_search_execution_route_plan": formal_search_execution_route_plan,
                "ranked_refactor_actions": next_actions,
                "offline_core_fallback_action": offline_core_fallback,
                "external_architecture_evidence_status": evidence_status,
                "cannot_delete_or_merge_code_automatically": True,
                "field_validation_boundary": (
                    "本轮是架构治理与接口复盘，不产生 field-supported 结论，不写执行器或 release gate。"
                ),
            },
        )

    @staticmethod
    def _default_external_evidence() -> list[dict[str, object]]:
        return [
            {
                "source": "LangChain multi-agent patterns, https://docs.langchain.com/oss/python/langchain/multi-agent",
                "method_family": "multi-agent graph, supervisor, network and handoff patterns",
                "model_mapping": "把 59 个历史 agent 从线性编号改成模块图，明确 supervisor/governance、handoff 和共享状态边界。",
                "data_needs": "agent 输入/输出、共享状态、下游消费者、失败边界和中断条件。",
                "implementation_path": "Agent60 先输出模块图谱和消费关系；后续再决定是否把运行链改成显式 graph orchestration。",
                "evaluation_metrics": [
                    "mapped_agent_count",
                    "core_consumption_link_count",
                    "unmapped_agent_count",
                    "self_interrupt_verdict",
                ],
                "failure_boundary": "该资料提供编排模式，不提供水处理机理或现场验证结论。",
            },
            {
                "source": "Microsoft AutoGen AgentChat documentation, https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/index.html",
                "method_family": "multi-agent conversation, team and workflow organization",
                "model_mapping": "借鉴 team/workflow 分层思想，把 field evidence、KG、控制和展示从同一 agent 序列中分离。",
                "data_needs": "角色边界、消息接口、可终止条件、人工复核点和重复职责列表。",
                "implementation_path": "把冗余 gate、claim package 和展示 agent 标注为合并/冻结候选，而不是继续扩张 agent 数量。",
                "evaluation_metrics": [
                    "redundancy_cluster_count",
                    "presentation_freeze_agent_count",
                    "consolidation_candidate_count",
                ],
                "failure_boundary": "通用多智能体 workflow 不能替代本项目的状态、动作、奖励和证据门控定义。",
            },
            {
                "source": "OpenAI Agents SDK handoffs documentation, https://openai.github.io/openai-agents-python/handoffs/",
                "method_family": "agent handoffs and explicit responsibility transfer",
                "model_mapping": "把 Agent48/51/54 到 Agent49/52/55，再到 Agent56/59 的承接关系写成显式 consumption map。",
                "data_needs": "handoff 输入契约、输出契约、验证指标、阻断条件和不可写回边界。",
                "implementation_path": "Agent60 输出 core_consumption_map；下一轮优先修复没有清晰消费者或重复 gate 的模块。",
                "evaluation_metrics": [
                    "core_anchor_coverage",
                    "handoff_contract_count",
                    "orphan_agent_count",
                ],
                "failure_boundary": "handoff 是软件架构方法，不能证明 synthetic 策略在现场有效。",
            },
        ]

    def _external_evidence_status(self) -> dict[str, object]:
        incomplete: list[dict[str, object]] = []
        for index, record in enumerate(self.external_architecture_evidence, start=1):
            missing = [field for field in REQUIRED_ARCHITECTURE_EVIDENCE_FIELDS if not record.get(field)]
            if missing:
                incomplete.append({"record_index": index, "source": record.get("source", "unknown"), "missing": missing})
        complete_count = len(self.external_architecture_evidence) - len(incomplete)
        return {
            "required_fields": list(REQUIRED_ARCHITECTURE_EVIDENCE_FIELDS),
            "record_count": len(self.external_architecture_evidence),
            "complete_record_count": complete_count,
            "incomplete_records": incomplete,
            "completeness_score": round(complete_count / max(1, len(self.external_architecture_evidence)), 3),
            "status": "architecture_evidence_complete" if self.external_architecture_evidence and not incomplete else "architecture_evidence_needs_patch",
        }

    def _agent_audit_table(self) -> list[dict[str, object]]:
        rows: list[dict[str, object]] = []
        for agent_name in self.agent_names:
            module_id, retention = AGENT_MODULE_MAP.get(agent_name, ("UNMAPPED", "needs_manual_mapping"))
            module = self._module_by_id(module_id)
            rows.append(
                {
                    "agent_name": agent_name,
                    "agent_number": self.agent_run_numbers.get(agent_name),
                    "module_id": module_id,
                    "module_title": module.get("title", "未映射模块"),
                    "module_type": module.get("module_type", "unknown"),
                    "retention_decision": retention,
                    "is_core_anchor": agent_name in CORE_ANCHOR_AGENTS,
                    "model_core_contribution": self._model_core_contribution(agent_name, module_id, retention),
                    "consumer_expectation": self._consumer_expectation(agent_name),
                    "failure_boundary": module.get("failure_boundary", "需要人工确认边界。"),
                }
            )
        rows.sort(key=lambda row: (str(row["module_id"]), row["agent_number"] or 999, str(row["agent_name"])))
        return rows

    def _module_board(self, audit_table: list[dict[str, object]]) -> list[dict[str, object]]:
        agents_by_module: dict[str, list[dict[str, object]]] = defaultdict(list)
        for row in audit_table:
            agents_by_module[str(row["module_id"])].append(row)
        board: list[dict[str, object]] = []
        for blueprint in MODULE_BLUEPRINTS:
            module_id = str(blueprint["module_id"])
            rows = agents_by_module.get(module_id, [])
            retention_counts = Counter(str(row["retention_decision"]) for row in rows)
            board.append(
                {
                    **blueprint,
                    "agent_count": len(rows),
                    "agents": [row["agent_name"] for row in rows],
                    "core_anchor_agents": [row["agent_name"] for row in rows if row["is_core_anchor"]],
                    "retention_counts": dict(retention_counts),
                    "module_consolidation_policy": self._module_consolidation_policy(module_id, retention_counts),
                }
            )
        if agents_by_module.get("UNMAPPED"):
            board.append(
                {
                    "module_id": "UNMAPPED",
                    "title": "未映射 Agent",
                    "model_role": "需要人工决定是否属于核心模型。",
                    "core_question": "这些 agent 是否应继续存在？",
                    "module_type": "needs_review",
                    "agent_count": len(agents_by_module["UNMAPPED"]),
                    "agents": [row["agent_name"] for row in agents_by_module["UNMAPPED"]],
                    "core_anchor_agents": [],
                    "retention_counts": {"needs_manual_mapping": len(agents_by_module["UNMAPPED"])},
                    "module_consolidation_policy": "block_new_work_until_mapped",
                    "failure_boundary": "未映射 agent 不能进入核心链路结论。",
                }
            )
        return board

    @staticmethod
    def _system_spine_map(module_board: list[dict[str, object]]) -> list[dict[str, object]]:
        rows: list[dict[str, object]] = []
        for module in module_board:
            module_id = str(module["module_id"])
            spine = MODULE_SYSTEM_SPINE_MAP.get(
                module_id,
                {
                    "primary_layer": "UNMAPPED_SYSTEM_LAYER",
                    "secondary_layers": [],
                    "core_abilities": [],
                    "spine_role": "该模块尚未映射到全局七层骨架。",
                },
            )
            primary_layer = str(spine["primary_layer"])
            secondary_layers = list(spine.get("secondary_layers", []))
            all_layers = [primary_layer, *secondary_layers]
            core_abilities = list(spine.get("core_abilities", []))
            rows.append(
                {
                    "module_id": module_id,
                    "module_title": module.get("title", ""),
                    "module_type": module.get("module_type", ""),
                    "primary_layer": primary_layer,
                    "secondary_layers": secondary_layers,
                    "all_layers": all_layers,
                    "core_abilities": core_abilities,
                    "spine_role": spine.get("spine_role", ""),
                    "agent_count": module.get("agent_count", 0),
                    "core_anchor_agents": module.get("core_anchor_agents", []),
                    "spine_policy": "freeze_outside_model_spine"
                    if primary_layer == "OUTSIDE_MODEL_SPINE"
                    else "keep_inside_global_system_spine",
                    "is_inside_model_spine": primary_layer not in {"OUTSIDE_MODEL_SPINE", "UNMAPPED_SYSTEM_LAYER"},
                }
            )
        return rows

    @staticmethod
    def _system_layer_board(system_spine_map: list[dict[str, object]]) -> list[dict[str, object]]:
        rows: list[dict[str, object]] = []
        for layer in SYSTEM_LAYER_BLUEPRINTS:
            layer_id = str(layer["layer_id"])
            primary_modules = [
                str(row["module_id"])
                for row in system_spine_map
                if row["primary_layer"] == layer_id
            ]
            secondary_modules = [
                str(row["module_id"])
                for row in system_spine_map
                if layer_id in row["secondary_layers"]
            ]
            modules = sorted(set(primary_modules + secondary_modules))
            ability_set: set[str] = set()
            for row in system_spine_map:
                if row["module_id"] in modules:
                    ability_set.update(str(ability) for ability in row.get("core_abilities", []))
            rows.append(
                {
                    **layer,
                    "primary_modules": primary_modules,
                    "secondary_modules": secondary_modules,
                    "modules": modules,
                    "module_count": len(modules),
                    "core_abilities": sorted(ability_set),
                    "coverage_status": "covered" if modules else "missing",
                }
            )
        return rows

    @staticmethod
    def _system_spine_coverage(
        system_layer_board: list[dict[str, object]],
        system_spine_map: list[dict[str, object]],
    ) -> dict[str, object]:
        covered_layers = [
            str(row["layer_id"])
            for row in system_layer_board
            if row["coverage_status"] == "covered"
        ]
        missing_layers = [
            str(row["layer_id"])
            for row in system_layer_board
            if row["coverage_status"] != "covered"
        ]
        covered_abilities = sorted(
            {
                str(ability)
                for row in system_spine_map
                for ability in row.get("core_abilities", [])
            }
        )
        missing_abilities = [
            ability for ability in REQUIRED_SYSTEM_ABILITIES if ability not in covered_abilities
        ]
        outside_modules = [
            str(row["module_id"])
            for row in system_spine_map
            if row["primary_layer"] == "OUTSIDE_MODEL_SPINE"
        ]
        unmapped_modules = [
            str(row["module_id"])
            for row in system_spine_map
            if row["primary_layer"] == "UNMAPPED_SYSTEM_LAYER"
        ]
        layer_coverage_rate = round(len(covered_layers) / max(1, len(SYSTEM_LAYER_BLUEPRINTS)), 3)
        ability_coverage_rate = round(
            len(covered_abilities) / max(1, len(REQUIRED_SYSTEM_ABILITIES)),
            3,
        )
        status = (
            "global_system_spine_mapped_with_frozen_expression_layer"
            if layer_coverage_rate == 1.0 and ability_coverage_rate == 1.0 and not unmapped_modules
            else "global_system_spine_mapping_needs_patch"
        )
        return {
            "system_spine_status": status,
            "required_layer_count": len(SYSTEM_LAYER_BLUEPRINTS),
            "covered_layer_count": len(covered_layers),
            "layer_coverage_rate": layer_coverage_rate,
            "covered_layers": covered_layers,
            "missing_layers": missing_layers,
            "required_abilities": list(REQUIRED_SYSTEM_ABILITIES),
            "covered_abilities": covered_abilities,
            "missing_abilities": missing_abilities,
            "ability_coverage_rate": ability_coverage_rate,
            "outside_model_spine_modules": outside_modules,
            "outside_model_spine_module_count": len(outside_modules),
            "unmapped_system_layer_modules": unmapped_modules,
            "unmapped_system_layer_module_count": len(unmapped_modules),
            "presentation_layer_policy": "freeze_outside_model_spine_until_model_metrics_change",
        }

    @staticmethod
    def _module_interface_contracts(module_board: list[dict[str, object]]) -> list[dict[str, object]]:
        contracts: list[dict[str, object]] = []
        for module in module_board:
            module_id = str(module["module_id"])
            contract = MODULE_INTERFACE_CONTRACTS.get(module_id, {})
            missing = [field for field in REQUIRED_MODULE_INTERFACE_FIELDS if not contract.get(field)]
            contracts.append(
                {
                    "module_id": module_id,
                    "module_title": module.get("title", ""),
                    "module_type": module.get("module_type", ""),
                    "required_fields": list(REQUIRED_MODULE_INTERFACE_FIELDS),
                    "missing_contract_fields": missing,
                    "contract_status": "interface_contract_complete"
                    if not missing
                    else "interface_contract_needs_patch",
                    **{field: contract.get(field, "") for field in REQUIRED_MODULE_INTERFACE_FIELDS},
                }
            )
        return contracts

    @staticmethod
    def _interface_contract_coverage(module_interface_contracts: list[dict[str, object]]) -> dict[str, object]:
        complete = [
            contract
            for contract in module_interface_contracts
            if contract["contract_status"] == "interface_contract_complete"
        ]
        incomplete = [
            {
                "module_id": contract["module_id"],
                "missing_contract_fields": contract["missing_contract_fields"],
            }
            for contract in module_interface_contracts
            if contract["contract_status"] != "interface_contract_complete"
        ]
        coverage_rate = round(len(complete) / max(1, len(module_interface_contracts)), 3)
        return {
            "interface_contract_status": "all_module_interface_contracts_complete"
            if coverage_rate == 1.0
            else "module_interface_contracts_need_patch",
            "required_contract_fields": list(REQUIRED_MODULE_INTERFACE_FIELDS),
            "module_contract_count": len(module_interface_contracts),
            "complete_module_contract_count": len(complete),
            "incomplete_module_contracts": incomplete,
            "interface_contract_coverage_rate": coverage_rate,
        }

    @staticmethod
    def _patent_technical_feature_ledger(
        *,
        module_board: list[dict[str, object]],
        system_spine_map: list[dict[str, object]],
        module_interface_contracts: list[dict[str, object]],
    ) -> list[dict[str, object]]:
        module_by_id = {str(module["module_id"]): module for module in module_board}
        spine_by_id = {str(row["module_id"]): row for row in system_spine_map}
        contract_by_id = {str(contract["module_id"]): contract for contract in module_interface_contracts}
        rows: list[dict[str, object]] = []
        for blueprint in PATENT_TECHNICAL_FEATURE_BLUEPRINTS:
            module_id = str(blueprint["module_id"])
            module = module_by_id.get(module_id, {})
            spine = spine_by_id.get(module_id, {})
            contract = contract_by_id.get(module_id, {})
            mapped_layers = [
                layer
                for layer in [spine.get("primary_layer"), *list(spine.get("secondary_layers", []))]
                if layer and layer != "OUTSIDE_MODEL_SPINE"
            ]
            row = {
                **blueprint,
                "module_title": module.get("title", ""),
                "mapped_layers": mapped_layers,
                "core_abilities": list(spine.get("core_abilities", [])),
                "module_inputs": contract.get("input_contract", ""),
                "module_outputs": contract.get("output_contract", ""),
                "state_variables": list(contract.get("state_variables", [])),
                "interface_metrics": list(contract.get("transferable_metrics", [])),
                "upstream_dependencies": list(contract.get("upstream_dependencies", [])),
                "downstream_consumers": list(contract.get("downstream_consumers", [])),
                "field_claim_status": "not_field_supported_until_replay_holdout_operator_review_and_release_gate_pass",
                "legal_status": "technical_disclosure_candidate_not_legal_advice",
            }
            missing = [
                field
                for field in REQUIRED_PATENT_TECHNICAL_FEATURE_FIELDS
                if not row.get(field)
            ]
            row["missing_feature_fields"] = missing
            row["abstract_only_risk"] = AgentArchitectureConsolidationAgent._abstract_only_feature_risk(row)
            row["feature_status"] = (
                "technical_feature_candidate_complete_not_field_claim"
                if not missing and not row["abstract_only_risk"]
                else "technical_feature_needs_patch"
            )
            rows.append(row)
        return rows

    @staticmethod
    def _abstract_only_feature_risk(row: dict[str, object]) -> bool:
        text = " ".join(
            str(row.get(field, ""))
            for field in (
                "technical_problem",
                "technical_means",
                "system_structure",
                "control_actions",
                "implementation_example",
                "verification_metrics",
                "technical_effect",
                "prior_art_distinction",
            )
        )
        abstract_terms = ("AI", "多智能体", "知识图谱", "闭环控制")
        concrete_markers = (
            "node-modality",
            "稀疏",
            "软传感",
            "灰箱",
            "隐藏状态",
            "缺测",
            "replay",
            "holdout",
            "release gate",
            "field package",
            "回流",
            "暂存",
            "投药",
            "催化剂",
            "R7",
            "R8p",
            "R8v",
            "压降",
            "operator review",
            "状态变量",
        )
        return any(term in text for term in abstract_terms) and not any(marker in text for marker in concrete_markers)

    @staticmethod
    def _patent_technical_feature_coverage(
        patent_technical_feature_ledger: list[dict[str, object]],
    ) -> dict[str, object]:
        complete = [
            row
            for row in patent_technical_feature_ledger
            if row["feature_status"] == "technical_feature_candidate_complete_not_field_claim"
        ]
        incomplete = [
            {
                "feature_id": row["feature_id"],
                "module_id": row["module_id"],
                "missing_feature_fields": row["missing_feature_fields"],
                "abstract_only_risk": row["abstract_only_risk"],
            }
            for row in patent_technical_feature_ledger
            if row["feature_status"] != "technical_feature_candidate_complete_not_field_claim"
        ]
        abstract_only = [
            str(row["feature_id"])
            for row in patent_technical_feature_ledger
            if row["abstract_only_risk"]
        ]
        coverage_rate = round(len(complete) / max(1, len(patent_technical_feature_ledger)), 3)
        return {
            "patent_technical_feature_status": (
                "technical_feature_ledger_ready_as_disclosure_scaffold_not_field_claim"
                if coverage_rate == 1.0 and not abstract_only
                else "technical_feature_ledger_needs_patch"
            ),
            "feature_count": len(patent_technical_feature_ledger),
            "complete_feature_count": len(complete),
            "incomplete_features": incomplete,
            "abstract_only_feature_ids": abstract_only,
            "technical_feature_coverage_rate": coverage_rate,
            "field_claim_upgrade_allowed": False,
            "field_claim_upgrade_boundary": (
                "该 ledger 只证明技术方案骨架更清楚；任何现场成立 claim 仍必须通过 "
                "R7/R8p/R8v、field holdout、operator review 和 release gate。"
            ),
            "legal_status": "technical_disclosure_candidate_not_legal_advice",
            "excluded_modules": ["M9_presentation_delivery"],
        }

    @staticmethod
    def _technical_claim_skeleton_scaffold(
        patent_technical_feature_ledger: list[dict[str, object]],
    ) -> list[dict[str, object]]:
        features_by_id = {
            str(feature["feature_id"]): feature
            for feature in patent_technical_feature_ledger
        }
        rows: list[dict[str, object]] = []
        for blueprint in TECHNICAL_CLAIM_SCAFFOLD_BLUEPRINTS:
            mapped_feature_ids = [str(feature_id) for feature_id in blueprint["mapped_feature_ids"]]
            linked_features = [
                features_by_id[feature_id]
                for feature_id in mapped_feature_ids
                if feature_id in features_by_id
            ]
            missing_feature_ids = [
                feature_id
                for feature_id in mapped_feature_ids
                if feature_id not in features_by_id
            ]
            linked_modules = sorted(
                {
                    str(feature["module_id"])
                    for feature in linked_features
                }
            )
            linked_feature_statuses = {
                str(feature["feature_id"]): str(feature["feature_status"])
                for feature in linked_features
            }
            row = {
                **blueprint,
                "linked_modules": linked_modules,
                "linked_feature_statuses": linked_feature_statuses,
                "missing_feature_ids": missing_feature_ids,
                "field_claim_status": "not_field_supported_until_required_gates_pass",
                "claim_upgrade_allowed": False,
            }
            missing_fields = [
                field
                for field in REQUIRED_TECHNICAL_CLAIM_SCAFFOLD_FIELDS
                if not row.get(field)
            ]
            row["missing_claim_fields"] = missing_fields
            row["abstract_only_risk"] = AgentArchitectureConsolidationAgent._abstract_only_claim_risk(row)
            row["claim_scaffold_status"] = (
                "technical_claim_scaffold_complete_not_legal_claim_not_field_claim"
                if not missing_fields
                and not missing_feature_ids
                and not row["abstract_only_risk"]
                and linked_features
                else "technical_claim_scaffold_needs_patch"
            )
            rows.append(row)
        return rows

    @staticmethod
    def _abstract_only_claim_risk(row: dict[str, object]) -> bool:
        text = " ".join(
            str(row.get(field, ""))
            for field in (
                "technical_problem",
                "technical_combination",
                "method_steps",
                "system_components",
                "state_variables",
                "control_actions",
                "verification_gates",
                "technical_effect",
                "prior_art_distinction",
            )
        )
        abstract_terms = ("AI", "多智能体", "知识图谱", "闭环控制")
        concrete_markers = (
            "node-modality",
            "稀疏",
            "软传感",
            "灰箱",
            "隐藏状态",
            "缺测",
            "replay",
            "holdout",
            "release gate",
            "field package",
            "回流",
            "暂存",
            "投药",
            "催化剂",
            "R7",
            "R8p",
            "R8v",
            "压降",
            "operator review",
            "field",
            "状态变量",
            "验证",
        )
        return any(term in text for term in abstract_terms) and not any(marker in text for marker in concrete_markers)

    @staticmethod
    def _technical_claim_skeleton_coverage(
        technical_claim_skeleton_scaffold: list[dict[str, object]],
    ) -> dict[str, object]:
        complete = [
            row
            for row in technical_claim_skeleton_scaffold
            if row["claim_scaffold_status"] == "technical_claim_scaffold_complete_not_legal_claim_not_field_claim"
        ]
        incomplete = [
            {
                "claim_id": row["claim_id"],
                "claim_type": row["claim_type"],
                "missing_claim_fields": row["missing_claim_fields"],
                "missing_feature_ids": row["missing_feature_ids"],
                "abstract_only_risk": row["abstract_only_risk"],
            }
            for row in technical_claim_skeleton_scaffold
            if row["claim_scaffold_status"] != "technical_claim_scaffold_complete_not_legal_claim_not_field_claim"
        ]
        independent_claims = [
            str(row["claim_id"])
            for row in technical_claim_skeleton_scaffold
            if str(row["claim_type"]).startswith("independent")
        ]
        dependent_claims = [
            str(row["claim_id"])
            for row in technical_claim_skeleton_scaffold
            if str(row["claim_type"]).startswith("dependent")
        ]
        covered_feature_ids = sorted(
            {
                str(feature_id)
                for row in technical_claim_skeleton_scaffold
                for feature_id in row.get("mapped_feature_ids", [])
            }
        )
        required_feature_ids = [
            str(feature["feature_id"])
            for feature in PATENT_TECHNICAL_FEATURE_BLUEPRINTS
        ]
        missing_feature_coverage = [
            feature_id
            for feature_id in required_feature_ids
            if feature_id not in covered_feature_ids
        ]
        coverage_rate = round(len(complete) / max(1, len(technical_claim_skeleton_scaffold)), 3)
        return {
            "technical_claim_skeleton_status": (
                "technical_claim_skeleton_ready_as_scaffold_not_legal_claim_not_field_claim"
                if coverage_rate == 1.0 and not incomplete and not missing_feature_coverage
                else "technical_claim_skeleton_needs_patch"
            ),
            "claim_scaffold_count": len(technical_claim_skeleton_scaffold),
            "complete_claim_scaffold_count": len(complete),
            "independent_claim_scaffold_ids": independent_claims,
            "dependent_or_divisional_scaffold_ids": dependent_claims,
            "incomplete_claim_scaffolds": incomplete,
            "covered_feature_ids": covered_feature_ids,
            "missing_feature_coverage": missing_feature_coverage,
            "technical_claim_skeleton_coverage_rate": coverage_rate,
            "field_claim_upgrade_allowed": False,
            "legal_status": "technical_claim_scaffold_not_legal_advice",
            "field_claim_upgrade_boundary": (
                "该 scaffold 只把技术方案组合成方法/系统/从属方向骨架；任何现场成立 claim 或执行器写回仍必须通过 "
                "R7/R8p/R8v、field holdout、operator review 和 release gate。"
            ),
        }

    @staticmethod
    def _technical_embodiment_validation_matrix(
        *,
        patent_technical_feature_ledger: list[dict[str, object]],
        technical_claim_skeleton_scaffold: list[dict[str, object]],
    ) -> list[dict[str, object]]:
        features_by_id = {
            str(feature["feature_id"]): feature
            for feature in patent_technical_feature_ledger
        }
        claims_by_id = {
            str(claim["claim_id"]): claim
            for claim in technical_claim_skeleton_scaffold
        }
        rows: list[dict[str, object]] = []
        for blueprint in TECHNICAL_EMBODIMENT_BLUEPRINTS:
            linked_claim_ids = [str(claim_id) for claim_id in blueprint["linked_claim_ids"]]
            linked_feature_ids = [str(feature_id) for feature_id in blueprint["linked_feature_ids"]]
            missing_claim_ids = [
                claim_id
                for claim_id in linked_claim_ids
                if claim_id not in claims_by_id
            ]
            missing_feature_ids = [
                feature_id
                for feature_id in linked_feature_ids
                if feature_id not in features_by_id
            ]
            linked_claim_statuses = {
                claim_id: claims_by_id[claim_id]["claim_scaffold_status"]
                for claim_id in linked_claim_ids
                if claim_id in claims_by_id
            }
            linked_feature_statuses = {
                feature_id: features_by_id[feature_id]["feature_status"]
                for feature_id in linked_feature_ids
                if feature_id in features_by_id
            }
            row = {
                **blueprint,
                "linked_claim_statuses": linked_claim_statuses,
                "linked_feature_statuses": linked_feature_statuses,
                "missing_claim_ids": missing_claim_ids,
                "missing_feature_ids": missing_feature_ids,
                "can_generate_field_evidence": False,
                "can_write_to_actuator": False,
                "can_write_to_release_gate": False,
                "embodiment_status": "technical_embodiment_scaffold_not_field_evidence",
            }
            missing_fields = [
                field
                for field in REQUIRED_TECHNICAL_EMBODIMENT_FIELDS
                if row.get(field) in (None, "", [])
            ]
            row["missing_embodiment_fields"] = missing_fields
            row["validation_ready_status"] = (
                "embodiment_validation_scaffold_complete_waiting_for_field_evidence"
                if not missing_fields
                and not missing_claim_ids
                and not missing_feature_ids
                and row["field_claim_upgrade_allowed"] is False
                else "embodiment_validation_scaffold_needs_patch"
            )
            rows.append(row)
        return rows

    @staticmethod
    def _technical_embodiment_validation_coverage(
        technical_embodiment_validation_matrix: list[dict[str, object]],
    ) -> dict[str, object]:
        complete = [
            row
            for row in technical_embodiment_validation_matrix
            if row["validation_ready_status"] == "embodiment_validation_scaffold_complete_waiting_for_field_evidence"
        ]
        incomplete = [
            {
                "embodiment_id": row["embodiment_id"],
                "missing_embodiment_fields": row["missing_embodiment_fields"],
                "missing_claim_ids": row["missing_claim_ids"],
                "missing_feature_ids": row["missing_feature_ids"],
            }
            for row in technical_embodiment_validation_matrix
            if row["validation_ready_status"] != "embodiment_validation_scaffold_complete_waiting_for_field_evidence"
        ]
        covered_claim_ids = sorted(
            {
                str(claim_id)
                for row in technical_embodiment_validation_matrix
                for claim_id in row.get("linked_claim_ids", [])
            }
        )
        covered_feature_ids = sorted(
            {
                str(feature_id)
                for row in technical_embodiment_validation_matrix
                for feature_id in row.get("linked_feature_ids", [])
            }
        )
        all_claim_ids = [str(claim["claim_id"]) for claim in TECHNICAL_CLAIM_SCAFFOLD_BLUEPRINTS]
        all_feature_ids = [str(feature["feature_id"]) for feature in PATENT_TECHNICAL_FEATURE_BLUEPRINTS]
        missing_claim_coverage = [
            claim_id
            for claim_id in all_claim_ids
            if claim_id not in covered_claim_ids
        ]
        missing_feature_coverage = [
            feature_id
            for feature_id in all_feature_ids
            if feature_id not in covered_feature_ids
        ]
        coverage_rate = round(len(complete) / max(1, len(technical_embodiment_validation_matrix)), 3)
        return {
            "technical_embodiment_validation_status": (
                "technical_embodiment_matrix_ready_not_field_evidence"
                if coverage_rate == 1.0
                and not incomplete
                and not missing_claim_coverage
                and not missing_feature_coverage
                else "technical_embodiment_matrix_needs_patch"
            ),
            "embodiment_count": len(technical_embodiment_validation_matrix),
            "complete_embodiment_count": len(complete),
            "technical_embodiment_validation_coverage_rate": coverage_rate,
            "incomplete_embodiments": incomplete,
            "covered_claim_ids": covered_claim_ids,
            "missing_claim_coverage": missing_claim_coverage,
            "covered_feature_ids": covered_feature_ids,
            "missing_feature_coverage": missing_feature_coverage,
            "field_claim_upgrade_allowed": False,
            "can_generate_field_evidence": False,
            "can_write_to_actuator": False,
            "can_write_to_release_gate": False,
            "evidence_boundary": (
                "该矩阵只定义实施例与验证门；没有真实 field package、replay、holdout 和 operator review 时，"
                "不能生成 field evidence、不能写执行器、不能写 release gate。"
            ),
        }

    @staticmethod
    def _technical_effect_measurement_matrix(
        technical_embodiment_validation_matrix: list[dict[str, object]],
    ) -> list[dict[str, object]]:
        embodiments_by_id = {
            str(embodiment["embodiment_id"]): embodiment
            for embodiment in technical_embodiment_validation_matrix
        }
        claim_ids = {
            str(claim_id)
            for embodiment in technical_embodiment_validation_matrix
            for claim_id in embodiment.get("linked_claim_ids", [])
        }
        feature_ids = {
            str(feature_id)
            for embodiment in technical_embodiment_validation_matrix
            for feature_id in embodiment.get("linked_feature_ids", [])
        }
        rows: list[dict[str, object]] = []
        for blueprint in TECHNICAL_EFFECT_MEASUREMENT_BLUEPRINTS:
            linked_embodiment_ids = [
                str(embodiment_id)
                for embodiment_id in blueprint["linked_embodiment_ids"]
            ]
            linked_claim_ids = [str(claim_id) for claim_id in blueprint["linked_claim_ids"]]
            linked_feature_ids = [
                str(feature_id)
                for feature_id in blueprint["linked_feature_ids"]
            ]
            missing_embodiment_ids = [
                embodiment_id
                for embodiment_id in linked_embodiment_ids
                if embodiment_id not in embodiments_by_id
            ]
            missing_claim_ids = [
                claim_id
                for claim_id in linked_claim_ids
                if claim_id not in claim_ids
            ]
            missing_feature_ids = [
                feature_id
                for feature_id in linked_feature_ids
                if feature_id not in feature_ids
            ]
            linked_embodiment_statuses = {
                embodiment_id: embodiments_by_id[embodiment_id]["validation_ready_status"]
                for embodiment_id in linked_embodiment_ids
                if embodiment_id in embodiments_by_id
            }
            row = {
                **blueprint,
                "linked_embodiment_statuses": linked_embodiment_statuses,
                "missing_embodiment_ids": missing_embodiment_ids,
                "missing_claim_ids": missing_claim_ids,
                "missing_feature_ids": missing_feature_ids,
                "can_generate_field_evidence": False,
                "effect_status": "technical_effect_measurement_candidate_not_field_evidence",
            }
            missing_fields = [
                field
                for field in REQUIRED_TECHNICAL_EFFECT_MEASUREMENT_FIELDS
                if row.get(field) in (None, "", [])
            ]
            row["missing_effect_measurement_fields"] = missing_fields
            row["measurement_ready_status"] = (
                "technical_effect_measurement_complete_waiting_for_field_evidence"
                if not missing_fields
                and not missing_embodiment_ids
                and not missing_claim_ids
                and not missing_feature_ids
                and row["field_claim_upgrade_allowed"] is False
                and row["can_write_to_actuator"] is False
                and row["can_write_to_release_gate"] is False
                else "technical_effect_measurement_needs_patch"
            )
            rows.append(row)
        return rows

    @staticmethod
    def _technical_effect_measurement_coverage(
        *,
        technical_effect_measurement_matrix: list[dict[str, object]],
        technical_embodiment_validation_matrix: list[dict[str, object]],
    ) -> dict[str, object]:
        complete = [
            row
            for row in technical_effect_measurement_matrix
            if row["measurement_ready_status"] == "technical_effect_measurement_complete_waiting_for_field_evidence"
        ]
        incomplete = [
            {
                "effect_id": row["effect_id"],
                "missing_effect_measurement_fields": row["missing_effect_measurement_fields"],
                "missing_embodiment_ids": row["missing_embodiment_ids"],
                "missing_claim_ids": row["missing_claim_ids"],
                "missing_feature_ids": row["missing_feature_ids"],
            }
            for row in technical_effect_measurement_matrix
            if row["measurement_ready_status"] != "technical_effect_measurement_complete_waiting_for_field_evidence"
        ]
        covered_embodiment_ids = sorted(
            {
                str(embodiment_id)
                for row in technical_effect_measurement_matrix
                for embodiment_id in row.get("linked_embodiment_ids", [])
            }
        )
        all_embodiment_ids = [
            str(embodiment["embodiment_id"])
            for embodiment in technical_embodiment_validation_matrix
        ]
        missing_embodiment_coverage = [
            embodiment_id
            for embodiment_id in all_embodiment_ids
            if embodiment_id not in covered_embodiment_ids
        ]
        can_write_to_release_gate = any(
            bool(row.get("can_write_to_release_gate"))
            for row in technical_effect_measurement_matrix
        )
        can_write_to_actuator = any(
            bool(row.get("can_write_to_actuator"))
            for row in technical_effect_measurement_matrix
        )
        field_claim_upgrade_allowed = any(
            bool(row.get("field_claim_upgrade_allowed"))
            for row in technical_effect_measurement_matrix
        )
        coverage_rate = round(len(complete) / max(1, len(technical_effect_measurement_matrix)), 3)
        return {
            "technical_effect_measurement_status": (
                "technical_effect_measurement_matrix_ready_not_field_evidence"
                if coverage_rate == 1.0
                and not incomplete
                and not missing_embodiment_coverage
                and not field_claim_upgrade_allowed
                and not can_write_to_release_gate
                and not can_write_to_actuator
                else "technical_effect_measurement_matrix_needs_patch"
            ),
            "effect_count": len(technical_effect_measurement_matrix),
            "complete_effect_count": len(complete),
            "technical_effect_measurement_coverage_rate": coverage_rate,
            "incomplete_effect_measurements": incomplete,
            "covered_embodiment_ids": covered_embodiment_ids,
            "missing_embodiment_coverage": missing_embodiment_coverage,
            "field_claim_upgrade_allowed": field_claim_upgrade_allowed,
            "can_generate_field_evidence": False,
            "can_write_to_actuator": can_write_to_actuator,
            "can_write_to_release_gate": can_write_to_release_gate,
            "evidence_boundary": (
                "该矩阵只把技术效果转成基线、指标、阈值和验证门；没有真实 field package、replay、holdout、"
                "operator review 和 release gate 时，不能把任何效果写成现场成立结论。"
            ),
        }

    @staticmethod
    def _prior_art_distinction_matrix(
        *,
        technical_claim_skeleton_scaffold: list[dict[str, object]],
        patent_technical_feature_ledger: list[dict[str, object]],
        technical_effect_measurement_matrix: list[dict[str, object]],
    ) -> list[dict[str, object]]:
        claim_ids = {
            str(claim["claim_id"])
            for claim in technical_claim_skeleton_scaffold
        }
        feature_ids = {
            str(feature["feature_id"])
            for feature in patent_technical_feature_ledger
        }
        effect_ids = {
            str(effect["effect_id"])
            for effect in technical_effect_measurement_matrix
        }
        rows: list[dict[str, object]] = []
        for blueprint in PRIOR_ART_DISTINCTION_BLUEPRINTS:
            mapped_claim_ids = [
                str(claim_id)
                for claim_id in blueprint["mapped_claim_ids"]
            ]
            mapped_feature_ids = [
                str(feature_id)
                for feature_id in blueprint["mapped_feature_ids"]
            ]
            mapped_effect_ids = [
                str(effect_id)
                for effect_id in blueprint["mapped_effect_ids"]
            ]
            missing_claim_ids = [
                claim_id
                for claim_id in mapped_claim_ids
                if claim_id not in claim_ids
            ]
            missing_feature_ids = [
                feature_id
                for feature_id in mapped_feature_ids
                if feature_id not in feature_ids
            ]
            missing_effect_ids = [
                effect_id
                for effect_id in mapped_effect_ids
                if effect_id not in effect_ids
            ]
            row = {
                **blueprint,
                "missing_claim_ids": missing_claim_ids,
                "missing_feature_ids": missing_feature_ids,
                "missing_effect_ids": missing_effect_ids,
                "novelty_or_inventiveness_opinion_allowed": False,
                "can_generate_field_evidence": False,
                "can_write_to_actuator": False,
                "can_write_to_release_gate": False,
                "distinction_status": "prior_art_distinction_hypothesis_not_search_not_legal_opinion",
            }
            missing_fields = [
                field
                for field in REQUIRED_PRIOR_ART_DISTINCTION_FIELDS
                if row.get(field) in (None, "", [])
            ]
            row["missing_prior_art_distinction_fields"] = missing_fields
            row["distinction_ready_status"] = (
                "prior_art_distinction_complete_waiting_for_formal_search_and_field_evidence"
                if not missing_fields
                and not missing_claim_ids
                and not missing_feature_ids
                and not missing_effect_ids
                and row["formal_search_required"] is True
                and row["field_claim_upgrade_allowed"] is False
                else "prior_art_distinction_needs_patch"
            )
            rows.append(row)
        return rows

    @staticmethod
    def _prior_art_distinction_coverage(
        *,
        prior_art_distinction_matrix: list[dict[str, object]],
        technical_claim_skeleton_scaffold: list[dict[str, object]],
        patent_technical_feature_ledger: list[dict[str, object]],
        technical_effect_measurement_matrix: list[dict[str, object]],
    ) -> dict[str, object]:
        complete = [
            row
            for row in prior_art_distinction_matrix
            if row["distinction_ready_status"]
            == "prior_art_distinction_complete_waiting_for_formal_search_and_field_evidence"
        ]
        incomplete = [
            {
                "distinction_id": row["distinction_id"],
                "missing_prior_art_distinction_fields": row["missing_prior_art_distinction_fields"],
                "missing_claim_ids": row["missing_claim_ids"],
                "missing_feature_ids": row["missing_feature_ids"],
                "missing_effect_ids": row["missing_effect_ids"],
            }
            for row in prior_art_distinction_matrix
            if row["distinction_ready_status"]
            != "prior_art_distinction_complete_waiting_for_formal_search_and_field_evidence"
        ]
        covered_claim_ids = sorted(
            {
                str(claim_id)
                for row in prior_art_distinction_matrix
                for claim_id in row.get("mapped_claim_ids", [])
            }
        )
        covered_feature_ids = sorted(
            {
                str(feature_id)
                for row in prior_art_distinction_matrix
                for feature_id in row.get("mapped_feature_ids", [])
            }
        )
        covered_effect_ids = sorted(
            {
                str(effect_id)
                for row in prior_art_distinction_matrix
                for effect_id in row.get("mapped_effect_ids", [])
            }
        )
        all_claim_ids = [
            str(claim["claim_id"])
            for claim in technical_claim_skeleton_scaffold
        ]
        all_feature_ids = [
            str(feature["feature_id"])
            for feature in patent_technical_feature_ledger
        ]
        all_effect_ids = [
            str(effect["effect_id"])
            for effect in technical_effect_measurement_matrix
        ]
        missing_claim_coverage = [
            claim_id
            for claim_id in all_claim_ids
            if claim_id not in covered_claim_ids
        ]
        missing_feature_coverage = [
            feature_id
            for feature_id in all_feature_ids
            if feature_id not in covered_feature_ids
        ]
        missing_effect_coverage = [
            effect_id
            for effect_id in all_effect_ids
            if effect_id not in covered_effect_ids
        ]
        field_claim_upgrade_allowed = any(
            bool(row.get("field_claim_upgrade_allowed"))
            for row in prior_art_distinction_matrix
        )
        novelty_or_inventiveness_opinion_allowed = any(
            bool(row.get("novelty_or_inventiveness_opinion_allowed"))
            for row in prior_art_distinction_matrix
        )
        formal_search_required = any(
            bool(row.get("formal_search_required"))
            for row in prior_art_distinction_matrix
        )
        coverage_rate = round(len(complete) / max(1, len(prior_art_distinction_matrix)), 3)
        return {
            "prior_art_distinction_status": (
                "prior_art_distinction_matrix_ready_as_hypothesis_not_search_or_legal_opinion"
                if coverage_rate == 1.0
                and not incomplete
                and not missing_claim_coverage
                and not missing_feature_coverage
                and not missing_effect_coverage
                and formal_search_required
                and not field_claim_upgrade_allowed
                and not novelty_or_inventiveness_opinion_allowed
                else "prior_art_distinction_matrix_needs_patch"
            ),
            "distinction_count": len(prior_art_distinction_matrix),
            "complete_distinction_count": len(complete),
            "prior_art_distinction_coverage_rate": coverage_rate,
            "incomplete_distinctions": incomplete,
            "covered_claim_ids": covered_claim_ids,
            "missing_claim_coverage": missing_claim_coverage,
            "covered_feature_ids": covered_feature_ids,
            "missing_feature_coverage": missing_feature_coverage,
            "covered_effect_ids": covered_effect_ids,
            "missing_effect_coverage": missing_effect_coverage,
            "formal_search_required": formal_search_required,
            "field_claim_upgrade_allowed": field_claim_upgrade_allowed,
            "novelty_or_inventiveness_opinion_allowed": novelty_or_inventiveness_opinion_allowed,
            "legal_status": "prior_art_distinction_hypothesis_not_legal_opinion",
            "evidence_boundary": (
                "该矩阵只把已有技术家族与本项目候选区别点映射成检索/交底假设；"
                "没有正式 prior-art search、法律审查和 field validation 时，不能声称新颖性、创造性或授权可能性。"
            ),
        }

    @staticmethod
    def _formal_search_work_package_matrix(
        prior_art_distinction_matrix: list[dict[str, object]],
    ) -> list[dict[str, object]]:
        distinctions_by_id = {
            str(distinction["distinction_id"]): distinction
            for distinction in prior_art_distinction_matrix
        }
        rows: list[dict[str, object]] = []
        for blueprint in FORMAL_SEARCH_WORK_PACKAGE_BLUEPRINTS:
            linked_distinction_ids = [
                str(distinction_id)
                for distinction_id in blueprint["linked_distinction_ids"]
            ]
            missing_distinction_ids = [
                distinction_id
                for distinction_id in linked_distinction_ids
                if distinction_id not in distinctions_by_id
            ]
            mapped_claim_ids = sorted(
                {
                    str(claim_id)
                    for distinction_id in linked_distinction_ids
                    if distinction_id in distinctions_by_id
                    for claim_id in distinctions_by_id[distinction_id].get("mapped_claim_ids", [])
                }
            )
            mapped_feature_ids = sorted(
                {
                    str(feature_id)
                    for distinction_id in linked_distinction_ids
                    if distinction_id in distinctions_by_id
                    for feature_id in distinctions_by_id[distinction_id].get("mapped_feature_ids", [])
                }
            )
            mapped_effect_ids = sorted(
                {
                    str(effect_id)
                    for distinction_id in linked_distinction_ids
                    if distinction_id in distinctions_by_id
                    for effect_id in distinctions_by_id[distinction_id].get("mapped_effect_ids", [])
                }
            )
            row = {
                **blueprint,
                "mapped_claim_ids": mapped_claim_ids,
                "mapped_feature_ids": mapped_feature_ids,
                "mapped_effect_ids": mapped_effect_ids,
                "missing_distinction_ids": missing_distinction_ids,
                "can_generate_prior_art_result": False,
                "can_generate_legal_opinion": False,
                "can_generate_field_evidence": False,
                "work_package_status": "formal_search_work_package_ready_not_search_result",
            }
            missing_fields = [
                field
                for field in REQUIRED_FORMAL_SEARCH_WORK_PACKAGE_FIELDS
                if row.get(field) in (None, "", [])
            ]
            row["missing_formal_search_work_package_fields"] = missing_fields
            row["work_package_ready_status"] = (
                "formal_search_work_package_complete_waiting_for_human_or_external_search"
                if not missing_fields
                and not missing_distinction_ids
                and row["formal_search_required"] is True
                and row["formal_search_completed"] is False
                and row["legal_opinion_allowed"] is False
                and row["field_claim_upgrade_allowed"] is False
                else "formal_search_work_package_needs_patch"
            )
            rows.append(row)
        return rows

    @staticmethod
    def _formal_search_work_package_coverage(
        *,
        formal_search_work_package_matrix: list[dict[str, object]],
        prior_art_distinction_matrix: list[dict[str, object]],
    ) -> dict[str, object]:
        complete = [
            row
            for row in formal_search_work_package_matrix
            if row["work_package_ready_status"]
            == "formal_search_work_package_complete_waiting_for_human_or_external_search"
        ]
        incomplete = [
            {
                "work_package_id": row["work_package_id"],
                "missing_formal_search_work_package_fields": row[
                    "missing_formal_search_work_package_fields"
                ],
                "missing_distinction_ids": row["missing_distinction_ids"],
            }
            for row in formal_search_work_package_matrix
            if row["work_package_ready_status"]
            != "formal_search_work_package_complete_waiting_for_human_or_external_search"
        ]
        covered_distinction_ids = sorted(
            {
                str(distinction_id)
                for row in formal_search_work_package_matrix
                for distinction_id in row.get("linked_distinction_ids", [])
            }
        )
        all_distinction_ids = [
            str(distinction["distinction_id"])
            for distinction in prior_art_distinction_matrix
        ]
        missing_distinction_coverage = [
            distinction_id
            for distinction_id in all_distinction_ids
            if distinction_id not in covered_distinction_ids
        ]
        formal_search_completed = any(
            bool(row.get("formal_search_completed"))
            for row in formal_search_work_package_matrix
        )
        legal_opinion_allowed = any(
            bool(row.get("legal_opinion_allowed"))
            for row in formal_search_work_package_matrix
        )
        field_claim_upgrade_allowed = any(
            bool(row.get("field_claim_upgrade_allowed"))
            for row in formal_search_work_package_matrix
        )
        coverage_rate = round(len(complete) / max(1, len(formal_search_work_package_matrix)), 3)
        return {
            "formal_search_work_package_status": (
                "formal_search_work_packages_ready_not_search_results"
                if coverage_rate == 1.0
                and not incomplete
                and not missing_distinction_coverage
                and not formal_search_completed
                and not legal_opinion_allowed
                and not field_claim_upgrade_allowed
                else "formal_search_work_packages_need_patch"
            ),
            "work_package_count": len(formal_search_work_package_matrix),
            "complete_work_package_count": len(complete),
            "formal_search_work_package_coverage_rate": coverage_rate,
            "incomplete_work_packages": incomplete,
            "covered_distinction_ids": covered_distinction_ids,
            "missing_distinction_coverage": missing_distinction_coverage,
            "formal_search_required": True,
            "formal_search_completed": formal_search_completed,
            "legal_opinion_allowed": legal_opinion_allowed,
            "field_claim_upgrade_allowed": field_claim_upgrade_allowed,
            "can_generate_prior_art_result": False,
            "can_generate_field_evidence": False,
            "evidence_boundary": (
                "该矩阵只生成正式检索工作包和 claim fallback 路线；它不是检索结果、不是法律意见、"
                "不证明新颖性/创造性，也不产生 field-supported claim。"
            ),
        }

    @staticmethod
    def _formal_search_result_intake_schema(
        formal_search_work_package_matrix: list[dict[str, object]],
    ) -> list[dict[str, object]]:
        rows: list[dict[str, object]] = []
        for index, work_package in enumerate(formal_search_work_package_matrix, start=1):
            work_package_id = str(work_package["work_package_id"])
            row = {
                "intake_id": f"FSRI{index}_{work_package_id}",
                "linked_work_package_id": work_package_id,
                "linked_distinction_ids": [
                    str(distinction_id)
                    for distinction_id in work_package.get("linked_distinction_ids", [])
                ],
                "mapped_claim_ids": [
                    str(claim_id)
                    for claim_id in work_package.get("mapped_claim_ids", [])
                ],
                "mapped_feature_ids": [
                    str(feature_id)
                    for feature_id in work_package.get("mapped_feature_ids", [])
                ],
                "mapped_effect_ids": [
                    str(effect_id)
                    for effect_id in work_package.get("mapped_effect_ids", [])
                ],
                "required_hit_table_fields": list(PRIOR_ART_HIT_TABLE_FIELDS),
                "required_claim_element_comparison_fields": list(CLAIM_ELEMENT_COMPARISON_FIELDS),
                "required_reviewer_fields": [
                    "reviewer_id",
                    "review_time",
                    "review_status",
                    "review_note",
                    "legal_status",
                ],
                "input_artifacts": [
                    f"{work_package_id}_prior_art_hit_table.csv_or_json",
                    f"{work_package_id}_claim_element_comparison_chart.csv_or_json",
                    f"{work_package_id}_fallback_claim_scope_recommendation.md_or_json",
                ],
                "acceptance_checks": [
                    "linked_work_package_id must match a generated formal search work package",
                    "source_database must be one of search_databases from the linked work package",
                    "matched_query must be one of the english/chinese search queries or a reviewer-approved expansion",
                    "claim element comparison must cover mapped claim, feature or effect elements",
                    "each hit must state both disclosed capabilities and missing project elements",
                    "review_status must not contain legal conclusion or field-supported claim upgrade",
                ],
                "blocking_conditions": [
                    "missing publication_or_patent_id or url_or_reference",
                    "unknown source_database",
                    "empty matched_claim_elements",
                    "empty missing_project_elements when overlap_level is full_or_near_full",
                    "legal opinion text in reviewer fields",
                    "attempt to set field_claim_upgrade_allowed=true before field validation gates",
                ],
                "minimum_evidence_to_accept_hit": [
                    "publication_or_patent_id",
                    "title",
                    "source_database",
                    "url_or_reference",
                    "matched_query",
                    "matched_claim_elements",
                    "missing_project_elements",
                    "reviewer_id",
                    "review_status",
                ],
                "claim_scope_decision_options": [
                    "retain_candidate_scope_pending_formal_review",
                    "narrow_to_dependent_fallback",
                    "request_external_counsel_review",
                    "discard_claim_route",
                    "keep_as_research_only_not_claim_candidate",
                ],
                "field_validation_gate_to_preserve": work_package["field_validation_gate_to_preserve"],
                "formal_search_result_supplied": False,
                "accepted_hit_count": 0,
                "can_generate_prior_art_result": False,
                "legal_opinion_allowed": False,
                "field_claim_upgrade_allowed": False,
                "failure_boundary": (
                    "该 intake 只定义检索结果如何提交和审查；没有人工/外部正式检索结果、claim element comparison "
                    "和 field validation gate 时，不能生成 prior-art 结论、法律意见或现场 claim。"
                ),
                "intake_status": "formal_search_result_intake_schema_ready_waiting_for_search_results",
            }
            missing_fields = [
                field
                for field in REQUIRED_FORMAL_SEARCH_RESULT_INTAKE_FIELDS
                if row.get(field) in (None, "", [])
            ]
            row["missing_formal_search_result_intake_fields"] = missing_fields
            row["intake_ready_status"] = (
                "formal_search_result_intake_complete_waiting_for_external_search_results"
                if not missing_fields
                and row["formal_search_result_supplied"] is False
                and row["accepted_hit_count"] == 0
                and row["can_generate_prior_art_result"] is False
                and row["legal_opinion_allowed"] is False
                and row["field_claim_upgrade_allowed"] is False
                else "formal_search_result_intake_needs_patch"
            )
            rows.append(row)
        return rows

    @staticmethod
    def _formal_search_result_intake_coverage(
        *,
        formal_search_result_intake_schema: list[dict[str, object]],
        formal_search_work_package_matrix: list[dict[str, object]],
    ) -> dict[str, object]:
        complete = [
            row
            for row in formal_search_result_intake_schema
            if row["intake_ready_status"]
            == "formal_search_result_intake_complete_waiting_for_external_search_results"
        ]
        incomplete = [
            {
                "intake_id": row["intake_id"],
                "missing_formal_search_result_intake_fields": row[
                    "missing_formal_search_result_intake_fields"
                ],
            }
            for row in formal_search_result_intake_schema
            if row["intake_ready_status"]
            != "formal_search_result_intake_complete_waiting_for_external_search_results"
        ]
        covered_work_package_ids = sorted(
            {
                str(row["linked_work_package_id"])
                for row in formal_search_result_intake_schema
            }
        )
        all_work_package_ids = [
            str(work_package["work_package_id"])
            for work_package in formal_search_work_package_matrix
        ]
        missing_work_package_coverage = [
            work_package_id
            for work_package_id in all_work_package_ids
            if work_package_id not in covered_work_package_ids
        ]
        result_supplied = any(
            bool(row.get("formal_search_result_supplied"))
            for row in formal_search_result_intake_schema
        )
        accepted_hit_count = sum(
            int(row.get("accepted_hit_count", 0))
            for row in formal_search_result_intake_schema
        )
        legal_opinion_allowed = any(
            bool(row.get("legal_opinion_allowed"))
            for row in formal_search_result_intake_schema
        )
        field_claim_upgrade_allowed = any(
            bool(row.get("field_claim_upgrade_allowed"))
            for row in formal_search_result_intake_schema
        )
        can_generate_prior_art_result = any(
            bool(row.get("can_generate_prior_art_result"))
            for row in formal_search_result_intake_schema
        )
        coverage_rate = round(len(complete) / max(1, len(formal_search_result_intake_schema)), 3)
        return {
            "formal_search_result_intake_status": (
                "formal_search_result_intake_schema_ready_waiting_for_external_results"
                if coverage_rate == 1.0
                and not incomplete
                and not missing_work_package_coverage
                and not result_supplied
                and accepted_hit_count == 0
                and not legal_opinion_allowed
                and not field_claim_upgrade_allowed
                and not can_generate_prior_art_result
                else "formal_search_result_intake_schema_needs_patch"
            ),
            "intake_count": len(formal_search_result_intake_schema),
            "complete_intake_count": len(complete),
            "formal_search_result_intake_coverage_rate": coverage_rate,
            "incomplete_intakes": incomplete,
            "covered_work_package_ids": covered_work_package_ids,
            "missing_work_package_coverage": missing_work_package_coverage,
            "formal_search_result_supplied": result_supplied,
            "accepted_hit_count": accepted_hit_count,
            "can_generate_prior_art_result": can_generate_prior_art_result,
            "legal_opinion_allowed": legal_opinion_allowed,
            "field_claim_upgrade_allowed": field_claim_upgrade_allowed,
            "required_hit_table_fields": list(PRIOR_ART_HIT_TABLE_FIELDS),
            "required_claim_element_comparison_fields": list(CLAIM_ELEMENT_COMPARISON_FIELDS),
            "evidence_boundary": (
                "该 schema 只定义正式检索结果的接收、字段和阻断规则；没有外部检索结果与人工复核时，"
                "不能生成 prior-art hit 结论、法律意见或 field-supported claim。"
            ),
        }

    @staticmethod
    def _formal_search_result_validation_gate(
        *,
        formal_search_result_intake_schema: list[dict[str, object]],
        formal_search_work_package_matrix: list[dict[str, object]],
    ) -> list[dict[str, object]]:
        work_packages = {
            str(work_package["work_package_id"]): work_package
            for work_package in formal_search_work_package_matrix
        }
        rows: list[dict[str, object]] = []
        for index, intake in enumerate(formal_search_result_intake_schema, start=1):
            work_package_id = str(intake["linked_work_package_id"])
            work_package = work_packages.get(work_package_id, {})
            allowed_queries = (
                list(work_package.get("english_search_queries", []))
                + list(work_package.get("chinese_search_queries", []))
                + ["reviewer_approved_query_expansion_with_rationale"]
            )
            row = {
                "validation_gate_id": f"FSRG{index}_{work_package_id}",
                "linked_intake_id": intake["intake_id"],
                "linked_work_package_id": work_package_id,
                "linked_distinction_ids": list(intake["linked_distinction_ids"]),
                "mapped_claim_ids": list(intake["mapped_claim_ids"]),
                "mapped_feature_ids": list(intake["mapped_feature_ids"]),
                "mapped_effect_ids": list(intake["mapped_effect_ids"]),
                "accepted_input_artifacts": list(intake["input_artifacts"]),
                "allowed_source_databases": list(work_package.get("search_databases", [])),
                "allowed_query_sources": allowed_queries,
                "hit_table_required_fields": list(PRIOR_ART_HIT_TABLE_FIELDS),
                "comparison_chart_required_fields": list(CLAIM_ELEMENT_COMPARISON_FIELDS),
                "runtime_validation_steps": [
                    "load prior_art_hit_table and claim_element_comparison_chart from the linked intake artifacts",
                    "reject package if required table fields or comparison fields are missing",
                    "reject hit rows whose linked_work_package_id is not the current work package",
                    "reject source_database values outside the linked formal search work package search_databases",
                    "reject matched_query values that are neither generated queries nor reviewer-approved expansions",
                    "require every accepted hit to state disclosed capabilities and missing project elements",
                    "require claim element comparisons to cover at least one mapped claim, feature or effect element",
                    "reject reviewer text that asserts legal conclusion, authorization likelihood or field-supported claim",
                    "route accepted overlap to claim_scope_decision_options without producing legal opinion",
                ],
                "blocking_conditions": [
                    "result package missing or unreadable",
                    "hit table or comparison chart missing required fields",
                    "unknown linked_work_package_id",
                    "source_database not in allowed_source_databases",
                    "matched_query lacks generated-query or reviewer-approved-expansion provenance",
                    "matched_claim_elements or prior_art_disclosure_text empty",
                    "missing_project_elements empty for full_or_near_full overlap",
                    "review_status or review_note contains novelty/inventiveness/legal conclusion",
                    "field_claim_upgrade_allowed set before field validation gate",
                    "can_generate_prior_art_result set without accepted hits and human/external review",
                ],
                "patch_plan_outputs": [
                    f"{work_package_id}_missing_required_fields_patch",
                    f"{work_package_id}_source_database_or_query_provenance_patch",
                    f"{work_package_id}_claim_element_comparison_gap_patch",
                    f"{work_package_id}_reviewer_boundary_patch",
                    f"{work_package_id}_claim_scope_fallback_patch",
                ],
                "prior_art_result_generation_rule": (
                    "Only after a non-empty external/human-reviewed result package passes hit-table, "
                    "comparison-chart, query-provenance and reviewer-boundary checks may Agent60 generate "
                    "a non-legal prior-art comparison summary. It must still preserve formal counsel and "
                    "field validation gates."
                ),
                "formal_search_result_package_supplied": False,
                "validated_hit_count": 0,
                "rejected_hit_count": 0,
                "can_generate_prior_art_result": False,
                "legal_opinion_allowed": False,
                "field_claim_upgrade_allowed": False,
                "failure_boundary": (
                    "该 gate 只验证正式检索结果包的结构、来源、比对覆盖和 reviewer 边界；"
                    "没有真实外部/人工检索结果时不能生成 prior-art comparison，任何情况下都不是法律意见，"
                    "也不能把检索结果升级为 field-supported claim。"
                ),
                "validation_gate_status": "formal_search_result_validation_gate_ready_waiting_for_result_package",
            }
            missing_fields = [
                field
                for field in REQUIRED_FORMAL_SEARCH_RESULT_VALIDATION_GATE_FIELDS
                if row.get(field) in (None, "", [])
            ]
            row["missing_formal_search_result_validation_gate_fields"] = missing_fields
            row["validation_ready_status"] = (
                "formal_search_result_validation_gate_complete_waiting_for_external_result_package"
                if not missing_fields
                and row["formal_search_result_package_supplied"] is False
                and row["validated_hit_count"] == 0
                and row["rejected_hit_count"] == 0
                and row["can_generate_prior_art_result"] is False
                and row["legal_opinion_allowed"] is False
                and row["field_claim_upgrade_allowed"] is False
                else "formal_search_result_validation_gate_needs_patch"
            )
            rows.append(row)
        return rows

    @staticmethod
    def _formal_search_result_validation_gate_coverage(
        *,
        formal_search_result_validation_gate: list[dict[str, object]],
        formal_search_result_intake_schema: list[dict[str, object]],
    ) -> dict[str, object]:
        complete = [
            row
            for row in formal_search_result_validation_gate
            if row["validation_ready_status"]
            == "formal_search_result_validation_gate_complete_waiting_for_external_result_package"
        ]
        incomplete = [
            {
                "validation_gate_id": row["validation_gate_id"],
                "missing_formal_search_result_validation_gate_fields": row[
                    "missing_formal_search_result_validation_gate_fields"
                ],
            }
            for row in formal_search_result_validation_gate
            if row["validation_ready_status"]
            != "formal_search_result_validation_gate_complete_waiting_for_external_result_package"
        ]
        covered_intake_ids = sorted(
            {str(row["linked_intake_id"]) for row in formal_search_result_validation_gate}
        )
        all_intake_ids = [
            str(intake["intake_id"])
            for intake in formal_search_result_intake_schema
        ]
        missing_intake_coverage = [
            intake_id
            for intake_id in all_intake_ids
            if intake_id not in covered_intake_ids
        ]
        result_package_supplied = any(
            bool(row.get("formal_search_result_package_supplied"))
            for row in formal_search_result_validation_gate
        )
        validated_hit_count = sum(
            int(row.get("validated_hit_count", 0))
            for row in formal_search_result_validation_gate
        )
        rejected_hit_count = sum(
            int(row.get("rejected_hit_count", 0))
            for row in formal_search_result_validation_gate
        )
        can_generate_prior_art_result = any(
            bool(row.get("can_generate_prior_art_result"))
            for row in formal_search_result_validation_gate
        )
        legal_opinion_allowed = any(
            bool(row.get("legal_opinion_allowed"))
            for row in formal_search_result_validation_gate
        )
        field_claim_upgrade_allowed = any(
            bool(row.get("field_claim_upgrade_allowed"))
            for row in formal_search_result_validation_gate
        )
        coverage_rate = round(
            len(complete) / max(1, len(formal_search_result_validation_gate)), 3
        )
        return {
            "formal_search_result_validation_gate_status": (
                "formal_search_result_validation_gate_ready_waiting_for_external_result_package"
                if coverage_rate == 1.0
                and not incomplete
                and not missing_intake_coverage
                and not result_package_supplied
                and validated_hit_count == 0
                and rejected_hit_count == 0
                and not can_generate_prior_art_result
                and not legal_opinion_allowed
                and not field_claim_upgrade_allowed
                else "formal_search_result_validation_gate_needs_patch"
            ),
            "validation_gate_count": len(formal_search_result_validation_gate),
            "complete_validation_gate_count": len(complete),
            "formal_search_result_validation_gate_coverage_rate": coverage_rate,
            "incomplete_validation_gates": incomplete,
            "covered_intake_ids": covered_intake_ids,
            "missing_intake_coverage": missing_intake_coverage,
            "formal_search_result_package_supplied": result_package_supplied,
            "validated_hit_count": validated_hit_count,
            "rejected_hit_count": rejected_hit_count,
            "can_generate_prior_art_result": can_generate_prior_art_result,
            "legal_opinion_allowed": legal_opinion_allowed,
            "field_claim_upgrade_allowed": field_claim_upgrade_allowed,
            "required_validation_gate_fields": list(
                REQUIRED_FORMAL_SEARCH_RESULT_VALIDATION_GATE_FIELDS
            ),
            "evidence_boundary": (
                "该 validation gate 只是正式检索结果包进入模型前的结构、来源、比对和 reviewer 边界门；"
                "当前没有外部结果包，因此不能生成 prior-art comparison、法律意见或 field-supported claim。"
            ),
        }

    @staticmethod
    def _formal_search_result_package_template(
        formal_search_result_validation_gate: list[dict[str, object]],
    ) -> list[dict[str, object]]:
        rows: list[dict[str, object]] = []
        for index, gate in enumerate(formal_search_result_validation_gate, start=1):
            work_package_id = str(gate["linked_work_package_id"])
            row = {
                "package_template_id": f"FSRPT{index}_{work_package_id}",
                "linked_validation_gate_id": gate["validation_gate_id"],
                "linked_intake_id": gate["linked_intake_id"],
                "linked_work_package_id": work_package_id,
                "mapped_claim_ids": list(gate["mapped_claim_ids"]),
                "mapped_feature_ids": list(gate["mapped_feature_ids"]),
                "mapped_effect_ids": list(gate["mapped_effect_ids"]),
                "package_root_key": work_package_id,
                "package_manifest_required_fields": [
                    "package_id",
                    "linked_work_package_id",
                    "search_executor",
                    "search_date",
                    "databases_searched",
                    "query_log",
                    "reviewer_id",
                    "review_time",
                    "review_boundary_statement",
                    "legal_status",
                ],
                "required_result_tables": [
                    "prior_art_hit_table",
                    "claim_element_comparison_chart",
                    "fallback_claim_scope_recommendation",
                ],
                "prior_art_hit_table_template_fields": list(PRIOR_ART_HIT_TABLE_FIELDS),
                "claim_element_comparison_template_fields": list(CLAIM_ELEMENT_COMPARISON_FIELDS),
                "fallback_recommendation_fields": [
                    "linked_work_package_id",
                    "claim_scope_decision_option",
                    "decision_rationale",
                    "triggering_hit_ids",
                    "preserved_field_validation_gate",
                    "reviewer_id",
                    "legal_status",
                ],
                "allowed_source_databases": list(gate["allowed_source_databases"]),
                "allowed_query_sources": list(gate["allowed_query_sources"]),
                "row_level_rejection_rules": [
                    "reject TODO/template/sample rows",
                    "reject rows without publication_or_patent_id and url_or_reference",
                    "reject rows without matched_claim_elements",
                    "reject rows whose source_database is outside allowed_source_databases",
                    "reject rows whose matched_query lacks generated-query or reviewer expansion provenance",
                    "reject comparison rows without prior_art_disclosure_text",
                    "reject reviewer fields that assert legal conclusion or field-supported claim",
                ],
                "validation_command": ".venv/bin/python experiments/run_agent60_agent_architecture_consolidation.py",
                "package_template_status": "formal_search_result_package_template_ready_waiting_for_submission",
                "formal_search_result_package_supplied": False,
                "can_route_to_validation_gate": False,
                "can_generate_prior_art_result": False,
                "legal_opinion_allowed": False,
                "field_claim_upgrade_allowed": False,
                "failure_boundary": (
                    "该 template 只规定正式检索结果包的提交结构；模板行、TODO 行或 sample 行不能作为 "
                    "prior-art hit，也不能生成法律意见或 field-supported claim。"
                ),
            }
            missing_fields = [
                field
                for field in REQUIRED_FORMAL_SEARCH_RESULT_PACKAGE_TEMPLATE_FIELDS
                if row.get(field) in (None, "", [])
            ]
            row["missing_formal_search_result_package_template_fields"] = missing_fields
            row["package_template_ready_status"] = (
                "formal_search_result_package_template_complete_waiting_for_submission"
                if not missing_fields
                and row["formal_search_result_package_supplied"] is False
                and row["can_route_to_validation_gate"] is False
                and row["can_generate_prior_art_result"] is False
                and row["legal_opinion_allowed"] is False
                and row["field_claim_upgrade_allowed"] is False
                else "formal_search_result_package_template_needs_patch"
            )
            rows.append(row)
        return rows

    @staticmethod
    def _formal_search_result_package_template_coverage(
        *,
        formal_search_result_package_template: list[dict[str, object]],
        formal_search_result_validation_gate: list[dict[str, object]],
    ) -> dict[str, object]:
        complete = [
            row
            for row in formal_search_result_package_template
            if row["package_template_ready_status"]
            == "formal_search_result_package_template_complete_waiting_for_submission"
        ]
        incomplete = [
            {
                "package_template_id": row["package_template_id"],
                "missing_formal_search_result_package_template_fields": row[
                    "missing_formal_search_result_package_template_fields"
                ],
            }
            for row in formal_search_result_package_template
            if row["package_template_ready_status"]
            != "formal_search_result_package_template_complete_waiting_for_submission"
        ]
        covered_validation_gate_ids = sorted(
            {str(row["linked_validation_gate_id"]) for row in formal_search_result_package_template}
        )
        all_validation_gate_ids = [
            str(gate["validation_gate_id"])
            for gate in formal_search_result_validation_gate
        ]
        missing_validation_gate_coverage = [
            gate_id
            for gate_id in all_validation_gate_ids
            if gate_id not in covered_validation_gate_ids
        ]
        coverage_rate = round(
            len(complete) / max(1, len(formal_search_result_package_template)), 3
        )
        return {
            "formal_search_result_package_template_status": (
                "formal_search_result_package_templates_ready_waiting_for_submission"
                if coverage_rate == 1.0
                and not incomplete
                and not missing_validation_gate_coverage
                else "formal_search_result_package_templates_need_patch"
            ),
            "package_template_count": len(formal_search_result_package_template),
            "complete_package_template_count": len(complete),
            "formal_search_result_package_template_coverage_rate": coverage_rate,
            "incomplete_package_templates": incomplete,
            "covered_validation_gate_ids": covered_validation_gate_ids,
            "missing_validation_gate_coverage": missing_validation_gate_coverage,
            "formal_search_result_package_supplied": False,
            "can_route_to_validation_gate": False,
            "can_generate_prior_art_result": False,
            "legal_opinion_allowed": False,
            "field_claim_upgrade_allowed": False,
            "required_package_template_fields": list(
                REQUIRED_FORMAL_SEARCH_RESULT_PACKAGE_TEMPLATE_FIELDS
            ),
            "evidence_boundary": (
                "该 package template 只提供外部/人工检索结果包的提交合同；没有提交真实结果包时，"
                "不能进入 validation gate，也不能生成 prior-art comparison、法律意见或 field-supported claim。"
            ),
        }

    @staticmethod
    def _formal_search_result_package_submission_template(
        formal_search_result_package_template: list[dict[str, object]],
    ) -> dict[str, object]:
        required_result_tables = [
            "prior_art_hit_table",
            "claim_element_comparison_chart",
            "fallback_claim_scope_recommendation",
        ]
        work_package_results: dict[str, object] = {}
        for template in formal_search_result_package_template:
            work_package_id = str(template["linked_work_package_id"])
            hit_row = {
                field: f"TODO_{work_package_id}_{field}"
                for field in template["prior_art_hit_table_template_fields"]
            }
            hit_row.update(
                {
                    "linked_work_package_id": work_package_id,
                    "template_only": True,
                    "evidence_status": "template_not_prior_art_evidence",
                    "legal_status": "template_not_legal_opinion",
                }
            )
            comparison_row = {
                field: f"TODO_{work_package_id}_{field}"
                for field in template["claim_element_comparison_template_fields"]
            }
            comparison_row.update(
                {
                    "linked_work_package_id": work_package_id,
                    "template_only": True,
                    "evidence_status": "template_not_prior_art_evidence",
                    "legal_status": "template_not_legal_opinion",
                }
            )
            fallback_row = {
                field: f"TODO_{work_package_id}_{field}"
                for field in template["fallback_recommendation_fields"]
            }
            fallback_row.update(
                {
                    "linked_work_package_id": work_package_id,
                    "template_only": True,
                    "evidence_status": "template_not_prior_art_evidence",
                    "legal_status": "template_not_legal_opinion",
                }
            )
            package_manifest = {
                field: f"TODO_{work_package_id}_{field}"
                for field in template["package_manifest_required_fields"]
            }
            package_manifest.update(
                {
                    "linked_work_package_id": work_package_id,
                    "allowed_source_databases": list(template["allowed_source_databases"]),
                    "allowed_query_sources": list(template["allowed_query_sources"]),
                    "template_only": True,
                    "evidence_status": "template_not_prior_art_evidence",
                    "legal_status": "template_not_legal_opinion",
                }
            )
            work_package_results[work_package_id] = {
                "package_manifest": package_manifest,
                "prior_art_hit_table": [hit_row],
                "claim_element_comparison_chart": [comparison_row],
                "fallback_claim_scope_recommendation": [fallback_row],
            }

        template_payload = {
            "submission_template_status": "formal_search_result_package_submission_template_ready",
            "expected_env_var": "FORMAL_SEARCH_RESULT_PACKAGE_PATH",
            "recommended_output_path": "outputs/agent_architecture_consolidation/formal_search_result_package_submission.json",
            "package_metadata": {
                "package_id": "TODO_FORMAL_SEARCH_RESULT_PACKAGE_ID",
                "package_type": "formal_search_result_package_submission_template",
                "search_executor": "TODO_SEARCH_EXECUTOR",
                "search_date": "TODO_SEARCH_DATE",
                "reviewer_id": "TODO_REVIEWER_ID",
                "review_time": "TODO_REVIEW_TIME",
                "review_boundary_statement": (
                    "No legal opinion, no novelty/inventiveness conclusion, no field-supported claim."
                ),
                "template_only": True,
                "evidence_status": "template_not_prior_art_evidence",
                "legal_status": "template_not_legal_opinion",
            },
            "work_package_results": work_package_results,
            "expected_work_package_ids": sorted(work_package_results),
            "required_result_tables": required_result_tables,
            "template_marker_policy": (
                "Replace every TODO_ value, template_only=true flag and template_not_prior_art_evidence marker "
                "before setting FORMAL_SEARCH_RESULT_PACKAGE_PATH. The preflight rejects this skeleton as evidence."
            ),
            "can_route_to_validation_gate": False,
            "can_generate_prior_art_result": False,
            "legal_opinion_allowed": False,
            "field_claim_upgrade_allowed": False,
            "failure_boundary": (
                "该 skeleton 是可填报提交骨架，不是 prior-art hit，不是正式检索结果，不是法律意见；"
                "原样提交会被 template-marker preflight 阻断。"
            ),
        }
        missing_fields = [
            field
            for field in REQUIRED_FORMAL_SEARCH_RESULT_SUBMISSION_TEMPLATE_FIELDS
            if template_payload.get(field) in (None, "", [])
        ]
        template_payload["missing_submission_template_fields"] = missing_fields
        template_payload["submission_template_ready_status"] = (
            "formal_search_result_package_submission_template_complete"
            if not missing_fields
            and template_payload["can_route_to_validation_gate"] is False
            and template_payload["can_generate_prior_art_result"] is False
            and template_payload["legal_opinion_allowed"] is False
            and template_payload["field_claim_upgrade_allowed"] is False
            else "formal_search_result_package_submission_template_needs_patch"
        )
        return template_payload

    @staticmethod
    def _template_marker_gaps(value: object, path: str) -> list[str]:
        markers: list[str] = []
        if isinstance(value, dict):
            if value.get("template_only") is True:
                markers.append(f"{path}.template_only:true")
            for key, child in value.items():
                markers.extend(
                    AgentArchitectureConsolidationAgent._template_marker_gaps(
                        child, f"{path}.{key}"
                    )
                )
            return markers
        if isinstance(value, list):
            for index, child in enumerate(value):
                markers.extend(
                    AgentArchitectureConsolidationAgent._template_marker_gaps(
                        child, f"{path}[{index}]"
                    )
                )
            return markers
        if isinstance(value, str):
            normalized = value.strip()
            if (
                normalized.startswith("TODO")
                or "template_not_prior_art_evidence" in normalized
                or "sample_not_prior_art_evidence" in normalized
                or "template_not_legal_opinion" in normalized
            ):
                markers.append(f"{path}:{normalized[:80]}")
        return markers

    def _formal_search_result_package_source_preflight(
        self,
        formal_search_result_package_template: list[dict[str, object]],
    ) -> dict[str, object]:
        expected_work_package_ids = [
            str(template["linked_work_package_id"])
            for template in formal_search_result_package_template
        ]
        required_root_keys = ["package_metadata", "work_package_results"]
        required_result_tables = [
            "prior_art_hit_table",
            "claim_element_comparison_chart",
            "fallback_claim_scope_recommendation",
        ]
        path_value = self.formal_search_result_package_path
        base = {
            "formal_search_result_package_path": path_value or "",
            "expected_env_var": "FORMAL_SEARCH_RESULT_PACKAGE_PATH",
            "required_root_keys": required_root_keys,
            "expected_work_package_ids": expected_work_package_ids,
            "required_result_tables": required_result_tables,
            "missing_root_keys": [],
            "unknown_work_package_ids": [],
            "missing_work_package_results": [],
            "invalid_table_shapes": [],
            "empty_required_tables": [],
            "template_marker_gaps": [],
            "template_marker_gap_count": 0,
            "preflight_blockers": [],
            "formal_search_result_package_supplied": False,
            "can_route_to_validation_gate": False,
            "can_generate_prior_art_result": False,
            "legal_opinion_allowed": False,
            "field_claim_upgrade_allowed": False,
            "failure_boundary": (
                "该 preflight 只检查正式检索结果包的 source/path/root shape；即使通过，也只允许进入 "
                "formal_search_result_validation_gate，不能直接生成法律意见、prior-art 结论或 field-supported claim。"
            ),
        }
        if not path_value:
            return {
                **base,
                "formal_search_result_package_source_status": (
                    "formal_search_result_package_preflight_waiting_for_submission_path"
                ),
                "preflight_blockers": ["FORMAL_SEARCH_RESULT_PACKAGE_PATH:not_set"],
            }
        package_path = Path(path_value).expanduser()
        if not package_path.exists():
            return {
                **base,
                "formal_search_result_package_source_status": (
                    "formal_search_result_package_file_missing"
                ),
                "preflight_blockers": [f"{package_path}:missing_file"],
            }
        try:
            payload = json.loads(package_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            return {
                **base,
                "formal_search_result_package_source_status": (
                    "formal_search_result_package_json_invalid"
                ),
                "preflight_blockers": [f"{package_path}:invalid_json:{exc.msg}"],
                "formal_search_result_package_supplied": True,
            }
        if not isinstance(payload, dict):
            return {
                **base,
                "formal_search_result_package_source_status": (
                    "formal_search_result_package_root_not_object"
                ),
                "preflight_blockers": [f"{package_path}:root_not_object"],
                "formal_search_result_package_supplied": True,
            }

        missing_root_keys = [
            root_key
            for root_key in required_root_keys
            if root_key not in payload
        ]
        metadata = payload.get("package_metadata")
        work_package_results = payload.get("work_package_results")
        blockers: list[str] = []
        invalid_table_shapes: list[dict[str, str]] = []
        empty_required_tables: list[dict[str, str]] = []
        template_marker_gaps: list[str] = []
        unknown_work_package_ids: list[str] = []
        missing_work_package_results: list[str] = []
        if missing_root_keys:
            blockers.extend(f"{root_key}:missing_root_key" for root_key in missing_root_keys)
        if "package_metadata" in payload and not isinstance(metadata, dict):
            blockers.append("package_metadata:not_object")
        elif isinstance(metadata, dict):
            template_marker_gaps.extend(
                self._template_marker_gaps(metadata, "package_metadata")
            )
        if "work_package_results" in payload and not isinstance(work_package_results, dict):
            blockers.append("work_package_results:not_object")
        if isinstance(work_package_results, dict):
            submitted_ids = {str(work_package_id) for work_package_id in work_package_results}
            unknown_work_package_ids = sorted(
                work_package_id
                for work_package_id in submitted_ids
                if work_package_id not in expected_work_package_ids
            )
            missing_work_package_results = [
                work_package_id
                for work_package_id in expected_work_package_ids
                if work_package_id not in submitted_ids
            ]
            blockers.extend(
                f"{work_package_id}:unknown_work_package_id"
                for work_package_id in unknown_work_package_ids
            )
            blockers.extend(
                f"{work_package_id}:missing_work_package_result"
                for work_package_id in missing_work_package_results
            )
            for work_package_id in sorted(submitted_ids & set(expected_work_package_ids)):
                result = work_package_results.get(work_package_id)
                if not isinstance(result, dict):
                    blockers.append(f"{work_package_id}:result_not_object")
                    continue
                template_marker_gaps.extend(
                    self._template_marker_gaps(
                        result.get("package_manifest", {}),
                        f"work_package_results.{work_package_id}.package_manifest",
                    )
                )
                for table_name in required_result_tables:
                    table = result.get(table_name)
                    if not isinstance(table, list):
                        invalid_table_shapes.append(
                            {
                                "work_package_id": work_package_id,
                                "table": table_name,
                                "issue": "missing_or_not_list",
                            }
                        )
                        blockers.append(f"{work_package_id}:{table_name}:missing_or_not_list")
                    elif not table:
                        empty_required_tables.append(
                            {
                                "work_package_id": work_package_id,
                                "table": table_name,
                                "issue": "empty_table",
                            }
                        )
                        blockers.append(f"{work_package_id}:{table_name}:empty_table")
                    else:
                        for row_index, row in enumerate(table):
                            if not isinstance(row, dict):
                                invalid_table_shapes.append(
                                    {
                                        "work_package_id": work_package_id,
                                        "table": table_name,
                                        "issue": f"row_{row_index}_not_object",
                                    }
                                )
                                blockers.append(
                                    f"{work_package_id}:{table_name}:row_{row_index}_not_object"
                                )
                                continue
                            template_marker_gaps.extend(
                                self._template_marker_gaps(
                                    row,
                                    (
                                        f"work_package_results.{work_package_id}."
                                        f"{table_name}[{row_index}]"
                                    ),
                                )
                            )
        if template_marker_gaps:
            blockers.append("template_marker_preflight:template_or_todo_values_present")
        can_route = not blockers
        return {
            **base,
            "formal_search_result_package_source_status": (
                "formal_search_result_package_source_ready_for_validation_gate"
                if can_route
                else (
                    "formal_search_result_package_failed_template_marker_preflight"
                    if template_marker_gaps
                    else "formal_search_result_package_loaded_with_preflight_gaps"
                )
            ),
            "missing_root_keys": missing_root_keys,
            "unknown_work_package_ids": unknown_work_package_ids,
            "missing_work_package_results": missing_work_package_results,
            "invalid_table_shapes": invalid_table_shapes,
            "empty_required_tables": empty_required_tables,
            "template_marker_gaps": template_marker_gaps,
            "template_marker_gap_count": len(template_marker_gaps),
            "preflight_blockers": blockers,
            "formal_search_result_package_supplied": True,
            "can_route_to_validation_gate": can_route,
            "can_generate_prior_art_result": False,
            "legal_opinion_allowed": False,
            "field_claim_upgrade_allowed": False,
        }

    @staticmethod
    def _empty_required_fields(row: dict[str, object], fields: Sequence[str]) -> list[str]:
        return [
            field
            for field in fields
            if row.get(field) in (None, "", [])
        ]

    @staticmethod
    def _contains_forbidden_review_text(value: object) -> bool:
        if isinstance(value, dict):
            return any(
                AgentArchitectureConsolidationAgent._contains_forbidden_review_text(child)
                for child in value.values()
            )
        if isinstance(value, list):
            return any(
                AgentArchitectureConsolidationAgent._contains_forbidden_review_text(child)
                for child in value
            )
        if isinstance(value, str):
            normalized = value.lower()
            return any(term.lower() in normalized for term in FORBIDDEN_PRIOR_ART_REVIEW_TERMS)
        return False

    def _formal_search_result_package_row_preflight(
        self,
        *,
        formal_search_result_package_template: list[dict[str, object]],
        source_preflight: dict[str, object],
    ) -> dict[str, object]:
        source_status = str(source_preflight.get("formal_search_result_package_source_status", ""))
        base = {
            "formal_search_result_package_row_preflight_status": (
                "formal_search_result_package_row_preflight_blocked_at_source_preflight"
            ),
            "source_preflight_status": source_status,
            "formal_search_result_package_path": source_preflight.get(
                "formal_search_result_package_path", ""
            ),
            "checked_work_package_count": 0,
            "required_work_package_count": len(formal_search_result_package_template),
            "checked_hit_row_count": 0,
            "checked_comparison_row_count": 0,
            "checked_fallback_row_count": 0,
            "structurally_valid_hit_row_count": 0,
            "row_gap_count": 0,
            "row_gaps": [],
            "comparison_coverage_gap_count": 0,
            "comparison_coverage_gaps": [],
            "forbidden_review_boundary_count": 0,
            "forbidden_review_boundary_gaps": [],
            "can_route_to_validation_gate": False,
            "can_generate_prior_art_result": False,
            "legal_opinion_allowed": False,
            "field_claim_upgrade_allowed": False,
            "failure_boundary": (
                "该 row preflight 只检查正式检索结果包的行级字段、来源、查询和 reviewer 边界；"
                "通过后也只能进入 validation gate，不能直接生成 prior-art comparison、法律意见或 field-supported claim。"
            ),
        }
        if source_status != "formal_search_result_package_source_ready_for_validation_gate":
            return {
                **base,
                "preflight_blockers": list(source_preflight.get("preflight_blockers", [])),
            }

        path_value = str(source_preflight.get("formal_search_result_package_path", ""))
        try:
            payload = json.loads(Path(path_value).expanduser().read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            return {
                **base,
                "formal_search_result_package_row_preflight_status": (
                    "formal_search_result_package_row_preflight_unreadable_after_source_preflight"
                ),
                "preflight_blockers": [f"{path_value}:unreadable:{exc}"],
            }

        templates = {
            str(template["linked_work_package_id"]): template
            for template in formal_search_result_package_template
        }
        row_gaps: list[dict[str, object]] = []
        coverage_gaps: list[dict[str, object]] = []
        forbidden_gaps: list[dict[str, object]] = []
        valid_hit_count = 0
        hit_row_count = 0
        comparison_row_count = 0
        fallback_row_count = 0
        package_metadata = payload.get("package_metadata", {})
        root_required = [
            "package_id",
            "search_executor",
            "search_date",
            "reviewer_id",
            "review_time",
            "review_boundary_statement",
            "legal_status",
        ]
        if isinstance(package_metadata, dict):
            missing_root = self._empty_required_fields(package_metadata, root_required)
            if missing_root:
                row_gaps.append(
                    {
                        "scope": "package_metadata",
                        "issue": "missing_required_metadata_fields",
                        "fields": missing_root,
                    }
                )
            if self._contains_forbidden_review_text(package_metadata):
                forbidden_gaps.append(
                    {
                        "scope": "package_metadata",
                        "issue": "forbidden_legal_or_field_claim_text",
                    }
                )
        else:
            row_gaps.append(
                {
                    "scope": "package_metadata",
                    "issue": "metadata_not_object",
                    "fields": root_required,
                }
            )

        results = payload.get("work_package_results", {})
        checked_work_packages = 0
        for work_package_id, template in templates.items():
            result = results.get(work_package_id) if isinstance(results, dict) else None
            if not isinstance(result, dict):
                row_gaps.append(
                    {
                        "scope": work_package_id,
                        "issue": "work_package_result_missing_or_not_object",
                        "fields": ["work_package_results"],
                    }
                )
                continue
            checked_work_packages += 1
            manifest = result.get("package_manifest", {})
            if not isinstance(manifest, dict):
                row_gaps.append(
                    {
                        "scope": f"{work_package_id}.package_manifest",
                        "issue": "manifest_missing_or_not_object",
                        "fields": template["package_manifest_required_fields"],
                    }
                )
            else:
                missing_manifest = self._empty_required_fields(
                    manifest, template["package_manifest_required_fields"]
                )
                if missing_manifest:
                    row_gaps.append(
                        {
                            "scope": f"{work_package_id}.package_manifest",
                            "issue": "missing_required_manifest_fields",
                            "fields": missing_manifest,
                        }
                    )
                if manifest.get("linked_work_package_id") != work_package_id:
                    row_gaps.append(
                        {
                            "scope": f"{work_package_id}.package_manifest",
                            "issue": "linked_work_package_id_mismatch",
                            "fields": ["linked_work_package_id"],
                        }
                    )
                if self._contains_forbidden_review_text(manifest):
                    forbidden_gaps.append(
                        {
                            "scope": f"{work_package_id}.package_manifest",
                            "issue": "forbidden_legal_or_field_claim_text",
                        }
                    )

            hit_ids: set[str] = set()
            for row_index, hit in enumerate(result.get("prior_art_hit_table", [])):
                hit_row_count += 1
                scope = f"{work_package_id}.prior_art_hit_table[{row_index}]"
                if not isinstance(hit, dict):
                    row_gaps.append({"scope": scope, "issue": "row_not_object", "fields": []})
                    continue
                missing_hit = self._empty_required_fields(hit, PRIOR_ART_HIT_TABLE_FIELDS)
                if missing_hit:
                    row_gaps.append(
                        {"scope": scope, "issue": "missing_required_hit_fields", "fields": missing_hit}
                    )
                if hit.get("linked_work_package_id") != work_package_id:
                    row_gaps.append(
                        {"scope": scope, "issue": "linked_work_package_id_mismatch", "fields": ["linked_work_package_id"]}
                    )
                if hit.get("source_database") not in template["allowed_source_databases"]:
                    row_gaps.append(
                        {"scope": scope, "issue": "source_database_not_allowed", "fields": ["source_database"]}
                    )
                if hit.get("matched_query") not in template["allowed_query_sources"]:
                    row_gaps.append(
                        {"scope": scope, "issue": "matched_query_not_in_allowed_sources", "fields": ["matched_query"]}
                    )
                if self._contains_forbidden_review_text(hit):
                    forbidden_gaps.append(
                        {"scope": scope, "issue": "forbidden_legal_or_field_claim_text"}
                    )
                if not missing_hit:
                    hit_id = str(hit.get("hit_id"))
                    hit_ids.add(hit_id)
                    valid_hit_count += 1

            covered_project_elements: set[str] = set()
            for row_index, comparison in enumerate(result.get("claim_element_comparison_chart", [])):
                comparison_row_count += 1
                scope = f"{work_package_id}.claim_element_comparison_chart[{row_index}]"
                if not isinstance(comparison, dict):
                    row_gaps.append({"scope": scope, "issue": "row_not_object", "fields": []})
                    continue
                missing_comparison = self._empty_required_fields(
                    comparison, CLAIM_ELEMENT_COMPARISON_FIELDS
                )
                if missing_comparison:
                    row_gaps.append(
                        {
                            "scope": scope,
                            "issue": "missing_required_comparison_fields",
                            "fields": missing_comparison,
                        }
                    )
                if comparison.get("linked_work_package_id") != work_package_id:
                    row_gaps.append(
                        {"scope": scope, "issue": "linked_work_package_id_mismatch", "fields": ["linked_work_package_id"]}
                    )
                if str(comparison.get("linked_hit_id")) not in hit_ids:
                    row_gaps.append(
                        {"scope": scope, "issue": "linked_hit_id_not_found_in_hit_table", "fields": ["linked_hit_id"]}
                    )
                element_text = str(comparison.get("claim_or_feature_element", ""))
                for mapped_id in (
                    list(template["mapped_claim_ids"])
                    + list(template["mapped_feature_ids"])
                    + list(template["mapped_effect_ids"])
                ):
                    if str(mapped_id) in element_text:
                        covered_project_elements.add(str(mapped_id))
                if self._contains_forbidden_review_text(comparison):
                    forbidden_gaps.append(
                        {"scope": scope, "issue": "forbidden_legal_or_field_claim_text"}
                    )
            if not covered_project_elements:
                coverage_gaps.append(
                    {
                        "work_package_id": work_package_id,
                        "issue": "comparison_chart_does_not_cover_mapped_claim_feature_or_effect",
                        "mapped_claim_ids": list(template["mapped_claim_ids"]),
                        "mapped_feature_ids": list(template["mapped_feature_ids"]),
                        "mapped_effect_ids": list(template["mapped_effect_ids"]),
                    }
                )

            for row_index, fallback in enumerate(result.get("fallback_claim_scope_recommendation", [])):
                fallback_row_count += 1
                scope = f"{work_package_id}.fallback_claim_scope_recommendation[{row_index}]"
                if not isinstance(fallback, dict):
                    row_gaps.append({"scope": scope, "issue": "row_not_object", "fields": []})
                    continue
                missing_fallback = self._empty_required_fields(
                    fallback, template["fallback_recommendation_fields"]
                )
                if missing_fallback:
                    row_gaps.append(
                        {
                            "scope": scope,
                            "issue": "missing_required_fallback_fields",
                            "fields": missing_fallback,
                        }
                    )
                if fallback.get("linked_work_package_id") != work_package_id:
                    row_gaps.append(
                        {"scope": scope, "issue": "linked_work_package_id_mismatch", "fields": ["linked_work_package_id"]}
                    )
                if self._contains_forbidden_review_text(fallback):
                    forbidden_gaps.append(
                        {"scope": scope, "issue": "forbidden_legal_or_field_claim_text"}
                    )

        all_gaps = row_gaps + coverage_gaps + forbidden_gaps
        can_route = not all_gaps and checked_work_packages == len(templates)
        return {
            **base,
            "formal_search_result_package_row_preflight_status": (
                "formal_search_result_package_row_preflight_ready_for_validation_gate"
                if can_route
                else "formal_search_result_package_row_preflight_failed_row_contract"
            ),
            "source_preflight_status": source_status,
            "checked_work_package_count": checked_work_packages,
            "checked_hit_row_count": hit_row_count,
            "checked_comparison_row_count": comparison_row_count,
            "checked_fallback_row_count": fallback_row_count,
            "structurally_valid_hit_row_count": valid_hit_count,
            "row_gap_count": len(row_gaps),
            "row_gaps": row_gaps,
            "comparison_coverage_gap_count": len(coverage_gaps),
            "comparison_coverage_gaps": coverage_gaps,
            "forbidden_review_boundary_count": len(forbidden_gaps),
            "forbidden_review_boundary_gaps": forbidden_gaps,
            "preflight_blockers": [
                f"row_gap_count={len(row_gaps)}",
                f"comparison_coverage_gap_count={len(coverage_gaps)}",
                f"forbidden_review_boundary_count={len(forbidden_gaps)}",
            ]
            if all_gaps
            else [],
            "can_route_to_validation_gate": can_route,
            "can_generate_prior_art_result": False,
            "legal_opinion_allowed": False,
            "field_claim_upgrade_allowed": False,
        }

    def _formal_search_result_validation_execution(
        self,
        *,
        formal_search_result_validation_gate: list[dict[str, object]],
        formal_search_result_package_template: list[dict[str, object]],
        source_preflight: dict[str, object],
        row_preflight: dict[str, object],
    ) -> dict[str, object]:
        row_status = str(row_preflight.get("formal_search_result_package_row_preflight_status", ""))
        base = {
            "formal_search_result_validation_execution_status": (
                "formal_search_result_validation_execution_blocked_at_row_preflight"
            ),
            "source_preflight_status": source_preflight.get(
                "formal_search_result_package_source_status",
                "",
            ),
            "row_preflight_status": row_status,
            "formal_search_result_package_path": source_preflight.get(
                "formal_search_result_package_path",
                "",
            ),
            "required_work_package_count": len(formal_search_result_package_template),
            "work_package_execution_count": 0,
            "execution_row_count": 0,
            "validated_hit_count": 0,
            "rejected_hit_count": 0,
            "comparison_row_count": 0,
            "fallback_row_count": 0,
            "execution_rows": [],
            "execution_patch_plan": [],
            "can_enter_human_nonlegal_comparison_review": False,
            "can_generate_prior_art_result": False,
            "legal_opinion_allowed": False,
            "field_claim_upgrade_allowed": False,
            "failure_boundary": (
                "该 execution 只把通过 row preflight 的检索结果包转成结构验收计数、hit-comparison "
                "回连和下一步人工非法律比较审查入口；它不生成法律意见、不判断新颖性/创造性，"
                "也不能把任何检索结果升级为 field-supported claim。"
            ),
        }
        if row_status != "formal_search_result_package_row_preflight_ready_for_validation_gate":
            return {
                **base,
                "preflight_blockers": list(row_preflight.get("preflight_blockers", [])),
            }

        path_value = str(source_preflight.get("formal_search_result_package_path", ""))
        try:
            payload = json.loads(Path(path_value).expanduser().read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            return {
                **base,
                "formal_search_result_validation_execution_status": (
                    "formal_search_result_validation_execution_unreadable_after_row_preflight"
                ),
                "preflight_blockers": [f"{path_value}:unreadable:{exc}"],
            }

        templates = {
            str(template["linked_work_package_id"]): template
            for template in formal_search_result_package_template
        }
        gates = {
            str(gate["linked_work_package_id"]): gate
            for gate in formal_search_result_validation_gate
        }
        results = payload.get("work_package_results", {})
        execution_rows: list[dict[str, object]] = []
        patch_plan: list[dict[str, object]] = []
        validated_hit_count = 0
        rejected_hit_count = 0
        comparison_row_count = 0
        fallback_row_count = 0
        executed_work_packages = 0

        for work_package_id, template in templates.items():
            result = results.get(work_package_id) if isinstance(results, dict) else None
            if not isinstance(result, dict):
                patch_plan.append(
                    {
                        "patch_id": f"{work_package_id}_missing_execution_result",
                        "work_package_id": work_package_id,
                        "reason": "work_package_result_missing_after_row_preflight",
                        "next_action": "rerun row preflight and resubmit package",
                    }
                )
                continue
            executed_work_packages += 1
            comparisons = [
                row
                for row in result.get("claim_element_comparison_chart", [])
                if isinstance(row, dict)
            ]
            comparison_row_count += len(comparisons)
            fallback_rows = [
                row
                for row in result.get("fallback_claim_scope_recommendation", [])
                if isinstance(row, dict)
            ]
            fallback_row_count += len(fallback_rows)
            mapped_ids = [
                str(mapped_id)
                for mapped_id in (
                    list(template["mapped_claim_ids"])
                    + list(template["mapped_feature_ids"])
                    + list(template["mapped_effect_ids"])
                )
            ]
            for hit_index, hit in enumerate(result.get("prior_art_hit_table", [])):
                if not isinstance(hit, dict):
                    rejected_hit_count += 1
                    patch_plan.append(
                        {
                            "patch_id": f"{work_package_id}_hit_{hit_index}_not_object",
                            "work_package_id": work_package_id,
                            "reason": "hit_row_not_object_after_row_preflight",
                            "next_action": "rerun row preflight and resubmit hit row as object",
                        }
                    )
                    continue
                hit_id = str(hit.get("hit_id", ""))
                linked_comparisons = [
                    comparison
                    for comparison in comparisons
                    if str(comparison.get("linked_hit_id", "")) == hit_id
                ]
                covered_project_elements = sorted(
                    {
                        mapped_id
                        for comparison in linked_comparisons
                        for mapped_id in mapped_ids
                        if mapped_id in str(comparison.get("claim_or_feature_element", ""))
                    }
                )
                hit_ready = bool(hit_id and linked_comparisons and covered_project_elements)
                execution_status = (
                    "structural_hit_validated_for_human_nonlegal_comparison_review"
                    if hit_ready
                    else "structural_hit_rejected_needs_patch"
                )
                if hit_ready:
                    validated_hit_count += 1
                else:
                    rejected_hit_count += 1
                    patch_plan.append(
                        {
                            "patch_id": f"{work_package_id}_{hit_id or hit_index}_comparison_linkage_patch",
                            "work_package_id": work_package_id,
                            "hit_id": hit_id,
                            "reason": "missing_linked_comparison_or_mapped_project_element_coverage",
                            "next_action": (
                                "add claim_element_comparison_chart row linked to this hit and covering "
                                "at least one mapped claim, feature or effect id"
                            ),
                        }
                    )
                gate = gates.get(work_package_id, {})
                execution_rows.append(
                    {
                        "validation_gate_id": gate.get("validation_gate_id", ""),
                        "linked_work_package_id": work_package_id,
                        "hit_id": hit_id,
                        "source_database": hit.get("source_database", ""),
                        "matched_query": hit.get("matched_query", ""),
                        "comparison_row_count": len(linked_comparisons),
                        "covered_project_element_ids": covered_project_elements,
                        "fallback_row_count": len(fallback_rows),
                        "structural_validation_status": execution_status,
                        "legal_status": hit.get("legal_status", "not_legal_opinion"),
                        "field_claim_upgrade_allowed": False,
                    }
                )

        can_enter_review = (
            executed_work_packages == len(templates)
            and validated_hit_count > 0
            and rejected_hit_count == 0
            and not patch_plan
        )
        return {
            **base,
            "formal_search_result_validation_execution_status": (
                "formal_search_result_validation_execution_ready_for_human_nonlegal_comparison_review"
                if can_enter_review
                else "formal_search_result_validation_execution_failed_structural_acceptance"
            ),
            "formal_search_result_package_supplied": True,
            "work_package_execution_count": executed_work_packages,
            "execution_row_count": len(execution_rows),
            "validated_hit_count": validated_hit_count,
            "rejected_hit_count": rejected_hit_count,
            "comparison_row_count": comparison_row_count,
            "fallback_row_count": fallback_row_count,
            "execution_rows": execution_rows,
            "execution_patch_plan": patch_plan,
            "can_enter_human_nonlegal_comparison_review": can_enter_review,
            "preflight_blockers": [
                patch["patch_id"]
                for patch in patch_plan
            ],
            "can_generate_prior_art_result": False,
            "legal_opinion_allowed": False,
            "field_claim_upgrade_allowed": False,
        }

    @staticmethod
    def _formal_search_nonlegal_comparison_review_packet(
        *,
        validation_execution: dict[str, object],
    ) -> dict[str, object]:
        execution_status = str(
            validation_execution.get("formal_search_result_validation_execution_status", "")
        )
        base = {
            "formal_search_nonlegal_comparison_review_packet_status": (
                "formal_search_nonlegal_review_packet_blocked_at_validation_execution"
            ),
            "validation_execution_status": execution_status,
            "formal_search_result_package_path": validation_execution.get(
                "formal_search_result_package_path",
                "",
            ),
            "review_packet_row_count": 0,
            "required_reviewer_field_count": 8,
            "review_packet_rows": [],
            "review_packet_patch_plan": [],
            "human_review_completed": False,
            "can_enter_human_nonlegal_comparison_review": False,
            "can_generate_prior_art_result": False,
            "legal_opinion_allowed": False,
            "field_claim_upgrade_allowed": False,
            "required_reviewer_fields": [
                "reviewer_id",
                "review_time",
                "nonlegal_overlap_assessment",
                "distinguishing_technical_detail",
                "fallback_scope_recommendation",
                "preserved_field_validation_gate",
                "evidence_boundary_acknowledgement",
                "reviewer_signature_or_trace_id",
            ],
            "failure_boundary": (
                "该 review packet 只把结构验收通过的命中项组织成人工非法律技术比较审查任务；"
                "它不包含审查结论，不输出新颖性/创造性/授权判断，也不能替代正式检索报告、"
                "专利代理人意见或 field validation。"
            ),
        }
        if execution_status != (
            "formal_search_result_validation_execution_ready_for_human_nonlegal_comparison_review"
        ):
            return {
                **base,
                "preflight_blockers": list(validation_execution.get("preflight_blockers", [])),
            }

        review_rows: list[dict[str, object]] = []
        patch_plan: list[dict[str, object]] = []
        for index, row in enumerate(validation_execution.get("execution_rows", []), start=1):
            if not isinstance(row, dict):
                patch_plan.append(
                    {
                        "patch_id": f"FSNCRP_ROW_{index}_NOT_OBJECT",
                        "reason": "execution_row_not_object",
                        "next_action": "rerun validation execution and rebuild packet",
                    }
                )
                continue
            hit_id = str(row.get("hit_id", ""))
            covered_elements = [
                str(element)
                for element in row.get("covered_project_element_ids", [])
            ]
            work_package_id = str(row.get("linked_work_package_id", ""))
            if not hit_id or not covered_elements:
                patch_plan.append(
                    {
                        "patch_id": f"FSNCRP_{work_package_id or index}_MISSING_HIT_OR_ELEMENT",
                        "work_package_id": work_package_id,
                        "hit_id": hit_id,
                        "reason": "missing_hit_id_or_covered_project_element",
                        "next_action": "repair validation execution comparison coverage before human review",
                    }
                )
            review_rows.append(
                {
                    "review_packet_row_id": f"FSNCRP{index}_{work_package_id}_{hit_id}",
                    "linked_validation_gate_id": row.get("validation_gate_id", ""),
                    "linked_work_package_id": work_package_id,
                    "hit_id": hit_id,
                    "source_database": row.get("source_database", ""),
                    "matched_query": row.get("matched_query", ""),
                    "covered_project_element_ids": covered_elements,
                    "comparison_row_count": row.get("comparison_row_count", 0),
                    "fallback_row_count": row.get("fallback_row_count", 0),
                    "technical_distinction_review_questions": [
                        "Which covered project element is fully disclosed, partially disclosed, or absent in the hit?",
                        "What concrete system structure, state variable, control action, validation gate, or evidence boundary remains distinguishing?",
                        "Does the hit require narrowing a claim skeleton, moving an element to a dependent claim, or adding an embodiment limitation?",
                        "Which field replay, holdout, operator review, or release gate must be preserved before any field-supported claim?",
                    ],
                    "allowed_nonlegal_review_outputs": [
                        "retain_candidate_scope_pending_formal_review",
                        "narrow_to_distinguishing_greybox_loop_feature",
                        "move_to_dependent_or_fallback_claim",
                        "mark_high_overlap_needs_external_patent_counsel_review",
                        "request_additional_search_or_comparison_rows",
                    ],
                    "required_reviewer_fields": list(base["required_reviewer_fields"]),
                    "cannot_do": [
                        "cannot assert novelty or inventiveness",
                        "cannot assert patentability or authorization likelihood",
                        "cannot upgrade literature or search evidence into field-supported claim",
                        "cannot write actuator or release gate",
                    ],
                    "review_packet_row_status": (
                        "ready_for_human_nonlegal_technical_comparison"
                        if hit_id and covered_elements
                        else "needs_execution_patch_before_review"
                    ),
                }
            )

        packet_ready = bool(review_rows) and not patch_plan
        return {
            **base,
            "formal_search_nonlegal_comparison_review_packet_status": (
                "formal_search_nonlegal_review_packet_ready_waiting_for_human_review"
                if packet_ready
                else "formal_search_nonlegal_review_packet_needs_execution_patch"
            ),
            "review_packet_row_count": len(review_rows),
            "review_packet_rows": review_rows,
            "review_packet_patch_plan": patch_plan,
            "can_enter_human_nonlegal_comparison_review": packet_ready,
            "preflight_blockers": [
                str(patch["patch_id"])
                for patch in patch_plan
            ],
            "can_generate_prior_art_result": False,
            "legal_opinion_allowed": False,
            "field_claim_upgrade_allowed": False,
        }

    @staticmethod
    def _formal_search_nonlegal_review_response_template(
        *,
        review_packet: dict[str, object],
    ) -> dict[str, object]:
        packet_status = str(
            review_packet.get("formal_search_nonlegal_comparison_review_packet_status", "")
        )
        base = {
            "formal_search_nonlegal_review_response_template_status": (
                "formal_search_nonlegal_review_response_template_blocked_at_review_packet"
            ),
            "linked_review_packet_status": packet_status,
            "expected_env_var": "FORMAL_SEARCH_NONLEGAL_REVIEW_RESPONSE_PATH",
            "recommended_output_path": (
                "outputs/agent_architecture_consolidation/formal_search_nonlegal_review_response.json"
            ),
            "required_root_keys": ["review_metadata", "review_rows"],
            "review_metadata_required_fields": [
                "response_package_id",
                "reviewer_id",
                "review_time",
                "evidence_boundary_acknowledgement",
                "legal_status",
            ],
            "review_row_required_fields": list(NONLEGAL_REVIEW_RESPONSE_FIELDS),
            "expected_review_packet_row_ids": [],
            "response_template_rows": [],
            "review_response_supplied": False,
            "human_review_completed": False,
            "can_route_to_claim_scope_patch_draft": False,
            "can_generate_prior_art_result": False,
            "legal_opinion_allowed": False,
            "field_claim_upgrade_allowed": False,
            "template_marker_policy": (
                "Template/TODO rows must be replaced by human nonlegal technical comparison review records "
                "before source preflight may route the response."
            ),
            "failure_boundary": (
                "该 template 只定义人工非法律技术比较审查结果如何回填；它不是审查结果，不是法律意见，"
                "不判断授权概率，也不能升级 field-supported claim。"
            ),
        }
        if packet_status != "formal_search_nonlegal_review_packet_ready_waiting_for_human_review":
            return {
                **base,
                "preflight_blockers": ["review_packet:not_ready_for_human_review"],
            }

        rows = [
            row
            for row in review_packet.get("review_packet_rows", [])
            if isinstance(row, dict)
        ]
        response_rows = []
        for row in rows:
            response_rows.append(
                {
                    "review_packet_row_id": row.get("review_packet_row_id", ""),
                    "linked_work_package_id": row.get("linked_work_package_id", ""),
                    "hit_id": row.get("hit_id", ""),
                    "reviewer_id": "TODO_REVIEWER_ID",
                    "review_time": "TODO_REVIEW_TIME",
                    "nonlegal_overlap_assessment": "TODO_partial_full_absent_or_needs_more_search",
                    "distinguishing_technical_detail": "TODO_specific_system_structure_state_action_or_gate_difference",
                    "fallback_scope_recommendation": "TODO_retain_narrow_move_to_dependent_or_request_more_search",
                    "preserved_field_validation_gate": "TODO_field_replay_holdout_operator_review_or_release_gate",
                    "evidence_boundary_acknowledgement": "TODO_nonlegal_review_not_legal_or_field_claim",
                    "reviewer_signature_or_trace_id": "TODO_TRACE_ID",
                    "legal_status": "template_not_legal_opinion",
                    "template_only": True,
                }
            )
        return {
            **base,
            "formal_search_nonlegal_review_response_template_status": (
                "formal_search_nonlegal_review_response_template_ready_waiting_for_human_submission"
            ),
            "expected_review_packet_row_ids": [
                str(row.get("review_packet_row_id", ""))
                for row in rows
            ],
            "response_template_rows": response_rows,
            "preflight_blockers": [],
        }

    def _formal_search_nonlegal_review_response_source_preflight(
        self,
        *,
        review_packet: dict[str, object],
        response_template: dict[str, object],
    ) -> dict[str, object]:
        template_status = str(
            response_template.get(
                "formal_search_nonlegal_review_response_template_status",
                "",
            )
        )
        base = {
            "formal_search_nonlegal_review_response_source_status": (
                "formal_search_nonlegal_review_response_preflight_blocked_at_template"
            ),
            "linked_review_packet_status": review_packet.get(
                "formal_search_nonlegal_comparison_review_packet_status",
                "",
            ),
            "linked_response_template_status": template_status,
            "expected_env_var": "FORMAL_SEARCH_NONLEGAL_REVIEW_RESPONSE_PATH",
            "formal_search_nonlegal_review_response_path": self.formal_search_nonlegal_review_response_path or "",
            "expected_review_packet_row_count": len(
                response_template.get("expected_review_packet_row_ids", [])
            ),
            "accepted_review_row_count": 0,
            "rejected_review_row_count": 0,
            "review_response_gap_count": 0,
            "review_response_gaps": [],
            "forbidden_review_boundary_count": 0,
            "forbidden_review_boundary_gaps": [],
            "ai_draft_boundary_gap_count": 0,
            "ai_draft_boundary_gaps": [],
            "template_marker_gap_count": 0,
            "template_marker_gaps": [],
            "accepted_review_rows": [],
            "review_response_supplied": False,
            "human_review_completed": False,
            "can_route_to_claim_scope_patch_draft": False,
            "can_generate_prior_art_result": False,
            "legal_opinion_allowed": False,
            "field_claim_upgrade_allowed": False,
            "failure_boundary": (
                "该 preflight 只验收人工非法律技术比较审查回填包的结构、行覆盖和边界声明；"
                "即使通过，也只能进入 claim scope patch draft，不能生成 prior-art 结论、法律意见或现场 claim。"
            ),
        }
        if template_status != (
            "formal_search_nonlegal_review_response_template_ready_waiting_for_human_submission"
        ):
            return {
                **base,
                "preflight_blockers": list(response_template.get("preflight_blockers", [])),
            }

        path_value = self.formal_search_nonlegal_review_response_path
        if not path_value:
            return {
                **base,
                "formal_search_nonlegal_review_response_source_status": (
                    "formal_search_nonlegal_review_response_preflight_waiting_for_submission_path"
                ),
                "preflight_blockers": ["FORMAL_SEARCH_NONLEGAL_REVIEW_RESPONSE_PATH:not_set"],
            }
        path = Path(path_value).expanduser()
        if not path.exists():
            return {
                **base,
                "formal_search_nonlegal_review_response_source_status": (
                    "formal_search_nonlegal_review_response_file_missing"
                ),
                "preflight_blockers": [f"{path_value}:missing_file"],
            }
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            return {
                **base,
                "formal_search_nonlegal_review_response_source_status": (
                    "formal_search_nonlegal_review_response_unreadable"
                ),
                "review_response_supplied": True,
                "preflight_blockers": [f"{path_value}:unreadable:{exc}"],
            }
        gaps: list[dict[str, object]] = []
        forbidden_gaps: list[dict[str, object]] = []
        ai_draft_gaps: list[dict[str, object]] = []
        template_gaps = self._template_marker_gaps(payload, "root")
        required_metadata = list(response_template["review_metadata_required_fields"])
        required_row_fields = list(response_template["review_row_required_fields"])
        expected_ids = {
            str(row_id)
            for row_id in response_template.get("expected_review_packet_row_ids", [])
        }
        if not isinstance(payload, dict):
            gaps.append(
                {
                    "scope": "root",
                    "issue": "response_payload_not_object",
                    "fields": ["review_metadata", "review_rows"],
                }
            )
            review_rows = []
        else:
            metadata = payload.get("review_metadata", {})
            if not isinstance(metadata, dict):
                gaps.append(
                    {
                        "scope": "review_metadata",
                        "issue": "metadata_missing_or_not_object",
                        "fields": required_metadata,
                    }
                )
            else:
                missing_metadata = self._empty_required_fields(metadata, required_metadata)
                if missing_metadata:
                    gaps.append(
                        {
                            "scope": "review_metadata",
                            "issue": "missing_required_metadata_fields",
                            "fields": missing_metadata,
                        }
                    )
                if self._contains_forbidden_review_text(metadata):
                    forbidden_gaps.append(
                        {
                            "scope": "review_metadata",
                            "issue": "forbidden_legal_or_field_claim_text",
                        }
                    )
                ai_draft_gaps.extend(
                    self._ai_draft_boundary_gaps(metadata, "review_metadata")
                )
            review_rows_raw = payload.get("review_rows", [])
            if not isinstance(review_rows_raw, list):
                gaps.append(
                    {
                        "scope": "review_rows",
                        "issue": "review_rows_not_list",
                        "fields": ["review_rows"],
                    }
                )
                review_rows = []
            else:
                review_rows = review_rows_raw

        accepted_count = 0
        accepted_review_rows: list[dict[str, object]] = []
        seen_ids: set[str] = set()
        for index, row in enumerate(review_rows):
            scope = f"review_rows[{index}]"
            if not isinstance(row, dict):
                gaps.append({"scope": scope, "issue": "row_not_object", "fields": []})
                continue
            missing_fields = self._empty_required_fields(row, required_row_fields)
            if missing_fields:
                gaps.append(
                    {
                        "scope": scope,
                        "issue": "missing_required_review_fields",
                        "fields": missing_fields,
                    }
                )
            row_id = str(row.get("review_packet_row_id", ""))
            if row_id not in expected_ids:
                gaps.append(
                    {
                        "scope": scope,
                        "issue": "unknown_review_packet_row_id",
                        "fields": ["review_packet_row_id"],
                    }
                )
            else:
                seen_ids.add(row_id)
            row_forbidden = self._contains_forbidden_review_text(row)
            if row_forbidden:
                forbidden_gaps.append(
                    {
                        "scope": scope,
                        "issue": "forbidden_legal_or_field_claim_text",
                    }
                )
            row_ai_draft_gaps = self._ai_draft_boundary_gaps(row, scope)
            ai_draft_gaps.extend(row_ai_draft_gaps)
            if (
                not missing_fields
                and row_id in expected_ids
                and not row_forbidden
                and not row_ai_draft_gaps
            ):
                accepted_count += 1
                accepted_review_rows.append(
                    {field: row.get(field, "") for field in required_row_fields}
                )
        missing_rows = sorted(expected_ids - seen_ids)
        if missing_rows:
            gaps.append(
                {
                    "scope": "review_rows",
                    "issue": "missing_expected_review_packet_rows",
                    "fields": missing_rows,
                }
            )
        rejected_count = max(0, len(review_rows) - accepted_count) + len(missing_rows)
        can_route = (
            accepted_count == len(expected_ids)
            and rejected_count == 0
            and not gaps
            and not forbidden_gaps
            and not ai_draft_gaps
            and not template_gaps
            and bool(expected_ids)
        )
        return {
            **base,
            "formal_search_nonlegal_review_response_source_status": (
                "formal_search_nonlegal_review_response_ready_for_claim_scope_patch_draft"
                if can_route
                else "formal_search_nonlegal_review_response_failed_preflight"
            ),
            "formal_search_nonlegal_review_response_path": path_value,
            "accepted_review_row_count": accepted_count,
            "rejected_review_row_count": rejected_count,
            "review_response_gap_count": len(gaps),
            "review_response_gaps": gaps,
            "forbidden_review_boundary_count": len(forbidden_gaps),
            "forbidden_review_boundary_gaps": forbidden_gaps,
            "ai_draft_boundary_gap_count": len(ai_draft_gaps),
            "ai_draft_boundary_gaps": ai_draft_gaps,
            "template_marker_gap_count": len(template_gaps),
            "template_marker_gaps": template_gaps,
            "accepted_review_rows": accepted_review_rows if can_route else [],
            "review_response_supplied": True,
            "human_review_completed": can_route,
            "can_route_to_claim_scope_patch_draft": can_route,
            "preflight_blockers": [
                f"review_response_gap_count={len(gaps)}",
                f"forbidden_review_boundary_count={len(forbidden_gaps)}",
                f"ai_draft_boundary_count={len(ai_draft_gaps)}",
                f"template_marker_gap_count={len(template_gaps)}",
            ]
            if not can_route
            else [],
            "can_generate_prior_art_result": False,
            "legal_opinion_allowed": False,
            "field_claim_upgrade_allowed": False,
        }

    @staticmethod
    def _ai_draft_boundary_gaps(value: object, scope: str) -> list[dict[str, object]]:
        if not isinstance(value, dict):
            return []
        fields = ["reviewer_id", "reviewer_role", "legal_status", "evidence_boundary_acknowledgement"]
        ai_markers = (
            "ai_assistant",
            "ai_assisted",
            "ai-generated",
            "ai generated",
            "ai_draft",
            "ai draft",
            "llm_draft",
            "machine_generated",
        )
        matched = [
            field
            for field in fields
            if any(marker in str(value.get(field, "")).lower() for marker in ai_markers)
        ]
        if not matched:
            return []
        return [
            {
                "scope": scope,
                "issue": "ai_draft_cannot_satisfy_human_nonlegal_review",
                "fields": ["reviewer_role", "legal_status"],
            }
        ]

    @staticmethod
    def _formal_search_claim_scope_patch_draft(
        *,
        response_preflight: dict[str, object],
    ) -> dict[str, object]:
        response_status = str(
            response_preflight.get("formal_search_nonlegal_review_response_source_status", "")
        )
        base = {
            "formal_search_claim_scope_patch_draft_status": (
                "formal_search_claim_scope_patch_draft_blocked_at_nonlegal_review_response"
            ),
            "linked_nonlegal_review_response_status": response_status,
            "source_review_response_path": response_preflight.get(
                "formal_search_nonlegal_review_response_path",
                "",
            ),
            "draft_patch_count": 0,
            "claim_scope_patch_rows": [],
            "human_review_completed": response_preflight.get("human_review_completed", False),
            "can_route_to_formal_counsel_review": False,
            "can_emit_claim_text": False,
            "can_generate_prior_art_result": False,
            "legal_opinion_allowed": False,
            "field_claim_upgrade_allowed": False,
            "failure_boundary": (
                "该 scaffold 只把人工非法律技术比较结果转成待正式专利代理人/法律审查的技术范围修补建议；"
                "不能生成权利要求文本、不能判断新颖性/创造性/授权可能性，也不能把任何结论升级为现场成立。"
            ),
        }
        if response_status != "formal_search_nonlegal_review_response_ready_for_claim_scope_patch_draft":
            return {
                **base,
                "draft_blockers": [
                    f"nonlegal_review_response_status:{response_status or 'missing'}"
                ],
            }

        accepted_rows = [
            row
            for row in response_preflight.get("accepted_review_rows", [])
            if isinstance(row, dict)
        ]
        patch_rows = []
        for index, row in enumerate(accepted_rows, start=1):
            fallback = str(row.get("fallback_scope_recommendation", "")).lower()
            if "more_search" in fallback or "request_more_search" in fallback:
                technical_patch_candidate = "request_additional_formal_search_before_scope_decision"
            elif "dependent" in fallback:
                technical_patch_candidate = "move_or_duplicate_element_to_dependent_fallback_scope"
            elif "narrow" in fallback:
                technical_patch_candidate = "narrow_candidate_scope_to_distinguishing_technical_detail"
            else:
                technical_patch_candidate = "retain_candidate_scope_pending_formal_counsel_review"

            patch_rows.append(
                {
                    "claim_scope_patch_id": f"CSPD_{index:02d}",
                    "review_packet_row_id": row.get("review_packet_row_id", ""),
                    "linked_work_package_id": row.get("linked_work_package_id", ""),
                    "hit_id": row.get("hit_id", ""),
                    "nonlegal_overlap_assessment": row.get("nonlegal_overlap_assessment", ""),
                    "distinguishing_technical_detail": row.get(
                        "distinguishing_technical_detail",
                        "",
                    ),
                    "fallback_scope_recommendation": row.get(
                        "fallback_scope_recommendation",
                        "",
                    ),
                    "technical_patch_candidate": technical_patch_candidate,
                    "preserved_field_validation_gate": row.get(
                        "preserved_field_validation_gate",
                        "",
                    ),
                    "evidence_boundary_acknowledgement": row.get(
                        "evidence_boundary_acknowledgement",
                        "",
                    ),
                    "reviewer_signature_or_trace_id": row.get(
                        "reviewer_signature_or_trace_id",
                        "",
                    ),
                    "required_next_review": "formal_patent_counsel_review_required",
                    "patch_status": "draft_only_waiting_for_formal_counsel_review",
                    "cannot_do": [
                        "cannot_emit_claim_text",
                        "cannot_assert_novelty_or_inventiveness",
                        "cannot_assert_patentability_or_grant_likelihood",
                        "cannot_upgrade_to_field_supported_claim",
                    ],
                }
            )

        return {
            **base,
            "formal_search_claim_scope_patch_draft_status": (
                "formal_search_claim_scope_patch_draft_ready_for_formal_counsel_review"
            ),
            "draft_patch_count": len(patch_rows),
            "claim_scope_patch_rows": patch_rows,
            "can_route_to_formal_counsel_review": bool(patch_rows),
            "draft_blockers": [],
        }

    @staticmethod
    def _formal_counsel_review_response_template(
        *,
        claim_scope_patch_draft: dict[str, object],
    ) -> dict[str, object]:
        draft_status = str(
            claim_scope_patch_draft.get("formal_search_claim_scope_patch_draft_status", "")
        )
        base = {
            "formal_counsel_review_response_template_status": (
                "formal_counsel_review_response_template_blocked_at_claim_scope_patch_draft"
            ),
            "linked_claim_scope_patch_draft_status": draft_status,
            "expected_env_var": "FORMAL_COUNSEL_REVIEW_RESPONSE_PATH",
            "recommended_output_path": (
                "outputs/agent_architecture_consolidation/formal_counsel_review_response.json"
            ),
            "required_root_keys": ["review_metadata", "review_rows"],
            "review_metadata_required_fields": [
                "response_package_id",
                "formal_reviewer_id",
                "review_time",
                "boundary_acknowledgement",
                "legal_status",
            ],
            "review_row_required_fields": list(FORMAL_COUNSEL_REVIEW_RESPONSE_FIELDS),
            "expected_claim_scope_patch_ids": [],
            "response_template_rows": [],
            "formal_review_response_supplied": False,
            "external_formal_review_completed": False,
            "can_route_to_disclosure_revision_queue": False,
            "can_emit_claim_text": False,
            "can_generate_prior_art_result": False,
            "legal_opinion_allowed": False,
            "field_claim_upgrade_allowed": False,
            "template_marker_policy": (
                "Template/TODO rows must be replaced by external formal counsel or qualified patent review records; "
                "the system may only route accepted records to a disclosure revision queue."
            ),
            "failure_boundary": (
                "该 template 只定义外部正式审查结果如何回填；系统不生成权利要求文本，不判断新颖性、创造性或授权可能性，"
                "也不能把任何记录升级为现场成立。"
            ),
        }
        if draft_status != "formal_search_claim_scope_patch_draft_ready_for_formal_counsel_review":
            return {
                **base,
                "template_blockers": ["claim_scope_patch_draft:not_ready_for_formal_review"],
            }

        patch_rows = [
            row
            for row in claim_scope_patch_draft.get("claim_scope_patch_rows", [])
            if isinstance(row, dict)
        ]
        response_rows = []
        for row in patch_rows:
            response_rows.append(
                {
                    "claim_scope_patch_id": row.get("claim_scope_patch_id", ""),
                    "review_packet_row_id": row.get("review_packet_row_id", ""),
                    "linked_work_package_id": row.get("linked_work_package_id", ""),
                    "hit_id": row.get("hit_id", ""),
                    "formal_reviewer_id": "TODO_FORMAL_REVIEWER_ID",
                    "review_time": "TODO_REVIEW_TIME",
                    "scope_review_disposition": "TODO_retain_narrow_dependent_drop_or_more_search",
                    "approved_technical_revision_summary": "TODO_technical_revision_summary_not_claim_text",
                    "required_disclosure_revision": "TODO_disclosure_revision_task",
                    "preserved_field_validation_gate": row.get("preserved_field_validation_gate", ""),
                    "required_followup_search_or_evidence": "TODO_followup_search_or_evidence_need",
                    "boundary_acknowledgement": "TODO_external_review_record_not_system_generated_legal_or_field_claim",
                    "formal_review_trace_id": "TODO_FORMAL_TRACE_ID",
                    "legal_status": "template_external_review_record_not_system_opinion",
                    "template_only": True,
                }
            )
        return {
            **base,
            "formal_counsel_review_response_template_status": (
                "formal_counsel_review_response_template_ready_waiting_for_external_formal_review"
            ),
            "expected_claim_scope_patch_ids": [
                str(row.get("claim_scope_patch_id", ""))
                for row in patch_rows
            ],
            "response_template_rows": response_rows,
            "template_blockers": [],
        }

    def _formal_counsel_review_response_source_preflight(
        self,
        *,
        response_template: dict[str, object],
    ) -> dict[str, object]:
        template_status = str(
            response_template.get("formal_counsel_review_response_template_status", "")
        )
        base = {
            "formal_counsel_review_response_source_status": (
                "formal_counsel_review_response_preflight_blocked_at_template"
            ),
            "linked_response_template_status": template_status,
            "expected_env_var": "FORMAL_COUNSEL_REVIEW_RESPONSE_PATH",
            "formal_counsel_review_response_path": self.formal_counsel_review_response_path or "",
            "expected_claim_scope_patch_count": len(
                response_template.get("expected_claim_scope_patch_ids", [])
            ),
            "accepted_formal_review_row_count": 0,
            "rejected_formal_review_row_count": 0,
            "formal_review_gap_count": 0,
            "formal_review_gaps": [],
            "forbidden_formal_review_boundary_count": 0,
            "forbidden_formal_review_boundary_gaps": [],
            "template_marker_gap_count": 0,
            "template_marker_gaps": [],
            "accepted_formal_review_rows": [],
            "formal_review_response_supplied": False,
            "external_formal_review_completed": False,
            "can_route_to_disclosure_revision_queue": False,
            "can_emit_claim_text": False,
            "can_generate_prior_art_result": False,
            "legal_opinion_allowed": False,
            "field_claim_upgrade_allowed": False,
            "failure_boundary": (
                "该 preflight 只验收外部正式审查回填包的结构、patch 覆盖和边界声明；"
                "通过后也只能进入技术交底修订队列，不能由系统生成法律意见、授权判断、权利要求文本或现场 claim。"
            ),
        }
        if template_status != (
            "formal_counsel_review_response_template_ready_waiting_for_external_formal_review"
        ):
            return {
                **base,
                "preflight_blockers": list(response_template.get("template_blockers", [])),
            }

        path_value = self.formal_counsel_review_response_path
        if not path_value:
            return {
                **base,
                "formal_counsel_review_response_source_status": (
                    "formal_counsel_review_response_preflight_waiting_for_submission_path"
                ),
                "preflight_blockers": ["FORMAL_COUNSEL_REVIEW_RESPONSE_PATH:not_set"],
            }
        path = Path(path_value).expanduser()
        if not path.exists():
            return {
                **base,
                "formal_counsel_review_response_source_status": (
                    "formal_counsel_review_response_file_missing"
                ),
                "preflight_blockers": [f"{path_value}:missing_file"],
            }
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            return {
                **base,
                "formal_counsel_review_response_source_status": (
                    "formal_counsel_review_response_unreadable"
                ),
                "formal_review_response_supplied": True,
                "preflight_blockers": [f"{path_value}:unreadable:{exc}"],
            }

        gaps: list[dict[str, object]] = []
        forbidden_gaps: list[dict[str, object]] = []
        template_gaps = self._template_marker_gaps(payload, "root")
        required_metadata = list(response_template["review_metadata_required_fields"])
        required_row_fields = list(response_template["review_row_required_fields"])
        expected_ids = {
            str(row_id)
            for row_id in response_template.get("expected_claim_scope_patch_ids", [])
        }
        if not isinstance(payload, dict):
            gaps.append(
                {
                    "scope": "root",
                    "issue": "response_payload_not_object",
                    "fields": ["review_metadata", "review_rows"],
                }
            )
            review_rows = []
        else:
            metadata = payload.get("review_metadata", {})
            if not isinstance(metadata, dict):
                gaps.append(
                    {
                        "scope": "review_metadata",
                        "issue": "metadata_missing_or_not_object",
                        "fields": required_metadata,
                    }
                )
            else:
                missing_metadata = self._empty_required_fields(metadata, required_metadata)
                if missing_metadata:
                    gaps.append(
                        {
                            "scope": "review_metadata",
                            "issue": "missing_required_metadata_fields",
                            "fields": missing_metadata,
                        }
                    )
                if self._contains_forbidden_formal_counsel_routing_text(metadata):
                    forbidden_gaps.append(
                        {
                            "scope": "review_metadata",
                            "issue": "forbidden_legal_conclusion_or_field_claim_text",
                        }
                    )
            review_rows_raw = payload.get("review_rows", [])
            if not isinstance(review_rows_raw, list):
                gaps.append(
                    {
                        "scope": "review_rows",
                        "issue": "review_rows_not_list",
                        "fields": ["review_rows"],
                    }
                )
                review_rows = []
            else:
                review_rows = review_rows_raw

        accepted_count = 0
        accepted_rows: list[dict[str, object]] = []
        seen_ids: set[str] = set()
        for index, row in enumerate(review_rows):
            scope = f"review_rows[{index}]"
            if not isinstance(row, dict):
                gaps.append({"scope": scope, "issue": "row_not_object", "fields": []})
                continue
            missing_fields = self._empty_required_fields(row, required_row_fields)
            if missing_fields:
                gaps.append(
                    {
                        "scope": scope,
                        "issue": "missing_required_formal_review_fields",
                        "fields": missing_fields,
                    }
                )
            patch_id = str(row.get("claim_scope_patch_id", ""))
            if patch_id not in expected_ids:
                gaps.append(
                    {
                        "scope": scope,
                        "issue": "unknown_claim_scope_patch_id",
                        "fields": ["claim_scope_patch_id"],
                    }
                )
            else:
                seen_ids.add(patch_id)
            row_forbidden = self._contains_forbidden_formal_counsel_routing_text(row)
            if row_forbidden:
                forbidden_gaps.append(
                    {
                        "scope": scope,
                        "issue": "forbidden_legal_conclusion_or_field_claim_text",
                    }
                )
            if not missing_fields and patch_id in expected_ids and not row_forbidden:
                accepted_count += 1
                accepted_rows.append({field: row.get(field, "") for field in required_row_fields})

        missing_rows = sorted(expected_ids - seen_ids)
        if missing_rows:
            gaps.append(
                {
                    "scope": "review_rows",
                    "issue": "missing_expected_claim_scope_patch_rows",
                    "fields": missing_rows,
                }
            )
        rejected_count = max(0, len(review_rows) - accepted_count) + len(missing_rows)
        can_route = (
            accepted_count == len(expected_ids)
            and rejected_count == 0
            and not gaps
            and not forbidden_gaps
            and not template_gaps
            and bool(expected_ids)
        )
        return {
            **base,
            "formal_counsel_review_response_source_status": (
                "formal_counsel_review_response_ready_for_disclosure_revision_queue"
                if can_route
                else "formal_counsel_review_response_failed_preflight"
            ),
            "formal_counsel_review_response_path": path_value,
            "accepted_formal_review_row_count": accepted_count,
            "rejected_formal_review_row_count": rejected_count,
            "formal_review_gap_count": len(gaps),
            "formal_review_gaps": gaps,
            "forbidden_formal_review_boundary_count": len(forbidden_gaps),
            "forbidden_formal_review_boundary_gaps": forbidden_gaps,
            "template_marker_gap_count": len(template_gaps),
            "template_marker_gaps": template_gaps,
            "accepted_formal_review_rows": accepted_rows if can_route else [],
            "formal_review_response_supplied": True,
            "external_formal_review_completed": can_route,
            "can_route_to_disclosure_revision_queue": can_route,
            "preflight_blockers": [
                f"formal_review_gap_count={len(gaps)}",
                f"forbidden_formal_review_boundary_count={len(forbidden_gaps)}",
                f"template_marker_gap_count={len(template_gaps)}",
            ]
            if not can_route
            else [],
            "can_emit_claim_text": False,
            "can_generate_prior_art_result": False,
            "legal_opinion_allowed": False,
            "field_claim_upgrade_allowed": False,
        }

    @staticmethod
    def _formal_disclosure_revision_queue(
        *,
        formal_counsel_preflight: dict[str, object],
    ) -> dict[str, object]:
        preflight_status = str(
            formal_counsel_preflight.get("formal_counsel_review_response_source_status", "")
        )
        base = {
            "formal_disclosure_revision_queue_status": (
                "formal_disclosure_revision_queue_blocked_at_formal_counsel_review_response"
            ),
            "linked_formal_counsel_review_response_status": preflight_status,
            "source_formal_counsel_review_response_path": formal_counsel_preflight.get(
                "formal_counsel_review_response_path",
                "",
            ),
            "revision_item_count": 0,
            "disclosure_revision_items": [],
            "external_formal_review_completed": formal_counsel_preflight.get(
                "external_formal_review_completed",
                False,
            ),
            "can_route_to_disclosure_editor": False,
            "can_apply_disclosure_revision_automatically": False,
            "can_emit_claim_text": False,
            "can_generate_prior_art_result": False,
            "legal_opinion_allowed": False,
            "field_claim_upgrade_allowed": False,
            "failure_boundary": (
                "该 queue 只把外部正式审查通过预检的技术修订要求转成技术交底修订任务；"
                "不能自动改写权利要求、不能生成法律意见、不能判断授权可能性，也不能绕过现场验证门。"
            ),
        }
        if preflight_status != "formal_counsel_review_response_ready_for_disclosure_revision_queue":
            return {
                **base,
                "queue_blockers": [
                    f"formal_counsel_review_response_status:{preflight_status or 'missing'}"
                ],
            }

        accepted_rows = [
            row
            for row in formal_counsel_preflight.get("accepted_formal_review_rows", [])
            if isinstance(row, dict)
        ]
        revision_items = []
        for index, row in enumerate(accepted_rows, start=1):
            disposition = str(row.get("scope_review_disposition", "")).lower()
            if "drop" in disposition:
                revision_action = "mark_candidate_scope_for_removal_from_disclosure_scaffold"
            elif "dependent" in disposition:
                revision_action = "move_technical_detail_to_dependent_or_fallback_embodiment"
            elif "narrow" in disposition:
                revision_action = "narrow_disclosure_scope_with_specific_technical_boundary"
            elif "more_search" in disposition or "followup" in disposition:
                revision_action = "hold_revision_until_followup_search_or_evidence"
            else:
                revision_action = "retain_and_expand_disclosure_implementation_detail"
            revision_items.append(
                {
                    "disclosure_revision_item_id": f"DRQ_{index:02d}",
                    "claim_scope_patch_id": row.get("claim_scope_patch_id", ""),
                    "review_packet_row_id": row.get("review_packet_row_id", ""),
                    "linked_work_package_id": row.get("linked_work_package_id", ""),
                    "hit_id": row.get("hit_id", ""),
                    "scope_review_disposition": row.get("scope_review_disposition", ""),
                    "revision_action": revision_action,
                    "approved_technical_revision_summary": row.get(
                        "approved_technical_revision_summary",
                        "",
                    ),
                    "required_disclosure_revision": row.get(
                        "required_disclosure_revision",
                        "",
                    ),
                    "preserved_field_validation_gate": row.get(
                        "preserved_field_validation_gate",
                        "",
                    ),
                    "required_followup_search_or_evidence": row.get(
                        "required_followup_search_or_evidence",
                        "",
                    ),
                    "formal_review_trace_id": row.get("formal_review_trace_id", ""),
                    "revision_status": "queued_for_human_disclosure_editor",
                    "cannot_do": [
                        "cannot_apply_revision_automatically",
                        "cannot_emit_claim_text",
                        "cannot_assert_novelty_or_inventiveness",
                        "cannot_upgrade_to_field_supported_claim",
                    ],
                }
            )
        return {
            **base,
            "formal_disclosure_revision_queue_status": (
                "formal_disclosure_revision_queue_ready_for_human_disclosure_editor"
            ),
            "revision_item_count": len(revision_items),
            "disclosure_revision_items": revision_items,
            "can_route_to_disclosure_editor": bool(revision_items),
            "queue_blockers": [],
        }

    @staticmethod
    def _formal_disclosure_revision_impact_plan(
        *,
        disclosure_revision_queue: dict[str, object],
    ) -> dict[str, object]:
        queue_status = str(
            disclosure_revision_queue.get("formal_disclosure_revision_queue_status", "")
        )
        base = {
            "formal_disclosure_revision_impact_plan_status": (
                "formal_disclosure_revision_impact_plan_blocked_at_revision_queue"
            ),
            "linked_formal_disclosure_revision_queue_status": queue_status,
            "revision_impact_item_count": 0,
            "revision_impact_items": [],
            "can_route_to_human_artifact_revision": False,
            "can_apply_artifact_patch_automatically": False,
            "can_emit_claim_text": False,
            "can_generate_prior_art_result": False,
            "legal_opinion_allowed": False,
            "field_claim_upgrade_allowed": False,
            "failure_boundary": (
                "该 impact plan 只把人工交底修订队列映射到核心技术交底工件；"
                "不能自动改写工件、不能输出权利要求文本、不能生成 prior-art 结论、"
                "不能替代正式法律意见，也不能把 template/synthetic 结果升级为 field claim。"
            ),
        }
        if queue_status != "formal_disclosure_revision_queue_ready_for_human_disclosure_editor":
            return {
                **base,
                "impact_plan_blockers": [
                    f"formal_disclosure_revision_queue_status:{queue_status or 'missing'}"
                ],
            }

        revision_items = [
            item
            for item in disclosure_revision_queue.get("disclosure_revision_items", [])
            if isinstance(item, dict)
        ]
        impact_items = []
        for index, item in enumerate(revision_items, start=1):
            followup = str(item.get("required_followup_search_or_evidence", "")).strip()
            followup_lower = followup.lower()
            target_artifacts = [
                "patent_technical_feature_ledger",
                "technical_claim_skeleton_scaffold",
                "technical_embodiment_validation_matrix",
                "technical_effect_measurement_matrix",
                "prior_art_distinction_matrix",
            ]
            if followup and not any(
                marker in followup_lower
                for marker in (
                    "no additional source",
                    "no additional evidence",
                    "none",
                    "not required",
                )
            ):
                target_artifacts.append("formal_search_work_package_matrix")
            impact_items.append(
                {
                    "revision_impact_item_id": f"DRIP_{index:02d}",
                    "disclosure_revision_item_id": item.get(
                        "disclosure_revision_item_id",
                        "",
                    ),
                    "claim_scope_patch_id": item.get("claim_scope_patch_id", ""),
                    "linked_work_package_id": item.get("linked_work_package_id", ""),
                    "hit_id": item.get("hit_id", ""),
                    "revision_action": item.get("revision_action", ""),
                    "approved_technical_revision_summary": item.get(
                        "approved_technical_revision_summary",
                        "",
                    ),
                    "required_disclosure_revision": item.get(
                        "required_disclosure_revision",
                        "",
                    ),
                    "preserved_field_validation_gate": item.get(
                        "preserved_field_validation_gate",
                        "",
                    ),
                    "required_followup_search_or_evidence": followup,
                    "formal_review_trace_id": item.get("formal_review_trace_id", ""),
                    "target_artifacts": target_artifacts,
                    "human_revision_steps": [
                        "update technical feature ledger with the approved technical revision summary",
                        "check claim skeleton scaffold for element-boundary consistency without emitting claim text",
                        "update embodiment and validation matrices with implementable detail and field gate limits",
                        "update technical effect matrix only where the effect can stay tied to synthetic/literature/template evidence",
                        "update prior-art distinction matrix as a nonlegal technical comparison record",
                    ],
                    "verification_before_acceptance": [
                        "formal review trace id remains linked",
                        "field validation gate remains preserved",
                        "no automatic claim text is emitted",
                        "no prior-art conclusion or legal opinion is generated",
                    ],
                    "impact_status": "impact_plan_waiting_for_human_artifact_revision",
                    "cannot_do": [
                        "cannot_apply_artifact_patch_automatically",
                        "cannot_emit_claim_text",
                        "cannot_assert_novelty_or_inventiveness",
                        "cannot_generate_prior_art_result",
                        "cannot_upgrade_to_field_supported_claim",
                    ],
                }
            )
        return {
            **base,
            "formal_disclosure_revision_impact_plan_status": (
                "formal_disclosure_revision_impact_plan_ready_for_human_artifact_revision"
            ),
            "revision_impact_item_count": len(impact_items),
            "revision_impact_items": impact_items,
            "can_route_to_human_artifact_revision": bool(impact_items),
            "impact_plan_blockers": [],
        }

    @staticmethod
    def _formal_search_execution_route_plan(
        *,
        formal_search_work_package_matrix: list[dict[str, object]],
        formal_search_result_package_template: list[dict[str, object]],
        formal_search_result_package_submission_template: dict[str, object],
        formal_search_review_readiness: dict[str, object],
        nonlegal_prior_art_seed_matrix: dict[str, object],
    ) -> dict[str, object]:
        templates_by_work_package = {
            str(template.get("linked_work_package_id", "")): template
            for template in formal_search_result_package_template
            if isinstance(template, dict)
        }
        seed_rows = [
            row
            for row in nonlegal_prior_art_seed_matrix.get("prior_art_seed_rows", [])
            if isinstance(row, dict)
        ]
        seed_status = str(
            nonlegal_prior_art_seed_matrix.get(
                "status",
                "optional_nonlegal_prior_art_seed_matrix_not_supplied",
            )
        )
        route_rows: list[dict[str, object]] = []
        for index, work_package in enumerate(formal_search_work_package_matrix, start=1):
            work_package_id = str(work_package.get("work_package_id", ""))
            template = templates_by_work_package.get(work_package_id, {})
            mapped_feature_ids = {
                str(feature_id)
                for feature_id in work_package.get("mapped_feature_ids", [])
            }
            mapped_seed_rows = [
                seed
                for seed in seed_rows
                if mapped_feature_ids.intersection(
                    {
                        str(feature_id)
                        for feature_id in seed.get("mapped_project_features", [])
                    }
                )
            ]
            search_databases = [
                str(database)
                for database in work_package.get("search_databases", [])
            ]
            english_queries = [
                str(query)
                for query in work_package.get("english_search_queries", [])
            ]
            chinese_queries = [
                str(query)
                for query in work_package.get("chinese_search_queries", [])
            ]
            required_tables = list(
                formal_search_result_package_submission_template.get(
                    "required_result_tables",
                    [],
                )
            )
            required_manifest_fields = list(
                template.get("package_manifest_required_fields", [])
            )
            route_gaps = []
            if not search_databases:
                route_gaps.append("missing_search_databases")
            if not english_queries and not chinese_queries:
                route_gaps.append("missing_generated_search_queries")
            if not required_tables:
                route_gaps.append("missing_required_result_tables")
            if not required_manifest_fields:
                route_gaps.append("missing_package_manifest_required_fields")
            route_ready = not route_gaps
            route_rows.append(
                {
                    "route_id": f"FSERP{index}_{work_package_id}",
                    "linked_work_package_id": work_package_id,
                    "execution_order": index,
                    "search_objective": work_package.get("search_objective", ""),
                    "mapped_claim_ids": list(work_package.get("mapped_claim_ids", [])),
                    "mapped_feature_ids": list(work_package.get("mapped_feature_ids", [])),
                    "mapped_effect_ids": list(work_package.get("mapped_effect_ids", [])),
                    "mapped_nonlegal_seed_ids": [
                        str(seed.get("seed_id", ""))
                        for seed in mapped_seed_rows
                    ],
                    "mapped_nonlegal_seed_urls": [
                        str(seed.get("url", ""))
                        for seed in mapped_seed_rows
                    ],
                    "seed_mapping_status": (
                        "nonlegal_prior_art_seed_references_available"
                        if mapped_seed_rows
                        else "no_optional_seed_reference_matched"
                    ),
                    "search_databases": search_databases,
                    "classification_hints": list(work_package.get("classification_hints", [])),
                    "english_search_queries": english_queries,
                    "chinese_search_queries": chinese_queries,
                    "reviewer_approved_expansion_rule": (
                        "Additional queries are allowed only if the reviewer records the query text, "
                        "database, date and rationale; expansions are not accepted as hidden model output."
                    ),
                    "required_result_tables": required_tables,
                    "result_package_root_key": work_package_id,
                    "package_manifest_required_fields": required_manifest_fields,
                    "prior_art_hit_table_required_fields": list(
                        template.get(
                            "prior_art_hit_table_template_fields",
                            PRIOR_ART_HIT_TABLE_FIELDS,
                        )
                    ),
                    "claim_element_comparison_required_fields": list(
                        template.get(
                            "claim_element_comparison_template_fields",
                            CLAIM_ELEMENT_COMPARISON_FIELDS,
                        )
                    ),
                    "execution_steps": [
                        "run each generated English and Chinese query against all allowed databases",
                        "record query_log entries with database, query text, date and executor",
                        "fill prior_art_hit_table only with reviewer-confirmed publications, patents or papers",
                        "fill claim_element_comparison_chart for every accepted hit and every mapped element it touches",
                        "state both disclosed capabilities and missing project elements before any fallback recommendation",
                        "fill fallback_claim_scope_recommendation as nonlegal technical scope guidance only",
                        "submit the assembled JSON path through FORMAL_SEARCH_RESULT_PACKAGE_PATH",
                    ],
                    "rejection_boundaries": [
                        "reject TODO/template/sample rows",
                        "reject rows without publication_or_patent_id and url_or_reference",
                        "reject source_database values outside this route",
                        "reject matched_query values without generated or reviewer-approved provenance",
                        "reject reviewer text asserting novelty, inventiveness, authorization likelihood or legal opinion",
                        "reject any field_claim_upgrade_allowed=true before field validation gates",
                    ],
                    "field_validation_gate_to_preserve": work_package.get(
                        "field_validation_gate_to_preserve",
                        "",
                    ),
                    "route_gaps": route_gaps,
                    "route_ready_status": (
                        "formal_search_execution_route_ready_waiting_for_external_search"
                        if route_ready
                        else "formal_search_execution_route_needs_patch"
                    ),
                    "can_generate_prior_art_result": False,
                    "legal_opinion_allowed": False,
                    "can_emit_claim_text": False,
                    "field_claim_upgrade_allowed": False,
                }
            )
        complete_routes = [
            row
            for row in route_rows
            if row["route_ready_status"]
            == "formal_search_execution_route_ready_waiting_for_external_search"
        ]
        mapped_seed_route_count = len(
            [
                row
                for row in route_rows
                if row["mapped_nonlegal_seed_ids"]
            ]
        )
        route_plan_ready = len(complete_routes) == len(route_rows) and bool(route_rows)
        package_path_missing = (
            formal_search_review_readiness.get("highest_priority_blocker")
            == "FSR_SOURCE_PREFLIGHT"
        )
        return {
            "artifact_id": "R8u79_formal_search_execution_route_plan",
            "route_plan_status": (
                "formal_search_execution_route_plan_ready_waiting_for_external_search_execution"
                if route_plan_ready
                else "formal_search_execution_route_plan_needs_patch"
            ),
            "linked_review_readiness_status": formal_search_review_readiness.get(
                "formal_search_review_readiness_status",
                "",
            ),
            "linked_review_highest_priority_blocker": formal_search_review_readiness.get(
                "highest_priority_blocker",
                "",
            ),
            "operator_first_action": (
                "execute_external_or_human_search_and_submit_FORMAL_SEARCH_RESULT_PACKAGE_PATH"
                if package_path_missing
                else formal_search_review_readiness.get("next_operator_action", "")
            ),
            "expected_env_var": formal_search_result_package_submission_template.get(
                "expected_env_var",
                "FORMAL_SEARCH_RESULT_PACKAGE_PATH",
            ),
            "recommended_output_path": formal_search_result_package_submission_template.get(
                "recommended_output_path",
                "outputs/agent_architecture_consolidation/formal_search_result_package_submission.json",
            ),
            "nonlegal_prior_art_seed_matrix_status": seed_status,
            "route_row_count": len(route_rows),
            "complete_route_row_count": len(complete_routes),
            "mapped_seed_route_count": mapped_seed_route_count,
            "route_rows": route_rows,
            "route_patch_plan": [
                {
                    "route_id": row["route_id"],
                    "linked_work_package_id": row["linked_work_package_id"],
                    "route_gaps": row["route_gaps"],
                    "next_action": "repair_work_package_or_submission_template_before_external_search",
                }
                for row in route_rows
                if row["route_gaps"]
            ],
            "can_generate_prior_art_result": False,
            "legal_opinion_allowed": False,
            "can_emit_claim_text": False,
            "field_claim_upgrade_allowed": False,
            "can_submit_synthetic_or_template_result_package": False,
            "failure_boundary": (
                "该 route plan 只把正式检索工作包、查询、数据库、seed references 和结果包填报合同连接成"
                "人工/外部检索执行路线；它不是正式检索结果，不接受 template/sample/TODO 行，"
                "不生成 prior-art 结论、法律意见、权利要求文本或 field-supported claim。"
            ),
        }

    @staticmethod
    def _formal_search_review_readiness(
        *,
        source_preflight: dict[str, object],
        row_preflight: dict[str, object],
        validation_execution: dict[str, object],
        nonlegal_review_packet: dict[str, object],
        nonlegal_response_preflight: dict[str, object],
        claim_scope_patch_draft: dict[str, object],
        formal_counsel_preflight: dict[str, object],
        disclosure_revision_queue: dict[str, object],
        disclosure_revision_impact_plan: dict[str, object],
    ) -> dict[str, object]:
        artifacts = {
            "source_preflight": source_preflight,
            "row_preflight": row_preflight,
            "validation_execution": validation_execution,
            "nonlegal_review_packet": nonlegal_review_packet,
            "nonlegal_response_preflight": nonlegal_response_preflight,
            "claim_scope_patch_draft": claim_scope_patch_draft,
            "formal_counsel_preflight": formal_counsel_preflight,
            "disclosure_revision_queue": disclosure_revision_queue,
            "disclosure_revision_impact_plan": disclosure_revision_impact_plan,
        }
        forbidden_flags = (
            "can_generate_prior_art_result",
            "legal_opinion_allowed",
            "field_claim_upgrade_allowed",
            "can_emit_claim_text",
        )
        boundary_violations = [
            {
                "artifact": artifact_name,
                "flag": flag,
                "value": artifact.get(flag),
            }
            for artifact_name, artifact in artifacts.items()
            for flag in forbidden_flags
            if bool(artifact.get(flag, False))
        ]
        boundary_ok = not boundary_violations
        source_ready = bool(source_preflight.get("can_route_to_validation_gate", False))
        row_ready = bool(row_preflight.get("can_route_to_validation_gate", False))
        validation_ready = bool(
            validation_execution.get("can_enter_human_nonlegal_comparison_review", False)
        )
        packet_ready = bool(
            nonlegal_review_packet.get(
                "can_enter_human_nonlegal_comparison_review",
                False,
            )
        )
        nonlegal_response_ready = bool(
            nonlegal_response_preflight.get("can_route_to_claim_scope_patch_draft", False)
        )
        claim_scope_ready = bool(
            claim_scope_patch_draft.get("can_route_to_formal_counsel_review", False)
        )
        formal_counsel_ready = bool(
            formal_counsel_preflight.get("can_route_to_disclosure_revision_queue", False)
        )
        disclosure_queue_ready = bool(
            disclosure_revision_queue.get("can_route_to_disclosure_editor", False)
        )
        disclosure_impact_ready = bool(
            disclosure_revision_impact_plan.get("can_route_to_human_artifact_revision", False)
        )

        def stage(
            stage_id: str,
            status: object,
            passed: bool,
            next_action: str,
            blockers: object,
        ) -> dict[str, object]:
            blocker_list = blockers if isinstance(blockers, list) else []
            return {
                "stage_id": stage_id,
                "status": status,
                "passed": passed,
                "next_operator_action": next_action,
                "blockers": blocker_list,
            }

        stage_checks = [
            stage(
                "NO_LEGAL_OR_FIELD_CLAIM_BOUNDARY",
                "boundary_passed" if boundary_ok else "boundary_violation",
                boundary_ok,
                "remove_forbidden_legal_claim_or_field_upgrade_flag",
                boundary_violations,
            ),
            stage(
                "FSR_SOURCE_PREFLIGHT",
                source_preflight.get("formal_search_result_package_source_status", ""),
                source_ready,
                "submit_formal_search_result_package",
                source_preflight.get("preflight_blockers", []),
            ),
            stage(
                "FSR_ROW_PREFLIGHT",
                row_preflight.get("formal_search_result_package_row_preflight_status", ""),
                row_ready,
                "repair_formal_search_result_package_rows",
                row_preflight.get("preflight_blockers", []),
            ),
            stage(
                "FSR_VALIDATION_EXECUTION",
                validation_execution.get("formal_search_result_validation_execution_status", ""),
                validation_ready,
                "repair_validation_execution_linkage_or_comparison_coverage",
                validation_execution.get("preflight_blockers", []),
            ),
            stage(
                "FSR_NONLEGAL_REVIEW_PACKET",
                nonlegal_review_packet.get(
                    "formal_search_nonlegal_comparison_review_packet_status",
                    "",
                ),
                packet_ready,
                "repair_nonlegal_review_packet_inputs",
                nonlegal_review_packet.get("preflight_blockers", []),
            ),
            stage(
                "FSR_NONLEGAL_REVIEW_RESPONSE",
                nonlegal_response_preflight.get(
                    "formal_search_nonlegal_review_response_source_status",
                    "",
                ),
                nonlegal_response_ready,
                "complete_human_nonlegal_comparison_review_response",
                nonlegal_response_preflight.get("preflight_blockers", []),
            ),
            stage(
                "FSR_CLAIM_SCOPE_PATCH_DRAFT",
                claim_scope_patch_draft.get("formal_search_claim_scope_patch_draft_status", ""),
                claim_scope_ready,
                "repair_claim_scope_patch_draft_inputs",
                claim_scope_patch_draft.get("draft_blockers", []),
            ),
            stage(
                "FSR_FORMAL_COUNSEL_RESPONSE",
                formal_counsel_preflight.get("formal_counsel_review_response_source_status", ""),
                formal_counsel_ready,
                "complete_external_formal_counsel_review_response",
                formal_counsel_preflight.get("preflight_blockers", []),
            ),
            stage(
                "FSR_DISCLOSURE_REVISION_QUEUE",
                disclosure_revision_queue.get("formal_disclosure_revision_queue_status", ""),
                disclosure_queue_ready,
                "repair_formal_disclosure_revision_queue",
                disclosure_revision_queue.get("queue_blockers", []),
            ),
            stage(
                "FSR_DISCLOSURE_REVISION_IMPACT_PLAN",
                disclosure_revision_impact_plan.get(
                    "formal_disclosure_revision_impact_plan_status",
                    "",
                ),
                disclosure_impact_ready,
                "perform_human_disclosure_revision_against_impact_plan",
                disclosure_revision_impact_plan.get("impact_plan_blockers", []),
            ),
        ]
        failed_stages = [row for row in stage_checks if not row["passed"]]

        if not boundary_ok:
            status = "formal_search_review_invalid_boundary_violation"
        elif not source_ready:
            status = "formal_search_review_blocked_at_result_package_source_preflight"
        elif not row_ready:
            status = "formal_search_review_blocked_at_result_package_row_preflight"
        elif not validation_ready:
            status = "formal_search_review_blocked_at_validation_execution"
        elif not packet_ready:
            status = "formal_search_review_blocked_at_nonlegal_review_packet"
        elif not nonlegal_response_ready:
            status = "formal_search_review_ready_for_human_nonlegal_comparison"
        elif not claim_scope_ready:
            status = "formal_search_review_blocked_at_claim_scope_patch_draft"
        elif not formal_counsel_ready:
            status = "formal_search_review_ready_for_external_formal_counsel_review"
        elif not disclosure_queue_ready:
            status = "formal_search_review_blocked_at_disclosure_revision_queue"
        elif not disclosure_impact_ready:
            status = "formal_search_review_blocked_at_disclosure_revision_impact_plan"
        else:
            status = "formal_search_review_ready_for_human_disclosure_revision"

        if status == "formal_search_review_ready_for_human_disclosure_revision":
            next_operator_action = "perform_human_disclosure_revision_against_impact_plan"
            highest_priority_blocker = "NONE"
        else:
            highest = failed_stages[0] if failed_stages else {}
            highest_priority_blocker = str(highest.get("stage_id", "NONE"))
            next_operator_action = str(
                highest.get("next_operator_action", "perform_human_disclosure_revision_against_impact_plan")
            )
            if status == "formal_search_review_ready_for_human_nonlegal_comparison":
                next_operator_action = "complete_human_nonlegal_comparison_review_response"
            elif status == "formal_search_review_ready_for_external_formal_counsel_review":
                next_operator_action = "complete_external_formal_counsel_review_response"

        operator_action_queue = [
            {
                "stage_id": row["stage_id"],
                "next_operator_action": row["next_operator_action"],
                "blockers": row["blockers"],
            }
            for row in failed_stages
        ]
        if status == "formal_search_review_ready_for_human_disclosure_revision":
            operator_action_queue = [
                {
                    "stage_id": "FSR_DISCLOSURE_REVISION_IMPACT_PLAN",
                    "next_operator_action": "perform_human_disclosure_revision_against_impact_plan",
                    "blockers": [],
                }
            ]

        return {
            "gate_id": "R8u78_formal_search_review_readiness_gate",
            "formal_search_review_readiness_status": status,
            "highest_priority_blocker": highest_priority_blocker,
            "blocking_stage_count": len(failed_stages),
            "next_operator_action": next_operator_action,
            "stage_checks": stage_checks,
            "operator_action_queue": operator_action_queue,
            "can_route_to_validation_gate": source_ready and row_ready,
            "can_enter_human_nonlegal_comparison_review": packet_ready,
            "human_nonlegal_review_completed": bool(
                nonlegal_response_preflight.get("human_review_completed", False)
            ),
            "can_route_to_claim_scope_patch_draft": nonlegal_response_ready,
            "can_route_to_formal_counsel_review": claim_scope_ready,
            "external_formal_review_completed": bool(
                formal_counsel_preflight.get("external_formal_review_completed", False)
            ),
            "can_route_to_disclosure_editor": disclosure_queue_ready,
            "can_route_to_human_artifact_revision": disclosure_impact_ready,
            "can_generate_prior_art_result": False,
            "legal_opinion_allowed": False,
            "can_emit_claim_text": False,
            "field_claim_upgrade_allowed": False,
            "boundary_violation_count": len(boundary_violations),
            "boundary_violations": boundary_violations,
            "failure_boundary": (
                "该 gate 只聚合 formal search、人工非法律技术比较、外部正式审查和交底修订的路由状态；"
                "它不执行正式检索、不生成 prior-art 结论、不写法律意见、不生成权利要求文本，"
                "也不能把 synthetic/template/literature 证据升级为 field-supported claim。"
            ),
        }

    @staticmethod
    def _contains_forbidden_formal_counsel_routing_text(value: object) -> bool:
        if isinstance(value, dict):
            return any(
                AgentArchitectureConsolidationAgent._contains_forbidden_formal_counsel_routing_text(child)
                for child in value.values()
            )
        if isinstance(value, list):
            return any(
                AgentArchitectureConsolidationAgent._contains_forbidden_formal_counsel_routing_text(child)
                for child in value
            )
        if isinstance(value, str):
            normalized = value.lower()
            return any(
                term.lower() in normalized
                for term in FORBIDDEN_FORMAL_COUNSEL_ROUTING_TERMS
            )
        return False

    @staticmethod
    def _module_consolidation_policy(module_id: str, retention_counts: Counter[str]) -> str:
        if module_id == "M9_presentation_delivery":
            return "freeze_low_priority_until_model_metrics_change"
        if module_id == "M7_project_operations_support":
            return "compress_to_project_operations_support_facade"
        if module_id in {"M5_kg_claim_evidence", "M6_field_evidence_chain"}:
            return "merge_gate_and_claim_evidence_contracts"
        if any(key.startswith("merge") for key in retention_counts):
            return "merge_subagents_into_module_interface"
        return "keep_as_core_module_with_explicit_io_contract"

    @staticmethod
    def _model_core_contribution(agent_name: str, module_id: str, retention: str) -> str:
        if agent_name in CORE_ANCHOR_AGENTS:
            return "核心锚点：直接影响观测、软传感、协同控制、灰箱、工程约束或 claim evidence。"
        if module_id == "M9_presentation_delivery":
            return "表达层：只在模型指标更新后同步，不作为当前核心优化对象。"
        if retention.startswith("compress"):
            return "项目运行支持：保留结果，但后续通过模块 facade 压缩复杂度。"
        if retention.startswith("merge"):
            return "可合并子能力：应进入模块统一接口，减少重复 gate 和重复文档化输出。"
        if module_id == "UNMAPPED":
            return "未映射：不能进入核心链路，需先确认职责。"
        return "核心或支撑能力：保留，但必须说明输入、输出、消费者和失败边界。"

    @staticmethod
    def _consumer_expectation(agent_name: str) -> str:
        expectations = {
            "sensor_network_sparse_placement_agent": "供 SoftSensorMatrix、CatalystProxy、MultiFacilityControl 消费。",
            "catalyst_activity_proxy_agent": "供 Agent49/52 的弱状态保护、reward prior 和 field_proxy_holdout 设计消费。",
            "soft_sensor_matrix_coupling_agent": "供 SoftSensor 训练 schema、missingness replay 和 Agent49 状态矩阵消费。",
            "multi_facility_collaborative_control_agent": "供 ReplayEvaluation、EngineeringConstraints 和 Arbitration 消费。",
            "multi_facility_replay_evaluation_agent": "供 Governance 排序、Agent49 reward patch 和 field replay 采集设计消费。",
            "minimal_grey_box_physics_agent": "供 SoftSensorMatrix、KG reasoning 和 control reward residual 消费。",
            "engineering_execution_constraint_agent": "供 Agent49 reward、CostSafety 和 Arbitration 消费。",
            "knowledge_graph_reasoning_agent": "供 Mechanism/Control action bias、FieldValidationQueue 和 Governance 消费。",
            "claim_specific_field_package_agent": "供 source_basis 补全和真实 field package 导入优先级消费。",
        }
        return expectations.get(agent_name, "通过所属模块的统一接口被消费；若无消费者，需合并或冻结。")

    @staticmethod
    def _redundancy_clusters(audit_table: list[dict[str, object]]) -> list[dict[str, object]]:
        names_by_decision: dict[str, list[str]] = defaultdict(list)
        for row in audit_table:
            names_by_decision[str(row["retention_decision"])].append(str(row["agent_name"]))
        return [
            {
                "cluster_id": "C1_soft_sensor_validation_cluster",
                "cluster_type": "merge",
                "agents": sorted(names_by_decision.get("merge_into_soft_sensor_validation", [])),
                "why_redundant": "不确定性、保形、弱目标和 field holdout 都在服务同一个 release calibration boundary。",
                "consolidation_target": "M2_soft_sensor_state_estimation + M6_field_evidence_chain shared gate contract",
                "preserve_metrics": [
                    "interval_coverage",
                    "weak_target_coverage",
                    "abstention_rate",
                    "field_holdout_gate_pass",
                ],
                "priority": "high",
            },
            {
                "cluster_id": "C2_field_evidence_claim_gate_cluster",
                "cluster_type": "merge",
                "agents": sorted(
                    names_by_decision.get("merge_into_field_evidence_gate", [])
                    + names_by_decision.get("merge_with_field_evidence_gate", [])
                ),
                "why_redundant": "field calibration、replay gate、claim package 和 source_basis 阻断都在回答同一件事：哪条 claim 能否升级。",
                "consolidation_target": "UnifiedFieldEvidenceGate interface",
                "preserve_metrics": [
                    "field_need_to_gate_coverage",
                    "source_basis_completion_rate",
                    "evidence_chain_pass",
                    "can_write_to_release_gate",
                ],
                "priority": "highest",
            },
            {
                "cluster_id": "C3_project_operations_cluster",
                "cluster_type": "compress",
                "agents": sorted(names_by_decision.get("compress_into_project_ops", [])),
                "why_redundant": "队列、资源、预算、压力测试、在线重规划和恢复爬坡属于同一实施支持层，不应继续占据核心模型链路。",
                "consolidation_target": "ProjectOperationsSupport facade",
                "preserve_metrics": [
                    "campaign_success_rate",
                    "resource_bottleneck_count",
                    "replan_trigger",
                    "recovery_load_fraction",
                ],
                "priority": "medium",
            },
            {
                "cluster_id": "C4_presentation_freeze_cluster",
                "cluster_type": "freeze",
                "agents": sorted(names_by_decision.get("freeze_low_priority", [])),
                "why_redundant": "展示、PPT、Word 和索引不改变模型能力，只有模型指标更新后才同步。",
                "consolidation_target": "FrozenPresentationBacklog",
                "preserve_metrics": ["none_for_model_core"],
                "priority": "low",
            },
            {
                "cluster_id": "C5_kg_literature_reasoning_cluster",
                "cluster_type": "merge",
                "agents": sorted(names_by_decision.get("merge_into_kg_evidence", [])),
                "why_redundant": "KG schema、文献证据和 reasoning patch 应共享同一证据记录格式，避免 source_basis 继续只是方法标签。",
                "consolidation_target": "M5_kg_claim_evidence source-backed evidence store",
                "preserve_metrics": [
                    "evidence_traceability",
                    "constraint_hit_rate",
                    "source_basis_completion_rate",
                    "field_supported_edge_ratio",
                ],
                "priority": "high",
            },
        ]

    @staticmethod
    def _core_consumption_map() -> list[dict[str, object]]:
        return [
            {
                "source_agent": "sensor_network_sparse_placement_agent",
                "consumer_agents": [
                    "soft_sensor_matrix_coupling_agent",
                    "catalyst_activity_proxy_agent",
                    "multi_facility_collaborative_control_agent",
                ],
                "interface": "node_modality observation matrix, selected sensors, missingness contract",
                "status": "consumed_synthetic_prior",
                "field_boundary": "needs field topology and node-specific timeseries",
            },
            {
                "source_agent": "catalyst_activity_proxy_agent",
                "consumer_agents": ["multi_facility_replay_evaluation_agent", "multi_facility_collaborative_control_agent"],
                "interface": "catalyst proxy features, recommended sensor patches, weak-state block boundary",
                "status": "design_prior_only",
                "field_boundary": "needs field_proxy_holdout labels before relaxing catalyst blocks",
            },
            {
                "source_agent": "minimal_grey_box_physics_agent",
                "consumer_agents": ["soft_sensor_matrix_coupling_agent", "main_chain_reconnection_agent"],
                "interface": "grey-box residual prior, mass-balance and byproduct risk flags",
                "status": "consumed_synthetic_prior",
                "field_boundary": "needs field RTD/lab/catalyst/byproduct calibration",
            },
            {
                "source_agent": "soft_sensor_matrix_coupling_agent",
                "consumer_agents": ["multi_facility_collaborative_control_agent", "soft_sensor_agent"],
                "interface": "layout_id, node, modality, availability mask, time-since-last-observed",
                "status": "contract_ready_not_field_validated",
                "field_boundary": "needs field missingness replay and node-specific values",
            },
            {
                "source_agent": "multi_facility_collaborative_control_agent",
                "consumer_agents": ["multi_facility_replay_evaluation_agent", "engineering_execution_constraint_agent"],
                "interface": "facility state/action matrix, joint actions, reward components, distilled rules",
                "status": "replay_ready_synthetic",
                "field_boundary": "needs multi-node state-action-reward replay",
            },
            {
                "source_agent": "engineering_execution_constraint_agent",
                "consumer_agents": ["multi_facility_collaborative_control_agent", "cost_safety_agent", "arbitration_agent"],
                "interface": "reward patch, action constraint patch, arbitration hard blocks",
                "status": "consumed_synthetic_patch",
                "field_boundary": "needs PLC/SCADA points, SOP and execution replay",
            },
            {
                "source_agent": "knowledge_graph_reasoning_agent",
                "consumer_agents": [
                    "mechanism_agent",
                    "control_strategy_agent",
                    "field_validation_queue_alignment_agent",
                ],
                "interface": "evidence paths, action constraints, field_validation_queue",
                "status": "traceable_literature_synthetic_patch",
                "field_boundary": "needs field-supported KG edges and source_basis detail",
            },
            {
                "source_agent": "claim_specific_field_package_agent",
                "consumer_agents": ["model_core_optimization_governance_agent", "future_source_basis_detail_work"],
                "interface": "claim-specific field package, source_basis completion tasks",
                "status": "schema_ready_source_basis_incomplete",
                "field_boundary": "needs citation details or real field package",
            },
        ]

    def _ranked_refactor_actions(self, redundancy_clusters: list[dict[str, object]]) -> list[dict[str, object]]:
        source_basis_rate = self._source_basis_completion_rate()
        citation_detail_rate = self._citation_detail_completion_rate()
        joint_action_accuracy = self._joint_action_accuracy()
        weak_state_coverage = self._weak_state_coverage()
        unified_gate_ready = self._unified_gate_ready()
        observation_contract_ready = self._observation_contract_ready()
        observation_contract_weak = self._observation_contract_weak_state()
        control_replay_stress_ready = self._control_replay_stress_ready()
        guardrail_accuracy = self._control_replay_guardrail_accuracy()
        control_replay_guardrails_integrated = self._control_replay_guardrails_integrated()
        guardrail_aware_replay_ready = self._guardrail_aware_replay_ready()
        guardrail_aware_regret_delta = self._guardrail_aware_regret_delta()
        guardrail_backpropagation_ready = self._guardrail_backpropagation_ready()
        guardrail_backpropagation_mechanism_coverage = self._guardrail_backpropagation_mechanism_coverage()
        guardrail_patch_consumption_ready = self._guardrail_patch_consumption_ready()
        unmet_guardrail_field_count = self._unmet_guardrail_field_count()
        unmet_guardrail_fields = self._unmet_guardrail_fields()
        claim_source_basis_rate = self._claim_specific_source_basis_completion_rate()
        field_package_field_pass_rate = self._minimal_field_package_field_pass_rate()
        r7_acceptance = self._real_field_package_acceptance_readiness()
        r7_pipeline = self._real_field_replay_pipeline_metrics()
        r1_action = {
            "action_id": "R1_unify_field_evidence_and_source_basis_gate",
            "title": "合并 field evidence、claim package 与 source_basis gate",
            "model_core_relevance": 0.92,
            "downstream_chain_impact": 0.88,
            "scientific_value": 0.90,
            "engineering_feasibility": 0.78,
            "verification_readiness": 0.82,
            "trigger_metric": (
                f"source_basis_completion_rate={source_basis_rate:.3f}; "
                f"citation_detail_completion_rate={citation_detail_rate:.3f}"
            ),
            "why_now": "Agent59 已把现场字段矩阵跑通，但 source_basis 仍不完整；继续分散在 Agent34/43/45/58/59 会让证据边界重复。",
            "implementation_path": "先做统一 evidence gate schema，再把 source_basis detail、field package import 和 claim upgrade blocker 归一。",
            "must_not_do": "不能把文献 source_basis 当成 field-supported evidence；不能写 release gate。",
            "expected_metrics": [
                "source_basis_completion_rate",
                "citation_detail_completion_rate",
                "field_claim_upgrade_blocker_count",
                "evidence_chain_pass",
            ],
        }
        if unified_gate_ready and citation_detail_rate < 0.8:
            r1_action.update(
                {
                    "action_id": "R1b_source_basis_detail_completion_inside_unified_gate",
                    "title": "在统一 evidence gate 内补 source_basis 的 citation、参数范围和适用边界",
                    "model_core_relevance": 0.88,
                    "downstream_chain_impact": 0.84,
                    "scientific_value": 0.90,
                    "engineering_feasibility": 0.76,
                    "verification_readiness": 0.78,
                    "trigger_metric": (
                        f"source_basis_completion_rate={source_basis_rate:.3f}; "
                        f"citation_detail_completion_rate={citation_detail_rate:.3f}"
                    ),
                    "why_now": "R1 统一 gate baseline 已形成，但 citation_detail_completion_rate 仍低，claim 仍被文献依据细节阻断。",
                    "implementation_path": "在统一 evidence gate 内补 source_basis detail library，并保持 literature-supported 与 field-supported 的边界。",
                    "must_not_do": "不能把 citation detail 当成 field-supported evidence；不能写 release gate。",
                    "expected_metrics": [
                        "citation_detail_completion_rate",
                        "source_basis_parameter_boundary_coverage",
                        "field_supported_edge_ratio",
                        "can_emit_field_claim_upgrade",
                    ],
                }
            )
        elif unified_gate_ready:
            r1_action.update(
                {
                    "action_id": "R1_unified_gate_baseline_completed",
                    "title": "统一 field evidence gate baseline 已形成",
                    "model_core_relevance": 0.58,
                    "downstream_chain_impact": 0.62,
                    "scientific_value": 0.62,
                    "engineering_feasibility": 0.78,
                    "verification_readiness": 0.72,
                    "why_now": "统一 gate 已形成且 source_basis 细节不再是主阻断，后续应回到观测/控制核心链路。",
                    "implementation_path": "维持接口，不继续堆 field gate；转向 Agent48/51/54 或 Agent49/52。",
                    "must_not_do": "不能把维护接口变成文档整理工作。",
                }
            )
        r2_action = {
                "action_id": "R2_agent48_51_54_observation_contract_merge",
                "title": "合并稀疏布点、催化剂代理与软传感观测矩阵合同",
                "model_core_relevance": 0.90,
                "downstream_chain_impact": 0.86,
                "scientific_value": 0.84,
                "engineering_feasibility": 0.74,
                "verification_readiness": 0.70,
                "trigger_metric": f"weak_state_coverage={weak_state_coverage:.3f}",
                "why_now": "Agent48、51、54 都在定义观测输入，但 catalyst_activity 仍弱，需要统一为一个 layout-aware observation contract。",
                "implementation_path": "把 catalyst proxy recommended patch 回写到 Agent48 candidate scoring，并让 Agent54 直接消费 proxy-enhanced layout。",
                "must_not_do": "不能仅增加传感器数量；必须保留成本约束和 field topology 边界。",
                "expected_metrics": [
                    "weak_state_coverage_after_proxy_design",
                    "layout_contract_score",
                    "missingness_robustness_score",
                    "total_cost_index",
                ],
            }
        if observation_contract_ready:
            r2_action.update(
                {
                    "action_id": "R2_observation_contract_baseline_completed",
                    "title": "Agent48/51/54 观测契约 baseline 已形成",
                    "model_core_relevance": 0.62,
                    "downstream_chain_impact": 0.66,
                    "scientific_value": 0.64,
                    "engineering_feasibility": 0.78,
                    "verification_readiness": 0.74,
                    "trigger_metric": (
                        f"proxy_enhanced_weak_state_coverage={observation_contract_weak:.3f}; "
                        "budget_pass=True"
                    ),
                    "why_now": "R2 已把稀疏布点、催化剂代理观测和软传感矩阵合同合并为预算内 observation contract；下一步应进入控制 replay 压力测试。",
                    "implementation_path": "维护 observation contract 输出，不继续在观测层堆补丁；转向 Agent49/52 replay counterfactual stress。",
                    "must_not_do": "不能把 synthetic observation contract 当作 field deployment 或 release gate。",
                }
            )
        r3_action = {
                "action_id": "R3_agent49_replay_counterfactual_stress",
                "title": "对 Agent49/52 做协同控制 replay 反事实压力测试",
                "model_core_relevance": 0.88,
                "downstream_chain_impact": 0.86,
                "scientific_value": 0.82,
                "engineering_feasibility": 0.72,
                "verification_readiness": 0.68,
                "trigger_metric": f"joint_action_accuracy={joint_action_accuracy:.3f}",
                "why_now": "Agent49 已有多设施结构，但 Agent52 joint_action_accuracy 仍不足，且 protective false positive 需要更细。",
                "implementation_path": "构造 synthetic counterfactual replay stress cases，检查 reward regret、保护性误触发成本和工程硬阻断。",
                "must_not_do": "不能训练黑箱 MARL 或写执行器；先做离线评估和规则蒸馏压力测试。",
                "expected_metrics": [
                    "joint_action_accuracy",
                    "p95_reward_regret",
                    "protective_false_positive_rate",
                    "distilled_policy_accuracy",
                ],
            }
        if guardrail_patch_consumption_ready and unmet_guardrail_field_count == 0:
            r3_action.update(
                {
                    "action_id": "R5_guardrail_schema_extension_baseline_completed",
                    "title": "R5 guardrail field/replay schema baseline 已覆盖",
                    "model_core_relevance": 0.58,
                    "downstream_chain_impact": 0.64,
                    "scientific_value": 0.64,
                    "engineering_feasibility": 0.78,
                    "verification_readiness": 0.80,
                    "trigger_metric": "unmet_guardrail_field_count=0; field_requirement_patch_consumption_rate=1.000",
                    "why_now": "R5 已把 R4b guardrail 必采字段纳入 Agent30/42 schema，继续扩字段的边际价值下降。",
                    "implementation_path": "保留 schema 扩展；下一步补 R4 guardrail source_basis detail 并准备真实 field package 导入验收。",
                    "must_not_do": "不能把 schema ready 当成 field-supported evidence 或控制有效性。",
                    "expected_metrics": [
                        "unmet_guardrail_field_count",
                        "source_basis_completion_rate",
                        "minimal_field_package_field_pass_rate",
                    ],
                }
            )
        elif guardrail_patch_consumption_ready:
            r3_action.update(
                {
                    "action_id": "R4b_patch_consumption_baseline_completed",
                    "title": "R4b patch consumption baseline 已接入 Agent53/58/59",
                    "model_core_relevance": 0.58,
                    "downstream_chain_impact": 0.64,
                    "scientific_value": 0.64,
                    "engineering_feasibility": 0.78,
                    "verification_readiness": 0.78,
                    "trigger_metric": (
                        "agent53_guardrail_boundary_consumption_rate=1.000; "
                        "field_requirement_patch_consumption_rate=1.000"
                    ),
                    "why_now": "R4b 已把控制失败边界消费到灰箱机制、现场验证队列和 claim-specific 采集包，继续停在 patch consumption 层会重复。",
                    "implementation_path": "保留 R4b 输出；下一步把 unmet_guardrail_fields 补入 Agent30/42 的 field/replay schema。",
                    "must_not_do": "不能把 patch consumption 当作 field-supported evidence 或真实现场 replay。",
                    "expected_metrics": [
                        "agent53_guardrail_boundary_consumption_rate",
                        "field_requirement_patch_consumption_rate",
                        "unmet_guardrail_field_count",
                    ],
                }
            )
        elif guardrail_backpropagation_ready:
            r3_action.update(
                {
                    "action_id": "R4_guardrail_backpropagation_baseline_completed",
                    "title": "R4 控制失败到灰箱/现场字段反写 baseline 已形成",
                    "model_core_relevance": 0.58,
                    "downstream_chain_impact": 0.62,
                    "scientific_value": 0.64,
                    "engineering_feasibility": 0.78,
                    "verification_readiness": 0.76,
                    "trigger_metric": (
                        f"backpropagation_ready=True; "
                        f"mechanism_coverage={guardrail_backpropagation_mechanism_coverage:.3f}"
                    ),
                    "why_now": "R4 facade 已完成 resolved cases 到机制边界和现场字段的映射，继续停在同一层会重复。",
                    "implementation_path": "保留 R4 backpropagation 输出；下一步让 Agent53/58/59 消费 patch。",
                    "must_not_do": "不能把 synthetic backpropagation 当作 grey-box field calibration。",
                    "expected_metrics": [
                        "resolved_case_to_mechanism_coverage",
                        "resolved_case_to_field_requirement_coverage",
                        "field_replay_coverage",
                    ],
                }
            )
        elif guardrail_aware_replay_ready:
            r3_action.update(
                {
                    "action_id": "R3_guardrail_replay_baseline_completed",
                    "title": "R3/R3b/R3c 控制 guardrail replay baseline 已形成",
                    "model_core_relevance": 0.60,
                    "downstream_chain_impact": 0.64,
                    "scientific_value": 0.62,
                    "engineering_feasibility": 0.78,
                    "verification_readiness": 0.76,
                    "trigger_metric": (
                        f"guardrail_aware_replay_ready=True; "
                        f"guardrail_aware_regret_delta={guardrail_aware_regret_delta:.3f}"
                    ),
                    "why_now": "R3c 已证明 replay 对照能跑，继续在同一层重复调参的边际价值下降。",
                    "implementation_path": "保留 Agent49/52 guardrail-aware 指标；下一步把 resolved cases 反写灰箱机制和 field replay 必采字段。",
                    "must_not_do": "不能把 synthetic guardrail-aware replay 当作现场控制有效性。",
                    "expected_metrics": [
                        "guardrail_aware_joint_action_accuracy",
                        "guardrail_aware_regret_delta",
                        "field_replay_coverage",
                    ],
                }
            )
        elif control_replay_stress_ready and control_replay_guardrails_integrated:
            r3_action.update(
                {
                    "action_id": "R3c_agent52_guardrail_aware_replay_refresh",
                    "title": "让 Agent52 消费 Agent49 R3b guardrail-aware reward prior 并刷新 replay 指标",
                    "model_core_relevance": 0.84,
                    "downstream_chain_impact": 0.82,
                    "scientific_value": 0.78,
                    "engineering_feasibility": 0.78,
                    "verification_readiness": 0.74,
                    "trigger_metric": f"Agent49 R3b integrated=True; guardrail_candidate_accuracy={guardrail_accuracy:.3f}",
                    "why_now": "R3b 已接入 Agent49 reward prior；下一步应让 Agent52 的 replay evaluator 识别 guardrail-aware policy，验证 regret 和误保护成本是否随之下降。",
                    "implementation_path": "把 Agent49 的 control_replay_guardrail_evaluation 写入 Agent52 replay_table，新增 guardrail-aware action/metric，并保持 field replay blocker。",
                    "must_not_do": "不能因为 synthetic replay 变好就训练在线控制器或写执行器。",
                    "expected_metrics": [
                        "guardrail_aware_joint_action_accuracy",
                        "guardrail_aware_p95_reward_regret",
                        "guardrail_aware_false_positive_action_cost",
                        "field_replay_coverage",
                    ],
                }
            )
        elif control_replay_stress_ready:
            r3_action.update(
                {
                    "action_id": "R3b_agent49_reward_prior_patch_from_counterfactual_stress",
                    "title": "把 R3 反事实压力结果写成 Agent49 reward prior guardrails",
                    "model_core_relevance": 0.86,
                    "downstream_chain_impact": 0.84,
                    "scientific_value": 0.80,
                    "engineering_feasibility": 0.76,
                    "verification_readiness": 0.72,
                    "trigger_metric": f"guardrail_candidate_accuracy={guardrail_accuracy:.3f}; field_replay_coverage=0.000",
                    "why_now": "R3 已用 counterfactual stress 暴露并修正 synthetic 高 regret/误保护场景；下一步应把 guardrail 变成 Agent49 reward prior，而不是停在报告里。",
                    "implementation_path": "把 R3G1/R3G2 接入 Agent49 reward_prior/decision_tree guardrail，并让 Agent52 replay 刷新指标。",
                    "must_not_do": "不能把 synthetic guardrail improvement 当成现场控制有效性，不能写执行器。",
                    "expected_metrics": [
                        "agent49_reward_prior_guardrail_count",
                        "replay_joint_action_accuracy_after_guardrail",
                        "p95_reward_regret_after_guardrail",
                        "can_write_to_actuator",
                    ],
                }
            )
        actions = [
            r1_action,
            r2_action,
            r3_action,
        ]
        if guardrail_backpropagation_ready and not guardrail_patch_consumption_ready:
            actions.append(
                {
                    "action_id": "R4b_patch_agent53_and_field_requirement_interfaces",
                    "title": "让 Agent53、Agent58、Agent59 消费 R4 grey-box/field patches",
                    "model_core_relevance": 0.86,
                    "downstream_chain_impact": 0.84,
                    "scientific_value": 0.82,
                    "engineering_feasibility": 0.78,
                    "verification_readiness": 0.78,
                    "trigger_metric": f"mechanism_coverage={guardrail_backpropagation_mechanism_coverage:.3f}; field_replay_coverage=0.000",
                    "why_now": "R4 已产生机制边界和现场字段 patch，但 Agent53/58/59 还没有把它纳入灰箱审计和 claim-specific 采集包。",
                    "implementation_path": "把 control_guardrail_backpropagation_metrics 接入 Agent53/58/59，输出 patch consumption rate 和未满足字段。",
                    "must_not_do": "不能把 patch consumption 当成 field-supported evidence。",
                    "expected_metrics": [
                        "agent53_guardrail_boundary_consumption_rate",
                        "field_requirement_patch_consumption_rate",
                        "unmet_guardrail_field_count",
                        "field_supported_edge_ratio",
                    ],
                }
            )
        elif guardrail_patch_consumption_ready and unmet_guardrail_field_count > 0:
            actions.append(
                {
                    "action_id": "R5_extend_guardrail_field_and_replay_schema",
                    "title": "把 R4b unmet guardrail fields 补入现场数据接口与 replay schema",
                    "model_core_relevance": 0.89,
                    "downstream_chain_impact": 0.87,
                    "scientific_value": 0.84,
                    "engineering_feasibility": 0.76,
                    "verification_readiness": 0.80,
                    "trigger_metric": (
                        f"unmet_guardrail_field_count={unmet_guardrail_field_count}; "
                        f"unmet_fields={', '.join(unmet_guardrail_fields) or '-'}"
                    ),
                    "why_now": "R4b 已证明控制失败边界能回传到 Agent53/58/59；现在真正阻塞 field replay 的是 guardrail 必采字段仍未进入 Agent30/42 schema。",
                    "implementation_path": "扩展 Agent30/42：FieldDataInterfaceAgent 与 TimestampedCampaignReplayAgent 的 schema，覆盖 proxy_holdout_label、regeneration_event、tank_storage_margin、actuator_latency_p90、pump_valve_result、hold_time_min 等字段，并刷新 Agent58/59 指标。",
                    "must_not_do": "不能因为 schema 扩展完成就声称现场验证完成；schema ready 仍只是 field-validation-required。",
                    "expected_metrics": [
                        "guardrail_missing_schema_field_count_after_extension",
                        "field_requirement_patch_consumption_rate",
                        "field_contract_coverage",
                        "replay_contract_coverage",
                        "can_write_to_release_gate",
                    ],
                }
            )
        elif guardrail_patch_consumption_ready and claim_source_basis_rate < 0.95:
            actions.append(
                {
                    "action_id": "R6_complete_guardrail_source_basis_and_field_package_acceptance",
                    "title": "补齐 R4 guardrail source_basis 并准备真实 field package 导入验收",
                    "model_core_relevance": 0.87,
                    "downstream_chain_impact": 0.84,
                    "scientific_value": 0.88,
                    "engineering_feasibility": 0.74,
                    "verification_readiness": 0.79,
                    "trigger_metric": (
                        f"source_basis_completion_rate={claim_source_basis_rate:.3f}; "
                        f"minimal_field_package_field_pass_rate={field_package_field_pass_rate:.3f}; "
                        "unmet_guardrail_field_count=0"
                    ),
                    "why_now": "R4b/R5 已把控制失败边界接入灰箱、现场字段和 schema；现在阻塞 claim 升级的是 R4 guardrail source_basis 细节缺失和真实 field package 尚未导入。",
                    "implementation_path": "为 R4_control_guardrail_failure_backpropagation 建立 source_basis detail 记录，明确 synthetic replay 来源、适用边界、参数字段和 field acceptance gate；同时刷新 Agent59/统一 evidence gate 的 blocker。",
                    "must_not_do": "不能把 synthetic guardrail source_basis 写成现场实证，不能绕过真实 field import、holdout 或人工复核。",
                    "expected_metrics": [
                        "source_basis_completion_rate",
                        "R4_guardrail_source_basis_present",
                        "field_package_import_ready",
                        "field_supported_edge_ratio",
                        "can_write_to_release_gate",
                    ],
                }
            )
        elif guardrail_patch_consumption_ready:
            actions.append(
                self._r7_real_field_package_action(
                    claim_source_basis_rate=claim_source_basis_rate,
                    field_package_field_pass_rate=field_package_field_pass_rate,
                    r7_acceptance=r7_acceptance,
                    r7_pipeline=r7_pipeline,
                )
            )
        elif guardrail_aware_replay_ready:
            actions.append(
                {
                    "action_id": "R4_backpropagate_guardrail_failures_to_grey_box_and_field_requirements",
                    "title": "把 R3c resolved failure cases 反写到灰箱机制与现场 replay 必采字段",
                    "model_core_relevance": 0.88,
                    "downstream_chain_impact": 0.84,
                    "scientific_value": 0.84,
                    "engineering_feasibility": 0.76,
                    "verification_readiness": 0.78,
                    "trigger_metric": f"guardrail_aware_regret_delta={guardrail_aware_regret_delta:.3f}; field_replay_coverage=0.000",
                    "why_now": "R3c 解决了两个 synthetic 失败案例，但还没有解释这些失败对应的水力延迟、催化剂代理和现场字段缺口；这一步能把控制 guardrail 回接灰箱机制和 field schema。",
                    "implementation_path": "读取 Agent52 guardrail_resolved_cases，生成 mechanism_backpropagation 和 field_requirement_patch，连接 Agent53/58/59。",
                    "must_not_do": "不能新增展示材料或声称现场验证完成；只能强化机制解释和真实采集需求。",
                    "expected_metrics": [
                        "resolved_case_to_mechanism_coverage",
                        "resolved_case_to_field_requirement_coverage",
                        "grey_box_failure_boundary_count",
                        "field_replay_required_field_count",
                    ],
                }
            )
        actions.append(
            {
                "action_id": "R4_freeze_presentation_and_compress_project_ops",
                "title": "冻结展示层并压缩项目运维链",
                "model_core_relevance": 0.54,
                "downstream_chain_impact": 0.60,
                "scientific_value": 0.48,
                "engineering_feasibility": 0.84,
                "verification_readiness": 0.76,
                "trigger_metric": f"redundancy_cluster_count={len(redundancy_clusters)}",
                "why_now": "展示层和项目运维链 agent 数量较多，容易把工作带离模型核心。",
                "implementation_path": "保留输出，但通过 module facade 压缩对主链的暴露面。",
                "must_not_do": "不能把压缩整理变成 PPT/Word 美化工作。",
                "expected_metrics": [
                    "presentation_freeze_agent_count",
                    "project_ops_compression_candidate_count",
                    "self_interrupt_verdict",
                ],
            }
        )
        for action in actions:
            action["marginal_value_score"] = self._score_action(action)
        actions.sort(key=lambda item: (-float(item["marginal_value_score"]), str(item["action_id"])))
        for index, action in enumerate(actions, start=1):
            action["rank"] = index
        return actions

    @staticmethod
    def _score_action(action: dict[str, object]) -> float:
        return round(
            0.23 * float(action["model_core_relevance"])
            + 0.20 * float(action["downstream_chain_impact"])
            + 0.18 * float(action["scientific_value"])
            + 0.16 * float(action["engineering_feasibility"])
            + 0.17 * float(action["verification_readiness"])
            + 0.06 * (0.1 if action["action_id"] == "R4_freeze_presentation_and_compress_project_ops" else 1.0),
            3,
        )

    @staticmethod
    def _core_anchor_coverage(audit_table: list[dict[str, object]]) -> dict[str, object]:
        found = {str(row["agent_name"]) for row in audit_table if row["is_core_anchor"]}
        missing = sorted(CORE_ANCHOR_AGENTS - found)
        return {
            "required_core_anchor_agents": sorted(CORE_ANCHOR_AGENTS),
            "covered_core_anchor_agents": sorted(found),
            "missing_core_anchor_agents": missing,
            "coverage_rate": round(len(found) / max(1, len(CORE_ANCHOR_AGENTS)), 3),
        }

    @staticmethod
    def _consolidation_score(
        *,
        audit_table: list[dict[str, object]],
        module_board: list[dict[str, object]],
        redundancy_clusters: list[dict[str, object]],
        evidence_status: dict[str, object],
        core_anchor_coverage: dict[str, object],
        system_spine_coverage: dict[str, object],
        interface_contract_coverage: dict[str, object],
    ) -> float:
        mapped_rate = len([row for row in audit_table if row["module_id"] != "UNMAPPED"]) / max(1, len(audit_table))
        module_score = min(1.0, len(module_board) / 9)
        cluster_score = min(1.0, len(redundancy_clusters) / 5)
        return round(
            0.24 * mapped_rate
            + 0.16 * float(core_anchor_coverage["coverage_rate"])
            + 0.15 * float(system_spine_coverage["layer_coverage_rate"])
            + 0.11 * float(system_spine_coverage["ability_coverage_rate"])
            + 0.12 * float(interface_contract_coverage["interface_contract_coverage_rate"])
            + 0.10 * module_score
            + 0.06 * cluster_score
            + 0.06 * float(evidence_status["completeness_score"]),
            3,
        )

    @staticmethod
    def _self_interrupt_verdict(audit_table: list[dict[str, object]], next_actions: list[dict[str, object]]) -> str:
        presentation_count = len([row for row in audit_table if row["module_id"] == "M9_presentation_delivery"])
        top_action_id = str(next_actions[0]["action_id"])
        if top_action_id == "R4_freeze_presentation_and_compress_project_ops" and presentation_count > 0:
            return "interrupt_and_refocus"
        return "continue_core_architecture_consolidation"

    def _issues(
        self,
        *,
        unmapped_agents: list[dict[str, object]],
        presentation_agents: list[dict[str, object]],
        evidence_status: dict[str, object],
        core_anchor_coverage: dict[str, object],
        system_spine_coverage: dict[str, object],
        interface_contract_coverage: dict[str, object],
    ) -> list[QualityIssue]:
        issues: list[QualityIssue] = []
        if unmapped_agents:
            issues.append(
                QualityIssue(
                    sensor="agent_architecture",
                    issue_type="unmapped_agent_detected",
                    severity=Severity.WARNING,
                    message=f"{len(unmapped_agents)} 个 agent 未映射到模块，不能进入核心链路结论。",
                    evidence={"unmapped_agents": [row["agent_name"] for row in unmapped_agents]},
                )
            )
        if presentation_agents:
            issues.append(
                QualityIssue(
                    sensor="agent_architecture",
                    issue_type="presentation_agents_frozen",
                    severity=Severity.INFO,
                    message="展示层 agent 已冻结为低优先级，只有模型指标更新后才同步。",
                    evidence={"presentation_agents": [row["agent_name"] for row in presentation_agents]},
                )
            )
        if evidence_status["status"] != "architecture_evidence_complete":
            issues.append(
                QualityIssue(
                    sensor="agent_architecture",
                    issue_type="architecture_evidence_incomplete",
                    severity=Severity.WARNING,
                    message="架构治理外部证据矩阵字段不完整。",
                    evidence=evidence_status,
                )
            )
        if core_anchor_coverage["missing_core_anchor_agents"]:
            issues.append(
                QualityIssue(
                    sensor="agent_architecture",
                    issue_type="core_anchor_mapping_incomplete",
                    severity=Severity.CRITICAL,
                    message="核心锚点 agent 映射不完整，不能安全进入减冗重构。",
                    evidence=core_anchor_coverage,
                )
            )
        if system_spine_coverage["missing_layers"]:
            issues.append(
                QualityIssue(
                    sensor="agent_architecture",
                    issue_type="global_system_spine_layer_gap",
                    severity=Severity.WARNING,
                    message="全局七层系统骨架仍有缺层，局部优化不能替代系统骨架补齐。",
                    evidence=system_spine_coverage,
                )
            )
        if system_spine_coverage["missing_abilities"]:
            issues.append(
                QualityIssue(
                    sensor="agent_architecture",
                    issue_type="global_system_ability_gap",
                    severity=Severity.WARNING,
                    message="全局系统能力覆盖不完整，需要补齐可观测、可控、可解释、可验证、可工程化或可演化中的缺口。",
                    evidence=system_spine_coverage,
                )
            )
        if system_spine_coverage["unmapped_system_layer_module_count"]:
            issues.append(
                QualityIssue(
                    sensor="agent_architecture",
                    issue_type="module_not_mapped_to_global_spine",
                    severity=Severity.WARNING,
                    message="存在模块未映射到全局系统骨架，不能作为长期架构中心。",
                    evidence=system_spine_coverage,
                )
            )
        if interface_contract_coverage["incomplete_module_contracts"]:
            issues.append(
                QualityIssue(
                    sensor="agent_architecture",
                    issue_type="module_interface_contract_incomplete",
                    severity=Severity.WARNING,
                    message="存在模块未完整说明输入、输出、状态变量、证据来源、指标、边界和上下游接口。",
                    evidence=interface_contract_coverage,
                )
            )
        return issues

    @staticmethod
    def _recommendations(
        next_actions: list[dict[str, object]],
        self_interrupt_verdict: str,
        offline_core_fallback: dict[str, object],
    ) -> list[str]:
        top = next_actions[0]
        recommendations = [
            f"自我打断结论：{self_interrupt_verdict}。",
            f"下一步最高边际价值重构：{top['action_id']} - {top['title']}。",
            f"实施边界：{top['must_not_do']}",
            "不要删除历史 agent 文件；先通过模块 facade 和统一接口压缩复杂度，等测试稳定后再物理合并代码。",
        ]
        if offline_core_fallback.get("fallback_enabled"):
            recommendations.insert(
                3,
                "无真实 field package 时的离线核心 fallback："
                f"{offline_core_fallback['action_id']} - {offline_core_fallback['title']}。",
            )
        return recommendations

    def _offline_core_fallback_action(self, next_actions: list[dict[str, object]]) -> dict[str, object]:
        top = next_actions[0] if next_actions else {}
        if not str(top.get("action_id", "")).startswith("R7a"):
            return {
                "fallback_enabled": False,
                "action_id": "none",
                "title": "top-ranked action is actionable without external field package fallback",
                "reason": "当前最高优先级不只是等待真实 field package。",
            }
        r7_readiness = self._real_field_package_acceptance_readiness()
        r7_status = str(
            r7_readiness.get(
                "real_field_package_acceptance_status",
                r7_readiness.get("r7_status", ""),
            )
        )
        if "blocked_at_import" not in r7_status:
            return {
                "fallback_enabled": False,
                "action_id": "none",
                "title": "R7 action has progressed beyond import blocker",
                "reason": f"R7 status is {r7_status}; continue R7-specific patching.",
            }
        ledger = self._agent48_hidden_state_requirement_ledger()
        patch = ledger.get("minimum_cost_requirement_patch", {}) if isinstance(ledger, dict) else {}
        patch = patch if isinstance(patch, dict) else {}
        pressure_pool = ledger.get("pressure_headloss_candidate_pool", {}) if isinstance(ledger, dict) else {}
        pressure_pool = pressure_pool if isinstance(pressure_pool, dict) else {}
        hard_unresolved = [str(item) for item in patch.get("hard_unresolved_hidden_states", [])]
        if hard_unresolved:
            pressure_pool_ready = str(
                pressure_pool.get(
                    "pool_status",
                    patch.get("pressure_headloss_candidate_pool_status", ""),
                )
            ).startswith("pressure_headloss_candidate_pool_ready")
            r2_consumes_pool = self._r2_pressure_headloss_candidate_pool_consumed()
            if pressure_pool_ready and r2_consumes_pool:
                r8c_consumed = self._agent54_49_pressure_headloss_contract_consumed()
                if r8c_consumed:
                    if self._agent52_pressure_headloss_boundary_consumed():
                        if self._r8e_pressure_headloss_field_schema_ready():
                            if self._r8f_pressure_headloss_import_gate_ready():
                                if self._r8g_pressure_headloss_r7_contract_ready():
                                    if self._r8h_agent44_pressure_headloss_preflight_diagnostics_ready():
                                        if self._r8i_agent51_pressure_headloss_event_log_ready():
                                            if self._r8j_pressure_source_propagated_to_control_replay():
                                                if self._r8k_pressure_source_conflict_boundary_ready():
                                                    if self._r8l_pressure_conflict_control_replay_ready():
                                                        if self._r8m_pressure_conflict_field_patch_ready():
                                                            if self._r8n_pressure_resolution_replay_clearance_ready():
                                                                if self._r8o_pressure_resolution_scenario_pack_ready():
                                                                    if self._r8p_pressure_resolution_rows_accepted():
                                                                        downstream_route_handoff = (
                                                                            self._r8v_pressure_resolution_downstream_route_handoff()
                                                                        )
                                                                        downstream_route_handoff_status = str(
                                                                            downstream_route_handoff.get(
                                                                                "downstream_route_handoff_status",
                                                                                "",
                                                                            )
                                                                        )
                                                                        downstream_handoff_target_count = int(
                                                                            downstream_route_handoff.get(
                                                                                "handoff_target_count",
                                                                                0,
                                                                            )
                                                                            or 0
                                                                        )
                                                                        downstream_ready_handoff_target_count = int(
                                                                            downstream_route_handoff.get(
                                                                                "ready_handoff_target_count",
                                                                                0,
                                                                            )
                                                                            or 0
                                                                        )
                                                                        downstream_blocked_handoff_target_count = int(
                                                                            downstream_route_handoff.get(
                                                                                "blocked_handoff_target_count",
                                                                                0,
                                                                            )
                                                                            or 0
                                                                        )
                                                                        downstream_target_gate_preflight = (
                                                                            self._r8v_pressure_resolution_downstream_target_gate_preflight()
                                                                        )
                                                                        downstream_target_gate_preflight_status = str(
                                                                            downstream_target_gate_preflight.get(
                                                                                "downstream_target_gate_preflight_status",
                                                                                "",
                                                                            )
                                                                        )
                                                                        downstream_target_gate_count = int(
                                                                            downstream_target_gate_preflight.get(
                                                                                "target_gate_count",
                                                                                0,
                                                                            )
                                                                            or 0
                                                                        )
                                                                        downstream_ready_target_gate_count = int(
                                                                            downstream_target_gate_preflight.get(
                                                                                "ready_target_gate_count",
                                                                                0,
                                                                            )
                                                                            or 0
                                                                        )
                                                                        downstream_blocked_target_gate_count = int(
                                                                            downstream_target_gate_preflight.get(
                                                                                "blocked_target_gate_count",
                                                                                0,
                                                                            )
                                                                            or 0
                                                                        )
                                                                        downstream_target_gate_next_operator_action = str(
                                                                            downstream_target_gate_preflight.get(
                                                                                "next_operator_action",
                                                                                "",
                                                                            )
                                                                        )
                                                                        downstream_target_gate_result_preflight = (
                                                                            self._r8v_pressure_resolution_downstream_target_gate_result_preflight()
                                                                        )
                                                                        downstream_target_gate_result_preflight_status = str(
                                                                            downstream_target_gate_result_preflight.get(
                                                                                "downstream_target_gate_result_preflight_status",
                                                                                "",
                                                                            )
                                                                        )
                                                                        downstream_target_gate_result_submitted_count = int(
                                                                            downstream_target_gate_result_preflight.get(
                                                                                "submitted_target_result_count",
                                                                                0,
                                                                            )
                                                                            or 0
                                                                        )
                                                                        downstream_target_gate_result_accepted_count = int(
                                                                            downstream_target_gate_result_preflight.get(
                                                                                "accepted_target_result_count",
                                                                                0,
                                                                            )
                                                                            or 0
                                                                        )
                                                                        downstream_target_gate_result_rejected_count = int(
                                                                            downstream_target_gate_result_preflight.get(
                                                                                "rejected_target_result_count",
                                                                                0,
                                                                            )
                                                                            or 0
                                                                        )
                                                                        downstream_target_gate_result_next_operator_action = str(
                                                                            downstream_target_gate_result_preflight.get(
                                                                                "next_operator_action",
                                                                                "",
                                                                            )
                                                                        )
                                                                        downstream_target_gate_result_arbitration = (
                                                                            self._r8v_pressure_resolution_downstream_target_gate_result_arbitration()
                                                                        )
                                                                        downstream_target_gate_result_arbitration_status = str(
                                                                            downstream_target_gate_result_arbitration.get(
                                                                                "downstream_target_gate_result_arbitration_status",
                                                                                "",
                                                                            )
                                                                        )
                                                                        downstream_target_gate_result_arbitration_next_operator_action = str(
                                                                            downstream_target_gate_result_arbitration.get(
                                                                                "next_operator_action",
                                                                                "",
                                                                            )
                                                                        )
                                                                        downstream_target_gate_result_can_route_to_operator_review = bool(
                                                                            downstream_target_gate_result_arbitration.get(
                                                                                "can_route_to_operator_review",
                                                                                False,
                                                                            )
                                                                        )
                                                                        downstream_target_gate_result_can_emit_protective_control_candidate = bool(
                                                                            downstream_target_gate_result_arbitration.get(
                                                                                "can_emit_protective_control_candidate",
                                                                                False,
                                                                            )
                                                                        )
                                                                        downstream_target_gate_operator_review = (
                                                                            self._r8v_pressure_resolution_downstream_target_gate_operator_review_preflight()
                                                                        )
                                                                        downstream_target_gate_operator_review_status = str(
                                                                            downstream_target_gate_operator_review.get(
                                                                                "downstream_target_gate_operator_review_preflight_status",
                                                                                "",
                                                                            )
                                                                        )
                                                                        downstream_target_gate_operator_review_approved_count = int(
                                                                            downstream_target_gate_operator_review.get(
                                                                                "approved_operator_review_count",
                                                                                0,
                                                                            )
                                                                            or 0
                                                                        )
                                                                        downstream_target_gate_operator_review_rejected_count = int(
                                                                            downstream_target_gate_operator_review.get(
                                                                                "rejected_operator_review_count",
                                                                                0,
                                                                            )
                                                                            or 0
                                                                        )
                                                                        downstream_target_gate_operator_review_hold_count = int(
                                                                            downstream_target_gate_operator_review.get(
                                                                                "hold_operator_review_count",
                                                                                0,
                                                                            )
                                                                            or 0
                                                                        )
                                                                        downstream_target_gate_operator_review_next_operator_action = str(
                                                                            downstream_target_gate_operator_review.get(
                                                                                "next_operator_action",
                                                                                "",
                                                                            )
                                                                        )
                                                                        downstream_target_gate_operator_review_can_route_to_post_review_gate = bool(
                                                                            downstream_target_gate_operator_review.get(
                                                                                "can_route_to_post_review_gate",
                                                                                False,
                                                                            )
                                                                        )
                                                                        downstream_target_gate_operator_review_can_emit_protective_control_candidate = bool(
                                                                            downstream_target_gate_operator_review.get(
                                                                                "can_emit_protective_control_candidate",
                                                                                False,
                                                                            )
                                                                        )
                                                                        downstream_target_gate_post_review = (
                                                                            self._r8v_pressure_resolution_downstream_target_gate_post_review_gate()
                                                                        )
                                                                        downstream_target_gate_post_review_status = str(
                                                                            downstream_target_gate_post_review.get(
                                                                                "downstream_target_gate_post_review_gate_status",
                                                                                "",
                                                                            )
                                                                        )
                                                                        downstream_target_gate_post_review_next_operator_action = str(
                                                                            downstream_target_gate_post_review.get(
                                                                                "next_operator_action",
                                                                                "",
                                                                            )
                                                                        )
                                                                        downstream_target_gate_post_review_can_route_to_protective_candidate = bool(
                                                                            downstream_target_gate_post_review.get(
                                                                                "can_route_to_protective_candidate_evaluation",
                                                                                False,
                                                                            )
                                                                        )
                                                                        downstream_target_gate_post_review_can_emit_protective_control_candidate = bool(
                                                                            downstream_target_gate_post_review.get(
                                                                                "can_emit_protective_control_candidate",
                                                                                False,
                                                                            )
                                                                        )
                                                                        downstream_target_gate_protective_candidate_evaluation = (
                                                                            self._r8v_pressure_resolution_downstream_target_gate_protective_candidate_evaluation()
                                                                        )
                                                                        downstream_target_gate_protective_candidate_evaluation_status = str(
                                                                            downstream_target_gate_protective_candidate_evaluation.get(
                                                                                "downstream_target_gate_protective_candidate_evaluation_status",
                                                                                "",
                                                                            )
                                                                        )
                                                                        downstream_target_gate_protective_candidate_evaluation_next_operator_action = str(
                                                                            downstream_target_gate_protective_candidate_evaluation.get(
                                                                                "next_operator_action",
                                                                                "",
                                                                            )
                                                                        )
                                                                        downstream_target_gate_protective_candidate_can_emit = bool(
                                                                            downstream_target_gate_protective_candidate_evaluation.get(
                                                                                "can_emit_protective_control_candidate",
                                                                                False,
                                                                            )
                                                                        )
                                                                        downstream_target_gate_protective_candidate_can_route_to_final_execution_review = bool(
                                                                            downstream_target_gate_protective_candidate_evaluation.get(
                                                                                "can_route_to_final_execution_review",
                                                                                False,
                                                                            )
                                                                        )
                                                                        return {
                                                                            "fallback_enabled": True,
                                                                            "action_id": (
                                                                                "R8v_route_pressure_resolution_rows_to_field_replay_and_holdout_gates"
                                                                            ),
                                                                            "title": (
                                                                                "把 pressure resolution 真实行送入 Agent51/49/52/R7 验证链"
                                                                            ),
                                                                            "reason": (
                                                                                "R8p 已验收 unresolved/resolved pressure conflict 的真实行包；"
                                                                                "下一步最高边际价值不是继续采集模板，而是让这些行进入 "
                                                                                "Agent51 catalyst proxy holdout、Agent49 控制保护上下文、"
                                                                                "Agent52 replay clearance 和 R7 evidence chain，检查解除门是否能被现场链路消费。"
                                                                            ),
                                                                            "trigger_metric": (
                                                                                "field_scenario_coverage=1.000; "
                                                                                "field_row_acceptance_status=field_replay_rows_accepted_for_all_scenarios; "
                                                                                "downstream_routing_preflight_status="
                                                                                "downstream_routing_preflight_passed_ready_for_r8v_field_replay_and_holdout_gates; "
                                                                                "downstream_route_handoff_status="
                                                                                f"{downstream_route_handoff_status or 'not_available'}; "
                                                                                "downstream_ready_handoff_target_count="
                                                                                f"{downstream_ready_handoff_target_count}; "
                                                                                "downstream_blocked_handoff_target_count="
                                                                                f"{downstream_blocked_handoff_target_count}; "
                                                                                "downstream_target_gate_preflight_status="
                                                                                f"{downstream_target_gate_preflight_status or 'not_available'}; "
                                                                                "downstream_ready_target_gate_count="
                                                                                f"{downstream_ready_target_gate_count}; "
                                                                                "downstream_blocked_target_gate_count="
                                                                                f"{downstream_blocked_target_gate_count}; "
                                                                                "downstream_target_gate_next_operator_action="
                                                                                f"{downstream_target_gate_next_operator_action or 'not_available'}; "
                                                                                "downstream_target_gate_result_preflight_status="
                                                                                f"{downstream_target_gate_result_preflight_status or 'not_available'}; "
                                                                                "downstream_target_gate_result_submitted_count="
                                                                                f"{downstream_target_gate_result_submitted_count}; "
                                                                                "downstream_target_gate_result_accepted_count="
                                                                                f"{downstream_target_gate_result_accepted_count}; "
                                                                                "downstream_target_gate_result_rejected_count="
                                                                                f"{downstream_target_gate_result_rejected_count}; "
                                                                                "downstream_target_gate_result_next_operator_action="
                                                                                f"{downstream_target_gate_result_next_operator_action or 'not_available'}; "
                                                                                "downstream_target_gate_result_arbitration_status="
                                                                                f"{downstream_target_gate_result_arbitration_status or 'not_available'}; "
                                                                                "downstream_target_gate_result_arbitration_next_operator_action="
                                                                                f"{downstream_target_gate_result_arbitration_next_operator_action or 'not_available'}; "
                                                                                "downstream_target_gate_result_can_route_to_operator_review="
                                                                                f"{downstream_target_gate_result_can_route_to_operator_review}; "
                                                                                "downstream_target_gate_result_can_emit_protective_control_candidate="
                                                                                f"{downstream_target_gate_result_can_emit_protective_control_candidate}; "
                                                                                "downstream_target_gate_operator_review_preflight_status="
                                                                                f"{downstream_target_gate_operator_review_status or 'not_available'}; "
                                                                                "downstream_target_gate_operator_review_approved_count="
                                                                                f"{downstream_target_gate_operator_review_approved_count}; "
                                                                                "downstream_target_gate_operator_review_rejected_count="
                                                                                f"{downstream_target_gate_operator_review_rejected_count}; "
                                                                                "downstream_target_gate_operator_review_hold_count="
                                                                                f"{downstream_target_gate_operator_review_hold_count}; "
                                                                                "downstream_target_gate_operator_review_next_operator_action="
                                                                                f"{downstream_target_gate_operator_review_next_operator_action or 'not_available'}; "
                                                                                "downstream_target_gate_operator_review_can_route_to_post_review_gate="
                                                                                f"{downstream_target_gate_operator_review_can_route_to_post_review_gate}; "
                                                                                "downstream_target_gate_operator_review_can_emit_protective_control_candidate="
                                                                                f"{downstream_target_gate_operator_review_can_emit_protective_control_candidate}; "
                                                                                "downstream_target_gate_post_review_gate_status="
                                                                                f"{downstream_target_gate_post_review_status or 'not_available'}; "
                                                                                "downstream_target_gate_post_review_next_operator_action="
                                                                                f"{downstream_target_gate_post_review_next_operator_action or 'not_available'}; "
                                                                                "downstream_target_gate_post_review_can_route_to_protective_candidate="
                                                                                f"{downstream_target_gate_post_review_can_route_to_protective_candidate}; "
                                                                                "downstream_target_gate_post_review_can_emit_protective_control_candidate="
                                                                                f"{downstream_target_gate_post_review_can_emit_protective_control_candidate}; "
                                                                                "downstream_target_gate_protective_candidate_evaluation_status="
                                                                                f"{downstream_target_gate_protective_candidate_evaluation_status or 'not_available'}; "
                                                                                "downstream_target_gate_protective_candidate_next_operator_action="
                                                                                f"{downstream_target_gate_protective_candidate_evaluation_next_operator_action or 'not_available'}; "
                                                                                "downstream_target_gate_protective_candidate_can_emit="
                                                                                f"{downstream_target_gate_protective_candidate_can_emit}; "
                                                                                "downstream_target_gate_protective_candidate_can_route_to_final_execution_review="
                                                                                f"{downstream_target_gate_protective_candidate_can_route_to_final_execution_review}"
                                                                            ),
                                                                            "must_not_do": (
                                                                                "不能因为 R8p 行级验收通过就写 actuator 或 release gate；"
                                                                                "必须先经过 Agent51/49/52/R7 的 field replay、holdout、claim gate 和人工复核。"
                                                                            ),
                                                                            "expected_metrics": [
                                                                                "field_rows_downstream_routing_preflight_status",
                                                                                "field_rows_routing_ready_target_count",
                                                                                "field_rows_downstream_routing_target_count",
                                                                                "field_rows_downstream_route_handoff_status",
                                                                                "field_rows_downstream_ready_handoff_target_count",
                                                                                "field_rows_downstream_blocked_handoff_target_count",
                                                                                "field_rows_downstream_target_gate_preflight_status",
                                                                                "field_rows_downstream_ready_target_gate_count",
                                                                                "field_rows_downstream_blocked_target_gate_count",
                                                                                "field_rows_downstream_target_gate_preflight_next_operator_action",
                                                                                "field_rows_downstream_target_gate_result_preflight_status",
                                                                                "field_rows_downstream_target_gate_result_submitted_count",
                                                                                "field_rows_downstream_target_gate_result_accepted_count",
                                                                                "field_rows_downstream_target_gate_result_rejected_count",
                                                                                "field_rows_downstream_target_gate_result_next_operator_action",
                                                                                "field_rows_downstream_target_gate_result_arbitration_status",
                                                                                "field_rows_downstream_target_gate_result_arbitration_next_operator_action",
                                                                                "field_rows_downstream_target_gate_result_can_route_to_operator_review",
                                                                                "field_rows_downstream_target_gate_result_can_emit_protective_control_candidate",
                                                                                "field_rows_downstream_target_gate_operator_review_preflight_status",
                                                                                "field_rows_downstream_target_gate_operator_review_approved_count",
                                                                                "field_rows_downstream_target_gate_operator_review_rejected_count",
                                                                                "field_rows_downstream_target_gate_operator_review_hold_count",
                                                                                "field_rows_downstream_target_gate_operator_review_next_operator_action",
                                                                                "field_rows_downstream_target_gate_operator_review_can_route_to_post_review_gate",
                                                                                "field_rows_downstream_target_gate_operator_review_can_emit_protective_control_candidate",
                                                                                "field_rows_downstream_target_gate_post_review_gate_status",
                                                                                "field_rows_downstream_target_gate_post_review_next_operator_action",
                                                                                "field_rows_downstream_target_gate_post_review_can_route_to_protective_candidate",
                                                                                "field_rows_downstream_target_gate_post_review_can_emit_protective_control_candidate",
                                                                                "field_rows_downstream_target_gate_protective_candidate_evaluation_status",
                                                                                "field_rows_downstream_target_gate_protective_candidate_next_operator_action",
                                                                                "field_rows_downstream_target_gate_protective_candidate_can_emit",
                                                                                "field_rows_downstream_target_gate_protective_candidate_can_route_to_final_execution_review",
                                                                                "agent51_scoreable_batch_count_after_resolution",
                                                                                "agent49_pressure_conflict_guardrail_clear",
                                                                                "agent52_pressure_source_conflict_clear",
                                                                                "field_replay_evidence_chain_pass",
                                                                                "human_review_gate_pass",
                                                                                "can_write_to_actuator",
                                                                                "can_write_to_release_gate",
                                                                            ],
                                                                            "field_rows_downstream_route_handoff_status": (
                                                                                downstream_route_handoff_status
                                                                            ),
                                                                            "downstream_handoff_target_count": (
                                                                                downstream_handoff_target_count
                                                                            ),
                                                                            "downstream_ready_handoff_target_count": (
                                                                                downstream_ready_handoff_target_count
                                                                            ),
                                                                            "downstream_blocked_handoff_target_count": (
                                                                                downstream_blocked_handoff_target_count
                                                                            ),
                                                                            "downstream_route_handoff_summary": (
                                                                                downstream_route_handoff
                                                                            ),
                                                                            "field_rows_downstream_target_gate_preflight_status": (
                                                                                downstream_target_gate_preflight_status
                                                                            ),
                                                                            "downstream_target_gate_count": (
                                                                                downstream_target_gate_count
                                                                            ),
                                                                            "downstream_ready_target_gate_count": (
                                                                                downstream_ready_target_gate_count
                                                                            ),
                                                                            "downstream_blocked_target_gate_count": (
                                                                                downstream_blocked_target_gate_count
                                                                            ),
                                                                            "downstream_target_gate_preflight_next_operator_action": (
                                                                                downstream_target_gate_next_operator_action
                                                                            ),
                                                                            "downstream_target_gate_preflight_summary": (
                                                                                downstream_target_gate_preflight
                                                                            ),
                                                                            "field_rows_downstream_target_gate_result_preflight_status": (
                                                                                downstream_target_gate_result_preflight_status
                                                                            ),
                                                                            "downstream_target_gate_result_submitted_count": (
                                                                                downstream_target_gate_result_submitted_count
                                                                            ),
                                                                            "downstream_target_gate_result_accepted_count": (
                                                                                downstream_target_gate_result_accepted_count
                                                                            ),
                                                                            "downstream_target_gate_result_rejected_count": (
                                                                                downstream_target_gate_result_rejected_count
                                                                            ),
                                                                            "downstream_target_gate_result_next_operator_action": (
                                                                                downstream_target_gate_result_next_operator_action
                                                                            ),
                                                                            "downstream_target_gate_result_preflight_summary": (
                                                                                downstream_target_gate_result_preflight
                                                                            ),
                                                                            "field_rows_downstream_target_gate_result_arbitration_status": (
                                                                                downstream_target_gate_result_arbitration_status
                                                                            ),
                                                                            "downstream_target_gate_result_arbitration_next_operator_action": (
                                                                                downstream_target_gate_result_arbitration_next_operator_action
                                                                            ),
                                                                            "downstream_target_gate_result_can_route_to_operator_review": (
                                                                                downstream_target_gate_result_can_route_to_operator_review
                                                                            ),
                                                                            "downstream_target_gate_result_can_emit_protective_control_candidate": (
                                                                                downstream_target_gate_result_can_emit_protective_control_candidate
                                                                            ),
                                                                            "downstream_target_gate_result_arbitration_summary": (
                                                                                downstream_target_gate_result_arbitration
                                                                            ),
                                                                            "field_rows_downstream_target_gate_operator_review_preflight_status": (
                                                                                downstream_target_gate_operator_review_status
                                                                            ),
                                                                            "downstream_target_gate_operator_review_approved_count": (
                                                                                downstream_target_gate_operator_review_approved_count
                                                                            ),
                                                                            "downstream_target_gate_operator_review_rejected_count": (
                                                                                downstream_target_gate_operator_review_rejected_count
                                                                            ),
                                                                            "downstream_target_gate_operator_review_hold_count": (
                                                                                downstream_target_gate_operator_review_hold_count
                                                                            ),
                                                                            "downstream_target_gate_operator_review_next_operator_action": (
                                                                                downstream_target_gate_operator_review_next_operator_action
                                                                            ),
                                                                            "downstream_target_gate_operator_review_can_route_to_post_review_gate": (
                                                                                downstream_target_gate_operator_review_can_route_to_post_review_gate
                                                                            ),
                                                                            "downstream_target_gate_operator_review_can_emit_protective_control_candidate": (
                                                                                downstream_target_gate_operator_review_can_emit_protective_control_candidate
                                                                            ),
                                                                            "downstream_target_gate_operator_review_summary": (
                                                                                downstream_target_gate_operator_review
                                                                            ),
                                                                            "field_rows_downstream_target_gate_post_review_gate_status": (
                                                                                downstream_target_gate_post_review_status
                                                                            ),
                                                                            "downstream_target_gate_post_review_next_operator_action": (
                                                                                downstream_target_gate_post_review_next_operator_action
                                                                            ),
                                                                            "downstream_target_gate_post_review_can_route_to_protective_candidate": (
                                                                                downstream_target_gate_post_review_can_route_to_protective_candidate
                                                                            ),
                                                                            "downstream_target_gate_post_review_can_emit_protective_control_candidate": (
                                                                                downstream_target_gate_post_review_can_emit_protective_control_candidate
                                                                            ),
                                                                            "downstream_target_gate_post_review_summary": (
                                                                                downstream_target_gate_post_review
                                                                            ),
                                                                            "field_rows_downstream_target_gate_protective_candidate_evaluation_status": (
                                                                                downstream_target_gate_protective_candidate_evaluation_status
                                                                            ),
                                                                            "downstream_target_gate_protective_candidate_next_operator_action": (
                                                                                downstream_target_gate_protective_candidate_evaluation_next_operator_action
                                                                            ),
                                                                            "downstream_target_gate_protective_candidate_can_emit": (
                                                                                downstream_target_gate_protective_candidate_can_emit
                                                                            ),
                                                                            "downstream_target_gate_protective_candidate_can_route_to_final_execution_review": (
                                                                                downstream_target_gate_protective_candidate_can_route_to_final_execution_review
                                                                            ),
                                                                            "downstream_target_gate_protective_candidate_summary": (
                                                                                downstream_target_gate_protective_candidate_evaluation
                                                                            ),
                                                                        }
                                                                    patch_plan = self._r8p_pressure_resolution_patch_plan()
                                                                    if patch_plan:
                                                                        operator_handoff = (
                                                                            self._r8p_pressure_resolution_operator_handoff()
                                                                        )
                                                                        patch_status = str(
                                                                            patch_plan.get("field_rows_patch_plan_status", "")
                                                                        )
                                                                        if patch_status and not patch_status.startswith(
                                                                            "field_rows_patch_plan_clear"
                                                                        ):
                                                                            highest_patch = str(
                                                                                patch_plan.get("highest_priority_patch_id", "unknown")
                                                                            )
                                                                            next_patch_action = str(
                                                                                patch_plan.get(
                                                                                    "next_operator_action",
                                                                                    "R8p_collect_pressure_resolution_replay_rows",
                                                                                )
                                                                            )
                                                                            patch_item_count = int(
                                                                                patch_plan.get("patch_item_count", 0) or 0
                                                                            )
                                                                            handoff_status = str(
                                                                                operator_handoff.get(
                                                                                    "field_rows_operator_handoff_status",
                                                                                    "",
                                                                                )
                                                                            )
                                                                            schema_status = str(
                                                                                operator_handoff.get(
                                                                                    "field_rows_package_schema_status",
                                                                                    "",
                                                                                )
                                                                            )
                                                                            schema_validation_status = str(
                                                                                operator_handoff.get(
                                                                                    "field_rows_schema_validation_status",
                                                                                    "",
                                                                                )
                                                                            )
                                                                            schema_validation_summary = operator_handoff.get(
                                                                                "schema_validation_summary",
                                                                                {},
                                                                            )
                                                                            collection_checklist_status = str(
                                                                                operator_handoff.get(
                                                                                    "field_rows_collection_checklist_status",
                                                                                    "",
                                                                                )
                                                                            )
                                                                            batch_bundle_preflight_status = str(
                                                                                operator_handoff.get(
                                                                                    "field_rows_batch_bundle_preflight_status",
                                                                                    "",
                                                                                )
                                                                            )
                                                                            batch_bundle_preflight_summary = operator_handoff.get(
                                                                                "batch_bundle_preflight_summary",
                                                                                {},
                                                                            )
                                                                            temporal_window_preflight_status = str(
                                                                                operator_handoff.get(
                                                                                    "field_rows_temporal_window_preflight_status",
                                                                                    "",
                                                                                )
                                                                            )
                                                                            temporal_window_preflight_summary = operator_handoff.get(
                                                                                "temporal_window_preflight_summary",
                                                                                {},
                                                                            )
                                                                            scenario_semantic_preflight_status = str(
                                                                                operator_handoff.get(
                                                                                    "field_rows_scenario_semantic_preflight_status",
                                                                                    "",
                                                                                )
                                                                            )
                                                                            scenario_semantic_preflight_summary = operator_handoff.get(
                                                                                "scenario_semantic_preflight_summary",
                                                                                {},
                                                                            )
                                                                            downstream_routing_preflight_status = str(
                                                                                operator_handoff.get(
                                                                                    "field_rows_downstream_routing_preflight_status",
                                                                                    "",
                                                                                )
                                                                            )
                                                                            downstream_routing_preflight_summary = operator_handoff.get(
                                                                                "downstream_routing_preflight_summary",
                                                                                {},
                                                                            )
                                                                            provenance_gate_status = str(
                                                                                operator_handoff.get(
                                                                                    "field_rows_provenance_gate_status",
                                                                                    "",
                                                                                )
                                                                            )
                                                                            all_tables_require_data_origin = bool(
                                                                                operator_handoff.get(
                                                                                    "field_rows_all_tables_require_data_origin",
                                                                                    False,
                                                                                )
                                                                            )
                                                                            provenance_required_table_count = int(
                                                                                operator_handoff.get(
                                                                                    "field_rows_provenance_required_table_count",
                                                                                    0,
                                                                                )
                                                                                or 0
                                                                            )
                                                                            r7_completion_plan = (
                                                                                self._r8p_pressure_resolution_r7_completion_plan()
                                                                            )
                                                                            r7_completion_plan_status = str(
                                                                                r7_completion_plan.get(
                                                                                    "completion_plan_status",
                                                                                    "",
                                                                                )
                                                                            )
                                                                            r7_completion_item_count = int(
                                                                                r7_completion_plan.get("item_count", 0) or 0
                                                                            )
                                                                            r7_completion_item_class_counts = (
                                                                                r7_completion_plan.get("item_class_counts", {})
                                                                            )
                                                                            if not isinstance(
                                                                                r7_completion_item_class_counts,
                                                                                dict,
                                                                            ):
                                                                                r7_completion_item_class_counts = {}
                                                                            r7_completion_field_gap_count_by_class = (
                                                                                r7_completion_plan.get(
                                                                                    "field_gap_count_by_class",
                                                                                    {},
                                                                                )
                                                                            )
                                                                            if not isinstance(
                                                                                r7_completion_field_gap_count_by_class,
                                                                                dict,
                                                                            ):
                                                                                r7_completion_field_gap_count_by_class = {}
                                                                            r7_completion_plan_path = str(
                                                                                r7_completion_plan.get(
                                                                                    "completion_plan_path",
                                                                                    "",
                                                                                )
                                                                            )
                                                                            r7_completion_required_execution_order = [
                                                                                str(item)
                                                                                for item in r7_completion_plan.get(
                                                                                    "required_execution_order",
                                                                                    [],
                                                                                )
                                                                            ]
                                                                            r7_completion_route_contracts = (
                                                                                self._r8p_pressure_resolution_r7_completion_route_contracts()
                                                                            )
                                                                            r7_completion_route_contracts_status = str(
                                                                                r7_completion_route_contracts.get(
                                                                                    "completion_route_contracts_status",
                                                                                    "",
                                                                                )
                                                                            )
                                                                            r7_completion_route_contract_count = int(
                                                                                r7_completion_route_contracts.get(
                                                                                    "route_contract_count",
                                                                                    0,
                                                                                )
                                                                                or 0
                                                                            )
                                                                            r7_completion_open_route_count = int(
                                                                                r7_completion_route_contracts.get("open_route_count", 0) or 0
                                                                            )
                                                                            r7_completion_open_route_ids = [
                                                                                str(item)
                                                                                for item in r7_completion_route_contracts.get(
                                                                                    "open_route_ids",
                                                                                    [],
                                                                                )
                                                                            ]
                                                                            r7_completion_route_contracts_path = str(
                                                                                r7_completion_route_contracts.get(
                                                                                    "completion_route_contracts_path",
                                                                                    "",
                                                                                )
                                                                            )
                                                                            r7_completion_route_work_packages = (
                                                                                self._r8p_pressure_resolution_r7_completion_route_work_packages()
                                                                            )
                                                                            r7_completion_route_work_packages_status = str(
                                                                                r7_completion_route_work_packages.get(
                                                                                    "route_work_packages_status",
                                                                                    "",
                                                                                )
                                                                            )
                                                                            r7_completion_route_work_package_count = int(
                                                                                r7_completion_route_work_packages.get(
                                                                                    "work_package_count",
                                                                                    0,
                                                                                )
                                                                                or 0
                                                                            )
                                                                            r7_completion_open_work_package_count = int(
                                                                                r7_completion_route_work_packages.get(
                                                                                    "open_work_package_count",
                                                                                    0,
                                                                                )
                                                                                or 0
                                                                            )
                                                                            r7_completion_open_work_package_ids = [
                                                                                str(item)
                                                                                for item in r7_completion_route_work_packages.get(
                                                                                    "open_work_package_ids",
                                                                                    [],
                                                                                )
                                                                            ]
                                                                            r7_completion_route_work_packages_path = str(
                                                                                r7_completion_route_work_packages.get(
                                                                                    "route_work_packages_path",
                                                                                    "",
                                                                                )
                                                                            )
                                                                            r7_completion_route_work_package_preflight = (
                                                                                self._r8p_pressure_resolution_r7_completion_route_work_package_preflight()
                                                                            )
                                                                            r7_completion_route_work_package_preflight_status = str(
                                                                                r7_completion_route_work_package_preflight.get(
                                                                                    "route_work_package_preflight_status",
                                                                                    "",
                                                                                )
                                                                            )
                                                                            r7_completion_submitted_work_package_count = int(
                                                                                r7_completion_route_work_package_preflight.get(
                                                                                    "submitted_work_package_count",
                                                                                    0,
                                                                                )
                                                                                or 0
                                                                            )
                                                                            r7_completion_passed_work_package_count = int(
                                                                                r7_completion_route_work_package_preflight.get(
                                                                                    "passed_work_package_count",
                                                                                    0,
                                                                                )
                                                                                or 0
                                                                            )
                                                                            r7_completion_blocked_work_package_count = int(
                                                                                r7_completion_route_work_package_preflight.get(
                                                                                    "blocked_work_package_count",
                                                                                    0,
                                                                                )
                                                                                or 0
                                                                            )
                                                                            r7_completion_route_work_package_preflight_path = str(
                                                                                r7_completion_route_work_package_preflight.get(
                                                                                    "route_work_package_preflight_path",
                                                                                    "",
                                                                                )
                                                                            )
                                                                            r7_completion_route_work_package_patch_plan = (
                                                                                self._r8p_pressure_resolution_r7_completion_route_work_package_patch_plan()
                                                                            )
                                                                            r7_completion_route_work_package_patch_plan_status = str(
                                                                                r7_completion_route_work_package_patch_plan.get(
                                                                                    "route_work_package_patch_plan_status",
                                                                                    "",
                                                                                )
                                                                            )
                                                                            r7_completion_route_work_package_patch_item_count = int(
                                                                                r7_completion_route_work_package_patch_plan.get(
                                                                                    "patch_item_count",
                                                                                    0,
                                                                                )
                                                                                or 0
                                                                            )
                                                                            r7_completion_route_work_package_highest_patch_id = str(
                                                                                r7_completion_route_work_package_patch_plan.get(
                                                                                    "highest_priority_patch_id",
                                                                                    "",
                                                                                )
                                                                            )
                                                                            r7_completion_route_work_package_patch_plan_path = str(
                                                                                r7_completion_route_work_package_patch_plan.get(
                                                                                    "route_work_package_patch_plan_path",
                                                                                    "",
                                                                                )
                                                                            )
                                                                            r7_completion_route_work_package_assembly_gate = (
                                                                                self._r8p_pressure_resolution_r7_completion_route_work_package_assembly_gate()
                                                                            )
                                                                            r7_completion_route_work_package_assembly_gate_status = str(
                                                                                r7_completion_route_work_package_assembly_gate.get(
                                                                                    "route_work_package_assembly_gate_status",
                                                                                    "",
                                                                                )
                                                                            )
                                                                            r7_completion_route_work_package_assembly_step_count = int(
                                                                                r7_completion_route_work_package_assembly_gate.get(
                                                                                    "assembly_step_count",
                                                                                    0,
                                                                                )
                                                                                or 0
                                                                            )
                                                                            r7_completion_route_work_package_ready_assembly_step_count = int(
                                                                                r7_completion_route_work_package_assembly_gate.get(
                                                                                    "ready_assembly_step_count",
                                                                                    0,
                                                                                )
                                                                                or 0
                                                                            )
                                                                            r7_completion_route_work_package_blocked_assembly_step_count = int(
                                                                                r7_completion_route_work_package_assembly_gate.get(
                                                                                    "blocked_assembly_step_count",
                                                                                    0,
                                                                                )
                                                                                or 0
                                                                            )
                                                                            r7_completion_route_work_package_assembly_gate_path = str(
                                                                                r7_completion_route_work_package_assembly_gate.get(
                                                                                    "route_work_package_assembly_gate_path",
                                                                                    "",
                                                                                )
                                                                            )
                                                                            r7_completion_route_work_package_templates = (
                                                                                self._r8p_pressure_resolution_r7_completion_route_work_package_templates()
                                                                            )
                                                                            r7_completion_route_work_package_template_status = str(
                                                                                r7_completion_route_work_package_templates.get(
                                                                                    "route_work_package_templates_status",
                                                                                    "",
                                                                                )
                                                                            )
                                                                            submission_readiness_review = (
                                                                                self._r8p_pressure_resolution_submission_readiness_review()
                                                                            )
                                                                            submission_readiness_review_status = str(
                                                                                submission_readiness_review.get(
                                                                                    "submission_readiness_review_status",
                                                                                    "",
                                                                                )
                                                                            )
                                                                            submission_readiness_next_operator_action = str(
                                                                                submission_readiness_review.get(
                                                                                    "next_operator_action",
                                                                                    "",
                                                                                )
                                                                            )
                                                                            submission_readiness_can_route_to_r8v = bool(
                                                                                submission_readiness_review.get(
                                                                                    "can_route_to_r8v",
                                                                                    False,
                                                                                )
                                                                            )
                                                                            submission_readiness_direct_highest_priority_patch_id = str(
                                                                                submission_readiness_review.get(
                                                                                    "direct_r8p_highest_priority_patch_id",
                                                                                    "",
                                                                                )
                                                                            )
                                                                            submission_readiness_r7_highest_priority_patch_id = str(
                                                                                submission_readiness_review.get(
                                                                                    "r7_to_r8p_highest_priority_patch_id",
                                                                                    "",
                                                                                )
                                                                            )
                                                                            submission_readiness_review_path = str(
                                                                                submission_readiness_review.get(
                                                                                    "review_path",
                                                                                    "",
                                                                                )
                                                                            )
                                                                            source_package_route_guide = (
                                                                                self._r8p_pressure_resolution_source_package_route_guide()
                                                                            )
                                                                            source_package_route_guide_status = str(
                                                                                source_package_route_guide.get(
                                                                                    "source_package_submission_route_guide_status",
                                                                                    "",
                                                                                )
                                                                            )
                                                                            source_package_recommended_route_id = str(
                                                                                source_package_route_guide.get(
                                                                                    "recommended_route_id",
                                                                                    "",
                                                                                )
                                                                            )
                                                                            source_package_next_operator_action = str(
                                                                                source_package_route_guide.get(
                                                                                    "next_operator_action",
                                                                                    "",
                                                                                )
                                                                            )
                                                                            source_package_route_option_count = int(
                                                                                source_package_route_guide.get(
                                                                                    "route_option_count",
                                                                                    0,
                                                                                )
                                                                                or 0
                                                                            )
                                                                            source_package_route_guide_path = str(
                                                                                source_package_route_guide.get(
                                                                                    "guide_path",
                                                                                    "",
                                                                                )
                                                                            )
                                                                            source_package_route_preflight = (
                                                                                self._r8p_pressure_resolution_source_package_route_preflight()
                                                                            )
                                                                            source_package_route_preflight_status = str(
                                                                                source_package_route_preflight.get(
                                                                                    "source_package_route_preflight_status",
                                                                                    "",
                                                                                )
                                                                            )
                                                                            source_package_recommended_route_preflight_status = str(
                                                                                source_package_route_preflight.get(
                                                                                    "recommended_route_preflight_status",
                                                                                    "",
                                                                                )
                                                                            )
                                                                            source_package_route_preflight_next_operator_action = str(
                                                                                source_package_route_preflight.get(
                                                                                    "next_operator_action",
                                                                                    "",
                                                                                )
                                                                            )
                                                                            source_package_ready_route_count = int(
                                                                                source_package_route_preflight.get(
                                                                                    "ready_route_count",
                                                                                    0,
                                                                                )
                                                                                or 0
                                                                            )
                                                                            source_package_waiting_route_count = int(
                                                                                source_package_route_preflight.get(
                                                                                    "waiting_route_count",
                                                                                    0,
                                                                                )
                                                                                or 0
                                                                            )
                                                                            source_package_blocked_route_count = int(
                                                                                source_package_route_preflight.get(
                                                                                    "blocked_route_count",
                                                                                    0,
                                                                                )
                                                                                or 0
                                                                            )
                                                                            source_package_route_preflight_path = str(
                                                                                source_package_route_preflight.get(
                                                                                    "route_preflight_path",
                                                                                    "",
                                                                                )
                                                                            )
                                                                            downstream_route_handoff = (
                                                                                self._r8v_pressure_resolution_downstream_route_handoff()
                                                                            )
                                                                            downstream_route_handoff_status = str(
                                                                                downstream_route_handoff.get(
                                                                                    "downstream_route_handoff_status",
                                                                                    "",
                                                                                )
                                                                            )
                                                                            downstream_handoff_target_count = int(
                                                                                downstream_route_handoff.get(
                                                                                    "handoff_target_count",
                                                                                    0,
                                                                                )
                                                                                or 0
                                                                            )
                                                                            downstream_ready_handoff_target_count = int(
                                                                                downstream_route_handoff.get(
                                                                                    "ready_handoff_target_count",
                                                                                    0,
                                                                                )
                                                                                or 0
                                                                            )
                                                                            downstream_blocked_handoff_target_count = int(
                                                                                downstream_route_handoff.get(
                                                                                    "blocked_handoff_target_count",
                                                                                    0,
                                                                                )
                                                                                or 0
                                                                            )
                                                                            downstream_route_handoff_next_operator_action = str(
                                                                                downstream_route_handoff.get(
                                                                                    "next_operator_action",
                                                                                    "",
                                                                                )
                                                                            )
                                                                            downstream_route_handoff_path = str(
                                                                                downstream_route_handoff.get("handoff_path", "")
                                                                            )
                                                                            downstream_target_gate_preflight = (
                                                                                self._r8v_pressure_resolution_downstream_target_gate_preflight()
                                                                            )
                                                                            downstream_target_gate_preflight_status = str(
                                                                                downstream_target_gate_preflight.get(
                                                                                    "downstream_target_gate_preflight_status",
                                                                                    "",
                                                                                )
                                                                            )
                                                                            downstream_target_gate_count = int(
                                                                                downstream_target_gate_preflight.get(
                                                                                    "target_gate_count",
                                                                                    0,
                                                                                )
                                                                                or 0
                                                                            )
                                                                            downstream_ready_target_gate_count = int(
                                                                                downstream_target_gate_preflight.get(
                                                                                    "ready_target_gate_count",
                                                                                    0,
                                                                                )
                                                                                or 0
                                                                            )
                                                                            downstream_blocked_target_gate_count = int(
                                                                                downstream_target_gate_preflight.get(
                                                                                    "blocked_target_gate_count",
                                                                                    0,
                                                                                )
                                                                                or 0
                                                                            )
                                                                            downstream_target_gate_next_operator_action = str(
                                                                                downstream_target_gate_preflight.get(
                                                                                    "next_operator_action",
                                                                                    "",
                                                                                )
                                                                            )
                                                                            downstream_target_gate_preflight_path = str(
                                                                                downstream_target_gate_preflight.get(
                                                                                    "target_gate_preflight_path",
                                                                                    "",
                                                                                )
                                                                            )
                                                                            downstream_target_gate_result_preflight = (
                                                                                self._r8v_pressure_resolution_downstream_target_gate_result_preflight()
                                                                            )
                                                                            downstream_target_gate_result_preflight_status = str(
                                                                                downstream_target_gate_result_preflight.get(
                                                                                    "downstream_target_gate_result_preflight_status",
                                                                                    "",
                                                                                )
                                                                            )
                                                                            downstream_target_gate_result_submitted_count = int(
                                                                                downstream_target_gate_result_preflight.get(
                                                                                    "submitted_target_result_count",
                                                                                    0,
                                                                                )
                                                                                or 0
                                                                            )
                                                                            downstream_target_gate_result_accepted_count = int(
                                                                                downstream_target_gate_result_preflight.get(
                                                                                    "accepted_target_result_count",
                                                                                    0,
                                                                                )
                                                                                or 0
                                                                            )
                                                                            downstream_target_gate_result_rejected_count = int(
                                                                                downstream_target_gate_result_preflight.get(
                                                                                    "rejected_target_result_count",
                                                                                    0,
                                                                                )
                                                                                or 0
                                                                            )
                                                                            downstream_target_gate_result_next_operator_action = str(
                                                                                downstream_target_gate_result_preflight.get(
                                                                                    "next_operator_action",
                                                                                    "",
                                                                                )
                                                                            )
                                                                            downstream_target_gate_result_preflight_path = str(
                                                                                downstream_target_gate_result_preflight.get(
                                                                                    "preflight_path",
                                                                                    "",
                                                                                )
                                                                            )
                                                                            downstream_target_gate_result_arbitration = (
                                                                                self._r8v_pressure_resolution_downstream_target_gate_result_arbitration()
                                                                            )
                                                                            downstream_target_gate_result_arbitration_status = str(
                                                                                downstream_target_gate_result_arbitration.get(
                                                                                    "downstream_target_gate_result_arbitration_status",
                                                                                    "",
                                                                                )
                                                                            )
                                                                            downstream_target_gate_result_arbitration_next_operator_action = str(
                                                                                downstream_target_gate_result_arbitration.get(
                                                                                    "next_operator_action",
                                                                                    "",
                                                                                )
                                                                            )
                                                                            downstream_target_gate_result_can_route_to_operator_review = bool(
                                                                                downstream_target_gate_result_arbitration.get(
                                                                                    "can_route_to_operator_review",
                                                                                    False,
                                                                                )
                                                                            )
                                                                            downstream_target_gate_result_can_emit_protective_control_candidate = bool(
                                                                                downstream_target_gate_result_arbitration.get(
                                                                                    "can_emit_protective_control_candidate",
                                                                                    False,
                                                                                )
                                                                            )
                                                                            downstream_target_gate_operator_review = (
                                                                                self._r8v_pressure_resolution_downstream_target_gate_operator_review_preflight()
                                                                            )
                                                                            downstream_target_gate_operator_review_status = str(
                                                                                downstream_target_gate_operator_review.get(
                                                                                    "downstream_target_gate_operator_review_preflight_status",
                                                                                    "",
                                                                                )
                                                                            )
                                                                            downstream_target_gate_operator_review_approved_count = int(
                                                                                downstream_target_gate_operator_review.get(
                                                                                    "approved_operator_review_count",
                                                                                    0,
                                                                                )
                                                                                or 0
                                                                            )
                                                                            downstream_target_gate_operator_review_rejected_count = int(
                                                                                downstream_target_gate_operator_review.get(
                                                                                    "rejected_operator_review_count",
                                                                                    0,
                                                                                )
                                                                                or 0
                                                                            )
                                                                            downstream_target_gate_operator_review_hold_count = int(
                                                                                downstream_target_gate_operator_review.get(
                                                                                    "hold_operator_review_count",
                                                                                    0,
                                                                                )
                                                                                or 0
                                                                            )
                                                                            downstream_target_gate_operator_review_next_operator_action = str(
                                                                                downstream_target_gate_operator_review.get(
                                                                                    "next_operator_action",
                                                                                    "",
                                                                                )
                                                                            )
                                                                            downstream_target_gate_operator_review_can_route_to_post_review_gate = bool(
                                                                                downstream_target_gate_operator_review.get(
                                                                                    "can_route_to_post_review_gate",
                                                                                    False,
                                                                                )
                                                                            )
                                                                            downstream_target_gate_operator_review_can_emit_protective_control_candidate = bool(
                                                                                downstream_target_gate_operator_review.get(
                                                                                    "can_emit_protective_control_candidate",
                                                                                    False,
                                                                                )
                                                                            )
                                                                            downstream_target_gate_post_review = (
                                                                                self._r8v_pressure_resolution_downstream_target_gate_post_review_gate()
                                                                            )
                                                                            downstream_target_gate_post_review_status = str(
                                                                                downstream_target_gate_post_review.get(
                                                                                    "downstream_target_gate_post_review_gate_status",
                                                                                    "",
                                                                                )
                                                                            )
                                                                            downstream_target_gate_post_review_next_operator_action = str(
                                                                                downstream_target_gate_post_review.get(
                                                                                    "next_operator_action",
                                                                                    "",
                                                                                )
                                                                            )
                                                                            downstream_target_gate_post_review_can_route_to_protective_candidate = bool(
                                                                                downstream_target_gate_post_review.get(
                                                                                    "can_route_to_protective_candidate_evaluation",
                                                                                    False,
                                                                                )
                                                                            )
                                                                            downstream_target_gate_post_review_can_emit_protective_control_candidate = bool(
                                                                                downstream_target_gate_post_review.get(
                                                                                    "can_emit_protective_control_candidate",
                                                                                    False,
                                                                                )
                                                                            )
                                                                            downstream_target_gate_protective_candidate_evaluation = (
                                                                                self._r8v_pressure_resolution_downstream_target_gate_protective_candidate_evaluation()
                                                                            )
                                                                            downstream_target_gate_protective_candidate_evaluation_status = str(
                                                                                downstream_target_gate_protective_candidate_evaluation.get(
                                                                                    "downstream_target_gate_protective_candidate_evaluation_status",
                                                                                    "",
                                                                                )
                                                                            )
                                                                            downstream_target_gate_protective_candidate_evaluation_next_operator_action = str(
                                                                                downstream_target_gate_protective_candidate_evaluation.get(
                                                                                    "next_operator_action",
                                                                                    "",
                                                                                )
                                                                            )
                                                                            downstream_target_gate_protective_candidate_can_emit = bool(
                                                                                downstream_target_gate_protective_candidate_evaluation.get(
                                                                                    "can_emit_protective_control_candidate",
                                                                                    False,
                                                                                )
                                                                            )
                                                                            downstream_target_gate_protective_candidate_can_route_to_final_execution_review = bool(
                                                                                downstream_target_gate_protective_candidate_evaluation.get(
                                                                                    "can_route_to_final_execution_review",
                                                                                    False,
                                                                                )
                                                                            )
                                                                            r7_completion_item_class_summary = (
                                                                                ",".join(
                                                                                    f"{key}:{value}"
                                                                                    for key, value in sorted(
                                                                                        r7_completion_item_class_counts.items()
                                                                                    )
                                                                                )
                                                                                or "not_available"
                                                                            )
                                                                            r7_completion_field_gap_summary = (
                                                                                ",".join(
                                                                                    f"{key}:{value}"
                                                                                    for key, value in sorted(
                                                                                        r7_completion_field_gap_count_by_class.items()
                                                                                    )
                                                                                )
                                                                                or "not_available"
                                                                            )
                                                                            r7_completion_reason = (
                                                                                "R7-to-R8p completion plan 进一步把补齐路径拆成 R7 source package、"
                                                                                "operator supplement 和 Agent52 replay export 三类证据工单；"
                                                                                if r7_completion_plan_status
                                                                                else ""
                                                                            )
                                                                            r7_route_contract_reason = (
                                                                                "R8u-24 route contracts 已把三类证据工单拆成生产者、输入输出、验收门和失败边界；"
                                                                                if r7_completion_route_contracts_status
                                                                                else ""
                                                                            )
                                                                            r7_route_work_package_reason = (
                                                                                "R8u-25 route work packages 已把每条证据路线进一步拆成提交文件、字段、验收检查和证据边界；"
                                                                                if r7_completion_route_work_packages_status
                                                                                else ""
                                                                            )
                                                                            r7_work_package_preflight_reason = (
                                                                                "R8u-26 work package templates/preflight 已把提交目录、模板占位和候选包缺口前移到机器检查；"
                                                                                if r7_completion_route_work_package_preflight_status
                                                                                else ""
                                                                            )
                                                                            r7_work_package_patch_plan_reason = (
                                                                                "R8u-27 work package patch plan 已把预检阻塞转成逐项可执行修补动作；"
                                                                                if r7_completion_route_work_package_patch_plan_status
                                                                                else ""
                                                                            )
                                                                            r7_work_package_assembly_gate_reason = (
                                                                                "R8u-28 assembly gate 已把四类 work package 到 R8p candidate rows 的装配顺序和验证边界固化；"
                                                                                if r7_completion_route_work_package_assembly_gate_status
                                                                                else ""
                                                                            )
                                                                            submission_readiness_reason = (
                                                                                "R8u-47 submission readiness review 已把 source、schema/provenance、bundle、temporal、semantic、routing 与 R7 work package assembly 汇总成 R8v 入口门；"
                                                                                if submission_readiness_review_status
                                                                                else ""
                                                                            )
                                                                            source_package_route_reason = (
                                                                                "R8u-48 source package route guide 已把 direct JSON、direct CSV directory 和 R7-to-R8p work package 三条提交路线并列成可执行入口；"
                                                                                if source_package_route_guide_status
                                                                                else ""
                                                                            )
                                                                            source_package_route_preflight_reason = (
                                                                                "R8u-49 source package route preflight 已把三条提交路线进一步判定为 ready/waiting/blocked，并保留 replay/holdout 边界；"
                                                                                if source_package_route_preflight_status
                                                                                else ""
                                                                            )
                                                                            downstream_route_handoff_reason = (
                                                                                "R8u-50 downstream route handoff 已把 R8v 目标、执行顺序、期望 gate metrics 和禁止写入边界固化成交接契约；"
                                                                                if downstream_route_handoff_status
                                                                                else ""
                                                                            )
                                                                            downstream_target_gate_preflight_reason = (
                                                                                "R8u-51 downstream target gate preflight 已把四个 R8v 下游目标的运行命令、输入合同、输出指标和阻断边界固化为 target-level preflight board；"
                                                                                if downstream_target_gate_preflight_status
                                                                                else ""
                                                                            )
                                                                            downstream_target_gate_result_preflight_reason = (
                                                                                "R8u-52 downstream target gate result intake 已把 Agent51/49/52/R7 返回结果的目标覆盖、指标字段、source artifact、人工复核边界和禁止写入边界固化为 result-package preflight；"
                                                                                if downstream_target_gate_result_preflight_status
                                                                                else ""
                                                                            )
                                                                            downstream_target_gate_result_arbitration_reason = (
                                                                                "R8u-53 downstream target gate result arbitration 已把四个目标 gate 的 pass/fail/blocked/review 状态合并为只可进入人工复核的安全仲裁门；"
                                                                                if downstream_target_gate_result_arbitration_status
                                                                                else ""
                                                                            )
                                                                            return {
                                                                                "fallback_enabled": True,
                                                                                "action_id": next_patch_action,
                                                                                "title": "按 R8p patch plan 修复 pressure resolution 真实行包",
                                                                                "reason": (
                                                                                    "R8p 已把 source/schema/template/provenance、同批次六表 bundle、"
                                                                                    "temporal-window、scenario-semantic 和场景验收失败转成可执行补包计划；"
                                                                                    "Agent60 现在应直接消费该计划，"
                                                                                    f"{r7_completion_reason}"
                                                                                    f"{r7_route_contract_reason}"
                                                                                    f"{r7_route_work_package_reason}"
                                                                                    f"{r7_work_package_preflight_reason}"
                                                                                    f"{r7_work_package_patch_plan_reason}"
                                                                                    f"{r7_work_package_assembly_gate_reason}"
                                                                                    f"{submission_readiness_reason}"
                                                                                    f"{source_package_route_reason}"
                                                                                    f"{source_package_route_preflight_reason}"
                                                                                    f"{downstream_route_handoff_reason}"
                                                                                    f"{downstream_target_gate_preflight_reason}"
                                                                                    f"{downstream_target_gate_result_preflight_reason}"
                                                                                    f"{downstream_target_gate_result_arbitration_reason}"
                                                                                    "优先处理最高阻断项，而不是继续停留在泛化的“采集真实行”。"
                                                                                ),
                                                                                "trigger_metric": (
                                                                                    f"field_rows_patch_plan_status={patch_status}; "
                                                                                    f"patch_item_count={patch_item_count}; "
                                                                                    f"highest_priority_patch_id={highest_patch}; "
                                                                                f"operator_handoff_status={handoff_status or 'not_available'}; "
                                                                                f"schema_status={schema_status or 'not_available'}; "
                                                                                "schema_validation_status="
                                                                                f"{schema_validation_status or 'not_available'}; "
                                                                                "collection_checklist_status="
                                                                                f"{collection_checklist_status or 'not_available'}; "
                                                                                "batch_bundle_preflight_status="
                                                                                f"{batch_bundle_preflight_status or 'not_available'}; "
                                                                                "temporal_window_preflight_status="
                                                                                f"{temporal_window_preflight_status or 'not_available'}; "
                                                                                "scenario_semantic_preflight_status="
                                                                                f"{scenario_semantic_preflight_status or 'not_available'}; "
                                                                                "downstream_routing_preflight_status="
                                                                                f"{downstream_routing_preflight_status or 'not_available'}; "
                                                                                "provenance_gate_status="
                                                                                    f"{provenance_gate_status or 'not_available'}; "
                                                                                    "all_tables_require_data_origin="
                                                                                    f"{all_tables_require_data_origin}; "
                                                                                    "r7_completion_plan_status="
                                                                                    f"{r7_completion_plan_status or 'not_available'}; "
                                                                                    "r7_completion_item_count="
                                                                                    f"{r7_completion_item_count}; "
                                                                                    "r7_completion_item_classes="
                                                                                    f"{r7_completion_item_class_summary}; "
                                                                                    "r7_completion_field_gaps="
                                                                                    f"{r7_completion_field_gap_summary}; "
                                                                                    "r7_route_contract_status="
                                                                                    f"{r7_completion_route_contracts_status or 'not_available'}; "
                                                                                    "r7_open_route_count="
                                                                                    f"{r7_completion_open_route_count}; "
                                                                                    "r7_open_route_ids="
                                                                                    f"{','.join(r7_completion_open_route_ids) or 'none'}; "
                                                                                    "r7_work_package_status="
                                                                                    f"{r7_completion_route_work_packages_status or 'not_available'}; "
                                                                                    "r7_open_work_package_count="
                                                                                    f"{r7_completion_open_work_package_count}; "
                                                                                    "r7_open_work_package_ids="
                                                                                    f"{','.join(r7_completion_open_work_package_ids) or 'none'}; "
                                                                                    "r7_work_package_template_status="
                                                                                    f"{r7_completion_route_work_package_template_status or 'not_available'}; "
                                                                                    "r7_work_package_preflight_status="
                                                                                    f"{r7_completion_route_work_package_preflight_status or 'not_available'}; "
                                                                                    "r7_submitted_work_package_count="
                                                                                    f"{r7_completion_submitted_work_package_count}; "
                                                                                    "r7_passed_work_package_count="
                                                                                    f"{r7_completion_passed_work_package_count}; "
                                                                                    "r7_blocked_work_package_count="
                                                                                    f"{r7_completion_blocked_work_package_count}; "
                                                                                    "r7_work_package_patch_plan_status="
                                                                                    f"{r7_completion_route_work_package_patch_plan_status or 'not_available'}; "
                                                                                    "r7_work_package_patch_item_count="
                                                                                    f"{r7_completion_route_work_package_patch_item_count}; "
                                                                                    "r7_work_package_highest_priority_patch_id="
                                                                                    f"{r7_completion_route_work_package_highest_patch_id or 'not_available'}; "
                                                                                    "r7_work_package_assembly_gate_status="
                                                                                    f"{r7_completion_route_work_package_assembly_gate_status or 'not_available'}; "
                                                                                    "r7_work_package_assembly_step_count="
                                                                                    f"{r7_completion_route_work_package_assembly_step_count}; "
                                                                                    "r7_work_package_ready_assembly_step_count="
                                                                                    f"{r7_completion_route_work_package_ready_assembly_step_count}; "
                                                                                    "r7_work_package_blocked_assembly_step_count="
                                                                                    f"{r7_completion_route_work_package_blocked_assembly_step_count}; "
                                                                                    "submission_readiness_review_status="
                                                                                    f"{submission_readiness_review_status or 'not_available'}; "
                                                                                    "submission_readiness_next_operator_action="
                                                                                    f"{submission_readiness_next_operator_action or 'not_available'}; "
                                                                                    "submission_readiness_can_route_to_r8v="
                                                                                    f"{submission_readiness_can_route_to_r8v}; "
                                                                                    "source_package_route_guide_status="
                                                                                    f"{source_package_route_guide_status or 'not_available'}; "
                                                                                    "source_package_recommended_route_id="
                                                                                    f"{source_package_recommended_route_id or 'not_available'}; "
                                                                                    "source_package_next_operator_action="
                                                                                    f"{source_package_next_operator_action or 'not_available'}; "
                                                                                    "source_package_route_option_count="
                                                                                    f"{source_package_route_option_count}; "
                                                                                    "source_package_route_preflight_status="
                                                                                    f"{source_package_route_preflight_status or 'not_available'}; "
                                                                                    "source_package_recommended_route_preflight_status="
                                                                                    f"{source_package_recommended_route_preflight_status or 'not_available'}; "
                                                                                    "source_package_route_preflight_next_operator_action="
                                                                                    f"{source_package_route_preflight_next_operator_action or 'not_available'}; "
                                                                                    "source_package_ready_route_count="
                                                                                    f"{source_package_ready_route_count}; "
                                                                                    "source_package_waiting_route_count="
                                                                                    f"{source_package_waiting_route_count}; "
                                                                                    "source_package_blocked_route_count="
                                                                                    f"{source_package_blocked_route_count}; "
                                                                                    "downstream_route_handoff_status="
                                                                                    f"{downstream_route_handoff_status or 'not_available'}; "
                                                                                    "downstream_ready_handoff_target_count="
                                                                                    f"{downstream_ready_handoff_target_count}; "
                                                                                    "downstream_blocked_handoff_target_count="
                                                                                    f"{downstream_blocked_handoff_target_count}; "
                                                                                    "downstream_route_handoff_next_operator_action="
                                                                                    f"{downstream_route_handoff_next_operator_action or 'not_available'}; "
                                                                                    "downstream_target_gate_preflight_status="
                                                                                    f"{downstream_target_gate_preflight_status or 'not_available'}; "
                                                                                    "downstream_ready_target_gate_count="
                                                                                    f"{downstream_ready_target_gate_count}; "
                                                                                    "downstream_blocked_target_gate_count="
                                                                                    f"{downstream_blocked_target_gate_count}; "
                                                                                    "downstream_target_gate_preflight_next_operator_action="
                                                                                    f"{downstream_target_gate_next_operator_action or 'not_available'}; "
                                                                                    "downstream_target_gate_result_preflight_status="
                                                                                    f"{downstream_target_gate_result_preflight_status or 'not_available'}; "
                                                                                    "downstream_target_gate_result_submitted_count="
                                                                                    f"{downstream_target_gate_result_submitted_count}; "
                                                                                    "downstream_target_gate_result_accepted_count="
                                                                                    f"{downstream_target_gate_result_accepted_count}; "
                                                                                    "downstream_target_gate_result_rejected_count="
                                                                                    f"{downstream_target_gate_result_rejected_count}; "
                                                                                    "downstream_target_gate_result_next_operator_action="
                                                                                    f"{downstream_target_gate_result_next_operator_action or 'not_available'}; "
                                                                                    "downstream_target_gate_result_arbitration_status="
                                                                                    f"{downstream_target_gate_result_arbitration_status or 'not_available'}; "
                                                                                    "downstream_target_gate_result_arbitration_next_operator_action="
                                                                                    f"{downstream_target_gate_result_arbitration_next_operator_action or 'not_available'}; "
                                                                                    "downstream_target_gate_result_can_route_to_operator_review="
                                                                                    f"{downstream_target_gate_result_can_route_to_operator_review}; "
                                                                                    "downstream_target_gate_result_can_emit_protective_control_candidate="
                                                                                    f"{downstream_target_gate_result_can_emit_protective_control_candidate}; "
                                                                                    "downstream_target_gate_operator_review_preflight_status="
                                                                                    f"{downstream_target_gate_operator_review_status or 'not_available'}; "
                                                                                    "downstream_target_gate_operator_review_approved_count="
                                                                                    f"{downstream_target_gate_operator_review_approved_count}; "
                                                                                    "downstream_target_gate_operator_review_rejected_count="
                                                                                    f"{downstream_target_gate_operator_review_rejected_count}; "
                                                                                    "downstream_target_gate_operator_review_hold_count="
                                                                                    f"{downstream_target_gate_operator_review_hold_count}; "
                                                                                    "downstream_target_gate_operator_review_next_operator_action="
                                                                                    f"{downstream_target_gate_operator_review_next_operator_action or 'not_available'}; "
                                                                                    "downstream_target_gate_operator_review_can_route_to_post_review_gate="
                                                                                    f"{downstream_target_gate_operator_review_can_route_to_post_review_gate}; "
                                                                                    "downstream_target_gate_operator_review_can_emit_protective_control_candidate="
                                                                                    f"{downstream_target_gate_operator_review_can_emit_protective_control_candidate}; "
                                                                                    "downstream_target_gate_post_review_gate_status="
                                                                                    f"{downstream_target_gate_post_review_status or 'not_available'}; "
                                                                                    "downstream_target_gate_post_review_next_operator_action="
                                                                                    f"{downstream_target_gate_post_review_next_operator_action or 'not_available'}; "
                                                                                    "downstream_target_gate_post_review_can_route_to_protective_candidate="
                                                                                    f"{downstream_target_gate_post_review_can_route_to_protective_candidate}; "
                                                                                    "downstream_target_gate_post_review_can_emit_protective_control_candidate="
                                                                                    f"{downstream_target_gate_post_review_can_emit_protective_control_candidate}; "
                                                                                    "downstream_target_gate_protective_candidate_evaluation_status="
                                                                                    f"{downstream_target_gate_protective_candidate_evaluation_status or 'not_available'}; "
                                                                                    "downstream_target_gate_protective_candidate_next_operator_action="
                                                                                    f"{downstream_target_gate_protective_candidate_evaluation_next_operator_action or 'not_available'}; "
                                                                                    "downstream_target_gate_protective_candidate_can_emit="
                                                                                    f"{downstream_target_gate_protective_candidate_can_emit}; "
                                                                                    "downstream_target_gate_protective_candidate_can_route_to_final_execution_review="
                                                                                    f"{downstream_target_gate_protective_candidate_can_route_to_final_execution_review}"
                                                                                ),
                                                                                "must_not_do": (
                                                                                    "不能把 patch plan 当作 field evidence；补包计划只指导现场采集，"
                                                                                    "所有真实行仍必须通过 R8p acceptance、R8v 路由复核和后续 "
                                                                                "Agent51/49/52/R7 gate，不能写 actuator 或 release gate。"
                                                                            ),
                                                                            "expected_metrics": [
                                                                                "field_rows_patch_plan_status",
                                                                                "highest_priority_patch_id",
                                                                                "field_rows_source_status",
                                                                                "field_row_acceptance_status",
                                                                                "accepted_field_scenario_count",
                                                                                "field_rows_operator_handoff_status",
                                                                                "field_rows_package_schema_status",
                                                                                "field_rows_schema_validation_status",
                                                                                "field_rows_schema_required_field_gap_count",
                                                                                "field_rows_schema_invalid_type_count",
                                                                                "field_rows_schema_template_marker_gap_count",
                                                                                "field_rows_schema_field_origin_gap_count",
                                                                                "field_rows_collection_checklist_status",
                                                                                "field_rows_batch_bundle_preflight_status",
                                                                                "field_rows_complete_batch_bundle_count",
                                                                                "field_rows_partial_batch_bundle_count",
                                                                                "field_rows_missing_bundle_table_count",
                                                                                "field_rows_temporal_window_preflight_status",
                                                                                "field_rows_temporal_valid_batch_count",
                                                                                "field_rows_temporal_violation_count",
                                                                                "field_rows_hold_time_violation_count",
                                                                                "field_rows_scenario_semantic_preflight_status",
                                                                                "field_rows_semantic_valid_batch_count",
                                                                                "field_rows_semantic_violation_count",
                                                                                "field_rows_downstream_routing_preflight_status",
                                                                                "field_rows_routing_ready_target_count",
                                                                                "field_rows_downstream_routing_target_count",
                                                                                    "field_rows_provenance_gate_status",
                                                                                    "field_rows_all_tables_require_data_origin",
                                                                                    "r7_completion_plan_status",
                                                                                    "r7_completion_item_class_counts",
                                                                                    "r7_completion_field_gap_count_by_class",
                                                                                    "r7_completion_required_execution_order",
                                                                                    "r7_completion_route_contracts_status",
                                                                                    "r7_completion_open_route_count",
                                                                                    "r7_completion_open_route_ids",
                                                                                    "r7_completion_route_work_packages_status",
                                                                                    "r7_completion_open_work_package_count",
                                                                                    "r7_completion_open_work_package_ids",
                                                                                    "r7_completion_route_work_package_preflight_status",
                                                                                    "r7_completion_submitted_work_package_count",
                                                                                    "r7_completion_passed_work_package_count",
                                                                                    "r7_completion_blocked_work_package_count",
                                                                                    "r7_completion_route_work_package_patch_plan_status",
                                                                                    "r7_completion_route_work_package_patch_item_count",
                                                                                    "r7_completion_route_work_package_highest_priority_patch_id",
                                                                                    "r7_completion_route_work_package_assembly_gate_status",
                                                                                    "r7_completion_route_work_package_assembly_step_count",
                                                                                    "r7_completion_route_work_package_ready_assembly_step_count",
                                                                                    "r7_completion_route_work_package_blocked_assembly_step_count",
                                                                                    "submission_readiness_review_status",
                                                                                    "submission_readiness_next_operator_action",
                                                                                    "submission_readiness_can_route_to_r8v",
                                                                                    "submission_readiness_direct_highest_priority_patch_id",
                                                                                    "submission_readiness_r7_highest_priority_patch_id",
                                                                                    "source_package_route_guide_status",
                                                                                    "source_package_recommended_route_id",
                                                                                    "source_package_next_operator_action",
                                                                                    "source_package_route_option_count",
                                                                                    "source_package_route_preflight_status",
                                                                                    "source_package_recommended_route_preflight_status",
                                                                                    "source_package_route_preflight_next_operator_action",
                                                                                    "source_package_ready_route_count",
                                                                                    "source_package_waiting_route_count",
                                                                                    "source_package_blocked_route_count",
                                                                                    "field_rows_downstream_route_handoff_status",
                                                                                    "field_rows_downstream_ready_handoff_target_count",
                                                                                    "field_rows_downstream_blocked_handoff_target_count",
                                                                                    "field_rows_downstream_route_handoff_next_operator_action",
                                                                                    "field_rows_downstream_target_gate_preflight_status",
                                                                                    "field_rows_downstream_ready_target_gate_count",
                                                                                    "field_rows_downstream_blocked_target_gate_count",
                                                                                    "field_rows_downstream_target_gate_preflight_next_operator_action",
                                                                                    "field_rows_downstream_target_gate_result_preflight_status",
                                                                                    "field_rows_downstream_target_gate_result_submitted_count",
                                                                                    "field_rows_downstream_target_gate_result_accepted_count",
                                                                                    "field_rows_downstream_target_gate_result_rejected_count",
                                                                                    "field_rows_downstream_target_gate_result_next_operator_action",
                                                                                    "field_rows_downstream_target_gate_result_arbitration_status",
                                                                                    "field_rows_downstream_target_gate_result_arbitration_next_operator_action",
                                                                                    "field_rows_downstream_target_gate_result_can_route_to_operator_review",
                                                                                    "field_rows_downstream_target_gate_result_can_emit_protective_control_candidate",
                                                                                    "field_rows_downstream_target_gate_operator_review_preflight_status",
                                                                                    "field_rows_downstream_target_gate_operator_review_approved_count",
                                                                                    "field_rows_downstream_target_gate_operator_review_rejected_count",
                                                                                    "field_rows_downstream_target_gate_operator_review_hold_count",
                                                                                    "field_rows_downstream_target_gate_operator_review_next_operator_action",
                                                                                    "field_rows_downstream_target_gate_operator_review_can_route_to_post_review_gate",
                                                                                    "field_rows_downstream_target_gate_operator_review_can_emit_protective_control_candidate",
                                                                                    "field_rows_downstream_target_gate_post_review_gate_status",
                                                                                    "field_rows_downstream_target_gate_post_review_next_operator_action",
                                                                                    "field_rows_downstream_target_gate_post_review_can_route_to_protective_candidate",
                                                                                    "field_rows_downstream_target_gate_post_review_can_emit_protective_control_candidate",
                                                                                    "field_rows_downstream_target_gate_protective_candidate_evaluation_status",
                                                                                    "field_rows_downstream_target_gate_protective_candidate_next_operator_action",
                                                                                    "field_rows_downstream_target_gate_protective_candidate_can_emit",
                                                                                    "field_rows_downstream_target_gate_protective_candidate_can_route_to_final_execution_review",
                                                                                    "can_write_to_actuator",
                                                                                    "can_write_to_release_gate",
                                                                                ],
                                                                            "patch_plan_status": patch_status,
                                                                            "highest_priority_patch_id": highest_patch,
                                                                            "patch_item_count": patch_item_count,
                                                                            "operator_handoff_status": handoff_status,
                                                                            "field_rows_package_schema_status": schema_status,
                                                                            "field_rows_schema_validation_status": (
                                                                                schema_validation_status
                                                                            ),
                                                                            "field_rows_collection_checklist_status": (
                                                                                collection_checklist_status
                                                                            ),
                                                                            "field_rows_batch_bundle_preflight_status": (
                                                                                batch_bundle_preflight_status
                                                                            ),
                                                                            "batch_bundle_preflight_summary": (
                                                                                batch_bundle_preflight_summary
                                                                                if isinstance(
                                                                                    batch_bundle_preflight_summary,
                                                                                    dict,
                                                                                )
                                                                                else {}
                                                                            ),
                                                                            "field_rows_temporal_window_preflight_status": (
                                                                                temporal_window_preflight_status
                                                                            ),
                                                                            "temporal_window_preflight_summary": (
                                                                                temporal_window_preflight_summary
                                                                                if isinstance(
                                                                                    temporal_window_preflight_summary,
                                                                                    dict,
                                                                                )
                                                                                else {}
                                                                            ),
                                                                            "field_rows_scenario_semantic_preflight_status": (
                                                                                scenario_semantic_preflight_status
                                                                            ),
                                                                            "scenario_semantic_preflight_summary": (
                                                                                scenario_semantic_preflight_summary
                                                                                if isinstance(
                                                                                    scenario_semantic_preflight_summary,
                                                                                    dict,
                                                                                )
                                                                                else {}
                                                                            ),
                                                                            "field_rows_downstream_routing_preflight_status": (
                                                                                downstream_routing_preflight_status
                                                                            ),
                                                                                "downstream_routing_preflight_summary": (
                                                                                    downstream_routing_preflight_summary
                                                                                    if isinstance(
                                                                                        downstream_routing_preflight_summary,
                                                                                        dict,
                                                                                    )
                                                                                    else {}
                                                                                ),
                                                                                "field_rows_downstream_route_handoff_status": (
                                                                                    downstream_route_handoff_status
                                                                                ),
                                                                                "downstream_handoff_target_count": (
                                                                                    downstream_handoff_target_count
                                                                                ),
                                                                                "downstream_ready_handoff_target_count": (
                                                                                    downstream_ready_handoff_target_count
                                                                                ),
                                                                                "downstream_blocked_handoff_target_count": (
                                                                                    downstream_blocked_handoff_target_count
                                                                                ),
                                                                                "downstream_route_handoff_next_operator_action": (
                                                                                    downstream_route_handoff_next_operator_action
                                                                                ),
                                                                                "downstream_route_handoff_path": (
                                                                                    downstream_route_handoff_path
                                                                                ),
                                                                                "field_rows_downstream_target_gate_preflight_status": (
                                                                                    downstream_target_gate_preflight_status
                                                                                ),
                                                                                "downstream_target_gate_count": (
                                                                                    downstream_target_gate_count
                                                                                ),
                                                                                "downstream_ready_target_gate_count": (
                                                                                    downstream_ready_target_gate_count
                                                                                ),
                                                                                "downstream_blocked_target_gate_count": (
                                                                                    downstream_blocked_target_gate_count
                                                                                ),
                                                                                "downstream_target_gate_preflight_next_operator_action": (
                                                                                    downstream_target_gate_next_operator_action
                                                                                ),
                                                                                "downstream_target_gate_preflight_path": (
                                                                                    downstream_target_gate_preflight_path
                                                                                ),
                                                                                "field_rows_downstream_target_gate_result_preflight_status": (
                                                                                    downstream_target_gate_result_preflight_status
                                                                                ),
                                                                                "downstream_target_gate_result_submitted_count": (
                                                                                    downstream_target_gate_result_submitted_count
                                                                                ),
                                                                                "downstream_target_gate_result_accepted_count": (
                                                                                    downstream_target_gate_result_accepted_count
                                                                                ),
                                                                                "downstream_target_gate_result_rejected_count": (
                                                                                    downstream_target_gate_result_rejected_count
                                                                                ),
                                                                                "downstream_target_gate_result_next_operator_action": (
                                                                                    downstream_target_gate_result_next_operator_action
                                                                                ),
                                                                                "downstream_target_gate_result_preflight_path": (
                                                                                    downstream_target_gate_result_preflight_path
                                                                                ),
                                                                                "field_rows_downstream_target_gate_result_arbitration_status": (
                                                                                    downstream_target_gate_result_arbitration_status
                                                                                ),
                                                                                "downstream_target_gate_result_arbitration_next_operator_action": (
                                                                                    downstream_target_gate_result_arbitration_next_operator_action
                                                                                ),
                                                                                "downstream_target_gate_result_can_route_to_operator_review": (
                                                                                    downstream_target_gate_result_can_route_to_operator_review
                                                                                ),
                                                                                "downstream_target_gate_result_can_emit_protective_control_candidate": (
                                                                                    downstream_target_gate_result_can_emit_protective_control_candidate
                                                                                ),
                                                                                "downstream_target_gate_result_arbitration_summary": (
                                                                                    downstream_target_gate_result_arbitration
                                                                                ),
                                                                                "field_rows_downstream_target_gate_operator_review_preflight_status": (
                                                                                    downstream_target_gate_operator_review_status
                                                                                ),
                                                                                "downstream_target_gate_operator_review_approved_count": (
                                                                                    downstream_target_gate_operator_review_approved_count
                                                                                ),
                                                                                "downstream_target_gate_operator_review_rejected_count": (
                                                                                    downstream_target_gate_operator_review_rejected_count
                                                                                ),
                                                                                "downstream_target_gate_operator_review_hold_count": (
                                                                                    downstream_target_gate_operator_review_hold_count
                                                                                ),
                                                                                "downstream_target_gate_operator_review_next_operator_action": (
                                                                                    downstream_target_gate_operator_review_next_operator_action
                                                                                ),
                                                                                "downstream_target_gate_operator_review_can_route_to_post_review_gate": (
                                                                                    downstream_target_gate_operator_review_can_route_to_post_review_gate
                                                                                ),
                                                                                "downstream_target_gate_operator_review_can_emit_protective_control_candidate": (
                                                                                    downstream_target_gate_operator_review_can_emit_protective_control_candidate
                                                                                ),
                                                                                "downstream_target_gate_operator_review_summary": (
                                                                                    downstream_target_gate_operator_review
                                                                                ),
                                                                                "field_rows_downstream_target_gate_post_review_gate_status": (
                                                                                    downstream_target_gate_post_review_status
                                                                                ),
                                                                                "downstream_target_gate_post_review_next_operator_action": (
                                                                                    downstream_target_gate_post_review_next_operator_action
                                                                                ),
                                                                                "downstream_target_gate_post_review_can_route_to_protective_candidate": (
                                                                                    downstream_target_gate_post_review_can_route_to_protective_candidate
                                                                                ),
                                                                                "downstream_target_gate_post_review_can_emit_protective_control_candidate": (
                                                                                    downstream_target_gate_post_review_can_emit_protective_control_candidate
                                                                                ),
                                                                                "downstream_target_gate_post_review_summary": (
                                                                                    downstream_target_gate_post_review
                                                                                ),
                                                                                "field_rows_downstream_target_gate_protective_candidate_evaluation_status": (
                                                                                    downstream_target_gate_protective_candidate_evaluation_status
                                                                                ),
                                                                                "downstream_target_gate_protective_candidate_next_operator_action": (
                                                                                    downstream_target_gate_protective_candidate_evaluation_next_operator_action
                                                                                ),
                                                                                "downstream_target_gate_protective_candidate_can_emit": (
                                                                                    downstream_target_gate_protective_candidate_can_emit
                                                                                ),
                                                                                "downstream_target_gate_protective_candidate_can_route_to_final_execution_review": (
                                                                                    downstream_target_gate_protective_candidate_can_route_to_final_execution_review
                                                                                ),
                                                                                "downstream_target_gate_protective_candidate_summary": (
                                                                                    downstream_target_gate_protective_candidate_evaluation
                                                                                ),
                                                                                "field_rows_provenance_gate_status": (
                                                                                    provenance_gate_status
                                                                                ),
                                                                            "field_rows_all_tables_require_data_origin": (
                                                                                all_tables_require_data_origin
                                                                            ),
                                                                                "field_rows_provenance_required_table_count": (
                                                                                    provenance_required_table_count
                                                                                ),
                                                                                "r7_completion_plan_status": (
                                                                                    r7_completion_plan_status
                                                                                ),
                                                                                "r7_completion_item_count": (
                                                                                    r7_completion_item_count
                                                                                ),
                                                                                "r7_completion_item_class_counts": (
                                                                                    r7_completion_item_class_counts
                                                                                ),
                                                                                "r7_completion_field_gap_count_by_class": (
                                                                                    r7_completion_field_gap_count_by_class
                                                                                ),
                                                                                "r7_completion_plan_path": (
                                                                                    r7_completion_plan_path
                                                                                ),
                                                                                "r7_completion_required_execution_order": (
                                                                                    r7_completion_required_execution_order
                                                                                ),
                                                                                "r7_completion_route_contracts_status": (
                                                                                    r7_completion_route_contracts_status
                                                                                ),
                                                                                "r7_completion_route_contract_count": (
                                                                                    r7_completion_route_contract_count
                                                                                ),
                                                                                "r7_completion_open_route_count": (
                                                                                    r7_completion_open_route_count
                                                                                ),
                                                                                "r7_completion_open_route_ids": (
                                                                                    r7_completion_open_route_ids
                                                                                ),
                                                                                "r7_completion_route_contracts_path": (
                                                                                    r7_completion_route_contracts_path
                                                                                ),
                                                                                "r7_completion_route_work_packages_status": (
                                                                                    r7_completion_route_work_packages_status
                                                                                ),
                                                                                "r7_completion_route_work_package_count": (
                                                                                    r7_completion_route_work_package_count
                                                                                ),
                                                                                "r7_completion_open_work_package_count": (
                                                                                    r7_completion_open_work_package_count
                                                                                ),
                                                                                "r7_completion_open_work_package_ids": (
                                                                                    r7_completion_open_work_package_ids
                                                                                ),
                                                                                "r7_completion_route_work_packages_path": (
                                                                                    r7_completion_route_work_packages_path
                                                                                ),
                                                                                "r7_completion_route_work_package_templates_status": (
                                                                                    r7_completion_route_work_package_template_status
                                                                                ),
                                                                                "r7_completion_route_work_package_preflight_status": (
                                                                                    r7_completion_route_work_package_preflight_status
                                                                                ),
                                                                                "r7_completion_submitted_work_package_count": (
                                                                                    r7_completion_submitted_work_package_count
                                                                                ),
                                                                                "r7_completion_passed_work_package_count": (
                                                                                    r7_completion_passed_work_package_count
                                                                                ),
                                                                                "r7_completion_blocked_work_package_count": (
                                                                                    r7_completion_blocked_work_package_count
                                                                                ),
                                                                                "r7_completion_route_work_package_preflight_path": (
                                                                                    r7_completion_route_work_package_preflight_path
                                                                                ),
                                                                                "r7_completion_route_work_package_patch_plan_status": (
                                                                                    r7_completion_route_work_package_patch_plan_status
                                                                                ),
                                                                                "r7_completion_route_work_package_patch_item_count": (
                                                                                    r7_completion_route_work_package_patch_item_count
                                                                                ),
                                                                                "r7_completion_route_work_package_highest_priority_patch_id": (
                                                                                    r7_completion_route_work_package_highest_patch_id
                                                                                ),
                                                                                "r7_completion_route_work_package_patch_plan_path": (
                                                                                    r7_completion_route_work_package_patch_plan_path
                                                                                ),
                                                                                "r7_completion_route_work_package_assembly_gate_status": (
                                                                                    r7_completion_route_work_package_assembly_gate_status
                                                                                ),
                                                                                "r7_completion_route_work_package_assembly_step_count": (
                                                                                    r7_completion_route_work_package_assembly_step_count
                                                                                ),
                                                                                "r7_completion_route_work_package_ready_assembly_step_count": (
                                                                                    r7_completion_route_work_package_ready_assembly_step_count
                                                                                ),
                                                                                "r7_completion_route_work_package_blocked_assembly_step_count": (
                                                                                    r7_completion_route_work_package_blocked_assembly_step_count
                                                                                ),
                                                                                "r7_completion_route_work_package_assembly_gate_path": (
                                                                                    r7_completion_route_work_package_assembly_gate_path
                                                                                ),
                                                                                "submission_readiness_review_status": (
                                                                                    submission_readiness_review_status
                                                                                ),
                                                                                "submission_readiness_next_operator_action": (
                                                                                    submission_readiness_next_operator_action
                                                                                ),
                                                                                "submission_readiness_can_route_to_r8v": (
                                                                                    submission_readiness_can_route_to_r8v
                                                                                ),
                                                                                "submission_readiness_direct_highest_priority_patch_id": (
                                                                                    submission_readiness_direct_highest_priority_patch_id
                                                                                ),
                                                                                "submission_readiness_r7_highest_priority_patch_id": (
                                                                                    submission_readiness_r7_highest_priority_patch_id
                                                                                ),
                                                                                "submission_readiness_review_path": (
                                                                                    submission_readiness_review_path
                                                                                ),
                                                                                "source_package_route_guide_status": (
                                                                                    source_package_route_guide_status
                                                                                ),
                                                                                "source_package_recommended_route_id": (
                                                                                    source_package_recommended_route_id
                                                                                ),
                                                                                "source_package_next_operator_action": (
                                                                                    source_package_next_operator_action
                                                                                ),
                                                                                "source_package_route_option_count": (
                                                                                    source_package_route_option_count
                                                                                ),
                                                                                "source_package_route_guide_path": (
                                                                                    source_package_route_guide_path
                                                                                ),
                                                                                "source_package_route_preflight_status": (
                                                                                    source_package_route_preflight_status
                                                                                ),
                                                                                "source_package_recommended_route_preflight_status": (
                                                                                    source_package_recommended_route_preflight_status
                                                                                ),
                                                                                "source_package_route_preflight_next_operator_action": (
                                                                                    source_package_route_preflight_next_operator_action
                                                                                ),
                                                                                "source_package_ready_route_count": (
                                                                                    source_package_ready_route_count
                                                                                ),
                                                                                "source_package_waiting_route_count": (
                                                                                    source_package_waiting_route_count
                                                                                ),
                                                                                "source_package_blocked_route_count": (
                                                                                    source_package_blocked_route_count
                                                                                ),
                                                                                "source_package_route_preflight_path": (
                                                                                    source_package_route_preflight_path
                                                                                ),
                                                                                "schema_validation_summary": (
                                                                                    schema_validation_summary
                                                                                    if isinstance(
                                                                                    schema_validation_summary,
                                                                                    dict,
                                                                                )
                                                                                else {}
                                                                            ),
                                                                                "validation_command": operator_handoff.get(
                                                                                    "validation_command_default",
                                                                                    "",
                                                                                ),
                                                                                "env_override_name": operator_handoff.get(
                                                                                    "env_override_name",
                                                                                    "",
                                                                                ),
                                                                                "default_field_rows_path": operator_handoff.get(
                                                                                    "default_field_rows_path",
                                                                                    "",
                                                                                ),
                                                                                "template_rows_path": operator_handoff.get(
                                                                                    "template_rows_path",
                                                                                    "",
                                                                                ),
                                                                                "rows_schema_path": operator_handoff.get(
                                                                                    "rows_schema_path",
                                                                                    "",
                                                                                ),
                                                                                "collection_checklist_path": operator_handoff.get(
                                                                                    "collection_checklist_path",
                                                                                    "",
                                                                                ),
                                                                                "batch_bundle_preflight_path": operator_handoff.get(
                                                                                    "field_rows_batch_bundle_preflight_path",
                                                                                    "",
                                                                                ),
                                                                                "temporal_window_preflight_path": operator_handoff.get(
                                                                                    "field_rows_temporal_window_preflight_path",
                                                                                    "",
                                                                                ),
                                                                                "scenario_semantic_preflight_path": operator_handoff.get(
                                                                                    "field_rows_scenario_semantic_preflight_path",
                                                                                    "",
                                                                                ),
                                                                                "downstream_routing_preflight_path": operator_handoff.get(
                                                                                    "field_rows_downstream_routing_preflight_path",
                                                                                    "",
                                                                                ),
                                                                            }
                                                                    return {
                                                                        "fallback_enabled": True,
                                                                        "action_id": "R8p_collect_pressure_resolution_replay_rows",
                                                                        "title": "采集 pressure resolution 的 resolved/unresolved 真实 replay 行",
                                                                        "reason": (
                                                                            "R8o 已把 pressure resolution replay 场景包定义为可执行 schema；"
                                                                            "下一步最高边际价值是采集真实 unresolved/resolved conflict、"
                                                                            "operator review latency、Agent51 scoreability recovery 与 Agent49/52 clearance 行，"
                                                                            "否则解除门仍停留在 synthetic/template 层。"
                                                                        ),
                                                                        "trigger_metric": (
                                                                            f"pressure_headloss_candidate_count={pressure_pool.get('candidate_count', 0)}; "
                                                                            "R8o_pressure_resolution_scenario_pack_ready=True"
                                                                        ),
                                                                        "must_not_do": (
                                                                            "不能用 scenario schema ready 代替 field replay；必须保留 batch-level "
                                                                            "node pressure、pressure/headloss event、operation review、lab label 与 replay row。"
                                                                        ),
                                                                        "expected_metrics": [
                                                                            "field_scenario_coverage",
                                                                            "unresolved_pressure_source_conflict_replay_case_count",
                                                                            "resolved_pressure_source_conflict_replay_case_count",
                                                                            "operator_review_latency_min",
                                                                            "scoreability_recovered_batch_count",
                                                                            "agent52_pressure_source_conflict_clear",
                                                                        ],
                                                                    }
                                                                return {
                                                                    "fallback_enabled": True,
                                                                    "action_id": "R8o_pressure_resolution_field_replay_scenario_pack",
                                                                    "title": "把压力源复核解除门转成真实 replay 场景采集包",
                                                                    "reason": (
                                                                        "R8n 已把 resolved/unresolved pressure source conflict "
                                                                        "接入 R7、Agent51、Agent49 与 Agent52；下一步离线核心价值是把"
                                                                        "已解决冲突、未解决冲突、复核延迟和 scoreability 恢复场景写成真实 replay 采集包，"
                                                                        "避免只在字段层证明解除门可运行。"
                                                                    ),
                                                                    "trigger_metric": (
                                                                        f"pressure_headloss_candidate_count={pressure_pool.get('candidate_count', 0)}; "
                                                                        "R8m_pressure_conflict_field_patch_ready=True; "
                                                                        "R8n_pressure_resolution_replay_clearance_ready=True"
                                                                    ),
                                                                    "must_not_do": (
                                                                        "不能把 resolved_count=0 的 template clear 当成现场已校准；"
                                                                        "必须用真实 batch-level reviewer/calibration/action/replay 行验证。"
                                                                    ),
                                                                    "expected_metrics": [
                                                                        "resolved_pressure_source_conflict_replay_case_count",
                                                                        "unresolved_pressure_source_conflict_replay_case_count",
                                                                        "pressure_source_resolution_record_count",
                                                                        "agent51_scoreability_recovered_batch_count",
                                                                        "agent49_pressure_conflict_guardrail_clear",
                                                                        "agent52_replay_conflict_clearance_case_count",
                                                                        "operator_review_latency_min",
                                                                    ],
                                                                }
                                                            return {
                                                                "fallback_enabled": True,
                                                                "action_id": "R8n_pressure_source_resolution_replay_clearance_gate",
                                                                "title": "把压力源冲突复核结果接回 Agent51/49/52 解除门",
                                                                "reason": (
                                                                    "R8m 已能把 pressure source conflict 转成 R7 field package patch items；"
                                                                    "下一步应定义 operator review resolution 如何让 Agent51 重新 score、"
                                                                    "并让 Agent49/52 只在冲突解除后才考虑保护放松。"
                                                                ),
                                                                "trigger_metric": (
                                                                    f"pressure_headloss_candidate_count={pressure_pool.get('candidate_count', 0)}; "
                                                                    "R8m_pressure_conflict_field_patch_ready=True"
                                                                ),
                                                                "must_not_do": (
                                                                    "不能因为 patch item 已生成就认为冲突已经解决；必须看到真实 reviewer/calibration/action 记录，"
                                                                    "并重跑 Agent51 holdout 与 Agent49/52 replay。"
                                                                ),
                                                                "expected_metrics": [
                                                                    "pressure_source_resolution_record_count",
                                                                    "unresolved_pressure_source_conflict_count",
                                                                    "agent51_scoreability_after_resolution",
                                                                    "agent49_pressure_conflict_guardrail_clear",
                                                                    "agent52_replay_conflict_clearance_case_count",
                                                                ],
                                                            }
                                                        return {
                                                            "fallback_enabled": True,
                                                            "action_id": "R8m_pressure_source_conflict_field_patch_requirements",
                                                            "title": "把 pressure source conflict 转成现场校准与补包任务",
                                                            "reason": (
                                                                "Agent51 已能识别压力双源冲突，Agent49/52 也已把冲突转成控制保护和 replay 指标；"
                                                                "下一步应将 conflict batch、冲突来源、容差、operator review 和校准动作写入 R7 patch plan/field package requirement，"
                                                                "让现场团队知道要补哪一类压力/水头损失校准证据。"
                                                            ),
                                                            "trigger_metric": (
                                                                f"pressure_headloss_candidate_count={pressure_pool.get('candidate_count', 0)}; "
                                                                "R8k_pressure_conflict_boundary_ready=True; "
                                                                "R8l_conflict_control_replay_ready=True"
                                                            ),
                                                            "must_not_do": (
                                                                "不能把 conflict count=0 的 template 结果当成现场无冲突；必须要求真实 batch-level 校准和人工复核记录。"
                                                            ),
                                                            "expected_metrics": [
                                                                "pressure_conflict_patch_item_count",
                                                                "operator_review_required_batch_count",
                                                                "pressure_source_calibration_requirement_count",
                                                                "field_package_pressure_conflict_resolution_ready",
                                                            ],
                                                        }
                                                    return {
                                                        "fallback_enabled": True,
                                                        "action_id": "R8l_pressure_source_conflict_control_replay_impact",
                                                        "title": "把 pressure source conflict 接入 Agent49/52 控制 replay 影响",
                                                        "reason": (
                                                            "Agent51 已建立压力双源冲突边界；下一步应让 Agent49 的 reward guardrail 和 Agent52 的 replay metrics "
                                                            "显式消费 pressure_source_conflict_count，确保冲突压力源会阻断催化剂/水力保护放松，并形成 replay blocked cases。"
                                                        ),
                                                        "trigger_metric": (
                                                            f"pressure_headloss_candidate_count={pressure_pool.get('candidate_count', 0)}; "
                                                            "R8k_pressure_conflict_boundary_ready=True"
                                                        ),
                                                        "must_not_do": (
                                                            "不能只在 Agent51 summary 中记录 conflict；必须让控制与 replay 层都看到它，否则冲突证据仍可能被下游策略忽略。"
                                                        ),
                                                        "expected_metrics": [
                                                            "agent49_pressure_source_conflict_control_block",
                                                            "agent52_pressure_source_conflict_replay_blocked_case_count",
                                                            "pressure_source_conflict_requires_operator_review",
                                                            "can_write_to_actuator",
                                                        ],
                                                    }
                                                return {
                                                    "fallback_enabled": True,
                                                    "action_id": "R8k_pressure_headloss_source_conflict_calibration_boundary",
                                                    "title": "建立 pressure/headloss 多来源冲突与校准边界",
                                                    "reason": (
                                                        "Agent51 已能消费 pressure_headloss_event_log，Agent49/52 也已透传压力证据来源；"
                                                        "下一步应处理节点长表压降与事件日志压降不一致时的来源优先级、校准权重和失败边界，"
                                                        "避免同一水力代理出现双源冲突却仍被当成可靠证据。"
                                                    ),
                                                    "trigger_metric": (
                                                        f"pressure_headloss_candidate_count={pressure_pool.get('candidate_count', 0)}; "
                                                        "R8i_agent51_pressure_event_source_ready=True; "
                                                        "R8j_pressure_source_context_propagated=True"
                                                    ),
                                                    "must_not_do": (
                                                        "不能把两个来源简单平均后当成 field-supported；必须保留 source-specific uncertainty、"
                                                        "传感器校准状态和人工复核边界。"
                                                    ),
                                                    "expected_metrics": [
                                                        "pressure_source_conflict_count",
                                                        "pressure_source_priority_policy",
                                                        "pressure_source_uncertainty_weight",
                                                        "conflict_requires_operator_review",
                                                    ],
                                                }
                                            return {
                                                "fallback_enabled": True,
                                                "action_id": "R8j_propagate_agent51_pressure_source_to_agent49_52",
                                                "title": "把 Agent51 pressure/headloss 证据来源透传到 Agent49/52 控制与 replay 上下文",
                                                "reason": (
                                                    "Agent51 已声明可接受 pressure_headloss_event_log 作为床层水力代理来源；"
                                                    "下一步应让 Agent49 reward guardrail 和 Agent52 replay context 都能看到 "
                                                    "accepted_pressure_evidence_sources 与 pressure_headloss_event_source_batch_count。"
                                                ),
                                                "trigger_metric": (
                                                    f"pressure_headloss_candidate_count={pressure_pool.get('candidate_count', 0)}; "
                                                    "R8i_agent51_pressure_event_source_ready=True"
                                                ),
                                                "must_not_do": (
                                                    "不能因为来源字段已透传就放松 catalyst guardrail；它只是解释上下文，仍需 field validation。"
                                                ),
                                                "expected_metrics": [
                                                    "agent49_accepted_pressure_evidence_sources",
                                                    "agent52_accepted_pressure_evidence_sources",
                                                    "pressure_headloss_event_source_batch_count",
                                                    "can_write_to_actuator",
                                                ],
                                            }
                                        return {
                                            "fallback_enabled": True,
                                            "action_id": "R8i_agent51_consume_pressure_headloss_event_log",
                                            "title": "让 Agent51 catalyst proxy holdout 消费 pressure_headloss_event_log",
                                            "reason": (
                                                "Agent44/R7 已能把 pressure/headloss 阻断转成可操作补包项；下一步应减少重复证据轨道，"
                                                "让 Agent51 催化剂弱状态 holdout 可把 pressure_headloss_event_log 作为床层水力代理来源之一，"
                                                "而不是只依赖 node_modality_sensor_timeseries 中的 pressure_drop_kPa。"
                                            ),
                                            "trigger_metric": (
                                                f"pressure_headloss_candidate_count={pressure_pool.get('candidate_count', 0)}; "
                                                "R8g_r7_pressure_headloss_contract_ready=True; "
                                                "R8h_agent44_preflight_diagnostics_ready=True"
                                            ),
                                            "must_not_do": (
                                                "不能把 pressure/headloss 事件本身等同于 catalyst_activity 标签；它只能作为水力代理证据，"
                                                "仍需 QA-passed catalyst_activity 或可接受替代标签校准。"
                                            ),
                                            "expected_metrics": [
                                                "agent51_pressure_headloss_event_source_batch_count",
                                                "accepted_pressure_evidence_sources",
                                                "matched_proxy_holdout_batch_count",
                                                "catalyst_activity_label_requirement_preserved",
                                            ],
                                        }
                                    return {
                                        "fallback_enabled": True,
                                        "action_id": "R8h_agent44_pressure_headloss_preflight_diagnostics",
                                        "title": "把 Agent44 type/linkage 阻断转成 R7 可操作补包诊断",
                                        "reason": (
                                            "R7 minimum replay contract 已显式要求 pressure/headloss 事件；下一步应补齐真实包预检诊断，"
                                            "让 pressure/headloss 的类型错误、缺失床层锚点、lab linkage 和异常标签问题进入 patch plan，"
                                            "否则现场包卡在 Agent44 时仍只能得到笼统阻断。"
                                        ),
                                        "trigger_metric": (
                                            f"pressure_headloss_candidate_count={pressure_pool.get('candidate_count', 0)}; "
                                            "R8e_field_schema_ready=True; R8f_import_gate_pressure_ready=True; "
                                            "R8g_r7_pressure_headloss_contract_ready=True"
                                        ),
                                        "must_not_do": (
                                            "不能因为 R7 contract 已集成 pressure/headloss 就放松 field origin、真实 timestamped rows "
                                            "或人工复核边界。"
                                        ),
                                        "expected_metrics": [
                                            "agent44_blocking_table_statuses",
                                            "agent44_type_error_patch_items",
                                            "pressure_headloss_import_blocker_items",
                                            "coverage_patch_plan_agent44_blocker_item_count",
                                        ],
                                    }
                                return {
                                    "fallback_enabled": True,
                                    "action_id": "R8g_r7_pressure_headloss_minimum_replay_contract",
                                    "title": "把 pressure/headloss 真实导入边界接入 R7 最小 replay/验收链",
                                    "reason": (
                                        "Agent30/42/44 已能表达、回放和导入 pressure/headloss 事件；下一步应让 R7 pipeline "
                                        "显式检查 pressure/headloss matched batch、site topology/bed geometry 和真实 field origin，"
                                        "避免该水力代理停留在 synthetic schema ready。"
                                    ),
                                    "trigger_metric": (
                                        f"pressure_headloss_candidate_count={pressure_pool.get('candidate_count', 0)}; "
                                        "R8e_field_schema_ready=True; R8f_import_gate_pressure_ready=True"
                                    ),
                                    "must_not_do": "不能把 synthetic import gate 通过表验收当成 field-supported；R7 仍必须阻断 non-field origin。",
                                    "expected_metrics": [
                                        "r7_pressure_headloss_minimum_matched_batch_count",
                                        "pressure_headloss_field_origin_ready",
                                        "site_topology_bed_geometry_linkage_ready",
                                        "can_write_to_actuator",
                                    ],
                                }
                            return {
                                "fallback_enabled": True,
                                "action_id": "R8f_agent44_pressure_headloss_import_gate_patch",
                                "title": "让 Agent44 field replay import gate 验收 pressure/headloss 事件表和 batch 锚点",
                                "reason": (
                                    "Agent30/42 已补齐 pressure/headloss 采集与 timestamped replay schema；下一步应让 Agent44 "
                                    "在真实包导入前检查 pressure/headloss 数值类型、布尔标签、batch linkage 和 lab anchor。"
                                ),
                                "trigger_metric": (
                                    f"pressure_headloss_candidate_count={pressure_pool.get('candidate_count', 0)}; "
                                    "R8e_field_schema_ready=True; Agent44_pressure_import_gate_ready=False"
                                ),
                                "must_not_do": "不能因为 Agent44 接受 synthetic rows 就进入 field claim；它只能做导入验收和阻断。",
                                "expected_metrics": [
                                    "pressure_headloss_event_log_import_status",
                                    "pressure_headloss_batch_linkage_status",
                                    "pressure_headloss_type_error_count",
                                    "can_pass_to_timestamped_replay",
                                ],
                            }
                        return {
                            "fallback_enabled": True,
                            "action_id": "R8e_agent30_42_pressure_headloss_field_schema_patch",
                            "title": "把 pressure/headloss replay 边界回写到 field data schema 与时间戳 replay 包",
                            "reason": (
                                "Agent52 已消费 pressure/headloss 控制边界并输出 replay 指标；下一步应把所需的压降/水头损失时序、"
                                "床层几何、matched lab labels 和 operation log 明确写入 Agent30/42/R7 field package schema。"
                            ),
                            "trigger_metric": (
                                f"pressure_headloss_candidate_count={pressure_pool.get('candidate_count', 0)}; "
                                "Agent52_pressure_headloss_boundary_consumed=True"
                            ),
                            "must_not_do": "不能伪造 field rows 或把 synthetic replay 结果写成 field-supported；只能补 schema、模板和验收字段。",
                            "expected_metrics": [
                                "field_schema_pressure_headloss_terms",
                                "timestamped_replay_pressure_headloss_join_keys",
                                "minimum_matched_batch_count",
                                "can_write_to_actuator",
                            ],
                        }
                    return {
                        "fallback_enabled": True,
                        "action_id": "R8d_agent52_pressure_headloss_guardrail_replay_refresh",
                        "title": "让 Agent52 replay 评估消费 Agent49 pressure-headloss 控制边界",
                        "reason": (
                            "Agent54 已把 pressure/headloss 写入软传感候选合同，Agent49 也已把它写成控制 guardrail 边界；"
                            "下一步应由 Agent52 离线 replay 评估这个边界是否影响 reward regret、误保护成本和回流升级阻断。"
                        ),
                        "trigger_metric": (
                            f"pressure_headloss_candidate_count={pressure_pool.get('candidate_count', 0)}; "
                            "R2_FV4_pressure_pool_consumed=True; Agent54_49_pressure_contract_consumed=True"
                        ),
                        "must_not_do": "不能因 pressure/headloss 候选存在就放松 R3G1/R3G2，也不能把 replay refresh 当成 field-supported 控制证据。",
                        "expected_metrics": [
                            "agent52_pressure_headloss_boundary_consumed",
                            "guardrail_aware_regret_delta",
                            "protective_false_positive_cost_delta",
                            "can_write_to_actuator",
                        ],
                    }
                return {
                    "fallback_enabled": True,
                    "action_id": "R8c_agent54_49_consume_pressure_headloss_contract",
                    "title": "让 Agent54/49 消费 Agent48/R2 pressure-headloss 候选合同",
                    "reason": (
                        "Agent48 已把 hard-unresolved hidden states 转成 pressure/headloss 候选池，R2 也已把它写入 "
                        "field validation contract；下一步应让软传感矩阵和多设施控制状态显式消费该候选合同。"
                    ),
                    "trigger_metric": (
                        f"pressure_headloss_candidate_count={pressure_pool.get('candidate_count', 0)}; "
                        "R2_FV4_pressure_pool_consumed=True"
                    ),
                    "must_not_do": "不能把 pressure/headloss 候选视为已安装传感器；只能作为软传感 schema 和控制 guardrail 的待验证输入合同。",
                    "expected_metrics": [
                        "agent54_pressure_headloss_contract_consumption",
                        "agent49_catalyst_state_visibility_boundary",
                        "can_write_to_actuator",
                        "field_validation_required",
                    ],
                }
            if pressure_pool_ready:
                return {
                    "fallback_enabled": True,
                    "action_id": "R8b_backprop_pressure_headloss_candidate_pool_to_R2",
                    "title": "把 Agent48 pressure/headloss 候选池写入 R2 field validation contract",
                    "reason": (
                        "Agent48 已形成 pressure/headloss 候选池，但 R2 observation contract 尚未显式消费该候选池。"
                    ),
                    "trigger_metric": (
                        f"pressure_headloss_candidate_count={pressure_pool.get('candidate_count', 0)}; "
                        "R2_FV4_pressure_pool_consumed=False"
                    ),
                    "must_not_do": "不能把候选池直接变成现场布点或 field-supported 结论。",
                    "expected_metrics": [
                        "R2_FV4_presence",
                        "pressure_headloss_candidate_ids",
                        "minimum_matched_batch_count",
                    ],
                }
            return {
                "fallback_enabled": True,
                "action_id": "R8b_agent48_pressure_headloss_candidate_pool_design",
                "title": "把 Agent48 hard-unresolved hidden states 转成 pressure/headloss 与 field-label 候选池设计",
                "reason": (
                    "R7a 需要外部真实包；当前可在模型内部继续推进的是把 Agent48 hidden-state ledger 中的 "
                    f"{hard_unresolved} 转成更明确的候选模态、现场字段和下游契约。"
                ),
                "trigger_metric": (
                    f"agent48_hidden_state_patch_status={patch.get('patch_status', 'unknown')}; "
                    f"hard_unresolved_hidden_states={','.join(hard_unresolved)}"
                ),
                "must_not_do": "不能把新增 pressure/headloss 候选当成 field-supported evidence；只能作为 design-prior 候选池和 R7j 字段需求。",
                "expected_metrics": [
                    "agent48_hidden_state_hard_unresolved_count",
                    "pressure_headloss_candidate_count",
                    "R2_FV4_presence",
                    "field_validation_required",
                ],
            }
        if ledger:
            return {
                "fallback_enabled": True,
                "action_id": "R8_agent48_hidden_state_requirement_ledger_followthrough",
                "title": "把 Agent48 hidden-state requirement ledger 接入 R2/R54/R49 消费链",
                "reason": "R7a 等真实包时，继续确保观测账本不只停留在 Agent48 输出，而是被软传感和控制层消费。",
                "trigger_metric": f"agent48_hidden_state_ledger_status={ledger.get('ledger_status', 'unknown')}",
                "must_not_do": "不能新增展示材料；必须改善观测、估计或控制链路。",
                "expected_metrics": [
                    "R2_consumes_agent48_hidden_state_ledger",
                    "agent54_hidden_state_contract_consumption",
                    "agent49_state_visibility_patch",
                ],
            }
        return {
            "fallback_enabled": True,
            "action_id": "R8_create_agent48_hidden_state_requirement_ledger",
            "title": "建立 Agent48 hidden-state requirement ledger",
            "reason": "R7a 等真实包时，先补足低成本稀疏感知到隐藏状态估计的可机读需求账本。",
            "trigger_metric": "agent48_hidden_state_ledger_missing",
            "must_not_do": "不能只写文字复盘；必须输出可机读 ledger 和测试。",
            "expected_metrics": [
                "hidden_state_requirement_ledger_status",
                "ready_hidden_state_count",
                "minimum_cost_requirement_patch_status",
            ],
        }

    def _source_basis_completion_rate(self) -> float:
        unified_metrics = self.core_metrics.get("unified_field_evidence_gate_metrics", {})
        unified_readiness = unified_metrics.get("readiness", {}) if isinstance(unified_metrics, dict) else {}
        if "source_basis_completion_rate" in unified_readiness:
            return float(unified_readiness.get("source_basis_completion_rate", 0.0))
        claim_metrics = self.core_metrics.get("claim_specific_field_package_metrics", {})
        readiness = claim_metrics.get("readiness", {}) if isinstance(claim_metrics, dict) else {}
        return float(readiness.get("source_basis_completion_rate", 0.45))

    def _citation_detail_completion_rate(self) -> float:
        unified_metrics = self.core_metrics.get("unified_field_evidence_gate_metrics", {})
        unified_readiness = unified_metrics.get("readiness", {}) if isinstance(unified_metrics, dict) else {}
        if "citation_detail_completion_rate" in unified_readiness:
            return float(unified_readiness.get("citation_detail_completion_rate", 0.0))
        return 0.0

    def _unified_gate_ready(self) -> bool:
        unified_metrics = self.core_metrics.get("unified_field_evidence_gate_metrics", {})
        readiness = unified_metrics.get("readiness", {}) if isinstance(unified_metrics, dict) else {}
        return (
            readiness.get("unified_field_evidence_gate_status") == "unified_gate_ready_blocking_field_claim_upgrade"
            and float(readiness.get("gate_source_consolidation_coverage", 0.0)) >= 1.0
        )

    def _joint_action_accuracy(self) -> float:
        replay_metrics = self.core_metrics.get("replay_evaluation_metrics", {})
        offline = replay_metrics.get("offline_evaluation_metrics", {}) if isinstance(replay_metrics, dict) else {}
        return float(offline.get("joint_action_accuracy", 0.667))

    def _weak_state_coverage(self) -> float:
        sparse_metrics = self.core_metrics.get("agent48_metrics", {})
        coverage = sparse_metrics.get("coverage", {}) if isinstance(sparse_metrics, dict) else {}
        return float(coverage.get("weak_state_coverage", 0.300))

    def _agent48_hidden_state_requirement_ledger(self) -> dict[str, object]:
        sparse_metrics = self.core_metrics.get("agent48_metrics", {})
        ledger = sparse_metrics.get("hidden_state_requirement_ledger", {}) if isinstance(sparse_metrics, dict) else {}
        return ledger if isinstance(ledger, dict) else {}

    def _r2_pressure_headloss_candidate_pool_consumed(self) -> bool:
        metrics = self.core_metrics.get("observation_contract_metrics", {})
        if not isinstance(metrics, dict):
            return False
        readiness = metrics.get("readiness", {})
        readiness = readiness if isinstance(readiness, dict) else {}
        if str(readiness.get("agent48_pressure_headloss_candidate_pool_status", "")).startswith(
            "pressure_headloss_candidate_pool_ready"
        ) and int(readiness.get("agent48_pressure_headloss_candidate_count", 0) or 0) > 0:
            return True
        requirements = metrics.get("field_validation_requirements", [])
        requirements = requirements if isinstance(requirements, list) else []
        for requirement in requirements:
            if not isinstance(requirement, dict):
                continue
            if requirement.get("requirement_id") != "R2_FV4_agent48_hidden_state_requirement_patch":
                continue
            if requirement.get("pressure_headloss_candidate_ids"):
                return True
        return False

    def _agent54_49_pressure_headloss_contract_consumed(self) -> bool:
        soft_metrics = self.core_metrics.get("soft_sensor_matrix_metrics", {})
        soft_metrics = soft_metrics if isinstance(soft_metrics, dict) else {}
        soft_readiness = soft_metrics.get("readiness", {})
        soft_readiness = soft_readiness if isinstance(soft_readiness, dict) else {}
        soft_contract = soft_metrics.get("feature_contract", {})
        soft_contract = soft_contract if isinstance(soft_contract, dict) else {}
        pressure_contract = soft_contract.get("pressure_headloss_candidate_contract", {})
        pressure_contract = pressure_contract if isinstance(pressure_contract, dict) else {}
        agent54_consumed = (
            int(
                soft_readiness.get(
                    "pressure_headloss_candidate_count",
                    pressure_contract.get("candidate_count", 0),
                )
                or 0
            )
            > 0
            and str(
                soft_readiness.get(
                    "pressure_headloss_candidate_pool_status",
                    pressure_contract.get("pool_status", ""),
                )
            ).startswith("pressure_headloss_candidate_pool_ready")
        )
        control_metrics = self.core_metrics.get("collaborative_control_metrics", {})
        control_metrics = control_metrics if isinstance(control_metrics, dict) else {}
        guardrail = control_metrics.get("control_replay_guardrail_context", {})
        guardrail = guardrail if isinstance(guardrail, dict) else {}
        sparse_context = control_metrics.get("sparse_context", {})
        sparse_context = sparse_context if isinstance(sparse_context, dict) else {}
        observation_context = sparse_context.get("observation_contract_context", {})
        observation_context = observation_context if isinstance(observation_context, dict) else {}
        agent49_consumed = bool(
            guardrail.get(
                "pressure_headloss_consumed_by_agent49",
                observation_context.get("pressure_headloss_consumed_by_agent49", False),
            )
        ) and int(
            guardrail.get(
                "pressure_headloss_candidate_count",
                observation_context.get("pressure_headloss_candidate_count", 0),
            )
            or 0
        ) > 0
        return agent54_consumed and agent49_consumed

    def _agent52_pressure_headloss_boundary_consumed(self) -> bool:
        replay_metrics = self.core_metrics.get("replay_evaluation_metrics", {})
        replay_metrics = replay_metrics if isinstance(replay_metrics, dict) else {}
        offline = replay_metrics.get("offline_evaluation_metrics", {})
        offline = offline if isinstance(offline, dict) else {}
        readiness = replay_metrics.get("readiness", {})
        readiness = readiness if isinstance(readiness, dict) else {}
        return bool(
            offline.get(
                "pressure_headloss_boundary_consumed",
                readiness.get("pressure_headloss_boundary_consumed", False),
            )
        ) and int(offline.get("pressure_headloss_candidate_count", readiness.get("pressure_headloss_candidate_count", 0)) or 0) > 0

    def _r8e_pressure_headloss_field_schema_ready(self) -> bool:
        field_metrics = self._nested_metrics("field_data_interface_metrics", "field_data_interface")
        timestamp_metrics = self._nested_metrics("timestamped_campaign_replay_metrics", "timestamped_campaign_replay")
        field_schema = field_metrics.get("schema_contract", {}) if isinstance(field_metrics, dict) else {}
        field_headers = field_metrics.get("template_headers", {}) if isinstance(field_metrics, dict) else {}
        timestamp_schema = timestamp_metrics.get("replay_schema_contract", {}) if isinstance(timestamp_metrics, dict) else {}
        timestamp_headers = timestamp_metrics.get("template_headers", {}) if isinstance(timestamp_metrics, dict) else {}
        replay = timestamp_metrics.get("replay_metrics", {}) if isinstance(timestamp_metrics, dict) else {}
        linkage = timestamp_metrics.get("linkage", {}) if isinstance(timestamp_metrics, dict) else {}
        field_ready = (
            "site_topology_or_bed_geometry" in field_schema
            and "pressure_drop_kPa" in _list(field_headers.get("sensor_timeseries", []))
            and "headloss_kPa_per_m" in _list(field_headers.get("sensor_timeseries", []))
            and "pressure_headloss_review_required" in _list(field_headers.get("campaign_operation_log", []))
        )
        timestamp_ready = (
            "pressure_headloss_event_log" in timestamp_schema
            and "pressure_drop_kPa" in _list(timestamp_headers.get("sensor_timeseries", []))
            and int(replay.get("pressure_headloss_event_count", 0) or 0) > 0
            and int(replay.get("pressure_headloss_matched_batch_count", 0) or 0) > 0
            and not _list(linkage.get("pressure_headloss_without_lab_batches", []))
        )
        return field_ready and timestamp_ready

    def _r8f_pressure_headloss_import_gate_ready(self) -> bool:
        metrics = self._nested_metrics("field_replay_import_metrics")
        table_audit = metrics.get("table_import_audit", {}) if isinstance(metrics, dict) else {}
        pressure_audit = table_audit.get("pressure_headloss_event_log", {}) if isinstance(table_audit, dict) else {}
        linkage = metrics.get("linkage_audit", {}) if isinstance(metrics, dict) else {}
        readiness = metrics.get("readiness", {}) if isinstance(metrics, dict) else {}
        return (
            pressure_audit.get("status") == "import_ready"
            and int(linkage.get("pressure_headloss_batch_count", 0) or 0) > 0
            and not _list(linkage.get("pressure_headloss_without_lab_batches", []))
            and int(readiness.get("accepted_table_count", 0) or 0) >= int(readiness.get("total_table_count", 1) or 1)
        )

    def _r8g_pressure_headloss_r7_contract_ready(self) -> bool:
        metrics = self.core_metrics.get("r7_real_field_replay_pipeline_metrics", {})
        metrics = metrics if isinstance(metrics, dict) else {}
        coverage = metrics.get("field_package_coverage", {})
        coverage = coverage if isinstance(coverage, dict) else {}
        contract = coverage.get("minimum_replay_contract_audit", {})
        contract = contract if isinstance(contract, dict) else {}
        readiness = metrics.get("pipeline_readiness", {})
        readiness = readiness if isinstance(readiness, dict) else {}
        required_tables = _list(contract.get("required_tables"))
        row_counts = contract.get("table_row_counts", {})
        row_counts = row_counts if isinstance(row_counts, dict) else {}
        return (
            "pressure_headloss_event_log" in required_tables
            and "pressure_headloss_event_log" in row_counts
            and "pressure_headloss_event_count" in contract
            and "valid_pressure_headloss_event_count" in contract
            and "valid_pressure_headloss_batch_count" in contract
            and "minimum_pressure_headloss_event_count" in readiness
            and "minimum_valid_pressure_headloss_event_count" in readiness
            and "minimum_valid_pressure_headloss_batch_count" in readiness
        )

    def _r8h_agent44_pressure_headloss_preflight_diagnostics_ready(self) -> bool:
        metrics = self.core_metrics.get("r7_real_field_replay_pipeline_metrics", {})
        metrics = metrics if isinstance(metrics, dict) else {}
        preflight = metrics.get("preflight", {})
        preflight = preflight if isinstance(preflight, dict) else {}
        patch_plan = _dict(_dict(metrics.get("field_package_coverage", {})).get("patch_plan"))
        return (
            "agent44_blocking_table_statuses" in preflight
            and "agent44_type_error_count" in preflight
            and "agent44_type_error_tables" in preflight
            and "agent44_required_field_blockers" in preflight
            and "agent44_linkage_blockers" in preflight
            and "patch_plan_status" in patch_plan
        )

    def _r8i_agent51_pressure_headloss_event_log_ready(self) -> bool:
        metrics = self.core_metrics.get("catalyst_proxy_metrics", {})
        metrics = metrics if isinstance(metrics, dict) else {}
        readiness = metrics.get("readiness", {})
        readiness = readiness if isinstance(readiness, dict) else {}
        summary = metrics.get("field_proxy_holdout_summary", {})
        summary = summary if isinstance(summary, dict) else {}
        method = metrics.get("method_contract", {})
        method = method if isinstance(method, dict) else {}
        contract_sources = _list(readiness.get("pressure_evidence_source_contract"))
        data_needs = _list(method.get("data_needs"))
        return (
            "pressure_headloss_event_log" in contract_sources
            or "pressure_headloss_event_log.pressure_drop_kPa" in data_needs
        ) and (
            "accepted_pressure_evidence_sources" in summary
            or "pressure_headloss_event_source_batch_count" in readiness
        )

    def _r8j_pressure_source_propagated_to_control_replay(self) -> bool:
        control_metrics = self.core_metrics.get("collaborative_control_metrics", {})
        control_metrics = control_metrics if isinstance(control_metrics, dict) else {}
        guardrail_context = control_metrics.get("control_replay_guardrail_context", {})
        guardrail_context = guardrail_context if isinstance(guardrail_context, dict) else {}
        replay_metrics = self.core_metrics.get("replay_evaluation_metrics", {})
        replay_metrics = replay_metrics if isinstance(replay_metrics, dict) else {}
        catalyst_context = replay_metrics.get("catalyst_proxy_context", {})
        catalyst_context = catalyst_context if isinstance(catalyst_context, dict) else {}
        return (
            "accepted_pressure_evidence_sources" in guardrail_context
            and "pressure_headloss_event_source_batch_count" in guardrail_context
            and "accepted_pressure_evidence_sources" in catalyst_context
            and "pressure_headloss_event_source_batch_count" in catalyst_context
        )

    def _r8k_pressure_source_conflict_boundary_ready(self) -> bool:
        metrics = self.core_metrics.get("catalyst_proxy_metrics", {})
        metrics = metrics if isinstance(metrics, dict) else {}
        summary = _dict(metrics.get("field_proxy_holdout_summary", {}))
        return (
            "pressure_source_priority_policy" in summary
            and "pressure_source_conflict_count" in summary
            and "pressure_source_conflicts" in summary
            and "conflict_requires_operator_review" in summary
        )

    def _r8l_pressure_conflict_control_replay_ready(self) -> bool:
        control_metrics = self.core_metrics.get("collaborative_control_metrics", {})
        control_metrics = control_metrics if isinstance(control_metrics, dict) else {}
        guardrail_context = _dict(control_metrics.get("control_replay_guardrail_context", {}))
        replay_metrics = self.core_metrics.get("replay_evaluation_metrics", {})
        replay_metrics = replay_metrics if isinstance(replay_metrics, dict) else {}
        offline = _dict(replay_metrics.get("offline_evaluation_metrics", {}))
        readiness = _dict(replay_metrics.get("readiness", {}))
        writeback = _dict(_dict(replay_metrics.get("agent49_writeback", {})).get("metric_patch", {}))
        return (
            "pressure_source_conflict_count" in guardrail_context
            and "pressure_source_conflict_control_block" in guardrail_context
            and "conflict_requires_operator_review" in guardrail_context
            and "pressure_source_conflict_count" in offline
            and "pressure_source_conflict_replay_blocked_case_count" in offline
            and "pressure_source_conflict_requires_operator_review" in readiness
            and "pressure_source_conflict_requires_operator_review" in writeback
        )

    def _r8m_pressure_conflict_field_patch_ready(self) -> bool:
        metrics = self.core_metrics.get("r7_real_field_replay_pipeline_metrics", {})
        metrics = metrics if isinstance(metrics, dict) else {}
        readiness = _dict(metrics.get("pipeline_readiness", {}))
        coverage = _dict(metrics.get("field_package_coverage", {}))
        coverage_readiness = _dict(coverage.get("readiness", {}))
        patch_plan = _dict(coverage.get("patch_plan", {}))
        patch_items = _list(patch_plan.get("items"))
        has_conflict_patch_item = any(
            _dict(item).get("item_id") == "R8M_PRESSURE_SOURCE_CONFLICT_FIELD_PATCH"
            for item in patch_items
        )
        pressure_conflict_count = int(
            readiness.get("pressure_source_conflict_count", coverage_readiness.get("pressure_source_conflict_count", 0))
            or 0
        )
        resolved_conflict_count = int(
            readiness.get(
                "resolved_pressure_source_conflict_count",
                coverage_readiness.get("resolved_pressure_source_conflict_count", 0),
            )
            or 0
        )
        has_resolved_conflict_clearance = pressure_conflict_count > 0 and resolved_conflict_count > 0
        has_resolution_schema = (
            "pressure_source_conflict_count" in readiness
            and "pressure_source_conflict_requires_operator_review" in readiness
            and "resolved_pressure_source_conflict_count" in readiness
            and "unresolved_pressure_source_conflict_count" in readiness
            and "pressure_source_resolution_record_count" in readiness
            and "field_package_pressure_conflict_resolution_status" in readiness
            and "field_package_pressure_conflict_resolution_ready" in readiness
            and "pressure_source_conflict_count" in coverage_readiness
            and "pressure_source_conflict_requires_operator_review" in coverage_readiness
            and "resolved_pressure_source_conflict_count" in coverage_readiness
            and "unresolved_pressure_source_conflict_count" in coverage_readiness
        )
        return has_resolution_schema and (
            has_conflict_patch_item
            or has_resolved_conflict_clearance
            or str(patch_plan.get("patch_plan_status", ""))
            == "patch_plan_requires_pressure_source_conflict_resolution"
            or str(
                readiness.get(
                    "field_package_pressure_conflict_resolution_status",
                    coverage_readiness.get("field_package_pressure_conflict_resolution_status", ""),
                )
            )
            == "pressure_source_conflict_resolution_clear"
        )

    def _r8n_pressure_resolution_replay_clearance_ready(self) -> bool:
        control_metrics = self.core_metrics.get("collaborative_control_metrics", {})
        control_metrics = control_metrics if isinstance(control_metrics, dict) else {}
        guardrail_context = _dict(control_metrics.get("control_replay_guardrail_context", {}))
        replay_metrics = self.core_metrics.get("replay_evaluation_metrics", {})
        replay_metrics = replay_metrics if isinstance(replay_metrics, dict) else {}
        offline = _dict(replay_metrics.get("offline_evaluation_metrics", {}))
        readiness = _dict(replay_metrics.get("readiness", {}))
        writeback = _dict(_dict(replay_metrics.get("agent49_writeback", {})).get("metric_patch", {}))
        pressure_context = _dict(replay_metrics.get("pressure_headloss_context", {}))
        return (
            "resolved_pressure_source_conflict_count" in guardrail_context
            and "unresolved_pressure_source_conflict_count" in guardrail_context
            and "pressure_source_resolution_record_count" in guardrail_context
            and "resolved_pressure_source_conflict_count" in offline
            and "unresolved_pressure_source_conflict_count" in offline
            and "pressure_source_resolution_record_count" in offline
            and "resolved_pressure_source_conflict_count" in readiness
            and "unresolved_pressure_source_conflict_count" in readiness
            and "pressure_source_conflict_clear" in readiness
            and "resolved_pressure_source_conflict_count" in writeback
            and "unresolved_pressure_source_conflict_count" in writeback
            and "pressure_source_resolution_record_count" in writeback
            and "resolved_pressure_source_conflict_count" in pressure_context
            and "unresolved_pressure_source_conflict_count" in pressure_context
            and "pressure_source_resolution_record_count" in pressure_context
        )

    def _r8o_pressure_resolution_scenario_pack_ready(self) -> bool:
        metrics = self.core_metrics.get("pressure_resolution_replay_scenario_pack_metrics", {})
        metrics = metrics if isinstance(metrics, dict) else {}
        readiness = _dict(metrics.get("readiness", {}))
        return (
            str(readiness.get("scenario_pack_status", "")).startswith("pressure_resolution_scenario_pack")
            and float(readiness.get("scenario_schema_coverage", 0.0)) >= 1.0
            and bool(readiness.get("source_chain_resolution_fields_ready", False))
            and bool(readiness.get("can_update_agent60_fallback", False))
        )

    def _r8p_pressure_resolution_rows_accepted(self) -> bool:
        metrics = self.core_metrics.get("pressure_resolution_replay_scenario_pack_metrics", {})
        metrics = metrics if isinstance(metrics, dict) else {}
        readiness = _dict(metrics.get("readiness", {}))
        field_acceptance = _dict(metrics.get("field_row_acceptance", {}))
        routing = _dict(metrics.get("field_rows_downstream_routing_preflight", {}))
        handoff = _dict(metrics.get("field_rows_downstream_route_handoff", {}))
        target_gate_preflight = _dict(metrics.get("field_rows_downstream_target_gate_preflight", {}))
        return (
            str(readiness.get("scenario_pack_status", ""))
            == "pressure_resolution_scenario_pack_field_replay_ready_for_human_review"
            and float(readiness.get("field_scenario_coverage", 0.0)) >= 1.0
            and bool(readiness.get("source_chain_resolution_fields_ready", False))
            and str(field_acceptance.get("field_row_acceptance_status", ""))
            == "field_replay_rows_accepted_for_all_scenarios"
            and int(field_acceptance.get("accepted_scenario_count", 0) or 0) >= 5
            and str(readiness.get("next_recommended_core_action", ""))
            == "R8v_route_pressure_resolution_rows_to_field_replay_and_holdout_gates"
            and str(routing.get("field_rows_downstream_routing_preflight_status", ""))
            == "downstream_routing_preflight_passed_ready_for_r8v_field_replay_and_holdout_gates"
            and bool(routing.get("can_route_to_r8v", False))
            and int(routing.get("routing_ready_target_count", 0) or 0) >= 4
            and str(handoff.get("downstream_route_handoff_status", ""))
            == "downstream_route_handoff_ready_for_r8v_target_gates"
            and bool(handoff.get("can_route_to_r8v", False))
            and int(handoff.get("ready_handoff_target_count", 0) or 0) >= 4
            and not bool(handoff.get("can_write_to_actuator", True))
            and not bool(handoff.get("can_write_to_release_gate", True))
            and str(target_gate_preflight.get("downstream_target_gate_preflight_status", ""))
            == "downstream_target_gate_preflight_ready_for_r8v_execution"
            and bool(target_gate_preflight.get("can_execute_all_target_gates", False))
            and int(target_gate_preflight.get("ready_target_gate_count", 0) or 0) >= 4
            and not bool(target_gate_preflight.get("can_write_to_actuator", True))
            and not bool(target_gate_preflight.get("can_write_to_release_gate", True))
        )

    def _r8p_pressure_resolution_patch_plan(self) -> dict[str, object]:
        metrics = self.core_metrics.get("pressure_resolution_replay_scenario_pack_metrics", {})
        metrics = metrics if isinstance(metrics, dict) else {}
        patch_plan = _dict(metrics.get("field_rows_patch_plan", {}))
        status = str(patch_plan.get("field_rows_patch_plan_status", ""))
        if not status:
            return {}
        return patch_plan

    def _r8p_pressure_resolution_operator_handoff(self) -> dict[str, object]:
        metrics = self.core_metrics.get("pressure_resolution_replay_scenario_pack_metrics", {})
        metrics = metrics if isinstance(metrics, dict) else {}
        handoff = _dict(metrics.get("field_rows_operator_handoff", {}))
        status = str(handoff.get("field_rows_operator_handoff_status", ""))
        if not status:
            return {}
        return handoff

    def _r8v_pressure_resolution_downstream_route_handoff(self) -> dict[str, object]:
        metrics = self.core_metrics.get("pressure_resolution_replay_scenario_pack_metrics", {})
        metrics = metrics if isinstance(metrics, dict) else {}
        handoff = _dict(metrics.get("field_rows_downstream_route_handoff", {}))
        status = str(handoff.get("downstream_route_handoff_status", ""))
        if not status:
            return {}
        return handoff

    def _r8v_pressure_resolution_downstream_target_gate_preflight(self) -> dict[str, object]:
        metrics = self.core_metrics.get("pressure_resolution_replay_scenario_pack_metrics", {})
        metrics = metrics if isinstance(metrics, dict) else {}
        preflight = _dict(metrics.get("field_rows_downstream_target_gate_preflight", {}))
        status = str(preflight.get("downstream_target_gate_preflight_status", ""))
        if not status:
            return {}
        return preflight

    def _r8v_pressure_resolution_downstream_target_gate_result_preflight(self) -> dict[str, object]:
        metrics = self.core_metrics.get("pressure_resolution_replay_scenario_pack_metrics", {})
        metrics = metrics if isinstance(metrics, dict) else {}
        preflight = _dict(metrics.get("field_rows_downstream_target_gate_result_preflight", {}))
        status = str(preflight.get("downstream_target_gate_result_preflight_status", ""))
        if not status:
            return {}
        return preflight

    def _r8v_pressure_resolution_downstream_target_gate_result_arbitration(self) -> dict[str, object]:
        metrics = self.core_metrics.get("pressure_resolution_replay_scenario_pack_metrics", {})
        metrics = metrics if isinstance(metrics, dict) else {}
        arbitration = _dict(metrics.get("field_rows_downstream_target_gate_result_arbitration", {}))
        status = str(arbitration.get("downstream_target_gate_result_arbitration_status", ""))
        if not status:
            return {}
        return arbitration

    def _r8v_pressure_resolution_downstream_target_gate_operator_review_preflight(self) -> dict[str, object]:
        metrics = self.core_metrics.get("pressure_resolution_replay_scenario_pack_metrics", {})
        metrics = metrics if isinstance(metrics, dict) else {}
        preflight = _dict(metrics.get("field_rows_downstream_target_gate_operator_review_preflight", {}))
        status = str(preflight.get("downstream_target_gate_operator_review_preflight_status", ""))
        if not status:
            return {}
        return preflight

    def _r8v_pressure_resolution_downstream_target_gate_post_review_gate(self) -> dict[str, object]:
        metrics = self.core_metrics.get("pressure_resolution_replay_scenario_pack_metrics", {})
        metrics = metrics if isinstance(metrics, dict) else {}
        gate = _dict(metrics.get("field_rows_downstream_target_gate_post_review_gate", {}))
        status = str(gate.get("downstream_target_gate_post_review_gate_status", ""))
        if not status:
            return {}
        return gate

    def _r8v_pressure_resolution_downstream_target_gate_protective_candidate_evaluation(self) -> dict[str, object]:
        metrics = self.core_metrics.get("pressure_resolution_replay_scenario_pack_metrics", {})
        metrics = metrics if isinstance(metrics, dict) else {}
        evaluation = _dict(
            metrics.get("field_rows_downstream_target_gate_protective_candidate_evaluation", {})
        )
        status = str(evaluation.get("downstream_target_gate_protective_candidate_evaluation_status", ""))
        if not status:
            return {}
        return evaluation

    def _r8p_pressure_resolution_r7_completion_plan(self) -> dict[str, object]:
        metrics = self.core_metrics.get("pressure_resolution_replay_scenario_pack_metrics", {})
        metrics = metrics if isinstance(metrics, dict) else {}
        completion_plan = _dict(metrics.get("field_rows_r7_completion_plan", {}))
        status = str(completion_plan.get("completion_plan_status", ""))
        if not status:
            return {}
        return completion_plan

    def _r8p_pressure_resolution_r7_completion_route_contracts(self) -> dict[str, object]:
        metrics = self.core_metrics.get("pressure_resolution_replay_scenario_pack_metrics", {})
        metrics = metrics if isinstance(metrics, dict) else {}
        route_contracts = _dict(metrics.get("field_rows_r7_completion_route_contracts", {}))
        status = str(route_contracts.get("completion_route_contracts_status", ""))
        if not status:
            return {}
        return route_contracts

    def _r8p_pressure_resolution_r7_completion_route_work_packages(self) -> dict[str, object]:
        metrics = self.core_metrics.get("pressure_resolution_replay_scenario_pack_metrics", {})
        metrics = metrics if isinstance(metrics, dict) else {}
        work_packages = _dict(metrics.get("field_rows_r7_completion_route_work_packages", {}))
        status = str(work_packages.get("route_work_packages_status", ""))
        if not status:
            return {}
        return work_packages

    def _r8p_pressure_resolution_r7_completion_route_work_package_templates(self) -> dict[str, object]:
        metrics = self.core_metrics.get("pressure_resolution_replay_scenario_pack_metrics", {})
        metrics = metrics if isinstance(metrics, dict) else {}
        templates = _dict(metrics.get("field_rows_r7_completion_route_work_package_templates", {}))
        status = str(templates.get("route_work_package_templates_status", ""))
        if not status:
            return {}
        return templates

    def _r8p_pressure_resolution_r7_completion_route_work_package_preflight(self) -> dict[str, object]:
        metrics = self.core_metrics.get("pressure_resolution_replay_scenario_pack_metrics", {})
        metrics = metrics if isinstance(metrics, dict) else {}
        preflight = _dict(metrics.get("field_rows_r7_completion_route_work_package_preflight", {}))
        status = str(preflight.get("route_work_package_preflight_status", ""))
        if not status:
            return {}
        return preflight

    def _r8p_pressure_resolution_r7_completion_route_work_package_patch_plan(self) -> dict[str, object]:
        metrics = self.core_metrics.get("pressure_resolution_replay_scenario_pack_metrics", {})
        metrics = metrics if isinstance(metrics, dict) else {}
        patch_plan = _dict(metrics.get("field_rows_r7_completion_route_work_package_patch_plan", {}))
        status = str(patch_plan.get("route_work_package_patch_plan_status", ""))
        if not status:
            return {}
        return patch_plan

    def _r8p_pressure_resolution_r7_completion_route_work_package_assembly_gate(self) -> dict[str, object]:
        metrics = self.core_metrics.get("pressure_resolution_replay_scenario_pack_metrics", {})
        metrics = metrics if isinstance(metrics, dict) else {}
        assembly_gate = _dict(metrics.get("field_rows_r7_completion_route_work_package_assembly_gate", {}))
        status = str(assembly_gate.get("route_work_package_assembly_gate_status", ""))
        if not status:
            return {}
        return assembly_gate

    def _r8p_pressure_resolution_submission_readiness_review(self) -> dict[str, object]:
        metrics = self.core_metrics.get("pressure_resolution_replay_scenario_pack_metrics", {})
        metrics = metrics if isinstance(metrics, dict) else {}
        review = _dict(metrics.get("field_rows_submission_readiness_review", {}))
        status = str(review.get("submission_readiness_review_status", ""))
        if not status:
            return {}
        return review

    def _r8p_pressure_resolution_source_package_route_guide(self) -> dict[str, object]:
        metrics = self.core_metrics.get("pressure_resolution_replay_scenario_pack_metrics", {})
        metrics = metrics if isinstance(metrics, dict) else {}
        guide = _dict(metrics.get("field_rows_source_package_submission_route_guide", {}))
        status = str(guide.get("source_package_submission_route_guide_status", ""))
        if not status:
            return {}
        return guide

    def _r8p_pressure_resolution_source_package_route_preflight(self) -> dict[str, object]:
        metrics = self.core_metrics.get("pressure_resolution_replay_scenario_pack_metrics", {})
        metrics = metrics if isinstance(metrics, dict) else {}
        preflight = _dict(metrics.get("field_rows_source_package_route_preflight", {}))
        status = str(preflight.get("source_package_route_preflight_status", ""))
        if not status:
            return {}
        return preflight

    def _nested_metrics(self, key: str, nested_key: str | None = None) -> dict[str, object]:
        metrics = self.core_metrics.get(key, {})
        if not isinstance(metrics, dict):
            return {}
        if nested_key is None:
            return metrics
        nested = metrics.get(nested_key, {})
        nested = nested if isinstance(nested, dict) else {}
        payload = nested.get("metrics", nested)
        return payload if isinstance(payload, dict) else {}

    def _observation_contract_ready(self) -> bool:
        metrics = self.core_metrics.get("observation_contract_metrics", {})
        readiness = metrics.get("readiness", {}) if isinstance(metrics, dict) else {}
        return (
            str(readiness.get("observation_contract_status", "")).startswith("synthetic_observation_contract_ready")
            and bool(readiness.get("budget_pass", False))
            and float(readiness.get("proxy_enhanced_weak_state_coverage", 0.0)) >= 0.55
        )

    def _observation_contract_weak_state(self) -> float:
        metrics = self.core_metrics.get("observation_contract_metrics", {})
        readiness = metrics.get("readiness", {}) if isinstance(metrics, dict) else {}
        return float(readiness.get("proxy_enhanced_weak_state_coverage", 0.0))

    def _control_replay_stress_ready(self) -> bool:
        metrics = self.core_metrics.get("control_replay_stress_metrics", {})
        readiness = metrics.get("readiness", {}) if isinstance(metrics, dict) else {}
        return (
            str(readiness.get("control_replay_stress_status", "")).startswith("synthetic_counterfactual_stress_ready")
            and bool(readiness.get("can_update_agent49_reward_prior", False))
        )

    def _control_replay_guardrail_accuracy(self) -> float:
        metrics = self.core_metrics.get("control_replay_stress_metrics", {})
        counterfactual = metrics.get("counterfactual_metrics", {}) if isinstance(metrics, dict) else {}
        guardrail = counterfactual.get("guardrail_candidate", {}) if isinstance(counterfactual, dict) else {}
        return float(guardrail.get("joint_action_accuracy", 0.0))

    def _control_replay_guardrails_integrated(self) -> bool:
        metrics = self.core_metrics.get("collaborative_control_metrics", {})
        readiness = metrics.get("readiness", {}) if isinstance(metrics, dict) else {}
        context = metrics.get("control_replay_guardrail_context", {}) if isinstance(metrics, dict) else {}
        return bool(readiness.get("control_replay_guardrails_integrated", False)) and bool(
            context.get("reward_prior_guardrail_available", False)
        )

    def _guardrail_aware_replay_ready(self) -> bool:
        metrics = self.core_metrics.get("replay_evaluation_metrics", {})
        offline = metrics.get("offline_evaluation_metrics", {}) if isinstance(metrics, dict) else {}
        readiness = metrics.get("readiness", {}) if isinstance(metrics, dict) else {}
        return bool(readiness.get("guardrail_aware_replay_ready", False)) and bool(
            offline.get("control_replay_guardrails_integrated", False)
        )

    def _guardrail_aware_regret_delta(self) -> float:
        metrics = self.core_metrics.get("replay_evaluation_metrics", {})
        offline = metrics.get("offline_evaluation_metrics", {}) if isinstance(metrics, dict) else {}
        return float(offline.get("guardrail_aware_regret_delta", 0.0))

    def _guardrail_backpropagation_ready(self) -> bool:
        metrics = self.core_metrics.get("control_guardrail_backpropagation_metrics", {})
        readiness = metrics.get("readiness", {}) if isinstance(metrics, dict) else {}
        return bool(readiness.get("backpropagation_ready", False))

    def _guardrail_backpropagation_mechanism_coverage(self) -> float:
        metrics = self.core_metrics.get("control_guardrail_backpropagation_metrics", {})
        coverage = metrics.get("coverage_metrics", {}) if isinstance(metrics, dict) else {}
        return float(coverage.get("resolved_case_to_mechanism_coverage", 0.0))

    def _guardrail_patch_consumption_ready(self) -> bool:
        agent53 = self._readiness_float(
            "minimal_grey_box_physics_metrics",
            "agent53_guardrail_boundary_consumption_rate",
        )
        agent58 = self._readiness_float(
            "field_validation_queue_alignment_metrics",
            "field_requirement_patch_consumption_rate",
        )
        agent59 = self._readiness_float(
            "claim_specific_field_package_metrics",
            "field_requirement_patch_consumption_rate",
        )
        return agent53 >= 1.0 and agent58 >= 1.0 and agent59 >= 1.0

    def _unmet_guardrail_field_count(self) -> int:
        metrics = self.core_metrics.get("claim_specific_field_package_metrics", {})
        readiness = metrics.get("readiness", {}) if isinstance(metrics, dict) else {}
        return int(readiness.get("unmet_guardrail_field_count", 0))

    def _unmet_guardrail_fields(self) -> list[str]:
        metrics = self.core_metrics.get("claim_specific_field_package_metrics", {})
        readiness = metrics.get("readiness", {}) if isinstance(metrics, dict) else {}
        fields = readiness.get("unmet_guardrail_fields", [])
        if isinstance(fields, list):
            return [str(field) for field in fields]
        return []

    def _claim_specific_source_basis_completion_rate(self) -> float:
        metrics = self.core_metrics.get("claim_specific_field_package_metrics", {})
        readiness = metrics.get("readiness", {}) if isinstance(metrics, dict) else {}
        return float(readiness.get("source_basis_completion_rate", 0.0))

    def _minimal_field_package_field_pass_rate(self) -> float:
        metrics = self.core_metrics.get("claim_specific_field_package_metrics", {})
        readiness = metrics.get("readiness", {}) if isinstance(metrics, dict) else {}
        return float(readiness.get("minimal_field_package_field_pass_rate", 0.0))

    def _real_field_package_acceptance_readiness(self) -> dict[str, object]:
        metrics = self.core_metrics.get("real_field_package_acceptance_gate_metrics", {})
        readiness = metrics.get("readiness", {}) if isinstance(metrics, dict) else {}
        return readiness if isinstance(readiness, dict) else {}

    def _real_field_replay_pipeline_metrics(self) -> dict[str, object]:
        metrics = self.core_metrics.get("r7_real_field_replay_pipeline_metrics", {})
        return metrics if isinstance(metrics, dict) else {}

    def _r7_real_field_package_action(
        self,
        *,
        claim_source_basis_rate: float,
        field_package_field_pass_rate: float,
        r7_acceptance: dict[str, object],
        r7_pipeline: dict[str, object] | None = None,
    ) -> dict[str, object]:
        r7_pipeline = r7_pipeline or {}
        pipeline_readiness = r7_pipeline.get("pipeline_readiness", {})
        if not isinstance(pipeline_readiness, dict):
            pipeline_readiness = {}
        coverage = r7_pipeline.get("field_package_coverage", {})
        coverage_readiness = coverage.get("readiness", {}) if isinstance(coverage, dict) else {}
        coverage_next_actions = coverage.get("next_actions", []) if isinstance(coverage, dict) else []
        patch_plan = coverage.get("patch_plan", {}) if isinstance(coverage, dict) else {}
        if not isinstance(coverage_readiness, dict):
            coverage_readiness = {}
        if not isinstance(coverage_next_actions, list):
            coverage_next_actions = []
        if not isinstance(patch_plan, dict):
            patch_plan = {}
        coverage_status = str(
            pipeline_readiness.get(
                "field_package_coverage_status",
                coverage_readiness.get("field_package_coverage_status", ""),
            )
        )
        claim_specific_coverage_rate = float(
            pipeline_readiness.get(
                "claim_specific_coverage_rate",
                coverage_readiness.get("claim_specific_coverage_rate", field_package_field_pass_rate),
            )
        )
        soft_holdout_coverage_pass = bool(
            pipeline_readiness.get(
                "soft_holdout_coverage_pass",
                coverage_readiness.get("soft_holdout_coverage_pass", False),
            )
        )
        patch_plan_status = str(
            pipeline_readiness.get(
                "coverage_patch_plan_status",
                patch_plan.get("patch_plan_status", ""),
            )
        )
        patch_plan_item_count = int(
            pipeline_readiness.get(
                "coverage_patch_plan_item_count",
                patch_plan.get("item_count", 0),
            )
            or 0
        )
        minimum_replay_contract_status = str(
            pipeline_readiness.get(
                "minimum_replay_contract_status",
                coverage_readiness.get("minimum_replay_contract_status", "unknown"),
            )
        )
        minimum_common_batch_count = int(
            pipeline_readiness.get(
                "minimum_common_batch_count",
                coverage_readiness.get("minimum_common_batch_count", 0),
            )
            or 0
        )
        minimum_valid_matched_batch_count = int(
            pipeline_readiness.get(
                "minimum_valid_matched_batch_count",
                coverage_readiness.get("minimum_valid_matched_batch_count", 0),
            )
            or 0
        )
        minimum_valid_operation_action_count = int(
            pipeline_readiness.get(
                "minimum_valid_operation_action_count",
                coverage_readiness.get("minimum_valid_operation_action_count", 0),
            )
            or 0
        )
        minimum_invalid_operation_action_count = int(
            pipeline_readiness.get(
                "minimum_invalid_operation_action_count",
                coverage_readiness.get("minimum_invalid_operation_action_count", 0),
            )
            or 0
        )
        minimum_valid_lab_result_count = int(
            pipeline_readiness.get(
                "minimum_valid_lab_result_count",
                coverage_readiness.get("minimum_valid_lab_result_count", 0),
            )
            or 0
        )
        minimum_invalid_lab_result_count = int(
            pipeline_readiness.get(
                "minimum_invalid_lab_result_count",
                coverage_readiness.get("minimum_invalid_lab_result_count", 0),
            )
            or 0
        )
        minimum_valid_proxy_label_count = int(
            pipeline_readiness.get(
                "minimum_valid_proxy_label_count",
                coverage_readiness.get("minimum_valid_proxy_label_count", 0),
            )
            or 0
        )
        minimum_invalid_proxy_label_count = int(
            pipeline_readiness.get(
                "minimum_invalid_proxy_label_count",
                coverage_readiness.get("minimum_invalid_proxy_label_count", 0),
            )
            or 0
        )
        minimum_time_order_violation_count = int(
            pipeline_readiness.get(
                "minimum_time_order_violation_count",
                coverage_readiness.get("minimum_time_order_violation_count", 0),
            )
            or 0
        )
        pressure_source_conflict_count = int(
            pipeline_readiness.get(
                "pressure_source_conflict_count",
                coverage_readiness.get("pressure_source_conflict_count", 0),
            )
            or 0
        )
        resolved_pressure_source_conflict_count = int(
            pipeline_readiness.get(
                "resolved_pressure_source_conflict_count",
                coverage_readiness.get("resolved_pressure_source_conflict_count", 0),
            )
            or 0
        )
        unresolved_pressure_source_conflict_count = int(
            pipeline_readiness.get(
                "unresolved_pressure_source_conflict_count",
                coverage_readiness.get("unresolved_pressure_source_conflict_count", 0),
            )
            or 0
        )
        pressure_source_resolution_record_count = int(
            pipeline_readiness.get(
                "pressure_source_resolution_record_count",
                coverage_readiness.get("pressure_source_resolution_record_count", 0),
            )
            or 0
        )
        pressure_source_conflict_requires_review = bool(
            pipeline_readiness.get(
                "pressure_source_conflict_requires_operator_review",
                coverage_readiness.get("pressure_source_conflict_requires_operator_review", False),
            )
        )
        pressure_conflict_resolution_status = str(
            pipeline_readiness.get(
                "field_package_pressure_conflict_resolution_status",
                coverage_readiness.get("field_package_pressure_conflict_resolution_status", "unknown"),
            )
        )
        r7_next_action = str(
            pipeline_readiness.get(
                "r7_next_action",
                r7_acceptance.get("next_recommended_core_action", "R7_real_field_package_import_acceptance_gate"),
            )
        )
        next_action = self._coverage_aware_r7_action_id(coverage_status, patch_plan_status, r7_next_action)
        status = str(r7_acceptance.get("real_field_package_acceptance_status", "not_run"))
        title_by_action = {
            "R7_real_field_package_import_acceptance_gate": "进入真实 field package 导入与 replay/holdout 验收门",
            "R7a_import_real_field_package_with_metadata_and_csv": "导入 data_origin=field 的真实 metadata 与 CSV 包",
            "R7b_run_timestamped_replay_g6_and_evidence_chain": "重跑 timestamped replay、G6/P6 和证据链",
            "R7c_collect_soft_sensor_field_holdout_labels": "采集并导入软传感 field holdout 标签",
            "R7d_link_claim_specific_field_rows": "把真实 field rows 绑定到 claim-specific package",
            "R7e_refresh_unified_evidence_gate": "刷新统一 evidence gate 的 field-supported 判断",
            "R7f_human_review_before_field_supported_upgrade": "人工复核后再考虑 field-supported 升级",
            "R7g_patch_field_package_claim_specific_coverage": "补齐真实包 claim-specific 必采字段覆盖",
            "R7h_patch_soft_holdout_weak_target_labels": "补齐软传感 field holdout 弱目标标签",
            "R7i_patch_minimum_replay_batch_linkage": "补齐最小 timestamped replay 共同批次与 proxy 事件",
            "R8m_pressure_source_conflict_field_patch_requirements": "把压力源冲突转成现场复核与校准补包任务",
        }
        blockers = r7_acceptance.get("blocking_reasons", [])
        blocker_items = [str(item) for item in blockers] if isinstance(blockers, list) else [str(blockers)]
        blocker_items.extend(str(item) for item in coverage_next_actions)
        blocker_text = ", ".join(item for item in blocker_items if item)
        implementation_path = (
            "按 R7 minimum_real_field_package 准备 metadata.json 与 sensor/lab/operation/proxy/catalyst CSV，"
            "依次重跑 Agent44->42->43->45->46->58->59->R7。"
        )
        if next_action == "R7g_patch_field_package_claim_specific_coverage":
            implementation_path = (
                "先读取 field_package_coverage.claim_audit，逐条补齐 failed claim need 的缺失 header、"
                "非空字段和真实行，再重跑 R7 pipeline 与 Agent59 claim-specific package。"
            )
        elif next_action == "R7h_patch_soft_holdout_weak_target_labels":
            implementation_path = (
                "在 offline_lab_results 中补入 catalyst_activity 与 matrix_interference 等弱目标 analyte 的真实 holdout 标签，"
                "再重跑 Agent36/39/47/46 与 R7 pipeline。"
            )
        elif next_action == "R7i_patch_minimum_replay_batch_linkage":
            implementation_path = (
                "按 minimum_replay_contract_audit 补齐至少 3 个跨 sensor/lab/operation/proxy 共同 batch_id，"
                "补足可执行、时间可解析、工程可采信的 campaign_operation_log，"
                "补足 QA 通过、数值非负且时间可解析的 offline_lab_results，"
                "并补足可解析的 field-labeled fast_proxy_event_log，包括 protective_triggered、"
                "field_label_matrix_shock、false_positive_cost_index 和 label 时间戳；确保这些有效 action/lab/proxy 证据落在同一批次；重跑 Agent44->42->43->45。"
            )
        elif next_action == "R8m_pressure_source_conflict_field_patch_requirements":
            implementation_path = (
                "读取 field_package_coverage.patch_plan 中 R8M_PRESSURE_SOURCE_CONFLICT_FIELD_PATCH，"
                "逐个冲突 batch 核查 node_modality_sensor_timeseries 与 pressure_headloss_event_log 的压降来源、"
                "校准状态、instrument_id、flow_Lmin、operator_review_required 和 authoritative_pressure_source；"
                "补入 reviewer_id、review_time、calibration_action_id 与 pressure_source_resolution 后，"
                "重跑 R7 pipeline、Agent51 catalyst proxy holdout 和 Agent49/52 replay。"
            )
        elif coverage_status == "field_package_coverage_blocked_before_import":
            implementation_path = (
                "先修复真实包 preflight/import：替换 placeholder metadata，补齐真实时间戳行和 data_origin=field，"
                "通过 Agent44 后再解释 claim/soft-holdout coverage。"
            )
        return {
            "action_id": next_action,
            "title": title_by_action.get(next_action, "推进 R7 真实现场验收"),
            "model_core_relevance": 0.87,
            "downstream_chain_impact": 0.87,
            "scientific_value": 0.85,
            "engineering_feasibility": 0.72,
            "verification_readiness": 0.82,
            "trigger_metric": (
                f"R7_status={status}; "
                f"passed_stage_count={r7_acceptance.get('passed_stage_count', 0)}/"
                f"{r7_acceptance.get('total_stage_count', 0)}; "
                f"field_package_coverage_status={coverage_status or 'not_run'}; "
                f"claim_specific_coverage_rate={claim_specific_coverage_rate:.3f}; "
                f"soft_holdout_coverage_pass={soft_holdout_coverage_pass}; "
                f"minimum_replay_contract_status={minimum_replay_contract_status}; "
                f"minimum_common_batch_count={minimum_common_batch_count}; "
                f"minimum_valid_matched_batch_count={minimum_valid_matched_batch_count}; "
                f"minimum_valid_operation_action_count={minimum_valid_operation_action_count}; "
                f"minimum_invalid_operation_action_count={minimum_invalid_operation_action_count}; "
                f"minimum_valid_lab_result_count={minimum_valid_lab_result_count}; "
                f"minimum_invalid_lab_result_count={minimum_invalid_lab_result_count}; "
                f"minimum_valid_proxy_label_count={minimum_valid_proxy_label_count}; "
                f"minimum_invalid_proxy_label_count={minimum_invalid_proxy_label_count}; "
                f"minimum_time_order_violation_count={minimum_time_order_violation_count}; "
                f"pressure_source_conflict_count={pressure_source_conflict_count}; "
                f"resolved_pressure_source_conflict_count={resolved_pressure_source_conflict_count}; "
                f"unresolved_pressure_source_conflict_count={unresolved_pressure_source_conflict_count}; "
                f"pressure_source_resolution_record_count={pressure_source_resolution_record_count}; "
                f"pressure_source_conflict_requires_operator_review={pressure_source_conflict_requires_review}; "
                f"pressure_conflict_resolution_status={pressure_conflict_resolution_status}; "
                f"patch_plan_status={patch_plan_status or 'not_run'}; "
                f"patch_plan_item_count={patch_plan_item_count}; "
                f"source_basis_completion_rate={claim_source_basis_rate:.3f}; "
                f"minimal_field_package_field_pass_rate={field_package_field_pass_rate:.3f}"
            ),
            "why_now": (
                "R4b/R5/R6 已完成 patch consumption、schema 覆盖和 source_basis detail；"
                "R7 pipeline 现在不仅能看导入是否通过，还能判断真实包是否足以支撑 claim-specific review 和 soft sensor holdout。"
            ),
            "implementation_path": implementation_path,
            "must_not_do": "没有真实 field package 时不能伪造 field-supported 结论，也不能把 synthetic template 当作现场 replay。",
            "expected_metrics": [
                "real_field_package_acceptance_status",
                "field_package_coverage_status",
                "claim_specific_coverage_rate",
                "soft_holdout_coverage_pass",
                "minimum_replay_contract_status",
                "minimum_common_batch_count",
                "minimum_valid_matched_batch_count",
                "minimum_valid_operation_action_count",
                "minimum_invalid_operation_action_count",
                "minimum_valid_lab_result_count",
                "minimum_invalid_lab_result_count",
                "minimum_valid_proxy_label_count",
                "minimum_invalid_proxy_label_count",
                "minimum_time_order_violation_count",
                "pressure_source_conflict_count",
                "resolved_pressure_source_conflict_count",
                "unresolved_pressure_source_conflict_count",
                "pressure_source_resolution_record_count",
                "pressure_source_conflict_requires_operator_review",
                "field_package_pressure_conflict_resolution_status",
                "coverage_patch_plan_status",
                "field_package_import_pass",
                "field_replay_evidence_chain_pass",
                "soft_sensor_field_holdout_gate_pass",
                "field_supported_edge_ratio",
                "can_write_to_release_gate",
            ],
            "current_blockers": blocker_text,
        }

    @staticmethod
    def _coverage_aware_r7_action_id(coverage_status: str, patch_plan_status: str, r7_next_action: str) -> str:
        if coverage_status == "field_package_claim_specific_coverage_gaps":
            return "R7g_patch_field_package_claim_specific_coverage"
        if coverage_status == "field_package_soft_holdout_coverage_gaps":
            return "R7h_patch_soft_holdout_weak_target_labels"
        if patch_plan_status == "patch_plan_requires_pressure_source_conflict_resolution":
            return "R8m_pressure_source_conflict_field_patch_requirements"
        if coverage_status == "field_package_coverage_blocked_before_import":
            return "R7a_import_real_field_package_with_metadata_and_csv"
        if patch_plan_status == "patch_plan_requires_minimum_replay_contract":
            return "R7i_patch_minimum_replay_batch_linkage"
        return r7_next_action

    def _readiness_float(self, metric_key: str, readiness_key: str) -> float:
        metrics = self.core_metrics.get(metric_key, {})
        readiness = metrics.get("readiness", {}) if isinstance(metrics, dict) else {}
        return float(readiness.get(readiness_key, 0.0))

    @staticmethod
    def _module_by_id(module_id: str) -> dict[str, object]:
        for module in MODULE_BLUEPRINTS:
            if module["module_id"] == module_id:
                return dict(module)
        return {}


def _list(value: object) -> list[object]:
    if isinstance(value, list):
        return value
    if isinstance(value, tuple | set):
        return list(value)
    return []


def _dict(value: object) -> dict[str, object]:
    return value if isinstance(value, dict) else {}

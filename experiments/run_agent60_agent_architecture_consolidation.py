from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

from water_ai.agents.agent_architecture_consolidation_agent import AgentArchitectureConsolidationAgent


PROJECT_ROOT = Path(__file__).resolve().parents[1]
AGENTS_DIR = PROJECT_ROOT / "src" / "water_ai" / "agents"
EXPERIMENTS_DIR = PROJECT_ROOT / "experiments"
MANIFEST_PATH = PROJECT_ROOT / "deliverables" / "manifest.json"
PRIORITY_PATH = PROJECT_ROOT / "outputs" / "model_core_governance" / "priority_ranking.json"
SPARSE_METRICS_PATH = PROJECT_ROOT / "outputs" / "sensor_network_sparse_placement" / "sparse_placement_metrics.json"
REPLAY_EVALUATION_METRICS_PATH = PROJECT_ROOT / "outputs" / "multi_facility_replay_evaluation" / "replay_evaluation_metrics.json"
CLAIM_PACKAGE_METRICS_PATH = PROJECT_ROOT / "outputs" / "claim_specific_field_package" / "claim_specific_field_package_metrics.json"
CATALYST_PROXY_METRICS_PATH = PROJECT_ROOT / "outputs" / "catalyst_activity_proxy" / "catalyst_activity_proxy_metrics.json"
UNIFIED_FIELD_EVIDENCE_GATE_METRICS_PATH = (
    PROJECT_ROOT / "outputs" / "unified_field_evidence_gate" / "unified_field_evidence_gate_metrics.json"
)
OBSERVATION_CONTRACT_METRICS_PATH = (
    PROJECT_ROOT / "outputs" / "observation_contract_merge" / "observation_contract_metrics.json"
)
SOFT_SENSOR_MATRIX_METRICS_PATH = (
    PROJECT_ROOT / "outputs" / "soft_sensor_matrix_coupling" / "soft_sensor_matrix_metrics.json"
)
CONTROL_REPLAY_STRESS_METRICS_PATH = (
    PROJECT_ROOT / "outputs" / "control_replay_counterfactual_stress" / "control_replay_stress_metrics.json"
)
COLLABORATIVE_CONTROL_METRICS_PATH = (
    PROJECT_ROOT / "outputs" / "multi_facility_collaborative_control" / "collaborative_control_metrics.json"
)
CONTROL_GUARDRAIL_BACKPROP_METRICS_PATH = (
    PROJECT_ROOT / "outputs" / "control_guardrail_backpropagation" / "control_guardrail_backpropagation_metrics.json"
)
MINIMAL_GREY_BOX_PHYSICS_METRICS_PATH = (
    PROJECT_ROOT / "outputs" / "minimal_grey_box_physics" / "grey_box_physics_metrics.json"
)
FIELD_VALIDATION_ALIGNMENT_METRICS_PATH = (
    PROJECT_ROOT / "outputs" / "field_validation_queue_alignment" / "field_validation_queue_alignment_metrics.json"
)
REAL_FIELD_PACKAGE_ACCEPTANCE_METRICS_PATH = (
    PROJECT_ROOT
    / "outputs"
    / "real_field_package_acceptance_gate"
    / "real_field_package_acceptance_gate_metrics.json"
)
R7_REAL_FIELD_REPLAY_PIPELINE_METRICS_PATH = (
    PROJECT_ROOT
    / "outputs"
    / "r7_real_field_replay_pipeline"
    / "r7_real_field_replay_pipeline_metrics.json"
)
FIELD_DATA_INTERFACE_REPORT_PATH = (
    PROJECT_ROOT / "outputs" / "agent30_field_data_interface" / "agent30_report.json"
)
TIMESTAMPED_CAMPAIGN_REPLAY_REPORT_PATH = (
    PROJECT_ROOT / "outputs" / "agent42_timestamped_campaign_replay" / "agent42_report.json"
)
FIELD_REPLAY_IMPORT_METRICS_PATH = (
    PROJECT_ROOT / "outputs" / "field_replay_import" / "import_acceptance_metrics.json"
)
PRESSURE_RESOLUTION_SCENARIO_PACK_METRICS_PATH = (
    PROJECT_ROOT
    / "outputs"
    / "pressure_resolution_replay_scenario_pack"
    / "pressure_resolution_replay_scenario_pack_metrics.json"
)
OUT_DIR = PROJECT_ROOT / "outputs" / "agent60_agent_architecture_consolidation"
METRICS_DIR = PROJECT_ROOT / "outputs" / "agent_architecture_consolidation"
DELIVERABLE_PATH = PROJECT_ROOT / "deliverables" / "model_core_optimization" / "agent_architecture_consolidation.md"
METRICS_PATH = METRICS_DIR / "architecture_consolidation_metrics.json"
PATENT_TECHNICAL_FEATURE_LEDGER_PATH = METRICS_DIR / "patent_technical_feature_ledger.json"
TECHNICAL_CLAIM_SKELETON_PATH = METRICS_DIR / "technical_claim_skeleton_scaffold.json"
TECHNICAL_EMBODIMENT_VALIDATION_PATH = METRICS_DIR / "technical_embodiment_validation_matrix.json"
TECHNICAL_EFFECT_MEASUREMENT_PATH = METRICS_DIR / "technical_effect_measurement_matrix.json"
PRIOR_ART_DISTINCTION_PATH = METRICS_DIR / "prior_art_distinction_matrix.json"
FORMAL_SEARCH_WORK_PACKAGES_PATH = METRICS_DIR / "formal_search_work_packages.json"
FORMAL_SEARCH_RESULT_INTAKE_PATH = METRICS_DIR / "formal_search_result_intake_schema.json"
FORMAL_SEARCH_RESULT_VALIDATION_GATE_PATH = METRICS_DIR / "formal_search_result_validation_gate.json"
FORMAL_SEARCH_RESULT_PACKAGE_TEMPLATE_PATH = METRICS_DIR / "formal_search_result_package_template.json"
FORMAL_SEARCH_RESULT_PACKAGE_SUBMISSION_TEMPLATE_PATH = (
    METRICS_DIR / "formal_search_result_package_submission_template.json"
)
FORMAL_SEARCH_RESULT_PACKAGE_PREFLIGHT_PATH = METRICS_DIR / "formal_search_result_package_source_preflight.json"
FORMAL_SEARCH_RESULT_PACKAGE_ROW_PREFLIGHT_PATH = (
    METRICS_DIR / "formal_search_result_package_row_preflight.json"
)
FORMAL_SEARCH_RESULT_VALIDATION_EXECUTION_PATH = (
    METRICS_DIR / "formal_search_result_validation_execution.json"
)
FORMAL_SEARCH_NONLEGAL_COMPARISON_REVIEW_PACKET_PATH = (
    METRICS_DIR / "formal_search_nonlegal_comparison_review_packet.json"
)
FORMAL_SEARCH_NONLEGAL_REVIEW_RESPONSE_TEMPLATE_PATH = (
    METRICS_DIR / "formal_search_nonlegal_review_response_template.json"
)
FORMAL_SEARCH_NONLEGAL_REVIEW_RESPONSE_PREFLIGHT_PATH = (
    METRICS_DIR / "formal_search_nonlegal_review_response_source_preflight.json"
)
FORMAL_SEARCH_CLAIM_SCOPE_PATCH_DRAFT_PATH = (
    METRICS_DIR / "formal_search_claim_scope_patch_draft.json"
)
FORMAL_COUNSEL_REVIEW_RESPONSE_TEMPLATE_PATH = (
    METRICS_DIR / "formal_counsel_review_response_template.json"
)
FORMAL_COUNSEL_REVIEW_RESPONSE_PREFLIGHT_PATH = (
    METRICS_DIR / "formal_counsel_review_response_source_preflight.json"
)
FORMAL_DISCLOSURE_REVISION_QUEUE_PATH = (
    METRICS_DIR / "formal_disclosure_revision_queue.json"
)
FORMAL_DISCLOSURE_REVISION_IMPACT_PLAN_PATH = (
    METRICS_DIR / "formal_disclosure_revision_impact_plan.json"
)
FORMAL_SEARCH_REVIEW_READINESS_PATH = (
    METRICS_DIR / "formal_search_review_readiness.json"
)
FORMAL_SEARCH_EXECUTION_ROUTE_PLAN_PATH = (
    METRICS_DIR / "formal_search_execution_route_plan.json"
)
NONLEGAL_PRIOR_ART_SEED_MATRIX_PATH = (
    METRICS_DIR / "nonlegal_prior_art_seed_matrix.json"
)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    DELIVERABLE_PATH.parent.mkdir(parents=True, exist_ok=True)

    agent_names = _agent_names()
    experiment_names = _experiment_names()
    report = AgentArchitectureConsolidationAgent(
        agent_names=agent_names,
        experiment_names=experiment_names,
        agent_run_numbers=_agent_run_numbers(experiment_names),
        priority_ranking=_read_optional_json(PRIORITY_PATH),
        core_metrics={
            "agent48_metrics": _read_optional_json(SPARSE_METRICS_PATH),
            "replay_evaluation_metrics": _read_optional_json(REPLAY_EVALUATION_METRICS_PATH),
            "catalyst_proxy_metrics": _read_optional_json(CATALYST_PROXY_METRICS_PATH),
            "claim_specific_field_package_metrics": _read_optional_json(CLAIM_PACKAGE_METRICS_PATH),
            "unified_field_evidence_gate_metrics": _read_optional_json(UNIFIED_FIELD_EVIDENCE_GATE_METRICS_PATH),
            "observation_contract_metrics": _read_optional_json(OBSERVATION_CONTRACT_METRICS_PATH),
            "soft_sensor_matrix_metrics": _read_optional_json(SOFT_SENSOR_MATRIX_METRICS_PATH),
            "control_replay_stress_metrics": _read_optional_json(CONTROL_REPLAY_STRESS_METRICS_PATH),
            "collaborative_control_metrics": _read_optional_json(COLLABORATIVE_CONTROL_METRICS_PATH),
            "control_guardrail_backpropagation_metrics": _read_optional_json(CONTROL_GUARDRAIL_BACKPROP_METRICS_PATH),
            "minimal_grey_box_physics_metrics": _read_optional_json(MINIMAL_GREY_BOX_PHYSICS_METRICS_PATH),
            "field_validation_queue_alignment_metrics": _read_optional_json(FIELD_VALIDATION_ALIGNMENT_METRICS_PATH),
            "real_field_package_acceptance_gate_metrics": _read_optional_json(
                REAL_FIELD_PACKAGE_ACCEPTANCE_METRICS_PATH
            ),
            "r7_real_field_replay_pipeline_metrics": _read_optional_json(R7_REAL_FIELD_REPLAY_PIPELINE_METRICS_PATH),
            "field_data_interface_metrics": _read_optional_json(FIELD_DATA_INTERFACE_REPORT_PATH),
            "timestamped_campaign_replay_metrics": _read_optional_json(TIMESTAMPED_CAMPAIGN_REPLAY_REPORT_PATH),
            "field_replay_import_metrics": _read_optional_json(FIELD_REPLAY_IMPORT_METRICS_PATH),
            "pressure_resolution_replay_scenario_pack_metrics": _read_optional_json(
                PRESSURE_RESOLUTION_SCENARIO_PACK_METRICS_PATH
            ),
        },
        nonlegal_prior_art_seed_matrix=_read_optional_json(NONLEGAL_PRIOR_ART_SEED_MATRIX_PATH),
        formal_search_result_package_path=os.environ.get("FORMAL_SEARCH_RESULT_PACKAGE_PATH"),
        formal_search_nonlegal_review_response_path=os.environ.get(
            "FORMAL_SEARCH_NONLEGAL_REVIEW_RESPONSE_PATH"
        ),
        formal_counsel_review_response_path=os.environ.get(
            "FORMAL_COUNSEL_REVIEW_RESPONSE_PATH"
        ),
    ).run([])

    payload = {"summary": report.summary, "recommendations": report.recommendations, "metrics": report.metrics}
    METRICS_PATH.write_text(json.dumps(report.metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    PATENT_TECHNICAL_FEATURE_LEDGER_PATH.write_text(
        json.dumps(
            {
                "coverage": report.metrics["patent_technical_feature_coverage"],
                "features": report.metrics["patent_technical_feature_ledger"],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    TECHNICAL_CLAIM_SKELETON_PATH.write_text(
        json.dumps(
            {
                "coverage": report.metrics["technical_claim_skeleton_coverage"],
                "claims": report.metrics["technical_claim_skeleton_scaffold"],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    TECHNICAL_EMBODIMENT_VALIDATION_PATH.write_text(
        json.dumps(
            {
                "coverage": report.metrics["technical_embodiment_validation_coverage"],
                "embodiments": report.metrics["technical_embodiment_validation_matrix"],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    TECHNICAL_EFFECT_MEASUREMENT_PATH.write_text(
        json.dumps(
            {
                "coverage": report.metrics["technical_effect_measurement_coverage"],
                "effects": report.metrics["technical_effect_measurement_matrix"],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    PRIOR_ART_DISTINCTION_PATH.write_text(
        json.dumps(
            {
                "coverage": report.metrics["prior_art_distinction_coverage"],
                "distinctions": report.metrics["prior_art_distinction_matrix"],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    FORMAL_SEARCH_WORK_PACKAGES_PATH.write_text(
        json.dumps(
            {
                "coverage": report.metrics["formal_search_work_package_coverage"],
                "work_packages": report.metrics["formal_search_work_package_matrix"],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    FORMAL_SEARCH_RESULT_INTAKE_PATH.write_text(
        json.dumps(
            {
                "coverage": report.metrics["formal_search_result_intake_coverage"],
                "intake_schema": report.metrics["formal_search_result_intake_schema"],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    FORMAL_SEARCH_RESULT_VALIDATION_GATE_PATH.write_text(
        json.dumps(
            {
                "coverage": report.metrics["formal_search_result_validation_gate_coverage"],
                "validation_gates": report.metrics["formal_search_result_validation_gate"],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    FORMAL_SEARCH_RESULT_PACKAGE_TEMPLATE_PATH.write_text(
        json.dumps(
            {
                "coverage": report.metrics["formal_search_result_package_template_coverage"],
                "package_templates": report.metrics["formal_search_result_package_template"],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    FORMAL_SEARCH_RESULT_PACKAGE_SUBMISSION_TEMPLATE_PATH.write_text(
        json.dumps(
            report.metrics["formal_search_result_package_submission_template"],
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    FORMAL_SEARCH_RESULT_PACKAGE_PREFLIGHT_PATH.write_text(
        json.dumps(
            report.metrics["formal_search_result_package_source_preflight"],
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    FORMAL_SEARCH_RESULT_PACKAGE_ROW_PREFLIGHT_PATH.write_text(
        json.dumps(
            report.metrics["formal_search_result_package_row_preflight"],
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    FORMAL_SEARCH_RESULT_VALIDATION_EXECUTION_PATH.write_text(
        json.dumps(
            report.metrics["formal_search_result_validation_execution"],
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    FORMAL_SEARCH_NONLEGAL_COMPARISON_REVIEW_PACKET_PATH.write_text(
        json.dumps(
            report.metrics["formal_search_nonlegal_comparison_review_packet"],
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    FORMAL_SEARCH_NONLEGAL_REVIEW_RESPONSE_TEMPLATE_PATH.write_text(
        json.dumps(
            report.metrics["formal_search_nonlegal_review_response_template"],
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    FORMAL_SEARCH_NONLEGAL_REVIEW_RESPONSE_PREFLIGHT_PATH.write_text(
        json.dumps(
            report.metrics["formal_search_nonlegal_review_response_source_preflight"],
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    FORMAL_SEARCH_CLAIM_SCOPE_PATCH_DRAFT_PATH.write_text(
        json.dumps(
            report.metrics["formal_search_claim_scope_patch_draft"],
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    FORMAL_COUNSEL_REVIEW_RESPONSE_TEMPLATE_PATH.write_text(
        json.dumps(
            report.metrics["formal_counsel_review_response_template"],
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    FORMAL_COUNSEL_REVIEW_RESPONSE_PREFLIGHT_PATH.write_text(
        json.dumps(
            report.metrics["formal_counsel_review_response_source_preflight"],
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    FORMAL_DISCLOSURE_REVISION_QUEUE_PATH.write_text(
        json.dumps(
            report.metrics["formal_disclosure_revision_queue"],
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    FORMAL_DISCLOSURE_REVISION_IMPACT_PLAN_PATH.write_text(
        json.dumps(
            report.metrics["formal_disclosure_revision_impact_plan"],
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    FORMAL_SEARCH_REVIEW_READINESS_PATH.write_text(
        json.dumps(
            report.metrics["formal_search_review_readiness"],
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    FORMAL_SEARCH_EXECUTION_ROUTE_PLAN_PATH.write_text(
        json.dumps(
            report.metrics["formal_search_execution_route_plan"],
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    (OUT_DIR / "agent60_report.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT_DIR / "agent60_report.md").write_text(_report_md(report), encoding="utf-8")
    DELIVERABLE_PATH.write_text(_deliverable_md(report), encoding="utf-8")
    _update_manifest(report)

    print(report.summary)
    for recommendation in report.recommendations:
        print(f"- {recommendation}")
    print(f"deliverable: {DELIVERABLE_PATH}")
    print(f"metrics: {METRICS_PATH}")


def _agent_names() -> list[str]:
    # Agent60 is the governance harness for this audit. The audited model body is
    # the active model body excluding this consolidation harness.
    return sorted(path.stem for path in AGENTS_DIR.glob("*_agent.py") if path.stem != "agent_architecture_consolidation_agent")


def _experiment_names() -> list[str]:
    return sorted(path.stem for path in EXPERIMENTS_DIR.glob("run_agent*.py"))


def _agent_run_numbers(experiment_names: list[str]) -> dict[str, int]:
    exceptions = {
        "model_core_governance": "model_core_optimization_governance_agent",
        "engineering_execution_constraints": "engineering_execution_constraint_agent",
        "agent_architecture_consolidation": "agent_architecture_consolidation_agent",
    }
    result: dict[str, int] = {}
    for name in experiment_names:
        match = re.match(r"run_agent(\d+)_(.+)", name)
        if not match:
            continue
        number = int(match.group(1))
        suffix = match.group(2)
        agent_name = exceptions.get(suffix, f"{suffix}_agent")
        result[agent_name] = number
    return result


def _read_optional_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _report_md(report) -> str:
    metrics = report.metrics
    lines = [
        "# Agent60 架构复盘与减冗治理报告",
        "",
        "说明：Agent60 是本轮复盘治理工具，不计入被复盘的模型能力链；下列统计审计的是当前模型本体。",
        "",
        f"- 状态：`{metrics['architecture_status']}`",
        f"- Agent 数：{metrics['agent_count']}",
        f"- 已映射 Agent：{metrics['mapped_agent_count']}/{metrics['agent_count']}",
        f"- 模块数：{metrics['module_count']}",
        f"- 七层系统骨架覆盖率：{metrics['system_spine_coverage']['layer_coverage_rate']}",
        f"- 六类系统能力覆盖率：{metrics['system_spine_coverage']['ability_coverage_rate']}",
        f"- 骨架状态：`{metrics['system_spine_coverage']['system_spine_status']}`",
        f"- 模块接口契约覆盖率：{metrics['interface_contract_coverage']['interface_contract_coverage_rate']}",
        f"- 接口契约状态：`{metrics['interface_contract_coverage']['interface_contract_status']}`",
        f"- 核心模型模块数：{metrics['core_model_module_count']}",
        f"- 冗余/合并簇数：{metrics['redundancy_cluster_count']}",
        f"- 展示层冻结 Agent 数：{metrics['presentation_freeze_agent_count']}",
        f"- 架构整理分数：{metrics['consolidation_readiness_score']}",
        f"- 自我打断结论：`{metrics['self_interrupt_verdict']}`",
        "",
        "## 下一步最高边际价值动作",
        "",
    ]
    for action in metrics["ranked_refactor_actions"]:
        lines.extend(
            [
                f"### {action['rank']}. {action['action_id']}",
                "",
                f"- 标题：{action['title']}",
                f"- 边际价值分：{action['marginal_value_score']}",
                f"- 触发指标：{action['trigger_metric']}",
                f"- 为什么现在做：{action['why_now']}",
                f"- 实现路径：{action['implementation_path']}",
                f"- 不能做：{action['must_not_do']}",
                "",
            ]
        )
    fallback = metrics["offline_core_fallback_action"]
    if fallback.get("fallback_enabled"):
        lines.extend(
            [
                "## 无真实包时的离线核心 Fallback",
                "",
            f"- 动作：`{fallback['action_id']}`",
            f"- 标题：{fallback['title']}",
            f"- 触发指标：{fallback['trigger_metric']}",
            f"- 原因：{fallback['reason']}",
                f"- 禁止事项：{fallback['must_not_do']}",
                "",
            ]
        )
        if fallback.get("r7_completion_plan_status"):
            lines.extend(
                [
                    "- R7-to-R8p completion plan："
                    f"{fallback['r7_completion_plan_status']}",
                    f"- completion item 数：{fallback.get('r7_completion_item_count', 0)}",
                    "- completion item 分类："
                    f"{fallback.get('r7_completion_item_class_counts', {})}",
                        "- completion 字段缺口分类："
                        f"{fallback.get('r7_completion_field_gap_count_by_class', {})}",
                        "- completion route contracts："
                        f"{fallback.get('r7_completion_route_contracts_status', '')}",
                        f"- open route 数：{fallback.get('r7_completion_open_route_count', 0)}",
                        f"- open routes：{fallback.get('r7_completion_open_route_ids', [])}",
                        "- completion route work packages："
                        f"{fallback.get('r7_completion_route_work_packages_status', '')}",
                        f"- open work package 数：{fallback.get('r7_completion_open_work_package_count', 0)}",
                        f"- open work packages：{fallback.get('r7_completion_open_work_package_ids', [])}",
                        "- completion route work package preflight："
                        f"{fallback.get('r7_completion_route_work_package_preflight_status', '')}",
                        f"- submitted work package 数：{fallback.get('r7_completion_submitted_work_package_count', 0)}",
                        f"- passed work package 数：{fallback.get('r7_completion_passed_work_package_count', 0)}",
                        f"- blocked work package 数：{fallback.get('r7_completion_blocked_work_package_count', 0)}",
                        "- completion route work package patch plan："
                        f"{fallback.get('r7_completion_route_work_package_patch_plan_status', '')}",
                        f"- patch item 数：{fallback.get('r7_completion_route_work_package_patch_item_count', 0)}",
                        f"- highest patch：{fallback.get('r7_completion_route_work_package_highest_priority_patch_id', '')}",
                        "- completion route work package assembly gate："
                        f"{fallback.get('r7_completion_route_work_package_assembly_gate_status', '')}",
                        f"- assembly step 数：{fallback.get('r7_completion_route_work_package_assembly_step_count', 0)}",
                        f"- blocked assembly step 数：{fallback.get('r7_completion_route_work_package_blocked_assembly_step_count', 0)}",
                        "- submission readiness review："
                        f"{fallback.get('submission_readiness_review_status', '')}",
                        "- submission readiness next action："
                        f"{fallback.get('submission_readiness_next_operator_action', '')}",
                        "- submission readiness can route to R8v："
                        f"{fallback.get('submission_readiness_can_route_to_r8v', False)}",
                        "- source package route guide："
                        f"{fallback.get('source_package_route_guide_status', '')}",
                        "- source package recommended route："
                        f"{fallback.get('source_package_recommended_route_id', '')}",
                        "- source package next action："
                        f"{fallback.get('source_package_next_operator_action', '')}",
                        "- source package route preflight："
                        f"{fallback.get('source_package_route_preflight_status', '')}",
                        "- source package recommended route preflight："
                        f"{fallback.get('source_package_recommended_route_preflight_status', '')}",
                        f"- source package ready/waiting/blocked routes："
                        f"{fallback.get('source_package_ready_route_count', 0)}/"
                        f"{fallback.get('source_package_waiting_route_count', 0)}/"
                        f"{fallback.get('source_package_blocked_route_count', 0)}",
                        f"- completion plan 路径：{fallback.get('r7_completion_plan_path', '')}",
                        "",
                    ]
            )
    lines.extend(
        [
            "## 全局七层系统骨架",
            "",
            "| 层级 | 覆盖状态 | 模块 | 能力 | 核心问题 |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for layer in metrics["system_layer_board"]:
        lines.append(
            "| "
            f"{layer['layer_id']} {layer['title']} | "
            f"{layer['coverage_status']} | "
            f"{', '.join(layer['modules']) or '-'} | "
            f"{', '.join(layer['core_abilities']) or '-'} | "
            f"{layer['core_question']} |"
        )
    lines.append("")
    lines.extend(
        [
            "## 模块接口契约矩阵",
            "",
            "| 模块 | 输入/输出契约 | 状态变量 | 可传递指标 | 不能做 | 现场验证需求 |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for contract in metrics["module_interface_contracts"]:
        lines.append(
            "| "
            f"{contract['module_id']} {contract['module_title']} | "
            f"输入：{contract['input_contract']}<br>输出：{contract['output_contract']} | "
            f"{', '.join(contract['state_variables'])} | "
            f"{', '.join(contract['transferable_metrics'])} | "
            f"{contract['cannot_do']} | "
            f"{contract['field_validation_need']} |"
        )
    lines.append("")
    patent_coverage = metrics["patent_technical_feature_coverage"]
    lines.extend(
        [
            "## 专利级技术特征 Ledger",
            "",
            "说明：该 ledger 是技术交底成熟度检查，不是法律意见，也不是 field-supported 结论。",
            "",
            f"- 状态：`{patent_coverage['patent_technical_feature_status']}`",
            f"- 技术特征数：{patent_coverage['complete_feature_count']}/{patent_coverage['feature_count']}",
            f"- 覆盖率：{patent_coverage['technical_feature_coverage_rate']}",
            f"- 抽象口号风险特征：{patent_coverage['abstract_only_feature_ids']}",
            f"- 允许现场 claim 升级：{patent_coverage['field_claim_upgrade_allowed']}",
            f"- 机器可读 ledger：`{PATENT_TECHNICAL_FEATURE_LEDGER_PATH.relative_to(PROJECT_ROOT)}`",
            "",
            "| 特征 | 对应模块 | 技术问题 | 技术手段 | 控制动作 | 验证指标 | 边界 |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for feature in metrics["patent_technical_feature_ledger"]:
        lines.append(
            "| "
            f"{feature['feature_id']} | "
            f"{feature['module_id']} | "
            f"{feature['technical_problem']} | "
            f"{feature['technical_means']} | "
            f"{', '.join(feature['control_actions'])} | "
            f"{', '.join(feature['verification_metrics'])} | "
            f"{feature['evidence_boundary']} |"
        )
    lines.append("")
    claim_coverage = metrics["technical_claim_skeleton_coverage"]
    lines.extend(
        [
            "## 技术方案 Claim Skeleton Scaffold",
            "",
            "说明：该 scaffold 只把技术特征组合成方法/系统/从属方向骨架，不是法律权利要求文本，也不是授权判断。",
            "",
            f"- 状态：`{claim_coverage['technical_claim_skeleton_status']}`",
            f"- Claim scaffold 数：{claim_coverage['complete_claim_scaffold_count']}/{claim_coverage['claim_scaffold_count']}",
            f"- 覆盖率：{claim_coverage['technical_claim_skeleton_coverage_rate']}",
            f"- 独立方向：{claim_coverage['independent_claim_scaffold_ids']}",
            f"- 从属/分案方向：{claim_coverage['dependent_or_divisional_scaffold_ids']}",
            f"- 缺失技术特征覆盖：{claim_coverage['missing_feature_coverage']}",
            f"- 允许现场 claim 升级：{claim_coverage['field_claim_upgrade_allowed']}",
            f"- 机器可读 scaffold：`{TECHNICAL_CLAIM_SKELETON_PATH.relative_to(PROJECT_ROOT)}`",
            "",
            "| Scaffold | 类型 | 映射特征 | 组合手段 | 验证门 | 边界 |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for claim in metrics["technical_claim_skeleton_scaffold"]:
        lines.append(
            "| "
            f"{claim['claim_id']} | "
            f"{claim['claim_type']} | "
            f"{', '.join(claim['mapped_feature_ids'])} | "
            f"{claim['technical_combination']} | "
            f"{', '.join(claim['verification_gates'])} | "
            f"{claim['evidence_boundary']} |"
        )
    lines.append("")
    embodiment_coverage = metrics["technical_embodiment_validation_coverage"]
    lines.extend(
        [
            "## 技术实施例与验证矩阵",
            "",
            "说明：该矩阵把方法/系统/从属方向落成可验收实施例，但仍不生成 field evidence。",
            "",
            f"- 状态：`{embodiment_coverage['technical_embodiment_validation_status']}`",
            f"- 实施例数：{embodiment_coverage['complete_embodiment_count']}/{embodiment_coverage['embodiment_count']}",
            f"- 覆盖率：{embodiment_coverage['technical_embodiment_validation_coverage_rate']}",
            f"- 缺失 claim 覆盖：{embodiment_coverage['missing_claim_coverage']}",
            f"- 缺失 feature 覆盖：{embodiment_coverage['missing_feature_coverage']}",
            f"- 允许现场 claim 升级：{embodiment_coverage['field_claim_upgrade_allowed']}",
            f"- 机器可读矩阵：`{TECHNICAL_EMBODIMENT_VALIDATION_PATH.relative_to(PROJECT_ROOT)}`",
            "",
            "| 实施例 | 链接 Claim | 数据包/工件 | 验证门 | 验收指标 | 边界 |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for embodiment in metrics["technical_embodiment_validation_matrix"]:
        lines.append(
            "| "
            f"{embodiment['embodiment_id']} | "
            f"{', '.join(embodiment['linked_claim_ids'])} | "
            f"{', '.join(embodiment['required_tables_or_artifacts'])} | "
            f"{', '.join(embodiment['validation_gates'])} | "
            f"{', '.join(embodiment['acceptance_metrics'])} | "
            f"{embodiment['failure_boundary']} |"
        )
    lines.append("")
    effect_coverage = metrics["technical_effect_measurement_coverage"]
    lines.extend(
        [
            "## 技术效果度量矩阵",
            "",
            "说明：该矩阵把实施例中的技术效果转成基线、指标、阈值和验证门；它仍然不是 field-supported 结论。",
            "",
            f"- 状态：`{effect_coverage['technical_effect_measurement_status']}`",
            f"- 技术效果数：{effect_coverage['complete_effect_count']}/{effect_coverage['effect_count']}",
            f"- 覆盖率：{effect_coverage['technical_effect_measurement_coverage_rate']}",
            f"- 缺失实施例覆盖：{effect_coverage['missing_embodiment_coverage']}",
            f"- 允许现场 claim 升级：{effect_coverage['field_claim_upgrade_allowed']}",
            f"- 可写执行器：{effect_coverage['can_write_to_actuator']}",
            f"- 可写 release gate：{effect_coverage['can_write_to_release_gate']}",
            f"- 机器可读矩阵：`{TECHNICAL_EFFECT_MEASUREMENT_PATH.relative_to(PROJECT_ROOT)}`",
            "",
            "| 技术效果 | 关联实施例 | 基线 | 指标 | 阈值/规则 | 验证门 | 边界 |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for effect in metrics["technical_effect_measurement_matrix"]:
        lines.append(
            "| "
            f"{effect['effect_id']} | "
            f"{', '.join(effect['linked_embodiment_ids'])} | "
            f"{effect['baseline_comparator']} | "
            f"{', '.join(effect['measurement_metrics'])} | "
            f"{'<br>'.join(effect['acceptance_thresholds'])} | "
            f"{effect['validation_gate']} | "
            f"{effect['failure_boundary']} |"
        )
    lines.append("")
    prior_art_coverage = metrics["prior_art_distinction_coverage"]
    lines.extend(
        [
            "## 现有技术区别与保护性风险矩阵",
            "",
            "说明：该矩阵是 prior-art distinction hypothesis，不是正式检索、法律意见或授权判断。",
            "",
            f"- 状态：`{prior_art_coverage['prior_art_distinction_status']}`",
            f"- 区别项：{prior_art_coverage['complete_distinction_count']}/{prior_art_coverage['distinction_count']}",
            f"- 覆盖率：{prior_art_coverage['prior_art_distinction_coverage_rate']}",
            f"- 缺失 claim 覆盖：{prior_art_coverage['missing_claim_coverage']}",
            f"- 缺失 feature 覆盖：{prior_art_coverage['missing_feature_coverage']}",
            f"- 缺失 effect 覆盖：{prior_art_coverage['missing_effect_coverage']}",
            f"- 需要正式检索：{prior_art_coverage['formal_search_required']}",
            f"- 允许新颖性/创造性结论：{prior_art_coverage['novelty_or_inventiveness_opinion_allowed']}",
            f"- 机器可读矩阵：`{PRIOR_ART_DISTINCTION_PATH.relative_to(PROJECT_ROOT)}`",
            "",
            "| 区别项 | 已知方法族 | 区别组合 | 风险 | 从属回退路线 | 边界 |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for distinction in metrics["prior_art_distinction_matrix"]:
        lines.append(
            "| "
            f"{distinction['distinction_id']} | "
            f"{distinction['prior_art_family']} | "
            f"{distinction['distinguishing_combination']} | "
            f"{distinction['novelty_risk_level']}；{distinction['combination_risk']} | "
            f"{distinction['dependent_fallback_path']} | "
            f"{distinction['failure_boundary']} |"
        )
    lines.append("")
    formal_search_coverage = metrics["formal_search_work_package_coverage"]
    lines.extend(
        [
            "## 正式检索工作包与 Claim 收窄路线",
            "",
            "说明：该矩阵只生成检索任务和 fallback 路线，不是检索结果、法律意见或授权判断。",
            "",
            f"- 状态：`{formal_search_coverage['formal_search_work_package_status']}`",
            f"- 工作包：{formal_search_coverage['complete_work_package_count']}/{formal_search_coverage['work_package_count']}",
            f"- 覆盖率：{formal_search_coverage['formal_search_work_package_coverage_rate']}",
            f"- 缺失 PAD 覆盖：{formal_search_coverage['missing_distinction_coverage']}",
            f"- 正式检索已完成：{formal_search_coverage['formal_search_completed']}",
            f"- 允许法律意见：{formal_search_coverage['legal_opinion_allowed']}",
            f"- 机器可读矩阵：`{FORMAL_SEARCH_WORK_PACKAGES_PATH.relative_to(PROJECT_ROOT)}`",
            "",
            "| 工作包 | 关联区别项 | 检索目标 | 检索库 | 检索式数 | Claim fallback | 决策规则 |",
            "| --- | --- | --- | --- | ---: | --- | --- |",
        ]
    )
    for work_package in metrics["formal_search_work_package_matrix"]:
        query_count = len(work_package["english_search_queries"]) + len(work_package["chinese_search_queries"])
        lines.append(
            "| "
            f"{work_package['work_package_id']} | "
            f"{', '.join(work_package['linked_distinction_ids'])} | "
            f"{work_package['search_objective']} | "
            f"{', '.join(work_package['search_databases'])} | "
            f"{query_count} | "
            f"{work_package['claim_fallback_if_prior_art_found']} | "
            f"{work_package['decision_rule']} |"
        )
    lines.append("")
    intake_coverage = metrics["formal_search_result_intake_coverage"]
    lines.extend(
        [
            "## 正式检索结果接收 Schema",
            "",
            "说明：该 schema 只定义检索结果如何提交、比对和阻断；不是 prior-art 结果或法律意见。",
            "",
            f"- 状态：`{intake_coverage['formal_search_result_intake_status']}`",
            f"- Intake schema：{intake_coverage['complete_intake_count']}/{intake_coverage['intake_count']}",
            f"- 覆盖率：{intake_coverage['formal_search_result_intake_coverage_rate']}",
            f"- 缺失 work package 覆盖：{intake_coverage['missing_work_package_coverage']}",
            f"- 已提供检索结果：{intake_coverage['formal_search_result_supplied']}",
            f"- accepted hit 数：{intake_coverage['accepted_hit_count']}",
            f"- 可生成 prior-art 结论：{intake_coverage['can_generate_prior_art_result']}",
            f"- 机器可读 schema：`{FORMAL_SEARCH_RESULT_INTAKE_PATH.relative_to(PROJECT_ROOT)}`",
            "",
            "| Intake | 工作包 | 输入工件 | Hit 字段数 | Comparison 字段数 | 阻断条件 |",
            "| --- | --- | --- | ---: | ---: | --- |",
        ]
    )
    for intake in metrics["formal_search_result_intake_schema"]:
        lines.append(
            "| "
            f"{intake['intake_id']} | "
            f"{intake['linked_work_package_id']} | "
            f"{', '.join(intake['input_artifacts'])} | "
            f"{len(intake['required_hit_table_fields'])} | "
            f"{len(intake['required_claim_element_comparison_fields'])} | "
            f"{'<br>'.join(intake['blocking_conditions'])} |"
        )
    lines.append("")
    validation_coverage = metrics["formal_search_result_validation_gate_coverage"]
    lines.extend(
        [
            "## 正式检索结果验证门",
            "",
            "说明：该 gate 验证外部/人工检索结果包的字段、来源、查询 provenance、claim element comparison 和 reviewer 边界；当前没有结果包，因此不会生成 prior-art 结论。",
            "",
            f"- 状态：`{validation_coverage['formal_search_result_validation_gate_status']}`",
            f"- Validation gate：{validation_coverage['complete_validation_gate_count']}/{validation_coverage['validation_gate_count']}",
            f"- 覆盖率：{validation_coverage['formal_search_result_validation_gate_coverage_rate']}",
            f"- 缺失 intake 覆盖：{validation_coverage['missing_intake_coverage']}",
            f"- 已提供结果包：{validation_coverage['formal_search_result_package_supplied']}",
            f"- validated hit 数：{validation_coverage['validated_hit_count']}",
            f"- rejected hit 数：{validation_coverage['rejected_hit_count']}",
            f"- 可生成 prior-art 结论：{validation_coverage['can_generate_prior_art_result']}",
            f"- 机器可读 gate：`{FORMAL_SEARCH_RESULT_VALIDATION_GATE_PATH.relative_to(PROJECT_ROOT)}`",
            "",
            "| Gate | Intake | 工作包 | 来源库 | 查询来源数 | 运行时验证步骤 | Patch outputs |",
            "| --- | --- | --- | --- | ---: | --- | --- |",
        ]
    )
    for gate in metrics["formal_search_result_validation_gate"]:
        lines.append(
            "| "
            f"{gate['validation_gate_id']} | "
            f"{gate['linked_intake_id']} | "
            f"{gate['linked_work_package_id']} | "
            f"{', '.join(gate['allowed_source_databases'])} | "
            f"{len(gate['allowed_query_sources'])} | "
            f"{'<br>'.join(gate['runtime_validation_steps'])} | "
            f"{'<br>'.join(gate['patch_plan_outputs'])} |"
        )
    lines.append("")
    package_template_coverage = metrics["formal_search_result_package_template_coverage"]
    submission_template = metrics["formal_search_result_package_submission_template"]
    package_preflight = metrics["formal_search_result_package_source_preflight"]
    row_preflight = metrics["formal_search_result_package_row_preflight"]
    validation_execution = metrics["formal_search_result_validation_execution"]
    nonlegal_review_packet = metrics["formal_search_nonlegal_comparison_review_packet"]
    nonlegal_response_template = metrics["formal_search_nonlegal_review_response_template"]
    nonlegal_response_preflight = metrics[
        "formal_search_nonlegal_review_response_source_preflight"
    ]
    claim_scope_patch_draft = metrics["formal_search_claim_scope_patch_draft"]
    formal_counsel_template = metrics["formal_counsel_review_response_template"]
    formal_counsel_preflight = metrics["formal_counsel_review_response_source_preflight"]
    disclosure_revision_queue = metrics["formal_disclosure_revision_queue"]
    disclosure_revision_impact_plan = metrics["formal_disclosure_revision_impact_plan"]
    formal_search_review_readiness = metrics["formal_search_review_readiness"]
    formal_search_execution_route_plan = metrics["formal_search_execution_route_plan"]
    lines.extend(
        [
            "## 正式检索结果包模板与 Source Preflight",
            "",
            "说明：该层把 validation gate 前移为可提交的 JSON 包合同，并生成可填报 submission skeleton；source preflight 会检查 source/path/root shape 和 TODO/template markers。没有真实结果包时仍保持等待，不生成 prior-art 结论。",
            "",
            f"- 模板状态：`{package_template_coverage['formal_search_result_package_template_status']}`",
            f"- 模板覆盖率：{package_template_coverage['formal_search_result_package_template_coverage_rate']}",
            f"- Submission skeleton：`{submission_template['submission_template_status']}`",
            f"- Source preflight：`{package_preflight['formal_search_result_package_source_status']}`",
            f"- Row preflight：`{row_preflight['formal_search_result_package_row_preflight_status']}`",
            f"- 结果包路径：`{package_preflight['formal_search_result_package_path'] or package_preflight['expected_env_var']}`",
            f"- Template marker gaps：{package_preflight['template_marker_gap_count']}",
            f"- Row gaps：{row_preflight['row_gap_count']}",
            f"- Comparison coverage gaps：{row_preflight['comparison_coverage_gap_count']}",
            f"- Reviewer boundary gaps：{row_preflight['forbidden_review_boundary_count']}",
            f"- 可进入 validation gate：{package_preflight['can_route_to_validation_gate']}",
            f"- 行级可进入 validation gate：{row_preflight['can_route_to_validation_gate']}",
            f"- Validation execution：`{validation_execution['formal_search_result_validation_execution_status']}`",
            f"- Execution validated hit 数：{validation_execution['validated_hit_count']}",
            f"- Execution rejected hit 数：{validation_execution['rejected_hit_count']}",
            f"- 可进入人工非法律比较审查：{validation_execution['can_enter_human_nonlegal_comparison_review']}",
            f"- 非法律比较审查包：`{nonlegal_review_packet['formal_search_nonlegal_comparison_review_packet_status']}`",
            f"- 审查包行数：{nonlegal_review_packet['review_packet_row_count']}",
            f"- 非法律审查回填模板：`{nonlegal_response_template['formal_search_nonlegal_review_response_template_status']}`",
            f"- 非法律审查回填 preflight：`{nonlegal_response_preflight['formal_search_nonlegal_review_response_source_status']}`",
            f"- 回填 accepted/rejected row：{nonlegal_response_preflight['accepted_review_row_count']} / {nonlegal_response_preflight['rejected_review_row_count']}",
            f"- Claim scope patch draft：`{claim_scope_patch_draft['formal_search_claim_scope_patch_draft_status']}`",
            f"- Draft patch row：{claim_scope_patch_draft['draft_patch_count']}",
            f"- 可进入正式专利代理人审查：{claim_scope_patch_draft['can_route_to_formal_counsel_review']}",
            f"- 可直接生成权利要求文本：{claim_scope_patch_draft['can_emit_claim_text']}",
            f"- Formal counsel review template：`{formal_counsel_template['formal_counsel_review_response_template_status']}`",
            f"- Formal counsel review preflight：`{formal_counsel_preflight['formal_counsel_review_response_source_status']}`",
            f"- 可进入技术交底修订队列：{formal_counsel_preflight['can_route_to_disclosure_revision_queue']}",
            f"- Disclosure revision queue：`{disclosure_revision_queue['formal_disclosure_revision_queue_status']}`",
            f"- Disclosure revision item：{disclosure_revision_queue['revision_item_count']}",
            f"- 可交给人工交底编辑：{disclosure_revision_queue['can_route_to_disclosure_editor']}",
            f"- 可自动应用修订：{disclosure_revision_queue['can_apply_disclosure_revision_automatically']}",
            f"- Disclosure revision impact plan：`{disclosure_revision_impact_plan['formal_disclosure_revision_impact_plan_status']}`",
            f"- Revision impact item：{disclosure_revision_impact_plan['revision_impact_item_count']}",
            f"- 可交给人工工件修订：{disclosure_revision_impact_plan['can_route_to_human_artifact_revision']}",
            f"- 可自动改写核心工件：{disclosure_revision_impact_plan['can_apply_artifact_patch_automatically']}",
            f"- Formal search review readiness：`{formal_search_review_readiness['formal_search_review_readiness_status']}`",
            f"- 最高优先阻塞：`{formal_search_review_readiness['highest_priority_blocker']}`",
            f"- 下一步人工动作：`{formal_search_review_readiness['next_operator_action']}`",
            f"- 边界违规数：{formal_search_review_readiness['boundary_violation_count']}",
            f"- Formal search execution route plan：`{formal_search_execution_route_plan['route_plan_status']}`",
            f"- 检索路线数：{formal_search_execution_route_plan['complete_route_row_count']} / {formal_search_execution_route_plan['route_row_count']}",
            f"- 首个执行动作：`{formal_search_execution_route_plan['operator_first_action']}`",
            f"- 可生成 prior-art 结论：{package_preflight['can_generate_prior_art_result']}",
            f"- 机器可读模板：`{FORMAL_SEARCH_RESULT_PACKAGE_TEMPLATE_PATH.relative_to(PROJECT_ROOT)}`",
            f"- 可填报 skeleton：`{FORMAL_SEARCH_RESULT_PACKAGE_SUBMISSION_TEMPLATE_PATH.relative_to(PROJECT_ROOT)}`",
            f"- 机器可读 preflight：`{FORMAL_SEARCH_RESULT_PACKAGE_PREFLIGHT_PATH.relative_to(PROJECT_ROOT)}`",
            f"- 行级 preflight：`{FORMAL_SEARCH_RESULT_PACKAGE_ROW_PREFLIGHT_PATH.relative_to(PROJECT_ROOT)}`",
            f"- Validation execution：`{FORMAL_SEARCH_RESULT_VALIDATION_EXECUTION_PATH.relative_to(PROJECT_ROOT)}`",
            f"- 非法律比较审查包：`{FORMAL_SEARCH_NONLEGAL_COMPARISON_REVIEW_PACKET_PATH.relative_to(PROJECT_ROOT)}`",
            f"- 非法律审查回填模板：`{FORMAL_SEARCH_NONLEGAL_REVIEW_RESPONSE_TEMPLATE_PATH.relative_to(PROJECT_ROOT)}`",
            f"- 非法律审查回填 preflight：`{FORMAL_SEARCH_NONLEGAL_REVIEW_RESPONSE_PREFLIGHT_PATH.relative_to(PROJECT_ROOT)}`",
            f"- Claim scope patch draft：`{FORMAL_SEARCH_CLAIM_SCOPE_PATCH_DRAFT_PATH.relative_to(PROJECT_ROOT)}`",
            f"- Formal counsel review template：`{FORMAL_COUNSEL_REVIEW_RESPONSE_TEMPLATE_PATH.relative_to(PROJECT_ROOT)}`",
            f"- Formal counsel review preflight：`{FORMAL_COUNSEL_REVIEW_RESPONSE_PREFLIGHT_PATH.relative_to(PROJECT_ROOT)}`",
            f"- Disclosure revision queue：`{FORMAL_DISCLOSURE_REVISION_QUEUE_PATH.relative_to(PROJECT_ROOT)}`",
            f"- Disclosure revision impact plan：`{FORMAL_DISCLOSURE_REVISION_IMPACT_PLAN_PATH.relative_to(PROJECT_ROOT)}`",
            f"- Formal search review readiness：`{FORMAL_SEARCH_REVIEW_READINESS_PATH.relative_to(PROJECT_ROOT)}`",
            f"- Formal search execution route plan：`{FORMAL_SEARCH_EXECUTION_ROUTE_PLAN_PATH.relative_to(PROJECT_ROOT)}`",
            "",
            "| Template | Gate | 工作包 | 必需表 | 来源库 |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for template in metrics["formal_search_result_package_template"]:
        lines.append(
            "| "
            f"{template['package_template_id']} | "
            f"{template['linked_validation_gate_id']} | "
            f"{template['linked_work_package_id']} | "
            f"{', '.join(template['required_result_tables'])} | "
            f"{', '.join(template['allowed_source_databases'])} |"
        )
    lines.append("")
    lines.extend(
        [
            "## 模块板块",
            "",
            "| 模块 | 类型 | Agent 数 | 核心锚点 | 处理策略 |",
            "| --- | --- | ---: | --- | --- |",
        ]
    )
    for module in metrics["module_board"]:
        lines.append(
            "| "
            f"{module['module_id']} {module['title']} | "
            f"{module['module_type']} | "
            f"{module['agent_count']} | "
            f"{', '.join(module['core_anchor_agents']) or '-'} | "
            f"{module['module_consolidation_policy']} |"
        )
    lines.extend(
        [
            "",
            "## 冗余与合并簇",
            "",
        ]
    )
    for cluster in metrics["redundancy_clusters"]:
        lines.extend(
            [
                f"### {cluster['cluster_id']}",
                "",
                f"- 类型：{cluster['cluster_type']}",
                f"- 优先级：{cluster['priority']}",
                f"- Agent：{', '.join(cluster['agents']) or '-'}",
                f"- 合并原因：{cluster['why_redundant']}",
                f"- 合并目标：{cluster['consolidation_target']}",
                f"- 保留指标：{', '.join(cluster['preserve_metrics'])}",
                "",
            ]
        )
    lines.extend(
        [
            "## 边界",
            "",
            "- 本轮是模型架构复盘与减冗治理，不产生 field-supported 结论。",
            "- 不删除历史代码；先通过模块 facade、统一接口和指标契约压缩复杂度。",
            "- synthetic/sample 仍只能作为仿真基线和接口验证，不能写执行器或 release gate。",
            "",
        ]
    )
    return "\n".join(lines)


def _deliverable_md(report) -> str:
    metrics = report.metrics
    lines = [
        "# 模型架构复盘与减冗治理",
        "",
        "## 核心判断",
        "",
        f"当前系统已经不适合继续按 agent 编号线性理解。更高价值的做法是把 {metrics['agent_count']} 个历史 agent 压缩到少数核心模块，"
        "并检查每个模块是否真正提升观测、推理、控制、验证或工程可执行性。",
        "Agent60 只作为本轮复盘治理工具存在，不计入原有模型能力链。",
        "",
        f"- 已映射 Agent：{metrics['mapped_agent_count']}/{metrics['agent_count']}",
        f"- 模块数：{metrics['module_count']}",
        f"- 七层系统骨架覆盖率：{metrics['system_spine_coverage']['layer_coverage_rate']}",
        f"- 六类系统能力覆盖率：{metrics['system_spine_coverage']['ability_coverage_rate']}",
        f"- 模块接口契约覆盖率：{metrics['interface_contract_coverage']['interface_contract_coverage_rate']}",
        f"- 核心锚点覆盖率：{metrics['core_anchor_coverage']['coverage_rate']}",
        f"- 冗余/合并簇数：{metrics['redundancy_cluster_count']}",
        f"- 展示层冻结数：{metrics['presentation_freeze_agent_count']}",
        "",
    ]
    lines.extend(
        [
            "## 全局七层系统骨架映射",
            "",
            "| 层级 | 模块 | 能力 | 状态 |",
            "| --- | --- | --- | --- |",
        ]
    )
    for layer in metrics["system_layer_board"]:
        lines.append(
            "| "
            f"{layer['layer_id']} {layer['title']} | "
            f"{', '.join(layer['modules']) or '-'} | "
            f"{', '.join(layer['core_abilities']) or '-'} | "
            f"{layer['coverage_status']} |"
        )
    lines.extend(
        [
            "",
            "## 模块接口契约矩阵",
            "",
            "这一部分对应全局 goal 中“先定义接口，再扩展功能”的原则。它检查每个模块是否具备输入、输出、状态变量、证据来源、可传递指标、不能做什么、上下游依赖和现场验证需求，而不是只保留一个抽象名称。",
            "",
            "| 模块 | 关键状态变量 | 可传递指标 | 上游依赖 | 下游消费者 | 不能做 |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for contract in metrics["module_interface_contracts"]:
        lines.append(
            "| "
            f"{contract['module_id']} {contract['module_title']} | "
            f"{', '.join(contract['state_variables'])} | "
            f"{', '.join(contract['transferable_metrics'])} | "
            f"{', '.join(contract['upstream_dependencies'])} | "
            f"{', '.join(contract['downstream_consumers'])} | "
            f"{contract['cannot_do']} |"
        )
    patent_coverage = metrics["patent_technical_feature_coverage"]
    lines.extend(
        [
            "",
            "## 专利级技术特征 Ledger",
            "",
            "这部分不是把项目转成专利文本，而是用专利交底的严谨度反向检查模型：每个核心特征必须说清技术问题、技术手段、状态变量、控制动作、验证指标、技术效果、现有技术区别和失败边界。",
            "",
            f"- 状态：`{patent_coverage['patent_technical_feature_status']}`",
            f"- 技术特征覆盖率：{patent_coverage['technical_feature_coverage_rate']}",
            f"- 机器可读 ledger：`{PATENT_TECHNICAL_FEATURE_LEDGER_PATH.relative_to(PROJECT_ROOT)}`",
            f"- 现场 claim 升级边界：{patent_coverage['field_claim_upgrade_boundary']}",
            "",
            "| 特征 | 模块 | 技术手段 | 技术效果 | 现有技术区别 | Claim 骨架角色 |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for feature in metrics["patent_technical_feature_ledger"]:
        lines.append(
            "| "
            f"{feature['feature_id']} | "
            f"{feature['module_id']} | "
            f"{feature['technical_means']} | "
            f"{feature['technical_effect']} | "
            f"{feature['prior_art_distinction']} | "
            f"{feature['claim_skeleton_role']} |"
        )
    claim_coverage = metrics["technical_claim_skeleton_coverage"]
    lines.extend(
        [
            "",
            "## 技术方案 Claim Skeleton Scaffold",
            "",
            "这部分把技术特征组合成“主方法/系统 + 从属或分案方向”的技术骨架。它不是法律权利要求文本，也不是授权判断；作用是检查系统主链是否已经能被清楚拆成可实施、可验证、可对比的技术方案。",
            "",
            f"- 状态：`{claim_coverage['technical_claim_skeleton_status']}`",
            f"- Claim scaffold 覆盖率：{claim_coverage['technical_claim_skeleton_coverage_rate']}",
            f"- 机器可读 scaffold：`{TECHNICAL_CLAIM_SKELETON_PATH.relative_to(PROJECT_ROOT)}`",
            f"- 现场 claim 升级边界：{claim_coverage['field_claim_upgrade_boundary']}",
            "",
            "| Scaffold | 类型 | 映射特征 | 技术效果 | 现有技术区别 |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for claim in metrics["technical_claim_skeleton_scaffold"]:
        lines.append(
            "| "
            f"{claim['claim_id']} | "
            f"{claim['claim_type']} | "
            f"{', '.join(claim['mapped_feature_ids'])} | "
            f"{claim['technical_effect']} | "
            f"{claim['prior_art_distinction']} |"
        )
    embodiment_coverage = metrics["technical_embodiment_validation_coverage"]
    lines.extend(
        [
            "",
            "## 技术实施例与验证矩阵",
            "",
            "这部分把 claim skeleton 落成实施例、所需数据包、验证门和验收指标。它仍然只是实施例 scaffold；没有真实 field package、replay、holdout 和 operator review 时，不能生成现场结论。",
            "",
            f"- 状态：`{embodiment_coverage['technical_embodiment_validation_status']}`",
            f"- 实施例覆盖率：{embodiment_coverage['technical_embodiment_validation_coverage_rate']}",
            f"- 机器可读矩阵：`{TECHNICAL_EMBODIMENT_VALIDATION_PATH.relative_to(PROJECT_ROOT)}`",
            f"- 证据边界：{embodiment_coverage['evidence_boundary']}",
            "",
            "| 实施例 | 场景 | 技术效果待测量项 | 当前证据状态 |",
            "| --- | --- | --- | --- |",
        ]
    )
    for embodiment in metrics["technical_embodiment_validation_matrix"]:
        lines.append(
            "| "
            f"{embodiment['embodiment_id']} | "
            f"{embodiment['scenario']} | "
            f"{embodiment['technical_effect_to_measure']} | "
            f"{embodiment['current_evidence_status']} |"
        )
    effect_coverage = metrics["technical_effect_measurement_coverage"]
    lines.extend(
        [
            "",
            "## 技术效果度量矩阵",
            "",
            "这部分把实施例中的“效果”继续压成可度量合同：相对什么基线、看哪些指标、需要什么阈值、通过哪个 gate、失败时如何保持阻断。它的作用是让后续 field package 到来后能直接验收，而不是提前宣称现场成立。",
            "",
            f"- 状态：`{effect_coverage['technical_effect_measurement_status']}`",
            f"- 技术效果覆盖率：{effect_coverage['technical_effect_measurement_coverage_rate']}",
            f"- 机器可读矩阵：`{TECHNICAL_EFFECT_MEASUREMENT_PATH.relative_to(PROJECT_ROOT)}`",
            f"- 证据边界：{effect_coverage['evidence_boundary']}",
            "",
            "| 技术效果 | 关联实施例 | 基线对照 | 核心指标 | 当前证据状态 |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for effect in metrics["technical_effect_measurement_matrix"]:
        lines.append(
            "| "
            f"{effect['effect_id']} | "
            f"{', '.join(effect['linked_embodiment_ids'])} | "
            f"{effect['baseline_comparator']} | "
            f"{', '.join(effect['measurement_metrics'])} | "
            f"{effect['current_evidence_status']} |"
        )
    prior_art_coverage = metrics["prior_art_distinction_coverage"]
    lines.extend(
        [
            "",
            "## 现有技术区别与保护性风险矩阵",
            "",
            "这部分把潜在 claim、技术特征和技术效果映射到已有方法族，检查项目的区别点是否足够具体。它不是正式专利检索，也不是法律意见；作用是提前暴露“只是普通 AI/软传感/多智能体”的风险，并给出从属回退方向。",
            "",
            f"- 状态：`{prior_art_coverage['prior_art_distinction_status']}`",
            f"- 区别矩阵覆盖率：{prior_art_coverage['prior_art_distinction_coverage_rate']}",
            f"- 机器可读矩阵：`{PRIOR_ART_DISTINCTION_PATH.relative_to(PROJECT_ROOT)}`",
            f"- 证据边界：{prior_art_coverage['evidence_boundary']}",
            "",
            "| 区别项 | 已知方法族 | 区别组合 | 风险等级 | 正式检索需求 |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for distinction in metrics["prior_art_distinction_matrix"]:
        lines.append(
            "| "
            f"{distinction['distinction_id']} | "
            f"{distinction['prior_art_family']} | "
            f"{distinction['distinguishing_combination']} | "
            f"{distinction['novelty_risk_level']} | "
            f"{', '.join(distinction['verification_needed'])} |"
        )
    formal_search_coverage = metrics["formal_search_work_package_coverage"]
    lines.extend(
        [
            "",
            "## 正式检索工作包与 Claim 收窄路线",
            "",
            "这部分把区别假设继续转成可执行检索任务：去哪里搜、搜什么、收集什么证据、发现相似现有技术后如何收窄 claim。它不是检索结果，也不允许给出新颖性或创造性判断。",
            "",
            f"- 状态：`{formal_search_coverage['formal_search_work_package_status']}`",
            f"- 工作包覆盖率：{formal_search_coverage['formal_search_work_package_coverage_rate']}",
            f"- 机器可读矩阵：`{FORMAL_SEARCH_WORK_PACKAGES_PATH.relative_to(PROJECT_ROOT)}`",
            f"- 证据边界：{formal_search_coverage['evidence_boundary']}",
            "",
            "| 工作包 | 关联区别项 | 搜索目标 | 回退路线 |",
            "| --- | --- | --- | --- |",
        ]
    )
    for work_package in metrics["formal_search_work_package_matrix"]:
        lines.append(
            "| "
            f"{work_package['work_package_id']} | "
            f"{', '.join(work_package['linked_distinction_ids'])} | "
            f"{work_package['search_objective']} | "
            f"{work_package['claim_fallback_if_prior_art_found']} |"
        )
    intake_coverage = metrics["formal_search_result_intake_coverage"]
    lines.extend(
        [
            "",
            "## 正式检索结果接收 Schema",
            "",
            "这部分规定正式检索结果回来后必须如何提交：每条命中要有来源、检索式、命中的 claim 元素、缺失元素、风险信号和 reviewer 状态；claim element comparison 必须逐项标记项目元素与现有技术披露的关系。",
            "",
            f"- 状态：`{intake_coverage['formal_search_result_intake_status']}`",
            f"- Intake 覆盖率：{intake_coverage['formal_search_result_intake_coverage_rate']}",
            f"- 机器可读 schema：`{FORMAL_SEARCH_RESULT_INTAKE_PATH.relative_to(PROJECT_ROOT)}`",
            f"- 证据边界：{intake_coverage['evidence_boundary']}",
            "",
            "| Intake | 工作包 | 接收状态 | 当前命中数 |",
            "| --- | --- | --- | ---: |",
        ]
    )
    for intake in metrics["formal_search_result_intake_schema"]:
        lines.append(
            "| "
            f"{intake['intake_id']} | "
            f"{intake['linked_work_package_id']} | "
            f"{intake['intake_status']} | "
            f"{intake['accepted_hit_count']} |"
        )
    validation_coverage = metrics["formal_search_result_validation_gate_coverage"]
    lines.extend(
        [
            "",
            "## 正式检索结果验证门",
            "",
            "这部分把接收 schema 进一步转成运行时 gate：检查结果包是否能读、字段是否完整、来源库和检索式是否可追溯、claim element comparison 是否覆盖项目元素、reviewer 字段是否越界。它仍然不是法律意见，也不会在没有外部/人工检索结果时生成 prior-art 结论。",
            "",
            f"- 状态：`{validation_coverage['formal_search_result_validation_gate_status']}`",
            f"- Gate 覆盖率：{validation_coverage['formal_search_result_validation_gate_coverage_rate']}",
            f"- 机器可读 gate：`{FORMAL_SEARCH_RESULT_VALIDATION_GATE_PATH.relative_to(PROJECT_ROOT)}`",
            f"- 证据边界：{validation_coverage['evidence_boundary']}",
            "",
            "| Gate | Intake | 工作包 | 状态 | 当前 validated hit |",
            "| --- | --- | --- | --- | ---: |",
        ]
    )
    for gate in metrics["formal_search_result_validation_gate"]:
        lines.append(
            "| "
            f"{gate['validation_gate_id']} | "
            f"{gate['linked_intake_id']} | "
            f"{gate['linked_work_package_id']} | "
            f"{gate['validation_gate_status']} | "
            f"{gate['validated_hit_count']} |"
        )
    package_template_coverage = metrics["formal_search_result_package_template_coverage"]
    submission_template = metrics["formal_search_result_package_submission_template"]
    package_preflight = metrics["formal_search_result_package_source_preflight"]
    row_preflight = metrics["formal_search_result_package_row_preflight"]
    validation_execution = metrics["formal_search_result_validation_execution"]
    nonlegal_review_packet = metrics["formal_search_nonlegal_comparison_review_packet"]
    nonlegal_response_template = metrics["formal_search_nonlegal_review_response_template"]
    nonlegal_response_preflight = metrics[
        "formal_search_nonlegal_review_response_source_preflight"
    ]
    claim_scope_patch_draft = metrics["formal_search_claim_scope_patch_draft"]
    formal_counsel_template = metrics["formal_counsel_review_response_template"]
    formal_counsel_preflight = metrics["formal_counsel_review_response_source_preflight"]
    disclosure_revision_queue = metrics["formal_disclosure_revision_queue"]
    disclosure_revision_impact_plan = metrics["formal_disclosure_revision_impact_plan"]
    formal_search_review_readiness = metrics["formal_search_review_readiness"]
    formal_search_execution_route_plan = metrics["formal_search_execution_route_plan"]
    lines.extend(
        [
            "",
            "## 正式检索结果包模板与 Source Preflight",
            "",
            "这部分把 validation gate 前移成可提交的结果包合同，并提供可填报 submission skeleton。外部/人工检索结果需要按 package metadata、work package results、prior-art hit table、claim element comparison 和 fallback recommendation 的结构提交；source preflight 会先检查路径、JSON 根结构、工作包覆盖、必需表形状和 TODO/template markers。",
            "",
            f"- 模板状态：`{package_template_coverage['formal_search_result_package_template_status']}`",
            f"- Submission skeleton：`{submission_template['submission_template_status']}`",
            f"- Source preflight：`{package_preflight['formal_search_result_package_source_status']}`",
            f"- Row preflight：`{row_preflight['formal_search_result_package_row_preflight_status']}`",
            f"- Validation execution：`{validation_execution['formal_search_result_validation_execution_status']}`",
            f"- Execution validated/rejected hit：{validation_execution['validated_hit_count']} / {validation_execution['rejected_hit_count']}",
            f"- 可进入人工非法律比较审查：{validation_execution['can_enter_human_nonlegal_comparison_review']}",
            f"- 非法律比较审查包：`{nonlegal_review_packet['formal_search_nonlegal_comparison_review_packet_status']}`",
            f"- 审查包行数：{nonlegal_review_packet['review_packet_row_count']}",
            f"- 非法律审查回填模板：`{nonlegal_response_template['formal_search_nonlegal_review_response_template_status']}`",
            f"- 非法律审查回填 preflight：`{nonlegal_response_preflight['formal_search_nonlegal_review_response_source_status']}`",
            f"- 回填 accepted/rejected row：{nonlegal_response_preflight['accepted_review_row_count']} / {nonlegal_response_preflight['rejected_review_row_count']}",
            f"- Claim scope patch draft：`{claim_scope_patch_draft['formal_search_claim_scope_patch_draft_status']}`",
            f"- Draft patch row：{claim_scope_patch_draft['draft_patch_count']}",
            f"- 可进入正式专利代理人审查：{claim_scope_patch_draft['can_route_to_formal_counsel_review']}",
            f"- 可直接生成权利要求文本：{claim_scope_patch_draft['can_emit_claim_text']}",
            f"- Formal counsel review template：`{formal_counsel_template['formal_counsel_review_response_template_status']}`",
            f"- Formal counsel review preflight：`{formal_counsel_preflight['formal_counsel_review_response_source_status']}`",
            f"- 可进入技术交底修订队列：{formal_counsel_preflight['can_route_to_disclosure_revision_queue']}",
            f"- Disclosure revision queue：`{disclosure_revision_queue['formal_disclosure_revision_queue_status']}`",
            f"- Disclosure revision item：{disclosure_revision_queue['revision_item_count']}",
            f"- 可交给人工交底编辑：{disclosure_revision_queue['can_route_to_disclosure_editor']}",
            f"- 可自动应用修订：{disclosure_revision_queue['can_apply_disclosure_revision_automatically']}",
            f"- Disclosure revision impact plan：`{disclosure_revision_impact_plan['formal_disclosure_revision_impact_plan_status']}`",
            f"- Revision impact item：{disclosure_revision_impact_plan['revision_impact_item_count']}",
            f"- 可交给人工工件修订：{disclosure_revision_impact_plan['can_route_to_human_artifact_revision']}",
            f"- 可自动改写核心工件：{disclosure_revision_impact_plan['can_apply_artifact_patch_automatically']}",
            f"- Formal search review readiness：`{formal_search_review_readiness['formal_search_review_readiness_status']}`",
            f"- 最高优先阻塞：`{formal_search_review_readiness['highest_priority_blocker']}`",
            f"- 下一步人工动作：`{formal_search_review_readiness['next_operator_action']}`",
            f"- 边界违规数：{formal_search_review_readiness['boundary_violation_count']}",
            f"- Formal search execution route plan：`{formal_search_execution_route_plan['route_plan_status']}`",
            f"- 检索路线数：{formal_search_execution_route_plan['complete_route_row_count']} / {formal_search_execution_route_plan['route_row_count']}",
            f"- 首个执行动作：`{formal_search_execution_route_plan['operator_first_action']}`",
            f"- 机器可读模板：`{FORMAL_SEARCH_RESULT_PACKAGE_TEMPLATE_PATH.relative_to(PROJECT_ROOT)}`",
            f"- 可填报 skeleton：`{FORMAL_SEARCH_RESULT_PACKAGE_SUBMISSION_TEMPLATE_PATH.relative_to(PROJECT_ROOT)}`",
            f"- 机器可读 preflight：`{FORMAL_SEARCH_RESULT_PACKAGE_PREFLIGHT_PATH.relative_to(PROJECT_ROOT)}`",
            f"- 行级 preflight：`{FORMAL_SEARCH_RESULT_PACKAGE_ROW_PREFLIGHT_PATH.relative_to(PROJECT_ROOT)}`",
            f"- Validation execution：`{FORMAL_SEARCH_RESULT_VALIDATION_EXECUTION_PATH.relative_to(PROJECT_ROOT)}`",
            f"- 非法律比较审查包：`{FORMAL_SEARCH_NONLEGAL_COMPARISON_REVIEW_PACKET_PATH.relative_to(PROJECT_ROOT)}`",
            f"- 非法律审查回填模板：`{FORMAL_SEARCH_NONLEGAL_REVIEW_RESPONSE_TEMPLATE_PATH.relative_to(PROJECT_ROOT)}`",
            f"- 非法律审查回填 preflight：`{FORMAL_SEARCH_NONLEGAL_REVIEW_RESPONSE_PREFLIGHT_PATH.relative_to(PROJECT_ROOT)}`",
            f"- Claim scope patch draft：`{FORMAL_SEARCH_CLAIM_SCOPE_PATCH_DRAFT_PATH.relative_to(PROJECT_ROOT)}`",
            f"- Formal counsel review template：`{FORMAL_COUNSEL_REVIEW_RESPONSE_TEMPLATE_PATH.relative_to(PROJECT_ROOT)}`",
            f"- Formal counsel review preflight：`{FORMAL_COUNSEL_REVIEW_RESPONSE_PREFLIGHT_PATH.relative_to(PROJECT_ROOT)}`",
            f"- Disclosure revision queue：`{FORMAL_DISCLOSURE_REVISION_QUEUE_PATH.relative_to(PROJECT_ROOT)}`",
            f"- Disclosure revision impact plan：`{FORMAL_DISCLOSURE_REVISION_IMPACT_PLAN_PATH.relative_to(PROJECT_ROOT)}`",
            f"- Formal search review readiness：`{FORMAL_SEARCH_REVIEW_READINESS_PATH.relative_to(PROJECT_ROOT)}`",
            f"- Formal search execution route plan：`{FORMAL_SEARCH_EXECUTION_ROUTE_PLAN_PATH.relative_to(PROJECT_ROOT)}`",
            f"- 证据边界：{package_preflight['failure_boundary']}",
            "",
            "| Template | 工作包 | 必需表 | 状态 |",
            "| --- | --- | --- | --- |",
        ]
    )
    for template in metrics["formal_search_result_package_template"]:
        lines.append(
            "| "
            f"{template['package_template_id']} | "
            f"{template['linked_work_package_id']} | "
            f"{', '.join(template['required_result_tables'])} | "
            f"{template['package_template_status']} |"
        )
    lines.extend(["", "## 模块化视角", ""])
    for module in metrics["module_board"]:
        lines.extend(
            [
                f"### {module['module_id']} {module['title']}",
                "",
                f"- 类型：{module['module_type']}",
                f"- 作用：{module['model_role']}",
                f"- 核心问题：{module['core_question']}",
                f"- Agent 数：{module['agent_count']}",
                f"- 核心锚点：{', '.join(module['core_anchor_agents']) or '-'}",
                f"- 策略：{module['module_consolidation_policy']}",
                f"- 失败边界：{module['failure_boundary']}",
                "",
            ]
        )
    lines.extend(
        [
            "## 核心链路消费关系",
            "",
            "| 来源 | 消费者 | 接口 | 状态 | 边界 |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for edge in metrics["core_consumption_map"]:
        lines.append(
            "| "
            f"{edge['source_agent']} | "
            f"{', '.join(edge['consumer_agents'])} | "
            f"{edge['interface']} | "
            f"{edge['status']} | "
            f"{edge['field_boundary']} |"
        )
    top = metrics["ranked_refactor_actions"][0]
    fallback = metrics["offline_core_fallback_action"]
    lines.extend(
        [
            "",
            "## 当前最高边际价值重构",
            "",
            f"- 动作：`{top['action_id']}`",
            f"- 标题：{top['title']}",
            f"- 触发指标：{top['trigger_metric']}",
            f"- 原因：{top['why_now']}",
            f"- 路径：{top['implementation_path']}",
            f"- 禁止事项：{top['must_not_do']}",
            "",
        ]
    )
    if fallback.get("fallback_enabled"):
        lines.extend(
            [
                "## 无真实包时的离线核心 Fallback",
                "",
            f"- 动作：`{fallback['action_id']}`",
            f"- 标题：{fallback['title']}",
            f"- 原因：{fallback['reason']}",
                f"- 边界：{fallback['must_not_do']}",
                "",
            ]
        )
        if fallback.get("r7_completion_plan_status"):
            lines.extend(
                [
                    "- R7-to-R8p completion plan："
                    f"{fallback['r7_completion_plan_status']}",
                    f"- completion item 数：{fallback.get('r7_completion_item_count', 0)}",
                    "- completion item 分类："
                    f"{fallback.get('r7_completion_item_class_counts', {})}",
                        "- completion 字段缺口分类："
                        f"{fallback.get('r7_completion_field_gap_count_by_class', {})}",
                        "- completion route contracts："
                        f"{fallback.get('r7_completion_route_contracts_status', '')}",
                        f"- open route 数：{fallback.get('r7_completion_open_route_count', 0)}",
                        f"- open routes：{fallback.get('r7_completion_open_route_ids', [])}",
                        "- completion route work packages："
                        f"{fallback.get('r7_completion_route_work_packages_status', '')}",
                        f"- open work package 数：{fallback.get('r7_completion_open_work_package_count', 0)}",
                        f"- open work packages：{fallback.get('r7_completion_open_work_package_ids', [])}",
                        "- completion route work package preflight："
                        f"{fallback.get('r7_completion_route_work_package_preflight_status', '')}",
                        f"- submitted work package 数：{fallback.get('r7_completion_submitted_work_package_count', 0)}",
                        f"- passed work package 数：{fallback.get('r7_completion_passed_work_package_count', 0)}",
                        f"- blocked work package 数：{fallback.get('r7_completion_blocked_work_package_count', 0)}",
                        "- completion route work package patch plan："
                        f"{fallback.get('r7_completion_route_work_package_patch_plan_status', '')}",
                        f"- patch item 数：{fallback.get('r7_completion_route_work_package_patch_item_count', 0)}",
                        f"- highest patch：{fallback.get('r7_completion_route_work_package_highest_priority_patch_id', '')}",
                        "- completion route work package assembly gate："
                        f"{fallback.get('r7_completion_route_work_package_assembly_gate_status', '')}",
                        f"- assembly step 数：{fallback.get('r7_completion_route_work_package_assembly_step_count', 0)}",
                        f"- blocked assembly step 数：{fallback.get('r7_completion_route_work_package_blocked_assembly_step_count', 0)}",
                        "- submission readiness review："
                        f"{fallback.get('submission_readiness_review_status', '')}",
                        "- submission readiness next action："
                        f"{fallback.get('submission_readiness_next_operator_action', '')}",
                        "- submission readiness can route to R8v："
                        f"{fallback.get('submission_readiness_can_route_to_r8v', False)}",
                        "- source package route guide："
                        f"{fallback.get('source_package_route_guide_status', '')}",
                        "- source package recommended route："
                        f"{fallback.get('source_package_recommended_route_id', '')}",
                        "- source package next action："
                        f"{fallback.get('source_package_next_operator_action', '')}",
                        "- source package route preflight："
                        f"{fallback.get('source_package_route_preflight_status', '')}",
                        "- source package recommended route preflight："
                        f"{fallback.get('source_package_recommended_route_preflight_status', '')}",
                        "",
                    ]
                )
    lines.extend(
        [
            "## 复盘后的工作原则",
            "",
            "- 后续不再默认新增 agent；优先合并接口、回接主链、压缩重复 gate。",
            "- 展示层 agent 默认冻结，只有模型指标更新后同步。",
            "- 项目运维 agent 作为支持层，不参与当前核心优先级竞争。",
            "- Agent48/51/54、Agent49/52/55、Agent56/59 是当前最需要保持联动的三条核心轴。",
            "- 所有 field-related 输出必须继续区分 schema ready、synthetic replay ready、field validation required。",
            "",
        ]
    )
    return "\n".join(lines)


def _update_manifest(report) -> None:
    manifest = _read_optional_json(MANIFEST_PATH)
    top = report.metrics["ranked_refactor_actions"][0]
    fallback = report.metrics["offline_core_fallback_action"]
    manifest["status"] = f"Agent60 复盘治理已更新，下一步指向 {top['action_id']}"
    manifest["latest_regression"] = manifest.get("latest_regression", "pending after Agent60")
    manifest["agent_architecture_consolidation"] = {
        "audited_scope": "existing_59_agent_model_body",
        "architecture_consolidation": str(DELIVERABLE_PATH.relative_to(PROJECT_ROOT)),
        "agent60_report": str((OUT_DIR / "agent60_report.md").relative_to(PROJECT_ROOT)),
        "architecture_consolidation_metrics": str(METRICS_PATH.relative_to(PROJECT_ROOT)),
        "patent_technical_feature_ledger": str(PATENT_TECHNICAL_FEATURE_LEDGER_PATH.relative_to(PROJECT_ROOT)),
        "technical_claim_skeleton_scaffold": str(TECHNICAL_CLAIM_SKELETON_PATH.relative_to(PROJECT_ROOT)),
        "technical_embodiment_validation_matrix": str(
            TECHNICAL_EMBODIMENT_VALIDATION_PATH.relative_to(PROJECT_ROOT)
        ),
        "technical_effect_measurement_matrix": str(
            TECHNICAL_EFFECT_MEASUREMENT_PATH.relative_to(PROJECT_ROOT)
        ),
        "prior_art_distinction_matrix": str(
            PRIOR_ART_DISTINCTION_PATH.relative_to(PROJECT_ROOT)
        ),
        "formal_search_work_packages": str(
            FORMAL_SEARCH_WORK_PACKAGES_PATH.relative_to(PROJECT_ROOT)
        ),
        "formal_search_result_intake_schema": str(
            FORMAL_SEARCH_RESULT_INTAKE_PATH.relative_to(PROJECT_ROOT)
        ),
        "formal_search_result_validation_gate": str(
            FORMAL_SEARCH_RESULT_VALIDATION_GATE_PATH.relative_to(PROJECT_ROOT)
        ),
        "formal_search_result_package_template": str(
            FORMAL_SEARCH_RESULT_PACKAGE_TEMPLATE_PATH.relative_to(PROJECT_ROOT)
        ),
        "formal_search_result_package_submission_template": str(
            FORMAL_SEARCH_RESULT_PACKAGE_SUBMISSION_TEMPLATE_PATH.relative_to(PROJECT_ROOT)
        ),
        "formal_search_result_package_source_preflight": str(
            FORMAL_SEARCH_RESULT_PACKAGE_PREFLIGHT_PATH.relative_to(PROJECT_ROOT)
        ),
        "formal_search_result_package_row_preflight": str(
            FORMAL_SEARCH_RESULT_PACKAGE_ROW_PREFLIGHT_PATH.relative_to(PROJECT_ROOT)
        ),
        "formal_search_result_validation_execution": str(
            FORMAL_SEARCH_RESULT_VALIDATION_EXECUTION_PATH.relative_to(PROJECT_ROOT)
        ),
        "formal_search_nonlegal_comparison_review_packet": str(
            FORMAL_SEARCH_NONLEGAL_COMPARISON_REVIEW_PACKET_PATH.relative_to(PROJECT_ROOT)
        ),
        "formal_search_nonlegal_review_response_template": str(
            FORMAL_SEARCH_NONLEGAL_REVIEW_RESPONSE_TEMPLATE_PATH.relative_to(PROJECT_ROOT)
        ),
        "formal_search_nonlegal_review_response_source_preflight": str(
            FORMAL_SEARCH_NONLEGAL_REVIEW_RESPONSE_PREFLIGHT_PATH.relative_to(PROJECT_ROOT)
        ),
        "formal_search_claim_scope_patch_draft": str(
            FORMAL_SEARCH_CLAIM_SCOPE_PATCH_DRAFT_PATH.relative_to(PROJECT_ROOT)
        ),
        "formal_counsel_review_response_template": str(
            FORMAL_COUNSEL_REVIEW_RESPONSE_TEMPLATE_PATH.relative_to(PROJECT_ROOT)
        ),
        "formal_counsel_review_response_source_preflight": str(
            FORMAL_COUNSEL_REVIEW_RESPONSE_PREFLIGHT_PATH.relative_to(PROJECT_ROOT)
        ),
        "formal_disclosure_revision_queue": str(
            FORMAL_DISCLOSURE_REVISION_QUEUE_PATH.relative_to(PROJECT_ROOT)
        ),
        "formal_disclosure_revision_impact_plan": str(
            FORMAL_DISCLOSURE_REVISION_IMPACT_PLAN_PATH.relative_to(PROJECT_ROOT)
        ),
        "formal_search_review_readiness": str(
            FORMAL_SEARCH_REVIEW_READINESS_PATH.relative_to(PROJECT_ROOT)
        ),
        "formal_search_execution_route_plan": str(
            FORMAL_SEARCH_EXECUTION_ROUTE_PLAN_PATH.relative_to(PROJECT_ROOT)
        ),
    }
    patent_coverage = report.metrics["patent_technical_feature_coverage"]
    claim_coverage = report.metrics["technical_claim_skeleton_coverage"]
    embodiment_coverage = report.metrics["technical_embodiment_validation_coverage"]
    effect_coverage = report.metrics["technical_effect_measurement_coverage"]
    prior_art_coverage = report.metrics["prior_art_distinction_coverage"]
    formal_search_coverage = report.metrics["formal_search_work_package_coverage"]
    intake_coverage = report.metrics["formal_search_result_intake_coverage"]
    validation_coverage = report.metrics["formal_search_result_validation_gate_coverage"]
    package_template_coverage = report.metrics["formal_search_result_package_template_coverage"]
    package_preflight = report.metrics["formal_search_result_package_source_preflight"]
    manifest["latest_agent60_patent_technical_feature_ledger"] = str(
        PATENT_TECHNICAL_FEATURE_LEDGER_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_agent60_patent_technical_feature_status"] = patent_coverage.get(
        "patent_technical_feature_status",
        "",
    )
    manifest["latest_agent60_patent_technical_feature_count"] = patent_coverage.get("feature_count", 0)
    manifest["latest_agent60_patent_technical_feature_coverage_rate"] = patent_coverage.get(
        "technical_feature_coverage_rate",
        0,
    )
    manifest["latest_agent60_patent_field_claim_upgrade_allowed"] = patent_coverage.get(
        "field_claim_upgrade_allowed",
        False,
    )
    manifest["latest_agent60_technical_claim_skeleton_scaffold"] = str(
        TECHNICAL_CLAIM_SKELETON_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_agent60_technical_claim_skeleton_status"] = claim_coverage.get(
        "technical_claim_skeleton_status",
        "",
    )
    manifest["latest_agent60_technical_claim_skeleton_count"] = claim_coverage.get(
        "claim_scaffold_count",
        0,
    )
    manifest["latest_agent60_technical_claim_skeleton_coverage_rate"] = claim_coverage.get(
        "technical_claim_skeleton_coverage_rate",
        0,
    )
    manifest["latest_agent60_technical_claim_field_upgrade_allowed"] = claim_coverage.get(
        "field_claim_upgrade_allowed",
        False,
    )
    manifest["latest_agent60_technical_embodiment_validation_matrix"] = str(
        TECHNICAL_EMBODIMENT_VALIDATION_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_agent60_technical_embodiment_validation_status"] = embodiment_coverage.get(
        "technical_embodiment_validation_status",
        "",
    )
    manifest["latest_agent60_technical_embodiment_count"] = embodiment_coverage.get(
        "embodiment_count",
        0,
    )
    manifest["latest_agent60_technical_embodiment_validation_coverage_rate"] = embodiment_coverage.get(
        "technical_embodiment_validation_coverage_rate",
        0,
    )
    manifest["latest_agent60_technical_embodiment_field_claim_upgrade_allowed"] = embodiment_coverage.get(
        "field_claim_upgrade_allowed",
        False,
    )
    manifest["latest_agent60_technical_embodiment_can_generate_field_evidence"] = embodiment_coverage.get(
        "can_generate_field_evidence",
        False,
    )
    manifest["latest_agent60_technical_effect_measurement_matrix"] = str(
        TECHNICAL_EFFECT_MEASUREMENT_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_agent60_technical_effect_measurement_status"] = effect_coverage.get(
        "technical_effect_measurement_status",
        "",
    )
    manifest["latest_agent60_technical_effect_measurement_count"] = effect_coverage.get(
        "effect_count",
        0,
    )
    manifest["latest_agent60_technical_effect_measurement_coverage_rate"] = effect_coverage.get(
        "technical_effect_measurement_coverage_rate",
        0,
    )
    manifest["latest_agent60_technical_effect_field_claim_upgrade_allowed"] = effect_coverage.get(
        "field_claim_upgrade_allowed",
        False,
    )
    manifest["latest_agent60_technical_effect_can_write_to_actuator"] = effect_coverage.get(
        "can_write_to_actuator",
        False,
    )
    manifest["latest_agent60_technical_effect_can_write_to_release_gate"] = effect_coverage.get(
        "can_write_to_release_gate",
        False,
    )
    manifest["latest_agent60_prior_art_distinction_matrix"] = str(
        PRIOR_ART_DISTINCTION_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_agent60_prior_art_distinction_status"] = prior_art_coverage.get(
        "prior_art_distinction_status",
        "",
    )
    manifest["latest_agent60_prior_art_distinction_count"] = prior_art_coverage.get(
        "distinction_count",
        0,
    )
    manifest["latest_agent60_prior_art_distinction_coverage_rate"] = prior_art_coverage.get(
        "prior_art_distinction_coverage_rate",
        0,
    )
    manifest["latest_agent60_prior_art_formal_search_required"] = prior_art_coverage.get(
        "formal_search_required",
        True,
    )
    manifest["latest_agent60_prior_art_novelty_or_inventiveness_opinion_allowed"] = prior_art_coverage.get(
        "novelty_or_inventiveness_opinion_allowed",
        False,
    )
    manifest["latest_agent60_prior_art_field_claim_upgrade_allowed"] = prior_art_coverage.get(
        "field_claim_upgrade_allowed",
        False,
    )
    manifest["latest_agent60_formal_search_work_packages"] = str(
        FORMAL_SEARCH_WORK_PACKAGES_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_agent60_formal_search_work_package_status"] = formal_search_coverage.get(
        "formal_search_work_package_status",
        "",
    )
    manifest["latest_agent60_formal_search_work_package_count"] = formal_search_coverage.get(
        "work_package_count",
        0,
    )
    manifest["latest_agent60_formal_search_work_package_coverage_rate"] = formal_search_coverage.get(
        "formal_search_work_package_coverage_rate",
        0,
    )
    manifest["latest_agent60_formal_search_completed"] = formal_search_coverage.get(
        "formal_search_completed",
        False,
    )
    manifest["latest_agent60_formal_search_legal_opinion_allowed"] = formal_search_coverage.get(
        "legal_opinion_allowed",
        False,
    )
    manifest["latest_agent60_formal_search_field_claim_upgrade_allowed"] = formal_search_coverage.get(
        "field_claim_upgrade_allowed",
        False,
    )
    manifest["latest_agent60_formal_search_result_intake_schema"] = str(
        FORMAL_SEARCH_RESULT_INTAKE_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_agent60_formal_search_result_intake_status"] = intake_coverage.get(
        "formal_search_result_intake_status",
        "",
    )
    manifest["latest_agent60_formal_search_result_intake_count"] = intake_coverage.get(
        "intake_count",
        0,
    )
    manifest["latest_agent60_formal_search_result_intake_coverage_rate"] = intake_coverage.get(
        "formal_search_result_intake_coverage_rate",
        0,
    )
    manifest["latest_agent60_formal_search_result_supplied"] = intake_coverage.get(
        "formal_search_result_supplied",
        False,
    )
    manifest["latest_agent60_formal_search_result_accepted_hit_count"] = intake_coverage.get(
        "accepted_hit_count",
        0,
    )
    manifest["latest_agent60_formal_search_result_can_generate_prior_art_result"] = intake_coverage.get(
        "can_generate_prior_art_result",
        False,
    )
    manifest["latest_agent60_formal_search_result_validation_gate"] = str(
        FORMAL_SEARCH_RESULT_VALIDATION_GATE_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_agent60_formal_search_result_validation_gate_status"] = validation_coverage.get(
        "formal_search_result_validation_gate_status",
        "",
    )
    manifest["latest_agent60_formal_search_result_validation_gate_count"] = validation_coverage.get(
        "validation_gate_count",
        0,
    )
    manifest["latest_agent60_formal_search_result_validation_gate_coverage_rate"] = validation_coverage.get(
        "formal_search_result_validation_gate_coverage_rate",
        0,
    )
    manifest["latest_agent60_formal_search_result_package_supplied"] = validation_coverage.get(
        "formal_search_result_package_supplied",
        False,
    )
    manifest["latest_agent60_formal_search_result_validated_hit_count"] = validation_coverage.get(
        "validated_hit_count",
        0,
    )
    manifest["latest_agent60_formal_search_result_rejected_hit_count"] = validation_coverage.get(
        "rejected_hit_count",
        0,
    )
    manifest["latest_agent60_formal_search_validation_can_generate_prior_art_result"] = validation_coverage.get(
        "can_generate_prior_art_result",
        False,
    )
    manifest["latest_agent60_formal_search_result_package_template"] = str(
        FORMAL_SEARCH_RESULT_PACKAGE_TEMPLATE_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_agent60_formal_search_result_package_template_status"] = package_template_coverage.get(
        "formal_search_result_package_template_status",
        "",
    )
    manifest["latest_agent60_formal_search_result_package_template_count"] = package_template_coverage.get(
        "package_template_count",
        0,
    )
    manifest["latest_agent60_formal_search_result_package_template_coverage_rate"] = package_template_coverage.get(
        "formal_search_result_package_template_coverage_rate",
        0,
    )
    submission_template = report.metrics["formal_search_result_package_submission_template"]
    manifest["latest_agent60_formal_search_result_package_submission_template"] = str(
        FORMAL_SEARCH_RESULT_PACKAGE_SUBMISSION_TEMPLATE_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_agent60_formal_search_result_package_submission_template_status"] = submission_template.get(
        "submission_template_status",
        "",
    )
    manifest["latest_agent60_formal_search_result_package_submission_template_ready_status"] = (
        submission_template.get("submission_template_ready_status", "")
    )
    manifest["latest_agent60_formal_search_result_package_submission_template_expected_work_package_count"] = len(
        submission_template.get("expected_work_package_ids", [])
    )
    manifest["latest_agent60_formal_search_result_package_submission_template_can_route_to_validation_gate"] = (
        submission_template.get("can_route_to_validation_gate", False)
    )
    manifest["latest_agent60_formal_search_result_package_source_preflight"] = str(
        FORMAL_SEARCH_RESULT_PACKAGE_PREFLIGHT_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_agent60_formal_search_result_package_source_status"] = package_preflight.get(
        "formal_search_result_package_source_status",
        "",
    )
    manifest["latest_agent60_formal_search_result_package_expected_env_var"] = package_preflight.get(
        "expected_env_var",
        "FORMAL_SEARCH_RESULT_PACKAGE_PATH",
    )
    manifest["latest_agent60_formal_search_result_package_can_route_to_validation_gate"] = package_preflight.get(
        "can_route_to_validation_gate",
        False,
    )
    manifest["latest_agent60_formal_search_result_package_preflight_blocker_count"] = len(
        package_preflight.get("preflight_blockers", [])
    )
    row_preflight = report.metrics["formal_search_result_package_row_preflight"]
    manifest["latest_agent60_formal_search_result_package_row_preflight"] = str(
        FORMAL_SEARCH_RESULT_PACKAGE_ROW_PREFLIGHT_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_agent60_formal_search_result_package_row_preflight_status"] = row_preflight.get(
        "formal_search_result_package_row_preflight_status",
        "",
    )
    manifest["latest_agent60_formal_search_result_package_row_gap_count"] = row_preflight.get(
        "row_gap_count",
        0,
    )
    manifest["latest_agent60_formal_search_result_package_comparison_coverage_gap_count"] = row_preflight.get(
        "comparison_coverage_gap_count",
        0,
    )
    manifest["latest_agent60_formal_search_result_package_forbidden_review_boundary_count"] = row_preflight.get(
        "forbidden_review_boundary_count",
        0,
    )
    manifest["latest_agent60_formal_search_result_package_row_can_route_to_validation_gate"] = row_preflight.get(
        "can_route_to_validation_gate",
        False,
    )
    validation_execution = report.metrics["formal_search_result_validation_execution"]
    manifest["latest_agent60_formal_search_result_validation_execution"] = str(
        FORMAL_SEARCH_RESULT_VALIDATION_EXECUTION_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_agent60_formal_search_result_validation_execution_status"] = validation_execution.get(
        "formal_search_result_validation_execution_status",
        "",
    )
    manifest["latest_agent60_formal_search_result_validation_execution_package_supplied"] = validation_execution.get(
        "formal_search_result_package_supplied",
        False,
    )
    manifest["latest_agent60_formal_search_result_validation_execution_validated_hit_count"] = validation_execution.get(
        "validated_hit_count",
        0,
    )
    manifest["latest_agent60_formal_search_result_validation_execution_rejected_hit_count"] = validation_execution.get(
        "rejected_hit_count",
        0,
    )
    manifest["latest_agent60_formal_search_result_validation_execution_can_enter_human_nonlegal_review"] = validation_execution.get(
        "can_enter_human_nonlegal_comparison_review",
        False,
    )
    manifest["latest_agent60_formal_search_result_validation_execution_can_generate_prior_art_result"] = validation_execution.get(
        "can_generate_prior_art_result",
        False,
    )
    manifest["latest_agent60_formal_search_result_validation_execution_legal_opinion_allowed"] = validation_execution.get(
        "legal_opinion_allowed",
        False,
    )
    manifest["latest_agent60_formal_search_result_validation_execution_field_claim_upgrade_allowed"] = validation_execution.get(
        "field_claim_upgrade_allowed",
        False,
    )
    nonlegal_review_packet = report.metrics["formal_search_nonlegal_comparison_review_packet"]
    manifest["latest_agent60_formal_search_nonlegal_comparison_review_packet"] = str(
        FORMAL_SEARCH_NONLEGAL_COMPARISON_REVIEW_PACKET_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_agent60_formal_search_nonlegal_comparison_review_packet_status"] = nonlegal_review_packet.get(
        "formal_search_nonlegal_comparison_review_packet_status",
        "",
    )
    manifest["latest_agent60_formal_search_nonlegal_comparison_review_packet_row_count"] = nonlegal_review_packet.get(
        "review_packet_row_count",
        0,
    )
    manifest["latest_agent60_formal_search_nonlegal_comparison_review_packet_human_review_completed"] = nonlegal_review_packet.get(
        "human_review_completed",
        False,
    )
    manifest["latest_agent60_formal_search_nonlegal_comparison_review_packet_can_enter_review"] = nonlegal_review_packet.get(
        "can_enter_human_nonlegal_comparison_review",
        False,
    )
    manifest["latest_agent60_formal_search_nonlegal_comparison_review_packet_can_generate_prior_art_result"] = nonlegal_review_packet.get(
        "can_generate_prior_art_result",
        False,
    )
    manifest["latest_agent60_formal_search_nonlegal_comparison_review_packet_legal_opinion_allowed"] = nonlegal_review_packet.get(
        "legal_opinion_allowed",
        False,
    )
    manifest["latest_agent60_formal_search_nonlegal_comparison_review_packet_field_claim_upgrade_allowed"] = nonlegal_review_packet.get(
        "field_claim_upgrade_allowed",
        False,
    )
    nonlegal_response_template = report.metrics["formal_search_nonlegal_review_response_template"]
    manifest["latest_agent60_formal_search_nonlegal_review_response_template"] = str(
        FORMAL_SEARCH_NONLEGAL_REVIEW_RESPONSE_TEMPLATE_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_agent60_formal_search_nonlegal_review_response_template_status"] = nonlegal_response_template.get(
        "formal_search_nonlegal_review_response_template_status",
        "",
    )
    manifest["latest_agent60_formal_search_nonlegal_review_response_template_expected_row_count"] = len(
        nonlegal_response_template.get("expected_review_packet_row_ids", [])
    )
    manifest["latest_agent60_formal_search_nonlegal_review_response_template_expected_env_var"] = nonlegal_response_template.get(
        "expected_env_var",
        "FORMAL_SEARCH_NONLEGAL_REVIEW_RESPONSE_PATH",
    )
    nonlegal_response_preflight = report.metrics[
        "formal_search_nonlegal_review_response_source_preflight"
    ]
    manifest["latest_agent60_formal_search_nonlegal_review_response_source_preflight"] = str(
        FORMAL_SEARCH_NONLEGAL_REVIEW_RESPONSE_PREFLIGHT_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_agent60_formal_search_nonlegal_review_response_source_status"] = nonlegal_response_preflight.get(
        "formal_search_nonlegal_review_response_source_status",
        "",
    )
    manifest["latest_agent60_formal_search_nonlegal_review_response_accepted_row_count"] = nonlegal_response_preflight.get(
        "accepted_review_row_count",
        0,
    )
    manifest["latest_agent60_formal_search_nonlegal_review_response_rejected_row_count"] = nonlegal_response_preflight.get(
        "rejected_review_row_count",
        0,
    )
    manifest["latest_agent60_formal_search_nonlegal_review_response_ai_draft_boundary_gap_count"] = nonlegal_response_preflight.get(
        "ai_draft_boundary_gap_count",
        0,
    )
    manifest["latest_agent60_formal_search_nonlegal_review_response_ai_draft_boundary_gaps"] = nonlegal_response_preflight.get(
        "ai_draft_boundary_gaps",
        [],
    )
    manifest["latest_agent60_formal_search_nonlegal_review_response_human_review_completed"] = nonlegal_response_preflight.get(
        "human_review_completed",
        False,
    )
    manifest["latest_agent60_formal_search_nonlegal_review_response_can_route_to_claim_scope_patch_draft"] = nonlegal_response_preflight.get(
        "can_route_to_claim_scope_patch_draft",
        False,
    )
    manifest["latest_agent60_formal_search_nonlegal_review_response_can_generate_prior_art_result"] = nonlegal_response_preflight.get(
        "can_generate_prior_art_result",
        False,
    )
    manifest["latest_agent60_formal_search_nonlegal_review_response_legal_opinion_allowed"] = nonlegal_response_preflight.get(
        "legal_opinion_allowed",
        False,
    )
    manifest["latest_agent60_formal_search_nonlegal_review_response_field_claim_upgrade_allowed"] = nonlegal_response_preflight.get(
        "field_claim_upgrade_allowed",
        False,
    )
    claim_scope_patch_draft = report.metrics["formal_search_claim_scope_patch_draft"]
    manifest["latest_agent60_formal_search_claim_scope_patch_draft"] = str(
        FORMAL_SEARCH_CLAIM_SCOPE_PATCH_DRAFT_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_agent60_formal_search_claim_scope_patch_draft_status"] = claim_scope_patch_draft.get(
        "formal_search_claim_scope_patch_draft_status",
        "",
    )
    manifest["latest_agent60_formal_search_claim_scope_patch_draft_patch_count"] = claim_scope_patch_draft.get(
        "draft_patch_count",
        0,
    )
    manifest["latest_agent60_formal_search_claim_scope_patch_draft_can_route_to_formal_counsel_review"] = claim_scope_patch_draft.get(
        "can_route_to_formal_counsel_review",
        False,
    )
    manifest["latest_agent60_formal_search_claim_scope_patch_draft_can_emit_claim_text"] = claim_scope_patch_draft.get(
        "can_emit_claim_text",
        False,
    )
    manifest["latest_agent60_formal_search_claim_scope_patch_draft_can_generate_prior_art_result"] = claim_scope_patch_draft.get(
        "can_generate_prior_art_result",
        False,
    )
    manifest["latest_agent60_formal_search_claim_scope_patch_draft_legal_opinion_allowed"] = claim_scope_patch_draft.get(
        "legal_opinion_allowed",
        False,
    )
    manifest["latest_agent60_formal_search_claim_scope_patch_draft_field_claim_upgrade_allowed"] = claim_scope_patch_draft.get(
        "field_claim_upgrade_allowed",
        False,
    )
    formal_counsel_template = report.metrics["formal_counsel_review_response_template"]
    manifest["latest_agent60_formal_counsel_review_response_template"] = str(
        FORMAL_COUNSEL_REVIEW_RESPONSE_TEMPLATE_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_agent60_formal_counsel_review_response_template_status"] = formal_counsel_template.get(
        "formal_counsel_review_response_template_status",
        "",
    )
    manifest["latest_agent60_formal_counsel_review_response_template_expected_row_count"] = len(
        formal_counsel_template.get("expected_claim_scope_patch_ids", [])
    )
    manifest["latest_agent60_formal_counsel_review_response_template_expected_env_var"] = formal_counsel_template.get(
        "expected_env_var",
        "FORMAL_COUNSEL_REVIEW_RESPONSE_PATH",
    )
    formal_counsel_preflight = report.metrics["formal_counsel_review_response_source_preflight"]
    manifest["latest_agent60_formal_counsel_review_response_source_preflight"] = str(
        FORMAL_COUNSEL_REVIEW_RESPONSE_PREFLIGHT_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_agent60_formal_counsel_review_response_source_status"] = formal_counsel_preflight.get(
        "formal_counsel_review_response_source_status",
        "",
    )
    manifest["latest_agent60_formal_counsel_review_response_accepted_row_count"] = formal_counsel_preflight.get(
        "accepted_formal_review_row_count",
        0,
    )
    manifest["latest_agent60_formal_counsel_review_response_rejected_row_count"] = formal_counsel_preflight.get(
        "rejected_formal_review_row_count",
        0,
    )
    manifest["latest_agent60_formal_counsel_review_response_external_review_completed"] = formal_counsel_preflight.get(
        "external_formal_review_completed",
        False,
    )
    manifest["latest_agent60_formal_counsel_review_response_can_route_to_disclosure_revision_queue"] = formal_counsel_preflight.get(
        "can_route_to_disclosure_revision_queue",
        False,
    )
    manifest["latest_agent60_formal_counsel_review_response_can_emit_claim_text"] = formal_counsel_preflight.get(
        "can_emit_claim_text",
        False,
    )
    manifest["latest_agent60_formal_counsel_review_response_can_generate_prior_art_result"] = formal_counsel_preflight.get(
        "can_generate_prior_art_result",
        False,
    )
    manifest["latest_agent60_formal_counsel_review_response_legal_opinion_allowed"] = formal_counsel_preflight.get(
        "legal_opinion_allowed",
        False,
    )
    manifest["latest_agent60_formal_counsel_review_response_field_claim_upgrade_allowed"] = formal_counsel_preflight.get(
        "field_claim_upgrade_allowed",
        False,
    )
    disclosure_revision_queue = report.metrics["formal_disclosure_revision_queue"]
    manifest["latest_agent60_formal_disclosure_revision_queue"] = str(
        FORMAL_DISCLOSURE_REVISION_QUEUE_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_agent60_formal_disclosure_revision_queue_status"] = disclosure_revision_queue.get(
        "formal_disclosure_revision_queue_status",
        "",
    )
    manifest["latest_agent60_formal_disclosure_revision_queue_item_count"] = disclosure_revision_queue.get(
        "revision_item_count",
        0,
    )
    manifest["latest_agent60_formal_disclosure_revision_queue_can_route_to_disclosure_editor"] = disclosure_revision_queue.get(
        "can_route_to_disclosure_editor",
        False,
    )
    manifest["latest_agent60_formal_disclosure_revision_queue_can_apply_disclosure_revision_automatically"] = disclosure_revision_queue.get(
        "can_apply_disclosure_revision_automatically",
        False,
    )
    manifest["latest_agent60_formal_disclosure_revision_queue_can_emit_claim_text"] = disclosure_revision_queue.get(
        "can_emit_claim_text",
        False,
    )
    manifest["latest_agent60_formal_disclosure_revision_queue_can_generate_prior_art_result"] = disclosure_revision_queue.get(
        "can_generate_prior_art_result",
        False,
    )
    manifest["latest_agent60_formal_disclosure_revision_queue_legal_opinion_allowed"] = disclosure_revision_queue.get(
        "legal_opinion_allowed",
        False,
    )
    manifest["latest_agent60_formal_disclosure_revision_queue_field_claim_upgrade_allowed"] = disclosure_revision_queue.get(
        "field_claim_upgrade_allowed",
        False,
    )
    disclosure_revision_impact_plan = report.metrics["formal_disclosure_revision_impact_plan"]
    manifest["latest_agent60_formal_disclosure_revision_impact_plan"] = str(
        FORMAL_DISCLOSURE_REVISION_IMPACT_PLAN_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_agent60_formal_disclosure_revision_impact_plan_status"] = disclosure_revision_impact_plan.get(
        "formal_disclosure_revision_impact_plan_status",
        "",
    )
    manifest["latest_agent60_formal_disclosure_revision_impact_plan_item_count"] = disclosure_revision_impact_plan.get(
        "revision_impact_item_count",
        0,
    )
    manifest["latest_agent60_formal_disclosure_revision_impact_plan_can_route_to_human_artifact_revision"] = disclosure_revision_impact_plan.get(
        "can_route_to_human_artifact_revision",
        False,
    )
    manifest["latest_agent60_formal_disclosure_revision_impact_plan_can_apply_artifact_patch_automatically"] = disclosure_revision_impact_plan.get(
        "can_apply_artifact_patch_automatically",
        False,
    )
    manifest["latest_agent60_formal_disclosure_revision_impact_plan_can_emit_claim_text"] = disclosure_revision_impact_plan.get(
        "can_emit_claim_text",
        False,
    )
    manifest["latest_agent60_formal_disclosure_revision_impact_plan_can_generate_prior_art_result"] = disclosure_revision_impact_plan.get(
        "can_generate_prior_art_result",
        False,
    )
    manifest["latest_agent60_formal_disclosure_revision_impact_plan_legal_opinion_allowed"] = disclosure_revision_impact_plan.get(
        "legal_opinion_allowed",
        False,
    )
    manifest["latest_agent60_formal_disclosure_revision_impact_plan_field_claim_upgrade_allowed"] = disclosure_revision_impact_plan.get(
        "field_claim_upgrade_allowed",
        False,
    )
    formal_search_review_readiness = report.metrics["formal_search_review_readiness"]
    manifest["latest_agent60_formal_search_review_readiness"] = str(
        FORMAL_SEARCH_REVIEW_READINESS_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_agent60_formal_search_review_readiness_status"] = formal_search_review_readiness.get(
        "formal_search_review_readiness_status",
        "",
    )
    manifest["latest_agent60_formal_search_review_highest_priority_blocker"] = formal_search_review_readiness.get(
        "highest_priority_blocker",
        "",
    )
    manifest["latest_agent60_formal_search_review_next_operator_action"] = formal_search_review_readiness.get(
        "next_operator_action",
        "",
    )
    manifest["latest_agent60_formal_search_review_blocking_stage_count"] = formal_search_review_readiness.get(
        "blocking_stage_count",
        0,
    )
    manifest["latest_agent60_formal_search_review_boundary_violation_count"] = formal_search_review_readiness.get(
        "boundary_violation_count",
        0,
    )
    manifest["latest_agent60_formal_search_review_can_generate_prior_art_result"] = formal_search_review_readiness.get(
        "can_generate_prior_art_result",
        False,
    )
    manifest["latest_agent60_formal_search_review_legal_opinion_allowed"] = formal_search_review_readiness.get(
        "legal_opinion_allowed",
        False,
    )
    manifest["latest_agent60_formal_search_review_can_emit_claim_text"] = formal_search_review_readiness.get(
        "can_emit_claim_text",
        False,
    )
    manifest["latest_agent60_formal_search_review_field_claim_upgrade_allowed"] = formal_search_review_readiness.get(
        "field_claim_upgrade_allowed",
        False,
    )
    formal_search_execution_route_plan = report.metrics["formal_search_execution_route_plan"]
    manifest["latest_agent60_formal_search_execution_route_plan"] = str(
        FORMAL_SEARCH_EXECUTION_ROUTE_PLAN_PATH.relative_to(PROJECT_ROOT)
    )
    manifest["latest_agent60_formal_search_execution_route_plan_status"] = formal_search_execution_route_plan.get(
        "route_plan_status",
        "",
    )
    manifest["latest_agent60_formal_search_execution_route_row_count"] = formal_search_execution_route_plan.get(
        "route_row_count",
        0,
    )
    manifest["latest_agent60_formal_search_execution_complete_route_row_count"] = formal_search_execution_route_plan.get(
        "complete_route_row_count",
        0,
    )
    manifest["latest_agent60_formal_search_execution_mapped_seed_route_count"] = formal_search_execution_route_plan.get(
        "mapped_seed_route_count",
        0,
    )
    manifest["latest_agent60_formal_search_execution_operator_first_action"] = formal_search_execution_route_plan.get(
        "operator_first_action",
        "",
    )
    manifest["latest_agent60_formal_search_execution_can_generate_prior_art_result"] = formal_search_execution_route_plan.get(
        "can_generate_prior_art_result",
        False,
    )
    manifest["latest_agent60_formal_search_execution_legal_opinion_allowed"] = formal_search_execution_route_plan.get(
        "legal_opinion_allowed",
        False,
    )
    manifest["latest_agent60_formal_search_execution_can_emit_claim_text"] = formal_search_execution_route_plan.get(
        "can_emit_claim_text",
        False,
    )
    manifest["latest_agent60_formal_search_execution_field_claim_upgrade_allowed"] = formal_search_execution_route_plan.get(
        "field_claim_upgrade_allowed",
        False,
    )
    if str(top["action_id"]).startswith("R4b"):
        next_stage_rationale = (
            "该步骤把 R4 已生成的灰箱边界和现场字段 patch 接入 Agent53/58/59，"
            "让控制失败案例真正回到机制解释和 field package，而不是停在 replay 报告里。"
        )
    elif str(top["action_id"]).startswith("R5_extend_guardrail_field"):
        next_stage_rationale = (
            "R4b 已完成 patch consumption，当前真正阻塞 field replay 的是部分 guardrail 必采字段仍未进入 "
            "Agent30/42 的现场数据接口与 timestamped replay schema。"
        )
    elif str(top["action_id"]).startswith("R6_complete_guardrail_source_basis"):
        next_stage_rationale = (
            "R4b/R5 已完成 patch consumption 和 schema 覆盖，当前阻塞 claim 升级的是 R4 guardrail source_basis "
            "细节与真实 field package 导入验收。"
        )
    elif str(top["action_id"]).startswith("R7_real_field_package"):
        next_stage_rationale = (
            "R4b/R5/R6 已完成 patch consumption、schema 覆盖与 source_basis detail，当前唯一能继续升级证据等级的是"
            "真实 field package、timestamped replay 和 holdout gate。"
        )
    elif str(top["action_id"]).startswith("R7"):
        r7_pipeline = _read_optional_json(R7_REAL_FIELD_REPLAY_PIPELINE_METRICS_PATH)
        pipeline_readiness = r7_pipeline.get("pipeline_readiness", {}) if isinstance(r7_pipeline, dict) else {}
        coverage = r7_pipeline.get("field_package_coverage", {}) if isinstance(r7_pipeline, dict) else {}
        patch_plan = coverage.get("patch_plan", {}) if isinstance(coverage, dict) else {}
        manifest["status"] = (
            "Agent60 复盘治理已接入 R7 coverage/minimum replay contract，"
            f"下一步指向 {top['action_id']}"
        )
        manifest["latest_r7_pipeline_minimum_replay_contract_status"] = pipeline_readiness.get(
            "minimum_replay_contract_status",
            "unknown",
        )
        manifest["latest_r7_pipeline_minimum_common_batch_count"] = pipeline_readiness.get(
            "minimum_common_batch_count",
            0,
        )
        manifest["latest_r7_pipeline_minimum_valid_matched_batch_count"] = pipeline_readiness.get(
            "minimum_valid_matched_batch_count",
            0,
        )
        manifest["latest_r7_pipeline_minimum_valid_operation_action_count"] = pipeline_readiness.get(
            "minimum_valid_operation_action_count",
            0,
        )
        manifest["latest_r7_pipeline_minimum_invalid_operation_action_count"] = pipeline_readiness.get(
            "minimum_invalid_operation_action_count",
            0,
        )
        manifest["latest_r7_pipeline_minimum_valid_lab_result_count"] = pipeline_readiness.get(
            "minimum_valid_lab_result_count",
            0,
        )
        manifest["latest_r7_pipeline_minimum_invalid_lab_result_count"] = pipeline_readiness.get(
            "minimum_invalid_lab_result_count",
            0,
        )
        manifest["latest_r7_pipeline_minimum_valid_proxy_label_count"] = pipeline_readiness.get(
            "minimum_valid_proxy_label_count",
            0,
        )
        manifest["latest_r7_pipeline_minimum_invalid_proxy_label_count"] = pipeline_readiness.get(
            "minimum_invalid_proxy_label_count",
            0,
        )
        manifest["latest_r7_pipeline_minimum_time_order_violation_count"] = pipeline_readiness.get(
            "minimum_time_order_violation_count",
            0,
        )
        next_stage_rationale = (
            "R7 acceptance gate 已把真实现场验收拆成导入、timestamped replay、G6/P6、证据链、"
            "多设施控制晋级/催化剂 holdout、soft holdout、claim package 和统一 evidence gate 八个阶段；"
            "Agent60 同时读取 R7 pipeline coverage，当前 "
            f"coverage_status={pipeline_readiness.get('field_package_coverage_status', 'unknown')}，"
            f"minimum_replay_contract_status={pipeline_readiness.get('minimum_replay_contract_status', 'unknown')}，"
            f"minimum_common_batch_count={pipeline_readiness.get('minimum_common_batch_count', 0)}，"
            f"minimum_valid_matched_batch_count={pipeline_readiness.get('minimum_valid_matched_batch_count', 0)}，"
            f"minimum_valid_operation_action_count={pipeline_readiness.get('minimum_valid_operation_action_count', 0)}，"
            f"minimum_invalid_operation_action_count={pipeline_readiness.get('minimum_invalid_operation_action_count', 0)}，"
            f"minimum_valid_lab_result_count={pipeline_readiness.get('minimum_valid_lab_result_count', 0)}，"
            f"minimum_invalid_lab_result_count={pipeline_readiness.get('minimum_invalid_lab_result_count', 0)}，"
            f"minimum_valid_proxy_label_count={pipeline_readiness.get('minimum_valid_proxy_label_count', 0)}，"
            f"minimum_invalid_proxy_label_count={pipeline_readiness.get('minimum_invalid_proxy_label_count', 0)}，"
            f"minimum_time_order_violation_count={pipeline_readiness.get('minimum_time_order_violation_count', 0)}，"
            f"patch_plan_status={patch_plan.get('patch_plan_status', 'unknown')}，"
            f"patch_plan_item_count={patch_plan.get('item_count', 0)}。"
        )
    elif str(top["action_id"]).startswith("R4_backpropagate"):
        next_stage_rationale = (
            "该步骤把 R3c resolved cases 反写成灰箱机制边界和现场 replay 必采字段，"
            "让控制 guardrail 回到黑箱变灰箱的第一性原理。"
        )
    elif str(top["action_id"]).startswith("R3b"):
        next_stage_rationale = (
            "该步骤把 R3 反事实压力测试中的规则补丁接入 Agent49 reward prior，"
            "让控制层真正吸收误保护和高 regret 案例，但仍不写执行器。"
        )
    elif str(top["action_id"]).startswith("R3"):
        next_stage_rationale = (
            "该步骤直接服务闭环控制可信度：用离线 replay、reward regret 和保护性误触发压力测试，"
            "检验多设施协同动作是否真的可执行、可回退、可解释。"
        )
    elif str(top["action_id"]).startswith("R2"):
        next_stage_rationale = (
            "该步骤直接服务黑箱转灰箱的观测基础：把稀疏布点、催化剂代理观测和软传感输入合同统一起来。"
        )
    else:
        next_stage_rationale = "该步骤继续服务模型核心链路的证据、观测、推理、控制或验证能力。"
    manifest["latest_architecture_consolidation_status"] = report.metrics["architecture_status"]
    manifest["latest_global_system_spine_status"] = report.metrics["system_spine_coverage"]["system_spine_status"]
    manifest["latest_global_system_layer_coverage_rate"] = report.metrics["system_spine_coverage"][
        "layer_coverage_rate"
    ]
    manifest["latest_global_system_ability_coverage_rate"] = report.metrics["system_spine_coverage"][
        "ability_coverage_rate"
    ]
    manifest["latest_module_interface_contract_status"] = report.metrics["interface_contract_coverage"][
        "interface_contract_status"
    ]
    manifest["latest_module_interface_contract_coverage_rate"] = report.metrics["interface_contract_coverage"][
        "interface_contract_coverage_rate"
    ]
    manifest["latest_offline_core_fallback_action"] = fallback.get("action_id", "none")
    manifest["latest_offline_core_fallback_enabled"] = bool(fallback.get("fallback_enabled", False))
    manifest["latest_offline_core_fallback_operator_handoff_status"] = fallback.get(
        "operator_handoff_status",
        "",
    )
    manifest["latest_offline_core_fallback_schema_status"] = fallback.get(
        "field_rows_package_schema_status",
        "",
    )
    manifest["latest_offline_core_fallback_schema_validation_status"] = fallback.get(
        "field_rows_schema_validation_status",
        "",
    )
    fallback_schema_summary = fallback.get("schema_validation_summary", {})
    if not isinstance(fallback_schema_summary, dict):
        fallback_schema_summary = {}
    manifest["latest_offline_core_fallback_schema_template_marker_gap_count"] = fallback_schema_summary.get(
        "template_marker_gap_count",
        0,
    )
    manifest["latest_offline_core_fallback_schema_field_origin_gap_count"] = fallback_schema_summary.get(
        "field_origin_gap_count",
        0,
    )
    manifest["latest_offline_core_fallback_collection_checklist_status"] = fallback.get(
        "field_rows_collection_checklist_status",
        "",
    )
    manifest["latest_offline_core_fallback_batch_bundle_preflight_status"] = fallback.get(
        "field_rows_batch_bundle_preflight_status",
        "",
    )
    fallback_batch_bundle_summary = fallback.get("batch_bundle_preflight_summary", {})
    if not isinstance(fallback_batch_bundle_summary, dict):
        fallback_batch_bundle_summary = {}
    manifest["latest_offline_core_fallback_complete_batch_bundle_count"] = fallback_batch_bundle_summary.get(
        "complete_bundle_count",
        0,
    )
    manifest["latest_offline_core_fallback_partial_batch_bundle_count"] = fallback_batch_bundle_summary.get(
        "partial_bundle_count",
        0,
    )
    manifest["latest_offline_core_fallback_missing_bundle_table_count"] = fallback_batch_bundle_summary.get(
        "missing_bundle_table_count",
        0,
    )
    manifest["latest_offline_core_fallback_temporal_window_preflight_status"] = fallback.get(
        "field_rows_temporal_window_preflight_status",
        "",
    )
    fallback_temporal_window_summary = fallback.get("temporal_window_preflight_summary", {})
    if not isinstance(fallback_temporal_window_summary, dict):
        fallback_temporal_window_summary = {}
    manifest["latest_offline_core_fallback_temporal_valid_batch_count"] = fallback_temporal_window_summary.get(
        "temporal_valid_batch_count",
        0,
    )
    manifest["latest_offline_core_fallback_temporal_violation_count"] = fallback_temporal_window_summary.get(
        "temporal_violation_count",
        0,
    )
    manifest["latest_offline_core_fallback_hold_time_violation_count"] = fallback_temporal_window_summary.get(
        "hold_time_violation_count",
        0,
    )
    manifest["latest_offline_core_fallback_scenario_semantic_preflight_status"] = fallback.get(
        "field_rows_scenario_semantic_preflight_status",
        "",
    )
    fallback_scenario_semantic_summary = fallback.get("scenario_semantic_preflight_summary", {})
    if not isinstance(fallback_scenario_semantic_summary, dict):
        fallback_scenario_semantic_summary = {}
    manifest["latest_offline_core_fallback_semantic_valid_batch_count"] = fallback_scenario_semantic_summary.get(
        "semantic_valid_batch_count",
        0,
    )
    manifest["latest_offline_core_fallback_semantic_violation_count"] = fallback_scenario_semantic_summary.get(
        "semantic_violation_count",
        0,
    )
    manifest["latest_offline_core_fallback_downstream_routing_preflight_status"] = fallback.get(
        "field_rows_downstream_routing_preflight_status",
        "",
    )
    fallback_downstream_routing_summary = fallback.get("downstream_routing_preflight_summary", {})
    if not isinstance(fallback_downstream_routing_summary, dict):
        fallback_downstream_routing_summary = {}
    manifest["latest_offline_core_fallback_routing_ready_target_count"] = fallback_downstream_routing_summary.get(
        "routing_ready_target_count",
        0,
    )
    manifest["latest_offline_core_fallback_downstream_routing_target_count"] = (
        fallback_downstream_routing_summary.get("routing_target_count", 0)
    )
    manifest["latest_offline_core_fallback_provenance_gate_status"] = fallback.get(
        "field_rows_provenance_gate_status",
        "",
    )
    manifest["latest_offline_core_fallback_all_tables_require_data_origin"] = fallback.get(
        "field_rows_all_tables_require_data_origin",
        False,
    )
    manifest["latest_offline_core_fallback_provenance_required_table_count"] = fallback.get(
        "field_rows_provenance_required_table_count",
        0,
    )
    manifest["latest_offline_core_fallback_r7_completion_plan_status"] = fallback.get(
        "r7_completion_plan_status",
        "",
    )
    manifest["latest_offline_core_fallback_r7_completion_item_count"] = fallback.get(
        "r7_completion_item_count",
        0,
    )
    manifest["latest_offline_core_fallback_r7_completion_item_class_counts"] = fallback.get(
        "r7_completion_item_class_counts",
        {},
    )
    manifest["latest_offline_core_fallback_r7_completion_field_gap_count_by_class"] = fallback.get(
        "r7_completion_field_gap_count_by_class",
        {},
    )
    manifest["latest_offline_core_fallback_r7_completion_plan_path"] = fallback.get(
        "r7_completion_plan_path",
        "",
    )
    manifest["latest_offline_core_fallback_r7_completion_required_execution_order"] = fallback.get(
        "r7_completion_required_execution_order",
        [],
    )
    manifest["latest_offline_core_fallback_r7_completion_route_contracts_status"] = fallback.get(
        "r7_completion_route_contracts_status",
        "",
    )
    manifest["latest_offline_core_fallback_r7_completion_route_contract_count"] = fallback.get(
        "r7_completion_route_contract_count",
        0,
    )
    manifest["latest_offline_core_fallback_r7_completion_open_route_count"] = fallback.get(
        "r7_completion_open_route_count",
        0,
    )
    manifest["latest_offline_core_fallback_r7_completion_open_route_ids"] = fallback.get(
        "r7_completion_open_route_ids",
        [],
    )
    manifest["latest_offline_core_fallback_r7_completion_route_contracts_path"] = fallback.get(
        "r7_completion_route_contracts_path",
        "",
    )
    manifest["latest_offline_core_fallback_r7_completion_route_work_packages_status"] = fallback.get(
        "r7_completion_route_work_packages_status",
        "",
    )
    manifest["latest_offline_core_fallback_r7_completion_route_work_package_count"] = fallback.get(
        "r7_completion_route_work_package_count",
        0,
    )
    manifest["latest_offline_core_fallback_r7_completion_open_work_package_count"] = fallback.get(
        "r7_completion_open_work_package_count",
        0,
    )
    manifest["latest_offline_core_fallback_r7_completion_open_work_package_ids"] = fallback.get(
        "r7_completion_open_work_package_ids",
        [],
    )
    manifest["latest_offline_core_fallback_r7_completion_route_work_packages_path"] = fallback.get(
        "r7_completion_route_work_packages_path",
        "",
    )
    manifest["latest_offline_core_fallback_r7_completion_route_work_package_templates_status"] = fallback.get(
        "r7_completion_route_work_package_templates_status",
        "",
    )
    manifest["latest_offline_core_fallback_r7_completion_route_work_package_preflight_status"] = fallback.get(
        "r7_completion_route_work_package_preflight_status",
        "",
    )
    manifest["latest_offline_core_fallback_r7_completion_submitted_work_package_count"] = fallback.get(
        "r7_completion_submitted_work_package_count",
        0,
    )
    manifest["latest_offline_core_fallback_r7_completion_passed_work_package_count"] = fallback.get(
        "r7_completion_passed_work_package_count",
        0,
    )
    manifest["latest_offline_core_fallback_r7_completion_blocked_work_package_count"] = fallback.get(
        "r7_completion_blocked_work_package_count",
        0,
    )
    manifest["latest_offline_core_fallback_r7_completion_route_work_package_preflight_path"] = fallback.get(
        "r7_completion_route_work_package_preflight_path",
        "",
    )
    manifest["latest_offline_core_fallback_r7_completion_route_work_package_patch_plan_status"] = fallback.get(
        "r7_completion_route_work_package_patch_plan_status",
        "",
    )
    manifest["latest_offline_core_fallback_r7_completion_route_work_package_patch_item_count"] = fallback.get(
        "r7_completion_route_work_package_patch_item_count",
        0,
    )
    manifest["latest_offline_core_fallback_r7_completion_route_work_package_highest_priority_patch_id"] = fallback.get(
        "r7_completion_route_work_package_highest_priority_patch_id",
        "",
    )
    manifest["latest_offline_core_fallback_r7_completion_route_work_package_patch_plan_path"] = fallback.get(
        "r7_completion_route_work_package_patch_plan_path",
        "",
    )
    manifest["latest_offline_core_fallback_r7_completion_route_work_package_assembly_gate_status"] = fallback.get(
        "r7_completion_route_work_package_assembly_gate_status",
        "",
    )
    manifest["latest_offline_core_fallback_r7_completion_route_work_package_assembly_step_count"] = fallback.get(
        "r7_completion_route_work_package_assembly_step_count",
        0,
    )
    manifest["latest_offline_core_fallback_r7_completion_route_work_package_ready_assembly_step_count"] = fallback.get(
        "r7_completion_route_work_package_ready_assembly_step_count",
        0,
    )
    manifest["latest_offline_core_fallback_r7_completion_route_work_package_blocked_assembly_step_count"] = fallback.get(
        "r7_completion_route_work_package_blocked_assembly_step_count",
        0,
    )
    manifest["latest_offline_core_fallback_r7_completion_route_work_package_assembly_gate_path"] = fallback.get(
        "r7_completion_route_work_package_assembly_gate_path",
        "",
    )
    manifest["latest_offline_core_fallback_submission_readiness_review_status"] = fallback.get(
        "submission_readiness_review_status",
        "",
    )
    manifest["latest_offline_core_fallback_submission_readiness_next_operator_action"] = fallback.get(
        "submission_readiness_next_operator_action",
        "",
    )
    manifest["latest_offline_core_fallback_submission_readiness_can_route_to_r8v"] = fallback.get(
        "submission_readiness_can_route_to_r8v",
        False,
    )
    manifest["latest_offline_core_fallback_submission_readiness_direct_highest_priority_patch_id"] = fallback.get(
        "submission_readiness_direct_highest_priority_patch_id",
        "",
    )
    manifest["latest_offline_core_fallback_submission_readiness_r7_highest_priority_patch_id"] = fallback.get(
        "submission_readiness_r7_highest_priority_patch_id",
        "",
    )
    manifest["latest_offline_core_fallback_submission_readiness_review_path"] = fallback.get(
        "submission_readiness_review_path",
        "",
    )
    manifest["latest_offline_core_fallback_source_package_route_guide_status"] = fallback.get(
        "source_package_route_guide_status",
        "",
    )
    manifest["latest_offline_core_fallback_source_package_recommended_route_id"] = fallback.get(
        "source_package_recommended_route_id",
        "",
    )
    manifest["latest_offline_core_fallback_source_package_next_operator_action"] = fallback.get(
        "source_package_next_operator_action",
        "",
    )
    manifest["latest_offline_core_fallback_source_package_route_option_count"] = fallback.get(
        "source_package_route_option_count",
        0,
    )
    manifest["latest_offline_core_fallback_source_package_route_guide_path"] = fallback.get(
        "source_package_route_guide_path",
        "",
    )
    manifest["latest_offline_core_fallback_source_package_route_preflight_status"] = fallback.get(
        "source_package_route_preflight_status",
        "",
    )
    manifest["latest_offline_core_fallback_source_package_recommended_route_preflight_status"] = fallback.get(
        "source_package_recommended_route_preflight_status",
        "",
    )
    manifest["latest_offline_core_fallback_source_package_route_preflight_next_operator_action"] = fallback.get(
        "source_package_route_preflight_next_operator_action",
        "",
    )
    manifest["latest_offline_core_fallback_source_package_ready_route_count"] = fallback.get(
        "source_package_ready_route_count",
        0,
    )
    manifest["latest_offline_core_fallback_source_package_waiting_route_count"] = fallback.get(
        "source_package_waiting_route_count",
        0,
    )
    manifest["latest_offline_core_fallback_source_package_blocked_route_count"] = fallback.get(
        "source_package_blocked_route_count",
        0,
    )
    manifest["latest_offline_core_fallback_source_package_route_preflight_path"] = fallback.get(
        "source_package_route_preflight_path",
        "",
    )
    manifest["latest_offline_core_fallback_validation_command"] = fallback.get(
        "validation_command",
        "",
    )
    manifest["latest_offline_core_fallback_rows_schema_path"] = fallback.get(
        "rows_schema_path",
        "",
    )
    manifest["latest_offline_core_fallback_collection_checklist_path"] = fallback.get(
        "collection_checklist_path",
        "",
    )
    manifest["latest_offline_core_fallback_batch_bundle_preflight_path"] = fallback.get(
        "batch_bundle_preflight_path",
        "",
    )
    manifest["latest_offline_core_fallback_temporal_window_preflight_path"] = fallback.get(
        "temporal_window_preflight_path",
        "",
    )
    manifest["latest_offline_core_fallback_scenario_semantic_preflight_path"] = fallback.get(
        "scenario_semantic_preflight_path",
        "",
    )
    manifest["latest_offline_core_fallback_downstream_routing_preflight_path"] = fallback.get(
        "downstream_routing_preflight_path",
        "",
    )
    status_parts = ["Agent60 复盘治理已接入 R7 coverage/minimum replay contract"]
    if fallback.get("r7_completion_route_work_package_patch_plan_status"):
        status_parts.append(
            "R8u-27 route work package patch plan="
            f"{fallback['r7_completion_route_work_package_patch_plan_status']}"
        )
    if fallback.get("r7_completion_route_work_package_assembly_gate_status"):
        status_parts.append(
            "R8u-28 route work package assembly gate="
            f"{fallback['r7_completion_route_work_package_assembly_gate_status']}"
            f"，blocked_steps={fallback.get('r7_completion_route_work_package_blocked_assembly_step_count', 0)}"
        )
    manifest["status"] = f"{'；'.join(status_parts)}；下一步指向 {top['action_id']}"
    manifest["next_stage"] = (
        f"按 Agent60 复盘结果，下一步优先推进 {top['action_id']}：{top['title']}。"
        f"{next_stage_rationale}"
    )
    if fallback.get("fallback_enabled"):
        manifest["next_stage"] += (
            f" 若没有真实 field package，则按离线核心 fallback 推进 {fallback['action_id']}："
            f"{fallback['title']}。"
        )
        if fallback.get("operator_handoff_status"):
            manifest["next_stage"] += (
                f" 当前 handoff={fallback['operator_handoff_status']}，"
                f"schema={fallback.get('field_rows_package_schema_status', '')}，"
                f"schema_validation={fallback.get('field_rows_schema_validation_status', '')}，"
            f"collection_checklist={fallback.get('field_rows_collection_checklist_status', '')}，"
            f"scenario_semantic={fallback.get('field_rows_scenario_semantic_preflight_status', '')}，"
            f"downstream_routing={fallback.get('field_rows_downstream_routing_preflight_status', '')}，"
            f"provenance_gate={fallback.get('field_rows_provenance_gate_status', '')}，"
                f"验收命令 `{fallback.get('validation_command', '')}`。"
            )
        if fallback.get("r7_completion_plan_status"):
            manifest["next_stage"] += (
                f" R7-to-R8p completion plan={fallback['r7_completion_plan_status']}，"
                f"completion_items={fallback.get('r7_completion_item_count', 0)}，"
                f"classes={fallback.get('r7_completion_item_class_counts', {})}，"
                f"field_gaps={fallback.get('r7_completion_field_gap_count_by_class', {})}。"
            )
        if fallback.get("r7_completion_route_contracts_status"):
                manifest["next_stage"] += (
                    f" completion route contracts={fallback['r7_completion_route_contracts_status']}，"
                    f"open_routes={fallback.get('r7_completion_open_route_ids', [])}。"
                )
        if fallback.get("r7_completion_route_work_packages_status"):
                manifest["next_stage"] += (
                    f" route work packages={fallback['r7_completion_route_work_packages_status']}，"
                    f"open_work_packages={fallback.get('r7_completion_open_work_package_ids', [])}。"
                )
        if fallback.get("r7_completion_route_work_package_preflight_status"):
                manifest["next_stage"] += (
                    f" route work package preflight="
                    f"{fallback['r7_completion_route_work_package_preflight_status']}，"
                    f"submitted={fallback.get('r7_completion_submitted_work_package_count', 0)}，"
                    f"passed={fallback.get('r7_completion_passed_work_package_count', 0)}，"
                    f"blocked={fallback.get('r7_completion_blocked_work_package_count', 0)}。"
                )
        if fallback.get("r7_completion_route_work_package_patch_plan_status"):
                manifest["next_stage"] += (
                    f" route work package patch plan="
                    f"{fallback['r7_completion_route_work_package_patch_plan_status']}，"
                    f"patch_items={fallback.get('r7_completion_route_work_package_patch_item_count', 0)}，"
                    f"highest_patch={fallback.get('r7_completion_route_work_package_highest_priority_patch_id', '')}。"
                )
        if fallback.get("r7_completion_route_work_package_assembly_gate_status"):
                manifest["next_stage"] += (
                    f" route work package assembly gate="
                    f"{fallback['r7_completion_route_work_package_assembly_gate_status']}，"
                    f"assembly_steps={fallback.get('r7_completion_route_work_package_assembly_step_count', 0)}，"
                    f"blocked_steps={fallback.get('r7_completion_route_work_package_blocked_assembly_step_count', 0)}。"
                )
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()

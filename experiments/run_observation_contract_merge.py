from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from water_ai.observation_contract import ObservationContractMerge


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SPARSE_METRICS_PATH = PROJECT_ROOT / "outputs" / "sensor_network_sparse_placement" / "sparse_placement_metrics.json"
CATALYST_PROXY_METRICS_PATH = PROJECT_ROOT / "outputs" / "catalyst_activity_proxy" / "catalyst_activity_proxy_metrics.json"
SOFT_SENSOR_MATRIX_METRICS_PATH = PROJECT_ROOT / "outputs" / "soft_sensor_matrix_coupling" / "soft_sensor_matrix_metrics.json"
MANIFEST_PATH = PROJECT_ROOT / "deliverables" / "manifest.json"
OUT_DIR = PROJECT_ROOT / "outputs" / "observation_contract_merge"
REPORT_DIR = PROJECT_ROOT / "outputs" / "observation_contract_merge_report"
DELIVERABLE_PATH = PROJECT_ROOT / "deliverables" / "model_core_optimization" / "observation_contract_merge.md"
METRICS_PATH = OUT_DIR / "observation_contract_metrics.json"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    DELIVERABLE_PATH.parent.mkdir(parents=True, exist_ok=True)

    result = ObservationContractMerge(
        sparse_placement_metrics=_read_json(SPARSE_METRICS_PATH),
        catalyst_proxy_metrics=_read_json(CATALYST_PROXY_METRICS_PATH),
        soft_sensor_matrix_metrics=_read_json(SOFT_SENSOR_MATRIX_METRICS_PATH),
    ).build()

    METRICS_PATH.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    (REPORT_DIR / "observation_contract_merge_report.md").write_text(_report_md(result), encoding="utf-8")
    DELIVERABLE_PATH.write_text(_deliverable_md(result), encoding="utf-8")
    _update_manifest(result)

    readiness = result["readiness"]
    recommended = result["recommended_observation_contract"]
    print(f"Observation contract merge: {readiness['observation_contract_status']}")
    print(f"- recommended: {readiness['recommended_contract_id']}")
    print(f"- weak_state: {readiness['base_weak_state_coverage']} -> {readiness['proxy_enhanced_weak_state_coverage']}")
    print(f"- cost: {readiness['recommended_cost_index']} / budget pass={readiness['budget_pass']}")
    print(f"- removed: {recommended['removed_base_pairs']}")
    print(f"- next: {result['next_refactor_action']['action_id']}")
    print(f"deliverable: {DELIVERABLE_PATH}")
    print(f"metrics: {METRICS_PATH}")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _report_md(result: dict[str, Any]) -> str:
    readiness = result["readiness"]
    recommended = result["recommended_observation_contract"]
    lines = [
        "# R2 观测契约合并报告",
        "",
        f"- 状态：`{readiness['observation_contract_status']}`",
        f"- 推荐 contract：`{readiness['recommended_contract_id']}`",
        f"- weak_state_coverage：{readiness['base_weak_state_coverage']} -> {readiness['proxy_enhanced_weak_state_coverage']}",
        f"- catalyst_observability_gain：{readiness['catalyst_observability_gain']}",
        f"- weak_axis_repair_status：`{readiness['weak_axis_repair_status']}`",
        f"- weak_axis_repair_score：{readiness['weak_axis_repair_score']}",
        f"- agent48_hidden_state_ledger_status：`{readiness['agent48_hidden_state_ledger_status']}`",
        f"- agent48_hidden_state_ready_count：{readiness['agent48_hidden_state_ready_count']}/{readiness['agent48_hidden_state_count']}",
        f"- agent48_hidden_state_minimum_patch_status：`{readiness['agent48_hidden_state_minimum_patch_status']}`",
        f"- agent48_hidden_state_hard_unresolved：{readiness['agent48_hidden_state_hard_unresolved']}",
        f"- agent48_pressure_headloss_candidate_pool_status：`{readiness['agent48_pressure_headloss_candidate_pool_status']}`",
        f"- agent48_pressure_headloss_candidate_count：{readiness['agent48_pressure_headloss_candidate_count']}",
        f"- estimated_missingness_robustness_after_patch：{readiness['missingness_robustness_after_patch']}",
        f"- recommended_cost_index：{readiness['recommended_cost_index']}",
        f"- budget_pass：{readiness['budget_pass']}",
        f"- can_write_to_release_gate：{readiness['can_write_to_release_gate']}",
        "",
        "## 推荐合同",
        "",
        f"- contract_id：`{recommended['contract_id']}`",
        f"- added_patch_pairs：{recommended['added_patch_pairs']}",
        f"- removed_base_pairs：{recommended['removed_base_pairs']}",
        f"- field_repair_evidence_requirement_count：{recommended['field_repair_evidence_requirement_count']}",
        f"- contract_pairs：{recommended['contract_pairs']}",
        "",
        "## 下一步",
        "",
        f"- `{result['next_refactor_action']['action_id']}`：{result['next_refactor_action']['title']}",
        f"- 原因：{result['next_refactor_action']['reason']}",
        f"- 禁止事项：{result['next_refactor_action']['must_not_do']}",
        "",
    ]
    return "\n".join(lines)


def _deliverable_md(result: dict[str, Any]) -> str:
    readiness = result["readiness"]
    base = result["base_layout_contract"]
    recommended = result["recommended_observation_contract"]
    lines = [
        "# R2 Agent48/51/54 观测契约合并",
        "",
        "## 核心判断",
        "",
        "R2 把稀疏布点、catalyst_activity 代理观测和软传感 node-modality/missingness 合同合成一个 observation contract。"
        "这一步的关键不是增加传感器数量，而是在预算约束下让弱隐藏状态可观测，并让软传感矩阵直接消费同一份观测合同。",
        "",
        f"- 状态：`{readiness['observation_contract_status']}`",
        f"- base weak_state_coverage：{readiness['base_weak_state_coverage']}",
        f"- proxy_enhanced_weak_state_coverage：{readiness['proxy_enhanced_weak_state_coverage']}",
        f"- catalyst_observability_gain：{readiness['catalyst_observability_gain']}",
        f"- weak_axis_repair_status：`{readiness['weak_axis_repair_status']}`",
        f"- weak_axis_repair_score：{readiness['weak_axis_repair_score']}",
        f"- field_repair_evidence_requirement_count：{readiness['field_repair_evidence_requirement_count']}",
        f"- agent48_hidden_state_ledger_status：`{readiness['agent48_hidden_state_ledger_status']}`",
        f"- agent48_hidden_state_ready_count：{readiness['agent48_hidden_state_ready_count']}/{readiness['agent48_hidden_state_count']}",
        f"- agent48_hidden_state_minimum_patch_status：`{readiness['agent48_hidden_state_minimum_patch_status']}`",
        f"- agent48_hidden_state_hard_unresolved：{readiness['agent48_hidden_state_hard_unresolved']}",
        f"- agent48_pressure_headloss_candidate_pool_status：`{readiness['agent48_pressure_headloss_candidate_pool_status']}`",
        f"- agent48_pressure_headloss_candidate_ids：{readiness['agent48_pressure_headloss_candidate_ids']}",
        f"- recommended_contract_id：`{readiness['recommended_contract_id']}`",
        f"- recommended_cost_index：{readiness['recommended_cost_index']}",
        f"- budget_pass：{readiness['budget_pass']}",
        f"- layout_alignment_pass：{readiness['base_layout_alignment_pass']}",
        f"- field_topology_ready：{readiness['field_topology_ready']}",
        f"- field_proxy_labels_ready：{readiness['field_proxy_labels_ready']}",
        f"- field_missingness_ready：{readiness['field_missingness_ready']}",
        "",
        "## Base Layout",
        "",
        f"- layout_id：`{base['layout_id']}`",
        f"- base_total_cost_index：{base['base_total_cost_index']}",
        f"- budget_limit：{base['budget_limit']}",
        f"- selected_pairs：{base['selected_pairs']}",
        f"- hidden_state_requirement_ledger_status：`{base['hidden_state_requirement_ledger_status']}`",
        f"- hidden_state_hard_unresolved：{base['hidden_state_hard_unresolved']}",
        f"- pressure_headloss_candidate_pool_status：`{base['pressure_headloss_candidate_pool_status']}`",
        f"- pressure_headloss_candidate_ids：{base['pressure_headloss_candidate_ids']}",
        "",
        "## Agent48 Hidden State Requirement Rows",
        "",
        "| Hidden State | Min Primary Score | Ready Count Basis | Hard Boundary |",
        "| --- | ---: | --- | --- |",
    ]
    for row in base["hidden_state_requirement_rows"]:
        lines.append(
            f"| `{row['hidden_state']}` | {row['min_primary_axis_score']} | "
            f"soft={row['ready_for_soft_sensor_estimation']}, control={row['ready_for_control_use']} | "
            f"{row['unresolved_requirements']} |"
        )
    lines.extend(
        [
            "",
            "## Contract Candidates",
            "",
            "| Candidate | Weak state | Cost | Budget | Added | Removed | Score |",
            "| --- | ---: | ---: | --- | --- | --- | ---: |",
        ]
    )
    for candidate in result["contract_candidates"]:
        lines.append(
            "| "
            f"`{candidate['candidate_id']}` | "
            f"{candidate['proxy_enhanced_weak_state_coverage']} | "
            f"{candidate['estimated_total_cost_index']} | "
            f"{candidate['budget_pass']} | "
            f"{candidate['added_patch_pairs']} | "
            f"{candidate['removed_base_pairs']} | "
            f"{candidate['contract_score']} |"
        )
    lines.extend(
        [
            "",
            "## Weak Axis Repair Records",
            "",
            "| Patch | Repair Priority | Patch Type | Why Needed |",
            "| --- | ---: | --- | --- |",
        ]
    )
    for patch in result["proxy_patch_records"]:
        lines.append(
            f"| `{patch['candidate_id']}` | {patch['repair_priority_score']} | "
            f"`{patch['patch_type']}` | {patch['repair_why_needed']} |"
        )
    lines.extend(
        [
            "",
            "## Recommended Observation Contract",
            "",
            f"- rationale：{recommended['rationale']}",
            f"- added_patch_pairs：{recommended['added_patch_pairs']}",
            f"- removed_base_pairs：{recommended['removed_base_pairs']}",
            f"- estimated_missingness_robustness_after_patch：{recommended['estimated_missingness_robustness_after_patch']}",
            "",
            "## Soft Sensor Schema Patch",
            "",
            f"- missing_layout_terms：{result['soft_sensor_schema_patch']['missing_layout_terms']}",
            f"- patch_target：{result['soft_sensor_schema_patch']['patch_target']}",
            "",
            "## Field Validation Requirements",
            "",
        ]
    )
    for requirement in result["field_validation_requirements"]:
        lines.append(
            f"- `{requirement['requirement_id']}`：{requirement['needed_for']}，"
            f"tables={requirement['required_tables']}"
        )
    lines.extend(
        [
            "",
            "## 下一步",
            "",
            f"- `{result['next_refactor_action']['action_id']}`：{result['next_refactor_action']['title']}",
            f"- 原因：{result['next_refactor_action']['reason']}",
            f"- 禁止事项：{result['next_refactor_action']['must_not_do']}",
            "",
            "## 边界",
            "",
            "- R2 只写 design prior 和 observation contract，不写执行器、不写 release gate。",
            "- budget-rebalanced contract 仍需要 field topology、proxy labels 和真实 missingness replay。",
            "- full proxy patch 是上限方案，但当前估算超预算，不能直接当成现场布点方案。",
            "",
        ]
    )
    return "\n".join(lines)


def _update_manifest(result: dict[str, Any]) -> None:
    manifest = _read_json(MANIFEST_PATH)
    manifest["status"] = "R2 Agent48/51/54 观测契约合并已生成"
    manifest["observation_contract_merge"] = {
        "observation_contract_merge": str(DELIVERABLE_PATH.relative_to(PROJECT_ROOT)),
        "observation_contract_merge_report": str(
            (REPORT_DIR / "observation_contract_merge_report.md").relative_to(PROJECT_ROOT)
        ),
        "observation_contract_metrics": str(METRICS_PATH.relative_to(PROJECT_ROOT)),
    }
    manifest["latest_observation_contract_status"] = result["readiness"]["observation_contract_status"]
    manifest["next_stage"] = (
        f"按 R2 观测契约合并结果，下一步优先推进 {result['next_refactor_action']['action_id']}："
        f"{result['next_refactor_action']['title']}。"
    )
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()

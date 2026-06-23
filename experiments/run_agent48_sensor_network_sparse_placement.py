from __future__ import annotations

import json
from pathlib import Path

from water_ai.agents.sensor_network_sparse_placement_agent import SensorNetworkSparsePlacementAgent


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = PROJECT_ROOT / "deliverables" / "manifest.json"
OUT_DIR = PROJECT_ROOT / "outputs" / "agent48_sensor_network_sparse_placement"
METRICS_DIR = PROJECT_ROOT / "outputs" / "sensor_network_sparse_placement"
DELIVERABLES_DIR = PROJECT_ROOT / "deliverables"
METRICS_PATH = METRICS_DIR / "sparse_placement_metrics.json"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    DELIVERABLES_DIR.mkdir(parents=True, exist_ok=True)
    report = SensorNetworkSparsePlacementAgent(max_sensors=6, budget_limit=5.8).run([])
    generated_files = {
        "sensor_network_sparse_placement": str(DELIVERABLES_DIR / "sensor_network_sparse_placement.md"),
        "agent48_report": str(OUT_DIR / "agent48_report.md"),
        "sparse_placement_metrics": str(METRICS_PATH),
    }

    (DELIVERABLES_DIR / "sensor_network_sparse_placement.md").write_text(_deliverable_md(report), encoding="utf-8")
    METRICS_PATH.write_text(
        json.dumps(
            {
                "observation_axes": report.metrics["observation_axes"],
                "topology_graph": report.metrics["topology_graph"],
                "selected_sensor_plan": report.metrics["selected_sensor_plan"],
                "algorithm_comparison": report.metrics["algorithm_comparison"],
                "baseline_comparison_contract": report.metrics["baseline_comparison_contract"],
                "selected_strategy": report.metrics["selected_strategy"],
                "coverage": report.metrics["coverage"],
                "placement_diagnostics": report.metrics["placement_diagnostics"],
                "hidden_state_requirement_ledger": report.metrics["hidden_state_requirement_ledger"],
                "hydraulic_path_coverage_contract": report.metrics["hydraulic_path_coverage_contract"],
                "readiness": report.metrics["readiness"],
                "soft_sensor_interface": report.metrics["soft_sensor_interface"],
                "method_contract": report.metrics["method_contract"],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    payload = {
        "sensor_network_sparse_placement": {
            "agent_name": report.agent_name,
            "confidence": report.confidence,
            "summary": report.summary,
            "recommendations": report.recommendations,
            "metrics": report.metrics,
            "issues": [
                {
                    "sensor": issue.sensor,
                    "issue_type": issue.issue_type,
                    "severity": issue.severity.value,
                    "message": issue.message,
                    "evidence": issue.evidence,
                }
                for issue in report.issues
            ],
        },
        "generated_files": generated_files,
    }
    (OUT_DIR / "agent48_report.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT_DIR / "agent48_report.md").write_text(_report_md(report, generated_files), encoding="utf-8")
    _update_manifest(generated_files, report)

    print(report.summary)
    for rec in report.recommendations:
        print(f"- {rec}")
    print(f"wrote {OUT_DIR / 'agent48_report.md'}")
    for key, path in generated_files.items():
        print(f"{key}: {path}")


def _deliverable_md(report) -> str:
    readiness = report.metrics["readiness"]
    coverage = report.metrics["coverage"]
    interface = report.metrics["soft_sensor_interface"]
    selected_strategy = report.metrics["selected_strategy"]
    baseline_contract = report.metrics["baseline_comparison_contract"]
    diagnostics = report.metrics["placement_diagnostics"]
    hidden_ledger = report.metrics["hidden_state_requirement_ledger"]
    minimum_patch = hidden_ledger["minimum_cost_requirement_patch"]
    pressure_pool = hidden_ledger["pressure_headloss_candidate_pool"]
    hydraulic_path = report.metrics["hydraulic_path_coverage_contract"]
    lines = [
        "# 管网布点与稀疏感知设计",
        "",
        f"- sparse_placement_status：`{readiness['sparse_placement_status']}`",
        f"- sparse_placement_score：`{readiness['sparse_placement_score']}`",
        f"- selected_strategy：`{selected_strategy['strategy_id']}`",
        f"- selected_strategy_score：`{selected_strategy['comparable_score']}`",
        f"- baseline_comparison_status：`{baseline_contract['comparison_status']}`",
        f"- best_vs_random_delta：`{baseline_contract['best_vs_random_delta']}`",
        f"- best_vs_cost_only_delta：`{baseline_contract['best_vs_cost_only_delta']}`",
        f"- selected_sensor_count：`{readiness['selected_sensor_count']}`",
        f"- total_cost_index：`{coverage['total_cost_index']}`",
        f"- weak_state_coverage：`{coverage['weak_state_coverage']}`",
        f"- reconstruction_stability_score：`{diagnostics['reconstruction_stability_score']}`",
        f"- condition_number_proxy：`{diagnostics['condition_number_proxy']}`",
        f"- weak_axis_gap_count：`{diagnostics['weak_axis_gap_count']}`",
        f"- hidden_state_ledger_status：`{hidden_ledger['ledger_status']}`",
        f"- ready_hidden_state_count：`{hidden_ledger['ready_hidden_state_count']}/{hidden_ledger['hidden_state_count']}`",
        f"- minimum_cost_patch_status：`{minimum_patch['patch_status']}`",
        f"- pressure_headloss_candidate_pool_status：`{pressure_pool['pool_status']}`",
        f"- pressure_headloss_candidate_count：`{pressure_pool['candidate_count']}`",
        f"- hydraulic_path_contract_status：`{hydraulic_path['contract_status']}`",
        f"- hydraulic_path_covered_stage_count：`{hydraulic_path['covered_stage_count']}/{hydraulic_path['path_stage_count']}`",
        f"- recirculation_loop_observed：`{hydraulic_path['recirculation_loop_observed']}`",
        f"- final_release_gate_needs_effluent_label：`{hydraulic_path['final_release_gate_needs_effluent_label']}`",
        f"- matrix_shape：`{interface['matrix_shape']}`",
        "",
        "## Strategy Comparison",
        "",
        "| Rank | Strategy | Comparable | Reconstruction | Classification | Robustness | Topology | Cost |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for item in report.metrics["algorithm_comparison"]:
        lines.append(
            f"| `{item['rank']}` | `{item['strategy_id']}` | `{item['comparable_score']}` | "
            f"`{item['reconstruction_objective']}` | `{item['classification_objective']}` | "
            f"`{item['robustness_objective']}` | `{item['topology_coverage_score']}` | `{item['cost_objective']}` |"
        )
    lines.extend(
        [
            "",
            "## Baseline Comparison Contract",
            "",
            f"- comparison_status：`{baseline_contract['comparison_status']}`",
            f"- required_baseline_strategy_ids：`{baseline_contract['required_baseline_strategy_ids']}`",
            f"- missing_baseline_strategy_ids：`{baseline_contract['missing_baseline_strategy_ids']}`",
            f"- claim_scope_use：{baseline_contract['claim_scope_use']}",
            f"- cannot_do：{baseline_contract['cannot_do']}",
        ]
    )
    lines.extend(
        [
            "",
        "## Selected Sparse Plan",
        "",
        "| Order | Candidate | Zone | Cost | Main Contribution |",
        "| --- | --- | --- | --- | --- |",
        ]
    )
    for item in report.metrics["selected_sensor_plan"]:
        lines.append(
            f"| `{item['selection_order']}` | `{item['candidate_id']}` | `{item['zone']}` | "
            f"`{item['cost_index']}` | {item['why_selected']} |"
        )
    lines.extend(["", "## Observation Coverage", "", "| Axis | Coverage |", "| --- | --- |"])
    for axis, value in coverage.items():
        lines.append(f"| `{axis}` | `{value}` |")
    lines.extend(
        [
            "",
            "## Placement Diagnostics",
            "",
            f"- diagnostic_status：`{diagnostics['diagnostic_status']}`",
            f"- selected_matrix_rank：`{diagnostics['selected_matrix_rank']}`",
            f"- axis_span_rank_ratio：`{diagnostics['axis_span_rank_ratio']}`",
            f"- layout_redundancy_score：`{diagnostics['layout_redundancy_score']}`",
            f"- single_point_dependency_count：`{diagnostics['single_point_dependency_count']}`",
            "",
            "| Axis | Current | Target | Best Available Candidate | Recoverable |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for gap in diagnostics["weak_axis_gaps"]:
        lines.append(
            f"| `{gap['axis']}` | `{gap['current_coverage']}` | `{gap['target']}` | "
            f"`{gap['best_available_candidate']}` | `{gap['recoverable_by_current_candidate_pool']}` |"
        )
    lines.extend(
        [
            "",
            "## Hidden State Requirement Ledger",
            "",
            "| Hidden State | Min Primary Score | Ready For Soft Sensor | Ready For Control | Patch Status | Unresolved |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in hidden_ledger["state_rows"]:
        lines.append(
            f"| `{row['hidden_state']}` | `{row['min_primary_axis_score']}` | "
            f"`{row['ready_for_soft_sensor_estimation']}` | `{row['ready_for_control_use']}` | "
            f"`{row['candidate_patch']['patch_status']}` | {row['unresolved_requirements']} |"
        )
    lines.extend(
        [
            "",
            "## Minimum Cost Requirement Patch",
            "",
            f"- patch_status：`{minimum_patch['patch_status']}`",
            f"- recommended_candidate_ids：`{minimum_patch['recommended_candidate_ids']}`",
            f"- hard_unresolved_hidden_states：`{minimum_patch['hard_unresolved_hidden_states']}`",
            f"- estimated_added_cost_upper_bound：`{minimum_patch['estimated_added_cost_upper_bound']}`",
            f"- pressure_headloss_candidate_ids：`{pressure_pool['candidate_ids']}`",
            "",
            "## Pressure/Headloss Candidate Pool",
            "",
            "| Candidate | Type | Target States | Cost | Required Table | Boundary |",
            "| --- | --- | --- | ---: | --- | --- |",
        ]
    )
    for candidate in pressure_pool["candidates"]:
        lines.append(
            f"| `{candidate['candidate_id']}` | `{candidate['candidate_type']}` | "
            f"{candidate['target_hidden_states']} | `{candidate['estimated_cost_index']}` | "
            f"`{candidate['required_table']}` | {candidate['design_boundary']} |"
        )
    lines.extend(
        [
            "",
            "## Hydraulic Path Coverage Contract",
            "",
            f"- contract_status：`{hydraulic_path['contract_status']}`",
            f"- can_support_soft_sensor_path_prior：`{hydraulic_path['can_support_soft_sensor_path_prior']}`",
            f"- can_support_control_replay_design_prior：`{hydraulic_path['can_support_control_replay_design_prior']}`",
            f"- can_finalize_field_deployment：`{hydraulic_path['can_finalize_field_deployment']}`",
            f"- unresolved_requirements：{hydraulic_path['unresolved_requirements']}",
            "",
            "| Stage | Role | Covered | Direct | Proxy | Sensors | Missing Zones | Missing Modalities |",
            "| --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for stage in hydraulic_path["path_stage_rows"]:
        lines.append(
            f"| `{stage['stage_id']}` {stage['stage_label']} | {stage['control_relevance']} | "
            f"`{stage['stage_covered']}` | `{stage['direct_zone_covered']}` | `{stage['proxy_zone_covered']}` | "
            f"{stage['selected_sensor_ids']} | {stage['missing_required_zones']} | {stage['missing_required_modalities']} |"
        )
    lines.extend(["", "## 结论", ""])
    for rec in report.recommendations:
        lines.append(f"- {rec}")
    return "\n".join(lines)


def _report_md(report, generated_files: dict[str, str]) -> str:
    readiness = report.metrics["readiness"]
    coverage = report.metrics["coverage"]
    selected_strategy = report.metrics["selected_strategy"]
    baseline_contract = report.metrics["baseline_comparison_contract"]
    diagnostics = report.metrics["placement_diagnostics"]
    hidden_ledger = report.metrics["hidden_state_requirement_ledger"]
    minimum_patch = hidden_ledger["minimum_cost_requirement_patch"]
    pressure_pool = hidden_ledger["pressure_headloss_candidate_pool"]
    hydraulic_path = report.metrics["hydraulic_path_coverage_contract"]
    lines = [
        "# Agent 48 管网布点与稀疏感知报告",
        "",
        f"- summary: {report.summary}",
        f"- sparse_placement_status: `{readiness['sparse_placement_status']}`",
        f"- selected_strategy: `{selected_strategy['strategy_id']}`",
        f"- selected_strategy_score: `{selected_strategy['comparable_score']}`",
        f"- baseline_comparison_status: `{baseline_contract['comparison_status']}`",
        f"- best_vs_random_delta: `{baseline_contract['best_vs_random_delta']}`",
        f"- best_vs_cost_only_delta: `{baseline_contract['best_vs_cost_only_delta']}`",
        f"- weak_state_coverage: `{coverage['weak_state_coverage']}`",
        f"- reconstruction_stability_score: `{diagnostics['reconstruction_stability_score']}`",
        f"- weak_axis_gap_count: `{diagnostics['weak_axis_gap_count']}`",
        f"- hidden_state_ledger_status: `{hidden_ledger['ledger_status']}`",
        f"- ready_hidden_state_count: `{hidden_ledger['ready_hidden_state_count']}/{hidden_ledger['hidden_state_count']}`",
        f"- minimum_cost_patch_status: `{minimum_patch['patch_status']}`",
        f"- hard_unresolved_hidden_states: `{minimum_patch['hard_unresolved_hidden_states']}`",
        f"- pressure_headloss_candidate_pool_status: `{pressure_pool['pool_status']}`",
        f"- pressure_headloss_candidate_count: `{pressure_pool['candidate_count']}`",
        f"- hydraulic_path_contract_status: `{hydraulic_path['contract_status']}`",
        f"- hydraulic_path_covered_stage_count: `{hydraulic_path['covered_stage_count']}/{hydraulic_path['path_stage_count']}`",
        f"- recirculation_loop_observed: `{hydraulic_path['recirculation_loop_observed']}`",
        f"- final_release_gate_needs_effluent_label: `{hydraulic_path['final_release_gate_needs_effluent_label']}`",
        f"- total_cost_index: `{coverage['total_cost_index']}`",
        "",
        "## 生成文件",
        "",
    ]
    for key, path in generated_files.items():
        lines.append(f"- {key}: `{path}`")
    lines.extend(["", "## 风险边界", ""])
    for issue in report.issues:
        lines.append(f"- `{issue.issue_type}`：{issue.message}")
    return "\n".join(lines)


def _update_manifest(generated_files: dict[str, str], report) -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    relative_generated = {
        key: str(Path(path).relative_to(PROJECT_ROOT))
        for key, path in generated_files.items()
    }
    baseline_contract = report.metrics["baseline_comparison_contract"]
    comparison = report.metrics["algorithm_comparison"]
    selected_strategy = report.metrics["selected_strategy"]
    hydraulic_path = report.metrics["hydraulic_path_coverage_contract"]
    manifest["sensor_network_sparse_placement"] = relative_generated
    manifest["latest_agent48_strategy_count"] = len(comparison)
    manifest["latest_agent48_selected_strategy"] = selected_strategy.get("strategy_id")
    manifest["latest_agent48_baseline_comparison_status"] = baseline_contract["comparison_status"]
    manifest["latest_agent48_best_vs_random_delta"] = baseline_contract["best_vs_random_delta"]
    manifest["latest_agent48_best_vs_cost_only_delta"] = baseline_contract["best_vs_cost_only_delta"]
    manifest["latest_agent48_hydraulic_path_contract_status"] = hydraulic_path["contract_status"]
    manifest["latest_agent48_hydraulic_path_covered_stage_count"] = hydraulic_path["covered_stage_count"]
    manifest["latest_agent48_final_release_gate_needs_effluent_label"] = hydraulic_path[
        "final_release_gate_needs_effluent_label"
    ]
    manifest["status"] = (
        "核心模型治理持续推进：Agent48 已加入 hydraulic path coverage contract，"
        "全局仍以 R7/R8p field package、真实 topology/labels、末端 release endpoint 和 release/actuator gate 为验证边界"
    )
    manifest["next_stage"] = (
        "全局优先导入 data_origin=field 的真实 field package 并运行 R7/R8p/R8v 验证；"
        "若无真实包，则继续用真实管网/处理单元拓扑、水力停留时间、维护可达性和节点级 field labels "
        "替换 Agent48 synthetic topology prior，并用 random/cost-only/sparse reconstruction/classification/topology-aware baselines "
        "重跑可比较布点 benchmark。"
    )
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()

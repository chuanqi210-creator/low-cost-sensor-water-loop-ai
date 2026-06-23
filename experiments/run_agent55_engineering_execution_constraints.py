from __future__ import annotations

import json
from pathlib import Path

from water_ai.agents.engineering_execution_constraint_agent import EngineeringExecutionConstraintAgent
from water_ai.agents.multi_facility_collaborative_control_agent import MultiFacilityCollaborativeControlAgent
from water_ai.agents.sensor_network_sparse_placement_agent import SensorNetworkSparsePlacementAgent


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = PROJECT_ROOT / "deliverables" / "manifest.json"
SPARSE_METRICS_PATH = PROJECT_ROOT / "outputs" / "sensor_network_sparse_placement" / "sparse_placement_metrics.json"
COLLAB_METRICS_PATH = PROJECT_ROOT / "outputs" / "multi_facility_collaborative_control" / "collaborative_control_metrics.json"
OUT_DIR = PROJECT_ROOT / "outputs" / "agent55_engineering_execution_constraints"
METRICS_DIR = PROJECT_ROOT / "outputs" / "engineering_execution_constraints"
DELIVERABLES_DIR = PROJECT_ROOT / "deliverables"
METRICS_PATH = METRICS_DIR / "engineering_constraints_metrics.json"
PATCHED_AGENT49_PATH = OUT_DIR / "agent49_engineering_patched_report.md"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    DELIVERABLES_DIR.mkdir(parents=True, exist_ok=True)

    sparse_metrics = _load_sparse_metrics()
    collaborative_metrics = _read_optional_json(COLLAB_METRICS_PATH)
    if not collaborative_metrics:
        collaborative_metrics = MultiFacilityCollaborativeControlAgent(sparse_placement_metrics=sparse_metrics).run([]).metrics

    report = EngineeringExecutionConstraintAgent(collaborative_control_metrics=collaborative_metrics).run([])
    metrics_payload = {
        "method_contract": report.metrics["method_contract"],
        "engineering_constraint_contract": report.metrics["engineering_constraint_contract"],
        "joint_action_constraint_evaluation": report.metrics["joint_action_constraint_evaluation"],
        "agent49_reward_patch": report.metrics["agent49_reward_patch"],
        "action_constraint_patch": report.metrics["action_constraint_patch"],
        "arbitration_patch": report.metrics["arbitration_patch"],
        "readiness": report.metrics["readiness"],
        "agent50_writeback": report.metrics["agent50_writeback"],
    }
    METRICS_PATH.write_text(json.dumps(metrics_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    patched_agent49 = MultiFacilityCollaborativeControlAgent(
        sparse_placement_metrics=sparse_metrics,
        engineering_constraints_metrics=metrics_payload,
    ).run([])
    _write_patched_agent49_metrics(patched_agent49)

    generated_files = {
        "engineering_execution_constraints": str(DELIVERABLES_DIR / "engineering_execution_constraints.md"),
        "agent55_report": str(OUT_DIR / "agent55_report.md"),
        "engineering_constraints_metrics": str(METRICS_PATH),
        "agent49_engineering_patched_report": str(PATCHED_AGENT49_PATH),
    }
    (DELIVERABLES_DIR / "engineering_execution_constraints.md").write_text(
        _deliverable_md(report, patched_agent49), encoding="utf-8"
    )
    (OUT_DIR / "agent55_report.md").write_text(_report_md(report, patched_agent49, generated_files), encoding="utf-8")
    (OUT_DIR / "agent55_report.json").write_text(
        json.dumps(
            {
                "engineering_execution_constraints": _report_payload(report),
                "patched_agent49": _report_payload(patched_agent49),
                "generated_files": generated_files,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    PATCHED_AGENT49_PATH.write_text(_patched_agent49_md(patched_agent49), encoding="utf-8")
    _update_manifest(generated_files)

    print(report.summary)
    for rec in report.recommendations:
        print(f"- {rec}")
    print(patched_agent49.summary)
    for key, path in generated_files.items():
        print(f"{key}: {path}")


def _load_sparse_metrics() -> dict[str, object]:
    if SPARSE_METRICS_PATH.exists():
        return json.loads(SPARSE_METRICS_PATH.read_text(encoding="utf-8"))
    report = SensorNetworkSparsePlacementAgent(max_sensors=6, budget_limit=5.8).run([])
    return {
        "observation_axes": report.metrics["observation_axes"],
        "selected_sensor_plan": report.metrics["selected_sensor_plan"],
        "coverage": report.metrics["coverage"],
        "readiness": report.metrics["readiness"],
        "soft_sensor_interface": report.metrics["soft_sensor_interface"],
        "method_contract": report.metrics["method_contract"],
    }


def _read_optional_json(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _write_patched_agent49_metrics(report) -> None:
    COLLAB_METRICS_PATH.parent.mkdir(parents=True, exist_ok=True)
    COLLAB_METRICS_PATH.write_text(
        json.dumps(
            {
                "method_contract": report.metrics["method_contract"],
                "sparse_context": report.metrics["sparse_context"],
                "control_state_axes": report.metrics["control_state_axes"],
                "facility_agents": report.metrics["facility_agents"],
                "facility_state_matrix": report.metrics["facility_state_matrix"],
                "joint_action_matrix": report.metrics["joint_action_matrix"],
                "reward_contract": report.metrics["reward_contract"],
                "engineering_constraints_context": report.metrics["engineering_constraints_context"],
                "shared_experience_pool": report.metrics["shared_experience_pool"],
                "decision_tree_distillation": report.metrics["decision_tree_distillation"],
                "readiness": report.metrics["readiness"],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def _deliverable_md(report, patched_agent49) -> str:
    readiness = report.metrics["readiness"]
    lines = [
        "# 工程执行约束进入 Reward 与仲裁",
        "",
        f"- engineering_constraints_status：`{readiness['engineering_constraints_status']}`",
        f"- mean_execution_feasibility：`{readiness['mean_execution_feasibility']}`",
        f"- reward_patch_coverage：`{readiness['reward_patch_coverage']}`",
        f"- arbitration_patch_coverage：`{readiness['arbitration_patch_coverage']}`",
        f"- can_write_to_actuator：`{readiness['can_write_to_actuator']}`",
        "",
        "## Joint Action Constraint Evaluation",
        "",
        "| Joint Action | Feasibility | Penalty | Hard Block | Reasons |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in report.metrics["joint_action_constraint_evaluation"]:
        lines.append(
            f"| `{row['joint_action_id']}` | `{row['execution_feasibility']}` | "
            f"`{row['engineering_constraint_penalty']}` | `{row['hard_blocked_by_engineering']}` | "
            f"`{row['hard_block_reasons']}` |"
        )
    lines.extend(
        [
            "",
            "## Patched Agent49 Top Actions",
            "",
            "| Rank | Joint Action | Score | Engineering Penalty | Feasibility |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for index, item in enumerate(patched_agent49.metrics["joint_action_matrix"], start=1):
        reward = item["reward_components"]
        lines.append(
            f"| `{index}` | `{item['joint_action_id']}` | `{item['joint_policy_score']}` | "
            f"`{reward['engineering_constraint_penalty']}` | `{reward['execution_feasibility']}` |"
        )
    lines.extend(["", "## 结论与边界", ""])
    for rec in report.recommendations:
        lines.append(f"- {rec}")
    return "\n".join(lines)


def _report_md(report, patched_agent49, generated_files: dict[str, str]) -> str:
    readiness = report.metrics["readiness"]
    lines = [
        "# Agent 55 工程执行约束报告",
        "",
        f"- summary: {report.summary}",
        f"- engineering_constraints_status: `{readiness['engineering_constraints_status']}`",
        f"- mean_execution_feasibility: `{readiness['mean_execution_feasibility']}`",
        f"- hard_blocked_joint_action_count: `{readiness['hard_blocked_joint_action_count']}`",
        f"- patched_agent49_top_action: `{patched_agent49.metrics['decision_tree_distillation']['top_ranked_action']}`",
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


def _patched_agent49_md(report) -> str:
    lines = [
        "# Agent49 工程约束补丁后协同控制摘要",
        "",
        f"- summary: {report.summary}",
        f"- engineering_constraints_status: `{report.metrics['engineering_constraints_context']['engineering_constraints_status']}`",
        "",
        "| Rank | Joint Action | Score | Penalty | Feasibility |",
        "| --- | --- | --- | --- | --- |",
    ]
    for index, item in enumerate(report.metrics["joint_action_matrix"], start=1):
        reward = item["reward_components"]
        lines.append(
            f"| `{index}` | `{item['joint_action_id']}` | `{item['joint_policy_score']}` | "
            f"`{reward['engineering_constraint_penalty']}` | `{reward['execution_feasibility']}` |"
        )
    return "\n".join(lines)


def _report_payload(report) -> dict[str, object]:
    return {
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
    }


def _update_manifest(generated_files: dict[str, str]) -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    relative_generated = {
        key: str(Path(path).relative_to(PROJECT_ROOT))
        for key, path in generated_files.items()
    }
    manifest["status"] = "工程执行约束 reward 与仲裁补丁已生成"
    manifest["engineering_execution_constraints"] = relative_generated
    manifest["next_stage"] = (
        "Agent55 已形成 P7 synthetic engineering reward/arbitration patch；"
        "下一轮由 Agent50 判断是否转向 P6 可推理 KG，同时等待 PLC/SCADA 点表、SOP 和 field execution replay"
    )
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()

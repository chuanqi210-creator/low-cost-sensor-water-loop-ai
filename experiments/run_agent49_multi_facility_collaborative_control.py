from __future__ import annotations

import json
from pathlib import Path

from water_ai.agents.multi_facility_collaborative_control_agent import MultiFacilityCollaborativeControlAgent
from water_ai.agents.sensor_network_sparse_placement_agent import SensorNetworkSparsePlacementAgent


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = PROJECT_ROOT / "deliverables" / "manifest.json"
SPARSE_METRICS_PATH = PROJECT_ROOT / "outputs" / "sensor_network_sparse_placement" / "sparse_placement_metrics.json"
ENGINEERING_CONSTRAINTS_METRICS_PATH = PROJECT_ROOT / "outputs" / "engineering_execution_constraints" / "engineering_constraints_metrics.json"
OBSERVATION_CONTRACT_METRICS_PATH = PROJECT_ROOT / "outputs" / "observation_contract_merge" / "observation_contract_metrics.json"
CATALYST_PROXY_METRICS_PATH = PROJECT_ROOT / "outputs" / "catalyst_activity_proxy" / "catalyst_activity_proxy_metrics.json"
CONTROL_REPLAY_STRESS_METRICS_PATH = (
    PROJECT_ROOT / "outputs" / "control_replay_counterfactual_stress" / "control_replay_stress_metrics.json"
)
OUT_DIR = PROJECT_ROOT / "outputs" / "agent49_multi_facility_collaborative_control"
METRICS_DIR = PROJECT_ROOT / "outputs" / "multi_facility_collaborative_control"
DELIVERABLES_DIR = PROJECT_ROOT / "deliverables"
METRICS_PATH = METRICS_DIR / "collaborative_control_metrics.json"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    DELIVERABLES_DIR.mkdir(parents=True, exist_ok=True)
    sparse_metrics = _load_sparse_metrics()
    engineering_constraints_metrics = _read_optional_json(ENGINEERING_CONSTRAINTS_METRICS_PATH)
    observation_contract_metrics = _read_optional_json(OBSERVATION_CONTRACT_METRICS_PATH)
    catalyst_proxy_metrics = _read_optional_json(CATALYST_PROXY_METRICS_PATH)
    control_replay_stress_metrics = _read_optional_json(CONTROL_REPLAY_STRESS_METRICS_PATH)
    report = MultiFacilityCollaborativeControlAgent(
        sparse_placement_metrics=sparse_metrics,
        observation_contract_metrics=observation_contract_metrics,
        catalyst_proxy_metrics=catalyst_proxy_metrics,
        engineering_constraints_metrics=engineering_constraints_metrics,
        control_replay_stress_metrics=control_replay_stress_metrics,
    ).run([])
    generated_files = {
        "multi_facility_collaborative_control": str(DELIVERABLES_DIR / "multi_facility_collaborative_control.md"),
        "agent49_report": str(OUT_DIR / "agent49_report.md"),
        "collaborative_control_metrics": str(METRICS_PATH),
    }

    (DELIVERABLES_DIR / "multi_facility_collaborative_control.md").write_text(_deliverable_md(report), encoding="utf-8")
    METRICS_PATH.write_text(
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
                "control_replay_guardrail_context": report.metrics["control_replay_guardrail_context"],
                "shared_experience_pool": report.metrics["shared_experience_pool"],
                "decision_tree_distillation": report.metrics["decision_tree_distillation"],
                "readiness": report.metrics["readiness"],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    payload = {
        "multi_facility_collaborative_control": {
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
    (OUT_DIR / "agent49_report.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT_DIR / "agent49_report.md").write_text(_report_md(report, generated_files), encoding="utf-8")
    _update_manifest(generated_files)

    print(report.summary)
    for rec in report.recommendations:
        print(f"- {rec}")
    print(f"wrote {OUT_DIR / 'agent49_report.md'}")
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


def _deliverable_md(report) -> str:
    readiness = report.metrics["readiness"]
    distilled = report.metrics["decision_tree_distillation"]
    guardrail = report.metrics["control_replay_guardrail_context"]
    observation_context = report.metrics["sparse_context"]["observation_contract_context"]
    lines = [
        "# 多设施协同控制与策略蒸馏设计",
        "",
        f"- coordination_status：`{readiness['coordination_status']}`",
        f"- coordination_readiness_score：`{readiness['coordination_readiness_score']}`",
        f"- can_write_to_actuator：`{readiness['can_write_to_actuator']}`",
        f"- control_replay_guardrails_integrated：`{readiness['control_replay_guardrails_integrated']}`",
        f"- reward_prior_guardrail_available：`{guardrail['reward_prior_guardrail_available']}`",
        f"- catalyst_proxy_summary_status：`{guardrail['catalyst_proxy_summary_status']}`",
        f"- catalyst_proxy_scoreable_batch_count：`{guardrail['catalyst_proxy_scoreable_batch_count']}`",
        f"- catalyst_guardrail_mode：`{guardrail['catalyst_guardrail_mode']}`",
        f"- pressure_headloss_candidate_pool_status：`{guardrail['pressure_headloss_candidate_pool_status']}`",
        f"- pressure_headloss_candidate_count：`{guardrail['pressure_headloss_candidate_count']}`",
        f"- pressure_headloss_can_relax_control_guardrail：`{guardrail['pressure_headloss_can_relax_control_guardrail']}`",
        f"- distilled_policy_accuracy_proxy：`{distilled['distilled_policy_accuracy_proxy']}`",
        f"- top_ranked_action：`{distilled['top_ranked_action']}`",
        "",
        "## Facility Agents",
        "",
        "| Agent | Role | Observed Nodes | Candidate Actions |",
        "| --- | --- | --- | --- |",
    ]
    for item in report.metrics["facility_agents"]:
        lines.append(
            f"| `{item['facility_agent_id']}` | {item['facility_role']} | {item['observed_nodes']} | {item['candidate_actions']} |"
        )
    lines.extend(
        [
            "",
            "## Joint Actions",
            "",
            "| Rank | Joint Action | Score | R3b Penalty | R3b Bonus | Intent |",
            "| --- | --- | --- | ---: | ---: | --- |",
        ]
    )
    for index, item in enumerate(report.metrics["joint_action_matrix"], start=1):
        reward = item["reward_components"]
        lines.append(
            f"| `{index}` | `{item['joint_action_id']}` | `{item['joint_policy_score']}` | "
            f"`{reward['control_replay_guardrail_penalty']}` | "
            f"`{reward['control_replay_guardrail_bonus']}` | {item['control_intent']} |"
        )
    lines.extend(
        [
            "",
            "## R3b Control Replay Guardrails",
            "",
            f"- patch_id：`{guardrail['patch_id']}`",
            f"- guardrail_candidate_accuracy：`{guardrail['guardrail_candidate_accuracy']}`",
            f"- field_replay_coverage：`{guardrail['field_replay_coverage']}`",
            f"- catalyst_proxy_summary_status：`{guardrail['catalyst_proxy_summary_status']}`",
            f"- catalyst_proxy_scoreable_batch_count：`{guardrail['catalyst_proxy_scoreable_batch_count']}`",
            f"- catalyst_guardrail_mode：`{guardrail['catalyst_guardrail_mode']}`",
            f"- pressure_headloss_candidate_ids：`{observation_context['pressure_headloss_candidate_ids']}`",
            f"- pressure_headloss_control_boundary：{observation_context['pressure_headloss_control_boundary']}",
            f"- 边界：{guardrail['field_boundary']}",
        ]
    )
    lines.extend(["", "## Decision Tree Distillation", ""])
    for rule in distilled["tree_rules"]:
        lines.append(f"- `{rule['rule_id']}`：IF {rule['if']} THEN `{rule['then']}`；{rule['engineering_meaning']}")
    lines.extend(["", "## 结论", ""])
    for rec in report.recommendations:
        lines.append(f"- {rec}")
    return "\n".join(lines)


def _report_md(report, generated_files: dict[str, str]) -> str:
    readiness = report.metrics["readiness"]
    distilled = report.metrics["decision_tree_distillation"]
    guardrail = report.metrics["control_replay_guardrail_context"]
    lines = [
        "# Agent 49 多设施协同控制报告",
        "",
        f"- summary: {report.summary}",
        f"- coordination_status: `{readiness['coordination_status']}`",
        f"- can_write_to_actuator: `{readiness['can_write_to_actuator']}`",
        f"- control_replay_guardrails_integrated: `{readiness['control_replay_guardrails_integrated']}`",
        f"- R3b patch: `{guardrail['patch_id']}`",
        f"- catalyst_proxy_summary_status: `{guardrail['catalyst_proxy_summary_status']}`",
        f"- catalyst_guardrail_mode: `{guardrail['catalyst_guardrail_mode']}`",
        f"- pressure_headloss_candidate_pool_status: `{guardrail['pressure_headloss_candidate_pool_status']}`",
        f"- pressure_headloss_candidate_count: `{guardrail['pressure_headloss_candidate_count']}`",
        f"- pressure_headloss_can_relax_control_guardrail: `{guardrail['pressure_headloss_can_relax_control_guardrail']}`",
        f"- distilled_policy_accuracy_proxy: `{distilled['distilled_policy_accuracy_proxy']}`",
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


def _update_manifest(generated_files: dict[str, str]) -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    relative_generated = {
        key: str(Path(path).relative_to(PROJECT_ROOT))
        for key, path in generated_files.items()
    }
    manifest["status"] = "R3b 已把 R3 反事实 guardrails 接入 Agent49 reward prior，仍需 field replay 和 Agent52 guardrail-aware 复核"
    manifest["multi_facility_collaborative_control"] = relative_generated
    manifest["latest_agent49_reward_prior_status"] = "R3b_reward_prior_guardrails_integrated_synthetic_only"
    manifest["next_stage"] = "推进 R3c：让 Agent52 消费 Agent49 的 R3b guardrail-aware reward prior，刷新 replay regret、误保护成本和 field replay 阻断边界；仍不得写执行器或 release gate"
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()

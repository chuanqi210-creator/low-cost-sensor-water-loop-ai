from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from water_ai.control_replay_stress import ControlReplayCounterfactualStress


PROJECT_ROOT = Path(__file__).resolve().parents[1]
COLLAB_METRICS_PATH = PROJECT_ROOT / "outputs" / "multi_facility_collaborative_control" / "collaborative_control_metrics.json"
REPLAY_METRICS_PATH = PROJECT_ROOT / "outputs" / "multi_facility_replay_evaluation" / "replay_evaluation_metrics.json"
OBSERVATION_CONTRACT_METRICS_PATH = PROJECT_ROOT / "outputs" / "observation_contract_merge" / "observation_contract_metrics.json"
MANIFEST_PATH = PROJECT_ROOT / "deliverables" / "manifest.json"
OUT_DIR = PROJECT_ROOT / "outputs" / "control_replay_counterfactual_stress"
REPORT_DIR = PROJECT_ROOT / "outputs" / "control_replay_counterfactual_stress_report"
DELIVERABLE_PATH = PROJECT_ROOT / "deliverables" / "model_core_optimization" / "control_replay_counterfactual_stress.md"
METRICS_PATH = OUT_DIR / "control_replay_stress_metrics.json"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    DELIVERABLE_PATH.parent.mkdir(parents=True, exist_ok=True)

    result = ControlReplayCounterfactualStress(
        collaborative_control_metrics=_read_json(COLLAB_METRICS_PATH),
        replay_evaluation_metrics=_read_json(REPLAY_METRICS_PATH),
        observation_contract_metrics=_read_json(OBSERVATION_CONTRACT_METRICS_PATH),
    ).build()

    METRICS_PATH.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    (REPORT_DIR / "control_replay_counterfactual_stress_report.md").write_text(_report_md(result), encoding="utf-8")
    DELIVERABLE_PATH.write_text(_deliverable_md(result), encoding="utf-8")
    _update_manifest(result)

    metrics = result["counterfactual_metrics"]
    print(f"Control replay stress: {result['readiness']['control_replay_stress_status']}")
    print(f"- baseline accuracy: {metrics['baseline']['joint_action_accuracy']}")
    print(f"- observation accuracy: {metrics['observation_contract']['joint_action_accuracy']}")
    print(f"- guardrail accuracy: {metrics['guardrail_candidate']['joint_action_accuracy']}")
    print(f"- p95 regret delta: {metrics['p95_reward_regret_delta_guardrail']}")
    print(f"- next: {result['next_refactor_action']['action_id']}")
    print(f"deliverable: {DELIVERABLE_PATH}")
    print(f"metrics: {METRICS_PATH}")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _report_md(result: dict[str, Any]) -> str:
    metrics = result["counterfactual_metrics"]
    readiness = result["readiness"]
    lines = [
        "# R3 控制 Replay 反事实压力测试报告",
        "",
        f"- 状态：`{readiness['control_replay_stress_status']}`",
        f"- stress_case_count：{metrics['stress_case_count']}",
        f"- baseline_joint_action_accuracy：{metrics['baseline']['joint_action_accuracy']}",
        f"- observation_contract_accuracy：{metrics['observation_contract']['joint_action_accuracy']}",
        f"- guardrail_candidate_accuracy：{metrics['guardrail_candidate']['joint_action_accuracy']}",
        f"- p95_reward_regret_delta_guardrail：{metrics['p95_reward_regret_delta_guardrail']}",
        f"- protective_false_positive_cost_delta_guardrail：{metrics['protective_false_positive_cost_delta_guardrail']}",
        f"- can_write_to_actuator：{readiness['can_write_to_actuator']}",
        "",
        "## Stress Cases",
        "",
        "| Case | Scenario | Baseline | Observation | Guardrail | Resolution |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in result["stress_table"]:
        lines.append(
            "| "
            f"`{row['case_id']}` | "
            f"{row['scenario']} | "
            f"`{row['baseline_policy_action_id']}` | "
            f"`{row['observation_contract_action_id']}` | "
            f"`{row['guardrail_candidate_action_id']}` | "
            f"{row['stress_resolution']} |"
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
        ]
    )
    return "\n".join(lines)


def _deliverable_md(result: dict[str, Any]) -> str:
    metrics = result["counterfactual_metrics"]
    readiness = result["readiness"]
    patch = result["reward_prior_patch"]
    lines = [
        "# R3 Agent49/52 控制 Replay 反事实压力测试",
        "",
        "## 核心判断",
        "",
        "R3 把 Agent52 的 replay-ready baseline 升级为反事实压力测试。它比较三层策略："
        "原始 Agent49/52 baseline、接入 R2 观测契约后的 observation-aware policy、以及 R3 reward guardrail candidate。"
        "目标不是训练在线 MARL，而是先找出高 regret、误保护和工程不可执行场景。",
        "",
        f"- 状态：`{readiness['control_replay_stress_status']}`",
        f"- baseline accuracy：{metrics['baseline']['joint_action_accuracy']}",
        f"- observation contract accuracy：{metrics['observation_contract']['joint_action_accuracy']}",
        f"- guardrail candidate accuracy：{metrics['guardrail_candidate']['joint_action_accuracy']}",
        f"- p95 regret delta：{metrics['p95_reward_regret_delta_guardrail']}",
        f"- false positive cost delta：{metrics['protective_false_positive_cost_delta_guardrail']}",
        f"- unsafe_action_block_correction_rate：{metrics['unsafe_action_block_correction_rate']}",
        f"- field_replay_coverage：{metrics['field_replay_coverage']}",
        f"- can_update_agent49_reward_prior：{readiness['can_update_agent49_reward_prior']}",
        f"- can_write_to_actuator：{readiness['can_write_to_actuator']}",
        f"- can_write_to_release_gate：{readiness['can_write_to_release_gate']}",
        "",
        "## Counterfactual Stress Table",
        "",
        "| Case | Scenario | Expert | Baseline | Observation Contract | Guardrail Candidate | Regret baseline -> guardrail | Boundary |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in result["stress_table"]:
        lines.append(
            "| "
            f"`{row['case_id']}` | "
            f"{row['scenario']} | "
            f"`{row['expert_action_id']}` | "
            f"`{row['baseline_policy_action_id']}` | "
            f"`{row['observation_contract_action_id']}` | "
            f"`{row['guardrail_candidate_action_id']}` | "
            f"{row['baseline_reward_regret']} -> {row['guardrail_reward_regret']} | "
            f"{row['residual_boundary']} |"
        )
    lines.extend(
        [
            "",
            "## Reward Prior Patch Candidate",
            "",
            f"- patch_id：`{patch['patch_id']}`",
            f"- target_agent：`{patch['target_agent']}`",
            f"- metric_delta：{patch['metric_delta']}",
            "",
        ]
    )
    for rule in patch["candidate_rules"]:
        lines.append(f"- `{rule['rule_id']}`：IF {rule['if']} THEN {rule['then']}；{rule['expected_effect']}")
    lines.extend(["", "## Field Replay Requirements", ""])
    for requirement in result["field_replay_requirements"]:
        lines.append(
            f"- `{requirement['requirement_id']}`：{requirement['needed_for']}，fields={requirement['required_fields']}"
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
            "- R3 只能写 reward prior 和 stress suite 候选，不能写执行器。",
            "- guardrail 在 synthetic stress 上改善指标，不等于现场控制有效性。",
            "- field replay coverage 仍为 0 前，不训练 offline RL，不做 release gate。",
            "",
        ]
    )
    return "\n".join(lines)


def _update_manifest(result: dict[str, Any]) -> None:
    manifest = _read_json(MANIFEST_PATH)
    manifest["status"] = "R3 控制 replay 反事实压力测试已生成"
    manifest["control_replay_counterfactual_stress"] = {
        "control_replay_counterfactual_stress": str(DELIVERABLE_PATH.relative_to(PROJECT_ROOT)),
        "control_replay_counterfactual_stress_report": str(
            (REPORT_DIR / "control_replay_counterfactual_stress_report.md").relative_to(PROJECT_ROOT)
        ),
        "control_replay_stress_metrics": str(METRICS_PATH.relative_to(PROJECT_ROOT)),
    }
    manifest["latest_control_replay_stress_status"] = result["readiness"]["control_replay_stress_status"]
    manifest["next_stage"] = (
        f"按 R3 控制 replay 压力测试结果，下一步优先推进 {result['next_refactor_action']['action_id']}："
        f"{result['next_refactor_action']['title']}。"
    )
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()

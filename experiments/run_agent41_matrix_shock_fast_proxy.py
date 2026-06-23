from __future__ import annotations

import json
from pathlib import Path

from water_ai.agents.arbitration_agent import ArbitrationAgent
from water_ai.agents.catalyst_lifecycle_agent import CatalystLifecycleAgent
from water_ai.agents.control_strategy_agent import ControlStrategyAgent
from water_ai.agents.cost_safety_agent import CostSafetyAgent
from water_ai.agents.data_quality_agent import DataQualityAgent
from water_ai.agents.fault_diagnosis_agent import FaultDiagnosisAgent
from water_ai.agents.matrix_shock_fast_proxy_agent import MatrixShockFastProxyAgent
from water_ai.agents.mechanism_agent import MechanismAgent
from water_ai.agents.soft_sensor_agent import SoftSensorAgent
from water_ai.agents.strategy_profile_agent import StrategyProfileAgent
from water_ai.agents.validation_planning_agent import ValidationPlanningAgent
from water_ai.process_dynamics import generate_sensor_stream_from_process_state, initial_process_state


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = PROJECT_ROOT / "deliverables" / "manifest.json"
AGENT40_METRICS = PROJECT_ROOT / "outputs" / "grey_box_dynamic_latency" / "latency_budget_metrics.json"
AGENT39_METRICS = PROJECT_ROOT / "outputs" / "soft_sensor_training" / "soft_sensor_conformal_metrics.json"
OUT_DIR = PROJECT_ROOT / "outputs" / "agent41_matrix_shock_fast_proxy"
DELIVERABLES_DIR = PROJECT_ROOT / "deliverables"
FAST_PROXY_METRICS = PROJECT_ROOT / "outputs" / "matrix_shock_fast_proxy" / "fast_proxy_metrics.json"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    FAST_PROXY_METRICS.parent.mkdir(parents=True, exist_ok=True)
    DELIVERABLES_DIR.mkdir(parents=True, exist_ok=True)
    latency_metrics = _read_json(AGENT40_METRICS)
    conformal_readiness = _read_conformal_readiness()
    scenario_reports = _scenario_reports(latency_metrics, conformal_readiness)
    matrix_report = scenario_reports["matrix_shock"]["proxy_report"]
    control_snapshot = _control_snapshot(latency_metrics, conformal_readiness)
    generated_files = {
        "matrix_shock_fast_proxy_control": str(DELIVERABLES_DIR / "matrix_shock_fast_proxy_control.md"),
        "agent41_report": str(OUT_DIR / "agent41_report.md"),
        "fast_proxy_metrics": str(FAST_PROXY_METRICS),
    }

    (DELIVERABLES_DIR / "matrix_shock_fast_proxy_control.md").write_text(
        _deliverable_md(scenario_reports, control_snapshot),
        encoding="utf-8",
    )
    FAST_PROXY_METRICS.write_text(
        json.dumps(
            {
                "scenario_reports": _serializable_scenario_reports(scenario_reports),
                "control_snapshot": control_snapshot,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    payload = {
        "matrix_shock_fast_proxy": {
            "agent_name": matrix_report.agent_name,
            "confidence": matrix_report.confidence,
            "summary": matrix_report.summary,
            "recommendations": matrix_report.recommendations,
            "metrics": matrix_report.metrics,
            "issues": [
                {
                    "sensor": issue.sensor,
                    "issue_type": issue.issue_type,
                    "severity": issue.severity.value,
                    "message": issue.message,
                    "evidence": issue.evidence,
                }
                for issue in matrix_report.issues
            ],
        },
        "scenario_reports": _serializable_scenario_reports(scenario_reports),
        "control_snapshot": control_snapshot,
        "generated_files": generated_files,
    }
    (OUT_DIR / "agent41_report.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT_DIR / "agent41_report.md").write_text(_report_md(matrix_report, generated_files, control_snapshot), encoding="utf-8")
    _update_manifest(generated_files)

    print(matrix_report.summary)
    for rec in matrix_report.recommendations:
        print(f"- {rec}")
    print(f"wrote {OUT_DIR / 'agent41_report.md'}")
    for key, path in generated_files.items():
        print(f"{key}: {path}")


def _scenario_reports(latency_metrics: dict[str, object], conformal_readiness: dict[str, object]) -> dict[str, dict[str, object]]:
    scenarios = ["matrix_shock", "clean_release", "oxidant_limitation"]
    reports: dict[str, dict[str, object]] = {}
    for scenario in scenarios:
        readings = generate_sensor_stream_from_process_state(initial_process_state(scenario), n=24, seed=7)
        report = MatrixShockFastProxyAgent(
            latency_metrics=latency_metrics,
            conformal_readiness=conformal_readiness,
            evidence_stage="synthetic_replay",
        ).run(readings)
        reports[scenario] = {
            "proxy_report": report,
            "summary": report.summary,
            "proxy": report.metrics["proxy"],
            "mitigation_budget": report.metrics["mitigation_budget"],
            "readiness": report.metrics["readiness"],
        }
    return reports


def _control_snapshot(latency_metrics: dict[str, object], conformal_readiness: dict[str, object]) -> dict[str, object]:
    readings = generate_sensor_stream_from_process_state(initial_process_state("matrix_shock"), n=24, seed=7)
    dq_report = DataQualityAgent().run(readings)
    soft_report = SoftSensorAgent(data_quality_report=dq_report).run(readings)
    mechanism_report = MechanismAgent(data_quality_report=dq_report, soft_sensor_report=soft_report).run(readings)
    fault_report = FaultDiagnosisAgent(
        data_quality_report=dq_report,
        soft_sensor_report=soft_report,
        mechanism_report=mechanism_report,
    ).run(readings)
    lifecycle_report = CatalystLifecycleAgent(soft_sensor_report=soft_report, fault_report=fault_report).run(readings)
    validation_report = ValidationPlanningAgent(soft_sensor_report=soft_report, fault_report=fault_report).run(readings)
    proxy_report = MatrixShockFastProxyAgent(
        latency_metrics=latency_metrics,
        conformal_readiness=conformal_readiness,
        evidence_stage="synthetic_replay",
    ).run(readings)
    baseline_control = ControlStrategyAgent(
        soft_sensor_report=soft_report,
        fault_report=fault_report,
        catalyst_lifecycle_report=lifecycle_report,
        validation_planning_report=validation_report,
    ).run(readings)
    adapted_control = ControlStrategyAgent(
        soft_sensor_report=soft_report,
        fault_report=fault_report,
        catalyst_lifecycle_report=lifecycle_report,
        validation_planning_report=validation_report,
        matrix_shock_fast_proxy_report=proxy_report,
    ).run(readings)
    strategy_report = StrategyProfileAgent(soft_sensor_report=soft_report, fault_report=fault_report).run(readings)
    adapted_cost = CostSafetyAgent(
        control_report=adapted_control,
        objective_profile=str(strategy_report.metrics["selected_profile"]),
    ).run(readings)
    adapted_arbitration = ArbitrationAgent(
        soft_sensor_report=soft_report,
        control_report=adapted_control,
        cost_safety_report=adapted_cost,
    ).run(readings)
    baseline_hold = _action_by_id(baseline_control.metrics["ranked_actions"], "hold_for_validation")
    adapted_hold = _action_by_id(adapted_control.metrics["ranked_actions"], "hold_for_validation")
    adapted_switch = _action_by_id(adapted_control.metrics["ranked_actions"], "switch_or_pretreat")
    return {
        "scenario": "matrix_shock",
        "baseline_top_actions": [action["action_id"] for action in baseline_control.metrics["ranked_actions"][:4]],
        "adapted_top_actions": [action["action_id"] for action in adapted_control.metrics["ranked_actions"][:4]],
        "baseline_hold_min": baseline_hold.get("parameters", {}).get("hold_min"),
        "adapted_hold_min": adapted_hold.get("parameters", {}).get("hold_min"),
        "adapted_switch_protective_mode": adapted_switch.get("parameters", {}).get("protective_mode"),
        "adapted_release_policy": adapted_switch.get("parameters", {}).get("release_policy"),
        "adapted_final_plan": [action["action_id"] for action in adapted_arbitration.metrics["final_plan"]],
        "blocked_actions": adapted_arbitration.metrics["blocked_actions"],
        "proxy_readiness": proxy_report.metrics["readiness"],
        "proxy_mitigation": proxy_report.metrics["mitigation_budget"],
    }


def _action_by_id(actions: list[dict[str, object]], action_id: str) -> dict[str, object]:
    for action in actions:
        if action.get("action_id") == action_id:
            return action
    return {}


def _deliverable_md(scenario_reports: dict[str, dict[str, object]], control_snapshot: dict[str, object]) -> str:
    matrix = scenario_reports["matrix_shock"]
    proxy = matrix["proxy"]
    mitigation = matrix["mitigation_budget"]
    readiness = matrix["readiness"]
    lines = [
        "# 基质冲击快代理与延迟感知控制",
        "",
        f"- fast_proxy_status：`{readiness['fast_proxy_status']}`",
        f"- proxy_score：`{proxy['proxy_score']}`",
        f"- specificity_guard_score：`{proxy['specificity_guard_score']}`",
        f"- protective_triggered：`{proxy['protective_triggered']}`",
        f"- protective_action_margin_min：`{mitigation['protective_action_margin_min']}`",
        f"- original_evidence_margin_min：`{mitigation['original_evidence_margin_min']}`",
        f"- projected_evidence_margin_after_extension_min：`{mitigation['projected_evidence_margin_after_extension_min']}`",
        f"- can_write_to_release_gate：`{readiness['can_write_to_release_gate']}`",
        "",
        "## 场景区分",
        "",
        "| 场景 | proxy_score | specificity_guard | protective_triggered | release_block |",
        "| --- | ---: | ---: | --- | --- |",
    ]
    for scenario, item in scenario_reports.items():
        scenario_proxy = item["proxy"]
        lines.append(
            f"| `{scenario}` | {scenario_proxy['proxy_score']} | {scenario_proxy['specificity_guard_score']} | "
            f"{scenario_proxy['protective_triggered']} | {scenario_proxy['release_block_recommended']} |"
        )
    lines.extend(
        [
            "",
            "## 控制接入效果",
            "",
            f"- baseline_hold_min：`{control_snapshot['baseline_hold_min']}`",
            f"- adapted_hold_min：`{control_snapshot['adapted_hold_min']}`",
            f"- adapted_switch_protective_mode：`{control_snapshot['adapted_switch_protective_mode']}`",
            f"- adapted_release_policy：`{control_snapshot['adapted_release_policy']}`",
            f"- adapted_final_plan：`{control_snapshot['adapted_final_plan']}`",
            "",
            "## 结论",
            "",
            "- 快代理解决的是保护性动作的提前触发，不解决自动放行。",
            "- `matrix_shock` 在 synthetic replay 中可由 EC/浊度/UV254/pH/ORP 快代理提前进入预处理/切换和暂存验证。",
            "- 真实写入前必须用 timestamped campaign replay 验证 precision、recall、提前量和误触发成本。",
        ]
    )
    return "\n".join(lines)


def _report_md(report, generated_files: dict[str, str], control_snapshot: dict[str, object]) -> str:
    readiness = report.metrics["readiness"]
    proxy = report.metrics["proxy"]
    mitigation = report.metrics["mitigation_budget"]
    lines = [
        "# Agent 41 基质冲击快代理与延迟感知控制报告",
        "",
        f"- summary: {report.summary}",
        f"- fast_proxy_status: `{readiness['fast_proxy_status']}`",
        f"- proxy_score: `{proxy['proxy_score']}`",
        f"- protective_action_margin_min: `{mitigation['protective_action_margin_min']}`",
        f"- adapted_release_policy: `{control_snapshot['adapted_release_policy']}`",
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


def _serializable_scenario_reports(scenario_reports: dict[str, dict[str, object]]) -> dict[str, dict[str, object]]:
    return {
        scenario: {
            "summary": str(item["summary"]),
            "proxy": item["proxy"],
            "mitigation_budget": item["mitigation_budget"],
            "readiness": item["readiness"],
        }
        for scenario, item in scenario_reports.items()
    }


def _read_conformal_readiness() -> dict[str, object]:
    if not AGENT39_METRICS.exists():
        return {}
    payload = _read_json(AGENT39_METRICS)
    readiness = payload.get("readiness", {})
    return readiness if isinstance(readiness, dict) else {}


def _read_json(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _update_manifest(generated_files: dict[str, str]) -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    relative_generated = {
        key: str(Path(path).relative_to(PROJECT_ROOT))
        for key, path in generated_files.items()
    }
    manifest["status"] = "基质冲击快代理与延迟感知控制层已生成"
    manifest["matrix_shock_fast_proxy_control"] = relative_generated
    manifest["next_stage"] = "用 timestamped campaign replay 验证 matrix_shock 快代理 precision/recall，并校准误触发成本后再写入保护性控制"
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()

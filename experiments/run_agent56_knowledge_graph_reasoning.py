from __future__ import annotations

import json
from pathlib import Path

from water_ai.agents.control_strategy_agent import ControlStrategyAgent
from water_ai.agents.data_quality_agent import DataQualityAgent
from water_ai.agents.fault_diagnosis_agent import FaultDiagnosisAgent
from water_ai.agents.knowledge_graph_reasoning_agent import KnowledgeGraphReasoningAgent
from water_ai.agents.mechanism_agent import MechanismAgent
from water_ai.agents.soft_sensor_agent import SoftSensorAgent
from water_ai.simulation import generate_low_cost_sensor_stream


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = PROJECT_ROOT / "deliverables" / "manifest.json"
OUT_DIR = PROJECT_ROOT / "outputs" / "agent56_knowledge_graph_reasoning"
METRICS_DIR = PROJECT_ROOT / "outputs" / "knowledge_graph_reasoning"
DELIVERABLES_DIR = PROJECT_ROOT / "deliverables"
MODEL_CORE_DIR = DELIVERABLES_DIR / "model_core_optimization"
METRICS_PATH = METRICS_DIR / "kg_reasoning_metrics.json"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    DELIVERABLES_DIR.mkdir(parents=True, exist_ok=True)
    MODEL_CORE_DIR.mkdir(parents=True, exist_ok=True)

    readings = generate_low_cost_sensor_stream(n=72, seed=7, inject_faults=True)
    dq_report = DataQualityAgent().run(readings)
    soft_report = SoftSensorAgent(data_quality_report=dq_report).run(readings)
    mechanism_report = MechanismAgent(data_quality_report=dq_report, soft_sensor_report=soft_report).run(readings)
    fault_report = FaultDiagnosisAgent(
        data_quality_report=dq_report,
        soft_sensor_report=soft_report,
        mechanism_report=mechanism_report,
    ).run(readings)
    control_report = ControlStrategyAgent(soft_sensor_report=soft_report, fault_report=fault_report).run(readings)

    state = soft_report.metrics.get("state_estimate", {})
    state = state if isinstance(state, dict) else {}
    report = KnowledgeGraphReasoningAgent(
        state_estimate={str(k): float(v) for k, v in state.items() if isinstance(v, int | float)},
        dq_issue_types={issue.issue_type for issue in dq_report.issues},
        soft_issue_types={issue.issue_type for issue in soft_report.issues},
    ).run([])

    main_chain_coupling = {
        "mechanism_consumes_kg_reasoning": bool(mechanism_report.metrics.get("kg_reasoning", {}).get("evidence_paths")),
        "fault_passes_kg_reasoning": bool(fault_report.metrics.get("kg_reasoning", {}).get("action_constraint_patch")),
        "control_uses_typed_kg_constraints": control_report.metrics.get("knowledge_reasoning_source")
        == "typed_kg_action_constraint_patch",
        "control_action_biases": control_report.metrics.get("knowledge_action_biases", {}),
        "top_control_action": control_report.metrics["ranked_actions"][0]["action_id"],
    }
    metrics_payload = {
        "method_contract": report.metrics["method_contract"],
        "kg_graph_summary": report.metrics["kg_graph"]["summary"],
        "kg_reasoning": report.metrics["kg_reasoning"],
        "agent_chain_retrospective": report.metrics["agent_chain_retrospective"],
        "action_constraint_patch": report.metrics["action_constraint_patch"],
        "mechanism_evidence_paths": report.metrics["mechanism_evidence_paths"],
        "field_validation_queue": report.metrics["field_validation_queue"],
        "main_chain_coupling": main_chain_coupling,
        "readiness": report.metrics["readiness"],
        "agent50_writeback": report.metrics["agent50_writeback"],
    }
    METRICS_PATH.write_text(json.dumps(metrics_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    generated_files = {
        "knowledge_graph_reasoning": str(DELIVERABLES_DIR / "knowledge_graph_reasoning.md"),
        "agent_chain_retrospective": str(MODEL_CORE_DIR / "agent_chain_retrospective.md"),
        "agent56_report": str(OUT_DIR / "agent56_report.md"),
        "kg_reasoning_metrics": str(METRICS_PATH),
    }
    (DELIVERABLES_DIR / "knowledge_graph_reasoning.md").write_text(
        _deliverable_md(report, main_chain_coupling),
        encoding="utf-8",
    )
    (MODEL_CORE_DIR / "agent_chain_retrospective.md").write_text(
        _retrospective_md(report),
        encoding="utf-8",
    )
    (OUT_DIR / "agent56_report.md").write_text(
        _report_md(report, generated_files, main_chain_coupling),
        encoding="utf-8",
    )
    (OUT_DIR / "agent56_report.json").write_text(
        json.dumps(
            {
                "knowledge_graph_reasoning": _report_payload(report),
                "main_chain_coupling": main_chain_coupling,
                "generated_files": generated_files,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    _update_manifest(generated_files, report)

    print(report.summary)
    for rec in report.recommendations:
        print(f"- {rec}")
    for key, path in generated_files.items():
        print(f"{key}: {path}")


def _deliverable_md(report, main_chain_coupling: dict[str, object]) -> str:
    readiness = report.metrics["readiness"]
    graph_summary = report.metrics["kg_graph"]["summary"]
    reasoning = report.metrics["kg_reasoning"]
    lines = [
        "# 可推理知识图谱与主链回接",
        "",
        f"- kg_reasoning_status：`{readiness['kg_reasoning_status']}`",
        f"- node_count：`{graph_summary['node_count']}`",
        f"- edge_count：`{graph_summary['edge_count']}`",
        f"- evidence_traceability：`{readiness['evidence_traceability']}`",
        f"- constraint_hit_rate：`{readiness['constraint_hit_rate']}`",
        f"- field_supported_edge_ratio：`{readiness['field_supported_edge_ratio']}`",
        f"- can_write_to_actuator：`{readiness['can_write_to_actuator']}`",
        f"- can_write_to_release_gate：`{readiness['can_write_to_release_gate']}`",
        "",
        "## 主链耦合状态",
        "",
    ]
    for key, value in main_chain_coupling.items():
        lines.append(f"- {key}：`{value}`")
    lines.extend(
        [
            "",
            "## Action Constraint Patch",
            "",
            "| Action | Direction | Bias | Evidence Paths | Boundary |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for row in reasoning["action_constraint_patch"]:
        lines.append(
            f"| `{row['action_id']}` | `{row['direction']}` | `{row['bias_score']}` | "
            f"`{row['evidence_paths']}` | `{row['writeback_boundary']}` |"
        )
    lines.extend(["", "## 结论边界", ""])
    for issue in report.issues:
        lines.append(f"- `{issue.issue_type}`：{issue.message}")
    return "\n".join(lines)


def _retrospective_md(report) -> str:
    lines = [
        "# Agent 链条复盘与承接顺序",
        "",
        "本复盘不服务展示层，目标是找出前面 agent 在全局视角下的联动缺口，并按边际价值决定下一步模型核心修改。",
        "",
        "| Rank | Gap | Affected Agents | Current Status | Next Carryover |",
        "| --- | --- | --- | --- | --- |",
    ]
    for gap in report.metrics["agent_chain_retrospective"]:
        lines.append(
            f"| `{gap['rank']}` | `{gap['gap_id']}` | `{', '.join(gap['affected_agents'])}` | "
            f"`{gap['after_agent56_status']}` | {gap['next_carryover']} |"
        )
    lines.extend(
        [
            "",
            "## 根基判断",
            "",
            "最高边际价值的问题是 `G0_flat_knowledge_not_coupled_to_decisions`：知识库若不能成为 typed evidence path，后续机理、故障、控制和工程仲裁就只能共享松散文本。Agent56 已把它改成可被 Agent3/4/5 消费的 KG reasoning patch。",
            "",
            "下一步不应回到 PPT/Word，而应处理 `G1_parallel_core_agents_not_fully_reconnected`：把 Agent53 灰箱 prior、Agent54 layout/missingness 合同、Agent55 engineering patch 继续接回主闭环链条。",
        ]
    )
    return "\n".join(lines)


def _report_md(report, generated_files: dict[str, str], main_chain_coupling: dict[str, object]) -> str:
    readiness = report.metrics["readiness"]
    lines = [
        "# Agent 56 可推理知识图谱报告",
        "",
        f"- summary: {report.summary}",
        f"- kg_reasoning_status: `{readiness['kg_reasoning_status']}`",
        f"- evidence_path_count: `{readiness['evidence_path_count']}`",
        f"- action_constraint_count: `{readiness['action_constraint_count']}`",
        f"- claim_verification_pass_rate: `{readiness['claim_verification_pass_rate']}`",
        "",
        "## 生成文件",
        "",
    ]
    for key, path in generated_files.items():
        lines.append(f"- {key}: `{path}`")
    lines.extend(["", "## 主链回接", ""])
    for key, value in main_chain_coupling.items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(["", "## 风险边界", ""])
    for issue in report.issues:
        lines.append(f"- `{issue.issue_type}`：{issue.message}")
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


def _update_manifest(generated_files: dict[str, str], report) -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    manifest["status"] = "可推理 KG reasoning 与 agent 链条复盘已生成"
    manifest["knowledge_graph_reasoning"] = {
        key: str(Path(path).relative_to(PROJECT_ROOT))
        for key, path in generated_files.items()
    }
    manifest["next_stage"] = (
        "Agent56 已把 P6 从 KG 策展推进到 typed evidence paths 与 action constraint patch；"
        "下一轮优先处理 G1/P8：把 Agent53 灰箱 prior、Agent54 layout/missingness 合同和 Agent55 engineering patch 继续接回主闭环链条，"
        "同时等待 field-supported KG edges。"
    )
    manifest["latest_kg_reasoning_status"] = report.metrics["readiness"]["kg_reasoning_status"]
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()

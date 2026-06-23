from __future__ import annotations

import json
from pathlib import Path

from water_ai.agents.arbitration_agent import ArbitrationAgent
from water_ai.agents.control_strategy_agent import ControlStrategyAgent
from water_ai.agents.cost_safety_agent import CostSafetyAgent
from water_ai.agents.data_quality_agent import DataQualityAgent
from water_ai.agents.engineering_execution_constraint_agent import EngineeringExecutionConstraintAgent
from water_ai.agents.fault_diagnosis_agent import FaultDiagnosisAgent
from water_ai.agents.main_chain_reconnection_agent import MainChainReconnectionAgent
from water_ai.agents.mechanism_agent import MechanismAgent
from water_ai.agents.multi_facility_collaborative_control_agent import MultiFacilityCollaborativeControlAgent
from water_ai.agents.soft_sensor_agent import SoftSensorAgent
from water_ai.process_dynamics import generate_sensor_stream_from_process_state, initial_process_state


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = PROJECT_ROOT / "deliverables" / "manifest.json"
SPARSE_METRICS_PATH = PROJECT_ROOT / "outputs" / "sensor_network_sparse_placement" / "sparse_placement_metrics.json"
COLLAB_METRICS_PATH = PROJECT_ROOT / "outputs" / "multi_facility_collaborative_control" / "collaborative_control_metrics.json"
KG_METRICS_PATH = PROJECT_ROOT / "outputs" / "knowledge_graph_reasoning" / "kg_reasoning_metrics.json"
GREY_BOX_METRICS_PATH = PROJECT_ROOT / "outputs" / "minimal_grey_box_physics" / "grey_box_physics_metrics.json"
SOFT_MATRIX_METRICS_PATH = PROJECT_ROOT / "outputs" / "soft_sensor_matrix_coupling" / "soft_sensor_matrix_metrics.json"
ENGINEERING_METRICS_PATH = PROJECT_ROOT / "outputs" / "engineering_execution_constraints" / "engineering_constraints_metrics.json"
OUT_DIR = PROJECT_ROOT / "outputs" / "agent57_main_chain_reconnection"
METRICS_DIR = PROJECT_ROOT / "outputs" / "main_chain_reconnection"
DELIVERABLES_DIR = PROJECT_ROOT / "deliverables"
METRICS_PATH = METRICS_DIR / "main_chain_reconnection_metrics.json"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    DELIVERABLES_DIR.mkdir(parents=True, exist_ok=True)

    sparse_metrics = _read_optional_json(SPARSE_METRICS_PATH)
    kg_metrics = _read_optional_json(KG_METRICS_PATH)
    grey_box_metrics = _read_optional_json(GREY_BOX_METRICS_PATH)
    soft_matrix_metrics = _read_optional_json(SOFT_MATRIX_METRICS_PATH)
    engineering_metrics = _read_optional_json(ENGINEERING_METRICS_PATH)
    collab_metrics = _read_optional_json(COLLAB_METRICS_PATH)
    interface = sparse_metrics.get("soft_sensor_interface", {}) if isinstance(sparse_metrics, dict) else {}
    collab_report = MultiFacilityCollaborativeControlAgent(
        sparse_placement_metrics=sparse_metrics,
        engineering_constraints_metrics=engineering_metrics,
    ).run([])
    collab_metrics = collab_report.metrics

    readings = generate_sensor_stream_from_process_state(initial_process_state("matrix_shock"), n=72, seed=57)
    dq_report = DataQualityAgent().run(readings)
    soft_report = SoftSensorAgent(
        data_quality_report=dq_report,
        sensor_layout_interface=interface if isinstance(interface, dict) else {},
        grey_box_physics_metrics=grey_box_metrics,
    ).run(readings)
    mechanism_report = MechanismAgent(data_quality_report=dq_report, soft_sensor_report=soft_report).run(readings)
    fault_report = FaultDiagnosisAgent(
        data_quality_report=dq_report,
        soft_sensor_report=soft_report,
        mechanism_report=mechanism_report,
    ).run(readings)
    control_report = ControlStrategyAgent(soft_sensor_report=soft_report, fault_report=fault_report).run(readings)
    engineering_report = EngineeringExecutionConstraintAgent(
        collaborative_control_metrics=collab_metrics if collab_metrics else {},
        data_origin=engineering_metrics.get("readiness", {}).get("engineering_constraints_status", "synthetic_engineering_contract")
        if isinstance(engineering_metrics.get("readiness", {}), dict)
        else "synthetic_engineering_contract",
    ).run([])
    cost_report = CostSafetyAgent(
        control_report=control_report,
        engineering_constraints_report=engineering_report,
        collaborative_control_report=collab_report,
    ).run(readings)
    arbitration_report = ArbitrationAgent(
        soft_sensor_report=soft_report,
        control_report=control_report,
        cost_safety_report=cost_report,
        engineering_constraints_report=engineering_report,
    ).run(readings)

    report = MainChainReconnectionAgent(
        soft_sensor_report=soft_report,
        mechanism_report=mechanism_report,
        fault_report=fault_report,
        control_report=control_report,
        cost_safety_report=cost_report,
        arbitration_report=arbitration_report,
        kg_reasoning_metrics=kg_metrics,
        multi_facility_control_metrics=collab_metrics,
        grey_box_physics_metrics=grey_box_metrics,
        soft_sensor_matrix_metrics=soft_matrix_metrics,
        engineering_constraints_metrics=engineering_metrics,
    ).run([])

    metrics_payload = {
        "method_contract": report.metrics["method_contract"],
        "coupling_table": report.metrics["coupling_table"],
        "readiness": report.metrics["readiness"],
        "agent50_writeback": report.metrics["agent50_writeback"],
        "main_chain_snapshots": {
            "soft_sensor": {
                "layout_context": soft_report.metrics.get("layout_context", {}),
                "grey_box_prior_context": soft_report.metrics.get("grey_box_prior_context", {}),
            },
            "control": {
                "knowledge_reasoning_source": control_report.metrics.get("knowledge_reasoning_source"),
                "knowledge_action_biases": control_report.metrics.get("knowledge_action_biases", {}),
            },
            "arbitration": {
                "engineering_constraints_used": arbitration_report.metrics.get("engineering_constraints_used", {}),
                "blocked_actions": arbitration_report.metrics.get("blocked_actions", []),
            },
        },
    }
    METRICS_PATH.write_text(json.dumps(metrics_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    generated_files = {
        "main_chain_reconnection": str(DELIVERABLES_DIR / "main_chain_reconnection.md"),
        "agent57_report": str(OUT_DIR / "agent57_report.md"),
        "main_chain_reconnection_metrics": str(METRICS_PATH),
    }
    (DELIVERABLES_DIR / "main_chain_reconnection.md").write_text(
        _deliverable_md(report),
        encoding="utf-8",
    )
    (OUT_DIR / "agent57_report.md").write_text(
        _report_md(report, generated_files),
        encoding="utf-8",
    )
    (OUT_DIR / "agent57_report.json").write_text(
        json.dumps(
            {
                "main_chain_reconnection": _report_payload(report),
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


def _read_optional_json(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _deliverable_md(report) -> str:
    readiness = report.metrics["readiness"]
    lines = [
        "# 主闭环链条回接审计",
        "",
        f"- main_chain_reconnection_status：`{readiness['main_chain_reconnection_status']}`",
        f"- main_chain_prior_consumption_rate：`{readiness['main_chain_prior_consumption_rate']}`",
        f"- consumed_link_count：`{readiness['consumed_link_count']}` / `{readiness['total_link_count']}`",
        f"- critical_links_ready：`{readiness['critical_links_ready']}`",
        f"- can_write_to_actuator：`{readiness['can_write_to_actuator']}`",
        f"- can_write_to_release_gate：`{readiness['can_write_to_release_gate']}`",
        "",
        "## Coupling Table",
        "",
        "| Link | Source -> Target | Consumed | Evidence | Boundary |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in report.metrics["coupling_table"]:
        lines.append(
            f"| `{row['link_id']}` | `{row['source_agent']} -> {row['target_agent']}` | "
            f"`{row['consumed']}` | `{row['evidence']}` | {row['writeback_boundary']} |"
        )
    lines.extend(["", "## 结论边界", ""])
    for issue in report.issues:
        lines.append(f"- `{issue.issue_type}`：{issue.message}")
    return "\n".join(lines)


def _report_md(report, generated_files: dict[str, str]) -> str:
    readiness = report.metrics["readiness"]
    lines = [
        "# Agent 57 主链回接报告",
        "",
        f"- summary: {report.summary}",
        f"- main_chain_reconnection_status: `{readiness['main_chain_reconnection_status']}`",
        f"- main_chain_prior_consumption_rate: `{readiness['main_chain_prior_consumption_rate']}`",
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
    manifest["status"] = "主闭环核心 prior 回接审计已生成"
    manifest["main_chain_reconnection"] = {
        key: str(Path(path).relative_to(PROJECT_ROOT))
        for key, path in generated_files.items()
    }
    manifest["latest_main_chain_reconnection_status"] = report.metrics["readiness"]["main_chain_reconnection_status"]
    manifest["next_stage"] = (
        "Agent57 已把 P8 从复盘结论推进到主链回接审计；下一轮优先对齐 field_validation_queue，"
        "并继续检查 Agent49 多设施协同是否应成为 Arbitration 的可消费动作池，而不是只作为并行控制候选。"
    )
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()

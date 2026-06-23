from __future__ import annotations

import json
from pathlib import Path

from water_ai.agents.deliverable_organization_agent import DeliverableOrganizationAgent


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = PROJECT_ROOT / "deliverables" / "manifest.json"
AGENT29_REPORT = PROJECT_ROOT / "outputs" / "agent29_project_synthesis" / "agent29_report.json"
AGENT30_REPORT = PROJECT_ROOT / "outputs" / "agent30_field_data_interface" / "agent30_report.json"
OUT_DIR = PROJECT_ROOT / "outputs" / "agent31_deliverable_organization"
DELIVERABLES_DIR = PROJECT_ROOT / "deliverables"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DELIVERABLES_DIR.mkdir(parents=True, exist_ok=True)
    manifest = _read_json(MANIFEST_PATH)
    agent29 = _read_json(AGENT29_REPORT)
    agent30 = _read_json(AGENT30_REPORT)
    project_metrics = agent29["project_synthesis"]["metrics"]
    field_metrics = agent30["field_data_interface"]["metrics"]
    artifact_existence = _artifact_existence(manifest)

    report = DeliverableOrganizationAgent(
        manifest=manifest,
        project_synthesis_metrics=project_metrics,
        field_data_metrics=field_metrics,
        artifact_existence=artifact_existence,
        latest_regression=str(manifest.get("latest_regression", "133 passed")),
    ).run([])

    generated_files = {
        "executive_brief": str(DELIVERABLES_DIR / "executive_brief.md"),
        "presentation_outline": str(DELIVERABLES_DIR / "presentation_outline.md"),
        "key_metrics_table": str(DELIVERABLES_DIR / "key_metrics_table.md"),
        "artifact_index": str(DELIVERABLES_DIR / "artifact_index.md"),
        "calibration_task_board": str(DELIVERABLES_DIR / "calibration_task_board.md"),
    }
    (DELIVERABLES_DIR / "executive_brief.md").write_text(_executive_brief_md(report), encoding="utf-8")
    (DELIVERABLES_DIR / "presentation_outline.md").write_text(_presentation_outline_md(report), encoding="utf-8")
    (DELIVERABLES_DIR / "key_metrics_table.md").write_text(_key_metrics_table_md(report), encoding="utf-8")
    (DELIVERABLES_DIR / "artifact_index.md").write_text(_artifact_index_md(report), encoding="utf-8")
    (DELIVERABLES_DIR / "calibration_task_board.md").write_text(_calibration_task_board_md(report), encoding="utf-8")

    payload = {
        "source_manifest": str(MANIFEST_PATH),
        "source_reports": {
            "agent29": str(AGENT29_REPORT),
            "agent30": str(AGENT30_REPORT),
        },
        "deliverable_organization": {
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
    (OUT_DIR / "agent31_report.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT_DIR / "agent31_report.md").write_text(_report_md(report, generated_files), encoding="utf-8")

    _update_manifest(manifest, generated_files)

    print(report.summary)
    for rec in report.recommendations:
        print(f"- {rec}")
    print(f"wrote {OUT_DIR / 'agent31_report.md'}")
    for path in generated_files.values():
        print(f"wrote {path}")


def _read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _artifact_existence(manifest: dict[str, object]) -> dict[str, bool]:
    paths: list[str] = []
    for key in ("core_documents", "key_reports"):
        values = manifest.get(key, [])
        if isinstance(values, list):
            paths.extend(str(value) for value in values)
    field_data = manifest.get("field_data_interface", {})
    if isinstance(field_data, dict):
        paths.extend(str(value) for value in field_data.values())
    organization_outputs = manifest.get("organization_outputs", {})
    if isinstance(organization_outputs, dict):
        paths.extend(str(value) for value in organization_outputs.values())
    presentation_assets = manifest.get("presentation_assets", {})
    if isinstance(presentation_assets, dict):
        paths.extend(str(value) for value in presentation_assets.values())
    formal_deck = manifest.get("formal_deck", {})
    if isinstance(formal_deck, dict):
        paths.extend(str(value) for value in formal_deck.values())
    field_calibration_gate = manifest.get("field_calibration_gate", {})
    if isinstance(field_calibration_gate, dict):
        paths.extend(str(value) for value in field_calibration_gate.values())
    model_realism_audit = manifest.get("model_realism_audit", {})
    if isinstance(model_realism_audit, dict):
        paths.extend(str(value) for value in model_realism_audit.values())
    soft_sensor_uncertainty = manifest.get("soft_sensor_uncertainty", {})
    if isinstance(soft_sensor_uncertainty, dict):
        paths.extend(str(value) for value in soft_sensor_uncertainty.values())
    knowledge_graph_curation = manifest.get("knowledge_graph_curation", {})
    if isinstance(knowledge_graph_curation, dict):
        paths.extend(str(value) for value in knowledge_graph_curation.values())
    literature_evidence = manifest.get("literature_evidence", {})
    if isinstance(literature_evidence, dict):
        paths.extend(str(value) for value in literature_evidence.values())
    soft_sensor_conformal_calibration = manifest.get("soft_sensor_conformal_calibration", {})
    if isinstance(soft_sensor_conformal_calibration, dict):
        paths.extend(str(value) for value in soft_sensor_conformal_calibration.values())
    soft_sensor_field_holdout_gate = manifest.get("soft_sensor_field_holdout_gate", {})
    if isinstance(soft_sensor_field_holdout_gate, dict):
        paths.extend(str(value) for value in soft_sensor_field_holdout_gate.values())
    weak_target_stratified_conformal = manifest.get("weak_target_stratified_conformal", {})
    if isinstance(weak_target_stratified_conformal, dict):
        paths.extend(str(value) for value in weak_target_stratified_conformal.values())
    sensor_network_sparse_placement = manifest.get("sensor_network_sparse_placement", {})
    if isinstance(sensor_network_sparse_placement, dict):
        paths.extend(str(value) for value in sensor_network_sparse_placement.values())
    multi_facility_collaborative_control = manifest.get("multi_facility_collaborative_control", {})
    if isinstance(multi_facility_collaborative_control, dict):
        paths.extend(str(value) for value in multi_facility_collaborative_control.values())
    model_core_optimization_governance = manifest.get("model_core_optimization_governance", {})
    if isinstance(model_core_optimization_governance, dict):
        paths.extend(str(value) for value in model_core_optimization_governance.values())
    catalyst_activity_proxy = manifest.get("catalyst_activity_proxy", {})
    if isinstance(catalyst_activity_proxy, dict):
        paths.extend(str(value) for value in catalyst_activity_proxy.values())
    multi_facility_replay_evaluation = manifest.get("multi_facility_replay_evaluation", {})
    if isinstance(multi_facility_replay_evaluation, dict):
        paths.extend(str(value) for value in multi_facility_replay_evaluation.values())
    minimal_grey_box_physics = manifest.get("minimal_grey_box_physics", {})
    if isinstance(minimal_grey_box_physics, dict):
        paths.extend(str(value) for value in minimal_grey_box_physics.values())
    soft_sensor_matrix_coupling = manifest.get("soft_sensor_matrix_coupling", {})
    if isinstance(soft_sensor_matrix_coupling, dict):
        paths.extend(str(value) for value in soft_sensor_matrix_coupling.values())
    grey_box_dynamic_latency = manifest.get("grey_box_dynamic_latency", {})
    if isinstance(grey_box_dynamic_latency, dict):
        paths.extend(str(value) for value in grey_box_dynamic_latency.values())
    matrix_shock_fast_proxy = manifest.get("matrix_shock_fast_proxy_control", {})
    if isinstance(matrix_shock_fast_proxy, dict):
        paths.extend(str(value) for value in matrix_shock_fast_proxy.values())
    timestamped_campaign_replay = manifest.get("timestamped_campaign_replay", {})
    if isinstance(timestamped_campaign_replay, dict):
        paths.extend(str(value) for value in timestamped_campaign_replay.values())
    field_replay_calibration_gate = manifest.get("field_replay_calibration_gate", {})
    if isinstance(field_replay_calibration_gate, dict):
        paths.extend(str(value) for value in field_replay_calibration_gate.values())
    field_replay_import = manifest.get("field_replay_import", {})
    if isinstance(field_replay_import, dict):
        paths.extend(str(value) for value in field_replay_import.values())
    field_replay_evidence_chain = manifest.get("field_replay_evidence_chain", {})
    if isinstance(field_replay_evidence_chain, dict):
        paths.extend(str(value) for value in field_replay_evidence_chain.values())
    return {path: (PROJECT_ROOT / path.rstrip("/")).exists() for path in paths}


def _executive_brief_md(report) -> str:
    lines = ["# 执行摘要", ""]
    for item in report.metrics["executive_summary"]:
        lines.append(f"- {item}")
    lines.extend(["", "## 汇报口径", ""])
    for rec in report.recommendations:
        lines.append(f"- {rec}")
    return "\n".join(lines)


def _presentation_outline_md(report) -> str:
    lines = ["# 汇报 / PPT 提纲", ""]
    for section in report.metrics["presentation_outline"]:
        lines.extend(
            [
                f"## {section['section_id']} {section['title']}",
                "",
                f"- 核心信息：{section['message']}",
                f"- 可用证据：{', '.join(str(item) for item in section['evidence'])}",
                "",
            ]
        )
    return "\n".join(lines)


def _key_metrics_table_md(report) -> str:
    lines = ["# 关键数值表", "", "| 指标 | 数值 | 汇报解释 |", "| --- | --- | --- |"]
    for row in report.metrics["key_metrics_table"]:
        lines.append(f"| `{row['metric']}` | `{row['value']}` | {row['interpretation']} |")
    return "\n".join(lines)


def _artifact_index_md(report) -> str:
    lines = ["# 成果索引", "", "| 类别 | 文件 | 状态 | 作用 |", "| --- | --- | --- | --- |"]
    for item in report.metrics["artifact_index"]:
        status = "存在" if item["exists"] else "缺失"
        lines.append(f"| {item['category']} | `{item['path']}` | {status} | {item['role']} |")
    return "\n".join(lines)


def _calibration_task_board_md(report) -> str:
    lines = ["# 实证校准任务板", "", "| 任务 | 状态 | 下一步 | 阻塞项 |", "| --- | --- | --- | --- |"]
    for task in report.metrics["calibration_task_board"]:
        lines.append(
            f"| `{task['task_id']}` {task['title']} | `{task['current_status']}` | "
            f"{task['next_action']} | {task['blockers']} |"
        )
    return "\n".join(lines)


def _report_md(report, generated_files: dict[str, str]) -> str:
    readiness = report.metrics["readiness"]
    lines = [
        "# Agent 31 成果整理与汇报素材报告",
        "",
        f"- summary: {report.summary}",
        f"- deliverable_status: `{readiness['deliverable_status']}`",
        f"- deliverable_score: `{readiness['deliverable_score']}`",
        f"- available_artifacts: `{readiness['available_artifact_count']}/{readiness['total_artifact_count']}`",
        "",
        "## 生成文件",
        "",
    ]
    for key, path in generated_files.items():
        lines.append(f"- {key}: `{path}`")
    lines.extend(["", "## 执行摘要", ""])
    for item in report.metrics["executive_summary"]:
        lines.append(f"- {item}")
    lines.extend(["", "## 风险边界", ""])
    for issue in report.issues:
        lines.append(f"- `{issue.issue_type}`：{issue.message}")
    return "\n".join(lines)


def _update_manifest(manifest: dict[str, object], generated_files: dict[str, str]) -> None:
    relative_generated = {
        key: str(Path(path).relative_to(PROJECT_ROOT))
        for key, path in generated_files.items()
    }
    manifest["organization_outputs"] = relative_generated
    if manifest.get("latest_global_system_spine_status"):
        MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        return
    if manifest.get("soft_sensor_matrix_coupling"):
        manifest["status"] = "软传感矩阵耦合层已生成"
        manifest["next_stage"] = "Agent54 已形成 P5 软传感 node-modality/missingness synthetic contract；Agent50 已将下一轮模型核心候选推进到 P7 工程执行约束进入 reward 和仲裁，同时等待 field missingness/layout holdout"
    elif manifest.get("minimal_grey_box_physics"):
        manifest["status"] = "最小灰箱物理机制层已生成"
        manifest["next_stage"] = "Agent53 已形成 P4 最小灰箱物理 synthetic prior；Agent50 下一轮应转向 P5 软传感 node-modality/missingness 耦合，同时等待 field 物理校准"
    elif manifest.get("multi_facility_replay_evaluation"):
        manifest["status"] = "多设施 replay 离线评估层已生成"
        manifest["next_stage"] = "Agent52 已形成 Agent49 replay-ready synthetic baseline；Agent50 已将下一轮模型核心候选推进到 P4 灰箱物理机制或 P5 软传感矩阵耦合；若补入真实多节点 replay，再回到 P3 校准 Agent49"
    elif manifest.get("catalyst_activity_proxy"):
        manifest["status"] = "催化剂活性代理观测层已生成"
        manifest["next_stage"] = "Agent51 已形成 catalyst_activity synthetic proxy design；Agent50 已将最高边际价值任务切换为 P3 Agent49 replay-ready 离线评估；若补入 field_proxy_holdout，再回到 P2 校准代理"
    elif manifest.get("model_core_optimization_governance"):
        manifest["status"] = "模型核心优化治理层已生成"
        manifest["next_stage"] = "按低摩擦阶段边界运行 Agent50 自我打断评估；Agent48 可比较布点 synthetic 基线已形成，当前优先推进 catalyst_activity 弱观测代理和 Agent49 replay-ready 离线评估"
    elif manifest.get("multi_facility_collaborative_control"):
        manifest["status"] = "多设施协同控制层已生成"
        manifest["next_stage"] = "以 Agent48 稀疏观测矩阵为状态入口，采集真实多节点 sensor/lab/operation/action replay，重跑 Agent49 校准 joint_action_accuracy、reward_regret 和决策树蒸馏准确度"
    elif manifest.get("sensor_network_sparse_placement"):
        manifest["status"] = "管网布点与稀疏感知层已生成"
        manifest["next_stage"] = "用真实管网/处理单元拓扑、水力停留时间、维护可达性和节点级 field labels 替换 synthetic topology prior，重跑 Agent48 后再更新软传感 field holdout 设计"
    elif manifest.get("weak_target_stratified_conformal"):
        manifest["status"] = "弱目标分层保形校准层已生成"
        manifest["next_stage"] = "采集真实 field holdout，重跑 Agent36/Agent39/Agent47/Agent46；先修复弱目标分层 coverage，再由 Agent46 形成 release gate 校准候选"
    elif manifest.get("soft_sensor_field_holdout_gate"):
        manifest["status"] = "软传感 field holdout 放行门控已生成"
        manifest["next_stage"] = "采集真实 field holdout，重跑 Agent36/Agent39/Agent46；只有 Agent46 全门控通过后才形成软传感 release gate 校准候选"
    elif manifest.get("field_replay_evidence_chain"):
        manifest["status"] = "field replay evidence chain 已生成"
        manifest["next_stage"] = "导入真实 field replay 包，通过 Agent44->Agent42->Agent43->Agent45 证据链后形成保护性写回候选"
    elif manifest.get("field_replay_import"):
        manifest["status"] = "field replay import gate 已生成"
        manifest["next_stage"] = "导入真实 field metadata 与 CSV replay 包，通过 Agent44 后再进入 Agent42/Agent43 G6/P6"
    elif manifest.get("field_replay_calibration_gate"):
        manifest["status"] = "field replay calibration gate 已生成"
        manifest["next_stage"] = "导入真实 field-labeled timestamped replay，通过 G6/P6 后再把 matrix_shock 快代理写入保护性控制"
    elif manifest.get("timestamped_campaign_replay"):
        manifest["status"] = "timestamped campaign replay 接口已生成"
        manifest["next_stage"] = "采集真实 timestamped campaign replay，验证 matrix_shock 快代理 precision/recall、提前量和误触发成本"
    elif manifest.get("matrix_shock_fast_proxy_control"):
        manifest["status"] = "基质冲击快代理与延迟感知控制层已生成"
        manifest["next_stage"] = "用 timestamped campaign replay 验证 matrix_shock 快代理 precision/recall，并校准误触发成本后再写入保护性控制"
    elif manifest.get("grey_box_dynamic_latency"):
        manifest["status"] = "灰箱动态延迟审计层已生成"
        manifest["next_stage"] = "采集现场 timestamped campaign replay，校准采样/检测/执行器/回流延迟后再接入 release gate"
    elif manifest.get("soft_sensor_conformal_calibration"):
        manifest["status"] = "软传感保形校准接口已生成"
        manifest["next_stage"] = "用真实 field holdout 重算 conformal thresholds，并接入 release gate 前完成 G0-G5 验收"
    elif manifest.get("literature_evidence"):
        manifest["status"] = "文献证据抽取层已生成"
        manifest["next_stage"] = "按 literature_evidence_matrix.md 推进软传感 field conformal calibration、灰箱动态控制延迟和 field-supported KG edges"
    elif manifest.get("knowledge_graph_curation"):
        manifest["status"] = "知识图谱策展层已生成"
        manifest["next_stage"] = "按 knowledge_graph_curation.md 补文献证据抽取、原始信号边和真实 field-supported KG edges"
    elif manifest.get("soft_sensor_uncertainty"):
        manifest["status"] = "软传感不确定性层已生成"
        manifest["next_stage"] = "用真实 field holdout 校准软传感预测区间，并继续扩展知识图谱证据矩阵"
    elif manifest.get("model_realism_audit"):
        manifest["status"] = "模型真实性审计已生成"
        manifest["next_stage"] = "优先按 model_upgrade_backlog.md 补充真实数据验收、软传感不确定性层和知识图谱证据矩阵"
    elif manifest.get("field_calibration_gate"):
        manifest["status"] = "实证校准入口门控已生成"
        manifest["next_stage"] = "按 field_calibration_runbook.md 导入真实现场数据，并用 field_data_acceptance_gates.md 做采集验收"
    elif manifest.get("formal_deck"):
        manifest["status"] = "整理阶段正式 PPTX 已生成"
        manifest["next_stage"] = "用 deck_qa_checklist.md 对正式 PPTX 做中文字体、边界说明和布局复核，再进入真实现场数据导入与校准"
    else:
        manifest["status"] = "整理阶段成果包已生成"
        manifest["next_stage"] = "基于 presentation_outline.md 和 executive_brief.md 生成正式汇报材料，并接入真实现场数据校准"
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()

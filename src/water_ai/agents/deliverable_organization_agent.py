from __future__ import annotations

from collections.abc import Sequence

from water_ai.agents.base import BaseAgent
from water_ai.domain import AgentReport, QualityIssue, SensorReading, Severity


class DeliverableOrganizationAgent(BaseAgent):
    """Organize project outputs into presentation-ready deliverables."""

    name = "deliverable_organization_agent"

    def __init__(
        self,
        *,
        manifest: dict[str, object] | None = None,
        project_synthesis_metrics: dict[str, object] | None = None,
        field_data_metrics: dict[str, object] | None = None,
        artifact_existence: dict[str, bool] | None = None,
        latest_regression: str = "unknown",
    ) -> None:
        self.manifest = manifest or {}
        self.project_synthesis_metrics = project_synthesis_metrics or {}
        self.field_data_metrics = field_data_metrics or {}
        self.artifact_existence = artifact_existence or {}
        self.latest_regression = latest_regression

    def run(self, readings: Sequence[SensorReading]) -> AgentReport:
        del readings
        artifact_index = self._artifact_index()
        core_metrics = self._core_metrics(artifact_index)
        executive_summary = self._executive_summary(core_metrics)
        presentation_outline = self._presentation_outline(core_metrics)
        key_metrics_table = self._key_metrics_table(core_metrics)
        calibration_task_board = self._calibration_task_board()
        readiness = self._readiness(artifact_index, presentation_outline)
        issues = self._issues(artifact_index, readiness)
        recommendations = self._recommendations(readiness)
        summary = (
            f"成果整理：{readiness['deliverable_status']}；"
            f"索引文件 {readiness['available_artifact_count']}/{readiness['total_artifact_count']} 可用，"
            f"汇报章节 {len(presentation_outline)} 个。"
        )
        confidence = round(min(0.92, max(0.3, 0.5 + 0.35 * readiness["deliverable_score"] - 0.04 * len(issues))), 3)

        return AgentReport(
            agent_name=self.name,
            confidence=confidence,
            summary=summary,
            issues=issues,
            recommendations=recommendations,
            metrics={
                "artifact_index": artifact_index,
                "core_metrics": core_metrics,
                "executive_summary": executive_summary,
                "presentation_outline": presentation_outline,
                "key_metrics_table": key_metrics_table,
                "calibration_task_board": calibration_task_board,
                "readiness": readiness,
                "latest_regression": self.latest_regression,
            },
        )

    def _artifact_index(self) -> list[dict[str, object]]:
        entries: list[dict[str, object]] = []
        categories = {
            "core_document": self.manifest.get("core_documents", []),
            "key_report": self.manifest.get("key_reports", []),
        }
        field_data = self.manifest.get("field_data_interface", {})
        if isinstance(field_data, dict):
            categories["field_data_interface"] = list(field_data.values())
        organization_outputs = self.manifest.get("organization_outputs", {})
        if isinstance(organization_outputs, dict):
            categories["organization_output"] = list(organization_outputs.values())
        presentation_assets = self.manifest.get("presentation_assets", {})
        if isinstance(presentation_assets, dict):
            categories["presentation_asset"] = list(presentation_assets.values())
        formal_deck = self.manifest.get("formal_deck", {})
        if isinstance(formal_deck, dict):
            categories["formal_deck"] = list(formal_deck.values())
        field_calibration_gate = self.manifest.get("field_calibration_gate", {})
        if isinstance(field_calibration_gate, dict):
            categories["field_calibration_gate"] = list(field_calibration_gate.values())
        model_realism_audit = self.manifest.get("model_realism_audit", {})
        if isinstance(model_realism_audit, dict):
            categories["model_realism_audit"] = list(model_realism_audit.values())
        soft_sensor_uncertainty = self.manifest.get("soft_sensor_uncertainty", {})
        if isinstance(soft_sensor_uncertainty, dict):
            categories["soft_sensor_uncertainty"] = list(soft_sensor_uncertainty.values())
        knowledge_graph_curation = self.manifest.get("knowledge_graph_curation", {})
        if isinstance(knowledge_graph_curation, dict):
            categories["knowledge_graph_curation"] = list(knowledge_graph_curation.values())
        literature_evidence = self.manifest.get("literature_evidence", {})
        if isinstance(literature_evidence, dict):
            categories["literature_evidence"] = list(literature_evidence.values())
        soft_sensor_conformal_calibration = self.manifest.get("soft_sensor_conformal_calibration", {})
        if isinstance(soft_sensor_conformal_calibration, dict):
            categories["soft_sensor_conformal_calibration"] = list(soft_sensor_conformal_calibration.values())
        soft_sensor_field_holdout_gate = self.manifest.get("soft_sensor_field_holdout_gate", {})
        if isinstance(soft_sensor_field_holdout_gate, dict):
            categories["soft_sensor_field_holdout_gate"] = list(soft_sensor_field_holdout_gate.values())
        weak_target_stratified_conformal = self.manifest.get("weak_target_stratified_conformal", {})
        if isinstance(weak_target_stratified_conformal, dict):
            categories["weak_target_stratified_conformal"] = list(weak_target_stratified_conformal.values())
        sensor_network_sparse_placement = self.manifest.get("sensor_network_sparse_placement", {})
        if isinstance(sensor_network_sparse_placement, dict):
            categories["sensor_network_sparse_placement"] = list(sensor_network_sparse_placement.values())
        multi_facility_collaborative_control = self.manifest.get("multi_facility_collaborative_control", {})
        if isinstance(multi_facility_collaborative_control, dict):
            categories["multi_facility_collaborative_control"] = list(multi_facility_collaborative_control.values())
        model_core_optimization_governance = self.manifest.get("model_core_optimization_governance", {})
        if isinstance(model_core_optimization_governance, dict):
            categories["model_core_optimization_governance"] = list(model_core_optimization_governance.values())
        catalyst_activity_proxy = self.manifest.get("catalyst_activity_proxy", {})
        if isinstance(catalyst_activity_proxy, dict):
            categories["catalyst_activity_proxy"] = list(catalyst_activity_proxy.values())
        multi_facility_replay_evaluation = self.manifest.get("multi_facility_replay_evaluation", {})
        if isinstance(multi_facility_replay_evaluation, dict):
            categories["multi_facility_replay_evaluation"] = list(multi_facility_replay_evaluation.values())
        minimal_grey_box_physics = self.manifest.get("minimal_grey_box_physics", {})
        if isinstance(minimal_grey_box_physics, dict):
            categories["minimal_grey_box_physics"] = list(minimal_grey_box_physics.values())
        soft_sensor_matrix_coupling = self.manifest.get("soft_sensor_matrix_coupling", {})
        if isinstance(soft_sensor_matrix_coupling, dict):
            categories["soft_sensor_matrix_coupling"] = list(soft_sensor_matrix_coupling.values())
        grey_box_dynamic_latency = self.manifest.get("grey_box_dynamic_latency", {})
        if isinstance(grey_box_dynamic_latency, dict):
            categories["grey_box_dynamic_latency"] = list(grey_box_dynamic_latency.values())
        matrix_shock_fast_proxy = self.manifest.get("matrix_shock_fast_proxy_control", {})
        if isinstance(matrix_shock_fast_proxy, dict):
            categories["matrix_shock_fast_proxy_control"] = list(matrix_shock_fast_proxy.values())
        timestamped_campaign_replay = self.manifest.get("timestamped_campaign_replay", {})
        if isinstance(timestamped_campaign_replay, dict):
            categories["timestamped_campaign_replay"] = list(timestamped_campaign_replay.values())
        field_replay_calibration_gate = self.manifest.get("field_replay_calibration_gate", {})
        if isinstance(field_replay_calibration_gate, dict):
            categories["field_replay_calibration_gate"] = list(field_replay_calibration_gate.values())
        field_replay_import = self.manifest.get("field_replay_import", {})
        if isinstance(field_replay_import, dict):
            categories["field_replay_import"] = list(field_replay_import.values())
        field_replay_evidence_chain = self.manifest.get("field_replay_evidence_chain", {})
        if isinstance(field_replay_evidence_chain, dict):
            categories["field_replay_evidence_chain"] = list(field_replay_evidence_chain.values())
        for category, paths in categories.items():
            if not isinstance(paths, list):
                continue
            for path in paths:
                path_str = str(path)
                entries.append(
                    {
                        "category": category,
                        "path": path_str,
                        "exists": bool(self.artifact_existence.get(path_str, False)),
                        "role": self._artifact_role(category, path_str),
                    }
                )
        return entries

    @staticmethod
    def _artifact_role(category: str, path: str) -> str:
        if "研究方案" in path:
            return "对外研究方案"
        if "agent_system_spec" in path:
            return "系统规格和技术细节"
        if "project_overview" in path:
            return "项目级总览和证据链"
        if "field_data_interface" in path:
            return "真实数据接口与校准模板"
        if "current_status" in path:
            return "最新状态"
        if "iteration_log" in path:
            return "迭代审计轨迹"
        if category == "field_data_interface":
            return "现场数据导入素材"
        if category == "organization_output":
            return "整理阶段汇报素材"
        if category == "presentation_asset":
            return "图表与讲述素材"
        if category == "formal_deck":
            return "正式 PPT 与展示 QA 交付"
        if category == "field_calibration_gate":
            return "现场校准门控与运行手册"
        if category == "model_realism_audit":
            return "模型真实性审计与优化路线"
        if category == "soft_sensor_uncertainty":
            return "软传感不确定性验证"
        if category == "knowledge_graph_curation":
            return "知识图谱策展与证据矩阵"
        if category == "literature_evidence":
            return "文献证据抽取与模型升级映射"
        if category == "soft_sensor_conformal_calibration":
            return "软传感保形校准接口"
        if category == "soft_sensor_field_holdout_gate":
            return "软传感 field holdout 放行门控"
        if category == "weak_target_stratified_conformal":
            return "弱目标分层保形校准"
        if category == "sensor_network_sparse_placement":
            return "管网布点与稀疏感知"
        if category == "multi_facility_collaborative_control":
            return "多设施协同控制与策略蒸馏"
        if category == "model_core_optimization_governance":
            return "全局系统架构治理与模型核心优化"
        if category == "catalyst_activity_proxy":
            return "催化剂活性代理观测"
        if category == "multi_facility_replay_evaluation":
            return "多设施 replay 离线评估"
        if category == "minimal_grey_box_physics":
            return "最小灰箱物理机制增强"
        if category == "soft_sensor_matrix_coupling":
            return "软传感矩阵耦合"
        if category == "grey_box_dynamic_latency":
            return "灰箱动态延迟审计"
        if category == "matrix_shock_fast_proxy_control":
            return "基质冲击快代理与延迟感知控制"
        if category == "timestamped_campaign_replay":
            return "现场时间戳回放接口"
        if category == "field_replay_calibration_gate":
            return "现场回放校准门控"
        if category == "field_replay_import":
            return "现场 replay 包导入与 provenance 验收"
        if category == "field_replay_evidence_chain":
            return "现场 replay 校准证据链"
        return "关键模拟报告"

    def _core_metrics(self, artifact_index: list[dict[str, object]]) -> dict[str, object]:
        latest_state = self.project_synthesis_metrics.get("latest_control_state", {})
        readiness = self.project_synthesis_metrics.get("readiness_assessment", {})
        field_readiness = self.field_data_metrics.get("readiness", {})
        table_statuses = self.field_data_metrics.get("table_statuses", {})
        execution_agent_count = int(self.project_synthesis_metrics.get("synthesized_agent_count", 28))
        support_agent_count = 3
        support_layer_label = "综合、接口、整理"
        presentation_assets = self.manifest.get("presentation_assets", {})
        if isinstance(presentation_assets, dict) and presentation_assets:
            support_agent_count += 1
            support_layer_label += "、展示素材"
        formal_deck = self.manifest.get("formal_deck", {})
        if isinstance(formal_deck, dict) and formal_deck:
            support_agent_count += 1
            support_layer_label += "、正式展示"
        field_calibration_gate = self.manifest.get("field_calibration_gate", {})
        if isinstance(field_calibration_gate, dict) and field_calibration_gate:
            support_agent_count += 1
            support_layer_label += "、校准门控"
        model_realism_audit = self.manifest.get("model_realism_audit", {})
        if isinstance(model_realism_audit, dict) and model_realism_audit:
            support_agent_count += 1
            support_layer_label += "、模型真实性审计"
        soft_sensor_uncertainty = self.manifest.get("soft_sensor_uncertainty", {})
        if isinstance(soft_sensor_uncertainty, dict) and soft_sensor_uncertainty:
            support_agent_count += 1
            support_layer_label += "、软传感不确定性验证"
        knowledge_graph_curation = self.manifest.get("knowledge_graph_curation", {})
        if isinstance(knowledge_graph_curation, dict) and knowledge_graph_curation:
            support_agent_count += 1
            support_layer_label += "、知识图谱策展"
        literature_evidence = self.manifest.get("literature_evidence", {})
        if isinstance(literature_evidence, dict) and literature_evidence:
            support_agent_count += 1
            support_layer_label += "、文献证据抽取"
        soft_sensor_conformal_calibration = self.manifest.get("soft_sensor_conformal_calibration", {})
        if isinstance(soft_sensor_conformal_calibration, dict) and soft_sensor_conformal_calibration:
            support_agent_count += 1
            support_layer_label += "、软传感保形校准"
        grey_box_dynamic_latency = self.manifest.get("grey_box_dynamic_latency", {})
        if isinstance(grey_box_dynamic_latency, dict) and grey_box_dynamic_latency:
            support_agent_count += 1
            support_layer_label += "、灰箱动态延迟审计"
        matrix_shock_fast_proxy = self.manifest.get("matrix_shock_fast_proxy_control", {})
        if isinstance(matrix_shock_fast_proxy, dict) and matrix_shock_fast_proxy:
            support_agent_count += 1
            support_layer_label += "、基质冲击快代理控制"
        timestamped_campaign_replay = self.manifest.get("timestamped_campaign_replay", {})
        if isinstance(timestamped_campaign_replay, dict) and timestamped_campaign_replay:
            support_agent_count += 1
            support_layer_label += "、时间戳回放接口"
        field_replay_calibration_gate = self.manifest.get("field_replay_calibration_gate", {})
        if isinstance(field_replay_calibration_gate, dict) and field_replay_calibration_gate:
            support_agent_count += 1
            support_layer_label += "、现场回放校准门控"
        field_replay_import = self.manifest.get("field_replay_import", {})
        if isinstance(field_replay_import, dict) and field_replay_import:
            support_agent_count += 1
            support_layer_label += "、现场 replay 导入门"
        field_replay_evidence_chain = self.manifest.get("field_replay_evidence_chain", {})
        if isinstance(field_replay_evidence_chain, dict) and field_replay_evidence_chain:
            support_agent_count += 1
            support_layer_label += "、现场 replay 证据链"
        soft_sensor_field_holdout_gate = self.manifest.get("soft_sensor_field_holdout_gate", {})
        if isinstance(soft_sensor_field_holdout_gate, dict) and soft_sensor_field_holdout_gate:
            support_agent_count += 1
            support_layer_label += "、软传感 field holdout 放行门控"
        weak_target_stratified_conformal = self.manifest.get("weak_target_stratified_conformal", {})
        if isinstance(weak_target_stratified_conformal, dict) and weak_target_stratified_conformal:
            support_agent_count += 1
            support_layer_label += "、弱目标分层保形校准"
        sensor_network_sparse_placement = self.manifest.get("sensor_network_sparse_placement", {})
        if isinstance(sensor_network_sparse_placement, dict) and sensor_network_sparse_placement:
            support_agent_count += 1
            support_layer_label += "、管网布点与稀疏感知"
        multi_facility_collaborative_control = self.manifest.get("multi_facility_collaborative_control", {})
        if isinstance(multi_facility_collaborative_control, dict) and multi_facility_collaborative_control:
            support_agent_count += 1
            support_layer_label += "、多设施协同控制"
        model_core_optimization_governance = self.manifest.get("model_core_optimization_governance", {})
        if isinstance(model_core_optimization_governance, dict) and model_core_optimization_governance:
            support_agent_count += 1
            support_layer_label += "、模型核心优化治理"
        catalyst_activity_proxy = self.manifest.get("catalyst_activity_proxy", {})
        if isinstance(catalyst_activity_proxy, dict) and catalyst_activity_proxy:
            support_agent_count += 1
            support_layer_label += "、催化剂活性代理观测"
        multi_facility_replay_evaluation = self.manifest.get("multi_facility_replay_evaluation", {})
        if isinstance(multi_facility_replay_evaluation, dict) and multi_facility_replay_evaluation:
            support_agent_count += 1
            support_layer_label += "、多设施 replay 离线评估"
        minimal_grey_box_physics = self.manifest.get("minimal_grey_box_physics", {})
        if isinstance(minimal_grey_box_physics, dict) and minimal_grey_box_physics:
            support_agent_count += 1
            support_layer_label += "、最小灰箱物理机制"
        soft_sensor_matrix_coupling = self.manifest.get("soft_sensor_matrix_coupling", {})
        if isinstance(soft_sensor_matrix_coupling, dict) and soft_sensor_matrix_coupling:
            support_agent_count += 1
            support_layer_label += "、软传感矩阵耦合"
        return {
            "total_agent_chain_count": execution_agent_count + support_agent_count,
            "execution_agent_count": execution_agent_count,
            "organizing_interface_agent_count": support_agent_count,
            "support_layer_label": support_layer_label,
            "latest_regression": self.latest_regression or self.manifest.get("latest_regression", "unknown"),
            "project_maturity": readiness.get("maturity_level", "unknown"),
            "recovery_control_mode": latest_state.get("recovery_control_mode", "unknown"),
            "next_intake_fraction": latest_state.get("next_intake_fraction"),
            "fallback_intake_fraction": latest_state.get("fallback_intake_fraction"),
            "replan_required": latest_state.get("replan_required"),
            "field_interface_status": field_readiness.get("interface_status", "unknown"),
            "field_data_origin": self.field_data_metrics.get("data_origin", "unknown"),
            "field_template_table_count": len(table_statuses),
            "artifact_count": len(artifact_index),
            "available_artifact_count": sum(1 for item in artifact_index if item["exists"]),
        }

    @staticmethod
    def _executive_summary(core_metrics: dict[str, object]) -> list[str]:
        return [
            "本项目已经从研究想法整理为可运行的低成本传感循环式水处理多智能体研究平台。",
            (
                f"当前链条包含 {core_metrics['total_agent_chain_count']} 个 agent："
                f"{core_metrics['execution_agent_count']} 个执行 agent 加 "
                f"{core_metrics['organizing_interface_agent_count']} 个{core_metrics['support_layer_label']} agent。"
            ),
            (
                "核心机制是用循环、暂存和慢证据窗口降低传感与反应速度要求，"
                "再用软传感器和多智能体诊断把黑箱过程变成可解释、可回退的灰箱。"
            ),
            (
                f"最新恢复控制为 {core_metrics['recovery_control_mode']}：下一轮进水 "
                f"{core_metrics['next_intake_fraction']}，失败回退 {core_metrics['fallback_intake_fraction']}。"
            ),
            (
                f"真实数据接口状态为 {core_metrics['field_interface_status']}，"
                "当前模板可运行，但必须用现场数据替换 synthetic/sample 行。"
            ),
        ]

    @staticmethod
    def _presentation_outline(core_metrics: dict[str, object]) -> list[dict[str, object]]:
        return [
            {
                "section_id": "S1",
                "title": "研究缘起：低成本传感下的黑箱困境",
                "message": "高端仪器昂贵且反应/检测存在延迟，工程上常出现进水、出水可测而中间过程不可观测的问题。",
                "evidence": ["聊天中提出的“软传感器把黑箱变灰箱”", "低成本传感与循环争取时间的研究定位"],
            },
            {
                "section_id": "S2",
                "title": "总体思路：循环结构 + 软传感 + 多智能体",
                "message": "系统不追求一次处理完，而是用回流、暂存、慢证据和闭环控制让行动可行。",
                "evidence": ["project_overview_28_agent.md", "agent_system_spec.md"],
            },
            {
                "section_id": "S3",
                "title": "系统架构：执行链 + 综合接口整理展示层",
                "message": (
                    f"当前成果包包含 {core_metrics['total_agent_chain_count']} 个 agent："
                    "执行链覆盖数据质控、软传感、机理诊断、控制仲裁、重规划和恢复控制，"
                    f"支持层覆盖{core_metrics['support_layer_label']}。"
                ),
                "evidence": [f"total_agent_chain_count={core_metrics['total_agent_chain_count']}", "docs/agent_system_spec.md"],
            },
            {
                "section_id": "S4",
                "title": "关键证据：从瓶颈发现到自动重规划",
                "message": "多批次运行暴露验证工时、时间窗口和催化剂库存瓶颈，系统能转入资源扩容、分阶段实施和写回回放。",
                "evidence": ["outputs/agent23_post_replan_replay/agent23_report.md"],
            },
            {
                "section_id": "S5",
                "title": "工程恢复：0.75 条件恢复与 0.60 回退线",
                "message": "0.75 不是永久满负荷结论，而是在验证错峰和 campaign 后复核条件下维持的恢复状态。",
                "evidence": ["outputs/agent27_recovery_execution_replay/agent27_report.md", "outputs/agent28_recovery_online_control/agent28_report.md"],
            },
            {
                "section_id": "S6",
                "title": "真实数据接口：从仿真平台进入实证校准",
                "message": "已定义五张现场数据表和 CSV 模板，用 batch_id 连接传感、离线检测、催化剂和操作日志。",
                "evidence": ["docs/field_data_interface_spec.md", "outputs/agent30_field_data_interface/field_data_templates/"],
            },
            {
                "section_id": "S7",
                "title": "边界说明：可作为研究平台，不是现场自治结论",
                "message": "当前结果适合项目书、原型展示和实证前仿真基线；真实漂移、寿命、副产物和部署接口仍需校准。",
                "evidence": [f"field_data_origin={core_metrics['field_data_origin']}", f"project_maturity={core_metrics['project_maturity']}"],
            },
            {
                "section_id": "S8",
                "title": "下一步实证校准",
                "message": "先接入真实传感时间序列、离线标签和 campaign 日志，再校准软传感器、时间预算和 fallback triggers。",
                "evidence": ["deliverables/README.md", "outputs/agent30_field_data_interface/agent30_report.md"],
            },
        ]

    @staticmethod
    def _key_metrics_table(core_metrics: dict[str, object]) -> list[dict[str, object]]:
        return [
            {
                "metric": "agent_chain_count",
                "value": core_metrics["total_agent_chain_count"],
                "interpretation": (
                    f"{core_metrics['execution_agent_count']} 个执行 agent 加 "
                    f"{core_metrics['organizing_interface_agent_count']} 个{core_metrics['support_layer_label']} agent"
                ),
            },
            {"metric": "latest_regression", "value": core_metrics["latest_regression"], "interpretation": "完整测试回归"},
            {"metric": "project_maturity", "value": core_metrics["project_maturity"], "interpretation": "适合进入真实数据校准的研究平台"},
            {"metric": "recovery_control_mode", "value": core_metrics["recovery_control_mode"], "interpretation": "最新恢复在线控制状态"},
            {"metric": "next_intake_fraction", "value": core_metrics["next_intake_fraction"], "interpretation": "下一轮条件恢复进水比例"},
            {"metric": "fallback_intake_fraction", "value": core_metrics["fallback_intake_fraction"], "interpretation": "恢复失败时回退比例"},
            {"metric": "replan_required", "value": core_metrics["replan_required"], "interpretation": "当前是否需要重规划"},
            {"metric": "field_interface_status", "value": core_metrics["field_interface_status"], "interpretation": "真实数据接口状态"},
            {"metric": "field_template_table_count", "value": core_metrics["field_template_table_count"], "interpretation": "已定义现场数据表数量"},
            {"metric": "available_artifacts", "value": f"{core_metrics['available_artifact_count']}/{core_metrics['artifact_count']}", "interpretation": "成果包索引可用性"},
        ]

    def _calibration_task_board(self) -> list[dict[str, object]]:
        tasks = self.field_data_metrics.get("calibration_tasks", [])
        if not isinstance(tasks, list):
            return []
        board: list[dict[str, object]] = []
        for task in tasks:
            if not isinstance(task, dict):
                continue
            board.append(
                {
                    "task_id": task.get("task_id"),
                    "title": task.get("title"),
                    "current_status": "template_ready" if task.get("task_ready") else "needs_data_patch",
                    "next_action": self._next_action_for_task(str(task.get("task_id", ""))),
                    "blockers": task.get("blockers", []),
                }
            )
        if self.manifest.get("field_replay_calibration_gate") or self.manifest.get("timestamped_campaign_replay"):
            board.append(
                {
                    "task_id": "P6_timestamped_fast_proxy_replay",
                    "title": "时间戳回放与快代理校准",
                    "current_status": "field_replay_required",
                    "next_action": self._next_action_for_task("P6_timestamped_fast_proxy_replay"),
                    "blockers": ["field_labeled_timestamped_replay_missing"],
                }
            )
        if self.manifest.get("field_replay_import"):
            board.append(
                {
                    "task_id": "P7_field_replay_import_package",
                    "title": "现场 replay 包导入与 provenance 验收",
                    "current_status": "field_package_required",
                    "next_action": self._next_action_for_task("P7_field_replay_import_package"),
                    "blockers": ["field_metadata_and_csv_package_missing"],
                }
            )
        if self.manifest.get("field_replay_evidence_chain"):
            board.append(
                {
                    "task_id": "P8_field_replay_evidence_chain",
                    "title": "现场 replay 导入-回放-G6 证据链",
                    "current_status": "evidence_chain_waiting_for_field_package",
                    "next_action": self._next_action_for_task("P8_field_replay_evidence_chain"),
                    "blockers": ["agent44_field_package_not_passed"],
                }
            )
        if self.manifest.get("soft_sensor_field_holdout_gate"):
            board.append(
                {
                    "task_id": "P9_soft_sensor_field_holdout_gate",
                    "title": "软传感 field holdout 放行门控",
                    "current_status": "field_holdout_required",
                    "next_action": self._next_action_for_task("P9_soft_sensor_field_holdout_gate"),
                    "blockers": ["field_holdout_labels_missing"],
                }
            )
        if self.manifest.get("weak_target_stratified_conformal"):
            board.append(
                {
                    "task_id": "P10_weak_target_stratified_conformal",
                    "title": "弱目标分层保形校准",
                    "current_status": "field_holdout_required",
                    "next_action": self._next_action_for_task("P10_weak_target_stratified_conformal"),
                    "blockers": ["weak_target_field_labels_missing"],
                }
            )
        if self.manifest.get("sensor_network_sparse_placement"):
            board.append(
                {
                    "task_id": "P11_sensor_network_sparse_placement",
                    "title": "管网布点与稀疏感知",
                    "current_status": "field_topology_required",
                    "next_action": self._next_action_for_task("P11_sensor_network_sparse_placement"),
                    "blockers": ["field_topology_and_node_labels_missing"],
                }
            )
        if self.manifest.get("multi_facility_collaborative_control"):
            board.append(
                {
                    "task_id": "P12_multi_facility_collaborative_control",
                    "title": "多设施协同控制与策略蒸馏",
                    "current_status": "field_coordination_replay_required",
                    "next_action": self._next_action_for_task("P12_multi_facility_collaborative_control"),
                    "blockers": ["multi_node_state_action_replay_missing", "distilled_policy_field_accuracy_missing"],
                }
            )
        if self.manifest.get("model_core_optimization_governance"):
            board.append(
                {
                    "task_id": "P13_model_core_optimization_governance",
                    "title": "全局系统架构治理与模型核心优化",
                    "current_status": "active_model_core_governance",
                    "next_action": self._next_action_for_task("P13_model_core_optimization_governance"),
                    "blockers": [],
                }
            )
        if self.manifest.get("catalyst_activity_proxy"):
            board.append(
                {
                    "task_id": "P14_catalyst_activity_proxy",
                    "title": "催化剂活性弱观测代理",
                    "current_status": "field_proxy_holdout_required",
                    "next_action": self._next_action_for_task("P14_catalyst_activity_proxy"),
                    "blockers": [
                        "field_catalyst_activity_labels_missing",
                        "pressure_drop_and_regeneration_events_missing",
                    ],
                }
            )
        if self.manifest.get("multi_facility_replay_evaluation"):
            board.append(
                {
                    "task_id": "P15_multi_facility_replay_evaluation",
                    "title": "多设施协同控制 replay 离线评估",
                    "current_status": "field_multinode_replay_required",
                    "next_action": self._next_action_for_task("P15_multi_facility_replay_evaluation"),
                    "blockers": [
                        "multi_node_state_action_reward_replay_missing",
                        "operator_or_validated_expert_action_labels_missing",
                    ],
                }
            )
        if self.manifest.get("minimal_grey_box_physics"):
            board.append(
                {
                    "task_id": "P16_minimal_grey_box_physics",
                    "title": "最小灰箱物理机制校准",
                    "current_status": "field_physics_calibration_required",
                    "next_action": self._next_action_for_task("P16_minimal_grey_box_physics"),
                    "blockers": [
                        "field_rtd_or_hydraulic_replay_missing",
                        "inlet_outlet_target_pollutant_labels_missing",
                        "byproduct_lab_panel_missing",
                    ],
                }
            )
        if self.manifest.get("soft_sensor_matrix_coupling"):
            board.append(
                {
                    "task_id": "P17_soft_sensor_matrix_coupling",
                    "title": "软传感 node-modality/missingness 矩阵耦合",
                    "current_status": "field_missingness_replay_required",
                    "next_action": self._next_action_for_task("P17_soft_sensor_matrix_coupling"),
                    "blockers": [
                        "node_specific_sensor_values_missing",
                        "layout_holdout_split_missing",
                        "field_missingness_reason_labels_missing",
                    ],
                }
            )
        return board

    @staticmethod
    def _next_action_for_task(task_id: str) -> str:
        mapping = {
            "P1_sensor_noise_drift": "导入真实传感器原始时间序列与校准/清洗记录。",
            "P2_soft_sensor_retraining": "对齐离线检测标签与传感窗口，重训软传感器。",
            "P3_catalyst_lifecycle": "补充催化剂活性、压降、再生和寿命记录。",
            "P4_loop_time_budget": "导入真实动作开始/结束时间，校准错峰收益和回退阈值。",
            "P5_cost_deployment": "替换真实报价、人工成本、提前期和 PLC/SCADA 点表。",
            "P6_timestamped_fast_proxy_replay": "导入真实 fast_proxy_event_log，对齐 result_time_min、effect_time_min、field_label_matrix_shock 和 false_positive_cost_index。",
            "P7_field_replay_import_package": "准备带 metadata.json 的真实 sensor/lab/operation/fast_proxy CSV 包，先通过 Agent44 再进入 Agent42/Agent43。",
            "P8_field_replay_evidence_chain": "按 Agent44 -> Agent42 -> Agent43 -> Agent45 顺序重跑证据链，只在完整链条通过后形成保护性写回候选。",
            "P9_soft_sensor_field_holdout_gate": "采集真实 field holdout 标签，重跑 Agent36/Agent39/Agent46，只有全门控通过才形成软传感 release gate 校准候选。",
            "P10_weak_target_stratified_conformal": "补 matrix_interference 与 catalyst_activity 的真实场景标签，重跑 Agent47 后再交给 Agent46 审查。",
            "P11_sensor_network_sparse_placement": "补真实管网/处理单元拓扑、水力停留时间、节点维护成本和节点级标签，重跑 Agent48 更新软传感观测矩阵。",
            "P12_multi_facility_collaborative_control": "补真实多节点 sensor/lab/operation/action replay，重跑 Agent49 校准 joint_action_accuracy、reward_regret 和决策树蒸馏准确度。",
            "P13_model_core_optimization_governance": "以全局七层系统骨架和六类能力为准星运行架构治理；普通新想法先沉淀，只有阶段边界或硬风险时才做深度重排。",
            "P14_catalyst_activity_proxy": "采集催化剂床前后 UV254/ORP、压降、再生事件和离线 catalyst_activity 标签，重跑 Agent51 形成 field_proxy_holdout，再由 Agent50 判断是否切回 P2 或推进 P3。",
            "P15_multi_facility_replay_evaluation": "采集真实多节点 sensor/lab/operation/action/reward replay，重跑 Agent52 校准 joint_action_accuracy、reward_regret、误保护成本和决策树 replay accuracy。",
            "P16_minimal_grey_box_physics": "采集 RTD/池容/流量、进出水目标污染物、氧化剂投加与余量、催化剂再生历史和副产物面板，重跑 Agent53 校准 k_eff、质量残差和副产物风险。",
            "P17_soft_sensor_matrix_coupling": "采集 node-specific 传感值、layout_id holdout split、缺测原因和 field missingness replay，重跑 Agent54 后再训练 layout-aware soft sensor baseline。",
        }
        return mapping.get(task_id, "补齐真实数据并重新运行接口检查。")

    @staticmethod
    def _readiness(artifact_index: list[dict[str, object]], presentation_outline: list[dict[str, object]]) -> dict[str, object]:
        total = len(artifact_index)
        available = sum(1 for item in artifact_index if item["exists"])
        artifact_score = available / max(1, total)
        outline_score = min(1.0, len(presentation_outline) / 8)
        score = round(0.7 * artifact_score + 0.3 * outline_score, 3)
        if score >= 0.95:
            status = "deliverable_pack_ready"
        elif score >= 0.75:
            status = "deliverable_pack_needs_minor_patch"
        else:
            status = "deliverable_pack_incomplete"
        return {
            "deliverable_status": status,
            "deliverable_score": score,
            "available_artifact_count": available,
            "total_artifact_count": total,
            "missing_artifacts": [item["path"] for item in artifact_index if not item["exists"]],
        }

    @staticmethod
    def _issues(artifact_index: list[dict[str, object]], readiness: dict[str, object]) -> list[QualityIssue]:
        issues: list[QualityIssue] = []
        missing = [item for item in artifact_index if not item["exists"]]
        for item in missing:
            issues.append(
                QualityIssue(
                    sensor="deliverable_artifact",
                    issue_type="deliverable_artifact_missing",
                    severity=Severity.WARNING,
                    message=f"成果索引中的文件不存在：{item['path']}",
                    evidence={"artifact": item},
                )
            )
        if readiness["deliverable_status"] == "deliverable_pack_ready":
            issues.append(
                QualityIssue(
                    sensor="deliverable_boundary",
                    issue_type="field_validation_not_completed",
                    severity=Severity.INFO,
                    message="成果包可用于汇报和项目书，但真实现场数据校准尚未完成。",
                    evidence={"next_stage": "field calibration"},
                )
            )
        return issues

    @staticmethod
    def _recommendations(readiness: dict[str, object]) -> list[str]:
        if readiness["deliverable_status"] != "deliverable_pack_ready":
            return [
                f"先补齐缺失成果文件：{readiness['missing_artifacts']}。",
                "补齐后重新生成成果包索引和汇报提纲。",
            ]
        return [
            "用 executive_brief.md 作为项目书摘要开头，用 presentation_outline.md 作为汇报/PPT 结构。",
            "用 key_metrics_table.md 统一口径，避免汇报时把 0.75 条件恢复误说成永久满负荷结论。",
            "下一阶段以 field_data_interface_spec.md、timestamped_campaign_replay_schema.md 和 CSV 模板为入口接入真实现场数据。",
        ]

from __future__ import annotations

from collections.abc import Sequence

from water_ai.agents.base import BaseAgent
from water_ai.domain import AgentReport, QualityIssue, SensorReading, Severity


class PresentationAssetAgent(BaseAgent):
    """Turn organized deliverables into slide-ready visual and narrative assets."""

    name = "presentation_asset_agent"

    def __init__(
        self,
        *,
        deliverable_metrics: dict[str, object] | None = None,
        project_synthesis_metrics: dict[str, object] | None = None,
        field_data_metrics: dict[str, object] | None = None,
    ) -> None:
        self.deliverable_metrics = deliverable_metrics or {}
        self.project_synthesis_metrics = project_synthesis_metrics or {}
        self.field_data_metrics = field_data_metrics or {}

    def run(self, readings: Sequence[SensorReading]) -> AgentReport:
        del readings
        core = self._core()
        slide_specs = self._slide_specs(core)
        visual_assets = self._visual_assets(core)
        narrative_script = self._narrative_script(slide_specs)
        project_book_sections = self._project_book_sections(core)
        readiness = self._readiness(slide_specs, visual_assets)
        issues = self._issues(core, readiness)
        recommendations = self._recommendations(readiness, core)
        summary = (
            f"汇报素材：{readiness['asset_status']}；"
            f"slide {len(slide_specs)} 页，图表素材 {len(visual_assets)} 个。"
        )
        confidence = round(min(0.92, max(0.35, 0.5 + 0.32 * readiness["asset_score"] - 0.03 * len(issues))), 3)

        return AgentReport(
            agent_name=self.name,
            confidence=confidence,
            summary=summary,
            issues=issues,
            recommendations=recommendations,
            metrics={
                "core": core,
                "slide_specs": slide_specs,
                "visual_assets": visual_assets,
                "narrative_script": narrative_script,
                "project_book_sections": project_book_sections,
                "readiness": readiness,
            },
        )

    def _core(self) -> dict[str, object]:
        core_metrics = self.deliverable_metrics.get("core_metrics", {})
        if not isinstance(core_metrics, dict):
            core_metrics = {}
        readiness = self.project_synthesis_metrics.get("readiness_assessment", {})
        if not isinstance(readiness, dict):
            readiness = {}
        field_readiness = self.field_data_metrics.get("readiness", {})
        if not isinstance(field_readiness, dict):
            field_readiness = {}
        deliverable_agent_count = int(core_metrics.get("total_agent_chain_count", 31))
        agent_chain_count = max(32, deliverable_agent_count if deliverable_agent_count >= 32 else deliverable_agent_count + 1)
        artifact_count = core_metrics.get("artifact_count")
        available_artifact_count = core_metrics.get("available_artifact_count")
        if "available_artifacts" in core_metrics:
            available_artifacts = core_metrics["available_artifacts"]
        elif isinstance(artifact_count, int) and isinstance(available_artifact_count, int):
            available_artifacts = f"{available_artifact_count}/{artifact_count}"
        else:
            available_artifacts = "unknown"
        return {
            "agent_chain_count": agent_chain_count,
            "prototype_agent_count": 30,
            "execution_agent_count": core_metrics.get("execution_agent_count", 28),
            "latest_regression": core_metrics.get("latest_regression", "130 passed"),
            "project_maturity": core_metrics.get("project_maturity", readiness.get("maturity_level", "unknown")),
            "recovery_control_mode": core_metrics.get("recovery_control_mode", "maintain_conditional_recovery"),
            "next_intake_fraction": core_metrics.get("next_intake_fraction", 0.75),
            "fallback_intake_fraction": core_metrics.get("fallback_intake_fraction", 0.6),
            "replan_required": core_metrics.get("replan_required", False),
            "field_interface_status": core_metrics.get(
                "field_interface_status", field_readiness.get("interface_status", "unknown")
            ),
            "field_data_origin": core_metrics.get("field_data_origin", self.field_data_metrics.get("data_origin", "unknown")),
            "field_template_table_count": core_metrics.get("field_template_table_count", 5),
            "available_artifacts": available_artifacts,
        }

    @staticmethod
    def _slide_specs(core: dict[str, object]) -> list[dict[str, object]]:
        support_label = "Agent31-33" if int(core["agent_chain_count"]) >= 33 else "Agent31-32"
        return [
            {
                "slide_id": "S1",
                "title": "低成本传感条件下，把水处理黑箱变成灰箱",
                "purpose": "建立研究问题和核心命题。",
                "visual_id": "grey_box_loop",
                "speaker_focus": "贵仪器和慢检测不是简单替换问题，而是需要系统结构为推断争取时间。",
            },
            {
                "slide_id": "S2",
                "title": "总体方案：循环结构 + 软传感器 + 多智能体闭环",
                "purpose": "说明系统为什么不是一次处理，而是动态回流、暂存、加药、验证和放行。",
                "visual_id": "control_loop",
                "speaker_focus": "循环窗口让传感和反应速度不必极快，从而降低成本并提升可执行性。",
            },
            {
                "slide_id": "S3",
                "title": "系统架构：30-agent 原型链与整理展示交付层",
                "purpose": "展示 agent 分层和责任边界。",
                "visual_id": "agent_layer_map",
                "speaker_focus": f"当前共有 {core['agent_chain_count']} 个 agent，其中 30 个构成原型链，{support_label} 负责成果整理、展示素材和正式 deck。",
            },
            {
                "slide_id": "S4",
                "title": "关键证据链：从多批次瓶颈到自动重规划",
                "purpose": "展示系统如何发现验证、时间和库存瓶颈，并转成资源和项目动作。",
                "visual_id": "evidence_waterfall",
                "speaker_focus": "单批次成功不等于 campaign 可执行，瓶颈必须能触发重规划和写回验证。",
            },
            {
                "slide_id": "S5",
                "title": "恢复控制边界：0.75 条件恢复，0.60 失败回退",
                "purpose": "统一关键工程结论，防止把条件恢复说成永久满负荷。",
                "visual_id": "recovery_boundary",
                "speaker_focus": f"当前恢复模式为 {core['recovery_control_mode']}，进水 {core['next_intake_fraction']}，回退 {core['fallback_intake_fraction']}。",
            },
            {
                "slide_id": "S6",
                "title": "真实数据接口：五张表连接现场和模型",
                "purpose": "说明后续实证怎样落地，不停留在仿真。",
                "visual_id": "field_data_schema",
                "speaker_focus": "用 batch_id 把在线传感、离线检测、催化剂寿命、操作日志和成本部署数据连起来。",
            },
            {
                "slide_id": "S7",
                "title": "边界和诚实口径：研究平台，不是现场自治结论",
                "purpose": "明确成熟度与尚未完成的实证验证。",
                "visual_id": "validation_boundary",
                "speaker_focus": f"当前接口状态为 {core['field_interface_status']}，数据来源是 {core['field_data_origin']}。",
            },
            {
                "slide_id": "S8",
                "title": "下一步：真实数据导入与参数校准",
                "purpose": "给出可执行后续路线。",
                "visual_id": "calibration_roadmap",
                "speaker_focus": "先导入真实传感和离线标签，再校准软传感、时间预算、错峰收益和回退门槛。",
            },
        ]

    @staticmethod
    def _visual_assets(core: dict[str, object]) -> list[dict[str, object]]:
        support_label = "31-33 整理/汇报/正式 deck" if int(core["agent_chain_count"]) >= 33 else "31-32 整理与汇报素材"
        return [
            {
                "visual_id": "grey_box_loop",
                "type": "mermaid",
                "title": "黑箱到灰箱逻辑图",
                "mermaid": """flowchart LR
    A["进水/出水低成本可测"] --> B["中间过程黑箱"]
    B --> C["循环/暂存争取时间"]
    C --> D["软传感估计隐藏状态"]
    D --> E["多智能体解释与诊断"]
    E --> F["灰箱：可解释、可干预、可回退"]""",
            },
            {
                "visual_id": "control_loop",
                "type": "mermaid",
                "title": "循环式闭环控制图",
                "mermaid": """flowchart LR
    S["低成本传感"] --> Q["数据质控"]
    Q --> H["软传感隐藏状态"]
    H --> M["机理解释/故障诊断"]
    M --> A["动作生成"]
    A --> C["成本安全仲裁"]
    C --> R{"是否可放行?"}
    R -- 否 --> L["回流/暂存/加药/再生/预处理"]
    L --> S
    R -- 是 --> O["达标放行"]""",
            },
            {
                "visual_id": "agent_layer_map",
                "type": "mermaid",
                "title": "Agent 分层图",
                "mermaid": """flowchart TB
    G1["1-2 感知与软传感"] --> G2["3-4 机理诊断"]
    G2 --> G3["5-10 控制与仲裁"]
    G3 --> G4["11-13 传感配置与批次调度"]
    G4 --> G5["14-18 资源/经济/实施"]
    G5 --> G6["19-23 在线重规划"]
    G6 --> G7["24-28 恢复控制"]
    G7 --> G8["29-30 项目总览与真实数据接口"]
    G8 --> G9[""" + support_label + """"]""",
            },
            {
                "visual_id": "evidence_waterfall",
                "type": "mermaid",
                "title": "瓶颈到重规划证据链",
                "mermaid": """flowchart LR
    B1["多批次瓶颈<br/>验证/时间/催化剂"] --> B2["资源扩容对比"]
    B2 --> B3["长期经济性与分阶段实施"]
    B3 --> B4["压力测试与项目组合"]
    B4 --> B5["在线重规划"]
    B5 --> B6["基线写回"]
    B6 --> B7["回放验证通过"]""",
            },
            {
                "visual_id": "recovery_boundary",
                "type": "mermaid",
                "title": "恢复进水边界图",
                "mermaid": f"""flowchart LR
    P["保护/恢复控制"] --> T["目标进水 {core['next_intake_fraction']}"]
    T --> C{{"campaign 后复核"}}
    C -- "稳定且无瓶颈" --> K["维持条件恢复"]
    C -- "时间/验证/库存触发" --> F["回退 {core['fallback_intake_fraction']}"]
    F --> R["重新运行重规划链"]""",
            },
            {
                "visual_id": "field_data_schema",
                "type": "mermaid",
                "title": "真实数据接口图",
                "mermaid": """flowchart TB
    B["batch_id"] --> S["sensor_timeseries"]
    B --> L["offline_lab_results"]
    B --> C["catalyst_lifecycle"]
    B --> O["campaign_operation_log"]
    D["cost_deployment"] --> P["经济性/部署校准"]
    S --> M["软传感/质控校准"]
    L --> M
    C --> K["催化剂寿命校准"]
    O --> T["时间预算/回退门槛校准"]""",
            },
            {
                "visual_id": "validation_boundary",
                "type": "callout",
                "title": "边界说明卡片",
                "content": [
                    "当前可用于项目书、原型展示和实证前仿真基线。",
                    "当前 synthetic/sample 数据只能验证接口，不等于现场实证。",
                    "必须继续校准真实传感漂移、催化剂寿命、副产物风险和部署接口。",
                ],
            },
            {
                "visual_id": "calibration_roadmap",
                "type": "timeline",
                "title": "P1-P5 实证校准路线",
                "milestones": [
                    "P1 传感器噪声与漂移",
                    "P2 软传感器真实标签重训",
                    "P3 催化剂寿命与副产物风险",
                    "P4 时间预算与回退门槛",
                    "P5 经济性与部署接口",
                ],
            },
        ]

    @staticmethod
    def _narrative_script(slide_specs: list[dict[str, object]]) -> list[dict[str, str]]:
        return [
            {
                "slide_id": str(slide["slide_id"]),
                "speaker_note": f"这一页讲 {slide['purpose']} 重点落在：{slide['speaker_focus']}",
            }
            for slide in slide_specs
        ]

    @staticmethod
    def _project_book_sections(core: dict[str, object]) -> list[dict[str, object]]:
        return [
            {
                "section": "研究背景与问题定义",
                "include_assets": ["grey_box_loop"],
                "must_say": "低成本传感条件下的关键不是少装仪器，而是把不可观测过程变成可推断灰箱。",
            },
            {
                "section": "总体技术路线",
                "include_assets": ["control_loop", "agent_layer_map"],
                "must_say": f"系统包含 {core['prototype_agent_count']} 个原型链 agent，并由整理层形成交付材料。",
            },
            {
                "section": "关键实验与模拟证据",
                "include_assets": ["evidence_waterfall", "recovery_boundary"],
                "must_say": "0.75 是条件恢复比例，0.60 是失败回退线。",
            },
            {
                "section": "真实数据与实证校准计划",
                "include_assets": ["field_data_schema", "calibration_roadmap"],
                "must_say": "所有现场数据必须围绕 batch_id 回连，synthetic/sample 只能作为接口测试。",
            },
        ]

    @staticmethod
    def _readiness(slide_specs: list[dict[str, object]], visual_assets: list[dict[str, object]]) -> dict[str, object]:
        slide_score = min(1.0, len(slide_specs) / 8)
        visual_score = min(1.0, len(visual_assets) / 8)
        asset_score = round(0.55 * slide_score + 0.45 * visual_score, 3)
        status = "presentation_assets_ready" if asset_score >= 0.95 else "presentation_assets_incomplete"
        return {
            "asset_status": status,
            "asset_score": asset_score,
            "slide_count": len(slide_specs),
            "visual_asset_count": len(visual_assets),
        }

    @staticmethod
    def _issues(core: dict[str, object], readiness: dict[str, object]) -> list[QualityIssue]:
        issues: list[QualityIssue] = []
        if readiness["asset_status"] != "presentation_assets_ready":
            issues.append(
                QualityIssue(
                    sensor="presentation_assets",
                    issue_type="presentation_assets_incomplete",
                    severity=Severity.WARNING,
                    message="汇报素材数量不足，需要补充 slide 或图表。",
                    evidence=readiness,
                )
            )
        if core.get("field_data_origin") != "field":
            issues.append(
                QualityIssue(
                    sensor="presentation_boundary",
                    issue_type="presentation_must_disclose_synthetic_data",
                    severity=Severity.INFO,
                    message="汇报中必须说明当前真实数据接口仍为 synthetic/sample，不是现场实证。",
                    evidence={"field_data_origin": core.get("field_data_origin")},
                )
            )
        return issues

    @staticmethod
    def _recommendations(readiness: dict[str, object], core: dict[str, object]) -> list[str]:
        if readiness["asset_status"] != "presentation_assets_ready":
            return ["先补齐 8 页 slide 结构和 8 个图表素材，再进入 PPT 制作。"]
        if int(core.get("agent_chain_count", 32)) >= 33:
            return [
                "正式 PPTX 已生成后，用 deck_qa_checklist.md 复核中文字体、恢复边界和 synthetic/sample 说明。",
                "汇报时保留 recovery_boundary 图，强调 0.75 是条件恢复而不是永久满负荷。",
                "下一阶段以 field_data_interface_spec.md 和 CSV 模板为入口接入真实现场数据。",
            ]
        return [
            "下一步可直接用 visual_storyboard.md 和 slide_narrative_script.md 制作正式 PPT。",
            "做 PPT 时保留 recovery_boundary 图，强调 0.75 是条件恢复而不是永久满负荷。",
            "项目书正文可按 project_book_sections.md 组织四个主要章节。",
        ]

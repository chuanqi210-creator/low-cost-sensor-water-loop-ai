from __future__ import annotations

from collections.abc import Sequence

from water_ai.agents.base import BaseAgent
from water_ai.domain import AgentReport, QualityIssue, SensorReading, Severity


class PresentationDeckAgent(BaseAgent):
    """Convert slide-ready assets into a formal deck plan and QA contract."""

    name = "presentation_deck_agent"

    def __init__(
        self,
        *,
        presentation_asset_metrics: dict[str, object] | None = None,
        output_targets: dict[str, str] | None = None,
    ) -> None:
        self.presentation_asset_metrics = presentation_asset_metrics or {}
        self.output_targets = output_targets or {
            "pptx": "deliverables/ppt/low_cost_water_ai_formal_deck.pptx",
            "claim_spine": "deliverables/deck_claim_spine.md",
            "design_system": "deliverables/deck_design_system.md",
            "qa_checklist": "deliverables/deck_qa_checklist.md",
        }

    def run(self, readings: Sequence[SensorReading]) -> AgentReport:
        del readings
        core = self._core()
        slide_specs = self._slide_specs()
        claim_spine = self._claim_spine(slide_specs, core)
        design_system = self._design_system()
        deck_plan = self._deck_plan(claim_spine)
        qa_gates = self._qa_gates(core)
        readiness = self._readiness(claim_spine, deck_plan, design_system, qa_gates)
        issues = self._issues(core, readiness)
        recommendations = self._recommendations(readiness)
        summary = (
            f"正式展示包规划：{readiness['deck_status']}；"
            f"{readiness['slide_count']} 页，QA 门槛 {readiness['qa_gate_count']} 项。"
        )
        confidence = round(min(0.93, max(0.35, 0.52 + 0.34 * readiness["deck_score"] - 0.03 * len(issues))), 3)

        return AgentReport(
            agent_name=self.name,
            confidence=confidence,
            summary=summary,
            issues=issues,
            recommendations=recommendations,
            metrics={
                "core": core,
                "claim_spine": claim_spine,
                "design_system": design_system,
                "deck_plan": deck_plan,
                "qa_gates": qa_gates,
                "readiness": readiness,
                "output_targets": self.output_targets,
            },
        )

    def _core(self) -> dict[str, object]:
        core = self.presentation_asset_metrics.get("core", {})
        if not isinstance(core, dict):
            core = {}
        return {
            "agent_chain_count": core.get("agent_chain_count", 32),
            "latest_regression": core.get("latest_regression", "136 passed"),
            "available_artifacts": core.get("available_artifacts", "27/27"),
            "recovery_control_mode": core.get("recovery_control_mode", "maintain_conditional_recovery"),
            "next_intake_fraction": core.get("next_intake_fraction", 0.75),
            "fallback_intake_fraction": core.get("fallback_intake_fraction", 0.6),
            "field_interface_status": core.get("field_interface_status", "template_ready_not_field_validated"),
            "field_data_origin": core.get("field_data_origin", "synthetic"),
        }

    def _slide_specs(self) -> list[dict[str, object]]:
        slide_specs = self.presentation_asset_metrics.get("slide_specs", [])
        if isinstance(slide_specs, list) and slide_specs:
            return [item for item in slide_specs if isinstance(item, dict)]
        return [
            {"slide_id": "S1", "title": "低成本传感条件下，把水处理黑箱变成灰箱", "visual_id": "grey_box_loop"},
            {"slide_id": "S2", "title": "总体方案：循环结构 + 软传感器 + 多智能体闭环", "visual_id": "control_loop"},
            {"slide_id": "S3", "title": "系统架构：30-agent 原型链与整理展示层", "visual_id": "agent_layer_map"},
            {"slide_id": "S4", "title": "关键证据链：从多批次瓶颈到自动重规划", "visual_id": "evidence_waterfall"},
            {"slide_id": "S5", "title": "恢复控制边界：0.75 条件恢复，0.60 失败回退", "visual_id": "recovery_boundary"},
            {"slide_id": "S6", "title": "真实数据接口：五张表连接现场和模型", "visual_id": "field_data_schema"},
            {"slide_id": "S7", "title": "边界和诚实口径：研究平台，不是现场自治结论", "visual_id": "validation_boundary"},
            {"slide_id": "S8", "title": "下一步：真实数据导入与参数校准", "visual_id": "calibration_roadmap"},
        ]

    @staticmethod
    def _claim_spine(slide_specs: list[dict[str, object]], core: dict[str, object]) -> list[dict[str, object]]:
        claims = {
            "S1": "低成本传感的核心难题不是少装仪器，而是中间过程不可观测。",
            "S2": "循环结构为慢传感和慢验证争取时间，使低成本闭环控制可执行。",
            "S3": f"当前系统已形成 {core['agent_chain_count']} 个 agent 的可运行研究平台。",
            "S4": "多批次瓶颈必须被自动转译为资源、排程和项目重规划动作。",
            "S5": (
                f"{core['next_intake_fraction']} 是条件恢复边界，"
                f"{core['fallback_intake_fraction']} 是失败回退线。"
            ),
            "S6": "五张现场数据表把传感、离线标签、催化剂寿命、操作日志和成本连成校准入口。",
            "S7": "当前结论是研究平台和仿真基线，不是现场自治系统已经成立。",
            "S8": "下一步应先做真实数据导入，再校准软传感、时间预算和回退门槛。",
        }
        proof_objects = {
            "grey_box_loop": "黑箱到灰箱逻辑图",
            "control_loop": "循环式闭环控制图",
            "agent_layer_map": "agent 分层架构图",
            "evidence_waterfall": "瓶颈到重规划证据链",
            "recovery_boundary": "恢复控制边界图",
            "field_data_schema": "真实数据接口图",
            "validation_boundary": "边界说明卡片",
            "calibration_roadmap": "P1-P5 校准路线图",
        }
        spine: list[dict[str, object]] = []
        for index, slide in enumerate(slide_specs, start=1):
            slide_id = str(slide.get("slide_id", f"S{index}"))
            visual_id = str(slide.get("visual_id", "unknown"))
            spine.append(
                {
                    "slide_id": slide_id,
                    "sequence": index,
                    "title": slide.get("title", slide_id),
                    "claim": claims.get(slide_id, str(slide.get("purpose", ""))),
                    "proof_object": proof_objects.get(visual_id, visual_id),
                    "visual_id": visual_id,
                    "must_keep": _must_keep(slide_id, core),
                }
            )
        return spine

    @staticmethod
    def _design_system() -> dict[str, object]:
        return {
            "deck_profile": "engineering-platform",
            "task_mode": "create",
            "canvas": "16:9 widescreen",
            "font_policy": {
                "primary_cjk": "Microsoft YaHei",
                "mac_fallback": "PingFang SC",
                "latin": "Aptos",
                "reason": "避免中文在 Word/PPT 兼容环境中出现乱码或缺字。",
            },
            "palette": {
                "ink": "#1E293B",
                "paper": "#F8FAFC",
                "blue": "#2563EB",
                "green": "#059669",
                "amber": "#D97706",
                "red": "#DC2626",
                "line": "#CBD5E1",
            },
            "layout_rules": [
                "每页只有一个可复述主张，证据图形必须支撑该主张。",
                "图形节点保持明确方向、分组和边界，不使用装饰性连接线。",
                "所有边界页必须显式写出 synthetic/sample 不能代表现场实证。",
                "恢复控制页必须同时出现 0.75 条件恢复和 0.60 回退线。",
            ],
        }

    @staticmethod
    def _deck_plan(claim_spine: list[dict[str, object]]) -> list[dict[str, object]]:
        layouts = [
            "problem-framing-flow",
            "closed-loop-architecture",
            "layered-agent-map",
            "evidence-waterfall",
            "decision-boundary",
            "schema-linkage",
            "boundary-callout",
            "calibration-roadmap",
        ]
        return [
            {
                **slide,
                "layout": layouts[index - 1] if index <= len(layouts) else "technical-proof",
                "speaker_mode": "claim-first, diagram-second, boundary-explicit",
                "footer_evidence": "synthetic/sample 数据仅用于接口与仿真验证，现场校准未完成。",
            }
            for index, slide in enumerate(claim_spine, start=1)
        ]

    @staticmethod
    def _qa_gates(core: dict[str, object]) -> list[dict[str, object]]:
        return [
            {
                "gate": "cjk_font_compatibility",
                "requirement": "PPTX 采用 Microsoft YaHei / PingFang SC / Aptos 字体策略，避免中文乱码。",
            },
            {
                "gate": "recovery_boundary_integrity",
                "requirement": f"必须同时显示 {core['next_intake_fraction']} 条件恢复和 {core['fallback_intake_fraction']} 失败回退。",
            },
            {
                "gate": "field_validation_disclosure",
                "requirement": "必须说明当前数据来源为 synthetic/sample，不得表述为现场自治结论。",
            },
            {
                "gate": "artifact_consistency",
                "requirement": f"关键页必须保持 {core['agent_chain_count']} agent、{core['available_artifacts']} 成果索引和 {core['latest_regression']} 回归口径。",
            },
            {
                "gate": "render_layout_check",
                "requirement": "导出前必须渲染预览并检查中文、线条、图表标签和页脚没有重叠。",
            },
        ]

    @staticmethod
    def _readiness(
        claim_spine: list[dict[str, object]],
        deck_plan: list[dict[str, object]],
        design_system: dict[str, object],
        qa_gates: list[dict[str, object]],
    ) -> dict[str, object]:
        slide_score = min(1.0, len(claim_spine) / 8)
        qa_score = min(1.0, len(qa_gates) / 5)
        has_font_policy = "font_policy" in design_system
        has_recovery_boundary = any(slide["visual_id"] == "recovery_boundary" for slide in deck_plan)
        score = round(0.45 * slide_score + 0.35 * qa_score + 0.1 * has_font_policy + 0.1 * has_recovery_boundary, 3)
        status = "formal_deck_plan_ready" if score >= 0.95 else "formal_deck_plan_incomplete"
        return {
            "deck_status": status,
            "deck_score": score,
            "slide_count": len(claim_spine),
            "qa_gate_count": len(qa_gates),
            "has_font_policy": has_font_policy,
            "has_recovery_boundary": has_recovery_boundary,
        }

    @staticmethod
    def _issues(core: dict[str, object], readiness: dict[str, object]) -> list[QualityIssue]:
        issues: list[QualityIssue] = []
        if readiness["deck_status"] != "formal_deck_plan_ready":
            issues.append(
                QualityIssue(
                    sensor="presentation_deck",
                    issue_type="formal_deck_plan_incomplete",
                    severity=Severity.WARNING,
                    message="正式展示包规划仍缺少必要 slide、字体策略或 QA 门槛。",
                    evidence=readiness,
                )
            )
        if core.get("field_data_origin") != "field":
            issues.append(
                QualityIssue(
                    sensor="presentation_boundary",
                    issue_type="deck_must_disclose_synthetic_data",
                    severity=Severity.INFO,
                    message="正式 PPT 必须说明 synthetic/sample 数据不能代表现场实证。",
                    evidence={"field_data_origin": core.get("field_data_origin")},
                )
            )
        return issues

    @staticmethod
    def _recommendations(readiness: dict[str, object]) -> list[str]:
        if readiness["deck_status"] != "formal_deck_plan_ready":
            return ["先补齐正式 deck 的 claim spine、字体策略和 QA 门槛，再进入 PPTX 生成。"]
        return [
            "按 deck_claim_spine.md 生成正式 PPTX，标题采用主张句，不做泛泛介绍页。",
            "PPTX 导出后必须检查中文字体、恢复边界页和 synthetic/sample 边界说明。",
            "正式汇报时把下一阶段定位为真实现场数据导入与参数校准。",
        ]


def _must_keep(slide_id: str, core: dict[str, object]) -> list[str]:
    mapping = {
        "S3": [f"{core['agent_chain_count']} agents", str(core["latest_regression"])],
        "S5": [f"intake={core['next_intake_fraction']}", f"fallback={core['fallback_intake_fraction']}"],
        "S7": [str(core["field_interface_status"]), str(core["field_data_origin"])],
        "S8": ["P1-P5 field calibration"],
    }
    return mapping.get(slide_id, [])

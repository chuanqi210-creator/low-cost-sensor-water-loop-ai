from water_ai.agents.presentation_deck_agent import PresentationDeckAgent


def test_presentation_deck_agent_builds_formal_deck_plan() -> None:
    report = PresentationDeckAgent(presentation_asset_metrics=_presentation_metrics()).run([])

    readiness = report.metrics["readiness"]
    design = report.metrics["design_system"]

    assert readiness["deck_status"] == "formal_deck_plan_ready"
    assert readiness["slide_count"] == 8
    assert readiness["qa_gate_count"] == 5
    assert design["font_policy"]["primary_cjk"] == "Microsoft YaHei"
    assert report.metrics["deck_plan"][0]["speaker_mode"] == "claim-first, diagram-second, boundary-explicit"


def test_presentation_deck_agent_preserves_recovery_boundary_and_counts() -> None:
    report = PresentationDeckAgent(presentation_asset_metrics=_presentation_metrics()).run([])

    claim_map = {slide["slide_id"]: slide for slide in report.metrics["claim_spine"]}
    gates = {gate["gate"]: gate for gate in report.metrics["qa_gates"]}

    assert "0.75" in claim_map["S5"]["claim"]
    assert "0.6" in claim_map["S5"]["claim"]
    assert "intake=0.75" in claim_map["S5"]["must_keep"]
    assert "32 agent" in gates["artifact_consistency"]["requirement"]
    assert "27/27" in gates["artifact_consistency"]["requirement"]


def test_presentation_deck_agent_discloses_synthetic_data_boundary() -> None:
    report = PresentationDeckAgent(presentation_asset_metrics=_presentation_metrics()).run([])

    assert any(issue.issue_type == "deck_must_disclose_synthetic_data" for issue in report.issues)


def _presentation_metrics() -> dict[str, object]:
    return {
        "core": {
            "agent_chain_count": 32,
            "latest_regression": "136 passed",
            "available_artifacts": "27/27",
            "recovery_control_mode": "maintain_conditional_recovery",
            "next_intake_fraction": 0.75,
            "fallback_intake_fraction": 0.6,
            "field_interface_status": "template_ready_not_field_validated",
            "field_data_origin": "synthetic",
        },
        "slide_specs": [
            {"slide_id": "S1", "title": "低成本传感条件下，把水处理黑箱变成灰箱", "visual_id": "grey_box_loop"},
            {"slide_id": "S2", "title": "总体方案：循环结构 + 软传感器 + 多智能体闭环", "visual_id": "control_loop"},
            {"slide_id": "S3", "title": "系统架构：30-agent 原型链与整理展示层", "visual_id": "agent_layer_map"},
            {"slide_id": "S4", "title": "关键证据链：从多批次瓶颈到自动重规划", "visual_id": "evidence_waterfall"},
            {"slide_id": "S5", "title": "恢复控制边界：0.75 条件恢复，0.60 失败回退", "visual_id": "recovery_boundary"},
            {"slide_id": "S6", "title": "真实数据接口：五张表连接现场和模型", "visual_id": "field_data_schema"},
            {"slide_id": "S7", "title": "边界和诚实口径：研究平台，不是现场自治结论", "visual_id": "validation_boundary"},
            {"slide_id": "S8", "title": "下一步：真实数据导入与参数校准", "visual_id": "calibration_roadmap"},
        ],
    }

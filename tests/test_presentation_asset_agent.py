from water_ai.agents.presentation_asset_agent import PresentationAssetAgent


def test_presentation_asset_agent_builds_slide_ready_assets() -> None:
    report = PresentationAssetAgent(
        deliverable_metrics=_deliverable_metrics(),
        project_synthesis_metrics=_project_metrics(),
        field_data_metrics=_field_metrics(),
    ).run([])

    readiness = report.metrics["readiness"]

    assert readiness["asset_status"] == "presentation_assets_ready"
    assert readiness["slide_count"] == 8
    assert readiness["visual_asset_count"] == 8
    assert report.metrics["slide_specs"][0]["slide_id"] == "S1"
    assert report.metrics["slide_specs"][-1]["visual_id"] == "calibration_roadmap"


def test_presentation_asset_agent_preserves_recovery_boundary() -> None:
    report = PresentationAssetAgent(
        deliverable_metrics=_deliverable_metrics(),
        project_synthesis_metrics=_project_metrics(),
        field_data_metrics=_field_metrics(),
    ).run([])

    visuals = {visual["visual_id"]: visual for visual in report.metrics["visual_assets"]}
    key_metrics = report.metrics["core"]

    assert key_metrics["next_intake_fraction"] == 0.75
    assert key_metrics["fallback_intake_fraction"] == 0.6
    assert "0.75" in visuals["recovery_boundary"]["mermaid"]
    assert "0.6" in visuals["recovery_boundary"]["mermaid"]


def test_presentation_asset_agent_derives_current_artifact_and_agent_counts() -> None:
    metrics = _deliverable_metrics()
    metrics["core_metrics"].pop("available_artifacts")
    metrics["core_metrics"]["available_artifact_count"] = 27
    metrics["core_metrics"]["artifact_count"] = 27

    report = PresentationAssetAgent(
        deliverable_metrics=metrics,
        project_synthesis_metrics=_project_metrics(),
        field_data_metrics=_field_metrics(),
    ).run([])

    core = report.metrics["core"]

    assert core["agent_chain_count"] == 32
    assert core["available_artifacts"] == "27/27"
    assert "Agent31-32" in report.metrics["slide_specs"][2]["speaker_focus"]


def test_presentation_asset_agent_does_not_double_count_existing_presentation_layer() -> None:
    metrics = _deliverable_metrics()
    metrics["core_metrics"]["total_agent_chain_count"] = 32

    report = PresentationAssetAgent(
        deliverable_metrics=metrics,
        project_synthesis_metrics=_project_metrics(),
        field_data_metrics=_field_metrics(),
    ).run([])

    assert report.metrics["core"]["agent_chain_count"] == 32


def test_presentation_asset_agent_describes_formal_deck_layer_when_present() -> None:
    metrics = _deliverable_metrics()
    metrics["core_metrics"]["total_agent_chain_count"] = 33

    report = PresentationAssetAgent(
        deliverable_metrics=metrics,
        project_synthesis_metrics=_project_metrics(),
        field_data_metrics=_field_metrics(),
    ).run([])

    slide = report.metrics["slide_specs"][2]
    visual = {item["visual_id"]: item for item in report.metrics["visual_assets"]}["agent_layer_map"]

    assert "Agent31-33" in slide["speaker_focus"]
    assert "31-33 整理/汇报/正式 deck" in visual["mermaid"]


def test_presentation_asset_agent_warns_when_data_is_synthetic() -> None:
    report = PresentationAssetAgent(
        deliverable_metrics=_deliverable_metrics(),
        project_synthesis_metrics=_project_metrics(),
        field_data_metrics=_field_metrics(),
    ).run([])

    assert any(issue.issue_type == "presentation_must_disclose_synthetic_data" for issue in report.issues)


def _deliverable_metrics() -> dict[str, object]:
    return {
        "core_metrics": {
            "total_agent_chain_count": 31,
            "execution_agent_count": 28,
            "latest_regression": "130 passed",
            "project_maturity": "research_platform_ready_for_field_calibration",
            "recovery_control_mode": "maintain_conditional_recovery",
            "next_intake_fraction": 0.75,
            "fallback_intake_fraction": 0.6,
            "replan_required": False,
            "field_interface_status": "template_ready_not_field_validated",
            "field_data_origin": "synthetic",
            "field_template_table_count": 5,
            "available_artifacts": "23/23",
        }
    }


def _project_metrics() -> dict[str, object]:
    return {
        "readiness_assessment": {
            "maturity_level": "research_platform_ready_for_field_calibration",
        }
    }


def _field_metrics() -> dict[str, object]:
    return {
        "data_origin": "synthetic",
        "readiness": {
            "interface_status": "template_ready_not_field_validated",
        },
    }

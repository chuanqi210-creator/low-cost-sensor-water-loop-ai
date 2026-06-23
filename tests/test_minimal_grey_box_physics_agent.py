from water_ai.agents.minimal_grey_box_physics_agent import MinimalGreyBoxPhysicsAgent


def test_minimal_grey_box_physics_agent_builds_physics_table() -> None:
    report = MinimalGreyBoxPhysicsAgent().run([])

    table = report.metrics["scenario_physics_table"]
    readiness = report.metrics["readiness"]

    assert len(table) >= 5
    assert readiness["scenario_count"] == len(table)
    assert all("pseudo_first_order_k_per_min" in row for row in table)
    assert all("mass_balance_residual" in row for row in table)
    assert all("byproduct_risk" in row for row in table)
    assert "synthetic" in readiness["grey_box_physics_status"]


def test_minimal_grey_box_physics_agent_flags_matrix_and_catalyst_physics_risks() -> None:
    report = MinimalGreyBoxPhysicsAgent().run([])

    rows = {row["scenario"]: row for row in report.metrics["scenario_physics_table"]}

    assert "matrix_inhibition_strong" in rows["matrix_shock"]["failure_modes"]
    assert "catalyst_decay_risk_high" in rows["catalyst_deactivation"]["failure_modes"]
    assert any(issue.issue_type == "field_physics_calibration_required" for issue in report.issues)


def test_minimal_grey_box_physics_agent_keeps_synthetic_prior_out_of_release_gate() -> None:
    report = MinimalGreyBoxPhysicsAgent().run([])

    readiness = report.metrics["readiness"]
    writeback = report.metrics["agent50_writeback"]

    assert readiness["can_update_soft_sensor_physics_prior"] is True
    assert readiness["can_write_to_release_gate"] is False
    assert "release_gate_policy" in writeback["blocked_writeback"]
    assert writeback["can_advance_governance_priority"] is True


def test_minimal_grey_box_physics_agent_can_become_field_candidate_without_release_gate() -> None:
    report = MinimalGreyBoxPhysicsAgent(
        evidence_stage="field_physics_calibration",
        field_calibration={
            "field_physics_coverage": 0.92,
            "max_field_residual": 0.08,
            "max_mass_balance_residual": 0.05,
        },
    ).run([])

    readiness = report.metrics["readiness"]

    assert readiness["field_ready"] is True
    assert readiness["can_write_to_actuator"] in {True, False}
    assert readiness["can_write_to_release_gate"] is False


def test_minimal_grey_box_physics_agent_consumes_guardrail_failure_boundaries() -> None:
    report = MinimalGreyBoxPhysicsAgent(
        control_guardrail_backpropagation_metrics=_guardrail_backpropagation_metrics()
    ).run([])

    readiness = report.metrics["readiness"]
    context = report.metrics["control_guardrail_backpropagation_context"]
    patch = report.metrics["guardrail_failure_boundary_patch"]

    assert readiness["agent53_guardrail_boundary_consumption_rate"] == 1.0
    assert readiness["can_update_guardrail_failure_boundaries"] is True
    assert context["backpropagation_ready"] is True
    assert len(patch) == 2
    assert {row["mechanism_family"] for row in patch} == {
        "catalyst_activity_proxy_uncertainty",
        "hydraulic_latency_and_storage_uncertainty",
    }
    assert readiness["can_write_to_release_gate"] is False


def _guardrail_backpropagation_metrics() -> dict[str, object]:
    return {
        "readiness": {
            "guardrail_backpropagation_status": (
                "synthetic_guardrail_backpropagation_ready_needs_field_replay_and_grey_box_calibration"
            ),
            "backpropagation_ready": True,
            "field_ready": False,
        },
        "coverage_metrics": {
            "resolved_case_count": 2,
        },
        "grey_box_patch": [
            {
                "mechanism_family": "catalyst_activity_proxy_uncertainty",
                "scenario": "catalyst_uncertain_low_proxy",
                "grey_box_boundary": ["catalyst activity needs proxy holdout"],
                "control_implication": "keep standby",
                "target_agent": "minimal_grey_box_physics_agent",
                "field_boundary": "field proxy labels required",
            },
            {
                "mechanism_family": "hydraulic_latency_and_storage_uncertainty",
                "scenario": "hydraulic_delay_violation",
                "grey_box_boundary": ["tank storage and latency required"],
                "control_implication": "prefer polishing gate",
                "target_agent": "minimal_grey_box_physics_agent",
                "field_boundary": "field hydraulic replay required",
            },
        ],
    }

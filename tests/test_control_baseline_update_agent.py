from water_ai.agents.control_baseline_update_agent import ControlBaselineUpdateAgent


def test_control_baseline_update_agent_writes_replan_trace_to_next_baseline() -> None:
    report = ControlBaselineUpdateAgent(
        replan_executed=True,
        replan_trace=_trace(),
        previous_baseline={"load_control_policy": {"protected_intake_fraction": 0.35}},
        baseline_version="baseline_v1",
    ).run([])

    updated = report.metrics["updated_baseline"]
    config = updated["online_control_config"]

    assert updated["update_required"] is True
    assert updated["baseline_version"] == "baseline_v1_replan"
    assert config["selected_queue_policy"]["policy_id"] == "high_risk_first"
    assert config["selected_portfolio"]["package_id"] == "resilience_bridge_portfolio"
    assert config["load_control_policy"]["protected_intake_fraction"] == 0.45
    assert not report.issues


def test_control_baseline_update_agent_keeps_previous_baseline_without_replan() -> None:
    previous = {"load_control_policy": {"protected_intake_fraction": 0.45}}

    report = ControlBaselineUpdateAgent(
        replan_executed=False,
        replan_trace={},
        previous_baseline=previous,
        baseline_version="baseline_v1",
    ).run([])

    updated = report.metrics["updated_baseline"]

    assert updated["update_required"] is False
    assert updated["online_control_config"] == previous
    assert "沿用" in report.recommendations[0]


def test_control_baseline_update_agent_flags_incomplete_writeback() -> None:
    trace = _trace()
    trace["adaptive_portfolio"]["budget_sequence"] = []

    report = ControlBaselineUpdateAgent(
        replan_executed=True,
        replan_trace=trace,
        baseline_version="baseline_v1",
    ).run([])

    assert report.issues
    assert report.issues[0].issue_type == "incomplete_writeback"


def _trace() -> dict[str, object]:
    return {
        "queue_planning": {
            "selected_policy": {"policy_id": "high_risk_first"},
        },
        "phased_implementation": {
            "readiness": {"estimated_ready_campaign": 2},
        },
        "implementation_stress_test": {
            "guardrails": {"max_transition_intake_fraction": 0.45},
        },
        "adaptive_portfolio": {
            "selected_portfolio": {"package_id": "resilience_bridge_portfolio"},
            "load_control_policy": {"protected_intake_fraction": 0.45},
            "budget_sequence": [
                {"order": 1, "budget_item": "外包低价值验证"},
                {"order": 2, "budget_item": "催化剂备用供应商"},
            ],
        },
    }

from water_ai.agents.adaptive_portfolio_agent import AdaptivePortfolioAgent


def test_adaptive_portfolio_agent_selects_resilience_bridge_for_combined_pressure() -> None:
    report = AdaptivePortfolioAgent(
        ranked_stress_scenarios=[
            {
                "scenario_id": "combined_delay_high_intake",
                "scenario_risk": 0.356,
                "catalyst_stockout_risk": 0.28,
                "validation_overload_risk": 0.4,
                "budget_gap": 0.25,
                "intake_pressure_multiplier": 1.25,
            },
            {
                "scenario_id": "acceptance_failure",
                "scenario_risk": 0.22,
            },
        ],
        guardrails={"max_transition_intake_fraction": 0.45},
        budget_limit_increment=1.2,
    ).run([])

    selected = report.metrics["selected_portfolio"]

    assert selected["package_id"] == "resilience_bridge_portfolio"
    assert "catalyst_delay" in selected["covered_signals"]
    assert "validation_ramp_delay" in selected["covered_signals"]
    assert report.metrics["load_control_policy"]["protected_intake_fraction"] == 0.45


def test_adaptive_portfolio_agent_selects_budget_package_for_budget_only_signal() -> None:
    report = AdaptivePortfolioAgent(
        ranked_stress_scenarios=[
            {
                "scenario_id": "budget_slow_release",
                "scenario_risk": 0.25,
                "budget_gap": 0.35,
                "intake_pressure_multiplier": 1.0,
            }
        ],
        guardrails={"max_transition_intake_fraction": 0.65},
        budget_limit_increment=0.8,
    ).run([])

    selected = report.metrics["selected_portfolio"]

    assert selected["package_id"] == "phased_budget_package"
    assert report.metrics["budget_sequence"][0]["budget_item"] == "验证能力批复"
    assert not report.issues


def test_adaptive_portfolio_agent_keeps_baseline_when_only_on_schedule() -> None:
    report = AdaptivePortfolioAgent(
        ranked_stress_scenarios=[
            {
                "scenario_id": "on_schedule",
                "scenario_risk": 0.0,
                "intake_pressure_multiplier": 1.0,
            }
        ],
        guardrails={"max_transition_intake_fraction": 0.65},
    ).run([])

    selected = report.metrics["selected_portfolio"]

    assert selected["package_id"] == "baseline_execution"
    assert selected["expected_risk_reduction"] == 0.0
    assert not report.issues

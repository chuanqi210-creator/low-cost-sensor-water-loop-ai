from water_ai.agents.online_project_control_agent import OnlineProjectControlAgent


def test_online_project_control_agent_replans_after_acceptance_failure() -> None:
    report = OnlineProjectControlAgent(
        selected_portfolio={"package_id": "resilience_bridge_portfolio"},
        budget_sequence=_budget_sequence(),
        load_control_policy={"protected_intake_fraction": 0.45},
        rolling_campaigns=[
            {
                "campaign_id": 0,
                "acceptance_passed": False,
                "success_rate": 0.88,
                "validation_staff_usage": 1.02,
                "time_budget_usage": 0.96,
                "catalyst_spares_remaining": 1,
                "oxidant_stock_units_remaining": 1.4,
                "intake_pressure_multiplier": 1.2,
                "budget_release_fraction": 0.7,
                "budget_released_items": [],
            }
        ],
    ).run([])

    state = report.metrics["current_control_state"]

    assert state["project_mode"] == "replan_and_protect"
    assert state["replan_required"]
    assert state["next_intake_fraction"] <= 0.35
    assert state["next_budget_item"] == "外包低价值验证"
    assert report.issues


def test_online_project_control_agent_ramps_up_after_two_stable_campaigns() -> None:
    report = OnlineProjectControlAgent(
        selected_portfolio={"package_id": "resilience_bridge_portfolio"},
        budget_sequence=_budget_sequence(),
        load_control_policy={"protected_intake_fraction": 0.45},
        rolling_campaigns=[
            {
                "campaign_id": 0,
                "acceptance_passed": True,
                "success_rate": 1.0,
                "validation_staff_usage": 0.70,
                "time_budget_usage": 0.72,
                "catalyst_spares_remaining": 2,
                "oxidant_stock_units_remaining": 1.6,
                "budget_released_items": ["外包低价值验证", "催化剂备用供应商"],
            },
            {
                "campaign_id": 1,
                "acceptance_passed": True,
                "success_rate": 1.0,
                "validation_staff_usage": 0.68,
                "time_budget_usage": 0.74,
                "catalyst_spares_remaining": 2,
                "oxidant_stock_units_remaining": 1.5,
                "budget_released_items": ["验证能力批复"],
            },
        ],
    ).run([])

    state = report.metrics["current_control_state"]

    assert state["project_mode"] == "controlled_ramp_up"
    assert state["stable_streak"] == 2
    assert state["next_intake_fraction"] > 0.45
    assert not state["replan_required"]
    assert not report.issues


def test_online_project_control_agent_prioritizes_catalyst_budget_when_stock_is_low() -> None:
    report = OnlineProjectControlAgent(
        selected_portfolio={"package_id": "resilience_bridge_portfolio"},
        budget_sequence=_budget_sequence(),
        load_control_policy={"protected_intake_fraction": 0.45},
        rolling_campaigns=[
            {
                "campaign_id": 0,
                "acceptance_passed": True,
                "success_rate": 1.0,
                "validation_staff_usage": 0.78,
                "time_budget_usage": 0.82,
                "catalyst_spares_remaining": 0,
                "oxidant_stock_units_remaining": 1.3,
                "budget_released_items": ["外包低价值验证"],
            }
        ],
    ).run([])

    state = report.metrics["current_control_state"]

    assert "catalyst_inventory" in state["dominant_signals"]
    assert state["next_budget_item"] == "催化剂备用供应商"
    assert state["next_intake_fraction"] == 0.45


def _budget_sequence() -> list[dict[str, object]]:
    return [
        {"order": 1, "budget_item": "外包低价值验证"},
        {"order": 2, "budget_item": "催化剂备用供应商"},
        {"order": 3, "budget_item": "验证能力批复"},
        {"order": 4, "budget_item": "催化剂库存批复"},
        {"order": 5, "budget_item": "氧化剂库存批复"},
    ]

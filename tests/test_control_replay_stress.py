from water_ai.control_replay_stress import ControlReplayCounterfactualStress


def test_control_replay_stress_improves_counterfactual_metrics_without_field_claim() -> None:
    result = _stress().build()
    metrics = result["counterfactual_metrics"]
    readiness = result["readiness"]

    assert metrics["baseline"]["joint_action_accuracy"] == 0.667
    assert metrics["observation_contract"]["joint_action_accuracy"] > metrics["baseline"]["joint_action_accuracy"]
    assert metrics["guardrail_candidate"]["joint_action_accuracy"] >= 0.9
    assert metrics["p95_reward_regret_delta_guardrail"] > 0
    assert readiness["control_replay_stress_status"] == "synthetic_counterfactual_stress_ready_needs_field_replay"
    assert readiness["can_write_to_actuator"] is False
    assert readiness["can_write_to_release_gate"] is False


def test_control_replay_stress_outputs_reward_prior_guardrails() -> None:
    result = _stress().build()
    patch = result["reward_prior_patch"]

    assert patch["patch_id"] == "R3_counterfactual_guardrail_reward_prior"
    assert len(patch["candidate_rules"]) == 2
    assert any(row["scenario"] == "catalyst_uncertain_low_proxy" for row in patch["triggered_by_cases"])
    assert any(row["scenario"] == "hydraulic_delay_violation" for row in patch["triggered_by_cases"])


def test_control_replay_stress_keeps_writeback_limited_to_priors_and_stress_suite() -> None:
    result = _stress().build()
    policy = result["writeback_policy"]

    assert "agent49_reward_prior_guardrail_candidate" in policy["allowed_writeback"]
    assert "agent52_counterfactual_stress_suite" in policy["allowed_writeback"]
    assert "actuator_policy" in policy["blocked_writeback"]
    assert "online_MARL_training" in policy["blocked_writeback"]
    assert result["next_refactor_action"]["action_id"] == (
        "R3b_agent49_reward_prior_patch_from_counterfactual_stress"
    )


def test_control_replay_stress_lists_field_replay_requirements() -> None:
    result = _stress().build()
    requirements = result["field_replay_requirements"]

    assert len(requirements) == 3
    assert requirements[0]["requirement_id"] == "R3_FV1_state_action_reward_replay"
    assert "tank_storage_margin" in requirements[1]["required_fields"]
    assert "proxy_holdout_label" in requirements[2]["required_fields"]


def _stress() -> ControlReplayCounterfactualStress:
    return ControlReplayCounterfactualStress(
        collaborative_control_metrics={},
        observation_contract_metrics={
            "readiness": {
                "budget_pass": True,
                "proxy_enhanced_weak_state_coverage": 0.58,
            }
        },
        replay_evaluation_metrics={
            "offline_evaluation_metrics": {"field_replay_coverage": 0.0},
            "replay_table": [
                _row("R0", "matrix_shock_visible", "J0_matrix_shock_equalize_and_recycle", "J0_matrix_shock_equalize_and_recycle"),
                _row("R1", "reaction_completion_lag", "J1_reaction_completion_recovery", "J1_reaction_completion_recovery"),
                _row(
                    "R2",
                    "catalyst_uncertain_low_proxy",
                    "J2_catalyst_protection_before_regeneration",
                    "J4_safe_low_cost_standby",
                    false_positive=True,
                    false_positive_cost=0.18,
                ),
                _row("R3", "polishing_release_risk", "J3_polishing_and_release_gate", "J3_polishing_and_release_gate"),
                _row("R4", "clean_but_low_field_evidence", "J4_safe_low_cost_standby", "J4_safe_low_cost_standby"),
                _row(
                    "R5",
                    "hydraulic_delay_violation",
                    "J0_matrix_shock_equalize_and_recycle",
                    "J3_polishing_and_release_gate",
                    unsafe=True,
                ),
            ],
        },
    )


def _row(
    case_id: str,
    scenario: str,
    policy: str,
    expert: str,
    *,
    false_positive: bool = False,
    false_positive_cost: float = 0.0,
    unsafe: bool = False,
) -> dict[str, object]:
    rewards = {
        "J0_matrix_shock_equalize_and_recycle": 0.50,
        "J1_reaction_completion_recovery": 0.52,
        "J2_catalyst_protection_before_regeneration": 0.43,
        "J3_polishing_and_release_gate": 0.62,
        "J4_safe_low_cost_standby": 0.61,
    }
    rewards[expert] = max(rewards.values())
    return {
        "batch_id": case_id,
        "scenario": scenario,
        "policy_action_id": policy,
        "expert_action_id": expert,
        "reward_by_action": rewards,
        "expert_reward": rewards[expert],
        "is_false_positive_protective_action": false_positive,
        "false_positive_action_cost": false_positive_cost,
        "unsafe_action_blocked": unsafe,
    }

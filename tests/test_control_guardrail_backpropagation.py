from water_ai.control_guardrail_backpropagation import ControlGuardrailBackpropagation


def test_guardrail_backpropagation_maps_resolved_cases_to_mechanism_and_field_needs() -> None:
    result = _backpropagation().build()
    coverage = result["coverage_metrics"]
    readiness = result["readiness"]

    assert coverage["resolved_case_count"] == 2
    assert coverage["resolved_case_to_mechanism_coverage"] == 1.0
    assert coverage["resolved_case_to_field_requirement_coverage"] == 1.0
    assert "proxy_holdout_label" in coverage["unique_field_replay_required_fields"]
    assert "tank_storage_margin" in coverage["unique_field_replay_required_fields"]
    assert readiness["guardrail_backpropagation_status"] == (
        "synthetic_guardrail_backpropagation_ready_needs_field_replay_and_grey_box_calibration"
    )
    assert readiness["can_write_to_actuator"] is False
    assert readiness["can_write_to_release_gate"] is False


def test_guardrail_backpropagation_outputs_grey_box_and_field_patches() -> None:
    result = _backpropagation().build()

    grey_box_patch = result["grey_box_patch"]
    field_patch = result["field_requirement_patch"]

    assert {row["mechanism_family"] for row in grey_box_patch} == {
        "catalyst_activity_proxy_uncertainty",
        "hydraulic_latency_and_storage_uncertainty",
    }
    assert all(row["target_agent"] == "minimal_grey_box_physics_agent" for row in grey_box_patch)
    assert all("claim_boundary" in row for row in field_patch)
    assert result["next_refactor_action"]["action_id"] == "R4b_patch_agent53_and_field_requirement_interfaces"


def test_guardrail_backpropagation_writeback_stays_away_from_actuators() -> None:
    result = _backpropagation().build()
    policy = result["writeback_policy"]

    assert "agent53_grey_box_failure_boundary_candidate" in policy["allowed_writeback"]
    assert "agent58_59_field_requirement_patch_candidate" in policy["allowed_writeback"]
    assert "actuator_policy" in policy["blocked_writeback"]
    assert "release_gate_policy" in policy["blocked_writeback"]
    assert policy["can_write_to_actuator"] is False


def _backpropagation() -> ControlGuardrailBackpropagation:
    return ControlGuardrailBackpropagation(
        replay_evaluation_metrics={
            "offline_evaluation_metrics": {
                "field_replay_coverage": 0.0,
            },
            "reward_diagnostics": {
                "guardrail_resolved_cases": [
                    {
                        "batch_id": "R2",
                        "scenario": "catalyst_uncertain_low_proxy",
                        "baseline_policy_action_id": "J2_catalyst_protection_before_regeneration",
                        "guardrail_aware_policy_action_id": "J4_safe_low_cost_standby",
                        "expert_action_id": "J4_safe_low_cost_standby",
                        "guardrail_source_rule_id": "R3G1_catalyst_uncertain_requires_standby_or_human_review",
                        "reward_regret_delta": 0.177,
                    },
                    {
                        "batch_id": "R5",
                        "scenario": "hydraulic_delay_violation",
                        "baseline_policy_action_id": "J0_matrix_shock_equalize_and_recycle",
                        "guardrail_aware_policy_action_id": "J3_polishing_and_release_gate",
                        "expert_action_id": "J3_polishing_and_release_gate",
                        "guardrail_source_rule_id": "R3G2_hydraulic_delay_unknown_blocks_recycle",
                        "reward_regret_delta": 0.153,
                    },
                ]
            },
        },
        grey_box_physics_metrics={},
        field_validation_alignment_metrics={},
        claim_specific_package_metrics={},
    )

from water_ai.real_field_package_acceptance_gate import RealFieldPackageAcceptanceGate


def test_real_field_package_acceptance_gate_blocks_current_synthetic_import() -> None:
    result = RealFieldPackageAcceptanceGate(
        field_replay_import_metrics=_import_metrics(origin="synthetic"),
        timestamped_replay_metrics={},
        field_replay_gate_metrics={},
        field_replay_evidence_chain_metrics=_evidence_chain_metrics(import_ready=False),
        soft_sensor_field_holdout_gate_metrics=_soft_gate_metrics(field_ready=False),
        claim_specific_package_metrics=_claim_metrics(field_pass=0.0),
        unified_field_evidence_gate_metrics=_unified_gate_metrics(field_pass=False),
    ).build()

    readiness = result["readiness"]

    assert readiness["real_field_package_acceptance_status"] == "real_field_package_acceptance_blocked_at_import"
    assert readiness["field_package_import_pass"] is False
    assert readiness["can_write_to_release_gate"] is False
    assert readiness["can_write_to_actuator"] is False
    assert result["next_refactor_action"]["action_id"] == "R7a_import_real_field_package_with_metadata_and_csv"
    assert result["minimum_real_field_package"]["metadata_required_values"]["data_origin"] == "field"
    assert "sensor_timeseries.csv" in result["minimum_real_field_package"]["csv_tables"]


def test_real_field_package_acceptance_gate_routes_replay_before_holdout() -> None:
    result = RealFieldPackageAcceptanceGate(
        field_replay_import_metrics=_import_metrics(origin="field"),
        timestamped_replay_metrics=_timestamped_metrics(field_ready=True),
        field_replay_gate_metrics=_replay_gate_metrics(ready=True),
        field_replay_evidence_chain_metrics=_evidence_chain_metrics(import_ready=True, chain_ready=True),
        multi_facility_replay_evaluation_metrics=_control_metrics(ready=True),
        soft_sensor_field_holdout_gate_metrics=_soft_gate_metrics(field_ready=False),
        claim_specific_package_metrics=_claim_metrics(field_pass=1.0),
        unified_field_evidence_gate_metrics=_unified_gate_metrics(field_pass=False),
    ).build()

    readiness = result["readiness"]

    assert readiness["field_package_import_pass"] is True
    assert readiness["field_replay_evidence_chain_pass"] is True
    assert readiness["multi_facility_control_promotion_pass"] is True
    assert readiness["soft_sensor_field_holdout_gate_pass"] is False
    assert readiness["real_field_package_acceptance_status"] == (
        "real_field_package_acceptance_blocked_at_soft_sensor_holdout"
    )
    assert result["next_refactor_action"]["action_id"] == "R7d_collect_soft_sensor_field_holdout_labels"


def test_real_field_package_acceptance_gate_blocks_control_candidate_when_agent52_or_catalyst_holdout_fails() -> None:
    result = RealFieldPackageAcceptanceGate(
        field_replay_import_metrics=_import_metrics(origin="field"),
        timestamped_replay_metrics=_timestamped_metrics(field_ready=True),
        field_replay_gate_metrics=_replay_gate_metrics(ready=True),
        field_replay_evidence_chain_metrics=_evidence_chain_metrics(import_ready=True, chain_ready=True),
        multi_facility_replay_evaluation_metrics=_control_metrics(ready=False),
        soft_sensor_field_holdout_gate_metrics=_soft_gate_metrics(field_ready=True),
        claim_specific_package_metrics=_claim_metrics(field_pass=1.0),
        unified_field_evidence_gate_metrics=_unified_gate_metrics(field_pass=True),
    ).build()

    readiness = result["readiness"]
    failed = set(readiness["failed_stage_ids"])

    assert readiness["real_field_package_acceptance_status"] == (
        "real_field_package_acceptance_blocked_at_multi_facility_control_gate"
    )
    assert readiness["multi_facility_control_promotion_pass"] is False
    assert readiness["catalyst_proxy_field_validation_pass"] is False
    assert readiness["can_emit_protective_control_candidate"] is False
    assert "R7S4b_multi_facility_control_promotion" in failed
    assert result["next_refactor_action"]["action_id"] == (
        "R7c_validate_agent49_52_control_replay_and_agent51_catalyst_holdout"
    )


def test_real_field_package_acceptance_gate_ready_still_requires_human_review() -> None:
    result = RealFieldPackageAcceptanceGate(
        field_replay_import_metrics=_import_metrics(origin="field"),
        timestamped_replay_metrics=_timestamped_metrics(field_ready=True),
        field_replay_gate_metrics=_replay_gate_metrics(ready=True),
        field_replay_evidence_chain_metrics=_evidence_chain_metrics(import_ready=True, chain_ready=True),
        multi_facility_replay_evaluation_metrics=_control_metrics(ready=True),
        soft_sensor_field_holdout_gate_metrics=_soft_gate_metrics(field_ready=True),
        claim_specific_package_metrics=_claim_metrics(field_pass=1.0),
        unified_field_evidence_gate_metrics=_unified_gate_metrics(field_pass=True),
    ).build()

    readiness = result["readiness"]
    policy = result["writeback_policy"]

    assert readiness["real_field_package_acceptance_status"] == "real_field_package_acceptance_ready_for_human_review"
    assert readiness["can_emit_field_supported_claim_candidate"] is True
    assert readiness["can_emit_protective_control_candidate"] is True
    assert readiness["can_emit_release_gate_calibration_candidate"] is True
    assert readiness["can_write_to_release_gate"] is False
    assert "automatic_release_gate_policy" in policy["blocked_writeback"]
    assert result["next_refactor_action"]["action_id"] == "R7g_human_review_before_field_supported_upgrade"


def _import_metrics(*, origin: str) -> dict[str, object]:
    ready = origin == "field"
    return {
        "readiness": {
            "field_replay_import_status": (
                "field_replay_import_ready_for_timestamped_replay"
                if ready
                else "field_replay_import_blocked_non_field_origin"
            ),
            "accepted_data_origin": origin if ready else "blocked",
            "accepted_table_count": 4,
            "total_table_count": 4,
            "can_pass_to_timestamped_replay": ready,
            "can_pass_to_g6": ready,
            "can_write_to_protective_control": False,
        }
    }


def _timestamped_metrics(*, field_ready: bool) -> dict[str, object]:
    return {
        "readiness": {
            "timestamped_replay_status": (
                "field_timestamped_replay_ready_for_fast_proxy_calibration"
                if field_ready
                else "synthetic_timestamp_schema_ready_needs_field_replay"
            ),
            "can_calibrate_fast_proxy": field_ready,
            "timestamp_coverage": 1.0,
        },
        "replay_metrics": {
            "proxy_precision": 0.92,
            "proxy_recall": 0.91,
        },
    }


def _replay_gate_metrics(*, ready: bool) -> dict[str, object]:
    return {
        "readiness": {
            "field_replay_gate_status": (
                "field_fast_proxy_protective_control_gate_ready" if ready else "synthetic_replay_gate_blocked"
            ),
            "can_write_to_protective_control": ready,
            "can_write_to_release_gate": False,
            "accepted_gate_count": 8 if ready else 7,
            "total_gate_count": 8,
            "failed_gate_ids": [] if ready else ["G6_1_field_origin"],
        }
    }


def _evidence_chain_metrics(*, import_ready: bool, chain_ready: bool = False) -> dict[str, object]:
    return {
        "readiness": {
            "field_replay_evidence_chain_status": (
                "field_replay_protective_writeback_candidate_ready"
                if chain_ready
                else "field_replay_evidence_chain_blocked_at_import"
            ),
            "import_ready": import_ready,
            "timestamped_replay_ready": chain_ready,
            "g6_ready": chain_ready,
            "can_emit_protective_writeback_candidate": chain_ready,
            "can_write_to_release_gate": False,
        }
    }


def _soft_gate_metrics(*, field_ready: bool) -> dict[str, object]:
    return {
        "readiness": {
            "soft_sensor_field_holdout_gate_status": (
                "soft_sensor_field_holdout_release_candidate_ready"
                if field_ready
                else "soft_sensor_release_gate_blocked_non_field_holdout"
            ),
            "passed_check_count": 7 if field_ready else 5,
            "total_check_count": 7,
            "failed_check_ids": [] if field_ready else ["SFG0_field_holdout_origin"],
            "can_write_to_release_gate": field_ready,
        }
    }


def _control_metrics(*, ready: bool) -> dict[str, object]:
    return {
        "readiness": {
            "replay_evaluation_status": (
                "field_replay_evaluation_candidate_ready"
                if ready
                else "synthetic_replay_evaluation_ready_needs_field_replay"
            ),
            "field_ready": ready,
            "catalyst_proxy_field_validation_pass": ready,
            "catalyst_guardrail_mode": (
                "agent51_field_validated_human_reviewed_relaxation_candidate"
                if ready
                else "agent51_holdout_coverage_gaps_keep_catalyst_guardrail"
            ),
            "can_write_to_actuator": ready,
        },
        "offline_evaluation_metrics": {
            "field_replay_coverage": 0.90 if ready else 0.0,
            "joint_action_accuracy": 0.93 if ready else 0.667,
            "mean_reward_regret": 0.05 if ready else 0.055,
            "catalyst_proxy_summary_status": (
                "field_proxy_holdout_validation_passed"
                if ready
                else "field_proxy_holdout_coverage_gaps"
            ),
            "catalyst_proxy_scoreable_batch_count": 4 if ready else 0,
            "catalyst_proxy_field_validation_pass": ready,
            "catalyst_guardrail_mode": (
                "agent51_field_validated_human_reviewed_relaxation_candidate"
                if ready
                else "agent51_holdout_coverage_gaps_keep_catalyst_guardrail"
            ),
        },
    }


def _claim_metrics(*, field_pass: float) -> dict[str, object]:
    return {
        "readiness": {
            "claim_specific_package_status": "claim_specific_package_ready_needs_real_data_and_source_basis_detail",
            "source_basis_completion_rate": 1.0,
            "minimal_field_package_schema_pass_rate": 1.0,
            "minimal_field_package_field_pass_rate": field_pass,
        }
    }


def _unified_gate_metrics(*, field_pass: bool) -> dict[str, object]:
    return {
        "readiness": {
            "unified_field_evidence_gate_status": (
                "unified_gate_field_claim_candidate_ready"
                if field_pass
                else "unified_gate_ready_blocking_field_claim_upgrade"
            ),
            "field_import_pass": field_pass,
            "field_replay_evidence_chain_pass": field_pass,
            "soft_sensor_field_holdout_gate_pass": field_pass,
            "can_emit_field_claim_upgrade": field_pass,
            "can_write_to_release_gate": False,
            "field_supported_edge_ratio": 0.8 if field_pass else 0.0,
        }
    }

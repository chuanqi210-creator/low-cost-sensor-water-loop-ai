from water_ai.agents.sensor_network_sparse_placement_agent import SensorNetworkSparsePlacementAgent
from water_ai.core_interface_consolidation import (
    build_core_interface_consolidation,
    core_interface_consolidation_report_md,
)
from water_ai.field_control_replay_package import (
    ACTUATOR_TABLE,
    EXPERT_LABEL_TABLE,
    REWARD_TABLE,
    TRANSITION_TABLE,
    UNSAFE_TABLE,
    build_field_control_replay_package_preflight,
)
from water_ai.sparse_topology_installability_package import (
    build_sparse_topology_installability_package_preflight,
)


def test_core_interface_consolidation_builds_three_facades_without_field_claims() -> None:
    consolidation = build_core_interface_consolidation(
        agent48_metrics=_agent48_metrics(),
        field_control_replay_preflight=build_field_control_replay_package_preflight(),
        sparse_topology_installability_preflight=build_sparse_topology_installability_package_preflight(),
        grey_box_collection_work_order=_grey_box_work_order(),
        external_package_acquisition_maturity_gate=_maturity_gate(),
    )

    assert consolidation["consolidation_id"] == "R8u158_core_interface_consolidation_facade"
    assert consolidation["facade_count"] == 3
    assert consolidation["boundary"]["can_generate_field_evidence"] is False
    assert consolidation["boundary"]["can_write_to_actuator"] is False
    assert consolidation["boundary"]["can_write_to_release_gate"] is False
    assert consolidation["priority_decision"]["top_external_action_env_var"] == "GREY_BOX_CALIBRATION_PACKAGE_DIR"
    assert consolidation["priority_decision"]["new_agent_recommendation"] == "do_not_add_linear_agent"


def test_external_package_lifecycle_facade_keeps_waiting_packages_and_next_actions() -> None:
    consolidation = build_core_interface_consolidation(
        agent48_metrics=_agent48_metrics(),
        field_control_replay_preflight=build_field_control_replay_package_preflight(),
        sparse_topology_installability_preflight=build_sparse_topology_installability_package_preflight(),
        grey_box_collection_work_order=_grey_box_work_order(),
        grey_box_submission_readiness_gate=_grey_box_submission_readiness_gate(),
        external_package_acquisition_maturity_gate=_maturity_gate(),
    )
    lifecycle = consolidation["facades"]["external_package_lifecycle"]
    rows = {row["package_key"]: row for row in lifecycle["package_lifecycle_rows"]}

    assert lifecycle["facade_status"] == "external_package_lifecycle_waiting_for_field_packages"
    assert lifecycle["ready_package_count"] == 0
    assert rows["grey_box_calibration"]["source_env_var"] == "GREY_BOX_CALIBRATION_PACKAGE_DIR"
    assert rows["grey_box_calibration"]["downstream_consumer"] == "Agent53_minimal_grey_box_physics"
    assert (
        rows["grey_box_calibration"]["submission_readiness_gate_status"]
        == "grey_box_submission_readiness_waiting_for_external_package"
    )
    assert rows["grey_box_calibration"]["submission_readiness_score"] == 0.143
    assert rows["grey_box_calibration"]["submission_highest_priority_gap_type"] == "missing_external_package"
    assert rows["grey_box_calibration"]["submission_highest_priority_gap_table"] == "all_required_tables"
    assert rows["grey_box_calibration"]["submission_missing_table_count"] == 5
    assert rows["grey_box_calibration"]["submission_missing_tables"] == [
        "batch_inlet_outlet_lab",
        "hydraulic_rtd_or_tracer",
        "oxidant_dose_residual_log",
        "catalyst_age_regeneration_log",
        "byproduct_panel",
    ]
    assert rows["grey_box_calibration"]["submission_source_env_var"] == "GREY_BOX_CALIBRATION_PACKAGE_DIR"
    assert rows["grey_box_calibration"]["can_submit_to_agent53_field_calibration"] is False
    assert rows["grey_box_calibration"]["can_submit_to_agent53_field_candidate"] is False
    assert rows["field_control_replay"]["downstream_consumer"] == "Agent49_52_offline_control_replay"
    assert rows["sparse_topology_installability"]["downstream_consumer"] == "Agent48_54_layout_holdout"
    assert all(row["can_generate_field_evidence"] is False for row in rows.values())
    assert all(row["can_write_to_release_gate"] is False for row in rows.values())


def test_sparse_layout_coupling_benchmark_scores_all_agent48_strategies_and_keeps_blockers() -> None:
    consolidation = build_core_interface_consolidation(
        agent48_metrics=_agent48_metrics(),
        field_control_replay_preflight=build_field_control_replay_package_preflight(),
        sparse_topology_installability_preflight=build_sparse_topology_installability_package_preflight(),
        grey_box_collection_work_order=_grey_box_work_order(),
        external_package_acquisition_maturity_gate=_maturity_gate(),
    )
    benchmark = consolidation["facades"]["sparse_layout_soft_sensor_coupling_benchmark"]
    rows = benchmark["layout_benchmark_rows"]

    assert benchmark["benchmark_status"] == "synthetic_layout_coupling_benchmark_ready_needs_field_topology_missingness_labels"
    assert len(rows) >= 6
    assert rows[0]["layout_coupling_score"] >= rows[-1]["layout_coupling_score"]
    assert all("masked_state_support_mean" in row for row in rows)
    assert all("catalyst_bed_uv_orp_missing" in row["missingness_stress_scores"] for row in rows)
    assert all(row["can_finalize_field_deployment"] is False for row in rows)
    assert all(row["can_relax_agent49"] is False for row in rows)
    assert "cannot claim field soft-sensor accuracy" in benchmark["cannot_claim"]
    assert "catalyst_activity" in benchmark["hard_blockers"]


def test_field_control_replay_crosswalk_maps_five_tables_to_agent52_schema() -> None:
    consolidation = build_core_interface_consolidation(
        agent48_metrics=_agent48_metrics(),
        field_control_replay_preflight=build_field_control_replay_package_preflight(),
        sparse_topology_installability_preflight=build_sparse_topology_installability_package_preflight(),
        grey_box_collection_work_order=_grey_box_work_order(),
        external_package_acquisition_maturity_gate=_maturity_gate(),
    )
    crosswalk = consolidation["facades"]["field_control_replay_crosswalk"]
    table_rows = {row["source_table"]: row for row in crosswalk["table_to_replay_schema_rows"]}

    assert crosswalk["crosswalk_status"] == "field_control_replay_crosswalk_ready_waiting_for_FIELD_CONTROL_REPLAY_PACKAGE_DIR"
    assert set(table_rows) == {
        TRANSITION_TABLE,
        REWARD_TABLE,
        EXPERT_LABEL_TABLE,
        ACTUATOR_TABLE,
        UNSAFE_TABLE,
    }
    assert "state_vector_ref" in table_rows[TRANSITION_TABLE]["source_columns"]
    assert "reward_components" in table_rows[REWARD_TABLE]["agent52_target_fields"]
    assert "human_review_required" in table_rows[UNSAFE_TABLE]["agent52_target_fields"]
    assert "guardrail_aware_policy" in crosswalk["policy_candidate_columns"]
    assert crosswalk["release_gate_requirements"]["can_authorize_policy_promotion"] is False
    assert crosswalk["release_gate_requirements"]["can_write_to_actuator"] is False
    assert crosswalk["release_gate_requirements"]["can_write_to_release_gate"] is False


def test_core_interface_consolidation_report_mentions_facades_and_boundaries() -> None:
    consolidation = build_core_interface_consolidation(
        agent48_metrics=_agent48_metrics(),
        field_control_replay_preflight=build_field_control_replay_package_preflight(),
        sparse_topology_installability_preflight=build_sparse_topology_installability_package_preflight(),
        grey_box_collection_work_order=_grey_box_work_order(),
        grey_box_submission_readiness_gate=_grey_box_submission_readiness_gate(),
        external_package_acquisition_maturity_gate=_maturity_gate(),
    )

    report = core_interface_consolidation_report_md(consolidation)

    assert "Core Interface Consolidation Facade" in report
    assert "external_package_lifecycle" in report
    assert "sparse_layout_soft_sensor_coupling_benchmark" in report
    assert "field_control_replay_crosswalk" in report
    assert "submission readiness" in report
    assert "grey_box_submission_readiness_waiting_for_external_package" in report
    assert "0.143" in report
    assert "cannot generate field evidence" in report
    assert "GREY_BOX_CALIBRATION_PACKAGE_DIR" in report


def _agent48_metrics() -> dict[str, object]:
    return SensorNetworkSparsePlacementAgent(max_sensors=6, budget_limit=5.8).run([]).metrics


def _grey_box_work_order() -> dict[str, object]:
    return {
        "work_order_id": "R8u157_grey_box_calibration_collection_work_order",
        "source_env_var": "GREY_BOX_CALIBRATION_PACKAGE_DIR",
        "work_order_status": "grey_box_calibration_collection_work_order_waiting_for_external_package",
        "package_status": "grey_box_calibration_package_waiting_for_GREY_BOX_CALIBRATION_PACKAGE_DIR",
        "minimum_matched_batch_count": 3,
        "matched_batch_count": 0,
        "next_operator_action": "fill_grey_box_calibration_package_template_and_set_GREY_BOX_CALIBRATION_PACKAGE_DIR",
        "can_generate_field_evidence": False,
        "can_resume_model_chain": False,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
    }


def _maturity_gate() -> dict[str, object]:
    return {
        "gate_status": "external_package_acquisition_interfaces_ready_waiting_for_field_packages",
        "field_package_ready_rate": 0.0,
        "ready_package_count": 0,
        "waiting_package_count": 5,
        "next_operator_source_env_var": "GREY_BOX_CALIBRATION_PACKAGE_DIR",
        "next_operator_action": "complete_grey_box_calibration_package_preflight_before_building_field_calibration_summary",
        "can_generate_field_evidence": False,
        "can_resume_model_chain": False,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
    }


def _grey_box_submission_readiness_gate() -> dict[str, object]:
    return {
        "gate_id": "R8u160_grey_box_submission_readiness_gate",
        "gate_status": "grey_box_submission_readiness_waiting_for_external_package",
        "readiness_score": 0.143,
        "highest_priority_gap": {
            "gap_type": "missing_external_package",
            "table": "all_required_tables",
            "missing_table_count": 5,
            "missing_tables": [
                "batch_inlet_outlet_lab",
                "hydraulic_rtd_or_tracer",
                "oxidant_dose_residual_log",
                "catalyst_age_regeneration_log",
                "byproduct_panel",
            ],
            "source_env_var": "GREY_BOX_CALIBRATION_PACKAGE_DIR",
        },
        "can_submit_to_agent53_field_calibration": False,
        "can_submit_to_agent53_field_candidate": False,
        "can_generate_field_evidence": False,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
    }

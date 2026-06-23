from water_ai.agents.data_quality_agent import DataQualityAgent
from water_ai.agents.sensor_network_sparse_placement_agent import SensorNetworkSparsePlacementAgent
from water_ai.agents.soft_sensor_agent import SoftSensorAgent
from water_ai.soft_sensor_model import hydraulic_path_feature_values
from water_ai.simulation import generate_low_cost_sensor_stream


def test_soft_sensor_estimates_bounded_states() -> None:
    readings = generate_low_cost_sensor_stream(n=72, seed=7, inject_faults=True)
    dq_report = DataQualityAgent().run(readings)
    report = SoftSensorAgent(data_quality_report=dq_report).run(readings)

    state = report.metrics["state_estimate"]
    for key in [
        "pollutant_residual_risk",
        "reaction_completion",
        "oxidant_remaining",
        "catalyst_activity",
        "matrix_interference",
        "byproduct_risk",
        "offline_validation_confidence",
        "offline_residual_proxy",
        "hydraulic_confidence",
        "sensor_confidence",
        "compliance_probability",
        "recycle_gain",
        "release_readiness",
        "soft_sensor_uncertainty",
        "ood_risk",
        "model_heuristic_disagreement",
        "prediction_interval_width",
    ]:
        assert 0.0 <= state[key] <= 1.0

    assert state["sensor_confidence"] < 1.0
    assert state["release_readiness"] <= state["compliance_probability"]
    assert "release_blocked_by_uncertainty" in {issue.issue_type for issue in report.issues}
    assert len(report.metrics["timeseries"]) == len(readings)
    assert "pollutant_residual_risk_abs_error" in report.metrics["synthetic_truth_validation"]
    assert report.metrics["uncertainty"]["prediction_interval_90"]
    assert report.metrics["uncertainty"]["evidence_stage"] == "synthetic_internal_uncertainty_not_field_calibrated"


def test_soft_sensor_risk_decreases_on_clean_stream() -> None:
    readings = generate_low_cost_sensor_stream(n=72, seed=7, inject_faults=False)
    report = SoftSensorAgent().run(readings)
    timeseries = report.metrics["timeseries"]

    assert timeseries[-1]["pollutant_residual_risk"] < timeseries[0]["pollutant_residual_risk"]
    assert timeseries[-1]["reaction_completion"] > timeseries[0]["reaction_completion"]


def test_soft_sensor_uses_training_path_prior_without_layout() -> None:
    values = hydraulic_path_feature_values()

    assert values["hydraulic_path_coverage_rate"] == 1.0
    assert values["direct_hydraulic_path_coverage_rate"] == 0.833333
    assert values["proxy_hydraulic_path_coverage_rate"] == 0.166667
    assert values["recirculation_loop_observed_flag"] == 1.0
    assert values["low_frequency_time_buffer_observed_flag"] == 1.0

    readings = generate_low_cost_sensor_stream(n=72, seed=7, inject_faults=False)
    report = SoftSensorAgent().run(readings)
    context = report.metrics["layout_context"]

    assert context["layout_status"] == "no_layout_interface"
    assert context["hydraulic_path_feature_source"] == "legacy_training_prior_not_field_layout"
    assert context["hydraulic_path_feature_values"] == values


def test_soft_sensor_uses_window_relative_time_for_model_domain() -> None:
    readings = generate_low_cost_sensor_stream(n=72, seed=7, inject_faults=False)
    shifted = [
        type(reading)(
            timestamp_min=reading.timestamp_min + 360,
            cycle_id=reading.cycle_id,
            values=reading.values,
            ground_truth_faults=reading.ground_truth_faults,
            ground_truth_state=reading.ground_truth_state,
        )
        for reading in readings
    ]

    report = SoftSensorAgent().run(shifted)

    assert all(item["feature"] != "timestamp_min" for item in report.metrics["uncertainty"]["ood_features"])


def test_soft_sensor_flags_out_of_domain_uncertainty() -> None:
    readings = generate_low_cost_sensor_stream(n=72, seed=7, inject_faults=False)
    last = readings[-1]
    readings[-1] = type(last)(
        timestamp_min=last.timestamp_min,
        cycle_id=24,
        values={**last.values, "UV254_abs": 8.0, "EC_uScm": 26000.0},
        ground_truth_faults=last.ground_truth_faults,
        ground_truth_state=last.ground_truth_state,
    )

    report = SoftSensorAgent().run(readings)

    assert report.metrics["state_estimate"]["ood_risk"] > 0
    assert report.metrics["uncertainty"]["ood_features"]
    assert any(issue.issue_type == "soft_sensor_ood_risk" for issue in report.issues)


def test_soft_sensor_accepts_node_modality_layout_context() -> None:
    readings = generate_low_cost_sensor_stream(n=72, seed=7, inject_faults=False)
    layout = SensorNetworkSparsePlacementAgent(max_sensors=6, budget_limit=5.8).run([]).metrics["soft_sensor_interface"]

    report = SoftSensorAgent(sensor_layout_interface=layout).run(readings)

    context = report.metrics["layout_context"]
    uncertainty = report.metrics["uncertainty"]

    assert context["layout_id"] == layout["layout_id"]
    assert context["mask_shape"] == layout["missingness_mask_contract"]["mask_shape"]
    assert context["layout_status"] == "global_modality_fallback_used_for_layout"
    assert context["requires_field_node_values"] is True
    assert context["hydraulic_path_feature_values"]["hydraulic_path_coverage_rate"] == 1.0
    assert context["hydraulic_path_feature_values"]["recirculation_loop_observed_flag"] == 1.0
    assert context["hydraulic_path_feature_values"]["release_endpoint_label_missing_flag"] == 1.0
    assert context["hydraulic_path_contract"]["contract_status"] == "hydraulic_path_contract_ready_needs_field_topology_and_release_endpoint"
    assert uncertainty["node_specific_gap"] > 0
    assert "layout_missingness_penalty" in uncertainty


def test_soft_sensor_consumes_grey_box_physics_prior() -> None:
    readings = generate_low_cost_sensor_stream(n=72, seed=7, inject_faults=False)
    grey_box_metrics = {
        "scenario_physics_table": [
            {"grey_box_residual": 0.18, "byproduct_risk": 0.62},
            {"grey_box_residual": 0.08, "byproduct_risk": 0.38},
        ],
        "readiness": {
            "grey_box_physics_status": "synthetic_grey_box_physics_prior_ready_needs_field_calibration",
            "synthetic_prior_ready": True,
            "can_update_soft_sensor_physics_prior": True,
            "mean_grey_box_residual": 0.11,
            "max_byproduct_risk": 0.62,
            "field_ready": False,
        },
    }

    report = SoftSensorAgent(grey_box_physics_metrics=grey_box_metrics).run(readings)

    state = report.metrics["state_estimate"]
    context = report.metrics["grey_box_prior_context"]
    uncertainty = report.metrics["uncertainty"]

    assert context["can_use_as_soft_sensor_prior"] is True
    assert state["grey_box_residual_prior"] == 0.18
    assert state["grey_box_byproduct_prior"] == 0.62
    assert uncertainty["grey_box_residual_penalty"] == 0.18
    assert uncertainty["grey_box_status"] == "synthetic_grey_box_physics_prior_ready_needs_field_calibration"

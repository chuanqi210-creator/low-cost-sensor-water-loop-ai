from water_ai.agents.sensitivity_analysis_agent import SensitivityAnalysisAgent
from water_ai.sensor_economics import compute_sensor_economics


def test_sensitivity_agent_ranks_stable_low_cost_design() -> None:
    evaluations = [
        {
            "design_id": "full",
            "description": "full",
            "disabled_sensors": [],
            "observation_window_min": 24,
            "sampling_interval_min": 1,
            "sensor_cost_index": 1.0,
            "scenario": "oxidant_limitation",
            "success_rate": 1.0,
            "mean_steps": 3.0,
            "mean_total_elapsed_min": 160.0,
            "mean_cost": 1.0,
            "mean_energy": 0.7,
        },
        {
            "design_id": "lean",
            "description": "lean",
            "disabled_sensors": ["UV254_abs"],
            "observation_window_min": 48,
            "sampling_interval_min": 3,
            "sensor_cost_index": 0.6,
            "scenario": "oxidant_limitation",
            "success_rate": 1.0,
            "mean_steps": 3.0,
            "mean_total_elapsed_min": 175.0,
            "mean_cost": 0.85,
            "mean_energy": 0.62,
        },
        {
            "design_id": "too_sparse",
            "description": "too sparse",
            "disabled_sensors": ["UV254_abs", "flow_Lmin"],
            "observation_window_min": 60,
            "sampling_interval_min": 5,
            "sensor_cost_index": 0.4,
            "scenario": "oxidant_limitation",
            "success_rate": 0.7,
            "mean_steps": 5.0,
            "mean_total_elapsed_min": 260.0,
            "mean_cost": 0.7,
            "mean_energy": 0.55,
        },
    ]
    report = SensitivityAnalysisAgent(evaluations=evaluations).run([])
    ranked = report.metrics["ranked_designs"]

    assert ranked[0]["design_id"] == "lean"
    assert any(issue.issue_type == "unstable_design" for issue in report.issues)
    assert report.recommendations


def test_sensitivity_agent_carries_sensor_economics() -> None:
    economics = compute_sensor_economics(
        disabled_sensors=[],
        sampling_interval_min=3,
        observation_window_min=36,
    )
    evaluations = [
        {
            "design_id": "full_36min_3min",
            "description": "full slow",
            "disabled_sensors": [],
            "observation_window_min": 36,
            "sampling_interval_min": 3,
            "sensor_cost_index": economics["engineering_cost_index"],
            "sensor_economics": economics,
            "scenario": "sensor_faults",
            "success_rate": 1.0,
            "mean_steps": 2.0,
            "mean_total_elapsed_min": 112.0,
            "mean_cost": 0.4,
            "mean_energy": 0.3,
        }
    ]

    report = SensitivityAnalysisAgent(evaluations=evaluations).run([])
    top = report.metrics["ranked_designs"][0]

    assert top["purchase_cost_cny"] == economics["purchase_cost_cny"]
    assert top["calibration_hours_per_month"] == economics["calibration_hours_per_month"]
    assert "月校准" in report.recommendations[0]

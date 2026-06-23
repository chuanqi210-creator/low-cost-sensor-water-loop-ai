from water_ai.robustness import evaluate_closed_loop_robustness


def test_closed_loop_robustness_smoke() -> None:
    result = evaluate_closed_loop_robustness(seeds=range(3), max_steps=6)
    summaries = {item["scenario"]: item for item in result["scenario_summaries"]}

    assert summaries["sensor_faults"]["success_rate"] == 1.0
    assert summaries["oxidant_limitation"]["success_rate"] == 1.0
    assert summaries["reaction_time_insufficient"]["success_rate"] == 1.0
    assert summaries["catalyst_deactivation"]["success_rate"] == 1.0
    assert summaries["matrix_shock"]["success_rate"] == 1.0

from water_ai.agents.data_quality_agent import DataQualityAgent
from water_ai.agents.soft_sensor_agent import SoftSensorAgent
from water_ai.process_dynamics import apply_actions_to_process_state, generate_sensor_stream_from_process_state, initial_process_state


def test_hold_for_validation_generates_delayed_offline_proxy() -> None:
    state = initial_process_state("reaction_time_insufficient")
    next_state = apply_actions_to_process_state(
        state,
        [
            {
                "action_id": "hold_for_validation",
                "parameters": {"hold_min": 24, "validation_delay_min": 12},
            }
        ],
    )

    assert next_state is not None
    assert next_state.elapsed_min == 36
    assert next_state.offline_validation_confidence > 0.0
    assert next_state.offline_validation_age_min == 0

    readings = generate_sensor_stream_from_process_state(next_state, n=24, seed=7)
    assert any("offline_residual_proxy" in reading.values for reading in readings)


def test_soft_sensor_uses_offline_validation_evidence() -> None:
    state = initial_process_state("reaction_time_insufficient")
    next_state = apply_actions_to_process_state(
        state,
        [
            {
                "action_id": "hold_for_validation",
                "parameters": {"hold_min": 24, "validation_delay_min": 12},
            }
        ],
    )
    assert next_state is not None
    readings = generate_sensor_stream_from_process_state(next_state, n=24, seed=7)
    dq_report = DataQualityAgent().run(readings)
    report = SoftSensorAgent(data_quality_report=dq_report).run(readings)
    state_estimate = report.metrics["state_estimate"]

    assert state_estimate["offline_validation_confidence"] > 0.0
    assert 0.0 <= state_estimate["offline_residual_proxy"] <= 1.0

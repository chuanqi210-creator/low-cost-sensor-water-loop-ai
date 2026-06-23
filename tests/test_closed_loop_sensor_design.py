from water_ai.closed_loop import _apply_sensor_design, run_closed_loop_episode
from water_ai.process_dynamics import generate_sensor_stream_from_process_state, initial_process_state


def test_closed_loop_degrades_safely_with_sparse_sampling_and_missing_uv() -> None:
    steps = run_closed_loop_episode(
        initial_scenario="reaction_time_insufficient",
        max_steps=5,
        observation_window_min=48,
        sampling_interval_min=3,
        disabled_sensors={"UV254_abs"},
        seed=7,
    )

    assert steps
    assert "release" not in steps[0].final_actions
    assert "release" in steps[0].blocked_actions


def test_sensor_design_noise_is_reproducible() -> None:
    readings = generate_sensor_stream_from_process_state(initial_process_state("clean_release"), n=12, seed=7)
    clean = _apply_sensor_design(
        readings,
        sampling_interval_min=2,
        disabled_sensors=None,
        sensor_noise_multiplier=0.0,
    )
    noisy_a = _apply_sensor_design(
        readings,
        sampling_interval_min=2,
        disabled_sensors=None,
        sensor_noise_multiplier=1.0,
    )
    noisy_b = _apply_sensor_design(
        readings,
        sampling_interval_min=2,
        disabled_sensors=None,
        sensor_noise_multiplier=1.0,
    )

    assert noisy_a[0].values == noisy_b[0].values
    assert noisy_a[0].values["ORP_mV"] != clean[0].values["ORP_mV"]

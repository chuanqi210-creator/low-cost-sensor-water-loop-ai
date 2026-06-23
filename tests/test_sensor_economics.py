from water_ai.sensor_economics import compute_sensor_economics


def test_sensor_economics_accounts_for_sampling_and_disabled_channels() -> None:
    full_fast = compute_sensor_economics(
        disabled_sensors=[],
        sampling_interval_min=1,
        observation_window_min=24,
    )
    full_slow = compute_sensor_economics(
        disabled_sensors=[],
        sampling_interval_min=3,
        observation_window_min=36,
    )
    no_uv = compute_sensor_economics(
        disabled_sensors=["UV254_abs"],
        sampling_interval_min=3,
        observation_window_min=48,
    )

    assert full_slow["sampling_load_index"] < full_fast["sampling_load_index"]
    assert full_slow["engineering_cost_index"] < full_fast["engineering_cost_index"]
    assert no_uv["purchase_cost_cny"] < full_fast["purchase_cost_cny"]
    assert "UV254_abs" not in no_uv["enabled_sensors"]

from experiments.run_design_sensitivity import _cache_key, _is_contiguous, _with_sensor_economics


def test_design_sensitivity_cache_key_tracks_design_inputs() -> None:
    design = _with_sensor_economics(
        {
            "design_id": "full_36min_3min",
            "description": "full slow",
            "observation_window_min": 36,
            "sampling_interval_min": 3,
            "disabled_sensors": [],
            "sensor_noise_multiplier": 0.75,
        }
    )
    changed_design = {**design, "sampling_interval_min": 5}
    changed_noise = {**design, "sensor_noise_multiplier": 1.2}

    assert _cache_key(design=design, seeds=[0, 1, 2]) == _cache_key(design=design, seeds=[0, 1, 2])
    assert _cache_key(design=design, seeds=[0, 1, 2]) != _cache_key(design=changed_design, seeds=[0, 1, 2])
    assert _cache_key(design=design, seeds=[0, 1, 2]) != _cache_key(design=changed_noise, seeds=[0, 1, 2])
    assert _cache_key(design=design, seeds=[0, 1, 2]) != _cache_key(design=design, seeds=[0, 1, 3])


def test_design_sensitivity_detects_contiguous_seed_ranges() -> None:
    assert _is_contiguous([0, 1, 2, 3])
    assert not _is_contiguous([0, 2, 3])

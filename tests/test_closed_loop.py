from water_ai.closed_loop import run_closed_loop_episode


def test_sensor_faults_episode_reaches_release_state() -> None:
    steps = run_closed_loop_episode(initial_scenario="sensor_faults", max_steps=4, seed=7)
    assert steps[-1].next_scenario is None
    assert "release" in steps[-1].final_actions


def test_oxidant_limitation_episode_reaches_release_state() -> None:
    steps = run_closed_loop_episode(initial_scenario="oxidant_limitation", max_steps=4, seed=7)
    assert steps[0].strategy_profile == "emergency_response"
    assert steps[-1].next_scenario is None
    assert "release" in steps[-1].final_actions


def test_reaction_time_insufficient_episode_recirculates_before_release() -> None:
    steps = run_closed_loop_episode(initial_scenario="reaction_time_insufficient", max_steps=4, seed=7)
    assert steps[0].strategy_profile == "balanced"
    assert "recirculate" in steps[0].final_actions
    assert "release" not in steps[0].final_actions
    assert steps[-1].next_scenario is None
    assert steps[-1].final_actions == ["release"]


def test_catalyst_deactivation_episode_regenerates_before_release() -> None:
    steps = run_closed_loop_episode(initial_scenario="catalyst_deactivation", max_steps=5, seed=7)
    assert steps[0].final_actions[:2] == ["regenerate_catalyst", "recirculate"]
    assert steps[0].process_after is not None
    assert steps[0].process_after["catalyst_activity"] > steps[0].process_before["catalyst_activity"]
    assert steps[-1].next_scenario is None
    assert "release" in steps[-1].final_actions


def test_matrix_shock_episode_reaches_release_state() -> None:
    steps = run_closed_loop_episode(initial_scenario="matrix_shock", max_steps=4, seed=7)
    assert steps[-1].next_scenario is None
    assert "release" in steps[-1].final_actions

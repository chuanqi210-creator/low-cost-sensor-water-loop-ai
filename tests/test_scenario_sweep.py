from experiments.run_scenario_sweep import run_chain


def test_clean_scenario_allows_release() -> None:
    result = run_chain("clean_release")
    final_ids = [action["action_id"] for action in result["final_plan"]]
    assert "release" in final_ids
    assert "release" not in result["blocked_actions"]


def test_oxidant_limitation_prefers_dosing_not_release() -> None:
    result = run_chain("oxidant_limitation")
    final_ids = [action["action_id"] for action in result["final_plan"]]
    assert "dose_oxidant" in final_ids
    assert "release" not in final_ids


def test_reaction_time_insufficient_prefers_recirculation() -> None:
    result = run_chain("reaction_time_insufficient")
    final_ids = [action["action_id"] for action in result["final_plan"]]
    assert "recirculate" in final_ids
    assert "release" not in final_ids


def test_catalyst_deactivation_prefers_regeneration_then_recirculation() -> None:
    result = run_chain("catalyst_deactivation")
    final_ids = [action["action_id"] for action in result["final_plan"]]
    assert final_ids[:2] == ["regenerate_catalyst", "recirculate"]
    assert "release" not in final_ids


def test_matrix_shock_prefers_switch_or_pretreat() -> None:
    result = run_chain("matrix_shock")
    final_ids = [action["action_id"] for action in result["final_plan"]]
    assert "switch_or_pretreat" in final_ids
    assert "release" not in final_ids

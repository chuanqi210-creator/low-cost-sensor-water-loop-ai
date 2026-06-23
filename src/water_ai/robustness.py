from __future__ import annotations

from dataclasses import asdict, dataclass

from water_ai.closed_loop import run_closed_loop_episode


PROBLEM_SCENARIOS = [
    "sensor_faults",
    "oxidant_limitation",
    "reaction_time_insufficient",
    "catalyst_deactivation",
    "matrix_shock",
]


@dataclass(frozen=True)
class EpisodeEvaluation:
    scenario: str
    seed: int
    success: bool
    steps: int
    final_actions: list[str]
    final_scenario: str | None
    cumulative_cost: float
    cumulative_energy: float
    elapsed_min: int

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


def evaluate_closed_loop_robustness(
    *,
    scenarios: list[str] | None = None,
    seeds: range = range(30),
    max_steps: int = 6,
    observation_window_min: int = 24,
    sampling_interval_min: int = 1,
    disabled_sensors: set[str] | None = None,
    sensor_noise_multiplier: float = 0.0,
) -> dict[str, object]:
    scenarios = scenarios or PROBLEM_SCENARIOS
    episodes: list[EpisodeEvaluation] = []
    for scenario in scenarios:
        for seed in seeds:
            steps = run_closed_loop_episode(
                initial_scenario=scenario,
                max_steps=max_steps,
                observation_window_min=observation_window_min,
                sampling_interval_min=sampling_interval_min,
                disabled_sensors=disabled_sensors,
                sensor_noise_multiplier=sensor_noise_multiplier,
                seed=seed,
            )
            last = steps[-1]
            final_process = last.process_before if last.process_after is None else last.process_after
            success = last.next_scenario is None and "release" in last.final_actions
            episodes.append(
                EpisodeEvaluation(
                    scenario=scenario,
                    seed=seed,
                    success=success,
                    steps=len(steps),
                    final_actions=last.final_actions,
                    final_scenario=last.next_scenario,
                    cumulative_cost=round(float(final_process.get("cumulative_cost", 0.0)), 4),
                    cumulative_energy=round(float(final_process.get("cumulative_energy", 0.0)), 4),
                    elapsed_min=int(final_process.get("elapsed_min", 0)),
                )
            )

    summaries = []
    for scenario in scenarios:
        items = [episode for episode in episodes if episode.scenario == scenario]
        successes = [episode for episode in items if episode.success]
        summaries.append(
            {
                "scenario": scenario,
                "runs": len(items),
                "success_rate": round(len(successes) / max(1, len(items)), 3),
                "mean_steps": round(sum(episode.steps for episode in items) / max(1, len(items)), 3),
                "mean_cost": round(sum(episode.cumulative_cost for episode in items) / max(1, len(items)), 3),
                "mean_energy": round(sum(episode.cumulative_energy for episode in items) / max(1, len(items)), 3),
                "mean_elapsed_min": round(sum(episode.elapsed_min for episode in items) / max(1, len(items)), 1),
                "failures": [episode.as_dict() for episode in items if not episode.success],
            }
        )

    return {
        "max_steps": max_steps,
        "observation_window_min": observation_window_min,
        "sampling_interval_min": sampling_interval_min,
        "disabled_sensors": sorted(disabled_sensors or []),
        "sensor_noise_multiplier": sensor_noise_multiplier,
        "scenario_summaries": summaries,
        "episodes": [episode.as_dict() for episode in episodes],
    }

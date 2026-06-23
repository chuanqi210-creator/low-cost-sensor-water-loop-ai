from __future__ import annotations

from dataclasses import dataclass
import math

from water_ai.domain import SENSOR_RANGES, SensorReading
from water_ai.pipeline import run_agent_chain
from water_ai.process_dynamics import (
    apply_actions_to_process_state,
    generate_sensor_stream_from_process_state,
    initial_process_state,
)


SENSOR_NOISE_STD: dict[str, float] = {
    "pH": 0.03,
    "ORP_mV": 4.0,
    "EC_uScm": 25.0,
    "turbidity_NTU": 0.18,
    "temp_C": 0.06,
    "flow_Lmin": 0.012,
    "UV254_abs": 0.006,
}


@dataclass(frozen=True)
class ClosedLoopStep:
    step_id: int
    scenario: str
    final_actions: list[str]
    blocked_actions: list[str]
    strategy_profile: str
    state: dict[str, float]
    summary: str
    next_scenario: str | None
    process_before: dict[str, float | int | str]
    process_after: dict[str, float | int | str] | None


def run_closed_loop_episode(
    *,
    initial_scenario: str,
    max_steps: int = 4,
    observation_window_min: int = 24,
    sampling_interval_min: int = 1,
    disabled_sensors: set[str] | None = None,
    sensor_noise_multiplier: float = 0.0,
    seed: int = 7,
) -> list[ClosedLoopStep]:
    process_state = initial_process_state(initial_scenario)
    steps: list[ClosedLoopStep] = []
    for step_id in range(max_steps):
        readings = generate_sensor_stream_from_process_state(process_state, n=observation_window_min, seed=seed + step_id)
        readings = _apply_sensor_design(
            readings,
            sampling_interval_min=sampling_interval_min,
            disabled_sensors=disabled_sensors,
            sensor_noise_multiplier=sensor_noise_multiplier,
        )
        result = run_agent_chain(readings)
        final_plan = result.arbitration.metrics["final_plan"]
        final_actions = [str(action["action_id"]) for action in final_plan]
        blocked_actions = [str(action) for action in result.arbitration.metrics["blocked_actions"]]
        strategy_profile = str(result.strategy_profile.metrics.get("selected_profile", "balanced"))
        state = {str(k): float(v) for k, v in result.soft_sensor.metrics["state_estimate"].items() if isinstance(v, int | float)}
        next_process_state = apply_actions_to_process_state(process_state, final_plan)
        next_scenario = next_process_state.label if next_process_state is not None else None
        steps.append(
            ClosedLoopStep(
                step_id=step_id,
                scenario=process_state.label,
                final_actions=final_actions,
                blocked_actions=blocked_actions,
                strategy_profile=strategy_profile,
                state=state,
                summary=result.arbitration.summary,
                next_scenario=next_scenario,
                process_before=process_state.as_dict(),
                process_after=next_process_state.as_dict() if next_process_state is not None else None,
            )
        )
        if next_process_state is None:
            break
        process_state = next_process_state
    return steps


def _apply_sensor_design(
    readings: list[SensorReading],
    *,
    sampling_interval_min: int,
    disabled_sensors: set[str] | None,
    sensor_noise_multiplier: float = 0.0,
) -> list[SensorReading]:
    step = max(1, int(sampling_interval_min))
    sampled = readings[::step]
    if readings and sampled[-1] is not readings[-1]:
        sampled = [*sampled, readings[-1]]

    disabled = set(disabled_sensors or [])
    designed: list[SensorReading] = []
    for reading in sampled:
        values = dict(reading.values)
        for sensor in disabled:
            if sensor in values:
                values[sensor] = None
        if sensor_noise_multiplier > 0:
            values = _apply_measurement_noise(reading, values, sensor_noise_multiplier=sensor_noise_multiplier)
        designed.append(
            SensorReading(
                timestamp_min=reading.timestamp_min,
                cycle_id=reading.cycle_id,
                values=values,
                ground_truth_faults=reading.ground_truth_faults,
                ground_truth_state=reading.ground_truth_state,
            )
        )
    return designed


def _apply_measurement_noise(
    reading: SensorReading,
    values: dict[str, float | None],
    *,
    sensor_noise_multiplier: float,
) -> dict[str, float | None]:
    noisy = dict(values)
    for sensor, value in values.items():
        if value is None or sensor not in SENSOR_NOISE_STD:
            continue
        perturbation = _deterministic_noise(
            sensor=sensor,
            timestamp_min=reading.timestamp_min,
            cycle_id=reading.cycle_id,
            multiplier=sensor_noise_multiplier,
        )
        lo, hi = SENSOR_RANGES.get(sensor, (-math.inf, math.inf))
        noisy[sensor] = round(max(lo, min(hi, float(value) + perturbation)), 4)
    return noisy


def _deterministic_noise(*, sensor: str, timestamp_min: int, cycle_id: int, multiplier: float) -> float:
    sensor_phase = sum(ord(char) for char in sensor) * 0.017
    phase = timestamp_min * 0.37 + cycle_id * 1.91 + sensor_phase
    waveform = math.sin(phase) + 0.45 * math.sin(phase * 0.31 + 1.7)
    return SENSOR_NOISE_STD[sensor] * multiplier * waveform


def transition_scenario(scenario: str, final_actions: list[str], blocked_actions: list[str]) -> str | None:
    if "release" in final_actions and "release" not in blocked_actions:
        return None

    actions = set(final_actions)
    if scenario == "sensor_faults":
        if {"hold_for_validation", "calibrate_sensors"} & actions:
            return "clean_release"
        return "sensor_faults"

    if scenario == "oxidant_limitation":
        if "dose_oxidant" in actions:
            return "clean_release" if "recirculate" in actions else "reaction_time_insufficient"
        return "oxidant_limitation"

    if scenario == "reaction_time_insufficient":
        if "recirculate" in actions:
            return "clean_release"
        return "reaction_time_insufficient"

    if scenario == "catalyst_deactivation":
        if "regenerate_catalyst" in actions and "recirculate" in actions:
            return "clean_release"
        if "regenerate_catalyst" in actions:
            return "reaction_time_insufficient"
        return "catalyst_deactivation"

    if scenario == "matrix_shock":
        if "switch_or_pretreat" in actions:
            return "clean_release"
        if "recirculate" in actions:
            return "reaction_time_insufficient"
        return "matrix_shock"

    if scenario == "clean_release":
        return None

    return scenario

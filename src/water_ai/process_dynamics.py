from __future__ import annotations

import math
import random
from dataclasses import asdict, dataclass, replace

from water_ai.domain import SensorReading


@dataclass(frozen=True)
class ProcessState:
    """Simplified physical state of a circular water-treatment batch."""

    label: str
    pollutant_load: float
    oxidant_level: float
    catalyst_activity: float
    matrix_interference: float
    sensor_health: float
    hydraulic_efficiency: float
    cycle_count: int = 0
    catalyst_age_cycles: int = 0
    catalyst_regen_count: int = 0
    catalyst_lifetime_fraction: float = 1.0
    elapsed_min: int = 0
    cumulative_cost: float = 0.0
    cumulative_energy: float = 0.0
    offline_residual_proxy: float = 1.0
    offline_validation_confidence: float = 0.0
    offline_validation_age_min: int = 999
    offline_validation_error: float = 0.0

    def as_dict(self) -> dict[str, float | int | str]:
        return asdict(self)


def initial_process_state(scenario: str) -> ProcessState:
    states = {
        "clean_release": ProcessState(
            label="clean_release",
            pollutant_load=0.22,
            oxidant_level=0.80,
            catalyst_activity=0.82,
            matrix_interference=0.24,
            sensor_health=0.98,
            hydraulic_efficiency=0.92,
            catalyst_age_cycles=1,
            catalyst_lifetime_fraction=0.96,
        ),
        "sensor_faults": ProcessState(
            label="sensor_faults",
            pollutant_load=0.24,
            oxidant_level=0.80,
            catalyst_activity=0.78,
            matrix_interference=0.38,
            sensor_health=0.48,
            hydraulic_efficiency=0.32,
            catalyst_age_cycles=2,
            catalyst_lifetime_fraction=0.90,
        ),
        "oxidant_limitation": ProcessState(
            label="oxidant_limitation",
            pollutant_load=0.72,
            oxidant_level=0.18,
            catalyst_activity=0.72,
            matrix_interference=0.30,
            sensor_health=0.96,
            hydraulic_efficiency=0.86,
            catalyst_age_cycles=3,
            catalyst_lifetime_fraction=0.88,
        ),
        "reaction_time_insufficient": ProcessState(
            label="reaction_time_insufficient",
            pollutant_load=0.68,
            oxidant_level=0.82,
            catalyst_activity=0.72,
            matrix_interference=0.30,
            sensor_health=0.96,
            hydraulic_efficiency=0.64,
            catalyst_age_cycles=3,
            catalyst_lifetime_fraction=0.86,
        ),
        "catalyst_deactivation": ProcessState(
            label="catalyst_deactivation",
            pollutant_load=0.70,
            oxidant_level=0.78,
            catalyst_activity=0.36,
            matrix_interference=0.28,
            sensor_health=0.96,
            hydraulic_efficiency=0.82,
            catalyst_age_cycles=7,
            catalyst_regen_count=1,
            catalyst_lifetime_fraction=0.66,
        ),
        "matrix_shock": ProcessState(
            label="matrix_shock",
            pollutant_load=0.62,
            oxidant_level=0.76,
            catalyst_activity=0.72,
            matrix_interference=0.88,
            sensor_health=0.92,
            hydraulic_efficiency=0.80,
            catalyst_age_cycles=4,
            catalyst_lifetime_fraction=0.82,
        ),
    }
    return states.get(scenario, states["sensor_faults"])


def generate_sensor_stream_from_process_state(
    state: ProcessState,
    *,
    n: int = 72,
    seed: int = 7,
) -> list[SensorReading]:
    rng = random.Random(seed + state.cycle_count * 31)
    readings: list[SensorReading] = []
    effective_rate = 0.010 + 0.060 * state.oxidant_level * state.catalyst_activity * state.hydraulic_efficiency * (1.0 - 0.55 * state.matrix_interference)
    effective_rate = max(0.002, effective_rate)

    for t in range(n):
        cycle_id = state.cycle_count + t // 12
        completion = 1.0 - math.exp(-effective_rate * t)
        remaining = _clip(state.pollutant_load * (1.0 - completion) + 0.12 * state.matrix_interference)
        oxidant_remaining = _clip(state.oxidant_level - 0.38 * completion * state.pollutant_load + 0.04 * (1.0 - state.matrix_interference))

        ph = 7.1 + 1.05 * (state.matrix_interference - 0.30) + rng.gauss(0, 0.035)
        orp = 220 + 520 * oxidant_remaining + 55 * completion - 90 * state.matrix_interference + rng.gauss(0, 8)
        matrix_shock_load = max(0.0, state.matrix_interference - 0.55)
        ec = 700 + 1500 * state.matrix_interference + 160 * state.pollutant_load + 2600 * matrix_shock_load + rng.gauss(0, 24)
        turbidity = max(
            0.0,
            3 + 18 * state.matrix_interference + 22 * remaining + 35 * matrix_shock_load - 7 * completion + rng.gauss(0, 0.9),
        )
        temp = 24.6 + 0.02 * t + rng.gauss(0, 0.08)
        flow = max(0.05, 0.20 + 1.15 * state.hydraulic_efficiency + 0.03 * math.sin(t / 6) + rng.gauss(0, 0.012))
        uv254 = max(0.0, 0.10 + 1.15 * remaining + 0.18 * state.matrix_interference + rng.gauss(0, 0.025))

        values: dict[str, float | None] = {
            "pH": round(ph, 3),
            "ORP_mV": round(orp, 2),
            "EC_uScm": round(ec, 2),
            "turbidity_NTU": round(turbidity, 3),
            "temp_C": round(temp, 3),
            "flow_Lmin": round(flow, 3),
            "UV254_abs": round(uv254, 4),
        }
        validation_confidence = state.offline_validation_confidence * math.exp(-(state.offline_validation_age_min + t) / 90)
        if validation_confidence >= 0.12:
            values["offline_residual_proxy"] = round(_clip(state.offline_residual_proxy), 4)
            values["offline_validation_confidence"] = round(_clip(validation_confidence), 4)
            values["offline_validation_age_min"] = float(state.offline_validation_age_min + t)
        faults: list[str] = []
        if state.sensor_health < 0.72:
            if t == 10:
                values["ORP_mV"] = None
                faults.append("missing_orp")
            if t == 21:
                values["pH"] = round(values["pH"] + 3.2, 3)
                faults.append("ph_spike")
            if 32 <= t <= 39:
                values["EC_uScm"] = round(700 + 1500 * state.matrix_interference + 2600 * max(0.0, state.matrix_interference - 0.55), 2)
                faults.append("ec_flatline")
            if t >= 46:
                values["turbidity_NTU"] = round((values["turbidity_NTU"] or 0.0) + 0.65 * (t - 45), 3)
                faults.append("turbidity_drift")

        if state.hydraulic_efficiency < 0.45 and 56 <= t <= 63:
            values["flow_Lmin"] = round(0.22 + rng.gauss(0, 0.008), 3)
            faults.append("flow_drop")

        ground_truth_state = {
            "pollutant_residual_risk": round(_clip(remaining), 4),
            "reaction_completion": round(_clip(completion), 4),
            "oxidant_remaining": round(oxidant_remaining, 4),
            "catalyst_activity": round(_clip(state.catalyst_activity), 4),
            "catalyst_age_cycles": float(state.catalyst_age_cycles),
            "catalyst_regen_count": float(state.catalyst_regen_count),
            "catalyst_lifetime_fraction": round(_clip(state.catalyst_lifetime_fraction), 4),
            "matrix_interference": round(_clip(state.matrix_interference), 4),
            "offline_validation_confidence": round(_clip(validation_confidence), 4),
            "offline_validation_error": round(state.offline_validation_error, 4),
        }
        readings.append(
            SensorReading(
                timestamp_min=state.elapsed_min + t,
                cycle_id=cycle_id,
                values=values,
                ground_truth_faults=faults,
                ground_truth_state=ground_truth_state,
            )
        )
    return readings


def apply_actions_to_process_state(state: ProcessState, final_actions: list[str | dict[str, object]]) -> ProcessState | None:
    action_ids = [_action_id(action) for action in final_actions]
    if "release" in action_ids:
        return None

    next_state = state
    for action in final_actions:
        action_id = _action_id(action)
        parameters = _action_parameters(action)
        if action_id == "hold_for_validation":
            hold_min = _clip(float(parameters.get("hold_min", 20)), 5, 60)
            validation_delay_min = _clip(float(parameters.get("validation_delay_min", 10)), 0, 45)
            passive_removal = _clip(
                0.10
                * next_state.oxidant_level
                * next_state.catalyst_activity
                * next_state.hydraulic_efficiency
                * (1.0 - 0.45 * next_state.matrix_interference),
                0.01,
                0.12,
            ) * _clip(hold_min / 20, 0.4, 2.0)
            updated_pollutant_load = _clip(next_state.pollutant_load * (1.0 - passive_removal), 0.02, 1.0)
            validation_error = 0.035 * math.sin((next_state.elapsed_min + hold_min + validation_delay_min) / 17.0)
            offline_residual_proxy = _clip(updated_pollutant_load + validation_error)
            next_state = replace(
                next_state,
                pollutant_load=updated_pollutant_load,
                oxidant_level=_clip(next_state.oxidant_level - 0.05 * passive_removal, 0.02, 1.0),
                sensor_health=_clip(next_state.sensor_health + 0.10),
                elapsed_min=next_state.elapsed_min + int(round(hold_min + validation_delay_min)),
                cumulative_cost=next_state.cumulative_cost + 0.08 * hold_min / 20 + 0.04 * validation_delay_min / 10,
                offline_residual_proxy=offline_residual_proxy,
                offline_validation_confidence=_clip(0.55 + hold_min / 100 - abs(validation_error) * 2.0, 0.2, 0.9),
                offline_validation_age_min=0,
                offline_validation_error=validation_error,
            )
        elif action_id == "inspect_hydraulics":
            next_state = replace(
                next_state,
                hydraulic_efficiency=_clip(next_state.hydraulic_efficiency + 0.48),
                sensor_health=_clip(next_state.sensor_health + 0.06),
                cumulative_cost=next_state.cumulative_cost + 0.10,
                offline_validation_age_min=next_state.offline_validation_age_min + 5,
            )
        elif action_id == "calibrate_sensors":
            next_state = replace(
                next_state,
                sensor_health=_clip(next_state.sensor_health + 0.38),
                cumulative_cost=next_state.cumulative_cost + 0.12,
                offline_validation_age_min=next_state.offline_validation_age_min + 5,
            )
        elif action_id == "dose_oxidant":
            dose_factor = _clip(float(parameters.get("dose_factor", 0.15)), 0.05, 0.40)
            next_state = replace(
                next_state,
                oxidant_level=_clip(next_state.oxidant_level + 1.8 * dose_factor),
                cumulative_cost=next_state.cumulative_cost + 0.22 * dose_factor / 0.15,
                offline_validation_confidence=_clip(next_state.offline_validation_confidence * 0.85),
                offline_validation_age_min=next_state.offline_validation_age_min + 5,
            )
        elif action_id == "regenerate_catalyst":
            regen_intensity = _clip(float(parameters.get("regen_intensity", 0.55)), 0.20, 0.95)
            downtime_min = _clip(float(parameters.get("downtime_min", 45)), 15, 120)
            next_regen_count = next_state.catalyst_regen_count + 1
            regen_efficiency = _clip(
                next_state.catalyst_lifetime_fraction
                * (1.0 - 0.09 * next_state.catalyst_regen_count)
                * (1.0 - 0.28 * next_state.matrix_interference),
                0.18,
                1.0,
            )
            updated_lifetime = _clip(
                next_state.catalyst_lifetime_fraction
                - 0.040
                - 0.035 * regen_intensity
                - 0.030 * next_state.matrix_interference
                - 0.012 * next_state.catalyst_regen_count,
                0.18,
                1.0,
            )
            activity_cap = _clip(0.42 + 0.56 * updated_lifetime - 0.035 * next_regen_count, 0.35, 0.96)
            new_activity = _clip(
                next_state.catalyst_activity
                + 0.34 * regen_intensity * regen_efficiency
                + 0.08 * (1.0 - next_state.matrix_interference),
                0.25,
                activity_cap,
            )
            passive_removal = _clip(
                0.08
                * next_state.oxidant_level
                * new_activity
                * next_state.hydraulic_efficiency
                * (1.0 - 0.42 * next_state.matrix_interference)
                * (downtime_min / 45),
                0.01,
                0.16,
            )
            next_state = replace(
                next_state,
                catalyst_activity=new_activity,
                catalyst_age_cycles=next_state.catalyst_age_cycles + 1,
                catalyst_regen_count=next_regen_count,
                catalyst_lifetime_fraction=updated_lifetime,
                pollutant_load=_clip(next_state.pollutant_load * (1.0 - passive_removal), 0.02, 1.0),
                oxidant_level=_clip(next_state.oxidant_level - 0.06 * passive_removal, 0.02, 1.0),
                elapsed_min=next_state.elapsed_min + int(round(downtime_min)),
                cumulative_cost=next_state.cumulative_cost + 0.34 * regen_intensity * (1.0 + 0.12 * next_state.catalyst_regen_count) + 0.08,
                cumulative_energy=next_state.cumulative_energy + 0.07 * regen_intensity,
                offline_validation_confidence=_clip(next_state.offline_validation_confidence * 0.78),
                offline_validation_age_min=next_state.offline_validation_age_min + int(round(downtime_min)),
            )
        elif action_id == "replace_catalyst":
            downtime_min = _clip(float(parameters.get("downtime_min", 90)), 45, 180)
            commissioning_confidence = _clip(float(parameters.get("commissioning_confidence", 0.82)), 0.45, 0.98)
            new_activity = _clip(0.90 - 0.05 * next_state.matrix_interference + 0.04 * commissioning_confidence, 0.72, 0.98)
            passive_removal = _clip(
                0.05
                * next_state.oxidant_level
                * new_activity
                * next_state.hydraulic_efficiency
                * (1.0 - 0.35 * next_state.matrix_interference)
                * (downtime_min / 90),
                0.01,
                0.14,
            )
            next_state = replace(
                next_state,
                catalyst_activity=new_activity,
                catalyst_age_cycles=0,
                catalyst_regen_count=0,
                catalyst_lifetime_fraction=1.0,
                pollutant_load=_clip(next_state.pollutant_load * (1.0 - passive_removal), 0.02, 1.0),
                oxidant_level=_clip(next_state.oxidant_level - 0.04 * passive_removal, 0.02, 1.0),
                elapsed_min=next_state.elapsed_min + int(round(downtime_min)),
                cumulative_cost=next_state.cumulative_cost + 0.82 + 0.18 * downtime_min / 90,
                cumulative_energy=next_state.cumulative_energy + 0.05,
                offline_validation_confidence=_clip(next_state.offline_validation_confidence * 0.70),
                offline_validation_age_min=next_state.offline_validation_age_min + int(round(downtime_min)),
            )
        elif action_id == "recirculate":
            recycle_ratio = _clip(float(parameters.get("recycle_ratio", 0.35)), 0.15, 0.75)
            extra_retention_min = _clip(float(parameters.get("extra_retention_min", 15)), 5, 60)
            intensity = _clip((recycle_ratio / 0.35) * (extra_retention_min / 15) ** 0.5, 0.5, 1.8)
            removal = _clip(
                0.42
                * next_state.oxidant_level
                * next_state.catalyst_activity
                * next_state.hydraulic_efficiency
                * (1.0 - 0.45 * next_state.matrix_interference)
                * intensity,
                0.03,
                0.55,
            )
            lifetime_decay = _clip(
                0.010
                + 0.018 * next_state.matrix_interference
                + 0.006 * max(0.0, intensity - 1.0)
                + 0.008 * max(0.0, 0.45 - next_state.catalyst_activity),
                0.006,
                0.045,
            )
            next_state = replace(
                next_state,
                pollutant_load=_clip(next_state.pollutant_load * (1.0 - removal), 0.02, 1.0),
                oxidant_level=_clip(next_state.oxidant_level - 0.12 * removal, 0.02, 1.0),
                catalyst_activity=_clip(
                    next_state.catalyst_activity
                    - 0.015 * next_state.matrix_interference
                    - 0.010 * max(0.0, intensity - 1.0),
                    0.20,
                    1.0,
                ),
                catalyst_age_cycles=next_state.catalyst_age_cycles + 1,
                catalyst_lifetime_fraction=_clip(next_state.catalyst_lifetime_fraction - lifetime_decay, 0.18, 1.0),
                cycle_count=next_state.cycle_count + 1,
                elapsed_min=next_state.elapsed_min + int(round(extra_retention_min)),
                cumulative_energy=next_state.cumulative_energy + 0.18 * intensity,
                cumulative_cost=next_state.cumulative_cost + 0.06 * intensity,
                offline_validation_confidence=_clip(next_state.offline_validation_confidence * math.exp(-extra_retention_min / 70)),
                offline_validation_age_min=next_state.offline_validation_age_min + int(round(extra_retention_min)),
            )
        elif action_id == "switch_or_pretreat":
            next_state = replace(
                next_state,
                matrix_interference=_clip(next_state.matrix_interference * 0.38, 0.05, 1.0),
                pollutant_load=_clip(next_state.pollutant_load * 0.78, 0.02, 1.0),
                hydraulic_efficiency=_clip(next_state.hydraulic_efficiency + 0.08),
                elapsed_min=next_state.elapsed_min + 35,
                cumulative_energy=next_state.cumulative_energy + 0.20,
                cumulative_cost=next_state.cumulative_cost + 0.36,
                offline_validation_confidence=_clip(next_state.offline_validation_confidence * 0.75),
                offline_validation_age_min=next_state.offline_validation_age_min + 35,
            )

    return replace(next_state, label=classify_process_state(next_state))


def _action_id(action: str | dict[str, object]) -> str:
    if isinstance(action, dict):
        return str(action.get("action_id", ""))
    return str(action)


def _action_parameters(action: str | dict[str, object]) -> dict[str, object]:
    if not isinstance(action, dict):
        return {}
    parameters = action.get("parameters", {})
    return parameters if isinstance(parameters, dict) else {}


def classify_process_state(state: ProcessState) -> str:
    if state.pollutant_load < 0.28 and state.matrix_interference < 0.45 and state.sensor_health >= 0.75 and state.hydraulic_efficiency >= 0.65:
        return "clean_release"
    if state.sensor_health < 0.72 or state.hydraulic_efficiency < 0.45:
        return "sensor_faults"
    if state.oxidant_level < 0.35 and state.pollutant_load >= 0.40:
        return "oxidant_limitation"
    if state.matrix_interference >= 0.58:
        return "matrix_shock"
    if (state.catalyst_activity < 0.52 or state.catalyst_lifetime_fraction < 0.38) and state.pollutant_load >= 0.35:
        return "catalyst_deactivation"
    if state.pollutant_load >= 0.38:
        return "reaction_time_insufficient"
    return "clean_release"


def _clip(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, value))

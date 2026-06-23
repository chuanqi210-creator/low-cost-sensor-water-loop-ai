from __future__ import annotations

import math
import random

from water_ai.domain import SensorReading


def generate_low_cost_sensor_stream(
    *,
    n: int = 72,
    seed: int = 42,
    inject_faults: bool = True,
    scenario: str = "sensor_faults",
) -> list[SensorReading]:
    """Generate synthetic low-cost sensor data for a circular treatment run.

    The stream represents one batch passing through repeated sensing and
    recirculation windows. It intentionally stays simple so agent behavior is
    auditable before the simulator becomes more physically detailed.
    """

    rng = random.Random(seed)
    readings: list[SensorReading] = []

    for t in range(n):
        cycle_id = t // 12
        reaction_progress = 1.0 - math.exp(-0.045 * t)
        pollutant_shock = 1.0 if t < 18 else 0.62
        catalyst_activity = max(0.62, 1.0 - 0.0035 * max(0, t - 28))
        matrix_interference = min(1.0, 0.18 + 0.00004 * (1250 + 80 * pollutant_shock) + (0.25 if t >= 46 else 0.0))

        ph = 7.25 + 0.12 * math.sin(t / 7) + rng.gauss(0, 0.035)
        orp = 350 + 220 * reaction_progress + rng.gauss(0, 8)
        ec = 1250 + 70 * math.sin(t / 12) + 80 * pollutant_shock + rng.gauss(0, 18)
        turbidity = max(0.0, 32 * math.exp(-0.035 * t) + rng.gauss(0, 0.8))
        temp = 24.8 + 0.03 * t + rng.gauss(0, 0.08)
        flow = 1.20 + 0.05 * math.sin(t / 6) + rng.gauss(0, 0.015)
        uv254 = max(0.0, 1.15 * math.exp(-0.025 * t) + rng.gauss(0, 0.025))

        if scenario == "clean_release":
            pass
        elif scenario == "oxidant_limitation":
            orp = 235 + 70 * reaction_progress + rng.gauss(0, 8)
            uv254 = max(0.0, 1.15 * math.exp(-0.008 * t) + rng.gauss(0, 0.025))
        elif scenario == "reaction_time_insufficient":
            orp = 420 + 170 * reaction_progress + rng.gauss(0, 8)
            uv254 = max(0.0, 1.15 * math.exp(-0.004 * t) + rng.gauss(0, 0.025))
        elif scenario == "catalyst_deactivation":
            catalyst_activity = max(0.32, 0.45 - 0.0018 * max(0, t - 18))
            orp = 445 + 150 * reaction_progress + rng.gauss(0, 8)
            uv254 = max(0.0, 1.15 * math.exp(-0.006 * t) + rng.gauss(0, 0.025))
        elif scenario == "matrix_shock":
            if t >= 24:
                ec += 3600
                turbidity += 22
                ph += 1.05
                uv254 = max(0.0, uv254 + 0.22)

        values: dict[str, float | None] = {
            "pH": round(ph, 3),
            "ORP_mV": round(orp, 2),
            "EC_uScm": round(ec, 2),
            "turbidity_NTU": round(turbidity, 3),
            "temp_C": round(temp, 3),
            "flow_Lmin": round(flow, 3),
            "UV254_abs": round(uv254, 4),
        }
        faults: list[str] = []

        if inject_faults and scenario == "sensor_faults":
            if t == 10:
                values["ORP_mV"] = None
                faults.append("missing_orp")
            if t == 21:
                values["pH"] = 10.95
                faults.append("ph_spike")
            if 32 <= t <= 39:
                values["EC_uScm"] = 1410.0
                faults.append("ec_flatline")
            if t >= 46:
                values["turbidity_NTU"] = round((values["turbidity_NTU"] or 0.0) + 0.72 * (t - 45), 3)
                faults.append("turbidity_drift")
            if 58 <= t <= 63:
                values["flow_Lmin"] = round(0.24 + rng.gauss(0, 0.008), 3)
                faults.append("flow_drop")

        ground_truth_state = {
            "pollutant_residual_risk": round(max(0.03, pollutant_shock * (1.0 - reaction_progress) + 0.12 * matrix_interference), 4),
            "reaction_completion": round(min(1.0, reaction_progress * catalyst_activity), 4),
            "oxidant_remaining": round(min(1.0, max(0.05, (orp - 250) / 420)), 4),
            "catalyst_activity": round(catalyst_activity, 4),
            "matrix_interference": round(matrix_interference, 4),
        }

        if scenario == "oxidant_limitation":
            ground_truth_state["pollutant_residual_risk"] = round(max(ground_truth_state["pollutant_residual_risk"], 0.58), 4)
            ground_truth_state["oxidant_remaining"] = round(max(0.04, min(0.28, ground_truth_state["oxidant_remaining"])), 4)
        elif scenario == "reaction_time_insufficient":
            ground_truth_state["pollutant_residual_risk"] = round(max(ground_truth_state["pollutant_residual_risk"], 0.52), 4)
            ground_truth_state["oxidant_remaining"] = round(max(0.55, ground_truth_state["oxidant_remaining"]), 4)
        elif scenario == "catalyst_deactivation":
            ground_truth_state["pollutant_residual_risk"] = round(max(ground_truth_state["pollutant_residual_risk"], 0.55), 4)
            ground_truth_state["oxidant_remaining"] = round(max(0.50, ground_truth_state["oxidant_remaining"]), 4)
            ground_truth_state["catalyst_activity"] = round(min(ground_truth_state["catalyst_activity"], 0.45), 4)
        elif scenario == "matrix_shock":
            ground_truth_state["matrix_interference"] = round(max(ground_truth_state["matrix_interference"], 0.82), 4)
            ground_truth_state["pollutant_residual_risk"] = round(max(ground_truth_state["pollutant_residual_risk"], 0.46), 4)

        readings.append(
            SensorReading(
                timestamp_min=t,
                cycle_id=cycle_id,
                values=values,
                ground_truth_faults=faults,
                ground_truth_state=ground_truth_state,
            )
        )

    return readings

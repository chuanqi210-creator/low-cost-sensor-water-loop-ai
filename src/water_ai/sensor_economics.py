from __future__ import annotations

from dataclasses import asdict, dataclass
from math import ceil


@dataclass(frozen=True)
class SensorEconomicProfile:
    purchase_cost_cny: float
    monthly_maintenance_cny: float
    calibration_minutes_per_week: float

    def as_dict(self) -> dict[str, float]:
        return asdict(self)


SENSOR_ECONOMIC_PROFILES: dict[str, SensorEconomicProfile] = {
    "pH": SensorEconomicProfile(purchase_cost_cny=800, monthly_maintenance_cny=45, calibration_minutes_per_week=15),
    "ORP_mV": SensorEconomicProfile(purchase_cost_cny=900, monthly_maintenance_cny=50, calibration_minutes_per_week=15),
    "EC_uScm": SensorEconomicProfile(purchase_cost_cny=700, monthly_maintenance_cny=30, calibration_minutes_per_week=10),
    "turbidity_NTU": SensorEconomicProfile(purchase_cost_cny=1500, monthly_maintenance_cny=60, calibration_minutes_per_week=20),
    "temp_C": SensorEconomicProfile(purchase_cost_cny=200, monthly_maintenance_cny=10, calibration_minutes_per_week=5),
    "flow_Lmin": SensorEconomicProfile(purchase_cost_cny=1200, monthly_maintenance_cny=45, calibration_minutes_per_week=15),
    "UV254_abs": SensorEconomicProfile(purchase_cost_cny=6500, monthly_maintenance_cny=180, calibration_minutes_per_week=45),
}

BASELINE_OBSERVATION_WINDOW_MIN = 24
BASELINE_SAMPLING_INTERVAL_MIN = 1
SENSOR_CHANNELS = tuple(SENSOR_ECONOMIC_PROFILES.keys())


def compute_sensor_economics(
    *,
    disabled_sensors: set[str] | list[str] | tuple[str, ...],
    sampling_interval_min: int,
    observation_window_min: int,
    profiles: dict[str, SensorEconomicProfile] = SENSOR_ECONOMIC_PROFILES,
) -> dict[str, object]:
    disabled = set(disabled_sensors)
    enabled = [sensor for sensor in profiles if sensor not in disabled]
    baseline_purchase = sum(profile.purchase_cost_cny for profile in profiles.values())
    baseline_maintenance = sum(profile.monthly_maintenance_cny * 12 for profile in profiles.values())
    baseline_samples = _samples_per_window(
        sensor_count=len(profiles),
        observation_window_min=BASELINE_OBSERVATION_WINDOW_MIN,
        sampling_interval_min=BASELINE_SAMPLING_INTERVAL_MIN,
    )

    purchase = sum(profiles[sensor].purchase_cost_cny for sensor in enabled)
    annual_maintenance = sum(profiles[sensor].monthly_maintenance_cny * 12 for sensor in enabled)
    calibration_hours_per_month = sum(profiles[sensor].calibration_minutes_per_week * 4.33 for sensor in enabled) / 60
    sample_count = _samples_per_window(
        sensor_count=len(enabled),
        observation_window_min=observation_window_min,
        sampling_interval_min=sampling_interval_min,
    )
    capex_index = _ratio(purchase, baseline_purchase)
    maintenance_index = _ratio(annual_maintenance, baseline_maintenance)
    sampling_load_index = _ratio(sample_count, baseline_samples)
    engineering_cost_index = _clip(0.50 * capex_index + 0.30 * maintenance_index + 0.20 * sampling_load_index)

    return {
        "enabled_sensors": enabled,
        "disabled_sensors": sorted(disabled),
        "purchase_cost_cny": round(purchase, 1),
        "annual_maintenance_cny": round(annual_maintenance, 1),
        "calibration_hours_per_month": round(calibration_hours_per_month, 2),
        "samples_per_window": sample_count,
        "capex_index": round(capex_index, 3),
        "maintenance_index": round(maintenance_index, 3),
        "sampling_load_index": round(sampling_load_index, 3),
        "engineering_cost_index": round(engineering_cost_index, 3),
        "profile_table": {sensor: profiles[sensor].as_dict() for sensor in enabled},
    }


def _samples_per_window(*, sensor_count: int, observation_window_min: int, sampling_interval_min: int) -> int:
    return int(sensor_count * max(1, ceil(observation_window_min / max(1, sampling_interval_min))))


def _ratio(value: float, baseline: float) -> float:
    if baseline <= 0:
        return 0.0
    return _clip(value / baseline)


def _clip(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, value))

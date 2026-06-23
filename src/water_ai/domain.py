from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Severity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass(frozen=True)
class SensorReading:
    """One low-cost sensing snapshot from the circular water-treatment process."""

    timestamp_min: int
    cycle_id: int
    values: dict[str, float | None]
    ground_truth_faults: list[str] = field(default_factory=list)
    ground_truth_state: dict[str, float] = field(default_factory=dict)


@dataclass(frozen=True)
class QualityIssue:
    sensor: str
    issue_type: str
    severity: Severity
    message: str
    timestamp_min: int | None = None
    evidence: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AgentReport:
    agent_name: str
    confidence: float
    summary: str
    issues: list[QualityIssue]
    recommendations: list[str]
    metrics: dict[str, Any]


SENSOR_RANGES: dict[str, tuple[float, float]] = {
    "pH": (3.0, 11.0),
    "ORP_mV": (50.0, 900.0),
    "EC_uScm": (50.0, 20000.0),
    "turbidity_NTU": (0.0, 1000.0),
    "temp_C": (5.0, 45.0),
    "flow_Lmin": (0.05, 5.0),
    "UV254_abs": (0.0, 5.0),
}


RATE_LIMITS: dict[str, float] = {
    "pH": 0.7,
    "ORP_mV": 85.0,
    "EC_uScm": 850.0,
    "turbidity_NTU": 45.0,
    "temp_C": 1.2,
    "flow_Lmin": 0.55,
    "UV254_abs": 0.22,
}


FLATLINE_EPS: dict[str, float] = {
    "pH": 0.01,
    "ORP_mV": 0.5,
    "EC_uScm": 2.0,
    "turbidity_NTU": 0.03,
    "temp_C": 0.02,
    "flow_Lmin": 0.003,
    "UV254_abs": 0.002,
}

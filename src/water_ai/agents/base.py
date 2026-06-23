from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

from water_ai.domain import AgentReport, SensorReading


class BaseAgent(ABC):
    name: str

    @abstractmethod
    def run(self, readings: Sequence[SensorReading]) -> AgentReport:
        """Analyze a sequence of readings and return an agent report."""


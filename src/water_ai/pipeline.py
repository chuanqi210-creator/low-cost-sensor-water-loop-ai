from __future__ import annotations

from dataclasses import dataclass

from water_ai.agents.arbitration_agent import ArbitrationAgent
from water_ai.agents.catalyst_lifecycle_agent import CatalystLifecycleAgent
from water_ai.agents.control_strategy_agent import ControlStrategyAgent
from water_ai.agents.cost_safety_agent import CostSafetyAgent
from water_ai.agents.data_quality_agent import DataQualityAgent
from water_ai.agents.fault_diagnosis_agent import FaultDiagnosisAgent
from water_ai.agents.mechanism_agent import MechanismAgent
from water_ai.agents.soft_sensor_agent import SoftSensorAgent
from water_ai.agents.strategy_profile_agent import StrategyProfileAgent
from water_ai.agents.validation_planning_agent import ValidationPlanningAgent
from water_ai.domain import AgentReport, SensorReading


@dataclass(frozen=True)
class AgentChainResult:
    data_quality: AgentReport
    soft_sensor: AgentReport
    mechanism: AgentReport
    fault_diagnosis: AgentReport
    catalyst_lifecycle: AgentReport
    validation_planning: AgentReport
    control_strategy: AgentReport
    strategy_profile: AgentReport
    cost_safety: AgentReport
    arbitration: AgentReport

    def summaries(self) -> dict[str, str]:
        return {
            "data_quality": self.data_quality.summary,
            "soft_sensor": self.soft_sensor.summary,
            "mechanism": self.mechanism.summary,
            "fault_diagnosis": self.fault_diagnosis.summary,
            "catalyst_lifecycle": self.catalyst_lifecycle.summary,
            "validation_planning": self.validation_planning.summary,
            "control_strategy": self.control_strategy.summary,
            "strategy_profile": self.strategy_profile.summary,
            "cost_safety": self.cost_safety.summary,
            "arbitration": self.arbitration.summary,
        }


def run_agent_chain(readings: list[SensorReading]) -> AgentChainResult:
    data_quality = DataQualityAgent().run(readings)
    soft_sensor = SoftSensorAgent(data_quality_report=data_quality).run(readings)
    mechanism = MechanismAgent(data_quality_report=data_quality, soft_sensor_report=soft_sensor).run(readings)
    fault_diagnosis = FaultDiagnosisAgent(
        data_quality_report=data_quality,
        soft_sensor_report=soft_sensor,
        mechanism_report=mechanism,
    ).run(readings)
    catalyst_lifecycle = CatalystLifecycleAgent(
        soft_sensor_report=soft_sensor,
        fault_report=fault_diagnosis,
    ).run(readings)
    validation_planning = ValidationPlanningAgent(
        soft_sensor_report=soft_sensor,
        fault_report=fault_diagnosis,
    ).run(readings)
    control_strategy = ControlStrategyAgent(
        soft_sensor_report=soft_sensor,
        fault_report=fault_diagnosis,
        catalyst_lifecycle_report=catalyst_lifecycle,
        validation_planning_report=validation_planning,
    ).run(readings)
    strategy_profile = StrategyProfileAgent(soft_sensor_report=soft_sensor, fault_report=fault_diagnosis).run(readings)
    objective_profile = str(strategy_profile.metrics.get("selected_profile", "balanced"))
    cost_safety = CostSafetyAgent(control_report=control_strategy, objective_profile=objective_profile).run(readings)
    arbitration = ArbitrationAgent(
        soft_sensor_report=soft_sensor,
        control_report=control_strategy,
        cost_safety_report=cost_safety,
    ).run(readings)
    return AgentChainResult(
        data_quality=data_quality,
        soft_sensor=soft_sensor,
        mechanism=mechanism,
        fault_diagnosis=fault_diagnosis,
        catalyst_lifecycle=catalyst_lifecycle,
        validation_planning=validation_planning,
        control_strategy=control_strategy,
        strategy_profile=strategy_profile,
        cost_safety=cost_safety,
        arbitration=arbitration,
    )

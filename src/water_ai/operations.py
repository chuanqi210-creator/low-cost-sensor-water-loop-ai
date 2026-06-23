from __future__ import annotations

from dataclasses import asdict, dataclass, replace

from water_ai.closed_loop import _apply_sensor_design
from water_ai.pipeline import run_agent_chain
from water_ai.process_dynamics import (
    ProcessState,
    apply_actions_to_process_state,
    generate_sensor_stream_from_process_state,
    initial_process_state,
)


@dataclass(frozen=True)
class BatchOperationRecord:
    batch_id: int
    scenario: str
    success: bool
    steps: int
    elapsed_min: int
    cumulative_cost: float
    cumulative_energy: float
    final_actions: list[str]
    all_actions: list[str]
    blocked_actions: list[str]
    strategy_profiles: list[str]
    validation_minutes: int
    regeneration_count: int
    replacement_count: int
    oxidant_dose_count: int
    catalyst_age_cycles_end: int
    catalyst_regen_count_end: int
    catalyst_lifetime_fraction_end: float
    catalyst_activity_end: float
    terminal_label: str

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class CampaignResult:
    records: list[BatchOperationRecord]
    catalyst_spares_remaining: int
    oxidant_stock_units_remaining: float
    total_elapsed_min: int
    total_cost: float
    total_energy: float

    def as_dict(self) -> dict[str, object]:
        return {
            "records": [record.as_dict() for record in self.records],
            "catalyst_spares_remaining": self.catalyst_spares_remaining,
            "oxidant_stock_units_remaining": round(self.oxidant_stock_units_remaining, 3),
            "total_elapsed_min": self.total_elapsed_min,
            "total_cost": round(self.total_cost, 3),
            "total_energy": round(self.total_energy, 3),
        }


def run_multibatch_campaign(
    scenarios: list[str],
    *,
    max_steps_per_batch: int = 5,
    observation_window_min: int = 24,
    sampling_interval_min: int = 1,
    disabled_sensors: set[str] | None = None,
    sensor_noise_multiplier: float = 0.0,
    initial_catalyst_spares: int = 1,
    initial_oxidant_stock_units: float = 3.0,
    seed: int = 7,
) -> CampaignResult:
    records: list[BatchOperationRecord] = []
    catalyst_spares_remaining = initial_catalyst_spares
    oxidant_stock_units_remaining = initial_oxidant_stock_units
    carried_catalyst: ProcessState | None = None

    for batch_id, scenario in enumerate(scenarios):
        process_state = _initialize_batch_state(scenario, carried_catalyst)
        all_actions: list[str] = []
        blocked_actions: list[str] = []
        strategy_profiles: list[str] = []
        validation_minutes = 0
        regeneration_count = 0
        replacement_count = 0
        oxidant_dose_count = 0
        success = False
        terminal_state = process_state
        final_actions: list[str] = []

        for step_id in range(max_steps_per_batch):
            readings = generate_sensor_stream_from_process_state(
                process_state,
                n=observation_window_min,
                seed=seed + batch_id * 101 + step_id,
            )
            readings = _apply_sensor_design(
                readings,
                sampling_interval_min=sampling_interval_min,
                disabled_sensors=disabled_sensors,
                sensor_noise_multiplier=sensor_noise_multiplier,
            )
            result = run_agent_chain(readings)
            final_plan = result.arbitration.metrics["final_plan"]
            final_actions = [str(action["action_id"]) for action in final_plan]
            all_actions.extend(final_actions)
            blocked_actions.extend(str(action) for action in result.arbitration.metrics["blocked_actions"])
            strategy_profiles.append(str(result.strategy_profile.metrics.get("selected_profile", "balanced")))
            validation_minutes += _validation_minutes(final_plan)
            regeneration_count += final_actions.count("regenerate_catalyst")
            replacement_count += final_actions.count("replace_catalyst")
            oxidant_dose_count += final_actions.count("dose_oxidant")

            next_state = apply_actions_to_process_state(process_state, final_plan)
            if next_state is None:
                success = "release" in final_actions
                terminal_state = process_state
                break
            process_state = next_state
            terminal_state = next_state

        catalyst_spares_remaining -= replacement_count
        oxidant_stock_units_remaining -= _oxidant_units_used(oxidant_dose_count)
        carried_catalyst = terminal_state
        records.append(
            BatchOperationRecord(
                batch_id=batch_id,
                scenario=scenario,
                success=success,
                steps=min(max_steps_per_batch, len(strategy_profiles)),
                elapsed_min=terminal_state.elapsed_min,
                cumulative_cost=round(terminal_state.cumulative_cost, 3),
                cumulative_energy=round(terminal_state.cumulative_energy, 3),
                final_actions=final_actions if strategy_profiles else [],
                all_actions=all_actions,
                blocked_actions=list(dict.fromkeys(blocked_actions)),
                strategy_profiles=strategy_profiles,
                validation_minutes=validation_minutes,
                regeneration_count=regeneration_count,
                replacement_count=replacement_count,
                oxidant_dose_count=oxidant_dose_count,
                catalyst_age_cycles_end=terminal_state.catalyst_age_cycles,
                catalyst_regen_count_end=terminal_state.catalyst_regen_count,
                catalyst_lifetime_fraction_end=round(terminal_state.catalyst_lifetime_fraction, 3),
                catalyst_activity_end=round(terminal_state.catalyst_activity, 3),
                terminal_label=terminal_state.label,
            )
        )

    return CampaignResult(
        records=records,
        catalyst_spares_remaining=catalyst_spares_remaining,
        oxidant_stock_units_remaining=round(oxidant_stock_units_remaining, 3),
        total_elapsed_min=sum(record.elapsed_min for record in records),
        total_cost=round(sum(record.cumulative_cost for record in records), 3),
        total_energy=round(sum(record.cumulative_energy for record in records), 3),
    )


def _initialize_batch_state(scenario: str, carried_catalyst: ProcessState | None) -> ProcessState:
    base = initial_process_state(scenario)
    if carried_catalyst is None:
        return base
    return replace(
        base,
        catalyst_activity=carried_catalyst.catalyst_activity,
        catalyst_age_cycles=carried_catalyst.catalyst_age_cycles,
        catalyst_regen_count=carried_catalyst.catalyst_regen_count,
        catalyst_lifetime_fraction=carried_catalyst.catalyst_lifetime_fraction,
    )


def _validation_minutes(final_plan: list[dict[str, object]]) -> int:
    total = 0
    for action in final_plan:
        if str(action.get("action_id")) != "hold_for_validation":
            continue
        parameters = action.get("parameters", {})
        if not isinstance(parameters, dict):
            continue
        hold_min = int(float(parameters.get("hold_min", 0)))
        validation_delay_min = int(float(parameters.get("validation_delay_min", 0)))
        total += hold_min + validation_delay_min
    return total


def _oxidant_units_used(oxidant_dose_count: int) -> float:
    return round(0.35 * oxidant_dose_count, 3)

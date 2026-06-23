import csv
from pathlib import Path

from water_ai.field_control_replay_package import (
    ACTUATOR_TABLE,
    EXPERT_LABEL_TABLE,
    REWARD_TABLE,
    SOURCE_ENV_VAR,
    TABLE_COLUMNS,
    TRANSITION_TABLE,
    UNSAFE_TABLE,
    build_field_control_replay_package_preflight,
    write_field_control_replay_package_template,
)


def test_field_control_replay_package_waits_for_external_dir() -> None:
    preflight = build_field_control_replay_package_preflight()

    assert preflight["source_env_var"] == SOURCE_ENV_VAR
    assert preflight["package_status"] == (
        "field_control_replay_package_waiting_for_FIELD_CONTROL_REPLAY_PACKAGE_DIR"
    )
    assert preflight["package_preflight_pass"] is False
    assert preflight["can_route_to_agent49_field_control_replay"] is False
    assert preflight["can_route_to_agent52_policy_replay_evaluation"] is False
    assert preflight["can_authorize_policy_promotion"] is False
    assert preflight["can_generate_field_evidence"] is False
    assert preflight["can_write_to_actuator"] is False
    assert preflight["can_write_to_release_gate"] is False
    assert "missing_external_package_dir" in preflight["blocking_reasons"]


def test_field_control_replay_package_blocks_template_rows(tmp_path: Path) -> None:
    write_field_control_replay_package_template(tmp_path)

    preflight = build_field_control_replay_package_preflight(
        source_dir=tmp_path,
        external_package_supplied=True,
    )

    assert preflight["package_preflight_pass"] is False
    assert preflight["package_status"] == "field_control_replay_package_blocked_at_field_origin"
    assert "template_markers_present" in preflight["blocking_reasons"]
    assert "non_field_rows_present" in preflight["blocking_reasons"]
    assert preflight["matched_transition_count"] == 0


def test_field_control_replay_package_accepts_minimum_field_transitions(
    tmp_path: Path,
) -> None:
    _write_valid_package(tmp_path)

    preflight = build_field_control_replay_package_preflight(
        source_dir=tmp_path,
        external_package_supplied=True,
    )

    assert preflight["package_status"] == "field_control_replay_package_ready_for_agent49_offline_replay"
    assert preflight["package_preflight_pass"] is True
    assert preflight["matched_transition_count"] == 3
    assert preflight["field_control_replay_coverage_candidate"] == 1.0
    assert preflight["reward_component_count"] == 3
    assert preflight["mean_actuator_latency_min"] == 2.0
    assert preflight["unsafe_or_override_transition_count"] == 1
    assert preflight["transition_audit"]["valid_row_count"] == 3
    assert preflight["reward_audit"]["valid_row_count"] == 3
    assert preflight["expert_label_audit"]["valid_row_count"] == 3
    assert preflight["actuator_audit"]["valid_row_count"] == 3
    assert preflight["unsafe_audit"]["valid_row_count"] == 3
    assert preflight["can_route_to_agent49_field_control_replay"] is True
    assert preflight["can_route_to_agent52_policy_replay_evaluation"] is True
    assert preflight["can_authorize_policy_promotion"] is False
    assert preflight["can_write_to_actuator"] is False
    assert preflight["can_write_to_release_gate"] is False
    assert "does not prove policy superiority" in preflight["field_boundary"]


def test_field_control_replay_package_blocks_missing_actuator_table(
    tmp_path: Path,
) -> None:
    _write_valid_package(tmp_path)
    (tmp_path / f"{ACTUATOR_TABLE}.csv").unlink()

    preflight = build_field_control_replay_package_preflight(
        source_dir=tmp_path,
        external_package_supplied=True,
    )

    assert preflight["package_preflight_pass"] is False
    assert preflight["package_status"] == "field_control_replay_package_blocked_at_schema"
    assert "missing_required_tables" in preflight["blocking_reasons"]
    assert "matched_transition_deficit" in preflight["blocking_reasons"]


def test_field_control_replay_package_blocks_invalid_actuator_latency(
    tmp_path: Path,
) -> None:
    _write_valid_package(tmp_path, invalid_latency=True)

    preflight = build_field_control_replay_package_preflight(
        source_dir=tmp_path,
        external_package_supplied=True,
    )

    assert preflight["package_preflight_pass"] is False
    assert preflight["package_status"] == "field_control_replay_package_blocked_at_transition_alignment"
    assert "insufficient_actuator_latency_result_rows" in preflight["blocking_reasons"]
    assert "matched_transition_deficit" in preflight["blocking_reasons"]


def _write_valid_package(root: Path, *, invalid_latency: bool = False) -> None:
    transition_ids = ["T001", "T002", "T003"]
    _write_csv(
        root / f"{TRANSITION_TABLE}.csv",
        TABLE_COLUMNS[TRANSITION_TABLE],
        [
            {
                "transition_id": transition_id,
                "batch_id": f"B{index:03d}",
                "facility_id": f"unit_{index}",
                "timestamp_min": str(index * 10),
                "state_vector_ref": f"state_{index}",
                "action_id": ["recycle", "hold", "dose_adjust"][index - 1],
                "next_state_vector_ref": f"next_state_{index}",
                "observed_outcome": "effluent_risk_reduced",
                "qa_flag": "pass",
                "data_origin": "field",
            }
            for index, transition_id in enumerate(transition_ids, start=1)
        ],
    )
    _write_csv(
        root / f"{REWARD_TABLE}.csv",
        TABLE_COLUMNS[REWARD_TABLE],
        [
            {
                "transition_id": transition_id,
                "reward_component": ["effluent_risk", "energy_cost", "safety_margin"][index - 1],
                "component_value": str(0.4 * index),
                "component_weight": "0.5",
                "objective_direction": "minimize",
                "qa_flag": "pass",
                "data_origin": "field",
            }
            for index, transition_id in enumerate(transition_ids, start=1)
        ],
    )
    _write_csv(
        root / f"{EXPERT_LABEL_TABLE}.csv",
        TABLE_COLUMNS[EXPERT_LABEL_TABLE],
        [
            {
                "transition_id": transition_id,
                "expert_action_id": ["recycle", "hold", "dose_adjust"][index - 1],
                "expert_action_label": "operator_confirmed_action",
                "reviewer_role": "process_engineer",
                "action_match_required": "true",
                "qa_flag": "pass",
                "data_origin": "field",
            }
            for index, transition_id in enumerate(transition_ids, start=1)
        ],
    )
    _write_csv(
        root / f"{ACTUATOR_TABLE}.csv",
        TABLE_COLUMNS[ACTUATOR_TABLE],
        [
            {
                "transition_id": transition_id,
                "actuator_id": f"pump_{index}",
                "commanded_action_id": ["recycle", "hold", "dose_adjust"][index - 1],
                "command_time_min": str(index * 10),
                "execution_time_min": str(index * 10 + 2),
                "latency_min": "5" if invalid_latency else "2",
                "execution_result": "success",
                "qa_flag": "pass",
                "data_origin": "field",
            }
            for index, transition_id in enumerate(transition_ids, start=1)
        ],
    )
    _write_csv(
        root / f"{UNSAFE_TABLE}.csv",
        TABLE_COLUMNS[UNSAFE_TABLE],
        [
            {
                "transition_id": transition_id,
                "unsafe_event_id": "U002" if index == 2 else "none",
                "unsafe_action_flag": "true" if index == 2 else "false",
                "override_flag": "true" if index == 2 else "false",
                "override_reason": "operator_override_due_to_high_ORP" if index == 2 else "none",
                "human_review_required": "true",
                "qa_flag": "pass",
                "data_origin": "field",
            }
            for index, transition_id in enumerate(transition_ids, start=1)
        ],
    )


def _write_csv(path: Path, columns: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)

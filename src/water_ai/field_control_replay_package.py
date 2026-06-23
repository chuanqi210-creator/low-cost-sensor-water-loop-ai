from __future__ import annotations

import csv
import math
from pathlib import Path
from typing import Any


PACKAGE_ID = "R8u152_field_control_replay_package_preflight"
SOURCE_ENV_VAR = "FIELD_CONTROL_REPLAY_PACKAGE_DIR"
MINIMUM_MATCHED_TRANSITION_COUNT = 3

TRANSITION_TABLE = "state_action_next_state_rows"
REWARD_TABLE = "reward_component_rows"
EXPERT_LABEL_TABLE = "operator_or_expert_action_labels"
ACTUATOR_TABLE = "actuator_latency_and_result_rows"
UNSAFE_TABLE = "unsafe_action_or_override_events"

REQUIRED_TABLES = (
    TRANSITION_TABLE,
    REWARD_TABLE,
    EXPERT_LABEL_TABLE,
    ACTUATOR_TABLE,
    UNSAFE_TABLE,
)

TABLE_COLUMNS = {
    TRANSITION_TABLE: [
        "transition_id",
        "batch_id",
        "facility_id",
        "timestamp_min",
        "state_vector_ref",
        "action_id",
        "next_state_vector_ref",
        "observed_outcome",
        "qa_flag",
        "data_origin",
    ],
    REWARD_TABLE: [
        "transition_id",
        "reward_component",
        "component_value",
        "component_weight",
        "objective_direction",
        "qa_flag",
        "data_origin",
    ],
    EXPERT_LABEL_TABLE: [
        "transition_id",
        "expert_action_id",
        "expert_action_label",
        "reviewer_role",
        "action_match_required",
        "qa_flag",
        "data_origin",
    ],
    ACTUATOR_TABLE: [
        "transition_id",
        "actuator_id",
        "commanded_action_id",
        "command_time_min",
        "execution_time_min",
        "latency_min",
        "execution_result",
        "qa_flag",
        "data_origin",
    ],
    UNSAFE_TABLE: [
        "transition_id",
        "unsafe_event_id",
        "unsafe_action_flag",
        "override_flag",
        "override_reason",
        "human_review_required",
        "qa_flag",
        "data_origin",
    ],
}

ACCEPTED_QA_FLAGS = {"pass", "passed", "valid", "ok", "qc_pass", "qualified", "合格"}
ACCEPTED_OBJECTIVE_DIRECTIONS = {
    "maximize",
    "minimize",
    "increase",
    "decrease",
    "reward",
    "penalty",
    "penalize",
    "reduce",
}


def build_field_control_replay_package_template(
    transition_ids: list[str] | None = None,
) -> dict[str, Any]:
    ids = transition_ids or [
        "TODO_transition_id_1",
        "TODO_transition_id_2",
        "TODO_transition_id_3",
    ]
    tables = {
        TRANSITION_TABLE: {
            "columns": TABLE_COLUMNS[TRANSITION_TABLE],
            "rows": [_transition_template_row(transition_id, index) for index, transition_id in enumerate(ids, start=1)],
        },
        REWARD_TABLE: {
            "columns": TABLE_COLUMNS[REWARD_TABLE],
            "rows": [_reward_template_row(transition_id) for transition_id in ids],
        },
        EXPERT_LABEL_TABLE: {
            "columns": TABLE_COLUMNS[EXPERT_LABEL_TABLE],
            "rows": [_expert_label_template_row(transition_id) for transition_id in ids],
        },
        ACTUATOR_TABLE: {
            "columns": TABLE_COLUMNS[ACTUATOR_TABLE],
            "rows": [_actuator_template_row(transition_id) for transition_id in ids],
        },
        UNSAFE_TABLE: {
            "columns": TABLE_COLUMNS[UNSAFE_TABLE],
            "rows": [_unsafe_template_row(transition_id) for transition_id in ids],
        },
    }
    return {
        "package_id": PACKAGE_ID,
        "package_type": "field_control_replay_package_template",
        "source_env_var": SOURCE_ENV_VAR,
        "required_table_count": len(REQUIRED_TABLES),
        "required_tables": list(REQUIRED_TABLES),
        "minimum_matched_transition_count": MINIMUM_MATCHED_TRANSITION_COUNT,
        "tables": tables,
        "table_row_counts": {name: len(table["rows"]) for name, table in tables.items()},
        "operator_instructions": [
            "Fill TODO values with real field state-action-next-state replay rows.",
            "Use at least three shared transition_id values across all five tables.",
            "Use data_origin=field for every row.",
            "Include operator/expert labels and unsafe/override review rows for every transition.",
            "Passing this preflight only routes the package to Agent49/Agent52 offline replay; it never authorizes live control.",
        ],
        "no_write_boundary": _no_write_boundary(),
    }


def write_field_control_replay_package_template(target_dir: str | Path) -> dict[str, Any]:
    target = Path(target_dir)
    target.mkdir(parents=True, exist_ok=True)
    template = build_field_control_replay_package_template()
    for table_name, table in template["tables"].items():
        _write_csv(target / f"{table_name}.csv", table["columns"], table["rows"])
    return template


def build_field_control_replay_package_preflight(
    *,
    source_dir: str | Path | None = None,
    external_package_supplied: bool = False,
) -> dict[str, Any]:
    source = Path(source_dir) if source_dir not in (None, "") else None
    if not external_package_supplied or source is None:
        return _preflight_payload(
            source_path="" if source is None else str(source),
            external_package_supplied=False,
            package_status="field_control_replay_package_waiting_for_FIELD_CONTROL_REPLAY_PACKAGE_DIR",
            table_audits={},
            transition_audit=_empty_signal_audit("state_action_transition"),
            reward_audit=_empty_signal_audit("reward_component"),
            expert_label_audit=_empty_signal_audit("operator_expert_action_label"),
            actuator_audit=_empty_signal_audit("actuator_latency_result"),
            unsafe_audit=_empty_signal_audit("unsafe_override_event"),
            matched_transition_ids=[],
            blocking_reasons=["missing_external_package_dir"],
        )
    if not source.exists() or not source.is_dir():
        return _preflight_payload(
            source_path=str(source),
            external_package_supplied=True,
            package_status="field_control_replay_package_blocked_at_missing_source_dir",
            table_audits={},
            transition_audit=_empty_signal_audit("state_action_transition"),
            reward_audit=_empty_signal_audit("reward_component"),
            expert_label_audit=_empty_signal_audit("operator_expert_action_label"),
            actuator_audit=_empty_signal_audit("actuator_latency_result"),
            unsafe_audit=_empty_signal_audit("unsafe_override_event"),
            matched_transition_ids=[],
            blocking_reasons=["source_dir_missing_or_not_directory"],
        )

    tables, table_audits = _read_tables(source)
    missing_tables = [name for name in REQUIRED_TABLES if not table_audits[name]["file_exists"]]
    header_gaps = [
        {"table": name, "missing_columns": audit["missing_columns"]}
        for name, audit in table_audits.items()
        if audit["missing_columns"]
    ]
    template_marker_count = sum(int(audit["template_marker_count"]) for audit in table_audits.values())
    non_field_row_count = sum(int(audit["non_field_row_count"]) for audit in table_audits.values())

    transition_audit = _transition_audit(tables.get(TRANSITION_TABLE, []))
    reward_audit = _reward_audit(tables.get(REWARD_TABLE, []))
    expert_label_audit = _expert_label_audit(tables.get(EXPERT_LABEL_TABLE, []))
    actuator_audit = _actuator_audit(tables.get(ACTUATOR_TABLE, []))
    unsafe_audit = _unsafe_audit(tables.get(UNSAFE_TABLE, []))
    matched_transition_ids = sorted(
        set(transition_audit["valid_transition_ids"])
        & set(reward_audit["valid_transition_ids"])
        & set(expert_label_audit["valid_transition_ids"])
        & set(actuator_audit["valid_transition_ids"])
        & set(unsafe_audit["valid_transition_ids"])
    )
    blocking_reasons = _blocking_reasons(
        missing_tables=missing_tables,
        header_gaps=header_gaps,
        template_marker_count=template_marker_count,
        non_field_row_count=non_field_row_count,
        transition_audit=transition_audit,
        reward_audit=reward_audit,
        expert_label_audit=expert_label_audit,
        actuator_audit=actuator_audit,
        unsafe_audit=unsafe_audit,
        matched_transition_ids=matched_transition_ids,
    )
    return _preflight_payload(
        source_path=str(source),
        external_package_supplied=True,
        package_status=_package_status(blocking_reasons),
        table_audits=table_audits,
        transition_audit=transition_audit,
        reward_audit=reward_audit,
        expert_label_audit=expert_label_audit,
        actuator_audit=actuator_audit,
        unsafe_audit=unsafe_audit,
        matched_transition_ids=matched_transition_ids,
        blocking_reasons=blocking_reasons,
    )


def _preflight_payload(
    *,
    source_path: str,
    external_package_supplied: bool,
    package_status: str,
    table_audits: dict[str, dict[str, Any]],
    transition_audit: dict[str, Any],
    reward_audit: dict[str, Any],
    expert_label_audit: dict[str, Any],
    actuator_audit: dict[str, Any],
    unsafe_audit: dict[str, Any],
    matched_transition_ids: list[str],
    blocking_reasons: list[str],
) -> dict[str, Any]:
    preflight_pass = external_package_supplied and not blocking_reasons
    coverage = round(
        min(1.0, len(matched_transition_ids) / MINIMUM_MATCHED_TRANSITION_COUNT),
        3,
    )
    return {
        "package_id": PACKAGE_ID,
        "package_type": "field_control_replay_package_preflight",
        "source_env_var": SOURCE_ENV_VAR,
        "source_path": source_path,
        "external_package_supplied": external_package_supplied,
        "package_status": package_status,
        "package_preflight_pass": preflight_pass,
        "required_table_count": len(REQUIRED_TABLES),
        "required_tables": list(REQUIRED_TABLES),
        "minimum_matched_transition_count": MINIMUM_MATCHED_TRANSITION_COUNT,
        "matched_transition_count": len(matched_transition_ids),
        "matched_transition_ids": matched_transition_ids,
        "field_control_replay_coverage_candidate": coverage,
        "unsafe_or_override_transition_count": int(unsafe_audit.get("unsafe_or_override_transition_count", 0) or 0),
        "mean_actuator_latency_min": actuator_audit.get("mean_latency_min"),
        "reward_component_count": int(reward_audit.get("reward_component_count", 0) or 0),
        "table_audits": table_audits,
        "transition_audit": transition_audit,
        "reward_audit": reward_audit,
        "expert_label_audit": expert_label_audit,
        "actuator_audit": actuator_audit,
        "unsafe_audit": unsafe_audit,
        "blocking_reasons": blocking_reasons,
        "can_route_to_agent49_field_control_replay": preflight_pass,
        "can_route_to_agent52_policy_replay_evaluation": preflight_pass,
        "can_authorize_policy_promotion": False,
        "can_generate_field_evidence": False,
        "can_resume_model_chain": False,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
        "next_operator_action": _next_operator_action(package_status),
        "field_boundary": (
            "This preflight only checks whether an external field control replay package is "
            "ready for Agent49/Agent52 offline evaluation. Passing this gate does not prove "
            "policy superiority, authorize live actuator writes, relax safety guardrails or "
            "open release-gate decisions."
        ),
        "no_write_boundary": _no_write_boundary(),
    }


def _read_tables(source: Path) -> tuple[dict[str, list[dict[str, str]]], dict[str, dict[str, Any]]]:
    tables: dict[str, list[dict[str, str]]] = {}
    audits: dict[str, dict[str, Any]] = {}
    for table_name in REQUIRED_TABLES:
        path = source / f"{table_name}.csv"
        required_columns = TABLE_COLUMNS[table_name]
        if not path.exists():
            audits[table_name] = {
                "file_exists": False,
                "row_count": 0,
                "missing_columns": required_columns,
                "template_marker_count": 0,
                "non_field_row_count": 0,
            }
            tables[table_name] = []
            continue
        rows, headers = _read_csv(path)
        audits[table_name] = {
            "file_exists": True,
            "row_count": len(rows),
            "missing_columns": [column for column in required_columns if column not in headers],
            "template_marker_count": sum(_row_has_template_marker(row) for row in rows),
            "non_field_row_count": sum(
                1 for row in rows if _normalize(row.get("data_origin")) != "field"
            ),
        }
        tables[table_name] = rows
    return tables, audits


def _transition_audit(rows: list[dict[str, str]]) -> dict[str, Any]:
    valid_ids = []
    facilities = set()
    batches = set()
    for row in rows:
        if not _row_common_valid(row):
            continue
        transition_id = str(row.get("transition_id", "")).strip()
        timestamp = _float(row.get("timestamp_min"))
        required_text = [
            "batch_id",
            "facility_id",
            "state_vector_ref",
            "action_id",
            "next_state_vector_ref",
            "observed_outcome",
        ]
        if timestamp is None or timestamp < 0 or any(not str(row.get(column, "")).strip() for column in required_text):
            continue
        valid_ids.append(transition_id)
        facilities.add(str(row.get("facility_id", "")).strip())
        batches.add(str(row.get("batch_id", "")).strip())
    return {
        "signal_family": "state_action_transition",
        "row_count": len(rows),
        "valid_row_count": len(valid_ids),
        "valid_transition_ids": sorted(set(valid_ids)),
        "facility_count": len(facilities),
        "batch_count": len(batches),
    }


def _reward_audit(rows: list[dict[str, str]]) -> dict[str, Any]:
    valid_ids = []
    components = set()
    weighted_values = []
    for row in rows:
        if not _row_common_valid(row):
            continue
        transition_id = str(row.get("transition_id", "")).strip()
        component = str(row.get("reward_component", "")).strip()
        value = _float(row.get("component_value"))
        weight = _float(row.get("component_weight"))
        direction = _normalize(row.get("objective_direction"))
        if (
            not component
            or value is None
            or weight is None
            or weight < 0
            or direction not in ACCEPTED_OBJECTIVE_DIRECTIONS
        ):
            continue
        valid_ids.append(transition_id)
        components.add(component)
        weighted_values.append(value * weight)
    return {
        "signal_family": "reward_component",
        "row_count": len(rows),
        "valid_row_count": len(valid_ids),
        "valid_transition_ids": sorted(set(valid_ids)),
        "reward_component_count": len(components),
        "reward_components": sorted(components),
        "mean_weighted_component_value": round(sum(weighted_values) / len(weighted_values), 3) if weighted_values else None,
    }


def _expert_label_audit(rows: list[dict[str, str]]) -> dict[str, Any]:
    valid_ids = []
    reviewer_roles = set()
    match_required_count = 0
    for row in rows:
        if not _row_common_valid(row):
            continue
        transition_id = str(row.get("transition_id", "")).strip()
        match_required = _bool(row.get("action_match_required"))
        if match_required is None or any(
            not str(row.get(column, "")).strip()
            for column in ["expert_action_id", "expert_action_label", "reviewer_role"]
        ):
            continue
        valid_ids.append(transition_id)
        reviewer_roles.add(str(row.get("reviewer_role", "")).strip())
        if match_required:
            match_required_count += 1
    return {
        "signal_family": "operator_expert_action_label",
        "row_count": len(rows),
        "valid_row_count": len(valid_ids),
        "valid_transition_ids": sorted(set(valid_ids)),
        "reviewer_roles": sorted(reviewer_roles),
        "action_match_required_row_count": match_required_count,
    }


def _actuator_audit(rows: list[dict[str, str]]) -> dict[str, Any]:
    valid_ids = []
    latencies = []
    execution_results = set()
    for row in rows:
        if not _row_common_valid(row):
            continue
        transition_id = str(row.get("transition_id", "")).strip()
        command_time = _float(row.get("command_time_min"))
        execution_time = _float(row.get("execution_time_min"))
        latency = _float(row.get("latency_min"))
        if any(
            not str(row.get(column, "")).strip()
            for column in ["actuator_id", "commanded_action_id", "execution_result"]
        ):
            continue
        if (
            command_time is None
            or execution_time is None
            or latency is None
            or command_time < 0
            or execution_time < 0
            or latency < 0
            or execution_time < command_time
            or abs((execution_time - command_time) - latency) > 1e-6
        ):
            continue
        valid_ids.append(transition_id)
        latencies.append(latency)
        execution_results.add(str(row.get("execution_result", "")).strip())
    return {
        "signal_family": "actuator_latency_result",
        "row_count": len(rows),
        "valid_row_count": len(valid_ids),
        "valid_transition_ids": sorted(set(valid_ids)),
        "mean_latency_min": round(sum(latencies) / len(latencies), 3) if latencies else None,
        "execution_results": sorted(execution_results),
    }


def _unsafe_audit(rows: list[dict[str, str]]) -> dict[str, Any]:
    valid_ids = []
    unsafe_or_override_ids = []
    human_review_count = 0
    for row in rows:
        if not _row_common_valid(row):
            continue
        transition_id = str(row.get("transition_id", "")).strip()
        unsafe = _bool(row.get("unsafe_action_flag"))
        override = _bool(row.get("override_flag"))
        review_required = _bool(row.get("human_review_required"))
        unsafe_event_id = str(row.get("unsafe_event_id", "")).strip()
        override_reason = str(row.get("override_reason", "")).strip()
        if (
            unsafe is None
            or override is None
            or review_required is None
            or not unsafe_event_id
            or not override_reason
            or not review_required
        ):
            continue
        valid_ids.append(transition_id)
        human_review_count += 1
        if unsafe or override:
            unsafe_or_override_ids.append(transition_id)
    return {
        "signal_family": "unsafe_override_event",
        "row_count": len(rows),
        "valid_row_count": len(valid_ids),
        "valid_transition_ids": sorted(set(valid_ids)),
        "unsafe_or_override_transition_count": len(set(unsafe_or_override_ids)),
        "human_review_required_row_count": human_review_count,
    }


def _blocking_reasons(
    *,
    missing_tables: list[str],
    header_gaps: list[dict[str, Any]],
    template_marker_count: int,
    non_field_row_count: int,
    transition_audit: dict[str, Any],
    reward_audit: dict[str, Any],
    expert_label_audit: dict[str, Any],
    actuator_audit: dict[str, Any],
    unsafe_audit: dict[str, Any],
    matched_transition_ids: list[str],
) -> list[str]:
    reasons: list[str] = []
    if missing_tables:
        reasons.append("missing_required_tables")
    if header_gaps:
        reasons.append("missing_required_columns")
    if template_marker_count > 0:
        reasons.append("template_markers_present")
    if non_field_row_count > 0:
        reasons.append("non_field_rows_present")
    signal_requirements = [
        ("insufficient_state_action_transition_rows", transition_audit),
        ("insufficient_reward_component_rows", reward_audit),
        ("insufficient_operator_expert_label_rows", expert_label_audit),
        ("insufficient_actuator_latency_result_rows", actuator_audit),
        ("insufficient_unsafe_override_rows", unsafe_audit),
    ]
    for reason, audit in signal_requirements:
        if int(audit.get("valid_row_count", 0) or 0) < MINIMUM_MATCHED_TRANSITION_COUNT:
            reasons.append(reason)
    if len(matched_transition_ids) < MINIMUM_MATCHED_TRANSITION_COUNT:
        reasons.append("matched_transition_deficit")
    return reasons


def _package_status(blocking_reasons: list[str]) -> str:
    if not blocking_reasons:
        return "field_control_replay_package_ready_for_agent49_offline_replay"
    if "missing_required_tables" in blocking_reasons or "missing_required_columns" in blocking_reasons:
        return "field_control_replay_package_blocked_at_schema"
    if "template_markers_present" in blocking_reasons or "non_field_rows_present" in blocking_reasons:
        return "field_control_replay_package_blocked_at_field_origin"
    if "matched_transition_deficit" in blocking_reasons:
        return "field_control_replay_package_blocked_at_transition_alignment"
    return "field_control_replay_package_blocked_at_content_preflight"


def _next_operator_action(package_status: str) -> str:
    if package_status == "field_control_replay_package_ready_for_agent49_offline_replay":
        return "route_FIELD_CONTROL_REPLAY_PACKAGE_DIR_to_Agent49_Agent52_offline_control_replay_consumer"
    if package_status == "field_control_replay_package_blocked_at_missing_source_dir":
        return "repair_FIELD_CONTROL_REPLAY_PACKAGE_DIR_path"
    if package_status == "field_control_replay_package_blocked_at_schema":
        return "repair_FIELD_CONTROL_REPLAY_PACKAGE_csv_headers_and_required_tables"
    if package_status == "field_control_replay_package_blocked_at_field_origin":
        return "replace_template_or_non_field_control_replay_rows_with_real_field_rows"
    if package_status == "field_control_replay_package_blocked_at_transition_alignment":
        return "add_at_least_three_shared_transition_ids_across_all_control_replay_tables"
    return "fill_field_control_replay_package_template_and_set_FIELD_CONTROL_REPLAY_PACKAGE_DIR"


def _empty_signal_audit(signal_family: str) -> dict[str, Any]:
    return {
        "signal_family": signal_family,
        "row_count": 0,
        "valid_row_count": 0,
        "valid_transition_ids": [],
    }


def _row_common_valid(row: dict[str, str]) -> bool:
    transition_id = str(row.get("transition_id", "")).strip()
    if not transition_id or "TODO" in transition_id:
        return False
    return _normalize(row.get("qa_flag")) in ACCEPTED_QA_FLAGS and _normalize(
        row.get("data_origin")
    ) == "field"


def _read_csv(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = [dict(row) for row in reader]
        return rows, list(reader.fieldnames or [])


def _write_csv(path: Path, columns: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def _row_has_template_marker(row: dict[str, str]) -> bool:
    return any(_has_template_marker(value) for value in row.values())


def _has_template_marker(value: object) -> bool:
    text = str(value or "").strip().lower()
    return not text or "todo" in text or "template" in text or "placeholder" in text


def _float(value: object) -> float | None:
    try:
        parsed = float(str(value).strip())
    except (TypeError, ValueError):
        return None
    if not math.isfinite(parsed):
        return None
    return parsed


def _bool(value: object) -> bool | None:
    text = _normalize(value)
    if text in {"true", "1", "yes", "y", "required", "是"}:
        return True
    if text in {"false", "0", "no", "n", "not_required", "none", "否"}:
        return False
    return None


def _normalize(value: object) -> str:
    return str(value or "").strip().lower()


def _no_write_boundary() -> str:
    return (
        "This package is only a field control replay preflight input. It cannot write "
        "actuator policy, release-gate policy, live control approval, policy-promotion "
        "claims or deployment clearance."
    )


def _transition_template_row(transition_id: str, index: int) -> dict[str, str]:
    return {
        "transition_id": transition_id,
        "batch_id": f"TODO_batch_{index}",
        "facility_id": "TODO_facility_or_unit_id",
        "timestamp_min": "TODO_numeric",
        "state_vector_ref": "TODO_state_vector_ref",
        "action_id": "TODO_action_id",
        "next_state_vector_ref": "TODO_next_state_vector_ref",
        "observed_outcome": "TODO_observed_outcome",
        "qa_flag": "TODO_pass",
        "data_origin": "TODO_field",
    }


def _reward_template_row(transition_id: str) -> dict[str, str]:
    return {
        "transition_id": transition_id,
        "reward_component": "TODO_effluent_risk_or_cost_or_energy_or_safety",
        "component_value": "TODO_numeric",
        "component_weight": "TODO_numeric",
        "objective_direction": "TODO_minimize_or_maximize",
        "qa_flag": "TODO_pass",
        "data_origin": "TODO_field",
    }


def _expert_label_template_row(transition_id: str) -> dict[str, str]:
    return {
        "transition_id": transition_id,
        "expert_action_id": "TODO_expert_action_id",
        "expert_action_label": "TODO_operator_or_expert_action",
        "reviewer_role": "TODO_operator_engineer_or_process_expert",
        "action_match_required": "TODO_true_or_false",
        "qa_flag": "TODO_pass",
        "data_origin": "TODO_field",
    }


def _actuator_template_row(transition_id: str) -> dict[str, str]:
    return {
        "transition_id": transition_id,
        "actuator_id": "TODO_pump_valve_doser_or_recycle_controller",
        "commanded_action_id": "TODO_action_id",
        "command_time_min": "TODO_numeric",
        "execution_time_min": "TODO_numeric",
        "latency_min": "TODO_numeric",
        "execution_result": "TODO_success_blocked_or_operator_override",
        "qa_flag": "TODO_pass",
        "data_origin": "TODO_field",
    }


def _unsafe_template_row(transition_id: str) -> dict[str, str]:
    return {
        "transition_id": transition_id,
        "unsafe_event_id": "TODO_event_id_or_none",
        "unsafe_action_flag": "TODO_true_or_false",
        "override_flag": "TODO_true_or_false",
        "override_reason": "TODO_reason_or_none",
        "human_review_required": "TODO_true",
        "qa_flag": "TODO_pass",
        "data_origin": "TODO_field",
    }

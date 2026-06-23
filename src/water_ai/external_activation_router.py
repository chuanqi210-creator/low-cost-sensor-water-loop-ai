from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from water_ai.agents.agent_architecture_consolidation_agent import (
    AgentArchitectureConsolidationAgent,
)
from water_ai.agents.field_replay_import_agent import preflight_field_replay_package
from water_ai.agents.soft_sensor_matrix_coupling_agent import (
    preflight_field_path_endpoint_label_package,
)


ROUTE_SPECS: dict[str, dict[str, object]] = {
    "R7_REAL_FIELD_PACKAGE": {
        "package_pointer": "REAL_FIELD_REPLAY_PACKAGE_DIR",
        "expected_path_type": "directory",
        "route_status_ready": "activation_route_ready_for_r7_pipeline_execution",
        "execution_target": "experiments/run_r7_real_field_replay_pipeline.py",
        "resumes_to": [
            "Agent44 field import preflight",
            "Agent42 timestamped campaign replay",
            "Agent43 G6/P6 calibration gate",
            "Agent45 field replay evidence chain",
        ],
    },
    "R8U66_PATH_ENDPOINT_LABEL_PACKAGE": {
        "package_pointer": "FIELD_PATH_ENDPOINT_LABEL_PACKAGE_DIR",
        "expected_path_type": "directory",
        "route_status_ready": "activation_route_ready_for_path_endpoint_layout_holdout",
        "execution_target": "preflight_field_path_endpoint_label_package",
        "resumes_to": [
            "Agent54 field layout holdout",
            "soft-sensor endpoint/path validation",
        ],
    },
    "R8U79_FORMAL_SEARCH_RESULT_PACKAGE": {
        "package_pointer": "FORMAL_SEARCH_RESULT_PACKAGE_PATH",
        "expected_path_type": "file",
        "route_status_ready": "activation_route_ready_for_agent60_formal_search_preflight",
        "execution_target": "experiments/run_agent60_agent_architecture_consolidation.py",
        "resumes_to": [
            "formal search result source preflight",
            "formal search row preflight",
            "nonlegal comparison review packet",
        ],
    },
}


def build_external_activation_router(
    contract: dict[str, Any],
    *,
    env: dict[str, str] | None = None,
    project_root: str | Path | None = None,
    catalyst_slice_r7_patch_candidate_metrics: dict[str, Any] | None = None,
    field_activation_external_readiness_gate: dict[str, Any] | None = None,
    field_activation_response_submission_packet: dict[str, Any] | None = None,
    field_activation_response_focus_handoff: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Turn the Agent50 activation contract into a concrete path-aware route plan."""

    env = env or {}
    root = Path(project_root).resolve() if project_root else Path.cwd().resolve()
    channels = contract.get("channels", [])
    catalyst_patch_candidate = _catalyst_patch_candidate_summary(
        catalyst_slice_r7_patch_candidate_metrics
    )
    field_activation_upstream = _field_activation_upstream_summary(
        field_activation_external_readiness_gate,
        field_activation_response_submission_packet,
        field_activation_response_focus_handoff,
    )
    route_rows = [
        _route_for_channel(
            channel,
            env=env,
            project_root=root,
            catalyst_patch_candidate=catalyst_patch_candidate,
            field_activation_upstream=field_activation_upstream,
        )
        for channel in channels
        if isinstance(channel, dict)
    ]
    ready_rows = [row for row in route_rows if row["route_ready"]]
    model_chain_ready_rows = [
        row for row in ready_rows if bool(row.get("can_resume_model_chain", False))
    ]
    handoff_ready_rows = [
        row for row in ready_rows if not bool(row.get("can_resume_model_chain", False))
    ]
    supplied_rows = [row for row in route_rows if row["path_supplied"]]
    boundary_preserved = bool(contract.get("boundary_preserved", False)) and all(
        row["boundary_preserved"] for row in route_rows
    )
    priority_route = _priority_route(route_rows)
    return {
        "router_id": "R8u82_external_activation_router",
        "source_contract_id": contract.get("contract_id", "unknown_contract"),
        "router_status": (
            "external_activation_router_has_model_chain_ready_routes"
            if model_chain_ready_rows
            else (
                "external_activation_router_has_handoff_ready_routes"
                if handoff_ready_rows
                else "external_activation_router_waiting_for_external_paths"
            )
        ),
        "path_supplied_count": len(supplied_rows),
        "route_ready_count": len(ready_rows),
        "model_chain_ready_route_count": len(model_chain_ready_rows),
        "handoff_ready_route_count": len(handoff_ready_rows),
        "blocked_route_count": len(route_rows) - len(ready_rows),
        "ready_channel_ids": [str(row["channel_id"]) for row in ready_rows],
        "model_chain_ready_channel_ids": [
            str(row["channel_id"]) for row in model_chain_ready_rows
        ],
        "handoff_ready_channel_ids": [
            str(row["channel_id"]) for row in handoff_ready_rows
        ],
        "blocked_channel_ids": [
            str(row["channel_id"]) for row in route_rows if not row["route_ready"]
        ],
        "priority_route_channel_id": str(priority_route.get("channel_id", "")),
        "priority_route_status": str(priority_route.get("route_status", "")),
        "priority_route_ready": bool(priority_route.get("route_ready", False)),
        "priority_route_can_resume_model_chain": bool(
            priority_route.get("can_resume_model_chain", False)
        ),
        "priority_route_preflight_status": _route_preflight_status(priority_route),
        "highest_priority_blocker": _highest_priority_blocker(priority_route),
        "next_operator_action": _next_operator_action(priority_route),
        "router_validation_command": ".venv/bin/python experiments/run_external_activation_router.py",
        "priority_route_command": str(priority_route.get("command_preview", "")),
        "catalyst_patch_candidate_consumed": bool(catalyst_patch_candidate["consumed"]),
        "catalyst_patch_candidate_status": str(catalyst_patch_candidate["patch_status"]),
        "catalyst_patch_candidate_materialized": bool(
            catalyst_patch_candidate["candidate_materialized"]
        ),
        "catalyst_patch_candidate_preflight_status": str(
            catalyst_patch_candidate["candidate_preflight_status"]
        ),
        "catalyst_patch_candidate_remaining_gap_count": int(
            catalyst_patch_candidate["remaining_gap_count"]
        ),
        "catalyst_patch_candidate_can_submit_as_REAL_FIELD_REPLAY_PACKAGE_DIR": bool(
            catalyst_patch_candidate["can_submit_candidate_as_REAL_FIELD_REPLAY_PACKAGE_DIR"]
        ),
        "catalyst_patch_candidate_package_dir": str(
            catalyst_patch_candidate["candidate_package_dir"]
        ),
        "field_activation_upstream_consumed": bool(field_activation_upstream["consumed"]),
        "field_activation_upstream_status": str(field_activation_upstream["status"]),
        "field_activation_upstream_first_blocked_step": str(
            field_activation_upstream["first_blocked_step"]
        ),
        "field_activation_upstream_highest_priority_blocker": str(
            field_activation_upstream["highest_priority_blocker"]
        ),
        "field_activation_upstream_next_operator_action": str(
            field_activation_upstream["next_operator_action"]
        ),
        "field_activation_upstream_can_submit_to_external_activation_router": bool(
            field_activation_upstream["can_submit_to_external_activation_router"]
        ),
        "field_activation_upstream_submission_packet_status": str(
            field_activation_upstream["submission_packet_status"]
        ),
        "field_activation_upstream_focus_handoff_status": str(
            field_activation_upstream["focus_handoff_status"]
        ),
        "field_activation_upstream_focus_handoff_target_hidden_state": str(
            field_activation_upstream["focus_handoff_target_hidden_state"]
        ),
        "field_activation_upstream_focus_handoff_source_env_var": str(
            field_activation_upstream["focus_handoff_source_env_var"]
        ),
        "field_activation_upstream_focus_handoff_repair_work_order_status": str(
            field_activation_upstream["focus_handoff_repair_work_order_status"]
        ),
        "field_activation_upstream_focus_handoff_repair_item_count": int(
            field_activation_upstream["focus_handoff_repair_item_count"]
        ),
        "field_activation_upstream_focus_handoff_repair_next_operator_action": str(
            field_activation_upstream["focus_handoff_repair_next_operator_action"]
        ),
        "boundary_preserved": boundary_preserved,
        "route_rows": route_rows,
        "next_commands": [
            row["command_preview"]
            for row in route_rows
            if row.get("command_preview") and row["route_ready"]
        ],
        "global_no_write_boundary": (
            "This router only prepares preflight/execution routes. It never writes actuator policy, release-gate "
            "clearance, patent/legal conclusions or field-supported claims."
        ),
    }


def _priority_route(route_rows: list[dict[str, Any]]) -> dict[str, Any]:
    supplied_blocked = [
        row for row in route_rows if bool(row.get("path_supplied", False)) and not bool(row.get("route_ready", False))
    ]
    if supplied_blocked:
        return supplied_blocked[0]
    ready_rows = [row for row in route_rows if bool(row.get("route_ready", False))]
    if ready_rows:
        return ready_rows[0]
    blocked_rows = [row for row in route_rows if not bool(row.get("route_ready", False))]
    return blocked_rows[0] if blocked_rows else {}


def _highest_priority_blocker(route: dict[str, Any]) -> str:
    if not route:
        return "external_activation_router_no_route_rows"
    if bool(route.get("route_ready", False)):
        return ""
    channel_id = str(route.get("channel_id", "unknown_channel"))
    blocked_reason = str(route.get("blocked_reason", "") or route.get("route_status", "unknown_route_status"))
    preflight_status = _route_preflight_status(route)
    if preflight_status != "-":
        return f"{channel_id}:{blocked_reason}:{preflight_status}"
    return f"{channel_id}:{blocked_reason}"


def _next_operator_action(route: dict[str, Any]) -> str:
    if not route:
        return "submit_or_set_one_external_activation_package_path"
    action = str(route.get("operator_action", ""))
    if action:
        return action
    command = str(route.get("command_preview", ""))
    if bool(route.get("route_ready", False)) and command:
        return command
    return "inspect_external_activation_router_route_summary"


def _route_preflight_status(route: dict[str, Any]) -> str:
    field_preflight = route.get("field_package_preflight")
    if isinstance(field_preflight, dict):
        return str(field_preflight.get("status", "field_package_preflight_unknown"))
    path_preflight = route.get("path_endpoint_preflight")
    if isinstance(path_preflight, dict):
        return str(path_preflight.get("preflight_status", "path_endpoint_preflight_unknown"))
    formal_row_preflight = route.get("formal_search_result_package_row_preflight")
    if isinstance(formal_row_preflight, dict):
        return str(
            formal_row_preflight.get(
                "formal_search_result_package_row_preflight_status",
                "formal_search_result_package_row_preflight_unknown",
            )
        )
    formal_source_preflight = route.get("formal_search_result_package_source_preflight")
    if isinstance(formal_source_preflight, dict):
        return str(
            formal_source_preflight.get(
                "formal_search_result_package_source_status",
                "formal_search_result_package_source_preflight_unknown",
            )
        )
    field_activation_upstream = route.get("field_activation_upstream_gate")
    if isinstance(field_activation_upstream, dict) and field_activation_upstream.get("consumed", False):
        return str(
            field_activation_upstream.get(
                "status",
                "field_activation_upstream_status_unknown",
            )
        )
    return "-"


def _route_for_channel(
    channel: dict[str, Any],
    *,
    env: dict[str, str],
    project_root: Path,
    catalyst_patch_candidate: dict[str, Any],
    field_activation_upstream: dict[str, Any],
) -> dict[str, Any]:
    channel_id = str(channel.get("channel_id", "unknown_channel"))
    spec = ROUTE_SPECS.get(channel_id, {})
    pointer = str(spec.get("package_pointer") or channel.get("package_pointer", ""))
    raw_path = env.get(pointer, "").strip() if pointer else ""
    base_row: dict[str, Any] = {
        "channel_id": channel_id,
        "package_pointer": pointer,
        "expected_path_type": spec.get("expected_path_type", "unknown"),
        "path_supplied": bool(raw_path),
        "submitted_path": raw_path,
        "route_ready": False,
        "can_resume_model_chain": False,
        "execution_target": spec.get("execution_target", "manual_review"),
        "command_preview": "",
        "boundary_preserved": True,
        "no_write_boundary": channel.get("no_write_boundary", ""),
        "resumes_to": spec.get("resumes_to", channel.get("resumes_to", [])),
    }
    if channel_id == "R7_REAL_FIELD_PACKAGE":
        base_row["catalyst_slice_r7_patch_candidate"] = catalyst_patch_candidate
        if field_activation_upstream.get("consumed", False):
            base_row["field_activation_upstream_gate"] = field_activation_upstream
    if not pointer:
        return {
            **base_row,
            "route_status": "activation_route_unknown_channel",
            "blocked_reason": "channel_id_not_registered_in_router",
        }
    if not raw_path:
        operator_action = f"set_{pointer}"
        route_status = "activation_route_waiting_for_env_var"
        blocked_reason = f"{pointer}:not_set"
        if (
            channel_id == "R7_REAL_FIELD_PACKAGE"
            and catalyst_patch_candidate.get(
                "can_submit_candidate_as_REAL_FIELD_REPLAY_PACKAGE_DIR",
                False,
            )
        ):
            operator_action = "set_REAL_FIELD_REPLAY_PACKAGE_DIR_to_catalyst_patch_candidate"
        elif (
            channel_id == "R7_REAL_FIELD_PACKAGE"
            and field_activation_upstream.get("consumed", False)
            and not field_activation_upstream.get(
                "can_submit_to_external_activation_router",
                False,
            )
        ):
            operator_action = str(
                field_activation_upstream.get(
                    "next_operator_action",
                    "complete_field_activation_upstream_gate_before_REAL_FIELD_REPLAY_PACKAGE_DIR",
                )
            )
            route_status = "activation_route_blocked_by_field_activation_upstream_gate"
            blocker = str(
                field_activation_upstream.get(
                    "highest_priority_blocker",
                    "field_activation_upstream_not_ready",
                )
            )
            blocked_reason = f"field_activation_upstream_not_ready:{blocker}"
        return {
            **base_row,
            "route_status": route_status,
            "blocked_reason": blocked_reason,
            "operator_action": operator_action,
        }
    submitted = Path(raw_path).expanduser()
    if not submitted.is_absolute():
        submitted = (project_root / submitted).resolve()
    else:
        submitted = submitted.resolve()
    base_row["submitted_path"] = str(submitted)
    if not submitted.exists():
        return {
            **base_row,
            "route_status": "activation_route_path_missing",
            "blocked_reason": f"{pointer}:path_missing",
            "operator_action": f"repair_{pointer}_path",
        }
    expected_type = str(spec.get("expected_path_type", "unknown"))
    if expected_type == "directory" and not submitted.is_dir():
        return {
            **base_row,
            "route_status": "activation_route_invalid_path_type",
            "blocked_reason": f"{pointer}:expected_directory",
            "operator_action": f"submit_directory_for_{pointer}",
        }
    if expected_type == "file" and not submitted.is_file():
        return {
            **base_row,
            "route_status": "activation_route_invalid_path_type",
            "blocked_reason": f"{pointer}:expected_file",
            "operator_action": f"submit_file_for_{pointer}",
        }
    if channel_id == "R7_REAL_FIELD_PACKAGE":
        return _field_package_route(base_row, submitted)
    if channel_id == "R8U66_PATH_ENDPOINT_LABEL_PACKAGE":
        return _path_endpoint_route(base_row, submitted)
    if channel_id == "R8U79_FORMAL_SEARCH_RESULT_PACKAGE":
        return _formal_search_result_route(base_row, submitted)
    command = _command_preview(pointer, submitted, str(spec.get("execution_target", "")))
    return {
        **base_row,
        "route_status": spec.get("route_status_ready", "activation_route_ready"),
        "route_ready": True,
        "can_resume_model_chain": channel_id == "R7_REAL_FIELD_PACKAGE",
        "command_preview": command,
        "blocked_reason": "",
        "operator_action": "run_preflight_or_pipeline_command",
    }


def _field_package_route(base_row: dict[str, Any], submitted: Path) -> dict[str, Any]:
    try:
        preflight = preflight_field_replay_package(submitted)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return {
            **base_row,
            "route_status": "activation_route_blocked_by_field_package_preflight_error",
            "route_ready": False,
            "can_resume_model_chain": False,
            "command_preview": "",
            "blocked_reason": "field_package_preflight_error",
            "operator_action": "repair_REAL_FIELD_REPLAY_PACKAGE_DIR_package_format",
            "field_package_preflight": {
                "status": "field_package_preflight_error",
                "error_type": type(exc).__name__,
                "error_message": str(exc),
            },
        }
    ready = bool(preflight.get("can_pass_to_timestamped_replay", False))
    command = _command_preview(
        "REAL_FIELD_REPLAY_PACKAGE_DIR",
        submitted,
        "experiments/run_r7_real_field_replay_pipeline.py",
    )
    return {
        **base_row,
        "route_status": (
            "activation_route_ready_for_r7_pipeline_execution"
            if ready
            else "activation_route_blocked_by_field_package_preflight"
        ),
        "route_ready": ready,
        "can_resume_model_chain": ready,
        "command_preview": command if ready else "",
        "blocked_reason": "" if ready else "field_package_preflight_not_ready",
        "operator_action": (
            "run_preflight_or_pipeline_command"
            if ready
            else _first_next_action(preflight, "repair_REAL_FIELD_REPLAY_PACKAGE_DIR_package")
        ),
        "field_package_preflight": preflight,
    }


def _path_endpoint_route(base_row: dict[str, Any], submitted: Path) -> dict[str, Any]:
    package = _read_csv_package(submitted)
    preflight = preflight_field_path_endpoint_label_package(package)
    ready = bool(preflight.get("can_route_to_field_layout_holdout", False))
    command = (
        f"FIELD_PATH_ENDPOINT_LABEL_PACKAGE_DIR={_shell_path(submitted)} "
        ".venv/bin/python experiments/run_external_activation_router.py"
    )
    return {
        **base_row,
        "route_status": (
            "activation_route_ready_for_path_endpoint_layout_holdout"
            if ready
            else "activation_route_blocked_by_path_endpoint_preflight"
        ),
        "route_ready": ready,
        "can_resume_model_chain": ready,
        "command_preview": command,
        "blocked_reason": "" if ready else "field_path_endpoint_preflight_not_ready",
        "operator_action": (
            "route_to_field_layout_holdout_review"
            if ready
            else preflight.get("next_operator_action", "repair_path_endpoint_package")
        ),
        "path_endpoint_preflight": preflight,
    }


def _formal_search_result_route(base_row: dict[str, Any], submitted: Path) -> dict[str, Any]:
    try:
        report = AgentArchitectureConsolidationAgent(
            formal_search_result_package_path=str(submitted)
        ).run([])
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return {
            **base_row,
            "route_status": "activation_route_blocked_by_formal_search_preflight_error",
            "route_ready": False,
            "can_resume_model_chain": False,
            "command_preview": "",
            "blocked_reason": "formal_search_result_preflight_error",
            "operator_action": "repair_FORMAL_SEARCH_RESULT_PACKAGE_PATH_package_format",
            "formal_search_result_package_source_preflight": {
                "formal_search_result_package_source_status": "formal_search_result_package_preflight_error",
                "error_type": type(exc).__name__,
                "error_message": str(exc),
            },
            "formal_search_result_package_row_preflight": {
                "formal_search_result_package_row_preflight_status": (
                    "formal_search_result_package_row_preflight_blocked_at_source_preflight"
                ),
                "can_route_to_validation_gate": False,
            },
        }
    source_preflight = report.metrics["formal_search_result_package_source_preflight"]
    row_preflight = report.metrics["formal_search_result_package_row_preflight"]
    validation_execution = report.metrics["formal_search_result_validation_execution"]
    ready = bool(row_preflight.get("can_route_to_validation_gate", False))
    command = _command_preview(
        "FORMAL_SEARCH_RESULT_PACKAGE_PATH",
        submitted,
        "experiments/run_agent60_agent_architecture_consolidation.py",
    )
    return {
        **base_row,
        "route_status": (
            "activation_route_ready_for_agent60_formal_search_preflight"
            if ready
            else "activation_route_blocked_by_formal_search_result_preflight"
        ),
        "route_ready": ready,
        "can_resume_model_chain": False,
        "command_preview": command if ready else "",
        "blocked_reason": "" if ready else "formal_search_result_preflight_not_ready",
        "operator_action": (
            "run_preflight_or_pipeline_command"
            if ready
            else _first_next_action(row_preflight, _first_next_action(source_preflight, "repair_FORMAL_SEARCH_RESULT_PACKAGE_PATH"))
        ),
        "formal_search_result_package_source_preflight": source_preflight,
        "formal_search_result_package_row_preflight": row_preflight,
        "formal_search_result_validation_execution": validation_execution,
    }


def _first_next_action(preflight: dict[str, Any], default: str) -> str:
    next_actions = preflight.get("next_actions", [])
    if isinstance(next_actions, list) and next_actions:
        return str(next_actions[0])
    blockers = preflight.get("preflight_blockers", [])
    if isinstance(blockers, list) and blockers:
        return str(blockers[0])
    return default


def _catalyst_patch_candidate_summary(
    metrics: dict[str, Any] | None,
) -> dict[str, Any]:
    if not isinstance(metrics, dict) or not metrics:
        return {
            "consumed": False,
            "patch_status": "catalyst_slice_r7_patch_candidate_not_consumed_by_external_activation_router",
            "candidate_materialized": False,
            "candidate_preflight_status": "not_consumed",
            "remaining_gap_count": 0,
            "can_submit_candidate_as_REAL_FIELD_REPLAY_PACKAGE_DIR": False,
            "can_route_to_agent51_field_proxy_holdout": False,
            "candidate_package_dir": "",
            "source_slice_path": "",
            "next_operator_action": "run_catalyst_slice_r7_patch_candidate_before_router_consumption",
            "candidate_submission_boundary": (
                "No catalyst R7 patch candidate metrics were consumed. R7 remains gated by "
                "REAL_FIELD_REPLAY_PACKAGE_DIR and full field preflight."
            ),
        }
    gap_summary = metrics.get("full_package_gap_summary", {})
    if not isinstance(gap_summary, dict):
        gap_summary = {}
    try:
        remaining_gap_count = int(
            metrics.get(
                "remaining_gap_count",
                gap_summary.get("remaining_gap_count", 0),
            )
            or 0
        )
    except (TypeError, ValueError):
        remaining_gap_count = 0
    can_submit = bool(
        metrics.get("can_submit_candidate_as_REAL_FIELD_REPLAY_PACKAGE_DIR", False)
    )
    candidate_dir = str(
        metrics.get("candidate_package_dir")
        or metrics.get("candidate_package_dir_relative")
        or ""
    )
    return {
        "consumed": True,
        "patch_status": str(
            metrics.get(
                "patch_status",
                "catalyst_slice_r7_patch_candidate_status_unknown",
            )
        ),
        "candidate_materialized": bool(metrics.get("candidate_materialized", False)),
        "candidate_preflight_status": str(
            metrics.get("candidate_preflight_status", "unknown")
        ),
        "remaining_gap_count": remaining_gap_count,
        "can_submit_candidate_as_REAL_FIELD_REPLAY_PACKAGE_DIR": can_submit,
        "can_route_to_agent51_field_proxy_holdout": bool(
            metrics.get("can_route_to_agent51_field_proxy_holdout", False)
        ),
        "candidate_package_dir": candidate_dir,
        "source_slice_path": str(metrics.get("source_slice_path", "")),
        "next_operator_action": str(
            metrics.get(
                "next_operator_action",
                "inspect_catalyst_slice_r7_patch_candidate_metrics",
            )
        ),
        "candidate_submission_boundary": (
            "A catalyst R7 patch candidate is only a suggested package path. It does not "
            "resume Agent42/44/45 or relax actuator/release gates until the operator sets "
            "REAL_FIELD_REPLAY_PACKAGE_DIR to that package and the full R7 field preflight passes."
        ),
    }


def _field_activation_upstream_summary(
    readiness_gate: dict[str, Any] | None,
    submission_packet: dict[str, Any] | None,
    focus_handoff: dict[str, Any] | None,
) -> dict[str, Any]:
    gate = readiness_gate if isinstance(readiness_gate, dict) else {}
    packet = submission_packet if isinstance(submission_packet, dict) else {}
    handoff = focus_handoff if isinstance(focus_handoff, dict) else {}
    consumed = bool(gate or packet or handoff)
    gate_status = str(
        gate.get(
            "gate_status",
            packet.get(
                "external_readiness_gate_status",
                (
                    "field_activation_upstream_not_consumed_by_external_activation_router"
                    if not consumed
                    else "field_activation_upstream_status_unknown"
                ),
            ),
        )
    )
    packet_status = str(
        packet.get(
            "packet_status",
            "field_activation_response_submission_packet_not_consumed",
        )
    )
    handoff_status = str(
        handoff.get(
            "handoff_status",
            "field_activation_response_focus_handoff_not_consumed",
        )
    )
    can_submit = bool(
        gate.get(
            "can_submit_to_external_activation_router",
            packet.get("can_route_to_external_activation_router", False),
        )
    )
    first_blocked_step = str(
        gate.get("first_blocked_step", packet.get("first_blocked_step", ""))
    )
    highest_priority_blocker = str(
        gate.get(
            "highest_priority_blocker",
            packet.get(
                "highest_priority_blocker",
                "" if not consumed else "field_activation_upstream_blocker_unknown",
            ),
        )
    )
    handoff_ready = handoff_status == "field_activation_response_focus_handoff_ready_for_catalyst_activity"
    handoff_action = str(handoff.get("next_operator_action", "")) if handoff_ready else ""
    packet_action = str(packet.get("next_operator_action", ""))
    gate_action = str(gate.get("next_operator_action", ""))
    next_operator_action = handoff_action or packet_action or gate_action
    if not next_operator_action:
        next_operator_action = (
            "run_field_activation_matrix_before_router_consumption"
            if not consumed
            else "inspect_field_activation_upstream_gate"
        )
    no_write_boundary = str(
        gate.get(
            "no_write_boundary",
            packet.get(
                "no_write_boundary",
                (
                    "Field activation upstream gate was not consumed. Router cannot use "
                    "field-activation state as field evidence."
                ),
            ),
        )
    )
    return {
        "consumed": consumed,
        "status": gate_status,
        "submission_packet_status": packet_status,
        "focus_handoff_status": handoff_status,
        "focus_handoff_target_hidden_state": str(handoff.get("target_hidden_state", "")),
        "focus_handoff_source_env_var": str(handoff.get("focused_merge_source_env_var", "")),
        "focus_handoff_repair_work_order_status": str(
            handoff.get(
                "focused_repair_work_order_status",
                "focused_catalyst_response_repair_work_order_not_available",
            )
        ),
        "focus_handoff_repair_item_count": _safe_int(handoff.get("focused_repair_item_count", 0)),
        "focus_handoff_repair_next_operator_action": str(
            handoff.get("focused_repair_next_operator_action", "")
        ),
        "can_submit_to_external_activation_router": can_submit,
        "first_blocked_step": first_blocked_step,
        "highest_priority_blocker": highest_priority_blocker,
        "next_operator_action": next_operator_action,
        "no_write_boundary": no_write_boundary,
        "upstream_gate_boundary": (
            "This upstream gate only orders field-activation response, repair, assembly, "
            "staging and materialized package preflights. It does not create field "
            "evidence and does not authorize actuator, release-gate, legal or field "
            "claim outputs."
        ),
    }


def _safe_int(value: object) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def _read_csv_package(package_dir: Path) -> dict[str, list[dict[str, str]]]:
    package: dict[str, list[dict[str, str]]] = {}
    for csv_path in sorted(package_dir.glob("*.csv")):
        with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
            package[csv_path.stem] = [dict(row) for row in csv.DictReader(handle)]
    return package


def _command_preview(pointer: str, path: Path, target: str) -> str:
    if not target:
        return ""
    return f"{pointer}={_shell_path(path)} .venv/bin/python {target}"


def _shell_path(path: Path) -> str:
    text = str(path)
    if any(char.isspace() for char in text):
        return "'" + text.replace("'", "'\"'\"'") + "'"
    return text

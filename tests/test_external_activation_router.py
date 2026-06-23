import csv
import json
from pathlib import Path

from water_ai.agents.agent_architecture_consolidation_agent import (
    AgentArchitectureConsolidationAgent,
)
from water_ai.external_activation_router import build_external_activation_router


def test_external_activation_router_waits_when_no_paths_are_supplied(tmp_path: Path) -> None:
    router = build_external_activation_router(_contract(), env={}, project_root=tmp_path)

    rows = {row["channel_id"]: row for row in router["route_rows"]}

    assert router["router_id"] == "R8u82_external_activation_router"
    assert router["router_status"] == "external_activation_router_waiting_for_external_paths"
    assert router["path_supplied_count"] == 0
    assert router["route_ready_count"] == 0
    assert router["model_chain_ready_route_count"] == 0
    assert router["handoff_ready_route_count"] == 0
    assert router["blocked_route_count"] == 3
    assert router["ready_channel_ids"] == []
    assert router["model_chain_ready_channel_ids"] == []
    assert router["handoff_ready_channel_ids"] == []
    assert router["blocked_channel_ids"] == [
        "R7_REAL_FIELD_PACKAGE",
        "R8U66_PATH_ENDPOINT_LABEL_PACKAGE",
        "R8U79_FORMAL_SEARCH_RESULT_PACKAGE",
    ]
    assert router["priority_route_channel_id"] == "R7_REAL_FIELD_PACKAGE"
    assert router["priority_route_status"] == "activation_route_waiting_for_env_var"
    assert router["priority_route_preflight_status"] == "-"
    assert router["highest_priority_blocker"] == "R7_REAL_FIELD_PACKAGE:REAL_FIELD_REPLAY_PACKAGE_DIR:not_set"
    assert router["next_operator_action"] == "set_REAL_FIELD_REPLAY_PACKAGE_DIR"
    assert router["router_validation_command"] == ".venv/bin/python experiments/run_external_activation_router.py"
    assert router["boundary_preserved"] is True
    assert rows["R7_REAL_FIELD_PACKAGE"]["route_status"] == "activation_route_waiting_for_env_var"
    assert rows["R8U66_PATH_ENDPOINT_LABEL_PACKAGE"]["route_status"] == "activation_route_waiting_for_env_var"
    assert rows["R8U79_FORMAL_SEARCH_RESULT_PACKAGE"]["route_status"] == "activation_route_waiting_for_env_var"
    assert router["next_commands"] == []


def test_external_activation_router_reports_catalyst_patch_candidate_when_waiting(
    tmp_path: Path,
) -> None:
    router = build_external_activation_router(
        _contract(),
        env={},
        project_root=tmp_path,
        catalyst_slice_r7_patch_candidate_metrics={
            "patch_status": "catalyst_slice_r7_patch_waiting_for_valid_catalyst_slice",
            "candidate_materialized": False,
            "candidate_preflight_status": "not_run",
            "full_package_gap_summary": {"remaining_gap_count": 0},
            "can_submit_candidate_as_REAL_FIELD_REPLAY_PACKAGE_DIR": False,
            "candidate_package_dir": str(tmp_path / "r7_patch_candidate_package"),
            "source_slice_path": "",
            "next_operator_action": "fill_valid_catalyst_slice_and_set_CATALYST_FIELD_PACKAGE_SLICE_DIR",
        },
    )
    row = {item["channel_id"]: item for item in router["route_rows"]}[
        "R7_REAL_FIELD_PACKAGE"
    ]
    candidate = row["catalyst_slice_r7_patch_candidate"]

    assert router["router_status"] == "external_activation_router_waiting_for_external_paths"
    assert router["catalyst_patch_candidate_consumed"] is True
    assert router["catalyst_patch_candidate_status"] == (
        "catalyst_slice_r7_patch_waiting_for_valid_catalyst_slice"
    )
    assert router["catalyst_patch_candidate_can_submit_as_REAL_FIELD_REPLAY_PACKAGE_DIR"] is False
    assert row["route_status"] == "activation_route_waiting_for_env_var"
    assert row["operator_action"] == "set_REAL_FIELD_REPLAY_PACKAGE_DIR"
    assert candidate["candidate_preflight_status"] == "not_run"
    assert candidate["next_operator_action"] == (
        "fill_valid_catalyst_slice_and_set_CATALYST_FIELD_PACKAGE_SLICE_DIR"
    )
    assert "full R7 field preflight passes" in candidate["candidate_submission_boundary"]


def test_external_activation_router_prefers_field_activation_upstream_when_r7_path_missing(
    tmp_path: Path,
) -> None:
    router = build_external_activation_router(
        _contract(),
        env={},
        project_root=tmp_path,
        field_activation_external_readiness_gate=_field_activation_readiness_blocked(),
        field_activation_response_submission_packet=_field_activation_submission_packet_blocked(),
        field_activation_response_focus_handoff=_field_activation_focus_handoff_ready(),
    )
    row = {item["channel_id"]: item for item in router["route_rows"]}[
        "R7_REAL_FIELD_PACKAGE"
    ]
    upstream = row["field_activation_upstream_gate"]

    assert row["route_status"] == "activation_route_blocked_by_field_activation_upstream_gate"
    assert row["route_ready"] is False
    assert row["can_resume_model_chain"] is False
    assert row["blocked_reason"] == (
        "field_activation_upstream_not_ready:R8U106_SUBMIT_FIELD_ACTIVATION_RESPONSE"
    )
    assert row["operator_action"] == (
        "fill_focused_catalyst_response_template_then_set_FOCUSED_CATALYST_RESPONSE_PATH_"
        "and_merge_to_FIELD_ACTIVATION_RESPONSE_PATH"
    )
    assert router["priority_route_status"] == (
        "activation_route_blocked_by_field_activation_upstream_gate"
    )
    assert router["priority_route_preflight_status"] == (
        "field_activation_external_readiness_waiting_for_external_response"
    )
    assert router["highest_priority_blocker"] == (
        "R7_REAL_FIELD_PACKAGE:field_activation_upstream_not_ready:"
        "R8U106_SUBMIT_FIELD_ACTIVATION_RESPONSE:"
        "field_activation_external_readiness_waiting_for_external_response"
    )
    assert router["next_operator_action"] == (
        "fill_focused_catalyst_response_template_then_set_FOCUSED_CATALYST_RESPONSE_PATH_"
        "and_merge_to_FIELD_ACTIVATION_RESPONSE_PATH"
    )
    assert router["field_activation_upstream_consumed"] is True
    assert router["field_activation_upstream_status"] == (
        "field_activation_external_readiness_waiting_for_external_response"
    )
    assert router["field_activation_upstream_submission_packet_status"] == (
        "field_activation_response_submission_packet_waiting_for_external_response"
    )
    assert router["field_activation_upstream_focus_handoff_status"] == (
        "field_activation_response_focus_handoff_ready_for_catalyst_activity"
    )
    assert router["field_activation_upstream_focus_handoff_source_env_var"] == (
        "FOCUSED_CATALYST_RESPONSE_PATH"
    )
    assert router["field_activation_upstream_focus_handoff_repair_work_order_status"] == (
        "focused_catalyst_response_repair_work_order_waiting_for_external_response"
    )
    assert router["field_activation_upstream_focus_handoff_repair_item_count"] == 1
    assert router["field_activation_upstream_first_blocked_step"] == "response_source"
    assert router["field_activation_upstream_can_submit_to_external_activation_router"] is False
    assert upstream["next_operator_action"] == (
        "fill_focused_catalyst_response_template_then_set_FOCUSED_CATALYST_RESPONSE_PATH_"
        "and_merge_to_FIELD_ACTIVATION_RESPONSE_PATH"
    )
    assert "does not create field evidence" in upstream["upstream_gate_boundary"]


def test_external_activation_router_uses_focused_repair_action_when_handoff_reports_source_blocker(
    tmp_path: Path,
) -> None:
    router = build_external_activation_router(
        _contract(),
        env={},
        project_root=tmp_path,
        field_activation_external_readiness_gate=_field_activation_readiness_blocked(),
        field_activation_response_submission_packet=_field_activation_submission_packet_blocked(),
        field_activation_response_focus_handoff=_field_activation_focus_handoff_with_source_repair(),
    )
    row = {item["channel_id"]: item for item in router["route_rows"]}[
        "R7_REAL_FIELD_PACKAGE"
    ]

    assert row["operator_action"] == "repair_FOCUSED_CATALYST_RESPONSE_PATH_file_path"
    assert router["next_operator_action"] == "repair_FOCUSED_CATALYST_RESPONSE_PATH_file_path"
    assert router["field_activation_upstream_next_operator_action"] == (
        "repair_FOCUSED_CATALYST_RESPONSE_PATH_file_path"
    )
    assert router["field_activation_upstream_focus_handoff_repair_work_order_status"] == (
        "focused_catalyst_response_repair_work_order_blocked_at_source_preflight"
    )
    assert router["field_activation_upstream_focus_handoff_repair_item_count"] == 1


def test_external_activation_router_suggests_candidate_without_marking_r7_ready(
    tmp_path: Path,
) -> None:
    candidate_dir = tmp_path / "r7_patch_candidate_package"
    candidate_dir.mkdir()

    router = build_external_activation_router(
        _contract(),
        env={},
        project_root=tmp_path,
        catalyst_slice_r7_patch_candidate_metrics={
            "patch_status": "catalyst_slice_r7_patch_candidate_ready_for_operator_submission",
            "candidate_materialized": True,
            "candidate_preflight_status": "field_package_preflight_ready_for_agent42",
            "full_package_gap_summary": {"remaining_gap_count": 0},
            "can_submit_candidate_as_REAL_FIELD_REPLAY_PACKAGE_DIR": True,
            "can_route_to_agent51_field_proxy_holdout": True,
            "candidate_package_dir": str(candidate_dir),
            "source_slice_path": str(tmp_path / "valid_slice"),
            "next_operator_action": "set_REAL_FIELD_REPLAY_PACKAGE_DIR_to_candidate_package",
        },
        field_activation_external_readiness_gate=_field_activation_readiness_blocked(),
        field_activation_response_submission_packet=_field_activation_submission_packet_blocked(),
    )
    row = {item["channel_id"]: item for item in router["route_rows"]}[
        "R7_REAL_FIELD_PACKAGE"
    ]
    candidate = row["catalyst_slice_r7_patch_candidate"]

    assert router["router_status"] == "external_activation_router_waiting_for_external_paths"
    assert router["route_ready_count"] == 0
    assert router["model_chain_ready_route_count"] == 0
    assert router["priority_route_ready"] is False
    assert router["priority_route_can_resume_model_chain"] is False
    assert router["next_commands"] == []
    assert row["route_status"] == "activation_route_waiting_for_env_var"
    assert row["route_ready"] is False
    assert row["can_resume_model_chain"] is False
    assert row["operator_action"] == "set_REAL_FIELD_REPLAY_PACKAGE_DIR_to_catalyst_patch_candidate"
    assert router["next_operator_action"] == "set_REAL_FIELD_REPLAY_PACKAGE_DIR_to_catalyst_patch_candidate"
    assert router["catalyst_patch_candidate_can_submit_as_REAL_FIELD_REPLAY_PACKAGE_DIR"] is True
    assert router["catalyst_patch_candidate_package_dir"] == str(candidate_dir)
    assert candidate["can_submit_candidate_as_REAL_FIELD_REPLAY_PACKAGE_DIR"] is True
    assert candidate["candidate_package_dir"] == str(candidate_dir)
    assert "does not resume Agent42/44/45" in candidate["candidate_submission_boundary"]


def test_external_activation_router_does_not_let_candidate_override_submitted_r7_path(
    tmp_path: Path,
) -> None:
    field_dir = tmp_path / "complete_field_package"
    _write_complete_field_package(field_dir)
    candidate_dir = tmp_path / "r7_patch_candidate_package"
    candidate_dir.mkdir()

    router = build_external_activation_router(
        _contract(),
        env={"REAL_FIELD_REPLAY_PACKAGE_DIR": str(field_dir)},
        project_root=tmp_path,
        catalyst_slice_r7_patch_candidate_metrics={
            "patch_status": "catalyst_slice_r7_patch_candidate_ready_for_operator_submission",
            "candidate_materialized": True,
            "candidate_preflight_status": "field_package_preflight_ready_for_agent42",
            "full_package_gap_summary": {"remaining_gap_count": 0},
            "can_submit_candidate_as_REAL_FIELD_REPLAY_PACKAGE_DIR": True,
            "candidate_package_dir": str(candidate_dir),
        },
    )
    row = {item["channel_id"]: item for item in router["route_rows"]}[
        "R7_REAL_FIELD_PACKAGE"
    ]

    assert row["submitted_path"] == str(field_dir)
    assert row["route_status"] == "activation_route_ready_for_r7_pipeline_execution"
    assert row["operator_action"] == "run_preflight_or_pipeline_command"
    assert row["route_ready"] is True
    assert row["can_resume_model_chain"] is True
    assert row["catalyst_slice_r7_patch_candidate"][
        "can_submit_candidate_as_REAL_FIELD_REPLAY_PACKAGE_DIR"
    ] is True


def test_external_activation_router_rejects_wrong_path_types(tmp_path: Path) -> None:
    field_file = tmp_path / "field_package.json"
    field_file.write_text("{}", encoding="utf-8")
    formal_dir = tmp_path / "formal_package_dir"
    formal_dir.mkdir()

    router = build_external_activation_router(
        _contract(),
        env={
            "REAL_FIELD_REPLAY_PACKAGE_DIR": str(field_file),
            "FORMAL_SEARCH_RESULT_PACKAGE_PATH": str(formal_dir),
        },
        project_root=tmp_path,
    )
    rows = {row["channel_id"]: row for row in router["route_rows"]}

    assert rows["R7_REAL_FIELD_PACKAGE"]["route_status"] == "activation_route_invalid_path_type"
    assert rows["R7_REAL_FIELD_PACKAGE"]["blocked_reason"] == "REAL_FIELD_REPLAY_PACKAGE_DIR:expected_directory"
    assert rows["R8U79_FORMAL_SEARCH_RESULT_PACKAGE"]["route_status"] == "activation_route_invalid_path_type"
    assert rows["R8U79_FORMAL_SEARCH_RESULT_PACKAGE"]["blocked_reason"] == "FORMAL_SEARCH_RESULT_PACKAGE_PATH:expected_file"
    assert router["route_ready_count"] == 0
    assert router["priority_route_channel_id"] == "R7_REAL_FIELD_PACKAGE"
    assert router["highest_priority_blocker"] == (
        "R7_REAL_FIELD_PACKAGE:REAL_FIELD_REPLAY_PACKAGE_DIR:expected_directory"
    )
    assert router["next_operator_action"] == "submit_directory_for_REAL_FIELD_REPLAY_PACKAGE_DIR"


def test_external_activation_router_blocks_existing_field_dir_that_fails_preflight(tmp_path: Path) -> None:
    field_dir = tmp_path / "field_package"
    field_dir.mkdir()
    formal_file = tmp_path / "formal_result.json"
    formal_file.write_text(json.dumps({"package_type": "formal_search_result_package"}), encoding="utf-8")

    router = build_external_activation_router(
        _contract(),
        env={
            "REAL_FIELD_REPLAY_PACKAGE_DIR": str(field_dir),
            "FORMAL_SEARCH_RESULT_PACKAGE_PATH": str(formal_file),
        },
        project_root=tmp_path,
    )
    rows = {row["channel_id"]: row for row in router["route_rows"]}

    assert rows["R7_REAL_FIELD_PACKAGE"]["route_status"] == (
        "activation_route_blocked_by_field_package_preflight"
    )
    assert rows["R7_REAL_FIELD_PACKAGE"]["can_resume_model_chain"] is False
    assert rows["R7_REAL_FIELD_PACKAGE"]["blocked_reason"] == "field_package_preflight_not_ready"
    assert rows["R7_REAL_FIELD_PACKAGE"]["field_package_preflight"]["status"] == (
        "field_package_preflight_missing_files_or_headers"
    )
    assert rows["R7_REAL_FIELD_PACKAGE"]["command_preview"] == ""
    assert rows["R8U79_FORMAL_SEARCH_RESULT_PACKAGE"]["route_status"] == (
        "activation_route_blocked_by_formal_search_result_preflight"
    )
    assert rows["R8U79_FORMAL_SEARCH_RESULT_PACKAGE"]["can_resume_model_chain"] is False
    assert rows["R8U79_FORMAL_SEARCH_RESULT_PACKAGE"]["blocked_reason"] == (
        "formal_search_result_preflight_not_ready"
    )
    assert rows["R8U79_FORMAL_SEARCH_RESULT_PACKAGE"][
        "formal_search_result_package_source_preflight"
    ]["formal_search_result_package_source_status"] == "formal_search_result_package_loaded_with_preflight_gaps"
    assert rows["R8U79_FORMAL_SEARCH_RESULT_PACKAGE"]["command_preview"] == ""
    assert router["route_ready_count"] == 0
    assert router["blocked_route_count"] == 3
    assert router["priority_route_channel_id"] == "R7_REAL_FIELD_PACKAGE"
    assert router["priority_route_preflight_status"] == "field_package_preflight_missing_files_or_headers"
    assert router["highest_priority_blocker"] == (
        "R7_REAL_FIELD_PACKAGE:field_package_preflight_not_ready:field_package_preflight_missing_files_or_headers"
    )


def test_external_activation_router_prepares_field_route_only_after_agent44_preflight(tmp_path: Path) -> None:
    field_dir = tmp_path / "complete_field_package"
    _write_complete_field_package(field_dir)

    router = build_external_activation_router(
        _contract(),
        env={"REAL_FIELD_REPLAY_PACKAGE_DIR": str(field_dir)},
        project_root=tmp_path,
    )
    row = {item["channel_id"]: item for item in router["route_rows"]}["R7_REAL_FIELD_PACKAGE"]

    assert row["route_status"] == "activation_route_ready_for_r7_pipeline_execution"
    assert row["route_ready"] is True
    assert row["can_resume_model_chain"] is True
    assert row["field_package_preflight"]["status"] == "field_package_preflight_ready_for_agent42"
    assert row["field_package_preflight"]["can_pass_to_timestamped_replay"] is True
    assert "run_r7_real_field_replay_pipeline.py" in row["command_preview"]
    assert router["route_ready_count"] == 1
    assert router["model_chain_ready_route_count"] == 1
    assert router["handoff_ready_route_count"] == 0
    assert router["router_status"] == "external_activation_router_has_model_chain_ready_routes"
    assert router["model_chain_ready_channel_ids"] == ["R7_REAL_FIELD_PACKAGE"]
    assert router["priority_route_channel_id"] == "R7_REAL_FIELD_PACKAGE"
    assert router["priority_route_ready"] is True
    assert router["priority_route_can_resume_model_chain"] is True
    assert router["highest_priority_blocker"] == ""
    assert router["next_operator_action"] == "run_preflight_or_pipeline_command"


def test_external_activation_router_runs_path_endpoint_preflight(tmp_path: Path) -> None:
    endpoint_dir = tmp_path / "path_endpoint"
    endpoint_dir.mkdir()
    _write_ready_path_endpoint_package(endpoint_dir)

    router = build_external_activation_router(
        _contract(),
        env={"FIELD_PATH_ENDPOINT_LABEL_PACKAGE_DIR": str(endpoint_dir)},
        project_root=tmp_path,
    )
    row = {item["channel_id"]: item for item in router["route_rows"]}[
        "R8U66_PATH_ENDPOINT_LABEL_PACKAGE"
    ]

    assert row["route_status"] == "activation_route_ready_for_path_endpoint_layout_holdout"
    assert row["route_ready"] is True
    assert row["can_resume_model_chain"] is True
    assert row["path_endpoint_preflight"]["matched_batch_count"] == 5
    assert row["path_endpoint_preflight"]["can_route_to_field_layout_holdout"] is True
    assert router["route_ready_count"] == 1
    assert router["model_chain_ready_route_count"] == 1
    assert router["handoff_ready_route_count"] == 0
    assert router["router_status"] == "external_activation_router_has_model_chain_ready_routes"
    assert router["model_chain_ready_channel_ids"] == ["R8U66_PATH_ENDPOINT_LABEL_PACKAGE"]
    assert router["priority_route_channel_id"] == "R8U66_PATH_ENDPOINT_LABEL_PACKAGE"
    assert router["highest_priority_blocker"] == ""
    assert router["next_operator_action"] == "route_to_field_layout_holdout_review"


def test_external_activation_router_runs_formal_search_result_preflight(tmp_path: Path) -> None:
    formal_package = tmp_path / "formal_search_result_package.json"
    _write_ready_formal_search_result_package(formal_package)

    router = build_external_activation_router(
        _contract(),
        env={"FORMAL_SEARCH_RESULT_PACKAGE_PATH": str(formal_package)},
        project_root=tmp_path,
    )
    row = {item["channel_id"]: item for item in router["route_rows"]}[
        "R8U79_FORMAL_SEARCH_RESULT_PACKAGE"
    ]

    assert row["route_status"] == "activation_route_ready_for_agent60_formal_search_preflight"
    assert row["route_ready"] is True
    assert row["can_resume_model_chain"] is False
    assert row["formal_search_result_package_source_preflight"][
        "formal_search_result_package_source_status"
    ] == "formal_search_result_package_source_ready_for_validation_gate"
    assert row["formal_search_result_package_row_preflight"][
        "formal_search_result_package_row_preflight_status"
    ] == "formal_search_result_package_row_preflight_ready_for_validation_gate"
    assert row["formal_search_result_validation_execution"][
        "can_enter_human_nonlegal_comparison_review"
    ] is True
    assert row["formal_search_result_validation_execution"]["can_generate_prior_art_result"] is False
    assert row["formal_search_result_validation_execution"]["legal_opinion_allowed"] is False
    assert "run_agent60_agent_architecture_consolidation.py" in row["command_preview"]
    assert router["route_ready_count"] == 1
    assert router["model_chain_ready_route_count"] == 0
    assert router["handoff_ready_route_count"] == 1
    assert router["router_status"] == "external_activation_router_has_handoff_ready_routes"
    assert router["handoff_ready_channel_ids"] == ["R8U79_FORMAL_SEARCH_RESULT_PACKAGE"]
    assert router["blocked_channel_ids"] == [
        "R7_REAL_FIELD_PACKAGE",
        "R8U66_PATH_ENDPOINT_LABEL_PACKAGE",
    ]
    assert router["priority_route_channel_id"] == "R8U79_FORMAL_SEARCH_RESULT_PACKAGE"
    assert router["highest_priority_blocker"] == ""
    assert router["next_operator_action"] == "run_preflight_or_pipeline_command"


def _contract() -> dict[str, object]:
    return {
        "contract_id": "R8u81_external_evidence_activation_contract",
        "boundary_preserved": True,
        "channels": [
            {
                "channel_id": "R7_REAL_FIELD_PACKAGE",
                "package_pointer": "REAL_FIELD_REPLAY_PACKAGE_DIR",
                "no_write_boundary": "field route no-write boundary",
            },
            {
                "channel_id": "R8U66_PATH_ENDPOINT_LABEL_PACKAGE",
                "package_pointer": "FIELD_PATH_ENDPOINT_LABEL_PACKAGE_DIR",
                "no_write_boundary": "path endpoint no-write boundary",
            },
            {
                "channel_id": "R8U79_FORMAL_SEARCH_RESULT_PACKAGE",
                "package_pointer": "FORMAL_SEARCH_RESULT_PACKAGE_PATH",
                "no_write_boundary": "formal route no-write boundary",
            },
        ],
    }


def _field_activation_readiness_blocked() -> dict[str, object]:
    return {
        "gate_status": "field_activation_external_readiness_waiting_for_external_response",
        "first_blocked_step": "response_source",
        "highest_priority_blocker": "R8U106_SUBMIT_FIELD_ACTIVATION_RESPONSE",
        "next_operator_action": "set_FIELD_ACTIVATION_RESPONSE_PATH_to_filled_external_response_json",
        "can_submit_to_external_activation_router": False,
        "can_resume_model_chain": False,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
        "no_write_boundary": (
            "This readiness gate only orders existing field-activation preflights. "
            "It does not create field evidence."
        ),
    }


def _field_activation_submission_packet_blocked() -> dict[str, object]:
    return {
        "packet_status": "field_activation_response_submission_packet_waiting_for_external_response",
        "external_readiness_gate_status": "field_activation_external_readiness_waiting_for_external_response",
        "first_blocked_step": "response_source",
        "highest_priority_blocker": "R8U106_SUBMIT_FIELD_ACTIVATION_RESPONSE",
        "next_operator_action": "fill_response_template_and_set_FIELD_ACTIVATION_RESPONSE_PATH",
        "can_route_to_external_activation_router": False,
        "can_resume_model_chain": False,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
    }


def _field_activation_focus_handoff_ready() -> dict[str, object]:
    return {
        "handoff_status": "field_activation_response_focus_handoff_ready_for_catalyst_activity",
        "target_hidden_state": "catalyst_activity",
        "focused_merge_source_env_var": "FOCUSED_CATALYST_RESPONSE_PATH",
        "next_operator_action": (
            "fill_focused_catalyst_response_template_then_set_FOCUSED_CATALYST_RESPONSE_PATH_"
            "and_merge_to_FIELD_ACTIVATION_RESPONSE_PATH"
        ),
        "focused_repair_work_order_status": (
            "focused_catalyst_response_repair_work_order_waiting_for_external_response"
        ),
        "focused_repair_item_count": 1,
        "focused_repair_next_operator_action": (
            "fill_outputs/catalyst_response_submission_kit/focused_catalyst_response_template.json_"
            "with_real_field_values_then_set_FOCUSED_CATALYST_RESPONSE_PATH"
        ),
        "can_submit_to_external_activation_router": False,
        "can_resume_model_chain": False,
        "can_write_to_actuator": False,
        "can_write_to_release_gate": False,
    }


def _field_activation_focus_handoff_with_source_repair() -> dict[str, object]:
    handoff = _field_activation_focus_handoff_ready()
    handoff["next_operator_action"] = "repair_FOCUSED_CATALYST_RESPONSE_PATH_file_path"
    handoff["focused_repair_work_order_status"] = (
        "focused_catalyst_response_repair_work_order_blocked_at_source_preflight"
    )
    handoff["focused_repair_item_count"] = 1
    handoff["focused_repair_next_operator_action"] = "repair_FOCUSED_CATALYST_RESPONSE_PATH_file_path"
    return handoff


def _write_complete_field_package(package_dir: Path) -> None:
    package_dir.mkdir()
    (package_dir / "metadata.json").write_text(json.dumps(_field_metadata(), ensure_ascii=False), encoding="utf-8")
    for table, rows in _field_replay_rows().items():
        _write_csv(package_dir / f"{table}.csv", rows)


def _field_metadata() -> dict[str, object]:
    return {
        "data_origin": "field",
        "site_id": "field_site_A",
        "campaign_id": "C001",
        "sampling_start": "2026-06-01T08:00:00+08:00",
        "sampling_end": "2026-06-01T12:00:00+08:00",
        "operator_id": "operator_01",
        "instrument_snapshot_id": "low_cost_sensor_bank_v2",
        "chain_of_custody_id": "custody_C001_signed",
    }


def _field_replay_rows() -> dict[str, list[dict[str, str]]]:
    return {
        "sensor_timeseries": [
            _sensor("B001", "0"),
            _sensor("B002", "0"),
            _sensor("B003", "0"),
        ],
        "offline_lab_results": [
            _lab("B001", "15", "95"),
            _lab("B002", "15", "90"),
            _lab("B003", "15", "100"),
        ],
        "campaign_operation_log": [
            _operation("B001", "switch_or_pretreat", "10", "16", "20", "42"),
            _operation("B002", "switch_or_pretreat", "12", "18", "22", "44"),
            _operation("B003", "hold_for_validation", "12", "15", "15", "90"),
        ],
        "pressure_headloss_event_log": [
            _pressure_event("B001", "18", "15", "true"),
            _pressure_event("B002", "20", "15", "true"),
            _pressure_event("B003", "30", "15", "false"),
        ],
        "fast_proxy_event_log": [
            _proxy_event("B001", "10", "95", "true", "true", "0.0"),
            _proxy_event("B002", "12", "90", "true", "true", "0.0"),
            _proxy_event("B003", "12", "100", "false", "false", "0.0"),
        ],
    }


def _sensor(batch_id: str, timestamp: str) -> dict[str, str]:
    return {
        "batch_id": batch_id,
        "timestamp_min": timestamp,
        "EC_uScm": "3000.0",
        "turbidity_NTU": "40.0",
        "UV254_abs": "0.86",
        "pH": "7.8",
        "ORP_mV": "510.0",
        "flow_Lmin": "1.20",
        "pressure_drop_kPa": "4.20",
        "headloss_kPa_per_m": "5.25",
        "bed_inlet_pressure_kPa": "104.10",
        "bed_outlet_pressure_kPa": "99.90",
    }


def _lab(batch_id: str, sample_time: str, result_time: str) -> dict[str, str]:
    return {
        "batch_id": batch_id,
        "sample_time_min": sample_time,
        "result_time_min": result_time,
        "analyte": "matrix_shock_label",
        "value": "1.0",
        "qa_flag": "pass",
        "proxy_holdout_label": "true",
        "pressure_headloss_proxy_label": "true",
    }


def _operation(batch_id: str, action_id: str, command: str, effect: str, start: str, end: str) -> dict[str, str]:
    return {
        "campaign_id": "C001",
        "batch_id": batch_id,
        "action_id": action_id,
        "command_time_min": command,
        "effect_time_min": effect,
        "start_min": start,
        "end_min": end,
        "release_policy": "block_release_until_lab_and_field_conformal_calibration",
        "recycle_ratio": "0.35",
        "tank_storage_margin": "0.42",
        "actuator_latency_p90": "8.0",
        "pump_valve_result": "ok",
        "hold_time_min": "45",
        "regeneration_event": "false",
        "bed_id": "BED_A",
        "pressure_headloss_review_required": "true",
    }


def _pressure_event(batch_id: str, event_time: str, matched_sample: str, anomaly: str) -> dict[str, str]:
    return {
        "campaign_id": "C001",
        "batch_id": batch_id,
        "event_time_min": event_time,
        "bed_id": "BED_A",
        "pressure_drop_kPa": "6.80" if anomaly == "true" else "4.10",
        "headloss_kPa_per_m": "8.50" if anomaly == "true" else "5.10",
        "flow_Lmin": "1.20",
        "matched_lab_sample_time_min": matched_sample,
        "regeneration_event": "false",
        "hydraulic_anomaly_label": anomaly,
        "flow_normalized_pressure_residual": "0.42" if anomaly == "true" else "0.08",
        "expected_clean_bed_pressure_drop_kPa": "3.20",
        "operator_review_required": anomaly,
    }


def _proxy_event(
    batch_id: str,
    event_time: str,
    label_time: str,
    triggered: str,
    label: str,
    cost: str,
) -> dict[str, str]:
    return {
        "campaign_id": "C001",
        "batch_id": batch_id,
        "event_time_min": event_time,
        "proxy_score": "0.88",
        "specificity_guard_score": "0.83",
        "protective_triggered": triggered,
        "triggered_action_id": "switch_or_pretreat" if triggered == "true" else "none",
        "field_label_matrix_shock": label,
        "lab_label_time_min": label_time,
        "false_positive_cost_index": cost,
    }


def _write_ready_path_endpoint_package(package_dir: Path) -> None:
    batches = [f"B{i:03d}" for i in range(1, 6)]
    _write_csv(
        package_dir / "site_topology_or_bed_geometry.csv",
        [
            {
                "site_id": "S1",
                "node_id": "N1",
                "zone": "influent",
                "upstream_node_id": "none",
                "downstream_node_id": "N2",
                "path_stage_id": "stage_influent",
                "hydraulic_path_role": "inlet",
                "nominal_flow_Lmin": "10",
                "nominal_HRT_min": "30",
                "recycle_ratio": "0.2",
                "release_boundary_flag": "False",
                "recirculation_loop_flag": "False",
            }
        ],
    )
    _write_csv(
        package_dir / "node_modality_sensor_timeseries.csv",
        [
            {
                "batch_id": batch,
                "timestamp_min": "10",
                "layout_id": "L1",
                "node_id": "N1",
                "zone": "influent",
                "modality": "UV254_abs",
                "sensor_value": "0.42",
                "availability_mask": "1",
                "time_since_last_observed_min": "0",
                "data_origin": "field",
            }
            for batch in batches
        ],
    )
    _write_csv(
        package_dir / "hydraulic_path_stage_labels.csv",
        [
            {
                "batch_id": batch,
                "layout_id": "L1",
                "node_id": "N1",
                "zone": "influent",
                "path_stage_id": "stage_influent",
                "hydraulic_path_role": "inlet",
                "stage_coverage_label": "covered",
                "direct_path_stage_coverage_label": "direct",
                "proxy_path_stage_coverage_label": "proxy",
                "label_source": "operator_review",
                "reviewer_id": "R1",
                "review_time_min": "20",
            }
            for batch in batches
        ],
    )
    _write_csv(
        package_dir / "final_effluent_endpoint_labels.csv",
        [
            {
                "batch_id": batch,
                "endpoint_node_id": "N5",
                "sample_time_min": "30",
                "final_effluent_direct_observed": "True",
                "release_gate_label": "hold",
                "release_risk_label": "review",
                "analyte": "target_pollutant",
                "value": "0.03",
                "unit": "mg/L",
                "qa_flag": "pass",
                "reviewer_id": "R1",
            }
            for batch in batches
        ],
    )
    _write_csv(
        package_dir / "campaign_operation_log.csv",
        [
            {
                "batch_id": batch,
                "campaign_id": "C1",
                "action_id": f"A_{batch}",
                "operation_id": f"OP_{batch}",
                "action_type": "hold",
                "start_min": "12",
                "end_min": "30",
                "command_time_min": "12",
                "effect_time_min": "18",
                "recycle_ratio": "0.2",
                "hold_time_min": "18",
                "release_policy": "manual_review_required",
                "operator_id": "operator_1",
                "operator_override": "False",
            }
            for batch in batches
        ],
    )
    _write_csv(
        package_dir / "offline_lab_results.csv",
        [
            {
                "batch_id": batch,
                "sample_time_min": "30",
                "analyte": "target_pollutant",
                "value": "0.03",
                "unit": "mg/L",
                "qa_flag": "pass",
                "method": "LCMS",
                "detection_limit": "0.001",
                "sample_source": "final_effluent",
            }
            for batch in batches
        ],
    )


def _write_ready_formal_search_result_package(path: Path) -> None:
    templates = AgentArchitectureConsolidationAgent().run([]).metrics[
        "formal_search_result_package_template"
    ]
    work_package_results = {}
    for template in templates:
        work_package_id = str(template["linked_work_package_id"])
        hit_id = f"HIT_{work_package_id}"
        mapped_element = str(
            (
                list(template["mapped_claim_ids"])
                + list(template["mapped_feature_ids"])
                + list(template["mapped_effect_ids"])
            )[0]
        )
        work_package_results[work_package_id] = {
            "package_manifest": {
                field: _formal_manifest_value(field, template, work_package_id)
                for field in template["package_manifest_required_fields"]
            },
            "prior_art_hit_table": [
                {
                    field: _formal_hit_value(field, template, work_package_id, hit_id)
                    for field in template["prior_art_hit_table_template_fields"]
                }
            ],
            "claim_element_comparison_chart": [
                {
                    field: _formal_comparison_value(
                        field,
                        work_package_id=work_package_id,
                        hit_id=hit_id,
                        mapped_element=mapped_element,
                    )
                    for field in template["claim_element_comparison_template_fields"]
                }
            ],
            "fallback_claim_scope_recommendation": [
                {
                    field: _formal_fallback_value(field, work_package_id=work_package_id, hit_id=hit_id)
                    for field in template["fallback_recommendation_fields"]
                }
            ],
        }
    path.write_text(
        json.dumps(
            {
                "package_metadata": {
                    "package_id": "PKG_FORMAL_SEARCH_ROUTER_TEST",
                    "package_type": "formal_search_result_package",
                    "search_executor": "external_searcher",
                    "search_date": "2026-06-21",
                    "reviewer_id": "reviewer_A",
                    "review_time": "2026-06-21T00:00:00Z",
                    "review_boundary_statement": "Comparison record only; no authorization or field claim asserted.",
                    "legal_status": "not_legal_opinion",
                },
                "work_package_results": work_package_results,
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def _formal_manifest_value(field: str, template: dict[str, object], work_package_id: str) -> object:
    if field == "linked_work_package_id":
        return work_package_id
    if field == "allowed_source_databases":
        return template["allowed_source_databases"]
    if field == "allowed_query_sources":
        return template["allowed_query_sources"]
    if field == "legal_status":
        return "not_legal_opinion"
    if field == "review_boundary_statement":
        return "Comparison record only; no field-supported or legal conclusion asserted."
    return f"{field}_{work_package_id}"


def _formal_hit_value(field: str, template: dict[str, object], work_package_id: str, hit_id: str) -> object:
    if field == "hit_id":
        return hit_id
    if field == "linked_work_package_id":
        return work_package_id
    if field == "source_database":
        return list(template["allowed_source_databases"])[0]
    if field == "matched_query":
        return list(template["allowed_query_sources"])[0]
    if field == "legal_status":
        return "not_legal_opinion"
    if field == "reviewer_boundary":
        return "Comparison record only; no legal or field conclusion."
    return f"{field}_{work_package_id}"


def _formal_comparison_value(field: str, *, work_package_id: str, hit_id: str, mapped_element: str) -> object:
    if field == "linked_work_package_id":
        return work_package_id
    if field == "linked_hit_id":
        return hit_id
    if field == "claim_or_feature_element":
        return f"{mapped_element}: sensor-limited grey-box loop element"
    if field == "reviewer_decision":
        return "comparison_record_only"
    if field == "legal_status":
        return "not_legal_opinion"
    if field == "field_validation_gate_to_preserve":
        return "field replay and operator review gate"
    return f"{field}_{work_package_id}"


def _formal_fallback_value(field: str, *, work_package_id: str, hit_id: str) -> object:
    if field == "linked_work_package_id":
        return work_package_id
    if field == "triggering_hit_ids":
        return [hit_id]
    if field == "claim_scope_decision_option":
        return "retain_candidate_scope_pending_formal_review"
    if field == "legal_status":
        return "not_legal_opinion"
    if field == "preserved_field_validation_gate":
        return "field replay and operator review gate"
    return f"{field}_{work_package_id}"


def _write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    headers = list(rows[0])
    text_rows = [",".join(headers)]
    text_rows.extend(",".join(row.get(header, "") for header in headers) for row in rows)
    path.write_text("\n".join(text_rows) + "\n", encoding="utf-8")

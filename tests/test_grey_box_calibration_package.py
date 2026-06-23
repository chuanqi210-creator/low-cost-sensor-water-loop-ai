import csv
from pathlib import Path

from water_ai.grey_box_calibration_package import (
    BATCH_LAB_TABLE,
    BYPRODUCT_TABLE,
    CATALYST_TABLE,
    HYDRAULIC_TABLE,
    OXIDANT_TABLE,
    REQUIRED_TABLES,
    SOURCE_ENV_VAR,
    TABLE_COLUMNS,
    build_grey_box_calibration_collection_work_order,
    build_grey_box_calibration_package_preflight,
    build_grey_box_field_calibration_summary,
    build_grey_box_submission_readiness_gate,
    grey_box_calibration_collection_work_order_report_md,
    grey_box_submission_readiness_gate_report_md,
    write_grey_box_calibration_package_template,
)


def test_grey_box_calibration_package_waits_for_external_dir() -> None:
    preflight = build_grey_box_calibration_package_preflight()
    summary = build_grey_box_field_calibration_summary(preflight=preflight)

    assert preflight["source_env_var"] == SOURCE_ENV_VAR
    assert preflight["package_status"] == (
        "grey_box_calibration_package_waiting_for_GREY_BOX_CALIBRATION_PACKAGE_DIR"
    )
    assert preflight["package_preflight_pass"] is False
    assert preflight["can_route_to_agent53_field_calibration"] is False
    assert preflight["can_generate_field_evidence"] is False
    assert preflight["can_write_to_actuator"] is False
    assert preflight["can_write_to_release_gate"] is False
    assert "missing_external_package_dir" in preflight["blocking_reasons"]
    assert summary["summary_status"] == "grey_box_field_calibration_waiting_for_preflight_ready"
    assert summary["can_run_agent53_field_calibration"] is False
    assert summary["agent53_field_candidate_ready"] is False
    assert summary["can_write_to_actuator"] is False
    assert summary["can_write_to_release_gate"] is False


def test_grey_box_calibration_package_blocks_template_rows(tmp_path: Path) -> None:
    write_grey_box_calibration_package_template(tmp_path)

    preflight = build_grey_box_calibration_package_preflight(
        source_dir=tmp_path,
        external_package_supplied=True,
    )

    assert preflight["package_preflight_pass"] is False
    assert preflight["package_status"] == "grey_box_calibration_package_blocked_at_field_origin"
    assert "template_markers_present" in preflight["blocking_reasons"]
    assert "non_field_rows_present" in preflight["blocking_reasons"]
    assert preflight["matched_batch_count"] == 0
    assert preflight["can_route_to_agent53_field_calibration"] is False


def test_grey_box_calibration_package_accepts_minimum_field_rows(tmp_path: Path) -> None:
    _write_valid_package(tmp_path)

    preflight = build_grey_box_calibration_package_preflight(
        source_dir=tmp_path,
        external_package_supplied=True,
    )
    summary = build_grey_box_field_calibration_summary(
        source_dir=tmp_path,
        external_package_supplied=True,
        preflight=preflight,
    )

    assert preflight["package_status"] == (
        "grey_box_calibration_package_ready_for_agent53_field_calibration"
    )
    assert preflight["package_preflight_pass"] is True
    assert preflight["matched_batch_count"] == 3
    assert preflight["field_physics_coverage_candidate"] == 1.0
    assert preflight["lab_pair_audit"]["valid_row_count"] == 3
    assert preflight["hydraulic_audit"]["valid_row_count"] == 3
    assert preflight["oxidant_audit"]["valid_row_count"] == 3
    assert preflight["catalyst_audit"]["valid_row_count"] == 3
    assert preflight["byproduct_audit"]["valid_row_count"] == 3
    assert preflight["can_route_to_agent53_field_calibration"] is True
    assert preflight["can_generate_field_evidence"] is False
    assert preflight["can_write_to_actuator"] is False
    assert preflight["can_write_to_release_gate"] is False
    assert "does not prove mechanism validity" in preflight["field_boundary"]
    assert summary["summary_status"] == (
        "grey_box_field_calibration_summary_ready_with_residual_blockers"
    )
    assert summary["can_run_agent53_field_calibration"] is True
    assert summary["agent53_field_candidate_ready"] is False
    assert summary["field_calibration_for_agent53"]["field_physics_coverage"] == 1.0
    assert summary["field_calibration_for_agent53"]["max_field_residual"] == 0.233
    assert summary["field_calibration_for_agent53"]["max_mass_balance_residual"] == 0.015
    assert summary["can_generate_field_evidence"] is False
    assert summary["can_write_to_actuator"] is False
    assert summary["can_write_to_release_gate"] is False


def test_grey_box_field_calibration_summary_can_prepare_agent53_candidate(tmp_path: Path) -> None:
    _write_valid_package(tmp_path, outlet_concentration="0.12")

    preflight = build_grey_box_calibration_package_preflight(
        source_dir=tmp_path,
        external_package_supplied=True,
    )
    summary = build_grey_box_field_calibration_summary(
        source_dir=tmp_path,
        external_package_supplied=True,
        preflight=preflight,
    )

    assert preflight["package_preflight_pass"] is True
    assert summary["summary_status"] == (
        "grey_box_field_calibration_summary_ready_for_agent53_field_candidate"
    )
    assert summary["can_run_agent53_field_calibration"] is True
    assert summary["agent53_field_candidate_ready"] is True
    assert summary["field_calibration_for_agent53"]["max_field_residual"] == 0.1
    assert summary["next_operator_action"] == (
        "run_Agent53_with_evidence_stage_field_physics_calibration_and_keep_release_gate_closed"
    )
    assert summary["can_generate_field_evidence"] is False
    assert summary["can_write_to_actuator"] is False
    assert summary["can_write_to_release_gate"] is False


def test_grey_box_calibration_package_blocks_missing_byproduct_panel(tmp_path: Path) -> None:
    _write_valid_package(tmp_path)
    (tmp_path / f"{BYPRODUCT_TABLE}.csv").unlink()

    preflight = build_grey_box_calibration_package_preflight(
        source_dir=tmp_path,
        external_package_supplied=True,
    )

    assert preflight["package_preflight_pass"] is False
    assert preflight["package_status"] == "grey_box_calibration_package_blocked_at_schema"
    assert "missing_required_tables" in preflight["blocking_reasons"]
    assert "matched_batch_deficit" in preflight["blocking_reasons"]


def test_grey_box_calibration_collection_work_order_waits_for_external_package() -> None:
    preflight = build_grey_box_calibration_package_preflight()
    summary = build_grey_box_field_calibration_summary(preflight=preflight)

    work_order = build_grey_box_calibration_collection_work_order(
        preflight=preflight,
        field_calibration_summary=summary,
        template_dir="outputs/grey_box_calibration_package/grey_box_calibration_package_template",
        validation_command=".venv/bin/python experiments/run_grey_box_calibration_package_preflight.py",
    )

    assert work_order["work_order_id"] == "R8u157_grey_box_calibration_collection_work_order"
    assert work_order["work_order_status"] == (
        "grey_box_calibration_collection_work_order_waiting_for_external_package"
    )
    assert work_order["source_env_var"] == SOURCE_ENV_VAR
    assert work_order["minimum_matched_batch_count"] == 3
    assert work_order["table_work_item_count"] == 5
    assert work_order["field_package_ready_for_agent53"] is False
    assert work_order["next_operator_action"] == (
        "fill_grey_box_calibration_package_template_and_set_GREY_BOX_CALIBRATION_PACKAGE_DIR"
    )
    assert work_order["table_work_items"][0]["table_name"] == BATCH_LAB_TABLE
    assert work_order["table_work_items"][0]["required_columns"] == TABLE_COLUMNS[BATCH_LAB_TABLE]
    assert work_order["table_work_items"][0]["template_csv"].endswith(
        "batch_inlet_outlet_lab.csv"
    )
    assert work_order["table_work_items"][0]["current_status"] == "needs_real_field_rows"
    assert work_order["can_generate_field_evidence"] is False
    assert work_order["can_resume_model_chain"] is False
    assert work_order["can_write_to_actuator"] is False
    assert work_order["can_write_to_release_gate"] is False


def test_grey_box_calibration_collection_work_order_surfaces_repair_scope(
    tmp_path: Path,
) -> None:
    write_grey_box_calibration_package_template(tmp_path)
    preflight = build_grey_box_calibration_package_preflight(
        source_dir=tmp_path,
        external_package_supplied=True,
    )
    summary = build_grey_box_field_calibration_summary(
        source_dir=tmp_path,
        external_package_supplied=True,
        preflight=preflight,
    )

    work_order = build_grey_box_calibration_collection_work_order(
        preflight=preflight,
        field_calibration_summary=summary,
        template_dir=str(tmp_path),
        validation_command=".venv/bin/python experiments/run_grey_box_calibration_package_preflight.py",
    )

    assert work_order["work_order_status"] == (
        "grey_box_calibration_collection_work_order_blocked_by_preflight_repair"
    )
    assert work_order["repair_required"] is True
    assert "template_markers_present" in work_order["blocking_reasons"]
    assert work_order["table_work_items"][0]["template_marker_count"] == 3
    assert work_order["table_work_items"][0]["non_field_row_count"] == 3
    assert work_order["table_work_items"][0]["current_status"] == (
        "replace_template_rows_with_field_rows"
    )


def test_grey_box_calibration_collection_work_order_routes_ready_package(
    tmp_path: Path,
) -> None:
    _write_valid_package(tmp_path, outlet_concentration="0.12")
    preflight = build_grey_box_calibration_package_preflight(
        source_dir=tmp_path,
        external_package_supplied=True,
    )
    summary = build_grey_box_field_calibration_summary(
        source_dir=tmp_path,
        external_package_supplied=True,
        preflight=preflight,
    )

    work_order = build_grey_box_calibration_collection_work_order(
        preflight=preflight,
        field_calibration_summary=summary,
        template_dir=str(tmp_path),
        validation_command=".venv/bin/python experiments/run_grey_box_calibration_package_preflight.py",
    )

    assert work_order["work_order_status"] == (
        "grey_box_calibration_collection_work_order_ready_for_agent53_field_calibration"
    )
    assert work_order["field_package_ready_for_agent53"] is True
    assert work_order["agent53_field_candidate_ready"] is True
    assert work_order["matched_batch_count"] == 3
    assert all(
        item["current_status"] == "table_ready_for_calibration_preflight"
        for item in work_order["table_work_items"]
    )
    assert work_order["can_generate_field_evidence"] is False
    assert work_order["can_write_to_actuator"] is False
    assert work_order["can_write_to_release_gate"] is False


def test_grey_box_calibration_collection_work_order_report_explains_boundary() -> None:
    preflight = build_grey_box_calibration_package_preflight()
    summary = build_grey_box_field_calibration_summary(preflight=preflight)
    work_order = build_grey_box_calibration_collection_work_order(
        preflight=preflight,
        field_calibration_summary=summary,
        template_dir="outputs/grey_box_calibration_package/grey_box_calibration_package_template",
        validation_command=".venv/bin/python experiments/run_grey_box_calibration_package_preflight.py",
    )

    report = grey_box_calibration_collection_work_order_report_md(work_order)

    assert "Grey-Box Calibration Collection Work Order" in report
    assert "batch_inlet_outlet_lab" in report
    assert "data_origin=field" in report
    assert "cannot resume the model chain" in report
    assert "GREY_BOX_CALIBRATION_PACKAGE_DIR" in report


def test_grey_box_submission_readiness_gate_waits_without_field_package() -> None:
    preflight = build_grey_box_calibration_package_preflight()
    summary = build_grey_box_field_calibration_summary(preflight=preflight)
    work_order = build_grey_box_calibration_collection_work_order(
        preflight=preflight,
        field_calibration_summary=summary,
        template_dir="outputs/grey_box_calibration_package/grey_box_calibration_package_template",
        validation_command=".venv/bin/python experiments/run_grey_box_calibration_package_preflight.py",
    )

    gate = build_grey_box_submission_readiness_gate(
        preflight=preflight,
        field_calibration_summary=summary,
        collection_work_order=work_order,
    )

    assert gate["gate_id"] == "R8u160_grey_box_submission_readiness_gate"
    assert gate["gate_status"] == "grey_box_submission_readiness_waiting_for_external_package"
    assert gate["readiness_score"] == 0.143
    assert gate["component_scores"]["source_package_present"] == 0.0
    assert gate["component_scores"]["no_write_boundary_integrity"] == 1.0
    assert gate["highest_priority_gap"]["gap_type"] == "missing_external_package"
    assert gate["highest_priority_gap"]["table"] == "all_required_tables"
    assert gate["highest_priority_gap"]["missing_table_count"] == len(REQUIRED_TABLES)
    assert gate["highest_priority_gap"]["missing_tables"] == list(REQUIRED_TABLES)
    assert gate["highest_priority_gap"]["source_env_var"] == SOURCE_ENV_VAR
    assert gate["can_submit_to_agent53_field_calibration"] is False
    assert gate["can_generate_field_evidence"] is False
    assert gate["can_write_to_actuator"] is False
    assert gate["can_write_to_release_gate"] is False
    assert gate["next_operator_action"] == (
        "fill_grey_box_calibration_package_template_and_set_GREY_BOX_CALIBRATION_PACKAGE_DIR"
    )


def test_grey_box_submission_readiness_gate_blocks_template_rows(
    tmp_path: Path,
) -> None:
    write_grey_box_calibration_package_template(tmp_path)
    preflight = build_grey_box_calibration_package_preflight(
        source_dir=tmp_path,
        external_package_supplied=True,
    )
    summary = build_grey_box_field_calibration_summary(
        source_dir=tmp_path,
        external_package_supplied=True,
        preflight=preflight,
    )
    work_order = build_grey_box_calibration_collection_work_order(
        preflight=preflight,
        field_calibration_summary=summary,
        template_dir=str(tmp_path),
        validation_command=".venv/bin/python experiments/run_grey_box_calibration_package_preflight.py",
    )

    gate = build_grey_box_submission_readiness_gate(
        preflight=preflight,
        field_calibration_summary=summary,
        collection_work_order=work_order,
    )

    assert gate["gate_status"] == "grey_box_submission_readiness_blocked_by_package_preflight"
    assert gate["readiness_score"] < 0.55
    assert gate["component_scores"]["schema_completeness"] == 1.0
    assert gate["component_scores"]["field_origin_integrity"] == 0.0
    assert gate["highest_priority_gap"]["gap_type"] == "replace_template_or_non_field_rows"
    assert gate["highest_priority_gap"]["table"] == BATCH_LAB_TABLE
    assert gate["can_submit_to_agent53_field_calibration"] is False


def test_grey_box_submission_readiness_gate_routes_ready_package_with_residual_review(
    tmp_path: Path,
) -> None:
    _write_valid_package(tmp_path)
    preflight = build_grey_box_calibration_package_preflight(
        source_dir=tmp_path,
        external_package_supplied=True,
    )
    summary = build_grey_box_field_calibration_summary(
        source_dir=tmp_path,
        external_package_supplied=True,
        preflight=preflight,
    )
    work_order = build_grey_box_calibration_collection_work_order(
        preflight=preflight,
        field_calibration_summary=summary,
        template_dir=str(tmp_path),
        validation_command=".venv/bin/python experiments/run_grey_box_calibration_package_preflight.py",
    )

    gate = build_grey_box_submission_readiness_gate(
        preflight=preflight,
        field_calibration_summary=summary,
        collection_work_order=work_order,
    )

    assert gate["gate_status"] == (
        "grey_box_submission_readiness_ready_for_agent53_calibration_with_residual_review"
    )
    assert gate["readiness_score"] == 0.95
    assert gate["component_scores"]["matched_batch_coverage"] == 1.0
    assert gate["component_scores"]["agent53_summary_readiness"] == 1.0
    assert gate["component_scores"]["residual_threshold_readiness"] == 0.5
    assert gate["can_submit_to_agent53_field_calibration"] is True
    assert gate["can_submit_to_agent53_field_candidate"] is False
    assert gate["can_generate_field_evidence"] is False


def test_grey_box_submission_readiness_gate_ready_for_agent53_candidate(
    tmp_path: Path,
) -> None:
    _write_valid_package(tmp_path, outlet_concentration="0.12")
    preflight = build_grey_box_calibration_package_preflight(
        source_dir=tmp_path,
        external_package_supplied=True,
    )
    summary = build_grey_box_field_calibration_summary(
        source_dir=tmp_path,
        external_package_supplied=True,
        preflight=preflight,
    )
    work_order = build_grey_box_calibration_collection_work_order(
        preflight=preflight,
        field_calibration_summary=summary,
        template_dir=str(tmp_path),
        validation_command=".venv/bin/python experiments/run_grey_box_calibration_package_preflight.py",
    )

    gate = build_grey_box_submission_readiness_gate(
        preflight=preflight,
        field_calibration_summary=summary,
        collection_work_order=work_order,
    )
    report = grey_box_submission_readiness_gate_report_md(gate)

    assert gate["gate_status"] == "grey_box_submission_readiness_ready_for_agent53_field_candidate"
    assert gate["readiness_score"] == 1.0
    assert gate["can_submit_to_agent53_field_candidate"] is True
    assert gate["highest_priority_gap"]["gap_type"] == "none"
    assert "Grey-Box Submission Readiness Gate" in report
    assert "cannot generate field evidence" in report
    assert "GREY_BOX_CALIBRATION_PACKAGE_DIR" in report


def _write_valid_package(root: Path, *, outlet_concentration: str = "0.28") -> None:
    batch_ids = ["B001", "B002", "B003"]
    _write_csv(
        root / f"{BATCH_LAB_TABLE}.csv",
        TABLE_COLUMNS[BATCH_LAB_TABLE],
        [
            {
                "batch_id": batch_id,
                "sample_time_min": str(10 + index),
                "target_pollutant": "diclofenac",
                "inlet_concentration": "1.20",
                "outlet_concentration": outlet_concentration,
                "pollutant_unit": "mg_L",
                "matrix_indicator": "42",
                "matrix_indicator_unit": "mgCOD_L",
                "lab_method": "LCMS",
                "qa_flag": "pass",
                "data_origin": "field",
            }
            for index, batch_id in enumerate(batch_ids)
        ],
    )
    _write_csv(
        root / f"{HYDRAULIC_TABLE}.csv",
        TABLE_COLUMNS[HYDRAULIC_TABLE],
        [
            {
                "batch_id": batch_id,
                "measurement_time_min": str(12 + index),
                "unit_id": "loop_reactor_1",
                "effective_HRT_min": "34.5",
                "nominal_HRT_min": "36.0",
                "rtd_t10_min": "18.0",
                "rtd_t90_min": "52.0",
                "tracer_recovery_fraction": "0.91",
                "flow_Lmin": "2.2",
                "volume_L": "79.2",
                "qa_flag": "pass",
                "data_origin": "field",
            }
            for index, batch_id in enumerate(batch_ids)
        ],
    )
    _write_csv(
        root / f"{OXIDANT_TABLE}.csv",
        TABLE_COLUMNS[OXIDANT_TABLE],
        [
            {
                "batch_id": batch_id,
                "timestamp_min": str(8 + index),
                "oxidant_name": "persulfate",
                "dose_mg_L": "18.0",
                "residual_mg_L": "2.1",
                "energy_kWh_m3": "0.42",
                "qa_flag": "pass",
                "data_origin": "field",
            }
            for index, batch_id in enumerate(batch_ids)
        ],
    )
    _write_csv(
        root / f"{CATALYST_TABLE}.csv",
        TABLE_COLUMNS[CATALYST_TABLE],
        [
            {
                "batch_id": batch_id,
                "timestamp_min": str(5 + index),
                "catalyst_id": "cat_A",
                "catalyst_age_h": "120",
                "catalyst_activity_label": "0.74",
                "regeneration_event": "none",
                "regeneration_count": "1",
                "qa_flag": "pass",
                "data_origin": "field",
            }
            for index, batch_id in enumerate(batch_ids)
        ],
    )
    _write_csv(
        root / f"{BYPRODUCT_TABLE}.csv",
        TABLE_COLUMNS[BYPRODUCT_TABLE],
        [
            {
                "batch_id": batch_id,
                "sample_time_min": str(40 + index),
                "analyte": "chlorinated_byproduct_A",
                "value": "0.018",
                "unit": "mg_L",
                "detection_limit": "0.001",
                "method": "GCMS",
                "qa_flag": "pass",
                "data_origin": "field",
            }
            for index, batch_id in enumerate(batch_ids)
        ],
    )


def _write_csv(path: Path, columns: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)

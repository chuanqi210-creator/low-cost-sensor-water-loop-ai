import csv
from pathlib import Path

from water_ai.field_supported_kg_edge_package import (
    CLAIM_ACTION_TABLE,
    EDGE_TABLE,
    FAILURE_BOUNDARY_TABLE,
    FIELD_SUPPORT_TABLE,
    SOURCE_BASIS_TABLE,
    SOURCE_ENV_VAR,
    TABLE_COLUMNS,
    build_field_supported_kg_edge_package_preflight,
    write_field_supported_kg_edge_package_template,
)


def test_field_supported_kg_edge_package_waits_for_external_dir() -> None:
    preflight = build_field_supported_kg_edge_package_preflight()

    assert preflight["source_env_var"] == SOURCE_ENV_VAR
    assert preflight["package_status"] == (
        "field_supported_kg_edge_package_waiting_for_FIELD_SUPPORTED_KG_EDGE_PACKAGE_DIR"
    )
    assert preflight["package_preflight_pass"] is False
    assert preflight["can_route_to_kg_reasoning_field_edge_update"] is False
    assert preflight["can_upgrade_site_specific_claims"] is False
    assert preflight["can_generate_field_evidence"] is False
    assert preflight["can_write_to_actuator"] is False
    assert preflight["can_write_to_release_gate"] is False
    assert "missing_external_package_dir" in preflight["blocking_reasons"]


def test_field_supported_kg_edge_package_blocks_template_rows(tmp_path: Path) -> None:
    write_field_supported_kg_edge_package_template(tmp_path)

    preflight = build_field_supported_kg_edge_package_preflight(
        source_dir=tmp_path,
        external_package_supplied=True,
    )

    assert preflight["package_preflight_pass"] is False
    assert preflight["package_status"] == "field_supported_kg_edge_package_blocked_at_field_origin"
    assert "template_markers_present" in preflight["blocking_reasons"]
    assert "non_field_rows_present" in preflight["blocking_reasons"]
    assert preflight["matched_edge_count"] == 0


def test_field_supported_kg_edge_package_accepts_minimum_field_edges(tmp_path: Path) -> None:
    _write_valid_package(tmp_path)

    preflight = build_field_supported_kg_edge_package_preflight(
        source_dir=tmp_path,
        external_package_supplied=True,
    )

    assert preflight["package_status"] == "field_supported_kg_edge_package_ready_for_kg_reasoning"
    assert preflight["package_preflight_pass"] is True
    assert preflight["matched_edge_count"] == 3
    assert preflight["field_supported_edge_coverage_candidate"] == 1.0
    assert preflight["edge_audit"]["valid_row_count"] == 3
    assert preflight["source_basis_audit"]["valid_row_count"] == 3
    assert preflight["field_support_audit"]["valid_row_count"] == 3
    assert preflight["failure_boundary_audit"]["valid_row_count"] == 3
    assert preflight["claim_action_audit"]["valid_row_count"] == 3
    assert preflight["field_support_audit"]["mean_field_support_score"] == 0.82
    assert preflight["can_route_to_kg_reasoning_field_edge_update"] is True
    assert preflight["can_upgrade_site_specific_claims"] is False
    assert preflight["can_generate_field_evidence"] is False
    assert preflight["can_write_to_actuator"] is False
    assert preflight["can_write_to_release_gate"] is False
    assert "does not prove a site-specific mechanism claim" in preflight["field_boundary"]


def test_field_supported_kg_edge_package_blocks_missing_failure_boundary(tmp_path: Path) -> None:
    _write_valid_package(tmp_path)
    (tmp_path / f"{FAILURE_BOUNDARY_TABLE}.csv").unlink()

    preflight = build_field_supported_kg_edge_package_preflight(
        source_dir=tmp_path,
        external_package_supplied=True,
    )

    assert preflight["package_preflight_pass"] is False
    assert preflight["package_status"] == "field_supported_kg_edge_package_blocked_at_schema"
    assert "missing_required_tables" in preflight["blocking_reasons"]
    assert "matched_edge_deficit" in preflight["blocking_reasons"]


def _write_valid_package(root: Path) -> None:
    edge_ids = ["E001", "E002", "E003"]
    _write_csv(
        root / f"{EDGE_TABLE}.csv",
        TABLE_COLUMNS[EDGE_TABLE],
        [
            {
                "edge_id": edge_id,
                "pollutant": "diclofenac",
                "material_or_unit": "cat_A",
                "condition_axis": "matrix_COD",
                "relation": "matrix_inhibits_degradation",
                "hidden_state": "matrix_inhibition",
                "action_constraint_id": "hold_for_lab_review",
                "evidence_stage": "field_supported",
                "qa_flag": "pass",
                "data_origin": "field",
            }
            for edge_id in edge_ids
        ],
    )
    _write_csv(
        root / f"{SOURCE_BASIS_TABLE}.csv",
        TABLE_COLUMNS[SOURCE_BASIS_TABLE],
        [
            {
                "edge_id": edge_id,
                "source_basis_id": f"SB_{edge_id}",
                "source_type": "field_lab",
                "source_reference": f"lab_batch_{edge_id}",
                "source_detail": "offline LCMS plus operation log aligned by batch_id",
                "qa_flag": "pass",
                "data_origin": "field",
            }
            for edge_id in edge_ids
        ],
    )
    _write_csv(
        root / f"{FIELD_SUPPORT_TABLE}.csv",
        TABLE_COLUMNS[FIELD_SUPPORT_TABLE],
        [
            {
                "edge_id": edge_id,
                "batch_id": f"B{index:03d}",
                "node_id": "loop_reactor_1",
                "observed_metric": "removal_drop_under_high_COD",
                "observed_value": "0.31",
                "expected_direction": "decrease",
                "support_direction": "supported",
                "field_support_score": "0.82",
                "qa_flag": "pass",
                "data_origin": "field",
            }
            for index, edge_id in enumerate(edge_ids, start=1)
        ],
    )
    _write_csv(
        root / f"{FAILURE_BOUNDARY_TABLE}.csv",
        TABLE_COLUMNS[FAILURE_BOUNDARY_TABLE],
        [
            {
                "edge_id": edge_id,
                "boundary_type": "site_specific_claim_boundary",
                "boundary_statement": "Only valid for aligned high-COD batches with LCMS labels.",
                "cannot_claim_without": "field holdout and operator review",
                "qa_flag": "pass",
                "data_origin": "field",
            }
            for edge_id in edge_ids
        ],
    )
    _write_csv(
        root / f"{CLAIM_ACTION_TABLE}.csv",
        TABLE_COLUMNS[CLAIM_ACTION_TABLE],
        [
            {
                "edge_id": edge_id,
                "claim_or_action_id": "release_gate_constraint",
                "constraint_type": "explanation_only_before_release_review",
                "allowed_use": "mechanism explanation candidate",
                "blocked_use": "automatic release or actuator relaxation",
                "human_review_required": "true",
                "qa_flag": "pass",
                "data_origin": "field",
            }
            for edge_id in edge_ids
        ],
    )


def _write_csv(path: Path, columns: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)

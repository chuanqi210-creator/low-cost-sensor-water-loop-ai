import csv
from pathlib import Path

from water_ai.sparse_topology_installability_package import (
    CONSTRAINT_TABLE,
    COST_TABLE,
    HYDRAULIC_DELAY_TABLE,
    LABEL_TABLE,
    SOURCE_ENV_VAR,
    TABLE_COLUMNS,
    TOPOLOGY_TABLE,
    build_sparse_topology_installability_package_preflight,
    write_sparse_topology_installability_package_template,
)


def test_sparse_topology_installability_package_waits_for_external_dir() -> None:
    preflight = build_sparse_topology_installability_package_preflight()

    assert preflight["source_env_var"] == SOURCE_ENV_VAR
    assert preflight["package_status"] == (
        "sparse_topology_installability_package_waiting_for_SPARSE_TOPOLOGY_INSTALLABILITY_PACKAGE_DIR"
    )
    assert preflight["package_preflight_pass"] is False
    assert preflight["can_route_to_agent48_sparse_layout_holdout"] is False
    assert preflight["can_authorize_field_deployment"] is False
    assert preflight["can_generate_field_evidence"] is False
    assert preflight["can_write_to_actuator"] is False
    assert preflight["can_write_to_release_gate"] is False
    assert "missing_external_package_dir" in preflight["blocking_reasons"]


def test_sparse_topology_installability_package_blocks_template_rows(tmp_path: Path) -> None:
    write_sparse_topology_installability_package_template(tmp_path)

    preflight = build_sparse_topology_installability_package_preflight(
        source_dir=tmp_path,
        external_package_supplied=True,
    )

    assert preflight["package_preflight_pass"] is False
    assert preflight["package_status"] == (
        "sparse_topology_installability_package_blocked_at_field_origin"
    )
    assert "template_markers_present" in preflight["blocking_reasons"]
    assert "non_field_rows_present" in preflight["blocking_reasons"]
    assert preflight["matched_node_count"] == 0


def test_sparse_topology_installability_package_accepts_minimum_field_nodes(
    tmp_path: Path,
) -> None:
    _write_valid_package(tmp_path)

    preflight = build_sparse_topology_installability_package_preflight(
        source_dir=tmp_path,
        external_package_supplied=True,
    )

    assert preflight["package_status"] == (
        "sparse_topology_installability_package_ready_for_agent48_layout_holdout"
    )
    assert preflight["package_preflight_pass"] is True
    assert preflight["matched_node_count"] == 3
    assert preflight["sparse_topology_coverage_candidate"] == 1.0
    assert preflight["installable_candidate_node_count"] == 3
    assert preflight["path_stage_count"] == 3
    assert preflight["hidden_state_count"] == 3
    assert preflight["topology_audit"]["valid_row_count"] == 3
    assert preflight["cost_audit"]["valid_row_count"] == 3
    assert preflight["constraint_audit"]["valid_row_count"] == 3
    assert preflight["hydraulic_delay_audit"]["valid_row_count"] == 3
    assert preflight["label_audit"]["valid_row_count"] == 3
    assert preflight["cost_audit"]["mean_capex_usd"] == 250.0
    assert preflight["hydraulic_delay_audit"]["mean_delay_min"] == 6.0
    assert preflight["can_route_to_agent48_sparse_layout_holdout"] is True
    assert preflight["can_authorize_field_deployment"] is False
    assert preflight["can_generate_field_evidence"] is False
    assert preflight["can_write_to_actuator"] is False
    assert preflight["can_write_to_release_gate"] is False
    assert "does not prove a deployable sensor layout" in preflight["field_boundary"]


def test_sparse_topology_installability_package_blocks_missing_label_matrix(
    tmp_path: Path,
) -> None:
    _write_valid_package(tmp_path)
    (tmp_path / f"{LABEL_TABLE}.csv").unlink()

    preflight = build_sparse_topology_installability_package_preflight(
        source_dir=tmp_path,
        external_package_supplied=True,
    )

    assert preflight["package_preflight_pass"] is False
    assert preflight["package_status"] == "sparse_topology_installability_package_blocked_at_schema"
    assert "missing_required_tables" in preflight["blocking_reasons"]
    assert "matched_node_deficit" in preflight["blocking_reasons"]


def test_sparse_topology_installability_package_blocks_uninstallable_nodes(
    tmp_path: Path,
) -> None:
    _write_valid_package(tmp_path, installable=False)

    preflight = build_sparse_topology_installability_package_preflight(
        source_dir=tmp_path,
        external_package_supplied=True,
    )

    assert preflight["package_preflight_pass"] is False
    assert preflight["package_status"] == (
        "sparse_topology_installability_package_blocked_at_installability"
    )
    assert "installable_node_deficit" in preflight["blocking_reasons"]
    assert preflight["installable_candidate_node_count"] == 0
    assert preflight["matched_node_count"] == 0


def _write_valid_package(root: Path, *, installable: bool = True) -> None:
    node_ids = ["N1_inlet", "N2_loop_reactor", "N3_release_boundary"]
    _write_csv(
        root / f"{TOPOLOGY_TABLE}.csv",
        TABLE_COLUMNS[TOPOLOGY_TABLE],
        [
            {
                "node_id": node_id,
                "node_type": "sampling_node",
                "upstream_node_id": "SOURCE" if index == 1 else node_ids[index - 2],
                "downstream_node_id": "SINK" if index == 3 else node_ids[index],
                "unit_id": f"U{index}",
                "path_stage": ["inlet", "recirculation_reactor", "release_boundary"][index - 1],
                "edge_length_m": str(index * 2.0),
                "nominal_flow_Lmin": "12.5",
                "qa_flag": "pass",
                "data_origin": "field",
            }
            for index, node_id in enumerate(node_ids, start=1)
        ],
    )
    _write_csv(
        root / f"{COST_TABLE}.csv",
        TABLE_COLUMNS[COST_TABLE],
        [
            {
                "node_id": node_id,
                "modality": ["pH", "UV254", "ORP"][index - 1],
                "sensor_type": "low_cost_probe",
                "capex_usd": str(index * 125),
                "opex_usd_month": "15",
                "maintenance_interval_day": "14",
                "installable_flag": "true" if installable else "false",
                "power_available": "true",
                "communication_available": "true",
                "qa_flag": "pass",
                "data_origin": "field",
            }
            for index, node_id in enumerate(node_ids, start=1)
        ],
    )
    _write_csv(
        root / f"{CONSTRAINT_TABLE}.csv",
        TABLE_COLUMNS[CONSTRAINT_TABLE],
        [
            {
                "node_id": node_id,
                "constraint_id": f"C{index}",
                "access_level": "medium",
                "safety_class": "wet_area_low_voltage",
                "maintenance_window_min": "30",
                "downtime_cost_index": "0.2",
                "operator_review_required": "true",
                "blocked_reason": "none",
                "qa_flag": "pass",
                "data_origin": "field",
            }
            for index, node_id in enumerate(node_ids, start=1)
        ],
    )
    _write_csv(
        root / f"{HYDRAULIC_DELAY_TABLE}.csv",
        TABLE_COLUMNS[HYDRAULIC_DELAY_TABLE],
        [
            {
                "node_id": node_id,
                "upstream_reference": "SOURCE" if index == 1 else node_ids[index - 2],
                "delay_min": str(index * 3.0),
                "mixing_volume_L": "80",
                "short_circuit_risk": "0.15",
                "hydraulic_confidence": "0.8",
                "qa_flag": "pass",
                "data_origin": "field",
            }
            for index, node_id in enumerate(node_ids, start=1)
        ],
    )
    _write_csv(
        root / f"{LABEL_TABLE}.csv",
        TABLE_COLUMNS[LABEL_TABLE],
        [
            {
                "node_id": node_id,
                "batch_id": f"B{index:03d}",
                "timestamp_min": str(index * 10),
                "hidden_state": [
                    "matrix_inhibition",
                    "catalyst_activity",
                    "residual_pollutant",
                ][index - 1],
                "label_value": str(0.2 * index),
                "label_source": "offline_lab",
                "layout_holdout_split": "field_holdout",
                "qa_flag": "pass",
                "data_origin": "field",
            }
            for index, node_id in enumerate(node_ids, start=1)
        ],
    )


def _write_csv(path: Path, columns: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)

from __future__ import annotations

from collections.abc import Sequence

from water_ai.agents.base import BaseAgent
from water_ai.domain import AgentReport, QualityIssue, SensorReading, Severity
from water_ai.soft_sensor_model import FEATURE_COLUMNS, HYDRAULIC_PATH_FEATURE_COLUMNS


REQUIRED_LAYOUT_FIELDS = (
    "layout_id",
    "selected_nodes",
    "selected_modalities",
    "missingness_mask_contract",
)

MATRIX_FEATURE_CHANNELS = [
    "sensor_value",
    "availability_mask",
    "time_since_last_observed_min",
    "data_quality_score",
    "observation_axis_weight",
    "hydraulic_path_stage_prior",
    "grey_box_residual_prior",
]

FIELD_SCHEMA_PATCH = [
    "batch_id",
    "timestamp_min",
    "layout_id",
    "node_id",
    "zone",
    "modality",
    "sensor_value",
    "availability_mask",
    "missingness_reason",
    "time_since_last_observed_min",
    "sensor_quality_score",
    "path_stage_id",
    "hydraulic_path_role",
    "stage_coverage_mask",
    "direct_path_stage_coverage_mask",
    "proxy_path_stage_coverage_mask",
    "release_boundary_flag",
    "recirculation_loop_flag",
]


class SoftSensorMatrixCouplingAgent(BaseAgent):
    """Bridge sparse sensor placement outputs into layout-aware soft sensor features."""

    name = "soft_sensor_matrix_coupling_agent"

    def __init__(
        self,
        *,
        sensor_layout_interface: dict[str, object] | None = None,
        sparse_placement_metrics: dict[str, object] | None = None,
        observation_contract_metrics: dict[str, object] | None = None,
        soft_sensor_training_metrics: dict[str, object] | None = None,
        grey_box_physics_metrics: dict[str, object] | None = None,
        soft_sensor_layout_context: dict[str, object] | None = None,
        field_path_label_package: dict[str, object] | None = None,
        data_origin: str = "synthetic_layout_contract",
    ) -> None:
        self.sensor_layout_interface = sensor_layout_interface or self._interface_from_sparse_metrics(sparse_placement_metrics or {})
        self.sparse_placement_metrics = sparse_placement_metrics or {}
        self.observation_contract_metrics = observation_contract_metrics or {}
        self.soft_sensor_training_metrics = soft_sensor_training_metrics or {}
        self.grey_box_physics_metrics = grey_box_physics_metrics or {}
        self.soft_sensor_layout_context = soft_sensor_layout_context or {}
        self.field_path_label_package = field_path_label_package or {}
        self.data_origin = data_origin

    def run(self, readings: Sequence[SensorReading]) -> AgentReport:
        del readings
        contract = self._feature_contract()
        stress_tests = self._missingness_stress_tests(contract)
        readiness = self._readiness(contract, stress_tests)
        issues = self._issues(readiness)
        recommendations = self._recommendations(readiness)
        summary = (
            f"软传感矩阵耦合：{readiness['soft_sensor_matrix_status']}；"
            f"layout_contract_score={readiness['layout_contract_score']:.3f}，"
            f"missingness_robustness={readiness['missingness_robustness_score']:.3f}。"
        )
        confidence = round(
            min(0.91, max(0.25, 0.40 + 0.42 * readiness["soft_sensor_matrix_score"] - 0.035 * len(issues))),
            3,
        )
        return AgentReport(
            agent_name=self.name,
            confidence=confidence,
            summary=summary,
            issues=issues,
            recommendations=recommendations,
            metrics={
                "method_contract": self._method_contract(),
                "feature_contract": contract,
                "missingness_stress_tests": stress_tests,
                "training_schema_gap": self._training_schema_gap(contract),
                "field_path_endpoint_label_package_preflight": contract["field_path_endpoint_label_package_preflight"],
                "readiness": readiness,
                "agent50_writeback": self._agent50_writeback(readiness),
            },
        )

    @staticmethod
    def _interface_from_sparse_metrics(metrics: dict[str, object]) -> dict[str, object]:
        interface = metrics.get("soft_sensor_interface", {})
        return interface if isinstance(interface, dict) else {}

    def _feature_contract(self) -> dict[str, object]:
        interface = self.sensor_layout_interface
        selected_nodes = [str(item) for item in interface.get("selected_nodes", [])]
        selected_modalities = [str(item) for item in interface.get("selected_modalities", [])]
        mask_contract = interface.get("missingness_mask_contract", {})
        mask_contract = mask_contract if isinstance(mask_contract, dict) else {}
        coverage = interface.get("coverage_for_soft_sensor", {})
        coverage = coverage if isinstance(coverage, dict) else {}
        grey_readiness = self.grey_box_physics_metrics.get("readiness", {})
        grey_readiness = grey_readiness if isinstance(grey_readiness, dict) else {}
        pressure_headloss_contract = self._pressure_headloss_candidate_contract()
        hydraulic_path_contract = self._hydraulic_path_feature_contract()
        field_path_endpoint_label_package_contract = self._field_path_endpoint_label_package_contract()
        field_path_endpoint_label_package_preflight = self._field_path_endpoint_label_package_preflight(
            field_path_endpoint_label_package_contract
        )
        return {
            "layout_id": str(interface.get("layout_id", "missing_layout_id")),
            "layout_source": "Agent48.soft_sensor_interface",
            "tensor_axes": ["time", "node", "modality", "feature_channel"],
            "feature_channels": MATRIX_FEATURE_CHANNELS,
            "selected_nodes": selected_nodes,
            "selected_modalities": selected_modalities,
            "node_count": len(selected_nodes),
            "modality_count": len(selected_modalities),
            "matrix_shape": list(interface.get("matrix_shape", [len(selected_nodes), len(coverage) or 0])),
            "mask_shape": list(mask_contract.get("mask_shape", [len(selected_nodes), len(selected_modalities)])),
            "field_schema_patch": FIELD_SCHEMA_PATCH,
            "coverage_for_soft_sensor": coverage,
            "grey_box_prior_available": bool(grey_readiness.get("synthetic_prior_ready", False)),
            "grey_box_status": str(grey_readiness.get("grey_box_physics_status", "not_available")),
            "hydraulic_path_feature_contract": hydraulic_path_contract,
            "hydraulic_path_feature_terms": hydraulic_path_contract["feature_terms"],
            "field_path_endpoint_label_package_contract": field_path_endpoint_label_package_contract,
            "field_path_endpoint_label_package_preflight": field_path_endpoint_label_package_preflight,
            "pressure_headloss_candidate_contract": pressure_headloss_contract,
            "pressure_headloss_candidate_feature_terms": pressure_headloss_contract["candidate_feature_terms"],
            "layout_context_from_live_agent": self.soft_sensor_layout_context,
            "cannot_do": [
                "cannot train a field-validated layout-aware model without node-specific field values",
                "cannot treat synthetic dropout as real fouling, communication loss or delayed lab evidence",
                "cannot treat pressure/headloss candidates as installed sensors before field topology and labels",
                "cannot treat polishing proxy coverage as final effluent release support",
                "cannot write release gate from layout contract alone",
            ],
        }

    @staticmethod
    def _field_path_endpoint_label_package_contract() -> dict[str, object]:
        table_contracts = {
            "site_topology_or_bed_geometry": {
                "required_fields": [
                    "site_id",
                    "node_id",
                    "zone",
                    "upstream_node_id",
                    "downstream_node_id",
                    "path_stage_id",
                    "hydraulic_path_role",
                    "nominal_flow_Lmin",
                    "nominal_HRT_min",
                    "recycle_ratio",
                    "release_boundary_flag",
                    "recirculation_loop_flag",
                ],
                "primary_key": ["site_id", "node_id"],
                "purpose": "map installed nodes to hydraulic path stages before field layout holdout",
            },
            "node_modality_sensor_timeseries": {
                "required_fields": [
                    "batch_id",
                    "timestamp_min",
                    "layout_id",
                    "node_id",
                    "zone",
                    "modality",
                    "sensor_value",
                    "availability_mask",
                    "time_since_last_observed_min",
                    "data_origin",
                ],
                "primary_key": ["batch_id", "timestamp_min", "node_id", "modality"],
                "purpose": "replace global modality fallback with node-specific field observations",
            },
            "hydraulic_path_stage_labels": {
                "required_fields": [
                    "batch_id",
                    "layout_id",
                    "node_id",
                    "zone",
                    "path_stage_id",
                    "hydraulic_path_role",
                    "stage_coverage_label",
                    "direct_path_stage_coverage_label",
                    "proxy_path_stage_coverage_label",
                    "label_source",
                    "reviewer_id",
                    "review_time_min",
                ],
                "primary_key": ["batch_id", "layout_id", "node_id", "path_stage_id"],
                "purpose": "validate whether synthetic path-stage coverage features match field-reviewed path labels",
            },
            "final_effluent_endpoint_labels": {
                "required_fields": [
                    "batch_id",
                    "endpoint_node_id",
                    "sample_time_min",
                    "final_effluent_direct_observed",
                    "release_gate_label",
                    "release_risk_label",
                    "analyte",
                    "value",
                    "unit",
                    "qa_flag",
                    "reviewer_id",
                ],
                "primary_key": ["batch_id", "endpoint_node_id", "sample_time_min", "analyte"],
                "purpose": "prevent polishing proxy observations from being treated as final effluent release support",
            },
            "campaign_operation_log": {
                "required_fields": [
                    "campaign_id",
                    "batch_id",
                    "action_id",
                    "start_min",
                    "end_min",
                    "recycle_ratio",
                    "hold_time_min",
                    "release_policy",
                    "operator_override",
                ],
                "primary_key": ["campaign_id", "batch_id", "action_id", "start_min"],
                "purpose": "connect field labels to recycle, hold, dose, switch and release candidate actions",
            },
            "offline_lab_results": {
                "required_fields": [
                    "batch_id",
                    "sample_time_min",
                    "sample_source",
                    "analyte",
                    "value",
                    "unit",
                    "method",
                    "qa_flag",
                ],
                "primary_key": ["batch_id", "sample_time_min", "sample_source", "analyte"],
                "purpose": "provide field labels for residual, byproduct/release risk and soft-sensor holdout targets",
            },
        }
        return {
            "contract_id": "R8u66_field_path_endpoint_label_package_contract",
            "package_status": "field_path_endpoint_label_package_contract_ready_needs_real_rows",
            "minimum_matched_batch_count": 5,
            "required_tables": list(table_contracts),
            "table_contracts": table_contracts,
            "template_marker_policy": {
                "reject_template_only": True,
                "reject_todo_values": True,
                "reject_sample_only": True,
            },
            "acceptance_gates": [
                "all_required_tables_present",
                "no_template_or_todo_rows",
                "required_fields_nonempty",
                "minimum_matched_batch_count_met",
                "node_specific_values_present",
                "final_effluent_endpoint_labels_present",
                "operator_or_reviewer_fields_present",
            ],
            "can_route_to_field_layout_holdout_when": (
                "all required tables contain non-template field rows and at least 5 batch_id values are matched "
                "across node sensor values, path stage labels, final endpoint labels, operation logs and lab labels"
            ),
            "cannot_do": [
                "cannot upgrade synthetic layout holdout to field performance without accepted package rows",
                "cannot use final effluent release gate labels without direct endpoint lab/reviewer evidence",
                "cannot write actuator or release gate from this package contract alone",
            ],
        }

    def _field_path_endpoint_label_package_preflight(self, contract: dict[str, object]) -> dict[str, object]:
        package = self.field_path_label_package
        required_tables = [str(item) for item in contract.get("required_tables", [])]
        table_contracts = contract.get("table_contracts", {})
        table_contracts = table_contracts if isinstance(table_contracts, dict) else {}
        if not package:
            alignment_patch_plan = self._field_path_endpoint_alignment_patch_plan(
                required_tables=required_tables,
                batch_tables=[table for table in required_tables if table != "site_topology_or_bed_geometry"],
                table_row_counts={table: 0 for table in required_tables},
                table_batch_counts={table: 0 for table in required_tables},
                missing_batch_ids_by_table={},
                batch_alignment_gap_count=0,
                matched_batch_count=0,
                minimum_batches=int(contract.get("minimum_matched_batch_count", 5) or 5),
                blockers=["no_field_path_endpoint_label_package_supplied"],
            )
            return {
                "preflight_status": "no_field_path_endpoint_label_package_supplied",
                "required_tables": required_tables,
                "missing_tables": required_tables,
                "empty_tables": [],
                "invalid_table_shapes": [],
                "template_marker_count": 0,
                "required_field_gap_count": 0,
                "table_row_counts": {table: 0 for table in required_tables},
                "table_batch_counts": {table: 0 for table in required_tables},
                "batch_alignment_gap_count": 0,
                "required_matched_batch_deficit": alignment_patch_plan["required_matched_batch_deficit"],
                "missing_batch_ids_by_table": {},
                "alignment_patch_plan": alignment_patch_plan,
                "matched_batch_count": 0,
                "accepted_batch_ids": [],
                "can_route_to_field_layout_holdout": False,
                "next_operator_action": "submit_field_path_endpoint_label_package_rows",
                "field_boundary": "contract only; no real path/endpoint package rows have been supplied",
            }
        if not isinstance(package, dict):
            alignment_patch_plan = self._field_path_endpoint_alignment_patch_plan(
                required_tables=required_tables,
                batch_tables=[table for table in required_tables if table != "site_topology_or_bed_geometry"],
                table_row_counts={table: 0 for table in required_tables},
                table_batch_counts={table: 0 for table in required_tables},
                missing_batch_ids_by_table={},
                batch_alignment_gap_count=0,
                matched_batch_count=0,
                minimum_batches=int(contract.get("minimum_matched_batch_count", 5) or 5),
                blockers=["field_path_endpoint_label_package_invalid_root"],
            )
            return {
                "preflight_status": "field_path_endpoint_label_package_invalid_root",
                "required_tables": required_tables,
                "missing_tables": required_tables,
                "empty_tables": [],
                "invalid_table_shapes": ["root:not_object"],
                "template_marker_count": 0,
                "required_field_gap_count": 0,
                "table_row_counts": {table: 0 for table in required_tables},
                "table_batch_counts": {table: 0 for table in required_tables},
                "batch_alignment_gap_count": 0,
                "required_matched_batch_deficit": alignment_patch_plan["required_matched_batch_deficit"],
                "missing_batch_ids_by_table": {},
                "alignment_patch_plan": alignment_patch_plan,
                "matched_batch_count": 0,
                "accepted_batch_ids": [],
                "can_route_to_field_layout_holdout": False,
                "next_operator_action": "resubmit_package_as_table_to_rows_object",
                "field_boundary": "invalid package root cannot be treated as field evidence",
            }

        missing_tables = [table for table in required_tables if table not in package]
        empty_tables: list[str] = []
        invalid_table_shapes: list[str] = []
        required_field_gaps: list[dict[str, object]] = []
        template_marker_count = 0
        batch_sets: dict[str, set[str]] = {}
        table_row_counts: dict[str, int] = {}

        for table in required_tables:
            rows = package.get(table, [])
            if not isinstance(rows, list):
                invalid_table_shapes.append(f"{table}:not_list")
                table_row_counts[table] = 0
                continue
            table_row_counts[table] = len(rows)
            if not rows:
                empty_tables.append(table)
                batch_sets[table] = set()
                continue
            table_spec = table_contracts.get(table, {})
            table_spec = table_spec if isinstance(table_spec, dict) else {}
            required_fields = [str(item) for item in table_spec.get("required_fields", [])]
            table_batches: set[str] = set()
            for row_index, row in enumerate(rows):
                if not isinstance(row, dict):
                    invalid_table_shapes.append(f"{table}[{row_index}]:not_object")
                    continue
                if self._has_template_marker(row):
                    template_marker_count += 1
                missing_fields = [
                    field
                    for field in required_fields
                    if field not in row or row.get(field) in {None, "", "TODO", "TODO_VALUE", "template"}
                ]
                if missing_fields:
                    required_field_gaps.append(
                        {
                            "table": table,
                            "row_index": row_index,
                            "missing_fields": missing_fields,
                        }
                    )
                batch_id = row.get("batch_id")
                if batch_id not in {None, ""}:
                    table_batches.add(str(batch_id))
            batch_sets[table] = table_batches

        batch_tables = [table for table in required_tables if table != "site_topology_or_bed_geometry"]
        matched_batches = set.intersection(*(batch_sets.get(table, set()) for table in batch_tables)) if batch_tables else set()
        matched_batch_count = len(matched_batches)
        minimum_batches = int(contract.get("minimum_matched_batch_count", 5) or 5)
        required_field_gap_count = len(required_field_gaps)
        table_batch_counts = {table: len(batch_sets.get(table, set())) for table in required_tables}
        batch_universe = self._field_path_endpoint_batch_universe(batch_sets, batch_tables)
        missing_batch_ids_by_table = {
            table: sorted(batch_universe - batch_sets.get(table, set()))
            for table in batch_tables
            if batch_universe - batch_sets.get(table, set())
        }
        batch_alignment_gap_count = sum(len(value) for value in missing_batch_ids_by_table.values())
        blockers = [
            *[f"{table}:missing_table" for table in missing_tables],
            *[f"{table}:empty_table" for table in empty_tables],
            *invalid_table_shapes,
        ]
        if template_marker_count:
            blockers.append("template_or_todo_markers_present")
        if required_field_gap_count:
            blockers.append("required_fields_missing_or_empty")
        if matched_batch_count < minimum_batches:
            blockers.append("minimum_matched_batch_count_not_met")

        ready = not blockers
        alignment_patch_plan = self._field_path_endpoint_alignment_patch_plan(
            required_tables=required_tables,
            batch_tables=batch_tables,
            table_row_counts=table_row_counts,
            table_batch_counts=table_batch_counts,
            missing_batch_ids_by_table=missing_batch_ids_by_table,
            batch_alignment_gap_count=batch_alignment_gap_count,
            matched_batch_count=matched_batch_count,
            minimum_batches=minimum_batches,
            blockers=blockers,
        )
        return {
            "preflight_status": (
                "field_path_endpoint_label_package_ready_for_field_layout_holdout"
                if ready
                else "field_path_endpoint_label_package_blocked_by_preflight"
            ),
            "required_tables": required_tables,
            "missing_tables": missing_tables,
            "empty_tables": empty_tables,
            "invalid_table_shapes": invalid_table_shapes,
            "required_field_gaps": required_field_gaps[:20],
            "required_field_gap_count": required_field_gap_count,
            "template_marker_count": template_marker_count,
            "table_row_counts": table_row_counts,
            "table_batch_counts": table_batch_counts,
            "batch_alignment_gap_count": batch_alignment_gap_count,
            "required_matched_batch_deficit": alignment_patch_plan["required_matched_batch_deficit"],
            "missing_batch_ids_by_table": {
                table: batch_ids[:20]
                for table, batch_ids in missing_batch_ids_by_table.items()
            },
            "alignment_patch_plan": alignment_patch_plan,
            "matched_batch_count": matched_batch_count,
            "minimum_matched_batch_count": minimum_batches,
            "accepted_batch_ids": sorted(matched_batches) if ready else [],
            "blockers": blockers,
            "can_route_to_field_layout_holdout": ready,
            "next_operator_action": (
                "run_field_layout_holdout_with_accepted_path_endpoint_labels"
                if ready
                else "fix_field_path_endpoint_label_package_preflight_blockers"
            ),
            "field_boundary": (
                "accepted package rows can route to field layout holdout only; they still require replay, "
                "operator review and release-gate validation before field-supported control claims"
            )
            if ready
            else "blocked package rows cannot be treated as field path or endpoint evidence",
        }

    @staticmethod
    def _field_path_endpoint_batch_universe(
        batch_sets: dict[str, set[str]],
        batch_tables: list[str],
    ) -> set[str]:
        batch_universe: set[str] = set()
        for table in batch_tables:
            batch_universe.update(batch_sets.get(table, set()))
        return batch_universe

    @staticmethod
    def _field_path_endpoint_alignment_patch_plan(
        *,
        required_tables: list[str],
        batch_tables: list[str],
        table_row_counts: dict[str, int],
        table_batch_counts: dict[str, int],
        missing_batch_ids_by_table: dict[str, list[str]],
        batch_alignment_gap_count: int,
        matched_batch_count: int,
        minimum_batches: int,
        blockers: list[str],
    ) -> dict[str, object]:
        required_matched_batch_deficit = max(0, minimum_batches - matched_batch_count)
        patch_items: list[dict[str, object]] = []
        for table in required_tables:
            if table_row_counts.get(table, 0) == 0:
                patch_items.append(
                    {
                        "item_id": f"R8U76_{table.upper()}_ROWS_REQUIRED",
                        "priority": "P1" if table in batch_tables else "P2",
                        "target_table": table,
                        "action": "add_real_field_rows",
                        "minimum_rows_hint": minimum_batches if table in batch_tables else 1,
                        "acceptance": (
                            f"{table} has non-template rows with all required fields; "
                            "rows must keep data_origin/provenance outside synthetic/template evidence."
                        ),
                    }
                )
        for table, missing_batches in sorted(missing_batch_ids_by_table.items()):
            patch_items.append(
                {
                    "item_id": f"R8U76_{table.upper()}_BATCH_ALIGNMENT",
                    "priority": "P1",
                    "target_table": table,
                    "action": "add_or_relabel_rows_for_missing_batch_ids",
                    "missing_batch_ids_sample": missing_batches[:20],
                    "missing_batch_id_count": len(missing_batches),
                    "acceptance": (
                        f"{table} contains rows for the same batch_id set used by node sensors, path labels, "
                        "endpoint labels, operation logs and lab results."
                    ),
                }
            )
        if required_matched_batch_deficit:
            patch_items.append(
                {
                    "item_id": "R8U76_MINIMUM_MATCHED_BATCH_DEFICIT",
                    "priority": "P1",
                    "target_table": "cross_table_batch_alignment",
                    "action": "collect_same_batch_bundle_across_path_endpoint_tables",
                    "required_matched_batch_deficit": required_matched_batch_deficit,
                    "acceptance": (
                        f"matched_batch_count >= {minimum_batches} across "
                        f"{', '.join(batch_tables)}."
                    ),
                }
            )
        status = "field_path_endpoint_alignment_ready"
        if blockers:
            status = "field_path_endpoint_alignment_blocked_by_preflight"
        elif batch_alignment_gap_count:
            status = "field_path_endpoint_alignment_needs_batch_linkage"
        return {
            "patch_plan_id": "R8u76_field_path_endpoint_batch_alignment_patch_plan",
            "patch_plan_status": status,
            "required_tables": required_tables,
            "batch_alignment_tables": batch_tables,
            "table_row_counts": table_row_counts,
            "table_batch_counts": table_batch_counts,
            "matched_batch_count": matched_batch_count,
            "minimum_matched_batch_count": minimum_batches,
            "required_matched_batch_deficit": required_matched_batch_deficit,
            "batch_alignment_gap_count": batch_alignment_gap_count,
            "item_count": len(patch_items),
            "items": patch_items,
            "field_boundary": (
                "This patch plan only describes how to collect or align field package rows. It does not create "
                "field evidence, does not validate control performance, and cannot authorize actuator or release "
                "gate writeback."
            ),
        }

    @staticmethod
    def _has_template_marker(row: dict[str, object]) -> bool:
        for key, value in row.items():
            key_text = str(key).lower()
            value_text = str(value).lower()
            if key_text == "template_only" and bool(value):
                return True
            if value_text.startswith("todo") or "template_not_" in value_text or "sample_not_" in value_text:
                return True
        return False

    def _hydraulic_path_feature_contract(self) -> dict[str, object]:
        sparse_contract = self.sparse_placement_metrics.get("hydraulic_path_coverage_contract", {})
        sparse_contract = sparse_contract if isinstance(sparse_contract, dict) else {}
        interface_contract = self.sensor_layout_interface.get("hydraulic_path_contract", {})
        interface_contract = interface_contract if isinstance(interface_contract, dict) else {}
        source_contract = sparse_contract or interface_contract
        stage_rows = source_contract.get("path_stage_rows", []) if isinstance(source_contract, dict) else []
        stage_rows = stage_rows if isinstance(stage_rows, list) else []
        feature_terms = [
            *HYDRAULIC_PATH_FEATURE_COLUMNS,
        ]
        field_schema_terms = [
            "path_stage_id",
            "hydraulic_path_role",
            "stage_coverage_mask",
            "direct_path_stage_coverage_mask",
            "proxy_path_stage_coverage_mask",
            "release_boundary_flag",
            "recirculation_loop_flag",
            "low_frequency_time_buffer_flag",
        ]
        status = str(source_contract.get("contract_status", "missing_hydraulic_path_contract"))
        source = "missing"
        if sparse_contract:
            source = "Agent48.hydraulic_path_coverage_contract"
        elif interface_contract:
            source = "Agent48.soft_sensor_interface.hydraulic_path_contract"
        final_release_needs_label = bool(source_contract.get("final_release_gate_needs_effluent_label", True))
        recirculation_loop_observed = bool(source_contract.get("recirculation_loop_observed", False))
        low_frequency_buffer_observed = bool(source_contract.get("low_frequency_time_buffer_observed", False))
        covered_stage_count = int(source_contract.get("covered_stage_count", 0) or 0)
        path_stage_count = int(source_contract.get("path_stage_count", len(stage_rows)) or len(stage_rows) or 0)
        release_rows = [
            row for row in stage_rows
            if isinstance(row, dict) and str(row.get("stage_id", "")) == "S5_release_boundary"
        ]
        release_boundary_direct = bool(release_rows and release_rows[0].get("direct_zone_covered", False))
        return {
            "contract_id": "R8u63_hydraulic_path_aware_soft_sensor_contract",
            "source": source,
            "contract_status": status,
            "path_id": str(source_contract.get("path_id", "missing_path_id")),
            "path_stage_count": path_stage_count,
            "covered_stage_count": covered_stage_count,
            "stage_rows_available": len(stage_rows),
            "feature_terms": feature_terms,
            "field_schema_terms": field_schema_terms,
            "recirculation_loop_observed": recirculation_loop_observed,
            "low_frequency_time_buffer_observed": low_frequency_buffer_observed,
            "final_release_gate_needs_effluent_label": final_release_needs_label,
            "release_boundary_directly_observed": release_boundary_direct,
            "can_support_soft_sensor_path_prior": bool(source_contract.get("can_support_soft_sensor_path_prior", False)),
            "can_support_control_replay_design_prior": bool(
                source_contract.get("can_support_control_replay_design_prior", False)
            ),
            "can_use_for_release_gate": False,
            "field_validation_required": True,
            "field_required_tables": [
                str(item)
                for item in (
                    source_contract.get("field_package_contract", {}).get("required_tables", [])
                    if isinstance(source_contract.get("field_package_contract", {}), dict)
                    else []
                )
            ],
            "unresolved_requirements": [
                str(item)
                for item in source_contract.get("unresolved_requirements", [])
            ]
            if isinstance(source_contract.get("unresolved_requirements", []), list)
            else [],
            "failure_boundary": (
                "numeric hydraulic path features can annotate soft-sensor models with process-stage context, while "
                "field schema terms preserve the human-readable stage labels; neither can convert polishing proxy "
                "coverage into final effluent release support without field topology, path labels and endpoint labels."
            ),
        }

    def _pressure_headloss_candidate_contract(self) -> dict[str, object]:
        r2_base_layout = self.observation_contract_metrics.get("base_layout_contract", {})
        r2_base_layout = r2_base_layout if isinstance(r2_base_layout, dict) else {}
        r2_readiness = self.observation_contract_metrics.get("readiness", {})
        r2_readiness = r2_readiness if isinstance(r2_readiness, dict) else {}
        hidden_ledger = self.sparse_placement_metrics.get("hidden_state_requirement_ledger", {})
        hidden_ledger = hidden_ledger if isinstance(hidden_ledger, dict) else {}
        sparse_pool = hidden_ledger.get("pressure_headloss_candidate_pool", {})
        sparse_pool = sparse_pool if isinstance(sparse_pool, dict) else {}
        sparse_field_contract = sparse_pool.get("field_package_contract", {})
        sparse_field_contract = sparse_field_contract if isinstance(sparse_field_contract, dict) else {}
        r2_field_contract = r2_base_layout.get("pressure_headloss_field_package_contract", {})
        r2_field_contract = r2_field_contract if isinstance(r2_field_contract, dict) else {}
        r2_candidate_ids = [
            str(item)
            for item in r2_base_layout.get(
                "pressure_headloss_candidate_ids",
                r2_readiness.get("agent48_pressure_headloss_candidate_ids", []),
            )
            if item
        ]
        sparse_candidate_ids = [str(item) for item in sparse_pool.get("candidate_ids", []) if item]
        candidate_ids = r2_candidate_ids or sparse_candidate_ids
        field_contract = r2_field_contract or sparse_field_contract
        status = str(
            r2_base_layout.get(
                "pressure_headloss_candidate_pool_status",
                r2_readiness.get(
                    "agent48_pressure_headloss_candidate_pool_status",
                    sparse_pool.get("pool_status", "missing_pressure_headloss_pool"),
                ),
            )
        )
        source = "missing"
        if r2_candidate_ids:
            source = "R2.observation_contract.base_layout"
        elif sparse_candidate_ids:
            source = "Agent48.hidden_state_requirement_ledger"
        required_tables = field_contract.get("required_tables", []) if isinstance(field_contract, dict) else []
        minimum_batches = int(field_contract.get("minimum_matched_batch_count", 3) or 3) if isinstance(field_contract, dict) else 3
        return {
            "contract_id": "R8c_pressure_headloss_candidate_soft_sensor_contract",
            "source": source,
            "pool_status": status,
            "candidate_count": len(candidate_ids),
            "candidate_ids": candidate_ids,
            "candidate_feature_terms": [
                "pressure_drop_kPa",
                "headloss_kPa_per_m",
                "flow_normalized_pressure_residual",
            ]
            if candidate_ids
            else [],
            "field_required_tables": [str(item) for item in required_tables],
            "minimum_matched_batch_count": minimum_batches,
            "soft_sensor_use": (
                "optional_candidate_feature_channel_for_catalyst_activity_and_hydraulic_state_only"
                if candidate_ids
                else "not_available"
            ),
            "field_validation_required": bool(candidate_ids),
            "can_use_as_installed_sensor": False,
            "can_write_to_release_gate": False,
            "failure_boundary": (
                "pressure/headloss candidates can shape the soft-sensor schema and missingness stress plan, "
                "but cannot be interpreted as field evidence until topology, bed geometry, matched lab labels "
                "and operation logs are imported."
            ),
        }

    def _missingness_stress_tests(self, contract: dict[str, object]) -> list[dict[str, object]]:
        node_count = int(contract.get("node_count", 0))
        modality_count = int(contract.get("modality_count", 0))
        total_cells = max(1, node_count * modality_count)
        coverage = contract.get("coverage_for_soft_sensor", {})
        coverage = coverage if isinstance(coverage, dict) else {}
        weak_state = float(coverage.get("weak_state_coverage", 0.0))
        reconstruction_gain = float(coverage.get("soft_sensor_reconstruction_gain", 0.0))
        catalyst_obs = float(coverage.get("catalyst_activity_observability", 0.0))
        matrix_obs = float(coverage.get("matrix_interference_observability", 0.0))
        scenarios = [
            {
                "scenario_id": "full_layout_available",
                "missing_cells": 0,
                "critical_target": "all_states",
                "fallback": "direct_node_modality_values",
            },
            {
                "scenario_id": "catalyst_bed_uv254_orp_missing",
                "missing_cells": max(1, min(total_cells, 2)),
                "critical_target": "catalyst_activity",
                "fallback": "pressure_drop_regeneration_response_and_grey_box_rate_residual",
            },
            {
                "scenario_id": "recycle_loop_flow_delay",
                "missing_cells": max(1, min(total_cells, node_count // 2)),
                "critical_target": "hydraulic_confidence",
                "fallback": "time_since_last_observed_and_loop_hold_time_prior",
            },
            {
                "scenario_id": "matrix_shock_ec_turbidity_sparse",
                "missing_cells": max(1, min(total_cells, 3)),
                "critical_target": "matrix_interference",
                "fallback": "uv254_ph_orp_proxy_and_fast_proxy_event_log",
            },
        ]
        rows: list[dict[str, object]] = []
        for scenario in scenarios:
            missing_fraction = float(scenario["missing_cells"]) / total_cells
            if scenario["critical_target"] == "catalyst_activity":
                target_support = catalyst_obs
            elif scenario["critical_target"] == "matrix_interference":
                target_support = matrix_obs
            elif scenario["critical_target"] == "hydraulic_confidence":
                target_support = float(coverage.get("hydraulic_observability", 0.0))
            else:
                target_support = min(1.0, 0.55 + 0.45 * reconstruction_gain)
            grey_bonus = 0.06 if contract.get("grey_box_prior_available") else 0.0
            robustness = max(0.0, min(1.0, 0.52 * target_support + 0.30 * reconstruction_gain + 0.12 * weak_state + grey_bonus - 0.42 * missing_fraction))
            rows.append(
                {
                    **scenario,
                    "missing_fraction": round(missing_fraction, 3),
                    "target_support_score": round(target_support, 3),
                    "layout_reconstruction_gain": round(reconstruction_gain, 3),
                    "estimated_masked_state_support": round(robustness, 3),
                    "field_validation_boundary": "synthetic mask stress only; must replay field missingness, fouling, delay and maintenance events",
                }
            )
        return rows

    def _readiness(self, contract: dict[str, object], stress_tests: list[dict[str, object]]) -> dict[str, object]:
        layout_fields_present = sum(1 for field in REQUIRED_LAYOUT_FIELDS if self.sensor_layout_interface.get(field)) / len(REQUIRED_LAYOUT_FIELDS)
        mask_shape = contract.get("mask_shape", [])
        expected_shape = [contract.get("node_count", 0), contract.get("modality_count", 0)]
        mask_shape_ok = list(mask_shape) == expected_shape and all(int(value) > 0 for value in expected_shape)
        training_gap = self._training_schema_gap(contract)
        layout_holdout = self.soft_sensor_training_metrics.get("layout_holdout", {})
        layout_holdout = layout_holdout if isinstance(layout_holdout, dict) else {}
        layout_holdout_status = str(layout_holdout.get("status", "missing_layout_holdout_metrics"))
        layout_holdout_ready = layout_holdout_status.startswith("synthetic_layout_holdout_ready")
        path_endpoint_preflight = contract.get("field_path_endpoint_label_package_preflight", {})
        path_endpoint_preflight = path_endpoint_preflight if isinstance(path_endpoint_preflight, dict) else {}
        path_endpoint_package_ready = bool(path_endpoint_preflight.get("can_route_to_field_layout_holdout", False))
        path_endpoint_preflight_status = str(
            path_endpoint_preflight.get("preflight_status", "missing_field_path_endpoint_label_package_preflight")
        )
        path_feature_variation_status = str(
            self.soft_sensor_training_metrics.get("hydraulic_path_feature_variation_status", "missing_path_feature_variation_metrics")
        )
        path_feature_variation_ready = path_feature_variation_status == "synthetic_path_feature_variation_ready_for_layout_holdout"
        stress_scores = [float(item["estimated_masked_state_support"]) for item in stress_tests]
        robustness = sum(stress_scores) / max(1, len(stress_scores))
        live_context_status = str(self.soft_sensor_layout_context.get("layout_status", "not_available"))
        live_context_connected = live_context_status != "not_available"
        field_ready = self.data_origin == "field_layout_missingness" and path_endpoint_package_ready
        pressure_contract = contract.get("pressure_headloss_candidate_contract", {})
        pressure_contract = pressure_contract if isinstance(pressure_contract, dict) else {}
        pressure_candidate_count = int(pressure_contract.get("candidate_count", 0) or 0)
        pressure_schema_ready = bool(training_gap.get("current_model_pressure_headloss_ready", False))
        path_contract = contract.get("hydraulic_path_feature_contract", {})
        path_contract = path_contract if isinstance(path_contract, dict) else {}
        path_terms = path_contract.get("feature_terms", []) if isinstance(path_contract.get("feature_terms", []), list) else []
        path_contract_available = path_contract.get("source") != "missing"
        path_schema_ready = bool(training_gap.get("current_model_hydraulic_path_ready", False))
        score = round(
            0.28 * layout_fields_present
            + 0.18 * float(mask_shape_ok)
            + 0.24 * robustness
            + 0.12 * float(live_context_connected)
            + 0.10 * float(bool(contract.get("grey_box_prior_available")))
            + 0.08 * float(field_ready),
            3,
        )
        if field_ready and robustness >= 0.72:
            status = "field_layout_aware_soft_sensor_candidate_ready"
        elif layout_fields_present >= 0.95 and mask_shape_ok and live_context_connected:
            status = "synthetic_layout_aware_soft_sensor_contract_ready_needs_field_missingness"
        else:
            status = "soft_sensor_matrix_contract_incomplete"
        return {
            "soft_sensor_matrix_status": status,
            "soft_sensor_matrix_score": score,
            "layout_contract_score": round(layout_fields_present, 3),
            "mask_shape_ok": mask_shape_ok,
            "missingness_robustness_score": round(robustness, 3),
            "live_layout_context_status": live_context_status,
            "current_model_layout_aware": training_gap["current_model_layout_aware"],
            "field_ready": field_ready,
            "can_update_soft_sensor_training_schema": status.startswith(("synthetic_", "field_")),
            "pressure_headloss_candidate_pool_status": str(pressure_contract.get("pool_status", "missing_pressure_headloss_pool")),
            "pressure_headloss_candidate_count": pressure_candidate_count,
            "pressure_headloss_candidate_ids": pressure_contract.get("candidate_ids", []),
            "pressure_headloss_schema_ready": pressure_schema_ready,
            "can_update_pressure_headloss_candidate_schema": pressure_candidate_count > 0,
            "can_use_pressure_headloss_for_field_claim": False,
            "hydraulic_path_contract_status": str(path_contract.get("contract_status", "missing_hydraulic_path_contract")),
            "hydraulic_path_feature_term_count": len(path_terms),
            "hydraulic_path_stage_count": int(path_contract.get("path_stage_count", 0) or 0),
            "hydraulic_path_covered_stage_count": int(path_contract.get("covered_stage_count", 0) or 0),
            "hydraulic_path_schema_ready": path_schema_ready,
            "hydraulic_path_feature_variation_status": path_feature_variation_status,
            "hydraulic_path_feature_variation_ready": path_feature_variation_ready,
            "layout_holdout_status": layout_holdout_status,
            "layout_holdout_ready": layout_holdout_ready,
            "layout_holdout_mean_mae": layout_holdout.get("mean_mae"),
            "layout_holdout_train_layout_count": len(layout_holdout.get("train_layout_ids", []) or []),
            "layout_holdout_heldout_layout_count": len(layout_holdout.get("holdout_layout_ids", []) or []),
            "layout_holdout_field_boundary": layout_holdout.get("field_boundary", ""),
            "field_path_endpoint_label_package_status": path_endpoint_preflight_status,
            "field_path_endpoint_label_package_ready": path_endpoint_package_ready,
            "field_path_endpoint_label_matched_batch_count": path_endpoint_preflight.get("matched_batch_count", 0),
            "field_path_endpoint_label_minimum_matched_batch_count": path_endpoint_preflight.get(
                "minimum_matched_batch_count", 5
            ),
            "field_path_endpoint_label_missing_tables": path_endpoint_preflight.get("missing_tables", []),
            "field_path_endpoint_label_preflight_blockers": path_endpoint_preflight.get("blockers", []),
            "can_route_to_field_layout_holdout": path_endpoint_package_ready,
            "hydraulic_path_final_release_gate_needs_effluent_label": bool(
                path_contract.get("final_release_gate_needs_effluent_label", True)
            ),
            "hydraulic_path_release_boundary_directly_observed": bool(
                path_contract.get("release_boundary_directly_observed", False)
            ),
            "can_update_hydraulic_path_feature_schema": bool(path_contract_available),
            "can_use_hydraulic_path_for_release_gate": False,
            "can_update_live_soft_sensor_inference_context": live_context_connected,
            "can_write_to_release_gate": False,
            "next_recommended_core_action": (
                "R8u63_add_hydraulic_path_terms_to_soft_sensor_training_schema"
                if path_contract_available and not path_schema_ready
                else "R8u65_add_synthetic_layout_holdout_for_path_features"
                if path_schema_ready and not layout_holdout_ready
                else "R8u66_collect_field_path_endpoint_labels_for_layout_holdout"
                if path_schema_ready and layout_holdout_ready and not path_endpoint_package_ready
                else "R8u67_run_field_layout_holdout_with_accepted_path_endpoint_labels"
                if path_schema_ready and layout_holdout_ready and path_endpoint_package_ready
                else "R8c_agent49_consume_pressure_headloss_control_boundary"
                if pressure_candidate_count > 0
                else "P7_engineering_constraints_in_reward_and_arbitration"
            ),
        }

    def _training_schema_gap(self, contract: dict[str, object]) -> dict[str, object]:
        training_features = self.soft_sensor_training_metrics.get("features", FEATURE_COLUMNS)
        if not isinstance(training_features, list):
            training_features = FEATURE_COLUMNS
        required_terms = ("layout_id", "node_id", "zone", "modality", "availability_mask", "time_since_last_observed_min")
        missing_terms = [term for term in required_terms if term not in training_features]
        pressure_contract = contract.get("pressure_headloss_candidate_contract", {})
        pressure_contract = pressure_contract if isinstance(pressure_contract, dict) else {}
        pressure_terms = [
            str(term)
            for term in pressure_contract.get("candidate_feature_terms", [])
            if str(term)
        ]
        missing_pressure_terms = [term for term in pressure_terms if term not in training_features]
        path_contract = contract.get("hydraulic_path_feature_contract", {})
        path_contract = path_contract if isinstance(path_contract, dict) else {}
        path_terms = [
            str(term)
            for term in path_contract.get("feature_terms", [])
            if str(term)
        ]
        missing_path_terms = [term for term in path_terms if term not in training_features]
        field_blockers = [
            "node_specific_sensor_values_missing",
            "field_missingness_reason_labels_missing",
            "layout_id_holdout_split_missing",
        ]
        if pressure_terms:
            field_blockers.extend(
                [
                    "pressure_headloss_field_topology_missing",
                    "pressure_headloss_matched_lab_labels_missing",
                ]
            )
        if path_terms:
            field_blockers.extend(
                [
                    "hydraulic_path_stage_labels_missing",
                    "final_effluent_release_endpoint_labels_missing",
                ]
            )
        if contract.get("grey_box_prior_available"):
            missing_terms.append("grey_box_residual_prior")
        return {
            "training_features": training_features,
            "required_layout_terms": list(required_terms),
            "missing_layout_terms": missing_terms,
            "pressure_headloss_candidate_terms": pressure_terms,
            "missing_pressure_headloss_terms": missing_pressure_terms,
            "hydraulic_path_feature_terms": path_terms,
            "missing_hydraulic_path_terms": missing_path_terms,
            "current_model_layout_aware": not missing_terms,
            "current_model_pressure_headloss_ready": bool(pressure_terms) and not missing_pressure_terms,
            "current_model_hydraulic_path_ready": bool(path_terms) and not missing_path_terms,
            "field_blockers": field_blockers,
        }

    def _issues(self, readiness: dict[str, object]) -> list[QualityIssue]:
        issues: list[QualityIssue] = []
        if not readiness["current_model_layout_aware"]:
            issues.append(
                QualityIssue(
                    sensor="soft_sensor_training_schema",
                    issue_type="soft_sensor_layout_features_missing",
                    severity=Severity.WARNING,
                    message="当前软传感训练特征仍不是 layout-aware，缺 node/zone/modality/mask/layout_id 等字段。",
                    evidence=readiness,
                )
            )
        if readiness["live_layout_context_status"] == "global_modality_fallback_used_for_layout":
            issues.append(
                QualityIssue(
                    sensor="soft_sensor_inference_schema",
                    issue_type="node_specific_values_missing",
                    severity=Severity.WARNING,
                    message="推理链已接入 layout_id 和 mask，但当前读数仍使用全局 modality fallback，缺节点级真实值。",
                    evidence=readiness,
                )
            )
        if not readiness["field_ready"]:
            issues.append(
                QualityIssue(
                    sensor="soft_sensor_matrix_coupling",
                    issue_type="field_missingness_replay_required",
                    severity=Severity.INFO,
                    message="P5 当前只能形成 synthetic layout contract，需要真实缺测、污染、延迟和维护事件 replay 才能校准。",
                    evidence=readiness,
                )
            )
        if readiness["pressure_headloss_candidate_count"] and not readiness["pressure_headloss_schema_ready"]:
            issues.append(
                QualityIssue(
                    sensor="soft_sensor_matrix_coupling",
                    issue_type="pressure_headloss_candidate_schema_not_trained",
                    severity=Severity.INFO,
                    message="Agent54 已读取 pressure/headloss 候选池，但当前软传感训练 schema 尚未包含这些候选特征；只能作为下一轮候选通道。",
                    evidence=readiness,
                )
            )
        if readiness["can_update_hydraulic_path_feature_schema"] and not readiness["hydraulic_path_schema_ready"]:
            issues.append(
                QualityIssue(
                    sensor="soft_sensor_matrix_coupling",
                    issue_type="hydraulic_path_feature_schema_not_trained",
                    severity=Severity.INFO,
                    message="Agent54 已读取 Agent48 的水力路径覆盖合同，但当前软传感训练 schema 尚未包含 path_stage/release/loop 特征；只能作为下一轮路径感知通道。",
                    evidence=readiness,
                )
            )
        if readiness["hydraulic_path_final_release_gate_needs_effluent_label"]:
            issues.append(
                QualityIssue(
                    sensor="soft_sensor_matrix_coupling",
                    issue_type="hydraulic_path_release_endpoint_blocks_release_use",
                    severity=Severity.WARNING,
                    message="当前软传感路径先验仍缺最终 effluent 放行端点标签，不能把 polishing 代理观察用于 release gate。",
                    evidence=readiness,
                )
            )
        if readiness.get("layout_holdout_ready", False) and not readiness.get("field_path_endpoint_label_package_ready", False):
            issues.append(
                QualityIssue(
                    sensor="field_path_endpoint_label_package",
                    issue_type="field_path_endpoint_label_package_required_for_field_holdout",
                    severity=Severity.WARNING,
                    message="已有 synthetic layout holdout，但缺真实 path_stage/endpoint/node-specific field rows，不能升级为 field layout holdout。",
                    evidence=readiness,
                )
            )
        return issues

    @staticmethod
    def _recommendations(readiness: dict[str, object]) -> list[str]:
        recs = [
            "把 Agent48 的 layout_id、node_id、zone、modality、availability_mask 和 time_since_last_observed_min 写入软传感训练/推理 schema。",
            "训练阶段按 layout_id 做 holdout，防止模型只记住某个 synthetic 布点而不能泛化到现场布点变化。",
            "将 Agent53 的 grey_box_residual_prior 作为可选 feature channel，但 field 物理校准前只能作为先验，不得写 release gate。",
            "下一轮应把工程执行约束写入 Agent49 reward 和最终仲裁，尤其是泵阀动作次数、池容、药剂库存和人工复核时间。",
        ]
        if readiness.get("pressure_headloss_candidate_count", 0):
            recs.append(
                "把 pressure_drop/headloss/flow-normalized residual 作为催化剂活性和水力状态的候选软传感通道，但必须等待现场床层几何、压降记录和 lab label 匹配后才能形成性能 claim。"
            )
        if readiness.get("can_update_hydraulic_path_feature_schema", False):
            if readiness.get("hydraulic_path_schema_ready", False):
                if readiness.get("layout_holdout_ready", False):
                    if readiness.get("field_path_endpoint_label_package_ready", False):
                        recs.append(
                            "真实 path/endpoint label package 已通过 preflight；下一步只能进入 field layout holdout/replay，仍不得直接写 release gate 或 actuator。"
                        )
                    else:
                        recs.append(
                            "软传感训练特征已接入数值化水力路径字段，并已形成 synthetic layout holdout；下一步应提交真实 "
                            "path_stage/endpoint labels、node-specific field values 和 final effluent 端点标签包，通过 R8u66 preflight 后再进入 field layout holdout。"
                        )
                else:
                    recs.append(
                        "软传感训练特征已接入数值化水力路径字段；下一步应形成 layout holdout，再补真实 path_stage/endpoint labels "
                        "和 final effluent 端点标签，验证这些路径特征是否真的提升状态估计。"
                    )
            else:
                recs.append(
                    "把数值化 path-stage 特征写入软传感训练 schema，同时在现场表保留 path_stage_id、"
                    "hydraulic_path_role、release_boundary_flag 和 recirculation_loop_flag；final effluent 标签补齐前仍不得写 release gate。"
                )
        return recs

    @staticmethod
    def _method_contract() -> dict[str, object]:
        return {
            "upgrade_id": "P5_soft_sensor_node_modality_missingness",
            "borrowed_from": [
                "GRU-D-style use of missingness masks and time gaps as signals",
                "BRITS-style bidirectional imputation framing for multivariate time series",
                "scikit-learn native missing-value handling in histogram gradient boosting as a lightweight tabular option",
                "PySensors-style sparse sensor placement/reconstruction interface from Agent48",
                "pressure/headloss proxy channel for weak catalyst and hydraulic-state observability from R8b",
                "hydraulic path coverage contract from Agent48 for process-stage-aware feature annotation",
            ],
            "reality_mapping": "把低成本传感从全局列升级为 node-zone-modality-time-path 张量，并把缺失、延迟、低频采样和循环路径阶段作为状态估计证据。",
            "data_needs": FIELD_SCHEMA_PATCH,
            "implementation_path": [
                "src/water_ai/agents/soft_sensor_agent.py",
                "src/water_ai/agents/soft_sensor_matrix_coupling_agent.py",
                "experiments/run_agent54_soft_sensor_matrix_coupling.py",
            ],
            "evaluation_metrics": [
                "layout_contract_score",
                "missingness_robustness_score",
                "masked_state_support",
                "node_specific_value_rate",
                "layout_holdout_masked_mae",
                "hydraulic_path_covered_stage_count",
                "hydraulic_path_release_endpoint_label_completion",
            ],
            "failure_boundary": "synthetic mask stress only proves schema and interface; field missingness and layout holdout are required before release-gate claims.",
        }

    @staticmethod
    def _agent50_writeback(readiness: dict[str, object]) -> dict[str, object]:
        return {
            "allowed_writeback": [
                "soft_sensor_training_schema_patch",
                "soft_sensor_inference_layout_context",
                "hydraulic_path_feature_schema_patch",
                "field_path_endpoint_label_package_preflight",
                "P5_completion_status_for_governance",
            ],
            "blocked_writeback": [
                "release_gate_policy",
                "field_missingness_claim",
                "layout_holdout_performance_claim",
                "field_layout_holdout_performance_claim_without_accepted_package",
            ],
            "can_advance_governance_priority": bool(readiness["can_update_soft_sensor_training_schema"]),
            "policy_effect": (
                "move_to_P7_engineering_constraints_in_reward_and_arbitration"
                if readiness["can_update_soft_sensor_training_schema"]
                else "keep_P5_until_layout_contract_is_complete"
            ),
        }


def build_field_path_endpoint_label_package_contract() -> dict[str, object]:
    """Public R8u66 contract used by Agent54 and R7 real-field package gates."""

    return SoftSensorMatrixCouplingAgent._field_path_endpoint_label_package_contract()


def preflight_field_path_endpoint_label_package(
    package: dict[str, object] | None,
    *,
    contract: dict[str, object] | None = None,
) -> dict[str, object]:
    """Validate field path-stage and final-effluent endpoint labels for layout holdout routing."""

    agent = SoftSensorMatrixCouplingAgent(field_path_label_package=package or {})
    return agent._field_path_endpoint_label_package_preflight(
        contract or build_field_path_endpoint_label_package_contract()
    )

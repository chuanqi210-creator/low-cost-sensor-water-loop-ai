from __future__ import annotations

from collections.abc import Sequence

from water_ai.agents.base import BaseAgent
from water_ai.domain import AgentReport, QualityIssue, SensorReading, Severity


PRESSURE_RESOLUTION_SCENARIOS = [
    {
        "scenario_id": "R8O_S1_unresolved_pressure_conflict_review_block",
        "scenario_type": "unresolved_conflict_review_block",
        "purpose": "证明 node pressure 与 pressure/headloss event 冲突未复核时，Agent51/49/52 必须保持阻断。",
        "acceptance_metrics": [
            "unresolved_pressure_source_conflict_count",
            "pressure_source_conflict_requires_operator_review",
            "pressure_source_conflict_control_block",
            "pressure_source_conflict_replay_blocked_case_count",
        ],
    },
    {
        "scenario_id": "R8O_S2_resolved_pressure_conflict_authoritative_source",
        "scenario_type": "resolved_conflict_authoritative_source",
        "purpose": "证明 operator review 选择 authoritative pressure source 后，冲突 batch 可以被重新纳入 scoreability/replay。",
        "acceptance_metrics": [
            "resolved_pressure_source_conflict_count",
            "pressure_source_resolution_record_count",
            "authoritative_pressure_source",
            "calibration_action_id",
        ],
    },
    {
        "scenario_id": "R8O_S3_operator_review_latency_budget",
        "scenario_type": "operator_review_latency_budget",
        "purpose": "证明循环/暂存结构为人工复核和校准争取到足够时间，不要求高速在线传感。",
        "acceptance_metrics": [
            "operator_review_latency_min",
            "hold_or_recycle_time_budget_min",
            "latency_margin_min",
            "review_completed_before_release",
        ],
    },
    {
        "scenario_id": "R8O_S4_agent51_scoreability_recovery_after_resolution",
        "scenario_type": "agent51_scoreability_recovery",
        "purpose": "证明压力源复核后 Agent51 catalyst proxy holdout 的 scoreable batch 能恢复，而不是永久丢弃该批次。",
        "acceptance_metrics": [
            "agent51_scoreable_batch_count_before_resolution",
            "agent51_scoreable_batch_count_after_resolution",
            "scoreability_recovered_batch_count",
            "field_proxy_holdout_summary_status",
        ],
    },
    {
        "scenario_id": "R8O_S5_agent49_agent52_guardrail_clearance_replay",
        "scenario_type": "guardrail_clearance_replay",
        "purpose": "证明已解决压力冲突能通过 Agent49/52 replay clearance，但仍不能绕过 actuator/release gate 的人工复核边界。",
        "acceptance_metrics": [
            "agent49_pressure_conflict_guardrail_clear",
            "agent52_pressure_source_conflict_clear",
            "can_write_to_actuator",
            "can_write_to_release_gate",
        ],
    },
]


REQUIRED_TABLE_FIELDS = {
    "node_modality_sensor_timeseries": [
        "batch_id",
        "node_id",
        "modality",
        "value",
        "unit",
        "sample_time_min",
        "instrument_id",
        "sensor_status",
        "data_origin",
    ],
    "pressure_headloss_event_log": [
        "batch_id",
        "bed_id",
        "pressure_drop_kPa",
        "headloss_kPa_per_m",
        "flow_Lmin",
        "event_time_min",
        "matched_lab_sample_time_min",
        "hydraulic_anomaly_label",
        "instrument_id",
        "data_origin",
    ],
    "campaign_operation_log": [
        "batch_id",
        "action_id",
        "operator_review_required",
        "pressure_source_resolution",
        "authoritative_pressure_source",
        "reviewer_id",
        "review_time",
        "calibration_action_id",
        "calibration_note",
        "hold_time_min",
        "recycle_ratio",
        "data_origin",
    ],
    "offline_lab_results": [
        "batch_id",
        "sample_time_min",
        "lab_label_time_min",
        "analyte",
        "value",
        "unit",
        "method",
        "qa_flag",
        "data_origin",
    ],
    "fast_proxy_event_log": [
        "batch_id",
        "proxy_label_time_min",
        "proxy_event_type",
        "protective_triggered",
        "false_positive_cost_index",
        "data_origin",
    ],
}


AGENT52_REPLAY_REQUIRED_FIELDS = [
    "batch_id",
    "scenario",
    "policy_action_id",
    "expert_action_id",
    "pressure_source_conflict_count",
    "resolved_pressure_source_conflict_count",
    "unresolved_pressure_source_conflict_count",
    "pressure_source_resolution_record_count",
    "pressure_source_conflict_requires_operator_review",
    "pressure_source_conflict_control_block",
    "data_origin",
]


class PressureResolutionReplayScenarioPackAgent(BaseAgent):
    """Define field replay scenarios for pressure-source conflict resolution."""

    name = "pressure_resolution_replay_scenario_pack_agent"

    def __init__(
        self,
        *,
        r7_pipeline_metrics: dict[str, object] | None = None,
        catalyst_proxy_metrics: dict[str, object] | None = None,
        collaborative_control_metrics: dict[str, object] | None = None,
        replay_evaluation_metrics: dict[str, object] | None = None,
        field_replay_rows_by_table: dict[str, list[dict[str, object]]] | None = None,
        min_required_scenarios: int = 5,
    ) -> None:
        self.r7_pipeline_metrics = r7_pipeline_metrics or {}
        self.catalyst_proxy_metrics = catalyst_proxy_metrics or {}
        self.collaborative_control_metrics = collaborative_control_metrics or {}
        self.replay_evaluation_metrics = replay_evaluation_metrics or {}
        self.field_replay_rows_by_table = field_replay_rows_by_table or {}
        self.min_required_scenarios = min_required_scenarios

    def run(self, readings: Sequence[SensorReading]) -> AgentReport:
        del readings
        snapshot = self._source_snapshot()
        scenario_matrix = self._scenario_matrix(snapshot)
        row_collection_plan = self._row_collection_plan(scenario_matrix)
        field_row_acceptance = self._field_row_acceptance(row_collection_plan)
        scenario_matrix = self._scenario_matrix(snapshot, field_row_acceptance["scenario_evidence_counts"])
        row_collection_plan = self._row_collection_plan(scenario_matrix)
        template_rows_by_table = self._template_rows_by_table(row_collection_plan)
        readiness = self._readiness(scenario_matrix, field_row_acceptance)
        row_collection_readiness = self._row_collection_readiness(
            row_collection_plan,
            template_rows_by_table,
            field_row_acceptance,
        )
        issues = self._issues(scenario_matrix, readiness, field_row_acceptance)
        recommendations = self._recommendations(readiness, row_collection_readiness)
        summary = (
            f"pressure resolution replay 场景包：{readiness['scenario_pack_status']}；"
            f"schema={readiness['scenario_schema_coverage']:.3f}，"
            f"field={readiness['field_scenario_coverage']:.3f}。"
        )
        confidence = round(
            min(0.9, max(0.18, 0.32 + 0.42 * readiness["scenario_pack_score"] - 0.03 * len(issues))),
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
                "source_snapshot": snapshot,
                "required_table_field_matrix": REQUIRED_TABLE_FIELDS,
                "pressure_resolution_replay_scenario_matrix": scenario_matrix,
                "row_collection_plan": row_collection_plan,
                "template_rows_by_table": template_rows_by_table,
                "field_row_acceptance": field_row_acceptance,
                "row_collection_readiness": row_collection_readiness,
                "readiness": readiness,
                "agent60_writeback": self._agent60_writeback(readiness),
            },
        )

    @staticmethod
    def _method_contract() -> dict[str, object]:
        return {
            "contract_id": "R8o_pressure_resolution_field_replay_scenario_pack",
            "model_core_role": (
                "把压力源冲突解除门从字段/summary 层推进到真实 replay 场景层，验证循环暂存、人工复核、"
                "Agent51 scoreability 恢复和 Agent49/52 guardrail clearance。"
            ),
            "must_distinguish": [
                "raw pressure conflict",
                "unresolved pressure conflict",
                "resolved pressure conflict with authoritative source",
                "template clear state without real conflict rows",
                "field-supported replay clearance",
            ],
            "writeback_boundary": "scenario package only; no actuator or release-gate writeback.",
        }

    def _row_collection_plan(self, scenario_matrix: list[dict[str, object]]) -> list[dict[str, object]]:
        rows: list[dict[str, object]] = []
        for index, scenario in enumerate(scenario_matrix, start=1):
            scenario_id = str(scenario["scenario_id"])
            scenario_type = str(scenario["scenario_type"])
            evidence_ready = bool(scenario["field_evidence_ready"])
            rows.append(
                {
                    "collection_id": f"R8P_ROW_BUNDLE_{index:02d}",
                    "scenario_id": scenario_id,
                    "scenario_type": scenario_type,
                    "collection_status": "field_replay_rows_present" if evidence_ready else "field_replay_rows_required",
                    "batch_role": self._batch_role(scenario_type),
                    "minimum_real_batches": 1,
                    "required_tables": list(REQUIRED_TABLE_FIELDS),
                    "required_non_empty_fields_by_table": REQUIRED_TABLE_FIELDS,
                    "agent52_replay_required_fields": AGENT52_REPLAY_REQUIRED_FIELDS,
                    "cross_table_join_keys": [
                        "batch_id",
                        "node_modality_sensor_timeseries.sample_time_min <= pressure_headloss_event_log.event_time_min <= offline_lab_results.lab_label_time_min",
                        "campaign_operation_log.batch_id links pressure_source_resolution to the same batch",
                        "fast_proxy_event_log.batch_id links protective_triggered and false_positive_cost_index",
                    ],
                    "minimum_resolution_fields": [
                        "pressure_source_resolution",
                        "authoritative_pressure_source",
                        "reviewer_id",
                        "review_time",
                        "calibration_action_id",
                        "calibration_note",
                    ],
                    "acceptance_metrics": scenario["acceptance_metrics"],
                    "template_rows_are_field_evidence": False,
                    "cannot_write_to_actuator": True,
                    "cannot_write_to_release_gate": True,
                }
            )
        return rows

    @staticmethod
    def _batch_role(scenario_type: str) -> str:
        roles = {
            "unresolved_conflict_review_block": "BATCH_WITH_UNRESOLVED_PRESSURE_SOURCE_CONFLICT",
            "resolved_conflict_authoritative_source": "BATCH_WITH_RESOLVED_PRESSURE_SOURCE_CONFLICT",
            "operator_review_latency_budget": "BATCH_WITH_REVIEW_LATENCY_AND_HOLD_TIME",
            "agent51_scoreability_recovery": "BATCH_WITH_AGENT51_SCOREABILITY_RECOVERY_AFTER_RESOLUTION",
            "guardrail_clearance_replay": "BATCH_WITH_AGENT49_AGENT52_PRESSURE_GUARDRAIL_CLEARANCE",
        }
        return roles.get(scenario_type, "BATCH_WITH_PRESSURE_RESOLUTION_REPLAY")

    def _template_rows_by_table(self, row_collection_plan: list[dict[str, object]]) -> dict[str, list[dict[str, object]]]:
        templates: dict[str, list[dict[str, object]]] = {table: [] for table in REQUIRED_TABLE_FIELDS}
        templates["agent52_replay_table"] = []
        for plan in row_collection_plan:
            if plan["collection_status"] != "field_replay_rows_required":
                continue
            batch_id = f"TODO_{plan['batch_role']}"
            scenario_id = str(plan["scenario_id"])
            scenario_type = str(plan["scenario_type"])
            for table, fields in REQUIRED_TABLE_FIELDS.items():
                row = {field: self._placeholder_value(table, field, batch_id, scenario_type) for field in fields}
                row["scenario_id"] = scenario_id
                row["collection_id"] = plan["collection_id"]
                row["template_only"] = True
                row["evidence_status"] = "template_not_field_evidence"
                row["source_stage"] = "field_validation_required"
                templates[table].append(row)
            replay_row = {
                field: self._placeholder_replay_value(field, batch_id, scenario_type)
                for field in AGENT52_REPLAY_REQUIRED_FIELDS
            }
            replay_row["scenario_id"] = scenario_id
            replay_row["collection_id"] = plan["collection_id"]
            replay_row["template_only"] = True
            replay_row["evidence_status"] = "template_not_field_evidence"
            replay_row["source_stage"] = "field_validation_required"
            templates["agent52_replay_table"].append(replay_row)
        return templates

    @staticmethod
    def _placeholder_value(table: str, field: str, batch_id: str, scenario_type: str) -> object:
        if field == "batch_id":
            return batch_id
        if field in {"node_id", "bed_id"}:
            return "N3_catalyst_bed"
        if field == "modality":
            return "pressure_drop_kPa"
        if field == "unit":
            return "kPa" if "pressure" in table or field == "value" else "TODO_UNIT"
        if field in {"operator_review_required", "protective_triggered"}:
            return scenario_type == "unresolved_conflict_review_block"
        if field == "pressure_source_resolution":
            return "unresolved" if scenario_type == "unresolved_conflict_review_block" else "resolved"
        if field == "authoritative_pressure_source":
            return "TODO_node_modality_sensor_timeseries_or_pressure_headloss_event_log"
        if field in {"reviewer_id", "review_time", "calibration_action_id", "calibration_note"}:
            return f"TODO_{field}"
        if field in {"hold_time_min", "recycle_ratio", "flow_Lmin", "pressure_drop_kPa", "headloss_kPa_per_m", "value"}:
            return f"TODO_NUMERIC_{field}"
        if field.endswith("_time_min") or field in {"sample_time_min", "event_time_min"}:
            return f"TODO_TIME_{field}"
        return f"TODO_{field}"

    @staticmethod
    def _placeholder_replay_value(field: str, batch_id: str, scenario_type: str) -> object:
        if field == "batch_id":
            return batch_id
        if field == "scenario":
            return scenario_type
        if field == "data_origin":
            return "TODO_FIELD_REPLAY_NOT_EVIDENCE"
        if field == "pressure_source_conflict_count":
            return 1
        if field == "resolved_pressure_source_conflict_count":
            return 0 if scenario_type == "unresolved_conflict_review_block" else 1
        if field == "unresolved_pressure_source_conflict_count":
            return 1 if scenario_type == "unresolved_conflict_review_block" else 0
        if field == "pressure_source_resolution_record_count":
            return 0 if scenario_type == "unresolved_conflict_review_block" else 1
        if field in {"pressure_source_conflict_requires_operator_review", "pressure_source_conflict_control_block"}:
            return scenario_type == "unresolved_conflict_review_block"
        if field in {"policy_action_id", "expert_action_id"}:
            return "TODO_AGENT49_OR_OPERATOR_ACTION_ID"
        return f"TODO_{field}"

    @staticmethod
    def _row_collection_readiness(
        row_collection_plan: list[dict[str, object]],
        template_rows_by_table: dict[str, list[dict[str, object]]],
        field_row_acceptance: dict[str, object],
    ) -> dict[str, object]:
        missing = [
            row for row in row_collection_plan if row["collection_status"] == "field_replay_rows_required"
        ]
        ready = [
            row for row in row_collection_plan if row["collection_status"] == "field_replay_rows_present"
        ]
        template_row_count = sum(len(rows) for rows in template_rows_by_table.values())
        if not row_collection_plan:
            status = "row_collection_plan_missing"
        elif missing:
            status = "row_collection_plan_ready_needs_real_rows"
        else:
            status = "row_collection_plan_field_scenarios_ready"
        return {
            "row_collection_plan_status": status,
            "required_scenario_count": len(row_collection_plan),
            "missing_scenario_count": len(missing),
            "ready_scenario_count": len(ready),
            "minimum_real_batch_count": sum(int(row.get("minimum_real_batches", 0) or 0) for row in missing),
            "required_table_count": len(REQUIRED_TABLE_FIELDS),
            "template_table_count": len(template_rows_by_table),
            "template_row_count": template_row_count,
            "template_rows_are_field_evidence": False,
            "field_row_acceptance_status": field_row_acceptance["field_row_acceptance_status"],
            "accepted_field_scenario_count": field_row_acceptance["accepted_scenario_count"],
            "rejected_field_row_count": field_row_acceptance["rejected_field_row_count"],
            "template_warning": "TODO/template rows only describe required field structure and must never be imported as field evidence.",
            "can_update_agent60_fallback": bool(row_collection_plan),
            "can_write_to_actuator": False,
            "can_write_to_release_gate": False,
        }

    def _field_row_acceptance(self, row_collection_plan: list[dict[str, object]]) -> dict[str, object]:
        supplied_row_count = sum(len(rows) for rows in self.field_replay_rows_by_table.values())
        if not supplied_row_count:
            return {
                "field_row_acceptance_status": "no_field_replay_rows_supplied",
                "supplied_field_row_count": 0,
                "accepted_field_row_count": 0,
                "rejected_field_row_count": 0,
                "accepted_scenario_count": 0,
                "accepted_batch_count": 0,
                "accepted_batches_by_scenario": {},
                "scenario_evidence_counts": {},
                "scenario_acceptance": [
                    {
                        "scenario_id": row["scenario_id"],
                        "scenario_type": row["scenario_type"],
                        "acceptance_status": "missing_field_rows",
                        "accepted_batches": [],
                        "blocking_reasons": ["no_field_replay_rows_supplied"],
                    }
                    for row in row_collection_plan
                ],
                "can_write_to_actuator": False,
                "can_write_to_release_gate": False,
            }

        scenario_acceptance: list[dict[str, object]] = []
        accepted_batches_by_scenario: dict[str, list[str]] = {}
        rejected_row_count = 0
        accepted_field_row_count = 0
        for plan in row_collection_plan:
            scenario_id = str(plan["scenario_id"])
            scenario_type = str(plan["scenario_type"])
            candidate_batches = self._candidate_batches_for_scenario(plan)
            accepted_batches: list[str] = []
            blocking_reasons: list[str] = []
            for batch_id in candidate_batches:
                batch_status = self._validate_batch_for_plan(plan, batch_id)
                if batch_status["batch_acceptance_status"] == "accepted":
                    accepted_batches.append(batch_id)
                    accepted_field_row_count += int(batch_status["accepted_row_count"])
                else:
                    rejected_row_count += int(batch_status["rejected_row_count"])
                    blocking_reasons.extend(str(reason) for reason in batch_status["blocking_reasons"])
            if not candidate_batches:
                blocking_reasons.append("no_candidate_batch_for_scenario")
            if accepted_batches:
                accepted_batches_by_scenario[scenario_id] = accepted_batches
                acceptance_status = "accepted_field_replay_rows"
            else:
                acceptance_status = "field_replay_rows_rejected_or_incomplete"
            scenario_acceptance.append(
                {
                    "scenario_id": scenario_id,
                    "scenario_type": scenario_type,
                    "acceptance_status": acceptance_status,
                    "candidate_batches": candidate_batches,
                    "accepted_batches": accepted_batches,
                    "blocking_reasons": sorted(set(blocking_reasons)),
                }
            )

        accepted_scenario_count = len(accepted_batches_by_scenario)
        required_count = max(1, len(row_collection_plan))
        if accepted_scenario_count == 0:
            status = "field_replay_rows_present_but_not_accepted"
        elif accepted_scenario_count < required_count:
            status = "field_replay_rows_partially_accepted"
        else:
            status = "field_replay_rows_accepted_for_all_scenarios"
        return {
            "field_row_acceptance_status": status,
            "supplied_field_row_count": supplied_row_count,
            "accepted_field_row_count": accepted_field_row_count,
            "rejected_field_row_count": rejected_row_count,
            "accepted_scenario_count": accepted_scenario_count,
            "accepted_batch_count": sum(len(batch_ids) for batch_ids in accepted_batches_by_scenario.values()),
            "accepted_batches_by_scenario": accepted_batches_by_scenario,
            "scenario_evidence_counts": {
                scenario_id: len(batch_ids)
                for scenario_id, batch_ids in accepted_batches_by_scenario.items()
            },
            "scenario_acceptance": scenario_acceptance,
            "can_write_to_actuator": False,
            "can_write_to_release_gate": False,
        }

    def _candidate_batches_for_scenario(self, plan: dict[str, object]) -> list[str]:
        scenario_id = str(plan["scenario_id"])
        scenario_type = str(plan["scenario_type"])
        batch_role = str(plan["batch_role"])
        batches: set[str] = set()
        for rows in self.field_replay_rows_by_table.values():
            for row in rows:
                if not isinstance(row, dict):
                    continue
                if self._row_matches_scenario(row, scenario_id, scenario_type, batch_role):
                    batch_id = row.get("batch_id")
                    if self._is_real_value(batch_id):
                        batches.add(str(batch_id))
        return sorted(batches)

    def _validate_batch_for_plan(self, plan: dict[str, object], batch_id: str) -> dict[str, object]:
        accepted_row_count = 0
        rejected_row_count = 0
        blocking_reasons: list[str] = []
        for table, required_fields in REQUIRED_TABLE_FIELDS.items():
            matching_rows = [
                row
                for row in self.field_replay_rows_by_table.get(table, [])
                if isinstance(row, dict)
                and str(row.get("batch_id", "")) == batch_id
                and self._row_matches_scenario(
                    row,
                    str(plan["scenario_id"]),
                    str(plan["scenario_type"]),
                    str(plan["batch_role"]),
                )
            ]
            valid_rows = [
                row
                for row in matching_rows
                if self._row_has_real_required_values(row, required_fields)
                and self._is_field_origin(row.get("data_origin"))
            ]
            if not valid_rows:
                blocking_reasons.append(f"{table}:missing_real_required_fields_or_field_origin")
                rejected_row_count += len(matching_rows)
            else:
                accepted_row_count += 1
        replay_rows = [
            row
            for row in self.field_replay_rows_by_table.get("agent52_replay_table", [])
            if isinstance(row, dict)
            and str(row.get("batch_id", "")) == batch_id
            and self._row_matches_scenario(
                row,
                str(plan["scenario_id"]),
                str(plan["scenario_type"]),
                str(plan["batch_role"]),
            )
        ]
        valid_replay_rows = [
            row
            for row in replay_rows
            if self._row_has_real_required_values(row, AGENT52_REPLAY_REQUIRED_FIELDS)
            and self._is_field_origin(row.get("data_origin"))
        ]
        if not valid_replay_rows:
            blocking_reasons.append("agent52_replay_table:missing_real_field_origin_row")
            rejected_row_count += len(replay_rows)
        else:
            accepted_row_count += 1
        semantic_reasons = self._scenario_semantic_blockers(str(plan["scenario_type"]), batch_id)
        blocking_reasons.extend(semantic_reasons)
        return {
            "batch_id": batch_id,
            "batch_acceptance_status": "accepted" if not blocking_reasons else "rejected",
            "accepted_row_count": accepted_row_count,
            "rejected_row_count": rejected_row_count,
            "blocking_reasons": sorted(set(blocking_reasons)),
        }

    def _scenario_semantic_blockers(self, scenario_type: str, batch_id: str) -> list[str]:
        operation_rows = [
            row
            for row in self.field_replay_rows_by_table.get("campaign_operation_log", [])
            if isinstance(row, dict) and str(row.get("batch_id", "")) == batch_id
        ]
        replay_rows = [
            row
            for row in self.field_replay_rows_by_table.get("agent52_replay_table", [])
            if isinstance(row, dict) and str(row.get("batch_id", "")) == batch_id
        ]
        reasons: list[str] = []
        if scenario_type == "unresolved_conflict_review_block":
            has_unresolved = any(
                str(row.get("pressure_source_resolution", "")).lower() in {"unresolved", "pending", "pending_operator_review"}
                and bool(row.get("operator_review_required", False))
                for row in operation_rows
            )
            has_replay_block = any(
                int(row.get("unresolved_pressure_source_conflict_count", 0) or 0) > 0
                and bool(row.get("pressure_source_conflict_requires_operator_review", False))
                for row in replay_rows
            )
            has_control_block = any(
                bool(row.get("pressure_source_conflict_control_block", False))
                for row in replay_rows
            )
            if not (has_unresolved and has_replay_block and has_control_block):
                reasons.append("unresolved_conflict_requires_operator_review_and_replay_block")
        elif scenario_type in {
            "resolved_conflict_authoritative_source",
            "agent51_scoreability_recovery",
            "guardrail_clearance_replay",
        }:
            has_resolved_operation = any(
                str(row.get("pressure_source_resolution", "")).lower() == "resolved"
                and self._is_real_value(row.get("authoritative_pressure_source"))
                for row in operation_rows
            )
            has_resolution_record = any(
                int(row.get("resolved_pressure_source_conflict_count", 0) or 0) > 0
                and int(row.get("pressure_source_resolution_record_count", 0) or 0) > 0
                for row in replay_rows
            )
            if not (has_resolved_operation and has_resolution_record):
                reasons.append("resolved_conflict_requires_authoritative_source_and_resolution_record")
            if scenario_type == "guardrail_clearance_replay":
                has_clearance = any(
                    not bool(row.get("pressure_source_conflict_control_block", False))
                    and not bool(row.get("pressure_source_conflict_requires_operator_review", False))
                    for row in replay_rows
                )
                if not has_clearance:
                    reasons.append("guardrail_clearance_requires_no_control_block")
        elif scenario_type == "operator_review_latency_budget":
            has_latency_context = any(
                self._is_real_value(row.get("review_time")) and self._is_real_value(row.get("hold_time_min"))
                for row in operation_rows
            )
            if not has_latency_context:
                reasons.append("operator_review_latency_requires_review_time_and_hold_time")
        reasons.extend(self._temporal_window_blockers(batch_id))
        return reasons

    def _temporal_window_blockers(self, batch_id: str) -> list[str]:
        node_row = self._first_batch_row("node_modality_sensor_timeseries", batch_id)
        pressure_row = self._first_batch_row("pressure_headloss_event_log", batch_id)
        operation_row = self._first_batch_row("campaign_operation_log", batch_id)
        lab_row = self._first_batch_row("offline_lab_results", batch_id)
        proxy_row = self._first_batch_row("fast_proxy_event_log", batch_id)
        if not all([node_row, pressure_row, operation_row, lab_row, proxy_row]):
            return []

        sensor_time = self._numeric_value(node_row.get("sample_time_min"))
        pressure_time = self._numeric_value(pressure_row.get("event_time_min"))
        matched_lab_time = self._numeric_value(pressure_row.get("matched_lab_sample_time_min"))
        lab_sample_time = self._numeric_value(lab_row.get("sample_time_min"))
        lab_label_time = self._numeric_value(lab_row.get("lab_label_time_min"))
        proxy_time = self._numeric_value(proxy_row.get("proxy_label_time_min"))
        hold_time = self._numeric_value(operation_row.get("hold_time_min"))

        reasons: list[str] = []
        if None not in {sensor_time, pressure_time} and sensor_time > pressure_time:
            reasons.append("temporal_order_requires_sensor_sample_before_pressure_event")
        if None not in {pressure_time, proxy_time} and pressure_time > proxy_time:
            reasons.append("temporal_order_requires_pressure_event_before_fast_proxy")
        if None not in {lab_sample_time, lab_label_time} and lab_sample_time > lab_label_time:
            reasons.append("temporal_order_requires_lab_sample_before_lab_label")
        if None not in {pressure_time, matched_lab_time, lab_label_time} and not (
            pressure_time <= matched_lab_time <= lab_label_time
        ):
            reasons.append("temporal_order_requires_pressure_matched_lab_within_label_window")
        if None not in {proxy_time, lab_label_time} and proxy_time > lab_label_time:
            reasons.append("temporal_order_requires_fast_proxy_before_lab_label")
        evidence_times = [
            time
            for time in [
                sensor_time,
                pressure_time,
                matched_lab_time,
                lab_sample_time,
                lab_label_time,
                proxy_time,
            ]
            if time is not None
        ]
        if hold_time is not None and evidence_times and hold_time < max(evidence_times):
            reasons.append("hold_time_budget_must_cover_slowest_evidence_label")
        return reasons

    def _first_batch_row(self, table: str, batch_id: str) -> dict[str, object]:
        for row in self.field_replay_rows_by_table.get(table, []):
            if isinstance(row, dict) and str(row.get("batch_id", "")) == batch_id:
                return row
        return {}

    @staticmethod
    def _numeric_value(value: object) -> float | None:
        if isinstance(value, bool) or value is None:
            return None
        if isinstance(value, (int, float)):
            return float(value)
        try:
            return float(str(value).strip())
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _row_matches_scenario(
        row: dict[str, object],
        scenario_id: str,
        scenario_type: str,
        batch_role: str,
    ) -> bool:
        markers = {
            str(row.get("scenario_id", "")),
            str(row.get("scenario", "")),
            str(row.get("scenario_type", "")),
            str(row.get("batch_role", "")),
        }
        batch_id = str(row.get("batch_id", ""))
        return (
            scenario_id in markers
            or scenario_type in markers
            or batch_role in markers
            or batch_role in batch_id
        )

    @classmethod
    def _row_has_real_required_values(cls, row: dict[str, object], required_fields: list[str]) -> bool:
        if bool(row.get("template_only", False)):
            return False
        if str(row.get("evidence_status", "")).lower() == "template_not_field_evidence":
            return False
        return all(cls._is_real_value(row.get(field)) for field in required_fields)

    @staticmethod
    def _is_real_value(value: object) -> bool:
        if value is None:
            return False
        text = str(value).strip()
        if not text:
            return False
        lowered = text.lower()
        return not (
            lowered.startswith("todo")
            or "todo_" in lowered
            or "template" in lowered
            or lowered in {"nan", "none", "null"}
        )

    @classmethod
    def _is_field_origin(cls, value: object) -> bool:
        if not cls._is_real_value(value):
            return False
        text = str(value).strip().lower()
        return "field" in text and "template" not in text and "synthetic" not in text and "todo" not in text

    def _scenario_matrix(
        self,
        snapshot: dict[str, object],
        accepted_evidence_counts: dict[str, int] | None = None,
    ) -> list[dict[str, object]]:
        evidence_counts = self._scenario_evidence_counts()
        accepted_evidence_counts = accepted_evidence_counts or {}
        rows: list[dict[str, object]] = []
        for scenario in PRESSURE_RESOLUTION_SCENARIOS:
            scenario_id = str(scenario["scenario_id"])
            inferred = self._inferred_evidence_count(str(scenario["scenario_type"]), snapshot)
            evidence_count = max(
                int(evidence_counts.get(scenario_id, inferred) or 0),
                int(accepted_evidence_counts.get(scenario_id, 0) or 0),
            )
            row = {
                **scenario,
                "required_table_fields": REQUIRED_TABLE_FIELDS,
                "required_agent_context": [
                    "R7 pipeline pressure conflict readiness",
                    "Agent51 field_proxy_holdout_summary pressure resolution fields",
                    "Agent49 control_replay_guardrail_context pressure conflict block/clear",
                    "Agent52 replay_table/offline/readiness pressure conflict clear fields",
                ],
                "minimum_real_rows": 1,
                "field_evidence_count": evidence_count,
                "field_row_acceptance_count": int(accepted_evidence_counts.get(scenario_id, 0) or 0),
                "scenario_schema_ready": bool(REQUIRED_TABLE_FIELDS)
                and all(bool(fields) for fields in REQUIRED_TABLE_FIELDS.values()),
                "field_evidence_ready": evidence_count >= 1,
                "blocks_field_supported_claim_until_ready": evidence_count < 1,
                "cannot_write_to_actuator": True,
                "cannot_write_to_release_gate": True,
            }
            rows.append(row)
        return rows

    def _readiness(
        self,
        scenario_matrix: list[dict[str, object]],
        field_row_acceptance: dict[str, object],
    ) -> dict[str, object]:
        total = len(scenario_matrix)
        schema_ready = sum(1 for row in scenario_matrix if row["scenario_schema_ready"])
        field_ready = sum(1 for row in scenario_matrix if row["field_evidence_ready"])
        missing = [
            str(row["scenario_id"])
            for row in scenario_matrix
            if not bool(row["field_evidence_ready"])
        ]
        schema_coverage = round(schema_ready / max(1, total), 3)
        field_coverage = round(field_ready / max(1, total), 3)
        agent52_resolution_fields_ready = self._agent52_resolution_fields_ready()
        agent49_resolution_fields_ready = self._agent49_resolution_fields_ready()
        r7_resolution_fields_ready = self._r7_resolution_fields_ready()
        source_chain_ready = agent52_resolution_fields_ready and agent49_resolution_fields_ready and r7_resolution_fields_ready
        score = round(
            0.36 * schema_coverage
            + 0.34 * field_coverage
            + 0.18 * float(source_chain_ready)
            + 0.12 * float(total >= self.min_required_scenarios),
            3,
        )
        if total < self.min_required_scenarios or schema_coverage < 1.0:
            status = "pressure_resolution_scenario_pack_schema_incomplete"
        elif field_coverage >= 1.0 and source_chain_ready:
            status = "pressure_resolution_scenario_pack_field_replay_ready_for_human_review"
        elif field_coverage > 0.0:
            status = "pressure_resolution_scenario_pack_partial_field_replay"
        else:
            status = "pressure_resolution_scenario_pack_ready_needs_real_replay_rows"
        next_action = (
            "R8v_route_pressure_resolution_rows_to_field_replay_and_holdout_gates"
            if field_coverage >= 1.0 and source_chain_ready
            else "R8p_collect_pressure_resolution_replay_rows"
        )
        return {
            "scenario_pack_status": status,
            "scenario_pack_score": score,
            "scenario_count": total,
            "required_scenario_count": self.min_required_scenarios,
            "scenario_schema_coverage": schema_coverage,
            "field_scenario_coverage": field_coverage,
            "missing_field_scenarios": missing,
            "agent52_resolution_fields_ready": agent52_resolution_fields_ready,
            "agent49_resolution_fields_ready": agent49_resolution_fields_ready,
            "r7_resolution_fields_ready": r7_resolution_fields_ready,
            "source_chain_resolution_fields_ready": source_chain_ready,
            "field_row_acceptance_status": field_row_acceptance["field_row_acceptance_status"],
            "accepted_field_scenario_count": field_row_acceptance["accepted_scenario_count"],
            "accepted_field_row_count": field_row_acceptance["accepted_field_row_count"],
            "accepted_field_batch_count": field_row_acceptance["accepted_batch_count"],
            "can_update_agent60_fallback": schema_coverage >= 1.0 and total >= self.min_required_scenarios,
            "can_upgrade_field_supported_claim": field_coverage >= 1.0 and source_chain_ready,
            "can_write_to_actuator": False,
            "can_write_to_release_gate": False,
            "next_recommended_core_action": next_action,
        }

    def _issues(
        self,
        scenario_matrix: list[dict[str, object]],
        readiness: dict[str, object],
        field_row_acceptance: dict[str, object],
    ) -> list[QualityIssue]:
        issues: list[QualityIssue] = []
        if field_row_acceptance["field_row_acceptance_status"] in {
            "field_replay_rows_present_but_not_accepted",
            "field_replay_rows_partially_accepted",
        }:
            issues.append(
                QualityIssue(
                    sensor="pressure_resolution_replay_scenario_pack",
                    issue_type="pressure_resolution_field_rows_rejected",
                    severity=Severity.WARNING,
                    message="检测到 pressure resolution 行，但它们仍包含模板/TODO、缺字段、非 field origin 或跨表 batch 不完整。",
                    evidence={"scenario_acceptance": field_row_acceptance["scenario_acceptance"]},
                )
            )
        if readiness["field_scenario_coverage"] < 1.0:
            issues.append(
                QualityIssue(
                    sensor="pressure_resolution_replay_scenario_pack",
                    issue_type="pressure_resolution_field_replay_rows_required",
                    severity=Severity.INFO,
                    message="R8o 场景合同已定义，但缺真实 resolved/unresolved pressure conflict replay 行。",
                    evidence={"missing_field_scenarios": readiness["missing_field_scenarios"]},
                )
            )
        if not readiness["source_chain_resolution_fields_ready"]:
            issues.append(
                QualityIssue(
                    sensor="pressure_resolution_replay_scenario_pack",
                    issue_type="pressure_resolution_source_chain_fields_incomplete",
                    severity=Severity.WARNING,
                    message="R7、Agent49 或 Agent52 尚未完整暴露 pressure resolution 字段，不能验证解除门端到端。",
                    evidence={
                        "r7": readiness["r7_resolution_fields_ready"],
                        "agent49": readiness["agent49_resolution_fields_ready"],
                        "agent52": readiness["agent52_resolution_fields_ready"],
                    },
                )
            )
        for row in scenario_matrix:
            if row["blocks_field_supported_claim_until_ready"]:
                issues.append(
                    QualityIssue(
                        sensor=str(row["scenario_id"]),
                        issue_type="pressure_resolution_scenario_missing_field_evidence",
                        severity=Severity.INFO,
                        message="该 pressure resolution 场景缺真实 replay 证据，不能升级为 field-supported clearance。",
                        evidence={"scenario_type": row["scenario_type"], "purpose": row["purpose"]},
                    )
                )
        return issues

    @staticmethod
    def _recommendations(
        readiness: dict[str, object],
        row_collection_readiness: dict[str, object],
    ) -> list[str]:
        return [
            "下一步采集至少 1 个 unresolved pressure conflict batch 和 1 个 resolved pressure conflict batch，并保留 reviewer/calibration/action 链。",
            "每个场景必须同时连接 node_modality_sensor_timeseries、pressure_headloss_event_log、campaign_operation_log、offline_lab_results 和 Agent49/52 replay row。",
            f"R8p 行级采集计划状态：{row_collection_readiness['row_collection_plan_status']}；缺失场景数 {row_collection_readiness['missing_scenario_count']}，模板行数 {row_collection_readiness['template_row_count']}。",
            "即使 R8o schema 完整，没有真实 replay 行前仍不得写 actuator 或 release gate。",
            f"当前下一步：{readiness['next_recommended_core_action']}。",
        ]

    def _source_snapshot(self) -> dict[str, object]:
        r7 = self._r7_readiness()
        agent51 = self._agent51_context()
        agent49 = self._agent49_context()
        agent52 = self._agent52_context()
        return {
            "pressure_source_conflict_count": max(
                self._int(r7, "pressure_source_conflict_count"),
                self._int(agent51, "pressure_source_conflict_count"),
                self._int(agent49, "pressure_source_conflict_count"),
                self._int(agent52, "pressure_source_conflict_count"),
            ),
            "resolved_pressure_source_conflict_count": max(
                self._int(r7, "resolved_pressure_source_conflict_count"),
                self._int(agent51, "resolved_pressure_source_conflict_count"),
                self._int(agent49, "resolved_pressure_source_conflict_count"),
                self._int(agent52, "resolved_pressure_source_conflict_count"),
            ),
            "unresolved_pressure_source_conflict_count": max(
                self._int(r7, "unresolved_pressure_source_conflict_count"),
                self._int(agent51, "unresolved_pressure_source_conflict_count"),
                self._int(agent49, "unresolved_pressure_source_conflict_count"),
                self._int(agent52, "unresolved_pressure_source_conflict_count"),
            ),
            "pressure_source_resolution_record_count": max(
                self._int(r7, "pressure_source_resolution_record_count"),
                self._int(agent51, "pressure_source_resolution_record_count"),
                self._int(agent49, "pressure_source_resolution_record_count"),
                self._int(agent52, "pressure_source_resolution_record_count"),
            ),
            "pressure_source_conflict_requires_operator_review": any(
                bool(context.get("pressure_source_conflict_requires_operator_review", context.get("conflict_requires_operator_review", False)))
                for context in (r7, agent51, agent49, agent52)
            ),
            "agent49_pressure_source_conflict_control_block": bool(
                agent49.get("pressure_source_conflict_control_block", False)
            ),
            "agent52_pressure_source_conflict_clear": bool(agent52.get("pressure_source_conflict_clear", False)),
            "agent52_pressure_source_conflict_replay_blocked_case_count": self._int(
                agent52,
                "pressure_source_conflict_replay_blocked_case_count",
            ),
            "agent51_scoreable_batch_count": self._int(agent51, "scoreable_batch_count", "field_holdout_scoreable_batch_count"),
            "field_package_pressure_conflict_resolution_status": r7.get(
                "field_package_pressure_conflict_resolution_status",
                "unknown",
            ),
        }

    def _r7_readiness(self) -> dict[str, object]:
        readiness = self._dict(self.r7_pipeline_metrics.get("pipeline_readiness"))
        coverage = self._dict(self.r7_pipeline_metrics.get("field_package_coverage"))
        coverage_readiness = self._dict(coverage.get("readiness"))
        return {**coverage_readiness, **readiness}

    def _agent51_context(self) -> dict[str, object]:
        readiness = self._dict(self.catalyst_proxy_metrics.get("readiness"))
        summary = self._dict(self.catalyst_proxy_metrics.get("field_proxy_holdout_summary"))
        return {**readiness, **summary}

    def _agent49_context(self) -> dict[str, object]:
        return self._dict(self.collaborative_control_metrics.get("control_replay_guardrail_context"))

    def _agent52_context(self) -> dict[str, object]:
        offline = self._dict(self.replay_evaluation_metrics.get("offline_evaluation_metrics"))
        readiness = self._dict(self.replay_evaluation_metrics.get("readiness"))
        pressure_context = self._dict(self.replay_evaluation_metrics.get("pressure_headloss_context"))
        return {**offline, **readiness, **pressure_context}

    def _scenario_evidence_counts(self) -> dict[str, int]:
        evidence = self._dict(self.replay_evaluation_metrics.get("pressure_resolution_replay_scenario_evidence"))
        result: dict[str, int] = {}
        for key, value in evidence.items():
            try:
                result[str(key)] = int(value)
            except (TypeError, ValueError):
                result[str(key)] = 0
        return result

    @staticmethod
    def _inferred_evidence_count(scenario_type: str, snapshot: dict[str, object]) -> int:
        unresolved = int(snapshot.get("unresolved_pressure_source_conflict_count", 0) or 0)
        resolved = int(snapshot.get("resolved_pressure_source_conflict_count", 0) or 0)
        resolution_records = int(snapshot.get("pressure_source_resolution_record_count", 0) or 0)
        review_required = bool(snapshot.get("pressure_source_conflict_requires_operator_review", False))
        agent49_block = bool(snapshot.get("agent49_pressure_source_conflict_control_block", False))
        agent52_clear = bool(snapshot.get("agent52_pressure_source_conflict_clear", False))
        blocked_cases = int(snapshot.get("agent52_pressure_source_conflict_replay_blocked_case_count", 0) or 0)
        scoreable = int(snapshot.get("agent51_scoreable_batch_count", 0) or 0)
        if scenario_type == "unresolved_conflict_review_block":
            return int(unresolved > 0 and review_required and (agent49_block or blocked_cases > 0))
        if scenario_type == "resolved_conflict_authoritative_source":
            return int(resolved > 0 and resolution_records > 0)
        if scenario_type == "operator_review_latency_budget":
            return int(resolution_records > 0)
        if scenario_type == "agent51_scoreability_recovery":
            return int(resolved > 0 and scoreable > 0)
        if scenario_type == "guardrail_clearance_replay":
            return int(resolved > 0 and agent52_clear and not agent49_block)
        return 0

    def _r7_resolution_fields_ready(self) -> bool:
        readiness = self._r7_readiness()
        return all(
            key in readiness
            for key in (
                "pressure_source_conflict_count",
                "resolved_pressure_source_conflict_count",
                "unresolved_pressure_source_conflict_count",
                "pressure_source_resolution_record_count",
                "field_package_pressure_conflict_resolution_status",
                "field_package_pressure_conflict_resolution_ready",
            )
        )

    def _agent49_resolution_fields_ready(self) -> bool:
        context = self._agent49_context()
        return all(
            key in context
            for key in (
                "pressure_source_conflict_count",
                "resolved_pressure_source_conflict_count",
                "unresolved_pressure_source_conflict_count",
                "pressure_source_resolution_record_count",
                "pressure_source_conflict_control_block",
            )
        )

    def _agent52_resolution_fields_ready(self) -> bool:
        context = self._agent52_context()
        return all(
            key in context
            for key in (
                "pressure_source_conflict_count",
                "resolved_pressure_source_conflict_count",
                "unresolved_pressure_source_conflict_count",
                "pressure_source_resolution_record_count",
                "pressure_source_conflict_clear",
            )
        )

    @staticmethod
    def _agent60_writeback(readiness: dict[str, object]) -> dict[str, object]:
        return {
            "completion_status_for_architecture_consolidation": "R8o_pressure_resolution_scenario_pack_ready"
            if readiness["can_update_agent60_fallback"]
            else "R8o_pressure_resolution_scenario_pack_incomplete",
            "recommended_next_fallback_action": readiness["next_recommended_core_action"],
            "allowed_writeback": ["offline_core_fallback_action", "r8o_scenario_package_metrics"]
            if readiness["can_update_agent60_fallback"]
            else [],
            "blocked_writeback": ["actuator_policy", "release_gate_policy", "field_supported_claim"],
        }

    @staticmethod
    def _dict(value: object) -> dict[str, object]:
        return value if isinstance(value, dict) else {}

    @classmethod
    def _int(cls, values: dict[str, object], *keys: str) -> int:
        for key in keys:
            if key in values:
                try:
                    return int(values.get(key) or 0)
                except (TypeError, ValueError):
                    return 0
        return 0

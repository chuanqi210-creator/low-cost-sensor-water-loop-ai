from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ControlGuardrailBackpropagation:
    """Backpropagate guardrail-resolved replay failures into grey-box and field needs."""

    replay_evaluation_metrics: dict[str, Any]
    grey_box_physics_metrics: dict[str, Any]
    field_validation_alignment_metrics: dict[str, Any]
    claim_specific_package_metrics: dict[str, Any]
    data_origin: str = "synthetic_guardrail_backpropagation"

    def build(self) -> dict[str, Any]:
        resolved_cases = self._resolved_cases()
        backpropagation_table = [self._map_case(case) for case in resolved_cases]
        coverage = self._coverage(backpropagation_table)
        readiness = self._readiness(coverage)
        return {
            "method_contract": self._method_contract(),
            "resolved_case_backpropagation_table": backpropagation_table,
            "coverage_metrics": coverage,
            "grey_box_patch": self._grey_box_patch(backpropagation_table),
            "field_requirement_patch": self._field_requirement_patch(backpropagation_table),
            "readiness": readiness,
            "writeback_policy": self._writeback_policy(readiness),
            "next_refactor_action": self._next_refactor_action(readiness),
        }

    @staticmethod
    def _method_contract() -> dict[str, Any]:
        return {
            "upgrade_id": "R4_control_guardrail_failure_backpropagation",
            "borrowed_from": [
                "model-based diagnosis after counterfactual policy replay",
                "grey-box residual boundary review",
                "field requirement traceability matrix",
                "failure mode and effects analysis for control guardrails",
            ],
            "reality_mapping": (
                "把 R3c replay 中被 guardrail 修复的控制失败案例，反写为灰箱机制边界和现场 replay 必采字段，"
                "让控制层的经验修正回到可解释过程机制。"
            ),
            "data_needs": [
                "Agent52 guardrail_resolved_cases",
                "Agent52 replay_table with missingness and rewards",
                "Agent53 grey_box failure boundaries",
                "Agent58/59 field requirement and claim-specific field package",
            ],
            "evaluation_metrics": [
                "resolved_case_to_mechanism_coverage",
                "resolved_case_to_field_requirement_coverage",
                "grey_box_failure_boundary_count",
                "field_replay_required_field_count",
            ],
            "failure_boundary": (
                "R4 can update grey-box boundary candidates and field requirement patches, but cannot claim field validation or write actuators."
            ),
        }

    def _map_case(self, case: dict[str, Any]) -> dict[str, Any]:
        scenario = str(case.get("scenario", ""))
        if scenario == "catalyst_uncertain_low_proxy":
            return {
                **case,
                "mechanism_family": "catalyst_activity_proxy_uncertainty",
                "grey_box_boundary": [
                    "catalyst activity cannot be treated as observed without proxy holdout label",
                    "protective/regeneration actions require pressure-drop or lifecycle evidence",
                    "matrix inhibition and catalyst deactivation must remain separable hypotheses",
                ],
                "field_required_fields": [
                    "proxy_holdout_label",
                    "pressure_drop_kPa",
                    "regeneration_event",
                    "operator_override",
                    "N3_catalyst_bed_outlet:UV254_abs",
                    "N3_catalyst_bed_outlet:turbidity_NTU",
                ],
                "target_modules": [
                    "M1_sparse_observation_layout",
                    "M3_grey_box_mechanism",
                    "M6_field_evidence_chain",
                ],
                "control_implication": "keep J4_safe_low_cost_standby or human-reviewed catalyst protection until field proxy labels close the uncertainty.",
                "claim_boundary": "synthetic guardrail resolved false-positive catalyst protection; field proxy labels are required before catalyst-control claim upgrade.",
            }
        if scenario == "hydraulic_delay_violation":
            return {
                **case,
                "mechanism_family": "hydraulic_latency_and_storage_uncertainty",
                "grey_box_boundary": [
                    "recycle escalation is unsafe when residence-time delay and storage margin are unobserved",
                    "latency budget must include actuator response, pump-valve result and tank capacity",
                    "loop retention benefit must be checked against polishing/release-gate alternative",
                ],
                "field_required_fields": [
                    "tank_storage_margin",
                    "actuator_latency_p90",
                    "pump_valve_result",
                    "flow_Lmin",
                    "hold_time_min",
                    "recycle_ratio",
                ],
                "target_modules": [
                    "M3_grey_box_mechanism",
                    "M4_collaborative_control",
                    "M6_field_evidence_chain",
                ],
                "control_implication": "prefer J3_polishing_and_release_gate over recycle escalation until hydraulic execution evidence exists.",
                "claim_boundary": "synthetic guardrail resolved high-regret recycle action; field hydraulic replay is required before recycle-control claim upgrade.",
            }
        return {
            **case,
            "mechanism_family": "unmapped_guardrail_failure",
            "grey_box_boundary": ["case requires manual mechanism mapping"],
            "field_required_fields": ["operator_or_expert_action_id", "reward_by_action", "next_state_summary"],
            "target_modules": ["M6_field_evidence_chain"],
            "control_implication": "hold for manual review",
            "claim_boundary": "unmapped synthetic guardrail case cannot upgrade any claim.",
        }

    def _coverage(self, table: list[dict[str, Any]]) -> dict[str, Any]:
        resolved_count = len(table)
        mechanism_count = sum(1 for row in table if row.get("mechanism_family") != "unmapped_guardrail_failure")
        field_count = sum(1 for row in table if row.get("field_required_fields"))
        unique_fields = sorted({str(field) for row in table for field in row.get("field_required_fields", [])})
        boundaries = [boundary for row in table for boundary in row.get("grey_box_boundary", [])]
        field_replay_coverage = self._field_replay_coverage()
        return {
            "resolved_case_count": resolved_count,
            "resolved_case_to_mechanism_coverage": round(mechanism_count / max(1, resolved_count), 3),
            "resolved_case_to_field_requirement_coverage": round(field_count / max(1, resolved_count), 3),
            "grey_box_failure_boundary_count": len(boundaries),
            "field_replay_required_field_count": len(unique_fields),
            "unique_field_replay_required_fields": unique_fields,
            "field_replay_coverage": field_replay_coverage,
            "data_origin": self.data_origin,
        }

    def _grey_box_patch(self, table: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [
            {
                "mechanism_family": row["mechanism_family"],
                "scenario": row["scenario"],
                "grey_box_boundary": row["grey_box_boundary"],
                "control_implication": row["control_implication"],
                "target_agent": "minimal_grey_box_physics_agent",
                "field_boundary": row["claim_boundary"],
            }
            for row in table
        ]

    def _field_requirement_patch(self, table: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [
            {
                "scenario": row["scenario"],
                "required_fields": row["field_required_fields"],
                "target_agents": [
                    "field_validation_queue_alignment_agent",
                    "claim_specific_field_package_agent",
                    "field_replay_import_agent",
                ],
                "claim_boundary": row["claim_boundary"],
            }
            for row in table
        ]

    def _readiness(self, coverage: dict[str, Any]) -> dict[str, Any]:
        ready = (
            int(coverage["resolved_case_count"]) >= 2
            and float(coverage["resolved_case_to_mechanism_coverage"]) >= 1.0
            and float(coverage["resolved_case_to_field_requirement_coverage"]) >= 1.0
        )
        field_ready = float(coverage["field_replay_coverage"]) >= 0.85 and self.data_origin.startswith("field_")
        score = round(
            0.24 * float(ready)
            + 0.20 * float(coverage["resolved_case_to_mechanism_coverage"])
            + 0.20 * float(coverage["resolved_case_to_field_requirement_coverage"])
            + 0.16 * min(1.0, int(coverage["grey_box_failure_boundary_count"]) / 6)
            + 0.12 * min(1.0, int(coverage["field_replay_required_field_count"]) / 10)
            + 0.08 * float(field_ready),
            3,
        )
        status = (
            "field_guardrail_backpropagation_candidate_ready"
            if field_ready and ready
            else "synthetic_guardrail_backpropagation_ready_needs_field_replay_and_grey_box_calibration"
        )
        return {
            "guardrail_backpropagation_status": status,
            "guardrail_backpropagation_score": score,
            "backpropagation_ready": ready,
            "field_ready": field_ready,
            "can_update_agent53_failure_boundaries": ready,
            "can_update_field_requirement_patch": ready,
            "can_write_to_actuator": False,
            "can_write_to_release_gate": False,
        }

    @staticmethod
    def _writeback_policy(readiness: dict[str, Any]) -> dict[str, Any]:
        return {
            "allowed_writeback": [
                "agent53_grey_box_failure_boundary_candidate",
                "agent58_59_field_requirement_patch_candidate",
                "architecture_consolidation_R4_status",
            ]
            if readiness["backpropagation_ready"]
            else [],
            "blocked_writeback": [
                "actuator_policy",
                "release_gate_policy",
                "field_control_effectiveness_claim",
                "grey_box_parameter_calibration_claim",
            ],
            "can_write_to_actuator": False,
            "can_write_to_release_gate": False,
            "policy_effect": "R4 can only backpropagate guardrail cases into mechanism and data requirements.",
        }

    @staticmethod
    def _next_refactor_action(readiness: dict[str, Any]) -> dict[str, Any]:
        if readiness["backpropagation_ready"]:
            return {
                "action_id": "R4b_patch_agent53_and_field_requirement_interfaces",
                "title": "把 R4 grey-box/field patches 接入 Agent53、Agent58 和 Agent59",
                "reason": "R4 已形成控制失败到机制边界和现场字段的映射；下一步应让灰箱和 field package 消费这些 patch。",
                "must_not_do": "不能把 synthetic backpropagation 当作 field-supported mechanism calibration.",
            }
        return {
            "action_id": "R4_continue_guardrail_case_mapping",
            "title": "继续补 R3c resolved cases 的机制映射",
            "reason": "仍有 guardrail resolved cases 未映射到灰箱边界或现场字段。",
            "must_not_do": "不能跳过机制映射直接改控制动作。",
        }

    def _resolved_cases(self) -> list[dict[str, Any]]:
        diagnostics = self.replay_evaluation_metrics.get("reward_diagnostics", {})
        diagnostics = diagnostics if isinstance(diagnostics, dict) else {}
        cases = diagnostics.get("guardrail_resolved_cases", [])
        return cases if isinstance(cases, list) else []

    def _field_replay_coverage(self) -> float:
        metrics = self.replay_evaluation_metrics.get("offline_evaluation_metrics", {})
        metrics = metrics if isinstance(metrics, dict) else {}
        return float(metrics.get("field_replay_coverage", 0.0))

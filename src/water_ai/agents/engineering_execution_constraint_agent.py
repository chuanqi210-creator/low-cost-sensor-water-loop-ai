from __future__ import annotations

from collections.abc import Sequence

from water_ai.agents.base import BaseAgent
from water_ai.domain import AgentReport, QualityIssue, SensorReading, Severity


JOINT_ACTION_RESOURCE_PROFILES: dict[str, dict[str, float]] = {
    "J0_matrix_shock_equalize_and_recycle": {
        "actuator_switch_count": 3.0,
        "actuator_p90_latency_min": 12.0,
        "storage_required_m3": 14.0,
        "chemical_inventory_fraction_required": 0.00,
        "maintenance_window_required_min": 0.0,
        "human_review_required_min": 8.0,
        "energy_cost_index": 0.32,
        "false_positive_cost_index": 0.12,
    },
    "J1_reaction_completion_recovery": {
        "actuator_switch_count": 2.0,
        "actuator_p90_latency_min": 10.0,
        "storage_required_m3": 8.0,
        "chemical_inventory_fraction_required": 0.28,
        "maintenance_window_required_min": 0.0,
        "human_review_required_min": 5.0,
        "energy_cost_index": 0.36,
        "false_positive_cost_index": 0.14,
    },
    "J2_catalyst_protection_before_regeneration": {
        "actuator_switch_count": 2.0,
        "actuator_p90_latency_min": 18.0,
        "storage_required_m3": 10.0,
        "chemical_inventory_fraction_required": 0.05,
        "maintenance_window_required_min": 45.0,
        "human_review_required_min": 18.0,
        "energy_cost_index": 0.18,
        "false_positive_cost_index": 0.20,
    },
    "J3_polishing_and_release_gate": {
        "actuator_switch_count": 3.0,
        "actuator_p90_latency_min": 14.0,
        "storage_required_m3": 18.0,
        "chemical_inventory_fraction_required": 0.02,
        "maintenance_window_required_min": 0.0,
        "human_review_required_min": 22.0,
        "energy_cost_index": 0.30,
        "false_positive_cost_index": 0.11,
    },
    "J4_safe_low_cost_standby": {
        "actuator_switch_count": 1.0,
        "actuator_p90_latency_min": 8.0,
        "storage_required_m3": 20.0,
        "chemical_inventory_fraction_required": 0.00,
        "maintenance_window_required_min": 0.0,
        "human_review_required_min": 26.0,
        "energy_cost_index": 0.10,
        "false_positive_cost_index": 0.08,
    },
}


DEFAULT_ENGINEERING_PROFILE: dict[str, float | bool] = {
    "max_actuator_switch_count_per_batch": 4.0,
    "max_actuator_p90_latency_min": 16.0,
    "available_buffer_storage_m3": 18.0,
    "chemical_inventory_fraction_available": 0.34,
    "maintenance_window_available_min": 35.0,
    "human_review_capacity_min": 28.0,
    "max_energy_cost_index": 0.62,
    "max_false_positive_cost_index": 0.16,
    "plc_scada_point_list_verified": False,
    "operator_sop_verified": False,
}


ACTION_PATCH_MAPPING = {
    "hold_for_validation": ["J3_polishing_and_release_gate", "J4_safe_low_cost_standby"],
    "recirculate": [
        "J0_matrix_shock_equalize_and_recycle",
        "J1_reaction_completion_recovery",
        "J3_polishing_and_release_gate",
    ],
    "dose_oxidant": ["J1_reaction_completion_recovery"],
    "regenerate_catalyst": ["J2_catalyst_protection_before_regeneration"],
    "replace_catalyst": ["J2_catalyst_protection_before_regeneration"],
    "switch_or_pretreat": ["J0_matrix_shock_equalize_and_recycle"],
    "release": ["J3_polishing_and_release_gate"],
}


class EngineeringExecutionConstraintAgent(BaseAgent):
    """Patch control rewards with storage, actuator, inventory and review constraints."""

    name = "engineering_execution_constraint_agent"

    def __init__(
        self,
        *,
        collaborative_control_metrics: dict[str, object] | None = None,
        engineering_profile: dict[str, object] | None = None,
        data_origin: str = "synthetic_engineering_constraint_design",
        field_execution_validation: dict[str, float] | None = None,
    ) -> None:
        self.collaborative_control_metrics = collaborative_control_metrics or {}
        self.engineering_profile = {**DEFAULT_ENGINEERING_PROFILE, **(engineering_profile or {})}
        self.data_origin = data_origin
        self.field_execution_validation = field_execution_validation or {}

    def run(self, readings: Sequence[SensorReading]) -> AgentReport:
        del readings
        contract = self._constraint_contract()
        joint_evaluation = self._joint_action_constraint_evaluation(contract)
        reward_patch = self._agent49_reward_patch(joint_evaluation)
        action_patch = self._action_constraint_patch(joint_evaluation)
        readiness = self._readiness(contract, joint_evaluation)
        issues = self._issues(readiness, joint_evaluation)
        recommendations = self._recommendations(readiness, joint_evaluation)
        summary = (
            f"工程执行约束：{readiness['engineering_constraints_status']}；"
            f"mean_feasibility={readiness['mean_execution_feasibility']:.3f}，"
            f"hard_blocked_joint_actions={readiness['hard_blocked_joint_action_count']}。"
        )
        confidence = round(
            min(0.91, max(0.24, 0.40 + 0.40 * readiness["engineering_constraints_score"] - 0.035 * len(issues))),
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
                "engineering_constraint_contract": contract,
                "joint_action_constraint_evaluation": joint_evaluation,
                "agent49_reward_patch": reward_patch,
                "action_constraint_patch": action_patch,
                "arbitration_patch": self._arbitration_patch(action_patch, readiness),
                "readiness": readiness,
                "agent50_writeback": self._agent50_writeback(readiness),
            },
        )

    def _constraint_contract(self) -> dict[str, object]:
        return {
            "contract_id": "P7_engineering_execution_constraints_v1",
            "data_origin": self.data_origin,
            "constraints": {
                "max_actuator_switch_count_per_batch": self._number("max_actuator_switch_count_per_batch"),
                "max_actuator_p90_latency_min": self._number("max_actuator_p90_latency_min"),
                "available_buffer_storage_m3": self._number("available_buffer_storage_m3"),
                "chemical_inventory_fraction_available": self._number("chemical_inventory_fraction_available"),
                "maintenance_window_available_min": self._number("maintenance_window_available_min"),
                "human_review_capacity_min": self._number("human_review_capacity_min"),
                "max_energy_cost_index": self._number("max_energy_cost_index"),
                "max_false_positive_cost_index": self._number("max_false_positive_cost_index"),
            },
            "field_execution_gates": [
                "plc_scada_point_list_verified",
                "operator_sop_verified",
                "field_execution_replay_coverage >= 0.85",
                "actuator_success_rate >= 0.95",
                "actuator_p90_latency_min <= configured maximum",
            ],
            "resource_profiles": self._resource_profiles(),
            "failure_boundary": (
                "synthetic constraint patch can change reward ranking and arbitration candidates, "
                "but cannot authorize PLC/SCADA execution or release gate writes without field execution replay."
            ),
        }

    def _resource_profiles(self) -> list[dict[str, object]]:
        observed_ids = self._observed_joint_action_ids()
        ids = observed_ids or list(JOINT_ACTION_RESOURCE_PROFILES)
        rows: list[dict[str, object]] = []
        for action_id in ids:
            profile = JOINT_ACTION_RESOURCE_PROFILES.get(action_id, JOINT_ACTION_RESOURCE_PROFILES["J4_safe_low_cost_standby"])
            rows.append({"joint_action_id": action_id, **profile})
        return rows

    def _observed_joint_action_ids(self) -> list[str]:
        joint_actions = self.collaborative_control_metrics.get("joint_action_matrix", [])
        if not isinstance(joint_actions, list):
            return []
        ids = [str(item.get("joint_action_id", "")) for item in joint_actions if isinstance(item, dict) and item.get("joint_action_id")]
        return [action_id for action_id in ids if action_id]

    def _joint_action_constraint_evaluation(self, contract: dict[str, object]) -> list[dict[str, object]]:
        constraints = contract["constraints"] if isinstance(contract["constraints"], dict) else {}
        rows: list[dict[str, object]] = []
        for profile in contract["resource_profiles"]:
            if not isinstance(profile, dict):
                continue
            pressure = {
                "switch_pressure": self._ratio_excess(profile, "actuator_switch_count", constraints, "max_actuator_switch_count_per_batch"),
                "latency_pressure": self._ratio_excess(profile, "actuator_p90_latency_min", constraints, "max_actuator_p90_latency_min"),
                "storage_pressure": self._ratio_excess(profile, "storage_required_m3", constraints, "available_buffer_storage_m3"),
                "chemical_inventory_pressure": self._inventory_pressure(profile, constraints),
                "maintenance_window_pressure": self._ratio_excess(profile, "maintenance_window_required_min", constraints, "maintenance_window_available_min"),
                "human_review_pressure": self._ratio_excess(profile, "human_review_required_min", constraints, "human_review_capacity_min"),
                "energy_pressure": self._ratio_excess(profile, "energy_cost_index", constraints, "max_energy_cost_index"),
                "false_positive_pressure": self._ratio_excess(profile, "false_positive_cost_index", constraints, "max_false_positive_cost_index"),
            }
            penalty = self._engineering_penalty(pressure)
            feasibility = self._clip(1.0 - 1.12 * penalty)
            hard_reasons = self._hard_block_reasons(pressure)
            rows.append(
                {
                    "joint_action_id": str(profile["joint_action_id"]),
                    "resource_profile": {key: value for key, value in profile.items() if key != "joint_action_id"},
                    "constraint_pressure": {key: round(value, 3) for key, value in pressure.items()},
                    "engineering_constraint_penalty": round(penalty, 3),
                    "execution_feasibility": round(feasibility, 3),
                    "hard_blocked_by_engineering": bool(hard_reasons),
                    "hard_block_reasons": hard_reasons,
                    "arbitration_required_checks": self._required_checks(pressure, hard_reasons),
                }
            )
        return rows

    @staticmethod
    def _ratio_excess(
        profile: dict[str, object],
        profile_key: str,
        constraints: dict[str, object],
        constraint_key: str,
    ) -> float:
        demand = float(profile.get(profile_key, 0.0))
        limit = max(1e-6, float(constraints.get(constraint_key, 0.0)))
        if demand <= 0.0:
            return 0.0
        return max(0.0, demand / limit - 1.0)

    @staticmethod
    def _inventory_pressure(profile: dict[str, object], constraints: dict[str, object]) -> float:
        required = float(profile.get("chemical_inventory_fraction_required", 0.0))
        available = float(constraints.get("chemical_inventory_fraction_available", 0.0))
        if required <= 0.0:
            return 0.0
        return max(0.0, (required - available) / max(0.01, required))

    def _engineering_penalty(self, pressure: dict[str, float]) -> float:
        return self._clip(
            0.15 * pressure["switch_pressure"]
            + 0.15 * pressure["latency_pressure"]
            + 0.20 * pressure["storage_pressure"]
            + 0.16 * pressure["chemical_inventory_pressure"]
            + 0.13 * pressure["maintenance_window_pressure"]
            + 0.10 * pressure["human_review_pressure"]
            + 0.06 * pressure["energy_pressure"]
            + 0.05 * pressure["false_positive_pressure"],
            hi=0.72,
        )

    @staticmethod
    def _hard_block_reasons(pressure: dict[str, float]) -> list[str]:
        thresholds = {
            "storage_pressure": 0.20,
            "chemical_inventory_pressure": 0.18,
            "maintenance_window_pressure": 0.20,
            "human_review_pressure": 0.35,
            "latency_pressure": 0.35,
        }
        return [key for key, threshold in thresholds.items() if pressure.get(key, 0.0) > threshold]

    @staticmethod
    def _required_checks(pressure: dict[str, float], hard_reasons: list[str]) -> list[str]:
        checks = ["operator_sop_review", "operation_log_replay_alignment"]
        if pressure.get("storage_pressure", 0.0) > 0:
            checks.append("buffer_storage_capacity_check")
        if pressure.get("chemical_inventory_pressure", 0.0) > 0:
            checks.append("chemical_inventory_check")
        if pressure.get("maintenance_window_pressure", 0.0) > 0:
            checks.append("maintenance_window_check")
        if pressure.get("latency_pressure", 0.0) > 0:
            checks.append("actuator_latency_check")
        if hard_reasons:
            checks.append("manual_override_required_before_execution")
        return list(dict.fromkeys(checks))

    @staticmethod
    def _agent49_reward_patch(joint_evaluation: list[dict[str, object]]) -> list[dict[str, object]]:
        return [
            {
                "joint_action_id": str(row["joint_action_id"]),
                "engineering_constraint_penalty": row["engineering_constraint_penalty"],
                "execution_feasibility": row["execution_feasibility"],
                "hard_blocked_by_engineering": row["hard_blocked_by_engineering"],
                "hard_block_reasons": row["hard_block_reasons"],
                "arbitration_required_checks": row["arbitration_required_checks"],
            }
            for row in joint_evaluation
        ]

    def _action_constraint_patch(self, joint_evaluation: list[dict[str, object]]) -> dict[str, object]:
        by_joint = {str(row["joint_action_id"]): row for row in joint_evaluation}
        patch: dict[str, object] = {}
        for action_id, joint_ids in ACTION_PATCH_MAPPING.items():
            rows = [by_joint[joint_id] for joint_id in joint_ids if joint_id in by_joint]
            if not rows:
                continue
            max_penalty = max(float(row["engineering_constraint_penalty"]) for row in rows)
            mean_feasibility = sum(float(row["execution_feasibility"]) for row in rows) / len(rows)
            hard_rows = [row for row in rows if bool(row["hard_blocked_by_engineering"])]
            reasons: list[str] = []
            for row in hard_rows:
                reasons.extend([str(item) for item in row["hard_block_reasons"]])
            patch[action_id] = {
                "source_joint_actions": [str(row["joint_action_id"]) for row in rows],
                "engineering_penalty": round(max_penalty, 3),
                "execution_feasibility": round(mean_feasibility, 3),
                "hard_block": bool(hard_rows),
                "block_reasons": list(dict.fromkeys(reasons)),
            }
        return patch

    @staticmethod
    def _arbitration_patch(action_patch: dict[str, object], readiness: dict[str, object]) -> dict[str, object]:
        hard_blocked = [
            action_id
            for action_id, patch in action_patch.items()
            if isinstance(patch, dict) and bool(patch.get("hard_block", False))
        ]
        return {
            "blocked_action_ids": hard_blocked,
            "action_constraint_patch": action_patch,
            "can_patch_final_arbitration": True,
            "can_authorize_actuator_execution": bool(readiness["can_write_to_actuator"]),
            "release_gate_write_allowed": False,
            "field_boundary": "engineering patch can block or downgrade actions; field execution replay is required before automatic actuation.",
        }

    def _readiness(self, contract: dict[str, object], joint_evaluation: list[dict[str, object]]) -> dict[str, object]:
        count = max(1, len(joint_evaluation))
        feasibility_scores = [float(row["execution_feasibility"]) for row in joint_evaluation]
        hard_blocks = [row for row in joint_evaluation if bool(row["hard_blocked_by_engineering"])]
        mean_feasibility = sum(feasibility_scores) / count
        storage_violation_rate = sum(1 for row in joint_evaluation if float(row["constraint_pressure"]["storage_pressure"]) > 0.0) / count
        actuator_pressure = max(
            (
                max(float(row["constraint_pressure"]["switch_pressure"]), float(row["constraint_pressure"]["latency_pressure"]))
                for row in joint_evaluation
            ),
            default=0.0,
        )
        inventory_risk = max((float(row["constraint_pressure"]["chemical_inventory_pressure"]) for row in joint_evaluation), default=0.0)
        review_bottleneck = max((float(row["constraint_pressure"]["human_review_pressure"]) for row in joint_evaluation), default=0.0)
        field_ready = self._field_ready(contract)
        score = round(
            0.28 * mean_feasibility
            + 0.18 * (1.0 - len(hard_blocks) / count)
            + 0.14 * max(0.0, 1.0 - storage_violation_rate)
            + 0.12 * max(0.0, 1.0 - actuator_pressure)
            + 0.10 * max(0.0, 1.0 - inventory_risk)
            + 0.08 * max(0.0, 1.0 - review_bottleneck)
            + 0.10 * float(field_ready),
            3,
        )
        if field_ready and not hard_blocks:
            status = "field_engineering_execution_constraints_candidate_ready"
        elif joint_evaluation:
            status = "synthetic_engineering_constraints_reward_patch_ready_needs_plc_scada_and_field_replay"
        else:
            status = "engineering_constraints_contract_incomplete"
        return {
            "engineering_constraints_status": status,
            "engineering_constraints_score": score,
            "constraint_contract_score": 1.0 if joint_evaluation else 0.0,
            "reward_patch_coverage": round(len(joint_evaluation) / max(1, len(JOINT_ACTION_RESOURCE_PROFILES)), 3),
            "arbitration_patch_coverage": round(len(ACTION_PATCH_MAPPING) / 7, 3),
            "mean_execution_feasibility": round(mean_feasibility, 3),
            "hard_blocked_joint_action_count": len(hard_blocks),
            "storage_violation_rate": round(storage_violation_rate, 3),
            "actuator_switch_pressure": round(actuator_pressure, 3),
            "inventory_risk_score": round(inventory_risk, 3),
            "human_review_bottleneck_score": round(review_bottleneck, 3),
            "field_ready": field_ready,
            "can_update_agent49_reward_contract": bool(joint_evaluation),
            "can_patch_final_arbitration": bool(joint_evaluation),
            "can_write_to_actuator": field_ready and not hard_blocks,
            "can_write_to_release_gate": False,
            "next_recommended_core_action": "P6_reasonable_knowledge_graph_upgrade",
        }

    def _field_ready(self, contract: dict[str, object]) -> bool:
        constraints = contract["constraints"] if isinstance(contract["constraints"], dict) else {}
        return (
            self.data_origin == "field_execution_replay"
            and bool(self.engineering_profile.get("plc_scada_point_list_verified", False))
            and bool(self.engineering_profile.get("operator_sop_verified", False))
            and float(self.field_execution_validation.get("field_execution_replay_coverage", 0.0)) >= 0.85
            and float(self.field_execution_validation.get("actuator_success_rate", 0.0)) >= 0.95
            and float(self.field_execution_validation.get("actuator_p90_latency_min", 10**6))
            <= float(constraints.get("max_actuator_p90_latency_min", 0.0))
        )

    def _issues(self, readiness: dict[str, object], joint_evaluation: list[dict[str, object]]) -> list[QualityIssue]:
        issues: list[QualityIssue] = []
        if not readiness["field_ready"]:
            issues.append(
                QualityIssue(
                    sensor="engineering_execution_constraints",
                    issue_type="field_execution_replay_required",
                    severity=Severity.WARNING,
                    message="工程约束已能修正 reward 和仲裁候选，但缺 PLC/SCADA 点表、SOP 和现场执行 replay，不能写入真实执行器。",
                    evidence=readiness,
                )
            )
        for row in joint_evaluation:
            if bool(row["hard_blocked_by_engineering"]):
                issues.append(
                    QualityIssue(
                        sensor=str(row["joint_action_id"]),
                        issue_type="engineering_hard_block_for_joint_action",
                        severity=Severity.WARNING,
                        message="该联动动作触发工程硬约束，必须降级为人工复核或改选其他候选。",
                        evidence=row,
                    )
                )
        return issues

    @staticmethod
    def _recommendations(readiness: dict[str, object], joint_evaluation: list[dict[str, object]]) -> list[str]:
        recs = [
            "把池容、泵阀动作次数、执行器延迟、药剂库存、维护窗口、人工复核和误动作成本写入 Agent49 reward，而不是只写在说明里。",
            "最终仲裁阶段要消费同一份 action_constraint_patch；触发硬约束的动作只能进入人工复核或保护性候选，不能自动执行。",
            "采集 PLC/SCADA 点表、执行器响应日志、人工复核排队和药剂库存日志后，才能把该层从 synthetic patch 升级为现场执行候选。",
        ]
        worst = max(joint_evaluation, key=lambda row: float(row["engineering_constraint_penalty"])) if joint_evaluation else None
        if worst:
            recs.append(
                f"优先复核 `{worst['joint_action_id']}`：penalty={worst['engineering_constraint_penalty']}，hard_reasons={worst['hard_block_reasons']}。"
            )
        if readiness["field_ready"]:
            recs.append("现场执行 replay 通过后，可把该层作为 actuator policy 前的工程可行性门控。")
        return recs

    @staticmethod
    def _method_contract() -> dict[str, object]:
        return {
            "upgrade_id": "P7_engineering_constraints_in_reward_and_arbitration",
            "borrowed_from": [
                "Pyomo-style explicit variables, objectives and constraints",
                "WaterTAP-style unit costing and process-wide cost fields",
                "QSDsan-style TEA/LCA/system simulation boundaries",
                "EPANET/WNTR-style pump, valve, tank, hydraulic and water-quality operation constraints",
                "offline replay safety gate before policy actuation",
            ],
            "reality_mapping": "把工程可执行性从文字边界转成 reward 和仲裁可消费的约束补丁，覆盖池容、泵阀、药剂、维护、人工复核和误动作成本。",
            "data_needs": [
                "PLC_SCADA_point_list",
                "actuator_response_log",
                "buffer_storage_volume_timeseries",
                "chemical_inventory_log",
                "maintenance_window_schedule",
                "human_review_queue_log",
                "operator_override_and_false_positive_cost",
                "field_state_action_reward_replay",
            ],
            "implementation_path": [
                "src/water_ai/agents/engineering_execution_constraint_agent.py",
                "src/water_ai/agents/multi_facility_collaborative_control_agent.py",
                "src/water_ai/agents/cost_safety_agent.py",
                "src/water_ai/agents/arbitration_agent.py",
                "experiments/run_agent55_engineering_execution_constraints.py",
            ],
            "evaluation_metrics": [
                "constraint_contract_score",
                "reward_patch_coverage",
                "arbitration_patch_coverage",
                "mean_execution_feasibility",
                "storage_violation_rate",
                "actuator_switch_pressure",
                "inventory_risk_score",
                "human_review_bottleneck_score",
            ],
            "failure_boundary": "无 PLC/SCADA 点表、SOP 和现场执行 replay 时，只能改变候选排序和人工复核边界，不能授权执行器或放行门。",
        }

    @staticmethod
    def _agent50_writeback(readiness: dict[str, object]) -> dict[str, object]:
        return {
            "allowed_writeback": [
                "agent49_reward_constraint_patch",
                "cost_safety_engineering_penalty_patch",
                "arbitration_engineering_block_patch",
                "P7_completion_status_for_governance",
            ],
            "blocked_writeback": [
                "actuator_policy",
                "release_gate_policy",
                "field_execution_claim",
            ],
            "can_advance_governance_priority": bool(readiness["can_update_agent49_reward_contract"]),
            "policy_effect": (
                "move_to_P6_reasonable_knowledge_graph_upgrade"
                if readiness["can_update_agent49_reward_contract"]
                else "keep_P7_until_engineering_constraint_contract_is_complete"
            ),
        }

    def _number(self, key: str, default: float = 0.0) -> float:
        value = self.engineering_profile.get(key, default)
        return float(value) if isinstance(value, int | float) else default

    @staticmethod
    def _clip(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
        return max(lo, min(hi, value))

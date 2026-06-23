from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ControlReplayCounterfactualStress:
    """Counterfactual stress layer for Agent49/52 collaborative control replay."""

    collaborative_control_metrics: dict[str, Any]
    replay_evaluation_metrics: dict[str, Any]
    observation_contract_metrics: dict[str, Any]
    data_origin: str = "synthetic_counterfactual_replay"

    def build(self) -> dict[str, Any]:
        replay_table = self._replay_table()
        stress_table = self._stress_table(replay_table)
        metrics = self._stress_metrics(stress_table)
        readiness = self._readiness(metrics)
        return {
            "method_contract": self._method_contract(),
            "stress_table": stress_table,
            "counterfactual_metrics": metrics,
            "reward_prior_patch": self._reward_prior_patch(stress_table, metrics),
            "field_replay_requirements": self._field_replay_requirements(),
            "readiness": readiness,
            "writeback_policy": self._writeback_policy(readiness),
            "next_refactor_action": self._next_refactor_action(readiness),
        }

    @staticmethod
    def _method_contract() -> dict[str, Any]:
        return {
            "upgrade_id": "R3_agent49_replay_counterfactual_stress",
            "borrowed_from": [
                "offline policy evaluation stress cases",
                "counterfactual action replay before online deployment",
                "protective-control false-positive cost audit",
                "decision-tree policy guardrail review",
            ],
            "reality_mapping": (
                "把 Agent52 的 replay-ready schema 升级为反事实压力测试：比较 base policy、"
                "R2 observation-contract-aware policy 和 R3 reward-guardrail candidate。"
            ),
            "data_needs": [
                "Agent49 joint_action_matrix and reward contract",
                "Agent52 replay_table and reward_by_action",
                "R2 observation contract with weak-state improvement",
                "field multi-node state-action-reward replay before any actuator promotion",
            ],
            "evaluation_metrics": [
                "baseline_joint_action_accuracy",
                "observation_contract_accuracy",
                "guardrail_candidate_accuracy",
                "p95_reward_regret_delta",
                "protective_false_positive_cost_delta",
                "unsafe_action_block_correction_rate",
            ],
            "failure_boundary": (
                "counterfactual stress can update reward priors and replay case suites, but synthetic corrections are not proof of field control safety."
            ),
        }

    def _stress_table(self, replay_table: list[dict[str, Any]]) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for row in replay_table:
            baseline_action = str(row["policy_action_id"])
            expert_action = str(row["expert_action_id"])
            observation_action = self._observation_contract_action(row, baseline_action)
            guardrail_action = self._guardrail_action(row, observation_action)
            rows.append(
                {
                    "case_id": row["batch_id"],
                    "scenario": row["scenario"],
                    "expert_action_id": expert_action,
                    "baseline_policy_action_id": baseline_action,
                    "observation_contract_action_id": observation_action,
                    "guardrail_candidate_action_id": guardrail_action,
                    "baseline_reward_regret": self._regret(row, baseline_action),
                    "observation_contract_reward_regret": self._regret(row, observation_action),
                    "guardrail_reward_regret": self._regret(row, guardrail_action),
                    "baseline_false_positive_cost": self._false_positive_cost(row, baseline_action),
                    "observation_contract_false_positive_cost": self._false_positive_cost(row, observation_action),
                    "guardrail_false_positive_cost": self._false_positive_cost(row, guardrail_action),
                    "unsafe_action_blocked": bool(row.get("unsafe_action_blocked", False)),
                    "stress_resolution": self._stress_resolution(row, observation_action, guardrail_action),
                    "residual_boundary": self._residual_boundary(row),
                }
            )
        return rows

    def _observation_contract_action(self, row: dict[str, Any], baseline_action: str) -> str:
        scenario = str(row.get("scenario", ""))
        if self._observation_contract_ready() and scenario == "catalyst_uncertain_low_proxy":
            return "J4_safe_low_cost_standby"
        return baseline_action

    @staticmethod
    def _guardrail_action(row: dict[str, Any], observation_action: str) -> str:
        scenario = str(row.get("scenario", ""))
        if scenario == "hydraulic_delay_violation" or bool(row.get("unsafe_action_blocked", False)):
            return "J3_polishing_and_release_gate"
        if scenario == "catalyst_uncertain_low_proxy":
            return "J4_safe_low_cost_standby"
        return observation_action

    @staticmethod
    def _stress_resolution(row: dict[str, Any], observation_action: str, guardrail_action: str) -> str:
        baseline_action = str(row["policy_action_id"])
        expert_action = str(row["expert_action_id"])
        if guardrail_action == expert_action and baseline_action != expert_action:
            return "resolved_by_R3_guardrail_candidate"
        if observation_action == expert_action and baseline_action != expert_action:
            return "resolved_by_R2_observation_contract"
        if baseline_action == expert_action:
            return "baseline_already_matches_expert"
        return "unresolved_needs_field_replay_or_reward_redesign"

    @staticmethod
    def _residual_boundary(row: dict[str, Any]) -> str:
        scenario = str(row.get("scenario", ""))
        if scenario == "catalyst_uncertain_low_proxy":
            return "needs field proxy labels before relaxing catalyst uncertainty block"
        if scenario == "hydraulic_delay_violation":
            return "needs tank storage, actuator latency and operation replay before recycle promotion"
        if scenario == "polishing_release_risk":
            return "needs lab label and release gate evidence before any release action"
        return "synthetic replay case; field replay required before policy promotion"

    def _stress_metrics(self, stress_table: list[dict[str, Any]]) -> dict[str, Any]:
        baseline = self._policy_metrics(stress_table, "baseline_policy_action_id", "baseline_reward_regret", "baseline_false_positive_cost")
        observation = self._policy_metrics(
            stress_table,
            "observation_contract_action_id",
            "observation_contract_reward_regret",
            "observation_contract_false_positive_cost",
        )
        guardrail = self._policy_metrics(
            stress_table,
            "guardrail_candidate_action_id",
            "guardrail_reward_regret",
            "guardrail_false_positive_cost",
        )
        return {
            "stress_case_count": len(stress_table),
            "baseline": baseline,
            "observation_contract": observation,
            "guardrail_candidate": guardrail,
            "accuracy_gain_observation_contract": round(observation["joint_action_accuracy"] - baseline["joint_action_accuracy"], 3),
            "accuracy_gain_guardrail": round(guardrail["joint_action_accuracy"] - baseline["joint_action_accuracy"], 3),
            "p95_reward_regret_delta_guardrail": round(baseline["p95_reward_regret"] - guardrail["p95_reward_regret"], 3),
            "protective_false_positive_cost_delta_guardrail": round(
                baseline["mean_false_positive_cost"] - guardrail["mean_false_positive_cost"],
                3,
            ),
            "unsafe_action_block_correction_rate": self._unsafe_correction_rate(stress_table),
            "field_replay_coverage": float(self._offline_metrics().get("field_replay_coverage", 0.0)),
            "data_origin": self.data_origin,
        }

    @staticmethod
    def _policy_metrics(
        stress_table: list[dict[str, Any]],
        action_key: str,
        regret_key: str,
        false_positive_key: str,
    ) -> dict[str, float]:
        count = max(1, len(stress_table))
        accuracy = sum(1 for row in stress_table if row[action_key] == row["expert_action_id"]) / count
        regrets = [float(row[regret_key]) for row in stress_table]
        false_costs = [float(row[false_positive_key]) for row in stress_table if float(row[false_positive_key]) > 0]
        false_positive_count = len(false_costs)
        return {
            "joint_action_accuracy": round(accuracy, 3),
            "mean_reward_regret": round(sum(regrets) / count, 3),
            "p95_reward_regret": ControlReplayCounterfactualStress._percentile(regrets, 0.95),
            "protective_false_positive_rate": round(false_positive_count / count, 3),
            "mean_false_positive_cost": round(sum(false_costs) / max(1, false_positive_count), 3),
        }

    @staticmethod
    def _unsafe_correction_rate(stress_table: list[dict[str, Any]]) -> float:
        unsafe = [row for row in stress_table if row["unsafe_action_blocked"]]
        if not unsafe:
            return 1.0
        corrected = [row for row in unsafe if row["guardrail_candidate_action_id"] == row["expert_action_id"]]
        return round(len(corrected) / len(unsafe), 3)

    def _readiness(self, metrics: dict[str, Any]) -> dict[str, Any]:
        guardrail = metrics["guardrail_candidate"]
        field_ready = float(metrics["field_replay_coverage"]) >= 0.85 and self.data_origin == "field_counterfactual_replay"
        stress_ready = (
            int(metrics["stress_case_count"]) >= 6
            and float(metrics["accuracy_gain_guardrail"]) > 0.0
            and float(guardrail["joint_action_accuracy"]) >= 0.90
        )
        score = round(
            0.18 * float(stress_ready)
            + 0.20 * float(guardrail["joint_action_accuracy"])
            + 0.16 * max(0.0, 1.0 - float(guardrail["p95_reward_regret"]) / 0.14)
            + 0.16 * max(0.0, 1.0 - float(guardrail["mean_false_positive_cost"]) / 0.14)
            + 0.12 * float(metrics["unsafe_action_block_correction_rate"])
            + 0.18 * float(field_ready),
            3,
        )
        status = (
            "field_counterfactual_replay_candidate_ready"
            if field_ready and stress_ready
            else "synthetic_counterfactual_stress_ready_needs_field_replay"
        )
        return {
            "control_replay_stress_status": status,
            "control_replay_stress_score": score,
            "stress_ready": stress_ready,
            "field_ready": field_ready,
            "can_update_agent49_reward_prior": stress_ready,
            "can_update_agent52_stress_suite": stress_ready,
            "can_train_offline_rl": field_ready,
            "can_write_to_actuator": False,
            "can_write_to_release_gate": False,
        }

    @staticmethod
    def _writeback_policy(readiness: dict[str, Any]) -> dict[str, Any]:
        return {
            "allowed_writeback": [
                "agent49_reward_prior_guardrail_candidate",
                "agent52_counterfactual_stress_suite",
                "architecture_consolidation_R3_status",
            ]
            if readiness["stress_ready"]
            else ["agent52_counterfactual_stress_suite"],
            "blocked_writeback": [
                "actuator_policy",
                "release_gate_policy",
                "online_MARL_training",
                "field_control_effectiveness_claim",
            ],
            "can_write_to_actuator": False,
            "can_write_to_release_gate": False,
            "policy_effect": "R3 can patch reward priors and stress suites only; field replay remains required.",
        }

    def _reward_prior_patch(self, stress_table: list[dict[str, Any]], metrics: dict[str, Any]) -> dict[str, Any]:
        return {
            "patch_id": "R3_counterfactual_guardrail_reward_prior",
            "target_agent": "multi_facility_collaborative_control_agent",
            "triggered_by_cases": [
                {
                    "case_id": row["case_id"],
                    "scenario": row["scenario"],
                    "baseline_action": row["baseline_policy_action_id"],
                    "guardrail_action": row["guardrail_candidate_action_id"],
                    "stress_resolution": row["stress_resolution"],
                }
                for row in stress_table
                if row["stress_resolution"].startswith("resolved")
            ],
            "candidate_rules": [
                {
                    "rule_id": "R3G1_catalyst_uncertain_requires_standby_or_human_review",
                    "if": "catalyst proxy is not field validated and catalyst action would be protective/regeneration",
                    "then": "prefer J4_safe_low_cost_standby or human-reviewed catalyst protection",
                    "expected_effect": "reduce protective false-positive cost from baseline replay cases",
                },
                {
                    "rule_id": "R3G2_hydraulic_delay_unknown_blocks_recycle",
                    "if": "tank storage margin or actuator latency evidence is missing",
                    "then": "prefer J3_polishing_and_release_gate over recycle escalation",
                    "expected_effect": "reduce high-regret unsafe recycle actions under delayed evidence",
                },
            ],
            "metric_delta": {
                "accuracy_gain_guardrail": metrics["accuracy_gain_guardrail"],
                "p95_reward_regret_delta_guardrail": metrics["p95_reward_regret_delta_guardrail"],
                "protective_false_positive_cost_delta_guardrail": metrics[
                    "protective_false_positive_cost_delta_guardrail"
                ],
            },
            "field_boundary": "reward prior patch is synthetic until field replay reproduces these stress improvements.",
        }

    @staticmethod
    def _field_replay_requirements() -> list[dict[str, Any]]:
        return [
            {
                "requirement_id": "R3_FV1_state_action_reward_replay",
                "needed_for": "control stress validation",
                "required_fields": [
                    "facility_state_vector",
                    "policy_action_id",
                    "operator_or_expert_action_id",
                    "reward_by_action",
                    "next_state_summary",
                ],
            },
            {
                "requirement_id": "R3_FV2_hydraulic_execution_replay",
                "needed_for": "recycle and hold action safety",
                "required_fields": ["tank_storage_margin", "actuator_latency_p90", "pump_valve_result"],
            },
            {
                "requirement_id": "R3_FV3_catalyst_action_replay",
                "needed_for": "catalyst protection false-positive cost",
                "required_fields": ["proxy_holdout_label", "pressure_drop_kPa", "regeneration_event", "operator_override"],
            },
        ]

    @staticmethod
    def _next_refactor_action(readiness: dict[str, Any]) -> dict[str, Any]:
        if readiness["stress_ready"]:
            return {
                "action_id": "R3b_agent49_reward_prior_patch_from_counterfactual_stress",
                "title": "把 R3 反事实压力结果写成 Agent49 reward prior guardrails",
                "reason": "R3 stress 已暴露并修复 synthetic 高 regret/误保护场景；下一步应把规则补丁接入 Agent49 reward prior，但仍不写执行器。",
                "must_not_do": "不能把 synthetic stress improvement 当作现场控制有效性。",
            }
        return {
            "action_id": "R3_continue_counterfactual_stress_case_design",
            "title": "继续补控制 replay 反事实压力样例",
            "reason": "stress suite 尚不足以形成 reward prior patch。",
            "must_not_do": "不能跳过 replay 指标直接调控制策略。",
        }

    def _observation_contract_ready(self) -> bool:
        readiness = self.observation_contract_metrics.get("readiness", {})
        readiness = readiness if isinstance(readiness, dict) else {}
        return bool(readiness.get("budget_pass", False)) and float(
            readiness.get("proxy_enhanced_weak_state_coverage", 0.0)
        ) >= 0.55

    def _replay_table(self) -> list[dict[str, Any]]:
        table = self.replay_evaluation_metrics.get("replay_table", [])
        return table if isinstance(table, list) else []

    def _offline_metrics(self) -> dict[str, Any]:
        metrics = self.replay_evaluation_metrics.get("offline_evaluation_metrics", {})
        return metrics if isinstance(metrics, dict) else {}

    @staticmethod
    def _regret(row: dict[str, Any], action_id: str) -> float:
        reward_by_action = row.get("reward_by_action", {})
        reward_by_action = reward_by_action if isinstance(reward_by_action, dict) else {}
        expert_reward = float(row.get("expert_reward", reward_by_action.get(row.get("expert_action_id"), 0.0)))
        action_reward = float(reward_by_action.get(action_id, 0.0))
        return round(max(0.0, expert_reward - action_reward), 3)

    @staticmethod
    def _false_positive_cost(row: dict[str, Any], action_id: str) -> float:
        if action_id == row.get("expert_action_id"):
            return 0.0
        if bool(row.get("is_false_positive_protective_action", False)) and action_id == row.get("policy_action_id"):
            return float(row.get("false_positive_action_cost", 0.0))
        if str(row.get("scenario", "")) == "catalyst_uncertain_low_proxy" and action_id == "J2_catalyst_protection_before_regeneration":
            return float(row.get("false_positive_action_cost", 0.18))
        return 0.0

    @staticmethod
    def _percentile(values: list[float], q: float) -> float:
        if not values:
            return 0.0
        ordered = sorted(values)
        index = min(len(ordered) - 1, max(0, round((len(ordered) - 1) * q)))
        return round(ordered[index], 3)

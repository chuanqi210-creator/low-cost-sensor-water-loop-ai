from __future__ import annotations

from collections.abc import Sequence

from water_ai.agents.base import BaseAgent
from water_ai.domain import AgentReport, QualityIssue, SensorReading, Severity


REPLAY_REQUIRED_FIELDS = [
    "batch_id",
    "timestamp_min",
    "scenario",
    "facility_state_vector",
    "available_node_modalities",
    "missingness_mask",
    "policy_action_id",
    "expert_action_id",
    "reward_by_action",
    "observed_reward",
    "next_state_summary",
    "lab_label",
    "operator_override",
    "catalyst_proxy_summary_status",
    "catalyst_proxy_validation_pass",
    "catalyst_proxy_scoreable_batch_count",
    "pressure_headloss_candidate_pool_status",
    "pressure_headloss_candidate_ids",
    "pressure_headloss_control_boundary",
    "pressure_source_conflict_count",
    "resolved_pressure_source_conflict_count",
    "unresolved_pressure_source_conflict_count",
    "pressure_source_resolution_record_count",
    "pressure_source_conflict_requires_operator_review",
    "data_origin",
]


class MultiFacilityReplayEvaluationAgent(BaseAgent):
    """Build and evaluate replay-ready offline checks for Agent49."""

    name = "multi_facility_replay_evaluation_agent"

    def __init__(
        self,
        *,
        collaborative_control_metrics: dict[str, object] | None = None,
        catalyst_proxy_metrics: dict[str, object] | None = None,
        replay_cases: list[dict[str, object]] | None = None,
        data_origin: str = "synthetic_replay_design",
        field_validation: dict[str, float] | None = None,
        min_case_count: int = 5,
        min_field_replay_coverage: float = 0.85,
        min_joint_action_accuracy: float = 0.90,
        max_reward_regret: float = 0.08,
        max_false_positive_cost: float = 0.14,
    ) -> None:
        self.collaborative_control_metrics = collaborative_control_metrics or {}
        self.catalyst_proxy_metrics = catalyst_proxy_metrics or {}
        self.data_origin = data_origin
        self.field_validation = field_validation or {}
        self.min_case_count = min_case_count
        self.min_field_replay_coverage = min_field_replay_coverage
        self.min_joint_action_accuracy = min_joint_action_accuracy
        self.max_reward_regret = max_reward_regret
        self.max_false_positive_cost = max_false_positive_cost
        self.replay_cases = replay_cases or self._default_replay_cases()

    def run(self, readings: Sequence[SensorReading]) -> AgentReport:
        del readings
        method_contract = self._method_contract()
        replay_schema = self._replay_schema()
        replay_table = self._replay_table()
        offline_metrics = self._offline_metrics(replay_table)
        control_policy_comparison = self._control_policy_comparison(replay_table)
        control_baseline_contract = self._control_baseline_contract(control_policy_comparison, offline_metrics)
        offline_metrics["control_policy_baseline_strategy_count"] = control_policy_comparison["strategy_count"]
        offline_metrics["control_policy_baseline_comparison_status"] = control_policy_comparison["comparison_status"]
        reward_diagnostics = self._reward_diagnostics(replay_table)
        distillation_eval = self._distillation_eval(replay_table, offline_metrics)
        catalyst_proxy_context = self._catalyst_proxy_context()
        pressure_headloss_context = self._pressure_headloss_context()
        readiness = self._readiness(offline_metrics, distillation_eval)
        agent49_writeback = self._agent49_writeback(readiness, offline_metrics)
        issues = self._issues(offline_metrics, distillation_eval, readiness)
        recommendations = self._recommendations(readiness, offline_metrics, reward_diagnostics)
        summary = (
            f"多设施 replay 离线评估：{readiness['replay_evaluation_status']}；"
            f"synthetic joint_action_accuracy={offline_metrics['joint_action_accuracy']:.3f}，"
            f"mean_reward_regret={offline_metrics['mean_reward_regret']:.3f}。"
        )
        confidence = round(
            min(0.91, max(0.20, 0.34 + 0.40 * readiness["replay_evaluation_score"] - 0.035 * len(issues))),
            3,
        )
        return AgentReport(
            agent_name=self.name,
            confidence=confidence,
            summary=summary,
            issues=issues,
            recommendations=recommendations,
            metrics={
                "method_contract": method_contract,
                "replay_schema": replay_schema,
                "replay_table": replay_table,
                "offline_evaluation_metrics": offline_metrics,
                "control_policy_comparison": control_policy_comparison,
                "control_baseline_contract": control_baseline_contract,
                "reward_diagnostics": reward_diagnostics,
                "distillation_evaluation": distillation_eval,
                "catalyst_proxy_context": catalyst_proxy_context,
                "pressure_headloss_context": pressure_headloss_context,
                "readiness": readiness,
                "agent49_writeback": agent49_writeback,
            },
        )

    def _replay_schema(self) -> dict[str, object]:
        return {
            "schema_id": "multi_facility_state_action_reward_replay_v1",
            "required_fields": REPLAY_REQUIRED_FIELDS,
            "join_keys": ["batch_id", "timestamp_min", "facility_agent_id", "joint_action_id"],
            "state_contract": [
                "facility_state_vector from Agent49",
                "Agent48 node-modality layout id and missingness mask",
                "Agent51 catalyst proxy status and proxy observability",
                "Agent51 field_proxy_holdout_summary status, scoreable batch count, MAE and correlation",
                "Agent49 pressure/headloss candidate control boundary from R8c",
                "field lab label window when available",
            ],
            "action_contract": [
                "policy_action_id generated by Agent49 rule/tree candidate",
                "guardrail_aware_policy_action_id generated after R3b reward-prior guardrails",
                "expert_action_id from operator or validated historical control",
                "action_was_executed and actuator_result for field replay",
            ],
            "reward_contract": [
                "quality_reward",
                "risk_reduction_reward",
                "latency_reward",
                "field_evidence_bonus",
                "cost_energy_efficiency",
                "false_positive_action_cost",
                "unsafe_action_penalty",
            ],
            "offline_metrics": [
                "joint_action_accuracy",
                "mean_reward_regret",
                "p95_reward_regret",
                "protective_false_positive_rate",
                "false_positive_action_cost",
                "distilled_policy_replay_accuracy",
                "guardrail_aware_joint_action_accuracy",
                "guardrail_aware_mean_reward_regret",
                "guardrail_aware_false_positive_action_cost",
                "pressure_headloss_boundary_consumed",
                "pressure_headloss_blocked_guardrail_case_count",
                "pressure_source_conflict_replay_blocked_case_count",
                "field_replay_coverage",
                "control_policy_baseline_strategy_count",
                "control_policy_baseline_comparison_status",
            ],
            "field_boundary": "synthetic replay only validates schema and metric plumbing; field replay is required before actuator or release-gate writeback.",
        }

    def _replay_table(self) -> list[dict[str, object]]:
        rows: list[dict[str, object]] = []
        catalyst_context = self._catalyst_proxy_context()
        pressure_context = self._pressure_headloss_context()
        for case in self.replay_cases:
            reward_by_action = self._reward_by_action(case)
            policy_action = str(case["policy_action_id"])
            expert_action = str(case["expert_action_id"])
            guardrail_action = self._guardrail_aware_policy_action(case, policy_action)
            expert_reward = float(reward_by_action.get(expert_action, 0.0))
            policy_reward = float(reward_by_action.get(policy_action, 0.0))
            guardrail_reward = float(reward_by_action.get(guardrail_action, 0.0))
            rows.append(
                {
                    "batch_id": str(case["batch_id"]),
                    "timestamp_min": int(case["timestamp_min"]),
                    "scenario": str(case["scenario"]),
                    "facility_state_vector": self._facility_state_vector(case),
                    "available_node_modalities": self._available_node_modalities(),
                    "missingness_mask": case["missingness_mask"],
                    "policy_action_id": policy_action,
                    "guardrail_aware_policy_action_id": guardrail_action,
                    "expert_action_id": expert_action,
                    "reward_by_action": {key: round(float(value), 3) for key, value in reward_by_action.items()},
                    "observed_reward": round(policy_reward, 3),
                    "guardrail_aware_observed_reward": round(guardrail_reward, 3),
                    "expert_reward": round(expert_reward, 3),
                    "reward_regret": round(max(0.0, expert_reward - policy_reward), 3),
                    "guardrail_aware_reward_regret": round(max(0.0, expert_reward - guardrail_reward), 3),
                    "is_correct_action": policy_action == expert_action,
                    "guardrail_aware_is_correct_action": guardrail_action == expert_action,
                    "is_protective_action": policy_action in {"J0_matrix_shock_equalize_and_recycle", "J2_catalyst_protection_before_regeneration", "J4_safe_low_cost_standby"},
                    "is_false_positive_protective_action": bool(case.get("false_positive_if_policy", False)),
                    "false_positive_action_cost": round(float(case.get("false_positive_action_cost", 0.0)), 3),
                    "guardrail_aware_false_positive_action_cost": self._false_positive_action_cost(
                        case,
                        guardrail_action,
                        policy_action,
                        expert_action,
                    ),
                    "guardrail_source_rule_id": self._guardrail_source_rule_id(case, guardrail_action, policy_action),
                    "unsafe_action_blocked": bool(case.get("unsafe_action_blocked", False)),
                    "next_state_summary": case["next_state_summary"],
                    "lab_label": case["lab_label"],
                    "operator_override": bool(case.get("operator_override", False)),
                    "catalyst_proxy_summary_status": catalyst_context["summary_status"],
                    "catalyst_proxy_validation_pass": catalyst_context["field_validation_pass"],
                    "catalyst_proxy_scoreable_batch_count": catalyst_context["scoreable_batch_count"],
                    "pressure_headloss_candidate_pool_status": pressure_context["pool_status"],
                    "pressure_headloss_candidate_ids": pressure_context["candidate_ids"],
            "pressure_headloss_boundary_consumed": pressure_context["consumed_by_agent52"],
            "pressure_headloss_can_relax_control_guardrail": pressure_context[
                "can_relax_hydraulic_or_catalyst_guardrail"
                    ],
                    "pressure_headloss_control_boundary": pressure_context["control_boundary"],
                    "pressure_source_conflict_count": pressure_context["pressure_source_conflict_count"],
                    "resolved_pressure_source_conflict_count": pressure_context[
                        "resolved_pressure_source_conflict_count"
                    ],
                    "unresolved_pressure_source_conflict_count": pressure_context[
                        "unresolved_pressure_source_conflict_count"
                    ],
                    "pressure_source_resolution_record_count": pressure_context[
                        "pressure_source_resolution_record_count"
                    ],
                    "pressure_source_conflict_requires_operator_review": pressure_context[
                        "conflict_requires_operator_review"
                    ],
                    "pressure_source_conflict_control_block": pressure_context["pressure_source_conflict_control_block"],
                    "data_origin": self.data_origin,
                }
            )
        return rows

    def _offline_metrics(self, replay_table: list[dict[str, object]]) -> dict[str, object]:
        count = len(replay_table)
        correct = sum(1 for row in replay_table if row["is_correct_action"])
        guardrail_correct = sum(1 for row in replay_table if row["guardrail_aware_is_correct_action"])
        regrets = [float(row["reward_regret"]) for row in replay_table]
        guardrail_regrets = [float(row["guardrail_aware_reward_regret"]) for row in replay_table]
        false_positive_rows = [row for row in replay_table if row["is_false_positive_protective_action"]]
        guardrail_false_positive_rows = [
            row for row in replay_table if float(row["guardrail_aware_false_positive_action_cost"]) > 0.0
        ]
        pressure_context = self._pressure_headloss_context()
        pressure_blocked_rows = [
            row
            for row in replay_table
            if bool(pressure_context["consumed_by_agent52"])
            and row["guardrail_source_rule_id"] in {
                "R3G1_catalyst_uncertain_requires_standby_or_human_review",
                "R3G2_hydraulic_delay_unknown_blocks_recycle",
            }
        ]
        pressure_conflict_rows = [
            row
            for row in replay_table
            if bool(pressure_context["conflict_requires_operator_review"])
            and (
                row["scenario"] in {"catalyst_uncertain_low_proxy", "hydraulic_delay_violation"}
                or row["policy_action_id"]
                in {"J0_matrix_shock_equalize_and_recycle", "J2_catalyst_protection_before_regeneration"}
            )
        ]
        unsafe_blocked = sum(1 for row in replay_table if row["unsafe_action_blocked"])
        synthetic_accuracy = correct / max(1, count)
        guardrail_accuracy = guardrail_correct / max(1, count)
        field_coverage = float(self.field_validation.get("field_replay_coverage", 0.0))
        joint_accuracy = float(self.field_validation.get("joint_action_accuracy", synthetic_accuracy))
        reward_regret = float(self.field_validation.get("reward_regret", sum(regrets) / max(1, count)))
        false_positive_cost = float(
            self.field_validation.get(
                "false_positive_action_cost",
                sum(float(row["false_positive_action_cost"]) for row in false_positive_rows) / max(1, len(false_positive_rows)),
            )
        )
        return {
            "replay_case_count": count,
            "synthetic_joint_action_accuracy": round(synthetic_accuracy, 3),
            "joint_action_accuracy": round(joint_accuracy, 3),
            "mean_reward_regret": round(reward_regret, 3),
            "p95_reward_regret": self._percentile(regrets, 0.95),
            "protective_false_positive_rate": round(len(false_positive_rows) / max(1, count), 3),
            "false_positive_action_cost": round(false_positive_cost, 3),
            "guardrail_aware_joint_action_accuracy": round(guardrail_accuracy, 3),
            "guardrail_aware_mean_reward_regret": round(sum(guardrail_regrets) / max(1, count), 3),
            "guardrail_aware_p95_reward_regret": self._percentile(guardrail_regrets, 0.95),
            "guardrail_aware_protective_false_positive_rate": round(len(guardrail_false_positive_rows) / max(1, count), 3),
            "guardrail_aware_false_positive_action_cost": round(
                sum(float(row["guardrail_aware_false_positive_action_cost"]) for row in guardrail_false_positive_rows)
                / max(1, len(guardrail_false_positive_rows)),
                3,
            ),
            "guardrail_aware_accuracy_gain": round(guardrail_accuracy - synthetic_accuracy, 3),
            "guardrail_aware_regret_delta": round(
                (sum(regrets) / max(1, count)) - (sum(guardrail_regrets) / max(1, count)),
                3,
            ),
            "unsafe_action_block_rate": round(unsafe_blocked / max(1, count), 3),
            "field_replay_coverage": round(field_coverage, 3),
            "synthetic_replay_coverage": round(count / max(self.min_case_count, count), 3),
            "candidate_action_count": len(self._candidate_action_ids()),
                "control_replay_guardrails_integrated": self._control_replay_guardrail_available(),
                "catalyst_proxy_summary_status": self._catalyst_proxy_context()["summary_status"],
                "catalyst_proxy_ready_for_agent51_validation": self._catalyst_proxy_context()["ready_for_agent51_validation"],
                "catalyst_proxy_field_validation_pass": self._catalyst_proxy_context()["field_validation_pass"],
                "catalyst_proxy_scoreable_batch_count": self._catalyst_proxy_context()["scoreable_batch_count"],
                "catalyst_proxy_matched_batch_count": self._catalyst_proxy_context()["matched_batch_count"],
                "catalyst_proxy_holdout_mae": self._catalyst_proxy_context()["holdout_mae"],
                "catalyst_proxy_label_correlation": self._catalyst_proxy_context()["proxy_label_correlation"],
                "catalyst_guardrail_mode": self._catalyst_proxy_context()["guardrail_mode"],
                "pressure_headloss_boundary_consumed": pressure_context["consumed_by_agent52"],
                "pressure_headloss_candidate_pool_status": pressure_context["pool_status"],
                "pressure_headloss_candidate_count": pressure_context["candidate_count"],
                "pressure_headloss_candidate_ids": pressure_context["candidate_ids"],
                "pressure_headloss_can_relax_control_guardrail": pressure_context[
                    "can_relax_hydraulic_or_catalyst_guardrail"
                ],
                "pressure_headloss_blocked_guardrail_case_count": len(pressure_blocked_rows),
                "pressure_headloss_field_validation_required": pressure_context["field_validation_required"],
                "pressure_source_conflict_count": pressure_context["pressure_source_conflict_count"],
                "resolved_pressure_source_conflict_count": pressure_context[
                    "resolved_pressure_source_conflict_count"
                ],
                "unresolved_pressure_source_conflict_count": pressure_context[
                    "unresolved_pressure_source_conflict_count"
                ],
                "pressure_source_resolution_record_count": pressure_context[
                    "pressure_source_resolution_record_count"
                ],
                "pressure_source_conflict_requires_operator_review": pressure_context[
                    "conflict_requires_operator_review"
                ],
                "pressure_source_conflict_replay_blocked_case_count": len(pressure_conflict_rows),
                "pressure_source_conflict_control_block": pressure_context["pressure_source_conflict_control_block"],
                "data_origin": self.data_origin,
            }

    def _control_policy_comparison(self, replay_table: list[dict[str, object]]) -> dict[str, object]:
        strategy_order = [
            "agent49_policy",
            "guardrail_aware_policy",
            "safe_standby_rule",
            "release_first_rule",
            "deterministic_random_action_baseline",
            "expert_upper_bound",
        ]
        strategy_descriptions = {
            "agent49_policy": "Agent49 原始候选协同动作，用作当前模型控制 baseline。",
            "guardrail_aware_policy": "Agent49 动作经过催化剂/水力/冲突保护规则后的保护性候选策略。",
            "safe_standby_rule": "保守待机规则，用于衡量过度保守的收益损失和保护边界。",
            "release_first_rule": "优先进入 polishing/release gate 的压力测试 baseline，用于暴露误放行/误晋级风险。",
            "deterministic_random_action_baseline": "固定随机动作 baseline，用于检查策略是否仅靠候选动作分布偶然变好。",
            "expert_upper_bound": "operator/validated expert action 上界，用于标定 replay 表可达到的最佳离线表现。",
        }
        metrics_by_strategy = {
            strategy_id: self._control_strategy_metrics(strategy_id, replay_table)
            for strategy_id in strategy_order
        }
        baseline = metrics_by_strategy["agent49_policy"]
        guardrail = metrics_by_strategy["guardrail_aware_policy"]
        release_first = metrics_by_strategy["release_first_rule"]
        safe_standby = metrics_by_strategy["safe_standby_rule"]
        random_policy = metrics_by_strategy["deterministic_random_action_baseline"]
        field_ready = self.data_origin == "field_coordination_replay" and float(
            self.field_validation.get("field_replay_coverage", 0.0)
        ) >= self.min_field_replay_coverage
        return {
            "comparison_status": (
                "field_control_policy_baseline_comparison_ready_needs_operator_review"
                if field_ready
                else "synthetic_control_policy_baseline_comparison_ready_needs_field_replay"
            ),
            "strategy_count": len(strategy_order),
            "strategy_order": strategy_order,
            "strategy_descriptions": strategy_descriptions,
            "metrics_by_strategy": metrics_by_strategy,
            "delta_summary": {
                "guardrail_vs_agent49_accuracy_gain": round(
                    float(guardrail["joint_action_accuracy"]) - float(baseline["joint_action_accuracy"]),
                    3,
                ),
                "guardrail_vs_agent49_mean_regret_delta": round(
                    float(baseline["mean_reward_regret"]) - float(guardrail["mean_reward_regret"]),
                    3,
                ),
                "guardrail_vs_agent49_false_positive_cost_delta": round(
                    float(baseline["false_positive_action_cost"]) - float(guardrail["false_positive_action_cost"]),
                    3,
                ),
                "guardrail_vs_release_first_mismatch_delta": round(
                    float(release_first["action_mismatch_rate"]) - float(guardrail["action_mismatch_rate"]),
                    3,
                ),
                "guardrail_vs_safe_standby_mean_reward_delta": round(
                    float(guardrail["mean_observed_reward"]) - float(safe_standby["mean_observed_reward"]),
                    3,
                ),
                "guardrail_vs_random_regret_delta": round(
                    float(random_policy["mean_reward_regret"]) - float(guardrail["mean_reward_regret"]),
                    3,
                ),
            },
            "claim_scope_use": [
                "用于说明多智能体策略不是直接上线控制，而是在同一 state-action-reward replay 表内与保守、放行优先、随机和专家上界对照。",
                "用于专利/论文中的实施例指标：accuracy、regret、保护性误触发成本、误放行代理风险、unsafe action block。",
                "只能证明 replay 对照机制可运行；synthetic 对照不能证明现场控制效果。",
            ],
            "field_boundary": (
                "control policy comparison can update reward-prior and experiment design only; "
                "field replay, operator review, release validation, and actuator interlock remain required."
            ),
        }

    def _control_strategy_metrics(
        self,
        strategy_id: str,
        replay_table: list[dict[str, object]],
    ) -> dict[str, object]:
        count = len(replay_table)
        regrets: list[float] = []
        observed_rewards: list[float] = []
        false_positive_costs: list[float] = []
        correct_count = 0
        protective_count = 0
        protective_false_positive_count = 0
        release_gate_mismatch_count = 0
        unsafe_action_count = 0
        action_distribution: dict[str, int] = {}
        for row in replay_table:
            action_id = self._strategy_action_id(strategy_id, row)
            reward_by_action = row.get("reward_by_action", {})
            reward_by_action = reward_by_action if isinstance(reward_by_action, dict) else {}
            expert_action_id = str(row["expert_action_id"])
            expert_reward = float(row.get("expert_reward", reward_by_action.get(expert_action_id, 0.0)))
            observed_reward = float(reward_by_action.get(action_id, reward_by_action.get(expert_action_id, 0.0)))
            regret = max(0.0, expert_reward - observed_reward)
            is_correct = action_id == expert_action_id
            is_protective = action_id in self._protective_action_ids()
            false_positive_cost = self._false_positive_cost_for_strategy_action(row, action_id, regret)
            if is_correct:
                correct_count += 1
            if is_protective:
                protective_count += 1
            if false_positive_cost > 0.0:
                protective_false_positive_count += 1
                false_positive_costs.append(false_positive_cost)
            if action_id == "J3_polishing_and_release_gate" and not is_correct:
                release_gate_mismatch_count += 1
            if bool(row.get("unsafe_action_blocked", False)) and action_id == row.get("policy_action_id"):
                unsafe_action_count += 1
            regrets.append(regret)
            observed_rewards.append(observed_reward)
            action_distribution[action_id] = action_distribution.get(action_id, 0) + 1
        return {
            "strategy_id": strategy_id,
            "joint_action_accuracy": round(correct_count / max(1, count), 3),
            "action_mismatch_rate": round(1.0 - correct_count / max(1, count), 3),
            "mean_observed_reward": round(sum(observed_rewards) / max(1, count), 3),
            "mean_reward_regret": round(sum(regrets) / max(1, count), 3),
            "p95_reward_regret": self._percentile(regrets, 0.95),
            "protective_action_rate": round(protective_count / max(1, count), 3),
            "protective_false_positive_rate": round(protective_false_positive_count / max(1, count), 3),
            "false_positive_action_cost": round(
                sum(false_positive_costs) / max(1, len(false_positive_costs)),
                3,
            ),
            "release_gate_mismatch_rate": round(release_gate_mismatch_count / max(1, count), 3),
            "unsafe_action_rate": round(unsafe_action_count / max(1, count), 3),
            "action_distribution": action_distribution,
            "case_count": count,
            "can_write_to_actuator": False,
            "can_write_to_release_gate": False,
            "field_replay_required": True,
        }

    def _strategy_action_id(self, strategy_id: str, row: dict[str, object]) -> str:
        reward_by_action = row.get("reward_by_action", {})
        reward_by_action = reward_by_action if isinstance(reward_by_action, dict) else {}
        candidate_actions = [action_id for action_id in self._candidate_action_ids() if action_id in reward_by_action]
        if not candidate_actions:
            candidate_actions = [str(action_id) for action_id in reward_by_action]
        fallback = str(row["expert_action_id"])
        if strategy_id == "agent49_policy":
            return str(row["policy_action_id"])
        if strategy_id == "guardrail_aware_policy":
            return str(row["guardrail_aware_policy_action_id"])
        if strategy_id == "safe_standby_rule":
            return "J4_safe_low_cost_standby" if "J4_safe_low_cost_standby" in candidate_actions else fallback
        if strategy_id == "release_first_rule":
            return "J3_polishing_and_release_gate" if "J3_polishing_and_release_gate" in candidate_actions else fallback
        if strategy_id == "expert_upper_bound":
            return fallback
        if strategy_id == "deterministic_random_action_baseline" and candidate_actions:
            seed = f"{row.get('batch_id', '')}:{row.get('scenario', '')}:{row.get('timestamp_min', '')}"
            index = sum(ord(char) for char in seed) % len(candidate_actions)
            return candidate_actions[index]
        return fallback

    @staticmethod
    def _protective_action_ids() -> set[str]:
        return {
            "J0_matrix_shock_equalize_and_recycle",
            "J2_catalyst_protection_before_regeneration",
            "J4_safe_low_cost_standby",
        }

    def _false_positive_cost_for_strategy_action(
        self,
        row: dict[str, object],
        action_id: str,
        regret: float,
    ) -> float:
        if action_id == row.get("expert_action_id"):
            return 0.0
        if action_id not in self._protective_action_ids():
            return 0.0
        if action_id == row.get("policy_action_id") and bool(row.get("is_false_positive_protective_action", False)):
            return round(float(row.get("false_positive_action_cost", 0.0)), 3)
        if str(row.get("scenario", "")) == "catalyst_uncertain_low_proxy" and (
            action_id == "J2_catalyst_protection_before_regeneration"
        ):
            return round(float(row.get("false_positive_action_cost", 0.18)), 3)
        return round(max(0.0, regret), 3)

    @staticmethod
    def _control_baseline_contract(
        control_policy_comparison: dict[str, object],
        offline_metrics: dict[str, object],
    ) -> dict[str, object]:
        required_policy_ids = [
            "agent49_policy",
            "guardrail_aware_policy",
            "safe_standby_rule",
            "release_first_rule",
            "deterministic_random_action_baseline",
            "expert_upper_bound",
        ]
        metrics_by_strategy = control_policy_comparison.get("metrics_by_strategy", {})
        metrics_by_strategy = metrics_by_strategy if isinstance(metrics_by_strategy, dict) else {}
        missing = [policy_id for policy_id in required_policy_ids if policy_id not in metrics_by_strategy]
        return {
            "contract_id": "agent52_control_policy_baseline_comparison_v1",
            "comparison_status": control_policy_comparison["comparison_status"],
            "required_baseline_policy_ids": required_policy_ids,
            "missing_baseline_policy_ids": missing,
            "baseline_strategy_count": len(metrics_by_strategy),
            "reference_policy_id": "guardrail_aware_policy",
            "field_benchmark_required": True,
            "minimum_required_field_replay_coverage": 0.85,
            "synthetic_case_count": offline_metrics["replay_case_count"],
            "can_update_agent49_reward_prior": not missing,
            "can_select_deployed_policy": False,
            "can_write_to_actuator": False,
            "can_write_to_release_gate": False,
            "delta_summary": control_policy_comparison["delta_summary"],
            "next_experiment_requirements": [
                "用 field-origin agent52_replay_table 替换 synthetic replay cases。",
                "每个 batch 必须包含 operator_or_validated_expert_action、action outcome、reward components、actuator delay/result。",
                "对比 agent49_policy、guardrail_aware_policy、safe_standby_rule、release_first_rule、random baseline 和 expert upper bound。",
                "通过 field replay、operator final review、release validation 和 actuator interlock 后，才能讨论现场候选策略。",
            ],
            "cannot_do": [
                "cannot prove deployed control performance from synthetic replay",
                "cannot prove patentability or inventiveness",
                "cannot write actuator policy",
                "cannot write release gate policy",
                "cannot replace operator review or field holdout",
            ],
        }

    def _reward_diagnostics(self, replay_table: list[dict[str, object]]) -> dict[str, object]:
        regret_rows = sorted(replay_table, key=lambda row: float(row["reward_regret"]), reverse=True)
        return {
            "highest_regret_cases": [
                {
                    "batch_id": row["batch_id"],
                    "scenario": row["scenario"],
                    "policy_action_id": row["policy_action_id"],
                    "expert_action_id": row["expert_action_id"],
                    "reward_regret": row["reward_regret"],
                }
                for row in regret_rows[:3]
            ],
            "false_positive_cases": [
                {
                    "batch_id": row["batch_id"],
                    "scenario": row["scenario"],
                    "policy_action_id": row["policy_action_id"],
                    "false_positive_action_cost": row["false_positive_action_cost"],
                }
                for row in replay_table
                if row["is_false_positive_protective_action"]
            ],
            "guardrail_resolved_cases": [
                {
                    "batch_id": row["batch_id"],
                    "scenario": row["scenario"],
                    "baseline_policy_action_id": row["policy_action_id"],
                    "guardrail_aware_policy_action_id": row["guardrail_aware_policy_action_id"],
                    "expert_action_id": row["expert_action_id"],
                    "guardrail_source_rule_id": row["guardrail_source_rule_id"],
                    "reward_regret_delta": round(
                        float(row["reward_regret"]) - float(row["guardrail_aware_reward_regret"]),
                        3,
                    ),
                }
                for row in replay_table
                if not row["is_correct_action"] and row["guardrail_aware_is_correct_action"]
            ],
            "engineering_interpretation": (
                "高 regret 或误保护案例应优先写入 Agent49 reward_contract；"
                "synthetic replay 只能暴露指标和 schema 缺口，不能证明现场策略有效。"
            ),
        }

    def _distillation_eval(self, replay_table: list[dict[str, object]], offline_metrics: dict[str, object]) -> dict[str, object]:
        distillation = self.collaborative_control_metrics.get("decision_tree_distillation", {})
        if not isinstance(distillation, dict):
            distillation = {}
        base_accuracy = float(distillation.get("distilled_policy_accuracy_proxy", 0.0))
        replay_accuracy = float(
            offline_metrics["guardrail_aware_joint_action_accuracy"]
            if offline_metrics.get("control_replay_guardrails_integrated", False)
            else offline_metrics["joint_action_accuracy"]
        )
        field_accuracy = float(self.field_validation.get("distilled_policy_accuracy", 0.0))
        effective_accuracy = field_accuracy if self.data_origin == "field_coordination_replay" and field_accuracy else min(base_accuracy, replay_accuracy)
        rules = distillation.get("tree_rules", [])
        if not isinstance(rules, list):
            rules = []
        return {
            "distillation_method": distillation.get("distillation_method", "ID3_style_decision_tree_surrogate"),
            "agent49_distilled_policy_accuracy_proxy": round(base_accuracy, 3),
            "replay_distilled_policy_accuracy": round(effective_accuracy, 3),
            "rule_count": len(rules),
            "minimum_required_accuracy": 0.90,
            "field_accuracy_required": True,
            "can_promote_distilled_policy": self.data_origin == "field_coordination_replay" and effective_accuracy >= 0.90,
            "rule_audit_findings": self._rule_audit_findings(replay_table),
        }

    def _readiness(self, offline_metrics: dict[str, object], distillation_eval: dict[str, object]) -> dict[str, object]:
        synthetic_replay_ready = (
            int(offline_metrics["replay_case_count"]) >= self.min_case_count
            and int(offline_metrics["candidate_action_count"]) >= 5
            and self._has_reward_by_action()
        )
        guardrail_aware_replay_ready = synthetic_replay_ready and bool(
            offline_metrics.get("control_replay_guardrails_integrated", False)
        )
        field_ready = (
            self.data_origin == "field_coordination_replay"
            and float(offline_metrics["field_replay_coverage"]) >= self.min_field_replay_coverage
            and float(offline_metrics["joint_action_accuracy"]) >= self.min_joint_action_accuracy
            and float(offline_metrics["mean_reward_regret"]) <= self.max_reward_regret
            and float(offline_metrics["false_positive_action_cost"]) <= self.max_false_positive_cost
            and bool(offline_metrics["catalyst_proxy_field_validation_pass"])
            and (
                not bool(offline_metrics.get("pressure_headloss_boundary_consumed", False))
                or bool(offline_metrics.get("pressure_headloss_can_relax_control_guardrail", False))
            )
            and not bool(offline_metrics.get("pressure_source_conflict_requires_operator_review", False))
            and bool(distillation_eval["can_promote_distilled_policy"])
        )
        score = round(
            0.18 * float(synthetic_replay_ready)
            + 0.18 * min(1.0, float(offline_metrics["joint_action_accuracy"]) / self.min_joint_action_accuracy)
            + 0.16 * min(1.0, max(0.0, 1.0 - float(offline_metrics["mean_reward_regret"]) / max(0.01, self.max_reward_regret)))
            + 0.16 * min(1.0, float(offline_metrics["field_replay_coverage"]) / self.min_field_replay_coverage)
            + 0.16 * min(1.0, float(distillation_eval["replay_distilled_policy_accuracy"]) / 0.90)
            + 0.16 * float(field_ready),
            3,
        )
        if not synthetic_replay_ready:
            status = "replay_schema_incomplete"
        elif not field_ready:
            status = "synthetic_replay_evaluation_ready_needs_field_replay"
        else:
            status = "field_replay_evaluation_candidate_ready"
        return {
            "replay_evaluation_status": status,
            "replay_evaluation_score": score,
            "synthetic_replay_ready": synthetic_replay_ready,
            "guardrail_aware_replay_ready": guardrail_aware_replay_ready,
            "field_ready": field_ready,
            "catalyst_proxy_field_validation_pass": bool(offline_metrics["catalyst_proxy_field_validation_pass"]),
            "catalyst_guardrail_mode": offline_metrics["catalyst_guardrail_mode"],
            "pressure_headloss_boundary_consumed": bool(offline_metrics.get("pressure_headloss_boundary_consumed", False)),
            "pressure_headloss_candidate_count": offline_metrics.get("pressure_headloss_candidate_count", 0),
            "pressure_headloss_guardrail_field_ready": (
                not bool(offline_metrics.get("pressure_headloss_boundary_consumed", False))
                or bool(offline_metrics.get("pressure_headloss_can_relax_control_guardrail", False))
            )
            and not bool(offline_metrics.get("pressure_source_conflict_requires_operator_review", False)),
            "pressure_source_conflict_count": offline_metrics.get("pressure_source_conflict_count", 0),
            "resolved_pressure_source_conflict_count": offline_metrics.get(
                "resolved_pressure_source_conflict_count",
                0,
            ),
            "unresolved_pressure_source_conflict_count": offline_metrics.get(
                "unresolved_pressure_source_conflict_count",
                0,
            ),
            "pressure_source_resolution_record_count": offline_metrics.get(
                "pressure_source_resolution_record_count",
                0,
            ),
            "pressure_source_conflict_clear": not bool(
                offline_metrics.get("pressure_source_conflict_requires_operator_review", False)
            ),
            "pressure_source_conflict_requires_operator_review": bool(
                offline_metrics.get("pressure_source_conflict_requires_operator_review", False)
            ),
            "can_update_agent49_reward_prior": synthetic_replay_ready,
            "can_train_offline_rl": field_ready,
            "can_write_to_actuator": field_ready,
            "can_write_to_release_gate": False,
        }

    @staticmethod
    def _agent49_writeback(readiness: dict[str, object], offline_metrics: dict[str, object]) -> dict[str, object]:
        return {
            "target_agent": "MultiFacilityCollaborativeControlAgent",
            "allowed_writeback": ["reward_prior", "replay_schema", "offline_metric_contract"]
            if readiness["synthetic_replay_ready"]
            else [],
            "blocked_writeback": ["actuator_policy", "release_gate_policy", "online_MARL_training"],
            "policy_effect": (
                "keep_agent49_synthetic_policy_block"
                if not readiness["field_ready"]
                else "allow_human_reviewed_actuator_candidate_only"
            ),
            "metric_patch": {
                "joint_action_accuracy": offline_metrics["joint_action_accuracy"],
                "mean_reward_regret": offline_metrics["mean_reward_regret"],
                "false_positive_action_cost": offline_metrics["false_positive_action_cost"],
                "guardrail_aware_joint_action_accuracy": offline_metrics["guardrail_aware_joint_action_accuracy"],
                "guardrail_aware_mean_reward_regret": offline_metrics["guardrail_aware_mean_reward_regret"],
                "guardrail_aware_false_positive_action_cost": offline_metrics["guardrail_aware_false_positive_action_cost"],
                "field_replay_coverage": offline_metrics["field_replay_coverage"],
                "control_policy_baseline_strategy_count": offline_metrics.get(
                    "control_policy_baseline_strategy_count",
                    0,
                ),
                "control_policy_baseline_comparison_status": offline_metrics.get(
                    "control_policy_baseline_comparison_status",
                    "not_generated",
                ),
                "catalyst_proxy_summary_status": offline_metrics["catalyst_proxy_summary_status"],
                "catalyst_proxy_scoreable_batch_count": offline_metrics["catalyst_proxy_scoreable_batch_count"],
                "catalyst_proxy_field_validation_pass": offline_metrics["catalyst_proxy_field_validation_pass"],
                "pressure_headloss_boundary_consumed": offline_metrics.get("pressure_headloss_boundary_consumed", False),
                "pressure_headloss_candidate_count": offline_metrics.get("pressure_headloss_candidate_count", 0),
                "pressure_headloss_blocked_guardrail_case_count": offline_metrics.get(
                    "pressure_headloss_blocked_guardrail_case_count",
                    0,
                ),
                "pressure_headloss_can_relax_control_guardrail": offline_metrics.get(
                    "pressure_headloss_can_relax_control_guardrail",
                    False,
                ),
                "pressure_source_conflict_count": offline_metrics.get("pressure_source_conflict_count", 0),
                "resolved_pressure_source_conflict_count": offline_metrics.get(
                    "resolved_pressure_source_conflict_count",
                    0,
                ),
                "unresolved_pressure_source_conflict_count": offline_metrics.get(
                    "unresolved_pressure_source_conflict_count",
                    0,
                ),
                "pressure_source_resolution_record_count": offline_metrics.get(
                    "pressure_source_resolution_record_count",
                    0,
                ),
                "pressure_source_conflict_requires_operator_review": offline_metrics.get(
                    "pressure_source_conflict_requires_operator_review",
                    False,
                ),
                "pressure_source_conflict_replay_blocked_case_count": offline_metrics.get(
                    "pressure_source_conflict_replay_blocked_case_count",
                    0,
                ),
            },
        }

    def _issues(
        self,
        offline_metrics: dict[str, object],
        distillation_eval: dict[str, object],
        readiness: dict[str, object],
    ) -> list[QualityIssue]:
        issues: list[QualityIssue] = []
        if not readiness["field_ready"]:
            issues.append(
                QualityIssue(
                    sensor="multi_facility_replay",
                    issue_type="field_replay_required_before_agent49_promotion",
                    severity=Severity.WARNING,
                    message="Agent49 replay 评估当前只在 synthetic cases 上可运行，必须导入真实多节点 state-action-reward replay 后才能提升为执行器候选。",
                    evidence=offline_metrics,
                )
            )
        if float(offline_metrics["joint_action_accuracy"]) < self.min_joint_action_accuracy:
            issues.append(
                QualityIssue(
                    sensor="multi_facility_replay",
                    issue_type="joint_action_accuracy_below_execution_threshold",
                    severity=Severity.WARNING,
                    message="离线 joint_action_accuracy 未达到现场执行候选门槛，说明协同动作仍需重放数据校准。",
                    evidence={"threshold": self.min_joint_action_accuracy, "actual": offline_metrics["joint_action_accuracy"]},
                )
            )
        if float(distillation_eval["replay_distilled_policy_accuracy"]) < 0.90:
            issues.append(
                QualityIssue(
                    sensor="multi_facility_replay",
                    issue_type="distilled_policy_replay_accuracy_not_ready",
                    severity=Severity.INFO,
                    message="决策树蒸馏还只是解释代理，未通过 replay accuracy 前不能替代控制策略。",
                    evidence=distillation_eval,
                )
            )
        if float(offline_metrics["protective_false_positive_rate"]) > 0.0:
            issues.append(
                QualityIssue(
                    sensor="multi_facility_replay",
                    issue_type="protective_false_positive_cost_visible",
                    severity=Severity.INFO,
                    message="synthetic replay 已暴露保护性动作误触发成本，需要进入 Agent49 reward 和人工复核字段。",
                    evidence=offline_metrics,
                )
            )
        if bool(offline_metrics.get("control_replay_guardrails_integrated", False)) and not readiness["field_ready"]:
            issues.append(
                QualityIssue(
                    sensor="multi_facility_replay",
                    issue_type="guardrail_aware_replay_still_synthetic",
                    severity=Severity.INFO,
                    message="R3b guardrail-aware replay 已改善 synthetic 指标，但 field_replay_coverage 仍为 0，不能升级为现场控制有效性。",
                    evidence=offline_metrics,
                )
            )
        if not bool(offline_metrics.get("catalyst_proxy_field_validation_pass", False)):
            issues.append(
                QualityIssue(
                    sensor="agent51_catalyst_proxy_holdout",
                    issue_type="catalyst_proxy_field_validation_blocks_agent49_promotion",
                    severity=Severity.WARNING,
                    message="Agent52 replay 已读取 Agent51 catalyst proxy 状态；在 field holdout 未通过前，Agent49 不能把催化剂保护/再生升级为执行器候选。",
                    evidence={
                        "summary_status": offline_metrics.get("catalyst_proxy_summary_status"),
                        "scoreable_batch_count": offline_metrics.get("catalyst_proxy_scoreable_batch_count"),
                        "guardrail_mode": offline_metrics.get("catalyst_guardrail_mode"),
                    },
                )
            )
        if bool(offline_metrics.get("pressure_headloss_boundary_consumed", False)) and not bool(
            offline_metrics.get("pressure_headloss_can_relax_control_guardrail", False)
        ):
            issues.append(
                QualityIssue(
                    sensor="multi_facility_replay",
                    issue_type="pressure_headloss_guardrail_boundary_requires_field_replay",
                    severity=Severity.INFO,
                    message="Agent52 已消费 Agent49 pressure/headloss 控制边界，但现场拓扑、床层几何和匹配 lab label 未过线前，它只能用于 replay 阻断解释。",
                    evidence={
                        "candidate_count": offline_metrics.get("pressure_headloss_candidate_count"),
                        "blocked_guardrail_case_count": offline_metrics.get(
                            "pressure_headloss_blocked_guardrail_case_count"
                        ),
                    },
                )
            )
        if bool(offline_metrics.get("pressure_source_conflict_requires_operator_review", False)):
            issues.append(
                QualityIssue(
                    sensor="agent51_pressure_headloss_source",
                    issue_type="pressure_source_conflict_blocks_agent49_promotion",
                    severity=Severity.WARNING,
                    message="Agent52 replay 已消费 R8k pressure source conflict；冲突未复核前，即使 field replay 指标达标，也不能提升 Agent49 为执行器候选。",
                    evidence={
                        "pressure_source_conflict_count": offline_metrics.get("pressure_source_conflict_count"),
                        "resolved_pressure_source_conflict_count": offline_metrics.get(
                            "resolved_pressure_source_conflict_count"
                        ),
                        "unresolved_pressure_source_conflict_count": offline_metrics.get(
                            "unresolved_pressure_source_conflict_count"
                        ),
                        "pressure_source_resolution_record_count": offline_metrics.get(
                            "pressure_source_resolution_record_count"
                        ),
                        "pressure_source_conflict_replay_blocked_case_count": offline_metrics.get(
                            "pressure_source_conflict_replay_blocked_case_count"
                        ),
                    },
                )
            )
        return issues

    @staticmethod
    def _recommendations(
        readiness: dict[str, object],
        offline_metrics: dict[str, object],
        reward_diagnostics: dict[str, object],
    ) -> list[str]:
        recs = [
            "把 Agent49 的候选协同动作接入 state-action-reward replay schema，而不是直接训练在线 MARL。",
            "先用 replay 计算 joint_action_accuracy、reward_regret、误保护成本和策略蒸馏准确度，再决定是否进入人工复核的执行器候选。",
            "将 highest_regret_cases 写回 Agent49 reward_prior，优先修正高 regret 场景的动作排序。",
        ]
        if not readiness["field_ready"]:
            recs.append("下一步必须准备真实多节点 sensor/lab/operation/action replay；synthetic replay 只能证明 schema 和指标可运行。")
        if float(offline_metrics["protective_false_positive_rate"]) > 0.0:
            recs.append(f"优先复核保护性误触发案例：{reward_diagnostics['false_positive_cases']}。")
        if bool(offline_metrics.get("control_replay_guardrails_integrated", False)):
            recs.append(
                "R3c 已形成 guardrail-aware replay 对照：保留 baseline 指标，同时用 R3b policy 检查 regret 与误保护成本是否下降。"
            )
        if not bool(offline_metrics.get("catalyst_proxy_field_validation_pass", False)):
            recs.append(
                "Agent51 catalyst proxy field holdout 未过线时，Agent52 只能更新 replay/reward prior，不能让 Agent49 放松催化剂不确定性保护。"
            )
        if bool(offline_metrics.get("pressure_headloss_boundary_consumed", False)):
            recs.append(
                "R8d 已把 pressure/headloss 控制边界纳入 Agent52 replay；下一步需要用压降/水头损失时序、床层几何和 matched lab labels 验证该边界，否则仍不能解除回流或催化剂 guardrail。"
            )
        if bool(offline_metrics.get("pressure_source_conflict_requires_operator_review", False)):
            recs.append(
                "R8k pressure source conflict 已进入 Agent52 replay；应把冲突 batch 写入现场校准/人工复核队列，并把受影响的 catalyst/hydraulic cases 作为高优先级 replay 样本。"
            )
        return recs

    def _method_contract(self) -> dict[str, object]:
        return {
            "upgrade_id": "agent49_replay_ready_offline_evaluation",
            "borrowed_from": [
                "Offline RL data contract with observations/actions/rewards/next_observations",
                "Conservative offline RL before online deployment",
                "D4RL-style fixed dataset benchmark separation",
                "Decision-tree policy extraction / VIPER-style interpretability",
                "User-provided wastewater multi-facility shared experience pool",
                "R3 counterfactual guardrail-aware replay before policy promotion",
                "R8d pressure/headloss guardrail-boundary replay refresh",
                "R8k pressure/headloss source conflict calibration boundary",
            ],
            "source_links": [
                "https://arxiv.org/abs/2005.01643",
                "https://arxiv.org/abs/2006.04779",
                "https://github.com/Farama-Foundation/D4RL",
                "https://arxiv.org/abs/1805.08328",
            ],
            "reality_mapping": "把 Agent49 的多设施候选控制从静态动作排序推进到可回放、可计分、可审计的 state-action-reward 离线评估框架。",
            "data_needs": [
                "multi_node_sensor_timeseries",
                "facility_state_vectors",
                "operation_action_log",
                "operator_or_validated_expert_action",
                "reward_components",
                "next_state_or_lab_label",
                "actuator_result_and_delay",
                "false_positive_action_cost",
                "pressure_headloss_timeseries_and_bed_geometry",
            ],
            "implementation_path": [
                "src/water_ai/agents/multi_facility_replay_evaluation_agent.py",
                "experiments/run_agent52_multi_facility_replay_evaluation.py",
                "outputs/multi_facility_replay_evaluation/replay_evaluation_metrics.json",
            ],
            "evaluation_metrics": [
                "joint_action_accuracy",
                "mean_reward_regret",
                "p95_reward_regret",
                "protective_false_positive_rate",
                "false_positive_action_cost",
                "guardrail_aware_joint_action_accuracy",
                "guardrail_aware_p95_reward_regret",
                "guardrail_aware_false_positive_action_cost",
                "distilled_policy_replay_accuracy",
                "field_replay_coverage",
                "catalyst_proxy_field_validation_pass",
                "catalyst_proxy_scoreable_batch_count",
                "pressure_headloss_boundary_consumed",
                "pressure_headloss_blocked_guardrail_case_count",
                "pressure_source_conflict_count",
                "pressure_source_conflict_replay_blocked_case_count",
                "control_policy_baseline_strategy_count",
                "control_policy_baseline_comparison_status",
            ],
            "failure_boundary": "synthetic replay can update schemas and reward priors, but cannot train or validate a deployable offline RL policy without field replay.",
        }

    def _default_replay_cases(self) -> list[dict[str, object]]:
        return [
            {
                "batch_id": "R0",
                "timestamp_min": 36,
                "scenario": "matrix_shock_visible",
                "policy_action_id": "J0_matrix_shock_equalize_and_recycle",
                "expert_action_id": "J0_matrix_shock_equalize_and_recycle",
                "state_scores": {"matrix": 0.88, "reaction": 0.52, "catalyst": 0.34, "release": 0.68, "latency": 0.82},
                "missingness_mask": {"N0_influent:EC_uScm": False, "N4_recirculation_loop:UV254_abs": False},
                "next_state_summary": "matrix load buffered and recycle evidence window preserved",
                "lab_label": {"matrix_shock": True, "release_safe": False},
            },
            {
                "batch_id": "R1",
                "timestamp_min": 44,
                "scenario": "reaction_completion_lag",
                "policy_action_id": "J1_reaction_completion_recovery",
                "expert_action_id": "J1_reaction_completion_recovery",
                "state_scores": {"matrix": 0.42, "reaction": 0.82, "catalyst": 0.42, "release": 0.70, "latency": 0.66},
                "missingness_mask": {"N2_reactor_mid:ORP_mV": False, "N1_equalization_tank:flow_Lmin": False},
                "next_state_summary": "oxidant and retention adjustment needed before polishing",
                "lab_label": {"reaction_incomplete": True, "release_safe": False},
            },
            {
                "batch_id": "R2",
                "timestamp_min": 52,
                "scenario": "catalyst_uncertain_low_proxy",
                "policy_action_id": "J2_catalyst_protection_before_regeneration",
                "expert_action_id": "J4_safe_low_cost_standby",
                "state_scores": {"matrix": 0.45, "reaction": 0.55, "catalyst": 0.28, "release": 0.56, "latency": 0.58},
                "missingness_mask": {"N3_catalyst_bed_outlet:UV254_abs": True, "N3_catalyst_bed:pressure_drop_kPa": True},
                "false_positive_if_policy": True,
                "false_positive_action_cost": 0.18,
                "next_state_summary": "catalyst action should wait for field proxy holdout and pressure evidence",
                "lab_label": {"catalyst_activity_low": "uncertain", "release_safe": False},
            },
            {
                "batch_id": "R3",
                "timestamp_min": 61,
                "scenario": "polishing_release_risk",
                "policy_action_id": "J3_polishing_and_release_gate",
                "expert_action_id": "J3_polishing_and_release_gate",
                "state_scores": {"matrix": 0.38, "reaction": 0.62, "catalyst": 0.44, "release": 0.91, "latency": 0.48},
                "missingness_mask": {"N5_polishing_inlet:turbidity_NTU": False, "offline_lab:target_residual": True},
                "next_state_summary": "release blocked until lab and polishing evidence return",
                "lab_label": {"release_safe": False, "polishing_required": True},
            },
            {
                "batch_id": "R4",
                "timestamp_min": 70,
                "scenario": "clean_but_low_field_evidence",
                "policy_action_id": "J4_safe_low_cost_standby",
                "expert_action_id": "J4_safe_low_cost_standby",
                "state_scores": {"matrix": 0.24, "reaction": 0.76, "catalyst": 0.60, "release": 0.72, "latency": 0.60},
                "missingness_mask": {"field_replay_label": True},
                "next_state_summary": "low-cost standby until field evidence closes release uncertainty",
                "lab_label": {"release_safe": "pending"},
            },
            {
                "batch_id": "R5",
                "timestamp_min": 83,
                "scenario": "hydraulic_delay_violation",
                "policy_action_id": "J0_matrix_shock_equalize_and_recycle",
                "expert_action_id": "J3_polishing_and_release_gate",
                "state_scores": {"matrix": 0.64, "reaction": 0.60, "catalyst": 0.38, "release": 0.78, "latency": 0.30},
                "missingness_mask": {"actuator_latency:P90": True, "tank_storage_margin": True},
                "unsafe_action_blocked": True,
                "next_state_summary": "recycle action should be blocked because latency and storage margins are unknown",
                "lab_label": {"hydraulic_delay_violation": True, "release_safe": False},
            },
        ]

    def _reward_by_action(self, case: dict[str, object]) -> dict[str, float]:
        scores = case.get("state_scores", {})
        if not isinstance(scores, dict):
            scores = {}
        matrix = self._float(scores, "matrix")
        reaction = self._float(scores, "reaction")
        catalyst = self._float(scores, "catalyst")
        release = self._float(scores, "release")
        latency = self._float(scores, "latency")
        uncertainty_penalty = 0.10 if self._catalyst_proxy_requires_field() else 0.0
        return {
            "J0_matrix_shock_equalize_and_recycle": self._clip(0.34 * matrix + 0.20 * release + 0.18 * latency + 0.18 * reaction - 0.04 * max(0.0, 0.45 - latency)),
            "J1_reaction_completion_recovery": self._clip(0.42 * reaction + 0.18 * release + 0.16 * latency + 0.12 * matrix - 0.05),
            "J2_catalyst_protection_before_regeneration": self._clip(0.38 * catalyst + 0.22 * release + 0.14 * latency + 0.14 * matrix - uncertainty_penalty),
            "J3_polishing_and_release_gate": self._clip(0.42 * release + 0.20 * reaction + 0.18 * (1.0 - max(0.0, 0.55 - latency)) + 0.10),
            "J4_safe_low_cost_standby": self._clip(0.26 * release + 0.18 * latency + 0.18 * (1.0 - matrix) + 0.14 * (1.0 - max(0.0, 0.55 - catalyst))),
        }

    def _control_replay_guardrail_available(self) -> bool:
        readiness = self.collaborative_control_metrics.get("readiness", {})
        context = self.collaborative_control_metrics.get("control_replay_guardrail_context", {})
        readiness = readiness if isinstance(readiness, dict) else {}
        context = context if isinstance(context, dict) else {}
        return bool(readiness.get("control_replay_guardrails_integrated", False)) and bool(
            context.get("reward_prior_guardrail_available", False)
        )

    def _pressure_headloss_context(self) -> dict[str, object]:
        guardrail = self.collaborative_control_metrics.get("control_replay_guardrail_context", {})
        guardrail = guardrail if isinstance(guardrail, dict) else {}
        catalyst_context = self._catalyst_proxy_context()
        sparse_context = self.collaborative_control_metrics.get("sparse_context", {})
        sparse_context = sparse_context if isinstance(sparse_context, dict) else {}
        observation_context = sparse_context.get("observation_contract_context", {})
        observation_context = observation_context if isinstance(observation_context, dict) else {}
        candidate_ids = [
            str(item)
            for item in guardrail.get(
                "pressure_headloss_candidate_ids",
                observation_context.get("pressure_headloss_candidate_ids", []),
            )
            if item
        ]
        candidate_count = int(
            guardrail.get(
                "pressure_headloss_candidate_count",
                observation_context.get("pressure_headloss_candidate_count", len(candidate_ids)),
            )
            or 0
        )
        consumed = bool(
            guardrail.get(
                "pressure_headloss_consumed_by_agent49",
                observation_context.get("pressure_headloss_consumed_by_agent49", False),
            )
        ) and (candidate_count > 0 or bool(candidate_ids))
        can_relax = bool(
            guardrail.get(
                "pressure_headloss_can_relax_control_guardrail",
                observation_context.get("pressure_headloss_can_relax_control_guardrail", False),
            )
        )
        conflict_count = int(
            guardrail.get(
                "pressure_source_conflict_count",
                catalyst_context.get("pressure_source_conflict_count", 0),
            )
            or 0
        )
        resolved_conflict_count = int(
            guardrail.get(
                "resolved_pressure_source_conflict_count",
                catalyst_context.get("resolved_pressure_source_conflict_count", 0),
            )
            or 0
        )
        unresolved_conflict_count = int(
            guardrail.get(
                "unresolved_pressure_source_conflict_count",
                catalyst_context.get("unresolved_pressure_source_conflict_count", max(0, conflict_count - resolved_conflict_count)),
            )
            or 0
        )
        resolution_record_count = int(
            guardrail.get(
                "pressure_source_resolution_record_count",
                catalyst_context.get("pressure_source_resolution_record_count", resolved_conflict_count),
            )
            or 0
        )
        conflict_requires_review = bool(
            guardrail.get(
                "conflict_requires_operator_review",
                catalyst_context.get("conflict_requires_operator_review", unresolved_conflict_count > 0),
            )
        )
        return {
            "pool_status": str(
                guardrail.get(
                    "pressure_headloss_candidate_pool_status",
                    observation_context.get("pressure_headloss_candidate_pool_status", "missing_pressure_headloss_pool"),
                )
            ),
            "candidate_count": candidate_count,
            "candidate_ids": candidate_ids,
            "consumed_by_agent52": consumed,
            "can_relax_hydraulic_or_catalyst_guardrail": can_relax,
            "field_validation_required": consumed and not can_relax,
            "control_boundary": str(
                guardrail.get(
                    "pressure_headloss_control_boundary",
                    observation_context.get(
                        "pressure_headloss_control_boundary",
                        "pressure/headloss candidate pool not supplied",
                    ),
                )
            ),
            "can_write_to_actuator": False,
            "can_write_to_release_gate": False,
            "pressure_source_conflict_count": conflict_count,
            "resolved_pressure_source_conflict_count": resolved_conflict_count,
            "unresolved_pressure_source_conflict_count": unresolved_conflict_count,
            "pressure_source_resolution_record_count": resolution_record_count,
            "conflict_requires_operator_review": conflict_requires_review,
            "pressure_source_conflict_control_block": bool(
                guardrail.get(
                    "pressure_source_conflict_control_block",
                    catalyst_context.get("pressure_source_conflict_control_block", conflict_requires_review),
                )
            ),
        }

    def _guardrail_aware_policy_action(self, case: dict[str, object], policy_action: str) -> str:
        if not self._control_replay_guardrail_available():
            return policy_action
        scenario = str(case.get("scenario", ""))
        if scenario == "catalyst_uncertain_low_proxy":
            return "J4_safe_low_cost_standby"
        if scenario == "hydraulic_delay_violation" or bool(case.get("unsafe_action_blocked", False)):
            return "J3_polishing_and_release_gate"
        return policy_action

    @staticmethod
    def _guardrail_source_rule_id(case: dict[str, object], guardrail_action: str, policy_action: str) -> str:
        if guardrail_action == policy_action:
            return "none"
        scenario = str(case.get("scenario", ""))
        if scenario == "catalyst_uncertain_low_proxy":
            return "R3G1_catalyst_uncertain_requires_standby_or_human_review"
        if scenario == "hydraulic_delay_violation" or bool(case.get("unsafe_action_blocked", False)):
            return "R3G2_hydraulic_delay_unknown_blocks_recycle"
        return "unknown_guardrail_rule"

    @staticmethod
    def _false_positive_action_cost(
        case: dict[str, object],
        action_id: str,
        policy_action: str,
        expert_action: str,
    ) -> float:
        if action_id == expert_action:
            return 0.0
        if bool(case.get("false_positive_if_policy", False)) and action_id == policy_action:
            return round(float(case.get("false_positive_action_cost", 0.0)), 3)
        if str(case.get("scenario", "")) == "catalyst_uncertain_low_proxy" and action_id == "J2_catalyst_protection_before_regeneration":
            return round(float(case.get("false_positive_action_cost", 0.18)), 3)
        return 0.0

    def _facility_state_vector(self, case: dict[str, object]) -> dict[str, float]:
        if isinstance(case.get("facility_state_vector"), dict):
            return dict(case["facility_state_vector"])
        scores = case.get("state_scores", {})
        if not isinstance(scores, dict):
            scores = {}
        return {
            "influent_disturbance_visibility": self._clip(self._float(scores, "matrix")),
            "reaction_state_visibility": self._clip(self._float(scores, "reaction")),
            "catalyst_state_visibility": self._clip(self._float(scores, "catalyst")),
            "release_risk_visibility": self._clip(self._float(scores, "release")),
            "control_latency_buffer": self._clip(self._float(scores, "latency")),
        }

    def _candidate_action_ids(self) -> list[str]:
        joint = self.collaborative_control_metrics.get("joint_action_matrix", [])
        if isinstance(joint, list) and joint:
            return [str(item.get("joint_action_id")) for item in joint if isinstance(item, dict) and item.get("joint_action_id")]
        return [
            "J0_matrix_shock_equalize_and_recycle",
            "J1_reaction_completion_recovery",
            "J2_catalyst_protection_before_regeneration",
            "J3_polishing_and_release_gate",
            "J4_safe_low_cost_standby",
        ]

    def _available_node_modalities(self) -> list[str]:
        sparse = self.collaborative_control_metrics.get("sparse_context", {})
        if not isinstance(sparse, dict):
            return []
        nodes = sparse.get("selected_nodes", [])
        modalities = sparse.get("selected_modalities", [])
        if not isinstance(nodes, list) or not isinstance(modalities, list):
            return []
        return [f"{node}:*" for node in nodes] + [f"*:{modality}" for modality in modalities]

    def _rule_audit_findings(self, replay_table: list[dict[str, object]]) -> list[dict[str, object]]:
        findings: list[dict[str, object]] = []
        for row in replay_table:
            if not row["is_correct_action"] or row["is_false_positive_protective_action"] or row["unsafe_action_blocked"]:
                findings.append(
                    {
                        "case_id": row["batch_id"],
                        "scenario": row["scenario"],
                        "finding": "rule_requires_field_replay_or_reward_patch",
                        "policy_action_id": row["policy_action_id"],
                        "expert_action_id": row["expert_action_id"],
                    }
                )
        return findings

    def _has_reward_by_action(self) -> bool:
        return all(action_id in self._reward_by_action(case) for case in self.replay_cases for action_id in self._candidate_action_ids()[:5])

    def _catalyst_proxy_requires_field(self) -> bool:
        return not bool(self._catalyst_proxy_context()["field_validation_pass"])

    def _catalyst_proxy_context(self) -> dict[str, object]:
        readiness = self.catalyst_proxy_metrics.get("readiness", {})
        readiness = readiness if isinstance(readiness, dict) else {}
        summary = self.catalyst_proxy_metrics.get("field_proxy_holdout_summary", {})
        summary = summary if isinstance(summary, dict) else {}
        validation = summary.get("field_validation_metrics", {})
        validation = validation if isinstance(validation, dict) else {}
        summary_supplied = bool(summary)
        field_validation_pass = bool(summary.get("field_validation_pass", readiness.get("field_validated", False)))
        ready_for_validation = bool(summary.get("ready_for_agent51_validation", False))
        scoreable_count = int(summary.get("scoreable_batch_count", readiness.get("field_holdout_scoreable_batch_count", 0)) or 0)
        matched_count = int(summary.get("matched_batch_count", readiness.get("field_holdout_matched_batch_count", 0)) or 0)
        accepted_pressure_sources = summary.get(
            "accepted_pressure_evidence_sources",
            readiness.get("accepted_pressure_evidence_sources", []),
        )
        pressure_source_counts = summary.get(
            "pressure_evidence_source_batch_counts",
            readiness.get("pressure_evidence_source_batch_counts", {}),
        )
        pressure_event_source_count = int(
            summary.get(
                "pressure_headloss_event_source_batch_count",
                readiness.get("pressure_headloss_event_source_batch_count", 0),
            )
            or 0
        )
        pressure_conflict_count = int(
            summary.get(
                "pressure_source_conflict_count",
                readiness.get("pressure_source_conflict_count", 0),
            )
            or 0
        )
        resolved_pressure_conflict_count = int(
            summary.get(
                "resolved_pressure_source_conflict_count",
                readiness.get("resolved_pressure_source_conflict_count", 0),
            )
            or 0
        )
        unresolved_pressure_conflict_count = int(
            summary.get(
                "unresolved_pressure_source_conflict_count",
                readiness.get("unresolved_pressure_source_conflict_count", 0),
            )
            or 0
        )
        pressure_resolution_record_count = int(
            summary.get(
                "pressure_source_resolution_record_count",
                readiness.get("pressure_source_resolution_record_count", 0),
            )
            or 0
        )
        conflict_requires_review = bool(
            summary.get(
                "conflict_requires_operator_review",
                readiness.get("conflict_requires_operator_review", pressure_conflict_count > 0),
            )
        )
        status = str(
            summary.get(
                "field_proxy_holdout_summary_status",
                readiness.get("field_proxy_holdout_summary_status", "not_supplied"),
            )
        )
        if conflict_requires_review:
            mode = "agent51_pressure_source_conflict_keep_catalyst_guardrail"
        elif field_validation_pass:
            mode = "agent51_field_validated_human_reviewed_relaxation_candidate"
        elif ready_for_validation:
            mode = "agent51_holdout_scoreable_but_recalibration_required"
        elif summary_supplied:
            mode = "agent51_holdout_coverage_gaps_keep_catalyst_guardrail"
        else:
            mode = "agent51_holdout_not_supplied_keep_catalyst_guardrail"
        return {
            "summary_supplied": summary_supplied,
            "summary_status": status,
            "ready_for_agent51_validation": ready_for_validation,
            "field_validation_pass": field_validation_pass,
            "scoreable_batch_count": scoreable_count,
            "matched_batch_count": matched_count,
            "holdout_mae": validation.get("holdout_mae"),
            "proxy_label_correlation": validation.get("proxy_label_correlation"),
            "accepted_pressure_evidence_sources": accepted_pressure_sources if isinstance(accepted_pressure_sources, list) else [],
            "pressure_evidence_source_batch_counts": pressure_source_counts if isinstance(pressure_source_counts, dict) else {},
            "pressure_headloss_event_source_batch_count": pressure_event_source_count,
            "pressure_source_conflict_count": pressure_conflict_count,
            "resolved_pressure_source_conflict_count": resolved_pressure_conflict_count,
            "unresolved_pressure_source_conflict_count": unresolved_pressure_conflict_count,
            "pressure_source_resolution_record_count": pressure_resolution_record_count,
            "conflict_requires_operator_review": conflict_requires_review,
            "pressure_source_conflict_control_block": conflict_requires_review,
            "guardrail_mode": mode,
            "can_write_to_actuator": False,
            "can_write_to_release_gate": False,
        }

    @staticmethod
    def _float(values: dict[str, object], key: str, default: float = 0.0) -> float:
        value = values.get(key, default)
        if isinstance(value, int | float):
            return float(value)
        return default

    @staticmethod
    def _clip(value: float) -> float:
        return round(max(0.0, min(1.0, value)), 3)

    @staticmethod
    def _percentile(values: list[float], q: float) -> float:
        if not values:
            return 0.0
        ordered = sorted(values)
        index = min(len(ordered) - 1, max(0, round((len(ordered) - 1) * q)))
        return round(ordered[index], 3)

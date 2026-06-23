from __future__ import annotations

from collections.abc import Sequence

from water_ai.agents.base import BaseAgent
from water_ai.domain import AgentReport, QualityIssue, SensorReading, Severity


CONTROL_STATE_AXES = [
    "influent_disturbance_visibility",
    "reaction_state_visibility",
    "catalyst_state_visibility",
    "hydraulic_state_visibility",
    "release_risk_visibility",
    "control_latency_buffer",
    "soft_sensor_confidence",
    "field_replay_evidence",
    "action_interpretability",
    "cost_energy_efficiency",
]


class MultiFacilityCollaborativeControlAgent(BaseAgent):
    """Convert sparse sensing into multi-facility collaborative control candidates."""

    name = "multi_facility_collaborative_control_agent"

    def __init__(
        self,
        *,
        sparse_placement_metrics: dict[str, object] | None = None,
        observation_contract_metrics: dict[str, object] | None = None,
        catalyst_proxy_metrics: dict[str, object] | None = None,
        engineering_constraints_metrics: dict[str, object] | None = None,
        control_replay_stress_metrics: dict[str, object] | None = None,
        data_origin: str = "synthetic_coordination_prior",
        field_validation: dict[str, object] | None = None,
    ) -> None:
        self.sparse_placement_metrics = sparse_placement_metrics or {}
        self.observation_contract_metrics = observation_contract_metrics or {}
        self.catalyst_proxy_metrics = catalyst_proxy_metrics or {}
        self.engineering_constraints_metrics = engineering_constraints_metrics or {}
        self.control_replay_stress_metrics = control_replay_stress_metrics or {}
        self.data_origin = data_origin
        self.field_validation = field_validation or {}

    def run(self, readings: Sequence[SensorReading]) -> AgentReport:
        del readings
        sparse_context = self._sparse_context()
        facility_agents = self._facility_agents(sparse_context)
        facility_state_matrix = self._facility_state_matrix(facility_agents, sparse_context)
        joint_action_matrix = self._joint_action_matrix(facility_state_matrix, sparse_context)
        shared_experience_pool = self._shared_experience_pool(joint_action_matrix)
        distilled_policy = self._decision_tree_distillation(joint_action_matrix, sparse_context)
        readiness = self._readiness(sparse_context, distilled_policy)
        issues = self._issues(sparse_context, distilled_policy, readiness)
        recommendations = self._recommendations(sparse_context, distilled_policy, readiness)
        summary = (
            f"多设施协同控制：{readiness['coordination_status']}；"
            f"设施 agent {len(facility_agents)} 个，"
            f"候选联动动作 {len(joint_action_matrix)} 个，"
            f"策略蒸馏准确度 {distilled_policy['distilled_policy_accuracy_proxy']:.3f}。"
        )
        confidence = round(
            min(0.90, max(0.18, 0.36 + 0.42 * readiness["coordination_readiness_score"] - 0.035 * len(issues))),
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
                "sparse_context": sparse_context,
                "control_state_axes": CONTROL_STATE_AXES,
                "facility_agents": facility_agents,
                "facility_state_matrix": facility_state_matrix,
                "joint_action_matrix": joint_action_matrix,
                "reward_contract": self._reward_contract(),
                "engineering_constraints_context": self._engineering_constraints_context(),
                "control_replay_guardrail_context": self._control_replay_guardrail_context(sparse_context),
                "shared_experience_pool": shared_experience_pool,
                "decision_tree_distillation": distilled_policy,
                "readiness": readiness,
            },
        )

    def _sparse_context(self) -> dict[str, object]:
        coverage = self.sparse_placement_metrics.get("coverage", {})
        if not isinstance(coverage, dict):
            coverage = {}
        readiness = self.sparse_placement_metrics.get("readiness", {})
        if not isinstance(readiness, dict):
            readiness = {}
        selected_plan = self.sparse_placement_metrics.get("selected_sensor_plan", [])
        if not isinstance(selected_plan, list):
            selected_plan = []
        selected_nodes = sorted({str(item.get("node_id", "")) for item in selected_plan if isinstance(item, dict) and item.get("node_id")})
        selected_modalities = sorted(
            {str(item.get("modality", "")) for item in selected_plan if isinstance(item, dict) and item.get("modality")}
        )
        coverage_patch = self._observation_contract_context()
        coverage = {
            "pollutant_residual_observability": self._number(coverage, "pollutant_residual_observability", 0.68),
            "reaction_completion_observability": self._number(coverage, "reaction_completion_observability", 0.64),
            "oxidant_observability": self._number(coverage, "oxidant_observability", 0.62),
            "catalyst_activity_observability": self._number(coverage, "catalyst_activity_observability", 0.30),
            "matrix_interference_observability": self._number(coverage, "matrix_interference_observability", 0.70),
            "hydraulic_observability": self._number(coverage, "hydraulic_observability", 0.60),
            "fault_classification_observability": self._number(coverage, "fault_classification_observability", 0.55),
            "control_latency_gain": self._number(coverage, "control_latency_gain", 0.70),
            "soft_sensor_reconstruction_gain": self._number(coverage, "soft_sensor_reconstruction_gain", 0.65),
            "cost_efficiency": self._number(coverage, "cost_efficiency", 0.85),
            "weak_state_coverage": self._number(coverage, "weak_state_coverage", 0.30),
        }
        if coverage_patch["contract_ready"]:
            coverage["catalyst_activity_observability"] = max(
                coverage["catalyst_activity_observability"],
                float(coverage_patch["proxy_enhanced_catalyst_activity_observability"]),
            )
            coverage["weak_state_coverage"] = max(
                coverage["weak_state_coverage"],
                float(coverage_patch["proxy_enhanced_weak_state_coverage"]),
            )
        if coverage_patch["contract_pairs"]:
            selected_nodes = sorted({pair.split(":", 1)[0] for pair in coverage_patch["contract_pairs"] if ":" in pair})
            selected_modalities = sorted({pair.split(":", 1)[1] for pair in coverage_patch["contract_pairs"] if ":" in pair})
        return {
            "coverage": coverage,
            "selected_nodes": selected_nodes,
            "selected_modalities": selected_modalities,
            "selected_sensor_count": int(
                coverage_patch["sensor_count"] if coverage_patch["contract_ready"] else readiness.get("selected_sensor_count", len(selected_plan))
            ),
            "sparse_placement_status": str(readiness.get("sparse_placement_status", "unknown")),
            "observation_contract_context": coverage_patch,
            "pressure_headloss_control_boundary": coverage_patch["pressure_headloss_control_boundary"],
            "pressure_headloss_candidate_ids": coverage_patch["pressure_headloss_candidate_ids"],
            "catalyst_proxy_field_context": self._catalyst_proxy_field_context(),
            "data_origin": self.data_origin,
        }

    def _observation_contract_context(self) -> dict[str, object]:
        readiness = self.observation_contract_metrics.get("readiness", {})
        readiness = readiness if isinstance(readiness, dict) else {}
        recommended = self.observation_contract_metrics.get("recommended_observation_contract", {})
        recommended = recommended if isinstance(recommended, dict) else {}
        pressure_headloss_context = self._pressure_headloss_contract_context()
        contract_ready = (
            str(readiness.get("observation_contract_status", "")).startswith("synthetic_observation_contract_ready")
            and bool(readiness.get("budget_pass", False))
            and float(readiness.get("proxy_enhanced_weak_state_coverage", 0.0)) >= 0.55
        )
        return {
            "contract_ready": contract_ready,
            "contract_id": recommended.get("contract_id", "not_available"),
            "recommended_contract_id": readiness.get("recommended_contract_id", recommended.get("candidate_id", "not_available")),
            "contract_pairs": recommended.get("contract_pairs", []) if isinstance(recommended.get("contract_pairs", []), list) else [],
            "sensor_count": int(readiness.get("recommended_sensor_count", recommended.get("sensor_count", 0)) or 0),
            "proxy_enhanced_catalyst_activity_observability": float(
                recommended.get(
                    "proxy_enhanced_catalyst_activity_observability",
                    readiness.get("proxy_enhanced_weak_state_coverage", 0.0),
                )
            ),
            "proxy_enhanced_weak_state_coverage": float(readiness.get("proxy_enhanced_weak_state_coverage", 0.0)),
            "budget_pass": bool(readiness.get("budget_pass", False)),
            "field_topology_ready": bool(readiness.get("field_topology_ready", False)),
            "field_proxy_labels_ready": bool(readiness.get("field_proxy_labels_ready", False)),
            "field_missingness_ready": bool(readiness.get("field_missingness_ready", False)),
            "weak_axis_repair_status": str(readiness.get("weak_axis_repair_status", recommended.get("weak_axis_repair_status", "unknown"))),
            "weak_axis_repair_score": float(readiness.get("weak_axis_repair_score", recommended.get("weak_axis_repair_score", 0.0)) or 0.0),
            "field_repair_evidence_requirement_count": int(
                readiness.get(
                    "field_repair_evidence_requirement_count",
                    recommended.get("field_repair_evidence_requirement_count", 0),
                )
                or 0
            ),
            "pressure_headloss_context": pressure_headloss_context,
            "pressure_headloss_candidate_pool_status": pressure_headloss_context["pool_status"],
            "pressure_headloss_candidate_count": pressure_headloss_context["candidate_count"],
            "pressure_headloss_candidate_ids": pressure_headloss_context["candidate_ids"],
            "pressure_headloss_consumed_by_agent49": pressure_headloss_context["consumed_by_agent49"],
            "pressure_headloss_control_boundary": pressure_headloss_context["control_boundary"],
            "pressure_headloss_can_relax_control_guardrail": pressure_headloss_context[
                "can_relax_hydraulic_or_catalyst_guardrail"
            ],
            "field_boundary": (
                "observation contract can update design prior, but field topology/proxy labels/missingness are required before actuator use"
            ),
        }

    def _pressure_headloss_contract_context(self) -> dict[str, object]:
        readiness = self.observation_contract_metrics.get("readiness", {})
        readiness = readiness if isinstance(readiness, dict) else {}
        base_layout = self.observation_contract_metrics.get("base_layout_contract", {})
        base_layout = base_layout if isinstance(base_layout, dict) else {}
        field_requirements = self.observation_contract_metrics.get("field_validation_requirements", [])
        field_requirements = field_requirements if isinstance(field_requirements, list) else []
        pressure_requirement = {}
        for item in field_requirements:
            if isinstance(item, dict) and item.get("requirement_id") == "R2_FV4_agent48_hidden_state_requirement_patch":
                pressure_requirement = item
                break
        candidate_ids = [
            str(item)
            for item in base_layout.get(
                "pressure_headloss_candidate_ids",
                readiness.get(
                    "agent48_pressure_headloss_candidate_ids",
                    pressure_requirement.get("pressure_headloss_candidate_ids", []),
                ),
            )
            if item
        ]
        status = str(
            base_layout.get(
                "pressure_headloss_candidate_pool_status",
                readiness.get(
                    "agent48_pressure_headloss_candidate_pool_status",
                    pressure_requirement.get("pressure_headloss_candidate_pool_status", "missing_pressure_headloss_pool"),
                ),
            )
        )
        field_contract = base_layout.get("pressure_headloss_field_package_contract", {})
        field_contract = field_contract if isinstance(field_contract, dict) else {}
        required_tables = field_contract.get("required_tables", pressure_requirement.get("required_tables", []))
        minimum_batches = int(
            field_contract.get(
                "minimum_matched_batch_count",
                pressure_requirement.get("minimum_matched_batch_count", 3),
            )
            or 3
        )
        field_topology_ready = bool(readiness.get("field_topology_ready", False))
        field_proxy_ready = bool(readiness.get("field_proxy_labels_ready", False))
        field_missingness_ready = bool(readiness.get("field_missingness_ready", False))
        can_relax = bool(candidate_ids) and field_topology_ready and field_proxy_ready and field_missingness_ready
        return {
            "contract_id": "R8c_pressure_headloss_control_boundary",
            "pool_status": status,
            "candidate_count": len(candidate_ids),
            "candidate_ids": candidate_ids,
            "required_tables": [str(item) for item in required_tables],
            "minimum_matched_batch_count": minimum_batches,
            "consumed_by_agent49": bool(candidate_ids),
            "can_update_state_vector_design_prior": bool(candidate_ids),
            "can_relax_hydraulic_or_catalyst_guardrail": can_relax,
            "can_write_to_actuator": False,
            "can_write_to_release_gate": False,
            "control_boundary": (
                "pressure/headloss may shape hydraulic and catalyst-state explanation priors, "
                "but cannot relax recycle/catalyst guardrails or promote actuator use without field topology, "
                "matched lab labels and missingness replay."
                if candidate_ids
                else "pressure/headloss candidate pool not supplied"
            ),
        }

    def _facility_agents(self, sparse_context: dict[str, object]) -> list[dict[str, object]]:
        selected_nodes = set(sparse_context["selected_nodes"]) if isinstance(sparse_context["selected_nodes"], list) else set()
        return [
            {
                "facility_agent_id": "F0_equalization_buffer_agent",
                "facility_role": "均质/暂存/进水扰动削峰",
                "observed_nodes": sorted(selected_nodes & {"N0_influent", "N1_equalization_tank"}),
                "candidate_actions": ["hold_and_homogenize", "divert_to_buffer", "reduce_intake_fraction"],
                "local_objective": "降低进水冲击和基质突变，给软传感与离线验证争取时间。",
            },
            {
                "facility_agent_id": "F1_reaction_core_agent",
                "facility_role": "反应核心与药剂/氧化剂调节",
                "observed_nodes": sorted(selected_nodes & {"N2_reactor_mid"}),
                "candidate_actions": ["extend_reaction_retention", "adjust_oxidant_dose", "pulse_mixing"],
                "local_objective": "补足反应完成度与氧化剂余量，避免把末端不达标全部推给回流。",
            },
            {
                "facility_agent_id": "F2_catalyst_bed_agent",
                "facility_role": "催化剂床保护、再生与切换",
                "observed_nodes": sorted(selected_nodes & {"N3_catalyst_bed_outlet"}),
                "candidate_actions": ["protect_catalyst_bed", "schedule_regeneration", "switch_parallel_bed"],
                "local_objective": "区分基质抑制、催化剂失活和寿命衰减，避免盲目再生或过早更换。",
            },
            {
                "facility_agent_id": "F3_recirculation_loop_agent",
                "facility_role": "回流、延长停留时间和低频观测缓冲",
                "observed_nodes": sorted(selected_nodes & {"N4_recirculation_loop"}),
                "candidate_actions": ["increase_recycle_ratio", "extend_loop_retention", "hold_for_slow_evidence"],
                "local_objective": "用循环结构换取决策时间，让低成本传感和慢证据仍能参与控制。",
            },
            {
                "facility_agent_id": "F4_polishing_release_agent",
                "facility_role": "末端精处理、暂存验证与放行阻断",
                "observed_nodes": sorted(selected_nodes & {"N5_polishing_inlet", "N6_effluent"}),
                "candidate_actions": ["route_to_polishing", "block_release_until_lab", "conditional_release_after_gate"],
                "local_objective": "把达标放行从单次预测改成证据门控，优先防止误放行。",
            },
        ]

    def _facility_state_matrix(
        self, facility_agents: list[dict[str, object]], sparse_context: dict[str, object]
    ) -> list[dict[str, object]]:
        coverage = sparse_context["coverage"] if isinstance(sparse_context["coverage"], dict) else {}
        matrix: list[dict[str, object]] = []
        for agent in facility_agents:
            agent_id = str(agent["facility_agent_id"])
            if "equalization" in agent_id:
                vector = {
                    "influent_disturbance_visibility": coverage["matrix_interference_observability"],
                    "reaction_state_visibility": 0.35 * coverage["reaction_completion_observability"],
                    "catalyst_state_visibility": 0.20 * coverage["catalyst_activity_observability"],
                    "hydraulic_state_visibility": 0.72 * coverage["hydraulic_observability"],
                    "release_risk_visibility": 0.45 * coverage["pollutant_residual_observability"],
                    "control_latency_buffer": coverage["control_latency_gain"],
                    "soft_sensor_confidence": 0.65 * coverage["soft_sensor_reconstruction_gain"],
                    "field_replay_evidence": self._field_evidence_score(),
                    "action_interpretability": 0.82,
                    "cost_energy_efficiency": coverage["cost_efficiency"],
                }
            elif "reaction_core" in agent_id:
                vector = {
                    "influent_disturbance_visibility": 0.58 * coverage["matrix_interference_observability"],
                    "reaction_state_visibility": coverage["reaction_completion_observability"],
                    "catalyst_state_visibility": 0.52 * coverage["catalyst_activity_observability"],
                    "hydraulic_state_visibility": 0.55 * coverage["hydraulic_observability"],
                    "release_risk_visibility": 0.70 * coverage["pollutant_residual_observability"],
                    "control_latency_buffer": 0.70 * coverage["control_latency_gain"],
                    "soft_sensor_confidence": coverage["soft_sensor_reconstruction_gain"],
                    "field_replay_evidence": self._field_evidence_score(),
                    "action_interpretability": 0.74,
                    "cost_energy_efficiency": 0.80 * coverage["cost_efficiency"],
                }
            elif "catalyst_bed" in agent_id:
                vector = {
                    "influent_disturbance_visibility": 0.42 * coverage["matrix_interference_observability"],
                    "reaction_state_visibility": 0.70 * coverage["reaction_completion_observability"],
                    "catalyst_state_visibility": coverage["catalyst_activity_observability"],
                    "hydraulic_state_visibility": 0.45 * coverage["hydraulic_observability"],
                    "release_risk_visibility": 0.60 * coverage["pollutant_residual_observability"],
                    "control_latency_buffer": 0.58 * coverage["control_latency_gain"],
                    "soft_sensor_confidence": 0.76 * coverage["soft_sensor_reconstruction_gain"],
                    "field_replay_evidence": self._field_evidence_score(),
                    "action_interpretability": 0.78,
                    "cost_energy_efficiency": 0.62 * coverage["cost_efficiency"],
                }
            elif "recirculation" in agent_id:
                vector = {
                    "influent_disturbance_visibility": 0.78 * coverage["matrix_interference_observability"],
                    "reaction_state_visibility": 0.76 * coverage["reaction_completion_observability"],
                    "catalyst_state_visibility": 0.48 * coverage["catalyst_activity_observability"],
                    "hydraulic_state_visibility": coverage["hydraulic_observability"],
                    "release_risk_visibility": 0.72 * coverage["pollutant_residual_observability"],
                    "control_latency_buffer": coverage["control_latency_gain"],
                    "soft_sensor_confidence": coverage["soft_sensor_reconstruction_gain"],
                    "field_replay_evidence": self._field_evidence_score(),
                    "action_interpretability": 0.84,
                    "cost_energy_efficiency": 0.74 * coverage["cost_efficiency"],
                }
            else:
                vector = {
                    "influent_disturbance_visibility": 0.38 * coverage["matrix_interference_observability"],
                    "reaction_state_visibility": 0.72 * coverage["reaction_completion_observability"],
                    "catalyst_state_visibility": 0.42 * coverage["catalyst_activity_observability"],
                    "hydraulic_state_visibility": 0.38 * coverage["hydraulic_observability"],
                    "release_risk_visibility": coverage["pollutant_residual_observability"],
                    "control_latency_buffer": 0.46 * coverage["control_latency_gain"],
                    "soft_sensor_confidence": 0.86 * coverage["soft_sensor_reconstruction_gain"],
                    "field_replay_evidence": self._field_evidence_score(),
                    "action_interpretability": 0.88,
                    "cost_energy_efficiency": 0.68 * coverage["cost_efficiency"],
                }
            matrix.append(
                {
                    "facility_agent_id": agent_id,
                    "facility_role": agent["facility_role"],
                    "observed_nodes": agent["observed_nodes"],
                    "state_vector": {axis: round(max(0.0, min(1.0, value)), 3) for axis, value in vector.items()},
                    "candidate_actions": agent["candidate_actions"],
                }
            )
        return matrix

    def _joint_action_matrix(
        self, facility_state_matrix: list[dict[str, object]], sparse_context: dict[str, object]
    ) -> list[dict[str, object]]:
        candidates = [
            {
                "joint_action_id": "J0_matrix_shock_equalize_and_recycle",
                "facility_agents": ["F0_equalization_buffer_agent", "F3_recirculation_loop_agent"],
                "actions": ["hold_and_homogenize", "increase_recycle_ratio"],
                "control_intent": "基质冲击先削峰再回流，避免反应核心被瞬时负荷推入不可解释区。",
            },
            {
                "joint_action_id": "J1_reaction_completion_recovery",
                "facility_agents": ["F1_reaction_core_agent", "F3_recirculation_loop_agent"],
                "actions": ["adjust_oxidant_dose", "extend_loop_retention"],
                "control_intent": "反应不足时同步调药和延长停留时间，而不是只提高单一药剂。",
            },
            {
                "joint_action_id": "J2_catalyst_protection_before_regeneration",
                "facility_agents": ["F0_equalization_buffer_agent", "F2_catalyst_bed_agent"],
                "actions": ["reduce_intake_fraction", "protect_catalyst_bed"],
                "control_intent": "催化剂状态不清时先保护负荷，再决定再生、切换或更换。",
            },
            {
                "joint_action_id": "J3_polishing_and_release_gate",
                "facility_agents": ["F3_recirculation_loop_agent", "F4_polishing_release_agent"],
                "actions": ["hold_for_slow_evidence", "route_to_polishing"],
                "control_intent": "末端风险不清时进入精处理与慢证据门控，不允许仅凭 synthetic 软传感放行。",
            },
            {
                "joint_action_id": "J4_safe_low_cost_standby",
                "facility_agents": ["F0_equalization_buffer_agent", "F4_polishing_release_agent"],
                "actions": ["hold_and_homogenize", "block_release_until_lab"],
                "control_intent": "观测不足或策略不确定时选择低成本暂存与放行阻断。",
            },
        ]
        state_by_agent = {str(row["facility_agent_id"]): row["state_vector"] for row in facility_state_matrix}
        scored: list[dict[str, object]] = []
        for candidate in candidates:
            combined = self._combined_state(candidate["facility_agents"], state_by_agent)
            reward = self._reward_components(candidate["joint_action_id"], combined, sparse_context)
            engineering_patch = self._engineering_reward_patch(str(candidate["joint_action_id"]))
            reward = self._apply_engineering_reward_patch(reward, engineering_patch)
            control_replay_patch = self._control_replay_guardrail_patch(str(candidate["joint_action_id"]), sparse_context)
            reward = self._apply_control_replay_guardrail_patch(reward, control_replay_patch)
            scored.append(
                {
                    **candidate,
                    "combined_state_vector": combined,
                    "reward_components": reward,
                    "joint_policy_score": reward["weighted_reward"],
                    "engineering_constraint_evaluation": engineering_patch,
                    "control_replay_guardrail_evaluation": control_replay_patch,
                    "can_write_to_actuator": False,
                    "writeback_boundary": "synthetic 或未蒸馏验证阶段只能形成控制候选，不写入现场执行器。",
                }
            )
        return sorted(scored, key=lambda item: float(item["joint_policy_score"]), reverse=True)

    def _combined_state(self, agent_ids: list[str], state_by_agent: dict[str, dict[str, float]]) -> dict[str, float]:
        combined: dict[str, float] = {}
        for axis in CONTROL_STATE_AXES:
            values = [float(state_by_agent.get(agent_id, {}).get(axis, 0.0)) for agent_id in agent_ids]
            combined[axis] = round(max(values) if values else 0.0, 3)
        return combined

    def _reward_components(
        self, joint_action_id: str, state_vector: dict[str, float], sparse_context: dict[str, object]
    ) -> dict[str, float]:
        coverage = sparse_context["coverage"] if isinstance(sparse_context["coverage"], dict) else {}
        quality_reward = 0.46 * state_vector["release_risk_visibility"] + 0.26 * state_vector["reaction_state_visibility"]
        risk_reduction = 0.35 * state_vector["influent_disturbance_visibility"] + 0.25 * state_vector["catalyst_state_visibility"]
        latency_reward = state_vector["control_latency_buffer"]
        evidence_bonus = state_vector["field_replay_evidence"]
        interpretability_bonus = state_vector["action_interpretability"]
        cost_efficiency = state_vector["cost_energy_efficiency"]
        chemical_cost_penalty = 0.22 if "adjust_oxidant" in joint_action_id else 0.10
        energy_penalty = 0.18 if "recycle" in joint_action_id or "completion" in joint_action_id else 0.08
        weak_state_penalty = max(0.0, 0.55 - float(coverage.get("weak_state_coverage", 0.0)))
        weighted_reward = (
            0.28 * quality_reward
            + 0.22 * risk_reduction
            + 0.16 * latency_reward
            + 0.12 * evidence_bonus
            + 0.12 * interpretability_bonus
            + 0.10 * cost_efficiency
            - 0.07 * chemical_cost_penalty
            - 0.07 * energy_penalty
            - 0.12 * weak_state_penalty
        )
        return {
            "quality_reward": round(quality_reward, 3),
            "risk_reduction_reward": round(risk_reduction, 3),
            "latency_reward": round(latency_reward, 3),
            "field_evidence_bonus": round(evidence_bonus, 3),
            "interpretability_bonus": round(interpretability_bonus, 3),
            "cost_energy_efficiency": round(cost_efficiency, 3),
            "chemical_cost_penalty": round(chemical_cost_penalty, 3),
            "energy_penalty": round(energy_penalty, 3),
            "weak_state_penalty": round(weak_state_penalty, 3),
            "engineering_constraint_penalty": 0.0,
            "execution_feasibility": 1.0,
            "weighted_reward": round(max(0.0, min(1.0, weighted_reward)), 3),
        }

    @staticmethod
    def _apply_engineering_reward_patch(
        reward: dict[str, float],
        engineering_patch: dict[str, object],
    ) -> dict[str, float]:
        if not engineering_patch:
            return {
                **reward,
                "control_replay_guardrail_penalty": 0.0,
                "control_replay_guardrail_bonus": 0.0,
            }
        engineering_penalty = float(engineering_patch.get("engineering_constraint_penalty", 0.0))
        execution_feasibility = float(engineering_patch.get("execution_feasibility", 1.0))
        hard_blocked = bool(engineering_patch.get("hard_blocked_by_engineering", False))
        adjusted = float(reward["weighted_reward"]) - 0.24 * engineering_penalty + 0.06 * (execution_feasibility - 0.50)
        if hard_blocked:
            adjusted -= 0.18
        patched = {
            **reward,
            "engineering_constraint_penalty": round(engineering_penalty, 3),
            "execution_feasibility": round(max(0.0, min(1.0, execution_feasibility)), 3),
            "weighted_reward": round(max(0.0, min(1.0, adjusted)), 3),
        }
        return patched

    def _control_replay_guardrail_context(self, sparse_context: dict[str, object]) -> dict[str, object]:
        readiness = self.control_replay_stress_metrics.get("readiness", {})
        readiness = readiness if isinstance(readiness, dict) else {}
        patch = self.control_replay_stress_metrics.get("reward_prior_patch", {})
        patch = patch if isinstance(patch, dict) else {}
        metrics = self.control_replay_stress_metrics.get("counterfactual_metrics", {})
        metrics = metrics if isinstance(metrics, dict) else {}
        candidate_rules = patch.get("candidate_rules", [])
        candidate_rules = candidate_rules if isinstance(candidate_rules, list) else []
        observation_context = sparse_context.get("observation_contract_context", {})
        observation_context = observation_context if isinstance(observation_context, dict) else {}
        pressure_context = observation_context.get("pressure_headloss_context", {})
        pressure_context = pressure_context if isinstance(pressure_context, dict) else {}
        catalyst_context = self._catalyst_proxy_field_context()
        guardrail_candidate = metrics.get("guardrail_candidate", {})
        guardrail_candidate = guardrail_candidate if isinstance(guardrail_candidate, dict) else {}
        field_ready = bool(readiness.get("field_ready", False))
        available = bool(readiness.get("can_update_agent49_reward_prior", False)) and bool(candidate_rules)
        conflict_requires_review = bool(catalyst_context.get("conflict_requires_operator_review", False))
        field_proxy_labels_ready = (
            bool(observation_context.get("field_proxy_labels_ready", False))
            or bool(catalyst_context.get("field_validation_pass", False))
        ) and not conflict_requires_review
        return {
            "reward_prior_guardrail_available": available,
            "patch_id": patch.get("patch_id", "not_available"),
            "control_replay_stress_status": readiness.get("control_replay_stress_status", "not_available"),
            "candidate_rule_ids": [str(item.get("rule_id")) for item in candidate_rules if isinstance(item, dict)],
            "triggered_case_count": len(patch.get("triggered_by_cases", []))
            if isinstance(patch.get("triggered_by_cases", []), list)
            else 0,
            "guardrail_candidate_accuracy": float(guardrail_candidate.get("joint_action_accuracy", 0.0)),
            "p95_reward_regret_delta_guardrail": float(metrics.get("p95_reward_regret_delta_guardrail", 0.0)),
            "protective_false_positive_cost_delta_guardrail": float(
                metrics.get("protective_false_positive_cost_delta_guardrail", 0.0)
            ),
            "field_replay_coverage": float(metrics.get("field_replay_coverage", 0.0)),
            "field_ready": field_ready,
            "field_proxy_labels_ready": field_proxy_labels_ready,
            "catalyst_proxy_summary_status": catalyst_context["summary_status"],
            "catalyst_proxy_ready_for_agent51_validation": catalyst_context["ready_for_agent51_validation"],
            "catalyst_proxy_field_validation_pass": catalyst_context["field_validation_pass"],
            "catalyst_proxy_scoreable_batch_count": catalyst_context["scoreable_batch_count"],
            "catalyst_proxy_matched_batch_count": catalyst_context["matched_batch_count"],
            "catalyst_proxy_holdout_mae": catalyst_context["holdout_mae"],
            "catalyst_proxy_label_correlation": catalyst_context["proxy_label_correlation"],
            "catalyst_proxy_missing_required_signals": catalyst_context["missing_required_signals"],
            "accepted_pressure_evidence_sources": catalyst_context["accepted_pressure_evidence_sources"],
            "pressure_evidence_source_batch_counts": catalyst_context["pressure_evidence_source_batch_counts"],
            "pressure_headloss_event_source_batch_count": catalyst_context[
                "pressure_headloss_event_source_batch_count"
            ],
            "pressure_source_conflict_count": catalyst_context["pressure_source_conflict_count"],
            "resolved_pressure_source_conflict_count": catalyst_context[
                "resolved_pressure_source_conflict_count"
            ],
            "unresolved_pressure_source_conflict_count": catalyst_context[
                "unresolved_pressure_source_conflict_count"
            ],
            "pressure_source_resolution_record_count": catalyst_context[
                "pressure_source_resolution_record_count"
            ],
            "pressure_source_conflicts": catalyst_context["pressure_source_conflicts"],
            "unresolved_pressure_source_conflicts": catalyst_context["unresolved_pressure_source_conflicts"],
            "pressure_source_resolutions": catalyst_context["pressure_source_resolutions"],
            "conflict_requires_operator_review": conflict_requires_review,
            "pressure_source_conflict_control_block": catalyst_context["pressure_source_conflict_control_block"],
            "catalyst_guardrail_mode": catalyst_context["guardrail_mode"],
            "pressure_headloss_candidate_pool_status": pressure_context.get(
                "pool_status",
                "missing_pressure_headloss_pool",
            ),
            "pressure_headloss_candidate_count": int(pressure_context.get("candidate_count", 0) or 0),
            "pressure_headloss_candidate_ids": pressure_context.get("candidate_ids", []),
            "pressure_headloss_consumed_by_agent49": bool(pressure_context.get("consumed_by_agent49", False)),
            "pressure_headloss_control_boundary": pressure_context.get(
                "control_boundary",
                "pressure/headloss candidate pool not supplied",
            ),
            "pressure_headloss_can_relax_control_guardrail": bool(
                pressure_context.get("can_relax_hydraulic_or_catalyst_guardrail", False)
            ),
            "hydraulic_execution_field_ready": field_ready,
            "can_write_to_actuator": False,
            "can_write_to_release_gate": False,
            "field_boundary": (
                "R3b reward prior guardrails can change synthetic reward ranking and explanation rules only; "
                "field replay is required before actuator or release-gate promotion."
            ),
        }

    def _control_replay_guardrail_patch(
        self,
        joint_action_id: str,
        sparse_context: dict[str, object],
    ) -> dict[str, object]:
        context = self._control_replay_guardrail_context(sparse_context)
        if not context["reward_prior_guardrail_available"]:
            return {}
        rule_ids = set(context["candidate_rule_ids"]) if isinstance(context["candidate_rule_ids"], list) else set()
        patches: list[dict[str, object]] = []
        if (
            "R3G1_catalyst_uncertain_requires_standby_or_human_review" in rule_ids
            and not bool(context["field_proxy_labels_ready"])
        ):
            if joint_action_id == "J2_catalyst_protection_before_regeneration":
                patches.append(
                    {
                        "rule_id": "R3G1_catalyst_uncertain_requires_standby_or_human_review",
                        "penalty": 0.16,
                        "bonus": 0.0,
                        "preferred_action_id": "J4_safe_low_cost_standby",
                        "requires_human_review": True,
                        "reason": (
                            "catalyst proxy labels are not field validated; avoid autonomous protective/regeneration action. "
                            f"Agent51 summary={context['catalyst_proxy_summary_status']}, "
                            f"scoreable_batches={context['catalyst_proxy_scoreable_batch_count']}."
                        ),
                    }
                )
            elif joint_action_id == "J4_safe_low_cost_standby":
                patches.append(
                    {
                        "rule_id": "R3G1_catalyst_uncertain_requires_standby_or_human_review",
                        "penalty": 0.0,
                        "bonus": 0.045,
                        "preferred_action_id": "J4_safe_low_cost_standby",
                        "requires_human_review": False,
                        "reason": (
                            "safe standby is the R3 guardrail candidate under unvalidated catalyst proxy labels. "
                            f"Agent51 guardrail mode={context['catalyst_guardrail_mode']}."
                        ),
                    }
                )
        if (
            "R3G2_hydraulic_delay_unknown_blocks_recycle" in rule_ids
            and not bool(context["hydraulic_execution_field_ready"])
        ):
            if joint_action_id == "J0_matrix_shock_equalize_and_recycle":
                patches.append(
                    {
                        "rule_id": "R3G2_hydraulic_delay_unknown_blocks_recycle",
                        "penalty": 0.14,
                        "bonus": 0.0,
                        "preferred_action_id": "J3_polishing_and_release_gate",
                        "requires_human_review": True,
                        "reason": "tank storage margin and actuator latency evidence are missing; recycle escalation remains high regret.",
                    }
                )
            elif joint_action_id == "J3_polishing_and_release_gate":
                patches.append(
                    {
                        "rule_id": "R3G2_hydraulic_delay_unknown_blocks_recycle",
                        "penalty": 0.0,
                        "bonus": 0.04,
                        "preferred_action_id": "J3_polishing_and_release_gate",
                        "requires_human_review": False,
                        "reason": "polishing and slow-evidence gate is the R3 guardrail candidate under hydraulic delay uncertainty.",
                    }
                )
        if not patches:
            return {
                "guardrail_patch_applied": False,
                "source_patch_id": context["patch_id"],
                "reason": "no R3 guardrail rule targets this joint action.",
            }
        penalty = round(sum(float(item["penalty"]) for item in patches), 3)
        bonus = round(sum(float(item["bonus"]) for item in patches), 3)
        return {
            "guardrail_patch_applied": True,
            "source_patch_id": context["patch_id"],
            "rule_ids": [str(item["rule_id"]) for item in patches],
            "penalty": penalty,
            "bonus": bonus,
            "preferred_action_ids": sorted({str(item["preferred_action_id"]) for item in patches}),
            "requires_human_review": any(bool(item["requires_human_review"]) for item in patches),
            "reasons": [str(item["reason"]) for item in patches],
            "field_boundary": context["field_boundary"],
        }

    @staticmethod
    def _apply_control_replay_guardrail_patch(
        reward: dict[str, float],
        guardrail_patch: dict[str, object],
    ) -> dict[str, float]:
        if not guardrail_patch or not guardrail_patch.get("guardrail_patch_applied", False):
            return {
                **reward,
                "control_replay_guardrail_penalty": 0.0,
                "control_replay_guardrail_bonus": 0.0,
            }
        penalty = float(guardrail_patch.get("penalty", 0.0))
        bonus = float(guardrail_patch.get("bonus", 0.0))
        adjusted = float(reward["weighted_reward"]) - penalty + bonus
        return {
            **reward,
            "control_replay_guardrail_penalty": round(penalty, 3),
            "control_replay_guardrail_bonus": round(bonus, 3),
            "weighted_reward": round(max(0.0, min(1.0, adjusted)), 3),
        }

    def _shared_experience_pool(self, joint_action_matrix: list[dict[str, object]]) -> dict[str, object]:
        return {
            "pool_id": "multi_facility_state_action_experience_pool",
            "record_schema": [
                "batch_id",
                "timestamp_min",
                "facility_agent_id",
                "state_vector",
                "joint_action_id",
                "local_action",
                "reward_components",
                "downstream_lab_label",
                "operator_override",
                "actuator_result",
            ],
            "priority_replay_keys": [
                "matrix_shock",
                "catalyst_activity_low",
                "false_positive_protective_action",
                "release_block_correctness",
                "hydraulic_delay_violation",
                "R3_counterfactual_guardrail_case",
            ],
            "seed_actions": [item["joint_action_id"] for item in joint_action_matrix[:3]],
            "field_requirement": "需要真实多节点 sensor/lab/operation/action replay 后才能训练或更新协同控制策略。",
        }

    def _decision_tree_distillation(
        self, joint_action_matrix: list[dict[str, object]], sparse_context: dict[str, object]
    ) -> dict[str, object]:
        coverage = sparse_context["coverage"] if isinstance(sparse_context["coverage"], dict) else {}
        field_accuracy = self._number(self.field_validation, "distilled_policy_accuracy", 0.0)
        if self.data_origin == "field_coordination_replay" and field_accuracy > 0.0:
            accuracy = field_accuracy
        else:
            top_margin = 0.0
            if len(joint_action_matrix) >= 2:
                top_margin = float(joint_action_matrix[0]["joint_policy_score"]) - float(joint_action_matrix[1]["joint_policy_score"])
            accuracy = min(
                0.86,
                0.54
                + 0.12 * float(coverage.get("fault_classification_observability", 0.0))
                + 0.10 * float(coverage.get("soft_sensor_reconstruction_gain", 0.0))
                + 0.08 * float(coverage.get("control_latency_gain", 0.0))
                + 0.22 * max(0.0, min(1.0, top_margin * 4.0)),
            )
        rules = [
            {
                "rule_id": "R1_matrix_shock_protective_loop",
                "if": "matrix_interference_observability >= 0.70 and control_latency_gain >= 0.70",
                "then": "J0_matrix_shock_equalize_and_recycle",
                "engineering_meaning": "发现基质冲击时优先均质暂存和回流削峰。",
            },
            {
                "rule_id": "R2_reaction_completion_recovery",
                "if": "reaction_completion_observability >= 0.65 and oxidant_observability >= 0.65",
                "then": "J1_reaction_completion_recovery",
                "engineering_meaning": "反应不足且氧化剂状态可观测时联动调药和延长停留。",
            },
            {
                "rule_id": "R3_catalyst_uncertainty_block",
                "if": "catalyst_activity_observability < 0.55",
                "then": "J2_catalyst_protection_before_regeneration with human_review",
                "engineering_meaning": "催化剂状态不可观测时先保护负荷，不自动再生或切换。",
            },
            {
                "rule_id": "R4_release_gate_block",
                "if": "field_replay_evidence < 0.85 or soft_sensor field holdout not passed",
                "then": "J3_polishing_and_release_gate",
                "engineering_meaning": "放行必须等待现场证据门，不能由 synthetic 策略直接决定。",
            },
        ]
        guardrail_context = self._control_replay_guardrail_context(sparse_context)
        if guardrail_context["reward_prior_guardrail_available"]:
            rules.extend(
                [
                    {
                        "rule_id": "R3G1_catalyst_uncertain_requires_standby_or_human_review",
                        "if": "catalyst proxy labels are not field validated and catalyst action would protect/regenerate",
                        "then": "prefer J4_safe_low_cost_standby or require human-reviewed catalyst protection",
                        "engineering_meaning": "R3 反事实压力测试发现催化剂低代理证据会触发保护性误动作，先暂存和阻断放行。",
                    },
                    {
                        "rule_id": "R3G2_hydraulic_delay_unknown_blocks_recycle",
                        "if": "tank storage margin or actuator latency evidence is missing and recycle escalation is proposed",
                        "then": "prefer J3_polishing_and_release_gate",
                        "engineering_meaning": "水力延迟和执行证据不足时，不把回流升级当成默认安全动作。",
                    },
                ]
            )
        if guardrail_context["pressure_headloss_consumed_by_agent49"]:
            rules.append(
                {
                    "rule_id": "R8C_pressure_headloss_candidate_boundary",
                    "if": "pressure/headloss candidate exists but field topology, matched lab labels or missingness replay are incomplete",
                    "then": "use as explanation prior only; do not relax hydraulic delay or catalyst guardrails",
                    "engineering_meaning": "压降/水头损失可帮助解释床层堵塞、催化剂衰减和水力异常，但现场证据前不能推动回流升级、再生或执行器动作。",
                }
            )
        if guardrail_context["pressure_source_conflict_control_block"]:
            rules.append(
                {
                    "rule_id": "R8K_pressure_source_conflict_requires_operator_review",
                    "if": "node pressure and pressure/headloss event pressure disagree beyond calibration tolerance",
                    "then": "keep catalyst and hydraulic guardrails; block autonomous relaxation until operator review",
                    "engineering_meaning": "同一批次的压降证据出现双源冲突时，系统承认水力代理不可用，而不是用冲突压力值支撑回流、再生或放行。",
                }
            )
        return {
            "distillation_method": "ID3_style_decision_tree_surrogate",
            "distilled_policy_accuracy_proxy": round(max(0.0, min(1.0, accuracy)), 3),
            "minimum_required_accuracy": 0.90,
            "tree_rules": rules,
            "top_ranked_action": joint_action_matrix[0]["joint_action_id"] if joint_action_matrix else None,
            "can_replace_black_box_policy": self.data_origin == "field_coordination_replay" and accuracy >= 0.90,
            "distillation_boundary": "当前规则树是协同策略的白箱代理草案，未经过真实状态-动作标签验证前不能作为现场控制器。",
        }

    def _readiness(self, sparse_context: dict[str, object], distilled_policy: dict[str, object]) -> dict[str, object]:
        coverage = sparse_context["coverage"] if isinstance(sparse_context["coverage"], dict) else {}
        field_action_accuracy = self._number(self.field_validation, "joint_action_accuracy", 0.0)
        field_reward_regret = self._number(self.field_validation, "reward_regret", 1.0)
        field_replay_coverage = self._number(self.field_validation, "field_replay_coverage", 0.0)
        field_ready = (
            self.data_origin == "field_coordination_replay"
            and field_action_accuracy >= 0.90
            and field_reward_regret <= 0.08
            and field_replay_coverage >= 0.85
        )
        weak_ready = float(coverage.get("weak_state_coverage", 0.0)) >= 0.55
        distilled_ready = bool(distilled_policy["can_replace_black_box_policy"])
        engineering_context = self._engineering_constraints_context()
        engineering_integrated = bool(engineering_context.get("agent49_reward_patch_available", False))
        engineering_ready = bool(engineering_context.get("field_ready", False))
        guardrail_context = self._control_replay_guardrail_context(sparse_context)
        control_replay_guardrails_integrated = bool(guardrail_context.get("reward_prior_guardrail_available", False))
        control_replay_guardrails_field_ready = bool(guardrail_context.get("field_ready", False))
        sparse_ready = str(sparse_context["sparse_placement_status"]).startswith("field_") or str(
            sparse_context["sparse_placement_status"]
        ).startswith("sparse_sensor_layout_ready")
        score = round(
            0.18 * float(sparse_ready)
            + 0.18 * float(weak_ready)
            + 0.18 * max(0.0, min(1.0, field_action_accuracy))
            + 0.14 * max(0.0, min(1.0, 1.0 - field_reward_regret))
            + 0.14 * max(0.0, min(1.0, field_replay_coverage))
            + 0.18 * float(distilled_ready),
            3,
        )
        if not field_ready:
            status = "synthetic_collaborative_policy_needs_field_replay"
        elif not weak_ready:
            status = "field_collaborative_policy_blocked_by_weak_state"
        elif not distilled_ready:
            status = "field_collaborative_policy_needs_distillation_review"
        else:
            status = "field_collaborative_policy_candidate_ready"
        return {
            "coordination_status": status,
            "coordination_readiness_score": score,
            "field_ready": field_ready,
            "weak_state_ready": weak_ready,
            "distilled_policy_ready": distilled_ready,
            "engineering_constraints_integrated": engineering_integrated,
            "engineering_constraints_field_ready": engineering_ready,
            "control_replay_guardrails_integrated": control_replay_guardrails_integrated,
            "control_replay_guardrails_field_ready": control_replay_guardrails_field_ready,
            "can_write_to_actuator": status == "field_collaborative_policy_candidate_ready"
            and (not engineering_integrated or engineering_ready),
            "can_write_to_release_gate": False,
            "field_validation": self.field_validation,
        }

    def _issues(
        self,
        sparse_context: dict[str, object],
        distilled_policy: dict[str, object],
        readiness: dict[str, object],
    ) -> list[QualityIssue]:
        issues: list[QualityIssue] = []
        coverage = sparse_context["coverage"] if isinstance(sparse_context["coverage"], dict) else {}
        if not readiness["field_ready"]:
            issues.append(
                QualityIssue(
                    sensor="multi_facility_collaborative_control",
                    issue_type="field_coordination_replay_required",
                    severity=Severity.WARNING,
                    message="当前多设施协同策略只是在稀疏观测矩阵上的候选策略，需要真实多节点状态-动作-结果 replay 验证。",
                    evidence=readiness,
                )
            )
        if float(coverage.get("catalyst_activity_observability", 0.0)) < 0.55:
            issues.append(
                QualityIssue(
                    sensor="multi_facility_collaborative_control",
                    issue_type="catalyst_state_too_weak_for_autonomous_policy",
                    severity=Severity.WARNING,
                    message="催化剂活性观测仍弱，不适合训练或执行自主催化剂再生/切换策略。",
                    evidence=coverage,
                )
            )
        observation_context = sparse_context.get("observation_contract_context", {})
        observation_context = observation_context if isinstance(observation_context, dict) else {}
        if (
            str(observation_context.get("weak_axis_repair_status", ""))
            == "agent48_catalyst_axis_requires_proxy_patch_and_field_label"
            and not bool(self._catalyst_proxy_field_context().get("field_validation_pass", False))
            and not bool(observation_context.get("field_proxy_labels_ready", False))
        ):
            issues.append(
                QualityIssue(
                    sensor="multi_facility_collaborative_control",
                    issue_type="catalyst_axis_repair_prior_not_field_validated",
                    severity=Severity.INFO,
                    message="催化剂活性观测已通过 Agent51/R2 形成修复先验，但缺 field proxy labels，协同控制仍不能解除催化剂保护规则。",
                    evidence=observation_context,
                )
            )
        if bool(observation_context.get("pressure_headloss_consumed_by_agent49", False)) and not bool(
            observation_context.get("pressure_headloss_can_relax_control_guardrail", False)
        ):
            issues.append(
                QualityIssue(
                    sensor="multi_facility_collaborative_control",
                    issue_type="pressure_headloss_candidate_not_field_validated_for_control",
                    severity=Severity.INFO,
                    message="Agent49 已读取 pressure/headloss 候选合同，但它只能作为水力/催化剂状态解释先验，不能解除回流或催化剂动作保护边界。",
                    evidence=observation_context.get("pressure_headloss_context", {}),
                )
            )
        catalyst_context = self._catalyst_proxy_field_context()
        if catalyst_context["conflict_requires_operator_review"]:
            issues.append(
                QualityIssue(
                    sensor="agent51_pressure_headloss_source",
                    issue_type="pressure_source_conflict_blocks_control_relaxation",
                    severity=Severity.WARNING,
                    message="Agent51 发现 node pressure 与 pressure/headloss event 同批次冲突；Agent49 必须继续保留催化剂/水力保护边界，等待人工复核或现场校准。",
                    evidence={
                        "pressure_source_conflict_count": catalyst_context["pressure_source_conflict_count"],
                        "pressure_source_conflicts": catalyst_context["pressure_source_conflicts"],
                        "guardrail_mode": catalyst_context["guardrail_mode"],
                    },
                )
            )
        if catalyst_context["summary_supplied"] and not catalyst_context["field_validation_pass"]:
            issues.append(
                QualityIssue(
                    sensor="agent51_catalyst_proxy_holdout",
                    issue_type="agent51_catalyst_proxy_not_ready_for_control_relaxation",
                    severity=Severity.WARNING,
                    message="Agent49 已读取 Agent51 field holdout summary，但催化剂代理尚未通过现场验证，因此控制侧继续保留 R3G1 保护边界。",
                    evidence=catalyst_context,
                )
            )
        if float(distilled_policy["distilled_policy_accuracy_proxy"]) < float(distilled_policy["minimum_required_accuracy"]):
            issues.append(
                QualityIssue(
                    sensor="multi_facility_collaborative_control",
                    issue_type="policy_distillation_accuracy_not_field_ready",
                    severity=Severity.INFO,
                    message="决策树蒸馏规则尚未达到现场控制所需准确度，只能作为解释草案。",
                    evidence=distilled_policy,
                )
            )
        return issues

    @staticmethod
    def _recommendations(
        sparse_context: dict[str, object],
        distilled_policy: dict[str, object],
        readiness: dict[str, object],
    ) -> list[str]:
        recs = [
            "把单处理链闭环升级为“多设施 agent 协同”：均质池、反应核心、催化剂床、回流环和末端精处理分别提出局部动作，再由联合奖励函数仲裁。",
            "把 Agent48 的 node-modality 稀疏观测矩阵作为协同控制的状态入口，缺节点或缺模态时用 missingness mask 显式进入策略。",
            "用决策树蒸馏把多 agent 策略转成现场可审查规则，所有规则都必须保留人工复核和禁止自动放行边界。",
        ]
        if not readiness["field_ready"]:
            recs.append("下一步应采集真实多节点 sensor/lab/operation/action replay，形成共享经验池，再验证 joint_action_accuracy、reward_regret 和误动作成本。")
        if sparse_context.get("selected_sensor_count", 0) < 6:
            recs.append("协同控制至少需要覆盖进水、均质、反应、催化剂床、回流和末端中的关键节点，否则多设施动作容易退化为单点启发式。")
        observation_context = sparse_context.get("observation_contract_context", {})
        observation_context = observation_context if isinstance(observation_context, dict) else {}
        if (
            str(observation_context.get("weak_axis_repair_status", ""))
            == "agent48_catalyst_axis_requires_proxy_patch_and_field_label"
        ):
            recs.append("Agent49 可消费 Agent51/R2 的催化剂弱轴修复先验更新状态向量，但 field proxy labels 前必须保留催化剂不确定性保护。")
        if observation_context.get("pressure_headloss_consumed_by_agent49", False):
            recs.append(
                "Agent49 已消费 pressure/headloss 候选合同；下一步需要用 site topology、bed geometry、压降时序、lab label 和操作日志做 field replay，否则只能作为解释先验和 guardrail 边界。"
            )
        if not distilled_policy["can_replace_black_box_policy"]:
            recs.append("决策树代理当前只能解释策略，不能替代协同控制器；需要 field replay 上准确度达到 0.90 后再进入执行器候选。")
        if readiness.get("control_replay_guardrails_integrated", False):
            recs.append("R3b 已把反事实压力测试中的 R3G1/R3G2 接入 Agent49 reward prior；下一步需要 Agent52 用 guardrail-aware replay 复核 regret 和误保护成本。")
        guardrail_context = MultiFacilityCollaborativeControlAgent._static_catalyst_context_from_sparse(sparse_context)
        if guardrail_context.get("summary_supplied") and not guardrail_context.get("field_validation_pass"):
            recs.append(
                "Agent49 已接入 Agent51 field holdout summary；若 scoreable batch 不足或 MAE/相关性未过线，J2 催化剂保护/再生仍要转入暂存或人工复核。"
            )
        if guardrail_context.get("conflict_requires_operator_review"):
            recs.append(
                "Agent49 已接入 R8k pressure source conflict；冲突 batch 不得用于放松催化剂/水力 guardrail，应进入现场校准、传感器核查或人工复核队列。"
            )
        recs.append("P7 后续必须把工程执行约束补丁持续接入 reward，包括池容、泵阀延迟、药剂库存、维护窗口和人工复核排队。")
        return recs

    @staticmethod
    def _method_contract() -> dict[str, object]:
        return {
            "upgrade_id": "multi_facility_collaborative_control_from_sparse_sensing",
            "borrowed_from": [
                "multi_agent_reinforcement_learning_for_multi_facility_wastewater_control",
                "LSTM_or_surrogate_environment_interaction_model",
                "shared_experience_replay_pool",
                "weighted_reward_for_energy_risk_operation_mode",
                "ID3_decision_tree_policy_distillation_for_interpretable_execution",
            ],
            "reality_mapping": "把城市污水多泵站协同优化的思想迁移为处理单元/回流单元/末端单元协同控制，但只借鉴状态-动作-奖励-经验池-蒸馏结构，不强行套用泵站水位目标。",
            "data_needs": [
                "multi_node_sensor_timeseries",
                "lab_labels_by_batch_and_node",
                "operation_action_log",
                "actuator_response_and_delay",
                "energy_chemical_cost",
                "engineering_constraint_patch",
                "operator_override_and_failure_reason",
            ],
            "implementation_path": [
                "src/water_ai/agents/multi_facility_collaborative_control_agent.py",
                "experiments/run_agent49_multi_facility_collaborative_control.py",
                "outputs/multi_facility_collaborative_control/collaborative_control_metrics.json",
            ],
            "evaluation_metrics": [
                "joint_action_accuracy",
                "reward_regret",
                "field_replay_coverage",
                "distilled_policy_accuracy",
                "false_positive_action_cost",
                "engineering_constraint_penalty",
                "execution_feasibility",
                "control_replay_guardrail_penalty",
                "pressure_source_conflict_control_block",
                "release_block_correctness",
            ],
            "failure_boundary": "当前只形成多设施协同控制候选和可解释规则树，不训练真实 MARL 控制器，也不允许 synthetic 策略写入执行器或放行门。",
        }

    @staticmethod
    def _reward_contract() -> dict[str, object]:
        return {
            "objective": "在低成本稀疏感知下同时优化水质安全、基质冲击削峰、反应完成度、催化剂保护、能耗药耗、延迟预算和可解释性。",
            "reward_terms": {
                "quality_reward": "残留污染物/末端风险可观测且动作能降低风险。",
                "risk_reduction_reward": "基质冲击和催化剂压力被提前削峰或隔离。",
                "latency_reward": "动作能利用循环/暂存结构争取控制和慢证据时间。",
                "field_evidence_bonus": "真实 replay 覆盖、动作准确度和回报后悔度达标。",
                "interpretability_bonus": "动作可被决策树规则解释并可人工复核。",
                "cost_energy_efficiency": "动作不把低成本研究方向推成高能耗高药耗方案。",
                "engineering_constraint_penalty": "池容、泵阀、库存、维护窗口、人工复核和误动作成本形成的执行约束惩罚。",
                "execution_feasibility": "该联动动作在当前工程资源边界下的可执行程度。",
                "control_replay_guardrail_penalty": "R3 反事实压力测试暴露的高 regret/误保护动作惩罚。",
                "control_replay_guardrail_bonus": "R3 guardrail 推荐的低风险暂存、精处理或慢证据动作加成。",
            },
            "hard_constraints": [
                "synthetic policy cannot write actuator",
                "collaborative policy cannot write release gate",
                "low catalyst observability blocks autonomous catalyst action",
                "field replay and decision-tree distillation required before execution candidate",
                "engineering hard blocks require manual review or action downgrade",
                "R3 control replay guardrails cannot promote actuator or release gate without field replay",
                "pressure/headloss candidates cannot relax hydraulic or catalyst guardrails without field topology and labels",
                "conflicting pressure sources cannot relax hydraulic or catalyst guardrails before operator review",
            ],
        }

    def _engineering_constraints_context(self) -> dict[str, object]:
        readiness = self.engineering_constraints_metrics.get("readiness", {})
        if not isinstance(readiness, dict):
            readiness = {}
        patch = self.engineering_constraints_metrics.get("agent49_reward_patch", [])
        patch_available = isinstance(patch, list) and bool(patch)
        return {
            "agent49_reward_patch_available": patch_available,
            "engineering_constraints_status": readiness.get("engineering_constraints_status", "not_available"),
            "field_ready": bool(readiness.get("field_ready", False)),
            "can_update_agent49_reward_contract": bool(readiness.get("can_update_agent49_reward_contract", patch_available)),
            "can_write_to_actuator": bool(readiness.get("can_write_to_actuator", False)),
        }

    def _engineering_reward_patch(self, joint_action_id: str) -> dict[str, object]:
        patch = self.engineering_constraints_metrics.get("agent49_reward_patch", [])
        if not isinstance(patch, list):
            return {}
        for item in patch:
            if isinstance(item, dict) and item.get("joint_action_id") == joint_action_id:
                return item
        return {}

    def _catalyst_proxy_field_context(self) -> dict[str, object]:
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
        pressure_source_conflicts = summary.get("pressure_source_conflicts", readiness.get("pressure_source_conflicts", []))
        pressure_source_conflicts = pressure_source_conflicts if isinstance(pressure_source_conflicts, list) else []
        unresolved_pressure_source_conflicts = summary.get(
            "unresolved_pressure_source_conflicts",
            readiness.get("unresolved_pressure_source_conflicts", []),
        )
        unresolved_pressure_source_conflicts = (
            unresolved_pressure_source_conflicts if isinstance(unresolved_pressure_source_conflicts, list) else []
        )
        pressure_source_resolutions = summary.get(
            "pressure_source_resolutions",
            readiness.get("pressure_source_resolutions", []),
        )
        pressure_source_resolutions = pressure_source_resolutions if isinstance(pressure_source_resolutions, list) else []
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
            "missing_required_signals": summary.get("missing_required_signals", []),
            "accepted_pressure_evidence_sources": accepted_pressure_sources if isinstance(accepted_pressure_sources, list) else [],
            "pressure_evidence_source_batch_counts": pressure_source_counts if isinstance(pressure_source_counts, dict) else {},
            "pressure_headloss_event_source_batch_count": pressure_event_source_count,
            "pressure_source_conflict_count": pressure_conflict_count,
            "resolved_pressure_source_conflict_count": resolved_pressure_conflict_count,
            "unresolved_pressure_source_conflict_count": unresolved_pressure_conflict_count,
            "pressure_source_resolution_record_count": pressure_resolution_record_count,
            "pressure_source_conflicts": pressure_source_conflicts[:12],
            "unresolved_pressure_source_conflicts": unresolved_pressure_source_conflicts[:12],
            "pressure_source_resolutions": pressure_source_resolutions[:12],
            "conflict_requires_operator_review": conflict_requires_review,
            "pressure_source_conflict_control_block": conflict_requires_review,
            "guardrail_mode": mode,
            "can_write_to_actuator": False,
            "can_write_to_release_gate": False,
        }

    @staticmethod
    def _static_catalyst_context_from_sparse(sparse_context: dict[str, object]) -> dict[str, object]:
        context = sparse_context.get("catalyst_proxy_field_context", {})
        return context if isinstance(context, dict) else {}

    def _field_evidence_score(self) -> float:
        if self.data_origin != "field_coordination_replay":
            return 0.0
        action_accuracy = self._number(self.field_validation, "joint_action_accuracy", 0.0)
        replay_coverage = self._number(self.field_validation, "field_replay_coverage", 0.0)
        reward_regret = self._number(self.field_validation, "reward_regret", 1.0)
        return round(0.40 * action_accuracy + 0.35 * replay_coverage + 0.25 * max(0.0, 1.0 - reward_regret), 3)

    @staticmethod
    def _number(values: dict[str, object], key: str, default: float) -> float:
        value = values.get(key, default)
        if isinstance(value, int | float):
            return float(value)
        return default

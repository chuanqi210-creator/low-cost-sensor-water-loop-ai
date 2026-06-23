from __future__ import annotations

from collections import deque
from collections.abc import Sequence

import numpy as np

from water_ai.agents.base import BaseAgent
from water_ai.domain import AgentReport, QualityIssue, SensorReading, Severity


OBSERVATION_AXES = [
    "pollutant_residual_observability",
    "reaction_completion_observability",
    "oxidant_observability",
    "catalyst_activity_observability",
    "matrix_interference_observability",
    "hydraulic_observability",
    "fault_classification_observability",
    "control_latency_gain",
    "soft_sensor_reconstruction_gain",
    "cost_efficiency",
]


class SensorNetworkSparsePlacementAgent(BaseAgent):
    """Rank sparse sensor placements over process/network nodes and sensor modalities."""

    name = "sensor_network_sparse_placement_agent"

    def __init__(
        self,
        *,
        candidate_nodes: list[dict[str, object]] | None = None,
        modality_profiles: dict[str, dict[str, float]] | None = None,
        topology_edges: list[tuple[str, str]] | None = None,
        max_sensors: int = 6,
        budget_limit: float = 5.8,
        data_origin: str = "synthetic_topology_prior",
        placement_strategy: str = "auto_compare",
    ) -> None:
        self.candidate_nodes = candidate_nodes or self._default_candidate_nodes()
        self.modality_profiles = modality_profiles or self._default_modality_profiles()
        self.topology_edges = topology_edges or self._default_topology_edges()
        self.max_sensors = max(1, max_sensors)
        self.budget_limit = max(0.1, budget_limit)
        self.data_origin = data_origin
        self.placement_strategy = placement_strategy

    def run(self, readings: Sequence[SensorReading]) -> AgentReport:
        del readings
        observation_matrix = self._observation_matrix()
        strategy_candidates = self._strategy_candidates(observation_matrix)
        selected_strategy = self._select_strategy(strategy_candidates)
        selected_plan = list(selected_strategy["selected_sensor_plan"])
        coverage = self._coverage(selected_plan)
        placement_diagnostics = self._placement_diagnostics(selected_plan, observation_matrix)
        hidden_state_requirements = self._hidden_state_requirement_ledger(selected_plan, observation_matrix, coverage)
        hydraulic_path_contract = self._hydraulic_path_coverage_contract(selected_plan)
        readiness = self._readiness(selected_plan, coverage)
        soft_sensor_interface = self._soft_sensor_interface(
            selected_plan,
            coverage,
            selected_strategy,
            placement_diagnostics,
            hidden_state_requirements,
            hydraulic_path_contract,
        )
        baseline_comparison_contract = self._baseline_comparison_contract(strategy_candidates, selected_strategy)
        issues = self._issues(readiness, coverage, placement_diagnostics, hidden_state_requirements, hydraulic_path_contract)
        recommendations = self._recommendations(
            readiness,
            selected_plan,
            placement_diagnostics,
            hidden_state_requirements,
            hydraulic_path_contract,
        )
        summary = (
            f"稀疏传感布点：{readiness['sparse_placement_status']}；"
            f"选择 {len(selected_plan)} 个 node-modality，"
            f"策略 {selected_strategy['strategy_id']}，"
            f"弱状态覆盖 {coverage['weak_state_coverage']:.3f}。"
        )
        confidence = round(
            min(0.90, max(0.18, 0.34 + 0.44 * readiness["sparse_placement_score"] - 0.035 * len(issues))),
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
                "observation_axes": OBSERVATION_AXES,
                "candidate_nodes": self.candidate_nodes,
                "modality_profiles": self.modality_profiles,
                "topology_graph": self._topology_graph(),
                "observation_matrix": observation_matrix,
                "algorithm_comparison": strategy_candidates,
                "baseline_comparison_contract": baseline_comparison_contract,
                "selected_strategy": selected_strategy,
                "selected_sensor_plan": selected_plan,
                "coverage": coverage,
                "placement_diagnostics": placement_diagnostics,
                "hidden_state_requirement_ledger": hidden_state_requirements,
                "hydraulic_path_coverage_contract": hydraulic_path_contract,
                "readiness": readiness,
                "soft_sensor_interface": soft_sensor_interface,
            },
        )

    def _observation_matrix(self) -> list[dict[str, object]]:
        rows: list[dict[str, object]] = []
        for node in self.candidate_nodes:
            node_id = str(node.get("node_id", "unknown_node"))
            for modality, profile in self.modality_profiles.items():
                vector = self._observation_vector(node, profile)
                cost = round(float(node.get("install_cost_index", 1.0)) * float(profile.get("cost_index", 1.0)), 3)
                maintenance = round(float(node.get("maintenance_access", 0.5)) * (1.0 - float(profile.get("maintenance_load", 0.4))), 3)
                rows.append(
                    {
                        "candidate_id": f"{node_id}:{modality}",
                        "node_id": node_id,
                        "zone": str(node.get("zone", "unknown")),
                        "modality": modality,
                        "vector": vector,
                        "cost_index": cost,
                        "maintenance_score": maintenance,
                        "admissible": bool(node.get("admissible", True)) and bool(profile.get("admissible", True)),
                        "basis_proxy_score": round(sum(vector[axis] for axis in OBSERVATION_AXES[:-1]) / max(1, len(OBSERVATION_AXES) - 1), 3),
                    }
                )
        return rows

    def _observation_vector(self, node: dict[str, object], profile: dict[str, float]) -> dict[str, float]:
        position = float(node.get("hydraulic_position", 0.5))
        process_representativeness = float(node.get("process_representativeness", 0.5))
        matrix_exposure = float(node.get("matrix_shock_exposure", 0.5))
        catalyst_access = float(node.get("catalyst_access", 0.2))
        hydraulic_leverage = float(node.get("hydraulic_leverage", 0.5))
        latency_value = float(node.get("control_latency_value", 0.5))
        maintenance_access = float(node.get("maintenance_access", 0.5))
        install_cost = float(node.get("install_cost_index", 1.0)) * float(profile.get("cost_index", 1.0))

        vector = {
            "pollutant_residual_observability": float(profile.get("pollutant", 0.0)) * (0.35 + 0.65 * process_representativeness),
            "reaction_completion_observability": float(profile.get("reaction", 0.0)) * (0.40 + 0.60 * process_representativeness),
            "oxidant_observability": float(profile.get("oxidant", 0.0)) * (0.35 + 0.45 * process_representativeness + 0.20 * position),
            "catalyst_activity_observability": float(profile.get("catalyst", 0.0)) * (0.25 + 0.75 * catalyst_access),
            "matrix_interference_observability": float(profile.get("matrix", 0.0)) * (0.25 + 0.75 * matrix_exposure),
            "hydraulic_observability": float(profile.get("hydraulic", 0.0)) * (0.35 + 0.65 * hydraulic_leverage),
            "fault_classification_observability": float(profile.get("fault_classification", 0.0))
            * (0.25 + 0.35 * matrix_exposure + 0.20 * catalyst_access + 0.20 * hydraulic_leverage),
            "control_latency_gain": float(profile.get("speed", 0.0)) * (0.30 + 0.70 * latency_value),
            "soft_sensor_reconstruction_gain": float(profile.get("reconstruction", 0.0))
            * (0.30 + 0.35 * process_representativeness + 0.20 * matrix_exposure + 0.15 * hydraulic_leverage),
            "cost_efficiency": max(0.0, min(1.0, 0.65 * maintenance_access + 0.35 * (1.0 / max(0.1, install_cost)))),
        }
        return {axis: round(max(0.0, min(1.0, value)), 3) for axis, value in vector.items()}

    def _strategy_candidates(self, observation_matrix: list[dict[str, object]]) -> list[dict[str, object]]:
        strategies = [
            ("greedy_marginal", "current weighted marginal coverage baseline"),
            ("cost_only_baseline", "low-cost rule baseline for prior-art comparison"),
            ("deterministic_random_baseline", "stable pseudo-random baseline for ablation"),
            ("reconstruction_qr_proxy", "SSPOR/QR-style reconstruction proxy"),
            ("classification_sspoc_proxy", "SSPOC-style fault classification proxy"),
            ("topology_robust_cost_proxy", "graph/topology and robust cost constrained proxy"),
        ]
        if self.placement_strategy != "auto_compare":
            strategies = [item for item in strategies if item[0] == self.placement_strategy] or strategies
        candidates: list[dict[str, object]] = []
        for strategy_id, method_family in strategies:
            selected_plan = self._select_sparse_plan(observation_matrix, strategy_id)
            coverage = self._coverage(selected_plan)
            objectives = self._strategy_objectives(selected_plan, coverage)
            diagnostics = self._placement_diagnostics(selected_plan, observation_matrix)
            candidates.append(
                {
                    "strategy_id": strategy_id,
                    "method_family": method_family,
                    "benchmark_role": self._strategy_benchmark_role(strategy_id),
                    "prior_art_family": self._strategy_prior_art_family(strategy_id),
                    "selected_sensor_plan": selected_plan,
                    "selected_sensor_ids": [str(item["candidate_id"]) for item in selected_plan],
                    "selected_sensor_count": len(selected_plan),
                    "coverage": coverage,
                    "topology_coverage_score": objectives["topology_coverage_score"],
                    "reconstruction_objective": objectives["reconstruction_objective"],
                    "classification_objective": objectives["classification_objective"],
                    "robustness_objective": objectives["robustness_objective"],
                    "cost_objective": objectives["cost_objective"],
                    "comparable_score": objectives["comparable_score"],
                    "axis_span_rank_ratio": diagnostics["axis_span_rank_ratio"],
                    "condition_number_proxy": diagnostics["condition_number_proxy"],
                    "weak_axis_gap_count": diagnostics["weak_axis_gap_count"],
                    "single_point_dependency_count": diagnostics["single_point_dependency_count"],
                    "layout_redundancy_score": diagnostics["layout_redundancy_score"],
                    "field_validation_boundary": (
                        "algorithm comparison is computed on synthetic topology prior unless data_origin=field_topology"
                    ),
                    "prior_art_comparison_boundary": (
                        "baseline supports nonlegal distinction analysis only; it is not a patentability opinion "
                        "and cannot prove field deployment performance without field topology and labels"
                    ),
                }
            )
        candidates.sort(key=lambda item: (-float(item["comparable_score"]), str(item["strategy_id"])))
        for rank, candidate in enumerate(candidates, start=1):
            candidate["rank"] = rank
        return candidates

    @staticmethod
    def _select_strategy(strategy_candidates: list[dict[str, object]]) -> dict[str, object]:
        if not strategy_candidates:
            return {
                "strategy_id": "no_feasible_strategy",
                "selected_sensor_plan": [],
                "comparable_score": 0.0,
                "field_validation_boundary": "no feasible sparse placement candidate under current budget",
            }
        selected = dict(strategy_candidates[0])
        selected["selected_sensor_plan"] = selected.pop("selected_sensor_plan", None) or []
        return selected

    def _select_sparse_plan(self, observation_matrix: list[dict[str, object]], strategy_id: str = "greedy_marginal") -> list[dict[str, object]]:
        selected: list[dict[str, object]] = []
        remaining = [row for row in observation_matrix if row["admissible"]]
        total_cost = 0.0
        while remaining and len(selected) < self.max_sensors:
            current_coverage = self._coverage(selected)
            best_row = None
            best_score = -999.0
            for row in remaining:
                cost = float(row["cost_index"])
                if total_cost + cost > self.budget_limit:
                    continue
                score = self._strategy_row_score(row, current_coverage, selected, strategy_id)
                if score > best_score:
                    best_score = score
                    best_row = row
            if best_row is None:
                break
            plan_item = {
                **best_row,
                "selection_order": len(selected) + 1,
                "marginal_score": round(best_score, 3),
                "selection_strategy": strategy_id,
                "why_selected": self._why_selected(best_row),
            }
            selected.append(plan_item)
            total_cost += float(best_row["cost_index"])
            remaining = [row for row in remaining if row["candidate_id"] != best_row["candidate_id"]]
        return selected

    def _strategy_row_score(
        self,
        row: dict[str, object],
        coverage: dict[str, float],
        selected: list[dict[str, object]],
        strategy_id: str,
    ) -> float:
        if strategy_id == "reconstruction_qr_proxy":
            return self._reconstruction_qr_score(row, selected)
        if strategy_id == "classification_sspoc_proxy":
            return self._classification_proxy_score(row, coverage, selected)
        if strategy_id == "topology_robust_cost_proxy":
            return self._topology_robust_cost_score(row, coverage, selected)
        if strategy_id == "cost_only_baseline":
            return self._cost_only_baseline_score(row, selected)
        if strategy_id == "deterministic_random_baseline":
            return self._deterministic_random_baseline_score(row, selected)
        return self._marginal_score(row, coverage, selected)

    def _marginal_score(self, row: dict[str, object], coverage: dict[str, float], selected: list[dict[str, object]]) -> float:
        vector = row["vector"] if isinstance(row["vector"], dict) else {}
        axis_weights = {
            "pollutant_residual_observability": 0.12,
            "reaction_completion_observability": 0.09,
            "oxidant_observability": 0.08,
            "catalyst_activity_observability": 0.14,
            "matrix_interference_observability": 0.16,
            "hydraulic_observability": 0.10,
            "fault_classification_observability": 0.12,
            "control_latency_gain": 0.07,
            "soft_sensor_reconstruction_gain": 0.10,
            "cost_efficiency": 0.02,
        }
        novelty = 0.0
        for axis, weight in axis_weights.items():
            value = float(vector.get(axis, 0.0))
            current = float(coverage.get(axis, 0.0))
            novelty += weight * max(0.0, min(value, 1.0 - current))
        selected_nodes = {str(item["node_id"]) for item in selected}
        selected_modalities = {str(item["modality"]) for item in selected}
        diversity_bonus = 0.035 * float(str(row["node_id"]) not in selected_nodes) + 0.025 * float(str(row["modality"]) not in selected_modalities)
        weak_bonus = 0.08 * float(vector.get("matrix_interference_observability", 0.0)) + 0.06 * float(vector.get("catalyst_activity_observability", 0.0))
        cost_penalty = 0.035 * float(row["cost_index"])
        redundancy_penalty = 0.04 * self._redundancy(row, selected)
        return novelty + diversity_bonus + weak_bonus - cost_penalty - redundancy_penalty

    def _reconstruction_qr_score(self, row: dict[str, object], selected: list[dict[str, object]]) -> float:
        current_objective = self._logdet_reconstruction_objective(selected)
        candidate_objective = self._logdet_reconstruction_objective([*selected, row])
        logdet_gain = candidate_objective - current_objective
        vector = row["vector"] if isinstance(row["vector"], dict) else {}
        reconstruction_bias = 0.20 * float(vector.get("soft_sensor_reconstruction_gain", 0.0))
        topology_bonus = 0.08 * self._topology_novelty(row, selected)
        weak_guard = 0.06 * float(vector.get("catalyst_activity_observability", 0.0))
        cost_penalty = 0.045 * float(row["cost_index"])
        redundancy_penalty = 0.08 * self._redundancy(row, selected)
        return logdet_gain + reconstruction_bias + topology_bonus + weak_guard - cost_penalty - redundancy_penalty

    def _classification_proxy_score(self, row: dict[str, object], coverage: dict[str, float], selected: list[dict[str, object]]) -> float:
        vector = row["vector"] if isinstance(row["vector"], dict) else {}
        classification_axes = {
            "fault_classification_observability": 0.28,
            "matrix_interference_observability": 0.20,
            "catalyst_activity_observability": 0.18,
            "hydraulic_observability": 0.14,
            "control_latency_gain": 0.12,
            "reaction_completion_observability": 0.08,
        }
        score = 0.0
        for axis, weight in classification_axes.items():
            value = float(vector.get(axis, 0.0))
            current = float(coverage.get(axis, 0.0))
            score += weight * (0.55 * value + 0.45 * max(0.0, value - current))
        score += 0.08 * self._topology_novelty(row, selected)
        score += 0.03 * float(str(row["modality"]) not in {str(item["modality"]) for item in selected})
        score -= 0.04 * float(row["cost_index"])
        score -= 0.06 * self._redundancy(row, selected)
        return score

    def _topology_robust_cost_score(self, row: dict[str, object], coverage: dict[str, float], selected: list[dict[str, object]]) -> float:
        vector = row["vector"] if isinstance(row["vector"], dict) else {}
        robust_axes = (
            "weak_state_coverage",
            "hydraulic_observability",
            "control_latency_gain",
            "matrix_interference_observability",
            "soft_sensor_reconstruction_gain",
        )
        weak_proxy = min(
            float(vector.get("catalyst_activity_observability", 0.0)),
            float(vector.get("matrix_interference_observability", 0.0)),
        )
        robust_values = {
            "weak_state_coverage": weak_proxy,
            "hydraulic_observability": float(vector.get("hydraulic_observability", 0.0)),
            "control_latency_gain": float(vector.get("control_latency_gain", 0.0)),
            "matrix_interference_observability": float(vector.get("matrix_interference_observability", 0.0)),
            "soft_sensor_reconstruction_gain": float(vector.get("soft_sensor_reconstruction_gain", 0.0)),
        }
        novelty = sum(max(0.0, robust_values[axis] - float(coverage.get(axis, 0.0))) for axis in robust_axes) / len(robust_axes)
        topology_bonus = 0.28 * self._topology_novelty(row, selected)
        maintenance_bonus = 0.12 * float(row.get("maintenance_score", 0.0))
        cost_efficiency = 0.18 * float(vector.get("cost_efficiency", 0.0))
        cost_penalty = 0.08 * float(row["cost_index"])
        return 0.48 * novelty + topology_bonus + maintenance_bonus + cost_efficiency - cost_penalty

    def _cost_only_baseline_score(self, row: dict[str, object], selected: list[dict[str, object]]) -> float:
        vector = row["vector"] if isinstance(row["vector"], dict) else {}
        node_novelty = 0.03 * float(str(row["node_id"]) not in {str(item["node_id"]) for item in selected})
        modality_novelty = 0.02 * float(str(row["modality"]) not in {str(item["modality"]) for item in selected})
        return (
            0.70 * float(vector.get("cost_efficiency", 0.0))
            + 0.18 * float(row.get("maintenance_score", 0.0))
            + node_novelty
            + modality_novelty
            - 0.12 * float(row["cost_index"])
        )

    def _deterministic_random_baseline_score(self, row: dict[str, object], selected: list[dict[str, object]]) -> float:
        # Stable pseudo-random ordering without relying on Python's salted hash.
        candidate_id = str(row.get("candidate_id", ""))
        checksum = sum((index + 1) * ord(char) for index, char in enumerate(candidate_id))
        pseudo_random = (checksum % 997) / 997.0
        diversity_bonus = 0.035 * float(str(row["node_id"]) not in {str(item["node_id"]) for item in selected})
        budget_bias = 0.04 * float((row.get("vector") or {}).get("cost_efficiency", 0.0))
        return pseudo_random + diversity_bonus + budget_bias - 0.03 * float(row["cost_index"])

    @staticmethod
    def _strategy_benchmark_role(strategy_id: str) -> str:
        roles = {
            "greedy_marginal": "project_candidate_strategy",
            "cost_only_baseline": "naive_low_cost_prior_art_baseline",
            "deterministic_random_baseline": "random_ablation_baseline",
            "reconstruction_qr_proxy": "sparse_reconstruction_prior_art_baseline",
            "classification_sspoc_proxy": "fault_classification_prior_art_baseline",
            "topology_robust_cost_proxy": "project_candidate_topology_aware_strategy",
        }
        return roles.get(strategy_id, "comparison_strategy")

    @staticmethod
    def _strategy_prior_art_family(strategy_id: str) -> str:
        families = {
            "greedy_marginal": "weighted hidden-state coverage heuristic",
            "cost_only_baseline": "lowest-cost sensor placement rule",
            "deterministic_random_baseline": "random sensor placement ablation",
            "reconstruction_qr_proxy": "SSPOR/QR/D-optimal sparse reconstruction",
            "classification_sspoc_proxy": "SSPOC-style sparse fault classification",
            "topology_robust_cost_proxy": "topology-aware robust monitoring placement",
        }
        return families.get(strategy_id, "unspecified sparse placement family")

    def _baseline_comparison_contract(
        self,
        strategy_candidates: list[dict[str, object]],
        selected_strategy: dict[str, object],
    ) -> dict[str, object]:
        required = [
            "deterministic_random_baseline",
            "cost_only_baseline",
            "reconstruction_qr_proxy",
            "classification_sspoc_proxy",
            "topology_robust_cost_proxy",
        ]
        observed = [str(item["strategy_id"]) for item in strategy_candidates]
        scores = {str(item["strategy_id"]): float(item["comparable_score"]) for item in strategy_candidates}
        best_score = float(selected_strategy.get("comparable_score", 0.0) or 0.0)
        status = "sparse_baseline_comparison_ready_needs_field_topology_and_labels"
        missing = [strategy_id for strategy_id in required if strategy_id not in observed]
        if missing:
            status = "sparse_baseline_comparison_missing_required_baselines"
        elif self.data_origin == "field_topology":
            status = "sparse_baseline_comparison_ready_for_field_benchmark"
        return {
            "comparison_status": status,
            "required_baseline_strategy_ids": required,
            "observed_strategy_ids": observed,
            "missing_baseline_strategy_ids": missing,
            "selected_strategy_id": selected_strategy.get("strategy_id", "unknown"),
            "selected_strategy_score": round(best_score, 3),
            "best_vs_random_delta": round(best_score - scores.get("deterministic_random_baseline", best_score), 3),
            "best_vs_cost_only_delta": round(best_score - scores.get("cost_only_baseline", best_score), 3),
            "best_vs_sparse_reconstruction_delta": round(best_score - scores.get("reconstruction_qr_proxy", best_score), 3),
            "best_vs_fault_classification_delta": round(best_score - scores.get("classification_sspoc_proxy", best_score), 3),
            "field_benchmark_required": self.data_origin != "field_topology",
            "claim_scope_use": (
                "use these baselines to distinguish node-modality hidden-state placement from generic sparse placement, "
                "cost-only rules and random ablations"
            ),
            "cannot_do": [
                "cannot prove patentability",
                "cannot prove field deployment performance",
                "cannot replace field topology, node-specific time series or offline hidden-state labels",
            ],
        }

    @staticmethod
    def _redundancy(row: dict[str, object], selected: list[dict[str, object]]) -> float:
        if not selected:
            return 0.0
        vector = row["vector"] if isinstance(row["vector"], dict) else {}
        row_values = [float(vector.get(axis, 0.0)) for axis in OBSERVATION_AXES]
        similarities: list[float] = []
        for item in selected:
            other = item["vector"] if isinstance(item.get("vector"), dict) else {}
            other_values = [float(other.get(axis, 0.0)) for axis in OBSERVATION_AXES]
            numerator = sum(a * b for a, b in zip(row_values, other_values, strict=True))
            denom_a = sum(a * a for a in row_values) ** 0.5
            denom_b = sum(b * b for b in other_values) ** 0.5
            similarities.append(numerator / max(1e-9, denom_a * denom_b))
        return max(similarities) if similarities else 0.0

    def _topology_novelty(self, row: dict[str, object], selected: list[dict[str, object]]) -> float:
        if not selected:
            return 1.0
        node_id = str(row["node_id"])
        distances = [self._topology_distance(node_id, str(item["node_id"])) for item in selected]
        return round(min(1.0, min(distances) / 3.0), 3)

    def _topology_distance(self, node_a: str, node_b: str) -> float:
        if node_a == node_b:
            return 0.0
        graph = self._topology_graph()["adjacency"]
        if node_a not in graph or node_b not in graph:
            positions = {str(node["node_id"]): float(node.get("hydraulic_position", 0.5)) for node in self.candidate_nodes}
            return min(3.0, 1.0 + 4.0 * abs(positions.get(node_a, 0.5) - positions.get(node_b, 0.5)))
        queue: deque[tuple[str, int]] = deque([(node_a, 0)])
        visited = {node_a}
        while queue:
            current, distance = queue.popleft()
            for neighbor in graph.get(current, []):
                if neighbor == node_b:
                    return float(distance + 1)
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, distance + 1))
        return 4.0

    def _topology_graph(self) -> dict[str, object]:
        adjacency: dict[str, list[str]] = {str(node["node_id"]): [] for node in self.candidate_nodes}
        for start, end in self.topology_edges:
            adjacency.setdefault(start, [])
            adjacency.setdefault(end, [])
            adjacency[start].append(end)
            adjacency[end].append(start)
        return {
            "nodes": [str(node["node_id"]) for node in self.candidate_nodes],
            "edges": [{"from": start, "to": end} for start, end in self.topology_edges],
            "adjacency": {node: sorted(set(neighbors)) for node, neighbors in adjacency.items()},
            "topology_type": "process_unit_graph_with_recirculation_loop",
        }

    @staticmethod
    def _vector_array(selected_plan: list[dict[str, object]], *, include_cost_efficiency: bool = False) -> np.ndarray:
        axes = OBSERVATION_AXES if include_cost_efficiency else OBSERVATION_AXES[:-1]
        if not selected_plan:
            return np.zeros((0, len(axes)))
        rows = []
        for item in selected_plan:
            vector = item["vector"] if isinstance(item.get("vector"), dict) else {}
            rows.append([float(vector.get(axis, 0.0)) for axis in axes])
        return np.asarray(rows, dtype=float)

    def _logdet_reconstruction_objective(self, selected_plan: list[dict[str, object]]) -> float:
        matrix = self._vector_array(selected_plan)
        if matrix.size == 0:
            return 0.0
        gram = matrix @ matrix.T
        gram += np.eye(gram.shape[0]) * 1e-3
        sign, logdet = np.linalg.slogdet(gram)
        if sign <= 0:
            return 0.0
        return float(logdet / max(1, gram.shape[0]))

    def _strategy_objectives(self, selected_plan: list[dict[str, object]], coverage: dict[str, float]) -> dict[str, float]:
        selected_nodes = {str(item["node_id"]) for item in selected_plan}
        selected_zones = {str(item["zone"]) for item in selected_plan}
        all_nodes = {str(item["node_id"]) for item in self.candidate_nodes}
        all_zones = {str(item.get("zone", "unknown")) for item in self.candidate_nodes}
        topology_coverage = 0.55 * len(selected_nodes) / max(1, len(all_nodes)) + 0.45 * len(selected_zones) / max(1, len(all_zones))
        pair_distances = [
            self._topology_distance(str(a["node_id"]), str(b["node_id"]))
            for index, a in enumerate(selected_plan)
            for b in selected_plan[index + 1 :]
        ]
        if pair_distances:
            topology_coverage = 0.75 * topology_coverage + 0.25 * min(1.0, min(pair_distances) / 2.0)
        reconstruction_objective = min(
            1.0,
            0.45 * float(coverage["soft_sensor_reconstruction_gain"])
            + 0.25 * float(coverage["pollutant_residual_observability"])
            + 0.15 * float(coverage["reaction_completion_observability"])
            + 0.15 * max(0.0, min(1.0, self._logdet_reconstruction_objective(selected_plan))),
        )
        classification_objective = min(
            1.0,
            0.36 * float(coverage["fault_classification_observability"])
            + 0.24 * float(coverage["matrix_interference_observability"])
            + 0.20 * float(coverage["catalyst_activity_observability"])
            + 0.20 * float(coverage["hydraulic_observability"]),
        )
        cost_objective = min(1.0, self.budget_limit / max(self.budget_limit, float(coverage["total_cost_index"])))
        robustness_objective = min(
            1.0,
            0.32 * float(coverage["weak_state_coverage"])
            + 0.20 * float(coverage["hydraulic_observability"])
            + 0.18 * float(coverage["control_latency_gain"])
            + 0.18 * float(coverage["matrix_interference_observability"])
            + 0.12 * cost_objective,
        )
        comparable_score = (
            0.28 * reconstruction_objective
            + 0.22 * classification_objective
            + 0.20 * robustness_objective
            + 0.16 * min(1.0, topology_coverage)
            + 0.14 * cost_objective
        )
        return {
            "topology_coverage_score": round(min(1.0, topology_coverage), 3),
            "reconstruction_objective": round(reconstruction_objective, 3),
            "classification_objective": round(classification_objective, 3),
            "robustness_objective": round(robustness_objective, 3),
            "cost_objective": round(cost_objective, 3),
            "comparable_score": round(comparable_score, 3),
        }

    @staticmethod
    def _why_selected(row: dict[str, object]) -> list[str]:
        vector = row["vector"] if isinstance(row["vector"], dict) else {}
        sorted_axes = sorted(
            ((axis, float(vector.get(axis, 0.0))) for axis in OBSERVATION_AXES),
            key=lambda item: item[1],
            reverse=True,
        )
        return [axis for axis, value in sorted_axes[:3] if value > 0.0]

    @staticmethod
    def _coverage(selected_plan: list[dict[str, object]]) -> dict[str, float]:
        coverage = {axis: 0.0 for axis in OBSERVATION_AXES}
        for item in selected_plan:
            vector = item["vector"] if isinstance(item.get("vector"), dict) else {}
            for axis in OBSERVATION_AXES:
                coverage[axis] = max(coverage[axis], float(vector.get(axis, 0.0)))
        coverage = {axis: round(min(1.0, value), 3) for axis, value in coverage.items()}
        coverage["weak_state_coverage"] = round(
            min(
                float(coverage["catalyst_activity_observability"]),
                float(coverage["matrix_interference_observability"]),
            ),
            3,
        )
        coverage["total_cost_index"] = round(sum(float(item["cost_index"]) for item in selected_plan), 3)
        coverage["node_diversity_count"] = float(len({str(item["node_id"]) for item in selected_plan}))
        coverage["modality_diversity_count"] = float(len({str(item["modality"]) for item in selected_plan}))
        return coverage

    def _placement_diagnostics(
        self,
        selected_plan: list[dict[str, object]],
        observation_matrix: list[dict[str, object]],
    ) -> dict[str, object]:
        axes = OBSERVATION_AXES[:-1]
        selected_matrix = self._vector_array(selected_plan)
        admissible_rows = [row for row in observation_matrix if row.get("admissible")]
        candidate_matrix = self._vector_array(admissible_rows)
        coverage = self._coverage(selected_plan)
        rank = int(np.linalg.matrix_rank(selected_matrix, tol=1e-6)) if selected_matrix.size else 0
        singular_values = (
            np.linalg.svd(selected_matrix, full_matrices=False, compute_uv=False).tolist()
            if selected_matrix.size
            else []
        )
        nonzero_singular_values = [float(value) for value in singular_values if float(value) > 1e-6]
        condition_number = (
            float(nonzero_singular_values[0] / max(nonzero_singular_values[-1], 1e-9))
            if nonzero_singular_values
            else 0.0
        )
        inverse_condition_score = 1.0
        if condition_number > 0.0:
            inverse_condition_score = 1.0 / (1.0 + np.log10(max(condition_number, 1.0)))
        rank_ratio = rank / max(1, len(axes))
        weak_axis_gaps = self._weak_axis_gaps(coverage, observation_matrix)
        dependency = self._single_point_dependency(selected_plan, coverage)
        redundancy_score = self._layout_redundancy_score(selected_plan)
        reconstruction_stability_score = round(
            min(
                1.0,
                0.42 * rank_ratio
                + 0.28 * inverse_condition_score
                + 0.18 * (1.0 - min(1.0, float(dependency["single_point_dependency_count"]) / 3.0))
                + 0.12 * (1.0 - redundancy_score),
            ),
            3,
        )
        status = "placement_diagnostics_ready_for_design_prior"
        if weak_axis_gaps or reconstruction_stability_score < 0.52:
            status = "placement_diagnostics_need_axis_patch_or_field_benchmark"
        return {
            "diagnostic_status": status,
            "selected_matrix_shape": [len(selected_plan), len(axes)],
            "candidate_matrix_shape": [len(admissible_rows), len(axes)],
            "selected_matrix_rank": rank,
            "axis_span_rank_ratio": round(rank_ratio, 3),
            "singular_values": [round(float(value), 4) for value in singular_values],
            "condition_number_proxy": round(condition_number, 3),
            "inverse_condition_score": round(float(inverse_condition_score), 3),
            "reconstruction_stability_score": reconstruction_stability_score,
            "layout_redundancy_score": redundancy_score,
            "weak_axis_gap_count": len(weak_axis_gaps),
            "weak_axis_gaps": weak_axis_gaps,
            "single_point_dependency_count": dependency["single_point_dependency_count"],
            "critical_sensor_dependencies": dependency["critical_sensor_dependencies"],
            "candidate_matrix_summary": {
                "candidate_count": len(observation_matrix),
                "admissible_candidate_count": len(admissible_rows),
                "budget_feasible_candidate_count": sum(
                    1 for row in admissible_rows if float(row.get("cost_index", 0.0)) <= self.budget_limit
                ),
                "axis_count": len(axes),
            },
            "field_benchmark_required": self.data_origin != "field_topology",
            "why_it_matters": (
                "coverage 只能说明某些 hidden-state axis 被看见；rank、condition number 和 single-point dependency "
                "用于判断这些低成本观测是否足以支撑软传感重建和多设施控制 replay。"
            ),
        }

    @staticmethod
    def _weak_axis_thresholds() -> dict[str, float]:
        return {
            "pollutant_residual_observability": 0.60,
            "reaction_completion_observability": 0.60,
            "oxidant_observability": 0.55,
            "catalyst_activity_observability": 0.55,
            "matrix_interference_observability": 0.62,
            "hydraulic_observability": 0.55,
            "fault_classification_observability": 0.60,
            "control_latency_gain": 0.62,
            "soft_sensor_reconstruction_gain": 0.62,
        }

    def _weak_axis_gaps(
        self,
        coverage: dict[str, float],
        observation_matrix: list[dict[str, object]],
    ) -> list[dict[str, object]]:
        rows = [row for row in observation_matrix if row.get("admissible")]
        gaps: list[dict[str, object]] = []
        for axis, threshold in self._weak_axis_thresholds().items():
            current = float(coverage.get(axis, 0.0))
            if current >= threshold:
                continue
            candidate_best = 0.0
            candidate_id = "none"
            for row in rows:
                vector = row["vector"] if isinstance(row.get("vector"), dict) else {}
                value = float(vector.get(axis, 0.0))
                if value > candidate_best:
                    candidate_best = value
                    candidate_id = str(row.get("candidate_id", "unknown"))
            gaps.append(
                {
                    "axis": axis,
                    "current_coverage": round(current, 3),
                    "target": threshold,
                    "gap": round(max(0.0, threshold - current), 3),
                    "best_available_candidate": candidate_id,
                    "best_available_value": round(candidate_best, 3),
                    "recoverable_by_current_candidate_pool": candidate_best >= threshold,
                }
            )
        return gaps

    def _single_point_dependency(
        self,
        selected_plan: list[dict[str, object]],
        coverage: dict[str, float],
    ) -> dict[str, object]:
        dependencies: list[dict[str, object]] = []
        base_logdet = self._logdet_reconstruction_objective(selected_plan)
        for item in selected_plan:
            reduced = [row for row in selected_plan if row["candidate_id"] != item["candidate_id"]]
            reduced_coverage = self._coverage(reduced)
            axis_drops = {
                axis: round(max(0.0, float(coverage.get(axis, 0.0)) - float(reduced_coverage.get(axis, 0.0))), 3)
                for axis in OBSERVATION_AXES[:-1]
            }
            max_axis_drop = max(axis_drops.values()) if axis_drops else 0.0
            weak_drop = round(
                max(0.0, float(coverage.get("weak_state_coverage", 0.0)) - float(reduced_coverage.get("weak_state_coverage", 0.0))),
                3,
            )
            logdet_drop = round(max(0.0, base_logdet - self._logdet_reconstruction_objective(reduced)), 3)
            if max_axis_drop >= 0.18 or weak_drop >= 0.10 or logdet_drop >= 0.12:
                dependencies.append(
                    {
                        "candidate_id": str(item["candidate_id"]),
                        "max_axis_drop": round(max_axis_drop, 3),
                        "weak_state_drop": weak_drop,
                        "logdet_drop": logdet_drop,
                        "most_affected_axes": [
                            axis
                            for axis, drop in sorted(axis_drops.items(), key=lambda entry: entry[1], reverse=True)[:3]
                            if drop > 0.0
                        ],
                    }
                )
        dependencies.sort(key=lambda item: (-float(item["max_axis_drop"]), -float(item["logdet_drop"]), item["candidate_id"]))
        return {
            "single_point_dependency_count": len(dependencies),
            "critical_sensor_dependencies": dependencies,
        }

    def _layout_redundancy_score(self, selected_plan: list[dict[str, object]]) -> float:
        if len(selected_plan) < 2:
            return 0.0
        similarities = [
            self._cosine_similarity(a, b)
            for index, a in enumerate(selected_plan)
            for b in selected_plan[index + 1 :]
        ]
        return round(sum(similarities) / max(1, len(similarities)), 3)

    @staticmethod
    def _cosine_similarity(a: dict[str, object], b: dict[str, object]) -> float:
        a_vector = a["vector"] if isinstance(a.get("vector"), dict) else {}
        b_vector = b["vector"] if isinstance(b.get("vector"), dict) else {}
        a_values = [float(a_vector.get(axis, 0.0)) for axis in OBSERVATION_AXES[:-1]]
        b_values = [float(b_vector.get(axis, 0.0)) for axis in OBSERVATION_AXES[:-1]]
        numerator = sum(left * right for left, right in zip(a_values, b_values, strict=True))
        denom_a = sum(value * value for value in a_values) ** 0.5
        denom_b = sum(value * value for value in b_values) ** 0.5
        return numerator / max(1e-9, denom_a * denom_b)

    def _hidden_state_requirement_ledger(
        self,
        selected_plan: list[dict[str, object]],
        observation_matrix: list[dict[str, object]],
        coverage: dict[str, float],
    ) -> dict[str, object]:
        requirements = self._hidden_state_requirements()
        selected_ids = {str(item["candidate_id"]) for item in selected_plan}
        remaining_budget = round(max(0.0, self.budget_limit - float(coverage["total_cost_index"])), 3)
        rows = [
            self._hidden_state_requirement_row(
                requirement,
                selected_plan,
                observation_matrix,
                coverage,
                selected_ids,
                remaining_budget,
            )
            for requirement in requirements
        ]
        pressure_headloss_pool = self._pressure_headloss_candidate_pool(rows)
        ready_count = sum(1 for row in rows if row["ready_for_soft_sensor_estimation"])
        control_ready_count = sum(1 for row in rows if row["ready_for_control_use"])
        unresolved = [row for row in rows if row["unresolved_requirements"]]
        ledger_status = "hidden_state_requirement_ledger_ready_with_gaps"
        if ready_count == len(rows) and not unresolved:
            ledger_status = "hidden_state_requirement_ledger_ready_for_field_benchmark"
        elif ready_count == 0:
            ledger_status = "hidden_state_requirement_ledger_blocked"
        return {
            "ledger_status": ledger_status,
            "hidden_state_count": len(rows),
            "ready_hidden_state_count": ready_count,
            "control_ready_hidden_state_count": control_ready_count,
            "unresolved_hidden_state_count": len(unresolved),
            "remaining_budget": remaining_budget,
            "state_rows": rows,
            "pressure_headloss_candidate_pool": pressure_headloss_pool,
            "minimum_cost_requirement_patch": self._minimum_cost_requirement_patch(rows, pressure_headloss_pool),
            "field_validation_boundary": (
                "hidden-state requirement coverage is a synthetic/design-prior contract until field topology, "
                "node-level timeseries and offline labels are imported"
            ),
        }

    @staticmethod
    def _hidden_state_requirements() -> list[dict[str, object]]:
        return [
            {
                "hidden_state": "pollutant_residual",
                "core_question": "末端残留污染物是否足以支撑暂存、回流或放行判断",
                "primary_axes": ["pollutant_residual_observability", "soft_sensor_reconstruction_gain"],
                "secondary_axes": ["reaction_completion_observability", "oxidant_observability"],
                "target": 0.60,
                "required_zones": ["reaction_core", "polishing", "effluent"],
                "required_modalities": ["UV254_abs", "ORP_mV"],
                "field_evidence_needed": ["offline_lab_results.pollutant_residual", "field_holdout_release_labels"],
                "control_use_requires_field": True,
            },
            {
                "hidden_state": "reaction_completion",
                "core_question": "反应是否完成，是否需要延长停留时间或回流",
                "primary_axes": ["reaction_completion_observability", "oxidant_observability"],
                "secondary_axes": ["soft_sensor_reconstruction_gain", "control_latency_gain"],
                "target": 0.60,
                "required_zones": ["reaction_core", "catalyst_bed", "loop"],
                "required_modalities": ["ORP_mV", "UV254_abs", "pH"],
                "field_evidence_needed": ["offline_lab_results.reaction_completion_proxy", "known_HRT_or_contact_time"],
                "control_use_requires_field": True,
            },
            {
                "hidden_state": "catalyst_activity",
                "core_question": "催化剂是否衰减、堵塞或需要再生，能否阻止错误催化剂动作",
                "primary_axes": ["catalyst_activity_observability", "hydraulic_observability"],
                "secondary_axes": ["reaction_completion_observability", "soft_sensor_reconstruction_gain"],
                "target": 0.55,
                "required_zones": ["catalyst_bed", "loop"],
                "required_modalities": ["UV254_abs", "ORP_mV", "pressure_drop_kPa"],
                "field_evidence_needed": [
                    "node_modality_sensor_timeseries.N3_catalyst_bed_outlet:UV254_abs",
                    "node_modality_sensor_timeseries.N3_catalyst_bed_outlet:ORP_mV",
                    "node_modality_sensor_timeseries.N3_catalyst_bed:pressure_drop_kPa",
                    "offline_lab_results.catalyst_activity",
                    "campaign_operation_log.regeneration_event",
                    "site_topology_or_bed_geometry.nominal_HRT_min",
                ],
                "control_use_requires_field": True,
            },
            {
                "hidden_state": "matrix_interference",
                "core_question": "进水基质冲击是否正在抑制处理效率，是否需要预处理/暂存",
                "primary_axes": ["matrix_interference_observability", "fault_classification_observability"],
                "secondary_axes": ["control_latency_gain", "soft_sensor_reconstruction_gain"],
                "target": 0.62,
                "required_zones": ["influent", "buffer", "loop"],
                "required_modalities": ["EC_uScm", "turbidity_NTU", "UV254_abs"],
                "field_evidence_needed": ["field_labeled_fast_proxy_event_log.matrix_shock", "offline_lab_results.matrix_interference"],
                "control_use_requires_field": True,
            },
            {
                "hidden_state": "hydraulic_delay",
                "core_question": "循环、回流、暂存和执行器延迟是否给诊断争取了足够时间",
                "primary_axes": ["hydraulic_observability", "control_latency_gain"],
                "secondary_axes": ["soft_sensor_reconstruction_gain", "matrix_interference_observability"],
                "target": 0.55,
                "required_zones": ["buffer", "loop", "reaction_core"],
                "required_modalities": ["flow_Lmin", "pressure_drop_kPa"],
                "field_evidence_needed": [
                    "campaign_operation_log.effect_time_min",
                    "campaign_operation_log.hold_time_min",
                    "campaign_operation_log.recycle_ratio",
                    "site_topology_or_bed_geometry.flow_Lmin",
                ],
                "control_use_requires_field": True,
            },
            {
                "hidden_state": "release_or_byproduct_risk",
                "core_question": "末端放行或副产物风险是否需要暂存验证或末端精处理",
                "primary_axes": ["pollutant_residual_observability", "reaction_completion_observability", "oxidant_observability"],
                "secondary_axes": ["fault_classification_observability"],
                "target": 0.58,
                "required_zones": ["polishing", "effluent"],
                "required_modalities": ["UV254_abs", "ORP_mV", "pH"],
                "field_evidence_needed": ["offline_lab_results.byproduct_or_release_risk", "human_reviewed_release_gate_labels"],
                "control_use_requires_field": True,
            },
        ]

    def _hidden_state_requirement_row(
        self,
        requirement: dict[str, object],
        selected_plan: list[dict[str, object]],
        observation_matrix: list[dict[str, object]],
        coverage: dict[str, float],
        selected_ids: set[str],
        remaining_budget: float,
    ) -> dict[str, object]:
        primary_axes = [str(axis) for axis in requirement["primary_axes"]]
        secondary_axes = [str(axis) for axis in requirement["secondary_axes"]]
        target = float(requirement["target"])
        axis_scores = {axis: float(coverage.get(axis, 0.0)) for axis in primary_axes}
        secondary_scores = {axis: float(coverage.get(axis, 0.0)) for axis in secondary_axes}
        min_primary_score = min(axis_scores.values()) if axis_scores else 0.0
        support_sensors = self._supporting_sensors_for_requirement(selected_plan, requirement)
        zone_support_count = len({str(item["zone"]) for item in support_sensors})
        modality_support_count = len({str(item["modality"]) for item in support_sensors})
        candidate_patch = self._candidate_patch_for_requirement(
            requirement,
            observation_matrix,
            selected_ids,
            coverage,
            remaining_budget,
        )
        missing_modalities = sorted(
            set(str(modality) for modality in requirement["required_modalities"])
            - {str(item["modality"]) for item in selected_plan}
        )
        missing_zones = sorted(
            set(str(zone) for zone in requirement["required_zones"])
            - {str(item["zone"]) for item in selected_plan}
        )
        unresolved = []
        if min_primary_score < target and not bool(candidate_patch["candidate_pool_recoverable"]):
            unresolved.append("candidate_pool_cannot_reach_primary_axis_target")
        if missing_modalities:
            unresolved.append("missing_required_modality:" + ",".join(missing_modalities))
        if missing_zones:
            unresolved.append("missing_required_zone:" + ",".join(missing_zones))
        if str(requirement["hidden_state"]) in {"catalyst_activity", "hydraulic_delay"} and "pressure_drop_kPa" in missing_modalities:
            unresolved.append("pressure_drop_or_headloss_proxy_not_in_selected_layout")
        if self.data_origin != "field_topology":
            unresolved.append("field_topology_and_labels_required")
        ready_for_soft_sensor = min_primary_score >= target and zone_support_count >= 1 and modality_support_count >= 1
        ready_for_control = ready_for_soft_sensor and self.data_origin == "field_topology" and not unresolved
        support_ids = [str(item["candidate_id"]) for item in support_sensors[:5]]
        return {
            "hidden_state": requirement["hidden_state"],
            "core_question": requirement["core_question"],
            "primary_axes": primary_axes,
            "secondary_axes": secondary_axes,
            "target": target,
            "axis_scores": {axis: round(score, 3) for axis, score in axis_scores.items()},
            "secondary_axis_scores": {axis: round(score, 3) for axis, score in secondary_scores.items()},
            "min_primary_axis_score": round(min_primary_score, 3),
            "ready_for_soft_sensor_estimation": ready_for_soft_sensor,
            "ready_for_control_use": ready_for_control,
            "support_sensor_count": len(support_sensors),
            "support_sensor_ids": support_ids,
            "zone_support_count": zone_support_count,
            "modality_support_count": modality_support_count,
            "missing_required_zones": missing_zones,
            "missing_required_modalities": missing_modalities,
            "candidate_patch": candidate_patch,
            "unresolved_requirements": sorted(set(unresolved)),
            "field_evidence_needed": requirement["field_evidence_needed"],
            "evidence_boundary": (
                "soft-sensor design prior only"
                if not ready_for_control
                else "field topology ready but still requires downstream holdout gate"
            ),
        }

    @staticmethod
    def _supporting_sensors_for_requirement(
        selected_plan: list[dict[str, object]],
        requirement: dict[str, object],
    ) -> list[dict[str, object]]:
        axes = [str(axis) for axis in requirement["primary_axes"]] + [str(axis) for axis in requirement["secondary_axes"]]
        required_zones = set(str(zone) for zone in requirement["required_zones"])
        required_modalities = set(str(modality) for modality in requirement["required_modalities"])
        support: list[dict[str, object]] = []
        for item in selected_plan:
            vector = item["vector"] if isinstance(item.get("vector"), dict) else {}
            axis_support = max(float(vector.get(axis, 0.0)) for axis in axes)
            zone_match = str(item["zone"]) in required_zones
            modality_match = str(item["modality"]) in required_modalities
            if axis_support >= 0.35 or (axis_support >= 0.25 and (zone_match or modality_match)):
                support.append(item)
        support.sort(
            key=lambda item: (
                -max(float((item.get("vector") or {}).get(axis, 0.0)) for axis in axes),
                str(item["candidate_id"]),
            )
        )
        return support

    def _candidate_patch_for_requirement(
        self,
        requirement: dict[str, object],
        observation_matrix: list[dict[str, object]],
        selected_ids: set[str],
        coverage: dict[str, float],
        remaining_budget: float,
    ) -> dict[str, object]:
        primary_axes = [str(axis) for axis in requirement["primary_axes"]]
        secondary_axes = [str(axis) for axis in requirement["secondary_axes"]]
        target = float(requirement["target"])
        projected = {axis: float(coverage.get(axis, 0.0)) for axis in primary_axes}
        if all(score >= target for score in projected.values()):
            return {
                "patch_status": "state_target_already_met",
                "candidate_pool_recoverable": True,
                "recommended_candidate_ids": [],
                "estimated_added_cost": 0.0,
                "remaining_budget_after_patch": remaining_budget,
                "projected_primary_axis_scores": {axis: round(value, 3) for axis, value in projected.items()},
                "unresolved_primary_axes": [],
                "boundary": "current selected layout already satisfies this hidden-state design target",
            }
        selected_patch: list[dict[str, object]] = []
        added_cost = 0.0
        candidates = [
            row
            for row in observation_matrix
            if row.get("admissible") and str(row.get("candidate_id")) not in selected_ids
        ]
        while any(score < target for score in projected.values()):
            best = None
            best_score = 0.0
            for row in candidates:
                if str(row.get("candidate_id")) in {str(item["candidate_id"]) for item in selected_patch}:
                    continue
                cost = float(row.get("cost_index", 0.0))
                if added_cost + cost > remaining_budget:
                    continue
                vector = row["vector"] if isinstance(row.get("vector"), dict) else {}
                primary_gain = sum(
                    max(0.0, min(float(vector.get(axis, 0.0)), target) - min(projected[axis], target))
                    for axis in primary_axes
                )
                secondary_gain = sum(float(vector.get(axis, 0.0)) for axis in secondary_axes) / max(1, len(secondary_axes))
                zone_bonus = 0.05 * float(str(row.get("zone")) in set(str(zone) for zone in requirement["required_zones"]))
                modality_bonus = 0.05 * float(
                    str(row.get("modality")) in set(str(modality) for modality in requirement["required_modalities"])
                )
                score = (primary_gain + 0.12 * secondary_gain + zone_bonus + modality_bonus) / max(0.1, cost)
                if score > best_score:
                    best_score = score
                    best = row
            if best is None or best_score <= 0.0:
                break
            selected_patch.append(
                {
                    "candidate_id": str(best["candidate_id"]),
                    "node_id": str(best["node_id"]),
                    "zone": str(best["zone"]),
                    "modality": str(best["modality"]),
                    "cost_index": float(best["cost_index"]),
                    "patch_score_per_cost": round(best_score, 3),
                    "supports_axes": [
                        axis
                        for axis in primary_axes + secondary_axes
                        if float((best.get("vector") or {}).get(axis, 0.0)) >= 0.25
                    ],
                }
            )
            added_cost += float(best["cost_index"])
            vector = best["vector"] if isinstance(best.get("vector"), dict) else {}
            for axis in primary_axes:
                projected[axis] = max(projected[axis], float(vector.get(axis, 0.0)))
        unresolved_axes = [axis for axis, value in projected.items() if value < target]
        return {
            "patch_status": "candidate_pool_patch_available" if not unresolved_axes else "candidate_pool_patch_incomplete",
            "candidate_pool_recoverable": not unresolved_axes,
            "recommended_candidate_ids": [item["candidate_id"] for item in selected_patch],
            "estimated_added_cost": round(added_cost, 3),
            "remaining_budget_after_patch": round(max(0.0, remaining_budget - added_cost), 3),
            "projected_primary_axis_scores": {axis: round(value, 3) for axis, value in projected.items()},
            "unresolved_primary_axes": unresolved_axes,
            "boundary": (
                "current candidate pool can satisfy this hidden-state design target within remaining budget"
                if not unresolved_axes
                else "current candidate pool or remaining budget cannot satisfy this hidden-state design target"
            ),
        }

    def _pressure_headloss_candidate_pool(self, state_rows: list[dict[str, object]]) -> dict[str, object]:
        hard_rows = [
            row
            for row in state_rows
            if "pressure_drop_or_headloss_proxy_not_in_selected_layout" in row.get("unresolved_requirements", [])
        ]
        target_states = sorted({str(row["hidden_state"]) for row in hard_rows})
        candidate_templates = [
            {
                "candidate_id": "N3_catalyst_bed:pressure_drop_kPa",
                "candidate_type": "direct_low_cost_differential_pressure_sensor",
                "node_id": "N3_catalyst_bed",
                "zone": "catalyst_bed",
                "modality": "pressure_drop_kPa",
                "estimated_cost_index": 0.68,
                "primary_supported_states": ["catalyst_activity", "hydraulic_delay"],
                "supports_axes": {
                    "catalyst_activity_observability": 0.72,
                    "hydraulic_observability": 0.74,
                    "fault_classification_observability": 0.66,
                },
                "why_needed": "压降能区分催化剂活性衰减、床层堵塞和水力短路，是催化剂灰箱状态的最低成本补充观测。",
                "required_table": "node_modality_sensor_timeseries",
                "required_fields": [
                    "batch_id",
                    "timestamp_min",
                    "node_id",
                    "modality",
                    "value",
                    "unit",
                    "sensor_status",
                    "instrument_id",
                ],
            },
            {
                "candidate_id": "N3_catalyst_bed:headloss_kPa_per_m",
                "candidate_type": "derived_headloss_proxy_from_pressure_and_bed_geometry",
                "node_id": "N3_catalyst_bed",
                "zone": "catalyst_bed",
                "modality": "headloss_kPa_per_m",
                "estimated_cost_index": 0.18,
                "primary_supported_states": ["catalyst_activity", "hydraulic_delay"],
                "supports_axes": {
                    "catalyst_activity_observability": 0.64,
                    "hydraulic_observability": 0.70,
                    "soft_sensor_reconstruction_gain": 0.52,
                },
                "why_needed": "把压降按床层长度或床体几何归一化，可减少不同装填/流量条件下的外推风险。",
                "required_table": "site_topology_or_bed_geometry",
                "required_fields": [
                    "node_id",
                    "bed_length_m",
                    "bed_volume",
                    "nominal_HRT_min",
                    "flow_Lmin",
                ],
            },
            {
                "candidate_id": "N3_catalyst_bed:flow_normalized_pressure_residual",
                "candidate_type": "grey_box_residual_proxy",
                "node_id": "N3_catalyst_bed",
                "zone": "catalyst_bed",
                "modality": "flow_normalized_pressure_residual",
                "estimated_cost_index": 0.0,
                "primary_supported_states": ["catalyst_activity", "hydraulic_delay"],
                "supports_axes": {
                    "catalyst_activity_observability": 0.60,
                    "hydraulic_observability": 0.76,
                    "control_latency_gain": 0.56,
                },
                "why_needed": "用 pressure_drop、flow 和 HRT 构造残差，帮助区分真实催化剂衰减与流量波动导致的表观性能下降。",
                "required_table": "node_modality_sensor_timeseries + site_topology_or_bed_geometry",
                "required_fields": [
                    "N3_catalyst_bed:pressure_drop_kPa",
                    "flow_Lmin",
                    "nominal_HRT_min",
                    "bed_volume",
                ],
            },
        ]
        candidates: list[dict[str, object]] = []
        for template in candidate_templates:
            states = sorted(set(template["primary_supported_states"]) & set(target_states))
            if not states:
                continue
            candidate = dict(template)
            candidate["target_hidden_states"] = states
            candidate["field_labels_required"] = [
                "offline_lab_results.catalyst_activity",
                "campaign_operation_log.regeneration_event",
                "field_proxy_holdout_label",
            ]
            candidate["evidence_stage_required"] = "field_proxy_holdout_before_control_relaxation"
            candidate["can_resolve_without_field_package"] = False
            candidate["design_boundary"] = (
                "supplemental pressure/headloss candidate only; not part of selected installed layout until field topology "
                "and installability are reviewed"
            )
            candidates.append(candidate)
        status = "pressure_headloss_candidate_pool_not_required"
        if candidates:
            status = "pressure_headloss_candidate_pool_ready_needs_field_topology_and_labels"
        return {
            "pool_status": status,
            "candidate_count": len(candidates),
            "target_hidden_states": target_states,
            "candidate_ids": [str(candidate["candidate_id"]) for candidate in candidates],
            "candidates": candidates,
            "field_package_contract": {
                "required_tables": [
                    "node_modality_sensor_timeseries",
                    "offline_lab_results",
                    "campaign_operation_log",
                    "site_topology_or_bed_geometry",
                ],
                "minimum_matched_batch_count": 3,
                "required_batch_alignment": (
                    "pressure/headloss candidate rows, catalyst_activity labels, regeneration events and HRT/flow geometry "
                    "must share batch_id before Agent51 field proxy holdout can score them"
                ),
                "cannot_do": [
                    "cannot relax Agent49 catalyst uncertainty block",
                    "cannot write actuator policy",
                    "cannot convert synthetic design prior to field-supported claim",
                ],
            },
            "field_validation_boundary": (
                "R8b candidate pool only turns hard-unresolved sensing needs into concrete field package requirements; "
                "it does not validate catalyst activity."
            ),
            "data_origin": self.data_origin,
        }

    @staticmethod
    def _minimum_cost_requirement_patch(
        state_rows: list[dict[str, object]],
        pressure_headloss_pool: dict[str, object],
    ) -> dict[str, object]:
        recommended_ids: list[str] = []
        unresolved_states: list[str] = []
        added_cost = 0.0
        for row in state_rows:
            patch = row["candidate_patch"] if isinstance(row.get("candidate_patch"), dict) else {}
            if not row.get("ready_for_soft_sensor_estimation", False):
                unresolved_states.append(str(row["hidden_state"]))
            for candidate in patch.get("recommended_candidate_ids", []):
                if str(candidate) not in recommended_ids:
                    recommended_ids.append(str(candidate))
            added_cost += float(patch.get("estimated_added_cost", 0.0))
        hard_unresolved = [
            str(row["hidden_state"])
            for row in state_rows
            if row.get("unresolved_requirements") and not bool((row.get("candidate_patch") or {}).get("candidate_pool_recoverable"))
        ]
        status = "minimum_cost_patch_ready_for_design_prior"
        if hard_unresolved:
            status = "minimum_cost_patch_requires_new_modality_or_field_label"
        elif unresolved_states:
            status = "minimum_cost_patch_available_with_current_candidate_pool"
        return {
            "patch_status": status,
            "recommended_candidate_ids": recommended_ids,
            "estimated_added_cost_upper_bound": round(added_cost, 3),
            "unresolved_hidden_states": sorted(set(unresolved_states)),
            "hard_unresolved_hidden_states": sorted(set(hard_unresolved)),
            "pressure_headloss_candidate_pool_status": pressure_headloss_pool["pool_status"],
            "pressure_headloss_candidate_count": pressure_headloss_pool["candidate_count"],
            "pressure_headloss_candidate_ids": pressure_headloss_pool["candidate_ids"],
            "why_it_matters": (
                "This patch translates hidden-state estimation needs into node-modality additions; it is still a "
                "design-prior recommendation until field topology and holdout labels exist."
            ),
        }

    def _readiness(self, selected_plan: list[dict[str, object]], coverage: dict[str, float]) -> dict[str, object]:
        weak_ready = coverage["weak_state_coverage"] >= 0.55
        reconstruction_ready = coverage["soft_sensor_reconstruction_gain"] >= 0.62
        matrix_ready = coverage["matrix_interference_observability"] >= 0.62
        hydraulic_ready = coverage["hydraulic_observability"] >= 0.55
        budget_ready = coverage["total_cost_index"] <= self.budget_limit
        enough_sensors = len(selected_plan) >= min(4, self.max_sensors)
        field_ready = self.data_origin == "field_topology"
        score = round(
            0.22 * float(weak_ready)
            + 0.18 * float(reconstruction_ready)
            + 0.16 * float(matrix_ready)
            + 0.12 * float(hydraulic_ready)
            + 0.12 * float(budget_ready)
            + 0.10 * float(enough_sensors)
            + 0.10 * float(field_ready),
            3,
        )
        if not field_ready:
            status = "sparse_sensor_layout_ready_needs_field_topology"
        elif not weak_ready or score < 0.78:
            status = "field_sparse_sensor_layout_needs_redesign"
        else:
            status = "field_sparse_sensor_layout_candidate_ready"
        return {
            "sparse_placement_status": status,
            "sparse_placement_score": score,
            "data_origin": self.data_origin,
            "field_topology_required": not field_ready,
            "selected_sensor_count": len(selected_plan),
            "budget_limit": self.budget_limit,
            "can_update_soft_sensor_design_prior": True,
            "can_finalize_field_deployment": field_ready and weak_ready and score >= 0.78,
        }

    def _hydraulic_path_coverage_contract(self, selected_plan: list[dict[str, object]]) -> dict[str, object]:
        selected_by_zone: dict[str, list[dict[str, object]]] = {}
        selected_modalities_by_zone: dict[str, set[str]] = {}
        for item in selected_plan:
            zone = str(item.get("zone", "unknown"))
            selected_by_zone.setdefault(zone, []).append(item)
            selected_modalities_by_zone.setdefault(zone, set()).add(str(item.get("modality", "unknown")))

        stage_rows: list[dict[str, object]] = []
        for stage in self._hydraulic_path_stages():
            required_zones = [str(zone) for zone in stage["required_zones"]]
            proxy_zones = [str(zone) for zone in stage.get("proxy_zones", [])]
            required_modalities = [str(modality) for modality in stage["required_modalities"]]
            direct_sensors = [
                item
                for zone in required_zones
                for item in selected_by_zone.get(zone, [])
            ]
            proxy_sensors = [
                item
                for zone in proxy_zones
                for item in selected_by_zone.get(zone, [])
            ]
            supporting_sensors = direct_sensors or proxy_sensors
            observed_modalities = sorted(
                {
                    modality
                    for zone in required_zones + proxy_zones
                    for modality in selected_modalities_by_zone.get(zone, set())
                }
            )
            missing_zones = [zone for zone in required_zones if zone not in selected_by_zone]
            missing_modalities = [
                modality
                for modality in required_modalities
                if modality not in observed_modalities
            ]
            direct_zone_covered = len(direct_sensors) > 0
            proxy_zone_covered = not direct_zone_covered and len(proxy_sensors) > 0
            stage_covered = direct_zone_covered or proxy_zone_covered
            stage_rows.append(
                {
                    "stage_id": stage["stage_id"],
                    "stage_label": stage["stage_label"],
                    "process_role": stage["process_role"],
                    "required_zones": required_zones,
                    "proxy_zones": proxy_zones,
                    "required_modalities": required_modalities,
                    "selected_sensor_ids": [str(item["candidate_id"]) for item in supporting_sensors],
                    "observed_modalities": observed_modalities,
                    "direct_zone_covered": direct_zone_covered,
                    "proxy_zone_covered": proxy_zone_covered,
                    "stage_covered": stage_covered,
                    "missing_required_zones": missing_zones,
                    "missing_required_modalities": missing_modalities,
                    "field_evidence_needed": stage["field_evidence_needed"],
                    "control_relevance": stage["control_relevance"],
                }
            )

        covered_stage_count = sum(1 for row in stage_rows if row["stage_covered"])
        recirculation_loop_observed = any(
            row["stage_id"] == "S4_recirculation_loop" and row["stage_covered"]
            for row in stage_rows
        )
        low_frequency_time_buffer_observed = all(
            any(row["stage_id"] == stage_id and row["stage_covered"] for row in stage_rows)
            for stage_id in ("S1_equalization_buffer", "S4_recirculation_loop")
        )
        release_stage = next(row for row in stage_rows if row["stage_id"] == "S5_release_boundary")
        final_effluent_directly_observed = "effluent" in selected_by_zone
        final_release_gate_needs_effluent_label = not final_effluent_directly_observed
        unresolved_requirements = []
        if self.data_origin != "field_topology":
            unresolved_requirements.append("field_topology_and_hydraulic_path_labels_required")
        if final_release_gate_needs_effluent_label:
            unresolved_requirements.append("final_effluent_release_endpoint_not_directly_observed")
        if any(not row["stage_covered"] for row in stage_rows):
            unresolved_requirements.append("hydraulic_path_stage_gap:" + ",".join(
                row["stage_id"] for row in stage_rows if not row["stage_covered"]
            ))
        if "pressure_drop_kPa" not in {str(item.get("modality")) for item in selected_plan}:
            unresolved_requirements.append("pressure_drop_or_headloss_proxy_not_installed_in_selected_layout")

        status = "hydraulic_path_contract_ready_needs_field_topology_and_release_endpoint"
        if any(not row["stage_covered"] for row in stage_rows):
            status = "hydraulic_path_contract_needs_stage_coverage_patch"
        elif self.data_origin == "field_topology" and not unresolved_requirements:
            status = "field_hydraulic_path_contract_candidate_ready"

        return {
            "path_id": "low_cost_circular_treatment_path_v1",
            "contract_status": status,
            "data_origin": self.data_origin,
            "path_stage_count": len(stage_rows),
            "covered_stage_count": covered_stage_count,
            "directly_covered_stage_count": sum(1 for row in stage_rows if row["direct_zone_covered"]),
            "proxy_covered_stage_count": sum(1 for row in stage_rows if row["proxy_zone_covered"]),
            "path_stage_rows": stage_rows,
            "selected_zone_count": len(selected_by_zone),
            "selected_zones": sorted(selected_by_zone),
            "recirculation_loop_observed": recirculation_loop_observed,
            "low_frequency_time_buffer_observed": low_frequency_time_buffer_observed,
            "final_effluent_directly_observed": final_effluent_directly_observed,
            "final_release_gate_needs_effluent_label": final_release_gate_needs_effluent_label,
            "can_support_soft_sensor_path_prior": covered_stage_count >= 5 and recirculation_loop_observed,
            "can_support_control_replay_design_prior": (
                covered_stage_count >= 5
                and recirculation_loop_observed
                and low_frequency_time_buffer_observed
            ),
            "can_finalize_field_deployment": self.data_origin == "field_topology" and not unresolved_requirements,
            "field_package_contract": {
                "required_tables": [
                    "site_topology_or_bed_geometry",
                    "node_modality_sensor_timeseries",
                    "campaign_operation_log",
                    "offline_lab_results",
                    "agent52_replay_table",
                ],
                "required_path_fields": [
                    "node_id",
                    "zone",
                    "upstream_node_id",
                    "downstream_node_id",
                    "nominal_HRT_min",
                    "flow_Lmin",
                    "recycle_ratio",
                    "release_gate_label",
                ],
                "minimum_matched_batch_count": 3,
                "required_boundary": (
                    "selected node-modality rows must be aligned to hydraulic path stages before Agent54 feature tensor, "
                    "Agent49 control candidates or Agent52 replay rows can be treated as path-aware"
                ),
            },
            "unresolved_requirements": sorted(set(unresolved_requirements)),
            "cannot_do": [
                "cannot prove installed sensor placement without field topology review",
                "cannot write release gate when final effluent endpoint is not directly field-labeled",
                "cannot write actuator policy from hydraulic path design prior",
            ],
            "why_it_matters": (
                "topology coverage says whether selected nodes are diverse; hydraulic path coverage says whether the "
                "low-cost layout observes the actual influent-buffer-reaction-catalyst-loop-release chain that makes "
                "soft sensing, delayed diagnosis and recycle/hold/release decisions meaningful."
            ),
        }

    @staticmethod
    def _hydraulic_path_stages() -> list[dict[str, object]]:
        return [
            {
                "stage_id": "S0_influent_matrix",
                "stage_label": "进水/基质冲击入口",
                "process_role": "识别进水基质、盐度、浊度或有机负荷冲击，决定是否预处理或暂存。",
                "required_zones": ["influent"],
                "proxy_zones": ["buffer"],
                "required_modalities": ["EC_uScm", "turbidity_NTU", "UV254_abs"],
                "field_evidence_needed": ["field_labeled_fast_proxy_event_log.matrix_shock", "offline_lab_results.COD_or_matrix_proxy"],
                "control_relevance": "pre_treat_or_hold_before_reactor",
            },
            {
                "stage_id": "S1_equalization_buffer",
                "stage_label": "均质/暂存缓冲段",
                "process_role": "为低频采样、离线检测和人工复核争取时间，避免进水冲击直接进入放行判断。",
                "required_zones": ["buffer"],
                "proxy_zones": ["influent", "loop"],
                "required_modalities": ["flow_Lmin"],
                "field_evidence_needed": ["campaign_operation_log.hold_time_min", "site_topology_or_bed_geometry.buffer_volume"],
                "control_relevance": "hold_or_extend_retention_time",
            },
            {
                "stage_id": "S2_reaction_core",
                "stage_label": "反应核心段",
                "process_role": "估计氧化/吸附/催化反应完成度，决定是否延长停留时间或调整药剂候选。",
                "required_zones": ["reaction_core"],
                "proxy_zones": ["catalyst_bed", "loop"],
                "required_modalities": ["ORP_mV", "UV254_abs", "pH"],
                "field_evidence_needed": ["offline_lab_results.reaction_completion_proxy", "campaign_operation_log.dose_or_contact_time"],
                "control_relevance": "dose_adjust_or_recycle_candidate",
            },
            {
                "stage_id": "S3_catalyst_bed",
                "stage_label": "催化剂/材料床段",
                "process_role": "估计材料活性、床层堵塞和水力短路风险，决定是否保护、再生或更换候选。",
                "required_zones": ["catalyst_bed"],
                "proxy_zones": ["reaction_core", "loop"],
                "required_modalities": ["UV254_abs", "ORP_mV", "pressure_drop_kPa"],
                "field_evidence_needed": [
                    "offline_lab_results.catalyst_activity",
                    "node_modality_sensor_timeseries.pressure_drop_kPa",
                    "campaign_operation_log.regeneration_event",
                ],
                "control_relevance": "catalyst_guardrail_or_regeneration_candidate",
            },
            {
                "stage_id": "S4_recirculation_loop",
                "stage_label": "回流/循环段",
                "process_role": "把一次处理改为可迭代处理，为软传感、诊断和延迟检测提供第二次观测窗口。",
                "required_zones": ["loop"],
                "proxy_zones": ["buffer", "reaction_core"],
                "required_modalities": ["flow_Lmin", "UV254_abs"],
                "field_evidence_needed": ["campaign_operation_log.recycle_ratio", "campaign_operation_log.effect_time_min"],
                "control_relevance": "recycle_or_extend_loop_decision",
            },
            {
                "stage_id": "S5_release_boundary",
                "stage_label": "末端精处理/放行边界",
                "process_role": "判断是否进入下一处理单元、暂存等待验证或允许人工复核后的放行候选。",
                "required_zones": ["effluent"],
                "proxy_zones": ["polishing"],
                "required_modalities": ["UV254_abs", "ORP_mV", "pH", "turbidity_NTU"],
                "field_evidence_needed": [
                    "offline_lab_results.byproduct_or_release_risk",
                    "human_reviewed_release_gate_labels",
                    "agent52_replay_table.expert_action_id",
                ],
                "control_relevance": "release_gate_or_hold_for_validation",
            },
        ]

    @staticmethod
    def _soft_sensor_interface(
        selected_plan: list[dict[str, object]],
        coverage: dict[str, float],
        selected_strategy: dict[str, object],
        placement_diagnostics: dict[str, object],
        hidden_state_requirements: dict[str, object],
        hydraulic_path_contract: dict[str, object],
    ) -> dict[str, object]:
        selected_modalities = sorted({str(item["modality"]) for item in selected_plan})
        selected_nodes = sorted({str(item["node_id"]) for item in selected_plan})
        return {
            "matrix_shape": [len(selected_plan), len(OBSERVATION_AXES)],
            "selected_modalities": selected_modalities,
            "selected_nodes": selected_nodes,
            "selected_strategy_id": selected_strategy.get("strategy_id", "unknown"),
            "layout_id": f"{selected_strategy.get('strategy_id', 'unknown')}:{len(selected_plan)}x{len(OBSERVATION_AXES)}",
            "feature_view": "node_modality_by_hidden_state_observation_matrix",
            "missingness_mask_contract": {
                "mask_shape": [len(selected_plan), len(selected_modalities)],
                "mask_value_1": "sensor value available for node-modality at timestamp",
                "mask_value_0": "sensor missing, failed, delayed or not installed",
                "requires_layout_id": True,
            },
            "downstream_agents": [
                "SoftSensorAgent",
                "DataQualityAgent",
                "SensitivityAnalysisAgent",
                "WeakTargetStratifiedConformalAgent",
                "MultiFacilityCollaborativeControlAgent",
            ],
            "recommended_soft_sensor_update": "add node_id, zone, modality, observation_axis vector and missingness mask to field holdout records",
            "coverage_for_soft_sensor": coverage,
            "hidden_state_requirement_contract": {
                "ledger_status": hidden_state_requirements["ledger_status"],
                "ready_hidden_state_count": hidden_state_requirements["ready_hidden_state_count"],
                "unresolved_hidden_state_count": hidden_state_requirements["unresolved_hidden_state_count"],
                "minimum_cost_patch_status": hidden_state_requirements["minimum_cost_requirement_patch"]["patch_status"],
                "state_readiness": {
                    str(row["hidden_state"]): {
                        "ready_for_soft_sensor_estimation": row["ready_for_soft_sensor_estimation"],
                        "ready_for_control_use": row["ready_for_control_use"],
                        "min_primary_axis_score": row["min_primary_axis_score"],
                    }
                    for row in hidden_state_requirements["state_rows"]
                },
            },
            "hydraulic_path_contract": {
                "path_id": hydraulic_path_contract["path_id"],
                "contract_status": hydraulic_path_contract["contract_status"],
                "covered_stage_count": hydraulic_path_contract["covered_stage_count"],
                "path_stage_count": hydraulic_path_contract["path_stage_count"],
                "directly_covered_stage_count": hydraulic_path_contract["directly_covered_stage_count"],
                "proxy_covered_stage_count": hydraulic_path_contract["proxy_covered_stage_count"],
                "recirculation_loop_observed": hydraulic_path_contract["recirculation_loop_observed"],
                "low_frequency_time_buffer_observed": hydraulic_path_contract["low_frequency_time_buffer_observed"],
                "final_effluent_directly_observed": hydraulic_path_contract["final_effluent_directly_observed"],
                "final_release_gate_needs_effluent_label": hydraulic_path_contract["final_release_gate_needs_effluent_label"],
                "can_support_soft_sensor_path_prior": hydraulic_path_contract["can_support_soft_sensor_path_prior"],
                "can_support_control_replay_design_prior": hydraulic_path_contract["can_support_control_replay_design_prior"],
            },
            "placement_diagnostics": {
                "diagnostic_status": placement_diagnostics["diagnostic_status"],
                "axis_span_rank_ratio": placement_diagnostics["axis_span_rank_ratio"],
                "condition_number_proxy": placement_diagnostics["condition_number_proxy"],
                "reconstruction_stability_score": placement_diagnostics["reconstruction_stability_score"],
                "weak_axis_gap_count": placement_diagnostics["weak_axis_gap_count"],
            },
        }

    def _issues(
        self,
        readiness: dict[str, object],
        coverage: dict[str, float],
        placement_diagnostics: dict[str, object],
        hidden_state_requirements: dict[str, object],
        hydraulic_path_contract: dict[str, object],
    ) -> list[QualityIssue]:
        issues: list[QualityIssue] = []
        if readiness["field_topology_required"]:
            issues.append(
                QualityIssue(
                    sensor="sensor_network_sparse_placement",
                    issue_type="field_topology_required_for_deployment",
                    severity=Severity.WARNING,
                    message="当前布点基于 synthetic topology prior，需要真实管网/处理单元拓扑和水力停留时间校准后才能部署。",
                    evidence=readiness,
                )
            )
        if coverage["weak_state_coverage"] < 0.55:
            issues.append(
                QualityIssue(
                    sensor="sensor_network_sparse_placement",
                    issue_type="weak_state_observability_low",
                    severity=Severity.WARNING,
                    message="稀疏布点对 catalyst_activity 或 matrix_interference 的观测覆盖不足。",
                    evidence=coverage,
                )
            )
        if coverage["total_cost_index"] > self.budget_limit:
            issues.append(
                QualityIssue(
                    sensor="sensor_network_sparse_placement",
                    issue_type="placement_budget_exceeded",
                    severity=Severity.WARNING,
                    message="当前布点组合超过预算约束。",
                    evidence={"total_cost_index": coverage["total_cost_index"], "budget_limit": self.budget_limit},
                )
            )
        if placement_diagnostics["diagnostic_status"] == "placement_diagnostics_need_axis_patch_or_field_benchmark":
            issues.append(
                QualityIssue(
                    sensor="sensor_network_sparse_placement",
                    issue_type="placement_matrix_diagnostics_need_axis_patch_or_field_benchmark",
                    severity=Severity.WARNING,
                    message="当前稀疏观测矩阵存在弱轴缺口、条件数偏高或单点依赖，需要补充候选轴或用真实 field topology benchmark 校准。",
                    evidence={
                        "reconstruction_stability_score": placement_diagnostics["reconstruction_stability_score"],
                        "weak_axis_gaps": placement_diagnostics["weak_axis_gaps"],
                        "single_point_dependency_count": placement_diagnostics["single_point_dependency_count"],
                    },
                )
            )
        hard_unresolved = hidden_state_requirements["minimum_cost_requirement_patch"]["hard_unresolved_hidden_states"]
        if hard_unresolved:
            issues.append(
                QualityIssue(
                    sensor="sensor_network_sparse_placement",
                    issue_type="hidden_state_requirement_requires_new_modality_or_field_label",
                    severity=Severity.WARNING,
                    message="现有候选传感器池无法用剩余预算满足部分隐藏状态需求，需要新增模态、节点级 field label 或床体/HRT 证据。",
                    evidence={
                        "hard_unresolved_hidden_states": hard_unresolved,
                        "patch_status": hidden_state_requirements["minimum_cost_requirement_patch"]["patch_status"],
                    },
                )
            )
        if hydraulic_path_contract["final_release_gate_needs_effluent_label"]:
            issues.append(
                QualityIssue(
                    sensor="sensor_network_sparse_placement",
                    issue_type="hydraulic_path_release_endpoint_needs_effluent_label",
                    severity=Severity.WARNING,
                    message="当前稀疏布点覆盖了末端精处理代理段，但没有直接覆盖最终 effluent 放行端点，不能支撑 release gate。",
                    evidence={
                        "contract_status": hydraulic_path_contract["contract_status"],
                        "covered_stage_count": hydraulic_path_contract["covered_stage_count"],
                        "unresolved_requirements": hydraulic_path_contract["unresolved_requirements"],
                    },
                )
            )
        return issues

    @staticmethod
    def _recommendations(
        readiness: dict[str, object],
        selected_plan: list[dict[str, object]],
        placement_diagnostics: dict[str, object],
        hidden_state_requirements: dict[str, object],
        hydraulic_path_contract: dict[str, object],
    ) -> list[str]:
        first = selected_plan[0] if selected_plan else {}
        recs = [
            "把当前传感设计从“传感器种类敏感性”升级为“节点-模态稀疏观测矩阵”，并把 node_id/zone/missingness mask 写入 field holdout。",
            "优先在基质冲击、催化剂床、回流环和末端出水之间形成互补布点，而不是只在进出水各放一个点。",
        ]
        if first:
            recs.append(f"当前最高边际价值布点候选为 {first.get('candidate_id')}，主要贡献 {first.get('why_selected')}。")
        if placement_diagnostics.get("weak_axis_gaps"):
            first_gap = placement_diagnostics["weak_axis_gaps"][0]
            recs.append(
                "下一轮布点优化应优先补 "
                f"{first_gap['axis']}，当前覆盖 {first_gap['current_coverage']}，"
                f"候选池最佳为 {first_gap['best_available_candidate']}。"
            )
        patch = hidden_state_requirements["minimum_cost_requirement_patch"]
        if patch["hard_unresolved_hidden_states"]:
            recs.append(
                "隐藏状态需求账本显示 "
                f"{patch['hard_unresolved_hidden_states']} 不是靠现有候选池简单加点能解决；"
                "需要把 pressure_drop/headloss、节点级 catalyst proxy 标签或床体/HRT 字段纳入现场包。"
            )
        elif patch["recommended_candidate_ids"]:
            recs.append(
                "按隐藏状态需求账本，当前最小补点候选为 "
                f"{patch['recommended_candidate_ids']}，仍需 field topology 和 holdout 标签验证。"
            )
        if readiness["field_topology_required"]:
            recs.append("下一步需要真实管网/反应单元拓扑、水力停留时间、维护可达性和仪表成本，替换 synthetic topology prior。")
        if hydraulic_path_contract["final_release_gate_needs_effluent_label"]:
            recs.append(
                "水力路径合同显示当前布点只把 polishing 作为末端代理观察；若要支撑放行门，"
                "必须补 effluent 端点标签、离线 byproduct/release risk 标签和人工复核结果。"
            )
        return recs

    @staticmethod
    def _method_contract() -> dict[str, object]:
        return {
            "upgrade_id": "sensor_network_sparse_sensing_placement",
            "borrowed_from": [
                "PySensors SSPOR sparse placement for reconstruction",
                "PySensors SSPOC sparse placement for classification",
                "QR/GQR/D-optimal style basis selection",
                "water network topology aware monitoring placement",
                "robust cost constrained sensor layout comparison",
            ],
            "reality_mapping": "把进水/出水单点传感扩展为管网或处理单元节点上的稀疏 node-modality 布点，用少量低成本传感器支撑软传感重构、故障分类和延迟感知控制。",
            "data_needs": [
                "field_network_or_process_unit_graph",
                "candidate_node_hydraulic_residence_time",
                "node_access_and_install_cost",
                "historical_sensor_timeseries_by_node",
                "offline_labels_for_hidden_states",
                "contamination_or_matrix_shock_scenarios",
            ],
            "implementation_path": [
                "src/water_ai/agents/sensor_network_sparse_placement_agent.py",
                "experiments/run_agent48_sensor_network_sparse_placement.py",
                "outputs/sensor_network_sparse_placement/sparse_placement_metrics.json",
            ],
            "evaluation_metrics": [
                "algorithm_comparison.comparable_score",
                "baseline_comparison_contract.best_vs_random_delta",
                "baseline_comparison_contract.best_vs_cost_only_delta",
                "topology_coverage_score",
                "reconstruction_objective",
                "classification_objective",
                "robustness_objective",
                "axis_span_rank_ratio",
                "condition_number_proxy",
                "reconstruction_stability_score",
                "weak_axis_gap_count",
                "single_point_dependency_count",
                "hidden_state_requirement_ledger.ready_hidden_state_count",
                "hidden_state_requirement_ledger.minimum_cost_requirement_patch.patch_status",
                "hydraulic_path_coverage_contract.covered_stage_count",
                "hydraulic_path_coverage_contract.recirculation_loop_observed",
                "hydraulic_path_coverage_contract.final_release_gate_needs_effluent_label",
                "sparse_placement_score",
                "weak_state_coverage",
                "soft_sensor_reconstruction_gain",
                "fault_classification_observability",
                "total_cost_index",
            ],
            "failure_boundary": "当前布点是 synthetic topology prior 上的模型设计候选，不能替代真实管网水力模型、现场安装可达性审查或 field holdout 验证。",
        }

    @staticmethod
    def _default_topology_edges() -> list[tuple[str, str]]:
        return [
            ("N0_influent", "N1_equalization_tank"),
            ("N1_equalization_tank", "N2_reactor_mid"),
            ("N2_reactor_mid", "N3_catalyst_bed_outlet"),
            ("N3_catalyst_bed_outlet", "N5_polishing_inlet"),
            ("N5_polishing_inlet", "N6_effluent"),
            ("N3_catalyst_bed_outlet", "N4_recirculation_loop"),
            ("N4_recirculation_loop", "N1_equalization_tank"),
            ("N4_recirculation_loop", "N2_reactor_mid"),
        ]

    @staticmethod
    def _default_candidate_nodes() -> list[dict[str, object]]:
        return [
            {
                "node_id": "N0_influent",
                "zone": "influent",
                "hydraulic_position": 0.05,
                "process_representativeness": 0.35,
                "matrix_shock_exposure": 0.90,
                "catalyst_access": 0.10,
                "hydraulic_leverage": 0.45,
                "control_latency_value": 0.90,
                "maintenance_access": 0.92,
                "install_cost_index": 0.70,
            },
            {
                "node_id": "N1_equalization_tank",
                "zone": "buffer",
                "hydraulic_position": 0.20,
                "process_representativeness": 0.55,
                "matrix_shock_exposure": 0.78,
                "catalyst_access": 0.15,
                "hydraulic_leverage": 0.68,
                "control_latency_value": 0.80,
                "maintenance_access": 0.86,
                "install_cost_index": 0.82,
            },
            {
                "node_id": "N2_reactor_mid",
                "zone": "reaction_core",
                "hydraulic_position": 0.48,
                "process_representativeness": 0.88,
                "matrix_shock_exposure": 0.62,
                "catalyst_access": 0.55,
                "hydraulic_leverage": 0.60,
                "control_latency_value": 0.62,
                "maintenance_access": 0.62,
                "install_cost_index": 1.05,
            },
            {
                "node_id": "N3_catalyst_bed_outlet",
                "zone": "catalyst_bed",
                "hydraulic_position": 0.66,
                "process_representativeness": 0.86,
                "matrix_shock_exposure": 0.58,
                "catalyst_access": 0.95,
                "hydraulic_leverage": 0.52,
                "control_latency_value": 0.58,
                "maintenance_access": 0.58,
                "install_cost_index": 1.18,
            },
            {
                "node_id": "N4_recirculation_loop",
                "zone": "loop",
                "hydraulic_position": 0.58,
                "process_representativeness": 0.78,
                "matrix_shock_exposure": 0.80,
                "catalyst_access": 0.62,
                "hydraulic_leverage": 0.92,
                "control_latency_value": 0.86,
                "maintenance_access": 0.74,
                "install_cost_index": 0.92,
            },
            {
                "node_id": "N5_polishing_inlet",
                "zone": "polishing",
                "hydraulic_position": 0.78,
                "process_representativeness": 0.72,
                "matrix_shock_exposure": 0.46,
                "catalyst_access": 0.42,
                "hydraulic_leverage": 0.48,
                "control_latency_value": 0.46,
                "maintenance_access": 0.76,
                "install_cost_index": 0.96,
            },
            {
                "node_id": "N6_effluent",
                "zone": "effluent",
                "hydraulic_position": 0.96,
                "process_representativeness": 0.92,
                "matrix_shock_exposure": 0.35,
                "catalyst_access": 0.30,
                "hydraulic_leverage": 0.42,
                "control_latency_value": 0.32,
                "maintenance_access": 0.88,
                "install_cost_index": 0.76,
            },
        ]

    @staticmethod
    def _default_modality_profiles() -> dict[str, dict[str, float]]:
        return {
            "pH": {
                "pollutant": 0.24,
                "reaction": 0.40,
                "oxidant": 0.42,
                "catalyst": 0.34,
                "matrix": 0.28,
                "hydraulic": 0.10,
                "fault_classification": 0.42,
                "speed": 0.82,
                "reconstruction": 0.42,
                "cost_index": 0.55,
                "maintenance_load": 0.22,
            },
            "ORP_mV": {
                "pollutant": 0.44,
                "reaction": 0.70,
                "oxidant": 0.92,
                "catalyst": 0.38,
                "matrix": 0.32,
                "hydraulic": 0.12,
                "fault_classification": 0.65,
                "speed": 0.86,
                "reconstruction": 0.68,
                "cost_index": 0.72,
                "maintenance_load": 0.30,
            },
            "EC_uScm": {
                "pollutant": 0.32,
                "reaction": 0.24,
                "oxidant": 0.18,
                "catalyst": 0.20,
                "matrix": 0.92,
                "hydraulic": 0.18,
                "fault_classification": 0.82,
                "speed": 0.90,
                "reconstruction": 0.72,
                "cost_index": 0.62,
                "maintenance_load": 0.20,
            },
            "turbidity_NTU": {
                "pollutant": 0.36,
                "reaction": 0.28,
                "oxidant": 0.10,
                "catalyst": 0.24,
                "matrix": 0.82,
                "hydraulic": 0.36,
                "fault_classification": 0.76,
                "speed": 0.82,
                "reconstruction": 0.68,
                "cost_index": 0.70,
                "maintenance_load": 0.34,
            },
            "UV254_abs": {
                "pollutant": 0.95,
                "reaction": 0.82,
                "oxidant": 0.22,
                "catalyst": 0.42,
                "matrix": 0.54,
                "hydraulic": 0.08,
                "fault_classification": 0.70,
                "speed": 0.66,
                "reconstruction": 0.95,
                "cost_index": 1.10,
                "maintenance_load": 0.44,
            },
            "flow_Lmin": {
                "pollutant": 0.12,
                "reaction": 0.32,
                "oxidant": 0.08,
                "catalyst": 0.18,
                "matrix": 0.18,
                "hydraulic": 0.96,
                "fault_classification": 0.58,
                "speed": 0.92,
                "reconstruction": 0.52,
                "cost_index": 0.58,
                "maintenance_load": 0.18,
            },
            "temp_C": {
                "pollutant": 0.18,
                "reaction": 0.36,
                "oxidant": 0.16,
                "catalyst": 0.30,
                "matrix": 0.16,
                "hydraulic": 0.08,
                "fault_classification": 0.30,
                "speed": 0.84,
                "reconstruction": 0.36,
                "cost_index": 0.38,
                "maintenance_load": 0.12,
            },
        }

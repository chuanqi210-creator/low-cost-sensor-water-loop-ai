# Scan Shortcuts

## First Read

- `CODEGRAPH.md`
- `notes/current_status.md`
- `deliverables/manifest.json`
- `deliverables/model_core_optimization/model_core_goal.md`
- `deliverables/model_core_optimization/quantified_goal_termination_criteria.md`

## Core Model Next Reads

- Agent48 `sensor_network_sparse_placement`：runner `experiments/run_agent48_sensor_network_sparse_placement.py`；source `src/water_ai/agents/sensor_network_sparse_placement_agent.py`；test `tests/test_sensor_network_sparse_placement_agent.py`。
- Agent51 `catalyst_activity_proxy`：runner `experiments/run_agent51_catalyst_activity_proxy.py`；source `src/water_ai/agents/catalyst_activity_proxy_agent.py`；test `tests/test_catalyst_activity_proxy_agent.py`。
- Agent49 `multi_facility_collaborative_control`：runner `experiments/run_agent49_multi_facility_collaborative_control.py`；source `src/water_ai/agents/multi_facility_collaborative_control_agent.py`；test `tests/test_multi_facility_collaborative_control_agent.py`。
- Agent52 `multi_facility_replay_evaluation`：runner `experiments/run_agent52_multi_facility_replay_evaluation.py`；source `src/water_ai/agents/multi_facility_replay_evaluation_agent.py`；test `tests/test_multi_facility_replay_evaluation_agent.py`。
- Agent53 `minimal_grey_box_physics`：runner `experiments/run_agent53_minimal_grey_box_physics.py`；source `src/water_ai/agents/minimal_grey_box_physics_agent.py`；test `tests/test_minimal_grey_box_physics_agent.py`。
- Agent54 `soft_sensor_matrix_coupling`：runner `experiments/run_agent54_soft_sensor_matrix_coupling.py`；source `src/water_ai/agents/soft_sensor_matrix_coupling_agent.py`；test `tests/test_soft_sensor_matrix_coupling_agent.py`。
- Agent56 `knowledge_graph_reasoning`：runner `experiments/run_agent56_knowledge_graph_reasoning.py`；source `src/water_ai/agents/knowledge_graph_reasoning_agent.py`；test `tests/test_knowledge_graph_reasoning_agent.py`。
- Agent57 `main_chain_reconnection`：runner `experiments/run_agent57_main_chain_reconnection.py`；source `src/water_ai/agents/main_chain_reconnection_agent.py`；test `tests/test_main_chain_reconnection_agent.py`。
- Agent60 `agent_architecture_consolidation`：runner `experiments/run_agent60_agent_architecture_consolidation.py`；source `src/water_ai/agents/agent_architecture_consolidation_agent.py`；test `tests/test_agent_architecture_consolidation_agent.py`。
- Agent61 `pressure_resolution_replay_scenario_pack`：runner `experiments/run_agent61_pressure_resolution_replay_scenario_pack.py`；source `src/water_ai/agents/pressure_resolution_replay_scenario_pack_agent.py`；test `tests/test_pressure_resolution_replay_scenario_pack_agent.py`。

## Rules

- Read CODEGRAPH.md before broad scanning.
- Use agent_index to jump from Agent number to runner/source/test/output.
- Use hotspot_files only as orientation; verify behavior with tests or experiment runs.
- Synthetic/sample/template outputs are not field evidence.

## Packet Handles

核心 agent 已生成 packet 文件。后续如果任务明确落在某个核心 agent，优先读对应 packet：

- `sensor_network_sparse_placement`：`deliverables/codegraph/packets/sensor_network_sparse_placement.md`，handle `agent-6f004e515e`
- `multi_facility_collaborative_control`：`deliverables/codegraph/packets/multi_facility_collaborative_control.md`，handle `agent-3b8a09a411`
- `catalyst_activity_proxy`：`deliverables/codegraph/packets/catalyst_activity_proxy.md`，handle `agent-07e3480502`
- `multi_facility_replay_evaluation`：`deliverables/codegraph/packets/multi_facility_replay_evaluation.md`，handle `agent-fc0beffe98`
- `minimal_grey_box_physics`：`deliverables/codegraph/packets/minimal_grey_box_physics.md`，handle `agent-9ff421b3c0`
- `soft_sensor_matrix_coupling`：`deliverables/codegraph/packets/soft_sensor_matrix_coupling.md`，handle `agent-7d3dd34b33`
- `knowledge_graph_reasoning`：`deliverables/codegraph/packets/knowledge_graph_reasoning.md`，handle `agent-65718487ad`
- `main_chain_reconnection`：`deliverables/codegraph/packets/main_chain_reconnection.md`，handle `agent-0e7189e876`
- `agent_architecture_consolidation`：`deliverables/codegraph/packets/agent_architecture_consolidation.md`，handle `agent-c9071fa6df`
- `pressure_resolution_replay_scenario_pack`：`deliverables/codegraph/packets/pressure_resolution_replay_scenario_pack.md`，handle `agent-218b4bc506`

# Packet: Agent48 sensor_network_sparse_placement

- Handle: `agent-6f004e515e`
- Runner: `experiments/run_agent48_sensor_network_sparse_placement.py`
- Source: `src/water_ai/agents/sensor_network_sparse_placement_agent.py`
- Test: `tests/test_sensor_network_sparse_placement_agent.py`
- Deliverable: `deliverables/sensor_network_sparse_placement.md`
- Output dir: `outputs/agent48_sensor_network_sparse_placement`

## How To Use

- Read runner first to understand generated artifacts and report wiring.
- Read source next for behavior and interfaces.
- Read test before editing to preserve current contract.
- Treat output_dir and deliverable as evidence of previous runs, not as field validation unless explicitly marked field-origin.

## Related Nodes

| handle | kind | path | summary |
| --- | --- | --- | --- |
| `agent-6f004e515e` | `agent_workflow` | `experiments/run_agent48_sensor_network_sparse_placement.py` |  |
| `dir-0620227519` | `output_dir` | `outputs/agent48_sensor_network_sparse_placement` |  |
| `file-60c7b61816` | `referenced_path` | `deliverables/sensor_network_sparse_placement.md` | 管网布点与稀疏感知设计 |
| `file-bbca599fdf` | `file` | `experiments/run_agent48_sensor_network_sparse_placement.py` | from __future__ import annotations |
| `file-55e2132604` | `referenced_path` | `src/water_ai/agents/sensor_network_sparse_placement_agent.py` | from __future__ import annotations |
| `file-8b3893ed86` | `referenced_path` | `tests/test_sensor_network_sparse_placement_agent.py` | from water_ai.agents.sensor_network_sparse_placement_agent import ( |

## Forward Edges

| kind | target | confidence |
| --- | --- | --- |
| `documented_by` | `file:deliverables/sensor_network_sparse_placement.md` | `high` |
| `implemented_by` | `file:src/water_ai/agents/sensor_network_sparse_placement_agent.py` | `high` |
| `runs_experiment` | `file:experiments/run_agent48_sensor_network_sparse_placement.py` | `high` |
| `verified_by` | `file:tests/test_sensor_network_sparse_placement_agent.py` | `high` |
| `writes_output_dir` | `dir:outputs/agent48_sensor_network_sparse_placement` | `medium` |

## Reverse Edges

| kind | source | confidence |
| --- | --- | --- |

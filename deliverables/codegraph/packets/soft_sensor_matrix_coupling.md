# Packet: Agent54 soft_sensor_matrix_coupling

- Handle: `agent-7d3dd34b33`
- Runner: `experiments/run_agent54_soft_sensor_matrix_coupling.py`
- Source: `src/water_ai/agents/soft_sensor_matrix_coupling_agent.py`
- Test: `tests/test_soft_sensor_matrix_coupling_agent.py`
- Deliverable: `deliverables/soft_sensor_matrix_coupling.md`
- Output dir: `outputs/agent54_soft_sensor_matrix_coupling`

## How To Use

- Read runner first to understand generated artifacts and report wiring.
- Read source next for behavior and interfaces.
- Read test before editing to preserve current contract.
- Treat output_dir and deliverable as evidence of previous runs, not as field validation unless explicitly marked field-origin.

## Related Nodes

| handle | kind | path | summary |
| --- | --- | --- | --- |
| `agent-7d3dd34b33` | `agent_workflow` | `experiments/run_agent54_soft_sensor_matrix_coupling.py` |  |
| `dir-dee2ec05fe` | `output_dir` | `outputs/agent54_soft_sensor_matrix_coupling` |  |
| `file-6eb569a6c1` | `referenced_path` | `deliverables/soft_sensor_matrix_coupling.md` | 软传感 Node-Modality/Missingness 矩阵耦合 |
| `file-0b54e09ed5` | `file` | `experiments/run_agent54_soft_sensor_matrix_coupling.py` | from __future__ import annotations |
| `file-cbf682fff6` | `referenced_path` | `src/water_ai/agents/soft_sensor_matrix_coupling_agent.py` | from __future__ import annotations |
| `file-e62201d4ac` | `referenced_path` | `tests/test_soft_sensor_matrix_coupling_agent.py` | from water_ai.agents.data_quality_agent import DataQualityAgent |

## Forward Edges

| kind | target | confidence |
| --- | --- | --- |
| `documented_by` | `file:deliverables/soft_sensor_matrix_coupling.md` | `high` |
| `implemented_by` | `file:src/water_ai/agents/soft_sensor_matrix_coupling_agent.py` | `high` |
| `runs_experiment` | `file:experiments/run_agent54_soft_sensor_matrix_coupling.py` | `high` |
| `verified_by` | `file:tests/test_soft_sensor_matrix_coupling_agent.py` | `high` |
| `writes_output_dir` | `dir:outputs/agent54_soft_sensor_matrix_coupling` | `medium` |

## Reverse Edges

| kind | source | confidence |
| --- | --- | --- |

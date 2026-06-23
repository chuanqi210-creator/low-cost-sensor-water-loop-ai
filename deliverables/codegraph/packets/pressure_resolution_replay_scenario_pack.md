# Packet: Agent61 pressure_resolution_replay_scenario_pack

- Handle: `agent-218b4bc506`
- Runner: `experiments/run_agent61_pressure_resolution_replay_scenario_pack.py`
- Source: `src/water_ai/agents/pressure_resolution_replay_scenario_pack_agent.py`
- Test: `tests/test_pressure_resolution_replay_scenario_pack_agent.py`
- Deliverable: `deliverables/model_core_optimization/pressure_resolution_replay_scenario_pack.md`
- Output dir: `outputs/agent61_pressure_resolution_replay_scenario_pack`

## How To Use

- Read runner first to understand generated artifacts and report wiring.
- Read source next for behavior and interfaces.
- Read test before editing to preserve current contract.
- Treat output_dir and deliverable as evidence of previous runs, not as field validation unless explicitly marked field-origin.

## Related Nodes

| handle | kind | path | summary |
| --- | --- | --- | --- |
| `agent-218b4bc506` | `agent_workflow` | `experiments/run_agent61_pressure_resolution_replay_scenario_pack.py` |  |
| `dir-94c28223b4` | `output_dir` | `outputs/agent61_pressure_resolution_replay_scenario_pack` |  |
| `file-08aa85750e` | `file` | `deliverables/model_core_optimization/pressure_resolution_replay_scenario_pack.md` | R8o Pressure Resolution Replay 场景采集包 |
| `file-24dcdf3690` | `file` | `experiments/run_agent61_pressure_resolution_replay_scenario_pack.py` | from __future__ import annotations |
| `file-7740ee1a13` | `referenced_path` | `src/water_ai/agents/pressure_resolution_replay_scenario_pack_agent.py` | from __future__ import annotations |
| `file-59bb24ea4a` | `referenced_path` | `tests/test_pressure_resolution_replay_scenario_pack_agent.py` | import csv |

## Forward Edges

| kind | target | confidence |
| --- | --- | --- |
| `documented_by` | `file:deliverables/model_core_optimization/pressure_resolution_replay_scenario_pack.md` | `high` |
| `implemented_by` | `file:src/water_ai/agents/pressure_resolution_replay_scenario_pack_agent.py` | `high` |
| `runs_experiment` | `file:experiments/run_agent61_pressure_resolution_replay_scenario_pack.py` | `high` |
| `verified_by` | `file:tests/test_pressure_resolution_replay_scenario_pack_agent.py` | `high` |
| `writes_output_dir` | `dir:outputs/agent61_pressure_resolution_replay_scenario_pack` | `medium` |

## Reverse Edges

| kind | source | confidence |
| --- | --- | --- |

# Packet: Agent49 multi_facility_collaborative_control

- Handle: `agent-3b8a09a411`
- Runner: `experiments/run_agent49_multi_facility_collaborative_control.py`
- Source: `src/water_ai/agents/multi_facility_collaborative_control_agent.py`
- Test: `tests/test_multi_facility_collaborative_control_agent.py`
- Deliverable: `deliverables/multi_facility_collaborative_control.md`
- Output dir: `outputs/agent49_multi_facility_collaborative_control`

## How To Use

- Read runner first to understand generated artifacts and report wiring.
- Read source next for behavior and interfaces.
- Read test before editing to preserve current contract.
- Treat output_dir and deliverable as evidence of previous runs, not as field validation unless explicitly marked field-origin.

## Related Nodes

| handle | kind | path | summary |
| --- | --- | --- | --- |
| `agent-3b8a09a411` | `agent_workflow` | `experiments/run_agent49_multi_facility_collaborative_control.py` |  |
| `dir-0e25b7487c` | `output_dir` | `outputs/agent49_multi_facility_collaborative_control` |  |
| `file-4e16611f5a` | `referenced_path` | `deliverables/multi_facility_collaborative_control.md` | 多设施协同控制与策略蒸馏设计 |
| `file-dbb10a8dcf` | `file` | `experiments/run_agent49_multi_facility_collaborative_control.py` | from __future__ import annotations |
| `file-a6327ce6dd` | `referenced_path` | `src/water_ai/agents/multi_facility_collaborative_control_agent.py` | from __future__ import annotations |
| `file-ba3997b20f` | `file` | `tests/test_multi_facility_collaborative_control_agent.py` | from water_ai.agents.multi_facility_collaborative_control_agent import ( |

## Forward Edges

| kind | target | confidence |
| --- | --- | --- |
| `documented_by` | `file:deliverables/multi_facility_collaborative_control.md` | `high` |
| `implemented_by` | `file:src/water_ai/agents/multi_facility_collaborative_control_agent.py` | `high` |
| `runs_experiment` | `file:experiments/run_agent49_multi_facility_collaborative_control.py` | `high` |
| `verified_by` | `file:tests/test_multi_facility_collaborative_control_agent.py` | `high` |
| `writes_output_dir` | `dir:outputs/agent49_multi_facility_collaborative_control` | `medium` |

## Reverse Edges

| kind | source | confidence |
| --- | --- | --- |

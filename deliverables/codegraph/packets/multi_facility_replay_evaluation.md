# Packet: Agent52 multi_facility_replay_evaluation

- Handle: `agent-fc0beffe98`
- Runner: `experiments/run_agent52_multi_facility_replay_evaluation.py`
- Source: `src/water_ai/agents/multi_facility_replay_evaluation_agent.py`
- Test: `tests/test_multi_facility_replay_evaluation_agent.py`
- Deliverable: `deliverables/multi_facility_replay_evaluation.md`
- Output dir: `outputs/agent52_multi_facility_replay_evaluation`

## How To Use

- Read runner first to understand generated artifacts and report wiring.
- Read source next for behavior and interfaces.
- Read test before editing to preserve current contract.
- Treat output_dir and deliverable as evidence of previous runs, not as field validation unless explicitly marked field-origin.

## Related Nodes

| handle | kind | path | summary |
| --- | --- | --- | --- |
| `agent-fc0beffe98` | `agent_workflow` | `experiments/run_agent52_multi_facility_replay_evaluation.py` |  |
| `dir-debe11e688` | `output_dir` | `outputs/agent52_multi_facility_replay_evaluation` |  |
| `file-9aaef07f01` | `referenced_path` | `deliverables/multi_facility_replay_evaluation.md` | 多设施协同控制 Replay-Ready 离线评估 |
| `file-f864e99422` | `file` | `experiments/run_agent52_multi_facility_replay_evaluation.py` | from __future__ import annotations |
| `file-f5970b30c7` | `referenced_path` | `src/water_ai/agents/multi_facility_replay_evaluation_agent.py` | from __future__ import annotations |
| `file-48bd404e38` | `referenced_path` | `tests/test_multi_facility_replay_evaluation_agent.py` | from experiments.run_agent52_multi_facility_replay_evaluation import ( |

## Forward Edges

| kind | target | confidence |
| --- | --- | --- |
| `documented_by` | `file:deliverables/multi_facility_replay_evaluation.md` | `high` |
| `implemented_by` | `file:src/water_ai/agents/multi_facility_replay_evaluation_agent.py` | `high` |
| `runs_experiment` | `file:experiments/run_agent52_multi_facility_replay_evaluation.py` | `high` |
| `verified_by` | `file:tests/test_multi_facility_replay_evaluation_agent.py` | `high` |
| `writes_output_dir` | `dir:outputs/agent52_multi_facility_replay_evaluation` | `medium` |

## Reverse Edges

| kind | source | confidence |
| --- | --- | --- |

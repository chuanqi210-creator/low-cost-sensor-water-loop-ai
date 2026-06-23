# Packet: Agent53 minimal_grey_box_physics

- Handle: `agent-9ff421b3c0`
- Runner: `experiments/run_agent53_minimal_grey_box_physics.py`
- Source: `src/water_ai/agents/minimal_grey_box_physics_agent.py`
- Test: `tests/test_minimal_grey_box_physics_agent.py`
- Deliverable: `deliverables/minimal_grey_box_physics.md`
- Output dir: `outputs/agent53_minimal_grey_box_physics`

## How To Use

- Read runner first to understand generated artifacts and report wiring.
- Read source next for behavior and interfaces.
- Read test before editing to preserve current contract.
- Treat output_dir and deliverable as evidence of previous runs, not as field validation unless explicitly marked field-origin.

## Related Nodes

| handle | kind | path | summary |
| --- | --- | --- | --- |
| `agent-9ff421b3c0` | `agent_workflow` | `experiments/run_agent53_minimal_grey_box_physics.py` |  |
| `dir-49296e4d81` | `output_dir` | `outputs/agent53_minimal_grey_box_physics` |  |
| `file-9d78af2631` | `referenced_path` | `deliverables/minimal_grey_box_physics.md` | 最小灰箱物理机制增强 |
| `file-5cb211b5cf` | `file` | `experiments/run_agent53_minimal_grey_box_physics.py` | from __future__ import annotations |
| `file-7036d89d3a` | `file` | `src/water_ai/agents/minimal_grey_box_physics_agent.py` | from __future__ import annotations |
| `file-f21fa9a166` | `file` | `tests/test_minimal_grey_box_physics_agent.py` | from water_ai.agents.minimal_grey_box_physics_agent import MinimalGreyBoxPhysicsAgent |

## Forward Edges

| kind | target | confidence |
| --- | --- | --- |
| `documented_by` | `file:deliverables/minimal_grey_box_physics.md` | `high` |
| `implemented_by` | `file:src/water_ai/agents/minimal_grey_box_physics_agent.py` | `high` |
| `runs_experiment` | `file:experiments/run_agent53_minimal_grey_box_physics.py` | `high` |
| `verified_by` | `file:tests/test_minimal_grey_box_physics_agent.py` | `high` |
| `writes_output_dir` | `dir:outputs/agent53_minimal_grey_box_physics` | `medium` |

## Reverse Edges

| kind | source | confidence |
| --- | --- | --- |

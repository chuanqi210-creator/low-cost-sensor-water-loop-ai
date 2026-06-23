# Packet: Agent51 catalyst_activity_proxy

- Handle: `agent-07e3480502`
- Runner: `experiments/run_agent51_catalyst_activity_proxy.py`
- Source: `src/water_ai/agents/catalyst_activity_proxy_agent.py`
- Test: `tests/test_catalyst_activity_proxy_agent.py`
- Deliverable: `deliverables/catalyst_activity_proxy.md`
- Output dir: `outputs/agent51_catalyst_activity_proxy`

## How To Use

- Read runner first to understand generated artifacts and report wiring.
- Read source next for behavior and interfaces.
- Read test before editing to preserve current contract.
- Treat output_dir and deliverable as evidence of previous runs, not as field validation unless explicitly marked field-origin.

## Related Nodes

| handle | kind | path | summary |
| --- | --- | --- | --- |
| `agent-07e3480502` | `agent_workflow` | `experiments/run_agent51_catalyst_activity_proxy.py` |  |
| `dir-3b3bf75f3c` | `output_dir` | `outputs/agent51_catalyst_activity_proxy` |  |
| `file-c856388cc5` | `referenced_path` | `deliverables/catalyst_activity_proxy.md` | 催化剂活性代理观测设计 |
| `file-80035a1ed2` | `file` | `experiments/run_agent51_catalyst_activity_proxy.py` | from __future__ import annotations |
| `file-33c3f4be4e` | `referenced_path` | `src/water_ai/agents/catalyst_activity_proxy_agent.py` | from __future__ import annotations |
| `file-da78a4add3` | `file` | `tests/test_catalyst_activity_proxy_agent.py` | import csv |

## Forward Edges

| kind | target | confidence |
| --- | --- | --- |
| `documented_by` | `file:deliverables/catalyst_activity_proxy.md` | `high` |
| `implemented_by` | `file:src/water_ai/agents/catalyst_activity_proxy_agent.py` | `high` |
| `runs_experiment` | `file:experiments/run_agent51_catalyst_activity_proxy.py` | `high` |
| `verified_by` | `file:tests/test_catalyst_activity_proxy_agent.py` | `high` |
| `writes_output_dir` | `dir:outputs/agent51_catalyst_activity_proxy` | `medium` |

## Reverse Edges

| kind | source | confidence |
| --- | --- | --- |

# Packet: Agent56 knowledge_graph_reasoning

- Handle: `agent-65718487ad`
- Runner: `experiments/run_agent56_knowledge_graph_reasoning.py`
- Source: `src/water_ai/agents/knowledge_graph_reasoning_agent.py`
- Test: `tests/test_knowledge_graph_reasoning_agent.py`
- Deliverable: `deliverables/knowledge_graph_reasoning.md`
- Output dir: `outputs/agent56_knowledge_graph_reasoning`

## How To Use

- Read runner first to understand generated artifacts and report wiring.
- Read source next for behavior and interfaces.
- Read test before editing to preserve current contract.
- Treat output_dir and deliverable as evidence of previous runs, not as field validation unless explicitly marked field-origin.

## Related Nodes

| handle | kind | path | summary |
| --- | --- | --- | --- |
| `agent-65718487ad` | `agent_workflow` | `experiments/run_agent56_knowledge_graph_reasoning.py` |  |
| `dir-0f17a01a81` | `output_dir` | `outputs/agent56_knowledge_graph_reasoning` |  |
| `file-28c17df262` | `referenced_path` | `deliverables/knowledge_graph_reasoning.md` | 可推理知识图谱与主链回接 |
| `file-db62aa8e32` | `file` | `experiments/run_agent56_knowledge_graph_reasoning.py` | from __future__ import annotations |
| `file-8c441bad29` | `file` | `src/water_ai/agents/knowledge_graph_reasoning_agent.py` | from __future__ import annotations |
| `file-f125f1fcd4` | `file` | `tests/test_knowledge_graph_reasoning_agent.py` | from water_ai.agents.control_strategy_agent import ControlStrategyAgent |

## Forward Edges

| kind | target | confidence |
| --- | --- | --- |
| `documented_by` | `file:deliverables/knowledge_graph_reasoning.md` | `high` |
| `implemented_by` | `file:src/water_ai/agents/knowledge_graph_reasoning_agent.py` | `high` |
| `runs_experiment` | `file:experiments/run_agent56_knowledge_graph_reasoning.py` | `high` |
| `verified_by` | `file:tests/test_knowledge_graph_reasoning_agent.py` | `high` |
| `writes_output_dir` | `dir:outputs/agent56_knowledge_graph_reasoning` | `medium` |

## Reverse Edges

| kind | source | confidence |
| --- | --- | --- |

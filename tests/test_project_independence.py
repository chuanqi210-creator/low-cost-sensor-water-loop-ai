from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OLD_PROJECT_ROOT = "/legacy/workspaces/low-cost-sensor-water-loop-ai-cn"
OLD_PY_LEARNING_ROOT = "/legacy/workspaces/py-learning/low-cost-sensor-water-loop-ai-cn"
OLD_DAILY_PROJECT_ROOT = "/legacy/workspaces/low-cost-sensor-water-loop-ai"


ACTIVE_PROJECT_ENTRYPOINTS = [
    "AGENTS.md",
    "README.md",
    "CODEGRAPH.md",
    "docs/field_data_interface_spec.md",
    "deliverables/model_core_optimization/governance_report.md",
    "deliverables/model_core_optimization/formal_search_nonlegal_review_operator_packet.md",
    "deliverables/manifest.json",
    "outputs/agent_architecture_consolidation/formal_search_nonlegal_review_operator_packet.json",
    "outputs/model_core_governance/priority_ranking.json",
    "outputs/model_core_governance/stage_boundary_external_action_board.json",
]


def test_active_project_entrypoints_do_not_route_to_old_project_root():
    offenders = []
    for relative_path in ACTIVE_PROJECT_ENTRYPOINTS:
        text = (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")
        if OLD_PROJECT_ROOT in text or OLD_PY_LEARNING_ROOT in text or OLD_DAILY_PROJECT_ROOT in text:
            offenders.append(relative_path)

    assert offenders == []

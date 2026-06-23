from water_ai.agents.knowledge_graph_curation_agent import KnowledgeGraphCurationAgent


def test_knowledge_graph_curation_agent_builds_axis_matrix() -> None:
    report = KnowledgeGraphCurationAgent().run([])

    readiness = report.metrics["readiness"]
    coverage = report.metrics["axis_coverage"]
    evidence = report.metrics["evidence_audit"]

    assert readiness["kg_curation_status"] == "scientific_kg_seed_needs_literature_and_field_evidence"
    assert "PFAS" in coverage["pollutant_axes"]["covered"]
    assert "重金属" in coverage["pollutant_axes"]["covered"]
    assert "抗生素" in coverage["pollutant_axes"]["missing"]
    assert evidence["field_supported_entry_count"] == 0
    assert any(issue.issue_type == "no_field_supported_knowledge_edges" for issue in report.issues)


def test_knowledge_graph_curation_agent_defines_scientific_review_chain() -> None:
    report = KnowledgeGraphCurationAgent().run([])

    chain = report.metrics["scientific_review_chain"]
    backlog = report.metrics["kg_upgrade_backlog"]

    assert [item["agent"] for item in chain] == [
        "LiteratureEvidenceAgent",
        "KnowledgeGraphCurationAgent",
        "MechanismBorrowingAgent",
        "UncertaintyValidationAgent",
        "FieldRealismAgent",
    ]
    assert any(item["work_id"] == "field_supported_kg_edges" for item in backlog)
    assert any(item["work_id"] == "raw_signal_to_hidden_state_edges" for item in backlog)

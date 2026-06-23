from water_ai.agents.knowledge_graph_curation_agent import KnowledgeGraphCurationAgent
from water_ai.agents.literature_evidence_agent import LiteratureEvidenceAgent


def test_literature_evidence_agent_maps_literature_to_kg_gaps() -> None:
    kg_report = KnowledgeGraphCurationAgent().run([])
    report = LiteratureEvidenceAgent(kg_curation_metrics=kg_report.metrics).run([])

    readiness = report.metrics["readiness"]
    gap = report.metrics["kg_gap_closure"]
    axis_mapping = report.metrics["axis_mapping"]

    assert readiness["literature_evidence_status"] == "literature_seed_ready_field_validation_required"
    assert readiness["record_count"] >= 8
    assert readiness["field_supported_record_count"] == 0
    assert readiness["kg_gap_closure_score"] > 0.7
    assert "抗生素" in gap["covered_missing"]["pollutant_axes"]
    assert "染料" in gap["covered_missing"]["pollutant_axes"]
    assert "农药" in gap["covered_missing"]["pollutant_axes"]
    assert "soft_sensor" in axis_mapping["model_upgrade_axes"]
    assert any(issue.issue_type == "literature_not_field_validation" for issue in report.issues)


def test_literature_evidence_agent_requires_model_upgrade_contract_fields() -> None:
    report = LiteratureEvidenceAgent().run([])

    schema_fields = {field["field"] for field in report.metrics["extraction_schema"]}
    upgrade_ids = {item["upgrade_id"] for item in report.metrics["model_upgrade_map"]}

    assert {
        "citation_key",
        "extracted_claim",
        "borrowed_idea",
        "project_mapping",
        "data_requirements",
        "evaluation_metrics",
        "failure_boundary",
    } <= schema_fields
    assert "soft_sensor_field_conformal_calibration" in upgrade_ids
    assert "scientific_kg_field_supported_edges" in upgrade_ids

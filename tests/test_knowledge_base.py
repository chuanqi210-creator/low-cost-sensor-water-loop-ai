from water_ai.knowledge import query_knowledge_base


def test_knowledge_base_matches_catalyst_site_fouling() -> None:
    matches = query_knowledge_base(
        {
            "pollutant_residual_risk": 0.48,
            "reaction_completion": 0.42,
            "oxidant_remaining": 0.72,
            "catalyst_activity": 0.28,
            "matrix_interference": 0.31,
            "byproduct_risk": 0.28,
            "recycle_gain": 0.36,
            "release_readiness": 0.74,
            "sensor_confidence": 1.0,
        }
    )

    assert matches[0]["entry_id"] == "kb_catalyst_site_fouling"
    assert "catalyst_deactivation" in matches[0]["supports_rules"]
    assert matches[0]["action_biases"]["regenerate_catalyst"] > 0
    assert matches[0]["evidence_stage"] == "literature_informed_simulation"


def test_knowledge_base_requires_coherent_evidence() -> None:
    matches = query_knowledge_base(
        {
            "pollutant_residual_risk": 0.2,
            "reaction_completion": 0.82,
            "oxidant_remaining": 0.7,
            "catalyst_activity": 0.72,
            "matrix_interference": 0.2,
            "byproduct_risk": 0.2,
            "recycle_gain": 0.05,
            "release_readiness": 0.9,
            "sensor_confidence": 0.95,
        }
    )

    assert matches == []


def test_knowledge_base_includes_persistent_pollutant_and_field_needs() -> None:
    matches = query_knowledge_base(
        {
            "pollutant_residual_risk": 0.72,
            "reaction_completion": 0.28,
            "oxidant_remaining": 0.68,
            "catalyst_activity": 0.72,
            "matrix_interference": 0.32,
            "byproduct_risk": 0.25,
            "recycle_gain": 0.38,
            "release_readiness": 0.55,
            "sensor_confidence": 0.92,
        }
    )

    entry_ids = [match["entry_id"] for match in matches]

    assert "kb_pfas_adsorption_or_membrane_needed" in entry_ids
    pfas = next(match for match in matches if match["entry_id"] == "kb_pfas_adsorption_or_membrane_needed")
    assert "目标物 LC-MS/LC-MS-MS 标签" in pfas["field_validation_need"]
    assert pfas["action_biases"]["dose_oxidant"] < 0

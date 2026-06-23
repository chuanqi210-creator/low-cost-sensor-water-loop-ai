from experiments.train_soft_sensor_model import (
    HYDRAULIC_PATH_FEATURE_COLUMNS,
    _path_feature_variation_status,
    build_dataset,
    build_layout_interfaces,
)


def test_soft_sensor_training_builds_multiple_layout_variants() -> None:
    layouts = build_layout_interfaces()

    layout_ids = {str(item["layout_id"]) for item in layouts}
    holdout_layouts = {str(item["layout_id"]) for item in layouts if item["layout_holdout_role"] == "holdout"}
    summaries = [item["layout_variant_summary"] for item in layouts]

    assert len(layout_ids) >= 6
    assert holdout_layouts
    assert any(summary["final_effluent_directly_observed"] for summary in summaries)
    assert any(summary["final_release_gate_needs_effluent_label"] for summary in summaries)
    assert len({summary["covered_stage_count"] for summary in summaries}) >= 3


def test_soft_sensor_training_dataset_supports_synthetic_layout_holdout() -> None:
    dataset = build_dataset()

    assert set(dataset["layout_holdout_role"]) == {"train", "holdout"}
    assert dataset["layout_id"].nunique() >= 6
    assert dataset.loc[dataset["layout_holdout_role"] == "holdout", "layout_id"].nunique() >= 2
    assert _path_feature_variation_status(dataset) == "synthetic_path_feature_variation_ready_for_layout_holdout"

    unique_counts = {feature: int(dataset[feature].nunique()) for feature in HYDRAULIC_PATH_FEATURE_COLUMNS}
    assert unique_counts["hydraulic_path_coverage_rate"] >= 3
    assert unique_counts["direct_hydraulic_path_coverage_rate"] >= 3
    assert unique_counts["final_effluent_direct_observed_flag"] == 2
    assert unique_counts["release_endpoint_label_missing_flag"] == 2

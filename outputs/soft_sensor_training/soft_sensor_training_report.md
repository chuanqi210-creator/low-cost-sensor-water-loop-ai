# 软传感器校正模型训练报告

- model_version: `rf_multioutput_v5_path_layout_holdout`
- rows: `51840`
- layout_variant_count: `7`
- layout_holdout_status: `synthetic_layout_holdout_ready_needs_field_path_labels`
- mean_mae: `0.0138`
- layout_holdout_mean_mae: `0.01524`

## MAE

- pollutant_residual_risk: 0.00769
- reaction_completion: 0.01088
- oxidant_remaining: 0.00553
- catalyst_activity: 0.02421
- matrix_interference: 0.02067

## R2

- pollutant_residual_risk: 0.99489
- reaction_completion: 0.98566
- oxidant_remaining: 0.99862
- catalyst_activity: 0.91345
- matrix_interference: 0.89805

## Layout Holdout

- pollutant_residual_risk: 0.00824
- reaction_completion: 0.0117
- oxidant_remaining: 0.0065
- catalyst_activity: 0.02711
- matrix_interference: 0.02267

## Boundary

- layout holdout uses synthetic layout variants only; it validates schema and benchmark readiness, not field deployment.
- field path labels, node-specific sensor values and final effluent endpoint labels are still required before release-gate claims.

# 最小灰箱物理机制增强

- grey_box_physics_status：`synthetic_grey_box_physics_prior_ready_needs_field_calibration`
- mean_grey_box_residual：`0.131`
- max_mass_balance_residual：`0.0`
- max_byproduct_risk：`0.597`
- can_write_to_actuator：`False`
- can_write_to_release_gate：`False`

## 方法契约

- upgrade_id：`P4_minimal_grey_box_physics`
- reality_mapping：用最小参数层表达停留时间、反应速率、基质抑制、催化剂衰减、副产物风险和守恒残差。
- failure_boundary：未经过 field calibration 前，只能作为 synthetic grey-box prior；不能证明现场机理或授权放行。

## 场景物理残差表

| Scenario | k_eff | RTD risk | Predicted outlet | Synthetic observed | Residual | Mass residual | Byproduct risk | Failure modes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `clean_release` | `0.02248` | `0.08` | `0.113` | `0.08` | `0.033` | `0.0` | `0.401` | `[]` |
| `oxidant_limitation` | `0.00919` | `0.14` | `0.552` | `0.453` | `0.099` | `0.0` | `0.313` | `[]` |
| `reaction_time_insufficient` | `0.01427` | `0.36` | `0.487` | `0.283` | `0.204` | `0.0` | `0.455` | `['grey_box_residual_high']` |
| `catalyst_deactivation` | `0.00746` | `0.18` | `0.567` | `0.361` | `0.206` | `0.0` | `0.42` | `['grey_box_residual_high', 'catalyst_decay_risk_high']` |
| `matrix_shock` | `0.00988` | `0.282` | `0.489` | `0.378` | `0.111` | `0.0` | `0.597` | `['matrix_inhibition_strong']` |

## R4b Guardrail Failure Boundary Patch

- `catalyst_uncertain_low_proxy` / `catalyst_activity_proxy_uncertainty`：keep J4_safe_low_cost_standby or human-reviewed catalyst protection until field proxy labels close the uncertainty.；boundary=synthetic guardrail resolved false-positive catalyst protection; field proxy labels are required before catalyst-control claim upgrade.
- `hydraulic_delay_violation` / `hydraulic_latency_and_storage_uncertainty`：prefer J3_polishing_and_release_gate over recycle escalation until hydraulic execution evidence exists.；boundary=synthetic guardrail resolved high-regret recycle action; field hydraulic replay is required before recycle-control claim upgrade.

## 校准需求

- batch_inlet_outlet_lab
- hydraulic_rtd_or_tracer
- oxidant_dose_residual_log
- catalyst_age_regeneration_log
- byproduct_panel

## 结论与边界

- 将停留时间分布、拟一级反应、基质抑制、催化剂衰减、副产物风险和质量/氧化剂残差写入软传感与控制的灰箱先验。
- 把 field 数据采集从单纯传感流扩展为进出水目标污染物、RTD/池容、氧化剂投加和余量、催化剂再生历史、副产物 lab panel。
- Agent53 输出只能作为模型结构先验和残差审计，不能单独授权执行器或 release gate。
- 优先校准 `catalyst_deactivation`：grey_box_residual=0.206，failure_modes=['grey_box_residual_high', 'catalyst_decay_risk_high']。
- R4b 已把控制 guardrail resolved cases 接入 Agent53：后续应把 catalyst proxy uncertainty 和 hydraulic latency/storage uncertainty 作为灰箱失败边界持续审计。
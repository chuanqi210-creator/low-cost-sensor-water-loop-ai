# Agent 12 多批次运行调度模拟报告

- summary: 运行调度：pause_or_limit_intake；成功率 1.0，验证工时占用 2.17，催化剂备件 0。
- campaign batches: 8
- total elapsed min: 1580
- total cost: 8.709
- total energy: 4.709
- catalyst spares remaining: 0
- oxidant stock remaining: 1.5

## 调度建议

- 限制新批次进水，优先消化待验证批次和维护风险。
- 增加旁路快检班次或压缩低价值验证项，优先保障放行门和副产物验证。
- 补充催化剂模块库存，并把寿命低于 0.45 的批次列入预防性维护。

## 批次记录

### Batch 0: sensor_faults

- success: `True`
- elapsed_min: `66`
- all_actions: `['inspect_hydraulics', 'calibrate_sensors', 'hold_for_validation', 'recirculate', 'release']`
- validation_minutes: `40`
- catalyst_lifetime_fraction_end: `0.88`
- catalyst_regen_count_end: `0`

### Batch 1: oxidant_limitation

- success: `True`
- elapsed_min: `173`
- all_actions: `['dose_oxidant', 'recirculate', 'regenerate_catalyst', 'hold_for_validation', 'recirculate', 'release']`
- validation_minutes: `46`
- catalyst_lifetime_fraction_end: `0.768`
- catalyst_regen_count_end: `1`

### Batch 2: reaction_time_insufficient

- success: `True`
- elapsed_min: `202`
- all_actions: `['hold_for_validation', 'recirculate', 'hold_for_validation', 'recirculate', 'release']`
- validation_minutes: `146`
- catalyst_lifetime_fraction_end: `0.729`
- catalyst_regen_count_end: `1`

### Batch 3: matrix_shock

- success: `True`
- elapsed_min: `147`
- all_actions: `['switch_or_pretreat', 'hold_for_validation', 'recirculate', 'release']`
- validation_minutes: `73`
- catalyst_lifetime_fraction_end: `0.708`
- catalyst_regen_count_end: `1`

### Batch 4: catalyst_deactivation

- success: `True`
- elapsed_min: `363`
- all_actions: `['regenerate_catalyst', 'hold_for_validation', 'recirculate', 'replace_catalyst', 'hold_for_validation', 'recirculate', 'release']`
- validation_minutes: `146`
- catalyst_lifetime_fraction_end: `0.981`
- catalyst_regen_count_end: `0`

### Batch 5: oxidant_limitation

- success: `True`
- elapsed_min: `172`
- all_actions: `['dose_oxidant', 'recirculate', 'regenerate_catalyst', 'hold_for_validation', 'recirculate', 'release']`
- validation_minutes: `46`
- catalyst_lifetime_fraction_end: `0.867`
- catalyst_regen_count_end: `1`

### Batch 6: matrix_shock

- success: `True`
- elapsed_min: `146`
- all_actions: `['switch_or_pretreat', 'hold_for_validation', 'recirculate', 'release']`
- validation_minutes: `73`
- catalyst_lifetime_fraction_end: `0.846`
- catalyst_regen_count_end: `1`

### Batch 7: catalyst_deactivation

- success: `True`
- elapsed_min: `311`
- all_actions: `['regenerate_catalyst', 'hold_for_validation', 'recirculate', 'regenerate_catalyst', 'hold_for_validation', 'recirculate', 'release']`
- validation_minutes: `146`
- catalyst_lifetime_fraction_end: `0.628`
- catalyst_regen_count_end: `3`

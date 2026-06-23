# 低成本传感-循环窗口敏感性分析

推荐设计：full_36min_3min，综合评分 0.882，平均成功率 1.0。

## 推荐

- 默认采用 full_36min_3min：观测窗口 36 min，采样间隔 3 min，噪声倍率 0.75，禁用传感器 []，工程成本指数 0.9，月校准 9.02 h，平均总耗时 155.4 min。
- 若现场更看重冗余，可保留 full_24min_1min 作为稳健备选，综合评分 0.783。
- 任何低成本配置都不应绕过最终放行安全门；节省传感成本只能通过循环窗口和旁路验证换取。

## 设计排序

### full_36min_3min

- utility_score: `0.882`
- mean_success_rate: `1.0`
- worst_success_rate: `1.0`
- mean_total_elapsed_min: `155.4`
- mean_cost: `0.489`
- mean_energy: `0.334`
- sensor_cost_index: `0.9`
- sensor_noise_multiplier: `0.75`
- purchase_cost_cny: `11800.0`
- annual_maintenance_cny: `5040.0`
- calibration_hours_per_month: `9.02`
- sampling_load_index: `0.5`
- disabled_sensors: `[]`

### full_24min_1min

- utility_score: `0.783`
- mean_success_rate: `1.0`
- worst_success_rate: `1.0`
- mean_total_elapsed_min: `226.6`
- mean_cost: `0.952`
- mean_energy: `0.606`
- sensor_cost_index: `1.0`
- sensor_noise_multiplier: `0.55`
- purchase_cost_cny: `11800.0`
- annual_maintenance_cny: `5040.0`
- calibration_hours_per_month: `9.02`
- sampling_load_index: `1.0`
- disabled_sensors: `[]`

### core_48min_5min

- utility_score: `0.0`
- mean_success_rate: `0.0`
- worst_success_rate: `0.0`
- mean_total_elapsed_min: `689.2`
- mean_cost: `2.417`
- mean_energy: `0.904`
- sensor_cost_index: `0.44`
- sensor_noise_multiplier: `1.15`
- purchase_cost_cny: `5100.0`
- annual_maintenance_cny: `2760.0`
- calibration_hours_per_month: `5.41`
- sampling_load_index: `0.298`
- disabled_sensors: `['UV254_abs', 'temp_C']`

### minimal_60min_5min

- utility_score: `0.0`
- mean_success_rate: `0.0`
- worst_success_rate: `0.0`
- mean_total_elapsed_min: `727.7`
- mean_cost: `2.28`
- mean_energy: `0.559`
- sensor_cost_index: `0.355`
- sensor_noise_multiplier: `1.35`
- purchase_cost_cny: `3900.0`
- annual_maintenance_cny: `2220.0`
- calibration_hours_per_month: `4.33`
- sampling_load_index: `0.286`
- disabled_sensors: `['UV254_abs', 'temp_C', 'flow_Lmin']`

### no_uv_48min_3min

- utility_score: `0.0`
- mean_success_rate: `0.0`
- worst_success_rate: `0.0`
- mean_total_elapsed_min: `1101.0`
- mean_cost: `5.187`
- mean_energy: `0.895`
- sensor_cost_index: `0.51`
- sensor_noise_multiplier: `0.95`
- purchase_cost_cny: `5300.0`
- annual_maintenance_cny: `2880.0`
- calibration_hours_per_month: `5.77`
- sampling_load_index: `0.571`
- disabled_sensors: `['UV254_abs']`

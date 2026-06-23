# Literature Evidence Extraction Schema

该 schema 用于把文献转成可写入 Scientific KG 和模型升级 backlog 的结构化记录。

| 字段 | 为什么需要 | 服务对象 |
| --- | --- | --- |
| `citation_key` | 保证每条 claim 可追溯到来源。 | KG edge provenance, claim audit |
| `extracted_claim` | 只抽取可映射到模型的科学主张，避免泛泛摘要。 | mechanism borrowing, model gap diagnosis |
| `borrowed_idea` | 明确借鉴的是方法、机制、指标还是控制约束。 | implementation planning |
| `project_mapping` | 把文献结论映射到当前软传感、灰箱过程、控制或 KG 环节。 | reality mapping |
| `data_requirements` | 列出从文献 seed 走向 field validation 所需的真实字段。 | field data interface |
| `evaluation_metrics` | 将文献启发转成可检验指标，而不是只加功能。 | model validation |
| `failure_boundary` | 防止 literature/simulation claim 被误写成现场实证结论。 | claim boundary enforcement |

## Sources

- `pan_2026_ecomats`：Multi-agent artificial intelligence designs novel catalysts for ultrafast water purification (2026), https://doi.org/10.1038/s44221-026-00634-9
- `ching_2021_wwtp_soft_sensor_review`：Advances in soft sensors for wastewater treatment plants: A systematic review (2021), https://doi.org/10.1016/j.jwpe.2021.102367
- `parsa_2024_dynamic_control_review`：Dynamic Modelling, Process Control, and Monitoring of Selected Biological and Advanced Oxidation Processes for Wastewater Treatment (2024), https://doi.org/10.3390/bioengineering11020189
- `angelopoulos_2021_conformal_prediction_intro`：A Gentle Introduction to Conformal Prediction and Distribution-Free Uncertainty Quantification (2021), https://arxiv.org/abs/2107.07511
- `nsr_2026_scientific_kg_survey`：Bridging data and discovery: a survey on knowledge graphs in AI for science (2026), https://academic.oup.com/nsr/article/13/8/nwag140/8507209
- `lupu_2023_antibiotics_aop_review`：Key Principles of Advanced Oxidation Processes: Current and Future Perspectives of Antibiotics Removal from Wastewater (2023), https://doi.org/10.3390/catal13091280
- `water_2021_textile_dye_aop_review`：Treatment of Textile Wastewater Using Advanced Oxidation Processes: A Critical Review (2021), https://doi.org/10.3390/w13243515
- `sustainability_2025_pesticide_aop_review`：A Review of Various Advanced Oxidation Techniques for Pesticide Degradation for Practical Application in Aqueous Environments (2025), https://doi.org/10.3390/su17104710

## 强制边界

- `literature_supported` 只能作为模型升级假设或 KG seed。
- 任何参数写回、release gate 修改或 field 结论，必须另有真实数据 G0-G5 验收。
- 摘要/元数据级记录必须在进入参数范围前做全文表格化抽取。
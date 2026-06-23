# Agent 37 知识图谱策展报告

- summary: 知识图谱策展：scientific_kg_seed_needs_literature_and_field_evidence；轴覆盖 0.700，field-supported edges 0 条。
- kg_curation_status: `scientific_kg_seed_needs_literature_and_field_evidence`
- kg_curation_score: `0.622`

## 生成文件

- knowledge_graph_curation: `deliverables/knowledge_graph_curation.md`
- knowledge_graph_schema: `deliverables/knowledge_graph_schema.md`
- agent37_report: `outputs/agent37_knowledge_graph_curation/agent37_report.md`
- knowledge_graph_records: `outputs/agent37_knowledge_graph_curation/knowledge_graph_records.json`

## 风险边界

- `no_field_supported_knowledge_edges`：当前知识图谱没有真实数据支持边，只能作为文献/仿真 seed，不能宣称现场验证成立。
- `pollutant_axis_undercoverage`：污染物轴仍缺：染料, 抗生素, 农药。
- `raw_signal_grounding_weak`：知识条目主要由隐藏状态触发，低成本原始信号到机制/状态的证据边仍偏弱。
# Native CodeGraph 与本地 Fallback 效果评估

结论：`hybrid_fallback_is_useful_but_not_equivalent_to_native_codegraph`。

## 本地 fallback 更适合本项目的地方

- Encodes project-specific research main chain and agent semantics.
- Links agent runner/source/test/deliverable/output in a way generic CodeGraph would not infer by itself.
- Preserves field/synthetic/template evidence boundaries in the navigation layer.

## 不如原生 CodeGraph 的地方

- No Tree-sitter level symbol resolution or call graph.
- No native packet/search/explain command surface.
- No duplicate detection, architecture drift, PR impact, or review artifact generation.
- No incremental cache or MCP server.

## 本轮已补的不足

- Added stable node handles.
- Added forward and reverse adjacency indexes.
- Added task route index by model workstream.
- Added packet-like bundles for core agents.
- Added explicit fallback evaluation and boundary notes.

## 下一步升级建议

- Install Node.js 24.10+ and @lzehrung/codegraph when CLI-level symbol navigation becomes worth the setup cost.
- Keep the local project packets even after native CodeGraph is installed, because they encode research semantics.

## 使用边界

- 本地图谱用于减少 scan 摩擦和定位上下文，不证明运行时行为。
- 结构关系不能替代测试、实验 replay、field holdout 或人工复核。
- 即便未来安装原生 CodeGraph CLI，也应保留这些项目语义 packet，因为原生工具不会天然理解本项目的研究主链和证据边界。

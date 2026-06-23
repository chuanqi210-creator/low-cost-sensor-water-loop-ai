# 2026-06-23 Architecture Review

## Review Scope

本轮是 review-loop 的第 0 轮，只读审查当前仓库的代码结构、行为契约、证据边界、runner/source 边界和后续行为保持优化入口。目标不是新增 agent 或补功能，而是在缺真实 field package / 外部输入的当前阶段，找出可以安全减冗、降低漂移风险的工程优化点。

实际审查域：

- 核心运行时：`src/water_ai/domain.py`、`src/water_ai/pipeline.py`、`src/water_ai/closed_loop.py`、`src/water_ai/process_dynamics.py`、基础 agent 和核心测试。
- 证据治理：`field_evidence_gate`、R7 real field replay pipeline、stage boundary、governance recovery、focused catalyst response 和相关 tests。
- Runner/manifest：`experiments/run_*.py` 中的输出写入、manifest 投影、重复 IO boilerplate 和超大 runner 热点。

## Current State

- 项目框架已经成熟，当前主要瓶颈是真实现场数据包、外部人工响应和 field validation，不是继续堆内部 agent。
- 当前仓库是唯一活动工作区，不应再依赖迁移前旧目录。
- 已有完整回归基线为 `.venv/bin/python -m pytest -q`，最近记录为 `665 passed`。
- 工作树中已有大量独立化整理和关键产物刷新改动；后续 review-loop 必须只追加本轮相关改动，不回滚不相关文件。

## Protected Behavior

以下行为和接口不得在结构优化中漂移：

- `SensorReading`、`QualityIssue`、`AgentReport` 是全链路基础契约；`AgentReport.metrics` 是 agent 间事实传递通道。
- 主链顺序保持为 DataQuality -> SoftSensor -> Mechanism -> FaultDiagnosis -> CatalystLifecycle -> ValidationPlanning -> ControlStrategy -> StrategyProfile -> CostSafety -> Arbitration。
- `strategy_profile.metrics["selected_profile"]` 必须继续传给 `CostSafetyAgent(objective_profile=...)`。
- 闭环逻辑必须继续读取 `arbitration.metrics["final_plan"]`、`arbitration.metrics["blocked_actions"]` 和 `strategy_profile.metrics["selected_profile"]`。
- `release` 仍是终止动作；被阻断的 release 不得绕过仲裁安全门。
- `final_plan` action 字段保持 `action_id`、`action_name`、`original_score`、`net_score`、`objective_score`、`parameters`。
- `metrics` 硬 key 保持 `state_estimate`、`ranked_actions`、`evaluated_actions`、`final_plan`、`blocked_actions`、`selected_profile`。

## Evidence And No-Write Boundaries

以下边界是硬约束：

- `synthetic`、`sample`、`template`、`literature` 只能作为接口测试、模板、方法先验或追溯依据，不能升级为 field evidence。
- `UnifiedFieldEvidenceGate` 是 facade，不是新 agent；它合并既有证据门输出，但不删除历史 agent，不写 actuator/release gate。
- R7 pipeline 默认是验证和修复路由，不创建 field evidence。
- Stage boundary 只能排序外部动作，不证明现场效果，不恢复模型链，不生成法律/专利结论。
- Focused catalyst merge 只产生可提交候选，不能进入 full router，不能跑 Agent51 holdout，不能放松 Agent49 保护，不能恢复模型链。
- `can_generate_field_evidence`、`can_write_to_actuator`、`can_write_to_release_gate`、`can_write_to_protective_control`、`can_emit_field_claim_upgrade` 等字段不得被结构优化误改。

敏感 env var 和路径：

- `FOCUSED_CATALYST_RESPONSE_PATH`
- `FIELD_ACTIVATION_RESPONSE_PATH`
- `REAL_FIELD_REPLAY_PACKAGE_DIR`
- `FIELD_PATH_ENDPOINT_LABEL_PACKAGE_DIR`
- `FORMAL_SEARCH_RESULT_PACKAGE_PATH`
- `FORMAL_SEARCH_NONLEGAL_REVIEW_RESPONSE_PATH`
- `PRESSURE_RESOLUTION_REPLAY_ROWS_PATH`
- `R7_TO_R8P_WORK_PACKAGE_DIR`
- `R8V_TARGET_GATE_RESULT_PACKAGE_PATH`
- `R8V_TARGET_GATE_OPERATOR_REVIEW_PATH`

## Structure Findings

- Runner/source 边界总体可用，但部分 runner 承担了过多 IO、manifest 投影和局部业务 helper。
- `experiments/run_agent50_model_core_governance.py` 和 `experiments/run_agent60_agent_architecture_consolidation.py` manifest 投影巨大，不适合作为第一轮重构入口。
- `experiments/run_agent61_pressure_resolution_replay_scenario_pack.py` 同时包含大量写入、schema validation、R7 staging/completion 和 target gate helper；第一轮不应迁移业务 helper，因为 tests 直接 import 多个 runner 私有函数。
- `experiments/run_formal_search_nonlegal_review_operator_packet.py` 风险最低：核心业务已在 `src/water_ai/formal_search_nonlegal_review_operator_packet.py`，runner 主要是读 JSON、写 JSON/Markdown、更新 manifest。
- `experiments/run_agent44_field_replay_import.py` 风险次低：核心导入逻辑在 source，runner 重复 generated files、JSON writer、manifest relative path。

重复 boilerplate：

- `PROJECT_ROOT = Path(__file__).resolve().parents[1]`
- `MANIFEST_PATH = PROJECT_ROOT / "deliverables" / "manifest.json"`
- `_read_json` / `_read_optional_json`
- `write_text(json.dumps(..., ensure_ascii=False, indent=2))`
- `mkdir(parents=True, exist_ok=True)`
- `path.relative_to(PROJECT_ROOT)`
- `_update_manifest` read-mut-write

## Recommended Loop

每轮必须执行：

1. 能力发现：读 `AGENTS.md`、`CODEGRAPH.md`、`notes/current_status.md`，用 `tool_search` 检查是否有更合适的工具、插件、连接器或 API。
2. 只读审查：把任务限定到一个域，先列出禁止漂移项。
3. 入口门：每个候选任务必须有风险等级、受保护输出、测试命令和退出条件。
4. 小步执行：一轮只改一个最高价值小任务。
5. 复核：做 spec review、code quality review、测试，再决定是否继续下一轮。

## Round 1 Recommendation

首轮执行 `experiments/run_formal_search_nonlegal_review_operator_packet.py` 的行为保持小抽象：

- 抽出 JSON 写入 helper。
- 抽出 text/Markdown 写入 helper。
- 抽出 project-relative path helper。
- 用 helper 替代 runner 内重复写入，不改变 packet schema、manifest key、输出路径或报告内容。
- 同时保留 formal-search handoff 的独立化路径修复：已知迁移前项目根会被 rebased 到当前仓库，避免 `FORMAL_SEARCH_RESULT_PACKAGE_PATH` 指向旧 checkout。

不得改变：

- `outputs/agent_architecture_consolidation/formal_search_nonlegal_review_operator_packet.json`
- `deliverables/model_core_optimization/formal_search_nonlegal_review_operator_packet.md`
- JSON root key：`operator_packet_metadata`、`operator_action`、`response_contract`、`downstream_state`、`boundary`、`human_review_rows`
- manifest key：所有 `latest_formal_search_nonlegal_review_operator_packet*`

本轮复核后新增的路径验收：

- `outputs/agent_architecture_consolidation/preliminary_formal_search_handoff.json`
- `outputs/agent_architecture_consolidation/formal_search_nonlegal_review_operator_packet.json`
- `deliverables/manifest.json`

以上三处的 preliminary formal search package path 必须指向 `...`。

## Backlog

- Agent44：抽 generated files / JSON writer / manifest relative path 小 helper。
- Agent61：只抽 artifact 写入表，不移动业务 helper。
- 证据治理：抽 no-write/evidence-boundary 构造器，但必须保留全部字段名和 manifest 投影。
- R7 submission stage：把多段 if 收敛为表驱动状态映射，保持阻断顺序 import -> minimum replay -> path endpoint -> sufficiency -> R7 acceptance -> no-write。
- Focused merge：集中 row/top-level 校验规则，不能放松 `data_origin=field`、template marker、batch alignment、no-write confirmed。

## Rejected Suggestions

- 不新增 agent。
- 不新增 synthetic 能力或模板证据。
- 不重调控制阈值、release 阈值或安全门。
- 不重命名或扁平化 `metrics` 字段。
- 不把 operator packet、route guide、repair work order、formal-search handoff 当作 field validation。
- 不在第一轮拆 Agent50/Agent60 巨型 manifest。
- 不在第一轮迁移 Agent61 业务 helper 到 `src`。

## Acceptance Commands

Review-only 检索：

```bash
rg -n "Capability Discovery|tool_search|skill-creator|synthetic|template|field evidence|can_write_to_actuator|can_write_to_release_gate" AGENTS.md CODEGRAPH.md notes/current_status.md src experiments tests
git diff --check
```

Round 1 formal-search runner 优化：

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q -p no:cacheprovider tests/test_formal_search_nonlegal_review_operator_packet.py
git diff --check
```

如果后续触碰 Agent44：

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q -p no:cacheprovider tests/test_field_replay_import_agent.py
```

如果后续触碰 Agent61：

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q -p no:cacheprovider tests/test_pressure_resolution_replay_scenario_pack_agent.py
```

只有跨 runner 共享 helper 或触碰 Agent50/60/61 多处 manifest 时，才运行完整回归：

```bash
.venv/bin/python -m pytest -q
```

## Capabilities Used

- Skills: `superpowers:using-superpowers`、`superpowers:executing-plans`、`superpowers:verification-before-completion`。
- Tools: `tool_search`、`rg`、`sed`、`git status`、`wc`、`apply_patch`、`pytest`。
- Context: `CODEGRAPH.md` 与 `deliverables/codegraph/*` fallback 图谱文档，三个只读 subagent explorer 审查结果。
- Considered but not used: browser、GitHub、automation、skill-creator。原因：本轮是本地仓库 review-loop 和小型行为保持重构，不涉及外部 API、PR 操作、定时自动化或创建可复用 Codex skill。

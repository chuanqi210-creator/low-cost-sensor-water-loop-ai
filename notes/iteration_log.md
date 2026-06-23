# 迭代日志

## 2026-06-22 R8u187 Formal Nonlegal Operator Handoff Dependency Repair

背景：

- R8u186 已经明确进入 `internal_expansion_saturated_waiting_for_external_input`，原则上不再继续内部微扩张。
- 但在刷新允许的外部恢复通道时发现硬性边界矛盾：`formal_search_ai_nonlegal_review_brief.json` 仍有 7 行人工非法律审查对象，`formal_search_nonlegal_review_operator_packet.json` 却因当前 Agent60 response template 变成 0 行而退化为 `formal_search_nonlegal_review_operator_packet_blocked_by_response_template`。
- 该问题不是展示层问题，也不是新增功能诉求，而是可保护性/人工审查 handoff 的状态漂移；属于 R8u186 允许的 `repair_hard_boundary_contradiction`。

系统化调试：

- 复核当前 JSON：
  - `formal_search_ai_nonlegal_review_brief.json`：`brief_rows=7`。
  - `formal_search_nonlegal_review_response_template.json`：`expected_review_packet_row_ids=[]`、`response_template_rows=[]`。
  - `formal_search_nonlegal_comparison_review_packet.json`：因当前未设置 `FORMAL_SEARCH_RESULT_PACKAGE_PATH`，状态为 `formal_search_nonlegal_review_packet_blocked_at_validation_execution`。
  - `preliminary_formal_search_handoff.json`：仍指向可用的 `preliminary_formal_search_result_package.json`，该包的 validation summary 显示可以进入人工非法律技术比较。
- 根因：operator packet 只依赖 Agent60 最新 response template；当 Agent60 在默认无 `FORMAL_SEARCH_RESULT_PACKAGE_PATH` 的环境下刷新时，模板合法回到 0 行，但 AI brief 和 preliminary formal search handoff 仍然代表上一轮已验证的 7 行人工审查对象。

TDD 红灯：

- 新增 `tests/test_formal_search_nonlegal_review_operator_packet.py::test_operator_packet_uses_ready_ai_brief_when_agent60_template_was_refreshed_without_upstream_package`。
- 红灯结果：`TypeError: build_formal_search_nonlegal_review_operator_packet() got an unexpected keyword argument 'upstream_formal_search_result_package_path'`。

实现：

- 更新 `src/water_ai/formal_search_nonlegal_review_operator_packet.py`：
  - 新增 `upstream_formal_search_result_package_path` 输入。
  - 当 AI brief 通过边界、brief rows 存在、且上游 package path 可用，而当前 Agent60 response template 为空时，使用 AI brief rows 生成稳定的人类审查合同。
  - 新增 `contract_basis=ai_brief_rows_with_upstream_formal_search_package_dependency`。
  - `operator_action` 新增 `upstream_source_env_var=FORMAL_SEARCH_RESULT_PACKAGE_PATH`、`upstream_formal_search_result_package_path` 和 `required_env_vars`。
  - validation command 改为同时携带 `FORMAL_SEARCH_RESULT_PACKAGE_PATH` 与 `FORMAL_SEARCH_NONLEGAL_REVIEW_RESPONSE_PATH`。
- 更新 `experiments/run_formal_search_nonlegal_review_operator_packet.py`：
  - 读取 `outputs/agent_architecture_consolidation/preliminary_formal_search_handoff.json`。
  - 若 handoff 状态为 `preliminary_formal_search_package_ready_for_FORMAL_SEARCH_RESULT_PACKAGE_PATH`，把其 package path 传入 operator packet。
  - Markdown 报告和 manifest 增加上游 env/path 与 contract basis。

当前结果：

- `packet_status=formal_search_nonlegal_review_operator_packet_ready_waiting_for_human_response`
- `expected_review_packet_row_count=7`
- `high_priority_review_row_count=1`
- `accepted_review_row_count=0`
- `contract_basis=ai_brief_rows_with_upstream_formal_search_package_dependency`
- `upstream_source_env_var=FORMAL_SEARCH_RESULT_PACKAGE_PATH`
- `source_env_var=FORMAL_SEARCH_NONLEGAL_REVIEW_RESPONSE_PATH`
- 第一条 validation command 同时包含两个 env，并运行 `.venv/bin/python experiments/run_agent60_agent_architecture_consolidation.py`。

验证：

- `.venv/bin/pytest tests/test_formal_search_nonlegal_review_operator_packet.py::test_operator_packet_uses_ready_ai_brief_when_agent60_template_was_refreshed_without_upstream_package -q`：红灯后通过。
- `.venv/bin/pytest tests/test_formal_search_nonlegal_review_operator_packet.py -q`：`4 passed`。
- `.venv/bin/python experiments/run_formal_search_nonlegal_review_operator_packet.py`：通过，operator packet 恢复为 7 行 ready。
- `.venv/bin/python experiments/run_external_activation_router.py && .venv/bin/python experiments/run_agent50_model_core_governance.py && .venv/bin/python experiments/run_stage_boundary_external_action_board.py && .venv/bin/python experiments/run_governance_recovery_integrity_audit.py`：通过，最高主链阻塞仍为 `FOCUSED_CATALYST_RESPONSE_PATH`。
- `.venv/bin/pytest tests/test_formal_search_nonlegal_review_operator_packet.py tests/test_external_activation_router.py tests/test_stage_boundary_external_action_board.py tests/test_governance_recovery_integrity_audit.py tests/test_agent50_core_interface_integration.py tests/test_model_core_optimization_governance_agent.py -q`：`97 passed`。
- `.venv/bin/pytest -q`：`663 passed`。
- `.venv/bin/python tools/build_project_codegraph.py`：通过，CodeGraph fallback 刷新为 `409 files / 5481 nodes / 8636 edges`。

边界：

- R8u187 不生成 human nonlegal review response。
- R8u187 不生成法律意见、prior-art 结论、专利授权判断或权利要求文本。
- R8u187 不生成 field evidence，不恢复 field replay/control 主链。
- R8u187 不写 actuator，不写 release gate。
- R8u187 只是修复人工审查 handoff 的上游依赖表达，避免默认环境刷新污染已验证的 7 行人工审查合同。

## 2026-06-22 R8u186 Stage Boundary Internal Expansion Saturation Gate

背景：

- 用户要求借鉴桌面 `复杂项目启动前置治理协议_v3_核心版.md` 优化工程模型，并建议开启子代理分工。
- 三个只读子代理分别审阅了协议可吸收原则、工程接入点和验证字段。共同结论是：不应复制完整协议或新增一套协议系统；最小高价值接入点是现有 `stage_boundary_external_action_board` / recovery audit / manifest 摘要。
- 当前 stage boundary 已具备 machine handoff、resource boundary、low-friction round gate 和 claim promotion snapshot；剩余最高阻塞仍是真实 `FOCUSED_CATALYST_RESPONSE_PATH`，继续内部微字段扩张边际价值下降。

TDD 红灯：

- 新增 `tests/test_stage_boundary_external_action_board.py::test_stage_boundary_action_board_exposes_protocol_adapted_internal_expansion_saturation_gate`。
- 红灯结果：`KeyError: internal_expansion_saturation_gate`。
- 新增 `tests/test_agent50_core_interface_integration.py::test_manifest_exposes_internal_expansion_saturation_gate_summary`。
- 红灯结果：旧产物缺少 `internal_expansion_saturation_gate` 与 manifest 摘要。

实现：

- 更新 `src/water_ai/stage_boundary_external_action_board.py`：
  - 新增 `internal_expansion_saturation_gate`。
  - 选择性吸收协议中的 `anti_protocol_bloat_gate`、`continuous_cycle_no_idle_expansion`、`claim_readiness_ladder`、`stage_handoff_route_back` 和 `micro_task_execution_check`。
  - 当前 gate 判定为 `internal_expansion_saturated_waiting_for_external_input`，并明确 `micro_tweak_expansion_allowed=False`。
  - 只允许 `consume_real_external_input`、`repair_hard_boundary_contradiction`、`refresh_artifacts_after_external_input` 和 `run_verification_without_expanding_model_logic`。
  - 禁止无新边界缺口时继续添加 operator convenience fields、继续生成 synthetic/template 进度、在 external wait 阶段无并行内部任务却开子代理、或绕过 field package 推广 claim/control。
- 更新 `experiments/run_stage_boundary_external_action_board.py` 与 `experiments/run_agent50_model_core_governance.py`：
  - 通用和 Agent50 manifest 均写入 saturation gate 状态、决策、必需外部输入、validation command、stop reasons、resume conditions 和 claim readiness ceiling。

当前结果：

- `outputs/model_core_governance/stage_boundary_external_action_board.json` 已包含 `internal_expansion_saturation_gate`。
- 当前 `gate_status=internal_expansion_saturated_waiting_for_external_input`。
- 当前 `decision=stop_internal_micro_expansion_wait_for_real_external_input`。
- 当前 `required_next_external_input=FOCUSED_CATALYST_RESPONSE_PATH`。
- 当前 `claim_readiness_ceiling=governance_contract_only_until_real_field_validation`。

边界：

- R8u186 只是验证治理层与空转抑制门。
- 它不生成 field evidence，不恢复模型链，不写 actuator/release gate，不输出法律/专利结论。
- 它不阻止真正的新核心接口；若出现硬性边界矛盾、真实外部输入或新的 P1/P2 核心接口阻塞，可以重新打开下一轮核心工作。

验证：

- `.venv/bin/pytest -q tests/test_stage_boundary_external_action_board.py::test_stage_boundary_action_board_exposes_protocol_adapted_internal_expansion_saturation_gate`：红灯后通过。
- `.venv/bin/python experiments/run_stage_boundary_external_action_board.py && .venv/bin/python experiments/run_agent50_model_core_governance.py`：刷新通过。
- `.venv/bin/pytest -q tests/test_stage_boundary_external_action_board.py::test_stage_boundary_action_board_exposes_protocol_adapted_internal_expansion_saturation_gate tests/test_agent50_core_interface_integration.py::test_manifest_exposes_internal_expansion_saturation_gate_summary`：`2 passed`。
- `.venv/bin/pytest -q tests/test_stage_boundary_external_action_board.py tests/test_agent50_core_interface_integration.py tests/test_governance_recovery_integrity_audit.py tests/test_model_core_optimization_governance_agent.py tests/test_external_activation_operator_packet.py`：`84 passed`。
- `.venv/bin/pytest -q`：`662 passed`。
- `.venv/bin/python tools/build_project_codegraph.py`：通过，CodeGraph fallback 刷新为 `409 files / 5474 nodes / 8629 edges`。

## 2026-06-22 R8u185 Stage Boundary Embedded Rejection Boundaries

背景：

- R8u184 已把 focused template/schema/command sequence 嵌入最高阶段入口和 manifest。
- 继续复核证据边界发现：`external_activation_operator_action_packet` 已含 `rejection_boundaries`、`boundary_checks` 与 `no_write_boundary`，但 stage board / low-friction gate / manifest 仍未暴露这些拒收条件。
- 这会造成一个风险：只读最高入口时，操作者能知道怎么提交，却不能完整看到什么输入必须拒收；这直接关系到 synthetic/template/sample 不被误写成 field 结论。

TDD 红灯：

- 更新 `tests/test_stage_boundary_external_action_board.py`：
  - 要求 `machine_handoff.manual_action_required.rejection_boundaries` 透传 operator packet 拒收条件。
  - 要求 `boundary_checks` 透传模板行不是 field evidence 的检查。
  - 要求 `no_write_boundary` 明确包含不能生成 field evidence。
  - 要求 low-friction gate 继承同一边界。
- 红灯结果：两个测试均因 `KeyError: rejection_boundaries` 失败。
- 更新 `tests/test_agent50_core_interface_integration.py`：
  - 要求通用 manifest 和 Agent50 manifest 暴露 rejection boundaries、boundary checks 和 no-write boundary。
  - 红灯结果：manifest 缺少 `latest_stage_boundary_external_action_board_machine_handoff_rejection_boundaries`。

实现：

- 更新 `src/water_ai/stage_boundary_external_action_board.py`：
  - R7/focused action row 从 operator packet 透传 `rejection_boundaries`、`boundary_checks`、`no_write_boundary`。
  - `operator_runbook`、`machine_handoff.manual_action_required` 和 `low_friction_round_gate.manual_action_required` 均继承这些边界。
- 更新 `experiments/run_stage_boundary_external_action_board.py` 与 `experiments/run_agent50_model_core_governance.py`：
  - 通用 manifest 与 Agent50 manifest 均写入 rejection boundaries、boundary checks 和 no-write boundary。

当前结果：

- 最高入口现在明确拒收：
  - template/sample/synthetic rows as field evidence。
  - TODO/template markers in required evidence payloads。
  - 不满足最小共同真实 batch 的响应。
  - 未确认 no-write boundary 的响应。
  - 跳过 focused merge/full response preflight/materialized package preflight/replay/holdout/operator review 的 shortcut。
- `governance_recovery_integrity_score=1.0`。

边界：

- R8u185 只是把已存在的证据拒收规则嵌入最高阶段入口和 manifest。
- 它不生成 field evidence，不恢复模型链，不改变 action 排序，不写 actuator/release gate，不输出法律/专利结论。

验证：

- `.venv/bin/pytest -q tests/test_stage_boundary_external_action_board.py::test_stage_boundary_action_board_exposes_machine_handoff_for_low_friction_resume tests/test_stage_boundary_external_action_board.py::test_stage_boundary_action_board_scores_low_friction_round_gate`：红灯后通过，2 passed。
- `.venv/bin/pytest -q tests/test_agent50_core_interface_integration.py::test_manifest_exposes_stage_boundary_machine_handoff_summary`：刷新 runner 后通过，1 passed。
- `.venv/bin/python experiments/run_governance_recovery_integrity_audit.py`：`recovery_integrity_score=1.0`。

## 2026-06-22 R8u184 Stage Boundary Embedded Focused Action Package

背景：

- R8u183 已将 focused catalyst 外部输入链路的 validation command 统一为可执行命令。
- 继续复核最高外部动作发现：`external_activation_operator_action_packet` 已经包含 focused template、schema、merge plan 和 `current_commands`，但最高阶段入口 `stage_boundary_external_action_board` 的 `machine_handoff` 与 `low_friction_round_gate` 仍只暴露 env var、action 和 validation command。
- 这意味着只读 stage board 或 manifest 的 agent 仍需要再扫描 operator packet 才知道填哪个模板、按哪个 schema、执行哪些命令。

TDD 红灯：

- 更新 `tests/test_stage_boundary_external_action_board.py`：
  - 要求 `machine_handoff.manual_action_required.input_template_path` 指向 focused template。
  - 要求 `schema_path` 指向 focused schema。
  - 要求 `command_sequence` 包含填模板、export `FOCUSED_CATALYST_RESPONSE_PATH` 和 focused merge 命令。
  - 要求 low-friction gate 继承同一最小执行包。
- 红灯结果：两个测试均因 `KeyError: input_template_path` 失败。
- 更新 `tests/test_agent50_core_interface_integration.py`：
  - 要求通用 manifest 和 Agent50 manifest 暴露 input template、schema 和 command sequence。
  - 红灯结果：manifest 缺少 `latest_stage_boundary_external_action_board_machine_handoff_input_template_path`。

实现：

- 更新 `src/water_ai/stage_boundary_external_action_board.py`：
  - R7/focused action row 从 `external_activation_operator_action_packet` 透传 `focused_template_path`、`focused_schema_path`、`focused_merge_plan_path` 和 `current_commands`。
  - `operator_runbook` 增加 `input_template_path`、`schema_path` 和 `command_sequence`。
  - `machine_handoff.manual_action_required` 增加 `input_template_path`、`schema_path`、`merge_plan_path` 和 `command_sequence`。
  - `low_friction_round_gate` 自动继承 machine handoff 的同一执行包。
- 更新 `experiments/run_stage_boundary_external_action_board.py` 与 `experiments/run_agent50_model_core_governance.py`：
  - 通用 manifest 与 Agent50 manifest 均写入 machine handoff 的 template/schema/command sequence 字段。

当前结果：

- `machine_handoff.manual_action_required.input_template_path=outputs/catalyst_response_submission_kit/focused_catalyst_response_template.json`。
- `machine_handoff.manual_action_required.schema_path=outputs/catalyst_response_submission_kit/focused_catalyst_response_schema.json`。
- `machine_handoff.manual_action_required.command_sequence` 包含：
  - `fill outputs/catalyst_response_submission_kit/focused_catalyst_response_template.json with real field values`
  - `export FOCUSED_CATALYST_RESPONSE_PATH=/absolute/path/to/filled_focused_response.json`
  - `.venv/bin/python experiments/run_focused_catalyst_response_merge.py`
- 通用和 Agent50 manifest 已同步暴露这些字段。
- `governance_recovery_integrity_score=1.0`。

边界：

- R8u184 只是把 operator packet 的最小执行包嵌入最高阶段入口和 manifest。
- 它不生成 field evidence，不恢复模型链，不改变 action 排序，不写 actuator/release gate，不输出法律/专利结论。

验证：

- `.venv/bin/pytest -q tests/test_stage_boundary_external_action_board.py::test_stage_boundary_action_board_exposes_machine_handoff_for_low_friction_resume tests/test_stage_boundary_external_action_board.py::test_stage_boundary_action_board_scores_low_friction_round_gate`：红灯后通过，2 passed。
- `.venv/bin/pytest -q tests/test_agent50_core_interface_integration.py::test_manifest_exposes_stage_boundary_machine_handoff_summary`：刷新 runner 后通过，1 passed。
- `.venv/bin/python experiments/run_governance_recovery_integrity_audit.py`：`recovery_integrity_score=1.0`。

## 2026-06-22 R8u183 Executable Focused Validation Command Contract

背景：

- R8u182 已把 `external_activation_operator_action_packet` 的下一步动作统一为顶层 `next_operator_action`。
- 继续复核最高外部恢复链时发现：operator packet 的 `current_commands` 已经是可执行命令 `.venv/bin/python experiments/run_focused_catalyst_response_merge.py`，但 stage board 的 machine handoff、low-friction gate 和 Agent50 推荐文本仍使用裸脚本路径 `experiments/run_focused_catalyst_response_merge.py`。
- 这不会改变模型判断，但会增加真实 focused catalyst response 提交时的人机执行摩擦：操作者能看到脚本，却不一定能直接复制执行。

TDD 红灯：

- 更新 `tests/test_stage_boundary_external_action_board.py`：
  - `machine_handoff.next_route_validation_command` 必须等于 `.venv/bin/python experiments/run_focused_catalyst_response_merge.py`。
  - `low_friction_round_gate.manual_action_required.validation_command` 必须等于同一可执行命令。
- 红灯结果：两个测试均失败，旧输出仍为裸脚本路径。
- 更新 `tests/test_model_core_optimization_governance_agent.py`：
  - Agent50 的 `recommended_next_core_action.next_experiment` 必须包含 `.venv/bin/python experiments/run_focused_catalyst_response_merge.py`。
  - 红灯结果：推荐文本仍只包含裸脚本路径。

实现：

- 更新 `src/water_ai/stage_boundary_external_action_board.py`：
  - 新增 `_python_experiment_command()`。
  - R7/focused action row 的 `validation_command` 由 `focused_merge_runner` 路径规范化为可执行命令。
  - `machine_handoff` 与 `low_friction_round_gate` 自动继承该命令。
- 更新 `src/water_ai/agents/model_core_optimization_governance_agent.py`：
  - focused handoff 推荐文本中的 focused merge、field activation 和 Agent50 rerun 都改为 `.venv/bin/python ...` 形式。
- 重新运行 stage board、governance recovery audit 和 Agent50 runner，刷新 JSON、Markdown 与 manifest。

当前结果：

- `machine_handoff.next_route_validation_command=.venv/bin/python experiments/run_focused_catalyst_response_merge.py`。
- `low_friction_round_gate.manual_action_required.validation_command=.venv/bin/python experiments/run_focused_catalyst_response_merge.py`。
- Agent50 推荐文本现在提示：
  - `.venv/bin/python experiments/run_focused_catalyst_response_merge.py`
  - `.venv/bin/python experiments/run_field_activation_matrix.py`
  - `.venv/bin/python experiments/run_agent50_model_core_governance.py`
- `governance_recovery_integrity_score=1.0`，说明 manifest 与 stage board 的恢复链仍一致。

边界：

- R8u183 只把真实外部输入恢复链从“脚本路径”压成“可执行命令合同”。
- 它不生成 field evidence，不恢复模型链，不改变 action 排序，不写 actuator/release gate，不输出法律/专利结论。

验证：

- `.venv/bin/pytest -q tests/test_stage_boundary_external_action_board.py::test_stage_boundary_action_board_exposes_machine_handoff_for_low_friction_resume tests/test_stage_boundary_external_action_board.py::test_stage_boundary_action_board_scores_low_friction_round_gate`：红灯后通过，2 passed。
- `.venv/bin/pytest -q tests/test_model_core_optimization_governance_agent.py::test_governance_agent_consumes_field_activation_matrix_without_resuming_model_chain tests/test_stage_boundary_external_action_board.py::test_stage_boundary_action_board_exposes_machine_handoff_for_low_friction_resume tests/test_stage_boundary_external_action_board.py::test_stage_boundary_action_board_scores_low_friction_round_gate`：3 passed。

## 2026-06-22 R8u182 External Operator Packet Generic Next Operator Action

背景：

- R8u181 已修复 stage boundary 低摩擦入口的 canonical/underlying action 语义。
- 当前最高价值动作仍是补 `catalyst_activity` 的 6 行 focused catalyst response，并设置 `FOCUSED_CATALYST_RESPONSE_PATH`。
- 复查 operator-facing packet 时发现：`external_activation_operator_action_packet` 输出了 `packet_next_operator_action`，但没有项目内通用的顶层 `next_operator_action`。这会让后续 agent 或操作者必须记住该 packet 的特殊字段名，降低恢复链可复用性。

TDD 红灯：

- 更新 `tests/test_external_activation_operator_packet.py` 的两个契约测试。
- 新增断言要求 `packet["next_operator_action"] == packet["packet_next_operator_action"]`。
- 红灯结果：两个测试均因 `KeyError: 'next_operator_action'` 失败，说明旧 packet 缺少通用下一步动作字段。

实现：

- 更新 `src/water_ai/external_activation_operator_packet.py`：
  - 在顶层 payload 中新增 `next_operator_action`。
  - 该字段保持与 `packet_next_operator_action` 完全一致。
- 更新 `experiments/run_external_activation_operator_packet.py`：
  - 终端输出新增 `next_operator_action`。
  - Markdown 报告新增 `next_operator_action`。
  - manifest latest 指针改为消费通用 `next_operator_action`。
- 刷新 `experiments/run_external_activation_operator_packet.py`、`experiments/run_stage_boundary_external_action_board.py` 和 `experiments/run_agent50_model_core_governance.py`，保持 packet、stage board 和 Agent50 指针一致。

当前结果：

- `packet_next_operator_action=fill_outputs/catalyst_response_submission_kit/focused_catalyst_response_template.json_with_real_field_values_then_set_FOCUSED_CATALYST_RESPONSE_PATH`。
- `next_operator_action=fill_outputs/catalyst_response_submission_kit/focused_catalyst_response_template.json_with_real_field_values_then_set_FOCUSED_CATALYST_RESPONSE_PATH`。
- `latest_external_activation_operator_action_packet_next_operator_action` 与 `latest_agent50_external_activation_operator_action_packet_next_operator_action` 均已读到同一动作。

边界：

- R8u182 只增强 operator packet 的通用接口、一致性和可恢复性。
- 它不生成 field evidence，不恢复模型链，不改变 action 排序，不写 actuator/release gate，不输出法律/专利结论。

验证：

- `.venv/bin/pytest -q tests/test_external_activation_operator_packet.py`：红灯后通过，2 passed。
- `.venv/bin/pytest -q tests/test_external_activation_operator_packet.py tests/test_stage_boundary_external_action_board.py tests/test_agent50_core_interface_integration.py tests/test_model_core_optimization_governance_agent.py`：78 passed。

## 2026-06-22 R8u181 Low-Friction Canonical Focus Handoff Action

背景：

- R8u180 已把模块阶段终止证明表补齐，继续堆治理证明的边际价值下降。
- 当前 stage boundary 已进入外部激活等待，Agent50 推荐动作为 `FIELD_ACTIVATION_RESPONSE_FOCUS_HANDOFF_NEXT_ACTION`。
- 复查真实产物发现：`low_friction_round_gate.selected_source_env_var=FOCUSED_CATALYST_RESPONSE_PATH`，但 `selected_action_id=R8u139_R7_REAL_FIELD_PACKAGE`。底层语义并不错误，因为 focused response 最终服务 R7 real field package；但人机恢复入口容易把“先补 6 行 focused catalyst response”误读成“先补全量 R7 field package”。

TDD 红灯：

- 更新 `tests/test_stage_boundary_external_action_board.py::test_stage_boundary_action_board_scores_low_friction_round_gate`。
- 新增断言要求 low-friction gate 暴露：
  - `selected_canonical_action_id=FIELD_ACTIVATION_RESPONSE_FOCUS_HANDOFF_NEXT_ACTION`
  - `selected_underlying_action_id=R8u139_R7_REAL_FIELD_PACKAGE`
- 更新 `tests/test_agent50_core_interface_integration.py::test_manifest_exposes_low_friction_round_gate_summary`。
- 红灯结果：`KeyError: selected_canonical_action_id` 与 manifest 字段缺失，符合预期。

实现：

- 更新 `src/water_ai/stage_boundary_external_action_board.py`：
  - 新增 `_canonical_low_friction_action_id()`。
  - `low_friction_round_gate` 保留 `selected_action_id`，并新增 `selected_underlying_action_id` 与 `selected_canonical_action_id`。
  - Markdown 报告显示 canonical/underlying 两层 action id。
- 更新 `experiments/run_stage_boundary_external_action_board.py`：
  - 通用 manifest 写入 canonical/underlying 两个 low-friction 字段。
- 更新 `experiments/run_agent50_model_core_governance.py`：
  - Agent50 manifest 写入 canonical/underlying 两个 low-friction 字段。

当前结果：

- `selected_action_id=R8u139_R7_REAL_FIELD_PACKAGE`。
- `selected_underlying_action_id=R8u139_R7_REAL_FIELD_PACKAGE`。
- `selected_canonical_action_id=FIELD_ACTIVATION_RESPONSE_FOCUS_HANDOFF_NEXT_ACTION`。
- `selected_source_env_var=FOCUSED_CATALYST_RESPONSE_PATH`。

边界：

- R8u181 只是恢复入口命名和人机交接语义修复。
- 它不改变 action 排序，不生成 field evidence，不恢复模型链，不写 actuator/release gate，不输出法律/专利结论。

验证：

- `.venv/bin/pytest -q tests/test_stage_boundary_external_action_board.py::test_stage_boundary_action_board_scores_low_friction_round_gate tests/test_agent50_core_interface_integration.py::test_manifest_exposes_low_friction_round_gate_summary`：红灯后通过。
- `.venv/bin/pytest -q tests/test_stage_boundary_external_action_board.py::test_stage_boundary_action_board_scores_low_friction_round_gate tests/test_agent50_core_interface_integration.py::test_manifest_exposes_low_friction_round_gate_summary tests/test_stage_boundary_external_action_board.py tests/test_agent50_core_interface_integration.py`：35 passed。
- `.venv/bin/pytest -q`：660 passed。
- `.venv/bin/python tools/build_project_codegraph.py`：通过，CodeGraph fallback 为 409 files、5465 nodes、8618 edges。

## 2026-06-22 R8u180 Module Stage Termination Proof Rows

背景：

- 当前 goal 要求每轮迭代不仅有 `core_score`，还要有可计算阶段终止条件和证据边界。
- 现有 Agent50 已有 `module_stage_termination_gate`，但主要输出汇总状态、阈值、metrics 和 blockers；当 gate 通过时，后续 agent 仍需要自行推断每个指标为什么通过、属于哪一层、增强哪种能力、失败边界是什么。
- 本轮不新增 agent，不新增 synthetic 模型结果，只把阶段终止判断压成机器可读 proof rows。

TDD 红灯：

- 新增 `tests/test_model_core_optimization_governance_agent.py::test_governance_agent_outputs_module_stage_termination_proof_rows`。
- 红灯结果：`KeyError: 'termination_proof_rows'`，说明生产代码尚未暴露逐项阶段终止证明。
- 新增 `tests/test_agent50_core_interface_integration.py::test_core_gate_and_manifest_expose_module_stage_termination_proof`。
- 红灯结果：`KeyError: 'termination_proof_rows'`，说明现有 `core_score_termination_gate.json` 和 manifest 也无法恢复该证明。

实现：

- 更新 `src/water_ai/agents/model_core_optimization_governance_agent.py`：
  - 新增 `MODULE_TERMINATION_PROOF_METADATA`。
  - 新增 `_module_stage_termination_proof_rows()`。
  - `module_stage_termination_gate` 现在输出 `termination_proof_status`、`termination_pass_rate` 和 `termination_proof_rows`。
- 更新 `experiments/run_agent50_model_core_governance.py`：
  - manifest 新增 `latest_agent50_module_stage_termination_proof_status`。
  - manifest 新增 `latest_agent50_module_stage_termination_pass_rate`。
  - manifest 新增 `latest_agent50_module_stage_termination_proof_row_count`。

当前结果：

- `termination_proof_status=module_stage_termination_proof_complete`。
- `termination_pass_rate=1.0`。
- `termination_proof_row_count=7`。
- 每一行 proof 都包含 metric、value、threshold、passed、system_layer、core_capability、evidence_source、failure_boundary、actuator/release no-write 和 field-claim boundary。

边界：

- R8u180 只证明架构阶段终止条件逐项可审查。
- 它不能生成 field evidence，不能把 synthetic/template/literature 升级为 field conclusion，不能恢复模型链，不能授权 actuator 或 release gate。

验证：

- `.venv/bin/pytest -q tests/test_model_core_optimization_governance_agent.py::test_governance_agent_outputs_module_stage_termination_proof_rows`：1 passed。
- `.venv/bin/pytest -q tests/test_agent50_core_interface_integration.py::test_core_gate_and_manifest_expose_module_stage_termination_proof`：1 passed。
- `.venv/bin/pytest -q tests/test_model_core_optimization_governance_agent.py tests/test_agent50_core_interface_integration.py tests/test_stage_boundary_external_action_board.py`：76 passed。
- `.venv/bin/pytest -q`：660 passed。
- `.venv/bin/python tools/build_project_codegraph.py`：通过，CodeGraph fallback 为 409 files、5462 nodes、8615 edges。

## 2026-06-22 R8u-163：Manifest Grey-Box Missing Table Contract

背景：

- R8u-162 已让 grey-box gate 与 core interface 暴露五张缺失表。
- 但 `deliverables/manifest.json` 仍只暴露 `highest_priority_gap_type/table`，只读 manifest 的后续 agent 无法直接知道缺表数量、缺表清单和 source env var。
- 当前处于外部真实包等待阶段，因此本轮只压实 manifest 入口，不新增模型能力，不伪造 field 数据。

TDD 红灯：

- 更新 `tests/test_agent50_core_interface_integration.py::test_manifest_exposes_core_interface_grey_box_submission_readiness_summary`。
- 新断言要求 manifest 三层字段与 `grey_box_submission_readiness_gate.json` 对齐：
  - `latest_grey_box_submission_readiness_missing_table_count`
  - `latest_grey_box_submission_readiness_missing_tables`
  - `latest_grey_box_submission_readiness_source_env_var`
  - `latest_agent50_grey_box_submission_readiness_missing_table_count`
  - `latest_agent50_grey_box_submission_readiness_missing_tables`
  - `latest_agent50_grey_box_submission_readiness_source_env_var`
  - `latest_core_interface_consolidation_grey_box_submission_missing_table_count`
  - `latest_core_interface_consolidation_grey_box_submission_missing_tables`
  - `latest_core_interface_consolidation_grey_box_submission_source_env_var`
- 红灯结果：`KeyError: latest_grey_box_submission_readiness_missing_table_count`，符合预期。

实现：

- 更新 `experiments/run_grey_box_calibration_package_preflight.py`：
  - grey-box runner 写入原始 gate 层的 missing table count/list/source env var。
- 更新 `experiments/run_core_interface_consolidation.py`：
  - 独立 core interface runner 写入 core-interface 层的 missing table count/list/source env var。
- 更新 `experiments/run_agent50_model_core_governance.py`：
  - Agent50 manifest 写入 `latest_agent50_grey_box_submission_readiness_*` 三个字段。
  - Agent50 刷新 core interface 后写入 `latest_core_interface_consolidation_grey_box_submission_*` 三个字段。

当前结果：

- `deliverables/manifest.json` 已直接暴露：
  - `latest_grey_box_submission_readiness_missing_table_count=5`
  - `latest_grey_box_submission_readiness_missing_tables=[batch_inlet_outlet_lab, hydraulic_rtd_or_tracer, oxidant_dose_residual_log, catalyst_age_regeneration_log, byproduct_panel]`
  - `latest_grey_box_submission_readiness_source_env_var=GREY_BOX_CALIBRATION_PACKAGE_DIR`
  - Agent50 和 core-interface 两组同名摘要也同步一致。

边界：

- R8u-163 只增强 manifest 入口的工程可执行性和可验证性。
- 不改变 `readiness_score=0.143`，不生成 field evidence，不证明灰箱机理，不恢复模型链，不写 actuator/release gate。

验证：

- `.venv/bin/pytest -q tests/test_agent50_core_interface_integration.py::test_manifest_exposes_core_interface_grey_box_submission_readiness_summary`：1 passed。
- `.venv/bin/pytest -q tests/test_agent50_core_interface_integration.py tests/test_grey_box_calibration_package.py tests/test_core_interface_consolidation.py tests/test_deliverable_organization_agent.py tests/test_model_core_optimization_governance_agent.py`：91 passed。
- `.venv/bin/pytest -q`：627 passed。
- `.venv/bin/python tools/build_project_codegraph.py`：通过，CodeGraph fallback 为 404 files、5309 nodes、8431 edges。

## 2026-06-22 R8u-162：Grey-Box Missing Package Gap Specificity

背景：

- R8u-161 已把 grey-box submission readiness gate 回接到 core interface。
- 当前阶段仍是外部真实包等待态，继续新增内部 synthetic 模块不符合阶段门。
- 但默认无 `GREY_BOX_CALIBRATION_PACKAGE_DIR` 时，`highest_priority_gap.table` 为空，导致 gate/manifest/core facade 不能精确表达“哪一组表缺失”。

实现：

- 更新 `src/water_ai/grey_box_calibration_package.py`：
  - `_highest_priority_submission_gap()` 在 `external_package_supplied=False` 时返回：
    - `table=all_required_tables`
    - `missing_table_count=5`
    - `missing_tables=[batch_inlet_outlet_lab, hydraulic_rtd_or_tracer, oxidant_dose_residual_log, catalyst_age_regeneration_log, byproduct_panel]`
    - `source_env_var=GREY_BOX_CALIBRATION_PACKAGE_DIR`
  - `grey_box_submission_readiness_gate_report_md()` 显示 `missing_table_count` 和 `missing_tables`。
- 更新 `src/water_ai/core_interface_consolidation.py`：
  - `_grey_box_submission_readiness_projection()` 新增 `submission_missing_table_count`、`submission_missing_tables` 和 `submission_source_env_var`。
  - core interface Markdown 的 submission readiness 单元显示 `missing_tables=5`。
- 更新测试：
  - `tests/test_grey_box_calibration_package.py` 先用 RED 测试锁定 missing-package gap 必须指向 all required tables。
  - `tests/test_core_interface_consolidation.py` 锁定 core facade 必须投影缺表数量、清单和 source env var。

当前结果：

- `outputs/grey_box_calibration_package/grey_box_submission_readiness_gate.json`：
  - `highest_priority_gap.gap_type=missing_external_package`
  - `highest_priority_gap.table=all_required_tables`
  - `highest_priority_gap.missing_table_count=5`
  - `highest_priority_gap.missing_tables` 覆盖五张灰箱校准表。
- `outputs/model_core_governance/core_interface_consolidation.json`：
  - `submission_highest_priority_gap_table=all_required_tables`
  - `submission_missing_table_count=5`
  - `submission_source_env_var=GREY_BOX_CALIBRATION_PACKAGE_DIR`
- `deliverables/manifest.json`：
  - `latest_grey_box_submission_readiness_highest_priority_gap_table=all_required_tables`
  - `latest_core_interface_consolidation_grey_box_submission_highest_priority_gap_table=all_required_tables`

边界：

- R8u-162 是证据边界/外部提交可执行性修复，不是新模型能力。
- `readiness_score` 仍为 `0.143`，仍等待真实五表 field package。
- 不生成 field evidence，不证明灰箱机理，不恢复模型链，不写 actuator/release gate。

验证：

- `.venv/bin/pytest -q tests/test_grey_box_calibration_package.py tests/test_core_interface_consolidation.py tests/test_agent50_core_interface_integration.py tests/test_deliverable_organization_agent.py tests/test_model_core_optimization_governance_agent.py`：91 passed。
- `.venv/bin/pytest -q`：627 passed。
- `.venv/bin/python tools/build_project_codegraph.py`：通过，CodeGraph fallback 为 404 files、5309 nodes、8431 edges。

## 2026-06-22 R8u-161：Core Interface 消费 Grey-Box Submission Readiness Gate

背景：

- R8u-160 已生成 `grey_box_submission_readiness_gate.json`，能计算灰箱校准包的提交成熟度、最高缺口和 Agent53 提交条件。
- Agent50 已能读取该 gate，但核心接口 facade 若不投影这些字段，就会出现“Agent50 可见、core interface 不可见”的断裂。
- 用户要求开启子代理协同，本轮按分工让子代理只读审计 core facade、Agent50 runner 和测试/产物消费证明，主 agent 负责实现和回归。

实现：

- 更新 `src/water_ai/core_interface_consolidation.py`：
  - `build_core_interface_consolidation()` 新增可选 `grey_box_submission_readiness_gate` 参数。
  - `external_package_lifecycle` 的 `grey_box_calibration` row 新增 `submission_readiness_gate_id/status/score`、`submission_highest_priority_gap_type/table`、`can_submit_to_agent53_field_calibration`、`can_submit_to_agent53_field_candidate`、`submission_gate_can_generate_field_evidence`、`submission_gate_can_write_to_actuator`、`submission_gate_can_write_to_release_gate`。
  - Markdown report 的 external package lifecycle 表新增 `submission readiness` 列。
- 更新 `experiments/run_core_interface_consolidation.py`：
  - 读取 `outputs/grey_box_calibration_package/grey_box_submission_readiness_gate.json`。
  - 传入 core interface builder。
  - 在 manifest 中写入 `latest_core_interface_consolidation_grey_box_submission_*` 摘要。
- 更新 `experiments/run_agent50_model_core_governance.py`：
  - Agent50 自动刷新 core interface 时传入同一个 grey-box submission readiness gate。
  - Agent50 写 manifest 时同步暴露 core-interface 层的灰箱提交成熟度摘要。
- 更新 `tests/test_core_interface_consolidation.py` 与 `tests/test_agent50_core_interface_integration.py`：
  - 先用 RED 测试确认 builder 不接受 gate 参数。
  - 增加 core lifecycle row 投影字段测试。
  - 增加 core artifact 与 gate artifact 对齐测试。
  - 增加 Agent50 payload 同时包含原始 gate 与 core projection 的只读测试。
  - 增加 manifest 摘要字段与 gate artifact 对齐测试。

当前结果：

- `outputs/model_core_governance/core_interface_consolidation.json` 的 `grey_box_calibration` lifecycle row 已显示：
  - `submission_readiness_gate_status=grey_box_submission_readiness_waiting_for_external_package`
  - `submission_readiness_score=0.143`
  - `submission_highest_priority_gap_type=missing_external_package`
  - `can_submit_to_agent53_field_calibration=False`
  - `can_submit_to_agent53_field_candidate=False`
  - no-write / no-field-evidence 边界均为 False。
- `deliverables/model_core_optimization/core_interface_consolidation.md` 的 lifecycle 表已显示 `grey_box_submission_readiness_waiting_for_external_package / 0.143`。
- `deliverables/manifest.json` 已新增 `latest_core_interface_consolidation_grey_box_submission_readiness_*` 和 `latest_core_interface_consolidation_can_submit_to_agent53_*` 字段。

边界：

- R8u-161 只是接口回接和消费证明，不生成真实 field evidence。
- 当前外部包仍缺失，`GREY_BOX_CALIBRATION_PACKAGE_DIR` 五表真实包仍是最高外部动作。
- 该轮不证明灰箱机理有效，不恢复模型链，不放松 Agent49 guardrail，不写 actuator/release gate。

验证：

- `.venv/bin/python -m py_compile src/water_ai/core_interface_consolidation.py experiments/run_core_interface_consolidation.py experiments/run_agent50_model_core_governance.py`：通过。
- `.venv/bin/pytest -q tests/test_agent50_core_interface_integration.py tests/test_core_interface_consolidation.py tests/test_grey_box_calibration_package.py`：25 passed。
- `.venv/bin/pytest -q tests/test_agent50_core_interface_integration.py tests/test_core_interface_consolidation.py tests/test_grey_box_calibration_package.py tests/test_deliverable_organization_agent.py tests/test_model_core_optimization_governance_agent.py`：91 passed。
- `.venv/bin/pytest -q`：627 passed。
- `.venv/bin/python tools/build_project_codegraph.py`：通过，CodeGraph fallback 刷新为 404 files、5309 nodes、8431 edges。

## 2026-06-22 R8u-160：Grey-Box Submission Readiness Gate

目标：

- 承接 R8u159：Agent50 已消费 `core_interface_consolidation`，最高外部证据动作仍是 `GREY_BOX_CALIBRATION_PACKAGE_DIR`。
- 本轮不伪造 field 数据，不生成 synthetic 结论，不新增线性 agent。
- 把灰箱校准真实包入口从“preflight + summary + collection work order”进一步压成一个可计算提交成熟度 gate：能量化当前包距离 Agent53 field calibration 还差多少、最高缺口是什么、是否可提交到 Agent53，以及哪些 no-write 边界必须保持。

TDD 红灯：

- 更新 `tests/test_grey_box_calibration_package.py`，新增 4 个测试：
  - 无外部包时 gate 必须 `waiting_for_external_package`，`readiness_score=0.143`，只能给 no-write boundary 基础分。
  - 模板行/非 field 行必须 blocked，并把最高缺口指向需要替换模板行的表。
  - 结构可通过但残差超阈值时，允许进入 Agent53 field calibration，但不能成为 Agent53 field candidate，`readiness_score=0.95`。
  - 残差也通过时，进入 Agent53 field candidate，`readiness_score=1.0`。
- 红灯结果：`ImportError: cannot import name 'build_grey_box_submission_readiness_gate'`，符合预期。

实现：

- 更新 `src/water_ai/grey_box_calibration_package.py`：
  - 新增 `SUBMISSION_READINESS_GATE_ID = R8u160_grey_box_submission_readiness_gate`。
  - 新增 `build_grey_box_submission_readiness_gate()`。
  - 新增 `grey_box_submission_readiness_gate_report_md()`。
  - 新增评分组件：`source_package_present`、`schema_completeness`、`field_origin_integrity`、`matched_batch_coverage`、`signal_validity_coverage`、`agent53_summary_readiness`、`residual_threshold_readiness`、`no_write_boundary_integrity`、`submitted_table_presence`。
  - 新增 `highest_priority_gap`，按 missing package、missing schema、template/non-field rows、valid rows deficit、batch alignment/signal audit 的顺序定位最高缺口。
  - 继续保持 `can_generate_field_evidence=False`、`can_resume_model_chain=False`、`can_write_to_actuator=False`、`can_write_to_release_gate=False`、`can_emit_field_supported_claim=False`。
- 更新 `experiments/run_grey_box_calibration_package_preflight.py`：
  - 生成 `outputs/grey_box_calibration_package/grey_box_submission_readiness_gate.json`。
  - 生成 `deliverables/model_core_optimization/grey_box_submission_readiness_gate.md`。
  - 回写 manifest 的 `latest_grey_box_submission_readiness_*` 字段。
- 更新 `experiments/run_agent50_model_core_governance.py`：
  - 读取 `GREY_BOX_SUBMISSION_READINESS_GATE_PATH`。
  - 将 gate 加入 Agent50 generated files、Markdown report、JSON payload 和 manifest。
  - 将 current work item 更新为 `r8u160_grey_box_submission_readiness_gate`。
  - 更新 manifest `next_stage`，说明 R8u160 已把灰箱真实包入口推进为可计算提交成熟度 gate。
- 更新 `tests/test_agent50_core_interface_integration.py` 和 `tests/test_deliverable_organization_agent.py`：
  - 防止 grey-box submission readiness gate 再次脱离 Agent50 或 deliverable organization。

当前结果：

- 默认未设置 `GREY_BOX_CALIBRATION_PACKAGE_DIR` 时：
  - `gate_status=grey_box_submission_readiness_waiting_for_external_package`
  - `readiness_score=0.143`
  - `highest_priority_gap=missing_external_package`
  - `can_submit_to_agent53_field_calibration=False`
  - `can_submit_to_agent53_field_candidate=False`
  - `can_generate_field_evidence=False`
  - `can_write_to_actuator=False`
  - `can_write_to_release_gate=False`
- Agent50 report 已显示：
  - `grey_box_submission_readiness_gate_status=grey_box_submission_readiness_waiting_for_external_package`
  - `grey_box_submission_readiness_score=0.143`
  - `grey_box_submission_readiness_highest_priority_gap=missing_external_package`

验证：

- `.venv/bin/pytest -q tests/test_grey_box_calibration_package.py`：13 passed。
- `.venv/bin/python -m py_compile src/water_ai/grey_box_calibration_package.py experiments/run_grey_box_calibration_package_preflight.py experiments/run_agent50_model_core_governance.py tests/test_grey_box_calibration_package.py tests/test_agent50_core_interface_integration.py`：通过。
- `.venv/bin/pytest -q tests/test_grey_box_calibration_package.py tests/test_agent50_core_interface_integration.py`：16 passed。
- `.venv/bin/python experiments/run_grey_box_calibration_package_preflight.py`：通过，生成 preflight、summary、collection work order 和 submission readiness gate。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：通过，Agent50 已消费 R8u160 gate。
- `.venv/bin/pytest -q tests/test_grey_box_calibration_package.py tests/test_agent50_core_interface_integration.py tests/test_deliverable_organization_agent.py tests/test_external_package_readiness_board.py tests/test_core_interface_consolidation.py tests/test_model_core_optimization_governance_agent.py`：96 passed。
- `.venv/bin/pytest -q`：623 passed。
- `.venv/bin/python tools/build_project_codegraph.py`：通过，CodeGraph 刷新为 404 files、5301 nodes、8422 edges。

边界：

- R8u160 只是提交成熟度 gate，不是 field validation。
- 它能告诉外部真实包离 Agent53 field calibration 还差什么，但不能生成真实数据、不能证明机理、不能恢复模型链、不能写 actuator、不能写 release gate、不能输出 field-supported claim。
- 若没有真实 `GREY_BOX_CALIBRATION_PACKAGE_DIR`，下一步不应继续内部 synthetic 扩张；应提交真实五表包，或在已有真实 catalyst 记录时走 focused catalyst response 次级补证路径。

## 2026-06-22 R8u-159：Agent50 Consumption of Core Interface Consolidation Facade

目标：

- 承接用户要求：开启子代理，让代码审查、产物一致性审查和下一步边际价值判断并行推进。
- 不新增线性业务 agent，不继续做流程图或展示层，而是检查 R8u158 `core_interface_consolidation` 是否真的进入 Agent50 主治理链。
- 把 R8u158 从“单独 facade 产物”升级为“Agent50 每次治理运行自动刷新、自动消费、自动写入 manifest 的核心接口入口”。

子代理反馈：

- Nash 审查代码接入：`core_interface_consolidation` 已在 Agent50 runner 中构建、写盘，并进入 report、payload 和 manifest；三个 helper 的签名与调用一致，未发现新增 NameError/KeyError 风险。建议补契约型测试，防止后续 schema 漂移。
- Leibniz 审查产物一致性：行为上已接入，但文档没有 R8u159 版本锚点，manifest 也缺少 `consumed`、`refresh_status`、`refreshed_by_runner` 等显式字段。建议保持 R8u158 作为 facade 本体 ID，把 R8u159 定义为 Agent50 消费/刷新集成层。
- Singer 审查全局边际价值：下一轮最高价值不是新增 Agent62 或继续调 synthetic replay，而是优先提交 `GREY_BOX_CALIBRATION_PACKAGE_DIR` 灰箱校准真实包；`catalyst_activity` focused field response 排第二，Agent49/52 replay 排第三，Agent48 布点和 agent 链条压缩暂不应继续内部扩张。

实现：

- 更新 `experiments/run_agent50_model_core_governance.py`：
  - 导入并调用 `build_core_interface_consolidation()` 与 `core_interface_consolidation_report_md()`。
  - 在 Agent50 主运行中构建 `core_interface_consolidation`。
  - 写入 `outputs/model_core_governance/core_interface_consolidation.json`。
  - 写入 `deliverables/model_core_optimization/core_interface_consolidation.md`。
  - 将 `core_interface_consolidation` 加入 Agent50 report Markdown、JSON payload 和 `generated_files`。
  - 在 manifest 写入 `latest_agent50_core_interface_consolidation_*` 与通用 `latest_core_interface_consolidation_*` 字段。
  - 新增 `latest_agent50_core_interface_consolidation_consumed=True`、`latest_agent50_core_interface_consolidation_refresh_status=agent50_runner_refreshed_current_facade`、`latest_agent50_core_interface_consolidation_refreshed_by_runner=experiments/run_agent50_model_core_governance.py`。
  - 更新 `next_stage` 叙述：说明 R8u159 已让 Agent50 自动消费 facade，core interface 当前最高外部证据动作为 `GREY_BOX_CALIBRATION_PACKAGE_DIR`，同时保留 Agent50 推荐队列中的 catalyst focused handoff 作为次级补证路径。
- 新增 `tests/test_agent50_core_interface_integration.py`：
  - 静态保护 Agent50 runner 必须构建、写入、报告、payload、manifest 消费 core interface consolidation。
  - 保护 `consumed_by_agent50`、`refresh_status`、`top_external_action_env_var` 等 R8u159 状态字段。
- 更新 `tests/test_deliverable_organization_agent.py`：
  - 将 `core_interface_consolidation.json` 与 `core_interface_consolidation.md` 纳入 model_core_optimization_governance artifact index。
  - 对应 governance package artifact count 从 10 更新到 12。

当前结果：

- Agent50 report 已输出：
  - `core_interface_consolidation_id=R8u158_core_interface_consolidation_facade`
  - `core_interface_consolidation_consumed_by_agent50=True`
  - `core_interface_consolidation_refresh_status=agent50_runner_refreshed_current_facade`
  - `core_interface_consolidation_top_external_action_env_var=GREY_BOX_CALIBRATION_PACKAGE_DIR`
  - `core_interface_consolidation_new_agent_recommendation=do_not_add_linear_agent`
- manifest 已输出：
  - `latest_agent50_core_interface_consolidation_consumed=true`
  - `latest_agent50_core_interface_consolidation_refresh_status=agent50_runner_refreshed_current_facade`
  - `latest_agent50_core_interface_consolidation_refreshed_by_runner=experiments/run_agent50_model_core_governance.py`
  - `latest_core_interface_consolidation_refresh_status=agent50_runner_refreshed_current_facade`
- R8u158 facade 本体 ID 保持不变；R8u159 只表示 Agent50 消费和刷新该 facade 的集成层。

验证：

- `.venv/bin/python -m py_compile experiments/run_agent50_model_core_governance.py tests/test_agent50_core_interface_integration.py`：通过。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：通过，Agent50 report、payload、manifest 与 core interface JSON/Markdown 已重写。
- `.venv/bin/pytest -q tests/test_agent50_core_interface_integration.py tests/test_core_interface_consolidation.py tests/test_deliverable_organization_agent.py tests/test_external_package_readiness_board.py tests/test_grey_box_calibration_package.py tests/test_field_control_replay_package.py tests/test_sparse_topology_installability_package.py tests/test_sensor_network_sparse_placement_agent.py tests/test_model_core_optimization_governance_agent.py`：113 passed。
- `.venv/bin/pytest -q`：618 passed。
- `.venv/bin/python tools/build_project_codegraph.py`：通过，CodeGraph 刷新为 403 files、5280 nodes、8395 edges。

边界：

- R8u159 是治理主链回接，不是新的现场证据、不恢复模型链、不放松 Agent49 guardrail、不写 actuator/release gate。
- Agent50 推荐队列仍可能保留 catalyst focused handoff；但 core interface facade 与 external package acquisition gate 均指向 `GREY_BOX_CALIBRATION_PACKAGE_DIR` 作为当前最高外部证据动作。
- 下一步若没有真实外部包，不应继续内部扩张；应优先补灰箱校准五表真实包，或在已有 catalyst 真实记录时补 focused catalyst response。

## 2026-06-22 R8u-158：Core Interface Consolidation Facade

目标：

- 承接用户要求：开启子代理，按组分分工、相互反馈，并让主控以边际价值决定下一步。
- 本轮不新增线性业务 agent，不扩大展示层，不把 synthetic/interface 结果写成 field conclusion。
- 把三个子代理的只读审计反馈压成一个可机读 facade：外部包生命周期、Agent48-54 布点-软传感耦合 benchmark、Agent49-52 控制 replay crosswalk。

子代理反馈：

- Mendel 审计整体 agent 链条：当前不适合继续按 1-61 线性 agent 增长，应按七层骨架和少数 facade/schema 管理；R8u154-157 可合并为外部包生命周期。
- Euclid 审计 Agent48：当前最大缺口不是再加布点启发式，而是把 Agent48 六类策略、missingness stress、软传感 schema readiness、`catalyst_activity` blocker 和 pressure/headloss gap 放进同一张可比较评分表。
- Gauss 审计 Agent49/52：Agent49 已是多设施候选控制层，不是现场在线 RL；最小增益是补 `FIELD_CONTROL_REPLAY_PACKAGE_DIR` 五表到 Agent52 replay schema 的 crosswalk，并保持 release/actuator no-write 边界。

TDD 红灯：

- 新增 `tests/test_core_interface_consolidation.py`。
- 红灯预期为缺少 `water_ai.core_interface_consolidation`。
- 目标断言包括：三类 facade 必须同时存在；external lifecycle 必须保留 waiting/no-write；Agent48 benchmark 必须覆盖至少 6 类策略并保留 `catalyst_activity` blocker；field control replay crosswalk 必须映射五张表到 Agent52 schema；报告必须明确不能生成 field evidence。

实现：

- 新增 `src/water_ai/core_interface_consolidation.py`：
  - `build_core_interface_consolidation()`。
  - `core_interface_consolidation_report_md()`。
  - `external_package_lifecycle`：统一灰箱校准、field control replay、sparse topology/installability 三类外部包生命周期。
  - `sparse_layout_soft_sensor_coupling_benchmark`：对 Agent48 strategy candidates 计算 `layout_coupling_score`、`masked_state_support_mean`、`catalyst_activity_support`、`missingness_robustness_score`、`pressure_headloss_gap_penalty`、`soft_sensor_schema_readiness`。
  - `field_control_replay_crosswalk`：将五张真实控制 replay 表映射为 Agent52 state-action-reward replay 所需字段和 release gate requirements。
- 新增 `experiments/run_core_interface_consolidation.py`：
  - 读取 `sparse_placement_metrics.json`、Agent52 replay metrics、R8u157 collection work order、field control replay preflight、sparse topology preflight 和 external package acquisition maturity gate。
  - 生成 `outputs/model_core_governance/core_interface_consolidation.json`。
  - 生成 `deliverables/model_core_optimization/core_interface_consolidation.md`。
  - 回写 manifest 的 `latest_core_interface_consolidation_*` 字段。

当前结果：

- `consolidation_id=R8u158_core_interface_consolidation_facade`。
- `facade_count=3`。
- `top_external_action_env_var=GREY_BOX_CALIBRATION_PACKAGE_DIR`。
- `top_internal_action=maintain_core_interface_facades_and_refresh_only_when field packages, Agent48 layout metrics or Agent52 replay schema change`。
- `new_agent_recommendation=do_not_add_linear_agent`。
- Agent48 coupling benchmark 当前排序：
  - `reconstruction_qr_proxy`：0.549。
  - `classification_sspoc_proxy`：0.545。
  - `greedy_marginal`：0.533。
- 所有 layout rows 都保持：
  - `can_finalize_field_deployment=False`
  - `can_relax_agent49=False`
  - `can_write_to_actuator=False`
  - `can_write_to_release_gate=False`
- field control replay crosswalk 当前状态：
  - `field_control_replay_crosswalk_ready_waiting_for_FIELD_CONTROL_REPLAY_PACKAGE_DIR`。

验证：

- `.venv/bin/pytest -q tests/test_core_interface_consolidation.py`：5 passed。
- `.venv/bin/python -m py_compile src/water_ai/core_interface_consolidation.py experiments/run_core_interface_consolidation.py`：通过。
- `.venv/bin/pytest -q tests/test_core_interface_consolidation.py tests/test_field_control_replay_package.py tests/test_sensor_network_sparse_placement_agent.py`：22 passed。
- `.venv/bin/pytest -q tests/test_core_interface_consolidation.py tests/test_external_package_readiness_board.py tests/test_grey_box_calibration_package.py tests/test_field_control_replay_package.py tests/test_sparse_topology_installability_package.py tests/test_sensor_network_sparse_placement_agent.py`：45 passed。
- `.venv/bin/python experiments/run_core_interface_consolidation.py`：通过，已生成 JSON/Markdown 并更新 manifest。
- `.venv/bin/pytest -q`：616 passed。
- `.venv/bin/python tools/build_project_codegraph.py`：通过，CodeGraph 刷新为 402 files、5277 nodes、8384 edges。

边界：

- R8u158 是接口收束和 synthetic/interface benchmark，不是 field validation。
- 不生成 field evidence，不恢复模型链，不放松 Agent49 catalyst guardrail，不写 actuator，不写 release gate。
- 后续只有真实 field package、Agent48 layout metrics 或 Agent52 replay schema 发生变化时才刷新该 facade；不应为了增加 agent 数量继续扩张。

## 2026-06-22 R8u-157：Grey-Box Calibration Collection Work Order

目标：

- 承接 R8u156：acquisition maturity gate 显示 `acquisition_maturity_score=0.85`，但 `field_package_ready_rate=0.0`。
- 本轮不新增 synthetic 模型能力，不修改 Agent48/49 控制逻辑。
- 把当前最高优先级真实包 `GREY_BOX_CALIBRATION_PACKAGE_DIR` 从“请填写模板”进一步压成表级采集工单：每张表填什么、共同 `batch_id` 怎么对齐、怎么拒收模板行、运行哪个命令、不能写什么。

TDD 红灯：

- 先在 `tests/test_grey_box_calibration_package.py` 中新增 4 个测试。
- 红灯预期为缺少 `build_grey_box_calibration_collection_work_order()` 与 `grey_box_calibration_collection_work_order_report_md()`。
- 目标断言包括：等待外部包时输出 5 个 table work items；模板行会进入 repair 状态；ready 包可路由到 Agent53 field calibration；报告必须包含 `data_origin=field`、`GREY_BOX_CALIBRATION_PACKAGE_DIR` 和 `cannot resume the model chain`。

实现：

- 更新 `src/water_ai/grey_box_calibration_package.py`：
  - 新增 `COLLECTION_WORK_ORDER_ID = R8u157_grey_box_calibration_collection_work_order`。
  - 新增 `build_grey_box_calibration_collection_work_order(preflight=..., field_calibration_summary=..., template_dir=..., validation_command=...)`。
  - 新增 `grey_box_calibration_collection_work_order_report_md(work_order)`。
  - 新增表级 helper：`_collection_table_work_item()`、`_collection_table_status()`、`_signal_audit_for_table()`、`_collection_work_order_status()`、`_collection_next_operator_action()`。
  - 工单状态区分：
    - `grey_box_calibration_collection_work_order_waiting_for_external_package`
    - `grey_box_calibration_collection_work_order_blocked_by_preflight_repair`
    - `grey_box_calibration_collection_work_order_ready_for_agent53_field_calibration`
- 更新 `experiments/run_grey_box_calibration_package_preflight.py`：
  - 同步生成 `outputs/grey_box_calibration_package/grey_box_calibration_collection_work_order.json`。
  - 同步生成 `deliverables/model_core_optimization/grey_box_calibration_collection_work_order.md`。
  - 回写 manifest 的 `latest_grey_box_calibration_collection_work_order_*` 字段。
- 更新 `experiments/run_agent50_model_core_governance.py`：
  - 将 R8u157 工单和报告加入 Agent50 `generated_files` 与 JSON payload 路径。

当前结果：

- `outputs/grey_box_calibration_package/grey_box_calibration_collection_work_order.json` 显示：
  - `work_order_id=R8u157_grey_box_calibration_collection_work_order`
  - `work_order_status=grey_box_calibration_collection_work_order_waiting_for_external_package`
  - `source_env_var=GREY_BOX_CALIBRATION_PACKAGE_DIR`
  - `template_dir=outputs/grey_box_calibration_package/grey_box_calibration_package_template`
  - `validation_command=.venv/bin/python experiments/run_grey_box_calibration_package_preflight.py`
  - `minimum_matched_batch_count=3`
  - `matched_batch_count=0`
  - `table_work_item_count=5`
  - `field_package_ready_for_agent53=False`
  - `agent53_field_candidate_ready=False`
- 五个 table work items 分别为：
  - `batch_inlet_outlet_lab`
  - `hydraulic_rtd_or_tracer`
  - `oxidant_dose_residual_log`
  - `catalyst_age_regeneration_log`
  - `byproduct_panel`
- 每个 table work item 都包含模板 CSV、必填列、`join_key=batch_id`、`minimum_rows=3`、`required_data_origin=field`、accepted QA flags、当前有效行数、模板标记数、non-field 行数和当前状态。

验证：

- `.venv/bin/python -m py_compile src/water_ai/grey_box_calibration_package.py experiments/run_grey_box_calibration_package_preflight.py experiments/run_agent50_model_core_governance.py`：通过。
- `.venv/bin/pytest -q tests/test_grey_box_calibration_package.py`：9 passed。
- `.venv/bin/python experiments/run_grey_box_calibration_package_preflight.py`：通过，生成 preflight、field calibration summary 和 collection work order。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：通过，Agent50 generated files 已包含 R8u157 工单。
- `.venv/bin/pytest -q tests/test_grey_box_calibration_package.py tests/test_external_package_readiness_board.py tests/test_new_core_interface_candidate_gate.py tests/test_stage_boundary_external_action_board.py tests/test_model_core_optimization_governance_agent.py`：72 passed。
- `.venv/bin/pytest -q`：611 passed。
- `.venv/bin/python tools/build_project_codegraph.py`：通过，CodeGraph 刷新为 398 files、5234 nodes、8316 edges。

边界：

- R8u157 是 `GREY_BOX_CALIBRATION_PACKAGE_DIR` 的采集/修复工单，不是 field validation。
- 它可以降低 operator 填写真实灰箱校准包的摩擦，但不会自动生成真实行。
- 它不运行 Agent53 field calibration，不证明机理有效，不恢复模型链，不写 actuator 或 release gate，也不能输出 field-supported mechanism claim。

## 2026-06-22 R8u-156：External Package Acquisition Maturity Gate

目标：

- 承接 R8u154/R8u155：五个 new-core-interface 外部真实包已经有 readiness board 和 operator action packet，但仍缺一个可计算阶段门来回答“采集接口是否成熟、是否可以恢复模型链、下一步是继续内部扩张还是等待真实包”。
- 本轮不新增 synthetic 模型能力，不修改 Agent48/49 控制逻辑。
- 把五包队列对齐到全局 goal 的阶段终止条件：接口成熟可以加分，但真实 field package ready rate 为 0 时，不能把它误读成现场证据成熟。

TDD 红灯：

- 先在 `tests/test_external_package_readiness_board.py` 中新增 3 个 acquisition maturity gate 测试。
- 红灯预期为缺少 `build_external_package_acquisition_maturity_gate()`。
- 目标断言包括：waiting queue 时 `field_package_ready_rate=0.0`、三项工程接口覆盖率为 `1.0`、`acquisition_maturity_score=0.85`、`model_chain_resume_ready=False`；blocked preflight 时必须优先修复 blocked candidate；报告必须明确 `cannot resume the model chain`。

实现：

- 更新 `src/water_ai/external_package_readiness_board.py`：
  - 新增 `ACQUISITION_MATURITY_GATE_ID = R8u156_external_package_acquisition_maturity_gate`。
  - 新增 `build_external_package_acquisition_maturity_gate(readiness_board=..., operator_action_packet=...)`。
  - 新增 `external_package_acquisition_maturity_gate_report_md(gate)`。
  - 新增/复用轻量 helper：`_operator_action_contract_coverage()`、`_no_write_boundary_integrity()`、`_acquisition_gate_status()`、`_acquisition_next_stage_decision()`、`_list_of_dicts()`、`_safe_ratio()`。
  - 评分公式为 `0.35*interface_preflight_coverage + 0.25*operator_action_contract_coverage + 0.25*no_write_boundary_integrity + 0.15*field_package_ready_rate - preflight_repair_penalty`。
  - 当前 waiting queue 下的 `0.85` 被定义为 collection-interface maturity，不是 field evidence maturity。
- 更新 `experiments/run_external_package_readiness_board.py`：
  - 同步生成 `outputs/model_core_governance/external_package_acquisition_maturity_gate.json`。
  - 同步生成 `deliverables/model_core_optimization/external_package_acquisition_maturity_gate.md`。
  - 回写 manifest 通用 `latest_external_package_acquisition_*` 字段。
- 更新 `experiments/run_agent50_model_core_governance.py`：
  - Agent50 每次主治理运行时同步构建 acquisition maturity gate。
  - 将 gate 加入 generated files、Agent50 markdown report、Agent50 JSON payload 和 manifest。
  - manifest 新增 `latest_agent50_external_package_acquisition_*` 与通用 `latest_external_package_acquisition_*` 字段。

当前结果：

- `outputs/model_core_governance/external_package_acquisition_maturity_gate.json` 显示：
  - `gate_id=R8u156_external_package_acquisition_maturity_gate`
  - `gate_status=external_package_acquisition_interfaces_ready_waiting_for_field_packages`
  - `package_count=5`
  - `ready_package_count=0`
  - `waiting_package_count=5`
  - `blocked_package_count=0`
  - `unimplemented_package_count=0`
  - `interface_preflight_coverage=1.0`
  - `operator_action_contract_coverage=1.0`
  - `no_write_boundary_integrity=1.0`
  - `field_package_ready_rate=0.0`
  - `acquisition_maturity_score=0.85`
  - `next_stage_decision=collect_external_field_packages_before_downstream_gates`
  - `next_operator_source_env_var=GREY_BOX_CALIBRATION_PACKAGE_DIR`
- `outputs/agent50_model_core_governance/agent50_report.md` 和 `deliverables/manifest.json` 已同时暴露分数、field ready rate、下一阶段动作和 no-write/no-resume 边界。

验证：

- `.venv/bin/python -m py_compile src/water_ai/external_package_readiness_board.py experiments/run_external_package_readiness_board.py experiments/run_agent50_model_core_governance.py`：通过。
- `.venv/bin/pytest -q tests/test_external_package_readiness_board.py`：9 passed。
- `.venv/bin/python experiments/run_external_package_readiness_board.py`：通过，生成 readiness board、operator packet 和 acquisition maturity gate。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：通过，Agent50 generated files 已包含 acquisition maturity gate。
- `.venv/bin/pytest -q tests/test_external_package_readiness_board.py tests/test_new_core_interface_candidate_gate.py tests/test_stage_boundary_external_action_board.py tests/test_model_core_optimization_governance_agent.py`：63 passed。
- `.venv/bin/pytest -q`：607 passed。
- `.venv/bin/python tools/build_project_codegraph.py`：通过，CodeGraph 刷新为 397 files、5210 nodes、8284 edges。

边界：

- R8u156 是外部包采集成熟度阶段门，不是 field validation。
- `acquisition_maturity_score=0.85` 必须与 `field_package_ready_rate=0.0` 同时阅读；它说明采集接口和操作合同成熟，不说明现场包 ready。
- 它不会自动提交任何包，不运行 downstream replay/holdout/calibration。
- 它不生成 field evidence，不恢复模型链，不写 actuator 或 release gate，也不能输出 field-supported claim。

## 2026-06-22 R8u-155：External Package Operator Action Packet

目标：

- 承接 R8u154：readiness board 已经统一五个外部包的 ready/waiting/blocked 状态，但仍偏看板。
- 本轮不新增 synthetic 模型能力，不继续堆内部 agent。
- 把五个真实数据包入口进一步压成 operator-facing action packet：每个包要知道填哪个模板、设置哪个环境变量、跑哪个验证命令、何时拒收、不能写什么。

TDD 红灯：

- 先在 `tests/test_external_package_readiness_board.py` 中新增 3 个测试。
- 第一次运行 `.venv/bin/pytest -q tests/test_external_package_readiness_board.py` 出现 import collection error。
- 调整为模块级导入后，第二次运行出现预期红灯：`AttributeError: module 'water_ai.external_package_readiness_board' has no attribute 'build_external_package_operator_action_packet'`。

实现：

- 更新 `src/water_ai/external_package_readiness_board.py`：
  - 新增 `OPERATOR_PACKET_ID = R8u155_external_package_operator_action_packet`。
  - 新增 `build_external_package_operator_action_packet(readiness_board=...)`。
  - 新增 `external_package_operator_action_packet_report_md(packet)`。
  - 新增 `_operator_action()`、`_operator_packet_status()`、`_operator_commands()` 等轻量 helper。
  - 将 package rows 转成有序 operator actions。
  - action 状态区分：
    - `collect_external_package`
    - `repair_preflight_blocker`
    - `ready_for_downstream_consumer`
  - packet 状态区分：
    - `external_package_operator_packet_waiting_for_field_packages`
    - `external_package_operator_packet_blocked_by_preflight_repair`
    - `external_package_operator_packet_ready_for_downstream_consumers`
    - `external_package_operator_packet_no_external_package_actions`
  - 固定 no-write 边界：不能生成 field evidence，不能恢复模型链，不能写 actuator，不能写 release gate，不能输出 field-supported claim。
- 更新 `experiments/run_external_package_readiness_board.py`：
  - 同步生成 `outputs/model_core_governance/external_package_operator_action_packet.json`。
  - 同步生成 `deliverables/model_core_optimization/external_package_operator_action_packet.md`。
  - 回写 manifest 通用 `latest_external_package_operator_action_packet_*` 字段。
- 更新 `experiments/run_agent50_model_core_governance.py`：
  - Agent50 每次主治理运行时同步构建 external package operator action packet。
  - 将 packet 加入 generated files、Agent50 markdown report、Agent50 JSON payload 和 manifest。
  - manifest 新增 `latest_agent50_external_package_operator_action_packet_*` 与通用 `latest_external_package_operator_action_packet_*` 字段。

当前结果：

- `outputs/model_core_governance/external_package_operator_action_packet.json` 显示：
  - `packet_id=R8u155_external_package_operator_action_packet`
  - `packet_status=external_package_operator_packet_waiting_for_field_packages`
  - `package_count=5`
  - `ready_package_count=0`
  - `waiting_package_count=5`
  - `blocked_package_count=0`
  - `next_operator_candidate_id=NCI1_GREY_BOX_CALIBRATION_PACKAGE`
  - `next_operator_source_env_var=GREY_BOX_CALIBRATION_PACKAGE_DIR`
  - `next_operator_validation_command=.venv/bin/python experiments/run_grey_box_calibration_package_preflight.py`
- `operator_action_sequence` 为：
  - `NCI1_GREY_BOX_CALIBRATION_PACKAGE`
  - `NCI5_FIELD_SUPPORTED_KG_EDGE_PACKAGE`
  - `NCI3_FIELD_CONTROL_REPLAY_PACKAGE`
  - `NCI4_SPARSE_TOPOLOGY_INSTALLABILITY_PACKAGE`
  - `NCI2_FIELD_MISSINGNESS_REPLAY_PACKAGE`
- Agent50 report 现在直接暴露 external package operator packet status、next env var 和 validation command。

验证：

- `.venv/bin/python -m py_compile src/water_ai/external_package_readiness_board.py experiments/run_external_package_readiness_board.py experiments/run_agent50_model_core_governance.py`：通过。
- `.venv/bin/pytest -q tests/test_external_package_readiness_board.py`：6 passed。
- `.venv/bin/python experiments/run_external_package_readiness_board.py`：通过，生成 readiness board 和 operator action packet。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：通过，Agent50 generated files 已包含 operator packet。
- `.venv/bin/pytest -q tests/test_external_package_readiness_board.py tests/test_new_core_interface_candidate_gate.py tests/test_stage_boundary_external_action_board.py tests/test_model_core_optimization_governance_agent.py`：60 passed。
- `.venv/bin/pytest -q`：604 passed。
- `.venv/bin/python tools/build_project_codegraph.py`：通过，CodeGraph 刷新为 396 files、5193 nodes、8262 edges。

边界：

- R8u155 是外部包采集/验证操作包，不是 field validation。
- 它不会自动提交任何包、不会运行 downstream replay/holdout/calibration。
- 它不生成 field evidence，不恢复模型链，不写 actuator 或 release gate。

## 2026-06-22 R8u-154：External Package Readiness Board

目标：

- 承接 R8u153 后的阶段边界复核：五个 new-core-interface 外部包都已有 preflight，但状态分散在各自 runner、report 和 manifest 字段中。
- 不继续堆 synthetic 算法或新增控制策略；先把真实外部包采集状态做成统一、可机读、可汇报的 readiness board。
- 让 operator 和后续 agent 一眼看到：哪个包 ready、哪个包等待外部目录、哪个包被 schema 阻断、下一步该补哪个环境变量，以及这些包是否允许恢复模型链或写执行器/放行门。

实现：

- 新增 `src/water_ai/external_package_readiness_board.py`：
  - 定义 `R8u154_external_package_readiness_board`。
  - 从 `new_core_interface_candidate_gate.candidate_rows` 聚合五个外部包。
  - 输出 `package_summary`：package/ready/waiting/blocked/unimplemented counts、最高优先级候选、下一 operator action 和 no-write flags。
  - 输出 `package_rows`：candidate、task、source env var、system layer、core ability、preflight status/pass、matched unit summary、template/report/preflight paths、validation command、failure boundary。
  - 输出 `collection_groups`：state estimation/grey-box、mechanism evidence KG、control replay、sparse observation layout、soft-sensor missingness。
  - 明确 board 只是 readiness/routing artifact，不验证 field performance，不运行 downstream replay/holdout/calibration，不授权 actuator/release gate。
- 新增 `experiments/run_external_package_readiness_board.py`：
  - 读取 `outputs/model_core_governance/new_core_interface_candidate_gate.json`。
  - 写出 `outputs/model_core_governance/external_package_readiness_board.json`。
  - 写出 `deliverables/model_core_optimization/external_package_readiness_board.md`。
  - 回写 manifest 的通用 `latest_external_package_readiness_board_*` 字段。
- 更新 `experiments/run_agent50_model_core_governance.py`：
  - 引入 `build_external_package_readiness_board()` 与 markdown renderer。
  - 每次 Agent50 主治理运行时同步生成 external package readiness board。
  - 将 board 加入 `generated_files`、Agent50 markdown report、Agent50 JSON payload 和 manifest。
  - manifest 新增 `latest_agent50_external_package_readiness_board_*` 与通用 `latest_external_package_readiness_board_*` 指针和计数。
- 新增 `tests/test_external_package_readiness_board.py`：
  - 验证五个 NCI 包能被统一聚合。
  - 验证 ready/waiting/blocked/unimplemented 计数。
  - 验证 blocked 包优先成为下一 operator 修复对象。
  - 验证报告中暴露 NCI4、NCI2 和 no-write boundary。

当前结果：

- `outputs/model_core_governance/external_package_readiness_board.json` 显示：
  - `package_count=5`
  - `ready_package_count=0`
  - `waiting_package_count=5`
  - `blocked_package_count=0`
  - `unimplemented_package_count=0`
  - `all_candidate_interfaces_have_preflight=True`
  - `next_operator_source_env_var=GREY_BOX_CALIBRATION_PACKAGE_DIR`
  - `can_generate_field_evidence=False`
  - `can_write_to_actuator=False`
  - `can_write_to_release_gate=False`
- 五个 package rows 依次为：
  - `NCI1_GREY_BOX_CALIBRATION_PACKAGE`
  - `NCI5_FIELD_SUPPORTED_KG_EDGE_PACKAGE`
  - `NCI3_FIELD_CONTROL_REPLAY_PACKAGE`
  - `NCI4_SPARSE_TOPOLOGY_INSTALLABILITY_PACKAGE`
  - `NCI2_FIELD_MISSINGNESS_REPLAY_PACKAGE`
- Agent50 report 现在直接显示 external package readiness board 的 package counts、next operator env var、next action 和 no-write boundary。
- 这轮把“所有外部包都已具备接口，但都等待真实 field package”的状态从分散事实升级为统一工程入口。

验证：

- `.venv/bin/python -m py_compile src/water_ai/external_package_readiness_board.py experiments/run_external_package_readiness_board.py experiments/run_agent50_model_core_governance.py`：通过。
- `.venv/bin/pytest -q tests/test_external_package_readiness_board.py`：3 passed。
- `.venv/bin/pytest -q tests/test_external_package_readiness_board.py tests/test_new_core_interface_candidate_gate.py tests/test_stage_boundary_external_action_board.py tests/test_model_core_optimization_governance_agent.py`：57 passed。
- `.venv/bin/python experiments/run_external_package_readiness_board.py`：通过，输出 5 packages、0 ready、5 waiting、0 blocked。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：通过，Agent50 generated files 已包含 external package readiness board。
- `.venv/bin/pytest -q`：601 passed。
- `.venv/bin/python tools/build_project_codegraph.py`：通过，CodeGraph 刷新为 395 files、5174 nodes、8234 edges。

边界：

- R8u154 是外部包 readiness/routing board，不是 field validation。
- 即使某个包 preflight ready，也只能进入对应 downstream consumer；仍不能跳过 replay、holdout、calibration、claim gate 或人工复核。
- 本轮不生成 field evidence，不恢复模型链，不写 actuator 或 release gate。

## 2026-06-22 R8u-153：Field Missingness Replay Package Preflight

目标：

- 承接 R8u152 后继续完成 new-core-interface 队列。
- P4/P6/P1/P3 均已有外部 preflight，剩余 NCI2/P5 是软传感缺测鲁棒性的真实接口缺口。
- 不训练新软传感模型；先定义真实 field missingness replay 包的最低证据契约。

实现：

- 新增 `src/water_ai/field_missingness_replay_package.py`：
  - 定义 `FIELD_MISSINGNESS_REPLAY_PACKAGE_DIR`。
  - 定义五张最小表：`node_modality_time_series`、`availability_mask`、`time_since_last_observed_min`、`sensor_quality_status`、`offline_hidden_state_labels`。
  - 新增 `build_field_missingness_replay_package_template()`。
  - 新增 `write_field_missingness_replay_package_template()`。
  - 新增 `build_field_missingness_replay_package_preflight()`。
  - 检查 field origin、QA、模板标记、必需列、节点-模态时间序列、availability mask、距上次观测时间、传感器质量状态和离线隐藏状态标签。
  - 要求至少 3 个共同 `sample_id` 贯穿五张表。
  - 要求至少 1 个真实 unavailable/missing 样本，防止全 available 数据误充 missingness replay。
- 新增 `experiments/run_field_missingness_replay_preflight.py`：
  - 写出 `outputs/field_missingness_replay_package/field_missingness_replay_package_template/`。
  - 写出 `outputs/field_missingness_replay_package/field_missingness_replay_package_preflight.json`。
  - 写出 `deliverables/model_core_optimization/field_missingness_replay_package_preflight.md`。
  - 回写 manifest。
- 更新 `src/water_ai/new_core_interface_candidate_gate.py`：
  - 新增 `field_missingness_replay_preflight` 输入。
  - `NCI2_FIELD_MISSINGNESS_REPLAY_PACKAGE` 现在消费该 preflight。
  - 新增 `candidate_matched_sample_count`，并把 ready 状态定义为 `interface_preflight_ready_for_agent54_field_missingness_replay`。
- 更新 `experiments/run_new_core_interface_candidate_gate.py` 与 `experiments/run_agent50_model_core_governance.py`：
  - 自动读取 `field_missingness_replay_package_preflight.json`。
  - 将 field missingness replay preflight 纳入 Agent50 generated files。
- 新增/更新测试：
  - field missingness package waiting/template/valid/missing-label/all-available 五类 preflight 测试。
  - new-core candidate gate 在 P5 排第一时能识别 field missingness package ready。

当前结果：

- 默认未设置 `FIELD_MISSINGNESS_REPLAY_PACKAGE_DIR`，因此：
  - `package_status=field_missingness_replay_package_waiting_for_FIELD_MISSINGNESS_REPLAY_PACKAGE_DIR`
  - `package_preflight_pass=False`
  - `matched_sample_count=0`
  - `unavailable_sample_count=0`
  - `next_operator_action=fill_field_missingness_replay_package_template_and_set_FIELD_MISSINGNESS_REPLAY_PACKAGE_DIR`
- `outputs/model_core_governance/new_core_interface_candidate_gate.json`：
  - 五个 new-core-interface 候选现在全部具备对应外部 preflight 或 downstream adapter。
  - `NCI2_FIELD_MISSINGNESS_REPLAY_PACKAGE` 已从 `interface_preflight_not_implemented_yet` 变成 `field_missingness_replay_package_waiting_for_FIELD_MISSINGNESS_REPLAY_PACKAGE_DIR`。
  - 这说明 P5 真实缺测回放接口已定义，等待外部包，而不是继续要求内部 synthetic dropout 扩写。

验证：

- `.venv/bin/python -m py_compile ...`：通过。
- `.venv/bin/pytest -q tests/test_field_missingness_replay_package.py tests/test_new_core_interface_candidate_gate.py`：13 passed。
- `.venv/bin/python experiments/run_field_missingness_replay_preflight.py`：通过。
- `.venv/bin/python experiments/run_new_core_interface_candidate_gate.py`：通过。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：通过。
- `.venv/bin/pytest -q tests/test_field_missingness_replay_package.py tests/test_field_control_replay_package.py tests/test_sparse_topology_installability_package.py tests/test_new_core_interface_candidate_gate.py tests/test_stage_boundary_external_action_board.py tests/test_model_core_optimization_governance_agent.py tests/test_soft_sensor_matrix_coupling_agent.py`：76 passed。
- `.venv/bin/pytest -q`：598 passed。
- `.venv/bin/python tools/build_project_codegraph.py`：通过，CodeGraph 刷新为 391 files、5144 nodes、8144 edges。

边界：

- R8u153 是 field missingness replay package 的 preflight，不是 soft-sensor field performance result。
- 即使 preflight 通过，也只表示可进入 Agent54/soft-sensor missingness holdout consumer；仍需 downstream holdout metrics、interval coverage、calibration/uncertainty 和 release gate。
- 本轮不证明 field soft-sensor accuracy，不恢复模型链，不写 actuator 或 release gate。

## 2026-06-22 R8u-152：Field Control Replay Package Preflight

目标：

- 承接 R8u151 后的低频自我打断评估：P1 外部拓扑/安装包接口已定义，继续在 P1 内部堆算法会缺真实包支撑。
- 转向 P3/NCI3 控制层阻断，把 Agent49/Agent52 从 synthetic control baseline 推向真实 field control replay package 预检。
- 不训练 RL、不推广控制策略；先固定离线回放最低证据契约。

实现：

- 新增 `src/water_ai/field_control_replay_package.py`：
  - 定义 `FIELD_CONTROL_REPLAY_PACKAGE_DIR`。
  - 定义五张最小表：`state_action_next_state_rows`、`reward_component_rows`、`operator_or_expert_action_labels`、`actuator_latency_and_result_rows`、`unsafe_action_or_override_events`。
  - 新增 `build_field_control_replay_package_template()`。
  - 新增 `write_field_control_replay_package_template()`。
  - 新增 `build_field_control_replay_package_preflight()`。
  - 检查 field origin、QA、模板标记、必需列、状态转移、reward 分量、专家动作标签、执行器延迟一致性和 unsafe/override 人工复核记录。
  - 要求至少 3 个共同 `transition_id` 贯穿五张表。
- 新增 `experiments/run_field_control_replay_preflight.py`：
  - 写出 `outputs/field_control_replay_package/field_control_replay_package_template/`。
  - 写出 `outputs/field_control_replay_package/field_control_replay_package_preflight.json`。
  - 写出 `deliverables/model_core_optimization/field_control_replay_package_preflight.md`。
  - 回写 manifest。
- 更新 `src/water_ai/new_core_interface_candidate_gate.py`：
  - 新增 `field_control_replay_preflight` 输入。
  - `NCI3_FIELD_CONTROL_REPLAY_PACKAGE` 现在消费该 preflight。
  - 新增 `candidate_matched_transition_count`，并把 ready 状态定义为 `interface_preflight_ready_for_agent49_field_control_replay`。
- 更新 `experiments/run_new_core_interface_candidate_gate.py` 与 `experiments/run_agent50_model_core_governance.py`：
  - 自动读取 `field_control_replay_package_preflight.json`。
  - 将 field control replay preflight 纳入 Agent50 generated files。
- 新增/更新测试：
  - field control package waiting/template/valid/missing-actuator/invalid-latency 五类 preflight 测试。
  - new-core candidate gate 在 P3 排第一时能识别 field control replay package ready。

当前结果：

- 默认未设置 `FIELD_CONTROL_REPLAY_PACKAGE_DIR`，因此：
  - `package_status=field_control_replay_package_waiting_for_FIELD_CONTROL_REPLAY_PACKAGE_DIR`
  - `package_preflight_pass=False`
  - `matched_transition_count=0`
  - `next_operator_action=fill_field_control_replay_package_template_and_set_FIELD_CONTROL_REPLAY_PACKAGE_DIR`
- `outputs/model_core_governance/new_core_interface_candidate_gate.json`：
  - `NCI1_GREY_BOX_CALIBRATION_PACKAGE` 仍是最高候选，因为当前 Agent50 排名中 P4 仍最高。
  - `NCI3_FIELD_CONTROL_REPLAY_PACKAGE` 已从 `interface_preflight_not_implemented_yet` 变成 `field_control_replay_package_waiting_for_FIELD_CONTROL_REPLAY_PACKAGE_DIR`。
  - 这说明 P3 真实控制回放接口已定义，等待外部包，而不是继续要求内部 synthetic 控制扩写。

验证：

- `.venv/bin/python -m py_compile ...`：通过。
- `.venv/bin/pytest -q tests/test_field_control_replay_package.py tests/test_new_core_interface_candidate_gate.py`：12 passed。
- `.venv/bin/python experiments/run_field_control_replay_preflight.py`：通过。
- `.venv/bin/python experiments/run_new_core_interface_candidate_gate.py`：通过。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：通过。
- `.venv/bin/pytest -q tests/test_field_control_replay_package.py tests/test_sparse_topology_installability_package.py tests/test_new_core_interface_candidate_gate.py tests/test_stage_boundary_external_action_board.py tests/test_model_core_optimization_governance_agent.py tests/test_multi_facility_collaborative_control_agent.py tests/test_multi_facility_replay_evaluation_agent.py`：85 passed。
- `.venv/bin/pytest -q`：592 passed。
- `.venv/bin/python tools/build_project_codegraph.py`：通过，CodeGraph 刷新为 387 files、5088 nodes、8063 edges。

边界：

- R8u152 是 field control replay package 的 preflight，不是离线策略评估结果。
- 即使 preflight 通过，也只表示可进入 Agent49/Agent52 offline replay consumer；仍需 downstream replay metrics、operator review、guardrail arbitration 和 release/actuator gate。
- 本轮不证明控制策略优越，不解除保护性阻断，不恢复模型链，不写 actuator 或 release gate。

## 2026-06-22 R8u-151：Sparse Topology Installability Package Preflight

目标：

- 回到 P1 观测层根基问题：Agent48 稀疏传感布点不能只停留在 synthetic/path prior，必须有真实 topology、节点-模态成本、安装维护约束、水力延迟和隐藏状态标签矩阵入口。
- 承接 R8u147 的 `NCI4_SPARSE_TOPOLOGY_INSTALLABILITY_PACKAGE`，把“可定义接口”的候选合同落成可运行 preflight。
- 不直接重开 Agent48 布点算法；先固定外部包契约，避免在缺真实拓扑与标签时继续堆内部 synthetic 细节。

实现：

- 新增 `src/water_ai/sparse_topology_installability_package.py`：
  - 定义 `SPARSE_TOPOLOGY_INSTALLABILITY_PACKAGE_DIR`。
  - 定义五张最小表：`site_topology_graph`、`candidate_node_modality_costs`、`installability_maintenance_constraints`、`node_hydraulic_delay`、`labeled_state_matrix`。
  - 新增 `build_sparse_topology_installability_package_template()`。
  - 新增 `write_sparse_topology_installability_package_template()`。
  - 新增 `build_sparse_topology_installability_package_preflight()`。
  - 检查 field origin、QA、模板标记、必需列、节点拓扑、节点-模态成本、可安装/供电/通信、水力延迟、维护约束和隐藏状态标签矩阵。
  - 要求至少 3 个共同 `node_id` 贯穿五张表，并且这些节点必须是可安装、可供电、可通信的候选节点。
- 新增 `experiments/run_sparse_topology_installability_preflight.py`：
  - 写出 `outputs/sparse_topology_installability_package/sparse_topology_installability_package_template/`。
  - 写出 `outputs/sparse_topology_installability_package/sparse_topology_installability_package_preflight.json`。
  - 写出 `deliverables/model_core_optimization/sparse_topology_installability_package_preflight.md`。
  - 回写 manifest。
- 更新 `src/water_ai/new_core_interface_candidate_gate.py`：
  - 新增 `sparse_topology_installability_preflight` 输入。
  - `NCI4_SPARSE_TOPOLOGY_INSTALLABILITY_PACKAGE` 现在消费该 preflight。
  - 新增 `candidate_matched_node_count`，并把 ready 状态定义为 `interface_preflight_ready_for_agent48_sparse_layout_holdout`。
- 更新 `experiments/run_new_core_interface_candidate_gate.py` 与 `experiments/run_agent50_model_core_governance.py`：
  - 自动读取 `sparse_topology_installability_package_preflight.json`。
  - 将 sparse topology preflight 纳入 Agent50 generated files。
- 新增/更新测试：
  - sparse topology package waiting/template/valid/missing-label/uninstallable 五类 preflight 测试。
  - new-core candidate gate 在 P1 排第一时能识别 sparse topology package ready。

当前结果：

- 默认未设置 `SPARSE_TOPOLOGY_INSTALLABILITY_PACKAGE_DIR`，因此：
  - `package_status=sparse_topology_installability_package_waiting_for_SPARSE_TOPOLOGY_INSTALLABILITY_PACKAGE_DIR`
  - `package_preflight_pass=False`
  - `matched_node_count=0`
  - `installable_candidate_node_count=0`
  - `next_operator_action=fill_sparse_topology_installability_package_template_and_set_SPARSE_TOPOLOGY_INSTALLABILITY_PACKAGE_DIR`
- `outputs/model_core_governance/new_core_interface_candidate_gate.json`：
  - `NCI1_GREY_BOX_CALIBRATION_PACKAGE` 仍是最高候选，因为当前 Agent50 排名中 P4 仍最高。
  - `NCI4_SPARSE_TOPOLOGY_INSTALLABILITY_PACKAGE` 已从 `interface_preflight_not_implemented_yet` 变成 `sparse_topology_installability_package_waiting_for_SPARSE_TOPOLOGY_INSTALLABILITY_PACKAGE_DIR`。
  - 这说明 P1 真实拓扑/安装/标签接口已定义，等待外部包，而不是继续要求内部 synthetic 扩写。

验证：

- `.venv/bin/python -m py_compile ...`：通过。
- `.venv/bin/pytest -q tests/test_sparse_topology_installability_package.py tests/test_new_core_interface_candidate_gate.py`：11 passed。
- `.venv/bin/python experiments/run_sparse_topology_installability_preflight.py`：通过。
- `.venv/bin/python experiments/run_new_core_interface_candidate_gate.py`：通过。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：通过。
- `.venv/bin/pytest -q tests/test_sparse_topology_installability_package.py tests/test_new_core_interface_candidate_gate.py tests/test_stage_boundary_external_action_board.py tests/test_model_core_optimization_governance_agent.py tests/test_engineering_execution_constraint_agent.py tests/test_multi_facility_replay_evaluation_agent.py`：73 passed。
- `.venv/bin/pytest -q`：586 passed。
- `.venv/bin/python tools/build_project_codegraph.py`：通过，CodeGraph 刷新为 383 files、5032 nodes、7982 edges。

边界：

- R8u151 是 sparse topology/installability package 的 preflight，不是可部署传感布局结果。
- 即使 preflight 通过，也只表示可进入 Agent48 sparse layout holdout consumer；仍需 downstream layout benchmark、field soft-sensor holdout、控制 replay、operator review 和 release gate。
- 本轮不生成 field soft-sensor performance，不证明现场布点有效，不恢复模型链，不写 actuator 或 release gate。

## 2026-06-22 R8u-150：Field-Supported KG Edge Package Preflight

目标：

- 承接 R8u149 后的 new-core-interface 队列。
- P4 灰箱校准接口已具备 preflight 与 Agent53 adapter，继续在 P4 内部扩 synthetic 细节边际价值低。
- 选择第二个高价值候选 `NCI5_FIELD_SUPPORTED_KG_EDGE_PACKAGE`，把 P6 KG reasoning 从 literature/synthetic patch 推向可预检的 field-supported KG edge 外部接口。

实现：

- 新增 `src/water_ai/field_supported_kg_edge_package.py`：
  - 定义 `FIELD_SUPPORTED_KG_EDGE_PACKAGE_DIR`。
  - 定义五张最小表：`pollutant_material_condition_edges`、`source_basis_rows`、`field_supported_edge_rows`、`failure_boundary_annotations`、`claim_action_constraint_links`。
  - 新增 `build_field_supported_kg_edge_package_template()`。
  - 新增 `write_field_supported_kg_edge_package_template()`。
  - 新增 `build_field_supported_kg_edge_package_preflight()`。
  - 检查 field origin、QA、模板标记、必需列、`evidence_stage=field_supported` 或更强、source basis、field support score、失败边界和人工复核约束。
  - 要求至少 3 个共同 `edge_id` 贯穿五张表。
- 新增 `experiments/run_field_supported_kg_edge_preflight.py`：
  - 写出 `outputs/field_supported_kg_edge_package/field_supported_kg_edge_package_template/`。
  - 写出 `outputs/field_supported_kg_edge_package/field_supported_kg_edge_package_preflight.json`。
  - 写出 `deliverables/model_core_optimization/field_supported_kg_edge_package_preflight.md`。
  - 回写 manifest。
- 更新 `src/water_ai/new_core_interface_candidate_gate.py`：
  - 新增 `field_supported_kg_edge_preflight` 输入。
  - `NCI5_FIELD_SUPPORTED_KG_EDGE_PACKAGE` 现在消费该 preflight。
  - 新增通用 `can_route_to_downstream_interface` 与 `downstream_interface_status`，避免把 KG reasoning update 误命名为 calibration。
- 更新 `src/water_ai/stage_boundary_external_action_board.py`：
  - stage board 与 operator runbook 透传通用 downstream interface 状态。
- 更新 `experiments/run_new_core_interface_candidate_gate.py` 与 `experiments/run_agent50_model_core_governance.py`：
  - 自动读取 `field_supported_kg_edge_package_preflight.json`。
  - 写入 generated files、report 和 manifest。
- 新增/更新测试：
  - KG edge package waiting/template/valid/missing-boundary 四类 preflight 测试。
  - new-core candidate gate 在 P6 排第一时能识别 KG edge package ready。
  - stage board 兼容新增通用 downstream interface 字段。

当前结果：

- 默认未设置 `FIELD_SUPPORTED_KG_EDGE_PACKAGE_DIR`，因此：
  - `package_status=field_supported_kg_edge_package_waiting_for_FIELD_SUPPORTED_KG_EDGE_PACKAGE_DIR`
  - `package_preflight_pass=False`
  - `matched_edge_count=0`
  - `next_operator_action=fill_field_supported_kg_edge_package_template_and_set_FIELD_SUPPORTED_KG_EDGE_PACKAGE_DIR`
- `outputs/model_core_governance/new_core_interface_candidate_gate.json`：
  - `NCI1_GREY_BOX_CALIBRATION_PACKAGE` 仍是最高候选，因为 P4 排名最高。
  - `NCI5_FIELD_SUPPORTED_KG_EDGE_PACKAGE` 已从 `interface_preflight_not_implemented_yet` 变成 `field_supported_kg_edge_package_waiting_for_FIELD_SUPPORTED_KG_EDGE_PACKAGE_DIR`。
  - 这说明 P6 现场 KG 边接口已定义，等待外部包，而不是继续要求内部 synthetic 扩写。

验证：

- `.venv/bin/python -m py_compile ...`：通过。
- `.venv/bin/pytest -q tests/test_field_supported_kg_edge_package.py tests/test_new_core_interface_candidate_gate.py tests/test_stage_boundary_external_action_board.py`：15 passed。
- `.venv/bin/python experiments/run_field_supported_kg_edge_preflight.py`：通过。
- `.venv/bin/python experiments/run_new_core_interface_candidate_gate.py`：通过。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：通过。
- `.venv/bin/pytest -q tests/test_field_supported_kg_edge_package.py tests/test_new_core_interface_candidate_gate.py tests/test_stage_boundary_external_action_board.py tests/test_model_core_optimization_governance_agent.py tests/test_knowledge_graph_reasoning_agent.py`：59 passed。
- `.venv/bin/pytest -q`：580 passed。
- `.venv/bin/python tools/build_project_codegraph.py`：`379 files / 4976 nodes / 7901 edges`。

边界：

- R8u150 是 field-supported KG edge package 的 preflight，不是 KG field claim result。
- 即使 preflight 通过，也只表示可进入 KG reasoning 的 field-edge update consumer；仍需 downstream KG reasoning、claim gate、field validation 和人工复核。
- 本轮不生成 site-specific mechanism claim，不生成 claim text，不恢复模型链，不写 actuator 或 release gate。

## 2026-06-22 R8u-149：Grey-Box Field Calibration Summary Adapter

目标：

- 承接 R8u148 的 `GREY_BOX_CALIBRATION_PACKAGE_DIR` preflight。
- 把“外部五表是否结构合格”推进为“能否生成 Agent53 可消费的现场灰箱校准摘要”。
- 区分三层边界：preflight 通过、Agent53 可运行 field calibration、Agent53 field candidate ready；任一层都不能直接写执行器或放行门。

实现：

- 更新 `src/water_ai/grey_box_calibration_package.py`：
  - 新增 `FIELD_CALIBRATION_SUMMARY_ID=R8u149_grey_box_field_calibration_summary`。
  - 新增 `build_grey_box_field_calibration_summary()`。
  - 从共同 `batch_id` 的进出水 lab、HRT/RTD 和副产物 panel 计算可传递指标。
  - 输出 `field_calibration_for_agent53`：`field_physics_coverage`、`max_field_residual`、`max_mass_balance_residual`、`mean_observed_k_per_min`、`mean_observed_removal_fraction`、`max_byproduct_load_fraction_proxy`。
  - 用 `summary_status` 区分 waiting、source reload blocked、computable batch blocked、ready with residual blockers、ready for Agent53 field candidate。
- 更新 `experiments/run_grey_box_calibration_package_preflight.py`：
  - 同步生成 `outputs/grey_box_calibration_package/grey_box_field_calibration_summary.json`。
  - Markdown 报告新增 Agent53 Field Calibration Summary 区块。
  - manifest 新增 `latest_grey_box_field_calibration_*` 指针与 no-write 状态。
- 更新 `src/water_ai/new_core_interface_candidate_gate.py`：
  - 候选门新增 downstream calibration status。
  - summary 新增 `highest_priority_can_run_agent53_field_calibration` 与 `highest_priority_agent53_field_candidate_ready`。
- 更新 `src/water_ai/stage_boundary_external_action_board.py`：
  - stage board 和 operator runbook 透传 downstream calibration status、Agent53 可运行校准状态和 field candidate ready 状态。
- 更新 `experiments/run_new_core_interface_candidate_gate.py` 与 `experiments/run_agent50_model_core_governance.py`：
  - 读取 `grey_box_field_calibration_summary.json`。
  - 写入 generated files、report 和 manifest。
- 更新测试：
  - 验证未设置外部目录时 summary 等待 preflight。
  - 验证 preflight 通过但残留风险较高时，可以运行 Agent53 field calibration，但不能标记 field candidate ready。
  - 验证强去除样例可生成 Agent53 field candidate ready，同时仍保持 no-write/no-release。

当前结果：

- 默认未设置 `GREY_BOX_CALIBRATION_PACKAGE_DIR`，因此：
  - `summary_status=grey_box_field_calibration_waiting_for_preflight_ready`
  - `can_run_agent53_field_calibration=False`
  - `agent53_field_candidate_ready=False`
- `outputs/model_core_governance/new_core_interface_candidate_gate.json` 与 `outputs/model_core_governance/stage_boundary_external_action_board.json` 已同步显示同一 downstream calibration 状态。
- 当前最高阶段动作仍是 `FOCUSED_CATALYST_RESPONSE_PATH`；`GREY_BOX_CALIBRATION_PACKAGE_DIR` 是 new-core-interface 侧的最高候选接口，不覆盖 R7 focused catalyst 外部包路线。

验证：

- `.venv/bin/python -m py_compile ...`：通过。
- `.venv/bin/pytest -q tests/test_grey_box_calibration_package.py tests/test_new_core_interface_candidate_gate.py tests/test_stage_boundary_external_action_board.py`：15 passed。
- `.venv/bin/python experiments/run_grey_box_calibration_package_preflight.py`：通过。
- `.venv/bin/python experiments/run_new_core_interface_candidate_gate.py`：通过。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：通过。
- `.venv/bin/pytest -q tests/test_grey_box_calibration_package.py tests/test_new_core_interface_candidate_gate.py tests/test_stage_boundary_external_action_board.py tests/test_model_core_optimization_governance_agent.py tests/test_minimal_grey_box_physics_agent.py`：60 passed。
- `.venv/bin/pytest -q`：575 passed。
- `.venv/bin/python tools/build_project_codegraph.py`：`375 files / 4922 nodes / 7822 edges`。

边界：

- R8u149 是灰箱校准包到 Agent53 的 adapter，不是现场机制证明。
- `field_calibration_for_agent53` 是下游 Agent53 可消费的校准输入；即使 `agent53_field_candidate_ready=True`，仍不能直接生成 field evidence、恢复模型链或授权控制/放行。
- 所有 actuator/release gate 写入仍为 False。

## 2026-06-22 R8u-148：Grey-Box Calibration Package Preflight

目标：

- 承接 R8u147 的最高 new-core-interface 候选 `NCI1_GREY_BOX_CALIBRATION_PACKAGE`。
- 把 `GREY_BOX_CALIBRATION_PACKAGE_DIR` 从候选接口名落成可执行 preflight。
- 让灰箱物理层从 synthetic prior 走向可校准外部接口，但不把 preflight 写成 field 结论。

实现：

- 新增 `src/water_ai/grey_box_calibration_package.py`：
  - 定义 `GREY_BOX_CALIBRATION_PACKAGE_DIR`。
  - 定义五张最小校准表：`batch_inlet_outlet_lab`、`hydraulic_rtd_or_tracer`、`oxidant_dose_residual_log`、`catalyst_age_regeneration_log`、`byproduct_panel`。
  - 新增 `build_grey_box_calibration_package_template()`。
  - 新增 `write_grey_box_calibration_package_template()`。
  - 新增 `build_grey_box_calibration_package_preflight()`。
  - 预检 field origin、QA、模板标记、必需列、数值合法性和五表共同 `batch_id`。
- 新增 `experiments/run_grey_box_calibration_package_preflight.py`：
  - 写出 `outputs/grey_box_calibration_package/grey_box_calibration_package_template/`。
  - 写出 `outputs/grey_box_calibration_package/grey_box_calibration_package_preflight.json`。
  - 写出 `deliverables/model_core_optimization/grey_box_calibration_package_preflight.md`。
  - 回写 manifest。
- 更新 `src/water_ai/new_core_interface_candidate_gate.py`：
  - 候选门现在消费 grey-box calibration preflight。
  - 最高候选 summary 新增 preflight status、preflight pass、can route to downstream calibration。
  - 修复一个候选筛选边界：`interface_preflight_ready...` 也属于可接受候选，不能被 admissible-only 过滤跳过。
- 更新 `src/water_ai/stage_boundary_external_action_board.py`：
  - `NEW_CORE_INTERFACE` action row 和 Markdown 报告透传最高候选 preflight status/pass。
- 更新 `experiments/run_agent50_model_core_governance.py`：
  - Agent50 自动读取 `grey_box_calibration_package_preflight.json`。
  - 生成文件列表与 manifest 接入该 preflight。

当前结果：

- `outputs/grey_box_calibration_package/grey_box_calibration_package_preflight.json`：
  - `package_status=grey_box_calibration_package_waiting_for_GREY_BOX_CALIBRATION_PACKAGE_DIR`
  - `package_preflight_pass=False`
  - `matched_batch_count=0`
  - `next_operator_action=fill_grey_box_calibration_package_template_and_set_GREY_BOX_CALIBRATION_PACKAGE_DIR`
- `outputs/model_core_governance/new_core_interface_candidate_gate.json`：
  - 最高候选仍为 `NCI1_GREY_BOX_CALIBRATION_PACKAGE`。
  - `highest_priority_preflight_status=grey_box_calibration_package_waiting_for_GREY_BOX_CALIBRATION_PACKAGE_DIR`
  - `highest_priority_preflight_pass=False`
- `outputs/model_core_governance/stage_boundary_external_action_board.json`：
  - `NEW_CORE_INTERFACE` 行显示 `GREY_BOX_CALIBRATION_PACKAGE_DIR`。
  - preflight status/pass 同步为 waiting/False。

验证：

- `.venv/bin/pytest -q tests/test_grey_box_calibration_package.py tests/test_new_core_interface_candidate_gate.py tests/test_stage_boundary_external_action_board.py`：14 passed。
- `.venv/bin/python experiments/run_grey_box_calibration_package_preflight.py`：通过。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：通过。
- `.venv/bin/pytest -q tests/test_grey_box_calibration_package.py tests/test_new_core_interface_candidate_gate.py tests/test_stage_boundary_external_action_board.py tests/test_model_core_optimization_governance_agent.py tests/test_minimal_grey_box_physics_agent.py`：59 passed。
- `.venv/bin/pytest -q`：574 passed。
- `.venv/bin/python tools/build_project_codegraph.py`：`375 files / 4912 nodes / 7810 edges`。

边界：

- R8u148 是灰箱校准包入口 preflight，不是 Agent53 field calibration 结果。
- 即使未来 preflight 通过，也只表示可进入 Agent53 calibration consumer；仍需 downstream calibration、replay/holdout 和人工/发布门。
- 本轮不生成 field evidence，不证明机理有效，不恢复模型链，不写 actuator 或 release gate。

## 2026-06-22 R8u-147：New Core Interface Candidate Gate

目标：

- 承接 R8u146 后的阶段边界判断。
- 当前核心门已停止内部 synthetic/template 扩张，允许继续的路径只有真实外部包或新的可测试核心接口。
- 修复 `NEW_CORE_INTERFACE` 过于泛化的问题：不能只写“可定义新接口”，必须说明新接口候选是什么、服务哪层骨架、需要什么输入、输出什么指标、验证命令是什么、失败边界是什么。

实现：

- 新增 `src/water_ai/new_core_interface_candidate_gate.py`：
  - 新增 `build_new_core_interface_candidate_gate()`。
  - 新增 `new_core_interface_candidate_gate_report_md()`。
  - 将 Agent50 priority ranking 过滤为 5 个可审查新接口候选。
- 新增 `experiments/run_new_core_interface_candidate_gate.py`：
  - 输出 `outputs/model_core_governance/new_core_interface_candidate_gate.json`。
  - 输出 `deliverables/model_core_optimization/new_core_interface_candidate_gate.md`。
  - 回写 manifest 的 latest new-core-interface 字段。
- 更新 `src/water_ai/stage_boundary_external_action_board.py`：
  - 新增可选输入 `new_core_interface_candidate_gate`。
  - 在 summary、NEW_CORE_INTERFACE action row、operator runbook 和 Markdown 报告中暴露最高候选接口。
- 更新 `experiments/run_stage_boundary_external_action_board.py`：
  - 若存在 `new_core_interface_candidate_gate.json`，自动接入行动板。
- 更新 `experiments/run_agent50_model_core_governance.py`：
  - 每次 Agent50 运行时自动生成 new core interface candidate gate。
  - 再把候选门喂给 stage boundary external action board。
  - 将候选门写入 generated files 和 manifest。
- 新增/更新测试：
  - 新增 `tests/test_new_core_interface_candidate_gate.py`。
  - 更新 `tests/test_stage_boundary_external_action_board.py`，断言行动板能看到 ranked new-core-interface candidate。

当前结果：

- `outputs/model_core_governance/new_core_interface_candidate_gate.json`：
  - `gate_status=new_core_interface_candidate_gate_ready_with_ranked_contracts`
  - `candidate_count=5`
  - `admissible_candidate_count=5`
  - `highest_priority_candidate_id=NCI1_GREY_BOX_CALIBRATION_PACKAGE`
  - `highest_priority_source_env_var=GREY_BOX_CALIBRATION_PACKAGE_DIR`
- `deliverables/model_core_optimization/stage_boundary_external_action_board.md`：
  - `NEW_CORE_INTERFACE` 行现在显示 `GREY_BOX_CALIBRATION_PACKAGE_DIR`。
  - 新增 `New Core Interface Candidate` 小节。
- `deliverables/manifest.json`：
  - 新增 `latest_agent50_new_core_interface_candidate_gate_status`。
  - 新增 `latest_agent50_new_core_interface_highest_priority_candidate_id`。
  - 新增 `latest_agent50_new_core_interface_highest_priority_source_env_var`。

验证：

- `.venv/bin/pytest -q tests/test_new_core_interface_candidate_gate.py tests/test_stage_boundary_external_action_board.py`：9 passed。
- `.venv/bin/python -m py_compile src/water_ai/new_core_interface_candidate_gate.py src/water_ai/stage_boundary_external_action_board.py experiments/run_new_core_interface_candidate_gate.py experiments/run_stage_boundary_external_action_board.py experiments/run_agent50_model_core_governance.py`：通过。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：通过，并刷新候选门、行动板与 manifest。
- `.venv/bin/pytest -q tests/test_new_core_interface_candidate_gate.py tests/test_stage_boundary_external_action_board.py tests/test_model_core_optimization_governance_agent.py`：49 passed。
- `.venv/bin/pytest -q`：569 passed。
- `.venv/bin/python tools/build_project_codegraph.py`：`371 files / 4857 nodes / 7730 edges`。

边界：

- R8u147 是架构治理接口门，不是新的 field 校准结果。
- 它不实现 `GREY_BOX_CALIBRATION_PACKAGE_DIR` preflight，只把该接口列为当前最高 new-core-interface 候选。
- 它不生成 field evidence，不恢复模型链，不写 actuator 或 release gate。

## 2026-06-22 R8u-146：Focused Merge Preflight Submit-Ready Semantics

目标：

- 承接 R8u145 的阶段行动板 submit-ready 语义收紧。
- 回到 focused catalyst response merge 源头，避免 `candidate_self_declared_submit_ready` 旧命名继续污染下游理解。
- 保留兼容字段，但新增更准确的 preflight submit-ready 语义，说明候选文件只可作为 `FIELD_ACTIVATION_RESPONSE_PATH` 的下游预检输入，不是 field validation。

实现：

- 更新 `src/water_ai/focused_catalyst_response_merge.py`：
  - 新增 `candidate_preflight_submit_ready`。
  - 新增 `candidate_submit_ready_semantics`。
  - 新增 `merged_full_response_candidate_preflight_submit_ready`。
  - 新增 `merged_full_response_candidate_submit_ready_semantics`。
  - 保留 `candidate_self_declared_submit_ready` / `merged_full_response_candidate_self_declared_submit_ready` 作为 legacy alias。
- 更新 `experiments/run_focused_catalyst_response_merge.py`：
  - Markdown 改为显示 `candidate_preflight_submit_ready`。
  - 旧 self-declared 字段改名为 `candidate_self_declared_submit_ready_legacy_alias`。
  - manifest 新增 `latest_focused_catalyst_response_merge_candidate_preflight_submit_ready` 与 `latest_focused_catalyst_response_merge_candidate_submit_ready_semantics`。
- 更新 `src/water_ai/agents/model_core_optimization_governance_agent.py`：
  - Agent50 scorecard 新增 `focused_catalyst_response_merge_candidate_preflight_submit_ready`。
  - Agent50 scorecard 新增 `focused_catalyst_response_merge_candidate_submit_ready_semantics`。
- 更新 `experiments/run_agent50_model_core_governance.py`：
  - manifest 新增 `latest_agent50_focused_catalyst_response_merge_candidate_preflight_submit_ready`。
  - manifest 新增 `latest_agent50_focused_catalyst_response_merge_candidate_submit_ready_semantics`。
- 更新测试：
  - focused merge 测试断言新字段和语义边界。
  - Agent50 测试断言治理层消费新字段。
  - focused merge Markdown 测试断言人读报告不再只展示含混 self-declared 标签。

当前结果：

- `focused_catalyst_response_merge_preflight.json`：
  - `merged_full_response_candidate_preflight_submit_ready=False`
  - `merged_full_response_candidate_self_declared_submit_ready=False`
  - `merged_full_response_candidate_submit_ready_semantics` 明确不是 field validation / model-chain resume / actuator / release。
- `merged_full_field_activation_response_candidate.json`：
  - `candidate_preflight_submit_ready=False`
  - `candidate_self_declared_submit_ready=False`
  - `candidate_submit_ready_semantics` 明确该文件只是下游 preflight 输入。
- `deliverables/manifest.json`：
  - `latest_focused_catalyst_response_merge_candidate_preflight_submit_ready=False`
  - `latest_agent50_focused_catalyst_response_merge_candidate_preflight_submit_ready=False`

验证：

- `.venv/bin/pytest -q tests/test_focused_catalyst_response_merge.py tests/test_model_core_optimization_governance_agent.py tests/test_external_activation_operator_packet.py tests/test_stage_boundary_external_action_board.py`：52 passed。
- `.venv/bin/python -m py_compile src/water_ai/focused_catalyst_response_merge.py src/water_ai/agents/model_core_optimization_governance_agent.py experiments/run_focused_catalyst_response_merge.py experiments/run_agent50_model_core_governance.py`：通过。
- `.venv/bin/python experiments/run_focused_catalyst_response_merge.py`：通过。
- `.venv/bin/python experiments/run_external_activation_operator_packet.py`：通过。
- `.venv/bin/python experiments/run_stage_boundary_external_action_board.py`：通过。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：通过。
- `.venv/bin/pytest -q`：565 passed。
- `.venv/bin/python tools/build_project_codegraph.py`：`367 files / 4823 nodes / 7675 edges`。

边界：

- R8u146 是 focused merge 源头证据语义修复，不是新模型 agent。
- 它不生成 focused response，不生成 field evidence，不恢复 model chain。
- 它不写 actuator 或 release gate。

## 2026-06-22 R8u-145：Stage Board Submit-Ready Semantics Tightened

目标：

- 继续承接外部 focused catalyst response 的最高优先级链路。
- 修复阶段边界行动板中 `highest_priority_focused_candidate_submit_ready` 的潜在语义风险：不能让 self-declared ready 被误读为真正可提交。
- 让 action board、operator runbook、Markdown 报告和 manifest 都区分：
  - `focused_candidate_self_declared_submit_ready`
  - `focused_candidate_operator_packet_submit_ready`
  - canonical `focused_candidate_submit_ready`

实现：

- 更新 `src/water_ai/stage_boundary_external_action_board.py`：
  - summary 的 `highest_priority_focused_candidate_submit_ready` 改为读取 canonical `focused_candidate_submit_ready`。
  - 新增 `highest_priority_focused_candidate_operator_packet_submit_ready`。
  - R7 focused candidate context 新增 `focused_candidate_operator_packet_submit_ready` 与 `focused_candidate_submit_ready`。
  - canonical submit-ready 只有在 operator packet ready、candidate can-submit gate 和 row preflight 均通过时才为 True。
  - Markdown 报告的 Board State 与 Action Rows 显示 operator-packet ready 和 submit-ready。
- 更新 `experiments/run_stage_boundary_external_action_board.py` 与 `experiments/run_agent50_model_core_governance.py`：
  - manifest 写入 `latest_stage_boundary_external_action_board_highest_priority_focused_candidate_operator_packet_submit_ready`。
  - Agent50 manifest 同步写入 `latest_agent50_stage_boundary_external_action_board_highest_priority_focused_candidate_operator_packet_submit_ready`。
- 更新 `tests/test_stage_boundary_external_action_board.py`：
  - 覆盖“自声明 ready 但 operator/preflight 未通过时仍不可提交”的场景。
  - 覆盖“operator packet 与 preflight 均通过时才 submit-ready”的场景。
  - 覆盖 Markdown 报告必须显示两个 ready 字段。

当前结果：

- `outputs/model_core_governance/stage_boundary_external_action_board.json`：
  - `highest_priority_focused_candidate_operator_packet_submit_ready=False`
  - `highest_priority_focused_candidate_submit_ready=False`
  - R7 row 中 `focused_candidate_operator_packet_submit_ready=False`
  - R7 row 中 `focused_candidate_submit_ready=False`
- `deliverables/manifest.json`：
  - `latest_stage_boundary_external_action_board_highest_priority_focused_candidate_operator_packet_submit_ready=False`
  - `latest_agent50_stage_boundary_external_action_board_highest_priority_focused_candidate_operator_packet_submit_ready=False`
- `deliverables/model_core_optimization/stage_boundary_external_action_board.md` 已显示 operator packet ready 与 submit ready。

验证：

- `.venv/bin/pytest -q tests/test_stage_boundary_external_action_board.py tests/test_model_core_optimization_governance_agent.py tests/test_external_activation_operator_packet.py tests/test_focused_catalyst_response_merge.py`：51 passed。
- `.venv/bin/python -m py_compile src/water_ai/stage_boundary_external_action_board.py experiments/run_stage_boundary_external_action_board.py experiments/run_agent50_model_core_governance.py`：通过。
- `.venv/bin/python experiments/run_stage_boundary_external_action_board.py`：通过。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：通过。
- `.venv/bin/pytest -q`：564 passed。
- `.venv/bin/python tools/build_project_codegraph.py`：`367 files / 4819 nodes / 7668 edges`。

边界：

- R8u145 是证据语义收紧，不是新模型 agent。
- 它不生成 focused response、不生成 field evidence、不恢复 model chain。
- 它不写 actuator 或 release gate。

## 2026-06-22 R8u-144：Core Gate R7 Action Consumes Focused Candidate Availability

目标：

- 承接 R8u143：operator packet 和 Agent50 已能看到 focused candidate 不可提交状态。
- 修复最高 core gate 中 R7 action row 的回接缺口：`next_allowed_actions.R7_REAL_FIELD_PACKAGE` 此前仍未直接暴露 candidate availability。
- 让只读 `core_score_termination_gate.json` 的后续流程，也能从 R7 external package action row 判断当前不能提交 `FIELD_ACTIVATION_RESPONSE_PATH`。

实现：

- 更新 `src/water_ai/agents/model_core_optimization_governance_agent.py`：
  - 新增 `_external_activation_operator_packet_core_gate_fields()`。
  - 将该字段包只回接到 `channel_id == R7_REAL_FIELD_PACKAGE` 的 action row。
  - 回接字段包括：
    - `external_activation_operator_action_packet_status`
    - `external_activation_operator_action_packet_target_hidden_state`
    - `external_activation_operator_action_packet_source_env_var`
    - `external_activation_operator_action_packet_expected_focused_response_row_count`
    - `external_activation_operator_action_packet_focused_candidate_availability_status`
    - `external_activation_operator_action_packet_focused_candidate_operator_packet_submit_ready`
    - `external_activation_operator_action_packet_next_operator_action`
    - `external_activation_operator_action_packet_boundary_pass`
    - `external_activation_operator_action_packet_can_resume_model_chain`
    - `external_activation_operator_action_packet_can_write_to_actuator`
    - `external_activation_operator_action_packet_can_write_to_release_gate`
- 更新 `tests/test_model_core_optimization_governance_agent.py`：
  - 断言 `R7_REAL_FIELD_PACKAGE` action row 直接显示 operator packet status、candidate availability、submit-ready false 和 no-write flags。

当前结果：

- `core_score_termination_gate.json.next_allowed_actions[R7_REAL_FIELD_PACKAGE]`：
  - `external_activation_operator_action_packet_status=operator_packet_waiting_for_focused_catalyst_response`
  - `external_activation_operator_action_packet_focused_candidate_availability_status=candidate_not_submittable_waiting_for_FOCUSED_CATALYST_RESPONSE_PATH`
  - `external_activation_operator_action_packet_focused_candidate_operator_packet_submit_ready=False`
  - `external_activation_operator_action_packet_can_resume_model_chain=False`
  - `external_activation_operator_action_packet_can_write_to_actuator=False`
  - `external_activation_operator_action_packet_can_write_to_release_gate=False`

验证：

- `.venv/bin/pytest -q tests/test_model_core_optimization_governance_agent.py`：40 passed。
- `.venv/bin/python experiments/run_focused_catalyst_response_merge.py`：通过。
- `.venv/bin/python experiments/run_external_activation_operator_packet.py`：通过。
- `.venv/bin/python experiments/run_stage_boundary_external_action_board.py`：通过。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：通过。
- `.venv/bin/pytest -q tests/test_model_core_optimization_governance_agent.py tests/test_external_activation_operator_packet.py tests/test_stage_boundary_external_action_board.py tests/test_focused_catalyst_response_merge.py`：49 passed。
- `.venv/bin/pytest -q`：562 passed。
- `.venv/bin/python tools/build_project_codegraph.py`：`367 files / 4817 nodes / 7665 edges`。

边界：

- R8u144 是最高 core gate 的证据边界回接，不是新模型 agent。
- 它不生成 focused response、不生成 field evidence、不恢复 model chain。
- 它不写 actuator 或 release gate。
- 它的作用是让 core gate 的 R7 action row、NEW_CORE_INTERFACE、external resume conditions、operator packet、action board 和 Agent50 scorecard 都一致承接 candidate 不可提交状态。

## 2026-06-22 R8u-143：Operator Packet Consumes Focused Candidate Availability

目标：

- 承接 R8u142：action board 已显示 focused candidate 当前不可提交。
- 修复 operator-facing 执行包的同类缺口：`external_activation_operator_action_packet.json` 此前给出 candidate path 与 can-submit 布尔值，但未直接暴露 candidate availability 和 use boundary。
- 让操作者只读 operator packet 时，也能知道当前 `merged_full_field_activation_response_candidate.json` 不能作为 `FIELD_ACTIVATION_RESPONSE_PATH` 使用。

实现：

- 更新 `src/water_ai/external_activation_operator_packet.py`：
  - 新增 `focused_candidate_availability_status`。
  - 新增 `focused_candidate_self_declared_submit_ready`。
  - 新增 `focused_candidate_external_response_supplied`。
  - 新增 `focused_candidate_operator_packet_submit_ready`。
  - 新增 `focused_candidate_use_boundary`。
  - packet readiness 现在同时参考 merge preflight `can_submit_candidate_as_FIELD_ACTIVATION_RESPONSE_PATH` 与 candidate self-declared submit-ready。
- 更新 `experiments/run_external_activation_operator_packet.py`：
  - Markdown 报告显示 candidate availability / submit-ready。
  - manifest 写入 `latest_external_activation_operator_action_packet_focused_candidate_*` 字段。
- 更新 `src/water_ai/agents/model_core_optimization_governance_agent.py`：
  - Agent50 scorecard 新增 operator packet candidate availability 与 submit-ready。
  - `field_evidence_wait_status` 同步暴露该状态。
  - core gate 的 `new_core_interface` 与 `external_resume_conditions.new_core_interface` 同步暴露该状态。
- 更新 `experiments/run_agent50_model_core_governance.py`：
  - manifest 写入 `latest_agent50_external_activation_operator_action_packet_focused_candidate_*` 字段。
- 更新测试：
  - `tests/test_external_activation_operator_packet.py` 覆盖 waiting 与 ready 两种 candidate availability。
  - `tests/test_model_core_optimization_governance_agent.py` 覆盖 scorecard、field wait status、core gate 和 resume conditions 的回接字段。

当前结果：

- `external_activation_operator_action_packet.json`：
  - `packet_status=operator_packet_waiting_for_focused_catalyst_response`
  - `focused_candidate_availability_status=candidate_not_submittable_waiting_for_FOCUSED_CATALYST_RESPONSE_PATH`
  - `focused_candidate_operator_packet_submit_ready=False`
- Agent50 scorecard：
  - `external_activation_operator_action_packet_focused_candidate_availability_status=candidate_not_submittable_waiting_for_FOCUSED_CATALYST_RESPONSE_PATH`
  - `external_activation_operator_action_packet_focused_candidate_operator_packet_submit_ready=False`
- manifest：
  - `latest_external_activation_operator_action_packet_focused_candidate_availability_status=candidate_not_submittable_waiting_for_FOCUSED_CATALYST_RESPONSE_PATH`
  - `latest_agent50_external_activation_operator_action_packet_focused_candidate_availability_status=candidate_not_submittable_waiting_for_FOCUSED_CATALYST_RESPONSE_PATH`

验证：

- `.venv/bin/pytest -q tests/test_external_activation_operator_packet.py tests/test_model_core_optimization_governance_agent.py`：42 passed。
- `.venv/bin/python experiments/run_focused_catalyst_response_merge.py`：通过。
- `.venv/bin/python experiments/run_external_activation_operator_packet.py`：通过。
- `.venv/bin/python experiments/run_stage_boundary_external_action_board.py`：通过。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：通过。
- `.venv/bin/pytest -q tests/test_external_activation_operator_packet.py tests/test_model_core_optimization_governance_agent.py tests/test_focused_catalyst_response_merge.py tests/test_stage_boundary_external_action_board.py`：49 passed。
- `.venv/bin/pytest -q`：562 passed。
- `.venv/bin/python tools/build_project_codegraph.py`：`367 files / 4816 nodes / 7664 edges`。

边界：

- R8u143 是外部执行包的证据边界回接，不是新模型 agent。
- 它不生成 focused response，不生成 field evidence，不恢复模型链。
- 它不写 actuator 或 release gate。
- 它的作用是让 operator packet、action board、Agent50 和 manifest 都一致承接“candidate 不可提交”的状态。

## 2026-06-22 R8u-142：Stage Board Consumes Focused Candidate Availability

目标：

- 承接 R8u141：focused merge candidate 已有自证式 availability watermark。
- 修复最高操作入口回接缺口：阶段边界 action board 此前只显示要填写 `FOCUSED_CATALYST_RESPONSE_PATH`，未显示当前 merged candidate 文件不可提交。
- 让操作者/后续 agent 只读 action board 时，也能知道“文件存在”不等于“candidate 可提交”。

实现：

- 更新 `src/water_ai/stage_boundary_external_action_board.py`：
  - `build_stage_boundary_external_action_board()` 新增可选输入 `focused_catalyst_response_merge_metrics`。
  - `R7_REAL_FIELD_PACKAGE` action row 新增：
    - `focused_merge_preflight_status`
    - `focused_candidate_availability_status`
    - `focused_candidate_self_declared_submit_ready`
    - `focused_candidate_external_response_supplied`
    - `focused_candidate_can_submit_as_FIELD_ACTIVATION_RESPONSE_PATH`
    - `focused_merge_row_preflight_pass`
    - `focused_merge_matched_batch_count`
    - `focused_merge_minimum_matched_batch_count`
    - `focused_candidate_use_boundary`
  - action summary 新增最高优先级 candidate availability 和 submit ready。
  - Markdown action rows 增加 candidate status 列。
  - operator runbook 增加 focused candidate availability 和 submit ready。
- 更新 `experiments/run_stage_boundary_external_action_board.py`：
  - 读取 `outputs/focused_catalyst_response_merge/focused_catalyst_response_merge_preflight.json`。
  - 将最高优先级 candidate availability/status 写入 manifest。
- 更新 `experiments/run_agent50_model_core_governance.py`：
  - Agent50 自动刷新 action board 时同步传入 focused merge metrics。
  - manifest 新增 `latest_agent50_stage_boundary_external_action_board_highest_priority_focused_candidate_*` 与通用 `latest_stage_boundary_external_action_board_highest_priority_focused_candidate_*` 字段。
- 更新 `tests/test_stage_boundary_external_action_board.py`：
  - 断言 R7 highest-priority action row 显示 focused merge preflight status、candidate availability、submit ready false、external response false 和 no-write。
  - 断言 Markdown 报告包含 `candidate_not_submittable_waiting_for_FOCUSED_CATALYST_RESPONSE_PATH`。

当前结果：

- `stage_boundary_external_action_board.json` 最高优先级 action row：
  - `source_env_var=FOCUSED_CATALYST_RESPONSE_PATH`
  - `focused_merge_preflight_status=focused_catalyst_response_merge_waiting_for_FOCUSED_CATALYST_RESPONSE_PATH`
  - `focused_candidate_availability_status=candidate_not_submittable_waiting_for_FOCUSED_CATALYST_RESPONSE_PATH`
  - `focused_candidate_self_declared_submit_ready=False`
  - `focused_candidate_external_response_supplied=False`
- manifest 同步显示：
  - `latest_agent50_stage_boundary_external_action_board_highest_priority_focused_candidate_availability_status=candidate_not_submittable_waiting_for_FOCUSED_CATALYST_RESPONSE_PATH`
  - `latest_stage_boundary_external_action_board_highest_priority_focused_candidate_availability_status=candidate_not_submittable_waiting_for_FOCUSED_CATALYST_RESPONSE_PATH`

验证：

- `.venv/bin/pytest -q tests/test_stage_boundary_external_action_board.py`：3 passed。
- `.venv/bin/python experiments/run_focused_catalyst_response_merge.py`：通过。
- `.venv/bin/python experiments/run_stage_boundary_external_action_board.py`：通过。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：通过。
- `.venv/bin/pytest -q tests/test_stage_boundary_external_action_board.py tests/test_focused_catalyst_response_merge.py tests/test_model_core_optimization_governance_agent.py tests/test_external_activation_operator_packet.py`：49 passed。
- `.venv/bin/pytest -q`：562 passed。
- `.venv/bin/python tools/build_project_codegraph.py`：`367 files / 4814 nodes / 7662 edges`。

边界：

- R8u142 是验证治理层和外部行动板的回接修复，不是新模型 agent。
- 它不生成 focused catalyst response，不生成 field evidence，不恢复 field replay/control。
- 它不写 actuator 或 release gate。
- 它的价值是让最高操作入口直接承接 R8u141 的“候选不可提交”水印，减少误用风险。

## 2026-06-22 R8u-141：Focused Merge Candidate Availability Watermark

目标：

- 承接 R8u140：Agent50 已能自动刷新阶段边界行动板，最高优先级仍是 `FOCUSED_CATALYST_RESPONSE_PATH`。
- 核查 focused catalyst response 入口的工程风险：未提交外部 focused response 时，runner 仍会写出 `merged_full_field_activation_response_candidate.json`。
- 修复“文件存在可能被误读为候选可提交”的验证治理缺口，让候选文件本身也能自证当前是否可作为 `FIELD_ACTIVATION_RESPONSE_PATH`。

实现：

- 更新 `src/water_ai/focused_catalyst_response_merge.py`：
  - merged candidate 新增 `candidate_availability_status`。
  - 新增 `can_submit_candidate_as_FIELD_ACTIVATION_RESPONSE_PATH`、`external_focused_response_supplied`、`source_preflight_status`、`focused_row_preflight_pass`、matched batch 指标和 `candidate_use_boundary`。
  - merge preflight 顶层同步输出 `merged_full_response_candidate_availability_status`、`merged_full_response_candidate_self_declared_submit_ready`、`merged_full_response_candidate_external_response_supplied` 和候选使用边界。
- 更新 `experiments/run_focused_catalyst_response_merge.py`：
  - Markdown 报告新增候选 availability 和 self-declared submit readiness。
  - manifest 新增 `latest_focused_catalyst_response_merge_candidate_*` 字段。
- 更新 `src/water_ai/agents/model_core_optimization_governance_agent.py`：
  - Agent50 scorecard 新增 `focused_catalyst_response_merge_candidate_availability_status`。
  - Agent50 scorecard 新增 `focused_catalyst_response_merge_candidate_self_declared_submit_ready`。
- 更新 `experiments/run_agent50_model_core_governance.py`：
  - manifest 新增 `latest_agent50_focused_catalyst_response_merge_candidate_*` 字段。
- 更新测试：
  - focused merge 单测断言等待外部输入时，候选状态为 `candidate_not_submittable_waiting_for_FOCUSED_CATALYST_RESPONSE_PATH`。
  - focused merge 单测断言 rows/batch 通过时，候选状态为 `candidate_ready_for_FIELD_ACTIVATION_RESPONSE_PATH_preflight_only`。
  - Agent50 单测断言治理层能看到候选不可提交状态。

当前结果：

- 当前未提交外部 focused response，因此候选文件自证：
  - `candidate_availability_status=candidate_not_submittable_waiting_for_FOCUSED_CATALYST_RESPONSE_PATH`
  - `can_submit_candidate_as_FIELD_ACTIVATION_RESPONSE_PATH=False`
  - `external_focused_response_supplied=False`
  - `focused_replacement_row_count=0`
- Agent50 scorecard 和 manifest 同步显示：
  - `focused_catalyst_response_merge_candidate_availability_status=candidate_not_submittable_waiting_for_FOCUSED_CATALYST_RESPONSE_PATH`
  - `focused_catalyst_response_merge_candidate_self_declared_submit_ready=False`

验证：

- `.venv/bin/pytest -q tests/test_focused_catalyst_response_merge.py tests/test_model_core_optimization_governance_agent.py`：44 passed。
- `.venv/bin/python experiments/run_focused_catalyst_response_merge.py`：通过，候选文件与 manifest 已刷新。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：通过，Agent50 已消费候选 availability。
- `.venv/bin/pytest -q tests/test_focused_catalyst_response_merge.py tests/test_model_core_optimization_governance_agent.py tests/test_stage_boundary_external_action_board.py tests/test_external_activation_operator_packet.py`：49 passed。
- `.venv/bin/pytest -q`：562 passed。
- `.venv/bin/python tools/build_project_codegraph.py`：`367 files / 4812 nodes / 7658 edges`。

边界：

- R8u141 是验证治理层的候选文件水印，不是新模型 agent。
- 它不生成 focused field response、不生成 full field activation response、不恢复模型链。
- 它不把 template/default candidate 升级成 field evidence，不写 actuator 或 release gate。
- 它的作用是让候选产物、manifest 和 Agent50 都能明确区分“文件存在”和“候选可提交”。

## 2026-06-22 R8u-140：Agent50 Refreshes Stage Boundary External Action Board

目标：

- 承接 R8u139：阶段边界外部行动板已经可独立生成，但尚未接入 Agent50 主治理 runner。
- 修复同步风险：如果后续只运行 Agent50，`stage_boundary_external_action_board.json/md` 可能落后于最新 core gate。
- 不新增模型复杂度，只把已经定义好的阶段边界行动板变成 Agent50 每次运行后的自动刷新产物。

实现：

- 更新 `src/water_ai/stage_boundary_external_action_board.py`：
  - 新增 `stage_boundary_external_action_board_report_md()`，把 Markdown 报告渲染逻辑从独立 runner 提到共享模型模块。
  - 保持 board JSON 结构不变，仍由 core gate、external activation operator packet 和 formal-search operator packet 构造。
- 更新 `experiments/run_stage_boundary_external_action_board.py`：
  - 改为调用共享 Markdown 渲染函数，避免独立 runner 和 Agent50 runner 维护两套报告逻辑。
- 更新 `experiments/run_agent50_model_core_governance.py`：
  - 读取 Agent50 当前生成的 `quantified_core_score_gate` 后，立即构造 `stage_boundary_external_action_board`。
  - 将 `stage_boundary_external_action_board.json` 与 `stage_boundary_external_action_board.md` 写入 `generated_files` 和 Agent50 payload。
  - manifest 新增/刷新 `latest_agent50_stage_boundary_external_action_board_*` 字段，并同步通用 `latest_stage_boundary_external_action_board_*` 字段。
  - 将当前 work item 元数据更新为 `r8u140_agent50_refreshes_stage_boundary_external_action_board`。
- 更新 `tests/test_stage_boundary_external_action_board.py`：
  - 新增 Markdown 报告断言，确认报告暴露最高优先级 `FOCUSED_CATALYST_RESPONSE_PATH`、formal review response env var 和 no-write 边界。

当前结果：

- Agent50 runner 现在会自动刷新：
  - `outputs/model_core_governance/stage_boundary_external_action_board.json`
  - `deliverables/model_core_optimization/stage_boundary_external_action_board.md`
- 自动刷新后的行动板状态：
  - `board_status=stage_boundary_external_action_board_waiting_for_external_inputs`
  - `action_count=4`
  - `external_wait_count=3`
  - `model_chain_resume_ready_count=0`
  - `highest_priority_source_env_var=FOCUSED_CATALYST_RESPONSE_PATH`
  - `can_write_to_actuator=False`
  - `can_write_to_release_gate=False`

验证：

- `.venv/bin/pytest -q tests/test_stage_boundary_external_action_board.py`：3 passed。
- `.venv/bin/python experiments/run_stage_boundary_external_action_board.py`：通过，独立 runner 仍可生成 board/report。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：通过，Agent50 已自动刷新 board/report 并回写 manifest。
- `.venv/bin/pytest -q tests/test_stage_boundary_external_action_board.py tests/test_external_activation_operator_packet.py tests/test_formal_search_nonlegal_review_operator_packet.py tests/test_model_core_optimization_governance_agent.py`：48 passed。
- `.venv/bin/pytest -q`：562 passed。
- `.venv/bin/python tools/build_project_codegraph.py`：`367 files / 4809 nodes / 7654 edges`。

边界：

- R8u140 是治理刷新链路修复，不是新模型 agent。
- 它不生成 field evidence、不生成法律意见、不生成 prior-art 结论、不生成权利要求文本。
- 它不恢复 field replay/control，不写 actuator 或 release gate。
- 它的价值是减少 stale artifact 风险，让“Agent50 全局治理产物”和“阶段边界外部行动板”保持同源同步。

## 2026-06-22 R8u-139：Stage Boundary External Action Board

目标：

- 承接 R8u138：核心阶段门已经能看见 formal-search operator packet，但当前阶段已经是外部等待态。
- 遵守 goal 的阶段门控节流机制：`core_score=0.96`、`iteration_delta=0.0`、`continue_expansion_allowed=False`，不继续堆内部 synthetic/template 模块。
- 把分散在 core gate、external activation operator packet、formal-search operator packet 和 manifest 中的外部动作压成一个机器可读行动板。

实现：

- 新增 `src/water_ai/stage_boundary_external_action_board.py`：
  - 消费 `core_score_termination_gate.json`、`external_activation_operator_action_packet.json` 和 `formal_search_nonlegal_review_operator_packet.json`。
  - 生成 action rows：`R7_REAL_FIELD_PACKAGE`、`R8U66_PATH_ENDPOINT_LABEL_PACKAGE`、`R8U79_FORMAL_SEARCH_RESULT_PACKAGE` 和 `NEW_CORE_INTERFACE`。
  - 按优先级排序：主链 focused catalyst response 优先，其次 path/endpoint label package，再到 formal-search handoff，最后才是 new core interface。
  - 明确每个 action 的 source env var、expected row count、next operator action、validation command、handoff ready、model-chain resume ready 和 no-write 边界。
- 新增 `experiments/run_stage_boundary_external_action_board.py`：
  - 生成 `outputs/model_core_governance/stage_boundary_external_action_board.json`。
  - 生成 `deliverables/model_core_optimization/stage_boundary_external_action_board.md`。
  - 回写 manifest 的 latest stage-boundary action board 指针、status、action count、external wait count、highest priority env var 和 next action。
- 新增 `tests/test_stage_boundary_external_action_board.py`：
  - 验证行动板不会允许内部扩张。
  - 验证 `R7_REAL_FIELD_PACKAGE` 最高优先级指向 `FOCUSED_CATALYST_RESPONSE_PATH` 和 6 行 catalyst_activity focused response。
  - 验证 `R8U79_FORMAL_SEARCH_RESULT_PACKAGE` 是 handoff-only，指向 `FORMAL_SEARCH_NONLEGAL_REVIEW_RESPONSE_PATH` 和 7 行 human nonlegal review response，且不能 claim patch/claim text。
  - 验证所有 action 和 board 边界均不能写 actuator 或 release gate。

当前结果：

- `board_status=stage_boundary_external_action_board_waiting_for_external_inputs`
- `internal_expansion_allowed=False`
- `action_count=4`
- `external_wait_count=3`
- `model_chain_resume_ready_count=0`
- `handoff_ready_count=1`
- `highest_priority_action_id=R8u139_R7_REAL_FIELD_PACKAGE`
- `highest_priority_source_env_var=FOCUSED_CATALYST_RESPONSE_PATH`

验证：

- `.venv/bin/pytest -q tests/test_stage_boundary_external_action_board.py`：2 passed。
- `.venv/bin/python experiments/run_stage_boundary_external_action_board.py`：通过，已生成 action board/report 并回写 manifest。
- `.venv/bin/pytest -q tests/test_stage_boundary_external_action_board.py tests/test_external_activation_operator_packet.py tests/test_formal_search_nonlegal_review_operator_packet.py tests/test_model_core_optimization_governance_agent.py`：47 passed。
- `.venv/bin/pytest -q`：561 passed。
- `.venv/bin/python tools/build_project_codegraph.py`：`367 files / 4808 nodes / 7651 edges`。

边界：

- R8u139 是阶段边界外部行动板，不是新模型 agent。
- 它不生成 field evidence、不生成法律意见、不生成 prior-art 结论、不生成权利要求文本。
- 它不恢复 field replay/control，不写 actuator 或 release gate。
- 它的作用是停止低价值内部扩张，把下一步明确收束到真实外部输入、人工审查或新可测试核心接口。

## 2026-06-22 R8u-138：Core Gate Consumes Formal Search Nonlegal Review Operator Packet

目标：

- 承接 R8u137：Agent50 scorecard/report/manifest 已消费 R8u136 operator packet，但最高层 `core_score_termination_gate.json` 仍未直接暴露。
- 修复核心阶段门可见性缺口：后续只读 `next_allowed_actions` 或 `external_resume_conditions` 时，也应知道 R8U79 已有 human nonlegal review operator packet。
- 保持 R8U79 的 handoff-only 边界：它不能恢复 field replay/control，不能进入 claim patch，不能生成 claim text、法律意见或 field-supported claim。

实现：

- 更新 `src/water_ai/agents/model_core_optimization_governance_agent.py`：
  - 新增 `_formal_search_nonlegal_review_operator_packet_core_gate_fields()`。
  - 将 operator packet status、ready flag、expected row count、high priority row count、accepted row count、source env var、next operator action、claim patch route flag、boundary preserved 和 no-write/no-legal/no-field flags 写入 R8U79 `next_allowed_actions`。
  - 将同一组字段写入 `external_resume_conditions.formal_search_nonlegal_review_operator_packet`。
- 更新 `experiments/run_agent50_model_core_governance.py`：
  - 将当前 work item 元数据更新为 `r8u138_core_gate_consumes_formal_search_nonlegal_review_operator_packet`。
- 更新 `tests/test_model_core_optimization_governance_agent.py`：
  - 在 R8u136 operator packet 测试中新增 core gate 断言。
  - 验证 R8U79 action 仍为 `formal_search_handoff_only`，`current_handoff_ready=True`，`current_model_chain_resume_ready=False`。
  - 验证 `can_emit_claim_text=False`、`can_resume_model_chain=False`、`can_write_to_actuator=False`、`can_write_to_release_gate=False`。

当前结果：

- `core_score_termination_gate.next_allowed_actions[R8U79_FORMAL_SEARCH_RESULT_PACKAGE]`：
  - `formal_nonlegal_review_operator_packet_status=formal_search_nonlegal_review_operator_packet_ready_waiting_for_human_response`
  - `formal_nonlegal_review_operator_packet_ready=True`
  - `formal_nonlegal_review_operator_packet_expected_review_packet_row_count=7`
  - `formal_nonlegal_review_operator_packet_source_env_var=FORMAL_SEARCH_NONLEGAL_REVIEW_RESPONSE_PATH`
  - `formal_nonlegal_review_operator_packet_can_route_to_claim_scope_patch_draft=False`
  - `formal_nonlegal_review_operator_packet_can_resume_model_chain=False`
  - `formal_nonlegal_review_operator_packet_can_emit_claim_text=False`
  - `formal_nonlegal_review_operator_packet_can_write_to_actuator=False`
  - `formal_nonlegal_review_operator_packet_can_write_to_release_gate=False`
- `external_resume_conditions.formal_search_nonlegal_review_operator_packet` 同步暴露上述字段。

验证：

- `.venv/bin/pytest -q tests/test_model_core_optimization_governance_agent.py`：40 passed。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：通过，已刷新 `core_score_termination_gate.json`、priority ranking、Agent50 report 和 governance report。
- `.venv/bin/pytest -q tests/test_formal_search_nonlegal_review_operator_packet.py tests/test_formal_search_nonlegal_review_brief.py tests/test_preliminary_formal_search_package.py tests/test_agent_architecture_consolidation_agent.py tests/test_model_core_optimization_governance_agent.py`：99 passed。
- `.venv/bin/pytest -q`：559 passed。
- `.venv/bin/python tools/build_project_codegraph.py`：`363 files / 4777 nodes / 7596 edges`。

边界：

- R8u138 只增强最高层核心阶段门对 R8u136/R8u137 的可见性。
- 它不生成 human review response、不生成法律意见、不生成 prior-art 结论、不生成权利要求文本。
- 它不恢复 field replay/control，不写 actuator 或 release gate。

## 2026-06-22 R8u-137：Agent50 Consumes Formal Search Nonlegal Review Operator Packet

目标：

- 承接 R8u136：operator packet 已生成，但 Agent50 全局治理层还不能直接消费。
- 修复下游回接缺口：后续只读 Agent50 report、governance report、priority ranking 或 manifest 时，也应知道 R8u136 packet 已就绪、需要 7 行 human nonlegal review response、仍不能 claim patch。
- 保持边界：该回接不等于人工 review response，不等于法律意见，不允许 claim text、field replay/control 或 actuator/release gate。

实现：

- 更新 `src/water_ai/agents/model_core_optimization_governance_agent.py`：
  - 新增可选输入 `formal_search_nonlegal_review_operator_packet`。
  - scorecard 新增 operator packet status、expected review row count、high-priority row count、accepted row count、source env var、can route to claim scope patch draft、boundary preserved 和 next operator action。
  - protectability score 增加小幅 operator-packet-ready 贡献，仅表示人工审查接口机器可读，不表示专利授权或法律结论。
  - blocked reason 在 formal handoff-ready、R8u134 brief ready 且 R8u136 packet ready 时，更新为等待 `FORMAL_SEARCH_NONLEGAL_REVIEW_RESPONSE_PATH` 的 7 行人工非法律 review response。
- 更新 `experiments/run_agent50_model_core_governance.py`：
  - 读取 `outputs/agent_architecture_consolidation/formal_search_nonlegal_review_operator_packet.json`。
  - 将 R8u136 状态写入 Agent50 report、governance report、priority ranking 和 manifest 的 `latest_agent50_formal_search_nonlegal_review_operator_packet_*` 字段。
  - 修正 `current_work_item` 为 `r8u137_agent50_consumes_formal_search_nonlegal_review_operator_packet`，避免本轮治理元数据沿用旧 R8u114 名称。
- 更新 `tests/test_model_core_optimization_governance_agent.py`：
  - 新增 R8u136 operator packet fixture。
  - 验证 Agent50 能消费 packet，并保持 `can_route_to_claim_scope_patch_draft=False`、boundary preserved、next operator action 指向 Agent60 source preflight。

当前结果：

- Agent50 scorecard：
  - `formal_search_nonlegal_review_operator_packet_status=formal_search_nonlegal_review_operator_packet_ready_waiting_for_human_response`
  - `formal_search_nonlegal_review_operator_packet_expected_review_packet_row_count=7`
  - `formal_search_nonlegal_review_operator_packet_high_priority_review_row_count=1`
  - `formal_search_nonlegal_review_operator_packet_accepted_review_row_count=0`
  - `formal_search_nonlegal_review_operator_packet_source_env_var=FORMAL_SEARCH_NONLEGAL_REVIEW_RESPONSE_PATH`
  - `formal_search_nonlegal_review_operator_packet_can_route_to_claim_scope_patch_draft=False`
  - `formal_search_nonlegal_review_operator_packet_boundary_preserved=True`
- Agent50 blocked reason 已明确：R8u136 packet 已把 AI brief、response contract、source preflight 和 review readiness 集中成一个人工提交接口，但仍需要 7 行 human nonlegal review response。

验证：

- `.venv/bin/pytest -q tests/test_model_core_optimization_governance_agent.py`：40 passed。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：通过，已刷新 Agent50 report、governance report、priority ranking 和 manifest。
- `.venv/bin/pytest -q tests/test_formal_search_nonlegal_review_operator_packet.py tests/test_formal_search_nonlegal_review_brief.py tests/test_preliminary_formal_search_package.py tests/test_agent_architecture_consolidation_agent.py tests/test_model_core_optimization_governance_agent.py`：99 passed。
- `.venv/bin/pytest -q`：559 passed。
- `.venv/bin/python tools/build_project_codegraph.py`：`363 files / 4776 nodes / 7595 edges`。

边界：

- R8u137 只增强 R8u136 operator packet 的治理层消费和下游可见性。
- 它不生成 human review response、不生成法律意见、不生成 prior-art 结论、不生成权利要求文本。
- 它不恢复 field replay/control，不写 actuator 或 release gate。

## 2026-06-22 R8u-136：Formal Search Nonlegal Review Operator Packet

目标：

- 承接 R8u135：Agent50 已能消费 AI nonlegal review brief，但下一步人工仍要在多个 Agent60 产物之间定位 response template、source preflight、review readiness 和 claim patch blocker。
- 把 `FORMAL_SEARCH_NONLEGAL_REVIEW_RESPONSE_PATH` 的提交要求整理成一个可机读 operator packet，降低人工非法律技术比较的操作摩擦。
- 保持边界：operator packet 不是人工 review response，不是法律意见，不是 prior-art 结论，不是权利要求文本，也不能恢复 field replay/control。

实现：

- 新增 `src/water_ai/formal_search_nonlegal_review_operator_packet.py`：
  - 聚合 R8u134 AI brief、Agent60 nonlegal review response template、response source preflight、formal search review readiness 和 claim scope patch draft blocker。
  - 输出 packet metadata、operator action、response contract、human review rows、pre-submission checklist、rejection conditions、downstream state 和 no-write/no-legal/no-field boundary。
  - 当 AI brief、template 或 review readiness 不满足边界时，packet 自动进入 blocked 状态；当 human response preflight ready 时，只允许进入 Agent60 patch gate，仍不允许 claim text、legal opinion 或 field upgrade。
- 新增 `experiments/run_formal_search_nonlegal_review_operator_packet.py`：
  - 生成 `outputs/agent_architecture_consolidation/formal_search_nonlegal_review_operator_packet.json`。
  - 生成 `deliverables/model_core_optimization/formal_search_nonlegal_review_operator_packet.md`。
  - 回写 manifest 的 latest operator packet 指针、status、row count、high-priority count、env var 和边界字段。
- 新增 `tests/test_formal_search_nonlegal_review_operator_packet.py`：
  - 验证 waiting 状态下能正确组织 source env var、recommended output path、7 行人工 response contract、拒收条件和 validation commands。
  - 验证 AI brief 边界不完整时阻断，不会继续要求人工提交 response。
  - 验证 human response preflight ready 时也仍保持 no-claim-text、no-legal、no-field 边界。

当前结果：

- `packet_status=formal_search_nonlegal_review_operator_packet_ready_waiting_for_human_response`
- `source_env_var=FORMAL_SEARCH_NONLEGAL_REVIEW_RESPONSE_PATH`
- `recommended_output_path=outputs/agent_architecture_consolidation/formal_search_nonlegal_review_response.json`
- `expected_review_packet_row_count=7`
- `high_priority_review_row_count=1`
- `accepted_review_row_count=0`
- `can_route_to_claim_scope_patch_draft=False`

验证：

- `.venv/bin/pytest -q tests/test_formal_search_nonlegal_review_operator_packet.py`：3 passed。
- `.venv/bin/python experiments/run_formal_search_nonlegal_review_operator_packet.py`：通过，已生成 operator packet/report 并回写 manifest。
- `.venv/bin/pytest -q tests/test_formal_search_nonlegal_review_operator_packet.py tests/test_formal_search_nonlegal_review_brief.py tests/test_preliminary_formal_search_package.py tests/test_agent_architecture_consolidation_agent.py tests/test_model_core_optimization_governance_agent.py`：98 passed。
- `.venv/bin/pytest -q`：558 passed。
- `.venv/bin/python tools/build_project_codegraph.py`：`363 files / 4761 nodes / 7579 edges`。

边界：

- R8u136 只把人工非法律审查响应的提交门整理为工程接口。
- 它不生成法律意见、不生成 prior-art 结论、不生成权利要求文本、不升级 field-supported claim。
- 它不恢复模型主链，不写 actuator，不写 release gate。
- 未来即使 `FORMAL_SEARCH_NONLEGAL_REVIEW_RESPONSE_PATH` 通过 preflight，也仍必须经过 claim scope patch draft、formal counsel review、field replay/holdout 和 release gate 边界。

## 2026-06-22 R8u-135：Agent50 Consumes Formal Search AI Nonlegal Review Brief

目标：

- 承接 R8u134：AI nonlegal review brief 已生成，但 Agent50 全局治理层还没有直接消费。
- 修复治理可见性缺口：后续只读 Agent50 report、priority ranking、governance report 或 manifest 时，也应知道可保护性链已经到 AI-assisted pre-review ready。
- 保持边界：该回接不等于人工 review response，不等于法律意见，不允许 claim patch、field replay/control 或 actuator/release gate。

实现：

- 更新 `src/water_ai/agents/model_core_optimization_governance_agent.py`：
  - 新增可选输入 `formal_search_ai_nonlegal_review_brief`。
  - scorecard 新增 `formal_search_ai_nonlegal_review_brief_status`、row count、missing source row count、missing claim mapping row count、can help human review、can route to claim scope patch draft、boundary preserved 和 next operator action。
  - protectability score 仅在 brief ready 且 no-legal/no-field/no-write 边界完整时获得小幅增益。
  - blocked reason 在 formal handoff-ready 且 R8u134 brief ready 时，更新为等待 `FORMAL_SEARCH_NONLEGAL_REVIEW_RESPONSE_PATH`，而不是停留在 R8u133 的 result package handoff 描述。
- 更新 `experiments/run_agent50_model_core_governance.py`：
  - 读取 `outputs/agent_architecture_consolidation/formal_search_ai_nonlegal_review_brief.json`。
  - 将 R8u134 状态写入 Agent50 report、governance report 和 manifest 的 `latest_agent50_formal_search_ai_nonlegal_review_brief_*` 字段。
- 更新 `tests/test_model_core_optimization_governance_agent.py`：
  - 新增 R8u134 brief fixture。
  - 验证 Agent50 能消费 brief，并保持 `can_route_to_claim_scope_patch_draft=False`、boundary preserved、next operator action 指向 `FORMAL_SEARCH_NONLEGAL_REVIEW_RESPONSE_PATH`。

当前结果：

- Agent50 scorecard：
  - `formal_search_ai_nonlegal_review_brief_status=formal_search_ai_nonlegal_review_brief_ready_for_human_review`
  - `formal_search_ai_nonlegal_review_brief_row_count=7`
  - `formal_search_ai_nonlegal_review_brief_missing_source_row_count=0`
  - `formal_search_ai_nonlegal_review_brief_missing_claim_mapping_row_count=0`
  - `formal_search_ai_nonlegal_review_brief_can_help_human_review=True`
  - `formal_search_ai_nonlegal_review_brief_can_route_to_claim_scope_patch_draft=False`
  - `formal_search_ai_nonlegal_review_brief_boundary_preserved=True`
- Agent50 blocked reason 已明确：R8u134 brief 只能作为 human triage pre-review，仍需人工提交 `FORMAL_SEARCH_NONLEGAL_REVIEW_RESPONSE_PATH`。

验证：

- `.venv/bin/pytest -q tests/test_model_core_optimization_governance_agent.py`：39 passed。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：通过，已刷新 Agent50 report、governance report、priority ranking 和 manifest。
- `.venv/bin/pytest -q tests/test_model_core_optimization_governance_agent.py tests/test_formal_search_nonlegal_review_brief.py tests/test_preliminary_formal_search_package.py tests/test_agent_architecture_consolidation_agent.py`：95 passed。
- `.venv/bin/pytest -q`：555 passed。
- `.venv/bin/python tools/build_project_codegraph.py`：`359 files / 4726 nodes / 7518 edges`。

边界：

- R8u135 只增强治理层可见性。
- 它不生成 field evidence、不生成法律意见、不生成 prior-art 结论、不生成权利要求文本。
- 它不恢复 field replay/control，不写 actuator 或 release gate。

## 2026-06-22 R8u-134：Formal Search AI Nonlegal Review Brief

目标：

- 承接 R8u133：formal search result package 已通过 Agent60 source/row/validation execution，但仍必须进入人工非法律技术比较。
- 不越过人工审查门，不生成法律结论、prior-art 结论或权利要求文本。
- 把 7 个公开来源命中项压缩成一个 AI-assisted briefing，降低人工比较审查摩擦，并保留 no-write/no-field/no-legal 边界。

实现：

- 新增 `src/water_ai/formal_search_nonlegal_review_brief.py`：
  - 读取 preliminary formal search result package、Agent60 nonlegal comparison review packet 和 technical claim skeleton scaffold。
  - 逐行聚合 source URL、covered PTF feature ids、mapped TCS claim scaffolds、risk tier、overlap level、preliminary distinction、human review focus 和 preserved field validation gate。
  - 自动把 high/component/partial overlap 拆成 `high_overlap_human_review_priority`、`component_or_architecture_overlap_review`、`partial_overlap_review` 等人工审查优先级。
  - 明确 `can_route_to_claim_scope_patch_draft=False`、`human_review_completed=False`、`legal_opinion_allowed=False`、`field_claim_upgrade_allowed=False`。
- 新增 `experiments/run_formal_search_nonlegal_review_brief.py`：
  - 生成 `outputs/agent_architecture_consolidation/formal_search_ai_nonlegal_review_brief.json`。
  - 生成 `deliverables/model_core_optimization/formal_search_ai_nonlegal_review_brief.md`。
  - 回写 manifest 的 latest formal-search AI brief 指针、行数、缺口数和边界字段。
- 新增 `tests/test_formal_search_nonlegal_review_brief.py`：
  - 验证 7/7 review rows 都能映射到 source 和 claim scaffold。
  - 验证 brief 不能进入 claim scope patch draft，不能生成法律意见，不能升级 field claim，不能写 actuator/release gate。

当前结果：

- `brief_status=formal_search_ai_nonlegal_review_brief_ready_for_human_review`
- `brief_row_count=7`
- `missing_source_row_count=0`
- `missing_claim_mapping_row_count=0`
- `can_help_human_nonlegal_review=True`
- `can_route_to_claim_scope_patch_draft=False`
- `legal_opinion_allowed=False`
- `field_claim_upgrade_allowed=False`
- risk tier：
  - partial overlap：1
  - component/architecture overlap：5
  - high-overlap human-review priority：1

验证：

- `.venv/bin/pytest -q tests/test_formal_search_nonlegal_review_brief.py`：2 passed。
- `.venv/bin/python experiments/run_formal_search_nonlegal_review_brief.py`：通过，已生成 brief/report 并回写 manifest。
- `.venv/bin/pytest -q tests/test_formal_search_nonlegal_review_brief.py tests/test_preliminary_formal_search_package.py tests/test_agent_architecture_consolidation_agent.py`：56 passed。
- `.venv/bin/pytest -q`：554 passed。
- `.venv/bin/python tools/build_project_codegraph.py`：`359 files / 4711 nodes / 7503 edges`。

边界：

- R8u134 是 AI-assisted pre-review，不是人工 review response。
- 下一步仍必须由人工填写并提交 `FORMAL_SEARCH_NONLEGAL_REVIEW_RESPONSE_PATH`。
- 该 brief 不能直接触发 `formal_search_claim_scope_patch_draft`，不能输出权利要求文本，不能恢复 field replay/control，不能写 actuator 或 release gate。

## 2026-06-22 R8u-133：Preliminary Formal Search Result Package

目标：

- 遵守当前阶段门：在没有真实 focused catalyst field response 时，不继续堆内部 synthetic/template 模块。
- 转向同一阶段门允许的 `FORMAL_SEARCH_RESULT_PACKAGE_PATH` 外部通道，推进可保护性和验证治理。
- 生成一个能被 Agent60 formal search source/row/validation gate 消费的 preliminary result package，同时保持非法律、非现场、no-write 边界。

实现：

- 新增 `src/water_ai/preliminary_formal_search_package.py`：
  - 读取既有 `formal_search_execution_route_plan.json` 的 7 个 route rows。
  - 为每个 formal search work package 填入 1 条真实公开来源 hit。
  - 输出 package metadata、package manifest、prior_art_hit_table、claim_element_comparison_chart 和 fallback_claim_scope_recommendation。
  - 所有行均避免 `TODO_`、`template_only=true`、template marker、法律结论文本和 field claim 越界文本。
- 新增 `experiments/run_preliminary_formal_search_result_package.py`：
  - 生成 `outputs/agent_architecture_consolidation/preliminary_formal_search_result_package.json`。
  - 生成 `outputs/agent_architecture_consolidation/preliminary_formal_search_handoff.json`。
  - 生成 `outputs/agent_architecture_consolidation/preliminary_formal_search_result_package_validation_summary.json`。
  - 生成 `deliverables/model_core_optimization/preliminary_formal_search_result_package.md`。
  - 回写 manifest 的 latest preliminary formal search 指针和 validation 状态。
- 新增 `tests/test_preliminary_formal_search_package.py`：
  - 验证 package 能通过 Agent60 source preflight、row preflight 和 validation execution。
  - 验证 handoff 仍保持 `can_resume_model_chain=False`、`can_write_to_actuator=False`、`can_write_to_release_gate=False`、`legal_opinion_allowed=False`。
- 更新 `ModelCoreOptimizationGovernanceAgent`：
  - 当 external activation router 已显示 `R8U79_FORMAL_SEARCH_RESULT_PACKAGE` handoff ready 时，blocked reason 不再说 `FORMAL_SEARCH_RESULT_PACKAGE_PATH` 仍未提交。
  - 改为说明 formal package 已通过 source/row preflight，可进入人工非法律技术比较，但仍不能恢复 field replay/control 或输出 claim text。

当前结果：

- Preliminary package：
  - `package_status=preliminary_formal_search_result_package_complete`
  - `filled_work_package_count=7`
  - `expected_work_package_count=7`
  - `can_route_to_agent60_formal_search_preflight=True`
- Agent60 validation：
  - `formal_search_result_package_source_status=formal_search_result_package_source_ready_for_validation_gate`
  - `formal_search_result_package_row_preflight_status=formal_search_result_package_row_preflight_ready_for_validation_gate`
  - `formal_search_result_validation_execution_status=formal_search_result_validation_execution_ready_for_human_nonlegal_comparison_review`
  - `validated_hit_count=7`
  - `rejected_hit_count=0`
  - `can_enter_human_nonlegal_comparison_review=True`
  - `can_generate_prior_art_result=False`
  - `legal_opinion_allowed=False`
  - `field_claim_upgrade_allowed=False`
- External activation router / Agent50：
  - `router_status=external_activation_router_has_handoff_ready_routes`
  - `handoff_ready_route_count=1`
  - `handoff_ready_channel_ids=[R8U79_FORMAL_SEARCH_RESULT_PACKAGE]`
  - `model_chain_ready_route_count=0`
  - Agent50 仍把 `FIELD_ACTIVATION_RESPONSE_FOCUS_HANDOFF_NEXT_ACTION` 作为最高主链动作，因为 formal handoff 不能替代 focused catalyst field response。

外部来源覆盖：

- EP2414901B1：水处理监测/软测量/监督控制相关专利。
- PySensors：稀疏传感布点库。
- npj Clean Water 2025：多智能体深度强化学习污染控制。
- WaterTAP documentation：水处理 flowsheet 建模和优化。
- SciKGs：AI for Science 知识图谱综述资源。
- Nature Water 2026：多智能体 AI 催化剂发现与水净化。
- Conservative Q-Learning：离线强化学习和 replay 风险控制的相邻方法。

边界：

- R8u133 是 preliminary public-source comparison package，不是正式法律检索结论。
- 它不能生成 prior-art 结论、法律意见、权利要求文本或 field-supported claim。
- 它不能恢复 field replay/control，不能写 actuator，不能写 release gate。
- 它只把可保护性链路从“等待 formal search result package”推进到“可进入人工非法律技术比较”。

验证：

- `.venv/bin/pytest -q tests/test_preliminary_formal_search_package.py`：2 passed。
- `.venv/bin/python experiments/run_preliminary_formal_search_result_package.py`：通过，生成 package/handoff/report/validation summary 并回写 manifest。
- `FORMAL_SEARCH_RESULT_PACKAGE_PATH=... .venv/bin/python experiments/run_agent60_agent_architecture_consolidation.py`：通过，Agent60 formal search validation ready for human nonlegal comparison review。
- `FORMAL_SEARCH_RESULT_PACKAGE_PATH=... .venv/bin/python experiments/run_external_activation_router.py`：通过，router handoff-ready route count 为 1，model-chain-ready route count 为 0。
- `FORMAL_SEARCH_RESULT_PACKAGE_PATH=... .venv/bin/python experiments/run_agent50_model_core_governance.py`：通过，Agent50 消费 handoff-ready 语义并保持 focused catalyst response 为最高主链动作。
- `.venv/bin/pytest -q tests/test_preliminary_formal_search_package.py tests/test_agent_architecture_consolidation_agent.py tests/test_external_activation_router.py tests/test_model_core_optimization_governance_agent.py`：103 passed。
- `.venv/bin/pytest -q`：552 passed。
- `.venv/bin/python tools/build_project_codegraph.py`：通过，CodeGraph 为 355 files、4682 nodes、7443 edges。

## 2026-06-22 R8u-132：Core Gate Operator Packet Visibility

目标：

- 承接 R8u131，继续消除 operator packet 的读取路径碎片。
- 让 `outputs/model_core_governance/core_score_termination_gate.json` 这个核心阶段门也能直接看到 `external_activation_operator_action_packet.json` 的状态、下一动作和 no-write/no-resume 边界。
- 保持当前阶段门：packet 可见性增强不等于 field evidence 成立，也不等于恢复模型链。

实现：

- 更新 `src/water_ai/agents/model_core_optimization_governance_agent.py`：
  - 在 `next_allowed_actions.NEW_CORE_INTERFACE` 中新增 `new_core_interface_external_activation_operator_action_packet_*` 字段。
  - 在 `external_resume_conditions.new_core_interface` 中新增 `external_activation_operator_action_packet_*` 字段。
  - 字段覆盖 status、target hidden state、source env var、expected focused response row count、next operator action、boundary pass、can resume model chain、can write actuator、can write release gate。
- 更新 `tests/test_model_core_optimization_governance_agent.py`：
  - 断言 NEW_CORE_INTERFACE allowed action 能看到 operator packet。
  - 断言 external resume conditions 能看到同一份 operator packet。
  - 断言 no-write/no-resume 边界保持为 false。
- 重新运行 `experiments/run_agent50_model_core_governance.py`，刷新 core score termination gate、priority ranking、Agent50 report、governance report 和 manifest。

当前结果：

- `core_score_termination_gate.json` 已在两个关键位置暴露 operator packet：
  - `next_allowed_actions.NEW_CORE_INTERFACE`
  - `external_resume_conditions.new_core_interface`
- 当前 packet 摘要：
  - `external_activation_operator_action_packet_status=operator_packet_waiting_for_focused_catalyst_response`
  - `external_activation_operator_action_packet_target_hidden_state=catalyst_activity`
  - `external_activation_operator_action_packet_source_env_var=FOCUSED_CATALYST_RESPONSE_PATH`
  - `external_activation_operator_action_packet_expected_focused_response_row_count=6`
  - `external_activation_operator_action_packet_boundary_pass=True`
  - `external_activation_operator_action_packet_can_resume_model_chain=False`
  - `external_activation_operator_action_packet_can_write_to_actuator=False`
  - `external_activation_operator_action_packet_can_write_to_release_gate=False`

边界：

- R8u132 是核心阶段门的可见性补丁，不新增 field evidence。
- 它不替代完整 `FIELD_ACTIVATION_RESPONSE_PATH`、package assembly、external router、field replay、holdout、operator review、actuator gate 或 release gate。
- 当前下一步仍是填写 6 行 focused catalyst response，设置 `FOCUSED_CATALYST_RESPONSE_PATH`，运行 focused merge；通过后才可能进入 full response candidate 预检链。

验证：

- `.venv/bin/pytest -q tests/test_model_core_optimization_governance_agent.py`：37 passed。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：通过，已刷新核心 gate 与 manifest。
- `.venv/bin/pytest -q tests/test_external_activation_operator_packet.py tests/test_model_core_optimization_governance_agent.py tests/test_focused_catalyst_response_merge.py tests/test_field_activation_matrix.py tests/test_external_activation_router.py`：92 passed。
- `.venv/bin/pytest -q`：549 passed。
- `.venv/bin/python tools/build_project_codegraph.py`：通过，CodeGraph 为 351 files、4657 nodes、7404 edges。

## 2026-06-22 R8u-131：Agent50 Consumption of External Activation Operator Packet

目标：

- 承接 R8u130，避免 `external_activation_operator_action_packet.json` 成为孤立产物。
- 让 Agent50 scorecard、priority ranking、governance report 和 manifest latest 指针能直接看到当前 operator packet 的状态、下一动作和 no-write 边界。
- 保持阶段门语义：消费 operator packet 不等于恢复模型链，也不等于 field evidence 成立。

实现：

- 更新 `src/water_ai/agents/model_core_optimization_governance_agent.py`：
  - 新增可选输入 `external_activation_operator_action_packet`。
  - scorecard 新增 `external_activation_operator_action_packet_status`、`target_hidden_state`、`source_env_var`、`expected_focused_response_row_count`、`next_operator_action`、`boundary_pass`、`can_resume_model_chain`、`can_write_to_actuator`、`can_write_to_release_gate`。
  - `field_evidence_wait_status` 同步暴露 operator packet 摘要，便于 priority ranking 直接显示外部操作状态。
- 更新 `experiments/run_agent50_model_core_governance.py`：
  - 读取 `outputs/model_core_governance/external_activation_operator_action_packet.json`。
  - governance report、Agent50 short report 和 manifest 写入 `latest_agent50_external_activation_operator_action_packet_*` 字段。
- 更新 `tests/test_model_core_optimization_governance_agent.py`：
  - 新增 operator packet fixture。
  - 断言 Agent50 scorecard 与 wait status 能消费 packet，同时保持 no-write/no-resume 边界。

当前结果：

- Agent50 当前已消费 operator packet：
  - `external_activation_operator_action_packet_status=operator_packet_waiting_for_focused_catalyst_response`
  - `external_activation_operator_action_packet_target_hidden_state=catalyst_activity`
  - `external_activation_operator_action_packet_source_env_var=FOCUSED_CATALYST_RESPONSE_PATH`
  - `external_activation_operator_action_packet_expected_focused_response_row_count=6`
  - `external_activation_operator_action_packet_boundary_pass=True`
  - `external_activation_operator_action_packet_can_resume_model_chain=False`
  - `external_activation_operator_action_packet_can_write_to_actuator=False`
  - `external_activation_operator_action_packet_can_write_to_release_gate=False`

边界：

- R8u131 只提高 R8u130 的下游回接率和治理可见性。
- 它不生成 field evidence，不改变 `FIELD_ACTIVATION_RESPONSE_FOCUS_HANDOFF_NEXT_ACTION` 的外部阻断状态，不恢复模型链，不写 actuator 或 release gate。

验证：

- `.venv/bin/pytest -q tests/test_model_core_optimization_governance_agent.py`：37 passed。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：通过，Agent50 report/governance report/manifest 已消费 operator packet。
- `.venv/bin/pytest -q tests/test_external_activation_operator_packet.py tests/test_model_core_optimization_governance_agent.py tests/test_focused_catalyst_response_merge.py tests/test_field_activation_matrix.py tests/test_external_activation_router.py`：92 passed。
- `.venv/bin/pytest -q`：549 passed。

## 2026-06-22 R8u-130：External Activation Operator Action Packet

目标：

- 遵守当前 Agent50 阶段门：`stop_expansion_wait_for_real_field_package_or_new_core_interface`。
- 不继续堆内部 synthetic/template 模型模块，而是把最高外部动作整理成一个可机读、可执行、可拒收的 operator action packet。
- 让后续 agent 或人工不必同时扫描 core gate、router、focused repair work order、submission kit 和 focused template，就能知道当前应该填写哪 6 行、设置哪个环境变量、运行哪个预检命令、哪些边界不能越过。

实现：

- 新增 `src/water_ai/external_activation_operator_packet.py`：
  - 读取 core gate、external activation router、catalyst response submission kit、focused catalyst response merge preflight 和 focused template。
  - 输出 `packet_status`、`target_hidden_state`、`source_env_var`、`focused_template_path`、`expected_focused_response_row_count`、`minimum_matched_batch_count`、`operator_steps`、`current_commands`、`boundary_checks`、`rejection_boundaries` 和 no-write 边界。
  - 当前默认状态为 `operator_packet_waiting_for_focused_catalyst_response`。
  - 如果 focused merge 已 ready，则 packet 会切换为 `operator_packet_ready_to_set_FIELD_ACTIVATION_RESPONSE_PATH`，下一步变为设置 full response candidate 并重跑 field activation/Agent50。
- 新增 `experiments/run_external_activation_operator_packet.py`：
  - 生成 `outputs/model_core_governance/external_activation_operator_action_packet.json`。
  - 生成人读报告 `deliverables/model_core_optimization/external_activation_operator_action_packet.md`。
  - 回写 manifest 的 latest operator action packet 指针、状态、目标隐藏状态、source env var、next action 和 boundary pass。
- 新增 `tests/test_external_activation_operator_packet.py`：
  - 覆盖默认等待 focused catalyst response。
  - 覆盖 focused merge ready 后路由到 `FIELD_ACTIVATION_RESPONSE_PATH` candidate。
- 更新 `deliverables/artifact_index.md`、`notes/current_status.md` 与 `deliverables/README.md`。

当前结果：

- 当前 packet：
  - `packet_status=operator_packet_waiting_for_focused_catalyst_response`
  - `target_hidden_state=catalyst_activity`
  - `source_env_var=FOCUSED_CATALYST_RESPONSE_PATH`
  - `expected_focused_response_row_count=6`
  - `template_evidence_row_count=6`
  - `minimum_matched_batch_count=3`
  - `packet_next_operator_action=fill_outputs/catalyst_response_submission_kit/focused_catalyst_response_template.json_with_real_field_values_then_set_FOCUSED_CATALYST_RESPONSE_PATH`
- 当前命令清单：
  - `fill outputs/catalyst_response_submission_kit/focused_catalyst_response_template.json with real field values`
  - `export FOCUSED_CATALYST_RESPONSE_PATH=/absolute/path/to/filled_focused_response.json`
  - `.venv/bin/python experiments/run_focused_catalyst_response_merge.py`

边界：

- R8u130 只是外部激活操作交接，不是 field evidence。
- 它不能恢复模型链，不能写 actuator，不能写 release gate，不能解除 Agent49 catalyst guardrail，不能通过 Agent51 holdout，也不能产出 field-supported claim。
- template/TODO/sample/synthetic 行仍必须被拒收为现场证据；focused merge ready 也只表示可进入 full response candidate 预检链，不代表 full package/replay/holdout ready。

验证：

- `.venv/bin/pytest -q tests/test_external_activation_operator_packet.py`：2 passed。
- `.venv/bin/python experiments/run_external_activation_operator_packet.py`：通过，已生成 packet/report 并回写 manifest。
- `.venv/bin/pytest -q tests/test_external_activation_operator_packet.py tests/test_focused_catalyst_response_merge.py tests/test_field_activation_matrix.py tests/test_external_activation_router.py tests/test_model_core_optimization_governance_agent.py`：92 passed。
- `.venv/bin/pytest -q`：549 passed。
- `.venv/bin/python tools/build_project_codegraph.py`：通过，CodeGraph 为 351 files、4646 nodes、7393 edges。

## 2026-06-22 R8u-129：Core Gate Focus Handoff Repair Visibility

目标：

- 承接 R8u128，不新增 agent，不扩展展示层，只补齐 Agent50 核心阶段门里的 focused repair handoff 可见性。
- 解决一个读取路径不一致问题：如果后续只读取 `core_score_termination_gate.json`，应该也能知道 focused catalyst response 当前等待哪个修复动作，而不是必须再扫 handoff/router/scorecard。
- 让 `next_allowed_actions.NEW_CORE_INTERFACE`、`external_resume_conditions.new_core_interface` 和 governance scorecard 对 `FOCUSED_CATALYST_RESPONSE_PATH` repair work order 的状态保持一致。

实现：

- 更新 `src/water_ai/agents/model_core_optimization_governance_agent.py`：
  - 在 `next_allowed_actions.NEW_CORE_INTERFACE` 中新增 `new_core_interface_response_focus_handoff_repair_work_order_status`、`new_core_interface_response_focus_handoff_repair_item_count`、`new_core_interface_response_focus_handoff_repair_next_operator_action`。
  - 在 `external_resume_conditions.new_core_interface` 中新增 `response_focus_handoff_repair_work_order_status`、`response_focus_handoff_repair_item_count`、`response_focus_handoff_repair_next_operator_action`。
- 更新 `tests/test_model_core_optimization_governance_agent.py`：
  - field activation matrix 测试夹具补入 focused repair handoff status/item/action。
  - 断言 core gate NEW_CORE_INTERFACE、external resume conditions 和 governance scorecard 三处都能读取同一份 repair handoff。
- 重新运行 `experiments/run_agent50_model_core_governance.py`，刷新 Agent50 report、priority ranking、core score termination gate 和 manifest。

当前结果：

- 默认没有设置 `FOCUSED_CATALYST_RESPONSE_PATH` 时：
  - `focused_catalyst_response_repair_work_order_status=focused_catalyst_response_repair_work_order_waiting_for_external_response`
  - `focused_catalyst_response_repair_item_count=1`
  - `focused_catalyst_response_repair_next_operator_action=fill_outputs/catalyst_response_submission_kit/focused_catalyst_response_template.json_with_real_field_values_then_set_FOCUSED_CATALYST_RESPONSE_PATH`
- `outputs/model_core_governance/core_score_termination_gate.json` 已在 NEW_CORE_INTERFACE 与 external resume conditions 两处暴露上述字段。
- `deliverables/manifest.json` 同步新增 latest Agent50/field activation focus handoff repair 指针。

边界：

- R8u129 是验证治理层的可见性补丁，不是新证据源。
- 它不生成 field evidence，不合成真实 focused response，不替代 full response、package assembly、external router、field replay/holdout、operator review、actuator gate 或 release gate。
- 当前系统仍停在 `FIELD_ACTIVATION_RESPONSE_FOCUS_HANDOFF_NEXT_ACTION`：先填写 6 行 focused catalyst response，再设置 `FOCUSED_CATALYST_RESPONSE_PATH` 并运行 focused merge。

验证：

- `.venv/bin/pytest -q tests/test_model_core_optimization_governance_agent.py`：37 passed。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：通过，已刷新 core gate/priority ranking/Agent50 report/manifest。
- `.venv/bin/pytest -q tests/test_focused_catalyst_response_merge.py tests/test_field_activation_matrix.py tests/test_model_core_optimization_governance_agent.py tests/test_external_activation_router.py tests/test_soft_sensor_matrix_coupling_agent.py`：97 passed。
- `.venv/bin/pytest -q`：547 passed。
- `.venv/bin/python tools/build_project_codegraph.py`：通过，CodeGraph 为 347 files、4608 nodes、7318 edges。

## 2026-06-22 R8u-128：Focused Repair Action Handoff/Router Consumption

目标：

- 承接 R8u127 repair work order，修复“工单动作已经生成，但顶层 handoff/router 仍可能输出泛化动作”的脱节。
- 保持默认等待态的主线动作不变；只有 focused source、row、batch 或 ready candidate 已经有明确工单动作时，才用 repair action 覆盖 handoff/router 的下一步。
- 让 `FOCUSED_CATALYST_RESPONSE_PATH` 填错路径、坏 JSON 或 row/batch 阻断时，顶层直接提示具体修复动作。

实现：

- 更新 `src/water_ai/field_activation_matrix.py`：
  - `build_field_activation_response_focus_handoff()` 读取 `focused_catalyst_response_merge_preflight.focused_catalyst_response_repair_work_order`。
  - 新增 `focused_repair_work_order_status`、`focused_repair_item_count`、`focused_repair_highest_priority_repair_id`、`focused_repair_next_operator_action`。
  - `_field_activation_response_focus_handoff_next_action()` 在 repair status 不是 `not_available` 或 `waiting_for_external_response` 时，采用工单动作。
- 更新 `src/water_ai/external_activation_router.py`：
  - `_field_activation_upstream_summary()` 透出 focused repair work order 状态、item count 和 repair action。
  - router 顶层新增 `field_activation_upstream_focus_handoff_repair_work_order_status`、`field_activation_upstream_focus_handoff_repair_item_count`、`field_activation_upstream_focus_handoff_repair_next_operator_action`。
- 更新 runner：
  - `experiments/run_field_activation_matrix.py` 的 Markdown 和 manifest 接入 focus handoff repair 字段。
  - `experiments/run_external_activation_router.py` 的 Markdown 和 manifest 接入 router focused repair 字段。
  - `experiments/run_agent50_model_core_governance.py` 的 manifest 接入 Agent50 focus handoff repair 字段。
- 更新 Agent50：
  - scorecard/readiness snapshot 新增 `field_activation_response_focus_handoff_repair_work_order_status`、`field_activation_response_focus_handoff_repair_item_count`、`field_activation_response_focus_handoff_repair_next_operator_action`。
- 更新测试：
  - 默认等待 external focused response 时，handoff/router 仍输出 focused handoff 主线动作。
  - 当 focused source repair work order 阻断时，handoff/router 输出 `repair_FOCUSED_CATALYST_RESPONSE_PATH_file_path`。

当前结果：

- 当前默认仍未设置 `FOCUSED_CATALYST_RESPONSE_PATH`：
  - `field_activation_response_focus_handoff_status=field_activation_response_focus_handoff_ready_for_catalyst_activity`
  - `focused_repair_work_order_status=focused_catalyst_response_repair_work_order_waiting_for_external_response`
  - `focused_repair_item_count=1`
  - `next_operator_action=fill_focused_catalyst_response_template_then_set_FOCUSED_CATALYST_RESPONSE_PATH_and_merge_to_FIELD_ACTIVATION_RESPONSE_PATH`
- 如果后续 `FOCUSED_CATALYST_RESPONSE_PATH` 指向坏文件，focused repair work order 的 source repair action 会向上覆盖 handoff/router 下一步，减少 operator 再扫 JSON 的摩擦。

边界：

- R8u128 只做 repair action 的上游消费和顶层路由对齐。
- 它不生成 field evidence，不合成真实 focused response，不替代 full response preflight、R7 package acceptance、Agent51 holdout、Agent49 guardrail、external router、operator review、actuator gate 或 release gate。

验证：

- `.venv/bin/pytest -q tests/test_field_activation_matrix.py tests/test_external_activation_router.py`：49 passed。
- `.venv/bin/pytest -q tests/test_focused_catalyst_response_merge.py tests/test_field_activation_matrix.py tests/test_model_core_optimization_governance_agent.py tests/test_external_activation_router.py tests/test_soft_sensor_matrix_coupling_agent.py`：97 passed。
- `.venv/bin/pytest -q`：547 passed。
- `.venv/bin/python experiments/run_field_activation_matrix.py`：通过，已刷新 focus handoff repair 字段。
- `.venv/bin/python experiments/run_external_activation_router.py`：通过，已刷新 router focused repair 字段。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：通过，Agent50 已消费 focus handoff repair 字段。
- `.venv/bin/python tools/build_project_codegraph.py`：通过，CodeGraph 刷新为 347 files、4608 nodes、7318 edges。

## 2026-06-22 R8u-127：Focused Catalyst Response Repair Work Order

目标：

- 承接 R8u126 source preflight，把 `FOCUSED_CATALYST_RESPONSE_PATH` 的阻断从“可诊断”推进到“可执行修复”。
- 避免 operator/后续 agent 反复扫描 focused merge preflight 的 source、top-level、row 和 batch 细节。
- 让 focused catalyst 六行小包在没有真实 field response 时保持等待态；在 source 坏、row 坏或 batch 对齐坏时给出明确 repair item。

实现：

- 更新 `src/water_ai/focused_catalyst_response_merge.py`：
  - 新增 `REPAIR_WORK_ORDER_ID=R8u127_focused_catalyst_response_repair_work_order`。
  - 新增 `build_focused_catalyst_response_repair_work_order()`。
  - 工单统一输出 `work_order_status`、`source_preflight_status`、`merge_preflight_status`、`focused_row_count`、`blocked_focused_response_row_count`、`top_level_issue_count`、`matched_batch_count`、`minimum_matched_batch_count`、`matched_batch_deficit`、`repair_items`、`highest_priority_repair_id`、`next_operator_action` 和 no-write boundary。
  - 默认未设置 `FOCUSED_CATALYST_RESPONSE_PATH` 时只生成一个 P0 item：`FOCUSED_SOURCE_SUBMIT_RESPONSE`，不把模板六行的 TODO 自动误报成真实 row-level repair。
  - source 文件缺失/JSON 错误/root not object 时生成 source repair；row issue 映射到具体字段修复；共同 batch 不足时生成 `FOCUSED_BATCH_ALIGNMENT`。
- 更新 `experiments/run_focused_catalyst_response_merge.py`：
  - 新增 `outputs/focused_catalyst_response_merge/focused_catalyst_response_repair_work_order.json`。
  - focused merge preflight JSON 内嵌 `focused_catalyst_response_repair_work_order`，方便 Agent50 直接消费。
  - focused merge Markdown、manifest 和命令行输出接入 repair work order status/item/next action。
- 更新 `ModelCoreOptimizationGovernanceAgent` 与 `experiments/run_agent50_model_core_governance.py`：
  - scorecard 和 manifest 新增 `focused_catalyst_response_repair_work_order_status`、`focused_catalyst_response_repair_item_count`、`focused_catalyst_response_repair_highest_priority_repair_id`、`focused_catalyst_response_repair_next_operator_action`。
- 更新测试：
  - 覆盖默认等待外部 focused response、source path missing、共同 batch 不足、ready candidate 四类场景。
  - 覆盖 Agent50 对 repair work order 的消费字段。

当前结果：

- 默认未设置 `FOCUSED_CATALYST_RESPONSE_PATH` 时：
  - `source_preflight_status=focused_catalyst_response_source_using_default_template`
  - `preflight_status=focused_catalyst_response_merge_waiting_for_FOCUSED_CATALYST_RESPONSE_PATH`
  - `work_order_status=focused_catalyst_response_repair_work_order_waiting_for_external_response`
  - `repair_item_count=1`
  - `highest_priority_repair_id=FOCUSED_SOURCE_SUBMIT_RESPONSE`
  - `next_operator_action=fill_outputs/catalyst_response_submission_kit/focused_catalyst_response_template.json_with_real_field_values_then_set_FOCUSED_CATALYST_RESPONSE_PATH`
- Agent50 顶层推荐仍是 `FIELD_ACTIVATION_RESPONSE_FOCUS_HANDOFF_NEXT_ACTION`，说明本轮修复没有偏离 focused catalyst handoff 主链。

边界：

- R8u127 只生成 focused catalyst response 外部响应修复工单。
- 它不生成 field evidence，不合成真实 focused response，不替代 full response preflight、R7 package acceptance、Agent51 holdout、Agent49 guardrail、external router、operator review、actuator gate 或 release gate。

验证：

- `.venv/bin/pytest -q tests/test_focused_catalyst_response_merge.py`：4 passed。
- `.venv/bin/pytest -q tests/test_model_core_optimization_governance_agent.py`：37 passed。
- `.venv/bin/pytest -q tests/test_focused_catalyst_response_merge.py tests/test_field_activation_matrix.py tests/test_model_core_optimization_governance_agent.py tests/test_external_activation_router.py tests/test_soft_sensor_matrix_coupling_agent.py`：95 passed。
- `.venv/bin/pytest -q`：545 passed。
- `.venv/bin/python experiments/run_focused_catalyst_response_merge.py`：通过，已生成 focused source preflight、merge preflight、repair work order 和 merged candidate。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：通过，Agent50 已消费 focused repair work order。
- `.venv/bin/python tools/build_project_codegraph.py`：通过，CodeGraph 刷新为 347 files、4600 nodes、7304 edges。

## 2026-06-22 R8u-126：Focused Catalyst Response Source Preflight

目标：

- 承接 R8u125 focused handoff，继续压实 `FOCUSED_CATALYST_RESPONSE_PATH` 入口。
- 解决一个工程诊断问题：此前 focused merge runner 只用路径是否存在判断是否外部响应已提交；路径填错、JSON 语法错误或根对象不是 object 时，容易退回默认模板等待态，operator 无法分辨“未设置”和“设置错误”。
- 把 focused 外部响应源诊断变成可测试 source gate，而不是让错误在 row-level merge preflight 中混淆。

实现：

- 更新 `src/water_ai/focused_catalyst_response_merge.py`：
  - 新增 `preflight_focused_catalyst_response_source()`。
  - 输出 `source_preflight_status`、`source_load_status`、`external_response_supplied`、`using_default_template`、`can_run_merge_preflight`、row count、next operator action 和 no-write boundary。
  - `build_focused_catalyst_response_merge_preflight()` 新增可选 `source_preflight` 输入。
  - 当 source preflight 不可运行时，merge status 切到 `focused_catalyst_response_merge_blocked_at_source_preflight`，下一步为 `repair_FOCUSED_CATALYST_RESPONSE_PATH_file_or_json_shape`。
- 更新 `experiments/run_focused_catalyst_response_merge.py`：
  - 新增 `outputs/focused_catalyst_response_merge/focused_catalyst_response_source_preflight.json`。
  - source loader 区分未设置、缺文件、invalid JSON 和 root not object。
  - focused merge Markdown 和 manifest 接入 source preflight status。
- 更新 Agent50：
  - scorecard、readiness snapshot、manifest 接入 `focused_catalyst_response_source_preflight_status` 与 `focused_catalyst_response_source_can_run_merge_preflight`。
- 更新测试：
  - 默认未设置 env 时，source preflight 显示 `focused_catalyst_response_source_using_default_template` 且可运行模板 merge preflight。
  - 缺文件时，source preflight 显示 `focused_catalyst_response_source_file_missing`，merge preflight 阻断在 source preflight。
  - 成功加载 focused response 时，source preflight 显示 loaded，merge 仍可产出 full response candidate。

当前结果：

- 默认未设置 `FOCUSED_CATALYST_RESPONSE_PATH` 时：
  - `source_preflight_status=focused_catalyst_response_source_using_default_template`
  - `source_can_run_merge_preflight=True`
  - `preflight_status=focused_catalyst_response_merge_waiting_for_FOCUSED_CATALYST_RESPONSE_PATH`
  - `row_preflight_pass=False`
- 若用户设置了错误路径，系统将进入 `focused_catalyst_response_merge_blocked_at_source_preflight`，而不是继续伪装成普通等待。

边界：

- R8u126 只诊断 focused catalyst response source 是否可读、可进入 merge preflight。
- 它不生成 field evidence，不合成真实 focused response，不替代 full response preflight、field package、external router、field replay/holdout、operator review、actuator gate 或 release gate。

验证：

- `.venv/bin/pytest -q tests/test_focused_catalyst_response_merge.py tests/test_model_core_optimization_governance_agent.py`：41 passed。
- `.venv/bin/pytest -q tests/test_focused_catalyst_response_merge.py tests/test_field_activation_matrix.py tests/test_model_core_optimization_governance_agent.py tests/test_external_activation_router.py tests/test_soft_sensor_matrix_coupling_agent.py`：95 passed。
- `.venv/bin/pytest -q`：545 passed。
- `.venv/bin/python experiments/run_focused_catalyst_response_merge.py`：通过，已生成 source preflight。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：通过，Agent50 已消费 focused source preflight。
- `.venv/bin/python tools/build_project_codegraph.py`：通过，CodeGraph 刷新为 347 files、4584 nodes、7287 edges。

## 2026-06-22 R8u-125：Field Activation Response Focus Handoff

目标：

- 承接 R8u124 的 completion ledger，把 `next_hidden_state_focus=catalyst_activity` 转成更小、更可执行的下一步。
- 修复治理层仍推荐全量 `FIELD_ACTIVATION_RESPONSE_PATH` 填写的问题；在已有 R8u111 focused catalyst submission kit 与 R8u112 focused merge preflight 的基础上，把 33 行 full response 缩成 6 行 catalyst activity 外部响应 handoff。
- 保持 no-write 和 field validation 边界，只降低外部 operator 填报与采集摩擦，不制造现场结论。

实现：

- 更新 `src/water_ai/field_activation_matrix.py`：
  - 新增 `build_field_activation_response_focus_handoff()`。
  - 当 completion ledger 的下一焦点为 `catalyst_activity` 且 focused kit ready 时，输出 `field_activation_response_focus_handoff_ready_for_catalyst_activity`。
  - 输出 focused template/schema/merge plan 路径、`FOCUSED_CATALYST_RESPONSE_PATH`、full response env var、row scan reduction、下一 operator action 和 no-write boundary。
- 更新 `experiments/run_field_activation_matrix.py`：
  - 读取 `outputs/catalyst_response_submission_kit/catalyst_response_submission_kit_metrics.json` 与 `outputs/focused_catalyst_response_merge/focused_catalyst_response_merge_preflight.json`。
  - 新增输出 `outputs/model_core_governance/field_activation_response_focus_handoff.json`。
  - `field_activation_matrix.json`、Markdown 和 manifest latest 指针接入 focus handoff。
- 更新 `ModelCoreOptimizationGovernanceAgent` 与 `experiments/run_agent50_model_core_governance.py`：
  - Agent50 scorecard、new core interface 摘要、external resume 条件、readiness snapshot、governance report、Agent50 report 和 manifest 接入 focus handoff 字段。
  - `_recommended_next_core_action()` 在 focused handoff ready 时优先返回 `FIELD_ACTIVATION_RESPONSE_FOCUS_HANDOFF_NEXT_ACTION`，只有无 focused handoff 时才回退到 full submission packet。
- 更新 `src/water_ai/external_activation_router.py` 与 `experiments/run_external_activation_router.py`：
  - external activation router 读取 `field_activation_response_focus_handoff.json`。
  - 当 field activation upstream 尚未 ready 但 focused handoff ready 时，R7 route row 和 router 顶层 `next_operator_action` 也切换为 focused handoff，避免 router 与 Agent50 推荐不一致。
  - manifest 和 router Markdown 接入 focus handoff status、target hidden state 和 source env var。
- 更新测试：
  - 默认模板必须路由到 catalyst 6 行小包。
  - catalyst 组已补完时，handoff 不再误路由，转回全量 response 其他 hidden state。
  - full response 填完时，handoff 自动退出并进入 package assembly staging。
  - Agent50 必须把 focused handoff 暴露进 scorecard，并把推荐动作切到 focused handoff。
  - external activation router 必须优先返回 focused handoff action，而不是旧的 full-response action。

当前结果：

- 默认无外部 response 时：
  - `handoff_status=field_activation_response_focus_handoff_ready_for_catalyst_activity`
  - `target_hidden_state=catalyst_activity`
  - `focused_response_row_count=6`
  - `full_response_expected_row_count=33`
  - `row_scan_reduction_ratio=0.818`
  - `focused_merge_source_env_var=FOCUSED_CATALYST_RESPONSE_PATH`
  - Agent50 推荐：`FIELD_ACTIVATION_RESPONSE_FOCUS_HANDOFF_NEXT_ACTION`
- 下一步实际动作：
  - 填写 `outputs/catalyst_response_submission_kit/focused_catalyst_response_template.json` 的 6 行真实 field provenance。
  - 设置 `FOCUSED_CATALYST_RESPONSE_PATH=/path/to/filled_focused_catalyst_response.json`。
  - 运行 `.venv/bin/python experiments/run_focused_catalyst_response_merge.py`。
  - 若 merge 预检通过，再把合并候选作为 `FIELD_ACTIVATION_RESPONSE_PATH` 重跑 field activation 与 Agent50。

边界：

- R8u125 只是 focused operator handoff。
- 它不能替代完整 33 行 full field activation response，不能替代 materialized package preflight、external activation router、field replay/holdout、operator review、actuator gate 或 release gate。
- 它不生成 field evidence，不恢复模型链，不解除 Agent49 catalyst guardrail，不写 actuator 或 release gate。

验证：

- `.venv/bin/pytest -q tests/test_field_activation_matrix.py`：37 passed。
- `.venv/bin/pytest -q tests/test_model_core_optimization_governance_agent.py`：37 passed。
- `.venv/bin/pytest -q tests/test_external_activation_router.py`：10 passed。
- `.venv/bin/pytest -q tests/test_field_activation_matrix.py tests/test_model_core_optimization_governance_agent.py`：74 passed。
- `.venv/bin/pytest -q tests/test_field_activation_matrix.py tests/test_model_core_optimization_governance_agent.py tests/test_external_activation_router.py tests/test_soft_sensor_matrix_coupling_agent.py`：91 passed。
- `.venv/bin/pytest -q`：544 passed。
- `.venv/bin/python experiments/run_field_activation_matrix.py`：通过，已生成 focus handoff。
- `.venv/bin/python experiments/run_external_activation_router.py`：通过，router 下一步已切到 focused handoff。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：通过，Agent50 推荐已切到 focused handoff。
- `.venv/bin/python tools/build_project_codegraph.py`：通过，CodeGraph 刷新为 347 files、4576 nodes、7275 edges。

## 2026-06-22 R8u-124：Field Activation Response Completion Ledger

目标：

- 承接 R8u123 的下游 preview 语义修正，继续压实当前最高阻断 `FIELD_ACTIVATION_RESPONSE_PATH`。
- 解决一个工程接口问题：response template、preflight、repair work order、coherence audit 和 downstream preview 已经存在，但外部响应的完成度仍分散在多个文件里。
- 把“33 行外部响应到底填到什么程度、哪个 hidden_state 先补、哪些 issue scope 仍阻断”变成可计算账本，而不是靠人工翻 JSON。

实现：

- 更新 `src/water_ai/field_activation_matrix.py`：
  - 新增 `build_field_activation_response_completion_ledger()`。
  - 按响应行判断 `missing_response_row`、`template_marker`、`non_field_origin`、`unsupported_channel`、`missing_alignment`、`missing_value_payload`、`template_value_payload`、`no_write_unconfirmed` 等 issue scopes。
  - 按 hidden_state 聚合 expected/provided/completed/incomplete rows、completion ratio、top issue scopes 和 next operator action。
  - 按 table 聚合完成度，便于后续从状态级响应继续落到 CSV package。
  - `next_hidden_state_focus` 在未补完时优先指向 `catalyst_activity`，因为它仍是当前弱观测核心状态。
- 更新 `experiments/run_field_activation_matrix.py`：
  - 新增输出 `outputs/model_core_governance/field_activation_response_completion_ledger.json`。
  - `field_activation_matrix.json`、Markdown 和 manifest latest 指针接入 completion ledger status、ratio、completed/incomplete row count、next hidden-state focus 和 next action。
- 更新 `ModelCoreOptimizationGovernanceAgent` 与 `experiments/run_agent50_model_core_governance.py`：
  - Agent50 scorecard、new core interface 摘要、external resume 条件、governance report、Agent50 report 和 manifest 接入 completion ledger。
- 更新 `tests/test_field_activation_matrix.py`：
  - 默认模板必须显示 0% 完成、`waiting_for_external_response`、next focus 为 `catalyst_activity`。
  - 只补 catalyst 行时必须显示局部完成，catalyst 组完成，下一焦点转向其他未补状态。
  - 全量填充响应时必须显示 100% 完成，并保持 no-write 边界。

当前结果：

- 默认无外部 response 时：
  - `ledger_status=field_activation_response_completion_waiting_for_external_response`
  - `completion_ratio=0.0`
  - `completed_response_row_count=0`
  - `incomplete_response_row_count=33`
  - `next_hidden_state_focus=catalyst_activity`
  - `next_operator_action=copy_template_fill_real_field_values_and_set_FIELD_ACTIVATION_RESPONSE_PATH`
- Agent50 与 manifest 已消费该状态，当前全局推荐仍正确保持为 `FIELD_ACTIVATION_RESPONSE_SUBMISSION_PACKET_NEXT_ACTION`。

边界：

- R8u124 只衡量外部响应填写进度和机器可读性。
- 它不生成 field evidence，不运行 replay/holdout，不恢复模型链，不写 actuator 或 release gate。
- 即使 completion ledger 达到 100%，也只表示可以进入 response preflight/package assembly/materialized package/downstream preview，不能直接升级现场结论。

验证：

- `.venv/bin/pytest -q tests/test_field_activation_matrix.py`：34 passed。
- `.venv/bin/python experiments/run_field_activation_matrix.py`：通过，已生成 response completion ledger。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：通过，Agent50 已消费 completion ledger。
- `.venv/bin/pytest -q tests/test_field_activation_matrix.py tests/test_model_core_optimization_governance_agent.py`：71 passed。
- `.venv/bin/pytest -q tests/test_field_activation_matrix.py tests/test_model_core_optimization_governance_agent.py tests/test_external_activation_router.py tests/test_soft_sensor_matrix_coupling_agent.py`：88 passed。
- `.venv/bin/pytest -q`：541 passed。
- `.venv/bin/python tools/build_project_codegraph.py`：通过，CodeGraph 刷新为 347 files、4559 nodes、7244 edges。

## 2026-06-22 R8u-123：Downstream Preview Deferred Metric Semantics Fix

目标：

- 修复 R8u121/R8u122 preview 未执行时的指标语义风险。
- 当 materialized package preflight 未 ready 时，R7/Agent44 与 path/endpoint downstream preflight 实际没有运行；此时若只显示 count=0，容易被误读为“下游缺口为 0”。
- 让默认等待态明确表达“未评估”，而不是“已通过或无缺口”。

实现：

- 更新 `src/water_ai/field_activation_matrix.py`：
  - R7 preview 与 path/endpoint preview 均新增 `preview_metric_evaluation_status`。
  - 未执行 preview 时新增 `not_evaluated_metric_names`，列出不能解释为已评估的下游指标。
  - 新增 `_downstream_preview_metric_evaluation_status()`，统一区分 materialized package 未 ready、package dir 未设置、不适用和已执行。
  - path/endpoint preview 在未执行时仍暴露合同门槛：`path_endpoint_required_table_count=6` 与 `path_endpoint_contract_minimum_matched_batch_count=5`。
- 更新 `experiments/run_field_activation_matrix.py`：
  - Markdown 与 manifest latest 指针接入 metric evaluation status、not evaluated count、path/endpoint required table count 和 minimum matched batch count。
- 更新 `ModelCoreOptimizationGovernanceAgent` 与 `experiments/run_agent50_model_core_governance.py`：
  - Agent50 scorecard、new core interface 摘要、external resume 摘要、governance report 和 manifest 接入 deferred metric semantics。
- 更新 `tests/test_field_activation_matrix.py`：
  - 默认等待态必须显示 `deferred_until_materialized_package_preflight_ready`。
  - 默认等待态必须列出未评估指标。
  - 执行态必须显示 metrics evaluated 且 `not_evaluated_metric_names=[]`。

当前结果：

- 默认无外部 response 时：
  - R7 preview:
    - `preview_metric_evaluation_status=deferred_until_materialized_package_preflight_ready`
    - `not_evaluated_metric_names` 覆盖 R7 preflight/import/type/linkage/can-pass 指标。
  - path/endpoint preview:
    - `preview_metric_evaluation_status=deferred_until_materialized_package_preflight_ready`
    - `not_evaluated_metric_names` 覆盖 matched batch、deficit、alignment、required fields、layout holdout 等指标。
    - `path_endpoint_required_table_count=6`
    - `path_endpoint_contract_minimum_matched_batch_count=5`

边界：

- R8u123 只修复未评估指标的语义边界。
- 它不执行 downstream preflight，不生成 field evidence，不运行 replay/holdout，不恢复模型链，不写 actuator 或 release gate。

验证：

- `.venv/bin/pytest -q tests/test_field_activation_matrix.py tests/test_model_core_optimization_governance_agent.py`：68 passed。
- `.venv/bin/python experiments/run_field_activation_matrix.py`：通过，已刷新 preview metric semantics。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：通过，Agent50 已消费 deferred metric semantics。
- `.venv/bin/pytest -q tests/test_field_activation_matrix.py tests/test_model_core_optimization_governance_agent.py tests/test_external_activation_router.py tests/test_soft_sensor_matrix_coupling_agent.py`：85 passed。
- `.venv/bin/pytest -q`：538 passed。
- `.venv/bin/python tools/build_project_codegraph.py`：通过，CodeGraph 刷新为 347 files、4535 nodes、7220 edges。

## 2026-06-22 R8u-122：Field Activation Downstream Path/Endpoint Preflight Preview

目标：

- 承接 R8u121 的 downstream no-write preview。
- R8u121 只照 R7/Agent44 import gate；但同一个 materialized package 还可能卡在 R8u66/Agent54 path-endpoint label gate。
- 提前暴露路径阶段、最终出水终点标签、共同 batch、operation log、offline lab rows 与 release gate endpoint 证据缺口。

实现：

- 更新 `src/water_ai/field_activation_matrix.py`：
  - 新增 `preview_field_activation_downstream_path_endpoint_preflight(staging_manifest, materialized_package_preflight, package_dir_path=...)`。
  - R8u105 未通过时，preview 阻断在 materialized package preflight，并沿用上游最高阻断和 next action。
  - R8u105 通过且 staging 中存在 path/endpoint preview scope 时，读取 materialized package 的 required path/endpoint CSV。
  - 复用 `preflight_field_path_endpoint_label_package()`，不重写 Agent54 规则。
  - 输出 path_endpoint preflight status、matched batch count、minimum/deficit、batch alignment gap、template marker、required field gap、alignment patch plan、highest blocker 与 next action。
  - preview 即使看到 path/endpoint ready，也保持 `can_resume_model_chain=False`、`can_write_to_actuator=False`、`can_write_to_release_gate=False`。
- 更新 `experiments/run_field_activation_matrix.py`：
  - 新增输出 `outputs/model_core_governance/field_activation_downstream_path_endpoint_preview.json`。
  - `field_activation_matrix.json`、Markdown 和 manifest latest 指针接入 R8u122 preview 状态。
- 更新 `ModelCoreOptimizationGovernanceAgent` 与 `experiments/run_agent50_model_core_governance.py`：
  - Agent50 scorecard、new core interface 摘要、external resume 摘要和 manifest 接入 downstream path/endpoint preview 字段。
- 更新 `tests/test_field_activation_matrix.py`：
  - 默认 materialized package 未 ready 时，preview 不运行 Agent54。
  - ready materialized package 会执行 path/endpoint preview，并暴露 Agent54/R8u66 阻断，同时保持 no-write。

当前结果：

- 默认无外部 response 时：
  - `outputs/model_core_governance/field_activation_downstream_path_endpoint_preview.json`
    - `preview_status=field_activation_downstream_path_endpoint_preview_blocked_by_materialized_package_preflight`
    - `preview_executed=False`
    - `path_endpoint_preflight_status=path_endpoint_preflight_not_run`
    - `highest_priority_blocker=R8U105_STAGING_MANIFEST_NOT_READY`
    - `downstream_path_endpoint_can_route_to_field_layout_holdout=False`
- 测试中的 ready materialized package 路径：
  - R8u105 可通过。
  - R8u122 会实际调用 R8u66/Agent54 path-endpoint label preflight。
  - 当前由 staging response 生成的包仍会被 path/endpoint preflight 阻断，说明“外部包物化可提交”与“路径/终点标签可进入 field layout holdout”是两道不同门。

边界：

- R8u122 只做下游 R8u66/Agent54 read-only preview。
- 它不运行 layout holdout、timestamped replay、field evidence chain、control replay、actuator writeback 或 release gate。
- 它不能恢复模型链、不能写 actuator、不能写 release gate，也不能把 synthetic/test package 写成 field-supported claim。

验证：

- `.venv/bin/pytest -q tests/test_field_activation_matrix.py`：31 passed。
- `.venv/bin/pytest -q tests/test_field_activation_matrix.py tests/test_model_core_optimization_governance_agent.py`：68 passed。
- `.venv/bin/python experiments/run_field_activation_matrix.py`：通过，已生成 downstream path/endpoint preview。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：通过，Agent50 已消费 preview 状态。
- `.venv/bin/pytest -q tests/test_field_activation_matrix.py tests/test_model_core_optimization_governance_agent.py tests/test_external_activation_router.py tests/test_soft_sensor_matrix_coupling_agent.py`：85 passed。
- `.venv/bin/pytest -q`：538 passed。
- `.venv/bin/python tools/build_project_codegraph.py`：通过，CodeGraph 刷新为 347 files、4528 nodes、7213 edges。

## 2026-06-22 R8u-121：Field Activation Downstream R7 Preflight Preview

目标：

- 承接 R8u120 的 row blueprint gate，检查 operator 物化包通过 R8u105 后，下游 R7/Agent44 是否真的能导入。
- 防止把 `field_activation_materialized_package_preflight_ready_for_external_activation_router` 误读成 `field_package_preflight_ready_for_agent42`。
- 在不恢复模型链、不运行 replay/holdout 的前提下，提前暴露 R7 文件/表头/真实行/类型/batch linkage 断点。

实现：

- 更新 `src/water_ai/field_activation_matrix.py`：
  - 新增 `preview_field_activation_downstream_r7_preflight(staging_manifest, materialized_package_preflight, package_dir_path=...)`。
  - 当 R8u105 未通过时，preview 阻断在 materialized package preflight，并沿用上游最高阻断和 next action。
  - 当 R8u105 通过且通道为 `R7_REAL_FIELD_PACKAGE`/`REAL_FIELD_REPLAY_PACKAGE_DIR` 时，只读调用 `preflight_field_replay_package()`。
  - 输出 R7 preflight status、Agent44 import status、files/rows ready、placeholder metadata、type error、required field blockers、batch linkage blockers、highest blocker 与 next action。
  - preview 即使看到 R7 would pass，也保持 `can_resume_model_chain=False`、`can_write_to_actuator=False`、`can_write_to_release_gate=False`。
- 更新 `experiments/run_field_activation_matrix.py`：
  - 新增输出 `outputs/model_core_governance/field_activation_downstream_r7_preview.json`。
  - `field_activation_matrix.json`、Markdown 和 manifest latest 指针接入 R8u121 preview 状态。
- 更新 `ModelCoreOptimizationGovernanceAgent` 与 `experiments/run_agent50_model_core_governance.py`：
  - Agent50 scorecard、new core interface 摘要、external resume 摘要和 manifest 接入 downstream R7 preview 字段。
- 更新 `tests/test_field_activation_matrix.py`：
  - 默认 materialized package 未 ready 时，preview 不运行 R7。
  - ready materialized package 会执行 R7 preview，并暴露 Agent44/R7 阻断，同时保持 no-write。

当前结果：

- 默认无外部 response 时：
  - `outputs/model_core_governance/field_activation_downstream_r7_preview.json`
    - `preview_status=field_activation_downstream_r7_preview_blocked_by_materialized_package_preflight`
    - `preview_executed=False`
    - `r7_preflight_status=r7_preflight_not_run`
    - `highest_priority_blocker=R8U105_STAGING_MANIFEST_NOT_READY`
    - `downstream_r7_can_pass_to_timestamped_replay=False`
- 测试中的 ready materialized package 路径：
  - R8u105 可通过。
  - R8u121 会实际调用 R7/Agent44 preflight。
  - 当前由 staging response 生成的包仍会被 R7 阻断，说明“上游包物化可提交”与“完整 R7 replay 包可进入 Agent42”是两道不同门。

边界：

- R8u121 只做下游 R7/Agent44 read-only preview。
- 它不运行 Agent42 replay、Agent43 G6/P6、Agent45 evidence chain、Agent46 holdout、Agent49 控制或 release gate。
- 它不能恢复模型链、不能写 actuator、不能写 release gate，也不能把 synthetic/test package 写成 field-supported claim。

验证：

- `.venv/bin/pytest -q tests/test_field_activation_matrix.py`：29 passed。
- `.venv/bin/pytest -q tests/test_model_core_optimization_governance_agent.py`：37 passed。
- `.venv/bin/python experiments/run_field_activation_matrix.py`：通过，已生成 downstream R7 preview。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：通过，Agent50 已消费 preview 状态。
- `.venv/bin/pytest -q tests/test_field_activation_matrix.py tests/test_model_core_optimization_governance_agent.py tests/test_external_activation_router.py`：76 passed。
- `.venv/bin/pytest -q`：536 passed。
- `.venv/bin/python tools/build_project_codegraph.py`：通过，CodeGraph 刷新为 347 files、4511 nodes、7191 edges。

## 2026-06-22 R8u-120：Field Activation Package Row Blueprint Gate

目标：

- 承接 R8u119 的 `evidence_value` 值本体合同。
- 修复 response 到 materialized package 的下一段接口断点：staging manifest 过去只告诉 operator 要建哪些表、哪些列、哪些 source response rows，但没有说明每个 `evidence_value` 应进入哪一张 CSV、哪一列、哪一行。
- 防止“response 中已有机器可读值，但 operator 物化 CSV 时丢失、错填或用泛化占位值”的包进入 external activation router。

实现：

- 更新 `src/water_ai/field_activation_matrix.py`：
  - `_table_assembly()` 保留 `source_response_rows`，包括 `response_row_id`、hidden state、required evidence、table/field、alignment keys、`evidence_value_reference`、`evidence_value` 和 custody/operator。
  - `_staging_table_manifest()` 新增 `value_payload_mappings` 与 `row_blueprints`。
  - `build_field_activation_package_staging_manifest()` 顶层新增 `selected_row_blueprint_count` 与 `selected_value_payload_mapping_count`。
  - `preflight_field_activation_materialized_package()` 与 `_materialized_table_audit()` 新增 blueprint 匹配审计，输出 `blueprint_expected_row_count`、`blueprint_matched_row_count` 和 `blueprint_missing_row_count`。
  - 若 CSV 不能匹配 staging row blueprint，新增阻断 `R8U105_TABLE_BLUEPRINT_ROWS_MISSING`。
  - materialized CSV 的 template marker 检查改为身份列严格、动态 payload 列由 blueprint 匹配保证，避免把宽表中非本行 payload 的空白列误判为 TODO。
- 更新 `ModelCoreOptimizationGovernanceAgent`：
  - scorecard、new core interface、external resume conditions 新增 package staging blueprint count、value payload mapping count 和 materialized blueprint missing row count。
- 更新 `experiments/run_field_activation_matrix.py` 与 `experiments/run_agent50_model_core_governance.py`：
  - field activation Markdown 与 manifest latest 指针输出 row blueprint / materialized blueprint 指标。
- 更新 `tests/test_field_activation_matrix.py`：
  - ready response 后 staging manifest 必须生成 row blueprints 和 value payload mappings。
  - materialized package helper 改为从 row blueprints 写 CSV。
  - 新增故意改错 CSV payload 的阻断测试，要求触发 `R8U105_TABLE_BLUEPRINT_ROWS_MISSING`。

当前结果：

- 默认无外部 response 时：
  - `outputs/model_core_governance/field_activation_package_staging_manifest.json`
    - `selected_row_blueprint_count=0`
    - `selected_value_payload_mapping_count=0`
  - `outputs/model_core_governance/field_activation_materialized_package_preflight.json`
    - `blueprint_expected_row_count=0`
    - `blueprint_missing_row_count=0`
    - 仍阻断在 `R8U105_STAGING_MANIFEST_NOT_READY`
- 测试中的 ready response 路径：
  - staging manifest 能生成 row blueprints。
  - operator materialized CSV 若按蓝图写入，则 materialized package preflight 通过。
  - CSV 若未承接 payload，则 materialized package preflight 阻断。

边界：

- R8u120 只生成 no-write CSV 行蓝图并检查 operator 物化包是否承接 response payload。
- 它不生成 field evidence，不证明 payload 真实、准确或可作为 field-supported claim。
- 即使 materialized package preflight 通过，也仍需 external activation router、R7/Agent44 或 Agent54 preflight、field replay/holdout 和人工复核。
- 不能写 actuator，不能写 release gate。

验证：

- `.venv/bin/python -m py_compile src/water_ai/field_activation_matrix.py src/water_ai/agents/model_core_optimization_governance_agent.py experiments/run_field_activation_matrix.py experiments/run_agent50_model_core_governance.py tests/test_field_activation_matrix.py tests/test_model_core_optimization_governance_agent.py`：通过。
- `.venv/bin/pytest -q tests/test_field_activation_matrix.py`：27 passed。
- `.venv/bin/pytest -q tests/test_field_activation_matrix.py tests/test_model_core_optimization_governance_agent.py -k "field_activation"`：29 passed, 35 deselected。
- `.venv/bin/python experiments/run_field_activation_matrix.py`：通过。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：通过。
- `.venv/bin/python experiments/run_external_activation_router.py`：通过。
- `.venv/bin/pytest -q`：534 passed。

## 2026-06-22 R8u-119：Field Activation Response Value Payload Contract

目标：

- 承接 R8u118 的阶段门控语义修正，继续压实 `FIELD_ACTIVATION_RESPONSE_PATH` 的真实外部响应入口。
- 发现一个工程 replay 风险：response 行此前要求 `evidence_value_reference`，能说明值来自哪张表/哪列/哪个文件，但没有显式要求 operator 提供可计算的实际值 payload。
- 如果不修，后续可能出现“行级 provenance、batch、timestamp、node、sensor 都填满，但没有实际 measured value / label / event flag / JSON payload”的响应包，造成 package assembly 或 replay 阶段返工。

实现：

- 更新 `src/water_ai/field_activation_matrix.py`：
  - `RESPONSE_ROW_REQUIRED_FIELDS` 新增 `evidence_value`。
  - `build_field_activation_response_template()` 的每行新增 `evidence_value=TODO_actual_field_value_or_json_payload`。
  - `preflight_field_activation_response()` 新增 `missing_value_payload_row_count` 与 `template_value_payload_row_count`。
  - response ready 条件新增 value payload 门控：缺少 `evidence_value` 或 `evidence_value` 仍为 TODO/template/sample/null 时，不能进入 external package preflight。
  - `build_field_activation_response_repair_work_order()` 新增 `R8U102_FILL_VALUE_PAYLOAD` 和 `R8U102_REPLACE_VALUE_PAYLOAD_TEMPLATE` 修复项。
- 更新 `ModelCoreOptimizationGovernanceAgent`：
  - scorecard、new core interface、external resume conditions 新增 `field_activation_response_missing_value_payload_row_count` 和 `field_activation_response_template_value_payload_row_count`。
- 更新 `experiments/run_field_activation_matrix.py` 与 `experiments/run_agent50_model_core_governance.py`：
  - field activation Markdown、Agent50 payload 和 manifest latest 指针输出 value payload 门控指标。
- 更新 `tests/test_field_activation_matrix.py` 与 `tests/test_model_core_optimization_governance_agent.py`：
  - 默认模板要求 `template_value_payload_row_count=33`。
  - 新增“只有 `evidence_value_reference`、没有 `evidence_value`”的阻断测试。
  - 已填满响应的测试统一填入 `evidence_value` 后才允许通过 response preflight。

当前结果：

- `outputs/model_core_governance/field_activation_response_template.json`：
  - 33 行 evidence rows 均包含 `evidence_value` 字段。
- `outputs/model_core_governance/field_activation_response_preflight.json`：
  - `preflight_status=field_activation_response_blocked_before_external_package_preflight`
  - `missing_value_payload_row_count=0`
  - `template_value_payload_row_count=33`
- `outputs/model_core_governance/field_activation_response_repair_work_order.json`：
  - `repair_item_count=7`
  - 新增 field value payload 修复项。
- `outputs/model_core_governance/field_activation_response_submission_packet.json`：
  - `required_evidence_row_fields` 包含 `evidence_value`。
  - `top_repair_items` 包含 `R8U102_REPLACE_VALUE_PAYLOAD_TEMPLATE`。
- `outputs/agent50_model_core_governance/agent50_report.json` 与 `deliverables/manifest.json`：
  - `field_activation_response_missing_value_payload_row_count=0`
  - `field_activation_response_template_value_payload_row_count=33`

边界：

- R8u119 只要求 response 行具备机器可读值 payload，不证明 payload 真实、准确或可作为 field evidence。
- 即使 value payload 门控通过，也仍必须继续通过 response coherence audit、package assembly、staging manifest、materialized package preflight、external activation router、R7/Agent44 或 Agent54 preflight、field replay/holdout 和人工复核。
- 该轮不生成 field evidence、不运行 replay/holdout、不恢复模型链、不写 actuator、不写 release gate。

验证：

- `.venv/bin/python -m py_compile src/water_ai/field_activation_matrix.py src/water_ai/agents/model_core_optimization_governance_agent.py experiments/run_field_activation_matrix.py experiments/run_agent50_model_core_governance.py tests/test_field_activation_matrix.py tests/test_model_core_optimization_governance_agent.py`：通过。
- `.venv/bin/pytest -q tests/test_field_activation_matrix.py`：26 passed。
- `.venv/bin/pytest -q tests/test_field_activation_matrix.py tests/test_model_core_optimization_governance_agent.py -k "field_activation"`：28 passed, 35 deselected。
- `.venv/bin/python experiments/run_field_activation_matrix.py`：通过。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：通过。
- `.venv/bin/python experiments/run_external_activation_router.py`：通过。

## 2026-06-22 R8u-118：Field Activation Coherence Gate Semantics Fix

目标：

- 复核 R8u117 产物后，发现 coherence audit 的等待态存在可解释性问题：默认未提交 `FIELD_ACTIVATION_RESPONSE_PATH` 时，状态是 `field_activation_response_coherence_audit_waiting_for_response_preflight`，但由于 audit 已扫描模板行，`hard_blocker_count` 仍会统计 timestamp/node/sensor/method 等模板缺口。
- 这会让后续 agent 或 operator 误以为“coherence audit 已经发现 30 个硬阻断”，而真实第一阻断应是 `response_source` / `response_preflight`，即先提交填写后的外部 response JSON。
- 本轮只修复阶段门控归因，避免前置模板阻断污染后置 coherence 审计。

实现：

- 更新 `src/water_ai/field_activation_matrix.py`：
  - `audit_field_activation_response_coherence()` 在 `response_preflight.can_route_to_external_activation_router=False` 时，将 `blockers` 和 `warnings` 清空。
  - 新增 `audit_execution_status`：
    - `coherence_checks_deferred_until_response_preflight_ready`
    - `coherence_checks_executed`
  - 只有外部 response 行级 preflight ready 后，才把 batch/node/sensor/custody/method 问题计入 hard blockers。
- 更新 `tests/test_field_activation_matrix.py`：
  - `test_field_activation_response_coherence_audit_waits_for_response_preflight` 现在要求 waiting 状态下 `hard_blocker_count=0`、`warning_count=0`、`highest_priority_blocker=""`、`blockers=[]`、`warnings=[]`。
- 刷新：
  - `experiments/run_field_activation_matrix.py`
  - `experiments/run_agent50_model_core_governance.py`
  - `experiments/run_external_activation_router.py`

当前结果：

- `outputs/model_core_governance/field_activation_response_coherence_audit.json`：
  - `audit_status=field_activation_response_coherence_audit_waiting_for_response_preflight`
  - `audit_execution_status=coherence_checks_deferred_until_response_preflight_ready`
  - `hard_blocker_count=0`
  - `warning_count=0`
  - `can_route_to_package_assembly=False`
- `outputs/model_core_governance/field_activation_package_assembly_plan.json`：
  - `response_coherence_hard_blocker_count=0`
  - 当前仍正确阻断在 `field_activation_package_assembly_plan_blocked_by_response_preflight`。
- `outputs/agent50_model_core_governance/agent50_report.json`：
  - `field_activation_response_coherence_hard_blocker_count=0`
  - `recommended_next_core_action.task_id=FIELD_ACTIVATION_RESPONSE_SUBMISSION_PACKET_NEXT_ACTION`
- `outputs/model_core_governance/external_activation_router.json`：
  - `next_operator_action=fill_response_template_and_set_FIELD_ACTIVATION_RESPONSE_PATH`

边界：

- R8u118 不新增现场证据入口，不生成 field evidence，不恢复模型链，不写 actuator，不写 release gate。
- 它只让阶段门控更诚实：先解决 response source/preflight，再执行 coherence hard blocker 审计。

验证：

- `.venv/bin/python -m py_compile src/water_ai/field_activation_matrix.py tests/test_field_activation_matrix.py`：通过。
- `.venv/bin/pytest -q tests/test_field_activation_matrix.py`：25 passed。
- `.venv/bin/pytest -q tests/test_field_activation_matrix.py tests/test_model_core_optimization_governance_agent.py -k "field_activation"`：27 passed, 35 deselected。
- `.venv/bin/python experiments/run_field_activation_matrix.py`：通过。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：通过。
- `.venv/bin/python experiments/run_external_activation_router.py`：通过。
- `.venv/bin/pytest -q`：532 passed。
- `.venv/bin/python tools/build_project_codegraph.py`：通过，CodeGraph 为 347 files、4481 nodes、7156 edges。

## 2026-06-22 R8u-117：Field Activation Response Coherence Audit

目标：

- 承接 R8u116 的 field activation upstream 顺序门。
- 不再继续堆叠内部 synthetic/template 产物，而是把真实外部响应入口做得更工程化：即使 operator 填写了 `FIELD_ACTIVATION_RESPONSE_PATH`，系统也要先确认这些行是否能按 batch、node、sensor、chain-of-custody 和 lab method 组成可回放证据组。
- 防止“行级字段都填满，但同一 hidden state 的证据不能拼成 replay/holdout 输入”的响应继续进入 package assembly、materialized package preflight 和 external activation router。

实现：

- 更新 `src/water_ai/field_activation_matrix.py`：
  - 新增 `audit_field_activation_response_coherence(response, matrix, response_preflight)`。
  - 对每个 hidden state 生成 `hidden_state_alignment_audits`，检查 response rows 的 batch alignment、table coverage 和 chain-of-custody fragmentation。
  - 对每个 response row 生成 `row_scope_audits`，检查 sensor/operation 类行的 `timestamp/node_id/sensor_id`，以及 `offline_lab_results` 的 `offline_method_id/detection_limit`。
  - 将 hard blockers 接入 `build_field_activation_package_assembly_plan()`：当行级 response preflight 已通过但 coherence audit 不通过时，assembly status 切换为 `field_activation_package_assembly_plan_blocked_by_response_coherence_audit`。
  - 将 coherence audit 接入 `build_field_activation_response_repair_work_order()` 和 `build_field_activation_external_readiness_gate()`，让修复工单和顺序门能显式输出 coherence blocker。
  - 将 coherence audit 状态写入 `build_field_activation_response_submission_packet()`。
- 更新 `experiments/run_field_activation_matrix.py`：
  - 生成 `outputs/model_core_governance/field_activation_response_coherence_audit.json`。
  - 将 audit 嵌入 `field_activation_matrix.json`、markdown 和 `deliverables/manifest.json`。
- 更新 `ModelCoreOptimizationGovernanceAgent` 与 `experiments/run_agent50_model_core_governance.py`：
  - Agent50 scorecard 与 manifest 新增 coherence audit status、hard blocker count、warning count、highest blocker 和 package assembly route flag。
- 更新测试：
  - 默认模板下 audit 等待 response preflight。
  - 填满但 `catalyst_activity` batch_id 碎片化时，audit 阻断 package assembly。
  - 自洽响应能通过 audit，并继续走到 materialized package preflight 等待目录。

当前默认输出：

- `outputs/model_core_governance/field_activation_response_coherence_audit.json`：
  - `audit_status=field_activation_response_coherence_audit_waiting_for_response_preflight`
  - `response_ready_for_audit=False`
  - `hard_blocker_count=0`
  - `warning_count=0`
  - `can_route_to_package_assembly=False`
- `outputs/model_core_governance/field_activation_package_assembly_plan.json`：
  - 当前仍因默认模板阻断在 `field_activation_package_assembly_plan_blocked_by_response_preflight`。
  - 若未来 response 行级预检通过但 coherence audit 不通过，会阻断在 `field_activation_package_assembly_plan_blocked_by_response_coherence_audit`。
- `outputs/model_core_governance/external_activation_router.json`：
  - 当前下一步仍为 `fill_response_template_and_set_FIELD_ACTIVATION_RESPONSE_PATH`。
- `outputs/agent50_model_core_governance/agent50_report.json`：
  - `recommended_next_core_action.task_id=FIELD_ACTIVATION_RESPONSE_SUBMISSION_PACKET_NEXT_ACTION`。

边界：

- R8u117 只检查外部响应的工程一致性和可回放拼接性，不证明 field evidence 成立。
- 即使 coherence audit 通过，也仍必须继续通过 package staging、materialized package preflight、external activation router、R7/Agent44 或 Agent54 preflight、field replay/holdout 和人工复核。
- 本轮不恢复模型链、不写 actuator、不写 release gate、不生成 legal/patent 结论或 field-supported claim。

验证：

- `.venv/bin/python -m py_compile src/water_ai/field_activation_matrix.py src/water_ai/agents/model_core_optimization_governance_agent.py experiments/run_field_activation_matrix.py experiments/run_agent50_model_core_governance.py tests/test_field_activation_matrix.py tests/test_model_core_optimization_governance_agent.py`：通过。
- `.venv/bin/pytest -q tests/test_field_activation_matrix.py`：25 passed。
- `.venv/bin/pytest -q tests/test_field_activation_matrix.py tests/test_model_core_optimization_governance_agent.py -k "field_activation"`：27 passed, 35 deselected。
- `.venv/bin/python experiments/run_field_activation_matrix.py`：通过，已刷新 matrix、response template/source/repair/preflight/coherence audit/assembly/staging/materialized/gate/submission/schema 产物。
- `.venv/bin/python experiments/run_external_activation_router.py`：通过，router 下一步仍为 `fill_response_template_and_set_FIELD_ACTIVATION_RESPONSE_PATH`。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：通过，Agent50 推荐仍为 `FIELD_ACTIVATION_RESPONSE_SUBMISSION_PACKET_NEXT_ACTION`。
- `.venv/bin/pytest -q`：532 passed。
- `.venv/bin/python tools/build_project_codegraph.py`：通过，CodeGraph 刷新为 347 files、4481 nodes、7156 edges。

## 2026-06-22 R8u-116：External Activation Router Field Activation Upstream Gate

目标：

- 承接 R8u115 external activation router candidate consumption。
- 解决一个接口一致性问题：Agent50 顶层推荐和 field activation submission packet 都要求先填 `FIELD_ACTIVATION_RESPONSE_PATH`，但 router 自己仍在默认状态下提示 `set_REAL_FIELD_REPLAY_PACKAGE_DIR`，容易让操作者绕过 response source、repair、assembly、staging 和 materialized package preflight。
- 让 router 消费 field activation external readiness gate 和 field activation response submission packet，在无真实 R7 路径、无可提交 R7 candidate 时，优先提示上游状态级补证动作。

实现：

- 更新 `src/water_ai/external_activation_router.py`：
  - `build_external_activation_router()` 新增 `field_activation_external_readiness_gate` 和 `field_activation_response_submission_packet` 输入。
  - 新增 `field_activation_upstream` 摘要，暴露 status、first blocked step、highest priority blocker、next operator action、submission packet status 和 no-write boundary。
  - R7 route row 在 upstream gate 被消费时新增 `field_activation_upstream_gate` block。
  - 当 `REAL_FIELD_REPLAY_PACKAGE_DIR` 未设置、R8u114 candidate 不可提交且 upstream gate 未 ready 时，R7 route status 切换为 `activation_route_blocked_by_field_activation_upstream_gate`，下一步切换为 `fill_response_template_and_set_FIELD_ACTIVATION_RESPONSE_PATH`。
  - 已提交真实 R7 路径仍优先走完整 R7 preflight；R8u114 candidate 若已经可提交，仍优先提示 candidate，不被 upstream gate 覆盖。
- 更新 `experiments/run_external_activation_router.py`：
  - 自动读取 `outputs/model_core_governance/field_activation_external_readiness_gate.json`。
  - 自动读取 `outputs/model_core_governance/field_activation_response_submission_packet.json`。
  - router markdown 和 manifest 写入 field activation upstream 摘要。
- 更新 `ModelCoreOptimizationGovernanceAgent`：
  - governance scorecard、external resume conditions、route summary 和 next allowed actions 消费 router upstream 状态。
  - Agent50 markdown 报告显示 router upstream status、upstream next operator action 和是否可提交 external activation router。
- 更新测试：
  - 覆盖 upstream gate 阻断时 router 优先提示 `FIELD_ACTIVATION_RESPONSE_PATH`。
  - 覆盖 R8u114 candidate 可提交时 candidate 不被 upstream gate 覆盖。
  - 覆盖 Agent50 能读取 router upstream gate 状态并传播到 core gate。

当前默认输出：

- `outputs/model_core_governance/external_activation_router.json`
- `deliverables/model_core_optimization/external_activation_router.md`
- `outputs/agent50_model_core_governance/agent50_report.json`
- 当前默认状态：
  - `router_status=external_activation_router_waiting_for_external_paths`
  - `priority_route_status=activation_route_blocked_by_field_activation_upstream_gate`
  - `priority_route_preflight_status=field_activation_external_readiness_waiting_for_external_response`
  - `highest_priority_blocker=R7_REAL_FIELD_PACKAGE:field_activation_upstream_not_ready:R8U106_SUBMIT_FIELD_ACTIVATION_RESPONSE:field_activation_external_readiness_waiting_for_external_response`
  - `next_operator_action=fill_response_template_and_set_FIELD_ACTIVATION_RESPONSE_PATH`
  - `field_activation_upstream_can_submit_to_external_activation_router=False`

验证：

- `.venv/bin/python -m py_compile src/water_ai/external_activation_router.py experiments/run_external_activation_router.py src/water_ai/agents/model_core_optimization_governance_agent.py experiments/run_agent50_model_core_governance.py tests/test_external_activation_router.py tests/test_model_core_optimization_governance_agent.py`：通过。
- `.venv/bin/pytest -q tests/test_external_activation_router.py`：10 passed。
- `.venv/bin/pytest -q tests/test_model_core_optimization_governance_agent.py -k "external_activation_router or field_activation_upstream"`：2 passed, 35 deselected。
- `.venv/bin/python experiments/run_external_activation_router.py`：通过，router 已消费 field activation upstream gate。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：通过，Agent50 已消费 router upstream 状态。
- `.venv/bin/pytest -q tests/test_external_activation_router.py tests/test_model_core_optimization_governance_agent.py`：47 passed。
- `.venv/bin/pytest -q`：529 passed。
- `.venv/bin/python tools/build_project_codegraph.py`：通过，CodeGraph 刷新为 347 files、4457 nodes、7128 edges。

边界：

- R8u116 不生成真实 response JSON，不物化 field package，不运行 replay/holdout，不恢复模型链。
- Upstream gate 只排序外部接入动作；通过它也不代表 field evidence 成立、R7 field replay 通过、Agent51 holdout 通过、Agent49 guardrail 可解除、actuator 可写或 release gate 可写。
- 该轮增强的是验证治理层、工程化和可演化性：router、Agent50 推荐和 field activation 顺序门现在对齐到同一个下一步，减少现场接包误操作。

## 2026-06-22 R8u-115：External Activation Router Consumes Catalyst R7 Patch Candidate

目标：

- 承接 R8u114 catalyst slice to R7 patch candidate。
- 解决 R8u114 后的下游回接缺口：R8u114 已能生成“可作为 full R7 package 候选路径”的状态，但 external activation router 仍只提示设置泛化 `REAL_FIELD_REPLAY_PACKAGE_DIR`，操作者看不到更窄的 catalyst slice -> R7 candidate 路线。
- 把 R8u114 的 candidate 状态接入 R7 外部激活路由，同时保持完整 R7 preflight 是唯一模型链恢复门。

实现：

- 更新 `src/water_ai/external_activation_router.py`：
  - `build_external_activation_router()` 新增 `catalyst_slice_r7_patch_candidate_metrics` 输入。
  - 新增 catalyst patch candidate 摘要，暴露 `patch_status`、`candidate_materialized`、`candidate_preflight_status`、`remaining_gap_count`、`candidate_package_dir` 和 `can_submit_candidate_as_REAL_FIELD_REPLAY_PACKAGE_DIR`。
  - `R7_REAL_FIELD_PACKAGE` route row 新增 `catalyst_slice_r7_patch_candidate` block。
  - 当 R8u114 candidate 可提交但 `REAL_FIELD_REPLAY_PACKAGE_DIR` 未设置时，router 的下一步可提示 `set_REAL_FIELD_REPLAY_PACKAGE_DIR_to_catalyst_patch_candidate`，但 `route_ready=False`、`can_resume_model_chain=False`。
  - 当真实 `REAL_FIELD_REPLAY_PACKAGE_DIR` 已提交时，真实路径和完整 R7 preflight 优先，candidate 不能覆盖已提交路径。
- 更新 `experiments/run_external_activation_router.py`：
  - 自动读取 `outputs/catalyst_slice_r7_patch_candidate/catalyst_slice_r7_patch_candidate_metrics.json`。
  - router markdown 与 manifest 写入 catalyst patch candidate 摘要。
- 更新 `ModelCoreOptimizationGovernanceAgent`：
  - governance scorecard、external resume conditions、route summary 和 next allowed actions 均消费 router 的 catalyst patch candidate 状态。
  - Agent50 报告显示 candidate status、是否可作为 R7 目录提交和剩余 gap count。
- 更新测试：
  - 覆盖 candidate waiting 状态只作为提示。
  - 覆盖 candidate 可提交时 router 仍不直接 ready。
  - 覆盖已提交真实 R7 路径时 candidate 不能覆盖真实路径。
  - 覆盖 Agent50 能读取 router candidate 状态。

当前默认输出：

- `outputs/model_core_governance/external_activation_router.json`
- `deliverables/model_core_optimization/external_activation_router.md`
- `outputs/agent50_model_core_governance/agent50_report.json`
- 当前默认状态：
  - `router_status=external_activation_router_waiting_for_external_paths`
  - `catalyst_patch_candidate_status=catalyst_slice_r7_patch_waiting_for_valid_catalyst_slice`
  - `catalyst_patch_candidate_materialized=False`
  - `catalyst_patch_candidate_preflight_status=not_run`
  - `catalyst_patch_candidate_can_submit_as_REAL_FIELD_REPLAY_PACKAGE_DIR=False`
  - `next_operator_action=set_REAL_FIELD_REPLAY_PACKAGE_DIR`

验证：

- `.venv/bin/python -m py_compile src/water_ai/external_activation_router.py experiments/run_external_activation_router.py src/water_ai/agents/model_core_optimization_governance_agent.py tests/test_external_activation_router.py tests/test_model_core_optimization_governance_agent.py`：通过。
- `.venv/bin/pytest -q tests/test_external_activation_router.py`：9 passed。
- `.venv/bin/pytest -q tests/test_model_core_optimization_governance_agent.py -k "external_activation_router or catalyst_patch_candidate"`：2 passed, 34 deselected。
- `.venv/bin/python experiments/run_external_activation_router.py`：通过，router 已消费 R8u114 candidate metrics。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：通过，Agent50 已消费 router candidate 状态。
- `.venv/bin/pytest -q`：527 passed。
- `.venv/bin/python tools/build_project_codegraph.py`：通过，CodeGraph 刷新为 347 files、4444 nodes、7115 edges。

边界：

- R8u115 不生成真实 field package，不运行 Agent51 holdout，不解除 Agent49 catalyst guardrail。
- Candidate 只是建议路径，不是 field-supported evidence；只有 operator 设置 `REAL_FIELD_REPLAY_PACKAGE_DIR` 且完整 R7 preflight 通过后，才可恢复下游模型链。
- 该轮增强的是验证治理层和工程接入清晰度：把“局部 catalyst 切片候选”回接到外部激活主链，同时保留 no-write、no-release、no-claim 边界。

## 2026-06-22 R8u-114：Catalyst Slice To R7 Patch Candidate

目标：

- 承接 R8u113 catalyst field package slice。
- 解决 R8u113 后的关键接口缺口：四表 slice 预检通过后，系统还不知道它如何进入 full R7 field package，也无法明确剩余全包缺口。
- 把 `CATALYST_FIELD_PACKAGE_SLICE_DIR` 指向的真实四表切片覆盖进 full R7 package candidate，并立即运行 R7 package preflight。
- 保持边界：valid slice 只是局部 patch，不能替代完整 R7 package、Agent51 holdout、Agent49 guardrail、actuator gate 或 release gate。

实现：

- 新增 `src/water_ai/catalyst_slice_r7_patch_candidate.py`：
  - `build_catalyst_slice_r7_patch_candidate()` 消费 `CATALYST_FIELD_PACKAGE_SLICE_DIR`、可选 `R7_BASE_FIELD_PACKAGE_DIR` 和候选输出目录。
  - 先调用 R8u113 slice preflight；未通过则保持等待/阻断。
  - slice 通过时，把四张表覆盖进 full R7 package candidate；若未提供 base package，则使用 R7 header/template 作为基底。
  - 立即调用 `preflight_field_replay_package()`，输出 metadata placeholder、header-only required tables、missing/header blockers 和 remaining gap count。
- 新增 `experiments/run_catalyst_slice_r7_patch_candidate.py`：
  - 默认输出 `outputs/catalyst_slice_r7_patch_candidate/catalyst_slice_r7_patch_candidate_metrics.json`。
  - 默认候选包目录为 `outputs/catalyst_slice_r7_patch_candidate/r7_patch_candidate_package`。
  - 生成 `deliverables/model_core_optimization/catalyst_slice_r7_patch_candidate.md`。
  - 更新 manifest latest 指针。
- 更新 Agent50：
  - 新增 `catalyst_slice_r7_patch_candidate_metrics` 输入。
  - governance scorecard、Agent50 报告和 manifest 暴露 patch status、candidate materialized、candidate preflight status、remaining gap count 和是否可作为 `REAL_FIELD_REPLAY_PACKAGE_DIR`。
- 更新测试：
  - 覆盖默认无 slice 时等待。
  - 覆盖 valid slice 可物化 full candidate，但模板基底仍因 metadata/required tables 缺口而阻断。
  - 覆盖显式 base package 不存在时阻断。

当前默认输出：

- `outputs/catalyst_slice_r7_patch_candidate/catalyst_slice_r7_patch_candidate_metrics.json`
- `deliverables/model_core_optimization/catalyst_slice_r7_patch_candidate.md`
- 当前默认状态：
  - `patch_status=catalyst_slice_r7_patch_waiting_for_valid_catalyst_slice`
  - `slice_preflight_pass=False`
  - `candidate_materialized=False`
  - `candidate_preflight_status=not_run`
  - `can_submit_candidate_as_REAL_FIELD_REPLAY_PACKAGE_DIR=False`

验证：

- `.venv/bin/python -m py_compile src/water_ai/catalyst_slice_r7_patch_candidate.py experiments/run_catalyst_slice_r7_patch_candidate.py src/water_ai/agents/model_core_optimization_governance_agent.py experiments/run_agent50_model_core_governance.py tests/test_catalyst_slice_r7_patch_candidate.py tests/test_model_core_optimization_governance_agent.py`：通过。
- `.venv/bin/pytest -q tests/test_catalyst_slice_r7_patch_candidate.py tests/test_catalyst_field_package_slice.py tests/test_model_core_optimization_governance_agent.py`：42 passed。
- `.venv/bin/python experiments/run_catalyst_slice_r7_patch_candidate.py`：通过，默认状态正确等待 valid catalyst slice。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：通过，Agent50 已消费 R8u114。

边界：

- R8u114 不生成真实 field package，不运行 replay/holdout，不产生 field-supported claim。
- 它只把“valid catalyst slice”转成 full package patch candidate，并显式暴露 remaining full-package gaps。
- 该轮增强的是工程化、可验证性和可演化性：真实切片出现时，系统能低摩擦进入 full R7 package candidate；没有真实切片或 full package 缺口未修复时，系统保持 no-write 阻断。

## 2026-06-22 R8u-113：Catalyst Field Package Slice

目标：

- 承接 R8u112 focused catalyst response merge。
- 解决一个更贴近真实工程的接入缺口：R8u111/112 解决了“六行响应 JSON 如何填、如何合并”，但 Agent51/R7 真正要消费的是四张现场 CSV 表和共同 batch 对齐。
- 把 `catalyst_activity` 的六条补证需求落成最小四表现场切片：三类 node-modality sensor 信号、离线 catalyst_activity 标签、再生事件/动作时延、床层几何/HRT。
- 保持边界：切片通过也只能成为 full R7 field package patch candidate，不替代完整 field package、Agent51 holdout、Agent49 guardrail、actuator gate 或 release gate。

实现：

- 新增 `src/water_ai/catalyst_field_package_slice.py`：
  - `build_catalyst_field_package_slice_template()` 生成四表最小模板。
  - `build_catalyst_field_package_slice_preflight()` 读取 `CATALYST_FIELD_PACKAGE_SLICE_DIR` 指向的外部目录，检查表存在、header、TODO 标记、三类 sensor signal、offline lab label、regeneration event、geometry 和 shared batch 对齐。
  - 输出 `can_route_to_r7_field_package_patch_candidate`，但始终保持 `can_route_to_agent51_field_proxy_holdout=False`、`can_relax_agent49_catalyst_uncertainty_block=False`。
- 新增 `experiments/run_catalyst_field_package_slice.py`：
  - 生成 `outputs/catalyst_field_package_slice/focused_field_package_slice_template/` 四张 CSV 模板。
  - 生成 `outputs/catalyst_field_package_slice/focused_field_package_slice_template_summary.json`。
  - 生成 `outputs/catalyst_field_package_slice/catalyst_field_package_slice_metrics.json`。
  - 生成 `deliverables/model_core_optimization/catalyst_field_package_slice.md`。
  - 更新 manifest latest 指针。
- 更新 Agent50：
  - 新增 `catalyst_field_package_slice_metrics` 输入。
  - governance scorecard、Agent50 报告和 manifest 暴露切片状态、preflight pass、matched batch count、template dir、R7 patch candidate route 与 Agent51 route 边界。
- 更新测试：
  - 覆盖四表模板结构和行数。
  - 覆盖默认未设置 `CATALYST_FIELD_PACKAGE_SLICE_DIR` 时等待。
  - 覆盖三批次真实切片可成为 R7 patch candidate 但不能声称 Agent51/Agent49 通过。
  - 覆盖 sensor/lab/operation batch 对齐不足时阻断。

当前默认输出：

- `outputs/catalyst_field_package_slice/catalyst_field_package_slice_metrics.json`
- `outputs/catalyst_field_package_slice/focused_field_package_slice_template/`
- `outputs/catalyst_field_package_slice/focused_field_package_slice_template_summary.json`
- `deliverables/model_core_optimization/catalyst_field_package_slice.md`
- 当前默认状态：
  - `slice_status=catalyst_field_package_slice_waiting_for_CATALYST_FIELD_PACKAGE_SLICE_DIR`
  - `slice_preflight_pass=False`
  - `matched_batch_count=0`
  - `can_route_to_r7_field_package_patch_candidate=False`
  - `can_route_to_agent51_field_proxy_holdout=False`

验证：

- `.venv/bin/python -m py_compile src/water_ai/catalyst_field_package_slice.py experiments/run_catalyst_field_package_slice.py src/water_ai/agents/model_core_optimization_governance_agent.py experiments/run_agent50_model_core_governance.py tests/test_catalyst_field_package_slice.py tests/test_model_core_optimization_governance_agent.py`：通过。
- `.venv/bin/pytest -q tests/test_catalyst_field_package_slice.py tests/test_model_core_optimization_governance_agent.py`：39 passed。
- `.venv/bin/python experiments/run_catalyst_field_package_slice.py`：通过，默认状态正确等待 `CATALYST_FIELD_PACKAGE_SLICE_DIR`。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：通过，Agent50 已消费 R8u113。

边界：

- R8u113 不是完整 R7 package import，不是 Agent51 field holdout，不是 field claim。
- 它只把当前最硬的 `catalyst_activity` 补证缺口压成最小四表 field slice，降低真实现场补数与导入预检摩擦。
- 该轮增强的是可验证性、工程化和可演化性：后续如果有真实四表切片，可以低摩擦进入 full R7 package patch/import；如果没有，系统明确停在外部证据等待态，不再靠 synthetic/template 继续冒进。

## 2026-06-22 R8u-112：Focused Catalyst Response Merge Preflight

目标：

- 承接 R8u111 focused catalyst response submission kit。
- 解决一个执行接口缺口：R8u111 生成了 6 行 focused template/schema/merge plan，但还没有机器入口来读取外部填写后的 `FOCUSED_CATALYST_RESPONSE_PATH`、检查 6 行质量，并自动合并成 full field activation response candidate。
- 将“focused 小包填写完成 -> merged full response candidate -> 可作为 `FIELD_ACTIVATION_RESPONSE_PATH` 继续走 R8u98/R8u108”的接口打通。
- 保持边界：merged candidate 只是预检产物；非 catalyst 的 27 行可能仍阻断 full response preflight，不能替代 field package、Agent51 holdout、Agent49 guardrail 或 release/actuator gates。

实现：

- 新增 `src/water_ai/focused_catalyst_response_merge.py`：
  - `build_focused_catalyst_response_merge_preflight()` 消费 focused response、focused schema、full response template 和 merge plan。
  - 验证 top-level package type、target hidden state、6 行 row id、必填行字段、真实 field origin、no-write、证据引用和共同 batch。
  - 通过时按 `response_row_id` 替换 full template 中 6 条 catalyst rows，输出 `merged_full_response_candidate`。
- 新增 `experiments/run_focused_catalyst_response_merge.py`：
  - 读取 `FOCUSED_CATALYST_RESPONSE_PATH`；未设置时使用默认 focused template 并保持等待态。
  - 生成 `outputs/focused_catalyst_response_merge/focused_catalyst_response_merge_preflight.json`。
  - 生成 `outputs/focused_catalyst_response_merge/merged_full_field_activation_response_candidate.json`。
  - 生成 `deliverables/model_core_optimization/focused_catalyst_response_merge.md`。
  - 更新 manifest latest 指针。
- 更新 Agent50：
  - 新增 `focused_catalyst_response_merge_metrics` 输入。
  - governance scorecard 和 field evidence wait status 暴露 merge preflight status、row pass、candidate emit、能否提交为 `FIELD_ACTIVATION_RESPONSE_PATH` 和 Agent51 route 状态。
- 更新测试：
  - 覆盖默认未设置 `FOCUSED_CATALYST_RESPONSE_PATH` 时等待。
  - 覆盖真实 focused response 满足 3 个共同 batch 时可发出 merged full response candidate，但不能声称 full preflight/Agent51 通过。
  - 覆盖共同 batch 不足时阻断。

当前默认输出：

- `outputs/focused_catalyst_response_merge/focused_catalyst_response_merge_preflight.json`
- `outputs/focused_catalyst_response_merge/merged_full_field_activation_response_candidate.json`
- `deliverables/model_core_optimization/focused_catalyst_response_merge.md`
- 当前默认状态：
  - `preflight_status=focused_catalyst_response_merge_waiting_for_FOCUSED_CATALYST_RESPONSE_PATH`
  - `row_preflight_pass=False`
  - `matched_batch_count=0`
  - `can_emit_merged_full_response_candidate=False`
  - `can_submit_candidate_as_FIELD_ACTIVATION_RESPONSE_PATH=False`
  - `can_route_to_agent51_field_proxy_holdout=False`

验证：

- `.venv/bin/python -m py_compile src/water_ai/focused_catalyst_response_merge.py experiments/run_focused_catalyst_response_merge.py src/water_ai/agents/model_core_optimization_governance_agent.py experiments/run_agent50_model_core_governance.py tests/test_focused_catalyst_response_merge.py tests/test_model_core_optimization_governance_agent.py`：通过。
- `.venv/bin/pytest tests/test_focused_catalyst_response_merge.py tests/test_model_core_optimization_governance_agent.py -q`：38 passed。
- `.venv/bin/python experiments/run_focused_catalyst_response_merge.py`：通过，默认状态正确等待 `FOCUSED_CATALYST_RESPONSE_PATH`。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：通过，Agent50 已消费 R8u112。

边界：

- R8u112 不是 full response preflight，不是 field package，也不是 Agent51 holdout。
- 它只把填好的 focused catalyst response 合并为 full response candidate；后续仍必须设置 `FIELD_ACTIVATION_RESPONSE_PATH` 并跑 R8u98/R8u108、materialized package preflight、Agent51 holdout、replay gates 和人工/工程门控。
- 该轮增强的是工程化、可验证性和可保护性：真实 focused 数据一旦出现，系统可以低摩擦转入 full response 链条，但不会越权提升证据等级。

## 2026-06-22 R8u-111：Catalyst Response Submission Kit

目标：

- 承接 R8u110 focused catalyst evidence response gate。
- 解决一个外部提交摩擦：全量 field activation response 有 33 行，但当前最高优先级的真实补证是 `catalyst_activity` 六条行。外部 operator 如果每次从 33 行模板里定位这 6 行，容易填错、漏填或污染上下文。
- 生成一个 focused catalyst response submission kit：包含 6 行 operator-fillable template、schema、以及把 6 行合并回 full response 的 merge plan。
- 保持边界：focused template 只是填写小包，不是 field evidence，不替代 full response，不运行 Agent51，不解除 Agent49，不写 actuator/release gate。

实现：

- 新增 `src/water_ai/catalyst_response_submission_kit.py`：
  - `build_catalyst_response_submission_kit()` 消费 R8u109 bridge、full response template 和 R8u110 gate。
  - 输出 focused template、schema 和 full response merge plan。
  - 每行保留 response_row_id、hidden_state、required_evidence、node/table/field、matched_batch_ids、evidence reference、chain-of-custody 和 no-write 确认。
- 新增 `experiments/run_catalyst_response_submission_kit.py`：
  - 生成 `outputs/catalyst_response_submission_kit/catalyst_response_submission_kit_metrics.json`。
  - 生成 `outputs/catalyst_response_submission_kit/focused_catalyst_response_template.json`。
  - 生成 `outputs/catalyst_response_submission_kit/focused_catalyst_response_schema.json`。
  - 生成 `outputs/catalyst_response_submission_kit/focused_to_full_response_merge_plan.json`。
  - 生成 `deliverables/model_core_optimization/catalyst_response_submission_kit.md`。
  - 更新 manifest latest 指针。
- 更新 Agent50：
  - 新增 `catalyst_response_submission_kit_metrics` 输入。
  - governance scorecard 和 field evidence wait status 暴露 kit status、target row count、focused template path 和 Agent51 route 状态。
- 更新测试：
  - 验证小包只生成 6 行 catalyst template。
  - 验证 merge plan 仍有 27 行 full response 未替换，不会把小包伪装成全量 response。
  - 验证 full template 缺目标行时 kit 阻断。

当前默认输出：

- `outputs/catalyst_response_submission_kit/focused_catalyst_response_template.json`
- `outputs/catalyst_response_submission_kit/focused_catalyst_response_schema.json`
- `outputs/catalyst_response_submission_kit/focused_to_full_response_merge_plan.json`
- `outputs/catalyst_response_submission_kit/catalyst_response_submission_kit_metrics.json`
- `deliverables/model_core_optimization/catalyst_response_submission_kit.md`
- 当前默认状态：
  - `kit_status=catalyst_response_submission_kit_ready_for_operator_fill`
  - `target_response_row_count=6`
  - `minimum_matched_batch_count=3`
  - `can_replace_full_field_activation_response=False`
  - `can_route_to_agent51_field_proxy_holdout=False`
  - `can_relax_agent49_catalyst_uncertainty_block=False`

验证：

- `.venv/bin/python -m py_compile src/water_ai/catalyst_response_submission_kit.py experiments/run_catalyst_response_submission_kit.py src/water_ai/agents/model_core_optimization_governance_agent.py experiments/run_agent50_model_core_governance.py tests/test_catalyst_response_submission_kit.py tests/test_model_core_optimization_governance_agent.py`：通过。
- `.venv/bin/pytest tests/test_catalyst_response_submission_kit.py tests/test_model_core_optimization_governance_agent.py -q`：37 passed。
- `.venv/bin/python experiments/run_catalyst_response_submission_kit.py`：通过，生成 focused template/schema/merge plan。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：通过，Agent50 已消费 R8u111。

边界：

- R8u111 不是现场数据，不是 Agent51 holdout，也不是 full response preflight。
- 它只把外部提交动作从“全量 33 行模板里找 6 行”压缩为“先填 6 行 focused template，再按 merge plan 回填 full response”。
- 该轮增强的是工程化、可验证性和可保护性：减少真实数据采集/回填摩擦，同时保留所有 no-write 和 field validation 边界。

## 2026-06-22 R8u-110：Catalyst Evidence Response Gate

目标：

- 承接 R8u109 observation response bridge。
- 解决一个阶段性验证缺口：R8u98 全量 response preflight 要求 33 行都完整，但当前最高价值弱轴是 `catalyst_activity` 的 6 条 response rows。系统需要能单独判断这 6 行是否已经够进入 focused package preflight，而不是每次都被全量模板拖住。
- 把 `catalyst_activity` 六条优先补证行升级为聚焦门控，检查真实 field origin、no-write、证据引用和至少 3 个共同 batch。
- 保持边界：该门控只检查 response rows，不检查物化 CSV 值、不运行 Agent51 holdout、不验证 catalyst_activity、不解除 Agent49 保护、不写 actuator 或 release gate。

实现：

- 新增 `src/water_ai/catalyst_evidence_response_gate.py`：
  - `build_catalyst_evidence_response_gate()` 消费 R8u109 bridge、field activation response、source preflight、full response preflight 和 submission packet。
  - 对 6 条目标行逐行输出 `row_status`、blocking issues、batch ids 和 evidence reference。
  - 输出 batch alignment：各观测角色共同 batch 交集、matched_batch_count、matched_batch_requirement_pass。
- 新增 `experiments/run_catalyst_evidence_response_gate.py`：
  - 优先读取 `FIELD_ACTIVATION_RESPONSE_PATH` 指向的外部响应；未设置时使用默认模板，因此保持等待/阻断态。
  - 生成 `outputs/catalyst_evidence_response_gate/catalyst_evidence_response_gate_metrics.json`。
  - 生成 `deliverables/model_core_optimization/catalyst_evidence_response_gate.md`。
  - 更新 manifest latest 指针。
- 更新 Agent50：
  - 新增 `catalyst_evidence_response_gate_metrics` 输入。
  - governance scorecard 和 field evidence wait status 现在暴露 gate status、target row count、row-level pass、matched_batch_count、matched_batch_requirement_pass、focused package route 和 Agent51 route 状态。
  - runner 消费 `outputs/catalyst_evidence_response_gate/catalyst_evidence_response_gate_metrics.json`。
- 更新测试：
  - 覆盖默认无外部响应时等待 `FIELD_ACTIVATION_RESPONSE_PATH`。
  - 覆盖 6 行已填 field origin 且 3 个 batch 对齐时，可进入 focused package preflight，但仍不能进入 Agent51 或放松 Agent49。
  - 覆盖缺失一条优先行时被阻断。

当前默认输出：

- `outputs/catalyst_evidence_response_gate/catalyst_evidence_response_gate_metrics.json`
- `deliverables/model_core_optimization/catalyst_evidence_response_gate.md`
- 当前默认状态：
  - `gate_status=catalyst_evidence_response_gate_waiting_for_FIELD_ACTIVATION_RESPONSE_PATH`
  - `target_response_row_count=6`
  - `row_level_preflight_pass=False`
  - `matched_batch_count=0`
  - `matched_batch_requirement_pass=False`
  - `can_route_to_focused_materialized_package_preflight=False`
  - `can_route_to_agent51_field_proxy_holdout=False`
  - `can_relax_agent49_catalyst_uncertainty_block=False`

验证：

- `.venv/bin/python -m py_compile src/water_ai/catalyst_evidence_response_gate.py experiments/run_catalyst_evidence_response_gate.py src/water_ai/agents/model_core_optimization_governance_agent.py experiments/run_agent50_model_core_governance.py tests/test_catalyst_evidence_response_gate.py tests/test_model_core_optimization_governance_agent.py`：通过。
- `.venv/bin/pytest tests/test_catalyst_evidence_response_gate.py tests/test_model_core_optimization_governance_agent.py -q`：38 passed。
- `.venv/bin/python experiments/run_catalyst_evidence_response_gate.py`：通过，默认状态正确等待 `FIELD_ACTIVATION_RESPONSE_PATH`。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：通过，Agent50 已消费 R8u110。

边界：

- R8u110 不是 field package，不是 field validation，也不是 Agent51 holdout。
- 通过该门控只表示 6 条 response rows 具备进入 focused materialized package preflight 的条件；仍必须通过物化包预检、Agent51 field proxy holdout、replay gates 和人工/工程门控。
- 该轮增强的是可验证性、可工程化和可保护性：让外部响应提交有更细粒度的阶段门，同时保持 no-write 边界。

## 2026-06-22 R8u-109：Observation Response Bridge

目标：

- 承接 R2 observation contract、Agent48 hidden-state ledger、Agent51 catalyst proxy holdout summary、Agent54 soft sensor matrix 和 R8u108 field activation response submission packet。
- 解决一个接入摩擦：系统已经知道 `catalyst_activity` 是当前最硬的弱观测隐藏状态，也已经有 33 行 field activation response template，但外部补证时仍需要在完整模板里重新找哪些行最关键。
- 把 `catalyst_activity` 的观测弱轴需求压成 6 条优先响应行，形成“观测合同 -> 现场补证模板 -> Agent51 holdout -> Agent49 guardrail”的桥。
- 保持边界：该桥只排序和映射 response rows，不生成现场证据、不验证 catalyst_activity、不解除 Agent49 保护、不写 actuator 或 release gate。

实现：

- 新增 `src/water_ai/observation_response_bridge.py`：
  - `build_observation_response_bridge()` 消费 observation contract、response template、submission packet、Agent51 holdout summary 和 Agent54 soft sensor matrix。
  - 将 response rows 映射为 6 个观测角色：`bed_outlet_uv254_proxy`、`bed_outlet_orp_proxy`、`pressure_headloss_proxy`、`catalyst_activity_label`、`regeneration_event`、`hydraulic_normalizer`。
  - 输出 `operator_priority_fill_plan`，指向 `fill_response_template_and_set_FIELD_ACTIVATION_RESPONSE_PATH`。
- 新增 `experiments/run_observation_response_bridge.py`：
  - 生成 `outputs/observation_response_bridge/observation_response_bridge_metrics.json`。
  - 生成 `deliverables/model_core_optimization/observation_response_bridge.md`。
  - 更新 manifest latest 指针。
- 更新 Agent50：
  - 新增 `observation_response_bridge_metrics` 输入。
  - governance scorecard 和 field evidence wait status 现在暴露 bridge status、目标隐藏状态、response row count、required role coverage、Agent51 route 状态和 Agent49 guardrail relaxation 状态。
  - runner 消费 `outputs/observation_response_bridge/observation_response_bridge_metrics.json`，并把该路径写入 Agent50 payload 与 generated_files。
- 更新测试：
  - 新增 `tests/test_observation_response_bridge.py`，覆盖 catalyst row prioritization、Agent51 route gating 和 missing target rows blocking。
  - 更新 Agent50 测试，确保 bridge 指标进入 governance scorecard，且不能恢复模型链或放松 Agent49。

当前默认输出：

- `outputs/observation_response_bridge/observation_response_bridge_metrics.json`
- `deliverables/model_core_optimization/observation_response_bridge.md`
- 当前默认状态：
  - `bridge_status=observation_response_bridge_ready_for_priority_field_response_fill`
  - `primary_target_hidden_state=catalyst_activity`
  - `response_row_count=6`
  - `required_role_coverage_rate=1.000`
  - `can_route_to_agent51_field_proxy_holdout=False`
  - `can_relax_agent49_catalyst_uncertainty_block=False`
  - `can_write_to_actuator=False`
  - `can_write_to_release_gate=False`

验证：

- `.venv/bin/python -m py_compile src/water_ai/observation_response_bridge.py experiments/run_observation_response_bridge.py src/water_ai/agents/model_core_optimization_governance_agent.py experiments/run_agent50_model_core_governance.py tests/test_observation_response_bridge.py tests/test_model_core_optimization_governance_agent.py`：通过。
- `.venv/bin/pytest tests/test_observation_response_bridge.py tests/test_model_core_optimization_governance_agent.py -q`：38 passed。
- `.venv/bin/python experiments/run_observation_response_bridge.py`：通过，bridge 状态为 `observation_response_bridge_ready_for_priority_field_response_fill`。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：通过，Agent50 已消费 observation response bridge。

边界：

- R8u109 不是新 field package，也不是 Agent51 field validation。
- 6 条行只说明 response template 中的补证角色已被定位；只有外部填入真实 `data_origin=field` 行、通过 response/source/package/preflight、Agent51 holdout 和后续 replay gate 后，才能讨论提升证据等级。
- 该轮增强的是观测层、状态估计层和验证治理层之间的接口清晰度，不改变控制策略、不恢复模型链。

## 2026-06-22 R8u-108：Field Activation Response Submission Packet

目标：

- 承接 R8u-106 顺序门和 R8u-107 顶层推荐。
- 解决一个低摩擦接入缺口：系统已经知道第一阻断是提交 `FIELD_ACTIVATION_RESPONSE_PATH`，但模板、repair work order、source preflight、response preflight 和 external readiness gate 分散在多个文件里。
- 把“如何提交填写后的 field activation response JSON”压成一个人和机器都能读的 no-write submission packet。
- 保持边界：submission packet 只指导提交和预检外部响应，不生成 field evidence、不物化包目录、不运行 replay/holdout、不恢复模型链、不写 actuator 或 release gate。

实现：

- 更新 `src/water_ai/field_activation_matrix.py`：
  - 新增 `build_field_activation_response_submission_packet()`。
  - 输出 `packet_status`、`source_env_var`、`response_template_path`、必填字段、最高阻断、下一步动作、验证命令和 no-write boundary。
  - 默认状态为 `field_activation_response_submission_packet_waiting_for_external_response`；填写后的外部 JSON 通过响应预检后，状态可推进为 `field_activation_response_submission_packet_response_ready_for_package_assembly`。
- 更新 `experiments/run_field_activation_matrix.py`：
  - 新增输出 `outputs/model_core_governance/field_activation_response_submission_packet.json`。
  - `field_activation_matrix.json`、matrix markdown 和 manifest latest 指针同步 submission packet 状态。
- 更新 Agent50：
  - governance scorecard、`next_allowed_actions.NEW_CORE_INTERFACE`、`external_resume_conditions.new_core_interface` 和 `field_evidence_wait_status` 消费 submission packet。
  - 当 external field blocker active 且 submission packet 可用时，`recommended_next_core_action` 优先返回 `FIELD_ACTIVATION_RESPONSE_SUBMISSION_PACKET_NEXT_ACTION`。
- 更新测试：
  - 默认模板路径下，submission packet 必须等待外部响应，并给出 `fill_response_template_and_set_FIELD_ACTIVATION_RESPONSE_PATH`。
  - 填好的响应 JSON 通过 response preflight 后，submission packet 必须进入 response-ready 状态，但仍保持 no-write。
  - Agent50 必须把顶层推荐从 R8u106 gate 升级到 R8u108 submission packet。

当前默认输出：

- `outputs/model_core_governance/field_activation_response_submission_packet.json`
- 当前默认状态：
  - `packet_status=field_activation_response_submission_packet_waiting_for_external_response`
  - `highest_priority_blocker=R8U106_SUBMIT_FIELD_ACTIVATION_RESPONSE`
  - `next_operator_action=fill_response_template_and_set_FIELD_ACTIVATION_RESPONSE_PATH`
  - `can_submit_to_response_preflight=True`
  - `can_route_to_external_activation_router=False`
  - `can_resume_model_chain=False`
  - `can_write_to_actuator=False`
  - `can_write_to_release_gate=False`
- Agent50 当前推荐：
  - `recommended_next_core_action=FIELD_ACTIVATION_RESPONSE_SUBMISSION_PACKET_NEXT_ACTION`

验证：

- `.venv/bin/python -m py_compile src/water_ai/field_activation_matrix.py experiments/run_field_activation_matrix.py src/water_ai/agents/model_core_optimization_governance_agent.py tests/test_field_activation_matrix.py tests/test_model_core_optimization_governance_agent.py`：通过。
- `.venv/bin/pytest tests/test_field_activation_matrix.py tests/test_model_core_optimization_governance_agent.py -q`：57 passed。
- `.venv/bin/python experiments/run_field_activation_matrix.py`：通过，已刷新 submission packet。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：通过，Agent50 顶层推荐已切换到 R8u108。

边界：

- R8u108 不是新的真实数据、不是现场包目录、不是 router，也不是控制策略升级。
- 它只降低外部真实响应提交的 scan 摩擦，让“第一份真实响应包怎么进系统”有唯一入口。
- 即使 response preflight 通过，也仍需 package assembly、staging、materialized package preflight、external activation router、field replay/holdout、operator review 和 release/actuator gates。

## 2026-06-22 R8u-107：Field Activation External Readiness Recommendation

目标：

- 承接 R8u-106 的 field activation external readiness gate。
- 解决一个上层推荐不一致问题：底层顺序门已经知道当前第一步是 `set_FIELD_ACTIVATION_RESPONSE_PATH_to_filled_external_response_json`，但 Agent50 顶层推荐仍输出泛化 `WAIT_real_field_package_or_new_core_interface`。
- 让 recommended_next_core_action 在外部 field blocker active 且顺序门可用时，直接指向 R8u106 的 first blocked step、highest blocker 和 next operator action。
- 保持边界：推荐层只是选择下一步，不生成 field evidence、不运行 replay/holdout、不恢复模型链、不写 actuator 或 release gate。

实现：

- 更新 `src/water_ai/agents/model_core_optimization_governance_agent.py`：
  - `_recommended_next_core_action()` 在没有内部高价值 actionable task 且 external readiness gate 可用时，返回 `FIELD_ACTIVATION_EXTERNAL_READINESS_NEXT_ACTION`。
  - 推荐项直接包含 `first_blocked_step=response_source`、`blocked_by=R8U106_SUBMIT_FIELD_ACTIVATION_RESPONSE`、`next_operator_action=set_FIELD_ACTIVATION_RESPONSE_PATH_to_filled_external_response_json`。
  - `field_evidence_wait_status` 同步加入 external readiness gate 状态、第一阻断、最高阻断、下一步和 can submit。
- 更新 `experiments/run_agent50_model_core_governance.py`：
  - current work item 改为 R8u107。
  - manifest 新增 `latest_agent50_recommended_next_core_action*` 和 `latest_agent50_field_activation_external_readiness_*` 指针。
- 更新测试：
  - 无 R8u106 输入的旧等待态仍保留泛化 WAIT。
  - 消费 field activation matrix 的场景必须推荐 `FIELD_ACTIVATION_EXTERNAL_READINESS_NEXT_ACTION`，并带出 R8u106 第一阻断。

当前默认输出：

- `outputs/model_core_governance/priority_ranking.json`
- `outputs/model_core_governance/core_score_termination_gate.json`
- `deliverables/manifest.json`
- 当前默认推荐：
  - `recommended_next_core_action=FIELD_ACTIVATION_EXTERNAL_READINESS_NEXT_ACTION`
  - `blocked_by=R8U106_SUBMIT_FIELD_ACTIVATION_RESPONSE`
  - `first_blocked_step=response_source`
  - `next_operator_action=set_FIELD_ACTIVATION_RESPONSE_PATH_to_filled_external_response_json`

验证：

- `.venv/bin/python -m py_compile experiments/run_agent50_model_core_governance.py src/water_ai/agents/model_core_optimization_governance_agent.py tests/test_model_core_optimization_governance_agent.py`：通过。
- `.venv/bin/pytest tests/test_model_core_optimization_governance_agent.py -q`：35 passed。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：通过，Agent50 顶层推荐已切换。

边界：

- R8u107 只是推荐层对齐，不改变 R8u106 gate 判定，不改变 router 判定。
- 推荐执行 `FIELD_ACTIVATION_RESPONSE_PATH` 只表示外部证据接入的第一步；即使完成，也不能直接形成 field-supported claim、actuator policy 或 release gate。
- 该轮增强的是验证治理层、工程化能力和可演化性：后续 agent 不再需要扫描多个文件才能知道当前第一操作。

## 2026-06-22 R8u-106：Field Activation External Readiness Gate

目标：

- 承接 R8u-105 的 materialized package preflight。
- 解决一个顺序冲突：external activation router 在默认无路径时提示 `set_REAL_FIELD_REPLAY_PACKAGE_DIR`，但 field activation 链条在当前默认状态下连填写后的 `FIELD_ACTIVATION_RESPONSE_PATH` 都还没有提交，直接设置目录会绕过状态级补证、repair work order、assembly 和 staging。
- 将 response source、schema、response preflight、repair work order、package assembly、staging manifest 和 materialized package preflight 串成一个机器可读的顺序门，给出唯一的 first blocked step、最高阻断和下一步操作。
- 保持边界：external readiness gate 只排序已有预检，不生成 field evidence、不运行 replay/holdout、不恢复模型链、不写 actuator 或 release gate。

实现：

- 更新 `src/water_ai/field_activation_matrix.py`：
  - 新增 `build_field_activation_external_readiness_gate()`。
  - 新增 `response_source -> schema_preflight -> response_preflight -> repair_work_order -> package_assembly -> package_staging -> materialized_package_preflight` 七步顺序门。
  - 当前默认第一阻断固定为 `response_source`，避免 operator 跳到 `REAL_FIELD_REPLAY_PACKAGE_DIR`。
  - 当 response/staging ready 但未设置目录时，第一阻断切换为 `materialized_package_preflight`，下一步才是 `set_REAL_FIELD_REPLAY_PACKAGE_DIR`。
  - 当物化目录预检通过时，状态进入 `field_activation_external_readiness_ready_for_external_activation_router`。
- 更新 `experiments/run_field_activation_matrix.py`：
  - 新增输出 `outputs/model_core_governance/field_activation_external_readiness_gate.json`。
  - `field_activation_matrix.json`、matrix markdown 和 manifest latest 指针同步 external readiness 状态。
- 更新 Agent50：
  - governance scorecard、`next_allowed_actions.NEW_CORE_INTERFACE` 和 `external_resume_conditions.new_core_interface` 现在消费 external readiness gate status、first blocked step、highest blocker、next operator action 和 can submit。
- 更新测试：
  - 默认模板路径下，顺序门必须优先阻断在 `response_source`，下一步为 `set_FIELD_ACTIVATION_RESPONSE_PATH_to_filled_external_response_json`。
  - response/staging ready 但未设置目录时，顺序门必须阻断在 materialized package preflight。
  - 临时 materialized package 目录通过预检后，顺序门可进入 ready for router，但仍保持 no-write。

当前默认输出：

- `outputs/model_core_governance/field_activation_external_readiness_gate.json`
- 当前默认状态：
  - `gate_status=field_activation_external_readiness_waiting_for_external_response`
  - `first_blocked_step=response_source`
  - `highest_priority_blocker=R8U106_SUBMIT_FIELD_ACTIVATION_RESPONSE`
  - `next_operator_action=set_FIELD_ACTIVATION_RESPONSE_PATH_to_filled_external_response_json`
  - `ready_step_count=1`
  - `blocked_step_count=6`
  - `can_submit_to_external_activation_router=False`
  - `can_resume_model_chain=False`
  - `can_write_to_actuator=False`
  - `can_write_to_release_gate=False`

验证：

- `.venv/bin/python -m py_compile src/water_ai/field_activation_matrix.py experiments/run_field_activation_matrix.py src/water_ai/agents/model_core_optimization_governance_agent.py experiments/run_agent50_model_core_governance.py tests/test_field_activation_matrix.py tests/test_model_core_optimization_governance_agent.py`：通过。
- `.venv/bin/pytest tests/test_field_activation_matrix.py tests/test_model_core_optimization_governance_agent.py tests/test_external_activation_router.py -q`：61 passed。
- `.venv/bin/python experiments/run_field_activation_matrix.py`：通过，已刷新 external readiness gate。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：通过，Agent50 已消费 external readiness gate。

边界：

- R8u106 不是新的现场证据层，也不是 router 本身；它只是把现有 preflight 结果排序。
- 即使 R8u106 ready，也只是说明可以提交 external activation router；仍必须通过 R7/Agent44 field package preflight、Agent54 path/endpoint preflight、field replay/holdout、operator review 或 release validation 后，才能讨论模型链恢复、保护性控制候选或 release gate。
- 该轮增强的是验证治理层、工程化能力和可保护性，不改变 Agent48/49 控制策略，不产生现场结论。

## 2026-06-22 R8u-105：Field Activation Materialized Package Preflight

目标：

- 承接 R8u-104 的 field activation package staging manifest。
- 解决一个新的真实接入缺口：staging manifest 已能告诉 operator 如何把填写后的 response 行整理成外部包目录，但系统还缺少一道机器预检去判断这个“已物化目录”是否真的满足 router 前置要求。
- 将“operator 物化出的现场包目录 -> external activation router”的桥压成 no-write materialized package preflight。
- 保持边界：materialized package preflight 只检查目录、metadata、CSV 表、字段、template marker 和 field provenance，不生成 field evidence、不运行 replay/holdout、不恢复模型链、不写 actuator 或 release gate。

实现：

- 更新 `src/water_ai/field_activation_matrix.py`：
  - 新增 `preflight_field_activation_materialized_package()`。
  - 新增 R7 metadata 必填字段合同：`data_origin`、`site_id`、`campaign_id`、`sampling_start`、`sampling_end`、`operator_id`、`instrument_snapshot_id`、`chain_of_custody_id`。
  - 默认 staging 未 ready 时，状态为 `field_activation_materialized_package_preflight_blocked_by_staging_manifest`。
  - staging ready 但未设置包目录时，状态为 `field_activation_materialized_package_preflight_waiting_for_package_dir`。
  - 目录齐全且 metadata/CSV 均满足 staging manifest 要求时，状态为 `field_activation_materialized_package_preflight_ready_for_external_activation_router`。
- 更新 `experiments/run_field_activation_matrix.py`：
  - 新增输出 `outputs/model_core_governance/field_activation_materialized_package_preflight.json`。
  - 支持读取 staging 中的 package pointer 环境变量，例如 `REAL_FIELD_REPLAY_PACKAGE_DIR=/path/to/package_dir`。
  - `field_activation_matrix.json`、matrix markdown 和 manifest latest 指针同步 materialized preflight 状态。
- 更新 Agent50：
  - governance scorecard、`next_allowed_actions.NEW_CORE_INTERFACE` 和 `external_resume_conditions.new_core_interface` 现在消费 materialized package preflight status、blocker count、highest blocker、can route 和 next operator action。
- 更新测试：
  - 默认模板路径下，materialized package preflight 必须阻断在 staging manifest。
  - staging ready 但未设置 package dir 时，必须提示 `set_REAL_FIELD_REPLAY_PACKAGE_DIR`。
  - 临时 materialized package 目录包含合格 metadata.json 和所有 staging CSV 时，预检可进入 `ready_for_external_activation_router`，但仍保持 no-write。
  - 缺少 metadata.json 时必须被 `R8U105_METADATA_JSON_MISSING` 阻断。

当前默认输出：

- `outputs/model_core_governance/field_activation_materialized_package_preflight.json`
- 当前默认状态：
  - `preflight_status=field_activation_materialized_package_preflight_blocked_by_staging_manifest`
  - `package_pointer=REAL_FIELD_REPLAY_PACKAGE_DIR`
  - `highest_priority_blocker=R8U105_STAGING_MANIFEST_NOT_READY`
  - `blocker_count=1`
  - `can_route_to_external_activation_router=False`
  - `can_resume_model_chain=False`
  - `can_write_to_actuator=False`
  - `can_write_to_release_gate=False`

验证：

- `.venv/bin/python -m py_compile src/water_ai/field_activation_matrix.py experiments/run_field_activation_matrix.py src/water_ai/agents/model_core_optimization_governance_agent.py tests/test_field_activation_matrix.py tests/test_model_core_optimization_governance_agent.py`：通过。
- `.venv/bin/pytest tests/test_field_activation_matrix.py tests/test_model_core_optimization_governance_agent.py tests/test_external_activation_router.py -q`：58 passed。
- `.venv/bin/python experiments/run_field_activation_matrix.py`：通过，已刷新 matrix、response template/source/repair/preflight、assembly plan、staging manifest、materialized package preflight、schema contract/preflight、manifest 和 matrix 说明。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：通过，Agent50 已消费 materialized package preflight。

边界：

- materialized package preflight 不是 field replay、field holdout 或现场结论，只是 router 前置的目录结构与 provenance 闸门。
- 即使 materialized preflight ready，也只是说明可以把该目录交给 external activation router；真正恢复主链仍需要 R7/Agent44 field package preflight、Agent54 path/endpoint preflight、field replay/holdout、operator review 或 release validation。
- 该轮增强的是验证治理层、工程化能力和可保护性，不改变 Agent48/49 控制策略，不产生现场结论。

## 2026-06-22 R8u-104：Field Activation Package Staging Manifest

目标：

- 承接 R8u-99/100/101/102 的 field activation 链条：已有 response template、source preflight、response preflight、assembly plan、schema preflight 和 repair work order。
- 解决一个真实接入缺口：当 operator 填完 `FIELD_ACTIVATION_RESPONSE_PATH` 后，系统还缺少一份机器可读清单说明这些响应行应如何转成 R7/path endpoint 外部包目录、需要设置哪个 env var、运行哪个 router preflight。
- 将“状态级响应 -> 外部包目录 -> external activation router”的桥压成 no-write staging manifest，减少 operator 和后续 agent 的 scan 摩擦。
- 保持边界：staging manifest 只指导组包，不写包、不合成 field evidence、不运行 replay/holdout、不恢复模型链、不写 actuator 或 release gate。

实现：

- 更新 `src/water_ai/field_activation_matrix.py`：
  - 新增 `build_field_activation_package_staging_manifest()`。
  - 默认 response preflight 未通过时，状态为 `field_activation_package_staging_manifest_blocked_by_response_preflight`。
  - response/assembly 通过时，状态为 `field_activation_package_staging_manifest_ready_for_operator_package_materialization`。
  - 输出 selected channel manifests、candidate channel requirements、package pointers、table manifests、required columns、source response row ids 和 router validation command。
- 更新 `experiments/run_field_activation_matrix.py`：
  - 新增输出 `outputs/model_core_governance/field_activation_package_staging_manifest.json`。
  - `field_activation_matrix.json`、matrix markdown 和 manifest latest 指针同步 staging 状态。
- 更新 Agent50：
  - governance scorecard、`next_allowed_actions.NEW_CORE_INTERFACE` 和 `external_resume_conditions.new_core_interface` 现在消费 staging status、selected channel count、candidate channel count、can materialize 和 next operator action。
- 更新测试：
  - 默认模板路径下，staging manifest 必须阻断在 response preflight。
  - 填满 field response 后，staging manifest 可给出 `REAL_FIELD_REPLAY_PACKAGE_DIR` 包指针、R7 table manifest 和 R8u66 candidate requirement，但仍保持 no-write。

当前默认输出：

- `outputs/model_core_governance/field_activation_package_staging_manifest.json`
- 当前默认状态：
  - `staging_status=field_activation_package_staging_manifest_blocked_by_response_preflight`
  - `selected_channel_manifest_count=1`
  - `candidate_channel_requirement_count=2`
  - `selected_channel_ids=[R7_REAL_FIELD_PACKAGE]`
  - `candidate_channel_ids=[R7_REAL_FIELD_PACKAGE, R8U66_PATH_ENDPOINT_LABEL_PACKAGE]`
  - `package_pointers_to_set=[REAL_FIELD_REPLAY_PACKAGE_DIR]`
  - `can_materialize_no_write_package_candidates=False`
  - `can_resume_model_chain=False`
  - `can_write_to_actuator=False`
  - `can_write_to_release_gate=False`

smoke check：

- 临时生成填满 33 行 `data_origin=field` 的 response JSON，并用 `FIELD_ACTIVATION_RESPONSE_PATH` 指向它运行 `experiments/run_field_activation_matrix.py`。
- 观察到：
  - `field_activation_response_source_loaded_external_json`
  - `field_activation_response_ready_for_external_package_preflight`
  - `field_activation_package_assembly_plan_ready_for_no_write_package_staging`
  - `field_activation_package_staging_manifest_ready_for_operator_package_materialization`
  - `can_materialize_no_write_package_candidates=True`
  - `can_resume_model_chain=False`
  - `can_write_to_actuator=False`
  - `can_write_to_release_gate=False`
- smoke check 后已恢复默认无外部响应状态，避免把临时 response 留成项目事实。

边界：

- staging manifest 不是 field evidence，只是 operator 组包清单。
- 即使 staging ready，也只是可以由 operator materialize no-write 包目录并运行 router preflight；真正恢复主链仍需要 R7/Agent44 field package preflight、Agent54 path/endpoint preflight、field replay/holdout、operator review 或 release validation。
- 该轮增强的是验证治理层、工程化能力和可演化性，不改变 Agent48/49 控制策略，不产生现场结论。

## 2026-06-21 R8u-103：External Activation Router Priority Summary

目标：

- 承接 R8u-102 后的阶段门状态：当前最高价值不是继续堆叠内部 synthetic/template 模型，而是让外部证据接入链路更短、更自解释。
- 解决一个 scan 摩擦：`external_activation_router.json` 过去需要下游 agent 或人工解析 `route_rows` 才能知道最高优先阻断、下一步动作和验证命令。
- 将 Agent50 中已有的 router 优先路由逻辑前移到 router 产物本体，使单个 router JSON 就能回答“先修哪条外部通道、为什么、下一步跑什么”。
- 保持边界：不改变 route_ready 判定，不执行 field replay/formal search，不生成 field evidence，不恢复模型链，不写 actuator 或 release gate。

实现：

- 更新 `src/water_ai/external_activation_router.py`：
  - 新增 router 顶层字段 `priority_route_channel_id`、`priority_route_status`、`priority_route_ready`、`priority_route_can_resume_model_chain`。
  - 新增 `priority_route_preflight_status`、`highest_priority_blocker`、`next_operator_action`、`router_validation_command` 和 `priority_route_command`。
  - 优先级规则保持与 Agent50 一致：已提交但阻断的路径优先，其次 ready route，其次未提交路径的阻断 route。
- 更新 `experiments/run_external_activation_router.py`：
  - 终端输出、router markdown 和 manifest latest 指针同步顶层优先阻断摘要。
- 更新 Agent50：
  - `ModelCoreOptimizationGovernanceAgent` 优先消费 router 顶层 `highest_priority_blocker` 与 `next_operator_action`。
  - 若读取旧 router 结构，仍回退到 `route_rows` 推导，保持兼容。
- 更新测试：
  - 默认无路径时，router 顶层最高阻断为 `R7_REAL_FIELD_PACKAGE:REAL_FIELD_REPLAY_PACKAGE_DIR:not_set`。
  - 错误路径类型、field package preflight 阻断、R7 ready、path/endpoint ready 和 formal-search handoff ready 均验证顶层 priority summary。
  - Agent50 fixture 同步覆盖新 router 顶层摘要。

当前默认输出：

- `outputs/model_core_governance/external_activation_router.json`
- 当前默认状态：
  - `router_status=external_activation_router_waiting_for_external_paths`
  - `priority_route_channel_id=R7_REAL_FIELD_PACKAGE`
  - `priority_route_status=activation_route_waiting_for_env_var`
  - `highest_priority_blocker=R7_REAL_FIELD_PACKAGE:REAL_FIELD_REPLAY_PACKAGE_DIR:not_set`
  - `next_operator_action=set_REAL_FIELD_REPLAY_PACKAGE_DIR`
  - `router_validation_command=.venv/bin/python experiments/run_external_activation_router.py`
  - `boundary_preserved=True`

边界：

- router priority summary 只是路由/预检摘要，不是 field evidence。
- 顶层摘要 ready 不等于 actuator/release gate ready；所有真实恢复仍必须通过对应 package preflight、field replay/holdout、operator review 或 formal search/human review gate。
- 该轮增强的是验证治理层、工程化能力和可演化性：它减少后续 agent 扫描 `route_rows` 的摩擦，不改变 Agent48/49 控制策略，不产生现场结论。

## 2026-06-21 R8u-102：Field Activation Response Repair Work Order

目标：

- 承接 R8u-101 的 `FIELD_ACTIVATION_RESPONSE_PATH` 外部响应源预检。
- 解决一个真实接入摩擦：当外部 response 没有提交或未通过 source/schema/response/assembly preflight 时，operator 仍需要自己在多个 JSON 中扫描阻断原因。
- 将 source、schema、response 和 assembly 阻断合并为可机读 repair work order，明确最高优先修复项和下一步动作。
- 保持边界：repair work order 只指导修复响应包，不生成 field evidence，不运行 replay/holdout，不恢复模型链，不写 actuator 或 release gate。

实现：

- 更新 `src/water_ai/field_activation_matrix.py`：
  - 新增 `build_field_activation_response_repair_work_order()`。
  - 新增 source/schema/response/assembly 四类 repair item 生成规则。
  - 默认无外部响应时，最高优先修复项为 `R8U102_SUBMIT_FIELD_ACTIVATION_RESPONSE`。
  - 已填满外部响应并通过 response/assembly/schema 时，work order 进入 `field_activation_response_repair_work_order_ready_no_repairs_required`。
- 更新 `experiments/run_field_activation_matrix.py`：
  - 新增输出 `outputs/model_core_governance/field_activation_response_repair_work_order.json`。
  - `field_activation_matrix.json`、`field_activation_matrix.md` 和 manifest latest 指针同步 repair work order 状态。
- 更新 Agent50：
  - governance scorecard、`next_allowed_actions.NEW_CORE_INTERFACE` 和 `external_resume_conditions.new_core_interface` 现在消费 repair work order 状态、repair item count 和 highest priority repair id。
- 更新测试：
  - 默认模板路径下，work order 状态为 `field_activation_response_repair_work_order_waiting_for_external_response`。
  - repair item 包含提交外部 response、确认 no-write、补齐 alignment、替换 template/value payload markers、设置 data_origin=field 和完成 response preflight before assembly。
  - 已填满外部 response 后，work order repair item count 为 0，但仍保持 no-write。

当前默认输出：

- `outputs/model_core_governance/field_activation_response_repair_work_order.json`
- 当前默认状态：
  - `work_order_status=field_activation_response_repair_work_order_waiting_for_external_response`
  - `repair_item_count=7`
  - `highest_priority_repair_id=R8U102_SUBMIT_FIELD_ACTIVATION_RESPONSE`
  - `next_operator_action=fill_response_template_and_set_FIELD_ACTIVATION_RESPONSE_PATH`
  - `can_resume_model_chain=False`
  - `can_write_to_actuator=False`
  - `can_write_to_release_gate=False`

边界：

- 修复工单不是 field evidence，也不是 replay 结果。
- 即使 repair work order ready，仍只能进入 no-write package staging candidate；真正恢复主链仍需要 R7/Agent44 field package preflight、Agent54 path label preflight、holdout/replay/operator review/release validation。
- 该轮增强的是验证治理层、工程化能力和可保护性，不改变 Agent48/49 控制策略，不产生现场结论。

## 2026-06-21 R8u-101：Field Activation Response Source Preflight

目标：

- 承接 R8u-100 的结构合同，把 field activation 从“只能默认用模板跑预检”推进为“可通过环境变量提交填写后的外部响应 JSON”。
- 解决现场接入摩擦：如果现场人员已经按 33 行 response template 填完真实 batch/timestamp/node/sensor/lab/operation 证据，系统应能直接读取该响应包并自动跑 source preflight、response preflight、assembly plan 和 schema preflight。
- 保持边界：source preflight 只检查响应源是否提供、文件是否可读、根结构是否可进入 response preflight；即使外部响应通过，也只进入 no-write package staging candidate，不能恢复模型链、不能写 actuator、不能写 release gate。

实现：

- 更新 `src/water_ai/field_activation_matrix.py`：
  - 新增 `preflight_field_activation_response_source()`。
  - 输出 `source_preflight_status`、`external_response_supplied`、`using_default_template`、`can_run_response_preflight`、`selected_response_row_count` 和 no-write 边界。
- 更新 `experiments/run_field_activation_matrix.py`：
  - 支持 `FIELD_ACTIVATION_RESPONSE_PATH=/path/to/response.json`。
  - 默认无外部响应时继续使用 `field_activation_response_template.json`，并保持 response preflight 阻断。
  - 新增输出 `outputs/model_core_governance/field_activation_response_source_preflight.json`。
  - manifest、matrix JSON 和 matrix markdown 同步 source preflight 状态。
- 更新 Agent50：
  - governance scorecard、`next_allowed_actions.NEW_CORE_INTERFACE` 和 `external_resume_conditions.new_core_interface` 现在消费 response source preflight。
  - Agent50 可以区分“未提交外部响应，只能用默认模板”和“外部响应已提交，可进入 response preflight”。
- 更新 `deliverables/README.md`、`deliverables/artifact_index.md`、`notes/current_status.md`。

当前默认输出：

- `outputs/model_core_governance/field_activation_response_source_preflight.json`
- 默认状态：
  - `source_preflight_status=field_activation_response_source_using_default_template`
  - `external_response_supplied=False`
  - `can_run_response_preflight=True`
  - `response_preflight_status=field_activation_response_blocked_before_external_package_preflight`
  - `package_assembly_status=field_activation_package_assembly_plan_blocked_by_response_preflight`
  - `can_resume_model_chain=False`
  - `can_write_to_actuator=False`
  - `can_write_to_release_gate=False`

外部响应 smoke check：

- 临时生成一个填满 33 行 field 值的 response JSON，并用 `FIELD_ACTIVATION_RESPONSE_PATH` 指向它运行 `experiments/run_field_activation_matrix.py`。
- 观察到：
  - `field_activation_response_source_loaded_external_json`
  - `field_activation_response_ready_for_external_package_preflight`
  - `field_activation_package_assembly_plan_ready_for_no_write_package_staging`
  - `can_stage_external_package_candidates=True`
  - `can_resume_model_chain=False`
  - `can_write_to_actuator=False`
  - `can_write_to_release_gate=False`
- smoke check 后已恢复默认无外部响应状态，避免把临时测试包留成当前项目事实。

边界：

- `FIELD_ACTIVATION_RESPONSE_PATH` 指向的响应包即使通过 response preflight，也只是“状态级证据响应已可组装”的候选，不是 field replay 通过。
- 真正恢复模型链仍需要 R7/Agent44 field replay package preflight、Agent54 path label preflight、holdout/replay、operator review 或 release validation。
- 该轮提升的是验证治理层、工程落地能力和可保护性，不改变 Agent48/49 控制策略，不产生 field-supported claim。

## 2026-06-21 R8u-100：Field Activation Schema Contract / Schema Preflight

目标：

- 承接 R8u-97/98/99 的 field activation matrix、response template/preflight 和 package assembly plan。
- 解决一个接口层问题：当前已有 33 行状态级证据模板和外部包组装计划，但还缺少机器可读的结构合同，后续真实现场包提交前仍可能靠人工阅读 JSON 判断字段是否齐全。
- 保持边界：schema preflight 只检查字段骨架、channel/table 结构和 no-write flags，不检查 TODO 是否被真实 field 值替换，也不能恢复模型链、不能写 actuator、不能写 release gate。

实现：

- 更新 `src/water_ai/field_activation_matrix.py`：
  - 新增 `build_field_activation_schema_contract()`。
  - 新增 `preflight_field_activation_schema_contract()`。
  - 新增 response template、evidence row、package assembly、channel plan、table assembly 的必填字段合同。
  - 新增 no-write schema violation 检查，确保 assembly plan 与 channel plan 不能把 `can_resume_model_chain`、`can_write_to_actuator`、`can_write_to_release_gate` 置为 True。
- 更新 `experiments/run_field_activation_matrix.py`：
  - 新增输出 `outputs/model_core_governance/field_activation_schema_contract.json`。
  - 新增输出 `outputs/model_core_governance/field_activation_schema_preflight.json`。
  - `field_activation_matrix.json`、`field_activation_matrix.md` 和 manifest latest 指针均同步 schema 状态。
- 更新 Agent50：
  - `ModelCoreOptimizationGovernanceAgent` 现在消费 `field_activation_schema_preflight`。
  - governance scorecard、`next_allowed_actions.NEW_CORE_INTERFACE` 和 `external_resume_conditions.new_core_interface` 均输出 schema preflight 状态和 no-write 边界。
- 更新测试：
  - 当前 TODO/template 响应模板仍不能通过 field evidence preflight。
  - 同一模板可以通过 schema preflight，因为字段结构完整。
  - 删除任一必填响应字段会阻断 schema preflight。
  - Agent50 可读取 schema passed，但仍保持 `can_resume_model_chain=False`、`can_write_to_actuator=False`、`can_write_to_release_gate=False`。

当前输出：

- `outputs/model_core_governance/field_activation_schema_contract.json`
- `outputs/model_core_governance/field_activation_schema_preflight.json`
- 当前默认状态：
  - `schema_preflight_status=field_activation_schema_preflight_passed`
  - `can_validate_field_activation_response_structure=True`
  - `response_preflight_status=field_activation_response_blocked_before_external_package_preflight`
  - `package_assembly_status=field_activation_package_assembly_plan_blocked_by_response_preflight`
  - `can_resume_model_chain=False`
  - `can_write_to_actuator=False`
  - `can_write_to_release_gate=False`

验证：

- `.venv/bin/python -m py_compile src/water_ai/field_activation_matrix.py experiments/run_field_activation_matrix.py src/water_ai/agents/model_core_optimization_governance_agent.py experiments/run_agent50_model_core_governance.py tests/test_field_activation_matrix.py tests/test_model_core_optimization_governance_agent.py`：通过。
- `.venv/bin/pytest tests/test_field_activation_matrix.py tests/test_model_core_optimization_governance_agent.py -q`：42 passed。
- `.venv/bin/python experiments/run_field_activation_matrix.py`：通过，已刷新 matrix、response template/preflight、assembly plan、schema contract/preflight、manifest 和 matrix 说明。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：顺序重跑通过，已确认 Agent50 消费 R8u-100 schema 输出。
- `.venv/bin/pytest tests/test_field_activation_matrix.py tests/test_model_core_optimization_governance_agent.py tests/test_external_activation_router.py -q`：48 passed。
- `.venv/bin/pytest -q`：490 passed。

边界：

- schema preflight passed 只表示“结构可验”，不是“现场证据成立”。
- 当前 response template 仍含 TODO/template markers，必须由真实 `data_origin=field` 行替换后才可能进入 field activation response preflight。
- R8u-100 不改变 Agent48/49 控制策略，不新增现场结论，不写执行器，不写放行门。

## 2026-06-21 R8u-87：R7 Submission Repair Response Preflight

目标：

- 承接 R8u-86 的 R7 submission repair work order，把“列出 13 个补包项”继续推进为“operator 是否逐项响应、响应是否仍是模板/TODO、是否允许重跑 R7 preflight”的可测试接口。
- 避免现场补包流程只停留在 work order 层：如果没有 response preflight，后续仍可能把“工单已生成”误读为“现场已修复”。
- 保持边界：operator response 即使通过，也只允许重跑 R7/Agent44 preflight，不能直接形成 field evidence、field claim、actuator writeback 或 release gate。

实现：

- 更新 `src/water_ai/real_field_replay_pipeline.py`：
  - 新增 `build_field_package_submission_repair_response_template()`。
  - 新增 `preflight_field_package_submission_repair_response()`。
  - `build_real_field_replay_pipeline()` 新增可选参数 `field_package_submission_repair_response`。
  - pipeline readiness 新增 `field_package_submission_repair_response_preflight_status`、`field_package_submission_repair_response_missing_item_count`、`field_package_submission_repair_response_template_marker_count` 和 `field_package_submission_repair_response_can_route_to_r7_preflight`。
- 更新 `experiments/run_r7_real_field_replay_pipeline.py`：
  - 支持 `FIELD_PACKAGE_SUBMISSION_REPAIR_RESPONSE_PATH=/path/to/repair_response.json`。
  - 新增输出 `outputs/r7_real_field_replay_pipeline/field_package_submission_repair_response_template.json`。
  - 新增输出 `outputs/r7_real_field_replay_pipeline/field_package_submission_repair_response_preflight.json`。
  - R7 report、deliverable 和 manifest 同步 response preflight 状态。
- 更新 Agent50：
  - `ModelCoreOptimizationGovernanceAgent` 现在消费 R7 response preflight 状态和 `can_route_to_r7_preflight`。
  - `external_activation_contract.json` 中的 `R7_REAL_FIELD_PACKAGE` channel 增加 response template/preflight 路径与路由状态。
  - manifest latest 指针新增 `latest_agent50_r7_submission_repair_response_preflight_status` 与 `latest_agent50_r7_submission_repair_response_can_route_to_r7_preflight`。
- 更新 `deliverables/README.md`、`deliverables/artifact_index.md`、`notes/current_status.md`：
  - 将 response template 和 response preflight 列为 R7 真实包入口的一等机器产物。

当前输出：

- `outputs/r7_real_field_replay_pipeline/field_package_submission_repair_response_template.json`
- `outputs/r7_real_field_replay_pipeline/field_package_submission_repair_response_preflight.json`
- 当前默认状态：
  - `preflight_status=repair_response_preflight_blocked_at_template_markers`
  - `required_work_item_count=13`
  - `response_row_count=13`
  - `submitted_item_count=0`
  - `template_marker_count=13`
  - `can_route_to_r7_preflight=False`
  - `next_operator_action=replace_todo_template_markers_before_submission`

验证：

- `.venv/bin/python -m py_compile src/water_ai/real_field_replay_pipeline.py experiments/run_r7_real_field_replay_pipeline.py tests/test_real_field_replay_pipeline.py`：通过。
- `.venv/bin/pytest -q tests/test_real_field_replay_pipeline.py`：6 passed。
- `.venv/bin/python experiments/run_r7_real_field_replay_pipeline.py`：通过，已刷新 R7 report、metrics、deliverable、manifest、repair work order、repair response template 和 repair response preflight。
- `.venv/bin/python -m py_compile src/water_ai/agents/model_core_optimization_governance_agent.py experiments/run_agent50_model_core_governance.py tests/test_model_core_optimization_governance_agent.py`：通过。
- `.venv/bin/pytest -q tests/test_model_core_optimization_governance_agent.py`：34 passed。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：通过，已刷新 Agent50 governance report、priority ranking、external activation contract、core score gate 和 manifest。

边界：

- response template 是 operator 填报骨架，默认含 TODO/template markers，必须被阻断。
- response preflight ready 只表示 operator response 完整到可以重跑 R7 preflight，不表示真实 field package 已通过。
- 该轮增强的是验证治理层、工程落地能力和可保护性：补齐了“工单 -> operator 响应 -> 预检 -> 重跑 R7 preflight”的接口，不改变 Agent48/49 控制策略，不产生 field-supported claim。

## 2026-06-21 R8u-86：R7 Submission Repair Work Order

目标：

- 承接当前全局 goal 的阶段门判断：Agent50 core score 已到 0.96，继续扩展内部 agent 的边际收益低；最高价值问题是让真实 field package 能被清楚提交、修复和路由。
- 解决 R7 入口已有 `R7A_IMPORT_PREFLIGHT`、coverage patch plan 和 R8U66 path/endpoint alignment patch plan，但这些信息分散在多个结构里，现场操作者或后续 agent 仍需要多处 scan 才知道该补什么。
- 保持边界：只生成 submission repair work order，不合成 field rows，不升级 field claim，不写 actuator，不写 release gate。

实现：

- 更新 `src/water_ai/real_field_replay_pipeline.py`：
  - 新增 `field_package_submission_repair_work_order`。
  - 将 `coverage_patch_plan.items` 与 `field_path_endpoint_alignment_patch_plan.items` 标准化为 `repair_items`。
  - 每个 repair item 保留 `work_item_id`、source stage、source plan、target、action、acceptance、why_required 以及关键字段需求。
  - work order 同时输出 `submission_requirements` 与 `routing_contract`，明确 `REAL_FIELD_REPLAY_PACKAGE_DIR`、`data_origin=field`、拒收 header-only/template/synthetic rows、最小 3 个 replay matched batches、最小 5 个 path endpoint matched batches，以及 no-write 边界。
  - pipeline_readiness 新增 `field_package_submission_repair_work_order_status` 和 `field_package_submission_repair_item_count`。
- 更新 `experiments/run_r7_real_field_replay_pipeline.py`：
  - 新增输出 `outputs/r7_real_field_replay_pipeline/field_package_submission_repair_work_order.json`。
  - R7 report、deliverable 和 manifest 同步显示 work order status、item count 和路径。
- 更新 `src/water_ai/agents/model_core_optimization_governance_agent.py` 与 `experiments/run_agent50_model_core_governance.py`：
  - Agent50 scorecard、field evidence wait status 和 external activation contract 现在消费 R7 submission repair work order。
  - manifest latest 指针新增 `latest_agent50_r7_submission_repair_work_order_status`、`latest_agent50_r7_submission_repair_item_count` 和 work order path。
- 更新 `tests/test_real_field_replay_pipeline.py`：
  - header-only template 必须生成 `field_package_submission_repair_work_order_blocked_at_import_preflight`。
  - repair items 必须包含 `R7A_METADATA_PLACEHOLDERS`、真实行补包项和 `R8U76_MINIMUM_MATCHED_BATCH_DEFICIT`。
  - path/endpoint deficit 必须进入 work order requirements。
  - no-write 边界必须保持为 actuator/release gate 均不可写。
- 更新 `deliverables/README.md`、`deliverables/artifact_index.md`、`notes/current_status.md`：
  - 将新工单列为 R7 真实包入口的一等机器产物。

当前输出：

- `outputs/r7_real_field_replay_pipeline/field_package_submission_repair_work_order.json`
- 当前状态：
  - `work_order_status=field_package_submission_repair_work_order_blocked_at_import_preflight`
  - `highest_priority_blocker=R7A_IMPORT_PREFLIGHT`
  - `repair_item_count=13`
  - `can_write_to_actuator=False`
  - `can_write_to_release_gate=False`
- 当前 13 个修复项把 R7A metadata/真实 timestamped rows、R7I 最小 replay 契约和 R8U66 path/endpoint 对齐缺口合并为一个 operator work order。

验证：

- `.venv/bin/python -m py_compile src/water_ai/real_field_replay_pipeline.py experiments/run_r7_real_field_replay_pipeline.py tests/test_real_field_replay_pipeline.py`：通过。
- `.venv/bin/pytest -q tests/test_real_field_replay_pipeline.py`：5 passed。
- `.venv/bin/python experiments/run_r7_real_field_replay_pipeline.py`：通过，已刷新 R7 report、metrics、deliverable、manifest 和 submission repair work order。
- `.venv/bin/python -m py_compile src/water_ai/agents/model_core_optimization_governance_agent.py experiments/run_agent50_model_core_governance.py tests/test_model_core_optimization_governance_agent.py`：通过。
- `.venv/bin/pytest -q tests/test_model_core_optimization_governance_agent.py`：34 passed。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：通过，已刷新 Agent50 governance report、priority ranking、external activation contract、core score gate 和 manifest。

边界：

- 该 work order 只把真实包提交与修复路线变清楚，不能替代真实 `data_origin=field` 的 package rows。
- 当前 header-only template 仍正确停在 import preflight；`repair_item_count=13` 是补包需求数量，不是现场验证通过数量。
- 这轮增强的是验证治理层和工程落地能力，解决一个 P1/P2 真实包接入阻断，因此符合当前 goal 的“解决硬阻断”有效迭代条件；它不改变 Agent48/49 控制策略，不主张 field-supported control performance。

## 2026-06-15 CodeGraph：项目结构知识图谱入口

目标：

- 响应“调用 GitHub 上的 codegraph skill，构建知识图谱以减少 scan 摩擦”。
- 后续进入项目时先读图谱，再按 Agent、runner、source、test、deliverable、output 跳转，避免每次重新全仓搜索。
- 保持边界：CodeGraph 只提供结构定位和依赖线索，不替代测试、实验、field replay、holdout 或人工复核。

实现：

- 使用 `skill-installer` 从 GitHub `lzehrung/codegraph` 安装 `codegraph-skill/codegraph` 到 `~/.codex/skills/codegraph`。
- 读取该 skill 的 `SKILL.md`，确认推荐工作流为 `codegraph doctor`、`codegraph orient --root . --budget small --json`、`packet/search/explain/deps/rdeps/impact/review` 等。
- 当前机器没有 Node.js 24.10+、`npm`、`npx`、`gh`、`brew` 或 `codegraph` CLI，因此未强行安装大运行时；改用项目本地 fallback。
- 新增 `codegraph.config.json`，固定未来原生 CodeGraph CLI 可复用的扫描边界。
- 新增 `tools/build_project_codegraph.py`，用 Python AST、Markdown/JSON 元数据和路径引用生成项目级静态图谱。
- 生成：
  - `CODEGRAPH.md`
  - `deliverables/codegraph/project_codegraph.json`
  - `deliverables/codegraph/project_codegraph_nodes.csv`
  - `deliverables/codegraph/project_codegraph_edges.csv`
  - `deliverables/codegraph/codegraph_summary.md`
  - `deliverables/codegraph/scan_shortcuts.md`
- 将 CodeGraph 入口接入 `deliverables/manifest.json`、`deliverables/README.md` 和 `notes/current_status.md`。

当前输出：

- 文件数：319。
- 节点数：3895。
- 边数：6320。
- Agent workflow 数：58。
- 覆盖关系包括：文件、Python class/function、import、内部 import、experiment-agent、test-source、deliverable/output 引用、Markdown heading 和路径引用。
- Agent7-9 在当前项目中没有独立 `run_agent7/8/9` runner，因此 workflow 计数为 58，并非扫描漏项。

验证：

- `.venv/bin/python -m py_compile tools/build_project_codegraph.py`：通过。
- `.venv/bin/python tools/build_project_codegraph.py`：通过，成功生成图谱文件。
- JSON 二次读取与摘要抽样检查：通过。

边界：

- 该图谱不是原生 CodeGraph CLI 的 AST/tree-sitter artifact；它是当前机器无 Node/CLI 条件下的项目本地静态图谱。
- 图谱关系是“定位线索”，不能作为运行时行为或现场有效性的证据。
- 若后续安装 Node.js 24.10+ 和 `@lzehrung/codegraph`，可按 `codegraph.config.json` 生成原生 CodeGraph artifact，并用 `orient/search/packet/explain/impact/review` 进一步降低扫描成本。

## 2026-06-04 R8u-46：Formal Disclosure Revision Impact Plan

目标：

- 承接 R8u-45 的 formal disclosure revision queue，把“人工交底修订任务”继续映射到具体核心交底工件。
- 避免正式审查回填只停留在孤立队列里，导致无法知道它会影响技术特征、实施例、技术效果、现有技术区别或后续检索工作包。
- 保持边界：impact plan 只做人工修订路由，不自动改写核心工件，不生成权利要求文本，不生成 prior-art 结论，不提供法律意见，不升级 field claim。

实现：

- `src/water_ai/agents/agent_architecture_consolidation_agent.py`：
  - 新增 `_formal_disclosure_revision_impact_plan()`。
  - 默认状态为 `formal_disclosure_revision_impact_plan_blocked_at_revision_queue`。
  - 只有 `formal_disclosure_revision_queue_ready_for_human_disclosure_editor` 后，才读取 `disclosure_revision_items` 并生成 `revision_impact_items`。
  - 每个 impact item 保留 `disclosure_revision_item_id`、`claim_scope_patch_id`、work package、hit、revision action、approved technical revision summary、required disclosure revision、preserved field validation gate、follow-up evidence/search 和 formal review trace id。
  - 每个 impact item 会路由到 `patent_technical_feature_ledger`、`technical_claim_skeleton_scaffold`、`technical_embodiment_validation_matrix`、`technical_effect_measurement_matrix`、`prior_art_distinction_matrix`；当需要补充检索/证据时，再追加 `formal_search_work_package_matrix`。
  - 输出始终保持 `can_apply_artifact_patch_automatically=False`、`can_emit_claim_text=False`、`can_generate_prior_art_result=False`、`legal_opinion_allowed=False`、`field_claim_upgrade_allowed=False`。
- `experiments/run_agent60_agent_architecture_consolidation.py`：
  - 新增 `outputs/agent_architecture_consolidation/formal_disclosure_revision_impact_plan.json`。
  - Agent60 report、deliverable package 和 manifest 已索引 impact plan。
- `tests/test_agent_architecture_consolidation_agent.py`：
  - 默认阻断路径新增 impact plan 断言。
  - 提交正式检索包但尚未进入正式审查时，确认 impact plan 仍被 revision queue 阻断。
  - 完整临时正式检索包、人工非法律回填包和外部正式审查回填包通过后，确认 impact plan 生成 7 条人工工件修订影响项。
  - 每条 impact item 必须回连核心工件，且不能自动改写、不能生成 claim text、不能生成 prior-art result。

当前输出：

- 新增文件：
  - `outputs/agent_architecture_consolidation/formal_disclosure_revision_impact_plan.json`
- 当前默认状态：
  - `formal_disclosure_revision_impact_plan_status=formal_disclosure_revision_impact_plan_blocked_at_revision_queue`
  - `linked_formal_disclosure_revision_queue_status=formal_disclosure_revision_queue_blocked_at_formal_counsel_review_response`
  - `revision_impact_item_count=0`
  - `can_route_to_human_artifact_revision=False`
  - `can_apply_artifact_patch_automatically=False`
  - `can_emit_claim_text=False`
  - `can_generate_prior_art_result=False`
  - `legal_opinion_allowed=False`
  - `field_claim_upgrade_allowed=False`

验证：

- `.venv/bin/python -m py_compile src/water_ai/agents/agent_architecture_consolidation_agent.py experiments/run_agent60_agent_architecture_consolidation.py tests/test_agent_architecture_consolidation_agent.py`：通过。
- `.venv/bin/pytest -q tests/test_agent_architecture_consolidation_agent.py`：51 passed。
- `.venv/bin/python experiments/run_agent60_agent_architecture_consolidation.py`：通过，已刷新 `formal_disclosure_revision_impact_plan.json`、deliverable 和 manifest。
- `.venv/bin/pytest -q tests/test_pressure_resolution_replay_scenario_pack_agent.py tests/test_agent_architecture_consolidation_agent.py`：82 passed。
- `.venv/bin/pytest -q`：430 passed。

边界：

- `formal_disclosure_revision_impact_plan_ready_for_human_artifact_revision` 只表示外部正式审查结果已经能映射到人工修订的核心技术工件，不表示系统可以自动修订技术交底，不表示能生成权利要求，不表示 prior-art 检索完成，也不表示现场验证成立。
- 该层提升的是专利级技术交底成熟度里的“修订影响可追溯性”：正式审查意见进入后，能清楚知道应该触达哪些技术特征、实施例、效果、区别和检索工件。

## 2026-06-04 R8u-45：Formal Disclosure Revision Queue Scaffold

目标：

- 承接 R8u-44 的 formal counsel review response preflight，把“外部正式审查回填通过预检”的结果继续推进为“技术交底修订任务队列”。
- 避免外部正式审查回填一通过，系统就自动改写交底、生成权利要求文本或形成法律/现场结论。
- 保持边界：disclosure revision queue 只把修订要求排队给人工交底编辑；系统不自动应用修订，不生成 claim text，不判断授权，不绕过 field validation gate。

实现：

- `src/water_ai/agents/agent_architecture_consolidation_agent.py`：
  - 新增 `_formal_disclosure_revision_queue()`。
  - 默认状态为 `formal_disclosure_revision_queue_blocked_at_formal_counsel_review_response`。
  - 只有 `formal_counsel_review_response_ready_for_disclosure_revision_queue` 后，才读取 `accepted_formal_review_rows` 并生成 `disclosure_revision_items`。
  - 每个 queue item 保留 `claim_scope_patch_id`、work package、hit、scope disposition、revision action、approved technical revision summary、required disclosure revision、preserved field validation gate、follow-up evidence/search 和 formal review trace id。
  - 输出始终保持 `can_apply_disclosure_revision_automatically=False`、`can_emit_claim_text=False`、`can_generate_prior_art_result=False`、`legal_opinion_allowed=False`、`field_claim_upgrade_allowed=False`。
- `experiments/run_agent60_agent_architecture_consolidation.py`：
  - 新增 `outputs/agent_architecture_consolidation/formal_disclosure_revision_queue.json`。
  - Agent60 report、deliverable package 和 manifest 已索引 disclosure revision queue。
- `tests/test_agent_architecture_consolidation_agent.py`：
  - 默认阻断路径新增 queue 断言。
  - 完整临时正式检索包、人工非法律回填包和外部正式审查回填包通过后，确认 queue 生成 7 条修订任务。
  - 每条修订任务必须保持人工编辑边界，不能自动应用、不能生成 claim text。

当前输出：

- 新增文件：
  - `outputs/agent_architecture_consolidation/formal_disclosure_revision_queue.json`
- 当前默认状态：
  - `formal_disclosure_revision_queue_status=formal_disclosure_revision_queue_blocked_at_formal_counsel_review_response`
  - `linked_formal_counsel_review_response_status=formal_counsel_review_response_preflight_blocked_at_template`
  - `revision_item_count=0`
  - `can_route_to_disclosure_editor=False`
  - `can_apply_disclosure_revision_automatically=False`
  - `can_emit_claim_text=False`
  - `can_generate_prior_art_result=False`
  - `legal_opinion_allowed=False`
  - `field_claim_upgrade_allowed=False`

验证：

- `.venv/bin/python -m py_compile src/water_ai/agents/agent_architecture_consolidation_agent.py experiments/run_agent60_agent_architecture_consolidation.py tests/test_agent_architecture_consolidation_agent.py`：通过。
- `.venv/bin/pytest -q tests/test_agent_architecture_consolidation_agent.py`：51 passed。
- `.venv/bin/python experiments/run_agent60_agent_architecture_consolidation.py`：通过，重新生成 Agent60 deliverable、metrics、manifest 和 formal disclosure revision queue。
- `.venv/bin/pytest -q tests/test_pressure_resolution_replay_scenario_pack_agent.py tests/test_agent_architecture_consolidation_agent.py`：82 passed。
- `.venv/bin/pytest -q`：430 passed。

边界：

- `formal_disclosure_revision_queue_ready_for_human_disclosure_editor` 只表示外部正式审查结果已被转成可处理的技术交底修订任务，不表示系统可以自动修订。
- 技术交底修订仍必须由人工编辑/正式审查流程确认，系统只提供任务队列和证据边界。
- 任何现场成立仍必须通过 field replay、holdout、operator review 和 release gate。

## 2026-06-04 R8u-44：Formal Counsel Review Response Template and Source Preflight

目标：

- 承接 R8u-43 的 claim scope patch draft，把“待正式专利代理人/法律审查的技术范围修补建议”继续推进为“外部正式审查结果如何回填、如何预检、如何只进入技术交底修订队列”的响应合同。
- 避免系统把 claim scope patch draft 直接改写成权利要求文本、授权判断、法律意见或 field-supported claim。
- 保持边界：formal counsel review response preflight 只验收外部正式审查回填包的结构、patch 覆盖和边界声明；通过后只能进入 disclosure revision queue，不能由系统生成专利法律结论。

实现：

- `src/water_ai/agents/agent_architecture_consolidation_agent.py`：
  - 新增 `FORMAL_COUNSEL_REVIEW_RESPONSE_FIELDS` 和 `FORBIDDEN_FORMAL_COUNSEL_ROUTING_TERMS`。
  - `AgentArchitectureConsolidationAgent` 新增可选 `formal_counsel_review_response_path`。
  - 新增 `_formal_counsel_review_response_template()`：只有 claim scope patch draft ready 时，才生成每个 `claim_scope_patch_id` 对应的 formal response template row；默认被 claim scope patch draft 阻断。
  - 新增 `_formal_counsel_review_response_source_preflight()`：读取 `FORMAL_COUNSEL_REVIEW_RESPONSE_PATH` 指向的 JSON 包，检查 root、metadata、review_rows、必填字段、claim scope patch 覆盖、template/TODO marker 和越界法律/field claim 文本。
  - 通过时输出 `formal_counsel_review_response_ready_for_disclosure_revision_queue`、accepted/rejected row count、`external_formal_review_completed=True` 和 `can_route_to_disclosure_revision_queue=True`；仍保持 `can_emit_claim_text=False`、`can_generate_prior_art_result=False`、`legal_opinion_allowed=False`、`field_claim_upgrade_allowed=False`。
- `experiments/run_agent60_agent_architecture_consolidation.py`：
  - 新增 `outputs/agent_architecture_consolidation/formal_counsel_review_response_template.json`。
  - 新增 `outputs/agent_architecture_consolidation/formal_counsel_review_response_source_preflight.json`。
  - 支持环境变量 `FORMAL_COUNSEL_REVIEW_RESPONSE_PATH`。
  - Agent60 report、deliverable package 和 manifest 已索引 formal counsel review response template/source preflight。
- `tests/test_agent_architecture_consolidation_agent.py`：
  - 默认无 claim draft ready 时新增 formal counsel template/preflight 阻断断言。
  - 完整临时正式检索包 + 人工非法律回填包可生成 formal counsel response template，但未提交正式审查回填时仍等待 `FORMAL_COUNSEL_REVIEW_RESPONSE_PATH`。
  - 完整临时正式审查回填包可通过 source preflight 并路由到 disclosure revision queue，但仍不能生成权利要求文本、prior-art 结论、法律意见或 field-supported claim。

当前输出：

- 新增文件：
  - `outputs/agent_architecture_consolidation/formal_counsel_review_response_template.json`
  - `outputs/agent_architecture_consolidation/formal_counsel_review_response_source_preflight.json`
- 当前默认状态：
  - `formal_counsel_review_response_template_status=formal_counsel_review_response_template_blocked_at_claim_scope_patch_draft`
  - `formal_counsel_review_response_source_status=formal_counsel_review_response_preflight_blocked_at_template`
  - `accepted_formal_review_row_count=0`
  - `rejected_formal_review_row_count=0`
  - `external_formal_review_completed=False`
  - `can_route_to_disclosure_revision_queue=False`
  - `can_emit_claim_text=False`
  - `can_generate_prior_art_result=False`
  - `legal_opinion_allowed=False`
  - `field_claim_upgrade_allowed=False`

验证：

- `.venv/bin/python -m py_compile src/water_ai/agents/agent_architecture_consolidation_agent.py experiments/run_agent60_agent_architecture_consolidation.py tests/test_agent_architecture_consolidation_agent.py`：通过。
- `.venv/bin/pytest -q tests/test_agent_architecture_consolidation_agent.py`：51 passed。
- `.venv/bin/python experiments/run_agent60_agent_architecture_consolidation.py`：通过，重新生成 Agent60 deliverable、metrics、manifest 和 formal counsel review response template/source preflight。
- `.venv/bin/pytest -q tests/test_pressure_resolution_replay_scenario_pack_agent.py tests/test_agent_architecture_consolidation_agent.py`：82 passed。
- `.venv/bin/pytest -q`：430 passed。

边界：

- `formal_counsel_review_response_ready_for_disclosure_revision_queue` 只表示外部正式审查回填包结构与覆盖可进入技术交底修订队列，不表示系统可生成权利要求文本。
- 本系统不解释或替代正式法律意见；`legal_opinion_allowed=False` 表示 Codex/模型侧不产生法律判断。
- 任何现场成立仍必须通过 field replay、holdout、operator review 和 release gate。

## 2026-06-04 R8u-43：Formal Search Claim Scope Patch Draft Scaffold

目标：

- 承接 R8u-42 的人工非法律技术比较回填 preflight，把已通过结构、覆盖和边界检查的 reviewer response 转成“技术范围修补草案”接口。
- 补上从人工技术比较到正式专利代理人审查之间的机器可读过渡层，避免人工 review 结果直接被误写为权利要求文本、prior-art 结论、法律意见或现场成立结论。
- 保持边界：claim scope patch draft 只路由到 formal counsel review；它不是法律意见，不生成权利要求文本，不判断新颖性/创造性/授权可能性，也不升级 field-supported claim。

实现：

- `src/water_ai/agents/agent_architecture_consolidation_agent.py`：
  - `_formal_search_nonlegal_review_response_source_preflight()` 新增 `accepted_review_rows`，仅在人工回填行必填字段完整、row id 覆盖、无 template marker、无法律/field 越界文本时保留已验收 reviewer row。
  - 新增 `_formal_search_claim_scope_patch_draft()`：默认停在 `formal_search_claim_scope_patch_draft_blocked_at_nonlegal_review_response`；只有 response preflight ready 后才生成 `claim_scope_patch_rows`。
  - 每条 draft row 保留 `review_packet_row_id`、`linked_work_package_id`、`hit_id`、`nonlegal_overlap_assessment`、`distinguishing_technical_detail`、`fallback_scope_recommendation`、`technical_patch_candidate`、`preserved_field_validation_gate` 和 trace id。
  - 输出始终保持 `can_emit_claim_text=False`、`can_generate_prior_art_result=False`、`legal_opinion_allowed=False`、`field_claim_upgrade_allowed=False`。
- `experiments/run_agent60_agent_architecture_consolidation.py`：
  - 新增 `outputs/agent_architecture_consolidation/formal_search_claim_scope_patch_draft.json`。
  - Agent60 report、deliverable package 和 manifest 已索引 claim scope patch draft 路径、状态、patch count、正式审查路由和禁止直接生成权利要求文本的边界。
- `tests/test_agent_architecture_consolidation_agent.py`：
  - 默认无人工回填路径时新增 claim scope patch draft 阻断断言。
  - 完整临时正式检索包但未提交人工回填时，claim draft 仍被 response preflight 阻断。
  - 完整临时正式检索包 + 完整人工非法律回填包时，确认生成 7 条 draft patch row，并且每条 row 只能进入 `formal_patent_counsel_review_required`。

当前输出：

- 新增文件：
  - `outputs/agent_architecture_consolidation/formal_search_claim_scope_patch_draft.json`
- 当前默认状态：
  - `formal_search_claim_scope_patch_draft_status=formal_search_claim_scope_patch_draft_blocked_at_nonlegal_review_response`
  - `linked_nonlegal_review_response_status=formal_search_nonlegal_review_response_preflight_blocked_at_template`
  - `draft_patch_count=0`
  - `can_route_to_formal_counsel_review=False`
  - `can_emit_claim_text=False`
  - `can_generate_prior_art_result=False`
  - `legal_opinion_allowed=False`
  - `field_claim_upgrade_allowed=False`

验证：

- `.venv/bin/python -m py_compile src/water_ai/agents/agent_architecture_consolidation_agent.py experiments/run_agent60_agent_architecture_consolidation.py`：通过。
- `.venv/bin/pytest -q tests/test_agent_architecture_consolidation_agent.py`：51 passed。
- `.venv/bin/python experiments/run_agent60_agent_architecture_consolidation.py`：通过，重新生成 Agent60 deliverable、metrics、manifest 和 claim scope patch draft。
- `.venv/bin/pytest -q tests/test_pressure_resolution_replay_scenario_pack_agent.py tests/test_agent_architecture_consolidation_agent.py`：82 passed。
- `.venv/bin/pytest -q`：430 passed。

边界：

- `formal_search_claim_scope_patch_draft_ready_for_formal_counsel_review` 只表示技术范围修补建议可交给正式专利代理人审查，不表示可授权、不表示新颖性/创造性成立。
- `technical_patch_candidate` 只是根据人工非法律 fallback 文本做的候选分类，不能替代正式 claim drafting。
- 任何现场成立仍必须通过 field replay、holdout、operator review 和 release gate；任何法律判断仍必须通过正式专利检索报告和法律审查。

## 2026-06-04 R8u-42：Formal Search Nonlegal Review Response Template and Source Preflight

目标：

- 承接 R8u-41 的 formal search nonlegal comparison review packet，把“人工非法律技术比较审查任务”继续推进为“人工 reviewer 如何回填、如何预检、如何保持非法律和非现场结论边界”的响应合同。
- 避免人工审查结果以自由文本方式直接进入模型，导致把技术比较意见误写成 prior-art 结论、法律意见、授权判断或 field-supported claim。
- 保持边界：review response preflight 只验收人工非法律技术比较回填包；通过后也只能进入 claim scope patch draft，不能生成 prior-art result 或现场 claim。

实现：

- `src/water_ai/agents/agent_architecture_consolidation_agent.py`：
  - 新增 `NONLEGAL_REVIEW_RESPONSE_FIELDS`。
  - `AgentArchitectureConsolidationAgent` 新增可选 `formal_search_nonlegal_review_response_path`。
  - 新增 `_formal_search_nonlegal_review_response_template()`：只有 review packet ready 时，才生成每个 review packet row 对应的 response template row；默认被 review packet 阻断。
  - 新增 `_formal_search_nonlegal_review_response_source_preflight()`：读取 `FORMAL_SEARCH_NONLEGAL_REVIEW_RESPONSE_PATH` 指向的 JSON 包，检查 root、metadata、review_rows、必填字段、review packet row 覆盖、template/TODO marker 和法律/field claim 越界文本。
  - 通过时输出 `formal_search_nonlegal_review_response_ready_for_claim_scope_patch_draft`、accepted/rejected row count、`human_review_completed=True` 和 `can_route_to_claim_scope_patch_draft=True`；仍保持 `can_generate_prior_art_result=False`、`legal_opinion_allowed=False`、`field_claim_upgrade_allowed=False`。
- `experiments/run_agent60_agent_architecture_consolidation.py`：
  - 新增 `outputs/agent_architecture_consolidation/formal_search_nonlegal_review_response_template.json`。
  - 新增 `outputs/agent_architecture_consolidation/formal_search_nonlegal_review_response_source_preflight.json`。
  - 支持环境变量 `FORMAL_SEARCH_NONLEGAL_REVIEW_RESPONSE_PATH`。
  - Agent60 report、deliverable package 和 manifest 已索引 response template/source preflight。
- `tests/test_agent_architecture_consolidation_agent.py`：
  - 默认无提交包测试新增 response template/preflight 断言，确认它们分别停在 review packet/template 阻断后。
  - 完整临时正式检索包测试新增 response template waiting 断言。
  - 新增完整临时人工回填包路径，确认 7 行 reviewer response 可通过 source preflight 并路由到 claim scope patch draft，但仍不能生成 prior-art/法律/field claim。

当前输出：

- 新增文件：
  - `outputs/agent_architecture_consolidation/formal_search_nonlegal_review_response_template.json`
  - `outputs/agent_architecture_consolidation/formal_search_nonlegal_review_response_source_preflight.json`
- 当前默认状态：
  - `formal_search_nonlegal_review_response_template_status=formal_search_nonlegal_review_response_template_blocked_at_review_packet`
  - `formal_search_nonlegal_review_response_source_status=formal_search_nonlegal_review_response_preflight_blocked_at_template`
  - `accepted_review_row_count=0`
  - `rejected_review_row_count=0`
  - `human_review_completed=False`
  - `can_route_to_claim_scope_patch_draft=False`
  - `can_generate_prior_art_result=False`
  - `legal_opinion_allowed=False`
  - `field_claim_upgrade_allowed=False`

验证：

- `.venv/bin/python -m py_compile src/water_ai/agents/agent_architecture_consolidation_agent.py experiments/run_agent60_agent_architecture_consolidation.py tests/test_agent_architecture_consolidation_agent.py`：通过。
- `.venv/bin/pytest tests/test_agent_architecture_consolidation_agent.py -q`：51 passed。
- `.venv/bin/python experiments/run_agent60_agent_architecture_consolidation.py`：通过，重新生成 Agent60 deliverable、metrics、manifest、review response template 和 source preflight。
- `.venv/bin/pytest tests/test_pressure_resolution_replay_scenario_pack_agent.py tests/test_agent_architecture_consolidation_agent.py -q`：82 passed。
- `.venv/bin/pytest -q`：430 passed。

边界：

- Template ready 只表示人工 reviewer 有可填写的回填合同，不表示审查完成。
- Source preflight 通过只表示人工非法律技术比较回填包结构、覆盖和边界声明合格，不表示 prior-art 结论成立。
- `can_route_to_claim_scope_patch_draft=True` 只允许进入下一步技术范围补丁草案；不能直接形成权利要求文本、法律意见、授权判断或 field-supported claim。
- 任何法律/授权判断仍必须走正式检索报告和专利代理人审查；任何现场成立仍必须走 field replay、holdout、operator review 和 release gate。

## 2026-06-04 R8u-41：Formal Search Nonlegal Comparison Review Packet

目标：

- 承接 R8u-40 的 formal search result validation execution，把“结构验收 ready 的检索命中”继续推进为“可交给人工 reviewer 的非法律技术比较审查任务包”。
- 让后续审查聚焦具体技术区别、实施例影响、claim fallback、field validation gate 保留和证据边界，而不是直接生成 prior-art 结论或法律判断。
- 保持边界：review packet 不是审查结果，不是正式检索报告，不是法律意见，不判断新颖性/创造性/授权可能性，也不能把检索结果升级为 field-supported claim。

实现：

- `src/water_ai/agents/agent_architecture_consolidation_agent.py`：
  - 新增 `_formal_search_nonlegal_comparison_review_packet()`。
  - 默认消费 `formal_search_result_validation_execution`；若 execution 不是 `formal_search_result_validation_execution_ready_for_human_nonlegal_comparison_review`，则返回 `formal_search_nonlegal_review_packet_blocked_at_validation_execution`。
  - 当 execution ready 时，为每条结构验收通过的 hit 生成 review packet row，回连 validation gate、work package、hit、source database、matched query 和 covered project element。
  - 每行审查任务包含 technical distinction review questions、allowed nonlegal review outputs、required reviewer fields 和 cannot_do 边界。
  - required reviewer fields 包含 `reviewer_id`、`review_time`、`nonlegal_overlap_assessment`、`distinguishing_technical_detail`、`fallback_scope_recommendation`、`preserved_field_validation_gate`、`evidence_boundary_acknowledgement` 和 trace id。
  - 即使 packet ready，也保持 `human_review_completed=False`、`can_generate_prior_art_result=False`、`legal_opinion_allowed=False`、`field_claim_upgrade_allowed=False`。
- `experiments/run_agent60_agent_architecture_consolidation.py`：
  - 新增 `outputs/agent_architecture_consolidation/formal_search_nonlegal_comparison_review_packet.json`。
  - Agent60 report、deliverable package 和 manifest 已索引 review packet。
  - manifest 新增 review packet status、row count、human review completed、can enter review、prior-art generation/legal/field boundary flags。
- `tests/test_agent_architecture_consolidation_agent.py`：
  - 默认无提交包测试新增 review packet 断言，确认它停在 validation execution 阻断后，不生成审查包行。
  - 完整临时提交包测试新增 review packet 断言，确认可生成 7 行人工非法律技术比较审查任务，且每行含 required reviewer fields 与 cannot_do 边界。

当前输出：

- 新增文件：
  - `outputs/agent_architecture_consolidation/formal_search_nonlegal_comparison_review_packet.json`
- 当前默认状态：
  - `formal_search_nonlegal_comparison_review_packet_status=formal_search_nonlegal_review_packet_blocked_at_validation_execution`
  - `validation_execution_status=formal_search_result_validation_execution_blocked_at_row_preflight`
  - `review_packet_row_count=0`
  - `human_review_completed=False`
  - `can_enter_human_nonlegal_comparison_review=False`
  - `can_generate_prior_art_result=False`
  - `legal_opinion_allowed=False`
  - `field_claim_upgrade_allowed=False`

验证：

- `.venv/bin/python -m py_compile src/water_ai/agents/agent_architecture_consolidation_agent.py experiments/run_agent60_agent_architecture_consolidation.py tests/test_agent_architecture_consolidation_agent.py`：通过。
- `.venv/bin/pytest tests/test_agent_architecture_consolidation_agent.py -q`：51 passed。
- `.venv/bin/python experiments/run_agent60_agent_architecture_consolidation.py`：通过，重新生成 Agent60 deliverable、metrics、manifest 和 nonlegal comparison review packet。
- `.venv/bin/pytest tests/test_pressure_resolution_replay_scenario_pack_agent.py tests/test_agent_architecture_consolidation_agent.py -q`：82 passed。
- `.venv/bin/pytest -q`：430 passed。

边界：

- Packet ready 只表示“审查任务可交给人工 reviewer”，不表示人工审查已完成。
- Packet row 只提出技术比较问题和允许的非法律输出，不得写 novelty、inventiveness、patentability、authorization likelihood 或 field-supported claim。
- 临时测试包只证明任务包生成路径存在，不证明任何外部检索命中真实成立。
- 任何后续 claim scope 调整、正式检索结论或专利授权判断仍必须依赖外部正式检索、人工复核和法律审查；现场成立仍必须走 field replay、holdout、operator review 和 release gate。

## 2026-06-04 R8u-40：Formal Search Result Validation Execution

目标：

- 承接 R8u-39 的 row-level schema/provenance preflight，把“提交包行级干净”继续推进为“提交包能否在 validation gate 层形成结构验收计数和下一步人工非法律比较审查入口”。
- 只在 row preflight 通过后读取正式检索结果包；默认无包或 source/row preflight 阻断时，execution 必须保持阻断。
- 保持边界：validation execution 只做结构验收和 hit-comparison 回连统计，不生成 prior-art 结论，不生成法律意见，不判断授权可能性，也不产生 field-supported claim。

实现：

- `src/water_ai/agents/agent_architecture_consolidation_agent.py`：
  - 新增 `_formal_search_result_validation_execution()`。
  - 默认读取 `formal_search_result_package_source_preflight` 与 `formal_search_result_package_row_preflight`；若 row preflight 不是 `formal_search_result_package_row_preflight_ready_for_validation_gate`，则返回 `formal_search_result_validation_execution_blocked_at_row_preflight`。
  - 当 row preflight ready 时，重新读取提交包，按 work package 统计 `work_package_execution_count`、`execution_row_count`、`validated_hit_count`、`rejected_hit_count`、`comparison_row_count` 和 `fallback_row_count`。
  - 对每个 hit 检查是否存在 linked comparison，以及 comparison 是否覆盖 mapped claim/feature/effect；通过者只标记为 `structural_hit_validated_for_human_nonlegal_comparison_review`。
  - 即使结构验收 ready，也保持 `can_generate_prior_art_result=False`、`legal_opinion_allowed=False`、`field_claim_upgrade_allowed=False`。
- `experiments/run_agent60_agent_architecture_consolidation.py`：
  - 新增 `outputs/agent_architecture_consolidation/formal_search_result_validation_execution.json`。
  - Agent60 report、deliverable package 和 manifest 已索引 validation execution。
  - manifest 新增 execution status、package supplied、validated/rejected hit count、human nonlegal review readiness、prior-art generation/legal/field boundary flags。
- `tests/test_agent_architecture_consolidation_agent.py`：
  - 默认无提交包测试新增 validation execution 断言，确认它停在 row preflight 阻断后，不产生 hit count 或审查入口。
  - 完整临时提交包测试新增 execution 断言，确认 7 个 work package、7 条 hit、7 条 comparison 和 7 条 fallback 可得到结构验收 ready，但仍不生成 prior-art 结论、法律意见或 field-supported claim。

当前输出：

- 新增文件：
  - `outputs/agent_architecture_consolidation/formal_search_result_validation_execution.json`
- 当前默认状态：
  - `formal_search_result_validation_execution_status=formal_search_result_validation_execution_blocked_at_row_preflight`
  - `source_preflight_status=formal_search_result_package_preflight_waiting_for_submission_path`
  - `row_preflight_status=formal_search_result_package_row_preflight_blocked_at_source_preflight`
  - `work_package_execution_count=0`
  - `execution_row_count=0`
  - `validated_hit_count=0`
  - `rejected_hit_count=0`
  - `can_enter_human_nonlegal_comparison_review=False`
  - `can_generate_prior_art_result=False`
  - `legal_opinion_allowed=False`
  - `field_claim_upgrade_allowed=False`

验证：

- `.venv/bin/python -m py_compile src/water_ai/agents/agent_architecture_consolidation_agent.py experiments/run_agent60_agent_architecture_consolidation.py tests/test_agent_architecture_consolidation_agent.py`：通过。
- `.venv/bin/pytest tests/test_agent_architecture_consolidation_agent.py -q`：51 passed。
- `.venv/bin/python experiments/run_agent60_agent_architecture_consolidation.py`：通过，重新生成 Agent60 deliverable、metrics、manifest 和 validation execution。
- `.venv/bin/pytest tests/test_pressure_resolution_replay_scenario_pack_agent.py tests/test_agent_architecture_consolidation_agent.py -q`：82 passed。
- `.venv/bin/pytest -q`：430 passed。

边界：

- Execution ready 只表示“可进入人工非法律比较审查”，不是 prior-art 结论。
- 临时测试包只证明结构验收路径存在，不证明任何命中真实成立。
- 没有正式外部/人工检索结果包、人工复核和后续法律审查时，不能判断新颖性/创造性/授权概率。
- 无论 validation execution 是否 ready，都不能升级 field-supported claim；现场结论仍必须走 field replay、holdout、operator review 和 gate。

## 2026-06-04 R8u-39：Formal Search Result Package Row-Level Schema and Provenance Preflight

目标：

- 承接 R8u-38 的 formal search result submission skeleton/source/template-marker preflight，把“提交包是否像一个可验收文件”继续推进为“提交包内部每一行是否具备进入 validation gate 的结构、来源和证据边界”。
- 只有 source/root/template-marker 预检通过后，才允许进入行级检查；默认无正式检索包时必须停在 source preflight，不得伪造 prior-art result。
- 保持边界：row preflight 只检查提交包结构、来源回连、claim/feature/effect 覆盖和 reviewer 边界；它不是正式检索结论，不是法律意见，不证明新颖性/创造性，也不产生 field-supported claim。

实现：

- `src/water_ai/agents/agent_architecture_consolidation_agent.py`：
  - `REQUIRED_FORMAL_SEARCH_RESULT_PACKAGE_TEMPLATE_FIELDS` 新增 `mapped_claim_ids`、`mapped_feature_ids`、`mapped_effect_ids`，让正式检索包不仅回连 work package，还能回连潜在权利要求、技术特征和技术效果。
  - 新增 `FORBIDDEN_PRIOR_ART_REVIEW_TERMS`，阻断 reviewer/manifest/comparison/fallback 字段中出现法律意见、授权可能性、现场 claim 晋级等越界表述。
  - 新增 `_empty_required_fields()`、`_contains_forbidden_review_text()` 和 `_formal_search_result_package_row_preflight()`。
  - Row preflight 在 source ready 后逐项检查 root `package_metadata`、每个 work package 的 `package_manifest`、`prior_art_hit_table`、`claim_element_comparison_chart` 和 `fallback_claim_scope_recommendation`。
  - 检查内容包括必填字段、`linked_work_package_id` 回连、`source_database` 是否属于 allowed databases、`matched_query` 是否属于 generated/allowed query sources、comparison 的 `linked_hit_id` 是否存在、comparison 是否覆盖至少一个 mapped claim/feature/effect，以及各 reviewer 字段是否含法律/现场 claim 越界文本。
- `experiments/run_agent60_agent_architecture_consolidation.py`：
  - 新增 `outputs/agent_architecture_consolidation/formal_search_result_package_row_preflight.json`。
  - Agent60 report、deliverable package 和 manifest 已索引 row preflight。
  - manifest 新增 row preflight status、row gap count、comparison coverage gap count、forbidden review boundary count 和 can route to validation gate 等字段。
- `tests/test_agent_architecture_consolidation_agent.py`：
  - 默认无提交包测试新增 row preflight 断言，确认它停在 `formal_search_result_package_row_preflight_blocked_at_source_preflight`。
  - 新增完整临时正式检索包测试：覆盖 7 个 work package、7 条 hit row、7 条 comparison row、7 条 fallback row，且每条 comparison 至少回连一个 mapped claim/feature/effect。
  - 该临时包通过时，row preflight 可得到 `formal_search_result_package_row_preflight_ready_for_validation_gate`，但仍 `can_generate_prior_art_result=False`、`legal_opinion_allowed=False`、`field_claim_upgrade_allowed=False`。

当前输出：

- 新增文件：
  - `outputs/agent_architecture_consolidation/formal_search_result_package_row_preflight.json`
- 当前默认状态：
  - `formal_search_result_package_row_preflight_status=formal_search_result_package_row_preflight_blocked_at_source_preflight`
  - `source_preflight_status=formal_search_result_package_preflight_waiting_for_submission_path`
  - `checked_work_package_count=0`
  - `row_gap_count=0`
  - `comparison_coverage_gap_count=0`
  - `forbidden_review_boundary_count=0`
  - `can_route_to_validation_gate=False`
  - `can_generate_prior_art_result=False`
  - `legal_opinion_allowed=False`
  - `field_claim_upgrade_allowed=False`

验证：

- `.venv/bin/python -m py_compile src/water_ai/agents/agent_architecture_consolidation_agent.py experiments/run_agent60_agent_architecture_consolidation.py`：通过。
- `.venv/bin/pytest tests/test_agent_architecture_consolidation_agent.py -q`：51 passed。
- `.venv/bin/python experiments/run_agent60_agent_architecture_consolidation.py`：通过，重新生成 Agent60 deliverable、metrics、manifest 和 row preflight。
- `.venv/bin/pytest tests/test_pressure_resolution_replay_scenario_pack_agent.py tests/test_agent_architecture_consolidation_agent.py -q`：82 passed。
- `.venv/bin/pytest -q`：430 passed。

边界：

- 默认 `row_gap_count=0` 只表示还没有正式提交包可进入行级检查，不表示正式检索结果已经干净。
- 完整临时包测试只证明结构合同可 route 到 validation gate，不证明任何 prior-art 命中真实成立。
- Row preflight 通过后下一步仍是 R8u-36 validation gate；不得直接生成 prior-art comparison、法律意见、授权性判断或 field-supported claim。

## 2026-06-04 R8u-38：Formal Search Result Submission Skeleton and Template-Marker Preflight

目标：

- 承接 R8u-37 的 formal search result package template/source preflight，把“字段级提交合同”继续推进为可直接填报的 submission skeleton。
- 同时补上 template-marker preflight，防止将 skeleton、TODO、sample 或 template 行原样提交为正式 prior-art evidence。
- 保持边界：skeleton 不是正式检索结果，不是 prior-art hit，不是法律意见，原样提交必须被阻断。

实现：

- `src/water_ai/agents/agent_architecture_consolidation_agent.py`：
  - 新增 `REQUIRED_FORMAL_SEARCH_RESULT_SUBMISSION_TEMPLATE_FIELDS`。
  - 新增 `_formal_search_result_package_submission_template()`。
  - 新增 `_template_marker_gaps()`，递归扫描 `TODO_*`、`template_not_prior_art_evidence`、`sample_not_prior_art_evidence`、`template_not_legal_opinion` 和 `template_only=true`。
  - 增强 `_formal_search_result_package_source_preflight()`：除 source/path/root shape、work package 覆盖和必需表形状外，现在还输出 `template_marker_gaps`、`template_marker_gap_count`，并在存在模板标记时返回 `formal_search_result_package_failed_template_marker_preflight`。
- `experiments/run_agent60_agent_architecture_consolidation.py`：
  - 新增 `outputs/agent_architecture_consolidation/formal_search_result_package_submission_template.json`。
  - Agent60 report、deliverable 和 manifest 已索引 submission skeleton。
- `tests/test_agent_architecture_consolidation_agent.py`：
  - 新增测试确保 submission skeleton 字段完整、覆盖 7 个 work package、仍不能 route 到 validation gate。
  - 新增临时文件测试：将 skeleton 原样写入临时 JSON 并作为 `formal_search_result_package_path` 输入时，source preflight 必须返回 `formal_search_result_package_failed_template_marker_preflight`，且 `can_route_to_validation_gate=False`。

当前输出：

- 新增文件：
  - `outputs/agent_architecture_consolidation/formal_search_result_package_submission_template.json`
- 当前默认状态：
  - `submission_template_status=formal_search_result_package_submission_template_ready`
  - `submission_template_ready_status=formal_search_result_package_submission_template_complete`
  - `expected_work_package_count=7`
  - `formal_search_result_package_source_status=formal_search_result_package_preflight_waiting_for_submission_path`
  - `preflight_blockers=['FORMAL_SEARCH_RESULT_PACKAGE_PATH:not_set']`
  - `template_marker_gap_count=0`
  - `can_route_to_validation_gate=False`
  - `can_generate_prior_art_result=False`
- Skeleton 原样提交测试：
  - `formal_search_result_package_source_status=formal_search_result_package_failed_template_marker_preflight`
  - `template_marker_gap_count=365`
  - `preflight_blockers=['template_marker_preflight:template_or_todo_values_present']`
  - `can_route_to_validation_gate=False`
  - `can_generate_prior_art_result=False`

验证：

- `.venv/bin/python -m py_compile src/water_ai/agents/agent_architecture_consolidation_agent.py experiments/run_agent60_agent_architecture_consolidation.py`：通过。
- `.venv/bin/pytest tests/test_agent_architecture_consolidation_agent.py -q`：50 passed。
- `.venv/bin/python experiments/run_agent60_agent_architecture_consolidation.py`：通过，重新生成 Agent60 deliverable、metrics、manifest、submission skeleton 和 source preflight。
- 手动设置 `FORMAL_SEARCH_RESULT_PACKAGE_PATH=outputs/agent_architecture_consolidation/formal_search_result_package_submission_template.json` 运行 Agent60：preflight 正确返回 template marker 阻断；随后已恢复默认无提交包状态。
- `.venv/bin/pytest tests/test_pressure_resolution_replay_scenario_pack_agent.py tests/test_agent_architecture_consolidation_agent.py -q`：81 passed。
- `.venv/bin/pytest -q`：429 passed。

边界：

- Submission skeleton 是填报骨架，不是 evidence。
- 模板标记必须全部替换成真实外部/人工检索结果、reviewer 信息和 comparison 信息后，才可能进入 R8u-36 validation gate。
- 即使 template-marker preflight 未来通过，也只能进入 validation gate；不能直接生成 prior-art comparison、法律意见或 field-supported claim。

## 2026-06-04 R8u-37：Formal Search Result Package Template and Source Preflight

目标：

- 承接 R8u-36 的 formal search result validation gate，把“如何验收结果包”继续推进为“如何提交结果包，以及提交前先做 source/root shape 预检”。
- 每个 package template 必须写清 linked validation gate、linked intake、linked work package、package manifest 字段、prior_art_hit_table 字段、claim_element_comparison_chart 字段、fallback recommendation 字段、允许来源库、允许查询来源、行级拒收规则、验证命令和 failure boundary。
- 保持边界：该 template/preflight 不是正式检索结果，不是法律意见，不生成 prior-art comparison，不产生 field-supported claim。

实现：

- `src/water_ai/agents/agent_architecture_consolidation_agent.py`：
  - 新增 `REQUIRED_FORMAL_SEARCH_RESULT_PACKAGE_TEMPLATE_FIELDS`。
  - 新增 `formal_search_result_package_path` 可选输入，用于读取 `FORMAL_SEARCH_RESULT_PACKAGE_PATH` 指向的结果包。
  - 新增 `_formal_search_result_package_template()`、`_formal_search_result_package_template_coverage()` 和 `_formal_search_result_package_source_preflight()`。
  - Agent60 metrics 现在输出 `formal_search_result_package_template`、`formal_search_result_package_template_coverage` 和 `formal_search_result_package_source_preflight`。
- `experiments/run_agent60_agent_architecture_consolidation.py`：
  - 新增 `outputs/agent_architecture_consolidation/formal_search_result_package_template.json`。
  - 新增 `outputs/agent_architecture_consolidation/formal_search_result_package_source_preflight.json`。
  - 支持通过 `FORMAL_SEARCH_RESULT_PACKAGE_PATH` 指向外部/人工检索结果包。
  - Agent60 report、deliverable 和 manifest 已索引 template/preflight。
- `tests/test_agent_architecture_consolidation_agent.py`：
  - 新增测试确保 7 个 package template 覆盖全部 7 个 validation gate。
  - 测试确保每个 template 都包含 prior-art hit table、claim element comparison、fallback recommendation、review boundary、allowed databases、row-level rejection rules 和 boundary flags。
  - 测试确保默认未设置 `FORMAL_SEARCH_RESULT_PACKAGE_PATH` 时，source preflight 停在 `formal_search_result_package_preflight_waiting_for_submission_path`，不能进入 validation gate，不能生成 prior-art result。

当前输出：

- 新增文件：
  - `outputs/agent_architecture_consolidation/formal_search_result_package_template.json`
  - `outputs/agent_architecture_consolidation/formal_search_result_package_source_preflight.json`
- 当前状态：
  - `formal_search_result_package_template_status=formal_search_result_package_templates_ready_waiting_for_submission`
  - `package_template_count=7`
  - `complete_package_template_count=7`
  - `formal_search_result_package_template_coverage_rate=1.0`
  - `missing_validation_gate_coverage=[]`
  - `formal_search_result_package_source_status=formal_search_result_package_preflight_waiting_for_submission_path`
  - `expected_env_var=FORMAL_SEARCH_RESULT_PACKAGE_PATH`
  - `preflight_blockers=['FORMAL_SEARCH_RESULT_PACKAGE_PATH:not_set']`
  - `can_route_to_validation_gate=False`
  - `can_generate_prior_art_result=False`
  - `legal_opinion_allowed=False`
  - `field_claim_upgrade_allowed=False`

验证：

- `.venv/bin/python -m py_compile src/water_ai/agents/agent_architecture_consolidation_agent.py experiments/run_agent60_agent_architecture_consolidation.py`：通过。
- `.venv/bin/pytest tests/test_agent_architecture_consolidation_agent.py -q`：49 passed。
- `.venv/bin/python experiments/run_agent60_agent_architecture_consolidation.py`：通过，重新生成 Agent60 deliverable、metrics、manifest、formal search result validation gate、formal search result package template 和 source preflight。
- `jq` 验证 package template coverage 为 1.0，source preflight 等待 `FORMAL_SEARCH_RESULT_PACKAGE_PATH`，`can_route_to_validation_gate=false`，`can_generate_prior_art_result=false`。
- `.venv/bin/pytest tests/test_pressure_resolution_replay_scenario_pack_agent.py tests/test_agent_architecture_consolidation_agent.py -q`：80 passed。
- `.venv/bin/pytest -q`：428 passed。

边界：

- 该 template/preflight 只提供正式检索结果包的提交入口和 source/root shape 预检。
- 未提交真实外部/人工检索结果包时，不能进入 validation gate。
- 即使 source preflight 未来通过，也只能进入 R8u-36 validation gate；不能直接生成 prior-art comparison、法律意见或 field-supported claim。

## 2026-06-04 R8u-36：Formal Search Result Validation Gate

目标：

- 承接 R8u-35 的 formal search result intake schema，把“结果该怎么提交”进一步推进为“提交后如何运行时验收、阻断和退回补证”。
- 每个 validation gate 必须写清 linked intake、linked work package、allowed source databases、allowed query sources、hit table/comparison chart 必填字段、runtime validation steps、blocking conditions、patch plan outputs、prior-art result generation rule 和 failure boundary。
- 保持边界：该 gate 不是正式检索结果，不是法律意见，不证明新颖性/创造性，不产生 field-supported claim。

实现：

- `src/water_ai/agents/agent_architecture_consolidation_agent.py`：
  - 新增 `REQUIRED_FORMAL_SEARCH_RESULT_VALIDATION_GATE_FIELDS`。
  - 新增 `_formal_search_result_validation_gate()` 和 `_formal_search_result_validation_gate_coverage()`。
  - Agent60 metrics 现在输出 `formal_search_result_validation_gate` 与 `formal_search_result_validation_gate_coverage`。
  - Validation gate 覆盖 7 个 intake，每个 gate 都回连 formal search work package 的检索库和中英文检索式，并允许 `reviewer_approved_query_expansion_with_rationale` 作为带说明的扩展检索来源。
- `experiments/run_agent60_agent_architecture_consolidation.py`：
  - 新增 `outputs/agent_architecture_consolidation/formal_search_result_validation_gate.json`。
  - Agent60 report、deliverable 和 manifest 已索引该 gate。
  - manifest 新增 `latest_agent60_formal_search_result_validation_gate_status`、gate count、coverage rate、result package supplied、validated hit count、rejected hit count 和 can generate prior-art result 等字段。
- `tests/test_agent_architecture_consolidation_agent.py`：
  - 新增测试确保 7 个 validation gate 覆盖全部 7 个 intake。
  - 测试确保 gate 包含 required fields、source database/query provenance 阻断、reviewer 边界阻断和 patch plan outputs。
  - 测试确保 `formal_search_result_package_supplied=False`、`validated_hit_count=0`、`rejected_hit_count=0`、`can_generate_prior_art_result=False`、`legal_opinion_allowed=False`、`field_claim_upgrade_allowed=False`。

当前输出：

- 新增文件：
  - `outputs/agent_architecture_consolidation/formal_search_result_validation_gate.json`
- 当前状态：
  - `formal_search_result_validation_gate_status=formal_search_result_validation_gate_ready_waiting_for_external_result_package`
  - `validation_gate_count=7`
  - `complete_validation_gate_count=7`
  - `formal_search_result_validation_gate_coverage_rate=1.0`
  - `missing_intake_coverage=[]`
  - `formal_search_result_package_supplied=False`
  - `validated_hit_count=0`
  - `rejected_hit_count=0`
  - `can_generate_prior_art_result=False`
  - `legal_opinion_allowed=False`
  - `field_claim_upgrade_allowed=False`

验证：

- `.venv/bin/python -m py_compile src/water_ai/agents/agent_architecture_consolidation_agent.py experiments/run_agent60_agent_architecture_consolidation.py`：通过。
- `.venv/bin/pytest tests/test_agent_architecture_consolidation_agent.py -q`：48 passed。
- `.venv/bin/python experiments/run_agent60_agent_architecture_consolidation.py`：通过，重新生成 Agent60 deliverable、metrics、manifest、technical feature ledger、technical claim skeleton scaffold、technical embodiment validation matrix、technical effect measurement matrix、prior-art distinction matrix、formal search work packages、formal search result intake schema 和 formal search result validation gate。
- `jq` 验证 formal search result validation gate coverage 为 1.0、missing intake coverage 为空、`formal_search_result_package_supplied=false`、`validated_hit_count=0`、`can_generate_prior_art_result=false`。
- `.venv/bin/pytest tests/test_pressure_resolution_replay_scenario_pack_agent.py tests/test_agent_architecture_consolidation_agent.py -q`：79 passed。
- `.venv/bin/pytest -q`：427 passed。

边界：

- 该 gate 只验证正式检索结果包的结构、来源、比对覆盖和 reviewer 边界。
- 没有外部/人工正式检索结果包时，不能生成 prior-art comparison。
- 即使未来结果包通过 gate，也只能生成非法律的 prior-art comparison summary；新颖性/创造性、授权判断和 field-supported claim 仍必须保留外部法律审查与 field validation gate。

## 2026-06-04 R8u-35：Formal Search Result Intake Schema

目标：

- 承接 R8u-34 的 formal search work packages，把正式检索结果的提交、比对和阻断规则提前固化。
- 每个 intake schema 必须写清 linked work package、prior-art hit table 必填字段、claim element comparison chart 必填字段、reviewer 字段、input artifacts、acceptance checks、blocking conditions、minimum evidence to accept hit、claim scope decision options 和 failure boundary。
- 保持边界：该 schema 不是检索结果，不是法律意见，不产生 prior-art 结论，不产生 field-supported claim。

实现：

- `src/water_ai/agents/agent_architecture_consolidation_agent.py`：
  - 新增 `PRIOR_ART_HIT_TABLE_FIELDS`，共 18 个 hit table 必填字段。
  - 新增 `CLAIM_ELEMENT_COMPARISON_FIELDS`，共 12 个 comparison chart 必填字段。
  - 新增 `REQUIRED_FORMAL_SEARCH_RESULT_INTAKE_FIELDS`。
  - 新增 `_formal_search_result_intake_schema()` 和 `_formal_search_result_intake_coverage()`。
  - Agent60 metrics 现在输出 `formal_search_result_intake_schema` 与 `formal_search_result_intake_coverage`。
- `experiments/run_agent60_agent_architecture_consolidation.py`：
  - 新增 `outputs/agent_architecture_consolidation/formal_search_result_intake_schema.json`。
  - Agent60 report、deliverable 和 manifest 已索引该 schema。
  - manifest 新增 `latest_agent60_formal_search_result_intake_status`、intake count、coverage rate、result supplied、accepted hit count 和 can generate prior-art result 等字段。
- `tests/test_agent_architecture_consolidation_agent.py`：
  - 新增测试确保 7 个 intake 覆盖全部 7 个 formal search work packages。
  - 测试确保每个 intake 都包含 18 个 hit table 字段、12 个 comparison chart 字段、验收检查、阻断条件和 claim scope decision options。
  - 测试确保 `formal_search_result_supplied=False`、`accepted_hit_count=0`、`can_generate_prior_art_result=False`、`legal_opinion_allowed=False`、`field_claim_upgrade_allowed=False`。

当前输出：

- 新增文件：
  - `outputs/agent_architecture_consolidation/formal_search_result_intake_schema.json`
- 当前状态：
  - `formal_search_result_intake_status=formal_search_result_intake_schema_ready_waiting_for_external_results`
  - `intake_count=7`
  - `complete_intake_count=7`
  - `formal_search_result_intake_coverage_rate=1.0`
  - `missing_work_package_coverage=[]`
  - `formal_search_result_supplied=False`
  - `accepted_hit_count=0`
  - `can_generate_prior_art_result=False`
  - `legal_opinion_allowed=False`
  - `field_claim_upgrade_allowed=False`

验证：

- `.venv/bin/python -m py_compile src/water_ai/agents/agent_architecture_consolidation_agent.py experiments/run_agent60_agent_architecture_consolidation.py`：通过。
- `.venv/bin/pytest tests/test_agent_architecture_consolidation_agent.py -q`：47 passed。
- `.venv/bin/python experiments/run_agent60_agent_architecture_consolidation.py`：通过，重新生成 Agent60 deliverable、metrics、manifest、technical feature ledger、technical claim skeleton scaffold、technical embodiment validation matrix、technical effect measurement matrix、prior-art distinction matrix、formal search work packages 和 formal search result intake schema。
- `jq` 验证 formal search result intake coverage 为 1.0、missing work package coverage 为空、`formal_search_result_supplied=false`、`accepted_hit_count=0`、`can_generate_prior_art_result=false`。
- `.venv/bin/pytest tests/test_pressure_resolution_replay_scenario_pack_agent.py tests/test_agent_architecture_consolidation_agent.py -q`：78 passed。
- `.venv/bin/pytest -q`：426 passed。

边界：

- 该 schema 只定义正式检索结果的接收、字段和阻断规则。
- 没有外部正式检索结果与人工复核时，不能生成 prior-art hit 结论、法律意见或 field-supported claim。
- 下一步如果继续该路线，应接收真实 `prior_art_hit_table` 和 `claim_element_comparison_chart`，再通过该 schema 验收。

## 2026-06-04 R8u-34：Formal Search Work Packages and Claim Fallback Routes

目标：

- 承接 R8u-33 的 prior-art distinction / protectability risk matrix，把每条区别假设进一步转成正式检索工作包和 claim fallback 路线。
- 每个工作包必须写清 search objective、search databases、english/chinese search queries、classification hints、evidence to collect、negative evidence checks、claim fallback、field validation gate、decision rule 和 expected output artifacts。
- 保持边界：该矩阵只是正式检索任务清单，不是检索结果，不是法律意见，不证明新颖性/创造性，也不产生 field-supported claim。

实现：

- `src/water_ai/agents/agent_architecture_consolidation_agent.py`：
  - 新增 `REQUIRED_FORMAL_SEARCH_WORK_PACKAGE_FIELDS`。
  - 新增 `FORMAL_SEARCH_WORK_PACKAGE_BLUEPRINTS`，共 7 个正式检索工作包：
    - `FSWP1_cyclic_greybox_soft_sensor_release_gate_search`
    - `FSWP2_node_modality_sparse_hidden_state_search`
    - `FSWP3_greybox_multi_agent_safety_arbitration_search`
    - `FSWP4_low_cost_observation_gated_flowsheet_search`
    - `FSWP5_scientific_kg_action_constraint_claim_gate_search`
    - `FSWP6_operational_catalyst_activity_guardrail_search`
    - `FSWP7_pressure_resolution_protective_release_gate_search`
  - 新增 `_formal_search_work_package_matrix()` 和 `_formal_search_work_package_coverage()`。
  - Agent60 metrics 现在输出 `formal_search_work_package_matrix` 与 `formal_search_work_package_coverage`。
- `experiments/run_agent60_agent_architecture_consolidation.py`：
  - 新增 `outputs/agent_architecture_consolidation/formal_search_work_packages.json`。
  - Agent60 report、deliverable 和 manifest 已索引该矩阵。
  - manifest 新增 `latest_agent60_formal_search_work_package_status`、work package count、coverage rate、formal search completed、legal opinion allowed 和 field claim upgrade allowed 等字段。
- `tests/test_agent_architecture_consolidation_agent.py`：
  - 新增测试确保 7 个工作包覆盖全部 7 条 prior-art distinction。
  - 测试确保每个工作包均包含英文/中文检索式、检索库、claim fallback 和 field validation gate。
  - 测试确保 `formal_search_completed=False`、`legal_opinion_allowed=False`、`field_claim_upgrade_allowed=False`。

当前输出：

- 新增文件：
  - `outputs/agent_architecture_consolidation/formal_search_work_packages.json`
- 当前状态：
  - `formal_search_work_package_status=formal_search_work_packages_ready_not_search_results`
  - `work_package_count=7`
  - `complete_work_package_count=7`
  - `formal_search_work_package_coverage_rate=1.0`
  - `missing_distinction_coverage=[]`
  - `formal_search_required=True`
  - `formal_search_completed=False`
  - `legal_opinion_allowed=False`
  - `field_claim_upgrade_allowed=False`

验证：

- `.venv/bin/python -m py_compile src/water_ai/agents/agent_architecture_consolidation_agent.py experiments/run_agent60_agent_architecture_consolidation.py`：通过。
- `.venv/bin/pytest tests/test_agent_architecture_consolidation_agent.py -q`：46 passed。
- `.venv/bin/python experiments/run_agent60_agent_architecture_consolidation.py`：通过，重新生成 Agent60 deliverable、metrics、manifest、technical feature ledger、technical claim skeleton scaffold、technical embodiment validation matrix、technical effect measurement matrix、prior-art distinction matrix 和 formal search work packages。
- `jq` 验证 formal search work package coverage 为 1.0、missing distinction coverage 为空、`formal_search_completed=false`、`legal_opinion_allowed=false`、`field_claim_upgrade_allowed=false`。
- `.venv/bin/pytest tests/test_pressure_resolution_replay_scenario_pack_agent.py tests/test_agent_architecture_consolidation_agent.py -q`：77 passed。
- `.venv/bin/pytest -q`：425 passed。

边界：

- 该矩阵只提供检索任务和 claim fallback 路线，不替代 CNIPA/Google Patents/Espacenet/WIPO/Scholar 等正式检索。
- 不能据此声称专利新颖性、创造性、授权可能性或现场成立。
- 若后续继续专利级路线，下一步可以把检索结果导入为 `prior_art_hit_table` 和 `claim_element_comparison_chart`，再决定主 claim 是否保留或收窄。

## 2026-06-04 R8u-33：Prior-Art Distinction / Protectability Risk Matrix

目标：

- 承接 R8u-32 的 technical effect measurement matrix，把 claim skeleton、technical feature 和 technical effect 进一步映射到已有方法族，形成“现有技术区别假设/保护性风险矩阵”。
- 每个区别项必须写清 prior art family、representative sources、known prior capability、distinguishing combination、why not generic AI/control、technical problem、measurable effects、novelty risk、combination risk、dependent fallback path、verification needed 和 failure boundary。
- 保持边界：该矩阵不是正式 prior-art search，不是法律意见，不给出新颖性/创造性/授权判断；所有项均要求 formal search 和 field validation。

实现：

- `src/water_ai/agents/agent_architecture_consolidation_agent.py`：
  - 新增 `REQUIRED_PRIOR_ART_DISTINCTION_FIELDS`。
  - 新增 `PRIOR_ART_DISTINCTION_BLUEPRINTS`，共 7 个区别/风险项：
    - `PAD1_soft_sensor_ml_vs_cyclic_greybox_release_gated_control`
    - `PAD2_sparse_sensor_placement_vs_node_modality_hidden_state_layout`
    - `PAD3_marl_pump_coordination_vs_greybox_multi_agent_safety_arbitration`
    - `PAD4_flowsheet_optimization_vs_low_cost_observation_gated_greybox_control`
    - `PAD5_scientific_kg_vs_action_constraint_and_claim_gate`
    - `PAD6_ai_catalyst_discovery_vs_operational_catalyst_activity_guardrail`
    - `PAD7_replay_validation_vs_pressure_resolution_protective_release_gate`
  - 新增 `_prior_art_distinction_matrix()` 和 `_prior_art_distinction_coverage()`。
  - Agent60 metrics 现在输出 `prior_art_distinction_matrix` 与 `prior_art_distinction_coverage`。
- `experiments/run_agent60_agent_architecture_consolidation.py`：
  - 新增 `outputs/agent_architecture_consolidation/prior_art_distinction_matrix.json`。
  - Agent60 report、deliverable 和 manifest 已索引该矩阵。
  - manifest 新增 `latest_agent60_prior_art_distinction_status`、distinction count、coverage rate、formal search required、novelty/inventiveness opinion allowed 和 field claim upgrade allowed 等字段。
- `tests/test_agent_architecture_consolidation_agent.py`：
  - 新增测试确保 7 个区别项覆盖全部 7 条 claim scaffold、8 条 PTF feature 和 7 条 technical effect。
  - 测试确保稀疏布点区别项不是只复述 PySensors，而是落到 node-modality 和 catalyst_activity fallback。
  - 测试确保多智能体区别项不是泛化黑箱 MARL，而是灰箱安全仲裁。
  - 测试确保催化剂区别项不是 AI 材料发现本身，而是运行态催化剂活性代理和 Agent51 field proxy holdout。

当前输出：

- 新增文件：
  - `outputs/agent_architecture_consolidation/prior_art_distinction_matrix.json`
- 当前状态：
  - `prior_art_distinction_status=prior_art_distinction_matrix_ready_as_hypothesis_not_search_or_legal_opinion`
  - `distinction_count=7`
  - `complete_distinction_count=7`
  - `prior_art_distinction_coverage_rate=1.0`
  - `missing_claim_coverage=[]`
  - `missing_feature_coverage=[]`
  - `missing_effect_coverage=[]`
  - `formal_search_required=True`
  - `field_claim_upgrade_allowed=False`
  - `novelty_or_inventiveness_opinion_allowed=False`

验证：

- `.venv/bin/python -m py_compile src/water_ai/agents/agent_architecture_consolidation_agent.py experiments/run_agent60_agent_architecture_consolidation.py`：通过。
- `.venv/bin/pytest tests/test_agent_architecture_consolidation_agent.py -q`：45 passed。
- `.venv/bin/python experiments/run_agent60_agent_architecture_consolidation.py`：通过，重新生成 Agent60 deliverable、metrics、manifest、technical feature ledger、technical claim skeleton scaffold、technical embodiment validation matrix、technical effect measurement matrix 和 prior-art distinction matrix。
- `jq` 验证 prior-art distinction coverage 为 1.0、missing claim/feature/effect coverage 为空、`formal_search_required=true`、`novelty_or_inventiveness_opinion_allowed=false`、`field_claim_upgrade_allowed=false`。
- `.venv/bin/pytest tests/test_pressure_resolution_replay_scenario_pack_agent.py tests/test_agent_architecture_consolidation_agent.py -q`：76 passed。
- `.venv/bin/pytest -q`：424 passed。

边界：

- 该矩阵只定义正式检索前的区别假设和保护性风险，不是专利检索报告。
- 不能据此声称新颖性、创造性、授权可能性或现场成立。
- 下一步若继续专利级成熟度路线，应优先把 prior-art distinction 与正式检索清单、可检索关键词、claim fallback 和 field validation gate 进一步连接。

## 2026-06-04 R8u-32：Technical Effect Measurement Matrix

目标：

- 承接 R8u-31 的 technical embodiment validation matrix，把实施例中的“技术效果待测量项”继续压成可验收的效果度量矩阵。
- 每个技术效果必须写清 linked embodiment/claim/feature、effect statement、baseline comparator、measurement metrics、acceptance thresholds、required evidence tiers、validation gate、current evidence status 和 failure boundary。
- 保持边界：技术效果度量矩阵只是验收合同，不产生 field evidence，不写 actuator，不写 release gate，不把 synthetic/template/sample 结果写成现场成立结论。

实现：

- `src/water_ai/agents/agent_architecture_consolidation_agent.py`：
  - 新增 `REQUIRED_TECHNICAL_EFFECT_MEASUREMENT_FIELDS`。
  - 新增 `TECHNICAL_EFFECT_MEASUREMENT_BLUEPRINTS`，共 7 个技术效果：
    - `TEM1_observability_gain_under_sparse_sensing`
    - `TEM2_blackbox_to_greybox_state_estimation`
    - `TEM3_low_frequency_cycle_window_reduces_fast_sensor_need`
    - `TEM4_catalyst_proxy_guardrail_effect`
    - `TEM5_field_replay_protective_writeback_reduces_false_release`
    - `TEM6_greybox_multi_agent_arbitration_reduces_conflict_actions`
    - `TEM7_engineering_execution_constraint_feasibility`
  - 新增 `_technical_effect_measurement_matrix()` 和 `_technical_effect_measurement_coverage()`。
  - Agent60 metrics 现在输出 `technical_effect_measurement_matrix` 与 `technical_effect_measurement_coverage`。
- `experiments/run_agent60_agent_architecture_consolidation.py`：
  - 新增 `outputs/agent_architecture_consolidation/technical_effect_measurement_matrix.json`。
  - Agent60 report、deliverable 和 manifest 已索引该矩阵。
  - manifest 新增 `latest_agent60_technical_effect_measurement_status`、effect count、coverage rate、field claim upgrade allowed、can write actuator、can write release gate 等字段。
- `tests/test_agent_architecture_consolidation_agent.py`：
  - 新增测试确保 7 个技术效果覆盖 6 个实施例。
  - 测试确保低频循环窗口效果包含 `latency_violation_rate`、timestamped field replay 与 actuator feedback gate。
  - 测试确保催化剂活性代理效果包含 `holdout_mae`、`Agent51 field proxy holdout` 且不能写执行器。
  - 测试确保 field replay/release gate 防误放行效果保持 `can_write_to_release_gate=False`。

当前输出：

- 新增文件：
  - `outputs/agent_architecture_consolidation/technical_effect_measurement_matrix.json`
- 当前状态：
  - `technical_effect_measurement_status=technical_effect_measurement_matrix_ready_not_field_evidence`
  - `effect_count=7`
  - `complete_effect_count=7`
  - `technical_effect_measurement_coverage_rate=1.0`
  - `missing_embodiment_coverage=[]`
  - `field_claim_upgrade_allowed=False`
  - `can_generate_field_evidence=False`
  - `can_write_to_actuator=False`
  - `can_write_to_release_gate=False`

验证：

- `.venv/bin/python -m py_compile src/water_ai/agents/agent_architecture_consolidation_agent.py experiments/run_agent60_agent_architecture_consolidation.py`：通过。
- `.venv/bin/pytest tests/test_agent_architecture_consolidation_agent.py -q`：44 passed。
- `.venv/bin/python experiments/run_agent60_agent_architecture_consolidation.py`：通过，重新生成 Agent60 deliverable、metrics、manifest、technical feature ledger、technical claim skeleton scaffold、technical embodiment validation matrix 和 technical effect measurement matrix。
- `jq` 验证 effect matrix coverage 为 1.0、missing embodiment coverage 为空、`can_generate_field_evidence=false`、`can_write_to_actuator=false`、`can_write_to_release_gate=false`。
- `.venv/bin/pytest tests/test_pressure_resolution_replay_scenario_pack_agent.py tests/test_agent_architecture_consolidation_agent.py -q`：75 passed。
- `.venv/bin/pytest -q`：423 passed。

边界：

- 该矩阵只定义技术效果的基线、指标、阈值和验证门，不产生现场证据。
- 没有真实 field package、replay、holdout、operator review 和 release gate 时，不能生成 field-supported claim、不能写执行器、不能写 release gate。

## 2026-06-04 R8u-31：Technical Embodiment Validation Matrix

目标：

- 承接 R8u-30 的 technical claim skeleton scaffold，把主方法/系统和从属方向进一步落成可验收实施例矩阵。
- 每个实施例必须写清 scenario、source package requirements、required tables/artifacts、step sequence、validation gates、acceptance metrics、technical effect to measure、current evidence status 和 failure boundary。
- 保持边界：实施例矩阵只是验证设计 scaffold，不产生 field evidence，不写 actuator，不写 release gate。

实现：

- `src/water_ai/agents/agent_architecture_consolidation_agent.py`：
  - 新增 `REQUIRED_TECHNICAL_EMBODIMENT_FIELDS`。
  - 新增 `TECHNICAL_EMBODIMENT_BLUEPRINTS`，共 6 个实施例：
    - `TE1_end_to_end_low_cost_cyclic_greybox_control`
    - `TE2_pressure_resolution_route_package_validation`
    - `TE3_catalyst_activity_proxy_regeneration`
    - `TE4_node_modality_sparse_hidden_state_layout`
    - `TE5_low_frequency_cycle_window_control`
    - `TE6_greybox_multi_agent_safety_arbitration`
  - 新增 `_technical_embodiment_validation_matrix()` 和 `_technical_embodiment_validation_coverage()`。
  - Agent60 metrics 现在输出 `technical_embodiment_validation_matrix` 与 `technical_embodiment_validation_coverage`。
- `experiments/run_agent60_agent_architecture_consolidation.py`：
  - 新增 `outputs/agent_architecture_consolidation/technical_embodiment_validation_matrix.json`。
  - Agent60 report、deliverable 和 manifest 已索引该矩阵。
  - manifest 新增 `latest_agent60_technical_embodiment_validation_status`、embodiment count、coverage rate、field claim upgrade allowed、can generate field evidence 等字段。
- `tests/test_agent_architecture_consolidation_agent.py`：
  - 新增测试确保 6 个实施例覆盖全部 7 条 claim scaffold 和 8 条 PTF feature。
  - 测试确保 `TE2_pressure_resolution_route_package_validation` 明确阻断在 `R7_TO_R8P_WORK_PACKAGE_DIR`。
  - 测试确保所有实施例均不能生成 field evidence、不能写 actuator、不能写 release gate。

当前输出：

- 新增文件：
  - `outputs/agent_architecture_consolidation/technical_embodiment_validation_matrix.json`
- 当前状态：
  - `technical_embodiment_validation_status=technical_embodiment_matrix_ready_not_field_evidence`
  - `embodiment_count=6`
  - `complete_embodiment_count=6`
  - `technical_embodiment_validation_coverage_rate=1.0`
  - `missing_claim_coverage=[]`
  - `missing_feature_coverage=[]`
  - `field_claim_upgrade_allowed=False`
  - `can_generate_field_evidence=False`
  - `can_write_to_actuator=False`
  - `can_write_to_release_gate=False`

验证：

- `.venv/bin/python -m py_compile src/water_ai/agents/agent_architecture_consolidation_agent.py experiments/run_agent60_agent_architecture_consolidation.py tests/test_agent_architecture_consolidation_agent.py`：通过。
- `.venv/bin/pytest tests/test_agent_architecture_consolidation_agent.py -q`：43 passed。
- `.venv/bin/python experiments/run_agent60_agent_architecture_consolidation.py`：通过，重新生成 Agent60 deliverable、metrics、manifest、technical feature ledger、technical claim skeleton scaffold 和 technical embodiment validation matrix。
- `jq` 验证 embodiment matrix coverage 为 1.0、missing claim/feature coverage 为空、`can_generate_field_evidence=false`、`can_write_to_actuator=false`、`can_write_to_release_gate=false`。
- `.venv/bin/pytest tests/test_pressure_resolution_replay_scenario_pack_agent.py tests/test_agent_architecture_consolidation_agent.py -q`：74 passed。
- `.venv/bin/pytest -q`：422 passed。

边界：

- 该矩阵只定义实施例与验证门，不产生现场证据。
- 没有真实 field package、replay、holdout 和 operator review 时，不能生成 field evidence、不能写执行器、不能写 release gate。

## 2026-06-04 R8u-30：Technical Claim Skeleton Scaffold

目标：

- 承接 R8u-29 的 patent-grade technical feature ledger，把八条技术特征进一步组合成“主方法/系统 + 从属或分案方向”的技术方案骨架。
- 回应全局 goal 中“潜在主专利方向”和“潜在从属或分案方向”的要求，但保持边界：这不是法律权利要求文本，不是授权判断，不产生 field evidence。
- 不新增 agent，继续复用 Agent60 架构治理层，符合“先复用、少堆叠”的原则。

实现：

- `src/water_ai/agents/agent_architecture_consolidation_agent.py`：
  - 新增 `REQUIRED_TECHNICAL_CLAIM_SCAFFOLD_FIELDS`。
  - 新增 `TECHNICAL_CLAIM_SCAFFOLD_BLUEPRINTS`，共 7 条：
    - `TCS1_independent_method_low_cost_sparse_cyclic_greybox_control`
    - `TCS2_independent_system_architecture`
    - `TCS3_dependent_catalyst_activity_regeneration_control`
    - `TCS4_dependent_node_modality_sparse_hidden_state_estimation`
    - `TCS5_dependent_field_replay_protective_writeback`
    - `TCS6_dependent_low_frequency_cycle_window_control`
    - `TCS7_dependent_greybox_multi_agent_safety_arbitration`
  - 新增 `_technical_claim_skeleton_scaffold()`、`_abstract_only_claim_risk()` 和 `_technical_claim_skeleton_coverage()`。
  - Agent60 metrics 现在输出 `technical_claim_skeleton_scaffold` 与 `technical_claim_skeleton_coverage`。
- `experiments/run_agent60_agent_architecture_consolidation.py`：
  - 新增 `outputs/agent_architecture_consolidation/technical_claim_skeleton_scaffold.json`。
  - Agent60 report、deliverable 和 manifest 已索引该 scaffold。
  - manifest 新增 `latest_agent60_technical_claim_skeleton_status`、scaffold count、coverage rate 和 `latest_agent60_technical_claim_field_upgrade_allowed`。
- `tests/test_agent_architecture_consolidation_agent.py`：
  - 新增测试确保 scaffold 覆盖 2 个独立方向与 5 个从属/分案方向。
  - 测试确保每条 scaffold 均回连已存在的 PTF feature、没有抽象口号风险、没有 missing feature，并明确 `claim_upgrade_allowed=False`。

当前输出：

- 新增文件：
  - `outputs/agent_architecture_consolidation/technical_claim_skeleton_scaffold.json`
- 当前状态：
  - `technical_claim_skeleton_status=technical_claim_skeleton_ready_as_scaffold_not_legal_claim_not_field_claim`
  - `claim_scaffold_count=7`
  - `complete_claim_scaffold_count=7`
  - `independent_claim_scaffold_ids=2`
  - `dependent_or_divisional_scaffold_ids=5`
  - `technical_claim_skeleton_coverage_rate=1.0`
  - `missing_feature_coverage=[]`
  - `field_claim_upgrade_allowed=False`

验证：

- `.venv/bin/python -m py_compile src/water_ai/agents/agent_architecture_consolidation_agent.py experiments/run_agent60_agent_architecture_consolidation.py tests/test_agent_architecture_consolidation_agent.py`：通过。
- `.venv/bin/pytest tests/test_agent_architecture_consolidation_agent.py -q`：42 passed。
- `.venv/bin/python experiments/run_agent60_agent_architecture_consolidation.py`：通过，重新生成 Agent60 deliverable、metrics、manifest、technical feature ledger 和 technical claim skeleton scaffold。
- `jq` 验证 claim skeleton coverage 为 1.0、2 个独立方向、5 个从属/分案方向、missing feature coverage 为空、`field_claim_upgrade_allowed=false`。
- `.venv/bin/pytest tests/test_pressure_resolution_replay_scenario_pack_agent.py tests/test_agent_architecture_consolidation_agent.py -q`：73 passed。
- `.venv/bin/pytest -q`：421 passed。

边界：

- 该 scaffold 是技术方案组织骨架，不是法律意见，不保证授权。
- 该 scaffold 不产生 field evidence，不写 actuator 或 release gate。
- 任何现场成立 claim 或执行器写回仍必须通过 R7/R8p/R8v、field holdout、operator review 和 release gate。

## 2026-06-04 R8u-29：Patent-Grade Technical Feature Ledger

目标：

- 承接全局 goal 的“以可保护技术方案反推系统清晰度”，把 Agent60 七层骨架和模块接口契约进一步压成机器可读技术特征 ledger。
- 避免把“AI、多智能体、知识图谱、闭环控制”当成创新点本身；每条特征必须落到技术问题、技术手段、系统结构、状态变量、控制动作、实施例、验证指标、技术效果、现有技术区别、claim skeleton role、证据边界和失败边界。
- 不新增 agent；直接复用 Agent60 架构治理层，符合“agent 不是越多越好”的约束。

实现：

- `src/water_ai/agents/agent_architecture_consolidation_agent.py`：
  - 新增 `REQUIRED_PATENT_TECHNICAL_FEATURE_FIELDS`。
  - 新增 8 条 `PATENT_TECHNICAL_FEATURE_BLUEPRINTS`，覆盖 M1-M8：
    - `PTF1_node_modality_sparse_sensing`
    - `PTF2_soft_sensor_grey_state_estimation`
    - `PTF3_grey_box_mechanism_boundary`
    - `PTF4_cyclic_low_frequency_control`
    - `PTF5_mechanism_kg_evidence_constraint`
    - `PTF6_field_replay_release_gate`
    - `PTF7_engineering_execution_constraints`
    - `PTF8_stage_gated_model_governance`
  - 新增 `_patent_technical_feature_ledger()`、`_abstract_only_feature_risk()` 和 `_patent_technical_feature_coverage()`。
  - Agent60 metrics 现在输出 `patent_technical_feature_ledger` 与 `patent_technical_feature_coverage`。
- `experiments/run_agent60_agent_architecture_consolidation.py`：
  - 新增 `outputs/agent_architecture_consolidation/patent_technical_feature_ledger.json`。
  - Agent60 report、deliverable 和 manifest 现在索引该 ledger。
  - manifest 新增 `latest_agent60_patent_technical_feature_status`、feature count、coverage rate 和 `latest_agent60_patent_field_claim_upgrade_allowed`。
- `tests/test_agent_architecture_consolidation_agent.py`：
  - 新增测试确保 ledger 完整、排除 M9 展示层、没有抽象口号风险，并明确 `field_claim_upgrade_allowed=False`。

当前输出：

- 新增文件：
  - `outputs/agent_architecture_consolidation/patent_technical_feature_ledger.json`
- 当前状态：
  - `patent_technical_feature_status=technical_feature_ledger_ready_as_disclosure_scaffold_not_field_claim`
  - `feature_count=8`
  - `complete_feature_count=8`
  - `technical_feature_coverage_rate=1.0`
  - `abstract_only_feature_ids=[]`
  - `field_claim_upgrade_allowed=False`
  - `excluded_modules=[M9_presentation_delivery]`

验证：

- `.venv/bin/python -m py_compile src/water_ai/agents/agent_architecture_consolidation_agent.py experiments/run_agent60_agent_architecture_consolidation.py tests/test_agent_architecture_consolidation_agent.py`：通过。
- `.venv/bin/pytest tests/test_agent_architecture_consolidation_agent.py -q`：41 passed。
- `.venv/bin/python experiments/run_agent60_agent_architecture_consolidation.py`：通过，重新生成 Agent60 deliverable、metrics、manifest 和 technical feature ledger。
- `jq` 验证 ledger coverage 为 1.0、abstract-only feature 为空、`field_claim_upgrade_allowed=false`。
- `.venv/bin/pytest tests/test_pressure_resolution_replay_scenario_pack_agent.py tests/test_agent_architecture_consolidation_agent.py -q`：72 passed。
- `.venv/bin/pytest -q`：420 passed。

边界：

- 该 ledger 是技术方案骨架/交底成熟度 scaffold，不是法律意见，不保证授权。
- 该 ledger 不产生 field evidence，不写 actuator 或 release gate。
- 任何现场成立 claim 仍必须通过 R7/R8p/R8v、field holdout、operator review 和 release gate。

## 2026-06-04 R8u-28b：Agent60 Manifest Status Stabilization

目标：

- 修复 Agent60 复跑时 `deliverables/manifest.json` 顶层 `status` 会退回旧 R7 coverage 口径的问题。
- 让 R8u-27 route work package patch plan 与 R8u-28 route work package assembly gate 不只出现在 `next_stage`，也成为可复跑、可审计的顶层治理状态。

实现：

- `experiments/run_agent60_agent_architecture_consolidation.py`：
  - 在 manifest 写回末端新增 `status_parts` 汇总。
  - 顶层 `status` 现在稳定包含：
    - R7 coverage/minimum replay contract 已接入。
    - R8u-27 route work package patch plan 状态。
    - R8u-28 route work package assembly gate 状态与 blocked assembly step 数。
    - 下一步仍指向最高证据价值动作 `R7a_import_real_field_package_with_metadata_and_csv`。

验证：

- `.venv/bin/python -m py_compile experiments/run_agent60_agent_architecture_consolidation.py`：通过。
- `.venv/bin/python experiments/run_agent60_agent_architecture_consolidation.py`：通过，重新生成 Agent60 deliverable、metrics 与 manifest。
- `jq` 验证 `deliverables/manifest.json` 顶层 `status` 已包含 R8u-27 patch plan 与 R8u-28 assembly gate；assembly gate 仍为 `route_work_package_assembly_gate_blocked_waiting_for_submission_dir`，`assembly_step_count=6`，`blocked_assembly_step_count=6`。
- `.venv/bin/pytest tests/test_pressure_resolution_replay_scenario_pack_agent.py tests/test_agent_architecture_consolidation_agent.py -q`：71 passed。
- `.venv/bin/pytest -q`：419 passed。

边界：

- 本轮不新增证据、不生成真实行、不写 actuator 或 release gate。
- 该修正只让治理状态更稳定，避免后续复跑覆盖核心模型进展。

## 2026-06-04 R8u-28：Route Work Package Assembly Gate

目标：

- 承接 R8u-27，让 work package patch plan 不只说明“先修哪个提交缺口”，还进一步定义四类 route work package 如何汇成 R8p candidate rows package。
- 固化装配顺序：R7 source package -> operator supplement -> Agent52 replay export -> R8p rows materialization -> R8p/R8v validation gates。
- 保持边界：assembly gate 只定义候选行包装配合同，不生成 field evidence，不写 actuator、release gate 或现场成立 claim。

实现：

- `experiments/run_agent61_pressure_resolution_replay_scenario_pack.py`：
  - 新增 `ROWS_R7_COMPLETION_ROUTE_WORK_PACKAGE_ASSEMBLY_GATE_PATH`。
  - 新增 `_field_rows_r7_completion_route_work_package_assembly_gate()`。
  - 新增 `_r7_completion_route_work_package_assembly_steps()`，定义 6 个装配步骤：
    - `R8U28_VALIDATE_WORK_PACKAGE_SUBMISSION`
    - `R8U28_STAGE_R7_SOURCE_PACKAGE_ROWS`
    - `R8U28_MERGE_OPERATOR_SUPPLEMENT_ROWS`
    - `R8U28_MERGE_AGENT52_REPLAY_EXPORT`
    - `R8U28_MATERIALIZE_R8P_ROWS_PACKAGE`
    - `R8U28_RERUN_R8P_AND_R8V_VALIDATION_GATES`
  - assembly gate 已写入 metrics、Agent61 report JSON、generated files、deliverable 和 manifest。
- `src/water_ai/agents/agent_architecture_consolidation_agent.py`：
  - 新增 `_r8p_pressure_resolution_r7_completion_route_work_package_assembly_gate()`。
  - Agent60 offline fallback 现在消费 assembly gate 状态、assembly step count、ready step count 和 blocked step count。
- `experiments/run_agent60_agent_architecture_consolidation.py`：
  - Agent60 report、deliverable、manifest 和 `next_stage` 已写回 route work package assembly gate 状态。
- 测试：
  - Agent61 测试验证未设置 `R7_TO_R8P_WORK_PACKAGE_DIR` 时 assembly gate 阻断在 `route_work_package_assembly_gate_blocked_waiting_for_submission_dir`。
  - Agent61 测试验证模板目录原样提交时 assembly gate 阻断在 `route_work_package_assembly_gate_blocked_by_work_package_repairs`。
  - Agent60 测试验证 fallback 消费并透传 assembly gate 状态与 step counts。

当前输出：

- 新增文件：
  - `outputs/pressure_resolution_replay_scenario_pack/pressure_resolution_replay_rows_r7_completion_route_work_package_assembly_gate.json`
- 当前默认未设置 `R7_TO_R8P_WORK_PACKAGE_DIR` 时：
  - `route_work_package_assembly_gate_status=route_work_package_assembly_gate_blocked_waiting_for_submission_dir`
  - `assembly_step_count=6`
  - `ready_assembly_step_count=0`
  - `blocked_assembly_step_count=6`
  - `can_materialize_candidate_rows_package=False`
  - `can_generate_field_evidence_from_assembly_gate=False`
  - `can_write_to_actuator=False`
  - `can_write_to_release_gate=False`
- Agent60 offline fallback 已新增：
  - `r7_work_package_assembly_gate_status=route_work_package_assembly_gate_blocked_waiting_for_submission_dir`
  - `r7_work_package_assembly_step_count=6`
  - `r7_work_package_ready_assembly_step_count=0`
  - `r7_work_package_blocked_assembly_step_count=6`

验证：

- `.venv/bin/python -m py_compile experiments/run_agent61_pressure_resolution_replay_scenario_pack.py experiments/run_agent60_agent_architecture_consolidation.py src/water_ai/agents/agent_architecture_consolidation_agent.py tests/test_pressure_resolution_replay_scenario_pack_agent.py tests/test_agent_architecture_consolidation_agent.py`：通过。
- `.venv/bin/pytest tests/test_pressure_resolution_replay_scenario_pack_agent.py::test_pressure_resolution_r7_work_package_templates_are_not_evidence_and_preflight_blocks_them tests/test_agent_architecture_consolidation_agent.py::test_architecture_consolidation_advances_fallback_after_pressure_resolution_scenario_pack_ready -q`：2 passed。
- `.venv/bin/pytest tests/test_pressure_resolution_replay_scenario_pack_agent.py tests/test_agent_architecture_consolidation_agent.py -q`：71 passed。
- `.venv/bin/pytest -q`：419 passed。

边界：

- assembly gate 不是导入器，也不是自动造数器；它只定义当 work package preflight 候选通过后，如何装配候选 R8p rows package 并重跑 gates。
- 当前没有真实 `R7_TO_R8P_WORK_PACKAGE_DIR`，所以不能 materialize candidate rows package。
- 即使未来 candidate rows package 被 materialize，也仍需 R8p schema/provenance/template/bundle/temporal/semantic gates、R8v routing、field holdout、Agent51/49/52/R7 evidence chain 和人工复核。

## 2026-06-04 R8u-27：Route Work Package Preflight Patch Plan

目标：

- 承接 R8u-26，让 work package submission preflight 不只停留在“阻断/等待”状态，而是把每个阻断点转成可执行、可验收、可由 Agent60 消费的修补计划。
- 保持主链：R7 source package、operator supplement、Agent52 replay export 与 R8p validation gates 仍是证据路线；patch plan 只指导修补这些路线的提交包。
- 保持边界：patch plan 不是 field evidence，不生成真实现场结论，不写 actuator、release gate 或 field-supported claim。

实现：

- `experiments/run_agent61_pressure_resolution_replay_scenario_pack.py`：
  - 新增 `ROWS_R7_COMPLETION_ROUTE_WORK_PACKAGE_PATCH_PLAN_PATH`。
  - 新增 `_field_rows_r7_completion_route_work_package_patch_plan()`。
  - 新增 package/file 级 patch item 拆解：missing work package dir、project dependency gate、missing submission file、CSV header contract、empty CSV rows、invalid JSON、template marker replacement 和 metadata provenance。
  - patch plan 已写入 metrics、Agent61 report JSON、generated files、deliverable 和 manifest。
- `src/water_ai/agents/agent_architecture_consolidation_agent.py`：
  - 新增 `_r8p_pressure_resolution_r7_completion_route_work_package_patch_plan()`。
  - Agent60 offline fallback 现在消费 work package patch plan 状态、patch item 数、highest patch 和 patch plan path。
- `experiments/run_agent60_agent_architecture_consolidation.py`：
  - Agent60 report、deliverable、manifest 和 `next_stage` 已写回 route work package patch plan 状态。
- 测试：
  - Agent61 测试验证未设置 `R7_TO_R8P_WORK_PACKAGE_DIR` 时生成 `R8U27_SET_R7_TO_R8P_WORK_PACKAGE_DIR`，且不能生成 field evidence。
  - Agent61 测试验证模板目录原样提交会生成 empty CSV、template marker、metadata provenance 和 project dependency patch items。
  - Agent60 测试验证 fallback 消费并透传 R8u-27 patch plan 状态、patch item 数和 highest patch。

当前输出：

- 新增文件：
  - `outputs/pressure_resolution_replay_scenario_pack/pressure_resolution_replay_rows_r7_completion_route_work_package_patch_plan.json`
- 当前默认未设置 `R7_TO_R8P_WORK_PACKAGE_DIR` 时：
  - `route_work_package_patch_plan_status=route_work_package_patch_plan_waiting_for_submission_dir`
  - `patch_item_count=1`
  - `highest_priority_patch_id=R8U27_SET_R7_TO_R8P_WORK_PACKAGE_DIR`
  - `can_generate_field_evidence_from_patch_plan=False`
  - `can_write_to_actuator=False`
  - `can_write_to_release_gate=False`
- Agent60 offline fallback 已新增：
  - `r7_work_package_patch_plan_status=route_work_package_patch_plan_waiting_for_submission_dir`
  - `r7_work_package_patch_item_count=1`
  - `r7_work_package_highest_priority_patch_id=R8U27_SET_R7_TO_R8P_WORK_PACKAGE_DIR`

验证：

- `.venv/bin/python -m py_compile experiments/run_agent61_pressure_resolution_replay_scenario_pack.py experiments/run_agent60_agent_architecture_consolidation.py src/water_ai/agents/agent_architecture_consolidation_agent.py tests/test_pressure_resolution_replay_scenario_pack_agent.py tests/test_agent_architecture_consolidation_agent.py`：通过。
- `.venv/bin/pytest tests/test_pressure_resolution_replay_scenario_pack_agent.py::test_pressure_resolution_r7_work_package_templates_are_not_evidence_and_preflight_blocks_them tests/test_agent_architecture_consolidation_agent.py::test_architecture_consolidation_advances_fallback_after_pressure_resolution_scenario_pack_ready -q`：2 passed。
- `.venv/bin/pytest tests/test_pressure_resolution_replay_scenario_pack_agent.py tests/test_agent_architecture_consolidation_agent.py -q`：71 passed。
- `.venv/bin/pytest -q`：419 passed。

边界：

- patch plan 只把 preflight blockers 转成 operator repair tasks，不能替代真实 R7 import、R8p schema/provenance/semantic gates、R8v routing、field holdout 或人工复核。
- 默认输出仍是“等待提交目录”，说明没有真实 `R7_TO_R8P_WORK_PACKAGE_DIR`；不能据此声称现场 replay 或控制链已成立。
- 本轮没有新增 agent，没有改变 Agent48/49/52 控制逻辑；只是把真实包接入链路的工程阻塞压实为可执行修补接口。

## 2026-06-04 R8u-26：Route Work Package Submission Templates And Preflight

目标：

- 承接 R8u-25，让 route work packages 不只停留在“应提交什么”的合同层，而是进一步形成可填报模板目录和机器可读 submission preflight。
- 生成四个 work package 的提交模板：R7 source package、operator supplement、Agent52 replay export、R8p validation gates。
- 增加 `R7_TO_R8P_WORK_PACKAGE_DIR` 提交目录预检：未提交时等待，提交模板原样时因 header-only/TODO/provenance gap 被阻断。
- 保持边界：模板与 preflight 只提供提交入口和候选完整性检查，不生成 field evidence，不写 actuator、release gate 或现场成立 claim。

实现：

- `experiments/run_agent61_pressure_resolution_replay_scenario_pack.py`：
  - 新增 `ROWS_R7_COMPLETION_ROUTE_WORK_PACKAGE_TEMPLATE_DIR`。
  - 新增 `ROWS_R7_COMPLETION_ROUTE_WORK_PACKAGE_PREFLIGHT_PATH`。
  - 新增 `_write_r7_completion_route_work_package_templates()`，按 work package 写入子目录、`submission_manifest.json`、CSV header 和 JSON placeholder。
  - 新增 `_field_rows_r7_completion_route_work_package_submission_preflight()`，读取可选 `R7_TO_R8P_WORK_PACKAGE_DIR` 并检查 package 目录、期望文件、CSV header、空 CSV、JSON 解析、TODO/template marker 和 metadata provenance。
  - preflight 输出已写入 metrics、Agent61 report JSON、generated files、deliverable 和 manifest。
- `src/water_ai/agents/agent_architecture_consolidation_agent.py`：
  - 新增 `_r8p_pressure_resolution_r7_completion_route_work_package_templates()`。
  - 新增 `_r8p_pressure_resolution_r7_completion_route_work_package_preflight()`。
  - Agent60 offline fallback 现在消费模板状态、preflight 状态、submitted/passed/blocked package counts 和 preflight path。
- `experiments/run_agent60_agent_architecture_consolidation.py`：
  - Agent60 report、deliverable、manifest 和 `next_stage` 已写回 route work package preflight 状态。
- 测试：
  - 新增测试验证模板生成后仍 `can_generate_field_evidence_from_templates=False`。
  - 新增测试验证未设置提交目录时 preflight 等待提交。
  - 新增测试验证模板目录原样提交会被 `header-only/TODO/provenance` 阻断，不能产生候选通过。
  - Agent60 测试验证 fallback 消费并透传 R8u-26 preflight 状态与 package counts。

当前输出：

- 新增目录：
  - `outputs/pressure_resolution_replay_scenario_pack/pressure_resolution_replay_rows_r7_completion_route_work_package_templates/`
- 新增文件：
  - `outputs/pressure_resolution_replay_scenario_pack/pressure_resolution_replay_rows_r7_completion_route_work_package_preflight.json`
- 当前默认未设置 `R7_TO_R8P_WORK_PACKAGE_DIR` 时：
  - `route_work_package_templates_status=route_work_package_templates_ready_not_evidence`
  - `route_work_package_preflight_status=route_work_package_preflight_waiting_for_submission_dir`
  - `expected_work_package_count=4`
  - `submitted_work_package_count=0`
  - `passed_work_package_count=0`
  - `blocked_work_package_count=4`
  - 每条路径均显式 `can_generate_field_evidence_from_preflight=False`、`can_write_to_actuator=False`、`can_write_to_release_gate=False`
- Agent60 offline fallback 仍为 `R8p_fix_field_rows_source_preflight`，但 trigger metric 已新增：
  - `r7_work_package_template_status=route_work_package_templates_ready_not_evidence`
  - `r7_work_package_preflight_status=route_work_package_preflight_waiting_for_submission_dir`
  - `r7_submitted_work_package_count=0`
  - `r7_passed_work_package_count=0`
  - `r7_blocked_work_package_count=4`

验证：

- `.venv/bin/python -m py_compile experiments/run_agent61_pressure_resolution_replay_scenario_pack.py src/water_ai/agents/agent_architecture_consolidation_agent.py experiments/run_agent60_agent_architecture_consolidation.py tests/test_pressure_resolution_replay_scenario_pack_agent.py tests/test_agent_architecture_consolidation_agent.py`：通过。
- `.venv/bin/pytest -q tests/test_pressure_resolution_replay_scenario_pack_agent.py tests/test_agent_architecture_consolidation_agent.py`：71 passed。
- `.venv/bin/pytest -q`：419 passed。

边界：

- 模板目录是提交入口，不是现场证据；原样提交会被 preflight 阻断。
- preflight passed 也只意味着候选完整，仍需 R7 import、R8p schema/provenance/semantic gates、R8v routing、field holdout、human review 和 release gate。
- 本轮没有导入真实 field package，没有进入 R8v，没有写 actuator、release gate 或 field-supported claim。

## 2026-06-04 R8u-25：R7-to-R8p Completion Route Work Packages

目标：

- 承接 R8u-24，让 route contracts 不只说明“每条证据路线由谁生产、进哪个门”，而是进一步变成 route-specific 工作包。
- 将 R7 source package、operator supplement、Agent52 replay export 和 R8p validation gates 分别拆成可交付的 work package，明确 expected_input_files、expected_output_files、submission_contract、acceptance_checks、validation_command、evidence_level_after_package 和 failure_boundary。
- 保持边界：work package 是工程交付接口，不生成真实现场数据，不写 actuator、release gate 或现场成立 claim。

实现：

- `experiments/run_agent61_pressure_resolution_replay_scenario_pack.py`：
  - 新增 `ROWS_R7_COMPLETION_ROUTE_WORK_PACKAGES_PATH`。
  - 新增 `_field_rows_r7_completion_route_work_packages()`，从 route contracts 生成四个 work package。
  - 新增 `_r7_completion_route_work_package()` 与 `_r7_completion_route_work_package_specs()`。
  - work packages 已写入 metrics、Agent61 report JSON、generated files、deliverable 和 manifest。
- `src/water_ai/agents/agent_architecture_consolidation_agent.py`：
  - 新增 `_r8p_pressure_resolution_r7_completion_route_work_packages()`。
  - Agent60 offline fallback 现在消费 `field_rows_r7_completion_route_work_packages`，并输出 route work package status、package count、open package count、open package ids 和 path。
- `experiments/run_agent60_agent_architecture_consolidation.py`：
  - Agent60 report、deliverable、manifest 和 `next_stage` 已写回 route work packages 状态与 open work packages。
- 测试：
  - Agent61 测试验证无 R7 包时四个 work package 均开放，且 R7 source package 阻断在真实 metadata/CSV 包。
  - Agent61 测试验证已有 R7 staged draft 时，R7 source package 转为 clear，operator supplement 与 Agent52 replay export work package 仍开放。
  - Agent60 测试验证 fallback 消费并透传 route work package status、open package count 和 open package ids。

当前输出：

- 新增文件：
  - `outputs/pressure_resolution_replay_scenario_pack/pressure_resolution_replay_rows_r7_completion_route_work_packages.json`
- 当前默认无 `REAL_FIELD_REPLAY_PACKAGE_DIR` 时：
  - `route_work_packages_status=route_work_packages_ready_waiting_for_r7_package`
  - `work_package_count=4`
  - `open_work_package_count=4`
  - `open_work_package_ids=[R8U25_R7_SOURCE_PACKAGE_WORK_PACKAGE, R8U25_OPERATOR_SUPPLEMENT_WORK_PACKAGE, R8U25_AGENT52_REPLAY_EXPORT_WORK_PACKAGE, R8U25_R8P_VALIDATION_GATES_WORK_PACKAGE]`
  - 每个 work package 均显式 `can_generate_field_evidence_by_package_only=False`、`can_write_to_actuator=False`、`can_write_to_release_gate=False`
- Agent60 offline fallback 仍为 `R8p_fix_field_rows_source_preflight`，但 trigger metric 已新增：
  - `r7_work_package_status=route_work_packages_ready_waiting_for_r7_package`
  - `r7_open_work_package_count=4`
  - `r7_open_work_package_ids=R8U25_R7_SOURCE_PACKAGE_WORK_PACKAGE,R8U25_OPERATOR_SUPPLEMENT_WORK_PACKAGE,R8U25_AGENT52_REPLAY_EXPORT_WORK_PACKAGE,R8U25_R8P_VALIDATION_GATES_WORK_PACKAGE`

验证：

- `.venv/bin/python -m py_compile experiments/run_agent61_pressure_resolution_replay_scenario_pack.py src/water_ai/agents/agent_architecture_consolidation_agent.py experiments/run_agent60_agent_architecture_consolidation.py tests/test_pressure_resolution_replay_scenario_pack_agent.py tests/test_agent_architecture_consolidation_agent.py`：通过。
- `.venv/bin/pytest -q tests/test_pressure_resolution_replay_scenario_pack_agent.py tests/test_agent_architecture_consolidation_agent.py`：70 passed。
- `.venv/bin/pytest -q`：418 passed。

边界：

- route work packages 让四条证据路线更可实施，但不生成真实数据。
- 当前 R7 source package、operator supplement 与 Agent52 replay export 仍未补齐，open work packages=4 是正确阻断。
- 本轮没有导入真实 field package，没有进入 R8v，没有写 actuator、release gate 或 field-supported claim。

## 2026-06-04 R8u-24：R7-to-R8p Completion Route Execution Contracts

目标：

- 承接 R8u-23，让 completion plan 不只说明“缺三类证据”，而是变成可执行、可验证、可由 Agent60 消费的 route-level 接口合同。
- 将 R7 source package、operator supplement、Agent49/52 replay export 和 Agent61/R8p validation gates 拆成四条 evidence route，分别明确 producer、input_contract、output_contract、required_fields_by_table、validation_gates、validation_command、downstream_consumers 和 failure_boundary。
- 保持边界：route contracts 是接口合同和执行工单，不是 field evidence，不能写 actuator、release gate 或现场成立 claim。

实现：

- `experiments/run_agent61_pressure_resolution_replay_scenario_pack.py`：
  - 新增 `ROWS_R7_COMPLETION_ROUTE_CONTRACTS_PATH`。
  - 新增 `_field_rows_r7_completion_route_contracts()`，从 completion plan 聚合四条 route contracts。
  - 新增 `_r7_completion_route_contract()` 与 `_required_fields_by_completion_table()`。
  - route contracts 已写入 metrics、Agent61 report JSON、generated files、deliverable 和 manifest。
- `src/water_ai/agents/agent_architecture_consolidation_agent.py`：
  - 新增 `_r8p_pressure_resolution_r7_completion_route_contracts()`。
  - Agent60 offline fallback 现在消费 `field_rows_r7_completion_route_contracts`，并输出 route contract status、route count、open route count、open route ids 和 path。
- `experiments/run_agent60_agent_architecture_consolidation.py`：
  - Agent60 report、deliverable、manifest 和 `next_stage` 已写回 route contracts 状态与 open routes。
- 测试：
  - Agent61 测试验证无 R7 包时四条 route 均开放，且 R7 source route 阻断在真实 source package。
  - Agent61 测试验证已有 R7 staged draft 时，R7 source route 转为 clear，operator supplement 与 Agent52 replay export 仍保持开放。
  - Agent60 测试验证 fallback 消费并透传 route contract status、open route count 和 open route ids。

当前输出：

- 新增文件：
  - `outputs/pressure_resolution_replay_scenario_pack/pressure_resolution_replay_rows_r7_completion_route_contracts.json`
- 当前默认无 `REAL_FIELD_REPLAY_PACKAGE_DIR` 时：
  - `completion_route_contracts_status=completion_route_contracts_ready_waiting_for_r7_package`
  - `route_contract_count=4`
  - `open_route_count=4`
  - `open_route_ids=[r7_source_package, operator_supplement, agent52_replay_export, r8p_validation_gates]`
  - 每条 route 均显式 `can_write_to_actuator=False`、`can_write_to_release_gate=False`
- Agent60 offline fallback 仍为 `R8p_fix_field_rows_source_preflight`，但 trigger metric 已新增：
  - `r7_route_contract_status=completion_route_contracts_ready_waiting_for_r7_package`
  - `r7_open_route_count=4`
  - `r7_open_route_ids=r7_source_package,operator_supplement,agent52_replay_export,r8p_validation_gates`

验证：

- `.venv/bin/python -m py_compile experiments/run_agent61_pressure_resolution_replay_scenario_pack.py src/water_ai/agents/agent_architecture_consolidation_agent.py experiments/run_agent60_agent_architecture_consolidation.py tests/test_pressure_resolution_replay_scenario_pack_agent.py tests/test_agent_architecture_consolidation_agent.py`：通过。
- `.venv/bin/pytest -q tests/test_pressure_resolution_replay_scenario_pack_agent.py tests/test_agent_architecture_consolidation_agent.py`：70 passed。
- `.venv/bin/pytest -q`：418 passed。

边界：

- route contracts 让证据路线更可执行，但不生成真实数据。
- R7 source package、operator supplement 与 Agent52 replay export 仍未补齐，当前 open routes=4 是正确阻断。
- 本轮没有导入真实 field package，没有进入 R8v，没有写 actuator、release gate 或 field-supported claim。

## 2026-06-04 R8u-23：Agent60 Consumes R7-to-R8p Completion Plan

目标：

- 承接 R8u-22，让 completion plan 不只停留在 Agent61/R8p 输出文件中，而是进入 Agent60 架构治理 fallback。
- 当真实 pressure-resolution 行包仍停在 source preflight 时，让治理层能区分 R7 source package、operator supplement 和 Agent52 replay export 三类补齐路线。
- 保持边界：Agent60 只消费 completion plan 作为下一步工单，不把它写成 field evidence、actuator action、release gate 或现场成立 claim。

实现：

- `src/water_ai/agents/agent_architecture_consolidation_agent.py`：
  - 新增 `_r8p_pressure_resolution_r7_completion_plan()`。
  - 在 `R8p_fix_field_rows_source_preflight` fallback 中读取 `field_rows_r7_completion_plan`。
  - fallback 新增 `r7_completion_plan_status`、`r7_completion_item_count`、`r7_completion_item_class_counts`、`r7_completion_field_gap_count_by_class`、`r7_completion_plan_path` 和 `r7_completion_required_execution_order`。
  - `trigger_metric` 和 `expected_metrics` 同步加入 completion plan 指标，让后续治理能直接追踪 evidence route gap。
- `experiments/run_agent60_agent_architecture_consolidation.py`：
  - Agent60 report、deliverable 和 manifest 写回 completion plan 状态、item 数、分类计数、字段缺口分类、plan 路径和执行顺序。
  - `next_stage` 现在会在离线 fallback 后追加 R7-to-R8p completion plan 摘要。
- `tests/test_agent_architecture_consolidation_agent.py`：
  - 扩展 R8p patch-plan fallback 测试，要求 Agent60 消费并透传 R7 completion plan。

当前输出：

- Agent60 离线 fallback 仍为 `R8p_fix_field_rows_source_preflight`。
- 新增/更新写回字段：
  - `latest_offline_core_fallback_r7_completion_plan_status=r7_to_r8p_completion_plan_waiting_for_r7_package`
  - `latest_offline_core_fallback_r7_completion_item_count=6`
  - `latest_offline_core_fallback_r7_completion_item_class_counts={r7_source_package:1, operator_supplement:4, agent52_replay_export:1}`
  - `latest_offline_core_fallback_r7_completion_field_gap_count_by_class={r7_source_package:0, operator_supplement:10, agent52_replay_export:11}`
  - `latest_offline_core_fallback_r7_completion_plan_path=outputs/pressure_resolution_replay_scenario_pack/pressure_resolution_replay_rows_r7_completion_plan.json`

验证：

- `.venv/bin/python -m py_compile src/water_ai/agents/agent_architecture_consolidation_agent.py experiments/run_agent60_agent_architecture_consolidation.py tests/test_agent_architecture_consolidation_agent.py`：通过。
- `.venv/bin/pytest -q tests/test_agent_architecture_consolidation_agent.py`：40 passed。
- `.venv/bin/pytest -q tests/test_pressure_resolution_replay_scenario_pack_agent.py tests/test_agent_architecture_consolidation_agent.py`：70 passed。
- `.venv/bin/pytest -q`：418 passed。

边界：

- completion plan 是工单和证据路线，不是现场证据。
- Agent60 消费 completion plan 不代表 R7 source package 已经存在，也不代表 operator supplement 或 Agent52 replay export 已补齐。
- 本轮没有导入真实 field package，没有进入 R8v，没有写 actuator、release gate 或 field-supported claim。

## 2026-06-04 R8u-22：R7-to-R8p Completion Plan

目标：

- 承接 R8u-21，把 staging preflight 中的字段缺口转成机器可读、可执行、可审查的补齐计划。
- 将 R8p pressure-resolution 行包需要的证据路线分离为 R7 source package、operator supplement、Agent52 replay export 和 R8p schema/preflight，避免现场观测、人工复核和 replay 输出混成同一类证据。
- 保持边界：completion plan 是补包/导出工单，不是 field evidence，不能写 actuator、release gate 或现场成立 claim。

实现：

- `experiments/run_agent61_pressure_resolution_replay_scenario_pack.py`：
  - 新增 `ROWS_R7_COMPLETION_PLAN_PATH`。
  - 新增 `_field_rows_r7_completion_plan()`，将 staging status、alignment mapping 和 evidence class 转成有序 completion items。
  - 新增 `_r7_source_package_completion_item()`、`_operator_supplement_completion_items()` 和 `_agent52_export_completion_item()`。
  - completion plan 已接入 metrics、Agent61 report JSON、generated files、deliverable 和 manifest。
- `tests/test_pressure_resolution_replay_scenario_pack_agent.py`：
  - 新增无 R7 package 时的 completion plan 测试。
  - 扩展临时 R7 package staging 测试，验证 plan 保留 `campaign_operation_log` operator supplement 和 `agent52_replay_table` replay export。

当前输出：

- 新增文件：
  - `outputs/pressure_resolution_replay_scenario_pack/pressure_resolution_replay_rows_r7_completion_plan.json`
- 默认无 `REAL_FIELD_REPLAY_PACKAGE_DIR` 时：
  - `completion_plan_status=r7_to_r8p_completion_plan_waiting_for_r7_package`
  - `item_count=6`
  - `item_class_counts={r7_source_package:1, operator_supplement:4, agent52_replay_export:1}`
  - `field_gap_count_by_class={operator_supplement:10, agent52_replay_export:11}`
  - `can_generate_field_evidence_from_plan=False`

验证：

- `.venv/bin/pytest -q tests/test_pressure_resolution_replay_scenario_pack_agent.py`：30 passed。
- `.venv/bin/pytest -q tests/test_pressure_resolution_replay_scenario_pack_agent.py tests/test_agent_architecture_consolidation_agent.py`：70 passed。
- `.venv/bin/pytest -q`：418 passed。

边界：

- completion plan 不会自动生成 operator review 结论，也不会伪造 Agent52 replay export。
- 即使 completion plan 全部执行，仍必须通过 Agent61 schema/provenance/template/bundle/temporal/semantic/downstream routing、R7 evidence chain 和人工复核。
- 本轮没有导入真实 field package，没有进入 R8v，没有写 actuator、release gate 或 field-supported claim。

## 2026-06-04 R8u-21：R7-to-R8p Staging Preflight And Draft Transformer

目标：

- 承接 R8u-20，不停留在字段对齐矩阵，而是把 R7/Agent44 真实 field package 到 R8p pressure-resolution replay rows 的转换推进为可执行 staging preflight。
- 让系统能自动区分：哪些 R7 字段可以直接复制，哪些需要别名转换，哪些只能从 metadata 复制 provenance，哪些必须由 operator supplement 补齐，哪些必须由 Agent49/52 replay export 生成。
- 保持证据边界：staged draft 只是补包草稿，不是 field evidence，不能写 actuator、release gate 或 field-supported claim。

实现：

- `experiments/run_agent61_pressure_resolution_replay_scenario_pack.py`：
  - 新增 `ROWS_R7_STAGING_PREFLIGHT_PATH` 与 `ROWS_R7_STAGED_DRAFT_PATH`。
  - 新增 `_r7_field_package_path()`，复用现有 `REAL_FIELD_REPLAY_PACKAGE_DIR`，避免新增并行配置。
  - 新增 `_field_rows_r7_staging_preflight()`，读取 R7 metadata/CSV 包，生成 R8p staged draft 与逐字段 gap report。
  - 新增 `_read_r7_staging_metadata()`、`_read_r7_staging_csv_tables()`、`_stage_r7_field()`、`_r7_supplement_candidate_value()` 和 `_r7_staging_next_action()`。
  - staging 已接入 metrics、Agent61 report JSON、generated files、deliverable 和 manifest。
- `tests/test_pressure_resolution_replay_scenario_pack_agent.py`：
  - 新增无 R7 package 时的阻断测试。
  - 新增临时 R7 metadata/CSV 包测试，验证 staged draft 可复制 `sample_time_min <- timestamp_min`、`data_origin <- metadata.json`、`instrument_id <- metadata.instrument_snapshot_id` 和 `operator_review_required <- pressure_headloss_review_required`，但仍保留 `pressure_source_resolution` operator gap 和 `agent52_replay_table` export gap。

当前输出：

- 新增文件：
  - `outputs/pressure_resolution_replay_scenario_pack/pressure_resolution_replay_rows_r7_staging_preflight.json`
  - `outputs/pressure_resolution_replay_scenario_pack/pressure_resolution_replay_rows_r7_staged_draft.json`
- 默认无 `REAL_FIELD_REPLAY_PACKAGE_DIR` 时：
  - `r7_staging_preflight_status=r7_to_r8p_staging_preflight_no_r7_package_supplied`
  - `staged_table_count=0`
  - `staged_row_count=0`
  - `agent52_export_required_field_gap_count=11`
  - `can_enter_r8p_schema_preflight=False`

验证：

- `.venv/bin/pytest -q tests/test_pressure_resolution_replay_scenario_pack_agent.py`：29 passed。
- `.venv/bin/pytest -q tests/test_pressure_resolution_replay_scenario_pack_agent.py tests/test_agent_architecture_consolidation_agent.py`：69 passed。
- `.venv/bin/pytest -q`：417 passed。

边界：

- R7-to-R8p staging 是草稿转换/预检层，不是 R8p acceptance。
- staged draft 仍必须补齐 operator supplement、Agent52 replay export、同批次六表 bundle、时间窗、场景语义、downstream routing、R7 evidence chain 和人工复核。
- 本轮没有导入真实 field package，没有进入 R8v，没有写 actuator、release gate 或现场成立 claim。

## 2026-06-03 Governance：专利级终局标准融入全局 Goal

目标：

- 承接用户对创新性和专利化边界的判断，把“专利级技术方案成熟度”加入全局 goal。
- 不把项目转向专利材料写作，也不承诺最终授权；只把专利交底所需的技术问题、技术手段、实施例、技术效果、现有技术区别和证据边界变成模型成熟度上限。
- 保留原有七层系统骨架、第一性原理、阶段门控节流和 synthetic/field 边界。

实现：

- `deliverables/model_core_optimization/model_core_goal.md` 新增：
  - `专利级终局标准`
  - “以可保护技术方案反推系统清晰度”的第一性原理
  - `可保护性` 架构优先级
  - 专利化永久约束和设计不变量
  - 每轮执行新增“是否接近专利级成熟度”的架构师式检查问题
- `deliverables/model_core_optimization/execution_prompt.md` 新增专利级成熟度执行要求。
- `deliverables/model_core_optimization/self_interrupt_checklist.md` 新增专利化相关节流规则：只有以专利为名扩大抽象表述且无技术特征/实施例/验证指标时才立即打断；普通专利灵感进入阶段边界 backlog。
- `notes/current_status.md` 已同步最新核心复盘承接。

边界：

- 专利级成熟度不是 legal opinion，不替代正式专利检索、代理人撰写和审查意见。
- “AI、多智能体、知识图谱、闭环控制”等抽象词不能单独作为创新点；必须回到低成本稀疏感知、循环/暂存结构、软传感灰箱状态、控制动作、replay/gate 和工程技术效果。
- 专利终局不放松 field validation；所有现场成立 claim 仍必须通过真实数据、replay、holdout、operator review 或 gate。

## 2026-06-04 R8u-20：R7-to-R8p Field Package Alignment

目标：

- 承接 R8u-19，把 R8p 专用 CSV 模板与 R7/Agent44 真实 field package 模板对齐，减少重复填表和字段错配。
- 明确哪些 R8p 字段可从 R7 field package 直接复用，哪些需要别名转换、metadata-to-row provenance copy、operator supplement，哪些必须来自 Agent49/52 replay export。
- 不把 R7 template 或 field CSV 自动升级为 R8p replay evidence。

实现：

- `experiments/run_agent61_pressure_resolution_replay_scenario_pack.py`：
  - 新增 `ROWS_R7_ALIGNMENT_PATH`。
  - 新增 `_field_rows_r7_alignment()`，读取 Agent44/R7 模板规格并逐字段生成 crosswalk。
  - 新增 `_r7_field_mapping()`、alias mapping、supplement mapping 和 table-level reuse summary。
  - alignment 已接入 metrics、Agent61 report JSON、generated files、operator handoff、deliverable 和 manifest。
- `tests/test_pressure_resolution_replay_scenario_pack_agent.py`：
  - 新增 R7-to-R8p alignment 测试，验证 5 张共享表、Agent52 replay export 硬边界、`sample_time_min <- timestamp_min` 别名、`data_origin <- metadata.json` provenance copy 和 operator supplement 边界。

当前输出：

- 新增文件：
  - `outputs/pressure_resolution_replay_scenario_pack/pressure_resolution_replay_rows_r7_alignment.json`
- 当前 alignment 计数：
  - expected_table_count：6
  - r7_shared_table_count：5
  - r8p_reusable_table_count：5
  - supplement_required_field_count：10
  - agent52_export_required_field_count：11
- `agent52_replay_table` 状态为 `requires_agent52_replay_export`，不能从现场 CSV 伪造。

验证：

- `.venv/bin/pytest -q tests/test_pressure_resolution_replay_scenario_pack_agent.py`：27 passed。
- `.venv/bin/pytest -q tests/test_pressure_resolution_replay_scenario_pack_agent.py tests/test_agent_architecture_consolidation_agent.py`：67 passed。
- `.venv/bin/pytest -q`：415 passed。

边界：

- crosswalk 是接口合同，不是数据转换结果。
- R7 field package 即使通过 Agent44，也仍需要 R8p supplement、Agent52 replay export、R8p preflight、R8v routing 和 R7 evidence chain。
- 本轮没有生成真实 field rows，没有进入 R8v，没有写 actuator、release gate 或 field-supported claim。

## 2026-06-04 R8u-19：R8p CSV/Metadata Collection Template

目标：

- 承接 R8u-18，把 “R8p 支持 metadata/CSV 目录包” 从读取能力推进为可执行采集工单。
- 生成可填写的 `metadata.json + 六张必需 CSV` 目录模板，减少真实 pressure-resolution replay 行包第一次提交的摩擦。
- 保持证据边界：模板原样提交必须被拦截，不能成为 field evidence。

实现：

- `experiments/run_agent61_pressure_resolution_replay_scenario_pack.py`：
  - 新增 `ROWS_CSV_TEMPLATE_DIR`。
  - 新增 `_write_field_rows_csv_template()`，生成 `metadata.json` 与 6 张 CSV。
  - CSV 表头优先列出 R8p required fields，再保留 scenario、collection、template/evidence 边界字段。
  - CSV 模板共写出 30 条场景级 TODO 行，对应 5 个 pressure-resolution 场景 x 6 张表。
  - `field_rows_csv_template` 已写入 metrics、Agent61 report JSON、generated files、handoff、deliverable 和 manifest。
- `tests/test_pressure_resolution_replay_scenario_pack_agent.py`：
  - 新增模板目录生成测试，验证 `metadata.json`、6 张 CSV、required field headers 和 30 条模板行。
  - 新增模板目录阻断测试，验证原样读取后得到 `schema_validation_failed_template_marker_contract` 和 `R8p_replace_template_markers_with_field_values`。

当前输出：

- 新增目录：
  - `outputs/pressure_resolution_replay_scenario_pack/pressure_resolution_replay_rows_csv_template/`
- 包含文件：
  - `metadata.json`
  - `node_modality_sensor_timeseries.csv`
  - `pressure_headloss_event_log.csv`
  - `campaign_operation_log.csv`
  - `offline_lab_results.csv`
  - `fast_proxy_event_log.csv`
  - `agent52_replay_table.csv`
- manifest 已记录：
  - `latest_r8p_pressure_resolution_replay_rows_csv_template`
  - `pressure_resolution_replay_scenario_pack.pressure_resolution_replay_rows_csv_template`

验证：

- `.venv/bin/pytest -q tests/test_pressure_resolution_replay_scenario_pack_agent.py`：26 passed。
- `.venv/bin/pytest -q tests/test_pressure_resolution_replay_scenario_pack_agent.py tests/test_agent_architecture_consolidation_agent.py`：66 passed。
- `.venv/bin/pytest -q`：414 passed。

边界：

- CSV 模板目录是采集合同，不是 field evidence。
- 模板保留 TODO、`template_only=True` 和 `template_not_field_evidence`，原样提交会被 template-marker gate 拒绝。
- 本轮仍没有真实 field rows，没有进入 R8v，没有写 actuator、release gate 或 field-supported claim。

## 2026-06-04 R8u-18：R8p CSV/Metadata Field Rows Source Adapter

目标：

- 承接 R8u-17，降低真实 pressure-resolution 行包进入 R8p/R8v 门控的工程摩擦。
- 把 R8p 输入从只支持 JSON 表映射扩展为双格式：JSON 文件，或 `metadata.json + 六张必需 CSV` 目录包。
- 不新增 agent，不伪造真实行，不改变 R8p/R8v 证据门；只让现场数据提供者可以按更接近 Agent44/R7 的 metadata/CSV 包习惯提交数据。

实现：

- `experiments/run_agent61_pressure_resolution_replay_scenario_pack.py`：
  - `_read_field_rows_package()` 保持原 JSON 兼容，同时新增目录包分支。
  - 新增 `field_rows_source_format` 与 `accepted_source_formats`。
  - 新增 `field_rows_directory_metadata` 审计，只作为 provenance context，不作为 field evidence。
  - 对 CSV 数字和布尔字段按 R8p schema 做保守类型转换；无法转换的值保留为字符串，由 schema validation 继续拦截。
  - operator handoff 和 patch plan 的 source package 文案更新为 JSON 文件或 metadata/CSV 目录包。
- `tests/test_pressure_resolution_replay_scenario_pack_agent.py`：
  - 新增 CSV 目录包成功测试：从完整 field rows 临时写出 6 张 CSV，验证 source、schema、same-batch bundle、temporal window、scenario semantic、downstream routing 全部通过。
  - 新增缺 CSV 表测试：缺少 `agent52_replay_table.csv` 时，source status 为 `field_rows_directory_loaded_with_schema_gaps`，schema validation 和 patch plan 正确阻断。

当前输出：

- 默认真实行包仍缺失，因此 R8p 默认状态继续停在 `field_rows_file_missing` / `schema_validation_blocked_at_source_preflight`。
- manifest 已记录 `latest_r8p_field_rows_source_format` 和 `latest_r8p_field_rows_accepted_source_formats`。
- R8p 的 `source_package` 验收顺序现在明确允许 `json_table_mapping` 或 `csv_directory_with_optional_metadata_json`。

验证：

- `.venv/bin/pytest -q tests/test_pressure_resolution_replay_scenario_pack_agent.py`：24 passed。
- `.venv/bin/pytest -q tests/test_pressure_resolution_replay_scenario_pack_agent.py tests/test_agent_architecture_consolidation_agent.py`：64 passed。
- `.venv/bin/pytest -q`：412 passed。

边界：

- CSV/metadata 目录包只是现场采集和导入接口，不自动成为真实现场证据。
- 即使 CSV 目录包 source/schema 通过，仍必须继续通过 field provenance、TODO/template、same-batch bundle、temporal window、scenario semantic、downstream routing、R7 evidence chain、claim gate 和人工复核。
- 本轮没有生成真实 field rows，没有进入 R8v，也没有写 actuator、release gate 或 field-supported claim。

## 2026-06-04 R8u-17：R8v Downstream-Routing Preflight

目标：

- 承接 R8u-16，把 “R8p accepted rows 下一步进入 R8v” 从一句 fallback 推荐压实为机器可读下游路由合同。
- 防止 R8p 行级验收通过后被误读为可直接写 actuator、release gate 或 field-supported claim。
- 不新增 agent，不生成真实行；只定义 R8p accepted rows 到 Agent51/49/52/R7 gates 的路由目标、输入边界、预期指标和禁止事项。

实现：

- 新增 `field_rows_downstream_routing_preflight`：
  - `field_rows_downstream_routing_preflight_status`
  - `accepted_batches_for_routing`
  - `routing_target_count`
  - `routing_ready_target_count`
  - `routing_targets`
  - `downstream_gate_sequence`
  - `can_route_to_r8v`
- 新增输出文件：
  - `outputs/pressure_resolution_replay_scenario_pack/pressure_resolution_replay_rows_downstream_routing_preflight.json`
- 固化 4 个 R8v 路由目标：
  - Agent51 catalyst proxy holdout
  - Agent49 guardrail context
  - Agent52 replay clearance
  - R7 evidence chain
- Agent60 的 R8v fallback 收紧：只有 R8p 行级验收全部通过且 downstream routing preflight 也通过，才会输出 `R8v_route_pressure_resolution_rows_to_field_replay_and_holdout_gates`。
- Agent60 的 R8p patch-plan fallback 现在同步消费 downstream routing status、summary 和 path。
- Agent61 deliverable/report、manifest 和 handoff 已输出 downstream routing preflight 状态与路径。

当前输出：

- 默认真实行包仍缺失，因此 downstream-routing preflight 正确停在 `downstream_routing_preflight_blocked_at_source_preflight`。
- `routing_target_count=4` 只表示合同中定义了 4 个下游 gate；`routing_ready_target_count=0` 表示当前没有 accepted rows 可路由。
- `can_route_to_r8v=False`，所以不能进入 Agent51/49/52/R7 下游 gate，更不能写 actuator 或 release gate。

验证：

- `.venv/bin/pytest -q tests/test_pressure_resolution_replay_scenario_pack_agent.py tests/test_agent_architecture_consolidation_agent.py`：62 passed。
- `.venv/bin/pytest -q`：410 passed。

边界：

- downstream-routing preflight 只负责把 accepted rows 送入下游验证链，不负责生成 field-supported claim。
- 即使未来 routing preflight 通过，仍必须经过 Agent51 field proxy holdout、Agent49 guardrail context、Agent52 replay clearance、R7 evidence chain、claim gate 和人工复核。
- 真实 actuator/release-gate 写入仍保持禁止，除非后续独立 gate 明确通过。

## 2026-06-04 R8u-16：R8p Scenario-Semantic Preflight

目标：

- 承接 R8u-15，把 pressure-resolution 场景语义从后置 scenario acceptance 前移为独立 preflight。
- 在 source/schema/template/provenance、same-batch bundle 和 temporal-window 均通过之后，先确认每个场景的“语义”是否符合控制安全边界。
- 不新增 agent，不生成真实行；只增强 Agent61/R8p 验证门、patch plan、handoff、Agent60 fallback 和测试保护。

实现：

- Agent61 core acceptance 加固 unresolved conflict 语义：
  - unresolved pressure conflict 必须同时具备 operation review、Agent52 operator-review flag 和 `pressure_source_conflict_control_block=True`。
  - 若缺少控制阻断，batch 会出现 `unresolved_conflict_requires_operator_review_and_replay_block`。
- 新增 `field_rows_scenario_semantic_preflight`：
  - `field_rows_scenario_semantic_preflight_status`
  - `checked_batch_count`
  - `semantic_valid_batch_count`
  - `semantic_violation_count`
  - `condition_violation_counts`
  - `scenario_semantic_status`
  - `batch_semantic_checks`
- 新增输出文件：
  - `outputs/pressure_resolution_replay_scenario_pack/pressure_resolution_replay_rows_scenario_semantic_preflight.json`
- `_field_rows_patch_plan()` 新增 patch type：
  - `scenario_semantic_contract`
  - next action：`R8p_fix_pressure_resolution_scenario_semantics`
  - 排序位置在 temporal-window 之后、scenario acceptance 之前。
- collection checklist 新增状态：
  - `field_rows_collection_checklist_ready_needs_scenario_semantic_fixes`
- operator handoff 新增：
  - `field_rows_scenario_semantic_preflight_status`
  - `scenario_semantic_preflight_summary`
  - `field_rows_scenario_semantic_preflight_path`
- Agent60 fallback 新增消费：
  - trigger metric 输出 `scenario_semantic_preflight_status`
  - expected metrics 新增 `field_rows_scenario_semantic_preflight_status`、`field_rows_semantic_valid_batch_count`、`field_rows_semantic_violation_count`
  - manifest 新增 offline fallback semantic status/count/path。

当前输出：

- 默认真实行包仍缺失，因此 scenario-semantic preflight 正确停在 `scenario_semantic_preflight_blocked_at_source_preflight`。
- `semantic_violation_count=0` 不能解释为场景语义已通过；它只表示 source 尚未加载，无法进行 batch-level semantic check。
- 新增失败测试证明：如果 unresolved conflict 的 Agent52 replay 行缺少 `pressure_source_conflict_control_block=True`，系统会生成 `field_rows_patch_plan_blocked_at_scenario_semantic_contract`，最高优先项为 `R8P_SCENARIO_SEMANTIC_R8O_S1_UNRESOLVED_PRESSURE_CONFLICT_REVIEW_BLOCK`。

验证：

- `.venv/bin/pytest -q tests/test_pressure_resolution_replay_scenario_pack_agent.py tests/test_agent_architecture_consolidation_agent.py`：62 passed。
- `.venv/bin/pytest -q`：410 passed。

边界：

- scenario-semantic preflight 只证明 pressure-resolution 场景意义在同批次证据内自洽。
- 语义通过不等于 field claim 通过，不允许写 actuator 或 release gate。
- 真实行仍必须继续通过 R8p scenario acceptance、R8v routing、Agent51/49/52/R7 gates 和人工复核。

## 2026-06-04 R8u-15：R8p Temporal-Window Preflight

目标：

- 承接 R8u-14，把“循环/暂存结构是否真的为低频传感、快代理、离线检测和人工复核争取到时间”从抽象设计点压实为可验时间窗合同。
- 在同批次六表 bundle 完整之后、scenario acceptance 之前，先检查同批次传感采样、压力事件、快代理、离线标签和 hold/recycle 时间是否构成可执行闭环。
- 不新增 agent，不生成真实数据；只增强 R8p 输入合同、真实行验收、patch plan、handoff、Agent60 fallback 和测试保护。

实现：

- Agent61 core acceptance 新增 temporal blockers：
  - `temporal_order_requires_sensor_sample_before_pressure_event`
  - `temporal_order_requires_pressure_event_before_fast_proxy`
  - `temporal_order_requires_lab_sample_before_lab_label`
  - `temporal_order_requires_pressure_matched_lab_within_label_window`
  - `temporal_order_requires_fast_proxy_before_lab_label`
  - `hold_time_budget_must_cover_slowest_evidence_label`
- 新增 `field_rows_temporal_window_preflight`：
  - `field_rows_temporal_window_preflight_status`
  - `checked_batch_count`
  - `temporal_valid_batch_count`
  - `temporal_violation_count`
  - `hold_time_violation_count`
  - `scenario_temporal_status`
  - `batch_temporal_checks`
- 新增输出文件：
  - `outputs/pressure_resolution_replay_scenario_pack/pressure_resolution_replay_rows_temporal_window_preflight.json`
- `_field_rows_patch_plan()` 新增 patch type：
  - `temporal_window_contract`
  - next action：`R8p_fix_same_batch_timestamps_and_hold_time_budget`
  - 排序位置在 source/schema/template/provenance/batch bundle 之后、scenario acceptance 之前。
- collection checklist 新增状态：
  - `field_rows_collection_checklist_ready_needs_temporal_window_fixes`
- operator handoff 新增：
  - `field_rows_temporal_window_preflight_status`
  - `temporal_window_preflight_summary`
  - `field_rows_temporal_window_preflight_path`
- Agent60 fallback expected metrics 新增：
  - `field_rows_temporal_window_preflight_status`
  - `field_rows_temporal_valid_batch_count`
  - `field_rows_temporal_violation_count`
  - `field_rows_hold_time_violation_count`

当前输出：

- 默认真实行包仍缺失，因此 temporal-window preflight 正确停在 `temporal_window_preflight_blocked_at_source_preflight`。
- `temporal_violation_count=0`、`hold_time_violation_count=0` 不能解释为时间窗已通过；它只表示 source 尚未加载，无法进行 batch-level temporal check。
- 如果 source/schema/template/provenance 和同批次六表 bundle 均通过，但 `hold_time_min` 小于最慢证据到达时间，系统会生成 `field_rows_patch_plan_blocked_at_temporal_window_contract`，并在 Agent61 acceptance 中拒绝该 batch。

验证：

- `.venv/bin/pytest -q tests/test_pressure_resolution_replay_scenario_pack_agent.py tests/test_agent_architecture_consolidation_agent.py`：61 passed。
- `.venv/bin/pytest -q`：409 passed。

边界：

- temporal-window preflight 只证明低频观测、快代理、离线标签和暂存/回流时间窗可用于尝试场景验收。
- 时间窗通过不等于 field claim 通过，不允许写 actuator 或 release gate。
- 真实行仍必须继续通过 R8p scenario acceptance、R8v routing、Agent51/49/52/R7 gates 和人工复核。

## 2026-06-04 R8u-14：R8p Same-Batch Bundle Preflight

目标：

- 承接 R8u-13，把“同一批次六张现场表是否形成完整 replay 证据包”从后置 scenario acceptance 前移为独立 batch bundle preflight。
- 让操作员在真实行包上传后能直接看到哪个 `batch_id` 缺哪张表，而不是只看到某个 pressure-resolution 场景未通过。
- 不新增 agent，不生成真实数据；只把 R8p 的现场包接口、补包动作、handoff、Agent60 fallback 和测试进一步压实。

实现：

- 新增 `field_rows_batch_bundle_preflight`：
  - `field_rows_batch_bundle_preflight_status`
  - `candidate_batch_count`
  - `complete_bundle_count`
  - `partial_bundle_count`
  - `missing_bundle_table_count`
  - `scenario_bundle_status`
  - `candidate_batch_bundles`
- 新增输出文件：
  - `outputs/pressure_resolution_replay_scenario_pack/pressure_resolution_replay_rows_batch_bundle_preflight.json`
- `_field_rows_patch_plan()` 新增 patch type：
  - `batch_bundle_contract`
  - next action：`R8p_complete_same_batch_six_table_bundles`
  - 排序位置在 source/schema/template/provenance 之后、scenario acceptance 之前。
- collection checklist 新增状态：
  - `field_rows_collection_checklist_ready_needs_same_batch_bundle_completion`
- operator handoff 新增：
  - `field_rows_batch_bundle_preflight_status`
  - `batch_bundle_preflight_summary`
  - `field_rows_batch_bundle_preflight_path`
- Agent60 fallback expected metrics 新增：
  - `field_rows_batch_bundle_preflight_status`
  - `field_rows_complete_batch_bundle_count`
  - `field_rows_partial_batch_bundle_count`
  - `field_rows_missing_bundle_table_count`

当前输出：

- 默认真实行包仍缺失，因此 batch bundle preflight 正确停在 `batch_bundle_preflight_blocked_at_source_preflight`。
- `complete_bundle_count=0`、`partial_bundle_count=0`、`missing_bundle_table_count=0` 不能解释为 bundle 已完整；它只表示 source 尚未加载，无法进行 batch-level bundle 检查。
- 如果 source/schema/template/provenance 均通过，但同一场景的某张表使用了不同 `batch_id`，系统会生成 `field_rows_patch_plan_blocked_at_batch_bundle_contract`，并指出缺失表与候选 batch。

验证：

- `.venv/bin/pytest -q tests/test_pressure_resolution_replay_scenario_pack_agent.py tests/test_agent_architecture_consolidation_agent.py`：60 passed。
- `.venv/bin/pytest -q`：408 passed。

边界：

- batch bundle preflight 只证明同一批次六表可用于尝试 scenario acceptance，不证明语义有效、现场 claim 成立、可写执行器或可放行。
- 真实行仍必须继续通过 R8p scenario acceptance、R8v routing、Agent51/49/52/R7 gates 和人工复核。
- 当前没有真实 source package，不能把任何 synthetic/template/sample 行写成 field-supported 结论。

## 2026-06-04 R8u-13：R8p Template-Marker-Aware Schema Preflight

目标：

- 承接 R8u-12，把 TODO/template/sample 占位值从后置 scenario acceptance 前移到 schema/template-marker preflight。
- 防止表结构完整、字段齐全、部分类型也可解析的模板行包被误认为“可以进入真实场景验收”。
- 不新增 agent，不生成真实行；只加固 R8p 真实行包的证据准入合同。

实现：

- `_field_rows_schema_validation()` 新增：
  - `template_marker_gap_count`
  - `template_marker_gaps_by_row`
  - `schema_validation_failed_template_marker_contract`
- 必填字段中出现以下值会被计入 template marker gap：
  - `TODO*`
  - 包含 `todo_`
  - 包含 `template`
  - `field_validation_required`
  - `replace_me`
  - `sample_only`
- `_field_rows_patch_plan()` 新增 P0 patch type：
  - `template_marker_contract`
  - patch id：`R8P_SCHEMA_TEMPLATE_MARKERS_<TABLE>`
  - next action：`R8p_replace_template_markers_with_field_values`
- patch plan 的 P0 内部排序改为：
  - source/table shape
  - template marker
  - field origin
  - schema row contract
  - scenario acceptance
- collection checklist 新增状态：
  - `field_rows_collection_checklist_ready_needs_template_marker_replacement`
- operator handoff、Agent61 report、deliverable、manifest 和 Agent60 fallback expected metrics 新增 template marker 计数。

当前输出：

- 默认真实行包仍缺失，因此 `template_marker_gap_count=0` 不是模板通过证明，而是“尚无行可验”。
- manifest 当前 template marker preflight 为 `template_marker_preflight_blocked_at_source_preflight`。
- 如果把 `pressure_resolution_replay_rows_template.json` 当作真实行包上传，会在 schema/template-marker preflight 阶段得到 `schema_validation_failed_template_marker_contract`，并生成 P0 `R8P_SCHEMA_TEMPLATE_MARKERS_<TABLE>` 补包项。

验证：

- `.venv/bin/pytest -q tests/test_pressure_resolution_replay_scenario_pack_agent.py tests/test_agent_architecture_consolidation_agent.py`：59 passed。
- `.venv/bin/pytest -q`：407 passed。

边界：

- template-marker preflight 只证明模板占位值是否被替换，不证明现场数据真实性。
- `template_marker_gap_count=0` 只有在 source package 已加载且存在行时才可解释为模板占位值预检清洁；source missing 时不能解释为模板已替换。
- 即使模板值和来源字段都通过，仍必须通过 R8p same-batch scenario acceptance、R8v routing、Agent51/49/52/R7 gates 和人工复核。

## 2026-06-04 R8u-12：R8p Provenance-Aware Schema Preflight

目标：

- 承接 R8u-11，把“每张必需表都要 field-origin `data_origin`”从后置 scenario acceptance 前移到 schema/provenance preflight。
- 让现场行包上传后，系统能直接报告 `data_origin` 来源错误，而不是等同批次场景验收失败后才看到模糊 blocker。
- 不新增 agent，不生成任何真实行；只增强 R8p 输入合同、patch plan、handoff、Agent60 fallback 和测试保护。

实现：

- `_field_rows_schema_validation()` 新增：
  - `field_origin_gap_count`
  - `field_origin_gaps_by_row`
  - `schema_validation_failed_provenance_contract`
- 当必需表中 `data_origin` 存在但为 synthetic/template/TODO/non-field 时，schema validation 会记录 row index、observed value 和规则 `must_be_field_origin_not_template_synthetic_or_todo`。
- `_field_rows_patch_plan()` 新增 P0 patch type：
  - `field_origin_contract`
  - patch id：`R8P_SCHEMA_FIELD_ORIGIN_<TABLE>`
  - next action：`R8p_fix_field_origin_provenance`
- collection checklist 新增状态：
  - `field_rows_collection_checklist_ready_needs_field_origin_provenance`
- operator handoff、Agent61 report、deliverable 和 manifest 新增 `field_origin_gap_count`。
- Agent60 fallback 的 expected metrics 新增：
  - `field_rows_schema_field_origin_gap_count`
- manifest 新增：
  - `latest_r8p_field_rows_schema_field_origin_gap_count`
  - `latest_r8p_field_rows_provenance_preflight_status`
  - `latest_offline_core_fallback_schema_field_origin_gap_count`

当前输出：

- 默认真实行包仍缺失，因此 `field_origin_gap_count=0` 不是通过证明，而是“尚无行可验”。
- manifest 当前 provenance preflight 为 `provenance_preflight_blocked_at_source_preflight`。
- 若后续真实行包中某张表出现 `data_origin=synthetic_lab_demo`，会在 schema/provenance preflight 阶段得到 `schema_validation_failed_provenance_contract` 和对应 P0 补包项。

验证：

- `.venv/bin/pytest -q tests/test_pressure_resolution_replay_scenario_pack_agent.py tests/test_agent_architecture_consolidation_agent.py`：58 passed。
- `.venv/bin/pytest -q`：406 passed。

边界：

- provenance-aware preflight 仍只是准入预检，不是 field evidence。
- `field_origin_gap_count=0` 只有在 source package 已加载且行存在时才表示来源字段预检清洁；在 source missing 时不能解释为现场来源通过。
- 即使 provenance preflight 通过，仍必须通过 R8p same-batch scenario acceptance、R8v routing、Agent51/49/52/R7 gates 和人工复核。

## 2026-06-04 R8u-11：R8p All-Table Field Provenance Gate

目标：

- 承接 R8u-10，把 R8p 的 field provenance gate 从 `agent52_replay_table` 单表压实到全部 6 张必需表。
- 防止真实行包中某些表满足字段 shape，但以 synthetic/template/TODO 来源混入 field claim 链。
- 不新增 agent，不生成假 field rows；只加固已有 Agent61/R8p 验收合同、checklist 和 manifest 状态。

实现：

- `PressureResolutionReplayScenarioPackAgent` 的 5 张非 Agent52 表必填字段均新增 `data_origin`：
  - `node_modality_sensor_timeseries`
  - `pressure_headloss_event_log`
  - `campaign_operation_log`
  - `offline_lab_results`
  - `fast_proxy_event_log`
- R8p scenario acceptance 现在要求所有必需表行同时满足：
  - 必填字段非空、非 TODO/template。
  - `data_origin` 必须通过 field-origin 判定。
- 任意必需表出现非 field 来源时，blocking reason 进入 `<table>:missing_real_required_fields_or_field_origin`。
- partial accepted 情况也会输出 `pressure_resolution_field_rows_rejected` issue，避免“部分场景通过”被误读为整体 field ready。
- `pressure_resolution_replay_rows_collection_checklist.json` 中 `data_origin` 的字段角色为 `field_provenance_gate`，validation rule 为 `must_be_field_origin_not_template_synthetic_or_todo`。
- `field_rows_operator_handoff` 的 schema boundary 已从“non-field Agent52 replay origin”更新为“non-field provenance in any required table”。
- manifest 新增：
  - `latest_r8p_field_rows_all_tables_require_data_origin=True`
  - `latest_r8p_field_rows_provenance_gate_status=all_required_tables_require_field_origin`
  - `latest_r8p_field_rows_provenance_required_table_count=6`

当前输出：

- checklist id：`R8u11_pressure_resolution_real_rows_collection_checklist`
- provenance gate：`all_required_tables_require_field_origin`
- 当前真实行包仍缺失，`field_rows_source_status=field_rows_file_missing`。
- fallback 仍为 `R8p_fix_field_rows_source_preflight`，通过真实 rows 后才可进入 R8v/R7/Agent51/49/52 下游 gate。

验证：

- `.venv/bin/pytest -q tests/test_pressure_resolution_replay_scenario_pack_agent.py tests/test_agent_architecture_consolidation_agent.py`：57 passed。
- `.venv/bin/pytest -q`：405 passed。

边界：

- provenance gate 是 field evidence 的准入条件，不是 field evidence 本身。
- 即使所有表都带 field-origin `data_origin`，仍必须继续通过同 batch linkage、operator review/calibration、Agent52 replay pair、Agent51 holdout、Agent49 control context、R7 evidence chain 和人工复核。
- 当前没有真实 source package，因此不能写 actuator、release gate、protective control candidate 或 field-supported claim。

## 2026-06-03 R8u-10：R8p Field Rows Collection Checklist Contract

目标：

- 承接 R8u-9，把真实行包接入从“schema 验证摘要”继续推进为“机器可读采集清单”。
- 不新增 agent，不创建 `pressure_resolution_replay_rows.json`，不填充 fake field rows；只把每个场景、每张表、每个必填字段、验收顺序和证据边界转成可执行合同。
- 让 R8p 补包不再停留在“创建真实行包”这一句话，而是能说明按什么场景采、采哪些表、每个字段承担什么证据角色、如何验证、通过后进入哪一层 gate。

实现：

- `experiments/run_agent61_pressure_resolution_replay_scenario_pack.py` 新增：
  - `ROWS_COLLECTION_CHECKLIST_PATH`
  - `_field_rows_collection_checklist()`
  - `_table_collection_role()`
  - `_field_collection_role()`
  - `_field_validation_rule()`
- Agent61 新增生成文件：
  - `outputs/pressure_resolution_replay_scenario_pack/pressure_resolution_replay_rows_collection_checklist.json`
- checklist 内容包括：
  - 5 个 pressure resolution 场景的 collection checklist。
  - 6 张必需表的 table/field checklist。
  - 每个必填字段的 expected type、evidence role 和 validation rule。
  - source package、schema contract、scenario bundle、downstream routing 四步验收顺序。
  - 技术问题、技术手段、技术效果、现有技术区别候选和 claim boundary。
  - field evidence boundaries 与 `can_write_to_actuator=False`、`can_write_to_release_gate=False`。
- Agent61 metrics、deliverable、report、manifest 已接入 `field_rows_collection_checklist`。
- Agent61 `field_rows_operator_handoff` 新增：
  - `collection_checklist_path`
  - `field_rows_collection_checklist_status`
  - `field_rows_collection_checklist_item_count`
- Agent60 fallback 已消费 checklist status/path，并把 `field_rows_collection_checklist_status` 放入 trigger metric 和 expected metrics。

当前输出：

- checklist 文件：`outputs/pressure_resolution_replay_scenario_pack/pressure_resolution_replay_rows_collection_checklist.json`
- 当前状态：`field_rows_collection_checklist_ready_needs_source_package`
- scenario count：5。
- table count：6。
- fallback 仍为 `R8p_fix_field_rows_source_preflight`。
- 当前真实行包仍缺失，schema validation 仍为 `schema_validation_blocked_at_source_preflight`。

验证：

- `.venv/bin/pytest -q tests/test_pressure_resolution_replay_scenario_pack_agent.py tests/test_agent_architecture_consolidation_agent.py`：56 passed。
- `.venv/bin/pytest -q`：404 passed。

边界：

- collection checklist 是现场采集和验证合同，不是 field evidence。
- checklist 里的技术问题/技术手段/技术效果只是专利级技术特征 scaffold，不是 legal opinion，也不是 field-supported claim。
- 真实行仍必须通过 R8p acceptance、R8v routing、Agent51/49/52/R7 gates 和人工复核，才能讨论保护性控制候选或现场 claim。

## 2026-06-03 R8u-9：R8p Runtime Schema Validation Summary

目标：

- 承接 R8u-8，把机器可读 schema 从“导出合同”推进为“运行时验证摘要”。
- 在 R8p field row acceptance 之前，先明确真实行包到底是 source preflight 阻断、table contract 阻断，还是 row contract 字段/类型阻断。
- 让 Agent60 的离线 fallback 不只知道缺真实行包，还能知道缺口是否来自文件缺失、表缺失、必填字段缺失或粗类型错误。

实现：

- `experiments/run_agent61_pressure_resolution_replay_scenario_pack.py` 新增运行时 `field_rows_schema_validation`，检查：
  - source preflight 是否已经阻断；
  - 六张必需表是否存在；
  - 行对象是否满足 schema 必填字段；
  - 布尔、数字、字符串、列表和对象等粗类型是否满足合同。
- Agent61 deliverable/report/metrics/manifest 新增：
  - `field_rows_schema_validation_status`
  - `schema_required_field_gap_count`
  - `schema_invalid_type_count`
  - `schema_validation_summary`
- R8p `field_rows_patch_plan` 和 `field_rows_operator_handoff` 已消费 schema validation 摘要：如果行包存在但字段或类型不满足合同，补包动作会指向 row contract 修复，而不是泛化为“继续收集数据”。
- Agent60 fallback 已消费并透传：
  - `field_rows_schema_validation_status`
  - `schema_validation_summary`
  - schema validation 相关 expected metrics
- `deliverables/manifest.json` 新增最新 schema validation 状态和缺口计数字段。

当前输出：

- 当前默认真实行包仍缺失，状态为 `schema_validation_blocked_at_source_preflight`。
- `missing_table_count=6`。
- `schema_required_field_gap_count=0`。
- `schema_invalid_type_count=0`。
- 当前 fallback 仍是 `R8p_fix_field_rows_source_preflight`，不是 R8v field replay/holdout。

验证：

- `.venv/bin/pytest -q tests/test_pressure_resolution_replay_scenario_pack_agent.py tests/test_agent_architecture_consolidation_agent.py`：54 passed。
- `.venv/bin/pytest -q`：402 passed。

边界：

- schema validation 只验证 source/table/required-field shape 和粗类型，不证明数据来自真实现场。
- 它不替代 R8p scenario acceptance、Agent52 replay linkage、operator review、field origin、R8v holdout 或 R7 evidence chain。
- 当前没有真实行包，所以不能写 actuator、release gate、protective control candidate 或 field-supported claim。

## 2026-06-03 R8u-8：R8p Field Rows Machine-Readable Schema Contract

目标：

- 承接 R8u-7，把现场行包 handoff 从“人可读操作交接”继续压实为“机器可读 schema 合同”。
- 不创建 `pressure_resolution_replay_rows.json`，不填充模板，不伪造 field evidence；只导出真实行包的结构契约。
- 让现场行包在进入 R8p acceptance 前，先具备稳定的 source/table/required-field shape 验证依据。

实现：

- `experiments/run_agent61_pressure_resolution_replay_scenario_pack.py` 新增：
  - `ROWS_SCHEMA_PATH`
  - `_field_rows_package_schema()`
  - `_table_schema()`
  - `_field_schema()`
- Agent61 新增生成文件：
  - `outputs/pressure_resolution_replay_scenario_pack/pressure_resolution_replay_rows_schema.json`
- Agent61 metrics 新增 `field_rows_package_schema`。
- Agent61 handoff 新增：
  - `field_rows_package_schema_status=field_rows_package_schema_ready`
  - `rows_schema_path`
  - `schema_boundary`
- Agent60 fallback 新增透传：
  - `field_rows_package_schema_status`
  - `rows_schema_path`
  - `schema_status` trigger metric
- `deliverables/manifest.json` 新增：
  - `latest_r8p_field_rows_package_schema_status`
  - `latest_r8p_pressure_resolution_replay_rows_schema`
  - `latest_offline_core_fallback_schema_status`
  - `latest_offline_core_fallback_rows_schema_path`

当前输出：

- schema 文件：`outputs/pressure_resolution_replay_scenario_pack/pressure_resolution_replay_rows_schema.json`
- 根对象要求 6 张表：
  - `agent52_replay_table`
  - `campaign_operation_log`
  - `fast_proxy_event_log`
  - `node_modality_sensor_timeseries`
  - `offline_lab_results`
  - `pressure_headloss_event_log`
- 根对象 `additionalProperties=False`，防止未知表静默进入。
- 行对象允许额外现场 metadata，但必填 R8p 当前合同字段。

验证：

- `.venv/bin/pytest -q tests/test_pressure_resolution_replay_scenario_pack_agent.py tests/test_agent_architecture_consolidation_agent.py`：52 passed。
- `.venv/bin/pytest -q`：400 passed。

边界：

- schema 只证明 source/table/required-field shape 可读，不证明 rows 是 field evidence。
- R8p acceptance 仍负责拒绝 TODO/template、弱场景 linkage 和非 field Agent52 replay origin。
- schema ready 不能写 actuator、release gate 或 field-supported claim。

## 2026-06-03 R8u-7：R8p Field Rows Operator Handoff

目标：

- 承接 R8u-6，让 `R8p_fix_field_rows_source_preflight` 不只是一句 fallback 动作，而是现场人员可执行、可验收的数据接入合同。
- 不新增 agent、不创建假真实数据、不放松执行器或 release gate；只增强 Agent61/60 对真实行包接入路径的可操作性。
- 把“缺真实 pressure resolution replay 行包”拆成路径、模板、环境变量、验收命令、必需表字段、四级里程碑和模板拒绝规则。

实现：

- `experiments/run_agent61_pressure_resolution_replay_scenario_pack.py` 新增 `_field_rows_operator_handoff()`。
- Agent61 metrics 新增 `field_rows_operator_handoff`，包含：
  - `field_rows_operator_handoff_status`
  - `default_field_rows_path`
  - `template_rows_path`
  - `env_override_name=PRESSURE_RESOLUTION_REPLAY_ROWS_PATH`
  - `validation_command_default`
  - `validation_command_with_env_override`
  - `required_tables`
  - `required_table_fields`
  - `template_rejection_rules`
  - `acceptance_milestones`
  - `field_evidence_boundary`
- Agent61 报告和 deliverable 新增 R8p 现场行包操作交接区。
- `AgentArchitectureConsolidationAgent` 新增 `_r8p_pressure_resolution_operator_handoff()`，并在 Agent60 offline fallback 中透传 handoff status、validation command、默认真实行路径和模板路径。
- `deliverables/manifest.json` 新增 `latest_r8p_field_rows_operator_handoff_status`、`latest_r8p_field_rows_validation_command` 和 `latest_r8p_default_field_rows_path`。

当前输出：

- Agent61 operator handoff：
  - `field_rows_operator_handoff_status=field_rows_operator_handoff_ready_needs_source_package`
  - 默认真实行包路径：`outputs/pressure_resolution_replay_scenario_pack/pressure_resolution_replay_rows.json`
  - 模板路径：`outputs/pressure_resolution_replay_scenario_pack/pressure_resolution_replay_rows_template.json`
  - 验收命令：`.venv/bin/python experiments/run_agent61_pressure_resolution_replay_scenario_pack.py`
- Agent60 offline fallback：
  - `action_id=R8p_fix_field_rows_source_preflight`
  - `operator_handoff_status=field_rows_operator_handoff_ready_needs_source_package`
  - `validation_command=.venv/bin/python experiments/run_agent61_pressure_resolution_replay_scenario_pack.py`

验证：

- `.venv/bin/pytest -q tests/test_pressure_resolution_replay_scenario_pack_agent.py tests/test_agent_architecture_consolidation_agent.py`：51 passed。
- `.venv/bin/pytest -q`：399 passed。

边界：

- `field_rows_operator_handoff` 是现场数据接入合同，不是 field evidence。
- `pressure_resolution_replay_rows_template.json` 仍只是 scaffold；直接提交模板行会被拒绝。
- 即使真实行包通过 source/table/scenario 验收，仍必须进入 R8v、Agent51/49/52/R7 gate 和人工复核，不能写 actuator 或 release gate。

## 2026-06-03 R8u-6：Agent60 消费 R8p Field Rows Patch Plan

目标：

- 承接 R8u-5，让补包计划不只停留在 Agent61 报告中，而是回接 Agent60 架构治理 fallback。
- 不新增 agent；直接增强 Agent60 对 Agent61 metrics 的消费，减少“有补包计划但治理层仍泛化描述”的碎片。
- 让无真实包时的离线核心动作从 `R8p_collect_pressure_resolution_replay_rows` 精确到当前最高阻断项。

实现：

- `AgentArchitectureConsolidationAgent` 新增 `_r8p_pressure_resolution_patch_plan()`。
- 当 R8o scenario pack 已 ready、R8p rows 尚未 accepted，且 `field_rows_patch_plan_status` 存在并非 clear 时：
  - Agent60 fallback 改为 `field_rows_patch_plan.next_operator_action`。
  - 当前输出为 `R8p_fix_field_rows_source_preflight`。
  - `trigger_metric` 写入 patch plan status、patch item count 和 highest priority patch id。
  - fallback 边界明确 patch plan 不是 field evidence，不能写 actuator/release gate。

当前输出：

- Agent60 offline fallback：
  - `action_id=R8p_fix_field_rows_source_preflight`
  - `patch_plan_status=field_rows_patch_plan_blocked_at_source_preflight`
  - `patch_item_count=12`
  - `highest_priority_patch_id=R8P_SOURCE_MISSING_FIELD_ROWS_FILE`
- `deliverables/manifest.json` 的 `latest_offline_core_fallback_action` 已同步为 `R8p_fix_field_rows_source_preflight`。

验证：

- `.venv/bin/pytest -q tests/test_agent_architecture_consolidation_agent.py`：40 passed。
- `.venv/bin/pytest -q tests/test_agent_architecture_consolidation_agent.py tests/test_pressure_resolution_replay_scenario_pack_agent.py tests/test_deliverable_organization_agent.py`：76 passed。
- `.venv/bin/pytest -q`：398 passed。

边界：

- Agent60 只是把补包计划提升为下一步治理动作，不产生 field-supported 结论。
- 即使 source preflight 修复完成，仍要继续通过 R8p scenario acceptance、R8v 路由复核和 Agent51/49/52/R7 gate。

## 2026-06-03 R8u-5：R8p Field Rows Patch Plan

目标：

- 承接 R8u-4 source preflight，把“缺文件/缺表/缺场景行”进一步转成可执行补包计划。
- 不新增 Agent62，不改变证据升级规则；只增强 Agent61/R8p 的现场采集可操作性。
- 让真实行包进入系统前，现场人员能看到最高优先级 patch、目标表、必填字段、场景 blocker 和验收检查。

实现：

- `experiments/run_agent61_pressure_resolution_replay_scenario_pack.py` 新增 `_field_rows_patch_plan()`。
- 新增 `field_rows_patch_plan` 输出：
  - `field_rows_patch_plan_status`
  - `next_operator_action`
  - `patch_item_count`
  - `highest_priority_patch_id`
  - `patch_items`
- patch item 覆盖：
  - 缺真实行文件：`R8P_SOURCE_MISSING_FIELD_ROWS_FILE`
  - 缺表：`R8P_MISSING_TABLE_*`
  - 空表：`R8P_EMPTY_TABLE_*`
  - JSON shape 问题：`R8P_INVALID_SHAPE_*`
  - 未知表：`R8P_UNKNOWN_TABLE_*`
  - 场景验收未通过：`R8P_SCENARIO_ROWS_*`
- Agent61 deliverable、report、metrics 和 manifest 已写入 patch plan 状态。

当前输出：

- 默认真实行输入仍缺失：
  - `field_rows_source_status=field_rows_file_missing`
  - `field_rows_patch_plan_status=field_rows_patch_plan_blocked_at_source_preflight`
  - `highest_priority_patch_id=R8P_SOURCE_MISSING_FIELD_ROWS_FILE`
  - `patch_item_count=12`
- 这说明当前阻断已从“缺真实行”变成可执行补包动作：创建真实 field rows JSON，或通过 `PRESSURE_RESOLUTION_REPLAY_ROWS_PATH` 指向真实包，并补齐 6 张必需表。

验证：

- `.venv/bin/pytest -q tests/test_pressure_resolution_replay_scenario_pack_agent.py`：10 passed。
- `.venv/bin/pytest -q tests/test_pressure_resolution_replay_scenario_pack_agent.py tests/test_agent_architecture_consolidation_agent.py tests/test_deliverable_organization_agent.py`：75 passed。
- `.venv/bin/pytest -q`：397 passed。

边界：

- patch plan 是现场补包指导，不是 field evidence。
- 即使 patch plan 清空，也只表示 R8p 可进入 R8v 路由复核；仍不能直接写 actuator 或 release gate。
- template/TODO 行仍被拒绝，不能作为真实现场 replay 行。

## 2026-06-02 R8u-4：R8p Source Preflight 缺表/空表诊断

目标：

- 承接 R8u-2 source preflight，把“部分表缺失”和“行级验收失败”拆开。
- 让现场真实行包如果只包含部分表，可以直接看到缺哪张表，而不是等到场景验收阶段才被笼统阻断。
- 不新增 agent，只增强 Agent61 输入源诊断。

实现：

- `_read_field_rows_package()` 新增：
  - `missing_tables`
  - `empty_tables`
- 当真实行 JSON 只提供部分 expected tables 时：
  - `field_rows_source_status=field_rows_file_loaded_with_schema_gaps`
  - `preflight_blockers` 中写入 `<table>:missing_table`
- 缺文件、invalid JSON、root shape invalid 时，也会返回完整 expected table 缺口。
- Agent61 deliverable 已把 `missing_tables` 和 `empty_tables` 写入 Field Rows Source Preflight 区块。

当前输出：

- 默认真实输入仍缺失：
  - `field_rows_source_status=field_rows_file_missing`
  - `missing_tables=["agent52_replay_table","campaign_operation_log","fast_proxy_event_log","node_modality_sensor_timeseries","offline_lab_results","pressure_headloss_event_log"]`
  - `field_row_acceptance_status=no_field_replay_rows_supplied`
- Agent60 fallback 仍为 `R8p_collect_pressure_resolution_replay_rows`。

验证：

- `.venv/bin/pytest -q tests/test_pressure_resolution_replay_scenario_pack_agent.py`：8 passed。
- `.venv/bin/pytest -q tests/test_pressure_resolution_replay_scenario_pack_agent.py tests/test_agent_architecture_consolidation_agent.py tests/test_multi_facility_replay_evaluation_agent.py tests/test_multi_facility_collaborative_control_agent.py tests/test_field_package_coverage.py tests/test_real_field_replay_pipeline.py tests/test_catalyst_activity_proxy_agent.py`：96 passed。
- `.venv/bin/pytest -q`：395 passed。

边界：

- 缺表诊断只说明输入包结构是否完整，不代表任何现场 replay 结论。
- 即使所有表都存在，也必须继续通过 R8p 行级验收，才能推进到 R8v。
- 模板行仍不能作为 field evidence。

## 2026-06-02 R8u-3：R8p 独立真实行填报模板

目标：

- 在 R8u 行级验收门和 R8u-2 source preflight 之后，降低真实 pressure resolution replay 行采集摩擦。
- 生成一个独立的、可填写的 JSON 模板，但不放在默认真实输入路径，避免模板被误读为 field evidence。
- 保持系统边界：模板帮助采集，不升级证据，不触发 R8v。

实现：

- `experiments/run_agent61_pressure_resolution_replay_scenario_pack.py` 新增：
  - `TEMPLATE_ROWS_PATH = outputs/pressure_resolution_replay_scenario_pack/pressure_resolution_replay_rows_template.json`
  - 每次 Agent61 运行时，将 `template_rows_by_table` 写成独立 JSON 模板。
- `generated_files`、Agent61 report、deliverable 和 manifest 新增模板文件路径：
  - `pressure_resolution_replay_rows_template`
  - `latest_r8p_pressure_resolution_replay_rows_template`
- 当前模板内容：
  - 6 张表：`node_modality_sensor_timeseries`、`pressure_headloss_event_log`、`campaign_operation_log`、`offline_lab_results`、`fast_proxy_event_log`、`agent52_replay_table`
  - 每张表 5 行，共 30 行。
  - 每行均带 `template_only=True` 和 `evidence_status=template_not_field_evidence`。

当前输出：

- 独立模板文件已生成：
  - `outputs/pressure_resolution_replay_scenario_pack/pressure_resolution_replay_rows_template.json`
- 默认真实输入仍缺失：
  - `field_rows_source_status=field_rows_file_missing`
  - `field_row_acceptance_status=no_field_replay_rows_supplied`
- Agent60 fallback 仍保持：
  - `R8p_collect_pressure_resolution_replay_rows`

验证：

- `.venv/bin/pytest -q tests/test_pressure_resolution_replay_scenario_pack_agent.py`：7 passed。
- `.venv/bin/pytest -q tests/test_pressure_resolution_replay_scenario_pack_agent.py tests/test_agent_architecture_consolidation_agent.py tests/test_multi_facility_replay_evaluation_agent.py tests/test_multi_facility_collaborative_control_agent.py tests/test_field_package_coverage.py tests/test_real_field_replay_pipeline.py tests/test_catalyst_activity_proxy_agent.py`：95 passed。
- `.venv/bin/pytest -q`：394 passed。

边界：

- 模板文件不是 field evidence。
- 不能直接把 `pressure_resolution_replay_rows_template.json` 当作真实输入；必须复制/转写为真实行、替换 TODO/template 字段，并放入 `pressure_resolution_replay_rows.json` 或通过 `PRESSURE_RESOLUTION_REPLAY_ROWS_PATH` 指向。
- 即使真实行文件存在，也必须通过 R8p 行级验收；验收不通过不能升级到 R8v。

## 2026-06-02 R8u-2：R8p 真实行包 Source Preflight

目标：

- 承接 R8u 行级验收门，把“没有真实行”进一步拆清楚：到底是默认路径缺失、JSON 结构错误、表结构错误、行结构错误，还是有真实行但验收失败。
- 不新增 agent，不改变控制策略；只增强 Agent61 的输入证据边界，让现场数据进入 R8p 前有工程级 preflight。
- 防止现场实际使用时，因为路径错或 JSON 根结构错，被系统静默解释为“没有数据”。

实现：

- `experiments/run_agent61_pressure_resolution_replay_scenario_pack.py` 新增 `_read_field_rows_package()`：
  - 默认读取 `outputs/pressure_resolution_replay_scenario_pack/pressure_resolution_replay_rows.json`。
  - 可通过 `PRESSURE_RESOLUTION_REPLAY_ROWS_PATH` 指向外部真实行包。
  - 缺文件时输出 `field_rows_source_status=field_rows_file_missing`。
  - JSON 无效时输出 `field_rows_file_invalid_json`。
  - 根结构不是 object 时输出 `field_rows_file_invalid_shape`。
  - 表不是 list 或行不是 object 时输出 `field_rows_file_loaded_with_shape_warnings` 和 `invalid_table_shapes`。
  - 出现未知表时输出 `unknown_tables`。
- Agent61 metrics 新增 `field_rows_source`：
  - `field_rows_source_path`
  - `field_rows_source`
  - `expected_tables`
  - `field_rows_source_status`
  - `table_count`
  - `row_count`
  - `table_summaries`
  - `invalid_table_shapes`
  - `unknown_tables`
  - `preflight_blockers`
- Agent61 report、deliverable 和 manifest 已写入：
  - `latest_r8p_field_rows_source_status`
  - `latest_r8p_field_rows_source_path`

当前输出：

- 当前默认路径不存在，因此：
  - `field_rows_source_status=field_rows_file_missing`
  - `field_row_acceptance_status=no_field_replay_rows_supplied`
  - `accepted_field_scenario_count=0`
  - `latest_offline_core_fallback_action=R8p_collect_pressure_resolution_replay_rows`
- 这说明当前阻断是未提供真实行包，而不是已有行包被验收失败。

验证：

- `.venv/bin/pytest -q tests/test_pressure_resolution_replay_scenario_pack_agent.py`：7 passed。
- `.venv/bin/pytest -q tests/test_pressure_resolution_replay_scenario_pack_agent.py tests/test_agent_architecture_consolidation_agent.py tests/test_multi_facility_replay_evaluation_agent.py tests/test_multi_facility_collaborative_control_agent.py tests/test_field_package_coverage.py tests/test_real_field_replay_pipeline.py tests/test_catalyst_activity_proxy_agent.py`：95 passed。
- `.venv/bin/pytest -q`：394 passed。

边界：

- Source preflight 只证明输入文件是否可被读取成 table-to-rows object，不能单独构成 field evidence。
- 即使 source preflight 为 loaded，也必须继续通过 Agent61 的行级验收门；只有 5 个场景真实行全通过，才允许推进到 R8v。
- 任何 template/TODO/synthetic 行仍会被行级验收拒绝。

## 2026-06-02 R8u：R8p pressure resolution 真实行验收门

目标：

- 承接全局 goal 中“先保证可验证，再讨论智能化”的原则，把 R8p 从行级采集计划推进为可机读验收门。
- 不新增 Agent62，不扩展展示层；直接增强 Agent61，让真实行进入前先被检查为非模板、跨表对齐、具备 reviewer/calibration/action 链，并保留 actuator/release gate 阻断。
- 让 Agent60 在 R8p 真实行验收通过时自动推进到 R8v，而不是永远停在“继续采集行”。

实现：

- `PressureResolutionReplayScenarioPackAgent` 新增可选输入 `field_replay_rows_by_table`：
  - 实验脚本可通过 `PRESSURE_RESOLUTION_REPLAY_ROWS_PATH` 指向真实行 JSON。
  - 未设置时默认读取 `outputs/pressure_resolution_replay_scenario_pack/pressure_resolution_replay_rows.json`；文件不存在时保持无真实行。
- Agent61 新增 `field_row_acceptance`：
  - `field_row_acceptance_status`
  - `supplied_field_row_count`
  - `accepted_field_row_count`
  - `rejected_field_row_count`
  - `accepted_scenario_count`
  - `accepted_batch_count`
  - `accepted_batches_by_scenario`
  - `scenario_acceptance`
- 行级验收要求：
  - 行不能带 `template_only=True`，不能是 `evidence_status=template_not_field_evidence`，不能含 TODO/template/null。
  - 每个场景必须有同 batch 的 `node_modality_sensor_timeseries`、`pressure_headloss_event_log`、`campaign_operation_log`、`offline_lab_results`、`fast_proxy_event_log` 和 `agent52_replay_table`。
  - `agent52_replay_table.data_origin` 必须是真实 field origin，不能是 synthetic/template/TODO。
  - unresolved conflict 场景必须保留 operator review required 和 replay block。
  - resolved/scoreability/clearance 场景必须具备 authoritative pressure source、resolution record，并且 clearance 场景不能仍处于 control block。
  - operator review latency 场景必须具备 review_time 和 hold_time_min。
- Agent61 readiness 新增：
  - `field_row_acceptance_status`
  - `accepted_field_scenario_count`
  - `accepted_field_row_count`
  - `accepted_field_batch_count`
  - 当 5 个场景全部通过且 source chain ready 时，`next_recommended_core_action` 变为 `R8v_route_pressure_resolution_rows_to_field_replay_and_holdout_gates`。
- Agent60 新增 `_r8p_pressure_resolution_rows_accepted()`：
  - 只有 `scenario_pack_status=pressure_resolution_scenario_pack_field_replay_ready_for_human_review`、`field_scenario_coverage=1.000`、`field_row_acceptance_status=field_replay_rows_accepted_for_all_scenarios` 且 `accepted_scenario_count>=5` 时，才把离线 fallback 推进到 R8v。
  - R8v 的边界仍是不能写 actuator 或 release gate，必须先进入 Agent51 holdout、Agent49 control context、Agent52 replay clearance 和 R7 evidence chain。

当前输出：

- 当前没有真实行包，因此 Agent61 输出：
  - `field_row_acceptance_status=no_field_replay_rows_supplied`
  - `accepted_field_scenario_count=0`
  - `accepted_field_batch_count=0`
  - `field_scenario_coverage=0.000`
  - `next_recommended_core_action=R8p_collect_pressure_resolution_replay_rows`
- Agent60 当前仍保持：
  - 主任务：`R7a_import_real_field_package_with_metadata_and_csv`
  - 无真实包 fallback：`R8p_collect_pressure_resolution_replay_rows`

验证：

- `.venv/bin/pytest -q tests/test_pressure_resolution_replay_scenario_pack_agent.py`：4 passed。
- `.venv/bin/pytest -q tests/test_pressure_resolution_replay_scenario_pack_agent.py tests/test_agent_architecture_consolidation_agent.py`：43 passed。
- `.venv/bin/pytest -q tests/test_pressure_resolution_replay_scenario_pack_agent.py tests/test_agent_architecture_consolidation_agent.py tests/test_multi_facility_replay_evaluation_agent.py tests/test_multi_facility_collaborative_control_agent.py tests/test_field_package_coverage.py tests/test_real_field_replay_pipeline.py tests/test_catalyst_activity_proxy_agent.py`：92 passed。
- `.venv/bin/pytest -q`：391 passed。

边界：

- R8u 只证明真实行进入前有验收门；当前没有真实行，所以不产生 field-supported 结论。
- 即使未来 R8p 行级验收通过，也只会推进到 R8v field replay/holdout gate，不会直接写执行器或 release gate。
- 模板行、TODO 行、synthetic 行、缺 batch join 的行都会被拒绝，不能升级为现场证据。

## 2026-06-02 R8t：模块接口契约矩阵接入 Agent60

目标：

- 承接全局 goal 中“先定义接口，再扩展功能”的第一性原理，把它从文本原则转成 Agent60 的可计算审计指标。
- 不新增 agent，不重开治理分支，直接增强 Agent60，避免 agent 链条继续变碎。
- 让每个模块不仅有名称、角色和层级映射，还必须说明输入、输出、状态变量、证据来源、可传递指标、不能做什么、上游依赖、下游消费者和现场验证需求。

实现：

- `AgentArchitectureConsolidationAgent` 新增 `REQUIRED_MODULE_INTERFACE_FIELDS`，固定 9 类接口必填字段：
  - `input_contract`
  - `output_contract`
  - `state_variables`
  - `evidence_sources`
  - `transferable_metrics`
  - `cannot_do`
  - `upstream_dependencies`
  - `downstream_consumers`
  - `field_validation_need`
- 新增 `MODULE_INTERFACE_CONTRACTS`：
  - M1 稀疏观测明确输出 node-modality 矩阵、弱状态覆盖和软传感输入先验。
  - M2 软传感明确输出隐藏状态估计、预测区间、OOD/abstention 和 release 前不确定性边界。
  - M3 灰箱机理明确输出灰箱残差、机理假设、故障模式和控制约束。
  - M4 协同控制明确输出联合动作候选、保护性阻断、策略解释和不可写执行器边界。
  - M5 KG/claim evidence 明确输出 typed KG edge、evidence path、claim constraint 和 source_basis detail。
  - M6 field evidence chain 明确区分 real field package、timestamped replay、claim gate 和 header/template 阻断。
  - M7 项目运行支持明确只能支撑工程实施，不能替代模型核心链路。
  - M8 治理层明确只能排序、阻断、冻结和复盘，不能替代模型能力或现场验证。
  - M9 展示层明确不能改变模型结论，不能制造 field-supported claim。
- Agent60 metrics 新增：
  - `module_interface_contracts`
  - `interface_contract_coverage`
- 当前输出：
  - `interface_contract_status=all_module_interface_contracts_complete`
  - `module_contract_count=9`
  - `complete_module_contract_count=9`
  - `interface_contract_coverage_rate=1.000`
  - `incomplete_module_contracts=[]`
- `experiments/run_agent60_agent_architecture_consolidation.py` 已把接口契约覆盖率写入 Agent60 报告、deliverable 和 manifest。
- `deliverables/manifest.json` 新增：
  - `latest_module_interface_contract_status`
  - `latest_module_interface_contract_coverage_rate`

验证：

- `.venv/bin/pytest -q tests/test_agent_architecture_consolidation_agent.py`：38 passed。
- `.venv/bin/pytest -q tests/test_agent_architecture_consolidation_agent.py tests/test_deliverable_organization_agent.py`：64 passed。
- `.venv/bin/pytest -q`：388 passed。

边界：

- 接口契约覆盖率 1.000 说明模块的输入/输出/状态/证据/边界已可审计，不说明现场数据已完成。
- M6 仍明确阻断 header-only/template package 伪装成 field evidence。
- M4 仍明确无真实多节点 replay 和人工复核门时不能写执行器或 release gate。
- 下一步仍保持主线：最高证据价值任务是 `R7a_import_real_field_package_with_metadata_and_csv`；没有真实包时，离线核心 fallback 仍是 `R8p_collect_pressure_resolution_replay_rows`。

## 2026-06-02 R8s：全局七层骨架接入 Agent60 架构复盘

目标：

- 让全局 goal 不只停留在 `model_core_goal.md` 文本里，而是进入可计算的架构治理指标。
- 不新增 agent，直接扩展已有 Agent60，符合“agent 不是越多越好；优先合并、抽象、复用、回接主链”的原则。
- 把九个模块投影到全局七层系统骨架和六类系统能力，检查当前模型是否真正服务“低成本受限观测下的循环式水处理灰箱闭环系统”。

实现：

- `AgentArchitectureConsolidationAgent` 新增全局系统骨架常量：
  - 七层：现场对象层、观测层、状态估计层、机理证据层、诊断决策层、闭环执行层、验证治理层。
  - 六类能力：可观测、可控、可解释、可验证、可工程化、可演化。
- 新增 `MODULE_SYSTEM_SPINE_MAP`：
  - 将 M1-M8 映射到七层骨架中的 primary/secondary layer 和 core abilities。
  - 将 M9 presentation 明确标为 `OUTSIDE_MODEL_SPINE`，策略为 `freeze_outside_model_spine`。
- Agent60 metrics 新增：
  - `system_spine_map`
  - `system_layer_board`
  - `system_spine_coverage`
- 当前输出：
  - `system_spine_status=global_system_spine_mapped_with_frozen_expression_layer`
  - `layer_coverage_rate=1.000`
  - `ability_coverage_rate=1.000`
  - `outside_model_spine_modules=["M9_presentation_delivery"]`
  - `unmapped_system_layer_module_count=0`
- `experiments/run_agent60_agent_architecture_consolidation.py` 已把七层骨架覆盖写入 Agent60 报告、deliverable 和 manifest。

验证：

- `experiments/run_agent60_agent_architecture_consolidation.py` 已刷新。
- `experiments/run_agent31_deliverable_organization.py` 已刷新，`artifact_index.md` 现在收录 `goal_iteration_trace.md`，P13 角色名更新为全局系统架构治理与模型核心优化。
- `.venv/bin/pytest -q tests/test_agent_architecture_consolidation_agent.py`：37 passed。
- `.venv/bin/pytest -q tests/test_agent_architecture_consolidation_agent.py tests/test_deliverable_organization_agent.py`：63 passed。
- `.venv/bin/pytest -q`：387 passed。

边界：

- 七层覆盖率 1.000 说明当前模块能映射到全局骨架，不说明现场数据已完成。
- M9 被标记为骨架外冻结，不代表删除展示材料，只代表展示不作为模型核心能力。
- 下一步仍应优先让骨架内模块的接口、证据链、replay 和 field validation 更真实、更短、更稳。

## 2026-06-02 R8r：Goal 十轮迭代，升级为全局系统总纲

目标：

- 回应新的架构要求：goal 不应过分强调现在，也不应绑定某个阶段、某个 agent 编号、某个当前问题或某次展示材料。
- 基于用户给出的文案做十轮抽象和去阶段化，把 goal 从“当前核心工作的执行约束”升级为“低成本传感循环式水处理智能灰箱闭环系统”的全局系统总纲。
- 让细节和现阶段任务成为系统演化中的自然产物，而不是 goal 的中心。

实现：

- `deliverables/model_core_optimization/model_core_goal.md` 已升级为“全局 Goal：低成本传感循环式水处理智能灰箱闭环系统”：
  - 系统使命明确为：高效形成一个能解释真实污染场景、能在低成本受限观测下行动、能被现场数据校准、能被证据链审查、能逐步工程化落地的系统架构。
  - 新增去阶段化说明：阶段任务、具体模块、代码细节、文档和实验只是系统演化中的自然产物。
  - 新增五条第一性原理：先搭骨架、先看闭环、先定义接口、先保证验证、先追求可演化。
  - 新增七层系统骨架：现场对象层、观测层、状态估计层、机理证据层、诊断决策层、闭环执行层、验证治理层。
  - 新增六类架构能力：可观测性、可控性、可解释性、可验证性、可工程化、可演化性。
  - 新增系统设计不变量：控制建议必须可追溯，现场结论必须通过真实数据/回放/人工复核，新增复杂度必须换来接口、证据、控制或验证收益。
  - 新增架构师式执行五问：属于哪一层、增强哪种能力、改变什么接口/状态/证据/验证门、是否减少碎片、让主链更清楚还是更混乱。
- 新增 `deliverables/model_core_optimization/goal_iteration_trace.md`：
  - 记录十轮收敛：去阶段化、定使命、定主链、定对象、定层级、定能力、定接口、定证据、定演化、定执行。
- `deliverables/model_core_optimization/execution_prompt.md` 已同步为宏观架构执行 prompt，要求每次实现前先做层级和能力映射。
- `experiments/run_agent50_model_core_governance.py` 的生成模板已同步，避免下次 Agent50 重跑时覆盖回旧版本。
- `ModelCoreOptimizationGovernanceAgent` 的 `governance_principles` 已同步为更全局的宏观架构原则、边际价值原则和架构收敛原则，不再把当前 agent 锚点作为治理原则中心。

验证：

- `experiments/run_agent50_model_core_governance.py` 已重新生成治理包。
- `.venv/bin/pytest -q tests/test_model_core_optimization_governance_agent.py`：19 passed。
- `.venv/bin/pytest -q tests/test_model_core_optimization_governance_agent.py tests/test_deliverable_organization_agent.py`：45 passed。
- `.venv/bin/pytest -q`：386 passed。

边界：

- 这不是暂停模型细节优化，而是给细节优化加架构准星。
- 后续新增 agent、字段、scenario、replay 或文档前，都应先说明它属于七层骨架哪一层，增强哪种系统能力，以及是否能减少系统碎片。
- goal 本身只承担长期系统方向，不承担现阶段任务清单；具体任务应自然服从它。

## 2026-06-02 R8p：pressure resolution 从场景包推进到行级采集计划

目标：

- 承接 Agent60 的离线 fallback `R8p_collect_pressure_resolution_replay_rows`，把“采集真实 replay 行”拆成现场可执行的行级合同。
- 让每个 pressure resolution 场景都明确 batch role、必需表、非空字段、跨表 join key、Agent52 replay 字段和模板边界。
- 防止 TODO/template 行被误当作 field evidence。

实现：

- `PressureResolutionReplayScenarioPackAgent` 新增 `row_collection_readiness`：
  - `row_collection_plan_status=row_collection_plan_ready_needs_real_rows`
  - `missing_scenario_count=5`
  - `minimum_real_batch_count=5`
  - `template_row_count=30`
- `row_collection_plan` 现在为 5 个 R8p bundle 输出：
  - unresolved pressure conflict review block。
  - resolved authoritative pressure source。
  - operator review latency budget。
  - Agent51 scoreability recovery after resolution。
  - Agent49/52 pressure guardrail clearance replay。
- `template_rows_by_table` 覆盖 `node_modality_sensor_timeseries`、`pressure_headloss_event_log`、`campaign_operation_log`、`offline_lab_results`、`fast_proxy_event_log` 和 `agent52_replay_table`。
- 所有模板行新增 `template_only=True`、`evidence_status=template_not_field_evidence`、`source_stage=field_validation_required`；Agent52 replay 模板的 `data_origin` 为 `TODO_FIELD_REPLAY_NOT_EVIDENCE`。
- Agent61 实验脚本现在把 `row_collection_plan`、`template_rows_by_table`、`row_collection_readiness` 写入 metrics、Markdown deliverable 和 manifest。

验证：

- `.venv/bin/pytest -q tests/test_pressure_resolution_replay_scenario_pack_agent.py`：2 passed。
- `experiments/run_agent61_pressure_resolution_replay_scenario_pack.py` 已刷新：R8p 行级采集计划状态为 `row_collection_plan_ready_needs_real_rows`。
- `experiments/run_agent60_agent_architecture_consolidation.py` 已刷新：无真实包 fallback 仍为 `R8p_collect_pressure_resolution_replay_rows`。
- `.venv/bin/pytest -q tests/test_pressure_resolution_replay_scenario_pack_agent.py tests/test_agent_architecture_consolidation_agent.py tests/test_multi_facility_replay_evaluation_agent.py tests/test_multi_facility_collaborative_control_agent.py tests/test_field_package_coverage.py tests/test_real_field_replay_pipeline.py tests/test_catalyst_activity_proxy_agent.py`：87 passed。
- `.venv/bin/pytest -q`：386 passed。

边界：

- R8p 只生成采集合同和 TODO 模板，不生成真实 field evidence。
- 当前 field_scenario_coverage 仍为 0.000；必须补入真实 reviewer/calibration/action/replay 行后，才可能进入 field-supported human review。
- 即使未来 R8p 行补齐，仍不能自动写 actuator 或 release gate，需要继续通过 Agent49/52 和人工复核门。

## 2026-06-02 R8q：自我打断二次节流，从 verdict 闸门升级为治理复盘准入门

目标：

- 回应新的效率问题：即使 `self_interrupt_verdict=continue_core_work`，如果每个新想法都触发 Agent50/60 级别的长上下文复盘，仍会增加算力摩擦和工作切换成本。
- 把自我打断从“模仿用户打断”改成真正的项目治理阀门：硬风险立即中断，阶段边界集中复盘，普通新想法延迟记录。

实现：

- `ModelCoreOptimizationGovernanceAgent` 新增 `governance_review_gate`：
  - `continue_current_micro_loop`：无硬风险、未到阶段边界时继续当前小闭环，不建议重跑治理。
  - `run_stage_review`：当前小闭环完成或显式进入阶段边界时，才允许集中重排。
  - `defer_review_due_to_budget`：阶段边界存在但治理复盘预算耗尽时，除硬风险外继续当前核心路径。
  - `interrupt_and_refocus_now`：展示漂移、硬性证据矛盾、synthetic/template 写成 field 结论、绕过 field replay/guardrail 时立即中断。
- `self_interrupt_mode` 更新为 `stage_gate_throttled_hard_gate_with_deferred_backlog`。
- Agent50 生成的 `model_core_goal.md`、`user_interrupt_lessons.md`、`self_interrupt_checklist.md`、`governance_report.md` 和 `priority_ranking.json` 已同步新规则。
- 当前 Agent50 输出：`self_interrupt_verdict=continue_core_work`，`governance_review_gate=continue_current_micro_loop`，`governance_rerun_recommended=False`。

验证：

- `.venv/bin/pytest -q tests/test_model_core_optimization_governance_agent.py`：19 passed。
- `.venv/bin/pytest -q tests/test_model_core_optimization_governance_agent.py tests/test_deliverable_organization_agent.py`：45 passed。
- `.venv/bin/pytest -q`：386 passed。
- `experiments/run_agent50_model_core_governance.py` 已重新生成治理包。

边界：

- 这不是取消复盘，而是限制复盘触发条件。后续只有完成当前可验证小闭环、进入阶段边界或出现硬风险时，才重跑 Agent50/60；普通思路先沉淀，不打断模型实现。

## 2026-06-02 R8o/R8p：pressure resolution replay 场景包落地，下一步推进真实行采集

目标：

- 把 Agent60 的 `R8o_pressure_resolution_field_replay_scenario_pack` 从一句 fallback 推荐落成可执行模型接口。
- 让 pressure source conflict resolution 不只停留在字段层，而是形成真实 replay 场景采集包，覆盖未解决冲突、已解决冲突、人工复核延迟、Agent51 可评分恢复和 Agent49/52 guardrail clearance。
- 如果 R8o schema 已经 ready，Agent60 不再继续显示 R8o，而是推进到 `R8p_collect_pressure_resolution_replay_rows`。

实现：

- 新增 `PressureResolutionReplayScenarioPackAgent`：
  - 定义 5 个 R8o 场景：unresolved conflict review block、resolved authoritative source、operator review latency budget、Agent51 scoreability recovery、Agent49/52 guardrail clearance replay。
  - 输出 `required_table_field_matrix`，强制连接 `node_modality_sensor_timeseries`、`pressure_headloss_event_log`、`campaign_operation_log`、`offline_lab_results`、`fast_proxy_event_log`。
  - 输出 `pressure_resolution_replay_scenario_matrix`、`field_scenario_coverage`、`source_chain_resolution_fields_ready` 和 `agent60_writeback`。
  - 保持边界：场景包不写 actuator，不写 release gate，真实 replay 行缺失时不能升级 field-supported claim。
- 新增 `experiments/run_agent61_pressure_resolution_replay_scenario_pack.py`：
  - 读取 R7、Agent51、Agent49、Agent52 输出。
  - 生成 `outputs/pressure_resolution_replay_scenario_pack/pressure_resolution_replay_scenario_pack_metrics.json`。
  - 生成 `deliverables/model_core_optimization/pressure_resolution_replay_scenario_pack.md`。
- Agent60 已读取 R8o metrics：
  - `pressure_resolution_replay_scenario_pack_agent` 映射到 `M6_field_evidence_chain`。
  - 当 R8o schema ready 且 source chain fields ready 时，离线 fallback 推进到 `R8p_collect_pressure_resolution_replay_rows`。

验证：

- `.venv/bin/pytest -q tests/test_pressure_resolution_replay_scenario_pack_agent.py tests/test_agent_architecture_consolidation_agent.py`：38 passed。
- `.venv/bin/pytest -q tests/test_pressure_resolution_replay_scenario_pack_agent.py tests/test_agent_architecture_consolidation_agent.py tests/test_multi_facility_replay_evaluation_agent.py tests/test_multi_facility_collaborative_control_agent.py tests/test_field_package_coverage.py tests/test_real_field_replay_pipeline.py tests/test_catalyst_activity_proxy_agent.py`：87 passed。
- `.venv/bin/pytest -q`：383 passed。
- `experiments/run_agent61_pressure_resolution_replay_scenario_pack.py`：`scenario_pack_status=pressure_resolution_scenario_pack_ready_needs_real_replay_rows`，`schema=1.000`，`field=0.000`。
- `experiments/run_agent60_agent_architecture_consolidation.py`：无真实包 fallback 已推进到 `R8p_collect_pressure_resolution_replay_rows`。

边界：

- 当前 R8o field_scenario_coverage 仍为 0.000，因为没有真实 resolved/unresolved pressure conflict replay 行。
- 不能把场景包 schema ready 当成现场校准完成；下一步必须采集 batch-level reviewer/calibration/action/replay 行。

## 2026-06-02 R8o：pressure resolution 解除门进入 Agent52 replay，并让 Agent60 跳出旧 R8m fallback

目标：

- 承接第一性原理中的“证据门控”和“多设施协同控制可验证性”：压力/水头损失双源冲突不能只在 Agent49 控制上下文里解除，还必须进入 Agent52 离线 replay 晋级门。
- 修正架构复盘的边际价值排序：R8m/R8n 已具备代码与测试能力后，Agent60 不应继续把离线 fallback 停在“生成 pressure conflict patch item”，而应推进到真实 replay 场景采集包。

实现：

- Agent52 `REPLAY_REQUIRED_FIELDS`、`replay_table`、`offline_evaluation_metrics`、`readiness`、`pressure_headloss_context` 和 `agent49_writeback.metric_patch` 新增：
  - `resolved_pressure_source_conflict_count`
  - `unresolved_pressure_source_conflict_count`
  - `pressure_source_resolution_record_count`
- Agent52 现在明确区分：
  - 原始 pressure conflict 存在但已由 operator review / calibration resolution 解决。
  - unresolved conflict 仍需要 operator review，并继续阻断 Agent49 promotion。
- Agent60 新增 `R8n_pressure_resolution_replay_clearance_ready` 识别：只有 R7、Agent49、Agent52、writeback 都具备 resolved/unresolved/resolution 字段，才认为 R8n 解除门进入主链。
- 当 R8n ready 后，Agent60 无真实包离线 fallback 推进为 `R8o_pressure_resolution_field_replay_scenario_pack`，要求下一步采集 resolved/unresolved pressure conflict 的真实 replay 场景。

验证：

- `.venv/bin/pytest -q tests/test_multi_facility_replay_evaluation_agent.py`：10 passed。
- `.venv/bin/pytest -q tests/test_agent_architecture_consolidation_agent.py`：35 passed。
- `.venv/bin/pytest -q tests/test_field_package_coverage.py tests/test_catalyst_activity_proxy_agent.py tests/test_real_field_replay_pipeline.py tests/test_agent_architecture_consolidation_agent.py tests/test_multi_facility_collaborative_control_agent.py tests/test_multi_facility_replay_evaluation_agent.py tests/test_model_core_optimization_governance_agent.py`：100 passed。
- `.venv/bin/pytest -q`：380 passed。
- `experiments/run_agent52_multi_facility_replay_evaluation.py` 已刷新 replay metrics。
- `experiments/run_agent60_agent_architecture_consolidation.py` 已刷新 fallback：`R8o_pressure_resolution_field_replay_scenario_pack`。

边界：

- 当前 template 仍没有真实 resolved/unresolved conflict batch；`0/0/0` 只能证明 schema 和代码路径可运行。
- 不能把 `pressure_source_conflict_resolution_clear` 的 template 状态写成现场已校准；R8o 要求真实 reviewer/calibration/action/replay 行。

## 2026-06-02 R8n：自我打断降摩擦，从三档 verdict 改成两态硬闸门

目标：

- 回应新的治理问题：自我打断不能模仿用户的高频纠偏，也不能让普通新想法反复触发上下文重算。
- 保留必要纠偏能力，但把它限制在高阈值场景：展示/整理漂移且无模型指标变化、硬性证据矛盾、绕过 field replay/保护边界。
- 普通复盘项、新想法和可能更高边际价值的问题，只沉淀到阶段边界 backlog，不改变当前小闭环的执行 verdict。
- 按新的低摩擦原则，治理修正后不再发散新分支，继续补完当前核心小闭环：pressure source conflict resolution 必须能被 Agent49 控制侧消费。

实现：

- `ModelCoreOptimizationGovernanceAgent` 的 `self_interrupt_verdict` 从三档收缩为两态：
  - `continue_core_work`
  - `interrupt_and_refocus`
- 原 `defer_refocus_until_stage_boundary` 不再作为 verdict 或 issue 出现。
- 新增 `stage_boundary_deferred_backlog`、`stage_boundary_deferred_count` 和 `self_interrupt_mode=two_state_hard_gate_with_stage_boundary_backlog`。
- 治理文档、Agent50 自动生成 checklist、user interrupt lessons、current_status 和项目概览已同步为“普通新想法只进 backlog，不触发打断”。
- Agent49 `control_replay_guardrail_context` 已新增 `resolved_pressure_source_conflict_count`、`unresolved_pressure_source_conflict_count`、`pressure_source_resolution_record_count`、`unresolved_pressure_source_conflicts` 和 `pressure_source_resolutions`。
- 新增 Agent49 resolved conflict 测试：同一 batch 有 pressure conflict，但已有完整 operator review / calibration resolution 时，`field_proxy_labels_ready=True`、`pressure_source_conflict_control_block=False`，不再触发 `pressure_source_conflict_blocks_control_relaxation` issue。

验证：

- `.venv/bin/pytest -q tests/test_model_core_optimization_governance_agent.py`：16 passed。
- `.venv/bin/pytest -q tests/test_multi_facility_collaborative_control_agent.py`：10 passed。
- `.venv/bin/pytest -q tests/test_field_package_coverage.py tests/test_catalyst_activity_proxy_agent.py tests/test_real_field_replay_pipeline.py tests/test_agent_architecture_consolidation_agent.py tests/test_multi_facility_collaborative_control_agent.py tests/test_multi_facility_replay_evaluation_agent.py tests/test_model_core_optimization_governance_agent.py`：98 passed。
- `.venv/bin/pytest -q`：378 passed。
- `experiments/run_agent50_model_core_governance.py` 已重新生成治理包，当前 `self_interrupt_verdict=continue_core_work`。
- `experiments/run_agent49_multi_facility_collaborative_control.py`、`experiments/run_agent52_multi_facility_replay_evaluation.py` 和 `experiments/run_agent60_agent_architecture_consolidation.py` 已重跑；当前 template 无真实 conflict/resolution row，因此输出为 0/0/0，但字段已存在。

边界：

- 这不是取消自我打断，而是把它降为低频硬闸门。
- stage backlog 只用于阶段边界统一复盘，不得在当前实现小闭环中反复重排优先级。

## 2026-06-02 R8m：pressure conflict 转成现场校准补包，并把自我打断改成阶段边界执行

目标：

- 回应新的治理问题：自我打断不能模仿用户的高频打断，否则会让模型优化被频繁切换、上下文重算和机制重写拖慢。
- 继续推进当前最高离线核心 fallback：把 R8k/R8l 已识别并传递到控制 replay 的 pressure source conflict，落到 R7 field package coverage 的可执行补包/校准任务。

实现：

- 低摩擦执行方式：
  - 未新增大型 agent，也未重开治理分支；直接在 R7 coverage、R7 pipeline readiness 和 Agent60 复盘入口中补齐 R8m。
  - 本轮当时把自我打断收敛为低摩擦阶段边界机制；后续 R8n 已进一步把它收缩为两态硬闸门，普通新想法只进入 `stage_boundary_deferred_backlog`。
- R8m field package coverage：
  - `field_package_coverage.py` 现在会比较 `node_modality_sensor_timeseries` 中 `N3_catalyst_bed:pressure_drop_kPa` 与 `pressure_headloss_event_log.pressure_drop_kPa` 的同 batch 压降。
  - 冲突容差为 `max(1.0 kPa, 0.25 * max(abs(node), abs(event)))`。
  - 超过容差时，readiness 输出 `pressure_source_conflict_count`、`pressure_source_conflict_requires_operator_review`、`field_package_pressure_conflict_resolution_status=pressure_source_conflicts_require_field_patch` 和 `field_package_pressure_conflict_resolution_ready=False`。
  - patch plan 生成 `R8M_PRESSURE_SOURCE_CONFLICT_FIELD_PATCH`，要求现场复核 `node_modality_sensor_timeseries`、`pressure_headloss_event_log` 与 `campaign_operation_log`，补入 `pressure_source_resolution`、`authoritative_pressure_source`、`reviewer_id`、`review_time`、`calibration_action_id` 和 `calibration_note`。
  - 只要冲突未解，R7j Agent51 field proxy holdout coverage 不通过；后续必须重跑 R7 pipeline、Agent51 holdout 和 Agent49/52 replay。
- R7 pipeline：
  - `pipeline_readiness` 新增 pressure conflict 与 conflict resolution 字段。
  - 报告和 deliverable 会显示 `pressure_source_conflict_count`、`operator_review`、`resolution_status` 和 `resolution_ready`。
- Agent60：
  - R7 主线 action 现在能识别 `patch_plan_requires_pressure_source_conflict_resolution`，并直接提升为 `R8m_pressure_source_conflict_field_patch_requirements`。
  - 无真实包时，template 没有 conflict batch，离线 fallback 仍显示 R8m；这不代表 R8m 未实现，而是说明当前没有真实冲突行可生成补丁项。

验证：

- 定向测试：
  - `.venv/bin/pytest -q tests/test_field_package_coverage.py tests/test_real_field_replay_pipeline.py tests/test_agent_architecture_consolidation_agent.py tests/test_catalyst_activity_proxy_agent.py`：61 passed。
- 实验脚本：
  - `experiments/run_r7_real_field_replay_pipeline.py`：仍为 `real_field_package_acceptance_blocked_at_import`；当前 template 下 `pressure_source_conflict_count=0`、`field_package_pressure_conflict_resolution_status=pressure_source_conflict_resolution_clear`，不代表真实现场无冲突。
  - `experiments/run_agent60_agent_architecture_consolidation.py`：主任务仍为 `R7a_import_real_field_package_with_metadata_and_csv`；无真实包 fallback 仍为 `R8m_pressure_source_conflict_field_patch_requirements`。
- 完整回归：
  - `.venv/bin/pytest -q`：375 passed。

结论：

- R8m 把“冲突识别”推进到“现场要怎么补证据、怎么校准、怎么解除保护”的工程动作层。
- 自我打断结构已进一步节流：只有阶段边界和高阈值证据冲突才改变主线；普通优化想法不再频繁打断当前实现闭环。
- 当前仍缺真实现场数据；所有 conflict clear 只代表 header/template 没有冲突行，不是现场一致性的实证结论。

## 2026-06-02 R8l + 低摩擦自我打断：pressure conflict 进入控制 replay，并节流治理切换

目标：

- 承接 R8k，把 pressure/headloss 双源冲突从 Agent51 holdout 边界继续推进到 Agent49/52 控制 replay 影响，而不是只停留在 summary 字段。
- 回应新的治理问题：原“自我打断机制”过于频繁，容易把每个新想法都变成上下文切换，增加算力和决策摩擦。自我打断不应模仿用户的实时纠偏，而应成为低频、高阈值的治理闸门。

实现：

- R8l：
  - Agent49 `control_replay_guardrail_context` 新增 `pressure_source_conflict_count`、`pressure_source_conflict_control_block`、`conflict_requires_operator_review` 和 `pressure_source_conflicts`。
  - 如果 Agent51 已 field validated 但 pressure source conflict 仍需人工复核，Agent49 会把 `field_proxy_labels_ready` 压回 False，并保持 J2 催化剂保护/再生的 R3G1 guardrail penalty。
  - Agent49 决策树新增 `R8K_pressure_source_conflict_requires_operator_review`，明确双源压力冲突不能支撑回流、再生或放行。
  - Agent52 replay row、offline metrics、readiness 和 Agent49 writeback 新增 `pressure_source_conflict_count`、`pressure_source_conflict_requires_operator_review` 和 `pressure_source_conflict_replay_blocked_case_count`。
  - 即使 field replay、Agent51 field holdout、distilled policy accuracy 等指标看似达标，只要 pressure source conflict 未清除，Agent52 仍阻断 Agent49 执行器候选晋级。
- 低摩擦自我打断：
  - R8l/R8m 当时把 Agent50 从频繁即时切换降为阶段边界机制。
  - 后续 R8n 已进一步收缩为两态硬闸门：只有纯展示/整理漂移且不改变模型指标、硬性证据矛盾、或绕过 field replay/保护边界时，才立即中断。
  - 普通新想法、潜在更高边际价值任务、复盘/整理类问题只进入 `stage_boundary_deferred_backlog`，完成当前可验证小闭环后再统一复盘。
  - `self_interrupt_checklist.md` 和 `model_core_goal.md` 已同步为该低摩擦闸门机制，避免后续治理层再次过度打断。
- Agent60：
  - fallback 链新增 R8k/R8l readiness 判断。
  - R8k ready 后推荐 `R8l_pressure_source_conflict_control_replay_impact`。
  - R8l ready 后推进到 `R8m_pressure_source_conflict_field_patch_requirements`，即把冲突 batch、冲突来源、容差和 operator review 写入现场校准/补包任务。

验证：

- 定向测试：
  - `.venv/bin/pytest -q tests/test_model_core_optimization_governance_agent.py tests/test_agent_architecture_consolidation_agent.py tests/test_multi_facility_collaborative_control_agent.py tests/test_multi_facility_replay_evaluation_agent.py`：67 passed。
- 实验脚本：
  - `experiments/run_agent49_multi_facility_collaborative_control.py`：仍为 `synthetic_collaborative_policy_needs_field_replay`；当前 template 下 `pressure_source_conflict_count=0`，但不代表现场无冲突。
  - `experiments/run_agent52_multi_facility_replay_evaluation.py`：仍为 `synthetic_replay_evaluation_ready_needs_field_replay`；新增冲突 replay 字段进入 metrics/readiness/writeback。
  - `experiments/run_agent50_model_core_governance.py`：`self_interrupt_verdict=continue_core_work`，不触发无谓中断。
  - `experiments/run_agent60_agent_architecture_consolidation.py`：离线 fallback 推进到 `R8m_pressure_source_conflict_field_patch_requirements`。
- 完整回归：
  - `.venv/bin/pytest -q`：373 passed。

结论：

- pressure/headloss 双源冲突现在不只是 Agent51 层面的数据质量问题，而是会明确影响 Agent49 协同控制和 Agent52 replay 晋级门的工程保护条件。
- 自我打断机制已改成低摩擦阶段闸门：它保留纠偏能力，但不再因为每个新想法频繁打断当前模型小闭环。
- 当前仍没有真实现场数据；conflict count=0 只说明 header/template 演练没有冲突行，不能证明真实现场压力源一致。

## 2026-06-02 R8j/R8k：pressure/headloss 证据进入控制上下文，并新增多来源冲突校准边界

目标：

- 沿“低成本受限观测下把黑箱变灰箱”的第一性原理，继续把 `pressure/headloss` 从可选水力代理推进为可被 Agent51、Agent49、Agent52 共同审查的证据对象。
- 解决两个新断点：
  - Agent51 虽然能用 `pressure_headloss_event_log` 补足 `N3_catalyst_bed:pressure_drop_kPa`，但 Agent49/52 下游控制 replay 之前看不到压力证据来源，无法解释催化剂保护边界来自节点长表还是压力/水头损失事件表。
  - 当 `node_modality_sensor_timeseries` 和 `pressure_headloss_event_log` 同时给出同一 batch 的 pressure_drop，但二者数值冲突时，系统不能静默平均、任意覆盖或继续把该 batch 当成 scoreable 证据。

实现：

- R8j：
  - Agent49 多设施协同控制与 Agent52 replay evaluation 的 catalyst proxy context/guardrail context 现在透传 `accepted_pressure_evidence_sources`、`pressure_evidence_source_batch_counts` 和 `pressure_headloss_event_source_batch_count`。
  - 这样 J2 催化剂保护、回流/暂存和 replay guardrail 不只知道“有压力代理”，还知道压力证据来自节点级低成本传感、pressure/headloss 事件表，还是仍然缺失。
- R8k：
  - `build_catalyst_proxy_field_holdout_summary()` 新增压力来源优先级与冲突策略：优先使用节点长表中的 `N3_catalyst_bed:pressure_drop_kPa`，缺失时用 `pressure_headloss_event_log` 补足。
  - 如果两个来源在同一 batch 上同时存在且差异超过 `max(1.0 kPa, 0.25 * max(abs(node), abs(event)))`，则该 batch 的 pressure 信号从 scoreable 集合剔除，记录到 `pressure_source_conflicts`，并标记 `operator_review_required_before_agent51_scoring`。
  - Summary 新增 `pressure_source_priority_policy`、`pressure_source_conflict_count`、`pressure_source_conflicts`、`pressure_source_conflict_abs_tolerance_kPa`、`pressure_source_conflict_rel_tolerance` 和 `conflict_requires_operator_review`。
  - Agent60 离线 fallback 推进到 `R8k_pressure_headloss_source_conflict_calibration_boundary`，说明在没有真实包可导入时，当前最高价值离线动作是把水力代理证据边界做实，而不是继续扩展展示或重复 agent。

验证：

- 定向链路测试：
  - `.venv/bin/pytest -q tests/test_catalyst_activity_proxy_agent.py tests/test_multi_facility_replay_evaluation_agent.py tests/test_multi_facility_collaborative_control_agent.py tests/test_field_package_coverage.py`：39 passed。
- 实验脚本：
  - `experiments/run_agent51_catalyst_activity_proxy.py`：仍为 `synthetic_catalyst_proxy_design_ready_needs_field_labels`，当前模板下 `accepted_pressure_evidence_sources=[]`、`pressure_headloss_event_source_batch_count=0`。
  - `experiments/run_agent49_multi_facility_collaborative_control.py`：仍为 `synthetic_collaborative_policy_needs_field_replay`，没有因水力代理合同而解除催化剂保护。
  - `experiments/run_agent52_multi_facility_replay_evaluation.py`：仍为 `synthetic_replay_evaluation_ready_needs_field_replay`，pressure/headloss 只进入 replay guardrail context。
  - `experiments/run_r7_real_field_replay_pipeline.py`：仍为 `real_field_package_acceptance_blocked_at_import`，正确阻断 header-only/template。
  - `experiments/run_agent60_agent_architecture_consolidation.py`：主任务仍为 R7a 真实包导入，离线 fallback 为 `R8k_pressure_headloss_source_conflict_calibration_boundary`。
- 完整回归：
  - `.venv/bin/pytest -q`：368 passed。

结论：

- pressure/headloss 现在不只是“可补足 pressure_drop 的替代字段”，而是具备来源追踪、下游控制上下文透传、冲突识别和人工复核边界的水力代理证据链。
- 这直接服务 `catalyst_activity` 弱状态估计和多设施协同控制的灰箱化：如果床层压降/水头损失与节点传感冲突，系统会承认该隐藏状态证据不足，而不是用错误压力值支撑催化剂保护或回流决策。
- 当前仍没有真实现场数据；本轮证明的是代码契约、冲突边界和 synthetic/template 阻断逻辑正确，不能证明 field-supported 控制有效。

## 2026-06-02 R8g/R8h/R8i：pressure/headloss 水力代理进入 R7 replay、Agent44 诊断和 Agent51 holdout 联动

目标：

- 沿“低成本受限观测下把黑箱变灰箱”的第一性原理，把 `pressure/headloss` 从候选传感字段推进为可被 replay、诊断和催化剂代理验证共同消费的水力证据。
- 解决三个联动断点：
  - Agent30/42/44 已能表达/导入 pressure/headloss，但 R7 最小 replay 契约还未强制消费。
  - 真实包若卡在 Agent44 type/linkage 阻断，R7 patch plan 之前不能给出足够可操作的补包诊断。
  - Agent51 catalyst proxy holdout 只读取 `node_modality_sensor_timeseries` 的 `pressure_drop_kPa`，没有消费已经标准化的 `pressure_headloss_event_log`。

实现：

- R8g：
  - `field_package_coverage.py` 将 `pressure_headloss_event_log` 加入 `REPLAY_TABLES`。
  - 新增 `pressure_headloss_quality` 审计，检查 `batch_id`、`bed_id`、`pressure_drop_kPa`、`headloss_kPa_per_m`、`flow_Lmin`、`matched_lab_sample_time_min`、`regeneration_event` 和 `hydraulic_anomaly_label`。
  - R7 readiness 和 pipeline 输出新增 pressure/headloss event、valid event、invalid event、valid batch 指标。
- R8h：
  - `preflight_field_replay_package()` 输出 Agent44 阻断诊断：blocking table statuses、type errors、required field blockers 和 linkage blockers。
  - R7 patch plan 在真实行存在但 Agent44 仍阻断时生成可操作补包项，包括 pressure/headloss 类型错误修复。
- R8i：
  - `build_catalyst_proxy_field_holdout_summary()` 现在可把 `pressure_headloss_event_log` 作为 `N3_catalyst_bed:pressure_drop_kPa` 的替代来源。
  - Agent51 holdout summary 新增 `accepted_pressure_evidence_sources`、`pressure_headloss_event_source_batch_count`、`pressure_evidence_source_batch_counts`，feature row 新增 `pressure_drop_source`。
  - 该改动不把 pressure/headloss 事件当成 catalyst_activity 标签；它只作为床层水力代理输入，仍需 QA 通过的 catalyst_activity label 才能形成 field holdout validation。

验证：

- 定向链路测试：
  - `.venv/bin/pytest -q tests/test_catalyst_activity_proxy_agent.py tests/test_multi_facility_replay_evaluation_agent.py tests/test_multi_facility_collaborative_control_agent.py tests/test_field_package_coverage.py tests/test_real_field_replay_pipeline.py tests/test_agent_architecture_consolidation_agent.py`：69 passed。
- 完整回归：
  - `.venv/bin/pytest -q`：364 passed。
- 实验脚本：
  - `experiments/run_agent51_catalyst_activity_proxy.py`：仍为 `synthetic_catalyst_proxy_design_ready_needs_field_labels`，模板下 `pressure_headloss_event_source_batch_count=0`。
  - `experiments/run_r7_real_field_replay_pipeline.py`：仍为 `real_field_package_acceptance_blocked_at_import`，正确阻断 header-only/template。
  - `experiments/run_agent60_agent_architecture_consolidation.py`：主任务仍为 R7a 真实包导入，离线 fallback 推进到 `R8i_agent51_consume_pressure_headloss_event_log`。

结论：

- pressure/headloss 现在不再只是字段或候选池，而是贯穿 R7 最小 replay、Agent44 真实包诊断和 Agent51 催化剂弱状态代理的同一条水力证据链。
- 当前仍没有真实现场数据；所有通过项只能证明代码路径、契约和 synthetic/template 阻断逻辑正确，不能证明 field-supported 控制有效。

## Agent 1：数据质控 Agent

目标：在软传感器和多智能体诊断之前，先判断低成本传感数据是否可信，识别缺失、越界、突变、卡死、漂移等问题，并给出下游处理建议。

当前设计：

- 输入：循环式水处理过程的低成本传感时间序列。
- 输出：传感可信度、质量问题列表、问题证据、控制前建议。
- 关键问题：不能让异常传感值直接驱动软测量、加药、回流或达标放行。

### 2026-05-31 迭代 1

第一轮模拟发现：Agent 能识别 ORP 缺失、pH 突变、电导率卡死和流量突变，但漏检了“浊度后段反常上升”。原因是漂移检测只比较全程开头和结尾，中间初始浊度较高时，后段局部上升会被整体下降趋势掩盖。

修复：

- 新增浊度局部窗口漂移检测，比较最近窗口与前一窗口的中位数。
- 新增流量持续偏移检测，用于识别泵阀异常或管路堵塞。
- 固化项目 `.venv` 依赖与 pytest 配置，后续每个 agent 都必须跑自动测试。

### 2026-05-31 迭代 2

新增下游接口：每个传感通道输出 `sensor_scores`，用于软传感器自动降低异常通道权重。这样 Agent 1 不只是写诊断文字，也能给 Agent 2 提供机器可读的可信度输入。

## Agent 2：软传感器 Agent

目标：利用低成本传感信号、循环历史和 Agent 1 的通道可信权重，估计不可直接观测的过程状态，包括污染物残留风险、反应完成度、氧化剂余量、催化剂活性、基质干扰、达标概率和回流边际收益。

当前实现：

- 使用 pandas 对低成本传感序列进行插值和窗口统计。
- 用灰箱启发式公式融合 UV254、ORP、浊度、电导率、pH、流量和循环次数。
- 接入 Agent 1 输出的 `sensor_scores`，异常通道会降低其在状态估计中的权重。
- 输出时间序列 CSV、状态估计 JSON/Markdown 和状态变化图。

### 2026-05-31 迭代 1

第一轮模拟发现：状态曲线方向正确，但“达标概率”和“可自动放行”容易混淆。在传感可信度只有中等水平时，即使估计水质可能达标，也不应直接给出放行倾向。

修复：

- 新增 `release_readiness`，把达标概率、传感可信度和回流边际收益共同作为放行准备度。
- 当达标概率高但 release readiness 不足时，输出 `release_blocked_by_uncertainty`。
- 增加合成真值校验字段，便于模拟阶段持续检查软测量偏差。

## Agent 3：机理解释 Agent

目标：把 Agent 1 的数据质量证据和 Agent 2 的隐藏状态估计，转化为可追溯的机理假设排序。它不直接做最终控制，而是回答“为什么现在不能放行/为什么应该回流/异常最可能来自哪里”。

当前设计：

- 内置轻量知识规则库：传感不确定性、水力停留异常、基质干扰、氧化剂不足、催化剂失活、反应时间不足、可能已处理但证据不足。
- 输入 Agent 1 的 `issue_types` 和 Agent 2 的 `state_estimate`。
- 输出排序后的机理假设、证据、行动提示。

## Agent 4：故障诊断 Agent

目标：把机理假设进一步压成“工程上要排查什么故障”。机理解释回答为什么，故障诊断回答优先查哪里、风险多高、下一步验证动作是什么。

当前故障模式：

- 传感数据不可靠
- 水力停留时间或回流执行异常
- 达标证据不足导致放行受阻
- 基质干扰或新扰动进入系统
- 氧化剂不足
- 催化剂失活或活性位受污染
- 反应时间不足

## Agent 5：控制策略 Agent

目标：把故障诊断压成可执行动作排序。它负责回答“现在到底做什么”，包括暂存验证、核查泵阀、校准传感器、继续回流、补加氧化剂、切换单元或达标放行。

当前策略原则：

- release readiness 不足时，不能因为 compliance probability 高就自动放行。
- 回流只有在回流边际收益足够高时才成为主动作。
- 氧化剂不足必须先有低氧化剂证据，不能盲目加药。
- 水力异常和传感异常优先进入检查/校准动作。

### 2026-05-31 迭代 1

第一轮模拟发现：`hold_for_validation` 分数过低，导致“达标证据不足”时暂存验证没有进入可执行计划。修复后，只要故障诊断指出达标证据不足，暂存并旁路验证就会成为可执行动作。

## Agent 6：成本安全 Agent

目标：在控制策略之后增加安全、成本、能耗、时间和人工复核代价评价，避免控制 Agent 为了“看起来积极”而过早切换单元、盲目加药或冒险放行。

当前评价维度：

- safety_gain：动作带来的安全收益
- money_cost：金钱/药剂/维护成本
- time_cost：处理或等待时间成本
- energy_cost：泵、回流、深度处理等能耗成本
- risk_cost：误放行、误动作或副产物风险
- requires_human_review：是否需要人工复核

### 2026-05-31 迭代 1

第一轮模拟发现：高成本动作“预处理或切换处理单元”虽然原始控制分数超过阈值，但成本安全净收益很低，仍出现在建议文本里。修复后，建议必须同时满足原始可行性和净收益阈值，避免后续仲裁被低净收益动作干扰。

## Agent 7：仲裁 Agent

目标：融合软传感器、控制策略和成本安全评价，形成最终闭环动作，并执行硬安全门。

当前硬约束：

- `release_readiness < 0.82` 时禁止放行。
- `oxidant_remaining >= 0.45` 时禁止盲目补加氧化剂。
- `recycle_gain < 0.2` 时禁止无效回流。
- 传感可信度不足时需要校准或旁路验证。

## 多场景仿真扫查

目标：不能只在一个“传感故障”场景里证明链条可运行，还要检查不同工况下最终仲裁动作是否符合研究方案逻辑。

新增场景：

- `clean_release`：正常处理完成，应允许放行。
- `sensor_faults`：传感异常和证据不足，应暂存验证、校准、查泵阀。
- `oxidant_limitation`：氧化剂不足，应倾向补加氧化剂。
- `reaction_time_insufficient`：反应时间不足但氧化能力尚可，应倾向回流/延长停留。
- `matrix_shock`：基质冲击，应倾向预处理或切换单元。

### 2026-05-31 迭代 1

多场景扫查第一次失败：基础链条过度保守，导致干净场景不放行、氧化剂不足不加药、反应时间不足不回流、基质冲击不切换。修复方向：

- 控制策略对 release、dose、recirculate、switch 动作采用更明确的场景触发权重。
- 成本安全 Agent 改为动态评价：高 release readiness 时放行风险降低；低氧化剂时补加药剂安全收益提高；高基质干扰时切换/预处理收益提高。

## 模型层迭代：Agent 2 软传感器校正

### 2026-05-31 迭代 1

新增合成数据训练脚本 `experiments/train_soft_sensor_model.py`，基于 5 类场景、40 个随机种子生成 14400 行训练数据，训练多输出随机森林校正模型。

训练结果：

- mean MAE：0.01286。
- pollutant residual risk MAE：0.00543。
- reaction completion MAE：0。
- oxidant remaining MAE：0.00017。
- catalyst activity MAE：0。
- matrix interference MAE：0.05869，R2：0.60272。

接入策略：

- Agent 2 不让模型完全接管，而是采用 `calibrated = alpha * model + (1-alpha) * heuristic`。
- `alpha` 随 Agent 1 的传感可信度降低而降低。
- 模型缺失或预测失败时自动退回纯灰箱启发式。

结果：

- 传感故障场景下污染物残留风险误差从约 0.143 降到约 0.073。
- 多场景回归保持通过。
- 氧化剂不足与反应时间不足场景的故障解释更符合预期。

## 闭环执行层迭代

### 2026-05-31 迭代 1

新增 `run_agent_chain` 管道函数和 `run_closed_loop_episode` 多轮闭环仿真。此前系统只做单次判断，现在可以模拟“仲裁动作 -> 场景转移 -> 下一轮感知诊断”的过程。

当前简化转移逻辑：

- 传感故障经暂存/校准后转入 clean release。
- 氧化剂不足经补加药剂并回流后转入 clean release。
- 反应时间不足经回流后转入 clean release。
- 基质冲击经预处理/切换单元后转入 clean release。

这还不是物理精确模型，但已经把研究方案里的“循环让行动变得可行”落实成了可运行闭环。

### 2026-05-31 迭代 2

第一版闭环仍有两个关键问题：

- 反应时间不足场景在长观测窗口下过早放行，没有体现“循环争取时间”。
- 仲裁层可能出现“残留风险安全门未通过，但仍输出 release”的矛盾。

本轮修复：

- 将闭环观测窗口改为 24 min，使每一步代表一个可执行的低成本监测-决策窗口，而不是一次性看完整个长流程。
- 增加过程状态模型 `ProcessState`，用污染物负荷、氧化剂、催化活性、基质干扰、传感健康度和水力效率驱动下一轮传感数据。
- 调整 EC 与浊度生成公式，使普通反应时间不足不会被错误解释为高基质冲击。
- 仲裁层把 `residual_risk_gate` 与动作屏蔽打通，残留风险高时直接禁止放行。
- 仲裁层将 `release` 作为终止动作，不再与回流、预处理等动作同时输出。
- Agent 1 增加 `low_flow_absolute`，让短窗口低流量也能被识别。
- Agent 4 把 `low_flow_absolute` 纳入 `hydraulic_retention_anomaly`，驱动 Agent 5 进入泵阀/回流管路核查。

验证结果：

- `pytest -q`：20 passed。
- 多场景扫查：clean release 放行；sensor faults 暂存/查泵阀/校准；oxidant limitation 补加氧化剂并回流；reaction time insufficient 先回流；matrix shock 预处理/切换并回流。
- 闭环 episode：sensor faults、oxidant limitation、reaction time insufficient、matrix shock 均在 2 步内完成处理或放行。

## Agent 2 软传感器迭代

### 2026-05-31 迭代 2

问题：第一版机器学习校正模型主要来自原始场景合成数据，接入过程动力学闭环后，短窗口数据分布发生变化。动态验证显示，旧模型在 clean/sensor_faults 的残留风险、matrix_shock 的基质干扰上误差偏高，容易造成过早放行或过度保守。

修复：

- 训练集从 14400 行扩展到 43200 行。
- 新增过程动力学增强样本 28800 行，覆盖 24、48、72 min 三类观测窗口。
- 模型版本升级为 `rf_multioutput_v2_dynamic`。
- 软传感状态新增 `hydraulic_confidence`。
- `release_readiness` 新增水力置信度上限：低流量/低 HRT 不能仅凭水质估计达标而自动放行。
- 过程模型增强 `hold_for_validation` 的被动反应效果，并提高 `recirculate` 对污染负荷的削减强度，使多轮循环能够收敛。

训练结果：

- mean MAE：0.0104。
- pollutant residual risk MAE：0.00682，R2：0.99478。
- reaction completion MAE：0.00539，R2：0.99853。
- oxidant remaining MAE：0.00501，R2：0.99898。
- catalyst activity MAE：0.01087，R2：0.97073。
- matrix interference MAE：0.02391，R2：0.8853。

验证结果：

- `pytest -q`：20 passed。
- `sensor_faults` 不再因残留风险刚好过线而首轮放行，而是先暂存验证、查泵阀、校准传感器。
- `oxidant_limitation` 与 `reaction_time_insufficient` 需要多轮回流后放行，更符合“循环为低成本传感和反应争取时间”的研究目的。

## Agent 3 机理解释迭代

### 2026-05-31 迭代 2

问题：软传感器新增 `hydraulic_confidence` 后，机理解释层仍只认识旧的 `sustained_shift`。同时，对“残留风险中等但回流收益仍存在”的状态，Agent 3 只能间接解释为反应时间不足，不能明确表达研究方案里的“循环争取时间”。

修复：

- `hydraulic_anomaly` 同时吸收 `sustained_shift`、`low_flow_absolute` 和 `hydraulic_confidence < 0.7`。
- 新增 `loop_buffer_needed` 机理规则。
- 当残留风险仍高于 0.32、氧化剂仍可用、回流收益为正且放行准备度不足时，Agent 3 会解释为需要循环缓冲窗口。

验证：

- 新增短窗口水力证据测试。
- 新增循环缓冲机理测试。
- `pytest -q`：22 passed。
- 闭环 episode 仍保持收敛：sensor faults 2 步，oxidant limitation 4 步，reaction time insufficient 4 步，matrix shock 2 步。

## Agent 4 故障诊断迭代

### 2026-05-31 迭代 2

问题：Agent 3 已经能提出 `loop_buffer_needed`，但 Agent 4 还没有把它转译为工程故障模式。这样后续控制策略只能依赖通用回流分数，缺少“循环窗口不足”的诊断解释。

修复：

- 新增 `cycle_window_insufficient` 故障模式。
- 故障证据包括污染物残留风险、氧化剂余量、放行准备度、回流收益和上游机理 ID。
- `hydraulic_retention_anomaly` 额外吸收 `hydraulic_confidence` 和 `hydraulic_anomaly` 机理证据。
- `reaction_time_insufficient` 在循环缓冲证据存在时适度加权。

验证：

- 新增 `test_fault_diagnosis_turns_loop_buffer_into_actionable_fault`。
- `pytest -q`：23 passed。
- 多场景扫查和闭环 episode 均保持稳定。

## Agent 5 控制策略迭代

### 2026-05-31 迭代 2

问题：控制策略虽然能选择回流、加药、暂存和切换单元，但参数过于固定，不能体现“动态决定是否回流、延长停留时间、调整药剂投加”的研究目标。同时低基质场景中的切换单元动作仍可能被轻微基质证据抬高。

修复：

- `recirculate` 的 `recycle_ratio` 和 `extra_retention_min` 动态化。
- `hold_for_validation` 的 `hold_min` 动态化。
- `dose_oxidant` 的 `dose_factor` 动态化。
- `release` 的控制层门槛加入残留风险和水力置信度。
- 低基质干扰时压低 `switch_or_pretreat`。

验证：

- 新增动态回流参数测试。
- 新增低基质不切换测试。
- `pytest -q`：25 passed。

## Agent 6 成本安全迭代

### 2026-05-31 迭代 2

问题：高基质冲击场景下，成本安全层因为预处理/切换单元成本较高，把“回流”排到了“预处理/切换”前面。工程上这会导致在高盐/高浊度/高 COD 干扰未处理前就先回流，动作顺序不合理。

修复：

- 当 `matrix_interference >= 0.75` 时，提高 `switch_or_pretreat` 的安全收益，降低其相对风险成本与时间成本。
- 新增高基质冲击下预处理优先于回流的成本安全测试。

验证：

- `pytest -q`：26 passed。
- `matrix_shock` 多场景扫查结果：`['switch_or_pretreat', 'recirculate']`。

## Agent 7 仲裁迭代

### 2026-05-31 迭代 2

问题：上游各层已经能产生正确动作，但最终仲裁层还没有显式记录水力置信度安全门，也缺少动作顺序兜底。若后续模型或成本分数波动，仍可能出现高基质先回流、低水力置信度下误放行等问题。

修复：

- 新增 `hydraulic_confidence_gate`。
- 放行动作屏蔽条件加入 `hydraulic_confidence < 0.7`。
- 仲裁后增加顺序约束：
  - 高基质冲击时，`switch_or_pretreat` 先于 `recirculate`。
  - 低水力置信度时，`inspect_hydraulics` 先于 `recirculate`。
  - `release` 保持终止动作。

验证：

- 新增低水力置信度禁止放行测试。
- 新增高基质冲击下预处理先于回流测试。
- `pytest -q`：28 passed。
- 多场景扫查和闭环 episode 均稳定。

## 鲁棒性评估迭代

### 2026-05-31 迭代 1

目标：从单 seed 验证升级到多随机种子鲁棒性验证，检查闭环系统在低成本传感噪声、过程扰动和不同初始随机条件下是否稳定收敛。

新增：

- `src/water_ai/robustness.py`。
- `experiments/run_closed_loop_robustness.py`。
- `tests/test_robustness.py`。

结果：

- 4 类问题场景、每类 30 个随机种子，共 120 条 episode。
- 全部成功放行或完成处理，失败样本为 0。
- 平均步数：
  - sensor_faults：2.0。
  - oxidant_limitation：4.733。
  - reaction_time_insufficient：4.067。
  - matrix_shock：2.067。

结论：

- 当前闭环不是“一步处理完”的玩具逻辑，而是能在慢传感、慢反应条件下通过多轮回流/验证逐步收敛。
- 氧化剂不足和反应时间不足是下一轮应重点优化成本与时间的场景。

### 2026-05-31 迭代 2

问题：Agent 5 已经输出动态控制参数，但闭环过程模型只接收动作 ID，导致 `recycle_ratio`、`extra_retention_min`、`dose_factor` 和 `hold_min` 还没有真实进入状态转移。

修复：

- `closed_loop.py` 改为把完整 `final_plan` 传给过程动力学层。
- `apply_actions_to_process_state` 支持动作字典和动作参数。
- `hold_for_validation` 根据 `hold_min` 改变被动反应时间、成本和污染物负荷。
- `dose_oxidant` 根据 `dose_factor` 改变氧化剂补加量和药剂成本。
- `recirculate` 根据 `recycle_ratio` 与 `extra_retention_min` 改变去除强度、停留时间、能耗和成本。

结果：

- `pytest -q`：29 passed。
- 单 seed 闭环：reaction_time_insufficient 从 4 步缩短到 3 步。
- 鲁棒性评估：
  - sensor_faults：success_rate 1.0，mean_steps 2.0。
  - oxidant_limitation：success_rate 1.0，mean_steps 4.9。
  - reaction_time_insufficient：success_rate 1.0，mean_steps 2.8。
  - matrix_shock：success_rate 1.0，mean_steps 2.067。

判断：

- 动态控制参数已经真正进入闭环反馈。
- 氧化剂不足场景的平均成本、能耗和步数偏高，下一轮应优化加药-回流联合策略。

### 2026-05-31 迭代 3

问题：参数进入过程反馈后，反应时间不足收敛加快，但氧化剂不足场景平均步数升至 4.9，mean_elapsed_min 达 178.7，说明初始补加氧化剂偏保守，后续需要靠多轮回流补偿。

修复：

- 调整 `dose_factor` 计算公式，使其对低氧化剂余量和高残留风险更敏感。
- 仍保留仲裁层“氧化剂余量足够禁止盲目加药”的硬约束，避免重复过量加药。

结果：

- `pytest -q`：29 passed。
- 单 seed `oxidant_limitation`：4 步缩短为 3 步。
- 30 seed 鲁棒性：
  - oxidant_limitation mean_steps：4.9 -> 2.733。
  - mean_elapsed_min：178.7 -> 72.1。
  - mean_energy：1.23 -> 0.554。
  - success_rate：保持 1.0。

## 副产物风险与过量氧化剂惩罚迭代

### 2026-05-31 迭代 1

问题：前一版加药-回流联合策略把氧化剂不足场景的平均步数从 4.9 降到 2.733，但系统还没有显式建模副产物风险或过量氧化剂风险，容易形成“只追求收敛速度”的偏差。

修复：

- Agent 2 新增 `byproduct_risk`。
- Agent 3 新增“副产物或过氧化风险升高”机理。
- Agent 4 新增 `byproduct_or_overoxidation_risk` 故障模式。
- Agent 5 在副产物风险高时降低补加氧化剂动作评分和 `dose_factor`。
- Agent 6 对高副产物风险或过高 `dose_factor` 的加药动作提高风险成本。
- Agent 7 新增 `byproduct_risk_gate`，副产物风险高于 0.65 时禁止自动放行。

验证：

- 新增软传感、机理、故障、成本安全和仲裁测试。
- `pytest -q`：33 passed。
- 多场景扫查动作保持稳定。
- 闭环 episode：sensor faults 2 步，oxidant limitation 3 步，reaction time insufficient 3 步，matrix shock 2 步。
- 鲁棒性评估：4 类问题场景、每类 30 seed，success_rate 均为 1.0，失败样本 0。

## 离线快检延迟与检测误差迭代

### 2026-05-31 迭代 1

问题：`hold_for_validation` 虽然会增加等待时间和被动反应，但没有显式模拟旁路/离线快检的延迟、误差和置信度，也没有让慢证据进入下一轮软传感。

修复：

- 过程状态新增 `offline_residual_proxy`、`offline_validation_confidence`、`offline_validation_age_min`、`offline_validation_error`。
- `hold_for_validation` 支持 `validation_delay_min`，总等待时间为 `hold_min + validation_delay_min`。
- 快检结果带确定性误差项，并随年龄衰减置信度。
- `generate_sensor_stream_from_process_state` 将仍有效的快检结果作为额外慢证据写入传感流。
- Agent 2 读取 `offline_residual_proxy`，并按 `offline_validation_confidence` 修正污染物残留风险估计。

验证：

- 新增离线快检过程测试和软传感吸收测试。
- `pytest -q`：35 passed。
- 单 seed 闭环仍收敛：sensor faults 2 步，oxidant limitation 3 步，reaction time insufficient 3 步，matrix shock 2 步。
- 30 seed 鲁棒性仍全部成功。

## 催化剂失活-再生/更换闭环迭代

### 2026-05-31 迭代 1

问题：系统已有“催化剂失活”机理和故障表述，但没有形成真正可执行的工程动作。更重要的是，早期判据容易把“反应时间不足”“氧化剂不足”“基质冲击”也误判成催化剂失活，导致不必要的再生/更换。

修复：

- 新增 `catalyst_deactivation` 初始过程场景和传统合成数据场景。
- `apply_actions_to_process_state` 新增 `regenerate_catalyst`，执行后提高 `catalyst_activity`，并计入停机时间、成本、能耗和快检证据衰减。
- Agent 5 新增“再生或更换催化剂”动作，动态输出 `regen_intensity`、`downtime_min` 和确认快检项目。
- Agent 6 新增再生动作成本安全评价，低活性时提高安全收益，活性足够时提高无效再生风险成本。
- Agent 7 新增催化活性约束，低活性下 `regenerate_catalyst` 先于 `recirculate`，高活性时禁止无效再生。
- 软传感器校正模型升级为 `rf_multioutput_v3_catalyst`，训练数据扩展到 51840 行。

关键迭代判断：

- 第一版规则一看到短窗口反应慢就触发再生，导致 `oxidant_limitation`、`reaction_time_insufficient` 和 `matrix_shock` 出现误触发。
- 第二版将失活判据收紧为“低反应完成度 + 明显低催化活性”，使失活场景保留再生动作，而其他场景回到各自正确动作链。

结果：

- `pytest -q`：40 passed。
- 多场景扫查：
  - clean_release：`release`。
  - sensor_faults：`inspect_hydraulics` -> `calibrate_sensors` -> `recirculate`。
  - oxidant_limitation：`dose_oxidant` -> `recirculate`。
  - reaction_time_insufficient：`recirculate`。
  - catalyst_deactivation：`regenerate_catalyst` -> `recirculate`。
  - matrix_shock：`switch_or_pretreat` -> `recirculate`。
- 闭环 episode：catalyst_deactivation 2 步收敛。
- 5 类问题场景、每类 30 seed，共 150 条 episode，success_rate 均为 1.0。

结论：

- 催化剂失活已经从“诊断文本”变成了可执行闭环动作链。
- 当前系统开始具备区分“该加药、该回流、该预处理、该再生”的能力，这是把黑箱过程拆成灰箱工程状态的关键一步。

## 低成本传感-循环窗口敏感性 Agent 迭代

### 2026-05-31 迭代 1

问题：系统已经可以闭环控制，但还不能回答一个更工程化的问题：低成本传感到底能省到什么程度？如果降低采样频率、延长观测窗口或取消某个传感器，系统是仍然可控，还是只是因为安全门过严而无法放行？

修复：

- 新增 `SensitivityAnalysisAgent`，把候选设计按成功率、总耗时、过程成本、能耗和传感成本指数排序。
- `run_closed_loop_episode` 新增 `sampling_interval_min` 和 `disabled_sensors`，支持慢采样和禁用传感器。
- 软传感器和机器学习特征层支持整列传感缺失，用工程中值兜底，并依靠数据质控降低可信度。
- 新增 `experiments/run_design_sensitivity.py`，默认比较 5 种设计：
  - `full_24min_1min`
  - `full_36min_3min`
  - `no_uv_48min_3min`
  - `core_48min_5min`
  - `minimal_60min_5min`

结果：

- `pytest -q`：42 passed。
- 推荐方案：`full_36min_3min`，完整低成本传感、36 min 观测窗口、3 min 采样间隔。
- `full_36min_3min` 平均成功率 1.0，平均总耗时 109.6 min，综合评分 0.908。
- `full_24min_1min` 成功率同为 1.0，但综合评分为 0.8，说明更高采样频率并不一定带来更优闭环效率。
- 取消 `UV254_abs` 的设计在当前模型下会安全降级但无法稳定放行，综合评分为 0。

结论：

- “循环争取时间”确实可以降低采样频率，但不能随意砍掉关键观测通道。
- 当前阶段 UV254 仍是把黑箱变灰箱的重要代理信号；若未来要取消 UV254，必须补充新的软传感特征、离线快检或机理先验。

## 污染物-材料-机制知识库迭代

### 2026-05-31 迭代 1

问题：Agent 3 虽然能用规则解释状态，但这些规则仍然偏“阈值判断”，缺少可维护的污染物-材料-机制知识层。这样不利于把文献、材料特性和工程动作连接起来，也不利于后续扩展到不同污染场景。

修复：

- 新增结构化 `KNOWLEDGE_BASE`。
- 每个知识条目包含：
  - `pollutant_class`
  - `material_family`
  - `mechanism_tags`
  - `signal_conditions`
  - `supports_rules`
  - `action_biases`
  - `explanation`
  - `action_hint`
- 新增 `query_knowledge_base`，根据软传感状态、数据质控 issue 和软传感 issue 对知识条目打分排序。
- Agent 3 输出 `knowledge_matches`，并把知识命中写入机理假设的 `knowledge_support`。
- Agent 4 接收 `knowledge_matches`，将知识证据带入故障诊断证据。

当前知识条目：

- `kb_matrix_aop_inhibition`：高盐/高 COD 基质抑制高级氧化。
- `kb_oxidant_limited_refractory_organics`：高负荷难降解有机物导致氧化剂不足。
- `kb_catalyst_site_fouling`：催化剂活性位污染或堵塞。
- `kb_loop_buffer_for_slow_sensing`：循环窗口为慢检测和软传感复估争取时间。
- `kb_overoxidation_byproduct_precursor`：强氧化体系下副产物/过氧化风险。
- `kb_sensor_limited_release_evidence`：低成本传感证据不足导致不能自动放行。

重要迭代判断：

- 第一版知识库把“循环缓冲”也支持为“达标证据不足”，导致氧化剂不足和基质冲击场景过度插入 `hold_for_validation`。
- 修正后，循环缓冲只支持 `loop_buffer_needed`；副产物和传感证据不足才会触发更强的暂存验证倾向。
- 对高基质冲击场景，新的安全逻辑允许在预处理后插入旁路验证，但仍保持“预处理必须先于回流”的核心顺序。

结果：

- `pytest -q`：46 passed。
- `run_agent3_mechanism.py` 输出知识库命中列表。
- 多场景扫查保持稳定：
  - clean_release：`release`。
  - sensor_faults：`inspect_hydraulics` -> `calibrate_sensors` -> `recirculate`。
  - oxidant_limitation：`dose_oxidant` -> `recirculate`。
  - reaction_time_insufficient：`recirculate`。
  - catalyst_deactivation：`regenerate_catalyst` -> `recirculate`。
  - matrix_shock：`switch_or_pretreat` -> `recirculate`。
- 5 类问题场景、每类 30 seed，共 150 条 episode，success_rate 均为 1.0。

结论：

- Agent 3 已从规则解释升级为“规则 + 结构化知识库”的灰箱解释层。
- 这为后续把文献知识、污染物类别、材料族和工程控制动作接到同一个系统里打下了基础。

## 知识库动作偏置接入 Agent 5 迭代

### 2026-05-31 迭代 1

问题：知识库已经能解释机理并支持故障诊断，但 `action_biases` 还没有影响控制策略。也就是说，知识条目虽然写明“该类场景倾向于预处理、验证、再生或抑制加药”，但 Agent 5 仍只看故障 ID 和软传感状态。

修复：

- Agent 5 从 Agent 4 的 `knowledge_matches` 中读取 `action_biases`。
- 按 `match_score * action_bias` 聚合为 `knowledge_action_biases`。
- 对每个动作评分施加小幅正/负偏置，并将 `knowledge_action_bias` 写入动作证据。
- 偏置被限制在 [-0.22, 0.22]，避免知识库单条命中压倒硬安全门和软传感状态。

结果：

- `pytest -q`：47 passed。
- Agent 5 报告中可看到：
  - `hold_for_validation` 因传感证据不足获得正偏置。
  - `calibrate_sensors` 因传感证据不足获得正偏置。
  - `release` 因放行证据不足获得负偏置。
- 多场景扫查保持稳定：
  - clean_release：`release`。
  - sensor_faults：`inspect_hydraulics` -> `calibrate_sensors` -> `hold_for_validation` -> `recirculate`。
  - oxidant_limitation：`dose_oxidant` -> `recirculate`。
  - reaction_time_insufficient：`recirculate`。
  - catalyst_deactivation：`regenerate_catalyst` -> `recirculate`。
  - matrix_shock：`switch_or_pretreat` -> `recirculate`。
- 5 类问题场景、每类 30 seed，共 150 条 episode，success_rate 均为 1.0。

结论：

- 知识库已经开始影响控制策略，但仍保持“软传感状态 + 安全门 + 成本安全评价”为主。
- 当前偏置更像专家经验的微调层，而不是替代控制决策的硬规则，这更适合低成本传感不确定条件下的灰箱闭环控制。

## 知识库成本安全修正接入 Agent 6 迭代

### 2026-05-31 迭代 1

问题：知识库偏置已经进入 Agent 5 的动作评分，但 Agent 6 成本安全评价仍然只按动作类别和局部证据评估安全收益、成本、时间、能耗和风险。这样会丢失“为什么某个动作在当前污染物-材料机制下更值得承担成本”的解释链。

修复：

- Agent 6 读取动作证据里的 `knowledge_action_bias`。
- 正向偏置：
  - 提高 `safety_gain`。
  - 降低 `risk_cost`。
  - 略微降低 `time_cost`。
- 负向偏置：
  - 降低 `safety_gain`。
  - 提高 `risk_cost`。
  - 略微提高 `time_cost`。
- 输出 `knowledge_cost_adjustment`，记录安全收益、风险成本、时间成本的修正量。

结果：

- `pytest -q`：48 passed。
- Agent 6 报告中，`hold_for_validation` 因低成本传感证据不足获得更高安全收益和更低风险成本。
- `release` 在放行证据不足时风险成本进一步上升。
- 多场景扫查保持稳定：
  - clean_release：`release`。
  - sensor_faults：`inspect_hydraulics` -> `calibrate_sensors` -> `hold_for_validation` -> `recirculate`。
  - oxidant_limitation：`dose_oxidant` -> `recirculate`。
  - reaction_time_insufficient：`recirculate`。
  - catalyst_deactivation：`regenerate_catalyst` -> `recirculate`。
  - matrix_shock：`switch_or_pretreat` -> `recirculate`。
- 5 类问题场景、每类 30 seed，共 150 条 episode，success_rate 均为 1.0。

结论：

- 知识库现在贯穿 Agent 3-6：先解释机理，再支持故障诊断，再影响控制动作评分，最后进入成本安全评价。
- 这使系统更接近“可审计的灰箱闭环控制”，而不是单纯黑箱模型输出动作。

## 统一策略优化目标接入 Agent 6-7 迭代

### 2026-05-31 迭代 1

问题：Agent 6 已经能评价成本、安全、时间和知识偏置，但最终决策仍容易被局部净收益或原始控制分数影响。对于低成本传感闭环系统，真正需要优化的是一个工程综合目标：既不能误放行，也不能无限等待；既要控制药耗和能耗，也要尊重慢检测、旁路验证和知识库机理证据。

修复：

- 新增 `src/water_ai/strategy_objective.py`。
- 新增 `StrategyObjectiveWeights`，将策略目标权重集中管理。
- 新增 `compute_strategy_objective`，统一计算：
  - 控制优先级收益。
  - 安全收益。
  - 知识库动作一致性收益。
  - 处理成本、等待时间、能耗和一般风险惩罚。
  - 误放行风险惩罚。
  - 副产物/过氧化压力惩罚。
  - 人工复核惩罚。
- 将误放行风险权重设为 0.30，使残留风险、传感置信度、水力置信度和副产物风险能真正压过高原始放行分数。
- Agent 6 输出 `objective_score` 和完整 `objective` 分解，推荐动作也改为按 `objective_score` 筛选。
- Agent 7 的最终动作筛选、顺序约束和置信度计算优先使用 `objective_score`，同时保留 `net_score` 作为解释指标。

测试与发现：

- 初始测试发现：误放行风险虽被记录，但默认权重不足以压过一个高原始分数的放行动作。
- 调整后新增的目标函数测试通过，能证明“暂存验证”在高残留、高不确定状态下优于不安全放行。
- 新增 Agent 7 测试，证明最终仲裁确实使用 `objective_score`，而不是继续被旧 `net_score` 主导。

结果：

- `pytest -q`：52 passed。
- 多场景扫查保持稳定：
  - clean_release：`release`。
  - sensor_faults：`inspect_hydraulics` -> `calibrate_sensors` -> `hold_for_validation` -> `recirculate`。
  - oxidant_limitation：`dose_oxidant` -> `recirculate`。
  - reaction_time_insufficient：`recirculate`。
  - catalyst_deactivation：`regenerate_catalyst` -> `recirculate`。
  - matrix_shock：`switch_or_pretreat` -> `recirculate`。
- 闭环 episode：
  - sensor_faults：2 步。
  - oxidant_limitation：3 步。
  - reaction_time_insufficient：3 步。
  - catalyst_deactivation：2 步。
  - matrix_shock：2 步。
- 150 条鲁棒性 episode 全部成功，失败样本 0。
- 低成本传感-循环窗口敏感性保持推荐 `full_36min_3min`，综合评分 0.908，平均成功率 1.0，平均总耗时 111.2 min。

结论：

- 系统现在形成了“软传感灰箱状态 -> 知识库机理证据 -> 故障诊断 -> 控制动作 -> 成本安全 -> 统一策略目标 -> 仲裁执行”的完整链条。
- 这一步让闭环控制从“多个 Agent 各自打分”升级为“可解释、可调权重、可审计的工程优化目标”。

## Agent 8 传感器经济性模型迭代

### 2026-05-31 迭代 1

问题：此前敏感性 Agent 只使用手填的 `sensor_cost_index`。这能粗略表达“少装传感器更便宜”，但无法解释为什么某个配置便宜、便宜在哪里、维护负担如何，也无法把慢采样带来的采样负担下降和硬件采购成本区分开。

修复：

- 新增 `sensor_economics.py`。
- 建立工程默认传感器经济性表，覆盖 `pH`、`ORP_mV`、`EC_uScm`、`turbidity_NTU`、`temp_C`、`flow_Lmin`、`UV254_abs`。
- 每个传感器包含：
  - 采购成本。
  - 月维护成本。
  - 周校准工时。
- 新增 `compute_sensor_economics`，根据禁用传感器、观测窗口和采样间隔计算：
  - `purchase_cost_cny`
  - `annual_maintenance_cny`
  - `calibration_hours_per_month`
  - `samples_per_window`
  - `sampling_load_index`
  - `engineering_cost_index`
- `run_design_sensitivity.py` 不再使用手填成本指数，而是每次根据设计自动计算工程成本。
- `SensitivityAnalysisAgent` 在排序结果和推荐文本中输出工程成本指数、采购成本、年度维护成本、月校准工时和采样负担。

结果：

- `pytest -q`：54 passed。
- `run_design_sensitivity.py` 推荐仍为 `full_36min_3min`。
- 推荐配置：
  - mean_success_rate：1.0。
  - mean_total_elapsed_min：111.2。
  - utility_score：0.882。
  - sensor_cost_index：0.9。
  - purchase_cost_cny：11800。
  - annual_maintenance_cny：5040。
  - calibration_hours_per_month：9.02。
- 极简配置和取消 UV254 的配置工程成本明显更低，但成功率为 0，因此仍不会被推荐。

结论：

- Agent 8 已经从“抽象低成本排序”升级为“传感器硬件成本 + 运维成本 + 采样负担 + 闭环成功率”的综合评估。
- 这更符合研究方案的核心判断：低成本不是盲目少装传感器，而是在安全门不失效的前提下，用循环结构和慢采样降低系统负担。

## Agent 8 设计敏感性缓存迭代

### 2026-05-31 迭代 1

问题：`run_design_sensitivity.py` 每次都要重新跑 5 个设计、5 类问题场景和多随机种子的完整闭环 episode。随着后续继续调整传感器价格表、排序权重和报告文本，如果每次都重跑仿真，会严重拖慢迭代速度。

修复：

- 为每个设计生成缓存键，缓存键包含：
  - 缓存版本。
  - 设计 ID。
  - 观测窗口。
  - 采样间隔。
  - 禁用传感器。
  - 工程成本指数。
  - 场景列表。
  - 随机种子。
  - 最大闭环步数。
- 新增 `outputs/design_sensitivity/cache/` 缓存目录。
- `evaluate_designs` 默认读取和写入缓存。
- 新增 `--force-refresh`：强制重跑闭环并刷新缓存。
- 新增 `--no-cache`：关闭缓存读写，用于排查缓存污染。
- 新增缓存键测试，确保设计参数和随机种子改变时缓存键也改变。

结果：

- `pytest -q`：56 passed。
- `run_design_sensitivity.py --force-refresh` 重算后结果不变。
- 普通 `run_design_sensitivity.py` 命中缓存后约 0.184 s。
- 当前默认 5 个设计各生成一个缓存文件。

结论：

- Agent 8 后续可以快速迭代价格表、权重和报告，不必每次重复完整闭环仿真。
- 缓存键包含影响闭环结果的核心输入，降低误用旧结果的风险。

## Agent 8 采样噪声模型迭代

### 2026-05-31 迭代 1

问题：此前设计敏感性只模拟了采样间隔和禁用传感器，但低成本传感的真实问题还包括测量噪声和漂移。若不把噪声显式纳入，系统可能高估慢采样或低价传感配置的可用性。

修复：

- `run_closed_loop_episode` 新增 `sensor_noise_multiplier` 参数。
- `_apply_sensor_design` 在抽样和通道禁用之后，可对保留传感器注入确定性测量噪声。
- 噪声按传感器类型设置基础幅度：
  - pH、ORP、EC、浊度、温度、流量、UV254 分别使用不同扰动尺度。
- 噪声采用确定性波形，而不是随机数；同一时间戳、同一 cycle、同一传感器和同一倍率会得到相同扰动，便于复现实验。
- `evaluate_closed_loop_robustness` 传递 `sensor_noise_multiplier`。
- `run_design_sensitivity.py` 为每个候选设计设置噪声倍率。
- 缓存版本升级到 `design_sensitivity_v3_sensor_noise`，避免复用无噪声旧缓存。

结果：

- `pytest -q`：57 passed。
- 带噪声 `run_design_sensitivity.py --force-refresh` 后，推荐仍为 `full_36min_3min`。
- 推荐配置：
  - sensor_noise_multiplier：0.75。
  - mean_success_rate：1.0。
  - mean_total_elapsed_min：111.1。
  - utility_score：0.882。
  - sensor_cost_index：0.9。
- 普通 `run_design_sensitivity.py` 命中 v3 缓存后约 0.186 s。

结论：

- 当前软传感和安全门对合理低成本测量扰动有容忍度。
- 低成本方案的排序现在同时考虑通道删减、采样间隔、硬件/维护成本和测量噪声，更接近真实工程部署评估。

## 策略目标场景模板迭代

### 2026-05-31 迭代 1

问题：统一策略目标已经能合成成本、时间、风险和安全收益，但目前只有一套默认权重。实际研究方案中，不同应用场景的目标函数不应完全相同：饮用水深度处理应更强调误放行风险，工业废水工程化示范可能更关注成本和能耗，应急旁路则更关注响应速度。

修复：

- 新增 `STRATEGY_OBJECTIVE_PROFILES`。
- 新增 `get_strategy_objective_weights`。
- 内置四类模板：
  - `balanced`：默认平衡模板。
  - `safety_first`：提高误放行风险、一般风险和副产物风险权重。
  - `cost_first`：提高处理成本、时间和能耗权重。
  - `emergency_response`：降低等待时间惩罚，提高控制优先级。
- `CostSafetyAgent` 支持 `objective_profile` 参数。
- 如果传入自定义 `StrategyObjectiveWeights`，输出 profile 标记为 `custom`。
- Agent 6 报告新增 `strategy_objective_profile`，便于审计决策口径。

结果：

- `pytest -q`：59 passed。
- 多场景扫查保持默认 `balanced` 链路不变：
  - clean_release：`release`。
  - sensor_faults：`inspect_hydraulics` -> `calibrate_sensors` -> `hold_for_validation` -> `recirculate`。
  - oxidant_limitation：`dose_oxidant` -> `recirculate`。
  - reaction_time_insufficient：`recirculate`。
  - catalyst_deactivation：`regenerate_catalyst` -> `recirculate`。
  - matrix_shock：`switch_or_pretreat` -> `recirculate`。

结论：

- 统一目标函数已经从“一个固定评分公式”升级为“可按研究场景切换的策略口径”。
- 下一步可以让上游场景识别或人工配置决定采用哪个 profile，而不是在 Agent 6 手动指定。

## 策略目标自动选择 Agent 迭代

### 2026-05-31 迭代 1

问题：上一轮已经建立了 `balanced`、`safety_first`、`cost_first`、`emergency_response` 四个策略目标模板，但它们还停留在 Agent 6 的手动参数层。主链路仍默认 `balanced`，没有真正根据软传感状态和故障诊断自动切换决策口径。

修复：

- 新增 `StrategyProfileAgent`。
- 输入：
  - Agent 2 的软传感状态。
  - Agent 4 的故障诊断排序。
- 输出：
  - `selected_profile`。
  - 各 profile 分数。
  - 选择依据。
  - 使用的状态与故障证据。
- `run_agent_chain` 在 Agent 5 控制策略之后调用 `StrategyProfileAgent`。
- `CostSafetyAgent` 使用 `StrategyProfileAgent` 输出的 profile 计算统一目标。
- `run_scenario_sweep.py` 和 `run_full_agent_chain.py` 已把策略 profile 写入输出报告。
- `run_closed_loop_episode.py` 已把每一步的策略 profile 写入闭环输出。
- 设计敏感性缓存版本升级为 `design_sensitivity_v4_strategy_profile`，避免复用旧 profile 逻辑下的缓存。

调试发现：

- 第一版启发式过于保守，所有场景都选择 `safety_first`。
- 修正后只保留可信故障证据，并把残留风险从“一票安全优先”改为评分项。
- 氧化剂不足且回流收益明确时允许选择 `emergency_response`。
- 清洁达标且传感/水力证据充分时选择 `cost_first`。

结果：

- `pytest -q`：63 passed。
- 多场景 profile 与动作链：
  - clean_release：`cost_first`，最终 `release`。
  - sensor_faults：`safety_first`，最终 `inspect_hydraulics` -> `calibrate_sensors` -> `hold_for_validation` -> `recirculate`。
  - oxidant_limitation：`emergency_response`，最终 `dose_oxidant` -> `recirculate`。
  - reaction_time_insufficient：`balanced`，最终 `recirculate`。
  - catalyst_deactivation：`safety_first`，最终 `regenerate_catalyst` -> `recirculate`。
  - matrix_shock：`safety_first`，最终 `switch_or_pretreat` -> `recirculate`。
- 150 条鲁棒性 episode 全部成功，失败样本 0：
  - sensor_faults mean_steps 2.233。
  - oxidant_limitation mean_steps 3.0。
  - reaction_time_insufficient mean_steps 3.0。
  - catalyst_deactivation mean_steps 2.9。
  - matrix_shock mean_steps 2.033。
- 带策略 profile 的设计敏感性推荐仍为 `full_36min_3min`，平均成功率 1.0，平均总耗时 119.8 min，综合评分 0.882。
- 普通 `run_design_sensitivity.py` 命中 v4 缓存后约 0.167 s。

结论：

- 策略 profile 已经从“配置项”变成主链路中的自动策略选择层。
- 这让系统更接近重大项目方案里的“场景识别-策略口径-控制执行”结构，而不是固定目标函数。

## 催化剂生命周期 Agent 迭代

### 2026-05-31 迭代 1

问题：此前系统能识别催化剂失活，也能执行 `regenerate_catalyst`，但所有催化剂问题都会被压缩成“再生一次再回流”。这不符合长期工程运行：催化剂多次再生后恢复率会下降，继续再生会增加停机、药耗和材料损耗；在寿命耗尽时，应进入更换模块而不是盲目重复再生。

修复：

- `ProcessState` 新增 `catalyst_age_cycles`、`catalyst_regen_count`、`catalyst_lifetime_fraction`。
- 过程动力学中，回流会消耗催化剂寿命；再生会提高当前活性，但会增加再生次数并降低后续可恢复上限。
- 新增动作 `replace_catalyst`：重置催化剂年龄、再生次数和寿命比例，同时引入更高停机时间与成本。
- `SoftSensorAgent` 新增生命周期灰箱状态：
  - `catalyst_age_cycles`
  - `catalyst_regen_count`
  - `catalyst_lifetime_fraction`
  - `catalyst_regeneration_potential`
  - `catalyst_replacement_urgency`
- `FaultDiagnosisAgent` 新增 `catalyst_lifecycle_exhaustion`。
- 新增 `CatalystLifecycleAgent`，把软传感状态与故障诊断转化为 `monitor_catalyst`、`regenerate_catalyst` 或 `replace_catalyst`。
- `ControlStrategyAgent` 接收生命周期建议，并把“再生”和“更换”拆成两个独立候选动作。
- `CostSafetyAgent` 对低再生潜力下的重复再生提高风险/时间成本，对高更换紧迫度下的更换提高安全收益。
- `ArbitrationAgent` 增加寿命安全门：更换紧迫度不足时禁止过早更换；更换紧迫度高且再生潜力低时禁止继续无效再生。
- 新增 `experiments/run_agent10_catalyst_lifecycle.py`，固定输出“寿命尚可”和“寿命耗尽”两个边界场景。
- 设计敏感性缓存版本升级为 `design_sensitivity_v5_catalyst_lifecycle`，并清理旧 v4 缓存。

调试发现：

- 初版若只看催化活性，容易让更换动作过早进入初始催化剂失活场景。
- 通过加入 `replacement_urgency < 0.55` 的仲裁门，系统保留“寿命尚可先再生”的工程习惯。
- 通过 `regeneration_potential <= 0.30` 与 `replacement_urgency >= 0.72` 的组合门，系统只在再生确实不划算时切换到更换。

结果：

- `pytest -q`：68 passed。
- `run_agent10_catalyst_lifecycle.py`：
  - `remaining_life_regeneration`：`regenerate_catalyst` -> `recirculate`。
  - `exhausted_life_replacement`：`replace_catalyst` -> `recirculate`。
- 多场景扫查保持主链稳定：
  - `clean_release`：`release`。
  - `sensor_faults`：`inspect_hydraulics` -> `calibrate_sensors` -> `hold_for_validation` -> `recirculate`。
  - `oxidant_limitation`：`dose_oxidant` -> `recirculate`。
  - `reaction_time_insufficient`：`recirculate`。
  - `catalyst_deactivation`：`regenerate_catalyst` -> `recirculate`。
  - `matrix_shock`：`switch_or_pretreat` -> `recirculate`。
- 150 条鲁棒性 episode 全部成功，失败样本 0：
  - `sensor_faults` mean_steps 2.233。
  - `oxidant_limitation` mean_steps 3.067。
  - `reaction_time_insufficient` mean_steps 3.0。
  - `catalyst_deactivation` mean_steps 3.067。
  - `matrix_shock` mean_steps 2.033。
- 设计敏感性推荐仍为 `full_36min_3min`，平均成功率 1.0，平均总耗时 122.3 min，综合评分 0.882。
- 当前缓存为 5 个 v5 默认设计缓存；普通 `run_design_sensitivity.py` 可直接复用。

结论：

- 催化剂失活现在不再只是“再生动作”，而是形成了“寿命估计-维护策略-成本安全-仲裁执行”的小闭环。
- 这让研究方案更接近长期工程运行：不仅判断这一批水能否处理达标，也开始判断材料系统能否经济、稳定、可持续地运行。

## 旁路验证规划 Agent 迭代

### 2026-05-31 迭代 1

问题：系统已有 `hold_for_validation`，但此前它只是一个笼统动作。研究方案的核心是“通过循环式水处理结构为软传感和诊断争取时间”，因此等待时间应该服务于具体慢证据：测什么、等多久、用于校准哪个安全门，都需要显式化。

修复：

- 新增 `ValidationPlanningAgent`。
- 输入 Agent 2 的软传感状态和 Agent 4 的故障诊断结果。
- 输出：
  - `plan_name`
  - `urgency`
  - `hold_min`
  - `validation_delay_min`
  - `targets`
  - `release_gate`
- 支持的验证规划包括：
  - 传感可靠性交叉验证。
  - 放行门验证。
  - 氧化剂余量快检。
  - 副产物防护验证。
  - 基质冲击表征。
  - 催化剂生命周期验证。
- `ControlStrategyAgent` 接入验证规划，把目标、暂存时间和等待时间写入 `hold_for_validation` 参数。
- 主链路、全链条报告、场景扫查和催化剂生命周期专项报告均纳入验证规划输出。
- 设计敏感性缓存版本升级为 `design_sensitivity_v6_validation_planning`，并清理旧 v5 缓存。

调试发现：

- 基质冲击场景在预处理/切换之后加入 `hold_for_validation`，这是预期变化：强基质扰动下，不应只靠低成本在线信号立即进入下一轮回流，而应等待盐度/浊度/COD 等慢证据确认。
- 慢证据规划会增加耗时和成本，但这正是本研究要量化的工程权衡：低成本传感并不是免费，而是用循环结构和等待窗口换取可信度。

结果：

- `pytest -q`：70 passed。
- 多场景扫查：
  - `clean_release`：`release`。
  - `sensor_faults`：`inspect_hydraulics` -> `calibrate_sensors` -> `hold_for_validation` -> `recirculate`。
  - `oxidant_limitation`：`dose_oxidant` -> `recirculate`。
  - `reaction_time_insufficient`：`recirculate`。
  - `catalyst_deactivation`：`regenerate_catalyst` -> `recirculate`。
  - `matrix_shock`：`switch_or_pretreat` -> `hold_for_validation` -> `recirculate`。
- 150 条鲁棒性 episode 全部成功，失败样本 0：
  - `sensor_faults` mean_steps 2.3，mean_elapsed_min 66.8。
  - `oxidant_limitation` mean_steps 3.067，mean_elapsed_min 177.2。
  - `reaction_time_insufficient` mean_steps 3.067，mean_elapsed_min 65.3。
  - `catalyst_deactivation` mean_steps 3.067，mean_elapsed_min 314.6。
  - `matrix_shock` mean_steps 2.1，mean_elapsed_min 132.6。
- 设计敏感性推荐仍为 `full_36min_3min`，平均成功率 1.0，平均总耗时 155.4 min，综合评分 0.882。
- 当前缓存为 5 个 v6 默认设计缓存；普通 `run_design_sensitivity.py` 可直接复用。

结论：

- 闭环中的“循环”现在不只是物理回流动作，也成为证据生产窗口。
- 系统开始具备研究方案中最关键的工程含义：传感器可以更便宜、更慢，但必须把等待时间组织成可解释、可审计、可反馈的验证计划。

## 多批次运行调度 Agent 迭代

### 2026-05-31 迭代 1

问题：前 11 个 Agent 已经能完成单批次闭环，但工程系统不是只处理一批水。连续运行时会出现单批次看不到的问题：旁路验证排队、催化剂备件耗尽、氧化剂库存不足、总运行窗口超时。若不把这些纳入系统，低成本传感的“可行性”仍然只停留在单次决策层面。

修复：

- 新增 `operations.py`。
- 新增 `run_multibatch_campaign`，连续运行多个 batch，并在批次之间保留催化剂状态：
  - `catalyst_activity`
  - `catalyst_age_cycles`
  - `catalyst_regen_count`
  - `catalyst_lifetime_fraction`
- 新增 `BatchOperationRecord` 和 `CampaignResult`，记录每个批次：
  - 成功/失败。
  - 步数和耗时。
  - 所有最终动作。
  - 验证分钟数。
  - 再生、更换、加药次数。
  - 终止时催化剂寿命、活性、再生次数。
  - 成本与能耗。
- 新增 `OperationsSchedulingAgent`。
- 输入多批次记录、催化剂备件库存、氧化剂库存、验证人员工时容量和 campaign 时间预算。
- 输出：
  - `campaign_metrics`
  - `bottlenecks`
  - `schedule`
  - `operating_mode`
  - `action_queue`
- 新增 `experiments/run_agent12_operations_scheduling.py`。

调试发现：

- 单批次全部成功并不代表 campaign 可持续运行。
- 示例 campaign 中 8 个批次全部达标，但验证工时占用达到 2.17 倍容量，催化剂备件为 0。
- 因此调度层不能只看 success_rate；必须同时看验证资源、备件库存和总运行时间。

结果：

- `pytest -q`：73 passed。
- `run_agent12_operations_scheduling.py`：
  - 8 个连续批次 success_rate 1.0。
  - total elapsed min：1580。
  - catalyst spares remaining：0。
  - validation staff usage：2.17。
  - operating mode：`pause_or_limit_intake`。
  - 调度建议：
    - 限制新批次进水。
    - 增加旁路快检班次或压缩低价值验证项。
    - 补充催化剂模块库存，并把低寿命批次列入预防性维护。

结论：

- 系统开始从“单批次智能闭环”进入“连续运行工程调度”。
- 这直接回应了研究方案里的可行性问题：传感和反应速度可以不那么快，但必须通过循环、排队、补库、错峰验证和限流，把慢动作组织成可执行系统。

## 批次队列规划 Agent 迭代

### 2026-05-31 迭代 1

问题：Agent 12 能发现多批次 campaign 的运行瓶颈，但还不能回答“换一种批次顺序是否能缓解瓶颈”。如果只给出限流和补库建议，系统仍然缺少队列层的主动规划能力。

修复：

- 新增 `QueuePlanningAgent`。
- 输入多个候选队列策略，每个策略包含：
  - `policy_id`
  - `description`
  - `scenarios`
  - campaign 运行指标
  - 调度瓶颈
  - 运行模式
- 输出：
  - `selected_policy`
  - `ranked_policies`
  - `queue_score`
  - 前 3 批建议顺序
  - 无法靠排序解决的瓶颈提示
- 新增 `experiments/run_agent13_queue_planning.py`。
- 默认比较 4 种队列：
  - `arrival_order`：按到达顺序。
  - `validation_smoothed`：分散高验证负担场景。
  - `catalyst_preserving`：推迟连续催化剂压力批次。
  - `high_risk_first`：优先处理基质冲击和催化剂风险。

调试发现：

- 4 种队列都能保持 success_rate 1.0。
- 但所有候选都存在 campaign 级瓶颈，说明这组任务不是“排好顺序就行”，而是资源容量不足。
- `high_risk_first` 得分最高，但 queue_score 只有 0.097。它的意义不是完美方案，而是较早暴露高风险维护瓶颈，并降低验证工时占用和时间占用。

结果：

- `pytest -q`：75 passed。
- `run_agent13_queue_planning.py`：
  - 推荐 `high_risk_first`。
  - queue_score：0.097。
  - validation_staff_usage：1.406。
  - time_budget_usage：1.188。
  - catalyst_spares_remaining：0。
  - bottlenecks：`validation_capacity`、`campaign_time_budget`、`catalyst_inventory`。
- 对比原始到达顺序：
  - `arrival_order` validation_staff_usage 2.17，time_budget_usage 1.646。
  - `high_risk_first` 将验证工时和时间压力降下来，但仍不足以恢复正常进水。

结论：

- 系统从“发现瓶颈”推进到“比较队列策略”。
- 当前最重要的结论是负面的但很有用：仅靠换顺序不能解决资源瓶颈，下一轮应比较资源扩容和低价值验证项压缩方案。

## 资源扩容对比 Agent 迭代

### 2026-05-31 迭代 1

问题：Agent 13 已经证明，在当前 8 批 campaign 中，仅靠调整批次顺序无法解除验证容量、总时间窗口和催化剂库存瓶颈。下一步必须回答“补哪块资源最划算”，否则系统只能给出笼统的扩容建议。

修复：

- 新增 `ResourceExpansionAgent`。
- 输入同一组 campaign 记录、当前催化剂备件、氧化剂库存、验证人员工时容量和 campaign 时间预算。
- 默认比较 7 类干预：
  - `add_validation_shift`：增加旁路快检/离线验证班次。
  - `add_catalyst_spare`：新增催化剂模块备件。
  - `replenish_oxidant_stock`：补充氧化剂库存。
  - `compress_low_value_validation`：压缩低价值验证项。
  - `extend_campaign_window`：延长当日运行窗口。
  - `validation_shift_plus_spare`：验证班次 + 催化剂备件。
  - `full_resource_recovery`：验证班次、催化剂备件、运行窗口、验证项压缩组合干预。
- 输出：
  - `intervention_score`
  - `bottleneck_relief`
  - `implementation_cost_index`
  - `implementation_risk`
  - 调整后的验证工时占用、时间预算占用、催化剂备件、氧化剂库存
  - `residual_bottleneck_ids`
- 新增 `experiments/run_agent14_resource_expansion.py`。

调试发现：

- 单独增加验证班次可以解除验证容量瓶颈，但仍留下 campaign 时间窗口和催化剂库存问题。
- 单独补催化剂备件可以解除库存瓶颈，但验证容量和时间窗口仍然过载。
- 因此当前 campaign 是复合瓶颈，必须组合干预。
- 测试中还确认了一个细节：如果催化剂寿命偏低，只补 1 个备件仍会保留库存 warning；真正解除库存瓶颈需要更高备件余量。

结果：

- `pytest -q`：78 passed。
- `run_agent14_resource_expansion.py`：
  - 推荐 `full_resource_recovery`。
  - intervention_score：1.0。
  - bottleneck_relief：2.45。
  - validation_staff_usage：从 1.406 降到 0.574。
  - time_budget_usage：从 1.188 降到 0.864。
  - residual_bottleneck_ids：空。
- 单项对比：
  - `validation_shift_plus_spare`：评分 0.884，仍剩 `campaign_time_budget`。
  - `add_validation_shift`：评分 0.501，仍剩 `campaign_time_budget` 和 `catalyst_inventory`。
  - `add_catalyst_spare`：评分 0.441，仍剩 `validation_capacity` 和 `campaign_time_budget`。

结论：

- 系统从“换顺序不够”推进到“量化资源干预收益”。
- 当前工程含义很明确：若要让低成本传感闭环在该 campaign 下可持续运行，不能只加一个人或只买一个备件，而应组合增加验证能力、补催化剂备件、压缩低价值验证项并延长运行窗口。

## 长期经济性与提前期 Agent 迭代

### 2026-05-31 迭代 1

问题：Agent 14 能说明当前 campaign 需要组合资源干预，并且 `full_resource_recovery` 能解除复合瓶颈；但它还不能回答“这套完整恢复能力是否长期划算、采购和人力爬坡是否来得及、预算是否承受得住”。如果缺少这一层，系统容易把一次性救急方案误当成长期建设方案。

修复：

- 新增 `LongTermEconomicsAgent`。
- 输入同一组 campaign 记录、Agent 14 的资源扩容排序、当前催化剂备件、氧化剂库存、验证人员工时容量和运行时间窗口。
- 默认比较 5 类长期项目：
  - `minimum_response`：只保留滚动监测和临时限流。
  - `validation_capacity_program`：优先补齐旁路快检与离线验证班次。
  - `inventory_buffer_program`：优先建立催化剂模块和氧化剂库存缓冲。
  - `balanced_recovery_program`：同时补验证班次、催化剂备件、氧化剂库存，并适度扩展运行窗口。
  - `full_recovery_program`：完整恢复能力，包含验证班次、备件、氧化剂、运行窗口和低价值验证压缩。
- 输出：
  - `program_score`
  - `service_level`
  - `resource_resilience`
  - `multi_campaign_cost_index`
  - `budget_pressure`
  - `lead_time_risk`
  - `residual_operational_risk`
  - `selected_program`
  - 分阶段预算、过渡期限流和验证优先级建议
- 新增 `experiments/run_agent15_long_term_economics.py`。

调试发现：

- 长期层不能简单复用 Agent 14 的最高分结果；必须同时惩罚预算压力和采购/人力提前期。
- `balanced_recovery_program` 成本更低，但在当前 8 批高风险 campaign 下仍残留 `campaign_time_budget` 瓶颈。
- `full_recovery_program` 虽然成本压力更高，却是当前候选中唯一能清空残余瓶颈的长期项目。
- 因此更合理的表述不是“满配最好”，而是“完整恢复是性能解，但必须分阶段实施，并在到位前限流和错峰”。

结果：

- `pytest -q`：81 passed。
- `run_agent15_long_term_economics.py`：
  - 推荐 `full_recovery_program`。
  - program_score：0.651。
  - service_level：0.723。
  - multi_campaign_cost_index：5.836。
  - budget_pressure：1.39。
  - lead_time_risk：0.53。
  - residual_bottleneck_ids：空。
- 对比：
  - `balanced_recovery_program`：评分 0.526，成本指数 3.468，仍剩 `campaign_time_budget`。
  - `validation_capacity_program`：评分 0.339，仍剩 `campaign_time_budget` 和 `catalyst_inventory`。
  - `inventory_buffer_program`：评分 0.334，仍剩 `validation_capacity` 和 `campaign_time_budget`。
  - `minimum_response`：评分 0.231，验证、时间和催化剂库存瓶颈全部保留。

结论：

- 系统从“该补什么资源”推进到“怎样把资源建设组织成可长期执行的项目”。
- 当前研究含义是：低成本传感并不要求传感和反应都很快，但必须通过循环窗口、软传感灰箱估计、旁路慢证据、资源扩容、采购提前期管理和过渡期限流，把慢系统组织成可控系统。

## 分阶段实施 Agent 迭代

### 2026-05-31 迭代 1

问题：Agent 15 已经指出完整恢复方案是当前性能解，但预算压力和提前期风险都偏高。如果只停在“推荐完整恢复”，工程上仍然不知道第一批先限流多少、哪些资源先补、催化剂没到货时怎么运行、什么时候才能恢复满负荷。

修复：

- 新增 `PhasedImplementationAgent`。
- 输入 Agent 15 的 `selected_program`、`ranked_programs`、baseline 和 planning assumptions。
- 输出：
  - `phase_plan`
  - `inventory_policy`
  - `validation_staffing_plan`
  - `intake_policy`
  - `milestones`
  - `execution_score`
  - `schedule_risk`
  - `implementation_readiness`
- 新增 `experiments/run_agent16_phased_implementation.py`。

默认阶段：

- `phase_0_transition_control`：资源到位前限流、错峰、集中慢证据优先级。
- `phase_1_validation_and_oxidant_ramp`：先补最快见效的验证能力和氧化剂库存。
- `phase_2_catalyst_procurement_lock`：锁定催化剂备件采购与预防性维护清单。
- `phase_3_integrated_ramp_up`：资源到位后做完整能力试运行，逐步恢复进水比例。

调试发现：

- 当前完整恢复方案不是“立即满负荷”，而是至少存在 2 个 campaign 的能力爬坡窗口。
- 第 0 个 campaign 必须先限流到 50%，否则验证、催化剂和时间瓶颈仍会压垮闭环。
- 验证与氧化剂可以在第 1 个 campaign 先见效，催化剂备件由于提前期要延续到第 2 个 campaign。
- 阶段验收必须看验证工时占用、时间预算占用、库存余量和最终放行门，而不是只看批次是否成功。

结果：

- `pytest -q`：84 passed。
- `run_agent16_phased_implementation.py`：
  - 围绕 `full_recovery_program` 形成 4 个阶段。
  - 预计第 2 个 campaign 进入完整能力验证。
  - execution_score：0.657。
  - schedule_risk：0.434。
  - implementation_readiness：0.668。
  - 第 0 个 campaign 最大进水比例：0.5。
  - 资源到位前最大进水比例：0.65。
  - 资源到位后最大进水比例：1.0。
  - 催化剂安全库存：2。
  - 氧化剂安全库存：1.2。
  - 验证工时目标：从 5.5 h/campaign 提高到 10.5 h/campaign。

结论：

- 系统从“长期项目选择”推进到“项目实施路线”。
- 这进一步落实了用户最初提出的核心想法：用循环式结构争取时间，不只是给软传感器争取推断时间，也给慢验证、资源补库、人力爬坡和安全放行争取组织时间。

## 实施压力测试 Agent 迭代

### 2026-05-31 迭代 1

问题：Agent 16 给出了分阶段实施计划，但现实中资源不会总是按计划到位。催化剂可能晚到、预算可能慢批、验证班次可能爬坡失败、进水压力可能突然升高、阶段验收也可能失败。缺少压力测试时，分阶段计划容易变成静态甘特图，而不是可滚动调整的工程闭环。

修复：

- 新增 `ImplementationStressTestAgent`。
- 输入 Agent 16 的 `phase_plan`、`intake_policy`、`inventory_policy`、`validation_staffing_plan` 和 Agent 15 的 `selected_program`。
- 默认压力情景：
  - `on_schedule`
  - `catalyst_delay`
  - `budget_slow_release`
  - `validation_ramp_delay`
  - `combined_delay_high_intake`
  - `acceptance_failure`
- 输出：
  - `ranked_stress_scenarios`
  - `worst_case`
  - `robustness_score`
  - `guardrails`
  - `trigger_table`
- 新增 `experiments/run_agent17_implementation_stress_test.py`。

调试发现：

- 第一版规则对“延迟 + 高进水压力”的组合情景偏乐观，仍允许 0.59 的过渡期进水比例。
- 修复后加入组合压力惩罚：只要 ready campaign 推迟且同时存在预算缺口或进水压力升高，就提高场景风险。
- 修复后组合情景会触发保护性进水上限 0.45，并进入备用路径。

结果：

- `pytest -q`：87 passed。
- `run_agent17_implementation_stress_test.py`：
  - 最坏情景：`combined_delay_high_intake`。
  - scenario_risk：0.356。
  - robustness_score：0.86。
  - max_transition_intake_fraction：0.45。
  - latest_safe_ready_campaign：3。
  - 自动重规划触发阈值：
    - `scenario_risk >= 0.55`
    - ready campaign 推迟超过 1 个 campaign
    - protected intake fraction <= 0.45
    - 阶段验收失败
  - 备用动作：
    - 催化剂外部调拨或备用供应商询价。
    - 外包低价值背景验证，内部班次保留放行门、副产物和催化剂寿命证据。
    - 预算拆成验证能力、催化剂库存和氧化剂库存三张批复单。
    - 拒绝新增高风险进水直到队列和库存恢复安全线。

结论：

- 系统从“项目实施路线”推进到“实施路线的韧性评估”。
- 现在的闭环已经覆盖技术层循环、调度层循环和项目实施层循环：每个 campaign 后不仅重新估计水质状态，也重新估计 ready campaign、库存安全线、验证队列和备用路径。

## 自适应项目组合 Agent 迭代

### 2026-05-31 迭代 1

问题：Agent 17 能发现最坏实施情景并给出触发阈值，但还没有自动回答“触发后究竟启动哪组备用项目、先批哪笔预算、负荷控制压到多少”。如果只列出备用动作，仍然需要人工把风险翻译成项目组合。

修复：

- 新增 `AdaptivePortfolioAgent`。
- 输入 Agent 17 的 `ranked_stress_scenarios`、`guardrails` 和 Agent 15 的 `selected_program`。
- 自动抽取主导压力信号：
  - `acceptance_failure`
  - `budget_slow_release`
  - `catalyst_delay`
  - `high_intake_pressure`
  - `validation_ramp_delay`
- 默认比较 5 类项目包：
  - `baseline_execution`
  - `validation_bridge_package`
  - `supplier_resilience_package`
  - `phased_budget_package`
  - `resilience_bridge_portfolio`
- 输出：
  - `selected_portfolio`
  - `ranked_portfolios`
  - `budget_sequence`
  - `load_control_policy`
  - `dominant_stress_signals`
- 新增 `experiments/run_agent18_adaptive_portfolio.py`。

调试发现：

- 单一预算压力时，`phased_budget_package` 会优先，因为它覆盖预算慢批且成本低。
- 无压力时，系统会保留 `baseline_execution`，避免为了“看起来更稳健”而无意义加预算。
- 复合压力下，单一外包验证或单一供应韧性项目包都只能覆盖部分信号，最终应选择综合项目包。

结果：

- `pytest -q`：90 passed。
- `run_agent18_adaptive_portfolio.py`：
  - 推荐 `resilience_bridge_portfolio`。
  - portfolio_score：0.724。
  - expected_risk_reduction：0.32。
  - residual_risk：0.036。
  - budget_pressure：0.875。
  - 覆盖信号：验收失败、预算慢批、催化剂延迟、高进水压力、验证爬坡延迟。
  - 过渡期保护性进水比例：0.45。
  - 预算释放顺序：
    1. 外包低价值验证。
    2. 催化剂备用供应商。
    3. 验证能力批复。
    4. 催化剂库存批复。
    5. 氧化剂库存批复。

结论：

- 系统从“压力测试”推进到“压力情景下的项目组合自动选择”。
- 现在链路已经能从低成本传感黑箱问题一路推到项目实施层：软传感把黑箱变灰箱，多智能体解释与控制让行动可行，调度和项目组合让慢动作在工程上可执行。

## 在线滚动项目控制 Agent 迭代

### 2026-05-31 迭代 1

问题：Agent 18 能根据压力测试结果选择备用项目包和预算释放顺序，但仍然是一次性项目建议。真实系统每个 campaign 后都会出现新的验收、库存、预算和进水压力状态，项目组合必须滚动调整，否则会再次退化成静态方案。

修复：

- 新增 `OnlineProjectControlAgent`。
- 输入 Agent 18 的 `selected_portfolio`、`budget_sequence`、`load_control_policy`，以及 campaign 后滚动更新记录。
- 每个 campaign 更新：
  - 验收是否通过。
  - success_rate。
  - validation_staff_usage。
  - time_budget_usage。
  - catalyst_spares_remaining。
  - oxidant_stock_units_remaining。
  - budget_released_items。
  - budget_release_fraction。
  - intake_pressure_multiplier。
  - ready_campaign_slip。
- 输出：
  - `rolling_decisions`
  - `current_control_state`
  - `next_intake_fraction`
  - `next_budget_item`
  - `replan_required`
  - `replan_reasons`
  - `stable_streak`
- 新增 `experiments/run_agent19_online_project_control.py`。

调试发现：

- 失败或压力升高时，不能只继续原保护性进水比例；若验收失败或 rolling risk 高，应该压到 0.35 左右并触发重规划。
- 连续两个 campaign 稳定通过后，可以按 0.15 梯度恢复进水，但仍保留最终放行门。
- 预算顺序不应机械照搬 Agent 18：如果最新 campaign 出现催化剂库存压力，就要优先催化剂备用供应商或催化剂库存批复。

结果：

- `pytest -q`：93 passed。
- `run_agent19_online_project_control.py`：
  - campaign 0：
    - mode：`replan_and_protect`
    - rolling_risk：0.368
    - next_intake_fraction：0.45
    - next_budget_item：`验证能力批复`
    - replan_required：True
  - campaign 1：
    - mode：`steady_monitoring`
    - rolling_risk：0.0
    - stable_streak：1
    - next_intake_fraction：0.53
  - campaign 2：
    - mode：`controlled_ramp_up`
    - rolling_risk：0.0
    - stable_streak：2
    - next_intake_fraction：0.68
    - next_budget_item：本轮无需新增预算项，保持滚动复核。

结论：

- 系统从“备用项目包选择”推进到“campaign 后在线项目控制”。
- 这让整个研究方案的“循环”更完整：水处理过程本身循环，软传感和慢证据循环，运行调度循环，资源建设和项目组合也按 campaign 循环更新。

## Campaign 遥测桥接 Agent 迭代

### 2026-05-31 迭代 1

问题：Agent 19 已经能根据 campaign 后状态做在线项目控制，但输入状态仍是人工构造的。这样会有一个风险：项目控制看起来能滚动，但没有真正接回前端运行仿真或现场批次记录。

修复：

- 新增 `CampaignTelemetryAgent`。
- 输入真实 `batch_records`、更新切点、初始催化剂备件、氧化剂库存、验证工时容量、时间预算和预算释放计划。
- 对每个更新切点取前缀 records，调用 `OperationsSchedulingAgent` 生成真实滚动指标。
- 输出：
  - `rolling_campaign_updates`
  - `latest_update`
  - `success_rate`
  - `validation_staff_usage`
  - `time_budget_usage`
  - `catalyst_spares_remaining`
  - `oxidant_stock_units_remaining`
  - `intake_pressure_multiplier`
  - `budget_release_fraction`
  - `budget_released_items`
  - `ready_campaign_slip`
  - `bottleneck_ids`
  - `operating_mode`
- 新增 `experiments/run_agent20_campaign_telemetry.py`。

调试发现：

- 手工示例里 Agent 19 在连续稳定验收后进入 `controlled_ramp_up`。
- 但接入真实 8 批高风险 campaign records 后，最新验证工时占用仍为 1.406，时间预算占用为 1.188，催化剂备件为 0。
- 因此真实遥测会把控制状态从乐观恢复纠正为 `replan_and_protect`。
- 这说明在线项目控制必须以真实运行数据为准，不能依赖手工构造的理想项目状态。

结果：

- `pytest -q`：96 passed。
- `run_agent20_campaign_telemetry.py`：
  - 生成 3 个滚动更新。
  - update 0：2 批后 success_rate 1.0，validation_staff_usage 0.161，time_budget_usage 0.223，无瓶颈。
  - update 1：5 批后 catalyst_spares_remaining 0，瓶颈为 `catalyst_inventory`。
  - update 2：8 批后 validation_staff_usage 1.406，time_budget_usage 1.188，瓶颈为 `validation_capacity`、`campaign_time_budget`、`catalyst_inventory`。
  - 接入 Agent 19 后：
    - current_project_mode：`replan_and_protect`
    - next_intake_fraction：0.35
    - next_budget_item：本轮无需新增预算项，保持滚动复核
    - replan_required：True

结论：

- 系统从“在线项目控制”推进到“运行数据驱动的在线项目控制”。
- 这一步很关键：它把真实多批次水处理运行、资源瓶颈、预算释放和项目控制接成一条数据链，形成真正的工程闭环。

## 自动重规划编排 Agent 迭代

### 2026-05-31 迭代 1

问题：Agent 20 已经能用真实遥测触发 Agent 19 的 `replan_and_protect`，但输出仍然只是“需要重跑队列规划、资源扩容、压力测试和项目组合”。为了形成真正闭环，系统应当自动执行这条后半链，而不是把重规划交还给人工。

修复：

- 新增 `ReplanningOrchestratorAgent`。
- 输入：
  - `current_control_state`
  - `batch_records`
  - `queue_candidate_plans`
  - 当前催化剂备件和氧化剂库存
  - 验证工时容量和 campaign 时间预算
- 如果 `replan_required=False`，保持滚动监测，不执行昂贵重规划。
- 如果 `replan_required=True`，自动重跑：
  - `QueuePlanningAgent`
  - `ResourceExpansionAgent`
  - `LongTermEconomicsAgent`
  - `PhasedImplementationAgent`
  - `ImplementationStressTestAgent`
  - `AdaptivePortfolioAgent`
- 输出 `replan_trace`，保留每一层的关键选择。
- 新增 `experiments/run_agent21_replanning_orchestrator.py`。

调试发现：

- 自动重规划必须允许没有候选队列的情况：现场可能只有当前 batch records，尚未生成队列候选。此时应跳过队列排序，但继续资源、长期、压力和项目组合重规划。
- 如果提供候选队列，则重规划 trace 必须保留 selected queue policy，避免后续只知道资源方案而不知道如何排队。

结果：

- `pytest -q`：99 passed。
- `run_agent21_replanning_orchestrator.py`：
  - 由 Agent 20 真实遥测触发 Agent 19 的 `replan_and_protect`。
  - 自动重规划执行成功。
  - 队列规划推荐：`high_risk_first`。
  - 资源扩容推荐：`full_resource_recovery`。
  - 长期经济性推荐：`full_recovery_program`。
  - 分阶段实施：第 2 个 campaign 进入完整能力验证。
  - 压力测试最坏情景：`combined_delay_high_intake`。
  - 自适应项目组合推荐：`resilience_bridge_portfolio`。
  - 重规划后保护性进水比例：0.45。
  - 预算顺序：外包低价值验证 -> 催化剂备用供应商 -> 验证能力批复 -> 催化剂库存批复 -> 氧化剂库存批复。

结论：

- 系统从“运行数据触发重规划”推进到“自动执行重规划”。
- 现在已经形成一条闭合工程链：真实 campaign 遥测 -> 在线项目控制 -> 自动重规划 -> 新项目组合和控制基线 -> 下一轮 campaign。

## 控制基线写回 Agent 迭代

### 2026-05-31 迭代 1

问题：Agent 21 已经能自动执行重规划并生成 `replan_trace`，但 trace 仍然是一次结果。如果不写回下一轮控制基线，下一轮 OnlineProjectControlAgent 仍可能沿用旧队列、旧项目包、旧预算顺序和旧保护性进水比例。

修复：

- 新增 `ControlBaselineUpdateAgent`。
- 输入：
  - `replan_trace`
  - `replan_executed`
  - `previous_baseline`
  - `baseline_version`
- 输出：
  - `updated_baseline`
  - `baseline_version`
  - `online_control_config`
  - `selected_queue_policy`
  - `selected_portfolio`
  - `budget_sequence`
  - `load_control_policy`
  - `readiness`
  - `guardrails`
  - `writeback_rules`
- 新增 `experiments/run_agent22_control_baseline_update.py`。

调试发现：

- 如果 `replan_executed=False`，不能伪造新基线，应沿用上一版并明确不更新。
- 如果重规划已执行但缺少预算顺序、项目包或负荷控制策略，应给出 incomplete writeback warning。
- 写回基线需要包含稳定验收恢复进水的规则，否则下一轮控制器只知道保护比例，不知道何时恢复负荷。

结果：

- `pytest -q`：102 passed。
- `run_agent22_control_baseline_update.py`：
  - 写回版本：`baseline_v1_replan`。
  - 默认队列策略：`high_risk_first`。
  - 默认项目包：`resilience_bridge_portfolio`。
  - 保护性进水比例：0.45。
  - 预算项：外包低价值验证、催化剂备用供应商、验证能力批复、催化剂库存批复、氧化剂库存批复。
  - 写回规则：
    - 连续 2 个 campaign 稳定验收后恢复进水。
    - 每次恢复梯度 0.15。
    - 验收失败触发重规划。
    - ready campaign 滑移超过 1 个 campaign 触发重规划。

结论：

- 系统从“自动执行重规划”推进到“自动重规划结果写回控制基线”。
- 至此，项目实施层闭环已经具备完整记忆：真实遥测触发重规划，重规划改变下一轮控制基线，下一轮 campaign 再用新基线继续滚动。

## 重规划后回放验证 Agent 迭代

### 2026-05-31 迭代 1

问题：Agent 22 已经能把自动重规划结果写回 `baseline_v1_replan`，但还需要验证这个写回基线在下一轮 campaign 中是否真的降低运行瓶颈。否则，链路只是“规划写回成功”，还不能证明工程效果。

修复：

- 新增 `PostReplanReplayAgent`。
- 输入：
  - 重规划前真实 batch records。
  - 写回后的 `online_control_config`。
  - 当前催化剂备件、氧化剂库存、验证工时容量和时间预算。
- 投影规则：
  - 按保护性进水比例截取下一轮接纳批次数。
  - `外包低价值验证` 将验证分钟数乘以 0.78。
  - `验证能力批复` 增加 5 h/campaign 验证容量。
  - `催化剂备用供应商` 和 `催化剂库存批复` 增加催化剂备件。
  - `氧化剂库存批复` 增加氧化剂库存。
- 输出：
  - `before`
  - `after`
  - `projection`
  - `comparison`
  - verdict、impact_score、移除瓶颈、剩余瓶颈和吞吐比例。
- 新增 `experiments/run_agent23_post_replan_replay.py`。

调试发现：

- 单测第一版设置的单批耗时过高，导致重规划后仍残留 `campaign_time_budget` warning。该结果是合理的 partial，而不是代码错误。
- 因此测试数据被调成“前置 campaign 有复合瓶颈，但写回基线足以清掉时间瓶颈”的情形；另保留无预算动作和低吞吐代价的测试。

结果：

- `pytest -q`：105 passed。
- `run_agent23_post_replan_replay.py`：
  - verdict：`validated`。
  - impact_score：0.864。
  - validation_staff_usage：1.406 -> 0.337。
  - time_budget_usage：1.188 -> 0.755。
  - removed_bottlenecks：`campaign_time_budget`、`catalyst_inventory`、`validation_capacity`。
  - remaining_bottlenecks：空。
  - throughput_fraction：0.5。
  - admitted_batch_count：4。

结论：

- 系统从“控制基线写回”推进到“写回基线的工程效果验证”。
- 回放说明重规划确实能清掉当前复合瓶颈，但代价是下一轮只能接纳半数批次；这正好符合研究思路：不是假装低成本慢系统可以满负荷运行，而是通过循环、限流、验证和资源补齐让行动变可行。

## 恢复放量爬坡验证 Agent 迭代

### 2026-05-31 迭代 1

问题：Agent 23 已经证明 `baseline_v1_replan` 在保护性进水下能清掉复合瓶颈，但还没有回答下一步工程问题：如果系统稳定后从 0.45 往上恢复负荷，恢复到哪里会再次失稳。若只说“连续两个 campaign 稳定后恢复”，控制基线仍缺少可执行的恢复边界。

修复：

- 新增 `RecoveryRampAgent`。
- 输入：
  - 下一轮候选 batch records。
  - 写回后的 `online_control_config`。
  - 当前催化剂备件、氧化剂库存、验证工时容量和 campaign 时间预算。
  - 可选 `start_fraction`、`ramp_step` 和 `target_stable_campaigns`。
- 投影规则：
  - 从保护性进水比例开始，按 `ramp_step` 逐轮增加。
  - 每个恢复比例按接纳批次数截取队列。
  - 应用外包低价值验证、验证能力批复、催化剂库存批复和氧化剂库存批复等预算项。
  - 每个爬坡点重新运行 `OperationsSchedulingAgent`。
- 输出：
  - `ramp_path`
  - `final_safe_intake_fraction`
  - `final_safe_throughput_fraction`
  - `limiting_attempted_fraction`
  - `limiting_bottlenecks`
  - `resource_projection`
- 新增 `experiments/run_agent24_recovery_ramp.py`。

调试发现：

- 第一个恢复点不能只看名义进水比例，还要记录实际吞吐比例。8 个候选批次下，尝试 0.60 会接纳 5 批，实际吞吐为 0.625。
- 0.60 恢复点可以稳定通过，但继续尝试 0.75 时，因接纳 6 批后总耗时占用达到警戒线，`campaign_time_budget` 重新出现。
- 因此“循环为低成本传感争取时间”不是无限延长，而是需要被 campaign 时间预算约束住。

结果：

- `pytest tests/test_recovery_ramp_agent.py -q`：3 passed。
- `run_agent24_recovery_ramp.py`：
  - verdict：`partial_ramp_hold`。
  - stable_campaigns_completed：1/2。
  - final_safe_intake_fraction：0.60。
  - final_safe_throughput_fraction：0.625。
  - limiting_attempted_fraction：0.75。
  - limiting_bottlenecks：`campaign_time_budget`。

结论：

- 系统从“写回基线有效性验证”推进到“写回基线后的恢复边界验证”。
- 当前最稳妥策略是把下一轮恢复上限设为 0.60，而不是直接按两轮规则盲目恢复到 0.75。
- 下一步应让在线控制基线吸收 Agent24 结果：当恢复被 `campaign_time_budget` 限制时，自动生成时间窗口释放、验证错峰和队列再排序方案。

## 时间预算恢复方案 Agent 迭代

### 2026-05-31 迭代 1

问题：Agent 24 证明了 0.60 可以稳定恢复，但 0.75 会重新触发 `campaign_time_budget`。这说明恢复边界已经找到了，但还没有把瓶颈转化为具体工程动作：是继续限流、延长运行窗口、错峰验证，还是调整队列。

修复：

- 新增 `TimeBudgetRecoveryAgent`。
- 输入：
  - Agent 24 的 `recovery_ramp_metrics`。
  - 下一轮候选 batch records。
  - 写回后的 `online_control_config`。
  - 当前资源和 campaign 时间预算。
- 候选方案：
  - `hold_safe_fraction`
  - `extend_campaign_window_120min`
  - `stagger_validation_overlap`
  - `time_smoothed_queue`
  - `hybrid_overlap_plus_60min`
- 每个候选方案都会重新运行 `OperationsSchedulingAgent`，输出稳定性、吞吐比例、时间占用、验证占用、额外窗口、节省耗时、队列扰动和综合评分。
- 选择策略增加工程约束：如果原队列顺序下存在稳定目标恢复方案，则优先保持原队列顺序，避免短耗时优先队列把高风险批次长期后移。
- 新增 `experiments/run_agent25_time_budget_recovery.py`。

调试发现：

- 单纯按综合评分，`time_smoothed_queue` 很容易最高，因为它通过暂缓长耗时批次获得最大时间余量。
- 但这会牺牲 `high_risk_first` 的原始治理逻辑，尤其可能把催化剂压力批次后移。
- 因此 Agent25 不能只做数值最优，还要把“队列扰动”作为工程约束处理。

结果：

- `pytest tests/test_time_budget_recovery_agent.py -q`：3 passed。
- `run_agent25_time_budget_recovery.py`：
  - verdict：`target_recovery_feasible`。
  - selected_candidate：`stagger_validation_overlap`。
  - target_intake_fraction：0.75。
  - actual_throughput_fraction：0.75。
  - time_budget_usage：0.884。
  - validation_staff_usage：0.394。
  - elapsed_reduction_min：90.2。

结论：

- 系统从“识别恢复边界”推进到“为边界瓶颈选择具体恢复动作”。
- 当前可执行方案是恢复到 0.75，但必须采用旁路验证、暂存和回流观察的错峰重叠，并在 campaign 后继续遥测复核。
- 下一步应把该方案写回在线控制基线，使恢复动作不再只是报告建议，而成为下一轮控制输入。

## 恢复策略写回 Agent 迭代

### 2026-05-31 迭代 1

问题：Agent 25 已经选出 `stagger_validation_overlap`，但该结果仍只是一个候选方案报告。如果不写回在线控制基线，下一轮 OnlineProjectControlAgent 仍只知道旧的保护性进水和旧的恢复规则，不知道“恢复到 0.75 必须带验证错峰、失败回退和遥测复核”。

修复：

- 新增 `RecoveryStrategyWritebackAgent`。
- 输入：
  - Agent 25 的 `time_budget_recovery_metrics`。
  - 上一版 `online_control_config`。
  - 当前基线版本。
- 写回内容：
  - 新基线版本 `baseline_v1_replan_recovery`。
  - `load_control_policy.protected_intake_fraction = 0.75`。
  - `load_control_policy.fallback_intake_fraction = 0.60`。
  - `recovery_control_policy`。
  - `selected_queue_policy.runtime_recovery_override`。
  - `writeback_rules` 中的恢复后回放、爬坡复核和重新规划门槛。
  - `guardrails` 中的恢复策略时间、验证和瓶颈回归阈值。
- 新增 `experiments/run_agent26_recovery_strategy_writeback.py`。

调试发现：

- 写回不能只改 `protected_intake_fraction`，否则会把恢复策略误读成普通负荷恢复。
- 必须同时写入 fallback triggers：验收失败、时间预算超 0.90、验证工时超 0.90、`campaign_time_budget` 返回、库存瓶颈返回。
- 对 `stagger_validation_overlap` 需要显式保留“不能取消放行门、副产物和催化剂寿命慢证据”，避免错峰被误用成删减验证。

结果：

- `pytest tests/test_recovery_strategy_writeback_agent.py -q`：3 passed。
- `run_agent26_recovery_strategy_writeback.py`：
  - baseline_version：`baseline_v1_replan_recovery`。
  - writeback_mode：`conditional_target_recovery`。
  - selected_candidate_id：`stagger_validation_overlap`。
  - next_intake_fraction：0.75。
  - fallback_intake_fraction：0.60。
  - expected_time_budget_usage：0.884。
  - expected_validation_staff_usage：0.394。

结论：

- 系统从“恢复方案选择”推进到“恢复方案写回控制基线”。
- 现在下一轮控制输入已经不只是 0.75 这个数字，而是一套条件恢复策略：错峰执行、原队列顺序、失败回退和 campaign 后复核。
- 下一步应对 `baseline_v1_replan_recovery` 做恢复后回放，验证写回后的策略在滚动运行里是否真的稳定。

## 恢复策略执行回放 Agent 迭代

### 2026-05-31 迭代 1

问题：Agent 26 已经把 `stagger_validation_overlap` 写回为 `baseline_v1_replan_recovery`，但仍需要验证写回策略在执行层是否真的能解除时间瓶颈。只验证配置存在不够，因为实际 campaign 仍可能因时间、验证工时或库存瓶颈而触发回退。

修复：

- 新增 `RecoveryExecutionReplayAgent`。
- 输入：
  - 下一轮候选 batch records。
  - `baseline_v1_replan_recovery`。
  - 当前催化剂备件、氧化剂库存、验证工时容量和 campaign 时间预算。
- 回放方式：
  - 构造 `without_recovery_strategy`，即 0.75 进水但不执行验证错峰。
  - 构造 `with_recovery_strategy`，即 0.75 进水并执行 `stagger_validation_overlap`。
  - 应用预算项带来的验证压缩、验证能力增加、催化剂备件和氧化剂库存补充。
  - 如果策略触发时间或验证工时门槛，则输出 fallback_required。
- 新增 `experiments/run_agent27_recovery_execution_replay.py`。

调试发现：

- 无错峰时 0.75 进水确实会触发 `campaign_time_budget`，time_budget_usage 为 0.978。
- 执行写回策略后，长验证批次总占用时间减少 90.2 min，time_budget_usage 降到 0.884。
- 这说明 Agent25 的方案不是纸面建议，Agent26 写回后在执行回放中仍能成立。

结果：

- `pytest tests/test_recovery_execution_replay_agent.py -q`：3 passed。
- `run_agent27_recovery_execution_replay.py`：
  - replay_verdict：`recovery_execution_validated`。
  - time_usage_without_strategy：0.978。
  - time_usage_with_strategy：0.884。
  - time_usage_reduction：0.094。
  - validation_usage_with_strategy：0.394。
  - strategy_bottleneck_ids：空。
  - recommended_next_intake_fraction：0.75。

结论：

- 系统从“恢复策略写回”推进到“恢复策略执行回放验证”。
- 当前可以有条件维持 0.75 进水，但不能把它视为永久满负荷基线；仍要保留 fallback_intake_fraction 0.60 和 campaign 后复核。
- 下一步应把 Agent27 的执行回放结果接入在线项目控制，使 OnlineProjectControlAgent 能基于恢复后遥测自动决定维持、回退或重规划。

## 恢复在线控制接入 Agent 迭代

### 2026-05-31 迭代 1

问题：Agent 27 已经证明 `baseline_v1_replan_recovery` 在执行回放中成立，但这个结果还没有接回在线项目控制。若 OnlineProjectControlAgent 只看普通 rolling risk，它可能无法严格执行恢复策略的硬回退线；因此需要一个恢复策略专用接入层。

修复：

- 新增 `RecoveryOnlineControlAgent`。
- 输入：
  - Agent 27 的 `recovery_execution_metrics`。
  - Agent 26 写回的 `recovery_baseline`。
- 处理流程：
  - 将恢复执行回放结果转换为 campaign 级 rolling update。
  - 调用 `OnlineProjectControlAgent` 生成原始在线控制状态。
  - 根据恢复策略的 `fallback_required`、`strategy_stable`、`target_intake_fraction` 和 `fallback_intake_fraction` 生成调整后的控制状态。
  - 如果恢复执行回放稳定，则维持 `maintain_conditional_recovery`。
  - 如果触发 fallback，则强制回退到 0.60 并标记 replan_required。
- 新增 `experiments/run_agent28_recovery_online_control.py`。

调试发现：

- OnlineProjectControlAgent 的普通风险权重适合常规 campaign，但对恢复策略中的硬回退门槛不够直接。
- 因此 Agent28 需要保留 `base_online_state`，同时输出 `adjusted_control_state`，避免把恢复策略控制和普通滚动控制混为一谈。

结果：

- `pytest tests/test_recovery_online_control_agent.py -q`：3 passed。
- `run_agent28_recovery_online_control.py`：
  - recovery_control_mode：`maintain_conditional_recovery`。
  - next_intake_fraction：0.75。
  - fallback_intake_fraction：0.60。
  - replan_required：False。
  - recovery_replay_verdict：`recovery_execution_validated`。

结论：

- 系统从“恢复策略执行回放”推进到“恢复策略在线控制接入”。
- 当前 0.75 是条件恢复状态，不是永久满负荷状态；它已经接入在线控制，但仍保留 fallback 和 campaign 后复核。
- 下一步应进入项目级收束：生成 28-agent 总流程图、模块表、关键证据链和真实数据校准清单。

## 项目综合总览 Agent 迭代

### 2026-05-31 迭代 1

问题：Agent 28 已经把恢复策略接回在线控制，但系统仍缺少一个项目级收束层。单个 agent 报告能说明局部链路，却不能直接回答“这个模型现在能不能作为研究方案、项目书和后续实证平台”。

修复：

- 新增 `ProjectSynthesisAgent`。
- 输入：
  - Agent 28 的最新恢复在线控制状态。
  - Agent 23、25、27 的关键回放与恢复证据。
  - 当前文件成果和回归结果。
- 输出：
  - 七个模块分组：低成本感知、机理诊断、闭环仲裁、批次调度、资源实施、在线重规划、恢复控制。
  - 关键证据链：从“黑箱变灰箱”到“0.75 条件恢复、0.60 回退线”。
  - 成熟度判断：`research_platform_ready_for_field_calibration`。
  - 真实数据校准路线：传感器漂移、软传感标签、催化剂寿命、副产物风险、时间预算和部署接口。
- 新增 `experiments/run_agent29_project_synthesis.py`。
- 新增 `docs/project_overview_28_agent.md`。

调试发现：

- 项目级总览不能把 Agent28 的稳定结果包装成“现场可自治运行”。当前证据足够支撑研究原型和重大项目方案骨架，但真实数据校准必须作为明确边界。
- Agent23 的回放字段命名与早期测试样例不同，`ProjectSynthesisAgent` 需要兼容 `before_validation_staff_usage`、`after_time_budget_usage` 和 `removed_bottleneck_ids` 等真实报告字段。

结果：

- `pytest tests/test_project_synthesis_agent.py -q`：3 passed。
- `run_agent29_project_synthesis.py`：
  - synthesized_agent_count：28。
  - maturity_level：`research_platform_ready_for_field_calibration`。
  - recovery_control_mode：`maintain_conditional_recovery`。
  - next_intake_fraction：0.75。
  - fallback_intake_fraction：0.60。
  - replan_required：False。
  - 输出 `outputs/agent29_project_synthesis/agent29_report.md` 和 `docs/project_overview_28_agent.md`。

结论：

- 系统从“连续追加控制 agent”推进到“项目级研究平台收束”。
- 现在可以回答：模型已经足够作为研究方案、项目书和原型展示的核心骨架；下一阶段不是继续堆 agent，而是接入真实传感器时间序列、离线检测标签、催化剂寿命记录和中试 campaign 运行日志做实证校准。

## 真实数据接口 Agent 迭代

### 2026-05-31 迭代 1

问题：Agent 29 已完成项目级收束，但“真实数据校准路线”仍停留在说明层。进入实证前必须先知道现场数据包要包含哪些表、哪些字段、怎样用 batch_id 回连，以及当前数据是合成样例还是真实现场数据。

修复：

- 新增 `FieldDataInterfaceAgent`。
- 定义五张数据表：
  - `sensor_timeseries`
  - `offline_lab_results`
  - `catalyst_lifecycle`
  - `campaign_operation_log`
  - `cost_deployment`
- 检查：
  - 必需字段完整性。
  - 最低记录数。
  - 主键重复。
  - batch_id 是否能在传感、离线检测、催化剂和操作日志之间回连。
  - 数据来源是否为真实 field 数据。
- 输出 P1-P5 校准任务就绪度。
- 新增 `experiments/run_agent30_field_data_interface.py`。
- 生成 `field_data_schema.json`、CSV 采集模板和 synthetic 样例数据包。

调试发现：

- 合成样例包字段完整时，校准任务会全部显示就绪；但这只能说明接口模板可运行，不能说明已经完成现场校准。
- 因此 Agent30 必须用 `template_ready_not_field_validated` 和 `synthetic_template_not_field_validated` 明确风险边界。
- 推荐语中不能出现空待办列表；当 P1-P5 模板均就绪时，应转而提示“用真实现场数据替换 synthetic/sample 行”。

结果：

- `pytest tests/test_field_data_interface_agent.py -q`：4 passed。
- `run_agent30_field_data_interface.py`：
  - interface_status：`template_ready_not_field_validated`。
  - field_coverage：1.0。
  - linkage_score：1.0。
  - calibration_readiness_score：1.0。
  - 生成 `outputs/agent30_field_data_interface/field_data_schema.json`。
  - 生成 `outputs/agent30_field_data_interface/field_data_templates/`。
  - 生成 `outputs/agent30_field_data_interface/synthetic_field_data_package/`。
  - 生成 `docs/field_data_interface_spec.md`。

结论：

- 系统从“项目级收束”推进到“整理阶段入口”。
- 现在已经有真实数据采集模板和字段契约，可以把项目成果整理成统一索引，并在后续接入真实现场数据时直接按表导入。

## 成果整理 Agent 迭代

### 2026-05-31 迭代 1

问题：Agent 30 已经生成真实数据接口模板，但项目材料仍散落在 `docs/`、`outputs/`、`notes/` 和 `deliverables/` 中。进入整理阶段后，需要把这些成果组织成可以直接用于项目书、汇报和后续实证校准的统一入口。

修复：

- 新增 `DeliverableOrganizationAgent`。
- 输入：
  - `deliverables/manifest.json`。
  - Agent29 项目综合报告。
  - Agent30 真实数据接口报告。
  - 成果文件存在性检查结果。
- 输出：
  - `executive_summary`。
  - `presentation_outline`。
  - `key_metrics_table`。
  - `artifact_index`。
  - `calibration_task_board`。
  - `readiness`。
- 新增 `experiments/run_agent31_deliverable_organization.py`。
- 生成 `deliverables/executive_brief.md`、`deliverables/presentation_outline.md`、`deliverables/key_metrics_table.md`、`deliverables/artifact_index.md` 和 `deliverables/calibration_task_board.md`。

调试发现：

- 项目口径需要区分“30-agent 原型链”和“Agent31 整理层”。因此汇报中应表达为：30-agent 原型链已完成，Agent31 用于组织成果和汇报材料。
- 关键数值表必须保留 0.75 条件恢复和 0.60 回退线的边界说明，避免汇报时误读为永久满负荷运行。

结果：

- `pytest tests/test_deliverable_organization_agent.py -q`：3 passed。
- `run_agent31_deliverable_organization.py`：
  - deliverable_status：`deliverable_pack_ready`。
  - deliverable_score：1.0。
  - 索引文件：23/23 可用。
  - 汇报章节：8 个。
  - 生成执行摘要、PPT 提纲、关键数值表、成果索引和实证校准任务板。

结论：

- 整理阶段已经形成统一成果入口。
- 当前材料可以直接用于项目书摘要、汇报结构和后续 PPT 初稿；下一步可以继续生成正式 PPT/图表，或进入真实现场数据导入与参数校准。

## 图表与汇报素材 Agent 迭代

### 2026-05-31 迭代 1

问题：Agent31 已经生成执行摘要、提纲和关键数值表，但距离正式 PPT/项目书图表还差一层“视觉故事板”和“逐页讲述脚本”。如果直接做 PPT，容易出现图表口径不统一，尤其可能把 0.75 条件恢复误说成永久满负荷。

修复：

- 新增 `PresentationAssetAgent`。
- 输入：
  - Agent31 成果整理报告。
  - Agent29 项目综合报告。
  - Agent30 真实数据接口报告。
- 输出：
  - `slide_specs`：8 页 slide 结构。
  - `visual_assets`：8 个图表素材。
  - `narrative_script`：逐页讲述脚本。
  - `project_book_sections`：项目书章节素材。
- 新增 `experiments/run_agent32_presentation_assets.py`。
- 生成：
  - `deliverables/visual_storyboard.md`
  - `deliverables/figure_specs.md`
  - `deliverables/slide_narrative_script.md`
  - `deliverables/project_book_sections.md`

调试发现：

- 成果索引需要把 Agent32 新增的图表素材也纳入检查，因此 Agent31 同步扩展为读取 `presentation_assets`。
- Agent31 重新运行后，成果索引从 23/23 扩展为 27/27。
- 图表素材中必须保留 `recovery_boundary`，明确 0.75 是条件恢复、0.60 是失败回退线。

结果：

- `pytest tests/test_presentation_asset_agent.py -q`：3 passed。
- `run_agent32_presentation_assets.py`：
  - asset_status：`presentation_assets_ready`。
  - slide_count：8。
  - visual_asset_count：8。
  - 生成视觉故事板、图表规格、逐页讲述脚本和项目书章节素材。
- `pytest -q`：133 passed。

结论：

- 整理阶段已经从“目录索引”推进到“可直接制作 PPT/项目书图表”的素材层。
- 下一步可以基于当前素材生成正式 PPT，或进入真实现场数据导入与参数校准。

### 2026-05-31 迭代 2：整理阶段口径收束

问题：进入整理阶段后，成果包已经包含 Agent32 图表素材，但部分报告仍保留旧口径：Agent32 报告中的 `available_artifacts` 残留 `23/23`，Agent31 成果包统计仍按 31 个 agent 表达；修正后又出现 Agent32 被重复计数为 33 的问题。

修复：

- Agent31 改为根据 manifest 是否包含 `presentation_assets` 动态统计综合/接口/整理/展示层数量。
- Agent32 改为从 Agent31 的 `available_artifact_count` 和 `artifact_count` 推导 `available_artifacts`。
- Agent32 对总 agent 数做去重：当 Agent31 已经把展示层纳入成果包时，不再二次加一。
- 同步更新 `deliverables/key_metrics_table.md`、Agent31 报告、Agent32 报告和当前验证口径。

结果：

- 当前成果包口径：`32` 个 agent。
- 当前成果索引：`27/27` 可用。
- 当前完整回归：`136 passed`。

结论：

- 收束工作已经完成，可以进入正式整理材料、制作 PPT/项目书图表，或转入真实现场数据导入与校准。

## 正式展示包 Agent 迭代

### 2026-05-31 迭代 1

问题：Agent32 已经生成视觉故事板、图表规格和逐页讲述脚本，但还不是可直接交付的正式 PPTX；同时需要显式处理中文字体兼容问题，避免再次出现 Word/PPT 中的乱码或竖排压缩。

修复：

- 新增 `PresentationDeckAgent`，作为 Agent33。
- 将 Agent32 的 `slide_specs` 转换成正式 deck 的 claim spine、设计系统、QA 门槛和输出目标。
- 设计系统明确中文字体策略：`Microsoft YaHei`，并在 QA 中记录 `PingFang SC` 备用口径。
- 生成 `deliverables/deck_claim_spine.md`、`deliverables/deck_design_system.md` 和 `deliverables/deck_qa_checklist.md`。
- 使用 Presentations artifact-tool 生成 `deliverables/ppt/low_cost_water_ai_formal_deck.pptx`。
- 首次预览发现内容被压到左侧，原因不是中文编码，而是 artifact-tool 默认 `1280x720` 像素坐标系与英寸坐标混用；随后加入坐标缩放层并重新导出。
- 将 formal deck 纳入 Agent31 成果索引，成果包从 `27/27` 扩展为 `31/31`。

结果：

- Agent33 deck_status：`formal_deck_plan_ready`。
- 当前链条口径：`33` 个 agent。
- 当前成果索引：`31/31` 可用。
- 当前完整回归：`141 passed`。
- PPTX contact sheet 复核：中文横排正常，恢复边界页保留 `0.75/0.60`，synthetic/sample 边界页保留。

结论：

- 整理阶段已经形成正式可展示 PPTX；后续重点应转向真实现场数据导入、校准与现场试点口径收敛。

## 实证校准门控 Agent 迭代

### 2026-05-31 迭代 1

问题：正式 PPTX 已经生成，但继续在呈现层反复同步口径会拖慢实质研究推进；当前更关键的是把 Agent30 的真实数据接口推进成可以执行、可以验收、可以写回模型参数的现场校准入口。

修复：

- 新增 `FieldCalibrationGateAgent`，作为 Agent34。
- 将 Agent30 的 `field_data_interface` 转换为 G0-G5 现场数据验收门。
- 明确 `synthetic/sample` 只能用于接口演示，不能作为软传感器、催化剂寿命或控制参数校准数据。
- 生成 P0-P5 校准顺序：现场快照、传感噪声漂移、软传感器重训、催化剂寿命、循环时间预算、成本部署接口。
- 生成 R1-R4 运行手册：采集最小现场数据包、运行验收门、写回模型参数、形成现场校准审计包。
- 将 Agent34 的三份校准文件和报告纳入 Agent31 成果索引。

结果：

- Agent34 gate_status：`calibration_protocol_ready_waiting_for_field_data`。
- 当前门控：5/6 通过，阻塞门为 `G0_data_origin`。
- 当前成果索引：`35/35` 可用。
- 当前完整回归：`145 passed`。

结论：

- PPTX 已冻结为 Agent33 快照；后续除非明确要求视觉修改，否则不再消耗时间做呈现打磨。
- 当前研究主线转入真实现场数据导入与校准：先通过 G0-G2 最小现场包，再按 P1-P5 写回数据质控、软传感、催化剂寿命、循环时间预算和成本部署参数。

## 模型真实性审计 Agent 迭代

### 2026-06-01 迭代 1

问题：用户明确指出 PPT 和 Word 只是表达层，项目重心应回到模型本身：知识库是否足够、软传感和闭环控制是否贴近真实问题、能否借鉴科学研究 skill / workflow 来提升现实意义。

修复：

- 新增 `ModelRealismAuditAgent`，作为 Agent35。
- 将知识库条目扩展为带 `evidence_stage`、`field_validation_need` 和 `source_basis` 的结构。
- 新增 PFAS/持久性微污染物、重金属/形态控制、生化尾水/营养盐等更现实污染场景知识条目。
- 新增 `experiments/run_agent35_model_realism_audit.py`。
- 生成：
  - `deliverables/model_realism_audit.md`
  - `deliverables/model_upgrade_backlog.md`
  - `outputs/agent35_model_realism_audit/agent35_report.md`
- 将 Agent35 纳入成果索引，成果包从 35/35 扩展为 38/38。

调试发现：

- 新增知识条目一开始过于宽泛，导致低基质传感故障误触发 PFAS/重金属类预处理偏置，也让催化剂失活场景的动作顺序偏离原安全逻辑。
- 随后收紧 PFAS、重金属和生化尾水条目的触发条件，使其必须有更明确状态组合才会进入控制偏置。

结果：

- Agent35 realism_status：`simulation_baseline_needs_field_grounding`。
- 知识库条目数：9。
- 当前成果索引：38/38 可用。
- 当前完整回归：149 passed。

结论：

- 当前模型仍应被表述为仿真基线，不是现场自治系统。
- 后续最重要的优化顺序是：真实数据 G0-G2 验收、软传感不确定性/校准曲线/OOD 风险门、知识图谱证据矩阵、参数化过程动力学。

## 软传感不确定性验证 Agent 迭代

### 2026-06-01 迭代 1

问题：Agent35 已把软传感不确定性列为模型真实性短板；如果只看 MAE/R2，仍无法回答“预测什么时候不可信”“放行概率是否校准”“外推样本是否应该被拦截”。

修复：

- 为 `SoftSensorAgent` 增加 `soft_sensor_uncertainty`、预测区间、OOD 风险、模型-启发式分歧和区间宽度。
- 将不确定性写入 `release_readiness` 和 agent confidence，避免高不确定性时仍乐观放行。
- 新增 `SoftSensorUncertaintyValidationAgent`，作为 Agent36。
- 在 synthetic holdout 上检查 prediction interval coverage、mean abs error、高低不确定性误差差异、OOD 警报和放行阻断。
- 生成：
  - `deliverables/soft_sensor_uncertainty_validation.md`
  - `outputs/agent36_soft_sensor_uncertainty_validation/agent36_report.md`
  - `outputs/soft_sensor_training/soft_sensor_uncertainty_metrics.json`

结果：

- Agent36 uncertainty_validation_status：`synthetic_uncertainty_layer_ready_needs_field_holdout`。
- overall_interval_coverage：1.0。
- mean_abs_error：0.0613。
- uncertainty_tracks_error：True。
- 当前成果索引：41/41 可用。
- 当前完整回归：153 passed。

结论：

- 不确定性层已经能作为 synthetic 内部风险门，但不能替代 field validation。
- 下一步必须用真实离线标签做 field holdout、release probability calibration 和 conformal calibration。

## 知识图谱策展 Agent 迭代

### 2026-06-01 迭代 1

问题：用户进一步强调，知识库不能只是堆论文或机制条目，而要升级为 Scientific Knowledge Graph 式的可推理结构；多智能体也不能只是分工多，而要有文献证据、机制迁移、不确定性验证和现场现实性的科学审查链。

修复：

- 新增 `KnowledgeGraphCurationAgent`，作为 Agent37。
- 将现有知识库整理为七类轴：污染物、基质、材料、过程条件、可观测低成本信号、隐藏状态和证据等级。
- 输出每条知识边的 `claim_boundary`，强制区分 literature/simulation/field。
- 定义科学审查链：`LiteratureEvidenceAgent`、`KnowledgeGraphCurationAgent`、`MechanismBorrowingAgent`、`UncertaintyValidationAgent`、`FieldRealismAgent`。
- 新增 KG backlog：field-supported edges、系统综述抽取 schema、原始信号到隐藏状态证据边、污染物轴扩展和过程条件轴扩展。
- 生成：
  - `deliverables/knowledge_graph_curation.md`
  - `deliverables/knowledge_graph_schema.md`
  - `outputs/agent37_knowledge_graph_curation/agent37_report.md`
  - `outputs/agent37_knowledge_graph_curation/knowledge_graph_records.json`

结果：

- Agent37 kg_curation_status：`scientific_kg_seed_needs_literature_and_field_evidence`。
- axis_coverage_score：0.700。
- field_supported_entry_count：0。
- 当前成果索引：45/45 可用。
- 当前完整回归：156 passed。

结论：

- 知识库已经从条目清单推进到可审查的 KG seed。
- 目前仍不能把 KG 边写成现场实证结论；下一步应补真实 field-supported KG edges、文献证据抽取和原始低成本信号到隐藏状态的可校准边。

## 文献证据抽取 Agent 迭代

### 2026-06-01 迭代 1

问题：Agent37 已经把知识库整理成 KG seed，但仍缺“文献 claim -> 模型升级”的结构化抽取层。如果没有这一层，后续容易回到堆论文摘要，无法说明借鉴来源、现实问题映射、数据需求、实现方式、评价指标和失败边界。

修复：

- 新增 `LiteratureEvidenceAgent`，作为 Agent38。
- 建立 8 条文献 seed evidence records，覆盖：
  - 多智能体催化剂发现与专家知识图谱审查。
  - WWTP 软传感综述。
  - 生物/AOP 废水动态建模、控制和在线监测综述。
  - conformal prediction / distribution-free uncertainty。
  - Scientific KG in AI for Science。
  - 抗生素、染料、农药 AOP 处理综述。
- 每条 evidence record 强制包含：
  - `extracted_claim`
  - `borrowed_idea`
  - `project_mapping`
  - `data_requirements`
  - `implementation_path`
  - `evaluation_metrics`
  - `failure_boundary`
- 新增模型升级映射：
  - `soft_sensor_field_conformal_calibration`
  - `grey_box_dynamic_control_latency`
  - `scientific_kg_field_supported_edges`
  - `pollutant_specific_process_axes`
- 生成：
  - `deliverables/literature_evidence_matrix.md`
  - `deliverables/literature_evidence_schema.md`
  - `outputs/agent38_literature_evidence/agent38_report.md`
  - `outputs/agent38_literature_evidence/literature_evidence_records.json`

结果：

- Agent38 literature_evidence_status：`literature_seed_ready_field_validation_required`。
- seed records：8。
- kg_gap_closure_score：0.889。
- 已覆盖 KG 缺失污染物轴：染料、抗生素、农药。
- 剩余 KG 缺口：过程条件轴的温度。
- Agent38 迭代完成时成果索引：49 项中 49 项可用。
- Agent38 迭代完成时完整回归：159 项测试通过。

结论：

- 文献证据已经从摘要层推进到模型升级 contract 层。
- 这些记录只能作为 literature seed；下一步不能直接写回参数，而应推进 field holdout、保形校准、动态控制延迟建模和 field-supported KG edges。

## 软传感保形校准 Agent 迭代

目标：

- 把 Agent36 的 synthetic holdout 不确定性验证继续推进为可审计的 split conformal 校准接口。
- 明确每个隐藏状态目标的非一致性阈值、覆盖率、区间宽度、放行 abstention 和 OOD 风险。
- 保持最初边界：synthetic/sample 只能作为仿真基线，不能写入真实放行门。

实现：

- 新增 `SoftSensorConformalCalibrationAgent`，读取验证记录中的目标绝对误差并按 calibration/evaluation split 计算 conformal thresholds。
- 新增 `experiments/run_agent39_soft_sensor_conformal_calibration.py`，生成 `deliverables/soft_sensor_conformal_calibration.md`、`outputs/agent39_soft_sensor_conformal_calibration/agent39_report.md` 和 `outputs/soft_sensor_training/soft_sensor_conformal_metrics.json`。
- 更新成果整理 Agent，使 Agent31 能把软传感保形校准纳入成果索引和支持层 agent 统计。
- 新增回归测试覆盖 synthetic 边界、低覆盖 field 告警、真实 field 达标写回条件和成果整理索引。

关键迭代点：

- 初版测试样例人为制造了 calibration/evaluation 分布漂移，导致“良好覆盖”测试失败。
- 没有降低 agent 的覆盖率门槛，而是修正测试 fixture，使其满足 exchangeability 假设；这样保留了 conformal calibration 的科学边界。

结果：

- Agent39 conformal_status：`synthetic_conformal_interface_ready_needs_field_holdout`。
- overall_conformal_coverage：0.975。
- mean_conformal_interval_width：0.233。
- release_abstention_rate：0.125。
- can_write_to_release_gate：False。
- Agent39 迭代完成时成果索引：52/52 可用。
- Agent39 迭代完成时完整回归：162 passed。

结论：

- 软传感不确定性层已经从“有区间”推进到“有保形校准接口”。
- 当前结果仍只是 synthetic holdout 上的接口验证；下一步必须用真实 field holdout 重算阈值，并检查 catalyst_activity、matrix_interference 等弱目标是否需要分场景或条件化保形校准。

## 灰箱动态延迟审计 Agent 迭代

目标：

- 把 `grey_box_dynamic_control_latency` 从文献证据矩阵中的升级方向落成可运行 agent。
- 检查循环式结构是否真的为低频传感、离线检测、人工复核和执行器动作争取了足够时间。
- 坚持边界：synthetic replay 只能做延迟预算基线，不能证明现场 PLC/人工/检测排队条件下可执行。

实现：

- 新增 `GreyBoxDynamicLatencyAgent`，按场景计算 observation latency、control action latency、release evidence latency、loop time credit、action/evidence margin 和 latency pressure。
- 新增 `experiments/run_agent40_grey_box_dynamic_latency.py`，生成 `deliverables/grey_box_dynamic_latency.md`、`outputs/agent40_grey_box_dynamic_latency/agent40_report.md` 和 `outputs/grey_box_dynamic_latency/latency_budget_metrics.json`。
- 将 Agent40 接入成果整理 Agent，使 Agent31 能索引灰箱动态延迟审计并把工作链更新到 40 个 agent。
- 新增测试覆盖 synthetic 边界、field timestamped ready 条件和现场动作过慢的阻断逻辑。

结果：

- Agent40 latency_status：`synthetic_latency_budget_ready_needs_field_timestamps`。
- latency_budget_violation_rate：0.200。
- minimum_evidence_margin_min：-31.0。
- minimum_action_margin_min：43.0。
- 问题场景：`matrix_shock` 的慢证据延迟为 115 min，但循环时间信用为 84 min。
- 当前成果索引：55/55 可用。
- 当前完整回归：166 passed。

结论：

- 循环式结构确实能降低多数场景对高速传感和高速反应的要求，但不能无限降低；`matrix_shock` 仍需要快代理信号、自动预处理/切换单元或更长暂存窗口。
- 下一步应采集现场 timestamped campaign replay，把采样、检测、人工复核、执行器和回流时间戳写入数据接口，再判断延迟预算能否进入 release gate。

## 基质冲击快代理与延迟感知控制 Agent 迭代

目标：

- 针对 Agent40 暴露的 `matrix_shock` 慢证据余量 -31 min，做真正的模型修复，而不是只记录缺口。
- 用 EC、浊度、UV254、pH 和 ORP 原始低成本信号形成快代理，在离线检测结果回来前触发保护性预处理/切换。
- 保持边界：快代理只允许保护性控制，不允许自动放行。

实现：

- 新增 `MatrixShockFastProxyAgent`，输出 proxy_score、specificity_guard、protective_triggered、release_block、保护动作余量和误触发验证需求。
- 将快代理接入 `ControlStrategyAgent`，触发后提升 `switch_or_pretreat`，延长 `hold_for_validation`，并把 release policy 固定为 `block_release_until_lab_and_field_conformal_calibration`。
- 新增 `experiments/run_agent41_matrix_shock_fast_proxy.py`，生成 `deliverables/matrix_shock_fast_proxy_control.md`、`outputs/agent41_matrix_shock_fast_proxy/agent41_report.md` 和 `outputs/matrix_shock_fast_proxy/fast_proxy_metrics.json`。
- 新增测试覆盖 matrix_shock 触发、clean/oxidant 场景不触发、控制策略接入和成果索引。

结果：

- Agent41 fast_proxy_status：`synthetic_fast_proxy_ready_needs_field_timestamp_validation`。
- matrix_shock proxy_score：0.559。
- specificity_guard_score：0.633。
- protective_action_margin_min：59.0。
- 原 evidence margin：-31.0。
- 延长暂存后 projected evidence margin：14.0。
- baseline_hold_min：35。
- adapted_hold_min：90。
- adapted_release_policy：`block_release_until_lab_and_field_conformal_calibration`。
- Agent41 迭代完成时成果索引：58/58 可用。
- Agent41 迭代完成时完整回归：170 passed。

结论：

- 这次改动的边际价值高于展示收束：它把 `matrix_shock` 的核心工程缺口从“慢证据赶不上”改造成“快代理先保护，慢证据只负责放行和校准”。
- 下一步不应继续美化材料，而应做 timestamped campaign replay 字段扩展和现场 precision/recall/误触发成本校准。

## 现场时间戳回放接口 Agent 迭代

目标：

- 接续 Agent41 的核心边界：快代理已经能提前触发保护性控制，但 synthetic 结果不能证明现场有效。
- 把 sensor、lab、operation 和 fast_proxy_event_log 放到同一 batch 时间轴，用真实 timestamped replay 校准 precision、recall、提前量和误触发成本。
- 坚持原始目的：循环式结构是为了给低成本传感、软传感和多智能体诊断争取时间，不是为了用展示材料掩盖现场数据缺口。

实现：

- 新增 `TimestampedCampaignReplayAgent`，定义 `sensor_timeseries`、`offline_lab_results`、`campaign_operation_log` 和 `fast_proxy_event_log` 四张时间戳回放表。
- 扩展 `FieldDataInterfaceAgent` 可选字段：`acquisition_time_min`、`ingest_time_min`、`result_time_min`、`turnaround_min`、`command_time_min`、`effect_time_min`、`fast_proxy_score` 和 `release_policy`。
- 新增 `experiments/run_agent42_timestamped_campaign_replay.py`，生成 `deliverables/timestamped_campaign_replay_schema.md`、`outputs/agent42_timestamped_campaign_replay/agent42_report.md`、`outputs/timestamped_campaign_replay/timestamped_replay_schema.json`、模板和 synthetic 时间戳样例包。
- 新增测试覆盖 synthetic 只可作为接口、field replay 达标写回条件、缺失 result_time 阻断和 precision/recall 失败阻断。

结果：

- Agent42 timestamped_replay_status：`synthetic_timestamp_schema_ready_needs_field_replay`。
- timestamp_coverage：1.0。
- proxy_label_count：12。
- proxy_precision：1.0。
- proxy_recall：1.0。
- mean_protective_action_lead_time_min：84.0。
- p90_lab_turnaround_min：80.0。
- p90_actuator_latency_min：10.0。
- can_calibrate_fast_proxy：False。
- can_write_to_protective_control：False。
- 当前成果索引：63/63 可用。
- 当前完整回归：175 passed。

结论：

- 这一步的边际价值高：它没有继续做展示收束，而是把 Agent41 的“快代理保护性控制”推进到可现场验证的 replay 数据接口。
- 现在最重要的下一步是采集真实 field-labeled timestamped campaign replay，用 precision、recall、提前量和误触发成本决定快代理能否从 synthetic 原型进入现场保护性控制。

## 现场回放校准门控 Agent 迭代

目标：

- 把 Agent42 的 replay 指标从“可计算”推进到“能否写回控制”的硬门控。
- 防止 synthetic replay、低 precision/recall、时间戳不完整或误触发成本过高的结果被误写入 matrix_shock 快代理。
- 保持边界：G6/P6 通过也只允许写入保护性控制，不能写入自动放行门。

实现：

- 新增 `FieldReplayCalibrationGateAgent`，作为 Agent43。
- 建立 G6/P6 验收门，覆盖：
  - field origin。
  - 时间戳 schema 和 timestamp coverage。
  - sensor/lab/operation/proxy batch 回连。
  - proxy label 数。
  - precision/recall。
  - protective action lead time 和 actuator P90 latency。
  - false positive cost。
  - release gate 永久禁止写回。
- 新增 `experiments/run_agent43_field_replay_calibration_gate.py`，生成 `deliverables/field_replay_calibration_gate.md`、`outputs/agent43_field_replay_calibration_gate/agent43_report.md` 和 `outputs/field_replay_calibration_gate/g6_p6_gate_metrics.json`。
- 更新成果整理 Agent，使 Agent31 能索引 Agent43，并把 P6 时间戳回放与快代理校准加入实证校准任务板。
- 新增测试覆盖 synthetic 阻断、field replay 达标只允许保护性写回、低 precision/误触发成本失败、缺失 result_time schema 失败和执行器过慢失败。

结果：

- Agent43 field_replay_gate_status：`synthetic_replay_gate_blocked`。
- accepted_gates：7/8。
- failed_gate_ids：[`G6_1_field_origin`]。
- can_write_to_protective_control：False。
- can_write_to_release_gate：False。
- writeback_mode：`blocked_until_field_replay_passes_g6`。
- 当前成果索引：66/66 可用。
- 当前完整回归：181 passed。

结论：

- 这次改动的边际价值高：它把“快代理是否能进现场控制”从口头边界变成可测试、可报告、可阻断的 G6/P6 门。
- 下一步的核心工作不是展示，而是导入真实 field-labeled timestamped replay，让 Agent43 决定是否允许把 matrix_shock 快代理写入保护性控制。

## 现场 replay 包导入门 Agent 迭代

目标：

- 回应“边际价值优先”的要求，把工作从展示收束转向模型真实性入口。
- 在 Agent42/43 之前增加真实现场 replay 包导入门，防止 synthetic/sample 数据或字段类型错误的数据进入 G6/P6。
- 保持最初目的：低成本传感、软传感和循环结构必须服务于真实工程可校准性，而不是只做形式化多 agent。

实现：

- 新增 `FieldReplayImportAgent`，作为 Agent44。
- 建立 metadata provenance、field origin、四张 CSV 必需字段、数字/布尔类型转换和 batch 回连验收。
- 新增 `load_field_replay_package`，可读取带 `metadata.json` 的现场 replay 包。
- 新增 `experiments/run_agent44_field_replay_import.py`，生成 `deliverables/field_replay_import_protocol.md`、`outputs/agent44_field_replay_import/agent44_report.md`、`outputs/field_replay_import/import_acceptance_metrics.json` 和 `outputs/field_replay_import/import_schema.json`。
- 更新成果整理 Agent，使 Agent31 能索引 Agent44，并新增 P7 现场 replay 包导入任务。
- 新增测试覆盖 synthetic origin 阻断、真实包进入 Agent42/43、缺失 metadata、缺失表、数字/布尔类型错误和 CSV 包加载。

结果：

- Agent44 field_replay_import_status：`field_replay_import_blocked_non_field_origin`。
- accepted_tables：4/4。
- can_pass_to_timestamped_replay：False。
- can_pass_to_g6：False。
- can_write_to_protective_control：False。
- 当前成果索引：71/71 可用。
- 当前完整回归：188 passed。

结论：

- 这次改动的边际价值很高：它把“真实数据怎么进入模型”从口头要求变成可执行、可测试、可阻断的入口门。
- 下一步应导入真实 field metadata 与 CSV replay 包，通过 Agent44 后再让 Agent42/43 计算快代理是否可进入保护性控制。

## 现场 replay 校准证据链 Agent 迭代

目标：

- 继续以模型真实性为核心，不做展示层美化。
- 把 Agent44 导入门、Agent42 时间戳回放和 Agent43 G6/P6 串成一条不可绕过的现场校准证据链。
- 防止用户或脚本单独运行 Agent42/43 后误把 synthetic/sample 或未验收数据当作现场保护性写回依据。

实现：

- 新增 `FieldReplayEvidenceChainAgent`，作为 Agent45。
- 证据链顺序固定为 Agent44 -> Agent42 -> Agent43；Agent44 未通过时不运行 downstream replay。
- 完整链条通过时只生成 `field_protective_control_parameter_update` 候选，仍要求人工复核，且 `can_write_to_release_gate=False`。
- 新增 `experiments/run_agent45_field_replay_evidence_chain.py`，生成 `deliverables/field_replay_evidence_chain.md`、`outputs/agent45_field_replay_evidence_chain/agent45_report.md` 和 `outputs/field_replay_evidence_chain/evidence_chain_metrics.json`。
- 更新成果整理 Agent，使 Agent31 能索引 Agent45，并新增 P8 现场 replay 证据链任务。
- 新增测试覆盖 synthetic import 阻断、缺失 Agent44 阻断、field 包完整通过形成保护性候选、G6 失败阻断和 release gate 边界保持。

结果：

- Agent45 field_replay_evidence_chain_status：`field_replay_evidence_chain_blocked_at_import`。
- import_ready：False。
- timestamped_replay_ready：False。
- g6_ready：False。
- can_emit_protective_writeback_candidate：False。
- can_write_to_release_gate：False。
- 当前成果索引：74/74 可用。
- 当前完整回归：194 passed。

结论：

- 这次改动的边际价值高：它把“真实数据通过后如何形成控制候选”的流程从分散脚本变成可审计证据链。
- 下一步应导入真实 field replay 包，让 Agent45 形成完整链条判断；在此之前，synthetic/sample 仍只能作为接口联调。

## 软传感 field holdout 放行门控 Agent 迭代

目标：

- 继续以模型真实性为核心，不做展示层美化。
- 把 Agent36 软传感不确定性验证和 Agent39 split conformal 校准接成 release gate 硬门控。
- 防止 synthetic holdout 指标被误写入闭环放行逻辑。

实现：

- 新增 `SoftSensorFieldHoldoutGateAgent`，作为 Agent46。
- 建立 SFG0-SFG6 门控：field holdout 来源、记录量、区间覆盖率、区间宽度、abstention/OOD、弱目标覆盖和场景多样性。
- 通过门控时只形成 `field_holdout_calibrated_interval_threshold_candidate`，仍要求人工复核和离线检测确认，且 `can_auto_release_treated_water=False`。
- 新增 `experiments/run_agent46_soft_sensor_field_holdout_gate.py`，生成 `deliverables/soft_sensor_field_holdout_gate.md`、`outputs/agent46_soft_sensor_field_holdout_gate/agent46_report.md` 和 `outputs/soft_sensor_field_holdout_gate/field_holdout_gate_metrics.json`。
- 更新成果整理 Agent，使 Agent31 能索引 Agent46，并新增 P9 软传感 field holdout 放行门控任务。
- 新增测试覆盖 synthetic 阻断、field 指标通过、弱目标/OOD 失败、场景多样性失败和 release gate 自动放行边界。

结果：

- Agent46 soft_sensor_field_holdout_gate_status：`soft_sensor_release_gate_blocked_non_field_holdout`。
- failed_check_ids：[`SFG0_field_holdout_origin`, `SFG5_weak_target_coverage`]。
- can_write_to_release_gate：False。
- can_auto_release_treated_water：False。
- 当前成果索引：77/77 可用。
- 当前完整回归：199 passed。

结论：

- 这次改动的边际价值高：它把“软传感器是否能参与放行门”从概念边界变成可测试、可阻断、可审计的 field holdout 门控。
- 当前 Agent36/Agent39 的 synthetic holdout 只能证明接口可运行；真实 field holdout 通过 Agent36 -> Agent39 -> Agent46 后，也只形成 release gate 校准候选，不能直接授权自动放行。

## 弱目标分层保形校准 Agent 迭代

目标：

- 继续围绕模型真实性推进，不做展示层美化。
- 回应 Agent46 暴露的 `SFG5_weak_target_coverage`：总体 conformal coverage 不能掩盖 `matrix_interference` 和 `catalyst_activity` 的弱目标风险。
- 把弱目标 coverage 做成 target/scenario 分层审查，只生成候选并交给 Agent46，不绕过 release gate。

实现：

- 新增 `WeakTargetStratifiedConformalAgent`，作为 Agent47。
- 建立 WTC0-WTC5 门控：field holdout 来源、弱目标评估量、弱目标 coverage、候选区间宽度、场景分层支持和 release gate 边界。
- 新增 `experiments/run_agent47_weak_target_stratified_conformal.py`，生成 `deliverables/weak_target_stratified_conformal.md`、`outputs/agent47_weak_target_stratified_conformal/agent47_report.md` 和 `outputs/weak_target_stratified_conformal/weak_target_stratified_metrics.json`。
- 更新成果整理 Agent，使 Agent31 能索引 Agent47，并新增 P10 弱目标分层保形校准任务。
- 新增测试覆盖 synthetic 阻断、field 候选只交给 Agent46、弱目标失败、release gate 边界保持。

结果：

- Agent47 weak_target_stratified_status：`weak_target_stratified_synthetic_candidate_needs_field_holdout`。
- 最弱目标：`matrix_interference`，coverage：0.875。
- failed_check_ids：[`WTC0_field_holdout_origin`, `WTC2_weak_target_coverage`]。
- can_pass_candidate_to_agent46：False。
- can_write_to_release_gate：False。
- 当前成果索引：80/80 可用。
- 当前完整回归：204 passed。

结论：

- 这次改动的边际价值高：它把“总体 coverage 好看但弱目标不稳”的问题变成可测试、可追踪、可阻断的分层校准链。
- 下一步应采集真实 field holdout 标签，按 Agent36 -> Agent39 -> Agent47 -> Agent46 顺序重跑；Agent47 修复弱目标分层 coverage 后，Agent46 才能判断是否形成 release gate 校准候选。

## 管网布点与稀疏感知 Agent 迭代

目标：

- 暂缓现场 replay 证据链等收束工作，优先服务模型核心。
- 把“进水装一个、出水装一个，中间全黑箱”的思路升级为管网/处理单元节点上的稀疏感知问题。
- 构建 node-modality by hidden-state 观测矩阵，为软传感器、故障分类和低延迟控制提供状态入口。

实现：

- 新增 `SensorNetworkSparsePlacementAgent`，作为 Agent48。
- 建立 10 个观测轴：污染物残留、反应完成度、氧化剂、催化剂活性、基质干扰、水力、故障分类、控制延迟、软传感重构和成本效率。
- 将进水、均质池、反应器中段、催化剂床出水、回流环、抛光入口和出水作为候选节点。
- 将 pH、ORP、EC、浊度、UV254、流量和温度作为候选传感模态。
- 用边际效用选择少量 node-modality 布点，并输出软传感接口所需的 node_id、zone、modality、observation vector 和 missingness mask。

结果：

- sparse_placement_status：`sparse_sensor_layout_ready_needs_field_topology`。
- selected_sensor_count：6。
- matrix_shape：6x10。
- total_cost_index：4.176。
- weak_state_coverage：0.300。
- 推荐候选包括回流环 UV254、催化剂床出水浊度、反应器中段 ORP、进水 EC、均质池流量和抛光入口浊度。

结论：

- 这次改动边际价值高：它把“低成本传感怎么布”从泛泛讨论变成了可运行、可测试、可传给软传感器的观测矩阵。
- 关键发现是 `catalyst_activity` 仍然不可充分观测，说明后续必须补催化剂床附近的真实节点标签或更贴近催化剂状态的低成本代理信号。

## 多设施协同控制与策略蒸馏 Agent 迭代

目标：

- 吸收“污水系统多设施协同优化”示例中真正有用的结构：环境交互模型、多 agent 协同控制、共享经验池、联合奖励函数和决策树蒸馏。
- 不强行套用泵站水位/泵站调度目标，而是迁移到本项目的均质池、反应核心、催化剂床、回流环和末端精处理协同控制。
- 继续坚持 synthetic 阶段不写执行器、不写放行门。

实现：

- 新增 `MultiFacilityCollaborativeControlAgent`，作为 Agent49。
- 将 Agent48 的稀疏观测矩阵转成 5 个 facility agent 的 state vector。
- 生成 5 个联合动作候选：基质冲击削峰回流、反应完成度恢复、催化剂保护、末端精处理/放行门控和低成本保守暂存。
- 建立联合奖励函数，显式包含水质安全、风险削减、延迟收益、现场证据、可解释性、成本能耗、药耗和弱状态惩罚。
- 构建共享经验池 schema，要求记录 batch_id、timestamp、facility_agent_id、state_vector、joint_action、reward、lab label、operator override 和 actuator result。
- 用 ID3 风格规则树蒸馏协同策略，形成现场可审查的规则草案。

结果：

- coordination_status：`synthetic_collaborative_policy_needs_field_replay`。
- facility agent 数量：5。
- 候选联动动作：5。
- distilled_policy_accuracy_proxy：0.794。
- can_write_to_actuator：False。
- can_write_to_release_gate：False。
- 当前成果索引：95/95 可用。
- 当前完整回归：219 passed。

结论：

- 这次改动边际价值高：它把“多 agent 协作”从分工叙事推进到可执行的多设施状态-动作-奖励结构。
- 当前 Agent49 只是协同控制候选和解释草案；下一步必须采集真实多节点 sensor/lab/operation/action replay，校准 joint_action_accuracy、reward_regret、误动作成本和决策树蒸馏准确度。

## 模型核心优化治理 Agent 迭代

目标：

- 把用户多次打断形成的“模型核心优先、展示层降级、自我打断评估”固化为可运行治理层。
- 避免后续继续把边际价值耗在 PPT、Word、索引或展示材料上。
- 在进入 Agent48/Agent49 下一轮算法升级前，先建立统一的边际价值排序和外部方法 evidence matrix。

实现：

- 新增 `ModelCoreOptimizationGovernanceAgent`，作为 Agent50。
- 读取 manifest、Agent48 稀疏布点指标、Agent49 协同控制指标、外部 evidence matrix 和当前 backlog。
- 输出 priority_ranking、low_priority_backlog、blocked_reasons、recommended_next_core_action、self_interrupt_verdict 和 governance_scorecard。
- scoring 字段固定为 `model_core_relevance`、`downstream_chain_impact`、`scientific_value`、`engineering_feasibility`、`verification_readiness`、`avoid_presentation_bias` 和 `marginal_value_score`。
- 外部 evidence matrix 覆盖 PySensors 稀疏布点、WNTR/EPANET 风格图拓扑、WaterTAP/QSDsan/Pyomo 工程建模、科研 agent skill、模型验证 skill 和用户提供的多设施协同优化启发。
- 成果整理 Agent 已识别 Agent50，并把 P13 “模型核心优化治理与自我打断”加入任务板。

结果：

- self_interrupt_verdict：`continue_core_work`。
- 最高边际价值任务：`P1_agent48_comparable_sparse_sensor_placement`。
- blocked_reasons：catalyst_activity weak observability、Agent49 still synthetic_collaborative_policy_needs_field_replay。
- PPT、Word、索引和展示美化进入 low-priority backlog。
- 针对性回归：27 passed。
- 完整回归：219 passed。

结论：

- 这次改动不是展示收束，而是把“下一步做什么”的判断机制固定为模型核心治理层。
- 下一步应按 Agent50 排序，优先把 Agent48 从启发式布点升级为可比较稀疏布点优化，并同步设计 catalyst_activity 代理观测；随后再把 Agent49 升级为 replay-ready 离线评估框架。

## Agent48 可比较稀疏布点优化迭代

目标：

- 按 Agent50 的最高优先级，把 Agent48 从单一启发式布点升级为可比较的 sparse sensor placement 框架。
- 不盲目安装外部库，先借鉴 PySensors SSPOR/SSPOC、QR/GQR/D-optimal、图拓扑监测布点和鲁棒成本约束思想，在本项目内部形成可测试基线。

实现：

- Agent48 新增 `algorithm_comparison`，同时比较：
  - `greedy_marginal`：当前加权边际覆盖基线。
  - `reconstruction_qr_proxy`：SSPOR/QR-style 重构代理。
  - `classification_sspoc_proxy`：SSPOC-style 故障分类代理。
  - `topology_robust_cost_proxy`：图拓扑鲁棒和成本约束代理。
- 新增 process-unit topology graph，显式包含进水、均质池、反应器、催化剂床、回流环、抛光入口和出水之间的边。
- soft sensor interface 新增 `selected_strategy_id`、`layout_id` 和 `missingness_mask_contract`，为后续软传感 node-modality/missingness 耦合做准备。
- Agent50 已能识别 Agent48 是否已经有可比较布点基线；当 P1 baseline 存在时，自动把下一步推荐切换到 P2 catalyst_activity 弱观测代理。

结果：

- selected_strategy：`greedy_marginal`。
- selected_strategy_score：0.726。
- algorithm_comparison top4：greedy 0.726、classification 0.694、reconstruction 0.692、topology robust 0.622。
- weak_state_coverage：0.300。
- total_cost_index：4.176。
- Agent50 recommended_next_core_action 已切换为 `P2_catalyst_activity_weak_observability_proxy`。
- 完整回归：222 passed。

结论：

- 这一步把 Agent48 的核心从“我选了几个传感器”推进到“不同布点目标之间可比较、可解释、可测试”。
- 关键暴露没有消失：即使引入多策略比较，`catalyst_activity` 仍然弱观测，说明下一步不应继续打磨布点框架，而应设计催化剂活性代理信号和相关验证指标。

## Agent51 催化剂活性代理观测迭代

目标：

- 按 Agent50 在 Agent48 升级后的最高边际价值排序，处理 `catalyst_activity` 弱观测问题。
- 不继续泛泛说“催化剂活性不可观测”，而是把它拆成可被低成本传感和慢证据共同支撑的代理观测。
- 保持边界：synthetic proxy design 只能作为设计先验，不能解除 Agent49 的执行器或 release gate 保护规则。

实现：

- 新增 `CatalystActivityProxyAgent`，作为 Agent51。
- 从 Agent48 的 selected node-modality 计划读取当前可用信号，构建催化剂活性 proxy catalog：
  - 催化剂床前后 UV254 去除率。
  - 催化剂床前后 ORP 衰减/利用。
  - 浊度与压降共同表示的污堵代理。
  - 再生前后响应增益。
  - 停留时间归一化反应速率残差。
- 输出 `proxy_feature_table`、`proxy_metrics`、`readiness` 和 `agent49_interface`。
- 将 Agent50 升级为可读取 Agent51 指标：当 Agent51 synthetic proxy baseline 已形成时，不再继续在 P2 上空转，而是自动把最高边际价值任务切到 P3 Agent49 replay-ready 离线评估。
- 成果整理 Agent 已识别 Agent51，并在实证校准任务板新增 P14 `catalyst_activity_proxy`。

结果：

- catalyst_proxy_status：`synthetic_catalyst_proxy_design_ready_needs_field_labels`。
- current_proxy_observability：0.331。
- proxy_observability_after_recommended_patch：0.720。
- weak_state_coverage_after_proxy_design：0.720。
- synthetic_proxy_label_mae：0.091。
- synthetic_proxy_label_correlation：0.961。
- 推荐补点：`N3_catalyst_bed_outlet:UV254_abs`、`N3_catalyst_bed_outlet:ORP_mV`、`N3_catalyst_bed:pressure_drop_kPa`。
- Agent50 recommended_next_core_action 已切换为 `P3_agent49_replay_ready_offline_evaluation`。
- 成果索引：98/98 可用。
- 定向回归：40 passed。
- 完整回归：228 passed。

结论：

- 这次改动把 `catalyst_activity` 从“软传感弱目标”推进到“有输入契约、代理特征、补点建议、Agent49 接口边界和 field holdout 需求”的模型组件。
- P2 当前不应继续无数据堆叠；除非补入 field_proxy_holdout，否则下一轮最高边际价值是 P3：把 Agent49 多设施协同控制升级成 replay-ready 离线评估框架。

## Agent52 多设施 Replay 离线评估迭代

目标：

- 按 Agent50 在 Agent51 后的最高边际价值排序，处理 Agent49 “只有协同控制候选、缺少 replay-ready 离线评估”的问题。
- 不直接训练 online MARL，也不把 synthetic 决策写进执行器，而是先建立可审计的 state-action-reward replay 合同。
- 借鉴 offline RL / conservative policy evaluation、D4RL 式数据集合同和 VIPER/决策树策略蒸馏思想，把多设施协同控制从静态候选推进到可回放、可比较、可解释的评估层。

实现：

- 新增 `MultiFacilityReplayEvaluationAgent`，作为 Agent52。
- 读取 Agent49 的 facility-state/action 矩阵、Agent51 catalyst proxy 指标和 synthetic replay cases。
- 输出：
  - `replay_schema`：多节点传感、软状态、facility state、joint action、reward components、safety gate、lab outcome 和 policy label 的字段合同。
  - `replay_table`：6 条 synthetic state-action-reward 回放样例。
  - `offline_evaluation_metrics`：joint_action_accuracy、mean_reward_regret、protective false positive cost。
  - `distillation_evaluation`：决策树策略回放准确率和失败样例。
  - `agent49_writeback`：哪些内容可写回为 reward prior / replay schema / metric contract，哪些必须阻断。
- 将 Agent50 升级为可读取 Agent52 指标：当 Agent52 synthetic replay baseline 已形成时，不再继续在 P3 上空转，自动把最高边际价值任务切到 P4 灰箱物理最小增强。
- 将成果整理 Agent 升级为识别 Agent52，并在实证校准任务板新增 P15 `multi_facility_replay_evaluation`。

结果：

- replay_evaluation_status：`synthetic_replay_evaluation_ready_needs_field_replay`。
- replay_case_count：6。
- joint_action_accuracy：0.667。
- mean_reward_regret：0.055。
- protective false positive action cost：0.18。
- 典型问题样例：`R2_catalyst_uncertain_low_proxy`，Agent49 在 catalyst proxy 不确定时触发保护性催化剂动作，但 replay 结果显示可能有误触发成本。
- 允许写回：reward prior、replay schema、offline metric contract。
- 阻断写回：actuator_policy、release_gate_policy、online_MARL_training。
- Agent50 recommended_next_core_action 已切换为 `P4_minimal_grey_box_physics`。
- 成果索引：101/101 可用。
- 完整回归：234 passed。

结论：

- 这次改动把 P3 从“多设施协同控制候选”推进到“有 replay schema、有离线评价指标、有误动作成本、有策略蒸馏回放、有写回边界”的模型核心组件。
- Agent52 让 Agent49 更接近真实工程项目：后续现场数据不是随便导入，而是必须按多节点 state-action-reward replay 合同采集，才能校准 joint_action_accuracy、reward_regret、保护性误触发成本和决策树解释可信度。
- 当前不应继续围绕 P3 空转；没有真实 field replay 前，最高边际价值已转向 P4：把反应动力学、传质限制、催化剂衰减、基质抑制和副产物风险纳入最小灰箱物理机制。

## Agent53 最小灰箱物理机制迭代

目标：

- 按 Agent50 在 Agent52 后的最高边际价值排序，处理 P4 灰箱物理机制缺失问题。
- 不直接引入复杂机理仿真框架，而是先建立可审计、可校准、可写入软传感先验的最小物理层。
- 把停留时间分布、旁路/短流、拟一级反应、基质抑制、催化剂有效活性、氧化剂消耗、质量守恒和副产物风险变成显式指标。

实现：

- 新增 `MinimalGreyBoxPhysicsAgent`，作为 Agent53。
- 新增 `experiments/run_agent53_minimal_grey_box_physics.py`，生成：
  - `deliverables/minimal_grey_box_physics.md`
  - `outputs/agent53_minimal_grey_box_physics/agent53_report.md`
  - `outputs/minimal_grey_box_physics/grey_box_physics_metrics.json`
- Agent53 读取 synthetic 场景状态，输出 `scenario_physics_table`、`readiness`、`calibration_contract` 和 `agent50_writeback`。
- 自我打断修正：初版把旁路/短流误压入质量守恒残差，导致 `max_mass_balance_residual=0.235`。本轮改为显式 `bypass_load_fraction` 和 `converted_load_proxy`，质量守恒残差降为 0，同时保留短流和灰箱残差信号。
- Agent50 已能读取 Agent53 指标：当 P4 synthetic prior 已形成时，下一轮最高边际价值切到 P5 软传感 node-modality/missingness 耦合。
- 成果整理 Agent 已识别 Agent53，并在实证校准任务板新增 P16 `minimal_grey_box_physics`。

结果：

- grey_box_physics_status：`synthetic_grey_box_physics_prior_ready_needs_field_calibration`。
- scenario_count：5。
- mean_grey_box_residual：0.131。
- max_grey_box_residual：0.206。
- max_mass_balance_residual：0.000。
- max_byproduct_risk：0.597。
- physics_violation_rate：0.600。
- violation_scenarios：`reaction_time_insufficient`、`catalyst_deactivation`、`matrix_shock`。
- can_update_soft_sensor_physics_prior：True。
- can_write_to_actuator：False。
- can_write_to_release_gate：False。
- Agent50 recommended_next_core_action 已切换为 `P5_soft_sensor_node_modality_missingness`。
- 成果索引：104/104 可用。
- 定向回归：38 passed。
- 完整回归：240 passed。

结论：

- 这次改动把 P4 从“灰箱物理机制缺口”推进到“有最小 physics prior、有质量守恒检查、有场景残差、有 field 校准合同、有写回边界”的模型核心组件。
- Agent53 当前只能作为 synthetic prior 和结构审计，不能证明现场机理，也不能写执行器或 release gate。
- 下一步不应继续打磨展示或围绕 P4 空转；最高边际价值已转向 P5，把 Agent48 的节点-模态-缺失矩阵真正接进软传感训练和推理链。

## Agent54 软传感矩阵耦合迭代

目标：

- 按 Agent50 在 Agent53 后的最高边际价值排序，处理 P5：软传感训练和推理不知道传感信号来自哪个 node、哪个 zone、哪个 modality，也不知道缺失掩码和 layout id 的问题。
- 不先引入复杂时序模型，而是借鉴 GRU-D 的 missingness mask/time gap 思路、BRITS 的双向缺测一致性、PyPOTS 的缺测 benchmark 组织方式和轻量 missing-value baseline 思路，先把真实工程必需的输入合同固定下来。
- 保持边界：synthetic 缺测压力测试只能证明 schema 和接口，不能证明现场传感污染、通信故障、低频采样或人工维护缺测下的鲁棒性。

实现：

- `SoftSensorAgent` 接收 `sensor_layout_interface`，输出 `layout_context`，并把 layout missingness penalty 与 node-specific gap 纳入不确定性层。
- 新增 `SoftSensorMatrixCouplingAgent`，作为 Agent54。
- 新增 `experiments/run_agent54_soft_sensor_matrix_coupling.py`，生成：
  - `deliverables/soft_sensor_matrix_coupling.md`
  - `outputs/agent54_soft_sensor_matrix_coupling/agent54_report.md`
  - `outputs/soft_sensor_matrix_coupling/soft_sensor_matrix_metrics.json`
- Agent54 输出 `time,node,modality,feature_channel` 软传感输入合同，feature channels 包含 `sensor_value`、`availability_mask`、`time_since_last_observed_min`、`data_quality_score`、`observation_axis_weight` 和 `grey_box_residual_prior`。
- 新增缺测压力测试：完整布局、催化剂床 UV254/ORP 缺失、回流环 flow 延迟、基质冲击 EC/浊度稀疏。
- Agent50 已能读取 Agent54 指标：当 P5 synthetic layout-aware contract 已形成时，下一轮最高边际价值切到 P7 工程执行约束进入 reward 和仲裁。

结果：

- soft_sensor_matrix_status：`synthetic_layout_aware_soft_sensor_contract_ready_needs_field_missingness`。
- layout_id：`greedy_marginal:6x10`。
- layout_contract_score：1.000。
- missingness_robustness_score：0.684。
- live_layout_context_status：`global_modality_fallback_used_for_layout`。
- mask_shape：`[6, 5]`。
- current_model_layout_aware：False。
- missing_layout_terms：`layout_id`、`node_id`、`zone`、`modality`、`availability_mask`、`time_since_last_observed_min`、`grey_box_residual_prior`。
- can_update_soft_sensor_training_schema：True。
- can_write_to_release_gate：False。
- Agent50 recommended_next_core_action 已切换为 `P7_engineering_constraints_in_reward_and_arbitration`。
- 定向回归：15 passed；治理/Agent54 定向回归：12 passed；完整回归：245 passed。

结论：

- 这次改动把 P5 从“软传感和稀疏布点之间只在概念上相关”推进到“有 layout-aware 输入合同、有缺测压力测试、有训练 schema gap、有 Agent50 写回边界”的模型核心组件。
- 最大缺陷不是代码问题，而是数据现实问题：当前 live context 仍使用全局模态 fallback，真实工程必须采集 node-specific sensor values、layout holdout splits 和 field missingness replay。
- 下一步不应继续围绕 P5 堆模型；最高边际价值已转向 P7，把泵阀动作次数、执行器延迟、池容、药剂库存、维护窗口、人工复核时间和误动作成本写入 Agent49 reward 与最终仲裁。

## Agent55 工程执行约束进入 Reward 与仲裁迭代

目标：

- 按 Agent50 在 Agent54 后的最高边际价值排序，处理 P7：工程执行约束还停留在说明文字，没有真正进入 Agent49 reward、CostSafety 和最终 Arbitration。
- 不直接安装或引入重型优化框架，而是先借鉴 Pyomo 的显式约束思想、WaterTAP/QSDsan 的 costing/system boundary、WNTR/EPANET 风格的泵阀/池容/水力约束表达，把工程可执行性转成可消费的约束补丁。
- 保持边界：synthetic 工程约束补丁只能改变候选排序、人工复核和硬阻断，不能写 PLC/SCADA 执行器或 release gate。

实现：

- 新增 `EngineeringExecutionConstraintAgent`，作为 Agent55。
- 新增 `experiments/run_agent55_engineering_execution_constraints.py`，生成：
  - `deliverables/engineering_execution_constraints.md`
  - `outputs/agent55_engineering_execution_constraints/agent55_report.md`
  - `outputs/engineering_execution_constraints/engineering_constraints_metrics.json`
  - `outputs/agent55_engineering_execution_constraints/agent49_engineering_patched_report.md`
- Agent55 把每个 Agent49 joint action 的工程需求拆成：
  - actuator_switch_count
  - actuator_p90_latency_min
  - storage_required_m3
  - chemical_inventory_fraction_required
  - maintenance_window_required_min
  - human_review_required_min
  - energy_cost_index
  - false_positive_cost_index
- `MultiFacilityCollaborativeControlAgent` 现在可读取 `agent49_reward_patch`，将 `engineering_constraint_penalty` 和 `execution_feasibility` 纳入 joint_policy_score。
- `CostSafetyAgent` 现在可读取 `action_constraint_patch`，把工程约束转成 safety_gain、money_cost、time_cost、energy_cost 和 risk_cost 的修正。
- `ArbitrationAgent` 现在可读取 `arbitration_patch`，把工程硬约束动作加入 blocked_actions，并输出 engineering execution field gate 与 hard block gate。
- Agent50 已能读取 Agent55 指标：当 P7 synthetic patch 已形成时，不再围绕工程约束空转，下一轮最高边际价值切到 P6 可推理 KG。

结果：

- engineering_constraints_status：`synthetic_engineering_constraints_reward_patch_ready_needs_plc_scada_and_field_replay`。
- mean_execution_feasibility：0.980。
- hard_blocked_joint_action_count：1。
- reward_patch_coverage：1.000。
- arbitration_patch_coverage：1.000。
- 当前主要硬阻断：`J2_catalyst_protection_before_regeneration`，原因是 `maintenance_window_pressure`。
- Agent49 约束补丁后继续保持 `synthetic_collaborative_policy_needs_field_replay`，策略蒸馏准确度代理值为 0.787。
- Agent50 recommended_next_core_action 已切换为 `P6_reasonable_knowledge_graph_upgrade`。
- 定向回归：34 passed。
- 完整回归：250 passed。

结论：

- 这次改动把 P7 从“工程约束应当考虑”推进到“工程约束已进入 reward、成本安全和最终仲裁”的模型核心组件。
- 当前最重要的缺陷不是缺代码，而是缺 PLC/SCADA 点表、执行器响应日志、池容/液位、药剂库存、维护窗口、人工复核队列和 field state-action-reward execution replay。
- 下一步不应继续围绕 P7 堆规则；最高边际价值已转向 P6，把知识库升级为能约束特征、先验、动作边界和失败解释的可推理 KG。

## Agent56-59 核心复盘、主链回接与现场验证承接

目标：

- 按用户“重新审视前面的 agent、先修最根基问题、按边际价值承接修改”的要求，停止流程图/展示工作，回到模型核心。
- 先解决知识库是否真正参与机理/控制，再解决核心 prior 是否进主链，之后把 KG 验证需求落到真实数据接口，最后生成每条 claim 的必采字段矩阵和 source_basis 补全任务。

实现：

- 新增 Agent56 `KnowledgeGraphReasoningAgent`，生成 typed KG evidence paths、action constraint patch、field_validation_queue 和 agent_chain_retrospective。
- 新增 Agent57 `MainChainReconnectionAgent`，审计 Agent53 灰箱 prior、Agent54 布点/缺测合同、Agent55 工程约束、Agent56 KG patch 和 Agent49 联动动作是否被 Agent1-10 主链消费。
- 新增 Agent58 `FieldValidationQueueAlignmentAgent`，把 field_validation_queue 映射到 Agent30 数据表、Agent42 replay 表、Agent44 metadata、Agent43/45 gate 和验证指标。
- 新增 Agent59 `ClaimSpecificFieldPackageAgent`，把 Agent58 mapping_table 升级为 claim-specific 必采字段矩阵、acceptance artifacts 和 source_basis 补全任务。
- Agent50 已连续更新 priority ranking：P6 -> P8 -> P9 -> P10 -> 当前 P11。

结果：

- Agent56：`kg_reasoning_patch_ready_needs_field_supported_edges`，evidence_traceability=1.000，constraint_hit_rate=1.000。
- Agent57：`synthetic_main_chain_reconnection_ready_needs_field_replay`，main_chain_prior_consumption_rate=1.000。
- Agent58：`field_validation_alignment_ready_needs_real_field_package`，field_need_to_table_coverage=1.000，field_need_to_gate_coverage=1.000。
- Agent59：`claim_specific_package_ready_needs_real_data_and_source_basis_detail`，minimal_field_package_schema_pass_rate=1.000，source_basis_completion_rate=0.450。
- Agent50 最新 recommended_next_core_action：`P11_source_basis_detail_or_real_field_package_import`。
- 完整回归：266 passed。

结论：

- 这次改动把“缺真实数据”拆成了更工程化的链条：缺哪条 KG 边的现场支持、缺哪个表/字段/gate、哪些 optional 字段必须升级为 claim 必采字段、哪些 source_basis 还只是方法标签。
- 当前最大缺陷仍不是代码，而是 field evidence 和 citation detail：没有真实包前不能升级现场结论；没有具体文献/参数/适用边界前，source_basis 仍不能支撑强 claim。
- 下一步若无真实现场包，应先补 `kb_sensor_limited_release_evidence` 的具体 citation、参数范围和适用边界；若有真实包，则运行 Agent44 -> Agent42 -> Agent43 -> Agent45，并把 field-supported evidence 回写到 KG。

## Agent60 架构复盘、模块化整合与减冗治理

目标：

- 按新的阶段目标，暂停新增展示材料和非必要 agent 堆叠，复盘原有 59 个 agent 在观测、软传感、灰箱机理、KG 证据、多设施控制、工程约束、现场证据门控和项目运行中的真实作用。
- 不把工作继续理解为“Agent 编号越多越好”，而是把历史链条压缩成清晰模块，检查哪些 agent 是核心能力、哪些只是阶段性包装、哪些应合并、冻结或压缩。
- 继续遵守边界：synthetic/sample 只能作为仿真基线和接口验证，不能表述为 field validation。

实现：

- 新增 `AgentArchitectureConsolidationAgent` 作为 Agent60 复盘治理工具；它不计入原有模型本体，只审计既有 59-agent 系统。
- 新增 `experiments/run_agent60_agent_architecture_consolidation.py`，生成：
  - `deliverables/model_core_optimization/agent_architecture_consolidation.md`
  - `outputs/agent60_agent_architecture_consolidation/agent60_report.md`
  - `outputs/agent_architecture_consolidation/architecture_consolidation_metrics.json`
- 将 59 个 agent 映射到 9 个模块：
  1. 低成本稀疏感知与布点。
  2. 软传感、缺测矩阵与不确定性。
  3. 灰箱物理、机理解释与故障诊断。
  4. 循环式处理、多设施协同控制与仲裁。
  5. 知识图谱、文献证据与 claim 审查。
  6. 现场数据接口、replay 与证据门控。
  7. 项目运行、资源调度与实施管理。
  8. 模型治理、主链回接与减冗复盘。
  9. 展示、文档与汇报材料，默认冻结为低优先级。
- 输出核心链路消费关系表，显式记录 Agent48 -> Agent51/54/49、Agent51 -> Agent49/52、Agent53 -> Agent54/57、Agent54 -> Agent2/49、Agent49 -> Agent52/55、Agent55 -> Agent49/6/7、Agent56 -> Agent3/5/58、Agent59 -> Agent50/后续 source_basis 细化。
- 输出 5 个合并/冻结簇：软传感验证簇、field evidence/claim gate 簇、项目运维压缩簇、展示层冻结簇、KG/文献/reasoning 簇。

结果：

- architecture_status：`module_consolidation_ready_needs_interface_refactor`。
- audited_scope：原有 59-agent 模型本体。
- mapped_agent_count：59/59。
- module_count：9。
- core_model_module_count：6。
- core_anchor_coverage：1.000。
- redundancy_cluster_count：5。
- presentation_freeze_agent_count：3。
- 当前最高边际价值重构：`R1_unify_field_evidence_and_source_basis_gate`。
- 第二优先级：`R2_agent48_51_54_observation_contract_merge`。
- 第三优先级：`R3_agent49_replay_counterfactual_stress`。
- 定向回归：7 passed。
- 完整回归：273 passed。

结论：

- 这次复盘没有把重点放在展示层，而是把当前模型从“59 个编号 agent”转换为“9 个职责清晰的模块 + 核心链路消费关系 + 合并/冻结清单”。
- 最根基的问题不再是继续加 agent，而是先统一重复的 field evidence、claim package 与 source_basis gate，避免同一类 evidence/claim/replay 阻断在多个 agent 中重复出现。
- 下一步如果继续实施，应先做 R1：统一 evidence gate schema，并保留 source_basis 文献证据、真实 field package、claim blocker 和 release gate 禁止边界之间的严格区分。

## R1 统一 Field Evidence Gate 接口

目标：

- 承接 Agent60 的最高边际价值重构 `R1_unify_field_evidence_and_source_basis_gate`。
- 不新增业务 agent 编号，而是建立统一 facade，把 Agent43/44/45/46/58/59 中重复出现的 field evidence、claim package、source_basis、replay gate、holdout gate 阻断合并成一个接口。
- 避免同一类 claim upgrade blocker 到处重复，同时继续保持 synthetic/sample、literature-supported 和 field-validation-required 的严格边界。

实现：

- 新增 `src/water_ai/field_evidence_gate.py`，提供 `UnifiedFieldEvidenceGate`。
- 新增 `experiments/run_unified_field_evidence_gate.py`，生成：
  - `deliverables/model_core_optimization/unified_field_evidence_gate.md`
  - `outputs/unified_field_evidence_gate_report/unified_field_evidence_gate_report.md`
  - `outputs/unified_field_evidence_gate/unified_field_evidence_gate_metrics.json`
- 新增 `tests/test_unified_field_evidence_gate.py`，检查：
  - 能消费 6 个既有 gate/claim 来源。
  - synthetic/sample 阻断被保留。
  - source_basis 不完整被路由为下一步任务。
  - 不写 release gate、不写 actuator。
- 更新 Agent60，让它读取统一 gate 指标；当 R1 baseline 已形成时，下一步不再重复推荐 R1，而切换为 `R1b_source_basis_detail_completion_inside_unified_gate`。

结果：

- unified_field_evidence_gate_status：`unified_gate_ready_blocking_field_claim_upgrade`。
- unified_evidence_record_count：3。
- gate_source_consolidation_coverage：1.000。
- source_basis_completion_rate：0.450。
- field_import_pass：False。
- field_replay_evidence_chain_pass：False。
- soft_sensor_field_holdout_gate_pass：False。
- can_emit_field_claim_upgrade：False。
- can_write_to_release_gate：False。
- can_write_to_actuator：False。
- Agent60 当前下一步：`R1b_source_basis_detail_completion_inside_unified_gate`。
- 定向回归：12 passed。

结论：

- 这一步把“重复的证据门控”合并成了一个可消费接口，完成了 R1 的架构减冗目标。
- 它没有试图绕过真实数据缺失，也没有把 source_basis 当成现场证据。
- 当前最高边际价值不是继续合并 gate，而是在统一 gate 内补 source_basis 的 citation、参数范围和适用边界；补齐后仍只能提升 literature-supported traceability，不能替代 field validation。

## R1b Source Basis Detail Library 并入统一 Gate

目标：

- 承接 R1 的统一 evidence gate，不再让 source_basis 只是方法标签。
- 把 `low_cost_proxy_sensing` 和 `soft_sensor_release_gate` 补成可追溯的文献依据、现实映射、适用条件、参数/方法边界、必需 field validation 和失败边界。
- 保持证据分层：citation/detail 可提升 literature-supported traceability，但不能替代 field-supported evidence。

实现：

- 在 `src/water_ai/field_evidence_gate.py` 新增 `SOURCE_BASIS_DETAIL_LIBRARY`。
- 统一 gate 现在输出：
  - `source_basis_detail_library`
  - `source_basis_detail_status`
  - `citation_detail_completion_rate`
  - `source_basis_parameter_boundary_coverage`
  - `effective_literature_traceability`
  - `field_supported_edge_ratio`
- 对旧的 `source_basis_needs_citation_or_parameter_detail` blocker 做规范化：如果 detail library 已补齐，则替换为 `source_basis_literature_detail_complete_not_field_supported`。
- 更新 Agent60 的排序逻辑：R1b 是否完成不再只看 Agent59 原始 `source_basis_completion_rate`，而是看统一 gate 的 `citation_detail_completion_rate`。

结果：

- unified_field_evidence_gate_status：`unified_gate_ready_blocking_field_claim_upgrade`。
- source_basis_completion_rate：0.450，保留为 Agent59 原始任务完成率。
- citation_detail_completion_rate：1.000。
- source_basis_parameter_boundary_coverage：1.000。
- effective_literature_traceability：1.000。
- field_supported_edge_ratio：0.000。
- field_import_pass：False。
- field_replay_evidence_chain_pass：False。
- soft_sensor_field_holdout_gate_pass：False。
- Agent60 当前下一步：`R2_agent48_51_54_observation_contract_merge`。
- 定向回归：14 passed。
- 完整回归：280 passed。

结论：

- R1b 已把 source_basis 从“标签”推进为“可审查的文献/参数/边界记录”。
- 当前阻断从“source_basis 缺 citation/参数边界”升级为“source_basis literature traceability 已完整，但仍不是 field-supported”。
- 下一步最高边际价值回到观测基础链路：合并 Agent48 稀疏布点、Agent51 catalyst_activity 代理观测和 Agent54 软传感观测矩阵合同。

## R2 Agent48/51/54 观测契约合并

目标：

- 承接 Agent60 排序后的 `R2_agent48_51_54_observation_contract_merge`。
- 不新增业务 agent 编号，而是建立 `ObservationContractMerge` facade，把 Agent48 稀疏布点、Agent51 catalyst_activity 代理补点和 Agent54 node-modality/missingness 合同合并为一个 observation contract。
- 关键原则：不能简单加传感器；必须在预算、弱状态覆盖、软传感输入合同和 field validation 边界之间做权衡。

实现：

- 新增 `src/water_ai/observation_contract.py`。
- 新增 `experiments/run_observation_contract_merge.py`，生成：
  - `deliverables/model_core_optimization/observation_contract_merge.md`
  - `outputs/observation_contract_merge_report/observation_contract_merge_report.md`
  - `outputs/observation_contract_merge/observation_contract_metrics.json`
- 新增 `tests/test_observation_contract.py`，检查：
  - 能消费 Agent48/51/54 指标并输出预算内 contract。
  - full proxy patch 保留为高观测上限方案，但因超预算不能直接推荐。
  - budget-rebalanced contract 能把 weak_state_coverage 推过 0.55。
  - 不写 actuator，不写 release gate，不解除 Agent49 catalyst uncertainty block。
- 更新 Agent60，让它读取 R2 observation contract 指标；当 R2 已完成后，下一步自动切换为 R3。

结果：

- observation_contract_status：`synthetic_observation_contract_ready_needs_field_topology_proxy_labels_and_missingness`。
- 推荐合同：`budget_rebalanced_proxy_contract`。
- base weak_state_coverage：0.300。
- proxy_enhanced_weak_state_coverage：0.580。
- catalyst_observability_gain：0.280。
- recommended_cost_index：5.272，budget_pass=True。
- full_proxy_patch_contract 可达到 weak_state_coverage=0.720，但当前估算超预算，不能直接作为现场方案。
- 移除/替换的低边际原始点：`N5_polishing_inlet:turbidity_NTU`。
- 仍缺 field_topology、field_proxy_labels 和 field_missingness replay。
- Agent60 当前下一步：`R3_agent49_replay_counterfactual_stress`。
- 定向回归：14 passed。
- 完整回归：285 passed。

结论：

- R2 已把“布点、催化剂代理、软传感矩阵”从三个分散输出合成一个预算感知 observation contract。
- 这一步直接服务“黑箱变灰箱”的观测基础：不是追求传感器更多，而是让低成本稀疏观测足以支撑隐藏状态估计。
- 下一步最高边际价值转为控制侧验证：用 Agent49/52 replay counterfactual stress 检查多设施协同控制是否真的稳健。

## R3 Agent49/52 控制 Replay 反事实压力测试

目标：

- 承接 Agent60 排序后的 `R3_agent49_replay_counterfactual_stress`。
- 让 R2 观测契约真正进入 Agent49，而不是只停在观测层报告。
- 把 Agent52 replay-ready baseline 升级为 counterfactual stress：比较 baseline policy、R2 observation-aware policy 和 R3 guardrail candidate。
- 核心问题：多设施协同动作在催化剂不确定、慢证据、液位/延迟缺失等场景下，是否会出现高 regret、误保护或工程不可执行。

实现：

- 更新 `MultiFacilityCollaborativeControlAgent`，新增 `observation_contract_metrics` 输入。
- Agent49 现在可消费 R2 的 `budget_rebalanced_proxy_contract`：
  - catalyst_activity_observability：0.300 -> 0.580。
  - weak_state_coverage：0.300 -> 0.580。
  - selected_sensor_count：7。
  - weak_state_ready：True。
- 新增 `src/water_ai/control_replay_stress.py`，提供 `ControlReplayCounterfactualStress` facade。
- 新增 `experiments/run_control_replay_counterfactual_stress.py`，生成：
  - `deliverables/model_core_optimization/control_replay_counterfactual_stress.md`
  - `outputs/control_replay_counterfactual_stress_report/control_replay_counterfactual_stress_report.md`
  - `outputs/control_replay_counterfactual_stress/control_replay_stress_metrics.json`
- 新增 `tests/test_control_replay_stress.py`，并扩展 Agent49/Agent60 测试。
- 更新 Agent60，让它读取 R3 stress 指标；R3 完成后下一步自动切换为 `R3b_agent49_reward_prior_patch_from_counterfactual_stress`。

结果：

- control_replay_stress_status：`synthetic_counterfactual_stress_ready_needs_field_replay`。
- baseline joint_action_accuracy：0.667。
- observation_contract joint_action_accuracy：0.833。
- guardrail_candidate joint_action_accuracy：1.000。
- p95_reward_regret_delta_guardrail：0.177。
- protective_false_positive_cost_delta_guardrail：0.180。
- unsafe_action_block_correction_rate：1.000。
- field_replay_coverage：0.000。
- can_update_agent49_reward_prior：True。
- can_train_offline_rl：False。
- can_write_to_actuator：False。
- can_write_to_release_gate：False。
- Agent60 当前下一步：`R3b_agent49_reward_prior_patch_from_counterfactual_stress`。
- 定向回归：19 passed。

结论：

- R3 已经把“控制策略看起来合理”推进到“反事实 replay 下可指出高 regret 和误保护案例”。
- 观测契约改善能修复 catalyst_uncertain_low_proxy 的误保护倾向，但 hydraulic_delay_violation 仍需要 R3 guardrail 和现场执行 replay。
- 下一步不应继续扩大报告，而应把 R3G1/R3G2 guardrails 接入 Agent49 reward prior，并刷新 Agent52 replay 指标。

## R3b/R3c/R4 控制 Guardrail 消费、Replay 刷新与灰箱反写

目标：

- 承接 Agent60 排序后的 `R3b_agent49_reward_prior_patch_from_counterfactual_stress`、`R3c_agent52_guardrail_aware_replay_refresh` 和 `R4_backpropagate_guardrail_failures_to_grey_box_and_field_requirements`。
- 不停在“R3 报告发现问题”，而是让 Agent49 reward prior、Agent52 replay evaluator、灰箱机制边界和 field requirement patch 都消费同一组控制失败案例。
- 核心问题：R3 发现的误保护和高 regret，是不是能进入模型内部的奖励、验证、机制解释和现场采集字段，而不是只作为文字结论。

实现：

- 更新 `MultiFacilityCollaborativeControlAgent`：
  - 新增 `control_replay_stress_metrics` 输入。
  - 新增 `control_replay_guardrail_context`。
  - 将 `R3G1_catalyst_uncertain_requires_standby_or_human_review` 接入 J2/J4 奖励。
  - 将 `R3G2_hydraulic_delay_unknown_blocks_recycle` 接入 J0/J3 奖励。
  - 在决策树解释规则中加入 R3G1/R3G2。
- 更新 `MultiFacilityReplayEvaluationAgent`：
  - replay_table 新增 `guardrail_aware_policy_action_id`、`guardrail_aware_reward_regret`、`guardrail_source_rule_id`。
  - offline metrics 新增 `guardrail_aware_joint_action_accuracy`、`guardrail_aware_p95_reward_regret`、`guardrail_aware_false_positive_action_cost`。
  - reward diagnostics 新增 `guardrail_resolved_cases`。
- 新增 `src/water_ai/control_guardrail_backpropagation.py`，提供 R4 facade。
- 新增 `experiments/run_control_guardrail_backpropagation.py`，生成：
  - `deliverables/model_core_optimization/control_guardrail_backpropagation.md`
  - `outputs/control_guardrail_backpropagation_report/control_guardrail_backpropagation_report.md`
  - `outputs/control_guardrail_backpropagation/control_guardrail_backpropagation_metrics.json`
- 新增 `tests/test_control_guardrail_backpropagation.py`，并扩展 Agent49/Agent52/Agent60 测试。
- 更新 Agent60：
  - R3b 完成后自动切换 R3c。
  - R3c 完成后自动切换 R4。
  - R4 完成后自动切换 R4b。

结果：

- Agent49 R3b：
  - J4_safe_low_cost_standby：score 0.616，R3b bonus 0.045。
  - J3_polishing_and_release_gate：score 0.582，R3b bonus 0.040。
  - J0_matrix_shock_equalize_and_recycle：score 0.401，R3b penalty 0.140。
  - J2_catalyst_protection_before_regeneration：score 0.185，R3b penalty 0.160。
  - control_replay_guardrails_integrated=True。
  - can_write_to_actuator=False。
- Agent52 R3c：
  - baseline joint_action_accuracy：0.667。
  - baseline p95_reward_regret：0.177。
  - baseline false_positive_action_cost：0.180。
  - guardrail_aware_joint_action_accuracy：1.000。
  - guardrail_aware_p95_reward_regret：0.000。
  - guardrail_aware_false_positive_action_cost：0.000。
  - field_replay_coverage：0.000。
- R4 backpropagation：
  - resolved_case_count：2。
  - resolved_case_to_mechanism_coverage：1.000。
  - resolved_case_to_field_requirement_coverage：1.000。
  - grey_box_failure_boundary_count：6。
  - field_replay_required_field_count：12。
  - status：`synthetic_guardrail_backpropagation_ready_needs_field_replay_and_grey_box_calibration`。
- Agent60 当前下一步：`R4b_patch_agent53_and_field_requirement_interfaces`。
- 定向回归：26 passed。
- 完整回归：299 passed。

结论：

- R3b/R3c/R4 把控制层“经验修正”推进成了可追踪的模型内部链路：counterfactual stress -> reward prior -> guardrail-aware replay -> grey-box/field requirement backpropagation。
- 这一步直接服务第一性原理：让低成本受限观测下的控制失败，不只是被控制器绕开，而是被解释为催化剂代理证据缺口、水力延迟缺口、池容/执行器延迟字段缺口。
- 所有改善仍是 synthetic replay 和 synthetic backpropagation，不能替代真实 field replay、灰箱参数校准或现场控制有效性。

## R4b/R5/R6 Guardrail Patch 消费、Schema 覆盖与 Source Basis 闭合

目标：

- 承接 Agent60 的 `R4b_patch_agent53_and_field_requirement_interfaces`，让 R4 生成的 grey-box/field patches 真正进入 Agent53/58/59。
- 按自我打断评估继续推进 R5/R6：如果 patch 已消费，就不再停留在报告或重复 patch consumption，而是补 schema 缺口、source_basis 缺口，直到下一步只能由真实 field package 推进。

实现：

- 更新 `MinimalGreyBoxPhysicsAgent`：
  - 新增 `control_guardrail_backpropagation_metrics` 输入。
  - 输出 `guardrail_failure_boundary_patch` 和 `control_guardrail_backpropagation_context`。
  - readiness 新增 `agent53_guardrail_boundary_consumption_rate`、`guardrail_failure_boundary_count`、`can_update_guardrail_failure_boundaries`。
- 更新 `FieldValidationQueueAlignmentAgent`：
  - 消费 R4 `field_requirement_patch`，新增两条 R4 guardrail validation rows。
  - 输出 `field_requirement_patch_consumption_rate`、`guardrail_required_field_count`、`guardrail_missing_schema_field_count`。
- 更新 `ClaimSpecificFieldPackageAgent`：
  - 在 claim-specific package 中保留 `_guardrail_requirement_patch`。
  - 输出 `guardrail_package_row_count`、`unmet_guardrail_field_count`。
  - 消费统一 evidence gate 的 `source_basis_detail_library`，并为 `R4_control_guardrail_failure_backpropagation` 添加 internal synthetic replay provenance。
- 更新 Agent30/42 schema：
  - Agent30 增加 `proxy_holdout_label`、`regeneration_event`、`tank_storage_margin`、`actuator_latency_p90`、`pump_valve_result`、`hold_time_min`。
  - Agent42 timestamped replay schema 增加同组 guardrail 字段和 `flow_Lmin` optional replay 字段。
- 更新 Agent60：
  - R4 完成后进入 R4b。
  - R4b 完成且存在 unmet fields 时进入 R5。
  - R5 schema 覆盖、R6 source_basis 完成后进入 `R7_real_field_package_import_acceptance_gate`。

结果：

- Agent53：
  - agent53_guardrail_boundary_consumption_rate：1.000。
  - guardrail_failure_boundary_count：6。
  - can_write_to_release_gate：False。
- Agent58：
  - field_requirement_patch_consumption_rate：1.000。
  - guardrail_required_field_count：12。
  - guardrail_missing_schema_field_count：0。
- Agent59：
  - field_requirement_patch_consumption_rate：1.000。
  - guardrail_package_row_count：2。
  - unmet_guardrail_field_count：0。
  - source_basis_completion_rate：1.000。
  - minimal_field_package_field_pass_rate：0.000。
- Agent60 当前下一步：`R7_real_field_package_import_acceptance_gate`。
- 定向回归：33 passed。
- 完整回归：308 passed。

结论：

- R4b/R5/R6 已经把“控制失败案例”从 replay 层回传到灰箱机制、现场字段、claim-specific package、schema 和 source_basis。
- 当前结构性阻塞已基本清空；真正阻塞证据等级提升的是没有真实 field package、timestamped replay、soft-sensor field holdout 和人工复核证据。
- 所有当前改善仍只能标注为 synthetic replay、internal synthetic provenance、literature-supported method 或 field-validation-required，不能写执行器或 release gate。

## R7 真实 Field Package 验收 Facade 与 Agent44 导入入口加固

目标：

- 承接 Agent60 当前最高边际价值动作 `R7a_import_real_field_package_with_metadata_and_csv`。
- 不继续停留在“缺真实数据”的笼统阻断，而是把真实现场数据进入模型主链的验收步骤拆细，让后续一旦有 field package 就可以直接运行 Agent44 -> Agent42 -> Agent43 -> Agent45 -> Agent46/59 -> unified gate。
- 把 R5/R7 新增的 guardrail 必采字段真正纳入 Agent44 类型化导入，避免真实 CSV 进来后仍因为字段解析能力不足而卡住。

实现：

- 新增 `RealFieldPackageAcceptanceGate`：
  - 消费 Agent44 field replay import、Agent42 timestamped replay、Agent43 G6/P6、Agent45 evidence chain、Agent46 field holdout、Agent59 claim-specific package 和 unified field evidence gate。
  - 输出七阶段 acceptance matrix、readiness、writeback policy 和下一步 refactor action。
  - 当前阶段包括 `R7S1_field_package_import`、`R7S2_timestamped_replay`、`R7S3_g6_p6_replay_gate`、`R7S4_field_replay_evidence_chain`、`R7S5_soft_sensor_field_holdout`、`R7S6_claim_specific_field_package`、`R7S7_unified_field_evidence_gate`。
- 新增 `experiments/run_real_field_package_acceptance_gate.py`：
  - 写出 `outputs/real_field_package_acceptance_gate/real_field_package_acceptance_gate_metrics.json`。
  - 写出 `outputs/real_field_package_acceptance_gate_report/real_field_package_acceptance_gate_report.md`。
  - 写出 `deliverables/model_core_optimization/real_field_package_acceptance_gate.md`。
  - 回写 manifest 的 R7 状态和下一步。
- 更新 Agent60：
  - 读取 R7 acceptance gate 指标。
  - 当 R7 指标存在时，不再只给抽象的 `R7_real_field_package_import_acceptance_gate`，而是直接推荐 `R7a_import_real_field_package_with_metadata_and_csv`。
  - 把当前 blocker 展开为 field package import、timestamped replay、G6/P6、evidence chain、soft holdout、claim package、unified evidence gate。
- 加固 Agent44：
  - `FieldReplayImportAgent` 的 numeric fields 增加 `flow_Lmin`、`recycle_ratio`、`tank_storage_margin`、`actuator_latency_p90`、`hold_time_min`。
  - boolean fields 增加 `proxy_holdout_label`、`regeneration_event`。
  - `experiments/run_agent44_field_replay_import.py` 支持 `REAL_FIELD_REPLAY_PACKAGE_DIR`：若设置该环境变量，则直接读取用户提供的真实 field package；否则继续生成 synthetic interface package 仅用于接口联调。
  - 导入报告和 acceptance metrics 记录 `source_package_type` 与 `source_package_dir`，避免 synthetic package 与 field package 混淆。

结果：

- 当前 R7 acceptance gate：
  - real_field_package_acceptance_status：`real_field_package_acceptance_blocked_at_import`。
  - passed_stage_count：0/7。
  - next_action：`R7a_import_real_field_package_with_metadata_and_csv`。
  - blocker：`field_package_not_imported_or_data_origin_not_field` 仍为首个阻断。
- Agent44 synthetic fallback：
  - source_package_type：`synthetic_interface_package`。
  - 表验收：4/4。
  - import status：`field_replay_import_blocked_non_field_origin`。
  - 说明字段 schema 与类型化入口已可用，但证据等级仍不能越过 field origin。
- Agent60 当前下一步：
  - action_id：`R7a_import_real_field_package_with_metadata_and_csv`。
  - 含义：导入 `data_origin=field` 的真实 metadata 与 CSV 包，再走 timestamped replay、G6/P6、evidence chain、soft holdout、claim package 和 unified evidence gate。
- 定向回归：
  - `tests/test_field_replay_import_agent.py tests/test_real_field_package_acceptance_gate.py tests/test_agent_architecture_consolidation_agent.py`：27 passed。
- 完整回归：
  - `.venv/bin/pytest -q`：312 passed。

结论：

- R7 的价值不是“又加一个 gate”，而是把 field-supported 证据的入口从一句“缺真实数据”变成可执行的验收管线。
- 当前系统可以清楚地区分：synthetic interface package 只能证明 schema 和类型化流程；真实 field package 需要 `data_origin=field`、provenance metadata、CSV 字段、batch linkage 和后续 replay/holdout 全链路通过。
- 在真实 package 进入并通过七阶段 gate 前，不能写执行器、不能写 release gate、不能把当前 synthetic 结果升级成 field-supported claim。

## R7a Field Package Preflight 与真实包模板

目标：

- 不在“等待真实数据”处空转，而是把 R7a 的真实包准备工作进一步工程化。
- 让现场数据提供者能直接按模板填 metadata 和四张 CSV，且在进入 Agent44 前先看到缺文件、缺 header、placeholder provenance、header-only rows、non-field origin 等具体阻断。
- 防止 `TODO_*`、`template`、`replace_me` 等占位 metadata 被误认为真实 provenance。

实现：

- 扩展 `FieldReplayImportAgent`：
  - 新增 placeholder 检测，metadata 必需字段和 CSV 必需字段中的 TODO/template/replace_me 等值都会被当成缺失。
  - 新增 `field_replay_package_template_spec()`、`write_field_replay_package_template()` 和 `preflight_field_replay_package()`。
  - preflight 输出 `file_audit`、`placeholder_metadata_fields`、`row_counts`、`files_ready`、`real_rows_ready`、`agent44_import_status` 和下一步动作。
- 更新 `experiments/run_agent44_field_replay_import.py`：
  - 每次运行都会生成 `outputs/field_replay_import/real_field_package_template/`。
  - 每次运行都会写出 `outputs/field_replay_import/real_field_package_preflight_metrics.json`。
  - import protocol 中增加 `preflight_status` 和 preflight 下一步。

结果：

- 当前 synthetic fallback：
  - preflight_status：`field_package_preflight_blocked_non_field_origin`。
  - agent44_import_status：`field_replay_import_blocked_non_field_origin`。
  - 说明 schema/header/row plumbing 可运行，但 data_origin 不可越过。
- 新增真实包模板：
  - `metadata.json` 含 `data_origin=field` 和 TODO provenance。
  - `sensor_timeseries.csv` 含 `flow_Lmin`。
  - `offline_lab_results.csv` 含 `proxy_holdout_label`。
  - `campaign_operation_log.csv` 含 `recycle_ratio`、`tank_storage_margin`、`actuator_latency_p90`、`pump_valve_result`、`hold_time_min`、`regeneration_event`。
  - `fast_proxy_event_log.csv` 保持 G6/P6 快代理所需字段。
- 定向回归：
  - `tests/test_field_replay_import_agent.py`：9 passed。
- 完整回归：
  - `.venv/bin/pytest -q`：315 passed。

结论：

- R7a 从“需要真实包”进一步变成“真实包应该长什么样、哪里没填、为什么不能进入 field replay”的可操作入口。
- header-only template 和 synthetic interface package 仍只属于接口准备，不改变任何 field-supported 结论。

## R7 真实 Field Replay 端到端管线

目标：

- 继续承接 R7a，但不把真实包进入主链拆成多个手工命令。
- 给定一个 package directory 后，一次性运行 Agent44 preflight/import、Agent45 内部 Agent42/43 replay/G6，再进入 R7 acceptance gate。
- 不覆盖 canonical synthetic baseline；该管线单独输出结果，用来定位真实包卡在哪个 gate。

实现：

- 新增 `src/water_ai/real_field_replay_pipeline.py`：
  - `build_real_field_replay_pipeline()` 在内存中串联 Agent44、Agent45 和 R7。
  - 返回 preflight、import report、field replay evidence chain report、R7 acceptance 和 pipeline_readiness。
  - 默认禁止 actuator/release gate writeback。
- 新增 `experiments/run_r7_real_field_replay_pipeline.py`：
  - 如果设置 `REAL_FIELD_REPLAY_PACKAGE_DIR`，读取用户真实包。
  - 如果未设置，生成并使用 header-only template 做 preflight 演练。
  - 输出 `outputs/r7_real_field_replay_pipeline/r7_real_field_replay_pipeline_metrics.json`。
  - 输出 `outputs/r7_real_field_replay_pipeline/r7_real_field_replay_pipeline_report.md`。
  - 输出 `deliverables/model_core_optimization/r7_real_field_replay_pipeline.md`。
- 新增 `tests/test_real_field_replay_pipeline.py`：
  - 覆盖 header-only template 被挡在 import 前。
  - 覆盖完整 field package 可通过 Agent44/45 内部 replay/G6，并在 soft holdout 阶段正确停住。

结果：

- 当前无真实包运行：
  - source_package_type：`header_only_template_preflight`。
  - import：`field_replay_import_metadata_blocked`。
  - evidence chain：`field_replay_evidence_chain_blocked_at_import`。
  - R7：`real_field_package_acceptance_blocked_at_import`。
  - next：`R7a_import_real_field_package_with_metadata_and_csv`。
- 定向回归：
  - `tests/test_real_field_replay_pipeline.py tests/test_real_field_package_acceptance_gate.py tests/test_field_replay_import_agent.py`：14 passed。
- 完整回归：
  - `.venv/bin/pytest -q`：317 passed。

结论：

- 真实包进入主链现在有了一个单命令入口：
  - `REAL_FIELD_REPLAY_PACKAGE_DIR=/path/to/field_package .venv/bin/python experiments/run_r7_real_field_replay_pipeline.py`
- 该入口可以证明“卡在哪里”，但不改变证据等级边界；模板、synthetic 或未过全链路 field package 都不能写执行器、release gate 或 field-supported claim。

## R7 Field Package Coverage / Gap 审计

目标：

- 继续强化 R7 pipeline：真实包不仅要能导入，还要能回答“是否足够支撑具体 claim 和软传感 field holdout”。
- 防止出现 package 通过 Agent44 导入，但缺少 claim-specific 必采字段、检测限、方法、单位、弱目标标签，最终仍无法支撑 field-supported claim。

实现：

- 新增 `src/water_ai/field_package_coverage.py`：
  - 读取 package 中所有 CSV 的 headers、row_count、非空字段和样例值。
  - 对照 Agent59 `minimal_field_package_matrix`，审计每条 claim 的 metadata、表字段、非空值和 row presence。
  - 对照 soft holdout 需求，检查 `sensor_timeseries`、`offline_lab_results` 基础字段和弱目标 analytes：`catalyst_activity`、`matrix_interference`。
  - 输出 `field_package_coverage_status`、`claim_specific_coverage_rate`、`soft_holdout_coverage_pass` 和 next_actions。
- 更新 `src/water_ai/real_field_replay_pipeline.py`：
  - 把 coverage audit 接入 pipeline result 和 `pipeline_readiness`。
- 更新 `experiments/run_r7_real_field_replay_pipeline.py`：
  - 报告正文展示 `field_package_coverage_status`、`claim_specific_coverage_rate`、`soft_holdout_coverage_pass` 和 coverage next actions。
- 新增 `tests/test_field_package_coverage.py`：
  - 覆盖 template import 前阻断。
  - 覆盖 claim-specific 字段缺失。
  - 覆盖 claim + soft holdout 字段通过。
  - 覆盖弱目标 analyte 缺失。

结果：

- 当前 header-only template 演练：
  - field_package_coverage_status：`field_package_coverage_blocked_before_import`。
  - claim_specific_coverage_rate：0.0。
  - soft_holdout_coverage_pass：False。
- 定向回归：
  - `tests/test_field_package_coverage.py tests/test_real_field_replay_pipeline.py`：6 passed。
- 完整回归：
  - `.venv/bin/pytest -q`：321 passed。

结论：

- R7 现在不仅能判断“真实包能不能进 replay”，还能提前判断“这个包能不能支撑 claim-specific field review 和 soft sensor holdout”。
- 这直接服务第一性原理里的证据边界：导入成功不等于 claim 支持，field replay 成功也不等于 release gate 或 actuator 可写。

## Agent60 接入 R7 Pipeline/Coverage 的下一步治理

目标：

- 承接“低成本受限观测条件下的循环式水处理智能灰箱闭环系统”第一性原理，不让治理层停留在笼统的“缺真实数据”。
- 让 Agent60 能读取 R7 端到端 pipeline 的 coverage 审计结果，在真实包导入后根据具体缺口自动切换下一步任务。

实现：

- 更新 `src/water_ai/agents/agent_architecture_consolidation_agent.py`：
  - 新增读取 `r7_real_field_replay_pipeline_metrics` 的逻辑。
  - 在 R7 action 的 `trigger_metric` 中加入 `field_package_coverage_status`、`claim_specific_coverage_rate` 和 `soft_holdout_coverage_pass`。
  - 当 coverage 状态为 `field_package_claim_specific_coverage_gaps` 时，最高边际价值动作切到 `R7g_patch_field_package_claim_specific_coverage`。
  - 当 coverage 状态为 `field_package_soft_holdout_coverage_gaps` 时，最高边际价值动作切到 `R7h_patch_soft_holdout_weak_target_labels`。
  - 当 coverage 仍阻断在 import/preflight 前时，保持 `R7a_import_real_field_package_with_metadata_and_csv`。
- 更新 `experiments/run_agent60_agent_architecture_consolidation.py`：
  - 将 `outputs/r7_real_field_replay_pipeline/r7_real_field_replay_pipeline_metrics.json` 接入 Agent60 core_metrics。
- 更新 `deliverables/model_core_optimization/model_core_goal.md`：
  - 用第一性原理重写项目 goal，强调“黑箱变灰箱”的观测、推断、解释、控制和验证主线。
- 扩展 `tests/test_agent_architecture_consolidation_agent.py`：
  - 覆盖 R7 acceptance gate 仍可驱动 R7a。
  - 覆盖 claim-specific coverage 缺口驱动 R7g。
  - 覆盖 weak-target soft holdout 缺口驱动 R7h。

结果：

- 当前无真实包时，Agent60 最高边际价值动作仍为：
  - `R7a_import_real_field_package_with_metadata_and_csv`。
- 当前触发指标已包含：
  - `field_package_coverage_status=field_package_coverage_blocked_before_import`。
  - `claim_specific_coverage_rate=0.000`。
  - `soft_holdout_coverage_pass=False`。
- 定向回归：
  - `.venv/bin/pytest -q tests/test_agent_architecture_consolidation_agent.py tests/test_real_field_replay_pipeline.py tests/test_field_package_coverage.py`：26 passed。
- 完整回归：
  - `.venv/bin/pytest -q`：323 passed。

结论：

- Agent60 现在不是只说“继续 R7”，而是会随着真实包进入链条后自动判断：先修导入、补 claim-specific 字段，还是补弱目标 holdout 标签。
- 这一步的边际价值在于把 R7 从“真实数据缺失”推进成可分阶段执行的证据门控路线，继续服务“低成本受限观测下黑箱变灰箱”的核心模型目标。

## R7 Coverage Patch Plan 可机读补包计划

目标：

- 承接 R7a，但不在“缺真实数据”处空转。
- 把 R7 coverage/gap 审计从文字 next_actions 升级为可机读、可测试、可由 Agent60 消费的补包计划。
- 让真实 field package 进入后，系统能明确区分：导入前补 metadata/rows、claim-specific 字段补全、soft holdout 弱目标标签补全。

实现：

- 更新 `src/water_ai/field_package_coverage.py`：
  - 新增 `patch_plan` 输出。
  - `field_package_coverage_blocked_before_import` 对应 `patch_plan_blocked_at_import_preflight`。
  - `field_package_claim_specific_coverage_gaps` 对应 `patch_plan_requires_claim_specific_fields`。
  - `field_package_soft_holdout_coverage_gaps` 对应 `patch_plan_requires_soft_holdout_weak_targets`。
  - `field_package_coverage_ready_for_replay_and_holdout` 对应 `patch_plan_ready_for_replay_and_holdout`。
  - patch item 保留 `item_id`、`stage`、`target_file/target_table`、`action`、`fields_to_add`、`fields_to_fill`、`required_analytes`、`minimum_rows` 和 `why_required`。
- 更新 `experiments/run_r7_real_field_replay_pipeline.py`：
  - 在 pipeline report 和 deliverable 中展示 patch plan status、item_count 和每个补包项。
  - manifest 同步 `latest_r7_pipeline_coverage_status`。
- 扩展测试：
  - template preflight 阻断时必须生成 metadata placeholder 和真实行补包项。
  - claim-specific 字段缺失时必须生成 R7G table patch。
  - 弱目标 analyte 缺失时必须生成 R7H weak target patch。
  - coverage ready 时 patch item_count 必须为 0。

结果：

- 当前 header-only template 演练：
  - `patch_plan_status=patch_plan_blocked_at_import_preflight`。
  - `patch_plan_item_count=5`。
  - 当前补包项：
    - `R7A_METADATA_PLACEHOLDERS`。
    - `R7A_REAL_ROWS_campaign_operation_log`。
    - `R7A_REAL_ROWS_fast_proxy_event_log`。
    - `R7A_REAL_ROWS_offline_lab_results`。
    - `R7A_REAL_ROWS_sensor_timeseries`。
- 定向回归：
  - `.venv/bin/pytest -q tests/test_field_package_coverage.py tests/test_real_field_replay_pipeline.py tests/test_agent_architecture_consolidation_agent.py`：26 passed。
- 完整回归：
  - `.venv/bin/pytest -q`：323 passed。

结论：

- R7a 已从“导入真实包”进一步具体化为“替换真实 provenance + 四张 CSV 补真实 timestamped rows”的可执行补包计划。
- 这一步直接服务第一性原理中的证据边界：只有真实 provenance、真实时间戳、真实 lab/proxy/operation/sensor 行进入 replay 后，后续软传感、claim 和控制结论才有资格升级。

## R7 最小 Timestamped Replay 包契约

目标：

- 防止真实包“每张表都有行”但仍无法进入 Agent42 replay。
- 把 R7a 继续细化为跨表共同 batch、时间顺序和 proxy 事件数要求，让补包计划不仅知道补哪张表，还知道如何补成可回放结构。

实现：

- 更新 `src/water_ai/field_package_coverage.py`：
  - 新增 `minimum_replay_contract_audit`。
  - 记录 `minimum_smoke_test_matched_batch_count=3`、`recommended_calibration_proxy_event_count=12`。
  - 审计 `sensor_timeseries`、`offline_lab_results`、`campaign_operation_log`、`fast_proxy_event_log` 的共同 `batch_id` 数量。
  - 记录时间顺序约束：
    - `sample_time_min <= result_time_min`。
    - `command_time_min <= effect_time_min <= end_min` 且 `start_min <= end_min`。
    - `event_time_min <= lab_label_time_min`。
  - 当字段覆盖和 soft holdout 都可用，但共同 batch/proxy 事件不足时，`patch_plan_status` 切到 `patch_plan_requires_minimum_replay_contract`。
- 更新 `src/water_ai/real_field_replay_pipeline.py`：
  - 在 `pipeline_readiness` 中加入 `minimum_replay_contract_status`、`minimum_replay_contract_pass`、`minimum_common_batch_count`、`minimum_proxy_event_count`、`coverage_patch_plan_status`。
- 更新 `src/water_ai/agents/agent_architecture_consolidation_agent.py`：
  - Agent60 读取最小 replay 契约。
  - 如果 coverage/holdout 字段齐全但共同 batch/proxy 事件不足，下一步会切到 `R7i_patch_minimum_replay_batch_linkage`。
- 扩展测试：
  - 字段齐但只有 1 个共同 batch 时，coverage 仍可 ready，但 patch plan 必须要求 `R7I_MATCHED_BATCH_GROUPS`。
  - Agent60 必须把该情况提升为 `R7i_patch_minimum_replay_batch_linkage`。

结果：

- 当前 header-only template 演练：
  - `minimum_replay_contract_status=minimum_replay_contract_blocked_missing_rows`。
  - `minimum_common_batch_count=0`。
  - `minimum_proxy_event_count=0`。
  - 最高边际价值仍为 `R7a_import_real_field_package_with_metadata_and_csv`，因为当前还未通过 preflight/import。
- 定向回归：
  - `.venv/bin/pytest -q tests/test_field_package_coverage.py tests/test_real_field_replay_pipeline.py tests/test_agent_architecture_consolidation_agent.py`：28 passed。
- 完整回归：
  - `.venv/bin/pytest -q`：325 passed。

结论：

- R7 现在可以区分三类经常混在一起的问题：真实来源未导入、字段/标签覆盖不足、跨表共同批次不足。
- 这让真实包接入更接近工程项目：不是“表填了就行”，而是必须形成可 replay 的 sensor/lab/operation/proxy 同轴批次。

## R7 Minimum Replay Time-Order Audit

目标：

- 继续加固 R7 最小 replay 契约，提前发现会污染延迟估计和控制 replay 的时间顺序错误。
- 不等 Agent42 才发现时间顺序异常，而是在 field package coverage 阶段就给出可机读 patch item。

实现：

- 更新 `src/water_ai/field_package_coverage.py`：
  - `table_profiles` 新增 `time_order_violations`。
  - 对齐 Agent42 的时间规则：
    - `offline_lab_results`: `sample_time_min <= result_time_min`。
    - `campaign_operation_log`: `command_time_min <= effect_time_min <= end_min` 且 `start_min <= end_min`。
    - `fast_proxy_event_log`: `event_time_min <= lab_label_time_min`。
  - `minimum_replay_contract_audit` 新增 `time_order_violation_count` 和 `time_order_violations`。
  - 若字段覆盖、弱目标和共同 batch 足够，但时间顺序异常，契约状态切到 `minimum_replay_contract_time_order_gaps`，patch item 为 `R7I_TIME_ORDER`。
- 更新 `src/water_ai/real_field_replay_pipeline.py`、`experiments/run_r7_real_field_replay_pipeline.py` 和 Agent60：
  - 在 pipeline readiness、报告和 Agent60 trigger metric 中加入 `minimum_time_order_violation_count`。
- 扩展测试：
  - 构造字段齐全、batch 足够但 lab/operation/proxy 时间顺序错误的真实包。
  - 断言 coverage 仍可 ready，但 minimum replay contract 必须阻断，并生成 `R7I_TIME_ORDER`。

结果：

- 当前 header-only template 演练：
  - `minimum_time_order_violation_count=0`，因为尚无真实行。
  - 阻断仍发生在 `R7a_import_real_field_package_with_metadata_and_csv`。
- 定向回归：
  - `.venv/bin/pytest -q tests/test_field_package_coverage.py tests/test_real_field_replay_pipeline.py tests/test_agent_architecture_consolidation_agent.py`：29 passed。
- 完整回归：
  - `.venv/bin/pytest -q`：326 passed。

结论：

- R7 现在不仅要求字段齐、批次对齐，还要求时间轴物理合理。
- 这直接服务“循环结构换时间”的第一性原理：如果时间顺序错，lab turnaround、actuator latency 和 proxy lead time 都会失真，后续闭环控制判断不能采信。

## R7 Fast Proxy Label Quality Gate

目标：

- 继续加固 R7 最小 replay 契约，避免真实包“fast_proxy_event_log 有行”但标签不可用于 precision/recall、误触发成本和保护动作提前量校准。
- 把“有 proxy 事件”和“有可验证 field-labeled proxy 事件”区分开，防止形式达标的数据包误进入 Agent42/43/45 校准链。

实现：

- 更新 `src/water_ai/field_package_coverage.py`：
  - 新增 `PROXY_LABEL_QUALITY_FIELDS`，要求 `protective_triggered`、`field_label_matrix_shock`、`false_positive_cost_index`、`event_time_min`、`lab_label_time_min` 可解析。
  - `table_profiles.fast_proxy_event_log` 新增 `proxy_label_quality`，记录 `valid_proxy_label_count`、`invalid_proxy_label_count`、`invalid_proxy_label_rows` 和标签类别计数。
  - `minimum_replay_contract_audit` 新增 `minimum_replay_contract_proxy_label_quality_gaps` 状态；当共同 batch、事件数和时间顺序足够，但有效 proxy 标签数不足 3 条时，阻断 replay。
  - `patch_plan` 新增 `R7I_PROXY_LABEL_QUALITY`，把需要修复的无效标签行、必需字段和当前有效标签数机读输出。
- 更新 `src/water_ai/real_field_replay_pipeline.py`：
  - 在 `pipeline_readiness` 中加入 `minimum_valid_proxy_label_count` 和 `minimum_invalid_proxy_label_count`。
- 更新 `src/water_ai/agents/agent_architecture_consolidation_agent.py`：
  - Agent60 的 R7 trigger metric 现在包含有效/无效 proxy 标签数。
  - R7i implementation path 明确要求可解析的 field-labeled fast proxy 事件，而不是只补事件行。
- 更新 `experiments/run_r7_real_field_replay_pipeline.py` 与 `experiments/run_agent60_agent_architecture_consolidation.py`：
  - 报告、deliverable、manifest 和 next_stage rationale 同步显示有效/无效 proxy 标签数。
- 扩展测试：
  - 构造字段齐、共同 batch 齐、但 `false_positive_cost_index` 为负数的真实包；coverage 仍可 ready，但最小 replay 契约必须切到 `minimum_replay_contract_proxy_label_quality_gaps`。
  - R7 pipeline 和 Agent60 测试断言新指标被消费。

结果：

- 当前 header-only template 演练：
  - `minimum_replay_contract_status=minimum_replay_contract_blocked_missing_rows`。
  - `minimum_common_batch_count=0`。
  - `minimum_valid_proxy_label_count=0`。
  - `minimum_invalid_proxy_label_count=0`。
  - 最高边际价值仍为 `R7a_import_real_field_package_with_metadata_and_csv`，因为当前还未通过 preflight/import。
- 定向回归：
  - `.venv/bin/pytest -q tests/test_field_package_coverage.py tests/test_real_field_replay_pipeline.py tests/test_agent_architecture_consolidation_agent.py`：30 passed。
- 完整回归：
  - `.venv/bin/pytest -q`：327 passed。

结论：

- R7 现在可以区分四类真实包问题：真实来源未导入、字段/标签覆盖不足、跨表共同批次/时间轴不足、proxy 标签语义不可用于校准。
- 这直接服务“低成本快代理 + 慢速离线标签”的核心链路：只有有效 field-labeled proxy 事件足够时，后续快代理保护控制、误触发成本和延迟窗口评估才有资格从 synthetic baseline 进入 field replay。

## R7 Offline Lab Result Quality Gate

目标：

- 继续加固 R7 最小 replay 契约，避免真实包“offline_lab_results 有行、有 batch、有数值”但 QA 不合格，导致软传感 holdout、快代理标签和 claim 审查使用不可采信的离线标签。
- 把“有 lab 行”和“有可作为现场校准标签的 lab 行”区分开。

实现：

- 更新 `src/water_ai/field_package_coverage.py`：
  - 新增 `LAB_RESULT_QUALITY_FIELDS` 和 `ACCEPTED_LAB_QA_FLAGS`。
  - `table_profiles.offline_lab_results` 新增 `lab_result_quality`，记录 `valid_lab_result_count`、`invalid_lab_result_count`、`invalid_lab_result_rows`、`analyte_valid_counts` 和 `qa_flag_counts`。
  - `minimum_replay_contract_audit` 新增 `minimum_replay_contract_lab_result_quality_gaps` 状态；当共同 batch 足够但 QA 通过、数值非负、时间可解析的 lab 结果不足 3 条时，阻断 replay。
  - `patch_plan` 新增 `R7I_LAB_RESULT_QUALITY`，把无效 lab 行、必需字段、可接受 QA flag 和当前有效标签数机读输出。
- 更新 `src/water_ai/real_field_replay_pipeline.py`：
  - 在 `pipeline_readiness` 中加入 `minimum_valid_lab_result_count` 和 `minimum_invalid_lab_result_count`。
- 更新 `src/water_ai/agents/agent_architecture_consolidation_agent.py`：
  - Agent60 的 R7 trigger metric 现在包含有效/无效 lab 结果数。
  - R7i implementation path 明确要求 QA 通过、数值非负且时间可解析的 `offline_lab_results`。
- 更新 `experiments/run_r7_real_field_replay_pipeline.py` 与 `experiments/run_agent60_agent_architecture_consolidation.py`：
  - 报告、deliverable、manifest 和 next_stage rationale 同步显示有效/无效 lab 结果数。
- 扩展测试：
  - 构造字段齐、共同 batch 齐、proxy 标签齐，但 `qa_flag=fail` 的真实包；coverage 仍可 ready，但最小 replay 契约必须切到 `minimum_replay_contract_lab_result_quality_gaps`。
  - R7 pipeline 和 Agent60 测试断言新指标被消费。

结果：

- 当前 header-only template 演练：
  - `minimum_replay_contract_status=minimum_replay_contract_blocked_missing_rows`。
  - `minimum_common_batch_count=0`。
  - `minimum_valid_lab_result_count=0`。
  - `minimum_invalid_lab_result_count=0`。
  - `minimum_valid_proxy_label_count=0`。
  - `minimum_invalid_proxy_label_count=0`。
  - 最高边际价值仍为 `R7a_import_real_field_package_with_metadata_and_csv`，因为当前还未通过 preflight/import。
- 定向回归：
  - `.venv/bin/pytest -q tests/test_field_package_coverage.py tests/test_real_field_replay_pipeline.py tests/test_agent_architecture_consolidation_agent.py`：31 passed。
- 完整回归：
  - `.venv/bin/pytest -q`：328 passed。

结论：

- R7 现在可以区分五类真实包问题：真实来源未导入、字段/标签覆盖不足、跨表共同批次/时间轴不足、offline lab 标签不可采信、proxy 标签语义不可用于校准。
- 这直接服务“慢速离线检测作为真值标签”的核心链路：只有 QA 合格的 lab 结果足够时，软传感 holdout、快代理校准和 claim 升级才有资格从 synthetic baseline 进入 field replay。

## R7 Valid Matched Replay Batch Gate

目标：

- 继续加固 R7 最小 replay 契约，避免真实包“有效 lab 行数够、有效 proxy 行数也够”，但二者不在同一批次上，导致 Agent42 仍没有足够的同轴 replay 批次。
- 把“有效行数够”推进为“同一 batch_id 上 sensor/lab/operation/proxy 都可用”。

实现：

- 更新 `src/water_ai/field_package_coverage.py`：
  - `lab_result_quality` 新增 `valid_lab_result_batch_ids` 和 `valid_lab_result_batch_count`。
  - `proxy_label_quality` 新增 `valid_proxy_label_batch_ids` 和 `valid_proxy_label_batch_count`。
  - `minimum_replay_contract_audit` 新增 `valid_matched_batch_count` 和 `valid_matched_batch_ids_sample`，计算共同 batch、有效 lab batch、有效 proxy batch 的交集。
  - 新增 `minimum_replay_contract_valid_matched_batch_gaps` 状态；当 common batch、lab QA 和 proxy 标签各自数量都够，但有效标签没有落在至少 3 个同一批次上时，阻断 replay。
  - `patch_plan` 新增 `R7I_VALID_MATCHED_BATCH_GROUPS`，要求把有效 lab/proxy 标签对齐到同一批次。
- 更新 `src/water_ai/real_field_replay_pipeline.py`：
  - 在 `pipeline_readiness` 中加入 `minimum_valid_matched_batch_count`。
- 更新 `src/water_ai/agents/agent_architecture_consolidation_agent.py`：
  - Agent60 的 R7 trigger metric 现在包含有效共同批次数。
  - R7i implementation path 明确要求有效 lab/proxy 标签落在同一批次。
- 更新 `experiments/run_r7_real_field_replay_pipeline.py` 与 `experiments/run_agent60_agent_architecture_consolidation.py`：
  - 报告、deliverable、manifest 和 next_stage rationale 同步显示有效共同批次数。
- 扩展测试：
  - 构造 4 个共同 batch，其中 lab 有效批次为 B002-B004，proxy 有效批次为 B001-B003；有效 lab/proxy 行数都够，但同一批次上的有效 replay 只有 B002/B003 两个。
  - 断言状态切到 `minimum_replay_contract_valid_matched_batch_gaps`，并生成 `R7I_VALID_MATCHED_BATCH_GROUPS`。

结果：

- 当前 header-only template 演练：
  - `minimum_replay_contract_status=minimum_replay_contract_blocked_missing_rows`。
  - `minimum_common_batch_count=0`。
  - `minimum_valid_matched_batch_count=0`。
  - `minimum_valid_lab_result_count=0`。
  - `minimum_valid_proxy_label_count=0`。
  - 最高边际价值仍为 `R7a_import_real_field_package_with_metadata_and_csv`，因为当前还未通过 preflight/import。
- 定向回归：
  - `.venv/bin/pytest -q tests/test_field_package_coverage.py tests/test_real_field_replay_pipeline.py tests/test_agent_architecture_consolidation_agent.py`：32 passed。
- 完整回归：
  - `.venv/bin/pytest -q`：329 passed。

结论：

- R7 现在不再只问“有没有三条 lab 标签、三条 proxy 标签”，而是问“有没有三组同一批次上的完整有效 replay 证据”。
- 这直接服务 field replay 的第一性原理：闭环控制、软传感校准和快代理校准都必须基于同一过程批次的观测、动作、慢标签和快标签，不能靠跨批次拼凑。

## R7 Operation Action Quality Gate

目标：

- 继续加固 R7 最小 replay 契约，避免真实包“campaign_operation_log 有行、有 batch”，但动作不可执行、时间不可解析、回流/暂存/泵阀结果字段不可信，导致 Agent42/49/52 在回放时把无效操作当成闭环控制证据。
- 把“同一批次有 operation 表记录”推进为“同一批次有可执行、时间可解析、工程字段合理的操作动作”。

实现：

- 更新 `src/water_ai/field_package_coverage.py`：
  - 新增 `operation_action_quality` 表画像，检查 `action_id`、`command_time_min`、`effect_time_min`、`start_min`、`end_min`、`release_policy`。
  - 对可选工程字段做合理性校验：`recycle_ratio` 必须在 `[0, 1]`，`tank_storage_margin`、`actuator_latency_p90`、`hold_time_min` 必须非负，`pump_valve_result` 必须落在可接受执行结果集合，`regeneration_event` 必须可解析为布尔值。
  - `minimum_replay_contract_audit` 新增 `valid_operation_action_count`、`invalid_operation_action_count`，并把有效共同批次推进为 sensor/lab/operation/proxy 四表共同 batch 与有效 action/lab/proxy batch 的交集。
  - 新增 `minimum_replay_contract_operation_action_quality_gaps` 状态；当共同 batch 足够但有效操作动作不足时，阻断 replay。
  - `patch_plan` 新增 `R7I_OPERATION_ACTION_QUALITY`，输出无效 action 行、必需字段、可接受泵阀结果和当前有效动作数。
- 更新 `src/water_ai/real_field_replay_pipeline.py`：
  - 在 `pipeline_readiness` 中加入 `minimum_valid_operation_action_count` 与 `minimum_invalid_operation_action_count`。
- 更新 `src/water_ai/agents/agent_architecture_consolidation_agent.py`：
  - Agent60 的 R7 trigger metric 现在包含有效/无效 operation action 数。
  - R7i implementation path 明确要求同批次有效 action/lab/proxy 证据，而不是只补操作日志行。
- 更新 `experiments/run_r7_real_field_replay_pipeline.py` 与 `experiments/run_agent60_agent_architecture_consolidation.py`：
  - 报告、deliverable、manifest 和 next_stage rationale 同步显示有效/无效 operation action 数。
- 扩展测试：
  - 构造共同 batch 齐、lab/proxy 可用，但 operation action 的 `recycle_ratio`、`tank_storage_margin`、`actuator_latency_p90`、`pump_valve_result`、`hold_time_min` 等字段不合理的真实包。
  - 断言状态切到 `minimum_replay_contract_operation_action_quality_gaps`，并生成 `R7I_OPERATION_ACTION_QUALITY`。
  - R7 pipeline 和 Agent60 测试断言新指标被消费。

结果：

- 当前 header-only template 演练：
  - `minimum_replay_contract_status=minimum_replay_contract_blocked_missing_rows`。
  - `minimum_common_batch_count=0`。
  - `minimum_valid_matched_batch_count=0`。
  - `minimum_valid_operation_action_count=0`。
  - `minimum_invalid_operation_action_count=0`。
  - `minimum_valid_lab_result_count=0`。
  - `minimum_valid_proxy_label_count=0`。
  - 最高边际价值仍为 `R7a_import_real_field_package_with_metadata_and_csv`，因为当前还未通过 preflight/import。
- 定向回归：
  - `.venv/bin/pytest -q tests/test_field_package_coverage.py tests/test_real_field_replay_pipeline.py tests/test_agent_architecture_consolidation_agent.py`：33 passed。
- 完整回归：
  - `.venv/bin/pytest -q`：330 passed。

结论：

- R7 现在可以区分六类真实包问题：真实来源未导入、字段/标签覆盖不足、跨表共同批次/时间轴不足、operation action 不可作为控制证据、offline lab 标签不可采信、proxy 标签语义不可用于校准。
- 这直接服务“循环结构换时间、动作证据支撑闭环”的第一性原理：只有回流、暂存、延长停留、泵阀执行和放行策略这些动作本身可信，后续多设施协同控制 replay 才能从 synthetic baseline 进入 field-validation-ready。

## Agent48 Sparse Placement Matrix Diagnostics

目标：

- 自我打断后从 R7 gate 细化回到观测第一性原理：低成本传感能否支撑隐藏状态估计，不能只看 coverage 最大值，还要看稀疏观测矩阵是否稳定、是否有弱轴缺口、是否依赖单个传感点。
- 在不破坏 Agent49/54/60 既有消费字段的前提下，为 Agent48 增加可比较诊断层，作为后续 field topology benchmark 和更正式稀疏布点算法升级的基准。

实现：

- 更新 `src/water_ai/agents/sensor_network_sparse_placement_agent.py`：
  - 新增 `placement_diagnostics`。
  - 输出 `selected_matrix_rank`、`axis_span_rank_ratio`、`singular_values`、`condition_number_proxy`、`inverse_condition_score`、`reconstruction_stability_score`、`layout_redundancy_score`。
  - 新增 `weak_axis_gaps`，把每个低覆盖 hidden-state axis 的当前覆盖、目标阈值、候选池最佳传感点和是否可由当前候选池补足写出。
  - 新增 `critical_sensor_dependencies`，通过 leave-one-sensor drop 找出单点依赖。
  - 将诊断摘要写入 `soft_sensor_interface`，让 Agent54/软传感输入合同后续可以消费。
  - 在 `algorithm_comparison` 中加入 rank ratio、condition number、weak axis gap count、single point dependency 和 layout redundancy，避免策略比较只停留在 coverage/成本层。
- 更新 `experiments/run_agent48_sensor_network_sparse_placement.py`：
  - `outputs/sensor_network_sparse_placement/sparse_placement_metrics.json` 写入 `placement_diagnostics`。
  - `deliverables/sensor_network_sparse_placement.md` 和 `outputs/agent48_sensor_network_sparse_placement/agent48_report.md` 展示矩阵稳定性、弱轴缺口和单点依赖。
- 扩展 `tests/test_sensor_network_sparse_placement_agent.py`：
  - 验证诊断进入 soft sensor interface。
  - 验证每个 strategy comparison 都带矩阵诊断字段。
  - 验证默认方案暴露 `catalyst_activity_observability` 弱轴缺口、condition number 和单点依赖。

结果：

- 当前默认 Agent48：
  - selected strategy：`greedy_marginal`。
  - selected matrix rank：6。
  - axis_span_rank_ratio：0.667。
  - condition_number_proxy：61.726。
  - reconstruction_stability_score：0.401。
  - weak_axis_gap_count：2。
  - `catalyst_activity_observability` 当前覆盖 0.300，目标 0.550，候选池最佳 `N3_catalyst_bed_outlet:UV254_abs` 为 0.404，说明当前候选池本身不能把催化剂活性观测补足到目标线。
- 定向回归：
  - `.venv/bin/pytest -q tests/test_sensor_network_sparse_placement_agent.py`：7 passed。
  - `.venv/bin/pytest -q tests/test_sensor_network_sparse_placement_agent.py tests/test_observation_contract.py tests/test_soft_sensor_matrix_coupling_agent.py tests/test_multi_facility_collaborative_control_agent.py`：18 passed。
- 完整回归：
  - `.venv/bin/pytest -q`：331 passed。

结论：

- Agent48 现在从“选了 6 个传感点”推进到“能诊断这个低成本观测矩阵哪里不稳、哪里缺轴、哪里单点依赖”。
- 这一步直接服务第一性原理中的观测基础：如果 catalyst_activity 这类关键隐藏状态不可观测，后续软传感、故障诊断和多设施控制都必须承认这个边界，而不能把 coverage 表面的高分误当成真实可观测性。

## Agent48 -> Agent51 -> R2 -> Agent49 Catalyst Weak Axis Repair Chain

目标：

- 承接 Agent48 新增的稀疏观测矩阵诊断，不再停留在“catalyst_activity 是弱轴”的描述层，而是把它转成可执行的修复链。
- 让 Agent51 明确消费 Agent48 的 `weak_axis_gaps`，判断当前低成本候选池是否能自然补足 catalyst_activity；若不能，则输出代理补点、现场标签和证据需求。
- 让 R2 observation contract 和 Agent49 控制上下文都消费该 repair plan，形成“诊断 -> 修复设计 -> 预算重平衡 -> 控制边界”的闭环。

实现：

- 更新 `src/water_ai/agents/catalyst_activity_proxy_agent.py`：
  - `_sparse_context()` 读取 Agent48 `placement_diagnostics` 和 `agent48_catalyst_axis_gap`。
  - 新增 `weak_axis_repair_plan`，输出 `repair_status`、`repair_score`、`prioritized_proxy_patches` 和 `field_repair_evidence_requirements`。
  - 当前 repair_status 为 `agent48_catalyst_axis_requires_proxy_patch_and_field_label`，说明 Agent48 候选池最佳值也无法把 catalyst_activity 补到 0.55。
  - 优先修复信号排序为床出口 UV254、床出口 ORP、催化剂床压降，并补充再生事件、离线标签、床体积/HRT 等 field holdout 要求。
  - Agent49 interface 中加入 `weak_axis_repair_status` 和 `prioritized_proxy_patches`，但仍保留 synthetic 阶段不能解除催化剂保护的边界。
- 更新 `src/water_ai/observation_contract.py`：
  - R2 patch records 消费 Agent51 的 repair priority。
  - `budget_rebalanced_proxy_contract` 现在不仅看 patch list，还继承 weak-axis repair status、repair score 和现场证据需求计数。
  - 推荐合同继续加入 `N3_catalyst_bed_outlet:UV254_abs` 和 `N3_catalyst_bed_outlet:ORP_mV`，移除 `N5_polishing_inlet:turbidity_NTU`，在预算 5.8 内把 weak_state_coverage 提到 0.580。
- 更新 `src/water_ai/agents/multi_facility_collaborative_control_agent.py`：
  - Agent49 observation contract context 携带 `weak_axis_repair_status`、`weak_axis_repair_score` 和 `field_repair_evidence_requirement_count`。
  - 新增 `catalyst_axis_repair_prior_not_field_validated` 边界，明确 Agent49 可以用修复先验更新状态向量，但 field proxy labels 前不能解除催化剂保护规则。
- 更新实验输出：
  - `experiments/run_agent51_catalyst_activity_proxy.py` 写出 `weak_axis_repair_plan`。
  - `experiments/run_observation_contract_merge.py` 写出 weak-axis repair records。
  - 刷新 Agent49 报告和协同控制指标。

结果：

- Agent51：
  - `weak_axis_repair_status=agent48_catalyst_axis_requires_proxy_patch_and_field_label`。
  - `repair_score=0.983`。
  - `current_axis_coverage=0.300`，target=0.550，proxy_projected_axis_coverage=0.720。
  - 现场修复证据需求覆盖 `sensor_timeseries`、`campaign_operation_log`、`offline_lab_results` 和 `site_topology_or_bed_geometry`。
- R2：
  - `recommended_contract_id=budget_rebalanced_proxy_contract`。
  - `proxy_enhanced_weak_state_coverage=0.580`。
  - `recommended_cost_index=5.272`，budget_pass=True。
  - `field_repair_evidence_requirement_count=4`。
- Agent49：
  - control context 消费 `weak_axis_repair_status`。
  - 新增 issue `catalyst_axis_repair_prior_not_field_validated`。
  - 仍保持 `can_write_to_actuator=False` 和 field replay 阻断。
- 定向回归：
  - `.venv/bin/pytest -q tests/test_catalyst_activity_proxy_agent.py tests/test_observation_contract.py tests/test_multi_facility_collaborative_control_agent.py`：14 passed。
- 完整回归：
  - `.venv/bin/pytest -q`：332 passed。

结论：

- catalyst_activity 弱观测现在不再只是 Agent48 coverage 的一个低分，而是已经进入可执行修复链：Agent48 诊断不可自然补足，Agent51 给出代理修复路径，R2 在预算内重平衡观测合同，Agent49 消费设计先验但保留现场验证边界。
- 这一步直接服务“低成本受限观测下黑箱变灰箱”的第一性原理：隐藏状态要先被诊断为不可见，再被转化为代理观测、现场标签和控制边界，而不是被 synthetic coverage 分数掩盖。

## R7j Agent51 Catalyst Proxy Field Holdout Contract

目标：

- 把 Agent51 的 `weak_axis_repair_plan` 从“设计先验/补点建议”推进为 R7 现场数据包能显式验收的证据契约。
- 解决上一轮留下的断点：Agent48/51/R2/49 已经知道 catalyst_activity 弱轴需要床出口 UV254/ORP、催化剂床压降、再生事件、HRT/床体积和离线活性标签，但 R7 field package 还没有检查这些证据是否真实进入同批次现场包。
- 保持第一性原理：不是继续加 agent，而是让“不可观测弱轴 -> 代理观测设计 -> 现场 holdout 验收 -> 控制边界”更闭合。

实现：

- 更新 `src/water_ai/field_package_coverage.py`：
  - `assess_field_package_coverage()` 新增 `catalyst_proxy_metrics` 输入。
  - 新增 `R7j_agent51_catalyst_proxy_holdout_contract`，消费 Agent51 `weak_axis_repair_plan.field_repair_evidence_requirements`。
  - 检查 `sensor_timeseries` 是否具备 node/modality/value/status 长表证据，覆盖 `N3_catalyst_bed_outlet:UV254_abs`、`N3_catalyst_bed_outlet:ORP_mV`、`N3_catalyst_bed:pressure_drop_kPa`。
  - 检查 `offline_lab_results` 是否具备 QA 通过的 `catalyst_activity` 和 `lab_label_time_min`。
  - 检查 `campaign_operation_log` 是否具备可解析 `regeneration_event`、`command_time_min`、`effect_time_min`。
  - 新增额外证据表 `site_topology_or_bed_geometry`，用于床体积、nominal HRT 和流量归一化。
  - 要求至少 3 个 batch_id 同时拥有完整 sensor、lab、operation 证据，形成 field proxy holdout smoke floor。
- 更新 `src/water_ai/real_field_replay_pipeline.py`：
  - `build_real_field_replay_pipeline()` 新增 `catalyst_proxy_metrics` 参数。
  - `pipeline_readiness` 输出 `field_proxy_holdout_status`、`field_proxy_holdout_required`、`field_proxy_holdout_coverage_pass`、`field_proxy_holdout_matched_batch_count`。
- 更新 `experiments/run_r7_real_field_replay_pipeline.py`：
  - 默认读取 `outputs/catalyst_activity_proxy/catalyst_activity_proxy_metrics.json`。
  - R7 报告、deliverable 和 manifest 增加 Agent51 catalyst proxy holdout 字段。
- 更新测试：
  - `tests/test_field_package_coverage.py` 增加缺失 R7j 证据被拦截、补齐 R7j 证据后通过两类测试。
  - `tests/test_real_field_replay_pipeline.py` 增加端到端 pipeline 暴露 Agent51 holdout gap 的测试。

结果：

- 当前默认 R7 template 演练：
  - `field_package_coverage_status=field_package_coverage_blocked_before_import`。
  - `field_proxy_holdout_status=field_proxy_holdout_coverage_gaps`。
  - `field_proxy_holdout_required=True`。
  - `field_proxy_holdout_coverage_pass=False`。
  - `field_proxy_holdout_matched_batch_count=0`。
- 这是正确边界：模板仍首先阻断在 R7a import；R7j 不绕过 import，只在真实包进入后继续检查 Agent51 催化剂代理证据是否可做 holdout。
- 定向回归：
  - `.venv/bin/pytest -q tests/test_field_package_coverage.py tests/test_real_field_replay_pipeline.py`：15 passed。
- 完整回归：
  - `.venv/bin/pytest -q`：335 passed。

结论：

- Agent51 的催化剂弱轴修复现在不再只是“建议采集什么”，而是变成 R7 能执行的现场包验收门。
- 这一步提升的是可验证性和可观测性：只有真实包提供节点级低成本信号、离线活性标签、再生事件和床体/HRT 归一化证据后，catalyst proxy 才有资格从 synthetic design prior 进入 field_proxy_holdout 验证。
- 即使 R7j 通过，也仍不能直接写执行器或 release gate；它只解除“是否具备 Agent51 holdout 数据”的证据入口问题，后续还要经过 Agent51 field run、R2/R7/R3 控制 replay 和人工/统一证据门控。

## R7j Field Package Template Supplement

目标：

- 上一轮已经让 R7 coverage 能检查 Agent51 catalyst proxy holdout，但真实采集模板本身还没有显式提供这些字段。
- 本轮把 R7j 的证据要求前移到 Agent44 真实包模板，并把主 replay 宽表与节点级 holdout supplement 解耦，避免未来真实采集包进入后才发现缺 `node_id/modality/value/sensor_status` 或床体/HRT 表，也避免污染主 `sensor_timeseries.csv`。
- 保持边界：R7j supplement 对 Agent44 最低导入是 optional；只有当 R7 coverage 消费 Agent51 `weak_axis_repair_plan` 时，它才成为 catalyst proxy field holdout 的验收要求。

实现：

- 更新 `src/water_ai/agents/field_replay_import_agent.py`：
  - 新增 `R7J_CATALYST_PROXY_TEMPLATE_HEADERS`。
  - `field_replay_package_template_spec()` 的 `csv_headers` 现在包含：
    - `sensor_timeseries.csv`：保留主 replay 宽表，只补 `sensor_status`、`instrument_id`、`acquisition_time_min`、`ingest_time_min`。
    - `node_modality_sensor_timeseries.csv`：`batch_id`、`timestamp_min`、`node_id`、`zone`、`modality`、`value`、`sensor_status`、`instrument_id`、`acquisition_time_min`、`ingest_time_min`。
    - `offline_lab_results.csv`：`lab_label_time_min`、`detection_limit`、`method`、`unit`。
    - `site_topology_or_bed_geometry.csv`：`node_id`、`bed_volume`、`nominal_HRT_min`、`flow_Lmin`。
  - `write_field_replay_package_template()` 现在写出 `node_modality_sensor_timeseries.csv` 和 `site_topology_or_bed_geometry.csv` header-only supplement。
  - `preflight_field_replay_package()` 现在输出 `r7j_supplement_audit`。
  - `import_schema.json` 暴露 `template_headers`、`optional_supplement_files` 和 `r7j_catalyst_proxy_holdout_template`。
- 更新 `experiments/run_agent44_field_replay_import.py`：
  - 新增 `outputs/field_replay_import/real_field_package_template_preflight_metrics.json`，专门记录模板 preflight，而不是混同当前输入包 preflight。
  - Agent44 报告和 `deliverables/field_replay_import_protocol.md` 显示当前输入包 supplement 状态，以及真实模板 supplement 状态。
- 更新 `experiments/run_r7_real_field_replay_pipeline.py`：
  - 修正 manifest 更新逻辑，保留 R7j field proxy holdout 审计口径。

结果：

- 当前模板目录 `outputs/field_replay_import/real_field_package_template/` 已包含：
  - `sensor_timeseries.csv`
  - `offline_lab_results.csv`
  - `campaign_operation_log.csv`
  - `fast_proxy_event_log.csv`
  - `node_modality_sensor_timeseries.csv`
  - `site_topology_or_bed_geometry.csv`
  - `metadata.json`
- 模板专用 preflight：
  - `real_field_package_template_preflight_metrics.json`
  - status=`field_package_template_ready_needs_real_values_and_rows`
  - R7j supplement `node_modality_sensor_timeseries` 与 `site_topology_or_bed_geometry` status=`supplement_header_ready`
- 当前输入包 preflight 仍为 synthetic/non-field：
  - status=`field_package_preflight_blocked_non_field_origin`
  - 这是正确阻断，不能当成 field evidence。
- 定向回归：
  - `.venv/bin/pytest -q tests/test_field_replay_import_agent.py tests/test_field_package_coverage.py tests/test_real_field_replay_pipeline.py`：24 passed。
- 完整回归：
  - `.venv/bin/pytest -q`：335 passed。

结论：

- 这一步把“R7j 要什么证据”从 coverage 报错后移，前移到了真实现场包采集入口。
- 对第一性原理的贡献是提升可验证性和可部署性：现场团队拿到模板时就能把主 replay 宽表、N3 节点级低成本信号、催化剂活性标签和床体/HRT 信息分表采集，而不是继续停留在“以后需要 field_proxy_holdout”的抽象提醒。

## R7j Node-Modality Supplement Separation

目标：

- 自我打断评估发现：如果把 `node_id/modality/value` 直接塞进主 `sensor_timeseries.csv`，真实采集时会被迫在每条节点级 N3 压差/ORP/UV254 行里补齐全局 EC、浊度、pH 等宽表字段，容易污染 Agent44/42 主 replay。
- 因此本轮把 R7j 节点级信号从主 replay 表中拆出，建立独立 `node_modality_sensor_timeseries.csv` supplement。

实现：

- `src/water_ai/agents/field_replay_import_agent.py`：
  - `sensor_timeseries.csv` 只保留主 replay 宽表和通用质量字段。
  - `node_modality_sensor_timeseries.csv` 承接 `batch_id/timestamp_min/node_id/zone/modality/value/sensor_status/instrument_id/acquisition_time_min/ingest_time_min`。
- `src/water_ai/field_package_coverage.py`：
  - R7j sensor audit 优先读取 `node_modality_sensor_timeseries.csv`。
  - 若历史包已经把 long-table 字段放进 `sensor_timeseries.csv`，仍保留兼容路径。
  - R7j patch plan 现在指向 `node_modality_sensor_timeseries`，不再要求污染主 `sensor_timeseries`。
- 测试：
  - R7j-ready fixture 主 `sensor_timeseries` 保持 3 行宽表，N3 UV254/ORP/压差信号进入 `node_modality_sensor_timeseries.csv`。
  - 新增断言确保 R7j 通过时 `sensor_signal_audit.source_table=node_modality_sensor_timeseries`。

结果：

- 定向回归：`.venv/bin/pytest -q tests/test_field_replay_import_agent.py tests/test_field_package_coverage.py tests/test_real_field_replay_pipeline.py`：24 passed。
- 完整回归：`.venv/bin/pytest -q`：335 passed。

结论：

- 这一步不是增加新 agent，而是修正真实工程数据结构：主 replay 宽表负责时间戳回放，node-modality supplement 负责稀疏节点级 holdout，二者通过 batch_id/timestamp_min 关联。

## Agent51 Field Proxy Holdout Summary Consumption

目标：

- 上一轮已经让 R7j 能检查真实包是否具备 Agent51 catalyst proxy holdout 证据，但 Agent51 本身仍主要依赖手填 `field_validation` 指标。
- 本轮把“有数据入口”推进到“Agent51 能消费入口”：从 R7j package 中直接提取节点级 N3 UV254/ORP/压差、QA 通过的 `catalyst_activity` 标签、再生事件和床体/HRT，生成可评分 holdout rows。
- 这一步服务第一性原理中的“黑箱变灰箱”和“证据门控”：催化剂活性不再只是 synthetic proxy design，而是具备从真实稀疏传感包进入 field validation 的计算路径。

实现：

- 新增 `src/water_ai/catalyst_proxy_field_holdout.py`：
  - `build_catalyst_proxy_field_holdout_summary(package_dir)` 读取 `sensor_timeseries.csv`、`node_modality_sensor_timeseries.csv`、`offline_lab_results.csv`、`campaign_operation_log.csv` 和 `site_topology_or_bed_geometry.csv`。
  - 输出 matched_batch_count、scoreable_batch_count、field_label_coverage、proxy_label_correlation、holdout_mae、feature_rows、invalid_rows 和写回边界。
  - 只有同一 batch 同时具备节点级信号、催化剂活性标签、再生事件和床体/HRT 时，才进入 scoreable rows。
- 更新 `src/water_ai/agents/catalyst_activity_proxy_agent.py`：
  - 新增 `field_proxy_holdout_summary` 输入。
  - 如果摘要达到 `ready_for_agent51_validation=True`，Agent51 自动把 data_origin 升级为 `field_proxy_holdout`。
  - field validation 指标可由摘要自动写入，但仍要求相关性、MAE 和标签覆盖达标后才允许 `can_relax_agent49_catalyst_uncertainty_block=True`。
  - 即使达标，也仍保持 `can_write_to_actuator=False`、`can_write_to_release_gate=False`。
  - `weak_axis_repair_plan` 的 low-cost sensor evidence table 更新为 `node_modality_sensor_timeseries`，避免回到污染主 `sensor_timeseries` 的旧结构。
- 更新 `src/water_ai/real_field_replay_pipeline.py`：
  - 当提供 catalyst_proxy_metrics 时，pipeline 同步输出 `agent51_field_proxy_holdout_summary`。
  - `pipeline_readiness` 增加 `agent51_field_proxy_summary_status`、`agent51_field_proxy_scoreable_batch_count`、`agent51_field_proxy_validation_pass`、`agent51_field_proxy_holdout_mae`、`agent51_field_proxy_label_correlation`。
- 更新 `experiments/run_agent51_catalyst_activity_proxy.py`：
  - 生成 `outputs/catalyst_activity_proxy/field_proxy_holdout_summary.json`。
  - Agent51 report 和 deliverable 显示 field summary 状态、可评分批次数和边界。
- 更新 `experiments/run_r7_real_field_replay_pipeline.py`：
  - R7 report、deliverable 和 manifest 增加 Agent51 field summary 指标。

结果：

- 当前 header-only template 演练：
  - `field_proxy_holdout_summary_status=field_proxy_holdout_coverage_gaps`。
  - matched_batch_count=0。
  - scoreable_batch_count=0。
  - field_validation_pass=False。
- 这是正确阻断：模板不能成为 field evidence；它只证明接口存在、字段结构能被检查。
- 新增测试覆盖：
  - 完整 R7j package 能提取 3 条 scoreable Agent51 holdout rows，并生成通过阈值的 correlation/MAE。
  - 缺 `node_modality_sensor_timeseries` 时，Agent51 必须保持 field validation 阻断。
  - R7 pipeline 能把 coverage gate 与 Agent51 summary status 同时暴露出来。
- 定向回归：
  - `.venv/bin/pytest -q tests/test_catalyst_activity_proxy_agent.py tests/test_field_package_coverage.py tests/test_real_field_replay_pipeline.py`：21 passed。
- 完整回归：
  - `.venv/bin/pytest -q`：337 passed。

结论：

- Agent51 的催化剂活性代理链条现在从“设计代理 + 采集需求”推进到“可从真实包提取 holdout 验证输入”。
- 对模型核心的贡献是把不可直接观测的 `catalyst_activity` 从黑箱隐藏状态进一步推向灰箱可验证状态：低成本节点信号、离线标签、再生事件和 HRT 共同形成代理评分行。
- 仍然不能把摘要通过等同于 field-supported 控制结论；它只允许进入 Agent51 field validation，再继续进入 Agent49 replay、统一证据门控和人工复核。

## R3d Agent51 Holdout Summary -> Agent49/52 Control Guardrail

目标：

- 上一轮已经让 Agent51 能从 R7j package 提取 catalyst proxy field holdout summary，但这个结果还没有真正进入多设施协同控制链。
- 本轮把 Agent51 的 `field_proxy_holdout_summary` 向下游传递给 Agent49 和 Agent52，避免控制侧只看粗粒度 `field_validated` 布尔值。
- 核心问题是：即使多设施 replay 指标看起来达标，如果 `catalyst_activity` 代理还没有真实 holdout 证据，催化剂保护/再生相关动作仍不能升级为执行器候选。

实现：

- 更新 `src/water_ai/agents/multi_facility_collaborative_control_agent.py`：
  - 新增 `catalyst_proxy_metrics` 输入。
  - `sparse_context` 增加 `catalyst_proxy_field_context`。
  - `control_replay_guardrail_context` 增加：
    - `catalyst_proxy_summary_status`
    - `catalyst_proxy_ready_for_agent51_validation`
    - `catalyst_proxy_field_validation_pass`
    - `catalyst_proxy_scoreable_batch_count`
    - `catalyst_proxy_holdout_mae`
    - `catalyst_proxy_label_correlation`
    - `catalyst_guardrail_mode`
  - R3G1 的原因不再只是“field proxy labels not ready”，而是带上 Agent51 summary 状态和可评分批次数。
  - 当 Agent51 summary 未过线时，Agent49 输出 `agent51_catalyst_proxy_not_ready_for_control_relaxation` 问题；当 summary 通过时，只取消 R3G1 reward penalty，不自动写执行器。
- 更新 `experiments/run_agent49_multi_facility_collaborative_control.py`：
  - 读取 `outputs/catalyst_activity_proxy/catalyst_activity_proxy_metrics.json`。
  - 报告中显示 catalyst proxy summary status、scoreable batch count 和 guardrail mode。
- 更新 `src/water_ai/agents/multi_facility_replay_evaluation_agent.py`：
  - replay required fields 增加 `catalyst_proxy_summary_status`、`catalyst_proxy_validation_pass`、`catalyst_proxy_scoreable_batch_count`。
  - `offline_evaluation_metrics` 增加 Agent51 summary/validation 相关指标。
  - `field_ready` 现在必须同时满足 `catalyst_proxy_field_validation_pass=True`；否则即使 field replay coverage、joint action accuracy、reward regret 和 distillation accuracy 达标，也不能提升 Agent49 催化剂相关策略。
  - 新增 `catalyst_proxy_field_validation_blocks_agent49_promotion` 问题。
- 更新 `experiments/run_agent52_multi_facility_replay_evaluation.py`：
  - 报告和 deliverable 展示 Agent51 catalyst proxy context。

结果：

- 当前模板演练下：
  - Agent49 `catalyst_proxy_summary_status=field_proxy_holdout_coverage_gaps`。
  - Agent49 `catalyst_proxy_scoreable_batch_count=0`。
  - Agent49 `catalyst_guardrail_mode=agent51_holdout_coverage_gaps_keep_catalyst_guardrail`。
  - Agent52 `catalyst_proxy_field_validation_pass=False`。
- 因此：
  - J2 `catalyst_protection_before_regeneration` 仍受 R3G1 penalty。
  - J4 `safe_low_cost_standby` 仍获得 R3G1 guardrail bonus。
  - Agent52 只能更新 replay schema/reward prior，不能把 Agent49 升级为执行器候选。
- 定向回归：
  - `.venv/bin/pytest -q tests/test_multi_facility_collaborative_control_agent.py tests/test_multi_facility_replay_evaluation_agent.py`：14 passed。
  - `.venv/bin/pytest -q tests/test_catalyst_activity_proxy_agent.py tests/test_real_field_replay_pipeline.py tests/test_multi_facility_collaborative_control_agent.py tests/test_multi_facility_replay_evaluation_agent.py`：23 passed。
- 完整回归：
  - `.venv/bin/pytest -q`：341 passed。

结论：

- 这一步把 Agent51 的“灰箱可验证状态”真正传入了控制层：观测层的 holdout 证据不足会直接阻断控制层的催化剂保护/再生晋级。
- 这比继续增加 agent 更有模型价值，因为它减少了链路断点：R7j package -> Agent51 holdout summary -> Agent49 reward guardrail -> Agent52 replay readiness 现在形成闭环。
- 当前仍然不是 field-supported 控制；真实包缺失导致 scoreable batch 为 0，所以控制边界保持阻断是正确结果。

## R7S4b Agent49/52 Control Promotion Gate -> R7 Acceptance

目标：

- 前序 R3d 已让 Agent51 catalyst proxy holdout summary 进入 Agent49/52 控制链，但 R7 上层真实包验收仍可能只看 Agent45 field replay evidence chain。
- 本轮把 Agent52 的多设施 replay 晋级门和 Agent51 催化剂代理 field validation 结果提升到 R7 acceptance facade，确保“控制候选输出”不能绕过催化剂 holdout 证据。
- 这一步服务第一性原理中的控制可验证性：低成本稀疏感知和软传感链条没有通过前，多设施协同控制只能保持 protected/review 候选，不能进入执行器或自动放行。

实现：

- 更新 `src/water_ai/real_field_package_acceptance_gate.py`：
  - 新增 `multi_facility_replay_evaluation_metrics` 输入。
  - acceptance matrix 增加 `R7S4b_multi_facility_control_promotion`。
  - 该阶段同时要求 Agent52 `field_ready=True` 和 `catalyst_proxy_field_validation_pass=True`。
  - `can_emit_protective_control_candidate` 现在必须同时满足 `R7S4_field_replay_evidence_chain` 和 `R7S4b_multi_facility_control_promotion`。
  - 新增阻断状态 `real_field_package_acceptance_blocked_at_multi_facility_control_gate`，下一步动作指向 `R7c_validate_agent49_52_control_replay_and_agent51_catalyst_holdout`。
- 更新 `src/water_ai/real_field_replay_pipeline.py`：
  - pipeline 可传入 Agent52 replay evaluation metrics。
  - `pipeline_readiness` 暴露 `multi_facility_control_promotion_pass` 和 `catalyst_proxy_field_validation_pass`。
- 更新 `experiments/run_real_field_package_acceptance_gate.py` 和 `experiments/run_r7_real_field_replay_pipeline.py`：
  - 默认读取 `outputs/multi_facility_replay_evaluation/replay_evaluation_metrics.json`。
  - report、deliverable 和 manifest 写入 control promotion/catalyst validation 状态。
- 更新测试：
  - R7 gate 在 field evidence chain 通过、但 Agent52/Agent51 control promotion 失败时，必须阻断在 `R7S4b_multi_facility_control_promotion`。
  - 只有 control promotion ready 时，完整 field package 才能继续路由到 soft sensor holdout gate。

结果：

- 当前 header-only template 演练：
  - R7 status：`real_field_package_acceptance_blocked_at_import`。
  - passed_stage_count：0/8。
  - `multi_facility_control_promotion_pass=False`。
  - `catalyst_proxy_field_validation_pass=False`。
  - `can_emit_protective_control_candidate=False`。
- 这是正确阻断：当前没有真实 `data_origin=field` package、没有 Agent51 可评分 catalyst proxy holdout rows，也没有 Agent52 field-ready replay 评价。

验证：

- 定向回归：
  - `.venv/bin/pytest -q tests/test_real_field_package_acceptance_gate.py tests/test_real_field_replay_pipeline.py`：7 passed。
- R7 实验脚本：
  - `.venv/bin/python experiments/run_real_field_package_acceptance_gate.py`：运行成功，状态为 `real_field_package_acceptance_blocked_at_import`，通过阶段 0/8。
  - `.venv/bin/python experiments/run_r7_real_field_replay_pipeline.py`：运行成功，状态为 `real_field_package_acceptance_blocked_at_import`，下一步为 `R7a_import_real_field_package_with_metadata_and_csv`。
- 完整回归：
  - `.venv/bin/pytest -q`：342 passed。

结论：

- R7 现在不再只是“真实包导入与 replay/holdout 验收”，而是把控制晋级也纳入同一个证据门控面。
- 这减少了核心链路断点：Agent51 holdout summary -> Agent49 reward guardrail -> Agent52 replay readiness -> R7 package acceptance 已形成上层闭环。
- 当前仍然不能产生 field-supported 控制结论；R7S4b 的作用是阻断不可靠晋级，而不是证明控制有效。

## R8 Agent48 Hidden-State Requirement Ledger and Offline Core Fallback

目标：

- 当前 Agent60 仍正确地把 R7a 真实 field package 导入识别为最高证据价值动作，但如果没有真实包，模型优化不能停在等待数据。
- 本轮沿第一性原理回到观测根基：低成本稀疏传感的关键不是只输出 coverage，而是回答“每个不可直接观测的隐藏状态需要哪些 node、modality、field label 和证据边界支撑”。
- 因此本轮不新增新 agent，而是在 Agent48/R2/Agent60 现有链路内增加可机读 hidden-state requirement ledger 和 offline fallback。

实现：

- 更新 `src/water_ai/agents/sensor_network_sparse_placement_agent.py`：
  - 新增 `hidden_state_requirement_ledger`。
  - 覆盖六类隐藏状态：
    - `pollutant_residual`
    - `reaction_completion`
    - `catalyst_activity`
    - `matrix_interference`
    - `hydraulic_delay`
    - `release_or_byproduct_risk`
  - 每个 hidden state 输出：
    - `primary_axes`
    - `secondary_axes`
    - `required_zones`
    - `required_modalities`
    - `field_evidence_needed`
    - `candidate_patch`
    - `unresolved_requirements`
    - `ready_for_soft_sensor_estimation`
    - `ready_for_control_use`
  - 新增 `minimum_cost_requirement_patch`，把隐藏状态缺口转成最小补点/补证据建议。
- 更新 Agent48 soft sensor interface：
  - 增加 `hidden_state_requirement_contract`，让 Agent54/软传感侧可以看到 hidden-state readiness，而不是只消费 selected nodes/modalities。
- 更新 `src/water_ai/observation_contract.py`：
  - R2 observation contract 读取 Agent48 hidden-state ledger。
  - readiness 增加：
    - `agent48_hidden_state_ledger_status`
    - `agent48_hidden_state_ready_count`
    - `agent48_hidden_state_minimum_patch_status`
    - `agent48_hidden_state_hard_unresolved`
  - field validation requirements 增加 `R2_FV4_agent48_hidden_state_requirement_patch`。
- 更新 `src/water_ai/agents/agent_architecture_consolidation_agent.py`：
  - 新增 `offline_core_fallback_action`。
  - 当 top action 是 R7a 且 R7 仍阻断在 import 时，如果 Agent48 ledger 暴露 hard-unresolved hidden state，则 fallback 指向 `R8b_agent48_pressure_headloss_candidate_pool_design`。
  - 这样不改写“真实包最高价值”的事实，但避免没有真实包时停止模型核心优化。
- 更新实验脚本：
  - `experiments/run_agent48_sensor_network_sparse_placement.py` 输出 hidden-state ledger 和 minimum patch。
  - `experiments/run_observation_contract_merge.py` 输出 Agent48 hidden-state ledger 在 R2 中的消费状态。
  - `experiments/run_agent60_agent_architecture_consolidation.py` 输出 offline fallback，并把 R7 验收口径更新为八阶段。

结果：

- Agent48 当前默认 synthetic topology prior：
  - `hidden_state_requirement_ledger_status=hidden_state_requirement_ledger_ready_with_gaps`。
  - ready hidden states：4/6。
  - `minimum_cost_patch_status=minimum_cost_patch_requires_new_modality_or_field_label`。
  - hard-unresolved hidden state：`catalyst_activity`。
- 具体含义：
  - `pollutant_residual`、`reaction_completion`、`hydraulic_delay`、`release_or_byproduct_risk` 已能作为 soft-sensor design prior。
  - `matrix_interference` 接近目标但仍需 field topology/labels。
  - `catalyst_activity` 不能靠当前候选池简单加点解决，需要 pressure/headloss proxy、catalyst_activity field label、regeneration_event 和 HRT/床体几何证据。
- R2 observation contract：
  - 继续推荐 `budget_rebalanced_proxy_contract`。
  - weak_state_coverage 仍为 0.300 -> 0.580。
  - 新增 `R2_FV4_agent48_hidden_state_requirement_patch`，把 Agent48 hard unresolved state 转成现场补包需求。
- Agent60：
  - top action 仍是 `R7a_import_real_field_package_with_metadata_and_csv`。
  - offline fallback 为 `R8b_agent48_pressure_headloss_candidate_pool_design`。

验证：

- 定向回归：
  - `.venv/bin/pytest -q tests/test_sensor_network_sparse_placement_agent.py tests/test_observation_contract.py tests/test_agent_architecture_consolidation_agent.py tests/test_multi_facility_collaborative_control_agent.py`：44 passed。
- 完整回归：
  - `.venv/bin/pytest -q`：346 passed。

结论：

- 这一步让 M1 低成本稀疏感知从“选了哪些传感器”升级为“这些传感器能支撑哪些隐藏状态、哪些状态仍是硬缺口、缺口应该用什么现场证据补”。
- 这比继续增加 agent 更重要，因为它把后续软传感、催化剂代理、R2 observation contract 和 Agent60 自我打断都接回同一个观测根基。
- 当前仍然是 synthetic/design-prior，不是 field-supported；pressure/headloss 和 catalyst label 只是下一步候选池/现场字段需求，不能解除 Agent49 控制保护。

## 2026-06-04 R8u-47：R8p Submission Readiness Review 回接 Agent60

目标：

- 承接 R8u-28/R8p 现场行包链路，继续沿“先保证可验证，再讨论智能化”的第一性原理推进。
- 不新增 Agent62，不生成展示材料，不伪造 field rows；只把 Agent61 已形成的 source/schema/provenance/bundle/temporal/semantic/downstream/R7 assembly 门控聚合成一个可被 Agent60 全局治理消费的 submission readiness gate。
- 让无真实包时的离线核心 fallback 不只知道“缺真实行包”，而能直接看到当前能否进入 R8v field replay/holdout、下一步 operator action 和 direct R8p/R7-to-R8p 两条修补路径的最高优先项。

实现：

- 更新 `experiments/run_agent61_pressure_resolution_replay_scenario_pack.py`：
  - 生成 `outputs/pressure_resolution_replay_scenario_pack/pressure_resolution_replay_rows_submission_readiness_review.json`。
  - 新增 `field_rows_submission_readiness_review`，按以下顺序聚合 gate：
    - source package。
    - schema/provenance/template marker。
    - same-batch bundle。
    - temporal window。
    - scenario semantic。
    - downstream routing。
    - R7-to-R8p work package assembly。
  - 当前默认状态为 `submission_readiness_review_blocked_at_source_package`，下一步 `R8p_fix_field_rows_source_preflight`。
- 更新 `src/water_ai/agents/agent_architecture_consolidation_agent.py`：
  - 新增 `_r8p_pressure_resolution_submission_readiness_review()`。
  - Agent60 offline fallback 现在透传：
    - `submission_readiness_review_status`
    - `submission_readiness_next_operator_action`
    - `submission_readiness_can_route_to_r8v`
    - `submission_readiness_direct_highest_priority_patch_id`
    - `submission_readiness_r7_highest_priority_patch_id`
    - `submission_readiness_review_path`
  - `trigger_metric` 和 `expected_metrics` 已纳入 submission readiness 字段。
- 更新 `experiments/run_agent60_agent_architecture_consolidation.py`：
  - Agent60 report/deliverable 输出 submission readiness 状态、下一步动作和 R8v 路由许可。
  - `deliverables/manifest.json` 新增 `latest_offline_core_fallback_submission_readiness_*` 字段。

当前结果：

- Agent61 submission readiness：
  - `submission_readiness_review_status=submission_readiness_review_blocked_at_source_package`
  - `next_operator_action=R8p_fix_field_rows_source_preflight`
  - `direct_r8p_highest_priority_patch_id=R8P_SOURCE_MISSING_FIELD_ROWS_FILE`
  - `r7_to_r8p_highest_priority_patch_id=R8U27_SET_R7_TO_R8P_WORK_PACKAGE_DIR`
  - `can_route_to_r8v=False`
- Agent60 fallback：
  - 仍为 `R8p_fix_field_rows_source_preflight`。
  - 已把 submission readiness review 状态写入 metrics、deliverable 和 manifest。
  - 原因文本中明确 R8u-47 是 R8v 入口门，而不是 field evidence。

验证：

- 语法检查：
  - `.venv/bin/python -m py_compile src/water_ai/agents/agent_architecture_consolidation_agent.py experiments/run_agent60_agent_architecture_consolidation.py tests/test_agent_architecture_consolidation_agent.py`
- 定向回归：
  - `.venv/bin/pytest -q tests/test_agent_architecture_consolidation_agent.py`：51 passed。
  - `.venv/bin/pytest -q tests/test_pressure_resolution_replay_scenario_pack_agent.py`：33 passed。
  - `.venv/bin/pytest -q tests/test_agent_architecture_consolidation_agent.py tests/test_pressure_resolution_replay_scenario_pack_agent.py`：84 passed。
- runner：
  - `.venv/bin/python experiments/run_agent61_pressure_resolution_replay_scenario_pack.py`：运行成功，生成 submission readiness review。
  - `.venv/bin/python experiments/run_agent60_agent_architecture_consolidation.py`：运行成功，manifest 已透传 submission readiness 字段。
- 完整回归：
  - `.venv/bin/pytest -q`：432 passed。

边界：

- submission readiness review 只是 R8p 到 R8v 的入口审查聚合，不是现场证据。
- 当前没有真实 pressure-resolution field rows，不能进入 R8v field replay/holdout，不能产生 field-supported 控制结论。
- 任何 actuator、release gate、protective control candidate 或现场 claim 仍必须等待真实行包、R8p acceptance、R8v replay/holdout、Agent51/49/52/R7 gate 和人工复核。

## 2026-06-04 R8u-48：R8p Source Package Submission Route Guide

目标：

- 承接 R8u-47 的 submission readiness review，继续把“source package 缺失”从状态码压成现场可执行路线。
- 不新增 Agent62，不制造真实数据，不绕过 R8p/R8v/R7 gate；只把 direct R8p JSON、direct R8p CSV directory 和 R7-to-R8p work package 三条入口并列成一个机器可读 route guide。
- 让 Agent60 全局 fallback 不仅知道当前阻断在 source package，还能给出推荐提交路线、下一步动作和可选路线数量。

实现：

- 更新 `experiments/run_agent61_pressure_resolution_replay_scenario_pack.py`：
  - 新增 `ROWS_SOURCE_PACKAGE_SUBMISSION_ROUTE_GUIDE_PATH`。
  - 新增 `_field_rows_source_package_submission_route_guide()`。
  - 输出 `outputs/pressure_resolution_replay_scenario_pack/pressure_resolution_replay_rows_source_package_submission_route_guide.json`。
  - metrics/report/deliverable/manifest 均接入 `field_rows_source_package_submission_route_guide`。
- route guide 包含三条提交路线：
  - `direct_r8p_json_table_mapping`：向默认 JSON 或 `PRESSURE_RESOLUTION_REPLAY_ROWS_PATH` 指定 JSON 提交六张 field-origin 表和 Agent52 replay 表。
  - `direct_r8p_csv_directory`：向 `metadata.json + required CSVs` 目录提交现场行。
  - `r7_to_r8p_route_work_package_submission`：通过 R7 source package、operator supplement、Agent52 replay export 和 R8p validation gates 四类 work package 装配 R8p candidate rows。
- 更新 `src/water_ai/agents/agent_architecture_consolidation_agent.py`：
  - 新增 `_r8p_pressure_resolution_source_package_route_guide()`。
  - Agent60 offline fallback 透传：
    - `source_package_route_guide_status`
    - `source_package_recommended_route_id`
    - `source_package_next_operator_action`
    - `source_package_route_option_count`
    - `source_package_route_guide_path`
- 更新 `experiments/run_agent60_agent_architecture_consolidation.py`：
  - Agent60 deliverable/report/manifest 输出 source package route guide 状态、推荐路线和下一步动作。

当前结果：

- Agent61 route guide：
  - `source_package_submission_route_guide_status=source_package_submission_route_guide_ready_for_source_package_submission`
  - `recommended_route_id=direct_r8p_json_or_csv_source_package`
  - `next_operator_action=R8p_submit_direct_json_or_csv_source_package`
  - `route_option_count=3`
  - `can_route_to_r8v=False`
  - `can_write_to_actuator=False`
  - `can_write_to_release_gate=False`
- Agent60 fallback：
  - 仍为 `R8p_fix_field_rows_source_preflight`。
  - trigger metric 已包含 `source_package_route_guide_status`、`source_package_recommended_route_id`、`source_package_next_operator_action` 和 `source_package_route_option_count`。
  - manifest 已同步 `latest_offline_core_fallback_source_package_*` 字段。

验证：

- 语法检查：
  - `.venv/bin/python -m py_compile src/water_ai/agents/agent_architecture_consolidation_agent.py experiments/run_agent60_agent_architecture_consolidation.py tests/test_agent_architecture_consolidation_agent.py experiments/run_agent61_pressure_resolution_replay_scenario_pack.py tests/test_pressure_resolution_replay_scenario_pack_agent.py`
- 定向回归：
  - `.venv/bin/pytest -q tests/test_pressure_resolution_replay_scenario_pack_agent.py`：33 passed。
  - `.venv/bin/pytest -q tests/test_pressure_resolution_replay_scenario_pack_agent.py tests/test_agent_architecture_consolidation_agent.py`：84 passed。
- runner：
  - `.venv/bin/python experiments/run_agent61_pressure_resolution_replay_scenario_pack.py`：运行成功，生成 source package route guide。
  - `.venv/bin/python experiments/run_agent60_agent_architecture_consolidation.py`：运行成功，Agent60 已透传 route guide。
- 完整回归：
  - `.venv/bin/pytest -q`：432 passed。

边界：

- route guide 是提交路线导引，不是 field evidence。
- route guide 不验证新行、不生成 Agent52 replay rows、不替代 R8p acceptance、R8v replay/holdout、Agent51/49/52/R7 gate 或人工复核。
- 当前仍无真实 pressure-resolution field rows；不能写 actuator、release gate、protective control candidate 或 field-supported claim。

## 2026-06-04 R8u-49：R8p Source Package Route Preflight

目标：

- 承接 R8u-48 的 source package submission route guide，把“有三条提交路线”继续压实为“每条路线当前 ready / waiting / blocked”。
- 不新增 Agent62，不改变 Agent61/Agent60 的控制主链，不伪造真实行包；只把 route guide 升级为机器可读预检门。
- 让 Agent60 全局 fallback 不只知道推荐路线，还能知道推荐路线当前是否可行动、ready/waiting/blocked 路线数量和下一步提交动作。

实现：

- 更新 `experiments/run_agent61_pressure_resolution_replay_scenario_pack.py`：
  - 新增 `ROWS_SOURCE_PACKAGE_ROUTE_PREFLIGHT_PATH`。
  - 新增 `_field_rows_source_package_route_preflight()`。
  - 输出 `outputs/pressure_resolution_replay_scenario_pack/pressure_resolution_replay_rows_source_package_route_preflight.json`。
  - metrics/report/deliverable/manifest 均接入 `field_rows_source_package_route_preflight`。
- route preflight 检查三条实际路线：
  - `direct_r8p_json_table_mapping`：检查当前 source 是否为 JSON table mapping、路径是否存在、source status 是否已加载或 invalid/missing。
  - `direct_r8p_csv_directory`：检查当前 source 是否为 `metadata.json + CSV directory`，并保留 CSV 目录路线的 waiting/loaded 边界。
  - `r7_to_r8p_route_work_package_submission`：消费 R7-to-R8p work package submission preflight 和 assembly gate，判断 work package 目录是否提交、是否通过、是否仍阻断。
- 当 R8p downstream routing 已可进入 R8v 时，preflight 会额外暴露 `route_to_r8v_field_replay_and_holdout_gates` ready 结果；不会伪装成真实 JSON/CSV 路径已存在。
- 更新 `src/water_ai/agents/agent_architecture_consolidation_agent.py`：
  - 新增 `_r8p_pressure_resolution_source_package_route_preflight()`。
  - Agent60 offline fallback 透传：
    - `source_package_route_preflight_status`
    - `source_package_recommended_route_preflight_status`
    - `source_package_route_preflight_next_operator_action`
    - `source_package_ready_route_count`
    - `source_package_waiting_route_count`
    - `source_package_blocked_route_count`
    - `source_package_route_preflight_path`
- 更新 `experiments/run_agent60_agent_architecture_consolidation.py`：
  - Agent60 deliverable/report/manifest 输出 route preflight 状态、推荐入口预检状态和 ready/waiting/blocked 计数。

当前结果：

- Agent61 route preflight：
  - `source_package_route_preflight_status=source_package_route_preflight_waiting_for_source_package_submission`
  - `recommended_route_id=direct_r8p_json_or_csv_source_package`
  - `recommended_route_preflight_status=recommended_route_preflight_waiting_for_direct_source_package`
  - `next_operator_action=R8p_submit_direct_json_or_csv_source_package`
  - `ready_route_count=0`
  - `waiting_route_count=3`
  - `blocked_route_count=0`
  - `can_route_to_r8v=False`
- 三条路线当前状态：
  - `direct_r8p_json_table_mapping=route_preflight_waiting_for_source_package_submission`
  - `direct_r8p_csv_directory=route_preflight_waiting_for_source_package_submission`
  - `r7_to_r8p_route_work_package_submission=route_preflight_waiting_for_r7_to_r8p_work_package_submission`
- Agent60 fallback：
  - 仍为 `R8p_fix_field_rows_source_preflight`。
  - trigger metric 已包含 route preflight 状态、推荐入口预检状态、下一步动作以及 ready/waiting/blocked 计数。
  - manifest 已同步 `latest_offline_core_fallback_source_package_route_preflight_*` 字段。

验证：

- 语法检查：
  - `.venv/bin/python -m py_compile experiments/run_agent61_pressure_resolution_replay_scenario_pack.py src/water_ai/agents/agent_architecture_consolidation_agent.py experiments/run_agent60_agent_architecture_consolidation.py tests/test_pressure_resolution_replay_scenario_pack_agent.py tests/test_agent_architecture_consolidation_agent.py`：通过。
- 定向回归：
  - `.venv/bin/pytest -q tests/test_pressure_resolution_replay_scenario_pack_agent.py`：33 passed。
  - `.venv/bin/pytest -q tests/test_agent_architecture_consolidation_agent.py`：51 passed。
- runner：
  - `.venv/bin/python experiments/run_agent61_pressure_resolution_replay_scenario_pack.py`：运行成功，生成 route preflight。
  - `.venv/bin/python experiments/run_agent60_agent_architecture_consolidation.py`：运行成功，Agent60 已透传 route preflight。
- 完整回归：
  - `.venv/bin/pytest -q`：432 passed。

边界：

- route preflight 是提交路线可行动性元数据，不是 field evidence。
- ready/waiting/blocked 只说明提交路线是否可进入下一层验证，不代表 R8p acceptance、R8v replay/holdout、Agent51/49/52/R7 gate 已通过。
- 当前仍无真实 pressure-resolution field rows；不能写 actuator、release gate、protective control candidate 或 field-supported claim。
- 该层提升的是验证治理与工程化能力：减少真实 source package 提交前的试错，同时保留所有 replay、holdout 和人工复核边界。

## 2026-06-04 R8u-50：R8v Downstream Route Handoff

目标：

- 承接 R8u-17 downstream routing preflight，把“R8p accepted rows 可以进入哪些 R8v 目标”继续压实为“每个下游目标的机器可读 handoff contract”。
- 不新增 Agent62，不运行下游 replay/holdout，不放松任何控制保护；只把 R8p 到 R8v 的交接接口变得可检查、可回接、可阻断。
- 让 Agent60 全局 fallback 不只知道 R8p 行级验收和 downstream routing 状态，还能看到 R8v handoff 是否 ready、ready/blocked target 数量和下一步动作。

实现：

- 更新 `experiments/run_agent61_pressure_resolution_replay_scenario_pack.py`：
  - 新增 `ROWS_DOWNSTREAM_ROUTE_HANDOFF_PATH`。
  - 新增 `_field_rows_downstream_route_handoff()`。
  - 输出 `outputs/pressure_resolution_replay_scenario_pack/pressure_resolution_replay_rows_downstream_route_handoff.json`。
  - metrics、report、deliverable、manifest 均接入 `field_rows_downstream_route_handoff`。
- handoff 对四个 R8v 目标逐一生成合同：
  - `agent51_catalyst_proxy_holdout`
  - `agent49_guardrail_context`
  - `agent52_replay_clearance`
  - `r7_evidence_chain`
- 每个目标合同包含：
  - execution order
  - required input tables/artifacts
  - expected gate metrics
  - accepted batches
  - input contract
  - gate contract
  - next operator action
  - blocked writes
  - evidence boundaries
- 更新 `src/water_ai/agents/agent_architecture_consolidation_agent.py`：
  - 新增 `_r8v_pressure_resolution_downstream_route_handoff()`。
  - Agent60 的 R8v 推荐动作现在要求 R8p 行级验收、downstream routing preflight 和 downstream route handoff 同时 ready。
  - Agent60 的 source-blocked fallback 也透传 handoff status、ready/blocked target count、next operator action 和 handoff path。

当前结果：

- Agent61 downstream route handoff：
  - `downstream_route_handoff_status=downstream_route_handoff_blocked_by_upstream_r8p_preflight`
  - `handoff_target_count=4`
  - `ready_handoff_target_count=0`
  - `blocked_handoff_target_count=4`
  - `next_operator_action=R8p_fix_field_rows_source_preflight`
  - `can_route_to_r8v=False`
  - `can_write_to_actuator=False`
  - `can_write_to_release_gate=False`
  - `field_claim_upgrade_allowed=False`
- Agent60 fallback：
  - 仍为 `R8p_fix_field_rows_source_preflight`。
  - trigger metric 已包含 downstream route handoff status、ready/blocked target count 和 next operator action。
  - 只有 handoff 状态变为 `downstream_route_handoff_ready_for_r8v_target_gates` 且四个目标 ready，Agent60 才会推荐 `R8v_route_pressure_resolution_rows_to_field_replay_and_holdout_gates`。

验证：

- 语法检查：
  - `.venv/bin/python -m py_compile experiments/run_agent61_pressure_resolution_replay_scenario_pack.py tests/test_pressure_resolution_replay_scenario_pack_agent.py src/water_ai/agents/agent_architecture_consolidation_agent.py tests/test_agent_architecture_consolidation_agent.py`：通过。
- 定向回归：
  - `.venv/bin/pytest -q tests/test_pressure_resolution_replay_scenario_pack_agent.py`：33 passed。
  - `.venv/bin/pytest -q tests/test_agent_architecture_consolidation_agent.py`：51 passed。
- runner：
  - `.venv/bin/python experiments/run_agent61_pressure_resolution_replay_scenario_pack.py`：运行成功，生成 downstream route handoff。
  - `.venv/bin/python experiments/run_agent60_agent_architecture_consolidation.py`：运行成功，Agent60 已透传 handoff 阻断状态。
- 完整回归：
  - `.venv/bin/pytest -q`：432 passed。

边界：

- downstream route handoff 是 R8p 到 R8v 的交接合同，不是 field evidence。
- handoff ready 只表示 accepted rows 可以进入下游 replay/holdout/evidence chain gates，不代表这些 gate 已通过。
- blocked handoff 不删除目标，只保留目标并标记上游 R8p/R8v preflight 阻断，防止下游验证链被静默跳过。
- 当前仍无真实 pressure-resolution field rows；不能写 actuator、release gate、protective control candidate 或 field-supported claim。

## 2026-06-04 R8u-51：R8v Downstream Target Gate Preflight

目标：

- 承接 R8u-50 downstream route handoff，把“哪些 R8v 目标需要接收 accepted rows”继续压实为“每个目标 gate 如何执行、需要什么输入、输出什么指标、被什么条件阻断”。
- 不新增 Agent62，不运行 Agent51/49/52/R7 gate，不生成 field evidence；只把 R8v 下游目标 gate 的执行合同提前固化。
- 让 Agent60 的 R8v 推荐动作不只看 R8p acceptance、downstream routing 和 route handoff，而是同时要求 target gate preflight ready，防止 handoff ready 被误读为下游验证已通过。

实现：

- 更新 `experiments/run_agent61_pressure_resolution_replay_scenario_pack.py`：
  - 新增 `ROWS_DOWNSTREAM_TARGET_GATE_PREFLIGHT_PATH`。
  - 新增 `_field_rows_downstream_target_gate_preflight()`。
  - 新增 `_r8v_target_gate_command_contract()`。
  - 输出 `outputs/pressure_resolution_replay_scenario_pack/pressure_resolution_replay_rows_downstream_target_gate_preflight.json`。
  - metrics、report JSON、deliverable、Agent61 report、generated files 和 manifest 均接入 `field_rows_downstream_target_gate_preflight`。
- target gate preflight 对四个 R8v 目标逐一生成执行合同：
  - `agent51_catalyst_proxy_holdout`：命令 `.venv/bin/python experiments/run_agent51_catalyst_activity_proxy.py`。
  - `agent49_guardrail_context`：命令 `.venv/bin/python experiments/run_agent49_multi_facility_collaborative_control.py`。
  - `agent52_replay_clearance`：命令 `.venv/bin/python experiments/run_agent52_multi_facility_replay_evaluation.py`。
  - `r7_evidence_chain`：命令 `.venv/bin/python experiments/run_r7_real_field_replay_pipeline.py`。
- 每个目标合同包含：
  - execution order
  - target agent
  - required input tables/artifacts
  - expected gate metrics
  - validation command
  - expected metrics artifact
  - output contract
  - blocked writes
  - next operator action
  - field boundary
- 更新 `src/water_ai/agents/agent_architecture_consolidation_agent.py`：
  - 新增 `_r8v_pressure_resolution_downstream_target_gate_preflight()`。
  - `_r8p_pressure_resolution_rows_accepted()` 现在要求 target gate preflight 状态为 `downstream_target_gate_preflight_ready_for_r8v_execution`，且 4 个 target gate 均 ready。
  - R8v accepted fallback 和 R8p patch-plan fallback 均透传 target gate preflight status、ready/blocked target gate count、next operator action 和 preflight path。
- 更新测试：
  - Agent61 测试验证完整 JSON 行包和 CSV 目录行包会生成 ready target gate preflight。
  - Agent61 测试验证缺失 source package 时 target gate preflight 阻断在 downstream route handoff。
  - Agent60 测试验证 R8v 推荐必须看到 target gate preflight ready。
  - Agent60 patch-plan fallback 测试验证 target gate preflight 的 blocked status 和 ready/blocked count 被透传。

当前结果：

- Agent61 downstream target gate preflight：
  - `downstream_target_gate_preflight_status=downstream_target_gate_preflight_blocked_by_downstream_route_handoff`
  - `target_gate_count=4`
  - `ready_target_gate_count=0`
  - `blocked_target_gate_count=4`
  - `next_operator_action=R8p_fix_field_rows_source_preflight`
  - `can_execute_all_target_gates=False`
  - `can_write_to_actuator=False`
  - `can_write_to_release_gate=False`
  - `field_claim_upgrade_allowed=False`
- Agent60 fallback：
  - 仍为 `R8p_fix_field_rows_source_preflight`。
  - trigger metric 和 expected metrics 已包含 downstream target gate preflight status、ready/blocked target gate count 和 next operator action。
  - 只有 target gate preflight 状态变为 `downstream_target_gate_preflight_ready_for_r8v_execution` 且四个 target gate 均 ready，Agent60 才会推荐 `R8v_route_pressure_resolution_rows_to_field_replay_and_holdout_gates`。

验证：

- 语法检查：
  - `.venv/bin/python -m py_compile experiments/run_agent61_pressure_resolution_replay_scenario_pack.py tests/test_pressure_resolution_replay_scenario_pack_agent.py`：通过。
  - `.venv/bin/python -m py_compile src/water_ai/agents/agent_architecture_consolidation_agent.py tests/test_agent_architecture_consolidation_agent.py`：通过。
- 定向回归：
  - `.venv/bin/pytest -q tests/test_pressure_resolution_replay_scenario_pack_agent.py`：33 passed。
  - `.venv/bin/pytest -q tests/test_agent_architecture_consolidation_agent.py`：51 passed。
- runner：
  - `.venv/bin/python experiments/run_agent61_pressure_resolution_replay_scenario_pack.py`：运行成功，生成 downstream target gate preflight。
  - `.venv/bin/python experiments/run_agent60_agent_architecture_consolidation.py`：运行成功，Agent60 已透传 target gate preflight 阻断状态。
- 完整回归：
  - `.venv/bin/pytest -q`：432 passed。

边界：

- downstream target gate preflight 是目标 gate 执行合同，不是 field evidence。
- target gate ready 只表示 R8p accepted rows 可以提交到该目标 gate，不代表 Agent51/49/52/R7 gate 已通过。
- 该层不写 actuator、不写 release gate、不解除 protective control，不升级 field-supported claim。
- 当前仍无真实 pressure-resolution field rows；最高优先动作仍是 `R8p_fix_field_rows_source_preflight`。

## 2026-06-04 R8u-52：R8v Downstream Target Gate Result Intake

目标：

- 承接 R8u-51 downstream target gate preflight，把“下游目标 gate 如何执行”继续压实为“下游目标 gate 跑完后，结果包如何回传、验收、阻断和进入下一步仲裁”。
- 不新增 Agent62，不做结果仲裁，不把下游 metrics 文件直接当作 field evidence；只建立 Agent51/49/52/R7 结果包进入系统前的结构、来源、目标覆盖和保护边界。
- 防止任意 result package 或含写入请求的 metrics 被误读为 actuator clearance、release gate clearance 或 field-supported claim。

实现：

- 更新 `experiments/run_agent61_pressure_resolution_replay_scenario_pack.py`：
  - 新增 `ROWS_DOWNSTREAM_TARGET_GATE_RESULT_INTAKE_SCHEMA_PATH`。
  - 新增 `ROWS_DOWNSTREAM_TARGET_GATE_RESULT_PREFLIGHT_PATH`。
  - 新增 `_r8v_target_gate_result_package_path()`，读取 `R8V_TARGET_GATE_RESULT_PACKAGE_PATH`。
  - 新增 `_field_rows_downstream_target_gate_result_intake_schema()`。
  - 新增 `_field_rows_downstream_target_gate_result_preflight()`。
  - 输出 `outputs/pressure_resolution_replay_scenario_pack/pressure_resolution_replay_rows_downstream_target_gate_result_intake_schema.json`。
  - 输出 `outputs/pressure_resolution_replay_scenario_pack/pressure_resolution_replay_rows_downstream_target_gate_result_preflight.json`。
  - metrics、report JSON、deliverable、Agent61 report、generated files 和 manifest 均接入 result intake schema/preflight。
- result intake schema 对四个目标逐一要求：
  - `target_id`
  - `target_gate_status`
  - `batch_ids`
  - `source_metrics_artifact`
  - `reported_metrics`
  - `operator_review_boundary_preserved`
  - `can_write_to_actuator`
  - `can_write_to_release_gate`
  - `field_claim_upgrade_allowed`
- result preflight 会阻断：
  - target gate preflight 尚未 ready。
  - 未设置或缺失 `R8V_TARGET_GATE_RESULT_PACKAGE_PATH`。
  - JSON 无法解析或根结构不含 `target_gate_results`。
  - 目标覆盖缺失或出现未知 target。
  - reported metrics 缺少目标合同要求的 gate metrics。
  - 结果行请求 actuator write、release gate write 或 field claim upgrade。
  - 人工复核边界未保留。
- 更新 `src/water_ai/agents/agent_architecture_consolidation_agent.py`：
  - 新增 `_r8v_pressure_resolution_downstream_target_gate_result_preflight()`。
  - R8v accepted fallback 透传 result preflight status、submitted/accepted/rejected count、next operator action 和 summary。
  - R8p patch-plan fallback 透传 result preflight status、submitted/accepted/rejected count、next operator action 和 preflight path。
  - result intake 不反向要求先通过才能执行 target gates；它是下游 gate 结果回传后的 intake gate。
- 更新测试：
  - Agent61 测试验证完整 target result package 可进入 result arbitration。
  - Agent61 测试验证 target result package 只要请求 release gate write 就被 protective write boundary 阻断。
  - Agent61 测试验证 target gate ready 但无 result package 时保持 waiting。
  - Agent60 测试验证 accepted fallback 和 patch-plan fallback 均透传 result preflight 状态与计数。

当前结果：

- result intake schema：
  - `expected_target_count=4`
  - `expected_target_ids=['agent51_catalyst_proxy_holdout', 'agent49_guardrail_context', 'agent52_replay_clearance', 'r7_evidence_chain']`
  - `can_write_to_actuator=False`
  - `can_write_to_release_gate=False`
  - `field_claim_upgrade_allowed=False`
- 当前默认 result preflight：
  - `downstream_target_gate_result_preflight_status=downstream_target_gate_result_preflight_blocked_by_target_gate_preflight`
  - `submitted_target_result_count=0`
  - `accepted_target_result_count=0`
  - `rejected_target_result_count=0`
  - `missing_target_ids` 为四个 R8v 目标。
  - `next_operator_action=R8p_fix_field_rows_source_preflight`
  - `can_route_to_result_arbitration=False`
  - `can_write_to_actuator=False`
  - `can_write_to_release_gate=False`
  - `field_claim_upgrade_allowed=False`
- Agent60 fallback：
  - 当前仍为 `R8p_fix_field_rows_source_preflight`。
  - 已透传 `field_rows_downstream_target_gate_result_preflight_status`、submitted/accepted/rejected count 和 next operator action。

验证：

- 语法检查：
  - `.venv/bin/python -m py_compile experiments/run_agent61_pressure_resolution_replay_scenario_pack.py tests/test_pressure_resolution_replay_scenario_pack_agent.py src/water_ai/agents/agent_architecture_consolidation_agent.py tests/test_agent_architecture_consolidation_agent.py`：通过。
- 定向回归：
  - `.venv/bin/pytest -q tests/test_pressure_resolution_replay_scenario_pack_agent.py`：35 passed。
  - `.venv/bin/pytest -q tests/test_agent_architecture_consolidation_agent.py`：51 passed。
- runner：
  - `.venv/bin/python experiments/run_agent61_pressure_resolution_replay_scenario_pack.py`：运行成功，生成 result intake schema/preflight。
  - `.venv/bin/python experiments/run_agent60_agent_architecture_consolidation.py`：运行成功，Agent60 已透传 result preflight 阻断状态。
- 完整回归：
  - `.venv/bin/pytest -q`：434 passed。

边界：

- result intake schema/preflight 是结果包入口门，不是下游 gate 成功结果。
- result preflight passed 只表示结果包结构、覆盖、来源和保护边界可进入下一步 arbitration，不代表 field evidence、control clearance 或 release clearance。
- 当前无真实 pressure-resolution field rows；target gate preflight 本身被阻断，因此 result preflight 也正确阻断。
- 该层不写 actuator、不写 release gate、不解除 protective control，不升级 field-supported claim。

## 2026-06-04 R8u-53：R8v Downstream Target Gate Result Arbitration

目标：

- 承接 R8u-52 result intake，把“下游目标 gate 结果包结构有效”继续推进为“下游目标 gate 结果如何被安全仲裁”。
- 不新增 Agent62，不运行在线控制，不把 result package 通过当成现场成功；只定义四个目标 gate 的 pass/fail/blocked/review 状态如何进入统一安全门。
- 防止 Agent51/49/52/R7 任一目标失败、阻塞、等待人工复核或状态非法时，被误读为可以进入保护性控制或 release gate。

实现：

- 更新 `experiments/run_agent61_pressure_resolution_replay_scenario_pack.py`：
  - 新增 `ROWS_DOWNSTREAM_TARGET_GATE_RESULT_ARBITRATION_PATH`。
  - 新增 `_field_rows_downstream_target_gate_result_arbitration()`。
  - 新增输出 `outputs/pressure_resolution_replay_scenario_pack/pressure_resolution_replay_rows_downstream_target_gate_result_arbitration.json`。
  - metrics、Agent61 report JSON、deliverable、generated files 和 manifest 均接入 `field_rows_downstream_target_gate_result_arbitration`。
  - result preflight 进一步补严 `target_gate_status` 枚举、`source_metrics_artifact` 一致性和非空 `batch_ids` 检查。
- arbitration gate 规则：
  - result preflight 未通过：`downstream_target_gate_result_arbitration_blocked_by_result_preflight`。
  - accepted target result 数不足：`downstream_target_gate_result_arbitration_blocked_by_incomplete_intake_acceptance`。
  - target status 非法：`downstream_target_gate_result_arbitration_blocked_by_invalid_target_status`。
  - 任一 target failed 或 blocked：`downstream_target_gate_result_arbitration_blocked_by_target_gate_failure`。
  - 任一 target waiting for operator review：`downstream_target_gate_result_arbitration_waiting_for_operator_review`。
  - 四个 target 均 passed：`downstream_target_gate_result_arbitration_ready_for_operator_review`。
  - 即使 unanimous pass，也只允许 `can_route_to_operator_review=True`；`can_emit_protective_control_candidate=False`、`can_write_to_actuator=False`、`can_write_to_release_gate=False`。
- 更新 `src/water_ai/agents/agent_architecture_consolidation_agent.py`：
  - 新增 `_r8v_pressure_resolution_downstream_target_gate_result_arbitration()`。
  - R8v accepted fallback 和 R8p patch-plan fallback 均透传 arbitration status、next operator action、operator-review route flag 和 protective-control candidate flag。
- 更新测试：
  - Agent61 测试验证四个 target 均 passed 时，arbitration 只进入 operator review，不写控制。
  - Agent61 测试验证 Agent52 target failed 时，result preflight 可以通过，但 arbitration 被 target gate failure 阻断。
  - Agent60 测试验证 result arbitration 在 accepted fallback 和 patch-plan fallback 中被透传。

当前结果：

- 默认 arbitration artifact：
  - `downstream_target_gate_result_arbitration_status=downstream_target_gate_result_arbitration_blocked_by_result_preflight`
  - `accepted_target_result_count=0`
  - `target_gate_status_counts={'target_gate_result_passed': 0, 'target_gate_result_failed': 0, 'target_gate_result_blocked': 0, 'target_gate_result_waiting_for_operator_review': 0, 'target_gate_result_invalid_or_missing': 0}`
  - `next_operator_action=R8p_fix_field_rows_source_preflight`
  - `can_route_to_operator_review=False`
  - `can_emit_protective_control_candidate=False`
  - `can_write_to_actuator=False`
  - `can_write_to_release_gate=False`
  - `field_claim_upgrade_allowed=False`
- Agent60 fallback：
  - 当前仍为 `R8p_fix_field_rows_source_preflight`。
  - 已透传 `field_rows_downstream_target_gate_result_arbitration_status`、arbitration next action、operator review route flag 和 protective control candidate flag。

验证：

- 语法检查：
  - `.venv/bin/python -m py_compile experiments/run_agent61_pressure_resolution_replay_scenario_pack.py src/water_ai/agents/agent_architecture_consolidation_agent.py tests/test_pressure_resolution_replay_scenario_pack_agent.py tests/test_agent_architecture_consolidation_agent.py`：通过。
- 定向回归：
  - `.venv/bin/pytest -q tests/test_pressure_resolution_replay_scenario_pack_agent.py`：36 passed。
  - `.venv/bin/pytest -q tests/test_agent_architecture_consolidation_agent.py`：51 passed。
- runner：
  - `.venv/bin/python experiments/run_agent61_pressure_resolution_replay_scenario_pack.py`：通过，生成 result arbitration artifact。
  - `.venv/bin/python experiments/run_agent60_agent_architecture_consolidation.py`：通过，Agent60 已消费 arbitration 状态。
- 完整回归：
  - `.venv/bin/pytest -q`：435 passed。

边界：

- result arbitration 是下游 target gate 结果的安全仲裁门，不是 field evidence。
- unanimous target pass 也只允许进入 operator review，不允许写 actuator、release gate 或 field-supported claim。
- 当前仍无真实 pressure-resolution field rows；result preflight 和 arbitration 都正确阻断在上游真实 source package 缺失链路。

## 2026-06-04 R8u-54：R8v Downstream Target Gate Operator Review Response Gate

目标：

- 承接 R8u-53 result arbitration，把“允许进入 operator review”继续压实为机器可读的人工复核响应门。
- 不新增 Agent62，不生成假人工意见，不运行在线控制；只让 Agent61/Agent60 能识别人工批准、拒绝、hold、边界确认和禁止写入标志。
- 防止四个 target gate 即使全部 passed，也绕过人工复核、post-review gate、执行器写入或 release gate。

实现：

- 更新 `experiments/run_agent61_pressure_resolution_replay_scenario_pack.py`：
  - 新增 `ROWS_DOWNSTREAM_TARGET_GATE_OPERATOR_REVIEW_TEMPLATE_PATH` 和 `ROWS_DOWNSTREAM_TARGET_GATE_OPERATOR_REVIEW_PREFLIGHT_PATH`。
  - 新增 `_r8v_target_gate_operator_review_path()`，读取可选 `R8V_TARGET_GATE_OPERATOR_REVIEW_PATH`。
  - 新增 `_field_rows_downstream_target_gate_operator_review_template()`，为四个 R8v target 生成 operator review 填报合同。
  - 新增 `_field_rows_downstream_target_gate_operator_review_preflight()`，检查 target 覆盖、target status 一致性、operator decision、reviewer、review time、review notes、boundary acknowledgement 和禁止写入边界。
  - metrics、Agent61 report JSON、deliverable、generated files 和 manifest 均接入 `field_rows_downstream_target_gate_operator_review_template` 与 `field_rows_downstream_target_gate_operator_review_preflight`。
- operator review preflight 规则：
  - arbitration 未 ready：`downstream_target_gate_operator_review_preflight_blocked_by_arbitration`。
  - arbitration ready 但未提交 review package：`downstream_target_gate_operator_review_preflight_waiting_for_review_package`。
  - target 缺失、未知或 status 不一致：阻断在 target coverage/status contract。
  - 任一行请求 actuator、release gate 或 field claim upgrade：`downstream_target_gate_operator_review_preflight_failed_protective_write_boundary`。
  - 任一 target reject 或 hold：`downstream_target_gate_operator_review_preflight_blocked_by_operator_decision`。
  - 全部 approved：`downstream_target_gate_operator_review_preflight_passed_ready_for_post_review_gate`，但仍 `can_emit_protective_control_candidate=False`、`can_write_to_actuator=False`、`can_write_to_release_gate=False`、`field_claim_upgrade_allowed=False`。
- 更新 `src/water_ai/agents/agent_architecture_consolidation_agent.py`：
  - 新增 `_r8v_pressure_resolution_downstream_target_gate_operator_review_preflight()`。
  - R8v accepted fallback 和 R8p patch-plan fallback 均透传 operator review preflight status、approved/rejected/hold count、next operator action、post-review route flag 和 protective-control candidate flag。
- 更新测试：
  - Agent61 测试验证 arbitration 未 ready 时 operator review 被阻断。
  - Agent61 测试验证 unanimous arbitration ready 但未提交 review package 时保持 waiting。
  - Agent61 测试验证四个 target 全部人工批准时只进入 post-review gate，不写控制或放行。
  - Agent61 测试验证 operator review package 只要请求 actuator/release/field claim 写入就被 protective write boundary 阻断。

当前结果：

- 默认 operator review template：
  - `template_id=R8u54_downstream_target_gate_operator_review_template`
  - `expected_target_count=4`
  - `accepted_decisions=['operator_approved_for_post_review_gate', 'operator_rejected_requires_remediation', 'operator_hold_requires_more_evidence']`
  - `can_write_to_actuator=False`
  - `can_write_to_release_gate=False`
  - `field_claim_upgrade_allowed=False`
- 默认 operator review preflight：
  - `downstream_target_gate_operator_review_preflight_status=downstream_target_gate_operator_review_preflight_blocked_by_arbitration`
  - `submitted_operator_review_count=0`
  - `approved_operator_review_count=0`
  - `rejected_operator_review_count=0`
  - `hold_operator_review_count=0`
  - `next_operator_action=R8p_fix_field_rows_source_preflight`
  - `can_route_to_post_review_gate=False`
  - `can_emit_protective_control_candidate=False`
  - `can_write_to_actuator=False`
  - `can_write_to_release_gate=False`
  - `field_claim_upgrade_allowed=False`
- Agent60 fallback：
  - 当前仍为 `R8p_fix_field_rows_source_preflight`。
  - 已透传 `field_rows_downstream_target_gate_operator_review_preflight_status`、operator review next action、post-review route flag 和 protective-control candidate flag。

验证：

- 语法检查：
  - `.venv/bin/python -m py_compile experiments/run_agent61_pressure_resolution_replay_scenario_pack.py src/water_ai/agents/agent_architecture_consolidation_agent.py`：通过。
- 定向回归：
  - `.venv/bin/pytest -q tests/test_pressure_resolution_replay_scenario_pack_agent.py`：40 passed。
  - `.venv/bin/pytest -q tests/test_agent_architecture_consolidation_agent.py`：51 passed。
- runner：
  - `.venv/bin/python experiments/run_agent61_pressure_resolution_replay_scenario_pack.py`：通过，生成 operator review template/preflight artifact。
  - `.venv/bin/python experiments/run_agent60_agent_architecture_consolidation.py`：通过，Agent60 已消费 operator review preflight 阻断状态。
- 完整回归：
  - `.venv/bin/pytest -q`：439 passed。

边界：

- operator review response gate 是人工复核响应合同，不是 field evidence。
- 全部 operator approved 也只进入 post-review gate，不允许写 actuator、release gate 或 field-supported claim。
- 当前仍无真实 pressure-resolution field rows；operator review preflight 正确阻断在上游 result arbitration/source package 缺失链路。

## 2026-06-04 R8u-55：R8v Downstream Target Gate Post Review Protective Candidate Gate

目标：

- 承接 R8u-54 operator-review response gate，把“人工批准后进入 post-review gate”继续压实为机器可读的保护性控制候选评估门。
- 不新增 Agent62，不运行在线控制，不生成 field-supported claim；只让 Agent61/Agent60 能区分“人工批准完成”和“仍然只能进入保护性候选评估，不能写执行器或放行门”。
- 防止四个 target gate 结果全部通过且人工全部 approved 后，直接被误读为 actuator command、release clearance 或现场成立结论。

实现：

- 更新 `experiments/run_agent61_pressure_resolution_replay_scenario_pack.py`：
  - 新增 `ROWS_DOWNSTREAM_TARGET_GATE_POST_REVIEW_GATE_PATH`。
  - 新增 `_field_rows_downstream_target_gate_post_review_gate()`。
  - metrics、Agent61 report JSON、deliverable、generated files 和 manifest 均接入 `field_rows_downstream_target_gate_post_review_gate`。
- post-review gate 规则：
  - operator review preflight 未通过：`downstream_target_gate_post_review_gate_blocked_by_operator_review_preflight`。
  - operator review 通过但批准数量不完整：`downstream_target_gate_post_review_gate_blocked_by_incomplete_operator_approval`。
  - 四个目标全部人工 approved：`downstream_target_gate_post_review_gate_passed_ready_for_protective_candidate_evaluation`。
  - 即使 gate 通过，也只允许 `can_route_to_protective_candidate_evaluation=True` 和 `can_emit_protective_control_candidate=True`；仍保持 `can_write_to_actuator=False`、`can_write_to_release_gate=False`、`field_claim_upgrade_allowed=False`。
- 更新 `src/water_ai/agents/agent_architecture_consolidation_agent.py`：
  - 新增 `_r8v_pressure_resolution_downstream_target_gate_post_review_gate()`。
  - R8v accepted fallback 和 R8p patch-plan fallback 均透传 post-review status、next operator action、protective candidate route flag 和 protective-control candidate flag。
- 更新测试：
  - Agent61 测试验证 operator review 未通过时 post-review gate 阻断。
  - Agent61 测试验证四个目标全部人工 approved 后，只能发出保护性控制候选评估许可，仍不能写 actuator/release/field claim。
  - Agent60 测试验证 accepted fallback 和 patch-plan fallback 均消费 post-review gate 状态。

当前结果：

- 默认 post-review gate：
  - `downstream_target_gate_post_review_gate_status=downstream_target_gate_post_review_gate_blocked_by_operator_review_preflight`
  - `candidate_target_count=0`
  - `next_operator_action=R8p_fix_field_rows_source_preflight`
  - `can_route_to_protective_candidate_evaluation=False`
  - `can_emit_protective_control_candidate=False`
  - `can_write_to_actuator=False`
  - `can_write_to_release_gate=False`
  - `field_claim_upgrade_allowed=False`
- Agent60 fallback：
  - 当前仍为 `R8p_fix_field_rows_source_preflight`。
  - 已透传 `field_rows_downstream_target_gate_post_review_gate_status`、post-review next action、protective candidate route flag 和 protective-control candidate flag。

验证：

- 定向回归：
  - `.venv/bin/pytest -q tests/test_pressure_resolution_replay_scenario_pack_agent.py`：42 passed。
  - `.venv/bin/pytest -q tests/test_agent_architecture_consolidation_agent.py`：51 passed。
- runner：
  - `.venv/bin/python experiments/run_agent61_pressure_resolution_replay_scenario_pack.py`：通过，生成 post-review gate artifact。
  - `.venv/bin/python experiments/run_agent60_agent_architecture_consolidation.py`：通过，Agent60 已消费 post-review gate 阻断状态。
- 完整回归：
  - `.venv/bin/pytest -q`：441 passed。

边界：

- post-review gate 是 operator review 之后、保护性控制候选评估之前的安全门。
- 它不是 actuator command、不是 release clearance、不是 field evidence，也不是专利或论文里的实证结果。
- 当前仍无真实 pressure-resolution field rows；post-review gate 正确阻断在 operator-review/source package 缺失链路。

## 2026-06-04 R8u-56：R8v Protective Control Candidate Evaluation Gate

目标：

- 承接 R8u-55 post-review gate，把“可进入保护性候选评估”继续压实为机器可读的 protective-control candidate evaluation gate。
- 不新增 Agent62，不运行在线控制，不写执行器，不写 release gate，不升级 field-supported claim；只让 Agent61/Agent60 明确知道 post-review 之后产生的是候选动作包，而不是执行命令。
- 把保护性候选动作与最终执行复核、执行器联锁、actuator feedback 和 release validation 分离，增强系统可控性、可验证性、工程边界和专利级技术特征清晰度。

实现：

- 更新 `experiments/run_agent61_pressure_resolution_replay_scenario_pack.py`：
  - 新增 `ROWS_DOWNSTREAM_TARGET_GATE_PROTECTIVE_CANDIDATE_EVALUATION_PATH`。
  - 新增 `_field_rows_downstream_target_gate_protective_candidate_evaluation()`。
  - metrics、Agent61 report JSON、deliverable、generated files 和 manifest 均接入 `field_rows_downstream_target_gate_protective_candidate_evaluation`。
- protective candidate evaluation 规则：
  - post-review gate 未通过：`protective_candidate_evaluation_blocked_by_post_review_gate`。
  - post-review 通过但四个 required target contribution 不完整：`protective_candidate_evaluation_blocked_by_missing_target_contributions`。
  - 任一 candidate target 请求 actuator/release/field claim 写入：`protective_candidate_evaluation_failed_no_write_boundary`。
  - 四个 target contribution 均完整且 no-write 边界保留：`protective_candidate_evaluation_passed_ready_for_final_execution_review`。
  - 即使通过，也只允许 `can_emit_protective_control_candidate=True` 和 `can_route_to_final_execution_review=True`；仍保持 `can_write_to_actuator=False`、`can_write_to_release_gate=False`、`field_claim_upgrade_allowed=False`。
- candidate action bundle 明确允许的仅是候选动作：
  - `temporarily_hold_batch`
  - `extend_retention_time`
  - `increase_recycle_or_return_flow_for_review`
  - `adjust_dose_as_candidate_not_command`
  - `trigger_catalyst_regeneration_or_replacement_review`
  - `switch_or_bypass_unit_as_candidate_not_command`
  - `keep_release_gate_blocked`
- 更新 `src/water_ai/agents/agent_architecture_consolidation_agent.py`：
  - 新增 `_r8v_pressure_resolution_downstream_target_gate_protective_candidate_evaluation()`。
  - R8v accepted fallback 和 R8p patch-plan fallback 均透传 candidate evaluation status、next action、candidate emit flag 和 final execution review route flag。
- 更新测试：
  - Agent61 测试验证 post-review 未通过时 candidate evaluation 阻断。
  - Agent61 测试验证四个 target 全部通过 post-review 后，只生成保护性候选动作包，仍不能写 actuator/release/field claim。
  - Agent60 测试验证 accepted fallback 和 patch-plan fallback 均消费 candidate evaluation 状态。

当前结果：

- 默认 candidate evaluation：
  - `downstream_target_gate_protective_candidate_evaluation_status=protective_candidate_evaluation_blocked_by_post_review_gate`
  - `candidate_target_count=0`
  - `candidate_action_count=7`
  - `next_operator_action=R8p_fix_field_rows_source_preflight`
  - `can_emit_protective_control_candidate=False`
  - `can_route_to_final_execution_review=False`
  - `can_write_to_actuator=False`
  - `can_write_to_release_gate=False`
  - `field_claim_upgrade_allowed=False`
- Agent60 fallback：
  - 当前仍为 `R8p_fix_field_rows_source_preflight`。
  - 已透传 `field_rows_downstream_target_gate_protective_candidate_evaluation_status`、candidate next action、candidate emit flag 和 final execution review route flag。

验证：

- 语法检查：
  - `.venv/bin/python -m py_compile experiments/run_agent61_pressure_resolution_replay_scenario_pack.py src/water_ai/agents/agent_architecture_consolidation_agent.py tests/test_pressure_resolution_replay_scenario_pack_agent.py tests/test_agent_architecture_consolidation_agent.py`：通过。
- 定向回归：
  - `.venv/bin/pytest -q tests/test_pressure_resolution_replay_scenario_pack_agent.py`：44 passed。
  - `.venv/bin/pytest -q tests/test_agent_architecture_consolidation_agent.py`：51 passed。
- runner：
  - `.venv/bin/python experiments/run_agent61_pressure_resolution_replay_scenario_pack.py`：通过，生成 candidate evaluation artifact。
  - `.venv/bin/python experiments/run_agent60_agent_architecture_consolidation.py`：通过，Agent60 已消费 candidate evaluation 阻断状态。
- 完整回归：
  - `.venv/bin/pytest -q`：443 passed。

边界：

- protective candidate evaluation 是候选动作评估门，不是在线执行命令。
- final execution review、actuator safety interlock、actuator feedback replay 和 release gate validation 仍是后续独立门。
- 当前仍无真实 pressure-resolution field rows；candidate evaluation 正确阻断在 post-review/source package 缺失链路。

## 2026-06-04 R8u-57：模型成熟度、专利可写性与论文可写性审计

目标：

- 回答“当前模型相比上次停止流程图、回到核心模型优化时，到底成熟了多少”的问题。
- 不再用 agent 数量或展示材料衡量进步，而是从创新点、工程成熟度、专利交底 readiness、论文 readiness、外部方法关系和下一步最高边际价值来判断。
- 明确区分“可写专利交底草案”“专利授权稳健”“可写方法论文”“可写实证论文”，防止把仿真、模板或框架误写成现场实证。

实现：

- 新增 `deliverables/model_core_optimization/model_maturity_patent_paper_audit.md`。
- 审计文件将当前提升概括为三条：
  - 七层骨架和 9 个核心模块压实，系统不再按 agent 编号碎片化理解。
  - 观测、软传感、灰箱机理、多设施控制、知识证据、field replay、operator review、release/actuator gate 之间形成可检查接口。
  - R8p/R8v/R8u-56 已把真实现场行包、模板/仿真阻断、保护性候选动作和 no-write 边界压成机器可读 gate。
- 审计文件给出相对成熟度判断：
  - 系统骨架清晰度约从 55/100 提升到 85/100。
  - 创新点可表达性约从 50/100 提升到 72/100。
  - 工程可执行性约从 40/100 提升到 62/100。
  - 验证治理成熟度约从 45/100 提升到 80/100。
  - 方法论文可写性约从 55/100 提升到 75/100。
  - 专利交底成熟度约从 45/100 提升到 72/100。
  - 专利授权稳健度约从 30/100 提升到 50/100。

当前判断：

- 模型具备进入“专利交底书 + 初步权利要求骨架 + 初步检索”的条件，但不能跳过正式 prior-art search、claim element mapping 和实施例数据。
- 模型可以写方法/架构/验证框架类论文草稿；实证水质改善、催化剂代理有效性、多设施控制优越性仍需真实 field package、holdout 和 replay 对照。
- 工程成熟度已经到“工程验证框架 ready”，但不是“现场闭环运行 ready”。

边界：

- 该审计不是法律意见，也不是专利授权判断。
- 该审计不生成 field evidence，不写 actuator，不写 release gate。
- 下一步最高边际价值仍是补真实 field package 或至少补 formal search/source-basis detail；如果无真实数据，再做高保真 semi-synthetic replay 时必须继续标注非 field。

## 2026-06-04 R8u-58：非法律 Prior-Art 种子矩阵

目标：

- 承接 R8u-57 的成熟度审计，把“专利交底 readiness”继续向外部对比证据推进。
- 不新增 agent，不伪装正式检索结果，不给法律意见；只建立一个可被后续 formal search package、人工非法律比对和专利代理人审查吸收的公开来源种子矩阵。
- 防止后续把 “AI / 多智能体 / 软传感 / 知识图谱 / 稀疏布点 / 闭环控制” 这类宽泛词误当主创新点。

实现：

- 新增 `deliverables/model_core_optimization/nonlegal_prior_art_seed_matrix.md`。
- 新增机器可读版本 `outputs/agent_architecture_consolidation/nonlegal_prior_art_seed_matrix.json`。
- 接入 `deliverables/manifest.json` 与 `notes/current_status.md`。

内容：

- Patentability 基准来源：
  - WIPO patent protection FAQ：用于约束可专利主题、新颖性、创造性/非显而易见性、工业适用性和充分公开。
  - CNIPA Patent Law translation：用于约束新颖性、创造性和实用性。
- Prior-art 种子族：
  - water purification soft sensor/control patent。
  - intelligent water/wastewater diagnosis/control patent。
  - WWTP soft sensor review。
  - soft-sensor real-time dosing control。
  - PySensors sparse sensor placement。
  - MARL/MADDPG WWTP optimal control。
  - full-scale multi-agent WWTP operation。
  - MARL integrated urban drainage/wastewater control。
  - WNTR/EPANET-style topology and hydraulics。
  - WaterTAP flowsheet/process/costing modeling。
  - QSDsan process/system/TEA/LCA modeling。
  - Offline RL / CQL / D4RL-style replay evaluation。

当前判断：

- 不能把“软传感 + 控制”“多智能体水处理优化”“稀疏布点”“流程建模/成本优化”“offline replay”单独作为主创新点。
- 更稳的主链是：低成本 node-modality 感知 -> 软传感/灰箱隐藏状态估计 -> 循环/暂存结构争取低频证据时间 -> KG/source_basis 与灰箱机理约束 -> 多智能体只生成保护性候选 -> field replay/operator review/release-actuator gate 决定是否晋级。
- 从属/分案方向优先保留：催化剂活性代理观测、pressure/headloss 多源冲突解除、低频传感-循环窗口协同、field replay 保护性写回。

边界：

- 该矩阵不是正式 prior-art search result，不是 legal opinion，不判断 novelty/inventiveness，也不能直接生成权利要求文本。
- 该矩阵不生成 field evidence，不写 actuator，不写 release gate。
- 后续若要进入 formal search validation gate，仍必须由真实检索结果和人工/代理人回填包提供 hit table 与 claim element comparison chart。

## 2026-06-04 R8u-59：Agent48 Prior-Art Baseline Comparison Patch

目标：

- 承接 R8u-58 非法律 prior-art 种子矩阵，把 Agent48 稀疏布点从“已有项目内比较策略”进一步压成可服务论文/专利对照的 baseline comparison contract。
- 不新增 agent，不改变下游 Agent51/49/52/54 的既有消费字段；只在 Agent48 内补齐 random/cost-only 朴素对照，并输出可追踪的 baseline delta。
- 防止后续把“稀疏传感布点”本身当作创新点，而是把保护重点落到 node-modality hidden-state placement 相对 random、cost-only、generic sparse reconstruction/classification 和 topology-aware baseline 的区别。

实现：

- 更新 `src/water_ai/agents/sensor_network_sparse_placement_agent.py`：
  - 新增 `cost_only_baseline`。
  - 新增 `deterministic_random_baseline`。
  - 为每个 strategy 输出 `benchmark_role`、`prior_art_family` 和 `prior_art_comparison_boundary`。
  - 新增 `baseline_comparison_contract`，包括 required/observed baseline、missing baseline、best_vs_random_delta、best_vs_cost_only_delta、best_vs_sparse_reconstruction_delta、best_vs_fault_classification_delta、claim_scope_use 和 cannot_do。
- 更新 `experiments/run_agent48_sensor_network_sparse_placement.py`：
  - metrics 与 report/deliverable 写入 `baseline_comparison_contract`。
  - manifest 只写 Agent48 最新指标，不再把全局 `next_stage` 覆盖成单点 Agent48 任务；全局仍保留 R7/R8p field package 与 release/actuator gate 边界。
- 更新 `tests/test_sensor_network_sparse_placement_agent.py`：
  - 要求 algorithm comparison 包含 random/cost-only baseline。
  - 要求 baseline contract 不缺 required baselines，并明确不能证明 patentability 或 field performance。

当前结果：

- selected strategy：`greedy_marginal`。
- strategy_count：6。
- baseline comparison status：`sparse_baseline_comparison_ready_needs_field_topology_and_labels`。
- best_vs_random_delta：0.062。
- best_vs_cost_only_delta：0.258。
- 关键边界：该比较仍基于 synthetic topology prior，只能作为设计先验、论文/专利对照和非法律区别分析；不能证明现场部署优越性、不能证明 patentability、不能替代真实 topology、node-specific timeseries 或 offline hidden-state labels。

验证：

- `.venv/bin/pytest -q tests/test_sensor_network_sparse_placement_agent.py`：11 passed。
- Agent48 下游相关链路测试：50 passed。
- `.venv/bin/python experiments/run_agent48_sensor_network_sparse_placement.py`：通过，生成更新后的 Agent48 report/metrics。
- `.venv/bin/pytest -q`：444 passed。

## 2026-06-04 R8u-60：Agent52 Control Policy Baseline Comparison Contract

目标：

- 承接 R8u-57/R8u-58/R8u-59 的专利级成熟度主线，把控制侧从“单一 Agent49/guardrail 指标”推进为可对照、可审查、可写入论文/专利实施例的 replay baseline 矩阵。
- 不新增 agent，不改变 Agent49/52 控制逻辑；只在 Agent52 replay 输出中补齐策略对照和部署边界。
- 防止后续把“多智能体控制表现好”当成未经对照的结论；必须和保守待机、放行优先、固定随机和专家上界在同一 state-action-reward replay 表内比较。

实现：

- 更新 `src/water_ai/agents/multi_facility_replay_evaluation_agent.py`：
  - 新增 `control_policy_comparison`。
  - 新增 `control_baseline_contract`。
  - 策略集合包括 `agent49_policy`、`guardrail_aware_policy`、`safe_standby_rule`、`release_first_rule`、`deterministic_random_action_baseline` 和 `expert_upper_bound`。
  - 每个策略输出 accuracy、mean/p95 regret、mean reward、protective false-positive cost、release mismatch、unsafe action rate、action distribution 和 no-write 边界。
  - contract 明确不能证明 deployed control performance、patentability/inventiveness，不能写 actuator 或 release gate。
- 更新 `experiments/run_agent52_multi_facility_replay_evaluation.py`：
  - metrics JSON、Agent52 report 和 deliverable 均写入 baseline comparison 与 delta summary。
  - manifest 增加 `latest_agent52_control_baseline_strategy_count=6` 与控制 baseline 边界。
- 更新 `tests/test_multi_facility_replay_evaluation_agent.py`：
  - 要求 Agent52 输出 6 类 baseline。
  - 要求 expert upper bound accuracy 为 1.0。
  - 要求 guardrail-aware policy 相对 Agent49 baseline 在 synthetic replay 中提升 accuracy、降低 regret。
  - 要求 synthetic baseline comparison 仍不能选 deployed policy、不能写 actuator/release gate。

当前结果：

- comparison status：`synthetic_control_policy_baseline_comparison_ready_needs_field_replay`。
- strategy_count：6。
- guardrail_vs_agent49_accuracy_gain：0.333。
- guardrail_vs_agent49_mean_regret_delta：0.055。
- guardrail_vs_agent49_false_positive_cost_delta：0.166。
- guardrail_vs_release_first_mismatch_delta：0.667。
- guardrail_vs_safe_standby_mean_reward_delta：0.121。
- guardrail_vs_random_regret_delta：0.096。

边界：

- 当前结果仍是 synthetic replay，只能更新 reward-prior、实验设计、专利/论文实施例 scaffold 和后续 field benchmark 需求。
- 不能证明现场部署控制性能，不能证明专利新颖性/创造性，不能替代 operator review、field holdout、release validation 或 actuator interlock。

验证：

- `.venv/bin/python -m py_compile src/water_ai/agents/multi_facility_replay_evaluation_agent.py experiments/run_agent52_multi_facility_replay_evaluation.py`：通过。
- `.venv/bin/pytest -q tests/test_multi_facility_replay_evaluation_agent.py`：11 passed。
- `.venv/bin/pytest -q tests/test_multi_facility_replay_evaluation_agent.py tests/test_multi_facility_collaborative_control_agent.py`：21 passed。
- `.venv/bin/pytest -q tests/test_pressure_resolution_replay_scenario_pack_agent.py tests/test_agent_architecture_consolidation_agent.py`：95 passed。
- `.venv/bin/python experiments/run_agent52_multi_facility_replay_evaluation.py`：通过，已刷新 Agent52 metrics/report/deliverable。
- `.venv/bin/pytest -q`：445 passed。

## 2026-06-04 R8u-61：Agent52 Replay Export Work Package

目标：

- 承接 R8u-60 的控制策略 baseline comparison，把 Agent52 replay 结果从报告指标推进为 Agent61/R8p 路由中明确要求的 `agent52_replay_export` 工作包。
- 不从 R7 field CSV 伪造 `policy_action_id`、`expert_action_id` 或 pressure-source conflict counters；这些字段必须来自 Agent49/52 replay 链。
- 让后续 R8U25/R8U28 路线可以拿到 `agent52_replay_export_manifest.json`、`agent52_replay_table.csv` 和 `agent52_replay_table.rows.json`，同时保留 synthetic/field evidence 边界。

实现：

- 更新 `experiments/run_agent52_multi_facility_replay_evaluation.py`：
  - 新增 `AGENT52_REPLAY_EXPORT_FIELDS`。
  - 新增 `_agent52_replay_export_payload()`、`_agent52_replay_export_rows()` 和 `_write_agent52_replay_export()`。
  - Agent52 runner 现在写出：
    - `outputs/multi_facility_replay_evaluation/agent52_replay_export/agent52_replay_export_manifest.json`
    - `outputs/multi_facility_replay_evaluation/agent52_replay_export/agent52_replay_table.csv`
    - `outputs/multi_facility_replay_evaluation/agent52_replay_export/agent52_replay_table.rows.json`
  - metrics JSON、Agent52 report、deliverable 和 manifest 均回写 replay export status、row count 和 no-write boundary。
- 更新 `tests/test_multi_facility_replay_evaluation_agent.py`：
  - 新增 export payload contract 测试，要求字段覆盖 Agent61/R8p work package 要求。
  - 要求 synthetic export 的 `all_rows_field_origin=False`、`can_route_to_r8p_candidate_rows=False`、`can_create_field_evidence_by_export_only=False`、`can_write_to_actuator=False`、`can_write_to_release_gate=False`。

当前结果：

- export status：`agent52_replay_export_ready_synthetic_only`。
- row_count：6。
- required fields 覆盖：`batch_id`、`scenario`、`policy_action_id`、`expert_action_id`、pressure-source conflict counters、`data_origin`。
- all_rows_field_origin：False。
- 每行 evidence_status：`synthetic_replay_candidate_not_field_evidence`。
- 导出包已与 R8U25 Agent52 replay export work package 的 expected files 对齐。

边界：

- 当前导出包只是 replay-origin synthetic candidate，不能作为 field evidence。
- 真实 field replay export 仍必须由 field-origin `agent52_replay_table`、operator/validated expert actions、action outcome、reward components 和 downstream R8p/R8v gates 支撑。
- 该导出包不能写 actuator，不能写 release gate，不能证明 deployed control performance 或 patentability/inventiveness。

验证：

- `.venv/bin/python -m py_compile experiments/run_agent52_multi_facility_replay_evaluation.py tests/test_multi_facility_replay_evaluation_agent.py`：通过。
- `.venv/bin/pytest -q tests/test_multi_facility_replay_evaluation_agent.py`：12 passed。
- `.venv/bin/python experiments/run_agent52_multi_facility_replay_evaluation.py`：通过，已生成 replay export 三件套。
- `.venv/bin/pytest -q tests/test_multi_facility_replay_evaluation_agent.py tests/test_multi_facility_collaborative_control_agent.py`：22 passed。
- `.venv/bin/pytest -q tests/test_pressure_resolution_replay_scenario_pack_agent.py tests/test_agent_architecture_consolidation_agent.py`：95 passed。
- `.venv/bin/pytest -q`：446 passed。

## 2026-06-04 R8u-62：Agent48 Hydraulic Path Coverage Contract

目标：

- 承接用户关于“传感器管网布点、稀疏感知、多维向量矩阵、循环式水处理结构”的核心方向，把 Agent48 从普通 topology coverage 推进为可解释的水力路径覆盖合同。
- 不再新增新的 topology baseline，因为 Agent48 已有 greedy、cost-only、random、QR/SSPOR-like、SSPOC-like 和 topology-aware 六类对照；本轮最高边际价值是让 selected layout 明确回答是否覆盖进水、均质、反应、催化剂床、回流和放行边界。

实现：

- 更新 `src/water_ai/agents/sensor_network_sparse_placement_agent.py`：
  - 新增 `hydraulic_path_coverage_contract`。
  - 新增六段 `low_cost_circular_treatment_path_v1`：`S0_influent_matrix`、`S1_equalization_buffer`、`S2_reaction_core`、`S3_catalyst_bed`、`S4_recirculation_loop`、`S5_release_boundary`。
  - 每段输出 required zones、proxy zones、required modalities、selected sensors、missing zones、missing modalities、field evidence needed 和 control relevance。
  - contract 输出 `recirculation_loop_observed`、`low_frequency_time_buffer_observed`、`final_effluent_directly_observed`、`final_release_gate_needs_effluent_label`、`can_support_soft_sensor_path_prior` 和 `can_support_control_replay_design_prior`。
  - 若最终 effluent 放行端点未被直接覆盖，新增 issue `hydraulic_path_release_endpoint_needs_effluent_label`，防止 polishing 代理观察被误写成 release gate 支持。
  - soft sensor interface 现在同步暴露 hydraulic path contract，供 Agent54/49/52 消费。
- 更新 `experiments/run_agent48_sensor_network_sparse_placement.py`：
  - metrics JSON、Agent48 report、deliverable 和 manifest 均写入 hydraulic path contract。
  - deliverable 新增逐段水力路径表。
- 更新 `tests/test_sensor_network_sparse_placement_agent.py`：
  - 新增测试要求 contract 覆盖 6/6 阶段、识别回流环和低频时间缓冲，但仍阻断 final effluent release gate、field topology 和 pressure/headloss 缺口。

当前结果：

- contract status：`hydraulic_path_contract_ready_needs_field_topology_and_release_endpoint`。
- covered_stage_count：6/6。
- recirculation_loop_observed：True。
- low_frequency_time_buffer_observed：True。
- final_effluent_directly_observed：False。
- final_release_gate_needs_effluent_label：True。
- unresolved requirements：`field_topology_and_hydraulic_path_labels_required`、`final_effluent_release_endpoint_not_directly_observed`、`pressure_drop_or_headloss_proxy_not_installed_in_selected_layout`。

边界：

- 当前结论仍是 synthetic topology prior 上的设计合同，只能支撑 soft sensor path prior 和 control replay design prior。
- 不能证明现场安装布点合理，不能写 release gate，不能写 actuator policy，不能替代真实 topology/HRT/flow、effluent endpoint label、pressure/headloss 和 offline release risk 标签。

验证：

- `.venv/bin/python -m py_compile src/water_ai/agents/sensor_network_sparse_placement_agent.py experiments/run_agent48_sensor_network_sparse_placement.py tests/test_sensor_network_sparse_placement_agent.py`：通过。
- `.venv/bin/pytest -q tests/test_sensor_network_sparse_placement_agent.py`：12 passed。
- `.venv/bin/pytest -q tests/test_sensor_network_sparse_placement_agent.py tests/test_soft_sensor_matrix_coupling_agent.py tests/test_multi_facility_collaborative_control_agent.py tests/test_multi_facility_replay_evaluation_agent.py`：37 passed。
- `.venv/bin/python experiments/run_agent48_sensor_network_sparse_placement.py`：通过，已刷新 Agent48 metrics/report/deliverable/manifest。
- `.venv/bin/pytest -q`：447 passed。

## 2026-06-04 R8u-63：Agent54 Hydraulic Path-Aware Soft Sensor Matrix

目标：

- 承接 R8u-62 的 Agent48 水力路径覆盖合同，把“布点覆盖了循环式处理路径的哪些阶段”从 Agent48 报告回接到 Agent54 状态估计层。
- 不新增 agent，不重跑全局治理；通过现有 Agent54 扩展，把软传感矩阵从 `node-zone-modality-time` 推进为 `node-zone-modality-time-path`。
- 让软传感训练/推理 schema 明确记录每个低成本信号处于进水、均质、反应、催化剂床、回流或放行边界中的哪一段，从而服务低频传感-循环窗口协同控制。

实现：

- 更新 `src/water_ai/agents/soft_sensor_matrix_coupling_agent.py`：
  - `MATRIX_FEATURE_CHANNELS` 新增 `hydraulic_path_stage_prior`。
  - `FIELD_SCHEMA_PATCH` 新增 `path_stage_id`、`hydraulic_path_role`、`stage_coverage_mask`、`direct_path_stage_coverage_mask`、`proxy_path_stage_coverage_mask`、`release_boundary_flag` 和 `recirculation_loop_flag`。
  - 新增 `hydraulic_path_feature_contract`，优先读取 `Agent48.hydraulic_path_coverage_contract`，并 fallback 到 `Agent48.soft_sensor_interface.hydraulic_path_contract`。
  - `training_schema_gap` 新增 `hydraulic_path_feature_terms`、`missing_hydraulic_path_terms` 和 `current_model_hydraulic_path_ready`。
  - `readiness` 新增 `hydraulic_path_contract_status`、`hydraulic_path_feature_term_count`、`hydraulic_path_schema_ready`、`hydraulic_path_final_release_gate_needs_effluent_label` 和 `can_update_hydraulic_path_feature_schema`。
  - 新增 issue：
    - `hydraulic_path_feature_schema_not_trained`
    - `hydraulic_path_release_endpoint_blocks_release_use`
- 更新 `experiments/run_agent54_soft_sensor_matrix_coupling.py`：
  - deliverable/report/manifest 写入 Agent54 hydraulic path contract 状态、缺失训练字段和 release gate 阻断边界。
- 更新 `tests/test_soft_sensor_matrix_coupling_agent.py`：
  - 新增测试要求 Agent54 消费 Agent48 hydraulic path contract，并识别 path-stage schema gap 与 final effluent release endpoint blocker。

当前结果：

- Agent54 `hydraulic_path_contract_status=hydraulic_path_contract_ready_needs_field_topology_and_release_endpoint`。
- `hydraulic_path_feature_term_count=8`。
- `hydraulic_path_schema_ready=False`。
- `hydraulic_path_final_release_gate_needs_effluent_label=True`。
- `next_recommended_core_action=R8u63_add_hydraulic_path_terms_to_soft_sensor_training_schema`。
- 缺失训练字段包括：`path_stage_id`、`hydraulic_path_role`、`stage_coverage_mask`、`direct_path_stage_coverage_mask`、`proxy_path_stage_coverage_mask`、`release_boundary_flag`、`recirculation_loop_flag`、`low_frequency_time_buffer_flag`。

边界：

- 这一步只把水力路径合同转成软传感 feature schema 和训练缺口，不证明路径感知模型已经训练完成。
- 当前仍不能把 polishing proxy coverage 写成 final effluent release 支持。
- 仍需要真实 field topology/path labels、field missingness/layout holdout、final effluent endpoint labels 和 release gate validation。

验证：

- `.venv/bin/python -m py_compile src/water_ai/agents/soft_sensor_matrix_coupling_agent.py experiments/run_agent54_soft_sensor_matrix_coupling.py tests/test_soft_sensor_matrix_coupling_agent.py`：通过。
- `.venv/bin/pytest -q tests/test_soft_sensor_matrix_coupling_agent.py`：4 passed。
- `.venv/bin/python experiments/run_agent54_soft_sensor_matrix_coupling.py`：通过，已刷新 Agent54 metrics/report/deliverable/manifest。
- `.venv/bin/pytest -q tests/test_sensor_network_sparse_placement_agent.py tests/test_soft_sensor_matrix_coupling_agent.py tests/test_multi_facility_collaborative_control_agent.py tests/test_multi_facility_replay_evaluation_agent.py`：38 passed。
- `.venv/bin/pytest -q`：448 passed。

## 2026-06-04 R8u-64：Hydraulic Path Features Enter Soft Sensor Training

目标：

- 承接 R8u-63 的 Agent54 路径阶段训练 gap，把 Agent48 的水力路径覆盖合同从“人类可读 schema gap”推进为软传感模型可消费的数值特征。
- 不新增 agent，不改变 Agent49/52 控制逻辑；先把观测层到状态估计层的接口打稳。
- 让后续低成本传感、循环结构、软传感和闭环控制之间形成更清楚的路径特征主链：传感器不只是属于某个 node/zone/modality/time，还要表达它覆盖水处理路径的哪一段。

实现：

- 更新 `src/water_ai/soft_sensor_model.py`：
  - 新增 `HYDRAULIC_PATH_FEATURE_COLUMNS`，包含 8 个数值化路径特征。
  - `FEATURE_COLUMNS` 从 15 个扩展到 23 个。
  - `readings_to_feature_frame`、`readings_to_training_frame` 和 `predict_final_state` 支持可选 `sensor_layout_interface`。
  - 新增 `hydraulic_path_feature_values()`，把 Agent48/soft sensor interface 的路径合同转成模型特征。
  - `feature_domain_risk` 改为基于模型 payload 的 feature list 计算，兼容旧模型和新模型。
  - 无显式 layout interface 时，`hydraulic_path_feature_values()` 使用 `DEFAULT_HYDRAULIC_PATH_FEATURE_PRIOR` 作为 legacy training prior，而不是把未知布点误判成路径完全未覆盖。
  - 模型输入的 `timestamp_min` 改为观测窗口相对时间，避免闭环多步运行中的全局累计时间触发错误 OOD。
- 更新 `experiments/train_soft_sensor_model.py`：
  - 训练数据构造时调用 `SensorNetworkSparsePlacementAgent(max_sensors=6, budget_limit=5.8)` 生成 synthetic layout prior。
  - 模型版本升级为 `rf_multioutput_v4_path_stage`。
  - 训练输出继续写入 `models/soft_sensor_calibrator.pkl` 和 `outputs/soft_sensor_training/soft_sensor_training_metrics.json`。
- 更新 `src/water_ai/agents/soft_sensor_agent.py`：
  - 校准预测时向软传感模型传入 `sensor_layout_interface`。
  - `_layout_context` 输出 `hydraulic_path_feature_values` 和 `hydraulic_path_contract`，使 Agent2/软传感层能解释路径特征来源。
  - 无 layout 时输出 `hydraulic_path_feature_source=legacy_training_prior_not_field_layout`，明确默认先验不是现场布点证据。
- 更新 `src/water_ai/agents/soft_sensor_matrix_coupling_agent.py`：
  - Agent54 的 `hydraulic_path_feature_contract.feature_terms` 改为模型真实训练特征。
  - `field_schema_terms` 保留 `path_stage_id`、`hydraulic_path_role`、`stage_coverage_mask`、`release_boundary_flag` 等人类可读/现场采集字段。
  - 当 8 个数值路径特征已经进入 `FEATURE_COLUMNS` 后，`hydraulic_path_schema_ready=True`，但仍保留 final effluent endpoint label blocker。
- 更新测试：
  - `tests/test_soft_sensor_agent.py` 检查 layout context 已输出路径特征。
  - `tests/test_soft_sensor_agent.py` 新增无 layout legacy prior 与窗口相对时间测试，防止路径特征升级破坏旧闭环或把后续批次误判为 timestamp OOD。
  - `tests/test_soft_sensor_matrix_coupling_agent.py` 检查 Agent54 识别数值路径特征已进入训练 schema，同时仍阻断 release endpoint。

当前结果：

- 新模型版本：`rf_multioutput_v4_path_stage`。
- 训练行数：51,840。
- 特征数：23。
- 水力路径特征数：8。
- mean MAE：0.01382。
- Agent54 `hydraulic_path_schema_ready=True`。
- Agent54 `missing_hydraulic_path_terms=[]`。
- Agent54 `hydraulic_path_final_release_gate_needs_effluent_label=True`。
- 下一步建议已更新为：补真实 path labels、endpoint labels、layout holdout 和 final effluent 端点标签，验证路径特征是否真的提升状态估计。

边界：

- 这一步证明的是接口和训练 schema 已经打通，不证明 field path-aware performance。
- 当前路径特征来自 Agent48 synthetic layout prior，训练集中路径特征是常量先验，因此不能用当前 MAE 声称路径特征带来真实泛化提升。
- 没有真实 field topology/path labels、layout holdout、final effluent endpoint labels 和 release validation 前，不能写现场 release gate、actuator policy 或 field-supported claim。
- `legacy_training_prior_not_field_layout` 只用于兼容旧链路和保持模型域内推理，不是现场布点证据；一旦进入 field package，必须用真实 layout/path labels 替代该默认先验。

验证：

- `.venv/bin/python -m py_compile src/water_ai/soft_sensor_model.py src/water_ai/agents/soft_sensor_agent.py src/water_ai/agents/soft_sensor_matrix_coupling_agent.py experiments/train_soft_sensor_model.py experiments/run_agent54_soft_sensor_matrix_coupling.py tests/test_soft_sensor_agent.py tests/test_soft_sensor_matrix_coupling_agent.py`：通过。
- `.venv/bin/pytest -q tests/test_soft_sensor_agent.py tests/test_soft_sensor_matrix_coupling_agent.py`：11 passed。
- `.venv/bin/python experiments/run_agent54_soft_sensor_matrix_coupling.py`：通过，已刷新 Agent54 metrics/report/deliverable/manifest。
- `.venv/bin/pytest -q tests/test_soft_sensor_agent.py tests/test_soft_sensor_matrix_coupling_agent.py tests/test_sensor_network_sparse_placement_agent.py tests/test_multi_facility_collaborative_control_agent.py tests/test_multi_facility_replay_evaluation_agent.py`：43 passed。
- `.venv/bin/pytest -q tests/test_soft_sensor_agent.py tests/test_arbitration_agent.py tests/test_closed_loop.py tests/test_control_strategy_agent.py tests/test_scenario_sweep.py`：30 passed。
- `.venv/bin/pytest -q`：450 passed。

## 2026-06-04 Goal Update：Quantified Termination Criteria

目标：

- 回应“迭代缺少终止条件”的架构问题，把无限迭代改造成可计算、可验收、可阶段收束的成熟度治理。
- 不把终止理解为停止项目，而是停止低边际价值堆叠：当某一模块达到阶段门，或没有真实数据无法继续升级时，转向下一高价值问题、真实数据采集、formal search 或人工审查。

实现：

- 新增 `deliverables/model_core_optimization/quantified_goal_termination_criteria.md`。
- 该文件把后续 goal 扩展为：
  - 七层系统骨架评分。
  - 七类核心能力评分。
  - `core_score` 加权计算。
  - 单轮有效迭代终止条件。
  - 模块成熟度门槛。
  - 专利级成熟度门槛。
  - 方法论文/实证论文 readiness 区分。
  - 工程 readiness 门槛。
  - 自我打断节流规则。
  - 阶段终止判定输出格式。

当前规则：

- 若单轮 `core_score` 提升小于 0.05，且没有解决 P1/P2 阻断，应停止扩展，进入复盘或 backlog。
- 若模块输入/输出契约、状态变量、下游回接、测试、证据边界、失败边界和 no-write 边界均达到门槛，应停止该模块继续堆叠，转向上游根因或下游回接。
- 若真实数据缺失，工程阶段终止在 package/gate/template/handoff 完成，不继续伪造 field 结论。

边界：

- 该文件是项目治理合同和 goal 扩展，不产生新的 field evidence。
- TRL、MRL、V&V 和专利交底框架只作为成熟度思想借鉴；当前项目仍需 formal search、真实 field package、operator review 和专利代理人审查，才能进入更高等级结论。

## 2026-06-04 R8u-65：Synthetic Layout Holdout for Hydraulic Path Features

目标：

- 承接 R8u-64 的关键边界：8 个 hydraulic path features 已进入模型，但训练集中此前是常量先验，只能说明接口打通，不能说明路径/布点变化下的泛化能力。
- 不新增 agent，不扩大展示层；在现有软传感训练脚本和 Agent54 readiness 内补齐 synthetic layout holdout benchmark。
- 让路径特征从“schema ready”推进为“synthetic layout holdout ready”，为下一步真实 path labels、endpoint labels 和 node-specific field values 留出明确入口。

实现：

- 更新 `experiments/train_soft_sensor_model.py`：
  - 新增 `LAYOUT_VARIANT_SPECS`，构造 7 个 Agent48 布点变体：
    - `low_cost_stage_gap`
    - `default_proxy_release`
    - `direct_effluent_full_budget`
    - `cost_only_effluent`
    - `random_direct_release`
    - `classification_proxy_release_gap`
    - `topology_robust_release_direct`
  - `build_dataset()` 不再只使用单一 `greedy_marginal:6x10` 布点，而是按 scenario、seed、source、window_min 轮换 layout interface。
  - 每个训练 frame 追加 metadata：`layout_id`、`layout_variant_id`、`layout_holdout_role`、`selected_sensor_count`、`path_stage_count`、`covered_stage_count`。
  - 新增 `_layout_holdout_metrics()`：用 train layout 训练 80-tree holdout evaluator，在 held-out layout 上输出 MAE/R2。
  - 新增 `hydraulic_path_feature_unique_counts`、`hydraulic_path_feature_variation_status`、`layout_variants`、`rows_by_layout_id` 和 `rows_by_layout_holdout_role`。
  - 模型版本升级为 `rf_multioutput_v5_path_layout_holdout`。
- 更新 `src/water_ai/agents/soft_sensor_matrix_coupling_agent.py`：
  - Agent54 readiness 读取训练 metrics 中的 `hydraulic_path_feature_variation_status` 和 `layout_holdout`。
  - 新增 `hydraulic_path_feature_variation_ready`、`layout_holdout_ready`、`layout_holdout_mean_mae`、`layout_holdout_train_layout_count`、`layout_holdout_heldout_layout_count` 和 `layout_holdout_field_boundary`。
  - 当 path schema ready 但缺 layout holdout 时，下一步为 `R8u65_add_synthetic_layout_holdout_for_path_features`。
  - 当 path schema ready 且 layout holdout ready 时，下一步推进为 `R8u66_collect_field_path_endpoint_labels_for_layout_holdout`。
- 更新 `experiments/run_agent54_soft_sensor_matrix_coupling.py`：
  - deliverable/report/manifest 写入 layout holdout 状态、mean MAE、布点变体计数和下一步动作。
  - manifest 自动从训练 metrics 同步 `latest_soft_sensor_model_version`、`latest_soft_sensor_layout_variant_count` 和 `latest_soft_sensor_layout_holdout_mean_mae`。
- 新增 `tests/test_soft_sensor_training_layout_holdout.py`：
  - 固定训练脚本必须构造多布点变体。
  - 固定训练数据必须包含 train/holdout 两类 layout。
  - 固定路径特征不能退化为单一常量。
- 更新 `tests/test_soft_sensor_matrix_coupling_agent.py`：
  - 无 layout holdout metrics 时，Agent54 下一步仍是补 synthetic layout holdout。
  - 有 layout holdout metrics 时，Agent54 下一步切换到真实 path/endpoint labels。

当前结果：

- 新模型版本：`rf_multioutput_v5_path_layout_holdout`。
- 训练行数：51,840。
- layout variant count：7。
- train rows：36,960。
- holdout rows：14,880。
- 随机 split mean MAE：0.0138。
- synthetic layout holdout mean MAE：0.01524。
- layout holdout held-out layouts：
  - `classification_sspoc_proxy:5x10`
  - `greedy_marginal:8x10`
- hydraulic path feature unique counts：
  - `hydraulic_path_coverage_rate`: 3。
  - `direct_hydraulic_path_coverage_rate`: 4。
  - `proxy_hydraulic_path_coverage_rate`: 3。
  - `release_boundary_proxy_flag`: 2。
  - `final_effluent_direct_observed_flag`: 2。
  - `release_endpoint_label_missing_flag`: 2。
- Agent54 `layout_holdout_status=synthetic_layout_holdout_ready_needs_field_path_labels`。
- Agent54 `next_recommended_core_action=R8u66_collect_field_path_endpoint_labels_for_layout_holdout`。

边界：

- 该 holdout 仍是 synthetic layout benchmark，只证明训练 schema、路径特征变体和留出布点评估接口已经形成。
- 因为当前传感值仍是全局 modality stream，不是 node-specific field values，layout holdout 不能证明真实布点部署效果。
- 没有真实 `path_stage` labels、final effluent endpoint labels、field topology、node-specific sensor values 和 offline lab labels 前，不能写 release gate、actuator policy、field-supported claim 或专利创造性结论。

验证：

- `.venv/bin/python -m py_compile experiments/train_soft_sensor_model.py tests/test_soft_sensor_training_layout_holdout.py`：通过。
- `.venv/bin/pytest -q tests/test_soft_sensor_training_layout_holdout.py`：2 passed。
- `.venv/bin/python experiments/train_soft_sensor_model.py`：通过，已刷新 `models/soft_sensor_calibrator.pkl`、training data/report/metrics。
- `.venv/bin/python -m py_compile src/water_ai/agents/soft_sensor_matrix_coupling_agent.py experiments/run_agent54_soft_sensor_matrix_coupling.py tests/test_soft_sensor_matrix_coupling_agent.py`：通过。
- `.venv/bin/pytest -q tests/test_soft_sensor_matrix_coupling_agent.py tests/test_soft_sensor_training_layout_holdout.py tests/test_soft_sensor_agent.py`：14 passed。
- `.venv/bin/python experiments/run_agent54_soft_sensor_matrix_coupling.py`：通过，已刷新 Agent54 deliverable/report/metrics/manifest。
- `.venv/bin/pytest -q`：453 passed。

## 2026-06-04 R8u-66：Field Path/Endpoint Label Package Preflight Gate

目标：

- 承接 R8u-65 的阶段门：synthetic layout holdout 已形成，但不能证明 field path-aware performance。
- 把“需要真实 path_stage/endpoint labels”从一句泛化缺口，压成可计算、可验收、可拒收 template/TODO 的 field package contract。
- 对齐更新后的 goal：本轮必须新增可测试 gate 和证据边界，防止 synthetic/template 结果被写成 field 结论。

实现：

- 更新 `src/water_ai/agents/soft_sensor_matrix_coupling_agent.py`：
  - `__init__` 新增 `field_path_label_package` 输入。
  - `feature_contract` 新增 `field_path_endpoint_label_package_contract` 与 `field_path_endpoint_label_package_preflight`。
  - 新增 `_field_path_endpoint_label_package_contract()`，定义 6 张必需表：
    - `site_topology_or_bed_geometry`
    - `node_modality_sensor_timeseries`
    - `hydraulic_path_stage_labels`
    - `final_effluent_endpoint_labels`
    - `campaign_operation_log`
    - `offline_lab_results`
  - 新增 `_field_path_endpoint_label_package_preflight()`，检查：
    - required tables 是否存在。
    - table shape 是否为 list。
    - 行是否为 object。
    - required fields 是否非空。
    - 是否含 `template_only`、`TODO_*`、`template_not_*` 或 `sample_not_*` 标记。
    - 是否至少 5 个 `batch_id` 跨节点级传感值、路径阶段标签、末端标签、操作日志和 lab label 对齐。
  - readiness 新增：
    - `field_path_endpoint_label_package_status`
    - `field_path_endpoint_label_package_ready`
    - `field_path_endpoint_label_matched_batch_count`
    - `field_path_endpoint_label_minimum_matched_batch_count`
    - `field_path_endpoint_label_missing_tables`
    - `field_path_endpoint_label_preflight_blockers`
    - `can_route_to_field_layout_holdout`
  - 当 synthetic layout holdout ready 但 field package 未通过时，下一步维持 `R8u66_collect_field_path_endpoint_labels_for_layout_holdout`。
  - 当 field package 通过时，下一步升级为 `R8u67_run_field_layout_holdout_with_accepted_path_endpoint_labels`。
  - 新增 issue `field_path_endpoint_label_package_required_for_field_holdout`，防止已有 synthetic holdout 后误升级 field holdout。
- 更新 `experiments/run_agent54_soft_sensor_matrix_coupling.py`：
  - 生成独立文件：
    - `outputs/soft_sensor_matrix_coupling/field_path_endpoint_label_package_contract.json`
    - `outputs/soft_sensor_matrix_coupling/field_path_endpoint_label_package_preflight.json`
    - `outputs/soft_sensor_matrix_coupling/field_path_endpoint_label_package_template.json`
  - template 行显式包含 `template_only=True`、`evidence_status=template_not_field_evidence` 和 `TODO_*` 值。
  - deliverable/report/manifest 写入 R8u-66 package status、matched batch count 和 field layout holdout 路由状态。
- 更新 `tests/test_soft_sensor_matrix_coupling_agent.py`：
  - 无真实包时，Agent54 保持 `R8u66_collect_field_path_endpoint_labels_for_layout_holdout`。
  - 带 template marker 的包会被拒收，`template_or_todo_markers_present` 进入 blockers。
  - 5 个 batch 对齐且字段完整的包会通过 preflight，并把下一步切换到 `R8u67_run_field_layout_holdout_with_accepted_path_endpoint_labels`。

当前结果：

- `field_path_endpoint_label_package_contract` 已生成。
- `field_path_endpoint_label_package_preflight` 当前状态：`no_field_path_endpoint_label_package_supplied`。
- required tables：6。
- missing tables：6。
- matched batch count：0。
- can_route_to_field_layout_holdout：False。
- next operator action：`submit_field_path_endpoint_label_package_rows`。
- Agent54 当前下一步：`R8u66_collect_field_path_endpoint_labels_for_layout_holdout`。

边界：

- 该 preflight 是真实数据进入 field layout holdout 的入口，不生成 field evidence。
- template 文件只能指导现场填报，不能作为 field evidence；原样提交会被拒收。
- 即使 package preflight 通过，也只能进入 field layout holdout/replay；仍不能直接写 release gate、actuator policy、field-supported claim 或实证论文结论。

验证：

- `.venv/bin/python -m py_compile src/water_ai/agents/soft_sensor_matrix_coupling_agent.py tests/test_soft_sensor_matrix_coupling_agent.py`：通过。
- `.venv/bin/pytest -q tests/test_soft_sensor_matrix_coupling_agent.py`：7 passed。
- `.venv/bin/python -m py_compile experiments/run_agent54_soft_sensor_matrix_coupling.py`：通过。
- `.venv/bin/python experiments/run_agent54_soft_sensor_matrix_coupling.py`：通过，已刷新 Agent54 deliverable/report/metrics/manifest 与 R8u-66 contract/preflight/template。
- `.venv/bin/pytest -q tests/test_soft_sensor_matrix_coupling_agent.py tests/test_soft_sensor_training_layout_holdout.py tests/test_soft_sensor_agent.py`：16 passed。
- `.venv/bin/pytest -q`：455 passed。

## 2026-06-04 R8u-67：Quantified Core Score and Termination Gate

目标：

- 承接用户提出的“迭代缺少终止条件”问题，把 goal 中的七类能力评分、单轮有效迭代条件和模块阶段门落实为可运行、可测试、可回写 manifest 的治理 gate。
- 不伪造真实 field package；在 field blocker 未解除时，只做接口、gate、证据边界和终止条件的核心治理增强。
- 让后续迭代能用 `previous_core_score`、`iteration_delta` 和 `stage_decision` 判断继续、复盘、收束或等待真实数据。

实现：

- 更新 `src/water_ai/agents/model_core_optimization_governance_agent.py`：
  - 新增 `CORE_ABILITY_WEIGHTS`，严格按 goal 公式计算：
    - `0.18*observability`
    - `0.16*controllability`
    - `0.14*explainability`
    - `0.18*verifiability`
    - `0.14*engineering_feasibility`
    - `0.10*evolvability`
    - `0.10*protectability`
  - 新增 `MODULE_TERMINATION_THRESHOLDS`，覆盖 input/output contract、state coverage、downstream reconnection、evidence/failure boundary 和 no-write boundary。
  - Agent50 输出新增 `quantified_core_score_gate`：
    - `ability_scores`
    - `core_score`
    - `previous_core_score`
    - `iteration_delta`
    - `iteration_validity_status`
    - `stage_decision`
    - `continue_expansion_allowed`
    - `module_stage_termination_gate`
    - `next_gate_action`
    - `no_write_boundaries`
  - 若 `iteration_delta < 0.05` 且没有解决 P1/P2 或硬阻断，则输出 `low_marginal_gain_without_hard_blocker`，并进入 `stop_expansion_enter_review_or_backlog`。
  - 若出现 synthetic/template/field 边界违规，则输出 `invalid_iteration_evidence_boundary_violation` 并触发回到证据边界。
- 更新 `experiments/run_agent50_model_core_governance.py`：
  - 新增独立产物 `outputs/model_core_governance/core_score_termination_gate.json`。
  - `priority_ranking.json` 同步写入 `quantified_core_score_gate`。
  - `governance_report.md` 和 `agent50_report.md` 显示 `core_score`、`iteration_validity_status`、`stage_decision`、能力分数和模块阶段门。
  - manifest 回写：
    - `latest_agent50_core_score`
    - `latest_agent50_core_score_previous`
    - `latest_agent50_core_score_delta`
    - `latest_agent50_iteration_validity_status`
    - `latest_agent50_stage_decision`
    - `latest_agent50_continue_expansion_allowed`
    - `latest_agent50_module_stage_status`
    - `latest_agent50_next_gate_action`
- 更新 `tests/test_model_core_optimization_governance_agent.py`：
  - 验证 Agent50 输出权重、七类能力分数、core_score、module gate 和 no-write boundary。
  - 验证低增益且未解决硬阻断时停止扩张。
  - 验证即使 `iteration_delta=0`，只要明确解决硬阻断，也能判定为有效迭代。

当前结果：

- `core_score=0.904`。
- `previous_core_score=None`，因此本轮为 baseline 记录，后续轮次可计算 `iteration_delta`。
- `iteration_validity_status=baseline_recorded_needs_next_delta`。
- `stage_decision=continue_core_work_with_quantified_baseline`。
- `next_gate_action=continue_only_on_interfaces_or_packages_that_do_not_fabricate_field_evidence`。
- 模块阶段门：
  - `input_contract_completeness=1.000`
  - `output_contract_completeness=1.000`
  - `state_variable_coverage=0.676`
  - `downstream_reconnection_rate=1.000`
  - `evidence_boundary_completeness=1.000`
  - `failure_boundary_completeness=1.000`
  - `no_write_boundary_clarity=1.000`
- 当前唯一模块阶段 blocker：`state_variable_coverage=0.676 < 0.90`。

边界：

- `core_score` 是架构/接口治理成熟度基线，不是 field validation 分数。
- 真实 field package、field holdout、operator review、actuator feedback 和 release validation 仍缺失。
- 该 gate 不允许写 actuator 或 release gate；它只决定当前迭代应继续、收束、复盘或等待真实数据。

验证：

- `.venv/bin/python -m py_compile src/water_ai/agents/model_core_optimization_governance_agent.py experiments/run_agent50_model_core_governance.py`：通过。
- `.venv/bin/pytest -q tests/test_model_core_optimization_governance_agent.py`：22 passed。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：通过，已刷新 governance report、priority ranking、core score gate 和 manifest。
- `.venv/bin/pytest -q tests/test_model_core_optimization_governance_agent.py tests/test_deliverable_organization_agent.py tests/test_agent_architecture_consolidation_agent.py`：99 passed。
- `.venv/bin/pytest -q`：458 passed。

## 2026-06-04 R8u-68：Hidden State Coverage Ledger and Reproducible Termination Gate

目标：

- 解决 R8u-67 模块阶段门唯一 blocker：`state_variable_coverage=0.676 < 0.90`。
- 不通过“调高分数”解决问题，而是把隐藏状态成熟度拆成可计算、可追踪、可解释的多层覆盖：架构契约、软传感估计、补丁/代理设计、现场验证和控制可用性。
- 让 Agent50 的终止条件可复跑，避免同一轮重新运行时因读取已更新 manifest 而误判为低增益重复工作。

实现：

- 更新 `src/water_ai/agents/model_core_optimization_governance_agent.py`：
  - 新增 `EXPECTED_HIDDEN_STATES`，固定 6 个主链隐藏状态：`pollutant_residual`、`reaction_completion`、`catalyst_activity`、`matrix_interference`、`hydraulic_delay`、`release_or_byproduct_risk`。
  - 新增 `hidden_state_coverage_ledger`，从 Agent48 `hidden_state_requirement_ledger` 与 Agent51 catalyst proxy 读取状态行。
  - 对每个隐藏状态输出：`contract_covered`、`sparse_estimation_ready`、`proxy_design_ready`、`candidate_patch_ready`、`design_or_patch_ready`、`field_validated`、`control_ready`、`coverage_stage` 和 `evidence_boundary`。
  - `state_variable_coverage` 不再使用粗糙平均值，而改为 `state_variable_contract_coverage`；现场验证和控制可用性单独进入 no-write 边界与 supporting metrics。
  - `module_stage_blocker_resolved` 只有在上一轮明确为 `module_stage_needs_more_core_work` 且本轮变为 `module_stage_complete` 时才成立；`not_recorded` 不再被误认为已解决 blocker。
  - `_previous_module_stage_status()` 支持从 `current_work_item.previous_module_stage_status` 读取显式迭代基线。
- 更新 `experiments/run_agent50_model_core_governance.py`：
  - 当前运行上下文明确为 `r8u68_hidden_state_coverage_ledger`。
  - 传入 `previous_core_score` 和 `previous_module_stage_status`，使同一轮 Agent50 复跑保持可复现。
  - `governance_report.md`、`agent50_report.md` 和 manifest 现在显示隐藏状态五层覆盖率。
  - manifest 新增：
    - `latest_agent50_module_stage_status_previous`
    - `latest_agent50_hidden_state_contract_coverage`
    - `latest_agent50_sparse_estimation_ready_coverage`
    - `latest_agent50_design_or_patch_ready_coverage`
    - `latest_agent50_field_validated_state_coverage`
    - `latest_agent50_control_ready_state_coverage`
- 更新 `tests/test_model_core_optimization_governance_agent.py`：
  - 新增隐藏状态 ledger fixture，覆盖 6 个关键隐藏状态。
  - 验证 Agent50 能区分架构合同完成、软传感/补丁设计完成、现场验证未完成和控制写入未完成。
  - 验证 catalyst_activity 当前阶段是 `synthetic_proxy_design_ready_needs_field_labels`，不能支撑 field claim、actuator write 或 release gate。

当前结果：

- `gate_id=R8u68_quantified_core_score_and_hidden_state_termination_gate`。
- `core_score=0.960`。
- `previous_core_score=0.904`。
- `iteration_delta=0.056`。
- `previous_module_stage_status=module_stage_needs_more_core_work`。
- `module_stage_blocker_resolved=True`。
- `iteration_validity_status=valid_iteration`。
- `stage_decision=continue_to_next_highest_value_core_action`。
- 隐藏状态分层覆盖：
  - `state_variable_contract_coverage=1.000`。
  - `sparse_estimation_ready_coverage=0.667`。
  - `design_or_patch_ready_coverage=1.000`。
  - `field_validated_state_coverage=0.000`。
  - `control_ready_state_coverage=0.000`。
- `module_stage_status=module_stage_complete`，blockers 为空。
- `next_gate_action=continue_only_on_interfaces_or_packages_that_do_not_fabricate_field_evidence`。

边界：

- R8u-68 关闭的是“隐藏状态是否进入架构合同”的 blocker，不是现场验证 blocker。
- `field_validated_state_coverage=0.000` 和 `control_ready_state_coverage=0.000` 仍表示 6 个隐藏状态全部缺真实现场验证和控制晋级证据。
- Agent50 仍禁止写 actuator、release gate 或 field-supported claim。
- 后续高价值工作应继续推进 source_basis 细节、真实 field package、field holdout/replay、operator review 和 release validation，而不是继续堆同一 governance gate。

验证：

- `.venv/bin/python -m py_compile src/water_ai/agents/model_core_optimization_governance_agent.py experiments/run_agent50_model_core_governance.py`：通过。
- `.venv/bin/pytest -q tests/test_model_core_optimization_governance_agent.py`：23 passed。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：通过，已刷新 governance report、Agent50 report、priority ranking、core score gate 和 manifest。
- `.venv/bin/pytest -q tests/test_model_core_optimization_governance_agent.py tests/test_deliverable_organization_agent.py tests/test_agent_architecture_consolidation_agent.py`：100 passed。
- `.venv/bin/pytest -q`：459 passed。

## 2026-06-04 R8u-69：Source Basis Detail Consumption and P11 Anti-Stale Gate

目标：

- 承接 R8u-68 的下一步 P11，不再盲目补已经存在的 citation，而是先审计 `kb_sensor_limited_release_evidence` 的 source_basis 是否真的被下游消费。
- 解决统一 Field Evidence Gate 对 Agent59 展开版 source_basis 字符串识别失败的问题。
- 防止 Agent50 在 `source_basis_completion_rate=1.000` 后仍继续推荐“补 citation”，造成低边际价值空转。

实现：

- 更新 `src/water_ai/field_evidence_gate.py`：
  - 新增 `_source_basis_id()`，同时识别短 ID（如 `low_cost_proxy_sensing`）和 Agent59 展开字符串（如 `source_basis_id:low_cost_proxy_sensing; evidence_stage:...`）。
  - `_detailed_source_basis()` 和 `_source_basis_detail_status()` 改为先还原 source_basis ID，再读取 `SOURCE_BASIS_DETAIL_LIBRARY`。
  - 修复后统一门能正确从 Agent59 展开后的 source_basis 中恢复 detail library。
- 更新 `src/water_ai/agents/model_core_optimization_governance_agent.py`：
  - 当 `source_basis_completion_rate >= 0.95` 时，P11 的 `implementation_status` 变为 `source_basis_detail_ready_needs_real_field_package_import`。
  - P11 的 `next_experiment` 明确写成：source_basis detail 已闭合，不要继续补 citation；若有真实 field package，运行 Agent44->42->43->45 和统一 evidence gate；若没有真实包，只能保持 field blocker。
  - Agent50 blocked reasons 和 issue message 也区分 source_basis 未完成与已完成两种情况。
- 更新测试：
  - `tests/test_unified_field_evidence_gate.py` 新增展开版 source_basis 字符串兼容测试。
  - `tests/test_model_core_optimization_governance_agent.py` 新增 anti-stale 测试，确保 source_basis 完成后不再推荐补 citation。

当前结果：

- 统一 Field Evidence Gate 当前输出：
  - `source_basis_completion_rate=1.000`
  - `citation_detail_completion_rate=1.000`
  - `source_basis_parameter_boundary_coverage=1.000`
  - `effective_literature_traceability=1.000`
  - `field_supported_edge_ratio=0.000`
  - `next=R2_agent48_51_54_observation_contract_merge`
- Agent59 当前输出：
  - `source_basis_completion_rate=1.000`
  - 推荐导入真实 field package 并通过 replay/holdout 证据链。
- Agent50 当前 P11 输出：
  - source_basis detail 已闭合。
  - 不再推荐继续补 citation。
  - 剩余 blocker 是真实 field package、Agent44->42->43->45 evidence chain、field replay/holdout 和人工复核。

边界：

- 文献 source_basis detail 完成只代表 literature-supported traceability 完成，不代表 field-supported evidence。
- `field_supported_edge_ratio=0.000`，所以不能升级现场 claim。
- 无真实 field package 时，不能写 actuator、release gate 或 field-supported claim。

验证：

- `.venv/bin/python -m py_compile src/water_ai/agents/model_core_optimization_governance_agent.py src/water_ai/field_evidence_gate.py tests/test_model_core_optimization_governance_agent.py tests/test_unified_field_evidence_gate.py`：通过。
- `.venv/bin/pytest -q tests/test_model_core_optimization_governance_agent.py tests/test_unified_field_evidence_gate.py`：30 passed。
- `.venv/bin/python experiments/run_unified_field_evidence_gate.py && .venv/bin/python experiments/run_agent59_claim_specific_field_package.py && .venv/bin/python experiments/run_unified_field_evidence_gate.py && .venv/bin/python experiments/run_agent50_model_core_governance.py`：通过，已刷新统一门、Agent59、Agent50 产物和 manifest。
- `.venv/bin/pytest -q tests/test_model_core_optimization_governance_agent.py tests/test_unified_field_evidence_gate.py tests/test_claim_specific_field_package_agent.py tests/test_agent_architecture_consolidation_agent.py`：85 passed。
- `.venv/bin/pytest -q`：461 passed。

## 2026-06-04 R8u-70：External Field Blocker Routing and Quantified Stop Condition

目标：

- 回应“迭代缺乏终止条件”的问题，把终止条件从 goal 文字落实为 Agent50 可计算的阶段边界。
- 防止 P11 在 source_basis detail 已闭合后继续占据最高优先级，造成“等待真实数据却继续内部加工”的低边际循环。
- 防止 Agent50 回到已被 R2/R3 消费的旧 P 队列，把 P1/P2/P3/P5 当作未完成的早期任务。

实现：

- 更新 `src/water_ai/agents/model_core_optimization_governance_agent.py`：
  - 新增 `unified_field_evidence_gate_metrics`、`real_field_package_acceptance_metrics`、`observation_contract_metrics` 和 `control_replay_stress_metrics` 输入。
  - 新增 `source_basis_detail_ready`、`field_import_ready`、`field_evidence_chain_ready`、`external_field_blocker_active` 和 `field_evidence_wait_status`。
  - 当 `source_basis_detail_ready=True` 且 `field_import_ready=False` 时，P11 的 `implementation_status` 变为 `waiting_on_real_field_package_external_blocker`，并进入 `external_blocker_backlog`。
  - 当 R2 observation contract 已形成时，P1/P2/P5 标记为 `consumed_by_R2_observation_contract_*`；当 R3 counterfactual stress 已形成时，P3 标记为 `consumed_by_R3_counterfactual_stress_*`。
  - 新增 `WAIT_real_field_package_or_new_core_interface` 推荐动作：当 source_basis/schema/R2/R3 synthetic 链条已形成、剩余高分项都在等真实 field 包时，停止内部扩张。
  - `quantified_core_score_gate` 新增 `external_field_wait_state`，并在该状态下输出 `stage_decision=stop_expansion_wait_for_real_field_package_or_new_core_interface`。
- 更新 `experiments/run_agent50_model_core_governance.py`：
  - 接入 unified gate、R7 acceptance、R2 observation contract 和 R3 counterfactual stress metrics。
  - 当前工作项改为 `r8u70_external_field_blocker_and_completed_core_consumption_router`，刷新 Agent50 governance report、priority ranking 和 core score gate。
- 更新 `tests/test_model_core_optimization_governance_agent.py`：
  - 新增 unified/R7/R2/R3 fixture。
  - 验证 P11 source_basis 完成后进入 external blocker backlog。
  - 验证 R2/R3 已完成时 P1/P2/P3/P5 不再作为下一轮内部最高优先级。
  - 验证推荐动作切换到 `WAIT_real_field_package_or_new_core_interface`，并停止继续扩张。

当前结果：

- Agent50 当前推荐动作：`WAIT_real_field_package_or_new_core_interface`。
- `source_basis_detail_ready=True`。
- `field_import_ready=False`。
- `field_evidence_chain_ready=False`。
- `external_field_blocker_active=True`。
- `external_blocker_backlog` 包含 P11：`waiting_on_real_field_package_external_blocker`。
- `iteration_validity_status=valid_stage_boundary_external_field_wait`。
- `stage_decision=stop_expansion_wait_for_real_field_package_or_new_core_interface`。
- `continue_expansion_allowed=False`。
- `core_score=0.960`，但该分数表示架构/接口/证据治理成熟度，不表示现场验证成熟。

边界：

- 等待态不是模型失败，而是正确的阶段终止条件。
- 没有 `data_origin=field` 的真实包时，不能继续把 synthetic/template/literature 加工成 field-supported claim。
- 当前不能写 actuator、release gate 或 field control effectiveness claim。
- 下一轮只有两类高价值入口：导入真实 field package 并运行 R7/Agent44->42->43->45；或定义新的核心接口/新增真实工程约束/补入可验证数据需求。

验证：

- `.venv/bin/python -m py_compile src/water_ai/agents/model_core_optimization_governance_agent.py experiments/run_agent50_model_core_governance.py tests/test_model_core_optimization_governance_agent.py`：通过。
- `.venv/bin/pytest -q tests/test_model_core_optimization_governance_agent.py`：25 passed。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：通过，已刷新 Agent50 governance report、priority ranking、core score gate 和 manifest。
- `.venv/bin/pytest -q tests/test_model_core_optimization_governance_agent.py tests/test_unified_field_evidence_gate.py tests/test_claim_specific_field_package_agent.py tests/test_agent_architecture_consolidation_agent.py tests/test_control_replay_stress.py tests/test_multi_facility_collaborative_control_agent.py tests/test_multi_facility_replay_evaluation_agent.py`：112 passed。
- `.venv/bin/pytest -q`：462 passed。

## 2026-06-04 R8u-71：Professional Roadmap Evidence Map and Claim Boundary Audit

目标：

- 承接用户要求的专业技术导图，防止导图变成单纯表达层成果。
- 把导图中的创新点、工程实现路径、关键指标和成熟度判断逐条绑定到当前项目输出文件。
- 审计导图是否混淆 synthetic、template、literature 与 field 证据。

实现：

- 新增 `deliverables/model_core_optimization/professional_technical_roadmap_evidence_map.md`：
  - 按 TR01-TR12 映射导图中的主链、隐藏状态 ledger、R2 观测合同、catalyst proxy、软传感路径特征、灰箱 prior、R3 replay stress、source_basis、field package wait state、no-write boundary、专利创新骨架和外部工程方法。
  - 每条主张都包含证据阶段、核心证据文件、指标和当前边界。
  - 给出图 1-9 的可说/不可说边界，明确专业导图不能被用作现场实证证明。
- 新增 `outputs/model_core_governance/professional_technical_roadmap_evidence_audit.json`：
  - `claim_count=12`
  - `traceable_claim_count=12`
  - `unsupported_claim_count=0`
  - `field_overclaim_count=0`
  - `field_supported_claim_count=0`
  - `no_write_boundary_preserved=true`
  - `stage_boundary_status=external_field_package_or_new_core_interface_required`
- 更新 `deliverables/manifest.json`：
  - 登记 `professional_technical_roadmap_evidence_map`
  - 登记 `professional_technical_roadmap_evidence_audit`
  - 登记 `latest_professional_technical_roadmap_field_overclaim_count=0`

当前结果：

- 专业技术导图可以作为技术路线、创新点和工程实现路径的专业说明使用。
- 导图不能作为现场验证、工程部署、专利授权或实证论文结论使用。
- 当前导图中的 field 相关内容均被标为等待真实 package、field replay、field holdout 或 operator review。

边界：

- 本轮没有继续堆旧 P1-P11 功能，符合 R8u-70 的 stop-expansion 阶段门。
- 本轮提升的是可解释性、可验证性、可保护性和证据治理质量，不是现场性能。
- 若后续导入真实 field package，必须先刷新 R7、Agent44->42->43->45、Agent46/47、Agent50，再更新导图和证据映射。

验证：

- `python3 -m json.tool deliverables/manifest.json`：通过。
- `python3 -m json.tool outputs/model_core_governance/professional_technical_roadmap_evidence_audit.json`：通过。
- 专业导图 Mermaid block 数量：11。
- 证据审计主张数：12，field overclaim：0。

## 2026-06-04 R8u-72：R7 Field Evidence Sufficiency Gate

目标：

- 承接用户“先优化 plan 再做”的纠偏，本轮不新增 agent，不继续扩大旧 P 队列。
- 在 R7 真实 field package 验证治理链内新增一个可计算证据充足度 gate。
- 区分三种状态：真实包仍被导入/证据阻断、最小 replay smoke ready、达到推荐校准证据量后可进入 human-review candidate queue。

实现：

- 更新 `src/water_ai/field_package_coverage.py`：
  - 新增 `R7_field_evidence_sufficiency_gate`。
  - gate 检查 field origin/import、claim-specific rows、soft sensor holdout labels、Agent51 catalyst proxy holdout、minimum replay contract、temporal alignment、pressure conflict resolution 和 no-write boundary。
  - 输出 `field_evidence_sufficiency_status`、`field_evidence_sufficiency_score`、`field_evidence_smoke_pass`、`field_evidence_calibration_volume_pass`、`can_route_to_agent42_smoke_replay`、`can_route_to_field_holdout`、`can_route_to_human_review_candidate`、`field_supported_claim_upgrade_ready`、`control_candidate_ready`、`release_gate_candidate_ready` 和 `no_write_boundary_pass`。
  - 3 个同批次有效 replay batch 只允许进入 smoke replay/field holdout；12 个同批次有效 proxy/lab/operation/pressure 事件才允许进入 human-review candidate queue。
  - 即使 gate 达到 human-review candidate，也仍不能写 actuator、release gate 或 field-supported claim。
- 更新 `src/water_ai/real_field_replay_pipeline.py`：
  - 将 field evidence sufficiency gate 字段暴露到 `pipeline_readiness`。
- 更新 `experiments/run_r7_real_field_replay_pipeline.py`：
  - R7 report、deliverable 和 manifest 增加 sufficiency status、score、smoke pass、calibration volume pass、human review candidate 和 field claim upgrade boundary。
- 更新 `tests/test_field_package_coverage.py`：
  - header-only template 必须阻断 sufficiency gate。
  - 3-batch 包能进入 smoke replay，但不能进入 human-review candidate。
  - 12-batch 包能进入 human-review candidate queue，但仍不能写 actuator 或 release gate。

当前结果：

- 当前 header-only template pipeline 输出：
  - `field_evidence_sufficiency_status=field_evidence_sufficiency_blocked_before_import`
  - `field_evidence_sufficiency_score=0.26`
  - `field_evidence_smoke_pass=False`
  - `field_evidence_calibration_volume_pass=False`
  - `can_route_to_human_review_candidate=False`
  - `field_supported_claim_upgrade_ready=False`
- R7 仍正确停在 `real_field_package_acceptance_blocked_at_import`。

边界：

- 该 gate 只判断真实包证据是否足以进入 replay、holdout 和人工复核队列。
- 它不证明现场闭环成立，不证明控制效果，不证明专利授权可能性，不证明实证论文成熟。
- synthetic/template/literature 仍不得被升级为 field evidence。
- actuator 和 release gate 写入仍为 False。

验证：

- `.venv/bin/python -m py_compile src/water_ai/field_package_coverage.py src/water_ai/real_field_replay_pipeline.py experiments/run_r7_real_field_replay_pipeline.py`：通过。
- `.venv/bin/pytest -q tests/test_field_package_coverage.py tests/test_real_field_replay_pipeline.py tests/test_real_field_package_acceptance_gate.py`：25 passed。
- `.venv/bin/python experiments/run_r7_real_field_replay_pipeline.py`：通过，已刷新 R7 pipeline report、metrics、deliverable 和 manifest。
- `python3 -m json.tool deliverables/manifest.json` 与 `python3 -m json.tool outputs/r7_real_field_replay_pipeline/r7_real_field_replay_pipeline_metrics.json`：通过。
- `.venv/bin/pytest -q tests/test_field_package_coverage.py tests/test_real_field_replay_pipeline.py tests/test_real_field_package_acceptance_gate.py tests/test_agent_architecture_consolidation_agent.py tests/test_model_core_optimization_governance_agent.py`：101 passed。
- `.venv/bin/pytest -q`：463 passed。

## 2026-06-04 R8u-73：Agent50 Consumption of R7 Field Evidence Sufficiency Gate

目标：

- 防止 R8u-72 的 `field_evidence_sufficiency_gate` 停留为局部 R7 pipeline 指标。
- 把 R7 真实证据充足度状态回接到 Agent50 的全局阶段门、priority ranking、governance scorecard 和 manifest latest 指针。
- 保持“不新增 agent、不扩张旧 P 队列”的架构收敛原则。

实现：

- 更新 `src/water_ai/agents/model_core_optimization_governance_agent.py`：
  - 新增 `r7_pipeline_metrics` 输入。
  - 新增 `_r7_pipeline_readiness()`、`_r7_field_evidence_sufficiency_status()`、`_r7_field_evidence_sufficiency_score()`、`_r7_field_evidence_smoke_pass()` 和 `_r7_can_route_to_human_review_candidate()`。
  - `governance_scorecard` 现在输出 `r7_field_evidence_sufficiency_status`、`r7_field_evidence_sufficiency_score`、`r7_field_evidence_smoke_pass` 和 `r7_can_route_to_human_review_candidate`。
  - `_field_evidence_wait_status()` 同步输出 R7 sufficiency routing 字段。
  - `_field_import_ready()` 现在把 R7 sufficiency smoke pass 视为真实包已能进入 smoke replay 的进展，避免把 smoke-ready 包误判成“仍未导入”。
- 更新 `experiments/run_agent50_model_core_governance.py`：
  - 读取 `outputs/r7_real_field_replay_pipeline/r7_real_field_replay_pipeline_metrics.json`。
  - 将 R7 pipeline metrics 传入 Agent50。
  - manifest 新增 `latest_agent50_r7_field_evidence_sufficiency_status`、`latest_agent50_r7_field_evidence_sufficiency_score`、`latest_agent50_r7_field_evidence_smoke_pass` 和 `latest_agent50_r7_can_route_to_human_review_candidate`。
- 更新 `tests/test_model_core_optimization_governance_agent.py`：
  - 验证当前 blocked-before-import 状态会被 Agent50 scorecard 和 wait_status 消费。
  - 验证模拟 smoke pass 时，Agent50 会把 `field_import_ready=True`，不再推荐 `WAIT_real_field_package_or_new_core_interface`。

当前结果：

- 当前 Agent50 已消费 R7 pipeline：
  - `r7_field_evidence_sufficiency_status=field_evidence_sufficiency_blocked_before_import`
  - `r7_field_evidence_sufficiency_score=0.26`
  - `r7_field_evidence_smoke_pass=False`
  - `r7_can_route_to_human_review_candidate=False`
- 当前仍推荐 `WAIT_real_field_package_or_new_core_interface`，这是正确阶段边界，因为当前 R7 pipeline 输入仍是 header-only template preflight。

边界：

- R8u-73 是治理回接，不是 field validation。
- R7 smoke pass 只代表可进入 Agent42 smoke replay/field holdout，不代表 field-supported claim、控制效果或 release validation。
- actuator 与 release gate 写入仍为 False。

验证：

- `.venv/bin/python -m py_compile src/water_ai/agents/model_core_optimization_governance_agent.py experiments/run_agent50_model_core_governance.py tests/test_model_core_optimization_governance_agent.py`：通过。
- `.venv/bin/pytest -q tests/test_model_core_optimization_governance_agent.py`：26 passed。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：通过，已刷新 Agent50 report、priority ranking、core score gate 和 manifest。
- `python3 -m json.tool deliverables/manifest.json`、`outputs/agent50_model_core_governance/agent50_report.json`、`outputs/model_core_governance/priority_ranking.json`、`outputs/model_core_governance/core_score_termination_gate.json`：通过。
- `.venv/bin/pytest -q tests/test_model_core_optimization_governance_agent.py tests/test_agent_architecture_consolidation_agent.py tests/test_field_package_coverage.py tests/test_real_field_replay_pipeline.py`：98 passed。
- `.venv/bin/pytest -q`：464 passed。

## 2026-06-04 R8u-74：Agent50 Consumption of Field Path/Endpoint Label Preflight

目标：

- 承接 R8u-73 后的阶段边界：不新增 agent，不继续堆旧 P 队列，而是把已经存在的 R8u-66 `field_path_endpoint_label_package_preflight` 回接到 Agent50。
- 区分三类现场证据门：
  - R7 smoke replay/import progress：是否已有足够真实包进入最小回放入口。
  - field layout holdout：是否已有路径阶段标签、节点级模态时序、操作日志、实验室标签和最终出水终点标签支撑布局 holdout。
  - release endpoint boundary：是否已有最终出水终点标签，防止 polishing 代理观测被误写成 release gate 证据。
- 让 Agent50 的等待态不再泛泛写“缺真实数据”，而是明确指出缺少哪些路径/终点标签表、能否进入布局 holdout、release gate endpoint 是否仍被阻断。

实现：

- 更新 `src/water_ai/agents/model_core_optimization_governance_agent.py`：
  - 新增 `field_path_endpoint_label_preflight` 输入。
  - 新增 `_field_path_endpoint_label_preflight_status()`、`_field_path_endpoint_matched_batch_count()`、`_field_path_endpoint_required_tables()`、`_field_path_endpoint_missing_tables()`、`_field_path_endpoint_label_package_ready()`、`_field_path_endpoint_final_effluent_label_ready()`、`_can_route_to_field_layout_holdout_with_path_labels()` 和 `_release_gate_endpoint_label_blocked()`。
  - `governance_scorecard` 现在输出 `field_path_endpoint_label_preflight_status`、`field_path_endpoint_matched_batch_count`、`field_path_endpoint_label_package_ready`、`field_path_endpoint_final_effluent_label_ready`、`can_route_to_field_layout_holdout_with_path_labels` 和 `release_gate_endpoint_label_blocked`。
  - `_field_evidence_wait_status()` 同步输出路径/终点标签 preflight 的 required tables、missing tables、matched batch count、layout holdout routing 和 release endpoint blocker。
  - `_blocked_reasons()` 新增 R8u66 路径/终点标签包阻断原因。
  - `_issues()` 新增 `field_path_endpoint_label_package_required`，明确 Agent54 synthetic layout contract 不能升级成 field layout holdout 或 release gate 支持。
- 更新 `experiments/run_agent50_model_core_governance.py`：
  - 读取 `outputs/soft_sensor_matrix_coupling/field_path_endpoint_label_package_preflight.json`。
  - 将 preflight 传入 Agent50。
  - Agent50 report 和 manifest latest 指针新增路径/终点标签 preflight 状态。
- 更新 `tests/test_model_core_optimization_governance_agent.py`：
  - 新增当前阻断态测试：无路径/终点标签包时，`can_route_to_field_layout_holdout_with_path_labels=False`、`release_gate_endpoint_label_blocked=True`。
  - 新增模拟 ready 测试：R7 smoke pass 且 5 个匹配 batch 的路径/终点标签包 ready 时，可以进入 field layout holdout 路由，但 `no_write_boundaries.can_write_to_release_gate` 仍为 False。

当前结果：

- 当前 Agent50 已消费 R8u-66 preflight：
  - `field_path_endpoint_label_preflight_status=no_field_path_endpoint_label_package_supplied`
  - `field_path_endpoint_matched_batch_count=0`
  - `field_path_endpoint_label_package_ready=False`
  - `field_path_endpoint_final_effluent_label_ready=False`
  - `can_route_to_field_layout_holdout_with_path_labels=False`
  - `release_gate_endpoint_label_blocked=True`
- 当前缺失表被明确压到 6 张：
  - `site_topology_or_bed_geometry`
  - `node_modality_sensor_timeseries`
  - `hydraulic_path_stage_labels`
  - `final_effluent_endpoint_labels`
  - `campaign_operation_log`
  - `offline_lab_results`
- Agent50 仍推荐 `WAIT_real_field_package_or_new_core_interface`，阶段判定仍为 `stop_expansion_wait_for_real_field_package_or_new_core_interface`。这次变化不是放开等待态，而是把等待态拆得更精确。

边界：

- R8u-74 是治理回接与验证边界增强，不是 field validation。
- `field_import_ready=True` 只表示可进入 smoke replay/import progress；它不自动等于 field layout holdout ready。
- field layout holdout 需要路径阶段标签和最终出水终点标签包通过 preflight。
- 即使模拟路径/终点标签包 ready，也只允许进入 field layout holdout/review 路由；不能写 actuator，不能写 release gate，不能升级 field-supported claim。
- synthetic/template/literature 仍不得被升级为 field evidence。

验证：

- `.venv/bin/pytest -q tests/test_model_core_optimization_governance_agent.py`：28 passed。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：通过，已刷新 Agent50 report、priority ranking、core score gate 和 manifest。
- `.venv/bin/pytest -q`：466 passed。

## 2026-06-04 R8u-75：R7 Dynamic Field Path/Endpoint Label Preflight Gate

目标：

- 承接 R8u-74：Agent50 已经能读取 R8u-66 的路径/终点标签 preflight，但那仍主要依赖 Agent54 生成的静态 JSON。
- 本轮把这个 preflight 前移到 R7 real field replay package 入口，让当前 package directory 自己动态决定是否具备 field layout holdout 所需的路径阶段标签、节点模态传感、操作日志、实验室标签和最终出水终点标签。
- 核心目的不是放开现场结论，而是让“真实包是否能进入路径感知 holdout”变成可计算、可回放、可被 Agent50 消费的动态 gate。

实现：

- 更新 `src/water_ai/agents/soft_sensor_matrix_coupling_agent.py`：
  - 暴露 `build_field_path_endpoint_label_package_contract()`。
  - 暴露 `preflight_field_path_endpoint_label_package()`。
  - 复用 R8u-66 已定义的同一套合同与 preflight 逻辑，避免另起一套路径/终点标签规则。
- 更新 `src/water_ai/real_field_replay_pipeline.py`：
  - R7 pipeline 在读取当前 package 后，直接对 `raw_tables` 执行 path/endpoint label preflight。
  - pipeline 顶层新增 `field_path_endpoint_label_package_preflight`。
  - pipeline readiness 新增：
    - `field_path_endpoint_label_preflight_status`
    - `field_path_endpoint_matched_batch_count`
    - `field_path_endpoint_minimum_matched_batch_count`
    - `field_path_endpoint_missing_tables`
    - `field_path_endpoint_required_field_gap_count`
    - `field_path_endpoint_template_marker_count`
    - `field_path_endpoint_label_package_ready`
    - `field_path_endpoint_final_effluent_label_ready`
    - `can_route_to_field_layout_holdout_with_path_labels`
    - `release_gate_endpoint_label_blocked`
- 更新 `src/water_ai/agents/field_replay_import_agent.py`：
  - R7 field package loader/template spec 扩展到 R8u-66 supplement tables。
  - 新增或扩展表头：
    - `node_modality_sensor_timeseries`
    - `site_topology_or_bed_geometry`
    - `hydraulic_path_stage_labels`
    - `final_effluent_endpoint_labels`
  - 继续保留原 R7/R7j/R8p field package 行级来源、模板标记和 import gate 约束。
- 更新 `experiments/run_r7_real_field_replay_pipeline.py`：
  - report、deliverable、manifest latest 指针输出 R7 动态 path/endpoint preflight 结果。
- 更新 `experiments/run_agent50_model_core_governance.py`：
  - Agent50 现在优先消费 R7 pipeline 里的动态 `field_path_endpoint_label_package_preflight`。
  - 只有 R7 未提供该字段时，才回退到 Agent54 的静态 preflight 文件。
- 更新 `src/water_ai/agents/pressure_resolution_replay_scenario_pack_agent.py`：
  - 修正 R8p `data_origin` provenance 冲突。
  - 即使 R8u-66 采集 CSV 中存在 `data_origin` 字段，R8p staging 仍从 metadata 复制 `data_origin`，不直接信任行级来源声明。

当前结果：

- 当前 header-only template 已被动态识别为包存在但不具备真实路径/终点标签证据：
  - `field_path_endpoint_label_preflight_status=field_path_endpoint_label_package_blocked_by_preflight`
  - `field_path_endpoint_matched_batch_count=0`
  - `field_path_endpoint_label_package_ready=False`
  - `can_route_to_field_layout_holdout_with_path_labels=False`
  - `release_gate_endpoint_label_blocked=True`
- 新增测试证明：当构造 5 个 batch 且补齐路径/终点标签、节点模态、操作日志和实验室标签时，R8u-66 path/endpoint preflight 可以通过。
- 但同一个测试也明确证明：path/endpoint package ready 不等于 R7 field layout holdout ready；如果 claim-specific rows、soft holdout 或 field evidence sufficiency 仍缺，R7 仍必须阻断 field layout holdout 和 field-supported claim upgrade。

边界：

- R8u-75 是真实包入口 gate 增强，不是 field validation。
- 动态 preflight 通过，只说明包具备进入路径感知 layout holdout/replay 的最低结构条件。
- 它不能直接升级为真实现场结论，不能写 actuator，不能写 release gate，不能替代 field holdout、replay、人工复核和 claim gate。
- `data_origin` 必须来自 package metadata/validated provenance gate，不能由单行 CSV 自称来源后被系统接受。

验证：

- `.venv/bin/pytest -q tests/test_real_field_replay_pipeline.py tests/test_soft_sensor_matrix_coupling_agent.py tests/test_model_core_optimization_governance_agent.py`：通过。
- `.venv/bin/pytest -q tests/test_field_replay_import_agent.py tests/test_real_field_package_acceptance_gate.py tests/test_field_package_coverage.py tests/test_real_field_replay_pipeline.py tests/test_soft_sensor_matrix_coupling_agent.py tests/test_model_core_optimization_governance_agent.py`：71 passed。
- `.venv/bin/python experiments/run_r7_real_field_replay_pipeline.py`：通过，当前 R7 仍停在 `real_field_package_acceptance_blocked_at_import`，这是 header-only template 下的正确保护状态。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：通过，Agent50 仍推荐 `WAIT_real_field_package_or_new_core_interface`。
- `.venv/bin/pytest -q tests/test_pressure_resolution_replay_scenario_pack_agent.py::test_pressure_resolution_r7_to_r8p_alignment_separates_shared_fields_and_replay_export tests/test_pressure_resolution_replay_scenario_pack_agent.py::test_pressure_resolution_r7_staging_builds_draft_but_keeps_operator_and_agent52_gaps`：2 passed。
- `.venv/bin/pytest -q`：467 passed。

## 2026-06-04 R8u-76：Field Path/Endpoint Same-Batch Alignment Diagnostics

目标：

- 承接 R8u-75：R7 已经能动态检查当前 package directory 的路径/终点标签 preflight，但 `matched_batch_count=0` 对真实采集操作者还不够可执行。
- 本轮不新增 agent，不放开任何控制门，而是把 path/endpoint gate 细化为可计算的 row count、batch count、batch alignment gap 和补包 patch plan。
- 阶段终止条件：
  - header-only template 必须显示 `required_matched_batch_deficit=5`。
  - 2-batch 部分包必须显示 `matched_batch_count=2`、`required_matched_batch_deficit=3`。
  - 5-batch 完整包必须显示 alignment ready，但仍不能绕过 R7 claim-specific/soft holdout/release gate。

实现：

- 更新 `src/water_ai/agents/soft_sensor_matrix_coupling_agent.py`：
  - R8u-66 `field_path_endpoint_label_package_preflight` 新增：
    - `table_row_counts`
    - `table_batch_counts`
    - `batch_alignment_gap_count`
    - `required_matched_batch_deficit`
    - `missing_batch_ids_by_table`
    - `alignment_patch_plan`
  - 新增内部对齐诊断方法：
    - `_field_path_endpoint_batch_universe()`
    - `_field_path_endpoint_alignment_patch_plan()`
  - `alignment_patch_plan` 输出 P1/P2 补包项，尤其是 `R8U76_MINIMUM_MATCHED_BATCH_DEFICIT`，用于指明还差多少个跨表 same-batch 证据包。
- 更新 `src/water_ai/real_field_replay_pipeline.py`：
  - pipeline readiness 消费并暴露新字段：
    - `field_path_endpoint_table_row_counts`
    - `field_path_endpoint_table_batch_counts`
    - `field_path_endpoint_batch_alignment_gap_count`
    - `field_path_endpoint_required_matched_batch_deficit`
    - `field_path_endpoint_alignment_patch_plan_status`
    - `field_path_endpoint_alignment_patch_plan_item_count`
- 更新 `experiments/run_r7_real_field_replay_pipeline.py`：
  - R7 report、deliverable 和 manifest latest 指针同步输出 path/endpoint batch alignment 诊断。
- 更新 `src/water_ai/agents/model_core_optimization_governance_agent.py`：
  - Agent50 governance scorecard 和 field evidence wait status 消费 batch alignment deficit、alignment gap 和 patch plan status。
  - 这些字段只作为采集/验证治理信息，不改变 release/actuator no-write 边界。
- 更新 `experiments/run_agent50_model_core_governance.py`：
  - 当 Agent50 只能从 R7 readiness fallback 构造 preflight 时，也保留 alignment patch plan 状态和缺口数量。

当前结果：

- 当前 header-only template：
  - `field_path_endpoint_label_preflight_status=field_path_endpoint_label_package_blocked_by_preflight`
  - `field_path_endpoint_matched_batch_count=0`
  - `field_path_endpoint_required_matched_batch_deficit=5`
  - `field_path_endpoint_batch_alignment_gap_count=0`
  - `field_path_endpoint_alignment_patch_plan_status=field_path_endpoint_alignment_blocked_by_preflight`
  - `field_path_endpoint_alignment_patch_plan_item_count=7`
- 这意味着当前不是“泛泛缺真实数据”，而是明确还需要至少 5 个同批次真实包横跨：
  - `node_modality_sensor_timeseries`
  - `hydraulic_path_stage_labels`
  - `final_effluent_endpoint_labels`
  - `campaign_operation_log`
  - `offline_lab_results`
- 新增 2-batch 测试证明：如果操作者只补了 2 个 aligned batch，系统会给出 `matched_batch_count=2`、`required_matched_batch_deficit=3`，而不是简单报错。
- 新增 5-batch 测试证明：完整 path/endpoint package 可进入 preflight ready；但若 R7 claim-specific rows、soft holdout 或 field evidence sufficiency 仍未满足，仍然不能进入 field-supported claim、actuator 或 release gate。

边界：

- R8u-76 是验证治理层和工程接入层的增强，不是 field validation。
- `alignment_patch_plan` 只说明该补哪些真实行、补齐哪些 same-batch 链接；它不制造 field evidence。
- path/endpoint preflight ready 只允许进入 field layout holdout/replay 路由，不能替代 operator review、release validation、field-supported claim gate，也不能写 actuator 或 release gate。

验证：

- `.venv/bin/python -m py_compile src/water_ai/agents/soft_sensor_matrix_coupling_agent.py src/water_ai/real_field_replay_pipeline.py src/water_ai/agents/model_core_optimization_governance_agent.py experiments/run_r7_real_field_replay_pipeline.py experiments/run_agent50_model_core_governance.py`：通过。
- `.venv/bin/pytest -q tests/test_real_field_replay_pipeline.py tests/test_model_core_optimization_governance_agent.py`：33 passed。
- `.venv/bin/python experiments/run_r7_real_field_replay_pipeline.py`：通过，已刷新 R7 pipeline metrics/report/manifest。
- `.venv/bin/python experiments/run_agent54_soft_sensor_matrix_coupling.py`：通过，已刷新 Agent54 field_path_endpoint preflight。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：通过，Agent50 已消费 R7 动态 alignment 诊断，阶段门仍保持 `WAIT_real_field_package_or_new_core_interface`。
- `.venv/bin/pytest -q tests/test_real_field_replay_pipeline.py tests/test_model_core_optimization_governance_agent.py tests/test_soft_sensor_matrix_coupling_agent.py tests/test_field_replay_import_agent.py`：50 passed。
- `.venv/bin/pytest -q`：468 passed。

## 2026-06-04 R8u-77：R7 Field Package Submission Readiness Gate

目标：

- 承接 R8u-76：R7 已经分别输出 import preflight、coverage patch plan、path/endpoint alignment、field evidence sufficiency 和 R7 acceptance，但真实包提交者仍需要跨多个 JSON/Markdown 才知道“最高优先先修什么”。
- 本轮不新增 agent，不放开任何控制门，而是在 R7 pipeline 内新增一个 `field_package_submission_readiness` 汇总 gate，把分散阻断压成单一、可排序、可机读的提交状态。
- 核心目标是缩短现场接入主链：真实包提交时先看一个 gate，就能知道是否能进入 Agent42 smoke replay、是否能进入 path-aware layout holdout、是否能进入 human review，以及 no-write 边界是否仍被保护。

实现：

- 更新 `src/water_ai/real_field_replay_pipeline.py`：
  - `build_real_field_replay_pipeline()` 现在生成并返回 `field_package_submission_readiness`。
  - pipeline readiness 同步输出：
    - `field_package_submission_readiness_status`
    - `field_package_submission_highest_priority_blocker`
    - `field_package_submission_next_operator_action`
    - `field_package_submission_blocking_stage_count`
    - `field_package_submission_can_submit_to_agent42_smoke_replay`
    - `field_package_submission_can_route_to_path_endpoint_layout_holdout`
    - `field_package_submission_no_write_boundary_pass`
  - 新增内部函数：
    - `_field_package_submission_readiness()`
    - `_submission_stage()`
    - `_coverage_patch_actions()`
    - `_path_endpoint_patch_actions()`
    - `_submission_next_operator_action()`
    - `_submission_operator_action_queue()`
    - `_submission_status()`
  - 汇总 gate 的 stage checks 覆盖：
    - `R7A_IMPORT_PREFLIGHT`
    - `R7I_MINIMUM_REPLAY_CONTRACT`
    - `R8U66_PATH_ENDPOINT_ALIGNMENT`
    - `R7_FIELD_EVIDENCE_SUFFICIENCY`
    - `R7_ACCEPTANCE`
    - `NO_WRITE_BOUNDARY`
- 更新 `experiments/run_r7_real_field_replay_pipeline.py`：
  - R7 report、deliverable 和 manifest latest 指针输出 submission readiness 状态、最高阻断、下一步动作和 no-write 边界。
- 更新 `src/water_ai/agents/model_core_optimization_governance_agent.py`：
  - Agent50 governance scorecard 和 field evidence wait status 读取：
    - `r7_submission_readiness_status`
    - `r7_submission_highest_priority_blocker`
    - `r7_submission_next_operator_action`
    - `r7_submission_blocking_stage_count`
  - 这些字段只用于治理观察，不改变 `WAIT_real_field_package_or_new_core_interface` 阶段门，也不允许写 release/actuator。
- 更新 `experiments/run_agent50_model_core_governance.py`：
  - Agent50 Markdown report 与 manifest latest 指针同步 R7 submission readiness 字段。

当前结果：

- 当前 header-only template 的 R7 submission readiness：
  - `submission_readiness_status=field_package_submission_blocked_at_import_preflight`
  - `highest_priority_blocker=R7A_IMPORT_PREFLIGHT`
  - `next_operator_action=repair_metadata_headers_and_real_rows_before_agent42`
  - `blocking_stage_count=5`
  - `can_submit_to_agent42_smoke_replay=False`
  - `can_route_to_path_endpoint_layout_holdout=False`
  - `no_write_boundary_pass=True`
- 5-batch path/endpoint 完整测试包会显示 path/endpoint ready，但 submission gate 仍会停在 `field_package_submission_import_ready_needs_replay_evidence`，最高阻断为 `R7_FIELD_EVIDENCE_SUFFICIENCY`，说明 path labels ready 不等于 field claim/control/release ready。
- Agent50 已消费该 gate，并把当前最高阻断保持为真实包入口问题；全局阶段判定仍是 `stop_expansion_wait_for_real_field_package_or_new_core_interface`。

边界：

- R8u-77 是 R7 真实包提交治理接口，不是 field validation。
- `field_package_submission_readiness` 只负责排序修复动作和路由下一阶段；它不生成 field evidence，不升级 claim，不授权 actuator 或 release gate。
- 即使 `can_submit_to_agent42_smoke_replay=True`，也只能进入 replay/holdout/人工复核链路；不能越过 R7 acceptance、operator review 和 release validation。

验证：

- `.venv/bin/python -m py_compile src/water_ai/real_field_replay_pipeline.py src/water_ai/agents/model_core_optimization_governance_agent.py experiments/run_r7_real_field_replay_pipeline.py experiments/run_agent50_model_core_governance.py`：通过。
- `.venv/bin/pytest -q tests/test_real_field_replay_pipeline.py`：5 passed。
- `.venv/bin/pytest -q tests/test_real_field_replay_pipeline.py tests/test_model_core_optimization_governance_agent.py`：33 passed。
- `.venv/bin/python experiments/run_r7_real_field_replay_pipeline.py`：通过，已刷新 R7 metrics/report/deliverable/manifest。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：通过，已刷新 Agent50 report/manifest。
- `.venv/bin/pytest -q`：468 passed。

## 2026-06-04 R8u-78：Formal Search Review Readiness Gate

背景：

- 承接 R8u-77 的模式：真实 field package 已有单一 submission readiness gate，但 formal search / 专利交底审查链仍分散在多个 JSON 中。
- 当前不应继续写展示材料或生成法律/专利结论；最高边际价值是把正式检索、人工非法律技术比较、外部正式审查和交底修订入口压成可计算路由。
- 该轮不执行正式检索，不生成 prior-art 结论，不写权利要求文本，不升级 field-supported claim。

实现：

- 更新 `src/water_ai/agents/agent_architecture_consolidation_agent.py`：
  - 新增 `_formal_search_review_readiness()`。
  - Agent60 report metrics 新增 `formal_search_review_readiness`。
  - 汇总 stage checks 覆盖：
    - `NO_LEGAL_OR_FIELD_CLAIM_BOUNDARY`
    - `FSR_SOURCE_PREFLIGHT`
    - `FSR_ROW_PREFLIGHT`
    - `FSR_VALIDATION_EXECUTION`
    - `FSR_NONLEGAL_REVIEW_PACKET`
    - `FSR_NONLEGAL_REVIEW_RESPONSE`
    - `FSR_CLAIM_SCOPE_PATCH_DRAFT`
    - `FSR_FORMAL_COUNSEL_RESPONSE`
    - `FSR_DISCLOSURE_REVISION_QUEUE`
    - `FSR_DISCLOSURE_REVISION_IMPACT_PLAN`
  - 输出：
    - `formal_search_review_readiness_status`
    - `highest_priority_blocker`
    - `blocking_stage_count`
    - `next_operator_action`
    - `operator_action_queue`
    - `can_route_to_validation_gate`
    - `can_enter_human_nonlegal_comparison_review`
    - `human_nonlegal_review_completed`
    - `can_route_to_claim_scope_patch_draft`
    - `can_route_to_formal_counsel_review`
    - `external_formal_review_completed`
    - `can_route_to_disclosure_editor`
    - `can_route_to_human_artifact_revision`
    - `boundary_violation_count`
- 更新 `experiments/run_agent60_agent_architecture_consolidation.py`：
  - 新增 `outputs/agent_architecture_consolidation/formal_search_review_readiness.json`。
  - Agent60 report/deliverable 输出 readiness 状态、最高阻断、下一步动作和边界违规数。
  - `deliverables/manifest.json` 新增 formal search review readiness 路径和 latest 指针。
- 更新 `tests/test_agent_architecture_consolidation_agent.py`：
  - 无正式检索结果包时必须阻断在 `FSR_SOURCE_PREFLIGHT`。
  - 合格正式检索结果包只能进入人工非法律技术比较，不能生成 prior-art 结论。
  - 人工非法律审查回填后只能进入外部正式审查。
  - 外部正式审查回填后只能进入人工交底修订 impact plan，仍不能自动生成权利要求文本、法律意见或 field claim。

当前结果：

- 当前默认状态：
  - `formal_search_review_readiness_status=formal_search_review_blocked_at_result_package_source_preflight`
  - `highest_priority_blocker=FSR_SOURCE_PREFLIGHT`
  - `next_operator_action=submit_formal_search_result_package`
  - `blocking_stage_count=9`
  - `boundary_violation_count=0`
- no-write / no-legal 边界：
  - `can_generate_prior_art_result=False`
  - `legal_opinion_allowed=False`
  - `can_emit_claim_text=False`
  - `field_claim_upgrade_allowed=False`
- 该 gate 明确把专利级成熟度当前阻断定位为正式检索结果包与人工/正式审查回填链，而不是文档润色或展示问题。

边界：

- R8u-78 是验证治理层和专利级成熟度路由接口，不是正式法律意见。
- 它不替代专业检索、专利代理人判断或真实 field validation。
- 即使后续所有 formal review gate 通过，也只能进入人工交底修订和下一轮 human review；不能由系统自动生成权利要求文本或现场成立结论。

验证：

- `.venv/bin/python -m py_compile src/water_ai/agents/agent_architecture_consolidation_agent.py experiments/run_agent60_agent_architecture_consolidation.py tests/test_agent_architecture_consolidation_agent.py`：通过。
- `.venv/bin/pytest -q tests/test_agent_architecture_consolidation_agent.py`：51 passed。
- `.venv/bin/python experiments/run_agent60_agent_architecture_consolidation.py`：通过，已刷新 Agent60 metrics/report/deliverable/manifest。
- `.venv/bin/python -m json.tool outputs/agent_architecture_consolidation/formal_search_review_readiness.json`：通过。
- `.venv/bin/python -m json.tool deliverables/manifest.json`：通过。
- `.venv/bin/pytest -q`：468 passed。

## 2026-06-04 R8u-79：Formal Search Execution Route Plan

背景：

- R8u-78 已把 formal search / 专利交底审查链压成 `formal_search_review_readiness`，当前最高阻断是 `FSR_SOURCE_PREFLIGHT`。
- 不能为了通过 preflight 而伪造正式检索结果包，也不能把 `nonlegal_prior_art_seed_matrix` 当成 accepted prior-art hit。
- 本轮目标是把 `submit_formal_search_result_package` 拆成外部/人工检索者可执行的路线：搜什么库、用什么 query、填什么表、保留什么 gate、哪些内容必须拒收。

实现：

- 更新 `src/water_ai/agents/agent_architecture_consolidation_agent.py`：
  - `AgentArchitectureConsolidationAgent` 新增可选输入 `nonlegal_prior_art_seed_matrix`。
  - 新增 `_formal_search_execution_route_plan()`。
  - Agent60 metrics 新增 `formal_search_execution_route_plan`。
  - route plan 聚合：
    - `formal_search_work_package_matrix`
    - `formal_search_result_package_template`
    - `formal_search_result_package_submission_template`
    - `formal_search_review_readiness`
    - 可选 `nonlegal_prior_art_seed_matrix`
  - 每个 route row 输出：
    - search databases
    - English / Chinese generated queries
    - classification hints
    - mapped nonlegal seed references
    - required result tables
    - package manifest fields
    - prior-art hit table fields
    - claim-element comparison fields
    - execution steps
    - rejection boundaries
    - preserved field validation gate
- 更新 `experiments/run_agent60_agent_architecture_consolidation.py`：
  - 读取 `outputs/agent_architecture_consolidation/nonlegal_prior_art_seed_matrix.json`。
  - 新增 `outputs/agent_architecture_consolidation/formal_search_execution_route_plan.json`。
  - Agent60 report/deliverable 输出 route plan 状态、路线数量和首个执行动作。
  - manifest latest 指针新增 formal search execution route plan 字段。
- 更新 `tests/test_agent_architecture_consolidation_agent.py`：
  - 默认 route plan 必须 7/7 ready，且不能生成 prior-art 结论、法律意见、权利要求文本或 field claim。
  - 当传入 nonlegal seed matrix 时，seed 只能映射为 route reference，不能升级为正式检索结果。

当前结果：

- `formal_search_execution_route_plan.json`：
  - `route_plan_status=formal_search_execution_route_plan_ready_waiting_for_external_search_execution`
  - `route_row_count=7`
  - `complete_route_row_count=7`
  - `mapped_seed_route_count=7`
  - `operator_first_action=execute_external_or_human_search_and_submit_FORMAL_SEARCH_RESULT_PACKAGE_PATH`
- 边界：
  - `can_submit_synthetic_or_template_result_package=False`
  - `can_generate_prior_art_result=False`
  - `legal_opinion_allowed=False`
  - `can_emit_claim_text=False`
  - `field_claim_upgrade_allowed=False`

边界：

- R8u-79 是 formal search 执行路线计划，不是 formal search result。
- 它可以指导人工/外部检索者生产结果包，但不能替代检索、人工技术比对、专利代理人审查或 field validation。
- nonlegal seed 只作为检索参考线索，不能作为 accepted hit 写入结果包。

验证：

- `.venv/bin/python -m py_compile src/water_ai/agents/agent_architecture_consolidation_agent.py experiments/run_agent60_agent_architecture_consolidation.py tests/test_agent_architecture_consolidation_agent.py`：通过。
- `.venv/bin/pytest -q tests/test_agent_architecture_consolidation_agent.py`：52 passed。
- `.venv/bin/python experiments/run_agent60_agent_architecture_consolidation.py`：通过，已刷新 Agent60 metrics/report/deliverable/manifest。
- `.venv/bin/python -m json.tool outputs/agent_architecture_consolidation/formal_search_execution_route_plan.json`：通过。
- `.venv/bin/python -m json.tool deliverables/manifest.json`：通过。
- `.venv/bin/pytest -q`：469 passed。

## 2026-06-04 R8u-80：Agent50 Consumption of Formal Search Execution Route Plan

背景：

- R8u-79 已生成 `formal_search_execution_route_plan`，但如果全局治理 Agent50 不消费它，该路线计划仍只是 Agent60 局部产物。
- 本轮目标不是新增检索结论，而是让 Agent50 能区分：
  - formal search result package 仍缺失；
  - 但正式检索执行路线、结果包填报合同和 no-legal/no-field 边界已经 ready。
- 这提升的是验证治理层与可保护性接口，不解除真实 field package 或正式检索结果包的外部阻断。

实现：

- 更新 `src/water_ai/agents/model_core_optimization_governance_agent.py`：
  - `ModelCoreOptimizationGovernanceAgent` 新增输入 `formal_search_execution_route_plan`。
  - governance scorecard 新增：
    - `formal_search_execution_route_plan_status`
    - `formal_search_execution_complete_route_row_count`
    - `formal_search_execution_route_row_count`
    - `formal_search_execution_mapped_seed_route_count`
    - `formal_search_execution_operator_first_action`
    - `formal_search_execution_boundary_preserved`
  - 新增 helper：
    - `_formal_search_execution_route_plan_status()`
    - `_formal_search_execution_route_plan_ready()`
    - `_formal_search_execution_route_row_count()`
    - `_formal_search_execution_complete_route_row_count()`
    - `_formal_search_execution_mapped_seed_route_count()`
    - `_formal_search_execution_operator_first_action()`
    - `_formal_search_execution_boundary_preserved()`
  - `protectability` ability score 新增轻量 route-plan readiness 项，但只有在 no-prior-art/no-legal/no-claim/no-field/no-template 边界全部 preserved 时才计入。
  - blocked reasons 新增说明：route plan ready 只是 external/human search execution handoff，仍需要 reviewer-filled `FORMAL_SEARCH_RESULT_PACKAGE_PATH`。
- 更新 `experiments/run_agent50_model_core_governance.py`：
  - 读取 `outputs/agent_architecture_consolidation/formal_search_execution_route_plan.json`。
  - current work item 切换为 `r8u80_consume_formal_search_execution_route_plan`。
  - governance report、Agent50 payload 和 manifest latest 指针输出 formal route plan consumption 字段。
- 更新 `tests/test_model_core_optimization_governance_agent.py`：
  - 新增测试验证 Agent50 消费 R8u-79 route plan，并使 protectability 高于无 route plan 基线。
  - 新增测试验证如果 route plan 试图允许 `can_emit_claim_text=True`，Agent50 不会把它当成 ready 的 route plan。

当前结果：

- Agent50 当前已消费 R8u-79：
  - `formal_search_execution_route_plan_status=formal_search_execution_route_plan_ready_waiting_for_external_search_execution`
  - `formal_search_execution_complete_route_row_count=7`
  - `formal_search_execution_route_row_count=7`
  - `formal_search_execution_mapped_seed_route_count=7`
  - `formal_search_execution_operator_first_action=execute_external_or_human_search_and_submit_FORMAL_SEARCH_RESULT_PACKAGE_PATH`
  - `formal_search_execution_boundary_preserved=True`
- `protectability=1.0`，但该分数只表示专利级接口/边界/路线成熟，不表示专利授权、正式检索完成或现场验证完成。
- Agent50 的全局推荐仍是 `WAIT_real_field_package_or_new_core_interface`，因为真实 field package 和正式检索结果包都仍是外部输入。

边界：

- R8u-80 是全局治理回接，不是 formal search result。
- 它不生成 prior-art 结论、不生成法律意见、不生成权利要求文本、不升级 field-supported claim。
- 即使 route plan 已 ready，也必须等待 reviewer-filled `FORMAL_SEARCH_RESULT_PACKAGE_PATH` 后才能进入 R8u-78 validation/nonlegal/formal counsel 链。

验证：

- `.venv/bin/python -m py_compile src/water_ai/agents/model_core_optimization_governance_agent.py experiments/run_agent50_model_core_governance.py tests/test_model_core_optimization_governance_agent.py`：通过。
- `.venv/bin/pytest -q tests/test_model_core_optimization_governance_agent.py`：30 passed。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：通过，已刷新 Agent50 report/governance report/manifest。
- `.venv/bin/python -m json.tool deliverables/manifest.json`：通过。
- `.venv/bin/python -m json.tool outputs/model_core_governance/priority_ranking.json`：通过。
- `.venv/bin/python -m json.tool outputs/model_core_governance/core_score_termination_gate.json`：通过。
- `.venv/bin/python -m json.tool outputs/agent50_model_core_governance/agent50_report.json`：通过。
- `.venv/bin/pytest -q`：471 passed。

## 2026-06-04 R8u-81：External Evidence Activation Contract

背景：

- R8u-80 后，Agent50 已能消费 formal search execution route plan，但全局阶段门仍停在 `WAIT_real_field_package_or_new_core_interface`。
- 该等待态此前能说明“缺真实 field package / formal result package”，但还没有一个统一、机器可读的恢复合同说明：哪些外部包可以让系统离开等待态、每个包提交到哪里、需要哪些证据、哪些 template/synthetic/seed-only 输入必须拒收。
- 本轮不新增 agent 编号，不生成 field/formal 结论；目标是在 Agent50 内新增可测试 `external_activation_contract`，把外部等待态压成验证治理接口。

实现：

- 更新 `src/water_ai/agents/model_core_optimization_governance_agent.py`：
  - 新增 `_external_activation_contract()`。
  - Agent50 metrics 新增 `external_activation_contract`。
  - governance scorecard 新增：
    - `external_activation_contract_status`
    - `external_activation_ready`
    - `external_activation_ready_channel_count`
    - `external_activation_blocked_channel_count`
    - `external_activation_next_operator_actions`
    - `external_activation_boundary_preserved`
  - contract 统一 3 个外部入口：
    - `R7_REAL_FIELD_PACKAGE`：`REAL_FIELD_REPLAY_PACKAGE_DIR`，恢复 Agent44->42->43->45 field evidence chain。
    - `R8U66_PATH_ENDPOINT_LABEL_PACKAGE`：`FIELD_PATH_ENDPOINT_LABEL_PACKAGE_DIR`，恢复 path/endpoint label layout holdout。
    - `R8U79_FORMAL_SEARCH_RESULT_PACKAGE`：`FORMAL_SEARCH_RESULT_PACKAGE_PATH`，恢复 formal search validation/nonlegal/formal counsel/human disclosure revision 链。
  - 每个入口输出 required evidence、resumes_to、reject_if、next_operator_action 和 no-write boundary。
- 更新 `experiments/run_agent50_model_core_governance.py`：
  - current work item 切换为 `r8u81_external_evidence_activation_contract`。
  - 新增 `outputs/model_core_governance/external_activation_contract.json`。
  - governance report、Agent50 short report、priority ranking 和 manifest latest 指针输出 activation contract 状态。
- 更新 `tests/test_model_core_optimization_governance_agent.py`：
  - 新增默认等待态测试：真实 field/path/formal 入口都不能恢复主链，formal route 只能作为外部 handoff。
  - 新增 ready 态测试：当 R7 smoke pass 且 path/endpoint labels ready 时，field 和 path 两个通道可恢复验证链，但 formal result 仍不能自动恢复，actuator/release gate 仍保持 no-write。

当前结果：

- `outputs/model_core_governance/external_activation_contract.json`：
  - `contract_id=R8u81_external_evidence_activation_contract`
  - `contract_status=waiting_for_external_evidence_packages`
  - `activation_ready=False`
  - `ready_channel_count=0`
  - `handoff_ready_channel_count=3`
  - `blocked_channel_count=3`
  - `boundary_preserved=True`
- manifest latest 指针已新增：
  - `latest_agent50_external_activation_contract`
  - `latest_agent50_external_activation_contract_status`
  - `latest_agent50_external_activation_ready`
  - `latest_agent50_external_activation_ready_channel_count`
  - `latest_agent50_external_activation_blocked_channel_count`
  - `latest_agent50_external_activation_boundary_preserved`
  - `latest_agent50_external_activation_next_operator_actions`
- Agent50 全局推荐仍是 `WAIT_real_field_package_or_new_core_interface`，这是正确阶段边界。

边界：

- R8u-81 是验证治理层接口，不是 field evidence、formal search result、法律意见、权利要求文本或现场控制结论。
- `activation_ready=False` 表示当前任何外部入口都尚不能恢复主链；`ready_for_external_submission=True` 只表示操作者可以按合同提交包，不表示包已通过。
- 所有通道均明确拒收 header-only template、synthetic/sample/template provenance、seed-only prior-art 和模型生成的 claim/legal/field 结论。
- actuator 与 release gate 仍需要 field replay/holdout、operator review、工程执行约束验证和 release validation。

验证：

- `.venv/bin/python -m py_compile src/water_ai/agents/model_core_optimization_governance_agent.py experiments/run_agent50_model_core_governance.py tests/test_model_core_optimization_governance_agent.py`：通过。
- `.venv/bin/pytest -q tests/test_model_core_optimization_governance_agent.py`：32 passed。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：通过，已刷新 Agent50 report/governance report/manifest。
- `.venv/bin/python -m json.tool outputs/model_core_governance/external_activation_contract.json`：通过。
- `.venv/bin/python -m json.tool outputs/model_core_governance/priority_ranking.json`：通过。
- `.venv/bin/python -m json.tool outputs/model_core_governance/core_score_termination_gate.json`：通过。
- `.venv/bin/python -m json.tool outputs/agent50_model_core_governance/agent50_report.json`：通过。
- `.venv/bin/python -m json.tool deliverables/manifest.json`：通过。
- `.venv/bin/pytest -q`：473 passed。

## 2026-06-04 R8u-82：External Activation Router

背景：

- R8u-81 已经把真实 field package、path/endpoint label package 和 formal search result package 三个外部入口压成统一 `external_activation_contract`。
- 但合同本身还只是说明“应该提交什么”和“会恢复哪条链路”，缺少一个路径感知执行入口来检查环境变量是否设置、路径是否存在、路径类型是否正确、以及 path/endpoint label 包是否能通过既有 preflight。
- 本轮不新增 agent 编号，不执行 field replay，不执行 formal search，不生成 field/formal/legal/claim 结论；目标是让等待态具备可操作恢复路径。

实现：

- 新增 `src/water_ai/external_activation_router.py`：
  - 读取 R8u-81 activation contract 和环境变量。
  - 路由 `REAL_FIELD_REPLAY_PACKAGE_DIR` 到 R7 real field replay pipeline。
  - 路由 `FIELD_PATH_ENDPOINT_LABEL_PACKAGE_DIR` 到 R8u-66 path/endpoint label preflight 与 layout holdout 前置链。
  - 路由 `FORMAL_SEARCH_RESULT_PACKAGE_PATH` 到 Agent60 formal search result preflight/review 链。
  - 对 field package 与 formal result package 执行路径存在性和文件/目录类型检查；对 path/endpoint label package 额外读取 CSV 并调用既有 `preflight_field_path_endpoint_label_package()`，避免“目录存在就算证据”。
- 新增 `experiments/run_external_activation_router.py`：
  - 输出 `outputs/model_core_governance/external_activation_router.json`。
  - 输出 `deliverables/model_core_optimization/external_activation_router.md`。
  - 回写 manifest latest 指针和状态字段。
- 新增 `tests/test_external_activation_router.py`：
  - 验证未设置外部路径时保持等待态。
  - 验证错误路径类型会被拒收。
  - 验证真实 field directory 和 formal result file 只进入对应恢复路线。
  - 验证 path/endpoint label package 必须通过 same-batch preflight 后才 route ready。

当前结果：

- `outputs/model_core_governance/external_activation_router.json`：
  - `router_id=R8u82_external_activation_router`
  - `router_status=external_activation_router_waiting_for_external_paths`
  - `path_supplied_count=0`
  - `route_ready_count=0`
  - `blocked_route_count=3`
  - `boundary_preserved=True`
- 当前默认环境下 3 个外部入口都未设置：
  - `REAL_FIELD_REPLAY_PACKAGE_DIR:not_set`
  - `FIELD_PATH_ENDPOINT_LABEL_PACKAGE_DIR:not_set`
  - `FORMAL_SEARCH_RESULT_PACKAGE_PATH:not_set`
- manifest 已新增 `latest_external_activation_router*` 字段，`notes/current_status.md` 已同步 R8u-82 状态。

边界：

- R8u-82 是验证治理层的恢复路由器，不是 field evidence、formal search result、专利法律意见、权利要求文本、控制执行器命令或 release gate。
- 路径存在不等于证据成立；path/endpoint label 包还必须通过既有 preflight，formal search result 包还必须进入 Agent60 formal search validation/review 链。
- `route_ready=True` 只表示可进入对应验证链；不能直接升级 field-supported claim，不能写 actuator，不能写 release gate。

验证：

- `.venv/bin/python -m py_compile src/water_ai/external_activation_router.py experiments/run_external_activation_router.py tests/test_external_activation_router.py`：通过。
- `.venv/bin/pytest -q tests/test_external_activation_router.py`：4 passed。
- `.venv/bin/python experiments/run_external_activation_router.py`：通过，已刷新 router JSON/report/manifest。
- `.venv/bin/python -m json.tool outputs/model_core_governance/external_activation_router.json`：通过。
- `.venv/bin/python -m json.tool deliverables/manifest.json`：通过。
- `.venv/bin/pytest -q tests/test_external_activation_router.py tests/test_model_core_optimization_governance_agent.py tests/test_real_field_replay_pipeline.py tests/test_agent_architecture_consolidation_agent.py`：93 passed。
- `.venv/bin/pytest -q`：477 passed。

## 2026-06-04 R8u-83：Consume External Activation Router in Agent50

背景：

- R8u-82 已经把 R8u-81 的 external activation contract 变成路径感知 router，但该 router 还只是独立 JSON/report。
- 若 Agent50 不消费 router 状态，全局治理层只能看到“外部激活合同”，不能看到“外部路径是否已设置、路由是否 ready、当前是否只是等待路径”的执行态。
- 本轮不新增 agent 编号，不改变控制策略，不执行 field replay，不执行 formal search；目标是把 router 作为验证治理层输入回接 Agent50，提升下游回接率、工程接入清晰度和 no-write 边界可见性。

实现：

- 更新 `src/water_ai/agents/model_core_optimization_governance_agent.py`：
  - `ModelCoreOptimizationGovernanceAgent` 新增可选输入 `external_activation_router`。
  - governance scorecard 新增：
    - `external_activation_router_status`
    - `external_activation_router_consumed`
    - `external_activation_router_path_supplied_count`
    - `external_activation_router_route_ready_count`
    - `external_activation_router_blocked_route_count`
    - `external_activation_router_boundary_preserved`
    - `external_activation_router_no_write_boundary`
  - 新增 helper，确保 router 缺失时为 `external_activation_router_not_consumed_by_agent50`，不会误报 ready 或 field evidence。
- 更新 `experiments/run_agent50_model_core_governance.py`：
  - 读取 `outputs/model_core_governance/external_activation_router.json`。
  - current work item 切换为 `r8u83_consume_external_activation_router`。
  - governance report、Agent50 markdown/json 和 manifest latest 指针输出 router consumption 字段。
- 更新 `tests/test_model_core_optimization_governance_agent.py`：
  - 默认无 router 时，Agent50 明确输出 `external_activation_router_not_consumed_by_agent50`，且 route_ready_count=0、boundary_preserved=False。
  - 有 R8u-82 waiting router 时，Agent50 输出 `external_activation_router_consumed=True`、status=`external_activation_router_waiting_for_external_paths`、path_supplied_count=0、route_ready_count=0、blocked_route_count=3、boundary_preserved=True。

当前结果：

- Agent50 已消费 R8u-82：
  - `external_activation_router_status=external_activation_router_waiting_for_external_paths`
  - `external_activation_router_consumed=True`
  - `external_activation_router_path_supplied_count=0`
  - `external_activation_router_route_ready_count=0`
  - `external_activation_router_blocked_route_count=3`
  - `external_activation_router_boundary_preserved=True`
- Agent50 全局阶段判定仍为 `stop_expansion_wait_for_real_field_package_or_new_core_interface`。
- 最高推荐仍为 `WAIT_real_field_package_or_new_core_interface`，这是正确阶段边界：真实 field package、path/endpoint label package 和 formal search result package 都还未提交。

边界：

- R8u-83 是 Agent50 对 R8u-82 router 状态的消费，不是新证据源。
- `external_activation_router_consumed=True` 只表示全局治理层看到了 router 执行态；它不等于任何外部包已通过。
- 当前 0 ready route、3 blocked route，所以不能升级 field-supported claim，不能写 actuator，不能写 release gate，不能生成法律意见或权利要求文本。

验证：

- `.venv/bin/python -m py_compile src/water_ai/agents/model_core_optimization_governance_agent.py experiments/run_agent50_model_core_governance.py tests/test_model_core_optimization_governance_agent.py`：通过。
- `.venv/bin/pytest -q tests/test_model_core_optimization_governance_agent.py`：33 passed。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：通过，已刷新 Agent50 report/governance report/manifest。
- `.venv/bin/python -m json.tool deliverables/manifest.json`：通过。
- `.venv/bin/python -m json.tool outputs/agent50_model_core_governance/agent50_report.json`：通过。
- `.venv/bin/python -m json.tool outputs/model_core_governance/priority_ranking.json`：通过。
- `.venv/bin/python -m json.tool outputs/model_core_governance/core_score_termination_gate.json`：通过。
- `.venv/bin/python -m json.tool outputs/model_core_governance/external_activation_router.json`：通过。
- `.venv/bin/pytest -q tests/test_external_activation_router.py tests/test_model_core_optimization_governance_agent.py tests/test_real_field_replay_pipeline.py tests/test_agent_architecture_consolidation_agent.py`：94 passed。
- `.venv/bin/pytest -q`：478 passed。

## 2026-06-04 R8u-84：Field Package Preflight Route Guard

背景：

- R8u-82 的 external activation router 已能检查外部路径是否设置、是否存在、类型是否正确。
- 但 `REAL_FIELD_REPLAY_PACKAGE_DIR` 路线仍有一个工程风险：只要提交的是存在的目录，router 就会标记为 `activation_route_ready_for_r7_pipeline_execution`，哪怕该目录是空目录、header-only template、placeholder metadata 或 non-field package。
- 这不会直接生成 field evidence，但会给“能恢复主链”的语义带来噪声。按照 goal 的证据边界原则，真实 field route 应至少先通过 Agent44 field package preflight，才能算可恢复 R7/Agent42 链。

实现：

- 更新 `src/water_ai/external_activation_router.py`：
  - 对 `R7_REAL_FIELD_PACKAGE` 增加 `_field_package_route()`。
  - 调用既有 `preflight_field_replay_package()`，检查 metadata、必需 CSV、headers、placeholder metadata、真实行、data_origin、Agent44 schema/type/linkage blockers。
  - 只有 `can_pass_to_timestamped_replay=True` 时，才输出：
    - `route_status=activation_route_ready_for_r7_pipeline_execution`
    - `route_ready=True`
    - `can_resume_model_chain=True`
    - R7 pipeline command preview。
  - 若 preflight 未通过，输出：
    - `route_status=activation_route_blocked_by_field_package_preflight`
    - `blocked_reason=field_package_preflight_not_ready`
    - `field_package_preflight` 完整预检结果
    - 来自 Agent44 preflight 的下一步修复动作。
  - 若 preflight 读取失败，输出 `activation_route_blocked_by_field_package_preflight_error`，不让异常路径伪装成 ready。
- 更新 `experiments/run_external_activation_router.py`：
  - Markdown route 表新增 `预检` 和 `阻断原因` 两列。
  - field route 显示 `field_package_preflight.status`；path/endpoint route 显示 `path_endpoint_preflight.preflight_status`。
- 更新 `tests/test_external_activation_router.py`：
  - 原“空 field 目录 ready”测试改为“空 field 目录被 field package preflight 阻断”。
  - 新增完整 field package 测试，只有 metadata + 五张主表 + 真实行通过 Agent44 preflight 后，R7 route 才 ready。
  - path/endpoint 与 formal route 测试保持通过。

当前结果：

- 默认未设置外部路径时，router 状态仍为：
  - `router_status=external_activation_router_waiting_for_external_paths`
  - `path_supplied_count=0`
  - `route_ready_count=0`
  - `blocked_route_count=3`
  - `boundary_preserved=True`
- 如果未来设置 `REAL_FIELD_REPLAY_PACKAGE_DIR`：
  - 空目录、缺 metadata、缺 CSV/header、header-only template、placeholder metadata、non-field origin、无真实行或 Agent44 type/linkage blocker 都会被 router 阻断。
  - 只有通过 Agent44 preflight 的真实包才可进入 R7 pipeline execution route。

边界：

- R8u-84 只收紧恢复路线，不创建 field evidence。
- `field_package_preflight_ready_for_agent42` 只表示可进入 timestamped replay / R7 pipeline，不表示 field-supported claim、soft sensor holdout、protective control 或 release gate 已成立。
- 即使 R7 route ready，actuator、release gate、legal/patent claim 和 field-supported conclusion 仍需后续 replay/holdout/operator/release validation gates。

验证：

- `.venv/bin/python -m py_compile src/water_ai/external_activation_router.py experiments/run_external_activation_router.py tests/test_external_activation_router.py`：通过。
- `.venv/bin/pytest -q tests/test_external_activation_router.py`：5 passed。
- `.venv/bin/python experiments/run_external_activation_router.py`：通过，已刷新 router JSON/report/manifest。
- `.venv/bin/pytest -q tests/test_external_activation_router.py tests/test_field_replay_import_agent.py tests/test_real_field_replay_pipeline.py tests/test_model_core_optimization_governance_agent.py`：53 passed。
- `.venv/bin/pytest -q`：479 passed。

## 2026-06-21 R8u-88：Core Gate Resume Action Contract

背景：

- 当前 Agent50 已能输出 `external_activation_contract.json`，其中列出 R7 真实 field package、R8u66 path/endpoint label package 和 R8u79 formal search result package 三条外部恢复通道。
- 但 `core_score_termination_gate.json` 只给出 `stage_decision=stop_expansion_wait_for_real_field_package_or_new_core_interface`，没有直接携带机器可读的 `next_allowed_actions` 和 `external_resume_conditions`。
- 这会让后续 agent 或人工复盘必须再扫描 external activation contract、manifest 和日志才能知道“停在哪里、下一步交什么、交完恢复到哪里”，增加 scan 摩擦。

实现：

- 更新 `src/water_ai/agents/model_core_optimization_governance_agent.py`：
  - `_quantified_core_score_gate()` 接收 `external_activation_contract`。
  - 新增 `_next_allowed_actions_for_stage()`，当阶段门进入外部等待态时，输出 4 类允许动作：
    - `R7_REAL_FIELD_PACKAGE` / `REAL_FIELD_REPLAY_PACKAGE_DIR`
    - `R8U66_PATH_ENDPOINT_LABEL_PACKAGE` / `FIELD_PATH_ENDPOINT_LABEL_PACKAGE_DIR`
    - `R8U79_FORMAL_SEARCH_RESULT_PACKAGE` / `FORMAL_SEARCH_RESULT_PACKAGE_PATH`
    - `NEW_CORE_INTERFACE`
  - 新增 `_external_resume_conditions_for_stage()`，把每条 channel 的 `current_status`、`can_resume_model_chain`、`required_evidence`、`reject_if` 和 `resumes_to` 回填到 core gate。
- 更新 `experiments/run_agent50_model_core_governance.py`：
  - manifest 新增 `latest_agent50_next_allowed_actions`。
  - manifest 新增 `latest_agent50_external_resume_conditions`。
- 更新 `tests/test_model_core_optimization_governance_agent.py`：
  - 阶段门处于外部等待态时，必须包含三条外部恢复通道和一条新核心接口通道。
  - R7 恢复条件必须保留 `data_origin=field` 证据要求。
  - 恢复动作必须保留不能写 actuator/release/field claim/legal conclusion 的边界。
- 更新 `deliverables/README.md`、`deliverables/artifact_index.md`、`notes/current_status.md`。

当前结果：

- `outputs/model_core_governance/core_score_termination_gate.json`：
  - `stage_decision=stop_expansion_wait_for_real_field_package_or_new_core_interface`
  - `next_allowed_actions` 包含 4 条允许动作。
  - `external_resume_conditions.contract_status=waiting_for_external_evidence_packages`
  - 三条外部通道当前 `can_resume_model_chain=False`。
- `deliverables/manifest.json` 已暴露同一批 latest 指针，后续无需扫描多个文件即可知道恢复动作。

边界：

- R8u-88 不新增 field evidence，不执行 field replay，不执行 formal search。
- 三条外部通道仍需真实包或人工/外部检索结果才能恢复主链。
- 该轮只增强验证治理层和工程化接口清晰度，不能写 actuator、release gate、法律结论或 field-supported claim。

验证：

- `.venv/bin/pytest tests/test_model_core_optimization_governance_agent.py -q`：34 passed。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：通过，已刷新 core gate、external activation contract、Agent50/governance report 和 manifest。
- `.venv/bin/python -m json.tool outputs/model_core_governance/core_score_termination_gate.json`：通过。
- `.venv/bin/python -m json.tool outputs/model_core_governance/external_activation_contract.json`：通过。
- `.venv/bin/python -m json.tool deliverables/manifest.json`：通过。

## 2026-06-21 R8u-89：Stage Boundary Verdict Alignment

背景：

- R8u-88 已把外部恢复动作写入 `core_score_termination_gate.json`，阶段门明确为 `stop_expansion_wait_for_real_field_package_or_new_core_interface`。
- 但 Agent50 的 `self_interrupt_verdict` 仍输出 `continue_core_work`，这与阶段门语义不一致：它容易让后续 agent 或人工复盘误以为可以继续内部扩张。
- 按低摩擦自我打断原则，外部等待态不应被表述为 hard interrupt，也不应被表述为继续内部工作，而应是一个独立的阶段边界等待状态。

实现：

- 更新 `src/water_ai/agents/model_core_optimization_governance_agent.py`：
  - `self_interrupt_verdict` 现在接收 `quantified_core_score_gate.stage_decision`。
  - 当阶段门为 `stop_expansion_wait_for_real_field_package_or_new_core_interface` 时，输出 `stage_boundary_wait_for_external_activation`。
  - hard risk 仍优先输出 `interrupt_and_refocus`。
  - 新增对应 `self_interrupt_reason`。
  - 新增 INFO 级 issue：`stage_boundary_wait_for_external_activation`。
  - recommendations 增加“停止继续堆叠内部 synthetic/template 产物”的提示。
- 更新 `experiments/run_agent50_model_core_governance.py`：
  - `priority_ranking.json` 增加 `self_interrupt_reason`。
  - manifest 增加 `latest_agent50_self_interrupt_verdict` 与 `latest_agent50_self_interrupt_reason`。
  - issue priority、governance report、Agent50 report 均显示 reason。
  - `user_interrupt_lessons.md` 与 `self_interrupt_checklist.md` 生成文本增加外部激活等待条件。
- 更新 `tests/test_model_core_optimization_governance_agent.py`：
  - 外部等待态必须输出 `stage_boundary_wait_for_external_activation`。
  - reason 必须说明外部激活等待。
  - issues 与 recommendations 必须包含对应边界信号。
- 更新 `deliverables/README.md` 与 `notes/current_status.md`。

当前结果：

- `outputs/model_core_governance/priority_ranking.json`：
  - `self_interrupt_verdict=stage_boundary_wait_for_external_activation`
  - `self_interrupt_reason=当前不是硬中断，也不是继续内部扩张；量化阶段门已进入外部激活等待，只允许提交真实外部证据包或定义新的可测试核心接口。`
- `deliverables/manifest.json` 已暴露同一 latest 指针。
- Agent50 summary 现在同时显示：
  - 推荐任务 `WAIT_real_field_package_or_new_core_interface`
  - 自我打断结论 `stage_boundary_wait_for_external_activation`
  - 阶段判定 `stop_expansion_wait_for_real_field_package_or_new_core_interface`

边界：

- R8u-89 不改变 Agent48/49 控制逻辑，不生成 field evidence。
- 该 verdict 不是新的频繁打断机制，而是为了区分三种状态：硬中断、普通继续、阶段边界等待外部激活。
- 当前仍不能写 actuator、release gate、法律结论或 field-supported claim。

验证：

- `.venv/bin/pytest tests/test_model_core_optimization_governance_agent.py -q`：34 passed。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：通过，已刷新 priority JSON、Agent50/governance report、manifest 和治理文档。

## 2026-06-21 R8u-90：Router Execution State Backfilled Into Core Gate

背景：

- R8u-88 让 `core_score_termination_gate.json` 知道“外部等待态允许提交哪些包”。
- R8u-89 让 `self_interrupt_verdict` 与阶段门对齐。
- 但 core gate 仍不知道 `external_activation_router.json` 的执行态：例如路径是否设置、哪条 route 是最高阻断、下一步 operator action 是什么、该运行哪个预检命令。
- 这使 core gate 仍需要结合 manifest/router/priority 多个文件才能回答“下一步怎么恢复主链”。

实现：

- 更新 `src/water_ai/agents/model_core_optimization_governance_agent.py`：
  - `next_allowed_actions` 的每条外部证据包动作新增：
    - `router_status`
    - `router_route_status`
    - `router_blocked_reason`
    - `router_operator_action`
    - `router_preflight_status`
    - `router_validation_command`
  - `external_resume_conditions` 新增：
    - `router_status`
    - `router_consumed`
    - `router_path_supplied_count`
    - `router_route_ready_count`
    - `router_blocked_route_count`
    - `router_boundary_preserved`
    - `router_ready_channel_ids`
    - `router_blocked_channel_ids`
    - `router_highest_priority_blocker`
    - `router_next_operator_action`
    - `router_validation_command`
    - `router_route_summary`
- 更新 `tests/test_model_core_optimization_governance_agent.py`：
  - router 未被 Agent50 消费时，core gate 必须显式输出 `external_activation_router_not_consumed_by_agent50`。
  - router 被消费且等待 env var 时，core gate 必须输出 3 条 blocked route、最高阻断和 `set_REAL_FIELD_REPLAY_PACKAGE_DIR`。
  - field route 已提交但被 preflight 阻断时，core gate 必须输出 field package preflight status。
- 重新运行 `experiments/run_agent50_model_core_governance.py`，刷新 core gate、priority JSON、Agent50 report、governance report 和 manifest。
- 更新 `deliverables/README.md` 与 `notes/current_status.md`。

当前结果：

- `outputs/model_core_governance/core_score_termination_gate.json`：
  - `external_resume_conditions.router_status=external_activation_router_waiting_for_external_paths`
  - `external_resume_conditions.router_consumed=True`
  - `external_resume_conditions.router_route_ready_count=0`
  - `external_resume_conditions.router_blocked_route_count=3`
  - `external_resume_conditions.router_highest_priority_blocker=R7_REAL_FIELD_PACKAGE:REAL_FIELD_REPLAY_PACKAGE_DIR:not_set`
  - `external_resume_conditions.router_next_operator_action=set_REAL_FIELD_REPLAY_PACKAGE_DIR`
  - `next_allowed_actions[*].router_validation_command=.venv/bin/python experiments/run_external_activation_router.py`

边界：

- R8u-90 不执行 router，不提交外部包，不导入 field package。
- router execution state 只是验证治理接口，不是 field evidence、formal search result、法律结论或 release gate 依据。
- 当前仍不能写 actuator、release gate、field-supported claim 或 patent/legal conclusions。

验证：

- `.venv/bin/pytest tests/test_model_core_optimization_governance_agent.py -q`：34 passed。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：通过，已刷新 core gate 与 manifest。
- `.venv/bin/python -m json.tool outputs/model_core_governance/core_score_termination_gate.json`：通过。
- `.venv/bin/python -m json.tool outputs/model_core_governance/priority_ranking.json`：通过。
- `.venv/bin/python -m json.tool deliverables/manifest.json`：通过。

## 2026-06-21 R8u-91：Formal Search Route Preflight Guard

背景：

- R8u-84 已把 R7 field route 从“目录存在即可 ready”收紧为 Agent44 field replay package preflight。
- R8u-90 已把 router 执行态回填进 core gate。
- 但 `R8U79_FORMAL_SEARCH_RESULT_PACKAGE` 仍存在同类风险：只要 `FORMAL_SEARCH_RESULT_PACKAGE_PATH` 指向一个存在的 JSON 文件，router 就会标记为 `activation_route_ready_for_agent60_formal_search_preflight`。
- 这会让 seed matrix、submission template 或空壳 JSON 有机会被误读成“formal search result route ready”。

实现：

- 更新 `src/water_ai/external_activation_router.py`：
  - `R8U79_FORMAL_SEARCH_RESULT_PACKAGE` 不再走通用文件存在检查。
  - 新增 `_formal_search_result_route()`。
  - 复用 `AgentArchitectureConsolidationAgent(formal_search_result_package_path=...).run([])` 的既有 formal search result package preflight：
    - `formal_search_result_package_source_preflight`
    - `formal_search_result_package_row_preflight`
    - `formal_search_result_validation_execution`
  - 只有 `row_preflight.can_route_to_validation_gate=True` 时，route 才 ready。
  - 若 source/row preflight 不通过，则输出 `activation_route_blocked_by_formal_search_result_preflight` 与 `formal_search_result_preflight_not_ready`。
- 更新 `src/water_ai/agents/model_core_optimization_governance_agent.py`：
  - `_external_activation_router_preflight_status()` 现在能读取 formal search row/source preflight status。
- 更新 `tests/test_external_activation_router.py`：
  - 原“formal 文件存在即 ready”断言改为“空壳 formal JSON 被 formal preflight 阻断”。
  - 新增 `test_external_activation_router_runs_formal_search_result_preflight`，用 Agent60 自己的 formal package template 构造最小合规 reviewer-filled package，验证只有 row preflight ready 时 route 才 ready。
- 重新运行 `experiments/run_external_activation_router.py` 和 `experiments/run_agent50_model_core_governance.py`。
- 更新 `deliverables/README.md` 与 `notes/current_status.md`。

当前结果：

- 默认环境未设置 `FORMAL_SEARCH_RESULT_PACKAGE_PATH`，router 仍为：
  - `router_status=external_activation_router_waiting_for_external_paths`
  - `route_ready_count=0`
  - `blocked_route_count=3`
- 测试证明：
  - 空壳 formal JSON 会被 `activation_route_blocked_by_formal_search_result_preflight` 阻断。
  - reviewer-filled 且通过 Agent60 source/row preflight 的 package 才能进入 `activation_route_ready_for_agent60_formal_search_preflight`。

边界：

- R8u-91 不执行 formal search，不生成 prior-art comparison、不输出法律意见、不生成权利要求文本。
- 通过 formal route preflight 也只允许进入 Agent60 formal search validation/nonlegal human review 链，不允许写 field-supported claim、actuator 或 release gate。

验证：

- `.venv/bin/pytest tests/test_external_activation_router.py -q`：6 passed。
- `.venv/bin/pytest tests/test_model_core_optimization_governance_agent.py -q`：34 passed。
- `.venv/bin/python experiments/run_external_activation_router.py`：通过，已刷新 router JSON/report。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：通过，已刷新 Agent50/core gate/manifest。

## 2026-06-21 R8u-92：Router Ready Channel Split

背景：

- R8u-91 已把 formal search route 从“文件存在即可 ready”收紧为 Agent60 formal package preflight。
- 但 router 顶层 `route_ready_count` 仍混合两种不同含义：一种是 R7/R8u-66 通过预检后可恢复 field replay/layout holdout 等模型主链；另一种是 R8u-79 formal search result package 通过预检后只可进入外部/人工非法律检索审查交接。
- 这会让后续治理或人工阅读时把“交接 ready”误读成“现场模型链 ready”。

实现：

- 更新 `src/water_ai/external_activation_router.py`：
  - 顶层新增 `model_chain_ready_route_count`、`handoff_ready_route_count`。
  - 顶层新增 `ready_channel_ids`、`model_chain_ready_channel_ids`、`handoff_ready_channel_ids`、`blocked_channel_ids`。
  - `router_status` 拆成 `external_activation_router_has_model_chain_ready_routes`、`external_activation_router_has_handoff_ready_routes` 和 `external_activation_router_waiting_for_external_paths`。
- 更新 `src/water_ai/agents/model_core_optimization_governance_agent.py`：
  - Agent50 scorecard 和 `external_resume_conditions` 同步消费 model-chain/handoff ready counts 与 channel ids。
  - 旧 router JSON 若没有新字段，仍可通过 route rows 回推兼容。
- 更新 `experiments/run_external_activation_router.py` 与 `experiments/run_agent50_model_core_governance.py`：
  - markdown 报告、console 输出和 manifest latest 指针均暴露新 ready 通道。
- 更新测试：
  - R7 field route ready 与 R8u-66 path endpoint route ready 必须进入 `model_chain_ready`。
  - R8u-79 formal search route ready 必须进入 `handoff_ready`，且 `can_resume_model_chain=False`。
  - Agent50 消费 router 时必须输出两类 ready 计数与 ids。

当前结果：

- 默认环境未提交外部包，router 正确停在：
  - `router_status=external_activation_router_waiting_for_external_paths`
  - `route_ready_count=0`
  - `model_chain_ready_route_count=0`
  - `handoff_ready_route_count=0`
  - `blocked_channel_ids=[R7_REAL_FIELD_PACKAGE, R8U66_PATH_ENDPOINT_LABEL_PACKAGE, R8U79_FORMAL_SEARCH_RESULT_PACKAGE]`
- 语义边界变清楚：formal search 通过预检也只表示可交给非法律检索审查，不代表 field evidence、现场控制、专利法律结论、actuator 或 release gate 可以恢复。

验证：

- `.venv/bin/python -m py_compile src/water_ai/external_activation_router.py src/water_ai/agents/model_core_optimization_governance_agent.py experiments/run_external_activation_router.py experiments/run_agent50_model_core_governance.py tests/test_external_activation_router.py tests/test_model_core_optimization_governance_agent.py`：通过。
- `.venv/bin/pytest tests/test_external_activation_router.py tests/test_model_core_optimization_governance_agent.py -q`：40 passed。
- `.venv/bin/python experiments/run_external_activation_router.py`：通过，已刷新 router JSON/report。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：通过，已刷新 Agent50/core gate/manifest。
- `.venv/bin/pytest -q`：482 passed。
- `.venv/bin/python tools/build_project_codegraph.py`：通过，CodeGraph 刷新为 319 files、3943 nodes、6405 edges。

## 2026-06-21 R8u-93：Core Gate Self-Interrupt Verdict Backfill

背景：

- R8u-89 已让 Agent50 的 `self_interrupt_verdict` 与阶段门对齐。
- R8u-90/R8u-92 已把外部 router 执行态和 ready 通道写入 `core_score_termination_gate.json`。
- 但最新核查发现 `priority_ranking.json` 与 manifest 中有 `self_interrupt_verdict=stage_boundary_wait_for_external_activation`，而 `core_score_termination_gate.json` 顶层该字段仍为 `null`。
- 这会让只读取 core gate 的后续 agent 误以为阶段门只有 `stage_decision`，不知道当前是“阶段边界等待外部激活”，从而增加错误恢复内部 synthetic/template 扩张的风险。

实现：

- 更新 `src/water_ai/agents/model_core_optimization_governance_agent.py`：
  - Agent50 在计算 `self_interrupt_verdict` 后，将 `self_interrupt_verdict`、`self_interrupt_reason` 和 `self_interrupt_mode` 直接写回 `quantified_core_score_gate`。
  - 这样 runner、测试或任何直接调用 Agent50 的代码都会得到同一份 self-interrupt 语义，不依赖外层 JSON 包装。
- 更新 `tests/test_model_core_optimization_governance_agent.py`：
  - 阶段等待态测试现在要求 `quantified_core_score_gate` 本体包含 `stage_boundary_wait_for_external_activation`、外部激活等待 reason 和阶段门控节流 mode。
- 重新运行 `experiments/run_agent50_model_core_governance.py`，刷新 Agent50/core gate/manifest。

当前结果：

- `outputs/model_core_governance/core_score_termination_gate.json` 已直接暴露：
  - `stage_decision=stop_expansion_wait_for_real_field_package_or_new_core_interface`
  - `self_interrupt_verdict=stage_boundary_wait_for_external_activation`
  - `self_interrupt_mode=stage_gate_throttled_hard_gate_with_deferred_backlog`
  - `external_resume_conditions.router_model_chain_ready_route_count=0`
  - `external_resume_conditions.router_handoff_ready_route_count=0`
- 语义边界：当前仍不是继续内部扩张，而是等待真实 field package、path/endpoint package、formal search result package 或新的可测试核心接口。

验证：

- `.venv/bin/python -m py_compile src/water_ai/agents/model_core_optimization_governance_agent.py tests/test_model_core_optimization_governance_agent.py`：通过。
- `.venv/bin/pytest tests/test_model_core_optimization_governance_agent.py -q`：34 passed。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：通过，已刷新 core gate、priority JSON、Agent50 report 与 manifest。
- `.venv/bin/pytest -q`：482 passed。
- `.venv/bin/python tools/build_project_codegraph.py`：通过，CodeGraph 保持 319 files、3943 nodes、6405 edges。

## 2026-06-21 R8u-94：Next Allowed Action Resume Class Boundary

背景：

- R8u-92 已把 router ready 拆成 `model_chain_ready` 与 `handoff_ready`。
- R8u-93 已把 `self_interrupt_verdict` 回填进 core gate。
- 但 `core_score_termination_gate.json` 的 `next_allowed_actions[*].boundary` 仍对三条外部证据包使用同一句泛化描述：`may resume import/replay/review gates only`。
- 这对 R8u-79 formal search result package 不够准确，因为 formal search 通过预检后只应进入非法律检索比对/律师审查交接/披露修订队列，不能恢复 field replay/control。

实现：

- 更新 `src/water_ai/agents/model_core_optimization_governance_agent.py`：
  - 每条外部 action 新增 `activation_route_class`。
  - R7 和 R8u-66 标记为 `model_chain_external_package`，并输出 `model_chain_resume_candidate=True`。
  - R8u-79 标记为 `formal_search_handoff_only`，并输出 `handoff_only=True`、`model_chain_resume_candidate=False`。
  - `NEW_CORE_INTERFACE` 标记为 `new_testable_core_interface` 与 `requires_tested_interface=True`。
  - 新增 channel-specific boundary：
    - R7 只可在 Agent44/42/43/45 通过后恢复 field import/timestamped replay/field evidence review。
    - R8u-66 只可在 path/endpoint preflight 通过后恢复 layout holdout/path-stage validation/endpoint evidence review。
    - R8u-79 明确是 formal-search handoff only，不能恢复 field replay/control。
- 更新 `tests/test_model_core_optimization_governance_agent.py`：
  - 阶段等待态测试检查 R7/R8u-66/formal/new-interface 四类 action 的 route class、handoff flag、model-chain candidate flag 和 boundary 文本。
- 重新运行 `experiments/run_agent50_model_core_governance.py`，刷新 core gate、priority JSON、Agent50 report 与 manifest。

当前结果：

- `outputs/model_core_governance/core_score_termination_gate.json`：
  - `R7_REAL_FIELD_PACKAGE.activation_route_class=model_chain_external_package`
  - `R8U66_PATH_ENDPOINT_LABEL_PACKAGE.activation_route_class=model_chain_external_package`
  - `R8U79_FORMAL_SEARCH_RESULT_PACKAGE.activation_route_class=formal_search_handoff_only`
  - `NEW_CORE_INTERFACE.activation_route_class=new_testable_core_interface`
  - formal search boundary 包含 `cannot resume field replay or control`
- 当前仍没有外部包通过 router：`router_model_chain_ready_route_count=0`、`router_handoff_ready_route_count=0`。

边界：

- R8u-94 只修复 action schema 与语义边界，不导入 field package、不执行 formal search、不生成 field evidence、专利法律结论、actuator policy 或 release gate。

验证：

- `.venv/bin/python -m py_compile src/water_ai/agents/model_core_optimization_governance_agent.py tests/test_model_core_optimization_governance_agent.py`：通过。
- `.venv/bin/pytest tests/test_model_core_optimization_governance_agent.py -q`：34 passed。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：通过，已刷新 Agent50/core gate/manifest。
- `.venv/bin/pytest -q`：482 passed。
- `.venv/bin/python tools/build_project_codegraph.py`：通过，CodeGraph 刷新为 319 files、3945 nodes、6407 edges。

## 2026-06-21 R8u-95：Next Allowed Action Current Resume State

背景：

- R8u-94 已给 `next_allowed_actions` 加上 route class，区分 R7/R8u-66 model-chain external package、R8u-79 formal-search handoff 和 `NEW_CORE_INTERFACE`。
- 但 `model_chain_resume_candidate=True` 是静态能力，`can_resume_model_chain=False` 是当前状态。两者并列时，后续机器消费仍需要自己推断“当前到底能不能恢复主链”。
- `NEW_CORE_INTERFACE` 也没有 router not-applicable 字段，可能被误读为 router 未执行或字段遗漏。

实现：

- 更新 `src/water_ai/agents/model_core_optimization_governance_agent.py`：
  - 每条 action 新增 `current_route_ready`、`current_model_chain_resume_ready`、`current_handoff_ready` 和 `action_resume_state`。
  - R7/R8u-66 等待态输出 `model_chain_blocked_waiting_for_package`。
  - R8u-79 等待态输出 `handoff_blocked_waiting_for_package`。
  - `NEW_CORE_INTERFACE` 输出 `new_interface_required_before_any_resume`。
  - 新接口动作补齐 `router_status=not_applicable_for_new_core_interface`、`router_route_status=not_applicable_for_new_core_interface`、`router_preflight_status=new_interface_needs_tests_or_verification_gate` 和 `router_validation_command=not_applicable_for_new_core_interface`。
- 更新 `tests/test_model_core_optimization_governance_agent.py`：
  - 阶段等待态测试要求四类 action 都输出当前恢复态，且 R7/R8u-66/formal/new-interface 都不能在当前状态恢复模型主链。
- 重新运行 `experiments/run_agent50_model_core_governance.py`，刷新 core gate、priority JSON、Agent50 report 与 manifest。

当前结果：

- `outputs/model_core_governance/core_score_termination_gate.json`：
  - R7：`action_resume_state=model_chain_blocked_waiting_for_package`
  - R8u-66：`action_resume_state=model_chain_blocked_waiting_for_package`
  - R8u-79：`action_resume_state=handoff_blocked_waiting_for_package`
  - NEW_CORE_INTERFACE：`action_resume_state=new_interface_required_before_any_resume`
- 当前 `current_model_chain_resume_ready=False`、`current_handoff_ready=False`，没有任何外部动作可直接恢复 field/control 主链。

边界：

- R8u-95 只增加机器可读当前状态，不提交外部包、不导入 field rows、不执行 formal search、不生成 field evidence、法律结论、actuator policy 或 release gate。

验证：

- `.venv/bin/python -m py_compile src/water_ai/agents/model_core_optimization_governance_agent.py tests/test_model_core_optimization_governance_agent.py`：通过。
- `.venv/bin/pytest tests/test_model_core_optimization_governance_agent.py -q`：34 passed。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：通过，已刷新 Agent50/core gate/manifest。
- `.venv/bin/pytest -q`：482 passed。
- `.venv/bin/python tools/build_project_codegraph.py`：通过，CodeGraph 刷新为 319 files、3946 nodes、6408 edges。

## 2026-06-21 R8u-96：Effective Iteration Basis Gate

背景：

- 当前 `core_score=0.960`、`iteration_delta=0.056`，低于有效分数提升强阈值 `0.10`，但阶段判定为 `stop_expansion_wait_for_real_field_package_or_new_core_interface`。
- 这不是矛盾：系统已经进入阶段边界，继续内部 synthetic/template 扩张应停止，等待真实 field package、formal search result package 或新的可测试核心接口。
- 但 `iteration_validity_status=valid_stage_boundary_external_field_wait` 本身没有解释“有效依据”来自阶段终止，而不是分数增益，后续机器可能把低增益微修复误读为有效模型提升。

实现：

- 更新 `src/water_ai/agents/model_core_optimization_governance_agent.py`：
  - 新增 `effective_iteration_gate`。
  - 输出 `score_delta_pass`、`hard_blocker_resolution_pass`、`stage_boundary_termination_pass`、`low_gain_without_hard_blocker`、`review_band_without_hard_blocker`、`micro_iteration_evidence_complete`、`effective_iteration_pass`、`expansion_stop_required`、`validity_basis` 和解释文本。
  - 将 `stage_boundary_external_wait_not_score_gain` 的解释优先于 baseline，使外部等待态即使没有 previous score 也不会被误标为普通 baseline。
- 更新 `tests/test_model_core_optimization_governance_agent.py`：
  - baseline、低增益停止、硬阻断解除和外部等待终止四类状态均检查 `effective_iteration_gate`。
- 更新 `experiments/run_agent50_model_core_governance.py`：
  - manifest 新增 `latest_agent50_effective_iteration_gate`、`latest_agent50_effective_iteration_pass`、`latest_agent50_effective_iteration_validity_basis`、`latest_agent50_score_delta_pass`、`latest_agent50_stage_boundary_termination_pass` 和 `latest_agent50_micro_iteration_evidence_complete`。
- 重新运行 `experiments/run_agent50_model_core_governance.py`，刷新 core gate、priority JSON、Agent50 report 与 manifest。

当前结果：

- `outputs/model_core_governance/core_score_termination_gate.json`：
  - `iteration_delta=0.056`
  - `effective_iteration_gate.score_delta_pass=False`
  - `effective_iteration_gate.stage_boundary_termination_pass=True`
  - `effective_iteration_gate.effective_iteration_pass=True`
  - `effective_iteration_gate.expansion_stop_required=True`
  - `effective_iteration_gate.validity_basis=stage_boundary_external_wait_not_score_gain`
  - `interpretation=Stage-boundary external wait is a valid termination condition, not a score-gain claim.`
- Manifest 已暴露同一 effective gate，减少后续 agent 只读 manifest 时的解释摩擦。

边界：

- R8u-96 不改变 core score、不恢复主链、不提交外部包、不导入 field rows、不执行 formal search、不生成 field evidence、法律结论、actuator policy 或 release gate。

验证：

- `.venv/bin/python -m py_compile src/water_ai/agents/model_core_optimization_governance_agent.py tests/test_model_core_optimization_governance_agent.py experiments/run_agent50_model_core_governance.py`：通过。
- `.venv/bin/pytest tests/test_model_core_optimization_governance_agent.py -q`：34 passed。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：通过，已刷新 Agent50/core gate/manifest。
- `.venv/bin/pytest -q`：482 passed。
- `.venv/bin/python tools/build_project_codegraph.py`：通过，CodeGraph 刷新为 319 files、3947 nodes、6409 edges。

## 2026-06-21 R8u-97：Field Activation Matrix Interface

背景：

- R8u-96 后系统已经进入 `stop_expansion_wait_for_real_field_package_or_new_core_interface`，继续堆内部 synthetic/template 产物边际价值低。
- 当前三条外部通道仍未提交真实包：R7 real field package、R8u-66 path/endpoint label package、R8u-79 formal search result package 都不能恢复模型主链。
- 但 `NEW_CORE_INTERFACE` 仍只是泛化动作，缺少一个具体、可测试、能减少现场采集摩擦的接口。

实现：

- 新增 `src/water_ai/field_activation_matrix.py`：
  - 输入 Agent50 `core_score_termination_gate.json` 中的 `hidden_state_coverage_ledger` 和 `external_resume_conditions`。
  - 输出 6 个隐藏状态到外部证据通道、真实字段、可恢复 gate、证据边界和 no-write 边界的矩阵。
  - `catalyst_activity` 显式绑定 N3 催化床 `UV254_abs`、`ORP_mV`、`pressure_drop_kPa`、`offline_lab_results.catalyst_activity`、`campaign_operation_log.regeneration_event` 和 HRT/床层几何。
- 新增 `experiments/run_field_activation_matrix.py`：
  - 生成 `outputs/model_core_governance/field_activation_matrix.json`。
  - 生成 `deliverables/model_core_optimization/field_activation_matrix.md`。
  - 回写 manifest 的 `latest_field_activation_matrix_*` 字段。
- 更新 `ModelCoreOptimizationGovernanceAgent`：
  - 新增可选输入 `field_activation_matrix_metrics`。
  - Agent50 scorecard、`next_allowed_actions.NEW_CORE_INTERFACE` 与 `external_resume_conditions.new_core_interface` 消费该接口。
  - 当矩阵存在时，`NEW_CORE_INTERFACE.action_resume_state` 从 `new_interface_required_before_any_resume` 变为 `new_core_interface_defined_waiting_for_external_evidence`。
- 更新 `experiments/run_agent50_model_core_governance.py`：
  - 读取 `outputs/model_core_governance/field_activation_matrix.json`。
  - manifest 新增 `latest_agent50_new_core_interface*` 字段。
  - 修正 `current_work_item.previous_core_score` 和 `previous_module_stage_status` 的读取：使用上一轮 `latest_agent50_core_score` 与 `latest_agent50_module_stage_status`，不再反复使用历史 `0.904` 与旧 module blocker。
- 新增 `tests/test_field_activation_matrix.py`，并扩展 Agent50 治理测试。

当前结果：

- `outputs/model_core_governance/field_activation_matrix.json`：
  - `interface_status=field_activation_matrix_ready_for_state_level_external_collection`
  - `hidden_state_row_count=6`
  - `hidden_state_row_coverage=1.0`
  - `activation_ready_state_count=0`
  - `field_validated_state_count=0`
  - `control_ready_state_count=0`
  - `can_resume_model_chain=False`
  - `can_write_to_actuator=False`
  - `can_write_to_release_gate=False`
  - `evidence_boundary_completeness=1.0`
  - `no_write_boundary_completeness=1.0`
- `outputs/model_core_governance/core_score_termination_gate.json`：
  - `previous_core_score=0.960`
  - `core_score=0.960`
  - `iteration_delta=0.000`
  - `previous_module_stage_status=module_stage_complete`
  - `module_stage_blocker_resolved=False`
  - `hard_blocker_resolved=False`
  - `effective_iteration_gate.stage_boundary_termination_pass=True`
  - `effective_iteration_gate.validity_basis=stage_boundary_external_wait_not_score_gain`
  - `external_resume_conditions.new_core_interface.interface_id=R8u97_field_activation_matrix_interface`

边界：

- R8u-97 定义的是状态级外部证据激活接口，不提交真实 field package、不执行 formal search、不生成 field evidence、不写 actuator policy、不写 release gate、不写法律结论或 field-supported claim。
- 该轮 `core_score` 没有提升，且不应被解释为专利/论文实证成熟；它的价值是让下一次真实数据采集、path/endpoint 补证和催化剂活性补证路径更具体、更可复查。

验证：

- `.venv/bin/python -m py_compile src/water_ai/field_activation_matrix.py src/water_ai/agents/model_core_optimization_governance_agent.py experiments/run_field_activation_matrix.py experiments/run_agent50_model_core_governance.py tests/test_field_activation_matrix.py tests/test_model_core_optimization_governance_agent.py`：通过。
- `.venv/bin/pytest tests/test_field_activation_matrix.py tests/test_model_core_optimization_governance_agent.py -q`：38 passed。
- `.venv/bin/python experiments/run_field_activation_matrix.py`：通过，已生成 field activation matrix。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：通过，Agent50 已消费新接口并刷新 core gate/manifest。
- `.venv/bin/pytest tests/test_field_activation_matrix.py tests/test_model_core_optimization_governance_agent.py tests/test_external_activation_router.py -q`：44 passed。
- `.venv/bin/pytest -q`：486 passed。
- `.venv/bin/python tools/build_project_codegraph.py`：通过，CodeGraph 刷新为 323 files、3992 nodes、6469 edges。

## 2026-06-21 R8u-98：Field Activation Evidence Response Preflight

背景：

- R8u-97 已把 6 个隐藏状态映射到外部证据通道和真实字段，但还只是“告诉现场要采什么”。
- 为了让下一次真实数据采集更可执行，需要把矩阵展开成可填写、可预检的响应包，避免现场或后续 agent 把文档说明误当作 field evidence。

实现：

- 更新 `src/water_ai/field_activation_matrix.py`：
  - 新增 `build_field_activation_response_template(matrix)`。
  - 新增 `preflight_field_activation_response(response, matrix)`。
  - 响应模板按“隐藏状态-证据字段”展开，每行要求 `data_origin=field`、`batch_id`、时间/节点/传感器或离线方法引用、chain-of-custody、operator 和 `no_write_boundary_confirmed=true`。
  - 预检检查缺失行、额外行、TODO/template marker、非 field origin、非法通道、缺少 batch/evidence reference、no-write 未确认等。
- 更新 `experiments/run_field_activation_matrix.py`：
  - 生成 `outputs/model_core_governance/field_activation_response_template.json`。
  - 生成 `outputs/model_core_governance/field_activation_response_preflight.json`。
  - 将 response preflight 状态嵌入 `field_activation_matrix.json`。
  - 回写 manifest 的 `latest_field_activation_response_*` 字段。
- 更新 `ModelCoreOptimizationGovernanceAgent`：
  - Agent50 scorecard、`next_allowed_actions.NEW_CORE_INTERFACE` 与 `external_resume_conditions.new_core_interface` 消费 response preflight 状态。
  - core gate 现在能直接显示模板仍阻断，不能进入 external activation router。
- 更新 `tests/test_field_activation_matrix.py` 与 `tests/test_model_core_optimization_governance_agent.py`。

当前结果：

- `outputs/model_core_governance/field_activation_response_template.json`：
  - `template_id=R8u98_field_activation_evidence_response_template`
  - `required_response_row_count=33`
  - 每行仍含 `TODO_*` 字段，等待真实 field 证据填写。
- `outputs/model_core_governance/field_activation_response_preflight.json`：
  - `preflight_status=field_activation_response_blocked_before_external_package_preflight`
  - `expected_response_row_count=33`
  - `provided_response_row_count=33`
  - `template_marker_row_count=33`
  - `non_field_row_count=33`
  - `missing_alignment_row_count=33`
  - `no_write_unconfirmed_row_count=33`
  - `can_route_to_external_activation_router=False`
  - `can_resume_model_chain=False`
  - `can_write_to_actuator=False`
  - `can_write_to_release_gate=False`
- `outputs/model_core_governance/core_score_termination_gate.json`：
  - `external_resume_conditions.new_core_interface.response_preflight_status=field_activation_response_blocked_before_external_package_preflight`
  - `external_resume_conditions.new_core_interface.response_can_route_to_external_activation_router=False`

边界：

- R8u-98 只是把状态级补证变成可填写/可预检接口，不导入真实 field rows、不执行 replay/holdout、不恢复模型主链、不写 actuator/release gate、不生成法律结论或 field-supported claim。
- 当前阻断是正确状态：模板中的 TODO 不能被视为 field evidence。

验证：

- `.venv/bin/python -m py_compile src/water_ai/field_activation_matrix.py experiments/run_field_activation_matrix.py tests/test_field_activation_matrix.py src/water_ai/agents/model_core_optimization_governance_agent.py`：通过。
- `.venv/bin/pytest tests/test_field_activation_matrix.py -q`：5 passed。
- `.venv/bin/pytest tests/test_field_activation_matrix.py tests/test_model_core_optimization_governance_agent.py -q`：40 passed。
- `.venv/bin/python experiments/run_field_activation_matrix.py`：通过，已生成矩阵、响应模板和响应预检。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：通过，Agent50 已消费 response preflight 状态。
- `.venv/bin/pytest tests/test_field_activation_matrix.py tests/test_model_core_optimization_governance_agent.py tests/test_external_activation_router.py -q`：46 passed。
- `.venv/bin/pytest -q`：488 passed。
- `.venv/bin/python tools/build_project_codegraph.py`：通过，CodeGraph 刷新为 323 files、4012 nodes、6496 edges。

## 2026-06-21 R8u-99：Field Activation Package Assembly Plan

背景：

- R8u-98 已把隐藏状态证据展开成 33 行 response template/preflight，但还没有说明这些响应行应如何进入 R7 real field package 或 R8u-66 path/endpoint package 的表结构。
- 若只依赖人工读模板，后续容易漏掉 path/endpoint 通道，或者把 response template 当成真实 package。

实现：

- 更新 `src/water_ai/field_activation_matrix.py`：
  - 新增 `build_field_activation_package_assembly_plan(response, matrix, response_preflight, external_activation_contract)`。
  - 将响应行按 `evidence_channel -> table_name -> field_names` 分组，生成 no-write package assembly plan。
  - 增加 `candidate_channel_plans`：即使当前 response 默认通道只落在 R7，也会基于矩阵 required channels 同时列出 R7 与 R8u-66 候选组装路径。
- 更新 `experiments/run_field_activation_matrix.py`：
  - 读取 `outputs/model_core_governance/external_activation_contract.json`。
  - 生成 `outputs/model_core_governance/field_activation_package_assembly_plan.json`。
  - 回写 manifest 的 `latest_field_activation_package_assembly_*` 字段。
- 更新 `ModelCoreOptimizationGovernanceAgent`：
  - Agent50 scorecard 与 `external_resume_conditions.new_core_interface` 消费 assembly plan 状态、候选通道数量和 stage 能力。
- 更新 `tests/test_field_activation_matrix.py` 与 `tests/test_model_core_optimization_governance_agent.py`。

当前结果：

- `outputs/model_core_governance/field_activation_package_assembly_plan.json`：
  - `assembly_status=field_activation_package_assembly_plan_blocked_by_response_preflight`
  - `channel_plan_count=1`
  - `candidate_channel_plan_count=2`
  - `candidate_table_plan_count=21`
  - `candidate_channel_plans=[R7_REAL_FIELD_PACKAGE, R8U66_PATH_ENDPOINT_LABEL_PACKAGE]`
  - `can_stage_external_package_candidates=False`
  - `can_route_to_external_activation_router=False`
  - `can_resume_model_chain=False`
  - `can_write_to_actuator=False`
  - `can_write_to_release_gate=False`
- `outputs/model_core_governance/core_score_termination_gate.json`：
  - `external_resume_conditions.new_core_interface.package_assembly_status=field_activation_package_assembly_plan_blocked_by_response_preflight`
  - `external_resume_conditions.new_core_interface.package_assembly_candidate_channel_plan_count=2`

边界：

- R8u-99 只生成组装计划，不写 CSV、不创建真实 package、不执行 router/replay/holdout、不恢复模型主链、不写 actuator/release gate、不生成 field-supported claim。
- 当前阻断是正确状态：R8u-98 response preflight 未通过前，assembly plan 不能 stage external package candidates。

验证：

- `.venv/bin/python -m py_compile src/water_ai/field_activation_matrix.py src/water_ai/agents/model_core_optimization_governance_agent.py experiments/run_field_activation_matrix.py tests/test_field_activation_matrix.py tests/test_model_core_optimization_governance_agent.py`：通过。
- `.venv/bin/pytest tests/test_field_activation_matrix.py tests/test_model_core_optimization_governance_agent.py -q`：40 passed。
- `.venv/bin/python experiments/run_field_activation_matrix.py`：通过，已生成 package assembly plan。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：通过，Agent50 已消费 assembly plan。
- `.venv/bin/pytest tests/test_field_activation_matrix.py tests/test_model_core_optimization_governance_agent.py tests/test_external_activation_router.py -q`：46 passed。
- `.venv/bin/pytest -q`：488 passed。
- `.venv/bin/python tools/build_project_codegraph.py`：通过，CodeGraph 刷新为 323 files、4029 nodes、6517 edges。

## 2026-06-22 R8u164：External Package Operator Missing Table Projection and Governance Adapter

背景：

- R8u160-R8u163 已经把 grey-box submission readiness gate、core interface 和 manifest 接到同一份缺表合同：默认未提交 `GREY_BOX_CALIBRATION_PACKAGE_DIR` 时，最高缺口是 `missing_external_package / all_required_tables / 5 tables`。
- 但面向 operator 的 `external_package_readiness_board.json` 和 `external_package_operator_action_packet.json` 仍主要暴露模板目录、env var 与 validation command，没有直接列出五张缺失表。
- 用户补充了桌面 `复杂项目启动前置治理协议_v3_核心版.md`，要求借鉴其前置治理思想优化工程模型；本轮判断应吸收低摩擦治理规则，而不是复制十阶段协议或新增治理 agent。

实现：

- 使用子代理并行只读审计：
  - 代码链路审计确认 `_package_row()`、`_operator_action()` 和 runner 未透传 `missing_table_count/missing_tables`。
  - 测试合同审计建议在 `tests/test_external_package_readiness_board.py` 中用 `candidate_id` 查找行，避免绑定排序下标。
  - 边际价值审计判断 R8u164 是当前同等规模内最高价值的小闭环：把 R8u163 的缺表合同投影到 operator-facing 包。
  - 治理协议映射审计建议只吸收 current_basis/not_current_basis、紧凑路由、人看/机器看分层、manual_action_required、子代理边界和 anti-bloat gate。
- 更新 `src/water_ai/external_package_readiness_board.py`：
  - 新增 `attach_submission_readiness_gap()`，从 `grey_box_submission_readiness_gate.highest_priority_gap` 提取 gap type、缺表数量、缺表清单和 source env var。
  - `_package_row()` 和 `_operator_action()` 透传可选 submission gap 字段。
  - operator packet 顶层新增 `next_operator_template_dir`、`next_operator_submission_gap_type`、`next_operator_missing_table_count`、`next_operator_missing_tables`。
  - Markdown report 增加缺表数量展示。
- 更新 `experiments/run_external_package_readiness_board.py` 与 `experiments/run_agent50_model_core_governance.py`：
  - 从 `outputs/grey_box_calibration_package/grey_box_submission_readiness_gate.json` 或 Agent50 已读 gate 自动附着 grey-box 缺表合同。
  - manifest 新增 operator packet 顶层缺表摘要字段。
- 更新测试：
  - `test_external_package_operator_action_packet_surfaces_grey_box_missing_tables`
  - `test_attach_submission_readiness_gap_copies_missing_table_contract`
  - `test_manifest_exposes_core_interface_grey_box_submission_readiness_summary` 增加 operator packet manifest 摘要断言。
- 新增 `deliverables/model_core_optimization/engineering_model_governance_adapter.md`：
  - 只吸收低摩擦工程治理规则，明确不照搬十阶段协议、不新增治理 agent、不让治理 Markdown 成为第二事实源。

当前结果：

- `outputs/model_core_governance/external_package_readiness_board.json` 的 `NCI1_GREY_BOX_CALIBRATION_PACKAGE` 行现在包含：
  - `submission_gap_type=missing_external_package`
  - `submission_highest_priority_gap_table=all_required_tables`
  - `missing_table_count=5`
  - `missing_tables=[batch_inlet_outlet_lab, hydraulic_rtd_or_tracer, oxidant_dose_residual_log, catalyst_age_regeneration_log, byproduct_panel]`
  - `submission_source_env_var=GREY_BOX_CALIBRATION_PACKAGE_DIR`
- `outputs/model_core_governance/external_package_operator_action_packet.json` 顶层现在包含：
  - `next_operator_submission_gap_type=missing_external_package`
  - `next_operator_missing_table_count=5`
  - `next_operator_missing_tables=[batch_inlet_outlet_lab, hydraulic_rtd_or_tracer, oxidant_dose_residual_log, catalyst_age_regeneration_log, byproduct_panel]`
  - `next_operator_template_dir=outputs/grey_box_calibration_package/grey_box_calibration_package_template`
  - `next_operator_validation_command=.venv/bin/python experiments/run_grey_box_calibration_package_preflight.py`
- `deliverables/manifest.json` 已更新：
  - `latest_regression=629 passed`
  - `latest_codegraph_fallback=405 files / 5323 nodes / 8448 edges`
  - `latest_engineering_model_governance_adapter=deliverables/model_core_optimization/engineering_model_governance_adapter.md`

边界：

- R8u164 只降低外部真实包提交的 scan 摩擦，并增强状态恢复能力。
- 不改变 `readiness_score=0.143`。
- 不生成 field evidence，不运行 downstream replay/holdout/calibration。
- 不恢复模型链，不写 actuator，不写 release gate。
- 不把桌面治理协议复制为新事实源；事实仍以代码、manifest、gate JSON、真实包和测试为准。

验证：

- `.venv/bin/python -m py_compile src/water_ai/external_package_readiness_board.py experiments/run_external_package_readiness_board.py experiments/run_agent50_model_core_governance.py`：通过。
- `.venv/bin/pytest -q tests/test_external_package_readiness_board.py`：11 passed。
- `.venv/bin/pytest -q tests/test_external_package_readiness_board.py tests/test_agent50_core_interface_integration.py tests/test_grey_box_calibration_package.py tests/test_core_interface_consolidation.py tests/test_model_core_optimization_governance_agent.py tests/test_deliverable_organization_agent.py`：102 passed。
- `.venv/bin/python experiments/run_external_package_readiness_board.py`：通过，已刷新 readiness board、operator packet 和 acquisition gate。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：通过，已刷新 Agent50 payload、manifest、core interface 与 external package artifacts。
- `.venv/bin/pytest -q`：629 passed。
- `.venv/bin/python tools/build_project_codegraph.py`：通过，CodeGraph fallback 刷新为 405 files、5323 nodes、8448 edges。

## 2026-06-22 R8u165：External Package Operator Machine Handoff Semantics

背景：

- R8u164 已把 grey-box 五张缺表合同投影到 external package readiness board、operator action packet 和 manifest。
- 但 operator packet 仍缺机器看版式的治理语义：只能看出下一步 env var、模板和 validation command，不能直接看出 route event、当前依据、非依据、人工动作、证据等级以及该 packet 能证明/不能证明什么。
- 这会让后续 agent 需要重新推断“当前只是 external activation wait，不是 field evidence，也不能恢复模型链”。

实现：

- 按 TDD 新增 `test_external_package_operator_action_packet_exposes_machine_handoff_semantics`，先确认 `route_event` 缺失导致失败。
- 更新 `src/water_ai/external_package_readiness_board.py`：
  - operator packet 顶层新增 `route_event`、`route_reason`、`evidence_level`。
  - 新增 `current_basis_refs` 与 `not_current_basis_refs`。
  - 新增 `manual_action_required`，指出当前需要 field operator/user 填写真实外部包、设置 env var 并运行 validation command。
  - 新增 `can_prove` 与 `cannot_prove`，显式区分“可证明下一步采集动作”与“不能证明 field performance / mechanism validity / model-chain resume / actuator or release-gate readiness”。
  - Markdown report 同步显示 route、evidence 和 manual action 字段。
- 更新 `experiments/run_external_package_readiness_board.py` 与 `experiments/run_agent50_model_core_governance.py`：
  - manifest 新增 `latest_external_package_operator_action_packet_route_event`、`route_reason`、`evidence_level`、`manual_action_required`、`current_basis_refs`、`not_current_basis_refs`。
- 更新 `tests/test_agent50_core_interface_integration.py`，锁定 manifest 的 operator packet 机器 handoff 字段。

当前结果：

- `outputs/model_core_governance/external_package_operator_action_packet.json` 现在显示：
  - `route_event=external_activation_wait`
  - `route_reason=waiting_for_real_external_package_before_downstream_replay_holdout_calibration`
  - `evidence_level=operator_handoff_only_not_field_evidence`
  - `manual_action_required.required=True`
  - `current_basis_refs=[source_board_id:R8u154_external_package_readiness_board, readiness_board.package_rows, readiness_board.package_summary, readiness_board.boundary, operator_actions.validation_command]`
  - `not_current_basis_refs=[template_rows, synthetic_rows, sample_rows, literature_only_rows, downstream_replay_holdout_calibration_not_run]`
- `deliverables/manifest.json` 已同步写入同组字段，后续只读 manifest 也能恢复当前 route 和证据边界。

边界：

- R8u165 只增强验证治理层和外部执行交接的状态恢复能力。
- 不改变 `readiness_score=0.143`。
- 不生成 field evidence，不运行 downstream replay/holdout/calibration。
- 不恢复模型链，不写 actuator，不写 release gate。

验证：

- `.venv/bin/python -m py_compile src/water_ai/external_package_readiness_board.py experiments/run_external_package_readiness_board.py experiments/run_agent50_model_core_governance.py`：通过。
- `.venv/bin/pytest -q tests/test_external_package_readiness_board.py::test_external_package_operator_action_packet_exposes_machine_handoff_semantics`：通过。
- `.venv/bin/pytest -q tests/test_external_package_readiness_board.py tests/test_agent50_core_interface_integration.py tests/test_grey_box_calibration_package.py tests/test_core_interface_consolidation.py tests/test_model_core_optimization_governance_agent.py tests/test_deliverable_organization_agent.py`：103 passed。
- `.venv/bin/python experiments/run_external_package_readiness_board.py`：通过，已刷新 readiness board、operator packet 和 acquisition gate。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：通过，已刷新 Agent50 payload、manifest、core interface 与 external package artifacts。
- `.venv/bin/pytest -q`：630 passed。
- `.venv/bin/python tools/build_project_codegraph.py`：通过，CodeGraph fallback 刷新为 405 files、5329 nodes、8454 edges。

## 2026-06-22 R8u166：External Package Acquisition Goal Termination Metrics

背景：

- R8u165 已把 operator packet 做成机器可恢复 handoff，能说明当前处于 `external_activation_wait`，需要提交真实外部包。
- 但 acquisition maturity gate 仍主要输出成熟度分数、包数量和 no-write 状态，尚未显式对齐当前 goal 中的模块终止阈值。
- 这会让后续 agent 仍需人工推断：接口合同是否完整、状态变量是否足够、证据/失败/no-write 边界是否完整、为什么不能终止。

实现：

- 按 TDD 新增 `test_external_package_acquisition_maturity_gate_exposes_goal_termination_metrics`，先确认 `termination_thresholds` 缺失导致失败。
- 更新 `src/water_ai/external_package_readiness_board.py`：
  - 新增 `ACQUISITION_TERMINATION_THRESHOLDS`。
  - acquisition gate 顶层新增 `input_contract_completeness`、`output_contract_completeness`、`handoff_state_variable_coverage`、`downstream_reconnection_rate`、`evidence_boundary_completeness`、`failure_boundary_completeness`、`no_write_boundary_completeness`。
  - 新增 `contract_termination_status`、`module_stage_termination_pass`、`termination_blockers` 和 `termination_boundary_note`。
  - `handoff_state_variable_coverage` 明确只评价外部包/operator lifecycle 状态字段，不代表真实污染过程隐藏状态已经现场验证。
- 更新 `experiments/run_external_package_readiness_board.py` 与 `experiments/run_agent50_model_core_governance.py`：
  - manifest 新增 `latest_external_package_acquisition_*` 与 `latest_agent50_external_package_acquisition_*` 终止指标字段。
- 更新 `tests/test_agent50_core_interface_integration.py`，锁定 manifest 必须暴露同一套终止状态和 blockers。

当前结果：

- `outputs/model_core_governance/external_package_acquisition_maturity_gate.json` 现在显示：
  - `input_contract_completeness=1.0`
  - `output_contract_completeness=1.0`
  - `handoff_state_variable_coverage=1.0`
  - `downstream_reconnection_rate=0.0`
  - `evidence_boundary_completeness=1.0`
  - `failure_boundary_completeness=1.0`
  - `no_write_boundary_completeness=1.0`
  - `contract_termination_status=external_package_contracts_complete_but_waiting_for_field_packages`
  - `module_stage_termination_pass=False`
  - `termination_blockers=[downstream_reconnection_rate_below_0.80, field_package_ready_rate_below_1.00]`
- `deliverables/manifest.json` 已同步写入同组字段，后续只读 manifest 也能判断当前 acquisition gate 不能通过阶段终止。

边界：

- R8u166 只增强验证治理层的可计算终止判断。
- 不改变 `field_package_ready_rate=0.0`。
- 不生成 field evidence，不运行 downstream replay/holdout/calibration。
- 不恢复模型链，不写 actuator，不写 release gate。

验证：

- `.venv/bin/python -m py_compile src/water_ai/external_package_readiness_board.py experiments/run_external_package_readiness_board.py experiments/run_agent50_model_core_governance.py`：通过。
- `.venv/bin/pytest -q tests/test_external_package_readiness_board.py::test_external_package_acquisition_maturity_gate_exposes_goal_termination_metrics`：通过。
- `.venv/bin/pytest -q tests/test_agent50_core_interface_integration.py::test_manifest_exposes_core_interface_grey_box_submission_readiness_summary`：通过。
- `.venv/bin/pytest -q tests/test_external_package_readiness_board.py tests/test_agent50_core_interface_integration.py tests/test_grey_box_calibration_package.py tests/test_core_interface_consolidation.py tests/test_model_core_optimization_governance_agent.py tests/test_deliverable_organization_agent.py`：104 passed。
- `.venv/bin/python experiments/run_external_package_readiness_board.py`：通过，已刷新 readiness board、operator packet 和 acquisition gate。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：通过，已刷新 Agent50 payload、manifest、core interface 与 external package artifacts。
- `.venv/bin/pytest -q`：631 passed。
- `.venv/bin/python tools/build_project_codegraph.py`：通过，CodeGraph fallback 刷新为 405 files、5337 nodes、8462 edges。

## 2026-06-22 R8u167：Core Gate Consumes External Package Acquisition Termination

背景：

- R8u166 已让 `external_package_acquisition_maturity_gate.json` 与 manifest 显式输出 goal-aligned 终止指标。
- 但 `core_score_termination_gate.json` 与 `priority_ranking.json` 仍没有 acquisition termination snapshot。
- 这意味着后续只读主治理入口的 agent 仍会看不到 `contract_termination_status`、`module_stage_termination_pass` 和 `termination_blockers`，需要回扫深层 acquisition gate。

实现：

- 按 TDD 新增 `test_core_gate_exposes_external_package_acquisition_termination_snapshot`，先确认 `core_score_termination_gate.json` 缺少 `external_package_acquisition_stage_gate` 导致失败。
- 更新 `experiments/run_agent50_model_core_governance.py`：
  - 新增 `_external_package_acquisition_stage_gate_snapshot()`，从 acquisition gate 提取精简终止快照。
  - 新增 `_attach_external_package_acquisition_stage_gate()`，把快照写回 `report.metrics`、`quantified_core_score_gate`、`external_resume_conditions.external_package_acquisition_stage_gate` 和 `external_resume_conditions.new_core_interface.external_package_acquisition_*`。
  - `priority_ranking.json` 顶层新增 `external_package_acquisition_stage_gate`。
  - Agent50 Markdown 报告新增 acquisition termination status、module pass 和 blockers。

当前结果：

- `outputs/model_core_governance/core_score_termination_gate.json` 现在显示：
  - `external_package_acquisition_stage_gate.contract_termination_status=external_package_contracts_complete_but_waiting_for_field_packages`
  - `module_stage_termination_pass=False`
  - `downstream_reconnection_rate=0.0`
  - `field_package_ready_rate=0.0`
  - `termination_blockers=[downstream_reconnection_rate_below_0.80, field_package_ready_rate_below_1.00]`
- `outputs/model_core_governance/priority_ranking.json` 顶层也暴露同一 snapshot。
- `external_resume_conditions.new_core_interface` 现在带有 `external_package_acquisition_*` 字段，后续只读 core gate 即可判断 NEW_CORE_INTERFACE 当前仍是外部真实包等待态。

边界：

- R8u167 是主治理入口回接补丁。
- 不改变 `core_score`。
- 不生成 field evidence，不运行 downstream replay/holdout/calibration。
- 不恢复模型链，不写 actuator，不写 release gate。

验证：

- `.venv/bin/python -m py_compile experiments/run_agent50_model_core_governance.py`：通过。
- `.venv/bin/pytest -q tests/test_agent50_core_interface_integration.py::test_core_gate_exposes_external_package_acquisition_termination_snapshot`：通过。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：通过，已刷新 Agent50 payload、core gate、priority ranking、manifest 与 external package artifacts。
- `.venv/bin/pytest -q tests/test_external_package_readiness_board.py tests/test_agent50_core_interface_integration.py tests/test_grey_box_calibration_package.py tests/test_core_interface_consolidation.py tests/test_model_core_optimization_governance_agent.py tests/test_deliverable_organization_agent.py`：105 passed。
- `.venv/bin/pytest -q`：632 passed。
- `.venv/bin/python tools/build_project_codegraph.py`：通过，CodeGraph fallback 刷新为 405 files、5340 nodes、8465 edges。

## 2026-06-22 R8u168：Stage Board Surfaces External Package Acquisition Termination

背景：

- 用户要求借鉴桌面 `复杂项目启动前置治理协议_v3_核心版.md` 来优化工程模型。
- 协议中对本项目最有价值的原则是：机器看版 handoff 要能独立恢复状态，next_route 不能漂移，阶段门不能只藏在深层 artifact，current_basis/not_current_basis 与 no-write 边界必须在最高操作入口可见。
- R8u167 已把 external package acquisition termination snapshot 回接到 `core_score_termination_gate.json` 与 `priority_ranking.json`。
- 但 `stage_boundary_external_action_board.json`、对应 Markdown 和 manifest 仍缺 `contract_termination_status/module_stage_termination_pass/termination_blockers`，导致操作者或后续 agent 只读 action board 时，仍可能看不到 NEW_CORE_INTERFACE 当前为什么不能结束 acquisition 阶段。

实现：

- 按 TDD 新增 `test_stage_boundary_action_board_surfaces_new_core_acquisition_termination_snapshot`，先确认 `action_summary` 缺 `new_core_interface_acquisition_contract_termination_status` 导致失败。
- 更新 `src/water_ai/stage_boundary_external_action_board.py`：
  - 将 `core_gate.external_package_acquisition_stage_gate` 传入 action rows。
  - 新增 `_new_core_acquisition_context()`，把 acquisition termination snapshot 投影到 `NEW_CORE_INTERFACE` row。
  - 新增 `_new_core_acquisition_summary()`，把同一 snapshot 提升到 `action_summary`。
  - `operator_runbook` 现在也保留 acquisition termination status、pass、rates、blockers 和 next-stage fields。
  - Markdown 报告的 Board State 与 New Core Interface Candidate 区域显示 acquisition termination status、stage pass 和 blockers。
- 新增 manifest 层测试 `test_manifest_exposes_stage_boundary_acquisition_termination_snapshot`，先确认顶层 manifest 缺恢复字段。
- 更新 `experiments/run_stage_boundary_external_action_board.py` 与 `experiments/run_agent50_model_core_governance.py`：
  - 通用 `latest_stage_boundary_external_action_board_*` 写入 acquisition termination 字段。
  - Agent50 `latest_agent50_stage_boundary_external_action_board_*` 同步写入同组字段。

当前结果：

- `outputs/model_core_governance/stage_boundary_external_action_board.json` 的 `action_summary`、`NEW_CORE_INTERFACE` row 和 `operator_runbook` 均显示：
  - `new_core_interface_acquisition_contract_termination_status=external_package_contracts_complete_but_waiting_for_field_packages`
  - `new_core_interface_acquisition_module_stage_termination_pass=False`
  - `new_core_interface_acquisition_downstream_reconnection_rate=0.0`
  - `new_core_interface_acquisition_field_package_ready_rate=0.0`
  - `new_core_interface_acquisition_termination_blockers=[downstream_reconnection_rate_below_0.80, field_package_ready_rate_below_1.00]`
- `deliverables/model_core_optimization/stage_boundary_external_action_board.md` 已显示同组字段。
- `deliverables/manifest.json` 已同步通用和 Agent50 两组 stage-boundary acquisition fields。
- 这轮把桌面协议中的“机器看版可继承”原则落成了模型的最高操作入口字段，而不是新增冗余治理文档。

边界：

- R8u168 是 stage-boundary action board 的恢复链与阶段门可见性修复。
- 不改变 `core_score`。
- 不生成 field evidence，不运行 downstream replay/holdout/calibration。
- 不恢复模型链，不写 actuator，不写 release gate。

验证：

- `.venv/bin/python -m py_compile src/water_ai/stage_boundary_external_action_board.py experiments/run_stage_boundary_external_action_board.py experiments/run_agent50_model_core_governance.py`：通过。
- `.venv/bin/pytest -q tests/test_stage_boundary_external_action_board.py`：7 passed。
- `.venv/bin/python experiments/run_stage_boundary_external_action_board.py`：通过，已刷新 action board JSON/Markdown/manifest。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：通过，已刷新 Agent50 payload、stage board、manifest 与 external package artifacts。
- `.venv/bin/pytest -q tests/test_stage_boundary_external_action_board.py tests/test_agent50_core_interface_integration.py tests/test_external_package_readiness_board.py tests/test_model_core_optimization_governance_agent.py tests/test_deliverable_organization_agent.py`：95 passed。
- `.venv/bin/pytest -q`：634 passed。
- `.venv/bin/python tools/build_project_codegraph.py`：通过，CodeGraph fallback 刷新为 405 files、5345 nodes、8470 edges。

## 2026-06-22 R8u169：Stage Boundary Machine Handoff Contract

背景：

- R8u168 已经把 external package acquisition 的终止快照回接到 `stage_boundary_external_action_board`。
- 但 action board 仍主要是“行动列表”，缺少可直接继承的机器看版字段：
  - 当前 route_event 是什么。
  - 下一步 route 是什么。
  - 哪些材料是 current basis。
  - 哪些材料不能作为 current basis。
  - 是否需要人工/现场包动作。
  - 当前能证明什么、不能证明什么。
- 这会让后续 agent 只读 action board 或 manifest 时仍需要回扫 core gate、operator packet、focused merge 和 acquisition gate 才能恢复阶段语义。

实现：

- 按 TDD 新增 `test_stage_boundary_action_board_exposes_machine_handoff_for_low_friction_resume`，先确认 `machine_handoff` 缺失导致失败。
- 更新 `src/water_ai/stage_boundary_external_action_board.py`：
  - 新增 `_machine_handoff()`。
  - 新增 `_machine_route_event()`、`_machine_route_reason()`、`_machine_next_route()`。
  - board 顶层新增 `machine_handoff`。
  - Markdown 报告新增 `## Machine Handoff` 区域。
- 新增 `test_manifest_exposes_stage_boundary_machine_handoff_summary`，锁定 manifest 必须暴露 handoff 摘要。
- 更新 `experiments/run_stage_boundary_external_action_board.py` 与 `experiments/run_agent50_model_core_governance.py`：
  - 通用 `latest_stage_boundary_external_action_board_machine_handoff_*` 写入 route、source env var、manual action、basis refs、can/cannot prove。
  - Agent50 `latest_agent50_stage_boundary_external_action_board_machine_handoff_*` 同步写入同组字段。

当前结果：

- `outputs/model_core_governance/stage_boundary_external_action_board.json` 现在包含：
  - `machine_handoff.handoff_id=R8u169_stage_boundary_external_action_machine_handoff`
  - `current_stage=stage_boundary_external_activation`
  - `route_event=external_activation_wait`
  - `next_route=submit_real_external_input_then_rerun_stage_preflight_and_agent50`
  - `next_route_source_env_var=FOCUSED_CATALYST_RESPONSE_PATH`
  - `next_route_validation_command=experiments/run_focused_catalyst_response_merge.py`
  - `manual_action_required.required=True`
  - `current_basis_refs=[core_gate.stage_decision, core_gate.next_allowed_actions, external_activation_operator_action_packet, focused_catalyst_response_merge_metrics, formal_search_nonlegal_review_operator_packet, new_core_interface_candidate_gate, core_gate.external_package_acquisition_stage_gate]`
  - `not_current_basis_refs=[synthetic_rows, template_rows, sample_rows, literature_only_rows, formal_search_handoff_as_field_evidence, downstream_replay_holdout_calibration_not_run, merged_candidate_when_submit_ready_false]`
  - `can_prove` 只限于下一外部动作、env var、验证命令、阶段停止原因和 no-write 边界。
  - `cannot_prove` 明确包含 field treatment performance、field-supported mechanism validity、model-chain resume readiness、actuator/release gate readiness 和 legal/patentability conclusions。
- `deliverables/model_core_optimization/stage_boundary_external_action_board.md` 已新增 `## Machine Handoff`。
- `deliverables/manifest.json` 已同步通用和 Agent50 两组 handoff 摘要。

边界：

- R8u169 是 action board 机器恢复合同，不是新的 field 数据或控制策略。
- 不改变 `core_score`。
- 不生成 field evidence，不运行 downstream replay/holdout/calibration。
- 不恢复模型链，不写 actuator，不写 release gate。
- 不输出法律、专利授权或权利要求结论。

验证：

- `.venv/bin/python -m py_compile src/water_ai/stage_boundary_external_action_board.py experiments/run_stage_boundary_external_action_board.py experiments/run_agent50_model_core_governance.py`：通过。
- `.venv/bin/pytest -q tests/test_stage_boundary_external_action_board.py::test_stage_boundary_action_board_exposes_machine_handoff_for_low_friction_resume`：通过。
- `.venv/bin/python experiments/run_stage_boundary_external_action_board.py`：通过，已刷新 action board JSON/Markdown/manifest。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：通过，已刷新 Agent50 payload、stage board、manifest 与 external package artifacts。
- `.venv/bin/pytest -q tests/test_stage_boundary_external_action_board.py tests/test_agent50_core_interface_integration.py tests/test_external_package_readiness_board.py tests/test_model_core_optimization_governance_agent.py tests/test_deliverable_organization_agent.py`：97 passed。
- `.venv/bin/pytest -q`：636 passed。
- `.venv/bin/python tools/build_project_codegraph.py`：通过，CodeGraph fallback 刷新为 405 files、5352 nodes、8477 edges。

## 2026-06-22 R8u170：Stage Boundary Machine Handoff Contract Gate

背景：

- R8u169 已让 stage boundary action board 具备 `machine_handoff`，后续 agent 可以读取 route、basis、manual action 和证明边界。
- 但该 handoff 仍缺一个可计算 gate，用来判断“机器看版合同是否完整到足以低摩擦恢复”。
- 按当前 goal 的模块阶段终止思想，恢复入口也应有可计算阈值、pass/status 和 blockers，不能只靠字段看起来完整。

实现：

- 按 TDD 新增 `test_stage_boundary_action_board_scores_machine_handoff_contract_completeness`，先确认 `machine_handoff_contract_gate` 缺失导致失败。
- 更新 `src/water_ai/stage_boundary_external_action_board.py`：
  - board 顶层新增 `machine_handoff_contract_gate`。
  - 新增 `_machine_handoff_contract_gate()`，对六个合同维度评分：
    - `route_contract_completeness`
    - `manual_action_contract_completeness`
    - `basis_boundary_completeness`
    - `proof_boundary_completeness`
    - `no_write_boundary_completeness`
    - `recovery_linkage_completeness`
  - 新增 `_machine_handoff_contract_gate_status()`、`_presence_score()`、`_manual_action_contract_completeness()`、`_list_boundary_score()`、`_no_write_boundary_score()` 和 `_has_value()`。
  - Markdown `## Machine Handoff` 区域新增 gate status、score、stage pass、contract blockers 和 external wait blockers。
- 新增 `test_manifest_exposes_stage_boundary_machine_handoff_contract_gate`，锁定 manifest 必须暴露 gate 摘要。
- 更新 `experiments/run_stage_boundary_external_action_board.py` 与 `experiments/run_agent50_model_core_governance.py`：
  - 通用 `latest_stage_boundary_external_action_board_machine_handoff_contract_*` 写入 gate status、score、stage pass、contract blockers 和 external wait blockers。
  - Agent50 `latest_agent50_stage_boundary_external_action_board_machine_handoff_contract_*` 同步写入同组字段。

当前结果：

- `outputs/model_core_governance/stage_boundary_external_action_board.json` 现在显示：
  - `machine_handoff_contract_gate.gate_id=R8u170_stage_boundary_machine_handoff_contract_gate`
  - `gate_status=machine_handoff_contract_complete_waiting_for_external_input`
  - `contract_score=1.0`
  - `contract_stage_pass=True`
  - 六个合同维度均为 `1.0`
  - `contract_blockers=[]`
  - `external_wait_blockers=[real_external_input_required]`
- `deliverables/model_core_optimization/stage_boundary_external_action_board.md` 已显示 gate status 和 score。
- `deliverables/manifest.json` 已同步通用和 Agent50 两组 contract gate 摘要。

边界：

- R8u170 只证明 action board 的机器 handoff 合同完整。
- 它不证明 field treatment performance。
- 它不生成 field evidence。
- 它不恢复模型链。
- 它不写 actuator 或 release gate。
- 它不输出法律、专利授权或权利要求结论。

验证：

- `.venv/bin/python -m py_compile src/water_ai/stage_boundary_external_action_board.py experiments/run_stage_boundary_external_action_board.py experiments/run_agent50_model_core_governance.py`：通过。
- `.venv/bin/pytest -q tests/test_stage_boundary_external_action_board.py::test_stage_boundary_action_board_scores_machine_handoff_contract_completeness`：通过。
- `.venv/bin/python experiments/run_stage_boundary_external_action_board.py`：通过，已刷新 action board JSON/Markdown/manifest。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：通过，已刷新 Agent50 payload、stage board、manifest 与 external package artifacts。
- `.venv/bin/pytest -q tests/test_stage_boundary_external_action_board.py tests/test_agent50_core_interface_integration.py tests/test_external_package_readiness_board.py tests/test_model_core_optimization_governance_agent.py tests/test_deliverable_organization_agent.py`：99 passed。
- `.venv/bin/pytest -q`：638 passed。
- `.venv/bin/python tools/build_project_codegraph.py`：通过，CodeGraph fallback 刷新为 405 files、5361 nodes、8486 edges。

## 2026-06-22 R8u171：Stage Boundary Resource Boundary Gate

背景：

- 桌面 `复杂项目启动前置治理协议_v3_核心版.md` 中最适合当前工程模型的机制，不是整套十阶段流程，而是 `resource_boundary`：明确允许依据、禁止依据、补充依据、灰区、外部工具政策、人工标注政策和 no-write 政策。
- R8u170 已经证明 `machine_handoff` 合同完整，但仍缺少一个可计算边界来阻止 template/synthetic/sample/literature-only/human handoff 被误升级为 field evidence、法律/专利意见或 actuator/release readiness。
- 子代理只读审计指出，当前模型局部 gate 已较强，后续最大工程风险是跨产物恢复链一致性；本轮先补 resource boundary 这个基础块，下一轮可继续做 `governance_recovery_integrity_audit/change_inventory`。

实现：

- 按 TDD 新增 `test_stage_boundary_action_board_exposes_resource_boundary_gate`，先确认 `resource_boundary` 缺失导致失败。
- 更新 `src/water_ai/stage_boundary_external_action_board.py`：
  - board 顶层新增 `resource_boundary`。
  - board 顶层新增 `resource_boundary_gate`。
  - 新增 `_resource_boundary()`，显式列出 `allowed_basis`、`forbidden_basis`、`official_supplementary_basis`、`gray_zone`、`approved_access_or_permission`、`external_model_or_tool_policy`、`manual_annotation_or_human_labeling_policy` 和 `no_write_policy`。
  - 新增 `_resource_boundary_gate()`，对七个资源边界维度评分：
    - `allowed_basis_completeness`
    - `forbidden_basis_completeness`
    - `supplementary_basis_completeness`
    - `gray_zone_completeness`
    - `tool_policy_completeness`
    - `manual_annotation_policy_completeness`
    - `no_write_policy_completeness`
  - Markdown 报告新增 `## Resource Boundary`，显示 gate status、score、stage pass、blockers 和 external wait blockers。
- 新增 `test_manifest_exposes_stage_boundary_resource_boundary_gate`，锁定 manifest 必须暴露通用与 Agent50 两组 resource boundary 摘要。
- 更新 `experiments/run_stage_boundary_external_action_board.py` 与 `experiments/run_agent50_model_core_governance.py`：
  - 写入 `latest_stage_boundary_external_action_board_resource_boundary_*`。
  - 写入 `latest_agent50_stage_boundary_external_action_board_resource_boundary_*`。

当前结果：

- `outputs/model_core_governance/stage_boundary_external_action_board.json` 现在显示：
  - `resource_boundary.boundary_id=R8u171_stage_boundary_resource_boundary`
  - `resource_boundary_gate.gate_id=R8u171_stage_boundary_resource_boundary_gate`
  - `gate_status=resource_boundary_complete_waiting_for_real_external_input`
  - `resource_boundary_score=1.0`
  - `resource_boundary_stage_pass=True`
  - 七个资源边界维度均为 `1.0`
  - `resource_boundary_blockers=[]`
  - `external_wait_blockers=[real_external_input_required]`
- `forbidden_basis` 明确包含：
  - `template_rows_as_field_evidence`
  - `synthetic_rows_as_field_evidence`
  - `sample_rows_as_field_evidence`
  - `literature_only_rows_as_field_evidence`
  - `self_declared_candidate_without_preflight`
  - `formal_search_handoff_as_legal_or_patent_opinion`
  - `actuator_or_release_write_before_downstream_gates`
- `deliverables/model_core_optimization/stage_boundary_external_action_board.md` 已显示 resource boundary。
- `deliverables/manifest.json` 已同步通用和 Agent50 两组 resource boundary 摘要。

边界：

- R8u171 只增强验证治理层和工程恢复层的资源边界。
- 它不生成 field evidence。
- 它不证明 field treatment performance。
- 它不恢复模型链。
- 它不写 actuator 或 release gate。
- 它不输出法律、专利授权或权利要求结论。
- 子代理建议的下一处高边际价值工作是 `governance_recovery_integrity_audit/change_inventory`，用于检查 manifest、board、validation command、stale artifact、数字指标和最新 route 的跨产物一致性。

验证：

- `.venv/bin/python -m py_compile src/water_ai/stage_boundary_external_action_board.py experiments/run_stage_boundary_external_action_board.py experiments/run_agent50_model_core_governance.py`：通过。
- `.venv/bin/pytest -q tests/test_stage_boundary_external_action_board.py::test_stage_boundary_action_board_exposes_resource_boundary_gate`：通过。
- `.venv/bin/python experiments/run_stage_boundary_external_action_board.py`：通过，已刷新 action board JSON/Markdown/manifest。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：通过，已刷新 Agent50 payload、stage board、manifest 与 external package artifacts。
- `.venv/bin/pytest -q tests/test_stage_boundary_external_action_board.py tests/test_agent50_core_interface_integration.py tests/test_external_package_readiness_board.py tests/test_model_core_optimization_governance_agent.py tests/test_deliverable_organization_agent.py`：101 passed。
- `.venv/bin/pytest -q`：640 passed。
- `.venv/bin/python tools/build_project_codegraph.py`：通过，CodeGraph fallback 刷新为 405 files、5369 nodes、8494 edges。

## 2026-06-22 R8u172：Governance Recovery Integrity Audit

背景：

- R8u171 已把 `resource_boundary` 接入 stage boundary action board，能区分 allowed/forbidden/supplementary/gray-zone resources。
- 子代理只读审计指出，当前更高阶的工程风险不是单个 gate 缺失，而是长期迭代后 manifest、stage board、validation command、basis boundary、resource boundary 和 no-write boundary 之间出现漂移。
- 本轮目标是做一个只读、可计算、跨产物的恢复链一致性审计，避免后续 agent 只看 stale manifest 或旧 route 继续推进。

实现：

- 按 TDD 新增 `tests/test_governance_recovery_integrity_audit.py`，先确认 `water_ai.governance_recovery_integrity_audit` 缺失导致失败。
- 新增 `src/water_ai/governance_recovery_integrity_audit.py`：
  - `build_governance_recovery_integrity_audit()` 读取 project root、manifest、stage boundary board 和 core score gate。
  - `governance_recovery_integrity_audit_report_md()` 生成紧凑人看报告。
  - 审计七项检查：
    - `manifest_stage_board_route_alignment`
    - `validation_command_exists`
    - `manifest_pointer_freshness`
    - `manual_action_contract_integrity`
    - `basis_boundary_integrity`
    - `resource_boundary_integrity`
    - `no_write_boundary_integrity`
  - 输出 `recovery_integrity_score`、`blockers`、`stale_or_mismatch_fields`、`safe_next_route` 和 `change_inventory`。
- 新增 `experiments/run_governance_recovery_integrity_audit.py`：
  - 生成 `outputs/model_core_governance/governance_recovery_integrity_audit.json`。
  - 生成 `deliverables/model_core_optimization/governance_recovery_integrity_audit.md`。
  - 回写 manifest 通用字段与 Agent50 摘要字段。
- 新增 `test_manifest_exposes_governance_recovery_integrity_audit`，锁定 manifest 必须暴露该审计结果。

当前结果：

- `outputs/model_core_governance/governance_recovery_integrity_audit.json` 显示：
  - `audit_id=R8u172_governance_recovery_integrity_audit`
  - `audit_status=recovery_integrity_pass_waiting_for_real_external_input`
  - `recovery_integrity_score=1.0`
  - `recovery_integrity_stage_pass=True`
  - `blockers=[]`
  - `stale_or_mismatch_fields=[]`
  - `safe_next_route=submit_real_external_input_then_rerun_stage_preflight_and_agent50`
- 七个检查项均为 `1.0`。
- `change_inventory` 确认以下恢复链对象存在：
  - `outputs/model_core_governance/stage_boundary_external_action_board.json`
  - `deliverables/model_core_optimization/stage_boundary_external_action_board.md`
  - `experiments/run_focused_catalyst_response_merge.py`
  - `deliverables/manifest.json`
- `deliverables/manifest.json` 已新增 `latest_governance_recovery_integrity_*` 和 `latest_agent50_governance_recovery_integrity_*`。

边界：

- R8u172 只证明恢复链一致性。
- 它不生成 field evidence。
- 它不证明 field treatment performance。
- 它不恢复模型链。
- 它不写 actuator 或 release gate。
- 它不输出法律、专利授权或权利要求结论。

验证：

- `.venv/bin/python -m py_compile src/water_ai/governance_recovery_integrity_audit.py experiments/run_governance_recovery_integrity_audit.py`：通过。
- `.venv/bin/pytest -q tests/test_governance_recovery_integrity_audit.py`：通过。
- `.venv/bin/python experiments/run_governance_recovery_integrity_audit.py`：通过。
- `.venv/bin/pytest -q tests/test_agent50_core_interface_integration.py::test_manifest_exposes_governance_recovery_integrity_audit`：通过。
- `.venv/bin/pytest -q tests/test_governance_recovery_integrity_audit.py tests/test_agent50_core_interface_integration.py tests/test_stage_boundary_external_action_board.py tests/test_external_package_readiness_board.py tests/test_model_core_optimization_governance_agent.py tests/test_deliverable_organization_agent.py`：103 passed。
- `.venv/bin/pytest -q`：642 passed。
- `.venv/bin/python tools/build_project_codegraph.py`：通过，CodeGraph fallback 刷新为 409 files、5404 nodes、8555 edges。

## 2026-06-22 R8u173：Protocol-Adapted Recovery Integrity Trace

背景：

- 用户给出桌面 `复杂项目启动前置治理协议_v3_核心版.md`，要求借鉴它来优化当前工程模型。
- R8u171/R8u172 已经吸收了 resource boundary 和 recovery integrity audit，但仍有两个缺口：
  - `recovery_integrity_score=1.0` 是结论值，还没有显式数字复算链。
  - 协议规则如何进入工程模型仍主要写在人看 adapter 文档里，恢复审计 JSON/manifest 不能直接表达“选择性吸收而非全量复制”。
- 本轮遵守 TDD：先写失败测试，再实现最小代码，不新增线性 agent。

子代理与取舍：

- Hubble 做只读协议迁移审计，建议优先吸收 `current_basis/resource_boundary/numeric_trace/micro_task/dynamic_stage/subagent_probe`，并把全量历史 traceability、全量 source recency、完整十阶段复制放入 backlog。
- Helmholtz 做只读代码接入点审计，确认最佳接入点是 `src/water_ai/governance_recovery_integrity_audit.py` 和 `experiments/run_governance_recovery_integrity_audit.py`，不是新建 protocol agent。
- 主线程采纳上述核心判断；未采纳“本轮新增独立 subagent check”的建议，因为这会扩大范围。`subagent_orchestration_probe` 暂作为 selected protocol rule，下一轮可升级为独立 check。

实现：

- 修改 `tests/test_governance_recovery_integrity_audit.py`：
  - 新增 `numeric_calculation_trace` 断言。
  - 新增 `protocol_adaptation` 与 `anti_protocol_bloat_gate` 断言。
  - 要求报告 Markdown 显示 `numeric_calculation_trace_status` 和 `protocol_adaptation_status`。
- 修改 `tests/test_agent50_core_interface_integration.py`：
  - 要求 manifest 暴露 numeric trace 状态、pass、score_delta。
  - 要求 manifest 暴露 protocol adaptation 状态、anti-bloat gate、selected/deferred rule counts。
- 红灯验证：
  - 两个目标测试均因 `KeyError: 'numeric_calculation_trace'` 失败，确认测试捕获缺失行为。
- 修改 `src/water_ai/governance_recovery_integrity_audit.py`：
  - 新增 `_numeric_calculation_trace()`，用 `mean(check_scores)` 从七个恢复检查项复算分数。
  - 若复算不一致，加入 `numeric_calculation_trace_failed` blocker。
  - 新增 `_protocol_adaptation()`，把桌面协议选择性转译为恢复门规则。
  - 新增 Markdown 报告章节 `Numeric Calculation Trace` 和 `Protocol Adaptation`。
- 修改 `experiments/run_governance_recovery_integrity_audit.py`：
  - 将 numeric/protocol 状态写回 `deliverables/manifest.json` 的通用与 Agent50 摘要字段。
- 刷新：
  - `outputs/model_core_governance/governance_recovery_integrity_audit.json`
  - `deliverables/model_core_optimization/governance_recovery_integrity_audit.md`
  - `deliverables/manifest.json`
  - `deliverables/model_core_optimization/engineering_model_governance_adapter.md`
  - `notes/current_status.md`
  - `deliverables/README.md`

当前结果：

- `numeric_calculation_trace`：
  - `trace_id=R8u173_recovery_integrity_numeric_calculation_trace`
  - `trace_status=numeric_trace_pass_recovery_integrity_score_recomputed`
  - `score_formula=mean(check_scores)`
  - `component_count=7`
  - `reported_score=1.0`
  - `computed_score=1.0`
  - `score_delta=0.0`
  - `trace_pass=True`
- `protocol_adaptation`：
  - `adaptation_id=R8u173_complex_project_protocol_to_engineering_model_adapter`
  - `adaptation_status=selected_protocol_rules_integrated_into_recovery_gate`
  - selected rules：`current_basis_contract`、`resource_boundary_contract`、`numeric_calculation_trace`、`dynamic_stage_handoff`、`micro_task_execution_check`、`subagent_orchestration_probe`
  - deferred rules：`live_project_pool_scan`、`full_traceability_matrix`、`rendered_artifact_freshness`、`real_project_pressure_test_gate`
  - `anti_protocol_bloat_gate=pass_selective_adoption_not_full_protocol_copy`
- manifest 已暴露：
  - `latest_governance_recovery_integrity_numeric_trace_status`
  - `latest_governance_recovery_integrity_numeric_trace_pass`
  - `latest_governance_recovery_integrity_numeric_trace_score_delta`
  - `latest_governance_recovery_integrity_protocol_adaptation_status`
  - `latest_governance_recovery_integrity_protocol_anti_bloat_gate_status`
  - `latest_governance_recovery_integrity_protocol_selected_rule_count`
  - `latest_governance_recovery_integrity_protocol_deferred_rule_count`

边界：

- R8u173 只增强验证治理层的数字可复算、协议选择性迁移、低摩擦恢复和反膨胀能力。
- 它不生成 field evidence。
- 它不证明 field treatment performance。
- 它不恢复模型链。
- 它不写 actuator 或 release gate。
- 它不输出法律、专利授权或权利要求结论。

待后续候选：

- 将 `subagent_orchestration_probe` 从 selected protocol rule 升级为独立恢复链 check。
- 扩展 `_route_alignment()`，纳入 `route_event`、`route_reason`、`validation_command` 和 `current_basis_refs` 的 manifest 漂移约束。
- 只在进入论文/专利/field package 成熟阶段时，再扩展更完整的 traceability matrix。

验证：

- `.venv/bin/python -m py_compile src/water_ai/governance_recovery_integrity_audit.py experiments/run_governance_recovery_integrity_audit.py`：通过。
- `.venv/bin/pytest -q tests/test_governance_recovery_integrity_audit.py::test_governance_recovery_integrity_audit_scores_stage_boundary_recovery_chain`：通过。
- `.venv/bin/python experiments/run_governance_recovery_integrity_audit.py`：通过，已刷新审计 JSON、Markdown 和 manifest。
- `.venv/bin/pytest -q tests/test_agent50_core_interface_integration.py::test_manifest_exposes_governance_recovery_integrity_audit`：通过。
- `.venv/bin/pytest -q tests/test_governance_recovery_integrity_audit.py tests/test_agent50_core_interface_integration.py tests/test_stage_boundary_external_action_board.py tests/test_external_package_readiness_board.py tests/test_model_core_optimization_governance_agent.py tests/test_deliverable_organization_agent.py`：103 passed。
- `.venv/bin/pytest -q`：642 passed。
- `.venv/bin/python tools/build_project_codegraph.py`：通过，CodeGraph fallback 刷新为 409 files、5408 nodes、8560 edges。

## 2026-06-22 R8u174：Extended Route Alignment Recovery Gate

背景：

- R8u173 已经把桌面复杂项目治理协议转成 `numeric_calculation_trace` 与 `protocol_adaptation`，但 Helmholtz 的只读审计指出 `_route_alignment()` 仍只比对少数字段。
- 旧审计能发现 next_route 或 source env var 不一致，却不能发现 manifest 中的 `route_event`、`next_route_validation_command`、`current_basis_refs` 或 `not_current_basis_refs` 陈旧。
- 这会造成一种危险的恢复假阳性：next_route 看似没变，但实际验证命令或依据边界已经漂移，后续 agent 仍可能按旧入口继续。

实现：

- 按 TDD 新增 `test_governance_recovery_integrity_audit_fails_on_extended_route_alignment_drift`：
  - 构造 manifest 中 `route_event=continue_current_micro_loop`、`next_route_validation_command=experiments/old_stale_route.py`、`current_basis_refs=[stale.current_basis]`，但 next_route/source env var/forbidden basis 仍保持一致。
  - 红灯结果：旧实现仍输出 `manifest_stage_board_route_alignment=1.0`，测试失败，证明漏洞存在。
- 更新 `src/water_ai/governance_recovery_integrity_audit.py`：
  - `_route_alignment()` 现在同时比对：
    - `latest_stage_boundary_external_action_board_machine_handoff_route_event`
    - `latest_stage_boundary_external_action_board_machine_handoff_next_route`
    - `latest_stage_boundary_external_action_board_machine_handoff_next_route_source_env_var`
    - `latest_stage_boundary_external_action_board_machine_handoff_next_route_validation_command`
    - `latest_stage_boundary_external_action_board_machine_handoff_manual_action_required`
    - `latest_stage_boundary_external_action_board_machine_handoff_current_basis_refs`
    - `latest_stage_boundary_external_action_board_machine_handoff_not_current_basis_refs`
    - `latest_stage_boundary_external_action_board_resource_boundary_forbidden_basis`
  - 漂移时仍归入同一 `manifest_stage_board_route_alignment` gate，避免新增碎片化检查项。
- 更新 `experiments/run_stage_boundary_external_action_board.py`：
  - manifest 通用 handoff 摘要新增 `latest_stage_boundary_external_action_board_machine_handoff_next_route_validation_command`。
- 更新 `experiments/run_agent50_model_core_governance.py`：
  - manifest 通用与 Agent50 handoff 摘要均新增 validation command 字段。
- 更新 `tests/test_agent50_core_interface_integration.py`：
  - 锁定通用与 Agent50 manifest 字段必须等于 stage board handoff 的 `next_route_validation_command`。

当前结果：

- 扩展漂移负例已通过：当 route_event、validation command 或 current_basis 漂移时，审计会输出：
  - `manifest_stage_board_route_alignment=0.0`
  - `manifest_stage_board_route_alignment_below_1.00`
  - `safe_next_route=repair_recovery_integrity_blockers_before_next_route`
  - `stale_or_mismatch_fields` 包含漂移字段名。
- 刷新真实产物后，当前项目仍通过更强合同：
  - `outputs/model_core_governance/governance_recovery_integrity_audit.json`
  - `checks.manifest_stage_board_route_alignment=1.0`
  - `blockers=[]`
  - `stale_or_mismatch_fields=[]`
  - `safe_next_route=submit_real_external_input_then_rerun_stage_preflight_and_agent50`
- manifest 现在暴露：
  - `latest_stage_boundary_external_action_board_machine_handoff_next_route_validation_command`
  - `latest_agent50_stage_boundary_external_action_board_machine_handoff_next_route_validation_command`

边界：

- R8u174 只增强验证治理层的恢复一致性、stale route 防护和低摩擦继续能力。
- 它不生成 field evidence。
- 它不证明 field treatment performance。
- 它不恢复模型链。
- 它不写 actuator 或 release gate。
- 它不输出法律、专利授权或权利要求结论。

验证：

- `.venv/bin/python -m py_compile src/water_ai/governance_recovery_integrity_audit.py experiments/run_stage_boundary_external_action_board.py experiments/run_agent50_model_core_governance.py experiments/run_governance_recovery_integrity_audit.py`：通过。
- `.venv/bin/pytest -q tests/test_governance_recovery_integrity_audit.py::test_governance_recovery_integrity_audit_fails_on_extended_route_alignment_drift`：先红后绿。
- `.venv/bin/python experiments/run_stage_boundary_external_action_board.py`：通过。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：通过。
- `.venv/bin/python experiments/run_governance_recovery_integrity_audit.py`：通过。
- `.venv/bin/pytest -q tests/test_governance_recovery_integrity_audit.py tests/test_agent50_core_interface_integration.py tests/test_stage_boundary_external_action_board.py tests/test_external_package_readiness_board.py tests/test_model_core_optimization_governance_agent.py tests/test_deliverable_organization_agent.py`：104 passed。
- `.venv/bin/pytest -q`：643 passed。
- `.venv/bin/python tools/build_project_codegraph.py`：通过，CodeGraph fallback 刷新为 409 files、5410 nodes、8562 edges。

下一步候选：

- 如果继续治理链：把 `subagent_orchestration_probe` 从 protocol selected rule 升级为独立恢复链 check。
- 如果回到模型主链：优先提交或构造真实 `FOCUSED_CATALYST_RESPONSE_PATH` / `GREY_BOX_CALIBRATION_PACKAGE_DIR` 外部包，而不是继续内部 synthetic 扩张。

## 2026-06-22 R8u175：Stage Boundary Subagent Orchestration Probe

背景：

- 桌面 `复杂项目启动前置治理协议_v3_核心版.md` 明确要求：复杂项目可以评估子代理，但不能因为环境里列出子代理名称就声称可调度；必须区分 `environment_listed`、`tool_discovered`、`spawn_attempted`、`agent_returned/result_integrated`，并在不需要或不能调用时记录 `inline_fallback/no_spawn_reason` 和生命周期清理状态。
- R8u173 已把 `subagent_orchestration_probe` 选入协议适配规则，但那时还只是 selected rule；R8u174 继续压实了 route alignment，却仍没有真正的 stage-board 字段和 audit check。
- 当前阶段是 `external_activation_wait`：最高价值动作是等待/提交真实 focused catalyst response 或新核心接口包，不存在边界清楚、可并行、能独立提高模型主链的内部子代理任务。因此正确动作不是开子代理，而是把“不该开”的理由写成可恢复、可审计字段。

实现：

- 按 TDD 新增三类红灯：
  - `test_stage_boundary_action_board_exposes_subagent_orchestration_probe` 要求 stage board 暴露 `subagent_orchestration_probe`。
  - `test_governance_recovery_integrity_audit_fails_on_invalid_subagent_probe` 构造 `capability=available`、`strategy=parallel_domains` 但无 tool/spawn/roles 证据的坏探针，要求恢复链失败。
  - `test_manifest_exposes_stage_boundary_subagent_orchestration_probe` 要求 manifest 暴露通用与 Agent50 的 subagent 摘要字段。
- 更新 `src/water_ai/stage_boundary_external_action_board.py`：
  - 新增 `subagent_orchestration_probe`，当前字段为：
    - `probe_id=R8u175_stage_boundary_subagent_orchestration_probe`
    - `probe_status=subagent_orchestration_not_needed_for_external_wait`
    - `capability=not_needed`
    - `strategy=not_needed`
    - `no_spawn_reason=current_stage_is_external_activation_wait_and_no_parallel_internal_task_is_required`
    - `capability_probe.tool_discovered=False`
    - `capability_probe.spawn_attempted=False`
    - `capability_probe.wait_status=not_started`
    - `capability_probe.integration_decision=not_needed`
    - `lifecycle_cleanup.close_status=not_needed`
    - `lifecycle_cleanup.open_agent_cleanup_required=False`
  - Markdown 报告新增 `## Subagent Orchestration Probe`，让人看版也能直接看到为什么当前不分派子代理。
- 更新 `src/water_ai/governance_recovery_integrity_audit.py`：
  - 新增 `subagent_orchestration_integrity` 检查。
  - 缺少探针时输出 `subagent_orchestration_probe_missing`。
  - 若 `capability=available` 但没有 `tool_discovered` 或 `spawn_attempted`，输出 `subagent_available_without_tool_or_spawn_evidence`。
  - 若 `strategy=parallel_domains` 但没有 roles，输出 `subagent_parallel_strategy_without_roles`。
  - 若子代理边界允许 goal delegation 或 field evidence generation，也会失败。
  - `protocol_adaptation.selected_rules.subagent_orchestration_probe.implemented_as` 已从 handoff-compatible fields 更新为 `subagent_orchestration_integrity`。
- 更新 `experiments/run_stage_boundary_external_action_board.py` 和 `experiments/run_agent50_model_core_governance.py`：
  - manifest 通用字段新增：
    - `latest_stage_boundary_external_action_board_subagent_probe_status`
    - `latest_stage_boundary_external_action_board_subagent_strategy`
    - `latest_stage_boundary_external_action_board_subagent_tool_discovered`
    - `latest_stage_boundary_external_action_board_subagent_spawn_attempted`
    - `latest_stage_boundary_external_action_board_subagent_open_cleanup_required`
  - Agent50 字段新增：
    - `latest_agent50_stage_boundary_external_action_board_subagent_probe_status`
    - `latest_agent50_stage_boundary_external_action_board_subagent_strategy`
    - `latest_agent50_stage_boundary_external_action_board_subagent_tool_discovered`
    - `latest_agent50_stage_boundary_external_action_board_subagent_spawn_attempted`
    - `latest_agent50_stage_boundary_external_action_board_subagent_open_cleanup_required`
- 刷新：
  - `outputs/model_core_governance/stage_boundary_external_action_board.json`
  - `deliverables/model_core_optimization/stage_boundary_external_action_board.md`
  - `outputs/model_core_governance/governance_recovery_integrity_audit.json`
  - `deliverables/model_core_optimization/governance_recovery_integrity_audit.md`
  - `deliverables/manifest.json`
  - `notes/current_status.md`
  - `deliverables/README.md`

当前结果：

- 当前真实 stage board 的 subagent 状态为：
  - `probe_status=subagent_orchestration_not_needed_for_external_wait`
  - `capability=not_needed`
  - `strategy=not_needed`
  - `tool_discovered=False`
  - `spawn_attempted=False`
  - `open_agent_cleanup_required=False`
- 当前恢复审计新增第八个检查项：
  - `subagent_orchestration_integrity=1.0`
  - `recovery_integrity_score=1.0`
  - `numeric_calculation_trace.component_count=8`
  - `blockers=[]`
  - `safe_next_route=submit_real_external_input_then_rerun_stage_preflight_and_agent50`
- 这轮把“该不该开子代理”从主观判断变成了机器可检查字段：开了要有工具/角色/集成/清理证据；没开要有 no-spawn reason。

边界：

- R8u175 不实际调用或创建子代理。
- R8u175 不生成 field evidence。
- R8u175 不证明 field treatment performance。
- R8u175 不恢复模型链。
- R8u175 不写 actuator 或 release gate。
- R8u175 不输出法律、专利授权或权利要求结论。

验证：

- `.venv/bin/pytest -q tests/test_stage_boundary_external_action_board.py::test_stage_boundary_action_board_exposes_subagent_orchestration_probe`：先红后绿。
- `.venv/bin/pytest -q tests/test_governance_recovery_integrity_audit.py::test_governance_recovery_integrity_audit_fails_on_invalid_subagent_probe`：先红后绿。
- `.venv/bin/pytest -q tests/test_agent50_core_interface_integration.py::test_manifest_exposes_stage_boundary_subagent_orchestration_probe`：刷新产物后通过。
- `.venv/bin/python experiments/run_stage_boundary_external_action_board.py`：通过，已刷新 stage board JSON、Markdown 和 manifest。
- `.venv/bin/python experiments/run_agent50_model_core_governance.py`：通过，Agent50 继续保持 external activation wait。
- `.venv/bin/python experiments/run_governance_recovery_integrity_audit.py`：通过，恢复链仍为 pass。
- `.venv/bin/pytest -q tests/test_governance_recovery_integrity_audit.py tests/test_agent50_core_interface_integration.py tests/test_stage_boundary_external_action_board.py tests/test_external_package_readiness_board.py tests/test_model_core_optimization_governance_agent.py tests/test_deliverable_organization_agent.py`：107 passed。
- `.venv/bin/pytest -q`：646 passed。
- `.venv/bin/python tools/build_project_codegraph.py`：通过，CodeGraph fallback 刷新为 409 files、5417 nodes、8569 edges。

下一步候选：

- 如果继续治理链：把 `subagent_problem_decomposition_builder` 从协议文字进一步压成可复用 helper，但只有在真实需要并行审计/领域核验时才启用，避免 meta-tooling loop。
- 如果回到模型主链：优先补 `FOCUSED_CATALYST_RESPONSE_PATH` 或 `GREY_BOX_CALIBRATION_PACKAGE_DIR` 这类真实外部输入包；没有真实包时，不继续内部 synthetic 扩张。

## 2026-06-22 R8u176/R8u177 协议治理运行门控

触发：

- 用户要求借鉴桌面 `复杂项目启动前置治理协议_v3_核心版.md`，继续优化工程模型。
- 当前模型已经有 machine handoff、resource boundary、numeric trace、subagent probe，但仍存在两个架构摩擦：第一，自我打断/治理审查可能过频；第二，恢复链虽能算分，但缺少最小“依据-动作-边界-反膨胀”追溯行。

子代理只读审计：

- Bernoulli 建议不要复制整份协议，而是迁移 current_basis、resource_boundary、decision log、traceability、stage handoff、anti-bloat 等运行时约束。
- Averroes 建议在 stage boundary board 新增低摩擦回合门，避免每次新想法都触发深度重排。
- Dalton 建议在 governance recovery audit 中新增最小追溯门，范围限定为恢复路由追溯，不扩大为全项目 traceability matrix。

实现：

- `src/water_ai/stage_boundary_external_action_board.py`
  - 新增 `low_friction_round_gate`。
  - 当前状态为 `low_friction_single_action_waiting_for_external_input`。
  - 当前 `round_score=1.0`。
  - 只保留一个最高优先外部动作：`FIELD_ACTIVATION_RESPONSE_FOCUS_HANDOFF_NEXT_ACTION`。
  - 明确 `continue_expansion_allowed=False`，防止在真实外部输入前继续内部扩张。
- `experiments/run_stage_boundary_external_action_board.py`
  - 将 low friction 摘要写入 manifest。
- `experiments/run_agent50_model_core_governance.py`
  - 将 low friction 摘要写入 Agent50 manifest 字段。
- `src/water_ai/governance_recovery_integrity_audit.py`
  - 新增 `minimum_traceability_gate`。
  - 当前状态为 `minimum_recovery_traceability_pass`。
  - 当前 `traceability_score=1.0`、`missing_link_count=0`。
  - 追溯行限定为 `basis_to_stage_route`、`resource_boundary_to_no_write`、`manual_action_to_resume_evidence`、`protocol_adaptation_to_anti_bloat`。
  - 明确范围为 `recovery_route_trace_only_not_full_project_traceability_matrix`。
- `experiments/run_governance_recovery_integrity_audit.py`
  - 将 minimum traceability 摘要写入通用和 Agent50 manifest 字段。
- `src/water_ai/agents/agent_architecture_consolidation_agent.py`
  - 刷新 formal search nonlegal review response 的 AI draft boundary：AI 草稿不能被当成人工非法律 review response，也不能进入 claim scope patch。

测试：

- 先新增失败测试，再实现最小代码。
- `.venv/bin/pytest -q tests/test_stage_boundary_external_action_board.py::test_stage_boundary_action_board_scores_low_friction_round_gate tests/test_governance_recovery_integrity_audit.py::test_governance_recovery_integrity_audit_scores_stage_boundary_recovery_chain tests/test_governance_recovery_integrity_audit.py::test_governance_recovery_integrity_audit_flags_missing_minimum_traceability_link`：3 passed。
- `.venv/bin/pytest -q tests/test_stage_boundary_external_action_board.py::test_stage_boundary_action_board_scores_low_friction_round_gate tests/test_governance_recovery_integrity_audit.py::test_governance_recovery_integrity_audit_scores_stage_boundary_recovery_chain tests/test_governance_recovery_integrity_audit.py::test_governance_recovery_integrity_audit_flags_missing_minimum_traceability_link tests/test_agent50_core_interface_integration.py::test_manifest_exposes_low_friction_round_gate_summary tests/test_agent50_core_interface_integration.py::test_manifest_exposes_minimum_recovery_traceability_gate_summary tests/test_agent50_core_interface_integration.py::test_manifest_exposes_nonlegal_review_ai_draft_boundary_gate`：6 passed。
- `.venv/bin/pytest -q tests/test_stage_boundary_external_action_board.py tests/test_governance_recovery_integrity_audit.py tests/test_agent50_core_interface_integration.py tests/test_agent_architecture_consolidation_agent.py tests/test_model_core_optimization_governance_agent.py`：126 passed。
- `.venv/bin/pytest -q`：652 passed。
- `.venv/bin/python tools/build_project_codegraph.py`：通过，CodeGraph fallback 刷新为 409 files、5430 nodes、8582 edges。

边界：

- R8u176/R8u177 只增强验证治理层、低摩擦阶段门、最小恢复追溯和 AI 草稿边界。
- 不生成 field evidence。
- 不证明 field treatment performance。
- 不恢复模型链。
- 不写 actuator 或 release gate。
- 不输出法律意见、专利授权判断或权利要求文本。

下一步：

- 继续围绕真实外部输入入口推进：优先 `FOCUSED_CATALYST_RESPONSE_PATH`，其次 `GREY_BOX_CALIBRATION_PACKAGE_DIR`。
- 如果没有真实包，不继续内部 synthetic 扩张；低摩擦门应把新增想法先沉淀进 backlog，而不是立刻触发深度重排。

## 2026-06-22 R8u178 Claim Basis Promotion Gate

触发：

- 当前 goal 明确要求每轮迭代有可计算目标、阶段终止条件和证据边界，并把专利级成熟度理解为“用专利交底标准反推模型清晰度”，不能把 `AI/多智能体/知识图谱/闭环控制` 词语本身当创新点。
- R8u176/R8u177 已经把治理打断降频，并证明当前最高外部动作仍是 `FOCUSED_CATALYST_RESPONSE_PATH`。在没有真实外部包时，本轮不继续扩张 synthetic 模型，而是压实“哪些主张能升级、哪些必须继续阻断”的证据边界。

实现：

- `src/water_ai/field_evidence_gate.py`
  - 在 `UnifiedFieldEvidenceGate.build()` 中新增 `claim_basis_promotion_gate`。
  - 每条 `unified_evidence_record` 生成一个 promotion row，包含 `current_basis`、`not_current_basis`、`blocked_by`、`allowed_promotion_level`、`next_required_gate`、`requires_human_review` 和 no-write flags。
  - 只有当 field import、timestamped replay/evidence chain、soft sensor holdout 和 blockers 同时通过时，才允许输出 `field_supported_claim_candidate_not_release_or_actuator`。
  - 即使该候选 ready，也仍不能写 actuator、release gate、专利/法律结论。
- `experiments/run_unified_field_evidence_gate.py`
  - 报告、deliverable 和 manifest 新增 claim promotion 摘要。
- `src/water_ai/agents/model_core_optimization_governance_agent.py`
  - Agent50 scorecard 新增 `claim_basis_promotion_*` 字段。
- `experiments/run_agent50_model_core_governance.py`
  - manifest 新增 Agent50 promotion gate 摘要。

当前真实项目结果：

- `claim_basis_promotion_gate_status=claim_basis_promotion_blocked_until_field_validation`
- `promotion_decision_count=5`
- `ready_promotion_count=0`
- `blocked_promotion_count=5`
- `can_emit_field_claim_upgrade=False`
- `can_write_to_actuator=False`
- `can_write_to_release_gate=False`
- 解释：source_basis detail 已完整，但 `field_supported_edge_ratio=0.0`，所以不能把文献追溯、模板、synthetic 或 handoff 误升级为 field-supported claim。

TDD 与验证：

- 新增测试后先红：
  - `tests/test_unified_field_evidence_gate.py::test_unified_gate_exposes_claim_basis_promotion_gate_for_blocked_records`
  - `tests/test_unified_field_evidence_gate.py::test_unified_gate_allows_only_field_supported_candidate_after_real_field_chain_passes`
  - 失败原因：缺少 `claim_basis_promotion_gate`。
- 最小实现后：
  - `.venv/bin/pytest -q tests/test_unified_field_evidence_gate.py::test_unified_gate_exposes_claim_basis_promotion_gate_for_blocked_records tests/test_unified_field_evidence_gate.py::test_unified_gate_allows_only_field_supported_candidate_after_real_field_chain_passes`：2 passed。
- manifest/Agent50 回接：
  - `tests/test_agent50_core_interface_integration.py::test_manifest_exposes_claim_basis_promotion_gate_summary`：先因旧 metrics 缺 gate 失败，刷新 `experiments/run_unified_field_evidence_gate.py` 后通过。
  - `tests/test_model_core_optimization_governance_agent.py::test_governance_agent_consumes_r2_r3_outputs_and_demotes_repeated_baselines`：先因 Agent50 scorecard 缺字段失败，接入后通过。
  - `tests/test_agent50_core_interface_integration.py::test_manifest_exposes_agent50_claim_basis_promotion_gate_summary`：先因 manifest 缺 Agent50 字段失败，接入并刷新 Agent50 后通过。
- targeted：
  - `.venv/bin/pytest -q tests/test_unified_field_evidence_gate.py tests/test_model_core_optimization_governance_agent.py tests/test_agent50_core_interface_integration.py`：68 passed。
- full regression：
  - `.venv/bin/pytest -q`：656 passed。
- CodeGraph：
  - `.venv/bin/python tools/build_project_codegraph.py`：通过，CodeGraph fallback 刷新为 409 files、5450 nodes、8603 edges。

边界：

- R8u178 不生成新 field evidence。
- R8u178 不证明现场处理效果。
- R8u178 不输出法律意见、专利授权判断或权利要求文本。
- R8u178 不恢复模型链。
- R8u178 不写 actuator 或 release gate。

阶段判断：

- 本轮不是 core_score 大幅提升轮，而是证据升级边界硬化轮。
- 按低摩擦门，完成该小闭环后不继续内部扩张；下一步仍应优先补真实 `FOCUSED_CATALYST_RESPONSE_PATH` 或进入真实 field package / human review 路径。

## 2026-06-22 R8u179 Stage Boundary Claim Basis Promotion Snapshot

触发：

- R8u178 已经让统一 field evidence gate 和 Agent50 scorecard 看见 `claim_basis_promotion_gate`。
- 但最高恢复入口 `stage_boundary_external_action_board` 仍只暴露泛化的 `field_claim_upgrade_allowed=False`，没有暴露具体 promotion gate 状态。
- 风险：后续 agent 如果只读 stage board，仍可能不知道当前 5 条主张升级都被 field validation 阻断。

TDD：

- 新增 `tests/test_stage_boundary_external_action_board.py::test_stage_boundary_action_board_exposes_claim_basis_promotion_snapshot`。
  - 先红：`build_stage_boundary_external_action_board()` 不接受 `claim_basis_promotion_gate`。
  - 实现后绿。
- 新增/扩展 `tests/test_agent50_core_interface_integration.py::test_manifest_exposes_stage_boundary_claim_basis_promotion_snapshot`。
  - 先红：旧 stage board JSON 缺 `claim_basis_promotion_snapshot`。
  - 接入 `experiments/run_stage_boundary_external_action_board.py` 后通用 manifest 字段通过。
  - 再扩展 Agent50 前缀字段，先红：manifest 缺 `latest_agent50_stage_boundary_claim_basis_promotion_*`。
  - 接入 `experiments/run_agent50_model_core_governance.py` 并刷新后通过。

实现：

- `src/water_ai/stage_boundary_external_action_board.py`
  - `build_stage_boundary_external_action_board()` 新增可选参数 `claim_basis_promotion_gate`。
  - 新增 `_claim_basis_promotion_snapshot()`。
  - 输出 `claim_basis_promotion_snapshot`。
  - Markdown 报告新增 `## Claim Basis Promotion Snapshot`。
- `experiments/run_stage_boundary_external_action_board.py`
  - 读取 `outputs/unified_field_evidence_gate/unified_field_evidence_gate_metrics.json`。
  - 将 `claim_basis_promotion_gate` 传给 stage board。
  - manifest 新增通用 `latest_stage_boundary_claim_basis_promotion_*` 字段。
- `experiments/run_agent50_model_core_governance.py`
  - Agent50 内部重建 stage board 时同样传入 `claim_basis_promotion_gate`。
  - manifest 新增 `latest_agent50_stage_boundary_claim_basis_promotion_*` 字段。

调试记录：

- 首次运行 `experiments/run_stage_boundary_external_action_board.py` 失败：
  - `NameError: name 'claim_basis_promotion_snapshot' is not defined`
  - 根因：在 `_update_manifest()` 内写 manifest 字段时没有从 `board` 中取局部变量。
  - 修复：在 `_update_manifest()` 中加入 `claim_basis_promotion_snapshot = board["claim_basis_promotion_snapshot"]`。

当前结果：

- `snapshot_status=claim_basis_promotion_blocked_until_field_validation`
- `ready_promotion_count=0`
- `blocked_promotion_count=5`
- `can_emit_field_claim_upgrade=False`
- `can_write_to_actuator=False`
- `can_write_to_release_gate=False`
- `stage_boundary_effect=keep_external_wait_until_real_field_validation_and_human_review`

验证：

- `.venv/bin/pytest -q tests/test_stage_boundary_external_action_board.py tests/test_agent50_core_interface_integration.py tests/test_model_core_optimization_governance_agent.py`：74 passed。
- `.venv/bin/pytest -q`：658 passed。
- `.venv/bin/python tools/build_project_codegraph.py`：通过，CodeGraph fallback 刷新为 409 files、5457 nodes、8610 edges。

边界：

- R8u179 只做最高恢复入口可见性回接。
- 不改变 action priority。
- 不生成 field evidence。
- 不恢复模型链。
- 不输出法律意见、专利授权判断或权利要求文本。
- 不写 actuator 或 release gate。

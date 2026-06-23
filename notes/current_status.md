# 当前状态

更新时间：2026-06-22

## 核心目标

在低成本传感条件下，通过循环式水处理结构为软传感器和多智能体诊断争取时间，利用软传感器估计不可直接观测的过程状态，再由多智能体系统完成机理解释、故障诊断与闭环控制，动态决定是否回流、延长停留时间、调整药剂投加、预处理/切换单元或放行。

## 最新核心复盘承接

- 2026-06-22 新增 `R8u187_formal_nonlegal_operator_handoff_dependency_repair`：承接 R8u186 的 internal expansion saturation gate，本轮没有继续内部微扩张，而是修复一个真实硬边界矛盾。复核外部恢复通道时发现：`formal_search_ai_nonlegal_review_brief.json` 仍保留 R8u133/R8u134 生成的 7 行人工非法律审查对象，但 `formal_search_nonlegal_review_response_template.json` 在无 `FORMAL_SEARCH_RESULT_PACKAGE_PATH` 的默认环境下被 Agent60 合法刷新回 0 行；随后 `run_formal_search_nonlegal_review_operator_packet.py` 只读最新模板，导致 operator packet 从 `ready_waiting_for_human_response` 退化为 `blocked_by_response_template`。现已在 `formal_search_nonlegal_review_operator_packet` 中显式加入上游 `FORMAL_SEARCH_RESULT_PACKAGE_PATH` 依赖：当 AI brief 已通过边界且 preliminary formal search handoff 可用时，即使当前 Agent60 模板被默认环境刷新为空，operator packet 仍可从 AI brief 稳定生成 7 行人工审查合同，并在 validation command 中同时携带 `FORMAL_SEARCH_RESULT_PACKAGE_PATH=...preliminary_formal_search_result_package.json` 与 `FORMAL_SEARCH_NONLEGAL_REVIEW_RESPONSE_PATH=...formal_search_nonlegal_review_response.json`。当前结果：`packet_status=formal_search_nonlegal_review_operator_packet_ready_waiting_for_human_response`、`expected_review_packet_row_count=7`、`contract_basis=ai_brief_rows_with_upstream_formal_search_package_dependency`、`can_route_to_claim_scope_patch_draft=False`。验证：TDD 红灯为 builder 不接受 `upstream_formal_search_result_package_path`；修复后 operator packet tests `4 passed`，核心 targeted tests `97 passed`，完整回归 `663 passed`，CodeGraph fallback 刷新为 `409 files / 5481 nodes / 8636 edges`。边界：R8u187 只修复人工审查 handoff 的依赖表达和状态漂移，不生成 human review response，不生成法律意见、prior-art 结论、权利要求文本或 field evidence，不恢复模型链，不写 actuator/release gate。
- 2026-06-22 新增 `R8u186_stage_boundary_internal_expansion_saturation_gate`：承接桌面 `复杂项目启动前置治理协议_v3_核心版.md` 和三位只读子代理审阅结果，本轮没有复制完整协议、没有新增 agent、没有继续补展示材料，而是把其中最适合当前阶段的 `anti_protocol_bloat`、`continuous cycle no-idle` 与 `claim_readiness_ladder` 压缩成一个可机读阶段门。`stage_boundary_external_action_board.json` 现在新增 `internal_expansion_saturation_gate`，当前状态为 `internal_expansion_saturated_waiting_for_external_input`、`decision=stop_internal_micro_expansion_wait_for_real_external_input`、`required_next_external_input=FOCUSED_CATALYST_RESPONSE_PATH`、`micro_tweak_expansion_allowed=False`、`claim_readiness_ceiling=governance_contract_only_until_real_field_validation`。该门明确：在 `iteration_delta=0.0`、machine handoff/resource boundary/low-friction gate 已完整、focused candidate 仍未提交真实外部输入、claim promotion 仍被 field validation 阻断时，停止继续内部微扩张；只允许消费真实外部输入、修复硬性边界矛盾、刷新外部输入后的产物或运行非扩张验证。通用和 Agent50 manifest 已同步暴露 saturation 摘要。验证：新增 TDD 红灯 `KeyError: internal_expansion_saturation_gate` 后通过；stage boundary/Agent50/recovery/external targeted tests `84 passed`。边界：R8u186 只增强验证治理层、空转抑制、主张成熟度天花板和可演化性，不生成 field evidence，不恢复模型链，不写 actuator/release gate，不输出法律/专利结论。
- 2026-06-22 新增 `R8u185_stage_boundary_embedded_rejection_boundaries`：承接 R8u184 后，本轮停止继续补“方便查看”的字段，只修复一个证据边界缺口。复核发现：`external_activation_operator_action_packet` 已含 `rejection_boundaries`、`boundary_checks` 和 `no_write_boundary`，但最高入口 `stage_boundary_external_action_board.machine_handoff.manual_action_required`、`low_friction_round_gate.manual_action_required` 和 manifest 仍主要暴露模板、schema、命令序列；只读 stage board/manifest 时，能执行 focused 外部输入，但不能完整看到“哪些输入必须拒收”。现已将 operator packet 的拒收边界、边界检查和 no-write boundary 透传到 R7/focused action row、operator runbook、machine handoff、low-friction gate，以及通用/Agent50 manifest。当前最高入口明确拒收 template/sample/synthetic rows 作为 field evidence、拒收 TODO/template markers、拒收未满足共同真实 batch、拒收未确认 no-write 的响应，并保留“不能生成 field evidence、不能恢复模型链、不能写 actuator/release gate”的边界。验证：先以 `KeyError: rejection_boundaries` 红灯，再通过；manifest 集成测试通过，recovery integrity 仍为 `1.0`。边界：R8u185 只增强验证治理层、证据边界完整性和工程可执行性，不生成 field evidence，不恢复模型链，不改变 action 排序，不写 actuator/release gate，不输出法律/专利结论。
- 2026-06-22 新增 `R8u184_stage_boundary_embedded_focused_action_package`：承接 R8u183 的可执行命令合同，本轮继续压低真实 `FOCUSED_CATALYST_RESPONSE_PATH` 提交前的跨文件扫描摩擦。复核发现：`external_activation_operator_action_packet` 已含 focused template、schema、merge plan 和三步 `current_commands`，但最高入口 `stage_boundary_external_action_board.machine_handoff.manual_action_required`、`low_friction_round_gate.manual_action_required` 和 manifest 仍只暴露 env var、action 与 validation command；后续只看 stage board/manifest 的 agent 或操作者仍需再跳到 operator packet 才能找到模板路径和命令序列。现已将 `focused_template_path`、`focused_schema_path`、`focused_merge_plan_path` 和 `current_commands` 最小执行包投影到 R7/focused action row、operator runbook、machine handoff、low-friction gate，以及通用/Agent50 manifest 摘要。当前 machine handoff 可直接读到 `input_template_path=outputs/catalyst_response_submission_kit/focused_catalyst_response_template.json`、`schema_path=outputs/catalyst_response_submission_kit/focused_catalyst_response_schema.json` 和命令序列：填 focused 模板、export `FOCUSED_CATALYST_RESPONSE_PATH`、运行 `.venv/bin/python experiments/run_focused_catalyst_response_merge.py`。验证：先以 `KeyError: input_template_path` 红灯，再通过；manifest 集成测试通过，recovery integrity 仍为 `1.0`。边界：R8u184 只增强验证治理层、工程可执行性和可演化性，不生成 field evidence，不恢复模型链，不写 actuator/release gate，不输出法律/专利结论。
- 2026-06-22 新增 `R8u183_executable_focused_validation_command_contract`：承接 R8u182 后继续处理同一条最高价值外部恢复链。本轮复核发现：operator packet 的 `current_commands` 已经使用 `.venv/bin/python experiments/run_focused_catalyst_response_merge.py`，但 `stage_boundary_external_action_board.machine_handoff.next_route_validation_command`、low-friction gate 的 `manual_action_required.validation_command` 和 Agent50 推荐文本仍使用裸脚本路径 `experiments/run_focused_catalyst_response_merge.py`。这会让“机器看字段”和“人看推荐”在真实 focused catalyst response 提交时产生执行摩擦。现已在 `stage_boundary_external_action_board` 中新增 Python experiment 命令规范化，使 R7/focused 外部动作的 validation command 统一为 `.venv/bin/python experiments/run_focused_catalyst_response_merge.py`；Agent50 推荐文本同步改为可直接执行的 focused merge、field activation 和 Agent50 rerun 命令。刷新后 stage board、recovery audit、Agent50 report 与 manifest 指针均保持一致，recovery integrity 仍为 `1.0`，下一步仍是提交真实 `FOCUSED_CATALYST_RESPONSE_PATH`。验证：先以裸命令断言红灯，再通过；focused validation command targeted tests `3 passed`。边界：R8u183 只增强工程可执行性、验证治理层和外部恢复接口一致性，不生成 field evidence，不恢复模型链，不写 actuator/release gate，不输出法律/专利结论。
- 2026-06-22 新增 `R8u182_external_operator_packet_generic_next_operator_action`：承接 R8u181 后，本轮继续只做高边际价值的恢复入口减摩擦，不新增 agent、不扩张展示层。复查 `external_activation_operator_action_packet` 发现它已经有 `packet_next_operator_action`，但缺少项目内多数 operator packet / router 通用使用的顶层 `next_operator_action`，导致后续 agent 或操作者必须知道这个 packet 的特定字段名，增加真实 focused catalyst response 提交链的 scan 摩擦。现已在 `src/water_ai/external_activation_operator_packet.py` 中新增顶层 `next_operator_action`，并保持其与 `packet_next_operator_action` 完全一致；`experiments/run_external_activation_operator_packet.py` 的终端输出、Markdown 报告和 manifest 写入也统一消费该通用字段。当前动作仍为 `fill_outputs/catalyst_response_submission_kit/focused_catalyst_response_template.json_with_real_field_values_then_set_FOCUSED_CATALYST_RESPONSE_PATH`，目标隐藏状态仍为 `catalyst_activity`，source env var 仍为 `FOCUSED_CATALYST_RESPONSE_PATH`。验证：external packet 单测先以 `KeyError: next_operator_action` 红灯，再通过；external packet/stage board/Agent50 integration/governance targeted tests `78 passed`。边界：R8u182 只增强验证治理层、工程可恢复性和接口一致性，不生成 field evidence，不恢复模型链，不写 actuator/release gate，不输出法律/专利结论。
- 2026-06-22 新增 `R8u181_low_friction_canonical_focus_handoff_action`：承接 R8u180 后的阶段门节流原则，本轮没有继续扩张治理证明，而是修复一个真实恢复入口摩擦：`stage_boundary_external_action_board` 的低摩擦 gate 实际已经选择 `FOCUSED_CATALYST_RESPONSE_PATH`，但 `selected_action_id` 仍显示底层 `R8u139_R7_REAL_FIELD_PACKAGE`，容易让后续操作者或 agent 误解为下一步要补全量 R7 field package，而不是先补 6 行 focused catalyst response。现在 `low_friction_round_gate` 同时暴露 `selected_underlying_action_id=R8u139_R7_REAL_FIELD_PACKAGE` 与 `selected_canonical_action_id=FIELD_ACTIVATION_RESPONSE_FOCUS_HANDOFF_NEXT_ACTION`；通用和 Agent50 manifest 也同步写入这两个字段。当前 `selected_source_env_var=FOCUSED_CATALYST_RESPONSE_PATH`，底层仍保持 R7 field package 语义，canonical 人机动作则对齐 Agent50 推荐动作。验证：stage board/Agent50 integration targeted tests `35 passed`，完整回归 `660 passed`，CodeGraph fallback 刷新为 `409 files / 5465 nodes / 8618 edges`。边界：R8u181 只增强验证治理层与工程恢复可执行性，不改变 action 排序，不生成 field evidence，不恢复模型链，不写 actuator/release gate，不输出法律/专利结论。
- 2026-06-22 新增 `R8u180_module_stage_termination_proof_rows`：承接当前 goal 的“可计算目标、阶段终止条件和证据边界”要求，本轮没有新增新的 agent 或 synthetic 模型能力，而是把 Agent50 的 `module_stage_termination_gate` 从汇总状态升级为逐项可审查的阶段终止证明表。`ModelCoreOptimizationGovernanceAgent` 现在输出 `termination_proof_rows`、`termination_proof_status` 和 `termination_pass_rate`；7 个阶段终止指标逐项映射到系统层、核心能力、证据来源、阈值、通过状态、失败边界和 no-write 边界。当前 `termination_proof_status=module_stage_termination_proof_complete`、`termination_pass_rate=1.0`、`termination_proof_row_count=7`，但该证明只说明架构阶段门可关闭，不升级任何 synthetic/template/literature 结论为 field evidence，且 `can_write_to_actuator=False`、`can_write_to_release_gate=False`。`experiments/run_agent50_model_core_governance.py` 已把 proof 摘要写入 manifest。验证：新增单测红绿通过，Agent50/阶段边界 targeted tests `76 passed`，完整回归 `660 passed`，CodeGraph fallback 刷新为 `409 files / 5462 nodes / 8615 edges`。边界：R8u180 只增强验证治理层、阶段终止可解释性和可保护性，不生成 field evidence，不改变 action 排序，不恢复模型链，不输出法律/专利结论，不写 actuator/release gate。
- 2026-06-22 新增 `R8u179_stage_boundary_claim_basis_promotion_snapshot`：承接 R8u178 后，本轮没有新增新的模型主张，而是把 `claim_basis_promotion_gate` 回接到最高恢复入口 `stage_boundary_external_action_board`，避免后续 agent 只读 stage board 时漏掉“所有 field claim upgrade 仍被真实 field validation 阻断”的事实。`build_stage_boundary_external_action_board()` 现在接收 `claim_basis_promotion_gate`，输出 `claim_basis_promotion_snapshot`；`experiments/run_stage_boundary_external_action_board.py` 与 `experiments/run_agent50_model_core_governance.py` 都已读取统一 field evidence gate 并写入通用/Agent50 manifest 字段。当前 snapshot 状态为 `claim_basis_promotion_blocked_until_field_validation`，`ready_promotion_count=0`、`blocked_promotion_count=5`、`can_emit_field_claim_upgrade=False`、`can_write_to_actuator=False`、`can_write_to_release_gate=False`，stage boundary effect 为 `keep_external_wait_until_real_field_validation_and_human_review`。验证：stage boundary/Agent50 integration/Agent50 governance targeted tests `74 passed`，完整回归 `658 passed`，CodeGraph fallback 刷新为 `409 files / 5457 nodes / 8610 edges`。边界：R8u179 只是最高阶段边界的可见性回接，不生成 field evidence，不改变 action 排序，不恢复模型链，不输出法律/专利结论，不写 actuator/release gate。
- 2026-06-22 新增 `R8u178_claim_basis_promotion_gate`：承接当前 goal 中“专利级成熟度不是保证授权，而是用专利交底标准反推模型清晰度”和“不能把 synthetic/template/literature 误写成 field 结论”的约束，本轮不继续堆内部 synthetic 产物，而是在统一 field evidence gate 内新增 `claim_basis_promotion_gate`。该 gate 将每条统一证据记录转成可机读的主张升级决策行，明确 `current_basis`、`not_current_basis`、`blocked_by`、`allowed_promotion_level`、`next_required_gate` 和 no-write 边界。当前真实项目结果为 `gate_status=claim_basis_promotion_blocked_until_field_validation`、`promotion_decision_count=5`、`ready_promotion_count=0`、`blocked_promotion_count=5`、`can_emit_field_claim_upgrade=False`、`can_write_to_actuator=False`、`can_write_to_release_gate=False`；这说明 source_basis 文献细节可追溯已经完整，但 `field_supported_edge_ratio=0.0`，所有主张升级仍必须等待真实 field package、replay/holdout 和人工复核。Agent50 scorecard 与 manifest 已同步暴露通用和 Agent50 两组 promotion gate 摘要。验证：统一 evidence gate/Agent50 governance/Agent50 integration targeted tests `68 passed`，完整回归 `656 passed`，CodeGraph fallback 刷新为 `409 files / 5450 nodes / 8603 edges`。边界：R8u178 只增强验证治理层、可保护性和证据升级边界，不生成 field evidence，不输出法律/专利结论，不恢复模型链，不写 actuator/release gate。
- 2026-06-22 新增 `R8u176_R8u177_protocol_governance_runtime_gates`：承接桌面 `复杂项目启动前置治理协议_v3_核心版.md`，本轮继续坚持“选择性转译而不是复制协议”。子代理只读审计建议将该 md 中最适合当前工程模型的规则压成两个运行时门控：一是 `stage_boundary_external_action_board` 的 `low_friction_round_gate`，二是 `governance_recovery_integrity_audit` 的 `minimum_traceability_gate`。前者解决自我打断过频、上下文切换成本过高的问题：当前 `gate_status=low_friction_single_action_waiting_for_external_input`、`round_score=1.0`、`selected_action_id=FIELD_ACTIVATION_RESPONSE_FOCUS_HANDOFF_NEXT_ACTION`，只允许保留一个最高价值外部动作，并禁止在真实外部输入前继续内部扩张。后者解决恢复链“依据-人工动作-资源边界-反膨胀规则”是否能互相追溯的问题：当前 `gate_status=minimum_recovery_traceability_pass`、`traceability_score=1.0`、`missing_link_count=0`，但明确只是 `recovery_route_trace_only_not_full_project_traceability_matrix`。同时刷新 Agent60 的 formal search nonlegal review response AI draft boundary，默认 `ai_draft_boundary_gap_count=0`，测试中 AI 草稿会被阻断进入 claim scope patch。验证：核心 targeted tests `126 passed`，完整回归 `652 passed`，CodeGraph fallback 刷新为 `409 files / 5430 nodes / 8582 edges`。边界：本轮只增强验证治理层、低摩擦阶段门和最小追溯能力，不生成 field evidence，不证明现场处理效果，不恢复模型链，不写 actuator/release gate，不输出法律/专利结论。
- 2026-06-22 新增 `R8u175_stage_boundary_subagent_orchestration_probe`：承接桌面 `复杂项目启动前置治理协议_v3_核心版.md` 的第 44 条子代理编排规则，把“环境里列出子代理名称”与“真的可调度、可等待、可集成、可清理”显式分开。R8u173 已把 `subagent_orchestration_probe` 选入协议适配规则，R8u174 已压实 route alignment，但 stage boundary board 和 recovery audit 仍没有机器字段能证明“当前为什么不应该开子代理”，也不能阻断“available/parallel_domains 但没有 tool/spawn/roles 证据”的虚报。本轮按 TDD 新增 stage board、governance audit 和 manifest 契约测试，先确认缺字段时失败，再在 `src/water_ai/stage_boundary_external_action_board.py` 新增 `subagent_orchestration_probe`：当前 `probe_status=subagent_orchestration_not_needed_for_external_wait`、`capability=not_needed`、`strategy=not_needed`、`tool_discovered=False`、`spawn_attempted=False`、`wait_status=not_started`、`open_agent_cleanup_required=False`，并明确 `no_spawn_reason=current_stage_is_external_activation_wait_and_no_parallel_internal_task_is_required`。`src/water_ai/governance_recovery_integrity_audit.py` 新增 `subagent_orchestration_integrity` 检查：若 capability 写成 available 但无 tool_discovered/spawn_attempted，或 strategy 写成 parallel_domains 但无 roles，会把恢复链降为失败并回到 repair route。刷新后 `governance_recovery_integrity_score=1.0`，`numeric_calculation_trace.component_count=8`，通用和 Agent50 manifest 已暴露 subagent probe status、strategy、tool_discovered、spawn_attempted 和 open_cleanup_required。验证：stage-board/governance recovery/Agent50/external/governance/organization targeted tests `107 passed`，完整回归 `646 passed`，CodeGraph fallback 为 `409 files / 5417 nodes / 8569 edges`。边界：R8u175 只增强验证治理层和可演化性，不实际开启子代理，不生成 field evidence，不恢复模型链，不写 actuator/release gate，不输出法律/专利结论。
- 2026-06-22 新增 `R8u174_extended_route_alignment_recovery_gate`：承接 R8u173 后，继续压实恢复链审计的“机器看版不漂移”能力。R8u173 已让 `recovery_integrity_score` 可复算，并把协议适配显式写入 `governance_recovery_integrity_audit`，但 `_route_alignment()` 仍只比对 next_route、source env var、manual action 和 forbidden basis；如果 manifest 中的 `route_event`、`next_route_validation_command` 或 `current_basis_refs` 陈旧，旧审计仍会误判通过。本轮按 TDD 新增负例 `test_governance_recovery_integrity_audit_fails_on_extended_route_alignment_drift`，先证明旧审计在 route_event/validation command/current_basis 漂移时仍输出 `manifest_stage_board_route_alignment=1.0`，再扩展 `src/water_ai/governance_recovery_integrity_audit.py`，把 `latest_stage_boundary_external_action_board_machine_handoff_route_event`、`latest_stage_boundary_external_action_board_machine_handoff_next_route_validation_command`、`latest_stage_boundary_external_action_board_machine_handoff_current_basis_refs` 和 `latest_stage_boundary_external_action_board_machine_handoff_not_current_basis_refs` 纳入 alignment gate；同时更新 `experiments/run_stage_boundary_external_action_board.py` 与 `experiments/run_agent50_model_core_governance.py`，让 manifest 的通用/Agent50 handoff 摘要都暴露 validation command。刷新后 `outputs/model_core_governance/governance_recovery_integrity_audit.json` 仍显示 `manifest_stage_board_route_alignment=1.0`、`blockers=[]`、`stale_or_mismatch_fields=[]`，但现在这是更强合同下的通过。验证：governance recovery/Agent50/stage-board/external/governance/organization targeted tests `104 passed`，完整回归 `643 passed`，CodeGraph fallback 为 `409 files / 5410 nodes / 8562 edges`。边界：R8u174 只增强验证治理层的恢复一致性与 stale route 防护，不生成 field evidence，不恢复模型链，不写 actuator/release gate，不输出法律/专利结论。
- 2026-06-22 新增 `R8u173_protocol_adapted_recovery_integrity_trace`：承接桌面 `复杂项目启动前置治理协议_v3_核心版.md`，本轮没有把完整十阶段协议复制进项目，也没有新增线性治理 agent，而是把最适合当前工程模型的规则压入 `governance_recovery_integrity_audit` 这个恢复链入口。按 TDD 先让 `tests/test_governance_recovery_integrity_audit.py` 和 `tests/test_agent50_core_interface_integration.py` 因缺少 `numeric_calculation_trace/protocol_adaptation` 失败，再更新 `src/water_ai/governance_recovery_integrity_audit.py` 与 `experiments/run_governance_recovery_integrity_audit.py`。当前审计新增 `numeric_calculation_trace`：`trace_id=R8u173_recovery_integrity_numeric_calculation_trace`、`score_formula=mean(check_scores)`、`component_count=7`、`reported_score=1.0`、`computed_score=1.0`、`score_delta=0.0`、`trace_pass=True`，证明恢复完整性分数可由七个检查项复算；同时新增 `protocol_adaptation`：`adaptation_id=R8u173_complex_project_protocol_to_engineering_model_adapter`、`adaptation_status=selected_protocol_rules_integrated_into_recovery_gate`，选择性吸收 `current_basis_contract/resource_boundary_contract/numeric_calculation_trace/dynamic_stage_handoff/micro_task_execution_check/subagent_orchestration_probe` 六条规则，延后 `live_project_pool_scan/full_traceability_matrix/rendered_artifact_freshness/real_project_pressure_test_gate` 四条规则，`anti_protocol_bloat_gate=pass_selective_adoption_not_full_protocol_copy`。manifest 已同步暴露通用与 Agent50 两组 numeric trace/protocol adaptation 字段。子代理只读审计结果已被部分采纳：接入点为恢复链审计，`subagent_orchestration_probe` 后续可升级为独立 check，但本轮先不扩大范围。验证：governance recovery/Agent50/stage-board/external/governance/organization targeted tests `103 passed`，完整回归 `642 passed`，CodeGraph fallback 为 `409 files / 5408 nodes / 8560 edges`。边界：R8u173 只增强验证治理层的可复算、可恢复和反膨胀能力，不生成 field evidence，不恢复模型链，不写 actuator/release gate，不输出法律/专利结论。
- 2026-06-22 新增 `R8u172_governance_recovery_integrity_audit`：承接 R8u171 后，把“资源边界完整”继续提升为“跨产物恢复链一致性可计算”。R8u171 已让 stage boundary action board 显式区分 allowed/forbidden/supplementary/gray-zone resources，但子代理审计指出更高阶风险是 manifest、stage board、validation command、basis boundary、resource boundary 与 no-write boundary 在长期迭代中漂移。本轮按 TDD 新增 `tests/test_governance_recovery_integrity_audit.py` 和 manifest 契约测试，再新增 `src/water_ai/governance_recovery_integrity_audit.py` 与 `experiments/run_governance_recovery_integrity_audit.py`。当前 `outputs/model_core_governance/governance_recovery_integrity_audit.json` 显示 `audit_id=R8u172_governance_recovery_integrity_audit`、`audit_status=recovery_integrity_pass_waiting_for_real_external_input`、`recovery_integrity_score=1.0`、`recovery_integrity_stage_pass=True`、`blockers=[]`、`stale_or_mismatch_fields=[]`、`safe_next_route=submit_real_external_input_then_rerun_stage_preflight_and_agent50`；七个检查项 `manifest_stage_board_route_alignment/validation_command_exists/manifest_pointer_freshness/manual_action_contract_integrity/basis_boundary_integrity/resource_boundary_integrity/no_write_boundary_integrity` 均为 `1.0`，`change_inventory` 确认 stage board JSON、Markdown、focused catalyst validation command 和 manifest 均存在。验证：governance recovery/Agent50/stage-board/external/governance/organization targeted tests `103 passed`，完整回归 `642 passed`，CodeGraph fallback 为 `409 files / 5404 nodes / 8555 edges`。边界：R8u172 只证明恢复链一致性和 no-write 保护仍成立，不能生成 field evidence、不能恢复模型链、不能写 actuator/release gate，也不能输出法律/专利结论。
- 2026-06-22 新增 `R8u171_stage_boundary_resource_boundary_gate`：在借鉴桌面 `复杂项目启动前置治理协议_v3_核心版.md` 时，本轮没有复制整套十阶段协议，而是把最适合当前工程模型的 `resource_boundary` 思想压入最高恢复入口 `stage_boundary_external_action_board`。R8u170 已证明机器 handoff 合同完整，但仍缺少“哪些资源能作为当前依据、哪些只能作为模板/背景/方法先验、哪些明确禁止升级为 field evidence”的可计算边界。本轮按 TDD 新增失败测试，再在 `src/water_ai/stage_boundary_external_action_board.py` 中新增 `resource_boundary` 与 `resource_boundary_gate`：当前 `boundary_id=R8u171_stage_boundary_resource_boundary`、`gate_id=R8u171_stage_boundary_resource_boundary_gate`、`gate_status=resource_boundary_complete_waiting_for_real_external_input`、`resource_boundary_score=1.0`、`resource_boundary_stage_pass=True`；七个维度 `allowed_basis/forbidden_basis/supplementary_basis/gray_zone/tool_policy/manual_annotation_policy/no_write_policy` 均达到 `1.0`，并明确禁止 `template_rows_as_field_evidence`、`synthetic_rows_as_field_evidence`、`literature_only_rows_as_field_evidence`、未通过预检的自声明候选、formal-search handoff 作为法律/专利意见，以及下游 gate 前写 actuator/release。Markdown 报告和 manifest 已同步暴露通用与 Agent50 两组 resource boundary 摘要。验证：stage-board/Agent50/external/governance/organization targeted tests `101 passed`，完整回归 `640 passed`，CodeGraph fallback 为 `405 files / 5369 nodes / 8494 edges`。边界：R8u171 只增强资源依据边界与证据泄漏防护，不能证明 field evidence、模型链恢复、执行器可写、release gate 可写或法律/专利结论；子代理审计指出下一步更高阶缺口是全局 `governance_recovery_integrity_audit/change_inventory`，用于检查 manifest、board、validation command 和 stale artifacts 的跨产物一致性。
- 2026-06-22 新增 `R8u170_stage_boundary_machine_handoff_contract_gate`：承接 R8u169 后，把 action board 的 `machine_handoff` 从“字段完整”升级为“可计算合同门”。R8u169 已经能让后续 agent 直接恢复 `route_event/next_route/current_basis/not_current_basis/manual_action_required/can_prove/cannot_prove`，但仍缺少一个机器可读的 completeness gate 来判断“这个 handoff 是否真的够用于低摩擦恢复”。本轮按 TDD 新增失败测试，再在 `src/water_ai/stage_boundary_external_action_board.py` 中新增 `machine_handoff_contract_gate`：当前 `gate_id=R8u170_stage_boundary_machine_handoff_contract_gate`、`gate_status=machine_handoff_contract_complete_waiting_for_external_input`、`contract_score=1.0`、`contract_stage_pass=True`；六个合同维度 `route_contract_completeness/manual_action_contract_completeness/basis_boundary_completeness/proof_boundary_completeness/no_write_boundary_completeness/recovery_linkage_completeness` 均为 `1.0`，`contract_blockers=[]`，但 `external_wait_blockers=[real_external_input_required]`。Markdown 报告和 manifest 已同步暴露该 gate。验证：stage-board/Agent50/external/governance/organization targeted tests `99 passed`，完整回归 `638 passed`，CodeGraph fallback 为 `405 files / 5361 nodes / 8486 edges`。边界：R8u170 只证明机器 handoff 合同完整，不能证明 field evidence、模型链恢复、执行器可写、release gate 可写或法律/专利结论。
- 2026-06-22 新增 `R8u169_stage_boundary_machine_handoff_contract`：承接 R8u168 后继续吸收桌面复杂项目治理协议的“机器看版 handoff、current_basis/not_current_basis、manual_action_required、低摩擦恢复入口”思想，把 `stage_boundary_external_action_board` 从外部行动列表升级为可独立恢复的机器看版入口。R8u168 已让 action board 显示 external package acquisition 为什么不能结束，但仍缺少 `route_event/next_route/current_basis_refs/not_current_basis_refs/manual_action_required/can_prove/cannot_prove`；后续只读 action board 或 manifest 的 agent 仍需要回扫上下游来判断“当前是外部等待态，不是模型可继续态”。本轮按 TDD 新增失败测试，再更新 `src/water_ai/stage_boundary_external_action_board.py`：新增 `machine_handoff`，当前 `route_event=external_activation_wait`、`next_route=submit_real_external_input_then_rerun_stage_preflight_and_agent50`、`next_route_source_env_var=FOCUSED_CATALYST_RESPONSE_PATH`、`manual_action_required.required=True`，并显式区分 current basis、not current basis、can prove 和 cannot prove；Markdown 报告新增 `## Machine Handoff`。同时更新 `experiments/run_stage_boundary_external_action_board.py` 与 `experiments/run_agent50_model_core_governance.py`，把 handoff 摘要写入通用和 Agent50 manifest 字段。验证：stage-board/Agent50/external/governance/organization targeted tests `97 passed`，完整回归 `636 passed`，CodeGraph fallback 为 `405 files / 5352 nodes / 8477 edges`。边界：R8u169 只增强验证治理层和工程交接层的状态恢复能力；不生成 field evidence，不恢复模型链，不写 actuator/release gate，不输出法律/专利结论。
- 2026-06-22 新增 `R8u168_stage_board_surfaces_external_package_acquisition_termination`：借鉴桌面 `复杂项目启动前置治理协议_v3_核心版.md` 中“机器看版 handoff、next_route 不漂移、current_basis/not_current_basis 分层、阶段门控和低摩擦恢复入口”的思想，把 R8u167 已进入 core gate 的 external package acquisition 终止快照继续回接到操作者最高入口 `stage_boundary_external_action_board`。R8u167 后，`core_score_termination_gate.json` 和 `priority_ranking.json` 已能看到 `contract_termination_status/module_stage_termination_pass/termination_blockers`，但 `outputs/model_core_governance/stage_boundary_external_action_board.json`、对应 Markdown 和 manifest 仍只显示 `NEW_CORE_INTERFACE` 的灰箱包候选，不显示为什么 acquisition 阶段不能结束；后续 agent 或操作者若只看 action board，仍会丢失“接口合同完整但真实现场包未就绪”的阻断原因。本轮按 TDD 先新增失败测试，再更新 `src/water_ai/stage_boundary_external_action_board.py`，让 `NEW_CORE_INTERFACE` action row、`action_summary`、`operator_runbook` 与 Markdown 同步显示 `new_core_interface_acquisition_contract_termination_status=external_package_contracts_complete_but_waiting_for_field_packages`、`module_stage_termination_pass=False`、`downstream_reconnection_rate=0.0`、`field_package_ready_rate=0.0` 和 termination blockers；同时更新 `experiments/run_stage_boundary_external_action_board.py` 与 `experiments/run_agent50_model_core_governance.py`，把同组字段写入通用和 Agent50 manifest 摘要。验证：stage-board/Agent50/external/governance/organization targeted tests `95 passed`，完整回归 `634 passed`，CodeGraph fallback 为 `405 files / 5345 nodes / 8470 edges`。边界：R8u168 只增强验证治理层和工程交接层的可恢复性；不提高 core_score，不生成 field evidence，不恢复模型链，不写 actuator/release gate。
- 2026-06-22 新增 `R8u167_core_gate_consumes_external_package_acquisition_termination`：承接 R8u166 后，把 external package acquisition 的可计算终止快照回接到最高核心阶段门。R8u166 已让 `external_package_acquisition_maturity_gate.json` 和 manifest 能判断“接口合同完整但等待真实现场包”，但 `core_score_termination_gate.json` 与 `priority_ranking.json` 仍看不到 `contract_termination_status/module_stage_termination_pass/termination_blockers`，导致后续只读主治理入口的 agent 还要回扫深层 acquisition gate。本轮按 TDD 新增 artifact-level 测试，先确认 `core_score_termination_gate.json` 缺 `external_package_acquisition_stage_gate` 后失败；随后在 `experiments/run_agent50_model_core_governance.py` 中新增 acquisition stage snapshot 回接，把 `contract_termination_status=external_package_contracts_complete_but_waiting_for_field_packages`、`module_stage_termination_pass=False`、`downstream_reconnection_rate=0.0`、`field_package_ready_rate=0.0` 和两个 termination blockers 同步写入 `core_score_termination_gate.external_package_acquisition_stage_gate`、`external_resume_conditions.external_package_acquisition_stage_gate`、`external_resume_conditions.new_core_interface.external_package_acquisition_*` 以及 `priority_ranking.external_package_acquisition_stage_gate`。验证：external/Agent50/core/grey-box/governance targeted tests `105 passed`，完整回归 `632 passed`，CodeGraph fallback 为 `405 files / 5340 nodes / 8465 edges`。边界：R8u167 只增强主治理入口的可恢复性和可验证性；不提高 core_score，不生成 field evidence，不恢复模型链，不写 actuator/release gate。
- 2026-06-22 新增 `R8u166_external_package_acquisition_goal_termination_metrics`：承接 R8u165 后，把 external package acquisition gate 从“接口成熟度分数”升级为可直接对应当前 goal 的模块终止门。R8u165 已能说明 operator packet 当前是 `external_activation_wait`，但 acquisition gate 仍缺 `input/output contract completeness`、`handoff_state_variable_coverage`、`downstream_reconnection_rate`、`evidence/failure/no-write boundary completeness`、`contract_termination_status` 和 `termination_blockers` 等可计算终止字段，后续 agent 仍需人工判断“接口完整但不能结束”。本轮按 TDD 给 `build_external_package_acquisition_maturity_gate()` 增加显式 `termination_thresholds` 与同名指标；当前结果为 `input_contract_completeness=1.0`、`output_contract_completeness=1.0`、`handoff_state_variable_coverage=1.0`、`evidence_boundary_completeness=1.0`、`failure_boundary_completeness=1.0`、`no_write_boundary_completeness=1.0`，但 `downstream_reconnection_rate=0.0`、`field_package_ready_rate=0.0`，所以 `contract_termination_status=external_package_contracts_complete_but_waiting_for_field_packages`、`module_stage_termination_pass=False`、`termination_blockers=[downstream_reconnection_rate_below_0.80, field_package_ready_rate_below_1.00]`。`experiments/run_external_package_readiness_board.py` 与 `experiments/run_agent50_model_core_governance.py` 已把这些字段写入 manifest，后续只读 manifest 也能判断阶段不能终止。验证：external/Agent50/core/grey-box/governance targeted tests `104 passed`，完整回归 `631 passed`，CodeGraph fallback 为 `405 files / 5337 nodes / 8462 edges`。边界：`handoff_state_variable_coverage` 只代表外部包交接状态字段完整，不代表污染过程隐藏状态已现场验证；本轮不生成 field evidence，不恢复模型链，不写 actuator/release gate。
- 2026-06-22 新增 `R8u165_external_package_operator_machine_handoff_semantics`：承接 R8u164 后继续把外部真实包等待态做成可恢复、可计算的机器看版入口。R8u164 已让 operator packet 直接显示灰箱五张缺表，但仍缺 `route_event/current_basis/not_current_basis/manual_action_required/evidence_level/can_prove/cannot_prove` 这类治理语义；后续只读 packet 或 manifest 的 agent 仍需要人工判断“这是外部等待、不是 field evidence”。本轮按 TDD 给 `external_package_operator_action_packet` 增加机器交接字段：当前 `route_event=external_activation_wait`、`route_reason=waiting_for_real_external_package_before_downstream_replay_holdout_calibration`、`evidence_level=operator_handoff_only_not_field_evidence`、`manual_action_required.required=True`，并显式列出 current basis、not current basis、能证明的内容和不能证明的内容。`experiments/run_external_package_readiness_board.py` 与 `experiments/run_agent50_model_core_governance.py` 已把这些字段写入 manifest，保证低摩擦恢复入口不丢语义。验证：external/Agent50/core/grey-box/governance targeted tests `103 passed`，完整回归 `630 passed`，CodeGraph fallback 为 `405 files / 5329 nodes / 8454 edges`。边界：R8u165 只增强验证治理层和外部执行交接的状态恢复能力；不生成 field evidence，不改变 `readiness_score=0.143`，不恢复模型链，不写 actuator/release gate。
- 2026-06-22 新增 `R8u164_external_package_operator_missing_table_projection` 并吸收轻量工程治理适配：承接 R8u163 后继续降低真实灰箱包提交的 scan 摩擦。R8u163 已让 manifest 暴露 `missing_table_count=5` 和五张灰箱校准缺表，但 operator-facing 的 `external_package_readiness_board.json` 与 `external_package_operator_action_packet.json` 仍只显示模板、env var 和验证命令，现场执行者仍要回查 grey-box submission gate 或 manifest 才知道具体补哪几张表。本轮按 TDD 新增 `attach_submission_readiness_gap()`，让 external package runner 和 Agent50 runner 从 `outputs/grey_box_calibration_package/grey_box_submission_readiness_gate.json` 读取 `highest_priority_gap`，并投影到 readiness board、operator action、operator packet 顶层摘要和 manifest。现在 `outputs/model_core_governance/external_package_operator_action_packet.json` 直接显示 `next_operator_submission_gap_type=missing_external_package`、`next_operator_missing_table_count=5`、五张表 `batch_inlet_outlet_lab / hydraulic_rtd_or_tracer / oxidant_dose_residual_log / catalyst_age_regeneration_log / byproduct_panel`、模板目录和 preflight 命令。另参考桌面 `复杂项目启动前置治理协议_v3_核心版.md`，新增 `deliverables/model_core_optimization/engineering_model_governance_adapter.md`，只吸收 current_basis/not_current_basis、紧凑路由事件、Plan/Goal 纪律、人看/机器看分层、manual_action_required 边界、工具搜索规则、子代理边界和 anti-bloat gate；不照搬十阶段协议、不新增治理 agent。验证：external/Agent50/core/grey-box/governance targeted tests `102 passed`，完整回归 `629 passed`，CodeGraph fallback 为 `405 files / 5323 nodes / 8448 edges`。边界：R8u164 只增强外部真实包提交入口的工程可执行性和状态恢复能力；不改变 `readiness_score=0.143`，不生成 field evidence，不恢复模型链，不写 actuator/release gate。
- 2026-06-22 新增 `R8u163_manifest_grey_box_missing_table_contract`：承接 R8u162 后继续减少真实灰箱包提交的 scan 摩擦。R8u162 已让 grey-box submission readiness gate 与 core interface 都能表达 `missing_table_count=5` 和五张缺失表清单，但 `deliverables/manifest.json` 仍只暴露 `highest_priority_gap_type/table`，导致只读 manifest 的后续 agent 还需要回查 JSON 才知道具体该补哪些表。本轮按 TDD 修复 manifest 摘要合同：`experiments/run_grey_box_calibration_package_preflight.py` 现在写入 `latest_grey_box_submission_readiness_missing_table_count`、`latest_grey_box_submission_readiness_missing_tables`、`latest_grey_box_submission_readiness_source_env_var`；`experiments/run_agent50_model_core_governance.py` 同步写入 `latest_agent50_grey_box_submission_readiness_*` 与 `latest_core_interface_consolidation_grey_box_submission_*` 三组缺表字段；`experiments/run_core_interface_consolidation.py` 也为独立 core-interface runner 写入相同 core 摘要。`tests/test_agent50_core_interface_integration.py` 已锁定 manifest 三层字段必须与 `grey_box_submission_readiness_gate.json` 一致。刷新后，manifest 直接暴露三层 `missing_table_count=5`、`missing_tables=[batch_inlet_outlet_lab, hydraulic_rtd_or_tracer, oxidant_dose_residual_log, catalyst_age_regeneration_log, byproduct_panel]` 和 `source_env_var=GREY_BOX_CALIBRATION_PACKAGE_DIR`。验证：相关单测通过，core/grey-box/Agent50/组织/治理 targeted tests `91 passed`，完整回归 `627 passed`，CodeGraph fallback 为 `404 files / 5309 nodes / 8431 edges`。边界：R8u163 只增强 manifest 作为项目入口的工程可执行性和可验证性；不改变 `readiness_score=0.143`，不生成 field evidence，不恢复模型链，不写 actuator/release gate。
- 2026-06-22 新增 `R8u162_grey_box_missing_package_gap_specificity`：承接 R8u161 后的证据边界细化。R8u161 已让 core interface 消费 grey-box submission readiness gate，但默认无外部包时，`highest_priority_gap.table` 仍为空字符串；这会让 manifest/core interface 只知道缺 `GREY_BOX_CALIBRATION_PACKAGE_DIR`，却不能机器可读地说明五张灰箱校准表全部缺失。本轮没有新增 agent，也没有继续内部 synthetic 扩张，而是修正 `src/water_ai/grey_box_calibration_package.py` 的 `_highest_priority_submission_gap()`：当 `external_package_supplied=False` 时，gap 现在输出 `table=all_required_tables`、`missing_table_count=5`、`missing_tables=[batch_inlet_outlet_lab, hydraulic_rtd_or_tracer, oxidant_dose_residual_log, catalyst_age_regeneration_log, byproduct_panel]` 和 `source_env_var=GREY_BOX_CALIBRATION_PACKAGE_DIR`。同时 `grey_box_submission_readiness_gate_report_md()` 会在报告中显示缺表数量/清单，`src/water_ai/core_interface_consolidation.py` 会把 `submission_missing_table_count`、`submission_missing_tables` 和 `submission_source_env_var` 投影到 `external_package_lifecycle.grey_box_calibration` 行。刷新后，`outputs/grey_box_calibration_package/grey_box_submission_readiness_gate.json`、`outputs/model_core_governance/core_interface_consolidation.json`、Agent50 payload 与 manifest 均显示最高缺口为 `missing_external_package / all_required_tables / 5 tables`。验证：灰箱/core-interface/Agent50/组织/治理 targeted tests `91 passed`，完整回归 `627 passed`，CodeGraph fallback 为 `404 files / 5309 nodes / 8431 edges`。边界：R8u162 只增强外部真实包提交缺口的可读性和机器可路由性；`readiness_score` 仍为 `0.143`，不生成 field evidence，不证明灰箱机理，不恢复模型链，不写 actuator/release gate。
- 2026-06-22 新增 `R8u161_core_interface_consumes_grey_box_submission_readiness_gate`：承接 R8u160 后的核心接口断点。R8u160 已生成灰箱包 submission readiness gate，Agent50 也能读取 gate；但如果该 gate 没有进入 `core_interface_consolidation` 的 `external_package_lifecycle` facade，后续只读核心接口的 agent/人仍可能看到“灰箱包等待中”，却看不到“提交成熟度分数、最高缺口、是否可进入 Agent53”的统一门控结果。本轮按子代理协同审计推进：Banach/Kepler/Halley 分别检查 core facade、Agent50 runner 和测试/产物消费证明；结论是源码应把 `grey_box_submission_readiness_gate` 投影到 `grey_box_calibration` lifecycle row，产物必须刷新并用 artifact/manifest tests 锁住。现已更新 `src/water_ai/core_interface_consolidation.py`，让 `build_core_interface_consolidation()` 接收 `grey_box_submission_readiness_gate`，并在灰箱生命周期行写入 `submission_readiness_gate_status`、`submission_readiness_score`、`submission_highest_priority_gap_type/table`、`can_submit_to_agent53_field_calibration`、`can_submit_to_agent53_field_candidate` 和 no-write 边界字段；`experiments/run_core_interface_consolidation.py` 与 `experiments/run_agent50_model_core_governance.py` 已同步读取并传递 `outputs/grey_box_calibration_package/grey_box_submission_readiness_gate.json`，manifest 也新增 `latest_core_interface_consolidation_grey_box_submission_*` 摘要字段。当前 core interface 产物显示 `grey_box_submission_readiness_waiting_for_external_package / 0.143`，最高缺口仍为 `missing_external_package`，两个 Agent53 submit flags 均为 False。新增/强化 `tests/test_core_interface_consolidation.py` 与 `tests/test_agent50_core_interface_integration.py`，覆盖源码契约、core artifact、Agent50 payload 和 manifest 对齐。验证：相关测试 `25 passed`，core/grey-box/Agent50/组织/治理 targeted tests `91 passed`，完整回归 `627 passed`，CodeGraph fallback 刷新为 `404 files / 5309 nodes / 8431 edges`。边界：R8u161 是接口回接和消费证明，不生成 field evidence，不证明灰箱机理，不恢复模型链，不写 actuator/release gate；下一步最高外部动作仍是提交真实 `GREY_BOX_CALIBRATION_PACKAGE_DIR` 五表包。
- 2026-06-22 新增 `R8u160_grey_box_submission_readiness_gate`：承接 R8u159 后的最高外部证据动作。R8u159 已让 Agent50 消费 `core_interface_consolidation`，而该 facade 与 external package acquisition gate 都指向 `GREY_BOX_CALIBRATION_PACKAGE_DIR`；但此前灰箱包只有 preflight、field calibration summary 和 collection work order，缺少一个统一的“提交成熟度分数/最高缺口/是否可进入 Agent53”的可计算 gate。现已在 `src/water_ai/grey_box_calibration_package.py` 中新增 `build_grey_box_submission_readiness_gate()` 与 `grey_box_submission_readiness_gate_report_md()`，把 source package、schema completeness、field origin integrity、matched batch coverage、signal validity coverage、Agent53 summary readiness、residual threshold readiness 和 no-write boundary integrity 压成 `readiness_score`。`experiments/run_grey_box_calibration_package_preflight.py` 现在生成 `outputs/grey_box_calibration_package/grey_box_submission_readiness_gate.json` 与 `deliverables/model_core_optimization/grey_box_submission_readiness_gate.md`，并回写 manifest；`experiments/run_agent50_model_core_governance.py` 已消费该 gate，在 Agent50 report、payload、generated files 和 manifest 中暴露 `grey_box_submission_readiness_gate_status`、`readiness_score` 和 `highest_priority_gap`。当前默认未提交外部包，所以 `gate_status=grey_box_submission_readiness_waiting_for_external_package`、`readiness_score=0.143`、`highest_priority_gap=missing_external_package`、`can_submit_to_agent53_field_calibration=False`、`can_submit_to_agent53_field_candidate=False`。这轮解决的是“真实包提交前缺少可计算终止/准入指标”的验证治理缺口，不生成 field evidence，不恢复模型链，不写 actuator/release gate。验证：灰箱包/Agent50/产物组织/外部包/core-interface/治理 targeted tests `96 passed`，完整回归 `623 passed`，CodeGraph 刷新为 `404 files / 5301 nodes / 8422 edges`。下一步仍是补齐 `GREY_BOX_CALIBRATION_PACKAGE_DIR` 五表真实包；若已有 catalyst 真实记录，再作为次级路径补 focused catalyst response。
- 2026-06-22 新增 `R8u159_agent50_refreshes_core_interface_consolidation_facade`：承接 R8u158 后的主链回接缺口。R8u158 已生成 `core_interface_consolidation` facade，但如果只停留在单独 runner 和 manifest 指针里，Agent50 后续治理仍可能继续按旧推荐队列运行，导致“核心接口收束”和“全局治理入口”脱链。本轮按用户要求开启子代理协同：Nash 审查代码接入，确认 `experiments/run_agent50_model_core_governance.py` 已构建、写盘、写入 report/payload/manifest，且 helper 签名一致；Leibniz 审查产物一致性，指出缺少 R8u159 版本锚点和 `consumed/refresh_status` 明示字段；Singer 审查全局边际价值，判断下一轮最高价值不是继续堆 synthetic agent，而是优先提交 `GREY_BOX_CALIBRATION_PACKAGE_DIR` 灰箱校准真实包，其次才是 `catalyst_activity` focused field response。现已让 Agent50 runner 直接调用 `build_core_interface_consolidation()`，自动刷新 `outputs/model_core_governance/core_interface_consolidation.json` 和 `deliverables/model_core_optimization/core_interface_consolidation.md`，并在 Agent50 Markdown/JSON 与 manifest 中暴露 `core_interface_consolidation_consumed_by_agent50=True`、`core_interface_consolidation_refresh_status=agent50_runner_refreshed_current_facade`、`top_external_action_env_var=GREY_BOX_CALIBRATION_PACKAGE_DIR`、`new_agent_recommendation=do_not_add_linear_agent`。同时新增 `tests/test_agent50_core_interface_integration.py`，并把 deliverable organization 的 governance package 索引扩展到 core interface JSON/Markdown，防止该 facade 再次成为孤立产物。验证：py_compile 通过；`.venv/bin/python experiments/run_agent50_model_core_governance.py` 通过；core-interface/Agent50/组织/外部包/Agent48 targeted tests `113 passed`；完整回归 `618 passed`；CodeGraph 刷新为 `403 files / 5280 nodes / 8395 edges`。边界：R8u159 是 Agent50 消费/刷新集成层，R8u158 仍是 facade 本体 ID；它不生成 field evidence，不恢复模型链，不放松 Agent49 guardrail，不写 actuator/release gate。下一步的最高外部证据动作应优先补齐 `GREY_BOX_CALIBRATION_PACKAGE_DIR` 五表真实包并运行 grey-box preflight；Agent50 旧推荐队列中的 catalyst focused handoff 保留为次级补证路径。
- 2026-06-22 新增 `R8u158_core_interface_consolidation_facade`：承接本轮子代理协同复盘。Mendel 审计现有 agent 链条，判断项目不应继续按 1-61 线性 agent 增长，而应压成七层骨架下的少数 facade/schema；Euclid 审计 Agent48，指出下一步不是再堆布点算法，而是把稀疏布点策略、missingness 与软传感评价放进同一张可比较 benchmark；Gauss 审计 Agent49/52，指出多设施协同控制仍是候选控制层，最小增益是把 `FIELD_CONTROL_REPLAY_PACKAGE_DIR` 五表映射到 Agent52 replay schema。现已新增 `src/water_ai/core_interface_consolidation.py`、`experiments/run_core_interface_consolidation.py` 和 `tests/test_core_interface_consolidation.py`，生成 `outputs/model_core_governance/core_interface_consolidation.json` 与 `deliverables/model_core_optimization/core_interface_consolidation.md`。该 facade 同时输出三块核心接口：`external_package_lifecycle` 将灰箱校准、field control replay、sparse topology/installability 三类外部包压成统一生命周期行；`sparse_layout_soft_sensor_coupling_benchmark` 对 Agent48 六类策略生成布点-软传感耦合评分表，当前最佳为 `reconstruction_qr_proxy`，但 `catalyst_activity`、pressure/headloss、field topology 和 field missingness replay 仍是硬阻断；`field_control_replay_crosswalk` 将 `state_action_next_state_rows`、`reward_component_rows`、`operator_or_expert_action_labels`、`actuator_latency_and_result_rows`、`unsafe_action_or_override_events` 映射到 Agent52 replay schema 和 release gate 条件。当前结论：`top_external_action_env_var=GREY_BOX_CALIBRATION_PACKAGE_DIR`，`new_agent_recommendation=do_not_add_linear_agent`，内部后续只在真实包、Agent48 layout metrics 或 Agent52 replay schema 变化时刷新 facade。验证：R8u158 单测 `5 passed`，R8u158/外部包/Agent48/field-control targeted tests `45 passed`，完整回归 `616 passed`，CodeGraph 刷新为 `402 files / 5277 nodes / 8384 edges`。边界：R8u158 是接口收束和 synthetic/interface benchmark，不生成 field evidence，不恢复模型链，不放松 Agent49 guardrail，不写 actuator/release gate。
- 2026-06-22 新增 `R8u157_grey_box_calibration_collection_work_order`：承接 R8u156 的阶段门结论。R8u156 已证明五个外部包的采集接口和 operator action contract 成熟，但 `field_package_ready_rate=0.0`，下一步必须优先补 `GREY_BOX_CALIBRATION_PACKAGE_DIR`，不能继续内部 synthetic 扩张。现已在 `src/water_ai/grey_box_calibration_package.py` 中新增 `build_grey_box_calibration_collection_work_order()` 与 `grey_box_calibration_collection_work_order_report_md()`，并让 `experiments/run_grey_box_calibration_package_preflight.py` 生成 `outputs/grey_box_calibration_package/grey_box_calibration_collection_work_order.json` 与 `deliverables/model_core_optimization/grey_box_calibration_collection_work_order.md`。该工单把灰箱校准包拆成五张表级采集项：`batch_inlet_outlet_lab`、`hydraulic_rtd_or_tracer`、`oxidant_dose_residual_log`、`catalyst_age_regeneration_log`、`byproduct_panel`，逐表列出模板 CSV、必填列、共同 `batch_id`、最小 3 个共同批次、`data_origin=field`、QA 要求、当前行数/有效行数、模板标记、non-field 行和 repair 状态。当前 `work_order_status=grey_box_calibration_collection_work_order_waiting_for_external_package`、`table_work_item_count=5`、`matched_batch_count=0`、`field_package_ready_for_agent53=False`、`agent53_field_candidate_ready=False`，下一步仍是填写模板并设置 `GREY_BOX_CALIBRATION_PACKAGE_DIR` 后运行 `.venv/bin/python experiments/run_grey_box_calibration_package_preflight.py`。Agent50 generated files、Agent50 payload 和 manifest 已消费该工单。验证：grey-box 单测 `9 passed`，grey-box/external-package/new-core/action-board/Agent50 targeted tests `72 passed`，完整回归 `611 passed`，CodeGraph 刷新为 `398 files / 5234 nodes / 8316 edges`。边界：R8u157 只是最高优先级外部真实包的采集/修复工单；它不生成 field evidence，不运行 Agent53 field calibration，不恢复模型链，不写 actuator/release gate，也不能输出 field-supported mechanism claim。
- 2026-06-22 新增 `R8u156_external_package_acquisition_maturity_gate`：承接 R8u154 readiness board 与 R8u155 operator action packet，把五个外部真实包采集入口从“可看、可执行”进一步压成可计算阶段门。现已在 `src/water_ai/external_package_readiness_board.py` 中新增 `build_external_package_acquisition_maturity_gate()` 与 `external_package_acquisition_maturity_gate_report_md()`，并让 `experiments/run_external_package_readiness_board.py` 和 `experiments/run_agent50_model_core_governance.py` 同步生成 `outputs/model_core_governance/external_package_acquisition_maturity_gate.json` 与 `deliverables/model_core_optimization/external_package_acquisition_maturity_gate.md`。当前 `package_count=5`、`ready_package_count=0`、`waiting_package_count=5`、`blocked_package_count=0`、`unimplemented_package_count=0`；`interface_preflight_coverage=1.0`、`operator_action_contract_coverage=1.0`、`no_write_boundary_integrity=1.0`，但 `field_package_ready_rate=0.0`，所以 `acquisition_maturity_score=0.85` 只表示采集接口和操作合同成熟，不表示 field evidence 成立。Agent50 主报告、payload、generated files 和 manifest 已消费该 gate；下一阶段决策仍是 `collect_external_field_packages_before_downstream_gates`，优先填写 `GREY_BOX_CALIBRATION_PACKAGE_DIR` 并运行 `.venv/bin/python experiments/run_grey_box_calibration_package_preflight.py`。验证：external package board/operator/acquisition gate 单测 `9 passed`，external board/new-core/action-board/Agent50 targeted tests `63 passed`，完整回归 `607 passed`，CodeGraph 刷新为 `397 files / 5210 nodes / 8284 edges`。边界：R8u156 主要增强验证治理层的可验证性、可工程化和可演化性；它不生成 field evidence，不运行 downstream replay/holdout/calibration，不恢复模型链，不写 actuator/release gate，也不能输出 field-supported claim。
- 2026-06-22 新增 `R8u155_external_package_operator_action_packet`：承接 R8u154 的外部包 readiness board。R8u154 已能统一显示五个外部真实数据包入口的 ready/waiting/blocked 状态，但仍偏“看板”，operator/后续 agent 还需要从每行里抽取模板目录、环境变量、验证命令、下一步动作和拒收边界。现已在 `src/water_ai/external_package_readiness_board.py` 中新增 `build_external_package_operator_action_packet()` 与 `external_package_operator_action_packet_report_md()`，并让 `experiments/run_external_package_readiness_board.py` 和 `experiments/run_agent50_model_core_governance.py` 同步生成 `outputs/model_core_governance/external_package_operator_action_packet.json` 与 `deliverables/model_core_optimization/external_package_operator_action_packet.md`。该 packet 将五个包压成有序操作队列，逐项输出 `action_status`、`priority_reason`、`template_dir`、`source_env_var`、`validation_command`、`run_after_submission`、`minimum_row_count`、输入/输出合同和失败边界；当前状态为 `external_package_operator_packet_waiting_for_field_packages`，`package_count=5`、`waiting_package_count=5`、`blocked_package_count=0`，下一步仍是填写灰箱校准包模板、设置 `GREY_BOX_CALIBRATION_PACKAGE_DIR` 并运行 `.venv/bin/python experiments/run_grey_box_calibration_package_preflight.py`。Agent50 主报告、payload、generated files 和 manifest 已消费该 packet。验证：external package board/operator packet 单测 `6 passed`，external board/new-core/action-board/Agent50 targeted tests `60 passed`，完整回归 `604 passed`，CodeGraph 刷新为 `396 files / 5193 nodes / 8262 edges`。边界：R8u155 只是把外部真实包采集/验证动作结构化，不生成 field evidence，不运行 downstream replay/holdout/calibration，不恢复模型链，不写 actuator/release gate。
- 2026-06-22 新增 `R8u154_external_package_readiness_board`：承接 R8u153 后的阶段边界复核。此前 NCI1/NCI5/NCI3/NCI4/NCI2 五个 new-core-interface 候选都已有各自 preflight 或 downstream adapter，但真实外部包状态仍分散在多个 runner、report 和 manifest 字段中；后续 operator/agent 需要重复扫描才能知道“哪个包已 ready、哪个只是等待外部目录、哪个不能恢复模型链”。现新增 `src/water_ai/external_package_readiness_board.py`、`experiments/run_external_package_readiness_board.py`、`tests/test_external_package_readiness_board.py`，生成 `outputs/model_core_governance/external_package_readiness_board.json` 与 `deliverables/model_core_optimization/external_package_readiness_board.md`。该 board 聚合五个外部包：`GREY_BOX_CALIBRATION_PACKAGE_DIR`、`FIELD_SUPPORTED_KG_EDGE_PACKAGE_DIR`、`FIELD_CONTROL_REPLAY_PACKAGE_DIR`、`SPARSE_TOPOLOGY_INSTALLABILITY_PACKAGE_DIR`、`FIELD_MISSINGNESS_REPLAY_PACKAGE_DIR`，逐行输出 candidate、task、source env var、preflight status、matched units、template path、validation command、next operator action 和 no-write 边界；同时按 state estimation/grey-box、mechanism evidence KG、control replay、sparse observation layout、soft-sensor missingness 分组。Agent50 主 runner 已消费该 board，在 Agent50 report、payload、generated files 和 manifest 中暴露 `package_count=5`、`ready_package_count=0`、`waiting_package_count=5`、`blocked_package_count=0`、`unimplemented_package_count=0`、`all_candidate_interfaces_have_preflight=True`，当前下一外部动作仍是补 `GREY_BOX_CALIBRATION_PACKAGE_DIR`。验证：external package board 单测 `3 passed`，external board/new-core/action-board/Agent50 targeted tests `57 passed`，完整回归 `601 passed`，CodeGraph 刷新为 `395 files / 5174 nodes / 8234 edges`。边界：R8u154 只是外部包采集/路由看板，不运行 downstream replay/holdout/calibration，不生成 field evidence，不恢复模型链，不写 actuator/release gate。
- 2026-06-22 新增 `R8u153_field_missingness_replay_package_preflight`：承接 R8u152 后完成 new-core-interface 队列中最后一个未落地的候选 NCI2/P5。Agent54 软传感矩阵耦合已有 synthetic layout/missingness contract，但真实低频采样、传感器脏污、通信中断、校准状态变化下的缺测鲁棒性仍缺少 field missingness replay 入口。现新增 `src/water_ai/field_missingness_replay_package.py`、`experiments/run_field_missingness_replay_preflight.py`、`tests/test_field_missingness_replay_package.py`，生成 `outputs/field_missingness_replay_package/field_missingness_replay_package_preflight.json`、`outputs/field_missingness_replay_package/field_missingness_replay_package_template/` 和 `deliverables/model_core_optimization/field_missingness_replay_package_preflight.md`。该接口要求五张表：`node_modality_time_series`、`availability_mask`、`time_since_last_observed_min`、`sensor_quality_status`、`offline_hidden_state_labels`，并要求至少 3 个共同 `sample_id` 同时通过 field origin、QA、节点-模态时间序列、availability mask、距上次观测时间、传感器质量状态和离线隐藏状态标签检查；同时要求至少 1 个真实 unavailable/missing 样本，防止全 available 数据伪装成 missingness replay。`new_core_interface_candidate_gate` 与 Agent50 generated files 已消费该 preflight；当前默认未设置外部目录，所以 NCI2 行状态为 `field_missingness_replay_package_waiting_for_FIELD_MISSINGNESS_REPLAY_PACKAGE_DIR`、`package_preflight_pass=False`、`matched_sample_count=0`。验证：field-missingness/new-core targeted tests `13 passed`，field-missingness/control/sparse/new-core/action-board/Agent50/Agent54 targeted tests `76 passed`，完整回归 `598 passed`，CodeGraph 刷新为 `391 files / 5144 nodes / 8144 edges`。边界：R8u153 只判断真实缺测回放包是否可进入 Agent54/soft-sensor missingness holdout；不证明 field soft-sensor accuracy，不恢复模型链，不写 actuator/release gate。
- 2026-06-22 新增 `R8u152_field_control_replay_package_preflight`：承接 R8u151 后继续处理剩余高价值 new-core-interface 候选，这次选择 P3/NCI3 的闭环执行层阻断。Agent49/52 多设施协同控制与 replay evaluation 目前仍是 synthetic baseline，缺少可进入离线评估的真实 state-action-next-state、reward、专家动作、执行器延迟和 unsafe/override 记录。现新增 `src/water_ai/field_control_replay_package.py`、`experiments/run_field_control_replay_preflight.py`、`tests/test_field_control_replay_package.py`，生成 `outputs/field_control_replay_package/field_control_replay_package_preflight.json`、`outputs/field_control_replay_package/field_control_replay_package_template/` 和 `deliverables/model_core_optimization/field_control_replay_package_preflight.md`。该接口要求五张表：`state_action_next_state_rows`、`reward_component_rows`、`operator_or_expert_action_labels`、`actuator_latency_and_result_rows`、`unsafe_action_or_override_events`，并要求至少 3 个共同 `transition_id` 同时通过 field origin、QA、状态转移、reward 分量、专家动作标签、执行器延迟一致性和人工复核安全边界。`new_core_interface_candidate_gate` 与 Agent50 generated files 已消费该 preflight；当前默认未设置外部目录，所以 NCI3 行状态为 `field_control_replay_package_waiting_for_FIELD_CONTROL_REPLAY_PACKAGE_DIR`、`package_preflight_pass=False`、`matched_transition_count=0`。验证：field-control/new-core targeted tests `12 passed`，field-control/sparse/new-core/action-board/Agent50/Agent49/52 targeted tests `85 passed`，完整回归 `592 passed`，CodeGraph 刷新为 `387 files / 5088 nodes / 8063 edges`。边界：R8u152 只判断真实控制回放包是否可进入 Agent49/52 离线 replay；不证明策略优越，不放松 guardrail，不恢复模型链，不写 actuator/release gate。
- 2026-06-22 新增 `R8u151_sparse_topology_installability_package_preflight`：承接 R8u150 后回到更根基的 P1 观测层阻断。此前 `NCI4_SPARSE_TOPOLOGY_INSTALLABILITY_PACKAGE` 已在 new-core-interface 队列中定义，但仍停留在 `interface_preflight_not_implemented_yet`；Agent48 稀疏布点已有 synthetic/path prior，却缺少真实 topology、node-modality cost、installability、hydraulic delay 与 labeled state matrix 的统一外部入口。现新增 `src/water_ai/sparse_topology_installability_package.py`、`experiments/run_sparse_topology_installability_preflight.py`、`tests/test_sparse_topology_installability_package.py`，生成 `outputs/sparse_topology_installability_package/sparse_topology_installability_package_preflight.json`、`outputs/sparse_topology_installability_package/sparse_topology_installability_package_template/` 和 `deliverables/model_core_optimization/sparse_topology_installability_package_preflight.md`。该接口要求五张表：`site_topology_graph`、`candidate_node_modality_costs`、`installability_maintenance_constraints`、`node_hydraulic_delay`、`labeled_state_matrix`，并要求至少 3 个共同 `node_id` 同时通过 field origin、QA、节点/模态成本、可安装/供电/通信、水力延迟、维护约束和隐藏状态标签检查。`new_core_interface_candidate_gate` 与 Agent50 generated files 已消费该 preflight；当前默认未设置外部目录，所以 NCI4 行状态为 `sparse_topology_installability_package_waiting_for_SPARSE_TOPOLOGY_INSTALLABILITY_PACKAGE_DIR`、`package_preflight_pass=False`、`matched_node_count=0`。验证：sparse-topology/new-core targeted tests `11 passed`，sparse-topology/new-core/action-board/Agent50/Agent48相关 targeted tests `73 passed`，完整回归 `586 passed`，CodeGraph 刷新为 `383 files / 5032 nodes / 7982 edges`。边界：R8u151 只判断真实拓扑与安装约束包是否可进入 Agent48 sparse layout holdout；不证明可部署传感布局，不生成 field soft-sensor performance，不恢复模型链，不写 actuator/release gate。
- 2026-06-22 新增 `R8u150_field_supported_kg_edge_package_preflight`：承接 R8u147/R8u149 后的 new-core-interface 队列，选择第二个仍具高边际价值的候选 `NCI5_FIELD_SUPPORTED_KG_EDGE_PACKAGE`。P4 灰箱包已具备 preflight+Agent53 adapter，继续在 P4 内部堆 synthetic 细节收益低；P6 的缺口是 KG reasoning 仍主要是 literature/synthetic reasoning patch，缺少 field-supported KG edges 与 source_basis completion。现新增 `src/water_ai/field_supported_kg_edge_package.py`、`experiments/run_field_supported_kg_edge_preflight.py`、`tests/test_field_supported_kg_edge_package.py`，生成 `outputs/field_supported_kg_edge_package/field_supported_kg_edge_package_preflight.json`、`outputs/field_supported_kg_edge_package/field_supported_kg_edge_package_template/` 和 `deliverables/model_core_optimization/field_supported_kg_edge_package_preflight.md`。该接口要求五张表：`pollutant_material_condition_edges`、`source_basis_rows`、`field_supported_edge_rows`、`failure_boundary_annotations`、`claim_action_constraint_links`，并要求至少 3 个共同 `edge_id` 同时通过 field origin、QA、field-supported evidence stage、source basis、现场支持分数、失败边界和人工复核约束。`new_core_interface_candidate_gate`、Agent50 generated files、stage board 和 manifest 已消费该 preflight；当前默认未设置外部目录，所以 P6 行状态为 `field_supported_kg_edge_package_waiting_for_FIELD_SUPPORTED_KG_EDGE_PACKAGE_DIR`、`package_preflight_pass=False`、`matched_edge_count=0`。验证：KG-edge/new-core/action-board targeted tests `15 passed`，KG-edge/new-core/action-board/Agent50/KG reasoning targeted tests `59 passed`，完整回归 `580 passed`，CodeGraph 刷新为 `379 files / 4976 nodes / 7901 edges`。边界：R8u150 只判断 field-supported KG edge package 是否可进入 KG reasoning；不生成 site-specific mechanism claim，不生成 claim text，不恢复模型链，不写 actuator/release gate。
- 2026-06-22 新增 `R8u149_grey_box_field_calibration_summary_adapter`：承接 R8u148 的灰箱校准包 preflight。R8u148 已定义 `GREY_BOX_CALIBRATION_PACKAGE_DIR` 五表入口，但它只回答“外部包结构是否可进入 Agent53”，还没有把五表现场记录压成 Agent53 可消费的 `field_calibration` 指标。现已在 `src/water_ai/grey_box_calibration_package.py` 中新增 `build_grey_box_field_calibration_summary()`，从通过 preflight 的 `batch_inlet_outlet_lab` 与 `hydraulic_rtd_or_tracer` 等表中按共同 `batch_id` 计算 `field_physics_coverage`、`max_field_residual`、`max_mass_balance_residual`、`mean_observed_k_per_min`、`mean_observed_removal_fraction` 和副产物负荷代理，并输出 `field_calibration_for_agent53`。`experiments/run_grey_box_calibration_package_preflight.py` 现在同步生成 `outputs/grey_box_calibration_package/grey_box_field_calibration_summary.json`，`new_core_interface_candidate_gate`、`stage_boundary_external_action_board`、Agent50 generated files 和 manifest 已消费 downstream calibration status。当前默认未设置外部目录，所以状态仍为 `grey_box_field_calibration_waiting_for_preflight_ready`、`can_run_agent53_field_calibration=False`、`agent53_field_candidate_ready=False`。验证：grey-box/new-core/action-board targeted tests `15 passed`，grey-box/new-core/action-board/Agent50/Agent53 targeted tests `60 passed`，完整回归 `575 passed`，CodeGraph 刷新为 `375 files / 4922 nodes / 7822 edges`。边界：R8u149 只是 preflight 到 Agent53 field calibration 的 adapter；它不生成 field evidence，不证明机理有效，不恢复模型链，不写 actuator/release gate。
- 2026-06-22 新增 `R8u148_grey_box_calibration_package_preflight`：承接 R8u147 的最高 new-core-interface 候选 `NCI1_GREY_BOX_CALIBRATION_PACKAGE`。此前 `NEW_CORE_INTERFACE` 已能指出下一类高价值接口是灰箱校准包，但尚未真正定义 `GREY_BOX_CALIBRATION_PACKAGE_DIR` 的文件结构、预检指标、批次对齐和 no-write 边界。现新增 `src/water_ai/grey_box_calibration_package.py`、`experiments/run_grey_box_calibration_package_preflight.py`、`tests/test_grey_box_calibration_package.py`，生成 `outputs/grey_box_calibration_package/grey_box_calibration_package_preflight.json`、`outputs/grey_box_calibration_package/grey_box_calibration_package_template/` 和 `deliverables/model_core_optimization/grey_box_calibration_package_preflight.md`。该接口要求五张最小现场校准表：`batch_inlet_outlet_lab`、`hydraulic_rtd_or_tracer`、`oxidant_dose_residual_log`、`catalyst_age_regeneration_log`、`byproduct_panel`，并要求至少 3 个共同 `batch_id` 同时通过 field origin、QA、数值合法性和五表对齐。`new_core_interface_candidate_gate`、`stage_boundary_external_action_board`、Agent50 generated files 和 manifest 已消费该 preflight；当前默认未设置外部目录，所以状态为 `grey_box_calibration_package_waiting_for_GREY_BOX_CALIBRATION_PACKAGE_DIR`、`package_preflight_pass=False`、`matched_batch_count=0`，下一步为填写模板并设置 `GREY_BOX_CALIBRATION_PACKAGE_DIR`。验证：grey-box-calibration/new-core/action-board/Agent50/Agent53 targeted tests `59 passed`，完整回归 `574 passed`，CodeGraph 刷新为 `375 files / 4912 nodes / 7810 edges`。边界：R8u148 只判断灰箱校准包是否可进入 Agent53 field calibration consumer，不生成 field evidence，不证明机理有效，不恢复模型链，不写 actuator/release gate。
- 2026-06-22 新增 `R8u147_new_core_interface_candidate_gate`：承接 R8u146 后的阶段边界复核。当前核心阶段门仍为 `stop_expansion_wait_for_real_field_package_or_new_core_interface`，最高外部动作仍是填写 6 行 `FOCUSED_CATALYST_RESPONSE_PATH`；但原 `NEW_CORE_INTERFACE` 在阶段行动板中仍偏泛化，只说明“可定义新的可测试接口”，没有把哪些接口值得开、需要什么输入、输出什么验证指标、不能越过什么边界压成机器可读队列。现新增 `src/water_ai/new_core_interface_candidate_gate.py` 与 `experiments/run_new_core_interface_candidate_gate.py`，并把该门接入 Agent50 自动刷新链路和 `stage_boundary_external_action_board`。该门会读取 Agent50 priority ranking，把可接受的新核心接口候选压成 5 个 ranked contracts：`NCI1_GREY_BOX_CALIBRATION_PACKAGE`、`NCI5_FIELD_SUPPORTED_KG_EDGE_PACKAGE`、`NCI3_FIELD_CONTROL_REPLAY_PACKAGE`、`NCI4_SPARSE_TOPOLOGY_INSTALLABILITY_PACKAGE`、`NCI2_FIELD_MISSINGNESS_REPLAY_PACKAGE`。当前最高候选为 `GREY_BOX_CALIBRATION_PACKAGE_DIR`，对应 P4 灰箱校准接口，要求 lab pairs、HRT/RTD、药剂/能耗、催化剂历史和基质抑制等输入；输出校准参数范围、mass balance residual、residence time error 和参数边界。`outputs/model_core_governance/new_core_interface_candidate_gate.json`、`deliverables/model_core_optimization/new_core_interface_candidate_gate.md`、行动板、Agent50 generated files 和 manifest 均已刷新。验证：new-core-interface/action-board/Agent50 targeted tests `49 passed`，完整回归 `569 passed`，CodeGraph 刷新为 `371 files / 4857 nodes / 7730 edges`。边界：R8u147 只把“可开新接口”从泛化逃生口变成可审查候选合同，不实现灰箱校准 preflight，不生成 field evidence，不恢复模型链，不写 actuator/release gate。
- 2026-06-22 新增 `R8u146_focused_merge_preflight_submit_ready_semantics`：承接 R8u145 的 submit-ready 语义收紧，继续向源头核查 focused catalyst response merge。发现 `focused_catalyst_response_merge.md` 与上游 preflight 仍主要使用 `candidate_self_declared_submit_ready` 这个旧命名，容易让人把“focused 六行 merge gate 通过”误解为真实 field validation 或可恢复模型链。现已在 `src/water_ai/focused_catalyst_response_merge.py` 中新增 `candidate_preflight_submit_ready`、`candidate_submit_ready_semantics`、`merged_full_response_candidate_preflight_submit_ready` 与 `merged_full_response_candidate_submit_ready_semantics`，并保留旧 `candidate_self_declared_submit_ready` 作为 legacy alias；`experiments/run_focused_catalyst_response_merge.py` 的 Markdown/manifest 改为优先显示 preflight submit-ready 和语义边界；Agent50 scorecard、priority ranking、Agent50 report 与 manifest 也已消费新字段。当前 focused merge、candidate、Agent50 和 manifest 均显示 `preflight_submit_ready=False`，且语义说明明确“不是 field validation、不是 model-chain resume readiness、不是 actuator/release readiness”。验证：focused/Agent50/operator/action-board targeted tests `52 passed`，完整回归 `565 passed`，CodeGraph 刷新为 `367 files / 4823 nodes / 7675 edges`。边界：R8u146 只修复 focused merge 源头候选可提交语义，不生成 focused response，不生成 field evidence，不恢复模型链，不写 actuator/release gate。
- 2026-06-22 新增 `R8u145_stage_board_submit_ready_semantics_tightened`：承接 R8u144 后继续检查阶段边界外部行动板的证据语义。发现 `highest_priority_focused_candidate_submit_ready` 名称像“真实可提交”，但此前实际更接近读取 focused candidate 的 self-declared 标记；虽然当前值为 False 未造成错误，但未来若候选文件自声明 ready 而 operator packet / focused merge preflight 未通过，action board 和 manifest 可能产生误导。现已在 `src/water_ai/stage_boundary_external_action_board.py` 中拆分 `focused_candidate_self_declared_submit_ready`、`focused_candidate_operator_packet_submit_ready` 和 canonical `focused_candidate_submit_ready`：最高优先级 summary 与 manifest 的 submit-ready 只认 operator packet ready、field-activation candidate submit gate 与 row preflight 共同通过的结果；人读 Markdown 表格也新增 operator packet ready 与 submit ready 两列。当前 action board、Agent50 manifest 与报告均显示 `focused_candidate_operator_packet_submit_ready=False`、`focused_candidate_submit_ready=False`。验证：stage-board/Agent50/operator/focused targeted tests `51 passed`，完整回归 `564 passed`，CodeGraph 刷新为 `367 files / 4819 nodes / 7668 edges`，产物已由 `experiments/run_stage_boundary_external_action_board.py` 与 `experiments/run_agent50_model_core_governance.py` 重生成。边界：R8u145 只收紧外部行动板的候选可提交语义，不生成 focused response，不生成 field evidence，不恢复模型链，不写 actuator/release gate。
- 2026-06-22 新增 `R8u144_core_gate_r7_action_consumes_focused_candidate_availability`：承接 R8u143 后的最高核心门 R7 action row 回接缺口。R8u143 已让 operator packet、Agent50 scorecard、field evidence wait status、core gate 的 `NEW_CORE_INTERFACE` 与 `external_resume_conditions` 看见 `candidate_not_submittable_waiting_for_FOCUSED_CATALYST_RESPONSE_PATH`，但 `core_score_termination_gate.json` 的 `next_allowed_actions.R7_REAL_FIELD_PACKAGE` 仍未直接暴露该状态；后续若只读取 R7 external package action row，仍可能漏掉 focused candidate 不可提交边界。现已在 `ModelCoreOptimizationGovernanceAgent` 中新增 `_external_activation_operator_packet_core_gate_fields()`，并把 operator packet status、target hidden state、source env var、expected focused rows、focused candidate availability、operator-packet submit-ready、next action、boundary pass、can_resume/no-write flags 回接到 R7 action row。当前 `R7_REAL_FIELD_PACKAGE` action row 显示 `external_activation_operator_action_packet_status=operator_packet_waiting_for_focused_catalyst_response`、`external_activation_operator_action_packet_focused_candidate_availability_status=candidate_not_submittable_waiting_for_FOCUSED_CATALYST_RESPONSE_PATH`、`external_activation_operator_action_packet_focused_candidate_operator_packet_submit_ready=False`，且 `can_write_to_actuator=False`、`can_write_to_release_gate=False`。验证：Agent50 单测 `40 passed`，governance/operator/action-board/focused targeted tests `49 passed`，完整回归 `562 passed`，CodeGraph 刷新为 `367 files / 4817 nodes / 7665 edges`。边界：R8u144 只把候选不可提交边界推到最高 core gate 的 R7 action row，不生成 focused response，不生成 field evidence，不恢复模型链，不写 actuator/release gate。
- 2026-06-22 新增 `R8u143_operator_packet_consumes_focused_candidate_availability`：承接 R8u142 后的 operator-facing 执行包回接缺口。R8u141/R8u142 已让 focused merge candidate 和 action board 显示 `candidate_not_submittable_waiting_for_FOCUSED_CATALYST_RESPONSE_PATH`，但 `external_activation_operator_action_packet.json` 本身此前只显示 candidate path、merge status 和 can-submit 布尔值，未直接暴露 candidate availability 与 use boundary；如果操作者只看 operator packet，仍可能误解 `merged_full_field_activation_response_candidate.json` 的可用性。现已在 `src/water_ai/external_activation_operator_packet.py` 中新增 `focused_candidate_availability_status`、`focused_candidate_self_declared_submit_ready`、`focused_candidate_external_response_supplied`、`focused_candidate_operator_packet_submit_ready` 和 `focused_candidate_use_boundary`，并让 packet readiness 同时参考 merge preflight 与 candidate self-declared submit-ready。`experiments/run_external_activation_operator_packet.py` 已将这些字段写入 Markdown 报告与 manifest；Agent50 governance scorecard、field evidence wait status、core gate 的 `new_core_interface` 与 `external_resume_conditions` 也已消费这些字段。当前 operator packet、Agent50 scorecard 和 manifest 均显示 `candidate_not_submittable_waiting_for_FOCUSED_CATALYST_RESPONSE_PATH`、`submit_ready=False`。验证：external packet + Agent50 单测 `42 passed`，operator/focused/action-board/Agent50 targeted tests `49 passed`，完整回归 `562 passed`，CodeGraph 刷新为 `367 files / 4816 nodes / 7664 edges`。边界：R8u143 只把候选不可提交状态推入 operator-facing packet 和治理主链，不生成 focused response，不生成 field evidence，不恢复模型链，不写 actuator/release gate。
- 2026-06-22 新增 `R8u142_stage_board_consumes_focused_candidate_availability`：承接 R8u141 后的最高操作入口回接缺口。R8u141 已让 `merged_full_field_activation_response_candidate.json` 自证 `candidate_not_submittable_waiting_for_FOCUSED_CATALYST_RESPONSE_PATH`，但阶段边界行动板此前只显示最高动作是填写 `FOCUSED_CATALYST_RESPONSE_PATH`，未暴露该 candidate availability；如果后续操作者只看 action board，仍可能不知道当前 merged candidate 文件不可提交。现已在 `src/water_ai/stage_boundary_external_action_board.py` 中新增可选输入 `focused_catalyst_response_merge_metrics`，并把 `focused_merge_preflight_status`、`focused_candidate_availability_status`、`focused_candidate_self_declared_submit_ready`、`focused_candidate_external_response_supplied`、`focused_candidate_can_submit_as_FIELD_ACTIVATION_RESPONSE_PATH`、row/batch preflight 指标和 `focused_candidate_use_boundary` 写入 `R7_REAL_FIELD_PACKAGE` action row 与 operator runbook；summary 新增最高优先级 candidate status。`experiments/run_stage_boundary_external_action_board.py` 与 `experiments/run_agent50_model_core_governance.py` 均已读取 `focused_catalyst_response_merge_preflight.json` 并回写 manifest。当前 action board 最高优先级行显示 `focused_candidate_availability_status=candidate_not_submittable_waiting_for_FOCUSED_CATALYST_RESPONSE_PATH`、`focused_candidate_self_declared_submit_ready=False`。验证：action board 单测 `3 passed`，stage-board/focused-merge/Agent50/operator-packet targeted tests `49 passed`，完整回归 `562 passed`，CodeGraph 刷新为 `367 files / 4814 nodes / 7662 edges`。边界：R8u142 只把 R8u141 的候选不可提交状态回接到阶段边界行动板，不生成 focused response，不生成 field evidence，不恢复模型链，不写 actuator/release gate。
- 2026-06-22 新增 `R8u141_focused_merge_candidate_availability_watermark`：承接 R8u140 后的外部 focused response 接口风险核查。当前最高优先级仍是 `FOCUSED_CATALYST_RESPONSE_PATH`，但 `experiments/run_focused_catalyst_response_merge.py` 即使在未提交外部 focused response 时，也会写出 `outputs/focused_catalyst_response_merge/merged_full_field_activation_response_candidate.json`；虽然 preflight 已显示不可提交，但候选文件本身此前缺少足够机器可读的 availability watermark，存在被后续 agent/操作者误读为可提交候选的风险。现已在 `src/water_ai/focused_catalyst_response_merge.py` 的 merged candidate 中新增 `candidate_availability_status`、`can_submit_candidate_as_FIELD_ACTIVATION_RESPONSE_PATH`、`external_focused_response_supplied`、source/row/batch 状态和 `candidate_use_boundary`，并将同类字段提升到 merge preflight 顶层；`experiments/run_focused_catalyst_response_merge.py` 已把候选 availability 写入 Markdown 报告与 manifest；Agent50 scorecard/manifest 也新增 `focused_catalyst_response_merge_candidate_availability_status` 与 `focused_catalyst_response_merge_candidate_self_declared_submit_ready`。当前状态为 `candidate_not_submittable_waiting_for_FOCUSED_CATALYST_RESPONSE_PATH`、`self_declared_submit_ready=False`、`external_focused_response_supplied=False`、`focused_replacement_row_count=0`。验证：focused merge + Agent50 单测 `44 passed`，focused/Agent50/action-board/operator-packet targeted tests `49 passed`，完整回归 `562 passed`，CodeGraph 刷新为 `367 files / 4812 nodes / 7658 edges`。边界：R8u141 只让候选文件和治理层自证“当前不能作为 FIELD_ACTIVATION_RESPONSE_PATH 使用”，不生成 field evidence，不恢复模型链，不写 actuator/release gate。
- 2026-06-22 新增 `R8u140_agent50_refreshes_stage_boundary_external_action_board`：承接 R8u139 后的同步缺口。R8u139 已把阶段边界的外部动作压成 `stage_boundary_external_action_board.json/md`，但此前它由独立 runner 生成；若后续只运行 Agent50，行动板可能成为静态旧副本。现已将 `build_stage_boundary_external_action_board()` 与共享 Markdown 渲染函数接入 `experiments/run_agent50_model_core_governance.py`：每次 Agent50 刷新 `core_score_termination_gate.json` 后，会自动同步生成 `outputs/model_core_governance/stage_boundary_external_action_board.json` 与 `deliverables/model_core_optimization/stage_boundary_external_action_board.md`，并写入 `generated_files`、Agent50 JSON payload、manifest 的 `latest_agent50_stage_boundary_external_action_board_*` 和通用 `latest_stage_boundary_external_action_board_*` 字段。当前自动刷新结果仍为 `stage_boundary_external_action_board_waiting_for_external_inputs`，`action_count=4`、`external_wait_count=3`、`model_chain_resume_ready_count=0`、最高优先级 source env var 为 `FOCUSED_CATALYST_RESPONSE_PATH`，且 `can_write_to_actuator=False`、`can_write_to_release_gate=False`。验证：action board 单测 `3 passed`，stage-board/external-packet/formal-packet/Agent50 targeted tests `48 passed`，完整回归 `562 passed`，CodeGraph 刷新为 `367 files / 4809 nodes / 7654 edges`。边界：R8u140 只修复治理产物自动刷新链路，不新增 field evidence，不生成法律意见、prior-art 结论或权利要求文本，不恢复模型链，不写 actuator/release gate。
- 2026-06-22 新增 `R8u139_stage_boundary_external_action_board`：承接 R8u138 后的阶段边界执行收束。当前 `core_score=0.96`、`iteration_delta=0.0`、`continue_expansion_allowed=False`、`stage_decision=stop_expansion_wait_for_real_field_package_or_new_core_interface`，继续做内部 synthetic/template 扩张已经低边际价值；但外部行动分散在 core gate、external activation operator packet、formal-search operator packet 和 manifest 中，操作入口仍不够集中。现新增 `src/water_ai/stage_boundary_external_action_board.py`、`experiments/run_stage_boundary_external_action_board.py` 和 `tests/test_stage_boundary_external_action_board.py`，生成 `outputs/model_core_governance/stage_boundary_external_action_board.json` 与 `deliverables/model_core_optimization/stage_boundary_external_action_board.md`，把阶段边界下的 4 个可行动作统一排序：1）`R7_REAL_FIELD_PACKAGE` 通过 `FOCUSED_CATALYST_RESPONSE_PATH` 补 6 行 catalyst_activity 真实 focused response；2）`R8U66_PATH_ENDPOINT_LABEL_PACKAGE` 设置 `FIELD_PATH_ENDPOINT_LABEL_PACKAGE_DIR` 补路径/终点标签包；3）`R8U79_FORMAL_SEARCH_RESULT_PACKAGE` 通过 `FORMAL_SEARCH_NONLEGAL_REVIEW_RESPONSE_PATH` 补 7 行人工非法律 review response；4）`NEW_CORE_INTERFACE` 仅作为新可测试接口入口。当前行动板状态为 `stage_boundary_external_action_board_waiting_for_external_inputs`，`action_count=4`、`external_wait_count=3`、`model_chain_resume_ready_count=0`、`handoff_ready_count=1`、最高优先级 source env var 为 `FOCUSED_CATALYST_RESPONSE_PATH`。验证：新增单测 `2 passed`，stage-board/external-packet/formal-packet/Agent50 targeted tests `47 passed`，完整回归 `561 passed`，CodeGraph 刷新为 `367 files / 4808 nodes / 7651 edges`。边界：R8u139 只把已存在的外部输入门压成阶段边界行动板，不生成 field evidence，不生成法律意见、prior-art 结论或权利要求文本，不恢复模型链，不写 actuator/release gate。
- 2026-06-22 新增 `R8u138_core_gate_consumes_formal_search_nonlegal_review_operator_packet`：承接 R8u137 后的核心阶段门回接缺口。R8u137 已让 Agent50 scorecard/report/manifest 消费 R8u136 operator packet，但 `core_score_termination_gate.json` 的 `next_allowed_actions.R8U79_FORMAL_SEARCH_RESULT_PACKAGE` 与 `external_resume_conditions` 仍只显示 formal-search result package handoff-ready，未暴露 R8u136 的 7 行人工非法律 review contract、source env var 和 no-write/no-claim 边界；后续若只读核心阶段门，仍可能不知道已有 operator packet。现已在 `ModelCoreOptimizationGovernanceAgent` 中新增 `formal_nonlegal_review_operator_packet_*` 核心门字段，并将其写入 R8U79 action 与 `external_resume_conditions.formal_search_nonlegal_review_operator_packet`。当前核心门显示：R8U79 仍是 `formal_search_handoff_only`、`handoff_only=True`、`current_handoff_ready=True`、`current_model_chain_resume_ready=False`；同时显示 `formal_nonlegal_review_operator_packet_status=formal_search_nonlegal_review_operator_packet_ready_waiting_for_human_response`、`expected_review_packet_row_count=7`、`source_env_var=FORMAL_SEARCH_NONLEGAL_REVIEW_RESPONSE_PATH`、`can_route_to_claim_scope_patch_draft=False`、`can_resume_model_chain=False`、`can_emit_claim_text=False`、`can_write_to_actuator=False`、`can_write_to_release_gate=False`。验证：Agent50 单测 `40 passed`，formal-search/Agent60/Agent50 targeted tests `99 passed`，完整回归 `559 passed`，CodeGraph 刷新为 `363 files / 4777 nodes / 7596 edges`。边界：R8u138 只把 R8u136/R8u137 的人工审查接口推进到最高核心阶段门，不生成 human response，不生成法律意见、prior-art 结论、权利要求文本或 field evidence，不恢复模型链，不写 actuator/release gate。
- 2026-06-22 新增 `R8u137_agent50_consumes_formal_search_nonlegal_review_operator_packet`：承接 R8u136 后的下游回接缺口。R8u136 已生成人工非法律技术比较 operator packet，但 Agent50 全局治理层此前只能看到 R8u134 AI brief，无法在 scorecard、blocked reasons、governance report、Agent50 report 和 manifest 中直接显示“已有可执行 operator packet、应按 7 行 response contract 提交、仍不能进入 claim patch”。现已在 `ModelCoreOptimizationGovernanceAgent` 中新增可选输入 `formal_search_nonlegal_review_operator_packet`，并把 `formal_search_nonlegal_review_operator_packet_status`、expected rows、high priority rows、accepted rows、source env var、can route to claim scope patch、boundary preserved 和 next operator action 接入 governance scorecard；blocked reason 也从泛化的 R8u134 brief 描述升级为 R8u136 packet-ready 描述。`experiments/run_agent50_model_core_governance.py` 已读取 `outputs/agent_architecture_consolidation/formal_search_nonlegal_review_operator_packet.json`，将状态写入 Agent50 report、governance report、priority ranking 和 manifest 的 `latest_agent50_formal_search_nonlegal_review_operator_packet_*` 字段。当前结果：`packet_status=formal_search_nonlegal_review_operator_packet_ready_waiting_for_human_response`、`expected_review_packet_row_count=7`、`high_priority_review_row_count=1`、`accepted_review_row_count=0`、`source_env_var=FORMAL_SEARCH_NONLEGAL_REVIEW_RESPONSE_PATH`、`can_route_to_claim_scope_patch_draft=False`、`boundary_preserved=True`。验证：Agent50 单测 `40 passed`，formal-search/Agent60/Agent50 targeted tests `99 passed`，完整回归 `559 passed`，CodeGraph 刷新为 `363 files / 4776 nodes / 7595 edges`。边界：R8u137 只增强 R8u136 的下游治理可见性和可保护性链工程交接，不生成 human response，不生成法律意见、prior-art 结论、权利要求文本或 field evidence，不恢复模型链，不写 actuator/release gate。
- 2026-06-22 新增 `R8u136_formal_search_nonlegal_review_operator_packet`：承接 R8u135 后的实际操作摩擦。R8u135 已让 Agent50 看见 R8u134 AI-assisted nonlegal brief，但人类下一步仍要在多个 Agent60 产物之间来回找：brief、response template、source preflight、review readiness、claim patch blocker。现新增 `src/water_ai/formal_search_nonlegal_review_operator_packet.py`、`experiments/run_formal_search_nonlegal_review_operator_packet.py` 和 `tests/test_formal_search_nonlegal_review_operator_packet.py`，把人工非法律技术比较的下一步压成一个机器可读 operator packet，输出 `outputs/agent_architecture_consolidation/formal_search_nonlegal_review_operator_packet.json` 和 `deliverables/model_core_optimization/formal_search_nonlegal_review_operator_packet.md`，并回写 manifest。当前 packet 状态为 `formal_search_nonlegal_review_operator_packet_ready_waiting_for_human_response`，要求通过 `FORMAL_SEARCH_NONLEGAL_REVIEW_RESPONSE_PATH` 提交 `outputs/agent_architecture_consolidation/formal_search_nonlegal_review_response.json`；`expected_review_packet_row_count=7`、`high_priority_review_row_count=1`、`accepted_review_row_count=0`、`can_route_to_claim_scope_patch_draft=False`。该 packet 同时列出 required root keys、review metadata fields、review row fields、7 行人工审查任务、pre-submission checklist、rejection conditions 和 validation commands。验证：新增单测 `3 passed`，formal-search/Agent60/Agent50 targeted tests `98 passed`，完整回归 `558 passed`，CodeGraph 刷新为 `363 files / 4761 nodes / 7579 edges`。边界：R8u136 只降低人工 nonlegal review response 的提交摩擦，不替代人工审查，不生成法律意见、prior-art 结论、权利要求文本或 field evidence，不恢复模型链，不写 actuator/release gate；即使未来 human response 通过 preflight，也仍必须继续经过 claim scope patch、formal counsel 和 field/replay/release 边界。
- 2026-06-22 新增 `R8u135_agent50_consumes_formal_search_ai_nonlegal_review_brief`：承接 R8u134 后的治理回接缺口。R8u134 已生成 `formal_search_ai_nonlegal_review_brief.json`，但 Agent50 全局治理层此前只消费 `formal_search_execution_route_plan.json` 和 external activation router 的 handoff-ready 状态，无法在 scorecard/priority ranking/governance report 中直接看到 AI nonlegal brief 是否已完成。现已在 `ModelCoreOptimizationGovernanceAgent` 中新增可选输入 `formal_search_ai_nonlegal_review_brief`，并把 `formal_search_ai_nonlegal_review_brief_status`、row count、missing source/claim mapping、can help human review、can route to claim scope patch、boundary preserved 和 next operator action 接入 governance scorecard；protectability 分数也只在 brief ready 且 no-legal/no-field/no-write 边界完整时获得小幅增益。`experiments/run_agent50_model_core_governance.py` 已读取 `outputs/agent_architecture_consolidation/formal_search_ai_nonlegal_review_brief.json`，将状态写入 Agent50 report、governance report、priority ranking 和 manifest 的 `latest_agent50_formal_search_ai_nonlegal_review_brief_*` 字段。当前 Agent50 blocked reason 已更新为：R8u134 AI brief 已将 preliminary public-source hits 映射到 technical claim scaffolds，可用于人工 triage，但仍必须提交 `FORMAL_SEARCH_NONLEGAL_REVIEW_RESPONSE_PATH` 后才可能进入 claim-scope patch draft；field replay/control 和 claim text 仍阻断。验证：Agent50 单测 `39 passed`，formal-search/Agent50 targeted tests `95 passed`，完整回归 `555 passed`，CodeGraph 刷新为 `359 files / 4726 nodes / 7518 edges`。边界：R8u135 只增强 Agent50 对可保护性链进度的可见性，不生成人工 review response，不生成法律意见、prior-art 结论、权利要求文本或 field evidence，不恢复模型链，不写 actuator/release gate。
- 2026-06-22 新增 `R8u134_formal_search_ai_nonlegal_review_brief`：承接 R8u133 后的下一阶段门。R8u133 已让 preliminary formal search result package 通过 Agent60 source/row/validation execution，并进入 `R8U79_FORMAL_SEARCH_RESULT_PACKAGE` handoff-ready，但仍停在人工非法律技术比较前；如果直接尝试生成 claim patch，会越过人工审查门。现新增 `src/water_ai/formal_search_nonlegal_review_brief.py`、`experiments/run_formal_search_nonlegal_review_brief.py` 和 `tests/test_formal_search_nonlegal_review_brief.py`，读取 `preliminary_formal_search_result_package.json`、`formal_search_nonlegal_comparison_review_packet.json` 与 `technical_claim_skeleton_scaffold.json`，生成 `outputs/agent_architecture_consolidation/formal_search_ai_nonlegal_review_brief.json` 和 `deliverables/model_core_optimization/formal_search_ai_nonlegal_review_brief.md`。该 brief 把 7 个公开来源命中项压成 AI-assisted pre-review：每行包含来源 URL、覆盖的 PTF 技术特征、映射的 TCS 技术骨架、overlap/risk tier、初步区别点、建议人工审查关注点、保留的 field replay/operator/release gate 和禁止越界边界。当前结果：`brief_status=formal_search_ai_nonlegal_review_brief_ready_for_human_review`、`brief_row_count=7`、`missing_source_row_count=0`、`missing_claim_mapping_row_count=0`、risk tier 为 1 个 partial overlap、5 个 component/architecture overlap、1 个 high-overlap human-review priority；其中 FSWP6 多智能体 AI 催化剂发现被标为 high-overlap 人工优先审查。验证：新增单测 `2 passed`，formal-search/Agent60 targeted tests `56 passed`，完整回归 `554 passed`，CodeGraph 刷新为 `359 files / 4711 nodes / 7503 edges`，runner 已生成 brief 并回写 manifest。边界：R8u134 不是人工 review response，不是法律意见，不是 prior-art 结论，不生成权利要求文本，不恢复 field replay/control，不写 actuator/release gate；下一步仍必须由人工完成 `FORMAL_SEARCH_NONLEGAL_REVIEW_RESPONSE_PATH` 后，才可能进入后续 claim scope patch draft。
- 2026-06-22 新增 `R8u133_preliminary_formal_search_result_package`：承接当前阶段门“不能继续内部 synthetic/template 扩张，应转向外部证据包、formal search、人工审查或 field validation”。在没有真实 focused catalyst field response 的情况下，本轮选择同一阶段门允许的 `FORMAL_SEARCH_RESULT_PACKAGE_PATH` 通道，推进可保护性/验证治理，而不伪造 field evidence。新增 `src/water_ai/preliminary_formal_search_package.py`、`experiments/run_preliminary_formal_search_result_package.py` 和 `tests/test_preliminary_formal_search_package.py`，读取既有 `formal_search_execution_route_plan.json`，用真实公开来源为 7 个 formal search work package 各填 1 条 preliminary hit，生成 `outputs/agent_architecture_consolidation/preliminary_formal_search_result_package.json`、`preliminary_formal_search_handoff.json`、`preliminary_formal_search_result_package_validation_summary.json` 和 `deliverables/model_core_optimization/preliminary_formal_search_result_package.md`。外部来源覆盖 Google Patents、GitHub、Google Scholar、WaterTAP/QSDsan/Pyomo documentation 等通道，示例包括 EP2414901B1 水处理监测/软测量相关专利、PySensors 稀疏传感布点库、npj Clean Water 多智能体污染控制、WaterTAP 工艺建模优化文档、SciKGs 科学知识图谱综述资源、Nature Water 多智能体 AI 催化剂发现论文和 Conservative Q-Learning 离线 RL。该包已通过 Agent60 source preflight、row preflight 和 validation execution：`source_ready_for_validation_gate`、`row_preflight_ready_for_validation_gate`、`validation_execution_ready_for_human_nonlegal_comparison_review`，7/7 work packages、7 validated hits、0 rejected hits、0 row gaps、0 forbidden boundary gaps。随后使用 `FORMAL_SEARCH_RESULT_PACKAGE_PATH` 运行 Agent60、external activation router 和 Agent50，当前 router 显示 `handoff_ready_route_count=1`、`handoff_ready_channel_ids=[R8U79_FORMAL_SEARCH_RESULT_PACKAGE]`、`model_chain_ready_route_count=0`；Agent50 blocked reason 已修正为 formal package 已通过 source/row preflight、可进入人工非法律技术比较，但仍不能恢复 field replay/control 或输出 claim text。验证：新增测试 `2 passed`，Agent50/formal/router targeted tests `103 passed`，完整回归 `552 passed`，CodeGraph 刷新为 `355 files / 4682 nodes / 7443 edges`。边界：R8u133 不是法律意见、不是正式授权判断、不是权利要求文本、不是 field evidence、不能写 actuator 或 release gate；它只把可保护性审查从“等待检索包”推进到“可进入人工非法律技术比较”。
- 2026-06-22 新增 `R8u132_core_gate_operator_packet_visibility`：承接 R8u131 后的剩余治理缺口。R8u131 已让 Agent50 scorecard、priority ranking、governance report 和 manifest 消费 `external_activation_operator_action_packet.json`，但 `core_score_termination_gate.json` 的 `next_allowed_actions.NEW_CORE_INTERFACE` 与 `external_resume_conditions.new_core_interface` 仍没有直接暴露 operator packet 状态；如果后续 agent 只读取核心终止门，仍可能不知道当前最高动作包要求填写 6 行 focused catalyst response 并设置 `FOCUSED_CATALYST_RESPONSE_PATH`。现已把 `external_activation_operator_action_packet_status`、target hidden state、source env var、expected focused row count、next operator action、boundary pass、can resume/write actuator/write release gate 等字段同步写入 NEW_CORE_INTERFACE allowed action 和 external resume conditions。刷新后核心 gate 显示：`operator_packet_waiting_for_focused_catalyst_response`、目标 `catalyst_activity`、source env var `FOCUSED_CATALYST_RESPONSE_PATH`、expected rows `6`、boundary pass `True`，同时保持 `can_resume_model_chain=False`、`can_write_to_actuator=False`、`can_write_to_release_gate=False`。验证：Agent50 单测 `37 passed`，外部激活链路 targeted tests `92 passed`，完整回归 `549 passed`，CodeGraph 刷新为 `351 files / 4657 nodes / 7404 edges`。该轮只把 operator packet 接入核心阶段门/恢复条件，不生成 field evidence、不替代 full response/package/router/replay/holdout、不恢复模型链、不写 actuator 或 release gate。
- 2026-06-22 新增 `R8u131_agent50_consumes_external_activation_operator_packet`：承接 R8u130，修复 operator action packet 还未回接 Agent50 全局治理层的问题。此前 R8u130 已生成 `outputs/model_core_governance/external_activation_operator_action_packet.json` 并回写 manifest，但 Agent50 scorecard、priority ranking、governance report 和 `latest_agent50_*` 指针还不能直接消费 packet 状态；如果后续只读 Agent50 产物，仍可能看不到当前最高外部操作包。现已在 `ModelCoreOptimizationGovernanceAgent` 中新增可选输入 `external_activation_operator_action_packet`，scorecard 与 `field_evidence_wait_status` 同步暴露 packet status、target hidden state、source env var、expected focused row count、next operator action、boundary pass、can resume/write 边界；`experiments/run_agent50_model_core_governance.py` 读取 `external_activation_operator_action_packet.json` 并写入 governance report、Agent50 report 和 manifest 的 `latest_agent50_external_activation_operator_action_packet_*` 字段。当前 Agent50 已消费 packet：`operator_packet_waiting_for_focused_catalyst_response`、目标 `catalyst_activity`、source env var `FOCUSED_CATALYST_RESPONSE_PATH`、expected rows `6`、boundary pass `True`，同时保持 `can_resume_model_chain=False`、`can_write_to_actuator=False`、`can_write_to_release_gate=False`。验证：Agent50 单测 `37 passed`，operator packet + focused merge + field activation + external router + Agent50 targeted tests `92 passed`，完整回归 `549 passed`。该轮增强的是 R8u130 的下游回接率和验证治理可见性，不生成 field evidence、不替代 full response/package/router/replay/holdout、不恢复模型链、不写 actuator 或 release gate。
- 2026-06-22 新增 `R8u130_external_activation_operator_action_packet`：承接 R8u129 后的阶段边界判断，不继续扩张内部 synthetic 模块，而是把当前最高外部动作压成一个可机读 operator action packet。新增 `src/water_ai/external_activation_operator_packet.py` 与 `experiments/run_external_activation_operator_packet.py`，输出 `outputs/model_core_governance/external_activation_operator_action_packet.json` 和 `deliverables/model_core_optimization/external_activation_operator_action_packet.md`。该 packet 聚合 `core_score_termination_gate.json`、`external_activation_router.json`、`catalyst_response_submission_kit_metrics.json`、`focused_catalyst_response_merge_preflight.json` 和 `focused_catalyst_response_template.json`，明确当前状态为 `operator_packet_waiting_for_focused_catalyst_response`，目标隐藏状态为 `catalyst_activity`，需要填写 6 行 focused catalyst response，至少 3 个共同真实 batch，设置 `FOCUSED_CATALYST_RESPONSE_PATH`，运行 `.venv/bin/python experiments/run_focused_catalyst_response_merge.py`；只有 focused merge ready 后才设置 `FIELD_ACTIVATION_RESPONSE_PATH` 并重跑 field activation/Agent50。packet 同时输出 boundary checks、拒收条件和 no-write 边界，显式保持 `can_resume_model_chain=False`、`can_write_to_actuator=False`、`can_write_to_release_gate=False`。验证：新单测 `2 passed`，runner 已生成 packet 并回写 manifest；external operator packet + focused merge + field activation + external router + Agent50 targeted tests `92 passed`，完整回归 `549 passed`，CodeGraph 刷新为 `351 files / 4646 nodes / 7393 edges`。该轮增强的是验证治理层到外部执行的工程化交接，不生成 field evidence、不替代 full response/package/router/replay/holdout、不恢复模型链、不写 actuator 或 release gate。
- 2026-06-22 新增 `R8u129_core_gate_focus_handoff_repair_visibility`：承接 R8u128 的 focused repair action 顶层消费，修复一个治理层可见性缺口：handoff/router/Agent50 scorecard 已能看到 `focused_catalyst_response_repair_work_order`，但 `core_score_termination_gate.json` 的 `next_allowed_actions.NEW_CORE_INTERFACE` 和 `external_resume_conditions.new_core_interface` 仍没有直接暴露 focused repair work order 状态、item count 和下一 operator action，后续若只读取核心终止门，仍可能不知道该按 `FOCUSED_CATALYST_RESPONSE_PATH` 修复工单恢复。现已在 `ModelCoreOptimizationGovernanceAgent` 中把 `new_core_interface_response_focus_handoff_repair_work_order_status`、`new_core_interface_response_focus_handoff_repair_item_count`、`new_core_interface_response_focus_handoff_repair_next_operator_action` 写入 NEW_CORE_INTERFACE，同时把 `response_focus_handoff_repair_*` 写入 external resume conditions；测试夹具也补上 focused repair handoff 字段并断言 core gate、resume conditions 和 scorecard 三处一致。刷新后 `core_score_termination_gate.json`、`priority_ranking.json`、`agent50_report.json` 和 manifest 均显示当前状态为 `focused_catalyst_response_repair_work_order_waiting_for_external_response`、item count `1`、下一步为填写 `outputs/catalyst_response_submission_kit/focused_catalyst_response_template.json` 并设置 `FOCUSED_CATALYST_RESPONSE_PATH`。验证：Agent50 单测 `37 passed`，focused merge + field activation + governance + external router + Agent54 targeted tests `97 passed`，完整回归 `547 passed`，CodeGraph 刷新为 `347 files / 4608 nodes / 7318 edges`。该轮只补齐核心阶段门/恢复条件的可见性，不生成 field evidence、不合成真实 focused response、不替代 full response/package/router/replay/holdout、不恢复模型链、不写 actuator 或 release gate。
- 2026-06-22 新增 `R8u128_focused_repair_action_handoff_router_consumption`：承接 R8u127 的 focused catalyst response repair work order，修复一个顶层动作脱节风险：工单已能指出 `FOCUSED_CATALYST_RESPONSE_PATH` 的 source/row/batch 修复项，但 field activation focus handoff 和 external activation router 仍主要使用泛化 handoff 动作，未来如果用户设置了坏路径或提交了格式错误 JSON，顶层仍可能提示“填 focused 模板并 merge”，而不是直接提示修 source。现已在 `build_field_activation_response_focus_handoff()` 中读取 `focused_catalyst_response_repair_work_order`，新增 `focused_repair_work_order_status`、`focused_repair_item_count`、`focused_repair_highest_priority_repair_id`、`focused_repair_next_operator_action`；默认 `waiting_for_external_response` 时保持原动作 `fill_focused_catalyst_response_template_then_set_FOCUSED_CATALYST_RESPONSE_PATH_and_merge_to_FIELD_ACTIVATION_RESPONSE_PATH`，但当 repair work order 进入 source/row/batch 阻断或 ready candidate 时，handoff 的 `next_operator_action` 会采用工单动作。external router 顶层同步暴露 focused repair 状态、item count 和 repair action，Agent50 scorecard/manifest 也接入 handoff repair 字段。新增测试证明：默认等待态不改变主线动作；当 focused source 被阻断时，handoff/router 会输出 `repair_FOCUSED_CATALYST_RESPONSE_PATH_file_path`。验证：field activation + external router 单测 `49 passed`，focused merge + field activation + governance + external router + Agent54 targeted tests `97 passed`，完整回归 `547 passed`，CodeGraph 刷新为 `347 files / 4608 nodes / 7318 edges`。该轮只让 repair work order 的动作回接顶层路由，不生成 field evidence、不合成真实 focused response、不替代 full response/package/router/replay/holdout、不恢复模型链、不写 actuator 或 release gate。
- 2026-06-22 新增 `R8u127_focused_catalyst_response_repair_work_order`：承接 R8u126 的 source preflight，把 `FOCUSED_CATALYST_RESPONSE_PATH` focused catalyst 外部响应入口从“能诊断 source/row/batch 阻断”推进到“能生成可执行修复工单”。此前 R8u126 已能区分未设置、缺文件、invalid JSON 和 root not object，但 row-level 阻断、共同 batch 阻断与 source 阻断仍分散在 merge preflight 中，operator/后续 agent 仍要重新扫描。现已在 `src/water_ai/focused_catalyst_response_merge.py` 中新增 `build_focused_catalyst_response_repair_work_order()`，生成 `outputs/focused_catalyst_response_merge/focused_catalyst_response_repair_work_order.json`，统一输出 `work_order_status`、`repair_item_count`、`highest_priority_repair_id`、`matched_batch_deficit`、source/merge status、逐项 `repair_items`、下一 operator action 和 no-write/evidence boundary。默认未设置 env 时状态为 `focused_catalyst_response_repair_work_order_waiting_for_external_response`，只有 1 个 P0 修复项 `FOCUSED_SOURCE_SUBMIT_RESPONSE`，要求填写 `focused_catalyst_response_template.json` 的真实 field 值并设置 `FOCUSED_CATALYST_RESPONSE_PATH`；若 source 文件坏则转为 source repair，若六行已提交但共同 batch 不足则转为 `FOCUSED_BATCH_ALIGNMENT`，若候选通过则状态进入 `ready_for_FIELD_ACTIVATION_RESPONSE_PATH_candidate`。runner、manifest、focused merge Markdown 和 Agent50 scorecard/manifest 已接入该工单。验证：focused merge 单测 `4 passed`，Agent50 单测 `37 passed`，focused merge + field activation + governance + external router + Agent54 targeted tests `95 passed`，完整回归 `545 passed`，CodeGraph 刷新为 `347 files / 4600 nodes / 7304 edges`。该轮只把 focused 外部响应修复路径结构化，不生成 field evidence、不合成真实 response、不替代 full response/package/router/replay/holdout、不恢复模型链、不写 actuator 或 release gate。
- 2026-06-22 新增 `R8u126_focused_catalyst_response_source_preflight`：承接 R8u125 的 focused handoff，继续降低当前最高外部阻断 `FOCUSED_CATALYST_RESPONSE_PATH` 的执行摩擦。R8u125 已把下一步从 33 行 full response 收缩到 6 行 catalyst focused response，但 `experiments/run_focused_catalyst_response_merge.py` 对 source loading 的诊断仍偏粗：如果 env var 填错路径、JSON 语法错误或根对象不是 object，容易退回默认模板等待态，operator 很难分清“未设置”和“设置错”。现已在 `src/water_ai/focused_catalyst_response_merge.py` 中新增 `preflight_focused_catalyst_response_source()`，在 `outputs/focused_catalyst_response_merge/focused_catalyst_response_source_preflight.json` 输出 `source_preflight_status`、`source_load_status`、`can_run_merge_preflight`、row count、next action 和 no-write boundary；merge preflight 若 source 不可读，会进入 `focused_catalyst_response_merge_blocked_at_source_preflight`，下一步为修复 `FOCUSED_CATALYST_RESPONSE_PATH` 文件或 JSON 形状，而不是泛化等待。runner、manifest、focused merge Markdown 和 Agent50 scorecard/manifest 已接入该 source preflight。当前默认未设置 env 时状态为 `focused_catalyst_response_source_using_default_template`，`can_run_merge_preflight=True`，merge 仍正确等待真实 focused response。验证：focused merge + Agent50 targeted tests `41 passed`，focused merge + field activation + governance + external router + Agent54 targeted tests `95 passed`，完整回归 `545 passed`，CodeGraph 刷新为 `347 files / 4584 nodes / 7287 edges`。该轮只增强 focused 外部响应源诊断，不生成 field evidence、不合成真实响应、不替代 full response/package/router/replay/holdout、不恢复模型链、不写 actuator 或 release gate。
- 2026-06-22 新增 `R8u125_field_activation_response_focus_handoff`：承接 R8u124 的 completion ledger，修复一个高边际价值接口断点：ledger 已能指出 `next_hidden_state_focus=catalyst_activity`，但治理层下一步仍停留在“填完整 33 行 response”的泛化动作，没有自动路由到 R8u111/R8u112 已存在的 6 行 focused catalyst 小包。现已新增 `build_field_activation_response_focus_handoff()` 与 `outputs/model_core_governance/field_activation_response_focus_handoff.json`，把 completion ledger、`catalyst_response_submission_kit_metrics.json` 和 `focused_catalyst_response_merge_preflight.json` 接成正式 handoff，并把该 handoff 回接 external activation router，避免 router 仍提示旧的 full-response action。当前默认状态为 `field_activation_response_focus_handoff_ready_for_catalyst_activity`，目标隐藏状态为 `catalyst_activity`，focused response 行数为 6，全量 response 行数为 33，`row_scan_reduction_ratio=0.818`，下一步为填写 focused catalyst 模板、设置 `FOCUSED_CATALYST_RESPONSE_PATH`、运行 `experiments/run_focused_catalyst_response_merge.py`，再把合并候选作为 `FIELD_ACTIVATION_RESPONSE_PATH` 重跑 field activation/Agent50。Agent50 推荐已从 `FIELD_ACTIVATION_RESPONSE_SUBMISSION_PACKET_NEXT_ACTION` 切换为 `FIELD_ACTIVATION_RESPONSE_FOCUS_HANDOFF_NEXT_ACTION`，external activation router 的 `next_operator_action` 也同步切到 focused handoff。验证：field activation 单测 `37 passed`，Agent50 单测 `37 passed`，external router 单测 `10 passed`，field activation + governance `74 passed`，field activation + governance + external router + Agent54 targeted tests `91 passed`，完整回归 `544 passed`，CodeGraph 刷新为 `347 files / 4576 nodes / 7275 edges`。该轮只减少外部 operator 填报/采集摩擦，不生成 field evidence、不替代完整 response/package/router/replay/holdout、不恢复模型链、不写 actuator 或 release gate。
- 2026-06-22 新增 `R8u124_field_activation_response_completion_ledger`：承接 R8u123 的证据语义修正，继续处理当前最高阻断 `FIELD_ACTIVATION_RESPONSE_PATH` 的工程摩擦。此前 response template、preflight、repair work order、coherence audit 和 downstream preview 都已存在，但“33 行外部响应到底完成了多少、哪个 hidden_state 先补、哪些 issue scope 仍阻断”仍分散在多个 artifact 中。现已新增 `build_field_activation_response_completion_ledger()` 与 `outputs/model_core_governance/field_activation_response_completion_ledger.json`，按响应行、hidden_state 和 table 聚合完成度；默认无外部响应时状态为 `field_activation_response_completion_waiting_for_external_response`、`completion_ratio=0.0`、`completed_response_row_count=0`、`next_hidden_state_focus=catalyst_activity`，明确当前仍只是模板。`experiments/run_field_activation_matrix.py`、field activation Markdown、manifest、Agent50 scorecard、new core interface 摘要、external resume 条件与 governance report 已接入该 ledger。验证：field activation 单测 `34 passed`，field activation + governance `71 passed`，field activation + governance + external router + Agent54 targeted tests `88 passed`，完整回归 `541 passed`，CodeGraph 刷新为 `347 files / 4559 nodes / 7244 edges`。该轮只衡量真实响应包填写进度和机器可读性，不生成 field evidence、不运行 replay/holdout、不恢复模型链、不写 actuator 或 release gate。
- 2026-06-22 新增 `R8u123_downstream_preview_deferred_metric_semantics_fix`：复核 R8u121/R8u122 后发现一个证据边界语义风险：当 downstream preview 因 R8u105 materialized package 未 ready 而没有执行时，若只输出若干 count=0，容易被误读为“R7/Agent44 或 path/endpoint 没有缺口”。现已在 R7 preview 与 path/endpoint preview 结果中新增 `preview_metric_evaluation_status` 和 `not_evaluated_metric_names`：默认状态明确为 `deferred_until_materialized_package_preflight_ready`，并列出未评估的 downstream 指标；path/endpoint preview 还新增 `path_endpoint_required_table_count=6` 与 `path_endpoint_contract_minimum_matched_batch_count=5`，让未执行状态也能显示合同门槛。Agent50、manifest、field activation Markdown 与 governance report 已接入这些语义字段。验证：field activation + governance 单测 `68 passed`，field activation + governance + external router + Agent54 targeted tests `85 passed`，完整回归 `538 passed`，CodeGraph 刷新为 `347 files / 4535 nodes / 7220 edges`。该轮只修复未评估指标的语义边界，不生成 field evidence、不运行 downstream replay/holdout、不恢复模型链、不写 actuator 或 release gate。
- 2026-06-22 新增 `R8u122_field_activation_downstream_path_endpoint_preflight_preview`：承接 R8u121 的 downstream preview 思路，继续检查同一个 field activation materialized package 是否会被 R8u66/Agent54 path-endpoint label preflight 阻断。R8u121 只预览 R7/Agent44 导入门，仍不能提前暴露路径阶段标签、最终出水终点标签、共同 batch、operation log、offline lab rows 和 release gate 端点证据缺口。现已新增 `preview_field_activation_downstream_path_endpoint_preflight()`，在 R8u105 materialized preflight ready 后只读读取 materialized package 的 path/endpoint CSV，并调用 `preflight_field_path_endpoint_label_package()`，输出 `field_activation_downstream_path_endpoint_preview.json`。默认未提交外部 response 时，preview 正确停在 `field_activation_downstream_path_endpoint_preview_blocked_by_materialized_package_preflight`；测试中的 ready materialized package 会实际执行 Agent54 preflight，并暴露 `field_activation_downstream_path_endpoint_preview_blocked_by_path_endpoint_preflight`，证明 R8u105 通过也不等于 path/endpoint layout holdout ready。Agent50、manifest 和 field activation Markdown 已接入 preview status、executed、preflight status、matched batch、deficit、highest blocker 与 next action。验证：field activation 单测 `31 passed`，field activation + governance + external router + Agent54 targeted tests `85 passed`，完整回归 `538 passed`，CodeGraph 刷新为 `347 files / 4528 nodes / 7213 edges`。该轮只做 downstream path/endpoint no-write 预检，不恢复模型链、不运行 layout holdout/replay、不写 actuator 或 release gate，也不生成 field-supported claim。
- 2026-06-22 新增 `R8u121_field_activation_downstream_r7_preflight_preview`：承接 R8u120 的 materialized package row blueprint gate，继续检查“上游 no-write 包物化通过后，下游 R7/Agent44 是否真的能导入”。此前 `preflight_field_activation_materialized_package()` 只能证明 operator 物化目录匹配 staging manifest、metadata/CSV/row blueprint 没有明显工程断链，但不能证明这个目录会通过 R7 real field replay package preflight。现已新增 `preview_field_activation_downstream_r7_preflight()`，在 R8u105 materialized preflight ready 后只读调用 `preflight_field_replay_package()`，输出 `field_activation_downstream_r7_preview.json`，暴露 R7 files/header、真实行、placeholder metadata、Agent44 类型转换、必需字段和 batch linkage 阻断。默认未提交外部 response 时，preview 正确停在 `field_activation_downstream_r7_preview_blocked_by_materialized_package_preflight`；测试中的 ready materialized package 会实际执行 R7 preview，并暴露 `field_activation_downstream_r7_preview_blocked_by_r7_preflight`，证明 R8u105 通过不等于 R7/Agent44 可进入 timestamped replay。Agent50、manifest 和 field activation Markdown 已接入 preview status、executed、Agent44 import status、R7 can pass、highest blocker 与 next action。验证：field activation 单测 `29 passed`，field activation + governance + external router targeted tests `76 passed`，完整回归 `536 passed`，CodeGraph 刷新为 `347 files / 4511 nodes / 7191 edges`。该轮只做下游 no-write 预检，不恢复模型链、不运行 replay/holdout、不写 actuator 或 release gate，也不生成 field-supported claim。
- 2026-06-22 新增 `R8u120_field_activation_package_row_blueprint_gate`：承接 R8u119 的 `evidence_value` 值本体合同，继续修复 response 到外部 package 的物化断点。此前 staging manifest 只列出 table、required columns、source response row ids，但没有明确“哪条 response 的 `evidence_value` 应填入哪个 CSV 字段”，导致 operator 物化包时仍可能丢失或错填值本体。现已在 `build_field_activation_package_staging_manifest()` 中新增 no-write `row_blueprints` 和 `value_payload_mappings`：当 response preflight 与 assembly ready 后，每张表会生成由 batch/timestamp/node/sensor/custody/method 等身份列和实际 payload 字段组成的 CSV 行蓝图；`preflight_field_activation_materialized_package()` 进一步检查 operator 物化出的 CSV 是否匹配这些蓝图，若 CSV 行未承接 response payload，会触发 `R8U105_TABLE_BLUEPRINT_ROWS_MISSING`。默认未提交外部 response 时，`selected_row_blueprint_count=0`、`selected_value_payload_mapping_count=0`，这是正确等待态；测试中的 ready response 可生成 row blueprint 并通过 materialized package preflight，故意改错 CSV payload 会被阻断。Agent50、manifest 和 field activation Markdown 已接入 staging blueprint 与 materialized blueprint missing 指标。验证：field activation 单测 `27 passed`，field activation + governance targeted tests `29 passed, 35 deselected`，完整回归 `534 passed`。该轮只把 operator-supplied response payload 映射到 no-write package CSV 蓝图，不生成 field evidence、不运行 replay/holdout、不恢复模型链、不写 actuator 或 release gate。
- 2026-06-22 新增 `R8u119_field_activation_response_value_payload_contract`：复核 R8u118 后发现一个更贴近工程 replay 的接口缺口：`FIELD_ACTIVATION_RESPONSE_PATH` 行级响应此前要求 `evidence_value_reference`，可追溯“值在哪里”，但没有强制要求可计算的实际值 payload，存在“只有引用路径、没有机器可读值”也可能通过 response preflight 的风险。现已在 `src/water_ai/field_activation_matrix.py` 中将 `evidence_value` 加入 `RESPONSE_ROW_REQUIRED_FIELDS` 和响应模板，`preflight_field_activation_response()` 新增 `missing_value_payload_row_count` 与 `template_value_payload_row_count`，并把这两类阻断接入 repair work order、submission packet、Agent50 scorecard、manifest 和 field activation Markdown。当前默认模板状态为 `missing_value_payload_row_count=0`、`template_value_payload_row_count=33`、`repair_item_count=7`，说明所有 33 行仍等待 operator 填入真实的 measured value / label / event flag / JSON payload；只有 `evidence_value_reference` 不再足够进入 package assembly。新增测试证明：填满 provenance 但删除 `evidence_value` 会被 response preflight 阻断；填入 `evidence_value` 后才允许进入后续 coherence/package assembly 候选。验证：field activation + governance targeted tests `28 passed, 35 deselected`。该轮只加强外部响应的可计算值契约，不生成 field evidence、不运行 replay/holdout、不恢复模型链、不写 actuator 或 release gate。
- 2026-06-22 新增 `R8u118_field_activation_coherence_gate_semantics_fix`：复核 R8u117 后发现一个阶段门控语义问题：默认尚未提交 `FIELD_ACTIVATION_RESPONSE_PATH` 时，`field_activation_response_coherence_audit.json` 虽然状态为 `field_activation_response_coherence_audit_waiting_for_response_preflight`，但仍把模板行缺失 timestamp/node/sensor/method 等字段计入 hard blockers，容易误读为 coherence 审计本身已经发现 30 个硬阻断。现已修正为：在 `response_preflight` 未 ready 前，coherence checks 标记为 `coherence_checks_deferred_until_response_preflight_ready`，`hard_blocker_count=0`、`warning_count=0`、`blockers=[]`、`warnings=[]`；只有外部响应先通过行级 preflight 后，才执行 batch/node/sensor/custody/method 一致性硬阻断。Agent50、package assembly 和 manifest 均已刷新，当前推荐仍为 `FIELD_ACTIVATION_RESPONSE_SUBMISSION_PACKET_NEXT_ACTION`，router 下一步仍为 `fill_response_template_and_set_FIELD_ACTIVATION_RESPONSE_PATH`。验证：field activation targeted tests `27 passed, 35 deselected`，全量回归 `532 passed`。该轮只修正证据门控归因，不生成 field evidence、不恢复模型链、不写 actuator 或 release gate。
- 2026-06-22 新增 `R8u117_field_activation_response_coherence_audit`：在 R8u116 之后，继续压实 `FIELD_ACTIVATION_RESPONSE_PATH` 真实外部响应入口。`src/water_ai/field_activation_matrix.py` 新增 `audit_field_activation_response_coherence()`，`experiments/run_field_activation_matrix.py` 现在输出 `outputs/model_core_governance/field_activation_response_coherence_audit.json`，并把该 audit 接入 package assembly、repair work order、external readiness gate、response submission packet、manifest 和 Agent50 scorecard。该 audit 不证明现场数据真实有效，只检查填好的 response 是否能按隐藏状态形成可回放证据组：同一隐藏状态的 batch_id 是否可对齐，sensor/operation 行是否具备 timestamp/node_id/sensor_id，offline lab 行是否具备 method/detection limit，chain-of-custody 与 node 映射是否需要复核。当前默认仍未提交外部响应，因此 `audit_status=field_activation_response_coherence_audit_waiting_for_response_preflight`，router 下一步仍为 `fill_response_template_and_set_FIELD_ACTIVATION_RESPONSE_PATH`。新增测试覆盖模板等待、碎片化 batch 阻断和自洽响应通过组装；全量回归为 `532 passed`。该轮只减少外部响应进入包组装和 router 前的工程一致性风险，不生成 field evidence、不运行 replay/holdout、不恢复模型链、不写 actuator 或 release gate。
- 2026-06-22 新增 `R8u116_external_activation_router_field_activation_upstream_gate`：在 R8u115 之后，继续修正 external activation router 的执行顺序一致性。`src/water_ai/external_activation_router.py` 和 `experiments/run_external_activation_router.py` 现在会消费 `outputs/model_core_governance/field_activation_external_readiness_gate.json` 与 `outputs/model_core_governance/field_activation_response_submission_packet.json`，并把 `field_activation_upstream_gate` 摘要挂到 R7 route row。当前真实状态为：`priority_route_status=activation_route_blocked_by_field_activation_upstream_gate`，最高阻断为 `R7_REAL_FIELD_PACKAGE:field_activation_upstream_not_ready:R8U106_SUBMIT_FIELD_ACTIVATION_RESPONSE:field_activation_external_readiness_waiting_for_external_response`，下一步为 `fill_response_template_and_set_FIELD_ACTIVATION_RESPONSE_PATH`，而不是直接 `set_REAL_FIELD_REPLAY_PACKAGE_DIR`。优先级规则为：已提交真实 R7 路径仍优先完整 R7 preflight；R8u114 若产生可提交 candidate，则提示 candidate；否则在 field activation 上游未 ready 时先补 `FIELD_ACTIVATION_RESPONSE_PATH`。Agent50 scorecard、route summary、external resume conditions 和 manifest 已消费该状态。该轮只让 router 的操作顺序对齐 field activation 证据链，不生成 field evidence、不运行 replay/holdout、不恢复模型链、不写 actuator 或 release gate。
- 2026-06-22 新增 `R8u115_external_activation_router_catalyst_patch_candidate_consumption`：在 R8u114 之后，更新 `src/water_ai/external_activation_router.py`、`experiments/run_external_activation_router.py` 和 Agent50 治理摘要，使 `outputs/model_core_governance/external_activation_router.json` 能消费 `outputs/catalyst_slice_r7_patch_candidate/catalyst_slice_r7_patch_candidate_metrics.json`。R7 路由行现在包含 `catalyst_slice_r7_patch_candidate` 摘要，顶层 router/manifest/Agent50 scorecard 也暴露候选补丁的 `patch_status`、`candidate_materialized`、`candidate_preflight_status`、`remaining_gap_count`、`candidate_package_dir` 和 `can_submit_candidate_as_REAL_FIELD_REPLAY_PACKAGE_DIR`。R8u115 的 candidate 默认状态为 `catalyst_slice_r7_patch_waiting_for_valid_catalyst_slice`、`can_submit_candidate_as_REAL_FIELD_REPLAY_PACKAGE_DIR=False`；如果未来 R8u114 生成可提交 candidate，router 可提示 `set_REAL_FIELD_REPLAY_PACKAGE_DIR_to_catalyst_patch_candidate`，但仍必须由 operator 显式设置环境变量并通过完整 R7 preflight 后才能恢复模型链。R8u116 已进一步把当前默认下一步改为先补 field activation response。该轮只减少外部真实数据接入摩擦，不生成 field evidence、不运行 Agent51/Agent49、不写 actuator 或 release gate。
- 2026-06-22 新增 `R8u114_catalyst_slice_r7_patch_candidate`：在 R8u113 四表催化剂活性切片之后，新增 `src/water_ai/catalyst_slice_r7_patch_candidate.py`、`experiments/run_catalyst_slice_r7_patch_candidate.py`、`outputs/catalyst_slice_r7_patch_candidate/catalyst_slice_r7_patch_candidate_metrics.json` 和 `deliverables/model_core_optimization/catalyst_slice_r7_patch_candidate.md`。该接口把通过预检的 `CATALYST_FIELD_PACKAGE_SLICE_DIR` 覆盖进 full R7 field package candidate，并立即运行 `preflight_field_replay_package()`，从而区分“catalyst_activity 四表补丁已可用”和“完整 R7 包仍缺 metadata、sensor_timeseries、fast_proxy_event_log、pressure_headloss_event_log、path/endpoint labels 等全包证据”。当前默认状态为 `catalyst_slice_r7_patch_waiting_for_valid_catalyst_slice`，因为还没有外部真实 catalyst slice；这是正确阻断。即使未来 valid slice 可物化为 candidate，也只有当 full R7 preflight 通过时，才允许 `can_submit_candidate_as_REAL_FIELD_REPLAY_PACKAGE_DIR=True`；该接口本身仍不能运行 Agent51 holdout、解除 Agent49 catalyst guardrail、写 actuator 或 release gate。
- 2026-06-22 新增 `R8u113_catalyst_field_package_slice`：在 R8u112 focused response merge 之后，继续把 `catalyst_activity` 六条补证行落到 R7/Agent51 可消费的四表现场数据切片。新增 `src/water_ai/catalyst_field_package_slice.py`、`experiments/run_catalyst_field_package_slice.py`、`outputs/catalyst_field_package_slice/catalyst_field_package_slice_metrics.json`、`outputs/catalyst_field_package_slice/focused_field_package_slice_template/` 和 `deliverables/model_core_optimization/catalyst_field_package_slice.md`。该切片模板包含 `node_modality_sensor_timeseries` 9 行、`offline_lab_results` 3 行、`campaign_operation_log` 3 行和 `site_topology_or_bed_geometry` 1 行，要求至少 3 个 shared batch 同时出现在三类动态证据中，并要求真实 `data_origin=field`、QA 通过的 `catalyst_activity` 离线标签、可解析的 `regeneration_event` 和正值床层几何。当前默认状态为 `catalyst_field_package_slice_waiting_for_CATALYST_FIELD_PACKAGE_SLICE_DIR`，因为还没有外部真实四表切片目录；这是正确阻断。即使未来该切片预检通过，也只表示可以作为 full R7 field package 的 patch candidate，仍不能直接运行 Agent51 holdout、解除 Agent49 catalyst guardrail、写 actuator 或 release gate。
- 2026-06-22 新增 `R8u112_focused_catalyst_response_merge_preflight`：在 R8u111 focused submission kit 之后，新增 `outputs/focused_catalyst_response_merge/focused_catalyst_response_merge_preflight.json`、`merged_full_field_activation_response_candidate.json` 和 `deliverables/model_core_optimization/focused_catalyst_response_merge.md`。该入口读取 `FOCUSED_CATALYST_RESPONSE_PATH` 指向的外部 focused catalyst response，先检查 6 行的真实 `data_origin=field`、no-write、证据引用和共同 batch，再按 merge plan 替换回 33 行 full field activation response candidate。当前默认状态为 `focused_catalyst_response_merge_waiting_for_FOCUSED_CATALYST_RESPONSE_PATH`，因为还没有外部 focused 响应；这是正确阻断。即使未来该预检通过，也只表示可以把 merged candidate 设置为 `FIELD_ACTIVATION_RESPONSE_PATH` 继续跑 R8u98/R8u108，不表示 full response preflight、field package、Agent51 holdout 或 Agent49 guardrail 已通过。
- 2026-06-22 新增 `R8u111_catalyst_response_submission_kit`：在 R8u110 focused gate 之后，新增 `outputs/catalyst_response_submission_kit/catalyst_response_submission_kit_metrics.json`、`focused_catalyst_response_template.json`、`focused_catalyst_response_schema.json`、`focused_to_full_response_merge_plan.json` 和 `deliverables/model_core_optimization/catalyst_response_submission_kit.md`。该小包把 33 行 full field activation response 缩成 `catalyst_activity` 的 6 行，降低外部 operator 填写真实 `FIELD_ACTIVATION_RESPONSE_PATH` 前的 scan 摩擦。当前 `kit_status=catalyst_response_submission_kit_ready_for_operator_fill`，`target_response_row_count=6`，模板要求至少 3 个共同 `batch_id`、真实 `data_origin=field`、证据引用和 no-write 确认；merge plan 明确只能按 `response_row_id` 把 6 行替换回 full response，剩余 27 行仍可能阻断全量 preflight。该小包不能替代 full response、不能进入 Agent51 holdout、不能解除 Agent49 保护、不能写 actuator 或 release gate。
- 2026-06-22 新增 `R8u110_catalyst_evidence_response_gate`：在 R8u109 observation response bridge 之后，新增 `outputs/catalyst_evidence_response_gate/catalyst_evidence_response_gate_metrics.json` 和 `deliverables/model_core_optimization/catalyst_evidence_response_gate.md`。该门控只检查 `catalyst_activity` 六条优先 response rows 是否完成真实 `data_origin=field`、no-write 确认、证据引用和至少 3 个共同 `batch_id`，用于把“知道该补哪 6 行”推进到“这 6 行是否够进入 focused package preflight”。当前默认状态为 `catalyst_evidence_response_gate_waiting_for_FIELD_ACTIVATION_RESPONSE_PATH`，`row_level_preflight_pass=False`，`matched_batch_count=0`，因为还没有外部填写后的响应 JSON；这是正确阻断。即使未来该聚焦门通过，也只能进入 focused materialized package preflight，仍不能直接运行 Agent51 holdout、解除 Agent49 催化剂不确定性保护、写 actuator 或 release gate。
- 2026-06-22 新增 `R8u109_observation_response_bridge`：在 R2/Agent48/51/54 的观测弱轴合同与 R8u108 field activation response submission packet 之间，新增 `outputs/observation_response_bridge/observation_response_bridge_metrics.json` 和 `deliverables/model_core_optimization/observation_response_bridge.md`。该桥把当前最硬的隐藏状态缺口 `catalyst_activity` 映射到 6 条优先补证行：N3 催化床出口 UV254、ORP、催化床压降/水头损失、离线 catalyst_activity 标签、再生事件和 nominal HRT/床层几何。当前 `required_role_coverage_rate=1.000`，说明 response template 内已有完整角色入口；但 `can_route_to_agent51_field_proxy_holdout=False`、`can_relax_agent49_catalyst_uncertainty_block=False`，因为还没有真实 field rows 和 Agent51 holdout 通过。Agent50 已消费该桥接指标，并在 scorecard 与 field evidence wait status 中暴露 bridge 状态、目标隐藏状态、响应行数和 no-write 边界。该轮增强的是“从观测弱轴到现场补证”的可执行接口，不生成 field evidence、不恢复模型链、不写 actuator 或 release gate。
- 2026-06-22 新增 `R8u108_field_activation_response_submission_packet`：在 R8u106 external readiness gate 与 R8u107 推荐层之上，新增 `outputs/model_core_governance/field_activation_response_submission_packet.json`，把“外部人员/后续 agent 下一步到底怎么提交填写后的 field activation response”压成一个可机读提交包。该包集中暴露 `source_env_var=FIELD_ACTIVATION_RESPONSE_PATH`、模板路径、必填 top-level/row 字段、33 行响应要求、最高阻断 `R8U106_SUBMIT_FIELD_ACTIVATION_RESPONSE`、下一步 `fill_response_template_and_set_FIELD_ACTIVATION_RESPONSE_PATH`、验证命令和 no-write 边界。默认状态为 `field_activation_response_submission_packet_waiting_for_external_response`；如果填好的外部 JSON 通过 response preflight，则切换为 `field_activation_response_submission_packet_response_ready_for_package_assembly`，但仍不能直接恢复模型链、写 actuator 或 release gate。Agent50 顶层推荐已从 R8u106 gate 动作升级为 `FIELD_ACTIVATION_RESPONSE_SUBMISSION_PACKET_NEXT_ACTION`，让阶段边界的下一步从“知道卡在哪”变成“知道如何提交并预检第一份真实响应包”。
- 2026-06-22 新增 `R8u107_field_activation_external_readiness_recommendation`：在 R8u106 顺序门已经正确识别第一阻断后，修正 Agent50 顶层推荐层，避免报告仍泛化输出 `WAIT_real_field_package_or_new_core_interface`。现在当 `field_activation_external_readiness_gate` 存在且外部 field blocker active 时，`recommended_next_core_action.task_id` 会切换为 `FIELD_ACTIVATION_EXTERNAL_READINESS_NEXT_ACTION`，并直接暴露 `first_blocked_step=response_source`、`blocked_by=R8U106_SUBMIT_FIELD_ACTIVATION_RESPONSE`、`next_operator_action=set_FIELD_ACTIVATION_RESPONSE_PATH_to_filled_external_response_json`。`deliverables/manifest.json` 也新增 `latest_agent50_recommended_next_core_action*` 与 `latest_agent50_field_activation_external_readiness_*` 指针，后续只读 manifest 的 agent 不需要扫描 priority/core gate 也能知道第一操作。该轮只让治理推荐层对齐已有顺序门，不改变 field evidence 判定、不恢复模型链、不写 actuator 或 release gate。
- 2026-06-22 新增 `R8u106_field_activation_external_readiness_gate`：在 R8u105 materialized package preflight 之后，新增 `outputs/model_core_governance/field_activation_external_readiness_gate.json`，把 field activation 的 response source、schema、response preflight、repair work order、package assembly、staging manifest 和 materialized package preflight 串成一个顺序门。它解决了一个真实工程接入问题：external activation router 顶层在无包路径时会提示 `set_REAL_FIELD_REPLAY_PACKAGE_DIR`，但 field activation 链条自身还没有提交填写后的 `FIELD_ACTIVATION_RESPONSE_PATH`，如果直接照 router 做会跳过上游状态级补证。R8u106 当前默认状态为 `field_activation_external_readiness_waiting_for_external_response`，`first_blocked_step=response_source`，最高阻断为 `R8U106_SUBMIT_FIELD_ACTIVATION_RESPONSE`，下一步为 `set_FIELD_ACTIVATION_RESPONSE_PATH_to_filled_external_response_json`；这比直接设置目录更符合证据链顺序。只有 response/source/schema/repair/assembly/staging/materialized package 全部通过后，才会进入 `field_activation_external_readiness_ready_for_external_activation_router`。该轮仍保持 `can_resume_model_chain=False`、`can_write_to_actuator=False`、`can_write_to_release_gate=False`，只负责排序和防误操作，不生成现场证据、不运行 replay/holdout。
- 2026-06-22 新增 `R8u105_field_activation_materialized_package_preflight`：在 R8u104 staging manifest 之后，新增 `outputs/model_core_governance/field_activation_materialized_package_preflight.json`，把 operator 物化出来的现场包目录纳入机器预检。该预检读取 staging 选中的 package pointer（默认 `REAL_FIELD_REPLAY_PACKAGE_DIR`），检查目录是否存在、`metadata.json` 是否包含 `data_origin=field`、site/campaign/operator/instrument/chain-of-custody 等必需字段，并逐张 CSV 检查 staging manifest 要求的表、列、非空行、无 TODO/template marker、行级 `data_origin=field`。当前默认状态仍正确阻断为 `field_activation_materialized_package_preflight_blocked_by_staging_manifest`，最高阻断为 `R8U105_STAGING_MANIFEST_NOT_READY`，因为默认还没有提交填写后的 field activation response。测试中的临时 materialized package 证明：当 response/staging ready 且目录中 metadata 与 CSV 满足要求时，预检可推进到 `field_activation_materialized_package_preflight_ready_for_external_activation_router`，但仍保持 `can_resume_model_chain=False`、`can_write_to_actuator=False`、`can_write_to_release_gate=False`。这轮只增加“已物化现场包目录 -> external activation router”的 no-write 闸门，不生成现场证据、不运行 replay/holdout、不写执行器或放行门。
- 2026-06-22 新增 `R8u104_field_activation_package_staging_manifest`：在 R8u99 assembly plan 与 R8u102 repair work order 之后，新增 `outputs/model_core_governance/field_activation_package_staging_manifest.json`，把已填好的 field activation response 转成 operator 可执行的 no-write 包提交清单。当前默认模板状态仍正确阻断为 `field_activation_package_staging_manifest_blocked_by_response_preflight`，`selected_channel_manifest_count=1`、`candidate_channel_requirement_count=2`，实际选中的包指针为 `REAL_FIELD_REPLAY_PACKAGE_DIR`，候选要求仍保留 `R8U66_PATH_ENDPOINT_LABEL_PACKAGE`。临时 smoke check 证明：当设置 `FIELD_ACTIVATION_RESPONSE_PATH` 指向填满 `data_origin=field`、batch/timestamp/node/sensor/lab/chain-of-custody/no-write 确认的响应 JSON 时，staging 可推进到 `field_activation_package_staging_manifest_ready_for_operator_package_materialization`，但仍保持 `can_resume_model_chain=False`、`can_write_to_actuator=False`、`can_write_to_release_gate=False`。该轮只缩短“状态级响应 -> 外部包目录 -> router preflight”的接入路径，不生成现场证据、不运行 replay/holdout、不写执行器或放行门。
- 2026-06-21 新增 `R8u103_external_activation_router_priority_summary`：把 external activation router 从“只在 `route_rows` 内部有阻断细节”升级为顶层自解释接口。`outputs/model_core_governance/external_activation_router.json` 现在直接暴露 `priority_route_channel_id`、`priority_route_status`、`priority_route_preflight_status`、`highest_priority_blocker`、`next_operator_action`、`router_validation_command` 和 `priority_route_command`；`experiments/run_external_activation_router.py`、manifest、router markdown 与 Agent50 core gate 均已消费这些字段。当前默认状态仍为 `external_activation_router_waiting_for_external_paths`，最高阻断为 `R7_REAL_FIELD_PACKAGE:REAL_FIELD_REPLAY_PACKAGE_DIR:not_set`，下一步为 `set_REAL_FIELD_REPLAY_PACKAGE_DIR`。该轮只减少外部接入链路 scan 摩擦，不改变任何 route_ready 判定，不生成 field evidence，不恢复模型链，不写 actuator 或 release gate。
- 2026-06-21 新增 `R8u102_field_activation_response_repair_work_order`：在 R8u101 外部响应源预检之后，把 source/schema/response/assembly 的阻断合并为可机读修复工单，生成 `outputs/model_core_governance/field_activation_response_repair_work_order.json`。当前默认状态为 `field_activation_response_repair_work_order_waiting_for_external_response`，R8u119 后 `repair_item_count=7`，最高优先修复项为 `R8U102_SUBMIT_FIELD_ACTIVATION_RESPONSE`，下一步是填写 `field_activation_response_template.json` 并设置 `FIELD_ACTIVATION_RESPONSE_PATH`。工单同时列出 no-write 确认、batch/evidence alignment、value payload、template marker、data_origin=field 和 assembly 阻断等修复项；它只指导 operator 修复 response 包，不生成 field evidence，不运行 replay/holdout，也不能恢复模型链、写 actuator 或写 release gate。
- 2026-06-21 新增 `R8u101_field_activation_response_source_preflight`：`experiments/run_field_activation_matrix.py` 现在支持通过 `FIELD_ACTIVATION_RESPONSE_PATH=/path/to/response.json` 提交填写后的 field activation response，并生成 `outputs/model_core_governance/field_activation_response_source_preflight.json`。默认无外部响应时，状态为 `field_activation_response_source_using_default_template`，继续使用模板跑预检并保持 `field_activation_response_blocked_before_external_package_preflight`；当临时填充的外部响应 JSON 通过 smoke check 时，状态可推进到 `field_activation_response_source_loaded_external_json`、`field_activation_response_ready_for_external_package_preflight` 和 `field_activation_package_assembly_plan_ready_for_no_write_package_staging`。该入口只让真实响应包进入预检和组装候选，不执行 replay/holdout，也不允许恢复模型链、写 actuator 或写 release gate。
- 2026-06-21 新增 `R8u100_field_activation_schema_contract/preflight`：在 R8u98 response template 与 R8u99 package assembly plan 之上，新增结构合同与结构预检，生成 `outputs/model_core_governance/field_activation_schema_contract.json` 与 `outputs/model_core_governance/field_activation_schema_preflight.json`。当前 `schema_preflight_status=field_activation_schema_preflight_passed`、`can_validate_field_activation_response_structure=True`，说明响应模板和装配计划的字段骨架、channel/table 结构与 no-write flags 已可机器验证；但 `response_preflight_status` 仍为 `field_activation_response_blocked_before_external_package_preflight`，`package_assembly_status` 仍为 `field_activation_package_assembly_plan_blocked_by_response_preflight`。这轮只打开“结构可验证”入口，不打开“现场证据成立”入口；仍不能恢复模型链、不能写 actuator、不能写 release gate，也不能把 TODO/template 行当成 field evidence。
- 2026-06-21 新增 `R8u99_field_activation_package_assembly_plan`：在 R8u98 response template/preflight 之后，新增状态级证据到外部包的组装计划，生成 `outputs/model_core_governance/field_activation_package_assembly_plan.json`。当前 `assembly_status=field_activation_package_assembly_plan_blocked_by_response_preflight`，因为 response template 仍未填写真实 field 行；`channel_plan_count=1` 表示当前模板默认填写通道仍落在 R7，`candidate_channel_plan_count=2` 表示基于矩阵的候选组装路径同时保留 `R7_REAL_FIELD_PACKAGE` 与 `R8U66_PATH_ENDPOINT_LABEL_PACKAGE`，避免 path/endpoint 标签包在现场补证时被漏掉。该计划只按 channel/table/field 分组，不能生成 field evidence，`can_stage_external_package_candidates=False`、`can_resume_model_chain=False`、`can_write_to_actuator=False`、`can_write_to_release_gate=False`。
- 2026-06-21 新增 `R8u98_field_activation_evidence_response_preflight`：在 R8u-97 field activation matrix 之上，新增状态级证据响应模板与预检。`experiments/run_field_activation_matrix.py` 现在生成 `outputs/model_core_governance/field_activation_response_template.json` 与 `outputs/model_core_governance/field_activation_response_preflight.json`；模板包含 33 行“隐藏状态-证据字段”响应项，每行要求填入真实 `data_origin=field`、`batch_id`、时间/节点/传感器或离线方法引用、chain-of-custody、operator 与 no-write 确认。当前预检状态为 `field_activation_response_blocked_before_external_package_preflight`，这是正确阻断：33 行仍含 TODO/template marker、非 field origin、缺少对齐字段且未确认 no-write，因此 `can_route_to_external_activation_router=False`、`can_resume_model_chain=False`、`can_write_to_actuator=False`、`can_write_to_release_gate=False`。Agent50 已消费该预检状态，后续真实现场补证可以直接按该模板逐行替换，而不能把模板当作 field evidence。
- 2026-06-21 新增 `R8u97_field_activation_matrix_interface`：`src/water_ai/field_activation_matrix.py` 将 Agent50 的 6 个隐藏状态逐一映射到外部证据通道、真实字段、可恢复 gate、证据边界与 no-write 边界；生成产物为 `outputs/model_core_governance/field_activation_matrix.json` 和 `deliverables/model_core_optimization/field_activation_matrix.md`。当前矩阵状态为 `field_activation_matrix_ready_for_state_level_external_collection`，覆盖 6/6 个隐藏状态，`can_resume_model_chain=False`、`can_write_to_actuator=False`、`can_write_to_release_gate=False`；其中 `catalyst_activity` 被明确绑定到 N3 催化床 UV254/ORP、`pressure_drop_kPa`、离线活性标签、再生日志和 HRT/床层几何。Agent50 已消费该接口，`NEW_CORE_INTERFACE` 的 `action_resume_state` 变为 `new_core_interface_defined_waiting_for_external_evidence`，但仍不能绕过真实 field package、replay/holdout 或人工复核。
- 2026-06-21 Agent50 runner 已修正上一轮基线读取方式：`previous_core_score` 现在读取上一轮 `latest_agent50_core_score=0.960`，`previous_module_stage_status` 读取上一轮 `latest_agent50_module_stage_status=module_stage_complete`，不再反复使用历史 `0.904` 与旧 blocker。刷新后 `iteration_delta=0.000`、`hard_blocker_resolved=False`、`effective_iteration_gate.validity_basis=stage_boundary_external_wait_not_score_gain`；本轮有效性来自阶段边界与新接口证据链，不是分数提升，也不是重复解决旧模块阶段 blocker。
- 2026-06-21 Agent50 已新增 `effective_iteration_gate`，把“本轮是否有效”的依据从单一 `iteration_validity_status` 拆成可计算判据：`score_delta_pass=False`、`stage_boundary_termination_pass=True`、`effective_iteration_pass=True`、`expansion_stop_required=True`、`validity_basis=stage_boundary_external_wait_not_score_gain`。这说明当前有效性来自阶段边界终止和外部激活等待，而不是分数增益；manifest 也已暴露 `latest_agent50_effective_iteration_gate` 等字段，后续只读 manifest/core gate 的 agent 不应把该状态解读为继续内部扩张。
- 2026-06-21 Agent50 `next_allowed_actions` 已补齐当前恢复态字段：每条 action 现在都有 `current_route_ready`、`current_model_chain_resume_ready`、`current_handoff_ready` 和 `action_resume_state`，用于区分“静态上属于 model-chain 外部包”与“当前是否真的可恢复模型主链”。R7 与 R8u-66 均为 `model_chain_blocked_waiting_for_package`，R8u-79 为 `handoff_blocked_waiting_for_package`；R8u-95 时 `NEW_CORE_INTERFACE` 仍为 `new_interface_required_before_any_resume`，当前已由 R8u-97 更新为 `new_core_interface_defined_waiting_for_external_evidence`。该轮不改变 ready 判定，只让 core gate 的恢复状态更稳定、更可计算。
- 2026-06-21 Agent50 `next_allowed_actions` 已补齐 channel-specific 恢复语义：R7 真实 field package 与 R8u-66 path/endpoint package 的 action 标记为 `activation_route_class=model_chain_external_package`、`model_chain_resume_candidate=True`，但当前 `can_resume_model_chain=False`，必须先通过各自 field preflight；R8u-79 formal search result package 标记为 `activation_route_class=formal_search_handoff_only`、`handoff_only=True`，其 boundary 明确“cannot resume field replay or control”，只能进入 nonlegal comparison、formal counsel review handoff 或 disclosure revision queue。`NEW_CORE_INTERFACE` 也显式标记为 `new_testable_core_interface` 与 `requires_tested_interface=True`。这修正了外部动作层仍用泛化 “import/replay/review gates” 描述 formal search 的问题，确保恢复动作、ready 通道和 no-write 边界保持一致。
- 2026-06-21 Agent50 core gate 已补齐 `self_interrupt_verdict` 本体回填：`outputs/model_core_governance/core_score_termination_gate.json` 不再只暴露 `stage_decision`、`next_allowed_actions` 和 `external_resume_conditions`，而是直接携带 `self_interrupt_verdict=stage_boundary_wait_for_external_activation`、对应 reason 与 `self_interrupt_mode=stage_gate_throttled_hard_gate_with_deferred_backlog`。这修正了 priority JSON/manifest 与 core gate 之间的可读性不一致，确保后续只读取 core gate 的 agent 也能知道当前不是 `continue_core_work`，而是阶段边界等待外部证据包或新核心接口，不能继续内部 synthetic/template 扩张。
- 2026-06-21 External activation router 已把泛化 `route_ready` 拆成 `model_chain_ready` 与 `handoff_ready` 两条语义通道：R7 真实 field package 和 R8u-66 path/endpoint label package 通过预检时才可进入 `model_chain_ready`，能恢复 field replay、layout holdout 等模型主链；R8u-79 formal search result package 即使通过 Agent60 formal package preflight，也只进入 `handoff_ready`，代表可交给外部/人工非法律检索审查，不代表现场控制链、field claim、actuator 或 release gate 可恢复。Agent50 scorecard、core gate 的 `external_resume_conditions`、manifest 和 router 报告均已暴露 `model_chain_ready_route_count`、`handoff_ready_route_count` 及对应 channel ids，避免把“文献/检索交接已就绪”误读成“模型现场链条可恢复”。
- 2026-06-21 External activation router 已收紧 formal search result package 路由：`R8U79_FORMAL_SEARCH_RESULT_PACKAGE` 不再因 `FORMAL_SEARCH_RESULT_PACKAGE_PATH` 文件存在就标记 ready，而是复用 Agent60 既有 `formal_search_result_package_source_preflight`、`formal_search_result_package_row_preflight` 和 `formal_search_result_validation_execution`。只有 row preflight 达到 `formal_search_result_package_row_preflight_ready_for_validation_gate` 时，router 才输出 `activation_route_ready_for_agent60_formal_search_preflight`；空壳 JSON、submission template、seed matrix 或含 TODO/template/legal/field claim 边界问题的包都会被阻断。该轮映射到验证治理层与可保护性：它防止 formal-search 外部通道把“路径存在”误当作正式检索结果可用，仍不生成 prior-art 结论、法律意见、权利要求文本或 field-supported claim。
- 2026-06-21 Agent50 core gate 已消费外部激活 router 执行态：`outputs/model_core_governance/core_score_termination_gate.json` 的 `external_resume_conditions` 现在直接包含 `router_status`、`router_consumed`、`router_route_ready_count`、`router_blocked_route_count`、`router_highest_priority_blocker`、`router_next_operator_action` 和 `router_route_summary`；`next_allowed_actions` 也为每条外部证据包动作补充 `router_route_status`、`router_operator_action`、`router_preflight_status` 与 `router_validation_command`。当前 router 状态为 `external_activation_router_waiting_for_external_paths`，最高阻断为 `R7_REAL_FIELD_PACKAGE:REAL_FIELD_REPLAY_PACKAGE_DIR:not_set`，下一步为 `set_REAL_FIELD_REPLAY_PACKAGE_DIR`。这让单个 core gate 文件即可回答“提交什么、先修哪条路由、运行哪个预检命令、是否能恢复主链”，不再需要在 manifest、router 和 priority JSON 之间来回扫描。
- 2026-06-21 Agent50 自我打断语义已与量化阶段门对齐：当 `stage_decision=stop_expansion_wait_for_real_field_package_or_new_core_interface` 时，`self_interrupt_verdict` 不再输出容易误导的 `continue_core_work`，而是输出 `stage_boundary_wait_for_external_activation`。这表示当前不是展示偏移或证据硬冲突触发的 `interrupt_and_refocus`，也不是允许继续内部扩张；系统只允许通过真实外部证据包、正式检索结果包或新的可测试核心接口恢复主链。`outputs/model_core_governance/priority_ranking.json`、Agent50 markdown 报告和 manifest latest 指针均已暴露该 verdict 与 reason。
- 2026-06-21 Agent50 阶段门已补齐机器可读恢复动作：`outputs/model_core_governance/core_score_termination_gate.json` 现在不只输出 `stage_decision=stop_expansion_wait_for_real_field_package_or_new_core_interface`，还直接给出 `next_allowed_actions` 与 `external_resume_conditions`。当前允许动作被收束为 4 类：提交 `REAL_FIELD_REPLAY_PACKAGE_DIR`、提交 `FIELD_PATH_ENDPOINT_LABEL_PACKAGE_DIR`、提交 `FORMAL_SEARCH_RESULT_PACKAGE_PATH`，或定义一个真正新的核心接口；三条外部通道当前 `can_resume_model_chain=False`，因此仍不能恢复 field replay/布局 holdout/formal review 主链。该轮映射到验证治理层与工程化能力：它没有扩张 Agent48/49 或生成 field 结论，而是把“为什么停、下一步交什么、交完恢复到哪里、哪些边界不能越过”压进核心 score gate 和 manifest latest 指针，减少后续 agent 扫描多个文件猜状态的摩擦。
- 2026-06-21 R7 真实 field package 入口已新增 `field_package_submission_repair_work_order` 和 operator response preflight：`src/water_ai/real_field_replay_pipeline.py` 现在把 submission readiness 的阻断阶段、coverage patch plan 和 path/endpoint alignment patch plan 合并成机器可读 operator work order，并生成 `field_package_submission_repair_response_template.json` 与 `field_package_submission_repair_response_preflight.json`。当前 header-only template 演练状态为 `field_package_submission_repair_work_order_blocked_at_import_preflight`、repair_item_count=`13`、highest_blocker=`R7A_IMPORT_PREFLIGHT`；response preflight 状态为 `repair_response_preflight_blocked_at_template_markers`、template_marker_count=`13`、can_route_to_r7_preflight=`False`。Agent50 已消费工单与 response preflight，并在 `outputs/model_core_governance/external_activation_contract.json`、`outputs/model_core_governance/priority_ranking.json` 和 manifest latest 指针中暴露对应状态。这轮映射到验证治理层与工程落地能力：它不新增 agent、不修改 Agent48/49 控制逻辑，而是把“真实包为什么不能进、现场应补哪些 metadata/CSV 行/path endpoint 标签、operator response 是否逐项填写、补完后能否重跑 R7 preflight”压成可执行接口；仍明确不能合成 field evidence，不能写 actuator，不能写 release gate。
- 2026-06-15 已按 GitHub `lzehrung/codegraph` 的 CodeGraph skill 思路接入项目级导航层：skill 已安装到 `~/.codex/skills/codegraph`，但当前机器缺少 Node.js 24.10+、`npm` 和 `codegraph` CLI，因此没有强行安装整套运行时，而是新增 `codegraph.config.json` 与 `tools/build_project_codegraph.py` 生成本地静态图谱。当前图谱入口为 `CODEGRAPH.md`，机器可读图谱位于 `deliverables/codegraph/project_codegraph.json`，并生成节点/边 CSV、`codegraph_summary.md` 与 `scan_shortcuts.md`。该层目标是减少后续 scan 摩擦：先用图谱定位 Agent、runner、source、test、deliverable、output，再进入具体模型优化；图谱只作为结构定位线索，行为结论仍必须由测试、实验或真实 field package 验证。
- Agent50 的 `model_core_goal.md` 已升级为“全局 Goal：低成本传感循环式水处理智能灰箱闭环系统”，并新增 `goal_iteration_trace.md` 记录十轮收敛过程。新版 goal 不绑定某个阶段、某个 agent 编号、某个当前问题或某次展示材料；阶段任务、具体模块、代码细节、文档和实验都只是系统演化中的自然产物。后续工作必须先映射到七层系统骨架：现场对象层、观测层、状态估计层、机理证据层、诊断决策层、闭环执行层、验证治理层，并说明它提升的是可观测性、可控性、可解释性、可验证性、可工程化或可演化性中的哪一类能力。
- 新增 `deliverables/model_core_optimization/model_maturity_patent_paper_audit.md`：把当前模型相对上次“停止流程图、回到核心模型优化”打断点的成熟度提升、创新点、工程成熟度、专利交底 readiness、论文 readiness 和下一步最高边际价值动作固化为治理审计。当前判断是：模型已从概念/演示原型提升到可接真实数据的工程验证框架和可撰写专利交底草案阶段；但没有真实 field package、field holdout、operator final review、actuator feedback 和 release validation 前，不能宣称现场闭环成立、专利授权稳或实证论文成熟。
- 新增 `deliverables/model_core_optimization/nonlegal_prior_art_seed_matrix.md` 和 `outputs/agent_architecture_consolidation/nonlegal_prior_art_seed_matrix.json`：把 WIPO/CNIPA 专利性基准、soft sensor 水处理控制、WWTP soft sensor 综述/加药控制、多智能体/MARL 污水控制、PySensors 稀疏布点、WNTR/WaterTAP/QSDsan/offline RL 等外部相邻方法整理成非法律 prior-art 种子矩阵。该矩阵只作为 formal search、人工非法律比对和专利代理人审查的输入种子；它不是正式检索结果、不是法律意见、不能生成新颖性/创造性结论，也不能升级 field-supported claim。当前 claim 收缩建议是避免把“AI/多智能体/软传感/KG/稀疏布点”单独作为主创新点，而把保护重点收敛到低成本 node-modality 感知、循环争取低频证据时间、灰箱状态估计、多智能体保护性候选、field replay/operator/release gate 的组合链。
- R8u-60 已把 Agent52 多设施控制 replay 从“Agent49 policy 与 guardrail-aware policy 两组指标”推进为控制策略 baseline comparison contract：同一 replay 表内现在对比 `agent49_policy`、`guardrail_aware_policy`、`safe_standby_rule`、`release_first_rule`、`deterministic_random_action_baseline` 和 `expert_upper_bound` 六类策略。当前 synthetic 对照显示 guardrail-aware policy 相对 Agent49 baseline 的 accuracy gain 为 `0.333`、mean regret delta 为 `0.055`、false-positive cost delta 为 `0.166`，相对 release-first 的 mismatch delta 为 `0.667`；这些指标只能更新 reward-prior、实验设计和专利/论文实施例 scaffold，不能证明 deployed control performance、patentability/inventiveness，也不能写 actuator 或 release gate。
- R8u-61 已把 Agent52 replay 结果落成 Agent61/R8p 可引用的 replay export work package：`outputs/multi_facility_replay_evaluation/agent52_replay_export/` 现在包含 `agent52_replay_export_manifest.json`、`agent52_replay_table.csv` 和 `agent52_replay_table.rows.json`。导出行覆盖 Agent61 要求的 `batch_id`、`scenario`、`policy_action_id`、`expert_action_id`、pressure-source conflict counters 和 `data_origin`，并补充 `replay_episode_id`、guardrail action、regret、baseline comparison status 和 no-write 边界。当前 `export_status=agent52_replay_export_ready_synthetic_only`、row_count=6、all_rows_field_origin=False，因此它只能作为 replay-origin synthetic candidate 和工作包接口验证，不能创建 field evidence，不能写 actuator 或 release gate。
- R8u-62 已把 Agent48 稀疏布点从“topology-aware 多策略对照”继续推进为“水力路径/循环结构覆盖契约”：`hydraulic_path_coverage_contract` 逐段检查进水基质入口、均质/暂存缓冲、反应核心、催化剂床、回流环和末端放行边界是否被当前 node-modality 布点直接或代理覆盖。当前默认 synthetic prior 下 covered_stage_count=6/6、recirculation_loop_observed=True、low_frequency_time_buffer_observed=True，说明该布点可支持 soft sensor path prior 和 control replay design prior；但 `final_effluent_directly_observed=False`、`final_release_gate_needs_effluent_label=True`，且缺 `pressure_drop/headloss` 代理与真实 topology/path labels，因此仍不能支撑 field deployment、release gate 或 actuator writeback。Agent48 deliverable、metrics、soft_sensor_interface 和 manifest 已同步该契约。
- R8u-63 已把 Agent48 的水力路径合同回接到 Agent54 软传感矩阵耦合层：`feature_contract` 新增 `hydraulic_path_feature_contract`、`hydraulic_path_feature_terms` 和 `hydraulic_path_stage_prior` 通道，把低成本观测从 `node-zone-modality-time` 张量推进为 `node-zone-modality-time-path` 张量。该轮先把路径阶段表达为训练 schema gap，明确 `final_release_gate_needs_effluent_label=True`，防止 polishing 代理观察被误写成 final effluent release gate 支持。
- R8u-64 已把 R8u-63 的路径阶段 gap 继续推进到软传感模型训练特征：`soft_sensor_model.FEATURE_COLUMNS` 新增 8 个数值化水力路径特征，包括 `hydraulic_path_coverage_rate`、`direct/proxy_hydraulic_path_coverage_rate`、`recirculation_loop_observed_flag`、`low_frequency_time_buffer_observed_flag`、`release_boundary_proxy_flag`、`final_effluent_direct_observed_flag` 和 `release_endpoint_label_missing_flag`。模型已重训为 `rf_multioutput_v4_path_stage`，训练行数 51,840，特征数 23，mean MAE 为 0.01382；Agent54 当前 `hydraulic_path_schema_ready=True`、`missing_hydraulic_path_terms=[]`。完整回归曾暴露两个接口问题并已修复：无显式 layout 时不能把“未知布点”误判成“路径完全未覆盖”，因此默认使用 `legacy_training_prior_not_field_layout` 兼容旧链路；模型输入的 `timestamp_min` 改为观测窗口相对时间，避免闭环后续批次因全局累计时间被误判 OOD。边界仍然明确：这些路径特征目前来自 Agent48 synthetic layout prior，训练集中路径特征取值是常量先验，说明接口已打通但不能证明 field path-aware performance；下一步必须补真实 `path_stage`/endpoint labels、layout holdout 和 final effluent 端点标签，才能讨论现场状态估计提升或 release gate 支持。
- R8u-65 已把 R8u-64 的“路径特征常量先验”继续推进为 synthetic layout holdout benchmark：`experiments/train_soft_sensor_model.py` 现在构造 7 个 Agent48 布点变体，覆盖低成本阶段缺口、默认代理放行、直接 effluent 高预算、cost-only effluent、deterministic random direct release、classification proxy release gap 和 topology-robust direct release。训练数据仍为 51,840 行，但按 `layout_id`、`layout_variant_id` 和 `layout_holdout_role` 轮换注入不同水力路径特征；`hydraulic_path_coverage_rate` 有 3 个取值、`direct_hydraulic_path_coverage_rate` 有 4 个取值，`final_effluent_direct_observed_flag` 与 `release_endpoint_label_missing_flag` 均有 2 个取值。模型版本升级为 `rf_multioutput_v5_path_layout_holdout`，随机 split mean MAE 为 0.0138，synthetic layout holdout mean MAE 为 0.01524；Agent54 当前 `layout_holdout_status=synthetic_layout_holdout_ready_needs_field_path_labels`，下一步变为 `R8u66_collect_field_path_endpoint_labels_for_layout_holdout`。边界：该 holdout 只证明路径/布点变体 schema 和 synthetic benchmark readiness，不证明 field path-aware performance，不允许写 release gate 或 actuator。
- R8u-66 已把 R8u-65 的“需要真实 path/endpoint labels”从泛泛缺口压成可计算 package contract 与 preflight gate：Agent54 现在输出 `field_path_endpoint_label_package_contract`、`field_path_endpoint_label_package_preflight` 和 `field_path_endpoint_label_package_template` 三个独立 JSON。该合同要求 6 张表：`site_topology_or_bed_geometry`、`node_modality_sensor_timeseries`、`hydraulic_path_stage_labels`、`final_effluent_endpoint_labels`、`campaign_operation_log`、`offline_lab_results`，且至少 5 个 `batch_id` 跨节点级传感值、路径阶段标签、末端放行标签、操作日志和实验室标签对齐。当前没有真实包，preflight 正确停在 `no_field_path_endpoint_label_package_supplied`、`matched_batch_count=0`、`can_route_to_field_layout_holdout=False`，下一步仍是提交真实 field path/endpoint rows。模板文件显式标注 `template_only=True` 与 `template_not_field_evidence`，即使误提交也会被拒收；通过 preflight 也只允许进入 field layout holdout/replay，仍不能直接写 release gate 或 actuator。
- R8u-67 已把“缺少终止条件”从 goal 文字落实为 Agent50 可运行量化 gate：`outputs/model_core_governance/core_score_termination_gate.json` 现在输出七类能力加权 `core_score`、`previous_core_score`、`iteration_delta`、`iteration_validity_status`、`stage_decision`、单轮有效迭代阈值、模块阶段门和 no-write 边界。当前 `core_score=0.904`、`iteration_validity_status=baseline_recorded_needs_next_delta`、`stage_decision=continue_core_work_with_quantified_baseline`；这只是架构/接口治理成熟度基线，不是 field validation 分数。模块阶段门仍为 `module_stage_needs_more_core_work`，唯一硬缺口是 `state_variable_coverage=0.676 < 0.90`，因此后续不应继续无界扩张，而应优先补弱隐藏状态覆盖、真实 field labels、field replay 或 source_basis detail。Agent50/manifest 已回写 `latest_agent50_core_score`、`latest_agent50_stage_decision`、`latest_agent50_module_stage_status` 和 `latest_agent50_next_gate_action`。
- R8u-68 已把 R8u-67 的 `state_variable_coverage` 粗粒度缺口拆成可追踪隐藏状态分层 ledger：Agent50 现在读取 Agent48 `hidden_state_requirement_ledger` 与 Agent51 catalyst proxy，分别计算 `state_variable_contract_coverage=1.000`、`sparse_estimation_ready_coverage=0.667`、`design_or_patch_ready_coverage=1.000`、`field_validated_state_coverage=0.000` 和 `control_ready_state_coverage=0.000`。这使模块阶段门从 `module_stage_needs_more_core_work` 变为 `module_stage_complete`，因为 6 个关键隐藏状态都已进入架构合同且补丁/代理设计可追踪；同时所有现场验证与控制写入 blocker 保持为 0，明确禁止把 synthetic/proxy/candidate patch 写成 field claim、actuator policy 或 release gate。当时 `core_score=0.960`、`previous_core_score=0.904`、`iteration_delta=0.056`，因解决上一轮模块阶段 blocker 判定为 `valid_iteration`；当前 R8u-97 复跑已修正上一轮基线读取，`previous_core_score=0.960`、`iteration_delta=0.000`，不能宣称现场闭环成立。
- R8u-69 已修正 P11 source_basis/detail 的下游消费问题：Agent59 已把 `kb_sensor_limited_release_evidence` 的 source_basis detail 展开为 citation、参数边界和 failure boundary，`source_basis_completion_rate=1.000`；但统一 Field Evidence Gate 之前只识别短 ID，不识别 `source_basis_id:...; citation:...` 展开字符串，导致重跑时误判 `citation_detail_completion_rate=0.000`。现在 `UnifiedFieldEvidenceGate` 同时识别短 ID 和展开字符串，统一门恢复 `citation_detail_completion_rate=1.000`、`source_basis_parameter_boundary_coverage=1.000`、`field_supported_edge_ratio=0.000`。Agent50 也已改为：source_basis detail 完成后不再推荐“继续补 citation”，而是明确 P11 剩余 blocker 是真实 field package、Agent44->42->43->45 证据链、field replay/holdout 与人工复核；没有真实包时不能写 actuator、release gate 或 field-supported claim。
- R8u-70 已把“缺少终止条件”的问题继续推进为 Agent50 的外部阻断路由：Agent50 现在读取 unified field evidence gate、R7 real field package acceptance、R2 observation contract 和 R3 counterfactual stress metrics，能区分“内部模型链条已形成”与“真实 field package 等待”。当前 `source_basis_detail_ready=True`、`field_import_ready=False`、`field_evidence_chain_ready=False`，P11 被标记为 `waiting_on_real_field_package_external_blocker` 并进入 `external_blocker_backlog`；R2/R3 已消费的 P1/P2/P3/P5 也不再被当作未完成旧任务。Agent50 当前推荐动作变为 `WAIT_real_field_package_or_new_core_interface`，`stage_decision=stop_expansion_wait_for_real_field_package_or_new_core_interface`，`continue_expansion_allowed=False`。这不是模型失败，而是阶段性终止条件：若没有 `data_origin=field` 的真实包，继续内部堆 P1-P11 只会把 synthetic/template/literature 加工成低边际输出；只有导入真实 field package，或定义新的核心接口/新增可验证工程约束时，才开启下一轮内部迭代。
- R8u-71 已把专业技术导图从“表达层图示”升级为可审查技术路线资产：新增 `deliverables/model_core_optimization/professional_technical_roadmap_evidence_map.md` 和 `outputs/model_core_governance/professional_technical_roadmap_evidence_audit.json`。审计把导图中的 12 条核心主张逐条绑定到 Agent50、R2、R3、R1/R7、soft sensor、grey-box、source_basis 和 patent scaffold 输出文件，标注 evidence_stage 与 field boundary。当前 `claim_count=12`、`traceable_claim_count=12`、`unsupported_claim_count=0`、`field_overclaim_count=0`、`field_supported_claim_count=0`、`no_write_boundary_preserved=true`。这轮不新增旧 P 队列功能，而是保证专业导图中的创新点、工程实现路径和成熟度判断不会越界为现场结论。
- R8u-72 已按“先优化 plan 再执行”的要求，把下一轮高边际价值动作收束为不新增 agent 的 R7 `field_evidence_sufficiency_gate`。该 gate 接入 `field_package_coverage.py` 与 R7 pipeline，把真实包分成三种状态：导入/证据不足阻断、最小 replay smoke ready、以及达到推荐校准证据量后进入 human-review candidate queue。它同时输出 `field_evidence_sufficiency_status`、`field_evidence_sufficiency_score`、`field_evidence_smoke_pass`、`field_evidence_calibration_volume_pass`、`can_route_to_agent42_smoke_replay`、`can_route_to_field_holdout`、`can_route_to_human_review_candidate`、`field_supported_claim_upgrade_ready`、`control_candidate_ready`、`release_gate_candidate_ready` 和 `no_write_boundary_pass`。当前 header-only template 演练被正确标记为 `field_evidence_sufficiency_blocked_before_import`、score=`0.26`、human_review_candidate=`False`、field_supported_claim_upgrade_ready=`False`；12 个同批次 field proxy/lab/operation/pressure 事件的测试包才会进入 `field_evidence_sufficiency_ready_for_replay_holdout_and_human_review_queue`，但仍不能写 actuator 或 release gate。
- R8u-73 已把 R8u-72 的 R7 `field_evidence_sufficiency_gate` 从局部 pipeline 指标回接到 Agent50 全局治理层。Agent50 现在读取 `outputs/r7_real_field_replay_pipeline/r7_real_field_replay_pipeline_metrics.json`，并在 governance scorecard、field evidence wait status、priority ranking 与 manifest latest 指针中暴露 `r7_field_evidence_sufficiency_status`、`r7_field_evidence_sufficiency_score`、`r7_field_evidence_smoke_pass` 和 `r7_can_route_to_human_review_candidate`。当前 Agent50 明确消费到 `field_evidence_sufficiency_blocked_before_import`、score=`0.26`、smoke_pass=`False`、human_review_candidate=`False`，因此继续给出 `WAIT_real_field_package_or_new_core_interface` 与 `stop_expansion_wait_for_real_field_package_or_new_core_interface`。测试中如果 R7 sufficiency 达到 smoke pass，Agent50 会把 `field_import_ready` 视为 True，不再误判为“尚未导入真实包”，而是转向后续 replay/holdout 路由。
- R8u-74 已把 R8u-66 的 `field_path_endpoint_label_package_preflight` 回接到 Agent50 全局治理层，避免把 R7 smoke replay 入口误读成 field layout holdout 或 release gate 证据。Agent50 现在读取 `outputs/soft_sensor_matrix_coupling/field_path_endpoint_label_package_preflight.json`，并在 governance scorecard、field evidence wait status 和 manifest latest 指针中暴露 `field_path_endpoint_label_preflight_status`、`field_path_endpoint_matched_batch_count`、`field_path_endpoint_label_package_ready`、`field_path_endpoint_final_effluent_label_ready`、`can_route_to_field_layout_holdout_with_path_labels` 和 `release_gate_endpoint_label_blocked`。当前真实状态仍为 `no_field_path_endpoint_label_package_supplied`、matched_batch_count=`0`、label_package_ready=`False`、layout_holdout_with_path_labels=`False`、release_gate_endpoint_label_blocked=`True`；缺口被明确压到 6 张现场表：`site_topology_or_bed_geometry`、`node_modality_sensor_timeseries`、`hydraulic_path_stage_labels`、`final_effluent_endpoint_labels`、`campaign_operation_log`、`offline_lab_results`。这轮仍不新增 agent，不写 actuator，不写 release gate，只是把“路径阶段/最终出水终点标签”作为更细的现场验证边界接入全局阶段门。
- R8u-75 已把 R8u-66 路径/终点标签 preflight 从“Agent54 静态输出文件”提升为 R7 真实包入口的动态 gate：`SoftSensorMatrixCouplingAgent` 现在公开 `build_field_path_endpoint_label_package_contract()` 和 `preflight_field_path_endpoint_label_package()`，R7 pipeline 直接用同一套合同检查当前 package directory 中的 `site_topology_or_bed_geometry`、`node_modality_sensor_timeseries`、`hydraulic_path_stage_labels`、`final_effluent_endpoint_labels`、`campaign_operation_log` 和 `offline_lab_results`。`load_field_replay_package()` 与 R7 template spec 已扩展读取/生成 R8u66 supplement 表头；Agent50 也改为优先消费 R7 pipeline 动态 preflight，只有 R7 未提供该字段时才退回 Agent54 静态 preflight。当前 header-only template 不再是 `no package supplied`，而是动态阻断为 `field_path_endpoint_label_package_blocked_by_preflight`、matched_batch_count=`0`、label_package_ready=`False`、layout_holdout_with_path_labels=`False`、release_gate_endpoint_label_blocked=`True`。本轮还修正了 R8p provenance 冲突：即使 R8u66 采集表包含 `data_origin` 字段，Agent61 R8p staging 仍优先从 metadata 复制 `data_origin`，避免直接信任行级来源声明。
- R8u-76 已把 R8u-75 的动态路径/终点标签 gate 继续细化为可执行的 same-batch 对齐诊断与补包计划：`field_path_endpoint_label_package_preflight` 现在输出 `table_row_counts`、`table_batch_counts`、`batch_alignment_gap_count`、`required_matched_batch_deficit`、`missing_batch_ids_by_table` 和 `alignment_patch_plan`。R7 pipeline readiness、R7 report、Agent50 governance scorecard 和 manifest latest 指针均已消费这些字段。当前 header-only template 的状态更具体：`matched_batch_count=0`、`required_matched_batch_deficit=5`、`batch_alignment_gap_count=0`、`alignment_patch_plan_status=field_path_endpoint_alignment_blocked_by_preflight`、`alignment_patch_plan_item_count=7`；也就是说现在不只是说“blocked”，而是明确至少还需要形成 5 个跨 `node_modality_sensor_timeseries`、`hydraulic_path_stage_labels`、`final_effluent_endpoint_labels`、`campaign_operation_log` 和 `offline_lab_results` 对齐的真实 batch 包。新增测试证明 2-batch 部分包会被识别为 matched=2、deficit=3，5-batch 完整包才进入 path/endpoint preflight ready；但即使 ready，仍不能绕过 R7 claim-specific/soft holdout/release gate。
- R8u-77 已把 R7 当前分散的 import preflight、minimum replay contract、path/endpoint alignment、field evidence sufficiency、R7 acceptance 和 no-write 边界合并为单一 `field_package_submission_readiness` 汇总 gate。该 gate 输出 `submission_readiness_status`、`highest_priority_blocker`、`blocking_stage_count`、`next_operator_action`、`operator_action_queue`、`can_submit_to_agent42_smoke_replay`、`can_route_to_path_endpoint_layout_holdout`、`can_route_to_human_review_candidate` 和 no-write 边界。当前 header-only template 被汇总为 `field_package_submission_blocked_at_import_preflight`，最高阻断为 `R7A_IMPORT_PREFLIGHT`，下一步为 `repair_metadata_headers_and_real_rows_before_agent42`，blocking_stage_count=`5`，且 `can_submit_to_agent42_smoke_replay=False`、`can_route_to_path_endpoint_layout_holdout=False`、`no_write_boundary_pass=True`。Agent50 已回接这些字段到 governance scorecard 与 manifest latest 指针，因此全局治理层现在能直接看到真实包入口的最高优先修复点，而不是分别翻 R7 preflight、coverage、path labels 和 acceptance gate。
- R8u-78 已按“先优化 plan 再执行”的方式，把 formal search / 专利交底审查链从多个分散 JSON 收束为 `formal_search_review_readiness` 汇总 gate。Agent60 现在聚合正式检索结果包 source preflight、row preflight、validation execution、人工非法律技术比较审查包、非法律审查回填、claim scope patch draft、外部正式审查回填、交底修订队列和 impact plan，输出 `formal_search_review_readiness_status`、`highest_priority_blocker`、`blocking_stage_count`、`next_operator_action`、`operator_action_queue` 和硬边界标志。当前状态为 `formal_search_review_blocked_at_result_package_source_preflight`，最高阻断 `FSR_SOURCE_PREFLIGHT`，下一步 `submit_formal_search_result_package`，blocking_stage_count=`9`，boundary_violation_count=`0`；这说明专利级路线不是缺写作，而是缺正式检索结果包/人工审查回填链。该 gate 明确保持 `can_generate_prior_art_result=False`、`legal_opinion_allowed=False`、`can_emit_claim_text=False`、`field_claim_upgrade_allowed=False`，只能作为非法律技术审查路由和交底修订准备，不生成法律结论、权利要求文本或 field-supported claim。
- R8u-79 已把 R8u-78 的“submit formal search result package”从抽象下一步拆成可执行 `formal_search_execution_route_plan`。该 route plan 读取 7 个 formal search work packages、正式检索结果包 submission template、R8u-78 review readiness 和已有 nonlegal prior-art seed matrix，逐工作包输出检索数据库、英文/中文查询族、分类号提示、可引用 seed references、必填结果表、manifest 必填字段、hit/comparison 必填字段、执行步骤、拒收边界和 field gate 保留要求。当前 `route_plan_status=formal_search_execution_route_plan_ready_waiting_for_external_search_execution`，`complete_route_row_count=7/7`，`mapped_seed_route_count=7`，首个动作是 `execute_external_or_human_search_and_submit_FORMAL_SEARCH_RESULT_PACKAGE_PATH`。边界仍然明确：route plan 不是正式检索结果，`can_submit_synthetic_or_template_result_package=False`、`can_generate_prior_art_result=False`、`legal_opinion_allowed=False`、`can_emit_claim_text=False`、`field_claim_upgrade_allowed=False`。因此这轮提升的是专利级成熟度的工程执行路径：人工/外部检索者现在可以按路线生产正式结果包，但系统不会伪造结果。
- R8u-80 已把 R8u-79 的 formal search execution route plan 回接到 Agent50 全局治理层。Agent50 现在读取 `outputs/agent_architecture_consolidation/formal_search_execution_route_plan.json`，在 governance scorecard、governance report、Agent50 JSON/Markdown 和 manifest latest 指针中输出 `formal_search_execution_route_plan_status`、`formal_search_execution_complete_route_row_count`、`formal_search_execution_route_row_count`、`formal_search_execution_mapped_seed_route_count`、`formal_search_execution_operator_first_action` 和 `formal_search_execution_boundary_preserved`。当前 Agent50 确认 route plan ready、7/7 路线完整、7 条路线均映射 seed、边界 preserved=True，并把它作为轻量 protectability 接口收益计入 core score；同时 blocked reasons 明确说明这只是 external/human search execution handoff，仍需要 reviewer-filled `FORMAL_SEARCH_RESULT_PACKAGE_PATH` 后才能进入 nonlegal comparison review、formal counsel review 或 patent-grade claim refinement。该回接没有解除 field/formal external blocker，也不生成法律意见、权利要求文本或 prior-art 结论。
- R8u-81 已在 Agent50 内新增 `external_activation_contract`，不新增 agent 编号，而是把当前 `WAIT_real_field_package_or_new_core_interface` 外部等待态压成可测试恢复合同。该合同统一 3 个外部入口：`R7_REAL_FIELD_PACKAGE` 使用 `REAL_FIELD_REPLAY_PACKAGE_DIR` 恢复 Agent44->42->43->45 真实现场证据链；`R8U66_PATH_ENDPOINT_LABEL_PACKAGE` 使用 `FIELD_PATH_ENDPOINT_LABEL_PACKAGE_DIR` 恢复 path/endpoint label layout holdout；`R8U79_FORMAL_SEARCH_RESULT_PACKAGE` 使用 `FORMAL_SEARCH_RESULT_PACKAGE_PATH` 恢复 formal search validation/nonlegal/formal counsel/human disclosure revision 链。当前 `contract_status=waiting_for_external_evidence_packages`、`activation_ready=False`、`ready_channel_count=0`、`blocked_channel_count=3`、`boundary_preserved=True`，并生成 `outputs/model_core_governance/external_activation_contract.json`。这轮提升的是验证治理/工程化/可保护性接口：明确何时可以离开等待态、提交什么包、哪些 template/synthetic/seed-only 输入会被拒收；它不写 actuator、不写 release gate、不生成法律意见或 field-supported claim。
- R8u-82 已新增 `external_activation_router`，把 R8u-81 的恢复合同进一步变成路径感知路由层。新增 `src/water_ai/external_activation_router.py` 和 `experiments/run_external_activation_router.py`，读取 `outputs/model_core_governance/external_activation_contract.json` 与 3 个环境变量：`REAL_FIELD_REPLAY_PACKAGE_DIR`、`FIELD_PATH_ENDPOINT_LABEL_PACKAGE_DIR`、`FORMAL_SEARCH_RESULT_PACKAGE_PATH`。router 会检查路径是否设置、是否存在、类型是否正确；对 `FIELD_PATH_ENDPOINT_LABEL_PACKAGE_DIR` 会直接调用既有 `preflight_field_path_endpoint_label_package`，避免“目录存在就算证据”。当前默认环境下未提交外部包，`router_status=external_activation_router_waiting_for_external_paths`、`path_supplied_count=0`、`route_ready_count=0`、`blocked_route_count=3`、`boundary_preserved=True`，并输出 `outputs/model_core_governance/external_activation_router.json` 与 `deliverables/model_core_optimization/external_activation_router.md`。该层只产生可执行命令建议，不执行 field replay、formal search 或任何控制/放行/法律结论。
- R8u-83 已把 R8u-82 的 `external_activation_router` 回接到 Agent50 全局治理层。Agent50 现在读取 `outputs/model_core_governance/external_activation_router.json`，并在 governance scorecard、governance report、Agent50 JSON/Markdown 和 manifest latest 指针中输出 `external_activation_router_status`、`external_activation_router_consumed`、`external_activation_router_path_supplied_count`、`external_activation_router_route_ready_count`、`external_activation_router_blocked_route_count` 和 `external_activation_router_boundary_preserved`。当前 `external_activation_router_consumed=True`，状态仍为 `external_activation_router_waiting_for_external_paths`，0 条 ready route、3 条 blocked route、boundary_preserved=True；这说明全局治理层已经能看见“外部包尚未提交”的执行态，而不是只知道抽象合同。该回接不生成现场证据、不执行 formal search、不写 actuator/release gate/legal/claim，只提升验证治理层的下游回接率与工程接入清晰度。
- R8u-84 已把 R8u-82 的 field route 从“目录存在即可 route ready”收紧为“必须通过 Agent44 field replay package preflight 才 route ready”。`src/water_ai/external_activation_router.py` 现在对 `REAL_FIELD_REPLAY_PACKAGE_DIR` 调用既有 `preflight_field_replay_package()`，并在 route row 中输出 `field_package_preflight`、`blocked_reason=field_package_preflight_not_ready` 和下一步修复动作；空目录、header-only template、placeholder metadata、non-field origin 或 Agent44 import blocker 都不会再被标为可恢复主链。只有 `field_package_preflight_ready_for_agent42` / `can_pass_to_timestamped_replay=True` 的真实包才输出 `activation_route_ready_for_r7_pipeline_execution`。`deliverables/model_core_optimization/external_activation_router.md` 也新增“预检”和“阻断原因”列，工程接包时能直接看到为什么不能进入 R7。当前默认无外部路径，状态仍正确停在 `external_activation_router_waiting_for_external_paths`。
- 新增 `deliverables/model_core_optimization/quantified_goal_termination_criteria.md`：把“缺少终止条件”的问题固化为可计算 goal 扩展。后续每轮必须按七层骨架、七类核心能力、模块成熟度、专利级 readiness、论文 readiness 和工程 readiness 评分；若单轮 `core_score` 提升小于 0.05 且没有解决 P1/P2 阻断，应停止扩张并进入复盘或 backlog。该文件把自我打断从频繁上下文重算改为阶段门控节流：只有偏离模型主链、混淆 synthetic/field、绕过 replay/release/actuator 边界，或当前小闭环已完成且继续做边际收益低时，才深度打断。
- 全局 goal 已进一步加入“专利级技术方案成熟度”作为终局上限：项目终点不是保证授权，也不是转向专利材料美化，而是把核心模型压实到足以支撑高质量专利交底的程度。后续每个高价值模块都要能回答具体技术问题、技术手段、实施例、验证指标、技术效果、现有技术区别和证据边界；若只能得到抽象 AI、多智能体、知识图谱或闭环控制表述，则不能作为核心创新点晋级。
- Agent60 已把全局 goal 的七层系统骨架从文本原则转成可计算架构复盘指标：新增 `system_spine_map`、`system_layer_board` 和 `system_spine_coverage`。当前 `system_spine_status=global_system_spine_mapped_with_frozen_expression_layer`，七层覆盖率 1.000，六类能力覆盖率 1.000；`M9_presentation_delivery` 被明确标为 `OUTSIDE_MODEL_SPINE` 并冻结，说明展示层不再混入模型骨架中心。
- Agent60 已进一步把全局 goal 中“先定义接口，再扩展功能”的原则转成模块接口契约矩阵：9 个模块均已明确 `input_contract`、`output_contract`、`state_variables`、`evidence_sources`、`transferable_metrics`、`cannot_do`、`upstream_dependencies`、`downstream_consumers` 和 `field_validation_need`。当前 `interface_contract_status=all_module_interface_contracts_complete`，接口契约覆盖率 1.000；这说明后续复盘不再只看 agent 名称和模块角色，而是检查每个模块能否向上下游交付可验证状态、指标和边界。
- 本轮按“黑箱变灰箱”的第一性原理和边际价值原则复盘 Agent 链条，先修最根基的模型联动、证据边界、观测合同与控制验证问题。
- R8g 已把 `pressure_headloss_event_log` 从 Agent30/42/44 的 schema/import 边界推进到 R7 最小 timestamped replay 契约：真实包现在必须同时具备 `sensor_timeseries`、`offline_lab_results`、`campaign_operation_log`、`fast_proxy_event_log` 和 `pressure_headloss_event_log` 五张同批次表，才能进入最小 replay smoke gate。R7 readiness 新增 `minimum_pressure_headloss_event_count`、`minimum_valid_pressure_headloss_event_count`、`minimum_invalid_pressure_headloss_event_count` 和 `minimum_valid_pressure_headloss_batch_count`。
- R8h 已把 Agent44 的 type/linkage 阻断转成 R7 可操作补包诊断：preflight 现在输出 `agent44_blocking_table_statuses`、`agent44_type_error_count`、`agent44_type_error_tables`、`agent44_required_field_blockers` 和 `agent44_linkage_blockers`；coverage patch plan 会在真实行已存在但 Agent44 仍阻断时生成 `R7A_AGENT44_TYPE_ERRORS_*`、`R7A_AGENT44_REQUIRED_FIELDS_*` 和 `R7A_AGENT44_BATCH_LINKAGE` 补包项。
- R8i 已让 Agent51 catalyst proxy holdout 能消费 `pressure_headloss_event_log` 作为 `N3_catalyst_bed:pressure_drop_kPa` 的替代水力证据源：如果节点长表缺少 catalyst bed pressure_drop，但压力/水头损失事件表具备同 batch、bed_id、正流量、matched lab sample time 和水力异常标签，Agent51 仍可构造可评分 batch。输出新增 `accepted_pressure_evidence_sources`、`pressure_headloss_event_source_batch_count`、`pressure_evidence_source_batch_counts` 和 feature row 的 `pressure_drop_source`。
- R8j/R8k 已把该压力证据源继续向控制 replay 和冲突校准边界推进：Agent49/52 现在能看到 `accepted_pressure_evidence_sources`、`pressure_evidence_source_batch_counts` 和 `pressure_headloss_event_source_batch_count`；Agent51 在 `node_modality_sensor_timeseries` 与 `pressure_headloss_event_log` 同批次压力值冲突超过容差时，会剔除该 batch 的 pressure scoreability，记录 `pressure_source_conflicts`，并要求 `operator_review_required_before_agent51_scoring`，防止两个水力来源被静默平均或任意覆盖。
- R8l 已把 pressure source conflict 接入 Agent49/52 控制 replay 影响：Agent49 的 `control_replay_guardrail_context` 现在输出 `pressure_source_conflict_count`、`pressure_source_conflict_control_block` 和 `conflict_requires_operator_review`，冲突存在时即使 Agent51 field holdout 其他指标通过，也会继续保留催化剂/水力保护；Agent52 replay row、offline metrics、readiness 和 Agent49 writeback 现在输出 `pressure_source_conflict_replay_blocked_case_count` 与 `pressure_source_conflict_requires_operator_review`，防止冲突水力代理绕过 replay 晋级门。
- R8m 已把 pressure source conflict 接入 R7 field package coverage/patch plan：当真实包中同一 batch 的 `node_modality_sensor_timeseries` 压降与 `pressure_headloss_event_log` 压降超过 `max(1.0 kPa, 0.25 * max(abs(node), abs(event)))` 容差时，coverage readiness 会输出 `pressure_source_conflict_count`、`pressure_source_conflict_requires_operator_review`、`field_package_pressure_conflict_resolution_status` 和 `field_package_pressure_conflict_resolution_ready=False`，patch plan 会生成 `R8M_PRESSURE_SOURCE_CONFLICT_FIELD_PATCH`，要求现场补充 operator review、authoritative pressure source、reviewer、review_time、calibration_action_id 和 calibration note，重跑 R7 pipeline、Agent51 holdout 与 Agent49/52 replay 后才允许考虑冲突解除。
- R8n 已把 pressure source conflict 从“发现冲突”推进到“可被 operator review / calibration 解除”：R7 coverage、Agent51 field holdout、R7 pipeline、Agent49 control context 和 Agent52 replay context 现在区分 `pressure_source_conflict_count`、`resolved_pressure_source_conflict_count`、`unresolved_pressure_source_conflict_count` 与 `pressure_source_resolution_record_count`。若补入完整 `pressure_source_resolution`、`authoritative_pressure_source`、`reviewer_id`、`review_time`、`calibration_action_id` 和 `calibration_note`，已解决冲突不再触发 Agent49 的 `pressure_source_conflict_control_block`；未解决冲突仍阻断催化剂/水力保护放松。
- R8n/R8o/R8p 衔接已把该解除门继续推进到 Agent52 replay 晋级逻辑、Agent61 场景采集包和 Agent60 架构复盘：Agent52 的 `replay_table`、`offline_evaluation_metrics`、`readiness`、`pressure_headloss_context` 和 `agent49_writeback.metric_patch` 都输出 resolved/unresolved/resolution record 字段；未解决冲突仍触发 `pressure_source_conflict_blocks_agent49_promotion`，已解决冲突不会产生该 issue。Agent61 `PressureResolutionReplayScenarioPackAgent` 已把 unresolved conflict、resolved conflict、operator review latency、Agent51 scoreability recovery、Agent49/52 guardrail clearance 固化为 R8o 场景包；Agent60 现在识别该场景包 schema ready，并在无真实包时把离线 fallback 推进到 `R8p_fix_field_rows_source_preflight`。
- 自我打断机制已从“两态硬闸门”进一步优化为“阶段门控 + 复盘节流”：`self_interrupt_mode=stage_gate_throttled_hard_gate_with_deferred_backlog`。普通新想法只进入 `stage_boundary_deferred_backlog`，不触发新 goal、不重跑项目级治理；只有纯展示/整理漂移且无模型指标变化、硬性证据矛盾、把 synthetic/template 写成 field 结论、绕过 field replay/保护边界，或当前可验证小闭环已经完成时，才允许深度复盘 Agent50/Agent60。当前 Agent50 输出 `governance_review_gate=continue_current_micro_loop`、`governance_rerun_recommended=False`，所以后续应直接承接当前核心模型小闭环，而不是反复审计上下文。
- 当前实际输出仍基于 header-only/template 演练：`accepted_pressure_evidence_sources=[]`、`pressure_headloss_event_source_batch_count=0`，R7 仍正确停在 `real_field_package_acceptance_blocked_at_import`。这说明新链路已具备代码与测试能力，但没有真实现场行时不会升级为 field-supported。
- Agent60 当前最高主任务仍是 `R7a_import_real_field_package_with_metadata_and_csv`；无真实包时的离线 fallback 已推进为 `R8p_fix_field_rows_source_preflight`。R8p 现在不再只是一句“采集真实行”：Agent61 已输出 `row_collection_plan_status=row_collection_plan_ready_needs_real_rows`、`missing_scenario_count=5`、`minimum_real_batch_count=5`、`template_row_count=30`，把每个 pressure resolution 场景拆成 batch role、必需表、非空字段、跨表 join key、Agent52 replay 必需字段和 TODO 模板。模板行均标记 `template_only=True`、`evidence_status=template_not_field_evidence`，不能导入为 field evidence，不能写 actuator 或 release gate。
- R8u 已把 R8p 从“行级采集计划”推进为“行级验收门”：Agent61 现在可读取可选 `PRESSURE_RESOLUTION_REPLAY_ROWS_PATH` 或默认 `outputs/pressure_resolution_replay_scenario_pack/pressure_resolution_replay_rows.json` 的真实行包，并输出 `field_row_acceptance`。验收要求每个场景的真实行必须非 template/TODO、具备真实 `data_origin`、同 batch 跨 `node_modality_sensor_timeseries`、`pressure_headloss_event_log`、`campaign_operation_log`、`offline_lab_results`、`fast_proxy_event_log` 和 `agent52_replay_table` 对齐，并包含 reviewer/calibration/action 链。当前状态为 `field_row_acceptance_status=no_field_replay_rows_supplied`、`accepted_field_scenario_count=0`、`accepted_field_batch_count=0`，所以仍正确停在 R8p，不会升级为 field-supported。
- R8u-2 已把 Agent61 的真实行输入路径升级为 source preflight：如果 `PRESSURE_RESOLUTION_REPLAY_ROWS_PATH` 或默认 `pressure_resolution_replay_rows.json` 缺失、JSON 无效、根结构不是 table-to-rows object、某张表不是 list、行不是 object 或出现未知表，都会写入 `field_rows_source`、`field_rows_source_status`、`invalid_table_shapes`、`unknown_tables` 和 `preflight_blockers`。当前状态为 `field_rows_source_status=field_rows_file_missing`，路径为 `outputs/pressure_resolution_replay_scenario_pack/pressure_resolution_replay_rows.json`，这说明当前阻断是输入包未提供，而不是行级验收已经失败。
- R8u-3 已生成独立真实行填报模板 `outputs/pressure_resolution_replay_scenario_pack/pressure_resolution_replay_rows_template.json`：它与默认真实输入 `pressure_resolution_replay_rows.json` 分离，包含 6 张表、30 行 TODO scaffolds，且每行均保留 `template_only=True` 与 `evidence_status=template_not_field_evidence`。这个文件用于现场填报参考，不能作为 field evidence；只有把 TODO/template 字段替换为真实 field rows 并放入真实输入路径或通过 `PRESSURE_RESOLUTION_REPLAY_ROWS_PATH` 指向，才会进入 R8p 行级验收。
- R8u-4 已把 R8p source preflight 继续细化为缺表/空表诊断：`field_rows_source` 现在输出 `missing_tables` 和 `empty_tables`。如果用户只提供部分表，会得到 `field_rows_file_loaded_with_schema_gaps`，并在 `preflight_blockers` 中出现 `<table>:missing_table`；这把“输入包表结构不完整”和“真实行内容未通过验收”分开。当前默认文件缺失时，`missing_tables` 明确列出 `agent52_replay_table`、`campaign_operation_log`、`fast_proxy_event_log`、`node_modality_sensor_timeseries`、`offline_lab_results` 和 `pressure_headloss_event_log` 六张必需表。
- R8u-5 已把 R8p 从“诊断缺什么”推进到“生成可执行补包计划”：Agent61 运行脚本现在输出 `field_rows_patch_plan`，将缺真实行文件、缺表、空表、JSON shape 问题、未知表和场景级 acceptance blocker 转成 patch item。当前默认真实行文件仍缺失，因此 `field_rows_patch_plan_status=field_rows_patch_plan_blocked_at_source_preflight`，`highest_priority_patch_id=R8P_SOURCE_MISSING_FIELD_ROWS_FILE`，`patch_item_count=12`；该补包计划只指导现场如何补齐真实行，不能写 actuator，不能写 release gate，也不能把 template/TODO 行升级为 field evidence。
- R8u-6 已把 Agent61 的 `field_rows_patch_plan` 回接到 Agent60 架构治理 fallback：当 R8o scenario schema ready 但 R8p 真实行未通过时，Agent60 不再只返回泛化的 `R8p_collect_pressure_resolution_replay_rows`，而是消费 patch plan 并把离线核心 fallback 指向 `R8p_fix_field_rows_source_preflight`。当前 Agent60 fallback 输出 `field_rows_patch_plan_status=field_rows_patch_plan_blocked_at_source_preflight`、`patch_item_count=12`、`highest_priority_patch_id=R8P_SOURCE_MISSING_FIELD_ROWS_FILE`，说明治理层已经能直接指向最高优先补包动作；边界仍是 patch plan 不是 field evidence，不能写 actuator 或 release gate。
- R8u-7 已把 R8p patch plan 继续推进为 `field_rows_operator_handoff`：Agent61 现在输出默认真实行包路径、模板路径、`PRESSURE_RESOLUTION_REPLAY_ROWS_PATH` 环境变量、验收命令、必需表字段、source/table/scenario/R8v 四级验收里程碑和模板拒绝规则。当前 handoff 状态为 `field_rows_operator_handoff_ready_needs_source_package`，默认验收命令为 `.venv/bin/python experiments/run_agent61_pressure_resolution_replay_scenario_pack.py`；Agent60 fallback 已透传 `operator_handoff_status`、`validation_command`、默认真实行路径和模板路径。这个 handoff 是现场数据接入合同，不是 field evidence，仍不能写 actuator 或 release gate。
- R8u-8 已把 R8p handoff 继续压实为机器可读真实行包 schema 合同：Agent61 现在生成 `outputs/pressure_resolution_replay_scenario_pack/pressure_resolution_replay_rows_schema.json`，并在 metrics、handoff、deliverable 和 manifest 中输出 `field_rows_package_schema_status=field_rows_package_schema_ready` 与 `rows_schema_path`。该 schema 要求真实行包根对象包含 `agent52_replay_table`、`campaign_operation_log`、`fast_proxy_event_log`、`node_modality_sensor_timeseries`、`offline_lab_results` 和 `pressure_headloss_event_log` 六张表，根对象不允许未知表；行对象允许额外现场 metadata，但必须满足 R8p 当前必填字段。schema 只验证 source/table/required-field shape，不替代 R8p acceptance，也不能写 actuator、release gate 或 field-supported claim。
- R8u-9 已把 R8p schema 合同推进为运行时 `field_rows_schema_validation`：Agent61 现在会在 source preflight 后、field row acceptance 前输出 schema 验证摘要，并把阻断区分为 `schema_validation_blocked_at_source_preflight`、table contract 缺口和 row contract 字段/类型缺口；Agent60 fallback 与 manifest 已同步消费 `field_rows_schema_validation_status`、required field gap count 和 invalid type count。当前默认真实行包仍缺失，所以状态为 `schema_validation_blocked_at_source_preflight`，`missing_table_count=6`，`schema_required_field_gap_count=0`，`schema_invalid_type_count=0`；这只说明还没有真实行包可验，不允许写 actuator、release gate 或 field-supported claim。
- R8u-10 已把 R8p 真实行包合同推进为机器可读采集清单：Agent61 现在生成 `outputs/pressure_resolution_replay_scenario_pack/pressure_resolution_replay_rows_collection_checklist.json`，把 5 个 pressure resolution 场景、6 张必需表、每个必填字段的证据角色/类型规则、四步验收顺序、技术问题-技术手段-技术效果映射和 field evidence 边界固化为可执行 checklist；Agent60 fallback 与 manifest 已同步消费 `field_rows_collection_checklist_status` 和 checklist 路径。当前状态为 `field_rows_collection_checklist_ready_needs_source_package`，仍只指导现场采集与验收，不能写 actuator、release gate、protective control candidate 或 field-supported claim。
- R8u-11 已把 R8p field provenance gate 从 `agent52_replay_table` 单表扩展到全部 6 张必需表：`node_modality_sensor_timeseries`、`pressure_headloss_event_log`、`campaign_operation_log`、`offline_lab_results`、`fast_proxy_event_log` 和 `agent52_replay_table` 的每一行都必须包含 field-origin `data_origin`。Agent61 的 acceptance 现在会拒绝任意必需表中的 synthetic/template/TODO 来源；collection checklist 中 `data_origin` 的 evidence role 为 `field_provenance_gate`，validation rule 为 `must_be_field_origin_not_template_synthetic_or_todo`。manifest 当前记录 `latest_r8p_field_rows_all_tables_require_data_origin=True`、`latest_r8p_field_rows_provenance_gate_status=all_required_tables_require_field_origin`、required table count=6。当前仍没有真实 source package，所以 gate 已压实但尚无真实行可通过；不能写 actuator、release gate、protective control candidate 或 field-supported claim。
- R8u-12 已把 R8p 的来源错误前移到 schema/provenance preflight：`field_rows_schema_validation` 现在不仅统计 `required_field_gap_count` 和 `invalid_type_count`，还统计 `field_origin_gap_count`；如果任意必需表行存在 non-field `data_origin`，会得到 `schema_validation_failed_provenance_contract`，patch plan 会生成 P0 `R8P_SCHEMA_FIELD_ORIGIN_<TABLE>`，下一步动作变为 `R8p_fix_field_origin_provenance`。Agent60 fallback 的 expected metrics 也已新增 `field_rows_schema_field_origin_gap_count`。当前默认真实行包仍缺失，所以 `field_origin_gap_count=0` 只表示还没有行可验，不表示来源通过；manifest 明确记录 `latest_r8p_field_rows_provenance_preflight_status=provenance_preflight_blocked_at_source_preflight`。
- R8u-13 已把 R8p 的 TODO/template/sample 占位值也前移到 schema/template-marker preflight：`field_rows_schema_validation` 现在统计 `template_marker_gap_count` 和 `template_marker_gaps_by_row`；如果必填字段仍含 `TODO_*`、`template_not_field_evidence`、`field_validation_required` 等占位值，会得到 `schema_validation_failed_template_marker_contract`，patch plan 会生成 P0 `R8P_SCHEMA_TEMPLATE_MARKERS_<TABLE>`，下一步动作变为 `R8p_replace_template_markers_with_field_values`。模板 marker 的优先级高于普通字段/类型修复和 provenance 修复，防止把模板行包误认为可进入场景验收。当前默认真实行包仍缺失，所以 `template_marker_gap_count=0` 也只是没有行可验；manifest 明确记录 `latest_r8p_field_rows_template_marker_preflight_status=template_marker_preflight_blocked_at_source_preflight`。
- R8u-14 已把 R8p 的同批次六表证据包完整性前移为 `field_rows_batch_bundle_preflight`：Agent61 现在生成 `outputs/pressure_resolution_replay_scenario_pack/pressure_resolution_replay_rows_batch_bundle_preflight.json`，统计 `candidate_batch_count`、`complete_bundle_count`、`partial_bundle_count`、`missing_bundle_table_count` 和每个 pressure-resolution scenario 的 `scenario_bundle_status`。如果 source/schema/template/provenance 已通过但某个 `batch_id` 缺少 `node_modality_sensor_timeseries`、`pressure_headloss_event_log`、`campaign_operation_log`、`offline_lab_results`、`fast_proxy_event_log` 或 `agent52_replay_table` 中任一张表，patch plan 会先生成 `batch_bundle_contract` 补包项，下一步动作变为 `R8p_complete_same_batch_six_table_bundles`，再进入 scenario acceptance。当前默认真实行包仍缺失，所以状态为 `batch_bundle_preflight_blocked_at_source_preflight`，complete/partial/missing 计数为 0 只表示 source 尚未加载，不表示 bundle 已完整。
- R8u-15 已把“循环/暂存结构是否真的为低频传感、快代理、离线检测和人工复核争取到时间”前移为 `field_rows_temporal_window_preflight`：Agent61 现在生成 `outputs/pressure_resolution_replay_scenario_pack/pressure_resolution_replay_rows_temporal_window_preflight.json`，检查同一 `batch_id` 下 `sensor.sample_time_min <= pressure.event_time_min <= fast_proxy.proxy_label_time_min <= offline_lab.lab_label_time_min`、pressure matched lab sample 是否落在 lab label window 内、offline sample 是否早于 lab label，以及 `campaign_operation_log.hold_time_min` 是否覆盖最慢证据到达时间。若六表同批次已完整但时间窗不成立，patch plan 会生成 `temporal_window_contract`，下一步动作变为 `R8p_fix_same_batch_timestamps_and_hold_time_budget`。当前默认真实行包仍缺失，所以状态为 `temporal_window_preflight_blocked_at_source_preflight`，temporal violation 计数为 0 只表示 source 尚未加载，不表示时间窗已通过。
- R8u-16 已把 pressure-resolution 的场景语义前移为 `field_rows_scenario_semantic_preflight`：Agent61 现在生成 `outputs/pressure_resolution_replay_scenario_pack/pressure_resolution_replay_rows_scenario_semantic_preflight.json`，在 source/schema/template/provenance、同批次六表 bundle 和 temporal-window 均通过之后，先检查未解决冲突是否仍保持 `operator_review_required` 与 `pressure_source_conflict_control_block`，已解决冲突是否具备 `authoritative_pressure_source` 与 `pressure_source_resolution_record_count`，以及 guardrail clearance 是否没有 review/control block。若语义不成立，patch plan 会生成 `scenario_semantic_contract`，下一步动作变为 `R8p_fix_pressure_resolution_scenario_semantics`，Agent60 fallback 已同步消费该状态。当前默认真实行包仍缺失，所以状态为 `scenario_semantic_preflight_blocked_at_source_preflight`，semantic violation 计数为 0 只表示 source 尚未加载，不表示场景语义已通过。
- R8u-17 已把 R8p accepted rows 到下游验证链的路径压实为 `field_rows_downstream_routing_preflight`：Agent61 现在生成 `outputs/pressure_resolution_replay_scenario_pack/pressure_resolution_replay_rows_downstream_routing_preflight.json`，明确 4 个 R8v 路由目标：Agent51 catalyst proxy holdout、Agent49 guardrail context、Agent52 replay clearance 和 R7 evidence chain。Agent60 的 R8v fallback 现在不再只看 `field_row_acceptance_status=field_replay_rows_accepted_for_all_scenarios`，还要求 `downstream_routing_preflight_passed_ready_for_r8v_field_replay_and_holdout_gates`、`can_route_to_r8v=True` 和 4 个 target 均 ready。当前默认真实行包仍缺失，所以状态为 `downstream_routing_preflight_blocked_at_source_preflight`，`routing_ready_target_count=0/4`；这表示 accepted rows 尚不存在，不能进入 R8v，更不能写 actuator 或 release gate。
- R8u-18 已把 R8p pressure-resolution 真实行包入口从只读 JSON 表映射扩展为双格式：`PRESSURE_RESOLUTION_REPLAY_ROWS_PATH` 可以指向 JSON 文件，也可以指向包含 `metadata.json` 与 6 张必需 CSV 的目录包。目录包加载会审计 metadata provenance context，并按 R8p schema 对 CSV 中的数字/布尔字段做保守类型转换；成功加载状态为 `field_rows_directory_loaded`，缺表状态为 `field_rows_directory_loaded_with_schema_gaps`。这只降低真实采集接入摩擦，不改变证据边界：目录包仍必须继续通过 schema/provenance、template marker、same-batch bundle、temporal window、scenario semantic、downstream routing、R7 evidence chain 和人工复核，不能直接写 actuator、release gate 或 field-supported claim。
- R8u-19 已把 R8p CSV/metadata 入口进一步落成可填写的采集目录模板：Agent61 现在生成 `outputs/pressure_resolution_replay_scenario_pack/pressure_resolution_replay_rows_csv_template/`，包含 `metadata.json`、`node_modality_sensor_timeseries.csv`、`pressure_headloss_event_log.csv`、`campaign_operation_log.csv`、`offline_lab_results.csv`、`fast_proxy_event_log.csv` 和 `agent52_replay_table.csv`。每张表保留 5 个 pressure-resolution 场景的 TODO 行，共 30 条模板行，字段顺序优先列出 R8p required fields；模板原样提交会得到 `schema_validation_failed_template_marker_contract` 和 `R8p_replace_template_markers_with_field_values`，因此不会被误认为 field evidence。
- R8u-20 已生成 `outputs/pressure_resolution_replay_scenario_pack/pressure_resolution_replay_rows_r7_alignment.json`，把 R7/Agent44 真实 field package 到 R8p pressure-resolution 行包的字段关系做成机器可读 crosswalk。当前结论：R8p 6 张目标表中有 5 张可与 R7 包共享，`agent52_replay_table` 必须来自 Agent49/52 replay export；直接字段、别名字段和 metadata-to-row provenance copy 可以复用，但还存在 10 个 R8p operator/supplement 字段和 11 个 Agent52 export 字段。该对齐矩阵只减少重复填表和字段错配，不能把 R7 template 或 field CSV 自动升级为 replay evidence。
- R8u-21 已把 R7-to-R8p crosswalk 推进为 staging preflight 和 draft transformer：Agent61 现在生成 `outputs/pressure_resolution_replay_scenario_pack/pressure_resolution_replay_rows_r7_staging_preflight.json` 与 `pressure_resolution_replay_rows_r7_staged_draft.json`。如果设置 `REAL_FIELD_REPLAY_PACKAGE_DIR`，staging 会读取 R7 metadata/CSV，按 direct field、alias field、metadata-to-row copy、operator supplement 和 Agent52 export 五类逐字段生成 R8p draft/gap report；默认无真实 R7 包时状态为 `r7_to_r8p_staging_preflight_no_r7_package_supplied`，`staged_row_count=0`，`agent52_export_required_field_gap_count=11`。该 draft 只是补包草稿，仍不能写 actuator、release gate 或 field-supported claim。
- R8u-22 已把 staging gap 进一步转成 `outputs/pressure_resolution_replay_scenario_pack/pressure_resolution_replay_rows_r7_completion_plan.json`。该 completion plan 把 R8p pressure-resolution 行包补齐动作拆成 4 类 evidence route：R7 source package、operator supplement、Agent52 replay export 和 R8p schema/preflight；当前默认无真实 R7 包时 `completion_plan_status=r7_to_r8p_completion_plan_waiting_for_r7_package`，`item_count=6`，`item_class_counts={r7_source_package:1, operator_supplement:4, agent52_replay_export:1}`，`field_gap_count_by_class={operator_supplement:10, agent52_replay_export:11}`。它是补包/导出工单，不能直接形成 field evidence。
- R8u-23 已把 R8u-22 completion plan 接入 Agent60 offline core fallback。Agent60 在 `R8p_fix_field_rows_source_preflight` 中现在不只消费 `field_rows_patch_plan` 与 `field_rows_operator_handoff`，还同步消费 `field_rows_r7_completion_plan`：当前 `r7_completion_plan_status=r7_to_r8p_completion_plan_waiting_for_r7_package`，`r7_completion_item_count=6`，`r7_completion_item_class_counts={r7_source_package:1, operator_supplement:4, agent52_replay_export:1}`，`r7_completion_field_gap_count_by_class={r7_source_package:0, operator_supplement:10, agent52_replay_export:11}`。这让治理层能把下一步补齐路线明确拆成“先给 R7 source package / metadata provenance、再生成 R7-to-R8p draft、再补 operator supplement、再导出 Agent49/52 replay、最后重跑 Agent61/R8p 与 R8v 路由门”。本轮只是治理消费与 manifest/report 写回，不生成真实现场结论，不写 actuator 或 release gate。
- R8u-24 已把 completion plan 推进为 route execution contracts：Agent61 现在生成 `outputs/pressure_resolution_replay_scenario_pack/pressure_resolution_replay_rows_r7_completion_route_contracts.json`，按证据生产者拆成四条路线：`r7_source_package` 由 R7/Agent44 field package importer 生产，`operator_supplement` 由现场 operator review/calibration workflow 生产，`agent52_replay_export` 由 Agent49/52 replay evaluation chain 生产，`r8p_validation_gates` 由 Agent61 执行 schema/provenance/template/bundle/temporal/semantic/routing 验收。每条 route 均包含 input_contract、output_contract、required_fields_by_table、validation_gates、validation_command、downstream_consumers 和 failure_boundary。当前 `completion_route_contracts_status=completion_route_contracts_ready_waiting_for_r7_package`，`open_route_count=4`，open routes 为 `r7_source_package`、`operator_supplement`、`agent52_replay_export`、`r8p_validation_gates`。Agent60 fallback 已消费这些字段，说明 route contracts 已回接治理主链；仍不能写 actuator、release gate 或 field-supported claim。
- R8u-25 已把 route execution contracts 推进为 route work packages：Agent61 现在生成 `outputs/pressure_resolution_replay_scenario_pack/pressure_resolution_replay_rows_r7_completion_route_work_packages.json`，把四条 evidence route 转成可交付工作包。`R8U25_R7_SOURCE_PACKAGE_WORK_PACKAGE` 要求 `metadata.json` 与五张 R7 shared CSV，`R8U25_OPERATOR_SUPPLEMENT_WORK_PACKAGE` 要求 operator supplement 与 calibration review 记录，`R8U25_AGENT52_REPLAY_EXPORT_WORK_PACKAGE` 要求 Agent52 replay manifest 与 replay table，`R8U25_R8P_VALIDATION_GATES_WORK_PACKAGE` 要求 assembled R8p rows 与 schema/gate 输出。每个 work package 均包含 expected_input_files、expected_output_files、submission_contract、acceptance_checks、validation_command、evidence_level_after_package 和 failure_boundary。当前 `route_work_packages_status=route_work_packages_ready_waiting_for_r7_package`，`open_work_package_count=4`；Agent60 fallback 已消费这些字段，说明工作包接口已回接治理主链；仍不能写 actuator、release gate 或 field-supported claim。
- R8u-26 已把 route work packages 推进为可填报模板与 submission preflight：Agent61 现在生成 `outputs/pressure_resolution_replay_scenario_pack/pressure_resolution_replay_rows_r7_completion_route_work_package_templates/` 与 `outputs/pressure_resolution_replay_scenario_pack/pressure_resolution_replay_rows_r7_completion_route_work_package_preflight.json`。模板目录按四个 work package 拆分，写入 `submission_manifest.json`、CSV header 和 JSON placeholder；preflight 读取可选 `R7_TO_R8P_WORK_PACKAGE_DIR`。当前未设置提交目录，因此 `route_work_package_preflight_status=route_work_package_preflight_waiting_for_submission_dir`，`submitted_work_package_count=0`，`passed_work_package_count=0`，`blocked_work_package_count=4`。模板原样提交会被 TODO/header-only/provenance gap 阻断；该机制只提供提交入口与预检，不能生成 field evidence、actuator 写回、release gate 或 field-supported claim。
- R8u-27 已把 route work package preflight 推进为可执行 patch plan：Agent61 现在生成 `outputs/pressure_resolution_replay_scenario_pack/pressure_resolution_replay_rows_r7_completion_route_work_package_patch_plan.json`。当前未设置 `R7_TO_R8P_WORK_PACKAGE_DIR` 时，`route_work_package_patch_plan_status=route_work_package_patch_plan_waiting_for_submission_dir`，`patch_item_count=1`，最高优先修补项为 `R8U27_SET_R7_TO_R8P_WORK_PACKAGE_DIR`；如果后续提交目录存在但仍有缺口，patch plan 会逐项拆出 missing work package dir、missing file、empty CSV rows、CSV header contract、invalid JSON、template marker replacement、metadata provenance 和 project dependency gate。Agent60 fallback 已消费 patch plan 状态、patch item 数与 highest patch，这让后续工作可以直接按阻塞项修补真实行包，而不是泛化地说“继续采集数据”。该 patch plan 不是 evidence，不能绕过 R7 import、R8p/R8v gates、field holdout、人工复核、actuator 或 release gate。
- R8u-28 已把 route work package patch plan 推进为 assembly gate：Agent61 现在生成 `outputs/pressure_resolution_replay_scenario_pack/pressure_resolution_replay_rows_r7_completion_route_work_package_assembly_gate.json`。该 gate 将四类 work package 到 R8p candidate rows 的路径拆成 6 步：验证 `R7_TO_R8P_WORK_PACKAGE_DIR`、stage R7 source package rows、merge operator supplement、merge Agent52 replay export、materialize R8p candidate rows package、重跑 R8p/R8v validation gates。当前未设置提交目录，所以 `route_work_package_assembly_gate_status=route_work_package_assembly_gate_blocked_waiting_for_submission_dir`，`assembly_step_count=6`，`ready_assembly_step_count=0`，`blocked_assembly_step_count=6`，每一步的 blocking patch 均为 `R8U27_SET_R7_TO_R8P_WORK_PACKAGE_DIR`。Agent60 fallback 已消费 assembly gate 状态和 step counts；该 gate 只定义 candidate rows 装配合同，不能把候选包升级为 field evidence，不能绕过 R8p/R8v/holdout/release gates。
- R8u-29 已把 Agent60 七层骨架和模块接口契约压成专利级技术特征 ledger：Agent60 现在生成 `outputs/agent_architecture_consolidation/patent_technical_feature_ledger.json`，覆盖 M1-M8 八条技术特征：node-modality 稀疏感知、软传感灰箱状态估计、灰箱机理边界、低频循环协同控制、KG 证据约束、field replay/release gate、工程执行约束和阶段门控治理。每条特征都必须具备技术问题、技术手段、系统结构、状态变量、控制动作、实施例、验证指标、技术效果、现有技术区别、claim skeleton role、证据边界和失败边界；当前 `technical_feature_coverage_rate=1.0`，`abstract_only_feature_ids=[]`，`field_claim_upgrade_allowed=False`，M9 展示层被排除。该 ledger 是技术交底成熟度 scaffold，不是法律意见，不产生 field evidence，不能写 actuator 或 release gate。
- R8u-30 已把 R8u-29 technical feature ledger 组合成 technical claim skeleton scaffold：Agent60 现在生成 `outputs/agent_architecture_consolidation/technical_claim_skeleton_scaffold.json`。该 scaffold 包含 7 条技术方案骨架：2 个独立方向（方法与系统）和 5 个从属/分案方向（催化剂活性代理观测与再生/更换、node-modality 稀疏布点与隐藏状态估计、现场 replay 证据门控与保护性写回、低频传感-循环窗口协同控制、灰箱机理约束下的多智能体安全仲裁）。当前 `technical_claim_skeleton_coverage_rate=1.0`，`missing_feature_coverage=[]`，`field_claim_upgrade_allowed=False`。该 scaffold 不是法律权利要求文本，不是授权判断；它只把模型核心链路组织成可实施、可验证、可对比的技术方案骨架。
- R8u-31 已把 R8u-30 technical claim skeleton scaffold 推进为 technical embodiment validation matrix：Agent60 现在生成 `outputs/agent_architecture_consolidation/technical_embodiment_validation_matrix.json`。该矩阵包含 6 个实施例：端到端低成本循环式灰箱闭环、压力源冲突解除/R7-to-R8p route work package 验收、催化剂活性代理观测与再生/更换、node-modality 稀疏布点与隐藏状态估计、低频传感-循环窗口协同控制、灰箱机理约束下的多智能体安全仲裁。当前 `technical_embodiment_validation_coverage_rate=1.0`，`missing_claim_coverage=[]`，`missing_feature_coverage=[]`，`field_claim_upgrade_allowed=False`，`can_generate_field_evidence=False`，`can_write_to_actuator=False`，`can_write_to_release_gate=False`。该矩阵只定义实施例、所需数据包、验证门、验收指标和失败边界，不产生现场结论。
- R8u-32 已把 R8u-31 technical embodiment validation matrix 推进为 technical effect measurement matrix：Agent60 现在生成 `outputs/agent_architecture_consolidation/technical_effect_measurement_matrix.json`。该矩阵把 6 个实施例中的技术效果压成 7 条可度量合同：稀疏感知可观测性提升、黑箱到灰箱状态估计、低频传感-循环窗口降低高频传感依赖、催化剂活性代理保护边界、field replay/release gate 防误放行、多智能体灰箱仲裁降低冲突动作、工程执行约束可行性。每条效果均写明 linked embodiment/claim/feature、effect statement、baseline comparator、measurement metrics、acceptance thresholds、required evidence tiers、validation gate、current evidence status 和 failure boundary。当前 `technical_effect_measurement_coverage_rate=1.0`，`effect_count=7`，`missing_embodiment_coverage=[]`，`field_claim_upgrade_allowed=False`，`can_generate_field_evidence=False`，`can_write_to_actuator=False`，`can_write_to_release_gate=False`。该矩阵只把技术效果转成验收指标，不产生 field-supported 结论。
- R8u-33 已把 R8u-32 technical effect measurement matrix 推进为 prior-art distinction / protectability risk matrix：Agent60 现在生成 `outputs/agent_architecture_consolidation/prior_art_distinction_matrix.json`。该矩阵把 7 条 claim scaffold、8 条 PTF 技术特征和 7 条技术效果映射到 7 个已有方法族：软传感/数据驱动监测、稀疏传感布点、多智能体/MARL/泵站协同、flowsheet/优化/TEA-LCA、Scientific KG/claim verification、AI 催化剂发现、offline replay/provenance gate。每条区别项均写明 known prior capability、distinguishing combination、why not generic AI/control、technical problem、measurable effects、novelty risk、combination risk、dependent fallback path、verification needed 和 failure boundary。当前 `prior_art_distinction_coverage_rate=1.0`，`distinction_count=7`，`missing_claim_coverage=[]`，`missing_feature_coverage=[]`，`missing_effect_coverage=[]`，`formal_search_required=True`，`field_claim_upgrade_allowed=False`，`novelty_or_inventiveness_opinion_allowed=False`。该矩阵只是正式 prior-art search 前的区别假设与风险清单，不是法律意见、不是新颖性/创造性结论、不是授权判断。
- R8u-34 已把 R8u-33 prior-art distinction / protectability risk matrix 推进为 formal search work packages：Agent60 现在生成 `outputs/agent_architecture_consolidation/formal_search_work_packages.json`。该矩阵把 7 条 PAD 区别假设分别转成可执行检索工作包，逐项写明 search objective、search databases、english/chinese search queries、classification hints、evidence to collect、negative evidence checks、claim fallback、field validation gate、decision rule 和 expected output artifacts。当前 `formal_search_work_package_coverage_rate=1.0`，`work_package_count=7`，`missing_distinction_coverage=[]`，`formal_search_required=True`，`formal_search_completed=False`，`legal_opinion_allowed=False`，`field_claim_upgrade_allowed=False`。该矩阵只生成检索任务和 claim fallback 路线，不是 prior-art search 结果、不是法律意见、不证明新颖性/创造性。
- R8u-35 已把 R8u-34 formal search work packages 推进为 formal search result intake schema：Agent60 现在生成 `outputs/agent_architecture_consolidation/formal_search_result_intake_schema.json`。该 schema 为 7 个 formal search work packages 分别定义 prior-art hit table 与 claim element comparison chart 的接收合同，包含 18 个 hit table 必填字段、12 个 comparison chart 必填字段、reviewer 字段、输入工件、验收检查、阻断条件、最小证据要求和 claim scope decision options。当前 `formal_search_result_intake_coverage_rate=1.0`，`intake_count=7`，`missing_work_package_coverage=[]`，`formal_search_result_supplied=False`，`accepted_hit_count=0`，`can_generate_prior_art_result=False`，`legal_opinion_allowed=False`，`field_claim_upgrade_allowed=False`。该 schema 只定义检索结果如何提交和审查；没有外部检索结果与人工复核时，不能生成 prior-art hit 结论、法律意见或 field-supported claim。
- R8u-36 已把 R8u-35 formal search result intake schema 推进为 formal search result validation gate：Agent60 现在生成 `outputs/agent_architecture_consolidation/formal_search_result_validation_gate.json`。该 gate 为 7 个 intake 分别定义运行时验收规则，检查外部/人工检索结果包是否可读、必填字段是否完整、source_database 是否属于对应工作包、matched_query 是否具备生成检索式或 reviewer-approved expansion 来源、claim element comparison 是否覆盖 mapped claim/feature/effect、reviewer 字段是否越界到法律意见或 field claim 升级。当前 `formal_search_result_validation_gate_coverage_rate=1.0`，`validation_gate_count=7`，`missing_intake_coverage=[]`，`formal_search_result_package_supplied=False`，`validated_hit_count=0`，`rejected_hit_count=0`，`can_generate_prior_art_result=False`，`legal_opinion_allowed=False`，`field_claim_upgrade_allowed=False`。该 gate 是 prior-art result package 进入模型前的结构、来源、比对和 reviewer 边界门；没有真实外部结果包时不能生成 prior-art comparison，任何情况下都不是法律意见，也不能升级 field-supported claim。
- R8u-37 已把 R8u-36 formal search result validation gate 推进为 formal search result package template 与 source preflight：Agent60 现在生成 `outputs/agent_architecture_consolidation/formal_search_result_package_template.json` 和 `outputs/agent_architecture_consolidation/formal_search_result_package_source_preflight.json`。模板为 7 个 validation gate 分别定义正式检索结果包提交合同，包含 package manifest 必填字段、prior_art_hit_table 字段、claim_element_comparison_chart 字段、fallback_claim_scope_recommendation 字段、允许来源库、允许查询来源、行级拒收规则和验证命令。source preflight 读取可选 `FORMAL_SEARCH_RESULT_PACKAGE_PATH`，先检查路径、JSON 根对象、`package_metadata`、`work_package_results`、未知 work package、缺失 work package、必需表是否 list 以及空表。当前 `formal_search_result_package_template_coverage_rate=1.0`，`package_template_count=7`，`missing_validation_gate_coverage=[]`，`formal_search_result_package_source_status=formal_search_result_package_preflight_waiting_for_submission_path`，`preflight_blockers=['FORMAL_SEARCH_RESULT_PACKAGE_PATH:not_set']`，`can_route_to_validation_gate=False`，`can_generate_prior_art_result=False`，`legal_opinion_allowed=False`，`field_claim_upgrade_allowed=False`。该机制只提供结果包提交入口和 source/root shape 预检；没有真实外部/人工检索结果包时不能进入 validation gate 或生成 prior-art comparison。
- R8u-38 已把 R8u-37 formal search result package template/source preflight 推进为可填报 submission skeleton 与 template-marker preflight：Agent60 现在生成 `outputs/agent_architecture_consolidation/formal_search_result_package_submission_template.json`。该 skeleton 根结构已经符合 R8u-37 source preflight：包含 `package_metadata` 和 7 个 `work_package_results`，每个 work package 都预置 `package_manifest`、`prior_art_hit_table`、`claim_element_comparison_chart` 和 `fallback_claim_scope_recommendation` 占位行；但所有占位行都显式标记 `template_only=True`、`evidence_status=template_not_prior_art_evidence`、`legal_status=template_not_legal_opinion` 和 `TODO_*` 字段。source preflight 现在会递归扫描 `TODO_*`、`template_not_prior_art_evidence`、`sample_not_prior_art_evidence`、`template_not_legal_opinion` 和 `template_only=true`。验证显示将 skeleton 原样设置为 `FORMAL_SEARCH_RESULT_PACKAGE_PATH` 时会得到 `formal_search_result_package_failed_template_marker_preflight`，检测到 365 个 template marker，`can_route_to_validation_gate=False`，`can_generate_prior_art_result=False`。当前默认无提交包状态已恢复为 `formal_search_result_package_preflight_waiting_for_submission_path`，不会进入 validation gate。
- R8u-39 已把 R8u-38 formal search result package submission skeleton/source preflight 推进为 row-level schema/provenance preflight：Agent60 现在生成 `outputs/agent_architecture_consolidation/formal_search_result_package_row_preflight.json`。该 preflight 只有在 source/root/template-marker 预检通过后才检查行级内容；默认无提交包时停在 `formal_search_result_package_row_preflight_blocked_at_source_preflight`。当提交包可读且结构干净时，row preflight 会逐项检查 root `package_metadata`、每个 work package 的 `package_manifest`、`prior_art_hit_table`、`claim_element_comparison_chart` 和 `fallback_claim_scope_recommendation`：包括必填字段、`linked_work_package_id` 回连、`source_database` 是否属于该工作包 allowed databases、`matched_query` 是否属于 generated/allowed query sources、comparison 的 `linked_hit_id` 是否存在、comparison 是否覆盖 mapped claim/feature/effect，以及 reviewer/manifest/fallback 字段是否含法律意见或 field-supported claim 越界文本。当前默认 `checked_work_package_count=0`，`row_gap_count=0`，`comparison_coverage_gap_count=0`，`forbidden_review_boundary_count=0`，`can_route_to_validation_gate=False`；测试中的完整临时提交包可得到 `formal_search_result_package_row_preflight_ready_for_validation_gate`，但仍 `can_generate_prior_art_result=False`、`legal_opinion_allowed=False`、`field_claim_upgrade_allowed=False`。
- R8u-40 已把 R8u-39 row-level schema/provenance preflight 推进为 formal search result validation execution：Agent60 现在生成 `outputs/agent_architecture_consolidation/formal_search_result_validation_execution.json`。该 execution 只有在 row preflight 通过后才读取提交包并执行结构验收，输出 `work_package_execution_count`、`execution_row_count`、`validated_hit_count`、`rejected_hit_count`、`comparison_row_count`、`fallback_row_count`、hit-comparison 回连和 mapped claim/feature/effect 覆盖情况。当前默认无提交包时状态为 `formal_search_result_validation_execution_blocked_at_row_preflight`，`validated_hit_count=0`，`rejected_hit_count=0`，`can_enter_human_nonlegal_comparison_review=False`，`can_generate_prior_art_result=False`；测试中的完整临时提交包可得到 `formal_search_result_validation_execution_ready_for_human_nonlegal_comparison_review`，但该 ready 只表示结构验收可进入人工非法律比较审查，不是 prior-art 结论、不是法律意见、不是授权判断，也不能升级 field-supported claim。
- R8u-41 已把 R8u-40 validation execution 推进为 formal search nonlegal comparison review packet：Agent60 现在生成 `outputs/agent_architecture_consolidation/formal_search_nonlegal_comparison_review_packet.json`。该 packet 只有在 validation execution ready 后才生成审查任务行，每行回连 validation gate、work package、hit、source database、matched query 和 covered project element，并要求 reviewer 填写 `nonlegal_overlap_assessment`、`distinguishing_technical_detail`、`fallback_scope_recommendation`、`preserved_field_validation_gate`、`evidence_boundary_acknowledgement` 和 trace id。当前默认无提交包时状态为 `formal_search_nonlegal_review_packet_blocked_at_validation_execution`，`review_packet_row_count=0`，`human_review_completed=False`，`can_enter_human_nonlegal_comparison_review=False`，`can_generate_prior_art_result=False`；测试中的完整临时提交包可得到 `formal_search_nonlegal_review_packet_ready_waiting_for_human_review` 和 7 行审查任务，但仍不产生 prior-art 结论、法律意见、授权判断或 field-supported claim。
- R8u-42 已把 R8u-41 review packet 推进为 formal search nonlegal review response template/source preflight：Agent60 现在生成 `outputs/agent_architecture_consolidation/formal_search_nonlegal_review_response_template.json` 和 `outputs/agent_architecture_consolidation/formal_search_nonlegal_review_response_source_preflight.json`。该层要求 `FORMAL_SEARCH_NONLEGAL_REVIEW_RESPONSE_PATH` 指向人工回填 JSON 包，根对象包含 `review_metadata` 和 `review_rows`；行级字段必须覆盖 `review_packet_row_id`、work package、hit、reviewer、review_time、非法律 overlap assessment、distinguishing technical detail、fallback scope recommendation、preserved field validation gate、evidence boundary acknowledgement、trace id 和 `legal_status`。当前默认状态为 `formal_search_nonlegal_review_response_template_blocked_at_review_packet` 与 `formal_search_nonlegal_review_response_preflight_blocked_at_template`，accepted/rejected row 均为 0；测试中的完整临时回填包可得到 `formal_search_nonlegal_review_response_ready_for_claim_scope_patch_draft`、accepted=7、rejected=0、`human_review_completed=True`，但仍 `can_generate_prior_art_result=False`、`legal_opinion_allowed=False`、`field_claim_upgrade_allowed=False`。
- R8u-43 已把 R8u-42 的人工非法律 review response preflight 推进为 formal search claim scope patch draft scaffold：Agent60 现在生成 `outputs/agent_architecture_consolidation/formal_search_claim_scope_patch_draft.json`。该层只在 `formal_search_nonlegal_review_response_ready_for_claim_scope_patch_draft` 后读取已验收的人工 review rows，并生成逐 hit 的技术范围修补草案行：包含 `nonlegal_overlap_assessment`、`distinguishing_technical_detail`、`fallback_scope_recommendation`、`technical_patch_candidate`、`preserved_field_validation_gate`、trace id 和 `required_next_review=formal_patent_counsel_review_required`。当前默认状态为 `formal_search_claim_scope_patch_draft_blocked_at_nonlegal_review_response`、`draft_patch_count=0`、`can_route_to_formal_counsel_review=False`；测试中的完整临时链路可得到 7 条 draft row 并路由到正式专利代理人审查，但仍 `can_emit_claim_text=False`、`can_generate_prior_art_result=False`、`legal_opinion_allowed=False`、`field_claim_upgrade_allowed=False`。
- R8u-44 已把 R8u-43 的 claim scope patch draft 推进为 formal counsel review response template/source preflight：Agent60 现在生成 `outputs/agent_architecture_consolidation/formal_counsel_review_response_template.json` 和 `outputs/agent_architecture_consolidation/formal_counsel_review_response_source_preflight.json`。该层只定义外部正式审查回填包如何进入模型，要求 `FORMAL_COUNSEL_REVIEW_RESPONSE_PATH` 指向包含 `review_metadata` 和 `review_rows` 的 JSON 包；行级字段必须覆盖 `claim_scope_patch_id`、work package、hit、formal reviewer、review time、scope disposition、technical revision summary、required disclosure revision、preserved field validation gate、follow-up evidence/search、boundary acknowledgement 和 trace id。当前默认状态为 `formal_counsel_review_response_template_blocked_at_claim_scope_patch_draft` 与 `formal_counsel_review_response_preflight_blocked_at_template`，accepted/rejected row 均为 0；测试中的完整临时链路可得到 `formal_counsel_review_response_ready_for_disclosure_revision_queue`、accepted=7、rejected=0、`external_formal_review_completed=True`，但仍 `can_emit_claim_text=False`、`can_generate_prior_art_result=False`、`legal_opinion_allowed=False`、`field_claim_upgrade_allowed=False`。
- R8u-45 已把 R8u-44 的 formal counsel response preflight 推进为 formal disclosure revision queue：Agent60 现在生成 `outputs/agent_architecture_consolidation/formal_disclosure_revision_queue.json`。该 queue 只在外部正式审查回填包通过预检后读取 `accepted_formal_review_rows`，并生成逐项技术交底修订任务：包含 `claim_scope_patch_id`、work package、hit、scope disposition、revision action、approved technical revision summary、required disclosure revision、preserved field validation gate、follow-up search/evidence 和 trace id。当前默认状态为 `formal_disclosure_revision_queue_blocked_at_formal_counsel_review_response`、`revision_item_count=0`、`can_route_to_disclosure_editor=False`；测试中的完整临时链路可得到 `formal_disclosure_revision_queue_ready_for_human_disclosure_editor` 和 7 条修订任务，但仍 `can_apply_disclosure_revision_automatically=False`、`can_emit_claim_text=False`、`legal_opinion_allowed=False`、`field_claim_upgrade_allowed=False`。
- R8u-46 已把 R8u-45 的 disclosure revision queue 推进为 formal disclosure revision impact plan：Agent60 现在生成 `outputs/agent_architecture_consolidation/formal_disclosure_revision_impact_plan.json`。该 plan 只在 `formal_disclosure_revision_queue_ready_for_human_disclosure_editor` 后读取 `disclosure_revision_items`，并把每条修订任务映射到需要人工更新的核心工件：技术特征 ledger、technical claim skeleton scaffold、实施例/验证矩阵、技术效果矩阵、prior-art distinction matrix，必要时追加 formal search work package matrix。当前默认状态为 `formal_disclosure_revision_impact_plan_blocked_at_revision_queue`、`revision_impact_item_count=0`、`can_route_to_human_artifact_revision=False`；测试中的完整临时链路可得到 7 条 impact item 并进入人工工件修订阶段，但仍 `can_apply_artifact_patch_automatically=False`、`can_emit_claim_text=False`、`can_generate_prior_art_result=False`、`legal_opinion_allowed=False`、`field_claim_upgrade_allowed=False`。
- R8u-47 已把 Agent61/R8p 的 pressure-resolution 真实行提交就绪审查回接到 Agent60 全局 fallback：Agent61 输出 `field_rows_submission_readiness_review` 和 `pressure_resolution_replay_rows_submission_readiness_review.json`，按 source package、schema/provenance、same-batch bundle、temporal window、scenario semantic、downstream routing、R7-to-R8p work package assembly 的顺序汇总一个 operator-facing gate；Agent60 现在透传 `submission_readiness_review_status`、`submission_readiness_next_operator_action`、`submission_readiness_can_route_to_r8v`、direct R8p 最高补包项和 R7-to-R8p 最高补包项。当前状态为 `submission_readiness_review_blocked_at_source_package`、下一步 `R8p_fix_field_rows_source_preflight`、`direct_r8p_highest_priority_patch_id=R8P_SOURCE_MISSING_FIELD_ROWS_FILE`、`r7_to_r8p_highest_priority_patch_id=R8U27_SET_R7_TO_R8P_WORK_PACKAGE_DIR`、`can_route_to_r8v=False`。该层只把真实行包进入 R8v replay/holdout 前的门控序列聚合为一个可执行入口，不产生 field evidence、不写 actuator、不写 release gate、不升级现场 claim。
- R8u-48 已把 R8u-47 的 submission readiness gate 继续推进为 source package submission route guide：Agent61 新增 `field_rows_source_package_submission_route_guide` 和 `pressure_resolution_replay_rows_source_package_submission_route_guide.json`，把 direct R8p JSON table mapping、direct R8p CSV directory 和 R7-to-R8p route work package 三条入口并列；每条路线都写明适用场景、提交目标、环境变量、必需输入、必需表/字段、验证命令、最高补包项和 failure boundary。Agent60 fallback 已消费 `source_package_route_guide_status`、`source_package_recommended_route_id`、`source_package_next_operator_action` 和 `source_package_route_option_count`。当前状态为 `source_package_submission_route_guide_ready_for_source_package_submission`，推荐路线 `direct_r8p_json_or_csv_source_package`，下一步 `R8p_submit_direct_json_or_csv_source_package`，route option count=3，`can_route_to_r8v=False`。该 guide 只降低真实 source package 提交摩擦，不验证新证据、不生成 Agent52 replay 行、不写 actuator、不写 release gate、不升级现场 claim。
- R8u-49 已把 R8u-48 的 route guide 推进为 source package route preflight：Agent61 新增 `field_rows_source_package_route_preflight` 和 `pressure_resolution_replay_rows_source_package_route_preflight.json`，对 direct JSON、direct CSV directory 和 R7-to-R8p work package 三条路线分别输出 `route_preflight_status`、路径/格式检查、validation command、blockers 与 next operator action；Agent60 fallback 已消费 route preflight 状态、推荐入口预检状态和 ready/waiting/blocked route count。当前无真实 source package 时，`source_package_route_preflight_status=source_package_route_preflight_waiting_for_source_package_submission`，`recommended_route_preflight_status=recommended_route_preflight_waiting_for_direct_source_package`，ready/waiting/blocked=0/3/0，`can_route_to_r8v=False`。该 preflight 只是提交路线可行动性检查，不产生 field evidence，不替代 R8p acceptance/R8v replay/holdout，不写 actuator 或 release gate。
- R8u-50 已把 R8u-17 的 downstream routing preflight 推进为 R8v downstream route handoff：Agent61 新增 `field_rows_downstream_route_handoff` 和 `pressure_resolution_replay_rows_downstream_route_handoff.json`，把 Agent51 catalyst proxy holdout、Agent49 guardrail context、Agent52 replay clearance 和 R7 evidence chain 四个目标逐一绑定到 required inputs、expected gate metrics、执行顺序、blocked writes 和 replay/holdout 边界；Agent60 现在在 R8v 推荐动作中同时要求 R8p 行级验收、downstream routing preflight 和 downstream route handoff 均 ready。当前无真实 source package 时，handoff 状态为 `downstream_route_handoff_blocked_by_upstream_r8p_preflight`，ready/blocked=0/4，下一步仍为 `R8p_fix_field_rows_source_preflight`。该 handoff 是下游验证交接合同，不运行下游 gate，不产生 field evidence，不写 actuator 或 release gate。
- R8u-51 已把 R8u-50 downstream route handoff 推进为 R8v downstream target gate preflight：Agent61 新增 `field_rows_downstream_target_gate_preflight` 和 `pressure_resolution_replay_rows_downstream_target_gate_preflight.json`，为 Agent51 catalyst proxy holdout、Agent49 guardrail context、Agent52 replay clearance 和 R7 evidence chain 四个目标逐一写明 validation command、expected metrics artifact、required input count、target gate output contract、blocked writes 和 blocking reasons；Agent60 现在在 R8v 推荐动作中同时要求 R8p 行级验收、downstream routing preflight、downstream route handoff 和 downstream target gate preflight 均 ready。当前无真实 source package 时，target gate preflight 状态为 `downstream_target_gate_preflight_blocked_by_downstream_route_handoff`，ready/blocked=0/4，下一步仍为 `R8p_fix_field_rows_source_preflight`。该 preflight 只定义下游 gate 执行合同，不运行 Agent51/49/52/R7，不产生 field evidence，不写 actuator 或 release gate。
- R8u-52 已把 R8u-51 downstream target gate preflight 推进为 downstream target gate result intake schema/preflight：Agent61 新增 `field_rows_downstream_target_gate_result_intake_schema`、`field_rows_downstream_target_gate_result_preflight`、`pressure_resolution_replay_rows_downstream_target_gate_result_intake_schema.json` 和 `pressure_resolution_replay_rows_downstream_target_gate_result_preflight.json`。该层要求 Agent51/49/52/R7 返回结果包逐目标覆盖 `target_id`、`target_gate_status`、`batch_ids`、`source_metrics_artifact`、`reported_metrics`、`operator_review_boundary_preserved`、`can_write_to_actuator`、`can_write_to_release_gate` 和 `field_claim_upgrade_allowed`；Agent60 fallback 已透传 result preflight status、submitted/accepted/rejected count 和 next operator action。当前无真实 source package 时，result preflight 被 target gate preflight 阻断，状态为 `downstream_target_gate_result_preflight_blocked_by_target_gate_preflight`，submitted/accepted/rejected=0/0/0，missing target ids 为四个 R8v 目标，下一步仍是 `R8p_fix_field_rows_source_preflight`。该 preflight 只验证下游 gate 结果包的结构、目标覆盖、source artifact、指标字段和保护性写入边界；不做结果仲裁，不产生 field evidence，不写 actuator 或 release gate，不升级 field-supported claim。
- R8u-53 已把 R8u-52 downstream target gate result intake 推进为 downstream target gate result arbitration：Agent61 新增 `field_rows_downstream_target_gate_result_arbitration` 和 `pressure_resolution_replay_rows_downstream_target_gate_result_arbitration.json`。该层只在 result preflight 通过后读取四个 target result 的 `target_gate_status`，统计 `passed/failed/blocked/waiting_for_operator_review/invalid`，并把 unanimous pass 路由到 operator review；任何 failed、blocked、waiting、invalid、missing 或 result preflight 阻断都会继续阻断控制和放行。当前无真实 source package 时，arbitration 状态为 `downstream_target_gate_result_arbitration_blocked_by_result_preflight`，accepted target result count=0，`can_route_to_operator_review=False`，`can_emit_protective_control_candidate=False`，下一步仍为 `R8p_fix_field_rows_source_preflight`。该仲裁门不是 field evidence、不是 release clearance，也不是保护性控制候选。
- R8u-54 已把 R8u-53 downstream target gate result arbitration 推进为 downstream target gate operator-review response gate：Agent61 新增 `field_rows_downstream_target_gate_operator_review_template`、`field_rows_downstream_target_gate_operator_review_preflight`、`pressure_resolution_replay_rows_downstream_target_gate_operator_review_template.json` 和 `pressure_resolution_replay_rows_downstream_target_gate_operator_review_preflight.json`。该层只在 arbitration ready for operator review 后读取 `R8V_TARGET_GATE_OPERATOR_REVIEW_PATH`，逐目标检查 `operator_review_decision`、`reviewer_id`、`review_time`、`review_notes`、`boundary_acknowledgement` 以及 `can_write_to_actuator=False`、`can_write_to_release_gate=False`、`field_claim_upgrade_allowed=False`；任一目标 reject/hold 或任何保护性写入请求都会阻断。当前无真实 source package 时，operator review 被 arbitration 阻断，状态为 `downstream_target_gate_operator_review_preflight_blocked_by_arbitration`，approved/rejected/hold=0/0/0，`can_route_to_post_review_gate=False`，下一步仍为 `R8p_fix_field_rows_source_preflight`。该层把人工复核从口头要求压成机器可读响应门，但仍不是 field evidence、不是 release clearance，也不是保护性控制候选。
- R8u-55 已把 R8u-54 downstream target gate operator-review response gate 推进为 post-review protective candidate gate：Agent61 新增 `field_rows_downstream_target_gate_post_review_gate` 和 `pressure_resolution_replay_rows_downstream_target_gate_post_review_gate.json`。该层只在 operator-review preflight 全部 approved 后，才允许把四个 target 的结果送入“保护性控制候选评估”；未通过人工复核、人工复核缺失、任一目标 reject/hold 或上游 source/result gate 阻断时，都保持 `can_route_to_protective_candidate_evaluation=False` 和 `can_emit_protective_control_candidate=False`。当前无真实 source package 时，post-review gate 状态为 `downstream_target_gate_post_review_gate_blocked_by_operator_review_preflight`，下一步仍为 `R8p_fix_field_rows_source_preflight`。该层不是 actuator command、不是 release clearance，也不是 field-supported claim。
- R8u-56 已把 R8u-55 post-review gate 推进为 protective-control candidate evaluation gate：Agent61 新增 `field_rows_downstream_target_gate_protective_candidate_evaluation` 和 `pressure_resolution_replay_rows_downstream_target_gate_protective_candidate_evaluation.json`。该层只在 post-review gate 通过后，把四个 target contribution 转成保护性候选动作包，候选动作包括暂存、延长停留、回流/回用审查、加药调整候选、催化剂再生/更换审查、单元切换候选和继续阻断 release gate；候选评估通过也仍需 policy gate、actuator safety interlock、operator final execution review、actuator feedback replay gate 和单独 release validation。当前无真实 source package 时，candidate evaluation 状态为 `protective_candidate_evaluation_blocked_by_post_review_gate`，`can_emit_protective_control_candidate=False`，`can_route_to_final_execution_review=False`。该层不是 actuator command、不是 release clearance，也不是 field-supported claim。
- Agent60 已接入 R8p 行级验收、R8v handoff/target gate preflight、target gate result intake、result arbitration、operator-review response gate、post-review gate 和 protective-control candidate evaluation gate：当且仅当 `field_scenario_coverage=1.000`、`field_row_acceptance_status=field_replay_rows_accepted_for_all_scenarios`、downstream routing 通过、`downstream_route_handoff_status=downstream_route_handoff_ready_for_r8v_target_gates` 且 `downstream_target_gate_preflight_status=downstream_target_gate_preflight_ready_for_r8v_execution` 时，离线 fallback 才会推进到 `R8v_route_pressure_resolution_rows_to_field_replay_and_holdout_gates`，把真实行送入 Agent51 catalyst proxy holdout、Agent49 控制保护上下文、Agent52 replay clearance 和 R7 evidence chain；target gate result intake/arbitration/operator review/post-review/candidate evaluation 是这些 gate 跑完后的结果回传、仲裁、人工响应、候选动作评估和最终执行复核入口，不会反向阻塞 target gate 执行，但会阻止任意结果包、非全通过目标状态、未经人工响应、未经 post-review 或未经 candidate evaluation 的结果进入保护控制或放行边界。当前无真实行时仍保持 `R8p_fix_field_rows_source_preflight`。
- 最新验证：全局 goal 十轮迭代版 Agent50 重新生成完成，Agent60 七层骨架映射、模块接口契约矩阵、专利级技术特征 ledger、technical claim skeleton scaffold、technical embodiment validation matrix、technical effect measurement matrix、prior-art distinction/protectability risk matrix、formal search work packages、formal search result intake schema、formal search result validation gate、formal search result package template、formal search result package submission skeleton、formal search result package source/template-marker preflight、formal search result package row-level preflight、formal search result validation execution、formal search nonlegal comparison review packet、formal search nonlegal review response template/source preflight、formal search claim scope patch draft、formal counsel review response template/source preflight、formal disclosure revision queue、formal disclosure revision impact plan、formal search review readiness 和 formal search execution route plan 已刷新并回接 Agent50，Agent61/R8p 行级验收门、source preflight、JSON/CSV-directory 双格式入口、CSV 采集目录模板、R7-to-R8p 字段对齐矩阵、R7-to-R8p staging preflight/draft transformer、R7-to-R8p completion plan、R7 completion plan 的 Agent60 fallback consumption、R7-to-R8p completion route contracts、R7-to-R8p route work packages、R7-to-R8p route work package templates/preflight、R7-to-R8p route work package patch plan、R7-to-R8p route work package assembly gate、submission readiness review、source package submission route guide、source package route preflight、R8v downstream route handoff、R8v downstream target gate preflight、R8v downstream target gate result intake schema/preflight/arbitration/operator-review response gate/post-review gate/protective-control candidate evaluation gate、缺表/空表诊断、独立真实行模板、field rows patch plan、operator handoff、机器可读 rows schema、runtime schema validation summary、field rows collection checklist、全表 field provenance gate、provenance-aware schema preflight、template-marker-aware schema preflight、same-batch bundle preflight、temporal-window preflight、scenario-semantic preflight、downstream-routing preflight、Agent60 fallback consumption、R8u-82 external activation router、R8u-83 Agent50 router consumption、R8u-84 field package preflight route guard、R8u-86 R7 submission repair work order 和 R8u-87 repair response preflight 已接入；当前完整回归 481 passed。
- Agent56 已把知识库从松散条目升级为 typed KG reasoning：输出 evidence paths、action constraint patch 和 field_validation_queue。
- Agent57 已把 Agent53 灰箱 prior、Agent54 布点/缺测合同、Agent55 工程约束、Agent56 KG 约束和 Agent49 联动动作回接主链，main_chain_prior_consumption_rate 为 1.000。
- Agent58 已把 Agent56 的 field_validation_queue 对齐到 Agent30/42/44/45 的表、字段、metadata 和 G6/P6 gate；table/gate coverage 均为 1.000。
- Agent59 已把 Agent58 mapping_table 升级为 claim-specific 必采字段矩阵和 source_basis 补全任务；schema pass 为 1.000，R6 后 source_basis_completion_rate 为 1.000，但 minimal_field_package_field_pass_rate 仍为 0.000。
- Agent60 已作为复盘治理工具审计当前模型本体，不计入被复盘的模型能力链；新增 Agent61/R8o 后，60/60 agent 已映射到 9 个模块，核心锚点覆盖率 1.000，模块接口契约覆盖率 1.000。
- Agent60 识别 5 个合并/冻结簇：软传感验证簇、field evidence/claim gate 簇、项目运维压缩簇、展示层冻结簇、KG/文献/reasoning 簇。
- Agent60 已把 `R1_unify_field_evidence_and_source_basis_gate` 作为已完成的接口合并基线：field evidence、claim package 与 source_basis gate 已统一，避免 Agent34/43/45/58/59 重复阻断；边界是不能把文献 source_basis 当成 field-supported evidence，不能写 release gate。
- R1 已落成统一 Field Evidence Gate facade，不新增 agent 编号；它消费 Agent43/44/45/46/58/59 的指标，生成 3 条统一证据记录，gate_source_consolidation_coverage 为 1.000。
- R1b 已在统一 gate 内补齐 `low_cost_proxy_sensing` 和 `soft_sensor_release_gate` 的 source_basis detail library：citation_detail_completion_rate=1.000，source_basis_parameter_boundary_coverage=1.000，effective_literature_traceability=1.000。
- 统一 Field Evidence Gate 当前状态为 `unified_gate_ready_blocking_field_claim_upgrade`，仍阻断 field claim upgrade：source_basis_completion_rate 为 1.000，citation_detail_completion_rate=1.000，source_basis_parameter_boundary_coverage=1.000，field_supported_edge_ratio=0.000，field_import_pass=False，field_replay_evidence_chain_pass=False，soft_sensor_field_holdout_gate_pass=False。
- R2 已生成 Agent48/51/54 统一观测契约：推荐 `budget_rebalanced_proxy_contract`，在不直接采用超预算 full patch 的情况下，把 weak_state_coverage 从 0.300 提升到 0.580，估算成本 5.272，低于 5.8 预算。
- Agent48 已新增稀疏布点矩阵诊断层：除 coverage 外，输出 selected matrix rank、axis_span_rank_ratio、condition_number_proxy、reconstruction_stability_score、weak_axis_gaps 和 single-point dependency；当前默认方案 rank=6、axis_span_rank_ratio=0.667、condition_number_proxy=61.726、reconstruction_stability_score=0.401，暴露 catalyst_activity_observability 仍是不可由当前候选池补足的弱轴。
- Agent48 已把可比较布点从四类策略扩展为六类 prior-art baseline：`greedy_marginal`、`deterministic_random_baseline`、`cost_only_baseline`、`reconstruction_qr_proxy`、`classification_sspoc_proxy`、`topology_robust_cost_proxy`。新增 `baseline_comparison_contract`，当前状态为 `sparse_baseline_comparison_ready_needs_field_topology_and_labels`，selected strategy 仍为 `greedy_marginal`，best_vs_random_delta=0.062，best_vs_cost_only_delta=0.258。该层只支持非法律 prior-art 区分和论文/专利对照设计，不能证明 patentability，也不能替代真实 topology、node-specific time series 或 offline hidden-state labels。
- Agent48 现已新增 hidden-state requirement ledger：把 `pollutant_residual`、`reaction_completion`、`catalyst_activity`、`matrix_interference`、`hydraulic_delay`、`release_or_byproduct_risk` 六类隐藏状态逐一映射到 primary axes、required zones、required modalities、field evidence 和 candidate patch。当前 `ready_hidden_state_count=4/6`，`minimum_cost_patch_status=minimum_cost_patch_requires_new_modality_or_field_label`，硬缺口为 `catalyst_activity`，明确需要 pressure/headloss proxy、catalyst_activity field label、regeneration_event 和 HRT/床体几何证据，而不能靠现有候选池简单加点伪装解决。
- R2 observation contract 已消费 Agent48 hidden-state ledger：`agent48_hidden_state_minimum_patch_status=minimum_cost_patch_requires_new_modality_or_field_label`，并新增 `R2_FV4_agent48_hidden_state_requirement_patch`，把 hard-unresolved `catalyst_activity` 转成 `node_modality_sensor_timeseries`、`offline_lab_results`、`campaign_operation_log`、`site_topology_or_bed_geometry` 的现场补证据需求。
- Agent51 已消费 Agent48 的 `catalyst_activity_observability` 弱轴诊断，生成 `weak_axis_repair_plan`：repair_status=`agent48_catalyst_axis_requires_proxy_patch_and_field_label`，repair_score=0.983，优先补 `N3_catalyst_bed_outlet:UV254_abs`、`N3_catalyst_bed_outlet:ORP_mV`、`N3_catalyst_bed:pressure_drop_kPa`，并要求 field_proxy_holdout 覆盖 `node_modality_sensor_timeseries`、campaign_operation_log、offline_lab_results 和床体积/HRT/流量字段。
- Agent51 现已新增 field holdout 数据摘要入口：`build_catalyst_proxy_field_holdout_summary()` 可从 R7j 包中提取节点级 N3 UV254/ORP/压差、QA 通过的 `catalyst_activity` 标签、再生事件和床体/HRT，生成 matched_batch_count、scoreable_batch_count、proxy_label_correlation、holdout_mae 和 evidence boundary。当前模板演练下 `field_proxy_holdout_summary_status=field_proxy_holdout_coverage_gaps`、scoreable_batch_count=0，这是正确阻断；真实包达到可评分批次后才会让 Agent51 从 synthetic design prior 进入 field_proxy_holdout validation。
- R2 现已消费 Agent51 的 weak-axis repair plan：推荐 `budget_rebalanced_proxy_contract` 不再只是普通补点，而是将床出口 UV254/ORP 两个最高优先级代理补点纳入合同，同时移除最低边际的 `N5_polishing_inlet:turbidity_NTU`，使 weak_state_coverage 达到 0.580 且预算仍通过。
- R2 仍是 synthetic/design-prior：field_topology_ready=False、field_proxy_labels_ready=False、field_missingness_ready=False；不能放松 Agent49 催化剂不确定性保护，不能写执行器或 release gate。
- Agent49 已消费 R2 观测契约和 Agent51/R2 的催化剂弱轴修复先验，控制侧 weak_state_coverage 从 0.300 更新到 0.580，weak_state_ready=True；同时新增 `catalyst_axis_repair_prior_not_field_validated` 边界，明确 field_proxy_labels 前仍不能解除催化剂保护规则、不能写执行器。Agent49 现进一步读取 Agent51 `field_proxy_holdout_summary`，当前 `catalyst_proxy_summary_status=field_proxy_holdout_coverage_gaps`、scoreable_batch_count=0、`catalyst_guardrail_mode=agent51_holdout_coverage_gaps_keep_catalyst_guardrail`，因此 J2 催化剂保护/再生仍受 R3G1 惩罚并转向暂存/人工复核。
- R3 已完成 Agent49/52 控制 replay 反事实压力测试：baseline accuracy=0.667，observation-aware accuracy=0.833，guardrail candidate accuracy=1.000，p95 regret delta=0.177，false positive cost delta=0.180；这些仍是 synthetic stress，不是 field-supported 控制结论。
- R3b 已把 R3G1/R3G2 接入 Agent49 reward prior：J4 safe standby 和 J3 polishing/release gate 获得 guardrail bonus，J2 autonomous catalyst protection 和 J0 recycle escalation 在缺 field proxy/hydraulic evidence 时被惩罚；仍不写执行器。
- R3c 已让 Agent52 消费 Agent49 的 guardrail-aware policy：baseline joint_action_accuracy=0.667、p95 regret=0.177、false positive cost=0.180；guardrail-aware joint_action_accuracy=1.000、p95 regret=0.000、false positive cost=0.000；field_replay_coverage 仍为 0.000。R3d 已让 Agent52 replay row 和 readiness 同步消费 Agent51 catalyst proxy summary：当前 `catalyst_proxy_field_validation_pass=False`、scoreable_batch_count=0，因此即使 field coordination replay 指标未来达标，只要 Agent51 holdout 未通过，仍不能提升 Agent49 催化剂相关策略为执行器候选。
- R4 已把 R3c resolved cases 反写为灰箱机制和现场字段：`catalyst_uncertain_low_proxy` 对应 catalyst proxy/pressure/drop/lifecycle field requirements，`hydraulic_delay_violation` 对应 tank storage、actuator latency、pump-valve、flow/hold/recycle requirements；mechanism coverage=1.000，field requirement coverage=1.000。
- R4b 已让 Agent53 消费 R4 grey-box failure boundary patches：agent53_guardrail_boundary_consumption_rate=1.000，新增 catalyst proxy uncertainty 与 hydraulic latency/storage uncertainty 两类灰箱失败边界。
- R4b 已让 Agent58/59 消费 R4 field requirement patches：field_requirement_patch_consumption_rate=1.000，guardrail_package_row_count=2。
- R5 已把 6 个 guardrail 必采字段补入 Agent30/42 schema：`proxy_holdout_label`、`regeneration_event`、`tank_storage_margin`、`actuator_latency_p90`、`pump_valve_result`、`hold_time_min`；unmet_guardrail_field_count 从 6 降到 0。
- R6 已让 Agent59 消费统一 evidence gate 的 source_basis_detail_library，并为 `R4_control_guardrail_failure_backpropagation` 添加 internal synthetic replay provenance；claim-specific source_basis_completion_rate 从 0.225 提升到 1.000。
- R7 已新增真实现场数据包验收 facade：把真实 field package 验收拆成导入、timestamped replay、G6/P6、field replay evidence chain、Agent49/52 多设施控制晋级与 Agent51 催化剂代理 holdout、soft sensor field holdout、claim-specific package 和 unified evidence gate 八个阶段。
- R7S4b 已把 Agent52 控制 replay 晋级门接入上层真实包验收：`multi_facility_control_promotion_pass=False`、`catalyst_proxy_field_validation_pass=False` 时，即使未来 field replay evidence chain 局部达标，也不能输出 protective control candidate；当前 `can_emit_protective_control_candidate=False`。
- R7 当前状态为 `real_field_package_acceptance_blocked_at_import`，passed_stage_count 为 0/8；这是正确阻断，因为当前输入仍是 header-only/template 演练，不能被当成 field-supported evidence。
- Agent60 仍把 R7a 真实 field package 导入识别为最高证据价值动作；同时通过 `offline_core_fallback_action` 在没有真实包可导入时继续推进离线核心链路。当前 fallback 为 `R8p_fix_field_rows_source_preflight`：R8m 的补包字段、R8n 的 resolved/unresolved 解除门、R8o 的场景包 schema、R8u 的行级验收门、R8u-7 的 operator handoff、R8u-8 的机器可读 rows schema、R8u-9 的 runtime schema validation、R8u-10 的 collection checklist、R8u-11 的全表 field provenance gate、R8u-12 的 provenance-aware schema preflight、R8u-13 的 template-marker-aware schema preflight、R8u-14 的 same-batch bundle preflight、R8u-15 的 temporal-window preflight、R8u-16 的 scenario-semantic preflight、R8u-17 的 downstream-routing preflight、R8u-18 的 JSON/CSV-directory 双格式 source adapter、R8u-19 的 CSV 采集目录模板、R8u-20 的 R7-to-R8p 字段对齐矩阵、R8u-21 的 R7-to-R8p staging preflight/draft transformer、R8u-22 的 completion plan、R8u-23 的 Agent60 completion plan consumption、R8u-24 的 route execution contracts、R8u-25 的 route work packages、R8u-26 的 submission templates/preflight、R8u-27 的 work package patch plan 和 R8u-28 的 assembly gate 已接入主链；当前 schema validation 仍停在 `schema_validation_blocked_at_source_preflight`，R7 staging 默认停在 `r7_to_r8p_staging_preflight_no_r7_package_supplied`，completion plan 默认停在 `r7_to_r8p_completion_plan_waiting_for_r7_package`，completion route contracts 默认停在 `completion_route_contracts_ready_waiting_for_r7_package` 且 open routes 为 4/4，route work packages 默认停在 `route_work_packages_ready_waiting_for_r7_package` 且 open work packages 为 4/4，route work package preflight 默认停在 `route_work_package_preflight_waiting_for_submission_dir` 且 submitted=0、passed=0、blocked=4，route work package patch plan 默认停在 `route_work_package_patch_plan_waiting_for_submission_dir` 且 patch_items=1、highest_patch=`R8U27_SET_R7_TO_R8P_WORK_PACKAGE_DIR`，route work package assembly gate 默认停在 `route_work_package_assembly_gate_blocked_waiting_for_submission_dir` 且 assembly_steps=6、ready_steps=0、blocked_steps=6，collection checklist 状态为 `field_rows_collection_checklist_ready_needs_source_package`，template marker preflight 状态为 `template_marker_preflight_blocked_at_source_preflight`，provenance gate 状态为 `all_required_tables_require_field_origin`，provenance preflight 状态为 `provenance_preflight_blocked_at_source_preflight`，batch bundle preflight 状态为 `batch_bundle_preflight_blocked_at_source_preflight`，temporal window preflight 状态为 `temporal_window_preflight_blocked_at_source_preflight`，scenario semantic preflight 状态为 `scenario_semantic_preflight_blocked_at_source_preflight`，downstream routing preflight 状态为 `downstream_routing_preflight_blocked_at_source_preflight`，下一步可以基于 R7 shared tables + R8p supplement + Agent52 replay export 的分工形成真实 pressure conflict replay 行包并运行 R8p/R8v 验收。
- Agent44 导入入口已支持 `REAL_FIELD_REPLAY_PACKAGE_DIR` 指向真实现场 metadata/CSV 包，并补齐 R5/R7 必采字段类型化：`flow_Lmin`、`proxy_holdout_label`、`recycle_ratio`、`tank_storage_margin`、`actuator_latency_p90`、`pump_valve_result`、`hold_time_min`、`regeneration_event`。
- Agent44 现已生成 R7 真实包模板与 preflight 报告：`real_field_package_template/` 只含 header 和 TODO provenance，placeholder 会被阻断；模板已扩展 R7j supplement，但不再把节点级 long-table 字段混入主 `sensor_timeseries.csv`。主 `sensor_timeseries.csv` 保持 replay 宽表，只增加 `sensor_status`、`instrument_id`、`acquisition_time_min`、`ingest_time_min` 等质量字段；节点级 N3 UV254/ORP/压差信号进入独立 `node_modality_sensor_timeseries.csv`，离线表增加 `lab_label_time_min`、`detection_limit`、`method`、`unit`，并额外生成 `site_topology_or_bed_geometry.csv`。`real_field_package_template_preflight_metrics.json` 显示两个 supplement header ready；`real_field_package_preflight_metrics.json` 仍是当前输入包 preflight，会区分 missing headers、placeholder metadata、header-only rows、non-field origin 和 Agent44 blocker。
- R7 端到端 replay pipeline 已新增：`experiments/run_r7_real_field_replay_pipeline.py` 会把一个 package directory 送入 Agent44 preflight/import、Agent45 内部 Agent42/43 replay/G6 和 R7 acceptance；当前未设置真实包时使用 header-only template 演练，状态为 `real_field_package_acceptance_blocked_at_import`。
- R7 pipeline 现已新增 field package coverage/gap 审计：读取 package headers、非空字段、claim-specific required fields 和 soft holdout weak-target analytes，输出 `field_package_coverage_status`、`claim_specific_coverage_rate`、`soft_holdout_coverage_pass`；当前 template 演练为 `field_package_coverage_blocked_before_import`。
- R7 coverage 现已生成可机读 `patch_plan`：当前状态为 `patch_plan_blocked_at_import_preflight`，共 6 个补包项，包括替换 `metadata.json` placeholder provenance，以及为 `campaign_operation_log`、`fast_proxy_event_log`、`offline_lab_results`、`pressure_headloss_event_log`、`sensor_timeseries` 添加真实 timestamped rows。
- R7 coverage 现已加入最小 timestamped replay 包契约：当前状态为 `minimum_replay_contract_blocked_missing_rows`，common_batch_count 为 0，valid_matched_batch_count 为 0，valid_operation_action_count 为 0，valid_lab_result_count 为 0，valid_proxy_label_count 为 0，time_order_violation_count 为 0；真实包至少应形成 3 个跨 `sensor_timeseries`、`offline_lab_results`、`campaign_operation_log`、`fast_proxy_event_log` 对齐的 `batch_id`，满足 lab result、operation effect、proxy label 的时间顺序，并在同一批次上提供至少 3 组可执行且时间可解析的 operation action、QA 通过且数值非负的 offline lab 结果、可解析的 field-labeled fast proxy 事件，再进入 Agent42 smoke replay。
- R7 coverage 现已接入 `R7j_agent51_catalyst_proxy_holdout_contract`：它直接消费 Agent51 的 `weak_axis_repair_plan`，要求至少 3 个同批次证据同时具备 N3 催化剂床出口 `UV254_abs`、N3 床出口 `ORP_mV`、N3 催化剂床 `pressure_drop_kPa` 的 node/modality/value/status 长表记录，QA 通过的 `catalyst_activity` 离线标签、可解析 `regeneration_event` 操作记录，以及 `site_topology_or_bed_geometry` 中床体积/HRT/流量记录。当前 template 演练下 `field_proxy_holdout_status=field_proxy_holdout_coverage_gaps`，matched_batch_count=0；R7 pipeline 同时输出 `agent51_field_proxy_summary_status=field_proxy_holdout_coverage_gaps`、scoreable_batch_count=0，这是正确阻断；它不会覆盖 R7a import 前置门槛。
- Agent60/R7 pipeline 现已接入 R7a/R7g/R7h/R7i/R7j 分层审计：当前最高边际价值仍是先导入真实 package；真实包通过 R7a 后，如果 claim-specific 字段不足切到 R7g，如果弱目标 holdout 标签不足切到 R7h，如果共同 batch/operation/lab/proxy replay 证据不足切到 R7i，如果 Agent51 catalyst proxy 的节点级信号、床体/HRT、再生事件或 catalyst_activity 标签不足切到 R7j。R7j 只证明“可进入 Agent51 field proxy holdout 验证”，不能直接让 catalyst proxy 成为 field-supported，也不能解除 Agent49 控制保护。
- 当前完整回归：`.venv/bin/pytest -q`，`481 passed`。

## 已整理文件

- `docs/研究方案_Word兼容版.docx`：研究方案 Word 版。
- `docs/build_research_plan_docx.py`：Word 生成脚本。
- `docs/agent_system_spec.md`：执行链与支持层系统规格说明。
- `docs/project_overview_28_agent.md`：前 28 个执行 agent 的项目级总览、证据链和真实数据校准路线。
- `docs/field_data_interface_spec.md`：真实数据接口与校准准备规范。
- `deliverables/README.md`：整理阶段成果包入口。
- `deliverables/manifest.json`：核心文档、关键报告和真实数据模板清单。
- `deliverables/executive_brief.md`：项目执行摘要。
- `deliverables/presentation_outline.md`：汇报/PPT 提纲。
- `deliverables/key_metrics_table.md`：统一汇报口径的关键数值表。
- `deliverables/artifact_index.md`：成果文件索引。
- `deliverables/calibration_task_board.md`：实证校准任务板。
- `deliverables/visual_storyboard.md`：逐页视觉故事板。
- `deliverables/figure_specs.md`：Mermaid 图表和卡片/时间线规格。
- `deliverables/slide_narrative_script.md`：逐页讲述脚本。
- `deliverables/project_book_sections.md`：项目书章节素材。
- `deliverables/deck_claim_spine.md`：正式 PPT 的主张线。
- `deliverables/deck_design_system.md`：正式 PPT 的字体、调色板和版式规则。
- `deliverables/deck_qa_checklist.md`：正式 PPT 的中文字体、边界说明和布局 QA 清单。
- `deliverables/ppt/low_cost_water_ai_formal_deck.pptx`：正式 PPTX 展示包。
- `deliverables/field_calibration_protocol.md`：现场实证校准协议。
- `deliverables/field_data_acceptance_gates.md`：现场数据 G0-G6 验收门。
- `deliverables/field_calibration_runbook.md`：现场校准运行手册。
- `deliverables/model_realism_audit.md`：模型真实性审计。
- `deliverables/model_upgrade_backlog.md`：模型优化 backlog。
- `deliverables/soft_sensor_uncertainty_validation.md`：软传感不确定性验证。
- `outputs/soft_sensor_training/soft_sensor_uncertainty_metrics.json`：软传感不确定性指标。
- `deliverables/knowledge_graph_curation.md`：知识图谱策展审计。
- `deliverables/knowledge_graph_schema.md`：Scientific KG schema。
- `outputs/agent37_knowledge_graph_curation/knowledge_graph_records.json`：知识图谱结构化记录。
- `deliverables/literature_evidence_matrix.md`：文献证据矩阵。
- `deliverables/literature_evidence_schema.md`：文献证据抽取 schema。
- `outputs/agent38_literature_evidence/literature_evidence_records.json`：文献证据结构化记录。
- `deliverables/soft_sensor_conformal_calibration.md`：软传感保形校准报告。
- `outputs/soft_sensor_training/soft_sensor_conformal_metrics.json`：软传感保形校准指标。
- `deliverables/grey_box_dynamic_latency.md`：灰箱动态延迟审计。
- `outputs/grey_box_dynamic_latency/latency_budget_metrics.json`：采样、检测、执行器、暂存和回流延迟预算指标。
- `deliverables/matrix_shock_fast_proxy_control.md`：基质冲击快代理与延迟感知控制。
- `outputs/matrix_shock_fast_proxy/fast_proxy_metrics.json`：基质冲击快代理、保护动作余量和控制接入指标。
- `deliverables/timestamped_campaign_replay_schema.md`：现场时间戳回放接口。
- `outputs/agent42_timestamped_campaign_replay/agent42_report.md`：Agent42 时间戳回放报告。
- `outputs/timestamped_campaign_replay/timestamped_replay_schema.json`：sensor、lab、operation 和 fast proxy event log 同轴回放 schema。
- `outputs/timestamped_campaign_replay/templates/`：真实 timestamped replay 采集模板。
- `outputs/timestamped_campaign_replay/synthetic_timestamped_replay/`：synthetic 时间戳样例包，仅用于接口联调。
- `deliverables/field_replay_calibration_gate.md`：现场回放校准门控。
- `outputs/agent43_field_replay_calibration_gate/agent43_report.md`：Agent43 G6/P6 门控报告。
- `outputs/field_replay_calibration_gate/g6_p6_gate_metrics.json`：G6/P6 验收门、写回策略和失败边界指标。
- `deliverables/field_replay_import_protocol.md`：现场 replay 包导入协议。
- `outputs/agent44_field_replay_import/agent44_report.md`：Agent44 导入验收报告。
- `outputs/field_replay_import/import_acceptance_metrics.json`：metadata、字段、类型转换和 batch 回连验收指标。
- `outputs/field_replay_import/real_field_package_preflight_metrics.json`：真实包 preflight、header/placeholder/行数和 non-field origin 阻断报告。
- `outputs/field_replay_import/import_schema.json`：Agent44 导入 schema。
- `outputs/field_replay_import/real_field_package_template/`：R7 header-only 真实采集包模板，不能直接作为 field evidence。
- `deliverables/model_core_optimization/r7_real_field_replay_pipeline.md`：R7 真实包端到端 replay 管线说明。
- `outputs/r7_real_field_replay_pipeline/r7_real_field_replay_pipeline_report.md`：R7 管线当前运行报告。
- `outputs/r7_real_field_replay_pipeline/r7_real_field_replay_pipeline_metrics.json`：R7 管线 preflight/import/evidence chain/acceptance 指标。
- `outputs/r7_real_field_replay_pipeline/field_package_submission_repair_work_order.json`：R7 submission readiness 的可机读现场补包/修复工单。
- `outputs/r7_real_field_replay_pipeline/field_package_submission_repair_response_template.json`：R7 修复工单的 operator response 模板。
- `outputs/r7_real_field_replay_pipeline/field_package_submission_repair_response_preflight.json`：R7 operator response 的机器预检结果。
- `deliverables/field_replay_evidence_chain.md`：现场 replay 导入-回放-G6 证据链。
- `outputs/agent45_field_replay_evidence_chain/agent45_report.md`：Agent45 证据链报告。
- `outputs/field_replay_evidence_chain/evidence_chain_metrics.json`：证据链状态、写回候选和失败边界指标。
- `deliverables/soft_sensor_field_holdout_gate.md`：软传感 field holdout 放行门控。
- `outputs/agent46_soft_sensor_field_holdout_gate/agent46_report.md`：Agent46 field holdout gate 报告。
- `outputs/soft_sensor_field_holdout_gate/field_holdout_gate_metrics.json`：软传感 release gate 校准候选门控指标。
- `deliverables/weak_target_stratified_conformal.md`：弱目标分层保形校准。
- `outputs/agent47_weak_target_stratified_conformal/agent47_report.md`：Agent47 弱目标分层报告。
- `outputs/weak_target_stratified_conformal/weak_target_stratified_metrics.json`：弱目标 target/scenario coverage 指标。
- `deliverables/sensor_network_sparse_placement.md`：管网布点与稀疏感知。
- `outputs/agent48_sensor_network_sparse_placement/agent48_report.md`：Agent48 稀疏布点报告。
- `outputs/sensor_network_sparse_placement/sparse_placement_metrics.json`：node-modality 观测矩阵与布点指标。
- `deliverables/multi_facility_collaborative_control.md`：多设施协同控制与策略蒸馏。
- `outputs/agent49_multi_facility_collaborative_control/agent49_report.md`：Agent49 协同控制报告。
- `outputs/multi_facility_collaborative_control/collaborative_control_metrics.json`：facility-state/action 矩阵、联合奖励和蒸馏指标。
- `deliverables/model_core_optimization/`：Agent50 模型核心优化治理包，包含 goal、用户打断约束、外部 evidence matrix、问题排序、执行 prompt、自我打断 checklist 和治理报告。
- `outputs/agent50_model_core_governance/agent50_report.md`：Agent50 模型核心治理报告。
- `outputs/model_core_governance/priority_ranking.json`：按边际价值排序的问题清单。
- `deliverables/catalyst_activity_proxy.md`：催化剂活性代理观测设计。
- `outputs/agent51_catalyst_activity_proxy/agent51_report.md`：Agent51 催化剂活性代理观测报告。
- `outputs/catalyst_activity_proxy/catalyst_activity_proxy_metrics.json`：catalyst_activity proxy catalog、feature table、补点设计和 Agent49 接口边界。
- `deliverables/multi_facility_replay_evaluation.md`：多设施 replay 离线评估设计。
- `outputs/agent52_multi_facility_replay_evaluation/agent52_report.md`：Agent52 多设施 replay 离线评估报告。
- `outputs/multi_facility_replay_evaluation/replay_evaluation_metrics.json`：state-action-reward replay schema、baseline/guardrail-aware 离线评价指标和写回边界。
- `deliverables/model_core_optimization/control_replay_counterfactual_stress.md`：Agent49/52 控制 replay 反事实压力测试。
- `outputs/control_replay_counterfactual_stress/control_replay_stress_metrics.json`：R3 baseline、observation-aware、guardrail candidate 对照指标。
- `deliverables/model_core_optimization/control_guardrail_backpropagation.md`：R3c resolved failure cases 到灰箱机制和 field requirements 的反写。
- `outputs/control_guardrail_backpropagation/control_guardrail_backpropagation_metrics.json`：R4 mechanism coverage、field requirement coverage 和写回边界指标。
- `deliverables/minimal_grey_box_physics.md`：最小灰箱物理机制增强。
- `outputs/agent53_minimal_grey_box_physics/agent53_report.md`：Agent53 最小灰箱物理机制报告。
- `outputs/minimal_grey_box_physics/grey_box_physics_metrics.json`：灰箱物理 residual、质量守恒、旁路短流、催化剂衰减和副产物风险指标。
- `deliverables/soft_sensor_matrix_coupling.md`：软传感 node-modality/missingness 矩阵耦合。
- `outputs/agent54_soft_sensor_matrix_coupling/agent54_report.md`：Agent54 软传感矩阵耦合报告。
- `outputs/soft_sensor_matrix_coupling/soft_sensor_matrix_metrics.json`：layout contract、feature tensor、缺测压力测试、训练 schema gap 和写回边界指标。
- `deliverables/engineering_execution_constraints.md`：工程执行约束进入 reward 与仲裁。
- `outputs/agent55_engineering_execution_constraints/agent55_report.md`：Agent55 工程执行约束报告。
- `outputs/engineering_execution_constraints/engineering_constraints_metrics.json`：工程约束合同、Agent49 reward patch、Arbitration action patch 和写回边界指标。
- `outputs/agent55_engineering_execution_constraints/agent49_engineering_patched_report.md`：Agent49 消费工程约束补丁后的协同控制摘要。
- `deliverables/knowledge_graph_reasoning.md`：Agent56 可推理知识图谱与动作约束。
- `outputs/agent56_knowledge_graph_reasoning/agent56_report.md`：Agent56 KG reasoning 报告。
- `outputs/knowledge_graph_reasoning/kg_reasoning_metrics.json`：KG evidence paths、action constraints 和 field_validation_queue。
- `deliverables/main_chain_reconnection.md`：Agent57 主链回接审计。
- `outputs/main_chain_reconnection/main_chain_reconnection_metrics.json`：核心 prior 主链消费率和回接边界。
- `deliverables/field_validation_queue_alignment.md`：Agent58 现场验证队列到数据接口/gate 的映射。
- `outputs/field_validation_queue_alignment/field_validation_queue_alignment_metrics.json`：field_need_to_table/gate coverage 与 claim blocker。
- `deliverables/claim_specific_field_package.md`：Agent59 claim-specific 必采字段矩阵和 source_basis 补全任务。
- `outputs/claim_specific_field_package/claim_specific_field_package_metrics.json`：采集包 schema pass、source_basis completion 和 claim blocker 指标。
- `deliverables/model_core_optimization/agent_architecture_consolidation.md`：Agent60 对当前模型本体的模块化复盘、核心链路消费关系和减冗合并清单。
- `outputs/agent60_agent_architecture_consolidation/agent60_report.md`：Agent60 架构复盘报告。
- `outputs/agent_architecture_consolidation/architecture_consolidation_metrics.json`：Agent-to-module 映射、七层系统骨架覆盖、模块接口契约矩阵、冗余簇、核心锚点覆盖率和下一轮重构排序。
- `deliverables/model_core_optimization/unified_field_evidence_gate.md`：统一 Field Evidence Gate，合并 field evidence、claim package、source_basis、replay/holdout gate。
- `outputs/unified_field_evidence_gate_report/unified_field_evidence_gate_report.md`：统一 Field Evidence Gate 报告。
- `outputs/unified_field_evidence_gate/unified_field_evidence_gate_metrics.json`：统一证据记录、阻断类型、source_basis detail library、写回边界和下一步 R2。
- `src/water_ai/`：多智能体原型代码。
- `experiments/`：单 agent、全链条、闭环和鲁棒性模拟脚本。
- `outputs/`：各轮模拟报告。
- `tests/`：回归测试。

## 当前 Agent 链条

1. `DataQualityAgent`
   - 识别缺失、越界、突变、卡死、漂移、持续偏移、短窗口低流量。
   - 输出每个传感通道的 `sensor_scores`，供软传感器降权。

2. `SoftSensorAgent`
   - 估计污染物残留风险、反应完成度、氧化剂余量、催化剂活性、基质干扰、副产物风险、离线快检慢证据、水力置信度、达标概率、回流收益和放行准备度。
   - 当前已输出 `soft_sensor_uncertainty`、预测区间宽度、模型-启发式分歧和 OOD 风险，用于降低放行准备度和置信度。
   - 当前模型：`rf_multioutput_v3_catalyst`。
   - 模型训练数据：51840 行，其中过程动力学增强数据 34560 行。
   - 关键训练指标：mean MAE 0.01383，catalyst_activity R2 0.91363，matrix_interference R2 0.8951。

3. `MechanismAgent`
   - 将隐藏状态与传感异常转化为机理假设。
   - 已覆盖传感不确定性、水力异常、基质干扰、氧化剂不足、副产物或过氧化风险、催化剂失活、反应时间不足、循环缓冲窗口不足。
   - 已接入结构化污染物-材料-机制知识库，输出 `knowledge_matches` 并将命中条目附加到机理假设证据。

4. `FaultDiagnosisAgent`
   - 将机理假设转化为工程故障模式。
   - 新增 `cycle_window_insufficient`，把“需要循环缓冲窗口”翻译成可执行排查/控制语言。
   - 接收 Agent 3 的知识库证据，并将其写入基质干扰、氧化剂不足、催化剂失活、副产物风险等故障证据。
   - 新增 `catalyst_lifecycle_exhaustion`，用于识别再生收益衰减或寿命接近耗尽。

5. `CatalystLifecycleAgent`
   - 读取软传感状态和故障诊断结果。
   - 输出催化剂生命周期状态：活性、寿命比例、再生次数、运行循环数、再生潜力和更换紧迫度。
   - 在“寿命尚可”时推荐 `regenerate_catalyst`，在“再生收益耗尽”时推荐 `replace_catalyst`。

6. `ValidationPlanningAgent`
   - 读取软传感状态和故障诊断结果。
   - 输出 `plan_name`、`hold_min`、`validation_delay_min`、`targets` 和放行门说明。
   - 将循环争取到的时间分配给传感可靠性、放行门、氧化剂余量、副产物、基质冲击或催化剂生命周期验证。

7. `ControlStrategyAgent`
   - 输出暂存验证、核查泵阀、校准传感器、回流、补加氧化剂、催化剂再生/更换、预处理/切换单元、放行。
   - `recycle_ratio`、`extra_retention_min`、`dose_factor`、`hold_min`、`validation_delay_min`、`regen_intensity`、再生/更换 `downtime_min` 均已动态化。
   - 已接入知识库 `action_biases`，输出 `knowledge_action_biases`，并把知识偏置写入对应动作证据。
   - 已接入 `CatalystLifecycleAgent`，避免把所有催化剂问题都简化为重复再生。
   - 已接入 `ValidationPlanningAgent`，把验证目标、暂存时间和等待时间写入 `hold_for_validation`。

8. `StrategyProfileAgent`
   - 根据软传感状态和故障诊断自动选择策略目标模板。
   - 当前可选择 `balanced`、`safety_first`、`cost_first`、`emergency_response`。
   - 典型映射：清洁达标放行用 `cost_first`，传感/水力/基质/催化风险用 `safety_first`，氧化剂不足且回流收益明确时用 `emergency_response`。

9. `CostSafetyAgent`
   - 评价安全收益、成本、时间、能耗、副产物风险、催化剂再生/更换停机成本和人工复核代价。
   - 高基质冲击下提高预处理/切换单元的优先级。
   - 根据 `knowledge_action_bias` 修正安全收益、风险成本和时间成本，并输出 `knowledge_cost_adjustment`。
   - 计算统一策略目标 `objective_score`，把控制优先级、安全收益、成本、等待时间、能耗、误放行风险、副产物风险、人工复核和知识一致性放到同一可调权重函数中。
   - 支持 `balanced`、`safety_first`、`cost_first`、`emergency_response` 场景权重模板。

10. `ArbitrationAgent`
   - 执行最终硬安全门。
   - `release` 是终止动作。
   - 高基质冲击下强制先预处理/切换，再回流。
   - 低催化活性下强制先再生催化剂，再回流。
   - 高寿命耗尽风险下强制先更换催化剂，再回流。
   - 低水力置信度下强制先核查泵阀。
   - 最终动作筛选和置信度优先使用 `objective_score`，保留 `net_score` 作为解释参考。

11. `SensitivityAnalysisAgent`
   - 对观测窗口、采样间隔、禁用传感器和传感成本指数进行跨场景排序。
   - 传感成本指数已由传感器采购成本、年度维护成本、月校准工时和采样负担计算得到。
   - 候选设计可设置 `sensor_noise_multiplier`，模拟不同低成本传感配置的测量噪声。
   - `run_design_sensitivity.py` 支持缓存、`--force-refresh` 和 `--no-cache`，避免重复跑完整闭环仿真。
   - 识别“成本更低但无法稳定放行”的配置，避免把安全降级误当成低成本成功。

12. `OperationsSchedulingAgent`
   - 读取多批次 campaign 运行记录。
   - 汇总成功率、总耗时、验证工时、成本、能耗、催化剂再生/更换、备件库存和氧化剂库存。
   - 输出 `normal_intake`、`staggered_intake` 或 `pause_or_limit_intake`，并给出补库、错峰验证、限制进水等调度动作。

13. `QueuePlanningAgent`
   - 比较不同批次队列策略。
   - 当前可比较到达顺序、验证负担平滑、催化剂保护和风险优先。
   - 输出 `queue_score`、推荐队列、前 3 批安排和无法靠排序解决的瓶颈。

14. `ResourceExpansionAgent`
   - 在队列排序不足以解除瓶颈时，比较资源干预方案。
   - 当前可比较增加验证班次、补充催化剂备件、补充氧化剂、压缩低价值验证项、延长运行窗口和组合干预。
   - 输出 `intervention_score`、瓶颈解除幅度、实施成本、实施风险和剩余瓶颈。

15. `LongTermEconomicsAgent`
   - 接在资源扩容对比之后，把单 campaign 干预扩展为多 campaign 建设项目。
   - 评价多周期成本指数、预算压力、催化剂/氧化剂采购提前期、验证人员爬坡、验证压缩风险、服务水平和残余运行风险。
   - 输出 `program_score`、`selected_program`、`ranked_programs` 和过渡期限流/错峰/分阶段预算建议。

16. `PhasedImplementationAgent`
   - 将长期项目转成 campaign 级执行路线。
   - 输出过渡期限流、验证与氧化剂爬坡、催化剂采购锁定、完整能力试运行等阶段。
   - 同时给出库存安全线、验证班次计划、进水比例策略、里程碑验收和执行风险。

17. `ImplementationStressTestAgent`
   - 对分阶段实施计划做供应、预算、人力、进水压力和验收失败压力测试。
   - 输出最坏情景、总体韧性、保护性进水上限、重规划阈值和备用动作。
   - 将现实偏差转化为外部调拨、备用供应商、外包低价值验证、预算拆分和限流策略。

18. `AdaptivePortfolioAgent`
   - 读取实施压力测试信号，自动选择备用项目包、预算释放顺序和负荷控制策略。
   - 当前可比较基准执行、验证桥接、供应韧性、分阶段预算和综合韧性桥接项目包。
   - 输出 `selected_portfolio`、`budget_sequence`、`load_control_policy` 和 `dominant_stress_signals`。

19. `OnlineProjectControlAgent`
   - 读取每个 campaign 后的验收、验证工时、时间预算、库存、预算释放和进水压力。
   - 输出滚动风险、主导信号、稳定验收 streak、下一进水比例、下一预算项和是否重规划。
   - 将自适应项目组合变成 campaign 后在线控制逻辑。

20. `CampaignTelemetryAgent`
   - 从真实 batch 运行记录自动生成在线项目控制所需的 rolling campaign updates。
   - 对每个更新点调用运行调度 Agent，提取 success_rate、验证占用、时间占用、库存、瓶颈、运行模式和进水压力。
   - 把真实仿真/现场记录接入项目控制，替代手工构造的项目状态。

21. `ReplanningOrchestratorAgent`
   - 当在线项目控制触发 `replan_required` 时自动重跑后半条规划链。
   - 串联队列规划、资源扩容、长期经济性、分阶段实施、压力测试和项目组合。
   - 输出可审计 `replan_trace`，供下一轮在线控制写回基线。

22. `ControlBaselineUpdateAgent`
   - 将自动重规划的 `replan_trace` 写回下一轮在线控制基线。
   - 输出 `baseline_v1_replan`、新队列策略、新项目包、新预算顺序、保护性进水比例和写回规则。
   - 让重规划结果成为下一轮 campaign 的默认控制输入。

23. `PostReplanReplayAgent`
   - 使用写回后的 `baseline_v1_replan` 对下一轮 campaign 做投影回放。
   - 对比重规划前后的验证工时占用、时间预算占用、瓶颈集合、吞吐比例和剩余风险。
   - 验证重规划输出是否真的改善运行瓶颈。

24. `RecoveryRampAgent`
   - 在重规划后回放验证通过后，按写回规则逐步恢复进水负荷。
   - 每个爬坡点重新运行 campaign 调度，检查成功率、验证工时、总时间窗口和库存瓶颈。
   - 输出安全恢复上限、实际吞吐比例、限制瓶颈和下一轮是否应保持限流。

25. `TimeBudgetRecoveryAgent`
   - 接收 Agent24 发现的 `campaign_time_budget` 限制。
   - 比较维持安全比例、延长时间窗口、验证错峰、短耗时队列和混合方案。
   - 优先选择不破坏原高风险队列顺序的稳定恢复策略。

26. `RecoveryStrategyWritebackAgent`
   - 将 Agent25 的恢复方案写回在线控制基线。
   - 生成 `baseline_v1_replan_recovery`。
   - 写入目标进水 0.75、回退比例 0.60、验证错峰执行规则和 campaign 后复核要求。

27. `RecoveryExecutionReplayAgent`
   - 按 `baseline_v1_replan_recovery` 执行恢复后 campaign 回放。
   - 比较无错峰和执行验证错峰后的时间占用、瓶颈集合与回退需求。
   - 验证写回策略是否在执行层面稳定。

28. `RecoveryOnlineControlAgent`
   - 将恢复执行回放结果转成在线项目控制滚动更新。
   - 保留 OnlineProjectControlAgent 原始判断，同时执行恢复策略硬回退规则。
   - 输出维持 0.75、回退 0.60 或重规划的调整后控制状态。

29. `ProjectSynthesisAgent`
   - 将前 28 个执行 agent 归并为七个研究模块。
   - 输出总流程图、模块表、关键证据链、成熟度判断和真实数据校准路线。
   - 当前判断：模型可作为研究平台和项目书核心原型，但必须进入真实数据校准，不能直接宣称现场自治运行。

30. `FieldDataInterfaceAgent`
   - 定义真实数据包 schema：传感时间序列、离线检测、催化剂寿命、campaign 操作日志和经济性/部署接口。
   - 检查必需字段、记录数量、主键重复、batch_id 回连和数据来源边界。
   - 生成 `field_data_schema.json`、CSV 采集模板和 synthetic 样例数据包。
   - 当前判断：接口模板可运行，但 synthetic/sample 行不能作为现场校准结论。

31. `DeliverableOrganizationAgent`
   - 读取成果 manifest、Agent29 项目总览和 Agent30 数据接口报告。
   - 检查核心文档、关键报告和数据模板是否存在。
   - 生成执行摘要、汇报提纲、关键数值表、成果索引和实证校准任务板。
   - 当前判断：成果包 `deliverable_pack_ready`，索引文件 104/104 可用。

32. `PresentationAssetAgent`
   - 读取 Agent31 成果整理、Agent29 项目总览和 Agent30 真实数据接口报告。
   - 生成 8 页 slide 结构、8 个图表素材、逐页讲述脚本和项目书章节素材。
   - 当前判断：汇报素材 `presentation_assets_ready`，但必须披露 synthetic/sample 不是现场实证。

33. `PresentationDeckAgent`
   - 读取 Agent32 汇报素材，生成正式 PPT 的 claim spine、设计系统、QA 门槛和输出目标。
   - 明确中文字体兼容策略，避免 Word/PPT 中出现乱码、缺字或竖排压缩。
   - 当前判断：正式展示包 `formal_deck_plan_ready`，PPTX 已生成并完成预览复核。

34. `FieldCalibrationGateAgent`
   - 读取 Agent30 真实数据接口与 manifest 回归基线。
   - 生成基础 G0-G5 现场数据验收门，明确 synthetic/sample 只能用于接口演示，不能用于参数校准。
   - 生成基础 P0-P5 校准顺序：冻结现场快照、标定传感噪声漂移、重训软传感器、校准催化剂寿命、校准循环时间预算、校准成本与部署接口。
   - Agent43 后已补充 G6/P6 时间戳回放与快代理校准门，要求真实 field-labeled fast_proxy_event_log 才能写回保护性控制。
   - 生成 R1-R4 运行手册：采集最小现场数据包、运行验收门、写回模型参数、形成校准审计包。
   - 当前判断：`calibration_protocol_ready_waiting_for_field_data`，基础门控 5/6 通过，阻塞门为 `G0_data_origin`；Agent43 扩展后还需通过 `G6_timestamped_fast_proxy_replay`。

35. `ModelRealismAuditAgent`
   - 读取软传感训练指标、Agent34 现场校准门控和知识库结构。
   - 审计知识库覆盖、软传感验证、field rows、过程模型现实性缺口和可借鉴 skill 工作流。
   - 已将知识库扩展到 PFAS/持久性微污染物、重金属/形态控制、生化尾水/营养盐等更现实的污染场景，并为条目增加 evidence_stage、field_validation_need 和 source_basis。
   - 当前判断：`simulation_baseline_needs_field_grounding`，最大短板是 field_rows=0、真实 field holdout 缺失和真实现场数据尚未通过 G0。

36. `SoftSensorUncertaintyValidationAgent`
   - 读取软传感预测、合成 holdout 真值和不确定性层输出。
   - 检查 prediction interval coverage、平均误差、区间宽度、高低不确定性误差差异、OOD 警报和放行阻断。
   - 当前判断：`synthetic_uncertainty_layer_ready_needs_field_holdout`，synthetic holdout 上高不确定性样本误差更高，但不能替代真实 field validation。

37. `KnowledgeGraphCurationAgent`
   - 按 Scientific Knowledge Graph 思路把知识库整理为污染物、基质、材料、过程条件、低成本信号、隐藏状态和证据等级七类轴。
   - 输出 KG schema、图谱记录、轴覆盖缺口、科学审查链和证据抽取 backlog。
   - 当前判断：`scientific_kg_seed_needs_literature_and_field_evidence`，field-supported edges 为 0，下一步必须补文献抽取、原始信号边和真实离线标签验证。

38. `LiteratureEvidenceAgent`
   - 将多智能体催化剂发现、WWTP 软传感、动态控制、保形不确定性、Scientific KG、抗生素/染料/农药 AOP 文献转成 evidence records。
   - 每条记录都包含 borrowed idea、现实映射、数据需求、实现路径、评价指标和失败边界。
   - 当前判断：`literature_seed_ready_field_validation_required`，文献 seed 覆盖 KG 缺口 0.889，但仍不能替代真实 field validation。

39. `SoftSensorConformalCalibrationAgent`
   - 读取 Agent36 的软传感验证误差和不确定性指标，构建 split conformal 校准接口。
   - 输出目标级非一致性阈值、预测区间覆盖率、平均区间宽度、scenario full coverage、release abstention 和 OOD alert 统计。
   - 当前判断：`synthetic_conformal_interface_ready_needs_field_holdout`，synthetic holdout 上覆盖率为 0.975、平均区间宽度为 0.233，但 `can_write_to_release_gate=False`，必须等待真实 field holdout 重算阈值后才能写入放行门。

40. `GreyBoxDynamicLatencyAgent`
   - 读取文献证据中的 `grey_box_dynamic_control_latency` 升级方向，并结合 Agent39 保形校准边界和 Agent27 恢复回放上下文。
   - 将采样间隔、质控窗口、软传感计算、人工复核、离线检测 turnaround、执行器响应、混合、暂存和回流统一成时序约束。
   - 输出 action latency margin、evidence latency margin、latency_budget_violation_rate、field replay 写回条件和场景失败边界。
   - 当前判断：`synthetic_latency_budget_ready_needs_field_timestamps`，synthetic replay 延迟违约率为 0.200，`matrix_shock` 慢证据余量为 -31 min，必须采集现场 timestamped campaign replay 后才能写入 release gate。

41. `MatrixShockFastProxyAgent`
   - 用 EC、浊度、UV254、pH 和 ORP 组成基质冲击快代理，在慢离线检测回来前触发保护性预处理/切换。
   - 将 Agent40 暴露的 `matrix_shock` 慢证据 -31 min 问题转化为控制接入：保护动作余量 59 min，暂存窗口从 35 min 增至 90 min。
   - 输出 proxy_score、specificity_guard、protective action latency、误触发验证需求和 release policy。
   - 当前判断：`synthetic_fast_proxy_ready_needs_field_timestamp_validation`，快代理只允许保护性控制，不能授权自动放行；必须用现场 timestamped replay 验证 precision、recall、提前量和误触发成本。

42. `TimestampedCampaignReplayAgent`
   - 将低成本传感、离线检测结果返回、控制动作命令/生效和 fast proxy event log 对齐到同一 batch 时间轴。
   - 输出 timestamp_coverage、proxy_precision、proxy_recall、protective action lead time、lab turnaround、actuator latency 和误触发成本。
   - 当前判断：`synthetic_timestamp_schema_ready_needs_field_replay`，schema 和 replay 计算可运行，但 synthetic 样例不能作为快代理现场有效性证据；必须导入真实 field-labeled replay 后才能写入保护性控制。

43. `FieldReplayCalibrationGateAgent`
   - 读取 Agent42 的 replay 指标和 Agent41 的快代理边界。
   - 将 data_origin、时间戳覆盖、batch 回连、proxy label 数、precision/recall、保护性提前量、执行器 P90 延迟、误触发成本和自动放行禁止边界转成 G6/P6 硬验收门。
   - 当前判断：`synthetic_replay_gate_blocked`，G6 当前 7/8 可计算，但 `G6_1_field_origin` 未通过；`can_write_to_protective_control=False`，`can_write_to_release_gate=False`。

44. `FieldReplayImportAgent`
   - 读取带 metadata.json 的 sensor、lab、operation 和 fast_proxy_event_log CSV 包。
   - 检查 provenance、field origin、必需字段、数字/布尔类型转换和 batch 回连。
   - 当前判断：`field_replay_import_blocked_non_field_origin`，synthetic 包只能联调，不能进入 Agent42/Agent43。

45. `FieldReplayEvidenceChainAgent`
   - 按 Agent44 -> Agent42 -> Agent43 顺序串联导入、时间戳回放和 G6/P6 门控。
   - 只有完整链条通过时才形成 matrix_shock 保护性写回候选；仍需人工复核，且不写 release gate。
   - 当前判断：`field_replay_evidence_chain_blocked_at_import`，synthetic 包未通过 Agent44，因此不运行 downstream replay。

46. `SoftSensorFieldHoldoutGateAgent`
   - 按 Agent36 -> Agent39 -> Agent46 顺序串联不确定性验证、保形校准和 release gate 候选门控。
   - 只有真实 field holdout 同时满足覆盖率、区间宽度、OOD/abstention、弱目标覆盖和场景多样性时，才形成软传感 release gate 校准候选。
   - 当前判断：`soft_sensor_release_gate_blocked_non_field_holdout`，synthetic holdout 只能作为接口验证，不能写入放行门。

47. `WeakTargetStratifiedConformalAgent`
   - 将 `catalyst_activity` 和 `matrix_interference` 从总体 coverage 中拆出，按 target 和 scenario 审查 conformal 覆盖。
   - 只向 Agent46 提供弱目标分层阈值候选，不能绕过 Agent46 写入 release gate。
   - 当前判断：`weak_target_stratified_synthetic_candidate_needs_field_holdout`，最弱目标为 `matrix_interference`，coverage 为 0.875。

48. `SensorNetworkSparsePlacementAgent`
   - 把处理单元/管网节点与传感器模态组成 node-modality 稀疏观测矩阵。
   - 当前已比较 greedy、reconstruction QR proxy、classification SSPOC proxy 和 topology robust cost proxy 四类布点策略，选中 `greedy_marginal`，comparable_score 为 0.726。
   - 当前判断：`sparse_sensor_layout_ready_needs_field_topology`，已选择 6 个候选布点，总成本指数 4.176。
   - weak_state_coverage 为 0.300，说明 `catalyst_activity` 仍缺直接观测支撑。

49. `MultiFacilityCollaborativeControlAgent`
   - 把 Agent48 稀疏观测矩阵转成均质池、反应核心、催化剂床、回流环和末端精处理的 facility-state/action 矩阵。
   - 当前已消费 R2 observation contract，`catalyst_activity_observability` 和 `weak_state_coverage` 均从 0.300 更新到 0.580，`weak_state_ready=True`。
   - 当前已消费 R3b control replay guardrails：J4/J3 获得 guardrail bonus，J2/J0 在缺 field proxy/hydraulic evidence 时获得 guardrail penalty。
   - 当前判断：`synthetic_collaborative_policy_needs_field_replay`，策略蒸馏准确度代理值约 0.790。
   - 该层只形成协同控制候选和可解释规则树；没有真实多节点 state-action replay 前，不写执行器或放行门。

50. `ModelCoreOptimizationGovernanceAgent`
   - 读取 manifest、Agent48/49、Agent51-59 的核心指标、外部方法 evidence matrix 和当前 backlog。
   - 输出 priority_ranking、blocked_reasons、recommended_next_core_action、self_interrupt_verdict 和 low_priority_backlog。
   - 历史判断为 `P11_source_basis_detail_or_real_field_package_import`；该任务已由 R1/R1b 统一 gate 和 source_basis detail library 承接完成。
   - 当前治理判断由 Agent60 接管到架构复盘层：R3/R3b/R3c/R4/R4b/R5/R6 已完成；Agent60 已接入 R7 pipeline/coverage，当前最高边际价值任务为 `R7a_import_real_field_package_with_metadata_and_csv`，后续会按 coverage 缺口切换到 R7g/R7h。

51. `CatalystActivityProxyAgent`
   - 读取 Agent48 的 node-modality 稀疏布点结果，围绕催化剂床构造 UV254 去除率、ORP 衰减、浊度/压降污堵、再生响应增益和停留时间归一化速率残差。
   - 当前判断：`synthetic_catalyst_proxy_design_ready_needs_field_labels`，current_proxy_observability 为 0.331，proxy_observability_after_recommended_patch 为 0.720。
   - 推荐补点：`N3_catalyst_bed_outlet:UV254_abs`、`N3_catalyst_bed_outlet:ORP_mV` 和 `N3_catalyst_bed:pressure_drop_kPa`。
   - 该层只能更新设计先验；没有 field_proxy_holdout 前，不放松 Agent49 催化剂不确定性保护，不写执行器或 release gate。

52. `MultiFacilityReplayEvaluationAgent`
   - 读取 Agent49 协同控制候选、Agent51 catalyst proxy 指标和 synthetic replay cases。
   - 输出 state-action-reward replay schema、offline evaluation metrics、reward diagnostics、distillation evaluation 和 Agent49 writeback boundary。
   - 当前判断：`synthetic_replay_evaluation_ready_needs_field_replay`，joint_action_accuracy 为 0.667，mean_reward_regret 为 0.055，`R2_catalyst_uncertain_low_proxy` 的保护性误触发成本为 0.18。
   - 该层只能写回 reward prior、replay schema 和 offline metric contract；没有真实多节点 field replay 前，不写 actuator policy、release gate policy 或 online MARL training。

53. `MinimalGreyBoxPhysicsAgent`
   - 读取 synthetic 场景状态，构造停留时间分布、旁路/短流、拟一级反应、基质抑制、催化剂有效活性、氧化剂消耗、质量守恒和副产物风险的最小 physics prior。
   - 当前判断：`synthetic_grey_box_physics_prior_ready_needs_field_calibration`，mean_grey_box_residual 为 0.131，max_mass_balance_residual 为 0.000，max_byproduct_risk 为 0.597。
   - 该层只能写回 soft_sensor_physics_prior、Agent49 reward residual candidate 和 Agent50 P4 状态；没有 field RTD、进出水污染物、氧化剂余量、催化剂历史和副产物 lab panel 前，不写执行器、release gate 或现场机理结论。

54. `SoftSensorMatrixCouplingAgent`
   - 读取 Agent48 的 `soft_sensor_interface`、软传感训练指标和 Agent53 灰箱物理指标。
   - 输出 `time,node,modality,feature_channel` 软传感输入合同，feature channel 包含 `sensor_value`、`availability_mask`、`time_since_last_observed_min`、`data_quality_score`、`observation_axis_weight` 和 `grey_box_residual_prior`。
   - 当前判断：`synthetic_layout_aware_soft_sensor_contract_ready_needs_field_missingness`，layout_contract_score 为 1.000，missingness_robustness_score 为 0.684。
   - live_layout_context_status 为 `global_modality_fallback_used_for_layout`，说明当前仍缺真实 node-specific 传感值；没有 field node-specific values、layout holdout split 和 missingness replay 前，不写 release gate 或现场缺测鲁棒性结论。

55. `EngineeringExecutionConstraintAgent`
   - 读取 Agent49 多设施协同控制指标，把每个 joint action 对池容、泵阀动作、执行器延迟、药剂库存、维护窗口、人工复核和误动作成本的需求转成约束压力。
   - 输出 `agent49_reward_patch`、`action_constraint_patch`、`arbitration_patch` 和 `agent50_writeback`。
   - 当前判断：`synthetic_engineering_constraints_reward_patch_ready_needs_plc_scada_and_field_replay`，mean_execution_feasibility 为 0.980，hard_blocked_joint_action_count 为 1。
   - 该层已经接入 Agent49 reward、CostSafety 成本风险修正和 Arbitration 硬阻断；没有 PLC/SCADA 点表、SOP 和 field execution replay 前，不写执行器或 release gate。

56. `KnowledgeGraphReasoningAgent`
   - 把知识库升级为 typed KG reasoning，输出 mechanism evidence paths、action constraint patch、field_validation_queue 和 agent_chain_retrospective。
   - 当前判断：`kg_reasoning_patch_ready_needs_field_supported_edges`，evidence_traceability 为 1.000，constraint_hit_rate 为 1.000，field_supported_edge_ratio 为 0.000。
   - 该层只能改变机理解释和动作排序先验；没有 field-supported edges 前，不写执行器、release gate 或现场机理结论。

57. `MainChainReconnectionAgent`
   - 审计 Agent53 灰箱 prior、Agent54 布点/缺测合同、Agent55 工程约束、Agent56 KG 约束和 Agent49 联动动作是否真正被 Agent1-10 主链消费。
   - 当前判断：`synthetic_main_chain_reconnection_ready_needs_field_replay`，main_chain_prior_consumption_rate 为 1.000。
   - 该层证明核心 prior 已进入主链，但仍只是 synthetic consumption audit；没有 field replay 前不升级控制结论。

58. `FieldValidationQueueAlignmentAgent`
   - 把 Agent56 的 field_validation_queue 映射到 Agent30 数据表、Agent42 时间戳 replay、Agent44 metadata provenance、Agent43/45 G6/P6 gate 和验收指标。
   - 当前判断：`field_validation_alignment_ready_needs_real_field_package`，field_need_to_table_coverage 为 1.000，field_need_to_gate_coverage 为 1.000。
   - 该层把“缺真实数据”细化为“缺哪些表、字段、metadata 和 gate”，但不产生现场有效性结论。

59. `ClaimSpecificFieldPackageAgent`
   - 把 Agent58 mapping_table 升级为每条 claim 的必采字段矩阵、metadata、gate、acceptance artifacts 和 source_basis 补全任务。
   - 当前判断：`claim_specific_package_ready_needs_real_data_and_source_basis_detail`，minimal_field_package_schema_pass_rate 为 1.000，source_basis_completion_rate 为 1.000，minimal_field_package_field_pass_rate 为 0.000。
   - 该层暴露出 `source_basis` 仍多为方法标签，下一步必须补具体 citation、参数范围和适用边界，或导入真实 field package 走证据链。

## 当前架构复盘模块

- Agent60 `AgentArchitectureConsolidationAgent` 是本轮复盘治理工具，不计入当前模型能力链。
- 它将原有 59 个 agent 归并为 9 个模块：
  1. 低成本稀疏感知与布点。
  2. 软传感、缺测矩阵与不确定性。
  3. 灰箱物理、机理解释与故障诊断。
  4. 循环式处理、多设施协同控制与仲裁。
  5. 知识图谱、文献证据与 claim 审查。
  6. 现场数据接口、replay 与证据门控。
  7. 项目运行、资源调度与实施管理。
  8. 模型治理、主链回接与减冗复盘。
  9. 展示、文档与汇报材料，默认冻结为低优先级。
- 核心链路消费关系已显式化：Agent48 -> Agent51/54/49，Agent51 -> Agent49/52，Agent53 -> Agent54/57，Agent54 -> Agent2/49，Agent49 -> Agent52/55，Agent55 -> Agent49/6/7，Agent56 -> Agent3/5/58，Agent59 -> Agent50/后续 source_basis 细化。
- 当前 R1/R1b 已完成统一 field evidence、claim package、source_basis gate 和 source_basis detail library；R2 已完成 Agent48/51/54 observation contract；R3/R3b/R3c 已完成 Agent49/52 反事实 replay、reward prior guardrail 和 guardrail-aware replay；R4 已完成控制失败到灰箱/field requirements 的反写；下一重构优先级为让 Agent53/58/59 消费 R4 patches。
- 所有这些结论仍属于 architecture/synthetic/literature-supported 层，不产生 field-supported 结论。

## 当前统一证据门控

- `UnifiedFieldEvidenceGate` 是 facade，不是新 agent；它合并 Agent43/44/45/46/58/59 的 field evidence、claim package、source_basis 和 replay/holdout gate。
- 当前统一记录数为 3：`FVQ01` 真实传感漂移记录、`FVQ02` 离线放行标签、`FVQ03` 低浓度目标物检测限。
- 当前统一阻断类型包括：`field_origin_not_verified`、`field_replay_import_not_passed`、`failed_replay_gate:G6_1_field_origin`、`field_replay_evidence_chain_not_passed`、`failed_soft_sensor_gate:SFG0_field_holdout_origin`、`failed_soft_sensor_gate:SFG5_weak_target_coverage`、`source_basis_literature_detail_complete_not_field_supported`。
- source_basis detail 状态：`citation_detail_completion_rate=1.000`、`source_basis_parameter_boundary_coverage=1.000`、`effective_literature_traceability=1.000`、`field_supported_edge_ratio=0.000`。
- 当前允许写回：统一 claim blocker 表、统一 field package requirements、source_basis detail tasks、R1/R1b status。
- 当前禁止写回：actuator policy、release gate policy、field mechanism claim、field control effectiveness claim。
- R1/R1b 已完成；source_basis 细节已从“缺 citation/参数边界”升级为“literature-supported traceability 完整但仍未 field-supported”，不能升级为现场验证结论。当前下一步已由 R2 观测契约、R3 控制 replay、R3b reward prior、R3c guardrail-aware replay、R4 灰箱/field 反写、R4b patch consumption、R5 schema 覆盖和 R6 source_basis 接入承接后切换到 R7 真实 field package 导入验收。

## 当前安全门

- `release_readiness >= 0.82` 才能放行。
- `pollutant_residual_risk <= 0.35` 才能放行。
- `sensor_confidence >= 0.75` 才能自动放行。
- `hydraulic_confidence >= 0.7` 才能自动放行。
- `byproduct_risk <= 0.65` 才能自动放行。
- `oxidant_remaining >= 0.45` 时禁止盲目补加氧化剂。
- `recycle_gain < 0.2` 时禁止无效回流。
- `catalyst_activity > 0.68` 时禁止无效催化剂再生。
- `catalyst_replacement_urgency < 0.55` 时禁止过早更换催化剂。
- `catalyst_replacement_urgency >= 0.72` 且 `catalyst_regeneration_potential <= 0.30` 时禁止继续无效再生。

## 当前验证

- `pytest -q`：266 passed。
- `experiments/run_scenario_sweep.py`：
  - `clean_release`：`cost_first`，放行。
  - `sensor_faults`：`safety_first`，核查泵阀、校准传感器、旁路验证、回流。
  - `oxidant_limitation`：`emergency_response`，补加氧化剂并回流。
  - `reaction_time_insufficient`：`balanced`，继续回流。
  - `catalyst_deactivation`：`safety_first`，先再生催化剂，再回流。
  - `matrix_shock`：`safety_first`，先预处理/切换单元，旁路验证后再回流。
- `experiments/run_agent10_catalyst_lifecycle.py`：
  - `remaining_life_regeneration`：`regenerate_catalyst` -> `recirculate`。
  - `exhausted_life_replacement`：`replace_catalyst` -> `recirculate`。
- `experiments/run_closed_loop_episode.py`：
  - `sensor_faults`：2 步收敛。
  - `oxidant_limitation`：3 步收敛。
  - `reaction_time_insufficient`：3 步收敛。
  - `catalyst_deactivation`：3 步收敛。
  - `matrix_shock`：2 步收敛。
- `experiments/run_closed_loop_robustness.py`：
  - 每个问题场景 30 个随机种子，共 150 条 episode。
  - 所有场景 success_rate 均为 1.0。
  - 失败样本 0。
- `experiments/run_design_sensitivity.py`：
  - 推荐 `full_36min_3min`：完整低成本传感、36 min 观测窗口、3 min 采样间隔。
  - 噪声倍率 0.75，平均成功率 1.0，平均总耗时 155.4 min，综合评分 0.882。
  - 工程成本指数 0.9，采购成本 11800 CNY，年度维护成本 5040 CNY，月校准约 9.02 h。
  - 已生成 5 个 v6 默认设计缓存文件，普通运行直接命中缓存。
  - `no_uv_48min_3min`、`core_48min_5min`、`minimal_60min_5min` 在当前模型下均无法稳定放行，说明 UV254 仍是关键低成本观测通道。
- `experiments/run_agent50_model_core_governance.py`：
  - self_interrupt_verdict：`continue_core_work`。
  - recommended_next_core_action：`P6_reasonable_knowledge_graph_upgrade`。
  - blocked_reasons：Agent51 catalyst proxy 仍缺 field_proxy_holdout、Agent52 仍缺真实多节点 state-action-reward replay、Agent53 仍缺 field RTD/进出水污染物/氧化剂/催化剂/副产物校准、Agent54 仍缺 field node-specific values、layout holdout splits 和 missingness replay、Agent55 仍缺 PLC/SCADA 点表、SOP 和 field execution replay。
  - 生成 `deliverables/model_core_optimization/` 治理包、Agent50 报告和 `outputs/model_core_governance/priority_ranking.json`。
  - 结论：后续每轮优先做模型核心增量；展示层、Word、PPT 和索引美化默认低优先级。
- `experiments/run_agent60_agent_architecture_consolidation.py`：
  - audited_scope：当前模型本体，Agent60 只是复盘治理工具。
  - architecture_status：`module_consolidation_ready_with_complete_interface_contracts`。
  - mapped_agent_count：60/60。
  - module_count：9。
  - core_anchor_coverage：1.000。
  - interface_contract_coverage：1.000。
  - redundancy_cluster_count：5。
  - presentation_freeze_agent_count：3。
  - recommended_next_refactor：`R7a_import_real_field_package_with_metadata_and_csv`；无真实包时 fallback 为 `R8p_fix_field_rows_source_preflight`，需要先按 R8p operator handoff 和 `pressure_resolution_replay_rows_schema.json` 创建真实行包并运行验收命令，R8p 真实行验收通过后才推进 R8v。
  - 结论：当前阶段不再继续按 agent 编号堆叠；优先统一 field evidence、claim package 与 source_basis gate，然后再做 Agent48/51/54 observation contract 合并和 Agent49/52 replay 反事实压力测试。
- `experiments/run_agent51_catalyst_activity_proxy.py`：
  - catalyst_proxy_status：`synthetic_catalyst_proxy_design_ready_needs_field_labels`。
  - current_proxy_observability：0.331。
  - proxy_observability_after_recommended_patch：0.720。
  - weak_state_coverage_after_proxy_design：0.720。
  - can_relax_agent49_catalyst_uncertainty_block：False。
  - 结论：Agent51 已把 catalyst_activity 弱观测从概念缺口推进到可测试代理设计；没有 field_proxy_holdout 前，只能作为 Agent48/49 设计先验，不能放松 Agent49 保护规则。
- `experiments/run_agent52_multi_facility_replay_evaluation.py`：
  - replay_evaluation_status：`synthetic_replay_evaluation_ready_needs_field_replay`。
  - replay_case_count：6。
  - joint_action_accuracy：0.667。
  - mean_reward_regret：0.055。
  - protective false positive action cost：0.18。
  - can_write_to_actuator：False。
  - can_write_to_release_gate：False。
  - 结论：Agent52 已把 Agent49 多设施协同控制候选推进到 replay-ready 离线评估框架；没有真实多节点 replay 前，不进入执行器候选。
- `experiments/run_agent53_minimal_grey_box_physics.py`：
  - grey_box_physics_status：`synthetic_grey_box_physics_prior_ready_needs_field_calibration`。
  - scenario_count：5。
  - mean_grey_box_residual：0.131。
  - max_grey_box_residual：0.206。
  - max_mass_balance_residual：0.000。
  - physics_violation_rate：0.600。
  - violation_scenarios：`reaction_time_insufficient`、`catalyst_deactivation`、`matrix_shock`。
  - can_write_to_actuator：False。
  - can_write_to_release_gate：False。
  - 结论：Agent53 已把 P4 灰箱物理机制从概念缺口推进到可审计 synthetic physics prior；Agent54 已接入该先验到软传感矩阵合同，同时等待 field 物理校准。
- `experiments/run_agent54_soft_sensor_matrix_coupling.py`：
  - soft_sensor_matrix_status：`synthetic_layout_aware_soft_sensor_contract_ready_needs_field_missingness`。
  - layout_contract_score：1.000。
  - missingness_robustness_score：0.684。
  - live_layout_context_status：`global_modality_fallback_used_for_layout`。
  - mask_shape：`[6, 5]`，layout_id：`greedy_marginal:6x10`。
  - current_model_layout_aware：False，缺 `layout_id`、`node_id`、`zone`、`modality`、`availability_mask`、`time_since_last_observed_min` 和 `grey_box_residual_prior`。
  - can_write_to_release_gate：False。
  - 结论：Agent54 已把 P5 从“软传感不知道布点/缺测结构”推进到可审计输入合同；下一轮最高边际价值转向 P7 工程执行约束进入 Agent49 reward 和最终仲裁。
- `experiments/run_agent55_engineering_execution_constraints.py`：
  - engineering_constraints_status：`synthetic_engineering_constraints_reward_patch_ready_needs_plc_scada_and_field_replay`。
  - mean_execution_feasibility：0.980。
  - hard_blocked_joint_action_count：1。
  - reward_patch_coverage：1.000，arbitration_patch_coverage：1.000。
  - 当前主要阻断：`J2_catalyst_protection_before_regeneration` 的 `maintenance_window_pressure`。
  - can_update_agent49_reward_contract：True。
  - can_patch_final_arbitration：True。
  - can_write_to_actuator：False，can_write_to_release_gate：False。
  - 结论：Agent55 已把 P7 从“工程约束说明”推进到可被 Agent49 reward、CostSafety 和 Arbitration 消费的 synthetic patch；下一轮最高边际价值由 Agent50 转向 P6 可推理 KG。
- `experiments/run_agent24_recovery_ramp.py`：
  - verdict：`partial_ramp_hold`。
  - 稳定轮次：1/2。
  - 安全进水上限：0.60。
  - 实际吞吐比例：0.625。
  - 尝试进水比例 0.75 时重新触发 `campaign_time_budget`。
  - 结论：下一轮可以从 0.45 保守恢复到 0.60，但必须先解决总时间窗口压力，才能继续恢复到 0.75。
- `experiments/run_agent25_time_budget_recovery.py`：
  - verdict：`target_recovery_feasible`。
  - 推荐方案：`stagger_validation_overlap`。
  - 目标进水比例：0.75。
  - 时间预算占用：0.884。
  - 验证工时占用：0.394。
  - 结论：在不改变原队列顺序的条件下，通过旁路验证与回流观察错峰，可以有条件恢复到 0.75。
- `experiments/run_agent26_recovery_strategy_writeback.py`：
  - baseline_version：`baseline_v1_replan_recovery`。
  - writeback_mode：`conditional_target_recovery`。
  - next_intake_fraction：0.75。
  - fallback_intake_fraction：0.60。
  - selected_candidate_id：`stagger_validation_overlap`。
  - 结论：恢复策略已经成为下一轮在线控制输入，并要求 campaign 后继续遥测、回放和爬坡复核。
- `experiments/run_agent27_recovery_execution_replay.py`：
  - replay_verdict：`recovery_execution_validated`。
  - 无错峰 time_budget_usage：0.978。
  - 执行错峰策略后 time_budget_usage：0.884。
  - validation_staff_usage：0.394。
  - strategy_bottleneck_ids：空。
  - recommended_next_intake_fraction：0.75。
- `experiments/run_agent28_recovery_online_control.py`：
  - recovery_control_mode：`maintain_conditional_recovery`。
  - next_intake_fraction：0.75。
  - fallback_intake_fraction：0.60。
  - replan_required：False。
  - 结论：恢复执行回放结果已接回在线控制，下一轮维持条件恢复进水。
- `experiments/run_agent29_project_synthesis.py`：
  - synthesized_agent_count：28。
  - maturity_level：`research_platform_ready_for_field_calibration`。
  - recovery_control_mode：`maintain_conditional_recovery`。
  - next_intake_fraction：0.75。
  - fallback_intake_fraction：0.60。
  - 输出：`outputs/agent29_project_synthesis/agent29_report.md` 与 `docs/project_overview_28_agent.md`。
  - 结论：当前模型可以作为研究平台与重大项目方案骨架，下一阶段要接入真实传感器时间序列、离线检测标签、催化剂寿命记录和中试 campaign 运行日志。
- `experiments/run_agent30_field_data_interface.py`：
  - interface_status：`template_ready_not_field_validated`。
  - field_coverage：1.0。
  - linkage_score：1.0。
  - calibration_readiness_score：1.0。
  - 生成：`outputs/agent30_field_data_interface/field_data_schema.json`。
  - 生成：`outputs/agent30_field_data_interface/field_data_templates/`。
  - 生成：`outputs/agent30_field_data_interface/synthetic_field_data_package/`。
  - 生成：`docs/field_data_interface_spec.md`。
  - 结论：P1-P5 校准任务在字段契约上已有模板入口；Agent42/43 后新增 P6 时间戳回放与 G6 写回门控，下一步应以真实现场数据替换 synthetic/sample 行。
- `experiments/run_agent31_deliverable_organization.py`：
  - deliverable_status：`deliverable_pack_ready`。
  - deliverable_score：1.0。
  - available_artifacts：101/101。
  - presentation_outline：8 个章节。
  - 生成：`deliverables/executive_brief.md`。
  - 生成：`deliverables/presentation_outline.md`。
  - 生成：`deliverables/key_metrics_table.md`。
  - 生成：`deliverables/artifact_index.md`。
  - 生成：`deliverables/calibration_task_board.md`。
  - 结论：整理阶段已有统一成果入口和汇报素材。
- `experiments/run_agent32_presentation_assets.py`：
  - asset_status：`presentation_assets_ready`。
  - asset_score：1.0。
  - slide_count：8。
  - visual_asset_count：8。
  - 生成：`deliverables/visual_storyboard.md`。
  - 生成：`deliverables/figure_specs.md`。
  - 生成：`deliverables/slide_narrative_script.md`。
  - 生成：`deliverables/project_book_sections.md`。
  - 结论：当前素材继续作为项目书图表和汇报复核来源；正式 PPTX 已冻结为 Agent33 快照。
- `experiments/run_agent33_presentation_deck.py`：
  - deck_status：`formal_deck_plan_ready`。
  - deck_score：1.0。
  - slide_count：8。
  - qa_gate_count：5。
  - 生成：`deliverables/deck_claim_spine.md`。
  - 生成：`deliverables/deck_design_system.md`。
  - 生成：`deliverables/deck_qa_checklist.md`。
  - 生成：`deliverables/ppt/low_cost_water_ai_formal_deck.pptx`。
  - 结论：整理阶段已经从文字素材推进到正式 PPTX 交付，且预览中中文渲染正常。
- `experiments/run_agent34_field_calibration_gate.py`：
  - calibration_gate_status：`calibration_protocol_ready_waiting_for_field_data`。
  - gate_score：0.833。
  - accepted_gates：基础门控 5/6；Agent43 扩展后还需 G6。
  - 阻塞门：`G0_data_origin`，原因是当前数据来源仍为 `synthetic`。
  - 生成：`deliverables/field_calibration_protocol.md`。
  - 生成：`deliverables/field_data_acceptance_gates.md`。
  - 生成：`deliverables/field_calibration_runbook.md`。
  - 结论：已经有可执行的现场校准协议，但必须导入真实 field 数据后才能写回参数。
- `experiments/run_agent35_model_realism_audit.py`：
  - realism_status：`simulation_baseline_needs_field_grounding`。
  - realism_score：0.771。
  - knowledge_base entries：9。
  - field_rows：0。
  - has_uncertainty_layer：True。
  - weaker_targets：`catalyst_activity`、`matrix_interference`。
  - 生成：`deliverables/model_realism_audit.md`。
  - 生成：`deliverables/model_upgrade_backlog.md`。
  - 结论：当前模型仍是仿真基线，后续优先补真实数据验收、软传感 field holdout / 保形校准和知识图谱证据矩阵。
- `experiments/run_agent36_soft_sensor_uncertainty_validation.py`：
  - uncertainty_validation_status：`synthetic_uncertainty_layer_ready_needs_field_holdout`。
  - overall_interval_coverage：1.0。
  - mean_abs_error：0.0613。
  - uncertainty_tracks_error：True。
  - ood_alert_count：0。
  - 生成：`deliverables/soft_sensor_uncertainty_validation.md`。
  - 生成：`outputs/soft_sensor_training/soft_sensor_uncertainty_metrics.json`。
  - 结论：不确定性层已经能作为 synthetic 内部风险门，但必须等待真实离线标签做 field holdout 和释放概率校准。
- `experiments/run_agent37_knowledge_graph_curation.py`：
  - kg_curation_status：`scientific_kg_seed_needs_literature_and_field_evidence`。
  - axis_coverage_score：0.700。
  - field_supported_entry_count：0。
  - 主要缺口：染料、抗生素、农药；pH 调节、温度、流量/水力；原始低成本信号到隐藏状态的证据边。
  - 生成：`deliverables/knowledge_graph_curation.md`。
  - 生成：`deliverables/knowledge_graph_schema.md`。
  - 生成：`outputs/agent37_knowledge_graph_curation/knowledge_graph_records.json`。
  - 结论：知识库已从条目清单推进到可审查 KG seed，但仍不能宣称现场证据成立。
- `experiments/run_agent38_literature_evidence.py`：
  - literature_evidence_status：`literature_seed_ready_field_validation_required`。
  - literature_evidence_score：0.804。
  - seed records：8。
  - kg_gap_closure_score：0.889。
  - field_supported_record_count：0。
  - 已覆盖 KG 缺失污染物轴：染料、抗生素、农药。
  - 生成：`deliverables/literature_evidence_matrix.md`。
  - 生成：`deliverables/literature_evidence_schema.md`。
  - 生成：`outputs/agent38_literature_evidence/literature_evidence_records.json`。
  - 结论：文献证据已能指导软传感保形校准、灰箱动态控制延迟和 field-supported KG edges，但所有结论仍需 field validation。
- `experiments/run_agent39_soft_sensor_conformal_calibration.py`：
  - conformal_status：`synthetic_conformal_interface_ready_needs_field_holdout`。
  - conformal_score：0.854。
  - evidence_stage：`synthetic_holdout`。
  - overall_conformal_coverage：0.975。
  - mean_conformal_interval_width：0.233。
  - release_abstention_rate：0.125。
  - can_write_to_release_gate：False。
  - 生成：`deliverables/soft_sensor_conformal_calibration.md`。
  - 生成：`outputs/agent39_soft_sensor_conformal_calibration/agent39_report.md`。
  - 生成：`outputs/soft_sensor_training/soft_sensor_conformal_metrics.json`。
  - 结论：保形校准接口已经成型，但 synthetic 校准不能替代真实现场保形阈值；下一步应采集 field holdout 并重算阈值、放行 abstention 与 OOD 门。
- `experiments/run_agent40_grey_box_dynamic_latency.py`：
  - latency_status：`synthetic_latency_budget_ready_needs_field_timestamps`。
  - latency_readiness_score：0.443。
  - latency_budget_violation_rate：0.200。
  - minimum_evidence_margin_min：-31.0。
  - minimum_action_margin_min：43.0。
  - release_gate_can_use_latency_budget：False。
  - 当前违约场景：`matrix_shock`，慢证据延迟 115 min，循环时间信用 84 min，证据余量 -31 min。
  - 生成：`deliverables/grey_box_dynamic_latency.md`。
  - 生成：`outputs/agent40_grey_box_dynamic_latency/agent40_report.md`。
  - 生成：`outputs/grey_box_dynamic_latency/latency_budget_metrics.json`。
  - 结论：循环结构能为多数场景争取时间，但 `matrix_shock` 仍需快代理信号、自动预处理/切换或更长暂存窗口；当前结果只允许作为模型真实性审计，不允许作为现场自动放行依据。
- `experiments/run_agent41_matrix_shock_fast_proxy.py`：
  - fast_proxy_status：`synthetic_fast_proxy_ready_needs_field_timestamp_validation`。
  - proxy_score：0.559。
  - specificity_guard_score：0.633。
  - protective_action_margin_min：59.0。
  - original_evidence_margin_min：-31.0。
  - projected_evidence_margin_after_extension_min：14.0。
  - baseline_hold_min：35。
  - adapted_hold_min：90。
  - adapted_release_policy：`block_release_until_lab_and_field_conformal_calibration`。
  - 生成：`deliverables/matrix_shock_fast_proxy_control.md`。
  - 生成：`outputs/agent41_matrix_shock_fast_proxy/agent41_report.md`。
  - 生成：`outputs/matrix_shock_fast_proxy/fast_proxy_metrics.json`。
  - 结论：快代理把慢证据问题转化为提前保护问题，但不解决自动放行；下一步必须用现场 timestamped replay 校准 precision、recall、提前量和误触发成本。
- `experiments/run_agent42_timestamped_campaign_replay.py`：
  - timestamped_replay_status：`synthetic_timestamp_schema_ready_needs_field_replay`。
  - timestamped_replay_score：0.94。
  - timestamp_coverage：1.0。
  - proxy_label_count：12。
  - proxy_precision：1.0。
  - proxy_recall：1.0。
  - mean_protective_action_lead_time_min：84.0。
  - p90_lab_turnaround_min：80.0。
  - p90_actuator_latency_min：10.0。
  - can_calibrate_fast_proxy：False。
  - can_write_to_protective_control：False。
  - 生成：`deliverables/timestamped_campaign_replay_schema.md`。
  - 生成：`outputs/agent42_timestamped_campaign_replay/agent42_report.md`。
  - 生成：`outputs/timestamped_campaign_replay/timestamped_replay_schema.json`。
  - 生成：`outputs/timestamped_campaign_replay/templates/`。
  - 生成：`outputs/timestamped_campaign_replay/synthetic_timestamped_replay/`。
  - 结论：时间戳回放把 Agent41 的快代理从 synthetic 控制修复推进到现场验证入口；下一步必须导入真实 field-labeled fast_proxy_event_log，计算 precision、recall、提前量和误触发成本。
- `experiments/run_agent43_field_replay_calibration_gate.py`：
  - field_replay_gate_status：`synthetic_replay_gate_blocked`。
  - field_replay_gate_score：0.875。
  - accepted_gates：7/8。
  - failed_gate_ids：[`G6_1_field_origin`]。
  - can_write_to_protective_control：False。
  - can_write_to_release_gate：False。
  - writeback_mode：`blocked_until_field_replay_passes_g6`。
  - 生成：`deliverables/field_replay_calibration_gate.md`。
  - 生成：`outputs/agent43_field_replay_calibration_gate/agent43_report.md`。
  - 生成：`outputs/field_replay_calibration_gate/g6_p6_gate_metrics.json`。
  - 结论：Agent43 把“真实 replay 是否足够写回快代理”变成硬门控；synthetic replay 只能联调接口，不能写入保护性控制。
- `experiments/run_agent44_field_replay_import.py`：
  - field_replay_import_status：`field_replay_import_blocked_non_field_origin`。
  - accepted_tables：4/4。
  - can_pass_to_timestamped_replay：False。
  - can_pass_to_g6：False。
  - can_write_to_protective_control：False。
  - 生成：`deliverables/field_replay_import_protocol.md`。
  - 生成：`outputs/agent44_field_replay_import/agent44_report.md`。
  - 生成：`outputs/field_replay_import/import_acceptance_metrics.json`。
  - 生成：`outputs/field_replay_import/import_schema.json`。
  - 结论：Agent44 把真实 replay 的入口前移到 provenance、field origin、CSV 字段/类型和 batch 回连验收；synthetic/sample 包不能进入 G6/P6。
- `experiments/run_agent45_field_replay_evidence_chain.py`：
  - field_replay_evidence_chain_status：`field_replay_evidence_chain_blocked_at_import`。
  - import_ready：False。
  - timestamped_replay_ready：False。
  - g6_ready：False。
  - can_emit_protective_writeback_candidate：False。
  - can_write_to_release_gate：False。
  - 生成：`deliverables/field_replay_evidence_chain.md`。
  - 生成：`outputs/agent45_field_replay_evidence_chain/agent45_report.md`。
  - 生成：`outputs/field_replay_evidence_chain/evidence_chain_metrics.json`。
  - 结论：Agent45 防止绕过 Agent44 单独采纳 Agent42/43；完整链条通过也只形成保护性写回候选。
- `experiments/run_agent46_soft_sensor_field_holdout_gate.py`：
  - soft_sensor_field_holdout_gate_status：`soft_sensor_release_gate_blocked_non_field_holdout`。
  - failed_check_ids：[`SFG0_field_holdout_origin`, `SFG5_weak_target_coverage`]。
  - can_write_to_release_gate：False。
  - can_auto_release_treated_water：False。
  - 生成：`deliverables/soft_sensor_field_holdout_gate.md`。
  - 生成：`outputs/agent46_soft_sensor_field_holdout_gate/agent46_report.md`。
  - 生成：`outputs/soft_sensor_field_holdout_gate/field_holdout_gate_metrics.json`。
  - 结论：Agent46 防止把 Agent36/Agent39 的 synthetic holdout 误写入 release gate；真实 field holdout 通过后也只形成校准候选，不直接授权自动放行。
- `experiments/run_agent47_weak_target_stratified_conformal.py`：
  - weak_target_stratified_status：`weak_target_stratified_synthetic_candidate_needs_field_holdout`。
  - 最弱目标：`matrix_interference`，coverage：0.875。
  - failed_check_ids：[`WTC0_field_holdout_origin`, `WTC2_weak_target_coverage`]。
  - can_pass_candidate_to_agent46：False。
  - can_write_to_release_gate：False。
  - 生成：`deliverables/weak_target_stratified_conformal.md`。
  - 生成：`outputs/agent47_weak_target_stratified_conformal/agent47_report.md`。
  - 生成：`outputs/weak_target_stratified_conformal/weak_target_stratified_metrics.json`。
  - 结论：总体 conformal coverage 不能替代弱目标分层 coverage；Agent47 只能生成 diagnostic candidate，必须由真实 field holdout 复核后再交给 Agent46。
- `experiments/run_agent12_operations_scheduling.py`：
  - 8 个连续批次 success_rate 1.0。
  - 验证工时占用 2.17，催化剂备件 0。
  - 调度模式为 `pause_or_limit_intake`。
  - 建议限制新批次进水、增加旁路快检班次、补充催化剂模块库存。
- `experiments/run_agent13_queue_planning.py`：
  - 比较 4 种队列策略。
  - 当前推荐 `high_risk_first`，queue_score 0.097。
  - 所有候选队列仍存在验证容量、campaign 总时间和催化剂库存瓶颈，说明仅靠排序不足以恢复正常进水，需要扩容或限流。
- `experiments/run_agent14_resource_expansion.py`：
  - 推荐 `full_resource_recovery`，intervention_score 1.0。
  - 验证工时占用从 1.406 降到 0.574。
  - 时间预算占用从 1.188 降到 0.864。
  - 剩余瓶颈为空。
- `experiments/run_agent15_long_term_economics.py`：
  - 推荐 `full_recovery_program`，program_score 0.651。
  - 服务水平 0.723，多 campaign 成本指数 5.836。
  - 预算压力 1.39，提前期风险 0.53。
  - 剩余瓶颈为空，但需要分阶段预算、过渡期限流、错峰进水和验证优先级调度。
  - `balanced_recovery_program` 成本指数 3.468，但仍残留 `campaign_time_budget` 瓶颈。
- `experiments/run_agent16_phased_implementation.py`：
  - 围绕 `full_recovery_program` 形成 4 个阶段。
  - 第 0 个 campaign 限流到 50%。
  - 第 1 个 campaign 先补验证能力和氧化剂库存。
  - 第 1-2 个 campaign 锁定催化剂备件采购。
  - 第 2 个 campaign 进入完整能力验证。
  - execution_score 0.657，schedule_risk 0.434，implementation_readiness 0.668。
- `experiments/run_agent17_implementation_stress_test.py`：
  - 最坏情景为 `combined_delay_high_intake`。
  - scenario_risk 0.356，robustness_score 0.86。
  - 保护性过渡期进水上限 0.45。
  - latest_safe_ready_campaign 为 3。
  - 备用动作包括外部催化剂调拨/备用供应商询价、外包低价值背景验证、预算拆分、拒绝新增高风险进水。
- `experiments/run_agent18_adaptive_portfolio.py`：
  - 推荐 `resilience_bridge_portfolio`，portfolio_score 0.724。
  - 覆盖验收失败、预算慢批、催化剂延迟、高进水压力和验证爬坡延迟。
  - expected_risk_reduction 0.32，residual_risk 0.036。
  - 过渡期保护性进水比例 0.45。
  - 预算释放顺序：外包低价值验证 -> 催化剂备用供应商 -> 验证能力批复 -> 催化剂库存批复 -> 氧化剂库存批复。
- `experiments/run_agent19_online_project_control.py`：
  - campaign 0：`replan_and_protect`，rolling_risk 0.368，进水比例 0.45，下一预算项 `验证能力批复`。
  - campaign 1：`steady_monitoring`，rolling_risk 0.0，stable_streak 1，进水比例 0.53。
  - campaign 2：`controlled_ramp_up`，rolling_risk 0.0，stable_streak 2，进水比例 0.68。
  - 当前预算项：本轮无需新增预算项，保持滚动复核。
- `experiments/run_agent20_campaign_telemetry.py`：
  - 从真实 8 批高风险 campaign records 生成 3 个滚动更新。
  - 最新 update success_rate 1.0，但 validation_staff_usage 1.406，time_budget_usage 1.188。
  - 最新瓶颈为 `validation_capacity`、`campaign_time_budget`、`catalyst_inventory`。
  - 接入在线项目控制后，当前模式为 `replan_and_protect`，下一轮进水比例 0.35。
  - 下一动作是重跑队列规划、资源扩容、压力测试和项目组合，而不是继续恢复进水。
- `experiments/run_agent21_replanning_orchestrator.py`：
  - 自动重规划已执行。
  - 队列策略：`high_risk_first`。
  - 资源干预：`full_resource_recovery`。
  - 长期项目：`full_recovery_program`。
  - 备用项目包：`resilience_bridge_portfolio`。
  - 重规划后保护性进水比例：0.45。
  - 预算顺序：外包低价值验证 -> 催化剂备用供应商 -> 验证能力批复 -> 催化剂库存批复 -> 氧化剂库存批复。
- `experiments/run_agent22_control_baseline_update.py`：
  - 已写回 `baseline_v1_replan`。
  - 默认队列策略：`high_risk_first`。
  - 默认项目包：`resilience_bridge_portfolio`。
  - 保护性进水比例：0.45。
  - 写回预算项 5 个，写回规则包括连续稳定验收恢复进水、验收失败触发重规划、ready campaign 滑移触发重规划。
- `experiments/run_agent23_post_replan_replay.py`：
  - verdict：`validated`，impact_score 0.864。
  - 验证工时占用从 1.406 降到 0.337。
  - 时间预算占用从 1.188 降到 0.755。
  - 移除 `campaign_time_budget`、`catalyst_inventory`、`validation_capacity` 三个瓶颈。
  - 剩余瓶颈为空。
  - 吞吐比例为 0.5，下一轮只接纳 4/8 批并继续滚动遥测。
- `experiments/run_agent3_mechanism.py`：
  - 输出知识库命中列表。
  - 当前传感故障样例命中 `kb_sensor_limited_release_evidence`，用于解释低成本代理信号不足时不能直接自动放行。

## 鲁棒性结果

- `sensor_faults`：mean_steps 2.3，mean_elapsed_min 66.8，mean_cost 0.496，mean_energy 0.245。
- `oxidant_limitation`：mean_steps 3.067，mean_elapsed_min 177.2，mean_cost 1.166，mean_energy 0.711。
- `reaction_time_insufficient`：mean_steps 3.067，mean_elapsed_min 65.3，mean_cost 0.235，mean_energy 0.637。
- `catalyst_deactivation`：mean_steps 3.067，mean_elapsed_min 314.6，mean_cost 1.957，mean_energy 0.764。
- `matrix_shock`：mean_steps 2.1，mean_elapsed_min 132.6，mean_cost 0.709，mean_energy 0.557。

## 最新关键迭代

- 闭环过程模型已真实读取 `recycle_ratio`、`extra_retention_min`、`dose_factor` 和 `hold_min`。
- 氧化剂不足场景经加药-回流联合策略优化后，30 seed 平均步数从 4.9 降到 2.733。
- 反应时间不足场景经动态回流参数接入后，30 seed 平均步数降到 2.8。
- 高基质冲击场景动作顺序稳定为 `switch_or_pretreat` -> `recirculate`。
- 副产物风险已贯穿 Agent 2-7：软传感估计、机理解释、故障诊断、加药抑制、成本惩罚和放行安全门。
- 离线快检已进入过程反馈：`hold_for_validation` 会产生带延迟和误差的 `offline_residual_proxy`，Agent 2 会按置信度吸收该慢证据。
- 催化剂失活已成为独立闭环：`catalyst_deactivation` 场景触发 `regenerate_catalyst` -> `recirculate`，过程状态真实提高 `catalyst_activity` 后再进入下一轮软传感。
- 低成本传感敏感性已验证：可以用更慢采样和更长观测窗口降低运行负担，但不能随意删除关键传感通道。
- 结构化知识库已进入 Agent 3-4：知识条目能解释为什么某类信号组合对应某类污染物/材料机制，并作为故障证据保留下游可查。
- 知识库动作偏置已进入 Agent 5：传感证据不足会提高旁路验证和传感校准评分、压低放行评分；氧化剂不足、基质干扰、催化剂失活等条目会对相应动作提供小幅可解释偏置。
- 知识库成本安全修正已进入 Agent 6：正向知识偏置会提高安全收益、降低风险成本；负向知识偏置会降低安全收益、提高风险成本。
- 统一策略目标已进入 Agent 6-7：`objective_score` 把成本、时间、能耗、安全、误放行、副产物和知识一致性合成为最终仲裁可用的工程目标，避免单一净收益或单一控制分数主导动作。
- 策略目标模板已进入 Agent 6：可按安全优先、成本优先、应急响应等研究场景切换权重。
- 策略目标自动选择已进入主链路：`StrategyProfileAgent` 会把 profile 传给成本安全 Agent，避免只能手动指定。
- 传感器经济性已进入敏感性分析 Agent：完整传感但慢采样的 `full_36min_3min` 仍保持最佳，但综合评分因采购和维护成本从 0.908 修正为 0.882。
- 敏感性实验缓存已进入敏感性分析 Agent：后续修改价格表、排序权重或文档时可快速复用闭环 episode 结果。
- 采样噪声已进入敏感性分析 Agent：带噪声刷新后 `full_36min_3min` 仍成功率 1.0，说明当前软传感和安全门对合理低成本测量扰动有容忍度。
- 催化剂生命周期已进入主链路：过程状态显式跟踪寿命、年龄和再生次数；`CatalystLifecycleAgent` 将催化剂失活拆成“可再生”和“应更换”两类工程动作。
- 专项生命周期模拟显示：寿命尚可时最终动作为 `regenerate_catalyst` -> `recirculate`；寿命耗尽时最终动作为 `replace_catalyst` -> `recirculate`。
- 旁路验证规划已进入主链路：`ValidationPlanningAgent` 会把放行证据不足、副产物风险、基质冲击等问题转化为具体慢证据目标，导致部分场景耗时上升，但更贴近“用循环结构换低成本传感可信度”的研究目的。
- 多批次运行调度已进入原型：`run_multibatch_campaign` 会连续执行多个闭环 batch 并保留催化剂状态，`OperationsSchedulingAgent` 能识别单批次看不到的验证工时过载、备件耗尽和限流需求。
- 批次队列规划已进入原型：`QueuePlanningAgent` 能比较不同污染场景顺序，并识别“换顺序只能减轻但不能消除瓶颈”的情况。
- 资源扩容对比已进入原型：`ResourceExpansionAgent` 能比较单项扩容与组合干预，并证明单独补某一项资源不足以解除当前 campaign 的复合瓶颈。
- 长期经济性与提前期已进入原型：`LongTermEconomicsAgent` 能把完整恢复、均衡建设、库存优先、验证优先和最低响应放入多 campaign 预算与提前期框架中比较。
- 分阶段实施已进入原型：`PhasedImplementationAgent` 能把完整恢复方案拆成过渡控制、验证/氧化剂爬坡、催化剂采购锁定和集成试运行，并给出库存、班次和进水策略。
- 实施压力测试已进入原型：`ImplementationStressTestAgent` 能检验分阶段计划在现实偏差下是否仍可执行，并给出自动升级阈值和备用路径。
- 自适应项目组合已进入原型：`AdaptivePortfolioAgent` 能将压力测试信号转成备用项目包、预算释放顺序和保护性进水策略。
- 在线项目控制已进入原型：`OnlineProjectControlAgent` 能根据 campaign 后状态滚动调整进水比例、预算项和重规划状态。
- Campaign 遥测桥接已进入原型：`CampaignTelemetryAgent` 能把真实多批次运行记录转成在线项目控制输入，使项目控制由运行数据驱动。
- 自动重规划编排已进入原型：`ReplanningOrchestratorAgent` 能把 replan_required 从提示变成自动重跑后半链的闭环动作。
- 控制基线写回已进入原型：`ControlBaselineUpdateAgent` 能把自动重规划结果写回下一轮在线控制配置。
- 重规划后回放验证已进入原型：`PostReplanReplayAgent` 能检查写回基线是否实际降低瓶颈，并显式记录吞吐代价。
- 恢复放量爬坡验证已进入原型：`RecoveryRampAgent` 能在回放验证通过后逐步恢复进水，并识别当前安全上限和重新出现的瓶颈。
- 时间预算恢复方案已进入原型：`TimeBudgetRecoveryAgent` 能把时间瓶颈转化为候选工程动作，并优先选择低队列扰动的可执行恢复策略。
- 恢复策略写回已进入原型：`RecoveryStrategyWritebackAgent` 能把时间预算恢复方案写入在线控制基线，形成目标、回退和复核规则。
- 恢复策略执行回放已进入原型：`RecoveryExecutionReplayAgent` 能验证写回策略在下一轮 campaign 投影中是否真正解除时间瓶颈。
- 恢复在线控制接入已进入原型：`RecoveryOnlineControlAgent` 能把恢复执行回放结果转成在线控制状态，明确维持、回退或重规划。
- 项目综合总览已进入原型：`ProjectSynthesisAgent` 能把 28-agent 执行链整理为可汇报的研究平台结构、证据链和真实数据校准路线。
- 真实数据接口已进入原型：`FieldDataInterfaceAgent` 能把真实校准路线落成可检查 schema、CSV 模板和样例数据包，并明确 synthetic 不等于现场实证。
- 成果整理已进入原型：`DeliverableOrganizationAgent` 能把项目成果整理成执行摘要、PPT 提纲、关键数值表、成果索引和实证校准任务板。
- 图表与汇报素材已进入原型：`PresentationAssetAgent` 能把整理成果转成 slide 结构、Mermaid 图表、讲述脚本和项目书章节骨架。
- 正式 PPTX 已冻结为 Agent33 快照，后续不再在呈现层反复打磨，除非明确提出视觉修改。
- 实证校准门控已进入原型：`FieldCalibrationGateAgent` 能把真实数据接口推进为现场校准协议、基础 G0-G5 验收门、P0-P5 参数写回顺序和 R1-R4 运行手册；Agent43 后补充 G6/P6 时间戳回放与快代理现场校准门。
- 基质冲击快代理已进入控制层：`MatrixShockFastProxyAgent` 能用 EC、浊度、UV254、pH 和 ORP 在慢离线证据回来前触发保护性预处理/切换，但不能授权自动放行。
- 现场时间戳回放接口已进入原型：`TimestampedCampaignReplayAgent` 能把 sensor、lab、operation 和 fast_proxy_event_log 放到同一 batch 时间轴，形成快代理 precision/recall、提前量和误触发成本的现场校准入口。
- 现场回放校准门控已进入原型：`FieldReplayCalibrationGateAgent` 能把 Agent42 replay 指标转成 G6/P6 写回门，只有真实 field-labeled replay 达标时才允许写入 matrix_shock 保护性控制，自动放行门始终禁止。
- 现场 replay 包导入门已进入原型：`FieldReplayImportAgent` 能读取 metadata.json 和四张 replay CSV，先挡住 synthetic/sample 包，并把真实包整理成 Agent42 可消费的 normalized datasets。
- 现场 replay 证据链已进入原型：`FieldReplayEvidenceChainAgent` 能把 Agent44、Agent42 和 Agent43 串成不可绕过的校准链，只在完整链条通过后形成保护性写回候选。
- 软传感 field holdout 放行门控已进入原型：`SoftSensorFieldHoldoutGateAgent` 能把 Agent36 和 Agent39 的 synthetic holdout 明确挡在 release gate 外，只有真实 field holdout 全门控通过后才形成软传感校准候选。

以下 dated 小节保留当轮迭代记录，里面的测试数量、缓存版本和耗时是历史快照；最新状态以上方“当前验证”和“鲁棒性结果”为准。

## 2026-05-31 敏感性分析 Agent 传感器经济性模型迭代

本轮完成了低成本传感配置的工程成本细化：

- 新增 `sensor_economics.py`。
- 为 `pH`、`ORP_mV`、`EC_uScm`、`turbidity_NTU`、`temp_C`、`flow_Lmin`、`UV254_abs` 建立工程默认经济性表。
- 每个传感器包含采购成本、月维护成本和周校准工时。
- `compute_sensor_economics` 会根据禁用传感器、观测窗口和采样间隔计算：
  - `purchase_cost_cny`
  - `annual_maintenance_cny`
  - `calibration_hours_per_month`
  - `samples_per_window`
  - `sampling_load_index`
  - `engineering_cost_index`
- 敏感性分析 Agent 把这些字段写入设计排序结果，并在推荐文本中说明工程成本指数和月校准负担。

验证：

- `pytest -q`：57 passed。
- `run_design_sensitivity.py` 推荐仍为 `full_36min_3min`。
- 推荐配置平均成功率 1.0；在后续策略 profile 接入后，当前平均总耗时为 119.8 min。
- 综合评分从 0.908 调整为 0.882，原因是完整传感的采购和维护成本被更真实地纳入评价。
- 极简配置虽然工程成本指数更低，但成功率为 0，仍不会被推荐。
- `run_design_sensitivity.py --force-refresh` 会重算缓存；普通运行命中当前 v4 缓存后约 0.167 s。

## 2026-05-31 敏感性分析 Agent 采样噪声模型迭代

本轮完成了低成本传感配置的测量扰动建模：

- `run_closed_loop_episode` 新增 `sensor_noise_multiplier`。
- `_apply_sensor_design` 在抽样和禁用传感器之外，可对保留传感器注入确定性测量噪声。
- 噪声模型按传感器类型设置基础扰动幅度，例如 pH、ORP、EC、浊度、流量和 UV254 各自不同。
- 噪声是确定性的：同一场景、同一时间戳、同一配置会得到相同扰动，便于测试和复现实验。
- `evaluate_closed_loop_robustness` 和 `run_design_sensitivity.py` 已传递 `sensor_noise_multiplier`。
- 设计敏感性缓存版本随后升级为 `design_sensitivity_v4_strategy_profile`，避免误用无策略 profile 旧缓存。

验证：

- `pytest -q`：57 passed。
- 带噪声 `run_design_sensitivity.py --force-refresh` 后推荐仍为 `full_36min_3min`。
- 推荐配置噪声倍率 0.75，平均成功率 1.0，当前平均总耗时 119.8 min，综合评分 0.882。
- 普通运行命中 v4 缓存后约 0.167 s。

## 2026-05-31 策略目标场景模板迭代

本轮完成了统一策略目标的场景模板化：

- 新增 `STRATEGY_OBJECTIVE_PROFILES`。
- 新增 `get_strategy_objective_weights`。
- 当前模板包括：
  - `balanced`：默认平衡模式。
  - `safety_first`：提高误放行风险、一般风险和副产物风险权重。
  - `cost_first`：提高处理成本、时间和能耗权重，但仍保留误放行惩罚。
  - `emergency_response`：降低时间惩罚，提高控制优先级，适合应急旁路或快速响应场景。
- `CostSafetyAgent` 支持 `objective_profile`，同时保留自定义 `objective_weights`。
- 输出新增 `strategy_objective_profile`，便于审计当前使用的决策口径。

验证：

- `pytest -q`：59 passed。
- 多场景扫查保持默认 `balanced` 行为稳定：
  - `clean_release`：`release`。
  - `sensor_faults`：`inspect_hydraulics` -> `calibrate_sensors` -> `hold_for_validation` -> `recirculate`。
  - `oxidant_limitation`：`dose_oxidant` -> `recirculate`。
  - `reaction_time_insufficient`：`recirculate`。
  - `catalyst_deactivation`：`regenerate_catalyst` -> `recirculate`。
  - `matrix_shock`：`switch_or_pretreat` -> `recirculate`。

## 2026-05-31 策略目标自动选择 Agent 迭代

本轮完成了策略模板从“可选参数”到“自动进入主链路”的升级：

- 新增 `StrategyProfileAgent`。
- 输入为软传感状态和故障诊断结果。
- 输出 `selected_profile`、`profile_scores`、选择依据和状态证据。
- `pipeline.run_agent_chain` 已在控制策略之后、成本安全之前调用该 Agent。
- `CostSafetyAgent` 读取自动选择的 profile，再计算 `objective_score`。
- `run_scenario_sweep.py` 和 `run_full_agent_chain.py` 已纳入策略 profile 报告。

验证：

- `pytest -q`：63 passed。
- 多场景 profile 结果：
  - `clean_release`：`cost_first`。
  - `sensor_faults`：`safety_first`。
  - `oxidant_limitation`：`emergency_response`。
  - `reaction_time_insufficient`：`balanced`。
  - `catalyst_deactivation`：`safety_first`。
  - `matrix_shock`：`safety_first`。
- 最终动作链保持稳定；其中催化剂失活场景更保守，平均步数上升到 2.9，但 30 seed 成功率仍为 1.0。

## 2026-05-31 统一策略优化目标迭代

本轮完成了从“成本安全评分”到“工程策略目标”的升级：

- 新增 `StrategyObjectiveWeights` 和 `compute_strategy_objective`。
- 默认目标函数包含控制优先级、安全收益、经济成本、等待时间、能耗、风险成本、误放行风险、副产物/过氧化压力、人工复核代价和知识库动作一致性。
- 误放行风险默认权重设为 0.30，高于一般成本项，避免高原始分数的放行动作压过残留风险或传感/水力不确定性。
- Agent 6 输出 `objective_score`、收益项、惩罚项、误放行风险和副产物压力。
- Agent 7 的动作筛选、排序和置信度计算改为优先使用 `objective_score`。
- `net_score` 保留为解释指标，用于说明动作的传统成本安全净收益。

验证：

- `pytest -q`：52 passed。
- 多场景扫查保持稳定：
  - `clean_release`：`release`。
  - `sensor_faults`：`inspect_hydraulics` -> `calibrate_sensors` -> `hold_for_validation` -> `recirculate`。
  - `oxidant_limitation`：`dose_oxidant` -> `recirculate`。
  - `reaction_time_insufficient`：`recirculate`。
  - `catalyst_deactivation`：`regenerate_catalyst` -> `recirculate`。
  - `matrix_shock`：`switch_or_pretreat` -> `recirculate`。
- 闭环 episode 仍在 2-3 步内收敛。
- 150 条鲁棒性 episode 全部成功，失败样本 0。
- 低成本传感敏感性推荐保持 `full_36min_3min`，平均成功率 1.0，平均总耗时 111.2 min；加入传感器经济性后综合评分为 0.882。

## 下一轮重点

1. 按 `deliverables/field_replay_import_protocol.md` 导入带 metadata.json 的真实 sensor、lab、operation 和 fast_proxy_event_log CSV 包，先通过 Agent44 provenance、field origin、字段、类型和 batch 回连验收。
2. 用真实 replay 重算 matrix_shock 快代理 precision、recall、protective action lead time、lab turnaround、actuator latency 和误触发成本，并通过 Agent45 证据链汇总 Agent44 -> Agent42 -> Agent43。
3. 接入真实 field holdout 后重跑 Agent36 -> Agent39 -> Agent47 -> Agent46，先修复弱目标分层 coverage，再由软传感 field holdout 放行门控决定是否形成 release gate 校准候选。
4. 继续校准时间预算、验证错峰收益、fallback triggers 和 field-supported KG edges。

## 2026-05-31 副产物风险与过量氧化剂惩罚迭代

本轮已完成副产物风险链路：

- Agent 2 新增 `byproduct_risk`，综合氧化剂余量、基质干扰、pH 偏离、处理完成度和循环暴露时间估计副产物或过氧化风险。
- Agent 3 新增 `byproduct_risk` 机理规则。
- Agent 4 新增 `byproduct_or_overoxidation_risk` 故障模式。
- Agent 5 在副产物风险高时降低 `dose_oxidant` 评分与 `dose_factor`，并把旁路验证范围扩展到余氧化剂/副产物快检。
- Agent 6 在副产物风险高或加药系数过大时提高加药风险成本。
- Agent 7 新增 `byproduct_risk_gate`，副产物风险高于 0.65 时禁止自动放行。

验证：

- `pytest -q`：33 passed。
- 多场景扫查保持稳定。
- 闭环 episode 保持：sensor faults 2 步，oxidant limitation 3 步，reaction time insufficient 3 步，matrix shock 2 步。
- 120 条鲁棒性 episode 全部成功，失败样本 0。

## 2026-05-31 离线快检延迟与检测误差迭代

本轮已完成旁路/离线快检慢证据建模：

- `hold_for_validation` 现在支持 `validation_delay_min`。
- 过程状态新增 `offline_residual_proxy`、`offline_validation_confidence`、`offline_validation_age_min`、`offline_validation_error`。
- 旁路快检带有确定性误差项，并随时间衰减置信度。
- 下一轮传感流会携带 `offline_residual_proxy` 等慢证据。
- Agent 2 会读取离线快检慢证据，并按置信度修正 `pollutant_residual_risk`。

验证：

- 新增 `test_offline_validation.py`。
- `pytest -q`：35 passed。
- 闭环 episode 保持：sensor faults 2 步，oxidant limitation 3 步，reaction time insufficient 3 步，matrix shock 2 步。
- 120 条鲁棒性 episode 全部成功，失败样本 0。

## 2026-05-31 催化剂失活-再生/更换闭环迭代

本轮已完成催化剂失活链路：

- 新增 `catalyst_deactivation` 过程场景，低催化活性会导致高残留、高氧化剂余量和低反应完成度并存。
- 软传感器校正模型升级为 `rf_multioutput_v3_catalyst`，训练数据扩展到 51840 行。
- Agent 3 和 Agent 4 收紧失活判据，避免把水力停留不足、氧化剂不足或基质冲击误判为催化剂失活。
- Agent 5 新增 `regenerate_catalyst`，动态输出 `regen_intensity` 和 `downtime_min`。
- Agent 6 新增催化剂再生/更换成本安全评价，对真实低活性提高安全收益，对活性足够时提高无效再生成本。
- Agent 7 增加再生动作约束：催化活性过高时禁止无效再生，低催化活性下再生/更换先于回流。
- 过程动力学层会在执行再生动作后真实提升 `catalyst_activity`，并计入停机时间、成本和能耗。

验证：

- 新增控制、成本安全、仲裁、闭环、场景扫查和鲁棒性测试。
- `pytest -q`：40 passed。
- 多场景扫查新增 `catalyst_deactivation`：最终动作为 `regenerate_catalyst` -> `recirculate`。
- 闭环 episode：catalyst deactivation 2 步收敛。
- 150 条鲁棒性 episode 全部成功，失败样本 0。

## 2026-05-31 知识库动作偏置接入 Agent 5 迭代

本轮已完成知识库从“解释证据”到“控制偏置”的第一步：

- Agent 5 读取 Agent 4 传递的 `knowledge_matches`。
- 聚合各知识条目的 `action_biases`，形成 `knowledge_action_biases`。
- 将动作偏置加到对应动作评分中，并把 `knowledge_action_bias` 写入动作证据。
- 示例：`kb_sensor_limited_release_evidence` 会提高 `hold_for_validation` 和 `calibrate_sensors`，并压低 `release`。

验证：

- 新增 Agent 5 知识动作偏置测试。
- `pytest -q`：47 passed。
- 多场景扫查保持主动作链稳定。
- `sensor_faults` 新增 `hold_for_validation`，因为低成本传感证据不足时旁路验证成为更合理的安全动作。
- 150 条鲁棒性 episode 全部成功，失败样本 0。

## 2026-05-31 知识库成本安全修正接入 Agent 6 迭代

本轮已完成知识库从“控制偏置”到“成本安全评价”的延伸：

- Agent 6 读取动作证据中的 `knowledge_action_bias`。
- 正向知识偏置会提高 `safety_gain`、降低 `risk_cost`，并略微降低时间成本。
- 负向知识偏置会降低 `safety_gain`、提高 `risk_cost`，并略微提高时间成本。
- 输出新增 `knowledge_cost_adjustment`，保留安全收益、风险成本、时间成本的具体修正量。

验证：

- 新增 Agent 6 知识成本修正测试。
- `pytest -q`：48 passed。
- 多场景扫查保持主动作链稳定。
- `sensor_faults` 场景因传感证据不足，旁路验证的成本安全净收益提高；鲁棒性仍保持 success_rate 1.0。
- 150 条鲁棒性 episode 全部成功，失败样本 0。

## 2026-05-31 低成本传感-循环窗口敏感性迭代

本轮已完成第 8 个 Agent：

- 新增 `SensitivityAnalysisAgent`，对候选传感/循环设计进行效用排序。
- `run_closed_loop_episode` 支持 `sampling_interval_min` 和 `disabled_sensors`，可模拟慢采样与不安装某些传感器。
- 软传感器和校正模型增加整列缺失兜底：缺失通道用工程中值填充，同时由数据质控降低对应通道可信度。
- 新增 `experiments/run_design_sensitivity.py`，比较完整传感、慢采样、取消 UV254、核心配置和极简配置。

验证：

- 新增敏感性 Agent 测试和稀疏传感安全降级测试。
- `pytest -q`：42 passed。
- 最优方案为 `full_36min_3min`：完整低成本传感、36 min 观测窗口、3 min 采样间隔，平均成功率 1.0，平均总耗时 109.6 min。
- `full_24min_1min` 作为稳健备选，成功率 1.0，但平均总耗时和综合效用不如 3 min 采样方案。
- 取消 `UV254_abs` 后系统不会误放行，但会保守退化，当前不推荐作为默认低成本配置。

## 2026-05-31 污染物-材料-机制知识库迭代

本轮已完成 Agent 3 的知识库增强：

- 新增结构化 `KNOWLEDGE_BASE`，每个条目包含污染物场景、材料/工艺族、机制标签、信号条件、支持规则、动作倾向和行动提示。
- 当前知识条目覆盖：
  - 高盐/高 COD 基质抑制高级氧化。
  - 高负荷还原性或难降解有机物导致氧化剂不足。
  - 催化剂活性位污染或堵塞。
  - 循环窗口为慢检测和软传感复估争取时间。
  - 强氧化体系下副产物/过氧化风险。
  - 低成本传感证据不足导致不能自动放行。
- Agent 3 查询知识库后输出 `knowledge_matches`，并将匹配条目写入机理假设的 `knowledge_support`。
- Agent 4 接收知识库证据，并把它写入相应故障模式的证据字段。

验证：

- 新增知识库直接查询测试、Agent 3 知识支持测试、Agent 4 知识证据传递测试。
- `pytest -q`：46 passed。
- 多场景扫查保持主动作链稳定：
  - `oxidant_limitation`：`dose_oxidant` -> `recirculate`。
  - `reaction_time_insufficient`：`recirculate`。
  - `catalyst_deactivation`：`regenerate_catalyst` -> `recirculate`。
  - `matrix_shock`：`switch_or_pretreat` -> `recirculate`。
- 150 条鲁棒性 episode 全部成功，失败样本 0。

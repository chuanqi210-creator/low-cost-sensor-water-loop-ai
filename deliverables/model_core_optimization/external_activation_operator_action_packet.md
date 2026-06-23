# External Activation Operator Action Packet

## 定位

该包把当前最高优先外部动作压成一个可执行清单：填写 focused catalyst response、设置 `FOCUSED_CATALYST_RESPONSE_PATH`、运行 focused merge，再在预检通过后回填 `FIELD_ACTIVATION_RESPONSE_PATH`。它只是操作交接，不生成现场证据。

## Current Action

- packet_id: `R8u130_external_activation_operator_action_packet`
- packet_status: `operator_packet_waiting_for_focused_catalyst_response`
- target_hidden_state: `catalyst_activity`
- source_env_var: `FOCUSED_CATALYST_RESPONSE_PATH`
- target_full_response_env_var: `FIELD_ACTIVATION_RESPONSE_PATH`
- focused_template_path: `outputs/catalyst_response_submission_kit/focused_catalyst_response_template.json`
- focused_schema_path: `outputs/catalyst_response_submission_kit/focused_catalyst_response_schema.json`
- focused_merge_plan_path: `outputs/catalyst_response_submission_kit/focused_to_full_response_merge_plan.json`
- expected_focused_response_row_count: `6`
- template_evidence_row_count: `6`
- minimum_matched_batch_count: `3`
- focused_merge_preflight_status: `focused_catalyst_response_merge_waiting_for_FOCUSED_CATALYST_RESPONSE_PATH`
- focused_candidate_availability_status: `candidate_not_submittable_waiting_for_FOCUSED_CATALYST_RESPONSE_PATH`
- focused_candidate_self_declared_submit_ready: `False`
- focused_candidate_operator_packet_submit_ready: `False`
- focused_repair_work_order_status: `focused_catalyst_response_repair_work_order_waiting_for_external_response`
- focused_repair_next_operator_action: `fill_outputs/catalyst_response_submission_kit/focused_catalyst_response_template.json_with_real_field_values_then_set_FOCUSED_CATALYST_RESPONSE_PATH`
- packet_next_operator_action: `fill_outputs/catalyst_response_submission_kit/focused_catalyst_response_template.json_with_real_field_values_then_set_FOCUSED_CATALYST_RESPONSE_PATH`
- next_operator_action: `fill_outputs/catalyst_response_submission_kit/focused_catalyst_response_template.json_with_real_field_values_then_set_FOCUSED_CATALYST_RESPONSE_PATH`
- operator_packet_boundary_pass: `True`

## Commands

- `fill outputs/catalyst_response_submission_kit/focused_catalyst_response_template.json with real field values`
- `export FOCUSED_CATALYST_RESPONSE_PATH=/absolute/path/to/filled_focused_response.json`
- `.venv/bin/python experiments/run_focused_catalyst_response_merge.py`

## Operator Steps

| order | step | action | condition |
| --- | --- | --- | --- |
| 1 | `OP1_FILL_FOCUSED_TEMPLATE` | `fill_focused_catalyst_response_template_with_real_field_values` |  |
| 2 | `OP2_SET_FOCUSED_ENV` | `set_FOCUSED_CATALYST_RESPONSE_PATH` |  |
| 3 | `OP3_RUN_FOCUSED_MERGE` | `run_focused_merge_preflight` |  |
| 4 | `OP4_SET_FULL_RESPONSE_CANDIDATE` | `set_FIELD_ACTIVATION_RESPONSE_PATH_if_focused_merge_ready` | only after OP3 ready status passes |
| 5 | `OP5_RERUN_MAIN_GATES` | `rerun_field_activation_and_agent50` | only after FIELD_ACTIVATION_RESPONSE_PATH points to the merged candidate |

## Boundary Checks

| check | pass | detail |
| --- | --- | --- |
| `template_has_rows` | `True` | template row count = 6 |
| `minimum_batch_count_declared` | `True` | minimum shared batch count = 3 |
| `no_write_confirmation_fields_present` | `True` | each template row must expose no_write_boundary_confirmed |
| `template_rows_are_not_field_evidence` | `True` | template TODO rows are collection instructions only, not field evidence |

## No-Write Boundary

Only use this file as FIELD_ACTIVATION_RESPONSE_PATH when can_submit_candidate_as_FIELD_ACTIVATION_RESPONSE_PATH is true and downstream full response, field package, replay, holdout, operator-review, actuator and release gates still pass. If false, this file is a diagnostic artifact and must not be routed as field evidence.

This packet only tells an operator how to fill and validate the focused catalyst response. It cannot generate field evidence, resume the model chain, write actuator policy, write a release gate, relax Agent49 catalyst guardrails, pass Agent51 holdout or emit a field-supported claim.

## Rejection Boundaries

- Reject template/sample/synthetic rows as field evidence.
- Reject rows with TODO/template markers in required evidence payloads.
- Reject responses that do not use at least the minimum shared real batch_id count.
- Reject responses whose no_write_boundary_confirmed is not true on every row.
- Reject any shortcut that skips focused merge, full response preflight, materialized package preflight, replay/holdout or operator review.

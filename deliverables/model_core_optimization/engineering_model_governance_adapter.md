# Engineering Model Governance Adapter

## Purpose

This adapter borrows only the low-friction governance rules that strengthen the
low-cost circular water-treatment grey-box control model. It is not a second
project protocol and it must not become a competing source of truth.

The source of truth remains the executable model chain: code, manifest, gate
JSON, preflight outputs, real external packages, tests and verification logs.

## Absorbed Rules

1. `current_basis` and `not_current_basis` must be explicit. Real field packages,
human review responses, current manifest pointers and passed preflight outputs
can enter `current_basis`. Old drafts, generated reports, templates, synthetic
samples, TODO rows and header-only CSV files stay outside `current_basis`.
2. Stage routing stays compact. The project uses these route events:
   `continue_current_micro_loop`, `route_back`, `blocked`,
   `ask_user_or_operator`, `external_activation_wait` and `execute_preflight`.
3. `Plan` is for current multi-step execution. The global `Goal` is reserved for
the long-lived system mission and must not be owned, completed or blocked by a
subagent.
4. Human-facing outputs and machine-facing outputs stay separated. Human-facing
updates summarize the decision, evidence, risk, verification and next route.
Machine-facing artifacts carry structured fields in manifest, gate JSON,
preflight packages, route boards and operator packets.
5. `manual_action_required` is only for real human or field actions: submitting
field packages, filling external rows, performing human nonlegal review, making
legal or patent decisions, granting access, or authorizing field execution.
Work that can be scanned, tested, generated or preflighted locally stays with
the model pipeline.
6. Skill, tool and external-method searches must serve a concrete model gap such
as sparse placement, missingness replay, grey-box calibration, formal search or
field replay. They are not used to justify unrelated framework growth.
7. Subagents are used only for bounded read-only audits, source checks,
independent implementation slices or verification. The main chain owns
integration, evidence upgrades, user preference interpretation and execution
authorization.
8. Every new rule, agent, schema, gate or route must pass an anti-bloat gate:
   trigger signal, observable behavior, required evidence or check, route-back
   condition, user-friction impact and whether it replaces, tightens or merges
   an existing rule.

## Seven-Layer Mapping

| Layer | Governance Mapping |
| --- | --- |
| Field object layer | Mark which pollutants, matrices, units, topology, catalysts, reagents and loop structures are real field objects versus templates or synthetic baselines. |
| Observation layer | Each sensor, node-modality entry, missingness pattern, delay and sampling window needs `data_origin`, time-window semantics, field contract and explicit limits. |
| State-estimation layer | Soft sensors, conformal intervals and hidden states only upgrade through evidence gates. Field holdout failure keeps them out of release gates. |
| Mechanism-evidence layer | Literature, KG edges, formal search and `source_basis` constrain hypotheses; they do not replace field mechanism validation. |
| Diagnosis-decision layer | Each action candidate must trace to observation, estimated state, mechanism evidence and review status; unresolved conflicts route through decision logs or operator review. |
| Closed-loop execution layer | Replay, SOP/SCADA mapping, operator review and execution feedback must pass before any actuator or release-gate write can become possible. |
| Verification-governance layer | Manifest, Agent50/60 gates, external action boards, preflights and no-write boundaries route and block work. They do not produce field evidence by themselves. |

## Active Micro-Loop Rule

When the project is in `external_activation_wait`, the highest-value internal
work is not to add another synthetic agent. It is to reduce scan friction and
submission ambiguity for real external packages, while keeping no-write
boundaries intact.

R8u173 is the current micro-task example:

- Trigger signal: the desktop governance protocol had already improved
  resource boundaries and machine handoff, but `recovery_integrity_score=1.0`
  was still only reported as a number, not as a recomputable trace, and the
  protocol-to-model mapping was not itself visible in the recovery audit.
- Observable behavior: `outputs/model_core_governance/governance_recovery_integrity_audit.json`
  now exposes `numeric_calculation_trace` and `protocol_adaptation`.
- Required evidence: the numeric trace recomputes the score from seven check
  scores with `mean(check_scores)`, reports `score_delta=0.0`, and preserves
  no-write / no-field-upgrade boundaries.
- Selective adoption: six rules enter the model recovery gate
  (`current_basis_contract`, `resource_boundary_contract`,
  `numeric_calculation_trace`, `dynamic_stage_handoff`,
  `micro_task_execution_check`, `subagent_orchestration_probe`); four rules
  remain backlog to avoid protocol bloat.
- Route-back if failed: if the numeric trace cannot recompute the score, the
  recovery gate adds `numeric_calculation_trace_failed` and routes to
  `repair_recovery_integrity_blockers_before_next_route`.
- User-friction impact: future agents can read manifest numeric/protocol fields
  instead of rescanning long protocol text or Markdown reports.

R8u164 is the earlier micro-task example that created this adapter:

- Trigger signal: grey-box missing tables were visible in the submission gate,
  core interface and manifest, but not in the operator-facing external package
  packet.
- Observable behavior: the operator packet now exposes `missing_table_count`,
  `missing_tables`, `submission_gap_type`, `template_dir` and validation command
  for `GREY_BOX_CALIBRATION_PACKAGE_DIR`.
- Required evidence: unit tests, refreshed JSON/Markdown artifacts and manifest
  fields.
- Route-back if failed: return to the external package readiness board and
  reject the operator packet as incomplete.
- User-friction impact: the next operator can fill the five required grey-box
  tables without scanning multiple upstream artifacts.

## Backlog, Not Immediate Work

- Full decision-log and traceability-matrix backfill.
- Full latest-board tail checking for every long-running governance file.
- Numeric calculation trace for all historical synthetic metrics.
- Dedicated subagent orchestration ledger.
- Formal source-link recency audit outside the formal-search package.

These are useful, but they should not interrupt the current external package
submission route unless a specific failure signal appears.

## Rejected Absorptions

1. Do not copy the full ten-stage protocol into this project. The model already
   has Agent50 gates, external action boards, manifests and preflight routes.
2. Do not run broad industry-best-practice scans every cycle. Search only when a
   new method family or formal review gap appears.
3. Do not add a new governance agent just to wrap Agent50 or Agent60.
4. Do not turn every small engineering patch into a user feedback gate.
5. Do not let governance Markdown become a second factual source. If a claim is
   not reflected in code, tests, gate JSON, manifest or real package outputs, it
   remains advisory.

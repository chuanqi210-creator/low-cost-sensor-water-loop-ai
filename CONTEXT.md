# Low-Cost Sensor Water Loop AI

This context describes the language of a research prototype for evidence-gated circular water-treatment control under sparse and low-cost sensing.

## Language

**Circular water-treatment loop**:
A treatment workflow where water can be held, recycled, reprocessed, or routed through additional validation before any release decision.
_Avoid_: simple one-pass treatment, generic pipeline

**Low-cost sensing**:
Sparse, noisy, delayed, or inexpensive sensor observations used as partial evidence about process state.
_Avoid_: full instrumentation, high-grade online monitoring

**Soft sensor**:
A model-derived estimate of a hidden process state that cannot be directly measured online.
_Avoid_: virtual sensor when it hides the evidence boundary

**Grey-box prior**:
A physics- or mechanism-informed constraint used to keep model estimates and action ranking auditable.
_Avoid_: black-box hint, heuristic when the prior is tied to mechanism

**Field package**:
A real external data package containing accepted sensor, lab, operation, replay, metadata, or operator rows for one or more batches.
_Avoid_: sample package, template package, synthetic package

**Evidence gate**:
A check that decides whether an artifact can be used as field evidence, simulation evidence, template scaffolding, or only an operator handoff.
_Avoid_: validation when the key distinction is evidence class

**No-write boundary**:
The project rule that generated candidates cannot directly write to actuators or release gates.
_Avoid_: safety flag, permission flag

**Replay package**:
A structured package used to replay historical or candidate state/action/evidence paths before any protective control candidate can be considered.
_Avoid_: log dump, test data

**Operator handoff**:
A human-readable or machine-readable artifact that tells an operator, reviewer, or future agent what evidence is missing and what action remains manual.
_Avoid_: autonomous command, final decision

**Template marker**:
A placeholder value that proves an artifact is a form or scaffold rather than field evidence.
_Avoid_: TODO as harmless note

**Protective control candidate**:
A conservative action proposal such as hold, recycle, extra validation, regeneration review, or unit switching that remains subject to manual review and no-write boundaries.
_Avoid_: actuator command

**Release gate**:
The final decision point for release or acceptance of treated water. This project does not write to it automatically.
_Avoid_: approval when the release semantics matter

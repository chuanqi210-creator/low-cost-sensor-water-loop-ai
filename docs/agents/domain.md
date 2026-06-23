# Domain Docs

This is a single-context repository.

## Before Exploring

Read:

- `CONTEXT.md` for the project domain language.
- `docs/adr/` when it exists and the work may touch a recorded architectural decision.
- `CODEGRAPH.md` for the shortest route into code and generated graph artifacts.
- `notes/current_status.md` for current evidence gates and iteration boundaries.

## Vocabulary Rules

Use the glossary's terms when naming issues, review findings, refactor candidates, tests, or handoff artifacts. For example, prefer `field package`, `evidence gate`, `operator handoff`, and `no-write boundary` over looser synonyms.

If a needed concept is missing from `CONTEXT.md`, treat that as a domain-modeling gap. Add a concise term only when the concept is resolved enough to be durable.

## ADR Rules

Create ADRs sparingly under `docs/adr/` only for decisions that are hard to reverse, surprising without context, and the result of a real trade-off.

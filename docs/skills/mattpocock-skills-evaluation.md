# mattpocock/skills Evaluation

Date: 2026-06-23

Source: `mattpocock/skills` on GitHub, default branch `main`, MIT licensed, 34 skill directories under `skills/`.

## Why This Was Missed Earlier

The active Codex session only exposed injected skills at startup plus tools discoverable through `tool_search`. External GitHub skill repositories are not automatically searched unless the project process explicitly asks for them. We had added generic capability discovery to `AGENTS.md`, but it did not yet require public skill-repository scouting for workflow, refactor, review, planning, or debugging work.

The correction is now in `AGENTS.md`: external skills must be searched, read, piloted, documented, and only then installed or relied on.

## Current Local State

The mattpocock skills are already present on disk under `~/.codex/skills`, including the 34 skills from `mattpocock/skills`. They were not visible in the running session's injected skill list, so Codex should be restarted before relying on automatic invocation.

## Skill Inventory And Fit

| Skill | Category | Project fit | Decision |
| --- | --- | --- | --- |
| `ask-matt` | engineering | Router for this skill family. | Useful after restart. |
| `codebase-design` | engineering | Gives deep-module vocabulary for runner/helper refactors. | Pilot/adopt. |
| `diagnosing-bugs` | engineering | Stronger bug loop than ad hoc debugging. | Pilot/adopt for failures. |
| `domain-modeling` | engineering | Fits our overloaded terms: field package, evidence gate, no-write boundary. | Pilot/adopt. |
| `grill-with-docs` | engineering | Useful before ambiguous refactors or design choices. | Conditional, user-invoked. |
| `implement` | engineering | Overlaps with existing execution workflow. | Conditional. |
| `improve-codebase-architecture` | engineering | Directly matches current desire for behavior-preserving structural optimization. | Pilot/adopt with Codex adaptation. |
| `prototype` | engineering | Useful for throwaway state/UX experiments, less central now. | Conditional. |
| `resolving-merge-conflicts` | engineering | Useful only when merge conflicts appear. | Install available, use on demand. |
| `setup-matt-pocock-skills` | engineering | Needed project config. | Applied manually here. |
| `tdd` | engineering | Valuable but overlaps with `superpowers:test-driven-development`. | Use case-by-case. |
| `to-issues` | engineering | Good for converting plans into GitHub Issues. | Adopt after label setup. |
| `to-prd` | engineering | Useful for larger project slices. | Conditional. |
| `triage` | engineering | Useful after public repo starts receiving issues/PRs. | Adopt after label setup. |
| `decision-mapping` | in-progress | Potentially useful, but not stable. | Watchlist. |
| `review` | in-progress | Interesting two-axis review, but in-progress. | Pilot only on low-risk branch. |
| `writing-beats` | in-progress | Writing workflow, not core codebase. | Low priority. |
| `writing-fragments` | in-progress | Writing workflow, not core codebase. | Low priority. |
| `writing-shape` | in-progress | Writing workflow, not core codebase. | Low priority. |
| `git-guardrails-claude-code` | misc | Claude-specific hooks; Codex already has git guardrails. | Do not adopt directly. |
| `migrate-to-shoehorn` | misc | TypeScript-specific. | Not applicable. |
| `scaffold-exercises` | misc | Course/exercise scaffolding. | Not applicable. |
| `setup-pre-commit` | misc | JS/Husky oriented; project is Python. | Not applicable without adaptation. |
| `edit-article` | personal | Article editing. | Not applicable. |
| `obsidian-vault` | personal | Personal knowledge base. | Not applicable. |
| `grill-me` | productivity | Useful for broad non-code planning. | Conditional. |
| `grilling` | productivity | Reusable interview loop behind design skills. | Conditional. |
| `handoff` | productivity | Useful across sessions; overlaps with Codex summaries. | Conditional. |
| `teach` | productivity | Learning sessions. | Low priority. |
| `writing-great-skills` | productivity | Useful if creating project-specific skills later. | Adopt when writing skills. |
| `design-an-interface` | deprecated | Deprecated. | Do not use. |
| `qa` | deprecated | Deprecated. | Do not use. |
| `request-refactor-plan` | deprecated | Deprecated. | Do not use. |
| `ubiquitous-language` | deprecated | Superseded by `domain-modeling`. | Do not use. |

## Pilot Validation

Small, low-risk pilot performed in documentation/config only:

1. Read `codebase-design`, `domain-modeling`, `improve-codebase-architecture`, `diagnosing-bugs`, `to-issues`, and `setup-matt-pocock-skills`.
2. Created root `CONTEXT.md` using `domain-modeling` rules: glossary only, no implementation spec.
3. Added `docs/agents/issue-tracker.md`, `docs/agents/triage-labels.md`, and `docs/agents/domain.md` from `setup-matt-pocock-skills` defaults, adapted to this GitHub repo.
4. Added an `AGENTS.md` Agent Skills section so future sessions know how to consume the installed skills.

This confirms the useful part for our project is not "more agents"; it is better review discipline: shared domain terms, deep-module vocabulary, issue slicing, and stronger diagnosis loops.

## Adoption Rules

- Do not install or invoke all external skills blindly.
- Prefer model-invoked discipline skills first: `codebase-design`, `domain-modeling`, `diagnosing-bugs`.
- Use user-invoked orchestration skills only when the task warrants it: `improve-codebase-architecture`, `grill-with-docs`, `to-issues`, `triage`.
- Avoid deprecated, personal, or JS-specific skills unless a future task explicitly matches them.
- Restart Codex after skill installation or major skill changes so the injected skill list refreshes.

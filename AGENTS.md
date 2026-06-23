# AGENTS.md

## Workspace Purpose

This project is the focused Codex workspace for the low-cost sensing circular water-treatment intelligent closed-loop research project.

## Defaults

- Treat this repository as the sole active project workspace. Do not rely on, mutate, or route commands through any pre-migration project directory.
- Keep code, experiments, reports, and model artifacts traceable.
- Put runtime code in `src/`, runnable experiment scripts in `experiments/`, tests in `tests/`, and publishable outputs in `deliverables/` or `outputs/`.
- Keep heavy or generated local artifacts out of Git when already ignored, especially `.venv/`, `.pytest_cache/`, `__pycache__/`, `*.pkl`, and `.worktrees/`.
- If creating worktrees, use `.worktrees/` and verify it is ignored before adding a worktree.
- Create and use this repository's own Python 3.12 virtual environment at `.venv/`; do not borrow another project's virtual environment.

## Capability Discovery

- At the start of each task, review the currently injected skills and read the `SKILL.md` for every triggered skill before acting.
- Use `tool_search` to look for useful tools, plugins, connectors, or APIs that may not already be exposed, especially for GitHub, browser, automation, document, data-analysis, and API-reference work.
- When the task is about workflow quality, refactoring, review, planning, or debugging, also search outside the currently injected skill list for reusable skills or skill repositories. Treat external skills as candidates: read their `SKILL.md`, assess overlap and risk, run a small pilot where possible, then document the adoption decision before installing or relying on them.
- When a task depends on an external API, platform rule, or recently changing capability, prefer official documentation or existing project documentation as the source of truth.
- Re-evaluate available capabilities at major phase changes: after understanding the request, before implementation, before verification or release, and when a new domain or blocker appears.
- In the final report, state which skills/tools were actually used and which relevant capabilities were considered but not used, with the reason.
- Use `skill-creator` only when creating or updating a reusable Codex skill; do not use it as a general discovery entrypoint.

## Agent Skills

### Issue Tracker

GitHub Issues are the project issue tracker, and external pull requests are also treated as a triage surface. See `docs/agents/issue-tracker.md`.

### Triage Labels

Use the default mattpocock/skills triage vocabulary: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, and `wontfix`. See `docs/agents/triage-labels.md`.

### Domain Docs

This is a single-context repository. Read root `CONTEXT.md` for domain language and `docs/adr/` for architectural decisions when present. See `docs/agents/domain.md`.

## Verification

Prefer lightweight checks before broad reruns:

```bash
.venv/bin/python -m pytest -q
```

If dependency installation or a full test run is too costly, run the smallest relevant test file and record the reason in `操作记录.md`.

# AGENTS.md

## Workspace Purpose

This project is the focused Codex workspace for the low-cost sensing circular water-treatment intelligent closed-loop research project.

## Defaults

- Preserve the original source directory at `/Users/chuchenqidawang/Documents/低成本传感循环式水处理智能闭环项目`; do not mutate it unless explicitly asked.
- Keep code, experiments, reports, and model artifacts traceable.
- Put runtime code in `src/`, runnable experiment scripts in `experiments/`, tests in `tests/`, and publishable outputs in `deliverables/` or `outputs/`.
- Keep heavy or generated local artifacts out of Git when already ignored, especially `.venv/`, `.pytest_cache/`, `__pycache__/`, `*.pkl`, and `.worktrees/`.
- If creating worktrees, use `.worktrees/` and verify it is ignored before adding a worktree.

## Verification

Prefer lightweight checks before broad reruns:

```bash
python3 -m pytest -q
```

If dependency installation or a full test run is too costly, run the smallest relevant test file and record the reason in `操作记录.md`.

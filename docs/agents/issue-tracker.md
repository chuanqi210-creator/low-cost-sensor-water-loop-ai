# Issue Tracker: GitHub

Issues and PRDs for this repo live as GitHub issues. Use the `gh` CLI for issue operations.

## Conventions

- Create an issue: `gh issue create --title "..." --body "..."`
- Read an issue: `gh issue view <number> --comments`
- List issues: `gh issue list --state open --json number,title,body,labels,comments`
- Comment on an issue: `gh issue comment <number> --body "..."`
- Apply or remove labels: `gh issue edit <number> --add-label "..."` / `--remove-label "..."`
- Close an issue: `gh issue close <number> --comment "..."`

Run these commands from this repository so `gh` infers `chuanqi210-creator/low-cost-sensor-water-loop-ai` from `origin`.

## Pull Requests As A Triage Surface

PRs as a request surface: yes.

External pull requests from non-collaborators should go through the same triage roles as issues. Owner, member, and collaborator PRs are implementation work, not request intake.

Use:

- Read a PR: `gh pr view <number> --comments`
- Inspect a PR diff: `gh pr diff <number>`
- List candidate external PRs: `gh pr list --state open --json number,title,body,labels,author,authorAssociation,comments`

GitHub shares one number space across issues and PRs, so resolve a bare `#42` with `gh pr view 42` first, then fall back to `gh issue view 42`.

## Publishing Work

When a skill says "publish to the issue tracker", create a GitHub issue unless the user explicitly asks for local markdown or another tracker.

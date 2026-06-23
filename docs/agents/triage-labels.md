# Triage Labels

The mattpocock/skills triage flow speaks in canonical roles. This project maps those roles directly to GitHub labels.

| Canonical role | GitHub label | Meaning |
| --- | --- | --- |
| `needs-triage` | `needs-triage` | Maintainer needs to evaluate this issue or external PR. |
| `needs-info` | `needs-info` | Waiting on the reporter for more information. |
| `ready-for-agent` | `ready-for-agent` | Fully specified and ready for an AFK agent. |
| `ready-for-human` | `ready-for-human` | Requires human implementation or judgment. |
| `wontfix` | `wontfix` | Will not be actioned. |

Each triaged issue should carry exactly one state role. When category labels are needed, use normal GitHub labels such as `bug`, `enhancement`, or `documentation`.

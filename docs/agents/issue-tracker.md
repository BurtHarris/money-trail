Issue tracker: GitHub

This repository uses GitHub Issues as the canonical issue tracker. The engineering skills (to-issues, triage, to-prd, qa, etc.) will interact using the `gh` CLI by default.

How skills will use it

- Read issues by querying the repository's issues via `gh issue list` and `gh issue view`.
- Create issues with `gh issue create` when converting PRDs or automations into work.
- Apply labels and comment using `gh issue edit` / `gh issue comment`.

If you prefer a different workflow (e.g., a separate project board, Jira, or local markdown), update this file and re-run the setup skill.
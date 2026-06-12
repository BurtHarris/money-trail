Issue tracker: GitHub

This repository uses GitHub Issues as the canonical issue tracker. The engineering skills (to-issues, triage, to-prd, qa, etc.) will interact using the `gh` CLI by default.

How skills will use it

- Read issues by querying the repository's issues via `gh issue list` and `gh issue view`.
- Create issues with `gh issue create` when converting PRDs or automations into work.
- Apply labels and comment using `gh issue edit` / `gh issue comment`.

Sprint usage conventions (weekly)

- Use one GitHub Milestone per week as sprint scope container.
- Keep issue slices to 1-2 days and estimate with `S`/`M`/`L` in issue body.
- Use labels `in-progress` and `ad-hoc` to track WIP and unplanned work.
- Track weekly outcomes with milestone completion, carryover count, and cycle-time trend.

If you prefer a different workflow (e.g., a separate project board, Jira, or local markdown), update this file and re-run the setup skill.
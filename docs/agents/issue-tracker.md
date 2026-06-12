Issue tracker: GitHub

This repository uses GitHub Issues as the canonical issue tracker. The engineering skills (to-issues, triage, to-prd, qa, etc.) will interact using the `gh` CLI by default.

How skills will use it

- Read issues by querying the repository's issues via `gh issue list` and `gh issue view`.
- Create issues with `gh issue create` when converting PRDs or automations into work.
- Apply labels and comment using `gh issue edit` / `gh issue comment`.

Sprint usage conventions (weekly)

- Use one GitHub Milestone per week as sprint scope container, named `Sprint YYYY-Www`.
- Open new sprint work from the issue forms under `.github/ISSUE_TEMPLATE/` and assign the current milestone after creation.
- Keep issue slices to 1-2 days and estimate with `S`/`M`/`L` in the issue form or body.
- Use `ready-for-human` or `ready-for-agent` as the initial intake label; ad-hoc issues may carry `ad-hoc` as well.
- Use labels `in-progress` and `ad-hoc` to track WIP and unplanned work.
- Optional labels `size:S`, `size:M`, and `size:L` can mirror the estimate for filtering.
- Track weekly outcomes with milestone completion, carryover count, and cycle-time trend.

If you prefer a different workflow (e.g., a separate project board, Jira, or local markdown), update this file and re-run the setup skill.
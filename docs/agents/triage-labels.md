Triage label vocabulary

Canonical roles and default labels used by the triage skill:

- needs-triage — maintainer needs to evaluate
- needs-info — waiting on reporter for more information
- ready-for-agent — fully specified; an AFK agent can pick this up
- ready-for-human — needs human implementation/attention
- in-progress — actively being worked; use to enforce WIP limits
- ad-hoc — unplanned work pulled from weekly buffer capacity
- wontfix — will not be actioned

Weekly scrum support conventions:

- `ready-for-agent` and `ready-for-human` are the default intake labels used by the GitHub issue forms.
- `in-progress` is applied only when active work starts, and should stay within the weekly WIP limit.
- `ad-hoc` marks sprint work that was not part of the original weekly commitment.
- Optional size labels `size:S`, `size:M`, and `size:L` can mirror the required S/M/L estimate field from the issue forms.

If your repository already uses different label names, update the mapping here so the triage automation applies or references the correct labels.
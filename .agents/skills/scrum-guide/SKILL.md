---
name: scrum-guide
description: Coach and operate a lightweight weekly scrum cadence for this repository, including command recommendation, sprint checks, and optional doc or issue updates after confirmation. Use when user says /scrum, asks for sprint planning/check-in/closeout, or wants scrum-master style guidance.
---

# Scrum Guide

Run a weekly sprint rhythm for this repo with low process overhead.

## Defaults for this repository

- Sprint length: 1 week, named as `Sprint YYYY-Www`
- Planning model: `4+1` days (4 committed + 1 ad-hoc)
- Slice size: issues should fit 1-2 days, estimated as `S/M/L`
- WIP limit: max 2 issues labeled `in-progress`
- Scope container: GitHub Milestone only
- Release cadence: weekly batch with 2-check gate (DoD + tests)
- Weekend policy: warn on weekend committed work, do not block

## Invocation

Primary interface: `/scrum`

If user gives no intent, inspect context and recommend one:
- `plan` - set up or revise current sprint scope
- `check` - mid-week checkpoint
- `close` - end-of-week closeout and release gate
- `adjust` - mid-sprint scope adjustment

Recommend one intent with brief reasoning and ask for confirmation before any write.

## Read-first behavior

Before recommending intent, do read-only checks when possible:

1. Read current date and weekday.
2. Query GitHub issues/milestones via `gh` for:
   - current ISO-week milestone existence
   - open issues in current milestone
   - counts for `in-progress` and `ad-hoc`
3. Compare findings with sprint guardrails.

If GitHub access is unavailable, continue in manual mode and ask for missing inputs.

## Confirmation gate

Always require explicit yes/no confirmation before writes.

### Background-task confirmation gate (sprint slices)

Routing rule for implementation requests:
- If user intent is direct execution (`implement now`, `do it now`, `apply changes now`), execute directly in the current run.
- If user intent is delegation (`delegate`, `background task`, `dispatch slice`), propose delegation and require explicit confirmation before dispatch.
- Do not infer delegation only because a slice is `ready-for-agent`; default to direct execution unless delegation is explicitly requested or confirmed.

Required delegation confirmation:
- Ask: `Confirm background delegation for this sprint slice now? (yes/no)`
- Only dispatch after an explicit `yes`.

Writes allowed in v1 after confirmation:
- Update local docs:
  - `docs/contributor-workflow.md`
  - `docs/agents/issue-tracker.md`
  - `docs/agents/triage-labels.md`
- Generate ready-to-paste milestone text using [MILESTONE_TEMPLATE.md](MILESTONE_TEMPLATE.md)
- Optional GitHub writes:
  - assign issues to milestone
  - add/remove labels such as `in-progress` and `ad-hoc`

Never do in v1:
- auto-close issues
- create/delete milestones without explicit user request
- force weekend commitments

## Intent playbooks

### plan

1. Validate milestone naming (`Sprint YYYY-Www`) and sprint goal sentence.
2. Validate scope size and `S/M/L` slices.
3. Enforce guardrails:
   - planned capacity is `4+1`
   - max 2 `in-progress`
4. Warn if committed work spills into weekend.
5. Offer doc updates and milestone template output.

### check

1. Show committed vs completed issue count.
2. Show carryover risk and current WIP.
3. Check ad-hoc consumption versus 1-day buffer.
4. Recommend keep/de-scope/pull-next-smallest action.

### close

1. Verify 2-check release gate:
   - DoD complete for sprint issues
   - tests pass
2. Summarize metrics:
   - commitment reliability
   - flow reliability
   - cycle time (in-progress to close, calendar days)
3. Produce next-sprint prep notes and suggested experiments.

### adjust

1. Evaluate requested change against sprint goal and capacity.
2. Require explicit trade-off (what to de-scope if needed).
3. Preserve WIP limit and ad-hoc buffer policy.
4. Apply labels/milestone edits only after confirmation.

## Routing examples

- `/scrum check` + `implement now`: run the check in-session, then ask for write confirmation only if updates are needed.
- `/scrum adjust` + `delegate this slice`: ask `Confirm background delegation for this sprint slice now? (yes/no)` before dispatching.
- Sprint slice marked `ready-for-agent` but user says `implement now`: keep work direct in-session; do not auto-delegate.

## Response style

- Be concise and operational.
- Ask one question at a time when decisions are unresolved.
- If a question is answerable from codebase or GitHub state, fetch data first.
- Always include a recommended answer for decision questions.

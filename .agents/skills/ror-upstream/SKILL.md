---
name: ror-upstream
description: Upstream merge discipline for the RoR fork — file layout that avoids conflicts, the touch register, the sync runbook, and provenance preservation. Load before editing an upstream file or running a sync.
---

# ror-upstream

Upstream is `Gtym33/Kursach-Himiya`, actively developed. This fork must be able to take his changes indefinitely.

## The two rules that matter most

**1. Merge, never rebase.** Provenance on the dashboard is computed by `git blame` against the upstream merge base. A rebase reattributes every focus in the mod to whoever ran it. This is not a style preference; it destroys data.

**2. New content goes in new files.**

```
common/national_focus/ror_fork_<TAG>_<branch>.txt
events/ror_fork_<theme>.txt
common/ideas/ror_fork_<theme>.txt
common/decisions/ror_fork_<theme>.txt
common/script_constants/ror_fork_<subsystem>.txt
localisation/russian/ror_fork_*_l_russian.yml
```

A new file cannot conflict. Every line added to an upstream file can.

Prefixes belong on **files in dedicated folders** — not on variable names, scripted effects or triggers. Do not prefix internals.

## Editing an upstream file

Only when the additive route genuinely does not exist. Then:

1. **Minimal mechanical edit.** No reformatting, no reordering, no tidying, no "while I'm here". Those turn a 3-line conflict into a 100-line one.
2. **Log it in `docs/upstream-touches.md`** — file, lines, reason, date, and whether behaviour changed.
3. If it changes behaviour, add an entry to `docs/known-upstream-defects.md` explaining what and why.

Prefer `shared_focus` when extending an existing tree — it stays additive.

## The sync runbook (human-triggered, never unattended)

An agent resolving Paradox script conflicts alone produces output that **parses cleanly and is semantically wrong** — T1 and T2 will both pass it. That is the worst available failure mode, so this runs with the owner present on the Mac.

1. `git fetch upstream && git merge upstream/master` — **merge, never rebase**.
2. Read `docs/upstream-touches.md` first. It lists the expected conflict sites.
3. Resolve with the owner approving each resolution individually.
4. Full T1; T2/T3 when they exist. Telemetry if Lane B2 changes are live.
5. **Refresh the style corpus:** `tools/build_corpus.py`. The fork's voice should track Gtym33's as he develops it.
6. **Refresh the lint baseline:** `tools/ror_lint.py --write-baseline tools/upstream-baseline.json`. This is the only legitimate reason to rewrite it.
7. Rebuild the graph and confirm provenance survived — `by_provenance` should still show the bulk as `upstream-human`. If it collapsed to `owner` or `agent`, history was rewritten and that must be fixed before anything else.

## Current state

Fork point: `ad86f3a6a`. 21 upstream files carry edits, all one or two characters, all logged. Four change behaviour: U-01 to U-04 in `docs/known-upstream-defects.md`.

The `upstream` remote has its push URL disabled on purpose. If you need to send something to Gtym33, that is an owner decision and an explicit action, not something to do in passing.

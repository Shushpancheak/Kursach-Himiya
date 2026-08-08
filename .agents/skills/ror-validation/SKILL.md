---
name: ror-validation
description: Run and interpret the RoR validation pyramid — T1 lints, T2 CWTools, T3 tree render, T4 boot smoke test, T5 telemetry. Load when validating a change or reading validation output.
---

# ror-validation

Cheap to expensive. Each tier gates the next.

## T1 — lints (seconds, every write)

```bash
tools/ror_lint.py --baseline tools/upstream-baseline.json
```

**Always pass `--baseline`.** Without it you get 2,681 inherited findings and no signal. With it you see only what your branch introduced. Exit code is non-zero if there are errors.

Other flags: `--changed` (only files changed vs the upstream merge base), `--json out.json`, `--warnings-as-errors`.

### Codes

| Code | Meaning |
|---|---|
| `S001` | Brace imbalance or unterminated string |
| `L001` | **Localisation file not UTF-8 with BOM** — highest-value check here |
| `L002` | Language header is not `l_russian` (C8) |
| `L003` `L004` | `:0` version suffix / duplicate key |
| `L005` | `§` with no colour code or reset |
| `E001` | `<=` or `>=` — unsupported, breaks the game |
| `E002` | Unary `-` on a variable token |
| `E003` | `ROOT.`/`PREV.` on a temporary variable — silently does nothing |
| `E004` | Global event target saved but never cleared |
| `E005` | `@CONSTANT` used but not defined in that file — they are file-scoped |
| `R003`–`R007` | Prerequisite / mutual exclusivity / localisation / icon does not resolve |
| `G001`–`G003` | Asymmetric exclusivity / prerequisite cycle / unreachable focus |
| `Y001` `Y002` | Bad anchor / coordinate collision |
| `P001` `P002` | Trivial `completion_reward` / missing `ai_will_do` |
| `V001` | Deny-lexicon hit in authored prose |

### The baseline

`tools/upstream-baseline.json` freezes what upstream already had. **Refresh it only after an upstream merge**, never to silence your own branch:

```bash
tools/ror_lint.py --write-baseline tools/upstream-baseline.json
```

Silencing your own finding by rewriting the baseline is the single easiest way to make this whole pipeline decorative.

### If T1 fails on code you did not touch

Check `docs/known-upstream-defects.md` first. If it is listed, cite the entry. If it is not, treat it as caused by your change (`AGENTS.md` §4.19).

## T1b — graph

```bash
tools/build_graph.py            # with provenance, ~3s
tools/build_graph.py --no-blame # faster
```

Confirm your focuses appear, positions resolve, and completeness is what you expect. `spec_drift` reports specs naming focuses that do not exist, and focuses with no spec.

## T2 — CWTools (minutes)

**Not yet wired.** Spike S2 is unresolved and it needs vanilla files. Do not claim T2 ran.

## T3 — tree render (minutes)

**Not yet wired.** Spike S3 (hoi4treesnap stripped of its Fyne GUI) is unresolved.

## T4 — boot smoke test (nightly, server)

**Not yet wired.** Spike S1 is unresolved pending the HOI4 install on the server. Xvfb + Mesa llvmpipe is confirmed working there (OpenGL 4.5), which is a good sign but not a result.

When it exists: launch with `-debug` under Xvfb, reach the main menu, exit, diff `error.log` against a baseline allowlist.

## T5 — telemetry (Lane B2 only)

See `ror-balance`. Gated on S1 and S4.

## hoi4skill

**Parked** by owner decision, pending vanilla files. The binary is built and pinned at v0.30.2 in `$ROR_REFS/hoi4skill/bin/`. It is not part of the pipeline. It reports 1,439 errors on unmodified upstream, of which roughly three quarters are its own generator's layout conventions. See `docs/tooling-decisions.md` before proposing to use it.

## Reporting

Per `AGENTS.md` §5: **report validation only when it is task-specific, could realistically have failed, found something, or changed the implementation.**

Do not write "T1 passed, BOM intact, braces balanced, no unsupported operators". That restates the rules rather than reporting evidence. Say what you ran, what it found, and what you did about it — or say nothing about it at all.

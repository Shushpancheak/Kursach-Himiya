# Tooling decisions and spike results

Why the pipeline is shaped the way it is. Written so that nobody re-runs an investigation whose answer is already known.

Plan documents: `ror-agent-loop-plan-v2.md` (authoritative), `ror-plan-addendum-A-tooling-survey.md`, `ror-agent-loop-plan.md` (history).

---

## S6 — Claude config isolation: **RESOLVED**

The variable is **`CLAUDE_CONFIG_DIR`**, confirmed against the shipped binary (2.1.220), not from memory or docs. `CLAUDE_SECURESTORAGE_CONFIG_DIR` also exists and is separate — it governs credential storage, not skills and settings.

`.envrc` sets it to `$HOME/.claude-ror`. Applied by `direnv` on directory entry, so it cannot be defeated by forgetting an alias.

Two caveats worth knowing:

- It takes effect in **new** sessions started inside the repo. A session already running when `.envrc` was added keeps the config it started with.
- The isolated directory starts empty, so the first session there needs a fresh login.

Project-scope `permissions.deny` in `.claude/settings.json` covers the owner's work source roots and credential files. Note that user-scope settings on this machine grant broad access; `deny` rules take precedence, which is what makes the project-scope list load-bearing rather than decorative.

---

## S9 — `hoi4skill validate` on unmodified upstream: **FAIL**

`hoi4skill 0.30.2`, run against the fork point with no `--game-root`: **1,439 errors, 23,097 warnings.**

The plan's calibration rule says a tool that fails on upstream is wrong until proven otherwise. Verified category by category:

| Finding | Count | Verdict |
|---|---|---|
| `focus missing relative_position_id` / `uses relative_position_id` | 1,082 | **House style.** Absolute `x`/`y` is legal HOI4. This is its own generator's convention. |
| `idea picture must omit GFX_idea_ prefix` | 119 | **Plausibly real, unresolved.** See N-01 in [known-upstream-defects.md](known-upstream-defects.md). |
| `focus missing completion_reward` | 66 | Real; this repo checks it as `P001`. |
| `£icon£ has no icon name` | 50 | **False positive.** See below. |
| brace imbalance | 20 | **Real**, independently confirmed. |
| `§` colour balance | 15 | 4 real, rest over-strict. |

Warnings are ~90% noise: 10,167 are "missing recommended *generated-template* field" and roughly 4,000 are sprite lookups that cannot resolve without a game root.

### The `£` tokenizer bug

hoi4skill flags **all 37** paired `£victory_points£` forms in this mod and **none of the 208** unpaired `£command_power` forms. It reads the closing `£` as a new marker with an empty name. Both forms are valid, and the flagged strings are vanilla-derived (`EFFECT_ADD_VP`, `MINIMUM_SEAZONE_DOMINANCE_NEEDED`).

### Where it was right

Its brace checker agreed with this repo's independent parser on **20 of 20** files, matching sign and depth. One disagreement: `PRM_contra_2.0.txt`, which hoi4skill called a depth-2 brace imbalance. Raw braces there are 28/28; the actual defect is an unterminated string. Its report was an artefact of its own string handling — right file, wrong reason.

---

## S10 — coverage overlap: **INCONCLUSIVE**

Addendum A required this before writing any lint. It cannot be settled yet: every hoi4skill capability that would justify adopting it — `--strict-code-index`, sprite resolution, reference integrity, event-chain analysis — needs `--game-root`, and no vanilla files exist on either machine.

**What is already known:**

- Focus geometry: hoi4skill has opinions about anchoring but does not check coordinate collisions. Ours.
- AND-of-OR prerequisite semantics: not covered. Ours.
- UTF-8 BOM: not observed to be checked. Ours, and it is the highest-value single check here — all 195 upstream localisation files carry the BOM, and a Cyrillic mod that loses it renders as mojibake with every other tier still green.
- Brace balance: covered by both, and both were verified correct.

**Decision (owner, 2026-08-08): park hoi4skill until vanilla files arrive.** The binary is built and pinned at `v0.30.2` in `$ROR_REFS/hoi4skill/bin/`, not wired into the pipeline. `tools/ror_lint.py` therefore has to stand alone, which R13 wanted anyway.

Re-run S9 and S10 with `--game-root` once vanilla is in place. The 119-error `GFX_idea_` question is the specific thing to settle first.

**Licence note:** GPL-3.0-only. Invoke the binary as a separate process. Do not vendor or link its source.

---

## Why the reference material lives outside the repo

`$ROR_REFS` (default `~/ror-refs`) holds the Paradox wiki snapshot, the vanilla HOI4 text subset and the hoi4skill binary.

- The wiki snapshot ships inside `klimPaskov/Agentic-HOI4-Modding`, which has **no licence file** — all rights reserved by default. It does not belong in a public fork.
- Vanilla game files are Paradox's.
- Fewer files in the repo means fewer upstream conflict sites (C7).

---

## T1 calibration

`tools/ror_lint.py` runs in ~5 s over 4,863 script files, 196 localisation files and 2,628 focuses.

First run against upstream produced 328 errors. **Three checks were wrong and were corrected, not suppressed:**

1. **Dead-node detection** compared options *within* one `prerequisite` block. That block is an OR, and options inside it being mutually exclusive is the ordinary "two branches converge here" pattern. It must compare *across* AND-ed blocks. The wrong version flagged ~160 healthy focuses.
2. **Colour-code validation** accepted only letters after `§`. Digits (`§1`) and signs (`§+`, `§-`) are valid. 15 false positives.
3. **Unary-minus detection** fired on `add = -num_armies` in `common/scorers/`, where the token is an engine scorer, not a script variable. The check now skips AI grammar.

After correction: **150 errors, all verified real** — 149 focuses with no localisation key, and one prerequisite deadlock. Both are upstream content problems, recorded in `known-upstream-defects.md` and frozen in `tools/upstream-baseline.json` (2,608 findings).

Branches gate on what they introduce:

```bash
tools/ror_lint.py --baseline tools/upstream-baseline.json
```

The gate was verified against deliberately planted defects — `>=`, a missing BOM, a non-Russian language header, a dangling prerequisite, missing localisation, an unreachable AND-group node, and a coordinate collision were all caught while all 2,608 inherited findings stayed suppressed.

**Refresh the baseline only after an upstream merge**, never to silence a branch's own findings.

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

## S10 — coverage overlap: **RESOLVED. Do not adopt hoi4skill.**

Re-run on 2026-08-08 with `--game-root` pointed at the real vanilla install, which is what Addendum A said was needed to settle it.

**It got worse, not better: 1,439 errors → 7,418.**

The dominant categories are demonstrably wrong:

| Category | Count | Verdict |
|---|---|---|
| `unknown trigger` | 2,179 | **2,131 are `CONTROLLER`, `OWNER` and `IF`** — scope changers, not triggers. 97.8% false positive in its largest category. |
| `unknown effect` | 999 | `token` and `iteration_output` (261 each) are `special_projects` schema fields; a further 239 are the same scope changers. |
| `idea picture must omit GFX_idea_` | 119 | **Disproved.** All 119 resolve via the engine's verbatim fallback, which vanilla itself relies on 20 times. See N-01. |
| `unknown modifier` | 258 | Not individually verified; the prior is poor. |
| focus layout opinions | ~1,082 | Its own generator's house style. Absolute `x`/`y` is legal. |

It does not model Clausewitz scope changers. In a mod whose triggers are full of `CONTROLLER = { ... }` and `OWNER = { ... }`, that is disqualifying on its own.

**What it got right, and what we kept:** its brace checker agreed with our parser on 20 of 20 files. That check now lives in `tools/clausewitz.py`, verified independently, so nothing is lost by dropping the tool.

**Decision: hoi4skill is not part of this pipeline.** The binary stays in `$ROR_REFS/hoi4skill/bin/` at `v0.30.2` for occasional cross-checking, invoked as a separate process (GPL-3.0-only — do not vendor or link its source). Addendum A's premise, that half of T1 already existed, did not survive contact with the mod. `tools/ror_lint.py` stands alone.

**What we own, and now verify:** geometry and coordinate collisions, AND-of-OR prerequisite semantics, UTF-8 BOM, focus and idea sprite resolution (with the vanilla index and both engine fallbacks), graph integrity, the period lexicon.

---

## Vanilla HOI4 — installed, and what it changed

`v1.19.2.0` "Operation Postern", matching RoR's `supported_version="1.19.*"`. 20 GB on the server via steamcmd; a 139 MB text subset synced to the Mac at `$HOI4_VANILLA_ROOT`.

**DLC: complete.** The game script references 16 distinct `has_dlc` gates and all 16 have an installed DLC; the mod gates on 13, all present. All four integrated expansions (Together for Victory, Death or Dishonor, Waking the Tiger, Man the Guns) are in `integrated_dlc/`. Gaps in the `dlcNNN` numbering are cosmetic and music packs sold as separate Steam apps that never appear in a `has_dlc` gate.

Worth knowing: **DLC ships its script in the base install**, gated at runtime. The `dlc/*/` folders hold only `gfx/`, `interface/`, `music/`, `portraits/` and `sound/`. Reference checking would work with no DLC owned at all.

### Effect on T1

Indexing vanilla changed the result set enormously:

| Check | Without vanilla | With vanilla |
|---|---|---|
| `R007` focus icons | 690 | **14** |
| `R008` idea pictures | 1,685 | **76** |

Because the two modes differ so much, the baseline records `vanilla_indexed` and the lint warns loudly when a comparison mixes them. A baseline built in one mode and used in the other reports thousands of phantom regressions.

`R008` had to learn two engine behaviours before it was trustworthy — the verbatim sprite fallback and graphical-culture suffix variants. Without those it reported ~1,600 phantom findings. Both were discovered by checking vanilla's own content, not by reading documentation.

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

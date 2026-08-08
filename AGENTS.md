# Repository Guidelines

This file describes how to read, edit and extend this fork of **Reaction or Revolution** (RoR, upstream `Gtym33/Kursach-Himiya`).

It is the **domain layer**: how to write correct HOI4 script. Three layers exist and must not bleed into each other.

| Layer | Lives in | Owns |
|---|---|---|
| **Process** | `openspec/` + the `opsx` skills | How a change moves idea → spec → implementation → archive |
| **Domain** | **this file** + `$PARADOX_WIKI` + `$HOI4_VANILLA_ROOT/documentation/` | Clausewitz syntax, engine gotchas, focus/event patterns |
| **Project** | `.claude/skills/ror-*` + `docs/` | RoR voice, validation pyramid, provenance, upstream discipline, budget |

**Never put RoR-specific or branch-specific content into this file or into a general skill.** Rules that accumulate one-off context stop being reusable and become noise. Branch specifics belong in the OpenSpec change folder.

Derived from `klimPaskov/Agentic-HOI4-Modding` (`AGENTS_template.md`), trimmed to what this repo uses. Two of its rules are **deliberately inverted** — see §4.15 and §4.16.

---

## 0. Required reading before any change

### Environment

`direnv` exports these on directory entry. Never hardcode paths.

| Variable | What |
|---|---|
| `$PARADOX_WIKI` | Offline Paradox wiki snapshot (50 pages, markdown) |
| `$HOI4_VANILLA_ROOT` | Vanilla HOI4 install, text subset |
| `$ROR_REFS` | Parent of both, outside the repo |

Reference material is **outside the repo on purpose**: the wiki snapshot ships in a kit with no licence file, and vanilla files are Paradox's. Neither goes in a public fork.

### Paradox wiki

Consult the relevant pages from `$PARADOX_WIKI` before opening any file. Use the snapshot; do not fetch the wiki over the web — the snapshot is deterministic and works headless.

Always open at least: Data structures, Triggers, Effects, Modifiers, Localisation, Scopes, On actions, Event modding, Decision modding, Idea modding, AI modding.

For other systems open the matching page (Interface Modding, Scripted GUI Modding, Country creation, National focus, Equipment, Division, Technology). **Do not rely on memory when a page exists.**

### Vanilla references

- `$HOI4_VANILLA_ROOT/documentation/` contains official markdown docs and **must be read**. Treat vanilla documentation as **more authoritative and more current than the wiki**. Both are required; neither is optional.
  - `documentation/script_concept_documentation.md`
  - `documentation/effects_documentation.md`
  - `documentation/triggers_documentation.md`
  - `common/script_constants/documentation.md`
- Vanilla docs also appear in other folders (e.g. `common/factions/_documentation.md`). Consult them for the systems you touch.
- When implementing anything, find a **vanilla or RoR precedent and mirror its structure**. If RoR already has a pattern for the same thing, follow RoR over vanilla, but still read the vanilla implementation.

### Specs and plans

Specifications live in **`openspec/`**, not `docs/specs/` and not `docs/plans/`.

- In-flight change → `openspec/changes/<slug>/` (proposal, specs, design, tasks)
- Standing capability → `openspec/specs/`
- Per-mechanic documentation → `docs/` (§4.3)

**The content inventory is never declared.** What focuses and events exist is parsed from the `.txt` files by `tools/build_graph.py`. Specs say what *should* exist; the parser reports what *does*. Disagreement between them is a finding, not something to paper over.

### Repo skills

Use these as required implementation guidance, not optional notes.

| Skill | Load before |
|---|---|
| `ror-focus-tree` | any focus-tree edit |
| `ror-event-chain` | any event work |
| `ror-voice` | any player-facing text |
| `ror-validation` | running or reading the T1–T5 pyramid |
| `ror-balance` | Track B Lane B2 only |
| `ror-upstream` | merges, upstream-file edits, conflict work |

### Subagents

Spawn every auditor with **`fork_context=false`**. No inherited parent context — a reviewer that shares the writer's context reproduces the writer's blind spots. If an auditor needs a constraint or prior decision, pass it explicitly in the prompt or write it into the change folder first.

Auditors return **evidence**. The main agent owns final wiring, final review, and every completion claim.

---

## 1. Coding style

Clausewitz script is picky. These are engine-correctness rules, not preferences.

1. Indent with **tabs**. Lowercase keys, snake_case identifiers.
2. **Never use `<=` or `>=`.** Unsupported; breaks the game. Use `check_variable` with `compare = greater_than_or_equals` / `less_than_or_equals`. Prefer plain `<` and `>` where they suffice — reach for the long form only when you actually need the boundary.
3. No magic numbers. Tuning lives in one place so it can be changed in one place.
4. **Temporary variables have no scope.** `ROOT.my_temp_var` and `PREV.my_temp_var` silently do nothing. Only normal variables have scope.
5. Use flags for boolean state, not variables that only ever hold 0 or 1.
6. Move repeated logic into `scripted_effects` / `scripted_triggers`.
7. **`@CONSTANT` is file-scoped** and cannot cross file boundaries.
   - Prefer `script_constants` in `common/script_constants/` for shared tuning values: global, readable, injected at load, no runtime cost.
   - Access them as `constant:category.key`.
   - Not every field parses `constant:` tokens. For fields that reject them (e.g. `days =` inside timed flags), assign to a variable first and pass the variable.
   - Read `$HOI4_VANILLA_ROOT/common/script_constants/documentation.md` before adding any.
8. **Event targets.** `save_event_target_as` for short-lived chains (auto-clears when the effect chain ends, but carries into events fired from that chain). `save_global_event_target_as` only when you need persistence beyond one chain — it does **not** auto-clear and **must** be paired with `clear_global_event_target`. In localisation, drop the prefix: `[my_target.GetName]`.
9. **No unary `-` on variable tokens.** `value = -my_var` is invalid; negate via `multiply_variable` first.
10. When an effect or trigger rejects dynamic values, use `meta_effect` / `meta_trigger` with `text = { ... }` to inject computed variables. These are powerful — `my_scripted_effect_[ID] = yes` lets you pick a scripted effect dynamically.
11. Prefer reusable dynamic scripted effects. Check what exists before writing new logic; document new ones in `docs/` in the same change.
12. **`on_weekly`, `on_daily`, `on_monthly` and similar on-actions iterate over every country.** See §10 — this is a hard gate, not a style note.

---

## 2. Localisation and UI

C8: **Russian only.** There is no English localisation track.

1. Localisation files must be **UTF-8 with BOM**. Wrong encoding breaks strings in game, and with Cyrillic content that is a certainty, not a risk. All 195 upstream files carry the BOM; keep it that way.
2. Adding or renaming anything on screen updates localisation **in the same change**.
3. Write keys as `key_name: "Text"` — no `:0`, no leading space.
4. Icon markers are written `£icon_name£` and colour codes `§R…§!`. Both forms appear in vanilla-derived text and are correct.
5. **Player-facing text describes world state and player choices, never implementation history.** No "now reworked", "newly added", "this was changed". Write updated content as if the feature always existed.
6. Icons: define in `interface/*.gfx` with stable names. Copy a **placeholder sprite from vanilla** matching each new `.gfx` definition, so the game loads without missing-sprite errors and final art drops in cleanly later. Register assets before requesting art so filenames never need to change.

---

## 3. Naming and file layout

Prefixes belong on **files in dedicated folders**, not on every variable, scripted effect or trigger. Unnecessary prefixes make code harder to read.

New content goes in **new files** with the `ror_fork_` prefix:

```
common/national_focus/ror_fork_<TAG>_<branch>.txt
events/ror_fork_<theme>.txt
common/ideas/ror_fork_<theme>.txt
common/decisions/ror_fork_<theme>.txt
common/script_constants/ror_fork_<subsystem>.txt
localisation/russian/ror_fork_*_l_russian.yml
```

1. Never append to an upstream file when a new one will do.
2. Extending an existing tree: prefer `shared_focus` to stay additive.
3. Editing an upstream file: **minimal mechanical edit only.** No reformatting, no reordering, no tidying, no "while I'm here". Those are what turn a 3-line conflict into a 100-line one.
4. **Every upstream-file edit is logged in `docs/upstream-touches.md`** with file, reason and date. That register is consulted before each upstream sync.

---

## 4. Modding checklist

1. Open the required wiki pages (§0) and keep Data Structures, Triggers, Effects, Modifiers and Localisation in front of you.
2. Read the vanilla documentation for the systems you touch.
3. **Create a markdown file in `docs/` for every new mechanic.** Describe what it does, how it works step by step, and how it interacts with existing systems. Add a section for future extensions.
4. In that docs file, **list every icon needed**: where sprites live, which `.gfx` references them, and the icon names used in code and localisation.
5. Plan variables and flags so values are dynamic and centralised.
6. Avoid unsupported operators and constructs (§1).
7. Use loops, meta effects and scripted effects to remove duplication.
8. Reuse existing dynamic scripted effects before writing bespoke logic.
9. Keep localisation, icons and UI definitions aligned in the same edit.
10. New equipment type / archetype / category ⇒ update `common/script_enums.txt` in the same change.
11. Document each new script file with an overview at the top.
12. Confirm decisions and event options have proper trigger tooltips and effect descriptions.
13. Respect repo style so new content blends with existing RoR code.
14. For systems touching an existing project-wide mechanic, review related docs and verify integration across events, on_actions, decisions, scripted logic, UI and localisation.
15. **[INVERTED from the source kit]** The source kit says never to launch HOI4 and that live testing belongs to the user. **That is wrong for this repo.** This loop has a headless server, `-debug` boot smoke tests and savegame telemetry. Launching the game headlessly is a normal, expected part of validation — see `ror-validation` for T4 and T5.
16. **[INVERTED from the source kit]** The source kit forbids asking for or searching logs, and assumes the owner verifies everything in a live session. **That is wrong for this repo.** `error.log` and telemetry artifacts are **primary evidence** and must be consulted before diagnosing anything. **Never ask the owner to reproduce something the harness can measure.**
17. **Fallbacks are never allowed without explicit owner approval.**
18. When something is wrong and the cause is unclear, add temporary debug output (`log = "..."`) exposing the relevant runtime values, then remove every debug line once resolved.
19. When an error appears after your changes, treat it as caused by your change set. Do not speculate that the project was already broken — unless `docs/known-upstream-defects.md` already records it, in which case cite the entry.
20. When updating content, write as if the feature always existed (§2.5).
21. Respect the writing style. `ror-voice` is the source of truth.

If this checklist cannot be satisfied, **stop and request design input instead of guessing.**

---

## 5. Completion proof and simplification reporting

A goal is never complete unless it is actually complete.

**Do not claim completion when:**

- only the most visible part was implemented
- a tree was created but not reviewed, customised, balanced, localised and wired
- a batch of countries received generic or copied content
- balance checks were skipped
- localisation, AI behaviour, or assets are missing, unwired or undocumented
- docs, tables or manifests describing the changed system are stale
- any requested route, country, decision, event chain or focus path is missing
- a fallback or simplification was used without explicit approval

**Do not replace real implementation work with tooling work.** Do not spend a goal building Python scripts, report generators or bulk-generation helpers while the actual content stays shallow. Small scripts for mechanical audits are fine; they are not a substitute for content. *(This repo is tooling-heavy by design. That makes this the easiest rule here to break.)*

**Do not bulk-generate** trees, country packages, decisions or localisation and call them done. Generated drafts count only when every result is reviewed, customised to its country and route, wired in, localised, given AI behaviour, and documented.

**Every simplification, omission and blocker gets its own report section**, headed `Simplifications, omissions, and blockers`. Even small deviations. If there were none, say so explicitly and back it with evidence — files changed, audits run, checklists completed.

**Report validation only when it is task-specific, could realistically have failed, found something, or changed the implementation.** Do not pad reports with boilerplate passes that merely restate the rules in this file.

A goal is not complete because the game loads, or because the visible part works.

---

## 6. Focus trees

Load `ror-focus-tree` before editing any tree. It owns depth, reward variety, route logic, AI weights, icons, geometry and completion standards.

Run the focus-tree auditor before claiming completion. If a tree works but feels shallow, duplicated, generic or disconnected from gameplay, that is a finding — report it rather than shipping it.

---

## 7. Skill maintenance

Skills are the agent's memory for repeated workflows and hard-won fixes.

1. Check whether an existing skill covers the workflow before creating one.
2. Prefer updating an existing skill over creating a new one.
3. Add concise rules based on actual experience, not speculation.
4. Record repo paths, commands, gotchas and validation steps that would otherwise be rediscovered.
5. Keep each skill to one reusable workflow.
6. **Never put feature-specific, country-specific or one-off context inside a general skill.** This matters more than it sounds.
7. Report which skills were used, created or updated at the end of each task.

---

## 8. Git

- Work happens on `ror/<slug>`. **Never commit to `main`. Never merge. Never rebase** — provenance attribution in the dashboard is computed from `git blame` against the upstream merge base, and a rebase destroys it.
- A commit contains only the changes belonging to its change folder.
- Review the diff before committing.
- Do not commit broken, unrelated or half-finished work. Report the blocker instead of writing a misleading commit.
- Upstream sync is **human-triggered and never unattended** (see `ror-upstream`).

---

## 9. Hard gates

These stop work and require the owner. They are not warnings and not lints.

### 9.1 World-iterating on-actions

`on_weekly`, `on_daily`, `on_monthly` and similar **iterate over every country by default**. In a mod spanning 1917–1945 that is a performance catastrophe, and it is exactly what global balance work reaches for first.

- `on_daily_TAG` and other narrowly-scoped variants: **allowed freely.**
- Any world-iterating on-action: **stop and request explicit owner approval before implementing.**
- Where iteration is genuinely needed, prefer MTTH-weighted or event-driven approaches first, and centralise tuning in `script_constants`.
- Telemetry for such a change must include **tick time**, not just world state. A balance script with perfect numbers that halves game speed is a failure.

### 9.2 Fallbacks

Never allowed without explicit owner approval. Report the blocker instead.

### 9.3 Upstream conflict resolution

Never resolved unattended. An agent resolving Paradox script conflicts alone produces output that **parses cleanly and is semantically wrong** — every automated tier will pass it.

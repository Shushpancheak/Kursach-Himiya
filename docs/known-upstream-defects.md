# Known upstream defects

Defects found in `Gtym33/Kursach-Himiya` and what this fork did about them.

`AGENTS.md` §4.19 says to treat any error appearing after your changes as caused by your changes. This file is the exception list: if a symptom matches an entry here, cite the entry instead of hunting your own diff.

Found by `tools/ror_lint.py` (structural pass) on the fork point, `ad86f3a6a`, 2026-08-08. Cross-checked against `hoi4skill 0.30.2`, which independently reported 19 of the 20.

---

## Fixed in this fork

### U-01 — `USA_npt.txt`: 20 focuses sat outside the focus tree
**Severity: high. Behaviour changed.**

`focus_tree = {` opened at line 1 and closed at line 2265, followed by an orphan `}`. The remaining 20 `focus = { ... }` blocks (lines 2267–2677) were therefore **top-level entries in a national_focus file**, which is not a valid position — the only legal top-level keys are `focus_tree`, `shared_focus`, `joint_focus`, `style` and `continuous_focus_palette`.

The affected focuses begin at `USA_gen_army_aviation2` and run to the end of the file.

**Fix:** removed the two orphan braces, closed the tree at EOF.

**Verified with `tools/build_graph.py`:** the USA tree held 133 focuses with 20 orphaned before the fix, and 153 with 0 orphaned after.

**Consequence:** 20 previously dead focuses are now live in the USA tree. This is a real gameplay change and USA's tree should be looked at before it is trusted. It is the reason this file is flagged in the touch register.

### U-02 — `events/Turkey.txt`: `turkey.29` and `turkey.30` could not fire correctly
**Severity: high. Behaviour changed.**

Both events contained `CONTROLLER = { OR = { tag = TUR is_subject_of = TUR } ` with no closing brace. The `trigger` block therefore never terminated, and `mean_time_to_happen`, `fire_only_once` and `option` were parsed as part of the trigger rather than as siblings of it.

**Fix:** closed the `CONTROLLER` block on lines 1411 and 1476.

**Consequence:** both events now have a real MTTH and a real option. They were previously inert.

### U-03 — `QIN - Qing.txt`: `1914.1.1` block closed early
**Severity: medium. Behaviour changed.**

A stray `}` after `set_politics = { ... }` closed the `1914.1.1 = {` block, leaving `set_popularities` and `add_ideas` at file scope — so they applied unconditionally at game start instead of on that date.

**Fix:** removed the stray brace.

### U-04 — `PRM_contra_2.0.txt`: unterminated string
**Severity: medium. Behaviour changed.**

`division_template = "Kavaleriyskaya Diviziya` was missing its closing quote, so the engine read to end of line and produced a silently wrong template name for the final division.

**Fix:** closed the string.

This was the **only** unterminated string in the mod, and it is the one file where `hoi4skill` and this repo's parser disagreed: hoi4skill reported it as a brace imbalance. Raw braces are 28/28. The brace report was an artefact of its own string handling.

### U-05 — nine files missing a closing brace
**Severity: low. No behaviour change.** The engine tolerates a truncated final block.

`common/ideas/npt_Soviet.txt`, `npt_italy.txt`, `npt_Austro-hungary.txt`, `common/scripted_triggers/npt_culture_scripted_triggers.txt`, `history/units/GDC_1917.txt`, `history/states/{1027-Basilicata,1028-Molise,1031-Liguria,1033-Friuli}.txt`.

### U-06 — seven files with an orphan closing brace
**Severity: low. No behaviour change.** The engine ignores a stray `}` at top level.

Six copied country templates (`BIA`, `CBV`, `BAR`, `SOK`, `ZIM`, `KAT` — all identical, line 34) and `Transcaspian_government.txt` line 1284.

### U-07 — four malformed colour codes
**Severity: cosmetic.**

`work_in_progress`, `no_good_idea` and `rcw_country_asks_foreing_help` in `npt_other_l_russian.yml` ended with a bare `§` rather than the reset token `§!`. `RVA_convening_military_council_prompt` in `npt_RVA_focuses_l_russian.yml` had `50%§.` — a `§` with no code after it.

---

## Not fixed

### N-01 — 119 ideas use `picture = GFX_idea_<name>` — **RESOLVED: not a defect**
**Status: closed 2026-08-08, once vanilla was available.**

All 119 resolve. **hoi4skill's 119 errors were false positives.**

The engine has a **verbatim fallback**: when `GFX_idea_<picture>` does not exist it uses `<picture>` directly as a sprite name. Vanilla relies on this in 20 of its own ideas — for example `picture = GFX_idea_CHI_air_force`, where `GFX_idea_GFX_idea_CHI_air_force` does not exist but `GFX_idea_CHI_air_force` does.

Checked against 29,629 sprite declarations across vanilla and the mod: 119 of 119 resolve. The mod is stylistically inconsistent (3,244 ideas use the bare form) but not broken.

### N-05 — idea pictures resolving to no sprite — **PARTIALLY FIXED**
**Reported by `tools/ror_lint.py` as `R008`. 76 uses → 27.**

Originally 76 uses across 50 distinct values.

**Fixed** in `interface/ror_fork_icons.gfx` (additive — no upstream file touched):

- **23 values whose `.dds` was already on disk with no spriteType.** The art shipped but was never declared, so the idea rendered with a missing icon. `GFX_CPG_vivox_resyrs_1/2`, `GFX_POL_agitation_fascism`, `Vasil_Zaharko`, `red_new_army` (20 uses on its own) and others.
- **4 misspelled references to sprites that exist in vanilla**, aliased rather than corrected at the call site so no upstream file changes: `mex_callistas` → `MEX_callistas`, `generic_oppresion` → `generic_oppression`, `idea_generic_war_preparation` (doubled prefix), `yug_orthodox_church_support` → `YUG_orthodox_church_support`.

**Still open — 27 uses, all genuinely lacking artwork.** Two of these look like substitutions rather than typos and are left as owner judgement calls, since choosing a different icon changes meaning:

- `generic_pp_stability_bonus` (5 uses) — nearest vanilla sprite is `generic_pp_unity_bonus`, which is a different concept.
- `foodstuffs_supply_crisis` — vanilla has `_4` and `_5` variants but no unsuffixed one.

The rest (`GFX_RSS_*`, `NVA_white_propaganda_no_ns`, `BLR_*`, `Helium_Belkind`, `Vasil_Zaharko` siblings) need art.

Note the check must allow two engine behaviours or it reports ~1,600 phantom findings: the verbatim fallback above, and **graphical-culture variants** — generic advisor portraits are declared as `GFX_idea_<name>_russian_2d`, `_western_european_2d` and so on, with the suffix chosen at runtime, so a bare `<name>` resolves through any of them. That accounts for 1,059 uses of `min_random_generic_icon_N` alone.

Note the check must allow two engine behaviours or it reports ~1,600 phantom findings: the verbatim fallback above, and **graphical-culture variants** — generic advisor portraits are declared as `GFX_idea_<name>_russian_2d`, `_western_european_2d` and so on, with the suffix chosen at runtime, so a bare `<name>` resolves through any of them. That accounts for 1,059 uses of `min_random_generic_icon_N` alone.

### N-06 — focus icons resolving to no sprite — **PARTIALLY FIXED**
**Reported as `R007`. 14 → 10.**

**Fixed:**

- **`GFX_ggoal_generic_air_fighter2`** (`USA_npt.txt:2317`) — a one-character typo for vanilla's `GFX_goal_generic_air_fighter2`. Corrected at the call site; logged in `upstream-touches.md`.
- **3 with art but no declaration** — `GFX_BLR_sovmest_zased`, `GFX_BLR_razvit_obrz`, `GFX_BLR_otkr_gos_univer`, all with `.dds` files under `gfx/interface/goals/LitBlr/`. Declared in `interface/ror_fork_icons.gfx`.

**Still open — 10 uses, no artwork anywhere:** `GFX_z_goal_rabgosudarstvo`, `GFX_z_goal_socmilirarism` (probably meant `socmilitarism`, but neither exists), `GFX_z_goal_permrevolt`, `GFX_BLR_pazvernut_vneshn_polit`. These affect the shared socialist branch in `generic_shared_npt.txt`, so they are visible on several countries.

### N-03 — `FIN_republic` and `FIN_ASK_94` deadlock each other
**Status: unresolved, needs a design decision.** `common/national_focus/Finland_npt_new.txt:451,694`

`FIN_republic` requires `FIN_ASK_94` **and** `FIN_finland_with_antanta` (two AND-ed prerequisite blocks). `FIN_ASK_94` requires `FIN_republic`. Neither focus can ever be completed.

Both also lack a `completion_reward`, so they read as unfinished rather than mis-wired. Fixing this means choosing which edge to cut, which is a design call, not a mechanical one — left for the owner.

This is the only prerequisite cycle in all 2,628 focuses.

### N-04 — 149 focuses have no localisation key
**Status: unresolved, content work.**

Of 2,628 focuses across 81 trees, 149 have no entry in `localisation/russian/`. In game they render as their raw id (`AUH_ITA_puppet`, `DON_commune`, `FIN_border_fin_sov`, …).

A further 219 have a title but no `_desc`.

These are frozen in `tools/upstream-baseline.json`. Writing the missing Russian text is real content work and belongs in a change of its own, not in a mechanical pass.

### N-02 — `hoi4skill` false positives
**Status: tool defect, no action in this repo.**

Recorded so nobody re-investigates:

- **Paired icon markers.** `£victory_points£` is valid and vanilla uses it. hoi4skill reads the closing `£` as a new empty marker and reports "icon marker has no icon name". It flags all 37 paired forms in this mod and none of the 208 unpaired `£command_power` forms.
- **Colour nesting.** Its `§`/`§!` balance check assumes strict nesting the engine does not require.
- **Focus geometry.** 1,082 of its 1,439 errors are "missing `relative_position_id`" / "uses `relative_position_id`". Absolute `x`/`y` is legal HOI4. This is its own generator's house style, not a correctness rule.

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

### N-01 — 117 ideas use `picture = GFX_idea_<name>`
**Status: unresolved, needs vanilla files.**

HOI4 resolves an idea's `picture` by prepending `GFX_idea_`, so `picture = GFX_idea_X` asks for the sprite `GFX_idea_GFX_idea_X`. Neither that name nor the bare `GFX_idea_X` is defined anywhere in the mod's 29 `.gfx` files.

The mod is inconsistent: elsewhere it uses the correct bare form (`picture = generic_naval_manufacturer_1`).

Either these 117 ideas have broken icons, or the sprites resolve from vanilla and the engine's fallback covers it. **This cannot be settled without `$HOI4_VANILLA_ROOT`.** Revisit once vanilla files are in place — it is the single largest open correctness question in the mod.

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

# Upstream touch register

Every edit to a file that came from `Gtym33/Kursach-Himiya` is recorded here, with file, reason and date. **This register is consulted before every upstream sync** — it is the list of expected conflict sites.

New content belongs in new `ror_fork_*` files (see `AGENTS.md` §3). An entry here means the additive route was not available.

| Date | File | Lines | Reason | Behaviour change? |
|---|---|---|---|---|
| 2026-08-08 | `common/national_focus/USA_npt.txt` | 2265–2266, EOF | Removed two orphan `}` that closed `focus_tree` at line 2265; moved the tree's close to EOF. | **Yes** — see defect U-01 |
| 2026-08-08 | `common/national_focus/USA_npt.txt` | 2317 | `GFX_ggoal_generic_air_fighter2` → `GFX_goal_generic_air_fighter2`; one-character typo, vanilla has the corrected name. | Icon now renders |
| 2026-08-08 | `common/national_focus/Transcaspian_government.txt` | 1284 | Removed a single orphan `}` after the last `shared_focus`. | No |
| 2026-08-08 | `common/ideas/npt_Soviet.txt` | EOF | Added the missing `}` closing `ideas`. | No |
| 2026-08-08 | `common/ideas/npt_italy.txt` | EOF | Added the missing `}` closing `ideas`. | No |
| 2026-08-08 | `common/ideas/npt_Austro-hungary.txt` | EOF | Added the missing `}` closing `ideas`. | No |
| 2026-08-08 | `common/scripted_triggers/npt_culture_scripted_triggers.txt` | EOF | Added the missing `}` closing `is_natural_core_territory_of_PREV`. | No |
| 2026-08-08 | `events/Turkey.txt` | 1411, 1476 | Closed the `CONTROLLER = { ... }` block in `turkey.29` and `turkey.30`. | **Yes** — see defect U-02 |
| 2026-08-08 | `history/countries/BIA - Biafra.txt` | 34 | Removed orphan `}`. | No |
| 2026-08-08 | `history/countries/CBV - Cabo Verde.txt` | 34 | Removed orphan `}`. | No |
| 2026-08-08 | `history/countries/BAR - Barotseland.txt` | 34 | Removed orphan `}`. | No |
| 2026-08-08 | `history/countries/SOK - Sokoto.txt` | 34 | Removed orphan `}`. | No |
| 2026-08-08 | `history/countries/ZIM - Zimbabwe.txt` | 34 | Removed orphan `}`. | No |
| 2026-08-08 | `history/countries/KAT - Katanga.txt` | 34 | Removed orphan `}`. | No |
| 2026-08-08 | `history/countries/QIN - Qing.txt` | 38 | Removed a stray `}` that closed the `1914.1.1` block early. | **Yes** — see defect U-03 |
| 2026-08-08 | `history/states/1027-Basilicata.txt` | EOF | Added the missing `}` closing `state`. | No |
| 2026-08-08 | `history/states/1028-Molise.txt` | EOF | Added the missing `}` closing `state`. | No |
| 2026-08-08 | `history/states/1031-Liguria.txt` | EOF | Added the missing `}` closing `state`. | No |
| 2026-08-08 | `history/states/1033-Friuli.txt` | EOF | Added the missing `}` closing `state`. | No |
| 2026-08-08 | `history/units/GDC_1917.txt` | EOF | Added the missing `}` closing `units`. | No |
| 2026-08-08 | `history/units/PRM_contra_2.0.txt` | 65 | Closed an unterminated string literal. | **Yes** — see defect U-04 |
| 2026-08-08 | `localisation/russian/npt_other_l_russian.yml` | 36–38 | `§` → `§!` on three dangling colour codes. | No |

## Conflict risk

All 21 edits are one or two characters. If upstream touches the same regions, expect small, easily-resolved conflicts. Nothing was reformatted, reordered or tidied.

Four entries change in-game behaviour. Those are described in [known-upstream-defects.md](known-upstream-defects.md) so a future reader does not mistake them for cosmetic.

# Content coverage

A snapshot to inform Track A design sessions (plan §5.1: *"Claude reads the dashboard for thin countries and periods"*). Regenerate the numbers with `tools/build_graph.py`; the judgements below are editorial and go stale.

Snapshot taken at `dae20b95f`, 2026-08-08. 2,628 focuses, 81 trees, 40 countries with a tree, 421 tags defined.

---

## The mod's centre of gravity

RUS, RSS, RSR, CCA and DON together hold **479 focuses — 18% of the mod**, and they are not five countries. They are rival claimants to the same Russia, which is the mod's actual subject.

Best-served: BLR 191 (4 sub-trees), LIT 160, USA 153, DON 148, RSS 132, RUS 108, OCH 105, CPG 105, CCA 97, RSR 94.

## Where the gaps are

| Region | Tags | Trees | Note |
|---|---|---|---|
| **Central Asia** | 14 | **0** | Basmachi, Turkestan Autonomy, Bukhara, Khiva, Kokand — nothing at all |
| **Caucasus** | ~21 | **1** | Only MRC, and it is 3 focuses. No Georgia, Armenia, Azerbaijan |
| **Siberia / Far East** | ~26 | 1 | Only SIB (45). No Far Eastern Republic, the actual 1920–22 buffer state |
| **Baltic** | 3+ | 1 | LIT has the mod's largest tree at 160; EST and LAT have zero |
| **Cossack hosts** | 8 | 6 | Astrakhan and Semirechye missing |
| **Ukraine** | — | 4 | Well covered: UKR, FRT, DNB, GAL |

## Period is not encoded, and cannot be derived

Plan v2 §8 expected to derive a focus's period from "spec + `available` date triggers". **The date-trigger half does not work here**: there are **8 date comparisons in all 81 focus files**, and `available_from` resolves for 3 of 2,628 focuses.

This is not an extractor defect. RoR gates availability by *prerequisite*, not by date. Period therefore has to come from the OpenSpec change folder, and a new branch should state its intended window there rather than assume the graph can infer it.

The one chronological gap that is real and visible another way: **every faction tree stops at the civil war.** SOV has a history file but no tree of its own, and the post-unification economy branches are commented out in `Russia_Bolsheviks.txt` (lines 2614–2622: `SOV_start_pos_planed_economy`, `..._new_economic_policy_economy`, `..._cooperative_workers_economy`). If the Reds win, the content ends.

## Thin trees

Mean completeness across the mod is 0.675. The `documented` criterion is true for 0.3% of focuses and depresses everything roughly equally, so compare trees against each other rather than against 1.0.

| Tree | Focuses | Mean completeness |
|---|---|---|
| `generic_shared_npt` | 94 | 0.002 — shared template, not narrative content |
| `Russia_Republic_focus` | 21 | **0.032** — the worst real branch in the mod |
| `Russia_Provisional_Committee_of_Duma_focus` | 14 | 0.198 |
| `Austro_Hungary_focus` | 72 | 0.375 — large but badly unfinished for its size |
| `Mountainous_Republic_of_the_Northern_Caucasus_focus` | 3 | 0.407 |
| `Lithuanian_Belarusian_Republic` | 49 | 0.435 |

## Orphaned content

Four trees resolve to no country:

- **`New_file` — `common/national_focus/Finland_npt_new.txt`, 59 focuses.** An abandoned work-in-progress, never wired to a country selector, so none of it is reachable. This is also where defect **N-03** lives — the `FIN_republic` / `FIN_ASK_94` prerequisite deadlock. The deadlock is not a mystery bug; it is unfinished work. Meanwhile the live `Finland_focus` has only 7 focuses, for a country that fought a well-documented 1918 civil war.
- `Salvation_Army_civil_war_focus` — 2 focuses.
- `generic_shared_npt` (94) and `generic_political_shared` (1) — shared templates, correctly countryless.

## Candidates for the next branch

Editorial, not computed. Ordered by how badly the gap contradicts the mod's own premise.

1. **Transcaucasia — Georgia, Armenia, Azerbaijan.** Twenty-one Caucasus tags and a 3-focus stub. The most historically legible post-Empire breakaways after the Baltics.
2. **Estonia and Latvia.** The starkest internal inconsistency: same theatre and same 1918–20 independence war as Lithuania, which has the largest tree in the mod.
3. **Far Eastern Republic**, plus the Astrakhan and Semirechye hosts. Extends systems that already work rather than inventing new ones.
4. **Central Asia — Bukhara, Khiva, Turkestan/Kokand.** The largest single unbuilt cluster, and squarely the mod's premise.
5. **Finland.** Not a new build so much as a decision: finish and wire `New_file`'s 59 orphaned focuses, or delete them. Leaving 59 dead focuses and a deadlock in the tree is the worst of both.
6. **Post-1922 SOV.** Closes the only real chronological gap and gives the Red victory a payoff.

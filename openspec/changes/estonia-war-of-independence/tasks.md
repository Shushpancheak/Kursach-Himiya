## 1. Make Estonia exist

- [ ] 1.1 Read `design.md` and `specs/countries/estonia/spec.md` in full before writing anything. Load the `ror-focus-tree` and `ror-voice` skills.
- [ ] 1.2 Create `events/ror_fork_EST_independence.txt` with a new namespace `ror_fork_est`. Add an event keyed off the November 1918 German collapse — the same `GER_monarchy_fall` / `WWI_GER_HAS_CAPITULATED` conditions `rcw_bfk.2` uses — that transfers EST-cored states to EST, sets its politics, and loads `EST_1917`.
- [ ] 1.3 Do NOT modify `events/RussianCivilWar_BalticFinlandKarelia.txt`. `rcw_bfk.1` option B stays as it is; this change is additive.
- [ ] 1.4 Verify Estonia actually spawns in a real game: `tools/t4_boot.sh` on the server, then confirm EST exists and holds territory. **If Estonia does not spawn, stop and report — every later task is worthless without this.**

## 2. The historical spine

- [ ] 2.1 Create `common/national_focus/ror_fork_EST_independence.txt` with `focus_tree = { id = ror_fork_EST_independence }` and a country block selecting EST.
- [ ] 2.2 Build the spine from the dated table in the spec: Maapäev declares authority → independence proclaimed → German occupation → Red Army invades → Laidoner's counter-offensive → Narva retaken.
- [ ] 2.3 Use the commanders already defined in `history/countries/EST - Estonia.txt` — Laidoner, Kuperjanov, Põdder, Tõnisson, Soots. Do not invent new characters.
- [ ] 2.4 Add the Cēsis focus. It is Estonia helping Latvia against *Latvia's* Landeswehr — not a war against Estonia's own Baltic Germans.
- [ ] 2.5 Gate the tree with `has_start_date` so it behaves correctly from all three bookmarks (`1917.1.1`, `1917.11.8`, `1918.8.6`).

## 3. Fork one — April 1919

- [ ] 3.1 Add the Hungarian mediation offer as a focus or event choice.
- [ ] 3.2 Accepting early peace must materially reduce Entente support — Cowan's threat to withdraw the Royal Navy was real and the loss must be felt, not cosmetic.
- [ ] 3.3 Declining keeps Entente backing and opens the route toward fork two.

## 4. The land question

- [ ] 4.1 Add the Land Reform Act focus, dated 10 October 1919, on the war spine rather than as a peacetime policy.
- [ ] 4.2 Uncompensated reform: resolve `landlordism`, bind the peasantry, reduce the domestic communist threat, and damage the Baltic German contribution to the war effort.
- [ ] 4.3 Compensated reform: retain capacity and the minority bloc's loyalty, at the cost of weaker redistribution and a larger communist threat.
- [ ] 4.4 Neither option may be strictly better than the other. If one dominates in play, rebalance and say so in the report.

## 5. Fork two — August 1919

- [ ] 5.1 Add the Bolshevik offer: recognition in exchange for withdrawal from Pskov.
- [ ] 5.2 Add the Yudenich alternative: back the Petrograd offensive alongside the North-Western Army.
- [ ] 5.3 Make the two mutually exclusive, declared symmetrically on both focuses.
- [ ] 5.4 Wire the Tartu branch to the fate of the interned North-Western Army — Estonia disarms it, the NWA is materially weakened, Estonia's negotiating position improves.
- [ ] 5.5 Give Estonia a response to `NWA_ultimatum_baltic_countries` so the NWA player is answered rather than obeyed.
- [ ] 5.6 The Petrograd bet must be able to fail. The White promise was hollow — "Russia one and indivisible" was never abandoned — and a successful offensive should not straightforwardly guarantee Estonian independence.

## 6. Endings

- [ ] 6.1 Land the branches on distinct ideologies using leaders already defined for EST — Päts (despotism), Anvelt (leninism), Tõnisson (market liberalism), Pitka (social liberalism), Strandman (social democracy / anarchist communism).
- [ ] 6.2 Where a branch changes Estonia's name or flag, use existing art: `EST_labor_commune`, `EST_sovrep`, `EST_socsovrep`, `EST_FIN_*`. Request new art only if nothing fits.
- [ ] 6.3 Treaty of Tartu is the historical completion state.

## 7. Localisation

- [ ] 7.1 Create `localisation/russian/ror_fork_EST_independence_l_russian.yml`, UTF-8 **with BOM**, header `l_russian`.
- [ ] 7.2 Load `ror-voice` and use the `baltic-national` register from `style/matrix.yaml`. Read the caution in that cell — Estonia is not a detached foreign observer.
- [ ] 7.3 Every focus needs both `<id>` and `<id>_desc`.
- [ ] 7.4 Flag any text you could not pitch confidently, rather than falling back to flat neutral prose. The owner reviews all flavour text.

## 8. Validation and reporting

- [ ] 8.1 `tools/ror_lint.py --baseline tools/upstream-baseline.json` must be clean.
- [ ] 8.2 `tools/build_graph.py` — confirm the focuses appear, positions resolve, completeness is as expected, and `unspecified_fork_content` does not grow.
- [ ] 8.3 `tools/t4_boot.sh` — no new runtime errors attributable to this change.
- [ ] 8.4 Write `docs/estonia-independence.md`: what the tree does, how it interacts with the NWA content, and every icon it needs.
- [ ] 8.5 Report with a `Simplifications, omissions, and blockers` section. If there were none, say so explicitly with evidence.

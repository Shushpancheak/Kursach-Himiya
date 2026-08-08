## Why

The mod already contains the Russian half of the Estonian story and none of the Estonian half. `Russia_Northwestern_army.txt` lets Yudenich's army issue `NWA_ultimatum_baltic_countries`, remove the Latvian government, and impose a `NWA_baltic_principality` — and Estonia has no focus tree with which to answer any of it. A 4,349-line event file narrates the Baltic war in detail; Estonia experiences all of it and steers none of it.

Historically the relationship ran the other way. Estonia hosted Yudenich's North-Western Army, then disarmed and interned it in November 1919 and signed the Treaty of Tartu with Soviet Russia, trading the White cause for recognition of its independence. The small state decided the northern theatre. The mod currently cannot represent that.

This is also the mod's starkest internal inconsistency: Lithuania has the largest tree in the mod at 160 focuses; Estonia and Latvia have zero, in the same theatre and the same war.

## What Changes

- A new Estonian national focus tree covering **November 1917 to February 1920** — the Maapäev's declaration of authority through to the Treaty of Tartu. The interwar period, the Vaps movement and the 1934 Päts coup are **out of scope** for this change.
- Estonia gains agency over events that currently happen to it: the April 1919 Entente-versus-early-peace fork, the August 1919 fork where both Moscow and Yudenich bid for Estonian cooperation, the land reform, and the fate of the interned North-Western Army.
- **BREAKING for the NWA player**: `NWA_ultimatum_baltic_countries` and the Petrograd offensive acquire a counterparty that can refuse, bargain or betray. A White run through the north-west will no longer be uncontested.
- Estonia's release must become reliable. Today it exists only if Russia takes `rcw_bfk.1` option B, which the AI weights `999` against `0`. A tree for a country that never spawns is dead content.
- Localisation in Russian for every new focus and event, per the fork's Russian-only rule.

Explicitly **not** in this change: Latvia, a shared Baltic tree, the interwar period, and any global balance adjustment.

## Capabilities

### New Capabilities

- `countries/estonia`: what the Estonian focus tree must represent — how Estonia comes into existence, the historical spine from the Maapäev to Tartu, the branch points where the player's choice diverges from history, and how those branches interact with the existing North-Western Army content.

### Modified Capabilities

None. The change is additive and works within `focus-trees`, `localisation`, `political-spectrum`, `scenario` and `custom-mechanics` as they stand. It is a first exercise of those specs rather than a revision of them.

## Impact

- **New files**: `common/national_focus/ror_fork_EST_independence.txt`, `localisation/russian/ror_fork_EST_*_l_russian.yml`, `events/ror_fork_EST_independence.txt` if the tree needs events of its own, `docs/estonia-independence.md`.
- **Upstream files touched**: expected to be one — the release path in `events/RussianCivilWar_BalticFinlandKarelia.txt`. Minimal mechanical edit, logged in `docs/upstream-touches.md`. If it can be avoided entirely, it should be.
- **Risk**: the tree is only as good as its Russian prose, and no automated tier can check that. Flavour text goes to owner review before merge.

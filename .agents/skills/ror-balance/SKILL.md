---
name: ror-balance
description: Track B Lane B2 only — global world-state balance for the 1917+ timeframe, telemetry thresholds, and the world-iteration gate. Load before proposing or implementing any global balance change.
---

# ror-balance

**Lane B2 only.** Additive content is Lane B1 and does not need this skill. The two never share a PR.

Lane B2 covers world-state maintenance for a timeframe vanilla was never designed for: global division counts, political power accumulation, manpower and population drift, AI stagnation across 1917–1945.

## The governing fact

**These changes are not reviewable by reading a diff.** A three-line edit to a weekly script can reshape the entire world by 1936. The only evidence that counts is a before/after telemetry pair.

Consequences:

- **One change per PR.** Batch two and a regression cannot be attributed.
- **No fixed cadence.** It ships when the numbers say so, which may be never.
- A baseline telemetry run and a candidate run are both required. Without them there is nothing to review and the change does not ship.

## The world-iteration gate — hard stop

`on_weekly`, `on_daily`, `on_monthly` and similar on-actions **iterate over every country by default**. That is exactly what a global balance change reaches for first, and in a mod spanning 1917–1945 it is a performance catastrophe.

- `on_daily_TAG` and other narrowly-scoped variants: **allowed freely.**
- Anything world-iterating: **stop and request explicit owner approval before implementing.** Not a warning. Not a lint. A hard halt, and you report it as a blocker rather than working around it.

Where iteration is genuinely needed:

1. Try MTTH-weighted or event-driven approaches first.
2. Centralise every tuning value in `common/script_constants/ror_fork_<subsystem>.txt`. Never magic numbers — the whole point is that the owner can retune in one place after seeing telemetry.
3. Scope as narrowly as the mechanic allows: `any_country` with a tight trigger beats iterating everything.

## Telemetry

Gated on spikes S1 (headless HOI4 on the server) and S4 (savegame parsing). **Neither is resolved**, so Lane B2 is currently blocked. Say so plainly rather than shipping a balance change without evidence.

When it exists: observer mode under Xvfb, fast-forward, autosave at 1920/1925/1930/1936/1940/1945, melt and parse each save, emit `metrics.json`, assert against `telemetry/thresholds.yaml`.

Metrics: total world divisions; per-country divisions; PP stockpile (max, p95); manpower; civilian and military factories; independent countries surviving; major-war participation; faction sizes; **and game tick time**.

**Tick time is not optional.** A balance script that produces perfect numbers and halves the game speed is a failure, and it is a failure that no world-state metric will show you.

Thresholds are set **from observed baseline values, not guessed**. A threshold invented before the first baseline run is noise.

Telemetry runs are long and consume compute rather than model quota, so they are scheduled separately from content runs and sit **outside** the 80% budget gate.

## Reporting

State the hypothesis, the metric that would falsify it, the baseline numbers, the candidate numbers, and the tick-time delta. "Balance was adjusted" is not a report. If the numbers did not move, say so — a change with no measurable effect is a change to drop, not to ship.

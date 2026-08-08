---
name: ror-event-chain
description: Write or edit HOI4 events in the RoR fork — namespaces, ids, triggers, options, event targets, wiring into focuses and on_actions. Load before touching anything in events/.
---

# ror-event-chain

Load before editing anything in `events/`.

## Before writing

1. Read `$PARADOX_WIKI/Event modding - Hearts of Iron 4 Wiki.md`.
2. Read `$HOI4_VANILLA_ROOT/documentation/effects_documentation.md` and `triggers_documentation.md`. These are **more authoritative than the wiki** — consult both.
3. Find an RoR precedent. `events/RussianCivilWar_Bolsheviks.txt` is a good model for a civil-war chain.
4. Load `ror-voice`.

## File placement

New events go in `events/ror_fork_<theme>.txt`. Never append to an upstream event file when a new one will do.

## Shape

```
add_namespace = ror_fork_example

country_event = {
	id = ror_fork_example.1
	title = ror_fork_example.1.t
	desc = ror_fork_example.1.d
	picture = GFX_report_event_generic

	is_triggered_only = yes

	option = {
		name = ror_fork_example.1.a
		ai_chance = { factor = 10 }
		add_political_power = 25
	}
	option = {
		name = ror_fork_example.1.b
		ai_chance = { factor = 1 }
		add_stability = -0.05
	}
}
```

**The namespace must match the id prefix.** `add_namespace = lithuania` with events called `lithuania.1` — a mismatch is a real defect and upstream has 128 of them in one file.

**Every event needs either `is_triggered_only = yes` or a `mean_time_to_happen`.** Without one it never fires, or fires immediately and constantly. Upstream has 43 events missing both.

**Every option needs a `name`.** An unnamed option renders blank.

## Triggers and scope

The most common structural mistake in this repo — and the cause of two genuinely inert upstream events — is an **unclosed nested block inside `trigger`**. When `CONTROLLER = { OR = { ... }` loses its brace, `trigger` never terminates, and `mean_time_to_happen`, `fire_only_once` and `option` are silently parsed *as part of the trigger*. The event then does nothing, and every reference check still passes. See U-02 in `docs/known-upstream-defects.md`.

T1 catches this as `S001`. Run it.

## Event targets

- `save_event_target_as` for short-lived chains. Clears itself when the effect chain ends, but carries into events fired from that chain.
- `save_global_event_target_as` **only** when persistence beyond one chain is genuinely needed. It does not auto-clear and **must** be paired with `clear_global_event_target`. T1 reports unpaired saves as `E004`.
- Use as a scope with `event_target:my_target`. In localisation, drop the prefix: `[my_target.GetName]`.

## Wiring

An event that exists but is never fired is dead content. It must be reachable from one of:

- a focus `completion_reward` (`country_event = { id = ... days = ... }`)
- a decision
- an `on_action`
- another event's option
- its own `mean_time_to_happen` plus `trigger`

**Check reachability explicitly before claiming completion.** `tools/build_graph.py` records `linked_events` per focus, which covers the focus route only.

## Chain integrity

For a multi-event chain, walk it end to end and confirm:

- every branch terminates — no event whose every option leads nowhere
- no loop that can fire indefinitely without a `fire_only_once` or a flag guard
- flags set by one event are read by the next, and cleared when the chain ends
- a player who takes the least-likely option at every step still reaches an ending

## World-iterating on-actions

`on_weekly`, `on_daily`, `on_monthly` and similar **iterate over every country**. `on_daily_TAG` and other narrowly-scoped variants are fine.

Anything world-iterating: **stop and ask the owner before implementing.** This is a hard gate, not a warning. See `AGENTS.md` §9.1.

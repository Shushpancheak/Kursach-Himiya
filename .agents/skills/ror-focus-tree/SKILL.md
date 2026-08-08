---
name: ror-focus-tree
description: Create or edit HOI4 national focus trees in the RoR fork — focus geometry, prerequisites, mutual exclusivity, AI weights, icons, rewards and completion standards. Load before touching any file in common/national_focus/.
---

# ror-focus-tree

Load before editing anything in `common/national_focus/`.

The mod currently has **2,628 focuses across 81 trees**. Run `tools/build_graph.py --no-blame` for the current picture; never work from a count in a document.

## Before writing

1. Read `$PARADOX_WIKI/National focus - Hearts of Iron 4 Wiki.md`.
2. Read the vanilla precedent: `$HOI4_VANILLA_ROOT/common/national_focus/`.
3. **Find an RoR precedent and mirror it.** RoR's conventions beat vanilla's where they differ. `common/national_focus/Russia_Bolsheviks.txt` and `Don_white_cossaks.txt` are good models.
4. Load `ror-voice` — every focus needs a name and a description.

## File placement (C7)

New trees go in a **new file**: `common/national_focus/ror_fork_<TAG>_<branch>.txt`.

Extending an existing tree: prefer `shared_focus` so the change stays additive. Editing an upstream file at all means a **minimal mechanical edit** and an entry in `docs/upstream-touches.md`.

## Structure that matters

```
focus_tree = {
	id = ror_fork_<tag>_<branch>
	country = { factor = 0 modifier = { add = 10 tag = SOV } }
	focus = {
		id = SOV_example
		icon = GFX_goal_generic_demand_territory
		x = 4
		y = 2
		cost = 10
		prerequisite = { focus = SOV_first focus = SOV_second }
		prerequisite = { focus = SOV_third }
		mutually_exclusive = { focus = SOV_other }
		available = { has_country_flag = something }
		completion_reward = { add_political_power = 50 }
		ai_will_do = { factor = 1 }
	}
}
```

**Prerequisite semantics — get this right or everything downstream lies.** Multiple `prerequisite = { }` blocks are **AND**-ed. `focus =` entries *within* one block are **OR**-ed. The example above means `(first OR second) AND third`.

Consequences worth internalising:
- Two options inside one block being mutually exclusive is the ordinary "branches converge here" pattern. Perfectly reachable.
- Two *separate* blocks whose contents are mutually exclusive make the focus **unreachable**. T1 reports this as `G003`.

**Mutual exclusivity must be symmetric.** If A excludes B, B must exclude A. T1 reports asymmetry as `G001`.

## Geometry

`x`/`y` are grid cells. `relative_position_id` anchors a focus to another, and offsets stack along the chain. Absolute coordinates are perfectly legal — `hoi4skill` disagrees, and it is wrong about this.

T1 resolves the whole chain and reports collisions as `Y002`. Two focuses in the same visual cell overlap in game.

## Completion standards

A focus is not done because it appears in the tree. Required:

| Requirement | Checked by |
|---|---|
| Localisation key | T1 `R005` |
| `_desc` key | T1 `R006` |
| `icon` that resolves | T1 `R007` |
| Non-trivial `completion_reward` | T1 `P001` |
| `ai_will_do` | T1 `P002` |
| Prerequisites resolve | T1 `R003` |
| No cycles | T1 `G002` |
| Entry in `docs/` | graph `checklist.documented` |

An empty `completion_reward = { }`, or one holding only a `custom_effect_tooltip`, counts as trivial. Upstream has 66 of them; do not add more.

**Reward variety.** A branch where every focus is `add_political_power` is a branch nobody enjoys. Mix research bonuses, ideas, decisions unlocked, events fired, manpower, state modifiers, diplomatic effects. Vary the shape, not just the number.

**`ai_will_do` is not optional decoration.** Without it the AI treats the focus as weight 1 and picks it at random. If a branch is meant to be taken by an AI in a specific situation, weight it for that situation.

## Icons

Declare in `interface/*.gfx` as `name = "GFX_focus_..."` with a `texturefile`. **Copy a placeholder sprite from vanilla that matches the new definition** so the game loads without missing-sprite errors and final art drops in cleanly later. List every icon needed in the mechanic's `docs/` file.

## Before claiming completion

1. `tools/ror_lint.py --baseline tools/upstream-baseline.json` — must be clean.
2. `tools/build_graph.py` — check your focuses appear, positions resolve, completeness is what you expect.
3. Spawn the focus-tree auditor with `fork_context=false`.
4. Report depth, reward variety and route coverage honestly. A tree that is wide and shallow is a finding, not a delivery.

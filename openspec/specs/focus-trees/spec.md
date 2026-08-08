## Purpose

Focus trees are how RoR tells its story: 2,628 focuses across 81 trees carry the alternate histories a player actually experiences. This capability defines what a focus tree in this fork must be, so that a new branch is judged against a standard rather than against whatever the last one happened to do.

## Requirements

### Requirement: Prerequisite structure is AND-of-OR and is preserved

Multiple `prerequisite = { }` blocks are AND-ed together. `focus =` entries within a single block are OR-ed. This distinction is load-bearing: it determines reachability, and both the lint and the dashboard's arrows depend on reading it correctly.

#### Scenario: Branches that converge

- **WHEN** two mutually exclusive focuses both lead to a later focus
- **THEN** they appear as alternatives inside one `prerequisite` block
- **AND** the later focus is reachable from either route

#### Scenario: A focus that cannot be reached

- **WHEN** two separate `prerequisite` blocks require focuses that are mutually exclusive with each other
- **THEN** the focus is unreachable and the change is rejected
- **AND** T1 reports it as `G003`

#### Scenario: Circular prerequisites

- **WHEN** a focus is a prerequisite of one of its own prerequisites
- **THEN** neither can ever be completed and the change is rejected
- **AND** T1 reports it as `G002`

### Requirement: Mutual exclusivity is symmetric

If A excludes B then B excludes A. A one-sided declaration lets a player take both.

#### Scenario: One-sided exclusivity

- **WHEN** a focus declares `mutually_exclusive` against a focus that does not declare it back
- **THEN** T1 reports `G001` and the missing side is added

### Requirement: A focus is not finished until it is wired

Appearing in the tree is not completion. A focus is complete when it has a localised name and description, an icon that resolves, a non-trivial `completion_reward`, an `ai_will_do`, and an entry in `docs/` for any mechanic it introduces.

An empty `completion_reward = { }`, or one containing only a `custom_effect_tooltip`, is a placeholder.

#### Scenario: A branch is proposed as complete

- **WHEN** a change claims a focus branch is done
- **THEN** every focus in it satisfies the checklist above
- **AND** `tools/build_graph.py` reports the expected completeness for those focuses
- **AND** any shortfall is listed under "Simplifications, omissions, and blockers"

#### Scenario: Reward variety

- **WHEN** a branch's focuses all grant the same kind of reward
- **THEN** that is a finding, not a delivery
- **AND** the branch is reworked to vary its effects across research, ideas, decisions, events, manpower and diplomacy

### Requirement: New trees are additive

New content goes in new files under the `ror_fork_` prefix. Extending an existing tree prefers `shared_focus`. Editing an upstream file requires a minimal mechanical edit and an entry in `docs/upstream-touches.md`.

#### Scenario: A new country branch is added

- **WHEN** a change adds a focus tree for a country
- **THEN** it creates `common/national_focus/ror_fork_<TAG>_<branch>.txt`
- **AND** no upstream focus file is modified

### Requirement: Geometry does not overlap

Grid positions resolve through `relative_position_id` chains. Two focuses in the same resolved cell overlap on screen. Absolute `x`/`y` is legal and is used widely in this mod.

#### Scenario: Two focuses share a cell

- **WHEN** resolved coordinates collide within a tree
- **THEN** T1 reports `Y002` and the layout is corrected

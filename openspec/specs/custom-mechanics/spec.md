## Purpose

RoR carries a dozen bespoke systems built on scripted GUIs, variables and dynamic modifiers — internal party struggles, regional insurgency trackers, political spectra. New content is expected to plug into the relevant system rather than reinvent or bypass it, because a focus that quietly ignores the Central Committee or the Sejm meter breaks the fiction those systems exist to tell.

## Requirements

### Requirement: New content integrates with the existing system for its subject

Before building a mechanic, check whether one already models that subject. The major systems, all verified present:

| System | Models | Entry point |
|---|---|---|
| Soviet Power / Central Committee | Bolshevik internal party democracy, seats across decist/left/centre/moderate/right | `common/scripted_effects/npt_SOV_soviet_power.txt` |
| GEN political spectrum | Reusable five-axis constitutional position for any country | `common/scripted_effects/npt_GEN_scripted_effects.txt` |
| RSS/SR party antagonism | Socialist-Revolutionary internal struggle | `common/decisions/npt_RSS_esser_struggle.txt` |
| Ural struggle | Hidden Volga/Ural/Siberia insurgency levels and Cheka checks | `common/scripted_guis/npt_RCW_ural_struggle_scripted_gui.txt` |
| Sejm antagonism | Polish parliamentary tension, 0–1 | `common/scripted_guis/npt_POL_polsky_seim.txt` |
| Red alert | Global fear-of-communism meter, weighted by size of countries turning | `common/scripted_guis/npt_red_alert.txt` |
| Country unification | Two countries merging into a third, blending popularities | `common/scripted_effects/npt_uniting_of_countries.txt` |
| NVA underground | Multi-city conspiracy with per-city success odds | `common/scripted_effects/npt_NVA_scripted_effects.txt` |
| Ideological fervour tiers | Radicalism grading across every ideology | `common/scripted_triggers/npt_ministers_scripted_triggers.txt` |
| LIT pogrom escalation | Five-tier ethnic violence ladder | `common/scripted_guis/npt_LIT_narodny_pogroms_gui.txt` |

#### Scenario: A branch touches Bolshevik internal politics

- **WHEN** a change adds content about factional struggle inside the Bolshevik party
- **THEN** it moves Central Committee seats through the existing effects
- **AND** it does not introduce a parallel variable for the same concept

#### Scenario: A branch needs a constitutional position for a minor country

- **WHEN** a change models where a country sits between monarchy, republic and soviets
- **THEN** it uses the GEN spectrum rather than bespoke flags
- **AND** the resulting dynamic modifiers come from `common/dynamic_modifiers/GEN_political_modifiers.txt`

### Requirement: A new mechanic is documented before it is claimed complete

Every new mechanic gets a markdown file in `docs/` describing what it does, how it works step by step, how it interacts with existing systems, and every icon it needs — sprite location, the `.gfx` that references it, and the names used in code and localisation.

#### Scenario: A change introduces a bespoke system

- **WHEN** a change adds scripted GUI, variables or dynamic modifiers for a new mechanic
- **THEN** `docs/<mechanic>.md` is written in the same change
- **AND** placeholder sprites are copied from vanilla for each new `.gfx` entry so the game loads cleanly

### Requirement: Tuning values are centralised

Systems are tuned after observation, which only works if the numbers live in one place.

#### Scenario: A mechanic introduces thresholds or weights

- **WHEN** a change adds tunable numbers to a mechanic
- **THEN** they go in `common/script_constants/ror_fork_<subsystem>.txt`
- **AND** they are not scattered as literals through effects and decisions

### Requirement: Whole-world iteration is a hard stop

`on_weekly`, `on_daily` and `on_monthly` iterate over every country. Several of these systems are exactly the kind of thing that would reach for one.

#### Scenario: A mechanic appears to need a global tick

- **WHEN** a change would add a world-iterating on-action
- **THEN** work stops and the owner is asked before implementation
- **AND** MTTH-weighted or event-driven alternatives, and `on_daily_TAG` variants, are considered first

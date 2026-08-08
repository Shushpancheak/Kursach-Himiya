## Context

See proposal.md for motivation. The constraints that shape the approach:

- Estonia owns **no territory** at game start — all ten Estonian states are `owner = RUS`. It is a region that must become a country.
- It is already richly prepared: eight country leaders (one per ideology), six named commanders including Laidoner and Kuperjanov, `EST_1917` and `EST_1918` orders of battle, and the `landlordism` national spirit.
- A 4,349-line event file (`rcw_bfk`, 96 events) already narrates this war. The tree is a **control surface over existing events**, not a new narrative.
- `Russia_Northwestern_army.txt` acts on Estonia and cannot be answered.
- Unused assets exist and signal the original author's intent: `EST_labor_commune` (art + localisation + an event reference), `EST_sovrep`/`EST_socsovrep` (art + localisation), and `EST_FIN_*`, `EST_UGRA_*`, `EST_belarus_*` (art only).

## Goals / Non-Goals

**Goals.** A tree completable along a recognisable historical route; two real forks with costs on both sides; endings on distinct ideologies; integration with the NWA's existing focuses.

**Non-Goals.** Latvia. A shared Baltic tree. The interwar period. Any change to global balance. New art.

## Decisions

### The spine is the war, and the branches hang off two forks

```
                    Maapäev declares supreme authority  (15 Nov 1917)
                                    │
                    Independence proclaimed             (24 Feb 1918)
                    German occupation                   (Mar–Nov 1918)
                                    │
                    Red Army invades                    (28 Nov 1918)
                    Laidoner's counter-offensive        (Jan 1919)
                                    │
         ┌──────────────────────────┴──────────────────────────┐
         │             FORK ONE — April 1919                    │
         │   Hungarian mediation offered; Cowan threatens to    │
         │   withdraw the Royal Navy if Estonia accepts         │
         └──────────────────────────┬──────────────────────────┘
                    │                                  │
            take the early peace              keep the Entente
                    │                                  │
                    │                    ┌─────────────┴─────────────┐
                    │                    │   THE LAND QUESTION       │
                    │                    │   (10 Oct 1919)           │
                    │                    │ uncompensated ◄─► compensated │
                    │                    └─────────────┬─────────────┘
                    │                                  │
         ┌──────────┴──────────────────────────────────┴──────────┐
         │             FORK TWO — August 1919                      │
         │   Moscow offers recognition for withdrawal from Pskov   │
         │   Yudenich's new government also recognises Estonia     │
         │   Both bid for the same country in the same month       │
         └──────────┬──────────────────────────────┬──────────────┘
                    │                              │
        ┌───────────┴──────────┐        ┌──────────┴───────────┐
        │  TARTU               │        │  THE PETROGRAD BET   │
        │  intern the NWA      │        │  march with Yudenich │
        │  (historical)        │        │                      │
        └──────────────────────┘        └──────────────────────┘
```

### Why these two forks and not a single peace-or-war choice

Both were genuinely open, and both cost something real.

**April 1919** trades an early peace against the fleet that was supplying Estonia's rifles and holding the Gulf. **August 1919** is sharper still: the White promise was hollow. Kolchak and Yudenich never abandoned "Russia one and indivisible"; the August recognition was coerced by British pressure, not conceded. So backing Yudenich means betting Estonian lives on allies who structurally cannot deliver independence *even if they win*, against the only party actually offering recognition — the Bolsheviks. That asymmetry is the best decision in the branch.

### The land question is a betrayal of allies

Corrected during design, and it inverts the obvious framing. Estonia's Baltic Germans fought **for** Estonia — the Baltenregiment supplied 300 of 2,500 troops in January 1919. Expropriating 96.6% of large estates without compensation hit the community whose sons were in the line. Compensation was contested and deliberately deferred to 1926.

So this is not "expropriate the enemy". It is: bind the peasantry and defuse Bolshevik agitation, or keep faith with allies and keep their capital. A tree that presents it the first way has the history backwards.

### Alternate branches, ranked by how much they cost the player

| Branch | Sourced hook | What it trades away |
|---|---|---|
| **Compensated land reform** | Compensation debated in the Constituent Assembly, enacted 1926 | Peasant legitimacy and the defusing of communism |
| **The Petrograd bet** | Yudenich's Aug 1919 recognition, British-brokered | The certain, cheap peace of Tartu, for allies doctrinally opposed to your existence |
| **Estonian–Finnish Union** | Päts and Poska drafted a concrete federal memorandum, 1917–18: separate parliaments, shared president, foreign minister, war minister and army | Sovereignty. Finland is the larger partner; the seat might be Helsinki |
| **Eesti Töörahva Kommuun** | Declared in Narva 29 Nov 1918 under Anvelt; recognised only by the RSFSR | Entente recognition entirely; and it needs a large divergence to be viable at all |
| **Federal Russia** | The Maapäev majority favoured federation into late 1917 | Independence itself — only reachable early, and only against a non-Bolshevik Russia |

The **Finnish union** is the strongest alt-branch: Päts personally advocated it, it required real Estonian concessions, Finland refused for documented reasons — and the mod already contains `EST_FIN_fascism` and `EST_FIN_national_syndicalism` flag art that nothing references. The original author sketched this and stopped.

The **Commune** is the one path needing a genuinely large divergence. Sourced accounts stress it had almost no indigenous cadre — the "Estonian rifle regiments" were mostly Russian, and it was designed by Moscow as camouflage for an invasion. To be playable it needs the Royal Navy delayed or the Finnish volunteers absent, and its honest ending is absorption rather than durable Soviet Estonian statehood.

### How Estonia comes into existence — DECIDED

**A new additive event, triggered by the November 1918 German collapse.** Owner decision, 2026-08-08.

`rcw_bfk.2` already fires for Germany on `GER_monarchy_fall` and `WWI_GER_HAS_CAPITULATED`. The new event lives in `events/ror_fork_EST_independence.txt` and keys off the same collapse, releasing Estonia and loading `EST_1917` regardless of what Russia chose.

This matches the history — the Provisional Government re-emerged in the German withdrawal's vacuum and did not ask Petrograd's permission — and it keeps the change **fully additive**: no upstream file is touched.

Rejected: raising `ai_chance` on `rcw_bfk.1` (still probabilistic, so Estonia would exist in some campaigns and not others), and making emergence the tree's own first focus (a tag needs to exist before it can have a tree).

The existing `rcw_bfk.1` option B stays as-is. A Russian player who *chooses* to release Estonia early still can; this only guarantees Estonia exists when Russia does not.

**T4 must confirm Estonia actually spawns.** Nothing static can check this.

### Voice — DECIDED

**A new `baltic-national` register in `style/matrix.yaml`.** Owner decision, 2026-08-08.

Neither existing cell fits. `foreign-power` is detached and instrumental, which is wrong for a country whose own survival is the subject. `kadet-provisional` is the register of a great power dissolving, not a small nation asserting itself.

## Risks

- **Estonia never spawns.** The tree is dead content if release stays at `ai_chance = 0`. Verify with T4 before claiming completion.
- **The NWA player loses a walkover.** Intended, and worth stating: an existing playable path becomes harder.
- **Voice.** Estonia is neither a Russian faction nor a pure foreign power. `style/matrix.yaml` has no cell for it — the closest is `foreign-power`, which would make Estonia sound detached about its own survival. The implementer should propose a register and flag it for owner review rather than defaulting.
- **Scope creep into Latvia.** Cēsis is a joint battle and the pull toward building Latvia too will be strong. Out of scope.

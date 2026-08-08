## Purpose

Estonia's focus tree gives the player the decisions Estonian leaders actually faced between the Bolshevik coup and the Treaty of Tartu, in a mod that already narrates those events but lets nobody steer them.

## ADDED Requirements

### Requirement: Estonia reliably comes into existence

Today Estonia exists only if the Russian player takes option B of `rcw_bfk.1`, weighted `ai_chance = 0` against `999` for keeping it. A tree behind a country that never spawns is dead content.

Estonia's appearance must not depend on Russia's goodwill. Historically it did not: the Maapäev declared itself the supreme authority on 15 November 1917 and proclaimed independence on 24 February 1918 without asking.

#### Scenario: Estonia becomes playable in an ordinary AI game

- **WHEN** a campaign runs with Russia under AI control
- **THEN** Estonia comes into existence along the historical path
- **AND** it receives its order of battle, since `EST_1917` and `EST_1918` already exist

#### Scenario: The Russian player refuses to let Estonia go

- **WHEN** the Russian player keeps Estonia
- **THEN** Estonia's emergence becomes a contested outcome rather than being silently cancelled
- **AND** the Russian player's refusal has consequences it does not have today

### Requirement: The tree spans November 1917 to February 1920

The scope is the War of Independence. The interwar republic, the Vaps movement and the 1934 coup are out of scope.

The mod has three bookmarks — `1917.1.1`, the October Revolution `1917.11.8`, and the Smuta `1918.8.6`. The tree must state which it is reachable from and gate itself with `has_start_date` rather than assuming the earliest.

#### Scenario: A player starts from the Smuta bookmark

- **WHEN** the campaign begins in August 1918, after the independence declaration
- **THEN** focuses depicting earlier events are either already resolved or unavailable
- **AND** the tree does not present decisions whose moment has passed

### Requirement: The historical spine is dated and recognisable

A player who takes the historical route should recognise the war. The spine, with dates established from sourced research:

| Moment | Date |
|---|---|
| Maapäev declares itself supreme authority | 15 Nov 1917 |
| Independence proclaimed; Germans enter Tallinn the next day | 24 Feb 1918 |
| German collapse; Red Army invades | Nov 1918 |
| Laidoner's counter-offensive; Narva retaken | 19 Jan 1919 |
| Cēsis — Estonians and Latvians rout the Landeswehr | 19–23 Jun 1919 |
| Land Reform Act | 10 Oct 1919 |
| Yudenich's Petrograd offensive collapses | Oct–Nov 1919 |
| Treaty of Tartu | 2 Feb 1920 |

#### Scenario: The player follows the historical route

- **WHEN** every historically-taken option is chosen
- **THEN** the sequence and approximate timing resemble the real war
- **AND** the tree reaches the Treaty of Tartu as a completable end state

### Requirement: The two historical forks are the tree's branch points

Estonia faced two moments where the decision was genuinely open, and both are better drama than a single peace-or-war choice at the end.

**April 1919.** Hungary offers to mediate an Estonian–Soviet peace. Rear-Admiral Cowan threatens to withdraw Royal Navy support if Estonia accepts. Early peace costs the fleet supplying Estonia's rifles and holding the Gulf.

**August 1919.** The Bolsheviks offer recognition in exchange for Estonian withdrawal from Pskov. In the same month Yudenich, under British pressure, forms a government that also recognises Estonian independence, to keep Estonia fighting. Both sides bid for the same small country at once.

#### Scenario: The player accepts early Soviet mediation

- **WHEN** the April 1919 peace option is taken
- **THEN** Entente support is materially reduced
- **AND** the loss is felt as a real cost, not a cosmetic penalty

#### Scenario: The player takes the August 1919 Bolshevik offer

- **WHEN** Estonia accepts recognition in exchange for withdrawing from Pskov
- **THEN** the route to supporting Yudenich's Petrograd offensive closes
- **AND** the two are mutually exclusive, symmetrically declared

### Requirement: The land question is a betrayal of allies, not a blow against enemies

**Estonia's Baltic Germans were not Latvia's.** Cēsis was Estonians helping Latvians fight *Latvia's* Landeswehr. Estonia's own Baltic Germans formed the Baltenregiment in November 1918 and fought alongside the Estonian army against the Red Army — 300 of 2,500 troops in January 1919, against 1.8% of the population. August Winnig transferred administrative power to the Estonian Provisional Government peacefully on 19 November 1918, and Baltic German representatives later co-drafted the minority-rights article of the 1920 constitution.

The fault line was economic, not military. The Land Reform Act of 10 October 1919 expropriated 1,065 manors — 96.6% of large estates, 58% of agricultural land — without compensation, from the same community whose sons were in the line. It bound the peasantry to the state and defused Bolshevik agitation; compensation was a live, contested question deliberately left unresolved until 1926.

Estonia already starts with the `landlordism` national spirit, so the mechanical hook exists.

**A tree that presents this as "expropriate the enemy" has the history backwards and throws away the best decision in the branch.**

#### Scenario: The player enacts uncompensated land reform

- **WHEN** the land reform focus completes without compensation
- **THEN** `landlordism` is resolved and the peasantry is bound to the state
- **AND** the domestic communist threat falls
- **AND** the Baltic German contribution to the war effort is damaged, because they are allies being expropriated

#### Scenario: The player pairs reform with compensation

- **WHEN** land reform is enacted with the compensation scheme that historically arrived only in 1926
- **THEN** agricultural and industrial capacity is retained, along with the minority bloc's loyalty
- **AND** the redistribution that defused Bolshevik agitation is weaker or slower
- **AND** neither option is strictly better than the other

### Requirement: The North-Western Army's fate is Estonia's decision

Yudenich's army operated from Estonian soil, failed at Petrograd, and was disarmed and interned by Estonia in November 1919 as leverage for the Tartu negotiations. `Russia_Northwestern_army.txt` already lets the NWA act on Estonia; nothing lets Estonia act on the NWA.

#### Scenario: The NWA issues its ultimatum

- **WHEN** the NWA player completes `NWA_ultimatum_baltic_countries`
- **THEN** Estonia has a response available rather than complying automatically

#### Scenario: Estonia interns the North-Western Army

- **WHEN** Estonia disarms the retreating White army
- **THEN** the NWA is materially weakened
- **AND** Estonia's position in peace negotiations with Moscow improves
- **AND** any future White Russian government treats Estonia accordingly

### Requirement: Branches end on distinct positions in the political spectrum

The mod has ten ideologies and Estonia already has a country leader for eight of them — Päts for despotism, Anvelt for leninism, Larka for fascism, Pitka for social liberalism, Tõnisson for market liberalism, Strandman twice, Kopp for conservatism.

The endings must not all be the same country wearing different hats.

#### Scenario: The tree is completed by different routes

- **WHEN** two players take different branches to completion
- **THEN** they end on different ruling ideologies with different leaders
- **AND** each uses a leader already defined in `history/countries/EST - Estonia.txt`

### Requirement: Existing unused assets are used before new ones are made

The mod already carries Estonian assets nobody wired up: `EST_labor_commune` has flag art, localisation and an event reference; `EST_sovrep` and `EST_socsovrep` have art and localisation; `EST_FIN_*`, `EST_UGRA_*` and `EST_belarus_*` have flag art only.

These are the original author's unfinished intentions. A branch that lands on one of them costs nothing in art.

#### Scenario: A branch needs a cosmetic tag

- **WHEN** a branch changes what Estonia is called or how it is flagged
- **THEN** an existing `EST_*` flag is used where one fits
- **AND** new art is requested only when nothing suitable exists

## Purpose

RoR replaces Hearts of Iron IV's seven-ideology WW2 framing with a ten-ideology spectrum appropriate to the Russian Revolution and Civil War, so that a Left SR, a Kadet and a Denikinite are distinguishable political positions rather than all "democratic".

## Requirements

### Requirement: The mod defines its own ideology set

The ideology set is RoR's, not vanilla's. Ten top-level ideologies are defined in `common/ideologies/`, each with sub-types representing distinct historical currents.

The current set is `radical_socialism`, `communism`, `social_democracy`, `social_liberalism`, `market_liberalism`, `conservatism`, `despotism`, `authoritarism`, `fascism`, `national_syndicalism`.

#### Scenario: New content picks a position on this spectrum

- **WHEN** a change adds a country, focus, idea or event that sets or tests a government
- **THEN** it uses one of the ten RoR ideologies or their sub-types
- **AND** it does not reference `democratic` or `neutrality`, which RoR removed

#### Scenario: Vanilla files overridden by the mod are updated to the RoR set

- **WHEN** a change overrides a vanilla file that references `democratic_drift`, `neutrality_drift` or another removed ideology
- **THEN** the reference is either updated to a RoR ideology or the override is dropped
- **AND** the change does not leave a modifier that the engine reports as invalid

### Requirement: Ideology tokens are used dynamically and that is intended

Referencing a custom ideology as a script token causes the engine to log `Token <ideology> is a dynamic token, this can cause OOS depending on how it's used`. This fork is single-player and accepts that warning as the cost of a custom spectrum.

#### Scenario: Dynamic-token warnings are not treated as defects

- **WHEN** T4 reports dynamic-token warnings for RoR ideologies
- **THEN** they are ignored rather than "fixed"
- **AND** no change removes a custom ideology in order to silence them

### Requirement: Sub-types carry the political distinction

A top-level ideology is too coarse to characterise a faction. Sub-types are what separate, for example, `leninism` from `revisionism` within `communism`, or `monarchism` from `authoritarism_ideology`.

#### Scenario: A faction's identity is expressed through a sub-type

- **WHEN** a change introduces or reworks a faction, party or country leader
- **THEN** it selects the sub-type that matches the historical position
- **AND** the choice is consistent with the voice register used for that faction's text

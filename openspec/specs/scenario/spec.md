## Purpose

RoR starts on 1 January 1917 and plays through the Revolution, the Civil War and the interwar period, in a game engine designed for 1936. The scenario capability records the constraints every piece of content inherits from that choice.

## Requirements

### Requirement: The scenario begins in 1917

The active bookmark is `RISEOFRUSSIA_NAME`, dated `1917.1.1.1`, with `RUS` as the default country. Vanilla's 1936 and 1939 bookmarks are not used.

#### Scenario: Content is dated from the 1917 start

- **WHEN** a change adds a focus, event or decision with a date condition
- **THEN** the date falls within the mod's timeframe rather than vanilla's
- **AND** the branch's expected completion window fits the period it depicts

#### Scenario: Technology and equipment match the period

- **WHEN** a change grants equipment, technology or unit types
- **THEN** the grant is plausible for the year it fires in
- **AND** it does not assume late-1930s vanilla baselines

### Requirement: The world is far larger than its authored content

421 country tags are defined; 40 of them have a focus tree. Most of the map is mechanically present and narratively thin, which is the pool Track A draws from.

#### Scenario: A branch is chosen against measured coverage

- **WHEN** a design session selects the week's divergence
- **THEN** the choice is informed by `tools/build_graph.py` output rather than by memory
- **AND** thin countries and thin periods are visible in that output

### Requirement: The engine's assumptions are 1936, and the mod's are not

Vanilla balance, AI behaviour and world state are tuned for a 1936 start and a 1939 war. A scenario running from 1917 accumulates drift the engine never anticipated — division counts, political power, manpower and AI stagnation.

#### Scenario: Global balance changes are evidenced, not argued

- **WHEN** a change alters world-state accumulation across many countries
- **THEN** it is Lane B2 and ships only with a before/after telemetry pair
- **AND** the telemetry includes tick time, not only world state

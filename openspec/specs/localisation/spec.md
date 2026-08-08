## Purpose

Every word a player reads is Russian, and the register shifts with who is speaking. This capability defines the mechanical and tonal requirements for player-facing text, because tone is the one property no automated tier can check.

## Requirements

### Requirement: Russian only

There is no English localisation track. Files live in `localisation/russian/` and declare `l_russian`.

#### Scenario: A change adds player-facing text

- **WHEN** a change adds a focus name, event, idea, decision or tooltip
- **THEN** the text is written in Russian
- **AND** T1 reports `L002` if the file declares any other language header

### Requirement: Localisation files are UTF-8 with BOM

Cyrillic content without the byte-order mark renders as mojibake in game while every reference check still passes. All 195 upstream files carry it.

#### Scenario: A new localisation file is added

- **WHEN** a change creates a file under `localisation/russian/`
- **THEN** it is encoded UTF-8 with BOM
- **AND** T1 reports `L001` if it is not

### Requirement: Script files are valid UTF-8

The engine's parser stops at the first byte it cannot decode, so a mis-encoded comment silently truncates the rest of the file and discards the definitions after it.

#### Scenario: A script file carries non-UTF-8 bytes

- **WHEN** any `.txt`, `.gfx`, `.gui` or `.yml` file fails to decode as UTF-8
- **THEN** T1 reports `S002` and the file is transcoded before the change proceeds

### Requirement: Register follows the country receiving the text

RoR's narration is a partisan contemporary account, not a neutral summary. The voice is chosen by who reads the event, not by which file it lives in — an event in a White-faction file may be written for a red player and use red vocabulary.

`style/matrix.yaml` maps register to leaning and country; `style/corpus/` holds 52 verbatim upstream samples.

#### Scenario: Writing text for a faction

- **WHEN** a change writes player-facing prose
- **THEN** the register is selected from `style/matrix.yaml` by the receiving country
- **AND** corpus samples for that register are read before writing
- **AND** vocabulary avoids `style/lexicon-deny.txt`

#### Scenario: Text that could not be pitched confidently

- **WHEN** the writer is unsure of the right register for an unfamiliar faction
- **THEN** that uncertainty is reported under "Simplifications, omissions, and blockers"
- **AND** it is not resolved by writing flat, neutral prose that passes every lint

### Requirement: Text describes the world, never the project

Player-facing strings describe world state and player choices. They never describe implementation history, tuning, or the mod's development.

#### Scenario: Reworking existing content

- **WHEN** a change rewrites an existing event or focus description
- **THEN** the new text reads as though the feature always existed
- **AND** it contains no "now reworked", "newly added" or similar wording

### Requirement: Every focus has a name and a description

A focus without localisation renders as its raw id. 149 upstream focuses currently do; that is recorded as a known defect and is not a licence to add more.

#### Scenario: A focus is added

- **WHEN** a change adds a focus with id `X`
- **THEN** `X` and `X_desc` both exist in `localisation/russian/`
- **AND** T1 reports `R005` or `R006` if either is missing

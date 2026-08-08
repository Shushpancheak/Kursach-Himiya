---
name: ror-voice
description: Write or review player-facing Russian text for the RoR fork — event titles and descriptions, option names, focus names and descriptions, idea and decision text. Load before writing any string a player will read.
---

# ror-voice

**Load this before writing a single player-facing string.** Not after.

R2 in the risk register: Russian that is grammatical but tonally wrong is **invisible to every automated tier**. T1 confirms the key exists. T2 confirms the reference resolves. T3 renders the tree. None of them can tell a Sovnarkom decree from a corporate memo. The lexicon lint catches crude vocabulary errors and nothing else.

## Procedure

1. **Read `style/summary.md` in full.** It is short and it is the brief.
2. **Identify the register.** Not from the filename — from **who receives the event**. An event living in `RussianCivilWar_Don_Kuban_Ukraine.txt` may be written for a red player and use red vocabulary. Ask: which country's screen is this on?
3. **Look up `style/matrix.yaml`.** Resolution order is `countries[<TAG>]` → `registers[<leaning>]` → `shared`. A TAG entry overrides its register.
4. **Read 2–3 samples from the matching `style/corpus/<register>/`.** This is the step people skip and it is the step that works. Showing beats describing.
5. Write.
6. **Re-read against `style/lexicon-deny.txt`.** Then run T1 — `V001` reports deny-list hits, but only in authored prose, so it will not save you in every case.

## What good looks like

- **Title:** short noun phrase. `Юнкерское выступление`. `Судьба Краснова`. Never a sentence, question or exclamation.
- **Description:** 2–5 sentences typically. Real names, institutions, dates, places. Paragraph break is `\n` inside the `.yml` value.
- **Options:** short, decided, carrying attitude. `Срочно выставить против них красную гвардию!` / `У красногвардейцев есть дела поважнее`. Where a body votes rather than a man deciding, say so: `Голосую — казнить`.

## Hard rules

1. **Russian only** (C8). No English localisation track exists in this fork.
2. **UTF-8 with BOM.** Every localisation file. With Cyrillic content, losing the BOM means mojibake in game while every other check stays green.
3. **Never describe implementation history.** No «теперь переработано», «добавлено», «изменено». Write updated content as if the feature always existed.
4. **Never break the fourth wall.** Describe world state and the player's choices. Effect tooltips carry the mechanics; prose does not.
5. **No placeholder text.** `work_in_progress` exists upstream. Do not add more. An unwritten string is a blocker to report, not a thing to fill with filler.
6. **Invented specificity is worse than none.** RoR's prose is dense with things that really happened. If you do not know the detail, write around it rather than inventing a plausible-sounding institution.
7. **Quote only real documents**, in guillemets, with `...` for elision, and attribute them.

## Localisation mechanics

```
 KEY_name: "Текст"
```

One leading space, no `:0` version suffix. That is this repo's dominant convention by 59,854 entries to 1,029 — the source kit's "no leading space" rule is simply wrong here.

Colour codes: `§R`, `§Y`, `§H`, digits `§1`, signs `§+` `§-`, reset `§!`. Icons: `£icon_name£` or `£icon_name`. Both icon forms are valid.

## Reporting

If you could not reach the right register for something — an unfamiliar faction, a country with no corpus samples, a mechanic with no precedent — **say so in the `Simplifications, omissions, and blockers` section**. Flat text that passes every lint is exactly the failure this project is trying to avoid, and the owner reviews all flavour text anyway (C9). Flagging your own uncertainty makes that review faster, not weaker.

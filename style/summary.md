# RoR's voice

Distilled from `style/corpus/` (52 upstream events across 7 registers). This describes what the mod *does*, not what it should do. Refresh after every upstream merge, along with the corpus.

Loaded by `ror-voice` together with the matching `matrix.yaml` cell and 2–3 corpus samples. Read the samples — showing beats describing.

---

## What the narration is

**A partisan contemporary account, not a historian's summary.** RoR's event text is written from inside the viewpoint of the country reading it. The Bolshevik player is told about *"контрреволюция Керенского"* and *"бандитская контрреволюционная шайка"*. The imperial player is told about *"недовольные граждане, подстрекаемые социалистами-провокаторами"*. Neither hedges. Neither is "balanced".

**The viewpoint follows the reading country, not the file.** An event in `RussianCivilWar_Don_Kuban_Ukraine.txt` describing Kaledin's declaration of martial law calls the Provisional Government *"народное правительство"* and the revolution a victory — because that event fires for a red player. Do not infer register from the filename. Infer it from who receives the event.

**Dense with real history.** Named people, institutions, dates, places, documents. `Инженерный замок`. `ЦВПК`. `Комитет спасения Родины и революции`. `[num_of_allrussian_congress_of_soviets] Всероссийский Съезд Советов`. The mod assumes a reader who wants the specific thing that happened, not a generic revolutionary mood. **Invented detail that reads as generic is the main failure mode.**

**Quotation is used heavily.** Real documents and speeches appear in guillemets with ellipses for elision:

> «Ввиду выступления большевиков с попытками низвержения Временного правительства... Войсковое правительство, считая такой захват власти большевиками преступным,... окажет... полную поддержку... Временному правительству»

Followed by narration that frames it. If you quote, quote something real, and attribute it.

## Shape

- **Title:** a short noun phrase. `Юнкерское выступление`. `Судьба Краснова`. `Доклад Колчака`. Not a sentence, not a question, no exclamation.
- **Description:** 2–5 sentences typically, up to a few paragraphs. Paragraph breaks are `\n` in the `.yml`.
- **Options:** short and decided. Imperative or first-person plural. `Срочно выставить против них красную гвардию!`, `Голосую — казнить`, `У красногвардейцев есть дела поважнее`, `Дон будет свободен!`
  - Options carry attitude. A dismissive option sounds dismissive. They are not neutral menu labels.
  - Where the choice is a vote or a collegial decision, the option says so (`Голосую — …`).

## Register markers

| Marker | Effect |
|---|---|
| Form of address | `товарищ` / `гражданин` / `господин` / `Ваше Высокопревосходительство` — see `matrix.yaml` |
| Naming | Bolshevik text names enemies by surname alone (`Краснов`). Respectful register uses name + patronymic (`Александр Васильевич`) |
| Institutional vocabulary | Each faction names the same body differently — `Совдеп` vs `Совет рабочих и солдатских депутатов` |
| Moral loading | Present in every register, pointing in different directions |

## Hard rules

1. **Russian only** (C8). No English localisation track exists.
2. **Never describe implementation history.** No *«теперь переработано»*, *«добавлено»*, *«изменено»*. Write updated content as if the feature always existed.
3. **Never break the fourth wall.** Text describes world state and the player's choices. Not mechanics-speak, not tuning notes, not "this gives +10 political power" — that is what the effect tooltip is for.
4. **No modern bureaucratic Russian.** See `lexicon-deny.txt`. This is the single most common way generated text gives itself away: grammatically perfect, period-blind.
5. **Placeholder text is a blocker, not a deliverable.** `work_in_progress` exists upstream; do not add more.

## Why this matters more than the rest of the pipeline

R2 in the risk register: agent-generated Russian that is grammatical but tonally wrong is **invisible to every automated tier**. T1 checks that the key exists. T2 checks the reference resolves. T3 renders the tree. None of them can tell a Sovnarkom decree from a corporate memo.

The lexicon lint catches the crudest cases. The corpus and this file aim at the rest. The owner's review (C9) is the only real gate.

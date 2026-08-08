#!/usr/bin/env python3
"""Extract the style corpus from upstream events.

The corpus is *verbatim reference*, not instruction. `ror-voice` loads
`style/summary.md`, the matching `style/matrix.yaml` cell, and a handful of
these samples — showing the model what RoR sounds like beats describing it.

Re-run after every upstream merge (plan §3.4) so the fork's voice tracks
Gtym33's as he develops it:

    tools/build_corpus.py --out style/corpus
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from clausewitz import parse_file, parse_localisation  # noqa: E402

REPO = Path(__file__).resolve().parent.parent

# Which event files speak in which political voice. Keyed on filename
# fragments because RoR's namespaces are not consistently themed.
#
# This mapping is editorial and deliberately lives here rather than being
# inferred: "who is talking" is a judgement about the mod's fiction, and a
# wrong guess would teach the wrong voice.
BUCKETS: dict[str, list[str]] = {
    "bolshevik": [
        "RussianCivilWar_Bolsheviks", "Russian_Petrograd_Commune", "Soviet",
        "RussianCivilWar_Donbass", "Belarus_soviet",
    ],
    "sr-komuch": [
        "RussianCivilWar_All_russian_constituent_assembly", "RussianCivilWar_CCA",
        "RussianCivilWar_DON_CCA", "RussianCivilWar_Izhevsk",
        "RussianCivilWar_All_russian_national_assembly",
    ],
    "kadet-provisional": [
        "Russia.txt", "Russia_filler", "RussianCivilWar_Kornilov_Counter_Revolution",
    ],
    "white": [
        "RussianCivilWar_Kolchak", "RussianCivilWar_Don_Kuban_Ukraine",
        "RussianCivilWar_North_Caucasus", "RussianCivilWar_Amur_Primorye",
        "RussianCivilWar_Crimea", "RussianCivilWar_Gold",
    ],
    "monarchist": [
        "Russian_Monarchy_Overtrow", "RussianCivilWar_Muscovy",
    ],
    "green-anarchist": [
        "RussianCivilWar_Green", "RussianCivilWar_Free_territory",
    ],
    "foreign-power": [
        "RussianCivilWar_Britishseas", "RussianCivilWar_Czechs", "Turkey",
        "RussianCivilWar_BalticFinlandKarelia", "Germany", "Austro-Hungary",
    ],
}

# A sample is only useful if it actually shows prose.
MIN_DESC = 240


def load_localisation() -> dict[str, str]:
    loc: dict[str, str] = {}
    for path in sorted(REPO.glob("localisation/**/*.yml")):
        for entry in parse_localisation(path)[0]:
            loc.setdefault(entry.key, entry.text)
    return loc


def bucket_for(path: Path) -> str | None:
    name = path.name
    for bucket, fragments in BUCKETS.items():
        if any(fragment.lower() in name.lower() for fragment in fragments):
            return bucket
    return None


def render(event_id: str, title: str, desc: str, options: list[str], source: str) -> str:
    # `\n` in localisation is a literal escape in the .yml; expand it so the
    # sample reads as the player sees it.
    body = desc.replace("\\n", "\n")
    lines = [
        f"# {event_id}",
        "",
        f"*Source: `{source}`*",
        "",
        f"**{title}**",
        "",
        body,
        "",
        "---",
        "",
    ]
    lines += [f"- {option}" for option in options]
    return "\n".join(lines) + "\n"


def build(out: Path, per_bucket: int, per_file: int) -> dict:
    loc = load_localisation()
    manifest: dict[str, list[str]] = {}

    for path in sorted(REPO.glob("events/*.txt")):
        bucket = bucket_for(path)
        if bucket is None:
            continue
        taken = manifest.setdefault(bucket, [])
        if len(taken) >= per_bucket:
            continue
        # Cap per file, otherwise the first file alphabetically fills the
        # whole bucket and the register is represented by one author's
        # handful of events rather than by the mod.
        from_this_file = 0

        for node in parse_file(path).root.nodes:
            if node.key not in ("country_event", "news_event") or not node.is_block:
                continue
            if len(taken) >= per_bucket or from_this_file >= per_file:
                break

            block = node.value
            event_id = block.value_of("id")
            title = loc.get(block.value_of("title") or "", "")
            desc = loc.get(block.value_of("desc") or "", "")
            if not event_id or not title or len(desc) < MIN_DESC:
                continue

            options = [
                loc.get(opt.value.value_of("name") or "", "")
                for opt in block.get_all("option")
                if opt.is_block
            ]
            options = [o for o in options if o]
            if not options:
                continue

            target = out / bucket / f"{event_id}.md"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(
                render(event_id, title, desc, options, str(path.relative_to(REPO))),
                encoding="utf-8",
            )
            taken.append(event_id)
            from_this_file += 1

    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract the RoR style corpus")
    parser.add_argument("--out", type=Path, default=REPO / "style" / "corpus")
    parser.add_argument("--per-bucket", type=int, default=8)
    parser.add_argument("--per-file", type=int, default=3)
    args = parser.parse_args()

    if args.out.exists():
        for stale in args.out.rglob("*.md"):
            stale.unlink()

    manifest = build(args.out, args.per_bucket, args.per_file)
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "manifest.json").write_text(
        json.dumps(manifest, indent=1, ensure_ascii=False), encoding="utf-8"
    )

    total = sum(len(v) for v in manifest.values())
    print(f"{total} samples across {len(manifest)} registers -> {args.out}")
    for bucket, ids in sorted(manifest.items()):
        print(f"  {len(ids):>3}  {bucket}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

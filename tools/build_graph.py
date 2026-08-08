#!/usr/bin/env python3
"""Build `graph.json` — the dashboard's only data source.

The governing rule (plan §3.1): **the inventory is never declared.** This reads
the `.txt` files and reports what exists. OpenSpec specs say what *should*
exist; disagreement between the two is surfaced as drift, not reconciled.

Everything here is computed. There is no hand-maintained "done" flag anywhere
in this repo, because a hand-maintained one drifts within a week.

Usage:
    tools/build_graph.py --out dashboard/graph.json
    tools/build_graph.py --no-blame        # skip provenance (much faster)
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from clausewitz import (  # noqa: E402
    Block,
    exclusive_ids,
    iter_focus_blocks,
    parse_file,
    parse_localisation,
    prerequisite_groups,
)

REPO = Path(__file__).resolve().parent.parent

UPSTREAM = "upstream-human"
OWNER = "owner"
AGENT = "agent"

# Commits carrying this trailer were written by the loop rather than by hand.
AGENT_TRAILER = re.compile(r"^Co-Authored-By:\s*Claude", re.MULTILINE | re.IGNORECASE)

TAG = re.compile(r"^[A-Z]{3}$")
DATE = re.compile(r"\b(\d{3,4})\.\d{1,2}\.\d{1,2}\b")


# --- provenance ------------------------------------------------------------


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=REPO, capture_output=True, text=True, check=True
    ).stdout


def upstream_commits() -> set[str] | None:
    """Every commit reachable from the upstream merge base.

    This is why C7 forbids rebasing: rewrite the history and every focus in the
    mod is reattributed to whoever ran the rebase.
    """
    try:
        base = git("merge-base", "upstream/master", "HEAD").strip()
    except subprocess.CalledProcessError:
        print("warning: no upstream/master — provenance unavailable", file=sys.stderr)
        return None
    return set(git("rev-list", base).split())


def agent_commits() -> set[str]:
    out = git("log", "--format=%H%x00%B%x01")
    found = set()
    for entry in out.split("\x01"):
        if "\x00" not in entry:
            continue
        sha, body = entry.split("\x00", 1)
        if AGENT_TRAILER.search(body):
            found.add(sha.strip())
    return found


def blame_lines(path: Path) -> dict[int, str]:
    """line number -> commit sha, from one `git blame` per file.

    Blaming per focus would mean 2,600 subprocesses. Per file it is 168.
    """
    try:
        out = git("blame", "--porcelain", "--", str(path.relative_to(REPO)))
    except subprocess.CalledProcessError:
        return {}
    mapping: dict[int, str] = {}
    for line in out.split("\n"):
        # Porcelain header: "<sha> <orig-line> <final-line> [<count>]"
        parts = line.split(" ")
        if len(parts) >= 3 and len(parts[0]) == 40 and all(c in "0123456789abcdef" for c in parts[0]):
            try:
                mapping[int(parts[2])] = parts[0]
            except ValueError:
                pass
    return mapping


def classify(shas: list[str], upstream: set[str] | None, agents: set[str]) -> str:
    """A focus is upstream only if *every* line of it is. One owner edit to an
    upstream focus makes it owner-touched, which is the honest reading for a
    dashboard whose job is to show what this fork changed."""
    if upstream is None or not shas:
        return "unknown"
    if any(sha in agents for sha in shas):
        return AGENT
    if all(sha in upstream for sha in shas):
        return UPSTREAM
    return OWNER


# --- extraction ------------------------------------------------------------


def tree_tags(tree: Block | None, focus_ids: list[str]) -> list[str]:
    """Country tags for a tree.

    Preference order: explicit `tag =` / `original_tag =` in the tree's
    `country` block, then the shared three-letter prefix of its focus ids.
    Focus-tree country blocks are weight expressions, not declarations, so
    there is no single authoritative field to read.
    """
    tags: list[str] = []
    if tree is not None:
        country = tree.get("country")
        if country is not None and country.is_block:
            for node in country.value.walk():
                if node.key in ("tag", "original_tag") and not node.is_block:
                    if TAG.match(str(node.value)) and node.value not in tags:
                        tags.append(node.value)
    if not tags:
        prefixes = {fid.split("_")[0] for fid in focus_ids if TAG.match(fid.split("_")[0])}
        if len(prefixes) == 1:
            tags = sorted(prefixes)
    return tags


def reward_is_trivial(block: Block) -> bool:
    """An empty `completion_reward = { }`, or one that only shows a tooltip,
    is a placeholder. Upstream has many; they are worth seeing on a dashboard."""
    node = block.get("completion_reward")
    if node is None or not node.is_block:
        return True
    body = node.value
    if not body.nodes and not body.items:
        return True
    return all(n.key == "custom_effect_tooltip" for n in body.nodes)


def earliest_date(block: Block) -> int | None:
    """Earliest year mentioned in `available`, as a period hint."""
    node = block.get("available")
    if node is None or not node.is_block:
        return None
    years = [int(m.group(1)) for n in node.value.walk() if not n.is_block
             for m in [DATE.search(str(n.value))] if m]
    return min(years) if years else None


def linked_events(block: Block) -> list[str]:
    node = block.get("completion_reward")
    if node is None or not node.is_block:
        return []
    found = []
    for child in node.value.walk():
        if child.key in ("country_event", "news_event"):
            target = child.value.value_of("id") if child.is_block else child.value
            if target:
                found.append(target)
    return found


def build(with_blame: bool = True) -> dict:
    loc_keys: set[str] = set()
    for path in sorted(REPO.glob("localisation/**/*.yml")):
        entries, _, _ = parse_localisation(path)
        loc_keys.update(e.key for e in entries)

    sprites: set[str] = set()
    for path in sorted(REPO.glob("interface/**/*.gfx")):
        sprites.update(
            re.findall(r'name\s*=\s*"(GFX_[A-Za-z0-9_.\-]+)"',
                       path.read_text(encoding="utf-8-sig", errors="replace"))
        )

    documented: set[str] = set()
    for path in sorted(REPO.glob("docs/**/*.md")):
        documented.update(re.findall(r"\b([A-Z]{3}_[A-Za-z0-9_]+)\b",
                                     path.read_text(encoding="utf-8", errors="replace")))

    upstream = upstream_commits() if with_blame else None
    agents = agent_commits() if with_blame else set()

    nodes: list[dict] = []
    trees: dict[str, dict] = {}
    by_file: dict[Path, list] = defaultdict(list)

    for path in sorted(REPO.glob("common/national_focus/*.txt")):
        result = parse_file(path)
        collected = list(iter_focus_blocks(result))
        for tree_id, kind, tree_block, block in collected:
            by_file[path].append((tree_id, kind, tree_block, block))

    for path, collected in by_file.items():
        blame = blame_lines(path) if with_blame else {}
        grouped: dict[str, list] = defaultdict(list)
        for tree_id, kind, tree_block, block in collected:
            grouped[tree_id].append((kind, tree_block, block))

        for tree_id, members in grouped.items():
            ids = [b.value_of("id") for _, _, b in members if b.value_of("id")]
            tags = tree_tags(next((t for _, t, _ in members if t is not None), None), ids)
            trees[tree_id] = {
                "id": tree_id,
                "file": str(path.relative_to(REPO)),
                "countries": tags,
                "focus_count": len(ids),
                "shared": members[0][0] == "shared",
            }

            for kind, _tree_block, block in members:
                focus_id = block.value_of("id")
                if not focus_id:
                    continue
                shas = [blame[n] for n in range(block.line, (block.end_line or block.line) + 1)
                        if n in blame]

                has_title = focus_id in loc_keys
                has_desc = f"{focus_id}_desc" in loc_keys
                icon = block.value_of("icon")
                icon_ok = bool(icon) and (not icon.startswith("GFX_") or icon in sprites)
                events = linked_events(block)
                trivial = reward_is_trivial(block)
                has_ai = block.get("ai_will_do") is not None

                checklist = {
                    "localisation_title": (has_title, 2),
                    "localisation_desc": (has_desc, 1),
                    "icon": (icon_ok, 1),
                    "completion_reward": (not trivial, 2),
                    "ai_will_do": (has_ai, 1),
                    "linked_events": (bool(events), 1),
                    "documented": (focus_id in documented, 1),
                }
                earned = sum(w for ok, w in checklist.values() if ok)
                total = sum(w for _, w in checklist.values())

                nodes.append({
                    "id": focus_id,
                    "tree": tree_id,
                    "countries": tags,
                    "file": str(path.relative_to(REPO)),
                    "line": block.line,
                    "x": block.value_of("x"),
                    "y": block.value_of("y"),
                    "relative_position_id": block.value_of("relative_position_id"),
                    "cost": block.value_of("cost"),
                    "icon": icon,
                    # AND-of-OR preserved: outer list is AND, inner list is OR.
                    "prerequisites": prerequisite_groups(block),
                    "mutually_exclusive": exclusive_ids(block),
                    "linked_events": events,
                    "available_from": earliest_date(block),
                    "provenance": classify(shas, upstream, agents),
                    "checklist": {k: ok for k, (ok, _) in checklist.items()},
                    "completeness": round(earned / total, 3),
                })

    resolve_positions(nodes)
    return {
        "schema": "ror.graph.v1",
        "generated_from": git("rev-parse", "HEAD").strip(),
        "nodes": nodes,
        "trees": sorted(trees.values(), key=lambda t: t["id"]),
        "spec_drift": spec_drift({n["id"] for n in nodes}),
        "summary": summarise(nodes),
    }


def resolve_positions(nodes: list[dict]):
    """Absolute grid coordinates, following `relative_position_id` chains.

    The dashboard lays the tree out on the mod's own coordinates so it mirrors
    the in-game view; that only works once anchors are resolved.
    """
    index = {n["id"]: n for n in nodes}

    def absolute(node, seen):
        if node["id"] in seen:
            return None
        try:
            x, y = int(node["x"]), int(node["y"])
        except (TypeError, ValueError):
            return None
        anchor = node.get("relative_position_id")
        if not anchor or anchor not in index:
            return (x, y)
        base = absolute(index[anchor], seen | {node["id"]})
        return None if base is None else (base[0] + x, base[1] + y)

    for node in nodes:
        position = absolute(node, set())
        node["abs_x"], node["abs_y"] = position if position else (None, None)


def spec_drift(focus_ids: set[str]) -> dict:
    """Focuses with no spec, and specs naming focuses that do not exist.

    OpenSpec describes intent; the parser reports reality. Neither is corrected
    to match the other — the gap itself is the finding.
    """
    spec_ids: set[str] = set()
    for path in sorted(REPO.glob("openspec/specs/**/*.md")):
        spec_ids.update(re.findall(r"\b([A-Z]{3}_[A-Za-z0-9_]+)\b",
                                   path.read_text(encoding="utf-8", errors="replace")))
    return {
        "specified_but_missing": sorted(spec_ids - focus_ids),
        "present_but_unspecified": len(focus_ids - spec_ids),
        "specs_indexed": len(spec_ids),
    }


def summarise(nodes: list[dict]) -> dict:
    by_provenance = defaultdict(int)
    for node in nodes:
        by_provenance[node["provenance"]] += 1
    complete = [n for n in nodes if n["completeness"] == 1.0]
    return {
        "focus_count": len(nodes),
        "by_provenance": dict(by_provenance),
        "mean_completeness": round(sum(n["completeness"] for n in nodes) / len(nodes), 3) if nodes else 0,
        "fully_complete": len(complete),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the dashboard graph")
    parser.add_argument("--out", type=Path, default=REPO / "dashboard" / "graph.json")
    parser.add_argument("--no-blame", action="store_true", help="skip provenance")
    args = parser.parse_args()

    graph = build(with_blame=not args.no_blame)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(graph, indent=1, ensure_ascii=False))

    summary = graph["summary"]
    print(f"{summary['focus_count']} focuses in {len(graph['trees'])} trees -> {args.out}")
    print(f"  provenance: {summary['by_provenance']}")
    print(f"  mean completeness: {summary['mean_completeness']}")
    print(f"  fully complete: {summary['fully_complete']}")
    drift = graph["spec_drift"]
    print(f"  spec drift: {len(drift['specified_but_missing'])} specified-but-missing, "
          f"{drift['present_but_unspecified']} present-but-unspecified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

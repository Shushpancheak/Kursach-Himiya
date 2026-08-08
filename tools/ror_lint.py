#!/usr/bin/env python3
"""T1 — RoR lint suite.

Runs in seconds, needs no game install, and encodes the invariants that matter
for this fork. Deliberately small: see `docs/tooling-decisions.md` for what was
left to other tiers and why.

Calibration rule (plan §14): **T1 must run green on unmodified upstream.** If a
check fires on upstream content, the check is wrong until proven otherwise —
or the finding is real and belongs in `docs/known-upstream-defects.md`, never
in a silent suppression. Use `--baseline` to freeze the known state and gate
only on what a branch newly introduces.

Usage:
    tools/ror_lint.py                      # lint everything, human output
    tools/ror_lint.py --json out.json      # machine-readable
    tools/ror_lint.py --baseline base.json # report only new findings
    tools/ror_lint.py --write-baseline base.json
    tools/ror_lint.py --changed            # only files changed vs upstream merge-base
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass, asdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from clausewitz import (  # noqa: E402
    Block,
    exclusive_ids,
    iter_focus_blocks,
    parse_file,
    parse_localisation,
    prerequisite_groups,
    strip_comments_and_strings,
)

REPO = Path(__file__).resolve().parent.parent

_UNSET = object()

ERROR = "error"
WARNING = "warning"


@dataclass(frozen=True)
class Finding:
    code: str
    severity: str
    file: str
    line: int
    message: str

    def key(self) -> str:
        """Baseline identity. Deliberately excludes the line number so that
        inserting content above a known finding does not resurrect it."""
        return f"{self.code}|{self.file}|{self.message}"

    def __str__(self) -> str:
        return f"{self.file}:{self.line}: [{self.code}] {self.message}"


class Lint:
    def __init__(self, root: Path, files: set[Path] | None = None):
        self.root = root
        self.limit = files
        self.findings: list[Finding] = []
        self._deny: list[tuple[re.Pattern, str]] | None = None
        self.focus_ids: set[str] = set()
        self._sprites: set[str] | None = None
        self._vanilla = _UNSET

    # -- helpers ------------------------------------------------------------

    def report(self, code, severity, path: Path, line: int, message: str):
        self.findings.append(
            Finding(code, severity, str(Path(path).relative_to(self.root)), line, message)
        )

    def scan(self, *globs: str) -> list[Path]:
        out: list[Path] = []
        for pattern in globs:
            out.extend(sorted(self.root.glob(pattern)))
        if self.limit is not None:
            out = [p for p in out if p in self.limit]
        return out

    # -- S: structure -------------------------------------------------------

    def check_structure(self):
        for path in self.scan("common/**/*.txt", "events/**/*.txt", "history/**/*.txt"):
            for line, message in parse_file(path).problems:
                self.report("S001", ERROR, path, line, message)

    # -- L: localisation ----------------------------------------------------

    def check_localisation(self):
        """The single highest-value group in this file.

        A Cyrillic mod without the UTF-8 BOM renders as mojibake in game, and
        nothing else in the pyramid catches it — the file parses, the keys
        resolve, the text is simply wrong on screen.
        """
        seen: dict[str, tuple[str, int]] = {}
        for path in self.scan("localisation/**/*.yml"):
            entries, has_bom, header = parse_localisation(path)

            if not has_bom:
                self.report("L001", ERROR, path, 1, "localisation file is not UTF-8 with BOM")

            if header and header != "l_russian":
                self.report(
                    "L002", ERROR, path, 1,
                    f"language header is `{header}`; this fork is Russian-only (C8)",
                )

            for entry in entries:
                if entry.version:
                    self.report(
                        "L003", WARNING, path, entry.line,
                        f"key `{entry.key}` uses the `:{entry.version}` version suffix; write `{entry.key}:`",
                    )
                if entry.key in seen:
                    other_file, other_line = seen[entry.key]
                    self.report(
                        "L004", WARNING, path, entry.line,
                        f"duplicate key `{entry.key}`, also at {other_file}:{other_line}",
                    )
                else:
                    seen[entry.key] = (str(Path(path).relative_to(self.root)), entry.line)

                self._check_markup(path, entry)
                self._check_voice(path, entry)

    def _check_markup(self, path: Path, entry):
        """Colour and icon markup.

        Only unambiguous breakage is reported. `£icon£` and `£icon` are both
        valid, and the engine does not require strictly nested `§` codes — a
        stricter reading produces hundreds of false positives on vanilla text.

        Colour codes are letters (`§R`), digits (`§1`) and the numeric sign
        forms (`§+`, `§-`), plus the reset `§!`. Only a `§` followed by none of
        those, or one at the very end of the value, is actually broken.
        """
        text = entry.text
        if re.search(r"§(?![A-Za-z0-9!+\-])", text) or text.endswith("§"):
            self.report(
                "L005", ERROR, path, entry.line,
                f"key `{entry.key}` has a `§` with no colour code or reset after it",
            )

    # Event localisation keys: `<namespace>.<number>.<suffix>`, e.g.
    # `rcw_kolchak.3.d`, `soviet.3.t`, `rcw_nrr.19.desc`.
    EVENT_KEY = re.compile(r"^[a-z][a-z0-9_]*\.\d+\.[a-z0-9_]+$")

    def _is_authored_prose(self, key: str) -> bool:
        """Voice rules apply to text this project writes: event and focus
        prose. They do not apply to engine UI strings, technology names or
        tooltips inherited from vanilla — those are Paradox's register, not
        RoR's, and holding them to the period lexicon produces noise rather
        than findings."""
        if self.EVENT_KEY.match(key):
            return True
        stem = key[:-5] if key.endswith("_desc") else key
        return stem in self.focus_ids

    def _check_voice(self, path: Path, entry):
        """Lexicon deny-list (R2).

        The crudest possible defence against tonally wrong Russian, and worth
        having precisely because every other tier is blind to voice: T1 checks
        the key exists, T2 that the reference resolves, T3 renders the tree.
        None can tell a Sovnarkom decree from a corporate memo.

        This catches vocabulary, not register. The corpus, `style/summary.md`
        and the owner's review (C9) are what actually carry R2.
        """
        if not self._is_authored_prose(entry.key):
            return
        for pattern, term in self.deny_lexicon:
            if pattern.search(entry.text):
                self.report(
                    "V001", WARNING, path, entry.line,
                    f"key `{entry.key}` contains `{term}`, which is on the deny lexicon "
                    "(anachronism or modern bureaucratic Russian)",
                )

    @property
    def deny_lexicon(self) -> list[tuple[re.Pattern, str]]:
        if self._deny is None:
            self._deny = []
            path = self.root / "style" / "lexicon-deny.txt"
            if path.exists():
                for line in path.read_text(encoding="utf-8").splitlines():
                    term = line.split("#")[0].strip()
                    if not term:
                        continue
                    # Match the stem so Russian inflections are caught, but
                    # require a word boundary at the start so `регион` does
                    # not fire inside an unrelated word.
                    self._deny.append(
                        (re.compile(rf"\b{re.escape(term)}", re.IGNORECASE), term)
                    )
        return self._deny

    # -- E: engine rules ----------------------------------------------------

    def check_engine(self):
        for path in self.scan("common/**/*.txt", "events/**/*.txt", "history/**/*.txt"):
            raw = path.read_text(encoding="utf-8-sig", errors="replace")
            code = strip_comments_and_strings(raw)
            relative = path.relative_to(self.root).as_posix()
            is_ai_grammar = relative.startswith(("common/scorers/", "common/ai_"))

            for number, line in enumerate(code.splitlines(), start=1):
                if "<=" in line or ">=" in line:
                    self.report(
                        "E001", ERROR, path, number,
                        "`<=`/`>=` are not supported by the engine; "
                        "use check_variable with compare = greater_than_or_equals",
                    )
                # AI scorers and strategy files have their own grammar, where
                # `add = -num_armies` refers to an engine scorer token rather
                # than a script variable. The rule does not apply there.
                if not is_ai_grammar and re.search(r"=\s*-[A-Za-z_][A-Za-z0-9_]*", line):
                    self.report(
                        "E002", ERROR, path, number,
                        "unary `-` on a variable token does nothing; negate with multiply_variable",
                    )
                if re.search(r"\b(?:ROOT|PREV|THIS|FROM)\.[A-Za-z_][A-Za-z0-9_]*\b", line) and (
                    "temp" in line
                ):
                    self.report(
                        "E003", WARNING, path, number,
                        "temporary variables have no scope; a ROOT./PREV. prefix silently does nothing",
                    )

            self._check_global_event_targets(path, code)
            self._check_file_scoped_constants(path, code)

    def _check_global_event_targets(self, path: Path, code: str):
        saved = set(re.findall(r"save_global_event_target_as\s*=\s*([A-Za-z_][\w]*)", code))
        cleared = set(re.findall(r"clear_global_event_target\s*=\s*([A-Za-z_][\w]*)", code))
        if re.search(r"clear_global_event_targets\b", code):
            return  # blanket clear covers everything in this file
        for name in sorted(saved - cleared):
            self.report(
                "E004", WARNING, path, 1,
                f"global event target `{name}` is saved but never cleared; "
                "global targets do not auto-clear",
            )

    def _check_file_scoped_constants(self, path: Path, code: str):
        defined = set(re.findall(r"^\s*(@[A-Za-z_][\w]*)\s*=", code, re.MULTILINE))
        used = set(re.findall(r"(?<![\w])(@[A-Za-z_][\w]*)", code))
        for name in sorted(used - defined):
            self.report(
                "E005", ERROR, path, 1,
                f"`{name}` is used but not defined in this file; "
                "@constants are file-scoped — use common/script_constants/ for shared values",
            )

    # -- focus trees --------------------------------------------------------

    def collect_focuses(self):
        """Return {focus_id: info} and {tree_id: [focus_id]} across the mod."""
        focuses: dict[str, dict] = {}
        trees: dict[str, list[str]] = defaultdict(list)

        for path in self.scan("common/national_focus/*.txt"):
            for tree_id, _kind, _tree, block in iter_focus_blocks(parse_file(path)):
                self._add_focus(focuses, trees, tree_id, block, path)
        return focuses, dict(trees)

    def _add_focus(self, focuses, trees, tree_id, block: Block, path: Path):
        focus_id = block.value_of("id")
        if not focus_id:
            self.report("R001", ERROR, path, block.line, "focus block has no `id`")
            return

        prerequisites = prerequisite_groups(block)
        exclusive = exclusive_ids(block)

        if focus_id in focuses:
            first = focuses[focus_id]["file"]
            self.report("R002", ERROR, path, block.line,
                        f"duplicate focus id `{focus_id}`, first defined in {first}")
            return

        focuses[focus_id] = {
            "id": focus_id,
            "tree": tree_id,
            "file": str(path.relative_to(self.root)),
            "line": block.line,
            "x": block.value_of("x"),
            "y": block.value_of("y"),
            "relative_position_id": block.value_of("relative_position_id"),
            "icon": block.value_of("icon"),
            "cost": block.value_of("cost"),
            "prerequisites": prerequisites,
            "mutually_exclusive": exclusive,
            "has_completion_reward": block.get("completion_reward") is not None,
            "has_ai_will_do": block.get("ai_will_do") is not None,
            "has_available": block.get("available") is not None,
        }
        trees[tree_id].append(focus_id)

    def check_focus_trees(self, focuses, trees):
        loc_keys = self.all_loc_keys()
        sprites = self.all_sprites()
        known = set(focuses)

        for focus in focuses.values():
            path = self.root / focus["file"]
            line = focus["line"]
            fid = focus["id"]

            for group in focus["prerequisites"]:
                for ref in group:
                    if ref not in known:
                        self.report("R003", ERROR, path, line,
                                    f"focus `{fid}` has prerequisite `{ref}` which does not exist")
            for ref in focus["mutually_exclusive"]:
                if ref not in known:
                    self.report("R004", ERROR, path, line,
                                f"focus `{fid}` is mutually exclusive with `{ref}` which does not exist")
                elif fid not in focuses[ref]["mutually_exclusive"]:
                    self.report("G001", WARNING, path, line,
                                f"mutual exclusivity `{fid}` -> `{ref}` is not symmetric")

            if loc_keys and fid not in loc_keys:
                self.report("R005", ERROR, path, line, f"focus `{fid}` has no localisation key")
            if loc_keys and f"{fid}_desc" not in loc_keys:
                self.report("R006", WARNING, path, line, f"focus `{fid}` has no `{fid}_desc` key")

            icon = focus["icon"]
            if icon and sprites and icon.startswith("GFX_") and icon not in sprites:
                self.report("R007", WARNING, path, line,
                            f"focus `{fid}` uses `{icon}`, which is declared in no .gfx "
                            f"{'(mod or vanilla)' if self.vanilla else '(mod only — vanilla not indexed)'}")

            if not focus["has_completion_reward"]:
                self.report("P001", WARNING, path, line,
                            f"focus `{fid}` has no completion_reward")
            if not focus["has_ai_will_do"]:
                self.report("P002", WARNING, path, line, f"focus `{fid}` has no ai_will_do")

            anchor = focus["relative_position_id"]
            if anchor and anchor not in known:
                self.report("Y001", ERROR, path, line,
                            f"focus `{fid}` anchors to `{anchor}` which does not exist")

        self.check_cycles(focuses)
        self.check_dead_nodes(focuses)
        self.check_geometry(focuses, trees)

    def check_cycles(self, focuses):
        """Depth-first cycle detection over the AND-of-OR prerequisite graph."""
        colour: dict[str, int] = {}
        WHITE, GREY, BLACK = 0, 1, 2

        def visit(fid, stack):
            colour[fid] = GREY
            for group in focuses[fid]["prerequisites"]:
                for ref in group:
                    if ref not in focuses:
                        continue
                    state = colour.get(ref, WHITE)
                    if state == GREY:
                        cycle = " -> ".join(stack[stack.index(ref):] + [ref]) if ref in stack else f"{fid} -> {ref}"
                        focus = focuses[fid]
                        self.report("G002", ERROR, self.root / focus["file"], focus["line"],
                                    f"prerequisite cycle: {cycle}")
                    elif state == WHITE:
                        visit(ref, stack + [ref])
            colour[fid] = BLACK

        sys.setrecursionlimit(10000)
        for fid in focuses:
            if colour.get(fid, WHITE) == WHITE:
                visit(fid, [fid])

    def check_dead_nodes(self, focuses):
        """A focus is unreachable when two *AND-ed* prerequisite groups cannot
        both be satisfied — every option in one is mutually exclusive with every
        option in the other.

        Note the asymmetry with OR: options *within* one group being mutually
        exclusive is the ordinary "two branches converge here" pattern and is
        perfectly reachable. Checking within-group instead of across-group
        reports ~160 healthy focuses in this mod as dead.
        """
        for focus in focuses.values():
            groups = [[r for r in g if r in focuses] for g in focus["prerequisites"]]
            groups = [g for g in groups if g]
            for i, first in enumerate(groups):
                for second in groups[i + 1:]:
                    if all(
                        b in focuses[a]["mutually_exclusive"]
                        for a in first
                        for b in second
                    ):
                        self.report("G003", ERROR, self.root / focus["file"], focus["line"],
                                    f"focus `{focus['id']}` is unreachable: it requires both "
                                    f"{first} and {second}, which are mutually exclusive")

    def check_geometry(self, focuses, trees):
        """Coordinate collisions, after resolving relative_position_id chains."""
        for tree_id, members in trees.items():
            positions: dict[tuple[int, int], str] = {}
            for fid in members:
                resolved = self._resolve_position(fid, focuses, set())
                if resolved is None:
                    continue
                if resolved in positions:
                    focus = focuses[fid]
                    self.report("Y002", WARNING, self.root / focus["file"], focus["line"],
                                f"focus `{fid}` sits at {resolved} in `{tree_id}`, "
                                f"same cell as `{positions[resolved]}`")
                else:
                    positions[resolved] = fid

    def _resolve_position(self, fid, focuses, seen):
        focus = focuses.get(fid)
        if focus is None or fid in seen:
            return None
        try:
            x, y = int(focus["x"]), int(focus["y"])
        except (TypeError, ValueError):
            return None
        anchor = focus["relative_position_id"]
        if not anchor:
            return (x, y)
        base = self._resolve_position(anchor, focuses, seen | {fid})
        if base is None:
            return None
        return (base[0] + x, base[1] + y)

    # -- shared indexes -----------------------------------------------------

    def all_loc_keys(self) -> set[str]:
        keys: set[str] = set()
        for path in sorted(self.root.glob("localisation/**/*.yml")):
            entries, _, _ = parse_localisation(path)
            keys.update(e.key for e in entries)
        return keys

    def all_sprites(self) -> set[str]:
        """Sprites declared by the mod *and* by vanilla.

        Without the vanilla index this reports hundreds of icons as missing
        that resolve perfectly well in game — most of the mod's focus icons
        are vanilla's `GFX_goal_generic_*`.
        """
        if self._sprites is None:
            self._sprites = self._scan_sprites(self.root)
            if self.vanilla:
                self._sprites |= self._scan_sprites(self.vanilla)
        return self._sprites

    @staticmethod
    def _scan_sprites(root: Path) -> set[str]:
        names: set[str] = set()
        for path in sorted(root.rglob("*.gfx")):
            text = path.read_text(encoding="utf-8-sig", errors="replace")
            names.update(re.findall(r'name\s*=\s*"(GFX_[A-Za-z0-9_.\-]+)"', text))
        return names

    @property
    def vanilla(self) -> Path | None:
        """`$HOI4_VANILLA_ROOT`, when it is present and looks like an install."""
        if self._vanilla is _UNSET:
            raw = os.environ.get("HOI4_VANILLA_ROOT", "")
            candidate = Path(raw).expanduser() if raw else None
            self._vanilla = (
                candidate
                if candidate and (candidate / "common").is_dir()
                else None
            )
        return self._vanilla

    # -- ideas --------------------------------------------------------------

    def check_idea_pictures(self):
        """`picture = X` on an idea resolves to the sprite `GFX_idea_X`.

        Two engine behaviours make a naive check wrong, and both were found by
        checking against vanilla rather than by reading documentation:

        1. **Verbatim fallback.** If `GFX_idea_<picture>` does not exist the
           engine uses `<picture>` as a sprite name directly. Vanilla itself
           relies on this in 20 of its own ideas, so `picture = GFX_idea_X`
           is legal despite looking like a doubled prefix.
        2. **Graphical-culture variants.** Generic advisor portraits are
           declared as `GFX_idea_<name>_russian_2d`, `_western_european_2d`
           and so on, and the suffix is chosen at runtime. A bare `<name>`
           resolves through any of them.
        """
        sprites = self.all_sprites()
        idea_prefixes = {s[len("GFX_idea_"):] for s in sprites if s.startswith("GFX_idea_")}

        for path in self.scan("common/ideas/**/*.txt"):
            text = path.read_text(encoding="utf-8-sig", errors="replace")
            for number, line in enumerate(strip_comments_and_strings(text).splitlines(), start=1):
                match = re.search(r"picture\s*=\s*([A-Za-z0-9_]+)", line)
                if not match:
                    continue
                value = match.group(1)
                if (
                    f"GFX_idea_{value}" in sprites
                    or value in sprites
                    or any(p.startswith(value + "_") for p in idea_prefixes)
                ):
                    continue
                self.report(
                    "R008", WARNING, path, number,
                    f"idea picture `{value}` resolves to no sprite; "
                    f"neither `GFX_idea_{value}` nor `{value}` is declared in any .gfx",
                )

    # -- entry point --------------------------------------------------------

    def run(self):
        # Focuses are collected first so the voice check can tell authored
        # focus prose from inherited UI strings.
        focuses, trees = self.collect_focuses()
        self.focus_ids = set(focuses)

        self.check_structure()
        self.check_localisation()
        self.check_engine()
        self.check_idea_pictures()
        self.check_focus_trees(focuses, trees)
        return self.findings


def changed_files(root: Path) -> set[Path]:
    """Files this branch changed relative to the upstream merge base."""
    base = subprocess.run(
        ["git", "merge-base", "upstream/master", "HEAD"],
        cwd=root, capture_output=True, text=True,
    )
    if base.returncode != 0:
        print("warning: no upstream/master; linting everything", file=sys.stderr)
        return None
    diff = subprocess.run(
        ["git", "diff", "--name-only", base.stdout.strip()],
        cwd=root, capture_output=True, text=True, check=True,
    )
    return {root / name for name in diff.stdout.split("\n") if name}


def main() -> int:
    parser = argparse.ArgumentParser(description="T1 lint suite for the RoR fork")
    parser.add_argument("--root", type=Path, default=REPO)
    parser.add_argument("--json", type=Path, help="write findings as JSON")
    parser.add_argument("--baseline", type=Path, help="report only findings absent from this baseline")
    parser.add_argument("--write-baseline", type=Path, help="write current findings as a baseline")
    parser.add_argument("--changed", action="store_true", help="only files changed vs upstream merge-base")
    parser.add_argument("--warnings-as-errors", action="store_true")
    parser.add_argument("--quiet", action="store_true", help="summary only")
    args = parser.parse_args()

    limit = changed_files(args.root) if args.changed else None

    # Whether vanilla was indexed changes the result set enormously — focus
    # icon findings alone go from 690 to 14 — so it is recorded in the
    # baseline and checked on every comparison. A baseline built in one mode
    # and used in the other reports hundreds of phantom regressions.
    lint = Lint(args.root, limit)
    findings = lint.run()
    has_vanilla = lint.vanilla is not None
    if not has_vanilla:
        print(
            "note: HOI4_VANILLA_ROOT is unset or not an install; vanilla sprites "
            "and references cannot be resolved. Run via direnv, or expect noise.",
            file=sys.stderr,
        )

    if args.write_baseline:
        args.write_baseline.parent.mkdir(parents=True, exist_ok=True)
        args.write_baseline.write_text(
            json.dumps(
                {"vanilla_indexed": has_vanilla, "keys": sorted({f.key() for f in findings})},
                indent=1, ensure_ascii=False,
            )
        )
        print(f"baseline written: {len(findings)} findings "
              f"(vanilla_indexed={has_vanilla}) -> {args.write_baseline}")
        return 0

    suppressed = 0
    if args.baseline and args.baseline.exists():
        data = json.loads(args.baseline.read_text())
        if data.get("vanilla_indexed", False) != has_vanilla:
            print(
                f"WARNING: baseline was built with vanilla_indexed="
                f"{data.get('vanilla_indexed')}, this run has {has_vanilla}. "
                "The comparison is not meaningful — fix the environment rather "
                "than rewriting the baseline.",
                file=sys.stderr,
            )
        known = set(data["keys"])
        before = len(findings)
        findings = [f for f in findings if f.key() not in known]
        suppressed = before - len(findings)

    errors = [f for f in findings if f.severity == ERROR]
    warnings = [f for f in findings if f.severity == WARNING]

    if not args.quiet:
        for finding in sorted(findings, key=lambda f: (f.severity != ERROR, f.file, f.line)):
            print(finding)
        if findings:
            print()

    by_code = defaultdict(int)
    for f in findings:
        by_code[f.code] += 1
    if by_code:
        print("by check:")
        for code, count in sorted(by_code.items(), key=lambda kv: -kv[1]):
            print(f"  {count:>6}  {code}")

    tail = f", {suppressed} suppressed by baseline" if suppressed else ""
    print(f"\n{len(errors)} error(s), {len(warnings)} warning(s){tail}")

    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(
            json.dumps([asdict(f) for f in findings], indent=1, ensure_ascii=False)
        )

    return 1 if errors or (args.warnings_as_errors and warnings) else 0


if __name__ == "__main__":
    raise SystemExit(main())

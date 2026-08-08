"""Minimal Clausewitz script parser.

Hand-rolled on purpose. `pyradox` and friends bitrot against new HOI4 versions,
and the plan needs exactly two things from a parser: brace/line fidelity for
linting, and enough structure to walk focus trees. Everything else is noise.

The parser is deliberately permissive. HOI4 itself accepts a lot of sloppiness
(stray closing braces at top level, duplicate keys, unquoted strings with odd
characters), and a parser stricter than the engine would report defects the
game does not have. Structural problems are *reported*, not raised.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path


# Clausewitz uses `=` for assignment and `<` `>` for numeric comparison.
# `<=` and `>=` are NOT supported by the engine; the lint checks for them
# separately rather than the parser accepting them.
_OPERATORS = ("=", "<", ">")

_TOKEN = re.compile(
    r"""
      (?P<comment>\#[^\n]*)
    | (?P<string>"(?:[^"\\]|\\.)*")
    | (?P<op><|>|=)
    | (?P<brace>[{}])
    | (?P<bare>[^\s{}"=<>#]+)
    """,
    re.VERBOSE,
)


@dataclass
class Node:
    """One `key = value` pair. `value` is a str, or a Block for `key = { ... }`."""

    key: str
    op: str
    value: "str | Block"
    line: int

    @property
    def is_block(self) -> bool:
        return isinstance(self.value, Block)


@dataclass
class Block:
    """A `{ ... }` body: named children plus bare list items like `{ a b c }`."""

    nodes: list[Node] = field(default_factory=list)
    items: list[str] = field(default_factory=list)
    line: int = 0

    def get(self, key: str) -> Node | None:
        """Last node with this key. Clausewitz lets later keys win."""
        found = None
        for node in self.nodes:
            if node.key == key:
                found = node
        return found

    def get_all(self, key: str) -> list[Node]:
        return [n for n in self.nodes if n.key == key]

    def value_of(self, key: str, default: str | None = None) -> str | None:
        node = self.get(key)
        if node is None or node.is_block:
            return default
        return node.value

    def walk(self):
        """Depth-first over every node beneath this block."""
        for node in self.nodes:
            yield node
            if node.is_block:
                yield from node.value.walk()


@dataclass
class ParseResult:
    path: Path
    root: Block
    text: str
    # Structural complaints. Reported rather than raised: see module docstring.
    problems: list[tuple[int, str]] = field(default_factory=list)


def _tokenise(text: str):
    """Yield (kind, value, line). Comments are dropped."""
    line = 1
    pos = 0
    length = len(text)
    while pos < length:
        char = text[pos]
        if char == "\n":
            line += 1
            pos += 1
            continue
        if char.isspace():
            pos += 1
            continue
        match = _TOKEN.match(text, pos)
        if match is None:
            if char == '"':
                # A quote the string pattern could not close. The engine reads
                # to end of line and produces a silently wrong value, so this
                # is a real defect rather than a parser limitation.
                yield "unterminated", '"', line
            # Skip the character rather than abort — the engine does the same
            # and the rest of the file is usually still useful.
            pos += 1
            continue
        kind = match.lastgroup
        value = match.group()
        if kind != "comment":
            yield kind, value, line
        line += value.count("\n")
        pos = match.end()


def parse_text(text: str, path: Path | None = None) -> ParseResult:
    root = Block(line=1)
    result = ParseResult(path=path or Path("<text>"), root=root, text=text)

    stack: list[Block] = [root]
    pending_key: str | None = None
    pending_op: str | None = None
    pending_line = 0

    for kind, value, line in _tokenise(text):
        if kind == "unterminated":
            result.problems.append((line, "unterminated quoted string"))
            continue

        if kind == "op":
            if pending_key is None:
                result.problems.append((line, f"operator `{value}` with no left-hand side"))
                continue
            pending_op = value
            continue

        if kind == "brace" and value == "{":
            block = Block(line=line)
            if pending_key is not None and pending_op is not None:
                stack[-1].nodes.append(Node(pending_key, pending_op, block, pending_line))
                pending_key = pending_op = None
            else:
                # Anonymous block, e.g. inside a list of blocks.
                stack[-1].nodes.append(Node("", "=", block, line))
                pending_key = pending_op = None
            stack.append(block)
            continue

        if kind == "brace" and value == "}":
            if len(stack) == 1:
                result.problems.append((line, "extra closing brace"))
                continue
            stack.pop()
            continue

        # A bare word or quoted string.
        token = value[1:-1] if kind == "string" else value
        if pending_key is not None and pending_op is not None:
            stack[-1].nodes.append(Node(pending_key, pending_op, token, pending_line))
            pending_key = pending_op = None
        elif pending_key is not None:
            # Previous key had no operator — both are list items.
            stack[-1].items.append(pending_key)
            pending_key, pending_line = token, line
        else:
            pending_key, pending_line = token, line

    if pending_key is not None:
        stack[-1].items.append(pending_key)

    if len(stack) > 1:
        result.problems.append(
            (stack[-1].line, f"unclosed brace opened here; {len(stack) - 1} block(s) never closed")
        )

    return result


def parse_file(path: Path) -> ParseResult:
    # utf-8-sig strips the BOM if present. Whether the BOM *should* be there is
    # a lint question (localisation requires it), not a parsing one.
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    return parse_text(text, path)


def strip_comments_and_strings(text: str) -> str:
    """Blank out comments and string bodies, preserving offsets and newlines.

    Used by lints that scan raw text for forbidden operators: `>=` inside a
    comment is not a defect, and neither is one inside a localisation string.
    """
    out = list(text)
    i, n = 0, len(text)
    while i < n:
        char = text[i]
        if char == "#":
            while i < n and text[i] != "\n":
                out[i] = " "
                i += 1
        elif char == '"':
            out[i] = " "
            i += 1
            while i < n and text[i] != '"':
                if text[i] != "\n":
                    out[i] = " "
                i += 1
            if i < n:
                out[i] = " "
                i += 1
        else:
            i += 1
    return "".join(out)


# --- localisation ----------------------------------------------------------

# `key:0 "Text"` and `key: "Text"` are both accepted by the engine; the plan
# bans the `:0` form for consistency. The version number is optional.
LOC_ENTRY = re.compile(r'^(?P<indent>\s*)(?P<key>[A-Za-z0-9_.\-]+):(?P<version>\d*)\s*"(?P<text>.*)"\s*$')


@dataclass
class LocEntry:
    key: str
    text: str
    line: int
    version: str
    indent: str


def parse_localisation(path: Path) -> tuple[list[LocEntry], bool, str]:
    """Return (entries, has_bom, language_header)."""
    raw = path.read_bytes()
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig", errors="replace")

    entries: list[LocEntry] = []
    header = ""
    for number, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.endswith(":") and " " not in stripped:
            header = stripped[:-1]
            continue
        match = LOC_ENTRY.match(line)
        if match:
            entries.append(
                LocEntry(
                    key=match.group("key"),
                    text=match.group("text"),
                    line=number,
                    version=match.group("version"),
                    indent=match.group("indent"),
                )
            )
    return entries, has_bom, header

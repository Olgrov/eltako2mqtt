#!/usr/bin/env python3
"""Check local Markdown destinations and GitHub/Jekyll heading anchors offline."""

from collections import Counter
from pathlib import Path
import re
import sys
import unicodedata
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]


def strip_code_fences(text):
    """Ignore fenced examples, but keep source line numbers for diagnostics."""
    lines = []
    fence = None
    for line in text.splitlines():
        match = re.match(r"^\s{0,3}(`{3,}|~{3,})", line)
        if match:
            marker = match[1]
            if fence is None:
                fence = marker
            elif marker[0] == fence[0] and len(marker) >= len(fence):
                fence = None
            lines.append("")
        else:
            lines.append(line if fence is None else "")
    return lines


def heading_ids(text):
    """Return GitHub-style automatic IDs, including duplicate-heading suffixes."""
    ids = set(re.findall(r'\bid=["\']([^"\']+)["\']', text))
    seen = Counter()
    lines = strip_code_fences(text)
    for index, line in enumerate(lines):
        match = re.match(r"^\s{0,3}#{1,6}\s+(.+?)(?:\s+#+)?\s*$", line)
        heading = match[1] if match else None
        if heading is None and index + 1 < len(lines) and line.strip():
            if re.fullmatch(r"\s{0,3}(?:=+|-+)\s*", lines[index + 1]):
                heading = line.strip()
        if heading is None:
            continue
        heading = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", heading)
        heading = re.sub(r"<[^>]+>", "", heading).lower()
        slug = "".join(
            char for char in heading
            if char in " -_" or unicodedata.category(char)[0] in ("L", "N", "M")
        ).replace(" ", "-")
        suffix = seen[slug]
        seen[slug] += 1
        ids.add(slug + (f"-{suffix}" if suffix else ""))
    return ids


def markdown_links(text):
    """Yield inline/image, autolink and reference destinations with source lines."""
    lines = strip_code_fences(text)
    definitions = {}
    for number, line in enumerate(lines, 1):
        match = re.match(r"^\s{0,3}\[([^\]]+)\]:\s*<?([^\s>]+)>?", line)
        if match:
            definitions[match[1].strip().casefold()] = (match[2], number)
    for number, line in enumerate(lines, 1):
        if re.match(r"^\s{0,3}\[[^\]]+\]:", line):
            continue
        for match in re.finditer(r"!?\[[^\]]*\]\(\s*(?:<([^>]+)>|([^\s)]+))", line):
            yield number, match[1] or match[2]
        for match in re.finditer(r"<((?:https?://|mailto:)[^>]+)>", line):
            yield number, match[1]
        for match in re.finditer(r"!?\[([^\]]+)\]\[([^\]]*)\]", line):
            key = (match[2] or match[1]).strip().casefold()
            if key not in definitions:
                yield number, f"unresolved-reference:{key}"
            else:
                yield number, definitions[key][0]
    # Definitions also cover shortcut links and otherwise unused references.
    for target, number in definitions.values():
        yield number, target


def check_documents(root=ROOT):
    root = Path(root).resolve()
    documents = sorted(root.glob("*.md")) + sorted((root / "docs").rglob("*.md"))
    problems = []
    checked = 0
    anchors = {}
    for document in documents:
        for number, target in markdown_links(document.read_text(encoding="utf-8")):
            parsed = urlsplit(target)
            if parsed.scheme == "unresolved-reference":
                problems.append(f"{document.relative_to(root)}:{number}: {target}")
                continue
            if parsed.scheme or parsed.netloc:
                continue
            checked += 1
            destination = (document.parent / unquote(parsed.path)).resolve() if parsed.path else document
            try:
                destination.relative_to(root)
            except ValueError:
                problems.append(f"{document.relative_to(root)}:{number}: target escapes repository: {target}")
                continue
            if not destination.is_file():
                problems.append(f"{document.relative_to(root)}:{number}: missing file: {target}")
                continue
            if parsed.fragment:
                if destination.suffix.lower() not in (".md", ".html"):
                    problems.append(f"{document.relative_to(root)}:{number}: unsupported fragment target: {target}")
                    continue
                if destination not in anchors:
                    anchors[destination] = heading_ids(destination.read_text(encoding="utf-8"))
                if unquote(parsed.fragment) not in anchors[destination]:
                    problems.append(f"{document.relative_to(root)}:{number}: missing anchor: {target}")
    return checked, problems


def main():
    checked, problems = check_documents()
    for problem in problems:
        print(problem, file=sys.stderr)
    print(f"Checked {checked} local Markdown links and anchors; {len(problems)} errors.")
    return bool(problems)


if __name__ == "__main__":
    raise SystemExit(main())

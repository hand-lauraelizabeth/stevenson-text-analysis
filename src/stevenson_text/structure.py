from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Iterable

from .corpus import tokenize

@dataclass(frozen=True)
class TextSection:
    index: int
    heading: str
    text: str

    @property
    def tokens(self) -> list[str]:
        return tokenize(self.text)

def split_by_headings(text: str, headings: Iterable[str]) -> list[TextSection]:
    """Split a text at known scholarly/narrative headings.

    Exact heading strings are supplied as data rather than hard-coded into the
    parser so editorial structure remains inspectable and revisable.
    """
    heading_list = [h.strip() for h in headings if h.strip()]
    if not heading_list:
        return [TextSection(index=1, heading="Full text", text=text.strip())]

    lookup = {h.casefold(): h for h in heading_list}
    lines = text.splitlines()
    sections: list[TextSection] = []
    current_heading = "Front matter"
    buffer: list[str] = []

    def flush() -> None:
        nonlocal buffer
        body = "\n".join(buffer).strip()
        if body:
            sections.append(
                TextSection(index=len(sections) + 1, heading=current_heading, text=body)
            )
        buffer = []

    for line in lines:
        stripped = re.sub(r"\s+", " ", line.strip())
        key = stripped.casefold()
        if key in lookup:
            flush()
            current_heading = lookup[key]
        else:
            buffer.append(line)
    flush()
    return sections

def _phrase_tokens(alias: str) -> tuple[str, ...]:
    return tuple(tokenize(alias))

def count_alias_groups(tokens: list[str], alias_groups: dict[str, list[str]]) -> dict[str, int]:
    """Count canonical entities while preventing overlap among aliases in a group.

    Longer aliases are matched first. Once an alias consumes a token span, a
    shorter alias from the same canonical group cannot count the same span.
    """
    lower = [token.lower() for token in tokens]
    result: dict[str, int] = {}

    for canonical, aliases in alias_groups.items():
        patterns = sorted(
            {_phrase_tokens(alias) for alias in aliases if _phrase_tokens(alias)},
            key=len,
            reverse=True,
        )
        consumed: set[int] = set()
        count = 0
        for pattern in patterns:
            width = len(pattern)
            for start in range(0, len(lower) - width + 1):
                positions = range(start, start + width)
                if any(pos in consumed for pos in positions):
                    continue
                if tuple(lower[start:start + width]) == pattern:
                    count += 1
                    consumed.update(positions)
        result[canonical] = count
    return result

def section_entity_matrix(
    sections: list[TextSection], alias_groups: dict[str, list[str]]
) -> list[dict[str, int | str]]:
    rows = []
    for section in sections:
        rows.append({
            "section": section.index,
            "heading": section.heading,
            "tokens": len(section.tokens),
            **count_alias_groups(section.tokens, alias_groups),
        })
    return rows

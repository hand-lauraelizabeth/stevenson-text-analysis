from __future__ import annotations

from collections import Counter
from itertools import combinations
from typing import Iterable

from .structure import TextSection, count_alias_groups

def cooccurrence_network(
    sections: Iterable[TextSection],
    alias_groups: dict[str, list[str]],
    min_section_mentions: int = 1,
) -> tuple[list[dict[str, int | str]], list[dict[str, int | str]]]:
    """Build a section-based character co-occurrence network.

    Two canonical entities are connected when both are mentioned in the same
    section. Edge weight is the number of sections in which that pair co-occurs.
    """
    node_sections = Counter()
    edge_sections = Counter()

    for section in sections:
        counts = count_alias_groups(section.tokens, alias_groups)
        present = sorted(
            canonical for canonical, count in counts.items()
            if count >= min_section_mentions
        )
        node_sections.update(present)
        edge_sections.update(combinations(present, 2))

    nodes = [
        {"id": node, "sections_present": count}
        for node, count in sorted(node_sections.items())
    ]
    edges = [
        {"source": source, "target": target, "weight": weight}
        for (source, target), weight in sorted(
            edge_sections.items(), key=lambda item: (-item[1], item[0])
        )
    ]
    return nodes, edges

from __future__ import annotations

import csv
from dataclasses import dataclass
from io import StringIO
from typing import Iterable

from .corpus import tokenize
from .phrases import phrase_occurrences
from .structure import TextSection, count_alias_groups

@dataclass(frozen=True)
class ResearchScene:
    scene_id: str
    section: str
    title: str
    anchor_phrase: str
    scene_type: str
    rationale: str

def load_scenes_csv(text: str) -> list[ResearchScene]:
    reader = csv.DictReader(StringIO(text))
    return [
        ResearchScene(
            scene_id=(row.get("scene_id") or "").strip(),
            section=(row.get("section") or "").strip(),
            title=(row.get("title") or "").strip(),
            anchor_phrase=(row.get("anchor_phrase") or "").strip(),
            scene_type=(row.get("scene_type") or "").strip(),
            rationale=(row.get("rationale") or "").strip(),
        )
        for row in reader
    ]

def validate_scenes(scenes: Iterable[ResearchScene]) -> list[dict[str, str]]:
    issues = []
    seen = set()
    for scene in scenes:
        if not scene.scene_id:
            issues.append({"scene_id": "", "field": "scene_id", "issue": "missing id"})
        elif scene.scene_id in seen:
            issues.append({"scene_id": scene.scene_id, "field": "scene_id", "issue": "duplicate id"})
        seen.add(scene.scene_id)

        if not scene.section:
            issues.append({"scene_id": scene.scene_id, "field": "section", "issue": "missing section"})
        if not scene.anchor_phrase:
            issues.append({"scene_id": scene.scene_id, "field": "anchor_phrase", "issue": "missing anchor"})
        if not scene.title:
            issues.append({"scene_id": scene.scene_id, "field": "title", "issue": "missing title"})
    return issues

def resolve_scene_windows(
    sections: Iterable[TextSection],
    scenes: Iterable[ResearchScene],
    window: int = 60,
) -> list[dict[str, str | int]]:
    """Resolve hand-curated research scenes to token windows within authored sections."""
    section_map = {section.heading.casefold(): section for section in sections}
    rows = []

    for scene in scenes:
        section = section_map.get(scene.section.casefold())
        if section is None:
            rows.append({
                "scene_id": scene.scene_id,
                "section": scene.section,
                "title": scene.title,
                "scene_type": scene.scene_type,
                "anchor_phrase": scene.anchor_phrase,
                "status": "missing_section",
                "match_count": 0,
                "match_index": 0,
                "start_position": "",
                "end_position": "",
                "window_text": "",
                "rationale": scene.rationale,
            })
            continue

        hits = phrase_occurrences(section.text, scene.anchor_phrase, window=window)
        if not hits:
            rows.append({
                "scene_id": scene.scene_id,
                "section": scene.section,
                "title": scene.title,
                "scene_type": scene.scene_type,
                "anchor_phrase": scene.anchor_phrase,
                "status": "unresolved",
                "match_count": 0,
                "match_index": 0,
                "start_position": "",
                "end_position": "",
                "window_text": "",
                "rationale": scene.rationale,
            })
            continue

        for index, hit in enumerate(hits, start=1):
            rows.append({
                "scene_id": scene.scene_id,
                "section": scene.section,
                "title": scene.title,
                "scene_type": scene.scene_type,
                "anchor_phrase": scene.anchor_phrase,
                "status": "resolved" if len(hits) == 1 else "ambiguous",
                "match_count": len(hits),
                "match_index": index,
                "start_position": hit["start_position"],
                "end_position": hit["end_position"],
                "window_text": " ".join(
                    part for part in [str(hit["left"]), str(hit["phrase"]), str(hit["right"])] if part
                ),
                "rationale": scene.rationale,
            })
    return rows

def scene_entity_matrix(
    scene_rows: Iterable[dict[str, str | int]],
    alias_groups: dict[str, list[str]],
) -> list[dict[str, str | int]]:
    rows = []
    for scene in scene_rows:
        if scene["status"] not in {"resolved", "ambiguous"}:
            continue
        tokens = tokenize(str(scene["window_text"]))
        rows.append({
            "scene_id": str(scene["scene_id"]),
            "section": str(scene["section"]),
            "title": str(scene["title"]),
            "scene_type": str(scene["scene_type"]),
            "tokens": len(tokens),
            **count_alias_groups(tokens, alias_groups),
        })
    return rows

def scene_term_matrix(
    scene_rows: Iterable[dict[str, str | int]],
    terms: Iterable[str],
) -> list[dict[str, str | int]]:
    terms = [term.casefold() for term in terms]
    rows = []
    for scene in scene_rows:
        if scene["status"] not in {"resolved", "ambiguous"}:
            continue
        tokens = tokenize(str(scene["window_text"]))
        rows.append({
            "scene_id": str(scene["scene_id"]),
            "section": str(scene["section"]),
            "title": str(scene["title"]),
            "scene_type": str(scene["scene_type"]),
            "tokens": len(tokens),
            **{term: tokens.count(term) for term in terms},
        })
    return rows

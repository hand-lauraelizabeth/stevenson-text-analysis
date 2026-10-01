from __future__ import annotations

from collections import Counter
import csv
from dataclasses import dataclass
from io import StringIO
from typing import Iterable

from .phrases import phrase_occurrences
from .structure import TextSection

ALLOWED_CATEGORIES = {
    "embodied_transformation",
    "handwriting_identity",
    "document_transfer",
    "touch_relation",
    "readerly_mediation",
    "figuration_idiom",
}

ALLOWED_CLAIM_ROLES = {"core", "supporting", "counterexample", "context"}

@dataclass(frozen=True)
class ResearchAnnotation:
    annotation_id: str
    section: str
    anchor_phrase: str
    category: str
    subcategory: str
    actors: str
    document_ref: str
    claim_role: str
    note: str

def load_annotations_csv(text: str) -> list[ResearchAnnotation]:
    reader = csv.DictReader(StringIO(text))
    rows = []
    for row in reader:
        rows.append(ResearchAnnotation(
            annotation_id=(row.get("annotation_id") or "").strip(),
            section=(row.get("section") or "").strip(),
            anchor_phrase=(row.get("anchor_phrase") or "").strip(),
            category=(row.get("category") or "").strip(),
            subcategory=(row.get("subcategory") or "").strip(),
            actors=(row.get("actors") or "").strip(),
            document_ref=(row.get("document_ref") or "").strip(),
            claim_role=(row.get("claim_role") or "").strip(),
            note=(row.get("note") or "").strip(),
        ))
    return rows

def validate_annotations(annotations: Iterable[ResearchAnnotation]) -> list[dict[str, str]]:
    issues = []
    seen = set()
    for annotation in annotations:
        if not annotation.annotation_id:
            issues.append({"annotation_id": "", "field": "annotation_id", "issue": "missing id"})
        elif annotation.annotation_id in seen:
            issues.append({"annotation_id": annotation.annotation_id, "field": "annotation_id", "issue": "duplicate id"})
        seen.add(annotation.annotation_id)

        if not annotation.anchor_phrase:
            issues.append({"annotation_id": annotation.annotation_id, "field": "anchor_phrase", "issue": "missing anchor"})
        if annotation.category not in ALLOWED_CATEGORIES:
            issues.append({"annotation_id": annotation.annotation_id, "field": "category", "issue": "unknown category"})
        if annotation.claim_role not in ALLOWED_CLAIM_ROLES:
            issues.append({"annotation_id": annotation.annotation_id, "field": "claim_role", "issue": "unknown claim role"})
    return issues

def resolve_annotation_anchors(
    text: str,
    annotations: Iterable[ResearchAnnotation],
    window: int = 12,
    sections: Iterable[TextSection] | None = None,
) -> list[dict[str, str | int]]:
    """Link manual annotations to token-aware anchors.

    When authored sections are supplied, an annotation with an expected
    section is resolved inside that section rather than against the entire
    document. This prevents a globally repeated phrase from being marked
    ambiguous when its declared section contains a single match.
    """
    section_map = (
        {section.heading.casefold(): section for section in sections}
        if sections is not None
        else {}
    )
    rows = []

    for annotation in annotations:
        search_text = text
        search_scope = "full_text"

        if section_map and annotation.section:
            section = section_map.get(annotation.section.casefold())
            if section is None:
                rows.append({
                    "annotation_id": annotation.annotation_id,
                    "category": annotation.category,
                    "claim_role": annotation.claim_role,
                    "section_expected": annotation.section,
                    "search_scope": "missing_section",
                    "anchor_phrase": annotation.anchor_phrase,
                    "match_count": 0,
                    "match_index": 0,
                    "left": "",
                    "matched_text": "",
                    "right": "",
                    "status": "missing_section",
                })
                continue
            search_text = section.text
            search_scope = section.heading

        hits = phrase_occurrences(search_text, annotation.anchor_phrase, window=window)
        if not hits:
            rows.append({
                "annotation_id": annotation.annotation_id,
                "category": annotation.category,
                "claim_role": annotation.claim_role,
                "section_expected": annotation.section,
                "search_scope": search_scope,
                "anchor_phrase": annotation.anchor_phrase,
                "match_count": 0,
                "match_index": 0,
                "left": "",
                "matched_text": "",
                "right": "",
                "status": "unresolved",
            })
            continue

        for index, hit in enumerate(hits, start=1):
            rows.append({
                "annotation_id": annotation.annotation_id,
                "category": annotation.category,
                "claim_role": annotation.claim_role,
                "section_expected": annotation.section,
                "search_scope": search_scope,
                "anchor_phrase": annotation.anchor_phrase,
                "match_count": len(hits),
                "match_index": index,
                "left": str(hit["left"]),
                "matched_text": str(hit["phrase"]),
                "right": str(hit["right"]),
                "status": "resolved" if len(hits) == 1 else "ambiguous",
            })
    return rows

def annotation_summary(annotations: Iterable[ResearchAnnotation]) -> list[dict[str, str | int]]:
    counts = Counter((a.category, a.claim_role) for a in annotations)
    return [
        {"category": category, "claim_role": role, "annotations": count}
        for (category, role), count in sorted(counts.items())
    ]

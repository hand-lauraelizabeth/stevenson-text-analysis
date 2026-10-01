from __future__ import annotations

from collections import Counter
from dataclasses import asdict
from typing import Iterable

from .annotations import ResearchAnnotation

def _by_id(annotations: Iterable[ResearchAnnotation]) -> dict[str, ResearchAnnotation]:
    return {annotation.annotation_id: annotation for annotation in annotations if annotation.annotation_id}

def compare_annotation_sets(
    first: Iterable[ResearchAnnotation],
    second: Iterable[ResearchAnnotation],
    field: str = "category",
) -> list[dict[str, str | bool]]:
    """Align two annotation sets by stable annotation id and compare one field."""
    if field not in ResearchAnnotation.__dataclass_fields__:
        raise ValueError(f"Unknown annotation field: {field}")

    left = _by_id(first)
    right = _by_id(second)
    rows = []
    for annotation_id in sorted(left.keys() | right.keys()):
        a = left.get(annotation_id)
        b = right.get(annotation_id)
        a_value = "" if a is None else str(getattr(a, field))
        b_value = "" if b is None else str(getattr(b, field))
        rows.append({
            "annotation_id": annotation_id,
            "coder_a": a_value,
            "coder_b": b_value,
            "agreement": bool(a is not None and b is not None and a_value == b_value),
            "status": "matched" if a is not None and b is not None else "missing_from_one_set",
        })
    return rows

def observed_agreement(rows: Iterable[dict[str, str | bool]]) -> float:
    matched = [row for row in rows if row["status"] == "matched"]
    if not matched:
        return 0.0
    return sum(bool(row["agreement"]) for row in matched) / len(matched)

def cohens_kappa(rows: Iterable[dict[str, str | bool]]) -> float:
    """Compute Cohen's kappa for matched nominal labels."""
    matched = [row for row in rows if row["status"] == "matched"]
    if not matched:
        return 0.0

    n = len(matched)
    observed = sum(bool(row["agreement"]) for row in matched) / n
    a_counts = Counter(str(row["coder_a"]) for row in matched)
    b_counts = Counter(str(row["coder_b"]) for row in matched)
    labels = a_counts.keys() | b_counts.keys()
    expected = sum((a_counts[label] / n) * (b_counts[label] / n) for label in labels)
    if expected == 1.0:
        # Kappa is undefined when the expected-agreement denominator is zero,
        # for example when both coders assign the same single category to all
        # matched units. Returning 1.0 would overstate what the statistic says.
        return float("nan")
    return (observed - expected) / (1.0 - expected)

def agreement_summary(
    first: Iterable[ResearchAnnotation],
    second: Iterable[ResearchAnnotation],
    field: str = "category",
) -> dict[str, float | int | str]:
    rows = compare_annotation_sets(first, second, field=field)
    matched = [row for row in rows if row["status"] == "matched"]
    return {
        "field": field,
        "matched_annotations": len(matched),
        "total_ids": len(rows),
        "observed_agreement": observed_agreement(rows),
        "cohens_kappa": cohens_kappa(rows),
    }

from __future__ import annotations

from collections import Counter
from typing import Iterable, Sequence

from .corpus import tokenize

def validate_lemma_groups(groups: dict[str, list[str]]) -> list[dict[str, str]]:
    """Validate an explicit research lexicon used for lemma-aware retrieval."""
    issues = []
    seen: dict[str, str] = {}
    for lemma, forms in groups.items():
        if not lemma.strip():
            issues.append({"lemma": lemma, "form": "", "issue": "empty lemma"})
        if not forms:
            issues.append({"lemma": lemma, "form": "", "issue": "no forms"})
        for form in forms:
            key = form.casefold().strip()
            if not key:
                issues.append({"lemma": lemma, "form": form, "issue": "empty form"})
                continue
            if key in seen and seen[key] != lemma:
                issues.append({
                    "lemma": lemma,
                    "form": form,
                    "issue": f"form already assigned to {seen[key]}",
                })
            else:
                seen[key] = lemma
    return issues

def lemma_lookup(groups: dict[str, list[str]]) -> dict[str, str]:
    """Create a surface-form→lemma lookup from an explicit lexicon."""
    lookup = {}
    for lemma, forms in groups.items():
        for form in forms:
            lookup[form.casefold()] = lemma.casefold()
    return lookup

def lemmatize_tokens(
    tokens: Sequence[str],
    groups: dict[str, list[str]],
    preserve_unknown: bool = True,
) -> list[str]:
    lookup = lemma_lookup(groups)
    output = []
    for token in tokens:
        key = token.casefold()
        if key in lookup:
            output.append(lookup[key])
        elif preserve_unknown:
            output.append(key)
    return output

def lemma_counts(
    tokens: Sequence[str],
    groups: dict[str, list[str]],
    lemmas: Iterable[str] | None = None,
) -> dict[str, int]:
    """Count declared morphological families without pretending to infer morphology."""
    selected = {lemma.casefold() for lemma in (lemmas or groups.keys())}
    lookup = lemma_lookup(groups)
    counts = Counter()
    for token in tokens:
        lemma = lookup.get(token.casefold())
        if lemma in selected:
            counts[lemma] += 1
    return {lemma: counts[lemma] for lemma in sorted(selected)}

def lemma_concordance(
    text: str,
    lemma: str,
    groups: dict[str, list[str]],
    window: int = 8,
) -> list[dict[str, str | int]]:
    """Return contexts for every declared surface form belonging to a lemma."""
    lemma_key = lemma.casefold()
    forms = {form.casefold() for form in groups.get(lemma_key, groups.get(lemma, []))}
    if not forms:
        return []

    original = tokenize(text, lowercase=False)
    lowered = [token.casefold() for token in original]
    hits = []
    for index, surface in enumerate(lowered):
        if surface not in forms:
            continue
        hits.append({
            "position": index,
            "lemma": lemma_key,
            "surface": original[index],
            "left": " ".join(original[max(0, index-window):index]),
            "right": " ".join(original[index+1:index+1+window]),
        })
    return hits

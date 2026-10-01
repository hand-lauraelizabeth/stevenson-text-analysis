from __future__ import annotations

from collections import Counter
from math import log
from statistics import mean, pstdev
from typing import Sequence

from .corpus import segment_tokens


def dispersion_profile(
    tokens: Sequence[str], term: str, segments: int = 10
) -> dict[str, float | int | str]:
    """Describe how evenly a term is distributed across sequential segments.

    Range reports the share of segments containing the term. Coefficient of
    variation (CV) reports unevenness relative to the mean segment count.
    """
    slices = segment_tokens(tokens, segments)
    counts = [segment.count(term.lower()) for segment in slices]
    total = sum(counts)
    occupied = sum(count > 0 for count in counts)
    avg = mean(counts) if counts else 0.0
    cv = (pstdev(counts) / avg) if avg else 0.0
    return {
        "term": term.lower(),
        "total": total,
        "segments": segments,
        "occupied_segments": occupied,
        "range": occupied / segments if segments else 0.0,
        "coefficient_of_variation": cv,
    }


def log_likelihood_keyness(
    target_tokens: Sequence[str],
    reference_tokens: Sequence[str],
    min_total: int = 3,
) -> list[dict[str, float | int | str]]:
    """Compare corpora with a full 2x2 Dunning-style log-likelihood (G²).

    The contingency table contains both the selected term and all non-term
    tokens in each corpus. Positive signed_g2 indicates relative overuse in
    the target corpus; negative values indicate relative underuse.

    The statistic is descriptive evidence for comparison, not an
    interpretation of literary significance.
    """
    target = Counter(token.lower() for token in target_tokens)
    reference = Counter(token.lower() for token in reference_tokens)
    n1, n2 = sum(target.values()), sum(reference.values())
    if not n1 or not n2:
        return []

    def component(observed: int, expected: float) -> float:
        return observed * log(observed / expected) if observed and expected else 0.0

    rows = []
    grand_total = n1 + n2
    for term in target.keys() | reference.keys():
        o1, o2 = target[term], reference[term]
        if o1 + o2 < min_total:
            continue

        term_total = o1 + o2
        nonterm1 = n1 - o1
        nonterm2 = n2 - o2
        nonterm_total = nonterm1 + nonterm2

        e_term1 = n1 * term_total / grand_total
        e_term2 = n2 * term_total / grand_total
        e_nonterm1 = n1 * nonterm_total / grand_total
        e_nonterm2 = n2 * nonterm_total / grand_total

        g2 = 2 * (
            component(o1, e_term1)
            + component(o2, e_term2)
            + component(nonterm1, e_nonterm1)
            + component(nonterm2, e_nonterm2)
        )

        rate1 = o1 / n1
        rate2 = o2 / n2
        signed = g2 if rate1 >= rate2 else -g2
        log_ratio = log((rate1 + 0.5 / n1) / (rate2 + 0.5 / n2), 2)

        rows.append({
            "term": term,
            "target_count": o1,
            "reference_count": o2,
            "target_per_10k": rate1 * 10000,
            "reference_per_10k": rate2 * 10000,
            "g2": g2,
            "signed_g2": signed,
            "log_ratio": log_ratio,
        })

    return sorted(rows, key=lambda row: abs(row["signed_g2"]), reverse=True)

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Iterable, Sequence

from .statistics import log_likelihood_keyness

@dataclass(frozen=True)
class CorpusText:
    title: str
    author: str
    publication_year: int | None
    corpus_role: str
    tokens: tuple[str, ...]

def pool_tokens(texts: Iterable[CorpusText]) -> list[str]:
    pooled: list[str] = []
    for text in texts:
        pooled.extend(text.tokens)
    return pooled

def term_rate_matrix(
    texts: Sequence[CorpusText],
    terms: Iterable[str],
    normalize_per: int = 10000,
) -> list[dict[str, float | int | str]]:
    """Return one auditable row per corpus text and research term."""
    rows = []
    terms = [term.casefold() for term in terms]
    for text in texts:
        counts = Counter(token.casefold() for token in text.tokens)
        total = len(text.tokens)
        for term in terms:
            count = counts[term]
            rate = count * normalize_per / total if total else 0.0
            rows.append({
                "title": text.title,
                "author": text.author,
                "publication_year": text.publication_year or "",
                "corpus_role": text.corpus_role,
                "term": term,
                "count": count,
                "tokens": total,
                f"per_{normalize_per}": rate,
            })
    return rows

def target_vs_pooled_reference(
    target: CorpusText,
    references: Sequence[CorpusText],
    min_total: int = 3,
) -> list[dict[str, float | int | str]]:
    """Compare one target text with a pooled, explicitly declared reference corpus."""
    pooled = pool_tokens(references)
    rows = log_likelihood_keyness(target.tokens, pooled, min_total=min_total)
    for row in rows:
        row["target_title"] = target.title
        row["reference_titles"] = "; ".join(text.title for text in references)
        row["reference_texts"] = len(references)
        row["reference_tokens_total"] = len(pooled)
    return rows

def research_term_comparison(
    target: CorpusText,
    references: Sequence[CorpusText],
    terms: Iterable[str],
    normalize_per: int = 10000,
) -> list[dict[str, float | int | str]]:
    """Compare declared research terms without filtering to statistical extremes."""
    all_texts = [target, *references]
    matrix = term_rate_matrix(all_texts, terms, normalize_per=normalize_per)
    by_title_term = {(row["title"], row["term"]): row for row in matrix}
    rows = []
    for term in [term.casefold() for term in terms]:
        target_row = by_title_term[(target.title, term)]
        ref_counts = []
        ref_rates = []
        for ref in references:
            row = by_title_term[(ref.title, term)]
            ref_counts.append(int(row["count"]))
            ref_rates.append(float(row[f"per_{normalize_per}"]))
        rows.append({
            "term": term,
            "target_title": target.title,
            "target_count": int(target_row["count"]),
            f"target_per_{normalize_per}": float(target_row[f"per_{normalize_per}"]),
            "reference_texts": len(references),
            "reference_total_count": sum(ref_counts),
            f"reference_mean_per_{normalize_per}": sum(ref_rates) / len(ref_rates) if ref_rates else 0.0,
            "reference_titles": "; ".join(ref.title for ref in references),
        })
    return rows

def leave_one_out_reference_rates(
    texts: Sequence[CorpusText],
    terms: Iterable[str],
    normalize_per: int = 10000,
) -> list[dict[str, float | int | str]]:
    """Show each text against the pooled remainder to expose comparator sensitivity."""
    terms = [term.casefold() for term in terms]
    rows = []
    for target in texts:
        refs = [text for text in texts if text.title != target.title]
        pooled = pool_tokens(refs)
        target_counts = Counter(target.tokens)
        ref_counts = Counter(pooled)
        for term in terms:
            target_rate = target_counts[term] * normalize_per / len(target.tokens) if target.tokens else 0.0
            ref_rate = ref_counts[term] * normalize_per / len(pooled) if pooled else 0.0
            rows.append({
                "target_title": target.title,
                "term": term,
                "target_count": target_counts[term],
                f"target_per_{normalize_per}": target_rate,
                "pooled_reference_count": ref_counts[term],
                f"pooled_reference_per_{normalize_per}": ref_rate,
                "reference_titles": "; ".join(ref.title for ref in refs),
            })
    return rows

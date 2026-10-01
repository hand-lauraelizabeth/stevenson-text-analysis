from __future__ import annotations

from collections import Counter
from typing import Iterable, Sequence

from .corpus import tokenize

def ngrams(tokens: Sequence[str], n: int = 2) -> list[tuple[str, ...]]:
    if n < 1:
        raise ValueError("n must be >= 1")
    return [tuple(tokens[i:i+n]) for i in range(len(tokens)-n+1)]

def frequent_ngrams(tokens: Sequence[str], n: int = 2, min_count: int = 2,
                    stopwords: set[str] | None = None) -> list[dict[str, int | str]]:
    stopwords = stopwords or set()
    counts = Counter()
    for gram in ngrams([t.lower() for t in tokens], n):
        if all(token in stopwords for token in gram):
            continue
        counts[gram] += 1
    rows = [
        {"ngram": " ".join(gram), "n": n, "count": count}
        for gram, count in counts.items() if count >= min_count
    ]
    return sorted(rows, key=lambda row: (-row["count"], row["ngram"]))

def phrase_occurrences(text: str, phrase: str, window: int = 10):
    """Return token-aware phrase matches with surrounding context."""
    original = tokenize(text, lowercase=False)
    lowered = [token.lower() for token in original]
    needle = [token.lower() for token in tokenize(phrase)]
    if not needle:
        return []
    hits = []
    width = len(needle)
    for start in range(len(lowered)-width+1):
        if lowered[start:start+width] != needle:
            continue
        end = start + width
        hits.append({
            "start_position": start,
            "end_position": end - 1,
            "left": " ".join(original[max(0,start-window):start]),
            "phrase": " ".join(original[start:end]),
            "right": " ".join(original[end:end+window]),
        })
    return hits

def phrase_counts(text: str, phrases: Iterable[str]) -> dict[str, int]:
    return {phrase: len(phrase_occurrences(text, phrase, window=0)) for phrase in phrases}

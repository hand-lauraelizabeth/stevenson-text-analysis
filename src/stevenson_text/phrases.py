from __future__ import annotations

from collections import Counter
from typing import Iterable, Iterator, Sequence

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


def _iter_skipgram_positions(length: int, n: int, max_skip: int) -> Iterator[tuple[int, ...]]:
    """Yield only position tuples that can satisfy the bounded-gap rule.

    The earlier implementation enumerated every n-combination in the corpus and
    discarded almost all of them. For bigrams that is O(N squared), which made
    the full Victorian comparison corpus unsuitable for CI. This iterator
    explores only local successors within max_skip + 1 positions of the
    previous token.
    """
    if n < 2:
        raise ValueError("skipgrams require n >= 2")
    if max_skip < 0:
        raise ValueError("max_skip must be >= 0")
    if length < n:
        return

    max_step = max_skip + 1

    def extend(path: tuple[int, ...]) -> Iterator[tuple[int, ...]]:
        if len(path) == n:
            yield path
            return
        last = path[-1]
        stop = min(length, last + max_step + 1)
        for nxt in range(last + 1, stop):
            yield from extend((*path, nxt))

    for start in range(length):
        yield from extend((start,))


def skipgrams(tokens: Sequence[str], n: int = 2, max_skip: int = 2) -> list[tuple[str, ...]]:
    """Generate ordered n-grams allowing bounded intervening tokens.

    For bigrams, max_skip=2 allows positions separated by up to two intervening
    tokens. Runtime scales with the local window rather than every possible
    token combination in the document.
    """
    lowered = [token.lower() for token in tokens]
    return [
        tuple(lowered[pos] for pos in positions)
        for positions in _iter_skipgram_positions(len(lowered), n=n, max_skip=max_skip)
    ]


def frequent_skipgrams(
    tokens: Sequence[str],
    n: int = 2,
    max_skip: int = 2,
    min_count: int = 2,
    stopwords: set[str] | None = None,
) -> list[dict[str, int | str]]:
    stopwords = stopwords or set()
    lowered = [token.lower() for token in tokens]
    counts = Counter()
    for positions in _iter_skipgram_positions(len(lowered), n=n, max_skip=max_skip):
        gram = tuple(lowered[pos] for pos in positions)
        if all(token in stopwords for token in gram):
            continue
        counts[gram] += 1
    rows = [
        {"skipgram": " … ".join(gram), "n": n, "max_skip": max_skip, "count": count}
        for gram, count in counts.items()
        if count >= min_count
    ]
    return sorted(rows, key=lambda row: (-row["count"], row["skipgram"]))


def phrase_occurrences(text: str, phrase: str, window: int = 10):
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

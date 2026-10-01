from __future__ import annotations

from collections import Counter
from math import log2
from typing import Iterable, Sequence

from .corpus import segment_tokens, tokenize

DEFAULT_STOPWORDS = {
    "a","all","an","and","as","at","be","but","by","for","from","had","have","he","his","i",
    "in","is","it","me","my","not","of","on","or","so","that","the","they","this","to","was",
    "we","were","which","with","you"
}

def moving_average_type_token_ratio(
    tokens: Sequence[str], window: int = 1000
) -> float:
    """Return moving-average type-token ratio (MATTR).

    MATTR reduces the strong text-length dependence of ordinary type-token
    ratio by averaging lexical diversity across fixed-size sliding windows.
    For texts shorter than the requested window, the whole-text TTR is used.
    """
    if window < 1:
        raise ValueError("window must be >= 1")

    corpus = [token.lower() for token in tokens]
    total = len(corpus)
    if not total:
        return 0.0
    if total <= window:
        return len(set(corpus)) / total

    counts = Counter(corpus[:window])
    diversity_sum = len(counts) / window
    windows = 1

    for index in range(window, total):
        outgoing = corpus[index - window]
        counts[outgoing] -= 1
        if counts[outgoing] == 0:
            del counts[outgoing]

        incoming = corpus[index]
        counts[incoming] += 1
        diversity_sum += len(counts) / window
        windows += 1

    return diversity_sum / windows


def lexical_summary(tokens: Sequence[str]) -> dict[str, float | int]:
    total = len(tokens)
    unique = len(set(tokens))
    return {
        "tokens": total,
        "types": unique,
        "type_token_ratio": unique / total if total else 0.0,
        "mattr_1000": moving_average_type_token_ratio(tokens, window=1000),
        "mean_token_length": sum(map(len, tokens)) / total if total else 0.0,
    }

def count_terms(tokens: Sequence[str], terms: Iterable[str]) -> dict[str, int]:
    counts = Counter(tokens)
    return {term.lower(): counts[term.lower()] for term in terms}

def segment_term_counts(tokens: Sequence[str], terms: Iterable[str], segments: int = 10,
                        normalize_per: int | None = 1000) -> list[dict[str, float | int]]:
    term_list = [term.lower() for term in terms]
    rows = []
    for number, segment in enumerate(segment_tokens(tokens, segments), start=1):
        counts = Counter(segment)
        row: dict[str, float | int] = {"segment": number, "segment_tokens": len(segment)}
        for term in term_list:
            value: float | int = counts[term]
            if normalize_per and segment:
                value = counts[term] * normalize_per / len(segment)
            row[term] = value
        rows.append(row)
    return rows

def concordance(text: str, term: str, window: int = 8, max_hits: int | None = 50):
    original = tokenize(text, lowercase=False)
    lowered = [token.lower() for token in original]
    needle = term.lower()
    hits = []
    for index, token in enumerate(lowered):
        if token != needle:
            continue
        hits.append({
            "position": index,
            "left": " ".join(original[max(0, index-window):index]),
            "term": original[index],
            "right": " ".join(original[index+1:index+1+window]),
        })
        if max_hits is not None and len(hits) >= max_hits:
            break
    return hits

def significant_collocates(tokens: Sequence[str], target: str, window: int = 5,
                            min_count: int = 2, stopwords: set[str] | None = None):
    stopwords = DEFAULT_STOPWORDS if stopwords is None else stopwords
    corpus = [token.lower() for token in tokens]
    total = len(corpus)
    target = target.lower()
    target_count = corpus.count(target)
    if not total or not target_count:
        return []
    vocab_counts = Counter(corpus)
    nearby = Counter()
    opportunities = 0
    for index, token in enumerate(corpus):
        if token != target:
            continue
        left, right = max(0, index-window), min(total, index+window+1)
        context = corpus[left:index] + corpus[index+1:right]
        opportunities += len(context)
        nearby.update(w for w in context if w != target and w not in stopwords and len(w) > 1)
    rows = []
    for word, co_count in nearby.items():
        if co_count < min_count:
            continue
        p_word = vocab_counts[word] / total
        p_given = co_count / opportunities if opportunities else 0
        pmi = log2(p_given / p_word) if p_word and p_given else 0.0
        rows.append({
            "term": word,
            "cooccurrences": co_count,
            "corpus_count": vocab_counts[word],
            "pmi": pmi,
        })
    return sorted(rows, key=lambda row: (row["pmi"], row["cooccurrences"]), reverse=True)

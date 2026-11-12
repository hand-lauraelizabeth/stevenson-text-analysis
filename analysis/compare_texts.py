"""Reproducible exploratory comparison of two public-domain Stevenson texts."""
from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
import re

import pandas as pd

try:
    from .cache_sources import load_source_text
    from .tokenization import tokenize
except ImportError:  # supports: python analysis/compare_texts.py
    from cache_sources import load_source_text
    from tokenization import tokenize

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "data" / "source_manifest.csv"
DEFAULT_CACHE = ROOT / "data" / "gutenberg-cache"
STOPWORDS = {"the", "and", "of", "to", "a", "in", "that", "was", "he", "it", "his", "i", "with", "as", "had", "for", "on", "you", "not", "but", "at", "is", "my", "be", "this", "by", "which", "from", "or", "we", "an", "me", "so", "all", "were", "have", "they"}
KEYWORDS = ["body", "face", "hand", "voice", "name", "man", "woman"]

START = re.compile(r"\*\*\* START OF THE PROJECT GUTENBERG EBOOK[^\n]*\*\*\*", re.I)
END = re.compile(r"\*\*\* END OF THE PROJECT GUTENBERG EBOOK[^\n]*\*\*\*", re.I)


def strip_gutenberg_wrapper(text: str) -> str:
    start = START.search(text)
    end = END.search(text)
    if not start or not end or end.start() <= start.end():
        raise ValueError("Missing or invalid Project Gutenberg text delimiters.")
    return text[start.end():end.start()].strip()


def analyze(manifest_path: Path = MANIFEST_PATH, cache_dir: Path = DEFAULT_CACHE, *, offline: bool = False):
    sources = pd.read_csv(manifest_path)
    required = {"title", "ebook_id", "source_url", "rights_note"}
    missing = required.difference(sources.columns)
    if missing:
        raise ValueError(f"Source manifest missing columns: {sorted(missing)}")
    if sources.empty:
        raise ValueError("Corpus manifest contains no sources.")

    rows = []
    keyword_rows = []
    for source in sources.to_dict("records"):
        raw = load_source_text(source["ebook_id"], source["source_url"], cache_dir, offline=offline)
        body = strip_gutenberg_wrapper(raw)
        tokens = tokenize(body)
        if not tokens:
            raise ValueError(f"No readable tokens in {source['title']}.")
        counts = Counter(tokens)
        rows.append({
            "title": source["title"],
            "ebook_id": source["ebook_id"],
            "word_count": len(tokens),
            "unique_tokens": len(counts),
            "type_token_ratio": len(counts) / len(tokens),
            "avg_token_length": sum(map(len, tokens)) / len(tokens),
            "top_terms": Counter(t for t in tokens if t not in STOPWORDS).most_common(12),
        })
        keyword_rows.append({"title": source["title"], **{term: counts[term] for term in KEYWORDS}})
    return pd.DataFrame(rows), pd.DataFrame(keyword_rows)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=MANIFEST_PATH)
    parser.add_argument("--cache-dir", type=Path, default=DEFAULT_CACHE)
    parser.add_argument("--offline", action="store_true", help="Never download; require valid cached checksums")
    args = parser.parse_args(argv)

    sources, keywords = analyze(args.manifest, args.cache_dir, offline=args.offline)
    print("STEVENSON TEXT ANALYSIS")
    print("=" * 28)
    print(sources[["title", "ebook_id", "word_count", "unique_tokens", "type_token_ratio", "avg_token_length"]].to_string(index=False, formatters={"type_token_ratio": "{:.3f}".format, "avg_token_length": "{:.2f}".format}))
    print("\nSelected embodiment and identity terms")
    print(keywords.to_string(index=False))
    print("\nTop content terms")
    print(sources[["title", "top_terms"]].to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

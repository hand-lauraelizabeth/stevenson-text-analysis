from collections import Counter
from pathlib import Path
import re

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "data" / "source_manifest.csv"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; Laura-Hand-DH-Portfolio/1.0)"}
STOPWORDS = {"the", "and", "of", "to", "a", "in", "that", "was", "he", "it", "his", "i", "with", "as", "had", "for", "on", "you", "not", "but", "at", "is", "my", "be", "this", "by", "which", "from", "or", "we", "an", "me", "so", "all", "were", "have", "they"}
KEYWORDS = ["body", "face", "hand", "voice", "name", "man", "woman"]

sources = pd.read_csv(MANIFEST_PATH)
required = {"title", "ebook_id", "source_url", "rights_note"}
missing = required.difference(sources.columns)
assert not missing, f"Missing required columns: {sorted(missing)}"
sources["raw_text"] = sources["source_url"].map(lambda url: requests.get(url, timeout=30, headers=HEADERS).text)
assert sources["raw_text"].str.len().gt(1000).all(), "One or more source downloads were unexpectedly short."
sources["body_text"] = sources["raw_text"].map(lambda text: text.split("*** START OF THE PROJECT GUTENBERG EBOOK", 1)[-1].split("*** END OF THE PROJECT GUTENBERG EBOOK", 1)[0])
sources["tokens"] = sources["body_text"].str.lower().map(lambda text: re.findall(r"[a-z]+(?:'[a-z]+)?", text))
sources["word_count"] = sources["tokens"].map(len)
sources["unique_tokens"] = sources["tokens"].map(lambda tokens: len(set(tokens)))
sources["type_token_ratio"] = sources["unique_tokens"] / sources["word_count"]
sources["avg_token_length"] = sources["tokens"].map(lambda tokens: sum(map(len, tokens)) / len(tokens))
sources["top_terms"] = sources["tokens"].map(lambda tokens: Counter(token for token in tokens if token not in STOPWORDS).most_common(12))
keyword_counts = pd.DataFrame({term: sources["tokens"].map(lambda tokens, term=term: tokens.count(term)) for term in KEYWORDS})
keyword_counts.insert(0, "title", sources["title"])

print("STEVENSON TEXT ANALYSIS")
print("=" * 28)
print(sources[["title", "ebook_id", "word_count", "unique_tokens", "type_token_ratio", "avg_token_length"]].to_string(index=False, formatters={"type_token_ratio": "{:.3f}".format, "avg_token_length": "{:.2f}".format}))
print("\nSelected embodiment and identity terms")
print(keyword_counts.to_string(index=False))
print("\nTop content terms")
print(sources[["title", "top_terms"]].to_string(index=False))

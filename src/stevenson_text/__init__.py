"""Computational text-analysis utilities for the Stevenson research corpus."""
from .analysis import concordance, count_terms, lexical_summary, segment_term_counts, significant_collocates
from .corpus import TextDocument, fetch_document, normalize_text, tokenize

__all__ = [
    "TextDocument","concordance","count_terms","fetch_document","lexical_summary",
    "normalize_text","segment_term_counts","significant_collocates","tokenize"
]

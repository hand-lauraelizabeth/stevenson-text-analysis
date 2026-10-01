"""Computational text-analysis utilities for the Stevenson research corpus."""

from .analysis import concordance, count_terms, lexical_summary, segment_term_counts, significant_collocates
from .corpus import TextDocument, fetch_document, normalize_text, tokenize
from .statistics import dispersion_profile, log_likelihood_keyness
from .structure import TextSection, count_alias_groups, section_entity_matrix, split_by_headings

__all__ = [
    "TextDocument",
    "TextSection",
    "concordance",
    "count_alias_groups",
    "count_terms",
    "dispersion_profile",
    "fetch_document",
    "lexical_summary",
    "log_likelihood_keyness",
    "normalize_text",
    "section_entity_matrix",
    "segment_term_counts",
    "significant_collocates",
    "split_by_headings",
    "tokenize",
]

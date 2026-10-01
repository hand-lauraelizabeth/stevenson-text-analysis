"""Computational text-analysis utilities for the Stevenson research corpus."""

from .analysis import concordance, count_terms, lexical_summary, segment_term_counts, significant_collocates
from .corpus import TextDocument, fetch_document, normalize_text, tokenize
from .networks import cooccurrence_network
from .phrases import frequent_ngrams, ngrams, phrase_counts, phrase_occurrences
from .statistics import dispersion_profile, log_likelihood_keyness
from .structure import TextSection, count_alias_groups, section_entity_matrix, split_by_headings
from .tei import (
    TEICorrespondence,
    TEISection,
    correspondence_edges,
    entity_frequencies,
    extract_correspondence,
    extract_named_entities,
    extract_tei_sections,
    parse_tei,
    tei_title,
)

__all__ = [
    "TEICorrespondence",
    "TEISection",
    "TextDocument",
    "TextSection",
    "concordance",
    "cooccurrence_network",
    "correspondence_edges",
    "count_alias_groups",
    "count_terms",
    "dispersion_profile",
    "entity_frequencies",
    "extract_correspondence",
    "extract_named_entities",
    "extract_tei_sections",
    "fetch_document",
    "frequent_ngrams",
    "lexical_summary",
    "log_likelihood_keyness",
    "ngrams",
    "normalize_text",
    "parse_tei",
    "phrase_counts",
    "phrase_occurrences",
    "section_entity_matrix",
    "segment_term_counts",
    "significant_collocates",
    "split_by_headings",
    "tei_title",
    "tokenize",
]

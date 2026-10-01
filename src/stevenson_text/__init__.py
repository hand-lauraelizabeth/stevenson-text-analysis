"""Computational text-analysis utilities for the Stevenson research corpus."""

from .analysis import concordance, count_terms, lexical_summary, segment_term_counts, significant_collocates
from .corpus import TextDocument, fetch_document, normalize_text, tokenize
from .networks import cooccurrence_network
from .phrases import frequent_ngrams, frequent_skipgrams, ngrams, phrase_counts, phrase_occurrences, skipgrams
from .statistics import dispersion_profile, log_likelihood_keyness
from .structure import TextSection, count_alias_groups, section_entity_matrix, split_by_headings
from .tei import (
    TEICorrespondence,
    TEIDocumentObject,
    TEIRelation,
    TEISection,
    correspondence_edges,
    document_circulation_edges,
    entity_frequencies,
    extract_correspondence,
    extract_document_objects,
    extract_named_entities,
    extract_relations,
    extract_tei_sections,
    parse_tei,
    query_elements,
    relation_edges,
    sections_containing_ref,
    tei_title,
)

__all__ = [
    "TEICorrespondence",
    "TEIDocumentObject",
    "TEIRelation",
    "TEISection",
    "TextDocument",
    "TextSection",
    "concordance",
    "cooccurrence_network",
    "correspondence_edges",
    "count_alias_groups",
    "count_terms",
    "dispersion_profile",
    "document_circulation_edges",
    "entity_frequencies",
    "extract_correspondence",
    "extract_document_objects",
    "extract_named_entities",
    "extract_relations",
    "extract_tei_sections",
    "fetch_document",
    "frequent_ngrams",
    "frequent_skipgrams",
    "lexical_summary",
    "log_likelihood_keyness",
    "ngrams",
    "normalize_text",
    "parse_tei",
    "phrase_counts",
    "phrase_occurrences",
    "query_elements",
    "relation_edges",
    "section_entity_matrix",
    "sections_containing_ref",
    "segment_term_counts",
    "significant_collocates",
    "skipgrams",
    "split_by_headings",
    "tei_title",
    "tokenize",
]

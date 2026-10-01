from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from .analysis import DEFAULT_STOPWORDS, concordance, count_terms, lexical_summary, segment_term_counts, significant_collocates
from .corpus import fetch_document
from .networks import cooccurrence_network
from .phrases import frequent_ngrams, phrase_counts
from .statistics import dispersion_profile, log_likelihood_keyness
from .structure import section_entity_matrix, split_by_headings
from .tei import correspondence_edges, entity_frequencies, extract_correspondence, extract_tei_sections, parse_tei, tei_title

def _load_json(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))

def main() -> None:
    parser = argparse.ArgumentParser(description="Run reproducible Stevenson corpus analysis.")
    parser.add_argument("--manifest", default="data/source_manifest.csv")
    parser.add_argument("--terms", default="data/research_terms.json")
    parser.add_argument("--aliases", default="data/character_aliases.json")
    parser.add_argument("--structure", default="data/structure_rules.json")
    parser.add_argument("--tei", default="data/tei/jekyll_research_sample.xml")
    parser.add_argument("--segments", type=int, default=10)
    parser.add_argument("--output", default="outputs")
    args = parser.parse_args()

    manifest = pd.read_csv(args.manifest)
    research = _load_json(args.terms)
    aliases = _load_json(args.aliases)
    structure_rules = _load_json(args.structure)
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)

    all_terms = sorted({
        term.lower()
        for group in research["term_sets"].values()
        for term in group["terms"]
        if " " not in term
    })
    phrases = sorted({
        term
        for group in research["term_sets"].values()
        for term in group["terms"]
        if " " in term
    })

    summaries = []
    term_counts = []
    phrase_count_rows = []
    documents = []

    for row in manifest.to_dict("records"):
        doc = fetch_document(row["title"], row["source_url"])
        documents.append(doc)
        tokens = doc.tokens
        stem = str(row["ebook_id"])

        summaries.append({"title": doc.title, **lexical_summary(tokens)})
        term_counts.append({"title": doc.title, **count_terms(tokens, all_terms)})
        if phrases:
            phrase_count_rows.append({"title": doc.title, **phrase_counts(doc.text, phrases)})

        pd.DataFrame(segment_term_counts(tokens, all_terms, segments=args.segments)).to_csv(
            output / f"{stem}_term_trajectories.csv", index=False
        )
        pd.DataFrame(
            dispersion_profile(tokens, term, segments=args.segments)
            for term in all_terms
        ).to_csv(output / f"{stem}_dispersion.csv", index=False)
        pd.DataFrame(
            frequent_ngrams(tokens, n=2, min_count=2, stopwords=DEFAULT_STOPWORDS)
        ).to_csv(output / f"{stem}_bigrams.csv", index=False)
        pd.DataFrame(
            frequent_ngrams(tokens, n=3, min_count=2, stopwords=DEFAULT_STOPWORDS)
        ).to_csv(output / f"{stem}_trigrams.csv", index=False)

        for anchor in research["anchor_terms"]:
            pd.DataFrame(concordance(doc.text, anchor, window=10, max_hits=100)).to_csv(
                output / f"{stem}_concordance_{anchor}.csv", index=False
            )
            pd.DataFrame(significant_collocates(tokens, anchor, window=5, min_count=2)).to_csv(
                output / f"{stem}_collocates_{anchor}.csv", index=False
            )

        if doc.title in structure_rules:
            sections = split_by_headings(doc.text, structure_rules[doc.title]["headings"])
            pd.DataFrame({
                "section": section.index,
                "heading": section.heading,
                "tokens": len(section.tokens),
            } for section in sections).to_csv(
                output / f"{stem}_sections.csv", index=False
            )

            if doc.title in aliases:
                pd.DataFrame(section_entity_matrix(sections, aliases[doc.title])).to_csv(
                    output / f"{stem}_character_by_section.csv", index=False
                )
                nodes, edges = cooccurrence_network(sections, aliases[doc.title])
                pd.DataFrame(nodes).to_csv(output / f"{stem}_network_nodes.csv", index=False)
                pd.DataFrame(edges).to_csv(output / f"{stem}_network_edges.csv", index=False)

    pd.DataFrame(summaries).to_csv(output / "lexical_summary.csv", index=False)
    pd.DataFrame(term_counts).to_csv(output / "research_term_counts.csv", index=False)
    if phrase_count_rows:
        pd.DataFrame(phrase_count_rows).to_csv(output / "research_phrase_counts.csv", index=False)

    if len(documents) >= 2:
        target, reference = documents[0], documents[1]
        pd.DataFrame(log_likelihood_keyness(target.tokens, reference.tokens)).to_csv(
            output / "keyness_target_vs_reference.csv", index=False
        )

    tei_path = Path(args.tei)
    if tei_path.exists():
        root = parse_tei(tei_path.read_text(encoding="utf-8"))
        sections = extract_tei_sections(root)
        pd.DataFrame({
            "xml_id": section.xml_id or "",
            "type": section.section_type or "",
            "heading": section.heading,
            "text": section.text,
        } for section in sections).to_csv(output / "tei_sections.csv", index=False)
        pd.DataFrame(entity_frequencies(root)).to_csv(output / "tei_entities.csv", index=False)
        correspondence = extract_correspondence(root)
        pd.DataFrame({
            "xml_id": record.xml_id or "",
            "senders": "; ".join(record.senders),
            "recipients": "; ".join(record.recipients),
            "date": record.date or "",
        } for record in correspondence).to_csv(output / "tei_correspondence.csv", index=False)
        pd.DataFrame(correspondence_edges(correspondence)).to_csv(
            output / "tei_correspondence_edges.csv", index=False
        )
        print(f"Parsed TEI sample: {tei_title(root)}")

    print(pd.DataFrame(summaries).to_string(index=False))
    print(f"\nWrote reproducible research outputs to {output.resolve()}")

if __name__ == "__main__":
    main()

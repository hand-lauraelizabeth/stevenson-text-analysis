from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from .agreement import agreement_summary, compare_annotation_sets
from .analysis import DEFAULT_STOPWORDS, concordance, count_terms, lexical_summary, segment_term_counts, significant_collocates
from .annotations import annotation_summary, load_annotations_csv, resolve_annotation_anchors, validate_annotations
from .comparison import (
    CorpusText,
    leave_one_out_reference_rates,
    research_term_comparison,
    target_vs_pooled_reference,
    term_rate_matrix,
)
from .corpus import fetch_document
from .evidence import evidence_bundle_rows, evidence_graph, evidence_summary, load_evidence_links_csv, validate_evidence_links
from .morphology import lemma_concordance, lemma_counts, validate_lemma_groups
from .networks import cooccurrence_network
from .phrases import frequent_ngrams, frequent_skipgrams, phrase_counts
from .scenes import load_scenes_csv, resolve_scene_windows, scene_entity_matrix, scene_term_matrix, validate_scenes
from .statistics import dispersion_profile, log_likelihood_keyness
from .structure import section_entity_matrix, split_by_headings
from .tei import (
    correspondence_edges,
    document_circulation_edges,
    entity_frequencies,
    extract_correspondence,
    extract_document_objects,
    extract_relations,
    extract_tei_sections,
    parse_tei,
    sections_containing_ref,
    tei_title,
)

def _load_json(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _select_target_record(records: list[CorpusText]) -> CorpusText:
    """Return the single manifest record explicitly declared as the target."""
    targets = [record for record in records if record.corpus_role == "target"]
    if len(targets) != 1:
        raise ValueError(
            "Source manifest must contain exactly one row with corpus_role='target'; "
            f"found {len(targets)}."
        )
    return targets[0]


def main() -> None:
    parser = argparse.ArgumentParser(description="Run reproducible Stevenson corpus analysis.")
    parser.add_argument("--manifest", default="data/source_manifest.csv")
    parser.add_argument("--comparison-manifest", default="data/victorian_comparison_manifest.csv")
    parser.add_argument("--terms", default="data/research_terms.json")
    parser.add_argument("--aliases", default="data/character_aliases.json")
    parser.add_argument("--structure", default="data/structure_rules.json")
    parser.add_argument("--lemma-groups", default="data/lemma_groups.json")
    parser.add_argument("--tei", default="data/tei/jekyll_research_sample.xml")
    parser.add_argument("--annotations", default="data/annotations/hand_motif_annotations.csv")
    parser.add_argument("--second-annotations", default=None)
    parser.add_argument("--scenes", default="data/scenes/hand_research_scenes.csv")
    parser.add_argument("--evidence-links", default="data/evidence_links.csv")
    parser.add_argument("--segments", type=int, default=10)
    parser.add_argument("--output", default="outputs")
    args = parser.parse_args()

    manifest = pd.read_csv(args.manifest)
    comparison_manifest = pd.read_csv(args.comparison_manifest) if Path(args.comparison_manifest).exists() else pd.DataFrame()
    research = _load_json(args.terms)
    aliases = _load_json(args.aliases)
    structure_rules = _load_json(args.structure)
    lemma_groups = _load_json(args.lemma_groups)
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)

    pd.DataFrame(validate_lemma_groups(lemma_groups)).to_csv(
        output / "lemma_group_validation_issues.csv", index=False
    )

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
    lemma_count_rows = []
    phrase_count_rows = []
    documents = []
    documents_by_title = {}
    corpus_records = []

    for row in manifest.to_dict("records"):
        doc = fetch_document(row["title"], row["source_url"])
        documents.append(doc)
        documents_by_title[doc.title] = doc
        corpus_records.append(CorpusText(
            title=doc.title,
            author=str(row.get("author", "")),
            publication_year=int(row["publication_year"]) if pd.notna(row.get("publication_year")) else None,
            corpus_role=str(row.get("corpus_role", "")),
            tokens=tuple(doc.tokens),
        ))
        tokens = doc.tokens
        stem = str(row["ebook_id"])

        summaries.append({"title": doc.title, **lexical_summary(tokens)})
        term_counts.append({"title": doc.title, **count_terms(tokens, all_terms)})
        lemma_count_rows.append({"title": doc.title, **lemma_counts(tokens, lemma_groups)})

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
        pd.DataFrame(
            frequent_skipgrams(tokens, n=2, max_skip=2, min_count=2, stopwords=DEFAULT_STOPWORDS)
        ).to_csv(output / f"{stem}_skip_bigrams.csv", index=False)

        for lemma in lemma_groups:
            pd.DataFrame(lemma_concordance(doc.text, lemma, lemma_groups, window=10)).to_csv(
                output / f"{stem}_lemma_concordance_{lemma}.csv", index=False
            )

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
    pd.DataFrame(lemma_count_rows).to_csv(output / "research_lemma_counts.csv", index=False)

    if phrase_count_rows:
        pd.DataFrame(phrase_count_rows).to_csv(output / "research_phrase_counts.csv", index=False)

    target_record = _select_target_record(corpus_records)
    target_document = documents_by_title[target_record.title]
    target_sections = (
        split_by_headings(
            target_document.text,
            structure_rules[target_record.title]["headings"],
        )
        if target_record.title in structure_rules
        else []
    )

    reference_record = next(
        (record for record in corpus_records if record.corpus_role == "same_author_comparator"),
        None,
    )
    if reference_record is None:
        reference_record = next(
            (record for record in corpus_records if record.title != target_record.title),
            None,
        )
    if reference_record is not None:
        reference_document = documents_by_title[reference_record.title]
        pd.DataFrame(
            log_likelihood_keyness(target_document.tokens, reference_document.tokens)
        ).to_csv(output / "keyness_target_vs_reference.csv", index=False)

    if not comparison_manifest.empty and corpus_records:
        comparison_records = []
        for row in comparison_manifest.to_dict("records"):
            doc = fetch_document(row["title"], row["source_url"])
            comparison_records.append(CorpusText(
                title=doc.title,
                author=str(row.get("author", "")),
                publication_year=int(row["publication_year"]) if pd.notna(row.get("publication_year")) else None,
                corpus_role=str(row.get("corpus_role", "")),
                tokens=tuple(doc.tokens),
            ))

        declared_terms = sorted(set(all_terms) | set(lemma_groups.keys()))
        comparison_set = [target_record, *comparison_records]

        pd.DataFrame(
            term_rate_matrix(comparison_set, declared_terms, normalize_per=10000)
        ).to_csv(output / "victorian_term_rate_matrix.csv", index=False)

        pd.DataFrame(
            research_term_comparison(
                target_record,
                comparison_records,
                declared_terms,
                normalize_per=10000,
            )
        ).to_csv(output / "victorian_research_term_comparison.csv", index=False)

        pd.DataFrame(
            target_vs_pooled_reference(target_record, comparison_records, min_total=3)
        ).to_csv(output / "victorian_keyness_target_vs_pooled_reference.csv", index=False)

        pd.DataFrame(
            leave_one_out_reference_rates(comparison_set, declared_terms, normalize_per=10000)
        ).to_csv(output / "victorian_leave_one_out_rates.csv", index=False)

    annotations_path = Path(args.annotations)
    primary_annotations = None
    if annotations_path.exists():
        primary_annotations = load_annotations_csv(annotations_path.read_text(encoding="utf-8"))
        issues = validate_annotations(primary_annotations)
        pd.DataFrame(issues).to_csv(output / "annotation_validation_issues.csv", index=False)
        pd.DataFrame(annotation_summary(primary_annotations)).to_csv(
            output / "annotation_summary.csv", index=False
        )
        pd.DataFrame(
            resolve_annotation_anchors(
                target_document.text,
                primary_annotations,
                window=14,
                sections=target_sections or None,
            )
        ).to_csv(output / "annotation_anchor_resolution.csv", index=False)

    scenes = []
    scenes_path = Path(args.scenes)
    if scenes_path.exists():
        scenes = load_scenes_csv(scenes_path.read_text(encoding="utf-8"))
        pd.DataFrame(validate_scenes(scenes)).to_csv(
            output / "scene_validation_issues.csv", index=False
        )

        target_title = target_record.title
        if target_sections:
            scene_rows = resolve_scene_windows(target_sections, scenes, window=60)
            pd.DataFrame(scene_rows).to_csv(output / "research_scenes.csv", index=False)

            if target_title in aliases:
                pd.DataFrame(
                    scene_entity_matrix(scene_rows, aliases[target_title])
                ).to_csv(output / "scene_character_matrix.csv", index=False)

            pd.DataFrame(
                scene_term_matrix(scene_rows, all_terms)
            ).to_csv(output / "scene_term_matrix.csv", index=False)

    tei_document_ids: list[str] = []
    tei_path = Path(args.tei)
    if tei_path.exists():
        root = parse_tei(tei_path.read_text(encoding="utf-8"))
        document_objects = extract_document_objects(root)
        tei_document_ids = [document.xml_id or "" for document in document_objects]

    evidence_path = Path(args.evidence_links)
    if evidence_path.exists() and scenes and primary_annotations is not None:
        links = load_evidence_links_csv(evidence_path.read_text(encoding="utf-8"))
        issues = validate_evidence_links(
            links,
            scenes,
            primary_annotations,
            known_documents=tei_document_ids,
        )
        pd.DataFrame(issues).to_csv(output / "evidence_link_validation_issues.csv", index=False)
        pd.DataFrame(evidence_summary(links)).to_csv(output / "evidence_link_summary.csv", index=False)
        pd.DataFrame(evidence_bundle_rows(links, scenes, primary_annotations)).to_csv(
            output / "evidence_bundles.csv", index=False
        )
        evidence_nodes, evidence_edges = evidence_graph(links, scenes, primary_annotations)
        pd.DataFrame(evidence_nodes).to_csv(output / "evidence_graph_nodes.csv", index=False)
        pd.DataFrame(evidence_edges).to_csv(output / "evidence_graph_edges.csv", index=False)

    if args.second_annotations and primary_annotations is not None:
        second_path = Path(args.second_annotations)
        if second_path.exists():
            secondary_annotations = load_annotations_csv(second_path.read_text(encoding="utf-8"))
            for field in ("category", "claim_role"):
                rows = compare_annotation_sets(primary_annotations, secondary_annotations, field=field)
                pd.DataFrame(rows).to_csv(output / f"annotation_agreement_{field}.csv", index=False)
                pd.DataFrame([agreement_summary(primary_annotations, secondary_annotations, field=field)]).to_csv(
                    output / f"annotation_agreement_{field}_summary.csv", index=False
                )

    if tei_path.exists():
        sections = extract_tei_sections(root)
        pd.DataFrame({
            "xml_id": section.xml_id or "",
            "type": section.section_type or "",
            "heading": section.heading,
            "text": section.text,
        } for section in sections).to_csv(output / "tei_sections.csv", index=False)

        entity_rows = entity_frequencies(root)
        pd.DataFrame(entity_rows).to_csv(output / "tei_entities.csv", index=False)

        entity_section_rows = []
        for entity in entity_rows:
            identifier = str(entity["identifier"])
            if identifier.startswith("#"):
                entity_section_rows.extend(sections_containing_ref(root, identifier))
        pd.DataFrame(entity_section_rows).to_csv(output / "tei_entity_sections.csv", index=False)

        document_objects = extract_document_objects(root)
        pd.DataFrame({
            "xml_id": document.xml_id or "",
            "document_type": document.document_type,
            "subtype": document.subtype or "",
            "heading": document.heading,
            "text": document.text,
        } for document in document_objects).to_csv(output / "tei_documents.csv", index=False)

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

        relations = extract_relations(root)
        pd.DataFrame({
            "name": relation.name,
            "active": "; ".join(relation.active),
            "passive": "; ".join(relation.passive),
            "document_ref": relation.document_ref or "",
        } for relation in relations).to_csv(output / "tei_relations.csv", index=False)
        pd.DataFrame(document_circulation_edges(relations)).to_csv(
            output / "tei_document_circulation_edges.csv", index=False
        )

        print(f"Parsed TEI sample: {tei_title(root)}")

    print(pd.DataFrame(summaries).to_string(index=False))
    print(f"\nWrote reproducible research outputs to {output.resolve()}")

if __name__ == "__main__":
    main()

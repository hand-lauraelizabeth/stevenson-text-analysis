import csv
import json
from pathlib import Path

from stevenson_text.annotations import load_annotations_csv
from stevenson_text.evidence import load_evidence_links_csv, validate_evidence_links
from stevenson_text.scenes import load_scenes_csv
from stevenson_text.tei import extract_document_objects, parse_tei

ROOT = Path(__file__).resolve().parents[1]


def test_target_manifest_title_has_ten_declared_jekyll_and_hyde_chapters():
    with (ROOT / "data/source_manifest.csv").open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    targets = [row for row in rows if row["corpus_role"] == "target"]
    assert len(targets) == 1

    rules = json.loads((ROOT / "data/structure_rules.json").read_text(encoding="utf-8"))
    target_title = targets[0]["title"]

    assert target_title in rules
    assert len(rules[target_title]["headings"]) == 10
    assert rules[target_title]["headings"][0] == "STORY OF THE DOOR"
    assert rules[target_title]["headings"][-1] == "HENRY JEKYLL'S FULL STATEMENT OF THE CASE"


def test_evidence_links_resolve_against_declared_scenes_annotations_and_tei_documents():
    scenes = load_scenes_csv(
        (ROOT / "data/scenes/hand_research_scenes.csv").read_text(encoding="utf-8")
    )
    annotations = load_annotations_csv(
        (ROOT / "data/annotations/hand_motif_annotations.csv").read_text(encoding="utf-8")
    )
    links = load_evidence_links_csv(
        (ROOT / "data/evidence_links.csv").read_text(encoding="utf-8")
    )
    root = parse_tei(
        (ROOT / "data/tei/jekyll_research_sample.xml").read_text(encoding="utf-8")
    )
    document_ids = [
        document.xml_id
        for document in extract_document_objects(root)
        if document.xml_id
    ]

    assert {"hyde-letter", "packet", "confession"}.issubset(document_ids)
    assert validate_evidence_links(
        links,
        scenes,
        annotations,
        known_documents=document_ids,
    ) == []


def test_web_interface_derives_target_dataset_paths_from_manifest():
    index_html = (ROOT / "web/index.html").read_text(encoding="utf-8")
    app_js = (ROOT / "web/app.js").read_text(encoding="utf-8")

    assert "../outputs/43_" not in index_html
    assert "../outputs/43_" not in app_js
    assert "{target}" in index_html
    assert "source_manifest.csv" in app_js
    assert 'row.corpus_role === "target"' in app_js

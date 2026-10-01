from stevenson_text.analysis import concordance, count_terms, segment_term_counts, significant_collocates
from stevenson_text.annotations import (
    annotation_summary,
    load_annotations_csv,
    resolve_annotation_anchors,
    validate_annotations,
)
from stevenson_text.agreement import agreement_summary, compare_annotation_sets
from stevenson_text.comparison import (
    CorpusText,
    leave_one_out_reference_rates,
    research_term_comparison,
    target_vs_pooled_reference,
    term_rate_matrix,
)
from stevenson_text.corpus import fetch_source_text, segment_tokens, strip_gutenberg_wrapper, tokenize
from stevenson_text.evidence import (
    evidence_bundle_rows,
    evidence_graph,
    load_evidence_links_csv,
    validate_evidence_links,
)
from stevenson_text.morphology import lemma_concordance, lemma_counts, validate_lemma_groups
from stevenson_text.networks import cooccurrence_network
from stevenson_text.phrases import frequent_ngrams, frequent_skipgrams, phrase_occurrences, skipgrams
from stevenson_text.scenes import (
    load_scenes_csv,
    resolve_scene_windows,
    scene_entity_matrix,
    scene_term_matrix,
    validate_scenes,
)
from stevenson_text.statistics import dispersion_profile, log_likelihood_keyness
from stevenson_text.structure import count_alias_groups, split_by_headings
from stevenson_text.tei import (
    correspondence_edges,
    document_circulation_edges,
    entity_frequencies,
    extract_correspondence,
    extract_document_objects,
    extract_relations,
    extract_tei_sections,
    parse_tei,
    query_elements,
    sections_containing_ref,
    tei_title,
)

def test_gutenberg_wrapper_is_removed():
    text = """header
*** START OF THE PROJECT GUTENBERG EBOOK TEST ***
A hand held another hand.
*** END OF THE PROJECT GUTENBERG EBOOK TEST ***
footer"""
    assert strip_gutenberg_wrapper(text) == "A hand held another hand."

def test_segments_preserve_all_tokens():
    tokens = list("abcdefghij")
    chunks = segment_tokens(tokens, 3)
    assert [item for chunk in chunks for item in chunk] == tokens
    assert max(map(len, chunks)) - min(map(len, chunks)) <= 1

def test_term_counts_are_case_normalized_by_tokenizer():
    tokens = tokenize("Man man woman HAND hand.")
    assert count_terms(tokens, ["man", "woman", "hand"]) == {"man": 2, "woman": 1, "hand": 2}

def test_segment_trajectories_return_requested_segments():
    tokens = tokenize("hand hand body voice hand body name voice")
    rows = segment_term_counts(tokens, ["hand", "body"], segments=4, normalize_per=None)
    assert len(rows) == 4
    assert sum(row["hand"] for row in rows) == 3
    assert sum(row["body"] for row in rows) == 2

def test_concordance_keeps_order_and_context():
    hits = concordance("One hand opens the door. Another hand writes.", "hand", window=2)
    assert len(hits) == 2
    assert hits[0]["position"] < hits[1]["position"]

def test_collocates_surface_repeated_context_words():
    tokens = tokenize("strange hand strange hand quiet room strange hand quiet room")
    rows = significant_collocates(tokens, "hand", window=2, min_count=2, stopwords=set())
    assert "strange" in {row["term"] for row in rows}

def test_known_headings_create_named_sections():
    text = """Preface text.
STORY OF THE DOOR
First chapter body.
SEARCH FOR MR. HYDE
Second chapter body."""
    sections = split_by_headings(text, ["STORY OF THE DOOR", "SEARCH FOR MR. HYDE"])
    assert [section.heading for section in sections] == [
        "Front matter", "STORY OF THE DOOR", "SEARCH FOR MR. HYDE"
    ]

def test_alias_groups_do_not_double_count_long_and_short_forms():
    tokens = tokenize("Dr. Jekyll met Jekyll. Henry Jekyll left.")
    counts = count_alias_groups(
        tokens,
        {"Jekyll": ["Dr. Jekyll", "Henry Jekyll", "Jekyll"]},
    )
    assert counts["Jekyll"] == 3

def test_dispersion_distinguishes_concentrated_term():
    tokens = ["hand"] * 4 + ["other"] * 12
    profile = dispersion_profile(tokens, "hand", segments=4)
    assert profile["total"] == 4
    assert profile["occupied_segments"] == 1
    assert profile["range"] == 0.25

def test_keyness_sign_reflects_relative_overuse():
    target = tokenize("hand hand hand body body quiet")
    reference = tokenize("hand body quiet quiet quiet quiet")
    rows = log_likelihood_keyness(target, reference, min_total=2)
    by_term = {row["term"]: row for row in rows}
    assert by_term["hand"]["signed_g2"] > 0
    assert by_term["quiet"]["signed_g2"] < 0

def test_phrase_occurrences_are_token_aware():
    hits = phrase_occurrences(
        "The written hand differs from a hand-written note. The written hand returns.",
        "written hand",
        window=2,
    )
    assert len(hits) == 2
    assert hits[0]["phrase"].lower() == "written hand"

def test_frequent_ngrams_count_repeated_sequences():
    rows = frequent_ngrams(tokenize("strange hand strange hand strange hand"), n=2, min_count=2)
    by_ngram = {row["ngram"]: row["count"] for row in rows}
    assert by_ngram["strange hand"] == 3
    assert by_ngram["hand strange"] == 2

def test_skipgrams_allow_bounded_intervening_tokens():
    tokens = tokenize("hand in the letter hand on letter")
    grams = skipgrams(tokens, n=2, max_skip=2)
    assert ("hand", "letter") in grams
    rows = frequent_skipgrams(tokens, n=2, max_skip=2, min_count=2)
    by_skipgram = {row["skipgram"]: row["count"] for row in rows}
    assert by_skipgram["hand … letter"] == 2

def test_annotation_layer_validates_and_resolves_anchors():
    csv_text = """annotation_id,section,anchor_phrase,category,subcategory,actors,document_ref,claim_role,note
A1,ONE,odd hand,handwriting_identity,script,Guest,,core,Test annotation
"""
    annotations = load_annotations_csv(csv_text)
    assert validate_annotations(annotations) == []
    resolved = resolve_annotation_anchors("The letter was in an odd hand.", annotations, window=2)
    assert resolved[0]["status"] == "resolved"
    assert resolved[0]["matched_text"].lower() == "odd hand"
    summary = annotation_summary(annotations)
    assert summary == [{"category": "handwriting_identity", "claim_role": "core", "annotations": 1}]

def test_annotation_validation_catches_unknown_category():
    csv_text = """annotation_id,section,anchor_phrase,category,subcategory,actors,document_ref,claim_role,note
A1,ONE,odd hand,not_a_category,script,Guest,,core,Test annotation
"""
    issues = validate_annotations(load_annotations_csv(csv_text))
    assert any(issue["field"] == "category" for issue in issues)

def test_network_weights_shared_sections():
    sections = split_by_headings(
        """ONE
Jekyll meets Hyde.
TWO
Jekyll and Hyde meet Utterson.
THREE
Utterson waits.""",
        ["ONE", "TWO", "THREE"],
    )
    aliases = {"Jekyll": ["Jekyll"], "Hyde": ["Hyde"], "Utterson": ["Utterson"]}
    _, edges = cooccurrence_network(sections, aliases)
    edge_map = {(row["source"], row["target"]): row["weight"] for row in edges}
    assert edge_map[("Hyde", "Jekyll")] == 2
    assert edge_map[("Jekyll", "Utterson")] == 1

TEI_SAMPLE = """<TEI xmlns="http://www.tei-c.org/ns/1.0">
<teiHeader>
  <fileDesc><titleStmt><title>Test Edition</title></titleStmt>
  <publicationStmt><p>Test</p></publicationStmt>
  <sourceDesc><p>Test</p></sourceDesc></fileDesc>
  <profileDesc>
    <correspDesc xml:id="c1" xmlns:xml="http://www.w3.org/XML/1998/namespace">
      <correspAction type="sent"><persName ref="#jekyll">Jekyll</persName><date when="1886-01-01"/></correspAction>
      <correspAction type="received"><persName ref="#utterson">Utterson</persName></correspAction>
    </correspDesc>
  </profileDesc>
</teiHeader>
<text><body>
  <div type="chapter" xml:id="ch1" xmlns:xml="http://www.w3.org/XML/1998/namespace">
    <head>Chapter One</head>
    <p><persName ref="#jekyll">Jekyll</persName> meets <persName ref="#utterson">Utterson</persName>.</p>
    <div type="document" subtype="letter" xml:id="letter1">
      <head>Letter</head>
      <p><persName ref="#utterson">Utterson</persName> reads it.</p>
    </div>
  </div>
</body></text>
<standOff>
  <listRelation>
    <relation name="transmits" active="#jekyll" passive="#utterson" corresp="#letter1"/>
    <relation name="scrutinizes" active="#utterson" passive="#jekyll" corresp="#letter1"/>
  </listRelation>
</standOff>
</TEI>"""

def test_tei_extracts_title_sections_and_entities():
    root = parse_tei(TEI_SAMPLE)
    assert tei_title(root) == "Test Edition"
    sections = extract_tei_sections(root)
    assert sections[0].xml_id == "ch1"
    assert sections[0].heading == "Chapter One"
    entities = entity_frequencies(root)
    assert {row["identifier"] for row in entities} == {"#jekyll", "#utterson"}

def test_tei_correspondence_produces_directed_edges():
    root = parse_tei(TEI_SAMPLE)
    records = extract_correspondence(root)
    assert records[0].senders == ("#jekyll",)
    assert records[0].recipients == ("#utterson",)
    assert records[0].date == "1886-01-01"
    assert correspondence_edges(records) == [
        {"source": "#jekyll", "target": "#utterson", "weight": 1}
    ]

def test_tei_structural_query_finds_ref_and_sections():
    root = parse_tei(TEI_SAMPLE)
    mentions = query_elements(root, "persName", ref="#utterson")
    assert len(mentions) == 2
    sections = sections_containing_ref(root, "#utterson")
    assert any(row["xml_id"] == "ch1" for row in sections)

def test_tei_document_objects_and_circulation_relations():
    root = parse_tei(TEI_SAMPLE)
    documents = extract_document_objects(root)
    assert documents[0].xml_id == "letter1"
    assert documents[0].subtype == "letter"
    relations = extract_relations(root)
    circulation = document_circulation_edges(relations)
    assert circulation == [{
        "source": "#jekyll",
        "target": "#utterson",
        "relation": "transmits",
        "weight": 1,
        "documents": "#letter1",
    }]


def test_controlled_lemma_groups_count_declared_forms():
    groups = {
        "write": ["write", "writes", "writing", "written", "wrote"],
        "hand": ["hand", "hands"],
    }
    assert validate_lemma_groups(groups) == []
    tokens = tokenize("He wrote with both hands and was writing again.")
    counts = lemma_counts(tokens, groups)
    assert counts["write"] == 2
    assert counts["hand"] == 1

def test_lemma_concordance_preserves_surface_form():
    groups = {"write": ["write", "writes", "writing", "written", "wrote"]}
    hits = lemma_concordance("He wrote, then began writing.", "write", groups, window=2)
    assert [hit["surface"].lower() for hit in hits] == ["wrote", "writing"]

def test_lemma_validation_catches_overlapping_surface_forms():
    groups = {"hand": ["hand"], "handle": ["hand"]}
    issues = validate_lemma_groups(groups)
    assert any("already assigned" in issue["issue"] for issue in issues)

def test_annotation_agreement_reports_kappa():
    coder_a = load_annotations_csv("""annotation_id,section,anchor_phrase,category,subcategory,actors,document_ref,claim_role,note
A1,ONE,odd hand,handwriting_identity,script,Guest,,core,One
A2,TWO,my own hand,embodied_transformation,body,Jekyll,,supporting,Two
""")
    coder_b = load_annotations_csv("""annotation_id,section,anchor_phrase,category,subcategory,actors,document_ref,claim_role,note
A1,ONE,odd hand,handwriting_identity,script,Guest,,core,One
A2,TWO,my own hand,handwriting_identity,body,Jekyll,,supporting,Two
""")
    rows = compare_annotation_sets(coder_a, coder_b, field="category")
    summary = agreement_summary(coder_a, coder_b, field="category")
    assert len(rows) == 2
    assert summary["observed_agreement"] == 0.5
    assert -1.0 <= summary["cohens_kappa"] <= 1.0


def test_victorian_comparison_preserves_corpus_metadata_and_rates():
    target = CorpusText(
        title="Target", author="A", publication_year=1886,
        corpus_role="target", tokens=("hand", "hand", "letter", "strange")
    )
    reference = CorpusText(
        title="Reference", author="B", publication_year=1890,
        corpus_role="late_victorian_comparator", tokens=("hand", "letter", "letter", "body")
    )
    rows = term_rate_matrix([target, reference], ["hand", "letter"], normalize_per=10000)
    target_hand = next(row for row in rows if row["title"] == "Target" and row["term"] == "hand")
    assert target_hand["author"] == "A"
    assert target_hand["publication_year"] == 1886
    assert target_hand["count"] == 2
    assert target_hand["per_10000"] == 5000.0

def test_target_vs_pooled_reference_records_reference_membership():
    target = CorpusText("Target", "A", 1886, "target", ("hand", "hand", "strange", "letter"))
    r1 = CorpusText("R1", "B", 1890, "reference", ("hand", "body", "body", "letter"))
    r2 = CorpusText("R2", "C", 1897, "reference", ("body", "body", "letter", "letter"))
    rows = target_vs_pooled_reference(target, [r1, r2], min_total=2)
    assert rows
    assert all(row["reference_titles"] == "R1; R2" for row in rows)
    assert all(row["reference_texts"] == 2 for row in rows)

def test_declared_term_comparison_keeps_non_extreme_terms():
    target = CorpusText("Target", "A", 1886, "target", ("hand", "hand", "letter", "strange"))
    r1 = CorpusText("R1", "B", 1890, "reference", ("hand", "letter", "body", "body"))
    rows = research_term_comparison(target, [r1], ["hand", "letter", "voice"])
    by_term = {row["term"]: row for row in rows}
    assert set(by_term) == {"hand", "letter", "voice"}
    assert by_term["voice"]["target_count"] == 0
    assert by_term["voice"]["reference_total_count"] == 0

def test_leave_one_out_rates_change_reference_membership():
    texts = [
        CorpusText("A", "A", 1886, "target", ("hand", "hand", "body")),
        CorpusText("B", "B", 1890, "reference", ("hand", "letter", "letter")),
        CorpusText("C", "C", 1897, "reference", ("body", "body", "letter")),
    ]
    rows = leave_one_out_reference_rates(texts, ["hand"])
    a_row = next(row for row in rows if row["target_title"] == "A")
    assert a_row["reference_titles"] == "B; C"


def test_research_scenes_resolve_within_expected_sections():
    sections = split_by_headings(
        """ONE
Utterson saw an odd hand in the letter.
TWO
The hand that lay on my knee changed before me.""",
        ["ONE", "TWO"],
    )
    scenes = load_scenes_csv("""scene_id,section,title,anchor_phrase,scene_type,rationale
S1,ONE,Odd hand,odd hand,handwriting,Test
S2,TWO,Changed hand,the hand that lay on my knee,transformation,Test
""")
    assert validate_scenes(scenes) == []
    rows = resolve_scene_windows(sections, scenes, window=4)
    by_id = {row["scene_id"]: row for row in rows}
    assert by_id["S1"]["status"] == "resolved"
    assert by_id["S2"]["status"] == "resolved"

def test_scene_resolution_reports_missing_section_and_unresolved_anchor():
    sections = split_by_headings("ONE\nSome text.", ["ONE"])
    scenes = load_scenes_csv("""scene_id,section,title,anchor_phrase,scene_type,rationale
S1,TWO,Missing section,odd hand,handwriting,Test
S2,ONE,Missing anchor,odd hand,handwriting,Test
""")
    rows = resolve_scene_windows(sections, scenes)
    by_id = {row["scene_id"]: row for row in rows}
    assert by_id["S1"]["status"] == "missing_section"
    assert by_id["S2"]["status"] == "unresolved"

def test_scene_matrices_preserve_scene_identity():
    scene_rows = [{
        "scene_id": "S1",
        "section": "ONE",
        "title": "Odd hand",
        "scene_type": "handwriting",
        "status": "resolved",
        "window_text": "Utterson saw Hyde's strange hand and letter.",
    }]
    aliases = {"Utterson": ["Utterson"], "Hyde": ["Hyde"]}
    entity_rows = scene_entity_matrix(scene_rows, aliases)
    term_rows = scene_term_matrix(scene_rows, ["hand", "letter", "voice"])
    assert entity_rows[0]["scene_id"] == "S1"
    assert entity_rows[0]["Utterson"] == 1
    assert entity_rows[0]["Hyde"] == 1
    assert term_rows[0]["hand"] == 1
    assert term_rows[0]["letter"] == 1
    assert term_rows[0]["voice"] == 0


def test_evidence_links_validate_references_and_bundle_layers():
    scenes = load_scenes_csv("""scene_id,section,title,anchor_phrase,scene_type,rationale
S1,ONE,Odd hand,odd hand,handwriting,Test scene
""")
    annotations = load_annotations_csv("""annotation_id,section,anchor_phrase,category,subcategory,actors,document_ref,claim_role,note
A1,ONE,odd hand,handwriting_identity,script,Guest,letter1,core,Test annotation
""")
    links = load_evidence_links_csv("""link_id,scene_id,annotation_id,document_ref,relation,note
L1,S1,A1,letter1,supports,Test link
""")
    assert validate_evidence_links(links, scenes, annotations, known_documents=["letter1"]) == []
    bundles = evidence_bundle_rows(links, scenes, annotations)
    assert bundles[0]["scene_title"] == "Odd hand"
    assert bundles[0]["annotation_category"] == "handwriting_identity"
    assert bundles[0]["document_ref"] == "letter1"

def test_evidence_link_validation_catches_broken_references():
    scenes = load_scenes_csv("""scene_id,section,title,anchor_phrase,scene_type,rationale
S1,ONE,Odd hand,odd hand,handwriting,Test scene
""")
    annotations = load_annotations_csv("""annotation_id,section,anchor_phrase,category,subcategory,actors,document_ref,claim_role,note
A1,ONE,odd hand,handwriting_identity,script,Guest,,core,Test annotation
""")
    links = load_evidence_links_csv("""link_id,scene_id,annotation_id,document_ref,relation,note
L1,S9,A9,missing,supports,Broken link
""")
    issues = validate_evidence_links(links, scenes, annotations, known_documents=["letter1"])
    fields = {issue["field"] for issue in issues}
    assert {"scene_id", "annotation_id", "document_ref"}.issubset(fields)

def test_evidence_graph_keeps_node_types_explicit():
    scenes = load_scenes_csv("""scene_id,section,title,anchor_phrase,scene_type,rationale
S1,ONE,Odd hand,odd hand,handwriting,Test scene
""")
    annotations = load_annotations_csv("""annotation_id,section,anchor_phrase,category,subcategory,actors,document_ref,claim_role,note
A1,ONE,odd hand,handwriting_identity,script,Guest,letter1,core,Test annotation
""")
    links = load_evidence_links_csv("""link_id,scene_id,annotation_id,document_ref,relation,note
L1,S1,A1,letter1,supports,Test link
""")
    nodes, edges = evidence_graph(links, scenes, annotations)
    assert {node["type"] for node in nodes} == {"scene", "annotation", "document"}
    assert len(edges) == 2
    assert edges[0]["source"].startswith("scene:")


def test_skipgrams_emit_only_local_bounded_combinations():
    tokens = ["t"] * 100
    grams = skipgrams(tokens, n=2, max_skip=2)
    # Distance 1, 2, or 3 only: 99 + 98 + 97.
    assert len(grams) == 294


def test_skipgrams_preserve_bounded_rule_for_higher_order_grams():
    tokens = tokenize("a b c d e")
    grams = skipgrams(tokens, n=3, max_skip=1)
    assert ("a", "b", "c") in grams
    assert ("a", "c", "e") in grams
    assert ("a", "d", "e") not in grams


def test_fetch_source_text_retries_transient_connection_errors(monkeypatch):
    calls = {"count": 0}

    class FakeResponse:
        text = "public domain text"

        def raise_for_status(self):
            return None

    def fake_get(*args, **kwargs):
        calls["count"] += 1
        if calls["count"] < 3:
            import requests
            raise requests.ConnectionError("temporary network outage")
        return FakeResponse()

    monkeypatch.setattr("stevenson_text.corpus.requests.get", fake_get)
    monkeypatch.setattr("stevenson_text.corpus.time.sleep", lambda _: None)

    assert fetch_source_text("https://example.test/text", attempts=3) == "public domain text"
    assert calls["count"] == 3

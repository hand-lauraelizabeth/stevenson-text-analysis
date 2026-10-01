from stevenson_text.analysis import concordance, count_terms, segment_term_counts, significant_collocates
from stevenson_text.annotations import (
    annotation_summary,
    load_annotations_csv,
    resolve_annotation_anchors,
    validate_annotations,
)
from stevenson_text.agreement import agreement_summary, compare_annotation_sets
from stevenson_text.corpus import segment_tokens, strip_gutenberg_wrapper, tokenize
from stevenson_text.morphology import lemma_concordance, lemma_counts, validate_lemma_groups
from stevenson_text.networks import cooccurrence_network
from stevenson_text.phrases import frequent_ngrams, frequent_skipgrams, phrase_occurrences, skipgrams
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

from stevenson_text.analysis import concordance, count_terms, segment_term_counts, significant_collocates
from stevenson_text.corpus import segment_tokens, strip_gutenberg_wrapper, tokenize

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

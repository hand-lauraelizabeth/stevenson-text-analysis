import pytest

from stevenson_text.corpus import tokenize
from stevenson_text.statistics import log_likelihood_keyness


def test_keyness_uses_full_2x2_contingency_table():
    target = tokenize("hand hand hand body body quiet")
    reference = tokenize("hand body quiet quiet quiet quiet")

    rows = log_likelihood_keyness(target, reference, min_total=2)
    by_term = {row["term"]: row for row in rows}

    # For "hand": [[3, 1], [3, 5]] produces G² = 1.5518393659605079.
    # The complement cells are essential; a term-only calculation is smaller.
    assert by_term["hand"]["g2"] == pytest.approx(1.5518393659605079)
    assert by_term["hand"]["signed_g2"] > 0


def test_keyness_handles_zero_term_count_without_zero_log_error():
    target = tokenize("hand hand hand body")
    reference = tokenize("body body body body")

    rows = log_likelihood_keyness(target, reference, min_total=2)
    by_term = {row["term"]: row for row in rows}

    assert by_term["hand"]["reference_count"] == 0
    assert by_term["hand"]["g2"] > 0
    assert by_term["hand"]["signed_g2"] > 0

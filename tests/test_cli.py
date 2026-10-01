import pytest

from stevenson_text.cli import _select_target_record
from stevenson_text.comparison import CorpusText


def test_target_selection_uses_declared_corpus_role_not_row_order():
    records = [
        CorpusText("Comparator", "B", 1890, "same_author_comparator", ("hand",)),
        CorpusText("Target", "A", 1886, "target", ("hand", "hand")),
    ]

    selected = _select_target_record(records)

    assert selected.title == "Target"
    assert selected.corpus_role == "target"


def test_target_selection_requires_exactly_one_target():
    no_target = [
        CorpusText("Comparator", "B", 1890, "same_author_comparator", ("hand",)),
    ]
    with pytest.raises(ValueError, match="exactly one"):
        _select_target_record(no_target)

    two_targets = [
        CorpusText("Target A", "A", 1886, "target", ("hand",)),
        CorpusText("Target B", "B", 1890, "target", ("body",)),
    ]
    with pytest.raises(ValueError, match="found 2"):
        _select_target_record(two_targets)

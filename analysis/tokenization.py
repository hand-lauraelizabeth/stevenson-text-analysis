"""Small, import-safe tokenizer for the legacy comparison and its tests."""
from __future__ import annotations

import re

TOKEN_RE = re.compile(r"[a-z]+(?:'[a-z]+)?", re.IGNORECASE)


def tokenize(text: str) -> list[str]:
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    normalized = text.replace("’", "'").replace("‘", "'")
    return TOKEN_RE.findall(normalized.lower())

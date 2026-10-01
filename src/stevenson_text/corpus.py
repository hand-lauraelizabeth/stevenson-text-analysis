from __future__ import annotations

from dataclasses import dataclass
import re
import time
from typing import Iterable

import requests

GUTENBERG_START = re.compile(r"\*\*\*\s*START OF THE PROJECT GUTENBERG EBOOK.*?\*\*\*", re.I | re.S)
GUTENBERG_END = re.compile(r"\*\*\*\s*END OF THE PROJECT GUTENBERG EBOOK.*?\*\*\*", re.I | re.S)
TOKEN_RE = re.compile(r"[A-Za-z]+(?:['’][A-Za-z]+)?")
HEADERS = {"User-Agent": "Laura-Hand-DH-Portfolio/2.0 (+https://github.com/hand-lauraelizabeth)"}


@dataclass(frozen=True)
class TextDocument:
    title: str
    text: str
    source_url: str | None = None

    @property
    def tokens(self) -> list[str]:
        return tokenize(self.text)


def strip_gutenberg_wrapper(text: str) -> str:
    start = GUTENBERG_START.search(text)
    if start:
        text = text[start.end():]
    end = GUTENBERG_END.search(text)
    if end:
        text = text[:end.start()]
    return text.strip()


def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace("’", "'").replace("‘", "'")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def tokenize(text: str, lowercase: bool = True) -> list[str]:
    tokens = TOKEN_RE.findall(text)
    return [token.lower() for token in tokens] if lowercase else tokens


def segment_tokens(tokens: Iterable[str], segments: int = 10) -> list[list[str]]:
    tokens = list(tokens)
    if segments < 1:
        raise ValueError("segments must be >= 1")
    if not tokens:
        return [[] for _ in range(segments)]
    base, remainder = divmod(len(tokens), segments)
    output = []
    start = 0
    for index in range(segments):
        width = base + (1 if index < remainder else 0)
        output.append(tokens[start:start + width])
        start += width
    return output


def fetch_source_text(
    source_url: str,
    timeout: int | float = 30,
    attempts: int = 3,
    backoff_seconds: float = 1.0,
) -> str:
    """Fetch a public corpus source with bounded retries for transient outages."""
    if attempts < 1:
        raise ValueError("attempts must be >= 1")

    last_error: requests.RequestException | None = None
    for attempt in range(1, attempts + 1):
        try:
            response = requests.get(source_url, timeout=timeout, headers=HEADERS)
            response.raise_for_status()
            return response.text
        except requests.RequestException as exc:
            last_error = exc
            if attempt == attempts:
                break
            time.sleep(backoff_seconds * (2 ** (attempt - 1)))

    assert last_error is not None
    raise last_error


def fetch_document(
    title: str,
    source_url: str,
    timeout: int | float = 30,
    attempts: int = 3,
) -> TextDocument:
    raw = fetch_source_text(source_url, timeout=timeout, attempts=attempts)
    body = normalize_text(strip_gutenberg_wrapper(raw))
    if len(body) < 1000:
        raise ValueError(f"Downloaded text for {title!r} was unexpectedly short.")
    return TextDocument(title=title, text=body, source_url=source_url)

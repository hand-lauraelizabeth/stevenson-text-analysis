from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Iterable

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

GUTENBERG_START = re.compile(r"\*\*\*\s*START OF THE PROJECT GUTENBERG EBOOK.*?\*\*\*", re.I | re.S)
GUTENBERG_END = re.compile(r"\*\*\*\s*END OF THE PROJECT GUTENBERG EBOOK.*?\*\*\*", re.I | re.S)
TOKEN_RE = re.compile(r"[A-Za-z]+(?:['’][A-Za-z]+)?")
HEADERS = {"User-Agent": "Laura-Hand-DH-Portfolio/2.0 (+https://github.com/hand-lauraelizabeth)"}
RETRYABLE_STATUS_CODES = (429, 500, 502, 503, 504)


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


def _retrying_session(retries: int = 3, backoff_factor: float = 0.75) -> requests.Session:
    """Build a session that tolerates transient source-host failures.

    The public corpus is intentionally fetched from Project Gutenberg rather
    than committed to the repository. CI should therefore retry temporary
    throttling and server/network errors instead of treating a single failed
    request as a research-code failure.
    """
    retry = Retry(
        total=retries,
        connect=retries,
        read=retries,
        status=retries,
        backoff_factor=backoff_factor,
        status_forcelist=RETRYABLE_STATUS_CODES,
        allowed_methods=frozenset({"GET"}),
        respect_retry_after_header=True,
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def fetch_document(
    title: str,
    source_url: str,
    timeout: int = 30,
    retries: int = 3,
) -> TextDocument:
    with _retrying_session(retries=retries) as session:
        response = session.get(source_url, timeout=timeout, headers=HEADERS)
        response.raise_for_status()
        body = normalize_text(strip_gutenberg_wrapper(response.text))
    if len(body) < 1000:
        raise ValueError(f"Downloaded text for {title!r} was unexpectedly short.")
    return TextDocument(title=title, text=body, source_url=source_url)

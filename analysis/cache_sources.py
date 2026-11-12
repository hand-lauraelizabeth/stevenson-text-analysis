"""Checksum-verified local cache for public-domain Gutenberg source downloads.

First acquisition requires a trusted HTTPS connection. Its SHA-256 is stored
locally; subsequent runs can operate offline and reject changed bytes.
A first-use checksum is a consistency record, not independent source
authentication or a committed, independently reviewed corpus snapshot.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from urllib.parse import urlsplit

import requests

HEADERS = {"User-Agent": "Laura-Hand-DH-Portfolio/1.1 (+https://github.com/hand-lauraelizabeth)"}


def load_source_text(ebook_id: int | str, source_url: str, cache_dir: Path, *, offline: bool = False) -> str:
    parsed = urlsplit(source_url)
    if parsed.scheme != "https" or parsed.hostname not in {"www.gutenberg.org", "gutenberg.org"}:
        raise ValueError("Source must be an official HTTPS Project Gutenberg URL.")
    stem = str(ebook_id)
    if not stem.isdecimal():
        raise ValueError("Project Gutenberg ebook ID must be numeric.")
    cache_dir = Path(cache_dir)
    data_path = cache_dir / f"gutenberg-{stem}.txt"
    checksum_path = cache_dir / f"gutenberg-{stem}.sha256"

    if data_path.exists():
        if not checksum_path.exists():
            raise ValueError(f"Cache for eBook {stem} has no checksum; refusing unverified bytes.")
        expected = checksum_path.read_text(encoding="ascii").strip()
        data = data_path.read_bytes()
        actual = hashlib.sha256(data).hexdigest()
        if len(expected) != 64 or actual != expected:
            raise ValueError(f"Checksum mismatch for cached eBook {stem}; refusing altered data.")
        return data.decode("utf-8-sig")

    if checksum_path.exists():
        raise ValueError(f"Cache for eBook {stem} lost its source file; no silent redownload.")
    if offline:
        raise FileNotFoundError(f"Verified cached eBook {stem} unavailable. Populate the cache first.")

    response = requests.get(source_url, timeout=30, headers=HEADERS)
    response.raise_for_status()
    data = response.content
    if len(data) < 1000 or b"*** START OF THE PROJECT GUTENBERG EBOOK" not in data:
        raise ValueError(f"Downloaded source for eBook {stem} is incomplete or not Gutenberg text.")
    text = data.decode("utf-8-sig")
    checksum = hashlib.sha256(data).hexdigest()
    cache_dir.mkdir(parents=True, exist_ok=True)
    tmp_data = data_path.with_suffix(".txt.tmp")
    tmp_checksum = checksum_path.with_suffix(".sha256.tmp")
    tmp_data.write_bytes(data)
    tmp_checksum.write_text(checksum + "\n", encoding="ascii")
    tmp_data.replace(data_path)
    tmp_checksum.replace(checksum_path)
    return text

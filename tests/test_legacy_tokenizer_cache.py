"""Offline tokenizer and cache regression tests for the legacy script."""
import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from analysis.tokenization import tokenize
from analysis.cache_sources import load_source_text
from analysis.compare_texts import strip_gutenberg_wrapper


class TokenizerTests(unittest.TestCase):
    def test_distinguishes_hyde_from_hide(self):
        tokens = tokenize("Hyde may hide; Hyde writes.")
        self.assertEqual(tokens.count("hyde"), 2)
        self.assertEqual(tokens.count("hide"), 1)

    def test_normalizes_apostrophes_and_preserves_contractions(self):
        self.assertEqual(tokenize("Don’t don’t"), ["don't", "don't"])

    def test_hyphen_is_not_a_word(self):
        self.assertEqual(tokenize("hand-written"), ["hand", "written"])

    def test_wrap_removal(self):
        raw = "Header\n*** START OF THE PROJECT GUTENBERG EBOOK TEST ***\nHyde hides.\n*** END OF THE PROJECT GUTENBERG EBOOK TEST ***\nLicense"
        self.assertEqual(strip_gutenberg_wrapper(raw), "Hyde hides.")


class CacheTests(unittest.TestCase):
    URL = "https://www.gutenberg.org/cache/epub/43/pg43.txt"

    def test_cache_is_checksum_verified_and_offline_reusable(self):
        text = b"*** START OF THE PROJECT GUTENBERG EBOOK TEST ***\n" + b"Hyde may hide. " * 100 + b"\n*** END OF THE PROJECT GUTENBERG EBOOK TEST ***"
        class Response:
            content = text
            def raise_for_status(self):
                pass
        with tempfile.TemporaryDirectory() as tmp:
            cache = Path(tmp)
            with patch("analysis.cache_sources.requests.get", return_value=Response()) as remote:
                self.assertEqual(load_source_text(43, self.URL, cache), text.decode("utf-8"))
                remote.assert_called_once()
            self.assertEqual(load_source_text(43, self.URL, cache, offline=True), text.decode("utf-8"))
            self.assertEqual((cache / "gutenberg-43.sha256").read_text().strip(), hashlib.sha256(text).hexdigest())
            (cache / "gutenberg-43.txt").write_bytes(text + b"modified")
            with self.assertRaisesRegex(ValueError, "Checksum mismatch"):
                load_source_text(43, self.URL, cache, offline=True)

    def test_offline_cache_miss_never_fetches(self):
        with tempfile.TemporaryDirectory() as tmp, patch("analysis.cache_sources.requests.get") as remote:
            with self.assertRaises(FileNotFoundError):
                load_source_text(43, self.URL, Path(tmp), offline=True)
            remote.assert_not_called()

    def test_refuses_untrusted_hosts(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "official HTTPS"):
                load_source_text(43, "http://example.invalid/43.txt", Path(tmp))


if __name__ == "__main__":
    unittest.main()

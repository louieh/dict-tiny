from unittest.mock import MagicMock, patch

import pytest

from dict_tiny.translators.google_trans import GoogleTrans


class TestGoogleTransUnit:
    """GoogleTrans translate and detect_language unit tests (mocked network)."""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.mock_obj = MagicMock()
        self.mock_obj.source_language = None
        self.mock_obj.target_language = None
        self.mock_obj.wordbook = None
        self.mock_obj.detect_language = False
        self.trans = GoogleTrans("hello", self.mock_obj)

    # ── do_translate ─────────────────────────────────────────

    def test_do_translate_detect_language_returns_false(self):
        """Returns False when --detect-language is set (skip translation)."""
        self.mock_obj.detect_language = True
        with patch.object(self.trans, "detect_language", return_value=True):
            result = self.trans.do_translate("hello")
        assert not result

    def test_do_translate_empty_response(self):
        """Returns False when the API returns None."""
        with patch("dict_tiny.translators.google_trans.downloader") as mock_dl:
            mock_dl.post.return_value = None
            result = self.trans.do_translate("hello")
        assert not result

    def test_do_translate_invalid_json(self):
        """Returns False when the API returns non-JSON response."""
        resp = MagicMock()
        resp.json.side_effect = ValueError("bad json")
        resp.text = "not json"
        with patch("dict_tiny.translators.google_trans.downloader") as mock_dl:
            mock_dl.post.return_value = resp
            result = self.trans.do_translate("hello")
        assert not result

    def test_do_translate_non_200(self):
        """Returns False when the API returns a non-200 status code."""
        resp = MagicMock()
        resp.json.return_value = {"code": 500, "msg": "server error"}
        with patch("dict_tiny.translators.google_trans.downloader") as mock_dl:
            mock_dl.post.return_value = resp
            result = self.trans.do_translate("hello")
        assert not result

    def test_do_translate_success(self):
        """Returns True on successful API response and prints translated text."""
        resp = MagicMock()
        resp.json.return_value = {
            "code": 200,
            "data": {"translatedText": "你好", "detectedSourceLanguage": "en"},
        }
        with patch("dict_tiny.translators.google_trans.downloader") as mock_dl:
            mock_dl.post.return_value = resp
            result = self.trans.do_translate("hello")
        assert result

    # ── detect_language ──────────────────────────────────────

    def test_detect_language_empty_response(self):
        """Returns False when the detect API returns None."""
        with patch("dict_tiny.translators.google_trans.downloader") as mock_dl:
            mock_dl.post.return_value = None
            result = self.trans.detect_language("hello")
        assert not result

    def test_detect_language_invalid_json(self):
        """Returns False when the detect API returns non-JSON response."""
        resp = MagicMock()
        resp.json.side_effect = ValueError("bad json")
        resp.text = "not json"
        with patch("dict_tiny.translators.google_trans.downloader") as mock_dl:
            mock_dl.post.return_value = resp
            result = self.trans.detect_language("hello")
        assert not result

    def test_detect_language_non_200(self):
        """Returns False when the detect API returns a non-200 status code."""
        resp = MagicMock()
        resp.json.return_value = {"code": 500, "msg": "server error"}
        with patch("dict_tiny.translators.google_trans.downloader") as mock_dl:
            mock_dl.post.return_value = resp
            result = self.trans.detect_language("hello")
        assert not result

    def test_detect_language_success(self):
        """Returns True on successful detect API response and prints detected language."""
        resp = MagicMock()
        resp.json.return_value = {
            "code": 200,
            "data": {"detectedLanguage": "en"},
        }
        with patch("dict_tiny.translators.google_trans.downloader") as mock_dl:
            mock_dl.post.return_value = resp
            result = self.trans.detect_language("hello")
        assert result

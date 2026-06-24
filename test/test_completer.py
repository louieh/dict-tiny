from unittest.mock import MagicMock, patch

import pytest

from dict_tiny.completer import YoudaoCompleter


class TestYoudaoCompleter:
    """YoudaoCompleter suggestion API tests."""

    @pytest.fixture(autouse=True)
    def _setup(self):
        self.document = MagicMock()
        self.mock_event = MagicMock()

    def _mock_response(self, entries=None, code=200):
        resp = MagicMock()
        resp.json.return_value = {
            "result": {"code": code},
            "data": {"entries": entries or []},
        }
        return resp

    def test_get_completions_success(self):
        """Returns completions with correct text and start_position."""
        self.document.get_word_before_cursor.return_value = "boo"
        resp = self._mock_response(
            entries=[
                {"entry": "book", "explain": "n. 书"},
                {"entry": "books", "explain": "n. 书籍(复数)"},
            ]
        )
        with patch("dict_tiny.completer.downloader") as mock_dl:
            mock_dl.get.return_value = resp
            completions = list(
                YoudaoCompleter("en").get_completions(self.document, self.mock_event)
            )
        assert len(completions) == 2
        assert completions[0].text == "book"
        assert completions[0].start_position == -3
        assert completions[1].text == "books"

    def test_get_completions_empty_response(self):
        """Returns empty list when API returns None."""
        with patch("dict_tiny.completer.downloader") as mock_dl:
            mock_dl.get.return_value = None
            completions = list(
                YoudaoCompleter("en").get_completions(self.document, self.mock_event)
            )
        assert completions == []

    def test_get_completions_non_200_code(self):
        """Returns empty list when API returns non-200 code."""
        resp = self._mock_response(code=404)
        with patch("dict_tiny.completer.downloader") as mock_dl:
            mock_dl.get.return_value = resp
            completions = list(
                YoudaoCompleter("en").get_completions(self.document, self.mock_event)
            )
        assert completions == []

    def test_get_completions_missing_entries_key(self):
        """Returns empty list when entries key is missing."""
        resp = MagicMock()
        resp.json.return_value = {"result": {"code": 200}, "data": {}}
        with patch("dict_tiny.completer.downloader") as mock_dl:
            mock_dl.get.return_value = resp
            completions = list(
                YoudaoCompleter("en").get_completions(self.document, self.mock_event)
            )
        assert completions == []

    def test_get_completions_json_decode_error(self):
        """Returns empty list when JSON decoding fails."""
        resp = MagicMock()
        resp.json.side_effect = ValueError("bad json")
        with patch("dict_tiny.completer.downloader") as mock_dl:
            mock_dl.get.return_value = resp
            completions = list(
                YoudaoCompleter("en").get_completions(self.document, self.mock_event)
            )
        assert completions == []

    def test_get_completions_truncates_explain_to_10(self):
        """Truncates display_meta to 10 characters."""
        self.document.get_word_before_cursor.return_value = "w"
        resp = self._mock_response(entries=[{"entry": "word", "explain": "a" * 50}])
        with patch("dict_tiny.completer.downloader") as mock_dl:
            mock_dl.get.return_value = resp
            with patch("dict_tiny.completer.Completion") as MockCompletion:
                list(
                    YoudaoCompleter("en").get_completions(
                        self.document, self.mock_event
                    )
                )
        _, call_kwargs = MockCompletion.call_args
        assert call_kwargs["display_meta"] == "a" * 10

    def test_get_completions_uses_le_in_url(self):
        """Uses the correct le parameter in the API URL."""
        resp = self._mock_response()
        with patch("dict_tiny.completer.downloader") as mock_dl:
            mock_dl.get.return_value = resp
            list(YoudaoCompleter("ja").get_completions(self.document, self.mock_event))
        args, _ = mock_dl.get.call_args
        assert "le=ja" in args[0]

    def test_get_completions_generic_exception(self):
        """Returns empty list when JSON parsing raises unexpected exception."""
        resp = MagicMock()
        resp.json.side_effect = RuntimeError("unexpected")
        with patch("dict_tiny.completer.downloader") as mock_dl:
            mock_dl.get.return_value = resp
            completions = list(
                YoudaoCompleter("en").get_completions(self.document, self.mock_event)
            )
        assert completions == []

    def test_get_completions_start_position_matches_word_length(self):
        """Start position is negative length of the word before cursor."""
        self.document.get_word_before_cursor.return_value = "hello"
        resp = self._mock_response(
            entries=[{"entry": "hello world", "explain": "greeting"}]
        )
        with patch("dict_tiny.completer.downloader") as mock_dl:
            mock_dl.get.return_value = resp
            completions = list(
                YoudaoCompleter("en").get_completions(self.document, self.mock_event)
            )
        assert len(completions) == 1
        assert completions[0].start_position == -5

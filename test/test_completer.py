from unittest.mock import MagicMock, patch

from dict_tiny.completer import YoudaoCompleter


def _document(word_before_cursor):
    doc = MagicMock()
    doc.get_word_before_cursor.return_value = word_before_cursor
    return doc


def _make_completer(le="en"):
    return YoudaoCompleter(le)


class TestYoudaoCompleter:
    def test_get_completions_success(self):
        resp = MagicMock()
        resp.json.return_value = {
            "result": {"code": 200},
            "data": {
                "entries": [
                    {"entry": "book", "explain": "n. 书"},
                    {"entry": "books", "explain": "n. 书籍(复数)"},
                ]
            },
        }
        with patch("dict_tiny.completer.downloader") as mock_dl:
            mock_dl.get.return_value = resp
            completer = _make_completer("en")
            completions = list(completer.get_completions(_document("boo"), MagicMock()))
        assert len(completions) == 2
        assert completions[0].text == "book"
        assert completions[0].start_position == -3
        assert completions[1].text == "books"

    def test_get_completions_empty_response(self):
        with patch("dict_tiny.completer.downloader") as mock_dl:
            mock_dl.get.return_value = None
            completer = _make_completer()
            completions = list(completer.get_completions(_document("x"), MagicMock()))
        assert completions == []

    def test_get_completions_non_200_code(self):
        resp = MagicMock()
        resp.json.return_value = {"result": {"code": 404}, "data": {"entries": []}}
        with patch("dict_tiny.completer.downloader") as mock_dl:
            mock_dl.get.return_value = resp
            completer = _make_completer()
            completions = list(completer.get_completions(_document("x"), MagicMock()))
        assert completions == []

    def test_get_completions_missing_entries_key(self):
        resp = MagicMock()
        resp.json.return_value = {"result": {"code": 200}, "data": {}}
        with patch("dict_tiny.completer.downloader") as mock_dl:
            mock_dl.get.return_value = resp
            completer = _make_completer()
            completions = list(completer.get_completions(_document("x"), MagicMock()))
        assert completions == []

    def test_get_completions_json_decode_error(self):
        resp = MagicMock()
        resp.json.side_effect = ValueError("bad json")
        with patch("dict_tiny.completer.downloader") as mock_dl:
            mock_dl.get.return_value = resp
            completer = _make_completer()
            completions = list(completer.get_completions(_document("x"), MagicMock()))
        assert completions == []

    def test_get_completions_truncates_explain_to_10(self):
        long_explain = "a" * 50
        resp = MagicMock()
        resp.json.return_value = {
            "result": {"code": 200},
            "data": {"entries": [{"entry": "w", "explain": long_explain}]},
        }
        captured = []
        with patch("dict_tiny.completer.downloader") as mock_dl:
            mock_dl.get.return_value = resp
            with patch(
                "dict_tiny.completer.Completion",
                side_effect=lambda *a, **kw: captured.append(kw) or MagicMock(),
            ):
                completer = _make_completer()
                list(completer.get_completions(_document("w"), MagicMock()))
        assert len(captured) == 1
        assert len(captured[0]["display_meta"]) == 10

    def test_get_completions_uses_le_in_url(self):
        resp = MagicMock()
        resp.json.return_value = {"result": {"code": 200}, "data": {"entries": []}}
        with patch("dict_tiny.completer.downloader") as mock_dl:
            mock_dl.get.return_value = resp
            completer = _make_completer("ja")
            list(completer.get_completions(_document("hon"), MagicMock()))
        args, kwargs = mock_dl.get.call_args
        assert "le=ja" in args[0]

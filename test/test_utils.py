from unittest.mock import MagicMock, patch

from dict_tiny.util import (
    Downloader,
    get_cn_length,
    get_terminal_size_column,
    is_alphabet,
    parse_le,
    print_equal,
    remove_html_tags,
)


class TestIsAlphabet:
    def test_empty(self):
        assert is_alphabet("") == "other"
        assert is_alphabet(" ") == "other"

    def test_english(self):
        assert is_alphabet("book") == "en"
        assert is_alphabet("database") == "en"
        assert is_alphabet("Hello") == "en"
        assert is_alphabet("hello world") == "en"

    def test_chinese(self):
        assert is_alphabet("书") == "zh"
        assert is_alphabet("数据库") == "zh"
        assert is_alphabet("你好世界") == "zh"

    def test_mixed_more_chinese(self):
        assert is_alphabet("如何用Python实现web scraping") == "zh"
        assert is_alphabet("Hello世界") == "zh"

    def test_mixed_more_english(self):
        assert is_alphabet("How are you 你好") == "en"

    def test_equal_english_chinese(self):
        assert is_alphabet("book书") == "zh"

    def test_equal_mixed(self):
        assert is_alphabet("你 A") == "zh"

    def test_mixed_more_english_2(self):
        assert is_alphabet("How are you 你好") == "en"

    def test_hyphenated_english(self):
        assert is_alphabet("don't") == "en"
        assert is_alphabet("well-known") == "en"
        assert is_alphabet("state-of-the-art") == "en"
        assert is_alphabet("don't 我不知道") == "zh"

    def test_non_alpha(self):
        assert is_alphabet("123") == "other"
        assert is_alphabet("...") == "other"
        assert is_alphabet("!@#") == "other"
        assert is_alphabet("   ") == "other"


class TestParseLe:
    def test_no_source_no_target(self):
        assert parse_le("", "") == "en"

    def test_source_english(self):
        assert parse_le("en", "") == "en"

    def test_target_japanese(self):
        assert parse_le("", "ja") == "ja"
        assert parse_le("en", "ja") == "en"

    def test_source_french(self):
        assert parse_le("fr", "") == "fr"

    def test_source_korean(self):
        assert parse_le("ko", "") == "ko"

    def test_source_unsupported(self):
        assert parse_le("pl", "en") == "en"
        assert parse_le("", "pl") == "en"

    def test_source_and_target_unsupported(self):
        assert parse_le("pl", "de") == "en"


class TestGetCnLength:
    def test_empty(self):
        assert get_cn_length("") == 0

    def test_english_only(self):
        assert get_cn_length("hello") == 0

    def test_chinese_only(self):
        assert get_cn_length("你好世界") == 4
        assert get_cn_length("书") == 1

    def test_mixed(self):
        assert get_cn_length("hello你好") == 2
        assert get_cn_length("Python编程") == 2

    def test_numbers_and_symbols(self):
        assert get_cn_length("123") == 0
        assert get_cn_length("!@#") == 0


class TestRemoveHtmlTags:
    def test_no_tags(self):
        assert remove_html_tags("hello world") == "hello world"

    def test_with_tags(self):
        assert remove_html_tags("<b>hello</b>") == "hello"
        assert remove_html_tags("<br/>") == ""
        assert remove_html_tags("<div>hello</div>world") == "helloworld"

    def test_nested_tags(self):
        assert remove_html_tags("<div><b>hello</b></div>") == "hello"

    def test_empty(self):
        assert remove_html_tags("") == ""
        assert remove_html_tags("<div></div>") == ""

    def test_mixed_content(self):
        text = "Hello <b>bold</b> and <i>italic</i>."
        assert remove_html_tags(text) == "Hello bold and italic."


class TestGetTerminalSizeColumn:
    def test_returns_int(self):
        result = get_terminal_size_column()
        assert isinstance(result, int)
        assert result > 0

    def test_fallback_on_error(self):
        with patch("os.get_terminal_size", side_effect=OSError("no tty")):
            assert get_terminal_size_column() == 20


class TestPrintEqual:
    def test_long_string_uses_eight_equal_format(self):
        with patch("dict_tiny.util.get_terminal_size_column", return_value=80):
            with patch("dict_tiny.util.normal_title_printer") as mock_print:
                print_equal("book")
                mock_print.assert_called_once()
                call_arg = mock_print.call_args[0][0]
                assert "book" in call_arg
                assert call_arg.startswith("========")

    def test_short_string_fallback(self):
        with patch("dict_tiny.util.get_terminal_size_column", return_value=10):
            with patch("dict_tiny.util.normal_title_printer") as mock_print:
                print_equal("a" * 20)
                mock_print.assert_called_once_with("a" * 20)


class TestDownloader:
    def _make(self):
        dl = Downloader(retries=1, backoff_factor=0, timeout=5)
        dl._session = MagicMock()
        return dl

    def test_download_returns_resp_on_200(self):
        dl = self._make()
        resp = MagicMock()
        resp.status_code = 200
        dl._session.request.return_value = resp
        result = dl.download("GET", "http://example.com")
        assert result is resp

    def test_download_returns_none_on_non_200(self):
        dl = self._make()
        resp = MagicMock()
        resp.status_code = 404
        dl._session.request.return_value = resp
        with patch("dict_tiny.util.normal_warn_printer") as mock_warn:
            result = dl.download("GET", "http://example.com")
        assert result is None
        mock_warn.assert_called_once()

    def test_download_handles_connection_error(self):
        dl = self._make()
        import requests

        dl._session.request.side_effect = requests.exceptions.ConnectionError(
            "no network"
        )
        with patch("dict_tiny.util.normal_error_printer") as mock_err:
            result = dl.download("GET", "http://example.com")
        assert result is None
        mock_err.assert_called_once()

    def test_download_handles_timeout(self):
        dl = self._make()
        import requests

        dl._session.request.side_effect = requests.exceptions.Timeout()
        with patch("dict_tiny.util.normal_error_printer") as mock_err:
            result = dl.download("GET", "http://example.com")
        assert result is None
        mock_err.assert_called_once()

    def test_download_handles_generic_exception(self):
        dl = self._make()
        dl._session.request.side_effect = RuntimeError("boom")
        with patch("dict_tiny.util.normal_error_printer") as mock_err:
            result = dl.download("GET", "http://example.com")
        assert result is None
        mock_err.assert_called_once()

    def test_download_pops_timeout_kwarg(self):
        dl = self._make()
        resp = MagicMock()
        resp.status_code = 200
        dl._session.request.return_value = resp
        dl.download("GET", "http://example.com", timeout=10, headers={"X": "y"})
        args, kwargs = dl._session.request.call_args
        assert args[0] == "GET"
        assert args[1] == "http://example.com"
        assert kwargs["timeout"] == 10
        assert kwargs["headers"] == {"X": "y"}

    def test_get_and_post_delegate_to_download(self):
        dl = self._make()
        with patch.object(dl, "download", return_value="ok") as mock_dl:
            assert dl.get("http://e.com") == "ok"
            mock_dl.assert_called_with("GET", "http://e.com")
            assert dl.post("http://e.com", json={"a": 1}) == "ok"
            mock_dl.assert_called_with("POST", "http://e.com", json={"a": 1})

    def test_session_lazy_init(self):
        dl = Downloader(retries=1, backoff_factor=0, timeout=5)
        assert dl._session is None
        with patch("requests.Session") as MockSession:
            with patch("requests.adapters.HTTPAdapter"):
                with patch("requests.adapters.Retry"):
                    mock_session = MagicMock()
                    MockSession.return_value = mock_session
                    session1 = dl.session
                    session2 = dl.session
                    assert session1 is session2
                    MockSession.assert_called_once()

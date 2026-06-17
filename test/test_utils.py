import unittest
from unittest.mock import MagicMock, patch

from dict_tiny.util import (
    is_alphabet,
    parse_le,
    get_cn_length,
    remove_html_tags,
    get_terminal_size_column,
    print_equal,
    Downloader,
)


class TestIsAlphabet(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(is_alphabet(""), "other")
        self.assertEqual(is_alphabet(" "), "other")

    def test_english(self):
        self.assertEqual(is_alphabet("book"), "en")
        self.assertEqual(is_alphabet("database"), "en")
        self.assertEqual(is_alphabet("Hello"), "en")
        self.assertEqual(is_alphabet("hello world"), "en")

    def test_chinese(self):
        self.assertEqual(is_alphabet("书"), "zh")
        self.assertEqual(is_alphabet("数据库"), "zh")
        self.assertEqual(is_alphabet("你好世界"), "zh")

    def test_mixed_more_chinese(self):
        self.assertEqual(is_alphabet("如何用Python实现web scraping"), "zh")
        self.assertEqual(is_alphabet("Hello世界"), "zh")

    def test_mixed_more_english(self):
        self.assertEqual(is_alphabet("How are you 你好"), "en")

    def test_equal_english_chinese(self):
        self.assertEqual(is_alphabet("book书"), "zh")

    def test_equal_mixed(self):
        self.assertEqual(is_alphabet("你 A"), "zh")

    def test_mixed_more_english_2(self):
        self.assertEqual(is_alphabet("How are you 你好"), "en")

    def test_hyphenated_english(self):
        self.assertEqual(is_alphabet("don't"), "en")
        self.assertEqual(is_alphabet("well-known"), "en")
        self.assertEqual(is_alphabet("state-of-the-art"), "en")
        self.assertEqual(is_alphabet("don't 我不知道"), "zh")

    def test_non_alpha(self):
        self.assertEqual(is_alphabet("123"), "other")
        self.assertEqual(is_alphabet("..."), "other")
        self.assertEqual(is_alphabet("!@#"), "other")
        self.assertEqual(is_alphabet("   "), "other")


class TestParseLe(unittest.TestCase):
    def test_no_source_no_target(self):
        self.assertEqual(parse_le("", ""), "en")

    def test_source_english(self):
        self.assertEqual(parse_le("en", ""), "en")

    def test_target_japanese(self):
        self.assertEqual(parse_le("", "ja"), "ja")
        self.assertEqual(parse_le("en", "ja"), "en")

    def test_source_french(self):
        self.assertEqual(parse_le("fr", ""), "fr")

    def test_source_korean(self):
        self.assertEqual(parse_le("ko", ""), "ko")

    def test_source_unsupported(self):
        self.assertEqual(parse_le("pl", "en"), "en")
        self.assertEqual(parse_le("", "pl"), "en")

    def test_source_and_target_unsupported(self):
        self.assertEqual(parse_le("pl", "de"), "en")


class TestGetCnLength(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(get_cn_length(""), 0)

    def test_english_only(self):
        self.assertEqual(get_cn_length("hello"), 0)

    def test_chinese_only(self):
        self.assertEqual(get_cn_length("你好世界"), 4)
        self.assertEqual(get_cn_length("书"), 1)

    def test_mixed(self):
        self.assertEqual(get_cn_length("hello你好"), 2)
        self.assertEqual(get_cn_length("Python编程"), 2)

    def test_numbers_and_symbols(self):
        self.assertEqual(get_cn_length("123"), 0)
        self.assertEqual(get_cn_length("!@#"), 0)


class TestRemoveHtmlTags(unittest.TestCase):
    def test_no_tags(self):
        self.assertEqual(remove_html_tags("hello world"), "hello world")

    def test_with_tags(self):
        self.assertEqual(remove_html_tags("<b>hello</b>"), "hello")
        self.assertEqual(remove_html_tags("<br/>"), "")
        self.assertEqual(remove_html_tags("<div>hello</div>world"), "helloworld")

    def test_nested_tags(self):
        self.assertEqual(remove_html_tags("<div><b>hello</b></div>"), "hello")

    def test_empty(self):
        self.assertEqual(remove_html_tags(""), "")
        self.assertEqual(remove_html_tags("<div></div>"), "")

    def test_mixed_content(self):
        text = "Hello <b>bold</b> and <i>italic</i>."
        self.assertEqual(remove_html_tags(text), "Hello bold and italic.")


class TestGetTerminalSizeColumn(unittest.TestCase):
    def test_returns_int(self):
        result = get_terminal_size_column()
        self.assertIsInstance(result, int)
        self.assertGreater(result, 0)

    def test_fallback_on_error(self):
        with patch("os.get_terminal_size", side_effect=OSError("no tty")):
            self.assertEqual(get_terminal_size_column(), 20)


class TestPrintEqual(unittest.TestCase):
    def test_long_string_uses_eight_equal_format(self):
        with patch("dict_tiny.util.get_terminal_size_column", return_value=80):
            with patch("dict_tiny.util.normal_title_printer") as mock_print:
                print_equal("book")
                mock_print.assert_called_once()
                call_arg = mock_print.call_args[0][0]
                self.assertIn("book", call_arg)
                self.assertTrue(call_arg.startswith("========"))

    def test_short_string_fallback(self):
        # When terminal is too narrow, just prints the string
        with patch("dict_tiny.util.get_terminal_size_column", return_value=10):
            with patch("dict_tiny.util.normal_title_printer") as mock_print:
                print_equal("a" * 20)
                mock_print.assert_called_once_with("a" * 20)


class TestDownloader(unittest.TestCase):
    def _make(self):
        dl = Downloader(retries=1, backoff_factor=0, timeout=5)
        # Pre-populate _session with a mock so the lazy property doesn't trigger
        dl._session = MagicMock()
        return dl

    def test_download_returns_resp_on_200(self):
        dl = self._make()
        resp = MagicMock()
        resp.status_code = 200
        dl._session.request.return_value = resp
        result = dl.download("GET", "http://example.com")
        self.assertIs(result, resp)

    def test_download_returns_none_on_non_200(self):
        dl = self._make()
        resp = MagicMock()
        resp.status_code = 404
        dl._session.request.return_value = resp
        with patch("dict_tiny.util.normal_warn_printer") as mock_warn:
            result = dl.download("GET", "http://example.com")
            self.assertIsNone(result)
            mock_warn.assert_called_once()

    def test_download_handles_connection_error(self):
        dl = self._make()
        import requests

        dl._session.request.side_effect = requests.exceptions.ConnectionError(
            "no network"
        )
        with patch("dict_tiny.util.normal_error_printer") as mock_err:
            result = dl.download("GET", "http://example.com")
            self.assertIsNone(result)
            mock_err.assert_called_once()

    def test_download_handles_timeout(self):
        dl = self._make()
        import requests

        dl._session.request.side_effect = requests.exceptions.Timeout()
        with patch("dict_tiny.util.normal_error_printer") as mock_err:
            result = dl.download("GET", "http://example.com")
            self.assertIsNone(result)
            mock_err.assert_called_once()

    def test_download_handles_generic_exception(self):
        dl = self._make()
        dl._session.request.side_effect = RuntimeError("boom")
        with patch("dict_tiny.util.normal_error_printer") as mock_err:
            result = dl.download("GET", "http://example.com")
            self.assertIsNone(result)
            mock_err.assert_called_once()

    def test_download_pops_timeout_kwarg(self):
        dl = self._make()
        resp = MagicMock()
        resp.status_code = 200
        dl._session.request.return_value = resp
        dl.download("GET", "http://example.com", timeout=10, headers={"X": "y"})
        args, kwargs = dl._session.request.call_args
        self.assertEqual(args[0], "GET")
        self.assertEqual(args[1], "http://example.com")
        self.assertEqual(kwargs["timeout"], 10)
        self.assertEqual(kwargs["headers"], {"X": "y"})

    def test_get_and_post_delegate_to_download(self):
        dl = self._make()
        with patch.object(dl, "download", return_value="ok") as mock_dl:
            self.assertEqual(dl.get("http://e.com"), "ok")
            mock_dl.assert_called_with("GET", "http://e.com")
            self.assertEqual(dl.post("http://e.com", json={"a": 1}), "ok")
            mock_dl.assert_called_with("POST", "http://e.com", json={"a": 1})

    def test_session_lazy_init(self):
        dl = Downloader(retries=1, backoff_factor=0, timeout=5)
        self.assertIsNone(dl._session)
        with patch("requests.Session") as MockSession:
            with patch("requests.adapters.HTTPAdapter"):
                with patch("requests.adapters.Retry"):
                    mock_session = MagicMock()
                    MockSession.return_value = mock_session
                    session1 = dl.session
                    session2 = dl.session
                    self.assertIs(session1, session2)
                    MockSession.assert_called_once()


if __name__ == "__main__":
    unittest.main()

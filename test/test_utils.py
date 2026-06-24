from unittest.mock import MagicMock, patch

import pytest
import requests

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
    """Tests for is_alphabet language detection function."""

    def test_empty(self):
        """Empty or whitespace strings return 'other'."""
        assert is_alphabet("") == "other"
        assert is_alphabet(" ") == "other"

    def test_english(self):
        """English text is detected as 'en'."""
        assert is_alphabet("book") == "en"
        assert is_alphabet("database") == "en"
        assert is_alphabet("Hello") == "en"
        assert is_alphabet("hello world") == "en"

    def test_chinese(self):
        """Chinese text is detected as 'zh'."""
        assert is_alphabet("书") == "zh"
        assert is_alphabet("数据库") == "zh"
        assert is_alphabet("你好世界") == "zh"

    def test_mixed_more_chinese(self):
        """Mixed text with more Chinese is detected as 'zh'."""
        assert is_alphabet("如何用Python实现web scraping") == "zh"
        assert is_alphabet("Hello世界") == "zh"

    def test_mixed_more_english(self):
        """Mixed text with more English is detected as 'en'."""
        assert is_alphabet("How are you 你好") == "en"

    def test_equal_english_chinese(self):
        """Mixed text with equal length defaults to 'zh'."""
        assert is_alphabet("book书") == "zh"

    def test_equal_mixed(self):
        """Single Chinese and single English character defaults to 'zh'."""
        assert is_alphabet("你 A") == "zh"

    def test_hyphenated_english(self):
        """Hyphenated or apostrophe English is still 'en'."""
        assert is_alphabet("don't") == "en"
        assert is_alphabet("well-known") == "en"
        assert is_alphabet("state-of-the-art") == "en"
        assert is_alphabet("don't 我不知道") == "zh"

    def test_non_alpha(self):
        """Numbers and symbols are 'other'."""
        assert is_alphabet("123") == "other"
        assert is_alphabet("...") == "other"
        assert is_alphabet("!@#") == "other"
        assert is_alphabet("   ") == "other"


class TestParseLe:
    """Tests for parse_le language code parsing function."""

    def test_no_source_no_target(self):
        """Defaults to 'en' when no languages specified."""
        assert parse_le("", "") == "en"

    def test_source_english(self):
        """Uses source language 'en' when specified."""
        assert parse_le("en", "") == "en"

    def test_target_japanese(self):
        """Uses target language 'ja' when specified."""
        assert parse_le("", "ja") == "ja"
        assert parse_le("en", "ja") == "en"

    def test_source_french(self):
        """Uses source language 'fr' when specified."""
        assert parse_le("fr", "") == "fr"

    def test_source_korean(self):
        """Uses source language 'ko' when specified."""
        assert parse_le("ko", "") == "ko"

    def test_source_unsupported(self):
        """Falls back to provided language when source is unsupported."""
        assert parse_le("pl", "en") == "en"
        assert parse_le("", "pl") == "en"

    def test_source_and_target_unsupported(self):
        """Falls back to 'en' when both languages are unsupported."""
        assert parse_le("pl", "de") == "en"


class TestGetCnLength:
    """Tests for get_cn_length Chinese character counting function."""

    def test_empty(self):
        """Empty string returns 0."""
        assert get_cn_length("") == 0

    def test_english_only(self):
        """English text returns 0 Chinese characters."""
        assert get_cn_length("hello") == 0

    def test_chinese_only(self):
        """Counts Chinese characters correctly."""
        assert get_cn_length("你好世界") == 4
        assert get_cn_length("书") == 1

    def test_mixed(self):
        """Counts only Chinese characters in mixed text."""
        assert get_cn_length("hello你好") == 2
        assert get_cn_length("Python编程") == 2

    def test_numbers_and_symbols(self):
        """Numbers and symbols are not counted as Chinese."""
        assert get_cn_length("123") == 0
        assert get_cn_length("!@#") == 0


class TestRemoveHtmlTags:
    """Tests for remove_html_tags HTML stripping function."""

    def test_no_tags(self):
        """Text without HTML tags is unchanged."""
        assert remove_html_tags("hello world") == "hello world"

    def test_with_tags(self):
        """Simple tags are removed correctly."""
        assert remove_html_tags("<b>hello</b>") == "hello"
        assert remove_html_tags("<br/>") == ""
        assert remove_html_tags("<div>hello</div>world") == "helloworld"

    def test_nested_tags(self):
        """Nested tags are removed correctly."""
        assert remove_html_tags("<div><b>hello</b></div>") == "hello"

    def test_empty(self):
        """Empty string or empty tags produce empty output."""
        assert remove_html_tags("") == ""
        assert remove_html_tags("<div></div>") == ""

    def test_mixed_content(self):
        """Mixed text and tags are handled correctly."""
        text = "Hello <b>bold</b> and <i>italic</i>."
        assert remove_html_tags(text) == "Hello bold and italic."


class TestGetTerminalSizeColumn:
    """Tests for get_terminal_size_column function."""

    def test_returns_int(self):
        """Returns a positive integer when successful."""
        result = get_terminal_size_column()
        assert isinstance(result, int)
        assert result > 0

    def test_fallback_on_error(self):
        """Falls back to DEFAULT_TERMINAL_SIZE_COLUMN on error."""
        with patch("os.get_terminal_size", side_effect=OSError("no tty")):
            assert get_terminal_size_column() == 20


class TestPrintEqual:
    """Tests for print_equal function with equal sign formatting."""

    @pytest.fixture(autouse=True)
    def setup(self):
        with patch("dict_tiny.util.EIGHT_EQUAL_FORMAT_THRESHOLD", 16):
            yield

    def test_equal_length_ge_16_uses_eight_equal_format(self):
        """Uses eight-equals format when equal_length >= 16."""
        with patch("dict_tiny.util.get_terminal_size_column", return_value=80):
            with patch("dict_tiny.util.normal_title_printer") as mock_print:
                print_equal("book")
                mock_print.assert_called_once()
                assert mock_print.call_args[0][0] == "======== book ========"

    def test_equal_length_eq_16_uses_eight_equal_format(self):
        """Uses eight-equals format when equal_length exactly equals 16."""
        with patch(
            "dict_tiny.util.get_terminal_size_column", return_value=16 + len("book") + 2
        ):
            with patch("dict_tiny.util.normal_title_printer") as mock_print:
                print_equal("book")
                mock_print.assert_called_once()
                assert mock_print.call_args[0][0] == "======== book ========"

    def test_equal_length_le_1_fallsback_to_string(self):
        """Just prints the string when equal_length <= 1."""
        with patch("dict_tiny.util.get_terminal_size_column", return_value=10):
            with patch("dict_tiny.util.normal_title_printer") as mock_print:
                print_equal("a" * 20)
                mock_print.assert_called_once_with("a" * 20)

    def test_equal_length_eq_1_fallsback_to_string(self):
        """Just prints the string when equal_length exactly equals 1."""
        with patch(
            "dict_tiny.util.get_terminal_size_column",
            return_value=1 + len("book") + get_cn_length("book") + 2,
        ):
            with patch("dict_tiny.util.normal_title_printer") as mock_print:
                print_equal("book")
                mock_print.assert_called_once_with("book")

    def test_equal_length_between_2_and_15_uses_balanced_equals(self):
        """Prints balanced equals on both sides for medium length."""
        with patch(
            "dict_tiny.util.get_terminal_size_column", return_value=15 + len("book") + 2
        ):
            with patch("dict_tiny.util.normal_title_printer") as mock_print:
                print_equal("book")
                assert mock_print.call_count == 3
                calls = mock_print.call_args_list
                assert calls[0][0][0] == "=" * 7
                assert calls[0][1]["end"] == ""
                assert calls[1][0][0] == " book "
                assert calls[1][1]["end"] == ""
                assert calls[2][0][0] == "=" * 7

    def test_with_chinese_characters(self):
        """Handles Chinese characters correctly in the calculation."""
        with patch("dict_tiny.util.get_terminal_size_column", return_value=80):
            with patch("dict_tiny.util.normal_title_printer") as mock_print:
                print_equal("测试")
                mock_print.assert_called_once()
                assert "测试" in mock_print.call_args[0][0]


class TestDownloader:
    """Tests for Downloader HTTP utility class."""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.dl = Downloader(retries=1, backoff_factor=0, timeout=5)
        self.dl._session = MagicMock()

    def test_download_success_on_200(self):
        """Returns response object when status code is 200."""
        resp = MagicMock()
        resp.status_code = 200
        self.dl._session.request.return_value = resp
        result = self.dl.download("GET", "http://example.com")
        assert result is resp

    def test_download_returns_none_on_non_200(self):
        """Returns None and prints warning on non-200 status code."""
        resp = MagicMock()
        resp.status_code = 404
        self.dl._session.request.return_value = resp
        with patch("dict_tiny.util.normal_warn_printer") as mock_warn:
            result = self.dl.download("GET", "http://example.com")
        assert result is None
        mock_warn.assert_called_once()

    def test_download_handles_connection_error(self):
        """Handles network connection errors gracefully."""
        self.dl._session.request.side_effect = requests.exceptions.ConnectionError(
            "no network"
        )
        with patch("dict_tiny.util.normal_error_printer") as mock_err:
            result = self.dl.download("GET", "http://example.com")
        assert result is None
        mock_err.assert_called_once()

    def test_download_handles_timeout(self):
        """Handles request timeout errors gracefully."""
        self.dl._session.request.side_effect = requests.exceptions.Timeout()
        with patch("dict_tiny.util.normal_error_printer") as mock_err:
            result = self.dl.download("GET", "http://example.com")
        assert result is None
        mock_err.assert_called_once()

    def test_download_handles_generic_exception(self):
        """Handles unexpected exceptions gracefully."""
        self.dl._session.request.side_effect = RuntimeError("boom")
        with patch("dict_tiny.util.normal_error_printer") as mock_err:
            result = self.dl.download("GET", "http://example.com")
        assert result is None
        mock_err.assert_called_once()

    def test_download_passes_timeout_and_kwargs_to_session(self):
        """Passes timeout and kwargs correctly to session.request."""
        resp = MagicMock()
        resp.status_code = 200
        self.dl._session.request.return_value = resp
        self.dl.download("GET", "http://example.com", timeout=10, headers={"X": "y"})
        args, kwargs = self.dl._session.request.call_args
        assert args[0] == "GET"
        assert args[1] == "http://example.com"
        assert kwargs["timeout"] == 10
        assert kwargs["headers"] == {"X": "y"}

    def test_get_delegates_to_download(self):
        """get() method delegates to download() with 'GET'."""
        with patch.object(self.dl, "download", return_value="ok") as mock_dl:
            assert self.dl.get("http://e.com") == "ok"
            mock_dl.assert_called_with("GET", "http://e.com")

    def test_post_delegates_to_download(self):
        """post() method delegates to download() with 'POST'."""
        with patch.object(self.dl, "download", return_value="ok") as mock_dl:
            assert self.dl.post("http://e.com", json={"a": 1}) == "ok"
            mock_dl.assert_called_with("POST", "http://e.com", json={"a": 1})

    def test_session_is_lazy_initialized(self):
        """Session is created only when first accessed and reused."""
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

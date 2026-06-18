from unittest.mock import MagicMock, patch

import pytest

from dict_tiny.config import YOUDAO_TARGET_LANG_SET
from dict_tiny.errors import TextInputError, YoudaoParamError
from dict_tiny.translators import YoudaoTrans
from dict_tiny.translators.youdao_trans import _get_parser_cls


class TestYoudaoInit:
    """YoudaoTrans initialization and configuration tests."""

    def _make_mock_obj(self, source=None, target=None):
        obj = MagicMock()
        obj.source_language = source
        obj.target_language = target
        return obj

    def test_init_default(self):
        """Default init sets name and leaves languages as None."""
        trans = YoudaoTrans("book", self._make_mock_obj())
        assert trans.name == "youdaodict"
        assert trans.source_language is None
        assert trans.target_language is None

    def test_init_with_target(self):
        """Target language is passed through from mock object."""
        trans = YoudaoTrans("book", self._make_mock_obj(target="ja"))
        assert trans.target_language == "ja"

    def test_init_lowercases_source_language(self):
        """Source language is lowercased on init."""
        trans = YoudaoTrans("book", self._make_mock_obj(source="EN"))
        assert trans.source_language == "en"

    def test_init_unsupported_target(self):
        """Unsupported target language raises YoudaoParamError."""
        with pytest.raises(YoudaoParamError):
            YoudaoTrans("book", self._make_mock_obj(target="pl"))

    def test_init_unsupported_source(self):
        """Unsupported source language raises YoudaoParamError."""
        with pytest.raises(YoudaoParamError):
            YoudaoTrans("book", self._make_mock_obj(source="de"))

    def test_supported_languages(self):
        """Supported languages include en, fr, ja, ko."""
        assert "en" in YOUDAO_TARGET_LANG_SET
        assert "fr" in YOUDAO_TARGET_LANG_SET
        assert "ja" in YOUDAO_TARGET_LANG_SET
        assert "ko" in YOUDAO_TARGET_LANG_SET

    def test_get_web_api_data(self):
        """Web API request data includes query, language, and sign."""
        data = YoudaoTrans.get_web_api_data("book", "en")
        assert "q" in data
        assert data["q"] == "book"
        assert data["le"] == "en"
        assert "sign" in data
        assert data["client"] == "web"
        assert data["keyfrom"] == "webdict"
        assert "t" in data


class TestYoudaoApiDownload:
    """YoudaoTrans.youdao_api_download static method tests."""

    def test_returns_none_on_empty_response(self):
        """Returns None when downloader returns None."""
        with patch("dict_tiny.translators.youdao_trans.downloader") as mock_dl:
            mock_dl.download.return_value = None
            assert YoudaoTrans.youdao_api_download("url", "POST") is None

    def test_returns_json_on_success(self):
        """Returns parsed JSON on successful download."""
        resp = MagicMock()
        resp.json.return_value = {"ec": {}}
        with patch("dict_tiny.translators.youdao_trans.downloader") as mock_dl:
            mock_dl.download.return_value = resp
            result = YoudaoTrans.youdao_api_download("url", "POST", data={"q": "x"})
            assert result == {"ec": {}}

    def test_returns_none_on_json_decode_error(self):
        """Returns None when JSON decoding fails."""
        resp = MagicMock()
        resp.json.side_effect = ValueError("bad json")
        with patch("dict_tiny.translators.youdao_trans.downloader") as mock_dl:
            mock_dl.download.return_value = resp
            assert YoudaoTrans.youdao_api_download("url", "POST") is None


class TestGetParserCls:
    """_get_parser_cls function tests."""

    @pytest.fixture(autouse=True)
    def _clear_parser_cache(self):
        from dict_tiny.translators.youdao_trans import _PARSER_CACHE

        _PARSER_CACHE.clear()

    def test_known_keys(self):
        """All known keys map to the correct parser class."""
        for key, expected_name in [
            ("EC", "ECParser"),
            ("CE", "CEParser"),
            ("FC", "FCParser"),
            ("CF", "CFParser"),
            ("KC", "KCParser"),
            ("CK", "CKParser"),
            ("JC", "JCParser"),
            ("CJ", "CJParser"),
            ("FANYI", "FANYIParser"),
        ]:
            cls = _get_parser_cls(key)
            assert cls.__name__ == expected_name, f"key={key}"

    def test_case_insensitive(self):
        """Key matching is case-insensitive."""
        cls_lower = _get_parser_cls("ec")
        cls_upper = _get_parser_cls("EC")
        assert cls_lower is cls_upper

    def test_unknown_key_raises_value_error(self):
        """Unknown key raises ValueError."""
        with pytest.raises(ValueError):
            _get_parser_cls("ZZ")

    def test_caches_classes(self):
        """Parser classes are cached and reused."""
        cls1 = _get_parser_cls("EC")
        cls2 = _get_parser_cls("EC")
        assert cls1 is cls2


class TestYoudaoDoTranslate:
    """YoudaoTrans.do_translate logic (API response handling and parser dispatch)."""

    @pytest.fixture(autouse=True)
    def _clear_parser_cache(self):
        from dict_tiny.translators.youdao_trans import _PARSER_CACHE

        _PARSER_CACHE.clear()

    def _make_trans(self, text="book", source=None, target=None):
        mock_obj = MagicMock()
        mock_obj.source_language = source
        mock_obj.target_language = target
        mock_obj.more_detail = False
        return YoudaoTrans(text, mock_obj)

    # ── API response handling ──────────────────────────────

    def test_empty_response_returns_false(self):
        """Returns False when API returns no response."""
        trans = self._make_trans()
        with patch.object(YoudaoTrans, "youdao_api_download", return_value=None):
            assert not trans.do_translate("book")

    def test_code_20_raises_text_input_error(self):
        """Code 20 (text too long) raises TextInputError."""
        trans = self._make_trans()
        resp = {"code": 20, "message": "text too long"}
        with patch.object(YoudaoTrans, "youdao_api_download", return_value=resp):
            with pytest.raises(TextInputError):
                trans.do_translate("book")

    def test_main_key_missing_no_fanyi_warns(self):
        """Warns and returns False when no dict data and no fanyi fallback."""
        trans = self._make_trans(source="en")
        resp = {"meta": {"guessLanguage": "en", "le": "ec", "dicts": {}}}
        with patch.object(YoudaoTrans, "youdao_api_download", return_value=resp):
            with patch(
                "dict_tiny.translators.youdao_trans.normal_warn_printer"
            ) as mock_warn:
                result = trans.do_translate("book")
        assert not result
        mock_warn.assert_called_once_with("No results found.")

    # ── Parser dispatch ────────────────────────────────────

    def test_fanyi_fallback(self):
        """Falls back to fanyi parser when the expected dict key is missing."""
        trans = self._make_trans(source="en")
        resp = {
            "meta": {
                "guessLanguage": "en",
                "le": "ec",
                "dicts": {"fanyi": {"tran": "书"}},
            }
        }
        with patch.object(YoudaoTrans, "youdao_api_download", return_value=resp):
            with patch(
                "dict_tiny.translators.YoudaoParser.FANYIParser.FANYIParser"
            ) as MockParser:
                MockParser.return_value.parse.return_value = True
                result = trans.do_translate("book")
        assert result
        MockParser.assert_called_once()
        args, kwargs = MockParser.call_args
        assert args[0] == "fanyi"

    def test_ec_parser(self):
        """English source uses ECParser with key 'ec'."""
        trans = self._make_trans(source="en")
        resp = {
            "meta": {
                "guessLanguage": "en",
                "le": "ec",
                "dicts": {"ec": {"word": {"usphone": "bʊk"}}},
            }
        }
        with patch.object(YoudaoTrans, "youdao_api_download", return_value=resp):
            with patch(
                "dict_tiny.translators.YoudaoParser.ENParser.ECParser"
            ) as MockParser:
                MockParser.return_value.parse.return_value = True
                result = trans.do_translate("book")
        assert result
        args, kwargs = MockParser.call_args
        assert args[0] == "ec"

    def test_ce_parser(self):
        """Chinese-to-English uses CEParser with key 'ce'."""
        trans = self._make_trans(target="en")
        resp = {
            "meta": {
                "guessLanguage": "zh",
                "le": "en",
                "dicts": {"ce": {"word": {"trs": [{"tran": "book"}]}}},
            }
        }
        with patch.object(YoudaoTrans, "youdao_api_download", return_value=resp):
            with patch(
                "dict_tiny.translators.YoudaoParser.ENParser.CEParser"
            ) as MockParser:
                MockParser.return_value.parse.return_value = True
                result = trans.do_translate("测试")
        assert result
        args, _ = MockParser.call_args
        assert args[0] == "ce"

    def test_guess_language_when_no_langs_set(self):
        """Uses guessLanguage from API when no source/target is set."""
        trans = self._make_trans()
        resp = {
            "meta": {
                "guessLanguage": "zh",
                "le": "en",
                "dicts": {"ce": {"word": {}}},
            }
        }
        with patch.object(YoudaoTrans, "youdao_api_download", return_value=resp):
            with patch(
                "dict_tiny.translators.YoudaoParser.ENParser.CEParser"
            ) as MockParser:
                MockParser.return_value.parse.return_value = True
                result = trans.do_translate("测试")
        assert result
        args, _ = MockParser.call_args
        assert args[0] == "ce"

    # ── Parser arguments ───────────────────────────────────

    def test_passes_more_detail_flag(self):
        """Passes more_detail flag to parser constructor."""
        mock_obj = MagicMock()
        mock_obj.source_language = "en"
        mock_obj.target_language = None
        mock_obj.more_detail = True
        trans = YoudaoTrans("book", mock_obj)
        resp = {
            "meta": {"guessLanguage": "en", "le": "ec", "dicts": {"ec": {"word": {}}}}
        }
        with patch.object(YoudaoTrans, "youdao_api_download", return_value=resp):
            with patch(
                "dict_tiny.translators.YoudaoParser.ENParser.ECParser"
            ) as MockParser:
                MockParser.return_value.parse.return_value = True
                trans.do_translate("book")
                args, kwargs = MockParser.call_args
                assert args[3] is True  # print_detail

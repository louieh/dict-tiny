import unittest
from unittest.mock import patch, MagicMock

from dict_tiny.config import (
    YOUDAO_APP_API_BASE_URL,
    YOUDAO_WEB_API_BASE_URL,
    YOUDAO_TARGET_LANG_SET,
)
from dict_tiny.errors import YoudaoParamError, TextInputError
from dict_tiny.translators import YoudaoTrans
from dict_tiny.translators.youdao_trans import _get_parser_cls
from test.util import assert_not_raises


class TestYoudaoInit(unittest.TestCase):
    def _make_mock_obj(self, source=None, target=None):
        obj = MagicMock()
        obj.source_language = source
        obj.target_language = target
        return obj

    def test_init_default(self):
        trans = YoudaoTrans("book", self._make_mock_obj())
        self.assertEqual(trans.name, "youdaodict")
        self.assertIsNone(trans.source_language)
        self.assertIsNone(trans.target_language)

    def test_init_with_target(self):
        trans = YoudaoTrans("book", self._make_mock_obj(target="ja"))
        self.assertEqual(trans.target_language, "ja")

    def test_init_unsupported_target(self):
        with self.assertRaises(YoudaoParamError):
            YoudaoTrans("book", self._make_mock_obj(target="pl"))

    def test_init_unsupported_source(self):
        with self.assertRaises(YoudaoParamError):
            YoudaoTrans("book", self._make_mock_obj(source="de"))

    def test_init_lowercases_source_language(self):
        trans = YoudaoTrans("book", self._make_mock_obj(source="EN"))
        self.assertEqual(trans.source_language, "en")

    def test_supported_languages(self):
        self.assertIn("en", YOUDAO_TARGET_LANG_SET)
        self.assertIn("fr", YOUDAO_TARGET_LANG_SET)
        self.assertIn("ja", YOUDAO_TARGET_LANG_SET)
        self.assertIn("ko", YOUDAO_TARGET_LANG_SET)

    def test_get_web_api_data(self):
        data = YoudaoTrans.get_web_api_data("book", "en")
        self.assertIn("q", data)
        self.assertEqual(data["q"], "book")
        self.assertEqual(data["le"], "en")
        self.assertIn("sign", data)
        self.assertEqual(data["client"], "web")
        self.assertEqual(data["keyfrom"], "webdict")
        self.assertIn("t", data)


class TestYoudaoDoTranslate(unittest.TestCase):
    def setUp(self):
        # _PARSER_CACHE persists across tests and holds real classes,
        # which would bypass parser patches. Clear it before each test.
        from dict_tiny.translators.youdao_trans import _PARSER_CACHE
        _PARSER_CACHE.clear()

    def _make_trans(self, text="book", source=None, target=None):
        mock_obj = MagicMock()
        mock_obj.source_language = source
        mock_obj.target_language = target
        mock_obj.more_detail = False
        return YoudaoTrans(text, mock_obj)

    def test_do_translate_empty_resp_returns_false(self):
        trans = self._make_trans()
        with patch.object(YoudaoTrans, "youdao_api_download", return_value=None):
            self.assertFalse(trans.do_translate("book"))

    def test_do_translate_code_20_raises_text_input_error(self):
        trans = self._make_trans()
        resp = {"code": 20, "message": "text too long"}
        with patch.object(YoudaoTrans, "youdao_api_download", return_value=resp):
            with self.assertRaises(TextInputError):
                trans.do_translate("book")

    def test_do_translate_main_key_missing_no_fanyi_warns(self):
        trans = self._make_trans(source="en")
        resp = {"meta": {"guessLanguage": "en", "le": "ec", "dicts": {}}}
        with patch.object(YoudaoTrans, "youdao_api_download", return_value=resp):
            with patch(
                "dict_tiny.translators.youdao_trans.normal_warn_printer"
            ) as mock_warn:
                result = trans.do_translate("book")
                self.assertFalse(result)
                mock_warn.assert_called_once_with("No results found.")

    def test_do_translate_fanyi_fallback(self):
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
                self.assertTrue(result)
                MockParser.assert_called_once()
                args, kwargs = MockParser.call_args
                self.assertEqual(args[0], "fanyi")

    def test_do_translate_cn_source_uses_c_prefix(self):
        trans = self._make_trans(source="en")  # en target → cn source
        # source=en, target=None: is_cn_source = target != zh → True (target is None)
        # Actually: target is None, so the elif branch is skipped; source is set
        # is_cn_source = (source == zh) → False since source=en
        # main_key = f"{le[0]}c" = "ec"
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
                self.assertTrue(result)
                args, kwargs = MockParser.call_args
                self.assertEqual(args[0], "ec")

    def test_do_translate_cn_source_with_cn_target(self):
        # source=None, target=en → is_cn_source = target != zh → True
        # le="en", main_key = f"c{le[0]}" = "c"+"e" = "ce"
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
                self.assertTrue(result)
                args, _ = MockParser.call_args
                self.assertEqual(args[0], "ce")

    def test_do_translate_guess_language_when_no_langs_set(self):
        trans = self._make_trans()
        # source=None, target=None → is_cn_source = (guess == zh)
        # le="en", main_key = f"c{le[0]}" = "ce"
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
                self.assertTrue(result)
                args, _ = MockParser.call_args
                self.assertEqual(args[0], "ce")

    def test_do_translate_passes_more_detail_flag(self):
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
                self.assertEqual(args[3], True)  # print_detail


class TestYoudaoApiDownload(unittest.TestCase):
    def test_returns_none_on_empty_response(self):
        with patch("dict_tiny.translators.youdao_trans.downloader") as mock_dl:
            mock_dl.download.return_value = None
            self.assertIsNone(YoudaoTrans.youdao_api_download("url", "POST"))

    def test_returns_json_on_success(self):
        resp = MagicMock()
        resp.json.return_value = {"ec": {}}
        with patch("dict_tiny.translators.youdao_trans.downloader") as mock_dl:
            mock_dl.download.return_value = resp
            result = YoudaoTrans.youdao_api_download("url", "POST", data={"q": "x"})
            self.assertEqual(result, {"ec": {}})

    def test_returns_none_on_json_decode_error(self):
        resp = MagicMock()
        resp.json.side_effect = ValueError("bad json")
        with patch("dict_tiny.translators.youdao_trans.downloader") as mock_dl:
            mock_dl.download.return_value = resp
            self.assertIsNone(YoudaoTrans.youdao_api_download("url", "POST"))


class TestGetParserCls(unittest.TestCase):
    def test_known_keys(self):
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
            self.assertEqual(cls.__name__, expected_name, f"key={key}")

    def test_case_insensitive(self):
        cls_lower = _get_parser_cls("ec")
        cls_upper = _get_parser_cls("EC")
        self.assertIs(cls_lower, cls_upper)

    def test_unknown_key_raises_value_error(self):
        with self.assertRaises(ValueError):
            _get_parser_cls("ZZ")

    def test_caches_classes(self):
        cls1 = _get_parser_cls("EC")
        cls2 = _get_parser_cls("EC")
        self.assertIs(cls1, cls2)


class TestYoudaoTransE2E(unittest.TestCase):
    @patch("sys.argv", ["", "-y", "book", "-m"])
    @assert_not_raises
    def test_e2e_ec(self):
        pass

    @patch("sys.argv", ["", "-y", "测试", "-m"])
    @assert_not_raises
    def test_e2e_ce(self):
        pass

    @patch("sys.argv", ["", "-y", "翻訳する", "-m", "--source-language", "ja"])
    @assert_not_raises
    def test_e2e_jc(self):
        pass

    @patch("sys.argv", ["", "-y", "测试", "-m", "--target-language", "ja"])
    @assert_not_raises
    def test_e2e_cj(self):
        pass

    @patch("sys.argv", ["", "-y", "Bonjour", "-m", "--source-language", "fr"])
    @assert_not_raises
    def test_e2e_fc(self):
        pass

    @patch("sys.argv", ["", "-y", "寄存器", "-m", "--target-language", "fr"])
    @assert_not_raises
    def test_e2e_cf(self):
        pass

    @patch("sys.argv", ["", "-y", "컴퓨터", "-m", "--source-language", "ko"])
    @assert_not_raises
    def test_e2e_kc(self):
        pass

    @patch("sys.argv", ["", "-y", "你好", "-m", "--target-language", "ko"])
    @assert_not_raises
    def test_e2e_ck(self):
        pass


if __name__ == "__main__":
    unittest.main()

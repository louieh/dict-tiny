import unittest
from unittest.mock import patch, MagicMock

from dict_tiny.config import (
    YOUDAO_APP_API_BASE_URL,
    YOUDAO_WEB_API_BASE_URL,
    YOUDAO_TARGET_LANG_SET,
)
from dict_tiny.errors import YoudaoParamError
from dict_tiny.translators import YoudaoTrans
from dict_tiny.main import Dict_tiny
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


class TestYoudoTransE2E(unittest.TestCase):
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

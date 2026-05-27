import unittest
from unittest.mock import patch, MagicMock

from dict_tiny.main import run
from dict_tiny.config import ISO639LCodes, MAX_TEXT_LENGTH
from dict_tiny.translators import _ALL_TRANSLATORS
from dict_tiny.errors import TextInputError
from dict_tiny.translators.translator import DefaultTrans


class TestCliInit(unittest.TestCase):
    def test_has_all_translators(self):
        self.assertIn("youdaodict", _ALL_TRANSLATORS)
        self.assertIn("googletranslate", _ALL_TRANSLATORS)

    def test_default_translator_is_youdao(self):
        from dict_tiny.translators import DEFAULT_TRANSLATOR

        self.assertEqual(DEFAULT_TRANSLATOR.__name__, "YoudaoTrans")

    def test_translator_list_matches_config(self):
        self.assertEqual(len(_ALL_TRANSLATORS), 2)

    def test_iso_codes(self):
        self.assertEqual(ISO639LCodes.Chinese.value, "zh")
        self.assertEqual(ISO639LCodes.English.value, "en")
        self.assertEqual(ISO639LCodes.French.value, "fr")
        self.assertEqual(ISO639LCodes.Japanese.value, "ja")
        self.assertEqual(ISO639LCodes.Korean.value, "ko")


class TestTextLengthLimit(unittest.TestCase):
    def setUp(self):
        self.mock_obj = MagicMock()
        self.mock_obj.source_language = None
        self.mock_obj.target_language = None

    def _make_trans(self, cls, text):
        return cls(text, self.mock_obj)

    def test_normal_text_passes(self):
        trans = self._make_trans(DefaultTrans, "hello")
        trans.pre_action("hello")

    def test_exact_limit_passes(self):
        text = "a" * MAX_TEXT_LENGTH
        trans = self._make_trans(DefaultTrans, text)
        trans.pre_action(text)

    def test_oversized_text_raises(self):
        text = "a" * (MAX_TEXT_LENGTH + 1)
        trans = self._make_trans(DefaultTrans, text)
        with self.assertRaises(TextInputError):
            trans.pre_action(text)

    def test_chinese_oversized_text_raises(self):
        text = "中" * (MAX_TEXT_LENGTH + 1)
        trans = self._make_trans(DefaultTrans, text)
        with self.assertRaises(TextInputError):
            trans.pre_action(text)

    def test_google_translate_normal_passes(self):
        trans = self._make_trans(_ALL_TRANSLATORS["googletranslate"], "hello")
        trans.pre_action("hello")

    def test_google_translate_oversized_raises(self):
        trans = self._make_trans(_ALL_TRANSLATORS["googletranslate"], "hello")
        text = "a" * (MAX_TEXT_LENGTH + 1)
        with self.assertRaises(TextInputError):
            trans.pre_action(text)

    def test_youdao_dict_normal_passes(self):
        trans = self._make_trans(_ALL_TRANSLATORS["youdaodict"], "hello")
        trans.pre_action("hello")

    def test_youdao_dict_oversized_raises(self):
        trans = self._make_trans(_ALL_TRANSLATORS["youdaodict"], "hello")
        text = "a" * (MAX_TEXT_LENGTH + 1)
        with self.assertRaises(TextInputError):
            trans.pre_action(text)


class TestCliIntegration(unittest.TestCase):
    @patch("sys.argv", ["", "-y", "book"])
    def test_cli_youdao_translate(self):
        try:
            run()
        except SystemExit:
            pass
        except Exception as e:
            self.fail(f"Unexpected exception: {e}")

    @patch("sys.argv", ["", "-y", "book", "--target-language", "ja"])
    def test_cli_youdao_japanese(self):
        try:
            run()
        except SystemExit:
            pass
        except Exception as e:
            self.fail(f"Unexpected exception: {e}")


if __name__ == "__main__":
    unittest.main()

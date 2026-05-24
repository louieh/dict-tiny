import unittest
from unittest.mock import patch

from dict_tiny.main import run
from dict_tiny.config import ISO639LCodes
from dict_tiny.translators import _ALL_TRANSLATORS


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

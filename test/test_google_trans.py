import unittest
from unittest.mock import patch

from test.util import assert_not_raises


class TestGoogleTrans(unittest.TestCase):
    @patch("sys.argv", ["", "-g", "book"])
    @assert_not_raises
    def test_translate(self):
        pass

    @patch("sys.argv", ["", "-g", "book", "--source-language", "en", "--target-language", "ja"])
    @assert_not_raises
    def test_translate_with_sou_tar_lang(self):
        pass

    @patch("sys.argv", ["", "-g", "book", "--detect-language"])
    @assert_not_raises
    def test_detect_language(self):
        pass

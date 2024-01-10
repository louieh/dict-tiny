import unittest
from unittest.mock import patch

from dict_tiny.translators import YoudaoTrans
from test.util import assert_not_raises


class TestYoudaoTrans(unittest.TestCase):
    @patch("sys.argv", ["", "book"])
    @assert_not_raises
    def test_translate_default(self):
        pass

    @patch("sys.argv", ["", "-y", "book"])
    @assert_not_raises
    def test_trans_en(self):
        pass

    @patch("sys.argv", ["", "-y", "测试"])
    @assert_not_raises
    def test_trans_cn(self):
        pass

    @patch("sys.argv", ["", "-y", "book", "-m"])
    @assert_not_raises
    def test_show_more(self):
        pass

    def test_download(self):
        res = YoudaoTrans.youdao_download("book")
        assert res is not None

    def test_api_download(self):
        res = YoudaoTrans.youdao_api_download("book")
        assert res is not None


if __name__ == '__main__':
    unittest.main()

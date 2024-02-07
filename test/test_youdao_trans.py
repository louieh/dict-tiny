import unittest
from unittest.mock import patch

from dict_tiny.config import YOUDAO_APP_API_BASE_URL, YOUDAO_WEB_API_BASE_URL
from dict_tiny.translators import YoudaoTrans
from test.util import assert_not_raises


class TestYoudaoTrans(unittest.TestCase):

    # legacy - ec
    @patch("sys.argv", ["", "-y", "book", "-m", "--legacy"])
    @assert_not_raises
    def test_trans_legacy_ec(self):
        pass

    # legacy - ce
    @patch("sys.argv", ["", "-y", "测试", "-m", "--legacy"])
    @assert_not_raises
    def test_trans_legacy_ce(self):
        pass

    # legacy - text
    @patch("sys.argv", ["", "-y", "this is a sentence", "-m", "--legacy"])
    @assert_not_raises
    def test_trans_legacy_text(self):
        pass

    # Chinese - English - ec
    @patch("sys.argv", ["", "-y", "book", "-m"])
    @assert_not_raises
    def test_trans_ec(self):
        pass

    # Chinese - English - ce
    @patch("sys.argv", ["", "-y", "测试", "-m"])
    @assert_not_raises
    def test_trans_ce(self):
        pass

    # Chinese - English - text
    @patch("sys.argv", ["", "-y", "this is a sentence", "-m"])
    @assert_not_raises
    def test_trans_en_text(self):
        pass

    # Chinese - Japanese - jc
    @patch("sys.argv", ["", "-y", "翻訳する", "-m", "--target-language", "ja"])
    @assert_not_raises
    def test_trans_jc(self):
        pass

    # Chinese - Japanese - cj
    @patch("sys.argv", ["", "-y", "测试", "-m", "--target-language", "ja"])
    @assert_not_raises
    def test_trans_cj(self):
        pass

    # Chinese - Japanese - text
    @patch("sys.argv", ["", "-y", "これは全文です、わか りますか？", "-m", "--target-language", "ja"])
    @assert_not_raises
    def test_trans_ja_text(self):
        pass

    # Chinese - French - fc
    @patch("sys.argv", ["", "-y", "Bonjour", "-m", "--target-language", "fr"])
    @assert_not_raises
    def test_trans_fc(self):
        pass

    # Chinese - French - cf
    @patch("sys.argv", ["", "-y", "寄存器", "-m", "--target-language", "fr"])
    @assert_not_raises
    def test_trans_cf(self):
        pass

    # Chinese - French - text
    @patch("sys.argv",
           ["", "-y", "Saviez-vous qu’il y a une calculatrice dans un ordinateur", "-m", "--target-language", "fr"])
    @assert_not_raises
    def test_trans_fr(self):
        pass

    # Chinese - Korean - kc
    @patch("sys.argv", ["", "-y", "컴퓨터", "-m", "--target-language", "ko"])
    @assert_not_raises
    def test_trans_kc(self):
        pass

    # Chinese - Korean - ck
    @patch("sys.argv", ["", "-y", "你好", "-m", "--target-language", "ko"])
    @assert_not_raises
    def test_trans_ck(self):
        pass

    # Chinese - Korean - text
    @patch("sys.argv", ["", "-y", "컴퓨터란 무엇인가", "-m", "--target-language", "ko"])
    @assert_not_raises
    def test_trans_ko(self):
        pass

    # target language not supported
    @patch("sys.argv", ["", "-y", "book", "-m", "--target-language", "pl"])
    @assert_not_raises
    def test_trans_target_lang_not_supported(self):
        pass

    # target language error
    @patch("sys.argv", ["", "-y", "book", "-m", "--source-language", "ko", "--target-language", "ja"])
    @assert_not_raises
    def test_trans_target_lang_error(self):
        pass

    @patch("sys.argv", ["", "-y", "book", "-m", "--target-language", "ja"])
    @assert_not_raises
    def test_trans_target_lang_error1(self):
        pass

    # #$% text
    @patch("sys.argv", ["", "-y", "%%%%", "-m", "--target-language", "ja"])
    @assert_not_raises
    def test_trans_error_text(self):
        pass

    @patch("sys.argv", ["", "-y", "%%%%", "-m", "--target-language", "ko"])
    @assert_not_raises
    def test_trans_error_text1(self):
        pass

    def test_download(self):
        res = YoudaoTrans.youdao_download("book")
        assert res is not None

    def test_api_download(self):
        res = YoudaoTrans.youdao_api_download(YOUDAO_APP_API_BASE_URL.format("book"))
        assert res is not None

    def test_web_api_download(self):
        text = "book"
        le = "en"
        data = YoudaoTrans.get_web_api_data(text, le)
        resp = YoudaoTrans.youdao_api_download(YOUDAO_WEB_API_BASE_URL.format(text), "POST", data=data)
        assert resp is not None


if __name__ == '__main__':
    unittest.main()

from unittest.mock import MagicMock, patch

import pytest

from dict_tiny.translators.google_trans import GoogleTrans


class TestGoogleTransIntegration:
    @patch("sys.argv", ["", "-g", "book"])
    def test_translate(self):
        from dict_tiny.main import run

        try:
            run()
        except SystemExit:
            pass
        except Exception as e:
            pytest.fail(f"Unexpected exception: {e}")

    @patch(
        "sys.argv",
        ["", "-g", "book", "--source-language", "en", "--target-language", "ja"],
    )
    def test_translate_with_sou_tar_lang(self):
        from dict_tiny.main import run

        try:
            run()
        except SystemExit:
            pass
        except Exception as e:
            pytest.fail(f"Unexpected exception: {e}")

    @patch("sys.argv", ["", "-g", "book", "--detect-language"])
    def test_detect_language(self):
        from dict_tiny.main import run

        try:
            run()
        except SystemExit:
            pass
        except Exception as e:
            pytest.fail(f"Unexpected exception: {e}")


class TestGoogleTransUnit:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.mock_obj = MagicMock()
        self.mock_obj.source_language = None
        self.mock_obj.target_language = None
        self.mock_obj.wordbook = None
        self.mock_obj.detect_language = False
        self.trans = GoogleTrans("hello", self.mock_obj)

    def test_do_translate_detect_language_returns_false(self):
        self.mock_obj.detect_language = True
        with patch.object(self.trans, "detect_language", return_value=True):
            result = self.trans.do_translate("hello")
        assert not result

    def test_do_translate_empty_response(self):
        with patch("dict_tiny.translators.google_trans.downloader") as mock_dl:
            mock_dl.post.return_value = None
            result = self.trans.do_translate("hello")
        assert not result

    def test_do_translate_invalid_json(self):
        resp = MagicMock()
        resp.json.side_effect = ValueError("bad json")
        resp.text = "not json"
        with patch("dict_tiny.translators.google_trans.downloader") as mock_dl:
            mock_dl.post.return_value = resp
            result = self.trans.do_translate("hello")
        assert not result

    def test_do_translate_non_200(self):
        resp = MagicMock()
        resp.json.return_value = {"code": 500, "msg": "server error"}
        with patch("dict_tiny.translators.google_trans.downloader") as mock_dl:
            mock_dl.post.return_value = resp
            result = self.trans.do_translate("hello")
        assert not result

    def test_do_translate_success(self):
        resp = MagicMock()
        resp.json.return_value = {
            "code": 200,
            "data": {"translatedText": "你好", "detectedSourceLanguage": "en"},
        }
        with patch("dict_tiny.translators.google_trans.downloader") as mock_dl:
            mock_dl.post.return_value = resp
            result = self.trans.do_translate("hello")
        assert result

    def test_detect_language_empty_response(self):
        with patch("dict_tiny.translators.google_trans.downloader") as mock_dl:
            mock_dl.post.return_value = None
            result = self.trans.detect_language("hello")
        assert not result

    def test_detect_language_invalid_json(self):
        resp = MagicMock()
        resp.json.side_effect = ValueError("bad json")
        resp.text = "not json"
        with patch("dict_tiny.translators.google_trans.downloader") as mock_dl:
            mock_dl.post.return_value = resp
            result = self.trans.detect_language("hello")
        assert not result

    def test_detect_language_non_200(self):
        resp = MagicMock()
        resp.json.return_value = {"code": 500, "msg": "server error"}
        with patch("dict_tiny.translators.google_trans.downloader") as mock_dl:
            mock_dl.post.return_value = resp
            result = self.trans.detect_language("hello")
        assert not result

    def test_detect_language_success(self):
        resp = MagicMock()
        resp.json.return_value = {
            "code": 200,
            "data": {"detectedLanguage": "en"},
        }
        with patch("dict_tiny.translators.google_trans.downloader") as mock_dl:
            mock_dl.post.return_value = resp
            result = self.trans.detect_language("hello")
        assert result

import unittest

from dict_tiny.util import downloader
from dict_tiny.config import (
    YOUDAO_SUGGESTION_API_BASE_URL,
    YOUDAO_WEB_API_BASE_URL,
    YOUDAO_SUGGEST_API_FAKE_HEADER,
    SUGGESTION_NUM,
)
from dict_tiny.translators.youdao_trans import YoudaoTrans


class TestYoudaoAPIs(unittest.TestCase):
    def test_suggestion_api(self):
        url = YOUDAO_SUGGESTION_API_BASE_URL.format(SUGGESTION_NUM, "en", "book")
        resp = downloader.get(url, headers=YOUDAO_SUGGEST_API_FAKE_HEADER)
        self.assertIsNotNone(resp)
        self.assertEqual(resp.json()["result"]["code"], 200)

    def test_web_api(self):
        text = "book"
        data = YoudaoTrans.get_web_api_data(text, "en")
        resp = YoudaoTrans.youdao_api_download(
            YOUDAO_WEB_API_BASE_URL, "POST", data=data
        )
        self.assertIsNotNone(resp)
        self.assertIn("ec", resp)


if __name__ == "__main__":
    unittest.main()

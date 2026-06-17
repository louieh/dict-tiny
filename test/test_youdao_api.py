from dict_tiny.config import (
    SUGGESTION_NUM,
    YOUDAO_SUGGEST_API_FAKE_HEADER,
    YOUDAO_SUGGESTION_API_BASE_URL,
    YOUDAO_WEB_API_BASE_URL,
)
from dict_tiny.translators.youdao_trans import YoudaoTrans
from dict_tiny.util import downloader


class TestYoudaoAPIs:
    def test_suggestion_api(self):
        url = YOUDAO_SUGGESTION_API_BASE_URL.format(SUGGESTION_NUM, "en", "book")
        resp = downloader.get(url, headers=YOUDAO_SUGGEST_API_FAKE_HEADER)
        assert resp is not None
        assert resp.json()["result"]["code"] == 200

    def test_web_api(self):
        text = "book"
        data = YoudaoTrans.get_web_api_data(text, "en")
        resp = YoudaoTrans.youdao_api_download(
            YOUDAO_WEB_API_BASE_URL, "POST", data=data
        )
        assert resp is not None
        assert "ec" in resp

from enum import Enum

SEPARATOR = ">>> {} <<<"

TIMEOUT = 5
RETRY = 3
BACKOFF_FACTOR = 1
MAX_TEXT_LENGTH = 3000
MAX_ENTRIES = 10000


class ISO639LCodes(Enum):
    Chinese = "zh"
    English = "en"
    French = "fr"
    Japanese = "ja"
    Korean = "ko"


DICT_TINY_SOURCE_LAN_ENV_NAME = "DICT_TINY_SOURCE_LAN"
DICT_TINY_TARGET_LAN_ENV_NAME = "DICT_TINY_TARGET_LAN"
DICT_TINY_DEFAULT_TRANS_ENV_NAME = "DICT_TINY_DEFAULT_TRANS"

# YOUDAO
YOUDAO_NAME = "youdaodict"
YOUDAO_DISPLAY = "YoudaoDict"
YOUDAO_WEB_FAKE_HEADER = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7,ja;q=0.6",
    "Host": "youdao.com",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36",
}
YOUDAO_API_FAKE_HEADER = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7",
    "Host": "dict.youdao.com",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
}
YOUDAO_SUGGEST_API_FAKE_HEADER = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7",
    "Host": "dict.youdao.com",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
}
SUGGESTION_NUM = 8
YOUDAO_WEB_BASE_URL = "http://youdao.com/w/{}"
YOUDAO_WEB_API_BASE_URL = "https://dict.youdao.com/jsonapi_s?doctype=json&jsonversion=4"
YOUDAO_APP_API_BASE_URL = "http://dict.youdao.com/jsonapi?q={}"
YOUDAO_SUGGESTION_API_BASE_URL = (
    "https://dict.youdao.com/suggest?num={}&ver=3.0&doctype=json&cache=false&le={}&q={}"
)
DEFAULT_LE = ISO639LCodes.English.value
YOUDAO_TARGET_LANG_SET = {"en", "fr", "ja", "ko"}

# GOOGLE TRANS
GOOGLE_NAME = "googletranslate"
GOOGLE_DISPLAY = "GoogleTranslate"
GOOGLE_TRANS_API_BASE_URL = "https://tinydict-translateapi.appspot.com/goog/{}"
GOOGLE_TRANS_API_HEADER = {
    "X-Dict-Tiny-Secret-Token": "e14d348d268dca4731a99b7055e07921"
}

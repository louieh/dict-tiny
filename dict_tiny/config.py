import os
from enum import Enum


class ISO639LCodes(Enum):
    Chinese = "zh"
    English = "en"
    French = "fr"
    Japanese = "ja"
    Korean = "ko"


DEFAULT_TARGET_LANGUAGE = ISO639LCodes.Chinese.value

# YOUDAO
YOUDAO_NAME = "Youdao Dict"
YOUDAO_WEB_FAKE_HEADER = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7,ja;q=0.6',
    'Host': 'youdao.com',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36',
}
YOUDAO_API_FAKE_HEADER = {
    "Host": "dict.youdao.com",
    "Accept": "*/*",
    "User-Agent": "YoudaoDict/139 CFNetwork/901.1 Darwin/17.6.0 (x86_64)",
    "Accept-Language": "en-us",
    "Accept-Encoding": "gzip",
    "Connection": "keep-alive",
}

YOUDAO_SUGGEST_API_FAKE_HEADER = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Host": "dict.youdao.com",
    "User-Agent": "YoudaoDict/139 CFNetwork/901.1 Darwin/17.6.0 (x86_64)",
}
TIMEOUT = 3
SUGGESTION_NUM = 8
YOUDAO_WEB_BASE_URL = "http://youdao.com/w/{}"
YOUDAO_WEB_API_BASE_URL = "https://dict.youdao.com/jsonapi_s?doctype=json&jsonversion=4"
YOUDAO_APP_API_BASE_URL = "http://dict.youdao.com/jsonapi?q={}"
YOUDAO_SUGGESTION_API_BASE_URL = "https://dict.youdao.com/suggest?num={}&ver=3.0&doctype=json&cache=false&le={}&q={}"
DEFAULT_LE = ISO639LCodes.English.value

# GOOGLE TRANS
GOOGLE_NAME = "Google Translate"
GOOGLE_TRANS_API_BASE_URL = "https://tinydict-translateapi.appspot.com/goog/{}"

# DEEPL TRANS
DEEPL_NAME = "DeepL Translate"
DEEPL_TRANS_API_BASE_URL = "https://tinydict-translateapi.appspot.com/deep/{}"

# GEMINI
GEMINI_NAME = "Gemini"
DEFAULT_GEMINI_MODEL = "gemini-pro"
GEMINI_API_KEY_ENV_NAME = "GEMINI_API_KEY"


class GEMINI_MODEL(Enum):
    gemini_pro = "gemini-pro"
    gemini_pro_vision = "gemini-pro-vision"


# OPENAI
OPENAI_NAME = "OpenAI"
DEFAULT_OPENAI_MODEL = "gpt-3.5-turbo"
OPENAI_API_KEY_ENV_NAME = "OPENAI_API_KEY"

OPENAI_MODEL = {
    "gpt-4-1106-preview": {
        "context_window": 128000
    },
    "gpt-4-vision-preview": {
        "context_window": 128000
    },
    "gpt-4": {
        "context_window": 8192
    },
    "gpt-4-32k": {
        "context_window": 32768
    },
    "gpt-4-0613": {
        "context_window": 8192
    },
    "gpt-4-32k-0613": {
        "context_window": 32768
    },
    "gpt-3.5-turbo-1106": {
        "context_window": 16385
    },
    "gpt-3.5-turbo": {
        "context_window": 4096
    },
    "gpt-3.5-turbo-16k": {
        "context_window": 16385
    },
    "gpt-3.5-turbo-instruct": {
        "context_window": 4096
    }
}

# SYSTEM
try:
    TERMINAL_SIZE_COLUMN = os.get_terminal_size().columns
except:
    TERMINAL_SIZE_COLUMN = 20
SEPARATOR = ">>> {} <<<"

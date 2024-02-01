import os
from enum import Enum

# SYSTEM
try:
    TERMINAL_SIZE_COLUMN = os.get_terminal_size().columns
except:
    TERMINAL_SIZE_COLUMN = 20
SEPARATOR = ">>> {} <<<"

TIMEOUT = 5
RETRY = 3
BACKOFF_FACTOR = 1
MAX_TEXT_LENGTH = 3000


class ISO639LCodes(Enum):
    Chinese = "zh"
    English = "en"
    French = "fr"
    Japanese = "ja"
    Korean = "ko"


DEFAULT_TARGET_LANGUAGE = ISO639LCodes.Chinese.value
DICT_TINY_TARGET_LAN_ENV_NAME = "DICT_TINY_TARGET_LAN"
DICT_TINY_DEFAULT_TRANS_ENV_NAME = "DICT_TINY_DEFAULT_TRANS"

# YOUDAO
YOUDAO_NAME = "YoudaoDict"
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
SUGGESTION_NUM = 8
YOUDAO_WEB_BASE_URL = "http://youdao.com/w/{}"
YOUDAO_WEB_API_BASE_URL = "https://dict.youdao.com/jsonapi_s?doctype=json&jsonversion=4"
YOUDAO_APP_API_BASE_URL = "http://dict.youdao.com/jsonapi?q={}"
YOUDAO_SUGGESTION_API_BASE_URL = "https://dict.youdao.com/suggest?num={}&ver=3.0&doctype=json&cache=false&le={}&q={}"
DEFAULT_LE = ISO639LCodes.English.value

# GOOGLE TRANS
GOOGLE_NAME = "GoogleTranslate"
GOOGLE_TRANS_API_BASE_URL = "https://tinydict-translateapi.appspot.com/goog/{}"
GOOGLE_TRANS_API_HEADER = {
    "X-Dict-Tiny-Secret-Token": "e14d348d268dca4731a99b7055e07921"
}

# DEEPL TRANS
DEEPL_NAME = "DeepLTranslate"
DEEPL_TRANS_API_BASE_URL = "https://tinydict-translateapi.appspot.com/deep/{}"

# GEMINI
GEMINI_NAME = "Gemini"
GEMINI_MODEL_ENV_NAME = "DICT_TINY_GEMINI_MODEL"
GEMINI_API_KEY_ENV_NAME = "DICT_TINY_GEMINI_API_KEY"


class GEMINI_MODEL(Enum):
    gemini_pro = "gemini-pro"
    gemini_pro_vision = "gemini-pro-vision"


DEFAULT_GEMINI_MODEL = GEMINI_MODEL.gemini_pro.value

GEMINI_MODEL_DETAIL = {
    GEMINI_MODEL.gemini_pro.value: {
        "input_token_limit": 30720,
        "output_token_limit": 2048
    },
    GEMINI_MODEL.gemini_pro_vision.value: {
        "input_token_limit": 12288,
        "output_token_limit": 4096
    }
}

# OPENAI
OPENAI_NAME = "OpenAI"
OPENAI_TIMEOUT = 20
OPENAI_MODEL_ENV_NAME = "DICT_TINY_OPENAI_MODEL"
OPENAI_API_KEY_ENV_NAME = "DICT_TINY_OPENAI_API_KEY"


class OPENAI_MODEL(Enum):
    gpt_4_0125_preview = "gpt-4-0125-preview"
    gpt_4_turbo_preview = "gpt-4-turbo-preview"
    gpt_4_1106_preview = "gpt-4-1106-preview"
    # gpt_4_vision_preview = "gpt-4-vision-preview"
    gpt_4 = "gpt-4"
    gpt_4_32k = "gpt-4-32k"
    gpt_4_0613 = "gpt-4-0613"
    gpt_4_32k_0613 = "gpt-4-32k-0613"
    gpt_35_turbo_1106 = "gpt-3.5-turbo-1106"
    gpt_35_turbo = "gpt-3.5-turbo"
    gpt_35_turbo_16k = "gpt-3.5-turbo-16k"
    gpt_35_turbo_instruct = "gpt-3.5-turbo-instruct"


DEFAULT_OPENAI_MODEL = OPENAI_MODEL.gpt_35_turbo.value

OPENAI_MODEL_DETAIL = {
    OPENAI_MODEL.gpt_4_0125_preview.value: {
        "context_window": 128000
    },
    OPENAI_MODEL.gpt_4_turbo_preview.value: {
        "context_window": 128000
    },
    OPENAI_MODEL.gpt_4_1106_preview.value: {
        "context_window": 128000
    },
    # OPENAI_MODEL.gpt_4_vision_preview.value: {
    #     "context_window": 128000
    # },
    OPENAI_MODEL.gpt_4.value: {
        "context_window": 8192
    },
    OPENAI_MODEL.gpt_4_32k.value: {
        "context_window": 32768
    },
    OPENAI_MODEL.gpt_4_0613.value: {
        "context_window": 8192
    },
    OPENAI_MODEL.gpt_4_32k_0613.value: {
        "context_window": 32768
    },
    OPENAI_MODEL.gpt_35_turbo_1106.value: {
        "context_window": 16385
    },
    OPENAI_MODEL.gpt_35_turbo.value: {
        "context_window": 4096
    },
    OPENAI_MODEL.gpt_35_turbo_16k.value: {
        "context_window": 16385
    },
    OPENAI_MODEL.gpt_35_turbo_instruct.value: {
        "context_window": 4096
    }
}

# LLM
TOKEN_USAGE_FACTOR = 0.9
SUMMARY_PROMPT = "Please summarize the current session history content in order to reduce the length of historical tokens, retain key information, and remove redundant information."

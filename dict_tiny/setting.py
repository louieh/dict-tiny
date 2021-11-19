import os

# YOUDAO
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

TIME_OUT = 5

YOUDAO_BASE_URL = "http://youdao.com/w/{}"

# GOOGLE TRANS
GOOGLE_TRANS_API_BASE_URL = "https://tinydict-translateapi.appspot.com/goog/{}"

# DEEPL TRANS
DEEPL_TRANS_API_BASE_URL = "https://tinydict-translateapi.appspot.com/deep/{}"

# SYSTEM
try:
    TERMINAL_SIZE_COLUMN = os.get_terminal_size().columns
except:
    TERMINAL_SIZE_COLUMN = 20

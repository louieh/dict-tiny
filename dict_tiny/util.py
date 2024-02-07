import re
from collections import defaultdict
from functools import partial

import requests
from plumbum import colors
from requests import Session
from requests.adapters import HTTPAdapter, Retry

from dict_tiny.config import TIMEOUT, DEFAULT_LE, ISO639LCodes, RETRY, BACKOFF_FACTOR, TERMINAL_SIZE_COLUMN


class Downloader:

    def __init__(self):
        self.retries = Retry(total=RETRY, backoff_factor=BACKOFF_FACTOR)
        self.session = Session()  # reuse tcp connection
        self.session.mount("http://", HTTPAdapter(max_retries=self.retries))
        self.session.mount("https://", HTTPAdapter(max_retries=self.retries))

    def download(self, method, url, **kwargs) -> requests.Response:
        """
        normal download method
        :param method: request method
        :param url: url to download
        :param kwargs: additional arguments: headers, data, json
        :return: Response object
        """
        try:
            resp = self.session.request(method, url, timeout=TIMEOUT, **kwargs)
            if resp.status_code == 200: return resp
            normal_warn_printer(f"Download error, status code: {resp.status_code} resp: {resp.text}")
        except requests.exceptions.ConnectionError as e:
            normal_error_printer(f"Connection Error. Please check your network. error: {e}")
        except requests.exceptions.Timeout as e:
            normal_error_printer("Time out. Please try again.")
        except Exception as e:
            # print(f"download error: {str(e)}")
            normal_error_printer("Something went wrong. Please try again.")


downloader = Downloader()


def is_alphabet(word):
    # TODO refactor
    """
    return the word is English or Chinese
    :param word:
    :return:
    """
    if not word: return 'other'
    is_alphabet = defaultdict(int)
    word = word.replace(' ', '')
    for each_letter in word:
        if each_letter >= '\u4e00' and each_letter <= '\u9fff':
            is_alphabet['zh'] += 1
        # elif word >= '\u0030' and word <= '\u0039':
        #     return 'num'
        elif (each_letter >= '\u0041' and each_letter <= '\u005a') or (
                each_letter >= '\u0061' and each_letter <= '\u007a'):
            is_alphabet['en'] += 1
        else:
            is_alphabet['other'] += 1

    is_alphabet['en'] /= 4

    for len_type, num in is_alphabet.items():
        if num >= sum(is_alphabet.values()) * 0.7:
            return len_type
    return 'other'


def parse_le(source: str, target: str, trans=False) -> str:
    """
    Determine the le value in youdao based on the input target language or source language. Default le is en.
    If trans is False which means the auto-completion section, the value of le depends on the source language, same as
    target language is None.
    If the source language is None, the value of le can only depend on the target language.
    @param source: source language
    @param target: target language
    @param trans: translate or suggestion
    @return le
    """
    st_set = {source, target}
    le_set = {
        ISO639LCodes.English.value,
        ISO639LCodes.French.value,
        ISO639LCodes.Korean.value,
        ISO639LCodes.Japanese.value
    }
    if not target or not trans:
        return DEFAULT_LE if source not in le_set else source
    if not source:
        return DEFAULT_LE if target not in le_set else target
    le = st_set.intersection(le_set)
    if ISO639LCodes.Chinese.value in st_set and le:
        return le.pop()
    return DEFAULT_LE


def normal_color_printer(text, color=None, **kwargs):
    if color is None:
        print(text, **kwargs)
    else:
        print(color | text, **kwargs)


normal_separator_printer = partial(normal_color_printer, color=colors.bold & colors.yellow)
normal_info_printer = partial(normal_color_printer, color=None)
normal_title_printer = partial(normal_color_printer, color=colors.green)
normal_warn_printer = partial(normal_color_printer, color=colors.yellow)
normal_error_printer = partial(normal_color_printer, color=colors.red)


def print_equal(string):
    """
    print equal symbol base on terminal size
    :param string:
    :return:
    """

    equal_length = TERMINAL_SIZE_COLUMN - len(string) - get_cn_length(string) - 2
    if equal_length >= 16:  # 8 equal each side
        normal_title_printer("======== %s ========" % string)
    elif equal_length <= 1:
        normal_title_printer(string)
    else:
        normal_title_printer("=" * int(equal_length / 2), end="")
        normal_title_printer(" %s " % string, end="")
        normal_title_printer("=" * (equal_length - int(equal_length / 2) - 1))


def get_cn_length(string):
    """
    return the number of chinese char
    :param string:
    :return:
    """

    count = 0
    for each in string:
        if '\u4e00' <= each <= '\u9fff':
            count += 1
    return count


def remove_html_tags(text):
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

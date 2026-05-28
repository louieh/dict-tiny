import os
import re
import sys
from pathlib import Path

from dict_tiny.config import (
    TIMEOUT,
    DEFAULT_LE,
    ISO639LCodes,
    RETRY,
    BACKOFF_FACTOR,
)


def get_terminal_size_column():
    import os

    try:
        return os.get_terminal_size().columns
    except Exception:
        return 20


class Downloader:

    def __init__(
        self,
        retries: int = RETRY,
        backoff_factor: float = BACKOFF_FACTOR,
        timeout: int = TIMEOUT,
    ):
        self._retries = retries
        self._backoff_factor = backoff_factor
        self.timeout = timeout
        self._session = None

    @property
    def session(self):
        if self._session is None:
            from requests import Session
            from requests.adapters import HTTPAdapter, Retry

            retry = Retry(total=self._retries, backoff_factor=self._backoff_factor)
            self._session = Session()
            self._session.mount("http://", HTTPAdapter(max_retries=retry))
            self._session.mount("https://", HTTPAdapter(max_retries=retry))
        return self._session

    def download(self, method: str, url: str, **kwargs):
        """
        Send a request and return the response on success.

        On failure, prints a user-friendly error and returns None.
        """
        try:
            import requests

            resp = self.session.request(
                method, url, timeout=kwargs.pop("timeout", self.timeout), **kwargs
            )
            if resp.status_code == 200:
                return resp
            normal_warn_printer(f"Download error, status code: {resp.status_code}")
        except requests.exceptions.ConnectionError as e:
            normal_error_printer(f"Connection error. Please check your network. ({e})")
        except requests.exceptions.Timeout:
            normal_error_printer("Request timed out. Please try again.")
        except Exception as e:
            normal_error_printer(f"Something went wrong: {e}")

    def get(self, url: str, **kwargs):
        return self.download("GET", url, **kwargs)

    def post(self, url: str, **kwargs):
        return self.download("POST", url, **kwargs)


downloader = Downloader()


def is_alphabet(word):
    """
    return the word is English or Chinese
    :param word:
    :return:
    """
    if not word:
        return "other"
    cn = sum(1 for c in word if "\u4e00" <= c <= "\u9fff")
    en = len(re.findall(r"[a-zA-Z]+(?:['-][a-zA-Z]+)*", word))

    if cn == 0 and en == 0:
        return "other"
    if cn == 0:
        return "en"
    if en == 0:
        return "zh"
    return "zh" if cn >= en else "en"


def parse_le(source: str, target: str) -> str:
    le_set = {
        ISO639LCodes.English.value,
        ISO639LCodes.French.value,
        ISO639LCodes.Korean.value,
        ISO639LCodes.Japanese.value,
    }
    for lang in (source, target):
        if lang and lang in le_set:
            return lang
    return DEFAULT_LE


def normal_color_printer(text, color=None, **kwargs):
    if color is None:
        print(text, **kwargs)
    else:
        from plumbum import colors

        print(color | text, **kwargs)


def normal_separator_printer(text, **kwargs):
    from plumbum import colors

    normal_color_printer(text, color=colors.bold & colors.yellow, **kwargs)


def normal_info_printer(text, **kwargs):
    normal_color_printer(text, color=None, **kwargs)


def normal_title_printer(text, **kwargs):
    from plumbum import colors

    normal_color_printer(text, color=colors.green, **kwargs)


def normal_warn_printer(text, **kwargs):
    from plumbum import colors

    normal_color_printer(text, color=colors.yellow, **kwargs)


def normal_error_printer(text, **kwargs):
    from plumbum import colors

    normal_color_printer(text, color=colors.red, **kwargs)


def print_equal(string):
    """
    print equal symbol base on terminal size
    :param string:
    :return:
    """

    equal_length = get_terminal_size_column() - len(string) - get_cn_length(string) - 2
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
        if "\u4e00" <= each <= "\u9fff":
            count += 1
    return count


def remove_html_tags(text):
    clean = re.compile("<.*?>")
    return re.sub(clean, "", text)


def get_data_dir():
    if sys.platform == "win32":
        base = os.environ.get("LOCALAPPDATA", str(Path.home() / "AppData" / "Local"))
    elif sys.platform == "darwin":
        base = str(Path.home() / "Library" / "Application Support")
    else:
        base = os.environ.get("XDG_DATA_HOME", str(Path.home() / ".local" / "share"))
    return Path(base) / "dict-tiny"

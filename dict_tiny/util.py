from collections import defaultdict

import requests
from plumbum import colors

from dict_tiny.config import TIMEOUT


def is_alphabet(word):
    """
    return the word is English or Chinese
    :param word:
    :return:
    """
    is_alphabet = defaultdict(int)
    word = word.replace(' ', '')
    for each_letter in word:
        if each_letter >= '\u4e00' and each_letter <= '\u9fff':
            is_alphabet['cn'] += 1
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


def downloader(method, url, **kwargs) -> requests.Response:
    """
    normal download method
    :param method: request method
    :param url: url to download
    :param kwargs: additional arguments: headers, data, json
    :return: Response object
    """
    try:
        resp = requests.request(method, url, timeout=TIMEOUT, **kwargs)
        if resp.status_code == 200: return resp
        normal_color_printer(f"Download error, status code: {resp.status_code}", colors.yellow)
    except requests.exceptions.ConnectionError as e:
        normal_color_printer("[Error!] Time out. Please try again.", colors.red)
    except Exception as e:
        normal_color_printer("[Error!] Something went wrong. Please try again.", colors.red)


def normal_color_printer(text, color=None, **kwargs):
    if color is None:
        print(text, **kwargs)
    else:
        print(color | text, **kwargs)

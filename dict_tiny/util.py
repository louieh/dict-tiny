from collections import defaultdict
from lxml import html
import requests
from plumbum import colors
from dict_tiny.setting import TIME_OUT


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


def downloader(url, header):
    """
    :param url: url need to be downloaded
    :param header: fake header
    :return:
    """
    try:
        result = requests.get(url, headers=header, timeout=TIME_OUT)
        result_selector = html.etree.HTML(result.text)
        resp_code = result.status_code
    except requests.exceptions.ConnectionError as e:
        print(colors.red | "[Error!] Time out.")
        print("<%s>" % e)
        result_selector = None
        resp_code = None
    return result_selector, resp_code


def downloader_plain(url, header):
    """
    plain download. Do not make the resp to selector
    :param url:
    :param header:
    :return:
    """
    try:
        return requests.get(url, headers=header).text
    except:
        return None

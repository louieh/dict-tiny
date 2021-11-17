from collections import defaultdict
from lxml import html
import requests
from plumbum import colors


def is_alphabet(word):
    """
    return the word is English or Chinese
    :param word:
    :return:
    """
    is_alphabet = defaultdict(int)
    word = word.replace(' ', '')
    word_len = len(word)
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

    if is_alphabet['cn'] / word_len >= 0.8:
        return 'cn'
    elif is_alphabet['en'] / word_len >= 0.8:
        return 'en'
    else:
        return 'other'


def downloader(url, header):
    """
    :param url: url need to be downloaded
    :param header: fake header
    :return:
    """
    try:
        result = requests.get(url, headers=header)
        result_selector = html.etree.HTML(result.text)
        resp_code = result.status_code
    except requests.exceptions.ConnectionError as e:
        print(colors.red | "[Error!] Unable to download webpage.")
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

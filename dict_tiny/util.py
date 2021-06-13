from lxml import html
import requests
from plumbum import colors


def is_alphabet(word):
    """
    return the word is English or Chinese
    :param word:
    :return:
    """
    is_alphabet = {
        'cn': 0,
        'en': 0,
    }
    for each_letter in word:
        if each_letter >= '\u4e00' and each_letter <= '\u9fff':
            is_alphabet['cn'] += 1
        # elif word >= '\u0030' and word <= '\u0039':
        #     return 'num'
        elif (each_letter >= '\u0041' and each_letter <= '\u005a') or (
                each_letter >= '\u0061' and each_letter <= '\u007a'):
            is_alphabet['en'] += 1

    if is_alphabet['cn'] / len(word) >= 0.8:
        return 'cn'
    elif is_alphabet['en'] == len(word):
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

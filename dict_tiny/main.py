#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import sys
import os
import requests
from lxml import html
from plumbum import cli
from plumbum import colors
import pyperclip
import json

from dict_tiny.en_detail.get_detail import get_data, print_basetrans, print_detailtrans, print_detailtrans_collins
from dict_tiny import version

APP_DESC = """
tiny translator
"""
APP_NAME = version.name
APP_VERSION = version.__version__


# TODO Command line interaction
# TODO 奇怪的问题：真的没有找到解释还是网络问题

class Dict_tiny(cli.Application):
    PROGNAME = colors.green | APP_NAME
    VERSION = colors.yellow | APP_VERSION
    DESCRIPTION = version.DESCRIPTION
    COLOR_GROUPS = {"Switches": colors.green}

    target_language = cli.SwitchAttr("--target-language", str, excludes=["-m", "--more"], group="google_translate_api",
                                     envname="DICT_TINY_TARGET_LAN",
                                     help="Target language for Google Translate api.")
    source_language = cli.SwitchAttr("--source-language", str, excludes=["-m", "--more"], group="google_translate_api",
                                     help="Source language for Google Translate api.")
    if_google_api = cli.Flag("-g", excludes=["-m", "--more"], group="google_translate_api",
                             help="Using Google Translate api.")
    moredetail = cli.Flag(["-m", "--more"], excludes=["-g", "--target-language", "--source-language"],
                          help="If given, more detail translation will be shown. You need to give a word or -c.")

    IF_STOP = False  # If return directly at main function
    targetWord = ""  # record the word and it must be translatable word
    try:
        TERMINAL_SIZE_COLUMN = os.get_terminal_size().columns
    except:
        TERMINAL_SIZE_COLUMN = 20

    FAKE_HEADER = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7,ja;q=0.6',
        'Host': 'youdao.com',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36',
    }

    Base_url = "https://tinydict-translateapi.appspot.com/{}"

    def trans_en(self, word):
        """
        English_Chinese
        """

        count = 2  # there are two chinere characters
        data, status_code = self.downloader(word)  # result will be deleted
        if data is None:  # no internet
            return
        phone = data.xpath('.//div[@id="phrsListTab"]/h2//span[@class="pronounce"]//text()')
        content = data.xpath('.//div[@id="phrsListTab"]/div[@class="trans-container"]/ul/li//text()')
        print(colors.green | word, end='  ')
        for each_phone in phone:
            if each_phone:
                print(colors.green | each_phone.strip(), end="")
                count += len(each_phone.strip())
        print("\n", end="")

        # print =
        if len(word) + count + 2 > self.TERMINAL_SIZE_COLUMN:
            for i in range(self.TERMINAL_SIZE_COLUMN - 1):
                print(colors.green | "=", end="")
            print(colors.green | "=")
        else:
            for i in range(len(word) + count + 1):
                print(colors.green | "=", end="")
            print(colors.green | "=")

        if len(content) >= 1:
            for each_result in content:
                print(each_result)
            self.targetWord = word + "_en"
        else:
            if status_code == 200:  # no translation
                print(colors.yellow | "Did not find an explanation for this word.")
            else:  # 403?
                print(colors.yellow | "The translation of this word cannot be found at this time. Please try again.")
        return

    def show_more(self, word, type, row=3, printall=True):
        """
        English_Chinese_detail
        """

        data_base = get_data(word)
        if not data_base:
            print(
                colors.yellow | "The detail translation of this word cannot be found at this time. Please try again later.")
            return
        # print_basetrans(data_base)
        if type == 'cn':
            print_detailtrans(data_base, type, row, printall)  # two parameters：row=3, printall=False
        elif type == 'en':
            print_detailtrans_collins(data_base)
        # print("[Error!] Cannot get detail translation.")
        return

    def trans_cn(self, word):
        """
        Chinese_English
        """

        count = len(word)
        data, status_code = self.downloader(word)  # result will be deleted
        if data is None:  # no internet
            return
        phone = data.xpath('.//div[@id="phrsListTab"]/h2/span[@class="phonetic"]//text()')
        content = data.xpath('.//div[@id="phrsListTab"]/div[@class="trans-container"]/ul//span//text()')
        for i in range(len(content)):
            if "\n" in content[i]:
                content[i] = "\n"
            if ";" in content[i]:
                content[i] = content[i].replace(" ", "")
                content[i - 1] = content[i + 1] = ""
        content = "".join(content[:-1])

        print(colors.green | word, end='  ')
        for each_phone in phone:
            if each_phone:
                print(colors.green | each_phone.strip(), end="")
                count += len(each_phone.strip())
        print("\n", end="")

        # print =
        if len(word) + count + 2 > self.TERMINAL_SIZE_COLUMN:
            for i in range(self.TERMINAL_SIZE_COLUMN - 1):
                print(colors.green | "=", end="")
            print(colors.green | "=")
        else:
            for i in range(len(word) + count + 1):
                print(colors.green | "=", end="")
            print(colors.green | "=")

        if content:
            print(content)
            self.targetWord = word + "_cn"
        else:
            if status_code == 200:  # no translation
                print(colors.yellow | "Did not find an explanation for this word.")
            else:  # 403?
                print(colors.yellow | "The translation of this word cannot be found at this time. Please try again.")
        return

    def downloader(self, word):
        request_url = "http://youdao.com/w/%s" % word
        try:
            result = requests.get(request_url, headers=self.FAKE_HEADER)
            result_selector = html.etree.HTML(result.text)
            resp_code = result.status_code
        except requests.exceptions.ConnectionError as e:
            print(colors.red | "[Error!] Unable to download webpage.")
            print("<%s>" % e)
            result_selector = None
            resp_code = None
        return result_selector, resp_code

    def is_alphabet(self, word):
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

    @cli.switch("--detect-language", str)
    def detect_language(self, text):
        """
        detect language
        """
        self.IF_STOP = True
        try:
            resp = requests.post(self.Base_url.format("detect_language"), json={
                "text": text
            })
            for k, v in resp.json().items():
                print("{}: {}".format(k, v))
        except Exception as e:
            print(str(e))

    @cli.switch(["-c", "--clipboard"])
    def trans_clipboard(self):
        """
        Translate the content of the current clipboard if it`s an English word or a Chinese word.
        No parameter required.
        """

        try:
            clipboard_data = pyperclip.paste().strip().replace('\n', '')
        except:
            self.IF_STOP = True
            print(colors.red | "[Error!] Cannot get clipboard content.")
            return

        if clipboard_data:
            if self.if_google_api or len(clipboard_data.split(" ")) > 1:
                self.google_trans(clipboard_data)
            else:
                self.you_dao(clipboard_data)
        else:
            self.IS_TRANS = True
            print(colors.yellow | "There is no content in the clipboard.")
        return

    def you_dao(self, word):
        self.IF_STOP = True

        if self.is_alphabet(word) == 'en':
            self.trans_en(word)
        elif self.is_alphabet(word) == 'cn':
            self.trans_cn(word)
        else:
            print(colors.red | "[Error!] The content is not an English word or a Chinese word.")
        return

    def google_trans(self, text):
        self.IF_STOP = True
        try:
            resp = requests.post(self.Base_url.format("translate"), json={
                "text": text,
                "target": self.target_language,
                "source": self.source_language,
            })
            for k, v in resp.json().items():
                print("{}: {}".format(k, v))
        except Exception as e:
            print(str(e))

    def main(self, *word):
        if not word and self.IF_STOP == False:
            self.help()
        elif word and self.IF_STOP == False:
            if self.if_google_api or len(word) > 1 or (len(word) == 1 and len(word[0]) > 4 and self.is_alphabet(word[0]) == 'cn'):
                self.google_trans(" ".join(word))
            else:
                self.you_dao(word[0])

        # -m
        # targetWord == 1 ==> IS_TRANS == 1
        # IS_TRANS == 1 <> targetWord == 1
        if self.targetWord and self.moredetail:
            self.targetWord, type = self.targetWord.split("_")
            self.show_more(self.targetWord, type)


if __name__ == "__main__":
    Dict_tiny()

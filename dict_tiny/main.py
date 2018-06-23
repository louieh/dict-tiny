#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sys
import requests
from lxml import html
import re
import argparse
from plumbum import cli
import pyperclip

from dict_tiny.en_detail.get_detail import get_data, print_basetrans, print_detailtrans

APP_DESC = """
tiny dictionary
"""


# TODO color
# TODO Command line interaction
# TODO phone

class Dict_tiny(cli.Application):
    PROGNAME = "Dict-tiny"
    VERSION = "0.2.1"
    DESCRIPTION = "A tiny command-line dictionary that scrapes youdao.com. Just for fun."

    moredetail = cli.Flag(["-m", "--more"],
                          help="If given, more detail translation will be shown. You need to give a word or -c.")
    # more = cli.switch(["m","more"], help="Getting more detial.")
    IS_TRANS = 0  # Has this word been translated
    targetWord = ""  # record the word and it must be translatable word

    FAKE_HEADER = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7,ja;q=0.6',
        'Host': 'youdao.com',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36',
    }

    def trans_en(self, word):
        """
        English_Chinese
        """

        data = self.downloader(word)
        content = data.xpath('.//div[@id="phrsListTab"]/div[@class="trans-container"]/ul/li//text()')
        print(word)
        for i in range(len(word) - 1):
            print("=", end="")
        print("==")
        if len(content) >= 1:
            for each_result in content:
                print(each_result)
            self.targetWord = word + "_en"
        else:
            print("The translation of this word cannot be found at this time. Please try again.")
        return

    def show_more(self, word, type, row=3, printall=True):
        """
        English_Chinese_detail
        """

        data_base = get_data(word)
        if not data_base:
            print("The detail translation of this word cannot be found at this time. Please try again later.")
            return
            # print_basetrans(data_base)
        print_detailtrans(data_base, type, row, printall)  # two parameters：row=3, printall=False
        # print("[Error!] Cannot get detail translation.")
        return

    def trans_cn(self, word):
        """
        Chinese_English
        """

        data = self.downloader(word)
        content = data.xpath('.//div[@id="phrsListTab"]/div[@class="trans-container"]/ul//span//text()')
        for i in range(len(content)):
            if "\n" in content[i]:
                content[i] = "\n"
            if ";" in content[i]:
                content[i] = content[i].replace(" ", "")
                content[i - 1] = content[i + 1] = ""
        content = "".join(content[:-1])
        if content:
            print(word)
            for i in range(len(word) - 1):
                print("=", end="")
            print("==")
            print(content)
            self.targetWord = word + "_cn"
        else:
            print("The translation of this word cannot be found at this time. Please try again.")
        return

    @cli.switch(["-c", "--clipboard"])
    def trans_clipboard(self):
        """
        Translate the content of the current clipboard if it`s an English word or a Chinese word.
        No parameter required.
        """

        try:
            clipboard_data = pyperclip.paste().strip().replace('\n', '')
        except:
            self.IS_TRANS = 1
            print("[Error!] Cannot get clipboard content.")
            return

        if clipboard_data:
            self.main_(clipboard_data)
        else:
            self.IS_TRANS = 1
            print("There is no content in the clipboard.")
        return

    def downloader(self, word):
        request_url = "http://youdao.com/w/%s" % word
        result = requests.get(request_url, headers=self.FAKE_HEADER).text
        result_selector = html.etree.HTML(result)
        return result_selector

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

        if is_alphabet['cn'] == len(word):
            return 'cn'
        elif is_alphabet['en'] == len(word):
            return 'en'
        else:
            return 'other'

    def main_(self, word):

        self.IS_TRANS = 1

        if self.is_alphabet(word) == 'en':
            self.trans_en(word)
        elif self.is_alphabet(word) == 'cn':
            self.trans_cn(word)
        else:
            print("[Error!] This is not an English word or a Chinese word.")
        return

    def main(self, *word):
        if not word and not self.IS_TRANS:
            self.help()
        elif word and not self.IS_TRANS:
            if len(word) > 1:
                print(
                    "Oops! You may want to translate a sentence, but I can only choose the first word as the target word.")
            word = word[0]
            self.main_(word)

        # -m
        # targetWord == 1 ==> IS_TRANS == 1
        # IS_TRANS == 1 <> targetWord == 1
        if self.targetWord and self.moredetail:
            self.targetWord, type = self.targetWord.split("_")
            self.show_more(self.targetWord, type)
        return


if __name__ == "__main__":
    Dict_tiny()

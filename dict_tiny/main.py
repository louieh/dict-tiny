#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sys
import requests
from lxml import html
import re
import argparse
from plumbum import cli
import pyperclip

from en_detail.get_detail import get_data, print_basetrans, print_detailtrans

APP_DESC = """
tiny dictionary
"""


class Dict_tiny(cli.Application):
    PROGNAME = "Dict-tiny"
    VERSION = "0.1.1"
    DESCRIPTION = "A tiny command-line dictionary that scrapes youdao.com. Just for fun."

    # verbose = cli.Flag(["v", "verbose"], help="If given, I will be very talkative")
    # more = cli.switch(["m","more"], help="Getting more detial.")
    IS_TRANS = 0

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
        self.IS_TRANS = 1

        data = self.downloader(word)
        content = data.xpath('.//div[@id="phrsListTab"]/div[@class="trans-container"]/ul/li//text()')
        print(word)
        for i in range(len(word) - 1):
            print("=", end="")
        print("==")
        if len(content) >= 1:
            for each_result in content:
                print(each_result)
            return
        else:
            print("No translation found for this word.")
            return

    @cli.switch(["-m", "--more"], str)
    def trans_en_more(self, word, row=3, printall=True):
        """
        English_Chinese_detail
        """
        self.IS_TRANS = 1

        if self.is_alphabet(word) != 'en':
            print("[Error!] You should enter an English word.")
            return

        data_base = get_data(word)
        print_basetrans(data_base)
        print_detailtrans(data_base, row, printall)  # two parameters：row=3, printall=False
        return

    def trans_cn(self, word):
        """
        Chinese_English
        """
        self.IS_TRANS = 1

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
            return
        else:
            print("No translation found for this word.")
            return

    @cli.switch(["-c", "--clipboard"])
    def trans_clipboard(self):
        """
        Translate the content of the current clipboard if it`s an English word or a Chinese word.
        No parameter required.
        """
        self.IS_TRANS = 1

        try:
            clipboard_data = pyperclip.paste().strip().replace('\n', '')
        except:
            print("[Error!] Cannot get clipboard content.")
            return

        if clipboard_data:
            self.main_(clipboard_data)
        else:
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
        # if self.verbose:
        #     print("")
        return


if __name__ == "__main__":
    Dict_tiny()

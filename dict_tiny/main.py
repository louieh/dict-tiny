#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import sys
import os
from plumbum import cli
from plumbum import colors
import pyperclip
import json

from dict_tiny.sources.googleTrans import detect_language, google_trans
from dict_tiny.sources.youdao import youdao_trans, show_more
from dict_tiny.util import is_alphabet
import version

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
    more_detail = cli.Flag(["-m", "--more"],
                           excludes=["-g", "--target-language", "--source-language", "--detect-language"],
                           help="If given, more detail Youdao translation will be shown. You need to give a word or switch -c.")

    IF_STOP = False  # If return directly at main function
    clipBoardContent = None  # Record the word in clipboard
    needDetailWord = None  # Record the word which need Youdao detail

    @cli.switch("--detect-language", str)
    def detect_language(self, text):
        self.IF_STOP = True
        detect_language(text)

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
            self.clipBoardContent = clipboard_data.split(" ")
        else:
            print(colors.yellow | "There is no content in the clipboard.")

    def main(self, *word):
        # stop, return directly
        if self.IF_STOP: return

        wordFinal = word or self.clipBoardContent  # word has high priority
        # no word, print help
        if not wordFinal:
            self.help()
        # wordFinal, do trans
        else:
            if self.if_google_api or len(wordFinal) > 1 or (
                    len(wordFinal) == 1 and len(wordFinal[0]) > 4 and is_alphabet(wordFinal[0]) == 'cn'):
                google_trans(" ".join(wordFinal), self.target_language, self.source_language)
                return
            else:
                self.needDetailWord = youdao_trans(wordFinal[0])

        # -m, print detail
        if self.needDetailWord and self.more_detail:
            self.needDetailWord, type = self.needDetailWord.split("_")
            show_more(self.needDetailWord, type)


if __name__ == "__main__":
    Dict_tiny()

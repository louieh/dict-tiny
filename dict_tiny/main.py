#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from plumbum import cli
from plumbum import colors
import pyperclip

from dict_tiny.sources.google_trans import detect_language, google_trans
from dict_tiny.sources.youdao import youdao_trans, show_more
from dict_tiny.sources.deepl_trans import deepl_trans
from dict_tiny.util import is_alphabet
from dict_tiny import version

APP_DESC = """
tiny command-line translator
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

    target_language = cli.SwitchAttr("--target-language", str, excludes=["-m", "--more"],
                                     envname="DICT_TINY_TARGET_LAN",
                                     help="what language you want to translate into")
    source_language = cli.SwitchAttr("--source-language", str, excludes=["-m", "--more"],
                                     help="what language you want to translate")
    if_google_api = cli.Flag(["-g", "--google"], excludes=["-m", "--more", "-d"], group="google_translate_api",
                             help="Using Google Translation API.")
    if_deep_api = cli.Flag(["-d", "--deepl"], excludes=["-m", "--more", "-g"], group="deepl_translate_api",
                           help="Using DeepL Translator API.")
    # if_youdao_api = cli.Flag(["-y", "--youdao"], excludes=["-g", "-d"], group="youdao_translate_api",
    #                          help="Youdao translate")
    more_detail = cli.Flag(["-m", "--more"], group="youdao_translate_api",
                           excludes=["-g", "-d", "--deepl", "--google", "--target-language", "--source-language",
                                     "--detect-language"],
                           help="If given, more detail Youdao translation will be shown. You need to give a word or switch -c.")

    IF_STOP = False  # If return directly at main function
    clipBoardContent = None  # Record the word in clipboard
    needDetailWord = None  # Record the word which need Youdao detail

    @cli.switch("--detect-language", str)
    def detect_language(self, text):
        """
        Detect the language of the given text.
        """
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
            if_sentence = True if len(wordFinal) > 1 or len(wordFinal) == 1 and len(wordFinal[0]) > 4 and is_alphabet(
                wordFinal[0]) == 'cn' else False
            wordFinal = " ".join(wordFinal)
            if_english = True if is_alphabet(wordFinal) == 'en' else False

            if not self.target_language:
                if self.if_google_api:
                    self.target_language = "zh" if if_english else "en"
                else:
                    self.target_language = "ZH" if if_english else "EN-US"

            if self.if_deep_api:
                deepl_trans(wordFinal, self.target_language)
            elif self.if_google_api:
                google_trans(wordFinal, self.target_language, self.source_language)
            else:
                if if_sentence:
                    deepl_trans(wordFinal, self.target_language)
                    return
                self.needDetailWord = youdao_trans(wordFinal)

        # -m, print detail
        if self.needDetailWord and self.more_detail:
            self.needDetailWord, type = self.needDetailWord.split("_")
            show_more(self.needDetailWord, type)


if __name__ == "__main__":
    Dict_tiny()

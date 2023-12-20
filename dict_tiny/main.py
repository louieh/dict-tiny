#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from plumbum import cli
from plumbum import colors

from dict_tiny.util import is_alphabet
from dict_tiny import version

from dict_tiny.translators import _ALL_TRANSLATORS, DEFAULT_TRANSLATOR

APP_DESC = """
tiny command-line translator
"""
APP_NAME = version.name
APP_VERSION = version.__version__


class Dict_tiny(cli.Application):
    PROGNAME = colors.green | APP_NAME
    VERSION = colors.yellow | APP_VERSION
    DESCRIPTION = version.DESCRIPTION
    COLOR_GROUPS = {
        "Switches": colors.yellow,
        "Google translate": colors.green,
        "Youdao dict": colors.green
    }

    stop = False  # whether return directly in main
    clipBoardContent = None  # Record the word in clipboard

    def main(self, *words):
        if self.stop: return
        text = words or self.clipBoardContent  # word has high priority
        if not text:
            self.help()
            return
        text = " ".join(text)

        if_english = True if is_alphabet(text) == 'en' else False
        if not self.target_language and self.use_googletrans:
            self.target_language = "zh" if if_english else "en"

        trans_objs = [translator.trans_obj_getter(text, self) for translator in _ALL_TRANSLATORS]
        if not any(trans_objs):
            trans_objs.append(DEFAULT_TRANSLATOR(text, self))
        for trans_obj in trans_objs:
            if trans_obj is None: continue
            trans_obj.translate()


if __name__ == "__main__":
    for translator in _ALL_TRANSLATORS:
        translator.attr_setter(Dict_tiny)
    Dict_tiny()

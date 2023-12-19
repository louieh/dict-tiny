#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from plumbum import cli
from plumbum import colors

from dict_tiny.util import is_alphabet
from dict_tiny import version

from dict_tiny.translators import _ALL_TRANSLATORS

APP_DESC = """
tiny command-line translator
"""
APP_NAME = version.name
APP_VERSION = version.__version__


# TODO 奇怪的问题：真的没有找到解释还是网络问题
# TODO 调整样式
# TODO 调整帮助信息
# TODO 扩大 youdao 语言范围
# TODO 修改 readme

class Dict_tiny(cli.Application):
    PROGNAME = colors.green | APP_NAME
    VERSION = colors.yellow | APP_VERSION
    DESCRIPTION = version.DESCRIPTION
    COLOR_GROUPS = {"Switches": colors.green}

    stop = False  # whether return  directly in main
    clipBoardContent = None  # Record the word in clipboard

    def main(self, *word):
        if self.stop: return
        text = " ".join(word) or self.clipBoardContent  # word has high priority
        if not text:
            self.help()
            return

        if_english = True if is_alphabet(text) == 'en' else False
        if not self.target_language and self.use_googletrans:
            self.target_language = "zh" if if_english else "en"

        trans_objs = [translator.trans_obj_getter(text, self) for translator in _ALL_TRANSLATORS]
        if not any(trans_objs): self.help()
        for trans_obj in trans_objs:
            if trans_obj is None: continue
            trans_obj.translate()


if __name__ == "__main__":
    for translator in _ALL_TRANSLATORS:
        translator.attr_setter(Dict_tiny)
    Dict_tiny()

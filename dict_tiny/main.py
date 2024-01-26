#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from plumbum import cli
from plumbum import colors

from dict_tiny import version
from dict_tiny.errors import CustomException
from dict_tiny.translators import _ALL_TRANSLATORS, DEFAULT_TRANSLATOR
from dict_tiny.util import normal_warn_printer, normal_error_printer

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
        "Youdao dict": colors.green,
        "Gemini": colors.green
    }

    stop = False  # whether return directly in main
    clipBoardContent = None  # Record the word in clipboard

    def main(self, *words):
        if self.stop: return
        text = words or self.clipBoardContent  # word has high priority
        if not text and not self.interactive and not hasattr(self, "img_path"):
            self.help()
            return

        text = " ".join(text) if text else ""
        try:
            trans_objs = [trans_obj for translator in _ALL_TRANSLATORS if
                          (trans_obj := translator.trans_obj_getter(text, self)) is not None]
            if not trans_objs:
                trans_objs.append(DEFAULT_TRANSLATOR(text, self))
        except CustomException as e:
            normal_error_printer(e.message)
            return

        # enter interactive mode
        if self.interactive:
            if len(trans_objs) > 1:
                normal_warn_printer("You can only enter the interactive mode of one translator")
                return
            trans_objs[0].interactive()
            return

        # not interactive mode
        for trans_obj in trans_objs:
            if trans_obj is None: continue
            trans_obj.translate()


def run():
    for translator in _ALL_TRANSLATORS:
        translator.attr_setter(Dict_tiny)
    Dict_tiny()


if __name__ == "__main__":
    run()

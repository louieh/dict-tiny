#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from plumbum import cli
from plumbum import colors

from dict_tiny import version
from dict_tiny.config import YOUDAO_NAME, GOOGLE_NAME, GEMINI_NAME, OPENAI_NAME
from dict_tiny.errors import CustomException
from dict_tiny.translators import _ALL_TRANSLATORS, DEFAULT_TRANSLATOR
from dict_tiny.util import normal_warn_printer, normal_error_printer

APP_DESC = version.DESCRIPTION
APP_NAME = version.name
APP_VERSION = version.__version__


class Dict_tiny(cli.Application):
    PROGNAME = colors.green | APP_NAME
    VERSION = colors.yellow | APP_VERSION
    DESCRIPTION = version.DESCRIPTION
    COLOR_GROUPS = {
        "Switches": colors.yellow,
        YOUDAO_NAME: colors.green,
        GOOGLE_NAME: colors.green,
        GEMINI_NAME: colors.green,
        OPENAI_NAME: colors.green,
        "LLM": colors.green,
    }

    stop = False  # whether return directly in main
    clipBoardContent = None  # Record the word in clipboard

    def main(self, *words):
        if self.stop: return
        text = words or self.clipBoardContent  # word has high priority
        if not text and not self.interactive and not getattr(self, "img_path", None):
            self.help()
            return

        text = " ".join(text) if text else ""
        try:
            trans_objs = [trans_obj for translator in _ALL_TRANSLATORS.values() if
                          (trans_obj := translator.trans_obj_getter(text, self)) is not None]
            if not trans_objs:
                default_translator = DEFAULT_TRANSLATOR
                if self.default_translator and self.default_translator.lower() in _ALL_TRANSLATORS:
                    default_translator = _ALL_TRANSLATORS[self.default_translator.lower()]
                trans_objs.append(default_translator(text, self))
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
    for translator in _ALL_TRANSLATORS.values():
        translator.attr_setter(Dict_tiny)
    Dict_tiny()


if __name__ == "__main__":
    run()

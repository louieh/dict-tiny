#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os

from plumbum import cli, colors

from dict_tiny import version
from dict_tiny.config import (
    DICT_TINY_DEFAULT_TRANS_ENV_NAME,
    GOOGLE_DISPLAY,
    YOUDAO_DISPLAY,
)
from dict_tiny.errors import CustomException
from dict_tiny.translators import _ALL_TRANSLATORS, DEFAULT_TRANSLATOR
from dict_tiny.util import normal_error_printer, normal_warn_printer
from dict_tiny.wordbook import WordBook
from dict_tiny.wordbook_cli import WordBookApp


class Dict_tiny(cli.Application):
    PROGNAME = colors.green | version.name
    VERSION = colors.yellow | version.__version__
    DESCRIPTION = version.DESCRIPTION
    COLOR_GROUPS = {
        "Switches": colors.yellow,
        YOUDAO_DISPLAY: colors.green,
        GOOGLE_DISPLAY: colors.green,
    }

    stop = False  # whether return directly in main
    clipBoardContent = None  # Record the word in clipboard
    wordbook = None  # WordBook instance, set lazily

    record = cli.Flag("--record", help="Record query to word book")
    no_record = cli.Flag("--no-record", help="Skip recording this query")

    def get_wordbook(self):
        if self.wordbook is not None and self.wordbook._conn is not None:
            return self.wordbook
        try:
            self.wordbook = WordBook()
            return self.wordbook
        except Exception as e:
            normal_error_printer(f"Failed to init wordbook: {e}")
            return None

    def main(self, *words):
        if self.nested_command:
            return

        if self.stop:
            return

        # ── recording decision ──────────────────────────────
        if self.record:
            should_record = True
        elif self.no_record:
            should_record = False
        elif WordBook.db_exists():
            wb = self.get_wordbook()
            should_record = wb.get_default_record() if wb else False
        else:
            should_record = False

        if should_record and self.wordbook is None:
            self.get_wordbook()
        # ─────────────────────────────────────────────────────

        text = words or self.clipBoardContent  # word has high priority
        if not text and not self.interactive:
            self.help()
            return

        text = " ".join(text) if text else ""
        try:
            trans_objs = [
                trans_obj
                for translator in _ALL_TRANSLATORS.values()
                if (trans_obj := translator.trans_obj_getter(text, self)) is not None
            ]
            if not trans_objs:
                default_translator = DEFAULT_TRANSLATOR
                default_trans_name_env = os.getenv(DICT_TINY_DEFAULT_TRANS_ENV_NAME)
                if (
                    default_trans_name_env
                    and default_trans_name_env.lower() in _ALL_TRANSLATORS
                ):
                    default_translator = _ALL_TRANSLATORS[
                        default_trans_name_env.lower()
                    ]
                trans_objs.append(default_translator(text, self))
        except CustomException as e:
            normal_error_printer(e.message)
            return
        except Exception as e:
            normal_error_printer(f"translator init error: {e}")
            return

        # enter interactive mode
        if self.interactive:
            if len(trans_objs) > 1:
                normal_warn_printer(
                    "You can only enter the interactive mode of one translator"
                )
                return
            trans_objs[0].interactive()
            if self.wordbook:
                self.wordbook.close()
            return

        # not interactive mode
        for trans_obj in trans_objs:
            if trans_obj is None:
                continue
            trans_obj.translate()

        if self.wordbook:
            self.wordbook.close()


Dict_tiny.subcommand("wb")(WordBookApp)


def run():
    for translator in _ALL_TRANSLATORS.values():
        translator.attr_setter(Dict_tiny)
    Dict_tiny()


if __name__ == "__main__":
    run()

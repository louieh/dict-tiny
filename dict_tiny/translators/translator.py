import pyperclip
from plumbum import cli
from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style

from dict_tiny.completer import YoudaoCompleter
from dict_tiny.config import SEPARATOR, TERMINAL_SIZE_COLUMN, DEFAULT_TARGET_LANGUAGE, DICT_TINY_TARGET_LAN_ENV_NAME, \
    DICT_TINY_DEFAULT_TRANS_ENV_NAME
from dict_tiny.errors import CustomException
from dict_tiny.util import normal_error_printer, normal_warn_printer, normal_separator_printer, normal_info_printer, \
    normal_title_printer, parse_le


class DefaultTrans(object):
    def __init__(self, text, dict_tiny_obj):
        self.text = text
        self.dict_tiny_obj = dict_tiny_obj
        self.source_language = dict_tiny_obj.source_language
        self.target_language = dict_tiny_obj.target_language or DEFAULT_TARGET_LANGUAGE

    @classmethod
    def attr_setter(cls, dict_tiny_cls):

        dict_tiny_cls.interactive = cli.Flag(["-i", "--interactive"],
                                             help="Interactive mode")
        dict_tiny_cls.source_language = cli.SwitchAttr("--source-language",
                                                       str,
                                                       help="what language you want to translate")
        dict_tiny_cls.target_language = cli.SwitchAttr("--target-language",
                                                       str,
                                                       envname=DICT_TINY_TARGET_LAN_ENV_NAME,
                                                       help="what language you want to translate into")
        dict_tiny_cls.default_translator = cli.SwitchAttr("--default-translator",
                                                          str,
                                                          envname=DICT_TINY_DEFAULT_TRANS_ENV_NAME,
                                                          help="set default translator")

        @cli.switch(["-c", "--clipboard"])
        def trans_clipboard(self):
            """
            Use the contents of the clipboard.
            """

            try:
                clipboard_data = pyperclip.paste().strip().replace('\n', '')
            except Exception as e:
                self.stop = True
                normal_error_printer("[Error!] Cannot get clipboard content.")
                return

            if clipboard_data:
                self.clipBoardContent = clipboard_data.split(" ")
            else:
                normal_warn_printer("There is no content in the clipboard.")

        dict_tiny_cls.trans_clipboard = trans_clipboard

    @classmethod
    def trans_obj_getter(cls, text, dict_tiny_obj):
        flag = f"use_{cls.__name__.lower()}"  # use_googletrans
        if not getattr(dict_tiny_obj, flag, False): return
        return cls(text, dict_tiny_obj)

    def pre_action(self, text):
        pass

    def print_separator(self):
        normal_separator_printer(SEPARATOR.format(self.name))

    def print_input(self, text):
        normal_title_printer(text)
        length = len(text) + 2
        if length > TERMINAL_SIZE_COLUMN:
            length = TERMINAL_SIZE_COLUMN - 1
        normal_title_printer("=" * length)

    def do_translate(self, text):
        raise NotImplementedError

    def extra_action(self, text):
        pass

    def translate(self):
        # 1. pre action (set default source or target language)
        # 2. translate (fetch data)
        # 3. print separator
        # 4. print user input
        # 5. print translation
        # 6. extra action (get more detail translation)
        try:
            self.print_separator()
            self.pre_action(self.text)
            self.print_input(self.text)
            self.do_translate(self.text)
            self.extra_action(self.text)
        except CustomException as e:
            normal_error_printer(e.message)
        except Exception as e:
            # print(f"error: {e}")
            pass

    def get_prompt_session(self):
        style = Style.from_dict({
            # completion
            'completion-menu.completion': 'bg:#008888 #ffffff',
            'completion-menu.completion.current': 'bg:#00aaaa #000000',
            'scrollbar.background': 'bg:#88aaaa',
            'scrollbar.button': 'bg:#222222',

            # User input (default text).
            '': '#ffbe54',

            # Prompt.
            'prompt_name': '#00aa00',
            'prompt_sign': '#60db94',
        })

        normal_separator_printer(SEPARATOR.format(f"{self.name} interactive mode"))
        normal_info_printer("Use Ctrl-D (i.e. EOF) to exit")

        suggest_le = parse_le(self.source_language, self.target_language)
        session = PromptSession(completer=YoudaoCompleter(suggest_le),
                                style=style,
                                complete_while_typing=False,
                                complete_in_thread=True)
        return session

    def interactive_loop(self, session):
        message = [
            ('class:prompt_name', self.name),
            ('class:prompt_sign', ' > '),
        ]
        while True:
            try:
                text = session.prompt(message)
                if not text: continue
            except KeyboardInterrupt:
                normal_info_printer("Use Ctrl-D (i.e. EOF) to exit")
                continue  # Control-C pressed. Try again.
            except EOFError:
                break  # Control-D pressed.
            else:
                try:
                    self.pre_action(text)
                    self.print_input(text)
                    self.do_translate(text)
                except CustomException as e:
                    normal_error_printer(e.message)
                except Exception as e:
                    # print(f"error: {e}")
                    continue
        print('GoodBye!')

    def interactive(self):
        session = self.get_prompt_session()
        self.interactive_loop(session)

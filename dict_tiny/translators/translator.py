from plumbum import cli
import pyperclip

from dict_tiny.util import normal_error_printer, normal_warn_printer


class DefaultTrans(object):
    def __init__(self, text, dict_tiny_obj):
        self.text = text
        self.dict_tiny_obj = dict_tiny_obj

    @classmethod
    def attr_setter(cls, dict_tiny_cls):

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

    def translate(self):
        raise NotImplementedError

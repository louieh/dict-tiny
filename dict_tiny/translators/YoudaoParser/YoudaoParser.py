import json
import re
from hashlib import md5
from lxml import html

from dict_tiny.config import YOUDAO_API_FAKE_HEADER, YOUDAO_WEB_BASE_URL, YOUDAO_WEB_FAKE_HEADER, TERMINAL_SIZE_COLUMN, \
    ISO639LCodes
from dict_tiny.util import downloader, normal_title_printer, normal_warn_printer


class YoudaoParser(object):
    def __init__(self, data, console, print_detail=False):
        self.data = data
        self.print_detail = print_detail
        self.console = console

    def parse_main_key(self):
        meta_dict = self.data.get("meta", {})
        guess_language = meta_dict.get("guess_language")
        le = meta_dict.get("le")
        if guess_language == ISO639LCodes.Chinese.value:
            self.main_key = f"c{le[0]}"
        else:
            self.main_key = f"{le[0]}c"
        dicts = meta_dict.get("dicts")
        if self.main_key not in dicts:
            if "fanyi" in dicts:
                self.main_key = "fanyi"
            else:
                normal_warn_printer("cannot find result currently")
                return

    def parse(self):
        self.parse_main_key()
        self.parse_phone()
        self.parse_simple_content()
        if self.print_detail:
            self.parse_detail_content()

    def parse_phone(self):
        pass

    def parse_simple_content(self):
        pass

    def parse_detail_content(self):
        pass

    @staticmethod
    def remove_html_tags(text):
        clean = re.compile('<.*?>')
        return re.sub(clean, '', text)


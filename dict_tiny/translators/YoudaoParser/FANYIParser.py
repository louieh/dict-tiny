from dict_tiny.translators.YoudaoParser.YoudaoParser import YoudaoParser
from dict_tiny.util import normal_info_printer


class FANYIParser(YoudaoParser):
    def parse_simple_content(self, word_data):
        basic_value = self.data.get(self.main_key)
        tran = basic_value.get("tran")
        normal_info_printer(tran)

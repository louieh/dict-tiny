from dict_tiny.util import normal_warn_printer


class YoudaoParser(object):
    def __init__(self, main_key, data, console, print_detail=False):
        self.main_key = main_key
        self.data = data
        self.print_detail = print_detail
        self.console = console

    def parse(self):
        basic_value = self.data.get(self.main_key)
        word_data = basic_value.get("word", {})
        if not word_data and "$ref" in basic_value:
            new_main_key = basic_value["$ref"].replace("$.", "")
            if new_main_key not in self.data:
                normal_warn_printer("cannot find main key currently")
                return
            word_data = self.data[new_main_key].get("word")
        self.parse_phone(word_data)
        self.parse_simple_content(word_data)
        if self.print_detail:
            self.parse_detail_content()

    def parse_phone(self, word_data):
        pass

    def parse_simple_content(self, word_data):
        pass

    def parse_detail_content(self):
        pass

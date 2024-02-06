from .YoudaoParser import YoudaoParser


class ENParserLegacy(YoudaoParser):
    def get_data(self):
        self.data = self.youdao_download(self.text)

    def parse_phone(self):
        pass

    def parse_simple_content(self):
        pass

    def parse_detail_content(self):
        pass

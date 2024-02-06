from .YoudaoParser import YoudaoParser


class CEParserLegacy(YoudaoParser):
    def get_data(self):
        self.data = self.youdao_download(self.text)

    def parse_phone(self):
        phone = self.data.xpath('.//div[@id="phrsListTab"]/h2/span[@class="phonetic"]//text()')

    def parse_simple_content(self):
        content = self.data.xpath('.//div[@id="phrsListTab"]/div[@class="trans-container"]/ul//span//text()')
        for i in range(len(content)):
            if "\n" in content[i]:
                content[i] = "\n"
            if ";" in content[i]:
                content[i] = content[i].replace(" ", "")
                content[i - 1] = content[i + 1] = ""
        content = "".join(content[:-1])

    def parse_detail_content(self):
        pass

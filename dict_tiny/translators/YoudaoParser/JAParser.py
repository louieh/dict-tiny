from dict_tiny.util import normal_title_printer, normal_info_printer
from .YoudaoParser import YoudaoParser


class JAParser(YoudaoParser):
    def parse_simple_content(self, word_data):
        sense = word_data.get("sense", [])
        for each_sense in sense:
            cx = each_sense.get("cx")
            if cx:
                normal_info_printer(f"[{cx}]")
            phrList = each_sense.get("phrList", [])
            for each_phrList in phrList:
                jmsy = each_phrList.get("jmsy")
                jmsyT = each_phrList.get("jmsyT")
                if jmsy and jmsyT:
                    normal_info_printer(f"{jmsy}: {jmsyT}")
                elif jmsy:
                    normal_info_printer(jmsy)
                normal_info_printer("")


class JCParser(JAParser):
    def parse_phone(self, word_data):
        head = word_data.get("head", {})
        rs = head.get("rs")
        if rs:
            normal_title_printer(rs)
            normal_info_printer("")


class CJParser(JAParser):
    def parse_phone(self, word_data):
        head = word_data.get("head", {})
        sound = head.get("sound")
        if sound:
            normal_title_printer(sound)
            normal_info_printer("")

from dict_tiny.util import normal_title_printer, normal_info_printer
from .YoudaoParser import YoudaoParser


class KOParser(YoudaoParser):
    def parse_phone(self, word_data):
        for each_word_data in word_data:
            phone = each_word_data.get("phone")
            if phone:
                normal_title_printer(phone)
                normal_info_printer("")

    def parse_simple_content(self, word_data):
        for each_word_data in word_data:
            word_trans = each_word_data.get("trs", [])
            for word_tran in word_trans:
                pos = word_tran.get("pos", "")
                if pos:
                    normal_info_printer(f"[{pos}]")
                tr = word_tran.get("tr", [])
                for each_tr in tr:
                    l = each_tr.get("l", {}).get("i", [])
                    for each_i in l:
                        normal_info_printer(each_i)
                    exam = each_tr.get("exam", {}).get("i", [])
                    for each_exam in exam:
                        f = each_exam.get("f", {}).get("l", {}).get("i", [])
                        n = each_exam.get("n", {}).get("l", {}).get("i", {})
                        if f:
                            normal_info_printer(f"{f[0]}: {n}")
                normal_info_printer("")


class KCParser(KOParser):
    """KCParser"""


class CKParser(KOParser):
    """CKParser"""

from dict_tiny.util import normal_title_printer, normal_info_printer, remove_html_tags
from dict_tiny.translators.YoudaoParser.YoudaoParser import YoudaoParser


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
                    normal_info_printer("")
                    exam = each_tr.get("exam", {}).get("i", [])
                    for each_exam in exam:
                        f = each_exam.get("f", {}).get("l", {}).get("i", [])
                        n = each_exam.get("n", {}).get("l", {}).get("i", [])
                        if f:
                            normal_info_printer(f"  {f[0]}")
                            if n:
                                normal_info_printer(
                                    f"  {n[0] if isinstance(n, list) else n}"
                                )
                            normal_info_printer("")
                normal_info_printer("")


class KCParser(KOParser):
    def parse_detail_content(self):
        longchao_kc = self.data.get("longchao-kc")
        if longchao_kc:
            source = longchao_kc.get("source", {}).get("name", "")
            self.console.print(f"\n:book: [bold magenta]{source}[/bold magenta]:")
            for item in longchao_kc.get("dataList", []):
                for sense in item.get("meanings", {}).get("sense", []):
                    pos = sense.get("pos", "")
                    if pos:
                        normal_info_printer(f"[{pos}]")

                    for tr_entry in sense.get("trs", []):
                        terminology = tr_entry.get("terminology", "")
                        tr_text = remove_html_tags(tr_entry.get("tr", ""))
                        prefix = f"{terminology} " if terminology else ""
                        if tr_text:
                            normal_info_printer(f"{prefix}{tr_text}")

                        sentences = tr_entry.get("sentences", [])
                        for sent in sentences:
                            normal_info_printer(f"  {sent.get('ko')}")
                            normal_info_printer(f"  {sent.get('cn')}")

                        normal_info_printer("")
                normal_info_printer("")


class CKParser(KOParser):
    def parse_detail_content(self):
        longchao_ck = self.data.get("longchao-ck")
        if longchao_ck:
            source = longchao_ck.get("source", {}).get("name", "")
            self.console.print(f"\n:book: [bold magenta]{source}[/bold magenta]:")
            for item in longchao_ck.get("dataList", []):
                terminology = item.get("meanings", {}).get("terminology", "")
                for sense in item.get("meanings", {}).get("sense", []):
                    pos = sense.get("pos", "")
                    if pos:
                        normal_info_printer(f"[{pos}]")

                    for tr_entry in sense.get("trs", []):
                        tr_text = remove_html_tags(tr_entry.get("tr", ""))
                        if terminology and tr_text:
                            normal_info_printer(f"{terminology} {tr_text}")
                        elif tr_text:
                            normal_info_printer(tr_text)

                        sentences = tr_entry.get("sentences", [])
                        for sent in sentences:
                            normal_info_printer(f"  {sent.get('ko')}")
                            normal_info_printer(f"  {sent.get('cn')}")

                        normal_info_printer("")
                normal_info_printer("")

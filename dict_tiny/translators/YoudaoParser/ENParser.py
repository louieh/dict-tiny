from dict_tiny.util import normal_title_printer, normal_info_printer, print_equal, remove_html_tags
from .YoudaoParser import YoudaoParser


class ENParser(YoudaoParser):
    def parse_phone(self, word_data):
        phone = []
        if "usphone" in word_data:
            phone.append(f"[美]{word_data['usphone']}")
        if "ukphone" in word_data:
            phone.append(f"[英]{word_data['ukphone']}")
        if "phone" in word_data:
            phone.append(word_data['phone'])
        if phone:
            normal_title_printer(" ".join(phone))
            normal_info_printer("")

    def parse_simple_content(self, word_data):
        word_trans = word_data.get("trs", [])
        for word_tran in word_trans:
            pos = word_tran.get("pos", "")
            tran = word_tran.get("tran", "")
            if pos or tran:
                normal_info_printer(f"{pos} {tran}")
            text = word_tran.get("#text")
            tran = word_tran.get("#tran")
            if text or tran:
                normal_info_printer(text)
                normal_info_printer(tran)
                normal_info_printer("")
        wfs = word_data.get("wfs", [])
        wfs_results = []
        for wf in wfs:
            wf = wf.get("wf")
            wfs_results.append(f"{wf.get('name')}: {wf.get('value')}")
        if wfs_results:
            normal_info_printer(", ".join(wfs_results))


class ECParser(ENParser):

    def parse_detail_content(self):
        collins = self.data.get("collins", {}).get("collins_entries", [])
        if collins:
            self.console.print("\n:book: [bold magenta]collins[/bold magenta]:")
            for each_collins_entry in collins:
                headword = each_collins_entry.get("headword")
                phonetic = each_collins_entry.get("phonetic")
                normal_title_printer(f"{headword}/{phonetic}")
                entries = each_collins_entry.get("entries", {}).get("entry")
                for entry in entries:
                    tran_entry = entry.get("tran_entry")[0]
                    pos_entry = tran_entry.get("pos_entry")
                    if not pos_entry: continue  # maybe seeAlso
                    print_equal(f"{pos_entry['pos']} {pos_entry['pos_tips']}")
                    tran = tran_entry.get("tran")
                    normal_info_printer(remove_html_tags(tran))
                    exam_sents = tran_entry.get("exam_sents", {}).get("sent", [])
                    for each_sent in exam_sents:
                        normal_info_printer(" 例: %s" % each_sent.get("eng_sent"))
                        normal_info_printer("     %s" % each_sent.get("chn_sent"))
                    normal_info_printer("")


class CEParser(ENParser):

    def parse_detail_content(self):
        wuguanghua = self.data.get("wuguanghua")
        if wuguanghua:
            self.console.print("\n:book: [bold magenta]wuguanghua[/bold magenta]:")
            for each_wuguanghua in wuguanghua.get("dataList", []):
                for entry in each_wuguanghua.get("trs", []):
                    tr = entry.get("tr")
                    normal_info_printer(f"({tr.get('cn')}) {tr.get('en')}")
                    normal_info_printer("")
                    sents = entry.get("sents", [])
                    for each_sent in sents:
                        normal_info_printer(" 例: %s" % each_sent.get("en"))
                        normal_info_printer("     %s" % each_sent.get("cn"))
                    normal_info_printer("")

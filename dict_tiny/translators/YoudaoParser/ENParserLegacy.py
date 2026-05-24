from dict_tiny.config import ISO639LCodes, TERMINAL_SIZE_COLUMN
from dict_tiny.util import normal_title_printer, normal_info_printer, normal_warn_printer, print_equal


class ENParserLegacy(object):

    def print_detailtrans(self, data_base, type, row=3, printall=True):
        '''
        print detail trans, default row=3
        printall has a high priority：
        If printall == True:
            row is invalid
        '''
        detailtrans_dict = self.get_detailtrans_21cn(data_base,
                                                     type)  # get detailtrans_dict from get_detailtrans_21 function
        if not detailtrans_dict:
            normal_warn_printer("\nNo more detail translation.")
            return
        normal_title_printer("\nmore detail:")

        for each_pos in detailtrans_dict.keys():
            if each_pos == None:
                if TERMINAL_SIZE_COLUMN < 20:
                    normal_title_printer("=" * (TERMINAL_SIZE_COLUMN - 1))
                else:
                    normal_title_printer("====================")
            else:
                print_equal(each_pos)

            detailtrans_dict_dict = detailtrans_dict.get(each_pos)
            real_row = len(detailtrans_dict_dict) if printall else min(len(detailtrans_dict_dict), row)
            for i in range(real_row):
                normal_info_printer(i + 1, end="")
                normal_info_printer(":")
                for each in detailtrans_dict_dict[str(i + 1)]:
                    normal_info_printer('  ', end="")
                    normal_info_printer(each)
            normal_info_printer('\n')

    def get_detailtrans_collins(self, data_base):
        '''
        :param data_base: get from get_data function
        :param type: make sure it is en or cn
        :return: a list to print_detailtrans function
        '''
        collins = data_base.get("collins")
        if not collins:
            return None

        detailtrans_list = []
        try:
            entry = collins.get("collins_entries")[0].get("entries").get("entry")
        except:
            return None

        for each_entry in entry:
            detailtrans_dict = {}
            each_entry_tran_entry = each_entry.get("tran_entry")[0]

            # ---- pos and pos tips ----
            pos = each_entry_tran_entry.get("pos_entry")
            if not pos:  # the case of see alse
                continue
            else:
                pos = pos.get("pos")
            pos_tips = each_entry_tran_entry.get("pos_entry").get("pos_tips")
            detailtrans_dict["pos_pos_tips"] = pos + " " + pos_tips if pos_tips else pos

            # ---- tran ----
            tranTemp = each_entry_tran_entry.get("tran")
            if tranTemp:
                tran = each_entry_tran_entry.get("tran").replace("<b>", "").replace("</b>", "")
                detailtrans_dict["tran"] = tran

            # ---- exam_sents ----
            if "exam_sents" in each_entry_tran_entry.keys():
                sents_list = each_entry_tran_entry.get("exam_sents").get("sent")
                detailtrans_dict["sents_list"] = sents_list

            detailtrans_list.append(detailtrans_dict)

        return detailtrans_list

    def print_detailtrans_collins(self, data_base):
        """
        print collins trans
        :param data_base:
        :return:
        """

        detailtrans_list = self.get_detailtrans_collins(data_base)
        if not detailtrans_list:
            normal_warn_printer("\nNo more detail translation.")
            return

        normal_title_printer("\nmore detail (collins):")

        for each_trans in detailtrans_list:
            print_equal(each_trans["pos_pos_tips"])

            # --- print tran ---
            if "tran" in each_trans:
                tran_cn = each_trans["tran"].split(". ")
                if len(tran_cn) >= 2:
                    tran_cn = tran_cn[-1]
                else:
                    tran_cn = each_trans["tran"].split(" ")[-1]
                normal_info_printer(" · " + tran_cn, end="\n\n")
                normal_info_printer(each_trans["tran"].replace(tran_cn, ""))
                normal_info_printer("\n")

            # --- print sents ---
            if "sents_list" in each_trans:
                for each_sent in each_trans["sents_list"]:
                    normal_info_printer(" 例: %s" % each_sent.get("eng_sent"))
                    normal_info_printer("     %s" % each_sent.get("chn_sent"))
                normal_info_printer("\n")

    def get_detailtrans_21cn(self, data_base, type):
        """
        get 21 detail trans dict
        :param data_base:
        :param type:
        :return:
        """

        data21cn = data_base.get("ec21") if type == ISO639LCodes.English.value else data_base.get("ce_new")
        if not data21cn:
            return None
        # -----source
        # source21cn = data21cn.get("source").get("name")

        # -----word
        # word = data21cn.get("return-phrase").get("l").get("i")[0]

        # -----detail trans
        detailtrans_dict = {}
        data21cn = data21cn.get("word")[0]
        # data21.keys(): dict_keys(['phone', 'phrs', 'return-phrase', 'trs'])
        # data21_phrs = data21.get("phrs")
        data21cn_trs = data21cn.get("trs")
        # len(data21_trs): 4: n. vt. vi. adj.
        for each_data21cn_trs in data21cn_trs:
            temp_dict = {}
            pos = each_data21cn_trs.get("pos")
            temp = each_data21cn_trs.get("tr")
            for i in range(len(temp)):
                if temp[i].get("l").get("i"):
                    interpre_list = [temp[i].get("l").get("i")[0]]
                else:
                    interpre_list = []
                # ---list---
                temp_temp = temp[i].get("tr")
                if temp_temp:
                    for j in range(len(temp_temp)):
                        interpre_list.append('(' + str(j + 1) + ')' + "." + temp_temp[j].get("l").get("i")[0])
                # ---exam---
                temp_temp_temp = temp[i].get("exam")
                if temp_temp_temp:
                    for k in range(len(temp_temp_temp)):
                        interpre_list.append(temp_temp_temp[k].get("i").get("f").get("l").get("i"))
                        interpre_list.append(temp_temp_temp[k].get("i").get("n").get("l").get("i"))

                temp_dict[str(i + 1)] = interpre_list
            detailtrans_dict[pos] = temp_dict

        return detailtrans_dict

    def print_basetrans(self, data_base):
        """
        print basic trans
        not be used
        :param data_base:
        :return:
        """

        data = data_base.get("ec")
        # -----word
        word = data.get("word")[0].get("return-phrase").get("l").get("i")
        normal_info_printer(word, end="  ")

        # -----word_type
        exam_type = data.get("exam_type")
        if exam_type:
            exam_type = ", ".join(exam_type)

        # -----word_phone
        data = data.get("word")[0]
        ukphone = data.get("ukphone")
        if ukphone:
            normal_info_printer("英[%s]" % ukphone, end=" ")
        usphone = data.get("usphone")
        if usphone:
            normal_info_printer("美[%s]" % usphone)

        # -----basic trans Not modified because it is not being used
        equal_length = TERMINAL_SIZE_COLUMN - 1 if len(word) + 1 > TERMINAL_SIZE_COLUMN else len(word) - 1
        normal_title_printer("=" * equal_length)
        data = data.get("trs")
        for each_data in data:
            normal_info_printer(each_data.get("tr")[0].get("l").get("i")[0])

    @staticmethod
    def print_phone(phone):
        phone_list = [each_phone.replace("\n", "").replace("\t", "").replace(" ", "") for each_phone in phone]
        for each_phone in phone_list:
            if not each_phone: continue
            normal_title_printer(each_phone, end="")
        if any(phone_list):
            normal_info_printer("\n", end="")

    @staticmethod
    def print_content(content):
        if not content:
            normal_warn_printer("Did not find an explanation for this word.")
            return
        if isinstance(content, str):
            content = [content]
        for each in content:
            normal_info_printer(each)


class ECParserLegacy(ENParserLegacy):

    def parse_phone(self, word_data):
        phone = word_data.xpath('.//div[@id="phrsListTab"]/h2//span[@class="pronounce"]//text()')
        self.print_phone(phone)

    def parse_simple_content(self, word_data):
        content = word_data.xpath('.//div[@id="phrsListTab"]/div[@class="trans-container"]/ul/li//text()')
        self.print_content(content)

    def parse_detail_content(self, data, row=3, printall=True):
        self.print_detailtrans_collins(data)


class CEParserLegacy(ENParserLegacy):

    def parse_phone(self, word_data):
        phone = word_data.xpath('.//div[@id="phrsListTab"]/h2/span[@class="phonetic"]//text()')
        self.print_phone(phone)

    def parse_simple_content(self, word_data):
        content = word_data.xpath('.//div[@id="phrsListTab"]/div[@class="trans-container"]/ul//span//text()')
        for i in range(len(content)):
            if "\n" in content[i]:
                content[i] = "\n"
            if ";" in content[i]:
                content[i] = content[i].replace(" ", "")
                content[i - 1] = content[i + 1] = ""
        content = "".join(content[:-1])
        self.print_content(content)

    def parse_detail_content(self, data, row=3, printall=True):
        self.print_detailtrans(data, "zh", row, printall)

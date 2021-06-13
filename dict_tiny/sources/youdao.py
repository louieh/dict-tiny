import json
import requests

from setting import YOUDAO_API_FAKE_HEADER, YOUDAO_WEB_FAKE_HEADER, YOUDAO_BASE_URL, TERMINAL_SIZE_COLUMN
from util import downloader, downloader_plain, is_alphabet
from plumbum import colors


def youdao_trans(word):
    """
    entry of youdao web translate
    :param word: a word need to by translated
    :return: self.needDetailWord in main.py
    """

    if is_alphabet(word) == 'en':
        return trans_en(word)
    elif is_alphabet(word) == 'cn':
        return trans_cn(word)
    else:
        print(colors.red | "[Error!] The content is not an English word or a Chinese word.")


def youdao_download(word):
    """
    youdao web download
    :param word:
    :return:
    """
    request_url = YOUDAO_BASE_URL.format(word)
    return downloader(request_url, YOUDAO_WEB_FAKE_HEADER)


def trans_en(word):
    """
    web: English_Chinese
    :param word:
    :return:
    """

    count = 2  # there are two chinere characters
    data, status_code = youdao_download(word)  # result will be deleted
    if data is None:  # no internet
        return
    phone = data.xpath('.//div[@id="phrsListTab"]/h2//span[@class="pronounce"]//text()')
    content = data.xpath('.//div[@id="phrsListTab"]/div[@class="trans-container"]/ul/li//text()')
    print(colors.green | word, end='  ')
    for each_phone in phone:
        if each_phone:
            print(colors.green | each_phone.strip(), end="")
            count += len(each_phone.strip())
    print("\n", end="")

    # print =
    if len(word) + count + 2 > TERMINAL_SIZE_COLUMN:
        for i in range(TERMINAL_SIZE_COLUMN - 1):
            print(colors.green | "=", end="")
        print(colors.green | "=")
    else:
        for i in range(len(word) + count + 1):
            print(colors.green | "=", end="")
        print(colors.green | "=")

    if len(content) >= 1:
        for each_result in content:
            print(each_result)
        return word + "_en"
    else:
        if status_code == 200:  # no translation
            print(colors.yellow | "Did not find an explanation for this word.")
        else:  # 403?
            print(colors.yellow | "The translation of this word cannot be found at this time. Please try again.")


def trans_cn(word):
    """
    web: Chinese_English
    :param word:
    :return:
    """

    count = len(word)
    data, status_code = youdao_download(word)  # result will be deleted
    if data is None:  # no internet
        return
    phone = data.xpath('.//div[@id="phrsListTab"]/h2/span[@class="phonetic"]//text()')
    content = data.xpath('.//div[@id="phrsListTab"]/div[@class="trans-container"]/ul//span//text()')
    for i in range(len(content)):
        if "\n" in content[i]:
            content[i] = "\n"
        if ";" in content[i]:
            content[i] = content[i].replace(" ", "")
            content[i - 1] = content[i + 1] = ""
    content = "".join(content[:-1])

    print(colors.green | word, end='  ')
    for each_phone in phone:
        if each_phone:
            print(colors.green | each_phone.strip(), end="")
            count += len(each_phone.strip())
    print("\n", end="")

    # print =
    if len(word) + count + 2 > TERMINAL_SIZE_COLUMN:
        for i in range(TERMINAL_SIZE_COLUMN - 1):
            print(colors.green | "=", end="")
        print(colors.green | "=")
    else:
        for i in range(len(word) + count + 1):
            print(colors.green | "=", end="")
        print(colors.green | "=")

    if content:
        print(content)
        return word + "_cn"
    else:
        if status_code == 200:  # no translation
            print(colors.yellow | "Did not find an explanation for this word.")
        else:  # 403?
            print(colors.yellow | "The translation of this word cannot be found at this time. Please try again.")


def show_more(word, type, row=3, printall=True):
    """
    youdao API English_Chinese_detail
    :param word: word
    :param type: cn or en
    :param row: the number of row need to be printed, default 3
    :param printall: if print all content, default True
    :return:
    """

    data_base = get_data(word)
    if not data_base:
        print(
            colors.yellow | "The detail translation of this word cannot be found at this time. Please try again later.")
        return
    # print_basetrans(data_base)
    if type == 'cn':
        print_detailtrans(data_base, type, row, printall)  # two parameters：row=3, printall=False
    elif type == 'en':
        print_detailtrans_collins(data_base)
    # print("[Error!] Cannot get detail translation.")


def get_data(word):
    """
    download data from API
    :param word:
    :return:
    """

    # real_requests_url = "http://dict.youdao.com/jsonapi?q=book&doctype=json&keyfrom=mac.main&id=4547758663ACBEFE0CFE4A1B3A362683&vendor=cidian.youdao.com&appVer=2.1.1&client=macdict&jsonversion=2"
    requests_url = "http://dict.youdao.com/jsonapi?q=%s" % word
    resp = downloader_plain(requests_url, YOUDAO_API_FAKE_HEADER)
    if resp:
        return json.loads(resp)
    return None


def print_detailtrans(data_base, type, row=3, printall=True):
    '''
    print detail trans, default row=3
    printall has a high priority：
    If printall == True:
        row is invalid
    '''
    detailtrans_dict = get_detailtrans_21cn(data_base, type)  # get detailtrans_dict from get_detailtrans_21 function
    if not detailtrans_dict:
        print(colors.yellow | "\nNo more detail translation.")
        return
    # print("\033[95m" + "\nmore ===detail:" + "\033[0m")
    print(colors.green | "\nmore detail:")

    for each_pos in detailtrans_dict.keys():
        if each_pos == None:
            if TERMINAL_SIZE_COLUMN < 20:
                for i in range(TERMINAL_SIZE_COLUMN - 1):
                    print(colors.green | "=", end="")
                print(colors.green | "=")
            else:
                print(colors.green | "====================")
        else:
            print_equal(each_pos)

        detailtrans_dict_dict = detailtrans_dict.get(each_pos)
        real_row = len(detailtrans_dict_dict) if printall else min(len(detailtrans_dict_dict), row)
        for i in range(real_row):
            print(i + 1, end="")
            print(":")
            for each in detailtrans_dict_dict[str(i + 1)]:
                print('  ', end="")
                print(each)
        print('\n')


def get_detailtrans_collins(data_base):
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


def print_detailtrans_collins(data_base):
    """
    print collins trans
    :param data_base:
    :return:
    """

    detailtrans_list = get_detailtrans_collins(data_base)
    if not detailtrans_list:
        print(colors.yellow | "\nNo more detail translation.")
        return

    print(colors.green | "\nmore detail (collins):")

    for each_trans in detailtrans_list:
        print_equal(each_trans["pos_pos_tips"])

        # --- print tran ---
        if "tran" in each_trans:
            tran_cn = each_trans["tran"].split(". ")
            if len(tran_cn) >= 2:
                tran_cn = tran_cn[-1]
            else:
                tran_cn = each_trans["tran"].split(" ")[-1]
            print(" · " + tran_cn, end="\n\n")
            print(each_trans["tran"].replace(tran_cn, ""))
            print("\n")

        # --- print sents ---
        if "sents_list" in each_trans:
            for each_sent in each_trans["sents_list"]:
                print(" 例: %s" % each_sent.get("eng_sent"))
                print("     %s" % each_sent.get("chn_sent"))
            print("\n")
    return


def get_detailtrans_21cn(data_base, type):
    """
    get 21 detail trans dict
    :param data_base:
    :param type:
    :return:
    """

    data21cn = data_base.get("ec21") if type == 'en' else data_base.get("ce_new")
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


def get_cn_length(string):
    """
    return the number of chinese char
    :param string:
    :return:
    """

    count = 0
    for each in string:
        if each >= '\u4e00' and each <= '\u9fff':
            count += 1
    return count


def print_equal(string):
    """
    print equal symbol base on terminal size
    :param string:
    :return:
    """

    equal_number = TERMINAL_SIZE_COLUMN - len(string) - get_cn_length(string) - 2
    if equal_number >= 16:  # 8 equal each side
        print(colors.green | "======== %s ========" % string)
    elif equal_number <= 1:
        print(colors.green | string)
    else:
        for i in range(int(equal_number / 2)):
            print(colors.green | "=", end="")
        print(colors.green | " %s " % string, end="")
        for i in range(equal_number - int(equal_number / 2) - 1):
            print(colors.green | "=", end="")
        print(colors.green | "=")


def print_basetrans(data_base):
    """
    print basic trans
    not be used
    :param data_base:
    :return:
    """

    data = data_base.get("ec")
    # -----word
    word = data.get("word")[0].get("return-phrase").get("l").get("i")
    print(word, end="  ")

    # -----word_type
    exam_type = data.get("exam_type")
    if exam_type:
        exam_type = ", ".join(exam_type)

    # -----word_phone
    data = data.get("word")[0]
    ukphone = data.get("ukphone")
    if ukphone:
        print("英[%s]" % ukphone, end=" ")
    usphone = data.get("usphone")
    if usphone:
        print("美[%s]" % usphone)

    # -----basic trans Not modified because it is not being used
    if len(word) - 1 + 2 > TERMINAL_SIZE_COLUMN:
        for i in range(TERMINAL_SIZE_COLUMN - 1):
            print(colors.green | "=", end="")
        print(colors.green | "=")
    else:
        for i in range(len(word) - 1):
            print(colors.green | "=", end="")
        print(colors.green | "==")
    data = data.get("trs")
    for each_data in data:
        print(each_data.get("tr")[0].get("l").get("i")[0])

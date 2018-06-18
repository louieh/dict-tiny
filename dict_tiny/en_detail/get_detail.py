#!/usr/bin/python
# -*- coding: UTF-8 -*-

import requests
import json


# TODO Fake_header

def get_data(word):
    '''
    download data from api
    '''
    # real_requests_url = "http://dict.youdao.com/jsonapi?q=book&doctype=json&keyfrom=mac.main&id=4547758663ACBEFE0CFE4A1B3A362683&vendor=cidian.youdao.com&appVer=2.1.1&client=macdict&jsonversion=2"
    requests_url = "http://dict.youdao.com/jsonapi?q=%s" % word
    resp = requests.get(requests_url).text
    data_base = json.loads(resp)

    return data_base


def print_basetrans(data_base):
    '''
    print basic trans
    '''
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

    # -----basic trans
    for i in range(len(word) - 1):
        print("=", end="")
    print("==")
    data = data.get("trs")
    for each_data in data:
        print(each_data.get("tr")[0].get("l").get("i")[0])


def print_detailtrans(data_base, row=3, pa=False):
    '''
    print detail trans, default row=3
    '''
    detailtrans_dict = get_detailtrans_21(data_base)  # get detailtrans_dict from get_detailtrans_21 function
    print("\nmore detail:")
    for each_pos in detailtrans_dict.keys():
        print("======== %s ========" % each_pos)
        detailtrans_dict_dict = detailtrans_dict.get(each_pos)
        real_row = len(detailtrans_dict_dict) if pa else min(len(detailtrans_dict_dict), row)
        for i in range(real_row):
            print(i + 1, end="")
            print(":")
            for each in detailtrans_dict_dict[str(i + 1)]:
                print('\t', end="")
                print(each)
        print('\t')


def get_detailtrans_21(data_base):
    '''
    get 21 detail trans dict
    '''
    data21 = data_base.get("ec21")

    # -----source
    source21 = data21.get("source").get("name")

    # -----word
    # word = data21.get("return-phrase").get("l").get("i")[0]

    # -----detail trans
    detailtrans_dict = {}
    data21 = data21.get("word")[0]
    # data21.keys(): dict_keys(['phone', 'phrs', 'return-phrase', 'trs'])
    # data21_phrs = data21.get("phrs")
    data21_trs = data21.get("trs")
    # len(data21_trs): 4: n. vt. vi. adj.
    for each_data21_trs in data21_trs:
        temp_dict = {}
        pos = each_data21_trs.get("pos")
        temp = each_data21_trs.get("tr")
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


if __name__ == "__main__":
    data_base = get_data(word="user")
    print_basetrans(data_base)
    print_detailtrans(data_base, row=3)

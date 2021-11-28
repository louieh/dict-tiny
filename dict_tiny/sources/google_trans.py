import requests
from html import unescape
from plumbum import colors
from dict_tiny.setting import GOOGLE_TRANS_API_BASE_URL, TIME_OUT


def google_trans(text, target_language, source_language):
    """
    google translate
    :param text: text need to be translated
    :param target_language:
    :param source_language:
    :return:
    """
    data = {"text": text}
    if target_language:
        data["target"] = target_language
    if source_language:
        data["source"] = source_language
    try:
        resp = requests.post(GOOGLE_TRANS_API_BASE_URL.format("translate"), json=data, timeout=TIME_OUT)
    except requests.exceptions.ConnectionError as e:
        print(colors.red | "[Error!] Time out.")
        return
    resp_json = resp.json()
    if resp_json["code"] != 200:
        print("Google translate error, code: ", resp_json["code"])
        return
    print(colors.green | ">>> Google Translate")
    res = {
        "input": text,
        "output": unescape(resp_json["data"]["translatedText"])
    }
    if not source_language:
        res.update({"detected language": resp_json["data"]["detectedSourceLanguage"]})
    else:
        res.update({"source language": source_language})
    for k, v in res.items():
        print("{}: {}".format(k, v))


def detect_language(text):
    """
    detect language
    :param text: text need to be detected
    :return:
    """
    try:
        resp = requests.post(GOOGLE_TRANS_API_BASE_URL.format("detect_language"), json={
            "text": text
        }, timeout=TIME_OUT)
    except requests.exceptions.ConnectionError as e:
        print(colors.red | "[Error!] Time out.")
        return
    resp_json = resp.json()
    if resp_json["code"] != 200:
        print("Google detect language error: ", resp_json["code"])
        return
    print(colors.green | ">>> Google language detection")
    for k, v in resp_json["data"].items():
        print("{}: {}".format(k, v))

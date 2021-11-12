import requests
from plumbum import colors
from dict_tiny.setting import GOOGLE_TRANS_API_BASE_URL


def google_trans(text, target_language, source_language):
    """
    google translate
    :param text: text need to be translated
    :param target_language:
    :param source_language:
    :return:
    """
    try:
        resp = requests.post(GOOGLE_TRANS_API_BASE_URL.format("translate"), json={
            "text": text,
            "target": target_language,
            "source": source_language,
        })
        resp_json = resp.json()
        if resp_json["code"] != 200:
            print("Google translate error, code: ", resp_json["code"])
        print(colors.green | ">>> Google Translate")
        for k, v in resp_json["data"].items():
            print("{}: {}".format(k, v))
    except Exception as e:
        # print(str(e))
        print("Google translate error.")


def detect_language(text):
    """
    detect language
    :param text: text need to be detected
    :return:
    """
    try:
        resp = requests.post(GOOGLE_TRANS_API_BASE_URL.format("detect_language"), json={
            "text": text
        })
        resp_json = resp.json()
        if resp_json["code"] != 200:
            print("Google detect language error: ", resp_json["code"])
        print(colors.green | ">>> Google detect language")
        for k, v in resp_json["data"].items():
            print("{}: {}".format(k, v))
    except Exception as e:
        print("Google detect language error.")

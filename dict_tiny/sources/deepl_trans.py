import requests
from plumbum import colors
from dict_tiny.setting import DEEPL_TRANS_API_BASE_URL, TIME_OUT


def deepl_trans(text, target_language=None):
    """
    :param text:
    :param target_language:
    :return:
    """
    data = {
        "text": text
    }
    if target_language:
        data.update({"target": target_language})
    try:
        resp = requests.post(DEEPL_TRANS_API_BASE_URL.format("translate"), json=data, timeout=TIME_OUT)
    except requests.exceptions.ConnectionError as e:
        print(colors.red | "[Error!] Time out.")
        return
    resp_json = resp.json()
    if resp_json["code"] != 200:
        # print("DeepL error: ", resp_json["msg"])
        print("DeepL error, code: ", resp_json["code"])
        return
    else:
        print(colors.green | ">>> DeepL Translator")
        res = {
            "detected language": resp_json["data"]["detected_source_lang"],
            "input": text,
            "output": resp_json["data"]["text"]
        }
        for k, v in res.items():
            print("{}: {}".format(k, v))

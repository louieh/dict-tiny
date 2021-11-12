import requests
from plumbum import colors
from dict_tiny.setting import DEEPL_TRANS_API_BASE_URL


def deepl_trans(text, target_language=None):
    """
    :param text:
    :param target_language:
    :return:
    """
    try:
        data = {
            "text": text
        }
        if target_language:
            data.update({"target": target_language})
        resp = requests.post(DEEPL_TRANS_API_BASE_URL.format("translate"), json=data)
        resp_json = resp.json()
        if resp_json["code"] != 200:
            # print("DeepL error: ", resp_json["msg"])
            print("DeepL error, code: ", resp_json["code"])
        else:
            print(colors.green | ">>> DeepL Translator")
            print("input: ", text)
            for k, v in resp_json["data"].items():
                print("{}: {}".format(k, v))
    except Exception as e:
        # print("DeepL error: ", str(e))
        print("DeepL error.")

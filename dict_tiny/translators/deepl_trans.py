from html import unescape

import requests
from plumbum import colors, cli

from dict_tiny.config import TIMEOUT, DEEPL_TRANS_API_BASE_URL, DEEPL_SEPARATOR
from dict_tiny.translators.translator import DefaultTrans


class DeepLTrans(DefaultTrans):

    def __init__(self, text, dict_tiny_obj):
        super().__init__(text, dict_tiny_obj)

    @classmethod
    def attr_setter(cls, dict_tiny_cls):
        super().attr_setter(dict_tiny_cls)
        dict_tiny_cls.use_deepltrans = cli.Flag(["-d", "--deepl"],
                                                group="deepl_translate_api",
                                                help="Using DeepL Translator API.")

    def translate(self, target_language=None):
        """
        :param text:
        :param target_language:
        :return:
        """
        data = {
            "text": self.text
        }
        if target_language:
            data.update({"target": target_language})
        try:
            resp = requests.post(DEEPL_TRANS_API_BASE_URL.format("translate"), json=data, timeout=TIMEOUT)
        except requests.exceptions.ConnectionError as e:
            print(colors.red | "[Error!] Time out.")
            return
        resp_json = resp.json()
        if resp_json["code"] != 200:
            # print("DeepL error: ", resp_json["msg"])
            if resp_json["msg"] == "Quota for this billing period has been exceeded, message: Quota Exceeded":
                print("DeepL error: ",
                      "The quota for this month has been exhausted, please try to add -g to use Google Translate.")
            else:
                print("DeepL error, code: ", resp_json["code"])
            return
        else:
            print(colors.bold & colors.yellow | DEEPL_SEPARATOR)
            res = {
                "detected language": resp_json["data"]["detected_source_lang"],
                "input": self.text,
                "output": unescape(resp_json["data"]["text"])
            }
            for k, v in res.items():
                print("{}: {}".format(k, v))

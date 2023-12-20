from html import unescape

import requests
from plumbum import colors, cli

from dict_tiny.config import TIMEOUT, GOOGLE_TRANS_API_BASE_URL, GOOGLE_SEPARATOR
from dict_tiny.translators.translator import DefaultTrans


class GoogleTrans(DefaultTrans):

    def __init__(self, text, dict_tiny_obj):
        super().__init__(text, dict_tiny_obj)

    @classmethod
    def attr_setter(cls, dict_tiny_cls):
        super().attr_setter(dict_tiny_cls)
        dict_tiny_cls.use_googletrans = cli.Flag(["-g", "--google"],
                                                 group="Google translate",
                                                 help="Use Google Translate")
        dict_tiny_cls.target_language = cli.SwitchAttr("--target-language", str,
                                                       group="Google translate",
                                                       envname="DICT_TINY_TARGET_LAN",
                                                       help="what language you want to translate into")
        dict_tiny_cls.source_language = cli.SwitchAttr("--source-language", str,
                                                       group="Google translate",
                                                       help="what language you want to translate")
        dict_tiny_cls.detect_language = cli.SwitchAttr("--detect-language", str,
                                                       group="Google translate",
                                                       help="Detect the language of the given text")
        # TODO
        # @cli.switch("--detect-language", str)
        # def detect_language(self, text):
        #     """
        #     Detect the language of the given text.
        #     """
        #     self.stop = True
        #     detect_language(text)
        #
        # dict_tiny_cls.detect_language = detect_language

    def translate(self):
        """
        google translate
        :param text: text need to be translated
        :param target_language:
        :param source_language:
        :return:
        """
        if self.dict_tiny_obj.detect_language:
            self.detect_language(self.text)
            return
        data = {"text": self.text}
        if self.dict_tiny_obj.target_language:
            data["target"] = self.dict_tiny_obj.target_language
        if self.dict_tiny_obj.source_language:
            data["source"] = self.dict_tiny_obj.source_language
        try:
            resp = requests.post(GOOGLE_TRANS_API_BASE_URL.format("translate"), json=data, timeout=TIMEOUT)
        except requests.exceptions.ConnectionError as e:
            print(colors.red | "[Error!] Time out.")
            return
        resp_json = resp.json()
        if resp_json["code"] != 200:
            print("Google translate error, code: ", resp_json["code"])
            return
        print(colors.bold & colors.yellow | GOOGLE_SEPARATOR)
        res = {
            "input": self.text,
            "output": unescape(resp_json["data"]["translatedText"])
        }
        if not self.dict_tiny_obj.source_language:
            res.update({"detected language": resp_json["data"]["detectedSourceLanguage"]})
        else:
            res.update({"source language": self.dict_tiny_obj.source_language})
        for k, v in res.items():
            print("{}: {}".format(k, v))

    def detect_language(self, text):
        """
        detect language
        :param text: text need to be detected
        :return:
        """
        try:
            resp = requests.post(GOOGLE_TRANS_API_BASE_URL.format("detect_language"), json={
                "text": text
            }, timeout=TIMEOUT)
        except requests.exceptions.ConnectionError as e:
            print(colors.red | "[Error!] Time out.")
            return
        resp_json = resp.json()
        if resp_json["code"] != 200:
            print("Google detect language error: ", resp_json["code"])
            return
        print(colors.bold & colors.yellow | GOOGLE_SEPARATOR)
        for k, v in resp_json["data"].items():
            print("{}: {}".format(k, v))

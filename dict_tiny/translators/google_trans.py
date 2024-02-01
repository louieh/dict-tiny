from html import unescape

from plumbum import cli

from dict_tiny.config import GOOGLE_TRANS_API_BASE_URL, GOOGLE_NAME, ISO639LCodes, GOOGLE_TRANS_API_HEADER, \
    MAX_TEXT_LENGTH
from dict_tiny.errors import TextInputError
from dict_tiny.translators.translator import DefaultTrans
from dict_tiny.util import downloader, normal_info_printer, is_alphabet, normal_error_printer


class GoogleTrans(DefaultTrans):

    def __init__(self, text, dict_tiny_obj):
        super().__init__(text, dict_tiny_obj)
        self.name = GOOGLE_NAME

    @classmethod
    def attr_setter(cls, dict_tiny_cls):
        super().attr_setter(dict_tiny_cls)
        dict_tiny_cls.use_googletrans = cli.Flag(["-g", "--google"],
                                                 group=GOOGLE_NAME,
                                                 help="Use Google Translate")
        dict_tiny_cls.detect_language = cli.Flag("--detect-language",
                                                 group=GOOGLE_NAME,
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

    def pre_action(self, text):
        if len(text) > MAX_TEXT_LENGTH:
            raise TextInputError("The entered text is too long")
        # exchange Chinese and English
        source_guess = ISO639LCodes.English.value if is_alphabet(
            text) == ISO639LCodes.English.value else ISO639LCodes.Chinese.value
        if not self.target_language or self.target_language == source_guess:
            self.target_language = ISO639LCodes.Chinese.value if source_guess == ISO639LCodes.English.value else ISO639LCodes.English.value

    def do_translate(self, text):
        if self.dict_tiny_obj.detect_language:
            self.detect_language(text)
            return

        data = {"text": text}
        if self.target_language:
            data["target"] = self.target_language
        if self.source_language:
            data["source"] = self.source_language

        resp = downloader.download("POST", GOOGLE_TRANS_API_BASE_URL.format("translate"), json=data,
                                   headers=GOOGLE_TRANS_API_HEADER)
        if not resp: return
        try:
            resp_json = resp.json()
        except Exception as e:
            normal_error_printer(f"resp.json error，resp: {resp.text}")
            return
        if resp_json["code"] != 200:
            normal_error_printer(resp_json['msg'])
            return
        res = {
            "output": unescape(resp_json["data"]["translatedText"])
        }
        if not self.source_language:
            res.update({"detected language": resp_json["data"]["detectedSourceLanguage"]})
        else:
            res.update({"source language": self.source_language})
        for k, v in res.items():
            normal_info_printer("{}: {}".format(k, v))

    def detect_language(self, text):
        """
        detect language
        :param text: text need to be detected
        :return:
        """

        resp = downloader.download("POST", GOOGLE_TRANS_API_BASE_URL.format("detect_language"), json={"text": text},
                                   headers=GOOGLE_TRANS_API_HEADER)
        if not resp: return
        try:
            resp_json = resp.json()
        except Exception as e:
            normal_error_printer(f"resp.json error，resp: {resp.text}")
            return
        if resp_json["code"] != 200:
            normal_error_printer(resp_json['msg'])
            return
        for k, v in resp_json["data"].items():
            normal_info_printer("{}: {}".format(k, v))

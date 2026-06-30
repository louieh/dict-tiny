from html import unescape

from plumbum import cli

from dict_tiny.config import (
    GOOGLE_DISPLAY,
    GOOGLE_NAME,
    GOOGLE_TRANS_API_BASE_URL,
    GOOGLE_TRANS_API_HEADER,
)
from dict_tiny.translators.translator import DefaultTrans
from dict_tiny.util import (
    downloader,
    normal_error_printer,
    normal_info_printer,
)


class GoogleTrans(DefaultTrans):
    name = GOOGLE_NAME
    display_name = GOOGLE_DISPLAY

    def __init__(self, text, dict_tiny_obj):
        super().__init__(text, dict_tiny_obj)

    @classmethod
    def attr_setter(cls, dict_tiny_cls):
        super().attr_setter(dict_tiny_cls)
        setattr(
            dict_tiny_cls,
            f"use_{cls.name}",
            cli.Flag(
                ["-g", "--google"],
                group=cls.display_name,
                help="Use Google Translate",
            ),
        )

        # Why Flag instead of SwitchAttr? If "--detect-language" took a string
        # argument, only the first word would be consumed — the rest would leak
        # into positional args. Using Flag + the full *words text is correct for
        # multi-word input.
        dict_tiny_cls.detect_language = cli.Flag(
            "--detect-language",
            group=cls.display_name,
            help="Detect the language of the given text",
        )

    def pre_action(self, text):
        super().pre_action(text)

    def do_translate(self, text):
        if self.dict_tiny_obj.detect_language:
            self.detect_language(text)
            return False

        data = {"text": text}
        if self.target_language:
            data["target"] = self.target_language
        if self.source_language:
            data["source"] = self.source_language

        resp = downloader.post(
            GOOGLE_TRANS_API_BASE_URL.format("translate"),
            json=data,
            headers=GOOGLE_TRANS_API_HEADER,
        )
        if not resp:
            return False
        try:
            resp_json = resp.json()
        except Exception as e:
            normal_error_printer(f"resp.json error，resp: {resp.text}")
            return False
        if resp_json["code"] != 200:
            normal_error_printer(resp_json["msg"])
            return False
        res = {"output": unescape(resp_json["data"]["translatedText"])}
        if not self.source_language:
            res.update(
                {"detected language": resp_json["data"]["detectedSourceLanguage"]}
            )
        else:
            res.update({"source language": self.source_language})
        for k, v in res.items():
            normal_info_printer("{}: {}".format(k, v))
        return True

    def detect_language(self, text):
        """
        detect language
        :param text: text need to be detected
        :return:
        """

        resp = downloader.post(
            GOOGLE_TRANS_API_BASE_URL.format("detect_language"),
            json={"text": text},
            headers=GOOGLE_TRANS_API_HEADER,
        )
        if not resp:
            return False
        try:
            resp_json = resp.json()
        except Exception as e:
            normal_error_printer(f"resp.json error，resp: {resp.text}")
            return False
        if resp_json["code"] != 200:
            normal_error_printer(resp_json["msg"])
            return False
        for k, v in resp_json["data"].items():
            normal_info_printer("{}: {}".format(k, v))
        return True

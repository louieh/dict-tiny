import json
from hashlib import md5

from plumbum import cli

from dict_tiny.config import (
    YOUDAO_API_FAKE_HEADER,
    YOUDAO_DISPLAY,
    YOUDAO_NAME,
    YOUDAO_TARGET_LANG_SET,
    YOUDAO_WEB_API_BASE_URL,
    ISO639LCodes,
)
from dict_tiny.errors import TextInputError, YoudaoParamError
from dict_tiny.translators.translator import DefaultTrans
from dict_tiny.util import (
    downloader,
    normal_warn_printer,
    parse_le,
)

_PARSER_CACHE = {}


def _get_parser_cls(main_key):
    key = main_key.upper()
    if key not in _PARSER_CACHE:
        if key == "EC":
            from dict_tiny.translators.YoudaoParser.ENParser import ECParser

            _PARSER_CACHE[key] = ECParser
        elif key == "CE":
            from dict_tiny.translators.YoudaoParser.ENParser import CEParser

            _PARSER_CACHE[key] = CEParser
        elif key == "FC":
            from dict_tiny.translators.YoudaoParser.FRParser import FCParser

            _PARSER_CACHE[key] = FCParser
        elif key == "CF":
            from dict_tiny.translators.YoudaoParser.FRParser import CFParser

            _PARSER_CACHE[key] = CFParser
        elif key == "KC":
            from dict_tiny.translators.YoudaoParser.KOParser import KCParser

            _PARSER_CACHE[key] = KCParser
        elif key == "CK":
            from dict_tiny.translators.YoudaoParser.KOParser import CKParser

            _PARSER_CACHE[key] = CKParser
        elif key == "JC":
            from dict_tiny.translators.YoudaoParser.JAParser import JCParser

            _PARSER_CACHE[key] = JCParser
        elif key == "CJ":
            from dict_tiny.translators.YoudaoParser.JAParser import CJParser

            _PARSER_CACHE[key] = CJParser
        elif key == "FANYI":
            from dict_tiny.translators.YoudaoParser.FANYIParser import FANYIParser

            _PARSER_CACHE[key] = FANYIParser
        else:
            raise ValueError(f"Unknown parser key: {main_key}")
    return _PARSER_CACHE[key]


class YoudaoTrans(DefaultTrans):
    name = YOUDAO_NAME
    display_name = YOUDAO_DISPLAY

    def __init__(self, text, dict_tiny_obj):
        super().__init__(text, dict_tiny_obj)
        if self.target_language and self.target_language not in YOUDAO_TARGET_LANG_SET:
            raise YoudaoParamError(
                f"the target language {self.target_language} is not supported"
            )
        if self.source_language and self.source_language not in YOUDAO_TARGET_LANG_SET:
            raise YoudaoParamError(
                f"the source language {self.source_language} is not supported"
            )
        self.trans_le = parse_le(self.source_language, self.target_language)

    @classmethod
    def attr_setter(cls, dict_tiny_cls):
        super().attr_setter(dict_tiny_cls)
        setattr(
            dict_tiny_cls,
            f"use_{cls.name}",
            cli.Flag(
                ["-y", "--youdao"],
                group=cls.display_name,
                help="Use Youdao Dictionary to translate",
            ),
        )
        dict_tiny_cls.more_detail = cli.Flag(
            ["-m", "--more"], group=cls.display_name, help="Get more details"
        )

    def do_translate(self, text):
        data = self.get_web_api_data(text, self.trans_le)
        resp = self.youdao_api_download(
            YOUDAO_WEB_API_BASE_URL.format(text), "POST", data=data
        )
        if not resp:
            return False

        if resp.get("code") == 20:
            raise TextInputError(resp.get("message"))

        meta_dict = resp.get("meta", {})
        guess_language = meta_dict.get("guessLanguage")
        le = meta_dict.get("le")
        if self.source_language:
            is_cn_source = self.source_language == ISO639LCodes.Chinese.value
        elif self.target_language:
            is_cn_source = self.target_language != ISO639LCodes.Chinese.value
        else:
            is_cn_source = guess_language == ISO639LCodes.Chinese.value

        main_key = f"c{le[0]}" if is_cn_source else f"{le[0]}c"
        dicts = meta_dict.get("dicts")
        if main_key not in dicts:
            if "fanyi" in dicts:
                main_key = "fanyi"
            else:
                normal_warn_printer("No results found.")
                return False
        parser_cls = _get_parser_cls(main_key)
        return parser_cls(
            main_key, resp, self.console, self.dict_tiny_obj.more_detail
        ).parse()

    @staticmethod
    def get_web_api_data(text, le):
        """
        from https://blog.csdn.net/cherish1112365/article/details/131537040
        :param text:
        :param le:
        :return:
        """
        w = "Mk6hqtUp33DGGtoS63tTJbMUYjRrG1Lu"
        v = "webdict"
        _ = "web"

        r = text + v
        t = len(r) % 10
        o = md5(r.encode("utf8")).hexdigest()
        n = _ + text + str(t) + w + o
        f = md5(n.encode("utf8")).hexdigest()

        return {"q": text, "le": le, "t": t, "client": _, "sign": f, "keyfrom": v}

    @staticmethod
    def youdao_api_download(url, method="GET", **kwargs):
        """
        download data from API
        :param text:
        :return:
        """

        # real_requests_url = "http://dict.youdao.com/jsonapi?q=book&doctype=json&keyfrom=mac.main&id=4547758663ACBEFE0CFE4A1B3A362683&vendor=cidian.youdao.com&appVer=2.1.1&client=macdict&jsonversion=2"
        resp = downloader.download(
            method, url, headers=YOUDAO_API_FAKE_HEADER, **kwargs
        )
        if not resp:
            return
        try:
            return resp.json()
        except json.JSONDecodeError:
            pass
        except Exception:
            pass

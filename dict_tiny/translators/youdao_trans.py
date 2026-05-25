import json
from hashlib import md5

from plumbum import cli

from dict_tiny.config import (
    YOUDAO_WEB_FAKE_HEADER,
    YOUDAO_API_FAKE_HEADER,
    YOUDAO_WEB_BASE_URL,
    YOUDAO_APP_API_BASE_URL,
    YOUDAO_NAME,
    ISO639LCodes,
    YOUDAO_TARGET_LANG_SET,
    YOUDAO_WEB_API_BASE_URL,
)
from dict_tiny.errors import YoudaoParamError, TextInputError
from dict_tiny.translators.translator import DefaultTrans
from dict_tiny.util import (
    downloader,
    normal_warn_printer,
    parse_le,
    is_alphabet,
    normal_error_printer,
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

    def __init__(self, text, dict_tiny_obj):
        super().__init__(text, dict_tiny_obj)
        self.name = YOUDAO_NAME
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
        dict_tiny_cls.use_youdaotrans = cli.Flag(
            ["-y", "--youdao"],
            group=YOUDAO_NAME,
            help="Use Youdao Dictionary to translate",
        )
        dict_tiny_cls.more_detail = cli.Flag(
            ["-m", "--more"], group=YOUDAO_NAME, help="Get more details"
        )
        dict_tiny_cls.legacy = cli.Flag(
            ["--legacy"], group=YOUDAO_NAME, help="Use legacy translate method"
        )

    def do_translate(self, text):
        if self.dict_tiny_obj.legacy:
            self.do_translate_legacy(text)
            return
        data = self.get_web_api_data(text, self.trans_le)
        resp = self.youdao_api_download(
            YOUDAO_WEB_API_BASE_URL.format(text), "POST", data=data
        )
        if not resp:
            return

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
                return
        parser_cls = _get_parser_cls(main_key)
        parser_cls(main_key, resp, self.console, self.dict_tiny_obj.more_detail).parse()

    def do_translate_legacy(self, text):
        data = self.youdao_download(text)
        if data is None:
            return

        self.source_language = is_alphabet(text)
        if self.source_language not in (
            ISO639LCodes.Chinese.value,
            ISO639LCodes.English.value,
        ):
            normal_error_printer(
                "The input content is neither an English word nor a Chinese word."
            )
            raise

        from dict_tiny.translators.YoudaoParser.ENParserLegacy import (
            ECParserLegacy,
            CEParserLegacy,
        )

        parser_obj = (
            ECParserLegacy()
            if self.source_language == ISO639LCodes.English.value
            else CEParserLegacy()
        )
        parser_obj.parse_phone(data)
        parser_obj.parse_simple_content(data)
        if not self.dict_tiny_obj.more_detail:
            return
        data_base = self.youdao_api_download(YOUDAO_APP_API_BASE_URL.format(text))
        if not data_base:
            normal_warn_printer(
                "The detail translation of this word cannot be found at this time. Please try again later."
            )
            return
        parser_obj.parse_detail_content(data_base, self.source_language)

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
    def youdao_download(text):
        """
        download from web
        :param text:
        :return:
        """
        resp = downloader.get(
            YOUDAO_WEB_BASE_URL.format(text), headers=YOUDAO_WEB_FAKE_HEADER
        )
        if not resp:
            return
        from lxml import html

        return html.etree.HTML(resp.text)

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
        except json.JSONDecodeError as e:
            pass
        except Exception as e:
            pass

from unittest.mock import MagicMock, patch

from dict_tiny.translators.YoudaoParser.ENParser import CEParser, ECParser, ENParser
from dict_tiny.translators.YoudaoParser.FRParser import FRParser
from dict_tiny.translators.YoudaoParser.YoudaoParser import YoudaoParser


class TestYoudaoParserBase:
    def test_parse_no_word_data_with_ref(self):
        data = {
            "ec": {"word": {}, "$ref": "$.ec2"},
            "ec2": {"word": {"trs": [{"pos": "n.", "tran": "书"}]}},
        }
        parser = YoudaoParser("ec", data, MagicMock())
        with patch(
            "dict_tiny.translators.YoudaoParser.YoudaoParser.normal_warn_printer"
        ) as mock_warn:
            parser.parse()
        mock_warn.assert_not_called()

    def test_parse_ref_not_found(self):
        data = {"ec": {"word": {}, "$ref": "$.nonexistent"}}
        parser = YoudaoParser("ec", data, MagicMock())
        with patch(
            "dict_tiny.translators.YoudaoParser.YoudaoParser.normal_warn_printer"
        ) as mock_warn:
            parser.parse()
        mock_warn.assert_called_once_with("cannot find main key")

    def test_parse_empty_data(self):
        parser = YoudaoParser("ec", {}, MagicMock())
        result = parser.parse()
        assert not result


class TestENParser:
    def test_parse_phone(self):
        word_data = {"usphone": "bʊk", "ukphone": "bʊk"}
        parser = ENParser("ec", {"ec": {"word": word_data}}, MagicMock())
        with patch(
            "dict_tiny.translators.YoudaoParser.ENParser.normal_title_printer"
        ) as mock_print:
            parser.parse_phone(word_data)
        mock_print.assert_called_once_with("[美]bʊk [英]bʊk")

    def test_parse_phone_us_only(self):
        word_data = {"usphone": "bʊk"}
        parser = ENParser("ec", {"ec": {"word": word_data}}, MagicMock())
        with patch(
            "dict_tiny.translators.YoudaoParser.ENParser.normal_title_printer"
        ) as mock_print:
            parser.parse_phone(word_data)
        mock_print.assert_called_once_with("[美]bʊk")

    def test_parse_phone_empty(self):
        parser = ENParser("ec", {"ec": {"word": {}}}, MagicMock())
        with patch(
            "dict_tiny.translators.YoudaoParser.ENParser.normal_title_printer"
        ) as mock_print:
            parser.parse_phone({})
        mock_print.assert_not_called()

    def test_parse_simple_content_with_trs(self):
        word_data = {
            "trs": [{"pos": "n.", "tran": "书，书籍"}, {"pos": "v.", "tran": "预订"}]
        }
        parser = ENParser("ec", {"ec": {"word": word_data}}, MagicMock())
        with patch(
            "dict_tiny.translators.YoudaoParser.ENParser.normal_info_printer"
        ) as mock_print:
            parser.parse_simple_content(word_data)
        mock_print.assert_any_call("n. 书，书籍")
        mock_print.assert_any_call("v. 预订")

    def test_parse_simple_content_with_wfs(self):
        word_data = {
            "wfs": [
                {"wf": {"name": "复数", "value": "books"}},
                {"wf": {"name": "过去式", "value": "booked"}},
            ]
        }
        parser = ENParser("ec", {"ec": {"word": word_data}}, MagicMock())
        with patch(
            "dict_tiny.translators.YoudaoParser.ENParser.normal_info_printer"
        ) as mock_print:
            parser.parse_simple_content(word_data)
        mock_print.assert_any_call("复数: books, 过去式: booked")


class TestECParser:
    def test_parse_detail_content_collins(self):
        data = {
            "ec": {"word": {}},
            "collins": {
                "collins_entries": [
                    {
                        "headword": "book",
                        "phonetic": "bʊk",
                        "entries": {
                            "entry": [
                                {
                                    "tran_entry": [
                                        {
                                            "pos_entry": {
                                                "pos": "N-COUNT",
                                                "pos_tips": "可数名词",
                                            },
                                            "tran": "a written work",
                                            "exam_sents": {
                                                "sent": [
                                                    {
                                                        "eng_sent": "This is a book.",
                                                        "chn_sent": "这是一本书。",
                                                    }
                                                ]
                                            },
                                        }
                                    ]
                                }
                            ]
                        },
                    }
                ]
            },
        }
        parser = ECParser("ec", data, MagicMock())
        with patch(
            "dict_tiny.translators.YoudaoParser.ENParser.normal_info_printer"
        ) as mock_print:
            with patch(
                "dict_tiny.translators.YoudaoParser.ENParser.print_equal"
            ) as mock_equal:
                parser.parse_detail_content()
        mock_equal.assert_called_once_with("N-COUNT 可数名词")
        mock_print.assert_any_call("a written work")
        mock_print.assert_any_call(" 例: This is a book.")
        mock_print.assert_any_call("     这是一本书。")


class TestCEParser:
    def test_parse_detail_content_wuguanghua(self):
        data = {
            "ec": {"word": {}},
            "wuguanghua": {
                "source": {"name": "《吴光华汉英大辞典》"},
                "dataList": [
                    {
                        "trs": [
                            {
                                "tr": {"en": "once"},
                                "sents": [
                                    {
                                        "en": "He once lived in Shanghai.",
                                        "cn": "他曾经在上海住过。",
                                    }
                                ],
                            }
                        ]
                    }
                ],
            },
        }
        parser = CEParser("ec", data, MagicMock())
        with patch(
            "dict_tiny.translators.YoudaoParser.ENParser.normal_title_printer"
        ) as mock_title:
            with patch(
                "dict_tiny.translators.YoudaoParser.ENParser.normal_info_printer"
            ) as mock_info:
                parser.parse_detail_content()
        mock_title.assert_any_call("once")
        mock_info.assert_any_call("  He once lived in Shanghai.")
        mock_info.assert_any_call("  他曾经在上海住过。")


class TestFRParser:
    def test_parse_phone(self):
        word_data = [{"phone": "bɔ̃ʒu:r"}]
        parser = FRParser("fc", {"fc": {"word": word_data}}, MagicMock())
        with patch(
            "dict_tiny.translators.YoudaoParser.FRParser.normal_title_printer"
        ) as mock_print:
            parser.parse_phone(word_data)
        mock_print.assert_called_once_with("bɔ̃ʒu:r")


class TestJAParser:
    def test_parse_phone_jc(self):
        word_data = {"head": {"hw": "ほん", "rs": "hon", "pjm": "ほん", "ppjm": "ホン"}}
        from dict_tiny.translators.YoudaoParser.JAParser import JCParser

        parser = JCParser("jc", {"jc": {"word": word_data}}, MagicMock())
        with patch(
            "dict_tiny.translators.YoudaoParser.JAParser.normal_title_printer"
        ) as mock_print:
            parser.parse_phone(word_data)
        mock_print.assert_called_once_with("ほん hon 【平】ほん 【片】ホン")

    def test_parse_phone_cj(self):
        word_data = {"head": {"sound": "つうやく"}}
        from dict_tiny.translators.YoudaoParser.JAParser import CJParser

        parser = CJParser("cj", {"cj": {"word": word_data}}, MagicMock())
        with patch(
            "dict_tiny.translators.YoudaoParser.JAParser.normal_title_printer"
        ) as mock_print:
            parser.parse_phone(word_data)
        mock_print.assert_called_once_with("つうやく")

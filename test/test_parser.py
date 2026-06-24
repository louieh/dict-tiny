from unittest.mock import MagicMock, patch

from dict_tiny.translators.YoudaoParser.ENParser import CEParser, ECParser, ENParser
from dict_tiny.translators.YoudaoParser.FANYIParser import FANYIParser
from dict_tiny.translators.YoudaoParser.FRParser import FRParser
from dict_tiny.translators.YoudaoParser.KOParser import CKParser, KCParser
from dict_tiny.translators.YoudaoParser.YoudaoParser import YoudaoParser


class TestYoudaoParserBase:
    """YoudaoParser base class logic: $ref resolution and empty data handling."""

    def test_parse_no_word_data_with_ref(self):
        """Resolves $ref when word data is empty and $ref points to another key."""
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
        """Warns when $ref points to a non-existent key."""
        data = {"ec": {"word": {}, "$ref": "$.nonexistent"}}
        parser = YoudaoParser("ec", data, MagicMock())
        with patch(
            "dict_tiny.translators.YoudaoParser.YoudaoParser.normal_warn_printer"
        ) as mock_warn:
            parser.parse()
        mock_warn.assert_called_once_with("cannot find main key")

    def test_parse_empty_data(self):
        """Returns False when dict data is empty."""
        parser = YoudaoParser("ec", {}, MagicMock())
        result = parser.parse()
        assert not result


class TestEnglishParsers:
    """ENParser/ECParser/CEParser English-related parser tests."""

    # ── ENParser phone ──────────────────────────────────────

    def test_en_parser_parse_phone(self):
        """Displays both US and UK phonetics."""
        word_data = {"usphone": "bʊk", "ukphone": "bʊk"}
        parser = ENParser("ec", {"ec": {"word": word_data}}, MagicMock())
        with patch(
            "dict_tiny.translators.YoudaoParser.ENParser.normal_title_printer"
        ) as mock_print:
            parser.parse_phone(word_data)
        mock_print.assert_called_once_with("[美]bʊk [英]bʊk")

    def test_en_parser_parse_phone_us_only(self):
        """Displays only US phonetics when UK is missing."""
        word_data = {"usphone": "bʊk"}
        parser = ENParser("ec", {"ec": {"word": word_data}}, MagicMock())
        with patch(
            "dict_tiny.translators.YoudaoParser.ENParser.normal_title_printer"
        ) as mock_print:
            parser.parse_phone(word_data)
        mock_print.assert_called_once_with("[美]bʊk")

    def test_en_parser_parse_phone_empty(self):
        """Does not print when phone data is empty."""
        parser = ENParser("ec", {"ec": {"word": {}}}, MagicMock())
        with patch(
            "dict_tiny.translators.YoudaoParser.ENParser.normal_title_printer"
        ) as mock_print:
            parser.parse_phone({})
        mock_print.assert_not_called()

    # ── ENParser simple content ─────────────────────────────

    def test_en_parser_parse_simple_content_with_trs(self):
        """Prints translations (trs) with part-of-speech labels."""
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

    def test_en_parser_parse_simple_content_with_wfs(self):
        """Prints word forms (wfs) like plural and past tense."""
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

    # ── ECParser detail content ─────────────────────────────

    def test_ec_parser_parse_detail_content_collins(self):
        """Parses Collins dictionary entries with POS, translation, and example sentences."""
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

    # ── CEParser detail content ─────────────────────────────

    def test_ce_parser_parse_detail_content_wuguanghua(self):
        """Parses Wuguanghua dictionary entries with translations and example sentences."""
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


class TestFrenchParser:
    """FRParser French parser tests."""

    def test_parse_phone(self):
        """Displays French phonetic notation."""
        word_data = [{"phone": "bɔ̃ʒu:r"}]
        parser = FRParser("fc", {"fc": {"word": word_data}}, MagicMock())
        with patch(
            "dict_tiny.translators.YoudaoParser.FRParser.normal_title_printer"
        ) as mock_print:
            parser.parse_phone(word_data)
        mock_print.assert_called_once_with("bɔ̃ʒu:r")

    def test_parse_simple_content_with_trs(self):
        """Prints French translations with part-of-speech labels."""
        word_data = [
            {
                "trs": [
                    {
                        "pos": "n.m.",
                        "tr": [
                            {"l": {"i": ["书", "书籍"]}},
                            {"l": {"i": ["笔记本"]}},
                        ],
                    }
                ]
            }
        ]
        parser = FRParser("fc", {"fc": {"word": word_data}}, MagicMock())
        with patch(
            "dict_tiny.translators.YoudaoParser.FRParser.normal_info_printer"
        ) as mock_print:
            parser.parse_simple_content(word_data)
        mock_print.assert_any_call("[n.m.]")
        mock_print.assert_any_call("书")
        mock_print.assert_any_call("书籍")
        mock_print.assert_any_call("笔记本")

    def test_parse_simple_content_with_exam(self):
        """Prints example sentences along with translations."""
        word_data = [
            {
                "trs": [
                    {
                        "tr": [
                            {
                                "l": {"i": ["书"]},
                                "exam": {
                                    "i": [
                                        {
                                            "f": {"l": {"i": ["C'est un livre."]}},
                                            "n": {"l": {"i": ["这是一本书。"]}},
                                        }
                                    ]
                                },
                            }
                        ],
                    }
                ]
            }
        ]
        parser = FRParser("fc", {"fc": {"word": word_data}}, MagicMock())
        with patch(
            "dict_tiny.translators.YoudaoParser.FRParser.normal_info_printer"
        ) as mock_print:
            parser.parse_simple_content(word_data)
        mock_print.assert_any_call("书")
        mock_print.assert_any_call("  C'est un livre.")
        mock_print.assert_any_call("  这是一本书。")


class TestJapaneseParser:
    """JAParser (Japanese) phone and simple content parsing for JC/CJ modes."""

    def test_parse_phone_jc(self):
        """Displays Japanese reading with hiragana, romaji, and katakana."""
        word_data = {"head": {"hw": "ほん", "rs": "hon", "pjm": "ほん", "ppjm": "ホン"}}
        from dict_tiny.translators.YoudaoParser.JAParser import JCParser

        parser = JCParser("jc", {"jc": {"word": word_data}}, MagicMock())
        with patch(
            "dict_tiny.translators.YoudaoParser.JAParser.normal_title_printer"
        ) as mock_print:
            parser.parse_phone(word_data)
        mock_print.assert_called_once_with("ほん hon 【平】ほん 【片】ホン")

    def test_parse_phone_cj(self):
        """Displays Japanese reading (hiragana) for CJ mode."""
        word_data = {"head": {"sound": "つうやく"}}
        from dict_tiny.translators.YoudaoParser.JAParser import CJParser

        parser = CJParser("cj", {"cj": {"word": word_data}}, MagicMock())
        with patch(
            "dict_tiny.translators.YoudaoParser.JAParser.normal_title_printer"
        ) as mock_print:
            parser.parse_phone(word_data)
        mock_print.assert_called_once_with("つうやく")

    def test_parse_simple_content_with_cx_and_phr(self):
        """Prints Japanese translations with category and phrase pairs."""
        from dict_tiny.translators.YoudaoParser.JAParser import JCParser

        word_data = {
            "sense": [
                {
                    "cx": "名",
                    "phrList": [
                        {"jmsy": "本", "jmsyT": "书"},
                        {"jmsy": "ほん", "jmsyT": "书本"},
                    ],
                }
            ]
        }
        parser = JCParser("jc", {"jc": {"word": word_data}}, MagicMock())
        with patch(
            "dict_tiny.translators.YoudaoParser.JAParser.normal_info_printer"
        ) as mock_print:
            parser.parse_simple_content(word_data)
        mock_print.assert_any_call("[名]")
        mock_print.assert_any_call("本")
        mock_print.assert_any_call("书")
        mock_print.assert_any_call("ほん")
        mock_print.assert_any_call("书本")

    def test_parse_simple_content_with_jmsy_only(self):
        """Prints Japanese phrases when only jmsy is available (no jmsyT)."""
        from dict_tiny.translators.YoudaoParser.JAParser import JCParser

        word_data = {
            "sense": [
                {
                    "phrList": [
                        {"jmsy": "ありがとう"},
                        {"jmsy": "こんにちは"},
                    ],
                }
            ]
        }
        parser = JCParser("jc", {"jc": {"word": word_data}}, MagicMock())
        with patch(
            "dict_tiny.translators.YoudaoParser.JAParser.normal_info_printer"
        ) as mock_print:
            parser.parse_simple_content(word_data)
        mock_print.assert_any_call("ありがとう")
        mock_print.assert_any_call("こんにちは")


class TestKoreanParser:
    """KOParser Korean phone/simple/detail content for KC (Ko-Ch) and CK (Ch-Ko) modes."""

    def test_parse_phone(self):
        """Displays Korean phonetic notation."""
        word_data = [{"phone": "han-guk"}]
        from dict_tiny.translators.YoudaoParser.KOParser import KOParser

        parser = KOParser("kc", {"kc": {"word": word_data}}, MagicMock())
        with patch(
            "dict_tiny.translators.YoudaoParser.KOParser.normal_title_printer"
        ) as mock_print:
            parser.parse_phone(word_data)
        mock_print.assert_called_once_with("han-guk")

    def test_parse_simple_content_with_trs(self):
        """Prints Korean translations with part-of-speech labels."""
        word_data = [
            {
                "trs": [
                    {
                        "pos": "n.",
                        "tr": [
                            {"l": {"i": ["书", "书籍"]}},
                        ],
                    }
                ]
            }
        ]
        from dict_tiny.translators.YoudaoParser.KOParser import KOParser

        parser = KOParser("kc", {"kc": {"word": word_data}}, MagicMock())
        with patch(
            "dict_tiny.translators.YoudaoParser.KOParser.normal_info_printer"
        ) as mock_print:
            parser.parse_simple_content(word_data)
        mock_print.assert_any_call("[n.]")
        mock_print.assert_any_call("书")
        mock_print.assert_any_call("书籍")

    def test_parse_simple_content_with_exam(self):
        """Prints example sentences along with Korean translations."""
        word_data = [
            {
                "trs": [
                    {
                        "tr": [
                            {
                                "l": {"i": ["书"]},
                                "exam": {
                                    "i": [
                                        {
                                            "f": {"l": {"i": ["이것은 책입니다."]}},
                                            "n": {"l": {"i": ["这是一本书。"]}},
                                        }
                                    ]
                                },
                            }
                        ],
                    }
                ]
            }
        ]
        from dict_tiny.translators.YoudaoParser.KOParser import KOParser

        parser = KOParser("kc", {"kc": {"word": word_data}}, MagicMock())
        with patch(
            "dict_tiny.translators.YoudaoParser.KOParser.normal_info_printer"
        ) as mock_print:
            parser.parse_simple_content(word_data)
        mock_print.assert_any_call("书")
        mock_print.assert_any_call("  이것은 책입니다.")
        mock_print.assert_any_call("  这是一本书。")

    def test_parse_detail_content_kc(self):
        """Parses longchao-kc Korean-Chinese detail content."""
        data = {
            "kc": {"word": {}},
            "longchao-kc": {
                "source": {"name": "Longchao韩中词典"},
                "dataList": [
                    {
                        "meanings": {
                            "sense": [
                                {
                                    "pos": "n.",
                                    "trs": [
                                        {
                                            "terminology": "[术语]",
                                            "tr": "书",
                                            "sentences": [
                                                {
                                                    "ko": "이것은 책입니다.",
                                                    "cn": "这是一本书。",
                                                }
                                            ],
                                        }
                                    ],
                                }
                            ],
                        },
                    }
                ],
            },
        }
        parser = KCParser("kc", data, MagicMock())
        parser.console = MagicMock()
        with patch(
            "dict_tiny.translators.YoudaoParser.KOParser.normal_info_printer"
        ) as mock_print:
            parser.parse_detail_content()
        parser.console.print.assert_called_once()
        mock_print.assert_any_call("[n.]")
        mock_print.assert_any_call("[术语] 书")
        mock_print.assert_any_call("  이것은 책입니다.")
        mock_print.assert_any_call("  这是一本书。")

    def test_parse_detail_content_ck(self):
        """Parses longchao-ck Chinese-Korean detail content."""
        data = {
            "ck": {"word": {}},
            "longchao-ck": {
                "source": {"name": "Longchao中韩词典"},
                "dataList": [
                    {
                        "meanings": {
                            "terminology": "[术语]",
                            "sense": [
                                {
                                    "pos": "n.",
                                    "trs": [
                                        {
                                            "tr": "책",
                                            "sentences": [
                                                {
                                                    "ko": "이것은 책입니다.",
                                                    "cn": "这是一本书。",
                                                }
                                            ],
                                        }
                                    ],
                                }
                            ],
                        },
                    }
                ],
            },
        }
        parser = CKParser("ck", data, MagicMock())
        parser.console = MagicMock()
        with patch(
            "dict_tiny.translators.YoudaoParser.KOParser.normal_info_printer"
        ) as mock_print:
            parser.parse_detail_content()
        parser.console.print.assert_called_once()
        mock_print.assert_any_call("[n.]")
        mock_print.assert_any_call("[术语] 책")
        mock_print.assert_any_call("  이것은 책입니다.")
        mock_print.assert_any_call("  这是一本书。")


class TestFANYIParser:
    """FANYIParser (Fanyi fallback) simple content parsing."""

    def test_parse_simple_content(self):
        """Prints the translation from the fanyi API."""
        data = {"fanyi": {"tran": "你好"}}
        parser = FANYIParser("fanyi", data, MagicMock())
        with patch(
            "dict_tiny.translators.YoudaoParser.FANYIParser.normal_info_printer"
        ) as mock_print:
            parser.parse_simple_content({})
        mock_print.assert_called_once_with("你好")

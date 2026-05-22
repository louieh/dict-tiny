import unittest

from dict_tiny.util import (
    is_alphabet,
    parse_le,
    get_cn_length,
    remove_html_tags,
)


class TestIsAlphabet(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(is_alphabet(""), "other")
        self.assertEqual(is_alphabet(" "), "other")

    def test_english(self):
        self.assertEqual(is_alphabet("book"), "en")
        self.assertEqual(is_alphabet("database"), "en")
        self.assertEqual(is_alphabet("Hello"), "en")
        self.assertEqual(is_alphabet("hello world"), "en")

    def test_chinese(self):
        self.assertEqual(is_alphabet("书"), "zh")
        self.assertEqual(is_alphabet("数据库"), "zh")
        self.assertEqual(is_alphabet("你好世界"), "zh")

    def test_mixed_more_chinese(self):
        self.assertEqual(is_alphabet("如何用Python实现web scraping"), "zh")
        self.assertEqual(is_alphabet("Hello世界"), "zh")

    def test_mixed_more_english(self):
        self.assertEqual(is_alphabet("How are you 你好"), "en")

    def test_equal_english_chinese(self):
        self.assertEqual(is_alphabet("book书"), "zh")

    def test_equal_mixed(self):
        self.assertEqual(is_alphabet("你 A"), "zh")

    def test_mixed_more_english(self):
        self.assertEqual(is_alphabet("How are you 你好"), "en")

    def test_hyphenated_english(self):
        self.assertEqual(is_alphabet("don't"), "en")
        self.assertEqual(is_alphabet("well-known"), "en")
        self.assertEqual(is_alphabet("state-of-the-art"), "en")
        self.assertEqual(is_alphabet("don't 我不知道"), "zh")

    def test_non_alpha(self):
        self.assertEqual(is_alphabet("123"), "other")
        self.assertEqual(is_alphabet("..."), "other")
        self.assertEqual(is_alphabet("!@#"), "other")
        self.assertEqual(is_alphabet("   "), "other")


class TestParseLe(unittest.TestCase):
    def test_no_source_no_target(self):
        self.assertEqual(parse_le("", ""), "en")

    def test_source_english(self):
        self.assertEqual(parse_le("en", ""), "en")

    def test_target_japanese(self):
        self.assertEqual(parse_le("", "ja"), "ja")
        self.assertEqual(parse_le("en", "ja"), "en")

    def test_source_french(self):
        self.assertEqual(parse_le("fr", ""), "fr")

    def test_source_korean(self):
        self.assertEqual(parse_le("ko", ""), "ko")

    def test_source_unsupported(self):
        self.assertEqual(parse_le("pl", "en"), "en")
        self.assertEqual(parse_le("", "pl"), "en")

    def test_source_and_target_unsupported(self):
        self.assertEqual(parse_le("pl", "de"), "en")


class TestGetCnLength(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(get_cn_length(""), 0)

    def test_english_only(self):
        self.assertEqual(get_cn_length("hello"), 0)

    def test_chinese_only(self):
        self.assertEqual(get_cn_length("你好世界"), 4)
        self.assertEqual(get_cn_length("书"), 1)

    def test_mixed(self):
        self.assertEqual(get_cn_length("hello你好"), 2)
        self.assertEqual(get_cn_length("Python编程"), 2)

    def test_numbers_and_symbols(self):
        self.assertEqual(get_cn_length("123"), 0)
        self.assertEqual(get_cn_length("!@#"), 0)


class TestRemoveHtmlTags(unittest.TestCase):
    def test_no_tags(self):
        self.assertEqual(remove_html_tags("hello world"), "hello world")

    def test_with_tags(self):
        self.assertEqual(remove_html_tags("<b>hello</b>"), "hello")
        self.assertEqual(remove_html_tags("<br/>"), "")
        self.assertEqual(remove_html_tags("<div>hello</div>world"), "helloworld")

    def test_nested_tags(self):
        self.assertEqual(remove_html_tags("<div><b>hello</b></div>"), "hello")

    def test_empty(self):
        self.assertEqual(remove_html_tags(""), "")
        self.assertEqual(remove_html_tags("<div></div>"), "")

    def test_mixed_content(self):
        text = "Hello <b>bold</b> and <i>italic</i>."
        self.assertEqual(remove_html_tags(text), "Hello bold and italic.")


if __name__ == "__main__":
    unittest.main()

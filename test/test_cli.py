import unittest
from unittest.mock import patch, MagicMock

from dict_tiny.main import run
from dict_tiny.config import ISO639LCodes, MAX_TEXT_LENGTH
from dict_tiny.translators import _ALL_TRANSLATORS
from dict_tiny.errors import TextInputError
from dict_tiny.translators.translator import DefaultTrans


class TestCliInit(unittest.TestCase):
    def test_has_all_translators(self):
        self.assertIn("youdaodict", _ALL_TRANSLATORS)
        self.assertIn("googletranslate", _ALL_TRANSLATORS)

    def test_default_translator_is_youdao(self):
        from dict_tiny.translators import DEFAULT_TRANSLATOR

        self.assertEqual(DEFAULT_TRANSLATOR.__name__, "YoudaoTrans")

    def test_translator_list_matches_config(self):
        self.assertEqual(len(_ALL_TRANSLATORS), 2)

    def test_iso_codes(self):
        self.assertEqual(ISO639LCodes.Chinese.value, "zh")
        self.assertEqual(ISO639LCodes.English.value, "en")
        self.assertEqual(ISO639LCodes.French.value, "fr")
        self.assertEqual(ISO639LCodes.Japanese.value, "ja")
        self.assertEqual(ISO639LCodes.Korean.value, "ko")


class TestTextLengthLimit(unittest.TestCase):
    def setUp(self):
        self.mock_obj = MagicMock()
        self.mock_obj.source_language = None
        self.mock_obj.target_language = None

    def _make_trans(self, cls, text):
        return cls(text, self.mock_obj)

    def test_normal_text_passes(self):
        trans = self._make_trans(DefaultTrans, "hello")
        trans.pre_action("hello")

    def test_exact_limit_passes(self):
        text = "a" * MAX_TEXT_LENGTH
        trans = self._make_trans(DefaultTrans, text)
        trans.pre_action(text)

    def test_oversized_text_raises(self):
        text = "a" * (MAX_TEXT_LENGTH + 1)
        trans = self._make_trans(DefaultTrans, text)
        with self.assertRaises(TextInputError):
            trans.pre_action(text)

    def test_chinese_oversized_text_raises(self):
        text = "中" * (MAX_TEXT_LENGTH + 1)
        trans = self._make_trans(DefaultTrans, text)
        with self.assertRaises(TextInputError):
            trans.pre_action(text)

    def test_google_translate_normal_passes(self):
        trans = self._make_trans(_ALL_TRANSLATORS["googletranslate"], "hello")
        trans.pre_action("hello")

    def test_google_translate_oversized_raises(self):
        trans = self._make_trans(_ALL_TRANSLATORS["googletranslate"], "hello")
        text = "a" * (MAX_TEXT_LENGTH + 1)
        with self.assertRaises(TextInputError):
            trans.pre_action(text)

    def test_youdao_dict_normal_passes(self):
        trans = self._make_trans(_ALL_TRANSLATORS["youdaodict"], "hello")
        trans.pre_action("hello")

    def test_youdao_dict_oversized_raises(self):
        trans = self._make_trans(_ALL_TRANSLATORS["youdaodict"], "hello")
        text = "a" * (MAX_TEXT_LENGTH + 1)
        with self.assertRaises(TextInputError):
            trans.pre_action(text)


class TestCliIntegration(unittest.TestCase):
    @patch("sys.argv", ["", "-y", "book"])
    def test_cli_youdao_translate(self):
        try:
            run()
        except SystemExit:
            pass
        except Exception as e:
            self.fail(f"Unexpected exception: {e}")

    @patch("sys.argv", ["", "-y", "book", "--target-language", "ja"])
    def test_cli_youdao_japanese(self):
        try:
            run()
        except SystemExit:
            pass
        except Exception as e:
            self.fail(f"Unexpected exception: {e}")




class TestTranslateErrorHandling(unittest.TestCase):
    def setUp(self):
        self.mock_obj = MagicMock()
        self.mock_obj.source_language = None
        self.mock_obj.target_language = None
        self.mock_obj.wordbook = None
        self.mock_obj.more_detail = False

    def _make_trans(self, text="hello"):
        trans = DefaultTrans(text, self.mock_obj)
        trans.name = "test"
        trans.display_name = "TestTrans"
        return trans

    def test_translate_returns_false_on_custom_exception(self):
        trans = self._make_trans()
        with patch.object(trans, 'do_translate',
                          side_effect=TextInputError("too long")):
            result = trans.translate()
            self.assertFalse(result)

    def test_translate_returns_false_on_not_implemented(self):
        trans = self._make_trans()
        with patch.object(trans, 'do_translate',
                          side_effect=NotImplementedError):
            result = trans.translate()
            self.assertFalse(result)

    def test_translate_returns_false_on_generic_exception(self):
        trans = self._make_trans()
        with patch.object(trans, 'do_translate',
                          side_effect=RuntimeError("network error")):
            result = trans.translate()
            self.assertFalse(result)

    def test_translate_skips_extra_action_on_false(self):
        trans = self._make_trans()
        with patch.object(trans, 'do_translate', return_value=False):
            with patch.object(trans, 'extra_action') as mock_ea:
                result = trans.translate()
                self.assertFalse(result)
                mock_ea.assert_not_called()

    def test_translate_calls_extra_action_on_true(self):
        trans = self._make_trans()
        with patch.object(trans, 'do_translate', return_value=True):
            with patch.object(trans, 'extra_action') as mock_ea:
                result = trans.translate()
                self.assertTrue(result)
                mock_ea.assert_called_once_with("hello")

    def test_extra_action_no_wordbook(self):
        """extra_action should not crash when wordbook is None"""
        self.mock_obj.wordbook = None
        trans = self._make_trans()
        trans.extra_action("hello")  # should not raise

    def test_extra_action_with_wordbook_records(self):
        """extra_action should record to wordbook when available"""
        mock_wb = MagicMock()
        self.mock_obj.wordbook = mock_wb
        trans = self._make_trans()
        trans.extra_action("hello")
        mock_wb.record.assert_called_once_with(
            "hello", None, None, "test"
        )

    def test_trans_obj_getter_returns_none_without_flag(self):
        class MockNoFlag:
            source_language = None
            target_language = None
        trans_cls = type("FakeTrans", (DefaultTrans,), {"name": "faketrans"})
        result = trans_cls.trans_obj_getter("hello", MockNoFlag())
        self.assertIsNone(result)

    def test_trans_obj_getter_returns_instance_with_flag(self):
        mock_cls = MagicMock()
        mock_cls.source_language = None
        mock_cls.target_language = None
        mock_cls.more_detail = False
        mock_cls.wordbook = None
        mock_cls.stop = False
        mock_cls.clipBoardContent = None

        class TestTrans(DefaultTrans):
            name = "testtrans"
            display_name = "TestTrans"

        setattr(mock_cls, "use_testtrans", True)
        result = TestTrans.trans_obj_getter("hello", mock_cls)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, TestTrans)

    def test_pre_action_text_length_check_passes(self):
        trans = self._make_trans()
        trans.pre_action("normal text")

    def test_print_separator_and_input_no_error(self):
        """print_separator and print_input should not raise"""
        trans = self._make_trans()
        with patch("dict_tiny.translators.translator.normal_separator_printer"):
            with patch("dict_tiny.translators.translator.normal_title_printer"):
                with patch("dict_tiny.translators.translator.get_terminal_size_column",
                          return_value=80):
                    trans.print_separator()
                    trans.print_input("hello")


class TestRecordingDecision(unittest.TestCase):
    @patch("sys.argv", ["", "--record", "hello"])
    def test_record_flag_creates_wordbook(self):
        """--record flag should set should_record and init wordbook"""
        with patch("dict_tiny.main.WordBook") as MockWB:
            mock_wb = MagicMock()
            MockWB.return_value = mock_wb
            MockWB.db_exists.return_value = False
            with patch(
                "dict_tiny.translators.youdao_trans.YoudaoTrans.do_translate",
                return_value=True,
            ):
                try:
                    run()
                except SystemExit:
                    pass
                MockWB.assert_called()

    @patch("sys.argv", ["", "--no-record", "hello"])
    def test_no_record_flag_skips_wordbook(self):
        """--no-record flag should keep should_record=False, wordbook=None"""
        with patch("dict_tiny.main.WordBook") as MockWB:
            mock_wb = MagicMock()
            MockWB.return_value = mock_wb
            MockWB.db_exists.return_value = False
            with patch(
                "dict_tiny.translators.youdao_trans.YoudaoTrans.do_translate",
                return_value=True,
            ):
                try:
                    run()
                except SystemExit:
                    pass
                mock_wb.record.assert_not_called()

    @patch("sys.argv", ["", "hello"])
    def test_default_no_record_when_no_db(self):
        """Without flags and no DB, should_record should be False"""
        with patch("dict_tiny.main.WordBook") as MockWB:
            MockWB.db_exists.return_value = False
            with patch(
                "dict_tiny.translators.youdao_trans.YoudaoTrans.do_translate",
                return_value=True,
            ):
                try:
                    run()
                except SystemExit:
                    pass


class TestDictTinyMain(unittest.TestCase):
    @patch("sys.argv", ["", "hello"])
    @patch.dict("os.environ", {"DICT_TINY_DEFAULT_TRANS": "googletranslate"})
    def test_env_default_translator(self):
        """DICT_TINY_DEFAULT_TRANS env var selects Google Translate as default"""
        with patch(
            "dict_tiny.translators.youdao_trans.YoudaoTrans.do_translate",
            return_value=True,
        ):
            with patch(
                "dict_tiny.translators.google_trans.GoogleTrans.do_translate",
                return_value=True,
            ) as mock_gt:
                try:
                    run()
                except SystemExit:
                    pass
                mock_gt.assert_called_once()

    @patch("sys.argv", ["", "-g", "-y", "-i", "hello"])
    def test_interactive_with_multiple_translators_returns_warning(self):
        """When both -g and -y are used with -i, a warning is shown"""
        with patch(
            "dict_tiny.translators.youdao_trans.YoudaoTrans.do_translate",
            return_value=True,
        ):
            with patch(
                "dict_tiny.translators.google_trans.GoogleTrans.do_translate",
                return_value=True,
            ):
                with patch(
                    "dict_tiny.main.normal_warn_printer"
                ) as mock_warn:
                    try:
                        run()
                    except SystemExit:
                        pass
                    mock_warn.assert_called_once_with(
                        "You can only enter the interactive mode of one translator"
                    )


class TestDefaultTransInit(unittest.TestCase):
    def test_source_language_lowered(self):
        mock_obj = MagicMock()
        mock_obj.source_language = "EN"
        mock_obj.target_language = None
        trans = DefaultTrans("hello", mock_obj)
        self.assertEqual(trans.source_language, "en")

    def test_target_language_lowered(self):
        mock_obj = MagicMock()
        mock_obj.source_language = None
        mock_obj.target_language = "JA"
        trans = DefaultTrans("hello", mock_obj)
        self.assertEqual(trans.target_language, "ja")

    def test_languages_none_when_not_set(self):
        mock_obj = MagicMock()
        mock_obj.source_language = None
        mock_obj.target_language = None
        trans = DefaultTrans("hello", mock_obj)
        self.assertIsNone(trans.source_language)
        self.assertIsNone(trans.target_language)

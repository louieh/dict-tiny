from unittest.mock import MagicMock, patch

import pytest

from dict_tiny.config import MAX_TEXT_LENGTH, ISO639LCodes
from dict_tiny.errors import TextInputError
from dict_tiny.main import run
from dict_tiny.translators import _ALL_TRANSLATORS
from dict_tiny.translators.translator import DefaultTrans

# ── Config & Init ──────────────────────────────────────────


class TestCliInit:
    """CLI basic configuration and initialization tests."""

    def test_has_all_translators(self):
        assert "youdaodict" in _ALL_TRANSLATORS
        assert "googletranslate" in _ALL_TRANSLATORS

    def test_default_translator_is_youdao(self):
        from dict_tiny.translators import DEFAULT_TRANSLATOR

        assert DEFAULT_TRANSLATOR.__name__ == "YoudaoTrans"

    def test_translator_list_matches_config(self):
        assert len(_ALL_TRANSLATORS) == 2

    def test_iso_codes(self):
        assert ISO639LCodes.Chinese.value == "zh"
        assert ISO639LCodes.English.value == "en"
        assert ISO639LCodes.French.value == "fr"
        assert ISO639LCodes.Japanese.value == "ja"
        assert ISO639LCodes.Korean.value == "ko"

    def test_source_language_lowered(self):
        """DefaultTrans lowercases source_language on init."""
        mock_obj = MagicMock()
        mock_obj.source_language = "EN"
        mock_obj.target_language = None
        trans = DefaultTrans("hello", mock_obj)
        assert trans.source_language == "en"

    def test_target_language_lowered(self):
        """DefaultTrans lowercases target_language on init."""
        mock_obj = MagicMock()
        mock_obj.source_language = None
        mock_obj.target_language = "JA"
        trans = DefaultTrans("hello", mock_obj)
        assert trans.target_language == "ja"

    def test_languages_none_when_not_set(self):
        """DefaultTrans leaves languages as None when not provided."""
        mock_obj = MagicMock()
        mock_obj.source_language = None
        mock_obj.target_language = None
        trans = DefaultTrans("hello", mock_obj)
        assert trans.source_language is None
        assert trans.target_language is None


# ── Text Validation ────────────────────────────────────────


class TestTextLengthLimit:
    """pre_action text length validation (shared across all translators)."""

    @pytest.fixture(autouse=True)
    def _setup(self):
        self.mock_obj = MagicMock()
        self.mock_obj.source_language = None
        self.mock_obj.target_language = None

    def test_normal_text_passes(self):
        trans = DefaultTrans("hello", self.mock_obj)
        trans.pre_action("hello")

    def test_exact_limit_passes(self):
        text = "a" * MAX_TEXT_LENGTH
        trans = DefaultTrans(text, self.mock_obj)
        trans.pre_action(text)

    def test_oversized_text_raises(self):
        text = "a" * (MAX_TEXT_LENGTH + 1)
        trans = DefaultTrans(text, self.mock_obj)
        with pytest.raises(TextInputError):
            trans.pre_action(text)

    def test_chinese_oversized_text_raises(self):
        text = "中" * (MAX_TEXT_LENGTH + 1)
        trans = DefaultTrans(text, self.mock_obj)
        with pytest.raises(TextInputError):
            trans.pre_action(text)


# ── Translator Methods ─────────────────────────────────────


class TestTranslateErrorHandling:
    """translate(), extra_action, trans_obj_getter, and print helpers."""

    @pytest.fixture(autouse=True)
    def _setup(self):
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

    # ── translate() ────────────────────────────────────────

    def test_translate_returns_false_on_custom_exception(self):
        trans = self._make_trans()
        with patch.object(
            trans, "do_translate", side_effect=TextInputError("too long")
        ):
            result = trans.translate()
        assert not result

    def test_translate_returns_false_on_not_implemented(self):
        trans = self._make_trans()
        with patch.object(trans, "do_translate", side_effect=NotImplementedError):
            result = trans.translate()
        assert not result

    def test_translate_returns_false_on_generic_exception(self):
        trans = self._make_trans()
        with patch.object(
            trans, "do_translate", side_effect=RuntimeError("network error")
        ):
            result = trans.translate()
        assert not result

    def test_translate_skips_extra_action_on_false(self):
        """When do_translate returns False, extra_action is not called."""
        trans = self._make_trans()
        with patch.object(trans, "do_translate", return_value=False):
            with patch.object(trans, "extra_action") as mock_ea:
                result = trans.translate()
        assert not result
        mock_ea.assert_not_called()

    def test_translate_calls_extra_action_on_true(self):
        """When do_translate returns True, extra_action is called with the text."""
        trans = self._make_trans()
        with patch.object(trans, "do_translate", return_value=True):
            with patch.object(trans, "extra_action") as mock_ea:
                result = trans.translate()
        assert result
        mock_ea.assert_called_once_with("hello")

    # ── extra_action() ─────────────────────────────────────

    def test_extra_action_no_wordbook(self):
        """extra_action does not crash when wordbook is None."""
        self.mock_obj.wordbook = None
        trans = self._make_trans()
        trans.extra_action("hello")

    def test_extra_action_with_wordbook_records(self):
        """extra_action records to wordbook when available."""
        mock_wb = MagicMock()
        self.mock_obj.wordbook = mock_wb
        trans = self._make_trans()
        trans.extra_action("hello")
        mock_wb.record.assert_called_once_with("hello", None, None, "test")

    # ── trans_obj_getter() ─────────────────────────────────

    def test_trans_obj_getter_returns_none_without_flag(self):
        """Without the use_<name> flag, trans_obj_getter returns None."""

        class MockNoFlag:
            source_language = None
            target_language = None

        trans_cls = type("FakeTrans", (DefaultTrans,), {"name": "faketrans"})
        result = trans_cls.trans_obj_getter("hello", MockNoFlag())
        assert result is None

    def test_trans_obj_getter_returns_instance_with_flag(self):
        """With the use_<name> flag, trans_obj_getter returns a translator instance."""
        mock_cls = MagicMock()
        mock_cls.source_language = None
        mock_cls.target_language = None
        setattr(mock_cls, "use_testtrans", True)

        class TestTrans(DefaultTrans):
            name = "testtrans"
            display_name = "TestTrans"

        result = TestTrans.trans_obj_getter("hello", mock_cls)
        assert result is not None
        assert isinstance(result, TestTrans)

    # ── Output helpers ─────────────────────────────────────

    def test_print_separator_and_input_no_error(self):
        """print_separator and print_input do not raise."""
        trans = self._make_trans()
        with patch("dict_tiny.translators.translator.normal_separator_printer"):
            with patch("dict_tiny.translators.translator.normal_title_printer"):
                with patch(
                    "dict_tiny.translators.translator.get_terminal_size_column",
                    return_value=80,
                ):
                    trans.print_separator()
                    trans.print_input("hello")


# ── CLI: Wordbook Recording ────────────────────────────────


class TestRecordingDecision:
    """--record / --no-record flags and wordbook creation behavior."""

    @patch("sys.argv", ["", "--record", "hello"])
    def test_record_flag_creates_wordbook(self):
        """--record flag triggers WordBook initialization."""
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
        """--no-record flag keeps wordbook=None and does not record."""
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
        """Without --record and no existing DB, recording is skipped."""
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

    @patch("sys.argv", ["", "--record", "hello"])
    def test_get_wordbook_failure_handled(self):
        """When WordBook init fails, error is printed and flow continues."""
        with patch("dict_tiny.main.WordBook") as MockWB:
            MockWB.db_exists.return_value = True
            MockWB.side_effect = Exception("db locked")
            with patch("dict_tiny.main.normal_error_printer") as mock_err:
                with patch(
                    "dict_tiny.translators.youdao_trans.YoudaoTrans.do_translate",
                    return_value=True,
                ):
                    try:
                        run()
                    except SystemExit:
                        pass
                    mock_err.assert_called()


# ── CLI: Environment Variables ─────────────────────────────


class TestEnvLanguageVars:
    """Environment variable overrides for language and default translator.
    Note: plumbum.local.env snapshots os.environ at import time,
    so we patch plumbum.local.env directly rather than os.environ.
    """

    def _capture_init(self):
        """Monkey-patch YoudaoTrans.__init__ to capture created instances."""
        from dict_tiny.translators.youdao_trans import YoudaoTrans

        captured = []
        orig_init = YoudaoTrans.__init__

        def new_init(self, text, dto):
            orig_init(self, text, dto)
            captured.append(self)

        YoudaoTrans.__init__ = new_init
        return captured, orig_init, YoudaoTrans

    @patch("sys.argv", ["", "-y", "hello"])
    def test_env_target_language(self):
        """DICT_TINY_TARGET_LAN sets the target language."""
        from plumbum import local

        with local.env(DICT_TINY_TARGET_LAN="ja"):
            captured, orig_init, YoudaoTrans = self._capture_init()
            with patch.object(YoudaoTrans, "do_translate", return_value=True):
                try:
                    run()
                except SystemExit:
                    pass
                assert len(captured) == 1
                assert captured[0].target_language == "ja"
            YoudaoTrans.__init__ = orig_init

    @patch("sys.argv", ["", "-y", "hello"])
    def test_env_source_language(self):
        """DICT_TINY_SOURCE_LAN sets the source language."""
        from plumbum import local

        with local.env(DICT_TINY_SOURCE_LAN="fr"):
            captured, orig_init, YoudaoTrans = self._capture_init()
            with patch.object(YoudaoTrans, "do_translate", return_value=True):
                try:
                    run()
                except SystemExit:
                    pass
                assert len(captured) == 1
                assert captured[0].source_language == "fr"
            YoudaoTrans.__init__ = orig_init

    @patch("sys.argv", ["", "-y", "--target-language", "ko", "hello"])
    def test_cli_flag_overrides_env(self):
        """CLI --target-language flag takes precedence over environment variable."""
        from plumbum import local

        with local.env(DICT_TINY_TARGET_LAN="ja"):
            captured, orig_init, YoudaoTrans = self._capture_init()
            with patch.object(YoudaoTrans, "do_translate", return_value=True):
                try:
                    run()
                except SystemExit:
                    pass
                assert len(captured) == 1
                assert captured[0].target_language == "ko"
            YoudaoTrans.__init__ = orig_init

    @patch("sys.argv", ["", "hello"])
    @patch.dict("os.environ", {"DICT_TINY_DEFAULT_TRANS": "googletranslate"})
    def test_env_default_translator(self):
        """DICT_TINY_DEFAULT_TRANS env var selects Google Translate as default."""
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


# ── CLI: Multiple Translators ─────────────────────────────


class TestMultipleTranslators:
    """Behavior when multiple translators (-y and -g) are specified."""

    @patch("sys.argv", ["", "-y", "-g", "hello"])
    def test_both_translators_run_non_interactive(self):
        """Without -i, both -y and -g translators run sequentially."""
        with patch(
            "dict_tiny.translators.youdao_trans.YoudaoTrans.do_translate",
            return_value=True,
        ) as mock_yd:
            with patch(
                "dict_tiny.translators.google_trans.GoogleTrans.do_translate",
                return_value=True,
            ) as mock_gt:
                with patch("dict_tiny.main.WordBook") as MockWB:
                    MockWB.db_exists.return_value = False
                    try:
                        run()
                    except SystemExit:
                        pass
                    mock_yd.assert_called_once()
                    mock_gt.assert_called_once()

    @patch("sys.argv", ["", "-g", "-y", "-i", "hello"])
    def test_interactive_with_multiple_translators_returns_warning(self):
        """When both -g and -y are used with -i, a warning is shown."""
        with patch(
            "dict_tiny.translators.youdao_trans.YoudaoTrans.do_translate",
            return_value=True,
        ):
            with patch(
                "dict_tiny.translators.google_trans.GoogleTrans.do_translate",
                return_value=True,
            ):
                with patch("dict_tiny.main.normal_warn_printer") as mock_warn:
                    try:
                        run()
                    except SystemExit:
                        pass
                    mock_warn.assert_called_once_with(
                        "You can only enter the interactive mode of one translator"
                    )


# ── CLI: Clipboard ─────────────────────────────────────────


class TestClipboardFlow:
    """Clipboard input (-c) behavior: error handling, input source, and formatting."""

    @patch("sys.argv", ["", "-c", "-y"])
    def test_clipboard_no_content_warns(self):
        """-c with empty clipboard shows warning and exits."""
        with patch("pyperclip.paste", return_value=""):
            with patch(
                "dict_tiny.translators.translator.normal_warn_printer"
            ) as mock_warn:
                try:
                    run()
                except SystemExit:
                    pass
                mock_warn.assert_called_once_with(
                    "There is no content in the clipboard."
                )

    @patch("sys.argv", ["", "-c", "-y"])
    def test_clipboard_error_stops_app(self):
        """If pyperclip fails, app stops with error message."""
        with patch("pyperclip.paste", side_effect=Exception("no clipboard")):
            with patch(
                "dict_tiny.translators.translator.normal_error_printer"
            ) as mock_err:
                try:
                    run()
                except SystemExit:
                    pass
                mock_err.assert_called_once_with(
                    "[Error!] Cannot get clipboard content."
                )

    @patch("sys.argv", ["", "-c", "-y", "hello"])
    def test_clipboard_with_content_uses_it(self):
        """When both clipboard and word arg exist, word arg takes precedence."""
        with patch("pyperclip.paste", return_value="clipboard_word"):
            with patch(
                "dict_tiny.translators.youdao_trans.YoudaoTrans.do_translate",
                return_value=True,
            ) as mock_dt:
                with patch("dict_tiny.main.WordBook") as MockWB:
                    MockWB.db_exists.return_value = False
                    try:
                        run()
                    except SystemExit:
                        pass
                    mock_dt.assert_called_once()
                    assert mock_dt.call_args[0][0] == "hello"

    @patch("sys.argv", ["", "-c", "-y"])
    def test_clipboard_used_when_no_word_arg(self):
        """When no word arg, clipboard content is used as input."""
        with patch("pyperclip.paste", return_value="clipword"):
            with patch(
                "dict_tiny.translators.youdao_trans.YoudaoTrans.do_translate",
                return_value=True,
            ) as mock_dt:
                with patch("dict_tiny.main.WordBook") as MockWB:
                    MockWB.db_exists.return_value = False
                    try:
                        run()
                    except SystemExit:
                        pass
                    mock_dt.assert_called_once()
                    assert mock_dt.call_args[0][0] == "clipword"

    @patch("sys.argv", ["", "-c", "-y"])
    def test_clipboard_strips_newlines(self):
        """Clipboard content has leading/trailing whitespace and newlines stripped."""
        with patch("pyperclip.paste", return_value="  hello\nworld  "):
            with patch(
                "dict_tiny.translators.youdao_trans.YoudaoTrans.do_translate",
                return_value=True,
            ) as mock_dt:
                with patch("dict_tiny.main.WordBook") as MockWB:
                    MockWB.db_exists.return_value = False
                    try:
                        run()
                    except SystemExit:
                        pass
                    mock_dt.assert_called_once()
                    arg = mock_dt.call_args[0][0]
                    assert "hello" in arg
                    assert "world" in arg


# ── CLI: Edge Cases ────────────────────────────────────────


class TestNoInputShowsHelp:
    """Behavior when no input is provided (no args, no clipboard, no -i)."""

    @patch("sys.argv", [""])
    def test_no_args_no_clipboard_does_not_crash(self):
        """With no text and no -i, app shows help and exits without crash."""
        with patch("dict_tiny.main.WordBook") as MockWB:
            MockWB.db_exists.return_value = False
            try:
                run()
            except SystemExit:
                pass
            except Exception as e:
                pytest.fail(f"Unexpected exception: {e}")


# ── Interactive Loop ───────────────────────────────────────


class TestInteractiveLoop:
    """Interactive mode (-i) prompt loop behavior."""

    def _make_trans(self):
        mock_obj = MagicMock()
        mock_obj.source_language = None
        mock_obj.target_language = None
        mock_obj.wordbook = None
        trans = DefaultTrans("hello", mock_obj)
        trans.name = "test"
        trans.display_name = "TestTrans"
        return trans

    def test_keyboard_interrupt_does_not_exit(self):
        """Ctrl-C prints info and continues, does not break the loop."""
        trans = self._make_trans()
        session = MagicMock()
        session.prompt.side_effect = [KeyboardInterrupt(), EOFError()]
        with patch.object(trans, "pre_action") as mock_pre:
            with patch.object(trans, "do_translate") as mock_dt:
                with patch.object(trans, "extra_action"):
                    with patch(
                        "dict_tiny.translators.translator.normal_info_printer"
                    ) as mock_info:
                        trans.interactive_loop(session)
                        info_calls = [str(c) for c in mock_info.call_args_list]
                        assert any("Ctrl-D" in c for c in info_calls)

    def test_eof_exits_loop(self):
        """Ctrl-D (EOF) exits the loop and prints GoodBye."""
        trans = self._make_trans()
        session = MagicMock()
        session.prompt.side_effect = EOFError()
        with patch("builtins.print") as mock_print:
            trans.interactive_loop(session)
            mock_print.assert_called_once_with("GoodBye!")

    def test_empty_input_continues_loop(self):
        """Empty input skips translate and continues the loop."""
        trans = self._make_trans()
        session = MagicMock()
        session.prompt.side_effect = ["", EOFError()]
        with patch.object(trans, "pre_action") as mock_pre:
            with patch.object(trans, "do_translate") as mock_dt:
                trans.interactive_loop(session)
                mock_pre.assert_not_called()
                mock_dt.assert_not_called()

    def test_successful_translate_calls_extra_action(self):
        """After successful translate, extra_action is called."""
        trans = self._make_trans()
        session = MagicMock()
        session.prompt.side_effect = ["hello", EOFError()]
        with patch.object(trans, "pre_action"):
            with patch.object(trans, "do_translate", return_value=True):
                with patch.object(trans, "extra_action") as mock_ea:
                    trans.interactive_loop(session)
                    mock_ea.assert_called_once_with("hello")

    def test_failed_translate_skips_extra_action(self):
        """When translate returns False, extra_action is not called."""
        trans = self._make_trans()
        session = MagicMock()
        session.prompt.side_effect = ["hello", EOFError()]
        with patch.object(trans, "pre_action"):
            with patch.object(trans, "do_translate", return_value=False):
                with patch.object(trans, "extra_action") as mock_ea:
                    trans.interactive_loop(session)
                    mock_ea.assert_not_called()

    def test_custom_exception_prints_error_continues_loop(self):
        """CustomException prints the error and continues the loop."""
        trans = self._make_trans()
        session = MagicMock()
        session.prompt.side_effect = ["hello", EOFError()]
        with patch.object(trans, "pre_action", side_effect=TextInputError("too long")):
            with patch.object(trans, "do_translate") as mock_dt:
                with patch(
                    "dict_tiny.translators.translator.normal_error_printer"
                ) as mock_err:
                    trans.interactive_loop(session)
                    mock_err.assert_called_once_with("too long")
                    mock_dt.assert_not_called()

    def test_generic_exception_continues_loop(self):
        """Generic exceptions (e.g. RuntimeError) are caught silently, loop continues."""
        trans = self._make_trans()
        session = MagicMock()
        session.prompt.side_effect = ["hello", EOFError()]
        with patch.object(trans, "pre_action"):
            with patch.object(
                trans, "do_translate", side_effect=RuntimeError("net error")
            ):
                with patch("builtins.print") as mock_print:
                    trans.interactive_loop(session)
                    mock_print.assert_any_call("GoodBye!")


# ── Integration Tests ──────────────────────────────────────


class TestCliIntegration:
    """Smoke tests that call real APIs (no mocking)."""

    @patch("sys.argv", ["", "-y", "book"])
    def test_cli_youdao_translate(self):
        try:
            run()
        except SystemExit:
            pass
        except Exception as e:
            pytest.fail(f"Unexpected exception: {e}")

    @patch("sys.argv", ["", "-y", "book", "--target-language", "ja"])
    def test_cli_youdao_japanese(self):
        try:
            run()
        except SystemExit:
            pass
        except Exception as e:
            pytest.fail(f"Unexpected exception: {e}")

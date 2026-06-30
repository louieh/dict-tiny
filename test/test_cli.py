from test.helpers import make_trans, run_cli
from unittest.mock import MagicMock, patch

from dict_tiny.config import ISO639LCodes
from dict_tiny.errors import TextInputError
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
                run_cli()
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
                run_cli()
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
                run_cli()
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
                    run_cli()
                    mock_err.assert_called()


# ── CLI: Environment Variables ─────────────────────────────


class TestEnvLanguageVars:
    """Environment variable overrides for language and default translator.
    Note: plumbum.local.env snapshots os.environ at import time,
    so we patch plumbum.local.env directly rather than os.environ.
    """

    def _capture_init(self):
        """Return a context manager that captures YoudaoTrans instances during init."""
        from unittest.mock import patch

        from dict_tiny.translators.youdao_trans import YoudaoTrans

        captured = []
        orig_init = YoudaoTrans.__init__

        def capture_side_effect(self_inst, text, dto):
            orig_init(self_inst, text, dto)
            captured.append(self_inst)

        return (
            patch.object(YoudaoTrans, "__init__", new=capture_side_effect),
            captured,
            YoudaoTrans,
        )

    @patch("sys.argv", ["", "-y", "hello"])
    def test_env_target_language(self):
        """DICT_TINY_TARGET_LAN sets the target language."""
        from plumbum import local

        with local.env(DICT_TINY_TARGET_LAN="ja"):
            patcher, captured, YoudaoTrans = self._capture_init()
            with patcher:
                with patch.object(YoudaoTrans, "do_translate", return_value=True):
                    run_cli()
                    assert len(captured) == 1
                    assert captured[0].target_language == "ja"

    @patch("sys.argv", ["", "-y", "hello"])
    def test_env_source_language(self):
        """DICT_TINY_SOURCE_LAN sets the source language."""
        from plumbum import local

        with local.env(DICT_TINY_SOURCE_LAN="fr"):
            patcher, captured, YoudaoTrans = self._capture_init()
            with patcher:
                with patch.object(YoudaoTrans, "do_translate", return_value=True):
                    run_cli()
                    assert len(captured) == 1
                    assert captured[0].source_language == "fr"

    @patch("sys.argv", ["", "-y", "--target-language", "ko", "hello"])
    def test_cli_flag_overrides_env(self):
        """CLI --target-language flag takes precedence over environment variable."""
        from plumbum import local

        with local.env(DICT_TINY_TARGET_LAN="ja"):
            patcher, captured, YoudaoTrans = self._capture_init()
            with patcher:
                with patch.object(YoudaoTrans, "do_translate", return_value=True):
                    run_cli()
                    assert len(captured) == 1
                    assert captured[0].target_language == "ko"

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
                run_cli()
                mock_gt.assert_called_once()

    @patch("sys.argv", ["", "hello"])
    @patch.dict("os.environ", {"DICT_TINY_DEFAULT_TRANS": "invalid_translator"})
    def test_env_default_translator_invalid_falls_back_to_youdao(self):
        """Invalid DICT_TINY_DEFAULT_TRANS value falls back to Youdao (DEFAULT_TRANSLATOR)."""
        with patch("dict_tiny.main.WordBook") as MockWB:
            MockWB.db_exists.return_value = False
            with patch(
                "dict_tiny.translators.youdao_trans.YoudaoTrans.do_translate",
                return_value=True,
            ) as mock_yd:
                with patch(
                    "dict_tiny.translators.google_trans.GoogleTrans.do_translate",
                    return_value=True,
                ):
                    run_cli()
                    mock_yd.assert_called_once()


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
                    run_cli()
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
                    run_cli()
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
                run_cli()
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
                run_cli()
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
                    run_cli()
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
                    run_cli()
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
                    run_cli()
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
            run_cli()


# ── Interactive Loop ───────────────────────────────────────


class TestInteractiveLoop:
    """Interactive mode (-i) prompt loop behavior."""

    def test_keyboard_interrupt_does_not_exit(self):
        """Ctrl-C prints info and continues, does not break the loop."""
        trans = make_trans()
        session = MagicMock()
        session.prompt.side_effect = [KeyboardInterrupt(), EOFError()]
        with patch.object(trans, "pre_action"):
            with patch.object(trans, "do_translate"):
                with patch.object(trans, "extra_action"):
                    with patch(
                        "dict_tiny.translators.translator.normal_info_printer"
                    ) as mock_info:
                        trans.interactive_loop(session)
                        info_calls = [str(c) for c in mock_info.call_args_list]
                        assert any("Ctrl-D" in c for c in info_calls)

    def test_eof_exits_loop(self):
        """Ctrl-D (EOF) exits the loop and prints GoodBye."""
        trans = make_trans()
        session = MagicMock()
        session.prompt.side_effect = EOFError()
        with patch("builtins.print") as mock_print:
            trans.interactive_loop(session)
            mock_print.assert_called_once_with("GoodBye!")

    def test_empty_input_continues_loop(self):
        """Empty input skips translate and continues the loop."""
        trans = make_trans()
        session = MagicMock()
        session.prompt.side_effect = ["", EOFError()]
        with patch.object(trans, "pre_action") as mock_pre:
            with patch.object(trans, "do_translate") as mock_dt:
                trans.interactive_loop(session)
                mock_pre.assert_not_called()
                mock_dt.assert_not_called()

    def test_successful_translate_calls_extra_action(self):
        """After successful translate, extra_action is called."""
        trans = make_trans()
        session = MagicMock()
        session.prompt.side_effect = ["hello", EOFError()]
        with patch.object(trans, "pre_action"):
            with patch.object(trans, "do_translate", return_value=True):
                with patch.object(trans, "extra_action") as mock_ea:
                    trans.interactive_loop(session)
                    mock_ea.assert_called_once_with("hello")

    def test_failed_translate_skips_extra_action(self):
        """When translate returns False, extra_action is not called."""
        trans = make_trans()
        session = MagicMock()
        session.prompt.side_effect = ["hello", EOFError()]
        with patch.object(trans, "pre_action"):
            with patch.object(trans, "do_translate", return_value=False):
                with patch.object(trans, "extra_action") as mock_ea:
                    trans.interactive_loop(session)
                    mock_ea.assert_not_called()

    def test_custom_exception_prints_error_continues_loop(self):
        """CustomException prints the error and continues the loop."""
        trans = make_trans()
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
        trans = make_trans()
        session = MagicMock()
        session.prompt.side_effect = ["hello", EOFError()]
        with patch.object(trans, "pre_action"):
            with patch.object(
                trans, "do_translate", side_effect=RuntimeError("net error")
            ):
                with patch("builtins.print") as mock_print:
                    trans.interactive_loop(session)
                    mock_print.assert_any_call("GoodBye!")


# ── Interactive: get_prompt_session & interactive ──────────


class TestGetPromptSession:
    """get_prompt_session() and interactive() entry point."""

    def test_get_prompt_session_creates_session(self):
        """get_prompt_session returns a PromptSession with completer."""
        trans = make_trans()
        with patch("prompt_toolkit.PromptSession") as MockPS:
            with patch("dict_tiny.translators.translator.normal_separator_printer"):
                with patch("dict_tiny.translators.translator.normal_info_printer"):
                    with patch("dict_tiny.completer.YoudaoCompleter"):
                        trans.get_prompt_session()
                        MockPS.assert_called_once()
                        _, kwargs = MockPS.call_args
                        assert "completer" in kwargs
                        assert kwargs["complete_while_typing"] is False
                        assert kwargs["complete_in_thread"] is True

    def test_get_prompt_session_parses_le(self):
        """get_prompt_session uses parse_le for completer language."""
        trans = make_trans(source_language="en", target_language="ja")
        with patch("dict_tiny.completer.YoudaoCompleter") as MockComp:
            with patch("dict_tiny.translators.translator.normal_separator_printer"):
                with patch("dict_tiny.translators.translator.normal_info_printer"):
                    with patch("prompt_toolkit.PromptSession"):
                        trans.get_prompt_session()
                        MockComp.assert_called_once_with("en")

    def test_interactive_calls_get_prompt_session_and_loop(self):
        """interactive() calls get_prompt_session then interactive_loop."""
        trans = make_trans()
        mock_session = MagicMock()
        with patch.object(
            trans, "get_prompt_session", return_value=mock_session
        ) as mock_gps:
            with patch.object(trans, "interactive_loop") as mock_loop:
                trans.interactive()
                mock_gps.assert_called_once()
                mock_loop.assert_called_once_with(mock_session)


# ── CLI: translator init exceptions ────────────────────────


class TestTranslatorInitErrors:
    """Exception handling during translator initialization in main()."""

    @patch("sys.argv", ["", "hello"])
    def test_custom_exception_on_translator_init(self):
        """CustomException during translator init prints error and returns."""
        from dict_tiny.errors import CustomException

        with patch("dict_tiny.main.WordBook") as MockWB:
            MockWB.db_exists.return_value = False
            with patch(
                "dict_tiny.translators.google_trans.GoogleTrans.trans_obj_getter",
                side_effect=CustomException("bad param"),
            ):
                with patch("dict_tiny.main.normal_error_printer") as mock_err:
                    run_cli()
                    mock_err.assert_called_once_with("bad param")

    @patch("sys.argv", ["", "hello"])
    def test_generic_exception_on_translator_init(self):
        """Generic Exception during translator init prints error and returns."""
        with patch("dict_tiny.main.WordBook") as MockWB:
            MockWB.db_exists.return_value = False
            with patch(
                "dict_tiny.translators.google_trans.GoogleTrans.trans_obj_getter",
                side_effect=RuntimeError("init failed"),
            ):
                with patch("dict_tiny.main.normal_error_printer") as mock_err:
                    run_cli()
                    error_msg = mock_err.call_args[0][0]
                    assert "init failed" in error_msg

    @patch("sys.argv", ["", "-i", "--record", "hello"])
    def test_interactive_mode_closes_wordbook(self):
        """In interactive mode, wordbook is closed after the loop."""
        with patch("dict_tiny.main.WordBook") as MockWB:
            mock_wb = MagicMock()
            MockWB.return_value = mock_wb
            MockWB.db_exists.return_value = False
            with patch(
                "dict_tiny.translators.youdao_trans.YoudaoTrans.do_translate",
                return_value=True,
            ):
                run_cli()
                mock_wb.close.assert_called()


# ── CLI: subcommand path ───────────────────────────────────


class TestSubcommandPath:
    """main() behavior when nested_command is set."""

    @patch("sys.argv", ["", "wb", "list"])
    def test_nested_command_closes_wordbook_and_returns(self):
        """When nested_command is set, wordbook is closed and main returns early."""
        with patch("dict_tiny.main.WordBook") as MockWB:
            mock_wb = MagicMock()
            MockWB.return_value = mock_wb
            MockWB.db_exists.return_value = True
            with patch.object(mock_wb, "get_default_record", return_value=True):
                run_cli()
                mock_wb.close.assert_called_once()

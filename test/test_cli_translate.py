from test.helpers import make_trans
from unittest.mock import MagicMock, patch

import pytest

from dict_tiny.config import MAX_TEXT_LENGTH
from dict_tiny.errors import TextInputError
from dict_tiny.translators.translator import DefaultTrans


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


class TestTranslateErrorHandling:
    """translate(), extra_action, trans_obj_getter, and print helpers."""

    # ── translate() ────────────────────────────────────────

    def test_translate_returns_false_on_custom_exception(self):
        trans = make_trans()
        with patch.object(
            trans, "do_translate", side_effect=TextInputError("too long")
        ):
            result = trans.translate()
        assert not result

    def test_translate_returns_false_on_not_implemented(self):
        trans = make_trans()
        with patch.object(trans, "do_translate", side_effect=NotImplementedError):
            result = trans.translate()
        assert not result

    def test_translate_returns_false_on_generic_exception(self):
        trans = make_trans()
        with patch.object(
            trans, "do_translate", side_effect=RuntimeError("network error")
        ):
            result = trans.translate()
        assert not result

    def test_translate_skips_extra_action_on_false(self):
        """When do_translate returns False, extra_action is not called."""
        trans = make_trans()
        with patch.object(trans, "do_translate", return_value=False):
            with patch.object(trans, "extra_action") as mock_ea:
                result = trans.translate()
        assert not result
        mock_ea.assert_not_called()

    def test_translate_calls_extra_action_on_true(self):
        """When do_translate returns True, extra_action is called with the text."""
        trans = make_trans()
        with patch.object(trans, "do_translate", return_value=True):
            with patch.object(trans, "extra_action") as mock_ea:
                result = trans.translate()
        assert result
        mock_ea.assert_called_once_with("hello")

    # ── extra_action() ─────────────────────────────────────

    def test_extra_action_no_wordbook(self):
        """extra_action does not crash when wordbook is None."""
        trans = make_trans()
        trans.extra_action("hello")

    def test_extra_action_with_wordbook_records(self):
        """extra_action records to wordbook when available."""
        mock_wb = MagicMock()
        trans = make_trans()
        trans.dict_tiny_obj.wordbook = mock_wb
        trans.dict_tiny_obj.should_record = True
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
        trans = make_trans()
        with patch("dict_tiny.translators.translator.normal_separator_printer"):
            with patch("dict_tiny.translators.translator.normal_title_printer"):
                with patch(
                    "dict_tiny.translators.translator.get_terminal_size_column",
                    return_value=80,
                ):
                    trans.print_separator()
                    trans.print_input("hello")

    def test_print_input_truncated_when_longer_than_terminal(self):
        """print_input truncates the separator line when text exceeds terminal width."""
        trans = make_trans()
        with patch("dict_tiny.translators.translator.normal_title_printer") as mock_p:
            with patch(
                "dict_tiny.translators.translator.get_terminal_size_column",
                return_value=20,
            ):
                trans.print_input("A" * 50)
                called_arg = mock_p.call_args[0][0]
                assert len(called_arg) <= 20

"""Tests for _render_table in wordbook_cli.py."""

from test.helpers import _entry

from dict_tiny.wordbook_cli import _render_table


class TestRenderTable:
    """_render_table rendering paths."""

    def test_render_basic(self):
        """Renders a table with basic entry."""
        entries = [_entry()]
        table = _render_table(entries, 1, 20, 1, caption=None)
        assert table is not None
        assert len(table.rows) == 1

    def test_render_empty(self):
        """Renders a table with no entries."""
        table = _render_table([], 1, 20, 0, caption=None)
        assert table is not None
        assert len(table.rows) == 0

    def test_render_google_translator_no_target_language(self):
        """Google Translate defaults target language to 'en' when not set."""
        entries = [
            _entry(
                translator="googletranslate",
                source_language="zh",
                target_language=None,
            )
        ]
        table = _render_table(entries, 1, 20, 1, caption=None)
        assert table is not None

    def test_render_youdao_no_languages(self):
        """Youdao translator with no languages shows zh↔en."""
        entries = [
            _entry(
                translator="youdaodict",
                source_language=None,
                target_language=None,
            )
        ]
        table = _render_table(entries, 1, 20, 1, caption=None)
        assert table is not None

    def test_render_no_languages_no_translator(self):
        """No languages and no known translator shows empty lang."""
        entries = [
            _entry(
                translator="unknown",
                source_language=None,
                target_language=None,
            )
        ]
        table = _render_table(entries, 1, 20, 1, caption=None)
        assert table is not None

    def test_render_custom_caption(self):
        """Uses custom caption when provided."""
        entries = [_entry()]
        table = _render_table(entries, 1, 20, 1, caption="Custom caption")
        assert table.caption == "Custom caption"

    def test_render_pagination_caption(self):
        """Generates default pagination caption when no custom caption."""
        entries = [_entry()]
        table = _render_table(entries, 2, 10, 25, caption=None)
        assert "Page 2/3" in table.caption
        assert "25 entries" in table.caption

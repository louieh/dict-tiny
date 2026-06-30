"""Tests for _render_table in wordbook_cli.py."""

from datetime import datetime
from test.helpers import _entry

from dict_tiny.wordbook_cli import _render_table


def _row_cells(table, row_idx):
    """Get cell values from a row across all columns."""
    return [col._cells[row_idx] for col in table.columns]


class TestRenderTable:
    """_render_table rendering paths."""

    def test_render_basic(self):
        """Renders a table with basic entry and correct columns."""
        entries = [_entry()]
        table = _render_table(entries, 1, 20, 1, caption=None)
        assert table is not None
        assert len(table.rows) == 1
        # Verify column headers
        assert [c.header for c in table.columns] == [
            "ID",
            "Text",
            "Lang",
            "Created",
            "Count",
        ]
        # Verify row content
        cells = _row_cells(table, 0)
        assert cells[0] == "1"  # ID
        assert cells[1] == "hello"  # Text

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
        cells = _row_cells(table, 0)
        assert cells[2] == "zh→en"  # Lang defaults to en for google

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
        cells = _row_cells(table, 0)
        assert cells[2] == "zh↔en"

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
        cells = _row_cells(table, 0)
        assert cells[2] == ""  # empty lang

    def test_render_with_both_languages(self):
        """Shows source→target language when both are set."""
        entries = [
            _entry(source_language="en", target_language="zh"),
        ]
        table = _render_table(entries, 1, 20, 1, caption=None)
        cells = _row_cells(table, 0)
        assert cells[2] == "en→zh"

    def test_render_timestamp_format(self):
        """Shows timestamp in YYYY-MM-DD HH:MM format."""
        ts = datetime(2025, 6, 15, 14, 30, 0).timestamp()
        entries = [_entry(timestamp=ts)]
        table = _render_table(entries, 1, 20, 1, caption=None)
        cells = _row_cells(table, 0)
        assert cells[3] == "2025-06-15 14:30"

    def test_render_access_count(self):
        """Shows access count prefixed with ×."""
        entries = [_entry(access_count=5)]
        table = _render_table(entries, 1, 20, 1, caption=None)
        cells = _row_cells(table, 0)
        assert cells[4] == "×5"

    def test_render_multiple_entries(self):
        """Renders multiple entries in correct order."""
        entries = [
            _entry(id=1, text="hello", timestamp=1000.0),
            _entry(id=2, text="world", timestamp=2000.0),
        ]
        table = _render_table(entries, 1, 20, 2, caption=None)
        assert len(table.rows) == 2
        cells_0 = _row_cells(table, 0)
        cells_1 = _row_cells(table, 1)
        assert cells_0[1] == "hello"
        assert cells_1[1] == "world"

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

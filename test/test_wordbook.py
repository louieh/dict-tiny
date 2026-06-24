import os
import shutil
import tempfile
import time
from unittest.mock import MagicMock

import pytest

from dict_tiny.config import MAX_ENTRIES
from dict_tiny.wordbook import WordBook


class TestWordBook:
    """WordBook database operations integration tests."""

    @pytest.fixture(autouse=True)
    def _setup_db(self):
        tmpdir = tempfile.mkdtemp()
        db_path = os.path.join(tmpdir, "test.db")
        wb = WordBook(db_path)
        self.tmpdir = tmpdir
        self.db_path = db_path
        self.wb = wb
        self._wordbooks = [wb]
        yield
        for each in self._wordbooks:
            each.close()
        shutil.rmtree(tmpdir, ignore_errors=True)

    # ── record ────────────────────────────────────────────

    def test_record_new(self):
        """Records a new entry successfully."""
        result = self.wb.record("hello", "en", "zh", "YoudaoDict")
        assert result
        assert self.wb.count() == 1

    def test_record_duplicate(self):
        """Updates existing entry on duplicate record."""
        self.wb.record("hello", "en", "zh", "YoudaoDict")
        self.wb.record("hello", "en", "fr", "GoogleTranslate")
        assert self.wb.count() == 1
        entry = self.wb.get_entry(1)
        assert entry.access_count == 2
        assert entry.translator == "GoogleTranslate"

    def test_record_eviction(self):
        """Evicts least recently accessed entry when at MAX_ENTRIES."""
        for i in range(MAX_ENTRIES):
            self.wb.record(f"word{i}", "en", "zh", "YoudaoDict")
        assert self.wb.count() == MAX_ENTRIES

        self.wb.record("overflow", "en", "zh", "YoudaoDict")
        assert self.wb.count() == MAX_ENTRIES

        entries, _ = self.wb.list_entries(page=1, page_size=MAX_ENTRIES)
        texts = {e.text for e in entries}
        assert "overflow" in texts
        assert "word0" not in texts

    def test_record_resilience(self):
        """Returns False when database is corrupted."""
        self.wb.close()
        with open(self.db_path, "w") as f:
            f.write("garbage")
        wb = WordBook(self.db_path)
        self._wordbooks.append(wb)
        assert wb._conn is None
        result = wb.record("hello", "en", "zh", "YoudaoDict")
        assert not result

    # ── get_entry ─────────────────────────────────────────

    def test_get_entry(self):
        """Returns entry with correct fields."""
        self.wb.record("hello", "en", "zh", "YoudaoDict")
        entry = self.wb.get_entry(1)
        assert entry is not None
        assert entry.text == "hello"
        assert entry.source_language == "en"
        assert entry.target_language == "zh"
        assert entry.translator == "YoudaoDict"
        assert entry.access_count == 1

    def test_get_entry_invalid(self):
        """Returns None for invalid entry IDs."""
        assert self.wb.get_entry(1) is None
        assert self.wb.get_entry(0) is None
        assert self.wb.get_entry(-1) is None

    # ── list_entries ──────────────────────────────────────

    def test_list_default_sort_by_time(self):
        """Defaults to sorting by creation time descending."""
        self.wb.record("first", "en", "zh", "YoudaoDict")
        time.sleep(0.01)
        self.wb.record("second", "en", "zh", "YoudaoDict")
        entries, total = self.wb.list_entries()
        assert total == 2
        assert entries[0].text == "second"
        assert entries[1].text == "first"

    def test_list_sort_freq(self):
        """Sorts by access_count descending."""
        self.wb.record("rare", "en", "zh", "YoudaoDict")
        self.wb.record("freq", "en", "zh", "YoudaoDict")
        self.wb.record("freq", "en", "zh", "YoudaoDict")
        entries, _ = self.wb.list_entries(sort_by="freq")
        assert entries[0].text == "freq"

    def test_list_sort_recent(self):
        """Sorts by last_access descending."""
        self.wb.record("old", "en", "zh", "YoudaoDict")
        time.sleep(0.01)
        self.wb.record("new", "en", "zh", "YoudaoDict")
        self.wb.record("old", "en", "zh", "YoudaoDict")
        entries, _ = self.wb.list_entries(sort_by="recent")
        assert entries[0].text == "old"

    def test_list_pagination(self):
        """Paginates correctly with page and page_size."""
        for i in range(5):
            self.wb.record(f"w{i}", "en", "zh", "YoudaoDict")
        entries, total = self.wb.list_entries(page=2, page_size=3)
        assert total == 5
        assert len(entries) == 2

    def test_list_since(self):
        """Filters entries created after given timestamp."""
        self.wb.record("old", "en", "zh", "YoudaoDict")
        mid = time.time()
        time.sleep(0.01)
        self.wb.record("new", "en", "zh", "YoudaoDict")
        entries, total = self.wb.list_entries(since=mid)
        assert total == 1
        assert entries[0].text == "new"

    # ── search ─────────────────────────────────────────────

    def test_search_fuzzy(self):
        """Returns matching entries with LIKE search."""
        for text in ("hello", "hello_world", "hell", "world"):
            self.wb.record(text, "en", "zh", "YoudaoDict")
        entries, total = self.wb.list_entries(search="hello")
        assert total == 2
        assert {e.text for e in entries} == {"hello", "hello_world"}

    def test_search_exact(self):
        """Returns exact match when exact=True."""
        for text in ("hello", "hello_world"):
            self.wb.record(text, "en", "zh", "YoudaoDict")
        entries, total = self.wb.list_entries(search="hello", exact=True)
        assert total == 1
        assert entries[0].text == "hello"

    def test_search_no_match(self):
        """Returns empty results for non-matching search."""
        self.wb.record("hello", "en", "zh", "YoudaoDict")
        entries, total = self.wb.list_entries(search="zzz_not_there")
        assert total == 0
        assert len(entries) == 0

    def test_search_pagination(self):
        """Paginates search results correctly."""
        for i in range(5):
            self.wb.record(f"hello_{i}", "en", "zh", "YoudaoDict")
        entries, total = self.wb.list_entries(search="hello", page=1, page_size=2)
        assert total == 5
        assert len(entries) == 2

    def test_search_empty_db(self):
        """Returns empty results when database is empty."""
        entries, total = self.wb.list_entries(search="hello")
        assert total == 0
        assert len(entries) == 0

    def test_search_with_since_filter(self):
        """Combines search query with since filter."""
        self.wb.record("old", "en", "zh", "YoudaoDict")
        mid = time.time()
        time.sleep(0.01)
        self.wb.record("hello", "en", "zh", "YoudaoDict")
        entries, total = self.wb.list_entries(search="hello", since=mid)
        assert total == 1
        assert entries[0].text == "hello"

    def test_search_combined_search_and_since_no_match(self):
        """Returns empty when since filter excludes all matches."""
        self.wb.record("hello", "en", "zh", "YoudaoDict")
        future = time.time() + 1000
        entries, total = self.wb.list_entries(search="hello", since=future)
        assert total == 0
        assert len(entries) == 0

    def test_list_invalid_page_returns_empty(self):
        """Returns empty list for invalid page numbers."""
        self.wb.record("hello", "en", "zh", "YoudaoDict")
        entries, total = self.wb.list_entries(page=0)
        assert entries == []
        assert total == 0
        entries, total = self.wb.list_entries(page=-1)
        assert entries == []

    def test_list_invalid_sort_falls_back_to_created(self):
        """Falls back to created sort for unknown sort_by value."""
        self.wb.record("hello", "en", "zh", "YoudaoDict")
        entries, total = self.wb.list_entries(sort_by="invalid_sort")
        assert total == 1
        assert entries[0].text == "hello"

    # ── delete ─────────────────────────────────────────────

    def test_delete(self):
        """Deletes an existing entry."""
        self.wb.record("hello", "en", "zh", "YoudaoDict")
        assert self.wb.delete(1)
        assert self.wb.count() == 0

    def test_delete_invalid(self):
        """Returns False when deleting non-existent entry."""
        assert not self.wb.delete(1)

    def test_delete_then_record_reuses_id(self):
        """Reuses deleted entry ID for new record."""
        self.wb.record("hello", "en", "zh", "YoudaoDict")
        assert self.wb.delete(1)
        assert self.wb.record("world", "en", "zh", "YoudaoDict")
        assert self.wb.count() == 1

    # ── delete_db ──────────────────────────────────────────

    def test_delete_db(self):
        """Deletes the database file and creates a fresh one."""
        self.wb.record("hello", "en", "zh", "YoudaoDict")
        self.wb.delete_db()
        assert not os.path.isfile(self.db_path)
        wb2 = WordBook(self.db_path)
        self._wordbooks.append(wb2)
        assert wb2.count() == 0
        wb2.close()

    def test_delete_db_missing_file_swallows_error(self):
        """Does not raise when database file is already missing."""
        self.wb.close()
        if os.path.isfile(self.db_path):
            os.remove(self.db_path)
        self.wb.delete_db()

    def test_close_idempotent(self):
        """Calling close() multiple times does not raise."""
        self.wb.close()
        self.wb.close()
        assert self.wb._conn is None

    def test_get_entry_after_close_returns_none(self):
        """Returns None when getting entry after close."""
        self.wb.record("hello", "en", "zh", "YoudaoDict")
        self.wb.close()
        assert self.wb.get_entry(1) is None

    def test_count_after_close_returns_zero(self):
        """Returns 0 when counting after close."""
        self.wb.record("hello", "en", "zh", "YoudaoDict")
        self.wb.close()
        assert self.wb.count() == 0

    def test_record_none_conn_returns_false(self):
        """Returns False when recording after close."""
        self.wb.close()
        assert not self.wb.record("hello", "en", "zh", "YoudaoDict")

    def test_set_default_record_none_conn_no_raise(self):
        """Does not raise when setting config after close."""
        self.wb.close()
        self.wb.set_default_record(True)
        assert not self.wb.get_default_record()

    # ── config ─────────────────────────────────────────────

    def test_config_default_record(self):
        """Persists default_record setting across instances."""
        assert not self.wb.get_default_record()
        self.wb.set_default_record(True)
        assert self.wb.get_default_record()
        config = self.wb.get_config()
        assert config["default_record"]

        self.wb.close()
        wb2 = WordBook(self.db_path)
        self._wordbooks.append(wb2)
        assert wb2.get_default_record()
        wb2.set_default_record(False)
        wb2.close()
        wb3 = WordBook(self.db_path)
        self._wordbooks.append(wb3)
        assert not wb3.get_default_record()
        wb3.close()

    # ── db_exists ──────────────────────────────────────────

    def test_db_exists(self):
        """Returns True only if database file exists."""
        path = os.path.join(self.tmpdir, "nonexistent.db")
        assert not WordBook.db_exists(path)
        WordBook(path).close()
        assert WordBook.db_exists(path)
        os.remove(path)

    # ── misc ───────────────────────────────────────────────

    def test_count(self):
        """Returns correct entry count."""
        assert self.wb.count() == 0
        self.wb.record("a", "en", "zh", "YoudaoDict")
        assert self.wb.count() == 1

    def test_get_data_dir(self):
        """Returns data directory path containing 'dict-tiny'."""
        from dict_tiny.util import get_data_dir

        d = get_data_dir()
        assert "dict-tiny" in str(d)


class TestWordBookExtraAction:
    """DefaultTrans.extra_action wordbook recording tests."""

    def test_extra_action_hook(self):
        """Records entry via wordbook when extra_action is called."""
        mock_wb = MagicMock()
        mock_dt = MagicMock()
        mock_dt.wordbook = mock_wb
        mock_dt.source_language = "en"
        mock_dt.target_language = "zh"
        mock_dt.detect_language = False

        from dict_tiny.translators.translator import DefaultTrans

        trans = DefaultTrans("hello", mock_dt)
        trans.name = "YoudaoDict"
        trans.extra_action("hello")

        mock_wb.record.assert_called_once_with("hello", "en", "zh", "YoudaoDict")


class TestWordBookOpen:
    """WordBook.open edge case tests."""

    def test_open_returns_none_on_failure(self):
        """Returns None when database cannot be opened."""
        wb = WordBook.open("/nonexistent/deep/db/test.db")
        assert wb is None

    def test_db_exists_returns_false_for_missing(self):
        """Returns False when database path does not exist."""
        assert not WordBook.db_exists("/nonexistent/deep/db/test.db")

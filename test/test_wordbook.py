import os
import tempfile
import time
import unittest
from unittest.mock import MagicMock, patch

from dict_tiny.config import MAX_ENTRIES
from dict_tiny.wordbook import WordBook, WordBookEntry


class TestWordBook(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.tmpdir, 'test.db')
        self.wb = WordBook(self.db_path)

    def tearDown(self):
        if self.wb:
            self.wb.close()
        try:
            os.remove(self.db_path)
        except OSError:
            pass
        try:
            os.rmdir(self.tmpdir)
        except OSError:
            pass

    # ── record ────────────────────────────────────────────

    def test_record_new(self):
        result = self.wb.record('hello', 'en', 'zh', 'YoudaoDict')
        self.assertTrue(result)
        self.assertEqual(self.wb.count(), 1)

    def test_record_duplicate(self):
        self.wb.record('hello', 'en', 'zh', 'YoudaoDict')
        self.wb.record('hello', 'en', 'fr', 'GoogleTranslate')
        self.assertEqual(self.wb.count(), 1)
        entry = self.wb.get_entry(1)
        self.assertEqual(entry.access_count, 2)
        self.assertEqual(entry.translator, 'GoogleTranslate')

    def test_record_eviction(self):
        # Fill up to MAX_ENTRIES
        for i in range(MAX_ENTRIES):
            self.wb.record(f'word{i}', 'en', 'zh', 'YoudaoDict')
        self.assertEqual(self.wb.count(), MAX_ENTRIES)

        # Evict the oldest (first inserted, lowest last_access)
        self.wb.record('overflow', 'en', 'zh', 'YoudaoDict')
        self.assertEqual(self.wb.count(), MAX_ENTRIES)

        entries, _ = self.wb.list_entries(page=1, page_size=MAX_ENTRIES)
        texts = {e.text for e in entries}
        self.assertIn('overflow', texts)
        # word0 should be evicted since it has the oldest last_access
        self.assertNotIn('word0', texts)

    def test_record_resilience(self):
        self.wb.close()
        # Corrupt the DB
        with open(self.db_path, 'w') as f:
            f.write('garbage')
        wb = WordBook(self.db_path)
        # Should not raise; _conn will be None
        self.assertIsNone(wb._conn)
        result = wb.record('hello', 'en', 'zh', 'YoudaoDict')
        self.assertFalse(result)

    # ── get_entry ─────────────────────────────────────────

    def test_get_entry(self):
        self.wb.record('hello', 'en', 'zh', 'YoudaoDict')
        entry = self.wb.get_entry(1)
        self.assertIsNotNone(entry)
        self.assertEqual(entry.text, 'hello')
        self.assertEqual(entry.source_language, 'en')
        self.assertEqual(entry.target_language, 'zh')
        self.assertEqual(entry.translator, 'YoudaoDict')
        self.assertEqual(entry.access_count, 1)

    def test_get_entry_invalid(self):
        self.assertIsNone(self.wb.get_entry(1))
        self.assertIsNone(self.wb.get_entry(0))
        self.assertIsNone(self.wb.get_entry(-1))

    # ── list_entries ──────────────────────────────────────

    def test_list_default_sort_by_time(self):
        self.wb.record('first', 'en', 'zh', 'YoudaoDict')
        time.sleep(0.01)
        self.wb.record('second', 'en', 'zh', 'YoudaoDict')
        entries, total = self.wb.list_entries()
        self.assertEqual(total, 2)
        self.assertEqual(entries[0].text, 'second')  # newest first
        self.assertEqual(entries[1].text, 'first')

    def test_list_sort_freq(self):
        self.wb.record('rare', 'en', 'zh', 'YoudaoDict')
        self.wb.record('freq', 'en', 'zh', 'YoudaoDict')
        self.wb.record('freq', 'en', 'zh', 'YoudaoDict')
        entries, _ = self.wb.list_entries(sort_by='freq')
        self.assertEqual(entries[0].text, 'freq')

    def test_list_sort_recent(self):
        self.wb.record('old', 'en', 'zh', 'YoudaoDict')
        time.sleep(0.01)
        self.wb.record('new', 'en', 'zh', 'YoudaoDict')
        self.wb.record('old', 'en', 'zh', 'YoudaoDict')  # updates last_access
        entries, _ = self.wb.list_entries(sort_by='recent')
        self.assertEqual(entries[0].text, 'old')  # most recently accessed

    def test_list_pagination(self):
        for i in range(5):
            self.wb.record(f'w{i}', 'en', 'zh', 'YoudaoDict')
        entries, total = self.wb.list_entries(page=2, page_size=3)
        self.assertEqual(total, 5)
        self.assertEqual(len(entries), 2)

    def test_list_since(self):
        self.wb.record('old', 'en', 'zh', 'YoudaoDict')
        mid = time.time()
        time.sleep(0.01)
        self.wb.record('new', 'en', 'zh', 'YoudaoDict')
        entries, total = self.wb.list_entries(since=mid)
        self.assertEqual(total, 1)
        self.assertEqual(entries[0].text, 'new')

    # ── search ─────────────────────────────────────────────

    def test_search_fuzzy(self):
        for text in ("hello", "hello_world", "hell", "world"):
            self.wb.record(text, "en", "zh", "YoudaoDict")
        entries, total = self.wb.list_entries(search="hello")
        self.assertEqual(total, 2)
        self.assertEqual({e.text for e in entries}, {"hello", "hello_world"})

    def test_search_exact(self):
        for text in ("hello", "hello_world"):
            self.wb.record(text, "en", "zh", "YoudaoDict")
        entries, total = self.wb.list_entries(search="hello", exact=True)
        self.assertEqual(total, 1)
        self.assertEqual(entries[0].text, "hello")

    def test_search_no_match(self):
        self.wb.record("hello", "en", "zh", "YoudaoDict")
        entries, total = self.wb.list_entries(search="zzz_not_there")
        self.assertEqual(total, 0)
        self.assertEqual(len(entries), 0)

    def test_search_pagination(self):
        for i in range(5):
            self.wb.record(f"hello_{i}", "en", "zh", "YoudaoDict")
        entries, total = self.wb.list_entries(search="hello", page=1, page_size=2)
        self.assertEqual(total, 5)
        self.assertEqual(len(entries), 2)

    def test_search_empty_db(self):
        entries, total = self.wb.list_entries(search="hello")
        self.assertEqual(total, 0)
        self.assertEqual(len(entries), 0)

    def test_search_with_since_filter(self):
        self.wb.record("old", "en", "zh", "YoudaoDict")
        mid = time.time()
        time.sleep(0.01)
        self.wb.record("hello", "en", "zh", "YoudaoDict")
        entries, total = self.wb.list_entries(search="hello", since=mid)
        self.assertEqual(total, 1)
        self.assertEqual(entries[0].text, "hello")

    def test_search_combined_search_and_since_no_match(self):
        self.wb.record("hello", "en", "zh", "YoudaoDict")
        future = time.time() + 1000
        entries, total = self.wb.list_entries(search="hello", since=future)
        self.assertEqual(total, 0)
        self.assertEqual(len(entries), 0)

    def test_list_invalid_page_returns_empty(self):
        self.wb.record("hello", "en", "zh", "YoudaoDict")
        entries, total = self.wb.list_entries(page=0)
        self.assertEqual(entries, [])
        self.assertEqual(total, 0)
        entries, total = self.wb.list_entries(page=-1)
        self.assertEqual(entries, [])

    def test_list_invalid_sort_falls_back_to_created(self):
        self.wb.record("hello", "en", "zh", "YoudaoDict")
        entries, total = self.wb.list_entries(sort_by="invalid_sort")
        self.assertEqual(total, 1)
        # Should not raise; falls back to "timestamp DESC"
        self.assertEqual(entries[0].text, "hello")

    # ── delete ─────────────────────────────────────────────

    def test_delete(self):
        self.wb.record('hello', 'en', 'zh', 'YoudaoDict')
        self.assertTrue(self.wb.delete(1))
        self.assertEqual(self.wb.count(), 0)

    def test_delete_invalid(self):
        self.assertFalse(self.wb.delete(1))

    def test_delete_then_record_reuses_id(self):
        """After delete, recording a new word should still work."""
        self.wb.record("hello", "en", "zh", "YoudaoDict")
        self.assertTrue(self.wb.delete(1))
        self.assertTrue(self.wb.record("world", "en", "zh", "YoudaoDict"))
        self.assertEqual(self.wb.count(), 1)

    # ── delete_db ──────────────────────────────────────────

    def test_delete_db(self):
        self.wb.record('hello', 'en', 'zh', 'YoudaoDict')
        self.wb.delete_db()
        self.assertFalse(os.path.isfile(self.db_path))
        # re-init works
        wb2 = WordBook(self.db_path)
        self.assertEqual(wb2.count(), 0)
        wb2.close()
        self.wb = None  # prevent tearDown from re-closing

    def test_delete_db_missing_file_swallows_error(self):
        """delete_db should not raise when the file is already gone."""
        # Close and manually remove the file
        self.wb.close()
        if os.path.isfile(self.db_path):
            os.remove(self.db_path)
        # Should not raise
        self.wb.delete_db()
        self.wb = None

    def test_close_idempotent(self):
        """Closing twice should not raise."""
        self.wb.close()
        self.wb.close()
        self.assertIsNone(self.wb._conn)
        self.wb = None

    def test_get_entry_after_close_returns_none(self):
        self.wb.record("hello", "en", "zh", "YoudaoDict")
        self.wb.close()
        self.assertIsNone(self.wb.get_entry(1))
        self.wb = None

    def test_count_after_close_returns_zero(self):
        self.wb.record("hello", "en", "zh", "YoudaoDict")
        self.wb.close()
        self.assertEqual(self.wb.count(), 0)
        self.wb = None

    def test_record_none_conn_returns_false(self):
        self.wb.close()
        self.assertFalse(self.wb.record("hello", "en", "zh", "YoudaoDict"))
        self.wb = None

    def test_set_default_record_none_conn_no_raise(self):
        self.wb.close()
        # Should not raise even with no connection
        self.wb.set_default_record(True)
        self.assertFalse(self.wb.get_default_record())
        self.wb = None

    # ── config ─────────────────────────────────────────────

    def test_config_default_record(self):
        self.assertFalse(self.wb.get_default_record())
        self.wb.set_default_record(True)
        self.assertTrue(self.wb.get_default_record())
        config = self.wb.get_config()
        self.assertTrue(config['default_record'])

        # persist across connections
        self.wb.close()
        wb2 = WordBook(self.db_path)
        self.assertTrue(wb2.get_default_record())
        wb2.set_default_record(False)
        wb2.close()
        wb3 = WordBook(self.db_path)
        self.assertFalse(wb3.get_default_record())
        wb3.close()
        self.wb = None

    # ── db_exists ──────────────────────────────────────────

    def test_db_exists(self):
        path = os.path.join(self.tmpdir, 'nonexistent.db')
        self.assertFalse(WordBook.db_exists(path))
        WordBook(path).close()
        self.assertTrue(WordBook.db_exists(path))
        os.remove(path)

    # ── misc ───────────────────────────────────────────────

    def test_count(self):
        self.assertEqual(self.wb.count(), 0)
        self.wb.record('a', 'en', 'zh', 'YoudaoDict')
        self.assertEqual(self.wb.count(), 1)

    def test_get_data_dir(self):
        from dict_tiny.util import get_data_dir
        d = get_data_dir()
        self.assertIn('dict-tiny', str(d))


class TestWordBookExtraAction(unittest.TestCase):
    def test_extra_action_hook(self):
        mock_wb = MagicMock()
        mock_dt = MagicMock()
        mock_dt.wordbook = mock_wb
        mock_dt.source_language = 'en'
        mock_dt.target_language = 'zh'
        mock_dt.detect_language = False

        from dict_tiny.translators.translator import DefaultTrans
        trans = DefaultTrans('hello', mock_dt)
        trans.name = 'YoudaoDict'
        trans.extra_action('hello')

        mock_wb.record.assert_called_once_with('hello', 'en', 'zh', 'YoudaoDict')


class TestWordBookOpen(unittest.TestCase):
    def test_open_returns_none_on_failure(self):
        wb = WordBook.open("/nonexistent/deep/db/test.db")
        self.assertIsNone(wb)

    def test_db_exists_returns_false_for_missing(self):
        self.assertFalse(WordBook.db_exists("/nonexistent/deep/db/test.db"))


if __name__ == "__main__":
    unittest.main()

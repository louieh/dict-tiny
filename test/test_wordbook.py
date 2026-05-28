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
        entries, total = self.wb.list_entries_since(mid)
        self.assertEqual(total, 1)
        self.assertEqual(entries[0].text, 'new')

    # ── delete ─────────────────────────────────────────────

    def test_delete(self):
        self.wb.record('hello', 'en', 'zh', 'YoudaoDict')
        self.assertTrue(self.wb.delete(1))
        self.assertEqual(self.wb.count(), 0)

    def test_delete_invalid(self):
        self.assertFalse(self.wb.delete(1))

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

        from dict_tiny.translators.translator import DefaultTrans
        trans = DefaultTrans('hello', mock_dt)
        trans.name = 'YoudaoDict'
        trans.extra_action('hello')

        mock_wb.record.assert_called_once_with('hello', 'en', 'zh', 'YoudaoDict')


if __name__ == "__main__":
    unittest.main()

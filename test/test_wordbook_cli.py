import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch

from dict_tiny.main import run
from dict_tiny.wordbook import WordBookEntry


class TestWbList(unittest.TestCase):
    def _entry(self, **kw):
        defaults = dict(
            id=1, text="hello", source_language="en", target_language="zh",
            translator="youdaodict", timestamp=1000.0, last_access=1001.0,
            access_count=2,
        )
        defaults.update(kw)
        return WordBookEntry(**defaults)

    @patch("sys.argv", ["", "wb", "list"])
    def test_list_empty(self):
        try:
            run()
        except SystemExit:
            pass

    @patch("sys.argv", ["", "wb", "list", "--page", "1", "--page-size", "5"])
    def test_list_pagination(self):
        entries = [self._entry(id=i) for i in range(1, 6)]
        with patch("dict_tiny.wordbook.WordBook.open") as mo:
            mo.return_value.list_entries.return_value = (entries, 20)
            try:
                run()
            except SystemExit:
                pass
            mo.return_value.list_entries.assert_called_once_with(1, 5, "created")

    @patch("sys.argv", ["", "wb", "list", "--sort", "freq"])
    def test_list_sort_freq(self):
        entries = [self._entry(id=1, access_count=5)]
        with patch("dict_tiny.wordbook.WordBook.open") as mo:
            mo.return_value.list_entries.return_value = (entries, 1)
            try:
                run()
            except SystemExit:
                pass
            mo.return_value.list_entries.assert_called_once_with(1, 20, "freq")

    @patch("sys.argv", ["", "wb", "list", "--sort", "recent"])
    def test_list_sort_recent(self):
        entries = [self._entry(id=1)]
        with patch("dict_tiny.wordbook.WordBook.open") as mo:
            mo.return_value.list_entries.return_value = (entries, 1)
            try:
                run()
            except SystemExit:
                pass
            mo.return_value.list_entries.assert_called_once_with(1, 20, "recent")

    @patch("sys.argv", ["", "wb", "list", "--sort", "invalid"])
    def test_list_invalid_sort(self):
        with patch("dict_tiny.wordbook.WordBook.open") as mo:
            try:
                run()
            except SystemExit:
                pass
            # list_entries should NOT be called for invalid sort
            mo.return_value.list_entries.assert_not_called()

    @patch("sys.argv", ["", "wb", "list", "--since", "2024-01-01"])
    def test_list_since(self):
        entries = [self._entry(id=1)]
        with patch("dict_tiny.wordbook.WordBook.open") as mo:
            mo.return_value.list_entries.return_value = (entries, 1)
            try:
                run()
            except SystemExit:
                pass
            expected_since = datetime(2024, 1, 1).timestamp()
            mo.return_value.list_entries.assert_called_once_with(
                1, 20, "created", since=expected_since
            )

    @patch("sys.argv", ["", "wb", "list", "--since", "not-a-date"])
    def test_list_invalid_since(self):
        with patch("dict_tiny.wordbook.WordBook.open") as mo:
            try:
                run()
            except SystemExit:
                pass
            mo.return_value.list_entries.assert_not_called()

    @patch("sys.argv", ["", "wb", "list"])
    def test_list_open_fails(self):
        with patch("dict_tiny.wordbook.WordBook.open") as mo:
            mo.return_value = None
            try:
                run()
            except SystemExit:
                pass


class TestWbDetail(unittest.TestCase):
    @patch("sys.argv", ["", "wb", "detail", "1"])
    def test_detail_found(self):
        entry = WordBookEntry(
            id=1, text="hello", source_language="en", target_language="zh",
            translator="youdaodict", timestamp=1000000.0, last_access=1000001.0,
            access_count=3,
        )
        with patch("dict_tiny.wordbook.WordBook.open") as mo:
            mo.return_value.get_entry.return_value = entry
            try:
                run()
            except SystemExit:
                pass
            mo.return_value.get_entry.assert_called_once_with(1)

    @patch("sys.argv", ["", "wb", "detail", "999"])
    def test_detail_not_found(self):
        with patch("dict_tiny.wordbook.WordBook.open") as mo:
            mo.return_value.get_entry.return_value = None
            try:
                run()
            except SystemExit:
                pass
            mo.return_value.get_entry.assert_called_once_with(999)


class TestWbDelete(unittest.TestCase):
    @patch("sys.argv", ["", "wb", "delete", "1"])
    def test_delete_ok(self):
        with patch("dict_tiny.wordbook.WordBook.open") as mo:
            mo.return_value.delete.return_value = True
            try:
                run()
            except SystemExit:
                pass
            mo.return_value.delete.assert_called_once_with(1)

    @patch("sys.argv", ["", "wb", "delete", "999"])
    def test_delete_not_found(self):
        with patch("dict_tiny.wordbook.WordBook.open") as mo:
            mo.return_value.delete.return_value = False
            try:
                run()
            except SystemExit:
                pass
            mo.return_value.delete.assert_called_once_with(999)


class TestWbSearch(unittest.TestCase):
    def _entry(self, **kw):
        defaults = dict(
            id=1, text="hello", source_language="en", target_language="zh",
            translator="youdaodict", timestamp=1000.0, last_access=1001.0,
            access_count=2,
        )
        defaults.update(kw)
        return WordBookEntry(**defaults)

    @patch("sys.argv", ["", "wb", "search", "hello"])
    def test_search_fuzzy(self):
        entries = [self._entry(id=1), self._entry(id=2, text="hello_world")]
        with patch("dict_tiny.wordbook.WordBook.open") as mo:
            mo.return_value.list_entries.return_value = (entries, 2)
            try:
                run()
            except SystemExit:
                pass
            mo.return_value.list_entries.assert_called_once_with(
                1, 20, sort_by="created", since=None, search="hello", exact=False
            )

    @patch("sys.argv", ["", "wb", "search", "hello", "--exact"])
    def test_search_exact(self):
        entries = [self._entry(id=1)]
        with patch("dict_tiny.wordbook.WordBook.open") as mo:
            mo.return_value.list_entries.return_value = (entries, 1)
            try:
                run()
            except SystemExit:
                pass
            mo.return_value.list_entries.assert_called_once_with(
                1, 20, sort_by="created", since=None, search="hello", exact=True
            )

    @patch("sys.argv", ["", "wb", "search", "hello", "--page", "2", "--page-size", "5"])
    def test_search_pagination(self):
        entries = [self._entry(id=i) for i in range(1, 6)]
        with patch("dict_tiny.wordbook.WordBook.open") as mo:
            mo.return_value.list_entries.return_value = (entries, 50)
            try:
                run()
            except SystemExit:
                pass
            mo.return_value.list_entries.assert_called_once_with(
                2, 5, sort_by="created", since=None, search="hello", exact=False
            )

    @patch("sys.argv", ["", "wb", "search", "zzz"])
    def test_search_empty(self):
        with patch("dict_tiny.wordbook.WordBook.open") as mo:
            mo.return_value.list_entries.return_value = ([], 0)
            try:
                run()
            except SystemExit:
                pass
            mo.return_value.list_entries.assert_called_once_with(
                1, 20, sort_by="created", since=None, search="zzz", exact=False
            )

    @patch("sys.argv", ["", "wb", "search", "hello"])
    def test_search_open_fails(self):
        with patch("dict_tiny.wordbook.WordBook.open") as mo:
            mo.return_value = None
            try:
                run()
            except SystemExit:
                pass

    @patch("sys.argv", ["", "wb", "search", "hello", "--sort", "freq"])
    def test_search_sort_freq(self):
        entries = [self._entry(id=1, access_count=5)]
        with patch("dict_tiny.wordbook.WordBook.open") as mo:
            mo.return_value.list_entries.return_value = (entries, 1)
            try:
                run()
            except SystemExit:
                pass
            mo.return_value.list_entries.assert_called_once_with(
                1, 20, sort_by="freq", since=None, search="hello", exact=False
            )

    @patch("sys.argv", ["", "wb", "search", "hello", "--since", "2024-01-01"])
    def test_search_since(self):
        entries = [self._entry(id=1)]
        with patch("dict_tiny.wordbook.WordBook.open") as mo:
            mo.return_value.list_entries.return_value = (entries, 1)
            try:
                run()
            except SystemExit:
                pass
            expected_since = datetime(2024, 1, 1).timestamp()
            mo.return_value.list_entries.assert_called_once_with(
                1, 20, sort_by="created", since=expected_since, search="hello", exact=False
            )

    @patch("sys.argv", ["", "wb", "search", "hello", "--sort", "invalid"])
    def test_search_invalid_sort(self):
        with patch("dict_tiny.wordbook.WordBook.open") as mo:
            try:
                run()
            except SystemExit:
                pass
            mo.return_value.list_entries.assert_not_called()


class TestWbConfig(unittest.TestCase):
    @patch("sys.argv", ["", "wb", "config"])
    def test_config_show(self):
        with patch("dict_tiny.wordbook.WordBook.open") as mo:
            mo.return_value.get_config.return_value = {
                "count": 5, "default_record": False,
            }
            mo.return_value.count.return_value = 5
            try:
                run()
            except SystemExit:
                pass

    @patch("sys.argv", ["", "wb", "config", "--record", "on"])
    def test_config_record_on(self):
        with patch("dict_tiny.wordbook.WordBook.open") as mo:
            try:
                run()
            except SystemExit:
                pass
            mo.return_value.set_default_record.assert_called_once_with(True)

    @patch("sys.argv", ["", "wb", "config", "--record", "off"])
    def test_config_record_off(self):
        with patch("dict_tiny.wordbook.WordBook.open") as mo:
            try:
                run()
            except SystemExit:
                pass
            mo.return_value.set_default_record.assert_called_once_with(False)

    @patch("sys.argv", ["", "wb", "config", "--record", "invalid"])
    def test_config_record_invalid(self):
        with patch("dict_tiny.wordbook.WordBook.open") as mo:
            try:
                run()
            except SystemExit:
                pass
            mo.return_value.set_default_record.assert_not_called()


class TestWbDbDelete(unittest.TestCase):
    @patch("sys.argv", ["", "wb", "db-delete"])
    @patch("builtins.input", return_value="y")
    def test_db_delete(self, mock_input):
        with patch("dict_tiny.wordbook.WordBook.open") as mo:
            mock_wb = MagicMock()
            mock_wb._path = "/fake/path"
            mo.return_value = mock_wb
            with patch("dict_tiny.wordbook.WordBook.db_exists", return_value=True):
                try:
                    run()
                except SystemExit:
                    pass
                mock_wb.delete_db.assert_called_once()

    @patch("sys.argv", ["", "wb", "db-delete"])
    @patch("builtins.input", return_value="n")
    def test_db_delete_cancelled(self, mock_input):
        with patch("dict_tiny.wordbook.WordBook.open") as mo:
            mock_wb = MagicMock()
            mock_wb._path = "/fake/path"
            mo.return_value = mock_wb
            with patch("dict_tiny.wordbook.WordBook.db_exists", return_value=True):
                try:
                    run()
                except SystemExit:
                    pass
                mock_wb.delete_db.assert_not_called()

    @patch("sys.argv", ["", "wb", "db-delete"])
    @patch("builtins.input", return_value="yes")
    def test_db_delete_yes_accepts_yes(self, mock_input):
        with patch("dict_tiny.wordbook.WordBook.open") as mo:
            mock_wb = MagicMock()
            mock_wb._path = "/fake/path"
            mo.return_value = mock_wb
            with patch("dict_tiny.wordbook.WordBook.db_exists", return_value=True):
                try:
                    run()
                except SystemExit:
                    pass
                mock_wb.delete_db.assert_called_once()

    @patch("sys.argv", ["", "wb", "db-delete"])
    def test_db_delete_no_db_early_exit(self):
        with patch("dict_tiny.wordbook.WordBook.open") as mo:
            mock_wb = MagicMock()
            mo.return_value = mock_wb
            with patch("dict_tiny.wordbook.WordBook.db_exists", return_value=False):
                try:
                    run()
                except SystemExit:
                    pass
                mock_wb.delete_db.assert_not_called()
                mo.assert_not_called()

    @patch("sys.argv", ["", "wb", "db-delete"])
    def test_db_delete_open_returns_none(self):
        with patch("dict_tiny.wordbook.WordBook.open", return_value=None):
            with patch("dict_tiny.wordbook.WordBook.db_exists", return_value=True):
                try:
                    run()
                except SystemExit:
                    pass


class TestWbListCombo(unittest.TestCase):
    def _entry(self, **kw):
        defaults = dict(
            id=1, text="hello", source_language="en", target_language="zh",
            translator="youdaodict", timestamp=1000.0, last_access=1001.0,
            access_count=2,
        )
        defaults.update(kw)
        return WordBookEntry(**defaults)

    @patch("sys.argv", ["", "wb", "list", "--sort", "freq", "--since", "2024-01-01"])
    def test_list_sort_freq_with_since(self):
        entries = [self._entry(id=1, access_count=5)]
        with patch("dict_tiny.wordbook.WordBook.open") as mo:
            mo.return_value.list_entries.return_value = (entries, 1)
            try:
                run()
            except SystemExit:
                pass
            expected_since = datetime(2024, 1, 1).timestamp()
            mo.return_value.list_entries.assert_called_once_with(
                1, 20, "freq", since=expected_since
            )

    @patch("sys.argv", ["", "wb", "list", "--page", "2", "--page-size", "10"])
    def test_list_with_pagination_and_default_sort(self):
        entries = [self._entry(id=i) for i in range(1, 11)]
        with patch("dict_tiny.wordbook.WordBook.open") as mo:
            mo.return_value.list_entries.return_value = (entries, 50)
            try:
                run()
            except SystemExit:
                pass
            mo.return_value.list_entries.assert_called_once_with(2, 10, "created")

    @patch("sys.argv", ["", "wb", "list"])
    def test_list_open_returns_none(self):
        with patch("dict_tiny.wordbook.WordBook.open", return_value=None):
            try:
                run()
            except SystemExit:
                pass


class TestWbQuery(unittest.TestCase):
    def _make_entry(self, **kw):
        defaults = dict(
            id=1, text="hello", source_language="en", target_language="ja",
            translator="youdaodict", timestamp=1000000.0, last_access=1000001.0,
            access_count=2,
        )
        defaults.update(kw)
        return WordBookEntry(**defaults)

    @patch("sys.argv", ["", "wb", "query", "1"])
    def test_query_not_found(self):
        with patch("dict_tiny.wordbook.WordBook.open") as mo:
            mo.return_value.get_entry.return_value = None
            try:
                run()
            except SystemExit:
                pass
            mo.return_value.get_entry.assert_called_once_with(1)

    @patch("sys.argv", ["", "--no-record", "wb", "query", "1"])
    def test_query_no_record_flag(self):
        entry = self._make_entry()
        with patch("dict_tiny.wordbook.WordBook.open") as mo:
            mo.return_value.get_entry.return_value = entry
            with patch(
                "dict_tiny.translators.youdao_trans.YoudaoTrans.do_translate",
                return_value=True,
            ):
                try:
                    run()
                except SystemExit:
                    pass
                mo.return_value.record.assert_not_called()

    @patch("sys.argv", ["", "--record", "wb", "query", "1"])
    def test_query_record_flag(self):
        entry = self._make_entry()
        with patch("dict_tiny.wordbook.WordBook.open") as mo:
            mo.return_value.get_entry.return_value = entry
            with patch(
                "dict_tiny.translators.youdao_trans.YoudaoTrans.do_translate",
                return_value=True,
            ):
                try:
                    run()
                except SystemExit:
                    pass
                mo.return_value.record.assert_called_once()

    @patch("sys.argv", ["", "wb", "query", "1"])
    def test_query_uses_stored_translator(self):
        entry = self._make_entry()
        with patch("dict_tiny.wordbook.WordBook.open") as mo:
            mo.return_value.get_entry.return_value = entry
            with patch(
                "dict_tiny.translators.youdao_trans.YoudaoTrans.do_translate",
                return_value=True,
            ) as mock_dt:
                try:
                    run()
                except SystemExit:
                    pass
                mock_dt.assert_called_once()

    @patch("sys.argv", ["", "-g", "wb", "query", "1"])
    def test_query_google_override(self):
        """-g flag overrides the stored translator"""
        entry = self._make_entry(translator="youdaodict")
        with patch("dict_tiny.wordbook.WordBook.open") as mo:
            mo.return_value.get_entry.return_value = entry
            with patch(
                "dict_tiny.translators.google_trans.GoogleTrans.do_translate",
                return_value=True,
            ) as mock_gt:
                with patch(
                    "dict_tiny.translators.youdao_trans.YoudaoTrans.do_translate"
                ) as mock_yd:
                    try:
                        run()
                    except SystemExit:
                        pass
                    mock_gt.assert_called_once()
                    mock_yd.assert_not_called()

    @patch("sys.argv", ["", "--record", "wb", "query", "1"])
    def test_query_translation_fails_no_record(self):
        """When translation returns False, should not record"""
        entry = self._make_entry()
        with patch("dict_tiny.wordbook.WordBook.open") as mo:
            mo.return_value.get_entry.return_value = entry
            with patch(
                "dict_tiny.translators.youdao_trans.YoudaoTrans.do_translate",
                return_value=False,
            ):
                try:
                    run()
                except SystemExit:
                    pass
                mo.return_value.record.assert_not_called()

    @patch("sys.argv", ["", "wb", "query", "1"])
    def test_query_open_returns_none(self):
        with patch("dict_tiny.wordbook.WordBook.open", return_value=None):
            try:
                run()
            except SystemExit:
                pass

    @patch("sys.argv", ["", "wb", "query", "1"])
    def test_query_translator_init_error_no_record(self):
        entry = self._make_entry()
        with patch("dict_tiny.wordbook.WordBook.open") as mo:
            mo.return_value.get_entry.return_value = entry
            with patch(
                "dict_tiny.translators.youdao_trans.YoudaoTrans.do_translate",
                side_effect=RuntimeError("network"),
            ):
                try:
                    run()
                except SystemExit:
                    pass
                mo.return_value.record.assert_not_called()


class TestWbDetailEdgeCases(unittest.TestCase):
    @patch("sys.argv", ["", "wb", "detail", "1"])
    def test_detail_open_returns_none(self):
        with patch("dict_tiny.wordbook.WordBook.open", return_value=None):
            try:
                run()
            except SystemExit:
                pass


class TestWbDeleteEdgeCases(unittest.TestCase):
    @patch("sys.argv", ["", "wb", "delete", "1"])
    def test_delete_open_returns_none(self):
        with patch("dict_tiny.wordbook.WordBook.open", return_value=None):
            try:
                run()
            except SystemExit:
                pass


class TestWbSearchCombo(unittest.TestCase):
    def _entry(self, **kw):
        defaults = dict(
            id=1, text="hello", source_language="en", target_language="zh",
            translator="youdaodict", timestamp=1000.0, last_access=1001.0,
            access_count=2,
        )
        defaults.update(kw)
        return WordBookEntry(**defaults)

    @patch("sys.argv", ["", "wb", "search", "hello", "--exact", "--sort", "recent"])
    def test_search_exact_with_sort(self):
        entries = [self._entry(id=1)]
        with patch("dict_tiny.wordbook.WordBook.open") as mo:
            mo.return_value.list_entries.return_value = (entries, 1)
            try:
                run()
            except SystemExit:
                pass
            mo.return_value.list_entries.assert_called_once_with(
                1, 20, sort_by="recent", since=None, search="hello", exact=True
            )

    @patch("sys.argv", ["", "wb", "search", "hello", "--since", "2024-06-01", "--sort", "freq"])
    def test_search_since_with_sort(self):
        entries = [self._entry(id=1)]
        with patch("dict_tiny.wordbook.WordBook.open") as mo:
            mo.return_value.list_entries.return_value = (entries, 1)
            try:
                run()
            except SystemExit:
                pass
            expected_since = datetime(2024, 6, 1).timestamp()
            mo.return_value.list_entries.assert_called_once_with(
                1, 20, sort_by="freq", since=expected_since, search="hello", exact=False
            )

    @patch("sys.argv", ["", "wb", "search", "hello", "--since", "not-a-date"])
    def test_search_invalid_since_no_list_call(self):
        with patch("dict_tiny.wordbook.WordBook.open") as mo:
            try:
                run()
            except SystemExit:
                pass
            mo.return_value.list_entries.assert_not_called()


class TestWbConfigEdgeCases(unittest.TestCase):
    @patch("sys.argv", ["", "wb", "config"])
    def test_config_open_returns_none(self):
        with patch("dict_tiny.wordbook.WordBook.open", return_value=None):
            try:
                run()
            except SystemExit:
                pass

    @patch("sys.argv", ["", "wb", "config", "--record", "ON"])
    def test_config_record_case_insensitive(self):
        with patch("dict_tiny.wordbook.WordBook.open") as mo:
            try:
                run()
            except SystemExit:
                pass
            mo.return_value.set_default_record.assert_called_once_with(True)


if __name__ == "__main__":
    unittest.main()

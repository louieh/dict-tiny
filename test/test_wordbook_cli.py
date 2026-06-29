from datetime import datetime
from test.helpers import _entry, run_cli
from unittest.mock import MagicMock, patch

import pytest


class TestWbList:
    """wb list command tests."""

    @patch("sys.argv", ["", "wb", "list"])
    def test_list_empty(self):
        """Does not crash when wordbook is empty."""
        with patch("dict_tiny.wordbook.WordBook.open") as mo:
            mo.return_value.list_entries.return_value = ([], 0)
            run_cli()

    @patch("sys.argv", ["", "wb", "list", "--page", "1", "--page-size", "5"])
    def test_list_pagination(self):
        """Passes page and page_size to list_entries."""
        with patch("dict_tiny.wordbook.WordBook.open") as mo:
            mo.return_value.list_entries.return_value = ([], 0)
            run_cli()
            mo.return_value.list_entries.assert_called_once_with(1, 5, "created")

    @patch("sys.argv", ["", "wb", "list", "--sort", "freq"])
    def test_list_sort_freq(self):
        """Passes sort_by='freq' to list_entries."""
        with patch("dict_tiny.wordbook.WordBook.open") as mo:
            mo.return_value.list_entries.return_value = ([], 0)
            run_cli()
            mo.return_value.list_entries.assert_called_once_with(1, 20, "freq")

    @patch("sys.argv", ["", "wb", "list", "--sort", "recent"])
    def test_list_sort_recent(self):
        """Passes sort_by='recent' to list_entries."""
        with patch("dict_tiny.wordbook.WordBook.open") as mo:
            mo.return_value.list_entries.return_value = ([], 0)
            run_cli()
            mo.return_value.list_entries.assert_called_once_with(1, 20, "recent")

    @patch("sys.argv", ["", "wb", "list", "--sort", "invalid"])
    def test_list_invalid_sort(self):
        """Does not call list_entries when sort is invalid."""
        with patch("dict_tiny.wordbook.WordBook.open") as mo:
            run_cli()
            mo.return_value.list_entries.assert_not_called()

    @patch("sys.argv", ["", "wb", "list", "--since", "2024-01-01"])
    def test_list_since(self):
        """Passes since timestamp to list_entries."""
        with patch("dict_tiny.wordbook.WordBook.open") as mo:
            mo.return_value.list_entries.return_value = ([], 0)
            run_cli()
            expected_since = datetime(2024, 1, 1).timestamp()
            mo.return_value.list_entries.assert_called_once_with(
                1, 20, "created", since=expected_since
            )

    @patch("sys.argv", ["", "wb", "list", "--since", "not-a-date"])
    def test_list_invalid_since(self):
        """Does not call list_entries when since is not a valid date."""
        with patch("dict_tiny.wordbook.WordBook.open") as mo:
            run_cli()
            mo.return_value.list_entries.assert_not_called()

    @patch("sys.argv", ["", "wb", "list"])
    def test_list_open_fails(self):
        """Does not crash when WordBook.open returns None."""
        with patch("dict_tiny.wordbook.WordBook.open") as mo:
            mo.return_value = None
            run_cli()

    @patch("sys.argv", ["", "wb", "list", "--sort", "freq", "--since", "2024-01-01"])
    def test_list_sort_freq_with_since(self):
        """Combines sort=freq and since filter correctly."""
        with patch("dict_tiny.wordbook.WordBook.open") as mo:
            mo.return_value.list_entries.return_value = ([], 0)
            run_cli()
            expected_since = datetime(2024, 1, 1).timestamp()
            mo.return_value.list_entries.assert_called_once_with(
                1, 20, "freq", since=expected_since
            )

    @patch("sys.argv", ["", "wb", "list", "--page", "2", "--page-size", "10"])
    def test_list_with_pagination_and_default_sort(self):
        """Combines page/pagination with default sort."""
        with patch("dict_tiny.wordbook.WordBook.open") as mo:
            mo.return_value.list_entries.return_value = ([], 0)
            run_cli()
            mo.return_value.list_entries.assert_called_once_with(2, 10, "created")


class TestWbDetail:
    """wb detail command tests."""

    @patch("sys.argv", ["", "wb", "detail", "1"])
    def test_detail_found(self):
        """Calls get_entry with the given ID."""
        with patch("dict_tiny.wordbook.WordBook.open") as mo:
            mo.return_value.get_entry.return_value = _entry()
            run_cli()
            mo.return_value.get_entry.assert_called_once_with(1)

    @patch("sys.argv", ["", "wb", "detail", "999"])
    def test_detail_not_found(self):
        """Handles missing entry gracefully."""
        with patch("dict_tiny.wordbook.WordBook.open") as mo:
            mo.return_value.get_entry.return_value = None
            run_cli()
            mo.return_value.get_entry.assert_called_once_with(999)

    @patch("sys.argv", ["", "wb", "detail", "1"])
    def test_detail_open_returns_none(self):
        """Does not crash when WordBook.open returns None."""
        with patch("dict_tiny.wordbook.WordBook.open", return_value=None):
            run_cli()

    @patch("sys.argv", ["", "wb", "detail", "abc"])
    def test_detail_non_integer_id(self):
        """Raises ValueError for non-integer entry ID."""
        from dict_tiny.main import run

        with pytest.raises(ValueError):
            run()


class TestWbDelete:
    """wb delete command tests."""

    @patch("sys.argv", ["", "wb", "delete", "1"])
    def test_delete_ok(self):
        """Calls delete with the given ID when successful."""
        with patch("dict_tiny.wordbook.WordBook.open") as mo:
            mo.return_value.delete.return_value = True
            run_cli()
            mo.return_value.delete.assert_called_once_with(1)

    @patch("sys.argv", ["", "wb", "delete", "999"])
    def test_delete_not_found(self):
        """Handles delete for non-existent entry."""
        with patch("dict_tiny.wordbook.WordBook.open") as mo:
            mo.return_value.delete.return_value = False
            run_cli()
            mo.return_value.delete.assert_called_once_with(999)

    @patch("sys.argv", ["", "wb", "delete", "1"])
    def test_delete_open_returns_none(self):
        """Does not crash when WordBook.open returns None."""
        with patch("dict_tiny.wordbook.WordBook.open", return_value=None):
            run_cli()


class TestWbSearch:
    """wb search command tests."""

    @patch("sys.argv", ["", "wb", "search", "hello"])
    def test_search_fuzzy(self):
        """Performs fuzzy search by default."""
        with patch("dict_tiny.wordbook.WordBook.open") as mo:
            mo.return_value.list_entries.return_value = ([], 0)
            run_cli()
            mo.return_value.list_entries.assert_called_once_with(
                1, 20, sort_by="created", since=None, search="hello", exact=False
            )

    @patch("sys.argv", ["", "wb", "search", "hello", "--exact"])
    def test_search_exact(self):
        """Performs exact search when --exact is given."""
        with patch("dict_tiny.wordbook.WordBook.open") as mo:
            mo.return_value.list_entries.return_value = ([], 0)
            run_cli()
            mo.return_value.list_entries.assert_called_once_with(
                1, 20, sort_by="created", since=None, search="hello", exact=True
            )

    @patch("sys.argv", ["", "wb", "search", "hello", "--page", "2", "--page-size", "5"])
    def test_search_pagination(self):
        """Passes pagination along with search query."""
        with patch("dict_tiny.wordbook.WordBook.open") as mo:
            mo.return_value.list_entries.return_value = ([], 0)
            run_cli()
            mo.return_value.list_entries.assert_called_once_with(
                2, 5, sort_by="created", since=None, search="hello", exact=False
            )

    @patch("sys.argv", ["", "wb", "search", "zzz"])
    def test_search_empty(self):
        """Returns empty results when nothing matches."""
        with patch("dict_tiny.wordbook.WordBook.open") as mo:
            mo.return_value.list_entries.return_value = ([], 0)
            run_cli()
            mo.return_value.list_entries.assert_called_once_with(
                1, 20, sort_by="created", since=None, search="zzz", exact=False
            )

    @patch("sys.argv", ["", "wb", "search", "hello"])
    def test_search_open_fails(self):
        """Does not crash when WordBook.open returns None."""
        with patch("dict_tiny.wordbook.WordBook.open") as mo:
            mo.return_value = None
            run_cli()

    @patch("sys.argv", ["", "wb", "search", "hello", "--sort", "freq"])
    def test_search_sort_freq(self):
        """Passes sort_by='freq' along with search query."""
        with patch("dict_tiny.wordbook.WordBook.open") as mo:
            mo.return_value.list_entries.return_value = ([], 0)
            run_cli()
            mo.return_value.list_entries.assert_called_once_with(
                1, 20, sort_by="freq", since=None, search="hello", exact=False
            )

    @patch("sys.argv", ["", "wb", "search", "hello", "--since", "2024-01-01"])
    def test_search_since(self):
        """Passes since filter along with search query."""
        with patch("dict_tiny.wordbook.WordBook.open") as mo:
            mo.return_value.list_entries.return_value = ([], 0)
            run_cli()
            expected_since = datetime(2024, 1, 1).timestamp()
            mo.return_value.list_entries.assert_called_once_with(
                1,
                20,
                sort_by="created",
                since=expected_since,
                search="hello",
                exact=False,
            )

    @patch("sys.argv", ["", "wb", "search", "hello", "--sort", "invalid"])
    def test_search_invalid_sort(self):
        """Does not call list_entries when sort is invalid."""
        with patch("dict_tiny.wordbook.WordBook.open") as mo:
            run_cli()
            mo.return_value.list_entries.assert_not_called()

    @patch("sys.argv", ["", "wb", "search", "hello", "--exact", "--sort", "recent"])
    def test_search_exact_with_sort(self):
        """Combines exact search with sort_by='recent'."""
        with patch("dict_tiny.wordbook.WordBook.open") as mo:
            mo.return_value.list_entries.return_value = ([], 0)
            run_cli()
            mo.return_value.list_entries.assert_called_once_with(
                1, 20, sort_by="recent", since=None, search="hello", exact=True
            )

    @patch(
        "sys.argv",
        ["", "wb", "search", "hello", "--since", "2024-06-01", "--sort", "freq"],
    )
    def test_search_since_with_sort(self):
        """Combines since filter with sort_by='freq'."""
        with patch("dict_tiny.wordbook.WordBook.open") as mo:
            mo.return_value.list_entries.return_value = ([], 0)
            run_cli()
            expected_since = datetime(2024, 6, 1).timestamp()
            mo.return_value.list_entries.assert_called_once_with(
                1, 20, sort_by="freq", since=expected_since, search="hello", exact=False
            )

    @patch("sys.argv", ["", "wb", "search", "hello", "--since", "not-a-date"])
    def test_search_invalid_since_no_list_call(self):
        """Does not call list_entries when since is invalid."""
        with patch("dict_tiny.wordbook.WordBook.open") as mo:
            run_cli()
            mo.return_value.list_entries.assert_not_called()


class TestWbConfig:
    """wb config command tests."""

    @patch("sys.argv", ["", "wb", "config"])
    def test_config_show(self):
        """Prints current config without crashing."""
        with patch("dict_tiny.wordbook.WordBook.open") as mo:
            mo.return_value.get_config.return_value = {
                "count": 5,
                "default_record": False,
            }
            run_cli()

    @patch("sys.argv", ["", "wb", "config", "--record", "on"])
    def test_config_record_on(self):
        """Sets default_record to True."""
        with patch("dict_tiny.wordbook.WordBook.open") as mo:
            run_cli()
            mo.return_value.set_default_record.assert_called_once_with(True)

    @patch("sys.argv", ["", "wb", "config", "--record", "off"])
    def test_config_record_off(self):
        """Sets default_record to False."""
        with patch("dict_tiny.wordbook.WordBook.open") as mo:
            run_cli()
            mo.return_value.set_default_record.assert_called_once_with(False)

    @patch("sys.argv", ["", "wb", "config", "--record", "invalid"])
    def test_config_record_invalid(self):
        """Does not change config when --record value is invalid."""
        with patch("dict_tiny.wordbook.WordBook.open") as mo:
            run_cli()
            mo.return_value.set_default_record.assert_not_called()

    @patch("sys.argv", ["", "wb", "config"])
    def test_config_open_returns_none(self):
        """Does not crash when WordBook.open returns None."""
        with patch("dict_tiny.wordbook.WordBook.open", return_value=None):
            run_cli()

    @patch("sys.argv", ["", "wb", "config", "--record", "ON"])
    def test_config_record_case_insensitive(self):
        """Accepts case-insensitive 'on'/'off' values."""
        with patch("dict_tiny.wordbook.WordBook.open") as mo:
            run_cli()
            mo.return_value.set_default_record.assert_called_once_with(True)


class TestWbDbDelete:
    """wb db-delete command tests."""

    @patch("sys.argv", ["", "wb", "db-delete"])
    @patch("builtins.input", return_value="y")
    def test_db_delete(self, _):
        """Deletes database when user confirms with 'y'."""
        with patch("dict_tiny.wordbook.WordBook.open") as mo:
            mock_wb = MagicMock()
            mock_wb._path = "/fake/path"
            mo.return_value = mock_wb
            with patch("dict_tiny.wordbook.WordBook.db_exists", return_value=True):
                run_cli()
                mock_wb.delete_db.assert_called_once()

    @patch("sys.argv", ["", "wb", "db-delete"])
    @patch("builtins.input", return_value="n")
    def test_db_delete_cancelled(self, _):
        """Does not delete when user cancels with 'n'."""
        with patch("dict_tiny.wordbook.WordBook.open") as mo:
            mock_wb = MagicMock()
            mock_wb._path = "/fake/path"
            mo.return_value = mock_wb
            with patch("dict_tiny.wordbook.WordBook.db_exists", return_value=True):
                run_cli()
                mock_wb.delete_db.assert_not_called()

    @patch("sys.argv", ["", "wb", "db-delete"])
    @patch("builtins.input", return_value="yes")
    def test_db_delete_yes_accepts_yes(self, _):
        """Also accepts 'yes' as confirmation."""
        with patch("dict_tiny.wordbook.WordBook.open") as mo:
            mock_wb = MagicMock()
            mock_wb._path = "/fake/path"
            mo.return_value = mock_wb
            with patch("dict_tiny.wordbook.WordBook.db_exists", return_value=True):
                run_cli()
                mock_wb.delete_db.assert_called_once()

    @patch("sys.argv", ["", "wb", "db-delete"])
    def test_db_delete_no_db_early_exit(self):
        """Exits early when database does not exist."""
        with patch("dict_tiny.wordbook.WordBook.open") as mo:
            with patch("dict_tiny.wordbook.WordBook.db_exists", return_value=False):
                run_cli()
                mo.assert_not_called()

    @patch("sys.argv", ["", "wb", "db-delete"])
    def test_db_delete_open_returns_none(self):
        """Does not crash when WordBook.open returns None."""
        with patch("dict_tiny.wordbook.WordBook.open", return_value=None):
            with patch("dict_tiny.wordbook.WordBook.db_exists", return_value=True):
                run_cli()


class TestWbQuery:
    """wb query command tests."""

    @patch("sys.argv", ["", "wb", "query", "1"])
    def test_query_not_found(self):
        """Handles missing entry."""
        with patch("dict_tiny.wordbook.WordBook.open") as mo:
            mo.return_value.get_entry.return_value = None
            run_cli()
            mo.return_value.get_entry.assert_called_once_with(1)

    @patch("sys.argv", ["", "--no-record", "wb", "query", "1"])
    def test_query_no_record_flag(self):
        """Does not record when --no-record is set."""
        with patch("dict_tiny.wordbook.WordBook.open") as mo:
            mo.return_value.get_entry.return_value = _entry()
            with patch(
                "dict_tiny.translators.youdao_trans.YoudaoTrans.do_translate",
                return_value=True,
            ):
                run_cli()
                mo.return_value.record.assert_not_called()

    @patch("sys.argv", ["", "--record", "wb", "query", "1"])
    def test_query_record_flag(self):
        """Records translation when --record is set."""
        with patch("dict_tiny.wordbook.WordBook.open") as mo:
            mo.return_value.get_entry.return_value = _entry()
            with patch(
                "dict_tiny.translators.youdao_trans.YoudaoTrans.do_translate",
                return_value=True,
            ):
                run_cli()
                mo.return_value.record.assert_called_once()

    @patch("sys.argv", ["", "wb", "query", "1"])
    def test_query_uses_stored_translator(self):
        """Uses the translator stored in the entry."""
        with patch("dict_tiny.wordbook.WordBook.open") as mo:
            mo.return_value.get_entry.return_value = _entry()
            with patch(
                "dict_tiny.translators.youdao_trans.YoudaoTrans.do_translate",
                return_value=True,
            ) as mock_dt:
                run_cli()
                mock_dt.assert_called_once()

    @patch("sys.argv", ["", "-g", "wb", "query", "1"])
    def test_query_google_override(self):
        """Overrides stored translator with -g flag."""
        with patch("dict_tiny.wordbook.WordBook.open") as mo:
            mo.return_value.get_entry.return_value = _entry()
            with patch(
                "dict_tiny.translators.google_trans.GoogleTrans.do_translate",
                return_value=True,
            ) as mock_gt:
                with patch(
                    "dict_tiny.translators.youdao_trans.YoudaoTrans.do_translate"
                ) as mock_yd:
                    run_cli()
                    mock_gt.assert_called_once()
                    mock_yd.assert_not_called()

    @patch("sys.argv", ["", "--record", "wb", "query", "1"])
    def test_query_translation_fails_no_record(self):
        """Does not record when translation fails."""
        with patch("dict_tiny.wordbook.WordBook.open") as mo:
            mo.return_value.get_entry.return_value = _entry()
            with patch(
                "dict_tiny.translators.youdao_trans.YoudaoTrans.do_translate",
                return_value=False,
            ):
                run_cli()
                mo.return_value.record.assert_not_called()

    @patch("sys.argv", ["", "wb", "query", "1"])
    def test_query_open_returns_none(self):
        """Does not crash when WordBook.open returns None."""
        with patch("dict_tiny.wordbook.WordBook.open", return_value=None):
            run_cli()

    @patch("sys.argv", ["", "wb", "query", "1"])
    def test_query_translator_init_error_no_record(self):
        """Does not record when translator raises an exception."""
        with patch("dict_tiny.wordbook.WordBook.open") as mo:
            mo.return_value.get_entry.return_value = _entry()
            with patch(
                "dict_tiny.translators.youdao_trans.YoudaoTrans.do_translate",
                side_effect=RuntimeError("network"),
            ):
                run_cli()
                mo.return_value.record.assert_not_called()

    @patch("sys.argv", ["", "wb", "query", "1"])
    def test_query_custom_exception_on_translator_init(self):
        """Handles CustomException when translator init fails (e.g. unsupported language)."""
        with patch("dict_tiny.wordbook.WordBook.open") as mo:
            mo.return_value.get_entry.return_value = _entry(
                source_language="de"  # German is unsupported by Youdao
            )
            run_cli()
            mo.return_value.record.assert_not_called()

from datetime import datetime

from plumbum import cli
from rich.box import MINIMAL
from rich.console import Console
from rich.table import Table

from dict_tiny.config import MAX_ENTRIES
from dict_tiny.translators import _ALL_TRANSLATORS, DEFAULT_TRANSLATOR
from dict_tiny.wordbook import WordBook

console = Console()


class WordBookApp(cli.Application):
    def main(self):
        if self.nested_command:
            return
        print("Usage: dict-tiny wb <command> [...]")
        print("Commands: list, detail, query, delete, config, db-delete")


@WordBookApp.subcommand("list")
class WbList(cli.Application):
    page = cli.SwitchAttr("--page", int, default=1, help="Page number")
    page_size = cli.SwitchAttr("--page-size", int, default=20, help="Entries per page")
    sort = cli.SwitchAttr(
        "--sort", str, default="time", help="Sort by: time, freq, recent"
    )
    since = cli.SwitchAttr(
        "--since", str, default=None, help="Filter by start date (YYYY-MM-DD)"
    )

    def main(self):
        wb = WordBook.open()
        if wb is None:
            return

        VALID_SORTS = ("time", "freq", "recent")
        if self.sort not in VALID_SORTS:
            print(f"Invalid --sort '{self.sort}'. Choose from: time, freq, recent")
            return

        if self.since:
            try:
                since_ts = datetime.strptime(self.since, "%Y-%m-%d").timestamp()
            except ValueError:
                print("Invalid date format. Use YYYY-MM-DD.")
                return
            entries, total = wb.list_entries_since(since_ts, self.page, self.page_size)
        else:
            entries, total = wb.list_entries(self.page, self.page_size, self.sort)

        if not entries:
            print("(empty)")
            return

        start_idx = (self.page - 1) * self.page_size + 1
        table = Table(show_header=True, header_style="bold", box=MINIMAL)
        table.add_column("", justify="right", width=4, no_wrap=True)
        table.add_column("Word", no_wrap=True)
        table.add_column("Lang", justify="center", width=8)
        table.add_column("Time", justify="center", width=16)
        table.add_column("Count", justify="right", width=5)

        for i, entry in enumerate(entries):
            dt = datetime.fromtimestamp(entry.timestamp)
            time_str = dt.strftime("%Y-%m-%d %H:%M")
            if entry.source_language or entry.target_language:
                lang = f"{entry.source_language or ''}→{entry.target_language or ''}"
            else:
                lang = ""
            table.add_row(
                str(start_idx + i),
                entry.text,
                lang,
                time_str,
                f"×{entry.access_count}",
            )

        console.print(table)

        total_pages = max(1, -(-total // self.page_size))
        print(f"\nPage {self.page}/{total_pages}  (Total: {total} / {MAX_ENTRIES})")
        wb.close()


@WordBookApp.subcommand("detail")
class WbDetail(cli.Application):
    def main(self, index):
        index = int(index)
        wb = WordBook.open()
        if wb is None:
            return
        entry = wb.get_entry(index)
        if entry is None:
            print(f"Entry {index} not found.")
            wb.close()
            return
        dt = datetime.fromtimestamp(entry.timestamp)
        la = datetime.fromtimestamp(entry.last_access)
        print(f"  Text:              {entry.text}")
        print(f"  Source Language:   {entry.source_language or 'auto'}")
        print(f"  Target Language:   {entry.target_language or 'auto'}")
        print(f"  Translator:        {entry.translator or 'default'}")
        print(f"  First Recorded:    {dt.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  Last Access:       {la.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  Access Count:      {entry.access_count}")
        wb.close()


@WordBookApp.subcommand("query")
class WbQuery(cli.Application):
    def main(self, index):
        index = int(index)
        wb = WordBook.open()
        if wb is None:
            return
        entry = wb.get_entry(index)
        if entry is None:
            print(f"Entry {index} not found.")
            wb.close()
            return

        dict_tiny_obj, trans_cls = self.parent.parent, None

        # User's CLI translator flag overrides entry's stored translator
        for t_cls_candidate in _ALL_TRANSLATORS.values():
            if getattr(dict_tiny_obj, f"use_{t_cls_candidate.name}", False):
                trans_cls = t_cls_candidate
                break
        if trans_cls is None:
            trans_cls = DEFAULT_TRANSLATOR
            for t_cls_candidate in _ALL_TRANSLATORS.values():
                if t_cls_candidate.name == entry.translator:
                    trans_cls = t_cls_candidate
                    break

        # User's CLI language switches override entry values
        if not dict_tiny_obj.source_language:
            dict_tiny_obj.source_language = entry.source_language
        if not dict_tiny_obj.target_language:
            dict_tiny_obj.target_language = entry.target_language

        trans = trans_cls(entry.text, dict_tiny_obj)
        trans.translate()
        wb.record(entry.text, trans.source_language, trans.target_language, trans.name)
        wb.close()


@WordBookApp.subcommand("delete")
class WbDelete(cli.Application):
    def main(self, index):
        index = int(index)
        wb = WordBook.open()
        if wb is None:
            return
        if wb.delete(index):
            print(f"Entry {index} deleted.")
        else:
            print(f"Entry {index} not found.")
        wb.close()


@WordBookApp.subcommand("config")
class WbConfig(cli.Application):
    record = cli.SwitchAttr(
        "--record", str, default=None, help="Set default recording: on or off"
    )

    def main(self):
        wb = WordBook.open()
        if wb is None:
            return

        if self.record is not None:
            val = self.record.lower()
            if val not in ("on", "off"):
                print("Usage: --record on|off")
                wb.close()
                return
            wb.set_default_record(val == "on")
            print(f"Default recording: {'ON' if val == 'on' else 'OFF'}")

        config = wb.get_config()
        print(f"Path:             {wb._path}")
        print(f"Entries:          {config['count']} / {MAX_ENTRIES}")
        print(f"Default Recording: {'ON' if config['default_record'] else 'OFF'}")
        wb.close()


@WordBookApp.subcommand("db-delete")
class WbDbDelete(cli.Application):
    def main(self):
        wb = WordBook.open()
        if wb is None:
            print("No database to delete.")
            return
        path = wb._path
        wb.delete_db()
        print(f"Database deleted: {path}")
        print("A new one will be created on next use.")

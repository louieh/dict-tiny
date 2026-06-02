from datetime import datetime

from plumbum import cli
from rich.box import SIMPLE_HEAVY
from rich.console import Console
from rich.table import Table

from dict_tiny.config import MAX_ENTRIES, YOUDAO_NAME
from dict_tiny.errors import CustomException
from dict_tiny.translators import _ALL_TRANSLATORS, DEFAULT_TRANSLATOR
from dict_tiny.util import normal_error_printer
from dict_tiny.wordbook import WordBook

console = Console()


def _render_table(entries, page, page_size, total, caption):
    """Render entries in a rich table. Returns a Table object ready to print."""
    total_pages = max(1, -(-total // page_size))
    table = Table(
        show_header=True,
        header_style="bold",
        style="cyan",
        box=SIMPLE_HEAVY,
        caption=caption
        or f"Page {page}/{total_pages}  ({total} entries, limit {MAX_ENTRIES})",
        caption_justify="left",
        caption_style="dim",
        padding=(0, 1),
        row_styles=["", "on grey19"],
    )
    table.add_column("ID", justify="right", width=4, no_wrap=True, style="dim")
    table.add_column("Text", overflow="fold")
    table.add_column("Lang", justify="center", width=8)
    table.add_column("Created", justify="center", width=16)
    table.add_column("Count", justify="right", width=5)

    for entry in entries:
        dt = datetime.fromtimestamp(entry.timestamp)
        time_str = dt.strftime("%Y-%m-%d %H:%M")
        if entry.source_language or entry.target_language:
            lang = f"{entry.source_language or ''}→{entry.target_language or ''}"
        elif entry.translator and entry.translator == YOUDAO_NAME:
            lang = "zh↔en"
        else:
            lang = ""
        table.add_row(
            str(entry.id),
            entry.text,
            lang,
            time_str,
            f"×{entry.access_count}",
        )
    return table


class WordBookApp(cli.Application):
    def main(self):
        if self.nested_command:
            return
        print("Usage: dict-tiny wb <command> [...]")
        print("Commands: list, detail, query, search, delete, config, db-delete")


@WordBookApp.subcommand("list")
class WbList(cli.Application):
    page = cli.SwitchAttr("--page", int, default=1, help="Page number")
    page_size = cli.SwitchAttr("--page-size", int, default=20, help="Entries per page")
    sort = cli.SwitchAttr(
        "--sort", str, default="created", help="Sort by: created, freq, recent"
    )
    since = cli.SwitchAttr(
        "--since", str, default=None, help="Filter by start date (YYYY-MM-DD)"
    )

    def main(self):
        wb = WordBook.open()
        if wb is None:
            return

        VALID_SORTS = ("created", "freq", "recent")
        if self.sort not in VALID_SORTS:
            print(f"Invalid --sort '{self.sort}'. Choose from: created, freq, recent")
            return

        if self.since:
            try:
                since_ts = datetime.strptime(self.since, "%Y-%m-%d").timestamp()
            except ValueError:
                print("Invalid date format. Use YYYY-MM-DD.")
                return
            entries, total = wb.list_entries(
                self.page, self.page_size, self.sort, since=since_ts
            )
        else:
            entries, total = wb.list_entries(self.page, self.page_size, self.sort)

        if not entries:
            print("(empty)")
            return

        table = _render_table(entries, self.page, self.page_size, total, caption=None)
        console.print(table)
        wb.close()


@WordBookApp.subcommand("detail")
class WbDetail(cli.Application):
    def main(self, entry_id):
        entry_id = int(entry_id)
        wb = WordBook.open()
        if wb is None:
            return
        entry = wb.get_entry(entry_id)
        if entry is None:
            print(f"Entry ID:{entry_id} not found.")
            wb.close()
            return
        dt = datetime.fromtimestamp(entry.timestamp)
        la = datetime.fromtimestamp(entry.last_access)
        print(f"  Text:              {entry.text}")
        print(f"  Source Language:   {entry.source_language or ''}")
        print(f"  Target Language:   {entry.target_language or ''}")
        print(f"  Translator:        {entry.translator or 'default'}")
        print(f"  Created:           {dt.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  Last Query:        {la.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  Access Count:      {entry.access_count}")
        wb.close()


@WordBookApp.subcommand("query")
class WbQuery(cli.Application):
    def main(self, entry_id):
        entry_id = int(entry_id)
        wb = WordBook.open()
        if wb is None:
            return
        entry = wb.get_entry(entry_id)
        if entry is None:
            print(f"Entry ID:{entry_id} not found.")
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

        try:
            trans = trans_cls(entry.text, dict_tiny_obj)
        except CustomException as e:
            normal_error_printer(e.message)
            wb.close()
            return
        except Exception as e:
            normal_error_printer(f"translator init error: {e}")
            wb.close()
            return

        trans_res = trans.translate()

        if trans_res and dict_tiny_obj.should_record:
            wb.record(
                entry.text,
                trans.source_language,
                trans.target_language,
                trans.name,
            )
        wb.close()


@WordBookApp.subcommand("delete")
class WbDelete(cli.Application):
    def main(self, entry_id):
        entry_id = int(entry_id)
        wb = WordBook.open()
        if wb is None:
            return
        if wb.delete(entry_id):
            print(f"Entry ID:{entry_id} deleted.")
        else:
            print(f"Entry ID:{entry_id} not found.")
        wb.close()


@WordBookApp.subcommand("search")
class WbSearch(cli.Application):
    exact = cli.Flag("--exact", help="Exact match instead of fuzzy")
    sort = cli.SwitchAttr(
        "--sort", str, default="created", help="Sort by: created, freq, recent"
    )
    since = cli.SwitchAttr(
        "--since", str, default=None, help="Filter by start date (YYYY-MM-DD)"
    )
    page = cli.SwitchAttr("--page", int, default=1, help="Page number")
    page_size = cli.SwitchAttr("--page-size", int, default=20, help="Entries per page")

    def main(self, text):
        wb = WordBook.open()
        if wb is None:
            return

        VALID_SORTS = ("created", "freq", "recent")
        if self.sort not in VALID_SORTS:
            print(f"Invalid --sort '{self.sort}'. Choose from: created, freq, recent")
            wb.close()
            return

        since_ts = None
        if self.since:
            try:
                since_ts = datetime.strptime(self.since, "%Y-%m-%d").timestamp()
            except ValueError:
                print("Invalid date format. Use YYYY-MM-DD.")
                wb.close()
                return

        entries, total = wb.list_entries(
            self.page,
            self.page_size,
            sort_by=self.sort,
            since=since_ts,
            search=text,
            exact=self.exact,
        )

        if not entries:
            print("(empty)")
            wb.close()
            return

        total_pages = max(1, -(-total // self.page_size))
        caption = (
            f"Search results for '{text}'{' (exact)' if self.exact else ''}"
            f"  —  Page {self.page}/{total_pages}  ({total} entries)"
        )
        table = _render_table(
            entries, self.page, self.page_size, total, caption=caption
        )
        console.print(table)
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
        wb.delete_db()
        print("Word book database deleted.")

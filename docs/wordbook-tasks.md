# Word Book Implementation Tasks

## Task 1: Create WordBook class — DB init and schema

**File(s)**: `dict_tiny/wordbook.py` (NEW)
**Status**: pending

- `_get_data_dir()` — module-level helper using `os` + `sys.platform` to resolve cross-platform data dir (Linux: `~/.local/share/dict-tiny`, macOS: `~/Library/Application Support/dict-tiny`, Windows: `%LOCALAPPDATA%/dict-tiny`)
- `WordBook.__init__(path=None)` — resolve path via `_get_data_dir() / wordbook.db` if path is None, create parent dir if not exists
- Connection with `check_same_thread=False`, WAL journal mode
- `db_exists()` classmethod — `os.path.isfile()` check
- `_init_db()` — run schema DDL (entries + config tables, indexes)
- Graceful handling of corrupted DB

**Schema**:

```sql
CREATE TABLE IF NOT EXISTS entries (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    text            TEXT NOT NULL UNIQUE,
    source_language TEXT,
    target_language TEXT,
    translator      TEXT,
    timestamp       REAL NOT NULL,
    last_access     REAL NOT NULL,
    access_count    INTEGER NOT NULL DEFAULT 1
);
CREATE INDEX IF NOT EXISTS idx_entries_timestamp   ON entries(timestamp);
CREATE INDEX IF NOT EXISTS idx_entries_last_access ON entries(last_access);
CREATE INDEX IF NOT EXISTS idx_entries_access_count ON entries(access_count);

CREATE TABLE IF NOT EXISTS config (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
```

---

## Task 2: Implement WordBook CRUD methods

**File(s)**: `dict_tiny/wordbook.py`
**Depends on**: Task 1
**Status**: pending

- `record(text, sl, tl, translator) -> bool` — INSERT or UPDATE (last_access, access_count, sl/tl/translator). If count >= 10000 before INSERT, evict oldest (ORDER BY last_access ASC LIMIT 1)
- `get_entry(index) -> WordBookEntry | None` — fetch by 1-based display index (offset = (page-1) * page_size with page=1, page_size=count). Read-only.
- `delete(index) -> bool` — resolve index to id, then DELETE

---

## Task 3: Implement WordBook list and config methods

**File(s)**: `dict_tiny/wordbook.py`
**Depends on**: Task 1
**Status**: pending

- `list_entries(page=1, page_size=20, sort_by='time') -> tuple[list[WordBookEntry], int]` — sort_by: time (timestamp DESC), freq (access_count DESC), recent (last_access DESC). Return paginated entries + total count.
- `list_entries_since(timestamp, page=1, page_size=20) -> tuple[list[WordBookEntry], int]`
- `count() -> int` — SELECT COUNT(*)
- `get_config() -> dict` — {count, default_record}
- `get_default_record() -> bool` — read from config table, default False if not set
- `set_default_record(on: bool)` — upsert config table
- `delete_db()` — close connection, remove file
- `close()` — close connection

All methods wrapped in try/except, return safe defaults on error.

---

## Task 4: Add --record / --no-record flags and lazy init in main.py

**File(s)**: `dict_tiny/main.py`
**Depends on**: Task 2
**Status**: pending

Add to `Dict_tiny` class:

```python
record    = cli.Flag("--record",    help="Record query to word book")
no_record = cli.Flag("--no-record", help="Skip recording this query")
```

Modify `main()` with lazy init logic:

```
if nested_command: return

if --record:                        → should_record=True
elif --no-record:                   → should_record=False
else:
    if DB file exists:              → read default_record from DB
        if default_record is True:  → should_record=True
        else:                       → should_record=False
    else:                           → should_record=False

if should_record:                   → _ensure_wordbook()

store should_record in self for translator to read
```

`_ensure_wordbook()` at module level: shared instance, print error on failure and return None.

Register subcommand at module level:

```python
Dict_tiny.wb = cli.Subcommand('wb', WordBookApp)
```

---

## Task 5: Implement WordBookApp subcommand and sub-subcommands

**File(s)**: `dict_tiny/wordbook.py`
**Depends on**: Task 3, Task 4
**Status**: pending

```python
class WbList(cli.Application):
    page = cli.SwitchAttr(...)
    page_size = cli.SwitchAttr(...)
    sort = cli.SwitchAttr(...)
    since = cli.SwitchAttr(...)
    def main(self): ...

class WbDetail(cli.Application):
    def main(self, index): ...

class WbQuery(cli.Application):
    def main(self, index): ...

class WbDelete(cli.Application):
    def main(self, index): ...

class WbConfig(cli.Application):
    record = cli.SwitchAttr(...)
    def main(self): ...

class WbDbDelete(cli.Application):
    def main(self): ...
```

**CLI interface:**

| Command | Behavior |
|---------|----------|
| `dict-tiny wb list` | Paginated list, "word \| sl→tl \| time \| ×count" per line |
| `dict-tiny wb list --page 2` | Page 2 |
| `dict-tiny wb list --page-size 50` | 50 per page |
| `dict-tiny wb list --sort freq` | Sort by frequency |
| `dict-tiny wb list --sort recent` | Sort by last access |
| `dict-tiny wb list --since 2026-05-01` | Filter by first-record time |
| `dict-tiny wb detail <n>` | Print all fields |
| `dict-tiny wb query <n>` | Re-translate using stored entry |
| `dict-tiny wb delete <n>` | Delete by index |
| `dict-tiny wb config` | Show count + default_record |
| `dict-tiny wb config --record on\|off` | Set default recording |
| `dict-tiny wb db-delete` | Delete DB file |

**WbQuery implementation**:

```python
def main(self, index):
    entry = wb.get_entry(index)
    if not entry:
        print("Entry not found")
        return
    # Build fake argv: [prog, --translator, text]
    # Dispatch through existing translator flow
    # After translation, wb.record(text, sl, tl, translator)
```

**Formatter**: timestamps displayed in local timezone (convert via `datetime.fromtimestamp`).

---

## Task 6: Integrate with Translator

**File(s)**: `dict_tiny/translators/translator.py`
**Depends on**: Task 4
**Status**: pending

In `DefaultTrans.__init__()`:

```python
self.wordbook = getattr(dict_tiny_obj, 'wordbook', None)
```

In `DefaultTrans.extra_action()` — currently a no-op:

```python
def extra_action(self, text):
    if self.wordbook:
        self.wordbook.record(text, self.source_language,
                             self.target_language, self.name)
```

In `DefaultTrans.interactive_loop()` — add after `do_translate()`:

```python
self.extra_action(text)
```

---

## Task 7: Write tests

**File(s)**: `test/test_wordbook.py` (NEW)
**Depends on**: Task 2, Task 3
**Status**: pending

Use `:memory:` SQLite for all WordBook tests.

**Test cases**:

| # | Test | Description |
|---|------|-------------|
| 1 | `test_record_new` | Insert new entry, verify count=1 |
| 2 | `test_record_duplicate` | Insert same text twice, verify access_count=2 |
| 3 | `test_record_eviction` | Insert 10001 entries, verify oldest evicted |
| 4 | `test_get_entry` | Get by index, verify correct fields |
| 5 | `test_get_entry_invalid` | Out-of-range index returns None |
| 6 | `test_list_default` | Default sort by time DESC |
| 7 | `test_list_sort_freq` | Sort by access_count DESC |
| 8 | `test_list_sort_recent` | Sort by last_access DESC |
| 9 | `test_list_pagination` | Page 2 with page_size=3 |
| 10 | `test_list_since` | Filter by timestamp |
| 11 | `test_delete` | Delete existing entry |
| 12 | `test_delete_invalid` | Delete non-existent returns False |
| 13 | `test_delete_db` | Delete file, verify file gone, re-init works |
| 14 | `test_config_default_record` | Set and persist default_record |
| 15 | `test_error_resilience` | Corrupted DB raises no exception |
| 16 | `test_extra_action_hook` | Mock wordbook, verify record called |

---

## Task 8: Verify existing tests not broken

**Depends on**: Task 6
**Status**: pending

```
python -m pytest test/ -v
```

**Expected**: All existing tests pass (71 tests), new wordbook tests pass.

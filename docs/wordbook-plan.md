# Word Book Implementation Plan

## Architecture

```
dict-tiny (main.py)
  ├── WordBook       ← NEW: persistence layer (wordbook.py)
  ├── WordBookApp    ← NEW: wb subcommand (wordbook.py)
  └── Translator     ← MODIFY: extra_action hook
```

WordBook 是持久化层，Translator 通过 `extra_action()` 调用它。两者解耦 — 翻译器不关心 WordBook 是否存在，记录失败也不影响翻译。

## Data Model

**DB path**: `~/.local/share/dict-tiny/wordbook.db` (Linux)，`~/Library/Application Support/dict-tiny/wordbook.db` (macOS)，`%LOCALAPPDATA%/dict-tiny/wordbook.db` (Windows)，通过标准库 `os` + `sys` 解析（`_get_data_dir()`）

```sql
CREATE TABLE IF NOT EXISTS entries (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    text            TEXT NOT NULL UNIQUE,
    source_language TEXT,
    target_language TEXT,
    translator      TEXT,
    timestamp       REAL NOT NULL,    -- UTC Unix timestamp
    last_access     REAL NOT NULL,    -- for LRU eviction
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

- `text` UNIQUE — 一词一行，重复查询只更新不新增
- `translator` — 存储最近一次使用的翻译器名，`wb query` 时沿用
- 容量固定 10000，达到后自动淘汰 `last_access` 最旧的记录

## WordBook API (`dict_tiny/wordbook.py`)

```python
class WordBook:
    def __init__(self, path: str | None = None):
        """path 为 None 时使用 platformdirs 默认路径"""

    # --- 核心操作 ---
    def record(self, text: str, source_language: str | None,
               target_language: str | None, translator: str | None) -> bool:
        """记录一次查询。已存在则 UPDATE 并覆盖 sl/tl/translator"""

    def get_entry(self, index: int) -> WordBookEntry | None:
        """按展示序号获取条目，只读"""

    def delete(self, index: int) -> bool:
        """按展示序号删除"""

    # --- 列表查询 ---
    def list_entries(self, page: int = 1, page_size: int = 20,
                     sort_by: str = 'time') -> tuple[list[WordBookEntry], int]:
        """分页返回 (entries, total)。sort_by: time | freq | recent"""

    def list_entries_since(self, timestamp: float, page: int = 1,
                           page_size: int = 20) -> tuple[list[WordBookEntry], int]:

    def search_entries(self, text: str, page: int = 1, page_size: int = 20,
                       exact: bool = False) -> tuple[list[WordBookEntry], int]:
        """按文本搜索，模糊或精确匹配。返回 (entries, total)"""

    # --- 管理 ---
    def count(self) -> int:
    def get_config(self) -> dict:               # {count, default_record}
    def get_default_record(self) -> bool:
    def set_default_record(self, on: bool):
    def delete_db(self):                        # 关闭连接、删除文件，不重建
    def close(self):
```

**容错原则**: 所有方法内部 `try/except`，异常静默降级，绝不向调用方抛异常。

## CLI Integration (`dict_tiny/main.py`)

### 新增 flags (`Dict_tiny`)

```python
record    = cli.Flag("--record",    help="Record query to word book")
no_record = cli.Flag("--no-record", help="Skip recording this query")
```

### 惰性初始化 (`main()`)

WordBook 实例 `Dict_tiny.wordbook` 初始为 None，翻译流程结束后 `extra_action()` 检查它是否存在，存在则记录。

```python
def main(self, *words):
    if self.nested_command:
        return  # wb 子命令由 WordBookApp 自行初始化

    # 是否需要记录？
    if self.record:
        should_record = True
    elif self.no_record:
        should_record = False
    else:
        # 没有指定 --record/--no-record：

        # 如果 DB 不存在，默认不记录，什么都不要做
        if not WordBook.db_exists():
            should_record = False
        else:
            # DB 已存在（用户之前开过记录），读取当时的默认设置
            wb = _ensure_wordbook()  # 打开已有 DB，不新建
            should_record = wb.get_default_record() if wb else False
            if should_record:
                Dict_tiny.wordbook = wb  # 保留实例供 extra_action 使用

    if should_record and Dict_tiny.wordbook is None:
        Dict_tiny.wordbook = _ensure_wordbook()

    # 翻译流程（extra_action 中检查 Dict_tiny.wordbook）
```

关键：不记录就不创建 DB；`db_exists()` 走 `os.path.isfile()`，不涉及建立连接。

`_ensure_wordbook()`: 创建或返回共享实例，创建失败时打印提示并返回 None。

### Recording decision

```
--record    → 记录
--no-record → 不记录
(neither)   → wb.get_default_record() if wb else False
```

### WordBookApp 子命令

在 `Dict_tiny` 类级别注册为 plumbum 子命令：

```python
Dict_tiny.wb = cli.Subcommand('wb', WordBookApp)
```

`WordBookApp` 自身也是一个 `cli.Application`，其 `main()` 中先 `_ensure_wordbook()` 确保 DB 可用，然后通过 `nested_command` 将请求分派给各个子命令：

```python
class WordBookApp(cli.Application):
    wb_list = cli.Subcommand('list', WbList)
    wb_query = cli.Subcommand('query', WbQuery)
    wb_detail = cli.Subcommand('detail', WbDetail)
    wb_delete = cli.Subcommand('delete', WbDelete)
    wb_config = cli.Subcommand('config', WbConfig)
    wb_db_delete = cli.Subcommand('db-delete', WbDbDelete)

    def main(self):
        if self.nested_command:
            return
        # 无参数时打印帮助
        print("Usage: dict-tiny wb <command> ...")
```

各子命令实现：

| 子命令       | 实现                                                                                                        |
| ------------ | ----------------------------------------------------------------------------------------------------------- |
| `WbList`     | `list_entries(page, page_size, sort_by)`，默认按时间倒序，`--since` 过滤用 `list_entries_since()`。表格展示 |
| `WbSearch`   | `search_entries(text, page, page_size, exact)`。表格展示，格式同 `WbList`                                   |
| `WbDetail`   | `get_entry(n)` → 打印 text / sl→tl / translator / timestamp / access_count 等全部字段                       |
| `WbQuery`    | `get_entry(n)` → 用 entry 的 sl/tl/translator 调用翻译器重新翻译，完成后 `record()` 刷新 last_access        |
| `WbDelete`   | `delete(n)`                                                                                                 |
| `WbConfig`   | 无参数时打印 count + default_record；`--record on\|off` 调用 `set_default_record()`                         |
| `WbDbDelete` | `delete_db()`，删除文件后打印提示                                                                           |

对应 CLI：

```
dict-tiny wb list [--page N] [--page-size N] [--sort time|freq|recent] [--since DATE]
dict-tiny wb query <n>                     → get_entry() → re-translate → record() 刷新 last_access
dict-tiny wb detail <n>                    → get_entry() → pretty print 全部字段
dict-tiny wb delete <n>
dict-tiny wb search <text> [--page N] [--page-size N] [--exact]
dict-tiny wb config [--record on|off]
dict-tiny wb db-delete
```

## Translator Integration (`dict_tiny/translators/translator.py`)

`DefaultTrans.__init__()` 中保存 `self.wordbook` 和 `self.record_query` 标志。  
`extra_action()` 中调用 `self.wordbook.record(text, sl, tl, translator_name)`。  
`interactive_loop()` 在 `do_translate()` 后调用 `extra_action(text)`。

## Tests (`test/test_wordbook.py`)

使用 `:memory:` SQLite 数据库。

- record / re_record — 插入和重复插入
- list_entries — 分页、排序、since 过滤
- delete — 按序号删除
- delete_db — 删除后重建
- Config persistence — set_default_record 跨连接持久化
- extra_action() / interactive_loop() recording hook
- Error resilience — 损坏的 DB 不抛异常
- nested_command guard

## Files Changed

| File                                  | Action                                       |
| ------------------------------------- | -------------------------------------------- |
| `dict_tiny/wordbook.py`               | **NEW** — WordBook + WordBookApp             |
| `dict_tiny/main.py`                   | **MODIFY** — flags, lazy init, subcommand    |
| `dict_tiny/translators/translator.py` | **MODIFY** — extra_action + interactive_loop |
| `test/test_wordbook.py`               | **NEW**                                      |

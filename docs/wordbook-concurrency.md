---
name: wordbook_concurrency
description: WordBook SQLite 并发安全的已知问题和修改建议
type: project
originSessionId: 9444fb7d-2efe-45cf-b1cd-95315cdd4d2b
---
## WordBook 并发问题

### 当前状态

WordBook 使用 SQLite WAL 模式，读写不互斥。所有 DB 操作包在 `try/except` 中，异常静默降级。

### 已知问题

1. **没有设置 busy_timeout** — SQLite 默认 busy_timeout 为 0，两个进程同时写时第二个立刻报 `SQLITE_BUSY`，被 except 吞掉后该条记录丢失
2. **SELECT → INSERT 竞态** — 进程 A 查 `hello` 不存在，进程 B 也查不存在，两者同时 INSERT，UNIQUE 约束导致第二个写入失败

### 影响评估

dict-tiny 是 CLI 工具，同时运行两个实例的概率极低。即便发生，至多丢一条记录，翻译流程不受影响。

### 修改建议

| 问题 | 方案 | 复杂度 |
|------|------|--------|
| busy_timeout | 连接后执行 `PRAGMA busy_timeout=3000` | 一行 |
| SELECT → INSERT 竞态 | 改用 `INSERT OR IGNORE` + 后续 UPDATE | 低 |

以当前的使用场景，两个问题的实际影响极小，可以不处理。

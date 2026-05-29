# TODO

- [ ] 翻译失败或没有结果时不写入 wordbook（目前 `WbQuery` 和 `translate()` 在翻译完成后无条件 record，需要先判断翻译结果是否有效）
- [ ] SQLite busy_timeout 默认 0，并发写入会丢记录。建议加 `PRAGMA busy_timeout=3000`
- [ ] SELECT → INSERT 竞态：同时查同一条不存在的记录时，UNIQUE 约束导致失败。考虑改用 `INSERT OR IGNORE` + 后续 UPDATE

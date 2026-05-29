# TODO

- [ ] 看下测试用例覆盖程度
- [ ] SQLite busy_timeout 默认 0，并发写入会丢记录。建议加 `PRAGMA busy_timeout=3000`
- [ ] SELECT → INSERT 竞态：同时查同一条不存在的记录时，UNIQUE 约束导致失败。考虑改用 `INSERT OR IGNORE` + 后续 UPDATE

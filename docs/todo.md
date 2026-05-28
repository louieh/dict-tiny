# TODO

- [ ] source_language / target_language 记录不准确，需要调整
- [ ] wb delete/detail/query 目前用的是展示序号（1-based OFFSET），删除后序号漂移会导致误操作。考虑改用 id 作为操作目标（用户从 `wb list` 看到 id 后再操作）
- [ ] SQLite busy_timeout 默认 0，并发写入会丢记录。建议加 `PRAGMA busy_timeout=3000`
- [ ] SELECT → INSERT 竞态：同时查同一条不存在的记录时，UNIQUE 约束导致失败。考虑改用 `INSERT OR IGNORE` + 后续 UPDATE

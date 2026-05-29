# TODO

- [ ] SELECT → INSERT 竞态：同时查同一条不存在的记录时，UNIQUE 约束导致失败。考虑改用 `INSERT OR IGNORE` + 后续 UPDATE

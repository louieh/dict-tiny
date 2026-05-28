# PRD: 单词本功能 (Word Book)

## 1. 概述

为 dict-tiny CLI 工具增加单词本功能，持久化保存用户的查询记录，支持查询历史回顾、单词本管理和自动清理策略。

## 2. 功能需求

### 2.1 查询记录

- 用户每次查询的单词/文本、源语言（source_language）、目标语言（target_language）、查询时间自动保存到单词本
- 重复查询同一单词时，更新**查询次数**（`access_count`）、时间戳和语种信息（覆盖），不产生重复记录
- 交互模式（`-i`）下的每次查询同样记录

### 2.2 记录控制

用户可通过三种方式控制是否记录：

| 方式       | 说明                                                                   |
| ---------- | ---------------------------------------------------------------------- |
| 默认记录   | config 表存储，通过 `dict-tiny wb config --record on` 设置（默认关闭） |
| 默认不记录 | `dict-tiny wb config --record off` 切换默认行为                        |
| 手动开关   | `--record` 强制记录，`--no-record` 强制不记录，覆盖默认行为            |

### 2.3 查询历史

- `dict-tiny wb list` — 分页展示（默认每页 20 条，按时间倒序）
- 支持 `--sort freq`（按频率）、`--sort recent`（按最近访问）切换排序
- 支持 `--since <日期>` 按首次查询时间过滤
- 支持 `--page` / `--page-size` 翻页和控制每页条数

展示内容：

- 序号
- 查询内容（单词/文本）
- 语种方向（源语言 → 目标语言）
- 翻译器（仅 `detail` 展示）
- 查询时间（格式化的本地日期时间，存储为 UTC Unix 时间戳）
- 查询次数（`access_count`）

### 2.4 单词本管理

| 操作         | 说明                                                                  |
| ------------ | --------------------------------------------------------------------- |
| 交互浏览     | `dict-tiny wb` 显示帮助信息                                           |
| 查看帮助     | `dict-tiny wb --help` 显示帮助信息                                    |
| 列出记录     | `dict-tiny wb list`，默认按时间倒序分页展示（每页 20 条）             |
| 查看详情     | `dict-tiny wb detail <索引>`                                          |
| 重新查询     | `dict-tiny wb query <索引>` 对历史记录再次翻译                        |
| 删除记录     | `dict-tiny wb delete <索引>`                                          |
| 查看状态     | `dict-tiny wb config` 查看当前数量 / 默认记录设置             |
| 删除数据库   | `dict-tiny wb db-delete` 删除数据库文件，下次使用时自动新建           |
| 设置默认记录 | `dict-tiny wb config --record <on\|off>` 切换默认是否记录查询         |

### 2.1a 惰性初始化

单词本功能**默认关闭**，DB 文件在以下时机按需创建：

- 用户使用了 `dict-tiny wb` 子命令
- 用户显式传了 `--record` 参数

默认情况下不创建任何 DB 文件，无额外磁盘和 IO 开销。

### 2.4a 重置与异常恢复

- 当数据库文件损坏或异常时，用户可通过 `dict-tiny wb db-delete` 删除数据库文件
- `wb db-delete` 仅删除文件，下次使用 `--record` 或 `wb` 命令时自动新建
- 启动时若检测到数据库损坏（`sqlite3` 连接/查询异常），自动提示用户使用 `dict-tiny wb db-delete` 修复

### 2.4b 错误容错

所有 DB 操作内部统一 `try/except`，任何异常静默降级为不记录，不干扰翻译主流程。用户自行修改或损坏 DB 文件不会导致 CLI 报错。

### 2.5 容量与清理

固定静默上限 10000 条，达到后自动淘汰最久未访问的记录，对用户完全透明，无需关心也无需配置。

### 2.7 重新查询（wb query）

**实现：**

```
dict-tiny wb query <索引> 流程：
  1. 取出 entry.text / entry.source_language / entry.target_language / entry.translator
  2. 若 translator 有值 → 调用对应的翻译器
  3. 若 translator 为 NULL → 使用默认翻译器（youdaodict）
  4. 若 sl/tl 有值 → 传给翻译器
  5. 若 sl/tl 为 NULL → 翻译器自动检测（行为等同于 dict-tiny hello）
  6. 更新 last_access 和 access_count
```

## 3. 用户交互示例

```bash
# 查询并记录（第2次查询 hello，次数递增）
$ dict-tiny hello --record

# 查询但不记录
$ dict-tiny --no-record hello

# 查看单词本（分页展示）
$ dict-tiny wb list
  1. hello             | en → zh      | 2026-05-27 14:30 | ×5
  2. world             | en → zh      | 2026-05-27 14:25 | ×2
  ...
 20. apple             | en → zh      | 2026-04-01 09:15 | ×1

Page 1/10 (Total: 200 / 1000)

# 翻页
$ dict-tiny wb list --page 2

# 按查询频率排序
$ dict-tiny wb list --sort freq

# 从指定日期开始展示
$ dict-tiny wb list --since 2026-05-01

# 每页 50 条
$ dict-tiny wb list --page-size 50

# 重新查询历史记录
$ dict-tiny wb query 1

# 查看记录详情
$ dict-tiny wb detail 1

# 删除记录
$ dict-tiny wb delete 1

# 查看状态
$ dict-tiny wb config
Path: /home/user/.local/share/dict-tiny/wordbook.db (Linux)
Entries: 200 / 10000
```

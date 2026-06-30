# Dict-tiny

[![PyPI version](https://img.shields.io/pypi/v/dict-tiny.svg)](https://pypi.python.org/pypi/dict-tiny/) [![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/louieh/dict-tiny/upload-dict-tiny-package.yml)](https://github.com/louieh/dict-tiny/actions?query=workflow%3A%22Upload+Dict-tiny+Python+Package%22) [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT) [![Downloads](https://pepy.tech/badge/dict-tiny)](https://pepy.tech/project/dict-tiny)

A command-line tool that integrates Youdao Dict and Google Translate.

Just for fun :)

- **Youdao Dict** — bilingual dictionary with phonetic symbols, definitions, examples
- **Google Translate** — multi-language translation and language detection
- **Interactive mode** — continuous querying with tab auto-completion
- **Word book** — records and queries translation history

</br>

<p align="left"><img src="./assets/demo_2_0_0.gif" alt="demo_2_0_0" width="65%" height="65%" /></p>

## Installation

Requires Python >= 3.11.

```bash
$ pip install dict-tiny
```

To upgrade:

```bash
$ pip install --upgrade dict-tiny
```

## Quick start

```bash
# Youdao Dict (default)
$ dict-tiny book
```

```bash
# Google Translate, auto-detect source
$ dict-tiny -g book
```

```bash
# Interactive mode with tab completion
$ dict-tiny -y -i
```

## Usage

### Options

```bash
$ dict-tiny

Usage:
    dict-tiny [SWITCHES] [SUBCOMMAND [SWITCHES]] words...

GoogleTranslate:
    --detect-language                      Detect the language of the given text
    -g, --google                           Use Google Translate

Meta-switches:
    -h, --help                             Prints this help message and quits
    --help-all                             Prints help messages of all sub-commands and quits
    -v, --version                          Prints the program's version and quits

Switches:
    -c, --clipboard                        Use the contents of the clipboard.
    -i, --interactive                      Interactive mode
    --no-record                            Skip recording this query
    --record                               Record query to word book
    --sl, --source-language VALUE:str      Source language (YoudaoDict only supports en/fr/ja/ko)
    --tl, --target-language VALUE:str      Target language (YoudaoDict only supports en/fr/ja/ko)

YoudaoDict:
    -m, --more                             Get more details
    -y, --youdao                           Use Youdao Dictionary to translate

Sub-commands:
    wb                                     see 'dict-tiny wb --help' for more info
```

### Youdao Dict

Youdao is the default translator. It supports Chinese↔English, Chinese↔French,
Chinese↔Japanese, and Chinese↔Korean. The default is Chinese↔English.

Language codes:

| Code | Language |
| ---- | -------- |
| `en` | English  |
| `fr` | French   |
| `ja` | Japanese |
| `ko` | Korean   |

Chinese is the implicit counterpart — no need to specify `zh`. For example, Chinese↔Japanese requires `--target-language ja` or `--source-language ja`.

<details>
<summary>English query</summary>

```bash
$ dict-tiny book

>>> YoudaoDict <<<
book
======
[美]bʊk [英]bʊk

n. 书，书籍；本子，簿册；（长篇作品的）篇，卷，部；装订成册之物；赌局，打赌；账册，账簿
v. 预订，预约；（警方）将……记录在案；（裁判）记名警告
 【名】 （Book）（英）布克，（瑞典）博克，（朝）北（人名）
复数: books, 第三人称单数: books, 现在分词: booking, 过去式: booked, 过去分词: booked
```

</details>

<details>
<summary>Chinese query</summary>

```bash
$ dict-tiny -y 书

>>> YoudaoDict <<<
书
===
shū

book
书，书籍；本子，簿册；（长篇作品的）篇，卷，部；装订成册之物；赌局，打赌；账册，账簿；预订，预约；（警方）将……记录在案；（裁判）记名警告；【名】 （Book）（英）布克，（瑞典）博克，（朝）北（人名）；

write
写作，编写；写道；写信；书写，写字；谱写（音乐作品）；编写（计算机程序）；将（计算机中的）数据写入（磁盘或其他储存媒体）；填写（表格、支票等），拟定；（笔）能写字；拼写；<加，南非>参加（笔试）；书写，手写（与铅印相对）；以写作为生；承保（保险单）；

letter
信，信函；字母；<美>（缝制在运动服上的）校运动队首字母标志；<英，非正式>（代表学位或职位等资格的）首字母缩略词（letters）；文学；法律文书，正式文书（letters）；字面确切含义；（印刷）一种铅字字体；<古> 学识，渊博的学问；用字母标注；把字母印刷（或缝制等）于；<美>赢得学校运动队的字母标志；【名】 （Letter）（美、英、巴西）莱特（人名）；

script
剧本，讲稿；笔迹，手写体；连写体，草体；字体；（一种语言的）字母系统，字母表；<英>（考生的）笔试答卷；脚本（程序）（计算机的一系列指令）；<非正式>（医生的）处方；期待，计划；写剧本，写讲稿；事先准备，计划；
```

</details>

<details>
<summary>More detail with -m</summary>

```bash
$ dict-tiny -y dictionary -m

>>> YoudaoDict <<<
dictionary
============
[美]ˈdɪkʃəneri [英]ˈdɪkʃən(ə)ri

n. 字典，词典；专业词典，术语大全；电子词典；双语词典
复数: dictionaries

📖 collins:
dictionary【ˈdɪkʃənərɪ】

======== N-COUNT 可数名词 ========
A dictionary is a book in which the words and phrases of a language are listed alphabetically, together with their meanings or their translations in another language. 词典
 例: ...a Spanish-English dictionary.
     …一本西班牙语—英语词典。
```

</details>

<details>
<summary>Specify target / source language</summary>

```bash
# Translate to Japanese
$ dict-tiny -y 进击的巨人 --target-language ja

>>> YoudaoDict <<<
进击的巨人
=======
jinjidejuren

進撃の巨人（しんげきのきょじん）（日本漫画家谏山创创作的少年漫画作品，于2009年在讲谈社旗下的漫画杂志《别册少年》上开始连载。）
```

```bash
# French source
$ dict-tiny -y Bonjour --source-language fr

>>> YoudaoDict <<<
Bonjour
=========
bɔ̃ʒu:r

[m.]
早安，日安，白天好，你好
```

```bash
# Korean source
$ dict-tiny -y "go는 구글이 만든 오픈 소스 프로그래밍 언어이다" --sl ko

>>> YoudaoDict <<<
go는 구글이 만든 오픈 소스 프로그래밍 언어이다
=============================
go는 谷歌开发的开源程序设计语言
```

</details>

### Google Translate

Add `-g` / `--google` to use Google Translate. Supports all [ISO 639-1](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes) languages.

`--source-language` specifies the source language of the input text. In most cases
this is optional, as the Google Translate API automatically detects the source
language. If you specify the wrong source language, the translation result may not
be what you expect.

The default target language is English. Use `--target-language` to change it, or
set `DICT_TINY_TARGET_LAN` environment variable (command-line flag overrides
environment variable).

```bash
$ dict-tiny -g book

>>> GoogleTranslate <<<
book
======
output: 书
detected language: en
```

<details>
<summary>Specify target / source language</summary>

```bash
$ dict-tiny -g operation system --target-language ja

>>> GoogleTranslate <<<
operation system
==================
output: オペレーションシステム
detected language: en
```

You can use ISO codes or full language names:

```bash
$ dict-tiny -g book --target-language zh --source-language en

>>> GoogleTranslate <<<
book
======
output: 书
source language: en
```

```bash
$ dict-tiny -g book --target-language German --source-language English

>>> GoogleTranslate <<<
book
======
output: Buch
source language: english
```

</details>

<details>
<summary>Detect language</summary>

```bash
$ dict-tiny -g --detect-language español

>>> GoogleTranslate <<<
español
=========
confidence: 0.49805447459220886
input: español
language: es
name: Spanish
```

**Note:** `--detect-language` must be used together with `-g`.

</details>

### Interactive mode

Add `-i` to enter interactive mode. Press <kbd>Ctrl</kbd> + <kbd>d</kbd> to exit.

- Continuously query words in an interactive session
- Press <kbd>Tab</kbd> for word auto-completion (powered by Youdao, supports Chinese, English, French, Japanese, Korean)
- Settings (target/source language) are fixed once in interactive mode

```bash
$ dict-tiny -y -i
```

### Clipboard

Use `-c` / `--clipboard` to translate clipboard content:

```bash
$ dict-tiny -c -y
```

**Note:** `-c` has lower priority than passing a word directly.

### Multiple translators

Use `-y` and `-g` together to show results from both translators:

```bash
$ dict-tiny formulation -y -g

>>> YoudaoDict <<<
formulation
=============
[美]ˌfɔːrmjuˈleɪʃ(ə)n [英]ˌfɔːmjuˈleɪʃ(ə)n

n. （政策、计划等的）制定，构想；（想法的）阐述方式，表达方法；（药品或化妆品的）配方，配方产品
复数: formulations
--------------------
>>> GoogleTranslate <<<
formulation
=============
output: formulation
detected language: en
```

## Word book

The word book records translation history. Recording is **off by default**.

Use `--record` to record a single query, or set it as default with:

```bash
$ dict-tiny wb config --record on
```

### Commands

```
$ dict-tiny wb <command> [...]

Commands: list, detail, query, search, delete, config, db-delete
```

Each subcommand supports `--help`, e.g. `dict-tiny wb list --help`.

<details>
<summary>wb list — list entries</summary>

```bash
$ dict-tiny wb list --sort freq

   ID   Text           Lang         Created        Count
 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
     1   hello         en→zh     2026-05-28 16:36    ×252
     2   world         en→zh     2026-05-28 16:37    ×100
     3   apple         en→ja     2026-05-28 16:40     ×53
     4   resilience    zh↔en     2026-06-01 16:15      ×1
     5   guardrails    zh↔en     2026-06-01 15:22      ×1

Page 1/1  (5 entries, limit 10000)
```

When the entry limit (10000) is reached, the least recently queried entry is evicted.

| Option          | Description                       |
| --------------- | --------------------------------- |
| `--sort SORT`   | `created`, `freq`, or `recent`    |
| `--since DATE`  | Filter by start date (YYYY-MM-DD) |
| `--page N`      | Page number (default: 1)          |
| `--page-size N` | Entries per page (default: 20)    |

**Note:**

- The Lang column shows the effective languages — defaults are shown if not
  explicitly set (e.g. Youdao defaults to `zh↔en`). Use `wb detail <ID>` to see the
  raw stored values.

- The stored translator, source language, and target language are updated to the
  values used in the most recent query for that entry.

</details>

<details>
<summary>wb detail — show entry details</summary>

```bash
$ dict-tiny wb detail 1

  Text:              hello
  Source Language:
  Target Language:
  Translator:        youdaodict
  Created:           2026-06-01 10:30:00
  Last Query:        2026-06-01 11:20:00
  Access Count:      3
```

</details>

<details>
<summary>wb query — re-translate an entry</summary>

Re-translates the entry using its stored text and languages. Supports overriding
the translator or languages via top-level flags (e.g., `-g`, `--target-language`).

```bash
# Re-translate entry ID 1 with its stored translator
$ dict-tiny wb query 1
```

```bash
# Re-translate with Google Translate, target Japanese
$ dict-tiny -g --target-language ja wb query 1
```

</details>

<details>
<summary>wb search — search entries</summary>

Fuzzy search by default (`LIKE '%text%'`). Use `--exact` for exact match.

```bash
$ dict-tiny wb search hello
```

```bash
$ dict-tiny wb search hello --exact
```

| Option          | Description                       |
| --------------- | --------------------------------- |
| `--exact`       | Exact match instead of fuzzy      |
| `--sort SORT`   | `created`, `freq`, or `recent`    |
| `--since DATE`  | Filter by start date (YYYY-MM-DD) |
| `--page N`      | Page number (default: 1)          |
| `--page-size N` | Entries per page (default: 20)    |

</details>

<details>
<summary>wb delete — delete an entry</summary>

```bash
$ dict-tiny wb delete 1
Entry ID:1 deleted.
```

</details>

<details>
<summary>wb config — view or change settings</summary>

```bash
$ dict-tiny wb config
  Entries:          5 / 10000
  Default Recording: OFF
```

```bash
$ dict-tiny wb config --record on
Default recording: ON
```

Use `--record on` or `--record off` to enable or disable default recording.

</details>

<details>
<summary>wb db-delete — delete the database</summary>

Deletes the entire word book database file.

```bash
$ dict-tiny wb db-delete
Word book database deleted.
```

</details>

### Notes

- Input text is limited to 3000 characters. Both Youdao Dict and Google Translate
  will reject longer input.

- Subcommands like `detail`, `query`, and `delete` take the entry ID as shown in
  the first column of `wb list` output. The ID is auto-incremented and may be
  non-contiguous; it does not reflect the current display order.

- Top-level flags (`-y`, `-g`, `--record`, `--no-record`, `--sl`, `--tl`) **must** come before `wb`:

  ```bash
  dict-tiny -y --no-record wb query 1   # ✓
  dict-tiny wb query 1 -y --no-record   # ✗
  ```

## Environment variables

| Variable                  | Default      | Description                                           |
| ------------------------- | ------------ | ----------------------------------------------------- |
| `DICT_TINY_DEFAULT_TRANS` | `youdaodict` | Default translator (`youdaodict` / `googletranslate`) |
| `DICT_TINY_TARGET_LAN`    |              | Default target language                               |
| `DICT_TINY_SOURCE_LAN`    |              | Default source language                               |

Command-line flags override environment variables.

## Uninstall

Before uninstalling, you may want to delete the word book database:

```bash
$ dict-tiny wb db-delete
```

Then uninstall the package:

```bash
$ pip uninstall dict-tiny
```

## License

[MIT](https://github.com/louieh/dict-tiny/blob/master/LICENSE)

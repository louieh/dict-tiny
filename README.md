# Dict-tiny

[![PyPI version](https://img.shields.io/pypi/v/dict-tiny.svg)](https://pypi.python.org/pypi/dict-tiny/) [![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/louieh/dict-tiny/upload-dict-tiny-package.yml)](https://github.com/louieh/dict-tiny/actions?query=workflow%3A%22Upload+Dict-tiny+Python+Package%22) [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT) [![Downloads](https://pepy.tech/badge/dict-tiny)](https://pepy.tech/project/dict-tiny)

A command-line tool that integrates Youdao Dict and Google Translate.

Just for fun :)

## Features

- Youdao dictionary
- Google Translate
- Interactive mode with word auto-completion

## Installing

Install with `pip`. (Python >= 3.9)

```bash
$ pip install dict-tiny
```

## Upgrading

```bash
$ pip install --upgrade dict-tiny
```

## Options

```bash
$ dict-tiny

Usage:
    dict-tiny [SWITCHES] words...

GoogleTranslate:
    --detect-language                   Detect the language of the given text
    -g, --google                        Use Google Translate

Meta-switches:
    -h, --help                          Prints this help message and quits
    --help-all                          Prints help messages of all sub-commands and quits
    -v, --version                       Prints the program's version and quits

Switches:
    -c, --clipboard                        Use the contents of the clipboard.
    --default-translator VALUE:str         Set default translator
    -i, --interactive                      Interactive mode
    --sl, --source-language VALUE:str      Source language of the input text
    --tl, --target-language VALUE:str      What language you want to translate into

YoudaoDict:
    --legacy                               Use legacy translate method
    -m, --more                             Get more details
    -y, --youdao                           Use Youdao Dictionary to translate
```

## Details and examples

### Youdao Dict

Add `-y` / `--youdao` to use Youdao Dict:

You can use Youdao for Chinese-English, Chinese-Japanese, Chinese-French, and Chinese-Korean translation. The default is Chinese-English translation.

**Note:** When using non-Chinese↔English translation, you need to specify `--source-language` or `--target-language`. For example, Chinese↔Japanese requires at least one of `--source-language ja` or `--target-language ja`.

```bash
$ dict-tiny -y book

>>> YoudaoDict <<<
book
======
[美]bʊk [英]bʊk

n. 书，书籍；本子，簿册；（长篇作品的）篇，卷，部；装订成册之物；赌局，打赌；账册，账簿
v. 预订，预约；（警方）将……记录在案；（裁判）记名警告
 【名】 （Book）（英）布克，（瑞典）博克，（朝）北（人名）
复数: books, 第三人称单数: books, 现在分词: booking, 过去式: booked, 过去分词: booked
```

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
信，信函；字母；<美>（缝制在运动服上的）校运动队首字母标志；<英，非正式>（代表学位或职位等资格的）首字母缩略词（letters）；文学；法律文书，正 式文书（letters）；字面确切含义；（印刷）一种铅字字体；<古> 学识，渊博的学问；用字母标注；把字母印刷（或缝制等）于；<美>赢得学校运动队的字母标志；【名】 （Letter）（美、英、巴西）莱特（人名）；

script
剧本，讲稿；笔迹，手写体；连写体，草体；字体；（一种语言的）字母系统，字母表；<英>（考生的）笔试答卷； 脚本（程序）（计算机的一系列指令）；<非正式>（医生的）处方；期待，计划；写剧本，写讲稿；事先准备，计划；

```

Use `-m` / `--more` to get more detailed translations for the word:

```bash
$ dict-tiny -y 曾经 -m

>>> YoudaoDict <<<
曾经
====
céng jīng

once
一次， 一回；曾经，一度；任何一次，从来；乘以一；一.....就， 一旦；一次；

ever
曾经，从来，在任何时候；一直，始终；越来越，愈发；究竟，到底；非常，确实；【名】 （Ever）（英）埃弗，（俄）叶韦尔，（西、法）埃韦尔（人名）；


📖 《吴光华汉英大辞典》:
once
  He once lived in Shanghai.
  他曾经在上海住过。
  She has taken part in a major battle for oil.
  她曾经参加过石油大会战。
  I have seen him before.
  我曾经见到过他。


📖 《现代汉语规范词典》:
曾经 [céngjīng] (副词)
参见1557页“已经”的提示。

表示从前有过某种动作、行为或情况
  例: 她曾经跳过芭蕾舞
  例: 他十年前曾经去过日本。
```

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

Specify `--target-language` to translate to other languages.

```bash
$ dict-tiny -y 进击的巨人 --target-language ja

>>> YoudaoDict <<<
进击的巨人
=======
jinjidejuren

進撃の巨人（しんげきのきょじん）（日本漫画家谏山创创作的少年漫画作品，于2009年在讲谈社旗下的漫画杂志《别册少年》上开始连载。）
```

```bash
$ dict-tiny -y Bonjour --source-language fr

>>> YoudaoDict <<<
Bonjour
=========
bɔ̃ʒu:r

[m.]
早安，日安，白天好，你好
```

```bash
$ dict-tiny -y go는 구글이 만든 오픈 소스 프로그래밍 언어이다 --sl ko

>>> YoudaoDict <<<
go는 구글이 만든 오픈 소스 프로그래밍 언어이다
=============================
go是谷歌开发的开源程序设计语言
```

### Google Translate

Add `-g` / `--google` to use Google Translate:

```bash
$ dict-tiny -g book

>>> GoogleTranslate <<<
book
======
output: 书
detected language: en
```

Add `--target-language` to specify the language to translate results into：

```bash
$ dict-tiny -g operation system --target-language ja

>>> GoogleTranslate <<<
operation system
==================
output: オペレーションシステム
detected language: en
```

Add `--source-language` to specify the source language of the input text. In most cases this is optional, as the Google Translate API automatically detects the source language.

If you specify the wrong source language, the translation result may not be what you expect.

Use `--detect-language` to detect the language type instead:

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

**Note:**

- Make sure Google services are available in your network environment.

- The source and target languages for Google Translate are identified using the [iso-639-1](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes) codes.

  ```bash
  $ dict-tiny -g book --target-language zh --source-language en

  >>> GoogleTranslate <<<
  book
  ======
  output: 书
  source language: en
  ```

  You can also enter the ISO language name:

  ```bash
  $ dict-tiny -g book --target-language German --source-language English

  >>> GoogleTranslate <<<
  book
  ======
  output: Buch
  source language: English
  ```

- Set the environment variable `$DICT_TINY_TARGET_LAN` so you don't have to specify the target language each time. If you also pass `--target-language` on the command line, it overrides the environment variable.
- The default `target-language` is `Chinese` .

### Interactive mode

You can enter interactive mode for any translator by adding `-i`. Press <kbd>Ctrl</kbd> + <kbd>d</kbd> to exit.

In interactive mode you can:

- Continuously query words in an interactive session.
- Press <kbd>Tab</kbd> for word auto-completion (using Youdao's auto-completion function, currently only supports Chinese, English, French, Korean, Japanese)
- Settings cannot be changed after entering interactive mode, such as target-language or source-language. You need to exit and re-enter to change them.

### Other

#### Default behavior

- Youdao Dict is the default translator used when no translator is specified.

  ```bash
  $ dict-tiny 机器学习

  >>> YoudaoDict <<<
  机器学习
  ======
  machine learning
  ```

  You can use the environment variable `$DICT_TINY_DEFAULT_TRANS` to set the default translator. There are two options described above: `YoudaoDict` and `GoogleTranslate`. Case insensitive.

- For Youdao Dict and Google Translate, if the target language is not specified, Chinese and English are used as the target language for one another.
- In non-interactive mode, multiple translators can be used at the same time, for example `dict-tiny formulation -y -g`.

  ```bash
  $ dict-tiny formulation -y -g

  >>> YoudaoDict <<<
  formulation
  =============
  英[ˌfɔːmjuˈleɪʃ(ə)n]美[ˌfɔːrmjuˈleɪʃ(ə)n]
  n. （政策、计划等的）制定，构想；（想法的）阐述方式，表达方法；（药品或化妆品的）配方，配方产品
  >>> GoogleTranslate <<<
  formulation
  =============
  output: 公式
  detected language: en
  ```

#### Use clipboard content

Use `-c`/`--clipboard` to use the contents of the clipboard:

```bash
$ dict-tiny -c -y

>>> YoudaoDict <<<
encounter
===========
英[ɪnˈkaʊntə(r)]美[ɪnˈkaʊntər]
v. 遭遇；偶遇，邂逅
n. 偶遇，邂逅；经历，体验；冲突；比赛，交锋
```

**Note:**

- `-c`/`--clipboard` has lower priority than passing a word directly. If you supply both, `-c` is ignored.

### Environment variables

| name                      | default    | description                                                       |
| ------------------------- | ---------- | ----------------------------------------------------------------- |
| `DICT_TINY_TARGET_LAN`    |            | Specify the default target language.                              |
| `DICT_TINY_SOURCE_LAN`    |            | Specify the default source language.                              |
| `DICT_TINY_DEFAULT_TRANS` | youdaodict | Specify the default translator.<br>`YoudaoDict` `GoogleTranslate` |

## License

[MIT](https://github.com/louieh/dict-tiny/blob/master/LICENSE)

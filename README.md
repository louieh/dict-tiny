# Dict-tiny

[![PyPI version](https://img.shields.io/pypi/v/dict-tiny.svg)](https://pypi.python.org/pypi/dict-tiny/) [![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/louieh/dict-tiny/upload-dict-tiny-package.yml)](https://github.com/louieh/dict-tiny/actions?query=workflow%3A%22Upload+Dict-tiny+Python+Package%22) [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT) [![Downloads](https://pepy.tech/badge/dict-tiny)](https://pepy.tech/project/dict-tiny)


A command line translator that integrates with Google Translate, ~~DeepL Translator~~ and Youdao Dict

Just for fun :)



## Installation

You can install `dict-tiny` via pip. (Python 3 only)

```shell
$ pip install dict-tiny
```



## Upgrading

```shell
$ pip install --upgrade dict-tiny
```



## Usage

### Youdao Dict

```python
$ dict-tiny book
>>> Youdao Dict <<<
book  英[bʊk]美[bʊk]
===================
n. 书籍；卷；账簿；名册；工作簿
vt. 预订；登记
n. (Book)人名；(中)卜(广东话·威妥玛)；(朝)北；(英)布
```

```python
$ dict-tiny 书
>>> Youdao Dict <<<
书  [shū]
=========
n.book;letter;script
vt.write
```

Use `-m`/`--more` to get more detail translation for word:

```python
$ dict-tiny 曾经 -m
>>> Youdao Dict <<<
曾经  [céng jīng]
=================
adv.once;ever

more detail:
======== 副词 ========
1:
  （表示有过某些行为或情况） once:
  He once lived in Shanghai.
  他曾经在上海住过。
  She has taken part in a major battle for oil.
  她曾经参加过石油大会战。
```

```python
$ dict-tiny dictionary -m
>>> Youdao Dict <<<
dictionary  英['dɪkʃ(ə)n(ə)rɪ]美['dɪkʃə'nɛri]
=============================================
n. 字典；词典

more detail (collins):
======== N-COUNT 可数名词 ========
 · 词典

A dictionary is a book in which the words and phrases of a language are listed alphabetically, together with their meanings or their translations in another language.


 例: ...a Spanish-English dictionary.
     …一本西班牙语—英语词典。
```

**Note:**

* Some words have a lot of translation that may occupy the entire screen.
* Only supports English or Chinese words currently.

### Google Translate

Add `-g` / `--google` to use Google Translate:

```python
$ dict-tiny -g book
>>> Google Translate <<<
detected language: en
input: book
output: 书
```

Add `--target-language` to specify what language you want to translate into：

```python
$ dict-tiny -g book --target-language japanese
>>> Google Translate <<<
detected language: en
input: book
output: 本
```

Add `--source-language` to specify what language you want to translate, but most of the time you don't need to do this because the API will automatically detect the language type.

So, of course, you can use it to detect the language type:

```python
$ dict-tiny --detect-language book
>>> Google Translate <<<
confidence: 1
input: book
language: en
name: English
```

**Note:**

* Make sure the google service is available in your network environment.

* The source and target languages for Google Translate are identified using the [iso-639-1](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes) codes. 

  ```python
  $ dict-tiny -g book --target-language zh --source-language en
  >>> Google Translate <<<
  input: book
  output: 书
  source language: en
  ```

  You can also enter the ISO language name:

  ```python
  $ dict-tiny -g book --target-language German --source-language English
  >>> Google Translate <<<
  input: book
  output: Buchen
  source language: English
  ```

### Target language

* Setting the environment variable `$DICT_TINY_TARGET_LAN` to the `target language` you prefer so that you do not have to specify the `target language` every time. `Dict-tiny` will first get `target language` from `$DICT_TINY_TARGET_LAN`. Giving the `--target-language` switch on the command line will override the environment variable value.
* The default `target-language` for Goole Translate are `ENGLISH_ISO_639='en'`  if the content you input is not in English.

### ~~DeepL Translate~~

For some reason I am no longer allowed to use deepl pro, so deepl is no longer supported.

### Default behavior

* Youdao Dict is the default translator, which means Youdao Dict will be used when no translator is specified.
* If the target language is not specified, Chinese or English will be set as the default target language.

### Use clipboard content

Use `-c`/`--clipboard` to use the contents of the clipboard:

```python
$ dict-tiny -c -y
>>> Youdao Dict <<<
encounter  英[ɪnˈkaʊntə(r)]美[ɪnˈkaʊntər]
=========================================
v. 遭遇；偶遇，邂逅
n. 偶遇，邂逅；经历，体验；冲突；比赛，交锋
```

```python
$ dict-tiny -g -c
>>> Google Translate <<<
input: clipboard
output: 剪贴板
detected language: en
```

**Note:**

* `-c`/`--clipboard` has low priority. If you add `-c` and a word at the same time, the switch `-c` will be ignored.




## License

[MIT](https://github.com/louieh/dict-tiny/blob/master/LICENSE)

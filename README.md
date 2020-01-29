# Dict-tiny

[![PyPI version](https://img.shields.io/pypi/v/dict-tiny.svg)](https://pypi.python.org/pypi/dict-tiny/) ![GitHub Workflow Status](https://img.shields.io/github/workflow/status/louieh/dict-tiny/Upload Dict-tiny Python Package) ![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)



A command-line utility that can be used as:

* A dictionary of Chinese and English word translation by getting the data of youdao.com.
* A translator by using Google Translation API. You can also use it to detect the language type.

 Just for fun :)



## Installation

You can install `dict-tiny` via the pip package manager. (Python 3 only)

```shell
$ pip install dict-tiny
```



## Upgrading

```shell
$ pip install --upgrade dict-tiny
```



## Usage

### One word

```shell
$ dict-tiny book
book  英[bʊk]美[bʊk]
===================
n. 书籍；卷；账簿；名册；工作簿
vt. 预订；登记
n. (Book)人名；(中)卜(广东话·威妥玛)；(朝)北；(英)布
```

```shell
$ dict-tiny 书
书  [shū]
=========
n.book;letter;script
vt.write
```



### Getting more detail

Use `-m`/`--more` to get more detail translation:

```shell
$ dict-tiny 曾经 -m
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

```shell
$ dict-tiny dictionary -m
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

* You can use `-c` and `-m` at the same time, which means get more detail translation about the word in clipboard.
* Some words have a lot of translation that may occupy the entire screen.



### Using Google Translation API

Adding `-g` to use Google Translation API:

```shell
$ dict-tiny -g book
detectedSourceLanguage: en
input: book
translatedText: 书
```

Adding `--target-language` to specify what language you want to translate into：

```shell
$ dict-tiny -g book --target-language japanese
detectedSourceLanguage: en
input: book
translatedText: 本
```

Adding `--source-language` to specify what language you want to translate, but most of the time you don't need to do this because the api will automatically detect the language type.

So, of course, you can use it to detect the language type:

```shell
$ dict-tiny --detect-language book
confidence: 1
input: book
language: en
name: Armenian
```

**Note:**

* Setting the environment variable `$DICT_TINY_TARGET_LAN` to the `target language` you prefer so that you do not have to specify the `target language` every time. `Dict-tiny` will first get `target language` from `$DICT_TINY_TARGET_LAN`. Giving the `--target-language` switch on the command line will override the environment variable value.

* If your input is a sentence or more than one word, the Google Translation API will be called automatically. In other word, you don't need to manually add -g when you type a sentence.

* The source and target languages are identified using the [iso-639-1](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes) codes. 

  ```shell
  $ dict-tiny -g book --target-language zh --source-language en
  input: book
  translatedText: 书
  ```

  You can also enter the ISO language name:

  ```shell
  $ dict-tiny -g book --target-language chinese --source-language english
  input: book
  translatedText: 书
  ```

* The default `target-language` is `ENGLISH_ISO_639='en'` if you do not specify a `target-language` includes giving `--target-language` switch on the command line and setting `$DICT_TINY_TARGET_LAN` environment variable. _(If the input is alse English then the default `target-language` will be Chinese.)_

  

### Translate the word in clipboard

Using `-c`/`--clipboard` to translate the word in clipboard:

```shell
$ dict-tiny -c
命令行  
======
command line
```

If you want to use `-g` you need to put it before `-c`.

```python
$ dict-tiny -g -c
detectedSourceLanguage: en
input: clipboard
translatedText: 剪贴板
```

**Note:**

* `-c`/`--clipboard` has high priority. If you add `-c` and a word at the same time, the word will be ignored.

  

## License

[MIT](https://github.com/louieh/dict-tiny/blob/master/LICENSE)
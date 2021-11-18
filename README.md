# Dict-tiny

[![PyPI version](https://img.shields.io/pypi/v/dict-tiny.svg)](https://pypi.python.org/pypi/dict-tiny/) [![GitHub Workflow Status](https://img.shields.io/github/workflow/status/louieh/dict-tiny/Upload%20Dict-tiny%20Python%20Package)](https://github.com/louieh/dict-tiny/actions?query=workflow%3A%22Upload+Dict-tiny+Python+Package%22) [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT) [![Downloads](https://pepy.tech/badge/dict-tiny)](https://pepy.tech/project/dict-tiny)


A command line translator that integrates with Google Translate, DeepL Translator and youdao.com

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

### DeepL Translator

Adding `-d` / `--deepl` to use DeepL Translator API:

```shell
$ dict-tiny -d easy come easy go
>>> DeepL Translator
detected language: EN
input: easy come easy go
output: 来得容易去得快
```

Specify the target translation language as French via the `--target-language`:

```shell
$ dict-tiny -d easy come easy go  --target-language FR
>>> DeepL Translator
detected language: EN
input: easy come easy go
output: ça va, ça vient
```

**Note:**

* The target-language parameter is required for deepl translator API. The default target-language is ZH.
* You can view the list of target languages [here](https://www.deepl.com/docs-api/translating-text/request/).





### Google Translation

Adding `-g` / `--google` to use Google Translation API:

```shell
$ dict-tiny -g book
>>> Google Translate
detected language: en
input: book
output: 书
```

Adding `--target-language` to specify what language you want to translate into：

```shell
$ dict-tiny -g book --target-language japanese
>>> Google Translate
detected language: en
input: book
output: 本
```

Adding `--source-language` to specify what language you want to translate, but most of the time you don't need to do this because the API will automatically detect the language type.

So, of course, you can use it to detect the language type:

```shell
$ dict-tiny --detect-language book
>>> Google detect language
confidence: 1
input: book
language: en
name: English
```

**Note:**

* The source and target languages for Google Translate are identified using the [iso-639-1](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes) codes. 

  ```shell
  $ dict-tiny -g book --target-language zh --source-language en
  >>> Google Translate
  input: book
  output: 书
  source language: en
  ```

  You can also enter the ISO language name:

  ```shell
  $ dict-tiny -g book --target-language German --source-language English
  >>> Google Translate
  input: book
  output: Buchen
  source language: English
  ```





### Target language

* Setting the environment variable `$DICT_TINY_TARGET_LAN` to the `target language` you prefer so that you do not have to specify the `target language` every time. `Dict-tiny` will first get `target language` from `$DICT_TINY_TARGET_LAN`. Giving the `--target-language` switch on the command line will override the environment variable value.
* The default `target-language` for Goole Translate and DeepL are `ENGLISH_ISO_639='en'` and `EN-US` if you do not specify a `target-language` includes giving `--target-language` switch on the command line and setting `$DICT_TINY_TARGET_LAN` environment variable.






### Default behavior

* If your input is a sentence or more than one word, the DeepL Translator will be called automatically.

* If your input is a word and you don't add any switch, then the default behavior is to use youdao.com to translate between English and Chinese. In other words, you have to input a Chinese words or an English words, forgive me, because I am an English learner :smile_cat: 

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

Use `-m`/`--more` to get more detail translation for word:

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

* Some words have a lot of translation that may occupy the entire screen.





### Translate the word in clipboard

Using `-c`/`--clipboard` to translate the word in clipboard:

```shell
$ dict-tiny -c
命令行  
======
command line
```

You can use both `-g` and `-c`.

```python
$ dict-tiny -g -c
>>> Google Translate
input: clipboard
output: 剪贴板
detected language: en
```

**Note:**

* Adding `-c` and `-m` at the same time, which means get more detail translation about the word in clipboard.

* `-c`/`--clipboard` has low priority. If you add `-c` and a word at the same time, the switch `-c` will be ignored.




## License

[MIT](https://github.com/louieh/dict-tiny/blob/master/LICENSE)
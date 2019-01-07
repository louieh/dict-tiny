# Dict-tiny

[![PyPI version](https://img.shields.io/pypi/v/dict-tiny.svg)](https://pypi.python.org/pypi/dict-tiny/)

Dict-tiny is a command-line utility that can translate English and Chinese words, which makes it easy to translate words from command-line interface. Just for fun :)

You can use `dict-tiny` in this way:



### Translate an English word or Chinese word

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


### Translate the word in clipboard

Use `-c`/`--clipboard` to translate the word in clipboard:

```shell
$ dict-tiny -c
命令行  
======
command line
```
**Note:**

* `-c`/`--clipboard` has high priority. If you add `-c` and a word at the same time, the word will be considered invalid.



### Get more detail translation about the word

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



## Installation

You can install `dict-tiny` via the pip package manager.

```shell
$ pip3 install dict-tiny
```



## Upgrading

```shell
$ pip3 install --upgrade dict-tiny
```


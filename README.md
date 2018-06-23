# Dict-tiny

Dict-tiny is a tiny command-line utility to look up English words or Chinese words from youdao.com. Just for fun :)

You can use `dict-tiny` in this way:



#### Translate an English word or Chinese word

```shell
$ dict-tiny book
n. 书籍；卷；账簿；名册；工作簿
vt. 预订；登记
n. (Book)人名；(中)卜(广东话·威妥玛)；(朝)北；(英)布克；(瑞典)博克
```

```shell
$ dict-tiny 书
n.book;letter;script
vt.write
```


#### Translate the word in clipboard

Use `-c`/`--clipboard` to translate the word in clipboard:

```shell
$ dict-tiny -c
命令行
====
command line
```
**Note:**

* `-c`/`--clipboard` has high priority. If you add `-c` and a word at the same time, the word will be considered invalid.



#### Get more detail translation about the word

Use `-m`/`--more` to get more detail translation:

```shell
$ dict-tiny 曾经 -m
曾经
===
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
$ dict-tiny html -m
html
=====
abbr. 超文本标记语言（Hypertext Markup Language）

more detail:
======== abbr. ========
1:
        hypertext markup language 【计算机】超文本标记语言

```

**Note:**

* You can use `-c` and `-m` at the same time, which means get more detail translation about the word in clipboard.
* Some words have a lot of translation that may occupy the entire screen.



### Installation

You can install `dict-tiny` via the pip package manager.

```shell
$ pip3 install dict-tiny
```

### Upgrading

```shell
$ pip3 install --upgrade dict-tiny
```


# Dict-tiny

[![PyPI version](https://img.shields.io/pypi/v/dict-tiny.svg)](https://pypi.python.org/pypi/dict-tiny/) [![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/louieh/dict-tiny/upload-dict-tiny-package.yml)](https://github.com/louieh/dict-tiny/actions?query=workflow%3A%22Upload+Dict-tiny+Python+Package%22) [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT) [![Downloads](https://pepy.tech/badge/dict-tiny)](https://pepy.tech/project/dict-tiny)

A command-line tool that integrates Youdao Dict, Google Translate, ~~DeepL Translator~~, Gemini and OpenAI.

Just for fun :)



## Installation

You can install `dict-tiny` via pip. (>=Python 3.9)

```python
$ pip install dict-tiny
```



## Upgrading

```python
$ pip install --upgrade dict-tiny
```



## Usage

### Youdao Dict

Add `-y` / `--youdao` to use Youdao Dict:

```python
$ dict-tiny -y book
>>> YoudaoDict <<<
book
======
英[bʊk]美[bʊk]
n. 书，书籍；本子，簿册；（长篇作品的）篇，卷，部；装订成册之物；赌局，打赌；账册，账簿
v. 预订，预约；（警方）将……记录在案；（裁判）记名警告
【名】 （Book）（英）布克，（瑞典）博克，（朝）北（人名）
```

```python
$ dict-tiny -y 书
>>> YoudaoDict <<<
书
===
[shū]
n.book;letter;script
vt.write
```

Use `-m`/`--more` to get more detail translation for the word:

```python
$ dict-tiny -y 曾经 -m
>>> YoudaoDict <<<
曾经
====
[céng jīng]
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
$ dict-tiny -y dictionary -m
>>> YoudaoDict <<<
dictionary
============
英[ˈdɪkʃən(ə)ri]美[ˈdɪkʃəneri]
n. 字典，词典；专业词典，术语大全；电子词典；双语词典

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
>>> GoogleTranslate <<<
book
======
output: 书
detected language: en
```

Add `--target-language` to specify the language to translate results into：

```python
$ dict-tiny -g operation system --target-language ja
>>> GoogleTranslate <<<
operation system
==================
output: オペレーションシステム
detected language: en
```

Add `--source-language` to specify the language of the text to be translated, but in most cases you don't need to do this because the google translate api automatically detects the source language type. 

And if you give a wrong source language, the translation result may not be what you expect.

So, of course, you can add `--detect-language` to detect the language type:

```python
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

* Make sure Google services are available in your network environment.

* The source and target languages for Google Translate are identified using the [iso-639-1](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes) codes. 

  ```python
  $ dict-tiny -g book --target-language zh --source-language en
  >>> GoogleTranslate <<<
  book
  ======
  output: 书
  source language: en
  ```
  
  You can also enter the ISO language name:
  
  ```python
  $ dict-tiny -g book --target-language German --source-language English
  >>> GoogleTranslate <<<
  book
  ======
  output: Buch
  source language: English
  ```

* Set the environment variable `$DICT_TINY_TARGET_LAN` so that you do not have to manually specify the target language each time. if you specify the target language parameter on the command line with `--target-language`, the setting in the environment variable will be overwritten.
* The default `target-language` for Goole Translate are `English` .

### ~~DeepL Translate~~

For some reason I am no longer allowed to use deepl pro, so deepl is no longer supported.

### Gemini

Add `--gemini` to use Gemini.

Use `--gemini-model` to specify the model used by Gemini. You can also set the environment variable `$DICT_TINY_GEMINI_MODEL`. The default model is `gemini-pro`.

Use `--gemini-key` to specify the Gemini api key, or set the environment variable `$DICT_TINY_GEMINI_API_KEY`.

**Note:**

* If you use `gemini-pro-vision` model, you need to use `--img-path` to specify the path of image.

* Use `--max-output-tokens` to specify the maximum output token.

* Use `--temperature` to specify the temperature.

### OpenAI

Add `--openai` to use OpenAI.

Use `--openai-model` to specify the model used by OpenAI. You can also set the environment variable `$DICT_TINY_OPENAI_MODEL`. The default model is `gpt-3.5-turbo`.

Use `--openai-key` to specify the OpenAI api key, or set the environment variable `$DICT_TINY_OPENAI_API_KEY`.

```python
$ dict-tiny --openai who are you?
>>> OpenAI-gpt-3.5-turbo <<<
I am an AI language model created by OpenAI. I can assist you with various tasks, answer questions, and
engage in conversations on a wide range of topics. How may I assist you today?
```

**Note:**

* Currently only text generation models are supported.

* Use `--max-output-tokens` to specify the maximum output token.

* Use `--temperature` to specify the temperature.

### Interactive mode

Each of the above functions can be entered into its interactive mode by adding the `-i` . `Control + d` to exit interactive mode.

<img src="./assets/interactive_mode.png" alt="interactive_mode" width="70%" height="70%" />

In interactive mode you can:

* Use above features in a continuous interactive manner.
* Press `Tab` key for word auto-completion (using Youdao's auto-completion function, currently only supports Chinese, English, French, Korean, Japanese)
* For Gemini and OpenAI, the dialog context is maintained in interactive mode, use `--dialog-turns` to specify the number of dialog turns to maintain, the default is 10.
* All settings cannot be changed after entering interactive mode, such as target-language, model, img-path, temperature, etc., unless you exit to change the settings and re-enter.

### Other

#### Default behavior

* Youdao Dict is the default translator, which means Youdao Dict will be used when no translator is specified.

  ```python
  $ dict-tiny 机器学习
  >>> YoudaoDict <<<
  机器学习
  ======
  machine learning
  ```
  
  You can use the environment variable `$DICT_TINY_DEFAULT_TRANS` to set the default translator. There are four options described above: `YoudaoDict`, `GoogleTranslate`, `Gemini`, `OpenAI`.  Case insensitive.
* For Youdao Dict and Google translate, if the target language is not specified, Chinese and English will be used as the target language for each other.
* In non-interactive mode, multiple translators can be specified at the same time, for example, YoudaoDict and GoogleTranslate can be used at the same time.

  ```python
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

```python
$ dict-tiny -c -y
>>> YoudaoDict <<<
encounter
===========
英[ɪnˈkaʊntə(r)]美[ɪnˈkaʊntər]
v. 遭遇；偶遇，邂逅
n. 偶遇，邂逅；经历，体验；冲突；比赛，交锋
```

**Note:**

* `-c`/`--clipboard` has low priority. If you add `-c` and a word at the same time, the switch `-c` will be ignored.




## License

[MIT](https://github.com/louieh/dict-tiny/blob/master/LICENSE)

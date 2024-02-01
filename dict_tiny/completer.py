from prompt_toolkit.completion import Completer, Completion

from dict_tiny.config import YOUDAO_SUGGESTION_API_BASE_URL, SUGGESTION_NUM, YOUDAO_SUGGEST_API_FAKE_HEADER
from dict_tiny.util import downloader


class YoudaoCompleter(Completer):
    def __init__(self, le):
        self.le = le

    def get_completions(self, document, complete_event):
        word_before_cursor = document.get_word_before_cursor()
        suggest_url = YOUDAO_SUGGESTION_API_BASE_URL.format(SUGGESTION_NUM, self.le, word_before_cursor)
        resp = downloader.download("GET", suggest_url, headers=YOUDAO_SUGGEST_API_FAKE_HEADER)
        if not resp: return []
        try:
            resp_json = resp.json()
            if resp_json["result"]["code"] != 200:
                return []
            for each in resp_json["data"]["entries"]:
                entry, explain = each["entry"], each["explain"]
                yield Completion(entry, start_position=-len(word_before_cursor))
        except Exception as e:
            return []

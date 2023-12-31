from prompt_toolkit.completion import WordCompleter, Completer, Completion

from dict_tiny.config import YOUDAO_SUGGESTION_API_BASE_URL, SUGGESTION_NUM, YOUDAO_SUGGEST_API_FAKE_HEADER
from dict_tiny.util import downloader

sql_completer = WordCompleter([
    'abort', 'action', 'add', 'after', 'all', 'alter', 'analyze', 'and',
    'as', 'asc', 'attach', 'autoincrement', 'before', 'begin', 'between',
    'by', 'cascade', 'case', 'cast', 'check', 'collate', 'column',
    'commit', 'conflict', 'constraint', 'create', 'cross', 'current_date',
    'current_time', 'current_timestamp', 'database', 'default',
    'deferrable', 'deferred', 'delete', 'desc', 'detach', 'distinct',
    'drop', 'each', 'else', 'end', 'escape', 'except', 'exclusive',
    'exists', 'explain', 'fail', 'for', 'foreign', 'from', 'full', 'glob',
    'group', 'having', 'if', 'ignore', 'immediate', 'in', 'index',
    'indexed', 'initially', 'inner', 'insert', 'instead', 'intersect',
    'into', 'is', 'isnull', 'join', 'key', 'left', 'like', 'limit',
    'match', 'natural', 'no', 'not', 'notnull', 'null', 'of', 'offset',
    'on', 'or', 'order', 'outer', 'plan', 'pragma', 'primary', 'query',
    'raise', 'recursive', 'references', 'regexp', 'reindex', 'release',
    'rename', 'replace', 'restrict', 'right', 'rollback', 'row',
    'savepoint', 'select', 'set', 'table', 'temp', 'temporary', 'then',
    'to', 'transaction', 'trigger', 'union', 'unique', 'update', 'using',
    'vacuum', 'values', 'view', 'virtual', 'when', 'where', 'with',
    'without'], ignore_case=True)


class YoudaoCompleter(Completer):
    def __init__(self, le):
        self.le = le

    def get_completions(self, document, complete_event):
        word_before_cursor = document.get_word_before_cursor()
        suggest_url = YOUDAO_SUGGESTION_API_BASE_URL.format(SUGGESTION_NUM, self.le, word_before_cursor)
        resp = downloader("GET", suggest_url, headers=YOUDAO_SUGGEST_API_FAKE_HEADER)
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

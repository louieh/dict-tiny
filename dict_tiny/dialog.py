import threading
from collections import deque
from itertools import chain
from typing import List

from dict_tiny.config import SUMMARY_PROMPT
from dict_tiny.errors import InitDialogError


class Dialog(object):
    def __init__(self, dialog_turns, llm_obj):
        if dialog_turns <= 0:
            raise InitDialogError(f"dialog_turns must be positive")
        self.capacity = dialog_turns
        self.dialog = deque(maxlen=dialog_turns)
        self.llm_obj = llm_obj

    def trim_worker(self):
        try:
            token_usage = self.llm_obj.get_token_usage()
            token_usage_window = self.llm_obj.get_token_usage_window()
        except Exception as e:
            return
        # print(f"token usage: {token_usage}, token usage window: {token_usage_window}")
        if token_usage < token_usage_window:
            return
        curr_question = self.llm_obj.generate_user_message(SUMMARY_PROMPT)
        prev_dialogs = self.get_flat()
        prev_dialogs.append(curr_question)
        response = self.llm_obj.chat_completion(prev_dialogs, stream=False)
        response_text = self.llm_obj.parse_response(response)
        # thread safe ?
        self.dialog.clear()
        self.dialog.append([
            curr_question,
            self.llm_obj.generate_model_message(response_text)
        ])

    def get_flat(self):
        return list(chain(*self.dialog))

    def add(self, messages: List):
        # default each dialog: [{'role': 'user', 'content'}, {'role': 'model', 'content'}]
        # need keep different roles appearing alternately
        self.dialog.append(messages)
        trim_thread = threading.Thread(target=self.trim_worker)
        trim_thread.start()

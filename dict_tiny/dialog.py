from collections import deque
from itertools import chain

from dict_tiny.errors import InitDialogError


class Dialog(object):
    def __init__(self, dialog_turns):
        if dialog_turns <= 0:
            raise InitDialogError(f"dialog_turns must be positive")
        self.capacity = dialog_turns
        self.dialog = deque(maxlen=dialog_turns)

    def _trim(self):
        pass

    def get_flat(self):
        return list(chain(*self.dialog))

    def add(self, message):
        # default each dialog: [{'role': 'user', 'content'}, {'role': 'model', 'content'}]
        if self.dialog and len(self.dialog[-1]) == 1:
            self.dialog[-1].append(message)
            return
        self.dialog.append([message])

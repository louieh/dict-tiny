from typing import Callable

from plumbum import cli
from rich.console import Console

from dict_tiny.dialog import Dialog
from dict_tiny.errors import LLMParamError
from dict_tiny.translators.translator import DefaultTrans


class DefaultLLM(DefaultTrans):
    def __init__(self, text, dict_tiny_obj):
        super().__init__(text, dict_tiny_obj)
        self.max_output_tokens = self.validate_param("max_output_tokens",
                                                     lambda x: x is None or x > 0,
                                                     error_msg="max_output_tokens must be positive")
        self.console = Console()
        self.dialogs = Dialog(dict_tiny_obj.dialog_turns, self)

    @classmethod
    def attr_setter(cls, dict_tiny_cls):
        super().attr_setter(dict_tiny_cls)
        dict_tiny_cls.max_output_tokens = cli.SwitchAttr("--max-output-tokens",
                                                         int,
                                                         group="LLM",
                                                         help="The maximum number of tokens to include in a candidate.")
        dict_tiny_cls.temperature = cli.SwitchAttr("--temperature",
                                                   float,
                                                   group="LLM",
                                                   help="Controls the randomness of the output")
        dict_tiny_cls.dialog_turns = cli.SwitchAttr(["--dialog-turns"],
                                                    cli.Range(1, 20),
                                                    group="LLM",
                                                    default=10,
                                                    help="Number of conversations turns")

    def get_token_usage(self) -> int:
        raise NotImplementedError

    def get_token_usage_window(self) -> int:
        raise NotImplementedError

    def generate_user_message(self, text: str) -> dict:
        raise NotImplementedError

    def generate_model_message(self, text: str) -> dict:
        raise NotImplementedError

    def chat_completion(self, messages: list, stream=False):
        raise NotImplementedError

    def parse_response(self, response) -> str:
        raise NotImplementedError

    def validate_param(self, param_name: str, valid_func: Callable = None, error_msg: str = None):
        param_value = getattr(self.dict_tiny_obj, param_name, None)
        if valid_func and not valid_func(param_value):
            raise LLMParamError(f"param {param_name} error: {error_msg}")
        return param_value

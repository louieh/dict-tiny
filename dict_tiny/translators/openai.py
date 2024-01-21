import openai
from plumbum import cli
from rich.console import Console
from rich.markdown import Markdown
from openai import OpenAI as openai_cls

from dict_tiny.config import OPENAI_NAME, DEFAULT_OPENAI_MODEL, OPENAI_API_KEY_ENV_NAME, SEPARATOR, OPENAI_MODEL
from dict_tiny.errors import LLMAPIKeyNotFoundError
from dict_tiny.translators.translator import DefaultTrans
from dict_tiny.util import normal_warn_printer


class OpenAI(DefaultTrans):
    def __init__(self, text, dict_tiny_obj):
        super().__init__(text, dict_tiny_obj)
        self.model = dict_tiny_obj.openai_model
        self.name = f"{OPENAI_NAME}-{self.model}"
        self.api_key = dict_tiny_obj.openai_api_key
        if not self.api_key:
            raise LLMAPIKeyNotFoundError("OpenAI api key not found")
        if self.model not in OPENAI_MODEL:
            normal_warn_printer(f"The model you entered may be wrong: {self.model}")
        self.console = Console()
        self.client = openai_cls(api_key=self.api_key)
        self.keep_context = dict_tiny_obj.keep_context
        self.conversation = []

    @classmethod
    def attr_setter(cls, dict_tiny_cls):
        super().attr_setter(dict_tiny_cls)
        dict_tiny_cls.use_openai = cli.Flag(["--openai"],
                                            group="OpenAI",
                                            help="Use OpenAI API")
        dict_tiny_cls.keep_context = cli.Flag(["--keep-context"],
                                              group="OpenAI",
                                              default=True,
                                              help="multi-turn conversations")
        dict_tiny_cls.openai_model = cli.SwitchAttr("--openai-model",
                                                    str,
                                                    group="OpenAI",
                                                    default=DEFAULT_OPENAI_MODEL,
                                                    help="Select openai model")
        dict_tiny_cls.openai_api_key = cli.SwitchAttr("--openai-key",
                                                      str,
                                                      group="OpenAI",
                                                      envname=OPENAI_API_KEY_ENV_NAME,
                                                      help="Indicate openai api key")
        # dict_tiny_cls.max_output_tokens = cli.SwitchAttr("--max-output-tokens",
        #                                                  int,
        #                                                  group="Gemini",
        #                                                  help="The maximum number of tokens to include in a candidate.")
        # dict_tiny_cls.temperature = cli.SwitchAttr("--temperature",
        #                                            float,
        #                                            group="Gemini",
        #                                            help="Controls the randomness of the output")
        # dict_tiny_cls.top_p = cli.SwitchAttr("--top-p",
        #                                      float,
        #                                      group="Gemini",
        #                                      help="The maximum cumulative probability of tokens to consider when sampling.")
        # dict_tiny_cls.top_k = cli.SwitchAttr("--top-k",
        #                                      int,
        #                                      group="Gemini",
        #                                      help="The maximum number of tokens to consider when sampling.")

    def pre_action(self, text):
        pass

    def print_input(self, text):
        pass

    def do_translate(self, text):
        self.conversation.append({"role": "user", "content": text})
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=self.conversation,
            )
        except openai.APIConnectionError as e:
            normal_warn_printer("The server could not be reached")
            return
        except openai.RateLimitError as e:
            normal_warn_printer("A 429 status code was received; we should back off a bit.")
            return
        except openai.APIStatusError as e:
            normal_warn_printer("Another non-200-range status code was received")
            return
        resp_text = resp.choices[0].message.content
        self.console.print(Markdown(resp_text))
        self.conversation.append({"role": "assistant", "content": resp_text})
        if not self.keep_context:
            self.conversation = []

    def interactive_loop(self, session):
        super().interactive_loop(session)

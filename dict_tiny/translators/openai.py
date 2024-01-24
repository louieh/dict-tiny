import openai
from openai import OpenAI as openai_cls
from plumbum import cli
from rich.markdown import Markdown

from dict_tiny.config import OPENAI_NAME, DEFAULT_OPENAI_MODEL, OPENAI_API_KEY_ENV_NAME, OPENAI_MODEL_DETAIL
from dict_tiny.translators.llm import DefaultLLM
from dict_tiny.util import normal_warn_printer


class OpenAI(DefaultLLM):
    def __init__(self, text, dict_tiny_obj):
        super().__init__(text, dict_tiny_obj)

        # param valid check
        self.model = self.validate_param("openai_model",
                                         lambda x: x is not None and x in OPENAI_MODEL_DETAIL,
                                         error_msg="model not found")
        self.api_key = self.validate_param("openai_api_key",
                                           lambda x: x is not None,
                                           error_msg="api key not found")
        self.temperature = self.validate_param("temperature",
                                               lambda x: x is None or (0 <= x <= 2),
                                               error_msg="temperature can range from [0.0,2.0], inclusive")
        self.api_params = {
            "max_tokens": self.max_output_tokens,
            "temperature": self.temperature
        }

        self.client = openai_cls(api_key=self.api_key)
        self.name = f"{OPENAI_NAME}-{self.model}"

    @classmethod
    def attr_setter(cls, dict_tiny_cls):
        super().attr_setter(dict_tiny_cls)
        dict_tiny_cls.use_openai = cli.Flag(["--openai"],
                                            group="OpenAI",
                                            help="Use OpenAI API")
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
        self.conversation = self.conversation[-self.dialogue_turns:]

    def interactive_loop(self, session):
        super().interactive_loop(session)

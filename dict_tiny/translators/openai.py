import openai
from openai import OpenAI as openai_cls
from plumbum import cli
from rich.markdown import Markdown

from dict_tiny.config import OPENAI_NAME, DEFAULT_OPENAI_MODEL, OPENAI_API_KEY_ENV_NAME, OPENAI_MODEL_DETAIL, \
    OPENAI_MODEL_ENV_NAME, OPENAI_TIMEOUT, TOKEN_USAGE_FACTOR
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

        self.azure_endpoint = dict_tiny_obj.azure_endpoint
        self.base_url = dict_tiny_obj.azure_base_url
        self.api_version = dict_tiny_obj.api_version
        self.api_params = {
            "max_tokens": self.max_output_tokens,
            "temperature": self.temperature
        }
        self.name = f"{OPENAI_NAME}-{self.model}"
        self.token_usage = 0

        if self.azure_endpoint or self.base_url:
            from openai import AzureOpenAI
            azure_client_params = {
                "timeout": OPENAI_TIMEOUT,
                "api_version": self.api_version,
                "api_key": self.api_key
            }
            if self.azure_endpoint:
                azure_client_params.update({"azure_endpoint": self.azure_endpoint})
            elif self.base_url:
                azure_client_params.update({"base_url": self.base_url})
            self.client = AzureOpenAI(**azure_client_params)
        else:
            self.client = openai_cls(
                api_key=self.api_key,
                timeout=OPENAI_TIMEOUT
            )

    @classmethod
    def attr_setter(cls, dict_tiny_cls):
        super().attr_setter(dict_tiny_cls)
        dict_tiny_cls.use_openai = cli.Flag(["--openai"],
                                            group=OPENAI_NAME,
                                            help="Use OpenAI API")
        dict_tiny_cls.openai_model = cli.SwitchAttr("--openai-model",
                                                    str,
                                                    group=OPENAI_NAME,
                                                    envname=OPENAI_MODEL_ENV_NAME,
                                                    default=DEFAULT_OPENAI_MODEL,
                                                    help="Select openai model")
        dict_tiny_cls.openai_api_key = cli.SwitchAttr("--openai-key",
                                                      str,
                                                      group=OPENAI_NAME,
                                                      envname=OPENAI_API_KEY_ENV_NAME,
                                                      help="Indicate openai api key")
        dict_tiny_cls.azure_endpoint = cli.SwitchAttr("--azure-endpoint",
                                                      str,
                                                      group=OPENAI_NAME,
                                                      help="azure endpoint")
        dict_tiny_cls.azure_base_url = cli.SwitchAttr("--azure-base-url",
                                                      str,
                                                      group=OPENAI_NAME,
                                                      help="azure openai base url")
        dict_tiny_cls.api_version = cli.SwitchAttr("--api-version",
                                                   str,
                                                   group=OPENAI_NAME,
                                                   help="azure openai api version")

    def pre_action(self, text):
        pass

    def print_input(self, text):
        pass

    def get_token_usage(self) -> int:
        return self.token_usage

    def get_token_usage_window(self) -> int:
        return OPENAI_MODEL_DETAIL[self.model]["context_window"] * TOKEN_USAGE_FACTOR

    def generate_user_message(self, text):
        return {
            "role": "user",
            "content": [text]
        }

    def generate_model_message(self, text):
        return {
            "role": "assistant",
            "content": [text]
        }

    def chat_completion(self, messages: list, stream=False):
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=stream,
                **self.api_params
            )
            return response
        except openai.APIConnectionError as e:
            normal_warn_printer(f"The server could not be reached: {e.__cause__}")
        except openai.RateLimitError as e:
            normal_warn_printer("A 429 status code was received; we should back off a bit.")
        except openai.APIStatusError as e:
            normal_warn_printer(
                f"Another non-200-range status code was received, code: {e.status_code}, response: {e.message}")

    def parse_response(self, response):
        return response.choices[0].message.content

    def do_translate(self, text):
        curr_question = {
            "role": "user",
            "content": text
        }
        prev_dialogs = self.dialogs.get_flat()
        prev_dialogs.append(curr_question)

        response = self.chat_completion(prev_dialogs)
        if not response: return

        response_text = self.parse_response(response)
        self.token_usage = response.usage.total_tokens
        self.console.print(Markdown(response_text))
        self.dialogs.add([curr_question,
                          {
                              "role": "assistant",
                              "content": response_text
                          }])

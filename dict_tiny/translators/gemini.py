import google.generativeai as genai
from plumbum import cli
from rich.console import Console
from rich.markdown import Markdown

from dict_tiny.config import GEMINI_NAME, DEFAULT_GEMINI_MODEL, GEMINI_API_KEY_ENV_NAME
from dict_tiny.translators.translator import DefaultTrans
from dict_tiny.util import normal_warn_printer


class Gemini(DefaultTrans):
    def __init__(self, text, dict_tiny_obj):
        super().__init__(text, dict_tiny_obj)
        self.chat = None
        self.name = GEMINI_NAME
        self.model = dict_tiny_obj.llm_model
        self.api_key = dict_tiny_obj.llm_api_key
        if not self.api_key:
            # TODO
            raise "API key not found"
        self.console = Console()

    @classmethod
    def attr_setter(cls, dict_tiny_cls):
        super().attr_setter(dict_tiny_cls)
        dict_tiny_cls.use_gemini = cli.Flag(["--gemini"],
                                            group="Gemini",
                                            help="Use Gemini API")
        dict_tiny_cls.llm_model = cli.SwitchAttr("--model", str,
                                                 group="Gemini",
                                                 default=DEFAULT_GEMINI_MODEL,
                                                 help="Select gemini model")
        dict_tiny_cls.llm_api_key = cli.SwitchAttr("--key", str,
                                                   group="Gemini",
                                                   envname=GEMINI_API_KEY_ENV_NAME,
                                                   help="Indicate gemini api key")

    def pre_action(self, text):
        genai.configure(api_key=self.api_key)
        self.chat = genai.GenerativeModel(self.model)

    def print_input(self, text):
        pass

    def do_translate(self, text):
        if not self.chat:
            normal_warn_printer("chat not found")
            return
        response = self.chat.generate_content(text)
        self.console.print(Markdown(response.text))

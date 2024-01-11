import google.generativeai as genai
from PIL import Image
from plumbum import cli
from rich.console import Console
from rich.markdown import Markdown

from dict_tiny.config import GEMINI_NAME, DEFAULT_GEMINI_MODEL, GEMINI_API_KEY_ENV_NAME, GEMINI_MODEL
from dict_tiny.errors import LLMAPIKeyNotFoundError
from dict_tiny.translators.translator import DefaultTrans
from dict_tiny.util import normal_warn_printer, normal_info_printer


class Gemini(DefaultTrans):
    def __init__(self, text, dict_tiny_obj):
        super().__init__(text, dict_tiny_obj)
        self.name = GEMINI_NAME
        self.model = dict_tiny_obj.llm_model
        self.api_key = dict_tiny_obj.gemini_api_key
        if not self.api_key:
            raise LLMAPIKeyNotFoundError("Gemini api key not found")
        genai.configure(api_key=self.api_key)
        model = genai.GenerativeModel(self.model)
        self.chat = model.start_chat(history=[]) if self.model == GEMINI_MODEL.gemini_pro.value else model
        self.generation_config = genai.types.GenerationConfig(
            max_output_tokens=dict_tiny_obj.max_output_tokens,
            temperature=dict_tiny_obj.temperature,
            top_p=dict_tiny_obj.top_p,
            top_k=dict_tiny_obj.top_k
        )
        self.console = Console()

    @classmethod
    def attr_setter(cls, dict_tiny_cls):
        super().attr_setter(dict_tiny_cls)
        dict_tiny_cls.use_gemini = cli.Flag(["--gemini"],
                                            group="Gemini",
                                            help="Use Gemini API")
        dict_tiny_cls.llm_model = cli.SwitchAttr("--model",
                                                 str,
                                                 group="Gemini",
                                                 default=DEFAULT_GEMINI_MODEL,
                                                 help="Select gemini model")
        dict_tiny_cls.img_path = cli.SwitchAttr("--img_path",
                                                str,
                                                group="Gemini",
                                                help="Indicate local image path if the model is gemini pro vision")
        dict_tiny_cls.gemini_api_key = cli.SwitchAttr("--gemini-key",
                                                   str,
                                                   group="Gemini",
                                                   envname=GEMINI_API_KEY_ENV_NAME,
                                                   help="Indicate gemini api key")
        dict_tiny_cls.max_output_tokens = cli.SwitchAttr("--max-output-tokens",
                                                         int,
                                                         group="Gemini",
                                                         help="The maximum number of tokens to include in a candidate.")
        dict_tiny_cls.temperature = cli.SwitchAttr("--temperature",
                                                   float,
                                                   group="Gemini",
                                                   help="Controls the randomness of the output")
        dict_tiny_cls.top_p = cli.SwitchAttr("--top-p",
                                             float,
                                             group="Gemini",
                                             help="The maximum cumulative probability of tokens to consider when sampling.")
        dict_tiny_cls.top_k = cli.SwitchAttr("--top-k",
                                             int,
                                             group="Gemini",
                                             help="The maximum number of tokens to consider when sampling.")

    def print_input(self, text):
        pass

    def do_translate(self, text):
        if self.model == GEMINI_MODEL.gemini_pro_vision.value:
            img_path, *text = text.split(" ")
            text = " ".join(text)
            try:
                img = Image.open(img_path)
            except Exception as e:
                normal_warn_printer(f"Unable to identify the image at: {img_path}")
                return
            response = self.chat.generate_content(
                [text, img],
                generation_config=self.generation_config,
                stream=True)
        else:
            response = self.chat.send_message(
                text,
                generation_config=self.generation_config,
                stream=True)

        for chunk in response:
            self.console.print(Markdown(chunk.text))

    def interactive_loop(self, session):
        if self.model == GEMINI_MODEL.gemini_pro_vision.value:
            normal_info_printer(
                "If you use gemini pro vision, please enter the image address first, and then enter the text separated by spaces.")
        super().interactive_loop(session)

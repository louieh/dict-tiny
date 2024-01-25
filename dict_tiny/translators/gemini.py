import google.generativeai as genai
from PIL import Image
from plumbum import cli
from rich.markdown import Markdown

from dict_tiny.config import GEMINI_NAME, DEFAULT_GEMINI_MODEL, GEMINI_API_KEY_ENV_NAME, GEMINI_MODEL, \
    GEMINI_MODEL_DETAIL
from dict_tiny.translators.llm import DefaultLLM
from dict_tiny.util import normal_warn_printer, normal_info_printer


class Gemini(DefaultLLM):
    def __init__(self, text, dict_tiny_obj):
        super().__init__(text, dict_tiny_obj)

        #  param valid check
        self.model = self.validate_param("gemini_model",
                                         lambda x: x is not None and x in GEMINI_MODEL_DETAIL,
                                         error_msg="model not found")
        self.api_key = self.validate_param("gemini_api_key",
                                           lambda x: x is not None,
                                           error_msg="api key not found")
        self.temperature = self.validate_param("temperature",
                                               lambda x: x is None or (0 <= x <= 1),
                                               error_msg="temperature can range from [0.0,1.0], inclusive")

        self.generation_config = genai.types.GenerationConfig(
            max_output_tokens=self.max_output_tokens,
            temperature=self.temperature,

        )
        genai.configure(api_key=self.api_key)
        self.chat = genai.GenerativeModel(self.model)
        self.name = f"{GEMINI_NAME}-{self.model}"

    @classmethod
    def attr_setter(cls, dict_tiny_cls):
        super().attr_setter(dict_tiny_cls)
        dict_tiny_cls.use_gemini = cli.Flag(["--gemini"],
                                            group="Gemini",
                                            help="Use Gemini API")
        dict_tiny_cls.gemini_model = cli.SwitchAttr("--gemini-model",
                                                    str,
                                                    group="Gemini",
                                                    default=DEFAULT_GEMINI_MODEL,
                                                    help="Select gemini model")
        dict_tiny_cls.gemini_api_key = cli.SwitchAttr("--gemini-key",
                                                      str,
                                                      group="Gemini",
                                                      envname=GEMINI_API_KEY_ENV_NAME,
                                                      help="Indicate gemini api key")
        dict_tiny_cls.img_path = cli.SwitchAttr("--img-path",
                                                cli.ExistingFile,
                                                group="Gemini",
                                                help="Indicate local image path if the model is gemini pro vision")

    def print_input(self, text):
        pass

    def do_translate(self, text):
        if self.model == GEMINI_MODEL.gemini_pro_vision.value:
            img_path, text = text.split(" ", maxsplit=1)
            try:
                img = Image.open(img_path)
            except Exception as e:
                normal_warn_printer(f"Unable to identify the image at: {img_path}")
                return
            parts = [text, img]
        else:
            parts = [text]
        try:
            self.dialogs.add({
                'role': 'user',
                'parts': parts
            })
            response = self.chat.generate_content(
                self.dialogs.get_flat(),
                generation_config=self.generation_config,
                stream=True)
        except Exception as e:
            normal_warn_printer(f"Gemini response wrong: {str(e)}")
            return

        full_response = ""
        for chunk in response:
            chunk_text = chunk.text
            self.console.print(Markdown(chunk_text))
            full_response += chunk_text
        self.dialogs.add({
            'role': 'model',
            'parts': [full_response]
        })

    def interactive_loop(self, session):
        if self.model == GEMINI_MODEL.gemini_pro_vision.value:
            normal_info_printer(
                "If you use gemini pro vision, please enter the image address first, and then enter the text separated by spaces.")
        super().interactive_loop(session)

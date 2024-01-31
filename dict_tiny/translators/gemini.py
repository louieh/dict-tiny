from pathlib import Path

import google.generativeai as genai
from plumbum import cli
from rich.markdown import Markdown

from dict_tiny.config import GEMINI_NAME, DEFAULT_GEMINI_MODEL, GEMINI_API_KEY_ENV_NAME, GEMINI_MODEL, \
    GEMINI_MODEL_DETAIL, GEMINI_MODEL_ENV_NAME, TOKEN_USAGE_FACTOR
from dict_tiny.translators.llm import DefaultLLM
from dict_tiny.util import normal_warn_printer, normal_error_printer


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
        self.img_path = self.validate_param("img_path",
                                            self.read_img,
                                            error_msg="parameter was not specified or image read failed")

    @classmethod
    def attr_setter(cls, dict_tiny_cls):
        super().attr_setter(dict_tiny_cls)
        dict_tiny_cls.use_gemini = cli.Flag(["--gemini"],
                                            group=GEMINI_NAME,
                                            help="Use Gemini API")
        dict_tiny_cls.gemini_model = cli.SwitchAttr("--gemini-model",
                                                    str,
                                                    group=GEMINI_NAME,
                                                    envname=GEMINI_MODEL_ENV_NAME,
                                                    default=DEFAULT_GEMINI_MODEL,
                                                    help="Select gemini model")
        dict_tiny_cls.gemini_api_key = cli.SwitchAttr("--gemini-key",
                                                      str,
                                                      group=GEMINI_NAME,
                                                      envname=GEMINI_API_KEY_ENV_NAME,
                                                      help="Indicate gemini api key")
        dict_tiny_cls.img_path = cli.SwitchAttr("--img-path",
                                                cli.ExistingFile,
                                                group=GEMINI_NAME,
                                                help="the path of image")

    def read_img(self, img_path):
        if not img_path:
            if self.model == GEMINI_MODEL.gemini_pro_vision.value:
                return False
            # do not need to read image if If img_path is not provided
            return True
        try:
            if not getattr(self, "img", None):
                setattr(self, "img", {
                    'mime_type': 'image/png',
                    'data': Path(img_path).read_bytes()
                })
                # try:
                #     img = Image.open(self.img_path)
                # except Exception as e:
                #     normal_warn_printer(f"Unable to identify the image at: {self.img_path}")
                #     return
        except Exception as e:
            normal_warn_printer(f"Unable to identify the image at: {img_path}")
            return False
        return True

    def _list_models(self) -> set:
        """
        Model(name='models/gemini-pro',
              base_model_id='',
              version='001',
              display_name='Gemini Pro',
              description='The best model for scaling across a wide range of tasks',
              input_token_limit=30720,
              output_token_limit=2048,
              supported_generation_methods=['generateContent', 'countTokens'],
              temperature=0.9,
              top_p=1.0,
              top_k=1)
        ...
        """
        model_set = set()
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                model_set.add(m.name)
        return model_set

    def print_input(self, text):
        pass

    def get_token_usage(self) -> int:
        return self.chat.count_tokens(self.dialogs.get_flat()).total_tokens

    def get_token_usage_window(self) -> int:
        return GEMINI_MODEL_DETAIL[self.model]["input_token_limit"] * TOKEN_USAGE_FACTOR

    def generate_user_message(self, text):
        return {
            "role": "user",
            "parts": [text]
        }

    def generate_model_message(self, text):
        return {
            "role": "model",
            "parts": [text]
        }

    def chat_completion(self, messages: list, stream=False):
        try:
            response = self.chat.generate_content(
                messages,
                generation_config=self.generation_config,
                stream=stream)
            return response
        except Exception as e:
            normal_warn_printer(f"Gemini response wrong: {str(e)}")
            return

    def parse_response(self, response):
        return response.text

    def pro_vision_helper(self, text):
        curr_question = [{
            "role": "user",
            "parts": [text, self.img]
        }]

        response = self.chat_completion(curr_question, stream=True)
        if not response: return

        for chunk in response:
            self.console.print(Markdown(chunk.text))

    def do_translate(self, text):
        if self.model == GEMINI_MODEL.gemini_pro_vision.value:
            self.pro_vision_helper(text)
            return

        curr_question = {
            "role": "user",
            "parts": [text]
        }
        prev_dialogs = self.dialogs.get_flat()
        prev_dialogs.append(curr_question)

        response = self.chat_completion(prev_dialogs, stream=True)
        if not response: return

        full_response = ""
        for chunk in response:
            chunk_text = chunk.text
            self.console.print(Markdown(chunk_text))
            full_response += chunk_text
        self.dialogs.add([curr_question,
                          {
                              "role": "model",
                              "parts": [full_response]
                          }])

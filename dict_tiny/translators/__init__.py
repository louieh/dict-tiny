from .deepl_trans import DeepLTrans
from .gemini import Gemini
from .google_trans import GoogleTrans
from .openai import OpenAI
from .youdao_trans import YoudaoTrans
from ..config import YOUDAO_NAME, GOOGLE_NAME, GEMINI_NAME, OPENAI_NAME

_ALL_TRANSLATORS = {
    YOUDAO_NAME.lower(): YoudaoTrans,
    GOOGLE_NAME.lower(): GoogleTrans,
    # DEEPL_NAME.lower(): DeepLTrans,
    GEMINI_NAME.lower(): Gemini,
    OPENAI_NAME.lower(): OpenAI
}

DEFAULT_TRANSLATOR = YoudaoTrans

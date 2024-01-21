from .gemini import Gemini
from .openai import OpenAI
from .youdao_trans import YoudaoTrans
from .google_trans import GoogleTrans
from .deepl_trans import DeepLTrans

_ALL_TRANSLATORS = [
    YoudaoTrans,
    GoogleTrans,
    # DeepLTrans
    Gemini,
    OpenAI
]

DEFAULT_TRANSLATOR = YoudaoTrans

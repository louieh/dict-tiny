from .gemini import Gemini
from .youdao_trans import YoudaoTrans
from .google_trans import GoogleTrans
from .deepl_trans import DeepLTrans

_ALL_TRANSLATORS = [
    YoudaoTrans,
    GoogleTrans,
    # DeepLTrans
    Gemini
]

DEFAULT_TRANSLATOR = YoudaoTrans

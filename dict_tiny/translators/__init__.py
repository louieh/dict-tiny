from dict_tiny.config import GOOGLE_NAME, YOUDAO_NAME
from dict_tiny.translators.google_trans import GoogleTrans
from dict_tiny.translators.youdao_trans import YoudaoTrans

_ALL_TRANSLATORS = {
    YOUDAO_NAME: YoudaoTrans,
    GOOGLE_NAME: GoogleTrans,
}

DEFAULT_TRANSLATOR = YoudaoTrans

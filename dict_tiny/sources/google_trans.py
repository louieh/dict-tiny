import requests

from dict_tiny.setting import GOOGLE_TANS_API_BASE_URL


def google_trans(text, target_language, source_language):
    """
    google translate
    :param text: text need to be translated
    :param target_language:
    :param source_language:
    :return:
    """
    try:
        resp = requests.post(GOOGLE_TANS_API_BASE_URL.format("translate"), json={
            "text": text,
            "target": target_language,
            "source": source_language,
        })
        for k, v in resp.json().items():
            print("{}: {}".format(k, v))
    except Exception as e:
        print(str(e))


def detect_language(text):
    """
    detect language
    :param text: text need to be detected
    :return:
    """
    try:
        resp = requests.post(GOOGLE_TANS_API_BASE_URL.format("detect_language"), json={
            "text": text
        })
        for k, v in resp.json().items():
            print("{}: {}".format(k, v))
    except Exception as e:
        print(str(e))

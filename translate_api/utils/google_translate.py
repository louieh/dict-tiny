from google.cloud import translate_v2 as translate
from flask import abort


class GoogleTranslate(object):
    def __int__(self):
        self.client = translate.Client()  # .from_service_account_json("TinyDict-f14aca799233.json")

    def translate(self, text, target_language):
        pass

    def detect_language(self, text):
        pass

    def get_languages(self):
        res = self.client.get_languages()
        return res

    def check_valid_lan(self, language=None):
        pass

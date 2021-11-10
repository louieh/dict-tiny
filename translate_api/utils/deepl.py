import os
import deepl


class DeepL(object):
    def __init__(self):
        DEEPL_AUTH_KEY = os.getenv("DEEPL_AUTH_KEY")
        self.translator = deepl.Translator(DEEPL_AUTH_KEY)

    def translate(self, text, target_lang="ZH"):
        try:
            res = self.translator.translate_text(text, target_lang=target_lang)
            return {"status": True, "data": {
                "detected_source_lang": res.detected_source_lang,
                "text": res.text
            }}
        except Exception as e:
            return {"status": False, "error": str(e)}

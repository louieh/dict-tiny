from google.cloud import translate_v2 as translate


class GoogleTranslate(object):
    def __init__(self):
        self.client = translate.Client()

    def get_languages(self):
        res = self.client.get_languages()
        return {"status": True, "data": res}

    def check_valid_lan(self, language):
        lan_res = self.get_languages().get("data")
        lan_res.append({'language': 'zh-CN', 'name': 'Chinese'})
        for lan_dict in lan_res:
            if language.lower() == lan_dict.get("language").lower() or language.lower() in lan_dict.get(
                    "language").lower():
                return {"status": True, "language": lan_dict.get("language"), "name": lan_dict.get("name")}
        return {"status": False}

    def detect_language(self, text):
        detect_result = self.client.detect_language(text)
        valid_lan_dict = self.check_valid_lan(detect_result.get("language"))
        if valid_lan_dict.get("status"):
            detect_result.update({"name": valid_lan_dict.get("name")})
            return {"status": True, "data": detect_result}
        return {"status": False, "error": ""}

    def translate(self, text, target_language, source_language=None):
        tar_lan_dict = self.check_valid_lan(target_language) if target_language else None
        if tar_lan_dict and not tar_lan_dict.get("status"):
            return {"status": False, "error": "target language is not valid"}
        sou_lan_dict = self.check_valid_lan(source_language) if source_language else None
        if sou_lan_dict and not sou_lan_dict.get("status"):
            return {"status": False, "error": "source language is not valid"}
        detect_res = self.detect_language(text)
        try:
            source_language = sou_lan_dict.get("language") if sou_lan_dict else None
            if not tar_lan_dict:
                if detect_res.get("language") == "en":
                    res = self.client.translate(text, target_language="zh", source_language=source_language)
                else:
                    res = self.client.translate(text, source_language=source_language)
            else:
                res = self.client.translate(text, target_language=tar_lan_dict.get("language"),
                                            source_language=source_language)
            return {"status": True, "data": res}
        except Exception as e:
            return {"status": False, "error": str(e)}

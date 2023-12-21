import requests
import time
from random import randrange
import json

API_URL = "https://www2.deepl.com/jsonrpc"

MAGIC_NUMBER = int("CAFEBABE", 16)

SUPPORTED_LANGUAGES = [
    {"code": "BG", "language": "Bulgarian"},
    {"code": "ZH", "language": "Chinese"},
    {"code": "CS", "language": "Czech"},
    {"code": "DA", "language": "Danish"},
    {"code": "NL", "language": "Dutch"},
    {"code": "EN", "language": "English"},
    {"code": "ET", "language": "Estonian"},
    {"code": "FI", "language": "Finnish"},
    {"code": "FR", "language": "French"},
    {"code": "DE", "language": "German"},
    {"code": "EL", "language": "Greek"},
    {"code": "HU", "language": "Hungarian"},
    {"code": "IT", "language": "Italian"},
    {"code": "JA", "language": "Japanese"},
    {"code": "LV", "language": "Latvian"},
    {"code": "LT", "language": "Lithuanian"},
    {"code": "PL", "language": "Polish"},
    {"code": "PT", "language": "Portuguese"},
    {"code": "RO", "language": "Romanian"},
    {"code": "RU", "language": "Russian"},
    {"code": "SK", "language": "Slovak"},
    {"code": "SL", "language": "Slovenian"},
    {"code": "ES", "language": "Spanish"},
    {"code": "SV", "language": "Swedish"},
]

SUPPORTED_FORMALITY_TONES = ["formal", "informal"]

headers = {
    "accept": "*/*",
    "accept-language": "en-US;q=0.8,en;q=0.7",
    "authority": "www2.deepl.com",
    "content-type": "application/json",
    "origin": "https://www.deepl.com",
    "referer": "https://www.deepl.com/translator",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": (
        "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/83.0.4103.97 Mobile Safari/537.36"
    ),
}


class DeeplCustomTrans(object):
    def __init__(self):
        pass

    def calculate_valid_timestamp(self, timestamp, i_count):
        try:
            return timestamp + (i_count - timestamp % i_count)
        except ZeroDivisionError:
            return timestamp

    def generate_timestamp(self, sentences):
        now = int(time.time() * 1000)
        i_count = 1
        for sentence in sentences:
            i_count += sentence.count("i")

        return self.calculate_valid_timestamp(now, i_count)

    def extract_translated_sentences(self, json_response):
        translations = json_response["result"]["translations"]
        translated_sentences = [
            translation["beams"][0]["postprocessed_sentence"]
            for translation in translations
        ]
        return translated_sentences

    def create_abbreviations_dictionary(self, languages=SUPPORTED_LANGUAGES):
        short_dict = {language["code"].lower(): language["code"] for language in languages}
        verbose_dict = {
            language["language"].lower(): language["code"] for language in languages
        }
        return {**short_dict, **verbose_dict}

    def abbreviate_language(self, language):
        language = language.lower()
        abbreviations = self.create_abbreviations_dictionary()
        return abbreviations.get(language.lower())

    def generate_jobs(self, sentences, beams=1):
        jobs = []
        for idx, sentence in enumerate(sentences):
            job = {
                "kind": "default",
                "raw_en_sentence": sentence,
                "raw_en_context_before": sentences[:idx],
                "raw_en_context_after": [sentences[idx + 1]]
                if idx + 1 < len(sentences)
                else [],
                "preferred_num_beams": beams,
            }
            jobs.append(job)
        return jobs

    def generate_common_job_params(self, formality_tone):
        if not formality_tone:
            return {}
        if formality_tone not in SUPPORTED_FORMALITY_TONES:
            raise ValueError(f"Formality tone '{formality_tone}' not supported.")
        return {"formality": formality_tone}

    def generate_translation_request_data(
            self,
            source_language,
            target_language,
            sentences,
            identifier=MAGIC_NUMBER,
            alternatives=1,
            formality_tone=None,
    ):
        return {
            "jsonrpc": "2.0",
            "method": "LMT_handle_jobs",
            "params": {
                "jobs": self.generate_jobs(sentences, beams=alternatives),
                "lang": {
                    "user_preferred_langs": [target_language, source_language],
                    "source_lang_computed": source_language,
                    "target_lang": target_language,
                },
                "priority": 1,
                "commonJobParams": self.generate_common_job_params(formality_tone),
                "timestamp": self.generate_timestamp(sentences),
            },
            "id": identifier,
        }

    def request_translation(self, source_language, target_language, text, **kwargs):
        sentences = [text]
        data = self.generate_translation_request_data(
            source_language, target_language, sentences, **kwargs
        )
        response = requests.post(API_URL, data=json.dumps(data), headers=headers)
        return response

    def translate(self, source_language, target_language, text, **kwargs):
        source_language = self.abbreviate_language(source_language)
        target_language = self.abbreviate_language(target_language)

        response = self.request_translation(source_language, target_language, text, **kwargs)
        response.raise_for_status()

        json_response = response.json()
        translated_sentences = self.extract_translated_sentences(json_response)
        translated_text = " ".join(translated_sentences)

        return translated_text

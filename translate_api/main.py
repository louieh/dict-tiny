#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, jsonify, request, abort
from utils.google_translate import GoogleTranslate
import six

# TODO 限制输入字数
# TODO 限制访问频率
# TODO 限制直接请求

# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = Flask(__name__)


@app.errorhandler(401)
def handle_bad_request_401(e):
    return 'Reformat text error: {}'.format(str(e)), 401


# @app.errorhandler(400)
# def handle_bad_request_400(e):
#     return 'Invalid language input.', 400


@app.errorhandler(404)
def handle_bad_request_404(e):
    return 'Request Translate Api error: {}'.format(str(e)), 404


@app.errorhandler(500)
def handle_bad_request_500(e):
    return 'Init error: {}'.format(str(e)), 500


@app.before_first_request
def before_first_request():
    global google_trans_client
    try:
        google_trans_client = GoogleTranslate()
    except Exception as e:
        print("init error: {}".format(str(e)))


@app.route('/test')
def hello():
    if not google_trans_client:
        abort(500)
    return 'dict tiny translate api'


@app.route('/get_languages')
def get_languages():
    try:
        res = google_trans_client.get_languages()
        return jsonify({"message": "OK: list languages", "data": res})
    except:
        abort(404)


def reformat_text(text):
    if not text:
        abort(401)
    if isinstance(text, six.binary_type):
        try:
            text = text.decode('utf-8')
        except:
            abort(401)
    if not isinstance(text, str):
        try:
            text = str(text)
        except:
            abort(401)
    return text


@app.route('/check_valid_lan', methods=["POST"])
def check_valid_lan(language=None):
    res = get_languages()
    if not language:
        language = reformat_text(request.json.get("language"))
    res.json["data"].append({'language': 'zh-CN', 'name': 'Chinese'})
    for lan_dict in res.json.get("data"):
        if language.lower() == lan_dict.get("language").lower() or language.lower() in lan_dict.get("language").lower():
            return jsonify({"status": True, "language": lan_dict.get("language"), "name": lan_dict.get("name")})
    return jsonify({"status": False})


@app.route('/detect_language', methods=["POST"])
def detect_language(text=None):
    if not text:
        text = reformat_text(request.json.get("text"))
    detect_result = client.detect_language(text)
    valid_lan_dict = check_valid_lan(detect_result.get("language"))
    if valid_lan_dict.json.get("status"):
        detect_result.update({"name": valid_lan_dict.json.get("name")})
    return jsonify(detect_result)


@app.route('/translate', methods=["POST"])
def translate_text():
    text = reformat_text(request.json.get("text"))
    target_language = request.json.get("target")
    source_language = request.json.get("source")
    tar_lan_dict = check_valid_lan(target_language).json if target_language else None
    if tar_lan_dict and not tar_lan_dict.get("status"):
        abort(400)
    sou_lan_dict = check_valid_lan(source_language).json if source_language else None
    if sou_lan_dict and not sou_lan_dict.get("status"):
        abort(400)
    detect_res = detect_language(text)
    try:
        source_language = sou_lan_dict.get("language") if sou_lan_dict else None
        if not tar_lan_dict:
            if detect_res.json.get("language") == "en":
                res = client.translate(text, target_language="zh", source_language=source_language)
            else:
                res = client.translate(text, source_language=source_language)
        else:
            res = client.translate(text, target_language=tar_lan_dict.get("language"), source_language=source_language)
        return jsonify(res)
    except Exception as e:
        abort(404)


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)

#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, jsonify, request, abort
from utils.google_translate import GoogleTranslate
from utils.deepl import DeepL
from utils.util import reformat_text

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

@app.errorhandler(417)
def handle_bad_request_417(e):
    return 'api error: {}'.format(str(e)), 417


@app.errorhandler(404)
def handle_bad_request_404(e):
    return 'Request Translate Api error: {}'.format(str(e)), 404


@app.errorhandler(500)
def handle_bad_request_500(e):
    return 'Init error: {}'.format(str(e)), 500


@app.before_first_request
def before_first_request():
    global google_trans_client
    global deepl_trans_client
    try:
        google_trans_client = GoogleTranslate()
        deepl_trans_client = DeepL()
    except Exception as e:
        print("init error: {}".format(str(e)))


@app.route('/test')
def hello():
    if not google_trans_client:
        abort(500)
    return jsonify({"code": 200, "msg": "dict tiny translate api", "data": None})


@app.route('/goog/get_languages')
def get_languages():
    ret = google_trans_client.get_languages()
    if ret.get("status"):
        return jsonify({"code": 200, "msg": "ok", "data": ret.get("data")})
    else:
        return jsonify({"code": 417, "msg": ret.get("error")})


@app.route('/goog/detect_language', methods=["POST"])
def goog_detect_language():
    text = reformat_text(request.json.get("text"))
    ret = google_trans_client.detect_language(text)
    if ret.get("status"):
        return jsonify({"code": 200, "msg": "ok", "data": ret.get("data")})
    return jsonify({"code": 417, "msg": ret.get("error")})


@app.route('/goog/translate', methods=["POST"])
def goog_translate_text():
    text = reformat_text(request.json.get("text"))
    target_language = request.json.get("target")
    source_language = request.json.get("source")
    ret = google_trans_client.translate(text, target_language, source_language)
    if ret.get("status"):
        return jsonify({"code": 200, "msg": "ok", "data": ret.get("data")})
    return jsonify({"code": 417, "msg": ret.get("error")})


@app.route('/deep/translate', methods=["POST"])
def deep_translate_text():
    text = request.json.get("text")
    target_language = request.json.get("target", "ZH")
    ret = deepl_trans_client.translate(text, target_language)
    if ret.get("status"):
        return jsonify({"code": 200, "msg": "ok", "data": ret.get("data")})
    return jsonify({"code": 417, "msg": ret.get("error")})


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)

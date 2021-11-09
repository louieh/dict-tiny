import six


def reformat_text(text):
    if not text:
        return None
    if isinstance(text, six.binary_type):
        try:
            text = text.decode('utf-8')
        except Exception as e:
            print("decode error: {}".format(str(e)))
    if not isinstance(text, str):
        try:
            text = str(text)
        except:
            print("str error: {}".format(text))
    return text

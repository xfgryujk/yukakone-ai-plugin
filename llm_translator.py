# Reference: https://nmori.github.io/yncneo-Docs/plugin/plugin_pythonunit/

#=====================================================
# ゆかコネNEO Pythonプラグイン拡張 サンプル
#=====================================================
# ・Pythonでつくれるプラグインモジュールです
# ・Pythonスクリプトで動かすより、コンパイルしたほう
#   速いですが、Pythonで書くほうがおそらく簡単です
#=====================================================

import logging.handlers
import os

import openai

logger = logging.getLogger('llm_translator')


def _init_logging():
    filename = os.path.splitext(__file__)[0] + '.log'
    handler = logging.handlers.TimedRotatingFileHandler(
        filename, encoding='utf-8', when='midnight', backupCount=1, delay=True
    )
    fmt = logging.Formatter('{asctime} {levelname} [{name}]: {message}', None, '{')
    handler.setFormatter(fmt)
    handler.setLevel(logging.INFO)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

_init_logging()


client = openai.OpenAI(api_key='no-key', base_url='http://127.0.0.1:8080/v1')

PROMPT = """\
你是一个轻小说翻译模型，可以流畅通顺地以日本轻小说的风格将日文翻译成简体中文，并联系上下文正确使用人称代词，不擅自添加原文中没有的代词。\
"""


#=====================================================
# 音声認識されたとき
#=====================================================
# これは、音声認識されるたびに呼び出されます。
# ここを書き換えると、母国語の表示を置換できます。
# Message["TextFixed"] が True ならば、音声認識で文が確定した状態です
# Message["isDeleted"] が True ならば、文が取り消されたことを意味します
# def PostRecognition(Message):
#     text = Message["Text"]
#     text = text.replace('です', 'にゃん')
#     return text


#=====================================================
# 翻訳を実行する前
#=====================================================
# これは、翻訳を掛ける前の状態を変更できます。
# Text1～Text4　は、それぞれ翻訳１～翻訳４に対応する母国語です。
# ここを書き換えたあとのものが翻訳されます。
# Message["Language1"] １～４が、翻訳先言語コードです
# Message["Native"] が母国語言語コードです
# Message["ID"] をみると、文章のユニークなIDが得られます
# def PreTranslation(Message):
#     text = Message["Text1"]
#     text = text.replace('今日', '昨日')
#     Message["Text1"] = text
#     return Message


#=====================================================
# 翻訳を実行した後
#=====================================================
# これは、翻訳を掛けたあとの状態を変更できます。
# Text1～Text4　は、それぞれ翻訳１～翻訳４に対応する翻訳後文です。
# ここを書き換えたあとのものが表示されます。
def PostTranslation(Message):
    try:
        # {'LogFolder': '...', 'ConfigFolder': '...', 'PluginFolder': '...', 'ID': '15132704-6f63-4103-9230-1cf33b32dbf6',
        # 'Version': 'Version 2.1.60', 'NativeText': 'test', 'AuthorName': '', 'Text1': '', 'Text2': '', 'Text3': '',
        # 'Text4': '', 'LanguageNative': 'ja', 'Language1': '*', 'Language2': '*', 'Language3': '*', 'Language4': '*',
        # 'UpdateTranslation': True, 'ShowCaptionMode': 0, 'TextFixed': True, 'talkerID': '639cc763-c8a3-4b64-a160-9bf1fb28a583',
        # 'talkerName': '', 'isOwnersTalkData': True, 'isDeleted': False, 'isClearTimer': False}
        # logger.info('[PostTranslation] Message=%s', {**Message})

        if Message['LanguageNative'] != 'ja' or Message['Language1'] != '*':
            return Message

        Message['Text1'] = translate(Message['NativeText'])
        return Message
    except Exception:
        logger.exception('PostTranslation error:')
        raise


def translate(input_):
    if input_ == '':
        return ''
    logger.info('<< %s', input_)

    query = '将下面的日文文本翻译成中文：' + input_
    messages=[
        {'role': 'system', 'content': PROMPT},
        {'role': 'user', 'content': query},
    ]
    extra_query = {
        'do_sample': False,
        'num_beams': 1,
        'repetition_penalty': 1.0,
    }
    rsp = client.chat.completions.create(
        model='',
        messages=messages,
        temperature=0.1,
        top_p=0.3,
        max_tokens=512,
        frequency_penalty=0.0,
        seed=-1,
        extra_query=extra_query,
        stream=False,
    )
    output = rsp.choices[0].message.content

    logger.info('>> %s', output)
    return output

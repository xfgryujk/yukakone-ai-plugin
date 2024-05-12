# Reference: https://nmori.github.io/yncneo-Docs/plugin/plugin_pythonunit/
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

API_KEY = 'no-key'
BASE_URL = 'http://127.0.0.1:8080/v1'
# https://github.com/SakuraLLM/Sakura-13B-Galgame
IS_SAKURA = True

if IS_SAKURA:
    SYSTEM_PROMPT = """\
你是一个轻小说翻译模型，可以流畅通顺地以日本轻小说的风格将日文翻译成简体中文，并联系上下文正确使用人称代词，不擅自添加原文中没有的代词。

将下面的日文文本翻译成中文：\
"""
    PRESET_MESSAGES = [
        {'role': 'system', 'content': SYSTEM_PROMPT},
    ]

    MAX_HISTORY_MESSAGES = 0
    history_messages = []

else:
    SYSTEM_PROMPT = """\
你是一个中日翻译专家。你的任务是将我说的日文翻译成流畅、地道的中文。

请遵循以下准则：

- 断句：以下的日文是语音识别的结果，可能缺少标点符号，可能不是一个完整的句子。\
你应该找到最后一个完整的句子并翻译，而在此之前的内容应该忽略。
- 谐音字：以下的日文是语音识别的结果，部分文字可能因为识别不准确而被替换为谐音字。\
如果遇到不流畅的地方，你可以合理地猜测并替换原文的文字。
- 语言和思维模式：注意中文语言的细微差别和文化思维模式，使译文能和母语人士产生共鸣。
- 标点符号：不要在翻译结果的末尾添加句号。

现在准备将我说的话翻译成中文。\
"""
    PRESET_MESSAGES = [
        {'role': 'system', 'content': SYSTEM_PROMPT},
        {'role': 'user', 'content': '配信来てくれてありがとう。'},
        {'role': 'assistant', 'content': '谢谢你来看我的直播'},
    ]

    # 带上上下文试试
    # 不能太长，否则容易复读
    MAX_HISTORY_MESSAGES = 2 * 2
    history_messages = []

client = openai.OpenAI(api_key=API_KEY, base_url=BASE_URL)


def PostTranslation(Message):
    try:
        # {'LogFolder': '...', 'ConfigFolder': '...', 'PluginFolder': '...', 'ID': '15132704-6f63-4103-9230-1cf33b32dbf6',
        # 'Version': 'Version 2.1.60', 'NativeText': 'test', 'AuthorName': '', 'Text1': '', 'Text2': '', 'Text3': '',
        # 'Text4': '', 'LanguageNative': 'ja', 'Language1': '*', 'Language2': '*', 'Language3': '*', 'Language4': '*',
        # 'UpdateTranslation': True, 'ShowCaptionMode': 0, 'TextFixed': True, 'talkerID': '639cc763-c8a3-4b64-a160-9bf1fb28a583',
        # 'talkerName': '', 'isOwnersTalkData': True, 'isDeleted': False, 'isClearTimer': False}
        # logger.info('[PostTranslation] Message=%s', {**Message})

        # 源语言必须是日语，第一个翻译引擎必须是关闭
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

    messages=[
        *PRESET_MESSAGES,
        *history_messages,
        {'role': 'user', 'content': input_},
    ]

    rsp = client.chat.completions.create(
        model='',
        messages=messages,
        temperature=0.1,
        top_p=0.3,
        max_tokens=512,
        frequency_penalty=0.0,
        seed=-1,
        extra_query={
            'do_sample': False,
            'num_beams': 1,
            'repetition_penalty': 1.0,
        },
        stream=False,
    )
    output = rsp.choices[0].message.content
    logger.info('>> %s', output)

    return post_process(input_, output)


if IS_SAKURA:
    def post_process(input_, output):
        return output

else:
    def post_process(input_, output):
        # 输出太长可能是发癫了
        input_len = len(input_)
        output_len = len(output)
        if input_len < 5:
            if output_len > 10:
                return ''
        else:
            if output_len > input_len * 2:
                return ''

        # 如果有重复输出，要清空上下文，否则会一直复读
        last_output_message = history_messages[-1] if history_messages else None
        if last_output_message and output.rstrip('。？') == last_output_message['content'].rstrip('。？'):
            history_messages.clear()
            return output

        # 添加上下文
        history_messages.append({'role': 'user', 'content': input_})
        history_messages.append({'role': 'assistant', 'content': output})
        if len(history_messages) > MAX_HISTORY_MESSAGES:
            del history_messages[:-MAX_HISTORY_MESSAGES]

        return output

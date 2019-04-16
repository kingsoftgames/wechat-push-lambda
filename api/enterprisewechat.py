import json
import logging
from botocore.vendored import requests
from helper.apireturndode import APIReturnCode
from helper.singleton import Singleton

__WECHAT_CORPID = "${im_ewc_corpid}"
__WECHAT_SECRET = "${im_ewc_corpsecret}"
__WECHAT_ACCESS_TOKEN_URL = "https://qyapi.weixin.qq.com/cgi-bin/gettoken"\
    "?corpid={}&corpsecret={}".format(__WECHAT_CORPID, __WECHAT_SECRET)
__WECHAT_SEND_URL = "https://qyapi.weixin.qq.com/cgi-bin/appchat/send"\
    "?access_token={}"

__MESSAGE_MARKDOWN = "markdown"
__MESSAGE_TEXT = "text"
__MESSAGE_TYPES = [__MESSAGE_MARKDOWN, __MESSAGE_TEXT]
__COLORS = {'green': 'info', 'gray': 'comment', 'red': 'warning'}
__logger = logging.getLogger(__name__)

__ERRCODE = "errcode"


def get_access_token():
    try:
        r = requests.get(__WECHAT_ACCESS_TOKEN_URL)
    except requests.exceptions.RequestException as e:
        __logger.exception("get_access_token RequestException")
        return APIReturnCode.REQUEST_EXCEPTION, repr(e)
    return __get_api_result(r)


def send(message, details, chat_id, message_type, color, access_token):
    url = __WECHAT_SEND_URL.format(access_token)
    try:
        r = requests.post(
            url, get_params(chat_id, message, details, message_type, color))
    except requests.exceptions.RequestException as e:
        __logger.exception("send RequestException")
        return APIReturnCode.REQUEST_EXCEPTION, repr(e)
    return __get_api_result(r)


def __get_api_result(response):
    if response.status_code == requests.codes.ok:
        wechat_ret = response.json()
        if wechat_ret[__ERRCODE] == EWeChatReturnCode.OK:
            return APIReturnCode.OK, wechat_ret
        else:
            return APIReturnCode.AIP_CODE_ERROR, wechat_ret[__ERRCODE]
    else:
        return APIReturnCode.HTTP_ERROR, str(response.status_code)


def get_params(chat_id, message, details, message_type, color):
    content = message
    if message_type == __MESSAGE_MARKDOWN:
        if color != '':
            content = "<font color=\""+__COLORS[color]+"\">●</font>  "+content
        if details != '':
            content = content+"\n>"+details

    return json.dumps({
            "chatid": chat_id,
            "msgtype": "markdown",
            "markdown": {
                "content": content
            }
        })


def check_params(chat_id, message, details, message_type, color):
    if message_type not in __MESSAGE_TYPES:
        return False

    if message_type == __MESSAGE_MARKDOWN:
        if (color != '' and color not in __COLORS):
            return False

    if chat_id == '':
        return False

    if message == '':
        return False

    if message == '' and details == '':
        return False

    return True


class EWeChatReturnCode(metaclass=Singleton):
    OK = 0
    ACCESS_TOKEN_EXPIRED = 42001
    ACCESS_TOKEN_INVALID = 40014

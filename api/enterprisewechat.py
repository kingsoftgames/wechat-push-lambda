import json
import logging
from botocore.vendored import requests
from helper.apireturndode import APIReturnCode
from helper.singleton import Singleton
from helper import rendersetting

__WECHAT_CORPID = rendersetting.WECHAT_CORPID
__WECHAT_SECRET = rendersetting.WECHAT_SECRET
__WECHAT_ACCESS_TOKEN_URL = "https://qyapi.weixin.qq.com/cgi-bin/gettoken"\
    "?corpid={}&corpsecret={}".format(__WECHAT_CORPID, __WECHAT_SECRET)
__WECHAT_SEND_URL = "https://qyapi.weixin.qq.com/cgi-bin/appchat/send"\
    "?access_token={}"
__ERRCODE = "errcode"
__logger = logging.getLogger(__name__)


def get_access_token():
    try:
        r = requests.get(__WECHAT_ACCESS_TOKEN_URL)
    except requests.exceptions.RequestException as e:
        __logger.exception("get_access_token RequestException")
        return APIReturnCode.REQUEST_EXCEPTION, repr(e)
    return __get_api_result(r)


def send(data, access_token):
    url = __WECHAT_SEND_URL.format(access_token)
    try:
        r = requests.post(url, data)
    except requests.exceptions.RequestException as e:
        __logger.exception("send RequestException")
        return APIReturnCode.REQUEST_EXCEPTION, repr(e)
    return __get_api_result(r)


def __get_api_result(response):
    if response.status_code == requests.codes.ok:
        wechat_ret = response.json()
        if wechat_ret[__ERRCODE] == EWeChatReturnCode.OK:
            return APIReturnCode.OK, response
        else:
            return APIReturnCode.AIP_CODE_ERROR, wechat_ret[__ERRCODE]
    else:
        return APIReturnCode.HTTP_ERROR, str(response.status_code)


class EWeChatReturnCode(metaclass=Singleton):
    OK = 0
    ACCESS_TOKEN_EXPIRED = 42001
    ACCESS_TOKEN_INVALID = 40014

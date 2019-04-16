import json
import boto3
from im import enterprisewechat as ewechat
from helper.returncode import ReturnCode


__SECRET_KEY = "${push_secretkey}"
__SECRET_KEY_NAME = "X-SecretKey"

__ENTERPRISE_WECHAT = "enterprise-wechat"
__SUPPORT_IMS = [__ENTERPRISE_WECHAT]


def lambda_handler(event, context):
    header = event['headers']
    if (__SECRET_KEY_NAME not in header or
            header[__SECRET_KEY_NAME] != __SECRET_KEY):
        return result(ReturnCode.SECRETKEY_EREEOR, '')

    path = event['path']
    urls = path.split('/')
    size = len(urls)
    if size != 4 and size != 2:
        return result(ReturnCode.URL_ERRROR, '')

    if size == 2:
        return result(ReturnCode.OK, json.dumps(__SUPPORT_IMS))

    path_params = event['pathParams']
    im = path_params['im']
    if im not in __SUPPORT_IMS:
        return result(ReturnCode.IM_ERRROR, '')

    chat_id = path_params['chatId']
    if im == __ENTERPRISE_WECHAT:
        data = event['body']
        code, message = ewechat.push(chat_id, data)
        return result(code, message)


def result(code, message):
    return {
        "code": code,
        "message": message
    }

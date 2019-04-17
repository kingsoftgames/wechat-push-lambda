import json
import boto3
from im import enterprisewechat as ewechat
from helper.returncode import ReturnCode
from helper import rendersetting

__SECRET_KEY = rendersetting.SECRET_KEY
__SECRET_KEY_NAME = "X-SecretKey"

__ENTERPRISE_WECHAT = "enterprise-wechat"
__SUPPORT_IMS = [__ENTERPRISE_WECHAT]


def lambda_handler(event, context):
    header = event['headers']
    if (not header or __SECRET_KEY_NAME not in header or
            header[__SECRET_KEY_NAME] != __SECRET_KEY):
        return result(ReturnCode.SECRETKEY_EREEOR, '')

    path_params = event['pathParameters']
    if not path_params:
        return result(ReturnCode.URL_ERRROR, '')

    im = path_params.get('im', '')
    if im not in __SUPPORT_IMS:
        return result(ReturnCode.IM_ERRROR, '')

    if im == __ENTERPRISE_WECHAT:
        data = event['body']
        code, ret = ewechat.push(data)
        return result(code, ret)


def result(code, ret):
    if (code == ReturnCode.OK):
        return {
            "statusCode": code,
            "headers": dict(ret.headers),
            "body": json.dumps(ret.json())
        }
    else:
        return {
            "statusCode": code,
            "headers": {
                "content-type": "application/json; charset=UTF-8"
            },
            "body": ""
        }

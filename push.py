import json
import boto3
import logging
import time
from enum import Enum, unique
from botocore.vendored import requests

"""======================for render==============================="""
__SECRET_KEY = "${push_secretkey}"
__WECHAT_CORPID = "${im_ewc_corpid}"
__WECHAT_SECRET = "${im_ewc_corpsecret}"
__TABLE_NAME = "${db_table_name}"
__HASH_KEY = "${db_hash_key}"
__REGION = "${db_region}"
"""======================for common==============================="""
__logger = logging.getLogger(__name__)


class ReturnCode:
    OK = 200
    DB_ERROR = 500
    IM_API_ERROR = 502
    RETRY_MAX = 500
    SECRETKEY_EREEOR = 401
    URL_ERRROR = 404
    IM_ERRROR = 404

ReturnCode = ReturnCode()
"""======================for push==============================="""
__SECRET_KEY_NAME = "X-SecretKey"
__ENTERPRISE_WECHAT = "enterprise-wechat"
__SUPPORT_IMS = [__ENTERPRISE_WECHAT]


def lambda_handler(event, context):
    header = event['headers']
    if (not header or __SECRET_KEY_NAME not in header or
            header[__SECRET_KEY_NAME] != __SECRET_KEY):
        return __result(ReturnCode.SECRETKEY_EREEOR, '')

    path_params = event['pathParameters']
    if not path_params:
        return __result(ReturnCode.URL_ERRROR, '')

    im = path_params.get('im', '')
    if im not in __SUPPORT_IMS:
        return __result(ReturnCode.IM_ERRROR, '')

    if im == __ENTERPRISE_WECHAT:
        data = event['body']
        code, ret = __push(json.dumps(data))
        return __result(code, ret)


def __result(code, ret):
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

"""======================service==============================="""


def __push(data, force_from_api=False):
    if RetryPolicy.exceeded_max_retry():
        return ReturnCode.RETRY_MAX, ''
    else:
        RetryPolicy.increment_retry_count()

    code, ret = __get_access_token(force_from_api)
    if code == ReturnCode.OK:
        api_code, ret = __api_send(data, ret)
        if (api_code == APIReturnCode.AIP_CODE_ERROR and
            (ret == EWeChatReturnCode.ACCESS_TOKEN_EXPIRED or
                ret == EWeChatReturnCode.ACCESS_TOKEN_INVALID)):
            return __push(data, True)
        else:
            return ReturnCode.OK, ret
    else:
        return code, ret


def __get_access_token(force_from_api=False):
    if force_from_api:
        return __get_access_token_by_api()

    db_code, ret = DbAccessToken.get(__ENTERPRISE_WECHAT)

    if db_code == DbReturnCode.TABLE_NOT_EXIST:
        return ReturnCode.DB_ERROR, str(db_code)

    if db_code == DbReturnCode.DB_ERROR:
        return ReturnCode.DB_ERROR, str(db_code)

    now = int(time.time())
    if (db_code == DbReturnCode.OK and now < ret[DbAccessToken.att_ttl()]):
        return ReturnCode.OK, ret[DbAccessToken.att_access_token()]
    else:
        db_code = DbReturnCode.ACCESS_TOKEN_NOT_EXIST
        return __get_access_token_by_api()

    if db_code == DbReturnCode.ACCESS_TOKEN_NOT_EXIST:
        return __get_access_token_by_api


def __get_access_token_by_api():
    api_code, ret = __api_get_access_token()
    if api_code == APIReturnCode.OK:
        body = ret.json()
        token = body['access_token']
        db_code = DbAccessToken.add(
            __ENTERPRISE_WECHAT, token, body['expires_in'])
        if db_code == DbReturnCode.OK:
            return ReturnCode.OK, token
        else:
            return ReturnCode.DB_ERROR, str(db_code)
    else:
        return ReturnCode.IM_API_ERROR, str(api_code)


class RetryPolicy:

    def __init__(self, max_retry_count):
        self.max_retry_count = max_retry_count
        self.retried_count = 0

    def increment_retry_count(self, count=1):
        self.retried_count += count

    def exceeded_max_retry(self):
        return (self.max_retry_count <= self.retried_count)

RetryPolicy = RetryPolicy(3)

"""======================call api==============================="""

__WECHAT_ACCESS_TOKEN_URL = "https://qyapi.weixin.qq.com/cgi-bin/gettoken"\
    "?corpid={}&corpsecret={}".format(__WECHAT_CORPID, __WECHAT_SECRET)
__WECHAT_SEND_URL = "https://qyapi.weixin.qq.com/cgi-bin/appchat/send"\
    "?access_token={}"
__ERRCODE = "errcode"


def __api_get_access_token():
    try:
        r = requests.get(__WECHAT_ACCESS_TOKEN_URL)
    except requests.exceptions.RequestException as e:
        __logger.exception("get_access_token RequestException")
        return APIReturnCode.REQUEST_EXCEPTION, repr(e)
    return __get_api_result(r)


def __api_send(data, access_token):
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
            return APIReturnCode.AIP_CODE_ERROR, response
    else:
        return APIReturnCode.HTTP_ERROR, response


@unique
class APIReturnCode(Enum):
    OK = 0
    HTTP_ERROR = 1
    REQUEST_EXCEPTION = 2
    AIP_CODE_ERROR = 3


class EWeChatReturnCode:
    OK = 0
    ACCESS_TOKEN_EXPIRED = 42001
    ACCESS_TOKEN_INVALID = 40014

EWeChatReturnCode = EWeChatReturnCode()

"""======================db==============================="""


class DbAccessToken:
    __ATTRIBUTE_ACCESS_TOKEN = "access_token"
    __ATTRIBUTE_TTL = "ttl"
    __LOCAL_ENDPOINT_URL = "http://localhost:8000"
    __dynamodb = None
    __table = None
    __exist_table = False
    __logger = logging.getLogger(__name__)

    def __init__(self, region, table_name, hash_key):
        self.__region = region
        self.__table_name = table_name
        self.__hash_key = hash_key
        self.__exist_table = False
        self.__getTable()

    def __getTable(self):
        self.__dynamodb = boto3.resource(
            'dynamodb', region_name=self.__region,
            endpoint_url=self.__LOCAL_ENDPOINT_URL)
        # endpoint_url=self.__LOCAL_ENDPOINT_URL
        table_list = self.__dynamodb.tables.all()
        for table in table_list:
            if table.table_name == self.__table_name:
                self.__exist_table = True
                break
        if self.__exist_table:
            self.__table = self.__dynamodb.Table(self.__table_name)

    def add(self, im, access_token, ttl):
        if not self.__exist_table:
            return DbReturnCode.TABLE_NOT_EXIST
        ttl = int(time.time()) + ttl
        try:
            self.__table.put_item(Item={
                    self.__hash_key: im,
                    self.__ATTRIBUTE_ACCESS_TOKEN: access_token,
                    self.__ATTRIBUTE_TTL: ttl
                })
        except ClientError:
            __logger.exception("add item error:")
            return DbReturnCode.DB_ERROR
        return DbReturnCode.OK

    def get(self, im):
        if not self.__exist_table:
            return DbReturnCode.TABLE_NOT_EXIST, ""
        try:
            response = self.__table.get_item(Key={
                self.__hash_key: im
            })
        except ClientError as e:
            self.__logger.error("get item error: %s", e)
            return DbReturnCode.DB_ERROR, ""
        key = 'Item'
        if key in response:
            item = response[key]
            return DbReturnCode.OK, item
        else:
            return DbReturnCode.ACCESS_TOKEN_NOT_EXIST, ""

    def att_ttl(self):
        return self.__ATTRIBUTE_TTL

    def att_access_token(self):
        return self.__ATTRIBUTE_ACCESS_TOKEN

DbAccessToken = DbAccessToken(__REGION, __TABLE_NAME, __HASH_KEY)


@unique
class DbReturnCode(Enum):
    OK = 0
    TABLE_NOT_EXIST = 1
    ACCESS_TOKEN_NOT_EXIST = 2
    DB_ERROR = 3

import boto3
import time
import logging
import json
from botocore.exceptions import ClientError
from enum import Enum, unique
from helper.singleton import Singleton
from helper import rendersetting


class DbAccessToken(metaclass=Singleton):

    __TABLE_NAME = rendersetting.TABLE_NAME
    __HASH_KEY = rendersetting.HASH_KEY
    __REGION = rendersetting.REGION
    __ATTRIBUTE_ACCESS_TOKEN = "access_token"
    __ATTRIBUTE_TTL = "ttl"
    __LOCAL_ENDPOINT_URL = "http://localhost:8000"
    __dynamodb = None
    __table = None
    __exist_table = False
    __logger = logging.getLogger(__name__)

    def __init__(self):
        self.__getTable()

    def __getTable(self):
        self.__dynamodb = boto3.resource(
            'dynamodb', region_name=self.__REGION)
        # endpoint_url=self.__LOCAL_ENDPOINT_URL
        table_list = self.__dynamodb.tables.all()
        for table in table_list:
            if table.table_name == self.__TABLE_NAME:
                self.__exist_table = True
                break
        if self.__exist_table:
            self.__table = self.__dynamodb.Table(self.__TABLE_NAME)

    def add(self, im, access_token, ttl):
        if not self.__exist_table:
            return DbReturnCode.TABLE_NOT_EXIST
        ttl = int(time.time()) + ttl
        print(self.__table)
        try:
            self.__table.put_item(Item={
                    self.__HASH_KEY: im,
                    self.__ATTRIBUTE_ACCESS_TOKEN: access_token,
                    self.__ATTRIBUTE_TTL: ttl
                })
        except ClientError:
            self.__logger.exception("add item error:")
            return DbReturnCode.DB_ERROR
        return DbReturnCode.OK

    def get(self, im):
        if not self.__exist_table:
            return DbReturnCode.TABLE_NOT_EXIST, ""
        try:
            response = self.__table.get_item(Key={
                self.__HASH_KEY: im
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


def db_access_token():
    return DbAccessToken()


@unique
class DbReturnCode(Enum):
    OK = 0
    TABLE_NOT_EXIST = 1
    ACCESS_TOKEN_NOT_EXIST = 2
    DB_ERROR = 3

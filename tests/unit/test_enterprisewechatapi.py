import json
import pytest
from api import enterprisewechat as api
from helper.apireturndode import APIReturnCode
from botocore.vendored import requests


def test_get_access_token():
    code, _ = api.get_access_token()
    assert code == APIReturnCode.OK


def test_send():
    access_token = "aaa"
    message = "我是測試"
    details = """我是詳情1
            ssss
            ssss"""
    chatid = "aa"
    message_type = "markdown"
    color = "green"
    code, _ = api.send(
        message, details, chatid, message_type, color, access_token)
    assert code == APIReturnCode.OK

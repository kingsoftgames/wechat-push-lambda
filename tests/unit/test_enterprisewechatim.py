import pytest
from im import enterprisewechat as wechat
from helper.returncode import ReturnCode


def test_wechatim_push():
    message = "我是第二測試3"
    details = """我是詳情1
            ssss
            ssss"""
    chat_id = "aa"
    message_type = "markdown"
    color = "green"
    data = {'message': message, 'message_type': message_type, 'color': color}
    data['details'] = details
    code, ret = wechat.push(chat_id, data)
    assert code == ReturnCode.OK

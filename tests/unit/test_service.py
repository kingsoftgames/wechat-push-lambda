import pytest
import json
from function.push import __push
from function.push import ReturnCode


def test_wechatim_push():
    data = {
        "chatid": "ss",
        "msgtype": "markdown",
        "markdown": {
            "content": "test1"
        }
    }
    code, ret = __push(json.dumps(data))
    assert code == ReturnCode.OK

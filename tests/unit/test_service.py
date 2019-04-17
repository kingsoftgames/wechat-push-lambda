import pytest
import json
from push import __push
from push import ReturnCode


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

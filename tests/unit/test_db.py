import json
import pytest
import time
from function.push import DbAccessToken
from function.push import DbReturnCode


def test_add_access_token():
    DbAccessToken.add("qq", "dd", 1)


def test_get_access_token():
    code, _ = DbAccessToken.get("qq")
    assert code == DbReturnCode.OK

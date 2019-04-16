import json
import pytest
import time
from db import db_access_token
from db import DbReturnCode


def test_ceate_table():
    db_access_token().create_table()


def test_add_access_token():
    db_access_token().add("qq", "xcccccccccc", 1)


def test_get_access_token():
    code, _ = db_access_token().get("qq")
    assert code == DbReturnCode.OK

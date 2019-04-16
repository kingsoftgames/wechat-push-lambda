import json
import time
from api import enterprisewechat as api
from api.enterprisewechat import EWeChatReturnCode
from db import db_access_token
from db import DbReturnCode
from helper.returncode import ReturnCode
from helper.apireturndode import APIReturnCode
from helper.retrypolicy import get_retry_policy

__IM = "enterprise_wechat"
__OK_MESSAGE = "ok"
__retry = get_retry_policy()


def push(chat_id, data, force_from_api=False):
    if __retry.exceeded_max_retry():
        return ReturnCode.RETRY_MAX, ''
    else:
        __retry.increment_retry_count()

    message = data.get('message', '')
    details = data.get('details', '')
    message_type = data.get('message_type', '')
    color = data.get('color', '')

    check = api.check_params(chat_id, message, details, message_type, color)

    if not check:
        return ReturnCode.PARAMS_ERROR, json.dumps(data)
    code, ret = __get_access_token(force_from_api)
    if code == ReturnCode.OK:
        api_code, ret = api.send(
            message, details, chat_id, message_type, color, ret)
        if api_code == APIReturnCode.OK:
            return ReturnCode.OK, __OK_MESSAGE
        else:
            if (api_code == APIReturnCode.AIP_CODE_ERROR and
                    (ret == EWeChatReturnCode.ACCESS_TOKEN_EXPIRED or
                        ret == EWeChatReturnCode.ACCESS_TOKEN_INVALID)):
                return push(chat_id, data, True)
            else:
                return ReturnCode.IM_API_ERROR, ret
    else:
        return code, ret


def __get_access_token(force_from_api=False):
    if force_from_api:
        return __get_access_token_by_api()

    db_code, ret = db_access_token().get(__IM)

    if db_code == DbReturnCode.TABLE_NOT_EXIST:
        return ReturnCode.DB_ERROR, ret

    if db_code == DbReturnCode.DB_ERROR:
        return ReturnCode.DB_ERROR, ret

    now = int(time.time())
    if (db_code == DbReturnCode.OK and now < ret[db_access_token().att_ttl()]):
        return ReturnCode.OK, ret[db_access_token().att_access_token()]
    else:
        db_code = DbReturnCode.ACCESS_TOKEN_NOT_EXIST
        return __get_access_token_by_api()

    if db_code == DbReturnCode.ACCESS_TOKEN_NOT_EXIST:
        return __get_access_token_by_api


def __get_access_token_by_api():
    api_code, ret = api.get_access_token()
    if api_code == APIReturnCode.OK:
        token = ret['access_token']
        db_code = db_access_token().add(__IM, token, ret['expires_in'])
        if db_code == DbReturnCode.OK:
            return ReturnCode.OK, token
        else:
            return ReturnCode.DB_ERROR, str(db_code)
    else:
        return ReturnCode.IM_API_ERROR, str(api_code)

from helper.singleton import Singleton


class ReturnCode(metaclass=Singleton):
    OK = 200
    DB_ERROR = 500
    IM_API_ERROR = 502
    RETRY_MAX = 500
    SECRETKEY_EREEOR = 401
    URL_ERRROR = 404
    IM_ERRROR = 404

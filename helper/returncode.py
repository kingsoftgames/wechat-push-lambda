from helper.singleton import Singleton


class ReturnCode(metaclass=Singleton):
    OK = 0
    DB_ERROR = 1
    IM_API_ERROR = 2
    PARAMS_ERROR = 3
    RETRY_MAX = 4
    SECRETKEY_EREEOR = 5
    URL_ERRROR = 6
    IM_ERRROR = 6

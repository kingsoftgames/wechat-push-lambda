from enum import Enum, unique


@unique
class APIReturnCode(Enum):
    OK = 0
    HTTP_ERROR = 1
    REQUEST_EXCEPTION = 2
    AIP_CODE_ERROR = 3

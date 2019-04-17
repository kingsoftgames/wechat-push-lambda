import json
import pytest

from push import lambda_handler


@pytest.fixture()
def apigw_event():
    """ Generates API GW Event"""

    return {
        'resource': '/push/{im}',
        'path': '/push/',
        'httpMethod': 'POST',
        'headers':
        {
            'X-SecretKey': 'aa'
        },
        'multiValueHeaders': None,
        'queryStringParameters': None,
        'multiValueQueryStringParameters': None,
        'pathParameters':
        {
            'im': "enterprise-wechat"
        },
        'stageVariables': None,
        'requestContext':
        {
            'path': '/push/{im}',
            'accountId': '216927468640',
            'resourceId': 'dwiqen',
            'stage': 'test-invoke-stage',
            'domainPrefix': 'testPrefix',
            'requestId': 'd3a9322c-60ec-11e9-9fb9-435fa8ab9898',
            'identity':
            {
                'cognitoIdentityPoolId': None,
                'cognitoIdentityId': None,
                'apiKey': 'test-invoke-api-key',
                'cognitoAuthenticationType': None,
                'userArn': 'arn:aws-cn:iam::216927468640:user/jianghaitao',
                'apiKeyId': 'test-invoke-api-key-id',
                'userAgent': 'aws-internal/3 aws-sdk-java/1.11.498 Linux/4.9.\
                    137-0.1.ac.218.74.329.metal1.x86_64 OpenJDK_64-\
                        Bit_Server_VM/25.202-b08 java/1.8.0_202',
                'accountId': '216927468640',
                'caller': 'AIDAO4OTWWCBQFG63TKEO',
                'sourceIp': 'test-invoke-source-ip',
                'accessKey': 'ASIATFAPCPRQJEPFIH22',
                'cognitoAuthenticationProvider': None,
                'user': 'AIDAO4OTWWCBQFG63TKEO'
            },
            'domainName': 'testPrefix.testDomainName',
            'resourcePath': '/push/{im}',
            'httpMethod': 'POST',
            'extendedRequestId': 'YRkMjGft5PgFY9g=',
            'apiId': '9tnh3yp2b6'
        },
        'body': {
            'chatid': 'aa',
            'msgtype': 'markdown',
            'markdown': {
                'content': 'test'
            }
        },
        'isBase64Encoded': False
        }


def test_lambda_handler(apigw_event):

    ret = lambda_handler(apigw_event, "")
    assert ret["statusCode"] >= ReturnCode.OK

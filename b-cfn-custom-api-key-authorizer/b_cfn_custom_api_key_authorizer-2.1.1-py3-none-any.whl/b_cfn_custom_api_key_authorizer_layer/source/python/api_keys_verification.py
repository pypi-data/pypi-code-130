import logging
import os

import boto3
from botocore.exceptions import ClientError

from auth_exception import AuthException
from api_secret_hash import ApiSecretHash

logger = logging.getLogger(__name__)


class ApiKeysVerification:
    """
    Class responsible for api key verification. The inspiration is taken from this example:
    https://github.com/awslabs/aws-support-tools/blob/master/Cognito/decode-verify-jwt/decode-verify-jwt.py
    """

    def __init__(self, api_key: str, api_secret: str):
        self.__api_key = api_key
        self.__api_secret = api_secret
        self.__api_key_database_name = os.environ.get('API_KEYS_DATABASE_NAME')

        if (not api_key) or (not isinstance(api_key, str)):
            raise AuthException('Api Key not provided.')

        if (not api_secret) or (not isinstance(api_secret, str)):
            raise AuthException('Api Secret not provided.')

        if not self.__api_key_database_name:
            raise ValueError('Database not configured.')

    def verify(self) -> None:
        """
        Verifies the provided api key. If api key is not valid
        an exception is thrown. If no exception is thrown - api key is valid.

        :return: No return.
        """
        try:
            dynamodb = boto3.resource('dynamodb')
            table = dynamodb.Table(self.__api_key_database_name)
            data = table.get_item(Key={'ApiKey': self.__api_key})
        except ClientError:
            raise AuthException('Could not retrieve api key from database.')

        data = data.get('Item', {})
        api_key = data.get('ApiKey')
        api_secret_hash = data.get('ApiSecretHash')

        if (not api_key) or (not isinstance(api_key, str)):
            raise AuthException('Database error.')

        if (not api_secret_hash) or (not isinstance(api_secret_hash, str)):
            raise AuthException('Database error.')

        if not api_key == self.__api_key:
            logger.info(
                f'Given api key ({self.__api_key}) '
                f'does not match database api key ({api_key}).'
            )

            raise AuthException('Invalid authentication.')

        if not api_secret_hash == ApiSecretHash.hash_api_secret(self.__api_secret):
            logger.info(
                f'Given api secret ({self.__api_secret[:3]}... hash) '
                f'does not match database api secret hash.'
            )

            raise AuthException('Invalid authentication.')

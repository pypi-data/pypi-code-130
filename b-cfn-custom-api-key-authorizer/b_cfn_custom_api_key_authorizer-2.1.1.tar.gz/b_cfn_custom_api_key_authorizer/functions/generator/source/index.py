import logging
import os
import random
import string

import boto3
from botocore.exceptions import ClientError

# These imports come from a layer.
from api_secret_hash import ApiSecretHash

logger = logging.getLogger(__name__)


def handler(event, context):
    try:
        key = generate_api_key()
        secret = generate_api_secret()
        secret_hash = ApiSecretHash.hash_api_secret(secret)

        data = {
            'ApiKey': key,
            'ApiSecretHash': secret_hash
        }

        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(os.environ.get('API_KEYS_DATABASE_NAME'))
        table.put_item(Item=data)
    except ClientError as e:
        client_error_message = e.response['Error']['Message']
        logger.exception(f'Failed to call dynamodb table. {client_error_message}.')
        raise ValueError('Could not generate and save api keys.')

    return {
        'ApiKey': key,
        'ApiSecret': secret
    }


def generate_api_key() -> str:
    space = string.ascii_uppercase + string.digits
    return ''.join(random.choices(space, k=15))


def generate_api_secret() -> str:
    simple_punctuation = '!@#%^&*()_+'
    space = string.ascii_letters + string.digits + simple_punctuation
    return ''.join(random.choices(space, k=30))

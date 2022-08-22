import logging
import os

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


def handler(event, context):
    api_key = event['ApiKey']

    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(os.environ.get('API_KEYS_DATABASE_NAME'))
        table.delete_item(Key={
            'ApiKey': api_key,
        })
    except ClientError as e:
        client_error_message = e.response['Error']['Message']
        logger.exception(f'Failed to call dynamodb table. {client_error_message}.')
        raise ValueError('Could not delete api keys.')

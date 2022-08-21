import logging

# These imports come from a layer.
from api_keys_verification import ApiKeysVerification
from auth_exception import AuthException

logger = logging.getLogger(__name__)


def handler(event, context):
    api_key = event['ApiKey']
    api_secret = event['ApiSecret']

    try:
        ApiKeysVerification(api_key, api_secret).verify()
        logger.info(f'Authentication succeeded for api key: {api_key}.')
        return {'Valid': True}
    except AuthException as ex:
        logger.info(f'Authentication failed for api key: {api_key}. Message: {repr(ex)}.')
        return {'Valid': False}

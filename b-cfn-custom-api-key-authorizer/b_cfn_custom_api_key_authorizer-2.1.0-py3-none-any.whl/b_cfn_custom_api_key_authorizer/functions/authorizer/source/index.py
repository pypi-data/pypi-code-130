import base64
import json
import logging
import os
from typing import Dict, Any, Tuple, Optional

# These imports come from a layer.
from api_keys_verification import ApiKeysVerification
from auth_exception import AuthException

from policy_document import PolicyDocument

# Allow extensive logging even with other file and other layer levels.
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
for handler in root_logger.handlers:
    handler.setLevel(logging.INFO)
logger = logging.getLogger(__name__)


def handler(event, context):
    logger.info(f'Received event:\n{json.dumps(event)}.')

    # Extract api key and secret from lambda event in various strategies.
    api_key, api_secret = __extract_api_key_secret_from_event(event)

    document = PolicyDocument(
        region=os.environ['AWS_REGION'],
        account_id=os.environ['AWS_ACCOUNT'],
        api_id=os.environ['AWS_API_ID'],
        api_key=api_key
    )

    logger.info('Attempting to verify api keys...')

    # Verify the authorization token.
    try:
        ApiKeysVerification(api_key, api_secret).verify()
        logger.info(f'Authentication succeeded for api key: {api_key}.')
        # Authorization was successful. Return "Allow".
        return document.create_policy_statement(allow=True)
    except AuthException as ex:
        # Log the error.
        logger.info(f'Authentication failed for api key: {api_key}. Message: {repr(ex)}.')
        # Authorization has failed. Return "Deny".
        return document.create_policy_statement(allow=False)


def __extract_api_key_secret_from_event(event: Dict[str, Any]) -> Tuple[Optional[str], Optional[str]]:
    # Firstly, try to extract from ApiKey & ApiSecret headers.
    # (identity_source=['$request.header.ApiKey', '$request.header.ApiSecret']).
    api_key: Optional[str] = event.get('headers', {}).get('apikey')
    api_secret: Optional[str] = event.get('headers', {}).get('apisecret')

    if api_key and api_secret:
        return api_key, api_secret

    # Secondly, try to extract from basic auth (which is way more standard).
    # (identity_source=['$request.header.Authorization']).
    basic_auth: Optional[str] = event.get('headers', {}).get('authorization')
    if basic_auth:
        basic_auth = basic_auth.replace('Basic ', '')
        basic_auth = base64.b64decode(basic_auth.encode()).decode()
        api_key, api_secret = basic_auth.split(':', maxsplit=1)
        return api_key, api_secret

    return None, None

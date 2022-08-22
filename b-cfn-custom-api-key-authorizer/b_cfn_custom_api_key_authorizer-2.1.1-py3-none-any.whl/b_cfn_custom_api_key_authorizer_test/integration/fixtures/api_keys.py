from typing import Callable, Tuple

from pytest import fixture

from b_cfn_custom_api_key_authorizer_test.integration.infrastructure.main_stack import MainStack
from b_cfn_custom_api_key_authorizer_test.integration.util.lambda_invoke import LambdaInvoke


@fixture(scope='function')
def api_keys_function() -> Callable[..., Tuple[str, str]]:
    """
    Fixture that returns a function.
    The function saves an api key - api secret pair object in database and
    returns a tuple (ApiKey, ApiSecret).

    This fixture does automatic cleanup (deletes the pair in the database) after test run.

    :return: Returns a function that saves api keys in database
        and returns a tuple representation of api keys.
    """
    generator_function = MainStack.get_output(MainStack.GENERATOR_FUNCTION)
    deleter_function = MainStack.get_output(MainStack.DELETER_FUNCTION)

    api_keys = []

    def __create_api_keys() -> Tuple[str, str]:
        response = LambdaInvoke(generator_function).invoke()

        # Extract generated api key and api secret.
        api_key = response['ApiKey']
        api_secret = response['ApiSecret']

        api_keys.append(api_key)

        return api_key, api_secret

    yield __create_api_keys

    for key in api_keys:
        LambdaInvoke(deleter_function).invoke({
            'ApiKey': key
        })


@fixture(scope='function')
def api_keys(api_keys_function) -> Tuple[str, str]:
    """
    Fixture that saves an api key - api secret pair object in database and
    returns a tuple (ApiKey, ApiSecret).

    This fixture does automatic cleanup (deletes the pair in the database) after test run.

    :return: Returns a tuple of api key and secret.
    """

    return api_keys_function()

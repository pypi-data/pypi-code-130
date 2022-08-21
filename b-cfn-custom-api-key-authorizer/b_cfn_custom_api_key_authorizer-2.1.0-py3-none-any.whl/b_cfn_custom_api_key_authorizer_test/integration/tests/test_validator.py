from b_cfn_custom_api_key_authorizer_test.integration.infrastructure.main_stack import MainStack
from b_cfn_custom_api_key_authorizer_test.integration.util.lambda_invoke import LambdaInvoke


def test_FUNCTION_validator_WITH_valid_api_keys_EXPECT_response_valid(api_keys):
    function = MainStack.get_output(MainStack.VALIDATOR_FUNCTION)
    api_key, api_secret = api_keys

    response = LambdaInvoke(function).invoke({
        'ApiKey': api_key,
        'ApiSecret': api_secret
    })

    assert response['Valid'] is True


def test_FUNCTION_validator_WITH_invalid_api_keys_EXPECT_response_invalid():
    function = MainStack.get_output(MainStack.VALIDATOR_FUNCTION)

    response = LambdaInvoke(function).invoke({
        'ApiKey': '123',
        'ApiSecret': '456'
    })

    assert response['Valid'] is False

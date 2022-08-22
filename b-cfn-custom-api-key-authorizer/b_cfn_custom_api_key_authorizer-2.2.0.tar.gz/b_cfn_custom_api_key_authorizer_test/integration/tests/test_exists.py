from b_cfn_custom_api_key_authorizer_test.integration.infrastructure.main_stack import MainStack
from b_cfn_custom_api_key_authorizer_test.integration.util.lambda_invoke import LambdaInvoke


def test_FUNCTION_exists_WITH_non_existent_api_keys_EXPECT_does_not_exist_response():
    function = MainStack.get_output(MainStack.EXISTS_FUNCTION)

    response = LambdaInvoke(function).invoke({
        'ApiKey': 'non-existent-api-key-123-abc'
    })

    assert response['Exists'] is False


def test_FUNCTION_exists_WITH_existing_api_keys_EXPECT_exists_response(api_keys):
    function = MainStack.get_output(MainStack.EXISTS_FUNCTION)
    api_key, _ = api_keys

    response = LambdaInvoke(function).invoke({
        'ApiKey': api_key
    })

    assert response['Exists'] is True

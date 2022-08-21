from b_cfn_custom_api_key_authorizer_test.integration.infrastructure.main_stack import MainStack
from b_cfn_custom_api_key_authorizer_test.integration.util.lambda_invoke import LambdaInvoke


def test_FUNCTION_deleter_WITH_non_existent_api_keys_EXPECT_no_error():
    function = MainStack.get_output(MainStack.DELETER_FUNCTION)
    LambdaInvoke(function).invoke({'ApiKey': 'non-existent-api-key-123-abc'})


def test_FUNCTION_deleter_WITH_existing_api_keys_EXPECT_deleted(api_keys):
    deleter_function = MainStack.get_output(MainStack.DELETER_FUNCTION)
    exists_function = MainStack.get_output(MainStack.EXISTS_FUNCTION)

    api_key, _ = api_keys

    response = LambdaInvoke(exists_function).invoke({'ApiKey': api_key})
    assert response['Exists'] is True

    LambdaInvoke(deleter_function).invoke({'ApiKey': api_key})

    response = LambdaInvoke(exists_function).invoke({'ApiKey': api_key})
    assert response['Exists'] is False

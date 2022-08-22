from b_cfn_custom_api_key_authorizer_test.integration.infrastructure.main_stack import MainStack
from b_cfn_custom_api_key_authorizer_test.integration.util.lambda_invoke import LambdaInvoke


def test_FUNCTION_generator_WITH_valid_configuration_EXPECT_generated():
    generator_function = MainStack.get_output(MainStack.GENERATOR_FUNCTION)
    exists_function = MainStack.get_output(MainStack.EXISTS_FUNCTION)

    response = LambdaInvoke(generator_function).invoke()
    api_key = response['ApiKey']

    response = LambdaInvoke(exists_function).invoke({'ApiKey': api_key})
    assert response['Exists'] is True

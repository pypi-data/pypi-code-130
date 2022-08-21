from aws_cdk.core import Construct
from b_aws_testing_framework.tools.cdk_testing.testing_stack import TestingStack

from b_cfn_custom_api_key_authorizer_test.integration.infrastructure.api_key_secret_auth_endpoint_stack import ApiKeySecretAuthEndpointStack
from b_cfn_custom_api_key_authorizer_test.integration.infrastructure.authorized_api_stack import AuthorizedApiStack
from b_cfn_custom_api_key_authorizer_test.integration.infrastructure.basic_auth_endpoint_stack import BasicAuthEndpointStack


class MainStack(TestingStack):
    # Used to test apikey - apisecret headers.
    API_ENDPOINT1 = 'ApiEndpoint1'
    # Used to test authorization header.
    API_ENDPOINT2 = 'ApiEndpoint2'

    AUTHORIZER_FUNCTION = 'AuthorizerFunction'
    DELETER_FUNCTION = 'DeleterFunction'
    EXISTS_FUNCTION = 'ExistsFunction'
    GENERATOR_FUNCTION = 'GeneratorFunction'
    VALIDATOR_FUNCTION = 'ValidatorFunction'

    def __init__(self, scope: Construct) -> None:
        super().__init__(scope=scope)

        self.api_stack = AuthorizedApiStack(self)
        self.api = self.api_stack.api
        self.stage = self.api_stack.stage

        """
        Endpoint 1.
        """

        endpoint1 = ApiKeySecretAuthEndpointStack(self, self.api)
        endpoint1_path = f'{self.api.attr_api_endpoint}/{self.stage.stage_name}{endpoint1.path}'
        self.add_output(self.API_ENDPOINT1, value=endpoint1_path)

        a1 = endpoint1.authorizer_api_key_and_secret
        self.add_output(self.AUTHORIZER_FUNCTION, value=a1.authorizer_function.function_name)
        self.add_output(self.DELETER_FUNCTION, value=a1.deleter_function.function_name)
        self.add_output(self.EXISTS_FUNCTION, value=a1.exists_function.function_name)
        self.add_output(self.GENERATOR_FUNCTION, value=a1.generator_function.function_name)
        self.add_output(self.VALIDATOR_FUNCTION, value=a1.validator_function.function_name)

        """
        Endpoint 2.
        """

        # Allow both authorizers to share the same api keys database, because our generator functions and
        # fixtures are looking only to a single database.
        endpoint2 = BasicAuthEndpointStack(self, self.api, endpoint1.authorizer_api_key_and_secret.api_keys_database)
        endpoint2_path = f'{self.api.attr_api_endpoint}/{self.stage.stage_name}{endpoint2.path}'
        self.add_output(self.API_ENDPOINT2, value=endpoint2_path)

from aws_cdk.aws_apigatewayv2 import CfnRoute, CfnApi
from aws_cdk.aws_dynamodb import Table
from aws_cdk.aws_lambda import Function, Code, Runtime, CfnPermission
from aws_cdk.core import Stack, Duration
from b_aws_testing_framework.tools.cdk_testing.testing_stack import TestingStack
from b_cfn_lambda_integration.lambda_integration import LambdaIntegration

from b_cfn_custom_api_key_authorizer.authorization_type import AuthorizationType
from b_cfn_custom_api_key_authorizer.custom_authorizer import ApiKeyCustomAuthorizer


class BasicAuthEndpointStack(Stack):
    def __init__(self, scope: Stack, api: CfnApi, custom_api_keys_database: Table):
        prefix = TestingStack.global_prefix() + 'BasicAuth'

        super().__init__(
            scope=scope,
            id=prefix + 'EndpointStack'
        )

        self.authorizer_basic_auth = ApiKeyCustomAuthorizer(
            scope=self,
            resource_name_prefix=prefix,
            api=api,
            authorization_type=AuthorizationType.AUTHORIZATION_HEADER,
            custom_api_keys_database=custom_api_keys_database
        )

        self.api_endpoint_function = Function(
            scope=self,
            id=prefix + 'ApiFunction',
            function_name=f'{prefix}ApiFunction',
            code=Code.from_inline(
                'def handler(event, context):\n'
                '    print(event)\n'
                '    return {\n'
                '        "statusCode": 200,\n'
                '        "headers": {},\n'
                '        "body": "Hello World!",\n'
                '        "isBase64Encoded": False'
                '    }'
            ),
            handler='index.handler',
            runtime=Runtime.PYTHON_3_7,
            memory_size=128,
            timeout=Duration.seconds(30),
        )

        CfnPermission(
            scope=self,
            id=f'{prefix}InvokePermission',
            action='lambda:InvokeFunction',
            function_name=self.api_endpoint_function.function_name,
            principal='apigateway.amazonaws.com',
        )

        self.integration = LambdaIntegration(
            scope=self,
            api=api,
            integration_name=f'{prefix}Integration',
            lambda_function=self.api_endpoint_function
        )

        self.path = '/dummy2'

        self.route = CfnRoute(
            scope=self,
            id='DummyRoute',
            api_id=api.ref,
            route_key=f'GET {self.path}',
            authorization_type='CUSTOM',
            target=f'integrations/{self.integration.ref}',
            authorizer_id=self.authorizer_basic_auth.ref
        )

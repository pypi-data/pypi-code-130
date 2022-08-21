from aws_cdk.aws_apigatewayv2 import CfnApi
from aws_cdk.aws_lambda import Code, CfnPermission
from aws_cdk.core import Stack

from b_cfn_custom_api_key_authorizer.api_keys_database import ApiKeysDatabase
from b_cfn_custom_api_key_authorizer.functions.base_function import BaseFunction
from b_cfn_custom_api_key_authorizer_layer.authorizer_layer import AuthorizerLayer


class AuthorizerFunction(BaseFunction):
    def __init__(
            self,
            scope: Stack,
            name: str,
            parent_api: CfnApi,
            api_keys_database: ApiKeysDatabase,
            authorizer_layer: AuthorizerLayer
    ) -> None:
        super().__init__(
            scope=scope,
            name=name,
            api_keys_database=api_keys_database,
            authorizer_layer=authorizer_layer
        )

        # These environment variables are necessary for a lambda function to create
        # a policy document to allow/deny access. Read more here:
        # https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-lambda-authorizer-output.html
        self.add_environment('AWS_ACCOUNT', scope.account)
        self.add_environment('AWS_API_ID', parent_api.ref)

        CfnPermission(
            scope=scope,
            id='InvokePermission',
            action='lambda:InvokeFunction',
            function_name=self.function_name,
            principal='apigateway.amazonaws.com',
        )

    def code(self) -> Code:
        from .source import root
        return Code.from_asset(root)

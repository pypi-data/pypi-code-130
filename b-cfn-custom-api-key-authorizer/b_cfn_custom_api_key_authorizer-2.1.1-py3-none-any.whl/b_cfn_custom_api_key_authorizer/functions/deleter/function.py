from aws_cdk.aws_lambda import Code
from aws_cdk.core import Stack

from b_cfn_custom_api_key_authorizer.api_keys_database import ApiKeysDatabase
from b_cfn_custom_api_key_authorizer.functions.base_function import BaseFunction
from b_cfn_custom_api_key_authorizer_layer.authorizer_layer import AuthorizerLayer


class DeleterFunction(BaseFunction):
    def __init__(
            self,
            scope: Stack,
            name: str,
            api_keys_database: ApiKeysDatabase,
            authorizer_layer: AuthorizerLayer
    ) -> None:
        super().__init__(
            scope=scope,
            name=name,
            api_keys_database=api_keys_database,
            authorizer_layer=authorizer_layer
        )

    def code(self) -> Code:
        from .source import root
        return Code.from_asset(root)

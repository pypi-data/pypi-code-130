from abc import abstractmethod, ABC

from aws_cdk.aws_iam import PolicyStatement
from aws_cdk.aws_lambda import Function, Code, Runtime
from aws_cdk.aws_logs import RetentionDays
from aws_cdk.core import Duration, Stack

from b_cfn_custom_api_key_authorizer.api_keys_database import ApiKeysDatabase
from b_cfn_custom_api_key_authorizer_layer.authorizer_layer import AuthorizerLayer


class BaseFunction(ABC, Function):
    def __init__(
            self,
            scope: Stack,
            name: str,
            api_keys_database: ApiKeysDatabase,
            authorizer_layer: AuthorizerLayer,
            *args,
            **kwargs
    ) -> None:
        super().__init__(
            scope=scope,
            id=name,
            function_name=name,
            code=self.code(),
            handler='index.handler',
            runtime=Runtime.PYTHON_3_8,
            log_retention=RetentionDays.ONE_MONTH,
            memory_size=128,
            timeout=Duration.seconds(30),
            *args,
            **kwargs
        )

        self.add_layers(authorizer_layer)

        # We want the functions to be able to access and manage the api keys database.
        self.add_environment('API_KEYS_DATABASE_NAME', api_keys_database.table_name)
        self.add_to_role_policy(
            PolicyStatement(
                actions=[
                    # Read actions.
                    'dynamodb:GetItem',
                    'dynamodb:Scan',
                    'dynamodb:Query',
                    'dynamodb:DescribeTable',
                    # Write actions.
                    'dynamodb:PutItem',
                    'dynamodb:DeleteItem',
                    'dynamodb:UpdateItem',
                    'dynamodb:BatchWriteItem'
                ],
                resources=[api_keys_database.table_arn]
            ))

    @abstractmethod
    def code(self) -> Code:
        pass

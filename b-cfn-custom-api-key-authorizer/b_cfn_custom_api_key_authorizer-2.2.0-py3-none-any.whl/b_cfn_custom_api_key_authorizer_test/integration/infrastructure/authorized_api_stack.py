from aws_cdk.aws_apigatewayv2 import CfnApi, CfnStage
from aws_cdk.core import Construct, Stack
from b_aws_testing_framework.tools.cdk_testing.testing_stack import TestingStack


class AuthorizedApiStack(Stack):
    def __init__(self, scope: Construct) -> None:
        prefix = TestingStack.global_prefix()

        super().__init__(
            scope=scope,
            id=prefix + 'ApiStack'
        )

        self.api = CfnApi(
            scope=self,
            id='Api',
            name=f'{prefix}Api',
            description='Sample description.',
            protocol_type='HTTP',
            cors_configuration=CfnApi.CorsProperty(
                allow_methods=['GET', 'PUT', 'POST', 'OPTIONS', 'DELETE'],
                allow_origins=['*'],
                allow_headers=[
                    'Content-Type',
                    'Authorization'
                ],
                max_age=300
            )
        )

        self.stage: CfnStage = CfnStage(
            scope=self,
            id='Stage',
            stage_name='test',
            api_id=self.api.ref,
            auto_deploy=True,
        )

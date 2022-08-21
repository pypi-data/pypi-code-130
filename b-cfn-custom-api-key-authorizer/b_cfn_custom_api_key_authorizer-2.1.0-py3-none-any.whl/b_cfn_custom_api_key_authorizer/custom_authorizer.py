from typing import Optional

from aws_cdk.aws_apigatewayv2 import CfnAuthorizer, CfnApi
from aws_cdk.aws_dynamodb import Table
from aws_cdk.core import Stack

from b_cfn_custom_api_key_authorizer.api_keys_database import ApiKeysDatabase
from b_cfn_custom_api_key_authorizer.authorization_type import AuthorizationType
from b_cfn_custom_api_key_authorizer.functions.authorizer.function import AuthorizerFunction
from b_cfn_custom_api_key_authorizer.functions.deleter.function import DeleterFunction
from b_cfn_custom_api_key_authorizer.functions.exists.function import ExistsFunction
from b_cfn_custom_api_key_authorizer.functions.generator.function import GeneratorFunction
from b_cfn_custom_api_key_authorizer.functions.validator.function import ValidatorFunction
from b_cfn_custom_api_key_authorizer_layer.authorizer_layer import AuthorizerLayer


class ApiKeyCustomAuthorizer(CfnAuthorizer):
    def __init__(
            self,
            scope: Stack,
            resource_name_prefix: str,
            api: CfnApi,
            cache_ttl: int = 60,
            authorization_type: AuthorizationType = AuthorizationType.API_KEY_AND_SECRET_HEADERS,
            custom_api_keys_database: Optional[Table] = None
    ) -> None:
        """
        Constructor.

        :param scope: CloudFormation stack.
        :param resource_name_prefix: Prefix string for all of the resources to be created.
            For example, if your prefix is "MyCoolProject", then the created api keys database
            will have a name of "MyCoolProjectApiKeysDatabase", api keys generator function
            will have a name of "MyCoolProjectApiKeysGeneratorFunction", and so on...
        :param api: Parent API for which we are creating the authorizer.
        :param cache_ttl: The TTL in seconds of cached authorizer results.
            If it equals 0, authorization caching is disabled.
            If it is greater than 0, API Gateway will cache authorizer responses.
            The maximum value is 3600, or 1 hour.
        :param authorization_type: Determine which header parameters will be used for authorization.
        :param custom_api_keys_database: Custom DynamoDb table to store your api keys and secrets.
        """
        self.api_keys_database = custom_api_keys_database or ApiKeysDatabase(
            scope=scope,
            table_name=f'{resource_name_prefix}ApiKeysDatabase'
        )

        authorizer_layer = AuthorizerLayer(scope)

        base_kwargs = dict(
            scope=scope,
            api_keys_database=self.api_keys_database,
            authorizer_layer=authorizer_layer
        )

        # Authorizes requests.
        self.authorizer_function = AuthorizerFunction(
            **base_kwargs,
            name=f'{resource_name_prefix}ApiKeysAuthorizerFunction',
            parent_api=api,
        )

        # Deletes api keys.
        self.deleter_function = DeleterFunction(
            **base_kwargs,
            name=f'{resource_name_prefix}ApiKeysDeleterFunction',
        )

        # Checks whether api keys exist.
        self.exists_function = ExistsFunction(
            **base_kwargs,
            name=f'{resource_name_prefix}ApiKeysExistsFunction',
        )

        # Generates api keys.
        self.generator_function = GeneratorFunction(
            **base_kwargs,
            name=f'{resource_name_prefix}ApiKeysGeneratorFunction',
        )

        # Validates api keys.
        self.validator_function = ValidatorFunction(
            **base_kwargs,
            name=f'{resource_name_prefix}ApiKeysValidatorFunction',
        )

        # Constructed by reading this documentation:
        # https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-authorizer.html
        super().__init__(
            scope=scope,
            id='ApiKeysCustomAuthorizer',
            name=f'{resource_name_prefix}ApiKeysCustomAuthorizer',
            api_id=api.ref,
            authorizer_payload_format_version='2.0',
            authorizer_result_ttl_in_seconds=cache_ttl,
            authorizer_type='REQUEST',
            authorizer_uri=(
                f'arn:aws:apigateway:{scope.region}:'
                f'lambda:path/2015-03-31/functions/arn:'
                f'aws:lambda:{scope.region}:{scope.account}:'
                f'function:{self.authorizer_function.function_name}/invocations'
            ),
            identity_source=authorization_type.get_authorization_config()
        )

    @property
    def authorization_type(self) -> str:
        """
        Property for authorization type when used with API Gateway service. Read more here:
        https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-apigatewayv2-route.html#cfn-apigatewayv2-route-authorizationtype

        :return: Authorization type string.
        """
        return 'CUSTOM'

from abc import ABC

from aws_cdk.aws_dynamodb import Attribute, Table, BillingMode, AttributeType, TableEncryption
from aws_cdk.core import Stack, RemovalPolicy


class ApiKeysDatabase(Table, ABC):
    def __init__(self, scope: Stack, table_name: str) -> None:
        self.__scope = scope
        self.__table_name = table_name

        super().__init__(
            scope=scope,
            id='ApiKeysDatabase',
            table_name=table_name,
            partition_key=Attribute(name='ApiKey', type=AttributeType.STRING),
            removal_policy=RemovalPolicy.DESTROY,
            point_in_time_recovery=True,
            billing_mode=BillingMode.PAY_PER_REQUEST,
            encryption=TableEncryption.DEFAULT,
        )

    @property
    def table_name(self) -> str:
        """
        Table name property.

        Overrides original parent method. Calling this method will not create a dependency to this resource.

        :return: Table name.
        """
        return self.__table_name

    @property
    def table_arn(self) -> str:
        """
        Table ARN property.

        Overrides original parent method. Calling this method will not create a dependency to this resource.

        :return: Table ARN.
        """
        return f'arn:aws:dynamodb:{self.__scope.region}:{self.__scope.account}:table/{self.__table_name}'

    @property
    def region(self) -> str:
        return self.__scope.region

# -*- coding: utf-8 -*-
from typing import Any
import logging
from matos_aws_provider.lib import factory
from matos_aws_provider.lib.base_provider import BaseProvider

logger = logging.getLogger(__name__)


class AwsIAM(BaseProvider):
    """AWS iam plugin"""
    def __init__(
        self,
        resource: dict,
        **kwargs,
    ) -> None:
        """Constructor method"""
        super().__init__(**kwargs, client_type="iam")

    def get_inventory(self) -> Any:
        """Get inventory asset"""
        return None

    def get_resources(self) -> Any:

        """
        Fetches instance details.

        Args:
        instance_id (str): Ec2 instance id.
        return: dictionary object.
        """
        pwd_policy = None
        try:
            pwd_policy = self.conn.get_account_password_policy().get("PasswordPolicy")
        except Exception as ex:
            logger.error(f"{ex}==== password policy fetch error")
        user_data = {
            "type": "iam",
        }
        if pwd_policy:
            user_data["PasswordPolicy"] = pwd_policy
        return user_data


def register() -> None:
    """Register plugin"""
    factory.register("iam", AwsIAM)

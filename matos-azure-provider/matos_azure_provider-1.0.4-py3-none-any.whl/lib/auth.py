# -*- coding: utf-8 -*-
import os
import json
import logging
from azure.identity import ClientSecretCredential
from matos_azure_provider.config import AZURE_CLIENT_MANAGER


logger = logging.getLogger(__name__)


class Connection:
    """
    Connection authen class
    """
    def __init__(self,
                 **kwargs) -> None:

        svc_account_filename = "azure_account.json"
        azure_svc_account_path = os.getenv("AZURE_SVC_ACCOUNT_PATH", "credentials")
        self._azure_svc_account_file = os.path.join(azure_svc_account_path, svc_account_filename)
        try:
            with open(self._azure_svc_account_file, encoding="utf-8") as file_handle:
                azure_credentials = json.load(file_handle)
        except Exception as ex:
            AZURE_CRED_EXCEPTION = "Not found account service json for Azure - credentials/azure_account.json"
            logger.error(ex)
            raise Exception(AZURE_CRED_EXCEPTION) from ex

        self.tenant_id = azure_credentials.get("tenantId", "")
        self.client_id = azure_credentials.get("clientId", "")
        self.client_secret = azure_credentials.get("clientSecret", "")
        self.subscription_id = azure_credentials.get("subscription_id", "")
        self._credential = None

    def client(self, service_name: str):
        """Get client method

        Args:
            service_name (str): service type

        Returns:
            Object: Client object
        """
        client_class = AZURE_CLIENT_MANAGER.get(service_name, None)
        return client_class(self.credential, self.subscription_id) if client_class else None

    @property
    def credential(self):
        """credential property

        Returns:
            Object: Azure credential object
        """
        if not self._credential:
            self._credential = ClientSecretCredential(
                client_id=self.client_id,
                client_secret=self.client_secret,
                tenant_id=self.tenant_id)
        return self._credential

    def scrub(self, x):
        """scrub method
        """
        org = x.as_dict()
        backup = vars(x)
        for k in backup:
            if backup[k] is None:
                backup[k] = 'None'
            elif k in org.keys():
                backup[k] = org[k]
        return backup

from __future__ import annotations

import dotenv
import os
import logging
import time
from datetime import datetime as datetime
import sys

from typing import Dict, Optional
from msal import ConfidentialClientApplication


class AzureADTokenSetter:
    def __init__(self, tenant, client_id, client_secret, var_prefix=None, token_expiration_min=60) -> None:
        self._tenant: str = tenant
        self._client_id: str = client_id
        self.__client_secret: str = client_secret
        self._token: Optional[Dict[str, str]] = None
        self._app: Optional[ConfidentialClientApplication] = None
        self.ready: bool = False
        self.var_prefix: Optional[str] = var_prefix
        self._error: Optional[str] = None
        self._token_expiration_min: int = token_expiration_min
        self._create_client()

    def _create_client(self):
        try:
            temp_client = ConfidentialClientApplication(self._client_id, self.__client_secret,
                                                        authority=f'https://login.microsoftonline.com/{self._tenant}')
            self._app = temp_client
            self.ready = True
        except Exception as e:
            logging.error(e)
            self._error = str(e)

    def _get_token_client_secret(self) -> None:
        if self.ready:
            result: Dict[str, str] = self._app.acquire_token_for_client(scopes=['https://graph.microsoft.com/.default'])
            try:
                _ = result['access_token']
            except KeyError:
                logging.error("Token was not pulled because of an Error")
                logging.error(result['error'])
                logging.error(result['error_description'])
                self.ready = False
                self._error = result['error']
                return
            self._token = result
        else:
            logging.error('Client not ready, probably credentials error. Recreate client')

    def _set_token_env_var(self) -> None:
        if self._token is not None:
            try:
                if self.var_prefix is not None:
                    os.environ[f'{self.var_prefix}_TOKEN'] = self._token['access_token']
                    os.environ[f'{self.var_prefix}_TOKEN_TYPE'] = self._token['token_type']
                    os.environ[f'{self.var_prefix}_TOKEN_TIME_UTC'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
                else:
                    os.environ['TOKEN'] = self._token['access_token']
                    os.environ['TOKEN_TYPE'] = self._token['token_type']
                    os.environ['TOKEN_TIME_UTC'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

            except KeyError as e:
                logging.error("Token not set because it was empty")
                self._error = "KeyError: " + str(e)
                logging.error(self._error)
                return

    def do_magic_trick(self) -> None:
        self._get_token_client_secret()
        try:
            expiration: int = int(self._token['expires_in'])
            if expiration < self._token_expiration_min:
                logging.info("Expiration less than 60 seconds, waiting to get new token")
                time.sleep(self._token_expiration_min)
                self._get_token_client_secret()
        except KeyError:
            logging.error("Token was not pulled because of an Error")
            logging.error(self._token['error'])
            self._error = self._token['error']
            return
        self._set_token_env_var()

    @property
    def token(self) -> Dict[str, str]:
        return self._token


def main(service: str) -> None:
    dotenv.load_dotenv()

    TENANT = os.getenv('TENANT_ID')
    CLIENT_ID = os.getenv('CLIENT_ID')
    CLIENT_SECRET = os.getenv('CLIENT_SECRET')

    client: AzureADTokenSetter = AzureADTokenSetter(TENANT, CLIENT_ID, CLIENT_SECRET, service)
    client.do_magic_trick()


if __name__ == '__main__':
    service_prefix = sys.argv[1] if len(sys.argv) > 1 else None
    main(service_prefix)

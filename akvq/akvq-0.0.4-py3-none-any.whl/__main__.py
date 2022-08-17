import os
import subprocess
from pathlib import Path

from azure.core.exceptions import ClientAuthenticationError
from azure.identity import (
    ChainedTokenCredential,
    DeviceCodeCredential,
    InteractiveBrowserCredential,
)
from azure.keyvault.secrets import SecretClient

from . import logger

__doc__ = """

get all secrets and only set ENV on keys that start with "akvq-"
use alwyas UPPERCASE for ENV
SWAP dash to underscores, akv only allow (link to spec)

See :manpage:`bash#name`

akvq-HASS -> HASS (as env)
hello -> (skip)
akvq-DEMO-VAR -> DEMO_VAR (as env)

For now I am skipping to implemt auth cache because we are saveing it to disk
https://github.com/Azure/azure-sdk-for-python/issues/11134

source ~/.akvq.sh
Follow for bash: https://stackoverflow.com/q/10735574

Uess the same as for ssh keys

:doc:`azure.keyvault.secrets`

:doc:`azure-keyvault-secrets:index`
"""

# start main logger to get all settings
log = logger.config("akvq")


def get_secrets() -> dict:
    """Get all AKVQ secrets from AKV, Expects secret_client"""
    log.critical("HELLOOOO")


def vault_uri() -> str:
    """
    Will check in order and return on match:

    - ENV
    - git config akvq.url

    Returns:
        str: url of azure key vault

    """
    uri = os.environ.get("AKVQ_VAULT_URI")
    if uri:
        log.debug("Got from ENV")

    if not uri:
        try:
            uri = (
                subprocess.check_output(["git", "config", "akvq.uri"]).decode().strip()
            )
            log.debug("Got from git config")
        except subprocess.CalledProcessError as exit_code:
            log.debug(exit_code)

    return uri


def main() -> int:
    """
    .. todo::

        - save secrets to file
        - clear file
        - add config list like poetry
        - support to add to vault
        - auto find vault based on tag
        - add support for windows

    """
    akvq_vault_uri = vault_uri()
    if not akvq_vault_uri:
        log.critical("Missing vault uri")
        return 1

    interactive_credential = InteractiveBrowserCredential()
    device_credential = DeviceCodeCredential()

    print(
        """A web browser has been opened at https://login.microsoftonline.com/organizations/oauth2/v2.0/authorize.
Please continue the login in the web browser.

If no web browser is available or if the web browser fails to open,
use the device code login."""
    )
    # https://azuresdkdocs.blob.core.windows.net/$web/python/azure-identity/latest/index.html#define-a-custom-authentication-flow-with-chainedtokencredential
    credential_chain = ChainedTokenCredential(interactive_credential, device_credential)

    secret_client = SecretClient(
        vault_url=vault_uri(), credential=credential_chain, logging_enable=True
    )

    aprefix = "akvq-"
    secrets = []
    secret_properties = secret_client.list_properties_of_secrets()
    for secret_property in secret_properties:
        # the list doesn't include values or versions of the secrets
        if secret_property.name.startswith(aprefix):
            secrets.append(secret_property.name)

    akfilename = Path.home() / ".akvq.env"
    print("Login successful")

    with open(akfilename, "w") as akfile:
        # Will override oldfile
        for secret in secrets:
            real_secret_name = secret.split(aprefix)[1]

            # AKV names are only allowed to contain alphanumeric characters and dashes
            # ENV names don't allow dash so a swap works good
            real_secret_name = real_secret_name.replace("-", "_")

            # log.info(f"adding: {real_secret_name}")
            print(f"adding: {real_secret_name}")
            secret_value = secret_client.get_secret(secret).value

            akfile.write(f"export {real_secret_name}={secret_value}\n")

    print("You might need to restart your terminal to source the new ENV")


if __name__ == "__main__":
    main()

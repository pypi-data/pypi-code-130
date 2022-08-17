"""Imports"""
import json
from logging import exception
import boto3
import hvac
from logging import Logger
from typing import NoReturn

vault_cred_json = dict()


class VaultCredentialFetcher(object):
    """
    This Class helps connecting with vault application
    """
    # reads config files from path
    def __init__(self, project_path: str, logger: Logger, environment: str, vault_region: str, vault_role_id: str,
                 display_vault_info: bool = False, vault_config_path: str = "") -> NoReturn:
        """

        :param project_path: Determines the path of project set for execution
        :param logger: determins the logger object to be consumed
        :param environment: environment in which application is deployed
        :param vault_region: Region in which vault related information is present
        :param vault_role_id: role id value for each env in which application is executed
        :param display_vault_info: If true displays valut related info on cloudwatch console
        :param vault_config_path: relative path from src where vault config file is stored
        """
        global vault_cred_json
        self.logger = logger
        self.project_path = project_path
        self.vault_region = vault_region
        self.vault_role = vault_role_id
        self.vault_config_path = vault_config_path
        v_config = self.__load_json_file()
        vault_paths = dict(v_config['vault_paths'])
        self.vault_app_secret_path = v_config['vault_app_secret_path']
        self.vault_db_secret_path = v_config['vault_db_secret_path']
        self.vault_pg_host_secret_path = v_config['vault_pg_host_secret_path']
        self.vault_crm_host_secret_path = vault_paths[environment]['vault_crm_host_secret_path']
        self.vault_baw_host_secret_path = vault_paths[environment]['vault_baw_host_secret_path']
        self.vault_azure_host_secret_path = vault_paths[environment]['vault_azure_host_secret_path']
        self.role_id = vault_paths[environment]['role_id']
        self.hostname = vault_paths[environment]['host']
        self.display_vault_info = display_vault_info

    def __load_json_file(self):
        """
        This Function loads the config json file from the path specified
        :return: Config file after being loaded in memory
        """
        try:
            with open(
                self.project_path + self.vault_config_path
            ) as json_data_file:
                v_config = json.load(json_data_file)
        except Exception:
            self.logger.error(f"Exception raised while loading Json File")
            self.logger.error(str("No such file or directory at path: 'vault_config.json'"))
            self.logger.error("Vault path is : " + self.vault_config_path)
            raise FileNotFoundError
        else:
            return v_config

    def get_vault_cred(self):
        """
        :param self
        :return: Vault creds that can be used directly while reading from AWS
        """
        try:
            if len(vault_cred_json) <= 0:
                hostname = "https://" + self.hostname
                vault_client = hvac.Client(url=hostname)

                self.logger.info("Role id : " + self.role_id)
                self.logger.info("Hostname : " + hostname)

                self.logger.debug('Starting to create Boto3 session')
                session = boto3.Session()
                self.logger.info('Boto3 Session Created')

                self.logger.debug('Starting to fetch Session Credentials')
                session_credentials = session.get_credentials()
                self.logger.info('Fetched Session Credentials')

                # For deploying app using IAM Permissions
                vault_client.auth_aws_iam(session_credentials.access_key, session_credentials.secret_key,
                                          session_credentials.token,
                                          header_value=self.hostname,
                                          role=self.vault_role, region=self.vault_region, use_token=True)

                # Creating vault cred after reading from vault
                vault_cred_json["app"] = vault_client.read(self.vault_app_secret_path)
                vault_cred_json["db"] = vault_client.read(self.vault_db_secret_path)
                vault_cred_json["pg_host"] = vault_client.read(self.vault_pg_host_secret_path)
                vault_cred_json["baw_host"] = vault_client.read(self.vault_baw_host_secret_path)
                vault_cred_json["azure_host"] = vault_client.read(self.vault_azure_host_secret_path)
                vault_cred_json["crm_host"] = vault_client.read(self.vault_crm_host_secret_path)
            else:
                self.logger.warning("Vault_config : vault cred json already exists")

        except exception as e:
            if e.code == -1003:
                self.logger.error("Too many request")
            else:
                self.logger.error('------------- Exception, can not connect with vault --------------------')
                self.logger.error(str(e))
                return e
        else:
            self.logger.info("---------------- Vault_config : vault cred json created -------------")
            if self.display_vault_info:
                self.logger.info(vault_cred_json)
            return vault_cred_json

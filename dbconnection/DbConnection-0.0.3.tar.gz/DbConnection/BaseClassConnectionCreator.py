"""Import statements"""
import os
import json


class BaseClassConnectionCreator(object):
    """
    This class creates a SQLDB session and retuns the connection string for the datatype passed
    """
    def __init__(self, project_path, logger, environment):

        """

        :param project_path:
        :param logger:
        :param environment:
        """
        self.env = environment
        self.logger = logger
        self.project_path = project_path

    def _get_connection_string(self, con_name, vault_cred, schema=False, keys_mapper_dict=None, **kwargs):
        """
        :param schema:
        :param self:
        :param con_name:
        :param vault_cred:
        :return:
        """
        raise NotImplementedError

    def get_session_conn_string(self, test='local', co_name=None, schema=False, vault_cred_dict=None, local_creds_json_file_with_path=None, connection_keys_mapper_file_with_path=None, **kwargs):
        """
        :param schema:
        :param test:
        :param co_name:
        :return:
        """
        keys_mapper_file_path = os.path.join(self.project_path, connection_keys_mapper_file_with_path)
        with open(keys_mapper_file_path) as json_data_file:
            keys_mapper_dict = json.load(json_data_file)

        if test == 'local':
            self.logger.info("App Executed locally")
            #db_cc_path = os.path.join(self.project_path, 'src', 'app_configs', 'db_con_config.json')
            db_cc_path = os.path.join(self.project_path, local_creds_json_file_with_path)
            with open(db_cc_path) as json_data_file:
                vault_cred = json.load(json_data_file)
                vault_cred = vault_cred[self.env]

        elif test == 'deploy':
            self.logger.info("App Executed on AWS")
            vault_cred = vault_cred_dict
        else:
            raise ConnectionError("wrong parameter passed")

        connection_string = self._get_connection_string(co_name, vault_cred, schema, keys_mapper_dict, **kwargs)
        if connection_string != "" or connection_string is None:
            return connection_string
        else:
            raise ConnectionError("Error in Connection String")

    def create_session(self, connection_string):
        """

        :param connection_string:
        :return:
        """
        raise NotImplementedError

    def create_eng(self, connection_string):
        """
        :param connection_string:
        :return: Engine
        """
        raise NotImplementedError



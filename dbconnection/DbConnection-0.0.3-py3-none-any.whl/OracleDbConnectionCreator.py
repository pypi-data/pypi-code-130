"""Import statements"""
import os
import json
import oracledb
import urllib
from DbConnection.BaseClassConnectionCreator import BaseClassConnectionCreator

oracledb.init_oracle_client(lib_dir=os.environ.get('ORACLE_HOME'))


class OracleDbConnectionCreator(BaseClassConnectionCreator):
    """
    This class creates a SQLDB session and retuns the connection string for the datatype passed
    """

    def __init__(self, project_path, logger, environment):

        """

        :param project_path:
        :param logger:
        :param environment:
        """
        super().__init__(project_path, logger, environment)

    def _get_connection_string(self, con_name, vault_cred, schema=False, keys_mapper_dict=None, **kwargs):
        """
        :param schema:
        :param self:
        :param con_name:
        :param vault_cred:
        :return:
        """
        if con_name == 'CRM':
            try:
                crm_pwd = str(vault_cred[keys_mapper_dict['CRM_connection']['password'][0]]['data'][keys_mapper_dict['CRM_connection']['password'][1]])#crm_conn['crm_password']
                crm_user = str(vault_cred[keys_mapper_dict['CRM_connection']['user_id'][0]]['data'][keys_mapper_dict['CRM_connection']['user_id'][1]])#crm_conn['crm_username']
                crm_hostname = str(vault_cred[keys_mapper_dict['CRM_connection']['hostname'][0]]['data'][keys_mapper_dict['CRM_connection']['hostname'][1]])#crm_conn['url']
                crm_port = str(vault_cred[keys_mapper_dict['CRM_connection']['port'][0]]['data'][keys_mapper_dict['CRM_connection']['port'][1]])#crm_conn['port']
                crm_service = str(vault_cred[keys_mapper_dict['CRM_connection']['servicename'][0]]['data'][keys_mapper_dict['CRM_connection']['servicename'][1]])#crm_conn['service']

                connection_string = f'{crm_user}/{crm_pwd}@{crm_hostname}:{crm_port}/{crm_service}'
                if connection_string != "":
                    return connection_string
                else:
                    self.logger.warning('CRM Empty connection string passed')
            except Exception as err:
                self.logger.exception(err)
                raise err
            else:
                return connection_string
        else:
            raise "incorrect value passed for argument con_name. Only CRM is allowed as parameter for oracledb library"

    def create_session(self, connection_string):
        """

        :param connection_string:
        :return:
        """
        session_created = oracledb.connect(connection_string).cursor()
        self.logger.info("Session object : " + str(session_created))
        return session_created




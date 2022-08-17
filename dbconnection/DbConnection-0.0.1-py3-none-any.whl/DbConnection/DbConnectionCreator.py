"""Import statements"""
import os
import json
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker
import urllib
from sqlalchemy.pool import NullPool


class DbConnectionCreator(object):
    """
    This class creates a SQLDB session and retuns the connection string for the datatype passed
    """
    session = None

    def __init__(self, project_path, logger, environment):

        """

        :param project_path:
        :param logger:
        :param environment:
        """
        self.env = environment
        self.logger = logger
        self.project_path = project_path

        """ Constructor"""


    def _get_connection_string(self, con_name, vault_cred, schema=False, keys_mapper_dict=None, **kwargs):
        """
        :param schema:
        :param self:
        :param con_name:
        :param vault_cred:
        :return:
        """
        if con_name == 'Postgres':

            try:
                # initialize connection
                #postgres_conn = postgres_index.postgres_index(self.env, vault_cred)
                # initialize connection string
                batch_pwd = str(vault_cred[keys_mapper_dict['Postgres_connection']['password'][0]]['data'][keys_mapper_dict['Postgres_connection']['password'][1]])#str(postgres_conn['postgres_password'])
                batch_user = str(vault_cred[keys_mapper_dict['Postgres_connection']['user_id'][0]]['data'][keys_mapper_dict['Postgres_connection']['user_id'][1]])#str(postgres_conn['postgres_password'])
                batch_hostname = str(vault_cred[keys_mapper_dict['Postgres_connection']['hostname'][0]]['data'][keys_mapper_dict['Postgres_connection']['hostname'][1]])#str(postgres_conn['postgres_password'])
                postgres_port = str(vault_cred[keys_mapper_dict['Postgres_connection']['port'][0]]['data'][keys_mapper_dict['Postgres_connection']['port'][1]])#str(postgres_conn['postgres_password'])
                postgres_service = str(vault_cred[keys_mapper_dict['Postgres_connection']['servicename'][0]]['data'][keys_mapper_dict['Postgres_connection']['servicename'][1]])#str(postgres_conn['postgres_password'])

                if not schema:
                    connection_string = f'postgresql://{batch_user}:{batch_pwd}@{batch_hostname}:{postgres_port}' \
                                        f'/{postgres_service}'
                else:

                    if len(kwargs) != 1:
                        self.logger.error('No. of arguments can not be greater than 1')
                        err = 'number of arguements should be one'
                        raise err

                    else:
                        schema_name = str(list(kwargs.values())[0])
                        connection_string = f'postgresql://{batch_user}:{batch_pwd}@{batch_hostname}:{postgres_port}' \
                                            f'/{postgres_service}?options=-csearch_path%3D{schema_name}'
                self.logger.info("Postgres Connection string used : " + str(connection_string))
                self.logger.warning('Postgres Empty connection string passed')

            except Exception as err:
                self.logger.exception(err)
                raise err

            else:
                return connection_string

        elif con_name == 'CRM':
            try:
                dialect = 'oracle'
                sql_driver = 'cx_oracle'
                crm_pwd = str(vault_cred[keys_mapper_dict['CRM_connection']['password'][0]]['data'][keys_mapper_dict['CRM_connection']['password'][1]])#crm_conn['crm_password']
                crm_user = str(vault_cred[keys_mapper_dict['CRM_connection']['user_id'][0]]['data'][keys_mapper_dict['CRM_connection']['user_id'][1]])#crm_conn['crm_username']
                crm_hostname = str(vault_cred[keys_mapper_dict['CRM_connection']['hostname'][0]]['data'][keys_mapper_dict['CRM_connection']['hostname'][1]])#crm_conn['url']
                crm_port = str(vault_cred[keys_mapper_dict['CRM_connection']['port'][0]]['data'][keys_mapper_dict['CRM_connection']['port'][1]])#crm_conn['port']
                crm_service = str(vault_cred[keys_mapper_dict['CRM_connection']['servicename'][0]]['data'][keys_mapper_dict['CRM_connection']['servicename'][1]])#crm_conn['service']

                connection_string = f"{dialect}+{sql_driver}://{crm_user}:{crm_pwd}@{crm_hostname}:{crm_port}" \
                                    f"/?service_name={crm_service}"
                if connection_string != "":
                    return connection_string
                else:
                    self.logger.warning('CRM Empty connection string passed')
            except Exception as err:
                self.logger.exception(err)
                raise err
            else:
                return connection_string

        elif con_name == 'AZURE':
            try:
                #azure_conn = azure_index.azure_index(self.env, vault_cred)
                azure_password = str(vault_cred[keys_mapper_dict['Azure_connection']['password'][0]]['data'][keys_mapper_dict['Azure_connection']['password'][1]])#azure_conn['azure_password']
                azure_uid = str(vault_cred[keys_mapper_dict['Azure_connection']['user_id'][0]]['data'][keys_mapper_dict['Azure_connection']['user_id'][1]])  # azure_conn['azure_uid']
                azure_database = str(vault_cred[keys_mapper_dict['Azure_connection']['servicename'][0]]['data'][keys_mapper_dict['Azure_connection']['servicename'][1]])#azure_conn['azure_database']
                azure_server = str(vault_cred[keys_mapper_dict['Azure_connection']['hostname'][0]]['data'][keys_mapper_dict['Azure_connection']['hostname'][1]])#azure_conn['azure_server']

                params = urllib.parse.quote_plus(r'Driver='+"{ODBC Driver 17 for SQL Server}"+';'
                                                 'Server='+azure_server+';'
                                                 'Database='+azure_database+';'
                                                 'UID='+azure_uid+';'
                                                 'PWD='+azure_password+';')

                connection_string = 'mssql+pyodbc:///?autocommit=true&odbc_connect={}'.format(params)
                if connection_string != "":
                    return connection_string
                else:
                    self.logger.warning('AZURE Empty connection string passed')
            except Exception as err:
                self.logger.exception(err)
                raise err
            else:
                return connection_string
        elif con_name == 'APP':
            try:
                app_creds = app_index.app_index(self.env, vault_cred)
                return app_creds
            except Exception as e:
                raise e

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
        engine = create_engine(connection_string, echo=False, poolclass=NullPool)
        session_maker = sessionmaker(bind=engine)
        DbConnectionCreator.session = session_maker()
        self.logger.info("Session object : " + str(DbConnectionCreator.session))
        return DbConnectionCreator.session

    def create_eng(self, connection_string):
        """
        :param connection_string:
        :return: Engine
        """
        engine = create_engine(connection_string, echo=False)
        self.logger.info('Engine Created')
        return engine



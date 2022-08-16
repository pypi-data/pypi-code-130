# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2020, 2021
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import ibm_db
import json
import logging
import time

from abc import ABC, abstractmethod
from ibm_wos_utils.joblib.utils import constants
from ibm_wos_utils.joblib.utils.db2_utils import DB2Utils
from ibm_wos_utils.joblib.utils.param_utils import get

logger = logging.getLogger(__name__)

class Client(ABC):

    """
    Abstract class for all Spark job related actions
    """

    @abstractmethod
    def run_job(self, job_name, job_class, job_args, data_file_list=None, background=True, timeout=constants.SYNC_JOB_MAX_WAIT_TIME):
        '''
        - Upload data_file_list
        - Push entry job if it is not already pushed
        - compose job payload
        - run the job (Jobs will be available in wos_utils package
        '''
        pass

    @abstractmethod
    def get_job_status(self, job_id):
        pass

    @abstractmethod
    def get_file(self, file_path):
        pass

    @abstractmethod
    def get_exception(self, output_file_path):
        pass

    @abstractmethod
    def get_job_logs(self, job_id):
        pass

    @abstractmethod
    def delete_job_artifacts(self, job_id):
        pass

    @abstractmethod
    def kill_job(self, job_id):
        pass

    def __upload_job_artifacts(self, files_list, target_folder, overwrite=True):
        pass

    @abstractmethod
    def download_directory(self, directory_path):
        pass
    
    @abstractmethod
    def delete_directory(self, directory_path):
        pass

    @abstractmethod
    def upload_directory(self, directory_path, archive_directory_content):
        pass

    def create_table_job_post_processing_steps(self, table_info_json):
        db2 = None
        try:

            table_info_details = json.loads(get(table_info_json, "table_info_details"))
            jdbc_connection_details = {}

            if table_info_details:
                jdbc_connection_details = get(table_info_json, "jdbc_connection_details")

            db2 = self.__get_db2_connection(jdbc_connection_details)
            self.__alter_db2_table_with_partition_index_primary_columns(db2, table_info_details)

            logger.info("Completed the post processing steps for create table job.")

        except Exception as e:
            logger.exception("An error occurred while updating partition column {}".format(str(e)))
            pass

        finally:
            if db2:
                db2.delete_certificate_file()
                db2.close_connection()

    def __get_db2_connection(self, jdbc_connection_details):

        if not jdbc_connection_details:
            raise Exception("jdbc connection details are not set in the partitions json.")

        certificate = get(jdbc_connection_details, "certificate")
        username = get(jdbc_connection_details, "user")
        password = get(jdbc_connection_details, "password")
        use_ssl = True if get(jdbc_connection_details, "sslConnection") else False
        jdbc_url = get(jdbc_connection_details, "url").split("//")
        host = jdbc_url[1].split(":")
        host_name = host[0]
        port = host[1].split("/")[0]
        database_name = host[1].split("/")[1]

        db2 = DB2Utils(database_name, host_name, port, username, password, use_ssl, certificate)
        db2.get_connection()
        return db2

    def __alter_db2_table_with_partition_index_primary_columns(self, db2, table_info_details):
        try:
            for table_info in table_info_details:
                schema_name = get(table_info, "schema_name")
                table_name = get(table_info, "table_name")
                
                partition_column_name = get(table_info, "partition_column")
                primary_key = get(table_info, "primary_key")
                index_column = get(table_info, "index_column")
                
                additional_index_columns = get(table_info, "additional_index_columns")
                additional_primary_keys = get(table_info, "additional_primary_keys")

                queries = []
                if partition_column_name:
                    queries.append(db2.generate_partition_column_query(
                        schema_name=schema_name,
                        table_name=table_name,
                        partition_column=partition_column_name))

                if primary_key:
                    queries.append(db2.generate_primary_keys_query(
                        schema_name=schema_name,
                        table_name=table_name,
                        primary_keys=[primary_key]))
                
                if additional_primary_keys:
                    queries.append(db2.generate_primary_keys_query(
                        schema_name=schema_name,
                        table_name=table_name,
                        primary_keys=additional_primary_keys))

                if index_column:
                    queries.append(db2.generate_index_columns_query(
                        schema_name=schema_name,
                        table_name=table_name,
                        index_columns=["{} DESC".format(index_column)]))

                if additional_index_columns:
                    queries.append(db2.generate_index_columns_query(
                        schema_name=schema_name,
                        table_name=table_name,
                        index_columns=additional_index_columns))

                logger.info("Alter table queries {}".format(queries))
        
                for query in queries:
                    try:
                        ibm_db.exec_immediate(db2.connection, query) 
                        time.sleep(1)
                        logger.info("Executed the alter table query successfully {}".format(query))
                    except Exception as e:
                        logger.warn("Query {} failed with exception: {}".format(query, str(e)))
                        pass

        except Exception as e:
            raise e


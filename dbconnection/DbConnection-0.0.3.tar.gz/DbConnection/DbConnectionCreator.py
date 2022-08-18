"""Import statements"""
from DbConnection.SqlAlchemyConnectionCreator import SqlAlchemyConnectionCreator
from DbConnection.OracleDbConnectionCreator import OracleDbConnectionCreator

class DbConnectionCreator(object):
    """
    This class creates a SQLDB session and retuns the connection string for the datatype passed
    """

    def __init__(self, project_path, logger, environment, db_library='sqlalchemy'):

        """

        :param project_path:
        :param logger:
        :param environment:
        """
        self.env = environment
        self.logger = logger
        self.project_path = project_path
        self.db_library = db_library


    def get_database_connection_object(self):
        if self.db_library=='sqlalchemy':
            db_conn_obj = SqlAlchemyConnectionCreator(self.project_path, self.logger, self.env)
        elif self.db_library=='oracledb':
            db_conn_obj = OracleDbConnectionCreator(self.project_path, self.logger, self.env)
        else:
            raise "incorrect argument passed. database library argument accepts only [sqlalchemy,oracledb]"

        return db_conn_obj
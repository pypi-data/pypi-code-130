import mysql.connector as sql

class db_connector:
    """
    Instantiate a DB connector.
    :param db_type: Database type (e.g. mysql)
    :type db_type: string

    :param db_host: Database host 
    :type db_host: string

    :param db_port: Database port
    :type db_port: string

    :param user: Username
    :type user: string

    :param password: Password
    :type password: string
    """
    
    def __init__(self, db_type, host, port, user, password):
        self.db_type = db_type
        self.host = host
        self.port = port
        self.user = user
        self.password = password

    
    def load_csv_local(
        self,
        db_name, 
        table_name, 
        file_name,
        write_disposition,
        delimiter=',', 
        ignore_rows=1,
    ):
        """
        Load a local CSV file into a table
        
        :param db_name: Database name where the CSV will be loaded
        :type db_name: string
        
        :param table_name: Table name where the CSV will be loaded
        :type table_name: string
        
        :param file_name: CSV file name
        :type file_name: string
        
        :param delimiter: CSV delimiter character
        :type delimiter: string

        :param ignore_rows: Number of rows that will be ignored from the top
        :type ignore_rows: int

        :param write_disposition: Write method to add data into table (WRITE_TRUNCATE, WRITE_APPEND)
        :type ignore_rows: str

        :return: The result of function
        :type: string
        """
        result = ''
        if self.db_type.lower() == 'mysql':
            db_connection = sql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                autocommit=True,
                allow_local_infile=True
            )
            db_cursor = db_connection.cursor()
            query = """SET GLOBAL local_infile=1"""
            db_cursor.execute(query)

            if write_disposition == 'WRITE_TRUNCATE':
                query = 'TRUNCATE TABLE {db_name}.{table_name}'.format(db_name=db_name, table_name=table_name)
                db_cursor.execute(query)
                db_connection.commit()

            # load table
            sql_import_table = (""" LOAD DATA LOCAL INFILE '{file_name}' 
                                    INTO TABLE {db_name}.{table_name}
                                    FIELDS TERMINATED BY '{delimiter}' 
                                    LINES TERMINATED BY '\\n'
                                    IGNORE {ignore_rows} ROWS;
            """).format(file_name=file_name, db_name=db_name, table_name=table_name, delimiter=delimiter, ignore_rows=ignore_rows)
            db_cursor.execute(sql_import_table)
            db_connection.commit()
            result = 'OK'
        else:
            result = 'Database is not supported'
        return result


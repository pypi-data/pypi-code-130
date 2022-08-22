import mysql.connector as sql

class mysql_connector:
    """Instantiate a DB connector.
    Args:
        host (str): Database host 
        port (str): Database port
        user (str): Username
        password (str): Password
    """
    
    def __init__(self, host, port, user, password):
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
        Args:
            db_name (str): Database name where the CSV will be loaded
            table_name (str): Table name where the CSV will be loaded
            file_name (str): CSV file name
            delimiter (str): CSV delimiter character
            ignore_rows (str): Number of rows that will be ignored from the top
            write_disposition (str): Write method to add data into table (WRITE_TRUNCATE, WRITE_APPEND)

        Returns:
            result (str): The result of function
        """
        result = ''
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
        return result


import pymysql


# ---------------------------------------------------------------------------------------------------------------------#
#                                       Functions to manipulate MySQL Database                                         #
# ---------------------------------------------------------------------------------------------------------------------#

####--------------------------------------- MySQL Database Functions -----------------------------------------------####


def open_mysql_connection(host, port, username, password, database):
    try:
        db_con = pymysql.connect(host=host, port=port, user=username, passwd=password, db=database,
                                 cursorclass=pymysql.cursors.DictCursor, autocommit=True)
    except Exception:
        print("Error in MySQL connection with " + database + " database.")
    else:
        return db_con


def get_columns_from_dict(source, args_key):
    """Convert a dict of arguments into a string to columns separate by comma. Example: 'column_1, column_2,
    column_3'. """
    str_columns = ""
    data_args = source.get(args_key.replace(' ', '_'))
    if data_args is not None:
        for key, value in enumerate(data_args[0]):
            str_columns += value + ', '
    else:
        message = "No matching results for parameter data = " + args_key + " was found in DataPool."
        raise Exception(message)
    return str_columns[:-2]


def execute_query(db_connection, sql_query):
    connection = db_connection
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql_query)
            result = cursor.fetchall()
            connection.commit()
    finally:
        connection.close()
    return result


def get_entire_result_from_executed_query(host, port, username, password, database, sql_query):
    connection = open_mysql_connection(host, port, username, password, database)
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql_query)
            result = cursor.fetchall()
            connection.commit()
    finally:
        connection.close()
    return result


def execute_query_from_db(host, port, username, password, database, sql_query):
    connection = open_mysql_connection(host, port, username, password, database)
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql_query)
            result = cursor.fetchall()
            connection.commit()
    finally:
        connection.close()
    return result


def select_all_from_table(db_connection, table):
    con = db_connection
    sql_query = "SELECT * FROM " + table
    con.execute(sql_query)
    return con.fetchall()


def close_connection_database(db_connection):
    con = db_connection
    con.close()

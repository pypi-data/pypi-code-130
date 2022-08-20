import psycopg2

# ---------------------------------------------------------------------------------------------------------------------#
#                                       Functions to manipulate Postgre Database                                       #
# ---------------------------------------------------------------------------------------------------------------------#

# -------------------------------------------------- CSV Functions ----------------------------------------------------#

# Update connection string information
host = "test_db.postgres.database.azure.com"
dbname = "test_db"
user = "postgresql_admin@test_db"
password = "password_x"
ssl_mode = "require"


def open_postgresql_connection(host, dbname, user, password, ssl_mode):
    # Construct connection string
    conn_string = "host={0} user={1} dbname={2} password={3} sslmode={4}".format(host, user, dbname, password, ssl_mode)
    conn = psycopg2.connect(conn_string)
    print("Connection established")
    return conn.cursor()


def connection_test():
    cursor = open_postgresql_connection(host, dbname, user, password, ssl_mode)
    # Fetch all rows from table
    cursor.execute("SELECT * FROM table limit 1;")
    print(cursor)
    rows = cursor.fetchall()

    # Print all rows
    for row in rows:
        print("Data row = %s" % (str(row)))
    cursor1 = open_postgresql_connection(host, dbname, user, password, ssl_mode)
    # Fetch all rows from table
    cursor1.execute("SELECT * FROM table limit 1;")
    print(cursor1)
    rows = cursor1.fetchall()
    # Print all rows
    for row in rows:
        print("Data row = %s" % (str(row)))

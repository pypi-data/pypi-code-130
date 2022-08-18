import os
from sqlalchemy import create_engine
from snowflake.sqlalchemy import URL
import yaml
import snowflake.connector as sfc

def close(connection):
    """
    Close connection to snowflake 

    Args:
        connection (connection, optional): sqlalchemy connection object

    Returns:
        None
    """    
    connection.close()
    return None

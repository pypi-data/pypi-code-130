""" SQL utility functions """
import re

TABLE_NAME_REGEX = r"^([\w_]+\.[\w_]+)$"


def is_qualified_table_name(qualified_name):
    """
    Returns True if qualified_name is of the form <database_name>.<table_name>
    and only contain alphabet characters, numbers and _.

    This character set is required by Hive and Spark SQL:
    https://docs.databricks.com/spark/latest/spark-sql/language-manual/sql-ref-identifiers.html
    http://hive.apache.org/javadocs/r3.0.0/api/org/apache/hadoop/hive/metastore/utils/MetaStoreUtils.html#validateName-java.lang.String-org.apache.hadoop.conf.Configuration-
    """
    return re.match(TABLE_NAME_REGEX, qualified_name)

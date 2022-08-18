import logging
from databricks.feature_store.utils.sql import is_qualified_table_name
from pyspark.sql import DataFrame

_logger = logging.getLogger(__name__)


def standardize_checkpoint_location(checkpoint_location):
    if checkpoint_location is None:
        return checkpoint_location
    checkpoint_location = checkpoint_location.strip()
    if checkpoint_location == "":
        checkpoint_location = None
    return checkpoint_location


def check_qualified_name(feature_table_name):
    if not is_qualified_table_name(feature_table_name):
        raise ValueError(
            "Feature table name must have the form <database_name>.<table_name> "
            "and only contain alphabet characters, numbers and _."
        )


def check_dataframe_type(df):
    """
    Check if df is a PySpark DataFrame, otherwise raise an error.
    """
    if not isinstance(df, DataFrame):
        raise ValueError(
            f"Unsupported DataFrame type: {type(df)}. DataFrame must be a PySpark DataFrame."
        )


def check_kwargs_empty(the_kwargs, method_name):
    if len(the_kwargs) != 0:
        raise TypeError(
            f"{method_name}() got unexpected keyword argument(s): {list(the_kwargs.keys())}"
        )

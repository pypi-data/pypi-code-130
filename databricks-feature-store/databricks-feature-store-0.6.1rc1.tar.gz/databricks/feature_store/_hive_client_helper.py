import logging
from databricks.feature_store.utils import validation_utils
from databricks.feature_store.hive_client import HiveClient

_logger = logging.getLogger(__name__)


class HiveClientHelper:
    """
    Helper functions that wrap calls to the hive client with application specific business logic.
    """

    def __init__(self, hive_client: HiveClient):
        self._hive_client = hive_client

    def check_database_exists(self, feature_table_name):
        """
        Check for the existence of a database.

        feature_table_name should have the form <database_name>.<table_name>.
        Check whether database_name is a database in the metastore.
        """
        database_name, _ = feature_table_name.split(".")
        if not self._hive_client.database_exists(database_name):
            raise ValueError(
                f"Database '{database_name}' does not exist in the Hive metastore."
            )

    def check_feature_table_exists_in_hive(self, feature_table_name):
        validation_utils.check_qualified_name(feature_table_name)
        self.check_database_exists(feature_table_name)
        if not self._hive_client.table_exists(feature_table_name):
            raise ValueError(
                f"The feature data table for '{feature_table_name}' could not be found."
            )

""" Module w.r.t. Azure table storage logic."""

import logging
import os
import typing
from dataclasses import dataclass

import pandas as pd
from azure.data.tables import TableClient, TableServiceClient


@dataclass
class WarpzoneTableClient:
    """Dataclass which serve the logic w.r.t. the azure table storage."""

    table_name: str
    partition_keys: typing.List[str]
    row_keys: typing.List[str]
    operation_type: str = "upsert"
    chunk_size: int = 100

    def __post_init__(self):
        self._service: TableServiceClient = self._get_table_service_connection()
        self._table: TableClient = self._get_table_client()

    def _get_table_service_connection(self) -> TableServiceClient:
        """Get service connection."""
        # storage_account_name = os.getenv("STORAGE_ACCOUNT_NAME")

        # service = TableServiceClient(
        #     endpoint=f"https://{storage_account_name}.table.core.windows.net/",
        #     credential=DefaultAzureCredential(),
        # )

        return TableServiceClient.from_connection_string(
            os.getenv("WARPZONE_DATA_CONNECTION_STRING", default="")
        )

    def _get_table_client(self) -> TableClient:
        """Get table client from service connection"""
        return self._service.get_table_client(self.table_name)

    @staticmethod
    def _chunkify(lst: typing.List, n: int) -> typing.List[typing.List]:
        """Split list into list of `n` lists.
        This is requried by the current Azure SDK implementation.

        Args:
            lst (typing.List): Initial list.
            n (int): Number of chunks to make.

        Returns:
            typing.List[typing.List]: List of lists with a given chunk size.
        """
        return [lst[i::n] for i in range(n)]

    @staticmethod
    def operation_count(operations: typing.List[typing.List]) -> int:
        """Count number of operations to make on table storage.

        Args:
            operations (typing.List[typing.List]): List of lists with operations.

        Returns:
            int: Number of operations.
        """
        return sum(len(partition) for partition in operations)

    def create_table_operations(
        self,
        df: pd.DataFrame,
    ) -> typing.List[typing.List]:
        """Convert dataframe into table storage operations-

        Args:
            df (pd.DataFrame): Dataframe of interest.

        Returns:
            typing.List[typing.List]: List of lists with operations for a given
            dataframe.
        """
        datatime_columns = df.select_dtypes(["datetime"]).columns

        for column in datatime_columns:
            df[column] = df[column].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
            df[f"{column}@odata.type"] = "Edm.DateTime"

        df["PartitionKey"] = df[self.partition_keys].agg("_".join, axis=1)
        df["RowKey"] = df[self.row_keys].agg("_".join, axis=1)

        operations = []
        for _, partition_group in df.groupby(self.partition_keys):
            records = partition_group.to_dict("records")
            operation = [(self.operation_type, record) for record in records]
            operations.append(operation)

        return operations

    def execute_table_operations(
        self,
        operations: typing.List[typing.List],
    ) -> None:
        """Perform table storage operations from a operation set.

        Args:
            operations (typing.List[typing.List]): List of lists with operations for a
            given dataframe.
        """
        for partition in operations:
            chunks = self._chunkify(partition, len(partition) // self.chunk_size + 1)
            for chunk in chunks:
                self._table.submit_transaction(chunk)

    def query_table(self, filter_query):
        """Retrieve data from Table Storage"""
        entities = [record for record in self._table.query_entities(filter_query)]
        return entities

    def insert_dataframe(self, df: pd.DataFrame) -> None:
        """Method which insert the dataframe into table storage.

        Args:
            df (pd.DataFrame): Dataframe of interest.
        """
        operations = self.create_table_operations(df)
        n_operations: int = self.operation_count(operations)
        logging.info(f"Operations to submit: {n_operations}")

        self.execute_table_operations(operations)
        logging.info("Operations to completed...")

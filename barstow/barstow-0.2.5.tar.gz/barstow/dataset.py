from pathlib import Path
from typing import List, Optional, Union, Generator

import pandas as pd
import pyarrow as pa
import pyarrow.dataset as ds

from barstow.io import write_dataset

field = pa.field


class Query:
    def __init__(self, dataset: ds.Dataset):
        self._dataset = dataset
        self._columns: Optional[List[str]] = None
        self._filter = None
        self._batch_size = 1_000_000

    def _scan(self) -> ds.Scanner:
        """Return a Scanner object for the current query"""
        return self._dataset.scanner(
            columns=self._columns, filter=self._filter, batch_size=self._batch_size
        )

    def select(self, columns: List[str]) -> "Query":
        """Select specific columns from the dataset"""
        self._columns = columns
        return self

    def where(self, expression: ds.Expression) -> "Query":
        """Filter the dataset, returns the query object.

        Refer to PyArrow documentation for information on creating expressions:
          https://arrow.apache.org/docs/python/generated/pyarrow.dataset.Expression.html
        """
        if self._filter is not None:
            self._filter = self._filter & expression
        else:
            self._filter = expression
        return self

    def batch_size(self, batch_size: int) -> "Query":
        self._batch_size = batch_size
        return self

    def count_rows(self) -> int:
        """Return the number of rows to be returned by the current query"""
        nrows: int = self._scan().count_rows()
        return nrows

    def head(self, n=5) -> pd.DataFrame:
        """Return the first n rows of the dataset"""
        return self._scan().head(n).to_pandas()

    def take(self, indices: List[int]) -> pd.DataFrame:
        """Return specific rows from the dataset"""
        return self._scan().take(indices).to_pandas()

    def to_pandas(self) -> pd.DataFrame:
        """Fetch the data from the dataset and return it as a Pandas DataFrame"""
        return self._scan().to_table().to_pandas()

    def to_batches(self, batch_size=1_000_000) -> Generator[pd.DataFrame, None, None]:
        """Fetch the data from the dataset as batches and return a generator that yields each
        batch as a Pandas DataFrame"""
        self._batch_size = batch_size
        for batch in self._scan().to_batches():
            yield batch.to_pandas()

    def to_dataset(self):
        """Return the query as an in-memory Dataset object"""
        dataset: ds.Dataset = ds.dataset(list(self._scan().to_batches()))
        return Dataset.from_pyarrow(dataset)

    def __repr__(self):
        return "Query(columns={}, filter={})".format(self._columns, self._filter)


class Dataset:
    def __init__(
        self,
        location: Union[str, Path],
        partitioning: Optional[List[str]] = None,
        format: str = "parquet",
        filesystem: Optional[pa.fs.FileSystem] = None,
        batch_size: int = 1_000_000,
    ):
        self._location = location
        self._partitioning = partitioning
        self._format = format
        self._fs = filesystem
        self.batch_size = batch_size

        if self._location:
            self._dataset = ds.dataset(
                self._location,
                format=format,
                filesystem=filesystem,
                partitioning=partitioning,
            )

    @staticmethod
    def from_pyarrow(
        dataset: ds.Dataset,
        partitioning: Optional[List[str]] = None,
        format: str = "parquet",
        filesystem: Optional[pa.fs.FileSystem] = None,
    ) -> "Dataset":
        """Create a Dataset object from a local PyArrow dataset"""
        new_dataset = Dataset(
            location="",
            partitioning=partitioning,
            format=format,
            filesystem=filesystem,
        )

        new_dataset._dataset = dataset

        return new_dataset

    @property
    def location(self) -> Union[str, Path]:
        return self._location

    @property
    def schema(self) -> pa.Schema:
        return self._dataset.schema

    @property
    def nrows(self) -> int:
        nrows: int = self._dataset.count_rows()
        return nrows

    @property
    def dataset(self) -> ds.Dataset:
        return self._dataset

    @property
    def query(self) -> Query:
        """Returns a Query object that can be used to query the dataset"""
        return Query(self._dataset)

    def select(self, columns: List[str]):
        """Select columns from the dataset"""
        return self.query.select(columns)

    def where(self, expression: ds.Expression):
        """Filter the dataset based on an expression"""
        return self.query.where(expression)

    def count_rows(self):
        return self.nrows

    def head(self, n: int = 5) -> pd.DataFrame:
        """Returns the first n rows of the dataset"""
        return self.dataset.head(n).to_pandas()

    def take(self, indices: List[int]):
        """Returns a subset of the dataset based on the given indices"""
        return self.dataset.take(indices).to_pandas()

    def join(
        self,
        other: "Dataset",
        keys: Union[str, List[str]],
        right_keys: Union[str, List[str]] = None,
        join_type="left outer",
        left_suffix: Optional[str] = None,
        right_suffix: Optional[str] = None,
        coalesce_keys=True,
    ):
        """Join two datasets together"""
        return Dataset.from_pyarrow(
            self.dataset.join(
                other.dataset,
                keys,
                right_keys=right_keys,
                join_type=join_type,
                left_suffix=left_suffix,
                right_suffix=right_suffix,
                coalesce_keys=coalesce_keys,
            )
        )

    def cast(self, **kwarg):
        """Cast a field in the dataset to another data type"""
        new_schema = self._dataset.schema

        for field, data_type in kwarg.items():
            idx = new_schema.get_field_index(field)
            new_schema = new_schema.set(idx, pa.field(field, data_type))

        if self._dataset.count_rows() > self.batch_size:
            # Dataset is too big to fit in memory, so we need to get it in batches and cast columns in each batch
            for batch in self._dataset.scanner(batch_size=self.batch_size).to_batches():
                table = pa.Table.from_batches([batch])
                new_table = table.cast(new_schema)

                dataset = ds.dataset(
                    [new_table],
                    schema=new_schema,
                )

                write_dataset(
                    dataset,
                    self.location,
                    new_schema,
                    format=self._format,
                    partitioning=self._partitioning,
                    filesystem=self._fs,
                    batch_size=self.batch_size,
                )
        else:
            table = self._dataset.to_table()
            new_table = table.cast(new_schema)

            dataset = ds.dataset([new_table], schema=new_schema)

            write_dataset(
                dataset,
                self.location,
                new_schema,
                format=self._format,
                partitioning=self._partitioning,
                filesystem=self._fs,
                batch_size=self.batch_size,
            )

    def write(self, location: Optional[Union[str, Path]] = None, mode="append"):
        """Save the dataset to a new location"""

        if location is None:
            if self._location == "":
                raise ValueError("Location to save to is not specified")
            else:
                location = self._location

        write_dataset(
            self._dataset,
            location,
            schema=self._dataset.schema,
            format=self._format,
            filesystem=self._fs,
            partitioning=self._partitioning,
            mode=mode,
        )

    def to_pandas(self) -> pd.DataFrame:
        """Returns the dataset as a Pandas DataFrame.

        Be aware that the dataset might be too large to fit in memory. Consider creating a query first."""
        return self._dataset.to_table().to_pandas()

    def __repr__(self):
        return f"Dataset(location={self._location})"

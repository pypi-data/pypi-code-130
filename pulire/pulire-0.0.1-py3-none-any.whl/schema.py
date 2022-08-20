"""
PULIRE

Schema Class

The code is licensed under the MIT license.
"""

from copy import copy
from typing import Union
from inspect import isfunction
from pandas import DataFrame, Series, concat
from .column import Column
from .validator import ValidationError, Validator


class Schema:
    """
    Pulire Schema
    """

    _index: list = []  # The index columns
    _columns: list = []  # The standard columns

    def __init__(self, index: Union[Column, list], columns: Union[Column, list]):
        self._index = index if isinstance(index, list) else [index]
        self._columns = columns if isinstance(columns, list) else [columns]

    def index(self) -> list:
        """
        Get the list of index column names
        """
        return list(map(lambda col: col.name, self._index))

    def columns(self) -> list:
        """
        Get the list of standard column names
        """
        return list(map(lambda col: col.name, self._columns))

    def props(self):
        """
        Get a list of all columns (both index and standard)
        """
        return self._index + self._columns

    def dtypes(self):
        """
        Get dict of dtypes
        """
        dtypes = {}
        for col in self._columns:
            dtypes[col.name] = col.dtype
        return dtypes

    def normalize(self, df: DataFrame, errors: str = "ignore") -> DataFrame:
        """
        Normalize a DataFrame
        """
        # Result DataFrame
        result = DataFrame(columns=self.index() + self.columns())
        result.set_index(self.index(), inplace=True)

        # Return new instance
        return (
            concat(
                [result, df[df.columns.intersection(self.columns())]],
                axis=0,
            )
            .groupby(level=df.index.names, as_index=True)
            .first()
            .astype(self.dtypes(), errors=errors)
        )

    @staticmethod
    def _run_check(validator: Validator, df: DataFrame, column: str = None) -> Series:
        validator = validator() if isfunction(validator) else validator
        if validator.skip_null:
            result = Series(data=True, index=df.index, dtype=bool)
            result.update(validator.check(df.loc[df[column].notnull()], column))
            return result.astype(bool)
        return validator.check(df, column)

    def validate(self, df: DataFrame, fill=None, normalize=True) -> DataFrame:
        """
        Validate a DataFrame
        """
        temp = self.normalize(df) if normalize else copy(df)

        for col in self._columns:
            if col.name in df.columns:
                for validator in col.validators:
                    test = self._run_check(validator, df, col.name)
                    temp.loc[~test, col.name] = fill

        return temp

    def debug(self, df: DataFrame) -> None:
        """
        Raise error when checks are failing
        """
        for col in self._columns:
            if col.name in df.columns:
                for i, validator in enumerate(col.validators):
                    test = self._run_check(validator, df, col.name)
                    if not test.all():
                        raise ValidationError(col, i, df, test)

    def is_valid(self, df: DataFrame) -> bool:
        """
        Check if a DataFrame is valid
        """
        for col in self._columns:
            if col.name in df.columns:
                for validator in col.validators:
                    test = self._run_check(validator, df, col.name)
                    if not test.all():
                        return False
        return True

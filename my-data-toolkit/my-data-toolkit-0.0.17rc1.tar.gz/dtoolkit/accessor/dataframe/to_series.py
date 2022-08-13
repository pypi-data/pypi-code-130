from __future__ import annotations

from typing import Hashable

import pandas as pd

from dtoolkit._typing import SeriesOrFrame
from dtoolkit.accessor.register import register_dataframe_method


@register_dataframe_method
def to_series(
    df: pd.DataFrame,
    /,
    name: Hashable = None,
    index_column: Hashable = None,
    value_column: Hashable = None,
) -> SeriesOrFrame:
    """
    Convert :class:`~pandas.DataFrame` to :class:`~pandas.Series`.

    Parameters
    ----------
    name : Hashable, optional
        The name of returned Series.

    index_column : Hashable, optional
        The Series's index.

    value_column : Hashable, optional
        The Series's value.

    Returns
    -------
    Series or DataFrame
        Series if ``df`` is one column DataFrame or ``value_column`` is set.

    Raises
    ------
    ValueError
        - If ``index_column`` is same to ``value_column``.
        - If ``index_column`` is not in the columns.
        - If ``value_column`` is not in the columns.

    Examples
    --------
    >>> import dtoolkit.accessor
    >>> import pandas as pd

    Convert one column DataFrame to Series.

    >>> df = pd.DataFrame(range(3))
    >>> df
       0
    0  0
    1  1
    2  2
    >>> df.to_series(name="new name")
    0    0
    1    1
    2    2
    Name: new name, dtype: int64

    Can't directly convert two or more columns DataFrame

    >>> df = pd.DataFrame({"a": range(3), "b": range(3, 6), "c": range(6, 9)})
    >>> df
       a  b  c
    0  0  3  6
    1  1  4  7
    2  2  5  8
    >>> df.to_series()
       a  b  c
    0  0  3  6
    1  1  4  7
    2  2  5  8

    Convert to Series via ``value_column``.
    A sugar syntax for ``df.get(value_column)``.

    >>> df.to_series(value_column="a")
    0  0
    1  1
    2  2
    Name: a, dtype: int64

    Convert to Series via ``index_column`` and ``value_column``.
    A sugar syntax for ``df.set_index(index_column).get(value_column)``.

    >>> df.to_series(index_column="b", value_column="c")
    b
    3    6
    4    7
    5    8
    Name: c, dtype: int64
    """

    if len(df.columns) == 1:  # one column
        column = df.columns[0]
        return df[column].rename(name or column)

    # two or more columns
    elif value_column is not None:
        if index_column is None:
            # use original index
            return df.pipe(
                _to_series,
                value_column=value_column,
                name=name,
            )

        if index_column == value_column:
            raise ValueError("'index_column' and 'value_column' should be different.")

        # use index_column as index
        return df.set_index(index_column).pipe(
            _to_series,
            value_column=value_column,
            name=name,
        )

    return df


def _to_series(df: pd.DataFrame, name: Hashable, value_column: Hashable) -> pd.Series:
    """Select one column of DataFrame and convert to Series."""

    return df[value_column].rename(name or value_column)

from typing import Collection, cast

import pandas as pd
import pyarrow as pa

from ._parse_level_coordinates import parse_level_coordinates


def arrow_to_pandas(
    table: pa.Table,  # type: ignore
) -> pd.DataFrame:
    return cast(
        pd.DataFrame,
        # Fast for small tables (less than 100k lines) but can take several seconds for larger datasets.
        table.to_pandas(),
    ).rename(
        columns={
            column_name: parse_level_coordinates(column_name)[2]  # type: ignore
            for column_name in cast(Collection[str], table.column_names)
            if parse_level_coordinates(column_name) is not None
        }
    )

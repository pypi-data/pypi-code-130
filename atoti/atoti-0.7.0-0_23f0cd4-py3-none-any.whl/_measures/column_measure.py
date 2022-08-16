from dataclasses import dataclass
from typing import Optional

from atoti_core import keyword_only_dataclass

from .._java_api import JavaApi
from ..measure_description import MeasureDescription


@keyword_only_dataclass
@dataclass(eq=False)
class ColumnMeasure(MeasureDescription):
    """Measure based on the column of a table."""

    _column_name: str
    _plugin_key: str
    _table_name: str

    def _do_distil(
        self, *, java_api: JavaApi, cube_name: str, measure_name: Optional[str] = None
    ) -> str:
        return java_api.aggregated_measure(
            cube_name=cube_name,
            measure_name=measure_name,
            table_name=self._table_name,
            column_name=self._column_name,
            agg_function=self._plugin_key,
        )

from __future__ import annotations

from datetime import datetime
from typing import Any, List, cast

import mitzu.adapters.generic_adapter as GA
import mitzu.adapters.sqlalchemy.athena.sqlalchemy.datatype as DA_T
import mitzu.model as M
import pandas as pd
from mitzu.adapters.helper import pdf_string_array_to_array
from mitzu.adapters.sqlalchemy.athena import sqlalchemy  # noqa: F401
from mitzu.adapters.sqlalchemy_adapter import SQLAlchemyAdapter

import sqlalchemy as SA
from sqlalchemy.sql.expression import CTE


class AthenaAdapter(SQLAlchemyAdapter):
    def __init__(self, project: M.Project):
        super().__init__(project)

    def execute_query(self, query: Any) -> pd.DataFrame:
        if type(query) != str:
            query = str(query.compile(compile_kwargs={"literal_binds": True}))
        return super().execute_query(query=query)

    def _get_column_values_df(
        self,
        event_data_table: M.EventDataTable,
        fields: List[M.Field],
        event_specific: bool,
    ) -> pd.DataFrame:
        df = super()._get_column_values_df(
            event_data_table=event_data_table,
            fields=fields,
            event_specific=event_specific,
        )
        return pdf_string_array_to_array(df)

    def _correct_timestamp(self, dt: datetime) -> Any:
        timeformat = dt.strftime("%Y-%m-%d %H:%M:%S")
        return SA.text(f"timestamp '{timeformat}'")

    def _get_timewindow_where_clause(self, cte: CTE, metric: M.Metric) -> Any:
        start_date = metric._start_dt.replace(microsecond=0)
        end_date = metric._end_dt.replace(microsecond=0)

        evt_time_col = cte.columns.get(GA.CTE_DATETIME_COL)
        return (evt_time_col >= self._correct_timestamp(start_date)) & (
            evt_time_col <= self._correct_timestamp(end_date)
        )

    def map_type(self, sa_type: Any) -> M.DataType:
        if isinstance(sa_type, DA_T.MAP):
            return M.DataType.MAP
        if isinstance(sa_type, DA_T.STRUCT):
            return M.DataType.STRUCT
        return super().map_type(sa_type)

    def _parse_map_type(
        self, sa_type: Any, name: str, event_data_table: M.EventDataTable
    ) -> M.Field:
        print(f"Discovering map: {name}")
        map: DA_T.MAP = cast(DA_T.MAP, sa_type)
        if map.value_type in (DA_T.STRUCT, DA_T.MAP):
            raise Exception(
                f"Compounded map types are not supported: map<{map.key_type}, {map.value_type}>"
            )
        cte = self._get_dataset_discovery_cte(event_data_table)
        F = SA.func
        map_keys_func = F.array_distinct(
            F.flatten(F.collect_set(F.map_keys(cte.columns[name])))
        )

        max_cardinality = self.project.max_map_key_cardinality
        q = SA.select(
            columns=[
                SA.case(
                    [(F.size(map_keys_func) < max_cardinality, map_keys_func)],
                    else_=None,
                ).label("sub_fields")
            ]
        )
        df = self.execute_query(q)
        if df.shape[0] == 0:
            return M.Field(_name=name, _type=M.DataType.MAP)
        keys = df.iat[0, 0].tolist()
        sf_type = self.map_type(map.value_type)
        sub_fields: List[M.Field] = [M.Field(key, sf_type) for key in keys]
        return M.Field(_name=name, _type=M.DataType.MAP, _sub_fields=tuple(sub_fields))

    def _parse_complex_type(
        self, sa_type: Any, name: str, event_data_table: M.EventDataTable, path: str
    ) -> M.Field:
        if isinstance(sa_type, DA_T.STRUCT):
            struct: DA_T.STRUCT = cast(DA_T.STRUCT, sa_type)
            sub_fields: List[M.Field] = []
            for n, st in struct.attr_types:
                next_path = f"{path}.{n}"
                if next_path in event_data_table.ignored_fields:
                    continue
                sf = self._parse_complex_type(
                    sa_type=st,
                    name=n,
                    event_data_table=event_data_table,
                    path=next_path,
                )
                if sf._type == M.DataType and (
                    sf._sub_fields is None or len(sf._sub_fields) == 0
                ):
                    continue
                sub_fields.append(sf)
            return M.Field(
                _name=name, _type=M.DataType.STRUCT, _sub_fields=tuple(sub_fields)
            )
        else:
            return M.Field(_name=name, _type=self.map_type(sa_type))

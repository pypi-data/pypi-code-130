from pydantic import BaseModel, Field

from .location import Location


class TableCellLocation(BaseModel):
    table_start_location: Location = Field(alias="tableStartLocation")
    row_index: int = Field(alias="rowIndex")
    column_index: int = Field(alias="columnIndex")

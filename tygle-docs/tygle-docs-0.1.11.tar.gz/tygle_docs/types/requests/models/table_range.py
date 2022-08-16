from pydantic import BaseModel, Field

from .table_cell_location import TableCellLocation


class TableRange(BaseModel):
    table_cell_location: TableCellLocation = Field(alias="tableCellLocation")
    row_span: int = Field(alias="rowSpan")
    column_span: int = Field(alias="columnSpan")

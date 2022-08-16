from typing import ClassVar, Optional

from pydantic import Field
from tygle_docs.types.resources.structural_element import TableCellStyleWrite

from .models import Location, TableRange
from .update_request import UpdateRequestBody


class UpdateTableCellStyle(UpdateRequestBody):
    key: ClassVar = "updateTableCellStyle"

    table_cell_style: TableCellStyleWrite = Field(alias="tableCellStyle")
    fields: str = Field()
    table_range: Optional[TableRange] = Field(None, alias="tableRange")
    table_start_location: Optional[Location] = Field(None, alias="tableStartLocation")

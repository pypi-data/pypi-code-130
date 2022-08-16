from typing import Dict, List

from pydantic import BaseModel, Field

from .table_cell import TableCell


class TableRow(BaseModel):
    start_index: int = Field(alias="startIndex")
    end_index: int = Field(alias="endIndex")
    table_cells: List[TableCell] = Field(alias="tableCells")
    suggested_insertion_ids: List[str] = Field(
        default_factory=list, alias="suggestedInsertionIds"
    )
    suggested_deletion_ids: List[str] = Field(
        default_factory=list, alias="suggestedDeletionIds"
    )
    table_row_style: Dict[str, Dict] = Field(alias="tableRowStyle")  # TODO: Type
    suggested_table_row_style_changes: Dict[str, Dict] = Field(  # TODO: Type
        default_factory=list, alias="suggestedTableRowStyleChanges"
    )

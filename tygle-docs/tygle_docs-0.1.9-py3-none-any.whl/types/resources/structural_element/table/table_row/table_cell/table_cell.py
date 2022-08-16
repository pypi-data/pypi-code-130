from typing import Dict, List

from pydantic import BaseModel, Field

from .table_cell_style import TableCellStyleRead


class TableCell(BaseModel):
    """
    https://developers.google.com/docs/api/reference/rest/v1/documents#TableCell
    """

    start_index: int = Field(alias="startIndex")
    end_index: int = Field(alias="endIndex")
    content: List[Dict] = Field()  # TODO: Type StructuralElementList
    table_cell_style: TableCellStyleRead = Field(alias="tableCellStyle")
    suggested_insertion_ids: List[str] = Field(
        default_factory=list, alias="suggestedInsertionIds"
    )
    suggested_deletion_ids: List[str] = Field(
        default_factory=list, alias="suggestedDeletionIds"
    )
    suggested_table_cell_style_changes: Dict[str, Dict] = Field(  # TODO: Type
        default_factory=list, alias="suggestedTableCellStyleChanges"
    )

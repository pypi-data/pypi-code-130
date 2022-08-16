from typing import Dict, List

from pydantic import BaseModel, Field

from .table_row import TableRow


class Table(BaseModel):
    rows: int = Field()
    columns: int = Field()
    table_rows: List[TableRow] = Field(default_factory=list, alias="tableRows")
    suggested_insertion_ids: List[str] = Field(
        default_factory=list, alias="suggestedInsertionIds"
    )
    suggested_deletion_ids: List[str] = Field(
        default_factory=list, alias="suggestedDeletionIds"
    )
    table_style: Dict[str, List] = Field(alias="tableStyle")  # TODO: Type

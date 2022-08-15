from typing import List

from pydantic import BaseModel

from vo.lark.LarkBitableRecordItem import LarkBitableRecordItem


class LarkBitableFetchRecordsResponse(BaseModel):
    items: List[LarkBitableRecordItem]
    page_token: str
    has_more: bool
    total: int


class LarkBitableGetRecordResponse(BaseModel):
    record: LarkBitableRecordItem


class LarkBitableGetRecordsResponse(BaseModel):
    records: List[LarkBitableRecordItem]


class LarkBitableDeleteRecordResponse(BaseModel):
    deleted: bool
    record_id: str

class LarkBitableDeleteRecordsResponse(BaseModel):
    records: List[LarkBitableDeleteRecordResponse]

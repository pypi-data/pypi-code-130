from typing import List, Optional

from pydantic import BaseModel

from vo.lark.LarkBitableRecordItem import LarkBitableRecordItem


class LarkBitableFetchRecordsResponse(BaseModel):
    items: Optional[List[LarkBitableRecordItem]]
    page_token: Optional[str]
    has_more: Optional[bool]
    total: Optional[int]


class LarkBitableGetRecordResponse(BaseModel):
    record: Optional[LarkBitableRecordItem]


class LarkBitableGetRecordsResponse(BaseModel):
    records: Optional[List[LarkBitableRecordItem]]


class LarkBitableDeleteRecordResponse(BaseModel):
    deleted: Optional[bool]
    record_id: Optional[str]


class LarkBitableDeleteRecordsResponse(BaseModel):
    records: Optional[List[LarkBitableDeleteRecordResponse]]

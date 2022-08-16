from typing import Optional

from pydantic import BaseModel


class LarkBitableRecordItem(BaseModel):
    id: Optional[str]
    record_id: str
    fields: dict

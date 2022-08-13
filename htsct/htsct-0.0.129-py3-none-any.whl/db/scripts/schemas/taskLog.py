import datetime
from pydantic import BaseModel


class TaskLog(BaseModel):
    id: str
    log: str

    class Config:
        orm_mode = True


class TaskLogResponse(BaseModel):
    datetime: datetime.datetime
    id: str
    log: str

    class Config:
        orm_mode = True


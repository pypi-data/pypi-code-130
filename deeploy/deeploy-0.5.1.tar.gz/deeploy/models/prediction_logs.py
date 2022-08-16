from pydantic import BaseModel
from typing import List
from deeploy.models import RequestLog, PredictionLog


class RequestLogs(BaseModel):
    data: List[RequestLog]
    count: int


class PredictionLogs(BaseModel):
    data: List[PredictionLog]
    count: int

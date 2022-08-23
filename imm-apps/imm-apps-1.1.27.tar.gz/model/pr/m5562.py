from model.common.commonmodel import CommonModel, BuilderModel
from datetime import date
from pydantic import BaseModel, root_validator
from typing import List
from model.common.mixins import DatePeriod
from model.common.utils import checkRow


class Travel(DatePeriod):
    length: int
    destination: str
    purpose: str

    @root_validator
    def checkCompletion(cls, values):
        all_fields = ["start_date", "end_date", "length", "destination", "purpose"]
        required_fields = ["start_date", "end_date", "length", "destination", "purpose"]
        checkRow(values, all_fields, required_fields)
        return values


class Personal(BaseModel):
    last_name: str
    first_name: str


class M5562Model(BaseModel):
    travel: List[Travel]
    personal: Personal

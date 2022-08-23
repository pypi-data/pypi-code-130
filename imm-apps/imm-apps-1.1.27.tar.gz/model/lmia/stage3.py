from pydantic import BaseModel, EmailStr
from model.common.commonmodel import CommonModel
import os
from typing import List
from pydantic import BaseModel
from model.common.advertisement import (
    Advertisement,
    InterviewRecord,
    RecruitmentSummary,
)


class LmiaApplication(BaseModel):

    advertisement: List[Advertisement]
    interviewrecord: List[InterviewRecord]
    recruitmentsummary: RecruitmentSummary

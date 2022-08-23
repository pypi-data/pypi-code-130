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
from model.lmia.stage3 import LmiaApplication


class LmiaApplicationE(CommonModel):

    advertisement: List[Advertisement]
    interviewrecord: List[InterviewRecord]
    recruitmentsummary: RecruitmentSummary

    # initialize the model with a list of excels, which includes all nececcery information the model required. if outpuot_excel_file is not None, it will make an excel file.
    def __init__(self, excels=None, output_excel_file=None):
        mother_excels = ["excel/recruitment.xlsx"]
        super().__init__(excels, output_excel_file, mother_excels, globals())

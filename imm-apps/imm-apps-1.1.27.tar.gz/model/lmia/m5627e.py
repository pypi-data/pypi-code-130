from model.common.commonmodel import CommonModel
from model.lmia.m5627 import M5627Model, Emp5627, Person
from model.lmia.common import *
from model.common.commonmodel import CommonModel
from webform.lmiaportal.webformmodel import WebformModel
from model.common.contact import Contacts
from model.common.finance import Finance
from model.common.advertisement import (
    InterviewRecord,
    InterviewRecords,
    RecruitmentSummary,
)
import os


class M5627ModelE(CommonModel, M5627Model):
    def __init__(self, excels=None, output_excel_file=None):
        mother_excels = [
            "excel/recruitment.xlsx",
            "excel/pa.xlsx",
            "excel/er.xlsx",
            "excel/rep.xlsx",
            "excel/lmia.xlsx",
        ]
        super().__init__(excels, output_excel_file, mother_excels, globals())

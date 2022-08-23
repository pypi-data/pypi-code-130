from model.common.commonmodel import CommonModel
from model.lmia.m5626 import M5626Model, Person, Emp5626

from model.lmia.common import *
from model.common.commonmodel import CommonModel, BuilderModel
from webform.lmiaportal.webformmodel import WebformModel
from model.common.finance import Finance
from model.common.contact import Contacts
from model.common.advertisement import (
    InterviewRecord,
    InterviewRecords,
    RecruitmentSummary,
)
import os


class M5626ModelE(CommonModel, M5626Model):
    def __init__(self, excels=None, output_excel_file=None):
        mother_excels = [
            "excel/recruitment.xlsx",
            "excel/pa.xlsx",
            "excel/er.xlsx",
            "excel/rep.xlsx",
            "excel/lmia.xlsx",
        ]
        super().__init__(excels, output_excel_file, mother_excels, globals())

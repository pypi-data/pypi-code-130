from model.common.advertisement import Advertisements, InterviewRecords
from model.common.finance import Finance
from model.common.advertisement import Advertisement, Advertisements
from model.common.advertisement import (
    InterviewRecord,
    InterviewRecords,
    RecruitmentSummary,
)
from model.common.contact import Contacts
from model.lmia.common import *
from model.common.commonmodel import CommonModel, BuilderModel
from webform.lmiaportal.webformmodel import WebformModel
import os
from model.lmia.m5593 import M5593Model


class M5593ModelE(CommonModel, M5593Model):
    # initialize the model with a list of excels, which includes all nececcery information the model required. if outpuot_excel_file is not None, it will make an excel file.
    def __init__(self, excels=None, output_excel_file=None):
        mother_excels = [
            "excel/recruitment.xlsx",
            "excel/pa.xlsx",
            "excel/er.xlsx",
            "excel/rep.xlsx",
            "excel/lmia.xlsx",
        ]
        # call parent class for validating
        super().__init__(excels, output_excel_file, mother_excels, globals())

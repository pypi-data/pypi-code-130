from typing import List, Optional
from model.common.address import Address
from model.common.phone import Phone
from model.common.trperson import (
    COR,
    PersonId,
    Personal,
    Marriage,
    Education,
    Employment,
    # Family,
)
from model.common.tr import TrCaseIn, TrBackground, WpInCanada
from model.common.commonmodel import CommonModel, BuilderModel
from pdfform.tr.fb5710 import FormBuilder5710
from termcolor import colored
import json
from model.tr.m5710 import M5710Model


class M5710ModelE(CommonModel, M5710Model):
    def __init__(self, excels=None, output_excel_file=None):
        mother_excels = ["excel/tr.xlsx", "excel/pa.xlsx"]
        super().__init__(excels, output_excel_file, mother_excels, globals())

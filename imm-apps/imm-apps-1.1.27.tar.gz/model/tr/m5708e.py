from pydantic import BaseModel
from termcolor import colored
from functools import reduce
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
)
from model.common.tr import TrCaseIn, TrBackground, VrInCanada
from model.common.commonmodel import CommonModel, BuilderModel
from pdfform.tr.fb5708 import FormBuilder5708
from datetime import date
import json
from model.tr.m5708 import M5708Model


class M5708ModelE(CommonModel, M5708Model):
    def __init__(self, excels=None, output_excel_file=None):
        mother_excels = ["excel/tr.xlsx", "excel/pa.xlsx"]
        super().__init__(excels, output_excel_file, mother_excels, globals())

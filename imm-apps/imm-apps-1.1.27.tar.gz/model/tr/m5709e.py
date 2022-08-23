from termcolor import colored
from functools import reduce
from typing import List
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
import json

from model.common.tr import TrCaseIn, TrBackground, SpInCanada
from model.common.commonmodel import CommonModel, BuilderModel
from pdfform.tr.fb5709 import FormBuilder5709
from model.tr.m5709 import M5709Model


class M5709ModelE(CommonModel, M5709Model):
    def __init__(self, excels=None, output_excel_file=None):
        mother_excels = ["excel/tr.xlsx", "excel/pa.xlsx"]
        super().__init__(excels, output_excel_file, mother_excels, globals())

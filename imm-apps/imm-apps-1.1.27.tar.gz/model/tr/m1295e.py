from termcolor import colored
from functools import reduce
from typing import List, Optional
from model.common.address import Address
from ..common.educationbase import EducationHistory
from model.common.phone import Phone
from model.common.trperson import (
    COR,
    PersonId,
    Personal,
    Marriage,
    Education,
    Employment,
    Travel,
    Family,
)
from model.common.person import PersonalAssess
from model.common.tr import TrCase, Wp, TrBackground
from model.common.commonmodel import CommonModel, BuilderModel
from pdfform.tr.fb1295 import FormBuilder1295
from model.lmia.common import Rcic
import json
from model.tr.m1295 import M1295Model


class M1295ModelE(CommonModel, M1295Model):
    def __init__(self, excels=None, output_excel_file=None):
        mother_excels = ["excel/tr.xlsx", "excel/pa.xlsx", "excel/rep.xlsx"]
        super().__init__(excels, output_excel_file, mother_excels, globals())
